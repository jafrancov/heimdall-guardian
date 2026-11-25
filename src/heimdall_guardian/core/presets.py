"""Folders worth suggesting to skip, from the detected stacks and known tool folders.

Suggestions are never applied on their own: the user confirms them.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..adapters.base import git_ignored
from ..i18n import Message, msg
from .detector import Stack, StackHit
from .files import Exclusions, list_folders

_NODE = (
    ".next",
    ".nuxt",
    ".svelte-kit",
    ".turbo",
    ".parcel-cache",
    ".cache",
    "coverage",
    "storybook-static",
)
_PYTHON = ("__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".tox", "htmlcov")
_JVM = (".gradle", ".kotlin", "target")
_PHP = ("bootstrap/cache", "storage/framework")

# Folder names typical of build output, caches and vendored dependencies, per stack.
STACK_DIRS: dict[Stack, tuple[str, ...]] = {
    Stack.NODE: _NODE,
    Stack.TYPESCRIPT: _NODE,
    Stack.PYTHON: _PYTHON,
    Stack.DJANGO: _PYTHON,
    Stack.SWIFT: ("Pods", "DerivedData", ".build", "Carthage", ".swiftpm"),
    Stack.DART: (".dart_tool",),
    Stack.FLUTTER: (".dart_tool",),
    Stack.KOTLIN: _JVM,
    Stack.ANDROID: _JVM,
    Stack.JAVA: _JVM,
    # Not "packages": a Node monorepo keeps its own code under that name.
    Stack.DOTNET: ("TestResults", ".vs"),
    Stack.RUST: ("target",),
    Stack.RUBY: (".bundle",),
    Stack.PHP: _PHP,
    Stack.LARAVEL: _PHP,
}

# Editor and AI-assistant folders. `.github` is deliberately NOT here: workflows are
# configuration worth analyzing.
TOOL_DIRS: tuple[str, ...] = (
    ".context",
    ".agents",
    ".claude",
    ".cursor",
    ".windsurf",
    ".idea",
    ".vscode",
    ".history",
)


_GITIGNORE_LIMIT = 64 * 1024


def gitignore_patterns(root: Path) -> list[str]:
    """Plain folder names and paths listed in the project's root `.gitignore`.

    The file is read as plain text, never executed, and only feeds suggestions. Anchored
    patterns (`/build`, `docs/old`) come back with a leading `/`; bare names have none.
    Globs, negations, comments and parent references are skipped.
    """
    path = root / ".gitignore"
    try:
        if path.is_symlink() or not path.is_file():
            return []
        with path.open("rb") as handle:
            raw = handle.read(_GITIGNORE_LIMIT)
    except OSError:
        return []
    found: list[str] = []
    for line in raw.decode("utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith(("#", "!")):
            continue
        if line.endswith("/**"):
            line = line[:-3]
        line = line.rstrip("/") if line.endswith("/") else line
        if any(c in line for c in "*?[\\"):
            continue
        name = line.lstrip("/")
        anchored = line.startswith("/") or "/" in name
        segments = name.split("/")
        if not name or "" in segments or "." in segments or ".." in segments:
            continue
        pattern = "/" + name if anchored else name
        if pattern not in found:
            found.append(pattern)
    return found


def ignored_entries(root: Path) -> tuple[list[str], str]:
    """What this run skips with `--exclude-gitignored`: (entries, source).

    Inside a git work tree the source is "git": the folders and files git ignores (read-only
    query). Elsewhere it is "gitignore": the plain names of the root `.gitignore`. Entries are
    relative posix paths, folders without the trailing slash; names with wildcard characters
    are left out because an exclusion entry would read them as a file pattern.
    """
    listed = git_ignored(root)
    if listed is None:
        names = [p.lstrip("/") for p in gitignore_patterns(root)]
        return [n for n in dict.fromkeys(names) if n], "gitignore"
    entries = [e.rstrip("/") for e in listed]
    kept = [e for e in dict.fromkeys(entries) if e and not any(c in e for c in "*?[\\")]
    return kept, "git"


@dataclass(frozen=True)
class Suggestion:
    pattern: str
    example: str  # first existing relative folder that matches
    source: str  # "stack", "tool" or "gitignore"
    stack: str = ""  # stack code when the source is "stack"


def suggest(
    root: Path,
    stacks: list[StackHit],
    exclusions: Exclusions,
    folders: list[str] | None = None,
) -> list[Suggestion]:
    """Patterns that match an existing folder which is not skipped yet."""
    if folders is None:
        folders = list_folders(root, depth=3)
    candidates: list[tuple[str, str, str]] = []
    anchored: set[str] = set()
    detected = {hit.stack for hit in stacks}
    for stack, patterns in STACK_DIRS.items():
        if stack in detected:
            candidates += [(p, "stack", stack.value) for p in patterns]
    candidates += [(p, "tool", "") for p in TOOL_DIRS]
    for raw in gitignore_patterns(root):
        if raw.startswith("/"):
            anchored.add(raw[1:])
        candidates.append((raw.lstrip("/"), "gitignore", ""))

    found: list[Suggestion] = []
    seen: set[str] = set()
    for pattern, source, stack_code in candidates:
        if pattern in seen:
            continue
        matcher = Exclusions(dirs=(pattern,))
        is_anchored = source == "gitignore" and pattern in anchored
        for folder in folders:
            hit = folder == pattern if is_anchored else matcher.excludes_dir(folder)
            if hit and not exclusions.excludes_dir(folder):
                seen.add(pattern)
                found.append(Suggestion(pattern, folder, source, stack_code))
                break
    return found


def reason(s: Suggestion) -> Message:
    """Why the folder is suggested, as a stored message."""
    if s.source == "stack":
        return msg("core.presets.reason.stack", stack=s.stack)
    if s.source == "gitignore":
        return msg("core.presets.reason.gitignore")
    return msg("core.presets.reason.tool")
