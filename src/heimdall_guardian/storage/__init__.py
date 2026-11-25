"""Local persistence: per-project baseline in SQLite."""

from __future__ import annotations

from ..core.paths import data_dir
from .store import (
    Store,
    forget_project,
    list_projects,
    load_project_exclusions,
    save_project_exclusions,
)

__all__ = [
    "Store",
    "data_dir",
    "forget_project",
    "list_projects",
    "load_project_exclusions",
    "save_project_exclusions",
]
