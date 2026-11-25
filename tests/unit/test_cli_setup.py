"""Installing the `hdl` command from the app: finding Python, status, commands, texts.

Nothing here installs anything: the machine is replaced by fakes.
"""

from __future__ import annotations

import importlib.util
import sys
import tarfile
from pathlib import Path

import pytest

from heimdall_guardian.core import cli_setup as cs
from heimdall_guardian.i18n import languages
from heimdall_guardian.ui import model as m

TOOLS = Path(__file__).resolve().parents[2] / "tools"


@pytest.fixture(params=["en", "es"])
def lang(request, monkeypatch):
    monkeypatch.setattr(languages, "_current", request.param)
    monkeypatch.setattr(languages, "_override", None)
    return request.param


def _fake_machine(versions: dict[str, tuple[int, int]]):
    """Probe, exists and glob over a dictionary of executable -> version."""

    def probe(command):
        exe = command[0]
        if exe not in versions:
            return None
        major, minor = versions[exe]
        return f"{major} {minor} {exe}\n"

    return probe, (lambda p: p in versions or p.endswith("py.exe")), (lambda pattern: [])


def test_find_python_prefers_python_org_on_mac():
    framework = "/Library/Frameworks/Python.framework/Versions/{}/bin/python3"
    versions = {
        framework.format("3.9"): (3, 9),
        framework.format("3.13"): (3, 13),
        framework.format("3.14"): (3, 14),
        "/opt/homebrew/bin/python3": (3, 12),
    }
    probe, exists, _ = _fake_machine(versions)
    found = cs.find_python(
        platform="darwin",
        env={},
        probe=probe,
        exists=exists,
        which=lambda name: None,
        find=lambda pattern: [k for k in versions if "Frameworks" in k],
    )
    assert found == cs.PythonInfo(framework.format("3.14"), (3, 14))


def test_find_python_falls_back_to_homebrew_then_path():
    versions = {"/opt/homebrew/bin/python3": (3, 12)}
    probe, exists, find = _fake_machine(versions)
    found = cs.find_python(
        platform="darwin", env={}, probe=probe, exists=exists, which=lambda n: None, find=find
    )
    assert found is not None
    assert found.path == "/opt/homebrew/bin/python3"
    versions = {"/somewhere/python3": (3, 13)}
    probe, exists, find = _fake_machine(versions)
    found = cs.find_python(
        platform="darwin",
        env={},
        probe=probe,
        exists=exists,
        which=lambda n: "/somewhere/python3" if n == "python3" else None,
        find=find,
    )
    assert found == cs.PythonInfo("/somewhere/python3", (3, 13))


def test_find_python_never_runs_the_apple_stub():
    probed: list[str] = []

    def probe(command):
        probed.append(command[0])
        return "3 9 /usr/bin/python3"

    found = cs.find_python(
        platform="darwin",
        env={},
        probe=probe,
        exists=lambda p: True,
        which=lambda n: "/usr/bin/python3",
        find=lambda pattern: [],
    )
    assert "/usr/bin/python3" not in probed
    assert found is None


def test_find_python_rejects_old_and_garbled_answers():
    probe_old = lambda command: "3 11 /usr/local/bin/python3"  # noqa: E731
    args = {"platform": "linux", "env": {}, "exists": lambda p: True, "find": lambda p: []}
    assert cs.find_python(probe=probe_old, which=lambda n: None, **args) is None
    assert cs.find_python(probe=lambda c: "hello", which=lambda n: None, **args) is None
    assert cs.find_python(probe=lambda c: None, which=lambda n: None, **args) is None
    assert cs.find_python((3, 11), probe=probe_old, which=lambda n: None, **args) is not None


def test_find_python_linux_order_and_dedupe():
    probed: list[str] = []

    def probe(command):
        probed.append(command[0])
        return ""

    cs.find_python(
        platform="linux",
        env={},
        probe=probe,
        exists=lambda p: True,
        which=lambda n: "/usr/bin/python3" if n == "python3" else None,
        find=lambda p: [],
    )
    assert probed == ["/usr/bin/python3", "/usr/local/bin/python3"]


