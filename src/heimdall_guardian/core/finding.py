"""Normalized finding model."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from enum import StrEnum
from typing import Any


class Severity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

    @property
    def rank(self) -> int:
        """0 is the most severe; used to sort and compare."""
        return list(Severity).index(self)


class Confidence(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Category(StrEnum):
    SECRETS = "secrets"
    DEPENDENCIES = "dependencies"
    SAST = "sast"
    ACCESS_CONTROL = "access_control"
    CONFIGURATION = "configuration"
    FLOW = "flow"


class Origin(StrEnum):
    DETERMINISTIC = "deterministic"
    AI = "ai"


class BaselineStatus(StrEnum):
    NEW = "new"
    PERSISTENT = "persistent"
    FIXED = "fixed"
    ACCEPTED = "accepted"
    FALSE_POSITIVE = "false_positive"


@dataclass
class Finding:
    fingerprint: str
    source: str
    rule_id: str
    category: Category
    severity: Severity
    confidence: Confidence
    file: str  # path relative to the analyzed folder
    line_start: int  # 0 = no known line (e.g. dependencies)
    line_end: int
    snippet: str  # always with secrets masked
    # Base text: the English of our own sources or whatever an external tool wrote.
    title: str = ""
    description: str = ""
    recommendation: str = ""
    owasp: str | None = None
    cwe: str | None = None
    references: list[str] = field(default_factory=list)
    origin: Origin = Origin.DETERMINISTIC
    baseline_status: BaselineStatus = BaselineStatus.NEW
    llm_assessment: dict[str, Any] | None = None
    # Tools that reported the same finding (same fingerprint).
    detected_by: list[str] = field(default_factory=list)
    module: str = ""  # analysis module that produced it (SEC, DEP, SAST...)
    fixed_version: str = ""  # dependencies: version that fixes the vulnerability
    id: str = ""  # assigned by the core when the run is closed
    # Texts of our own sources in each language: {"en": {"title": ...}, "es": {...}}.
    # The one for the current language is shown; `i18n.text_of` handles the fallback to English.
    texts: dict[str, dict[str, str]] = field(default_factory=dict)
    # Only candidates (rules tagged CAND) carry it: sql, exec, path, ssrf or redirect. They
    # are handed to the AI and never stored, so `to_dict` leaves it out when it is empty.
    candidate_kind: str = ""

    def __post_init__(self) -> None:
        if not self.detected_by:
            self.detected_by = [self.source]
        base = self.texts.get("en", {})
        for name in ("title", "description", "recommendation"):
            if not getattr(self, name) and base.get(name):
                setattr(self, name, base[name])

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Finding:
        """Rebuilds a stored finding (the inverse of `to_dict`)."""
        known = {item.name for item in fields(cls)}
        values = {key: value for key, value in data.items() if key in known}
        for name, enum in (
            ("category", Category),
            ("severity", Severity),
            ("confidence", Confidence),
            ("origin", Origin),
            ("baseline_status", BaselineStatus),
        ):
            values[name] = enum(values[name])
        return cls(**values)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        if not data["candidate_kind"]:
            del data["candidate_kind"]
        # `id` first: it is what a person looks for when reading the JSON.
        return {"id": data.pop("id"), **data}
