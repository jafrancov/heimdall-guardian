"""Installing the `hdl` command from the desktop app.

The app carries `install_hdl.py` and a light wheel in `_bundle/cli/`; this module finds them,
finds a usable Python on the machine (the app runs with a minimal PATH, so the usual places are
looked at one by one), reports whether the command is installed and builds and runs the
installer. Everything that touches the machine is injectable so tests use fakes.
"""

from __future__ import annotations

import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .paths import data_dir
from .processes import no_window

MINIMUM_PYTHON = (3, 12)
DOWNLOADS_URL = "https://www.python.org/downloads/"
OFFER_MARKER = "cli_offer_shown"
WHEEL_PATTERN = "heimdall_guardian-*-py3-none-any.whl"
SCRIPT_NAME = "install_hdl.py"
# Inside the app the installer is stored as plain text: `flet build` compiles every `.py`
# of the app to bytecode for its own Python, which the user's Python could not run.
BUNDLED_SCRIPT_NAME = SCRIPT_NAME + ".txt"
WINDOWS_BIN_NAME = "Heimdall Guardian"
_PROBE_TIMEOUT = 15
_INSTALL_TIMEOUT = 900
_PROBE_CODE = "import sys; print(sys.version_info[0], sys.version_info[1], sys.executable)"
# The Python of the macOS system and of the Xcode tools: older than the minimum, and running
# it without the tools installed pops up the developer tools installer.
_APPLE_PREFIXES = ("/usr/bin/", "/Library/Developer/")
# Variables that would make the user's Python load the app's own (bundled) interpreter state.
_PYTHON_ENV_VARS = (
    "PYTHONHOME",
    "PYTHONPATH",
    "PYTHONSTARTUP",
    "PYTHONEXECUTABLE",
    "VIRTUAL_ENV",
    "__PYVENV_LAUNCHER__",
)

_PACKAGE = Path(__file__).resolve().parents[1]
_REPO = _PACKAGE.parents[1]


@dataclass(frozen=True)
class CliFiles:
    """The installer script and the wheel to install (the wheel is optional)."""

    script: Path
    wheel: Path | None


@dataclass(frozen=True)
class PythonInfo:
    """A Python that meets the minimum: its executable and (major, minor)."""

    path: str
    version: tuple[int, int]


@dataclass(frozen=True)
class CliStatus:
    """Whether the `hdl` command of this installer exists, and where."""

    installed: bool
    command: Path  # the `hdl` inside the virtual environment
    link: Path | None  # the symlink or shim on the user's bin folder, when it exists
    version: str | None


@dataclass(frozen=True)
class RunResult:
    returncode: int
    output: str


def _version_key(name: str) -> tuple[int, ...]:
    return tuple(int(n) for n in re.findall(r"\d+", name))


# ------------------------------------------------------------------- bundled files


def bundled_cli_files(
    package_dir: Path = _PACKAGE, repo: Path = _REPO, runnable_dir: Path | None = None
) -> CliFiles | None:
    """The installer and the wheel inside the app, or in a development checkout.

    Returns None when there is no installer script at all.
    """
    bundled = package_dir / "_bundle" / "cli"
    stored = bundled / BUNDLED_SCRIPT_NAME
    if stored.is_file():
        return CliFiles(_runnable_copy(stored, runnable_dir), _newest(bundled))
    script = bundled / SCRIPT_NAME
    if script.is_file():
        return CliFiles(script, _newest(bundled))
    script = repo / "packaging" / "cli" / SCRIPT_NAME
    if script.is_file():
        return CliFiles(script, _newest(repo / "dist" / "cli"))
    return None


def _runnable_copy(stored: Path, runnable_dir: Path | None) -> Path:
    """Writes the stored installer as a `.py` the user's Python can run (outside any project)."""
    target_dir = runnable_dir or Path(tempfile.gettempdir()) / "heimdall-cli-installer"
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / SCRIPT_NAME
    target.write_bytes(stored.read_bytes())
    return target


def _newest(folder: Path) -> Path | None:
    wheels = sorted(folder.glob(WHEEL_PATTERN), key=lambda p: _version_key(p.name))
    return wheels[-1] if wheels else None


# ---------------------------------------------------------------- finding a Python


