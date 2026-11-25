"""OWASP Top 10:2025: categories, migration from 2021, per-CWE guidance and report section."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from heimdall_guardian.core import owasp

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_ORDER = [
    ("A01", "Broken Access Control"),
    ("A02", "Security Misconfiguration"),
    ("A03", "Software Supply Chain Failures"),
    ("A04", "Cryptographic Failures"),
    ("A05", "Injection"),
    ("A06", "Insecure Design"),
    ("A07", "Authentication Failures"),
    ("A08", "Software or Data Integrity Failures"),
    ("A09", "Security Logging and Alerting Failures"),
    ("A10", "Mishandling of Exceptional Conditions"),
]


def test_ten_complete_categories_in_order():
    assert [(c.code, c.name_en) for c in owasp.CATEGORIES] == EXPECTED_ORDER
    for category in owasp.CATEGORIES:
        assert category.label == f"{category.code}:2025 {category.name_en}"
        assert category.coverage in owasp.COVERAGE_LEVELS
        assert all(
            [
                category.name("es"),
                category.explanation("es"),
                category.example("es"),
                category.coverage_note("es"),
            ]
        )
    assert {c.coverage for c in owasp.CATEGORIES} == set(owasp.COVERAGE_LEVELS)


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ("A01:2021 Broken Access Control", "A01:2025 Broken Access Control"),
        ("A02:2021 Cryptographic Failures", "A04:2025 Cryptographic Failures"),
        ("A03:2021 Injection", "A05:2025 Injection"),
        ("A04:2021 Insecure Design", "A06:2025 Insecure Design"),
        ("A05:2021 Security Misconfiguration", "A02:2025 Security Misconfiguration"),
        ("A06:2021 Vulnerable and Outdated Components", "A03:2025 Software Supply Chain Failures"),
        ("A07:2021 Identification and Authentication Failures", "A07:2025 Authentication Failures"),
        (
            "A08:2021 Software and Data Integrity Failures",
            "A08:2025 Software or Data Integrity Failures",
        ),
        (
            "A09:2021 Security Logging and Monitoring Failures",
            "A09:2025 Security Logging and Alerting Failures",
        ),
        ("A10:2021 Server-Side Request Forgery", "A01:2025 Broken Access Control"),
        ("A05:2025 Injection", "A05:2025 Injection"),
        ("Otra cosa", "Otra cosa"),
    ],
)
def test_migrate_2021(old: str, new: str):
    assert owasp.migrate_2021(old) == new


def _rule_files() -> list[Path]:
    return sorted((ROOT / "rules" / "heimdall").rglob("*.yaml"))


def test_rules_use_2025_labels_and_every_cwe_has_a_hint():
    labels = {c.label for c in owasp.CATEGORIES}
    files = _rule_files()
    assert files
    for path in files:
        for rule in yaml.safe_load(path.read_text(encoding="utf-8"))["rules"]:
            meta = rule["metadata"]
            assert meta["owasp"] in labels, path.name
            assert owasp.verification_hint(meta["cwe"]), (
                f"{path.name}: {meta['cwe']} has no guidance"
            )


def test_adapters_cwes_have_a_hint():
    source = "".join(
        p.read_text(encoding="utf-8")
        for p in (ROOT / "src" / "heimdall_guardian").rglob("*.py")
        if "ui" not in p.parts
    )
    for cwe in set(re.findall(r'"(CWE-\d+)"', source)):
        assert owasp.verification_hint(cwe), cwe
    assert owasp.verification_hint(None) is None
    assert owasp.verification_hint("CWE-99999") is None


def test_nothing_in_src_or_rules_keeps_2021():
    pattern = re.compile(r"A\d{2}:2021")
    paths = [*_rule_files(), *(ROOT / "src" / "heimdall_guardian").rglob("*.py")]
    paths = [p for p in paths if p.name != "owasp.py"]
    assert not [p.name for p in paths if pattern.search(p.read_text(encoding="utf-8"))]


def test_coverage_rows_count_open_findings_by_category():
    rows = owasp.coverage_rows(
        [{"owasp": "A05:2025 Injection"}, {"owasp": "A05:2025 Injection"}, {"owasp": None}]
    )
    assert [r["code"] for r in rows] == [c.code for c in owasp.CATEGORIES]
    assert {r["code"]: r["count"] for r in rows}["A05"] == 2
    assert sum(r["count"] for r in rows) == 2
