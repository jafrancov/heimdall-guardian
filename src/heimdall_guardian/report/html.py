"""Self-contained HTML report: executive and technical in a single file."""

from __future__ import annotations

import base64
from collections import Counter
from typing import Any

from jinja2 import Environment, PackageLoader, StrictUndefined

from ..core import owasp as owasp_top10
from ..core.finding import BaselineStatus, Category, Severity
from ..core.palette import ASSETS, BRONZE, GOLD, GOOD, LINE, NIGHT, SEVERITY_COLORS
from ..i18n import get_language, label, render, t, text_of, tn
from . import text
from .plan import fix_plan, ids_text, plan_line

SEVERITIES = tuple(s.value for s in Severity)
OPEN_STATUSES = (BaselineStatus.NEW.value, BaselineStatus.PERSISTENT.value)
_TREND_RUNS = 12

# Finding content comes from third-party code: autoescape is always on.
_ENV = Environment(
    loader=PackageLoader("heimdall_guardian.report"),
    autoescape=True,
    undefined=StrictUndefined,
    trim_blocks=True,
    lstrip_blocks=True,
)
_ENV.filters["lbl"] = lambda value, kind, variant="default": label(value, kind, variant=variant)
_ENV.filters["r"] = render  # a stored message, in the current language
# Fixed texts are requested from the catalog when rendering, never on import.
_ENV.globals.update(
    t=t,
    tn=tn,
    text_of=text_of,
    profile_name=text.profile_name,
    tool_status=text.tool_status,
    database_label=text.database_label,
    yes_no=text.yes_no,
    methods_label=text.methods_label,
    ai_verdict=text.ai_verdict,
    ai_reachable=text.ai_reachable,
    ai_level=text.ai_level,
    risk_level=text.risk_level,
)


def _image(name: str) -> str:
    """A brand image embedded as base64: the report does not depend on external files."""
    try:
        data = (ASSETS / name).read_bytes()
    except OSError:
        return ""
    return "data:image/png;base64," + base64.b64encode(data).decode("ascii")


def _rank(finding: dict[str, Any]) -> int:
    return SEVERITIES.index(finding["severity"]) if finding["severity"] in SEVERITIES else 99


def _traffic_light(counts: dict[str, int]) -> str:
    if counts.get(Severity.CRITICAL, 0):
        return "rojo"
    return "amarillo" if counts.get(Severity.HIGH, 0) else "verde"


