from __future__ import annotations

from pathlib import Path

import pytest

from heimdall_guardian.core import severity
from heimdall_guardian.core.detector import Stack, detect
from heimdall_guardian.core.files import Exclusions, read_lines, scan_tree, tree_hash
from heimdall_guardian.core.finding import Severity
from heimdall_guardian.core.fingerprint import fingerprint
from heimdall_guardian.core.masking import mask_generic, mask_known, mask_secret
from heimdall_guardian.core.profiles import Module, parse_modules, resolve
from heimdall_guardian.i18n import render


def test_severity_mappings():
    assert severity.from_opengrep("ERROR") is Severity.HIGH
    assert severity.from_opengrep("WARNING") is Severity.MEDIUM
    assert severity.from_opengrep("INFO") is Severity.LOW
    assert severity.from_opengrep("INFO", "critical") is Severity.CRITICAL
    assert severity.from_opengrep("ERROR", "CRITICAL") is Severity.CRITICAL
    assert severity.from_opengrep("ERROR", "inventada") is Severity.HIGH
    assert [severity.from_cvss(s) for s in (9.0, 8.9, 7.0, 6.9, 4.0, 3.9)] == [
        Severity.CRITICAL,
        Severity.HIGH,
        Severity.HIGH,
        Severity.MEDIUM,
        Severity.MEDIUM,
        Severity.LOW,
    ]
    assert severity.from_bandit("HIGH", "HIGH") is Severity.HIGH
    assert severity.from_bandit("LOW", "LOW") is Severity.INFO
    assert severity.for_secret(in_current_code=True) is Severity.CRITICAL
    assert severity.for_secret(in_current_code=False) is Severity.HIGH


def test_fingerprint_ignores_whitespace_but_not_content():
    base = fingerprint("R1", "app/views.py", "x = 1")
    assert base == fingerprint("R1", "app/views.py", "   x   =   1\n")
    assert base == fingerprint("R1", "app\\views.py", "x = 1")
    assert base != fingerprint("R1", "app/views.py", "x = 2")
    assert base != fingerprint("R2", "app/views.py", "x = 1")
    assert base != fingerprint("R1", "app/otra.py", "x = 1")


def test_mask_secret():
    assert mask_secret("AKIAIOSFODNN7EXAMPLE") == "AKIA****MPLE"
    assert mask_secret("hunter2") == "****"


def test_mask_known_replaces_every_occurrence():
    text = "key=AKIAIOSFODNN7EXAMPLE; otra vez AKIAIOSFODNN7EXAMPLE"
    assert "AKIAIOSFODNN7EXAMPLE" not in mask_known(text, ["AKIAIOSFODNN7EXAMPLE", ""])


@pytest.mark.parametrize(
    ("text", "leaked"),
    [
        ('SECRET_KEY = "fixture-django-insecure-9x!k2m"', "insecure"),
        ("'PASSWORD': 'fixture-Sup3rS3creta',", "Sup3r"),
        ('$db_password = "clave1234";', "clave1234"),
        ("'api_key' => 'abcd1234efgh'", "abcd1234efgh"),
        ('"Default": "Server=db;User Id=sa;Password=fixture-Cl4ve;"', "Cl4ve"),
        ('"Default": "Password=fixture-Cl4ve;Server=db"', "Cl4ve"),
        ('connectionString="Data Source=db;User ID=sa;Pwd=fixture-Cl4ve" />', "Cl4ve"),
        ("APP_ENV=production\nDB_PASSWORD=fixture-Cl4ve\n", "Cl4ve"),
    ],
)
def test_mask_generic_hides_credentials(text: str, leaked: str):
    assert leaked not in mask_generic(text)


def test_mask_generic_keeps_ordinary_code():
    code = 'password = request.POST.get("password")\nnombre = "Ana"'
    assert mask_generic(code) == code


def test_exclusions():
    exclusions = Exclusions()
    assert exclusions.excludes("node_modules/x/index.js")
    assert exclusions.excludes("web/static/CACHE/a.js")
    assert not exclusions.excludes("web/static/app.js")
    assert exclusions.excludes(".git/config")
    assert not exclusions.excludes("app/tests/test_x.py")
    assert exclusions.excludes("app/tests/test_x.py", sast=True)
    # Only directories count, not a file with the same name.
    assert not exclusions.excludes("docs/vendor")


def test_scan_tree_skips_excluded_symlinks_and_oversized(tmp_path: Path):
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "a.py").write_text("x = 1\n")
    (tmp_path / "node_modules" / "lib").mkdir(parents=True)
    (tmp_path / "node_modules" / "lib" / "i.js").write_text("x")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("x")
    (tmp_path / "grande.bin").write_bytes(b"\x89PNG\0" * 600)  # binary
    outside = tmp_path.parent / "fuera.txt"
    outside.write_text("secreto ajeno")
    (tmp_path / "enlace.txt").symlink_to(outside)

    tree = scan_tree(tmp_path, Exclusions(max_file_kb=1))
    assert tree.files == ["app/a.py", "grande.bin"]
    assert tree.analyzable == ["app/a.py"]
    assert tree.symlinks == 1


def test_tree_hash_changes_with_content(tmp_path: Path):
    (tmp_path / "a.py").write_text("x = 1\n")
    first = tree_hash(tmp_path, ["a.py"])
    assert first == tree_hash(tmp_path, ["a.py"])
    (tmp_path / "a.py").write_text("x = 2\n")
    assert first != tree_hash(tmp_path, ["a.py"])


