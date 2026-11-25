"""The "Where to start" fix plan: open findings grouped by common cause, worst first.

Computed from the run dictionary when a report or a screen is drawn; it is never stored.
Deterministic findings only (AI suggestions do not count, P5).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from ..core.finding import BaselineStatus, Category, Origin, Severity
from ..i18n import t, text_of, tn

_SEVERITIES = tuple(s.value for s in Severity)
_OPEN = (BaselineStatus.NEW.value, BaselineStatus.PERSISTENT.value)
_CHUNKS = re.compile(r"\d+|[A-Za-z]+")
MAX_IDS_SHOWN = 5


@dataclass(frozen=True)
class FixGroup:
    kind: str  # "dependency" | "rule"
    key: str  # package name or rule_id
    count: int
    files: int
    severity: str  # the worst one in the group
    target: str  # dependencies: version to update to ("" if none is known)
    title: str  # rule groups: a representative visible title
    ids: tuple[str, ...]  # finding IDs


def _version_key(version: str) -> tuple[tuple[int, int, str], ...]:
    """Tolerant ordering key: numbers compare as numbers, pre-release words sort first."""
    chunks: list[tuple[int, int, str]] = []
    for chunk in _CHUNKS.findall(version.strip().lstrip("vV")):
        chunks.append((2, int(chunk), "") if chunk.isdigit() else (0, 0, chunk.lower()))
    chunks.append((1, 0, ""))
    return tuple(chunks)


def _highest(versions: list[str]) -> str:
    return max(versions, key=_version_key, default="")


def _rank(severity: str) -> int:
    return _SEVERITIES.index(severity) if severity in _SEVERITIES else len(_SEVERITIES)


def _package(finding: dict[str, Any]) -> str:
    snippet = str(finding.get("snippet") or "")
    return snippet.rpartition("@")[0] if "@" in snippet else ""


def fix_plan(payload: dict[str, Any], lang: str | None = None, limit: int = 10) -> list[FixGroup]:
    """Groups the open deterministic findings by package or rule, worst and biggest first."""
    buckets: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for finding in payload.get("findings") or []:
        if finding.get("baseline_status") not in _OPEN:
            continue
        if finding.get("origin", Origin.DETERMINISTIC.value) != Origin.DETERMINISTIC.value:
            continue
        package = _package(finding) if finding.get("category") == Category.DEPENDENCIES else ""
        bucket = ("dependency", package) if package else ("rule", str(finding.get("rule_id", "")))
        buckets.setdefault(bucket, []).append(finding)

    groups: list[FixGroup] = []
    for (kind, key), items in buckets.items():
        versions = [
            v.strip()
            for item in items
            for v in str(item.get("fixed_version") or "").split(",")
            if v.strip()
        ]
        groups.append(
            FixGroup(
                kind=kind,
                key=key,
                count=len(items),
                files=len({str(item.get("file", "")) for item in items}),
                severity=min((str(i.get("severity")) for i in items), key=_rank),
                target=_highest(versions) if kind == "dependency" else "",
                title=text_of(items[0], "title", lang) if kind == "rule" else "",
                ids=tuple(str(i["id"]) for i in items if i.get("id")),
            )
        )
    groups.sort(key=lambda g: (_rank(g.severity), -g.count, g.key))
    return groups[: max(limit, 0)]


def plan_line(group: FixGroup, lang: str | None = None) -> str:
    """The action sentence of a group, in the requested (or current) language."""
    findings = tn("report.plan.findings", group.count, lang)
    files = tn("report.plan.files", group.files, lang)
    if group.kind == "dependency" and group.target:
        return t(
            "report.plan.update",
            lang,
            package=group.key,
            version=group.target,
            findings=findings,
            files=files,
        )
    if group.kind == "dependency":
        return t("report.plan.review", lang, package=group.key, findings=findings)
    return t(
        "report.plan.rule", lang, title=group.title or group.key, findings=findings, files=files
    )


def ids_text(group: FixGroup) -> str:
    """The first IDs of a group, with an ellipsis when there are more."""
    shown = ", ".join(group.ids[:MAX_IDS_SHOWN])
    return shown + (" …" if len(group.ids) > MAX_IDS_SHOWN else "")
