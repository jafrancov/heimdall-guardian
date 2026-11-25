"""One report of what is out of date: Python packages, pinned tools and GitHub Actions.

python tools/check_outdated.py [--strict]

It informs and changes nothing. The exit code is 0 unless `--strict` is given and
something is outdated (then 1). If the network fails, it says so and still exits 0.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tomllib
from collections.abc import Callable
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from heimdall_guardian.adapters import updates  # noqa: E402

Fetch = Callable[[str], Any]
# `tools.toml` section name -> key in `updates.SOURCES`.
TOOL_SOURCE = {"osv-scanner": "osv"}
_USES = re.compile(r"^\s*-?\s*uses:\s*([\w.-]+/[\w.-]+)(/[\w./-]+)?@(\S+)(?:\s*#\s*(\S+))?", re.M)
_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*")


def normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def requirement_name(requirement: str) -> str | None:
    """«flet[all]>=1.0.4» -> «flet»."""
    match = _NAME.match(requirement.strip())
    return normalize(match.group(0)) if match else None


def direct_dependencies(pyproject: dict[str, Any]) -> dict[str, str]:
    """Normalized name -> where it is declared (project, ui extra, dev group...)."""
    found: dict[str, str] = {}
    sources: list[tuple[str, list[str]]] = [
        ("project", pyproject["project"].get("dependencies", []))
    ]
    for extra, items in pyproject["project"].get("optional-dependencies", {}).items():
        sources.append((f"extra {extra}", items))
    for group, items in pyproject.get("dependency-groups", {}).items():
        sources.append((f"group {group}", [i for i in items if isinstance(i, str)]))
    for where, items in sources:
        for item in items:
            name = requirement_name(item)
            if name:
                found.setdefault(name, where)
    return found


def major(version: str) -> int:
    parsed = updates.parse_version(version)
    return parsed[0] if parsed else 0


def jump(current: str, latest: str) -> str:
    return "MAJOR" if major(latest) > major(current) else ""


def parse_pip_outdated(text: str, direct: dict[str, str]) -> list[dict[str, str]]:
    """Rows for the direct dependencies out of `uv pip list --outdated --format json`."""
    rows = []
    for item in json.loads(text):
        name = normalize(item["name"])
        if name in direct:
            rows.append(
                {
                    "name": name,
                    "where": direct[name],
                    "current": item["version"],
                    "latest": item["latest_version"],
                    "jump": jump(item["version"], item["latest_version"]),
                }
            )
    return sorted(rows, key=lambda row: row["name"])


def python_report(direct: dict[str, str]) -> tuple[list[dict[str, str]], str]:
    """(rows, error). An empty error means the query worked."""
    try:
        done = subprocess.run(
            ["uv", "pip", "list", "--outdated", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=REPO,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return [], str(exc)
    if done.returncode != 0:
        return [], (done.stderr.strip().splitlines() or ["uv failed"])[-1]
    try:
        return parse_pip_outdated(done.stdout, direct), ""
    except (ValueError, KeyError, TypeError) as exc:
        return [], f"unexpected uv output ({exc})"


def tool_report(manifest: dict[str, Any], fetch: Fetch) -> list[dict[str, str]]:
    rows = []
    for name, spec in manifest.items():
        source = TOOL_SOURCE.get(name, name)
        if source not in updates.SOURCES:
            continue
        pinned = str(spec.get("version", ""))
        for novelty in updates.check({source: pinned}, fetch):
            rows.append(
                {
                    "name": name,
                    "current": pinned,
                    "latest": novelty.latest or "",
                    "error": novelty.error,
                    "outdated": "yes" if novelty.outdated else "",
                }
            )
    return rows


def parse_actions(texts: list[str]) -> dict[str, str]:
    """«owner/repo» -> the version in use (the comment of a SHA pin, else the ref)."""
    found: dict[str, str] = {}
    for text in texts:
        for match in _USES.finditer(text):
            repo, _, ref, comment = match.groups()
            version = comment if re.fullmatch(r"[0-9a-f]{40}", ref) and comment else ref
            found.setdefault(repo, version)
    return found


def action_report(actions: dict[str, str], fetch: Fetch) -> list[dict[str, str]]:
    rows = []
    for repo, version in sorted(actions.items()):
        row = {"name": repo, "current": version, "latest": "", "error": "", "outdated": ""}
        if not re.fullmatch(r"v?\d+(\.\d+)*", version):
            row["error"] = "not a version tag, skipped"
            rows.append(row)
            continue
        try:
            data = fetch(f"https://api.github.com/repos/{repo}/releases/latest")
            row["latest"] = str(data.get("tag_name") or "")
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
            row["error"] = str(getattr(exc, "reason", "") or exc) or type(exc).__name__
        # Pins carry only the major (`v4`): a newer major is what matters here.
        if row["latest"] and major(row["latest"]) > major(version):
            row["outdated"] = "yes"
        rows.append(row)
    return rows


def render(
    python: tuple[list[dict[str, str]], str],
    tools: list[dict[str, str]],
    actions: list[dict[str, str]],
) -> tuple[str, bool]:
    """The plain-text report and whether anything is outdated."""
    lines = ["== Python packages (direct dependencies) =="]
    rows, error = python
    if error:
        lines.append(f"  could not check (offline?): {error}")
    elif not rows:
        lines.append("  all up to date")
    for row in rows:
        mark = "  <- major jump" if row["jump"] else ""
        lines.append(
            f"  {row['name']:<22} {row['current']:<12} -> {row['latest']:<12} "
            f"({row['where']}){mark}"
        )
    for title, items in (("Pinned tools (tools/tools.toml)", tools), ("GitHub Actions", actions)):
        lines += ["", f"== {title} =="]
        if not items:
            lines.append("  nothing to check")
        for row in items:
            if row["error"]:
                state = f"not checked: {row['error']}"
            elif row["outdated"]:
                state = f"-> {row['latest']}  <- outdated"
            else:
                state = "up to date"
            lines.append(f"  {row['name']:<28} {row['current']:<12} {state}")
    outdated = bool(rows) or any(r["outdated"] for r in [*tools, *actions])
    return "\n".join(lines) + "\n", outdated


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Report outdated dependencies, tools and actions.")
    parser.add_argument("--strict", action="store_true", help="exit 1 if anything is outdated")
    args = parser.parse_args(argv)
    pyproject = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))
    manifest = tomllib.loads((REPO / "tools" / "tools.toml").read_text(encoding="utf-8"))
    workflows = [
        p.read_text(encoding="utf-8")
        for p in sorted((REPO / ".github" / "workflows").glob("*.yml"))
    ]
    text, outdated = render(
        python_report(direct_dependencies(pyproject)),
        tool_report(manifest, updates.fetch_json),
        action_report(parse_actions(workflows), updates.fetch_json),
    )
    sys.stdout.write(text)
    return 1 if args.strict and outdated else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
