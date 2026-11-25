"""Stable fingerprint of a finding."""

from __future__ import annotations

import hashlib
from pathlib import PurePosixPath


def normalize_snippet(snippet: str) -> str:
    """Collapses whitespace so re-indenting the code does not change the fingerprint."""
    return " ".join(snippet.split())


def fingerprint(rule_id: str, relative_path: str, snippet: str) -> str:
    """sha256(rule + relative path + normalized snippet).

    It does not use the line number: moving code must not produce "new" findings.
    It is computed from the *unmasked* snippet to tell two different secrets in
    the same file apart; only the hash is kept.
    """
    path = PurePosixPath(relative_path.replace("\\", "/")).as_posix()
    payload = "\0".join((rule_id, path, normalize_snippet(snippet)))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
