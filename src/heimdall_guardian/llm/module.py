"""AI module: finding triage (T1), endpoint review (T2), summary (T3) and sink review (T4).

It works on bounded targets handed to it by the core; it never walks the
repository. Its results are suggestions: they change no severities and
suppress no findings, and a model failure does not stop the run.
"""

from __future__ import annotations

import hashlib
import json
import math
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from pydantic import BaseModel

from ..core.config import LlmConfig, LlmDestination
from ..core.finding import Category, Confidence, Finding, Origin, Severity
from ..core.fingerprint import fingerprint
from ..core.paths import data_dir
from ..core.profiles import Module
from ..i18n import Message, get_language, msg, t, texts_of
from . import prompts
from .client import ChatReply, LlmClient, LlmError
from .context import (
    CONTEXT_RADIUS,
    MAX_CONTEXT_LINES,
    EndpointContext,
    enclosing_function,
    endpoint_context,
    line_budget,
    numbered_code,
    python_block,
    sink_context,
)
from .destinations import DestinationError, validate_model
from .schemas import (
    EndpointReview,
    Level,
    Reach,
    Risk,
    SinkReview,
    Summary,
    Triage,
    Verdict,
    parse,
)

__all__ = ["CONTEXT_RADIUS", "MAX_CONTEXT_LINES"]

SINK_SHARE = 0.6  # of the run budget, at most, goes to the sink review (T4)
MAX_CONSECUTIVE_FAILURES = 3


def ai_label() -> str:
    """ "AI suggestion — requires human validation", in the current language."""
    return t("llm.ai_label")


_TRIAGE_SEVERITIES = (Severity.CRITICAL, Severity.HIGH)
# Only a "high" risk produces a finding, and it never goes above MEDIA: an AI
# suggestion must not move the traffic light or the verdict on its own (P5).
_RISK_SEVERITY = {Risk.HIGH: Severity.MEDIUM}
_SINK_RULES = {
    "sql": "AI-SQL-001",
    "exec": "AI-EXEC-001",
    "deser": "AI-DESER-001",
    "path": "AI-PATH-001",
    "ssrf": "AI-SSRF-001",
    "xxe": "AI-XXE-001",
    "redirect": "AI-REDIR-001",
}
_SINK_ORDER = tuple(_SINK_RULES)
# Findings from the endpoint inventory are reviewed by T2 with more context
# (route, methods, authentication); assessing them in T1 too duplicated queries.
_REVIEWED_BY_T2 = frozenset({"AUTHZ-001", "AUTHZ-002"})


class ChatClient(Protocol):
    destination: LlmDestination

    def models(self) -> list[str]: ...

    def chat(
        self, model: str, system: str, user: str, schema: dict[str, Any] | None = None,
        max_tokens: int = 700,
    ) -> ChatReply: ...  # fmt: skip


def _code(message: Any) -> str:
    return str(message.get("code", "")) if isinstance(message, dict) else ""


@dataclass
class AiOutcome:
    status: str = "skipped"  # ran | skipped | error
    detail: Message | str = ""
    destination: str = ""
    models: list[str] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    limitations: list[Message] = field(default_factory=list)
    summary: str = ""
    summary_language: str = ""  # the language it was written in (the run's)
    asked: int = 0
    valid: int = 0
    truncated: int = 0
    cached: int = 0
    sinks_reviewed: int = 0
    sinks_found: int = 0
    seconds: float = 0.0


def code_context(root: Path, file: str, line: int, secrets: set[str]) -> tuple[str, int]:
    """Code around `line`, numbered and with secrets masked.

    For Python the complete function or class containing the line is sent, not
    an arbitrary cut; for other languages, a window around it.
    """
    start, end = max(1, line - CONTEXT_RADIUS), line + CONTEXT_RADIUS
    if file.endswith(".py"):
        block = python_block(root, file, line, classes=True)
        if block is not None:
            _, start, end = block
    return numbered_code(root, file, start, end, secrets), start


