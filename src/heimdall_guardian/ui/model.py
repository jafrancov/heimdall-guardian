"""What the interface says and draws, computed without Flet (and therefore testable)."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from ..core import cli_setup, owasp, palette
from ..core.config import Config, ConfigError, LegacyConfigError, load_config, save_config
from ..core.coverage import rule_stack_names
from ..core.files import Exclusions, is_file_pattern
from ..core.finding import BaselineStatus, Severity
from ..core.paths import data_location_lines
from ..core.presets import Suggestion
from ..core.profiles import CUSTOM_PROFILE, PROFILES
from ..core.profiles import profile_name as profile_name
from ..core.subprojects import SubProject
from ..core.user_rules import UserRules, rule_ids_of
from ..core.verdict import Outcome
from ..i18n import (
    apply_language,
    get_language,
    has_message,
    label,
    render,
    set_language,
    t,
    text_of,
    tn,
)
from ..report import text as report_text
from ..report.plan import fix_plan, plan_line

# The interface takes colors and slogans from here.
ASSETS = palette.ASSETS
NIGHT = palette.NIGHT
CHARCOAL = palette.CHARCOAL
GOLD = palette.GOLD
GOLD_LIGHT = palette.GOLD_LIGHT
BRONZE = palette.BRONZE
SAND = palette.SAND
GOOD = palette.GOOD
WHITE = palette.WHITE
GRAY_LIGHT = palette.GRAY_LIGHT
GRAY_MID = palette.GRAY_MID
GRAY_DARK = palette.GRAY_DARK
LINE = palette.LINE
PAPER = palette.PAPER
SEVERITY_COLORS = palette.SEVERITY_COLORS

SEVERITIES = tuple(s.value for s in Severity)
OPEN_STATUSES = (BaselineStatus.NEW.value, BaselineStatus.PERSISTENT.value)
STRATUM_COLORS: dict[str, tuple[str, str]] = {
    name: colors[:2] for name, colors in SEVERITY_COLORS.items()
}

_MODULE_SLUGS = {
    "SEC": "sec",
    "SEC-H": "sec_h",
    "DEP": "dep",
    "CONF": "conf",
    "SAST": "sast",
    "AUTHZ": "authz",
    "AI": "ai",
    "SBOM": "sbom",
}
_TOOL_SLUGS = (
    "gitleaks",
    "trivy",
    "osv",
    "vendored",
    "opengrep",
    "bandit",
    "authz",
    "llm",
    "summary",
    "result",
)
_RISK_NAMES = {"idor_risk": "idor", "flow_risk": "flow", "risk": "sink"}


def parse_patterns(raw: str) -> list[str]:
    """File patterns typed by the user: commas or newlines apart, only glob entries."""
    entries = (part.strip() for part in raw.replace("\n", ",").split(","))
    return list(dict.fromkeys(e for e in entries if e and is_file_pattern(e)))


def pattern_text(entries: Iterable[str]) -> str:
    """The file-pattern entries of an exclusion list, as one editable line."""
    return ", ".join(e for e in entries if is_file_pattern(e))


def data_lines() -> list[str]:
    """Where the app keeps its data: the same folders the `hdl` command uses."""
    return data_location_lines()


def tagline() -> str:
    return t("ui.brand.tagline")


def motto() -> str:
    return t("ui.brand.motto")


def profiles() -> tuple[tuple[str, str, str], ...]:
    """(key, name, description) of each «how thorough» option, in the current language."""
    return tuple(
        (code, t(f"ui.profile.{code}.name"), t(f"ui.profile.{code}.desc"))
        for code in (*PROFILES, CUSTOM_PROFILE)
    )


def module_name(code: str) -> str:
    slug = _MODULE_SLUGS.get(code)
    return t(f"ui.module.{slug}") if slug else code


def module_names() -> dict[str, str]:
    return {code: module_name(code) for code in _MODULE_SLUGS}


def _join_names(names: list[str]) -> str:
    """«A, B and C» in the current language."""
    if len(names) < 2:
        return "".join(names)
    return t("ui.list.and", first=", ".join(names[:-1]), last=names[-1])


def tool_name(name: str, stacks: Iterable[str] | None = None) -> str:
    """Visible name of a tool; Opengrep says which code it reviews when stacks are known."""
    if name == "opengrep" and stacks:
        names = rule_stack_names(stacks)
        if names:
            return t("ui.tool.opengrep_for", names=_join_names(names))
    return t(f"ui.tool.{name}") if name in _TOOL_SLUGS else name


def payload_stacks(payload: dict[str, Any]) -> list[str]:
    """Stack codes detected in a run payload."""
    return [hit["stack"] for hit in payload.get("stack") or []]


def severity_name(severity: str, count: int) -> str:
    """Singular or plural Spanish label depending on the count (in English it does not change)."""
    return tn(f"ui.severity_name.{severity}", count)


def ai_opinion(assessment: dict[str, Any]) -> list[str]:
    """The AI suggestion as readable lines.

    T1 (triage) gives a verdict, T2 (endpoint) gives IDOR and flow risks, and T4 (risk
    point) says whether user input reaches it, from which input, and the risk.
    """
    lines: list[str] = []
    if assessment.get("reachable"):
        lines.append(
            t("ui.ai.reachable", answer=_ai_level("ui.ai.reachable", str(assessment["reachable"])))
        )
    if assessment.get("source"):
        lines.append(t("ui.ai.source", source=assessment["source"]))
    if assessment.get("verdict"):
        raw = str(assessment["verdict"])
        verdict_text = (
            t(f"ui.ai.verdict.{raw}")
            if has_message(f"ui.ai.verdict.{raw}")
            else raw.replace("_", " ").capitalize()
        )
        lines.append(
            t(
                "ui.ai.opinion",
                verdict=verdict_text,
                level=_ai_level("ui.ai.level", str(assessment.get("confidence", "low"))),
            )
        )
    risks = [
        t(
            "ui.ai.risk",
            name=t(f"ui.ai.risk_name.{slug}"),
            level=_ai_level("ui.ai.risk_level", str(assessment[key])),
        )
        for key, slug in _RISK_NAMES.items()
        if assessment.get(key)
    ]
    if risks:
        lines.append("; ".join(risks).capitalize() + ".")
    if assessment.get("explanation"):
        lines.append(render(assessment["explanation"]))
    if assessment.get("suggested_fix"):
        lines.append(t("ui.ai.suggested_fix", fix=assessment["suggested_fix"]))
    return lines


def _ai_level(prefix: str, value: str) -> str:
    key = f"{prefix}.{value}"
    return t(key) if has_message(key) else value


def count_label(count: int, severity: str) -> str:
    return f"{count} {severity_name(severity, count)}"


_DELIVERY_HEADLINES = {
    Outcome.NOT_APPROVED: "ui.delivery.not_approved",
    Outcome.APPROVED_WITH_OBSERVATIONS: "ui.delivery.approved_with_observations",
    Outcome.APPROVED: "ui.delivery.approved",
}


def delivery_verdict(delivery: dict[str, Any]) -> tuple[str, str]:
    """The vendor verdict in one sentence, and which criteria decide it."""
    exceeded = [c for c in delivery["criteria"] if c["exceeded"]]
    if exceeded:
        criteria = "; ".join(
            t(
                "ui.delivery.criterion",
                name=render(c["criterion"]).lower(),
                found=c["found"],
                maximum=c["limit"],
            )
            for c in exceeded
        )
        why = t("ui.delivery.exceeds", criteria=criteria)
    elif delivery["medium_open"]:
        why = t("ui.delivery.mediums", count=delivery["medium_open"])
    else:
        why = t("ui.delivery.within")
    return t(_DELIVERY_HEADLINES[delivery["outcome"]]), why


def verdict(summary: dict[str, Any], delivery: dict[str, Any] | None = None) -> tuple[str, str]:
    """The answer in one sentence, and the why beneath it."""
    if delivery:
        return delivery_verdict(delivery)
    counts: dict[str, int] = summary["by_severity"]
    critical, high = counts.get(Severity.CRITICAL, 0), counts.get(Severity.HIGH, 0)
    rest = sum(counts.get(s, 0) for s in (Severity.MEDIUM, Severity.LOW, Severity.INFO))
    if critical:
        headline = t("ui.verdict.critical.headline")
        critical_text = count_label(critical, Severity.CRITICAL)
        if high:
            why = t(
                "ui.verdict.critical.why_high",
                critical=critical_text,
                high=count_label(high, Severity.HIGH),
            )
        else:
            why = t("ui.verdict.critical.why", critical=critical_text)
    elif high:
        headline = t("ui.verdict.high.headline")
        why = t("ui.verdict.high.why", high=count_label(high, Severity.HIGH))
    elif rest:
        headline = t("ui.verdict.rest.headline")
        why = t("ui.verdict.rest.why", count=rest)
    else:
        headline = t("ui.verdict.clean.headline")
        why = t("ui.verdict.clean.why")
    return headline, why


def comparison(summary: dict[str, Any], previous_run: int | None) -> str:
    states: dict[str, int] = summary.get("by_status", {})
    if previous_run is None:
        return t("ui.compare.first")
    parts = [
        t("ui.compare.new", count=states.get("new", 0)),
        t("ui.compare.fixed", count=states.get("fixed", 0)),
        t("ui.compare.persistent", count=states.get("persistent", 0)),
    ]
    accepted = states.get("accepted", 0) + states.get("false_positive", 0)
    if accepted:
        parts.append(t("ui.compare.accepted", count=accepted))
    return t("ui.compare.since", previous=previous_run, parts=", ".join(parts))


@dataclass(frozen=True)
class Stratum:
    severity: str
    count: int
    flex: int  # proportion of height within the column
    background: str
    foreground: str


def strata(summary: dict[str, Any]) -> list[Stratum]:
    """One band per severity that has findings; its height grows with the count.

    The square root of the count is used: 40 dependencies must not crush 2 critical ones.
    """
    counts: dict[str, int] = summary["by_severity"]
    return [
        Stratum(
            severity,
            counts[severity],
            # Bounded: the smallest band always lets its number show.
            min(8, max(4, round(counts[severity] ** 0.5 * 2))),
            *STRATUM_COLORS[severity],
        )
        for severity in SEVERITIES
        if counts.get(severity, 0)
    ]


def visible_findings(
    findings: list[dict[str, Any]],
    severity: str | None,
    text: str = "",
    *,
    include_suppressed: bool = True,
) -> list[dict[str, Any]]:
    """Findings for the list: open ones first, filtered by stratum and by text."""
    needle = text.strip().lower()
    chosen = [
        f
        for f in findings
        if (severity is None or f["severity"] == severity)
        and (include_suppressed or f["baseline_status"] in OPEN_STATUSES)
        and (
            not needle
            or needle in f"{text_of(f, 'title')} {f['file']} {f['rule_id']} {f['id']}".lower()
        )
    ]
    return sorted(
        chosen,
        key=lambda f: (f["baseline_status"] not in OPEN_STATUSES, SEVERITIES.index(f["severity"])),
    )


def location(finding: dict[str, Any]) -> str:
    line = f":{finding['line_start']}" if finding["line_start"] else ""
    return f"{finding['file']}{line}"


# Heimdall Guardian coverage per category: (background, ink). Green yes, amber partly, gray no.
COVERAGE_COLORS = {
    "yes": palette.GOOD[2:4],
    "partial": palette.SEVERITY_COLORS[Severity.MEDIUM][2:4],
    "no": palette.SEVERITY_COLORS[Severity.INFO][2:4],
}


def owasp_overview(payload: dict[str, Any] | None) -> dict[str, Any]:
    """What the «What it reviews» section says: the 10 categories and, with a result, open ones."""
    open_findings = (
        [
            f
            for f in owasp.migrate_payload(payload)["findings"]
            if f["baseline_status"] in OPEN_STATUSES
        ]
        if payload
        else []
    )
    rows = []
    for row in owasp.coverage_rows(open_findings):
        background, ink = COVERAGE_COLORS[row["coverage"]]
        english = get_language() == "en"
        rows.append(
            {
                "title": f"{row['code']}:{owasp.YEAR} {row['name']}",
                "subtitle": "" if english else row["name_en"],
                "explanation": row["explanation"],
                "example": row["example"],
                "coverage": t(f"ui.coverage.{row['coverage']}"),
                "coverage_note": row["coverage_note"],
                "background": background,
                "ink": ink,
                "count": row["count"] if payload else None,
            }
        )
    return {
        "intro": owasp.what_is_owasp(),
        "edition": t("ui.coverage.edition", year=owasp.YEAR),
        "warning": owasp.scope_warning(),
        "rows": rows,
    }


def expert_facts(finding: dict[str, Any]) -> list[tuple[str, str]]:
    """Technical data of a finding for whoever verifies it: (label, value), without empty ones."""
    facts: list[tuple[str, str]] = []
    if finding.get("rule_id"):
        facts.append((t("ui.expert.rule"), str(finding["rule_id"])))
    tools = finding.get("detected_by") or []
    if tools:
        facts.append((t("ui.expert.tool"), ", ".join(tools)))
    if finding.get("cwe"):
        facts.append((t("ui.expert.cwe"), str(finding["cwe"])))
    owasp_label = owasp.migrate_2021(finding["owasp"]) if finding.get("owasp") else ""
    code = owasp.category_code(owasp_label)
    if owasp_label:
        name = next((c.name() for c in owasp.CATEGORIES if c.code == code), "")
        facts.append((t("ui.expert.owasp"), f"{owasp_label} ({name})" if name else owasp_label))
    if finding.get("confidence"):
        facts.append(
            (t("ui.expert.confidence"), label(finding["confidence"], "confidence", variant="lower"))
        )
    facts.append((t("ui.expert.location"), location(finding)))
    hint = owasp.verification_hint(finding.get("cwe"))
    if hint:
        facts.append((t("ui.expert.verify"), hint))
    return facts


AUTHOR = "Alejandro Franco"
ART_NOTICE = palette.ART_NOTICE  # the author's notice: shown as is in both languages
PROJECT_URL = "https://github.com/jafrancov/heimdall-guardian"


def about_update(result: Any) -> tuple[str, str | None]:
    """Line and release-page link for the About panel from an `updates.SelfUpdate`.

    The link is only offered when a newer release exists.
    """
    line = t("ui.about.update_line", installed=result.installed, status=result.status)
    return line, (result.page if result.outdated else None)


def profile_steps(profile: str, custom: set[str] | None = None) -> list[str]:
    """What each «how thorough» option reviews, in plain words."""
    codes = custom if profile == CUSTOM_PROFILE else PROFILES.get(profile, frozenset())
    steps = [name for code, name in module_names().items() if code in (codes or ())]
    if profile == "vendor":
        steps.append(t("ui.profile.verdict_step"))
    return steps


def plan_rows(payload: dict[str, Any]) -> list[dict[str, str]]:
    """The "Where to start" plan: severity code and action sentence per group."""
    return [{"severity": g.severity, "line": plan_line(g)} for g in fix_plan(payload)]


def run_facts(payload: dict[str, Any]) -> list[str]:
    """What actually ran in a run, including whether the AI took part."""
    tools = payload["tools"]
    ran = [run for run in tools if run["status"] == "ran" and run["name"] != "llm"]
    failed = [run for run in tools if run["status"] != "ran" and run["name"] != "llm"]
    stacks = payload_stacks(payload)
    facts = [t("ui.facts.ran", tools=", ".join(tool_name(run["name"], stacks) for run in ran))]
    if failed:
        facts.append(
            t(
                "ui.facts.failed",
                tools=", ".join(tool_name(run["name"], stacks) for run in failed),
            )
        )
    ai = next((run for run in tools if run["name"] == "llm"), None)
    if ai is None:
        facts.append(t("ui.facts.no_ai"))
    elif ai["status"] == "ran":
        summary = t(
            "ui.facts.ai_summary_yes" if payload.get("ai_summary") else "ui.facts.ai_summary_no"
        )
        facts.append(
            t(
                "ui.facts.ai_ran",
                model=ai["version"] or t("ui.facts.unnamed_model"),
                detail=render(ai["detail"]),
                summary=summary,
            )
        )
    else:
        facts.append(
            t("ui.facts.ai_failed", detail=render(ai["detail"]) or t("ui.facts.unavailable"))
        )
    facts.extend(_ai_new_facts(payload, ai))
    if report_text.has_omitted(payload):
        facts.append(t("ui.facts.omitted", parts=report_text.omitted_parts(payload)))
    return facts


def _ai_new_facts(payload: dict[str, Any], ai: dict[str, Any] | None) -> list[str]:
    """What the sink review (T4) added: new AI findings, or a clean bill for its points."""
    if ai is None or ai["status"] != "ran":
        return []
    found = sum(
        1
        for f in payload.get("findings", [])
        if f.get("origin") == "ai" and (f.get("llm_assessment") or {}).get("task") == "T4"
    )
    if found:
        return [tn("ui.facts.ai_new_findings", found)]
    reviewed = int((ai.get("stats") or {}).get("sinks_reviewed", 0))
    if reviewed:
        return [tn("ui.facts.ai_sinks_clear", reviewed)]
    return []


def suppressed_count(findings: list[dict[str, Any]]) -> int:
    return sum(1 for f in findings if f["baseline_status"] not in OPEN_STATUSES)


def recent_projects(
    projects: list[dict[str, Any]], current: str | None, limit: int = 5
) -> list[dict[str, Any]]:
    """The newest `limit` projects, ready for the compact list of the left panel."""
    return [
        {
            "path": item["path"],
            "name": item["name"],
            "date": str(item["started"])[:10],
            "tone": verdict_tone(item),
            "active": item["path"] == current,
        }
        for item in projects[:limit]
    ]


def verdict_tone(summary: dict[str, Any], delivery: dict[str, Any] | None = None) -> str:
    """Traffic-light color of the result sentence: red, amber or green."""
    red, amber, green = (
        SEVERITY_COLORS[Severity.CRITICAL][0],
        SEVERITY_COLORS[Severity.HIGH][3],
        GOOD[0],
    )
    if delivery:
        return {Outcome.NOT_APPROVED: red, Outcome.APPROVED_WITH_OBSERVATIONS: amber}.get(
            delivery["outcome"], green
        )
    counts = summary["by_severity"]
    if counts.get(Severity.CRITICAL, 0):
        return red
    return amber if counts.get(Severity.HIGH, 0) else green


def watch_line(projects: list[dict[str, Any]]) -> str:
    """Status of what is already being watched, for the welcome screen."""
    if not projects:
        return ""
    critical = sum(1 for p in projects if p.get("by_severity", {}).get(Severity.CRITICAL, 0))
    total = len(projects)
    if critical:
        return tn("ui.home.watch_critical", total, critical=critical)
    return tn("ui.home.watch_clear", total)


def ai_time_warning() -> str:
    return t("ui.ai.time_warning")


# ------------------------------------------------------- configuration and language


def load_startup_config(lang: str | None = None) -> tuple[Config, str | None]:
    """The configuration the interface starts with, the language already applied and a notice.

    A `config.toml` that cannot be used (e.g. from an earlier version, with keys in
    Spanish) does not prevent opening the application: the defaults are used and a notice is given.
    The file is not touched until the user saves the configuration.
    """
    try:
        config, notice = load_config(), None
    except LegacyConfigError as exc:
        config, notice = Config(), t("config.notice.old_version", path=exc.path)
    except ConfigError as exc:
        config, notice = Config(), str(exc)
    apply_language(lang, config=config.general.language)
    return config, notice


def change_language(config: Config, lang: str) -> Config:
    """Changes the language now and saves it to `config.toml`; returns the new configuration."""
    code = set_language(lang)
    updated = replace(config, general=replace(config.general, language=code))
    save_config(updated)
    return updated


# ------------------------------------------------------------ first-run tour

TOUR_STEPS = ("what", "wont", "read")
TOUR_ICONS = {"what": "SECURITY", "wont": "LOCK_OUTLINE", "read": "FACT_CHECK_OUTLINED"}


def tour_pending(config: Config) -> bool:
    """Whether the first-run tour has not been seen yet."""
    return not config.general.onboarding_seen


def tour_step(index: int) -> dict[str, str]:
    """Title, text, icon name and "n of total" indicator of one step (0-based)."""
    index = max(0, min(index, len(TOUR_STEPS) - 1))
    code = TOUR_STEPS[index]
    return {
        "title": t(f"ui.tour.{code}.title"),
        "body": t(f"ui.tour.{code}.body"),
        "icon": TOUR_ICONS[code],
        "indicator": t("ui.tour.indicator", current=index + 1, total=len(TOUR_STEPS)),
    }


def mark_tour_seen(config: Config) -> Config:
    """Records that the tour was seen and saves it; returns the new configuration."""
    if config.general.onboarding_seen:
        return config
    updated = replace(config, general=replace(config.general, onboarding_seen=True))
    save_config(updated)
    return updated


# ------------------------------------------------------- AI destinations

AI_TASK_IDS = ("triage", "endpoints", "sinks", "summary", "consensus")


def ai_tasks() -> tuple[tuple[str, str], ...]:
    """(task, model label) in the current language."""
    return tuple((task, t(f"ui.aitask.{task}")) for task in AI_TASK_IDS)


def destination_form(destination: Any) -> dict[str, str]:
    """The editable fields of an AI destination, as text."""
    form = {
        "original": destination.name,
        "name": destination.name,
        "url": destination.url,
        "reasoning": "on" if destination.reasoning == "on" else "off",
    }
    form.update({task: destination.model(task) or "" for task in AI_TASK_IDS})
    return form


def llm_from_forms(
    llm: Any, forms: list[dict[str, str]], active: int, fallback: int | None, *, enabled: bool
) -> Any:
    """Builds the AI configuration from what was entered; `ValueError` if something does not add up.

    `active` and `fallback` are positions in `forms`: that way a name change does not lose them.
    It keeps what the interface does not edit (token, context size) from the original destination,
    even if it is renamed.
    """
    from ..core.config import NO_FALLBACK, UNSET, LlmDestination
    from ..llm.destinations import validate_model, validate_url

    if not forms:
        raise ValueError(t("ui.aiform.at_least_one"))
    previous = {d.name: d for d in llm.destinations}
    destinations: list[LlmDestination] = []
    for number, form in enumerate(forms, 1):
        name = form["name"].strip()
        if not name:
            raise ValueError(t("ui.aiform.name_required", number=number))
        if any(d.name == name for d in destinations):
            raise ValueError(t("ui.aiform.duplicate", name=name))
        url = form["url"].strip()
        try:
            validate_url(url, llm.allowed_hosts)
            models = {task: form[task].strip() for task in AI_TASK_IDS}
            for model in models.values():
                if model:
                    validate_model(model)
        except ValueError as exc:
            raise ValueError(f"{name}: {exc}") from exc
        base = previous.get(form.get("original", "")) or LlmDestination(name=name, url=url)
        destinations.append(
            replace(
                base,
                name=name,
                url=url,
                reasoning="on" if form.get("reasoning") == "on" else "off",
                **{f"model_{task}": value or UNSET for task, value in models.items()},
            )
        )
    chosen = destinations[active] if 0 <= active < len(destinations) else destinations[0]
    backup = NO_FALLBACK
    if fallback is not None and 0 <= fallback < len(destinations):
        backup = destinations[fallback].name
    return replace(
        llm,
        enabled=enabled,
        destinations=tuple(destinations),
        active_destination=chosen.name,
        fallback_destination=NO_FALLBACK if backup == chosen.name else backup,
    )


def destination_label(destination: Any) -> str:
    """«oficina · qwen2.5-coder:14b, qwen3:14b»: name and models, to choose one."""
    models: list[str] = []
    for task in AI_TASK_IDS:
        model = destination.model(task)
        if model and model not in models:
            models.append(model)
    return f"{destination.name} · {', '.join(models) or t('ui.aiedit.models_none')}"


def nav_context(project: str | None, panel_title: str | None) -> str:
    """What the navigation bar says on the left: the open section or the project."""
    return panel_title or project or "Heimdall Guardian"


def subproject_rows(subs: list[SubProject]) -> list[dict[str, str]]:
    """One row per separate project found inside the folder."""
    return [
        {"path": sub.path, "name": sub.path, "stacks": ", ".join(sub.stacks) or "\u2014"}
        for sub in subs
    ]


def suggestion_defaults(suggestions: list[Suggestion], profile: str) -> dict[str, bool]:
    """Which suggested folders start checked.

    Editor, assistant and `.gitignore` folders stay unchecked for vendor code, where they can
    hide code.
    """
    risky = {"tool", "gitignore"}
    return {s.pattern: not (s.source in risky and profile == "vendor") for s in suggestions}


def kept_folder_entries(saved: list[str], unchecked: list[str]) -> list[str]:
    """Saved folder entries that survive a save of the "Folders to skip" dialog.

    The dialog only shows two levels of folders, so a saved pattern such as `.next` may
    match nothing on screen; it is kept unless the user unticked a folder it skips.
    """
    return [
        entry
        for entry in saved
        if not is_file_pattern(entry)
        and not any(Exclusions(dirs=(entry,)).excludes_dir(folder) for folder in unchecked)
    ]


MAX_RULE_LINES = 8


def user_rules_summary(user: UserRules, engine_failures: dict[Path, str] | None) -> list[str]:
    """Lines that say how the user's rule folders checked out (problems capped)."""
    failures = engine_failures or {}
    if not user.files and not user.problems and not failures:
        return [t("ui.settings.user_rules_none")]
    ready = [path for path in user.files if path not in failures]
    count = sum(len(rule_ids_of(path)) for path in ready) if failures else len(user.ids)
    lines = [tn("ui.settings.user_rules_ok", count, files=len(ready))]
    details = [
        t("ui.settings.user_rules_problem", file=problem.file, detail=render(problem.message))
        for problem in user.problems
    ]
    details += [
        t("ui.settings.user_rules_problem", file=str(path), detail=detail)
        for path, detail in failures.items()
    ]
    lines += details[:MAX_RULE_LINES]
    if len(details) > MAX_RULE_LINES:
        lines.append(tn("ui.settings.user_rules_more", len(details) - MAX_RULE_LINES))
    return lines


