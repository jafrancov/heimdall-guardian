from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path

import pytest
from helpers import FakeAdapter, make_finding

from heimdall_guardian import cli
from heimdall_guardian.adapters.base import AdapterResult
from heimdall_guardian.core.finding import BaselineStatus, Category, Finding, Severity
from heimdall_guardian.core.runner import ScanResult, build_plan, run_scan
from heimdall_guardian.i18n import render
from heimdall_guardian.storage import Store, forget_project, list_projects

S = BaselineStatus


def sast(rule: str, file: str, snippet: str, line: int = 1, sev: Severity = Severity.HIGH):
    finding = make_finding("uno", rule, file, snippet, sev, module="SAST")
    finding.line_start = finding.line_end = line
    return finding


def dep(cve: str, component: str) -> Finding:
    return make_finding(
        "uno",
        cve,
        "requirements.txt",
        component,
        Severity.MEDIUM,
        category=Category.DEPENDENCIES,
        module="DEP",
    )


def scan(
    root: Path, findings: list[Finding], *, profile: str = "standard", **adapter
) -> ScanResult:
    """A complete run with a baseline, using a fake adapter called `uno`."""
    plan = build_plan(root, profile=profile)
    result = run_scan(
        plan, adapters=[FakeAdapter("uno", AdapterResult(findings=findings), **adapter)]
    )
    with Store(root) as store:
        store.record(result)
    return result


def states(result: ScanResult) -> dict[str, BaselineStatus]:
    return {f.rule_id: f.baseline_status for f in result.findings}


def test_two_runs_show_new_persistent_and_fixed(project):
    """Exit criterion of H3."""
    root = project("django_app")
    first = scan(root, [sast("R-A", "a.py", "eval(x)"), sast("R-B", "b.py", "exec(y)")])
    assert states(first) == {"R-A": S.NEW, "R-B": S.NEW}
    assert (first.run_id, first.previous_run_id, first.fixed) == (1, None, [])

    second = scan(root, [sast("R-A", "a.py", "eval(x)"), sast("R-C", "c.py", "os.system(z)")])
    assert states(second) == {"R-A": S.PERSISTENT, "R-C": S.NEW}
    assert [(f["rule_id"], f["baseline_status"]) for f in second.fixed] == [("R-B", "fixed")]
    assert second.summary()["by_status"] == {
        "new": 1,
        "persistent": 1,
        "fixed": 1,
        "accepted": 0,
        "false_positive": 0,
    }
    assert [run["run"] for run in second.trend] == [1, 2]

    # IDs are consecutive per project and stable across runs.
    ids = {f.rule_id: f.id for f in [*first.findings, *second.findings]}
    year = first.started.year
    assert ids == {
        "R-A": f"HDL-{year}-000001",
        "R-B": f"HDL-{year}-000002",
        "R-C": f"HDL-{year}-000003",
    }

    third = scan(root, [sast("R-B", "b.py", "exec(y)")])
    # A fixed finding that reappears comes back as NUEVO, with its original ID.
    assert states(third) == {"R-B": S.NEW}
    assert third.findings[0].id == f"HDL-{year}-000002"


def test_moved_code_is_not_a_new_finding(project):
    root = project("django_app")
    scan(root, [sast("R-A", "a.py", "cursor.execute(q)", line=10)])
    moved = scan(root, [sast("R-A", "a.py", "cursor.execute(q)", line=240)])
    assert states(moved) == {"R-A": S.PERSISTENT}
    assert moved.fixed == []


def test_edited_snippet_nearby_keeps_identity_but_far_away_does_not(project):
    root = project("django_app")
    first = scan(root, [sast("R-A", "a.py", "cursor.execute(q + x)", line=10)])
    edited = scan(root, [sast("R-A", "a.py", "cursor.execute(q + y)", line=18)])
    assert states(edited) == {"R-A": S.PERSISTENT}
    assert edited.findings[0].id == first.findings[0].id
    assert edited.fixed == []

    far = scan(root, [sast("R-A", "a.py", "cursor.execute(otra)", line=300)])
    assert states(far) == {"R-A": S.NEW}
    assert len(far.fixed) == 1


def test_shorter_profile_or_failed_tool_does_not_fix_findings(project):
    root = project("django_app")
    scan(root, [sast("R-A", "a.py", "eval(x)"), dep("CVE-1", "django@2.2.0")])

    # The quick profile does not include SAST: R-A was not evaluated, so it is not fixed.
    quick = scan(root, [], profile="quick")
    assert [f["rule_id"] for f in quick.fixed] == ["CVE-1"]

    scan(root, [sast("R-A", "a.py", "eval(x)"), dep("CVE-2", "django@2.2.0")])
    broken = scan(root, [], error="explotó")
    assert broken.fixed == []

    back = scan(root, [sast("R-A", "a.py", "eval(x)")])
    assert states(back) == {"R-A": S.PERSISTENT}


