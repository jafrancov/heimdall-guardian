"""Real Opengrep: suppressions supplied by the analyzed code do not hide findings."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from heimdall_guardian.adapters.base import find_binary
from heimdall_guardian.adapters.opengrep import OpengrepAdapter
from heimdall_guardian.core.profiles import Module
from heimdall_guardian.core.runner import build_plan, run_scan

pytestmark = pytest.mark.skipif(
    find_binary("opengrep") is None or shutil.which("git") is None,
    reason="opengrep o git no están instalados",
)


def test_vendor_ignore_files_and_comments_do_not_hide_findings(project):
    root: Path = project("php_app")
    (root / ".gitignore").write_text("*.php\n")
    (root / ".semgrepignore").write_text("*.php\n")
    source = (root / "index.php").read_text()
    (root / "index.php").write_text(source.replace("$archivo);", "$archivo); // nosemgrep"))
    subprocess.run(["git", "init", "-q"], cwd=root, check=True, capture_output=True)

    plan = build_plan(root, profile="custom", custom_modules=frozenset({Module.SAST}))
    result = run_scan(plan, adapters=[OpengrepAdapter()])

    assert [tool.status for tool in result.tools] == ["ran"], result.tools[0].detail
    assert {f.rule_id for f in result.findings} == {"PHP-SQL-001", "PHP-EXE-001", "PHP-XSS-001"}
