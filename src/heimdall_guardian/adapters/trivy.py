"""Trivy in `fs` mode: vulnerable dependencies (DEP) and insecure configuration (CONF)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..core import severity
from ..core.finding import Category, Confidence, Finding, Severity
from ..core.fingerprint import fingerprint
from ..core.masking import mask_generic
from ..core.paths import bases_dir
from ..core.profiles import Module
from ..i18n import msg, texts_of
from .base import (
    DEFAULT_TIMEOUT_SECONDS,
    DOWNLOAD_TIMEOUT_SECONDS,
    AdapterError,
    AdapterResult,
    BinaryAdapter,
    MissingDatabaseError,
    ScanContext,
    anonymous_registry_env,
    find_binary,
    missing_database,
    run,
    stderr_tail,
)

_OWASP_COMPONENTS = "A03:2025 Software Supply Chain Failures"
_OWASP_MISCONFIG = "A02:2025 Security Misconfiguration"


def _vulnerability_severity(vuln: dict[str, Any]) -> tuple[Severity, Confidence]:
    """CVSS from the source Trivy chose; if there is no score, its text label."""
    cvss = vuln.get("CVSS") or {}
    for source in (vuln.get("SeveritySource"), "nvd"):
        score = (cvss.get(source) or {}).get("V3Score")
        if isinstance(score, int | float):
            return severity.from_cvss(float(score)), Confidence.HIGH
    labelled = severity.from_label(str(vuln.get("Severity", "")))
    if labelled is not None:
        return labelled, Confidence.HIGH
    # No score or label: it is not discarded, but it is marked as low confidence.
    return Severity.MEDIUM, Confidence.LOW


def _vulnerability(target: str, vuln: dict[str, Any]) -> Finding:
    vuln_id = str(vuln.get("VulnerabilityID", "desconocida"))
    package = str(vuln.get("PkgName", "?"))
    installed = str(vuln.get("InstalledVersion", "?"))
    fixed = str(vuln.get("FixedVersion", "")).strip()
    sev, confidence = _vulnerability_severity(vuln)
    component = f"{package}@{installed}"
    summary = str(vuln.get("Title") or vuln.get("Description") or "").strip()
    cwes = vuln.get("CweIDs") or []
    return Finding(
        fingerprint=fingerprint(vuln_id, target, component.lower()),
        source="trivy",
        rule_id=vuln_id,
        category=Category.DEPENDENCIES,
        severity=sev,
        confidence=confidence,
        file=target,
        line_start=0,
        line_end=0,
        snippet=component,
        texts=texts_of(
            title=msg("adapter.dependency.title", package=package, installed=installed, id=vuln_id),
            description=msg("adapter.dependency.description", summary=summary),
            recommendation=msg("adapter.trivy.rec_fixed", package=package, version=fixed)
            if fixed
            else msg("adapter.dependency.rec_no_fix"),
        ),
        owasp=_OWASP_COMPONENTS,
        module=Module.DEP,
        fixed_version=fixed,
        cwe=str(cwes[0]) if cwes else None,
        references=[str(vuln["PrimaryURL"])] if vuln.get("PrimaryURL") else [],
    )


def _misconfiguration(target: str, item: dict[str, Any]) -> Finding:
    rule_id = str(item.get("ID") or item.get("AVDID") or "desconocida")
    cause = item.get("CauseMetadata") or {}
    lines = (cause.get("Code") or {}).get("Lines") or []
    snippet = "\n".join(str(line.get("Content", "")) for line in lines[:20])
    details = " ".join(
        text for key in ("Description", "Message") if (text := str(item.get(key) or "").strip())
    )
    return Finding(
        fingerprint=fingerprint(rule_id, target, snippet),
        source="trivy",
        rule_id=rule_id,
        category=Category.CONFIGURATION,
        severity=severity.from_label(str(item.get("Severity", ""))) or Severity.MEDIUM,
        confidence=Confidence.HIGH,
        file=target,
        line_start=int(cause.get("StartLine", 0) or 0),
        line_end=int(cause.get("EndLine", 0) or 0),
        snippet=mask_generic(snippet),
        # Trivy writes the title, description and resolution: they are shown as they are.
        title=str(item.get("Title") or rule_id),
        description=details,
        recommendation=str(item.get("Resolution") or ""),
        texts={}
        if item.get("Resolution")
        else texts_of(recommendation=msg("adapter.trivy.default_resolution")),
        owasp=_OWASP_MISCONFIG,
        module=Module.CONF,
        references=[str(item["PrimaryURL"])] if item.get("PrimaryURL") else [],
    )


def parse_report(data: dict[str, Any], modules: frozenset[Module]) -> list[Finding]:
    findings: list[Finding] = []
    for result in data.get("Results") or []:
        target = Path(str(result.get("Target", ""))).as_posix()
        if Module.DEP in modules:
            findings += [_vulnerability(target, v) for v in result.get("Vulnerabilities") or []]
        if Module.CONF in modules:
            findings += [
                _misconfiguration(target, m)
                for m in result.get("Misconfigurations") or []
                if m.get("Status", "FAIL") == "FAIL"
            ]
    return findings


class TrivyAdapter(BinaryAdapter):
    name = "trivy"
    binary = "trivy"
    modules = frozenset({Module.DEP, Module.CONF, Module.SBOM})

    def _version_info(self) -> dict[str, Any]:
        path = find_binary(self.binary)
        if path is None:
            return {}
        try:
            proc = run(
                [path, "--cache-dir", str(bases_dir() / "trivy"), "version", "--format", "json"],
                cwd=Path(path).parent,
                timeout=30,
            )
            data = json.loads(proc.stdout)
        except (AdapterError, json.JSONDecodeError):
            return {}
        return data if isinstance(data, dict) else {}

    def version(self) -> str | None:
        value = self._version_info().get("Version")
        return str(value) if value else None

    def db_updated_at(self) -> str | None:
        value = (self._version_info().get("VulnerabilityDB") or {}).get("UpdatedAt")
        return str(value) if value else None

    def _run(self, ctx: ScanContext, name: str, options: list[str]) -> dict[str, Any]:
        """One pass of `trivy fs`; returns the JSON it writes."""
        report = ctx.workdir / name
        cmd = [
            self._bin(),
            "fs",
            *options,
            "--output",
            str(report),
            "--cache-dir",
            str(bases_dir() / "trivy"),
            "--quiet",
            "--disable-telemetry",
            "--skip-version-check",
            # No calls to external services to resolve dependencies (P3).
            "--offline-scan",
        ]
        if not ctx.update_dbs:
            cmd += ["--skip-db-update", "--skip-java-db-update", "--skip-check-update"]
        for excluded in ctx.exclusions.dirs:
            cmd += ["--skip-dirs", f"**/{excluded}"]
        cmd.append(str(ctx.root))

        # `cwd` is the temporary directory: there is no `.trivyignore` or
        # `trivy.yaml` there that the analyzed code could contribute.
        proc = run(
            cmd,
            cwd=ctx.workdir,
            env=anonymous_registry_env(ctx.workdir),
            timeout=DOWNLOAD_TIMEOUT_SECONDS if ctx.update_dbs else DEFAULT_TIMEOUT_SECONDS,
        )
        if proc.returncode != 0 or not report.is_file():
            if "--skip-db-update cannot be specified" in (proc.stderr or ""):
                raise MissingDatabaseError()
            raise AdapterError("adapter.failed", tool="trivy", detail=stderr_tail(proc))
        try:
            data: dict[str, Any] = json.loads(report.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise AdapterError("adapter.unreadable_report", tool="trivy", error=str(exc)) from exc
        return data

    def has_database(self) -> bool:
        return (bases_dir() / "trivy" / "db" / "trivy.db").is_file()

    def invoke(self, ctx: ScanContext) -> AdapterResult:
        result = AdapterResult()
        scanners = [
            name
            for module, name in ((Module.DEP, "vuln"), (Module.CONF, "misconfig"))
            if module in ctx.modules
        ]
        if "vuln" in scanners and not ctx.update_dbs and not self.has_database():
            # Without the database there is no dependency review, but the configuration
            # review does not need it: what can run does run, and what was missing is reported.
            scanners.remove("vuln")
            result.limitations.append(missing_database())
            if not scanners and Module.SBOM not in ctx.modules:
                raise MissingDatabaseError()
        if scanners:
            data = self._run(
                ctx, "trivy.json", ["--scanners", ",".join(scanners), "--format", "json"]
            )
            result.findings = parse_report(data, ctx.modules)
        if Module.SBOM in ctx.modules:
            # Inventory only: read lockfiles and manifests, no vulnerability database.
            result.sbom = self._run(ctx, "sbom.cdx.json", ["--format", "cyclonedx"])
        return result
