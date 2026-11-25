"""E1: what is stored or exported uses only English keys and codes."""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path
from typing import Any

import pytest
from helpers import FakeAdapter
from test_llm import REVIEW_IDOR, TRIAGE_OK, FakeClient, runner, sql_finding

from heimdall_guardian import cli
from heimdall_guardian.adapters.base import AdapterResult
from heimdall_guardian.authz.adapter import AuthzAdapter
from heimdall_guardian.core.finding import BaselineStatus
from heimdall_guardian.core.paths import data_dir
from heimdall_guardian.core.profiles import canonical_profile, profile_name, resolve
from heimdall_guardian.core.runner import build_plan, run_scan
from heimdall_guardian.core.verdict import Thresholds
from heimdall_guardian.i18n import languages, render
from heimdall_guardian.report import write_report
from heimdall_guardian.storage import Store, load_project_exclusions, save_project_exclusions
from heimdall_guardian.storage.thresholds import ThresholdStore

# Single words (separated by "_") that give away a Spanish key.
SPANISH_WORDS = frozenset(
    """
hallazgos hallazgo resumen linea archivo archivos ruta nombre estado perfil modulos modulo
herramientas herramienta limitaciones dictamen criterio criterios umbrales umbral corrida
inicio fin proyecto severidad categoria origen detalle duracion tendencia corregidos
metodos manejador evidencia escritura requiere tiene riesgo veredicto explicacion
correccion sugerida confianza consenso coincide modelo idioma texto tarea firma emite
fecha resultado encontrados maximo rebasado esquema huella formato supresiones
justificacion autor cambio antes despues omitir incluir exclusiones regla fuente
revision revisar medios abiertos aceptados impide recibir propuesta base actualizada
analizados grandes omitidos tamano enlaces simbolicos ignorados
    """.split()  # noqa: SIM905
)
SKIPPED = {"sbom"}  # CycloneDX: its keys are those of the standard


def key_problems(node: Any, path: str = "") -> list[str]:
    """Keys with non-ASCII characters or with typical Spanish words."""
    problems: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            where = f"{path}/{key}"
            words = set(re.split(r"[_\-\s]+", str(key).lower()))
            if not str(key).isascii() or words & SPANISH_WORDS:
                problems.append(where)
            if key not in SKIPPED:
                problems += key_problems(value, where)
    elif isinstance(node, list):
        for item in node:
            problems += key_problems(item, f"{path}[]")
    return problems


def test_key_check_catches_spanish_keys():
    assert key_problems({"a": [{"hallazgos": 1}], "por_estado": {}, "ok": {"año": 1}})


def test_saved_run_payload_uses_only_english_keys(project, tmp_path: Path, monkeypatch):
    root = project("authz_django")
    client = FakeClient({"T1": TRIAGE_OK, "T2": {**REVIEW_IDOR, "flow_risk": "medium"},
                         "T3": {"summary": "Estado general: requiere atención."}})  # fmt: skip
    extra = sql_finding()
    sbom = {"bomFormat": "CycloneDX", "specVersion": "1.6", "components": [{"name": "php"}]}
    adapters = [FakeAdapter("uno", AdapterResult(findings=[extra], sbom=sbom)), AuthzAdapter()]
    plan = build_plan(root, profile="vendor")
    result = run_scan(plan, adapters=adapters, ai=runner(client, tmp_path=tmp_path))
    with Store(root) as store:
        store.record(result, thresholds=Thresholds(), issuer="Ana")
        store.suppress(result.findings[0].id, BaselineStatus.ACCEPTED, "Se retira", "ana")
        saved = store.payload()
        listed = store.runs() + store.suppressions()
        exported = tmp_path / "baseline.json"
        store.export_baseline(exported)

    assert key_problems(saved) == []
    assert key_problems(result.to_dict()) == []
    assert key_problems(listed) == []
    assert key_problems(json.loads(exported.read_text())) == []
    # The parts that used to be in Spanish, with their new name.
    assert saved["run"]["profile"] == "vendor"
    assert {t["status"] for t in saved["tools"]} <= {"ran", "skipped", "error"}
    assert saved["verdict"]["criteria"][0]["criterion"]["code"].startswith("verdict.criterion.")
    assert saved["ai_summary"]["text"].startswith("Estado general")
    assert "requires_auth" in saved["endpoints"][0]
    assert any(f["llm_assessment"] for f in saved["findings"])
    assessments = [f["llm_assessment"] for f in saved["findings"] if f["llm_assessment"]]
    assert all({"task", "model", "language"} <= set(a) for a in assessments)

    # All formats are generated from that dictionary (inventory, AI and verdict included).
    for name in ("r.html", "r.pdf", "r.xlsx", "r.sarif", "r.json"):
        write_report(saved, tmp_path / name)
        assert (tmp_path / name).stat().st_size > 500
    sarif = json.loads((tmp_path / "r.sarif").read_text(encoding="utf-8"))
    properties = sarif["runs"][0]["results"][0]["properties"]
    assert key_problems(properties) == []
    assert {"severity", "category", "origin", "baseline_status"} <= set(properties)
    html = (tmp_path / "r.html").read_text(encoding="utf-8")
    assert "Estado general: requiere atención." in html


def test_plan_dict_and_project_listing_use_english_keys(project):
    root = project("php_app")
    plan = build_plan(root, profile="quick")
    assert key_problems(plan.to_dict()) == []
    result = run_scan(plan, adapters=[])
    with Store(root) as store:
        store.record(result)
    from heimdall_guardian.storage import list_projects

    assert key_problems(list_projects()) == []


