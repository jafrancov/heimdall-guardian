"""Run executor: plans, launches adapters and normalizes the result."""

from __future__ import annotations

import contextlib
import dataclasses
import re
import tempfile
import time
from collections import Counter
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .. import __version__
from ..adapters import default_adapters
from ..adapters.base import (
    Adapter,
    AdapterError,
    MissingDatabaseError,
    ScanContext,
    missing_database,
)
from ..adapters.opengrep import rules_version
from ..i18n import Message, get_language, label, msg, t, text_of
from .coverage import coverage_notes
from .detector import StackHit, detect
from .endpoints import Endpoint
from .files import Exclusions, TreeInfo, scan_tree, tree_hash
from .finding import BaselineStatus, Category, Finding, Origin, Severity
from .lockfiles import direct_only_manifests
from .locking import database_lock
from .masking import mask_generic, mask_known
from .profiles import IMPLEMENTED, PARTIAL, Module, resolve
from .user_rules import RuleProblem, check_user_rules, own_rule_ids, rule_ids_of
from .vendored import VendoredLibrary
from .vendored import detect as detect_vendored
from .verdict import Thresholds, evaluate

if TYPE_CHECKING:
    from ..llm.module import AiOutcome, AiRunner

# Opengrep rules that the endpoint inventory evaluates with more context
# (it crosses routes, inheritance and global configuration).
SUPERSEDED_RULES = frozenset(
    {"DJ-AUTH-001", "DJ-AUTH-002", "NET-AUTH-001", "NET-AUTH-002", "PHP-AUTH-002"}
)

SCHEMA_VERSION = 8  # 8: run keys, profiles and enum members in English
DB_ALERT_DAYS = 7  # age of the databases beyond which a warning is shown
OPEN_STATUSES = (BaselineStatus.NEW, BaselineStatus.PERSISTENT)
_SAST_CATEGORIES = (Category.SAST, Category.ACCESS_CONTROL)


@dataclass
class ToolRun:
    name: str
    status: str  # ran | skipped | error
    version: str | None = None
    db_updated_at: str | None = None
    seconds: float = 0.0
    findings: int = 0
    detail: Message | str = ""  # structured message (or free text from a tool)
    stats: dict[str, int] | None = None  # optional counters, English keys

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "name": self.name,
            "status": self.status,
            "version": self.version,
            "db_updated_at": self.db_updated_at,
            "seconds": round(self.seconds, 2),
            "findings": self.findings,
            "detail": self.detail,
        }
        if self.stats is not None:
            data["stats"] = dict(self.stats)
        return data


@dataclass
class Plan:
    """What would be analyzed; it is also the output of `--dry-run`."""

    root: Path
    profile: str
    requested: frozenset[Module]
    tree: TreeInfo
    stacks: list[StackHit]
    exclusions: Exclusions
    # The user's own rule files that passed the structural check, and what failed it.
    user_rules: tuple[Path, ...] = ()
    user_rule_problems: tuple[RuleProblem, ...] = ()
    # Libraries copied into the tree (recognized by their version header).
    vendored: tuple[VendoredLibrary, ...] = ()

    @property
    def modules(self) -> frozenset[Module]:
        return self.requested & IMPLEMENTED

    @property
    def pending_modules(self) -> list[Module]:
        return sorted(self.requested - IMPLEMENTED)

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": str(self.root),
            "profile": self.profile,
            "modules": sorted(self.modules),
            "unavailable_modules": self.pending_modules,
            "stack": [hit.to_dict() for hit in self.stacks],
            "exclusions": [*self.exclusions.dirs, *self.exclusions.file_entries],
            "files": self.tree.analyzable,
            "oversized_files": self.tree.oversized,
            "large_code_files": self.tree.large_code,
            "ignored_symlinks": self.tree.symlinks,
            "vendored": [lib.to_dict() for lib in self.vendored],
        }