def _probe(command: Sequence[str]) -> str | None:
    """Runs the candidate with a fixed one-liner; its output, or None if it does not run."""
    try:
        done = subprocess.run(
            [*command, "-I", "-c", _PROBE_CODE],
            capture_output=True,
            text=True,
            timeout=_PROBE_TIMEOUT,
            stdin=subprocess.DEVNULL,
            check=False,
            **no_window(),
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return done.stdout if done.returncode == 0 else None


def _registry_pythons() -> list[str]:
    """Pythons registered under `Software\\Python` (PEP 514), newest first; Windows only.

    The python.org installer, the Python install manager, uv and conda register their
    interpreters there, wherever they were installed.
    """
    if sys.platform != "win32":
        return []
    import winreg

    found: list[tuple[tuple[int, ...], str]] = []
    places = (
        (winreg.HKEY_CURRENT_USER, 0),
        (winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY),
        (winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY),
    )
    for hive, view in places:
        try:
            root = winreg.OpenKey(hive, r"Software\Python", 0, winreg.KEY_READ | view)
        except OSError:
            continue
        with root:
            for company in _subkeys(winreg, root):
                try:
                    company_key = winreg.OpenKey(root, company)
                except OSError:
                    continue
                with company_key:
                    for tag in _subkeys(winreg, company_key):
                        exe = _registered_executable(winreg, company_key, tag)
                        if exe:
                            found.append((_version_key(tag), exe))
    return [exe for _, exe in sorted(found, key=lambda item: item[0], reverse=True)]


def _subkeys(winreg: Any, key: Any) -> list[str]:
    names: list[str] = []
    index = 0
    while True:
        try:
            names.append(winreg.EnumKey(key, index))
        except OSError:
            return names
        index += 1


def _registered_executable(winreg: Any, company_key: Any, tag: str) -> str | None:
    try:
        with winreg.OpenKey(company_key, tag + r"\InstallPath") as install:
            try:
                return str(winreg.QueryValueEx(install, "ExecutablePath")[0])
            except OSError:
                folder = str(winreg.QueryValueEx(install, "")[0])
                return str(Path(folder) / "python.exe")
    except OSError:
        return None


def _candidates(
    platform: str,
    env: Mapping[str, str],
    which: Callable[[str], str | None],
    exists: Callable[[str], bool],
    find: Callable[[str], list[str]],
    registry: Callable[[], list[str]] = _registry_pythons,
) -> list[list[str]]:
    found: list[list[str]] = []
    if platform == "darwin":
        frameworks = find("/Library/Frameworks/Python.framework/Versions/*/bin/python3")
        found += [[p] for p in sorted(frameworks, key=_version_key, reverse=True)]
        found += [[p] for p in ("/opt/homebrew/bin/python3", "/usr/local/bin/python3")]
    elif platform == "win32":
        found += [[p] for p in registry()]
        local = env.get("LOCALAPPDATA")
        launchers = []
        windir = env.get("WINDIR") or env.get("SystemRoot")
        if windir:
            launchers.append(str(Path(windir) / "py.exe"))
        if local:
            launchers.append(str(Path(local) / "Programs" / "Python" / "Launcher" / "py.exe"))
        found += [[launcher, "-3"] for launcher in launchers if exists(launcher)]
        patterns = []
        if local:
            # python.org per user, and the Python install manager (pymanager).
            patterns.append(Path(local) / "Programs" / "Python" / "Python3*" / "python.exe")
            patterns.append(Path(local) / "Python" / "pythoncore-3*" / "python.exe")
        for variable in ("ProgramFiles", "ProgramFiles(x86)"):
            if env.get(variable):
                # python.org for all users.
                patterns.append(Path(env[variable]) / "Python3*" / "python.exe")
        for pattern in patterns:
            found += [[p] for p in sorted(find(str(pattern)), key=_version_key, reverse=True)]
    else:
        found += [[p] for p in ("/usr/bin/python3", "/usr/local/bin/python3")]
    for name in ("python3", "python"):
        path = which(name)
        if path:
            found.append([path])
    return found


def _usable_path(command: list[str], platform: str) -> bool:
    """Skips the Apple system Python and the Windows Store stub without running them."""
    path = command[0].replace("\\", "/")
    if platform == "darwin" and (path.startswith(_APPLE_PREFIXES) or "/Xcode" in path):
        return False
    return not (platform == "win32" and "WindowsApps" in path)


def _parse(output: str, minimum: tuple[int, int]) -> PythonInfo | None:
    lines = output.strip().splitlines()
    if not lines:
        return None
    parts = lines[-1].split(None, 2)
    if len(parts) != 3 or not (parts[0].isdigit() and parts[1].isdigit()):
        return None
    version = (int(parts[0]), int(parts[1]))
    return PythonInfo(parts[2], version) if version >= minimum else None


def find_python(
    minimum: tuple[int, int] = MINIMUM_PYTHON,
    *,
    platform: str = sys.platform,
    env: Mapping[str, str] | None = None,
    probe: Callable[[Sequence[str]], str | None] = _probe,
    which: Callable[[str], str | None] = shutil.which,
    exists: Callable[[str], bool] = os.path.exists,
    find: Callable[[str], list[str]] = glob.glob,
    registry: Callable[[], list[str]] = _registry_pythons,
) -> PythonInfo | None:
    """The first Python of at least `minimum` in the usual places, or None.

    The desktop app starts with a minimal PATH, so the python.org and Homebrew locations (on
    Windows, the registered interpreters and the usual install folders) are tried before
    whatever the PATH offers.
    """
    environment = os.environ if env is None else env
    seen: set[str] = set()
    for command in _candidates(platform, environment, which, exists, find, registry):
        key = " ".join(command)
        if key in seen or not _usable_path(command, platform):
            continue
        seen.add(key)
        if len(command) == 1 and not exists(command[0]):
            continue
        output = probe(command)
        info = _parse(output, minimum) if output else None
        if info is not None:
            return info
    return None


# --------------------------------------------------------------------------- status


def venv_command(data: Path, platform: str = sys.platform) -> Path:
    venv = data / "cli" / "venv"
    return venv / "Scripts" / "hdl.exe" if platform == "win32" else venv / "bin" / "hdl"


def venv_python(data: Path, platform: str = sys.platform) -> Path:
    venv = data / "cli" / "venv"
    return venv / "Scripts" / "python.exe" if platform == "win32" else venv / "bin" / "python"


def default_bin_dir(env: Mapping[str, str], platform: str, home: Path) -> Path:
    """Same folder the installer links `hdl` in by default."""
    if platform == "win32":
        base = env.get("LOCALAPPDATA", str(home / "AppData" / "Local"))
        return Path(base) / "Programs" / WINDOWS_BIN_NAME / "bin"
    return home / ".local" / "bin"


def installed_version(data: Path) -> str | None:
    """The version of the package inside the venv, from its dist-info folder name."""
    venv = data / "cli" / "venv"
    pattern = "heimdall_guardian-*.dist-info"
    found = [
        *venv.glob(f"lib/python*/site-packages/{pattern}"),
        *venv.glob(f"Lib/site-packages/{pattern}"),
    ]
    for folder in found:
        match = re.fullmatch(r"heimdall_guardian-(.+)\.dist-info", folder.name)
        if match:
            return match.group(1)
    return None


def cli_status(
    data: Path | None = None,
    *,
    platform: str = sys.platform,
    env: Mapping[str, str] | None = None,
    home: Path | None = None,
    bin_dir: Path | None = None,
) -> CliStatus:
    """Looks at the disk only: the command exists when the venv has its `hdl`."""
    folder = data_dir() if data is None else data
    environment = os.environ if env is None else env
    command = venv_command(folder, platform)
    installed = command.is_file()
    link: Path | None = None
    if installed:
        base = bin_dir or default_bin_dir(environment, platform, home or Path.home())
        candidate = base / ("hdl.cmd" if platform == "win32" else "hdl")
        if candidate.is_symlink() or candidate.exists():
            link = candidate
    return CliStatus(installed, command, link, installed_version(folder) if installed else None)


# ---------------------------------------------------------------- running it


def install_command(python: str, files: CliFiles, *, bin_dir: Path | None = None) -> list[str]:
    """The installer command line; without a wheel it installs the release from PyPI."""
    command = [python, str(files.script)]
    if files.wheel is not None:
        command += ["--wheel", str(files.wheel)]
    if bin_dir is not None:
        command += ["--bin-dir", str(bin_dir)]
    return [*command, "--yes"]


def uninstall_command(python: str, files: CliFiles, *, bin_dir: Path | None = None) -> list[str]:
    command = [python, str(files.script), "--uninstall"]
    if bin_dir is not None:
        command += ["--bin-dir", str(bin_dir)]
    return [*command, "--yes"]


def installer_env(lang: str, base: Mapping[str, str] | None = None) -> dict[str, str]:
    """The environment for the installer: the app's language and no leftovers of its Python."""
    env = dict(os.environ if base is None else base)
    for name in _PYTHON_ENV_VARS:
        env.pop(name, None)
    env["HDL_LANG"] = lang
    return env


def run_installer(
    command: Sequence[str],
    lang: str,
    *,
    timeout: float = _INSTALL_TIMEOUT,
    env: Mapping[str, str] | None = None,
) -> RunResult:
    """Runs the installer capturing its output (stdout and stderr together)."""
    try:
        done = subprocess.run(
            list(command),
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout,
            stdin=subprocess.DEVNULL,
            env=installer_env(lang, env),
            check=False,
            **no_window(),
        )
    except subprocess.TimeoutExpired:
        return RunResult(1, "timeout")
    except OSError as exc:
        return RunResult(1, str(exc))
    # Order is lost between the two streams; the installer keeps its errors on stderr only.
    return RunResult(done.returncode, "\n".join(s for s in (done.stdout, done.stderr) if s))


# ---------------------------------------------------------------- reading output


def output_tail(output: str, lines: int = 12) -> list[str]:
    """The last non-empty lines of the installer output (for the failure dialog)."""
    kept = [line.rstrip() for line in output.splitlines() if line.strip()]
    return kept[-lines:]


def path_advice(output: str) -> list[str]:
    """The installer's PATH advice: the line with `export PATH=` and the sentence before it."""
    lines = [line.rstrip() for line in output.splitlines()]
    for index, line in enumerate(lines):
        if "export PATH=" in line and index > 0:
            return [lines[index - 1], line]
    return []


# --------------------------------------------------------------------- first offer


def offer_marker() -> Path:
    return data_dir() / OFFER_MARKER


def offer_due(marker: Path, installed: bool) -> bool:
    """The one-off offer is made once, and only when the command is not installed."""
    return not installed and not marker.exists()


def mark_offered(marker: Path) -> None:
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("1\n", encoding="utf-8")
