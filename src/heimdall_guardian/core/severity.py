"""Severity normalization per tool."""

from __future__ import annotations

from .finding import Severity

_OPENGREP = {
    "CRITICAL": Severity.CRITICAL,
    "ERROR": Severity.HIGH,
    "HIGH": Severity.HIGH,
    "WARNING": Severity.MEDIUM,
    "MEDIUM": Severity.MEDIUM,
    "INFO": Severity.LOW,
    "LOW": Severity.LOW,
}

_LABEL = {
    "CRITICAL": Severity.CRITICAL,
    "HIGH": Severity.HIGH,
    "MEDIUM": Severity.MEDIUM,
    "MODERATE": Severity.MEDIUM,
    "LOW": Severity.LOW,
}

# Bandit: (severity, confidence). The proposal only fixes HIGH/HIGH → ALTA; the
# rest of the matrix drops a level when confidence does not keep up.
_BANDIT = {
    ("HIGH", "HIGH"): Severity.HIGH,
    ("HIGH", "MEDIUM"): Severity.MEDIUM,
    ("HIGH", "LOW"): Severity.MEDIUM,
    ("MEDIUM", "HIGH"): Severity.MEDIUM,
    ("MEDIUM", "MEDIUM"): Severity.MEDIUM,
    ("MEDIUM", "LOW"): Severity.LOW,
    ("LOW", "HIGH"): Severity.LOW,
    ("LOW", "MEDIUM"): Severity.LOW,
    ("LOW", "LOW"): Severity.INFO,
}


# Rules declare severity with the neutral code (the same one that is stored).
_DECLARED = {
    "critical": Severity.CRITICAL,
    "high": Severity.HIGH,
    "medium": Severity.MEDIUM,
    "low": Severity.LOW,
    "info": Severity.INFO,
}


def parse_declared(value: object) -> Severity | None:
    """Interprets `metadata.severity_hdl` (critical | high | medium | low | info)."""
    if not isinstance(value, str):
        return None
    return _DECLARED.get(value.strip().lower())


def from_opengrep(level: str, severity_hdl: object = None) -> Severity:
    return parse_declared(severity_hdl) or _OPENGREP.get(level.upper(), Severity.MEDIUM)


def from_cvss(score: float) -> Severity:
    if score >= 9.0:
        return Severity.CRITICAL
    if score >= 7.0:
        return Severity.HIGH
    if score >= 4.0:
        return Severity.MEDIUM
    return Severity.LOW


def from_label(label: str) -> Severity | None:
    """Text label from an advisory provider (CRITICAL, HIGH...)."""
    return _LABEL.get(label.strip().upper())


def from_bandit(severity: str, confidence: str) -> Severity:
    return _BANDIT.get((severity.upper(), confidence.upper()), Severity.LOW)


def for_secret(*, in_current_code: bool) -> Severity:
    return Severity.CRITICAL if in_current_code else Severity.HIGH
