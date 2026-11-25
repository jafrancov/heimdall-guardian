"""Endpoint inventory model (AUTHZ module)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from ..i18n.messages import Message

# Why an endpoint was concluded to have (or lack) authentication: a structured message
# or, when it is just code (`@login_required`), the text as is.
Evidence = Message | str

WRITE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})
ANY_METHOD = "*"
# Routes that are usually public by design. This only lowers the finding's
# confidence: a name is not enough to consider an unprotected route fine.
_PUBLIC_BY_DESIGN = re.compile(
    r"(?i)(^|[/_.-])(login|logout|signin|sign-in|signup|registro|register|acceso|entrar|"
    r"salir|health|healthz|ping|status|password|recuperar|csrf|favicon|robots)([/_.-]|$)"
)


@dataclass
class Endpoint:
    path: str
    methods: list[str]  # ["*"] = any method
    handler: str  # view, action or file that serves the route
    file: str  # handler file, relative to the analyzed folder
    line: int
    framework: str
    has_auth: bool | None  # None = could not be determined
    evidence: Evidence
    writes: bool
    route_file: str = ""  # where the route is declared, if not `file`
    # Other lines of `file` that this endpoint already evaluates (e.g. the class).
    covers: list[int] = field(default_factory=list)

    @property
    def public_by_design(self) -> bool:
        return bool(_PUBLIC_BY_DESIGN.search(self.path) or _PUBLIC_BY_DESIGN.search(self.handler))

    @property
    def methods_key(self) -> str:
        """The methods as part of the fingerprint: language-independent («*» = any)."""
        return ANY_METHOD if self.methods == [ANY_METHOD] else ", ".join(self.methods)

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "methods": self.methods,
            "handler": self.handler,
            "file": self.file,
            "line": self.line,
            "framework": self.framework,
            "requires_auth": not self.public_by_design,
            "has_auth": self.has_auth,
            "evidence": self.evidence,
            "writes": self.writes,
            "idor_risk": None,  # evaluated by the AI module
            "source": "rule",
        }


def join_path(*parts: str) -> str:
    """Joins route segments into one with a leading `/` and no double slashes."""
    joined = "/".join(part.strip("/") for part in parts if part and part.strip("/"))
    return "/" + joined


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def strip_comments(text: str, *, hash_comments: bool = False) -> str:
    """Blanks out comments, preserving line breaks and positions.

    It is not a full lexer: it is enough so the extractors' regular
    expressions do not read commented-out code.
    """
    pattern = r"/\*.*?\*/|//[^\n]*" + (r"|#[^\n\[]*" if hash_comments else "")
    string = r"\"(?:\\.|[^\"\\\n])*\"|'(?:\\.|[^'\\\n])*'"

    def blank(match: re.Match[str]) -> str:
        chunk = match.group(0)
        if chunk[0] in "\"'":
            return chunk
        return re.sub(r"[^\n]", " ", chunk)

    return re.sub(f"{string}|{pattern}", blank, text, flags=re.S)
