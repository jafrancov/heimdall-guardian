"""Messages per language: catalogs, `t()`, language priority and English configuration."""

from __future__ import annotations

import ast
import tomllib
from pathlib import Path

import pytest

from heimdall_guardian import i18n
from heimdall_guardian.core import config as config_module
from heimdall_guardian.core.config import (
    TEMPLATE,
    ConfigError,
    LegacyConfigError,
    load_config,
    save_config,
)
from heimdall_guardian.i18n import languages, messages
from heimdall_guardian.ui import model as ui_model

_REAL_MACOS_LANGUAGE = languages._macos_language
_REAL_DEFAULT_LANGUAGE = languages.DEFAULT_LANGUAGE

SRC = Path(__file__).resolve().parents[2] / "src"


@pytest.fixture(autouse=True)
def _restore_language(monkeypatch):
    monkeypatch.setattr(languages, "_current", "es")
    monkeypatch.setattr(languages, "DEFAULT_LANGUAGE", _REAL_DEFAULT_LANGUAGE)
    monkeypatch.setattr(languages, "_override", None)
    for var in ("HDL_LANG", "LC_ALL", "LC_MESSAGES", "LANG"):
        monkeypatch.delenv(var, raising=False)


def test_catalogs_have_same_keys_and_placeholders():
    en, es = messages.CATALOGS["en"], messages.CATALOGS["es"]
    assert en.keys() == es.keys()
    for key in en:
        assert messages.placeholders(en[key]) == messages.placeholders(es[key]), key
        assert en[key].strip(), key
        assert es[key].strip(), key


def test_translations_fall_back_to_english_and_then_to_the_key(monkeypatch):
    monkeypatch.setitem(messages.CATALOGS["en"], "test.only_en", "Hello {who}")
    assert i18n.t("test.only_en", lang="es", who="Ana") == "Hello Ana"
    assert i18n.t("test.missing.key") == "test.missing.key"
    assert i18n.t("lang.name.en", lang="es") == "Inglés"
    assert i18n.t("lang.name.en", lang="en") == "English"
    i18n.set_language("en")
    assert i18n.t("lang.name.es") == "Spanish"
    assert i18n.t("lang.name.es", lang="xx") == "Spanish"  # unknown language: English


# Functions whose first argument is a catalog key (`msg` and the adapter errors
# store the key in the run; `tn` uses it with `.one`/`.other`).
_KEY_FUNCTIONS = {"t", "_t", "tn", "msg", "AdapterError", "MissingDatabaseError"}


def _called_name(node: ast.Call) -> str | None:
    if isinstance(node.func, ast.Name):
        return node.func.id
    return node.func.attr if isinstance(node.func, ast.Attribute) else None


def _key_exists(key: str) -> bool:
    return i18n.has_message(key) or i18n.has_message(f"{key}.one")


def test_every_key_used_in_the_code_exists():
    used: list[tuple[str, str]] = []
    for path in SRC.rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            is_key_call = (
                isinstance(node, ast.Call)
                and _called_name(node) in _KEY_FUNCTIONS
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            )
            if is_key_call:
                used.append((str(path.relative_to(SRC)), node.args[0].value))  # type: ignore[attr-defined]
    assert used  # the walk finds at least one use
    missing = [(f, k) for f, k in used if not _key_exists(k)]
    assert not missing, missing


def test_message_keys_built_at_runtime_exist():
    """Key families built with f-strings: one per possible value."""
    from heimdall_guardian import cli
    from heimdall_guardian.core import owasp
    from heimdall_guardian.core.profiles import CUSTOM_PROFILE, PROFILES
    from heimdall_guardian.report import text as report_text

    keys = [
        f"owasp.{c.code}.{part}"
        for c in owasp.CATEGORIES
        for part in ("name", "explanation", "example", "coverage_note")
    ]
    keys += [f"owasp.coverage.{level}" for level in owasp.COVERAGE_LEVELS]
    keys += [f"owasp.hint.{cwe}" for cwe in owasp.hinted_cwes()]
    keys += [
        f"verdict.criterion.{key}"
        for key in (
            "max_critical",
            "max_secrets",
            "max_unauth_write_endpoints",
            "max_patchable_critical_deps",
            "max_high",
        )
    ]
    keys += [
        f"report.light.{c}{suffix}"
        for c in ("rojo", "amarillo", "verde")
        for suffix in ("", ".text")
    ]
    keys += [f"ui.profile.{code}.name" for code in (*PROFILES, CUSTOM_PROFILE)]
    keys += [
        f"cli.{group}.{key}" for group in ("baseline", "databases") for key in ("export", "import")
    ]
    keys += [f"ui.thresholds.{name}" for name in cli._THRESHOLD_OPTIONS if name.startswith("max_")]
    keys += [f"report.tool_status.{s}" for s in report_text._TOOL_STATUS.values()]
    keys += [f"report.ai.verdict.{v}" for v in ("likely_real", "likely_false", "uncertain")]
    keys += [f"report.ai.level.{v}" for v in ("high", "medium", "low")]
    keys += [f"report.ai.risk_level.{v}" for v in ("high", "medium", "low", "none")]
    missing = [key for key in keys if not i18n.has_message(key)]
    assert not missing, missing


