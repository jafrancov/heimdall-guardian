"""Per-project SQLite database: runs, known findings and suppressions.

It lives in the application's data directory, never in the analyzed folder (P1).
"""

from __future__ import annotations

import configparser
import hashlib
import json
import re
import shutil
import sqlite3
from contextlib import closing
from datetime import date, datetime
from pathlib import Path
from typing import Any

from ..core.baseline import Known, Suppression, compare
from ..core.finding import BaselineStatus, Finding
from ..core.owasp import migrate_payload
from ..core.paths import archive_file, data_dir
from ..core.profiles import Module
from ..core.runner import ScanResult, issue_verdict, summarize
from ..core.verdict import Thresholds, evaluate
from ..i18n import Message, msg, t

SUPPRESSION_STATUSES = (BaselineStatus.ACCEPTED, BaselineStatus.FALSE_POSITIVE)
BASELINE_FORMAT = 3  # 3: English keys
# Schema version (PRAGMA user_version). Version 1 is that of unmarked databases, with the
# stored values in Spanish; version 2 stores neutral English codes. A database of another
# version is not migrated: it is archived and a new one is started.
SCHEMA_VERSION = 5  # 5: run keys and enum members in English
BASELINE_FILE = ".heimdall-baseline.json"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started TEXT NOT NULL,
    profile TEXT NOT NULL,
    tree_hash TEXT NOT NULL,
    summary TEXT NOT NULL,
    payload TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS findings (
    fingerprint TEXT PRIMARY KEY,
    seq INTEGER NOT NULL UNIQUE,
    public_id TEXT NOT NULL UNIQUE,
    rule_id TEXT NOT NULL,
    file TEXT NOT NULL,
    line_start INTEGER NOT NULL,
    module TEXT NOT NULL,
    detected_by TEXT NOT NULL,
    open INTEGER NOT NULL,
    first_run INTEGER NOT NULL,
    last_run INTEGER NOT NULL,
    fixed_run INTEGER,
    data TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS suppressions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fingerprint TEXT NOT NULL,
    status TEXT NOT NULL,
    justification TEXT NOT NULL CHECK (length(trim(justification)) > 0),
    author TEXT NOT NULL,
    created TEXT NOT NULL,
    review_date TEXT,
    revoked TEXT
);
"""


def _archive_old_database(directory: Path) -> Message | None:
    """Sets `baseline.db` aside if it uses an earlier schema; returns the notice or `None`."""
    database = directory / "baseline.db"
    if not database.is_file():
        return None
    try:
        with closing(sqlite3.connect(database)) as db:
            version = int(db.execute("PRAGMA user_version").fetchone()[0])
            has_tables = db.execute("SELECT count(*) FROM sqlite_master").fetchone()[0] > 0
    except sqlite3.Error:
        version, has_tables = 0, False
    if version == SCHEMA_VERSION or not has_tables:
        return None
    previous = version or 1
    target = directory / f"baseline.db.v{previous}.bak"
    counter = 1
    while target.exists():
        counter += 1
        target = directory / f"baseline.db.v{previous}.{counter}.bak"
    database.rename(target)
    for suffix in ("-wal", "-shm", "-journal"):
        extra = directory / f"baseline.db{suffix}"
        if extra.exists():
            extra.unlink()
    return msg("storage.archived", name=target.name)


_URL_CREDENTIALS = re.compile(r"(?<=://)[^/@]+@")


def _remote_url(root: Path) -> str | None:
    """URL of the `origin` remote, read from `.git/config` without running git."""
    parser = configparser.ConfigParser(strict=False, interpolation=None)
    try:
        parser.read(root / ".git" / "config", encoding="utf-8")
        url = parser.get('remote "origin"', "url", fallback=None)
    except (configparser.Error, OSError, UnicodeDecodeError):
        return None
    # A URL with user:token must not be stored.
    return _URL_CREDENTIALS.sub("", url.strip()) if url else None


def project_identity(root: Path) -> tuple[str, str]:
    """(id, key) of the project: the git remote if there is one; otherwise its path."""
    key = _remote_url(root) or str(root)
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16], key


EXCLUSIONS_FILE = "exclusions.json"
_LEGACY_EXCLUSIONS_FILE = "exclusiones.json"  # Spanish keys: set aside, not migrated
# Notices of files set aside before opening the project, waiting for the next run.
_pending_notices: dict[Path, list[Message]] = {}


def _archive_legacy_files(directory: Path) -> None:
    """Sets aside the project's files in the earlier format and leaves the notice pending."""
    target = archive_file(directory / _LEGACY_EXCLUSIONS_FILE, 1)
    if target is not None:
        _pending_notices.setdefault(directory.resolve(), []).append(
            msg("storage.archived_exclusions", name=target.name)
        )


