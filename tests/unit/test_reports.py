from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from helpers import FakeAdapter, make_finding
from openpyxl import load_workbook

from heimdall_guardian.adapters.base import AdapterResult
from heimdall_guardian.core import owasp
from heimdall_guardian.core.finding import Category, Severity
from heimdall_guardian.core.runner import build_plan, run_scan
from heimdall_guardian.report import write_report
from heimdall_guardian.report.html import render_html
from heimdall_guardian.report.sarif import render_sarif
from heimdall_guardian.report.text import disclaimer
from heimdall_guardian.report.xlsx import safe_cell
from heimdall_guardian.storage import Store

HOSTILE = '<script>alert("xss")</script>'


def _payload(root: Path, findings) -> dict:
    result = run_scan(
        build_plan(root, profile="standard"),
        adapters=[FakeAdapter("uno", AdapterResult(findings=findings))],
    )
    with Store(root) as store:
        store.record(result)
    return result.to_dict()


@pytest.fixture
def payload(project) -> dict:
    root = project("django_app")
    crit = make_finding(
        "uno",
        "DJ-SQL-001",
        "app/views.py",
        f"cursor.execute({HOSTILE})",
        Severity.CRITICAL,
        module="SAST",
        owasp="A05:2025 Injection",
        cwe="CWE-89",
    )
    crit.title = "SQL dinámico en consulta directa"
    gone = make_finding("uno", "R-VIEJA", "app/old.py", "eval(x)", Severity.MEDIUM, module="SAST")
    lib = make_finding(
        "uno",
        "CVE-2019-14234",
        "requirements.txt",
        "django@2.2.0",
        Severity.HIGH,
        category=Category.DEPENDENCIES,
        module="DEP",
    )
    formula = make_finding("uno", "R-XLS", "=HYPERLINK(evil).py", "x", Severity.LOW, module="SAST")
    _payload(root, [crit, gone])
    return _payload(root, [crit, lib, formula])


def test_html_report_is_self_contained_and_escapes_hostile_content(payload: dict):
    html = render_html(payload)
    assert HOSTILE not in html
    assert "&lt;script&gt;alert" in html
    assert "http://" not in html.split("<main>")[0]
    assert "<link" not in html
    assert 'src="http' not in html  # the only resource is the logo, embedded
    assert 'src="data:image/png;base64,' in html
    for expected in (
        "Semáforo: rojo",
        "SQL dinámico en consulta directa",
        "Dependencia vulnerable: django",
        "Corregidos desde la corrida anterior",
        "A05:2025 Injection",
        "Tendencia de hallazgos abiertos",
        payload["project"]["tree_hash"],
        disclaimer(),
    ):
        assert expected in html


def test_html_report_without_findings_or_baseline(project):
    result = run_scan(build_plan(project("php_app"), profile="quick"), adapters=[])
    html = render_html(result.to_dict())
    assert "Semáforo: verde" in html
    assert "Corrida sin línea base" in html


def test_xlsx_has_one_row_per_finding_and_neutralizes_formulas(payload: dict, tmp_path: Path):
    path = tmp_path / "reporte.xlsx"
    write_report(payload, path)
    sheet = load_workbook(path)["Hallazgos"]
    header = [cell.value for cell in sheet[1]]
    rows = list(sheet.iter_rows(min_row=2, values_only=True))
    assert len(rows) == len(payload["findings"]) + len(payload["fixed"])
    assert {"Responsable", "Fecha compromiso", "Estado de atención"} <= set(header)
    files = [row[header.index("Archivo")] for row in rows]
    assert "'=HYPERLINK(evil).py" in files
    assert all(cell.data_type != "f" for row in sheet.iter_rows() for cell in row)
    assert [safe_cell(v) for v in ("+1", "-1", "@x", "normal", 7)] == [
        "'+1",
        "'-1",
        "'@x",
        "normal",
        7,
    ]


def test_sarif_shape_and_baseline_state(payload: dict):
    sarif = render_sarif(payload)
    assert sarif["version"] == "2.1.0"
    (run,) = sarif["runs"]
    assert run["tool"]["driver"]["name"] == "Heimdall Guardian"
    by_rule = {r["ruleId"]: r for r in run["results"]}
    assert by_rule["DJ-SQL-001"]["level"] == "error"
    assert by_rule["DJ-SQL-001"]["baselineState"] == "unchanged"
    assert by_rule["CVE-2019-14234"]["baselineState"] == "new"
    assert by_rule["R-VIEJA"]["baselineState"] == "absent"
    # Without a known line, no region is invented.
    assert "region" in by_rule["DJ-SQL-001"]["locations"][0]["physicalLocation"]
    assert {r["id"] for r in run["tool"]["driver"]["rules"]} == set(by_rule)
    json.dumps(sarif)


