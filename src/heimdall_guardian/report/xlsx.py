"""Excel: one row per finding, with columns for follow-up."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from ..core import owasp as owasp_top10
from ..core.palette import NIGHT, SEVERITY_COLORS
from ..i18n import is_message, render, t, text_of
from ..i18n import label as code_label
from . import text
from .html import OPEN_STATUSES, coverage_colors
from .plan import fix_plan, plan_line

# (header key in the catalog, finding field, column width)
_COLUMNS: list[tuple[str, str | None, int]] = [
    ("report.xlsx.id", "id", 18),
    ("report.xlsx.severity", "severity", 11),
    ("report.xlsx.baseline_status", "baseline_status", 17),
    ("report.xlsx.category", "category", 17),
    ("report.xlsx.title", "title", 46),
    ("report.xlsx.file", "file", 38),
    ("report.xlsx.line", "line_start", 8),
    ("report.xlsx.description", "description", 60),
    ("report.xlsx.recommendation", "recommendation", 60),
    ("report.xlsx.rule", "rule_id", 20),
    ("report.xlsx.cwe", "cwe", 11),
    ("report.xlsx.owasp", "owasp", 30),
    ("report.xlsx.origin", "origin", 15),
    ("report.xlsx.detected_by", "detected_by", 18),
    # Blank columns so that management can assign and follow up.
    ("report.xlsx.owner", None, 22),
    ("report.xlsx.due_date", None, 17),
    ("report.xlsx.handling_status", None, 19),
    ("report.xlsx.notes", None, 40),
]
_SEVERITY_FILL = {name: c[0].lstrip("#") for name, c in SEVERITY_COLORS.items()}
_SEVERITY_FONT = {name: c[1].lstrip("#") for name, c in SEVERITY_COLORS.items()}
_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def safe_cell(value: Any) -> Any:
    """Neutralizes formula injection: the text comes from third-party code."""
    if isinstance(value, list):
        value = ", ".join(str(item) for item in value)
    if isinstance(value, str) and value.startswith(_FORMULA_PREFIXES):
        return "'" + value
    return value


def _endpoint_cell(value: Any) -> Any:
    if isinstance(value, bool) or value is None:
        return text.yes_no(value)
    return safe_cell(render(value) if is_message(value) else value)


def _top10_sheet(workbook: Workbook, payload: dict[str, Any]) -> None:
    sheet = workbook.create_sheet(t("report.xlsx.sheet.owasp"))
    open_findings = [f for f in payload["findings"] if f["baseline_status"] in OPEN_STATUSES]
    columns = [(t("report.xlsx.owasp.category"), "label", 40),
               (t("report.xlsx.owasp.name"), "name", 34),
               (t("report.coverage.meaning"), "explanation", 60),
               (t("report.coverage.example"), "example", 60),
               (t("report.coverage.coverage"), "coverage_text", 14),
               (t("report.xlsx.owasp.covers"), "coverage_note", 60),
               (t("report.coverage.open"), "count", 12)]  # fmt: skip
    sheet.append([title for title, _, _ in columns])
    for cell in sheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor=NIGHT.lstrip("#"))
        cell.alignment = Alignment(vertical="center", wrap_text=True)
    fills = {level: c[2].lstrip("#") for level, c in coverage_colors().items()}
    for row in owasp_top10.coverage_rows(open_findings):
        sheet.append([safe_cell(row[key]) for _, key, _ in columns])
        for cell in sheet[sheet.max_row]:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
        sheet[sheet.max_row][4].fill = PatternFill("solid", fgColor=fills[row["coverage"]])
    for index, (_, _, width) in enumerate(columns, start=1):
        sheet.column_dimensions[get_column_letter(index)].width = width
    sheet.append([])
    sheet.append([safe_cell(owasp_top10.scope_warning())])
    sheet.freeze_panes = "A2"


_TEXTS = ("title", "description", "recommendation")
_LABELLED = {
    "severity": ("severity", "default"),
    "baseline_status": ("status", "snake"),
    "category": ("category", "snake"),
    "origin": ("origin", "default"),
}


def _cell(finding: dict[str, Any], key: str | None) -> Any:
    if not key:
        return None
    value = text_of(finding, key) if key in _TEXTS else finding.get(key)
    if key in _LABELLED and value is not None:
        kind, variant = _LABELLED[key]
        return safe_cell(code_label(value, kind, variant=variant))
    return safe_cell(value)


def _omitted_sheet(workbook: Workbook, payload: dict[str, Any]) -> None:
    """Folders and files left out of the run; no sheet when nothing was omitted."""
    if not text.has_omitted(payload):
        return
    omitted = workbook.create_sheet(t("report.omitted.sheet"))
    omitted.append([t("report.omitted.type"), t("report.omitted.path")])
    for cell in omitted[1]:
        cell.font = Font(bold=True)
    data = payload.get("omitted") or {}
    for kind, key in (("folder", "folders"), ("file", "files")):
        for entry in data.get(key) or []:
            omitted.append([safe_cell(t(f"report.omitted.type.{kind}")), safe_cell(str(entry))])
    omitted.column_dimensions["A"].width = 14
    omitted.column_dimensions["B"].width = 80


def _plan_sheet(workbook: Workbook, payload: dict[str, Any]) -> None:
    """Where to start; no sheet when there is nothing open to fix."""
    groups = fix_plan(payload)
    if not groups:
        return
    sheet = workbook.create_sheet(t("report.plan.title"))
    sheet.append(
        [
            t("report.plan.col.number"),
            t("report.xlsx.severity"),
            t("report.plan.col.action"),
            t("report.plan.col.findings"),
            t("report.plan.col.files"),
            t("report.plan.col.ids"),
        ]
    )
    for cell in sheet[1]:
        cell.font = Font(bold=True)
    for index, group in enumerate(groups, start=1):
        sheet.append(
            [
                index,
                safe_cell(code_label(group.severity, "severity")),
                safe_cell(plan_line(group)),
                group.count,
                group.files,
                safe_cell(", ".join(group.ids)),
            ]
        )
        for cell in sheet[sheet.max_row]:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    for index, width in enumerate((5, 12, 80, 10, 8, 50), start=1):
        sheet.column_dimensions[get_column_letter(index)].width = width
    sheet.freeze_panes = "A2"


def write_xlsx(payload: dict[str, Any], path: Path) -> None:
    payload = owasp_top10.migrate_payload(payload)
    workbook = Workbook()
    sheet = workbook.active
    assert sheet is not None  # noqa: S101 - a new workbook always has a sheet
    sheet.title = t("report.xlsx.sheet.findings")
    sheet.append([t(key) for key, _, _ in _COLUMNS])
    for cell in sheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor=NIGHT.lstrip("#"))
        cell.alignment = Alignment(vertical="center", wrap_text=True)

    wrap = Alignment(vertical="top", wrap_text=True)
    for finding in [*payload["findings"], *payload.get("fixed", [])]:
        sheet.append([_cell(finding, key) for _, key, _ in _COLUMNS])
        row = sheet[sheet.max_row]
        for cell in row:
            cell.alignment = wrap
        color = _SEVERITY_FILL.get(finding["severity"])
        if color:
            row[1].fill = PatternFill("solid", fgColor=color)
            row[1].font = Font(bold=True, color=_SEVERITY_FONT[finding["severity"]])

    for index, (_, _, width) in enumerate(_COLUMNS, start=1):
        sheet.column_dimensions[get_column_letter(index)].width = width
    sheet.freeze_panes = "B2"
    sheet.auto_filter.ref = sheet.dimensions

    summary = workbook.create_sheet(t("report.xlsx.sheet.summary"))
    project, run = payload["project"], payload["run"]
    rows: list[tuple[str, Any]] = [
        (t("report.xlsx.summary.project"), project["name"]),
        (t("report.html.date"), run["started"]),
        (t("report.profile"), text.profile_name(run["profile"])),
        (t("report.xlsx.summary.hash"), project["tree_hash"]),
        (t("report.version"), payload["heimdall_version"]),
        ("", ""),
        (t("report.xlsx.summary.by_severity"), ""),
        *[(code_label(k, "severity"), v) for k, v in payload["summary"]["by_severity"].items()],
        ("", ""),
        (t("report.xlsx.summary.by_status"), ""),
        *[
            (code_label(k, "status", variant="snake"), v)
            for k, v in payload["summary"]["by_status"].items()
        ],
        ("", ""),
        (t("report.xlsx.summary.limitations"), ""),
        *[("", render(item)) for item in payload["limitations"]],
    ]
    for name, value in rows:
        summary.append([safe_cell(name), safe_cell(value)])
    for cell in summary["A"]:
        cell.font = Font(bold=True)
    summary.column_dimensions["A"].width = 34
    summary.column_dimensions["B"].width = 80
    _plan_sheet(workbook, payload)
    _top10_sheet(workbook, payload)
    endpoints = payload.get("endpoints") or []
    if endpoints:
        inventory = workbook.create_sheet(t("report.xlsx.sheet.endpoints"))
        columns = [(t("report.pdf.methods"), "methods"), (t("report.endpoints.route"), "path"),
                   (t("report.endpoints.handler"), "handler"),
                   (t("report.xlsx.file"), "file"), (t("report.xlsx.line"), "line"),
                   (t("report.xlsx.endpoints.requires_auth"), "requires_auth"),
                   (t("report.xlsx.endpoints.has_auth"), "has_auth"),
                   (t("report.pdf.write"), "writes"),
                   (t("report.xlsx.endpoints.evidence"), "evidence")]  # fmt: skip
        inventory.append([title for title, _ in columns])
        for cell in inventory[1]:
            cell.font = Font(bold=True)
        for endpoint in endpoints:
            inventory.append([_endpoint_cell(endpoint[key]) for _, key in columns])
        for index, width in enumerate((16, 40, 30, 40, 8, 22, 20, 11, 60), start=1):
            inventory.column_dimensions[get_column_letter(index)].width = width
        inventory.freeze_panes = "A2"
    _omitted_sheet(workbook, payload)
    workbook.save(path)
