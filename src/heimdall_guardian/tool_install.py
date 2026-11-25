"""Installs the pinned analysis tools into the data directory (the CLI without the app).

The pin list (`tools.toml`: version, URL and SHA-256 per platform) ships inside the package as
`_bundle/tools.toml`. Each binary is downloaded over HTTPS, its SHA-256 is checked before
anything touches the disk, and it lands in `<data>/tools/<fingerprint>/`: the same folder the
desktop app extracts its bundled binaries to, so whichever installed first, the other reuses.
`tools/fetch_tools.py` (development) shares the download and verification code below.
"""

from __future__ import annotations

import fnmatch
import hashlib
import io
import platform
import sys
import tarfile
import tomllib
import urllib.request
import zipfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from .core.paths import data_dir
from .i18n import t

COMPLETE_MARKER = ".completo"
_MACHINES = {"arm64": "arm64", "aarch64": "arm64", "x86_64": "x64", "amd64": "x64"}
_PACKAGE = Path(__file__).resolve().parent
_REPO = _PACKAGE.parents[1]
_DOWNLOAD_TIMEOUT_SECONDS = 120

Manifest = dict[str, dict[str, Any]]


class ToolInstallError(ValueError):
    """A pinned tool could not be installed; the text is already in the current language."""


@dataclass(frozen=True)
class InstallRecord:
    """What happened to one tool: downloaded (with sizes) or already there."""

    name: str
    version: str
    downloaded: bool
    size: int = 0  # bytes of the installed binary
    transferred: int = 0  # bytes downloaded


def current_platform() -> str:
    system = {"darwin": "darwin", "win32": "windows"}.get(sys.platform, sys.platform)
    if system.startswith("linux"):
        system = "linux"
    machine = platform.machine().lower()
    return f"{system}-{_MACHINES.get(machine, machine)}"


def binary_name(name: str, target_platform: str) -> str:
    """File name of a tool's executable on the platform (`.exe` on Windows)."""
    return f"{name}.exe" if target_platform.startswith("windows-") else name


def manifest_path() -> Path | None:
    """The packaged pin list, or the repository's own when running from a checkout."""
    for candidate in (_PACKAGE / "_bundle" / "tools.toml", _REPO / "tools" / "tools.toml"):
        if candidate.is_file():
            return candidate
    return None


def load_manifest() -> Manifest | None:
    path = manifest_path()
    if path is None:
        return None
    manifest: Manifest = tomllib.loads(path.read_text(encoding="utf-8"))
    return manifest


def pinned_tools(manifest: Manifest, target_platform: str) -> dict[str, dict[str, Any]]:
    """The tools that have a pinned binary for the platform."""
    return {
        name: spec for name, spec in manifest.items() if isinstance(spec.get(target_platform), dict)
    }


def tools_key(manifest: Manifest, target_platform: str) -> str:
    """Fingerprint of the pinned binaries; `tools/build_bundle.py` writes the same value."""
    digest = hashlib.sha256()
    for name, spec in pinned_tools(manifest, target_platform).items():
        asset = spec[target_platform]
        digest.update(f"{name}:{asset['sha256']}\n".encode())
        # Extra files change what an extraction holds even with the same archive hash.
        # Only written when present, so platforms without extras keep their old key.
        if asset.get("extra"):
            digest.update(f"{name}:extra:{','.join(map(str, asset['extra']))}\n".encode())
    return digest.hexdigest()[:16]


def tools_folder(manifest: Manifest, target_platform: str) -> Path:
    return data_dir() / "tools" / tools_key(manifest, target_platform)


def installed_tools_dir() -> Path | None:
    """The complete tools folder for the pinned versions, if one is already in the data dir."""
    manifest = load_manifest()
    if manifest is None:
        return None
    target = current_platform()
    if not pinned_tools(manifest, target):
        return None
    folder = tools_folder(manifest, target)
    return folder if (folder / COMPLETE_MARKER).is_file() else None


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _download(url: str) -> bytes:
    if not url.startswith("https://"):
        raise ToolInstallError(t("tools.install.only_https", url=url))
    with urllib.request.urlopen(url, timeout=_DOWNLOAD_TIMEOUT_SECONDS) as response:  # noqa: S310
        data: bytes = response.read()
    return data


def _extract(archive: bytes, member: str, url: str) -> bytes:
    """Reads a single file from a .zip or .tar.gz in memory; never extracts to disk."""
    if url.lower().endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
            if member not in bundle.namelist():
                raise ToolInstallError(t("tools.install.no_member", member=member))
            return bundle.read(member)
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
        handle = tar.extractfile(member)
        if handle is None:
            raise ToolInstallError(t("tools.install.no_member", member=member))
        return handle.read()


