"""Baseline engine: compares a run against what the project already knows."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import date

from .finding import BaselineStatus, Finding

# If the snippet changed but rule and file match within this distance, it is
# treated as the same finding rather than one fixed plus one new.
LINE_TOLERANCE = 20


@dataclass(frozen=True)
class Known:
    """A finding already recorded in the project's baseline."""

    fingerprint: str
    rule_id: str
    file: str
    line_start: int
    module: str
    detected_by: tuple[str, ...]
    open: bool


@dataclass(frozen=True)
class Suppression:
    fingerprint: str
    status: BaselineStatus  # ACEPTADO | FALSO_POSITIVO
    justification: str
    author: str
    created: str
    review_date: date | None = None

    def active(self, today: date) -> bool:
        """An expired suppression stops hiding the finding."""
        return self.review_date is None or self.review_date >= today


@dataclass
class Comparison:
    statuses: dict[str, BaselineStatus] = field(default_factory=dict)
    rekeyed: dict[str, str] = field(default_factory=dict)  # new fingerprint → previous fingerprint
    fixed: list[str] = field(default_factory=list)  # fingerprints that become CORREGIDO
    expired: list[str] = field(default_factory=list)  # with an expired suppression


def _match_moved(new: list[Finding], missing: list[Known]) -> dict[str, str]:
    """Pairs findings whose snippet changed; only when there is no ambiguity."""
    new_groups: dict[tuple[str, str], list[Finding]] = defaultdict(list)
    for finding in new:
        new_groups[(finding.rule_id, finding.file)].append(finding)
    missing_groups: dict[tuple[str, str], list[Known]] = defaultdict(list)
    for known in missing:
        missing_groups[(known.rule_id, known.file)].append(known)

    matches: dict[str, str] = {}
    for key, candidates in new_groups.items():
        previous = missing_groups.get(key, [])
        if len(candidates) != 1 or len(previous) != 1:
            continue
        if abs(candidates[0].line_start - previous[0].line_start) <= LINE_TOLERANCE:
            matches[candidates[0].fingerprint] = previous[0].fingerprint
    return matches


def compare(
    current: Iterable[Finding],
    known: Iterable[Known],
    suppressions: dict[str, Suppression],
    *,
    evaluated: Callable[[Known], bool],
    today: date,
) -> Comparison:
    """Decides the status of each current finding and which known ones were fixed.

    `evaluated` says whether this run actually looked for a known finding
    again: one that does not show up only counts as CORREGIDO if its module and
    its tool ran. That way a shorter profile "fixes" nothing.
    """
    current = list(current)
    known_by_fp = {k.fingerprint: k for k in known}
    current_fps = {f.fingerprint for f in current}
    missing = [k for k in known_by_fp.values() if k.open and k.fingerprint not in current_fps]
    new = [f for f in current if f.fingerprint not in known_by_fp]

    result = Comparison(rekeyed=_match_moved(new, missing))
    for finding in current:
        previous = known_by_fp.get(finding.fingerprint)
        if (previous is not None and previous.open) or finding.fingerprint in result.rekeyed:
            status = BaselineStatus.PERSISTENT
        else:
            # Unknown, or known but previously fixed and showing up again.
            status = BaselineStatus.NEW
        suppression = suppressions.get(finding.fingerprint)
        if suppression is not None:
            if suppression.active(today):
                status = suppression.status
            else:
                result.expired.append(finding.fingerprint)
        result.statuses[finding.fingerprint] = status

    moved = set(result.rekeyed.values())
    result.fixed = [k.fingerprint for k in missing if k.fingerprint not in moved and evaluated(k)]
    return result
