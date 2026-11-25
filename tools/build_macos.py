"""Builds the macOS application and its `.dmg` installer in `dist/`.

The installer is assembled with `diskutil image` (blank APFS image, copy, Finder layout
written with `ds-store` and `mac-alias`, compressed UDZO); `hdiutil` is not used.

Usage:  python tools/build_macos.py

Requires Flutter and Xcode. Prepares the resources (`build_bundle.py`) and runs
`flet build macos`. The Flet 1.0.4 template pinned macOS 11 as the minimum version and
Xcode 27 requires 12 or later (the 1.1.3 template already says 12.0, so the patch is
harmless there, but it still adds the per-pod deployment target): the official template zip
(from Flet's own cache) is extracted to `build/flet-template/` with the minimum raised and
passed with `--template`, so the first build succeeds. If that is not possible, or the build
still fails, the generated project is fixed and the build is retried.
"""

from __future__ import annotations

import contextlib
import os
import platform
import plistlib
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import tomllib
import zipfile
from collections.abc import Callable
from pathlib import Path

from flet_build import flet_build

REPO = Path(__file__).resolve().parents[1]
OUTPUT = REPO / "build" / "macos"
MACOS = REPO / "build" / "flutter" / "macos"
MINIMUM = "12.0"
VOLUME = "Heimdall Guardian"
# Installer window in points: half the background (1672x941 px, Retina).
BACKGROUND = REPO / "assets" / "Heimdall_Guardian_bifrost.png"
WINDOW = (836, 470)
# The real icons go over the two empty boxes in the background (measured in pixels and
# divided by 2): application centered at (703, 482) and ~207 px wide, Applications
# folder at (1400, 492) and ~186 px. A macOS icon fills ~80 % of its box;
# at 108 pt the folder (the widest) fills its box and the app sits slightly inside its own.
ICON_SIZE = 108
TEXT_SIZE = 11
APP_AT = (352, 241)
APPLICATIONS_AT = (700, 246)
_POD_SETTING = (
    "    target.build_configurations.each do |config|\n"
    f"      config.build_settings['MACOSX_DEPLOYMENT_TARGET'] = '{MINIMUM}'\n"
    "    end\n"
)


def patch_podfile(text: str) -> str:
    """Raises the minimum macOS version in the text of a Podfile."""
    patched = text.replace("platform :osx, '11.0'", f"platform :osx, '{MINIMUM}'")
    anchor = "    flutter_additional_macos_build_settings(target)\n"
    if _POD_SETTING not in patched and anchor in patched:
        patched = patched.replace(anchor, anchor + _POD_SETTING, 1)
    return patched


def patch_project(text: str) -> str:
    """Raises the minimum macOS version in the text of a `project.pbxproj`."""
    return text.replace(
        "MACOSX_DEPLOYMENT_TARGET = 11.0;", f"MACOSX_DEPLOYMENT_TARGET = {MINIMUM};"
    )


def _patch_file(path: Path, patch: Callable[[str], str]) -> bool:
    text = path.read_text(encoding="utf-8")
    patched = patch(text)
    if patched == text:
        return False
    path.write_text(patched, encoding="utf-8")
    return True


def raise_deployment_target() -> bool:
    """Raises the minimum macOS version in the generated project; `True` if anything changed."""
    podfile = MACOS / "Podfile"
    project = MACOS / "Runner.xcodeproj" / "project.pbxproj"
    if not podfile.is_file() or not project.is_file():
        return False
    changed = _patch_file(podfile, patch_podfile)
    return _patch_file(project, patch_project) or changed


def patched_template() -> Path | None:
    """Extracts Flet's official template with the minimum macOS version raised.

    Returns the folder to pass to `flet build --template`, or `None` (with a notice)
    if it cannot be prepared; the build then uses Flet's template as is.
    """
    try:
        from flet.version import flet_version
        from flet_cli.utils.template_cache import get_cached_template_zip

        url = f"https://github.com/flet-dev/flet/releases/download/v{flet_version}/flet-build-template.zip"
        archive = get_cached_template_zip(url, flet_version)
        target = REPO / "build" / "flet-template" / flet_version
        shutil.rmtree(target, ignore_errors=True)
        target.mkdir(parents=True)
        with zipfile.ZipFile(archive) as bundle:
            bundle.extractall(target)
        manifests = sorted(target.rglob("cookiecutter.json"), key=lambda p: len(p.parts))
        if not manifests:
            raise FileNotFoundError("cookiecutter.json not found in the template")
        for podfile in target.rglob("Podfile"):
            if "macos" in podfile.parts:
                _patch_file(podfile, patch_podfile)
        for project in target.rglob("project.pbxproj"):
            if "macos" in project.parts:
                _patch_file(project, patch_project)
        return manifests[0].parent
    except Exception as exc:
        print(f"Could not prepare the patched Flet template ({exc}); using the default one.")
        return None


