"""Visible labels for the stored codes.

What is stored and exported (database, JSON, SARIF) are neutral English codes
(`critical`, `new`, `access_control`...). What a person sees comes from here.
Every language must have exactly the same keys as Spanish
(`tests/unit/test_i18n.py` checks it).
"""

from __future__ import annotations

from enum import StrEnum

from ..core.finding import BaselineStatus, Category, Confidence, Origin, Severity
from ..core.verdict import Outcome
from .languages import BASE_LANGUAGE, get_language

# Kinds of code that have a label, with the enum that defines them.
KINDS: dict[str, type[StrEnum]] = {
    "severity": Severity,
    "confidence": Confidence,
    "category": Category,
    "origin": Origin,
    "status": BaselineStatus,
    "outcome": Outcome,
}

# English is the base language (source text); Spanish is its translation. All
# languages have the same keys and, if a translation is missing, English is used.
LABELS: dict[str, dict[str, dict[str, str]]] = {
    "en": {
        "severity": {
            "critical": "CRITICAL",
            "high": "HIGH",
            "medium": "MEDIUM",
            "low": "LOW",
            "info": "INFO",
        },
        "confidence": {"high": "HIGH", "medium": "MEDIUM", "low": "LOW"},
        "category": {
            "secrets": "SECRETS",
            "dependencies": "DEPENDENCIES",
            "sast": "SAST",
            "access_control": "ACCESS CONTROL",
            "configuration": "CONFIGURATION",
            "flow": "FLOW",
        },
        "origin": {"deterministic": "deterministic", "ai": "ai"},
        "status": {
            "new": "NEW",
            "persistent": "PERSISTENT",
            "fixed": "FIXED",
            "accepted": "ACCEPTED",
            "false_positive": "FALSE POSITIVE",
        },
        "outcome": {
            "approved": "APPROVED",
            "approved_with_observations": "APPROVED WITH OBSERVATIONS",
            "not_approved": "NOT APPROVED",
        },
    },
    "es": {
        "severity": {
            "critical": "CRÍTICA",
            "high": "ALTA",
            "medium": "MEDIA",
            "low": "BAJA",
            "info": "INFO",
        },
        "confidence": {"high": "ALTA", "medium": "MEDIA", "low": "BAJA"},
        "category": {
            "secrets": "SECRETOS",
            "dependencies": "DEPENDENCIAS",
            "sast": "SAST",
            "access_control": "CONTROL ACCESO",
            "configuration": "CONFIGURACION",
            "flow": "FLUJO",
        },
        "origin": {"deterministic": "determinístico", "ai": "ia"},
        "status": {
            "new": "NUEVO",
            "persistent": "PERSISTENTE",
            "fixed": "CORREGIDO",
            "accepted": "ACEPTADO",
            "false_positive": "FALSO POSITIVO",
        },
        "outcome": {
            "approved": "APROBADO",
            "approved_with_observations": "APROBADO CON OBSERVACIONES",
            "not_approved": "NO APROBADO",
        },
    },
}


def kind_of(value: StrEnum) -> str:
    """The label kind of an enum member."""
    for kind, enum in KINDS.items():
        if isinstance(value, enum):
            return kind
    raise TypeError(f"{type(value).__name__} has no labels.")


def label(
    value: str,
    kind: str | None = None,
    lang: str | None = None,
    *,
    variant: str = "default",
) -> str:
    """The visible label of a code.

    `kind` may be omitted when `value` is an enum member. Variants:
    `default` (the one shown almost everywhere), `lower` (lowercase), `capitalized`
    (only the initial uppercase) and `snake` (with underscores, as shown in the
    spreadsheets). An unknown code is returned as is.
    """
    if kind is None:
        if not isinstance(value, StrEnum):
            raise TypeError("Give the label kind (`kind`) or pass an enum member.")
        kind = kind_of(value)
    lang = lang or get_language()
    table = LABELS.get(lang, {}).get(kind, {})
    text = table.get(str(value)) or LABELS[BASE_LANGUAGE][kind].get(str(value), str(value))
    if variant == "lower":
        return text.lower()
    if variant == "capitalized":
        return text.capitalize()
    if variant == "snake":
        return text.replace(" ", "_")
    return text


def severity_label(value: str, lang: str | None = None, *, variant: str = "default") -> str:
    return label(value, "severity", lang, variant=variant)


def status_label(value: str, lang: str | None = None, *, variant: str = "default") -> str:
    return label(value, "status", lang, variant=variant)


def category_label(value: str, lang: str | None = None, *, variant: str = "default") -> str:
    return label(value, "category", lang, variant=variant)


def origin_label(value: str, lang: str | None = None, *, variant: str = "default") -> str:
    return label(value, "origin", lang, variant=variant)


def confidence_label(value: str, lang: str | None = None, *, variant: str = "default") -> str:
    return label(value, "confidence", lang, variant=variant)


def outcome_label(value: str, lang: str | None = None, *, variant: str = "default") -> str:
    return label(value, "outcome", lang, variant=variant)
