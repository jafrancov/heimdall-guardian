"""Supported languages and which one is used (no core dependencies, to avoid cycles)."""

from __future__ import annotations

import locale
import os
import subprocess
import sys
from collections.abc import Mapping

SUPPORTED = ("en", "es")
BASE_LANGUAGE = "en"
DEFAULT_LANGUAGE = "en"
ENV_VAR = "HDL_LANG"

_current = DEFAULT_LANGUAGE
_override: str | None = None  # the language requested on the command line


def normalize(value: str | None) -> str | None:
    """`es_MX.UTF-8` → `es`; None if it is not a supported language."""
    if not value:
        return None
    code = value.strip().lower().replace("-", "_").split("_")[0].split(".")[0]
    return code if code in SUPPORTED else None


def _unsupported(value: object) -> str:
    from .messages import t

    return t("lang.error.unsupported", value=repr(value), options=", ".join(SUPPORTED))


def get_language() -> str:
    return _current


def set_language(lang: str) -> str:
    """Sets the session language; `ValueError` if it is not supported."""
    global _current
    code = normalize(lang)
    if code is None:
        raise ValueError(_unsupported(lang))
    _current = code
    return code


def set_override(lang: str | None) -> None:
    """Remembers the language requested with `--lang`, so that it also wins when the interface
    (which resolves it again at startup) is opened from the same process."""
    global _override
    _override = None if lang is None else resolve_language(lang)


def _macos_language() -> str | None:
    """The user's preferred language on macOS.

    An application launched from Finder does not receive `LANG`: the global preference
    (`AppleLanguages`, the ordered list of languages) is consulted. No shell, with a timeout.
    """
    if sys.platform != "darwin":
        return None
    try:
        result = subprocess.run(
            ["/usr/bin/defaults", "read", "-g", "AppleLanguages"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    # Output: «(\n    "es-MX",\n    "en-US"\n)». The first supported one is used.
    for item in result.stdout.replace("(", " ").replace(")", " ").split(","):
        code = normalize(item.strip().strip('"'))
        if code:
            return code
        if item.strip().strip('"'):
            return None  # the preferred language is not supported: the default is used
    return None


def system_language() -> str | None:
    for var in ("LC_ALL", "LC_MESSAGES", "LANG"):
        code = normalize(os.environ.get(var))
        if code:
            return code
    try:
        code = normalize(locale.getlocale()[0])
    except (ValueError, TypeError):
        code = None
    return code or _macos_language()


def resolve_language(
    cli: str | None = None,
    *,
    config: str | None = None,
    environ: Mapping[str, str] | None = None,
) -> str:
    """Priority: `--lang` argument > `HDL_LANG` > `config.toml` > system > default.

    An unsupported value at one level is ignored and the next is tried, except `cli`,
    which is a usage error (`ValueError`).
    """
    cli = cli or _override
    if cli:
        code = normalize(cli)
        if code is None:
            raise ValueError(_unsupported(cli))
        return code
    env = os.environ if environ is None else environ
    return normalize(env.get(ENV_VAR)) or normalize(config) or system_language() or DEFAULT_LANGUAGE


def apply_language(cli: str | None = None, *, config: str | None = None) -> str:
    """Decides the language with `resolve_language`'s priority and makes it active.

    If `config` is None it reads `config.toml` (an unreadable file is ignored here; whoever
    loads it already reports the error).
    """
    if config is None:
        from ..core.config import ConfigError, load_config

        try:
            config = load_config().general.language
        except ConfigError:
            config = ""
    return set_language(resolve_language(cli, config=config))