def test_label_follows_the_current_language():
    assert i18n.label("critical", "severity") == "CRÍTICA"
    i18n.set_language("en")
    assert i18n.label("critical", "severity") == "CRITICAL"
    assert i18n.label("critical", "severity", lang="es") == "CRÍTICA"


def test_set_language_rejects_unsupported():
    with pytest.raises(ValueError, match="no soportado"):
        i18n.set_language("fr")
    assert i18n.set_language("EN") == "en"
    assert i18n.normalize("es_MX.UTF-8") == "es"
    assert i18n.normalize("fr_FR") is None


def test_language_priority(monkeypatch):
    # with nothing: the default, English
    assert languages.DEFAULT_LANGUAGE == _REAL_DEFAULT_LANGUAGE == "en"
    assert i18n.resolve_language() == "en"
    # system
    monkeypatch.setenv("LANG", "en_US.UTF-8")
    assert i18n.resolve_language() == "en"
    # config wins over the system
    assert i18n.resolve_language(config="es") == "es"
    # environment variable wins over config
    monkeypatch.setenv("HDL_LANG", "en")
    assert i18n.resolve_language(config="es") == "en"
    monkeypatch.setenv("HDL_LANG", "es")
    assert i18n.resolve_language(config="en") == "es"
    # argument wins over everything
    assert i18n.resolve_language("en", config="es") == "en"
    # an invalid environment or config value is ignored
    monkeypatch.setenv("HDL_LANG", "fr")
    assert i18n.resolve_language(config="en") == "en"
    with pytest.raises(ValueError, match="no soportado"):
        i18n.resolve_language("fr")
    # a system in another language falls back to the default
    monkeypatch.delenv("HDL_LANG")
    monkeypatch.setenv("LANG", "fr_FR.UTF-8")
    assert i18n.resolve_language() == "en"


def test_override_from_the_command_line_survives_reapplying(monkeypatch):
    monkeypatch.setenv("HDL_LANG", "es")
    i18n.set_override("en")
    assert i18n.apply_language(config="es") == "en"
    assert i18n.get_language() == "en"


# ------------------------------------------------------------ configuration


def test_template_uses_english_keys_and_loads(tmp_path: Path):
    parsed = tomllib.loads(TEMPLATE)
    assert set(parsed) == {"general", "exclusions", "llm", "databases", "rules"}
    assert set(parsed["general"]) == {"default_profile", "language", "onboarding_seen"}
    assert {"paths", "exclude_extra", "include_extra", "max_file_size_kb"} == set(
        parsed["exclusions"]
    )
    assert set(parsed["databases"]) == {"alert_age_days"}
    llm = parsed["llm"]
    assert {"enabled", "active_destination", "fallback_destination", "allowed_hosts"} <= set(llm)
    assert {"internal_ca", "temperature", "max_targets_per_run", "timeout_per_target_s"} <= set(llm)
    assert set(llm["destinations"][0]) == {
        "name",
        "url",
        "runtime",
        "requires_token",
        "context_tokens",
        "model_triage",
        "model_endpoints",
        "model_summary",
        "model_sinks",
        "model_consensus",
        "reasoning",
    }
    path = tmp_path / "config.toml"
    path.write_text(TEMPLATE, encoding="utf-8")
    config = load_config(path)
    assert config.general.language == ""
    assert config.llm.active_destination == "laptop"
    assert config.llm.fallback_destination == config_module.NO_FALLBACK


def test_language_in_config_is_validated(tmp_path: Path):
    path = tmp_path / "config.toml"
    path.write_text('[general]\nlanguage = "en"\n')
    assert load_config(path).general.language == "en"
    path.write_text('[general]\nlanguage = "fr"\n')
    with pytest.raises(ConfigError, match="language"):
        load_config(path)


