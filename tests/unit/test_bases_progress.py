"""Database downloads show their size and that they are still working (slow links)."""

from __future__ import annotations

import sys

import pytest

from heimdall_guardian.adapters import base
from heimdall_guardian.adapters.base import AdapterError, run
from heimdall_guardian.storage import bases


def test_run_calls_the_heartbeat_while_the_program_works(tmp_path, monkeypatch):
    monkeypatch.setattr(base, "HEARTBEAT_SECONDS", 0.05)
    beats: list[int] = []
    proc = run(
        [sys.executable, "-c", "import time; time.sleep(0.4); print('done')"],
        cwd=tmp_path,
        heartbeat=beats.append,
    )
    assert proc.returncode == 0
    assert proc.stdout.strip() == "done"
    assert beats  # it said it was alive at least once
    assert beats == sorted(beats)


def test_run_with_heartbeat_still_honours_the_timeout(tmp_path, monkeypatch):
    monkeypatch.setattr(base, "HEARTBEAT_SECONDS", 0.05)
    with pytest.raises(AdapterError):
        run(
            [sys.executable, "-c", "import time; time.sleep(10)"],
            cwd=tmp_path,
            timeout=0,
            heartbeat=lambda _: None,
        )


def test_elapsed_text_reads_minutes_and_seconds():
    assert bases.elapsed_text(40) == "40 s"
    assert bases.elapsed_text(185) == "3 min 05 s"


def test_update_reports_elapsed_time_and_allows_a_long_download(monkeypatch):
    seen: dict[str, object] = {}

    class Done:
        returncode, stdout, stderr = 0, "", ""

    def fake_run(cmd, *, cwd, env=None, timeout=0, heartbeat=None):
        seen["timeout"] = timeout
        assert heartbeat is not None
        heartbeat(65)
        return Done()

    monkeypatch.setattr(
        bases, "find_binary", lambda name: f"/bin/{name}" if name == "trivy" else None
    )
    monkeypatch.setattr(bases, "run", fake_run)
    waits: list[str] = []
    lines: list[str] = []
    outcome = bases.update_bases(lines.append, on_wait=waits.append)
    assert outcome["trivy"] == bases.UPDATED
    assert outcome["osv"] == bases.NOT_INSTALLED
    assert seen["timeout"] == base.DOWNLOAD_TIMEOUT_SECONDS
    assert len(lines) == 2  # size notice + the only database there is to download
    assert waits
    assert waits[0].startswith(lines[1])
    assert waits[0].endswith("1 min 05 s")


def test_no_size_notice_when_no_tool_is_installed(monkeypatch):
    monkeypatch.setattr(bases, "find_binary", lambda name: None)
    lines: list[str] = []
    bases.update_bases(lines.append)
    assert lines == []