def clean_output() -> None:
    """Deletes the previous output of `flet build`.

    Sometimes it is left with permissions that make it unreadable (`d-w-------`), Flet cannot
    replace it and the build fails after several minutes. The owner's permissions
    are restored before deleting.
    """
    if not OUTPUT.exists():
        return
    # Top to bottom: each folder regains permissions before its contents are read.
    OUTPUT.chmod(OUTPUT.stat().st_mode | stat.S_IRWXU)
    for folder, dirs, files in os.walk(OUTPUT, topdown=True):
        for name in [*dirs, *files]:
            path = Path(folder) / name
            if not path.is_symlink():
                path.chmod(path.stat().st_mode | stat.S_IRWXU)
    # If the folder is open in Finder, Finder recreates `.DS_Store` while it is
    # being deleted and `rmtree` fails with «Directory not empty»: retry.
    for attempt in range(5):
        try:
            shutil.rmtree(OUTPUT)
            return
        except OSError:
            if attempt == 4:
                raise
            time.sleep(1)


def retina_background(tmp: Path) -> Path:
    """Multi-resolution TIFF of the background: 1x for normal displays, original art as 2x."""
    original = tmp / "fondo@2x.png"
    normal = tmp / "fondo.png"
    shutil.copyfile(BACKGROUND, original)
    shutil.copyfile(BACKGROUND, normal)
    sips = ["sips", "-s", "dpiWidth"]
    # `tiffutil -cathidpicheck` requires 72 dpi on the 1x and 144 on the 2x.
    subprocess.run(
        [*sips, "144", "-s", "dpiHeight", "144", str(original)], check=True, capture_output=True
    )
    subprocess.run(
        ["sips", "-z", str(WINDOW[1]), str(WINDOW[0]), str(normal)], check=True, capture_output=True
    )
    subprocess.run(
        [*sips, "72", "-s", "dpiHeight", "72", str(normal)], check=True, capture_output=True
    )
    tiff = tmp / "fondo.tiff"
    subprocess.run(
        ["tiffutil", "-cathidpicheck", str(normal), str(original), "-out", str(tiff)],
        check=True,
        capture_output=True,
    )
    return tiff


def _tree_size(folder: Path) -> int:
    """Sum of the file sizes under `folder` (symlinks count as their own link, not the target)."""
    total = 0
    for base, _dirs, files in os.walk(folder):
        for name in files:
            with contextlib.suppress(OSError):
                total += os.lstat(os.path.join(base, name)).st_size
    return total


def _write_ds_store(mount: Path, app_name: str, background: Path) -> None:
    """Writes the Finder layout of the disk (`.DS_Store`).

    These records mirror what dmgbuild wrote for our settings (same keys, value types and
    defaults for the fields we do not set), so the window looks exactly as before.
    """
    from ds_store import DSStore  # dev group
    from mac_alias import Alias

    (left, top), (width, height) = (200, 120), WINDOW
    bwsp = {
        "ShowStatusBar": False,
        "WindowBounds": f"{{{{{left}, {top}}}, {{{width}, {height}}}}}",
        "ContainerShowSidebar": False,
        "PreviewPaneVisibility": False,
        "SidebarWidth": 180,
        "ShowTabView": False,
        "ShowToolbar": False,
        "ShowPathbar": False,
        "ShowSidebar": False,
    }
    alias = Alias.for_file(str(background))
    # Finder resolves the alias by volume name and file ID; record the usual mount path
    # even if this disk is mounted elsewhere while it is assembled.
    alias.volume.posix_path = f"/Volumes/{VOLUME}"
    icvp = {
        "viewOptionsVersion": 1,
        "backgroundType": 2,
        "backgroundColorRed": 1.0,
        "backgroundColorGreen": 1.0,
        "backgroundColorBlue": 1.0,
        "gridOffsetX": 0.0,
        "gridOffsetY": 0.0,
        "gridSpacing": 100.0,
        "arrangeBy": "none",
        "showIconPreview": False,
        "showItemInfo": False,
        "labelOnBottom": True,
        "textSize": float(TEXT_SIZE),
        "iconSize": float(ICON_SIZE),
        "scrollPositionX": 0.0,
        "scrollPositionY": 0.0,
        "backgroundImageAlias": alias.to_bytes(),
    }
    with DSStore.open(str(mount / ".DS_Store"), "w+") as store:
        store["."]["vSrn"] = ("long", 1)
        store["."]["bwsp"] = bwsp
        store["."]["icvp"] = icvp
        store["."]["icvl"] = (b"type", b"icnv")
        store[app_name]["Iloc"] = APP_AT
        store["Applications"]["Iloc"] = APPLICATIONS_AT


def _attached_device(plist: bytes) -> str:
    """The whole-disk device (`/dev/diskN`) that `diskutil image attach --plist` reports."""
    entities = plistlib.loads(plist).get("system-entities", [])
    for entity in entities:
        entry = str(entity.get("dev-entry", ""))
        if entry and "s" not in entry.removeprefix("disk"):
            return f"/dev/{entry}"
    raise RuntimeError(f"diskutil did not report a device: {entities!r}")