def test_find_python_windows_launcher_and_store_stub():
    probed: list[list[str]] = []

    def probe(command):
        probed.append(list(command))
        return "3 13 C:\\Python313\\python.exe" if len(command) == 2 else None

    found = cs.find_python(
        platform="win32",
        env={"WINDIR": "C:\\Windows", "LOCALAPPDATA": "C:\\Users\\a\\AppData\\Local"},
        probe=probe,
        exists=lambda p: True,
        which=lambda n: "C:\\Users\\a\\AppData\\Local\\Microsoft\\WindowsApps\\python.exe",
        find=lambda p: [],
        registry=lambda: [],  # on a Windows host the real registry would answer first
    )
    assert found == cs.PythonInfo("C:\\Python313\\python.exe", (3, 13))
    assert probed[0][1] == "-3"
    # The Store stub is skipped without being run.
    assert (
        cs.find_python(
            platform="win32",
            env={},
            probe=lambda c: pytest.fail("must not run"),
            exists=lambda p: True,
            which=lambda n: "C:\\Users\\a\\AppData\\Local\\Microsoft\\WindowsApps\\python.exe",
            find=lambda p: [],
            registry=lambda: [],
        )
        is None
    )


def test_find_python_windows_prefers_registered_interpreters():
    registered = "D:\\tools\\py314\\python.exe"
    found = cs.find_python(
        platform="win32",
        env={"WINDIR": "C:\\Windows"},
        probe=lambda c: f"3 14 {c[0]}" if c[0] == registered else None,
        exists=lambda p: True,
        which=lambda n: None,
        find=lambda p: [],
        registry=lambda: [registered],
    )
    assert found == cs.PythonInfo(registered, (3, 14))


def test_find_python_windows_install_manager_and_all_users_folders():
    local = "C:\\Users\\a\\AppData\\Local"
    patterns: list[str] = []
    probed: list[list[str]] = []
    manager = local + "\\Python\\pythoncore-3.14-64\\python.exe"

    def find(pattern):
        patterns.append(pattern.replace("\\", "/"))
        return [manager] if "pythoncore" in pattern else []

    def probe(command):
        probed.append(list(command))
        return f"3 14 {manager}" if command[0] == manager else None

    found = cs.find_python(
        platform="win32",
        env={"LOCALAPPDATA": local, "ProgramFiles": "C:\\Program Files"},
        probe=probe,
        exists=lambda p: "Launcher" in p or p == manager,
        which=lambda n: None,
        find=find,
        registry=lambda: [],
    )
    assert found == cs.PythonInfo(manager, (3, 14))
    assert probed[0][0].replace("\\", "/").endswith("Programs/Python/Launcher/py.exe")
    assert any(p.endswith("Python/pythoncore-3*/python.exe") for p in patterns)
    assert any(p.endswith("Program Files/Python3*/python.exe") for p in patterns)


def test_child_processes_hide_the_console_only_on_windows(monkeypatch):
    from heimdall_guardian.core import processes

    monkeypatch.setattr(processes.sys, "platform", "darwin")
    assert processes.no_window() == {}
    monkeypatch.setattr(processes.sys, "platform", "win32")
    monkeypatch.setattr(processes.subprocess, "CREATE_NO_WINDOW", 0x08000000, raising=False)
    assert processes.no_window() == {"creationflags": 0x08000000}


def test_cli_status_reads_the_disk_only(tmp_path: Path):
    data, home = tmp_path / "data", tmp_path / "home"
    missing = cs.cli_status(data, platform="linux", env={}, home=home)
    assert not missing.installed
    assert missing.link is None
    assert missing.version is None
    command = data / "cli" / "venv" / "bin" / "hdl"
    command.parent.mkdir(parents=True)
    command.write_text("")
    dist = data / "cli" / "venv" / "lib" / "python3.14" / "site-packages"
    (dist / "heimdall_guardian-0.41.0.dist-info").mkdir(parents=True)
    bare = cs.cli_status(data, platform="linux", env={}, home=home)
    assert bare.installed
    assert bare.link is None
    assert bare.version == "0.41.0"
    (home / ".local" / "bin").mkdir(parents=True)
    (home / ".local" / "bin" / "hdl").symlink_to(command)
    linked = cs.cli_status(data, platform="linux", env={}, home=home)
    assert linked.link == home / ".local" / "bin" / "hdl"


def test_cli_status_windows_layout(tmp_path: Path):
    data = tmp_path / "data"
    exe = data / "cli" / "venv" / "Scripts" / "hdl.exe"
    exe.parent.mkdir(parents=True)
    exe.write_text("")
    (data / "cli" / "venv" / "Lib" / "site-packages" / "heimdall_guardian-1.2.3.dist-info").mkdir(
        parents=True
    )
    status = cs.cli_status(data, platform="win32", env={"LOCALAPPDATA": str(tmp_path / "L")})
    assert status.installed
    assert status.version == "1.2.3"


