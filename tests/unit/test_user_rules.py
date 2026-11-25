"""The user's own rules: config, structural checks, engine validation and `hdl rules`."""

from __future__ import annotations

from pathlib import Path

import pytest

from heimdall_guardian import cli, i18n
from heimdall_guardian.adapters.base import ScanContext, find_binary
from heimdall_guardian.adapters.opengrep import OpengrepAdapter, rules_version
from heimdall_guardian.core.config import RulesConfig, dump_config, load_config
from heimdall_guardian.core.files import Exclusions, scan_tree
from heimdall_guardian.core.profiles import Module
from heimdall_guardian.core.runner import build_plan, run_scan
from heimdall_guardian.core.user_rules import check_user_rules, own_rule_ids
from heimdall_guardian.i18n import render

GOOD = """\
rules:
  - id: ACME-SQL-001
    languages: [python]
    severity: ERROR
    message: Do not call dangerous().
    pattern: dangerous(...)
    metadata:
      cwe: "CWE-89"
      owasp: "A05:2025 Injection"
      severity_hdl: high
      confidence: medium
      title: "Dangerous call"
      recommendation: "Remove it."
"""


@pytest.fixture(autouse=True)
def _english():
    i18n.set_override(None)
    i18n.set_language("en")
    yield
    i18n.set_override(None)
    i18n.set_language("es")


def _write(folder: Path, name: str, text: str) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / name
    path.write_text(text, encoding="utf-8")
    return path


def _check(folder: Path, root: Path | None = None, own: set[str] | None = None):
    return check_user_rules([folder], analyzed_root=root, own_ids=own or set())


def _texts(result) -> str:
    return "\n".join(render(p.message) for p in result.problems)


def test_config_round_trip(tmp_path):
    from dataclasses import replace

    config = replace(
        load_config(tmp_path / "none.toml"), rules=RulesConfig(extra_dirs=("~/rules", "/x/y"))
    )
    path = tmp_path / "config.toml"
    path.write_text(dump_config(config), encoding="utf-8")
    assert load_config(path).rules.extra_dirs == ("~/rules", "/x/y")
    assert load_config(tmp_path / "none.toml").rules.extra_dirs == ()


def test_valid_rule_is_accepted_and_spanish_texts_are_optional(tmp_path):
    path = _write(tmp_path / "rules", "a.yaml", GOOD)
    result = _check(tmp_path / "rules")
    assert result.problems == ()
    assert result.files == (path.resolve(),)
    assert result.ids == ("ACME-SQL-001",)


def test_missing_metadata_rejects_the_whole_file(tmp_path):
    text = GOOD.replace('      cwe: "CWE-89"\n', "")
    _write(tmp_path / "r", "a.yaml", text + GOOD.split("rules:\n")[1].replace("001", "002"))
    result = _check(tmp_path / "r")
    assert result.files == ()
    assert result.ids == ()
    assert "metadata.cwe" in _texts(result)
    assert "ACME-SQL-001" in _texts(result)


@pytest.mark.parametrize("bad", ["acme-sql-1", "ACME-001", "ACME-SQL-0001"])
def test_bad_id(tmp_path, bad):
    _write(tmp_path / "r", "a.yml", GOOD.replace("ACME-SQL-001", bad))
    assert "the ID must look like" in _texts(_check(tmp_path / "r"))


def test_id_colliding_with_a_builtin_rule(tmp_path):
    assert "PHP-SQL-001" in own_rule_ids()
    _write(tmp_path / "r", "a.yaml", GOOD.replace("ACME-SQL-001", "PHP-SQL-001"))
    result = _check(tmp_path / "r", own=own_rule_ids())
    assert "already used by a built-in rule" in _texts(result)


@pytest.mark.parametrize("reserved", ["AI-SQL-001", "ACME-CAND-001"])
def test_reserved_prefix_and_tag(tmp_path, reserved):
    _write(tmp_path / "r", "a.yaml", GOOD.replace("ACME-SQL-001", reserved))
    assert "reserved" in _texts(_check(tmp_path / "r"))


def test_duplicate_id_across_files(tmp_path):
    _write(tmp_path / "r", "a.yaml", GOOD)
    _write(tmp_path / "r", "b.yaml", GOOD)
    result = _check(tmp_path / "r")
    assert len(result.files) == 1
    assert "more than once" in _texts(result)


def test_owasp_2021_label_is_rejected_with_the_2025_one(tmp_path):
    _write(tmp_path / "r", "a.yaml", GOOD.replace("A05:2025 Injection", "A03:2021 Injection"))
    text = _texts(_check(tmp_path / "r"))
    assert "2021" in text
    assert "A05:2025 Injection" in text


def test_bad_severity_confidence_and_matcher(tmp_path):
    text = GOOD.replace("severity_hdl: high", "severity_hdl: huge").replace(
        "    pattern: dangerous(...)\n", ""
    )
    _write(tmp_path / "r", "a.yaml", text)
    shown = _texts(_check(tmp_path / "r"))
    assert "severity_hdl" in shown
    assert "needs `pattern`" in shown


