"""Utilities shared by the tests."""

from __future__ import annotations

from heimdall_guardian.adapters.base import Adapter, AdapterError, AdapterResult, ScanContext
from heimdall_guardian.core.finding import Category, Confidence, Finding, Severity
from heimdall_guardian.core.fingerprint import fingerprint
from heimdall_guardian.core.profiles import Module


def make_finding(source: str, rule: str, file: str, snippet: str, sev: Severity, **kw) -> Finding:
    return Finding(
        fingerprint=fingerprint(rule, file, snippet),
        source=source,
        rule_id=rule,
        category=kw.pop("category", Category.SAST),
        severity=sev,
        confidence=Confidence.HIGH,
        file=file,
        line_start=1,
        line_end=1,
        snippet=snippet,
        title=rule,
        description="",
        recommendation="",
        **kw,
    )


class FakeAdapter(Adapter):
    modules = frozenset({Module.SEC, Module.DEP, Module.SAST})

    def __init__(self, name, result=None, *, available=True, error=None):
        self.name = name
        self._result = result or AdapterResult()
        self._available = available
        self._error = error
        self.contexts: list[ScanContext] = []

    def is_available(self) -> bool:
        return self._available

    def version(self) -> str | None:
        return "1.0"

    def invoke(self, ctx: ScanContext) -> AdapterResult:
        self.contexts.append(ctx)
        if self._error:
            raise AdapterError(self._error)
        return self._result
