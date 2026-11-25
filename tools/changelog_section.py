"""Prints the CHANGELOG.md section of one version (used as the release notes).

python tools/changelog_section.py 0.41.0
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

CHANGELOG = Path(__file__).resolve().parent.parent / "CHANGELOG.md"


def section(text: str, version: str) -> str | None:
    """The body under `## [version]` up to the next `## [` heading, or None."""
    version = version.lstrip("vV")
    heading = re.compile(rf"^## \[{re.escape(version)}\]", re.MULTILINE)
    match = heading.search(text)
    if match is None:
        return None
    rest = text[match.start() :]
    following = re.search(r"^## \[", rest[3:], re.MULTILINE)
    end = following.start() + 3 if following else len(rest)
    body = rest[:end]
    # Drop the trailing link-reference block of Keep a Changelog, if the last section has it.
    body = re.split(r"^\[[^\]]+\]: \S+\s*$", body, maxsplit=1, flags=re.MULTILINE)[0]
    return body.strip() + "\n"


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: changelog_section.py VERSION", file=sys.stderr)
        return 2
    found = section(CHANGELOG.read_text(encoding="utf-8"), argv[1])
    if found is None:
        print(f"no CHANGELOG entry for {argv[1]}", file=sys.stderr)
        return 1
    sys.stdout.write(found)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
