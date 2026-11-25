"""Tool download, bundling and lookup across platforms (macOS, Linux, Windows)."""

from __future__ import annotations

import importlib.util
import io
import re
import sys
import tarfile
import tomllib
import zipfile
from pathlib import Path
from types import ModuleType

import pytest

from heimdall_guardian import tool_install
from heimdall_guardian.adapters import base

ROOT = Path(__file__).resolve().parents[2]


def _load_fetch_tools() -> ModuleType:
    spec = importlib.util.spec_from_file_location("fetch_tools", ROOT / "tools" / "fetch_tools.py")
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("fetch_tools", module)
    spec.loader.exec_module(module)
    return module


fetch_tools = _load_fetch_tools()


@pytest.mark.parametrize(
    ("platform_name", "machine", "expected"),
    [
        ("win32", "AMD64", "windows-x64"),
        ("linux", "x86_64", "linux-x64"),
        ("linux", "aarch64", "linux-arm64"),
        ("darwin", "arm64", "darwin-arm64"),
        ("darwin", "x86_64", "darwin-x64"),
    ],
)
def test_current_platform(
    monkeypatch: pytest.MonkeyPatch, platform_name: str, machine: str, expected: str
) -> None:
    monkeypatch.setattr(sys, "platform", platform_name)
    monkeypatch.setattr(tool_install.platform, "machine", lambda: machine)
    assert fetch_tools.current_platform() == expected


def test_binary_name() -> None:
    assert fetch_tools.binary_name("trivy", "windows-x64") == "trivy.exe"
    assert fetch_tools.binary_name("trivy", "linux-x64") == "trivy"
    assert fetch_tools.binary_name("trivy", "darwin-arm64") == "trivy"


def test_extract_zip_single_member() -> None:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as bundle:
        bundle.writestr("trivy.exe", b"MZ-binary")
        bundle.writestr("LICENSE", b"text")
    data = tool_install._extract(buffer.getvalue(), "trivy.exe", "https://x/trivy.zip")
    assert data == b"MZ-binary"


def test_extract_zip_rejects_missing_or_inexact_member() -> None:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as bundle:
        bundle.writestr("sub/trivy.exe", b"x")
    with pytest.raises(ValueError, match=r"trivy\.exe"):
        tool_install._extract(buffer.getvalue(), "trivy.exe", "https://x/trivy.zip")


def test_extract_tar_gz() -> None:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
        info = tarfile.TarInfo("gitleaks")
        payload = b"ELF"
        info.size = len(payload)
        tar.addfile(info, io.BytesIO(payload))
    data = tool_install._extract(buffer.getvalue(), "gitleaks", "https://x/g.tar.gz")
    assert data == b"ELF"
    with pytest.raises(KeyError):
        tool_install._extract(buffer.getvalue(), "other", "https://x/g.tar.gz")


