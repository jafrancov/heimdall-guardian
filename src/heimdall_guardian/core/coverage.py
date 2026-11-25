"""Which layers Heimdall covers per stack: pure logic, no file reads."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from ..i18n import Message, msg
from .detector import Stack


@dataclass(frozen=True)
class StackCoverage:
    name: str  # display name
    code_rules: bool  # own code rules (Opengrep or Bandit)
    endpoints: bool  # endpoint inventory


# Secrets, dependencies and configuration apply to every stack. When adding rules
# or an endpoint extractor for a stack, just change its entry. Docker and Git
# are not languages: they carry no note.
COVERAGE: dict[Stack, StackCoverage] = {
    Stack.PYTHON: StackCoverage("Python", code_rules=True, endpoints=False),
    Stack.DJANGO: StackCoverage("Django", code_rules=True, endpoints=True),
    Stack.PHP: StackCoverage("PHP", code_rules=True, endpoints=True),
    Stack.LARAVEL: StackCoverage("Laravel", code_rules=True, endpoints=True),
    Stack.DOTNET: StackCoverage(".NET", code_rules=True, endpoints=True),
    Stack.NODE: StackCoverage("Node.js", code_rules=True, endpoints=True),
    Stack.TYPESCRIPT: StackCoverage("TypeScript", code_rules=True, endpoints=True),
    Stack.DART: StackCoverage("Dart", code_rules=True, endpoints=False),
    Stack.FLUTTER: StackCoverage("Flutter", code_rules=True, endpoints=False),
    Stack.SWIFT: StackCoverage("Swift", code_rules=True, endpoints=False),
    Stack.KOTLIN: StackCoverage("Kotlin", code_rules=True, endpoints=False),
    Stack.ANDROID: StackCoverage("Android", code_rules=True, endpoints=False),
    Stack.JAVA: StackCoverage("Java", code_rules=False, endpoints=False),
    Stack.GO: StackCoverage("Go", code_rules=False, endpoints=False),
    Stack.RUBY: StackCoverage("Ruby", code_rules=False, endpoints=False),
    Stack.RUST: StackCoverage("Rust", code_rules=False, endpoints=False),
}


# A stack that lives inside another does not repeat the note: Flutter already says
# what Dart would, and Node.js what TypeScript would (they share rules). A Flutter app
# ships native folders (`android/`, `ios/`) with generated code: its rules review that
# configuration, so Android, Kotlin and Swift carry no separate note.
_COVERED_BY = {
    Stack.DART: Stack.FLUTTER,
    Stack.TYPESCRIPT: Stack.NODE,
    Stack.ANDROID: Stack.FLUTTER,
    Stack.KOTLIN: Stack.FLUTTER,
    Stack.SWIFT: Stack.FLUTTER,
}


def coverage_notes(stacks: Iterable[Stack]) -> list[Message]:
    """One note per detected stack that has no code rules of its own.

    They are structured messages (stored in the run and shown in the current language).
    """
    present = set(stacks)
    notes = []
    for stack, cover in COVERAGE.items():  # in enum order
        if stack not in present or cover.code_rules or _COVERED_BY.get(stack) in present:
            continue
        missing = msg(
            "core.coverage.missing_rules" if cover.endpoints else "core.coverage.missing_both"
        )
        notes.append(msg("core.coverage.note", name=cover.name, missing=missing))
    return notes


def rule_stack_names(stacks: Iterable[Stack | str]) -> list[str]:
    """Display names of the detected stacks reviewed by own code rules, in enum order.

    A stack that lives inside another (see `_COVERED_BY`) is left out, and so is Python
    when Django is present, because Django already says it.
    """
    present = {Stack(s) for s in stacks}
    names = []
    for stack, cover in COVERAGE.items():  # in enum order
        if stack not in present or not cover.code_rules:
            continue
        if _COVERED_BY.get(stack) in present:
            continue
        if stack is Stack.PYTHON and Stack.DJANGO in present:
            continue
        names.append(cover.name)
    return names
