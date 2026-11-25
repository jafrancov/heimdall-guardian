"""Builds the desktop application and installer for the operating system running this script.

Usage:  python tools/build_app.py [--dry-run]

Picks the build script by platform: macOS -> `build_macos.py` (`.app` + `.dmg`), Windows ->
`build_windows.py` (Inno Setup installer), Linux -> `build_linux.py` (`.tar.gz` + `.deb`).
Everything lands in `dist/`. The light CLI wheel is built first (`build_cli_wheel.py`) because
the app carries it. `--dry-run` only prints which script would run.
"""

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = {
    "darwin": "build_macos.py",
    "win32": "build_windows.py",
    "linux": "build_linux.py",
}


def project_version() -> str:
    """The version declared in `pyproject.toml`."""
    data = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def main(argv: list[str]) -> int:
    script = SCRIPTS.get(sys.platform)
    if script is None:
        supported = ", ".join(sorted(SCRIPTS))
        print(
            f"Unsupported platform '{sys.platform}'. Supported: {supported}.",
            file=sys.stderr,
        )
        return 2
    path = REPO / "tools" / script
    if "--dry-run" in argv:
        print(f"Heimdall Guardian {project_version()} on {sys.platform}: would run {path}")
        return 0
    # The app carries the light CLI wheel, so it is built first (it rebuilds `_bundle/`
    # without binaries; the platform script then rebuilds it in full and copies the wheel).
    wheel = subprocess.run(
        [sys.executable, str(REPO / "tools" / "build_cli_wheel.py")], cwd=REPO, check=False
    )
    if wheel.returncode != 0:
        return wheel.returncode
    return subprocess.run([sys.executable, str(path)], cwd=REPO, check=False).returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
