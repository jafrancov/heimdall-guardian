"""Output schemas for each AI task. Whatever fails validation is discarded.

The field names are the usual ones, but their values are neutral English codes
(`likely_real`, `high`, `none`...): the interface and the reports show them with the
current language's label, just like severity.
"""

from __future__ import annotations

import json
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class Verdict(StrEnum):
    LIKELY_REAL = "likely_real"
    LIKELY_FALSE = "likely_false"
    UNCERTAIN = "uncertain"


class Level(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Risk(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class Reach(StrEnum):
    YES = "yes"
    NO = "no"
    UNCLEAR = "unclear"


class _Output(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)


class Triage(_Output):
    """T1: is the tool's finding real?"""

    verdict: Verdict
    explanation: str = Field(min_length=1, max_length=1200)
    suggested_fix: str = Field(default="", max_length=1500)
    confidence: Level


class EndpointReview(_Output):
    """T2: access control of an endpoint."""

    requires_auth: bool
    has_auth: bool
    checks_object_ownership: bool | None = None
    idor_risk: Risk
    flow_risk: Risk
    explanation: str = Field(min_length=1, max_length=1200)


class SinkReview(_Output):
    """T4: does untrusted input reach a dangerous operation unprotected?"""

    reachable: Reach
    source: str = Field(default="", max_length=300)
    risk: Risk
    explanation: str = Field(min_length=1, max_length=1200)
    suggested_fix: str = Field(default="", max_length=1500)


class Summary(_Output):
    """T3: executive summary."""

    summary: str = Field(min_length=1, max_length=2500)


def extract_json(text: str) -> str | None:
    """First JSON object in the text: tolerates code fences and surrounding text."""
    start = text.find("{")
    while start != -1:
        depth, quote, index = 0, False, start
        while index < len(text):
            char = text[index]
            if quote:
                if char == "\\":
                    index += 1
                elif char == '"':
                    quote = False
            elif char == '"':
                quote = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return text[start : index + 1]
            index += 1
        start = text.find("{", start + 1)
    return None


def parse[T: BaseModel](text: str, model: type[T]) -> T | None:
    """Tolerant extraction and strict validation; `None` if it does not meet the schema."""
    candidate = extract_json(text)
    if candidate is None:
        return None
    try:
        return model.model_validate(json.loads(candidate))
    except (json.JSONDecodeError, ValidationError):
        return None