def test_cli_json_report_has_only_english_keys(project, tmp_path: Path):
    out = tmp_path / "r.json"
    assert cli.main(["scan", str(project("php_app")), "--profile", "quick", "--output",
                     str(out)]) == 0  # fmt: skip
    assert key_problems(json.loads(out.read_text(encoding="utf-8"))) == []


# ------------------------------------------------------------ archiving old data


def test_legacy_project_exclusions_are_archived_and_announced(project):
    root = project("php_app")
    with Store(root) as store:
        directory = store.directory
    legacy = directory / "exclusiones.json"
    legacy.write_text('{"omitir": ["vendor2"], "incluir": []}', encoding="utf-8")

    assert load_project_exclusions(root) == ((), ())  # the old format is not interpreted
    assert not legacy.exists()
    assert (directory / "exclusiones.json.v1.bak").read_text(encoding="utf-8").startswith("{")

    save_project_exclusions(root, ["vendor2"], ["build"])
    saved = json.loads((directory / "exclusions.json").read_text(encoding="utf-8"))
    assert saved == {"exclude": ["vendor2"], "include": ["build"]}
    assert load_project_exclusions(root) == (("vendor2",), ("build",))

    result = run_scan(build_plan(root, profile="quick"), adapters=[])
    with Store(root) as store:
        store.record(result)
    notices = [render(item) for item in result.limitations]
    assert any("exclusiones.json.v1.bak" in text for text in notices)


def test_legacy_exclusions_notice_survives_until_the_next_run(project):
    root = project("php_app")
    with Store(root) as store:
        directory = store.directory
    (directory / "exclusiones.json").write_text('{"omitir": []}', encoding="utf-8")
    with Store(root) as store:  # opening the project also sets the file aside
        assert any("exclusiones" in render(n) for n in store.archive_notices)
    assert (directory / "exclusiones.json.v1.bak").is_file()


def test_legacy_threshold_files_are_archived_and_the_pin_is_dropped(tmp_path: Path):
    (tmp_path / "dictamen.json").write_text(
        json.dumps({"umbrales": {"max_altos": 99}, "pin": {"sal": "00", "hash": "x"}}),
        encoding="utf-8",
    )
    (tmp_path / "dictamen-bitacora.jsonl").write_text('{"fecha": "x"}\n', encoding="utf-8")

    store = ThresholdStore(tmp_path)
    assert not store.has_pin()
    assert store.load() == Thresholds()  # the verdict is not relaxed with old data
    assert len(store.notices) == 1
    text = render(store.notices[0])
    assert "dictamen.json.v1.bak" in text
    assert "PIN" in text
    assert (tmp_path / "dictamen.json.v1.bak").is_file()
    assert (tmp_path / "dictamen-bitacora.jsonl.v1.bak").is_file()
    assert not (tmp_path / "dictamen.json").exists()

    store.set_pin("pin-seguro-1", "ana")
    store.save(Thresholds(max_high=7), "pin-seguro-1", "ana")
    data = json.loads((tmp_path / "verdict_thresholds.json").read_text(encoding="utf-8"))
    assert key_problems(data) == []
    assert data["thresholds"]["max_high"] == 7
    assert set(data["pin"]) == {"salt", "hash"}
    assert key_problems(store.history()) == []
    assert ThresholdStore(tmp_path).notices == []  # it only warns the time it archives


def test_old_baseline_database_is_archived_as_a_new_schema(project):
    root = project("php_app")
    with Store(root) as store:
        directory = store.directory
    with sqlite3.connect(directory / "baseline.db") as db:
        db.execute("PRAGMA user_version = 4")
    db.close()
    with Store(root) as store:
        assert any("baseline.db.v4.bak" in render(n) for n in store.archive_notices)
    assert (directory / "baseline.db.v4.bak").is_file()


def test_project_file_uses_english_keys(project):
    root = project("php_app")
    with Store(root) as store:
        info = json.loads((store.directory / "project.json").read_text(encoding="utf-8"))
    assert set(info) == {"name", "key", "path"}


# ---------------------------------------------------------------- profiles and language


def test_profile_codes_are_english_and_spanish_names_are_aliases():
    assert canonical_profile("Rapido") == "quick"
    spanish = ("estandar", "completo", "proveedor", "personalizado")
    assert [canonical_profile(p) for p in spanish] == ["standard", "full", "vendor", "custom"]
    assert resolve("estandar") == resolve("standard")
    assert profile_name("estandar") == profile_name("standard")
    assert canonical_profile("unknown") == "unknown"


def test_default_language_is_english_when_nothing_else_applies(monkeypatch):
    monkeypatch.undo()  # without the test settings
    assert languages.DEFAULT_LANGUAGE == "en"
    for var in ("HDL_LANG", "LC_ALL", "LC_MESSAGES", "LANG"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr(languages, "_macos_language", lambda: None)
    monkeypatch.setattr(languages.locale, "getlocale", lambda: (None, None))
    assert languages.resolve_language() == "en"


def test_spanish_profile_in_old_config_still_loads(tmp_path: Path):
    from heimdall_guardian.core.config import load_config

    path = tmp_path / "config.toml"
    path.write_text('[general]\ndefault_profile = "estandar"\n', encoding="utf-8")
    assert canonical_profile(load_config(path).general.default_profile) == "standard"


@pytest.mark.usefixtures("isolated_data_dir")
def test_data_dir_files_have_english_names():
    store = ThresholdStore()
    store.set_pin("pin-seguro-1", "ana")
    assert {p.name for p in data_dir().iterdir()} == {
        "verdict_thresholds.json",
        "verdict_thresholds_log.jsonl",
    }