# --------------------------------------------------- the `hdl` command (Settings, first offer)


@dataclass(frozen=True)
class CliSection:
    """What the "Command line" part of Settings says and offers.

    `action` is `install`, `uninstall`, `download_python` or `none` (this copy of the app
    has no installer to run).
    """

    lines: list[str]
    action: str
    button: str


def cli_section(
    status: cli_setup.CliStatus,
    python: cli_setup.PythonInfo | None,
    files: cli_setup.CliFiles | None,
) -> CliSection:
    """The status line, notes and the one button of the Settings section."""
    minimum = ".".join(str(n) for n in cli_setup.MINIMUM_PYTHON)
    if status.installed:
        where = status.link or status.command
        lines = [t("ui.cli.installed", path=where)]
        if status.version:
            lines.append(t("ui.cli.installed_version", version=status.version))
        lines.append(t("ui.cli.note"))
        action = "uninstall" if files is not None else "none"
        return CliSection(lines, action, t("ui.cli.uninstall") if files is not None else "")
    lines = [t("ui.cli.not_installed")]
    if files is None:
        return CliSection([*lines, t("ui.cli.unavailable")], "none", "")
    if python is None:
        lines.append(t("ui.cli.no_python", minimum=minimum))
        return CliSection(lines, "download_python", t("ui.cli.download_python"))
    lines += [t("ui.cli.note"), t("ui.cli.needs_internet")]
    return CliSection(lines, "install", t("ui.cli.install"))


