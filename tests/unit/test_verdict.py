"""H7: vendor-delivery verdict, PIN-protected thresholds, SBOM and PDF."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from helpers import FakeAdapter, make_finding

from heimdall_guardian import cli
from heimdall_guardian.adapters.base import AdapterResult
from heimdall_guardian.core.finding import BaselineStatus, Category, Finding, Origin, Severity
from heimdall_guardian.core.runner import build_plan, run_scan
from heimdall_guardian.core.verdict import Outcome, Thresholds, evaluate, sign
from heimdall_guardian.i18n import render
from heimdall_guardian.report import write_report
from heimdall_guardian.report.html import render_html
from heimdall_guardian.report.pdf import clean
from heimdall_guardian.storage import Store
from heimdall_guardian.storage.thresholds import PinError, ThresholdStore

PIN = "prueba-123456"


def finding(rule: str, severity: Severity, **kwargs) -> Finding:
    category = kwargs.pop("category", Category.SAST)
    status = kwargs.pop("status", BaselineStatus.NEW)
    origin = kwargs.pop("origin", Origin.DETERMINISTIC)
    item = make_finding(
        "uno", rule, "a.py", rule, severity, category=category, module="SAST", **kwargs
    )
    item.baseline_status, item.origin, item.id = status, origin, f"HDL-{rule}"
    return item


def judge(findings: list[Finding], thresholds: Thresholds | None = None):
    return evaluate(
        findings,
        thresholds or Thresholds(),
        issuer="Ana Pérez",
        tree_hash="a" * 64,
        rules_version="abc123",
        issued="2026-10-09T10:00:00-06:00",
    )


def counts(verdict) -> dict[str, int]:
    return {c.key: c.count for c in verdict.criteria}


def test_clean_delivery_is_approved():
    verdict = judge([finding("R-BAJA", Severity.LOW), finding("R-ALTA", Severity.HIGH)])
    assert verdict.outcome is Outcome.APPROVED  # up to 5 high ones are tolerated


@pytest.mark.parametrize(
    ("blocker", "key"),
    [
        (finding("R-CRIT", Severity.CRITICAL), "max_critical"),
        (finding("gitleaks", Severity.HIGH, category=Category.SECRETS), "max_secrets"),
        (finding("DJ-CONF-002", Severity.LOW, category=Category.CONFIGURATION), "max_secrets"),
        (
            finding("AUTHZ-001", Severity.CRITICAL, category=Category.ACCESS_CONTROL),
            "max_unauth_write_endpoints",
        ),
        (
            finding(
                "CVE-1", Severity.CRITICAL, category=Category.DEPENDENCIES, fixed_version="2.2.4"
            ),
            "max_patchable_critical_deps",
        ),
    ],
)
def test_any_zero_threshold_blocks_the_delivery(blocker: Finding, key: str):
    verdict = judge([blocker])
    assert verdict.outcome is Outcome.NOT_APPROVED
    assert counts(verdict)[key] == 1


def test_critical_dependency_without_fix_counts_as_critical_but_not_as_patchable():
    verdict = judge([finding("CVE-2", Severity.CRITICAL, category=Category.DEPENDENCIES)])
    assert counts(verdict)["max_patchable_critical_deps"] == 0
    assert counts(verdict)["max_critical"] == 1


def test_too_many_highs_or_any_medium_means_observations():
    highs = [finding(f"R-{n}", Severity.HIGH) for n in range(6)]
    assert judge(highs).outcome is Outcome.APPROVED_WITH_OBSERVATIONS
    assert judge(highs[:5]).outcome is Outcome.APPROVED
    assert judge([finding("R-M", Severity.MEDIUM)]).outcome is Outcome.APPROVED_WITH_OBSERVATIONS


def test_accepted_risks_and_ai_suggestions_do_not_count():
    accepted = finding("R-CRIT", Severity.CRITICAL, status=BaselineStatus.ACCEPTED)
    false_positive = finding("R-FP", Severity.CRITICAL, status=BaselineStatus.FALSE_POSITIVE)
    suggestion = finding("AI-IDOR-001", Severity.MEDIUM, origin=Origin.AI)
    verdict = judge([accepted, false_positive, suggestion])
    assert verdict.outcome is Outcome.APPROVED
    # What stopped being counted is written in the verdict.
    assert [item["id"] for item in verdict.accepted] == ["HDL-R-CRIT", "HDL-R-FP"]
    with_ai = judge([suggestion], Thresholds(count_ai_findings=True))
    assert with_ai.outcome is Outcome.APPROVED_WITH_OBSERVATIONS


def test_signature_binds_result_to_code_rules_and_issuer():
    verdict = judge([])
    base = ("a" * 64, "abc123", "Ana Pérez", "approved", "2026-10-09T10:00:00-06:00")
    assert verdict.signature == sign(*base)
    for index, other in enumerate(("b" * 64, "zzz", "Otra", "not_approved", "2027")):
        changed = [*base]
        changed[index] = other
        assert sign(*changed) != verdict.signature
    assert verdict.to_dict()["default_thresholds"] is True


def test_thresholds_reject_nonsense():
    with pytest.raises(ValueError, match="desconocido"):
        Thresholds.from_dict({"max_inventado": 1})
    with pytest.raises(ValueError, match="no válido"):
        Thresholds.from_dict({"max_high": -1})
    with pytest.raises(ValueError, match="no válido"):
        Thresholds.from_dict({"max_high": "muchos"})


def test_thresholds_need_pin_and_every_change_is_logged(tmp_path: Path):
    store = ThresholdStore(tmp_path)
    assert store.load() == Thresholds()
    relaxed = Thresholds(max_high=20)
    with pytest.raises(PinError, match="no hay PIN"):
        store.save(relaxed, PIN, "ana")
    with pytest.raises(PinError, match="al menos"):
        store.set_pin("123", "ana")
    store.set_pin(PIN, "ana")
    with pytest.raises(PinError, match="no coincide"):
        store.save(relaxed, "otro-pin-000", "luis")
    assert store.load() == Thresholds()

    store.save(relaxed, PIN, "ana")
    assert store.load().max_high == 20
    with pytest.raises(PinError, match="no coincide"):
        store.set_pin("nuevo-pin-999", "luis", "equivocado")

    history = store.history()
    assert [render(entry["change"]) for entry in history] == [
        "PIN definido",
        "umbrales modificados",
    ]
    assert (history[1]["before"]["max_high"], history[1]["after"]["max_high"]) == (5, 20)
    assert PIN not in (tmp_path / "verdict_thresholds.json").read_text(encoding="utf-8")

    # A damaged file does not relax the verdict: it goes back to the proposal's values.
    (tmp_path / "verdict_thresholds.json").write_text('{"thresholds": {"max_high": -5}}')
    assert store.load() == Thresholds()


def test_vendor_profile_issues_verdict_after_suppressions(project, tmp_path: Path, monkeypatch):
    root = project("php_app")
    critical = finding("PHP-EXE-001", Severity.CRITICAL)
    critical.file, critical.line_start = "index.php", 8
    sbom = {"bomFormat": "CycloneDX", "specVersion": "1.6", "components": [{"name": "php"}]}
    fake = FakeAdapter("uno", AdapterResult(findings=[critical], sbom=sbom))
    monkeypatch.setattr("heimdall_guardian.core.runner.default_adapters", lambda: [fake])
    out = tmp_path / "entrega"
    out.mkdir()
    scan = ["scan", str(root), "--perfil", "vendor", "--emite", "Ana Pérez"]

    assert cli.main([*scan, "--salida", str(out / "uno.json")]) == 0
    first = json.loads((out / "uno.json").read_text(encoding="utf-8"))
    assert first["verdict"]["outcome"] == "not_approved"
    assert first["verdict"]["issuer"] == "Ana Pérez"
    assert first["verdict"]["tree_hash"] == first["project"]["tree_hash"]
    assert first["run"]["rules_version"] == first["verdict"]["rules_version"] != ""

    finding_id = first["findings"][0]["id"]
    with Store(root) as store:
        store.suppress(finding_id, BaselineStatus.ACCEPTED, "Se retira en la entrega 2", "ana")

    # Accepting the risk changes the verdict of the already saved run, without analyzing again.
    assert cli.main(["report", str(root), "--salida", str(out / "tras-aceptar.json")]) == 0
    restated = json.loads((out / "tras-aceptar.json").read_text(encoding="utf-8"))["verdict"]
    assert restated["outcome"] == "approved"
    assert restated["issuer"] == "Ana Pérez"

    outputs = [out / "dos.json", out / "dictamen.pdf", out / "sbom.cdx.json", out / "dos.html"]
    args = [arg for path in outputs for arg in ("--salida", str(path))]
    assert cli.main([*scan, *args]) == 0
    second = json.loads(outputs[0].read_text(encoding="utf-8"))
    assert second["verdict"]["outcome"] == "approved"
    assert [a["id"] for a in second["verdict"]["accepted_findings"]] == [finding_id]
    assert outputs[1].read_bytes().startswith(b"%PDF")
    assert json.loads(outputs[2].read_text(encoding="utf-8")) == sbom
    html = outputs[3].read_text(encoding="utf-8")
    assert "Dictamen de entrega" in html
    assert second["verdict"]["signature"] in html

    # `report` regenerates the saved verdict without analyzing again.
    assert cli.main(["report", str(root), "--corrida", "1", "--salida", str(out / "r.pdf")]) == 0
    assert (out / "r.pdf").stat().st_size > 1500


def test_other_profiles_issue_no_verdict_and_sbom_export_needs_the_module(project, tmp_path):
    plan = build_plan(project("php_app"), profile="standard")
    payload = run_scan(plan, adapters=[]).to_dict()
    assert payload["verdict"] is None
    assert "Dictamen de entrega" not in render_html(payload)
    with pytest.raises(ValueError, match="no generó SBOM"):
        write_report(payload, tmp_path / "x.cdx.json")
    write_report(payload, tmp_path / "sin-dictamen.pdf")
    assert (tmp_path / "sin-dictamen.pdf").read_bytes().startswith(b"%PDF")


def test_pdf_text_survives_characters_outside_latin1():
    assert clean("Inyección — «ñ» … ≤ 5") == "Inyección - «ñ» ... <= 5"
    assert clean("código 日本語 😀") == "código ??? ?"
    assert clean(None) == ""


def test_bases_travel_in_one_archive_and_reject_foreign_content(tmp_path, monkeypatch):
    origin, target = tmp_path / "origin", tmp_path / "destino"
    monkeypatch.setenv("HDL_DATA_DIR", str(origin))
    (origin / "bases" / "trivy" / "db").mkdir(parents=True)
    (origin / "bases" / "trivy" / "db" / "trivy.db").write_bytes(b"datos")
    archive = tmp_path / "bases.tar.gz"
    assert cli.main(["bases", "--exportar", str(archive)]) == 0

    monkeypatch.setenv("HDL_DATA_DIR", str(target))
    assert cli.main(["bases", "--exportar", str(tmp_path / "vacio.tar.gz")]) == 2
    assert cli.main(["bases", "--importar", str(archive)]) == 0
    assert (target / "bases" / "trivy" / "db" / "trivy.db").read_bytes() == b"datos"

    import tarfile

    hostile = tmp_path / "hostil.tar.gz"
    (tmp_path / "x.txt").write_text("x")
    with tarfile.open(hostile, "w:gz") as tar:
        tar.add(tmp_path / "x.txt", arcname="../fuera.txt")
    assert cli.main(["bases", "--importar", str(hostile)]) == 2
    assert not (tmp_path / "fuera.txt").exists()


def test_old_vulnerability_database_is_declared(project):
    class Stale(FakeAdapter):
        def db_updated_at(self) -> str | None:
            return "2026-01-01T00:00:00.123456789Z"

    result = run_scan(build_plan(project("php_app"), profile="quick"), adapters=[Stale("vieja")])
    assert any(
        "base de vulnerabilidades de vieja tiene" in render(text) for text in result.limitations
    )


def test_ui_states_the_delivery_verdict_in_plain_words():
    from heimdall_guardian.ui import model as m

    blocked = judge([finding("R-CRIT", Severity.CRITICAL)]).to_dict()
    headline, why = m.verdict({}, blocked)
    assert headline == "La entrega no se puede recibir."
    assert "hallazgos críticos (1, máximo 0)" in why
    assert m.verdict({}, judge([]).to_dict()) == (
        "La entrega se puede recibir.",
        "No rebasa ningún umbral del dictamen.",
    )


def test_update_bases_downloads_every_supported_ecosystem_without_a_project(monkeypatch):
    from heimdall_guardian.storage import bases

    calls: list[tuple[list[str], dict]] = []

    class Done:
        returncode, stdout, stderr = 0, "", ""

    def fake_run(cmd, *, cwd, env=None, timeout=0, heartbeat=None):
        probe = Path(cmd[-1])
        calls.append((cmd, {"env": env, "files": sorted(p.name for p in probe.iterdir())}))
        return Done()

    monkeypatch.setattr(bases, "find_binary", lambda name: f"/bin/{name}")
    monkeypatch.setattr(bases, "run", fake_run)
    messages: list[str] = []
    assert bases.update_bases(messages.append) == {
        "trivy": bases.UPDATED,
        "osv": bases.UPDATED,
    }
    assert render(bases.UPDATED) == "actualizada"
    # The size notice, then one line per database with its step.
    assert len(messages) == 3
    assert "2 GB" in messages[0]
    assert "(1 de 2)" in messages[1]
    assert "(2 de 2)" in messages[2]

    (trivy, _), (osv, extra) = calls
    assert "--download-db-only" in trivy
    assert "--download-offline-databases" in osv
    assert "--no-resolve" in osv  # nor here are external services queried needlessly
    assert "OSV_SCANNER_LOCAL_DB_CACHE_DIRECTORY" in extra["env"]
    # One manifest per ecosystem: Python, Node, PHP, .NET, Go, Rust, Ruby, Pub, Maven and Swift.
    assert extra["files"] == sorted(bases._PROBE_FILES)
    assert len(extra["files"]) == 10

    monkeypatch.setattr(bases, "find_binary", lambda name: None)
    assert bases.update_bases() == {
        "trivy": bases.NOT_INSTALLED,
        "osv": bases.NOT_INSTALLED,
    }


def test_trivy_downloads_do_not_use_docker_credentials(tmp_path):
    """With Docker Desktop installed, Trivy called a helper missing from the app's PATH."""
    from heimdall_guardian.adapters.base import anonymous_registry_env

    env = anonymous_registry_env(tmp_path)
    config_dir = Path(env["DOCKER_CONFIG"])
    assert config_dir.is_dir()
    assert not list(config_dir.iterdir())  # empty: no credsStore and no credentials
    assert config_dir.is_relative_to(tmp_path)