def summarize(findings: list[Finding], fixed: int) -> dict[str, Any]:
    """Counts by severity and category (open ones only) and by status."""
    open_findings = [f for f in findings if f.baseline_status in OPEN_STATUSES]
    by_severity = Counter(f.severity for f in open_findings)
    by_category = Counter(f.category for f in open_findings)
    by_status = Counter(f.baseline_status for f in findings)
    by_status[BaselineStatus.FIXED] = fixed
    return {
        "by_severity": {s.value: by_severity.get(s, 0) for s in Severity},
        "by_category": {c.value: n for c, n in sorted(by_category.items())},
        "by_status": {s.value: by_status.get(s, 0) for s in BaselineStatus},
    }


@dataclass
class ScanResult:
    plan: Plan
    tree_hash: str
    started: datetime
    finished: datetime
    tools: list[ToolRun] = field(default_factory=list)
    limitations: list[Message] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    # Filled in by the baseline (`storage.Store.record`) when it is used.
    run_id: int | None = None
    previous_run_id: int | None = None
    fixed: list[dict[str, Any]] = field(default_factory=list)  # CORREGIDO in this run
    trend: list[dict[str, Any]] = field(default_factory=list)
    endpoints: list[dict[str, Any]] = field(default_factory=list)  # AUTHZ inventory
    ai_summary: dict[str, str] | None = None  # executive summary from the AI module (T3)
    sbom: dict[str, Any] | None = None  # CycloneDX (SBOM module)
    verdict: dict[str, Any] | None = None  # vendor delivery verdict
    rules_version: str = ""
    # Known open findings that sit in places this run left out (kept as they were).
    omitted_findings: int = 0
    # User rule files the engine accepted and ran, with their rule IDs (P6).
    user_rules: list[dict[str, Any]] = field(default_factory=list)

    def summary(self) -> dict[str, Any]:
        """Counts for the run; severity and category only count what is open."""
        return summarize(self.findings, len(self.fixed))

    def to_dict(self) -> dict[str, Any]:
        plan = self.plan
        return {
            "schema": SCHEMA_VERSION,
            "heimdall_version": __version__,
            "project": {
                "name": plan.root.name,
                "path": str(plan.root),
                "tree_hash": self.tree_hash,
                "files_analyzed": len(plan.tree.analyzable),
            },
            "run": {
                "started": self.started.isoformat(timespec="seconds"),
                "finished": self.finished.isoformat(timespec="seconds"),
                "profile": plan.profile,
                "modules": sorted(plan.modules),
                "exclusions": [*plan.exclusions.dirs, *plan.exclusions.file_entries],
                "rules_version": self.rules_version,
            },
            "stack": [hit.to_dict() for hit in plan.stacks],
            "tools": [tool.to_dict() for tool in self.tools],
            "limitations": self.limitations,
            "summary": self.summary(),
            "ai_summary": self.ai_summary,
            "verdict": self.verdict,
            "baseline": {
                "run": self.run_id,
                "previous_run": self.previous_run_id,
                "trend": self.trend,
            }
            if self.run_id is not None
            else None,
            "endpoints": self.endpoints,
            "findings": [finding.to_dict() for finding in self.findings],
            "fixed": self.fixed,
            "omitted": {
                "folders": list(plan.tree.skipped_dirs),
                "files": list(plan.tree.pattern_skipped),
                "findings": self.omitted_findings,
            },
            "sbom": self.sbom,
            "user_rules": self.user_rules,
        }


def build_plan(
    root: Path,
    *,
    profile: str,
    custom_modules: frozenset[Module] | None = None,
    exclusions: Exclusions | None = None,
    extra_rule_dirs: Iterable[str] = (),
) -> Plan:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(t("core.error.not_a_folder", path=root))
    exclusions = exclusions or Exclusions()
    tree = scan_tree(root, exclusions)
    # Copied libraries are third-party code: their files are kept out of the code rules only.
    vendored = detect_vendored(root, tree.analyzable)
    exclusions = dataclasses.replace(exclusions, sast_files=tuple(lib.file for lib in vendored))
    dirs = tuple(extra_rule_dirs)
    user = check_user_rules(dirs, analyzed_root=root, own_ids=own_rule_ids()) if dirs else None
    return Plan(
        root=root,
        profile=profile,
        requested=resolve(profile, custom_modules),
        tree=tree,
        stacks=detect(root, tree.files),
        exclusions=exclusions,
        user_rules=user.files if user else (),
        user_rule_problems=user.problems if user else (),
        vendored=vendored,
    )


