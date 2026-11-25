"""Stored neutral codes, visible labels and archiving of earlier databases."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from heimdall_guardian.core.finding import BaselineStatus, Category, Confidence, Origin, Severity
from heimdall_guardian.core.verdict import Outcome
from heimdall_guardian.i18n import BASE_LANGUAGE, KINDS, LABELS, label, render
from heimdall_guardian.storage import store as store_module
from heimdall_guardian.storage.store import SCHEMA_VERSION, Store

ENUMS = [Severity, Confidence, Category, Origin, BaselineStatus, Outcome]


@pytest.mark.parametrize("enum", ENUMS)
def test_enum_values_are_neutral_ascii_codes(enum):
    for member in enum:
        assert member.value.isascii()
        assert member.value == member.value.lower()
        assert " " not in member.value


@pytest.mark.parametrize("enum", ENUMS)
def test_every_enum_value_has_a_label_in_every_language(enum):
    for lang in LABELS:
        for member in enum:
            assert label(member, lang=lang)
            assert member.value in LABELS[lang][next(k for k, e in KINDS.items() if e is enum)]


def test_languages_share_exactly_the_same_keys():
    base = LABELS[BASE_LANGUAGE]
    for lang, table in LABELS.items():
        assert table.keys() == base.keys()
        for kind in base:
            assert table[kind].keys() == base[kind].keys(), (lang, kind)


def test_spanish_labels_match_what_was_displayed_before():
    assert label(Severity.CRITICAL) == "CRÍTICA"
    assert label("false_positive", "status") == "FALSO POSITIVO"
    assert label("false_positive", "status", variant="snake") == "FALSO_POSITIVO"
    assert label("access_control", "category") == "CONTROL ACCESO"
    assert label("critical", "severity", variant="capitalized") == "Crítica"
    assert label("approved_with_observations", "outcome") == "APROBADO CON OBSERVACIONES"
    assert label(Origin.DETERMINISTIC) == "determinístico"
    assert label("critical", "severity", "en") == "CRITICAL"


def test_missing_translation_falls_back_to_english(monkeypatch):
    monkeypatch.setitem(LABELS, "xx", {"severity": {}})
    assert label("high", "severity", "xx") == "HIGH"


def test_old_schema_database_is_archived_not_migrated(tmp_path: Path):
    root = tmp_path / "project"
    root.mkdir()
    (root / "a.py").write_text("x = 1\n", encoding="utf-8")
    base = tmp_path / "datos"
    with Store(root, base) as store:
        directory = store.directory
    database = directory / "baseline.db"
    with sqlite3.connect(database) as db:
        db.execute("PRAGMA user_version = 1")
        db.execute(
            "INSERT INTO suppressions (fingerprint, status, justification, author, created)"
            " VALUES ('f', 'ACEPTADO', 'x', 'y', 'z')"
        )
    db.close()
    with Store(root, base) as store:
        assert len(store.archive_notices) == 1
        assert "archivó" in render(store.archive_notices[0])
        assert (directory / "baseline.db.v1.bak").is_file()
        assert store._db.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION
        assert store._db.execute("SELECT count(*) FROM suppressions").fetchone()[0] == 0
    with Store(root, base) as store:  # already of the current schema: it is not archived again
        assert store.archive_notices == []
    assert sorted(p.name for p in root.iterdir()) == ["a.py"]  # P1
    assert store_module.SCHEMA_VERSION == 5