def test_suppressions_require_justification_and_expire(project):
    root = project("django_app")
    findings = [
        sast("R-A", "a.py", "eval(x)", sev=Severity.CRITICAL),
        sast("R-B", "b.py", "exec(y)"),
    ]
    first = scan(root, findings)
    id_a, id_b = (f.id for f in first.findings)
    today = first.started.date()

    with Store(root) as store:
        with pytest.raises(ValueError, match="obligatoria"):
            store.suppress(id_a, S.ACCEPTED, "   ", "ana")
        with pytest.raises(ValueError, match="ACEPTADO o FALSO_POSITIVO"):
            store.suppress(id_a, S.FIXED, "x", "ana")
        with pytest.raises(LookupError):
            store.suppress("HDL-1999-000001", S.ACCEPTED, "x", "ana")
        store.suppress(
            id_a, S.ACCEPTED, "Sistema interno sin exposición", "ana", today + timedelta(days=30)
        )
        store.suppress(
            id_b, S.FALSE_POSITIVE, "El valor es una constante", "ana", today - timedelta(days=1)
        )
        assert [s["id"] for s in store.suppressions()] == [id_a, id_b]

    second = scan(root, findings)
    # The current one hides the finding from the count; the expired one no longer does.
    assert states(second) == {"R-A": S.ACCEPTED, "R-B": S.PERSISTENT}
    assert second.summary()["by_severity"]["critical"] == 0
    assert any(id_b in render(text) and "venció" in render(text) for text in second.limitations)

    with Store(root) as store:
        assert store.unsuppress(id_a) is True
        assert store.unsuppress(id_a) is False
    assert states(scan(root, findings))["R-A"] is S.PERSISTENT


def test_store_keeps_data_outside_analyzed_folder_and_strips_git_credentials(
    project, isolated_data_dir: Path
):
    root = project("django_app")
    (root / ".git").mkdir()
    (root / ".git" / "config").write_text(
        '[remote "origin"]\n\turl = https://ana:ghp_secreto@git.example/acme/payroll.git\n'
    )
    before = sorted(p.as_posix() for p in root.rglob("*"))
    scan(root, [sast("R-A", "a.py", "eval(x)")])
    assert sorted(p.as_posix() for p in root.rglob("*")) == before

    (project_json,) = isolated_data_dir.glob("projects/*/project.json")
    data = json.loads(project_json.read_text())
    assert data["key"] == "https://git.example/acme/payroll.git"

    with pytest.raises(ValueError, match="dentro de la carpeta analizada"):
        Store(root, base=root / "datos")


def test_cli_scan_suppress_and_report_flow(project, tmp_path: Path, monkeypatch, capsys):
    root = project("php_app")
    finding = sast("PHP-EXE-001", "index.php", "system($x)", line=8, sev=Severity.CRITICAL)
    fake = FakeAdapter("uno", AdapterResult(findings=[finding]))
    monkeypatch.setattr("heimdall_guardian.core.runner.default_adapters", lambda: [fake])
    out = tmp_path / "salidas"
    out.mkdir()

    assert cli.main(["scan", str(root), "--salida", str(out / "uno.json")]) == 0
    finding_id = json.loads((out / "uno.json").read_text())["findings"][0]["id"]

    args = ["suppress", str(root), finding_id, "--estado", "aceptado"]
    assert (
        cli.main([*args, "--motivo", "Se retira en la versión 2", "--revisar", "2099-01-01"]) == 0
    )
    assert cli.main(["suppressions", str(root)]) == 0
    assert "Se retira en la versión 2" in capsys.readouterr().out

    assert cli.main(["scan", str(root), "--salida", str(out / "dos.json")]) == 0
    assert (
        json.loads((out / "dos.json").read_text())["findings"][0]["baseline_status"] == "accepted"
    )

    # `report` regenerates any saved run without analyzing again.
    calls = len(fake.contexts)
    formats = [str(out / f"r.{ext}") for ext in ("html", "xlsx", "sarif", "json")]
    outputs = [arg for path in formats for arg in ("--salida", path)]
    assert cli.main(["report", str(root), "--corrida", "1", *outputs]) == 0
    assert len(fake.contexts) == calls
    # Run 1 was the latest when the risk was accepted: it reflects it immediately.
    assert json.loads((out / "r.json").read_text())["findings"][0]["baseline_status"] == "accepted"
    assert all(Path(f).stat().st_size > 0 for f in formats)

    assert cli.main(["runs", str(root)]) == 0
    assert len(capsys.readouterr().out.strip().splitlines()) == 2
    assert cli.main(["report", str(root), "--corrida", "99"]) == 2
    assert cli.main(["scan", str(root), "--salida", str(out / "x.docx")]) == 2
    assert cli.main(["unsuppress", str(root), "HDL-1999-000001"]) == 2
    # An AI configuration that does not exist is rejected before analyzing.
    assert cli.main(["scan", str(root), "--perfil", "full", "--ia", "nadie"]) == 2
    assert "No existe la configuración de IA 'nadie'" in capsys.readouterr().err


