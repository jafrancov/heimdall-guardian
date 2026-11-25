"""AUTHZ module adapter: endpoint inventory and its findings."""

from __future__ import annotations

from typing import Protocol

from .. import __version__
from ..adapters.base import Adapter, AdapterResult, ScanContext
from ..core.detector import Stack
from ..core.endpoints import ANY_METHOD, Endpoint
from ..core.files import read_lines
from ..core.finding import Category, Confidence, Finding, Severity
from ..core.fingerprint import fingerprint
from ..core.masking import mask_generic
from ..core.profiles import Module
from ..i18n import Message, msg, texts_of
from .django import DjangoExtractor
from .dotnet import DotnetExtractor
from .laravel import LaravelExtractor
from .node import NodeExtractor
from .php import PhpExtractor

RULE_WRITE = "AUTHZ-001"
RULE_READ = "AUTHZ-002"


class _Extractor(Protocol):
    notes: list[Message]

    def extract(self) -> list[Endpoint]: ...


def _finding(endpoint: Endpoint, ctx: ScanContext) -> Finding:
    rule_id = RULE_WRITE if endpoint.writes else RULE_READ
    kind = msg("authz.kind.write" if endpoint.writes else "authz.kind.read")
    # The fingerprint uses the methods as they are («*» = any): it does not depend on the language.
    route = f"{endpoint.methods_key} {endpoint.path}"
    methods = msg("report.any_method") if endpoint.methods == [ANY_METHOD] else endpoint.methods
    declared = (
        msg("authz.finding.declared_in", file=endpoint.route_file)
        if endpoint.route_file and endpoint.route_file != endpoint.file
        else ""
    )
    note: Message | str = ""
    if endpoint.public_by_design:
        note = msg("authz.finding.note_public")
    elif endpoint.methods == [ANY_METHOD]:
        note = msg("authz.finding.note_any_method")
    texts = texts_of(
        title=msg(
            "authz.finding.title",
            kind=kind,
            route=msg("authz.route", methods=methods, path=endpoint.path),
        ),
        description=msg(
            "authz.finding.description",
            kind=kind,
            path=endpoint.path,
            methods=methods,
            handler=endpoint.handler,
            evidence=endpoint.evidence,
            declared=declared,
            note=note,
        ),
        recommendation=msg("authz.finding.recommendation"),
    )
    return Finding(
        # The fingerprint uses methods, route and handler: it survives the code being moved.
        fingerprint=fingerprint(rule_id, endpoint.file, f"{route} {endpoint.handler}"),
        source="authz",
        rule_id=rule_id,
        category=Category.ACCESS_CONTROL,
        severity=Severity.CRITICAL if endpoint.writes else Severity.HIGH,
        confidence=Confidence.LOW if endpoint.public_by_design else Confidence.MEDIUM,
        file=endpoint.file,
        line_start=endpoint.line,
        line_end=endpoint.line,
        snippet=mask_generic(read_lines(ctx.root, endpoint.file, endpoint.line, endpoint.line)),
        texts=texts,
        owasp="A01:2025 Broken Access Control",
        cwe="CWE-306",
        module=Module.AUTHZ,
    )


class AuthzAdapter(Adapter):
    """Own route extractors; they do not depend on any external tool."""

    name = "authz"
    modules = frozenset({Module.AUTHZ})

    def is_available(self) -> bool:
        return True

    def version(self) -> str | None:
        return __version__

    def _extractors(self, ctx: ScanContext) -> list[_Extractor]:
        extractors: list[_Extractor] = []
        if Stack.DJANGO in ctx.stacks:
            extractors.append(DjangoExtractor(ctx.root, ctx.files))
        if Stack.DOTNET in ctx.stacks:
            extractors.append(DotnetExtractor(ctx.root, ctx.files))
        if Stack.LARAVEL in ctx.stacks:
            extractors.append(LaravelExtractor(ctx.root, ctx.files))
        elif Stack.PHP in ctx.stacks:
            extractors.append(PhpExtractor(ctx.root, ctx.files))
        if Stack.NODE in ctx.stacks or Stack.TYPESCRIPT in ctx.stacks:
            extractors.append(NodeExtractor(ctx.root, ctx.files))
        return extractors

    def invoke(self, ctx: ScanContext) -> AdapterResult:
        result = AdapterResult()
        for extractor in self._extractors(ctx):
            try:
                result.endpoints += extractor.extract()
            except Exception as exc:
                # An extractor that stumbles must not bring down the run or the other extractors.
                name = type(extractor).__name__.removesuffix("Extractor")
                result.limitations.append(
                    msg("authz.limit.extractor_failed", name=name, error=type(exc).__name__)
                )
            result.limitations += extractor.notes
        unknown = sum(1 for e in result.endpoints if e.has_auth is None)
        if unknown:
            result.limitations.append(msg("authz.limit.undetermined", count=unknown))
        result.findings = [_finding(e, ctx) for e in result.endpoints if e.has_auth is False]
        return result
