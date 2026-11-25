"""Opengrep: central SAST engine, with the own rules (`rules/heimdall/`)."""

from __future__ import annotations

import fnmatch
import hashlib
import json
import os
from collections.abc import Iterable
from pathlib import Path, PurePosixPath
from typing import Any

from ..core import severity
from ..core.files import read_lines
from ..core.finding import Category, Confidence, Finding
from ..core.fingerprint import fingerprint
from ..core.masking import mask_generic
from ..core.profiles import Module
from ..i18n import SUPPORTED, Message, msg, t
from .base import (
    SAFE_GIT_ENV,
    AdapterError,
    AdapterResult,
    BinaryAdapter,
    ScanContext,
    examples_message,
    git_tracked,
    rules_dirs,
    run,
    stderr_tail,
)

_EXIT_FINDINGS = 1
# `validate` only parses rule files; a longer wait means the engine is stuck.
VALIDATE_TIMEOUT_SECONDS = 120
MAX_TARGET_BYTES = 20_000_000
# The rule ID decides category and module: DJ-CONF-001, NET-AUTH-002...
CANDIDATE_TAG = "CAND"
_CATEGORY_BY_TAG = {
    "CONF": (Category.CONFIGURATION, Module.CONF),
    "AUTH": (Category.ACCESS_CONTROL, Module.AUTHZ),
    "IDOR": (Category.ACCESS_CONTROL, Module.AUTHZ),
    # Candidates are a SAST concern; they are separated from the findings after parsing.
    CANDIDATE_TAG: (Category.SAST, Module.SAST),
}
# Rules declare confidence with the neutral code: high | medium | low.
_DECLARED_CONFIDENCE = {
    "high": Confidence.HIGH,
    "medium": Confidence.MEDIUM,
    "low": Confidence.LOW,
}
_NO_NETWORK_ENV = {"SEMGREP_SEND_METRICS": "off", "SEMGREP_ENABLE_VERSION_CHECK": "0"}


def rules_dir() -> Path:
    """Own rules: `HDL_RULES_DIR`, the packaged ones or the repository's `rules/heimdall/`."""
    override = os.environ.get("HDL_RULES_DIR")
    if override:
        return Path(override)
    candidates = rules_dirs()
    return next((path for path in candidates if path.is_dir()), candidates[0])