def test_folder_inside_the_analyzed_project_is_ignored(tmp_path):
    root = tmp_path / "proj"
    _write(root / ".rules", "a.yaml", GOOD)
    result = _check(root / ".rules", root)
    assert result.files == ()
    assert "inside the analyzed project" in _texts(result)
    # The same folder is fine when it is not under the project.
    assert _check(root / ".rules", tmp_path / "other").files


def test_missing_folder_is_reported(tmp_path):
    assert "does not exist" in _texts(_check(tmp_path / "nope"))


def test_invalid_yaml_and_empty_rules(tmp_path):
    _write(tmp_path / "r", "a.yaml", "rules: [")
    _write(tmp_path / "r", "b.yaml", "rules: []\n")
    shown = _texts(_check(tmp_path / "r"))
    assert "not valid YAML" in shown
    assert "non-empty" in shown


def test_plan_carries_files_and_problems_as_limitations(tmp_path):
    root = tmp_path / "proj"
    _write(root, "app.py", "dangerous(1)\n")
    _write(tmp_path / "ok", "a.yaml", GOOD)
    plan = build_plan(
        root, profile="quick", extra_rule_dirs=[str(tmp_path / "ok"), str(tmp_path / "gone")]
    )
    assert len(plan.user_rules) == 1
    result = run_scan(plan, adapters=[])
    assert any(m["code"] == "core.limit.user_rule_problem" for m in result.limitations)
    assert result.to_dict()["user_rules"] == []  # nothing ran, so nothing is claimed


def test_rules_version_changes_with_user_rules(tmp_path):
    path = _write(tmp_path, "a.yaml", GOOD)
    assert rules_version() == rules_version([])
    assert rules_version([path]) != rules_version()


def test_hdl_rules_exit_codes(tmp_path, capsys):
    _write(tmp_path / "good", "a.yaml", GOOD)
    _write(tmp_path / "bad", "a.yaml", GOOD.replace("A05:2025", "A03:2021"))
    assert cli.main(["--lang", "en", "rules", "--check", "--dir", str(tmp_path / "bad")]) == 1
    assert "INVALID" in capsys.readouterr().out
    code = cli.main(["--lang", "en", "reglas", "--dir", str(tmp_path / "good")])
    out = capsys.readouterr().out
    assert "ACME-SQL-001" in out
    assert code == 0


def test_hdl_rules_without_folders(capsys):
    assert cli.main(["--lang", "en", "rules"]) == 0
    assert "No extra rule folders" in capsys.readouterr().out


needs_engine = pytest.mark.skipif(find_binary("opengrep") is None, reason="opengrep not installed")


@needs_engine
def test_engine_invalid_rule_is_dropped_and_valid_one_finds(tmp_path):
    root = tmp_path / "proj"
    _write(root, "app.py", "dangerous(1)\n")
    rules = tmp_path / "rules"
    _write(rules, "good.yaml", GOOD)
    _write(
        rules,
        "broken.yaml",
        GOOD.replace("ACME-SQL-001", "ACME-SQL-002").replace("dangerous(...)", "foo("),
    )
    plan = build_plan(root, profile="standard", extra_rule_dirs=[str(rules)])
    assert len(plan.user_rules) == 2  # both pass the structural check
    exclusions = Exclusions(dirs=())
    ctx = ScanContext(
        root=root,
        files=scan_tree(root, exclusions).files,
        modules=frozenset({Module.SAST}),
        stacks=frozenset(),
        exclusions=exclusions,
        workdir=tmp_path / "work",
        user_rules=plan.user_rules,
    )
    (tmp_path / "work").mkdir()
    result = OpengrepAdapter().invoke(ctx)
    assert [p.name for p in result.rule_files] == ["good.yaml"]
    assert any(m["code"] == "adapter.opengrep.user_rule_invalid" for m in result.limitations)
    assert [f.rule_id for f in result.findings] == ["ACME-SQL-001"]


def test_validate_timeout_is_an_error_not_a_hang(tmp_path, monkeypatch):
    import subprocess

    from heimdall_guardian.adapters import base
    from heimdall_guardian.adapters.opengrep import VALIDATE_TIMEOUT_SECONDS, validate_rule_files

    seen: list[object] = []

    def fake_run(cmd, **kwargs):
        seen.append(kwargs.get("timeout"))
        raise subprocess.TimeoutExpired(cmd, kwargs.get("timeout"))

    monkeypatch.setattr(base.subprocess, "run", fake_run)
    rule = _write(tmp_path, "a.yaml", GOOD)
    with pytest.raises(base.AdapterError) as error:
        validate_rule_files([rule], tmp_path, binary="opengrep")
    assert error.value.message["code"] == "adapter.timeout"
    assert seen == [VALIDATE_TIMEOUT_SECONDS] == [120]


def test_hdl_rules_reports_a_validate_timeout(tmp_path, monkeypatch, capsys):
    from heimdall_guardian.adapters.base import AdapterError

    def timed_out(*_args, **_kwargs):
        raise AdapterError("adapter.timeout", seconds=120)

    monkeypatch.setattr(cli, "validate_rule_files", timed_out)
    _write(tmp_path / "good", "a.yaml", GOOD)
    assert cli.main(["--lang", "en", "rules", "--dir", str(tmp_path / "good")]) == 0
    captured = capsys.readouterr()
    assert "time limit exceeded" in captured.err