class _Cache:
    """Already-validated replies, keyed by hash of (task, model, prompt)."""

    def __init__(self, directory: Path | None) -> None:
        self.directory = directory

    def _path(self, key: str) -> Path | None:
        return self.directory / f"{key}.json" if self.directory else None

    def get(self, key: str) -> dict[str, Any] | None:
        path = self._path(key)
        if path is None or not path.is_file():
            return None
        try:
            data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        return data

    def put(self, key: str, value: dict[str, Any]) -> None:
        path = self._path(key)
        if path is None:
            return
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


_RISK_ORDER = ("none", "low", "medium", "high")


def _by_handler(findings: list[Finding]) -> dict[tuple[str, int], list[Finding]]:
    """Inventory findings by file and line; several routes share a handler."""
    places: dict[tuple[str, int], list[Finding]] = {}
    for finding in findings:
        if finding.rule_id in _REVIEWED_BY_T2:
            places.setdefault((finding.file, finding.line_start), []).append(finding)
    return places


def _riskier(review: EndpointReview, previous: dict[str, Any]) -> bool:
    """If the handler already has a review from another route, the riskier one is kept."""

    def level(*risks: str) -> int:
        return max(_RISK_ORDER.index(r) if r in _RISK_ORDER else 0 for r in risks)

    now = level(review.idor_risk.value, review.flow_risk.value)
    before = level(str(previous.get("idor_risk")), str(previous.get("flow_risk")))
    return now > before


