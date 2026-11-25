"""Tool installation into the data directory (`hdl tools --install`), without network."""

from __future__ import annotations

import hashlib
import io
import tarfile
from pathlib import Path
from typing import Any

import pytest

from heimdall_guardian import cli, tool_install
from heimdall_guardian.adapters import base
from heimdall_guardian.core.paths import data_dir

TARGET = "linux-x64"


def _manifest(payload: bytes) -> tool_install.Manifest:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
        info = tarfile.TarInfo("gitleaks")
        info.size = len(payload)
        tar.addfile(info, io.BytesIO(payload))
    archive = buffer.getvalue()
    manifest: tool_install.Manifest = {
        "gitleaks": {
            "version": "1.0.0",
            TARGET: {
                "url": "https://example.test/gitleaks.tar.gz",
                "sha256": hashlib.sha256(archive).hexdigest(),
                "member": "gitleaks",
            },
        }
    }
    manifest["_archive"] = {"bytes": archive}  # test helper, not a tool
    return manifest


def _split(manifest: tool_install.Manifest) -> tuple[tool_install.Manifest, bytes]:
    archive = manifest.pop("_archive")["bytes"]
    assert isinstance(archive, bytes)
    return manifest, archive


def test_install_verifies_and_places_binary() -> None:
    manifest, archive = _split(_manifest(b"binary"))
    records = tool_install.install_tools(manifest, TARGET, None, lambda _u: archive)
    folder = tool_install.tools_folder(manifest, TARGET)
    assert (folder / "gitleaks").read_bytes() == b"binary"
    assert (folder / tool_install.COMPLETE_MARKER).is_file()
    assert folder.parent == data_dir() / "tools"
    assert records[0].downloaded
    assert records[0].transferred == len(archive)
    assert tool_install.missing_tools(manifest, TARGET, folder) == []


def test_install_reuses_what_is_already_there() -> None:
    manifest, archive = _split(_manifest(b"binary"))
    tool_install.install_tools(manifest, TARGET, None, lambda _u: archive)

    def forbidden(_url: str) -> bytes:
        raise AssertionError("no download expected")

    again = tool_install.install_tools(manifest, TARGET, None, forbidden)
    assert not again[0].downloaded


def test_install_refuses_a_hash_mismatch() -> None:
    manifest, _ = _split(_manifest(b"binary"))
    with pytest.raises(tool_install.ToolInstallError, match="SHA-256"):
        tool_install.install_tools(manifest, TARGET, None, lambda _u: b"tampered")
    folder = tool_install.tools_folder(manifest, TARGET)
    assert not (folder / "gitleaks").exists()
    assert not (folder / tool_install.COMPLETE_MARKER).exists()


def test_only_https_is_downloaded() -> None:
    with pytest.raises(tool_install.ToolInstallError):
        tool_install._download("http://example.test/x")


def test_find_binary_uses_installed_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    manifest, archive = _split(_manifest(b"binary"))
    tool_install.install_tools(manifest, TARGET, None, lambda _u: archive)
    monkeypatch.setattr(tool_install, "load_manifest", lambda: manifest)
    monkeypatch.setattr(tool_install, "current_platform", lambda: TARGET)
    monkeypatch.setattr(base, "_extracted_tools", lambda: None)
    monkeypatch.setattr(base, "_REPO", Path("/nowhere"))
    monkeypatch.delenv("HDL_GITLEAKS_BIN", raising=False)
    monkeypatch.setattr("sys.platform", "linux")
    found = base.find_binary("gitleaks")
    assert found == str(tool_install.tools_folder(manifest, TARGET) / "gitleaks")


def test_packaged_manifest_fingerprint_matches_the_bundle_script() -> None:
    manifest = tool_install.load_manifest()
    assert manifest is not None
    assert len(tool_install.tools_key(manifest, "darwin-arm64")) == 16


