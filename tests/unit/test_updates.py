"""\"Novedades\" (what's new): compares installed and published versions, downloading nothing."""

from __future__ import annotations

import urllib.error

from heimdall_guardian import cli
from heimdall_guardian.adapters import updates

PUBLISHED = {
    "https://api.github.com/repos/gitleaks/gitleaks/releases/latest": {"tag_name": "v8.30.1"},
    "https://api.github.com/repos/aquasecurity/trivy/releases/latest": {"tag_name": "v0.80.0"},
    "https://pypi.org/pypi/bandit/json": {"info": {"version": "1.9.4"}},
}


def fake_fetch(url: str):
    if url not in PUBLISHED:
        raise urllib.error.URLError("sin red")
    return PUBLISHED[url]


def test_versions_compare_as_numbers_not_text():
    assert updates.parse_version("v0.80.0") > updates.parse_version("0.9.1")
    assert updates.parse_version("1.30.10") > updates.parse_version("1.30.9")
    assert updates.parse_version("2.6.0-rc1") == (2, 6, 0)


def test_novelties_report_each_tool_and_survive_failures():
    installed = {"gitleaks": "8.30.1", "trivy": "0.75.0", "osv": "2.6.0", "bandit": None}
    results = {item.tool: item for item in updates.check(installed, fake_fetch)}

    assert results["gitleaks"].status == "al día"
    assert results["trivy"].outdated
    assert results["trivy"].status == "hay una más nueva: 0.80.0"
    assert results["trivy"].page == "https://github.com/aquasecurity/trivy/releases"
    assert results["osv"].status == "no se pudo consultar (sin red)"  # the rest continue
    assert results["bandit"].status == "no instalada; la última es 1.9.4"
    assert "opengrep" not in results  # only the tools that are known


def test_cli_only_goes_online_when_asked(monkeypatch, capsys):
    calls: list[str] = []

    def spy(url: str):
        calls.append(url)
        return fake_fetch(url)

    monkeypatch.setattr(updates, "fetch_json", spy)
    monkeypatch.setattr(updates.check, "__defaults__", (spy,))
    assert cli.main(["tools"]) == 0
    assert calls == []
    assert cli.main(["tools", "--novedades"]) == 0
    assert calls
    assert "Versiones publicadas" in capsys.readouterr().out
