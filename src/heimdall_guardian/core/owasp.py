"""OWASP Top 10:2025: categories, Heimdall's coverage and verification guidance (pure logic).

Single source of the labels, of the executive-facing texts the reports carry and of
the per-CWE guidance for whoever verifies by hand. Runs stored with 2021 labels are
translated with `migrate_2021` when read; the findings' fingerprint does not change.

The texts live in the catalog (`owasp.*`) and are requested through functions: nothing
visible is computed at import time, so that switching language also switches the reports.
"""

from __future__ import annotations

import copy
import re
from dataclasses import dataclass
from typing import Any

from ..i18n import t

YEAR = 2025
COVERAGE_LEVELS = ("yes", "partial", "no")


def what_is_owasp(lang: str | None = None) -> str:
    return t("owasp.what_is", lang)


def scope_warning(lang: str | None = None) -> str:
    return t("owasp.scope_warning", lang)


def coverage_label(level: str, lang: str | None = None) -> str:
    """ "Yes" / "Partial" / "No" (localized) for a coverage level (`yes` | `partial` | `no`)."""
    return t(f"owasp.coverage.{level}", lang)


@dataclass(frozen=True)
class OwaspCategory:
    code: str  # «A05»
    name_en: str  # official name, the one the findings' label carries
    coverage: str  # «yes» | «partial» | «no»

    @property
    def label(self) -> str:
        """The label the findings carry: `A05:2025 Injection`."""
        return f"{self.code}:{YEAR} {self.name_en}"

    def name(self, lang: str | None = None) -> str:
        """The name in the requested language (in English, the official one)."""
        return t(f"owasp.{self.code}.name", lang)

    def explanation(self, lang: str | None = None) -> str:  # for an executive
        return t(f"owasp.{self.code}.explanation", lang)

    def example(self, lang: str | None = None) -> str:
        return t(f"owasp.{self.code}.example", lang)

    def coverage_note(self, lang: str | None = None) -> str:
        return t(f"owasp.{self.code}.coverage_note", lang)


CATEGORIES: tuple[OwaspCategory, ...] = (
    OwaspCategory("A01", "Broken Access Control", "yes"),
    OwaspCategory("A02", "Security Misconfiguration", "yes"),
    OwaspCategory("A03", "Software Supply Chain Failures", "partial"),
    OwaspCategory("A04", "Cryptographic Failures", "partial"),
    OwaspCategory("A05", "Injection", "yes"),
    OwaspCategory("A06", "Insecure Design", "partial"),
    OwaspCategory("A07", "Authentication Failures", "partial"),
    OwaspCategory("A08", "Software or Data Integrity Failures", "partial"),
    OwaspCategory("A09", "Security Logging and Alerting Failures", "no"),
    OwaspCategory("A10", "Mishandling of Exceptional Conditions", "no"),
)

# Translation of 2021 labels → 2025 (by 2021 code and name).
_FROM_2021: dict[str, str] = {
    "A01:2021 Broken Access Control": "A01",
    "A02:2021 Cryptographic Failures": "A04",
    "A03:2021 Injection": "A05",
    "A04:2021 Insecure Design": "A06",
    "A05:2021 Security Misconfiguration": "A02",
    "A06:2021 Vulnerable and Outdated Components": "A03",
    "A07:2021 Identification and Authentication Failures": "A07",
    "A08:2021 Software and Data Integrity Failures": "A08",
    "A09:2021 Security Logging and Monitoring Failures": "A09",
    "A10:2021 Server-Side Request Forgery": "A01",
}
_BY_CODE = {category.code: category for category in CATEGORIES}
_CODE = re.compile(r"^(A\d{2}):2025\b")


def migrate_2021(label: str) -> str:
    """2021 label → its 2025 equivalent; anything unknown or already 2025 is returned as is."""
    code = _FROM_2021.get(label.strip()) if isinstance(label, str) else None
    return _BY_CODE[code].label if code else label


def migrate_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Copy of a run's result with the OWASP labels in 2025.

    It touches neither the fingerprint nor what is stored: it is applied on read, so an
    old run is shown and exported with the current edition.
    """
    lists = [key for key in ("findings", "fixed") if payload.get(key)]
    if not any(
        isinstance(item.get("owasp"), str) and item["owasp"] in _FROM_2021
        for key in lists
        for item in payload[key]
    ):
        return payload
    migrated = copy.copy(payload)
    for key in lists:
        migrated[key] = [
            {**item, "owasp": migrate_2021(item["owasp"])} if item.get("owasp") else item
            for item in payload[key]
        ]
    return migrated


def category_code(label: str | None) -> str | None:
    """`A05:2025 Injection` → `A05`; None if the label is not from the 2025 edition."""
    match = _CODE.match(label or "")
    return match[1] if match else None


def coverage_rows(findings: list[dict[str, Any]], lang: str | None = None) -> list[dict[str, Any]]:
    """The 10 categories with how many of these (open) findings fall into each."""
    counts: dict[str, int] = {}
    for finding in findings:
        code = category_code(finding.get("owasp"))
        if code:
            counts[code] = counts.get(code, 0) + 1
    return [
        {
            "code": c.code,
            "label": c.label,
            "name": c.name(lang),
            "name_en": c.name_en,
            "explanation": c.explanation(lang),
            "example": c.example(lang),
            "coverage": c.coverage,
            "coverage_text": coverage_label(c.coverage, lang),
            "coverage_note": c.coverage_note(lang),
            "count": counts.get(c.code, 0),
        }
        for c in CATEGORIES
    ]


# CWEs with verification guidance (the text is in the catalog: `owasp.hint.<CWE>`).
_HINTED: frozenset[str] = frozenset(
    {
        "CWE-16",
        "CWE-20",
        "CWE-22",
        "CWE-78",
        "CWE-79",
        "CWE-89",
        "CWE-94",
        "CWE-95",
        "CWE-80",
        "CWE-98",
        "CWE-155",
        "CWE-209",
        "CWE-259",
        "CWE-284",
        "CWE-285",
        "CWE-295",
        "CWE-306",
        "CWE-311",
        "CWE-319",
        "CWE-312",
        "CWE-326",
        "CWE-327",
        "CWE-330",
        "CWE-345",
        "CWE-347",
        "CWE-352",
        "CWE-377",
        "CWE-400",
        "CWE-434",
        "CWE-477",
        "CWE-494",
        "CWE-489",
        "CWE-502",
        "CWE-601",
        "CWE-605",
        "CWE-611",
        "CWE-614",
        "CWE-639",
        "CWE-703",
        "CWE-732",
        "CWE-532",
        "CWE-749",
        "CWE-798",
        "CWE-838",
        "CWE-841",
        "CWE-915",
        "CWE-916",
        "CWE-918",
        "CWE-926",
        "CWE-927",
        "CWE-942",
        "CWE-943",
        "CWE-1004",
    }
)


def verification_hint(cwe: str | None, lang: str | None = None) -> str | None:
    """How to verify a finding of that CWE by hand; None if there is no guidance.

    Guidance for whoever verifies by hand: how to check the finding without running
    someone else's code.
    """
    if not cwe:
        return None
    key = cwe.strip().upper()
    return t(f"owasp.hint.{key}", lang) if key in _HINTED else None


def hinted_cwes() -> frozenset[str]:
    return _HINTED
