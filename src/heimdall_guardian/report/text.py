"""Texts shared by the reports (HTML, PDF and Excel), requested in the current language.

Nothing here is computed on import: each function queries the catalog when called, so the
same run dictionary comes out in Spanish or English depending on `set_language`.
"""

from __future__ import annotations

from typing import Any

from ..core.profiles import profile_name as profile_name
from ..i18n import get_language, has_message, t, tn

# How a tool's statuses are stored → key of its label.
_TOOL_STATUS = {"ran": "ran", "skipped": "skipped", "error": "error"}
# The tools that query a vulnerability database.
TOOLS_WITH_DATABASE = ("trivy", "osv", "vendored")


def disclaimer() -> str:
    return t("report.disclaimer")


def tagline() -> str:
    return t("ui.brand.tagline")


def tool_status(status: str) -> str:
    slug = _TOOL_STATUS.get(status)
    return t(f"report.tool_status.{slug}") if slug else status


def database_label(tool: dict[str, Any]) -> str:
    """Date of a tool's vulnerability database, or why there is none."""
    if tool.get("db_updated_at"):
        return str(tool["db_updated_at"])[:10]
    return t("report.db.none" if tool["name"] in TOOLS_WITH_DATABASE else "report.db.unused")


def yes_no(value: bool | None) -> str:
    if value is None:
        return t("report.undetermined")
    return t("report.yes" if value else "report.no")


def methods_label(methods: list[str]) -> str:
    return t("report.any_method") if methods == ["*"] else ", ".join(methods)


def _level(prefix: str, raw: object) -> str:
    key = f"{prefix}.{raw}"
    return t(key) if has_message(key) else str(raw)


def ai_verdict(raw: object) -> str:
    """«likely_real» → «probable real» / «probably real»."""
    key = f"report.ai.verdict.{raw}"
    return t(key) if has_message(key) else str(raw).replace("_", " ")


def ai_level(raw: object) -> str:
    return _level("report.ai.level", raw)


def ai_reachable(raw: object) -> str:
    return _level("report.ai.reachable", raw)


def risk_level(raw: object) -> str:
    return _level("report.ai.risk_level", raw)


def html_lang() -> str:
    return t("report.html.lang")


def is_english() -> bool:
    return get_language() == "en"


def omitted_counts(payload: dict[str, Any]) -> tuple[int, int, int]:
    """Folders, files and earlier findings left out of a run (older payloads have none)."""
    omitted = payload.get("omitted") or {}
    return (
        len(omitted.get("folders") or []),
        len(omitted.get("files") or []),
        int(omitted.get("findings") or 0),
    )


def omitted_parts(payload: dict[str, Any]) -> str:
    """ "2 folders and 3 files": only the non-zero parts; empty when nothing was left out."""
    folders, files, _ = omitted_counts(payload)
    parts = []
    if folders:
        parts.append(tn("report.omitted.folders", folders))
    if files:
        parts.append(tn("report.omitted.files", files))
    if len(parts) == 2:
        return t("report.omitted.and", first=parts[0], second=parts[1])
    return parts[0] if parts else ""


def omitted_sentence(payload: dict[str, Any]) -> str:
    parts = omitted_parts(payload)
    return t("report.omitted.left_out", parts=parts) if parts else ""


def omitted_findings_sentence(payload: dict[str, Any]) -> str:
    count = omitted_counts(payload)[2]
    return tn("report.omitted.findings", count) if count else ""


def omitted_entries(payload: dict[str, Any], cap: int | None = None) -> tuple[list[str], int]:
    """Paths to list (folders with a trailing slash, then files) and how many were cut."""
    omitted = payload.get("omitted") or {}
    entries = [f"{folder.rstrip('/')}/" for folder in omitted.get("folders") or []]
    entries += list(omitted.get("files") or [])
    if cap is None or len(entries) <= cap:
        return entries, 0
    return entries[:cap], len(entries) - cap


def has_omitted(payload: dict[str, Any]) -> bool:
    return any(omitted_counts(payload))
