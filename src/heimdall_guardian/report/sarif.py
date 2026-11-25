"""SARIF 2.1.0: normalized data for integrations (CI, DefectDojo)."""

from __future__ import annotations

from typing import Any

from ..core.finding import BaselineStatus, Severity
from ..i18n import render, text_of

_LEVEL = {
    Severity.CRITICAL: "error",
    Severity.HIGH: "error",
    Severity.MEDIUM: "warning",
    Severity.LOW: "note",
    Severity.INFO: "note",
}
_BASELINE = {
    BaselineStatus.NEW: "new",
    BaselineStatus.PERSISTENT: "unchanged",
    BaselineStatus.FIXED: "absent",
}
_SUPPRESSED = {BaselineStatus.ACCEPTED, BaselineStatus.FALSE_POSITIVE}
SARIF_SCHEMA = "https://json.schemastore.org/sarif-2.1.0.json"


def _result(finding: dict[str, Any], with_baseline: bool) -> dict[str, Any]:
    location: dict[str, Any] = {"artifactLocation": {"uri": finding["file"]}}
    if finding["line_start"] >= 1:
        location["region"] = {
            "startLine": finding["line_start"],
            "endLine": max(finding["line_end"], finding["line_start"]),
        }
    result: dict[str, Any] = {
        "ruleId": finding["rule_id"],
        "level": _LEVEL.get(finding["severity"], "warning"),
        "message": {
            "text": f"{text_of(finding, 'title')}. {text_of(finding, 'recommendation')}".strip()
        },
        "locations": [{"physicalLocation": location}],
        "partialFingerprints": {"heimdallFingerprint/v1": finding["fingerprint"]},
        "properties": {
            "id": finding["id"],
            "severity": finding["severity"],
            "category": finding["category"],
            "origin": finding["origin"],
            "detected_by": finding["detected_by"],
            "baseline_status": finding["baseline_status"],
        },
    }
    status = finding["baseline_status"]
    if with_baseline and status in _BASELINE:
        result["baselineState"] = _BASELINE[status]
    if status in _SUPPRESSED:
        result["suppressions"] = [{"kind": "external", "status": "accepted"}]
    return result


def render_sarif(payload: dict[str, Any]) -> dict[str, Any]:
    with_baseline = payload.get("baseline") is not None
    findings = [*payload["findings"], *payload.get("fixed", [])]
    rules: dict[str, dict[str, Any]] = {}
    for finding in findings:
        rule = rules.setdefault(
            finding["rule_id"],
            {
                "id": finding["rule_id"],
                "shortDescription": {"text": text_of(finding, "title")},
                "help": {"text": text_of(finding, "recommendation")},
                "properties": {"tags": []},
            },
        )
        for tag in (finding.get("cwe"), finding.get("owasp")):
            if tag and tag not in rule["properties"]["tags"]:
                rule["properties"]["tags"].append(tag)
    return {
        "$schema": SARIF_SCHEMA,
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Heimdall Guardian",
                        "version": payload["heimdall_version"],
                        "rules": list(rules.values()),
                    }
                },
                "results": [_result(finding, with_baseline) for finding in findings],
                "properties": {
                    "tree_hash": payload["project"]["tree_hash"],
                    "profile": payload["run"]["profile"],
                    "limitations": [render(item) for item in payload["limitations"]],
                },
            }
        ],
    }
