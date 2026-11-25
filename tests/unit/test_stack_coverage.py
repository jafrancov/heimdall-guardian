"""Detection of more stacks, per-stack coverage and partial OSV databases."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

import pytest
import yaml
from helpers import FakeAdapter

from heimdall_guardian.adapters.base import MissingDatabaseError, missing_database
from heimdall_guardian.adapters.osv import _ECOSYSTEM_DB
from heimdall_guardian.core.coverage import COVERAGE, coverage_notes
from heimdall_guardian.core.detector import Stack, detect
from heimdall_guardian.core.runner import build_plan, run_scan
from heimdall_guardian.i18n import render
from heimdall_guardian.storage.bases import _PROBE_FILES


def _stacks(root: Path, files: dict[str, str]) -> set[Stack]:
    for name, content in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    return {hit.stack for hit in detect(root, list(files))}


@pytest.mark.parametrize(
    ("files", "expected"),
    [
        ({"tsconfig.json": "{}"}, Stack.TYPESCRIPT),
        ({"src/app.tsx": ""}, Stack.TYPESCRIPT),
        ({"main.dart": ""}, Stack.DART),
        ({"pubspec.yaml": "name: x\n"}, Stack.DART),
        ({"pubspec.yaml": "dependencies:\n  flutter:\n    sdk: flutter\n"}, Stack.FLUTTER),
        ({"Sources/App.swift": ""}, Stack.SWIFT),
        ({"Package.swift": ""}, Stack.SWIFT),
        ({"Podfile": ""}, Stack.SWIFT),
        ({"Package.resolved": "{}"}, Stack.SWIFT),
        ({"App.xcodeproj/project.pbxproj": ""}, Stack.SWIFT),
        ({"Main.kt": ""}, Stack.KOTLIN),
        ({"build.gradle.kts": ""}, Stack.KOTLIN),
        ({"app/src/main/AndroidManifest.xml": "<manifest/>"}, Stack.ANDROID),
        ({"A.java": ""}, Stack.JAVA),
        ({"pom.xml": "<project/>"}, Stack.JAVA),
        ({"go.mod": "module x\n"}, Stack.GO),
        ({"main.go": ""}, Stack.GO),
        ({"Gemfile": ""}, Stack.RUBY),
        ({"Gemfile.lock": ""}, Stack.RUBY),
        ({"a.rb": ""}, Stack.RUBY),
        ({"Cargo.toml": ""}, Stack.RUST),
        ({"lib.rs": ""}, Stack.RUST),
    ],
)
def test_detect_new_stacks(tmp_path: Path, files: dict[str, str], expected: Stack):
    assert expected in _stacks(tmp_path, files)


def test_dart_without_flutter_is_not_flutter(tmp_path: Path):
    found = _stacks(tmp_path, {"pubspec.yaml": "name: x\ndependencies:\n  http: ^1.0.0\n"})
    assert Stack.DART in found
    assert Stack.FLUTTER not in found


def test_flutter_sdk_regex_tolerates_spaces(tmp_path: Path):
    found = _stacks(tmp_path, {"pubspec.yaml": "dependencies:\n  flutter:\n    sdk:   flutter\n"})
    assert {Stack.DART, Stack.FLUTTER} <= found


def test_declaration_files_alone_are_not_typescript(tmp_path: Path):
    assert Stack.TYPESCRIPT not in _stacks(tmp_path, {"types/globals.d.ts": ""})


def test_node_keeps_depending_on_package_json(tmp_path: Path):
    assert _stacks(tmp_path, {"package.json": "{}"}) == {Stack.NODE}


def test_coverage_notes_only_for_stacks_without_code_rules():
    notes = coverage_notes([Stack.GO, Stack.DJANGO, Stack.PYTHON, Stack.DOCKER, Stack.GIT])
    assert [render(note) for note in notes] == [
        "Go: se revisan secretos, dependencias y configuración; "
        "aún no hay reglas de código propias ni inventario de endpoints."
    ]
    assert coverage_notes([Stack.DJANGO, Stack.PHP, Stack.DOTNET, Stack.PYTHON]) == []
    assert coverage_notes([]) == []


def test_every_language_stack_has_a_coverage_entry():
    assert set(Stack) - set(COVERAGE) == {Stack.DOCKER, Stack.GIT}


def test_coverage_notes_reach_the_scan_limitations(tmp_path: Path):
    (tmp_path / "main.go").write_text("package main\n")
    result = run_scan(build_plan(tmp_path, profile="quick"), adapters=[])
    assert any(render(text).startswith("Go: se revisan secretos") for text in result.limitations)


def test_partial_missing_database_adds_its_own_limitation_once(tmp_path: Path):
    (tmp_path / "main.py").write_text("x = 1\n")
    message = "OSV no tiene en este equipo la base de Pub; actualiza las bases."

    class Partial(FakeAdapter):
        def invoke(self, ctx):
            raise MissingDatabaseError(message, partial=True)  # a loose text also works

    class Total(FakeAdapter):
        def invoke(self, ctx):
            raise MissingDatabaseError()

    plan = build_plan(tmp_path, profile="quick")
    result = run_scan(plan, adapters=[Partial("osv"), Partial("osv2")])
    assert [render(x) for x in result.limitations].count(message) == 1
    assert missing_database() not in result.limitations
    result = run_scan(plan, adapters=[Total("trivy")])
    assert missing_database() in result.limitations


def test_osv_error_text_names_the_ecosystem():
    text = "could not load db for SwiftURL ecosystem: unable to fetch OSV database"
    assert _ECOSYSTEM_DB.findall(text) == ["SwiftURL"]


@pytest.mark.parametrize("name", sorted(_PROBE_FILES))
def test_probe_files_are_well_formed(name: str):
    content = _PROBE_FILES[name]
    if name.endswith((".json", ".resolved")):
        json.loads(content)
    elif name == "Cargo.lock":
        assert tomllib.loads(content)["package"][0]["name"] == "time"
    elif name == "pubspec.lock":
        assert yaml.safe_load(content)["packages"]["http"]["version"] == "0.12.0"
    elif name == "gradle.lockfile":
        assert "log4j-core:2.14.1=" in content
    else:
        assert content.strip()


def test_a_stack_inside_another_does_not_repeat_its_note():
    from heimdall_guardian.core.coverage import coverage_notes
    from heimdall_guardian.core.detector import Stack

    notes = coverage_notes([Stack.DART, Stack.FLUTTER, Stack.NODE, Stack.TYPESCRIPT])
    assert notes == []  # Dart, Flutter, Node.js and TypeScript already have rules
    assert coverage_notes([Stack.DART]) == []


def test_a_flutter_app_does_not_flag_its_native_folders():
    from heimdall_guardian.core.coverage import coverage_notes
    from heimdall_guardian.core.detector import Stack

    flutter_app = [Stack.DART, Stack.FLUTTER, Stack.ANDROID, Stack.KOTLIN, Stack.SWIFT]
    assert coverage_notes(flutter_app) == []
    assert [render(n).split(":")[0] for n in coverage_notes([Stack.RUST])] == ["Rust"]
