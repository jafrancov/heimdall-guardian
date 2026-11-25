"""Omitted places: known findings there are kept (not fixed) and every run lists them."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from helpers import FakeAdapter, make_finding
from openpyxl import load_workbook

from heimdall_guardian.adapters.base import AdapterResult
from heimdall_guardian.core.files import DEFAULT_EXCLUDED_DIRS, Exclusions, scan_tree
from heimdall_guardian.core.finding import Finding, Severity
from heimdall_guardian.core.runner import ScanResult, build_plan, run_scan
from heimdall_guardian.report import write_report
from heimdall_guardian.report.html import render_html
from heimdall_guardian.storage import Store
from heimdall_guardian.ui import model as m


def _finding(file: str, module: str = "SAST") -> Finding:
    return make_finding("uno", "R-X", file, "eval(x)", Severity.HIGH, module=module)


def _run(root: Path, findings: list[Finding], exclusions: Exclusions | None = None) -> ScanResult:
    plan = build_plan(root, profile="standard", exclusions=exclusions)
    result = run_scan(plan, adapters=[FakeAdapter("uno", AdapterResult(findings=findings))])
    with Store(root) as store:
        store.record(result)
    return result


def _open_ids(root: Path) -> int:
    with Store(root) as store:
        return store._db.execute("SELECT COUNT(*) FROM findings WHERE open = 1").fetchone()[0]


def _setup(project, *folders: str) -> Path:
    root = project("django_app")
    for folder in folders:
        (root / folder).mkdir(parents=True, exist_ok=True)
        (root / folder / "keep.txt").write_text("x")
    return root


def test_folder_skipped_later_omits_instead_of_fixing(project):
    root = _setup(project, "legacy")
    _run(root, [_finding("legacy/a.py")])
    skip = Exclusions(dirs=(*DEFAULT_EXCLUDED_DIRS, "legacy"))
    second = _run(root, [], skip)
    assert second.fixed == []
    assert second.omitted_findings == 1
    assert second.to_dict()["omitted"]["findings"] == 1
    assert "legacy" in second.to_dict()["omitted"]["folders"]
    assert _open_ids(root) == 1
    with Store(root) as store:
        row = store._db.execute("SELECT open, fixed_run FROM findings").fetchone()
    assert (row["open"], row["fixed_run"]) == (1, None)


def test_file_pattern_omits_sast_finding(project):
    root = _setup(project, "src")
    (root / "src" / "a.spec.ts").write_text("x")
    _run(root, [_finding("src/a.spec.ts")])
    second = _run(root, [], Exclusions(files=("*.spec.ts",)))
    assert second.fixed == []
    assert second.omitted_findings == 1
    assert "src/a.spec.ts" in second.to_dict()["omitted"]["files"]


def test_file_pattern_never_hides_secrets(project):
    root = _setup(project, "src")
    _run(root, [_finding("src/a.spec.ts", module="SEC")])
    second = _run(root, [], Exclusions(files=("*.spec.ts",)))
    assert [f["rule_id"] for f in second.fixed] == ["R-X"]
    assert second.omitted_findings == 0
    assert _open_ids(root) == 0


def test_without_exclusions_absent_means_fixed(project):
    root = _setup(project, "legacy")
    _run(root, [_finding("legacy/a.py")])
    second = _run(root, [])
    assert len(second.fixed) == 1
    assert second.omitted_findings == 0
    assert second.to_dict()["omitted"] == {"folders": [], "files": [], "findings": 0}


def test_scan_tree_lists_skipped_folders_but_not_vcs(tmp_path):
    for folder in ("node_modules/pkg", "legacy", ".git", "src"):
        (tmp_path / folder).mkdir(parents=True)
        (tmp_path / folder / "f.txt").write_text("x")
    info = scan_tree(tmp_path, Exclusions(dirs=(*DEFAULT_EXCLUDED_DIRS, "legacy")))
    assert info.skipped_dirs == ["legacy", "node_modules"]


def _payload(**omitted: Any) -> dict[str, Any]:
    base = {"folders": [], "files": [], "findings": 0}
    return {"omitted": {**base, **omitted}}


def _full_payload(project) -> dict[str, Any]:
    root = _setup(project, "legacy")
    data = _run(root, [_finding("app/views.py")]).to_dict()
    data.pop("omitted")
    return data


def _with(data: dict[str, Any], **omitted: Any) -> dict[str, Any]:
    return {**data, "omitted": {"folders": [], "files": [], "findings": 0, **omitted}}


def test_html_lists_omitted_places_and_old_payloads_still_render(project):
    old = _full_payload(project)
    html = render_html(
        _with(old, folders=["legacy", "<b>x</b>"], files=["src/a.spec.ts"], findings=2)
    )
    assert "legacy/" in html
    assert "src/a.spec.ts" in html
    assert "<b>x</b>" not in html
    assert render_html(old)


def test_html_caps_long_lists(project):
    data = _with(_full_payload(project), files=[f"f{i}.spec.ts" for i in range(250)])
    html = render_html(data)
    assert "f199.spec.ts" in html
    assert "f200.spec.ts" not in html


def test_xlsx_sheet_only_when_something_was_omitted(project, tmp_path):
    old = _full_payload(project)
    with_data = _with(old, folders=["legacy"], files=["=evil.spec.ts"])
    write_report(with_data, tmp_path / "a.xlsx")
    book = load_workbook(tmp_path / "a.xlsx")
    sheet = book.worksheets[-1]
    cells = [c.value for row in sheet.iter_rows(min_row=2) for c in row]
    assert "legacy" in cells
    assert "=evil.spec.ts" not in cells
    assert "'=evil.spec.ts" in cells

    write_report(old, tmp_path / "b.xlsx")
    assert len(load_workbook(tmp_path / "b.xlsx").worksheets) == len(book.worksheets) - 1


def test_pdf_builds_with_and_without_omitted(project, tmp_path):
    old = _full_payload(project)
    omitted = _with(old, folders=["legacy"], files=[f"f{i}.ts" for i in range(80)], findings=1)
    write_report(omitted, tmp_path / "a.pdf")
    write_report(old, tmp_path / "b.pdf")
    assert (tmp_path / "a.pdf").read_bytes().startswith(b"%PDF")
    assert (tmp_path / "b.pdf").read_bytes().startswith(b"%PDF")


def test_run_facts_mention_omitted_only_when_needed():
    base = {"tools": [{"name": "gitleaks", "status": "ran", "version": None, "detail": ""}]}
    plain = m.run_facts({**base, **_payload()})
    assert m.run_facts(base) == plain
    omitted = m.run_facts({**base, **_payload(folders=["legacy"], files=["a.spec.ts"])})
    assert len(omitted) == len(plain) + 1
    assert "1" in omitted[-1]
