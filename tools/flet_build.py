"""Runs `flet build <platform>` for the platform build scripts, with a short hint on failure.

`flet build` runs `flutter doctor` after any failed build and prints its summary last. That
summary warns about the `flutter` on the PATH even when the build used the right SDK, so it
reads like the cause when the real error is a few hundred lines above. The doctor run is
skipped here and replaced with a hint that points at the real error.

Before building, it also checks whether a Flutter that Flet accepts is already there. If not,
Flet is about to offer downloading its own copy, and people who use Flutter for other work
need to know what that touches (and what it does not) before they answer.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUILD = REPO / "build"


def required_flutter() -> str | None:
    """The Flutter version the installed Flet builds with, or None if Flet is not importable."""
    try:
        from flet.version import flutter_version
    except ImportError:
        return None
    return str(flutter_version)


def flet_flutter_dir(flutter: str, home: Path | None = None) -> Path:
    """Where Flet keeps (or downloads) its own copy of that Flutter version."""
    return (home or Path.home()) / "flutter" / flutter


def _version_of(executable: str) -> str | None:
    try:
        done = subprocess.run(
            [executable, "--version", "--no-version-check", "--suppress-analytics"],
            capture_output=True,
            text=True,
            errors="replace",
            timeout=180,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    match = re.search(r"Flutter (\d+\.\d+\.\d+)", done.stdout or "")
    return match.group(1) if match else None


def _same_minor(a: str, b: str) -> bool:
    return a.split(".")[:2] == b.split(".")[:2]


def download_notice(
    flutter: str,
    *,
    home: Path | None = None,
    which: Callable[[str], str | None] = shutil.which,
    version_of: Callable[[str], str | None] = _version_of,
    windows: bool = os.name == "nt",
) -> str | None:
    """A notice when Flet will offer to download Flutter; None when a usable one is there."""
    ext = ".bat" if windows else ""
    folder = flet_flutter_dir(flutter, home)
    if (folder / "bin" / f"flutter{ext}").exists():
        return None
    found = which("flutter")
    current = version_of(found) if found else None
    if current is not None and _same_minor(current, flutter):
        return None
    yours = (
        f"Your `flutter` ({found}) is {current}, which Flet does not accept."
        if found and current
        else "No usable `flutter` was found on the PATH."
    )
    cache = r"%LOCALAPPDATA%\Pub\Cache" if windows else "~/.pub-cache"
    return "\n".join(
        [
            "",
            f"Flutter notice: this Flet release builds with Flutter {flutter} (same major and",
            "minor version required).",
            yours,
            f"Flet will now ask to download Flutter {flutter} into {folder}",
            "(about 1-2 GB, once). If you also use Flutter for other work:",
            "  - It does NOT upgrade, downgrade or replace your Flutter, and it does not",
            "    change your PATH: your other projects keep using the Flutter they use now.",
            f"  - It shares with your Flutter the package cache ({cache}) and the",
            "    user-wide Flutter settings, where Flet only turns on desktop support for",
            "    this system.",
            "  - To use a Flutter you manage yourself instead, answer n and put a",
            f"    Flutter {'.'.join(flutter.split('.')[:2])}.x on the PATH or in {folder}.",
            "",
        ]
    )


def reset_stale_stamps(build: Path = BUILD) -> bool:
    """Forgets Flet's build stamps when the generated Flutter project is gone.

    Flet regenerates `build/flutter` only when its stamps in `build/.hash` change. If the
    project folder was deleted by hand and the stamps stayed, it skips the generation and
    then runs Flutter in a folder that does not exist (on Windows, WinError 267).
    """
    stamps = build / ".hash"
    if stamps.is_dir() and not (build / "flutter" / "pubspec.yaml").is_file():
        shutil.rmtree(stamps)
        return True
    return False


def build_env(base: dict[str, str] | None = None) -> dict[str, str]:
    """The environment for `flet build`: output that never crashes on a character.

    On Windows, with the output piped (`| Tee-Object`), Python writes in the ANSI code page
    (cp1252) and Flet's spinner characters crashed it with UnicodeEncodeError. Forcing UTF-8
    instead garbles the text in Windows PowerShell, which reads pipes in the console code
    page. So the encoding stays the system's and what it cannot draw becomes `?`. On a real
    console Python writes Unicode directly and nothing changes.
    """
    env = dict(os.environ if base is None else base)
    env["PYTHONIOENCODING"] = ":replace"
    return env


def command(platform: str, extra: Sequence[str] = ()) -> list[str]:
    return ["flet", "build", platform, "--skip-flutter-doctor", *extra]


def failure_hint(flutter: str | None) -> str:
    sdk = f"Flutter {flutter}" if flutter else "the Flutter version Flet pins"
    asked = f"Flutter SDK {flutter}" if flutter else "Flutter SDK <version>"
    folder = f"~/flutter/{flutter}" if flutter else "~/flutter/<version>"
    return "\n".join(
        [
            "",
            "flet build failed. How to read the log above:",
            "  - The cause is in the FIRST red lines, not the last ones: when one package",
            "    fails to compile, every package that uses it repeats the error.",
            f"  - Flet builds with {sdk}, from {folder} or from the `flutter` on the PATH",
            "    when it has the same major and minor version. A newer Flutter on the PATH",
            "    is not the problem.",
            f"  - It stopped at '{asked} is required ... Proceed?': answer y (it downloads that",
            f"    version into {folder} once, apart from your own Flutter). Without a terminal",
            "    to answer, the prompt fails with EOFError.",
            "  - A Dart package that does not compile ('... isn't a type'): run",
            f"    `{folder}/bin/flutter pub cache repair`, delete the whole build folder (not",
            "    only build/flutter) and build again.",
            "  - 'Building with plugins requires symlink support' (Windows): turn on Developer",
            "    Mode (`start ms-settings:developers`) and build again.",
            "  - Toolchain problems (Visual Studio, Xcode, GTK...): run `flutter doctor -v`.",
        ]
    )


def flet_build(platform: str, extra: Sequence[str] = ()) -> int:
    """Runs `flet build` from the repository root; prints the hint when it fails."""
    if reset_stale_stamps():
        print("build/flutter is missing: Flet will generate the Flutter project again.", flush=True)
    flutter = required_flutter()
    notice = download_notice(flutter) if flutter else None
    if notice:
        # Flushed now: with the output piped it would otherwise appear after Flet's prompt.
        print(notice, flush=True)
    code = subprocess.run(
        command(platform, extra), cwd=REPO, env=build_env(), check=False
    ).returncode
    if code != 0:
        print(failure_hint(flutter), file=sys.stderr, flush=True)
    return code
