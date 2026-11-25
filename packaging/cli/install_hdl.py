#!/usr/bin/env python3
"""Installs the `hdl` command (Heimdall Guardian, command line only) on your own Python.

Standard library only: this script runs before Heimdall exists, so it imports nothing from
the package. It keeps its own copy of the data-directory rules of
`heimdall_guardian.core.paths.data_dir()`; a unit test compares both.

    python3 install_hdl.py                     # latest release from PyPI
    python3 install_hdl.py --wheel PATH.whl    # a wheel you already have (offline)
    python3 install_hdl.py --uninstall         # removes the venv and the link, nothing else

It creates `<data>/cli/venv`, installs the package there and links `hdl` into a folder that
should be on your PATH. Databases, history and configuration are never touched.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

MINIMUM = (3, 12)
DOWNLOADS_URL = "https://www.python.org/downloads/"
APP_DIR = "Heimdall"
PACKAGE = "heimdall-guardian"
WINDOWS_BIN_NAME = "Heimdall Guardian"

# Visible texts, English and Spanish (es-MX). The script is stand-alone, so it has its own.
TEXTS: dict[str, dict[str, str]] = {
    "en": {
        "too_old": (
            "Heimdall Guardian needs Python {minimum} or newer; this is Python {found}.\n"
            "Install a current Python from {url} and run this script again with it."
        ),
        "apple_python": (
            "This looks like the Python that comes with macOS or the Xcode tools, which is "
            "too old and cannot be updated.\n"
            "The python.org installer puts a newer one next to it; then run "
            "`python3.12 install_hdl.py` (or the version you installed)."
        ),
        "plan": (
            "This will install Heimdall Guardian ({source}) into {venv} and link `hdl` in {bin}."
        ),
        "ask": "Continue? [y/N] ",
        "cancelled": "Nothing was installed.",
        "creating_venv": "Creating the virtual environment in {venv} ...",
        "venv_failed": (
            "Could not create the virtual environment: {error}\n"
            "On Debian and Ubuntu, install the `python3-venv` package first."
        ),
        "installing": "Installing {source} (this downloads the dependencies) ...",
        "pip_failed": "pip could not install Heimdall Guardian (exit code {code}).",
        "no_command": "The installed package has no `hdl` command at {path}.",
        "linked": "Command ready: {link}",
        "path_hint": (
            "{bin} is not on your PATH. Add this line to {rc} and open a new terminal:\n"
            '    export PATH="{bin}:$PATH"'
        ),
        "path_added": "{bin} was added to your user PATH. Open a new terminal to use `hdl`.",
        "foreign_link": "{link} exists and is not from this installer; it was left alone.",
        "status": "Tool status:",
        "uninstalled": "Removed {removed}. Your databases, history and settings were not touched.",
        "nothing_to_remove": "Nothing to remove: there is no installation in {venv}.",
        "done": "Done. Run `hdl --help` in a new terminal.",
    },
    "es": {
        "too_old": (
            "Heimdall Guardian necesita Python {minimum} o más nuevo; este es Python {found}.\n"
            "Instala un Python actual desde {url} y vuelve a ejecutar este script con él."
        ),
        "apple_python": (
            "Parece el Python que trae macOS o las herramientas de Xcode; es demasiado viejo y "
            "no se puede actualizar.\n"
            "El instalador de python.org pone uno más nuevo a su lado; luego ejecuta "
            "`python3.12 install_hdl.py` (o la versión que instalaste)."
        ),
        "plan": (
            "Esto instalará Heimdall Guardian ({source}) en {venv} y enlazará `hdl` en {bin}."
        ),
        "ask": "¿Continuar? [s/N] ",
        "cancelled": "No se instaló nada.",
        "creating_venv": "Creando el entorno virtual en {venv} ...",
        "venv_failed": (
            "No se pudo crear el entorno virtual: {error}\n"
            "En Debian y Ubuntu, instala antes el paquete `python3-venv`."
        ),
        "installing": "Instalando {source} (descarga las dependencias) ...",
        "pip_failed": "pip no pudo instalar Heimdall Guardian (código {code}).",
        "no_command": "El paquete instalado no trae el comando `hdl` en {path}.",
        "linked": "Comando listo: {link}",
        "path_hint": (
            "{bin} no está en tu PATH. Agrega esta línea a {rc} y abre una terminal nueva:\n"
            '    export PATH="{bin}:$PATH"'
        ),
        "path_added": (
            "Se agregó {bin} a tu PATH de usuario. Abre una terminal nueva para usar `hdl`."
        ),
        "foreign_link": "{link} ya existe y no es de este instalador; se dejó como estaba.",
        "status": "Estado de las herramientas:",
        "uninstalled": ("Se quitó {removed}. Tus bases, historial y ajustes no se tocaron."),
        "nothing_to_remove": "Nada que quitar: no hay instalación en {venv}.",
        "done": "Listo. Ejecuta `hdl --help` en una terminal nueva.",
    },
}


def choose_language(env: dict[str, str]) -> str:
    """`HDL_LANG`, then the locale variables; English by default."""
    for variable in ("HDL_LANG", "LC_ALL", "LC_MESSAGES", "LANG"):
        value = env.get(variable, "").strip().lower()
        if value:
            return "es" if value.startswith("es") else "en"
    return "en"


def say(lang: str, key: str, **params: object) -> str:
    return TEXTS[lang][key].format(**params)


def version_problem(
    version_info: tuple[int, ...], executable: str, lang: str, platform: str = sys.platform
) -> str | None:
    """The message to show when this Python is too old, or None when it is fine."""
    if tuple(version_info[:2]) >= MINIMUM:
        return None
    lines = [
        say(
            lang,
            "too_old",
            minimum=".".join(str(n) for n in MINIMUM),
            found=".".join(str(n) for n in version_info[:3]),
            url=DOWNLOADS_URL,
        )
    ]
    system_python = executable.startswith(("/usr/bin/", "/Library/Developer/"))
    if platform == "darwin" and (system_python or "Xcode" in executable):
        lines.append(say(lang, "apple_python"))
    return "\n".join(lines)


def data_dir(env: dict[str, str], platform: str, home: Path) -> Path:
    """Same rules as `heimdall_guardian.core.paths.data_dir()`."""
    override = env.get("HDL_DATA_DIR")
    if override:
        return Path(override)
    if platform == "darwin":
        return home / "Library" / "Application Support" / APP_DIR
    if platform == "win32":
        return Path(env.get("APPDATA", str(home / "AppData" / "Roaming"))) / APP_DIR
    return Path(env.get("XDG_DATA_HOME", str(home / ".local" / "share"))) / APP_DIR


def venv_dir(data: Path) -> Path:
    return data / "cli" / "venv"


def venv_hdl(venv: Path, platform: str) -> Path:
    return venv / "Scripts" / "hdl.exe" if platform == "win32" else venv / "bin" / "hdl"


def venv_python(venv: Path, platform: str) -> Path:
    return venv / "Scripts" / "python.exe" if platform == "win32" else venv / "bin" / "python"


def default_bin_dir(env: dict[str, str], platform: str, home: Path) -> Path:
    if platform == "win32":
        base = env.get("LOCALAPPDATA", str(home / "AppData" / "Local"))
        return Path(base) / "Programs" / WINDOWS_BIN_NAME / "bin"
    return home / ".local" / "bin"


def link_path(bin_dir: Path, platform: str) -> Path:
    return bin_dir / ("hdl.cmd" if platform == "win32" else "hdl")


def on_path(bin_dir: Path, path_value: str, platform: str = sys.platform) -> bool:
    separator = ";" if platform == "win32" else ":"
    wanted = os.path.normcase(os.path.normpath(str(bin_dir)))
    return any(
        os.path.normcase(os.path.normpath(entry)) == wanted
        for entry in path_value.split(separator)
        if entry
    )


def shell_rc(env: dict[str, str]) -> str:
    return "~/.zshrc" if os.path.basename(env.get("SHELL", "")) == "zsh" else "~/.bashrc"


def path_advice(bin_dir: Path, env: dict[str, str], lang: str, platform: str) -> str | None:
    """What to tell a POSIX user when the bin folder is not on the PATH (None if it is)."""
    if platform == "win32" or on_path(bin_dir, env.get("PATH", ""), platform):
        return None
    return say(lang, "path_hint", bin=bin_dir, rc=shell_rc(env))


def create_link(venv: Path, bin_dir: Path, platform: str) -> Path:
    """POSIX: a symlink to the venv's `hdl`; Windows: a `hdl.cmd` shim that calls it."""
    target = venv_hdl(venv, platform)
    link = link_path(bin_dir, platform)
    bin_dir.mkdir(parents=True, exist_ok=True)
    if link.is_symlink() or link.exists():
        link.unlink()
    if platform == "win32":
        link.write_text(f'@echo off\r\n"{target}" %*\r\n', encoding="utf-8")
    else:
        link.symlink_to(target)
    return link


