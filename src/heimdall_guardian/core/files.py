"""Walk of the analyzed folder: read-only, without following symbolic links."""

from __future__ import annotations

import fnmatch
import hashlib
import os
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

DEFAULT_EXCLUDED_DIRS = (
    "node_modules",
    "venv",
    ".venv",
    "vendor",
    "bin",
    "obj",
    "dist",
    "build",
    "static/CACHE",
    "migrations",
)
# Tests and fixtures are excluded from SAST, but not from secret analysis.
DEFAULT_SAST_EXCLUDED_DIRS = ("tests", "test", "__tests__", "fixtures")
# Code and configuration extensions: such a file is analyzed even when it is
# large. The size limit only discards what is not code (binaries, data).
CODE_SUFFIXES = frozenset(
    {
        ".py",
        ".php",
        ".phtml",
        ".cs",
        ".cshtml",
        ".vb",
        ".aspx",
        ".ascx",
        ".js",
        ".jsx",
        ".mjs",
        ".cjs",
        ".ts",
        ".tsx",
        ".vue",
        ".java",
        ".kt",
        ".go",
        ".rb",
        ".rs",
        ".c",
        ".h",
        ".cpp",
        ".hpp",
        ".swift",
        ".sql",
        ".sh",
        ".ps1",
        ".html",
        ".htm",
        ".xml",
        ".config",
        ".json",
        ".yml",
        ".yaml",
        ".toml",
        ".ini",
        ".env",
        ".tf",
        ".gradle",
        ".csproj",
    }
)
# Version-control metadata: never analyzed as code.
_ALWAYS_EXCLUDED_DIRS = (".git", ".hg", ".svn")
# Dependency manifests and lockfiles: a file pattern never skips them.
PROTECTED_FILES = frozenset(
    {
        "package.json",
        "package-lock.json",
        "npm-shrinkwrap.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "bun.lockb",
        "requirements.txt",
        "pipfile",
        "pipfile.lock",
        "poetry.lock",
        "pyproject.toml",
        "uv.lock",
        "setup.py",
        "setup.cfg",
        "composer.json",
        "composer.lock",
        "packages.config",
        "packages.lock.json",
        "directory.packages.props",
        "pubspec.yaml",
        "pubspec.lock",
        "package.swift",
        "package.resolved",
        "podfile",
        "podfile.lock",
        "cartfile.resolved",
        "build.gradle",
        "build.gradle.kts",
        "gradle.lockfile",
        "pom.xml",
        "go.mod",
        "go.sum",
        "gemfile",
        "gemfile.lock",
        "cargo.toml",
        "cargo.lock",
    }
)
PROTECTED_SUFFIXES = (".csproj", ".vbproj", ".fsproj")


def is_protected(relative_file: str) -> bool:
    """Is it a dependency manifest or lockfile (never skipped by a file pattern)?"""
    name = PurePosixPath(relative_file).name.lower()
    return (
        name in PROTECTED_FILES
        or name.endswith(PROTECTED_SUFFIXES)
        or (name.startswith("requirements") and name.endswith(".txt"))
    )


def is_file_pattern(entry: str) -> bool:
    """An exclusion entry with a glob character is a file pattern, not a folder."""
    return any(ch in entry for ch in "*?[")


def existing_file_entry(root: Path, entry: str) -> str | None:
    """The relative posix path when `entry` names an existing regular file under `root`.

    Nothing is resolved through symbolic links and `..` never leaves the folder: an entry
    that is anything else (a folder, a glob, a missing path) gives None.
    """
    text = entry.strip()
    if not text or is_file_pattern(text):
        return None
    candidate = Path(text)
    if candidate.is_absolute():
        try:
            candidate = candidate.relative_to(root)
        except ValueError:
            return None
    normal = os.path.normpath(candidate)
    if normal in (".", "") or normal == ".." or normal.startswith(".." + os.sep):
        return None
    full = root / normal
    if full.is_symlink() or not full.is_file():
        return None
    return PurePosixPath(*Path(normal).parts).as_posix()


def _contains(parts: tuple[str, ...], pattern: str) -> bool:
    """Does `pattern` (one or more segments) appear as a contiguous run of `parts`?"""
    wanted = PurePosixPath(pattern).parts
    size = len(wanted)
    return any(parts[i : i + size] == wanted for i in range(len(parts) - size + 1))