def _top_risks(open_findings: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    """Groups by rule (or by package, for dependencies) and takes the most severe."""
    groups: dict[tuple[str, str], dict[str, Any]] = {}
    for finding in sorted(open_findings, key=_rank):
        is_dependency = finding["category"] == Category.DEPENDENCIES
        package = finding["snippet"].split("@")[0]
        key = ("dep", package) if is_dependency else ("rule", finding["rule_id"])
        group = groups.setdefault(
            key,
            {
                "severity": finding["severity"],
                "title": t("report.risk.vulnerable_dependency", package=package)
                if is_dependency
                else text_of(finding, "title"),
                "count": 0,
                "files": set(),
            },
        )
        group["count"] += 1
        group["files"].add(finding["file"])
    ranked = sorted(groups.values(), key=lambda g: (SEVERITIES.index(g["severity"]), -g["count"]))
    return [{**group, "files": len(group["files"])} for group in ranked[:limit]]


def _trend(runs: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Stacked bars of open findings by severity, one per run."""
    runs = [run for run in runs if "by_severity" in run][-_TREND_RUNS:]
    if len(runs) < 2:
        return None
    width, height, gap = 44, 120, 14
    top = max(sum(run["by_severity"].values()) for run in runs) or 1
    bars = []
    for index, run in enumerate(runs):
        y = float(height)
        segments = []
        for severity in reversed(SEVERITIES):
            count = run["by_severity"].get(severity, 0)
            size = count / top * height
            y -= size
            if count:
                segments.append(
                    {
                        "y": round(y, 1),
                        "h": round(size, 1),
                        "cls": SEVERITIES.index(severity),
                        "label": label(severity, "severity"),
                        "count": count,
                    }
                )
        bars.append(
            {
                "x": index * (width + gap),
                "segments": segments,
                "total": sum(run["by_severity"].values()),
                "run": run["run"],
                "date": run["started"][:10],
            }
        )
    return {
        "bars": bars,
        "bar_width": width,
        "height": height,
        "width": len(bars) * (width + gap) - gap,
    }


def coverage_colors() -> dict[str, tuple[str, str, str, str]]:
    """Color of each coverage level: green yes, amber partly, gray no (shared palette)."""
    return {
        "yes": GOOD,
        "partial": SEVERITY_COLORS[Severity.MEDIUM],
        "no": SEVERITY_COLORS[Severity.INFO],
    }


def _omitted_block(payload: dict[str, Any]) -> dict[str, Any] | None:
    if not text.has_omitted(payload):
        return None
    entries, more = text.omitted_entries(payload, 200)
    return {
        "sentence": text.omitted_sentence(payload),
        "findings": text.omitted_findings_sentence(payload),
        "entries": entries,
        "more": t("report.omitted.more", count=more) if more else "",
    }


def build_context(payload: dict[str, Any]) -> dict[str, Any]:
    payload = owasp_top10.migrate_payload(payload)
    findings: list[dict[str, Any]] = payload["findings"]
    open_findings = [f for f in findings if f["baseline_status"] in OPEN_STATUSES]
    counts: dict[str, int] = payload["summary"]["by_severity"]
    light = _traffic_light(counts)

    code = [
        {**f, "verification_hint": owasp_top10.verification_hint(f.get("cwe"))}
        for f in findings
        if f["category"] != Category.DEPENDENCIES
    ]
    dependencies = sorted(
        (f for f in findings if f["category"] == Category.DEPENDENCIES),
        key=lambda f: (_rank(f), f["snippet"], f["rule_id"]),
    )
    unclassified = t("report.owasp.unclassified")
    owasp = Counter(f["owasp"] or unclassified for f in open_findings)
    baseline = payload.get("baseline")
    return {
        "p": payload,
        "light": light,
        "light_text": t(f"report.light.{light}.text"),
        "light_name": t(f"report.light.{light}"),
        "html_lang": text.html_lang(),
        "english": get_language() == "en",
        "coverage_levels": owasp_top10.COVERAGE_LEVELS,
        "counts": counts,
        "states": payload["summary"].get("by_status", {}),
        "open_total": len(open_findings),
        "top_risks": _top_risks(open_findings),
        "plan": [
            {"severity": g.severity, "line": plan_line(g), "ids": ids_text(g)}
            for g in fix_plan(payload)
        ],
        "owasp": sorted(owasp.items()),
        "top10": owasp_top10.coverage_rows(open_findings),
        "what_is_owasp": owasp_top10.what_is_owasp(),
        "scope_warning": owasp_top10.scope_warning(),
        "coverage_colors": coverage_colors(),
        "owasp_max": max(owasp.values(), default=1),
        "groups": [(s, [f for f in code if f["severity"] == s]) for s in SEVERITIES],
        "code_total": len(code),
        "dependencies": dependencies,
        "fixed": payload.get("fixed", []),
        "baseline": baseline,
        "trend": _trend(baseline["trend"]) if baseline else None,
        "severities": SEVERITIES,
        "omitted": _omitted_block(payload),
        "disclaimer": text.disclaimer(),
        "colors": SEVERITY_COLORS,
        "ok": GOOD,
        "structure": {"noche": NIGHT, "oro": GOLD, "bronce": BRONZE, "line": LINE},
        "tagline": text.tagline(),
        "logo": _image("emblema.png"),
        "watermark": _image("sello.png"),
    }


def render_html(payload: dict[str, Any]) -> str:
    return _ENV.get_template("report.html.j2").render(**build_context(payload))