def _build_disk_image(app: Path, image: Path, tmp: Path) -> None:
    """One attempt: blank read-write HFS+ image, fill, lay out, eject, compress."""
    megabyte = 1024 * 1024
    size = -(-int(_tree_size(app) * 1.25 + 32 * megabyte) // megabyte) * megabyte
    scratch = tmp / "rw.dmg"
    mount = tmp / "mnt"
    scratch.unlink(missing_ok=True)
    mount.mkdir(exist_ok=True)
    # HFS+ like the installers made with dmgbuild: on APFS, Finder does not resolve the
    # background alias. `diskutil image` only formats APFS, so the blank image is attached
    # without a file system and formatted with `newfs_hfs` (no partition map).
    subprocess.run(
        ["diskutil", "image", "create", "blank", "--fs", "None", "--size", str(size), str(scratch)],
        check=True, capture_output=True, text=True,
    )  # fmt: skip
    attached = subprocess.run(
        ["diskutil", "image", "attach", "--mountPolicy", "noMount", "--plist", str(scratch)],
        check=True, capture_output=True,
    )  # fmt: skip
    device = _attached_device(attached.stdout)
    try:
        subprocess.run(
            ["newfs_hfs", "-v", VOLUME, device], check=True, capture_output=True, text=True
        )
        subprocess.run(
            [
                "diskutil", "mount", "-mountOptions", "nobrowse", "-mountPoint", str(mount),
                device,
            ],
            check=True, capture_output=True, text=True,
        )  # fmt: skip
    except subprocess.CalledProcessError:
        subprocess.run(["diskutil", "eject", device], capture_output=True, check=False)
        raise
    try:
        # `ditto` preserves the signature, permissions and attributes of the bundle.
        subprocess.run(
            ["ditto", str(app), str(mount / app.name)],
            check=True, capture_output=True, text=True,
        )  # fmt: skip
        (mount / "Applications").symlink_to("/Applications")
        background = mount / ".background.tiff"
        shutil.copyfile(retina_background(tmp), background)
        _write_ds_store(mount, app.name, background)
        for leftover in (".Trashes", ".fseventsd"):
            shutil.rmtree(mount / leftover, ignore_errors=True)
    finally:
        eject = ["diskutil", "eject", str(mount)]
        if subprocess.run(eject, capture_output=True, check=False).returncode != 0:
            time.sleep(2)
            subprocess.run(eject, capture_output=True, check=True)
    image.unlink(missing_ok=True)
    subprocess.run(
        ["diskutil", "image", "create", "from", "--format", "UDZO", str(scratch), str(image)],
        check=True, capture_output=True, text=True,
    )  # fmt: skip


def disk_image(app: Path, image: Path) -> int:
    """Creates the `.dmg` with background and icon positions; retries if the disk is busy."""
    error: Exception | None = None
    for attempt in range(3):
        if attempt:
            time.sleep(5)
        with tempfile.TemporaryDirectory(prefix="heimdall-dmg-") as tmp:
            try:
                _build_disk_image(app, image, Path(tmp))
                return 0
            except (OSError, subprocess.CalledProcessError) as exc:
                error = exc
                detail = getattr(exc, "stderr", None) or getattr(exc, "stdout", None)
                if detail:
                    error = RuntimeError(f"{exc}: {str(detail).strip()}")
    print(f"Could not create the installer: {error}", file=sys.stderr)
    return 1


def build_app(template: Path | None = None) -> int:
    # A local template folder is read as is: cookiecutter ignores the ref for it.
    extra = ["--template", str(template)] if template is not None else []
    return flet_build("macos", extra)


def main() -> int:
    bundle = subprocess.run(
        [sys.executable, str(REPO / "tools" / "build_bundle.py")], cwd=REPO, check=False
    )
    if bundle.returncode != 0:
        return bundle.returncode
    clean_output()
    raise_deployment_target()
    template = patched_template()
    code = build_app(template)
    if code != 0 and raise_deployment_target():
        print("Fixed the minimum macOS version of the generated project; retrying.")
        code = build_app(template)
    if code != 0:
        return code
    app = next(OUTPUT.glob("*.app"))
    version = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))["project"][
        "version"
    ]
    image = REPO / "dist" / f"HeimdallGuardian-{version}-{platform.machine()}.dmg"
    image.parent.mkdir(exist_ok=True)
    # The installation disk carries the application and a shortcut to
    # Applications, so it can be installed by dragging one onto the other.
    staged = Path(tempfile.mkdtemp(prefix="heimdall-app-")) / "Heimdall Guardian.app"
    try:
        # `ditto` preserves the signature, permissions and attributes of the bundle.
        copied = subprocess.run(["ditto", str(app), str(staged)], cwd=REPO, check=False).returncode
        if copied != 0:
            return copied
        image.unlink(missing_ok=True)
        code = disk_image(staged, image)
    finally:
        shutil.rmtree(staged.parent, ignore_errors=True)
    if code == 0:
        # Only this version's installer is kept: older ones cause confusion.
        for pattern in ("Heimdall-*", "HeimdallGuardian-*"):
            for old in image.parent.glob(f"{pattern}-{platform.machine()}.dmg"):
                if old != image:
                    old.unlink()
        print(f"Installer: {image.relative_to(REPO)}. It is not signed with Developer ID.")
    return code


if __name__ == "__main__":
    sys.exit(main())
