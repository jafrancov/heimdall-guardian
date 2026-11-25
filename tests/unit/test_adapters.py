from __future__ import annotations

import sys
from pathlib import Path

from heimdall_guardian.adapters import gitleaks, opengrep, osv, trivy
from heimdall_guardian.adapters.bandit import BanditAdapter
from heimdall_guardian.adapters.base import ScanContext
from heimdall_guardian.core.files import Exclusions, scan_tree
from heimdall_guardian.core.finding import Category, Confidence, Severity
from heimdall_guardian.core.profiles import Module

# Absolute on every platform (on Windows "/proyecto" has no drive, so it is not absolute).
ROOT = Path("/proyecto").resolve()
AWS_KEY = "AKIAIOSFODNN7EXAMPLE"


def _leak(**overrides):
    item = {
        "RuleID": "aws-access-token",
        "Description": "AWS credentials",
        "File": str(ROOT / "app" / "settings.py"),
        "StartLine": 4,
        "EndLine": 4,
        "Match": f'AWS_KEY = "{AWS_KEY}"',
        "Secret": AWS_KEY,
        "Commit": "",
    }
    return {**item, **overrides}


def test_gitleaks_current_code_is_critical_and_masked():
    findings, secrets = gitleaks.parse_report([_leak()], ROOT, history=False)
    (finding,) = findings
    assert finding.severity is Severity.CRITICAL
    assert finding.category is Category.SECRETS
    assert finding.file == "app/settings.py"
    assert AWS_KEY not in finding.snippet
    assert "AKIA****MPLE" in finding.snippet
    assert secrets == {AWS_KEY}


def test_gitleaks_history_skips_secrets_still_in_code():
    current_items = [_leak()]
    current = {gitleaks._secret_key(item) for item in current_items}
    history = [
        _leak(File="app/settings.py", Commit="a" * 40, Date="2026-01-05T10:00:00Z"),
        _leak(
            File="deploy/old.env",
            Commit="b" * 40,
            Date="2025-11-02T10:00:00Z",
            Secret="AKIAI44QH8DHBEXAMPLE",
            Match="KEY=AKIAI44QH8DHBEXAMPLE",
        ),
    ]
    findings, secrets = gitleaks.parse_report(history, ROOT, history=True, current=current)
    (finding,) = findings
    assert finding.file == "deploy/old.env"
    assert finding.severity is Severity.HIGH
    assert "bbbbbbbbbb" in finding.description
    assert "AKIAI44QH8DHBEXAMPLE" not in finding.snippet
    assert len(secrets) == 2


def test_trivy_vulnerabilities_and_misconfigurations():
    data = {
        "Results": [
            {
                "Target": "requirements.txt",
                "Vulnerabilities": [
                    {
                        "VulnerabilityID": "CVE-2019-14234",
                        "PkgName": "Django",
                        "InstalledVersion": "2.2.0",
                        "FixedVersion": "2.2.4",
                        "Severity": "HIGH",
                        "SeveritySource": "ghsa",
                        "CVSS": {"ghsa": {"V3Score": 9.8}, "nvd": {"V3Score": 7.5}},
                        "Title": "SQL injection in JSONField",
                        "CweIDs": ["CWE-89"],
                        "PrimaryURL": "https://avd.aquasec.com/nvd/cve-2019-14234",
                    },
                    {"VulnerabilityID": "CVE-0000-0001", "PkgName": "x", "InstalledVersion": "1"},
                ],
            },
            {
                "Target": "Dockerfile",
                "Misconfigurations": [
                    {
                        "ID": "DS002",
                        "Title": "Image user should not be 'root'",
                        "Description": "Running as root is risky.",
                        "Resolution": "Add 'USER <non root user name>'",
                        "Severity": "HIGH",
                        "Status": "FAIL",
                        "CauseMetadata": {"StartLine": 1, "EndLine": 1},
                    },
                    {"ID": "DS999", "Severity": "LOW", "Status": "PASS"},
                ],
            },
        ]
    }
    findings = trivy.parse_report(data, frozenset({Module.DEP, Module.CONF}))
    django, unknown, docker = findings
    assert django.severity is Severity.CRITICAL  # CVSS of the chosen source, not the label
    assert django.rule_id == "CVE-2019-14234"
    assert django.snippet == "Django@2.2.0"
    assert "2.2.4" in django.recommendation
    assert django.cwe == "CWE-89"
    assert (unknown.severity, unknown.confidence) == (Severity.MEDIUM, Confidence.LOW)
    assert docker.category is Category.CONFIGURATION
    assert docker.severity is Severity.HIGH

    only_deps = trivy.parse_report(data, frozenset({Module.DEP}))
    assert {f.category for f in only_deps} == {Category.DEPENDENCIES}