def test_scan_without_baseline_stores_nothing(
    project, isolated_data_dir: Path, monkeypatch, capsys
):
    fake = FakeAdapter("uno", AdapterResult(findings=[sast("R-A", "a.py", "eval(x)")]))
    monkeypatch.setattr("heimdall_guardian.core.runner.default_adapters", lambda: [fake])
    assert cli.main(["scan", str(project("php_app")), "--sin-linea-base"]) == 0
    assert json.loads(capsys.readouterr().out)["baseline"] is None
    assert not list(isolated_data_dir.iterdir())


def test_baseline_travels_between_teammates_and_detects_tampering(project, tmp_path, monkeypatch):
    root = project("django_app")
    findings = [sast("R-A", "a.py", "eval(x)"), sast("R-B", "b.py", "exec(y)")]
    first = scan(root, findings)
    with Store(root) as store:
        store.suppress(first.findings[0].id, S.ACCEPTED, "Sistema sin exposición", "ana")
    shared = tmp_path / ".heimdall-baseline.json"
    assert cli.main(["baseline", str(root), "--exportar", str(shared)]) == 0
    assert "eval(x)" not in shared.read_text()  # no code travels
    assert cli.main(["baseline", str(root), "--exportar", str(root / "dentro.json")]) == 2

    # Another person, with their own data directory and no previous runs.
    monkeypatch.setenv("HDL_DATA_DIR", str(tmp_path / "otro-equipo"))
    assert cli.main(["baseline", str(root), "--importar", str(shared)]) == 0
    assert cli.main(["baseline", str(root), "--importar", str(shared)]) == 0  # idempotent
    theirs = scan(root, findings)
    assert states(theirs) == {"R-A": S.ACCEPTED, "R-B": S.PERSISTENT}

    tampered = json.loads(shared.read_text())
    tampered["suppressions"][0]["justification"] = "Cambiada a mano"
    shared.write_text(json.dumps(tampered))
    assert cli.main(["baseline", str(root), "--importar", str(shared)]) == 2
    assert cli.main(["baseline", str(root)]) == 2


def test_accepting_a_risk_updates_the_last_run_without_rescanning(project):
    root = project("django_app")
    critical = sast("R-A", "a.py", "eval(x)", sev=Severity.CRITICAL)
    first = scan(root, [critical, sast("R-B", "b.py", "exec(y)")])
    scan(root, [critical, sast("R-B", "b.py", "exec(y)")])
    finding_id = first.findings[0].id

    with Store(root) as store:
        store.suppress(finding_id, S.ACCEPTED, "Sistema sin exposición", "ana")
        payload = store.payload()
        earlier = store.payload(1)
    by_rule = {f["rule_id"]: f["baseline_status"] for f in payload["findings"]}
    assert by_rule == {"R-A": "accepted", "R-B": "persistent"}
    assert payload["summary"]["by_severity"]["critical"] == 0
    assert payload["summary"]["by_status"]["accepted"] == 1
    assert payload["baseline"]["trend"][-1]["by_severity"]["critical"] == 0
    # Earlier runs are not rewritten.
    assert earlier["summary"]["by_severity"]["critical"] == 1

    with Store(root) as store:
        store.unsuppress(finding_id)
        restored = store.payload()
    assert restored["summary"]["by_severity"]["critical"] == 1
    assert {f["baseline_status"] for f in restored["findings"]} == {"persistent"}


def test_forgetting_a_project_removes_its_history_only(project, isolated_data_dir: Path, capsys):
    root = project("django_app")
    scan(root, [sast("R-A", "a.py", "eval(x)")])
    before = sorted(p.as_posix() for p in root.rglob("*"))
    (item,) = [p for p in list_projects() if p["name"] == "django_app"]

    assert cli.main(["forget", str(root)]) == 2  # without --si nothing is deleted
    assert list_projects()
    assert cli.main(["forget", str(root), "--si"]) == 0
    assert list_projects() == []
    assert sorted(p.as_posix() for p in root.rglob("*")) == before  # the folder, untouched
    assert cli.main(["forget", str(root), "--si"]) == 2

    # An identifier that is not a project never deletes anything else.
    assert forget_project("../..", base=isolated_data_dir) is False
    assert forget_project(item["id"], base=isolated_data_dir) is False
