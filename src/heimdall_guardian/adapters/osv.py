"""OSV-Scanner: second source of vulnerable dependencies (DEP), reading lockfiles."""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from ..core import severity
from ..core.finding import Category, Confidence, Finding, Severity
from ..core.fingerprint import fingerprint
from ..core.paths import bases_dir
from ..core.profiles import Module
from ..i18n import Message, msg, texts_of
from .base import (
    DEFAULT_TIMEOUT_SECONDS,
    DOWNLOAD_TIMEOUT_SECONDS,
    AdapterError,
    AdapterResult,
    BinaryAdapter,
    MissingDatabaseError,
    ScanContext,
    bases_location,
    run,
    stderr_tail,
)

_OWASP_COMPONENTS = "A03:2025 Software Supply Chain Failures"
_EXIT_VULNERABILITIES_FOUND = 1
_CACHE_ENV = "OSV_SCANNER_LOCAL_DB_CACHE_DIRECTORY"
_EXIT_NO_PACKAGES = 128
_NO_OFFLINE_DB = "no offline version of the OSV database"
_ECOSYSTEM_DB = re.compile(r"could not load db for (\S+) ecosystem")


def _relative(path: str, root: Path) -> str:
    try:
        return Path(path).relative_to(root).as_posix()
    except ValueError:
        return Path(path).as_posix()


def _preferred_id(vuln: dict[str, Any]) -> str:
    """Prefers the CVE: that way the fingerprint matches Trivy's and it is deduplicated."""
    ids = [str(vuln.get("id", "")), *(str(alias) for alias in vuln.get("aliases") or [])]
    return next((i for i in ids if i.startswith("CVE-")), ids[0] or "desconocida")


def _fixed_versions(vuln: dict[str, Any], package: str) -> list[str]:
    fixed: set[str] = set()
    for affected in vuln.get("affected") or []:
        if (affected.get("package") or {}).get("name") != package:
            continue
        for rng in affected.get("ranges") or []:
            if rng.get("type") == "GIT":
                continue
            fixed.update(str(e["fixed"]) for e in rng.get("events") or [] if e.get("fixed"))
    return sorted(fixed)


def _severity(vuln: dict[str, Any], scores: dict[str, str]) -> tuple[Severity, Confidence]:
    raw = scores.get(str(vuln.get("id", "")), "")
    try:
        score = float(raw)
    except ValueError:
        score = 0.0
    if score > 0:
        return severity.from_cvss(score), Confidence.HIGH
    label = str((vuln.get("database_specific") or {}).get("severity", ""))
    labelled = severity.from_label(label)
    if labelled is not None:
        return labelled, Confidence.HIGH
    return Severity.MEDIUM, Confidence.LOW


@dataclass(frozen=True)
class Vulnerability:
    """One vulnerability OSV reports for one package of one lockfile."""

    source: str  # path of the lockfile, as OSV printed it
    name: str
    installed: str
    vuln: dict[str, Any]
    rule_id: str
    severity: Severity
    confidence: Confidence
    fixed: list[str]


def vulnerabilities(data: dict[str, Any]) -> Iterator[Vulnerability]:
    """Flattens the OSV report: one item per (package, vulnerability)."""
    for result in data.get("results") or []:
        source = str((result.get("source") or {}).get("path", ""))
        for entry in result.get("packages") or []:
            package = entry.get("package") or {}
            name = str(package.get("name", "?"))
            installed = str(package.get("version", "?"))
            # `max_severity` (CVSS score) comes per group of equivalent advisories.
            scores = {
                str(vuln_id): str(group.get("max_severity", ""))
                for group in entry.get("groups") or []
                for vuln_id in group.get("ids") or []
            }
            for vuln in entry.get("vulnerabilities") or []:
                sev, confidence = _severity(vuln, scores)
                yield Vulnerability(
                    source=source,
                    name=name,
                    installed=installed,
                    vuln=vuln,
                    rule_id=_preferred_id(vuln),
                    severity=sev,
                    confidence=confidence,
                    fixed=_fixed_versions(vuln, name),
                )