def test_osv_prefers_cve_so_it_merges_with_trivy():
    data = {
        "results": [
            {
                "source": {"path": str(ROOT / "requirements.txt"), "type": "lockfile"},
                "packages": [
                    {
                        # OSV reports the normalized name; Trivy, as written.
                        "package": {"name": "django", "version": "2.2.0", "ecosystem": "PyPI"},
                        "vulnerabilities": [
                            {
                                "id": "GHSA-6r97-cj55-9hrq",
                                "aliases": ["CVE-2019-14234"],
                                "summary": "SQL injection",
                                "affected": [
                                    {
                                        "package": {"name": "django"},
                                        "ranges": [
                                            {
                                                "type": "ECOSYSTEM",
                                                "events": [{"introduced": "0"}, {"fixed": "2.2.4"}],
                                            }
                                        ],
                                    }
                                ],
                            }
                        ],
                        "groups": [{"ids": ["GHSA-6r97-cj55-9hrq"], "max_severity": "9.8"}],
                    }
                ],
            }
        ]
    }
    (finding,) = osv.parse_report(data, ROOT)
    assert finding.rule_id == "CVE-2019-14234"
    assert finding.file == "requirements.txt"
    assert finding.severity is Severity.CRITICAL
    assert "2.2.4" in finding.recommendation

    trivy_like = trivy.parse_report(
        {
            "Results": [
                {
                    "Target": "requirements.txt",
                    "Vulnerabilities": [
                        {
                            "VulnerabilityID": "CVE-2019-14234",
                            "PkgName": "Django",
                            "InstalledVersion": "2.2.0",
                        }
                    ],
                }
            ]
        },
        frozenset({Module.DEP}),
    )
    assert trivy_like[0].fingerprint == finding.fingerprint


def test_opengrep_uses_own_metadata_and_filters_by_module(tmp_path: Path):
    (tmp_path / "settings.py").write_text('DEBUG = True\nSECRET_KEY = "abcdef123456"\n')
    data = {
        "results": [
            {
                "check_id": "rules.heimdall.django.DJ-SQL-001",
                "path": str(tmp_path / "views.py"),
                "start": {"line": 10},
                "end": {"line": 10},
                "extra": {
                    "message": "Dynamic SQL query.",
                    "severity": "WARNING",
                    "lines": '    cursor.execute(f"SELECT {x}")',
                    "metadata": {
                        "severity_hdl": "high",
                        "title": "Dynamic SQL",
                        "recommendation": "Parameterize.",
                        "cwe": ["CWE-89"],
                        "owasp": "A05:2025 Injection",
                    },
                },
            },
            {
                "check_id": "DJ-CONF-002",
                "path": str(tmp_path / "settings.py"),
                "start": {"line": 2},
                "end": {"line": 2},
                "extra": {"message": "SECRET_KEY literal.", "severity": "ERROR", "lines": ""},
            },
            {
                "check_id": "DJ-AUTH-001",
                "path": str(tmp_path / "views.py"),
                "start": {"line": 1},
                "end": {"line": 1},
                "extra": {"message": "Vista sin autenticación.", "severity": "ERROR"},
            },
        ]
    }
    modules = frozenset({Module.SAST, Module.CONF})
    sql, conf = opengrep.parse_report(data, tmp_path, modules)
    assert (sql.rule_id, sql.severity, sql.title) == ("DJ-SQL-001", Severity.HIGH, "Dynamic SQL")
    assert (sql.file, sql.cwe, sql.category) == ("views.py", "CWE-89", Category.SAST)
    assert conf.category is Category.CONFIGURATION
    # Without `lines` in the output, the snippet is read from the file and masked.
    assert conf.snippet.startswith("SECRET_KEY")
    assert "abcdef123456" not in conf.snippet

    assert [f.rule_id for f in opengrep.parse_report(data, tmp_path, frozenset({Module.CONF}))] == [
        "DJ-CONF-002"
    ]


