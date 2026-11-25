"""The stand-alone `hdl` installer (packaging/cli/install_hdl.py): pure functions, no network."""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType

import pytest

from heimdall_guardian.core import paths

SCRIPT = Path(__file__).resolve().parents[2] / "packaging" / "cli" / "install_hdl.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("install_hdl", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["install_hdl"] = module
    spec.loader.exec_module(module)
    return module


installer = _load()


@pytest.mark.parametrize("platform", ["darwin", "win32", "linux"])
@pytest.mark.parametrize("override", [True, False])
def test_data_dir_matches_the_package(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, platform: str, override: bool
) -> None:
    monkeypatch.setattr(sys, "platform", platform)
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path / "home"))
    for variable in ("HDL_DATA_DIR", "APPDATA", "XDG_DATA_HOME"):
        monkeypatch.delenv(variable, raising=False)
    if override:
        monkeypatch.setenv("HDL_DATA_DIR", str(tmp_path / "custom"))
    expected = paths.data_dir()
    assert installer.data_dir(dict(os.environ), platform, tmp_path / "home") == expected


def test_data_dir_honours_appdata_and_xdg(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("HDL_DATA_DIR", raising=False)
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    monkeypatch.setenv("APPDATA", str(tmp_path / "roaming"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "xdg"))
    for platform in ("win32", "linux"):
        monkeypatch.setattr(sys, "platform", platform)
        env = {"APPDATA": str(tmp_path / "roaming"), "XDG_DATA_HOME": str(tmp_path / "xdg")}
        assert installer.data_dir(env, platform, tmp_path) == paths.data_dir()


def test_old_python_message_names_minimum_and_link() -> None:
    message = installer.version_problem((3, 9, 6), "/usr/bin/python3", "en", "linux")
    assert message is not None
    assert "3.12" in message
    assert "3.9.6" in message
    assert "https://www.python.org/downloads/" in message
    assert "Xcode" not in message


def test_old_python_on_macos_system_python_is_explained() -> None:
    message = installer.version_problem((3, 9, 6), "/usr/bin/python3", "en", "darwin")
    assert message is not None
    assert "Xcode" in message


def test_old_python_message_in_spanish() -> None:
    message = installer.version_problem((3, 10, 0), "/opt/py", "es", "linux")
    assert message is not None
    assert "necesita Python 3.12" in message


def test_current_python_has_no_problem() -> None:
    assert installer.version_problem((3, 12, 0), "/x/python", "en") is None
    assert installer.version_problem((3, 14, 1), "/x/python", "en") is None


def test_language_choice() -> None:
    assert installer.choose_language({}) == "en"
    assert installer.choose_language({"LANG": "es_MX.UTF-8"}) == "es"
    assert installer.choose_language({"LANG": "es_MX.UTF-8", "HDL_LANG": "en"}) == "en"
    assert installer.choose_language({"LANG": "C.UTF-8"}) == "en"


def test_default_bin_dirs(tmp_path: Path) -> None:
    assert installer.default_bin_dir({}, "linux", tmp_path) == tmp_path / ".local" / "bin"
    assert installer.default_bin_dir({}, "darwin", tmp_path) == tmp_path / ".local" / "bin"
    windows = installer.default_bin_dir(
        {"LOCALAPPDATA": str(tmp_path / "local")}, "win32", tmp_path
    )
    assert windows == tmp_path / "local" / "Programs" / "Heimdall Guardian" / "bin"


@pytest.mark.skipif(sys.platform == "win32", reason="simulates a POSIX PATH (':' separated)")
def test_path_advice(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    env = {"PATH": f"/usr/bin:{bin_dir}", "SHELL": "/bin/zsh"}
    assert installer.path_advice(bin_dir, env, "en", "linux") is None
    advice = installer.path_advice(
        bin_dir, {"PATH": "/usr/bin", "SHELL": "/bin/zsh"}, "en", "linux"
    )
    assert advice is not None
    assert "~/.zshrc" in advice
    assert f'export PATH="{bin_dir}:$PATH"' in advice
    bash = installer.path_advice(bin_dir, {"PATH": "/usr/bin", "SHELL": "/bin/bash"}, "es", "linux")
    assert bash is not None
    assert "~/.bashrc" in bash
    assert installer.path_advice(bin_dir, {"PATH": ""}, "en", "win32") is None


def test_windows_path_value_edits() -> None:
    entry = r"C:\Users\me\Programs\Heimdall Guardian\bin"
    added = installer.add_to_path_value(r"C:\Windows;C:\Tools", entry)
    assert added.endswith(entry)
    assert installer.add_to_path_value(added, entry) == added
    assert installer.remove_from_path_value(added, entry) == r"C:\Windows;C:\Tools"


def _fake_venv(tmp_path: Path) -> Path:
    venv = installer.venv_dir(tmp_path / "data")
    (venv / "bin").mkdir(parents=True)
    (venv / "bin" / "hdl").write_text("#!/bin/sh\n", encoding="utf-8")
    return venv


def test_create_link_and_uninstall(tmp_path: Path) -> None:
    data = tmp_path / "data"
    venv = _fake_venv(tmp_path)
    bin_dir = tmp_path / "bin"
    link = installer.create_link(venv, bin_dir, "linux")
    assert link.is_symlink()
    assert link.resolve() == (venv / "bin" / "hdl").resolve()
    # A second install replaces the link instead of failing.
    assert installer.create_link(venv, bin_dir, "linux") == link
    (data / "bases").mkdir()
    (data / "config.toml").write_text("x", encoding="utf-8")

    removed = installer.uninstall(data, bin_dir, "linux", "en")
    assert str(link) in removed
    assert not link.is_symlink()
    assert not venv.exists()
    assert (data / "bases").is_dir()
    assert (data / "config.toml").is_file()


def test_uninstall_leaves_a_foreign_link_alone(tmp_path: Path) -> None:
    data = tmp_path / "data"
    venv = _fake_venv(tmp_path)
    other = tmp_path / "other-hdl"
    other.write_text("x", encoding="utf-8")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "hdl").symlink_to(other)
    removed = installer.uninstall(data, bin_dir, "linux", "en")
    assert (bin_dir / "hdl").is_symlink()
    assert removed == [str(venv)]


def test_uninstall_without_installation_is_a_no_op(tmp_path: Path) -> None:
    assert installer.uninstall(tmp_path / "data", tmp_path / "bin", "linux", "en") == []


def test_windows_shim_content(tmp_path: Path) -> None:
    venv = installer.venv_dir(tmp_path / "data")
    shim = installer.create_link(venv, tmp_path / "bin", "win32")
    assert shim.name == "hdl.cmd"
    assert str(venv / "Scripts" / "hdl.exe") in shim.read_text(encoding="utf-8")
    assert installer.is_ours(shim, venv, "win32")


def test_main_refuses_old_python(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "version_info", (3, 9, 6, "final", 0))
    assert installer.main(["--yes"], {"HDL_LANG": "en"}) == 1
    assert "python.org/downloads" in capsys.readouterr().err
