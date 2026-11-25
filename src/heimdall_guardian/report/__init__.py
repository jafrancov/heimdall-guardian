"""Report generators from the normalized result of a run."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from ..core.owasp import migrate_payload
from ..i18n import t
from .html import render_html
from .pdf import write_pdf
from .sarif import render_sarif
from .xlsx import write_xlsx

Payload = dict[str, Any]


def _write_text(render: Callable[[Payload], str]) -> Callable[[Payload, Path], None]:
    def write(payload: Payload, path: Path) -> None:
        path.write_text(render(payload), encoding="utf-8")

    return write


def _json(payload: Payload) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def _sarif(payload: Payload) -> str:
    return json.dumps(render_sarif(payload), ensure_ascii=False, indent=2) + "\n"


WRITERS: dict[str, Callable[[Payload, Path], None]] = {
    ".json": _write_text(_json),
    ".html": _write_text(render_html),
    ".sarif": _write_text(_sarif),
    ".xlsx": write_xlsx,
    ".pdf": write_pdf,
}
SBOM_SUFFIX = ".cdx.json"


def write_report(payload: Payload, path: Path) -> None:
    """Writes the report in the format given by the file extension.

    The text comes out in the current language (`get_language()`), even if the run was
    saved in another: what is stored are messages and codes, not drafted text.

    `*.cdx.json` writes only the component inventory (SBOM, CycloneDX).
    """
    payload = migrate_payload(payload)  # runs saved with OWASP 2021 labels
    if path.name.lower().endswith(SBOM_SUFFIX):
        if not payload.get("sbom"):
            raise ValueError(t("report.error.no_sbom"))
        path.write_text(_json(payload["sbom"]), encoding="utf-8")
        return
    try:
        writer = WRITERS[path.suffix.lower()]
    except KeyError:
        valid = ", ".join([*WRITERS, SBOM_SUFFIX])
        raise ValueError(
            t("report.error.unsupported_format", name=path.name, valid=valid)
        ) from None
    writer(payload, path)