def _merge(findings: list[Finding]) -> list[Finding]:
    """Merges findings with the same fingerprint and keeps the highest severity."""
    merged: dict[str, Finding] = {}
    for finding in findings:
        kept = merged.get(finding.fingerprint)
        if kept is None:
            merged[finding.fingerprint] = finding
            continue
        if finding.severity.rank < kept.severity.rank:
            kept.severity = finding.severity
        kept.detected_by = sorted({*kept.detected_by, *finding.detected_by})
        kept.references = list(dict.fromkeys([*kept.references, *finding.references]))
        kept.fixed_version = kept.fixed_version or finding.fixed_version
    return list(merged.values())


def _finalize(
    findings: list[Finding], exclusions: Exclusions, secrets: set[str], year: int
) -> list[Finding]:
    # Exclusions are applied here, uniformly, without depending on how each
    # tool interprets them.
    kept = [
        f
        for f in findings
        if not exclusions.excludes(
            f.file, sast=f.category in _SAST_CATEGORIES, secret=f.category == Category.SECRETS
        )
    ]
    for finding in kept:
        finding.snippet = mask_generic(mask_known(finding.snippet, secrets))
        finding.title = mask_known(finding.title, secrets)
        finding.description = mask_known(finding.description, secrets)
        for texts in finding.texts.values():
            for name in ("title", "description"):
                if name in texts:
                    texts[name] = mask_known(texts[name], secrets)
    kept = _merge(kept)
    kept.sort(key=lambda f: (f.severity.rank, f.file, f.line_start, f.rule_id, f.fingerprint))
    # Sequential per run; it becomes per project with the baseline (H3).
    for number, finding in enumerate(kept, start=1):
        finding.id = f"HDL-{year}-{number:06d}"
    return kept


# A candidate this close to a reported finding is the same place: it is already reported.
CANDIDATE_NEAR_LINES = 3


def _prepare_candidates(
    candidates: list[Finding], final: list[Finding], exclusions: Exclusions, secrets: set[str]
) -> list[Finding]:
    """Candidates for the AI: excluded files out, snippets masked, duplicates merged and
    the ones next to a deterministic finding (already reported) dropped.

    Unlike findings they get no ID and never reach the summary, the verdict or the reports.
    """
    kept = [c for c in candidates if not exclusions.excludes(c.file, sast=True, secret=False)]
    for candidate in kept:
        candidate.snippet = mask_generic(mask_known(candidate.snippet, secrets))
    reported: dict[str, list[int]] = {}
    for finding in final:
        if finding.origin is Origin.DETERMINISTIC and finding.category in _SAST_CATEGORIES:
            reported.setdefault(finding.file, []).append(finding.line_start)
    # Merged per line, not per fingerprint: two identical lines in one file (the same
    # `rawQuery(sql, null)` in two functions) are two different places to review.
    unique: dict[tuple[str, int], Finding] = {}
    for candidate in kept:
        unique.setdefault((candidate.fingerprint, candidate.line_start), candidate)
    return [
        c
        for c in unique.values()
        if not any(
            abs(c.line_start - line) <= CANDIDATE_NEAR_LINES for line in reported.get(c.file, ())
        )
    ]


