"""Stack detector: decides by file names and manifests, without running anything."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path, PurePosixPath


class Stack(StrEnum):
    PYTHON = "python"
    DJANGO = "django"
    PHP = "php"
    LARAVEL = "laravel"
    DOTNET = "dotnet"
    NODE = "node"
    TYPESCRIPT = "typescript"
    DART = "dart"
    FLUTTER = "flutter"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    ANDROID = "android"
    JAVA = "java"
    GO = "go"
    RUBY = "ruby"
    RUST = "rust"
    DOCKER = "docker"
    GIT = "git"


@dataclass(frozen=True)
class StackHit:
    stack: Stack
    evidence: str  # file that gives it away

    def to_dict(self) -> dict[str, str]:
        return {"stack": self.stack.value, "evidence": self.evidence}


_PYTHON_MANIFESTS = {"requirements.txt", "pyproject.toml", "pipfile", "setup.py", "uv.lock"}
_DOTNET_SUFFIXES = {".csproj", ".vbproj", ".sln", ".cs", ".cshtml", ".aspx", ".ascx"}
_DOTNET_NAMES = {"web.config", "appsettings.json", "packages.config"}
_COMPOSE = re.compile(r"^(docker-)?compose(\.[\w-]+)?\.ya?ml$")
_DJANGO_DEP = re.compile(r"(?im)^\s*[\"']?django\b(?!-)")
_FLUTTER_SDK = re.compile(r"(?m)^\s*sdk\s*:\s*[\"']?flutter\b")
_SWIFT_NAMES = {"package.swift", "podfile", "package.resolved"}
_MANIFEST_READ_LIMIT = 256 * 1024


def _read(root: Path, relative: str) -> str:
    try:
        with (root / relative).open(encoding="utf-8", errors="replace") as handle:
            return handle.read(_MANIFEST_READ_LIMIT)
    except OSError:
        return ""


def _more_stacks(root: Path, relative: str, name: str, suffix: str) -> list[Stack]:
    """Stacks given away by a file's name or suffix."""
    stacks = []
    if name == "tsconfig.json" or (suffix in {".ts", ".tsx"} and not name.endswith(".d.ts")):
        stacks.append(Stack.TYPESCRIPT)
    if name == "pubspec.yaml" or suffix == ".dart":
        stacks.append(Stack.DART)
    if name == "pubspec.yaml" and _FLUTTER_SDK.search(_read(root, relative)):
        stacks.append(Stack.FLUTTER)
    if suffix == ".swift" or name in _SWIFT_NAMES or ".xcodeproj/" in relative.lower():
        stacks.append(Stack.SWIFT)
    if suffix in {".kt", ".kts"}:
        stacks.append(Stack.KOTLIN)
    if name == "androidmanifest.xml":
        stacks.append(Stack.ANDROID)
    if suffix == ".java" or name == "pom.xml":
        stacks.append(Stack.JAVA)
    if name == "go.mod" or suffix == ".go":
        stacks.append(Stack.GO)
    if name in {"gemfile", "gemfile.lock"} or suffix == ".rb":
        stacks.append(Stack.RUBY)
    if name == "cargo.toml" or suffix == ".rs":
        stacks.append(Stack.RUST)
    return stacks


def detect(root: Path, files: list[str]) -> list[StackHit]:
    """Returns one `StackHit` per stack present, with the first file that shows it."""
    found: dict[Stack, str] = {}

    def hit(stack: Stack, evidence: str) -> None:
        found.setdefault(stack, evidence)

    for relative in files:
        path = PurePosixPath(relative)
        name = path.name.lower()
        suffix = path.suffix.lower()

        if suffix == ".py" or name in _PYTHON_MANIFESTS:
            hit(Stack.PYTHON, relative)
        if name == "manage.py" or (
            Stack.DJANGO not in found
            and ((name.startswith("requirements") and suffix == ".txt") or name == "pyproject.toml")
            and _DJANGO_DEP.search(_read(root, relative))
        ):
            hit(Stack.DJANGO, relative)

        if suffix == ".php" or name == "composer.json":
            hit(Stack.PHP, relative)
        if name == "artisan" or (
            name == "composer.json" and "laravel/framework" in _read(root, relative)
        ):
            hit(Stack.LARAVEL, relative)

        if suffix in _DOTNET_SUFFIXES or name in _DOTNET_NAMES:
            hit(Stack.DOTNET, relative)
        if name == "package.json":
            hit(Stack.NODE, relative)
        for stack in _more_stacks(root, relative, name, suffix):
            hit(stack, relative)
        if name.startswith("dockerfile") or suffix == ".dockerfile" or _COMPOSE.match(name):
            hit(Stack.DOCKER, relative)

    if (root / ".git").exists():
        hit(Stack.GIT, ".git")

    return [StackHit(stack, found[stack]) for stack in Stack if stack in found]
