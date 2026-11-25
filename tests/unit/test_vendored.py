"""Libraries copied into the project: recognition, set-aside of SAST findings, OSV mapping."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from helpers import FakeAdapter, make_finding

from heimdall_guardian import i18n
from heimdall_guardian.adapters import default_adapters
from heimdall_guardian.adapters.base import AdapterResult
from heimdall_guardian.adapters.vendored import VendoredAdapter, write_lockfiles
from heimdall_guardian.core.files import DEFAULT_EXCLUDED_DIRS, Exclusions
from heimdall_guardian.core.finding import Category, Severity
from heimdall_guardian.core.runner import build_plan, run_scan
from heimdall_guardian.core.vendored import LIBRARIES, VendoredLibrary, detect
from heimdall_guardian.storage import Store

# Synthetic files: a banner or a version constant written for these tests, never library code.
SAMPLES = {
    "js/jq.min.js": ("/*! jQuery v2.1.1 | synthetic banner */\nvar a=1;", "jquery", "2.1.1"),
    "js/jq-full.js": (
        "/*!\n * jQuery JavaScript Library v1.11.1\n * synthetic\n */\n",
        "jquery",
        "1.11.1",
    ),
    "js/ui.js": ("/*! jQuery UI - v1.10.4 - 2014-01-17 */\n", "jquery-ui", "1.10.4"),
    "js/dt.min.js": ("/*! DataTables 1.10.4\n * synthetic */\n", "datatables.net", "1.10.4"),
    "js/dt.js": (
        "/**\n * @summary     DataTables\n * @description synthetic\n"
        " * @version     1.10.12\n */\n",
        "datatables.net",
        "1.10.12",
    ),
    "js/hc.js": ("/*\n Highcharts JS v4.0.4 (2014-09-02)\n synthetic\n*/\n", "highcharts", "4.0.4"),
    "js/bs.js": ("/*!\n * Bootstrap v3.3.7 (https://example.test)\n */\n", "bootstrap", "3.3.7"),
    "js/bs-modal.js": ("/* ========\n * Bootstrap: modal.js v3.3.6\n */\n", "bootstrap", "3.3.6"),
    "js/moment.js": ("//! moment.js\n//! version : 2.10.3\n//! synthetic\n", "moment", "2.10.3"),
    "js/lodash.js": (
        "/**\n * @license\n * Lodash <https://lodash.example/>\n */\nvar VERSION = '4.17.4';\n",
        "lodash",
        "4.17.4",
    ),
    "fm/elfinder.min.js": (
        "/*!\n * elFinder - file manager for web\n * Version 2.1.57 (synthetic)\n */\n",
        "studio-42/elfinder",
        "2.1.57",
    ),
    "lib/class.phpmailer.php": (
        "<?php\nclass PHPMailer {\n  public $Version = '5.2.9';\n}\n",
        "phpmailer/phpmailer",
        "5.2.9",
    ),
    "lib/PHPMailer.php": (
        "<?php\nclass PHPMailer {\n  const VERSION = '6.5.0';\n}\n",
        "phpmailer/phpmailer",
        "6.5.0",
    ),
    "lib/PHPExcel.php": (
        "<?php\n/**\n * @version    1.8.0, 2014-03-02\n */\nclass PHPExcel {}\n",
        "phpoffice/phpexcel",
        "1.8.0",
    ),
    "lib/fpdf.php": (
        "<?php\ndefine('FPDF_VERSION','1.7');\nclass FPDF {}\n",
        "setasign/fpdf",
        "1.7",
    ),
    "lib2/fpdf.php": (
        "<?php\nclass FPDF {\n  const VERSION = '1.84';\n}\n",
        "setasign/fpdf",
        "1.84",
    ),
    "lib/tcpdf.php": (
        "<?php\nclass TCPDF {\n  private static $tcpdf_version = '6.2.13';\n}\n",
        "tecnickcom/tcpdf",
        "6.2.13",
    ),
    "lib/nusoap.php": (
        "<?php\nclass nusoap_base {\n  var $version = '0.9.5';\n}\n",
        "econea/nusoap",
        "0.9.5",
    ),
}


def _write(root: Path, files: dict[str, str]) -> None:
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


@pytest.mark.parametrize("name", sorted(SAMPLES))
def test_each_signature_recognizes_its_library(tmp_path: Path, name: str):
    text, package, version = SAMPLES[name]
    _write(tmp_path, {name: text})
    (lib,) = detect(tmp_path, [name])
    assert (lib.file, lib.package, lib.version) == (name, package, version)


def test_every_signature_is_covered_by_a_sample():
    covered = {package for _, package, _ in SAMPLES.values()}
    assert {sig.package for sig in LIBRARIES} <= covered


def test_jquery_ui_is_not_read_as_jquery(tmp_path: Path):
    _write(tmp_path, {"ui.js": "/*! jQuery UI - v1.10.4 */\n"})
    assert [lib.package for lib in detect(tmp_path, ["ui.js"])] == ["jquery-ui"]


def test_negatives_are_not_recognized(tmp_path: Path):
    files = {
        "a/migrate.js": "/*! jQuery Migrate v1.2.1 | synthetic */\n",
        "a/validation.js": "/*! jQuery Validation Plugin v1.19.0 */\n",
        "a/mention.js": "// uses jQuery, see their site\nvar x = 'jQuery';\n",
        "a/buttons.js": "/*! Buttons for DataTables 1.5.1 */\n",
        "a/tz.js": "//! moment-timezone.js\n//! version : 0.5.1\n",
        "a/other.js": "var VERSION = '4.17.4';\n",  # no Lodash marker
        "a/version.php": "<?php\nclass Thing { var $version = '1.2.3'; }\n",
        "a/nusoap.php": "<?php\nclass other { var $version = '0.9.5'; }\n",  # no marker
        "a/fpdf.php": "<?php\nclass Other { const VERSION = '1.84'; }\n",
    }
    _write(tmp_path, files)
    assert detect(tmp_path, sorted(files)) == ()


def test_detection_is_sorted_one_per_file_and_to_dict(tmp_path: Path):
    _write(tmp_path, {"z/jq.js": SAMPLES["js/jq.min.js"][0], "b/jq.js": SAMPLES["js/ui.js"][0]})
    libs = detect(tmp_path, ["z/jq.js", "b/jq.js"])
    assert [lib.file for lib in libs] == ["b/jq.js", "z/jq.js"]
    assert libs[0].to_dict() == {
        "file": "b/jq.js",
        "name": "jQuery UI",
        "ecosystem": "npm",
        "package": "jquery-ui",
        "version": "1.10.4",
    }


# ------------------------------------------------------------------ exclusions


def test_sast_files_only_skip_the_code_rules():
    exclusions = Exclusions(sast_files=("js/jq.js",))
    assert exclusions.excludes("js/jq.js", sast=True)
    assert not exclusions.excludes("js/jq.js")
    assert not exclusions.excludes("js/jq.js", secret=True)
    assert not exclusions.excludes("js/other.js", sast=True)


# ------------------------------------------------------------------ the scan


def _project(tmp_path: Path) -> Path:
    root = tmp_path / "app"
    _write(
        root,
        {
            "static/jquery-2.1.1.min.js": SAMPLES["js/jq.min.js"][0],
            "static/mine.js": "var x = 1;\n",
        },
    )
    return root


def test_plan_recognizes_libraries_and_sets_the_exclusion(tmp_path: Path):
    plan = build_plan(_project(tmp_path), profile="standard")
    assert [lib.file for lib in plan.vendored] == ["static/jquery-2.1.1.min.js"]
    assert plan.exclusions.sast_files == ("static/jquery-2.1.1.min.js",)
    assert plan.to_dict()["vendored"][0]["version"] == "2.1.1"


def test_libraries_in_skipped_folders_are_not_recognized(tmp_path: Path):
    root = tmp_path / "app"
    _write(root, {"vendor/jq.js": SAMPLES["js/jq.min.js"][0]})
    plan = build_plan(root, profile="standard", exclusions=Exclusions(dirs=DEFAULT_EXCLUDED_DIRS))
    assert plan.vendored == ()


def test_sast_findings_in_vendored_files_are_set_aside(tmp_path: Path):
    root = _project(tmp_path)
    lib = "static/jquery-2.1.1.min.js"
    findings = [
        make_finding("uno", "R-SAST", lib, "eval(x)", Severity.HIGH),
        make_finding("uno", "R-SAST", "static/mine.js", "eval(y)", Severity.HIGH),
        make_finding("uno", "R-SEC", lib, "tok", Severity.HIGH, category=Category.SECRETS),
        make_finding(
            "uno", "CVE-1", lib, "jquery@2.1.1", Severity.HIGH, category=Category.DEPENDENCIES
        ),
    ]
    plan = build_plan(root, profile="standard")
    result = run_scan(plan, adapters=[FakeAdapter("uno", AdapterResult(findings=findings))])
    kept = {(f.rule_id, f.file) for f in result.findings}
    assert kept == {("R-SAST", "static/mine.js"), ("R-SEC", lib), ("CVE-1", lib)}
    codes = [m["code"] for m in result.limitations if isinstance(m, dict)]
    assert "core.limit.vendored_sast" in codes
    assert "core.limit.dropped" not in codes
    (aside,) = [m for m in result.limitations if m["code"] == "core.limit.vendored_sast"]
    assert aside["params"]["count"] == 1
    assert lib in str(aside)


def test_found_limitation_lists_what_was_recognized(tmp_path: Path):
    plan = build_plan(_project(tmp_path), profile="standard")
    result = run_scan(plan, adapters=[])
    (found,) = [m for m in result.limitations if m["code"] == "core.limit.vendored_found"]
    assert found["params"]["count"] == 1
    i18n.set_language("en")
    assert "jQuery 2.1.1 (static/jquery-2.1.1.min.js)" in str(found)


def test_found_limitation_gives_up_to_five_examples(tmp_path: Path):
    root = tmp_path / "app"
    _write(root, {f"js/{n}/jq.js": SAMPLES["js/jq.min.js"][0] for n in range(7)})
    plan = build_plan(root, profile="standard")
    (found,) = [m for m in _limits(plan) if m["code"] == "core.limit.vendored_found"]
    assert found["params"]["count"] == 7
    assert len(found["params"]["examples"]["params"]["paths"]) == 5
    assert found["params"]["examples"]["code"] == "core.examples.many"


def _limits(plan):
    return run_scan(plan, adapters=[]).limitations


def test_no_libraries_no_limitations(tmp_path: Path):
    root = tmp_path / "app"
    _write(root, {"a.js": "var a = 1;\n"})
    codes = [m["code"] for m in _limits(build_plan(root, profile="standard"))]
    assert not any(code.startswith("core.limit.vendored") for code in codes)


def test_a_stored_sast_finding_in_a_now_vendored_file_is_omitted_not_fixed(tmp_path: Path):
    root = tmp_path / "app"
    lib = "static/jquery-2.1.1.min.js"
    _write(root, {lib: "var a = 1;\n"})  # not recognizable yet
    finding = make_finding("uno", "R-X", lib, "eval(x)", Severity.HIGH, module="SAST")
    with Store(root) as store:
        first = run_scan(
            build_plan(root, profile="standard"),
            adapters=[FakeAdapter("uno", AdapterResult(findings=[finding]))],
        )
        store.record(first)
    _write(root, {lib: SAMPLES["js/jq.min.js"][0]})  # now it has the banner
    with Store(root) as store:
        second = run_scan(
            build_plan(root, profile="standard"),
            adapters=[FakeAdapter("uno", AdapterResult())],
        )
        store.record(second)
        row = store._db.execute("SELECT open, fixed_run FROM findings").fetchone()
    assert second.fixed == []
    assert second.omitted_findings == 1
    assert (row["open"], row["fixed_run"]) == (1, None)


# ------------------------------------------------------------------ the adapter


def _libs(*items: tuple[str, str, str, str]) -> tuple[VendoredLibrary, ...]:
    return tuple(
        VendoredLibrary(file=f, name=f, ecosystem=eco, package=pkg, version=ver)
        for f, eco, pkg, ver in items
    )


def test_lockfiles_are_written_with_nested_unique_paths(tmp_path: Path):
    libs = _libs(
        ("a.js", "npm", "jquery", "2.1.1"),
        ("b.js", "npm", "jquery", "1.11.1"),
        ("c.js", "npm", "jquery", "2.1.1"),
        ("d.php", "Packagist", "phpmailer/phpmailer", "5.2.9"),
    )
    written = write_lockfiles(libs, tmp_path / "t")
    assert written == ["package-lock.json", "composer.lock"]
    npm = json.loads((tmp_path / "t" / "package-lock.json").read_text())
    assert npm["lockfileVersion"] == 3
    assert all(
        v["resolved"].endswith(f"{v['version']}.tgz") for k, v in npm["packages"].items() if k
    )
    assert {k: v["version"] for k, v in npm["packages"].items() if k} == {
        "node_modules/hdl-vendored-0/node_modules/jquery": "1.11.1",
        "node_modules/hdl-vendored-1/node_modules/jquery": "2.1.1",
    }
    composer = json.loads((tmp_path / "t" / "composer.lock").read_text())
    assert composer == {
        "packages": [{"name": "phpmailer/phpmailer", "version": "5.2.9"}],
        "packages-dev": [],
    }


def test_only_the_needed_lockfile_is_written(tmp_path: Path):
    assert write_lockfiles(_libs(("a.js", "npm", "jquery", "2.1.1")), tmp_path) == [
        "package-lock.json"
    ]
    assert not (tmp_path / "composer.lock").exists()


def _osv_report() -> dict:
    vuln = {
        "id": "GHSA-gxr4-xjj5-5px2",
        "aliases": ["CVE-2020-11022"],
        "summary": "Synthetic XSS",
        "affected": [
            {
                "package": {"name": "jquery"},
                "ranges": [
                    {"type": "ECOSYSTEM", "events": [{"introduced": "1.2.0"}, {"fixed": "3.5.0"}]}
                ],
            }
        ],
    }
    return {
        "results": [
            {
                "source": {"path": "/tmp/work/vendored/package-lock.json", "type": "lockfile"},
                "packages": [
                    {
                        "package": {"name": "jquery", "version": "2.1.1", "ecosystem": "npm"},
                        "vulnerabilities": [vuln],
                        "groups": [{"ids": ["GHSA-gxr4-xjj5-5px2"], "max_severity": "6.9"}],
                    },
                    {
                        "package": {"name": "jquery", "version": "9.9.9", "ecosystem": "npm"},
                        "vulnerabilities": [],
                    },
                ],
            }
        ]
    }


def test_osv_report_is_mapped_back_to_every_file_with_that_library(tmp_path: Path, monkeypatch):
    libs = _libs(
        ("static/a.js", "npm", "jquery", "2.1.1"),
        ("static/b.js", "npm", "jquery", "2.1.1"),
        ("static/c.js", "npm", "jquery", "1.11.1"),
    )
    adapter = VendoredAdapter()
    seen: list[Path] = []

    def fake_scan(ctx, target):
        seen.append(target)
        return _osv_report()

    monkeypatch.setattr(adapter, "_scan", fake_scan)
    ctx = _context(tmp_path, libs)
    result = adapter.invoke(ctx)
    assert seen == [ctx.workdir / "vendored"]
    assert (ctx.workdir / "vendored" / "package-lock.json").is_file()
    assert sorted(f.file for f in result.findings) == ["static/a.js", "static/b.js"]
    first = result.findings[0]
    assert first.source == "vendored"
    assert first.detected_by == ["vendored"]
    assert first.rule_id == "CVE-2020-11022"
    assert first.category is Category.DEPENDENCIES
    assert first.line_start == 0
    assert first.snippet == "jquery@2.1.1"
    assert first.fixed_version == "3.5.0"
    assert first.severity is Severity.MEDIUM
    assert "3.5.0" in first.texts["en"]["recommendation"]
    assert "Sustituye" in first.texts["es"]["recommendation"]
    assert len({f.fingerprint for f in result.findings}) == 2


def test_no_packages_gives_an_empty_result(tmp_path: Path, monkeypatch):
    adapter = VendoredAdapter()
    monkeypatch.setattr(adapter, "_scan", lambda ctx, target: None)
    ctx = _context(tmp_path, _libs(("a.js", "npm", "jquery", "2.1.1")))
    assert adapter.invoke(ctx).findings == []


def test_adapter_applies_only_with_dep_and_libraries(tmp_path: Path):
    from heimdall_guardian.core.profiles import Module

    libs = _libs(("a.js", "npm", "jquery", "2.1.1"))
    adapter = VendoredAdapter()
    assert adapter.applies(_context(tmp_path, libs))
    assert not adapter.applies(_context(tmp_path, ()))
    assert not adapter.applies(_context(tmp_path, libs, modules=frozenset({Module.SAST})))


def test_adapter_is_registered_after_osv():
    names = [a.name for a in default_adapters()]
    assert names.index("vendored") == names.index("osv") + 1


def _context(tmp_path: Path, libs, modules=None):
    from heimdall_guardian.adapters.base import ScanContext
    from heimdall_guardian.core.profiles import Module

    work = tmp_path / "work"
    work.mkdir(exist_ok=True)
    return ScanContext(
        root=tmp_path,
        files=[],
        modules=modules or frozenset({Module.DEP}),
        stacks=frozenset(),
        exclusions=Exclusions(),
        workdir=work,
        vendored=libs,
    )