def _project_directory(root: Path, base: Path | None = None) -> Path:
    project_id, _ = project_identity(root.resolve())
    return (base or data_dir()) / "projects" / project_id


def _project_exclusions_file(root: Path, base: Path | None = None) -> Path:
    return _project_directory(root, base) / EXCLUSIONS_FILE


def load_project_exclusions(root: Path) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """(folders to skip, folders to include) that the user chose for this project."""
    _archive_legacy_files(_project_directory(root))
    try:
        data = json.loads(_project_exclusions_file(root).read_text(encoding="utf-8"))
        return tuple(map(str, data.get("exclude", []))), tuple(map(str, data.get("include", [])))
    except (OSError, json.JSONDecodeError, AttributeError, TypeError):
        return (), ()


def save_project_exclusions(root: Path, exclude: list[str], include: list[str]) -> None:
    target = _project_exclusions_file(root)
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    _archive_legacy_files(target.parent)
    target.write_text(
        json.dumps(
            {"exclude": sorted(set(exclude)), "include": sorted(set(include))},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


class Store:
    def __init__(self, root: Path, base: Path | None = None) -> None:
        root = root.resolve()
        base = (base or data_dir()).resolve()
        if base.is_relative_to(root):
            raise ValueError(t("storage.error.data_inside_folder"))
        self.project_id, self.project_key = project_identity(root)
        self.directory = base / "projects" / self.project_id
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        _archive_legacy_files(self.directory)
        self.archive_notices: list[Message] = _pending_notices.pop(self.directory.resolve(), [])
        if notice := _archive_old_database(self.directory):
            self.archive_notices.append(notice)
        self._db = sqlite3.connect(self.directory / "baseline.db")
        self._db.row_factory = sqlite3.Row
        self._db.executescript(_SCHEMA)
        self._db.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        (self.directory / "project.json").write_text(
            json.dumps(
                {"name": root.name, "key": self.project_key, "path": str(root)},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def close(self) -> None:
        self._db.close()

    def __enter__(self) -> Store:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    # ---------------------------------------------------------------- runs

    def _known(self) -> list[Known]:
        return [
            Known(
                fingerprint=row["fingerprint"],
                rule_id=row["rule_id"],
                file=row["file"],
                line_start=row["line_start"],
                module=row["module"],
                detected_by=tuple(json.loads(row["detected_by"])),
                open=bool(row["open"]),
            )
            for row in self._db.execute("SELECT * FROM findings")
        ]

    def _active_suppressions(self) -> dict[str, Suppression]:
        rows = self._db.execute("SELECT * FROM suppressions WHERE revoked IS NULL ORDER BY id")
        return {
            row["fingerprint"]: Suppression(
                fingerprint=row["fingerprint"],
                status=BaselineStatus(row["status"]),
                justification=row["justification"],
                author=row["author"],
                created=row["created"],
                review_date=date.fromisoformat(row["review_date"]) if row["review_date"] else None,
            )
            for row in rows
        }

    def record(
        self,
        result: ScanResult,
        *,
        thresholds: Thresholds | None = None,
        issuer: str = "",
    ) -> None:
        """Applies the baseline to the run (statuses and IDs) and saves it.

        With `thresholds` it also issues the verdict: that has to happen here, after
        applying the suppressions, because an accepted risk stops counting.
        """
        ran = {tool.name for tool in result.tools if tool.status == "ran"}
        modules = {str(module) for module in result.plan.modules}

        omitted = 0
        exclusions = result.plan.exclusions

        def evaluated(known: Known) -> bool:
            nonlocal omitted
            # A finding in a place the user now skips was not looked for: it is
            # omitted (kept as it was), never "fixed".
            if exclusions.excludes(
                known.file,
                sast=known.module in {Module.SAST.value, Module.AUTHZ.value},
                secret=known.module in {Module.SEC.value, Module.SEC_H.value},
            ):
                omitted += 1
                return False
            return known.module in modules and bool(ran.intersection(known.detected_by))

        suppressions = self._active_suppressions()
        today = result.started.date()
        comparison = compare(
            result.findings, self._known(), suppressions, evaluated=evaluated, today=today
        )

        result.omitted_findings = omitted
        with self._db:
            previous = self._db.execute("SELECT MAX(id) FROM runs").fetchone()[0]
            run_id = self._db.execute(
                "INSERT INTO runs (started, profile, tree_hash, summary, payload) "
                "VALUES (?, ?, ?, '', '')",
                (
                    result.started.isoformat(timespec="seconds"),
                    result.plan.profile,
                    result.tree_hash,
                ),
            ).lastrowid
            assert run_id is not None  # noqa: S101 - guaranteed by the INSERT

            # A finding whose snippet merely changed keeps its ID, but not its
            # suppression: the code is different and the justification must be reviewed.
            for new_fp, old_fp in comparison.rekeyed.items():
                self._db.execute(
                    "UPDATE findings SET fingerprint = ? WHERE fingerprint = ?", (new_fp, old_fp)
                )

            seq = self._db.execute("SELECT COALESCE(MAX(seq), 0) FROM findings").fetchone()[0]
            for finding in result.findings:
                finding.baseline_status = comparison.statuses[finding.fingerprint]
                row = self._db.execute(
                    "SELECT public_id FROM findings WHERE fingerprint = ?", (finding.fingerprint,)
                ).fetchone()
                if row is None:
                    seq += 1
                    finding.id = f"HDL-{result.started.year}-{seq:06d}"
                    self._db.execute(
                        "INSERT INTO findings VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, NULL, ?)",
                        (
                            finding.fingerprint,
                            seq,
                            finding.id,
                            finding.rule_id,
                            finding.file,
                            finding.line_start,
                            finding.module,
                            json.dumps(finding.detected_by),
                            run_id,
                            run_id,
                            json.dumps(finding.to_dict(), ensure_ascii=False),
                        ),
                    )
                else:
                    finding.id = row["public_id"]
                    self._db.execute(
                        "UPDATE findings SET open = 1, fixed_run = NULL, last_run = ?, file = ?, "
                        "line_start = ?, module = ?, detected_by = ?, data = ? "
                        "WHERE fingerprint = ?",
                        (
                            run_id,
                            finding.file,
                            finding.line_start,
                            finding.module,
                            json.dumps(finding.detected_by),
                            json.dumps(finding.to_dict(), ensure_ascii=False),
                            finding.fingerprint,
                        ),
                    )

            result.limitations += self.archive_notices
            self.archive_notices = []
            result.fixed = []
            for fingerprint in comparison.fixed:
                row = self._db.execute(
                    "SELECT data FROM findings WHERE fingerprint = ?", (fingerprint,)
                ).fetchone()
                self._db.execute(
                    "UPDATE findings SET open = 0, fixed_run = ? WHERE fingerprint = ?",
                    (run_id, fingerprint),
                )
                data = json.loads(row["data"])
                data["baseline_status"] = BaselineStatus.FIXED.value
                result.fixed.append(data)
            result.fixed.sort(key=lambda item: item["id"])

            for finding in result.findings:
                suppression = suppressions.get(finding.fingerprint)
                if suppression and finding.fingerprint in comparison.expired:
                    result.limitations.append(
                        msg(
                            "storage.suppression_expired",
                            id=finding.id,
                            date=str(suppression.review_date),
                        )
                    )

            if thresholds is not None:
                issue_verdict(result, thresholds, issuer)
            result.run_id = run_id
            result.previous_run_id = previous
            summary = result.summary()
            self._db.execute(
                "UPDATE runs SET summary = ? WHERE id = ?",
                (json.dumps(summary, ensure_ascii=False), run_id),
            )
            result.trend = self.runs()
            self._db.execute(
                "UPDATE runs SET payload = ? WHERE id = ?",
                (json.dumps(result.to_dict(), ensure_ascii=False), run_id),
            )

    def runs(self) -> list[dict[str, Any]]:
        """The project's runs, from oldest to newest (trend)."""
        return [
            {
                "run": row["id"],
                "started": row["started"],
                "profile": row["profile"],
                "tree_hash": row["tree_hash"],
                **json.loads(row["summary"] or "{}"),
            }
            for row in self._db.execute("SELECT * FROM runs ORDER BY id")
        ]

    def payload(self, run_id: int | None = None) -> dict[str, Any]:
        """Stored result of a run (the latest if none is given)."""
        if run_id is None:
            row = self._db.execute("SELECT payload FROM runs ORDER BY id DESC LIMIT 1").fetchone()
        else:
            row = self._db.execute("SELECT payload FROM runs WHERE id = ?", (run_id,)).fetchone()
        if row is None:
            raise LookupError(
                t("storage.error.no_runs")
                if run_id is None
                else t("storage.error.no_such_run", run=run_id)
            )
        data: dict[str, Any] = json.loads(row["payload"])
        return migrate_payload(data)  # an old run is shown with the current edition

    # ---------------------------------------------------------- suppressions

    def _fingerprint_of(self, public_id: str) -> str:
        row = self._db.execute(
            "SELECT fingerprint FROM findings WHERE public_id = ?", (public_id.strip().upper(),)
        ).fetchone()
        if row is None:
            raise LookupError(t("storage.error.no_such_finding", id=public_id))
        return str(row["fingerprint"])

    def suppress(
        self,
        public_id: str,
        status: BaselineStatus,
        justification: str,
        author: str,
        review_date: date | None = None,
    ) -> None:
        if status not in SUPPRESSION_STATUSES:
            raise ValueError(t("storage.error.bad_suppression_status"))
        if not justification.strip():
            raise ValueError(t("storage.error.justification_required"))
        fingerprint = self._fingerprint_of(public_id)
        now = datetime.now().astimezone().isoformat(timespec="seconds")
        with self._db:
            self._db.execute(
                "UPDATE suppressions SET revoked = ? WHERE fingerprint = ? AND revoked IS NULL",
                (now, fingerprint),
            )
            self._db.execute(
                "INSERT INTO suppressions (fingerprint, status, justification, author, created, "
                "review_date) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    fingerprint,
                    status.value,
                    justification.strip(),
                    author,
                    now,
                    review_date.isoformat() if review_date else None,
                ),
            )
        self.restate_last_run()

    def unsuppress(self, public_id: str) -> bool:
        fingerprint = self._fingerprint_of(public_id)
        now = datetime.now().astimezone().isoformat(timespec="seconds")
        with self._db:
            cursor = self._db.execute(
                "UPDATE suppressions SET revoked = ? WHERE fingerprint = ? AND revoked IS NULL",
                (now, fingerprint),
            )
        self.restate_last_run()
        return cursor.rowcount > 0

    def restate_last_run(self) -> bool:
        """Re-applies the current suppressions to the latest stored run.

        This way accepting a risk, or withdrawing it, shows up immediately in the list
        and in the reports, without analyzing again. It recomputes summary and verdict.
        """
        row = self._db.execute("SELECT id, payload FROM runs ORDER BY id DESC LIMIT 1").fetchone()
        if row is None or not row["payload"]:
            return False
        run_id, payload = row["id"], json.loads(row["payload"])
        today = datetime.now().astimezone().date()
        suppressions = self._active_suppressions()
        first_runs = {
            r["fingerprint"]: r["first_run"]
            for r in self._db.execute("SELECT fingerprint, first_run FROM findings")
        }
        findings = [Finding.from_dict(item) for item in payload["findings"]]
        for finding in findings:
            suppression = suppressions.get(finding.fingerprint)
            if suppression is not None and suppression.active(today):
                finding.baseline_status = suppression.status
            elif first_runs.get(finding.fingerprint) == run_id:
                finding.baseline_status = BaselineStatus.NEW
            else:
                finding.baseline_status = BaselineStatus.PERSISTENT

        payload["findings"] = [finding.to_dict() for finding in findings]
        payload["summary"] = summarize(findings, len(payload.get("fixed") or []))
        delivery = payload.get("verdict")
        if delivery:
            # Same thresholds, issuer and date: only what stopped counting changes.
            payload["verdict"] = evaluate(
                findings,
                Thresholds.from_dict(delivery["thresholds"]),
                issuer=delivery["issuer"],
                tree_hash=delivery["tree_hash"],
                rules_version=delivery["rules_version"],
                issued=delivery["issued"],
            ).to_dict()
        with self._db:
            self._db.execute(
                "UPDATE runs SET summary = ? WHERE id = ?",
                (json.dumps(payload["summary"], ensure_ascii=False), run_id),
            )
            if payload.get("baseline"):
                payload["baseline"]["trend"] = self.runs()
            self._db.execute(
                "UPDATE runs SET payload = ? WHERE id = ?",
                (json.dumps(payload, ensure_ascii=False), run_id),
            )
            for finding in findings:
                self._db.execute(
                    "UPDATE findings SET data = ? WHERE fingerprint = ?",
                    (json.dumps(finding.to_dict(), ensure_ascii=False), finding.fingerprint),
                )
        return True

    def suppressions(self) -> list[dict[str, Any]]:
        """Current suppressions, with the finding they refer to."""
        rows = self._db.execute(
            "SELECT s.*, f.public_id, f.rule_id, f.file FROM suppressions s "
            "JOIN findings f ON f.fingerprint = s.fingerprint "
            "WHERE s.revoked IS NULL ORDER BY s.id"
        )
        return [
            {
                "id": row["public_id"],
                "rule": row["rule_id"],
                "file": row["file"],
                "status": row["status"],
                "justification": row["justification"],
                "author": row["author"],
                "created": row["created"],
                "review_date": row["review_date"],
            }
            for row in rows
        ]

    # ------------------------------------------------- sharing the baseline

    def export_baseline(self, target: Path) -> int:
        """Writes known findings and current suppressions to a file with a digest.

        It serves to share the baseline with the team or to hand it over along with
        the report. It includes neither runs nor code snippets.
        """
        findings = [
            {
                key: row[key]
                for key in (
                    "fingerprint",
                    "public_id",
                    "rule_id",
                    "file",
                    "line_start",
                    "module",
                    "open",
                )
            }
            | {"detected_by": json.loads(row["detected_by"])}
            for row in self._db.execute("SELECT * FROM findings ORDER BY seq")
        ]
        suppressions = [
            {
                key: row[key]
                for key in (
                    "fingerprint",
                    "status",
                    "justification",
                    "author",
                    "created",
                    "review_date",
                )
            }
            for row in self._db.execute(
                "SELECT * FROM suppressions WHERE revoked IS NULL ORDER BY id"
            )
        ]
        content = {
            "format": BASELINE_FORMAT,
            "project": self.project_key,
            "findings": findings,
            "suppressions": suppressions,
        }
        target.write_text(
            json.dumps(
                {**content, "digest": _baseline_digest(content)}, ensure_ascii=False, indent=2
            ),
            encoding="utf-8",
        )
        return len(findings)

    def import_baseline(self, source: Path) -> tuple[int, int]:
        """Incorporates an exported baseline; returns the new (findings, suppressions).

        It only adds: it never deletes or reopens anything local. IDs belong to each
        machine, so a finding that did not exist here gets a new local ID.
        """
        try:
            data = json.loads(source.read_text(encoding="utf-8"))
            content = {key: data[key] for key in ("format", "project", "findings", "suppressions")}
        except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
            raise ValueError(t("storage.error.bad_baseline_file", error=exc)) from exc
        if content["format"] != BASELINE_FORMAT:
            raise ValueError(t("storage.error.bad_baseline_format", format=repr(content["format"])))
        if data.get("digest") != _baseline_digest(content):
            raise ValueError(t("storage.error.digest_mismatch"))

        added_findings = added_suppressions = 0
        with self._db:
            seq = self._db.execute("SELECT COALESCE(MAX(seq), 0) FROM findings").fetchone()[0]
            year = datetime.now().year
            for item in content["findings"]:
                exists = self._db.execute(
                    "SELECT 1 FROM findings WHERE fingerprint = ?", (item["fingerprint"],)
                ).fetchone()
                if exists:
                    continue
                seq += 1
                self._db.execute(
                    "INSERT INTO findings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, NULL, '{}')",
                    (
                        item["fingerprint"],
                        seq,
                        f"HDL-{year}-{seq:06d}",
                        item["rule_id"],
                        item["file"],
                        int(item["line_start"]),
                        item["module"],
                        json.dumps(item["detected_by"]),
                        int(bool(item["open"])),
                    ),
                )
                added_findings += 1
            for item in content["suppressions"]:
                if item["status"] not in {s.value for s in SUPPRESSION_STATUSES}:
                    raise ValueError(
                        t("storage.error.bad_imported_status", status=repr(item["status"]))
                    )
                if not str(item["justification"]).strip():
                    raise ValueError(t("storage.error.imported_without_justification"))
                active = self._db.execute(
                    "SELECT 1 FROM suppressions WHERE fingerprint = ? AND revoked IS NULL",
                    (item["fingerprint"],),
                ).fetchone()
                if active:
                    continue  # the local decision prevails
                self._db.execute(
                    "INSERT INTO suppressions (fingerprint, status, justification, author, "
                    "created, review_date) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        item["fingerprint"],
                        item["status"],
                        item["justification"],
                        item["author"],
                        item["created"],
                        item["review_date"],
                    ),
                )
                added_suppressions += 1
        return added_findings, added_suppressions


def _baseline_digest(content: dict[str, Any]) -> str:
    """Integrity digest: detects changes or damage, it does not prove authorship."""
    canonical = json.dumps(content, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def list_projects(base: Path | None = None) -> list[dict[str, Any]]:
    """Projects with stored runs, from newest to oldest."""
    projects = []
    for info in (base or data_dir()).glob("projects/*/project.json"):
        database = info.parent / "baseline.db"
        if not database.is_file():
            continue
        try:
            data = json.loads(info.read_text(encoding="utf-8"))
            # `with sqlite3.connect` only closes the transaction, not the connection.
            with closing(sqlite3.connect(database)) as db:
                if db.execute("PRAGMA user_version").fetchone()[0] != SCHEMA_VERSION:
                    continue
                row = db.execute(
                    "SELECT id, started, profile, summary FROM runs ORDER BY id DESC LIMIT 1"
                ).fetchone()
        except (OSError, json.JSONDecodeError, sqlite3.Error):
            continue
        if row is None:
            continue
        projects.append(
            {
                "id": info.parent.name,
                "name": data.get("name", ""),
                "path": data.get("path", ""),
                "run": row[0],
                "started": row[1],
                "profile": row[2],
                **json.loads(row[3] or "{}"),
            }
        )
    return sorted(projects, key=lambda item: item["started"], reverse=True)


def forget_project(project_id: str, base: Path | None = None) -> bool:
    """Deletes a project's history: runs, baseline, acceptances and exclusions.

    It does not touch the project folder (P1): only what Heimdall Guardian stored about it.
    """
    projects = ((base or data_dir()) / "projects").resolve()
    target = (projects / project_id).resolve()
    # Only a simple identifier, inside `projects/`: never another path.
    if target.parent != projects or not target.is_dir():
        return False
    shutil.rmtree(target)
    return True
