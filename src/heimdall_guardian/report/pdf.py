"""PDF for a case file or official letter: verdict, summary and findings, printable."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fpdf import FPDF
from fpdf.enums import XPos, YPos
from fpdf.fonts import FontFace

from ..core import owasp as owasp_top10
from ..core import palette
from ..core.finding import Category, Origin, Severity
from ..core.palette import SEVERITY_COLORS, rgb
from ..i18n import label, render, t, text_of, tn
from . import text
from .html import OPEN_STATUSES, SEVERITIES, coverage_colors
from .plan import fix_plan, ids_text, plan_line

NIGHT = rgb(palette.NIGHT)
SAND = rgb(palette.SAND)
LINE = rgb(palette.LINE)
BRONZE = rgb(palette.BRONZE)
GRIS = rgb(palette.GRAY_DARK)
PAPER = rgb(palette.PAPER)
NEGRO = (30, 30, 30)
WHITE = (255, 255, 255)
GOLD = rgb(palette.GOLD)
_SEVERITY = {
    name: (rgb(solid), rgb(on_solid)) for name, (solid, on_solid, _, _) in SEVERITY_COLORS.items()
}
_OUTCOME = {
    "not_approved": _SEVERITY[Severity.CRITICAL],
    "approved_with_observations": _SEVERITY[Severity.MEDIUM],
    "approved": (rgb(palette.GOOD[0]), rgb(palette.GOOD[1])),
}
_REPLACEMENTS = {
    "—": "-",
    "–": "-",
    "…": "...",
    "“": '"',
    "”": '"',
    "‘": "'",
    "’": "'",
    "→": "->",
    "≤": "<=",
    "≥": ">=",
    "•": "-",
    "\t": "    ",
}
MAX_FINDINGS = 300


def clean(value: Any) -> str:
    """Text that the PDF base fonts can draw (Latin-1).

    Anything that does not exist in Latin-1 (e.g. characters from other alphabets inside
    a code snippet) is replaced with `?`.
    """
    text = "" if value is None else str(value)
    for original, replacement in _REPLACEMENTS.items():
        text = text.replace(original, replacement)
    return text.encode("latin-1", errors="replace").decode("latin-1")


class _Document(FPDF):
    def __init__(self, project: str) -> None:
        super().__init__(format="Letter", unit="mm")
        self.project = project
        self.set_margins(18, 18, 18)
        self.set_auto_page_break(auto=True, margin=18)
        self.set_title(clean(t("report.pdf.title", project=project)))
        self.set_author("Heimdall Guardian")

    def header(self) -> None:
        self._watermark()
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*GRIS)
        title = clean(t("report.pdf.running_header", project=self.project))
        self.cell(0, 5, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)

    def _watermark(self) -> None:
        """The seal, very faint, at the back of each page."""
        seal = palette.ASSETS / "sello.png"
        if not seal.is_file():
            return
        width = 150.0
        with self.local_context(fill_opacity=0.05, stroke_opacity=0.05):
            self.image(
                str(seal), x=(self.w - width) / 2, y=(self.h - width * 480 / 406) / 2, w=width
            )

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*GRIS)
        # fpdf replaces `{nb}` with the total page count when the document is closed.
        self.cell(0, 5, clean(t("report.pdf.page", page=self.page_no(), total="{nb}")), align="R")

    # ------------------------------------------------------------- piezas

    def heading(self, text: str) -> None:
        if self.get_y() > self.h - 50:
            self.add_page()
        self.ln(4)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*NIGHT)
        self.cell(0, 8, clean(text), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*GOLD)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

    def paragraph(
        self, text: str, size: float = 10, color: tuple[int, int, int] = NEGRO, style: str = ""
    ) -> None:
        self.set_font("Helvetica", style, size)
        self.set_text_color(*color)
        self.multi_cell(0, size * 0.48, clean(text), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

    def pairs(self, rows: list[tuple[str, Any]]) -> None:
        for name, value in rows:
            self.set_font("Helvetica", "B", 9)
            self.set_text_color(*GRIS)
            self.cell(52, 5.5, clean(name))
            self.set_font("Helvetica", "", 9)
            self.set_text_color(*NEGRO)
            self.multi_cell(0, 5.5, clean(value), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def grid(self, headers: list[str], rows: list[list[Any]], widths: tuple[float, ...]) -> None:
        self.set_font("Helvetica", "", 8.5)
        self.set_text_color(*NEGRO)
        self.set_draw_color(*LINE)
        with self.table(
            col_widths=widths,
            line_height=4.6,
            padding=1.4,
            headings_style=_headings(),
            # Without this the rows inherit the last fill color used.
            cell_fill_color=WHITE,
            cell_fill_mode="ALL",
        ) as table:
            head = table.row()
            for title in headers:
                head.cell(clean(title))
            for values in rows:
                row = table.row()
                for value in values:
                    row.cell(clean(value))
        self.ln(2)


def _headings() -> Any:
    return FontFace(emphasis="BOLD", color=WHITE, fill_color=NIGHT)


def _location(finding: dict[str, Any]) -> str:
    line = f":{finding['line_start']}" if finding["line_start"] else ""
    return f"{finding['file']}{line}"


def _cover(pdf: _Document, payload: dict[str, Any]) -> None:
    project, run = payload["project"], payload["run"]
    pdf.add_page()
    pdf.set_fill_color(*NIGHT)
    pdf.rect(0, 0, pdf.w, 62, style="F")
    pdf.set_fill_color(*GOLD)
    pdf.rect(0, 62, pdf.w, 1.2, style="F")

    # On the right, the brand: color emblem and, beside it, the name in letters.
    brand_width = 0.0
    emblem, wordmark = palette.ASSETS / "emblema.png", palette.ASSETS / "letras.png"
    if emblem.is_file() and wordmark.is_file():
        emblem_height, wordmark_width = 36.0, 58.0
        emblem_width = emblem_height * 420 / 367  # aspect ratio of emblema.png
        brand_width = emblem_width + 3 + wordmark_width
        left = pdf.w - pdf.r_margin - brand_width
        pdf.image(str(emblem), x=left, y=11, h=emblem_height)
        pdf.image(str(wordmark), x=left + emblem_width + 3, y=18, w=wordmark_width)
        pdf.set_xy(left + emblem_width + 3, 39)
        pdf.set_text_color(*SAND)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.cell(wordmark_width, 4, clean(text.tagline()), align="C")

    # On the left, what was analyzed.
    pdf.set_xy(pdf.l_margin, 17)
    pdf.set_text_color(*SAND)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, clean(t("report.pdf.analyzed_project")), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", 24)
    pdf.multi_cell(
        pdf.w - pdf.l_margin - pdf.r_margin - brand_width - 8,
        11,
        clean(project["name"]),
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.set_y(72)
    baseline = payload.get("baseline") or {}
    pdf.pairs(
        [
            (t("report.pdf.analysis_date"), run["started"][:16].replace("T", " ")),
            (
                t("report.profile"),
                f"{text.profile_name(run['profile'])} ({', '.join(run['modules'])})",
            ),
            (t("report.run"), baseline.get("run") or t("report.no_baseline")),
            (t("report.files"), project["files_analyzed"]),
            (t("report.pdf.hash"), project["tree_hash"]),
            (t("report.rules_version"), run.get("rules_version") or "-"),
            (t("report.version"), payload["heimdall_version"]),
        ]
    )


def _verdict(pdf: _Document, verdict: dict[str, Any]) -> None:
    pdf.heading(t("report.verdict.title"))
    fill, ink = _OUTCOME.get(verdict["outcome"], (NIGHT, WHITE))
    pdf.set_fill_color(*fill)
    pdf.set_text_color(*ink)
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(
        0,
        16,
        clean(label(verdict["outcome"], "outcome")),
        align="C",
        fill=True,
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.ln(4)
    pdf.grid(
        [
            t("report.verdict.criterion"),
            t("report.verdict.found"),
            t("report.verdict.maximum"),
            t("report.verdict.result"),
        ],
        [
            [
                render(c["criterion"]),
                c["found"],
                c["limit"],
                t("report.pdf.exceeded_blocking" if c["blocking"] else "report.verdict.exceeded")
                if c["exceeded"]
                else t("report.verdict.within"),
            ]
            for c in verdict["criteria"]
        ],
        (92, 26, 22, 40),
    )
    if verdict["medium_open"]:
        pdf.paragraph(tn("report.pdf.mediums", verdict["medium_open"]), 9)
    if not verdict["default_thresholds"]:
        pdf.paragraph(t("report.pdf.custom_thresholds"), 9, GRIS)
    if verdict["accepted_findings"]:
        pdf.paragraph(t("report.pdf.accepted_intro"), 9, GRIS)
        pdf.grid(
            [
                "ID",
                t("report.dependencies.severity"),
                t("report.annex.status"),
                t("report.fixed.finding"),
            ],
            [
                [
                    a["id"],
                    label(a["severity"], "severity"),
                    label(a["status"], "status"),
                    text_of({"title": a["title"], "texts": a.get("texts")}, "title"),
                ]
                for a in verdict["accepted_findings"]
            ],
            (34, 22, 32, 92),
        )
    pdf.ln(2)
    pdf.pairs(
        [
            (t("report.pdf.issuer"), verdict["issuer"]),
            (t("report.html.date"), verdict["issued"][:16].replace("T", " ")),
            (t("report.pdf.analyzed_code"), verdict["tree_hash"]),
            (t("report.rules_version"), verdict["rules_version"]),
            (t("report.verdict.signature"), verdict["signature"]),
        ]
    )
    pdf.ln(10)
    pdf.set_draw_color(*GRIS)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + 80, pdf.get_y())
    pdf.paragraph(t("report.pdf.sign_here"), 8, GRIS)


def _summary(pdf: _Document, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    pdf.heading(t("report.pdf.summary"))
    pdf.grid(
        [label(s, "severity") for s in SEVERITIES],
        [[summary["by_severity"].get(s, 0) for s in SEVERITIES]],
        (36, 36, 36, 36, 36),
    )
    pdf.paragraph(t("report.pdf.by_severity"), 8.5, GRIS)
    baseline = payload.get("baseline") or {}
    if baseline.get("previous_run"):
        states = summary["by_status"]
        pdf.paragraph(
            t(
                "report.pdf.compared",
                previous=baseline["previous_run"],
                new=states.get("new", 0),
                persistent=states.get("persistent", 0),
                fixed=states.get("fixed", 0),
                accepted=states.get("accepted", 0),
                false_positive=states.get("false_positive", 0),
            )
        )
    if payload.get("ai_summary"):
        pdf.paragraph(t("report.pdf.ai_summary_intro"), 8.5, GRIS)
        pdf.paragraph(payload["ai_summary"]["text"], 10)


def _plan(pdf: _Document, payload: dict[str, Any]) -> None:
    """Where to start: the grouped fix plan, up to ten lines."""
    groups = fix_plan(payload)
    if not groups:
        return
    pdf.heading(t("report.plan.title"))
    pdf.paragraph(t("report.plan.help"), 8.5, GRIS)
    for index, group in enumerate(groups, start=1):
        sev = label(group.severity, "severity")
        pdf.paragraph(f"{index}. [{sev}] {plan_line(group)}", 9.5)
        pdf.paragraph(ids_text(group), 8, GRIS)


def _what_we_review(pdf: _Document, payload: dict[str, Any]) -> None:
    """For non-technical readers: what OWASP is and how much of each category is covered."""
    open_findings = [f for f in payload["findings"] if f["baseline_status"] in OPEN_STATUSES]
    pdf.heading(t("report.coverage.title"))
    pdf.paragraph(owasp_top10.what_is_owasp())
    pdf.ln(1)
    colors = {
        level: (rgb(solid), rgb(ink)) for level, (_, _, solid, ink) in coverage_colors().items()
    }
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*NEGRO)
    pdf.set_draw_color(*LINE)
    with pdf.table(
        col_widths=(36, 44, 40, 42, 16),
        text_align="LEFT",
        line_height=4.2,
        padding=1.3,
        headings_style=_headings(),
        cell_fill_color=WHITE,
        cell_fill_mode="ALL",
    ) as table:
        head = table.row()
        for title in (
            t("report.coverage.category"),
            t("report.coverage.meaning"),
            t("report.pdf.example"),
            t("report.pdf.coverage"),
            t("report.pdf.open"),
        ):
            head.cell(clean(title))
        for row in owasp_top10.coverage_rows(open_findings):
            fill, ink = colors[row["coverage"]]
            cells = table.row()
            cells.cell(clean(f"{row['code']} {row['name']}"))
            cells.cell(clean(row["explanation"]))
            cells.cell(clean(row["example"]))
            cells.cell(
                clean(f"{row['coverage_text']}. {row['coverage_note']}"),
                style=FontFace(color=ink, fill_color=fill),
            )
            cells.cell(str(row["count"]), align="C")
    if text.has_omitted(payload):
        pdf.paragraph(f"{t('report.omitted.title')}:", 9, GRIS, "B")
        if text.omitted_sentence(payload):
            pdf.paragraph(text.omitted_sentence(payload), 9)
        entries, more = text.omitted_entries(payload, 60)
        for entry in entries:
            pdf.paragraph(f"- {entry}", 9)
        if more:
            pdf.paragraph(f"- {t('report.omitted.more', count=more)}", 9)
        if text.omitted_findings_sentence(payload):
            pdf.paragraph(text.omitted_findings_sentence(payload), 9)
    pdf.ln(2)
    pdf.paragraph(f"{t('report.scope')} {owasp_top10.scope_warning()}", 9, NIGHT, "B")


def _findings(pdf: _Document, payload: dict[str, Any]) -> None:
    code = [f for f in payload["findings"] if f["category"] != Category.DEPENDENCIES]
    pdf.heading(t("report.pdf.code_findings", count=len(code)))
    if not code:
        pdf.paragraph(t("report.findings.none"), 10, GRIS)
    for finding in code[:MAX_FINDINGS]:
        if pdf.get_y() > pdf.h - 45:
            pdf.add_page()
        fill, ink = _SEVERITY.get(finding["severity"], (PAPER, NEGRO))
        pdf.set_fill_color(*fill)
        pdf.set_text_color(*ink)
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(20, 5.5, clean(label(finding["severity"], "severity")), align="C", fill=True)
        pdf.set_text_color(*GRIS)
        pdf.set_font("Helvetica", "", 8)
        state = label(finding["baseline_status"], "status")
        origin = t("report.pdf.ai_suggestion") if finding["origin"] == Origin.AI else ""
        pdf.cell(
            0,
            5.5,
            clean(f"  {finding['id']} - {state}{origin}"),
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        pdf.paragraph(text_of(finding, "title"), 10.5, NIGHT, "B")
        pdf.paragraph(_location(finding), 8.5, GRIS)
        if finding["snippet"]:
            pdf.set_font("Courier", "", 8)
            pdf.set_text_color(*NEGRO)
            pdf.set_fill_color(*PAPER)
            snippet = "\n".join(finding["snippet"].splitlines()[:8])
            pdf.multi_cell(0, 3.8, clean(snippet), fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(1)
        if description := text_of(finding, "description"):
            pdf.paragraph(description, 9)
        pdf.paragraph(f"{t('report.finding.fix')}: {text_of(finding, 'recommendation')}", 9)
        if reach := (finding.get("llm_assessment") or {}).get("reachable"):
            assessment = finding["llm_assessment"]
            line = f"{t('report.ai.reachable')}: {text.ai_reachable(reach)}"
            if assessment.get("source"):
                line += f" - {t('report.ai.source')}: {assessment['source']}"
            pdf.paragraph(line, 9)
        pdf.ln(2)
    if len(code) > MAX_FINDINGS:
        pdf.paragraph(t("report.pdf.truncated", max=MAX_FINDINGS), 9, GRIS)


def _tables(pdf: _Document, payload: dict[str, Any]) -> None:
    dependencies = [f for f in payload["findings"] if f["category"] == Category.DEPENDENCIES]
    if dependencies:
        pdf.heading(t("report.pdf.dependencies", count=len(dependencies)))
        pdf.grid(
            [
                t("report.dependencies.severity"),
                t("report.dependencies.package"),
                t("report.dependencies.vulnerability"),
                t("report.pdf.fixed_version"),
                t("report.annex.status"),
            ],
            [
                [
                    label(f["severity"], "severity"),
                    f["snippet"],
                    f["rule_id"],
                    f.get("fixed_version") or t("report.pdf.no_patch"),
                    label(f["baseline_status"], "status"),
                ]
                for f in dependencies
            ],
            (22, 50, 38, 44, 26),
        )
    open_endpoints = [e for e in payload.get("endpoints") or [] if e["has_auth"] is False]
    if payload.get("endpoints"):
        total = len(payload["endpoints"])
        pdf.heading(t("report.pdf.endpoints", open=len(open_endpoints), total=total))
        if open_endpoints:
            pdf.grid(
                [
                    t("report.pdf.methods"),
                    t("report.endpoints.route"),
                    t("report.endpoints.handler"),
                    t("report.pdf.write"),
                ],
                [
                    [
                        text.methods_label(e["methods"]),
                        e["path"],
                        f"{e['handler']} ({e['file']}:{e['line']})",
                        text.yes_no(bool(e["writes"])),
                    ]
                    for e in open_endpoints
                ],
                (28, 58, 76, 18),
            )
        else:
            pdf.paragraph(t("report.pdf.all_authenticated"), 10, GRIS)
    if payload.get("fixed"):
        pdf.heading(t("report.pdf.fixed", count=len(payload["fixed"])))
        pdf.grid(
            [
                "ID",
                t("report.dependencies.severity"),
                t("report.fixed.finding"),
                t("report.fixed.previous_location"),
            ],
            [
                [f["id"], label(f["severity"], "severity"), text_of(f, "title"), _location(f)]
                for f in payload["fixed"]
            ],
            (34, 22, 70, 54),
        )


def _annex(pdf: _Document, payload: dict[str, Any]) -> None:
    pdf.heading(t("report.annex.title"))
    pdf.grid(
        [
            t("report.annex.tool"),
            t("report.annex.version"),
            t("report.annex.status"),
            t("report.annex.findings"),
            t("report.annex.database"),
        ],
        [
            [
                tool["name"],
                tool["version"] or "-",
                text.tool_status(tool["status"]),
                tool["findings"],
                text.database_label(tool),
            ]
            for tool in payload["tools"]
        ],
        (34, 60, 26, 22, 38),
    )
    sbom = payload.get("sbom")
    if sbom:
        pdf.paragraph(
            t(
                "report.sbom.note",
                version=sbom.get("specVersion", ""),
                count=len(sbom.get("components") or []),
            ),
            9,
        )
    if payload["limitations"]:
        pdf.paragraph(f"{t('report.annex.limitations')}:", 9, GRIS, "B")
        for item in payload["limitations"]:
            pdf.paragraph(f"- {render(item)}", 9)
    pdf.ln(2)
    pdf.paragraph(f"{t('report.scope')} {text.disclaimer()}", 9, NIGHT, "B")


def write_pdf(payload: dict[str, Any], path: Path) -> None:
    payload = owasp_top10.migrate_payload(payload)
    pdf = _Document(payload["project"]["name"])
    pdf.alias_nb_pages()
    _cover(pdf, payload)
    if payload.get("verdict"):
        _verdict(pdf, payload["verdict"])
    _summary(pdf, payload)
    _plan(pdf, payload)
    _what_we_review(pdf, payload)
    _findings(pdf, payload)
    _tables(pdf, payload)
    _annex(pdf, payload)
    pdf.output(str(path))


__all__ = ["OPEN_STATUSES", "clean", "write_pdf"]
