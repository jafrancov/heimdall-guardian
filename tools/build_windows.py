"""Builds the Windows application and its Inno Setup installer in `dist/`.

Usage:  python tools/build_windows.py

Requires Flutter, Visual Studio with the "Desktop development with C++" workload and
Inno Setup 6 or 7. Prepares the resources (`build_bundle.py`), runs `flet build windows` and
compiles `packaging/windows/heimdall-guardian.iss` with `iscc`. The installer is unsigned.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tomllib
from collections.abc import Mapping
from pathlib import Path

from flet_build import flet_build

REPO = Path(__file__).resolve().parents[1]
OUTPUT = REPO / "build" / "windows"
DIST = REPO / "dist"
SCRIPT = REPO / "packaging" / "windows" / "heimdall-guardian.iss"
# Written at 1024 px by build_bundle.py, which runs first.
ICON_PNG = REPO / "src" / "assets" / "icon.png"
ICON_ICO = REPO / "packaging" / "windows" / "icon.ico"
# Newest first. Per-user installs (no administrator rights) go under %LOCALAPPDATA%\Programs.
INNO_VERSIONS = ("7", "6")
INNO_ROOTS = ("ProgramFiles(x86)", "ProgramFiles", "LOCALAPPDATA")


def iscc_candidates(env: Mapping[str, str] | None = None) -> list[Path]:
    """Usual locations of `ISCC.exe` for Inno Setup 7 and 6, newest first."""
    env = os.environ if env is None else env
    candidates = []
    for version in INNO_VERSIONS:
        for root in INNO_ROOTS:
            base = env.get(root)
            if not base:
                continue
            folder = Path(base) / "Programs" if root == "LOCALAPPDATA" else Path(base)
            candidates.append(folder / f"Inno Setup {version}" / "ISCC.exe")
    return candidates


def find_iscc(env: Mapping[str, str] | None = None) -> str | None:
    """Path of the Inno Setup compiler, from the PATH or its usual install folders."""
    found = shutil.which("iscc")
    if found:
        return found
    for candidate in iscc_candidates(env):
        if candidate.is_file():
            return str(candidate)
    return None


def make_icon() -> Path | None:
    """Creates `icon.ico` from the app icon; `None` if Pillow is not available."""
    try:
        from PIL import Image
    except ImportError:
        return None
    with Image.open(ICON_PNG) as image:
        image.convert("RGBA").save(
            ICON_ICO, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (256, 256)]
        )
    return ICON_ICO


def find_exe() -> Path | None:
    """The executable `flet build` produced, whatever the product name turned out to be."""
    candidates = [p for p in OUTPUT.glob("*.exe") if "unins" not in p.name.lower()]
    return candidates[0] if candidates else None


def main() -> int:
    iscc = find_iscc()
    if iscc is None:
        print(
            "Inno Setup (ISCC.exe) was not found on the PATH or in the usual Inno Setup 7 "
            "and 6 folders. Install it (https://jrsoftware.org/isinfo.php, or "
            "`choco install innosetup`) or add the folder that holds ISCC.exe to the PATH.",
            file=sys.stderr,
        )
        return 1
    bundle = subprocess.run(
        [sys.executable, str(REPO / "tools" / "build_bundle.py")], cwd=REPO, check=False
    )
    if bundle.returncode != 0:
        return bundle.returncode
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    code = flet_build("windows")
    if code != 0:
        return code
    exe = find_exe()
    if exe is None:
        print(f"`flet build` left no .exe in {OUTPUT}.", file=sys.stderr)
        return 1
    version = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))["project"][
        "version"
    ]
    DIST.mkdir(exist_ok=True)
    command = [
        iscc,
        f"/DAppVersion={version}",
        f"/DSourceDir={OUTPUT}",
        f"/DAppExe={exe.name}",
        f"/DOutputDir={DIST}",
        f"/DLicenseFile={REPO / 'LICENSE'}",
    ]
    icon = make_icon()
    if icon is not None:
        command.append(f"/DIconFile={icon}")
    else:
        print("Pillow is not available: the installer will use the default icon.")
    command.append(str(SCRIPT))
    code = subprocess.run(command, cwd=REPO, check=False, env=os.environ.copy()).returncode
    if code == 0:
        setup = DIST / f"heimdall-guardian-{version}-windows-x64-setup.exe"
        print(f"Installer: {setup.relative_to(REPO)}. It is not signed.")
    return code


if __name__ == "__main__":
    sys.exit(main())
