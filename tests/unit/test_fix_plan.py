from __future__ import annotations

from pathlib import Path

import pytest
from helpers import FakeAdapter, make_finding
from openpyxl import load_workbook

from heimdall_guardian.adapters.base import AdapterResult
from heimdall_guardian.core.finding import Category, Origin, Severity
from heimdall_guardian.core.runner import build_plan, run_scan
from heimdall_guardian.i18n import t
from heimdall_guardian.report import write_report
from heimdall_guardian.report.html import render_html
from heimdall_guardian.report.plan import _highest, fix_plan, plan_line
from heimdall_guardian.ui import model


def _f(rule, file, snippet, severity, **extra):
    base = {
        "id": f"HDL-2026-{abs(hash((rule, file, snippet))) % 1000000:06d}",
        "rule_id": rule,
        "category": "sast",
        "severity": severity,
        "file": file,
        "snippet": snippet,
        "fixed_version": "",
        "baseline_status": "new",
        "origin": "deterministic",
        "title": f"title of {rule}",
        "texts": {"es": {"title": f"titulo de {rule}"}},
    }
    return {**base, **extra}


def _dep(pkg, file, fixed, severity="high", **extra):
    return _f(
        f"CVE-{pkg}-{fixed}",
        file,
        f"{pkg}@1.0.0",
        severity,
        category="dependencies",
        fixed_version=fixed,
        **extra,
    )


def test_dependencies_group_by_package_with_highest_target():
    payload = {
        "findings": [
            _dep("lodash", "a/package-lock.json", "4.17.19"),
            _dep("lodash", "b/package-lock.json", "4.17.21"),
            _dep("minimist", "a/package-lock.json", "1.2.6"),
        ]
    }
    plan = fix_plan(payload)
    assert [g.key for g in plan] == ["lodash", "minimist"]
    assert (plan[0].target, plan[0].count, plan[0].files) == ("4.17.21", 2, 2)
    assert len(plan[0].ids) == 2


def test_version_compare_is_tolerant():
    assert _highest(["4.17.9", "4.17.21"]) == "4.17.21"
    assert _highest(["1.2.3-rc1", "1.2.3"]) == "1.2.3"
    assert _highest([["1.2.3", "2.0.1"][0], "2.0.1"]) == "2.0.1"
    assert _highest([]) == ""
    payload = {"findings": [_dep("x", "f", "1.2.3, 2.0.1"), _dep("x", "g", "")]}
    assert fix_plan(payload)[0].target == "2.0.1"
    assert fix_plan({"findings": [_dep("y", "f", "")]})[0].target == ""


def test_rule_grouping_and_title_language():
    payload = {
        "findings": [
            _f("R-1", "a.py", "x1", "high"),
            _f("R-1", "a.py", "x2", "medium"),
            _f("R-1", "b.py", "x3", "low"),
        ]
    }
    (group,) = fix_plan(payload, lang="es")
    assert (group.count, group.files, group.severity) == (3, 2, "high")
    assert group.title == "titulo de R-1"
    assert fix_plan(payload, lang="en")[0].title == "title of R-1"


def test_excluded_and_ordering_and_empty():
    payload = {
        "findings": [
            _f("AI-1", "a.py", "a", "critical", origin="ai"),
            _f("ACC", "a.py", "b", "critical", baseline_status="accepted"),
            _f("FP", "a.py", "c", "critical", baseline_status="false_positive"),
            _f("MANY", "a.py", "d", "medium"),
            _f("MANY", "b.py", "e", "medium"),
            _f("HI", "a.py", "f", "high"),
            _f("ONE", "a.py", "g", "medium"),
        ]
    }
    assert [g.key for g in fix_plan(payload)] == ["HI", "MANY", "ONE"]
    assert len(fix_plan(payload, limit=2)) == 2
    assert fix_plan({}) == []
    assert fix_plan({"findings": []}) == []


def test_plan_line_in_both_languages():
    payload = {
        "findings": [
            _dep("lodash", "a", "4.17.21"),
            _dep("old", "a", ""),
            _f("R-1", "a.py", "x", "low"),
        ]
    }
    lines = {g.key: g for g in fix_plan(payload, lang="en")}
    assert plan_line(lines["lodash"], "en") == (
        "Update lodash to 4.17.21: resolves 1 finding in 1 file"
    )
    assert "Actualiza lodash a 4.17.21" in plan_line(lines["lodash"], "es")
    assert "no fixed version" in plan_line(lines["old"], "en")
    assert "title of R-1: 1 finding" in plan_line(lines["R-1"], "en")
    assert "hallazgo" in plan_line(lines["R-1"], "es")


def _payload(root: Path, findings) -> dict:
    result = run_scan(
        build_plan(root, profile="standard"),
        adapters=[FakeAdapter("uno", AdapterResult(findings=findings))],
    )
    return result.to_dict()


@pytest.fixture
def with_findings(project) -> dict:
    root = project("django_app")
    lib = make_finding(
        "uno",
        "CVE-1",
        "requirements.txt",
        "django@2.2.0",
        Severity.HIGH,
        category=Category.DEPENDENCIES,
        module="DEP",
        fixed_version="3.2.1",
    )
    code = make_finding("uno", "R-2", "app/v.py", "eval(x)", Severity.MEDIUM, module="SAST")
    return _payload(root, [lib, code])


def test_html_xlsx_pdf_with_findings(with_findings: dict, tmp_path: Path):
    html = render_html(with_findings)
    assert t("report.plan.title") in html
    xlsx = tmp_path / "r.xlsx"
    write_report(with_findings, xlsx)
    book = load_workbook(xlsx)
    assert t("report.plan.title") in book.sheetnames
    rows = list(book[t("report.plan.title")].iter_rows(values_only=True))
    assert len(rows) == 3
    assert rows[1][0] == 1
    pdf = tmp_path / "r.pdf"
    write_report(with_findings, pdf)
    assert pdf.read_bytes().startswith(b"%PDF")


def test_html_xlsx_without_findings(project, tmp_path: Path):
    payload = _payload(project("django_app"), [])
    assert t("report.plan.title") not in render_html(payload)
    xlsx = tmp_path / "r.xlsx"
    write_report(payload, xlsx)
    assert t("report.plan.title") not in load_workbook(xlsx).sheetnames
    assert model.plan_rows(payload) == []
    pdf = tmp_path / "r.pdf"
    write_report(payload, pdf)
    assert pdf.read_bytes().startswith(b"%PDF")


def test_ui_plan_rows(with_findings: dict):
    rows = model.plan_rows(with_findings)
    assert [r["severity"] for r in rows] == ["high", "medium"]
    assert "django" in rows[0]["line"]


def test_ai_findings_never_count():
    payload = {"findings": [_f("AI", "a", "x", "high", origin=Origin.AI.value)]}
    assert fix_plan(payload) == []
