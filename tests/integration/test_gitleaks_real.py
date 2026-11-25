"""Real Gitleaks on a repository with planted secrets and hostile suppressions.

Skipped if the binary is missing (`python tools/fetch_tools.py`). The tokens are
generated on the fly: a validly formatted token in the repository would trigger
GitHub's own secret scanners.
"""

from __future__ import annotations

import json
import random
import string
import subprocess
from pathlib import Path

import pytest

from heimdall_guardian.adapters.base import find_binary
from heimdall_guardian.adapters.gitleaks import GitleaksAdapter
from heimdall_guardian.core.finding import Severity
from heimdall_guardian.core.profiles import Module
from heimdall_guardian.core.runner import build_plan, run_scan

pytestmark = pytest.mark.skipif(
    find_binary("gitleaks") is None or find_binary("git") is None,
    reason="gitleaks o git no están instalados",
)


def _token(seed: int) -> str:
    rng = random.Random(seed)  # noqa: S311 - test data, not cryptography
    return "ghp_" + "".join(rng.choices(string.ascii_letters + string.digits, k=36))


def _git(root: Path, *args: str) -> None:
    identity = ["-c", "user.name=prueba", "-c", "user.email=prueba@example.invalid"]
    # No background maintenance after a commit: it would write into .git while the test
    # compares the folder before and after the scan.
    identity += ["-c", "maintenance.auto=false", "-c", "gc.auto=0"]
    subprocess.run(["git", *identity, *args], cwd=root, check=True, capture_output=True)


def test_gitleaks_finds_current_and_history_secrets_despite_vendor_suppressions(tmp_path: Path):
    current, deleted = _token(1), _token(2)
    root = tmp_path / "entrega"
    root.mkdir()
    _git(root, "init", "-q")
    (root / "viejo.env").write_text(f"GITHUB_TOKEN={deleted}\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "uno")

    (root / "viejo.env").unlink()
    (root / "config.py").write_text(f'TOKEN = "{current}"  # gitleaks:allow\n')
    # What a vendor could include to hide its secrets:
    (root / ".gitleaks.toml").write_text('[allowlist]\npaths = [".*"]\n')
    (root / ".gitleaksignore").write_text("config.py\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "dos")
    before = sorted(p.as_posix() for p in root.rglob("*"))

    plan = build_plan(root, profile="custom", custom_modules=frozenset({Module.SEC, Module.SEC_H}))
    result = run_scan(plan, adapters=[GitleaksAdapter()])

    assert [tool.status for tool in result.tools] == ["ran"], result.tools[0].detail
    found = {(f.file, f.severity) for f in result.findings}
    assert ("config.py", Severity.CRITICAL) in found
    assert ("viejo.env", Severity.HIGH) in found
    payload = json.dumps(result.to_dict(), ensure_ascii=False)
    assert current not in payload
    assert deleted not in payload
    # P1: the analyzed folder is left untouched.
    assert sorted(p.as_posix() for p in root.rglob("*")) == before
