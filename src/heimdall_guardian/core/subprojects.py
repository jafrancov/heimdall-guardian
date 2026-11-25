"""Detects separate projects inside one folder (api/, ios/, backend/...)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from .detector import Stack, detect
from .files import is_protected

_IGNORED_STACKS = {Stack.GIT, Stack.DOCKER}


@dataclass(frozen=True)
class SubProject:
    path: str  # relative posix folder
    stacks: tuple[str, ...]  # stack codes, without git and docker


def find_subprojects(root: Path, files: list[str], max_depth: int = 3) -> list[SubProject]:
    """Returns the top-most folders that hold their own manifest, if there are at least two.

    A manifest at the root means one project (for example a monorepo with workspaces), so
    nothing is returned in that case.
    """
    candidates: set[str] = set()
    for file in files:
        if not is_protected(file):
            continue
        parent = PurePosixPath(file).parent
        depth = len(parent.parts) if parent.as_posix() != "." else 0
        if depth == 0:
            return []
        if depth <= max_depth:
            candidates.add(parent.as_posix())
    top = [
        c for c in sorted(candidates) if not any(c.startswith(other + "/") for other in candidates)
    ]
    if len(top) < 2:
        return []
    result = []
    for path in top:
        inner = [f[len(path) + 1 :] for f in files if f.startswith(path + "/")]
        stacks = tuple(
            hit.stack.value
            for hit in detect(root / path, inner)
            if hit.stack not in _IGNORED_STACKS
        )
        result.append(SubProject(path=path, stacks=stacks))
    return result
