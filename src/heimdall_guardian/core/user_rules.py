"""The user's own Opengrep rules: structural checks before the engine ever sees them.

Extra folders come from `[rules] extra_dirs` in `config.toml` (or `hdl rules --dir`). A rule
file is accepted whole or rejected whole, and a rejected one never stops a scan: it is
declared as a limitation instead. A folder inside the analyzed project is ignored, because
the analyzed code must not configure the analysis. Pure Python: the engine's own syntax
check lives in the Opengrep adapter.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

from ..i18n import Message, msg
from .owasp import CATEGORIES, migrate_2021

MAX_FILES = 500
MAX_FILE_BYTES = 1024 * 1024
_ID = re.compile(r"^[A-Z][A-Z0-9]*-[A-Z]+-\d{3}$")
_CWE = re.compile(r"^CWE-\d+$")
_RESERVED_PREFIX = "AI"
_RESERVED_TAG = "CAND"
_SEVERITIES = ("critical", "high", "medium", "low", "info")
_CONFIDENCES = ("high", "medium", "low")
_MATCHERS = ("pattern", "patterns", "pattern-either", "pattern-regex")
_OWASP_LABELS = frozenset(category.label for category in CATEGORIES)


@dataclass(frozen=True)
class RuleProblem:
    file: str
    message: Message


@dataclass(frozen=True)
class UserRules:
    files: tuple[Path, ...]
    problems: tuple[RuleProblem, ...]
    ids: tuple[str, ...]


def own_rule_ids() -> set[str]:
    """IDs of the built-in rules (a user rule may not reuse them)."""
    from ..adapters.opengrep import rules_dir

    directory = rules_dir()
    ids: set[str] = set()
    for path in directory.rglob("*.y*ml") if directory.is_dir() else []:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError):
            continue
        for rule in data.get("rules") or [] if isinstance(data, dict) else []:
            if isinstance(rule, dict) and isinstance(rule.get("id"), str):
                ids.add(rule["id"])
    return ids


def rule_ids_of(path: Path) -> list[str]:
    """IDs defined by a rule file; empty if it cannot be read."""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        return []
    rules = data.get("rules") if isinstance(data, dict) else None
    return [r["id"] for r in rules or [] if isinstance(r, dict) and isinstance(r.get("id"), str)]


def _text(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""


def _has_matcher(rule: dict[str, Any]) -> bool:
    if any(key in rule for key in _MATCHERS):
        return True
    return rule.get("mode") == "taint" and "pattern-sources" in rule and "pattern-sinks" in rule


def _owasp_problem(rule: str, value: object) -> Message | None:
    labels = value if isinstance(value, list) and value else [value]
    for label in labels:
        if not isinstance(label, str) or not label.strip():
            return msg("core.user_rules.missing_field", rule=rule, field="metadata.owasp")
        if label in _OWASP_LABELS:
            continue
        migrated = migrate_2021(label)
        if migrated != label:
            return msg("core.user_rules.owasp_2021", rule=rule, value=label, suggestion=migrated)
        return msg("core.user_rules.bad_owasp", rule=rule, value=label)
    return None


def _id_problem(
    raw_id: object, rule_id: str, unavailable: set[str], own_ids: set[str]
) -> Message | None:
    if not isinstance(raw_id, str) or not raw_id:
        return msg("core.user_rules.missing_field", rule=rule_id, field="id")
    if not _ID.match(raw_id):
        return msg("core.user_rules.bad_id", rule=rule_id)
    parts = raw_id.split("-")
    if parts[0] == _RESERVED_PREFIX or parts[1] == _RESERVED_TAG:
        return msg("core.user_rules.reserved_id", rule=rule_id)
    if raw_id in own_ids:
        return msg("core.user_rules.builtin_id", rule=rule_id)
    if raw_id in unavailable:
        return msg("core.user_rules.duplicate_id", rule=rule_id)
    return None


def _choice_problem(
    metadata: dict[str, Any], key: str, allowed: tuple[str, ...], rule_id: str
) -> Message | None:
    value = metadata.get(key)
    if value is None:
        return msg("core.user_rules.missing_field", rule=rule_id, field=f"metadata.{key}")
    if not isinstance(value, str) or value.strip().lower() not in allowed:
        return msg(
            "core.user_rules.bad_value",
            rule=rule_id,
            field=f"metadata.{key}",
            value=str(value),
            expected=" | ".join(allowed),
        )
    return None


def _metadata_problems(metadata: dict[str, Any], rule_id: str) -> list[Message]:
    out: list[Message | None] = []
    cwe = metadata.get("cwe")
    cwe = cwe[0] if isinstance(cwe, list) and cwe else cwe
    if not isinstance(cwe, str) or not cwe:
        out.append(msg("core.user_rules.missing_field", rule=rule_id, field="metadata.cwe"))
    elif not _CWE.match(cwe):
        out.append(msg("core.user_rules.bad_cwe", rule=rule_id, value=cwe))
    if "owasp" not in metadata:
        out.append(msg("core.user_rules.missing_field", rule=rule_id, field="metadata.owasp"))
    else:
        out.append(_owasp_problem(rule_id, metadata["owasp"]))
    out.append(_choice_problem(metadata, "severity_hdl", _SEVERITIES, rule_id))
    out.append(_choice_problem(metadata, "confidence", _CONFIDENCES, rule_id))
    for key in ("title", "recommendation"):
        if not _text(metadata.get(key)):
            out.append(msg("core.user_rules.missing_field", rule=rule_id, field=f"metadata.{key}"))
    return [item for item in out if item is not None]


def _check_rule(
    rule: Any, index: int, taken: set[str], own_ids: set[str], local: set[str]
) -> list[Message]:
    if not isinstance(rule, dict):
        return [msg("core.user_rules.rule_not_mapping", rule=f"#{index}")]
    raw_id = rule.get("id")
    rule_id = raw_id if isinstance(raw_id, str) and raw_id else f"#{index}"
    out: list[Message | None] = [_id_problem(raw_id, rule_id, taken | local, own_ids)]
    languages = rule.get("languages")
    if not (isinstance(languages, list) and languages):
        out.append(msg("core.user_rules.missing_field", rule=rule_id, field="languages"))
    if not _text(rule.get("message")):
        out.append(msg("core.user_rules.missing_field", rule=rule_id, field="message"))
    if not _has_matcher(rule):
        out.append(msg("core.user_rules.no_matcher", rule=rule_id))
    metadata = rule.get("metadata")
    if isinstance(metadata, dict):
        out += _metadata_problems(metadata, rule_id)
    else:
        out.append(msg("core.user_rules.missing_field", rule=rule_id, field="metadata"))
    return [item for item in out if item is not None]


def _check_file(path: Path, taken: set[str], own_ids: set[str]) -> tuple[list[Message], list[str]]:
    """Problems of a rule file and, when it has none, the IDs it defines."""
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return [msg("core.user_rules.file_too_big", limit_kb=MAX_FILE_BYTES // 1024)], []
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [msg("core.user_rules.bad_yaml", error=" ".join(str(exc).split())[:200])], []
    except (OSError, UnicodeDecodeError) as exc:
        return [msg("core.user_rules.unreadable", error=str(exc))], []
    rules = data.get("rules") if isinstance(data, dict) else None
    if not isinstance(rules, list) or not rules:
        return [msg("core.user_rules.no_rules")], []
    problems: list[Message] = []
    local: set[str] = set()
    ids: list[str] = []
    for index, rule in enumerate(rules, start=1):
        problems += _check_rule(rule, index, taken, own_ids, local)
        if isinstance(rule, dict) and isinstance(rule.get("id"), str):
            local.add(rule["id"])
            ids.append(rule["id"])
    return problems, [] if problems else ids


def check_user_rules(
    dirs: Iterable[str | Path], *, analyzed_root: Path | None, own_ids: set[str]
) -> UserRules:
    """Validates the rule files of the extra folders without running any engine."""
    files: list[Path] = []
    problems: list[RuleProblem] = []
    ids: list[str] = []
    root = analyzed_root.resolve() if analyzed_root is not None else None
    for entry in dirs:
        shown = str(entry)
        folder = Path(entry).expanduser()
        if not folder.is_dir():
            problems.append(RuleProblem(shown, msg("core.user_rules.missing_dir", dir=shown)))
            continue
        folder = folder.resolve()
        if root is not None and (folder == root or root in folder.parents):
            problems.append(RuleProblem(shown, msg("core.user_rules.inside_project", dir=shown)))
            continue
        candidates = sorted(
            p for p in folder.rglob("*") if p.suffix in (".yaml", ".yml") and p.is_file()
        )
        if len(candidates) > MAX_FILES:
            problems.append(
                RuleProblem(
                    shown, msg("core.user_rules.too_many_files", dir=shown, limit=MAX_FILES)
                )
            )
            candidates = candidates[:MAX_FILES]
        for path in candidates:
            if path in files:
                continue
            found, file_ids = _check_file(path, set(ids), own_ids)
            if found:
                problems += [RuleProblem(str(path), item) for item in found]
                continue
            files.append(path)
            ids += file_ids
    return UserRules(files=tuple(files), problems=tuple(problems), ids=tuple(ids))
