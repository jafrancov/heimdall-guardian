"""Bandit: Python SAST. Used as a library; it only reads the AST and runs nothing."""

from __future__ import annotations

import importlib.util
import re
from importlib import metadata
from pathlib import Path

from ..core import severity
from ..core.files import read_lines
from ..core.finding import Category, Confidence, Finding
from ..core.fingerprint import fingerprint
from ..core.masking import mask_generic, mask_secret
from ..core.profiles import Module
from ..i18n import msg, texts_of
from .base import Adapter, AdapterError, AdapterResult, ScanContext

# B105-B107 quote the password they found inside the message itself.
_QUOTED_PASSWORD = re.compile(r"(?s)^(Possible hardcoded password: )'(.*)'$")

_A01 = "A01:2025 Broken Access Control"
_A02 = "A02:2025 Security Misconfiguration"
_A04 = "A04:2025 Cryptographic Failures"
_A05 = "A05:2025 Injection"
_A06 = "A06:2025 Insecure Design"
_A07 = "A07:2025 Authentication Failures"
_A08 = "A08:2025 Software or Data Integrity Failures"
_A10 = "A10:2025 Mishandling of Exceptional Conditions"

# OWASP Top 10:2025 category per CWE that Bandit reports (bandit.core.issue.Cwe), kept
# consistent with the own rules (e.g. CWE-295 is A04 there as well). A CWE that is not
# listed leaves the finding without a category rather than guessing one.
OWASP_BY_CWE: dict[int, str] = {
    20: _A05,
    22: _A01,
    78: _A05,
    79: _A05,
    80: _A05,
    89: _A05,
    94: _A05,
    155: _A05,
    259: _A07,
    284: _A01,
    295: _A04,
    319: _A04,
    326: _A04,
    327: _A04,
    330: _A04,
    377: _A02,
    400: _A06,
    494: _A08,
    502: _A08,
    605: _A02,
    703: _A10,
    732: _A01,
    838: _A05,
}

_CONFIDENCE = {"HIGH": Confidence.HIGH, "MEDIUM": Confidence.MEDIUM, "LOW": Confidence.LOW}


class BanditAdapter(Adapter):
    name = "bandit"
    modules = frozenset({Module.SAST})

    def is_available(self) -> bool:
        return importlib.util.find_spec("bandit") is not None

    def version(self) -> str | None:
        try:
            return metadata.version("bandit")
        except metadata.PackageNotFoundError:
            return None

    @staticmethod
    def _targets(ctx: ScanContext) -> list[str]:
        """Relative paths of the Python files Bandit should read."""
        return [
            path
            for path in ctx.files
            if path.endswith(".py") and not ctx.exclusions.excludes(path, sast=True)
        ]

    def applies(self, ctx: ScanContext) -> bool:
        # Without Python code the step is not run at all (no progress row, no ToolRun).
        return super().applies(ctx) and bool(self._targets(ctx))

    def invoke(self, ctx: ScanContext) -> AdapterResult:
        targets = [str(ctx.root / path) for path in self._targets(ctx)]
        if not targets:
            return AdapterResult()

        from bandit.core import config as bandit_config
        from bandit.core import docs_utils
        from bandit.core import manager as bandit_manager

        try:
            # ignore_nosec: the `# nosec` comments in the analyzed code do not count.
            manager = bandit_manager.BanditManager(
                bandit_config.BanditConfig(), "file", ignore_nosec=True
            )
            manager.discover_files(targets, recursive=False)
            manager.run_tests()
            issues = manager.get_issue_list()
        except Exception as exc:  # the library does not define its own base exception
            raise AdapterError("adapter.failed", tool="bandit", detail=str(exc)) from exc

        result = AdapterResult()
        for issue in issues:
            text = str(issue.text)
            quoted = _QUOTED_PASSWORD.match(text)
            if quoted:
                result.secrets.add(quoted[2])
                text = f"{quoted[1]}'{mask_secret(quoted[2])}'"
            file = Path(issue.fname).relative_to(ctx.root).as_posix()
            lines = [int(n) for n in (issue.linerange or [issue.lineno])]
            start, end = min(lines), max(lines)
            snippet = read_lines(ctx.root, file, start, end)
            cwe_id = getattr(issue.cwe, "id", None)
            result.findings.append(
                Finding(
                    fingerprint=fingerprint(issue.test_id, file, snippet),
                    source="bandit",
                    rule_id=issue.test_id,
                    category=Category.SAST,
                    module=Module.SAST,
                    severity=severity.from_bandit(str(issue.severity), str(issue.confidence)),
                    confidence=_CONFIDENCE.get(str(issue.confidence).upper(), Confidence.MEDIUM),
                    file=file,
                    line_start=start,
                    line_end=end,
                    snippet=mask_generic(snippet),
                    # Bandit writes the title and the message: they are shown as they are.
                    title=f"Bandit {issue.test_id}: {issue.test}",
                    description=text,
                    texts=texts_of(recommendation=msg("adapter.bandit.recommendation")),
                    cwe=f"CWE-{cwe_id}" if cwe_id else None,
                    owasp=OWASP_BY_CWE.get(cwe_id) if cwe_id else None,
                    references=[docs_utils.get_url(issue.test_id)],
                )
            )
        return result