def test_find_binary_prefers_exe_on_windows(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake_repo = tmp_path / "repo"
    (fake_repo / "tools" / "bin").mkdir(parents=True)
    (fake_repo / "tools" / "bin" / "gitleaks.exe").write_bytes(b"x")
    (fake_repo / "tools" / "bin" / "gitleaks").write_bytes(b"x")
    monkeypatch.setattr(base, "_REPO", fake_repo)
    monkeypatch.setattr(base, "_extracted_tools", lambda: None)
    monkeypatch.delenv("HDL_GITLEAKS_BIN", raising=False)

    monkeypatch.setattr(sys, "platform", "win32")
    assert base.find_binary("gitleaks") == str(fake_repo / "tools" / "bin" / "gitleaks.exe")
    monkeypatch.setattr(sys, "platform", "linux")
    assert base.find_binary("gitleaks") == str(fake_repo / "tools" / "bin" / "gitleaks")


def test_find_binary_in_extracted_bundle_on_windows(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    extracted = tmp_path / "extracted"
    extracted.mkdir()
    (extracted / "trivy.exe").write_bytes(b"x")
    monkeypatch.setattr(base, "_REPO", tmp_path / "nowhere")
    monkeypatch.setattr(base, "_extracted_tools", lambda: extracted)
    monkeypatch.delenv("HDL_TRIVY_BIN", raising=False)
    monkeypatch.setattr(sys, "platform", "win32")
    assert base.find_binary("trivy") == str(extracted / "trivy.exe")


def test_find_binary_env_override(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    custom = tmp_path / "mine"
    custom.write_bytes(b"x")
    monkeypatch.setenv("HDL_OSV_SCANNER_BIN", str(custom))
    assert base.find_binary("osv-scanner") == str(custom)


def test_manifest_has_every_platform() -> None:
    manifest = tomllib.loads((ROOT / "tools" / "tools.toml").read_text(encoding="utf-8"))
    for name, spec in manifest.items():
        for target in ("windows-x64", "linux-x64", "darwin-arm64"):
            asset = spec.get(target)
            assert isinstance(asset, dict), f"{name} has no {target}"
            assert asset["url"].startswith("https://"), (name, target)
            assert re.fullmatch(r"[0-9a-f]{64}", asset["sha256"]), (name, target)
            if asset["url"].endswith((".zip", ".tar.gz")):
                assert "member" in asset, (name, target)
        if "member" in spec["windows-x64"]:
            assert spec["windows-x64"]["member"] == f"{name}.exe"


def _load_build_windows() -> ModuleType:
    # It imports its sibling `flet_build`, as it does when run as a script.
    if str(ROOT / "tools") not in sys.path:
        sys.path.insert(0, str(ROOT / "tools"))
    path = ROOT / "tools" / "build_windows.py"
    spec = importlib.util.spec_from_file_location("build_windows", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_iscc_candidates_cover_inno_7_and_6_including_per_user(tmp_path: Path) -> None:
    build_windows = _load_build_windows()
    env = {
        "ProgramFiles(x86)": str(tmp_path / "pf86"),
        "ProgramFiles": str(tmp_path / "pf"),
        "LOCALAPPDATA": str(tmp_path / "local"),
    }
    candidates = build_windows.iscc_candidates(env)
    assert candidates[0] == tmp_path / "pf86" / "Inno Setup 7" / "ISCC.exe"
    assert tmp_path / "local" / "Programs" / "Inno Setup 7" / "ISCC.exe" in candidates
    assert tmp_path / "local" / "Programs" / "Inno Setup 6" / "ISCC.exe" in candidates
    assert len(candidates) == 6
    assert build_windows.iscc_candidates({}) == []


def test_find_iscc_finds_a_per_user_inno_setup_7(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    build_windows = _load_build_windows()
    monkeypatch.setattr(build_windows.shutil, "which", lambda _name: None)
    iscc = tmp_path / "Programs" / "Inno Setup 7" / "ISCC.exe"
    iscc.parent.mkdir(parents=True)
    iscc.write_bytes(b"")
    assert build_windows.find_iscc({"LOCALAPPDATA": str(tmp_path)}) == str(iscc)
    assert build_windows.find_iscc({}) is None


def test_flet_build_skips_doctor_and_points_at_the_first_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _load_build_windows()
    import flet_build

    assert flet_build.command("windows") == [
        "flet",
        "build",
        "windows",
        "--skip-flutter-doctor",
    ]
    assert flet_build.command("macos", ["--template", "t"])[-2:] == ["--template", "t"]

    class Done:
        returncode = 1

    monkeypatch.setattr(flet_build.subprocess, "run", lambda *a, **k: Done())
    monkeypatch.setattr(flet_build, "required_flutter", lambda: "3.47.9")
    monkeypatch.setattr(flet_build, "download_notice", lambda _flutter: None)
    monkeypatch.setattr(flet_build, "reset_stale_stamps", lambda: False)
    assert flet_build.flet_build("linux") == 1
    hint = capsys.readouterr().err
    assert "FIRST red lines" in hint
    assert "~/flutter/3.47.9/bin/flutter pub cache repair" in hint
    assert "Flutter version Flet pins" in flet_build.failure_hint(None)


def test_flutter_download_notice_only_when_flet_would_download(tmp_path: Path) -> None:
    _load_build_windows()
    import flet_build

    def notice(found: str | None, version: str | None) -> str | None:
        return flet_build.download_notice(
            "3.47.9",
            home=tmp_path,
            which=lambda _name: found,
            version_of=lambda _exe: version,
            windows=False,
        )

    assert notice("/sdk/bin/flutter", "3.47.2") is None  # same major.minor: no download
    newer = notice("/sdk/bin/flutter", "3.50.1")
    assert newer is not None
    assert "is 3.50.1" in newer
    assert "does NOT upgrade, downgrade or replace your Flutter" in newer
    assert str(tmp_path / "flutter" / "3.47.9") in newer
    assert "No usable `flutter`" in (notice(None, None) or "")
    own = tmp_path / "flutter" / "3.47.9" / "bin" / "flutter"
    own.parent.mkdir(parents=True)
    own.write_bytes(b"")
    assert notice("/sdk/bin/flutter", "3.50.1") is None  # Flet's own copy is already there


def test_stale_flet_stamps_are_dropped_when_the_flutter_project_is_gone(tmp_path: Path) -> None:
    _load_build_windows()
    import flet_build

    (tmp_path / ".hash").mkdir()
    (tmp_path / ".hash" / "template-1").write_text("x")
    assert flet_build.reset_stale_stamps(tmp_path) is True
    assert not (tmp_path / ".hash").exists()
    assert flet_build.reset_stale_stamps(tmp_path) is False  # nothing to drop
    (tmp_path / ".hash").mkdir()
    (tmp_path / "flutter").mkdir()
    (tmp_path / "flutter" / "pubspec.yaml").write_text("name: app")
    assert flet_build.reset_stale_stamps(tmp_path) is False  # project present: keep them
    assert (tmp_path / ".hash").is_dir()


def test_flet_build_output_never_fails_on_a_character() -> None:
    _load_build_windows()
    import flet_build

    env = flet_build.build_env({"PATH": "/bin", "PYTHONIOENCODING": "cp1252"})
    assert env["PYTHONIOENCODING"] == ":replace"  # system encoding, unknown chars -> "?"
    assert "PYTHONUTF8" not in env
    assert env["PATH"] == "/bin"
