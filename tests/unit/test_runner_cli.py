from __future__ import annotations

import json
from pathlib import Path

from helpers import FakeAdapter, make_finding

from heimdall_guardian import cli
from heimdall_guardian.adapters.base import AdapterResult
from heimdall_guardian.core.finding import Category, Severity
from heimdall_guardian.core.runner import SCHEMA_VERSION, build_plan, run_scan
from heimdall_guardian.i18n import render

SECRET = "AKIAIOSFODNN7EXAMPLE"


def test_run_scan_merges_masks_filters_and_survives_failures(project):
    root = project("django_app")
    dep = {"category": Category.DEPENDENCIES}
    one = FakeAdapter(
        "uno",
        AdapterResult(
            findings=[
                make_finding(
                    "uno", "CVE-1", "requirements.txt", "Django@2.2.0", Severity.MEDIUM, **dep
                ),
                make_finding("uno", "R-SAST", "app/tests/test_x.py", "eval(x)", Severity.HIGH),
                make_finding("uno", "R-VENDOR", "vendor/lib/a.py", "eval(x)", Severity.HIGH),
            ],
            secrets={SECRET},
        ),
    )
    two = FakeAdapter(
        "dos",
        AdapterResult(
            findings=[
                make_finding(
                    "dos", "CVE-1", "requirements.txt", "Django@2.2.0", Severity.HIGH, **dep
                ),
                make_finding("dos", "R-KEY", "app/views.py", f'k = "{SECRET}"', Severity.LOW),
            ]
        ),
    )
    missing = FakeAdapter("ausente", available=False)
    broken = FakeAdapter("rota", error="explotó")

    plan = build_plan(root, profile="full")
    result = run_scan(plan, adapters=[one, two, missing, broken])

    assert [f.rule_id for f in result.findings] == ["CVE-1", "R-KEY"]
    merged, key = result.findings
    assert merged.severity is Severity.HIGH
    assert merged.detected_by == ["dos", "uno"]
    assert SECRET not in key.snippet
    assert "AKIA****MPLE" in key.snippet
    assert [f.id for f in result.findings] == [
        f"HDL-{result.started.year}-000001",
        f"HDL-{result.started.year}-000002",
    ]
    assert {t.name: t.status for t in result.tools} == {
        "uno": "ran",
        "dos": "ran",
        "ausente": "skipped",
        "rota": "error",
        "llm": "skipped",  # the full profile asks for AI and none was configured
    }
    text = " ".join(render(m) for m in result.limitations)
    assert "IA desactivada" in text
    assert "ausente no está instalado" in text
    assert "rota falló" in text

    # P1: the working directory stays outside the analyzed folder and is removed.
    workdir = one.contexts[0].workdir
    assert not workdir.is_relative_to(plan.root)
    assert not workdir.exists()

    payload = json.dumps(result.to_dict(), ensure_ascii=False)
    assert SECRET not in payload
    assert len(result.to_dict()["project"]["tree_hash"]) == 64


def test_cli_dry_run_lists_files_without_running_tools(project, capsys, monkeypatch):
    root = project("php_app")
    monkeypatch.setattr(cli, "run_scan", lambda *a, **k: (_ for _ in ()).throw(AssertionError))
    assert cli.main(["scan", str(root), "--perfil", "quick", "--dry-run"]) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["files"] == ["composer.json", "index.php"]
    assert plan["modules"] == ["CONF", "DEP", "SEC"]
    assert plan["stack"][0]["stack"] == "php"


def test_cli_refuses_to_write_inside_analyzed_folder(project, capsys):
    root = project("php_app")
    code = cli.main(["scan", str(root), "--salida", str(root / "reporte.json")])
    assert code == 2
    assert "dentro de la carpeta analizada" in capsys.readouterr().err
    assert not (root / "reporte.json").exists()


def test_cli_rejects_modules_without_custom_profile(project, capsys):
    assert cli.main(["scan", str(project("php_app")), "--modulos", "SEC"]) == 2
    assert "personalizado" in capsys.readouterr().err


def test_cli_scan_writes_normalized_json(project, tmp_path: Path, monkeypatch):
    root = project("dotnet_app")
    fake = FakeAdapter(
        "falsa",
        AdapterResult(
            findings=[
                make_finding(
                    "falsa",
                    "NET-DES-001",
                    "Controllers/DataController.cs",
                    "new BinaryFormatter()",
                    Severity.HIGH,
                )
            ]
        ),
    )
    monkeypatch.setattr("heimdall_guardian.core.runner.default_adapters", lambda: [fake])
    output = tmp_path / "salida.json"
    assert cli.main(["scan", str(root), "--salida", str(output)]) == 0
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["schema"] == SCHEMA_VERSION
    assert data["summary"]["by_severity"]["high"] == 1
    assert data["findings"][0]["origin"] == "deterministic"
    assert data["findings"][0]["baseline_status"] == "new"
    assert data["stack"] == [{"stack": "dotnet", "evidence": "App.csproj"}]