def cli_running_text(action: str) -> str:
    """What is said while the installer works."""
    return t("ui.cli.running_uninstall" if action == "uninstall" else "ui.cli.running_install")


def cli_result(
    action: str, result: cli_setup.RunResult, status: cli_setup.CliStatus
) -> tuple[str, list[str], bool]:
    """Title, body lines and success flag of the dialog shown when the installer ends."""
    done = result.returncode == 0
    if action == "uninstall":
        if done and not status.installed:
            return t("ui.cli.result.uninstalled_title"), [t("ui.cli.result.uninstalled")], True
        return t("ui.cli.result.uninstall_failed"), _failure_lines(result), False
    if done and status.installed:
        where = status.link or status.command
        body = [t("ui.cli.result.installed", path=where)]
        advice = cli_setup.path_advice(result.output)
        body += advice if advice else [t("ui.cli.result.reopen")]
        return t("ui.cli.result.installed_title"), body, True
    return t("ui.cli.result.install_failed"), _failure_lines(result), False


def _failure_lines(result: cli_setup.RunResult) -> list[str]:
    tail = cli_setup.output_tail(result.output)
    return [t("ui.cli.result.last_lines"), *tail] if tail else [t("ui.cli.result.no_output")]


def cli_offer(python: cli_setup.PythonInfo | None) -> tuple[str, list[str], str, str]:
    """Title, body, the main action (`install` or `download_python`) and its button."""
    body = [t("ui.cli.offer.body")]
    if python is None:
        minimum = ".".join(str(n) for n in cli_setup.MINIMUM_PYTHON)
        body.append(t("ui.cli.no_python", minimum=minimum))
        action, button = "download_python", t("ui.cli.download_python")
    else:
        action, button = "install", t("ui.cli.offer.install")
    body.append(t("ui.cli.offer.later_note"))
    return t("ui.cli.offer.title"), body, action, button
