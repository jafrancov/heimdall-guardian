"""Application data locations: always outside the analyzed folder (P1)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

APP_DIR = "Heimdall"


def data_dir() -> Path:
    """Application data directory; `HDL_DATA_DIR` overrides it."""
    override = os.environ.get("HDL_DATA_DIR")
    if override:
        return Path(override)
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_DIR
    if sys.platform == "win32":
        return Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / APP_DIR
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / APP_DIR


def config_path() -> Path:
    """Configuration file; `HDL_CONFIG` overrides it."""
    override = os.environ.get("HDL_CONFIG")
    return Path(override) if override else data_dir() / "config.toml"


def archive_file(path: Path, version: int) -> Path | None:
    """Sets aside a file of an earlier format as `<name>.v<N>.bak`; it never deletes.

    Returns the new path, or `None` if the file does not exist.
    """
    if not path.is_file():
        return None
    target = path.with_name(f"{path.name}.v{version}.bak")
    counter = 1
    while target.exists():
        counter += 1
        target = path.with_name(f"{path.name}.v{version}.{counter}.bak")
    path.rename(target)
    return target


def bases_dir() -> Path:
    """Local vulnerability databases: next to the data, so they can be carried
    in a single file to a machine without internet (P4). `HDL_BASES_DIR` overrides it, so an
    isolated data directory can still reuse the databases downloaded elsewhere."""
    override = os.environ.get("HDL_BASES_DIR")
    if override:
        return Path(override)
    return data_dir() / "bases"


def data_location_lines() -> list[str]:
    """Where data lives, in the current language: shared by the CLI and the app."""
    from ..i18n import t

    def source(variable: str) -> str:
        return t("core.paths.from_env", variable=variable) if os.environ.get(variable) else ""

    return [
        t("core.paths.data", path=data_dir(), source=source("HDL_DATA_DIR")),
        t("core.paths.bases", path=bases_dir(), source=source("HDL_BASES_DIR")),
    ]
