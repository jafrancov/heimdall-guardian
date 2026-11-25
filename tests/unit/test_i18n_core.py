"""Core and report texts in the chosen language, from what was stored."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from helpers import FakeAdapter, make_finding
from openpyxl import load_workbook

from heimdall_guardian import i18n
from heimdall_guardian.adapters.base import (
    AdapterError,
    AdapterResult,
    MissingDatabaseError,
    bases_location,
)
from heimdall_guardian.core import coverage, owasp
from heimdall_guardian.core.finding import Severity
from heimdall_guardian.core.runner import build_plan, run_scan
from heimdall_guardian.core.verdict import Thresholds
from heimdall_guardian.i18n import msg, render, set_language
from heimdall_guardian.report import write_report
from heimdall_guardian.storage import Store

SPANISH_WORDS = re.compile(
    r"\b(Perfil|Fecha|Archivo|Hallazgos?|Severidad|Estado|Corrida|Dictamen|Limitaciones|"
    r"Resumen|Cómo|Qué|Ninguna?|Dependencias|Ruta|Herramienta|Versión|Alcance)\b"
)


@pytest.fixture
def stored(project):
    """A run with limitations, verdict and baseline, saved to and read back from the database."""
    root = project("django_app")
    finding = make_finding(
        "uno", "DJ-SQL-001", "app/views.py", "cursor.execute(q)", Severity.CRITICAL, module="SAST"
    )

    class NoDatabase(FakeAdapter):
        def invoke(self, ctx):
            raise MissingDatabaseError()

    plan = build_plan(root, profile="vendor")
    result = run_scan(
        plan,
        adapters=[FakeAdapter("uno", AdapterResult(findings=[finding])), NoDatabase("trivy")],
    )
    with Store(root) as store:
        store.record(result, thresholds=Thresholds(), issuer="ACME")
        return store.payload()


def _html_text(html: str) -> str:
    body = re.sub(r"<style>.*?</style>|<script>.*?</script>", "", html, flags=re.S)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body))


def test_structured_messages_render_in_both_languages_and_survive_json():
    item = msg("core.limit.symlinks", count=2)
    assert json.loads(json.dumps(item)) == {"code": "core.limit.symlinks", "params": {"count": 2}}
    assert render(item, "es") == "2 enlace(s) simbólico(s) ignorados."
    assert render(item, "en") == "2 symbolic links were ignored."
    assert render(msg("core.limit.symlinks", count=1), "en") == "1 symbolic link was ignored."
    set_language("en")
    assert str(item) == "2 symbolic links were ignored."  # an f-string also speaks the language
    set_language("es")
    assert f"{item}" == "2 enlace(s) simbólico(s) ignorados."


def test_render_handles_nested_messages_lists_and_free_text():
    examples = msg("core.examples.many", paths=["a.py", "b.py", "c.py"])
    item = msg("core.limit.oversized", count=4, limit=500, examples=examples)
    assert render(item, "en").endswith("(e.g. a.py, b.py, c.py and others).")
    assert render(item, "es").endswith("(p. ej. a.py, b.py, c.py y otros).")
    problems = [msg("llm.problem", name="a", error="x"), msg("llm.problem", name="b", error="y")]
    assert render(msg("llm.detail.problems", problems=problems), "en") == "a: x; b: y"
    assert render("texto suelto de una herramienta") == "texto suelto de una herramienta"
    assert render(None) == ""
    # A code that is not in the catalog is shown as is (it does not break an old report).
    assert render(msg("Texto ya redactado")) == "Texto ya redactado"


def test_limitations_are_stored_as_messages_not_text(stored: dict):
    assert stored["limitations"]
    assert all(isinstance(item, dict) and "code" in item for item in stored["limitations"])
    codes = {item["code"] for item in stored["limitations"]}
    assert "adapter.db.missing" in codes
    tools = {tool["name"]: tool for tool in stored["tools"]}
    assert tools["trivy"]["detail"]["code"] == "adapter.db.missing_short"
    # The verdict stores the criterion as a message, not as text.
    assert stored["verdict"]["criteria"][0]["criterion"]["code"].startswith("verdict.criterion.")
    # Nothing stored ended up in a language: the JSON does not contain the translated text.
    raw = json.dumps(stored, ensure_ascii=False)
    assert "Faltan las bases" not in raw
    assert "databases are missing" not in raw


def test_a_stored_limitation_is_shown_in_the_current_language(stored: dict):
    limitation = next(i for i in stored["limitations"] if i["code"] == "adapter.db.missing")
    assert "Faltan las bases de vulnerabilidades" in render(limitation, "es")
    assert "vulnerability databases are missing" in render(limitation, "en")
    set_language("en")
    assert "vulnerability databases are missing" in render(limitation)


def test_reports_are_generated_in_english_and_spanish_from_the_same_payload(
    stored: dict, tmp_path: Path
):
    texts: dict[str, dict[str, str]] = {"en": {}, "es": {}}
    for lang in ("en", "es"):
        set_language(lang)
        html, pdf, xlsx = (tmp_path / f"{lang}{ext}" for ext in (".html", ".pdf", ".xlsx"))
        for path in (html, pdf, xlsx):
            write_report(stored, path)
        assert pdf.read_bytes().startswith(b"%PDF")
        texts[lang]["html"] = html.read_text(encoding="utf-8")
        book = load_workbook(xlsx)
        texts[lang]["sheets"] = " | ".join(book.sheetnames)
        texts[lang]["xlsx"] = " ".join(
            str(cell.value or "") for sheet in book for row in sheet.iter_rows() for cell in row
        )

    english, spanish = texts["en"], texts["es"]
    assert '<html lang="en">' in english["html"]
    assert '<html lang="es-MX">' in spanish["html"]
    visible = _html_text(english["html"])
    for expected in (
        "Delivery verdict",
        "NOT APPROVED",
        "Traffic light: red",
        "Detailed findings",
        "Technical annex",
        "What Heimdall Guardian checks",
        "The vulnerability databases are missing",
        "Mishandling of Exceptional Conditions",
    ):
        assert expected in visible
    assert not SPANISH_WORDS.search(visible.replace("Secreto", ""))
    assert "Dictamen de entrega" in spanish["html"]
    assert "Faltan las bases de vulnerabilidades" in spanish["html"]
    assert "Manejo inadecuado de condiciones excepcionales" in spanish["html"]
    assert english["sheets"] == "Findings | Summary | Where to start | OWASP Top 10"
    assert spanish["sheets"] == "Hallazgos | Resumen | Por dónde empezar | OWASP Top 10"
    assert "The vulnerability databases are missing" in english["xlsx"]
    assert "Faltan las bases de vulnerabilidades" in spanish["xlsx"]


def test_pdf_text_is_in_the_chosen_language(stored: dict, tmp_path: Path):
    from heimdall_guardian.report.pdf import clean

    set_language("en")
    path = tmp_path / "r.pdf"
    write_report(stored, path)
    raw = path.read_bytes()
    assert raw.startswith(b"%PDF")
    # The texts go through `clean` (Latin-1): what cannot be drawn is replaced.
    assert clean("Delivery verdict — “ok” …") == 'Delivery verdict - "ok" ...'
    assert clean(i18n.t("report.pdf.page", page=1, total=5)) == "Page 1 of 5"


def test_html_dates_and_counts_follow_the_language(stored: dict):
    from heimdall_guardian.report.html import render_html

    set_language("en")
    english = _html_text(render_html(stored))
    assert re.search(r"1 case in 1 file", english)
    set_language("es")
    assert re.search(r"1 caso en 1 archivo", _html_text(render_html(stored)))


def test_regenerating_a_report_saved_in_spanish_gives_english_text(stored: dict, tmp_path: Path):
    """What is stored carries no language: `hdl report` shows it in the current language."""
    set_language("es")
    spanish = tmp_path / "es.html"
    write_report(stored, spanish)
    set_language("en")
    english = tmp_path / "en.html"
    write_report(stored, english)
    assert "Dictamen de entrega" in spanish.read_text(encoding="utf-8")
    assert "Dictamen de entrega" not in english.read_text(encoding="utf-8")
    assert "Delivery verdict" in english.read_text(encoding="utf-8")


def test_sarif_limitations_are_rendered_text(stored: dict):
    from heimdall_guardian.report.sarif import render_sarif

    set_language("en")
    (run,) = render_sarif(stored)["runs"]
    assert all(isinstance(text, str) for text in run["properties"]["limitations"])
    assert any("databases are missing" in text for text in run["properties"]["limitations"])


def test_owasp_and_coverage_have_no_visible_constants_frozen_at_import():
    """Nothing visible is computed at import time: changing language changes the text."""
    for module in (owasp, coverage):
        frozen = [
            name
            for name, value in vars(module).items()
            if isinstance(value, str)
            and not name.startswith("_")
            and name != "annotations"
            and " " in value
        ]
        assert not frozen, (module.__name__, frozen)
    for category in owasp.CATEGORIES:
        for part in ("explanation", "example", "coverage_note", "name"):
            assert getattr(category, part)("en") != getattr(category, part)("es") or part == "name"
    assert owasp.what_is_owasp("en") != owasp.what_is_owasp("es")
    assert owasp.scope_warning("en") != owasp.scope_warning("es")
    assert owasp.verification_hint("CWE-89", "en") != owasp.verification_hint("CWE-89", "es")
    set_language("en")
    assert owasp.what_is_owasp().startswith("OWASP is a non-profit")
    assert owasp.CATEGORIES[4].name() == "Injection"
    set_language("es")
    assert owasp.CATEGORIES[4].name() == "Inyección"
    assert owasp.coverage_label("partial", "en") == "Partly"
    assert owasp.coverage_label("partial", "es") == "En parte"


def test_coverage_notes_are_messages():
    from heimdall_guardian.core.detector import Stack

    (note,) = coverage.coverage_notes([Stack.GO])
    assert render(note, "en").startswith("Go: secrets, dependencies and configuration")
    assert render(note, "es").startswith("Go: se revisan secretos")


def test_adapter_errors_carry_a_structured_message():
    error = AdapterError("adapter.failed", tool="trivy", detail="boom")
    assert error.message == {
        "code": "adapter.failed",
        "params": {"tool": "trivy", "detail": "boom"},
    }
    assert render(error.message, "en") == "trivy failed: boom"
    assert render(error.message, "es") == "trivy falló: boom"
    partial = MissingDatabaseError(
        "adapter.osv.db_missing",
        partial=True,
        named=msg("adapter.osv.db_of_one"),
        **bases_location(),
    )
    assert partial.partial
    assert "the database for an ecosystem" in render(partial.message, "en")


def test_errors_raised_for_immediate_display_follow_the_language():
    from heimdall_guardian.llm.destinations import DestinationError, validate_model, validate_url

    set_language("en")
    with pytest.raises(DestinationError, match="not local"):
        validate_url("http://example.com/v1")
    with pytest.raises(DestinationError, match="runs in the cloud"):
        validate_model("llama:cloud")
    set_language("es")
    with pytest.raises(DestinationError, match="no es local"):
        validate_url("http://example.com/v1")