def _ai_stats(result: ScanResult) -> dict[str, Any]:
    """Aggregate figures for the executive summary: they never include code (T3).

    The labels use the run's language, which is the one of the summary prompt.
    """
    lang = get_language()
    summary = result.summary()
    titles = Counter(
        text_of(f, "title", lang) for f in result.findings if f.origin is Origin.DETERMINISTIC
    )
    stacks = ", ".join(hit.stack for hit in result.plan.stacks) or t("core.ai_stats.none", lang)
    stats: dict[str, Any] = {
        t("core.ai_stats.profile", lang): result.plan.profile,
        t("core.ai_stats.files", lang): len(result.plan.tree.analyzable),
        t("core.ai_stats.stacks", lang): stacks,
        t("core.ai_stats.open_total", lang): sum(summary["by_severity"].values()),
    }
    stats |= {
        t("core.ai_stats.by_severity", lang, name=label(name, "severity", lang)): n
        for name, n in summary["by_severity"].items()
    }
    stats |= {
        t("core.ai_stats.by_category", lang, name=label(name, "category", lang, variant="snake")): n
        for name, n in summary["by_category"].items()
    }
    if result.endpoints:
        stats[t("core.ai_stats.endpoints", lang)] = len(result.endpoints)
        stats[t("core.ai_stats.endpoints_open", lang)] = sum(
            1 for e in result.endpoints if e["has_auth"] is False
        )
    ai_new = sum(
        1
        for f in result.findings
        if f.origin is Origin.AI and (f.llm_assessment or {}).get("task") == "T4"
    )
    if ai_new:
        stats[t("core.ai_stats.ai_new", lang)] = ai_new
    stats[t("core.ai_stats.frequent", lang)] = "; ".join(
        f"{title} ({count})" for title, count in titles.most_common(5)
    )
    return stats


def _ai_tool(outcome: AiOutcome) -> ToolRun:
    """Row of the AI module in the tools table, with the models used (P6)."""
    detail: Message | str = outcome.detail
    if outcome.asked or outcome.cached:
        stats = {
            "destination": outcome.destination,
            "valid": outcome.valid,
            "asked": outcome.asked,
            "cached": outcome.cached,
            "sinks_reviewed": outcome.sinks_reviewed,
            "sinks_found": outcome.sinks_found,
        }
        detail = (
            msg("core.tool.ai_stats_detail", **stats, detail=outcome.detail)
            if outcome.detail
            else msg("core.tool.ai_stats", **stats)
        )
    ai_stats: dict[str, Any] = {}
    if outcome.sinks_reviewed:
        ai_stats = {"sinks_reviewed": outcome.sinks_reviewed, "sinks_found": outcome.sinks_found}
    if outcome.truncated:
        ai_stats["truncated"] = outcome.truncated
    return ToolRun(
        "llm",
        outcome.status,
        version=", ".join(outcome.models) or None,
        seconds=outcome.seconds,
        findings=len(outcome.findings),
        detail=detail,
        stats=ai_stats or None,
    )


def _run_ai(
    ai: AiRunner | None,
    plan: Plan,
    findings: list[Finding],
    endpoints: list[dict[str, Any]],
    secrets: set[str],
    candidates: list[Finding],
    tools: list[ToolRun],
    limitations: list[Message],
    *,
    notify: Callable[[str, str | Message], None],
    cancelled: Callable[[], bool] | None,
) -> list[Finding]:
    """Runs the AI module; whatever happens, the run continues ."""
    if ai is None:
        tools.append(ToolRun("llm", "skipped", detail=msg("core.tool.no_ai_config")))
        limitations.append(msg("core.limit.ai_disabled"))
        return []
    # Each target can take tens of seconds: progress is reported one by one and
    # cancelling is allowed between them.
    ai.on_progress = lambda done, total: notify(
        "llm", msg("core.ai.progress", done=done, total=total)
    )
    ai.cancelled = cancelled
    outcome = ai.run(
        findings,
        endpoints,
        plan.root,
        secrets,
        candidates=candidates,
        files=plan.tree.analyzable,
    )
    tools.append(_ai_tool(outcome))
    limitations += outcome.limitations
    if outcome.status != "ran":
        limitations.append(msg("core.limit.ai_unavailable", detail=outcome.detail))
    return outcome.findings


