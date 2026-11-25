"""Minimal client for the OpenAI-compatible API (Ollama, LM Studio, vLLM)."""

from __future__ import annotations

import json
import ssl
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from ..core.config import LlmConfig, LlmDestination
from ..i18n import t
from .destinations import validate_model, validate_url

KEYRING_SERVICE = "Heimdall"


class LlmError(Exception):
    """The destination did not answer, or answered something unusable."""


@dataclass(frozen=True)
class ChatReply:
    text: str
    completion_tokens: int
    seconds: float
    finish_reason: str = ""

    @property
    def tokens_per_second(self) -> float:
        return self.completion_tokens / self.seconds if self.seconds > 0 else 0.0


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """A redirect could carry the code to another host: none is followed."""

    def redirect_request(self, *args: Any, **kwargs: Any) -> None:
        return None


def read_token(destination: LlmDestination) -> str | None:
    """The destination's token, stored in the system keychain; never in the config."""
    try:
        import keyring

        return keyring.get_password(KEYRING_SERVICE, destination.name)
    except Exception:
        return None


class LlmClient:
    def __init__(self, destination: LlmDestination, config: LlmConfig) -> None:
        validate_url(destination.url, config.allowed_hosts)
        self.destination = destination
        self._base = destination.url.rstrip("/")
        self._timeout = config.timeout_per_target_s
        # Set once the runtime rejects `reasoning_effort`; it is not tried again.
        self._no_reasoning_effort = False
        self._temperature = min(max(config.temperature, 0.0), 0.2)
        self._headers = {"Content-Type": "application/json"}
        if destination.requires_token:
            token = read_token(destination)
            if not token:
                raise LlmError(t("llm.client.token_missing", name=destination.name))
            self._headers["Authorization"] = f"Bearer {token}"
        context = ssl.create_default_context(cafile=config.internal_ca or None)
        # No proxies from the environment: they would divert traffic away from the
        # validated destination.
        self._opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}),
            _NoRedirect(),
            urllib.request.HTTPSHandler(context=context),
        )

    def _request(self, path: str, payload: dict[str, Any] | None, timeout: int) -> dict[str, Any]:
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(  # noqa: S310 - the scheme was already validated
            self._base + path, data=data, headers=self._headers
        )
        try:
            with self._opener.open(request, timeout=timeout) as response:
                body: dict[str, Any] = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            with exc:
                detail = exc.read().decode("utf-8", errors="replace")[:200]
            raise LlmError(t("llm.client.http_error", code=exc.code, detail=detail)) from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise LlmError(
                t("llm.client.no_connection", name=self.destination.name, error=exc)
            ) from exc
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise LlmError(t("llm.client.unreadable")) from exc
        return body

    def models(self) -> list[str]:
        body = self._request("/models", None, timeout=10)
        return sorted(str(item.get("id", "")) for item in body.get("data", []))

    def chat(
        self,
        model: str,
        system: str,
        user: str,
        schema: dict[str, Any] | None = None,
        max_tokens: int = 700,
    ) -> ChatReply:
        validate_model(model)
        reasoning_on = self.destination.reasoning == "on"
        payload: dict[str, Any] = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": self._temperature,
            "seed": 7,
            "max_tokens": max(max_tokens, 4096) if reasoning_on else max_tokens,
            "stream": False,
        }
        if not reasoning_on and not self._no_reasoning_effort:
            payload["reasoning_effort"] = "none"
        if schema is not None:
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {"name": "response", "schema": schema},
            }
        started = time.monotonic()
        body = self._send(payload)
        try:
            choice = body["choices"][0]
            text = str(choice["message"]["content"] or "")
            finish = str(choice.get("finish_reason") or "")
        except (KeyError, IndexError, TypeError, AttributeError) as exc:
            raise LlmError(t("llm.client.empty")) from exc
        tokens = int((body.get("usage") or {}).get("completion_tokens", 0) or 0)
        return ChatReply(text, tokens, time.monotonic() - started, finish)

    def _send(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Posts the chat request, dropping the optional fields a runtime rejects."""
        while True:
            try:
                return self._request("/chat/completions", payload, self._timeout)
            except LlmError as exc:
                rejected = "HTTP 400" in str(exc) or "HTTP 422" in str(exc)
                if not rejected:
                    raise
                # Some runtimes reject these fields; the tolerant parser covers for it.
                if "reasoning_effort" in payload:
                    payload.pop("reasoning_effort")
                    self._no_reasoning_effort = True
                elif "response_format" in payload:
                    payload.pop("response_format")
                else:
                    raise