def rules_version(extra: Iterable[Path] = ()) -> str:
    """Fingerprint of the rules a scan used (P6): the own ones plus the user's accepted files.

    A user file counts by its name and content only, so the digest does not depend on where
    the folder lives on each machine. Without user rules the digest is the same as ever.
    """
    digest = hashlib.sha256()
    directory = rules_dir()
    for path in sorted(directory.rglob("*.y*ml")) if directory.is_dir() else []:
        digest.update(path.relative_to(directory).as_posix().encode("utf-8") + b"\0")
        digest.update(path.read_bytes())
    for path in sorted(extra, key=lambda p: (p.name, str(p))):
        digest.update(b"user:" + path.name.encode("utf-8") + b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()[:12]


def validate_rule_files(
    paths: Iterable[Path], workdir: Path, binary: str | None = None
) -> dict[Path, str]:
    """Asks the engine to validate rule files; returns `{file: short error}` for the bad ones.

    One call checks them all; only if it fails is each file validated alone to isolate the
    bad ones. Raises `AdapterError` if the engine is missing or cannot run.
    """
    files = list(paths)
    if not files:
        return {}
    binary = binary or OpengrepAdapter()._bin()
    env = {**SAFE_GIT_ENV, **_NO_NETWORK_ENV}
    proc = run(
        [binary, "validate", *map(str, files)],
        cwd=workdir,
        env=env,
        timeout=VALIDATE_TIMEOUT_SECONDS,
    )
    if proc.returncode == 0:
        return {}
    failures: dict[Path, str] = {}
    for path in files:
        alone = run(
            [binary, "validate", str(path)],
            cwd=workdir,
            env=env,
            timeout=VALIDATE_TIMEOUT_SECONDS,
        )
        if alone.returncode != 0:
            failures[path] = stderr_tail(alone, 300)
    return failures


def is_candidate(rule_id: str) -> bool:
    """A candidate rule (`<PREFIX>-CAND-NNN`) marks a risky sink for the AI to review."""
    parts = rule_id.split("-")
    return len(parts) > 1 and parts[1] == CANDIDATE_TAG


def split_candidates(findings: Iterable[Finding]) -> tuple[list[Finding], list[Finding]]:
    """Separates `(findings, candidates)`: candidates are never reported on their own."""
    reported: list[Finding] = []
    candidates: list[Finding] = []
    for finding in findings:
        (candidates if is_candidate(finding.rule_id) else reported).append(finding)
    return reported, candidates


def classify(rule_id: str) -> tuple[Category, Module]:
    parts = rule_id.split("-")
    tag = parts[1] if len(parts) > 1 else ""
    return _CATEGORY_BY_TAG.get(tag, (Category.SAST, Module.SAST))


def _first(value: object) -> str | None:
    if isinstance(value, list):
        value = value[0] if value else None
    return str(value) if value else None


def _relative(path: str, root: Path) -> str:
    try:
        return Path(path).relative_to(root).as_posix()
    except ValueError:
        return Path(path).as_posix()


def _rule_texts(metadata: dict[str, Any], message: str, rule_id: str) -> dict[str, dict[str, str]]:
    """Title, description and recommendation of an own rule, in each language.

    English is the base language: it comes in `message`, `metadata.title` and
    `metadata.recommendation`. Translations carry `title_<language>`,
    `recommendation_<language>` and `message_<language>`. Whatever is missing in a language is
    filled in with the rule's English and, as a last resort, with a generic text.
    """
    english = {
        "title": str(metadata.get("title") or message.split(". ")[0] or rule_id),
        "description": message,
        "recommendation": str(
            metadata.get("recommendation") or t("adapter.opengrep.default_recommendation", "en")
        ),
    }
    texts: dict[str, dict[str, str]] = {"en": english}
    for lang in (code for code in SUPPORTED if code != "en"):
        texts[lang] = {
            "title": str(metadata.get(f"title_{lang}") or english["title"]),
            "description": str(metadata.get(f"message_{lang}") or "").strip() or message,
            "recommendation": str(
                metadata.get(f"recommendation_{lang}") or english["recommendation"]
            ),
        }
    return texts


def _needs_tracking(file: str, metadata: dict[str, Any]) -> bool:
    """Does the rule only apply to this file when git versions it (`versioned_only` globs)?"""
    patterns = metadata.get("versioned_only") or []
    if not isinstance(patterns, list):
        return False
    name = PurePosixPath(file).name
    return any(fnmatch.fnmatchcase(file if "/" in str(p) else name, str(p)) for p in patterns)


def parse_report(
    data: dict[str, Any],
    root: Path,
    modules: frozenset[Module],
    untracked: list[str] | None = None,
) -> list[Finding]:
    """Findings of an Opengrep report.

    A rule can declare `metadata.versioned_only` (globs of files): its claim is about
    versioned files ("credentials in a versioned .env"). When `untracked` is a list and the
    folder is inside a git work tree, findings on matching files that git does not track are
    dropped and their paths appended to `untracked`. Outside a git repository they stay.
    """
    findings: list[Finding] = []
    tracked_loaded = False
    tracked = None
    for item in data.get("results") or []:
        # Opengrep prepends the rule's path: `rules.heimdall.django.DJ-SQL-001`.
        rule_id = str(item.get("check_id", "desconocida")).rsplit(".", 1)[-1]
        category, module = classify(rule_id)
        if module not in modules:
            continue
        extra = item.get("extra") or {}
        metadata = extra.get("metadata") or {}
        file = _relative(str(item.get("path", "")), root)
        if untracked is not None and _needs_tracking(file, metadata):
            if not tracked_loaded:
                tracked, tracked_loaded = git_tracked(root), True
            if tracked is not None and not tracked.tracks(file):
                untracked.append(file)
                continue
        start = int((item.get("start") or {}).get("line", 0) or 0)
        end = int((item.get("end") or {}).get("line", start) or start)
        snippet = str(extra.get("lines") or "").rstrip()
        if not snippet or snippet == "requires login":
            snippet = read_lines(root, file, start, end)
        message = str(extra.get("message") or "").strip()
        texts = _rule_texts(metadata, message, rule_id)
        confidence = _DECLARED_CONFIDENCE.get(
            str(metadata.get("confidence", "")).strip().lower(), Confidence.MEDIUM
        )
        references = metadata.get("references") or []
        findings.append(
            Finding(
                fingerprint=fingerprint(rule_id, file, snippet),
                source="opengrep",
                rule_id=rule_id,
                category=category,
                severity=severity.from_opengrep(
                    str(extra.get("severity", "")), metadata.get("severity_hdl")
                ),
                confidence=confidence,
                file=file,
                line_start=start,
                line_end=end,
                snippet=mask_generic(snippet),
                texts=texts,
                owasp=_first(metadata.get("owasp")),
                cwe=_first(metadata.get("cwe")),
                module=module,
                references=[str(r) for r in references] if isinstance(references, list) else [],
                candidate_kind=(
                    str(metadata.get("candidate_kind") or "") if is_candidate(rule_id) else ""
                ),
            )
        )
    return findings


class OpengrepAdapter(BinaryAdapter):
    name = "opengrep"
    binary = "opengrep"
    modules = frozenset({Module.SAST, Module.CONF, Module.AUTHZ})

    def invoke(self, ctx: ScanContext) -> AdapterResult:
        rules = rules_dir()
        if not rules.is_dir() or not any(rules.rglob("*.y*ml")):
            raise AdapterError("adapter.opengrep.no_rules", path=str(rules))
        cmd = [
            self._bin(),
            "scan",
            "--json",
            "--quiet",
            # A single process: in parallel, data-flow (taint) rules
            # lose findings non-deterministically between identical runs.
            "--jobs",
            "1",
            # The `nosemgrep` comments in the analyzed code do not suppress findings.
            "--disable-nosem",
            # By default the engine ignores files larger than 1 MB: the limit is
            # raised so that large code (generated, minified) does get reviewed.
            "--max-target-bytes",
            str(MAX_TARGET_BYTES),
            # Nor its `.gitignore`: in a git repository it would hide whole files.
            "--no-git-ignore",
            # Nor its `.semgrepignore` files (honoured since Opengrep 2.0).
            "--x-ignore-semgrepignore-files",
            "--config",
            str(rules),
        ]
        accepted: list[Path] = []
        rejected: list[Message] = []
        if ctx.user_rules:
            failures = validate_rule_files(ctx.user_rules, ctx.workdir, self._bin())
            for path in ctx.user_rules:
                if path in failures:
                    rejected.append(
                        msg(
                            "adapter.opengrep.user_rule_invalid",
                            file=str(path),
                            detail=failures[path],
                        )
                    )
                else:
                    accepted.append(path)
                    cmd += ["--config", str(path)]
        for excluded in ctx.exclusions.dirs:
            cmd += ["--exclude", excluded]
        cmd.append(str(ctx.root))

        proc = run(cmd, cwd=ctx.workdir, env={**SAFE_GIT_ENV, **_NO_NETWORK_ENV})
        if proc.returncode not in (0, _EXIT_FINDINGS):
            raise AdapterError("adapter.failed", tool="opengrep", detail=stderr_tail(proc))
        try:
            data = json.loads(proc.stdout or "{}")
        except json.JSONDecodeError as exc:
            raise AdapterError(
                "adapter.unreadable_output", tool="opengrep", error=str(exc)
            ) from exc

        untracked: list[str] = []
        reported, candidates = split_candidates(
            parse_report(data, ctx.root, ctx.modules, untracked)
        )
        result = AdapterResult(
            findings=reported,
            candidates=candidates,
            limitations=rejected,
            rule_files=accepted,
        )
        if untracked:
            places = sorted(set(untracked))
            result.limitations.append(
                msg(
                    "core.limit.untracked_versioned",
                    count=len(untracked),
                    examples=examples_message(places),
                )
            )
        errors = data.get("errors") or []
        if errors:
            result.limitations.append(msg("adapter.opengrep.partial", count=len(errors)))
        return result
