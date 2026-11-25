"""Git-aware scoping: `.env` rules only for versioned files, `--exclude-gitignored`, exact files."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest

from heimdall_guardian import cli
from heimdall_guardian.adapters.opengrep import parse_report
from heimdall_guardian.core.config import ExclusionsConfig
from heimdall_guardian.core.files import Exclusions, scan_tree
from heimdall_guardian.core.presets import ignored_entries
from heimdall_guardian.core.profiles import Module
from heimdall_guardian.core.runner import _plan_limitations, build_plan
from heimdall_guardian.i18n import render, set_language

needs_git = pytest.mark.skipif(shutil.which("git") is None, reason="git is not installed")


def _git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(root), "-c", "user.email=t@t", "-c", "user.name=t", *args],
        check=True,
        capture_output=True,
    )


def _item(root: Path, name: str) -> dict[str, Any]:
    return {
        "check_id": "rules.heimdall.php.PHP-CONF-001",
        "path": str(root / name),
        "start": {"line": 1},
        "end": {"line": 1},
        "extra": {
            "lines": "DB_PASSWORD=hunter2",
            "message": "m",
            "severity": "ERROR",
            "metadata": {"versioned_only": [".env", ".env.*"], "severity_hdl": "high"},
        },
    }


def _repo(tmp_path: Path) -> Path:
    root = tmp_path / "proj"
    root.mkdir()
    (root / ".gitignore").write_text(".env.local\nlogs/\n")
    (root / ".env").write_text("DB_PASSWORD=hunter2\n")
    (root / ".env.local").write_text("DB_PASSWORD=hunter2\n")
    (root / "app.php").write_text("<?php\n")
    (root / "logs").mkdir()
    (root / "logs" / "app.log").write_text("x\n")
    _git(root, "init", "-q")
    _git(root, "add", ".gitignore", ".env", "app.php")
    _git(root, "commit", "-q", "-m", "init")
    return root


@needs_git
def test_untracked_env_is_dropped_and_tracked_kept(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    data = {"results": [_item(root, ".env"), _item(root, ".env.local")]}
    untracked: list[str] = []
    found = parse_report(data, root, frozenset({Module.CONF}), untracked)
    assert [f.file for f in found] == [".env"]
    assert untracked == [".env.local"]


def test_outside_git_env_findings_are_kept(tmp_path: Path) -> None:
    root = tmp_path / "plain"
    root.mkdir()
    (root / ".env").write_text("X=1\n")
    untracked: list[str] = []
    found = parse_report(
        {"results": [_item(root, ".env")]}, root, frozenset({Module.CONF}), untracked
    )
    assert len(found) == 1
    assert untracked == []


def test_without_a_list_nothing_is_filtered(tmp_path: Path) -> None:
    found = parse_report(
        {"results": [_item(tmp_path, ".env.local")]}, tmp_path, frozenset({Module.CONF})
    )
    assert len(found) == 1


def test_rule_declares_versioned_only() -> None:
    text = (
        Path(__file__).parents[2] / "rules" / "heimdall" / "php" / "PHP-CONF-001.yaml"
    ).read_text()
    assert "versioned_only:" in text


@needs_git
def test_ignored_entries_in_git(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    entries, source = ignored_entries(root)
    assert source == "git"
    assert {"logs", ".env.local"} <= set(entries)
    assert ".env" not in entries


def test_ignored_entries_fall_back_to_gitignore(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text("logs/\n/out\n*.tmp\n")
    entries, source = ignored_entries(tmp_path)
    assert source == "gitignore"
    assert entries == ["logs", "out"]


@needs_git
def test_exclude_gitignored_flag_skips_ignored(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _repo(tmp_path)
    (root / "composer.json").write_text("{}")
    assert (
        cli.main(["scan", str(root), "--profile", "quick", "--dry-run", "--exclude-gitignored"])
        == 0
    )
    out = capsys.readouterr()
    assert "logs/app.log" not in out.out
    assert ".env.local" not in out.out.split('"files"')[1]
    assert "logs" in out.out  # recorded as an exclusion
    assert "git" in out.err


@needs_git
def test_exclude_gitignored_spanish_alias(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _repo(tmp_path)
    assert (
        cli.main(["scan", str(root), "--perfil", "quick", "--dry-run", "--excluir-ignorados"]) == 0
    )
    assert "logs/app.log" not in capsys.readouterr().out


def test_exclude_gitignored_never_skips_manifests(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text("{}")
    cfg = ExclusionsConfig().to_exclusions(("package.json",), root=tmp_path)
    assert cfg.paths == ("package.json",)
    assert not cfg.excludes_file("package.json")
    assert scan_tree(tmp_path, cfg).analyzable == ["package.json"]


def test_exclude_names_an_existing_file(tmp_path: Path) -> None:
    (tmp_path / "web" / "js").mkdir(parents=True)
    (tmp_path / "web" / "js" / "big.js").write_text("x")
    (tmp_path / "web" / "js" / "keep.js").write_text("x")
    (tmp_path / "other").mkdir()
    (tmp_path / "other" / "big.js").write_text("x")
    ex = ExclusionsConfig().to_exclusions(("web/js/big.js", "./web/js/../js/zz.js"), root=tmp_path)
    assert ex.paths == ("web/js/big.js",)
    assert "web/js/big.js" not in ex.dirs
    info = scan_tree(tmp_path, ex)
    assert info.pattern_skipped == ["web/js/big.js"]
    assert {"other/big.js", "web/js/keep.js"} <= set(info.analyzable)
    # Secrets are still searched in it.
    assert not ex.excludes("web/js/big.js", secret=True)
    assert ex.excludes("web/js/big.js")
    # Paths outside the folder are never taken.
    assert ExclusionsConfig().to_exclusions(("../x",), root=tmp_path).paths == ()


def test_exact_file_shows_in_plan_and_limitation(tmp_path: Path) -> None:
    (tmp_path / "a.js").write_text("x")
    ex = ExclusionsConfig().to_exclusions(("a.js",), root=tmp_path)
    plan = build_plan(tmp_path, profile="quick", exclusions=ex)
    assert "a.js" in plan.to_dict()["exclusions"]
    assert plan.tree.pattern_skipped == ["a.js"]


@pytest.mark.parametrize("lang", ["en", "es"])
def test_limitations_do_not_repeat_examples_marker(tmp_path: Path, lang: str) -> None:
    for name in ("a.spec.ts", "b.spec.ts", "c.spec.ts", "d.spec.ts"):
        (tmp_path / name).write_text("x")
    plan = build_plan(tmp_path, profile="quick", exclusions=Exclusions(files=("*.spec.ts",)))
    set_language(lang)
    try:
        texts = [render(m) for m in _plan_limitations(plan)]
        texts.append(
            render(
                {
                    "code": "core.limit.untracked_versioned",
                    "params": {
                        "count": 2,
                        "examples": {"code": "core.examples.few", "params": {"paths": [".env"]}},
                    },
                }
            )
        )
    finally:
        set_language("en")
    joined = " ".join(texts)
    assert "e.g." in joined or "p. ej." in joined
    assert "e.g. e.g." not in joined
    assert "p. ej. p. ej." not in joined
