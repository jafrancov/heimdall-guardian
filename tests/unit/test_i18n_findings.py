"""Findings with text in each language, stable fingerprints and bilingual AI (subphase I4-A)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from helpers import FakeAdapter

from heimdall_guardian import cli, i18n
from heimdall_guardian.adapters import gitleaks, opengrep, osv, trivy
from heimdall_guardian.adapters.base import AdapterResult
from heimdall_guardian.authz.adapter import AuthzAdapter
from heimdall_guardian.core.config import LlmConfig, LlmDestination
from heimdall_guardian.core.finding import (
    BaselineStatus,
    Category,
    Confidence,
    Finding,
    Severity,
)
from heimdall_guardian.core.profiles import Module
from heimdall_guardian.core.runner import build_plan, run_scan
from heimdall_guardian.i18n import render, text_of
from heimdall_guardian.llm import prompts
from heimdall_guardian.llm.client import ChatReply
from heimdall_guardian.llm.context import EndpointContext
from heimdall_guardian.llm.module import AiRunner
from heimdall_guardian.llm.schemas import Level, Risk, Verdict
from heimdall_guardian.report import write_report
from heimdall_guardian.storage import Store

ROOT = Path("/proyecto")


@pytest.fixture(autouse=True)
def _reset_language():
    i18n.set_override(None)
    yield
    i18n.set_override(None)
    i18n.set_language("es")


# ------------------------------------------------------------------ rules


def _rule_item(tmp_path: Path, **metadata: str) -> dict:
    return {
        "check_id": "rules.heimdall.django.DJ-SQL-001",
        "path": str(tmp_path / "views.py"),
        "start": {"line": 3},
        "end": {"line": 3},
        "extra": {
            "message": "Dynamic SQL query.",
            "severity": "WARNING",
            "lines": "cursor.execute(q)",
            "metadata": {
                "severity_hdl": "high",
                "title": "Dynamic SQL",
                "recommendation": "Parameterize.",
                **metadata,
            },
        },
    }


def test_rule_finding_reads_in_both_languages(tmp_path: Path):
    item = _rule_item(
        tmp_path,
        title_es="SQL dinámico",
        recommendation_es="Parametrizar.",
        message_es="Consulta SQL dinámica.",
    )
    (finding,) = opengrep.parse_report({"results": [item]}, tmp_path, frozenset({Module.SAST}))
    assert text_of(finding, "title", "es") == "SQL dinámico"
    assert text_of(finding, "title", "en") == "Dynamic SQL"
    assert text_of(finding, "description", "es") == "Consulta SQL dinámica."
    assert text_of(finding, "description", "en") == "Dynamic SQL query."
    assert text_of(finding, "recommendation", "es") == "Parametrizar."
    assert text_of(finding, "recommendation", "en") == "Parameterize."
    # The flat field stores English, which is the fallback for any other language.
    assert (finding.title, finding.recommendation) == ("Dynamic SQL", "Parameterize.")
    i18n.set_language("en")
    assert text_of(finding, "title") == "Dynamic SQL"
    assert text_of(finding.to_dict(), "title", "xx") == "Dynamic SQL"  # language without texts


def test_rule_without_spanish_text_falls_back_to_english(tmp_path: Path):
    (finding,) = opengrep.parse_report(
        {"results": [_rule_item(tmp_path)]}, tmp_path, frozenset({Module.SAST})
    )
    assert text_of(finding, "title", "es") == "Dynamic SQL"
    assert text_of(finding, "description", "es") == "Dynamic SQL query."
    assert text_of(finding, "recommendation", "es") == "Parameterize."
    (bare,) = opengrep.parse_report(
        {"results": [_rule_item(tmp_path, recommendation="")]},
        tmp_path,
        frozenset({Module.SAST}),
    )
    assert "Review and fix" in text_of(bare, "recommendation", "en")


def test_fingerprint_depends_on_rule_path_and_snippet_not_on_language(tmp_path: Path):
    item = _rule_item(tmp_path, title_es="SQL dinámico", message_es="x", recommendation_es="y")
    modules = frozenset({Module.SAST})
    i18n.set_language("es")
    (spanish,) = opengrep.parse_report({"results": [item]}, tmp_path, modules)
    i18n.set_language("en")
    (english,) = opengrep.parse_report({"results": [item]}, tmp_path, modules)
    assert spanish.fingerprint == english.fingerprint
    other = _rule_item(tmp_path, title_es="Otro título", title="Another title")
    (changed,) = opengrep.parse_report({"results": [other]}, tmp_path, modules)
    assert changed.fingerprint == spanish.fingerprint  # the title is not part of the fingerprint


# ------------------------------------------------------ adapters with fixed text


def test_fixed_texts_of_tool_adapters_come_in_both_languages():
    leak = {
        "RuleID": "aws-access-token",
        "Description": "AWS credentials",
        "File": "/proyecto/a.py",
        "StartLine": 1,
        "EndLine": 1,
        "Match": 'K = "AKIAIOSFODNN7EXAMPLE"',
        "Secret": "AKIAIOSFODNN7EXAMPLE",
    }
    (finding,), _ = gitleaks.parse_report([leak], ROOT, history=False)
    assert text_of(finding, "title", "en") == "Secret in the code: aws-access-token"
    assert text_of(finding, "title", "es") == "Secreto en el código: aws-access-token"
    assert "Detector: AWS credentials." in text_of(finding, "description", "en")
    assert text_of(finding, "recommendation", "en").startswith("Revoke and rotate")
    assert text_of(finding, "recommendation", "es").startswith("Revocar y rotar")

    data = {
        "Results": [
            {
                "Target": "requirements.txt",
                "Vulnerabilities": [
                    {
                        "VulnerabilityID": "CVE-1",
                        "PkgName": "Django",
                        "InstalledVersion": "2.2.0",
                        "FixedVersion": "2.2.4",
                        "Severity": "HIGH",
                        "Title": "SQL injection in JSONField",
                    }
                ],
                "Misconfigurations": [
                    {
                        "ID": "DS002",
                        "Title": "Image user should not be 'root'",
                        "Status": "FAIL",
                        "Severity": "HIGH",
                    }
                ],
            }
        ]
    }
    dependency, misconfiguration = trivy.parse_report(data, frozenset({Module.DEP, Module.CONF}))
    assert text_of(dependency, "title", "en") == "Django 2.2.0 has a known vulnerability (CVE-1)"
    assert (
        text_of(dependency, "title", "es")
        == "Django 2.2.0 tiene una vulnerabilidad conocida (CVE-1)"
    )
    # The description quotes the tool's text as is.
    assert text_of(dependency, "description", "es").endswith("SQL injection in JSONField")
    assert (
        text_of(dependency, "recommendation", "es")
        == "Actualizar Django a la versión 2.2.4 o posterior."
    )
    assert text_of(dependency, "recommendation", "en") == "Update Django to version 2.2.4 or later."
    # What the tool writes comes out the same in any language.
    assert text_of(misconfiguration, "title", "es") == "Image user should not be 'root'"
    assert "configuración" in text_of(misconfiguration, "recommendation", "es")
    assert "configuration" in text_of(misconfiguration, "recommendation", "en")

    osv_data = {
        "results": [
            {
                "source": {"path": "/proyecto/requirements.txt"},
                "packages": [
                    {
                        "package": {"name": "x", "version": "1"},
                        "vulnerabilities": [{"id": "GHSA-1", "summary": "Bad"}],
                    }
                ],
            }
        ]
    }
    (unpatched,) = osv.parse_report(osv_data, ROOT)
    assert text_of(unpatched, "recommendation", "en").startswith("No fixed version")
    assert text_of(unpatched, "recommendation", "es").startswith("Aún no hay versión")


# ------------------------------------------------------------------- AUTHZ


def _authz_scan(root: Path):
    return run_scan(build_plan(root, profile="standard"), adapters=[AuthzAdapter()])


def test_authz_findings_and_evidence_read_in_both_languages(project):
    result = _authz_scan(project("authz_django"))
    finding = next(f for f in result.findings if f.rule_id == "AUTHZ-001")
    assert text_of(finding, "title", "en").startswith("write endpoint without authentication: ")
    assert text_of(finding, "title", "es").startswith("Endpoint de escritura sin autenticación: ")
    assert "does not require authentication:" in text_of(finding, "description", "en")
    assert "no exige autenticación:" in text_of(finding, "description", "es")
    assert text_of(finding, "recommendation", "en").startswith("Require authentication")
    assert text_of(finding, "recommendation", "es").startswith("Exigir autenticación")
    # The inventory evidence is a stored message, not already translated text.
    assert all(
        i18n.is_message(e["evidence"]) or isinstance(e["evidence"], str) for e in result.endpoints
    )
    evidences = {render(e["evidence"], "en") for e in result.endpoints}
    assert "no authentication decorator" in evidences
    assert "sin decorador de autenticación" in {
        render(e["evidence"], "es") for e in result.endpoints
    }


def test_scanning_in_another_language_keeps_every_fingerprint_and_the_baseline(project):
    root = project("authz_django")
    i18n.set_language("en")
    first = _authz_scan(root)
    with Store(root) as store:
        store.record(first)
    i18n.set_language("es")
    second = _authz_scan(root)
    with Store(root) as store:
        store.record(second)
    assert first.findings
    assert [f.fingerprint for f in first.findings] == [f.fingerprint for f in second.findings]
    assert [f.id for f in first.findings] == [f.id for f in second.findings]
    assert {f.baseline_status for f in second.findings} == {BaselineStatus.PERSISTENT}
    # The title is shown in the current language, not in that of the first run.
    assert all("Endpoint de" in text_of(f, "title") for f in second.findings)


def test_cli_reports_the_findings_in_the_chosen_language(project, tmp_path: Path):
    root = project("django_app")
    html_en, html_es = tmp_path / "en.html", tmp_path / "es.html"
    for lang, target in (("en", html_en), ("es", html_es)):
        code = cli.main(
            ["--lang", lang, "scan", str(root), "--profile", "quick", "--output", str(target)]
        )
        assert code == 0
    english = html_en.read_text(encoding="utf-8")
    spanish = html_es.read_text(encoding="utf-8")
    assert "Hardcoded" in english or "Secret in the code" in english
    assert "Secreto en el código" in spanish
    assert "Secret in the code" not in spanish


def test_json_report_keeps_both_languages_and_every_format_follows_the_language(project, tmp_path):
    result = _authz_scan(project("authz_django"))
    payload = result.to_dict()
    texts = payload["findings"][0]["texts"]
    assert set(texts) == {"en", "es"}
    assert set(texts["en"]) == {"title", "description", "recommendation"}
    outputs = {}
    for lang in ("en", "es"):
        i18n.set_language(lang)
        for extension in ("html", "xlsx", "sarif", "pdf"):
            target = tmp_path / f"{lang}.{extension}"
            write_report(payload, target)
            outputs[lang, extension] = target
    assert "without authentication" in outputs["en", "html"].read_text(encoding="utf-8")
    assert "sin autenticación" in outputs["es", "html"].read_text(encoding="utf-8")
    sarif_en = json.loads(outputs["en", "sarif"].read_text(encoding="utf-8"))
    sarif_es = json.loads(outputs["es", "sarif"].read_text(encoding="utf-8"))
    assert "without authentication" in sarif_en["runs"][0]["results"][0]["message"]["text"]
    assert "sin autenticación" in sarif_es["runs"][0]["results"][0]["message"]["text"]
    for target in outputs.values():
        assert target.stat().st_size > 0


# ---------------------------------------------------------------- prompts (AI)

_CODE = '10: cursor.execute(f"SELECT {x}")'
_FINDING = {
    "rule_id": "DJ-SQL-001",
    "title": "Dynamic SQL",
    "description": "Dynamic SQL query.",
    "file": "a.py",
    "line_start": 10,
    "texts": {
        "en": {"title": "Dynamic SQL", "description": "Dynamic SQL query."},
        "es": {"title": "SQL dinámico", "description": "Consulta SQL dinámica."},
    },
}
_ENDPOINT = {
    "path": "/x",
    "methods": ["*"],
    "handler": "h",
    "file": "a.py",
    "has_auth": False,
    "evidence": i18n.msg("authz.ev.django_no_decorator"),
}


@pytest.mark.parametrize("lang", ["en", "es"])
def test_prompts_keep_the_injection_guard_the_marks_and_the_json_schema(lang: str):
    for system in (prompts.system_triage(lang), prompts.system_endpoint(lang)):
        assert ("DATA to analyze" if lang == "en" else "DATO a analizar") in system
        assert (
            "ONLY with a valid JSON" if lang == "en" else "ÚNICAMENTE con un objeto JSON"
        ) in system
        assert "{guard}" not in system
    assert "likely_real" in prompts.system_triage(lang)
    assert "uncertain" in prompts.system_triage(lang)
    assert '"idor_risk"' in prompts.system_endpoint(lang)
    assert '{"summary": "..."}' in prompts.system_summary(lang)
    assert ("English" if lang == "en" else "español") in prompts.system_triage(lang)

    user = prompts.triage(_FINDING, _CODE, 10, lang)
    assert "<<<DATO-" in user
    assert _CODE in user
    assert ("Dynamic SQL" if lang == "en" else "SQL dinámico") in user
    endpoint = prompts.endpoint(_ENDPOINT, EndpointContext("a.py", 10, _CODE, True), lang)
    assert "<<<DATO-" in endpoint
    assert ("no authentication decorator" if lang == "en" else "sin decorador") in endpoint
    assert prompts.summary({"a": 1}, lang).endswith("- a: 1")


def test_prompt_language_follows_the_current_language_and_the_codes_are_neutral():
    i18n.set_language("en")
    assert prompts.system_triage() == prompts.system_triage("en")
    i18n.set_language("es")
    assert prompts.system_triage() == prompts.system_triage("es")
    assert prompts.system_triage("en") != prompts.system_triage("es")
    assert {v.value for v in Verdict} == {"likely_real", "likely_false", "uncertain"}
    assert {v.value for v in Level} == {"high", "medium", "low"}
    assert {v.value for v in Risk} == {"high", "medium", "low", "none"}
    for kind in ("ui.ai.verdict", "report.ai.verdict"):
        for code in Verdict:
            assert i18n.has_message(f"{kind}.{code.value}")


class _Client:
    def __init__(self) -> None:
        self.destination = LlmDestination(
            name="x", url="http://localhost:1/v1", model_triage="m", model_summary="m"
        )
        self.calls: list[tuple[str, str]] = []

    def models(self) -> list[str]:
        return ["m"]

    def chat(self, model, system, user, schema=None, max_tokens=700) -> ChatReply:
        self.calls.append((system, user))
        if "JSON object: {" in system or '{"summary"' in system:
            return ChatReply(json.dumps({"summary": "Resumen."}), 5, 0.1)
        return ChatReply(
            json.dumps(
                {
                    "verdict": "likely_real",
                    "explanation": "x",
                    "suggested_fix": "",
                    "confidence": "high",
                }
            ),
            5,
            0.1,
        )


def _ai_scan(root: Path, client: _Client, cache: Path, lang: str):
    i18n.set_language(lang)
    finding = Finding(
        fingerprint="f",
        source="uno",
        rule_id="DJ-SQL-001",
        category=Category.SAST,
        severity=Severity.HIGH,
        confidence=Confidence.MEDIUM,
        file="app/views.py",
        line_start=10,
        line_end=10,
        snippet="cursor.execute(f...)",
        module="SAST",
        texts=i18n.texts_of(title=i18n.msg("adapter.dependency.rec_no_fix")),
    )
    ai = AiRunner(LlmConfig(), clients=[client], cache_dir=cache)  # type: ignore[list-item]
    result = run_scan(
        build_plan(root, profile="full"),
        adapters=[FakeAdapter("uno", AdapterResult(findings=[finding]))],
        ai=ai,
    )
    return result, ai


def test_ai_cache_is_separate_per_language_and_the_summary_records_its_language(project, tmp_path):
    root = project("django_app")
    client = _Client()
    cache = tmp_path / "cache"
    first, ai_es = _ai_scan(root, client, cache, "es")
    assert (ai_es.outcome.asked, ai_es.outcome.cached) == (2, 0)
    assert first.ai_summary
    assert first.ai_summary["language"] == "es"
    assert first.findings[0].llm_assessment["language"] == "es"
    assert "español" in client.calls[0][0]

    _, again = _ai_scan(root, client, cache, "es")
    assert (again.outcome.asked, again.outcome.cached) == (0, 2)  # same cache

    second, ai_en = _ai_scan(root, client, cache, "en")
    assert (ai_en.outcome.asked, ai_en.outcome.cached) == (2, 0)  # another language: another query
    assert second.ai_summary
    assert second.ai_summary["language"] == "en"
    assert "English" in client.calls[-1][0] or "English" in client.calls[-2][0]
    stats_line = client.calls[-1][1]
    assert "Analysis figures:" in stats_line
    assert "Findings of severity HIGH" in stats_line
