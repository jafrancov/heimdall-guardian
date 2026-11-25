"""Guard: comments and docstrings in src/ and tests/ are written in English.

Spanish is allowed only in user-facing strings (catalog, reports, UI) and in test data.
This test looks at comments and docstrings only, never at ordinary string literals.
"""

from __future__ import annotations

import ast
import io
import re
import tokenize
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

SPANISH_CHARS = re.compile(r"[áéíóúñÁÉÍÓÚÑ¿¡]")
# Frequent Spanish words that are not English words.
SPANISH_WORDS = re.compile(
    r"\b(?:para|cuando|porque|hallazgos?|reglas?|análisis|carpetas?|archivos?|aquí|también"
    r"|pero|sobre|desde|donde|siempre|nunca|puede|debe|según|además|ningún|ninguna"
    r"|usuario|prueba|pruebas|código|que|del|los|las|una|por|como|hay|cada|solo|nada|todo"
    r"|todos|tiene|tienen|esto|queda|quedan|nunca|sino|aunque|mismo|misma|dato|datos)\b",
    re.IGNORECASE,
)

EXCLUDED_DIRS = (
    ROOT / "tests" / "fixtures",
    ROOT / "tests" / "rules" / "fixtures",
)
EXCLUDED_FILES = {ROOT / "src" / "heimdall_guardian" / "i18n" / "messages_es.py"}

# (path relative to the root, substring of the offending comment/docstring): reason.
# Keep this list short and justified.
ALLOWED: dict[tuple[str, str], str] = {}


def _python_files() -> list[Path]:
    files = []
    for base in (ROOT / "src", ROOT / "tests"):
        for path in sorted(base.rglob("*.py")):
            if path in EXCLUDED_FILES or any(d in path.parents for d in EXCLUDED_DIRS):
                continue
            files.append(path)
    return files


def _texts(path: Path) -> list[tuple[int, str]]:
    """Comments and docstrings of a file as (line, text)."""
    source = path.read_text(encoding="utf-8")
    found: list[tuple[int, str]] = []
    for tok in tokenize.generate_tokens(io.StringIO(source).readline):
        if tok.type == tokenize.COMMENT:
            found.append((tok.start[0], tok.string))
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            doc = ast.get_docstring(node, clean=False)
            if doc and node.body and isinstance(node.body[0], ast.Expr):
                found.append((node.body[0].lineno, doc))
    return found


def _allowed(rel: str, text: str) -> bool:
    return any(rel == p and frag in text for (p, frag) in ALLOWED)


def test_comments_and_docstrings_are_english() -> None:
    offenders = []
    for path in _python_files():
        rel = path.relative_to(ROOT).as_posix()
        for line, text in _texts(path):
            if (SPANISH_CHARS.search(text) or SPANISH_WORDS.search(text)) and not _allowed(
                rel, text
            ):
                offenders.append(f"{rel}:{line}: {text.strip().splitlines()[0][:90]}")
    assert not offenders, "Spanish in comments or docstrings:\n" + "\n".join(offenders)


def test_allowed_exceptions_are_still_needed() -> None:
    """An exception that no longer matches anything must be removed."""
    stale = []
    for (rel, frag), _reason in ALLOWED.items():
        path = ROOT / rel
        if not path.exists():
            stale.append(rel)
            continue
        if not any(
            frag in text and (SPANISH_CHARS.search(text) or SPANISH_WORDS.search(text))
            for _, text in _texts(path)
        ):
            stale.append(f"{rel}: {frag!r}")
    assert not stale, "Unused exceptions: " + ", ".join(stale)


@pytest.mark.parametrize("word", ["hallazgo", "carpeta", "análisis"])
def test_guard_detects_spanish(word: str) -> None:
    assert SPANISH_CHARS.search(word) or SPANISH_WORDS.search(word)
