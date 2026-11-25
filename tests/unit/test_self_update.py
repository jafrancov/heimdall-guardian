"""Heimdall's own update check (`hdl version --check`, About panel) and the changelog extractor."""

from __future__ import annotations

import importlib.util
import io
import urllib.error
from pathlib import Path

import pytest

from heimdall_guardian import cli
from heimdall_guardian.adapters import updates
from heimdall_guardian.ui import model

ROOT = Path(__file__).resolve().parents[2]
API = "https://api.github.com/repos/jafrancov/heimdall-guardian/releases/latest"


def release(tag: str):
    def fetch(url: str):
        assert url == API  # only the releases of the project's own repository
        return {"tag_name": tag}

    return fetch


def http_error(code: int) -> urllib.error.HTTPError:
    return urllib.error.HTTPError(API, code, "x", {}, io.BytesIO(b""))  # type: ignore[arg-type]


def failing(exc: Exception):
    def fetch(url: str):
        raise exc

    return fetch


def test_repository_comes_from_the_metadata_with_a_fallback():
    assert updates.repository_slug() == "jafrancov/heimdall-guardian"
    urls = ["Homepage, https://x.example/", "Repository, https://github.com/acme/tool.git"]
    assert updates.repository_slug(urls) == "acme/tool"
    assert updates.repository_slug([]) == "jafrancov/heimdall-guardian"


@pytest.mark.parametrize(
    ("tag", "installed", "state"),
    [
        ("v1.2.0", "1.1.0", "newer"),
        ("1.2.0", "1.2.0", "current"),  # a tag without the «v»
        ("v1.2.0", "1.2.0", "current"),
        ("v1.0.0", "1.2.0", "ahead"),
        ("nightly", "1.2.0", "no_release"),  # malformed tag: nothing to compare
        ("", "1.2.0", "no_release"),
    ],
)
def test_comparison_with_the_latest_release(tag, installed, state):
    result = updates.check_self(release(tag), installed)
    assert result.state == state
    assert result.outdated == (state == "newer")
    assert result.status


def test_newer_release_points_to_its_page():
    result = updates.check_self(release("v9.9.9"), "0.1.0")
    assert result.latest == "9.9.9"
    assert result.page == "https://github.com/jafrancov/heimdall-guardian/releases/latest"


def test_no_release_yet_is_neutral():
    exc = http_error(404)
    result = updates.check_self(failing(exc), "0.1.0")
    assert result.state == "no_release"
    assert result.error == ""


def test_network_errors_never_raise():
    for exc in (
        urllib.error.URLError("no network"),
        http_error(403),
        TimeoutError("timed out"),
        ValueError("not json"),
    ):
        result = updates.check_self(failing(exc), "0.1.0")
        assert result.state == "error"
        assert not result.outdated
        assert result.error


def test_non_object_answer_is_an_error_not_a_crash():
    result = updates.check_self(lambda url: ["unexpected"], "0.1.0")
    assert result.state == "error"


def test_about_panel_line_and_link():
    newer = model.about_update(updates.check_self(release("v9.9.9"), "0.1.0"))
    assert "0.1.0" in newer[0]
    assert newer[1] is not None
    assert newer[1].startswith("https://github.com/")
    assert model.about_update(updates.check_self(release("v0.1.0"), "0.1.0"))[1] is None


def test_version_command(monkeypatch, capsys):
    monkeypatch.setattr(updates, "fetch_json", release("v9.9.9"))
    assert cli.main(["--lang", "en", "version"]) == 0
    plain = capsys.readouterr().out
    assert plain.startswith("hdl ")
    assert "Latest release" not in plain

    assert cli.main(["--lang", "en", "version", "--check"]) == 0
    out = capsys.readouterr().out
    assert "Latest release: 9.9.9" in out
    assert "Release page: https://github.com/jafrancov/heimdall-guardian/releases/latest" in out
    assert "install_hdl.py" not in out  # not running from the installer's venv


def test_version_check_offers_the_update_command_inside_the_installer_venv(monkeypatch, capsys):
    monkeypatch.setattr(cli, "_installed_by_script", lambda: True)
    monkeypatch.setattr(updates, "fetch_json", release("v9.9.9"))
    cli.main(["--lang", "en", "version", "--check"])
    out = capsys.readouterr().out
    assert "python3 install_hdl.py --wheel heimdall_guardian-9.9.9-py3-none-any.whl" in out


def test_version_check_offline_is_a_neutral_message(monkeypatch, capsys):
    monkeypatch.setattr(updates, "fetch_json", failing(urllib.error.URLError("no network")))
    assert cli.main(["--lang", "en", "version", "--check"]) == 0
    assert "could not check (no network)" in capsys.readouterr().out


def _changelog_module():
    spec = importlib.util.spec_from_file_location(
        "changelog_section", ROOT / "tools" / "changelog_section.py"
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SAMPLE = """# Changelog

## [Unreleased]

## [0.2.0] - 2026-02-01

### Added
- Two.

## [0.1.0] - 2026-01-01

### Added
- One.

[0.2.0]: https://example.invalid/0.2.0
"""


def test_changelog_section_extraction():
    module = _changelog_module()
    assert module.section(SAMPLE, "0.2.0") == "## [0.2.0] - 2026-02-01\n\n### Added\n- Two.\n"
    last = module.section(SAMPLE, "v0.1.0")  # the tag form works too
    assert last == "## [0.1.0] - 2026-01-01\n\n### Added\n- One.\n"
    assert module.section(SAMPLE, "9.9.9") is None
    assert module.section(SAMPLE, "0.2") is None  # no prefix matches


def test_current_version_has_a_changelog_section():
    from heimdall_guardian import __version__

    module = _changelog_module()
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert module.section(text, __version__)
