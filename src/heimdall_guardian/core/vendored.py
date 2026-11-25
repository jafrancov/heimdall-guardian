"""Libraries copied into the project ("vendored"), recognized by their version header.

Pure logic: it only reads the first bytes of text files under the analyzed folder (P1, P2: the
files are never executed). A recognized file is reported against the local vulnerability
database as the library it is, and its own code is not scanned by the SAST rules, since it is
third-party code and not the vendor's.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

# How much of each file is read: banners sit at the top of JS files; PHP classes declare their
# version a bit further down.
HEAD_BYTES = {".js": 64 * 1024, ".php": 512 * 1024}

_VERSION = r"(\d+\.\d+\.\d+)"


@dataclass(frozen=True)
class VendoredLibrary:
    file: str  # relative posix path
    name: str  # display name, e.g. "jQuery"
    ecosystem: str  # "npm" | "Packagist"
    package: str  # name in the ecosystem, e.g. "phpmailer/phpmailer"
    version: str

    def to_dict(self) -> dict[str, str]:
        return {
            "file": self.file,
            "name": self.name,
            "ecosystem": self.ecosystem,
            "package": self.package,
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VendoredLibrary:
        return cls(
            file=str(data["file"]),
            name=str(data["name"]),
            ecosystem=str(data["ecosystem"]),
            package=str(data["package"]),
            version=str(data["version"]),
        )


@dataclass(frozen=True)
class Signature:
    name: str
    ecosystem: str
    package: str
    suffix: str  # ".js" or ".php"
    versions: tuple[re.Pattern[str], ...]  # each with one group; the first that matches wins
    marker: re.Pattern[str] | None = None  # must also appear in the head
    filename: re.Pattern[str] | None = None  # must match the file's base name


def _rx(pattern: str, flags: int = 0) -> re.Pattern[str]:
    return re.compile(pattern, flags)


# Strict on purpose: a banner at the start of a comment, never a loose mention of the name.
LIBRARIES: tuple[Signature, ...] = (
    # "/*! jQuery v2.1.1 | ..." and " * jQuery JavaScript Library v1.11.1". "jQuery UI",
    # "jQuery Migrate" and other plugins do not have "v" right after "jQuery".
    Signature(
        "jQuery",
        "npm",
        "jquery",
        ".js",
        (_rx(r"/\*[!*]?[\s*]*jQuery (?:JavaScript Library )?v" + _VERSION),),
    ),
    # "/*! jQuery UI - v1.10.4 - 2014-01-17"
    Signature(
        "jQuery UI",
        "npm",
        "jquery-ui",
        ".js",
        (_rx(r"/\*[!*]?[\s*]*jQuery UI - v" + _VERSION),),
    ),
    # "/*! DataTables 1.10.4" (minified) or "@summary DataTables" ... "@version 1.10.4".
    # "Buttons for DataTables" and the other extensions do not start with the name.
    Signature(
        "DataTables",
        "npm",
        "datatables.net",
        ".js",
        (
            _rx(r"/\*[!*]?[\s*]*DataTables " + _VERSION),
            _rx(r"@summary\s+DataTables\s*\n[\s\S]{0,300}?@version\s+" + _VERSION),
        ),
    ),
    # "Highcharts JS v4.0.4 (2014-09-02)" in the license comment.
    Signature(
        "Highcharts",
        "npm",
        "highcharts",
        ".js",
        (_rx(r"(?:@license|/\*[!*]?)[\s*]*Highcharts JS v" + _VERSION),),
    ),
    # "* Bootstrap v3.3.7 (...)"; the 3.x plugin files say "* Bootstrap: modal.js v3.3.7".
    Signature(
        "Bootstrap",
        "npm",
        "bootstrap",
        ".js",
        (_rx(r"\*[\s*]*Bootstrap(?::\s*[\w.-]+\.js)? v" + _VERSION),),
    ),
    # "//! moment.js" on its own line, then "//! version : 2.10.3". moment-timezone and the
    # locale files do not have that first line.
    Signature(
        "Moment.js",
        "npm",
        "moment",
        ".js",
        (_rx(r"^//!\s*version\s*:\s*" + _VERSION, re.M),),
        marker=_rx(r"^//!\s*moment\.js\s*$", re.M),
    ),
    # "@license Lodash <https://lodash.com/>" followed by `var VERSION = '4.17.4'`.
    Signature(
        "Lodash",
        "npm",
        "lodash",
        ".js",
        (_rx(r"\bVERSION\s*=\s*[\"']" + _VERSION + r"[\"']"),),
        marker=_rx(r"/\*[!*]?[\s*]*(?:@license[\s*]*)?[Ll]odash\b"),
    ),
    # "elFinder - file manager for web" and, a line below, "Version 2.1.57".
    Signature(
        "elFinder",
        "Packagist",
        "studio-42/elfinder",
        ".js",
        (_rx(r"elFinder - file manager for web[\s\S]{0,200}?\bVersion " + _VERSION),),
    ),
    # 5.x: `public $Version = '5.2.9';` (class.phpmailer.php); 6.x: `const VERSION = '6.5.0';`.
    Signature(
        "PHPMailer",
        "Packagist",
        "phpmailer/phpmailer",
        ".php",
        (_rx(r"(?:public\s+\$Version|\bconst\s+VERSION)\s*=\s*[\"']" + _VERSION + r"[\"']"),),
        marker=_rx(r"\bclass\s+PHPMailer\b"),
        filename=_rx(r"^(?:class\.)?phpmailer\.php$", re.I),
    ),
    # PHPExcel.php: "@version 1.8.0, 2014-03-02" in the file's docblock.
    Signature(
        "PHPExcel",
        "Packagist",
        "phpoffice/phpexcel",
        ".php",
        (_rx(r"@version\s+" + _VERSION),),
        marker=_rx(r"\bclass\s+PHPExcel\b"),
        filename=_rx(r"^phpexcel\.php$", re.I),
    ),
    # 1.7 and 1.82: `define('FPDF_VERSION','1.82')`; 1.84 and later: `const VERSION = '1.84';`.
    Signature(
        "FPDF",
        "Packagist",
        "setasign/fpdf",
        ".php",
        (
            _rx(r"define\(\s*[\"']FPDF_VERSION[\"']\s*,\s*[\"'](\d+\.\d+(?:\.\d+)?)[\"']"),
            _rx(r"\bconst\s+VERSION\s*=\s*[\"'](\d+\.\d+(?:\.\d+)?)[\"']"),
        ),
        marker=_rx(r"\bclass\s+FPDF\b"),
        filename=_rx(r"^fpdf\.php$", re.I),
    ),
    # tcpdf.php: `$tcpdf_version = '6.2.13';`
    Signature(
        "TCPDF",
        "Packagist",
        "tecnickcom/tcpdf",
        ".php",
        (_rx(r"\$tcpdf_version\s*=\s*[\"']" + _VERSION + r"[\"']"),),
        marker=_rx(r"\bclass\s+TCPDF\b"),
        filename=_rx(r"^tcpdf\.php$", re.I),
    ),
    # nusoap.php: `var $version = '0.9.5';` in class nusoap_base.
    Signature(
        "NuSOAP",
        "Packagist",
        "econea/nusoap",
        ".php",
        (_rx(r"\$version\s*=\s*[\"']" + _VERSION + r"[\"']"),),
        marker=_rx(r"\bclass\s+nusoap_base\b"),
        filename=_rx(r"^nusoap\.php$", re.I),
    ),
)

_SUFFIXES = frozenset(sig.suffix for sig in LIBRARIES)


def _read_head(path: Path, size: int) -> str:
    try:
        with path.open("rb") as handle:
            return handle.read(size).decode("utf-8", errors="ignore")
    except OSError:
        return ""


def _may_match(base_name: str, suffix: str) -> bool:
    """Cheap check before reading: some signature fits this extension and file name."""
    return any(
        sig.suffix == suffix and (sig.filename is None or sig.filename.search(base_name))
        for sig in LIBRARIES
    )


def recognize(head: str, base_name: str, suffix: str) -> tuple[Signature, str] | None:
    """The first signature that matches this file head, with the version it declares."""
    for sig in LIBRARIES:
        if sig.suffix != suffix:
            continue
        if sig.filename is not None and not sig.filename.search(base_name):
            continue
        if sig.marker is not None and not sig.marker.search(head):
            continue
        for pattern in sig.versions:
            found = pattern.search(head)
            if found:
                return sig, found.group(1)
    return None


def detect(root: Path, files: Iterable[str]) -> tuple[VendoredLibrary, ...]:
    """Libraries copied into the tree, one per file, sorted by file."""
    found: list[VendoredLibrary] = []
    for relative in files:
        posix = PurePosixPath(relative)
        suffix = posix.suffix.lower()
        if suffix not in _SUFFIXES:
            continue
        if not _may_match(posix.name, suffix):
            continue
        path = root / relative
        if path.is_symlink():
            continue
        head = _read_head(path, HEAD_BYTES[suffix])
        if not head:
            continue
        match = recognize(head, posix.name, suffix)
        if match is not None:
            sig, version = match
            found.append(
                VendoredLibrary(
                    file=relative,
                    name=sig.name,
                    ecosystem=sig.ecosystem,
                    package=sig.package,
                    version=version,
                )
            )
    return tuple(sorted(found, key=lambda lib: lib.file))
