"""Builds the Linux application and its packages (`.tar.gz` and `.deb`) in `dist/`.

Usage:  python tools/build_linux.py

Requires Flutter and its Linux desktop dependencies (see CONTRIBUTING). Prepares the
resources (`build_bundle.py`), runs `flet build linux` and packs `build/linux/` as a
tarball (with a `.desktop` file and the icon) and, if `dpkg-deb` is installed, as a Debian
package that installs into `/opt/heimdall-guardian`. It also writes the CLI-only archive
(`build_cli_archive.py`) for servers.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
from pathlib import Path

from flet_build import flet_build

REPO = Path(__file__).resolve().parents[1]
OUTPUT = REPO / "build" / "linux"
DIST = REPO / "dist"
DESKTOP = REPO / "packaging" / "linux" / "heimdall-guardian.desktop"
# Written at 1024 px by build_bundle.py, which runs first.
ICON_PNG = REPO / "src" / "assets" / "icon.png"
NAME = "heimdall-guardian"
# Runtime libraries of a Flutter GTK desktop app. The Flet client also links libmpv for
# media playback, so it is declared too; the package manager pulls its dependencies.
DEPENDS = "libgtk-3-0, libmpv2 | libmpv1, libsecret-1-0"
CONTROL = """\
Package: {name}
Version: {version}
Architecture: amd64
Maintainer: Alejandro Franco <jafrancov@users.noreply.github.com>
Section: devel
Priority: optional
Depends: {depends}
Homepage: https://github.com/jafrancov/heimdall-guardian
Description: Local, read-only static security analysis of source code
 Heimdall Guardian orchestrates static analysis tools (secrets, dependencies, SAST,
 configuration, endpoints) on a local folder without running its code, and writes
 reports. This package is not signed.
"""


def find_executable() -> Path:
    """The main executable `flet build` left in the bundle folder."""
    for path in sorted(OUTPUT.iterdir()):
        if path.is_file() and os.access(path, os.X_OK) and ".so" not in path.name:
            return path
    raise FileNotFoundError(f"`flet build` left no executable in {OUTPUT}")


def icon_512(target: Path) -> None:
    """Writes the icon as 512x512 PNG (resized with Pillow when available)."""
    try:
        from PIL import Image
    except ImportError:
        shutil.copyfile(ICON_PNG, target)
        return
    with Image.open(ICON_PNG) as image:
        image.convert("RGBA").resize((512, 512), Image.Resampling.LANCZOS).save(target)


def make_tarball(version: str, executable: Path) -> Path:
    """`.tar.gz` with the bundle folder, the `.desktop` file and the icon."""
    archive = DIST / f"{NAME}-{version}-linux-x64.tar.gz"
    root = f"{NAME}-{version}"
    with tempfile.TemporaryDirectory(prefix="heimdall-icon-") as tmp:
        icon = Path(tmp) / f"{NAME}.png"
        icon_512(icon)
        with tarfile.open(archive, "w:gz") as tar:
            tar.add(OUTPUT, arcname=f"{root}/app")
            tar.add(DESKTOP, arcname=f"{root}/{NAME}.desktop")
            tar.add(icon, arcname=f"{root}/{NAME}.png")
    print(f"Run it with: {root}/app/{executable.name}")
    return archive


def make_deb(version: str, executable: Path) -> Path | None:
    """`.deb` installing into `/opt`; `None` (with a message) if `dpkg-deb` is missing."""
    if shutil.which("dpkg-deb") is None:
        print("dpkg-deb not found: skipping the .deb package.")
        return None
    package = DIST / f"{NAME}_{version}_amd64.deb"
    with tempfile.TemporaryDirectory(prefix="heimdall-deb-") as tmp:
        stage = Path(tmp)
        opt = stage / "opt" / NAME
        shutil.copytree(OUTPUT, opt, symlinks=True)
        (stage / "usr" / "bin").mkdir(parents=True)
        (stage / "usr" / "bin" / NAME).symlink_to(f"/opt/{NAME}/{executable.name}")
        applications = stage / "usr" / "share" / "applications"
        applications.mkdir(parents=True)
        shutil.copyfile(DESKTOP, applications / f"{NAME}.desktop")
        icons = stage / "usr" / "share" / "icons" / "hicolor" / "512x512" / "apps"
        icons.mkdir(parents=True)
        icon_512(icons / f"{NAME}.png")
        debian = stage / "DEBIAN"
        debian.mkdir()
        (debian / "control").write_text(
            CONTROL.format(name=NAME, version=version, depends=DEPENDS), encoding="utf-8"
        )
        for folder, _dirs, _files in os.walk(stage):
            Path(folder).chmod(0o755)
        package.unlink(missing_ok=True)
        subprocess.run(
            ["dpkg-deb", "--build", "--root-owner-group", str(stage), str(package)], check=True
        )
    return package


def main() -> int:
    bundle = subprocess.run(
        [sys.executable, str(REPO / "tools" / "build_bundle.py")], cwd=REPO, check=False
    )
    if bundle.returncode != 0:
        return bundle.returncode
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    code = flet_build("linux")
    if code != 0:
        return code
    version = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))["project"][
        "version"
    ]
    DIST.mkdir(exist_ok=True)
    executable = find_executable()
    print(f"Package: {make_tarball(version, executable).relative_to(REPO)}")
    from build_cli_archive import CLI_WHEELS, make_cli_archive

    wheel = CLI_WHEELS / f"heimdall_guardian-{version}-py3-none-any.whl"
    print(f"Package: {make_cli_archive(version, wheel).relative_to(REPO)} (servers, no desktop)")
    deb = make_deb(version, executable)
    if deb is not None:
        print(f"Package: {deb.relative_to(REPO)}. It is not signed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
