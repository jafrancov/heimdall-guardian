"""Validation of AI destinations: the code does not leave the local network (P3)."""

from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlsplit

from ..i18n import t

LOCAL_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})
# Ollama publishes remote models with a `:cloud` suffix: they would send the code out.
_CLOUD_MODEL = re.compile(r"(?i)[:_-]cloud$")


class DestinationError(ValueError):
    """The destination or model would violate P3; it is not used."""


def validate_url(url: str, allowed_hosts: tuple[str, ...] = ()) -> None:
    parts = urlsplit(url)
    host = (parts.hostname or "").lower()
    if parts.scheme not in ("http", "https") or not host:
        raise DestinationError(t("llm.destination.invalid_url", url=repr(url)))
    if parts.username or parts.password:
        raise DestinationError(t("llm.destination.credentials"))
    if host in LOCAL_HOSTS:
        return
    try:
        private = ipaddress.ip_address(host).is_private
    except ValueError:
        private = False
    if host not in allowed_hosts and not private:
        raise DestinationError(t("llm.destination.not_local", host=host))
    if parts.scheme != "https":
        raise DestinationError(t("llm.destination.https_required", host=host))


def validate_model(model: str) -> None:
    if _CLOUD_MODEL.search(model.strip()):
        raise DestinationError(t("llm.model.cloud", model=repr(model)))