def _safe_basename(member: str) -> str:
    """The file name of an archive member, refusing absolute names and `..` segments."""
    parts = PurePosixPath(member.replace("\\", "/")).parts
    if (
        not parts
        or PurePosixPath(member).is_absolute()
        or PureWindowsPath(member).is_absolute()
        or PureWindowsPath(member).drive
        or ".." in parts
    ):
        raise ToolInstallError(t("tools.install.unsafe_member", member=member))
    return parts[-1]


def _extract_extras(archive: bytes, patterns: list[str], url: str, main: str) -> dict[str, bytes]:
    """Reads the files whose base name matches a pattern (e.g. `*.dll`), in memory.

    The result maps a plain file name to its content: the caller writes them next to the
    binary, so nothing can land outside that folder.
    """
    extras: dict[str, bytes] = {}
    if url.lower().endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
            for info in bundle.infolist():
                if info.is_dir() or info.filename == main:
                    continue
                base = PurePosixPath(info.filename.replace("\\", "/")).name
                if any(fnmatch.fnmatchcase(base, pattern) for pattern in patterns):
                    extras[_safe_basename(info.filename)] = bundle.read(info)
        return extras
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
        for entry in tar.getmembers():
            if not entry.isfile() or entry.name == main:
                continue
            base = PurePosixPath(entry.name.replace("\\", "/")).name
            if any(fnmatch.fnmatchcase(base, pattern) for pattern in patterns):
                handle = tar.extractfile(entry)
                if handle is not None:
                    extras[_safe_basename(entry.name)] = handle.read()
    return extras


def fetch_asset(
    name: str,
    version: str,
    asset: dict[str, Any],
    downloader: Callable[[str], bytes] = _download,
) -> tuple[bytes, dict[str, bytes], int]:
    """Downloads one pinned asset: `(binary, extra files by name, bytes downloaded)`.

    The SHA-256 of the download must equal the pinned one; otherwise nothing is returned.
    `extra` (glob patterns on base names) names more files of the archive that must sit next
    to the binary, such as the DLLs of a Windows build.
    """
    url = str(asset["url"])
    data = downloader(url)
    expected = str(asset["sha256"])
    actual = _sha256(data)
    if actual != expected:
        raise ToolInstallError(
            t(
                "tools.install.hash_mismatch",
                name=name,
                version=version,
                expected=expected,
                actual=actual,
            )
        )
    transferred = len(data)
    extras: dict[str, bytes] = {}
    if "member" in asset:
        member = str(asset["member"])
        patterns = [str(pattern) for pattern in asset.get("extra", [])]
        if patterns:
            extras = _extract_extras(data, patterns, url, member)
        data = _extract(data, member, url)
    return data, extras, transferred


def fetch_binary(
    name: str,
    version: str,
    asset: dict[str, Any],
    downloader: Callable[[str], bytes] = _download,
) -> tuple[bytes, int]:
    """Like `fetch_asset` without the extra files: `(binary, bytes downloaded)`."""
    data, _extras, transferred = fetch_asset(name, version, asset, downloader)
    return data, transferred


def write_extras(extras: dict[str, bytes], folder: Path) -> None:
    """Writes extra files directly inside `folder`; a name with a separator is refused."""
    for file_name, content in extras.items():
        if _safe_basename(file_name) != file_name or "/" in file_name or "\\" in file_name:
            raise ToolInstallError(t("tools.install.unsafe_member", member=file_name))
        target = folder / file_name
        temporary = target.with_name(target.name + ".tmp")
        temporary.write_bytes(content)
        temporary.replace(target)


def missing_tools(manifest: Manifest, target_platform: str, folder: Path) -> list[str]:
    """Pinned tools whose binary is not in the folder."""
    return [
        name
        for name in pinned_tools(manifest, target_platform)
        if not (folder / binary_name(name, target_platform)).is_file()
    ]


def install_tools(
    manifest: Manifest,
    target_platform: str,
    on_record: Callable[[InstallRecord], None] | None = None,
    downloader: Callable[[str], bytes] = _download,
) -> list[InstallRecord]:
    """Installs every pinned tool missing from `<data>/tools/<fingerprint>/`.

    A binary that is already there is kept; the folder is marked complete at the end, which is
    what the desktop app checks before reusing it.
    """
    folder = tools_folder(manifest, target_platform)
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    records: list[InstallRecord] = []
    for name, spec in pinned_tools(manifest, target_platform).items():
        version = str(spec["version"])
        destination = folder / binary_name(name, target_platform)
        if destination.is_file():
            record = InstallRecord(name, version, downloaded=False, size=destination.stat().st_size)
        else:
            data, extras, transferred = fetch_asset(
                name, version, spec[target_platform], downloader
            )
            write_extras(extras, folder)
            temporary = destination.with_name(destination.name + ".tmp")
            temporary.write_bytes(data)
            temporary.chmod(0o755)
            temporary.replace(destination)
            record = InstallRecord(name, version, True, len(data), transferred)
        records.append(record)
        if on_record is not None:
            on_record(record)
    (folder / COMPLETE_MARKER).write_text("ok", encoding="utf-8")
    return records
