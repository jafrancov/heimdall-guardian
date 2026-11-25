"""What kind of machine the command runs on, to decide whether to suggest the app.

Pure functions: the environment, platform and home folder are injected.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Mapping
from importlib import metadata
from pathlib import Path

from .paths import data_dir

HINT_MARKER = "cli_hint_shown"
FALLBACK_URL = "https://jafrancov.github.io/heimdall-guardian/"
_CI_VARS = (
    "CI",
    "GITHUB_ACTIONS",
    "GITLAB_CI",
    "BUILDKITE",
    "JENKINS_URL",
    "TF_BUILD",
    "CIRCLECI",
    "TRAVIS",
)
_APP_NAME = "Heimdall Guardian"


def _remote(env: Mapping[str, str]) -> bool:
    return bool(env.get("SSH_CONNECTION") or env.get("SSH_TTY") or env.get("SSH_CLIENT"))


def graphical_session(env: Mapping[str, str], platform: str) -> bool:
    """True when the user is probably in front of a desktop (not over SSH)."""
    if _remote(env):
        return False
    if platform in ("darwin", "win32"):
        return True
    return bool(env.get("DISPLAY") or env.get("WAYLAND_DISPLAY"))


def in_ci(env: Mapping[str, str]) -> bool:
    return any(env.get(name) for name in _CI_VARS)


def app_installed(
    platform: str,
    home: Path,
    env: Mapping[str, str] | None = None,
    system_root: Path = Path("/"),
) -> bool:
    """Whether the desktop app is installed in one of the usual places."""
    env = os.environ if env is None else env
    candidates: list[Path] = []
    if platform == "darwin":
        candidates = [
            system_root / "Applications" / f"{_APP_NAME}.app",
            home / "Applications" / f"{_APP_NAME}.app",
        ]
    elif platform == "win32":
        program_files = env.get("ProgramFiles")
        local = env.get("LOCALAPPDATA")
        if program_files:
            candidates.append(Path(program_files) / _APP_NAME)
        candidates.append(
            (Path(local) if local else home / "AppData" / "Local") / "Programs" / _APP_NAME
        )
    else:
        candidates = [
            system_root / "usr" / "bin" / "heimdall-guardian",
            system_root / "usr" / "share" / "applications" / "heimdall-guardian.desktop",
            home / ".local" / "share" / "applications" / "heimdall-guardian.desktop",
        ]
    return any(path.exists() for path in candidates)


def homepage_url() -> str:
    """Project homepage from the package metadata; a constant if it is not installed."""
    try:
        for entry in metadata.metadata("heimdall-guardian").get_all("Project-URL") or []:
            label, _, url = entry.partition(",")
            if label.strip().lower() == "homepage" and url.strip():
                return str(url.strip())
    except metadata.PackageNotFoundError:
        pass
    return FALLBACK_URL


def should_hint(
    *,
    tty: bool,
    env: Mapping[str, str],
    platform: str,
    home: Path,
    marker: Path,
    system_root: Path = Path("/"),
) -> bool:
    """All the conditions to print the app tip once."""
    if not tty or env.get("HDL_NO_HINTS") or in_ci(env):
        return False
    if not graphical_session(env, platform) or app_installed(platform, home, env, system_root):
        return False
    return not marker.exists()


def maybe_app_hint(*, tty: bool) -> str | None:
    """The tip text to print now (and records that it was shown), or `None`."""
    from ..i18n import t

    marker = data_dir() / HINT_MARKER
    if not should_hint(
        tty=tty, env=os.environ, platform=sys.platform, home=Path.home(), marker=marker
    ):
        return None
    try:
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text("1\n", encoding="utf-8")
    except OSError:
        pass  # not being able to remember it only means it may show again
    return t("cli.hint.app", url=homepage_url())
