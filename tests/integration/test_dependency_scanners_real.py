"""Real OSV-Scanner and Trivy against known-vulnerable lockfiles.

Skipped if the binary is missing (`python tools/fetch_tools.py`) or if the machine has
no downloaded vulnerability databases (`hdl bases --actualizar`); a missing database is
never a failure, and these tests never download anything (P4).

Data directory decision: the autouse `isolated_data_dir` fixture points `HDL_DATA_DIR` to
an empty directory, which would hide the real databases. The real location is therefore
resolved at import time, before any fixture runs. The databases (about 1.5 GB) are not
used in place, because the tools may write lock or cache files next to them: the needed
parts are cloned (APFS copy-on-write where available) into the isolated directory, so
the user's databases are only ever read.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from heimdall_guardian.adapters.base import find_binary
from heimdall_guardian.adapters.osv import OsvAdapter
from heimdall_guardian.adapters.trivy import TrivyAdapter
from heimdall_guardian.core.finding import Category, Finding, Severity
from heimdall_guardian.core.paths import bases_dir
from heimdall_guardian.core.profiles import Module
from heimdall_guardian.core.runner import build_plan, run_scan

# Resolved at import time: the autouse fixture has not replaced HDL_DATA_DIR yet.
REAL_BASES = bases_dir()
FIXTURE = Path(__file__).parent.parent / "fixtures" / "deps_lockfiles"
OSV_ECOSYSTEMS = ("PyPI", "npm")


def _clone(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if sys.platform == "darwin":
        proc = subprocess.run(["cp", "-cR", str(source), str(target)], capture_output=True)
        if proc.returncode == 0:
            return
        shutil.rmtree(target, ignore_errors=True)
    shutil.copytree(source, target)


def _prepare(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, parts: list[str]) -> Path:
    """Copies the fixture and the needed database parts; returns the project root."""
    for part in parts:
        if not (REAL_BASES / part).exists():
            pytest.skip(f"database not downloaded on this machine: {REAL_BASES / part}")
    data = tmp_path / "datos"
    for part in parts:
        _clone(REAL_BASES / part, data / "bases" / part)
    monkeypatch.setenv("HDL_DATA_DIR", str(data))
    root = tmp_path / "proyecto"
    shutil.copytree(FIXTURE, root)
    return root


def _check(findings: list[Finding]) -> None:
    assert findings
    for finding in findings:
        assert finding.category == Category.DEPENDENCIES
        assert finding.severity in set(Severity)
        assert finding.rule_id.startswith(("CVE-", "GHSA-", "PYSEC-", "OSV-", "GO-", "RUSTSEC-"))
    paths = {f.file for f in findings}
    assert any(p.endswith("requirements.txt") for p in paths)
    assert any(p.endswith("package-lock.json") for p in paths)


@pytest.mark.skipif(find_binary("osv-scanner") is None, reason="osv-scanner no está instalado")
def test_osv_scanner_finds_vulnerabilities_in_both_ecosystems(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    parts = [f"osv/osv-scalibr/{eco}" for eco in OSV_ECOSYSTEMS]
    root = _prepare(tmp_path, monkeypatch, parts)
    plan = build_plan(root, profile="custom", custom_modules=frozenset({Module.DEP}))
    result = run_scan(plan, adapters=[OsvAdapter()])
    assert not any(s.status == "error" for s in result.tools), result.limitations
    _check(result.findings)


@pytest.mark.skipif(find_binary("trivy") is None, reason="trivy no está instalado")
def test_trivy_finds_vulnerabilities_in_both_ecosystems(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    root = _prepare(tmp_path, monkeypatch, ["trivy/db"])
    plan = build_plan(root, profile="custom", custom_modules=frozenset({Module.DEP}))
    result = run_scan(plan, adapters=[TrivyAdapter()])
    assert not any(s.status == "error" for s in result.tools), result.limitations
    _check(result.findings)
