"""Vendor delivery verdict: turns the report into a yes or a no."""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field, fields
from enum import StrEnum
from typing import Any

from .finding import BaselineStatus, Category, Finding, Origin, Severity

OPEN_STATUSES = (BaselineStatus.NEW, BaselineStatus.PERSISTENT)
WRITE_ENDPOINT_RULE = "AUTHZ-001"
# Configuration rules that actually point to a credential in the code.
SECRET_RULES = frozenset({"DJ-CONF-002", "NET-CONF-001"})


class Outcome(StrEnum):
    APPROVED = "approved"
    APPROVED_WITH_OBSERVATIONS = "approved_with_observations"
    NOT_APPROVED = "not_approved"


def _t(key: str, **params: Any) -> str:
    """`t` with a deferred import: the label catalog imports this module."""
    from ..i18n import t

    return t(key, **params)


@dataclass(frozen=True)
class Thresholds:
    """Maximum tolerated per criterion. The defaults are the ones in the proposal."""

    max_critical: int = 0
    max_secrets: int = 0
    max_unauth_write_endpoints: int = 0
    max_high: int = 5
    max_patchable_critical_deps: int = 0
    count_ai_findings: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Thresholds:
        known = {f.name for f in fields(cls)}
        unknown = sorted(set(data) - known)
        if unknown:
            raise ValueError(_t("core.verdict.unknown_threshold", names=", ".join(unknown)))
        values = cls(**data)
        for item in fields(cls):
            value = getattr(values, item.name)
            expected = bool if item.name == "count_ai_findings" else int
            if type(value) is not expected or (expected is int and value < 0):
                raise ValueError(
                    _t("core.verdict.invalid_value", name=item.name, value=repr(value))
                )
        return values


@dataclass(frozen=True)
class Criterion:
    key: str
    count: int
    limit: int
    blocking: bool  # exceeding it prevents accepting the delivery

    @property
    def exceeded(self) -> bool:
        return self.count > self.limit

    @property
    def label(self) -> str:
        """The criterion's name in the current language."""
        return _t(f"verdict.criterion.{self.key}")

    def to_dict(self) -> dict[str, Any]:
        from ..i18n import msg

        return {
            "criterion": msg(f"verdict.criterion.{self.key}"),
            "found": self.count,
            "limit": self.limit,
            "exceeded": self.exceeded,
            "blocking": self.blocking,
        }


@dataclass
class Verdict:
    outcome: Outcome
    criteria: list[Criterion]
    thresholds: Thresholds
    issuer: str
    tree_hash: str
    rules_version: str
    issued: str
    accepted: list[dict[str, Any]] = field(default_factory=list)
    medium_open: int = 0
    signature: str = ""

    def __post_init__(self) -> None:
        if not self.signature:
            self.signature = sign(
                self.tree_hash, self.rules_version, self.issuer, self.outcome, self.issued
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome": self.outcome.value,
            "criteria": [criterion.to_dict() for criterion in self.criteria],
            "thresholds": asdict(self.thresholds),
            "default_thresholds": self.thresholds == Thresholds(),
            "medium_open": self.medium_open,
            "accepted_findings": self.accepted,
            "issuer": self.issuer,
            "issued": self.issued,
            "tree_hash": self.tree_hash,
            "rules_version": self.rules_version,
            "signature": self.signature,
        }


def sign(tree_hash: str, rules_version: str, issuer: str, outcome: str, issued: str) -> str:
    """Fingerprint of the verdict: ties the result to the code, the rules and whoever issues it.

    It is not a cryptographic signature with a key: it serves to check that a
    verdict corresponds to an exact version of the code, not to prove
    identity.
    """
    payload = "\n".join((tree_hash, rules_version, issuer, outcome, issued))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def evaluate(
    findings: list[Finding],
    thresholds: Thresholds,
    *,
    issuer: str,
    tree_hash: str,
    rules_version: str,
    issued: str,
) -> Verdict:
    """Applies the thresholds to the open findings.

    Accepted findings and false positives do not count (they stay listed in the
    verdict), nor do AI suggestions unless the thresholds ask for them.
    """
    counted = [
        f
        for f in findings
        if f.baseline_status in OPEN_STATUSES
        and (thresholds.count_ai_findings or f.origin is Origin.DETERMINISTIC)
    ]

    def count(predicate: Any) -> int:
        return sum(1 for finding in counted if predicate(finding))

    criteria = [
        Criterion(
            "max_critical",
            count(lambda f: f.severity is Severity.CRITICAL),
            thresholds.max_critical,
            blocking=True,
        ),
        Criterion(
            "max_secrets",
            count(lambda f: f.category is Category.SECRETS or f.rule_id in SECRET_RULES),
            thresholds.max_secrets,
            blocking=True,
        ),
        Criterion(
            "max_unauth_write_endpoints",
            count(lambda f: f.rule_id == WRITE_ENDPOINT_RULE),
            thresholds.max_unauth_write_endpoints,
            blocking=True,
        ),
        Criterion(
            "max_patchable_critical_deps",
            count(
                lambda f: (
                    f.category is Category.DEPENDENCIES
                    and f.severity is Severity.CRITICAL
                    and bool(f.fixed_version)
                )
            ),
            thresholds.max_patchable_critical_deps,
            blocking=True,
        ),
        Criterion(
            "max_high",
            count(lambda f: f.severity is Severity.HIGH),
            thresholds.max_high,
            blocking=False,
        ),
    ]
    medium = count(lambda f: f.severity is Severity.MEDIUM)
    if any(c.exceeded for c in criteria if c.blocking):
        outcome = Outcome.NOT_APPROVED
    elif any(c.exceeded for c in criteria) or medium:
        outcome = Outcome.APPROVED_WITH_OBSERVATIONS
    else:
        outcome = Outcome.APPROVED

    accepted = [
        {"id": f.id, "title": f.title, "texts": f.texts, "severity": f.severity.value,
         "status": f.baseline_status.value}
        for f in findings
        if f.baseline_status in (BaselineStatus.ACCEPTED, BaselineStatus.FALSE_POSITIVE)
    ]  # fmt: skip
    return Verdict(
        outcome=outcome,
        criteria=criteria,
        thresholds=thresholds,
        issuer=issuer,
        tree_hash=tree_hash,
        rules_version=rules_version,
        issued=issued,
        accepted=accepted,
        medium_open=medium,
    )