def test_bundled_files_and_development_fallback(tmp_path: Path):
    package, repo = tmp_path / "pkg", tmp_path / "repo"
    assert cs.bundled_cli_files(package, repo) is None
    (repo / "packaging" / "cli").mkdir(parents=True)
    (repo / "packaging" / "cli" / "install_hdl.py").write_text("")
    only_script = cs.bundled_cli_files(package, repo)
    assert only_script is not None
    assert only_script.wheel is None
    (repo / "dist" / "cli").mkdir(parents=True)
    for version in ("0.9.0", "0.10.0"):
        (repo / "dist" / "cli" / f"heimdall_guardian-{version}-py3-none-any.whl").write_text("")
    dev = cs.bundled_cli_files(package, repo)
    assert dev is not None
    assert dev.wheel is not None
    assert dev.wheel.name.startswith("heimdall_guardian-0.10.0")
    (package / "_bundle" / "cli").mkdir(parents=True)
    (package / "_bundle" / "cli" / "install_hdl.py").write_text("")
    (package / "_bundle" / "cli" / "heimdall_guardian-1.0.0-py3-none-any.whl").write_text("")
    bundled = cs.bundled_cli_files(package, repo)
    assert bundled is not None
    assert bundled.script.parent == package / "_bundle" / "cli"
    assert bundled.wheel is not None
    assert bundled.wheel.name.startswith("heimdall_guardian-1.0.0")


def test_command_lines(tmp_path: Path):
    files = cs.CliFiles(Path("/b/install_hdl.py"), Path("/b/x.whl"))
    script, wheel = str(files.script), str(files.wheel)  # native separators
    assert cs.install_command("/py", files) == [
        "/py",
        script,
        "--wheel",
        wheel,
        "--yes",
    ]
    assert cs.install_command("/py", cs.CliFiles(files.script, None), bin_dir=tmp_path) == [
        "/py",
        script,
        "--bin-dir",
        str(tmp_path),
        "--yes",
    ]
    assert cs.uninstall_command("/py", files) == [
        "/py",
        script,
        "--uninstall",
        "--yes",
    ]


def test_installer_env_drops_python_state_and_sets_language():
    env = cs.installer_env("es", {"PYTHONHOME": "/app", "PYTHONPATH": "/x", "PATH": "/bin"})
    assert env == {"PATH": "/bin", "HDL_LANG": "es"}


def test_output_parsing():
    out = 'x\nplan\n/home/u/.local/bin is not on your PATH.\n    export PATH="/h:$PATH"\nDone.'
    assert cs.path_advice(out) == [
        "/home/u/.local/bin is not on your PATH.",
        '    export PATH="/h:$PATH"',
    ]
    assert cs.path_advice("all good") == []
    long = "\n".join(f"line {i}" for i in range(30)) + "\n\n"
    tail = cs.output_tail(long)
    assert tail[-1] == "line 29"
    assert len(tail) == 12


def test_offer_is_made_once_and_only_when_missing(tmp_path: Path):
    marker = tmp_path / "sub" / "cli_offer_shown"
    assert cs.offer_due(marker, installed=False)
    assert not cs.offer_due(marker, installed=True)
    cs.mark_offered(marker)
    assert not cs.offer_due(marker, installed=False)


def _status(installed: bool, tmp: Path, version: str | None = None) -> cs.CliStatus:
    return cs.CliStatus(
        installed, tmp / "venv" / "hdl", tmp / "bin" / "hdl" if installed else None, version
    )


FILES = cs.CliFiles(Path("/b/install_hdl.py"), Path("/b/x.whl"))
PYTHON = cs.PythonInfo("/py", (3, 14))


def test_section_states(tmp_path: Path, lang: str):
    ready = m.cli_section(_status(False, tmp_path), PYTHON, FILES)
    assert ready.action == "install"
    assert ready.button == (
        "Install the hdl command" if lang == "en" else "Instalar el comando hdl"
    )
    assert any("internet" in line for line in ready.lines)

    no_python = m.cli_section(_status(False, tmp_path), None, FILES)
    assert no_python.action == "download_python"
    assert any("3.12" in line for line in no_python.lines)
    assert no_python.button == ("Download Python" if lang == "en" else "Descargar Python")

    installed = m.cli_section(_status(True, tmp_path, "0.41.0"), None, FILES)
    assert installed.action == "uninstall"
    assert str(tmp_path / "bin" / "hdl") in installed.lines[0]
    assert any("0.41.0" in line for line in installed.lines)

    none = m.cli_section(_status(False, tmp_path), PYTHON, None)
    assert none.action == "none"
    assert none.button == ""