def test_seed_rules_exist():
    names = {path.stem for path in opengrep.rules_dir().rglob("*.yaml")}
    assert {"DJ-SQL-001", "PHP-EXE-001", "NET-DES-001"} <= names


def test_bandit_runs_as_library_on_django_fixture(project, tmp_path: Path):
    root = project("django_app").resolve()
    exclusions = Exclusions()
    ctx = ScanContext(
        root=root,
        files=scan_tree(root, exclusions).analyzable,
        modules=frozenset({Module.SAST}),
        stacks=frozenset(),
        exclusions=exclusions,
        workdir=tmp_path,
    )
    adapter = BanditAdapter()
    assert adapter.is_available()
    assert adapter.version()
    result = adapter.invoke(ctx)
    findings = result.findings
    # Bandit quotes the password in its message: it must not reach the finding.
    assert "fixture-Sup3rS3creta" in result.secrets
    assert all("Sup3r" not in f.description + f.snippet for f in findings)
    shell = next(f for f in findings if f.rule_id == "B602")
    assert shell.file == "app/views.py"
    assert shell.severity is Severity.HIGH
    assert "shell=True" in shell.snippet
    assert all(not Path(f.file).is_absolute() for f in findings)
    assert shell.owasp == "A05:2025 Injection"
    assert all(f.owasp for f in findings if f.cwe)


def test_bandit_owasp_table_uses_valid_2025_categories_with_hints():
    from heimdall_guardian.adapters.bandit import OWASP_BY_CWE
    from heimdall_guardian.core import owasp

    labels = {category.label for category in owasp.CATEGORIES}
    assert set(OWASP_BY_CWE.values()) <= labels
    assert OWASP_BY_CWE[89] == "A05:2025 Injection"
    assert OWASP_BY_CWE[259] == "A07:2025 Authentication Failures"
    assert OWASP_BY_CWE[327] == "A04:2025 Cryptographic Failures"
    assert OWASP_BY_CWE[502] == "A08:2025 Software or Data Integrity Failures"
    assert OWASP_BY_CWE[22] == "A01:2025 Broken Access Control"
    # Every CWE Bandit can report has verification guidance.
    assert {f"CWE-{cwe}" for cwe in OWASP_BY_CWE} <= owasp.hinted_cwes()


def test_bundled_tools_are_extracted_once_into_the_data_dir(tmp_path: Path, monkeypatch):
    """Installed application: the binaries come from `_bundle/tools.tar.gz`."""
    import tarfile

    from heimdall_guardian.adapters import base

    bundle = tmp_path / "_bundle"
    bundle.mkdir()
    name = "gitleaks.exe" if sys.platform == "win32" else "gitleaks"
    tool = tmp_path / name
    tool.write_text("#!/bin/sh\necho 9.9.9\n")
    with tarfile.open(bundle / "tools.tar.gz", "w:gz") as archive:
        archive.add(tool, arcname=name)
    (bundle / "tools.key").write_text("abc123\n")
    data = tmp_path / "datos"
    monkeypatch.setenv("HDL_DATA_DIR", str(data))
    monkeypatch.setattr(base, "_BUNDLE", bundle)
    monkeypatch.setattr(base, "_REPO", tmp_path / "sin-repositorio")
    monkeypatch.delenv("HDL_GITLEAKS_BIN", raising=False)

    found = base.find_binary("gitleaks")
    assert found == str(data / "tools" / "abc123" / name)
    assert Path(found).stat().st_mode & 0o111  # executable
    Path(found).write_text("marca")  # a second call does not extract again
    assert base.find_binary("gitleaks") == found
    assert Path(found).read_text() == "marca"
    assert base.rules_dirs()[-1] == bundle / "rules"


def test_bandit_applies_only_with_python_files(tmp_path: Path):
    def ctx(files: list[str]) -> ScanContext:
        return ScanContext(
            root=tmp_path,
            files=files,
            modules=frozenset({Module.SAST}),
            stacks=frozenset(),
            exclusions=Exclusions(),
            workdir=tmp_path,
        )

    assert not BanditAdapter().applies(ctx(["index.php", "app.cs"]))
    assert BanditAdapter().applies(ctx(["index.php", "app.py"]))