@pytest.mark.parametrize(
    "old",
    [
        '[exclusiones]\nrutas = ["x"]\n',
        "[bases]\nalerta_antiguedad_dias = 3\n",
        '[general]\nperfil_por_defecto = "quick"\n',
        "[llm]\ntemperatura = 0.1\n",
        '[[llm.destinos]]\nnombre = "a"\nurl = "http://localhost:1/v1"\n',
    ],
)
def test_old_spanish_config_is_rejected_with_a_clear_message(tmp_path: Path, old: str):
    path = tmp_path / "config.toml"
    path.write_text(old)
    with pytest.raises(LegacyConfigError, match="versión anterior") as info:
        load_config(path)
    assert "hdl config --init" in str(info.value)


def test_saving_over_an_old_config_keeps_a_backup(tmp_path: Path):
    path = tmp_path / "config.toml"
    old = '[general]\nperfil_por_defecto = "quick"\n'
    path.write_text(old)
    save_config(config_module.Config(), path)
    assert (tmp_path / "config.toml.v1.bak").read_text() == old
    assert load_config(path).general.default_profile == "standard"


def test_ui_starts_with_defaults_and_a_notice_on_an_old_config(isolated_data_dir, monkeypatch):
    from heimdall_guardian.core.paths import config_path

    config_path().parent.mkdir(parents=True, exist_ok=True)
    config_path().write_text('[exclusiones]\nrutas = ["x"]\n')
    config, notice = ui_model.load_startup_config()
    assert config == config_module.Config()
    assert notice is not None
    assert str(config_path()) in notice


def test_change_language_saves_it_and_applies_it(isolated_data_dir):
    from heimdall_guardian.core.paths import config_path

    config, notice = ui_model.load_startup_config()
    assert notice is None
    updated = ui_model.change_language(config, "en")
    assert i18n.get_language() == "en"
    assert updated.general.language == "en"
    assert load_config(config_path()).general.language == "en"
    # on starting again, what was stored is respected
    i18n.set_language("es")
    ui_model.load_startup_config()
    assert i18n.get_language() == "en"


# --------------------------------------------------------------- plurals


def test_tn_picks_one_or_other(monkeypatch):
    assert (
        i18n.tn("ui.bases.updated_ago", 1) == "Bases de vulnerabilidades actualizadas hace 1 día."
    )
    assert i18n.tn("ui.bases.updated_ago", 0).endswith("hace 0 días.")
    assert i18n.tn("ui.bases.updated_ago", 3, lang="en") == (
        "Vulnerability databases updated 3 days ago."
    )
    assert i18n.tn("ui.coverage.open", 1, lang="en") == "1 open"


def test_every_plural_key_has_both_forms():
    for catalog in messages.CATALOGS.values():
        stems = {k.rsplit(".", 1)[0] for k in catalog if k.endswith((".one", ".other"))}
        for stem in stems:
            assert f"{stem}.one" in catalog
            assert f"{stem}.other" in catalog


# ----------------------------------------------------- system language (macOS)


class _Done:
    def __init__(self, stdout: str, returncode: int = 0):
        self.stdout, self.returncode = stdout, returncode


def test_macos_preferred_language_is_used_without_lang_variables(monkeypatch):
    calls = []

    def run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        return _Done('(\n    "en-MX",\n    "es-MX"\n)\n')

    monkeypatch.setattr(languages.sys, "platform", "darwin")
    monkeypatch.setattr(languages.subprocess, "run", run)
    monkeypatch.setattr(languages, "_macos_language", _REAL_MACOS_LANGUAGE)
    monkeypatch.setattr(languages.locale, "getlocale", lambda: (None, None))
    assert i18n.resolve_language() == "en"
    cmd, kwargs = calls[0]
    assert cmd == ["/usr/bin/defaults", "read", "-g", "AppleLanguages"]
    assert kwargs["timeout"] <= 5
    assert "shell" not in kwargs
    # LANG, if present, takes priority
    monkeypatch.setenv("LANG", "es_MX.UTF-8")
    assert i18n.resolve_language() == "es"


@pytest.mark.parametrize(
    "outcome",
    [
        _Done('(\n    "fr-FR"\n)'),
        _Done("", 1),
        OSError("no defaults"),
        languages.subprocess.TimeoutExpired("defaults", 2),
    ],
)
def test_macos_language_failures_fall_back_to_the_default(monkeypatch, outcome):
    def run(cmd, **kwargs):
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    monkeypatch.setattr(languages.sys, "platform", "darwin")
    monkeypatch.setattr(languages.subprocess, "run", run)
    monkeypatch.setattr(languages, "_macos_language", _REAL_MACOS_LANGUAGE)
    monkeypatch.setattr(languages.locale, "getlocale", lambda: (None, None))
    assert i18n.resolve_language() == "en"