@dataclass
class _Collected:
    """What the adapters leave behind over the course of the run."""

    tools: list[ToolRun] = field(default_factory=list)
    limitations: list[Message] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    candidates: list[Finding] = field(default_factory=list)
    secrets: set[str] = field(default_factory=set)
    endpoints: list[Endpoint] = field(default_factory=list)
    sbom: dict[str, Any] | None = None
    rule_files: list[Path] = field(default_factory=list)


def _examples(paths: list[str], limit: int = 3) -> Message:
    """ "e.g. a, b, c" or "e.g. a, b, c and others": the paths are data, not text."""
    code = "core.examples.many" if len(paths) > limit else "core.examples.few"
    return msg(code, paths=paths[:limit])


def _plan_limitations(plan: Plan) -> list[Message]:
    limitations = []
    if plan.pending_modules:
        limitations.append(msg("core.limit.pending_modules", names=list(plan.pending_modules)))
    for module in sorted(plan.modules & PARTIAL.keys()):
        limitations.append(
            msg("core.limit.partial_module", module=module, reason=msg(PARTIAL[module]))
        )
    limit = plan.exclusions.max_file_kb
    if plan.tree.large_code:
        limitations.append(
            msg(
                "core.limit.large_code",
                count=len(plan.tree.large_code),
                limit=limit,
                examples=_examples(plan.tree.large_code),
            )
        )
    if plan.tree.oversized:
        limitations.append(
            msg(
                "core.limit.oversized",
                count=len(plan.tree.oversized),
                limit=limit,
                examples=_examples(plan.tree.oversized),
            )
        )
    if plan.tree.pattern_skipped:
        limitations.append(
            msg(
                "core.limit.pattern_skipped",
                count=len(plan.tree.pattern_skipped),
                patterns=", ".join(plan.exclusions.file_entries),
                examples=_examples(plan.tree.pattern_skipped),
            )
        )
    if plan.tree.symlinks:
        limitations.append(msg("core.limit.symlinks", count=plan.tree.symlinks))
    if plan.vendored:
        recognized = [f"{lib.name} {lib.version} ({lib.file})" for lib in plan.vendored]
        limitations.append(
            msg(
                "core.limit.vendored_found",
                count=len(recognized),
                examples=_examples(recognized, limit=5),
            )
        )
    if Module.DEP in plan.modules:
        direct_only = direct_only_manifests(plan.root, plan.tree.files)
        if direct_only:
            limitations.append(
                msg(
                    "core.limit.direct_only",
                    count=len(direct_only),
                    examples=_examples(direct_only),
                )
            )
    for problem in plan.user_rule_problems:
        limitations.append(
            msg("core.limit.user_rule_problem", file=problem.file, detail=problem.message)
        )
    limitations += coverage_notes(hit.stack for hit in plan.stacks)
    return limitations


def _days_old(timestamp: str | None) -> int | None:
    if not timestamp:
        return None
    try:
        # Trivy gives nanoseconds; `fromisoformat` accepts up to microseconds.
        moment = datetime.fromisoformat(re.sub(r"(\.\d{6})\d+", r"\1", timestamp))
    except ValueError:
        return None
    if moment.tzinfo is None:
        moment = moment.astimezone()
    return (datetime.now().astimezone() - moment).days