def is_ours(link: Path, venv: Path, platform: str) -> bool:
    """True when the link or shim points into this installer's venv."""
    if platform == "win32":
        return link.is_file() and str(venv) in link.read_text(encoding="utf-8", errors="replace")
    if not link.is_symlink():
        return False
    return str(venv) in os.readlink(link)


def add_to_path_value(current: str, entry: str) -> str:
    """The Windows user PATH with `entry` appended once."""
    parts = [p for p in current.split(";") if p]
    if any(os.path.normcase(p) == os.path.normcase(entry) for p in parts):
        return current
    return ";".join([*parts, entry])


def remove_from_path_value(current: str, entry: str) -> str:
    parts = [p for p in current.split(";") if p]
    kept = [p for p in parts if os.path.normcase(p) != os.path.normcase(entry)]
    return ";".join(kept)


def _registry_path(change: Any) -> bool:  # pragma: no cover - Windows only
    """Reads the user PATH from HKCU\\Environment, applies `change`, writes it back."""
    import winreg

    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ | winreg.KEY_WRITE
    ) as key:
        try:
            current, kind = winreg.QueryValueEx(key, "Path")
        except FileNotFoundError:
            current, kind = "", winreg.REG_EXPAND_SZ
        updated = change(current)
        if updated == current:
            return False
        winreg.SetValueEx(key, "Path", 0, kind, updated)
    return True