def test_result_dialog(tmp_path: Path, lang: str):
    ok = cs.RunResult(0, 'Command ready\nfoo is not on your PATH:\n    export PATH="/h:$PATH"\n')
    title, body, success = m.cli_result("install", ok, _status(True, tmp_path))
    assert success
    assert any("export PATH" in line for line in body)
    assert str(tmp_path / "bin" / "hdl") in body[0]
    _, body, _ = m.cli_result("install", cs.RunResult(0, "fine"), _status(True, tmp_path))
    assert len(body) == 2

    failed = cs.RunResult(1, "a\nb\npip could not install")
    title, body, success = m.cli_result("install", failed, _status(False, tmp_path))
    assert not success
    assert body[-1] == "pip could not install"
    assert title == (
        "The command could not be installed" if lang == "en" else "No se pudo instalar el comando"
    )
    _, body, success = m.cli_result("uninstall", cs.RunResult(0, ""), _status(False, tmp_path))
    assert success
    _, body, success = m.cli_result("uninstall", cs.RunResult(1, ""), _status(True, tmp_path))
    assert not success
    assert len(body) == 1


def test_first_launch_offer_texts(lang: str):
    _, body, action, button = m.cli_offer(PYTHON)
    assert action == "install"
    assert "hdl" in body[0]
    assert button == ("Install it" if lang == "en" else "Instalarlo")
    assert ("Settings" if lang == "en" else "Configuración") in body[-1]
    _, body, action, button = m.cli_offer(None)
    assert action == "download_python"
    assert any("3.12" in line for line in body)
    assert m.cli_running_text("uninstall") != m.cli_running_text("install")


def _load_archive_tool():
    spec = importlib.util.spec_from_file_location(
        "build_cli_archive", TOOLS / "build_cli_archive.py"
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["build_cli_archive"] = module
    spec.loader.exec_module(module)
    return module


def test_cli_archive_contents(tmp_path: Path):
    tool = _load_archive_tool()
    wheel = tmp_path / "heimdall_guardian-9.9.9-py3-none-any.whl"
    wheel.write_bytes(b"wheel")
    script = tmp_path / "install_hdl.py"
    script.write_text("print('x')\n")
    archive = tool.make_cli_archive("9.9.9", wheel, output=tmp_path / "out", script=script)
    assert archive.name == "heimdall-guardian-cli-9.9.9.tar.gz"
    with tarfile.open(archive) as tar:
        names = tar.getnames()
        readme = tar.extractfile("heimdall-guardian-cli-9.9.9/README.txt")
        assert readme is not None
        text = readme.read().decode()
        modes = {member.name: member.mode for member in tar.getmembers()}
    root = "heimdall-guardian-cli-9.9.9"
    assert names == [f"{root}/install_hdl.py", f"{root}/{wheel.name}", f"{root}/README.txt"]
    assert "Español" in text
    assert wheel.name in text
    assert modes[f"{root}/install_hdl.py"] == 0o755
    with pytest.raises(FileNotFoundError):
        tool.make_cli_archive("1.0.0", tmp_path / "missing.whl", output=tmp_path / "o2")


def test_the_app_stores_the_installer_as_text_and_runs_a_py_copy(tmp_path: Path) -> None:
    package = tmp_path / "pkg"
    cli = package / "_bundle" / "cli"
    cli.mkdir(parents=True)
    (cli / "install_hdl.py.txt").write_text("print('installer')\n")
    (cli / "heimdall_guardian-1.0.0-py3-none-any.whl").write_text("")
    files = cs.bundled_cli_files(package, tmp_path / "repo", runnable_dir=tmp_path / "run")
    assert files is not None
    assert files.script == tmp_path / "run" / "install_hdl.py"
    assert files.script.read_text() == "print('installer')\n"
    assert files.wheel is not None
    assert files.wheel.parent == cli


def test_the_app_build_pins_the_locked_flet_version() -> None:
    import tomllib

    root = Path(__file__).resolve().parents[2]
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    lock = tomllib.loads((root / "uv.lock").read_text(encoding="utf-8"))
    locked = next(p["version"] for p in lock["package"] if p["name"] == "flet")
    for platform in ("macos", "windows", "linux"):
        assert project["tool"]["flet"][platform]["dependencies"] == [f"flet=={locked}"]
