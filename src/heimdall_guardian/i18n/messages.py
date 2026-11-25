"""Visible messages per language: `t("ui.welcome.title")`.

English is the source: each key is born in `messages_en` and translated in `messages_es`
(same keys and same `{name}` placeholders). If the translation is missing, English is
used and, if the key does not exist either, the key itself is returned.

What is stored (limitations, a tool's detail, verdict criteria) does not carry the
already-written text but a structured message, `msg("key", data=...)`, which `render`
converts to the current language every time it is shown. That way a regenerated report
or the interface speak today's language and not that of when the analysis was done.
"""

from __future__ import annotations

import string
from typing import Any

from . import messages_en, messages_es
from .languages import BASE_LANGUAGE, get_language

CATALOGS: dict[str, dict[str, str]] = {"en": messages_en.MESSAGES, "es": messages_es.MESSAGES}


def placeholders(text: str) -> set[str]:
    """Names of the `{name}` placeholders in a message."""
    return {name for _, name, _, _ in string.Formatter().parse(text) if name}


def has_message(key: str) -> bool:
    return key in CATALOGS[BASE_LANGUAGE]


def t(key: str, /, lang: str | None = None, **params: object) -> str:
    """The message `key` in `lang` (by default, the current language)."""
    text = CATALOGS.get(lang or get_language(), {}).get(key)
    if text is None:
        text = CATALOGS[BASE_LANGUAGE].get(key)
    if text is None:
        return key
    return text.format(**params) if params else text


def tn(key: str, count: int, /, lang: str | None = None, **params: object) -> str:
    """Message with singular/plural: uses `key.one` if `count` is 1 and `key.other` otherwise.

    `{count}` is available as a placeholder.
    """
    form = "one" if count == 1 else "other"
    return t(f"{key}.{form}", lang, count=count, **params)


class Message(dict[str, Any]):
    """A structured message: `{"code": key, "params": {data}}`.

    It is a dictionary (stored as is in JSON), but when converted to text, for
    example inside an f-string, it is shown in the current language.
    """

    __slots__ = ()

    def __str__(self) -> str:
        return render(self)


def msg(code: str, /, **params: object) -> Message:
    """A message to store. The params are only data: never already-translated text."""
    return Message(code=code, params=params)


def is_message(item: object) -> bool:
    return isinstance(item, dict) and isinstance(item.get("code"), str)


def _param(value: object, lang: str | None) -> object:
    if is_message(value):
        return render(value, lang)
    if isinstance(value, list | tuple):
        # A list of messages are sentences (joined with "; "); one of data, names or paths.
        separator = "; " if value and all(is_message(item) for item in value) else ", "
        return separator.join(str(_param(item, lang)) for item in value)
    return value


def render(item: object, lang: str | None = None) -> str:
    """The text of a stored message in `lang` (by default, the current language).

    It accepts a structured message, loose text (what a tool or a model writes, shown
    as is) or `None`. A param that is another message is rendered; a list of data is
    joined with commas and a list of messages with semicolons. With a `count` param it
    uses the `.one`/`.other` form if the catalog has it.
    """
    if item is None:
        return ""
    if not is_message(item):
        return str(item)
    assert isinstance(item, dict)  # noqa: S101 - for the type checker
    code = str(item["code"])
    params = {name: _param(value, lang) for name, value in (item.get("params") or {}).items()}
    if "count" in params and has_message(f"{code}.other"):
        count = params.pop("count")
        return tn(code, int(str(count)), lang, **params)
    return t(code, lang, **params)


def texts_of(**fields: object) -> dict[str, dict[str, str]]:
    """A finding's texts in every language: `{"en": {"title": ...}, "es": {...}}`.

    Each value is a message (`msg(...)`) or loose text, which comes out the same in every
    language. It is what `Finding.texts` stores.
    """
    return {
        lang: {name: render(value, lang).strip() for name, value in fields.items()}
        for lang in CATALOGS
    }


def text_of(item: Any, field: str, lang: str | None = None) -> str:
    """The text `field` ("title", "description", "recommendation") of a finding.

    `item` is a `Finding` or its dictionary. It looks in `texts` for the requested language
    (by default, the current one), then English, and finally the plain field, which holds
    the English or the text exactly as an external tool wrote it.
    """
    if isinstance(item, dict):
        texts, plain = item.get("texts"), item.get(field)
    else:
        texts, plain = getattr(item, "texts", None), getattr(item, field, "")
    for code in (lang or get_language(), BASE_LANGUAGE):
        value = ((texts or {}).get(code) or {}).get(field)
        if value:
            return str(value)
    return str(plain or "")