@dataclass(frozen=True)
class Exclusions:
    dirs: tuple[str, ...] = DEFAULT_EXCLUDED_DIRS
    sast_dirs: tuple[str, ...] = DEFAULT_SAST_EXCLUDED_DIRS
    max_file_kb: int = 1024
    files: tuple[str, ...] = ()  # file glob patterns
    paths: tuple[str, ...] = ()  # exact files (relative posix paths) named one by one
    # Exact files skipped only by the code rules (SAST): copied third-party libraries, which
    # are still read for secrets, dependencies and configuration.
    sast_files: tuple[str, ...] = ()

    @property
    def file_entries(self) -> tuple[str, ...]:
        """Every file-level entry (glob patterns, then exact paths), for display."""
        return (*self.files, *self.paths)

    def excludes_dir(self, relative_dir: str, *, sast: bool = False) -> bool:
        parts = PurePosixPath(relative_dir).parts
        patterns = _ALWAYS_EXCLUDED_DIRS + self.dirs + (self.sast_dirs if sast else ())
        return any(_contains(parts, pattern) for pattern in patterns)

    def excludes_file(self, relative_file: str) -> bool:
        """Does a file pattern skip it? Manifests and lockfiles are never skipped."""
        if is_protected(relative_file):
            return False
        if relative_file in self.paths:
            return True
        name = PurePosixPath(relative_file).name
        return any(
            fnmatch.fnmatchcase(relative_file if "/" in pattern else name, pattern)
            for pattern in self.files
        )

    def excludes(self, relative_file: str, *, sast: bool = False, secret: bool = False) -> bool:
        if sast and relative_file in self.sast_files:
            return True
        parent = PurePosixPath(relative_file).parent.as_posix()
        if self.excludes_dir(parent, sast=sast):
            return True
        # Secrets are searched in every file: file patterns do not apply to them.
        return not secret and self.excludes_file(relative_file)


@dataclass
class TreeInfo:
    files: list[str] = field(default_factory=list)  # relative paths (posix), sorted
    oversized: list[str] = field(default_factory=list)  # binary and over the limit: skipped
    large_code: list[str] = field(default_factory=list)  # large text: analyzed and flagged
    symlinks: int = 0  # symbolic links ignored
    # Files kept out of analysis by a file pattern. They stay in `files` so the
    # tree hash still covers them.
    pattern_skipped: list[str] = field(default_factory=list)
    # Folders pruned by exclusions (the prune points only), relative posix paths, sorted.
    skipped_dirs: list[str] = field(default_factory=list)

    @property
    def analyzable(self) -> list[str]:
        skipped = {*self.oversized, *self.pattern_skipped}
        return [path for path in self.files if path not in skipped]


def scan_tree(root: Path, exclusions: Exclusions) -> TreeInfo:
    """Lists the files to analyze.

    Symbolic links are ignored: in a vendor's code they could point outside
    the chosen folder.
    """
    info = TreeInfo()
    limit = exclusions.max_file_kb * 1024
    for current, dirnames, filenames in os.walk(root, followlinks=False):
        base = Path(current)
        kept = []
        for name in sorted(dirnames):
            path = base / name
            if path.is_symlink():
                info.symlinks += 1
            elif exclusions.excludes_dir(path.relative_to(root).as_posix()):
                if name not in _ALWAYS_EXCLUDED_DIRS:
                    info.skipped_dirs.append(path.relative_to(root).as_posix())
            else:
                kept.append(name)
        dirnames[:] = kept
        for name in sorted(filenames):
            path = base / name
            if path.is_symlink():
                info.symlinks += 1
                continue
            if not path.is_file():
                continue
            relative = path.relative_to(root).as_posix()
            info.files.append(relative)
            if exclusions.excludes_file(relative):
                info.pattern_skipped.append(relative)
                continue
            if path.stat().st_size > limit:
                # Text (code, styles, templates, data) is analyzed even when
                # large; only binaries are skipped: images, fonts...
                (info.large_code if is_text(path) else info.oversized).append(relative)
    info.files.sort()
    info.skipped_dirs.sort()
    return info


def list_folders(root: Path, depth: int = 2, limit: int = 300) -> list[str]:
    """Project folders up to `depth` levels, including the ones that are skipped."""
    folders: list[str] = []
    pending = [(root, 1)]
    while pending and len(folders) < limit:
        current, level = pending.pop(0)
        try:
            children = sorted(p for p in current.iterdir() if p.is_dir() and not p.is_symlink())
        except OSError:
            continue
        for child in children:
            if child.name in _ALWAYS_EXCLUDED_DIRS:
                continue
            folders.append(child.relative_to(root).as_posix())
            if level < depth:
                pending.append((child, level + 1))
    return sorted(folders)[:limit]


def is_text(path: Path, sample: int = 8192) -> bool:
    """Is it a text file? A null byte near the start gives a binary away."""
    if path.suffix.lower() in CODE_SUFFIXES or path.name.lower() == "dockerfile":
        return True
    try:
        with path.open("rb") as handle:
            return b"\0" not in handle.read(sample)
    except OSError:
        return False


def tree_hash(root: Path, files: list[str]) -> str:
    """SHA-256 of the analyzed tree: identifies which version of the code was reviewed (P6)."""
    digest = hashlib.sha256()
    for relative in sorted(files):
        file_digest = hashlib.sha256()
        with (root / relative).open("rb") as handle:
            for chunk in iter(lambda: handle.read(1 << 20), b""):
                file_digest.update(chunk)
        digest.update(relative.encode("utf-8") + b"\0" + file_digest.digest())
    return digest.hexdigest()


def read_lines(root: Path, relative: str, start: int, end: int, *, max_lines: int = 20) -> str:
    """Reads a snippet of a file in the analyzed folder, without leaving it."""
    if start < 1:
        return ""
    path = root / relative
    try:
        if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
            return ""
        with path.open(encoding="utf-8", errors="replace") as handle:
            lines = handle.read().splitlines()
    except OSError:
        return ""
    end = min(max(end, start), start + max_lines - 1)
    return "\n".join(lines[start - 1 : end])