def test_cli_install_reports_downloads(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    manifest, archive = _split(_manifest(b"binary"))
    monkeypatch.setattr(tool_install, "load_manifest", lambda: manifest)
    monkeypatch.setattr(tool_install, "current_platform", lambda: TARGET)
    monkeypatch.setattr(tool_install, "_download", lambda _u: archive)
    original: Any = tool_install.install_tools
    monkeypatch.setattr(
        tool_install,
        "install_tools",
        lambda m, t, cb: original(m, t, cb, lambda _u: archive),
    )
    assert cli.main(["--lang", "en", "tools", "--install"]) == 0
    out = capsys.readouterr().out
    assert "gitleaks 1.0.0: downloaded" in out
    assert "1 downloaded" in out


def test_cli_install_fails_cleanly_on_mismatch(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    manifest, _ = _split(_manifest(b"binary"))
    monkeypatch.setattr(tool_install, "load_manifest", lambda: manifest)
    monkeypatch.setattr(tool_install, "current_platform", lambda: TARGET)
    original: Any = tool_install.install_tools
    monkeypatch.setattr(
        tool_install,
        "install_tools",
        lambda m, t, cb: original(m, t, cb, lambda _u: b"tampered"),
    )
    assert cli.main(["--lang", "en", "tools", "--install"]) == 1
    assert "SHA-256" in capsys.readouterr().err


def test_ui_without_flet_explains_and_fails(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("importlib.util.find_spec", lambda _name: None)
    assert cli.main(["--lang", "en", "ui"]) == 1
    assert "heimdall-guardian[ui]" in capsys.readouterr().err


def test_tools_suggests_install_when_missing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    manifest, _ = _split(_manifest(b"binary"))
    monkeypatch.setattr(tool_install, "load_manifest", lambda: manifest)
    monkeypatch.setattr(tool_install, "current_platform", lambda: TARGET)
    monkeypatch.setattr(cli, "find_binary", lambda _name: None)
    assert cli.main(["--lang", "en", "tools"]) == 0
    out = capsys.readouterr().out
    assert "Missing tools: gitleaks" in out
    assert "hdl tools --install" in out


def _zip_manifest(members: dict[str, bytes], extra: list[str] | None = None) -> Any:
    import zipfile

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as bundle:
        for member, content in members.items():
            bundle.writestr(member, content)
    archive = buffer.getvalue()
    asset: dict[str, Any] = {
        "url": "https://example.test/opengrep.zip",
        "sha256": hashlib.sha256(archive).hexdigest(),
        "member": "opengrep.exe",
    }
    if extra is not None:
        asset["extra"] = extra
    manifest: tool_install.Manifest = {
        "opengrep": {"version": "2.0.0", "windows-x64": asset},
    }
    return manifest, archive


def test_extra_files_land_next_to_the_binary() -> None:
    members = {"opengrep.exe": b"exe", "libgmp.dll": b"gmp", "libzstd.dll": b"zstd", "README": b"x"}
    manifest, archive = _zip_manifest(members, ["*.dll"])
    tool_install.install_tools(manifest, "windows-x64", None, lambda _u: archive)
    folder = tool_install.tools_folder(manifest, "windows-x64")
    assert (folder / "opengrep.exe").read_bytes() == b"exe"
    assert (folder / "libgmp.dll").read_bytes() == b"gmp"
    assert (folder / "libzstd.dll").read_bytes() == b"zstd"
    assert not (folder / "README").exists()


def test_without_extra_only_the_binary_is_written() -> None:
    manifest, archive = _zip_manifest({"opengrep.exe": b"exe", "libgmp.dll": b"gmp"})
    tool_install.install_tools(manifest, "windows-x64", None, lambda _u: archive)
    folder = tool_install.tools_folder(manifest, "windows-x64")
    assert not (folder / "libgmp.dll").exists()


def test_extra_patterns_change_the_fingerprint() -> None:
    with_extra, _ = _zip_manifest({"opengrep.exe": b"exe"}, ["*.dll"])
    without, _ = _zip_manifest({"opengrep.exe": b"exe"})
    assert tool_install.tools_key(with_extra, "windows-x64") != tool_install.tools_key(
        without, "windows-x64"
    )


@pytest.mark.parametrize("name", ["../evil.dll", "/abs/evil.dll", "sub/../../evil.dll", "C:/x.dll"])
def test_extra_with_traversal_is_refused(name: str) -> None:
    manifest, archive = _zip_manifest({"opengrep.exe": b"exe", name: b"bad"}, ["*.dll"])
    with pytest.raises(tool_install.ToolInstallError):
        tool_install.install_tools(manifest, "windows-x64", None, lambda _u: archive)
    folder = tool_install.tools_folder(manifest, "windows-x64")
    assert not (folder / "opengrep.exe").exists()
    assert not (folder / tool_install.COMPLETE_MARKER).exists()
    assert not (folder.parent / "evil.dll").exists()


def test_write_extras_refuses_names_with_separators(tmp_path: Path) -> None:
    with pytest.raises(tool_install.ToolInstallError):
        tool_install.write_extras({"../x.dll": b"x"}, tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_extra_hash_mismatch_writes_nothing() -> None:
    manifest, archive = _zip_manifest({"opengrep.exe": b"exe", "libgmp.dll": b"gmp"}, ["*.dll"])
    with pytest.raises(tool_install.ToolInstallError, match="SHA-256"):
        tool_install.install_tools(manifest, "windows-x64", None, lambda _u: archive + b"x")
    folder = tool_install.tools_folder(manifest, "windows-x64")
    assert not any(folder.iterdir())