def windows_path_add(bin_dir: Path) -> bool:  # pragma: no cover - Windows only
    return _registry_path(lambda current: add_to_path_value(current, str(bin_dir)))


def windows_path_remove(bin_dir: Path) -> bool:  # pragma: no cover - Windows only
    return _registry_path(lambda current: remove_from_path_value(current, str(bin_dir)))


def uninstall(data: Path, bin_dir: Path, platform: str, lang: str) -> list[str]:
    """Removes the venv and the link or shim (never databases, history or settings).

    Returns the human description of what was removed.
    """
    venv = venv_dir(data)
    removed: list[str] = []
    link = link_path(bin_dir, platform)
    if (link.is_symlink() or link.exists()) and is_ours(link, venv, platform):
        link.unlink()
        removed.append(str(link))
    if venv.exists():
        shutil.rmtree(venv)
        removed.append(str(venv))
        cli_dir = venv.parent
        if cli_dir.is_dir() and not any(cli_dir.iterdir()):
            cli_dir.rmdir()
    if platform == "win32" and removed:  # pragma: no cover - Windows only
        windows_path_remove(bin_dir)
    return removed


def _ask(lang: str) -> bool:
    answer = input(say(lang, "ask")).strip().lower()
    return answer in ("y", "yes", "s", "si", "sí")


