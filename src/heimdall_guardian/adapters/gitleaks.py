"""Gitleaks: secrets in files (SEC) and in git history (SEC-H)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from ..core import severity
from ..core.finding import Category, Confidence, Finding
from ..core.fingerprint import fingerprint
from ..core.masking import mask_known
from ..core.profiles import Module
from ..i18n import msg, texts_of
from .base import (
    SAFE_GIT_ENV,
    AdapterError,
    AdapterResult,
    BinaryAdapter,
    ScanContext,
    run,
    stderr_tail,
)

# Our own configuration: without it Gitleaks loads the `.gitleaks.toml` of the analyzed
# folder, and a vendor could use it to hide its secrets.
_CONFIG = 'title = "Heimdall"\n\n[extend]\nuseDefault = true\n'

_GIT_LOG_OPTS = "--full-history --all --no-ext-diff --no-textconv"

_MAX_SNIPPET_LINES = 3


def _relative(path: str, root: Path) -> str:
    candidate = Path(path)
    if candidate.is_absolute():
        try:
            return candidate.relative_to(root).as_posix()
        except ValueError:
            return candidate.as_posix()
    return candidate.as_posix()


def _secret_key(item: dict[str, Any]) -> tuple[str, str]:
    digest = hashlib.sha256(str(item.get("Secret", "")).encode("utf-8")).hexdigest()
    return str(item.get("RuleID", "")), digest


def parse_report(
    items: list[dict[str, Any]],
    root: Path,
    *,
    history: bool,
    current: set[tuple[str, str]] | None = None,
) -> tuple[list[Finding], set[str]]:
    """Turns Gitleaks JSON into findings with the secret already masked.

    In history mode, secrets that are still in the current code (`current`) are
    skipped: the file scan already reports those as CRITICAL.
    """
    findings: list[Finding] = []
    secrets: set[str] = set()
    for item in items:
        secret = str(item.get("Secret", ""))
        if secret:
            secrets.add(secret)
        if history and current and _secret_key(item) in current:
            continue

        rule_id = str(item.get("RuleID", "desconocida"))
        file = _relative(str(item.get("File", "")), root)
        match = str(item.get("Match", "")) or secret
        snippet = "\n".join(match.splitlines()[:_MAX_SNIPPET_LINES])
        detail = str(item.get("Description", "")).strip()

        detector = msg("adapter.gitleaks.detector", detail=detail) if detail else ""
        if history:
            description = msg(
                "adapter.gitleaks.description_history",
                commit=str(item.get("Commit", ""))[:10],
                date=str(item.get("Date", ""))[:10],
                detector=detector,
            )
        else:
            description = msg("adapter.gitleaks.description_code", detector=detector)
        suffix = "history" if history else "code"

        findings.append(
            Finding(
                fingerprint=fingerprint(rule_id, file, match),
                source="gitleaks",
                rule_id=rule_id,
                category=Category.SECRETS,
                severity=severity.for_secret(in_current_code=not history),
                confidence=Confidence.HIGH,
                file=file,
                line_start=int(item.get("StartLine", 0) or 0),
                line_end=int(item.get("EndLine", 0) or 0),
                snippet=mask_known(snippet, [secret]),
                texts=texts_of(
                    title=msg(f"adapter.gitleaks.title_{suffix}", rule=rule_id),
                    description=description,
                    recommendation=msg(f"adapter.gitleaks.rec_{suffix}"),
                ),
                owasp="A07:2025 Authentication Failures",
                cwe="CWE-798",
                module=Module.SEC_H if history else Module.SEC,
            )
        )
    return findings, secrets


class GitleaksAdapter(BinaryAdapter):
    name = "gitleaks"
    binary = "gitleaks"
    version_args = ("version",)
    modules = frozenset({Module.SEC, Module.SEC_H})

    def _scan(self, ctx: ScanContext, mode: str) -> list[dict[str, Any]]:
        config = ctx.workdir / "gitleaks.toml"
        config.write_text(_CONFIG, encoding="utf-8")
        # Empty folder: this way the analyzed code's `.gitleaksignore` is not applied.
        ignore_dir = ctx.workdir / "gitleaks-ignore"
        ignore_dir.mkdir(exist_ok=True)
        report = ctx.workdir / f"gitleaks-{mode}.json"

        cmd = [
            self._bin(),
            mode,
            str(ctx.root),
            "--config",
            str(config),
            "--gitleaks-ignore-path",
            str(ignore_dir),
            "--ignore-gitleaks-allow",
            "--report-format",
            "json",
            "--report-path",
            str(report),
            "--exit-code",
            "0",
            "--no-banner",
            "--no-color",
        ]
        if mode == "git":
            cmd.append(f"--log-opts={_GIT_LOG_OPTS}")
        proc = run(cmd, cwd=ctx.workdir, env=SAFE_GIT_ENV)
        if proc.returncode != 0 or not report.is_file():
            raise AdapterError("adapter.failed", tool=f"gitleaks {mode}", detail=stderr_tail(proc))
        try:
            data = json.loads(report.read_text(encoding="utf-8") or "[]")
        except json.JSONDecodeError as exc:
            raise AdapterError(
                "adapter.unreadable_report", tool=f"gitleaks {mode}", error=str(exc)
            ) from exc
        finally:
            report.unlink(missing_ok=True)  # contains the plaintext secrets
        return data if isinstance(data, list) else []

    def invoke(self, ctx: ScanContext) -> AdapterResult:
        result = AdapterResult()
        # The file scan always runs: SEC-H needs it to know which history
        # secrets are still present in the code.
        current_items = self._scan(ctx, "dir")
        findings, secrets = parse_report(current_items, ctx.root, history=False)
        result.secrets |= secrets
        if Module.SEC in ctx.modules:
            result.findings += findings

        if Module.SEC_H in ctx.modules:
            if (ctx.root / ".git").exists():
                current = {_secret_key(item) for item in current_items}
                history_items = self._scan(ctx, "git")
                findings, secrets = parse_report(
                    history_items, ctx.root, history=True, current=current
                )
                result.findings += findings
                result.secrets |= secrets
            else:
                result.limitations.append(msg("adapter.gitleaks.no_history"))
        return result
