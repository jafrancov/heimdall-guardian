"""Real OSV-Scanner against a synthetic copied library (a banner file written for the test).

Skipped when the binary or the npm database is missing on this machine; it never downloads
anything (P4). The database parts are cloned into the isolated data directory, as in
`test_dependency_scanners_real.py`.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from heimdall_guardian.adapters.base import find_binary
from heimdall_guardian.adapters.opengrep import OpengrepAdapter
from heimdall_guardian.adapters.vendored import VendoredAdapter
from heimdall_guardian.core.paths import bases_dir
from heimdall_guardian.core.profiles import Module
from heimdall_guardian.core.runner import build_plan, run_scan

# Resolved at import time: the autouse fixture has not replaced HDL_DATA_DIR yet.
REAL_BASES = bases_dir()
NPM_DATABASE = REAL_BASES / "osv" / "osv-scalibr" / "npm"


def _clone(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if sys.platform == "darwin":
        proc = subprocess.run(["cp", "-cR", str(source), str(target)], capture_output=True)
        if proc.returncode == 0:
            return
        shutil.rmtree(target, ignore_errors=True)
    shutil.copytree(source, target)


@pytest.mark.skipif(find_binary("osv-scanner") is None, reason="osv-scanner is not installed")
def test_copied_jquery_is_reported_against_its_file(tmp_path: Path, monkeypatch):
    if not NPM_DATABASE.exists():
        pytest.skip(f"database not downloaded on this machine: {NPM_DATABASE}")
    data = tmp_path / "data"
    _clone(NPM_DATABASE, data / "bases" / "osv" / "osv-scalibr" / "npm")
    monkeypatch.setenv("HDL_DATA_DIR", str(data))

    root = tmp_path / "project"
    (root / "static" / "js").mkdir(parents=True)
    library = root / "static" / "js" / "jquery-2.1.1.min.js"
    library.write_text("/*! jQuery v2.1.1 | synthetic banner for tests */\nvar a=1;\n")
    modules = frozenset({Module.DEP, Module.SAST})
    plan = build_plan(root, profile="custom", custom_modules=modules)
    assert [lib.version for lib in plan.vendored] == ["2.1.1"]

    adapters = [VendoredAdapter(), OpengrepAdapter()]
    result = run_scan(plan, adapters=adapters)
    tool = next(t for t in result.tools if t.name == "vendored")
    assert tool.status == "ran", (tool.detail, result.limitations)
    hits = [f for f in result.findings if f.rule_id == "CVE-2019-11358"]
    assert [f.file for f in hits] == ["static/js/jquery-2.1.1.min.js"]
    assert hits[0].source == "vendored"
    assert hits[0].detected_by == ["vendored"]
    assert not (root / "package-lock.json").exists()  # P1: nothing written in the project
    assert sorted(p.name for p in root.rglob("*") if p.is_file()) == ["jquery-2.1.1.min.js"]
