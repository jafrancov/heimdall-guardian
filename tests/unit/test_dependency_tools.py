"""Pure parts of tools/check_outdated.py and tools/try_upgrade.py (no network, no uv)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

TOOLS = Path(__file__).resolve().parents[2] / "tools"


def _load(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, TOOLS / f"{name}.py")
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def outdated() -> ModuleType:
    return _load("check_outdated")


@pytest.fixture(scope="module")
def upgrade() -> ModuleType:
    return _load("try_upgrade")


def test_direct_dependencies_cover_project_extras_and_groups(outdated: ModuleType) -> None:
    pyproject = {
        "project": {
            "dependencies": ["PyYAML>=6"],
            "optional-dependencies": {"ui": ["flet[all]>=1.0"]},
        },
        "dependency-groups": {"dev": ["ruff>=0.6", {"include-group": "docs"}]},
    }
    found = outdated.direct_dependencies(pyproject)
    assert found == {"pyyaml": "project", "flet": "extra ui", "ruff": "group dev"}


def test_parse_pip_outdated_keeps_direct_and_marks_major_jumps(outdated: ModuleType) -> None:
    text = json.dumps(
        [
            {"name": "Pillow", "version": "12.3.0", "latest_version": "13.0.0"},
            {"name": "ruff", "version": "0.16.10", "latest_version": "0.17.6"},
            {"name": "transitive", "version": "1.0", "latest_version": "2.0"},
        ]
    )
    rows = outdated.parse_pip_outdated(text, {"pillow": "group dev", "ruff": "group dev"})
    assert [(r["name"], r["jump"]) for r in rows] == [("pillow", "MAJOR"), ("ruff", "")]


def test_parse_actions_reads_sha_comments_and_plain_tags(outdated: ModuleType) -> None:
    sha = "a" * 40
    text = (
        f"      - uses: actions/checkout@{sha} # v4\n"
        "      - uses: astral-sh/setup-uv@v5\n"
        "        uses: github/codeql-action/analyze@v3\n"
    )
    assert outdated.parse_actions([text]) == {
        "actions/checkout": "v4",
        "astral-sh/setup-uv": "v5",
        "github/codeql-action": "v3",
    }


def test_action_report_compares_majors_and_tolerates_errors(outdated: ModuleType) -> None:
    def fetch(url: str):
        if "broken" in url:
            raise OSError("rate limited")
        return {"tag_name": "v5.1.0" if "newer" in url else "v4.2.0"}

    rows = outdated.action_report(
        {"o/newer": "v4", "o/same": "v4", "o/broken": "v4", "o/branch": "release/v1"}, fetch
    )
    state = {r["name"]: (r["outdated"], bool(r["error"])) for r in rows}
    assert state == {
        "o/branch": ("", True),
        "o/broken": ("", True),
        "o/newer": ("yes", False),
        "o/same": ("", False),
    }


def test_render_reports_offline_and_strict_signal(outdated: ModuleType) -> None:
    text, flagged = outdated.render(([], "network down"), [], [])
    assert "could not check" in text
    assert not flagged
    _, flagged = outdated.render(
        ([], ""), [{"name": "t", "current": "1", "latest": "2", "error": "", "outdated": "yes"}], []
    )
    assert flagged


def test_rewrite_flet_pin_changes_every_platform(upgrade: ModuleType) -> None:
    text = (
        '[tool.flet.macos]\ndependencies = ["flet==1.0.4"]\n\n'
        '[tool.flet.linux]\ndependencies = ["flet==1.0.4"]\n\n'
        '[project]\ndependencies = ["flet>=1.0"]\n'
    )
    out = upgrade.rewrite_flet_pin(text, "1.1.3")
    assert out.count("flet==1.1.3") == 2
    assert 'dependencies = ["flet>=1.0"]' in out


def test_changes_and_app_build_hint(upgrade: ModuleType) -> None:
    before = {"flet": "1.0.4", "ruff": "0.16.10", "same": "1", "gone": "1"}
    after = {"flet": "1.1.3", "ruff": "0.17.6", "same": "1", "fresh": "2"}
    assert upgrade.changes(before, after) == [
        "flet: 1.0.4 -> 1.1.3",
        "fresh: (new) -> 2",
        "gone: 1 -> (removed)",
        "ruff: 0.16.10 -> 0.17.6",
    ]
    assert upgrade.needs_app_build(before, after)
    assert not upgrade.needs_app_build({"ruff": "1"}, {"ruff": "2"})


def test_locked_versions_and_lock_command(upgrade: ModuleType) -> None:
    lock = '[[package]]\nname = "flet"\nversion = "1.0.4"\n\n[[package]]\nname = "heimdall"\n'
    assert upgrade.locked_versions(lock) == {"flet": "1.0.4"}
    assert upgrade.lock_command([]) == ["uv", "lock", "--upgrade"]
    assert upgrade.lock_command(["a", "b"]) == [
        "uv",
        "lock",
        "--upgrade-package",
        "a",
        "--upgrade-package",
        "b",
    ]