def _install(args: argparse.Namespace, env: dict[str, str], platform: str, lang: str) -> int:
    data = data_dir(env, platform, Path.home())
    venv = venv_dir(data)
    bin_dir = args.bin_dir or default_bin_dir(env, platform, Path.home())
    source = (
        str(args.wheel) if args.wheel else f"{PACKAGE}=={args.version}" if args.version else PACKAGE
    )
    if args.wheel and not args.wheel.is_file():
        print(f"{args.wheel}: not found", file=sys.stderr)
        return 1
    print(say(lang, "plan", source=source, venv=venv, bin=bin_dir))
    if not args.yes and not _ask(lang):
        print(say(lang, "cancelled"))
        return 1

    print(say(lang, "creating_venv", venv=venv))
    venv.parent.mkdir(parents=True, exist_ok=True)
    created = subprocess.run(
        [sys.executable, "-m", "venv", str(venv)], capture_output=True, text=True, check=False
    )
    if created.returncode != 0:
        detail = (created.stderr or created.stdout).strip()
        print(say(lang, "venv_failed", error=detail), file=sys.stderr)
        return 1

    print(say(lang, "installing", source=source))
    # No `--user`, and the package itself is never built from source.
    pip = [
        str(venv_python(venv, platform)),
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        f"--only-binary={PACKAGE}",
        str(args.wheel) if args.wheel else source,
    ]
    sys.stdout.flush()
    installed = subprocess.run(pip, check=False)
    if installed.returncode != 0:
        print(say(lang, "pip_failed", code=installed.returncode), file=sys.stderr)
        return 1
    hdl = venv_hdl(venv, platform)
    if not hdl.is_file():
        print(say(lang, "no_command", path=hdl), file=sys.stderr)
        return 1

    link = link_path(bin_dir, platform)
    if (link.is_symlink() or link.exists()) and not is_ours(link, venv, platform):
        print(say(lang, "foreign_link", link=link), file=sys.stderr)
    else:
        print(say(lang, "linked", link=create_link(venv, bin_dir, platform)))
        if platform == "win32":  # pragma: no cover - Windows only
            windows_path_add(bin_dir)
            print(say(lang, "path_added", bin=bin_dir))
        else:
            advice = path_advice(bin_dir, env, lang, platform)
            if advice:
                print(advice)

    # The tools status (and the hint to `hdl tools --install`) comes from the command itself:
    # it sees what the desktop app already extracted into the shared data directory.
    print(say(lang, "status"), flush=True)
    subprocess.run([str(hdl), "tools"], env=env, check=False)
    print(say(lang, "done"))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="install_hdl.py", description="Installs the `hdl` command (Heimdall Guardian)."
    )
    parser.add_argument("--wheel", type=Path, help="install this wheel instead of PyPI (offline)")
    parser.add_argument("--version", help="version to install from PyPI (default: latest)")
    parser.add_argument("--bin-dir", type=Path, help="where to link `hdl` (default: per system)")
    parser.add_argument("--yes", action="store_true", help="do not ask for confirmation")
    parser.add_argument("--uninstall", action="store_true", help="remove the venv and the link")
    return parser


def main(argv: list[str] | None = None, env: dict[str, str] | None = None) -> int:
    environment = dict(os.environ) if env is None else env
    lang = choose_language(environment)
    problem = version_problem(sys.version_info, sys.executable, lang)
    if problem:
        print(problem, file=sys.stderr)
        return 1
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.wheel and args.version:
        parser.error("--wheel and --version cannot be used together")
    platform = sys.platform
    if args.uninstall:
        data = data_dir(environment, platform, Path.home())
        bin_dir = args.bin_dir or default_bin_dir(environment, platform, Path.home())
        removed = uninstall(data, bin_dir, platform, lang)
        if removed:
            print(say(lang, "uninstalled", removed=", ".join(removed)))
        else:
            print(say(lang, "nothing_to_remove", venv=venv_dir(data)))
        return 0
    return _install(args, environment, platform, lang)


if __name__ == "__main__":
    sys.exit(main())
