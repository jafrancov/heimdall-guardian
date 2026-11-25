"""File patterns in the exclusion lists: matching, protection and the plan."""

from pathlib import Path

from heimdall_guardian.core.config import ExclusionsConfig
from heimdall_guardian.core.files import Exclusions, is_file_pattern, is_protected, scan_tree
from heimdall_guardian.core.runner import _plan_limitations, build_plan
from heimdall_guardian.ui import model as m


def test_name_pattern_matches_file_name_only() -> None:
    ex = Exclusions(files=("*.spec.ts",))
    assert ex.excludes_file("src/a/foo.spec.ts")
    assert ex.excludes_file("foo.spec.ts")
    assert not ex.excludes_file("src/foo.ts")


def test_path_pattern_matches_whole_relative_path() -> None:
    ex = Exclusions(files=("docs/*.md",))
    assert ex.excludes_file("docs/a.md")
    assert not ex.excludes_file("src/docs/a.md")
    assert not ex.excludes_file("a.md")


def test_protected_files_are_never_excluded() -> None:
    ex = Exclusions(files=("*",))
    for name in ("package.json", "app/Foo.csproj", "requirements-dev.txt", "x/Cargo.LOCK"):
        assert is_protected(name)
        assert not ex.excludes_file(name)
        assert not ex.excludes(name)
    assert ex.excludes("src/main.py")


def test_secret_ignores_file_patterns_but_honors_folders() -> None:
    ex = Exclusions(dirs=("build",), files=("*.env",))
    assert ex.excludes("config/prod.env")
    assert not ex.excludes("config/prod.env", secret=True)
    assert ex.excludes("build/prod.env", secret=True)


def test_is_file_pattern() -> None:
    assert all(is_file_pattern(e) for e in ("*.ts", "a?", "[ab]"))
    assert not any(is_file_pattern(e) for e in ("build", "static/CACHE"))


def test_to_exclusions_splits_folders_and_files() -> None:
    cfg = ExclusionsConfig()
    ex = cfg.to_exclusions(("out", "*.spec.ts", "docs/*.md"), ("*.spec.ts",))
    assert {"out", "node_modules"} <= set(ex.dirs)
    assert not any(is_file_pattern(d) for d in ex.dirs)
    assert ex.files == ("docs/*.md",)
    assert cfg.to_exclusions(("*.log",)).files == ("*.log",)


def test_scan_tree_reports_pattern_skipped(tmp_path: Path) -> None:
    (tmp_path / "a.spec.ts").write_text("x")
    (tmp_path / "a.ts").write_text("x")
    (tmp_path / "package.json").write_text("{}")
    info = scan_tree(tmp_path, Exclusions(files=("*.spec.ts", "*.json")))
    assert info.pattern_skipped == ["a.spec.ts"]
    assert "a.spec.ts" in info.files
    assert "a.spec.ts" not in info.analyzable
    assert {"a.ts", "package.json"} <= set(info.analyzable)


def test_plan_lists_pattern_skipped(tmp_path: Path) -> None:
    (tmp_path / "a.spec.ts").write_text("x")
    (tmp_path / "a.ts").write_text("x")
    plan = build_plan(tmp_path, profile="quick", exclusions=Exclusions(files=("*.spec.ts",)))
    assert plan.tree.pattern_skipped == ["a.spec.ts"]
    assert "*.spec.ts" in plan.to_dict()["exclusions"]
    notes = [n for n in _plan_limitations(plan) if n["code"].startswith("core.limit.pattern")]
    assert notes[0]["params"]["count"] == 1


def test_parse_and_format_patterns() -> None:
    assert m.parse_patterns("*.spec.ts, docs/*.md\nbuild,, *.spec.ts") == ["*.spec.ts", "docs/*.md"]
    assert m.pattern_text(["build", "*.a", "x/*.b"]) == "*.a, x/*.b"
    assert m.parse_patterns("") == []