def test_write_report_rejects_unknown_format(payload: dict, tmp_path: Path):
    with pytest.raises(ValueError, match="Formato no soportado"):
        write_report(payload, tmp_path / "reporte.docx")


def _as_2021(payload: dict) -> dict:
    old = {**payload, "findings": [dict(f) for f in payload["findings"]]}
    for finding in old["findings"]:
        if finding["owasp"]:
            finding["owasp"] = "A03:2021 Injection"
    assert any("2021" in (f["owasp"] or "") for f in old["findings"])
    return old


def test_html_has_the_executive_owasp_section_and_migrates_old_runs(payload: dict):
    html = render_html(_as_2021(payload))
    assert "Qué revisa Heimdall Guardian" in html
    assert "Qué es OWASP" in html
    assert "A05:2025 Inyección" in html
    assert "Cobertura de Heimdall Guardian" in html
    assert owasp.scope_warning() in html
    assert "2021" not in html
    assert html.index("Qué revisa Heimdall Guardian") < html.index("Hallazgos detallados")
    assert re.search(r'A05:2025 Injection</span><i[^>]*></i><span class="num">1<', html)


def test_pdf_and_xlsx_carry_the_owasp_section(payload: dict, tmp_path: Path, monkeypatch):
    seen: list[list[dict]] = []
    original = owasp.coverage_rows
    monkeypatch.setattr(
        owasp, "coverage_rows", lambda findings: seen.append(original(findings)) or seen[-1]
    )
    pdf = tmp_path / "r.pdf"
    write_report(_as_2021(payload), pdf)
    assert pdf.read_bytes().startswith(b"%PDF")
    assert {r["code"]: r["count"] for r in seen[0]}["A05"] == 1
    assert len(seen[0]) == 10

    xlsx = tmp_path / "r.xlsx"
    write_report(_as_2021(payload), xlsx)
    sheet = load_workbook(xlsx)["OWASP Top 10"]
    rows = list(sheet.iter_rows(min_row=2, max_row=11, values_only=True))
    assert [r[0].split()[0] for r in rows] == [f"{c.code}:2025" for c in owasp.CATEGORIES]
    assert next(r for r in rows if r[0].startswith("A05"))[6] == 1
    findings_col = [c.value for c in load_workbook(xlsx)["Hallazgos"]["L"]]
    assert "A05:2025 Injection" in findings_col
    assert not any("2021" in str(v) for v in findings_col)


def test_json_and_sarif_carry_2025_labels(payload: dict, tmp_path: Path):
    for name in ("r.json", "r.sarif"):
        write_report(_as_2021(payload), tmp_path / name)
        assert "2021" not in (tmp_path / name).read_text(encoding="utf-8")
        assert "A05:2025 Injection" in (tmp_path / name).read_text(encoding="utf-8")


def test_stored_run_with_2021_labels_reads_as_2025(project):
    root = project("django_app")
    old = make_finding(
        "uno", "R-OLD", "app/a.py", "eval(x)", Severity.HIGH, module="SAST",
        owasp="A06:2021 Vulnerable and Outdated Components",
    )  # fmt: skip
    _payload(root, [old])
    with Store(root) as store:
        assert store.payload()["findings"][0]["owasp"] == "A03:2025 Software Supply Chain Failures"


def test_html_shows_how_to_verify_when_there_is_a_guide(payload: dict):
    payload["findings"][0]["cwe"] = "CWE-89"
    assert "Cómo verificarlo" in render_html(payload)
    payload["findings"][0]["cwe"] = "CWE-1"
    assert "Cómo verificarlo" not in render_html(payload)


def test_t4_finding_shows_reachability_in_every_format(payload: dict, tmp_path: Path):
    finding = payload["findings"][0]
    finding["origin"] = "ai"
    finding["llm_assessment"] = {
        "task": "T4",
        "model": "m",
        "reachable": "yes",
        "source": "query parameter id",
        "risk": "high",
        "explanation": "The id reaches the query.",
        "suggested_fix": "Use parameters.",
    }
    html = render_html(payload)
    assert "Alcanzable desde la entrada del usuario" in html
    assert "query parameter id" in html
    write_report(payload, tmp_path / "r.pdf")
    write_report(payload, tmp_path / "r.xlsx")
    assert (tmp_path / "r.pdf").read_bytes().startswith(b"%PDF")
    assert (tmp_path / "r.xlsx").exists()
