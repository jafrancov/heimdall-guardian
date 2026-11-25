from __future__ import annotations

import shutil
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def project(tmp_path: Path):
    """Copy a fixture to a temporary folder and return its path."""

    def _copy(name: str) -> Path:
        target = tmp_path / name
        shutil.copytree(FIXTURES / name, target)
        return target

    return _copy


@pytest.fixture(autouse=True)
def isolated_data_dir(tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch):
    """No test writes to the user's real data directory."""
    path = tmp_path_factory.mktemp("datos")
    monkeypatch.setenv("HDL_DATA_DIR", str(path))
    monkeypatch.delenv("HDL_BASES_DIR", raising=False)
    return path


@pytest.fixture(autouse=True)
def _no_system_language(monkeypatch: pytest.MonkeyPatch):
    """The language of the tests does not depend on the machine: its macOS preference, its
    locale variables or the locale Python started with (a CI runner is in English)."""
    from heimdall_guardian.i18n import languages

    monkeypatch.setattr(languages, "_macos_language", lambda: None)
    monkeypatch.setattr(languages.locale, "getlocale", lambda *_args: (None, None))
    for var in ("HDL_LANG", "LC_ALL", "LC_MESSAGES", "LANG"):
        monkeypatch.delenv(var, raising=False)


@pytest.fixture(autouse=True)
def _restore_language(monkeypatch: pytest.MonkeyPatch):
    """A test that changes the session language does not affect the following ones."""
    from heimdall_guardian.i18n import languages

    # Almost all tests expect Spanish texts: the real default is English.
    monkeypatch.setattr(languages, "_current", "es")
    monkeypatch.setattr(languages, "DEFAULT_LANGUAGE", "es")