def test_read_lines_stays_inside_root(tmp_path: Path):
    root = tmp_path / "root"
    root.mkdir()
    (root / "a.txt").write_text("uno\ndos\ntres\n")
    (tmp_path / "fuera.txt").write_text("ajeno\n")
    assert read_lines(root, "a.txt", 2, 3) == "dos\ntres"
    assert read_lines(root, "../fuera.txt", 1, 1) == ""
    assert read_lines(root, "no-existe.txt", 1, 1) == ""


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("django_app", {Stack.PYTHON, Stack.DJANGO, Stack.DOCKER}),
        ("php_app", {Stack.PHP}),
        ("dotnet_app", {Stack.DOTNET}),
    ],
)
def test_detect_fixture_stacks(project, name: str, expected: set[Stack]):
    root = project(name)
    hits = detect(root, scan_tree(root, Exclusions()).files)
    assert {hit.stack for hit in hits} == expected


def test_detect_django_from_requirements_and_git(tmp_path: Path):
    (tmp_path / "requirements.txt").write_text("requests\nDjango>=4.2\n")
    (tmp_path / ".git").mkdir()
    stacks = {hit.stack for hit in detect(tmp_path, ["requirements.txt"])}
    assert stacks == {Stack.PYTHON, Stack.DJANGO, Stack.GIT}


def test_detect_does_not_confuse_django_plugins(tmp_path: Path):
    (tmp_path / "requirements.txt").write_text("django-environ==0.11\n")
    stacks = {hit.stack for hit in detect(tmp_path, ["requirements.txt"])}
    assert Stack.DJANGO not in stacks


def test_profiles():
    assert resolve("quick") == {Module.SEC, Module.DEP, Module.CONF}
    assert resolve("standard") == resolve("quick") | {Module.SAST, Module.AUTHZ}
    assert Module.SBOM in resolve("vendor")
    assert resolve("custom", parse_modules("sec, sec_h")) == {Module.SEC, Module.SEC_H}
    with pytest.raises(ValueError, match="personalizado"):
        resolve("custom")
    with pytest.raises(ValueError, match="desconocido"):
        resolve("inventado")
    with pytest.raises(ValueError, match="desconocido"):
        parse_modules("SEC,XYZ")


def test_large_code_is_analyzed_and_reported_but_large_data_is_skipped(tmp_path: Path):
    from heimdall_guardian.core.runner import build_plan, run_scan

    (tmp_path / "paquete.min.js").write_text("x" * 4000)
    (tmp_path / "datos.bin").write_bytes(b"\0\1\2" * 1500)  # binary
    (tmp_path / "estilos.css").write_text("a{}" * 1500)  # text without a code extension
    (tmp_path / "build" / "salida").mkdir(parents=True)
    (tmp_path / "build" / "salida" / "app.js").write_text("eval(x)")
    exclusions = Exclusions(max_file_kb=1)

    tree = scan_tree(tmp_path, exclusions)
    assert tree.files == ["datos.bin", "estilos.css", "paquete.min.js"]  # `build/` is skipped
    assert tree.analyzable == ["estilos.css", "paquete.min.js"]
    assert (tree.large_code, tree.oversized) == (["estilos.css", "paquete.min.js"], ["datos.bin"])

    plan = build_plan(tmp_path, profile="quick", exclusions=exclusions)
    text = " ".join(render(m) for m in run_scan(plan, adapters=[]).limitations)
    assert "2 archivo(s) de texto pesan más de 1 KB (p. ej. estilos.css, paquete.min.js)" in text
    assert "1 archivo(s) binarios de más de 1 KB no se analizaron" in text
    assert "datos.bin" in text


def test_default_exclusions_apply_even_with_a_config_saved_by_an_older_version(tmp_path: Path):
    from heimdall_guardian.core.config import load_config

    # A config.toml saved before `build` became a default exclusion.
    path = tmp_path / "config.toml"
    path.write_text('[exclusions]\npaths = ["node_modules", "venv"]\nexclude_extra = ["legado"]\n')
    exclusions = load_config(path).exclusions.to_exclusions()
    assert exclusions.excludes("build/flutter/app.js")
    assert exclusions.excludes("legado/a.py")
    assert not exclusions.excludes("src/a.py")
    # What a project asks for is added; and it can include a default folder again.
    project = load_config(path).exclusions.to_exclusions(("docs/viejo",), ("build",))
    assert project.excludes("docs/viejo/x.py")
    assert not project.excludes("build/flutter/app.js")


def test_list_folders_shows_excluded_ones_too(tmp_path: Path):
    from heimdall_guardian.core.files import list_folders

    for folder in ("src/app", "build/flutter/deep", "node_modules/x", ".git/objects"):
        (tmp_path / folder).mkdir(parents=True)
    assert list_folders(tmp_path) == [
        "build",
        "build/flutter",
        "node_modules",
        "node_modules/x",
        "src",
        "src/app",
    ]


def test_version_is_the_same_everywhere_and_logged():
    import tomllib

    from heimdall_guardian import __version__

    root = Path(__file__).resolve().parents[2]
    project = tomllib.loads((root / "pyproject.toml").read_text())["project"]["version"]
    assert __version__ == project
    # Each published version has its entry in the changelog.
    assert f"## [{project}]" in (root / "CHANGELOG.md").read_text()