def _run_adapter(
    adapter: Adapter, ctx: ScanContext, collected: _Collected, db_alert_days: int = DB_ALERT_DAYS
) -> None:
    affected = ", ".join(sorted(adapter.modules & ctx.modules))
    if not adapter.is_available():
        collected.tools.append(
            ToolRun(adapter.name, "skipped", detail=msg("core.tool.not_installed"))
        )
        collected.limitations.append(
            msg("core.limit.not_installed", tool=adapter.name, affected=affected)
        )
        return
    tool = ToolRun(
        adapter.name,
        "ran",
        version=adapter.version(),
        db_updated_at=adapter.db_updated_at(),
    )
    clock = time.monotonic()
    try:
        outcome = adapter.invoke(ctx)
    except MissingDatabaseError as exc:
        tool.status = "error"
        tool.detail = exc.message
        note = exc.message if exc.partial else missing_database()
        if note not in collected.limitations:
            collected.limitations.append(note)
    except AdapterError as exc:
        tool.status = "error"
        tool.detail = exc.message
        collected.limitations.append(
            msg("core.limit.tool_failed", tool=adapter.name, affected=affected)
        )
    else:
        tool.findings = len(outcome.findings)
        collected.findings += outcome.findings
        collected.candidates += outcome.candidates
        collected.endpoints += outcome.endpoints
        collected.sbom = outcome.sbom or collected.sbom
        collected.rule_files += outcome.rule_files
        collected.limitations += [x for x in outcome.limitations if x not in collected.limitations]
        collected.secrets |= outcome.secrets
    tool.seconds = time.monotonic() - clock
    collected.tools.append(tool)
    age = _days_old(tool.db_updated_at)
    if age is not None and age > db_alert_days:
        collected.limitations.append(msg("core.limit.db_old", tool=adapter.name, age=age))


class ScanCancelled(Exception):  # noqa: N818 - not an error: the user asks for it
    """The user cancelled the run; nothing is saved."""


def _set_aside_vendored(
    findings: list[Finding], plan: Plan, limitations: list[Message]
) -> list[Finding]:
    """Code-rule findings inside copied libraries are not reported: third-party code.

    They are counted in their own limitation, apart from the folders the user skips.
    """
    vendored_files = {lib.file for lib in plan.vendored}

    def is_set_aside(f: Finding) -> bool:
        return f.category in _SAST_CATEGORIES and f.file in vendored_files

    aside = [f for f in findings if is_set_aside(f)]
    if not aside:
        return findings
    limitations.append(
        msg(
            "core.limit.vendored_sast",
            count=len(aside),
            examples=_examples(sorted({f.file for f in aside})),
        )
    )
    return [f for f in findings if not is_set_aside(f)]