def test_folders_chosen_by_the_user_are_skipped(project, tmp_path, capsys):
    from heimdall_guardian.storage import load_project_exclusions, save_project_exclusions

    root = project("php_app")
    (root / "generado").mkdir()
    (root / "generado" / "salida.php").write_text("<?php echo 1;")
    (root / "build").mkdir()
    (root / "build" / "app.php").write_text("<?php echo 1;")

    def files(*extra: str) -> list[str]:
        assert cli.main(["scan", str(root), "--perfil", "quick", "--dry-run", *extra]) == 0
        return json.loads(capsys.readouterr().out)["files"]

    assert files() == ["composer.json", "generado/salida.php", "index.php"]  # build: by default
    assert files("--excluir", "generado") == ["composer.json", "index.php"]
    assert "build/app.php" in files("--incluir", "build")

    # What was chosen in the application is remembered per project and also applies in the CLI.
    save_project_exclusions(root, ["generado"], [])
    assert load_project_exclusions(root) == (("generado",), ())
    assert files() == ["composer.json", "index.php"]
    assert not list(root.rglob("exclusiones.json"))  # it is saved outside the analyzed folder


def test_missing_vulnerability_database_is_explained_once_and_does_not_look_like_a_crash(project):
    from heimdall_guardian.adapters.base import MissingDatabaseError, missing_database

    class NoDatabase(FakeAdapter):
        def invoke(self, ctx):
            raise MissingDatabaseError()

    plan = build_plan(project("django_app"), profile="quick")
    result = run_scan(plan, adapters=[NoDatabase("trivy"), NoDatabase("osv")])
    assert result.limitations.count(missing_database()) == 1
    assert not any("falló" in render(text) for text in result.limitations)
    assert "Actualizar las bases al analizar" in render(missing_database())
    assert "--actualizar-bases" in render(missing_database())


def test_trivy_still_reviews_configuration_without_a_database(project, tmp_path, monkeypatch):
    from heimdall_guardian.adapters.base import ScanContext, missing_database
    from heimdall_guardian.adapters.trivy import TrivyAdapter
    from heimdall_guardian.core.files import Exclusions
    from heimdall_guardian.core.profiles import Module

    adapter = TrivyAdapter()
    asked: list[list[str]] = []
    monkeypatch.setattr(adapter, "_run", lambda ctx, name, options: asked.append(options) or {})
    assert adapter.has_database() is False  # the test's data directory is empty
    ctx = ScanContext(
        root=project("django_app"),
        files=[],
        modules=frozenset({Module.DEP, Module.CONF}),
        stacks=frozenset(),
        exclusions=Exclusions(),
        workdir=tmp_path,
    )
    result = adapter.invoke(ctx)
    assert asked == [["--scanners", "misconfig", "--format", "json"]]
    assert result.limitations == [missing_database()]


def test_findings_in_skipped_folders_are_explained_and_not_counted(project):
    """A tool may read bin/ or obj/; what it finds there does not count and is reported."""
    dep: dict = {"category": Category.DEPENDENCIES, "module": "DEP"}
    kept = make_finding("osv", "CVE-1", "requirements.txt", "django@2.2.0", Severity.HIGH, **dep)
    hidden = [
        make_finding(
            "osv", f"CVE-{n}", "App/obj/project.assets.json", f"pkg@{n}", Severity.HIGH, **dep
        )
        for n in range(2, 5)
    ]
    plan = build_plan(project("django_app"), profile="quick")
    result = run_scan(plan, adapters=[FakeAdapter("osv", AdapterResult(findings=[kept, *hidden]))])

    assert [f.rule_id for f in result.findings] == ["CVE-1"]
    assert [t.findings for t in result.tools if t.name == "osv"] == [1]  # not 4
    text = " ".join(render(m) for m in result.limitations)
    assert "3 hallazgo(s) de las herramientas quedaron fuera" in text
    assert "App/obj/project.assets.json" in text


def test_cli_lang_option_and_config_init_write_english_keys(isolated_data_dir, capsys):
    from heimdall_guardian import i18n
    from heimdall_guardian.core.paths import config_path

    i18n.set_override(None)
    assert cli.main(["--lang", "en", "config", "--init"]) == 0
    assert i18n.get_language() == "en"
    text = config_path().read_text(encoding="utf-8")
    for expected in ("[exclusions]", "default_profile", "[[llm.destinations]]"):
        assert expected in text
    assert "exclusiones" not in text
    assert cli.main(["--idioma", "es", "config"]) == 0
    assert i18n.get_language() == "es"
    i18n.set_override(None)


def test_cli_dry_run_prints_suggested_folders(tmp_path, capsys):
    root = tmp_path / "web"
    (root / ".next").mkdir(parents=True)
    (root / "package.json").write_text('{"name": "x"}')
    assert cli.main(["--lang", "en", "scan", str(root), "--profile", "quick", "--dry-run"]) == 0
    err = capsys.readouterr().err
    assert "Suggested to skip: .next (Usual in node projects), e.g. .next" in err
    assert "--exclude NAME" in err


def test_cli_dry_run_prints_subprojects(tmp_path, capsys):
    root = tmp_path / "multi"
    for name in ("api/package.json", "ios/Package.swift", "backend/package.json"):
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text("{}")
    assert cli.main(["--lang", "en", "scan", str(root), "--profile", "quick", "--dry-run"]) == 0
    err = capsys.readouterr().err
    assert "This folder holds 3 projects: api (node), backend (node), ios (swift)." in err
    assert "hdl scan" in err
