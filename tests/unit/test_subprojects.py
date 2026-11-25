from __future__ import annotations

from pathlib import Path

from heimdall_guardian.core.subprojects import SubProject, find_subprojects


def make(root: Path, names: list[str]) -> list[str]:
    for name in names:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}")
    return names


def test_three_subprojects_sorted(tmp_path):
    files = make(
        tmp_path,
        [
            "api/package.json",
            "ios/Package.swift",
            "backend/package.json",
            "backend/tsconfig.json",
            "specs/a.yaml",
        ],
    )
    subs = find_subprojects(tmp_path, files)
    assert [s.path for s in subs] == ["api", "backend", "ios"]
    assert subs[0].stacks == ("node",)
    assert subs[1].stacks == ("node", "typescript")
    assert subs[2].stacks == ("swift",)


def test_root_manifest_means_one_project(tmp_path):
    files = make(tmp_path, ["package.json", "packages/a/package.json", "packages/b/package.json"])
    assert find_subprojects(tmp_path, files) == []


def test_single_subproject_is_not_listed(tmp_path):
    files = make(tmp_path, ["api/package.json", "docs/readme.md"])
    assert find_subprojects(tmp_path, files) == []


def test_only_top_most(tmp_path):
    files = make(tmp_path, ["apps/web/package.json", "apps/web/sub/package.json", "svc/go.mod"])
    subs = find_subprojects(tmp_path, files)
    assert [s.path for s in subs] == ["apps/web", "svc"]
    assert isinstance(subs[0], SubProject)


def test_depth_limit(tmp_path):
    files = make(tmp_path, ["a/b/c/d/package.json", "x/package.json"])
    assert find_subprojects(tmp_path, files, max_depth=3) == []