def run_scan(
    plan: Plan,
    *,
    update_dbs: bool = False,
    adapters: list[Adapter] | None = None,
    ai: AiRunner | None = None,
    on_progress: Callable[[str, str | Message], None] | None = None,
    cancelled: Callable[[], bool] | None = None,
    db_alert_days: int = DB_ALERT_DAYS,
) -> ScanResult:
    """Runs the scan.

    `on_progress(tool, status)` reports when each tool starts ("start") and how
    it ends; AI progress arrives as a structured message (`core.ai.progress`,
    with `done` and `total`) so it can be shown in the current language.
    `cancelled()` is consulted between tools.
    """
    started = datetime.now().astimezone()
    collected = _Collected(limitations=_plan_limitations(plan))

    def notify(name: str, status: str | Message) -> None:
        if on_progress is not None:
            on_progress(name, status)

    def check_cancelled() -> None:
        if cancelled is not None and cancelled():
            raise ScanCancelled

    # The temporary directory lives outside the analyzed folder (P1).
    with tempfile.TemporaryDirectory(prefix="heimdall-") as tmp:
        ctx = ScanContext(
            root=plan.root,
            files=plan.tree.analyzable,
            modules=plan.modules,
            stacks=frozenset(hit.stack for hit in plan.stacks),
            exclusions=plan.exclusions,
            workdir=Path(tmp),
            update_dbs=update_dbs,
            user_rules=plan.user_rules,
            vendored=plan.vendored,
        )
        # Only a scan that may download databases takes the cross-process lock.
        guard = (
            database_lock(lambda text: notify("databases", text))
            if update_dbs
            else contextlib.nullcontext()
        )
        with guard:
            for adapter in adapters if adapters is not None else default_adapters():
                if adapter.applies(ctx):
                    check_cancelled()
                    notify(adapter.name, "start")
                    _run_adapter(adapter, ctx, collected, db_alert_days)
                    notify(adapter.name, collected.tools[-1].status)

    # Where the inventory already evaluated a handler, its verdict replaces the
    # equivalent Opengrep rule's, which does not cross routes or configuration.
    covered = {(e.file, line) for e in collected.endpoints for line in (e.line, *e.covers)}
    findings = [
        f
        for f in collected.findings
        if not (f.rule_id in SUPERSEDED_RULES and (f.file, f.line_start) in covered)
    ]

    findings = _set_aside_vendored(findings, plan, collected.limitations)

    secrets, year = collected.secrets, started.year
    # Some tools (OSV, Gitleaks) also read omitted folders, such as the build
    # output (bin/, obj/). What they find there is not reported, but how much it
    # was is stated so the annex does not seem to contradict the summary.
    dropped = [
        f
        for f in findings
        if plan.exclusions.excludes(
            f.file, sast=f.category in _SAST_CATEGORIES, secret=f.category == Category.SECRETS
        )
    ]
    if dropped:
        places = sorted({f.file for f in dropped})
        collected.limitations.append(
            msg("core.limit.dropped", count=len(dropped), examples=_examples(places))
        )
    final = _finalize(findings, plan.exclusions, secrets, year)
    endpoint_rows = [endpoint.to_dict() for endpoint in collected.endpoints]
    use_ai = Module.AI in plan.modules
    if use_ai:
        check_cancelled()
        notify("llm", "start")
        candidates = _prepare_candidates(collected.candidates, final, plan.exclusions, secrets)
        suggested = _run_ai(
            ai, plan, final, endpoint_rows, secrets, candidates, collected.tools,
            collected.limitations,
            notify=notify, cancelled=cancelled,
        )  # fmt: skip
        notify("llm", collected.tools[-1].status)
        check_cancelled()
        final = _finalize([*final, *suggested], plan.exclusions, secrets, year)

    # The annex shows what each tool contributed to the report, not its raw
    # count: after omitting folders, merging duplicates and replacing rules.
    for tool in collected.tools:
        if tool.status == "ran":
            tool.findings = sum(1 for f in final if tool.name in f.detected_by)

    result = ScanResult(
        plan=plan,
        tree_hash=tree_hash(plan.root, plan.tree.files),
        started=started,
        finished=datetime.now().astimezone(),
        tools=collected.tools,
        limitations=collected.limitations,
        findings=final,
        endpoints=endpoint_rows,
        sbom=collected.sbom,
        rules_version=rules_version(collected.rule_files),
        user_rules=[{"file": path.name, "ids": rule_ids_of(path)} for path in collected.rule_files],
    )
    if use_ai and ai is not None:
        notify("summary", "start")
        _summarize(ai, result)
        notify("summary", "ran" if result.ai_summary else "skipped")
    return result


def _summarize(ai: AiRunner, result: ScanResult) -> None:
    known = len(ai.outcome.limitations)
    ai.summarize(_ai_stats(result))
    if ai.outcome.summary:
        result.ai_summary = {
            "text": ai.outcome.summary,
            "language": ai.outcome.summary_language,
            "model": ai.outcome.models[-1] if ai.outcome.models else "",
        }
    result.limitations += ai.outcome.limitations[known:]
    # The summary also queries the model: its row is updated.
    result.tools = [_ai_tool(ai.outcome) if t.name == "llm" else t for t in result.tools]
    result.finished = datetime.now().astimezone()


def issue_verdict(result: ScanResult, thresholds: Thresholds, issuer: str) -> None:
    """Issues the run's verdict with the baseline statuses already applied."""
    result.verdict = evaluate(
        result.findings,
        thresholds,
        issuer=issuer,
        tree_hash=result.tree_hash,
        rules_version=result.rules_version,
        issued=result.started.isoformat(timespec="seconds"),
    ).to_dict()