def test_macos_language_is_not_asked_on_other_platforms(monkeypatch):
    monkeypatch.setattr(languages.sys, "platform", "linux")
    monkeypatch.setattr(
        languages.subprocess, "run", lambda *a, **k: pytest.fail("no debe consultarse")
    )
    assert _REAL_MACOS_LANGUAGE() is None


# ------------------------------------------- no text without catalog in the interface

_SPANISH_LETTERS = set("áéíóúñ¿¡ÁÉÍÓÚÑ")
# Loose literals (from any file) allowed outside `t()`: none. The
# exceptions go per file in `_ALLOWED_LITERALS`, with their reason.
_ALLOWED_SPANISH: set[str] = set()


def _docstring_nodes(tree: ast.AST) -> set[int]:
    ids: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            body = node.body
            if (
                body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                ids.add(id(body[0].value))
    return ids


def _spanish_literals(path: Path) -> list[tuple[int, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    skip = _docstring_nodes(tree)
    return [
        (node.lineno, node.value)
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and id(node) not in skip
        and _SPANISH_LETTERS & set(node.value)
        and node.value not in _ALLOWED_SPANISH
    ]


@pytest.mark.parametrize("name", ["app.py", "model.py"])
def test_ui_has_no_spanish_literals_outside_the_catalog(name: str):
    offenders = _spanish_literals(SRC / "heimdall_guardian" / "ui" / name)
    assert not offenders, offenders


# Spanish texts allowed outside the catalog, per file, with their reason. They are
# compared by prefix.
_ALLOWED_LITERALS: dict[str, list[tuple[str, str]]] = {
    "core/palette.py": [
        (
            "Los elementos gráficos de HEIMDALL",
            "ART_NOTICE: debe aparecer tal cual, en español, en README, NOTICE y «Acerca de»",
        ),
    ],
}


def _checked_files() -> list[str]:
    root = SRC / "heimdall_guardian"
    files = [
        path
        for folder in ("core", "report", "storage", "adapters", "authz")
        for path in sorted((root / folder).glob("*.py"))
    ]
    files += [
        root / "llm" / "module.py",
        root / "llm" / "destinations.py",
        root / "llm" / "schemas.py",
    ]
    files += [root / "llm" / "client.py", root / "cli.py"]
    return [path.relative_to(root).as_posix() for path in files]


@pytest.mark.parametrize("name", _checked_files())
def test_core_has_no_spanish_literals_outside_the_catalog(name: str):
    allowed = _ALLOWED_LITERALS.get(name, [])
    offenders = [
        (line, text)
        for line, text in _spanish_literals(SRC / "heimdall_guardian" / name)
        if not any(text.startswith(prefix) for prefix, _ in allowed)
    ]
    assert not offenders, offenders


def test_every_allowed_literal_still_exists():
    """An exception that is no longer used is deleted, so the list does not fill with leftovers."""
    for name, entries in _ALLOWED_LITERALS.items():
        found = [text for _, text in _spanish_literals(SRC / "heimdall_guardian" / name)]
        for prefix, _ in entries:
            assert any(text.startswith(prefix) for text in found), (name, prefix)


def _literals_outside(path: Path, variable: str) -> list[tuple[int, str]]:
    """Literals with Spanish letters outside the `variable` dictionary (e.g. `_ES`)."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    inside: set[int] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.AnnAssign | ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == variable
                for target in ([node.target] if isinstance(node, ast.AnnAssign) else node.targets)
            )
            and node.value is not None
        ):
            inside |= {id(child) for child in ast.walk(node.value)}
    skip = _docstring_nodes(tree)
    return [
        (node.lineno, node.value)
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and id(node) not in skip
        and id(node) not in inside
        and _SPANISH_LETTERS & set(node.value)
    ]


def test_prompts_keep_spanish_only_in_their_own_language_table():
    """The Spanish of the prompts lives in `_ES`; the rest of the module has no literals."""
    path = SRC / "heimdall_guardian" / "llm" / "prompts.py"
    assert not _literals_outside(path, "_ES")
    assert _spanish_literals(path), "`_ES` should contain Spanish text"
