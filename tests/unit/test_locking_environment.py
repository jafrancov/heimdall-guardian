"""Database update lock, data locations and the CLI's app tip."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from heimdall_guardian import cli
from heimdall_guardian.core import environment as env_mod
from heimdall_guardian.core import locking
from heimdall_guardian.core.paths import bases_dir, data_dir, data_location_lines
from heimdall_guardian.storage import bases
from heimdall_guardian.ui import model


def test_lock_file_lives_in_bases_dir() -> None:
    with locking.database_lock():
        assert locking.lock_path() == bases_dir() / ".update.lock"
        assert locking.lock_path().is_file()


def test_second_acquisition_waits_and_times_out() -> None:
    told: list[str] = []
    with (
        locking.database_lock(),
        pytest.raises(locking.DatabaseLockTimeout),
        locking.database_lock(told.append, timeout=0.2, poll=0.05),
    ):
        pass
    assert len(told) == 1  # the waiting notice comes out once
    with locking.database_lock(timeout=0.2):  # released: it can be taken again
        pass


def test_lock_released_after_error() -> None:
    with pytest.raises(RuntimeError), locking.database_lock():
        raise RuntimeError("boom")
    with locking.database_lock(timeout=0.2, poll=0.05):
        pass


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX demonstration")
def test_lock_released_when_holder_process_dies(tmp_path: Path) -> None:
    import subprocess

    script = (
        "import os, sys\n"
        "from heimdall_guardian.core import locking\n"
        "cm = locking.database_lock(); cm.__enter__()\n"
        "print('held', flush=True)\n"
        "os._exit(0)\n"
    )
    proc = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    assert "held" in proc.stdout
    with locking.database_lock(timeout=0.5, poll=0.05):
        pass


def test_update_and_import_take_the_lock(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    held: list[str] = []

    def probe(name: str):
        def inner(*args: object, **kwargs: object):
            with (
                pytest.raises(locking.DatabaseLockTimeout),
                locking.database_lock(timeout=0.1, poll=0.02),
            ):
                pass
            held.append(name)
            return {} if name == "update" else 0

        return inner

    monkeypatch.setattr(bases, "_update_bases", probe("update"))
    monkeypatch.setattr(bases, "_import_bases", probe("import"))
    bases.update_bases()
    bases.import_bases(tmp_path / "x.tar.gz")
    assert held == ["update", "import"]
    with locking.database_lock(timeout=0.1):  # released afterwards
        pass


def test_scan_takes_lock_only_when_updating(
    monkeypatch: pytest.MonkeyPatch, project, tmp_path: Path
) -> None:
    from heimdall_guardian.core.runner import build_plan, run_scan

    taken: list[bool] = []
    real = locking.database_lock

    def spy(*args: object, **kwargs: object):
        taken.append(True)
        return real(*args, **kwargs)  # type: ignore[arg-type]

    from heimdall_guardian.core import runner

    monkeypatch.setattr(runner, "database_lock", spy)
    root = tmp_path / "proj"
    root.mkdir()
    (root / "a.py").write_text("x = 1\n")
    plan = build_plan(root, profile="quick")
    run_scan(plan, adapters=[], update_dbs=False)
    assert taken == []
    run_scan(plan, adapters=[], update_dbs=True)
    assert taken == [True]


def test_app_and_cli_resolve_same_folders(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    monkeypatch.setenv("HDL_BASES_DIR", str(tmp_path / "b"))
    lines = model.data_lines()
    assert lines == data_location_lines()
    assert str(data_dir()) in lines[0]
    assert "HDL_DATA_DIR" in lines[0]
    assert str(tmp_path / "b") in lines[1]
    assert "HDL_BASES_DIR" in lines[1]
    cli.main(["tools"])
    out = capsys.readouterr().out
    for line in lines:
        assert line in out


# --- environment ---


def test_graphical_session() -> None:
    assert env_mod.graphical_session({}, "darwin")
    assert not env_mod.graphical_session({"SSH_CONNECTION": "1"}, "darwin")
    assert not env_mod.graphical_session({"SSH_TTY": "/dev/pts/0"}, "win32")
    assert env_mod.graphical_session({}, "win32")
    assert not env_mod.graphical_session({}, "linux")
    assert env_mod.graphical_session({"DISPLAY": ":0"}, "linux")
    assert env_mod.graphical_session({"WAYLAND_DISPLAY": "w"}, "linux")
    assert not env_mod.graphical_session({"DISPLAY": ":0", "SSH_TTY": "x"}, "linux")


def test_in_ci() -> None:
    assert not env_mod.in_ci({})
    assert env_mod.in_ci({"CI": "true"})
    assert env_mod.in_ci({"GITHUB_ACTIONS": "true"})
    assert env_mod.in_ci({"JENKINS_URL": "http://j"})


def test_app_installed(tmp_path: Path) -> None:
    assert not env_mod.app_installed("darwin", tmp_path, {}, tmp_path)
    (tmp_path / "Applications" / "Heimdall Guardian.app").mkdir(parents=True)
    assert env_mod.app_installed("darwin", tmp_path, {}, tmp_path)
    assert not env_mod.app_installed("linux", tmp_path, {}, tmp_path)
    desktop = tmp_path / ".local" / "share" / "applications"
    desktop.mkdir(parents=True)
    (desktop / "heimdall-guardian.desktop").write_text("x")
    assert env_mod.app_installed("linux", tmp_path, {}, tmp_path)
    programs = tmp_path / "pf" / "Heimdall Guardian"
    programs.mkdir(parents=True)
    assert env_mod.app_installed(
        "win32", tmp_path, {"ProgramFiles": str(tmp_path / "pf")}, tmp_path
    )


def _hint(tmp_path: Path, **overrides: object) -> bool:
    args: dict[str, object] = {
        "tty": True,
        "env": {},
        "platform": "darwin",
        "home": tmp_path,
        "marker": tmp_path / "marker",
        "system_root": tmp_path,
    }
    args.update(overrides)
    return env_mod.should_hint(**args)  # type: ignore[arg-type]


def test_should_hint_conditions(tmp_path: Path) -> None:
    assert _hint(tmp_path)
    assert not _hint(tmp_path, tty=False)
    assert not _hint(tmp_path, env={"SSH_CONNECTION": "1"})
    assert not _hint(tmp_path, env={"CI": "1"})
    assert not _hint(tmp_path, env={"HDL_NO_HINTS": "1"})
    assert not _hint(tmp_path, platform="linux")
    (tmp_path / "Applications" / "Heimdall Guardian.app").mkdir(parents=True)
    assert not _hint(tmp_path)


def test_hint_shown_once(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(env_mod, "app_installed", lambda *a, **k: False)
    for name in ("SSH_CONNECTION", "SSH_TTY", "SSH_CLIENT", "HDL_NO_HINTS", *env_mod._CI_VARS):
        monkeypatch.delenv(name, raising=False)
    first = env_mod.maybe_app_hint(tty=True)
    assert first
    assert env_mod.homepage_url() in first
    assert (data_dir() / env_mod.HINT_MARKER).is_file()
    assert env_mod.maybe_app_hint(tty=True) is None


def test_cli_prints_hint_on_tty_only(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(env_mod, "maybe_app_hint", lambda *, tty: "TIP" if tty else None)
    monkeypatch.setattr(cli, "maybe_app_hint", env_mod.maybe_app_hint)
    cli.main(["tools"])
    assert "TIP" not in capsys.readouterr().err  # pytest's stderr is not a TTY
