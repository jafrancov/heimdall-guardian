"""The CLI in the chosen language: help, messages and Spanish aliases."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from helpers import FakeAdapter, make_finding

from heimdall_guardian import cli, i18n
from heimdall_guardian.adapters.base import AdapterResult
from heimdall_guardian.core.finding import BaselineStatus, Confidence, Severity
from heimdall_guardian.core.profiles import profile_name


@pytest.fixture(autouse=True)
def _reset_language():
    i18n.set_override(None)
    yield
    i18n.set_override(None)
    i18n.set_language("es")


def _help(capsys, *argv: str) -> str:
    with pytest.raises(SystemExit) as stop:
        cli.main([*argv, "--help"])
    assert stop.value.code == 0
    return capsys.readouterr().out


def test_help_comes_out_in_the_chosen_language(capsys):
    english = _help(capsys, "--lang", "en")
    assert "static security analysis of source code" in english
    assert "análisis estático" not in english
    spanish = _help(capsys, "--lang", "es")
    assert "análisis estático de seguridad" in spanish
    assert "static security analysis" not in spanish

    scan_en = _help(capsys, "--lang", "en", "scan")
    assert "--profile" in scan_en
    assert (
        "analyzes a folder" not in scan_en
    )  # that phrase belongs to the listing, not to `scan --help`
    assert "project folder (never modified)" in scan_en
    scan_es = _help(capsys, "--idioma", "es", "scan")
    assert "carpeta del proyecto (nunca se modifica)" in scan_es
    assert scan_es.index("--perfil") < scan_es.index("--profile")  # the language one goes first
    assert scan_en.index("--profile") < scan_en.index("--perfil")


def test_language_is_decided_before_the_parser_is_built(capsys, monkeypatch):
    monkeypatch.setenv("HDL_LANG", "es")
    assert "static security" in _help(capsys, "--lang", "en")
    assert "análisis estático" in _help(capsys)  # without --lang, HDL_LANG decides


def test_unsupported_language_is_a_usage_error(capsys):
    with pytest.raises(SystemExit) as stop:
        cli.main(["--lang", "fr", "tools"])
    assert stop.value.code == 2
    assert "fr" in capsys.readouterr().err


CASES = [
    (["scan", "x", "--profile", "vendor", "--output", "a.json", "--update-databases"],
     ["scan", "x", "--perfil", "proveedor", "--salida", "a.json", "--actualizar-bases"]),
    (["scan", "x", "--exclude", "a", "--include", "b", "--ai", "n", "--issuer", "Ana",
      "--no-baseline", "--modules", "SEC"],
     ["scan", "x", "--excluir", "a", "--incluir", "b", "--ia", "n", "--emite", "Ana",
      "--sin-linea-base", "--modulos", "SEC"]),
    (["report", "x", "--run", "3", "--output", "r.html"],
     ["report", "x", "--corrida", "3", "--salida", "r.html"]),
    (["forget", "x", "--yes"], ["forget", "x", "--si"]),
    (["suppress", "x", "HDL-1", "--status", "accepted", "--reason", "m", "--review", "2099-01-01"],
     ["suppress", "x", "HDL-1", "--estado", "aceptado", "--motivo", "m",
      "--revisar", "2099-01-01"]),
    (["tools", "--news"], ["tools", "--novedades"]),
    (["databases", "--update", "--export", "b.tgz"],
     ["bases", "--actualizar", "--exportar", "b.tgz"]),
    (["baseline", "x", "--import", "b.json"], ["baseline", "x", "--importar", "b.json"]),
    (["llm", "--destination", "d", "--save-token"], ["llm", "--destino", "d", "--guardar-token"]),
    (["thresholds", "--set-pin", "--log", "--max-critical", "1", "--count-ai-findings", "yes"],
     ["thresholds", "--definir-pin", "--bitacora", "--max-criticos", "1",
      "--contar-hallazgos-ia", "si"]),
]  # fmt: skip


@pytest.mark.parametrize("lang", ["en", "es"])
@pytest.mark.parametrize(("english", "spanish"), CASES)
def test_english_names_and_spanish_aliases_parse_the_same(lang, english, spanish):
    i18n.set_language(lang)
    parser = cli._parser()
    new, old = parser.parse_args(english), parser.parse_args(spanish)
    old.command = cli._COMMAND_ALIASES.get(old.command, old.command)
    new.command = cli._COMMAND_ALIASES.get(new.command, new.command)
    assert vars(new) == vars(old)


def test_profile_and_status_values_accept_both_languages():
    parser = cli._parser()
    profiles = {"quick": "rapido", "standard": "estandar", "full": "completo",
                "vendor": "proveedor", "custom": "personalizado"}  # fmt: skip
    for english, spanish in profiles.items():
        for value in (english, spanish, english.upper()):
            assert parser.parse_args(["scan", "x", "--profile", value]).profile == english
    for value in ("accepted", "aceptado"):
        args = parser.parse_args(["suppress", "x", "i", "--status", value, "--reason", "r"])
        assert args.status is BaselineStatus.ACCEPTED
    for value in ("false_positive", "false-positive", "falso-positivo"):
        args = parser.parse_args(["suppress", "x", "i", "--status", value, "--reason", "r"])
        assert args.status is BaselineStatus.FALSE_POSITIVE
    with pytest.raises(SystemExit):
        parser.parse_args(["scan", "x", "--profile", "turbo"])


def test_spanish_aliases_keep_working(project, tmp_path: Path, capsys, monkeypatch):
    root = project("php_app")
    out = tmp_path / "r.json"
    code = cli.main(["scan", str(root), "--perfil", "rapido", "--salida", str(out)])
    assert code == 0
    assert json.loads(out.read_text(encoding="utf-8"))["run"]["profile"] == "quick"
    assert cli.main(["forget", str(root)]) == 2  # without --si nothing is deleted
    assert cli.main(["forget", str(root), "--si"]) == 0
    assert cli.main(["tools"]) == 0

    calls: list[object] = []
    monkeypatch.setattr(cli, "update_bases", lambda say, **_: calls.append(say) or {})
    assert cli.main(["bases", "--actualizar"]) == 0
    assert cli.main(["databases", "--update"]) == 0
    assert len(calls) == 2


def test_scan_prints_summary_and_limitations_in_english(project, tmp_path, capsys, monkeypatch):
    root = project("dotnet_app")
    finding = make_finding("fake", "R-1", "a.cs", "x()", Severity.HIGH)
    # AI triage skips high-confidence findings; a medium one still yields the "no model" note.
    finding.confidence = Confidence.MEDIUM
    fake = FakeAdapter("fake", AdapterResult(findings=[finding]))
    monkeypatch.setattr("heimdall_guardian.core.runner.default_adapters", lambda: [fake])
    out = tmp_path / "b.json"
    assert cli.main(["--lang", "en", "scan", str(root), "--profile", "full",
                     "--output", str(out)]) == 0  # fmt: skip
    err = capsys.readouterr().err
    for expected in ("Folder:", "Profile:  Full", "Files:", "finding(s)", "Open: ",
                     "HIGH 1", "Run 1: ", "Limitation: ", "Report:"):  # fmt: skip
        assert expected in err, expected
    for spanish in ("Carpeta", "Perfil", "Abiertos", "Limitación", "Corrida", "hallazgo"):
        assert spanish not in err

    assert cli.main(["--lang", "es", "scan", str(root), "--perfil", "completo",
                     "--salida", str(out)]) == 0  # fmt: skip
    err = capsys.readouterr().err
    for expected in ("Carpeta:", "Perfil:   Completo", "Archivos:", "hallazgo(s)", "Abiertos: ",
                     "ALTA 1", "Limitación: ", "Reporte:"):  # fmt: skip
        assert expected in err, expected


def test_errors_and_confirmations_follow_the_language(project, capsys):
    root = project("php_app")
    assert cli.main(["--lang", "en", "forget", str(root)]) == 2
    err = capsys.readouterr().err
    assert err.startswith("Error: This deletes")
    assert "--yes" in err
    assert cli.main(["--lang", "es", "forget", str(root)]) == 2
    err = capsys.readouterr().err
    assert "Esto borra" in err
    assert "--si" in err
    assert cli.main(["--lang", "en", "scan", str(root), "--modules", "SEC"]) == 2
    assert "--modules only applies with --profile custom" in capsys.readouterr().err
    assert cli.main(["--lang", "en", "runs", str(root)]) == 0
    assert "There are no saved runs" in capsys.readouterr().out


def test_tools_and_thresholds_in_english(capsys):
    assert cli.main(["--lang", "en", "tools"]) == 0
    out = capsys.readouterr().out
    assert "not installed" in out or "unknown version" in out or "." in out
    assert "no instalado" not in out
    assert cli.main(["--lang", "en", "thresholds"]) == 0
    out = capsys.readouterr().out
    assert "max-critical = 0" in out
    assert "max-high = 5" in out
    assert "count-ai-findings = False" in out
    assert cli.main(["--lang", "es", "thresholds"]) == 0
    assert "max-altos = 5" in capsys.readouterr().out


def test_databases_state_in_english(capsys, tmp_path):
    assert cli.main(["--lang", "en", "databases"]) == 0
    assert "Location: " in capsys.readouterr().out


def test_ai_progress_is_structured_and_follows_the_language(capsys, monkeypatch):
    class Tty:
        def __init__(self) -> None:
            self.text = ""

        def isatty(self) -> bool:
            return True

        def write(self, value: str) -> int:
            self.text += value
            return len(value)

        def flush(self) -> None:
            return None

    for lang, expected in (("en", "AI: reviewing 3 of 9"), ("es", "IA: revisando 3 de 9")):
        i18n.set_language(lang)
        tty = Tty()
        monkeypatch.setattr("sys.stderr", tty)
        cli._progress("llm", i18n.msg("core.ai.progress", done=3, total=9))
        assert expected in tty.text


def test_report_shows_the_profile_name_in_both_languages(project):
    from heimdall_guardian.core.runner import build_plan, run_scan
    from heimdall_guardian.report import write_report

    root = project("php_app")
    payload = run_scan(build_plan(root, profile="standard"), adapters=[]).to_dict()
    for lang, name in (("es", "Estándar"), ("en", "Standard")):
        i18n.set_language(lang)
        assert profile_name("standard") == name
        out = root.parent / f"r-{lang}.html"
        write_report(payload, out)
        assert f"<dd>{name} (" in out.read_text(encoding="utf-8")


def test_language_errors_come_from_the_catalog():
    i18n.set_language("en")
    with pytest.raises(ValueError, match="Unsupported language") as exc:
        i18n.set_language("fr")
    assert "en, es" in str(exc.value)
    i18n.set_language("es")
    with pytest.raises(ValueError, match="Idioma no soportado"):
        i18n.set_language("fr")
