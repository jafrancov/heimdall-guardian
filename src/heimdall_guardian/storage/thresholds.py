"""Verdict thresholds: PIN-protected, with a log of every change.

They live in the data directory, not in `config.toml`: that way a change goes
through the PIN and is recorded. The PIN is a local protection against
accidental changes; whoever controls the machine can edit the files, which is
why the verdict always declares the thresholds it was issued with.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from ..core.paths import archive_file, data_dir
from ..core.verdict import Thresholds
from ..i18n import Message, msg, t

THRESHOLDS_FILE = "verdict_thresholds.json"
LOG_FILE = "verdict_thresholds_log.jsonl"
_LEGACY_FILE = "dictamen.json"  # Spanish keys: set aside, not migrated
_LEGACY_LOG = "dictamen-bitacora.jsonl"
_ITERATIONS = 240_000
MIN_PIN_LENGTH = 6


class PinError(ValueError):
    """The PIN is missing or does not match."""


class ThresholdStore:
    def __init__(self, base: Path | None = None) -> None:
        self.directory = base or data_dir()
        self._file = self.directory / THRESHOLDS_FILE
        self._log = self.directory / LOG_FILE
        # Notices about what was set aside on opening (the earlier format, PIN included).
        self.notices: list[Message] = self._archive_legacy()

    def _archive_legacy(self) -> list[Message]:
        """Sets aside the files of the version with Spanish keys; the PIN is not kept."""
        archived = [
            target.name
            for name in (_LEGACY_FILE, _LEGACY_LOG)
            if (target := archive_file(self.directory / name, 1)) is not None
        ]
        return [msg("thresholds.archived", names=", ".join(archived))] if archived else []

    def _read(self) -> dict[str, Any]:
        try:
            data: dict[str, Any] = json.loads(self._file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return data

    def _write(self, data: dict[str, Any]) -> None:
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        self._file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        self._file.chmod(0o600)

    def _record(self, author: str, change: Message, detail: dict[str, Any]) -> None:
        entry = {
            "date": datetime.now().astimezone().isoformat(timespec="seconds"),
            "author": author,
            "change": change,
            **detail,
        }
        with self._log.open("a", encoding="utf-8") as log:
            log.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # ---------------------------------------------------------------- PIN

    @staticmethod
    def _hash(pin: str, salt: bytes) -> str:
        return hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), salt, _ITERATIONS).hex()

    def has_pin(self) -> bool:
        return "pin" in self._read()

    def _check(self, pin: str) -> None:
        stored = self._read().get("pin")
        if stored is None:
            raise PinError(t("thresholds.error.no_pin"))
        expected = self._hash(pin, bytes.fromhex(stored["salt"]))
        if not hmac.compare_digest(expected, stored["hash"]):
            raise PinError(t("thresholds.error.pin_mismatch"))

    def set_pin(self, new_pin: str, author: str, current_pin: str | None = None) -> None:
        if len(new_pin) < MIN_PIN_LENGTH:
            raise PinError(t("thresholds.error.pin_too_short", minimum=MIN_PIN_LENGTH))
        data = self._read()
        if "pin" in data:
            self._check(current_pin or "")
        salt = secrets.token_bytes(16)
        data["pin"] = {"salt": salt.hex(), "hash": self._hash(new_pin, salt)}
        self._write(data)
        self._record(
            author,
            msg("thresholds.log.pin_set" if current_pin is None else "thresholds.log.pin_changed"),
            {},
        )

    # ---------------------------------------------------------- thresholds

    def load(self) -> Thresholds:
        raw = self._read().get("thresholds")
        if not raw:
            return Thresholds()
        try:
            return Thresholds.from_dict(raw)
        except (ValueError, TypeError):
            # A damaged file must not relax the verdict: the proposal's defaults are used.
            return Thresholds()

    def save(self, thresholds: Thresholds, pin: str, author: str) -> None:
        self._check(pin)
        previous = self.load()
        if thresholds == previous:
            return
        data = self._read()
        data["thresholds"] = asdict(thresholds)
        self._write(data)
        self._record(
            author,
            msg("thresholds.log.changed"),
            {"before": asdict(previous), "after": asdict(thresholds)},
        )

    def history(self) -> list[dict[str, Any]]:
        try:
            lines = self._log.read_text(encoding="utf-8").splitlines()
        except OSError:
            return []
        entries = [json.loads(line) for line in lines if line.strip()]
        for entry in entries:
            # A new change is a message (shown in the current language); those from
            # earlier versions are already-written text and are shown as is.
            if isinstance(entry.get("change"), dict):
                entry["change"] = Message(entry["change"])
        return entries