def dependency_finding(
    item: Vulnerability, file: str, *, source: str, recommendation: Message
) -> Finding:
    """The finding for one vulnerability, attached to `file`."""
    component = f"{item.name}@{item.installed}"
    summary = str(item.vuln.get("summary") or "").strip()
    return Finding(
        fingerprint=fingerprint(item.rule_id, file, component.lower()),
        source=source,
        rule_id=item.rule_id,
        category=Category.DEPENDENCIES,
        severity=item.severity,
        confidence=item.confidence,
        file=file,
        line_start=0,
        line_end=0,
        snippet=component,
        texts=texts_of(
            title=msg(
                "adapter.dependency.title",
                package=item.name,
                installed=item.installed,
                id=item.rule_id,
            ),
            description=msg("adapter.dependency.description", summary=summary),
            recommendation=recommendation,
        ),
        owasp=_OWASP_COMPONENTS,
        module=Module.DEP,
        fixed_version=", ".join(item.fixed),
        references=[f"https://osv.dev/vulnerability/{item.vuln.get('id')}"],
    )


def parse_report(data: dict[str, Any], root: Path) -> list[Finding]:
    return [
        dependency_finding(
            item,
            _relative(item.source, root),
            source="osv",
            recommendation=msg("adapter.osv.rec_fixed", package=item.name, versions=item.fixed)
            if item.fixed
            else msg("adapter.dependency.rec_no_fix"),
        )
        for item in vulnerabilities(data)
    ]


class OsvAdapter(BinaryAdapter):
    name = "osv"
    binary = "osv-scanner"
    modules = frozenset({Module.DEP})

    def applies(self, ctx: ScanContext) -> bool:
        return Module.DEP in ctx.modules

    def db_updated_at(self) -> str | None:
        """Date of the most recent file in the local database."""
        files = [p for p in (bases_dir() / "osv").rglob("*") if p.is_file()]
        if not files:
            return None
        newest = max(p.stat().st_mtime for p in files)
        return datetime.fromtimestamp(newest).astimezone().isoformat(timespec="seconds")

    def _scan(self, ctx: ScanContext, target: Path) -> dict[str, Any] | None:
        """Runs the scanner on `target`, always against the local database.

        Returns the parsed report, or None when it found no packages to look at.
        """
        # Our own empty configuration: overrides the analyzed code's `osv-scanner.toml`,
        # with which a vendor could ignore vulnerabilities.
        config = ctx.workdir / "osv-scanner.toml"
        config.write_text("", encoding="utf-8")
        cmd = [
            self._bin(),
            "scan",
            "source",
            "--recursive",
            "--format",
            "json",
            "--config",
            str(config),
            # A vendor's `.gitignore` must not hide lockfiles.
            "--no-ignore",
            "--allow-no-lockfiles",
            # No transitive resolution: it would send the inventory to deps.dev (P3).
            "--no-resolve",
            # Call analysis can launch build scripts (P2).
            "--no-call-analysis=all",
        ]
        # Always against the local database: online mode sends the dependency
        # inventory to osv.dev. The network is only used to update the database.
        if ctx.update_dbs:
            cmd += ["--offline-vulnerabilities", "--download-offline-databases"]
        else:
            cmd.append("--offline")
        cmd.append(str(target))

        directory = bases_dir() / "osv"
        directory.mkdir(parents=True, exist_ok=True)
        proc = run(
            cmd,
            cwd=ctx.workdir,
            env={_CACHE_ENV: str(directory)},
            timeout=DOWNLOAD_TIMEOUT_SECONDS if ctx.update_dbs else DEFAULT_TIMEOUT_SECONDS,
        )
        if proc.returncode == _EXIT_NO_PACKAGES:
            return None
        if proc.returncode not in (0, _EXIT_VULNERABILITIES_FOUND):
            # OSV keeps one database per ecosystem: this project's may be missing
            # even though others exist.
            output = proc.stderr + proc.stdout
            if _NO_OFFLINE_DB in output:
                ecosystems = sorted(set(_ECOSYSTEM_DB.findall(output)))
                named = (
                    msg("adapter.osv.db_of", names=ecosystems)
                    if ecosystems
                    else msg("adapter.osv.db_of_one")
                )
                raise MissingDatabaseError(
                    "adapter.osv.db_missing", partial=True, named=named, **bases_location()
                )
            raise AdapterError("adapter.failed", tool="osv-scanner", detail=stderr_tail(proc))
        try:
            data: dict[str, Any] = json.loads(proc.stdout or "{}")
        except json.JSONDecodeError as exc:
            raise AdapterError(
                "adapter.unreadable_output", tool="osv-scanner", error=str(exc)
            ) from exc
        return data

    def invoke(self, ctx: ScanContext) -> AdapterResult:
        data = self._scan(ctx, ctx.root)
        if data is None:
            return AdapterResult()
        return AdapterResult(findings=parse_report(data, ctx.root))
