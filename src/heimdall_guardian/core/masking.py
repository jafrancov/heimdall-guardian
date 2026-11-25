"""Secret masking: the report must never become a new leak."""

from __future__ import annotations

import re
from collections.abc import Iterable

MASK = "****"

# name = "literal" / 'NAME': 'literal' / $name => "literal"
_ASSIGNMENT = re.compile(
    r"""(?ix)
    (\b[\w.$-]*(?:password|passwd|pwd|contrasen[ai]a|secret|token|api[_-]?key|access[_-]?key)
       [\w.-]*["']?\s*(?:=>|[:=])\s*)
    (["'])([^"'\n]{4,})\2
    """
)
# Connection strings: ...;Password=value;... (no spaces around the `=`)
_CONNECTION_STRING = re.compile(r"(?im)((?:^|[;\"'\s])(?:password|pwd)=)([^;\"'\s]+)")
# .env files: DB_PASSWORD=value
_ENV_ASSIGNMENT = re.compile(
    r"(?m)^([ \t]*(?:export[ \t]+)?[A-Z0-9_]*(?:PASSWORD|SECRET|API_KEY|TOKEN|PASS|PWD)"
    r"[A-Z0-9_]*[ \t]*=[ \t]*)([^\s\"'(\[#]+)[ \t]*$"
)


def mask_secret(secret: str) -> str:
    """`AKIA****WXYZ` for long secrets; short ones are hidden entirely."""
    if len(secret) >= 16:
        return f"{secret[:4]}{MASK}{secret[-4:]}"
    return MASK


def mask_known(text: str, secrets: Iterable[str]) -> str:
    """Replaces every already-identified secret, wherever it appears."""
    for secret in sorted({s for s in secrets if s}, key=len, reverse=True):
        text = text.replace(secret, mask_secret(secret))
    return text


def mask_generic(text: str) -> str:
    """Hides literals assigned to names that give a credential away.

    It is deliberately broad: it prefers hiding too much in a snippet to
    reproducing a password in the report.
    """
    text = _ASSIGNMENT.sub(lambda m: f"{m[1]}{m[2]}{mask_secret(m[3])}{m[2]}", text)
    text = _CONNECTION_STRING.sub(lambda m: f"{m[1]}{mask_secret(m[2])}", text)
    return _ENV_ASSIGNMENT.sub(lambda m: f"{m[1]}{mask_secret(m[2])}", text)
