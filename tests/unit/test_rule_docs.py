"""The generated documentation pages (rules catalog, OWASP, stacks, CLI) stay in sync."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
REGENERATE = "run `python tools/build_rule_docs.py` (or `make docs`) and commit the result"


@pytest.fixture(scope="module")
def builder() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "build_rule_docs", ROOT / "tools" / "build_rule_docs.py"
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["build_rule_docs"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def pages(builder: ModuleType) -> dict[str, str]:
    result: dict[str, str] = builder.generate(include_cli=False)
    return result


def test_versioned_pages_match_the_generator(
    builder: ModuleType, pages: dict[str, str], tmp_path: Path
) -> None:
    builder.write(pages, tmp_path)
    stale = [
        relative
        for relative in pages
        if not (DOCS / relative).is_file()
        or (DOCS / relative).read_text(encoding="utf-8")
        != (tmp_path / relative).read_text(encoding="utf-8")
    ]
    assert not stale, f"out-of-date docs pages {stale[:5]}...: {REGENERATE}"


def test_no_stale_rule_pages(pages: dict[str, str]) -> None:
    on_disk = {f"rules/{path.name}" for path in (DOCS / "rules").glob("*.md")}
    assert on_disk == {name for name in pages if name.startswith("rules/")}, REGENERATE


def test_every_rule_has_a_page_in_both_languages(
    builder: ModuleType, pages: dict[str, str]
) -> None:
    for rule in builder.load_rules():
        assert f"rules/{rule['id']}.md" in pages
        assert f"rules/{rule['id']}.es.md" in pages


def test_generation_is_deterministic(builder: ModuleType, pages: dict[str, str]) -> None:
    assert builder.generate(include_cli=False) == pages
