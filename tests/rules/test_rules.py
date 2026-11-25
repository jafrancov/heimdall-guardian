"""Each own rule is tested against its positive and negative fixtures."""

from __future__ import annotations

import os
import shutil
from collections import Counter
from pathlib import Path

import pytest
import yaml

from heimdall_guardian.adapters.base import ScanContext, find_binary
from heimdall_guardian.adapters.opengrep import OpengrepAdapter, rules_dir
from heimdall_guardian.core.files import Exclusions, scan_tree
from heimdall_guardian.core.profiles import Module
from heimdall_guardian.core.severity import parse_declared

FIXTURES = Path(__file__).parent / "fixtures"
# Exact findings each rule must give on its positive fixture: prevents a
# rule from still "passing" when it stops detecting one of its cases.
EXPECTED = yaml.safe_load((Path(__file__).parent / "expected.yaml").read_text(encoding="utf-8"))
REQUIRED_METADATA = ("cwe", "owasp", "severity_hdl", "confidence", "title", "recommendation")
SEVERITIES = {"critical", "high", "medium", "low", "info"}
CONFIDENCES = {"high", "medium", "low"}


def _load_rules() -> dict[str, dict]:
    rules = {}
    for path in sorted(rules_dir().rglob("*.yaml")):
        (rule,) = yaml.safe_load(path.read_text(encoding="utf-8"))["rules"]
        assert rule["id"] == path.stem, f"{path.name}: the file must be named after the rule"
        rules[rule["id"]] = rule
    return rules


RULES = _load_rules()


@pytest.mark.parametrize("rule_id", sorted(RULES))
def test_rule_has_complete_metadata(rule_id: str):
    rule = RULES[rule_id]
    metadata = rule.get("metadata", {})
    missing = [key for key in REQUIRED_METADATA if not metadata.get(key)]
    assert not missing, f"missing metadata: {missing}"
    assert metadata["severity_hdl"] in SEVERITIES
    assert parse_declared(metadata["severity_hdl"]) is not None
    assert metadata["confidence"] in CONFIDENCES
    assert rule.get("message", "").strip()


# English is the base language (`message`, `title`, `recommendation`); Spanish goes in
# `message_es`, `title_es` and `recommendation_es`.
SPANISH_METADATA = ("message_es", "title_es", "recommendation_es")


@pytest.mark.parametrize("rule_id", sorted(RULES))
def test_rule_has_spanish_texts(rule_id: str):
    metadata = RULES[rule_id].get("metadata", {})
    missing = [key for key in SPANISH_METADATA if not str(metadata.get(key) or "").strip()]
    assert not missing, f"missing Spanish texts: {missing}"
    assert not {"title_en", "recommendation_en", "message_en"} & set(metadata)


@pytest.mark.parametrize("rule_id", sorted(RULES))
def test_rule_has_both_fixtures(rule_id: str):
    for kind in ("positive", "negative"):
        folder = FIXTURES / rule_id / kind
        assert folder.is_dir(), f"missing fixture {kind}"
        assert any(folder.rglob("*")), f"the {kind} fixture is empty"


def test_no_orphan_fixtures():
    assert {path.name for path in FIXTURES.iterdir() if path.is_dir()} <= set(RULES)
    assert set(EXPECTED) == set(RULES)


@pytest.fixture(scope="session")
def matches(tmp_path_factory: pytest.TempPathFactory) -> Counter[tuple[str, str]]:
    """Run the engine once over all the fixtures: {(rule, kind): findings}."""
    # Opengrep is the official engine; Semgrep works as a substitute (same format).
    engine = find_binary("opengrep") or shutil.which("semgrep")
    if engine is None:
        if os.environ.get("HDL_REQUIRE_RULE_ENGINE"):
            pytest.fail("no hay motor de reglas (opengrep o semgrep) y se exige uno")
        pytest.skip("no hay motor de reglas instalado (opengrep o semgrep)")

    # A copy is analyzed: that way the path does not contain `tests/`, which the engine skips.
    root = tmp_path_factory.mktemp("reglas") / "casos"
    shutil.copytree(FIXTURES, root)
    _fill_fake_secrets(root)
    exclusions = Exclusions(dirs=())
    ctx = ScanContext(
        root=root,
        files=scan_tree(root, exclusions).files,
        modules=frozenset(Module),
        stacks=frozenset(),
        exclusions=exclusions,
        workdir=tmp_path_factory.mktemp("trabajo"),
    )
    previous = os.environ.get("HDL_OPENGREP_BIN")
    os.environ["HDL_OPENGREP_BIN"] = engine
    try:
        result = OpengrepAdapter().invoke(ctx)
    finally:
        if previous is None:
            del os.environ["HDL_OPENGREP_BIN"]
        else:
            os.environ["HDL_OPENGREP_BIN"] = previous
    assert not result.limitations, result.limitations

    counts: Counter[tuple[str, str]] = Counter()
    # Candidate rules never reach `findings`; their fixtures are counted the same way.
    for finding in [*result.findings, *result.candidates]:
        folder, kind = Path(finding.file).parts[:2]
        # Only the rule that owns the fixture counts; others may match incidentally.
        if folder == finding.rule_id:
            counts[(finding.rule_id, kind)] += 1
    return counts


@pytest.mark.parametrize("rule_id", sorted(RULES))
def test_rule_detects_positive_fixture(rule_id: str, matches: Counter[tuple[str, str]]):
    assert matches[(rule_id, "positive")] == EXPECTED[rule_id]


@pytest.mark.parametrize("rule_id", sorted(RULES))
def test_rule_ignores_negative_fixture(rule_id: str, matches: Counter[tuple[str, str]]):
    assert matches[(rule_id, "negative")] == 0


# Provider-shaped fake secrets are not stored in the repository (hosting services block
# pushes that contain them): the fixtures carry placeholders, filled in the copy.
FAKE_SECRETS = {
    "@@FAKE_STRIPE_KEY_A@@": "sk_" + "live_" + "4eC39HqLyjWDarjtT1zdp7dc",
    "@@FAKE_STRIPE_KEY_B@@": "sk_" + "live_" + "51HxYzAbCdEfGhIjKlMnOp",
    "@@FAKE_GITHUB_TOKEN@@": "ghp" + "_" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    "@@FAKE_GOOGLE_KEY_A@@": "AI" + "za" + "SyD4mKq9xZpL3vN8tR2wY6uB1cE5fH7jA0s",
    "@@FAKE_GOOGLE_KEY_B@@": "AI" + "za" + "SyD4e8Kq3vP0mZxN7wQ2rT5uY1oL9bC6hJs",
}


def _fill_fake_secrets(root: Path) -> None:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "@@FAKE_" not in text:
            continue
        for placeholder, value in FAKE_SECRETS.items():
            text = text.replace(placeholder, value)
        path.write_text(text, encoding="utf-8")