class AiRunner:
    def __init__(
        self,
        config: LlmConfig,
        *,
        clients: list[ChatClient] | None = None,
        cache_dir: Path | None = None,
        use_cache: bool = True,
    ) -> None:
        self.config = config
        self._clients = clients
        self._cache = _Cache((cache_dir or data_dir() / "cache" / "llm") if use_cache else None)
        self._client: ChatClient | None = None
        self._failures = 0
        self._candidate_sinks: list[Finding] = []
        self._files: list[str] = []
        self.outcome = AiOutcome()
        # `on_progress(done, total)` reports before each target; `cancelled()`
        # is consulted between targets so a long review can be stopped.
        self.on_progress: Callable[[int, int], None] | None = None
        self.cancelled: Callable[[], bool] | None = None
        self._done = 0
        self._total = 0
        self._cancel_noted = False

    # ---------------------------------------------------------- connection

    def _connect(self) -> bool:
        """Picks the first destination that answers: the active one, then the fallback."""
        out = self.outcome
        if not self.config.enabled:
            out.detail = msg("llm.detail.disabled")
            return False
        problems: list[Message] = []
        for destination in self._candidates(problems):
            try:
                destination.models()
            except LlmError as exc:
                problems.append(
                    msg("llm.problem", name=destination.destination.name, error=str(exc))
                )
                continue
            self._client = destination
            out.destination = destination.destination.name
            if problems:
                out.limitations.append(
                    msg("llm.limit.fallback", destination=out.destination, problems=problems)
                )
            return True
        out.status = "error" if problems else "skipped"
        out.detail = (
            msg("llm.detail.problems", problems=problems)
            if problems
            else msg("llm.detail.no_destinations")
        )
        return False

    def _candidates(self, problems: list[Message]) -> list[ChatClient]:
        if self._clients is not None:
            return self._clients
        clients: list[ChatClient] = []
        for destination in self.config.candidates():
            try:
                clients.append(LlmClient(destination, self.config))
            except (DestinationError, LlmError, OSError) as exc:
                problems.append(msg("llm.problem", name=destination.name, error=str(exc)))
        return clients

    def _model(self, task: str) -> str | None:
        assert self._client is not None  # noqa: S101 - only called after _connect
        model = self._client.destination.model(task)
        if model is None and task == "sinks":
            model = self._client.destination.model("triage")
        if model is None:
            return None
        try:
            validate_model(model)
        except DestinationError as exc:
            self.outcome.limitations.append(msg("llm.limit.generic", error=str(exc)))
            return None
        if model not in self.outcome.models:
            self.outcome.models.append(model)
        return model

    # --------------------------------------------------------------- calls

    def _ask(self, task: str, model: str, system: str, user: str, schema: type[BaseModel]) -> Any:
        """A query with caching; returns the validated model or `None`."""
        out = self.outcome
        raw_key = "\0".join(
            (str(prompts.PROMPT_VERSION), get_language(), task, model, system, user)
        )
        key = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
        cached = self._cache.get(key)
        if cached is not None:
            out.cached += 1
            return schema.model_validate(cached)

        assert self._client is not None  # noqa: S101
        out.asked += 1
        try:
            reply = self._client.chat(model, system, user, schema.model_json_schema())
        except LlmError as exc:
            self._failures += 1
            if self._failures >= MAX_CONSECUTIVE_FAILURES:
                raise
            out.limitations.append(msg("llm.limit.query_failed", error=str(exc)))
            return None
        self._failures = 0
        if getattr(reply, "finish_reason", "") == "length":
            out.truncated += 1
        parsed = parse(reply.text, schema)
        if parsed is None:
            return None  # does not meet the schema: treated as "uncertain"
        out.valid += 1
        self._cache.put(key, parsed.model_dump(mode="json"))
        return parsed

    def run(
        self,
        findings: list[Finding],
        endpoints: list[dict[str, Any]],
        root: Path,
        secrets: set[str],
        candidates: list[Finding] | None = None,
        files: list[str] | None = None,
    ) -> AiOutcome:
        """T4 over the candidate sinks, T2 over the endpoints and T1 over the serious
        findings, in that order and within one shared budget."""
        self._candidate_sinks = [c for c in (candidates or []) if c.candidate_kind in _SINK_RULES]
        self._files = files or []
        out = self.outcome
        started = time.monotonic()
        if not self._connect():
            return out
        out.status = "ran"
        budget = self.config.max_targets_per_run
        assert self._client is not None  # noqa: S101 - guaranteed by _connect
        destination = self._client.destination
        has_sink_model = (destination.model("sinks") or destination.model("triage")) is not None
        sinks = self._candidate_sinks if has_sink_model else []
        reviews_endpoints = bool(endpoints) and destination.model("endpoints") is not None
        targets = self._triage_targets(findings, skip_authz=reviews_endpoints)
        in_sinks = min(len(sinks), math.ceil(SINK_SHARE * budget))
        in_endpoints = min(budget - in_sinks, len(endpoints)) if reviews_endpoints else 0
        in_triage = (
            min(budget - in_sinks - in_endpoints, len(targets))
            if destination.model("triage")
            else 0
        )
        self._total = in_sinks + in_endpoints + in_triage
        try:
            budget = self._sinks(sinks, endpoints, root, secrets, budget)
            budget = self._endpoints(endpoints, findings, root, secrets, budget)
            self._triage(targets, root, secrets, budget)
        except LlmError as exc:
            out.status = "error"
            out.detail = msg("llm.detail.stopped", error=str(exc))
        out.seconds = time.monotonic() - started
        self._note_low_valid()
        return out

    def _note_low_valid(self) -> None:
        """One limitation when most replies were unusable (typically a reasoning model)."""
        out = self.outcome
        if out.asked >= 3 and out.valid / out.asked < 0.5:
            out.limitations = [m for m in out.limitations if _code(m) != "llm.limit.low_valid"]
            out.limitations.append(
                msg(
                    "llm.limit.low_valid",
                    asked=out.asked,
                    valid=out.valid,
                    invalid=out.asked - out.valid,
                    truncated=out.truncated,
                )
            )

    def _step(self) -> bool:
        """Advances the counter; `False` if cancellation was requested."""
        if self.cancelled is not None and self.cancelled():
            if not self._cancel_noted:
                self._cancel_noted = True
                self.outcome.detail = msg("llm.detail.cancelled")
                self.outcome.limitations.append(
                    msg("llm.limit.cancelled", done=self._done, total=self._total)
                )
            return False
        self._done += 1
        if self.on_progress is not None:
            self.on_progress(self._done, self._total)
        return True

    @staticmethod
    def _triage_targets(findings: list[Finding], *, skip_authz: bool) -> list[Finding]:
        return [
            f
            for f in findings
            if f.severity in _TRIAGE_SEVERITIES
            and f.origin is Origin.DETERMINISTIC
            and f.category is not Category.DEPENDENCIES
            and f.line_start >= 1
            # Confirming a rule that is already sure of itself adds little for its cost.
            and f.confidence is not Confidence.HIGH
            and not (skip_authz and f.rule_id in _REVIEWED_BY_T2)
        ]

    def _triage(self, targets: list[Finding], root: Path, secrets: set[str], budget: int) -> int:
        model = self._model("triage")
        if model is None:
            if targets:
                self.outcome.limitations.append(msg("llm.limit.no_triage_model"))
            return budget
        second = self._client.destination.model("consensus") if self._client else None
        if second == model:
            second = None
        skipped = max(0, len(targets) - budget)
        for finding in targets[:budget]:
            if not self._step():
                break
            code, first = code_context(root, finding.file, finding.line_start, secrets)
            user = prompts.triage(finding.to_dict(), code, first)
            verdict = self._ask("T1", model, prompts.system_triage(), user, Triage)
            assessment: dict[str, Any] = {
                "task": "T1",
                "model": model,
                "language": get_language(),
                **(
                    verdict.model_dump(mode="json")
                    if verdict
                    else {
                        "verdict": Verdict.UNCERTAIN.value,
                        "explanation": msg("llm.invalid_reply"),
                        "suggested_fix": "",
                        "confidence": Level.LOW.value,
                    }
                ),
            }
            if second is not None and verdict is not None:
                other = self._ask("T1", second, prompts.system_triage(), user, Triage)
                agree = other is not None and other.verdict == verdict.verdict
                # Two models that agree give more confidence; if they disagree, less.
                assessment["consensus"] = {"model": second, "agrees": agree}
                assessment["confidence"] = (Level.HIGH if agree else Level.LOW).value
            finding.llm_assessment = assessment
        if skipped:
            self.outcome.limitations.append(msg("llm.limit.triage_budget", count=skipped))
        return budget - min(budget, len(targets))

    def _endpoints(
        self,
        endpoints: list[dict[str, Any]],
        findings: list[Finding],
        root: Path,
        secrets: set[str],
        budget: int,
    ) -> int:
        """Reviews endpoints within `budget`; returns what is left of it."""
        if not endpoints:
            return budget
        model = self._model("endpoints")
        if model is None:
            self.outcome.limitations.append(msg("llm.limit.no_endpoint_model"))
            return budget

        def priority(item: dict[str, Any]) -> tuple[bool, bool, str]:
            parametric = any(mark in item["path"] for mark in "{<:")
            return (not (item["writes"] and parametric), not parametric, item["path"])

        ordered = sorted(endpoints, key=priority)
        reported = _by_handler(findings)
        assert self._client is not None  # noqa: S101
        window = line_budget(self._client.destination.context_tokens)
        for item in ordered[:budget]:
            if not self._step():
                break
            ctx = endpoint_context(root, item, self._files, secrets, max_lines=window)
            review = self._ask(
                "T2", model, prompts.system_endpoint(), prompts.endpoint(item, ctx),
                EndpointReview,
            )  # fmt: skip
            if review is None:
                continue
            self._apply_review(item, review, model, reported.get((item["file"], item["line"])), ctx)
        if len(ordered) > budget:
            self.outcome.limitations.append(
                msg("llm.limit.endpoint_budget", count=len(ordered) - budget)
            )
        return budget - min(budget, len(ordered))

    # ------------------------------------------------------------ T4: sinks

    def _sink_priority(self, endpoint_files: set[str]) -> Callable[[Finding], Any]:
        def key(candidate: Finding) -> tuple[bool, int, str, int]:
            kind = candidate.candidate_kind
            order = _SINK_ORDER.index(kind) if kind in _SINK_ORDER else len(_SINK_ORDER)
            return (
                candidate.file not in endpoint_files,
                order,
                candidate.file,
                candidate.line_start,
            )

        return key

    def _sinks(
        self,
        candidates: list[Finding],
        endpoints: list[dict[str, Any]],
        root: Path,
        secrets: set[str],
        budget: int,
    ) -> int:
        """Reviews candidate sinks within their share of `budget`; returns what is left."""
        if not candidates:
            return budget
        model = self._model("sinks")
        if model is None:
            return budget
        second = self._client.destination.model("consensus") if self._client else None
        if second == model:
            second = None
        endpoint_files = {item["file"] for item in endpoints}
        ordered = sorted(candidates, key=self._sink_priority(endpoint_files))
        share = min(len(ordered), math.ceil(SINK_SHARE * budget))
        assert self._client is not None  # noqa: S101
        window = line_budget(self._client.destination.context_tokens)
        used = 0
        for candidate in ordered[:share]:
            if not self._step():
                break
            used += 1
            code, first, callers = sink_context(
                root, candidate.file, candidate.line_start, self._files, secrets, max_lines=window
            )
            system = prompts.system_sink(candidate.candidate_kind)
            user = prompts.sink(candidate.to_dict(), code, first, callers)
            review = self._ask("T4", model, system, user, SinkReview)
            self.outcome.sinks_reviewed += 1
            if review is None or review.risk is not Risk.HIGH or review.reachable is not Reach.YES:
                continue
            agrees = False
            if second is not None:
                other = self._ask("T4", second, system, user, SinkReview)
                agrees = (
                    other is not None and other.risk is Risk.HIGH and other.reachable is Reach.YES
                )
            function, _, _ = enclosing_function(root, candidate.file, candidate.line_start)
            finding = self._sink_finding(candidate, review, model, agrees, function or "")
            self.outcome.findings.append(finding)
            self.outcome.sinks_found += 1
        if len(ordered) > share:
            self.outcome.limitations.append(
                msg("llm.limit.sink_budget", count=len(ordered) - share)
            )
        return budget - used

    def _sink_finding(
        self, candidate: Finding, review: SinkReview, model: str, agrees: bool, function: str = ""
    ) -> Finding:
        kind = candidate.candidate_kind
        rule_id = _SINK_RULES[kind]
        texts = texts_of(
            title=msg(
                "llm.finding.title_sink",
                label=msg("llm.ai_label"),
                what=msg(f"llm.finding.what_{kind}"),
                file=candidate.file,
            ),
            # The model writes the explanation in the run's language: it goes out as is.
            description=msg(
                "llm.finding.description_sink", explanation=review.explanation, source=review.source
            )
            if review.source
            else review.explanation,
            recommendation=review.suggested_fix or msg("llm.finding.recommendation_sink"),
        )
        return Finding(
            # The enclosing function tells apart identical lines in one file; the line number
            # stays out so moving code does not create a "new" finding.
            fingerprint=fingerprint(
                rule_id, candidate.file, f"{function} {candidate.snippet}".strip()
            ),
            source="llm",
            origin=Origin.AI,
            rule_id=rule_id,
            category=Category.SAST,
            severity=_RISK_SEVERITY[Risk.HIGH],
            confidence=Confidence.MEDIUM if agrees else Confidence.LOW,
            file=candidate.file,
            line_start=candidate.line_start,
            line_end=candidate.line_end,
            snippet=candidate.snippet,
            texts=texts,
            owasp=candidate.owasp,
            cwe=candidate.cwe,
            module=Module.AI,
            llm_assessment={
                "task": "T4",
                "model": model,
                "language": get_language(),
                **review.model_dump(mode="json"),
                "candidate_rule": candidate.rule_id,
            },
        )

    def _apply_review(
        self,
        item: dict[str, Any],
        review: EndpointReview,
        model: str,
        existing: list[Finding] | None,
        ctx: EndpointContext,
    ) -> None:
        item["idor_risk"] = review.idor_risk.value
        item["ai_review"] = {
            "model": model,
            "language": get_language(),
            "handler_file": ctx.handler_file,
            "handler_line": ctx.handler_first,
            **review.model_dump(mode="json"),
        }
        if existing:
            # The route already has its deterministic finding (no authentication): the
            # review is attached to it instead of creating a suggestion that repeats it.
            for finding in existing:
                if finding.llm_assessment is None or _riskier(review, finding.llm_assessment):
                    finding.llm_assessment = {"task": "T2", **item["ai_review"]}
            return
        if not ctx.resolved:
            return
        for kind, risk in (("IDOR", review.idor_risk), ("FLOW", review.flow_risk)):
            if kind == "IDOR" and review.checks_object_ownership is True:
                continue  # contradictory: ownership is checked, so there is nothing to report
            if risk in _RISK_SEVERITY:
                self.outcome.findings.append(self._finding(kind, risk, item, review, model))

    def _finding(
        self, kind: str, risk: Risk, item: dict[str, Any], review: EndpointReview, model: str
    ) -> Finding:
        rule_id = f"AI-{kind}-001"
        # The fingerprint does not depend on the language: «*» means any method.
        route = f"{', '.join(item['methods'])} {item['path']}"
        shown = msg("llm.finding.any_method") if item["methods"] == ["*"] else item["methods"]
        what = msg("llm.finding.what_idor" if kind == "IDOR" else "llm.finding.what_flow")
        texts = texts_of(
            title=msg(
                "llm.finding.title",
                label=msg("llm.ai_label"),
                what=what,
                route=msg("authz.route", methods=shown, path=item["path"]),
            ),
            # The model writes the explanation in the run's language: it goes out as is.
            description=review.explanation,
            recommendation=msg("llm.finding.recommendation"),
        )
        return Finding(
            fingerprint=fingerprint(rule_id, item["file"], f"{route} {item['handler']}"),
            source="llm",
            origin=Origin.AI,
            rule_id=rule_id,
            category=Category.ACCESS_CONTROL if kind == "IDOR" else Category.FLOW,
            severity=_RISK_SEVERITY[risk],
            confidence=Confidence.LOW,
            file=item["file"],
            line_start=item["line"],
            line_end=item["line"],
            snippet="",
            texts=texts,
            owasp="A01:2025 Broken Access Control"
            if kind == "IDOR"
            else "A06:2025 Insecure Design",
            cwe="CWE-639" if kind == "IDOR" else "CWE-841",
            module=Module.AI,
            llm_assessment={
                "task": "T2",
                "model": model,
                "language": get_language(),
                **review.model_dump(mode="json"),
            },
        )

    def summarize(self, stats: dict[str, Any]) -> None:
        """T3: executive summary from aggregate figures; it never receives code."""
        out = self.outcome
        if out.status != "ran" or self._client is None:
            return
        model = self._model("summary")
        if model is None:
            return
        try:
            result = self._ask(
                "T3", model, prompts.system_summary(), prompts.summary(stats), Summary
            )
        except LlmError as exc:
            out.limitations.append(msg("llm.limit.no_summary", error=str(exc)))
            return
        if result is not None:
            out.summary = result.summary
            out.summary_language = get_language()
        self._note_low_valid()
