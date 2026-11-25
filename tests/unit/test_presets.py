from __future__ import annotations

import pytest

from heimdall_guardian.core.config import ExclusionsConfig
from heimdall_guardian.core.detector import Stack, StackHit
from heimdall_guardian.core.files import Exclusions
from heimdall_guardian.core.presets import gitignore_patterns, reason, suggest
from heimdall_guardian.i18n import render

NODE = [StackHit(Stack.NODE, "package.json")]


def _tree(tmp_path):
    for folder in (
        "apps/web/.next",
        ".context",
        "src",
        "node_modules/x",
        ".github/workflows",
        "Pods",
    ):
        (tmp_path / folder).mkdir(parents=True)
    return tmp_path


def test_suggests_stack_then_tool_folders(tmp_path):
    root = _tree(tmp_path)
    found = suggest(root, NODE, ExclusionsConfig().to_exclusions())
    assert [(s.pattern, s.source, s.example) for s in found] == [
        (".next", "stack", "apps/web/.next"),
        (".context", "tool", ".context"),
    ]
    assert found[0].stack == "node"


def test_never_suggests_github_or_undetected_stack_folders(tmp_path):
    root = _tree(tmp_path)
    patterns = {s.pattern for s in suggest(root, NODE, ExclusionsConfig().to_exclusions())}
    assert ".github" not in patterns
    assert "Pods" not in patterns
    assert "node_modules" not in patterns


def test_already_skipped_pattern_is_not_suggested(tmp_path):
    root = _tree(tmp_path)
    skipped = ExclusionsConfig().to_exclusions(exclude=(".next",))
    assert [s.pattern for s in suggest(root, NODE, skipped)] == [".context"]
    assert suggest(root, NODE, Exclusions(dirs=(".next", ".context"))) == []


def test_reason_renders_in_both_languages(tmp_path):
    root = _tree(tmp_path)
    stack, tool = suggest(root, NODE, ExclusionsConfig().to_exclusions())
    assert render(reason(stack), lang="en") == "Usual in node projects"
    assert render(reason(stack), lang="es") == "Habitual en proyectos node"
    assert render(reason(tool), lang="es") == "Carpeta de editor o asistente de IA"


GITIGNORE = "# c\n!keep\n*.log\ntmp/\n/out\ndocs/old/\n.env\nmissing/\n../escape\n"


def _git_tree(tmp_path, folders, gitignore=GITIGNORE):
    for folder in folders:
        (tmp_path / folder).mkdir(parents=True)
    (tmp_path / ".env").write_text("x")
    (tmp_path / ".gitignore").write_text(gitignore)
    return tmp_path


def _git(root, stacks=()):
    found = suggest(root, list(stacks), ExclusionsConfig().to_exclusions())
    return {s.pattern: s for s in found if s.source == "gitignore"}


def test_gitignore_patterns_parsing(tmp_path):
    _git_tree(tmp_path, [])
    assert gitignore_patterns(tmp_path) == ["tmp", "/out", "/docs/old", ".env", "missing"]


def test_gitignore_suggestions(tmp_path):
    root = _git_tree(tmp_path, ["tmp", "a/tmp", "out", "x/out", "docs/old", "src"])
    found = _git(root)
    assert set(found) == {"tmp", "out", "docs/old"}
    assert found["out"].example == "out"
    assert found["docs/old"].example == "docs/old"
    assert render(reason(found["tmp"]), lang="en") == "Listed in the project's .gitignore"
    assert render(reason(found["tmp"]), lang="es") == "Aparece en el .gitignore del proyecto"


def test_anchored_gitignore_pattern_needs_exact_path(tmp_path):
    root = _git_tree(tmp_path, ["x/out", "src"])
    assert "out" not in _git(root)


def test_gitignore_does_not_repeat_stack_suggestion(tmp_path):
    root = _git_tree(tmp_path, ["apps/web/.next"], gitignore=".next/\n")
    found = suggest(root, NODE, ExclusionsConfig().to_exclusions())
    assert [(s.pattern, s.source) for s in found] == [(".next", "stack")]


def test_symlinked_gitignore_is_ignored(tmp_path):
    (tmp_path / "tmp").mkdir()
    real = tmp_path / "real.txt"
    real.write_text("tmp/\n")
    try:
        (tmp_path / ".gitignore").symlink_to(real)
    except OSError:
        pytest.skip("symlinks not available")
    assert gitignore_patterns(tmp_path) == []
    assert _git(tmp_path) == {}


def test_huge_gitignore_is_read_only_up_to_the_limit(tmp_path):
    (tmp_path / "tmp").mkdir()
    (tmp_path / ".gitignore").write_text("# filler\n" * 10000 + "tmp/\n")
    assert _git(tmp_path) == {}
