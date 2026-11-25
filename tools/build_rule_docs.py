"""Generates the documentation pages that come from the code: the rules catalog,
the OWASP coverage page, the supported-stacks page and the CLI reference.

Usage:  python tools/build_rule_docs.py [--check]

Reads `rules/heimdall/**/*.yaml` and the `core/owasp.py`, `core/coverage.py`
and `cli.py` modules, and writes English pages (`X.md`) and Spanish pages (`X.es.md`) under
`docs/`. The output is deterministic: files are sorted and nothing depends on the
date or the machine. `tests/unit/test_rule_docs.py` fails when the versioned pages
are out of date (the CLI reference is git-ignored and always rebuilt). With `--check`,
nothing is written and the exit code says whether the pages are current.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from heimdall_guardian import cli  # noqa: E402
from heimdall_guardian.adapters.opengrep import classify, is_candidate  # noqa: E402
from heimdall_guardian.core import coverage as stack_coverage  # noqa: E402
from heimdall_guardian.core import owasp  # noqa: E402
from heimdall_guardian.i18n import (  # noqa: E402
    category_label,
    confidence_label,
    get_language,
    set_language,
    severity_label,
)

RULES_DIR = ROOT / "rules" / "heimdall"
DOCS_DIR = ROOT / "docs"
LANGS = ("en", "es")
SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}

STACK_NAMES = {
    "dart": "Dart and Flutter",
    "django": "Python and Django",
    "dotnet": ".NET",
    "kotlin": "Kotlin and Android",
    "node": "Node.js and TypeScript",
    "php": "PHP and Laravel",
    "swift": "Swift",
}

TEXT = {
    "en": {
        "rules_title": "Rules catalog",
        "rules_intro": (
            "Heimdall Guardian ships {count} own rules in Opengrep format. This catalog is "
            "generated from the rule files, so it always matches the version you install."
        ),
        "columns": ["ID", "Title", "Severity", "Confidence", "CWE", "OWASP"],
        "detects": "What it detects",
        "fix": "How to fix it",
        "why": "Why it matters",
        "verify": "How to verify it",
        "facts": "Facts",
        "severity": "Severity",
        "confidence": "Confidence",
        "category": "Category",
        "languages": "Languages",
        "stack": "Stack",
        "why_text": "This rule maps to {cwe} and to the OWASP Top 10:2025 category {owasp}.",
        "back": "Back to the rules catalog",
        "checks_title": "What it checks",
        "checks_intro": (
            "Findings are classified with the OWASP Top 10:2025 categories. Covering a "
            "category does not mean there are no other risks."
        ),
        "checks_cols": ["Category", "Coverage", "What it is", "Example", "What Heimdall does"],
        "stacks_title": "Supported stacks",
        "stacks_intro": (
            "Heimdall Guardian detects the stack from file names and manifests, without "
            "running anything. Secrets, dependencies and configuration are checked in any "
            "project; this table shows the layers that depend on the stack."
        ),
        "stacks_cols": ["Stack", "Own code rules", "Endpoint inventory"],
        "yes": "yes",
        "no": "no",
        "candidate": "Candidate: only reviewed by the local AI, never reported on its own",
        "candidate_mark": "candidate",
    },
    "es": {
        "rules_title": "Catálogo de reglas",
        "rules_intro": (
            "Heimdall Guardian incluye {count} reglas propias en formato Opengrep. Este "
            "catálogo se genera a partir de los archivos de reglas, así que siempre coincide "
            "con la versión que instalas."
        ),
        "columns": ["ID", "Título", "Severidad", "Confianza", "CWE", "OWASP"],
        "detects": "Qué detecta",
        "fix": "Cómo corregirlo",
        "why": "Por qué importa",
        "verify": "Cómo verificarlo",
        "facts": "Datos",
        "severity": "Severidad",
        "confidence": "Confianza",
        "category": "Categoría",
        "languages": "Lenguajes",
        "stack": "Stack",
        "why_text": (
            "Esta regla corresponde a {cwe} y a la categoría {owasp} del OWASP Top 10:2025."
        ),
        "back": "Volver al catálogo de reglas",
        "checks_title": "Qué revisa",
        "checks_intro": (
            "Los hallazgos se clasifican con las categorías del OWASP Top 10:2025. Cubrir una "
            "categoría no significa que no existan otros riesgos."
        ),
        "checks_cols": ["Categoría", "Cobertura", "Qué es", "Ejemplo", "Qué hace Heimdall"],
        "stacks_title": "Stacks soportados",
        "stacks_intro": (
            "Heimdall Guardian detecta el stack por los nombres de archivo y los manifiestos, "
            "sin ejecutar nada. Los secretos, las dependencias y la configuración se revisan "
            "en cualquier proyecto; esta tabla muestra las capas que dependen del stack."
        ),
        "stacks_cols": ["Stack", "Reglas de código propias", "Inventario de endpoints"],
        "yes": "sí",
        "no": "no",
        "candidate": "Candidata: solo la revisa la IA local, nunca se reporta sola",
        "candidate_mark": "candidata",
    },
}


def _stack_name(stack: str, lang: str) -> str:
    name = STACK_NAMES.get(stack, stack)
    return name.replace(" and ", " y ") if lang == "es" else name


def _suffix(lang: str) -> str:
    return "" if lang == "en" else ".es"


def _cell(text: str) -> str:
    """Escapes text for a Markdown table cell or paragraph (foreign text may hold HTML)."""
    flat = " ".join(str(text).split())
    return flat.replace("|", "\\|").replace("<", "&lt;").replace(">", "&gt;")


def load_rules() -> list[dict[str, Any]]:
    """Every own rule as a flat dict, sorted by stack and ID."""
    rules = []
    for path in sorted(RULES_DIR.glob("*/*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        rule = data["rules"][0]
        meta = rule["metadata"]
        rules.append(
            {
                "id": rule["id"],
                "stack": path.parent.name,
                "languages": list(rule["languages"]),
                "message": {"en": rule["message"], "es": meta.get("message_es", rule["message"])},
                "title": {"en": meta["title"], "es": meta.get("title_es", meta["title"])},
                "recommendation": {
                    "en": meta["recommendation"],
                    "es": meta.get("recommendation_es", meta["recommendation"]),
                },
                "cwe": str(meta["cwe"]),
                "owasp": str(meta["owasp"]),
                "severity": str(meta["severity_hdl"]),
                "confidence": str(meta["confidence"]),
                "category": classify(rule["id"])[0].value,
                "candidate": is_candidate(rule["id"]),
            }
        )
    rules.sort(key=lambda r: (r["stack"], r["id"]))
    return rules


def _cwe_link(cwe: str) -> str:
    number = cwe.upper().removeprefix("CWE-")
    return f"[{cwe}](https://cwe.mitre.org/data/definitions/{number}.html)"


def _owasp_name(label: str, lang: str) -> str:
    code = owasp.category_code(label)
    category = owasp._BY_CODE.get(code or "")
    return f"{code}:2025 {category.name(lang)}" if category else label


def rule_page(rule: dict[str, Any], lang: str) -> str:
    tx = TEXT[lang]
    hint = owasp.verification_hint(rule["cwe"], lang)
    lines = [
        f"# {rule['id']}: {_cell(rule['title'][lang])}",
        "",
        f"[{tx['back']}](index{_suffix(lang)}.md)",
        "",
        f"## {tx['detects']}",
        "",
        *([f"> {tx['candidate']}", ""] if rule["candidate"] else []),
        _cell(rule["message"][lang]),
        "",
        f"## {tx['fix']}",
        "",
        _cell(rule["recommendation"][lang]),
        "",
        f"## {tx['why']}",
        "",
        tx["why_text"].format(cwe=_cwe_link(rule["cwe"]), owasp=_owasp_name(rule["owasp"], lang)),
        "",
    ]
    if hint:
        lines += [f"## {tx['verify']}", "", _cell(hint), ""]
    lines += [
        f"## {tx['facts']}",
        "",
        "| | |",
        "|---|---|",
        f"| {tx['severity']} | {severity_label(rule['severity'], lang)} |",
        f"| {tx['confidence']} | {confidence_label(rule['confidence'], lang)} |",
        f"| {tx['category']} | {category_label(rule['category'], lang)} |",
        f"| {tx['stack']} | {_stack_name(rule['stack'], lang)} |",
        f"| {tx['languages']} | {', '.join(f'`{x}`' for x in rule['languages'])} |",
        f"| CWE | {_cwe_link(rule['cwe'])} |",
        f"| OWASP | {_cell(_owasp_name(rule['owasp'], lang))} |",
        "",
    ]
    return "\n".join(lines)


def rules_index(rules: list[dict[str, Any]], lang: str) -> str:
    tx = TEXT[lang]
    lines = [f"# {tx['rules_title']}", "", tx["rules_intro"].format(count=len(rules)), ""]
    header = "| " + " | ".join(tx["columns"]) + " |"
    divider = "|" + "---|" * len(tx["columns"])
    for stack in sorted({r["stack"] for r in rules}):
        group = [r for r in rules if r["stack"] == stack]
        group.sort(key=lambda r: (SEVERITY_ORDER.get(r["severity"], 9), r["id"]))
        lines += [f"## {_stack_name(stack, lang)}", "", header, divider]
        for r in group:
            lines.append(
                f"| [{r['id']}]({r['id']}{_suffix(lang)}.md) | {_cell(r['title'][lang])}"
                f"{' (' + tx['candidate_mark'] + ')' if r['candidate'] else ''} "
                f"| {severity_label(r['severity'], lang)} "
                f"| {confidence_label(r['confidence'], lang)} | {r['cwe']} "
                f"| {_cell(_owasp_name(r['owasp'], lang))} |"
            )
        lines.append("")
    return "\n".join(lines)


def checks_page(lang: str) -> str:
    tx = TEXT[lang]
    lines = [
        f"# {tx['checks_title']}",
        "",
        owasp.what_is_owasp(lang),
        "",
        tx["checks_intro"],
        "",
        f"> {owasp.scope_warning(lang)}",
        "",
        "| " + " | ".join(tx["checks_cols"]) + " |",
        "|" + "---|" * len(tx["checks_cols"]),
    ]
    for c in owasp.CATEGORIES:
        lines.append(
            f"| {c.code}:2025 {_cell(c.name(lang))} | {owasp.coverage_label(c.coverage, lang)} "
            f"| {_cell(c.explanation(lang))} | {_cell(c.example(lang))} "
            f"| {_cell(c.coverage_note(lang))} |"
        )
    lines.append("")
    return "\n".join(lines)


def stacks_page(lang: str) -> str:
    tx = TEXT[lang]
    lines = [
        f"# {tx['stacks_title']}",
        "",
        tx["stacks_intro"],
        "",
        "| " + " | ".join(tx["stacks_cols"]) + " |",
        "|" + "---|" * len(tx["stacks_cols"]),
    ]
    for cover in stack_coverage.COVERAGE.values():
        rules = tx["yes"] if cover.code_rules else tx["no"]
        endpoints = tx["yes"] if cover.endpoints else tx["no"]
        lines.append(f"| {cover.name} | {rules} | {endpoints} |")
    lines.append("")
    return "\n".join(lines)


def cli_page(lang: str) -> str:
    """The command reference: the `--help` of every command, in the requested language."""
    previous = get_language()
    columns = os.environ.get("COLUMNS")
    os.environ["COLUMNS"] = "88"
    set_language(lang)
    try:
        parser = cli._parser()
        title = "CLI reference" if lang == "en" else "Referencia de la línea de comandos"
        lines = [f"# {title}", "", "```text", parser.format_help().rstrip(), "```", ""]
        seen: set[int] = set()
        for action in parser._actions:
            if not isinstance(action, argparse._SubParsersAction):
                continue
            for name, sub in action.choices.items():
                if id(sub) in seen:
                    continue
                seen.add(id(sub))
                sub.prog = f"hdl {name}"
                lines += [f"## `hdl {name}`", "", "```text", sub.format_help().rstrip(), "```", ""]
        return "\n".join(lines)
    finally:
        set_language(previous)
        if columns is None:
            os.environ.pop("COLUMNS", None)
        else:
            os.environ["COLUMNS"] = columns


def generate(*, include_cli: bool = True) -> dict[str, str]:
    """Every generated page as {path relative to docs/: content}.

    The CLI reference depends on the Python version (argparse formats help differently), so
    it is built on demand, git-ignored and left out of the sync test (`include_cli=False`).
    """
    rules = load_rules()
    pages: dict[str, str] = {}
    for lang in LANGS:
        suffix = _suffix(lang)
        pages[f"rules/index{suffix}.md"] = rules_index(rules, lang)
        pages[f"checks{suffix}.md"] = checks_page(lang)
        pages[f"stacks{suffix}.md"] = stacks_page(lang)
        if include_cli:
            pages[f"cli{suffix}.md"] = cli_page(lang)
        for rule in rules:
            pages[f"rules/{rule['id']}{suffix}.md"] = rule_page(rule, lang)
    return pages


def write(pages: dict[str, str], docs_dir: Path) -> None:
    """Writes the pages and removes stale rule pages that no rule produces any more."""
    rules_dir = docs_dir / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    for stale in rules_dir.glob("*.md"):
        if f"rules/{stale.name}" not in pages:
            stale.unlink()
    for relative, content in pages.items():
        target = docs_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def main() -> int:
    pages = generate()
    if "--check" in sys.argv:
        stale = [
            p
            for p, c in pages.items()
            if not (DOCS_DIR / p).is_file() or (DOCS_DIR / p).read_text(encoding="utf-8") != c
        ]
        for path in stale:
            print(f"out of date: docs/{path}")
        return 1 if stale else 0
    write(pages, DOCS_DIR)
    print(f"{len(pages)} pages written to {DOCS_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
