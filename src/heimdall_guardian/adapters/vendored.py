"""Libraries copied into the project: known vulnerabilities from the local OSV database.

A copied `jquery-2.1.1.min.js` is in no lockfile, so the dependency tools never see it. The
recognition (`core/vendored.py`) reads its version header; this adapter writes a synthetic
lockfile with the recognized (package, version) pairs in the run's temporary directory (never
in the analyzed folder, P1), scans it with the same OSV-Scanner and the same offline database
as `OsvAdapter`, and reports each vulnerability against every file that holds that library.
"""

from __future__ import annotations

import json
from pathlib import Path

from ..core.finding import Finding
from ..core.profiles import Module
from ..core.vendored import VendoredLibrary
from ..i18n import msg
from .base import AdapterResult, ScanContext
from .osv import OsvAdapter, dependency_finding, vulnerabilities

_DIRECTORY = "vendored"


def write_lockfiles(libraries: tuple[VendoredLibrary, ...], target: Path) -> list[str]:
    """Writes the synthetic lockfiles for `libraries` into `target`; returns their names.

    Each distinct (package, version) is one entry. In `package-lock.json` every npm entry has
    its own nested path, so several versions of the same package can coexist.
    """
    target.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    npm = sorted({(lib.package, lib.version) for lib in libraries if lib.ecosystem == "npm"})
    if npm:
        packages: dict[str, dict[str, str]] = {"": {"name": "hdl-vendored"}}
        for number, (package, version) in enumerate(npm):
            # Without `resolved` the scanner treats the entry as a local link and skips it.
            # The address is never fetched: the scan is always offline.
            packages[f"node_modules/hdl-vendored-{number}/node_modules/{package}"] = {
                "version": version,
                "resolved": f"https://registry.npmjs.org/{package}/-/{package}-{version}.tgz",
            }
        lock = {"name": "hdl-vendored", "lockfileVersion": 3, "packages": packages}
        (target / "package-lock.json").write_text(json.dumps(lock, indent=1), encoding="utf-8")
        written.append("package-lock.json")
    composer = sorted(
        {(lib.package, lib.version) for lib in libraries if lib.ecosystem == "Packagist"}
    )
    if composer:
        lock = {
            "packages": [{"name": name, "version": version} for name, version in composer],
            "packages-dev": [],
        }
        (target / "composer.lock").write_text(json.dumps(lock, indent=1), encoding="utf-8")
        written.append("composer.lock")
    return written


class VendoredAdapter(OsvAdapter):
    name = "vendored"
    modules = frozenset({Module.DEP})

    def applies(self, ctx: ScanContext) -> bool:
        return Module.DEP in ctx.modules and bool(ctx.vendored)

    def invoke(self, ctx: ScanContext) -> AdapterResult:
        target = ctx.workdir / _DIRECTORY
        write_lockfiles(ctx.vendored, target)
        data = self._scan(ctx, target)
        if data is None:
            return AdapterResult()
        holders: dict[tuple[str, str], list[VendoredLibrary]] = {}
        for lib in ctx.vendored:
            holders.setdefault((lib.package.lower(), lib.version), []).append(lib)
        findings: list[Finding] = []
        for item in vulnerabilities(data):
            recommendation = (
                msg("adapter.vendored.rec_fixed", package=item.name, versions=item.fixed)
                if item.fixed
                else msg("adapter.vendored.rec_no_fix", package=item.name)
            )
            for lib in holders.get((item.name.lower(), item.installed), ()):
                findings.append(
                    dependency_finding(
                        item, lib.file, source=self.name, recommendation=recommendation
                    )
                )
        return AdapterResult(findings=findings)
