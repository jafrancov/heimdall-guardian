"""G3a: candidate rules (tag CAND) are handed to the AI and never reported on their own."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from helpers import FakeAdapter, make_finding

from heimdall_guardian.adapters.base import AdapterResult
from heimdall_guardian.adapters.opengrep import (
    classify,
    is_candidate,
    parse_report,
    split_candidates,
)
from heimdall_guardian.core.config import LlmConfig
from heimdall_guardian.core.finding import Category, Finding, Origin, Severity
from heimdall_guardian.core.profiles import Module
from heimdall_guardian.core.runner import build_plan, run_scan
from heimdall_guardian.llm.module import AiOutcome, AiRunner


def _item(rule: str, line: int, kind: str | None) -> dict[str, Any]:
    metadata: dict[str, Any] = {"cwe": "CWE-89", "confidence": "low", "severity_hdl": "medium"}
    if kind:
        metadata["candidate_kind"] = kind
    return {
        "check_id": f"rules.heimdall.php.{rule}",
        "path": "/proj/app/db.php",
        "start": {"line": line},
        "end": {"line": line},
        "extra": {"lines": f"query($x . {line});", "message": "m", "severity": "INFO",
                  "metadata": metadata},
    }  # fmt: skip


def test_candidate_tag_is_recognized_and_stays_in_sast():
    assert is_candidate("PHP-CAND-001")
    assert not is_candidate("PHP-SQL-001")
    assert not is_candidate("CAND")
    assert classify("NODE-CAND-003") == (Category.SAST, Module.SAST)


def test_candidates_are_separated_from_findings():
    report = {"results": [_item("PHP-CAND-001", 4, "sql"), _item("PHP-SQL-001", 9, None)]}
    parsed = parse_report(report, Path("/proj"), frozenset({Module.SAST}))
    findings, candidates = split_candidates(parsed)
    assert [f.rule_id for f in findings] == ["PHP-SQL-001"]
    assert [c.rule_id for c in candidates] == ["PHP-CAND-001"]
    assert candidates[0].candidate_kind == "sql"
    assert findings[0].candidate_kind == ""


def test_candidate_kind_is_not_stored_with_normal_findings():
    plain = make_finding("opengrep", "PHP-SQL-001", "a.php", "q", Severity.HIGH)
    assert "candidate_kind" not in plain.to_dict()
    kept = make_finding("opengrep", "PHP-CAND-001", "a.php", "q", Severity.MEDIUM)
    kept.candidate_kind = "sql"
    assert Finding.from_dict(kept.to_dict()).candidate_kind == "sql"


class _SpyAi(AiRunner):
    """AI module that only records the candidates it is given."""

    def __init__(self) -> None:
        super().__init__(LlmConfig())
        self.seen: list[Finding] | None = None
        self.outcome = AiOutcome()
        self.outcome.status = "ran"

    def run(self, findings, endpoints, root, secrets, candidates=None, files=None) -> AiOutcome:  # type: ignore[no-untyped-def]
        self.seen = candidates
        return self.outcome

    def summarize(self, stats) -> None:  # type: ignore[no-untyped-def]
        return None


def _candidate(file: str, line: int, snippet: str) -> Finding:
    found = make_finding("opengrep", "PHP-CAND-001", file, snippet, Severity.MEDIUM)
    found.line_start = found.line_end = line
    found.candidate_kind = "sql"
    return found


def test_runner_drops_candidates_next_to_a_finding_and_keeps_the_rest(tmp_path: Path):
    (tmp_path / "app.php").write_text("<?php\n")
    reported = make_finding(
        "opengrep", "PHP-SQL-001", "app.php", "mysqli_query($c, $q)", Severity.HIGH
    )
    reported.line_start = reported.line_end = 20
    result_in = AdapterResult(
        findings=[reported],
        candidates=[
            _candidate("app.php", 22, "near"),  # within 3 lines of the finding
            _candidate("app.php", 40, "far"),
            _candidate("other.php", 20, "other file"),
            _candidate("app.php", 40, "far"),  # duplicate fingerprint
            _candidate("node_modules/x.php", 1, "skipped"),
        ],
    )
    ai = _SpyAi()
    plan = build_plan(tmp_path, profile="full")
    result = run_scan(plan, adapters=[FakeAdapter("opengrep", result_in)], ai=ai)

    assert ai.seen is not None
    assert sorted(c.snippet for c in ai.seen) == ["far", "other file"]
    # Candidates are not findings: no summary, no IDs, no tool count.
    assert [f.rule_id for f in result.findings] == ["PHP-SQL-001"]
    assert all(f.origin is Origin.DETERMINISTIC for f in result.findings)
    assert sum(result.summary()["by_severity"].values()) == 1
    assert next(t for t in result.tools if t.name == "opengrep").findings == 1


def test_identical_candidate_lines_in_one_file_are_reviewed_separately(tmp_path: Path):
    (tmp_path / "app.php").write_text("<?php\n")
    same = "$rows = $db->query($sql);"
    result_in = AdapterResult(
        candidates=[_candidate("app.php", 10, same), _candidate("app.php", 30, same)]
    )
    ai = _SpyAi()
    run_scan(
        build_plan(tmp_path, profile="full"),
        adapters=[FakeAdapter("opengrep", result_in)],
        ai=ai,
    )
    assert ai.seen is not None
    assert [c.line_start for c in ai.seen] == [10, 30]


def test_candidates_do_not_change_the_summary_without_ai(tmp_path: Path):
    (tmp_path / "app.php").write_text("<?php\n")
    base = run_scan(
        build_plan(tmp_path, profile="standard"),
        adapters=[FakeAdapter("opengrep", AdapterResult())],
    )
    with_candidates = run_scan(
        build_plan(tmp_path, profile="standard"),
        adapters=[
            FakeAdapter("opengrep", AdapterResult(candidates=[_candidate("app.php", 3, "x")]))
        ],
    )
    assert with_candidates.findings == base.findings == []
    assert with_candidates.summary() == base.summary()
