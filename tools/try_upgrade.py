"""Tries to upgrade the locked dependencies and keeps the result only if QA stays green.

python tools/try_upgrade.py [--package NAME ...]

Backs up `pyproject.toml` and `uv.lock` (copies in a temporary folder), runs `uv lock
--upgrade` (or `--upgrade-package` for each named package), moves the Flet pins in
`[tool.flet.*]` to the newly locked version, syncs and runs QA. If any step fails, both files are
restored, the environment is synced back and the failing step is reported (exit 1).
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FILES = ("pyproject.toml", "uv.lock")
# Packages whose change needs a rebuilt app and a visual check.
APP_PACKAGES = ("flet", "flet-cli", "flet-desktop", "pillow")
_FLET_PIN = re.compile(r'(dependencies\s*=\s*\[\s*"flet==)[^"]+(")')


def locked_versions(lock_text: str) -> dict[str, str]:
    """Package name -> locked version, from the text of `uv.lock`."""
    data = tomllib.loads(lock_text)
    return {p["name"]: p["version"] for p in data.get("package", []) if "version" in p}


def rewrite_flet_pin(pyproject_text: str, version: str) -> str:
    """Sets every `flet==X` pin in `[tool.flet.*]` to `version`."""
    return _FLET_PIN.sub(rf"\g<1>{version}\g<2>", pyproject_text)


def changes(before: dict[str, str], after: dict[str, str]) -> list[str]:
    """«name: old -> new» lines, sorted; added and removed packages are marked."""
    lines = []
    for name in sorted(before.keys() | after.keys()):
        old, new = before.get(name), after.get(name)
        if old == new:
            continue
        if old is None:
            lines.append(f"{name}: (new) -> {new}")
        elif new is None:
            lines.append(f"{name}: {old} -> (removed)")
        else:
            lines.append(f"{name}: {old} -> {new}")
    return lines


def needs_app_build(before: dict[str, str], after: dict[str, str]) -> bool:
    return any(before.get(name) != after.get(name) for name in APP_PACKAGES)


def lock_command(packages: list[str]) -> list[str]:
    if not packages:
        return ["uv", "lock", "--upgrade"]
    command = ["uv", "lock"]
    for name in packages:
        command += ["--upgrade-package", name]
    return command


def run(step: str, command: list[str], env: dict[str, str] | None = None) -> str | None:
    """Runs one step; returns `None` if it passed or the tail of its output if it failed."""
    print(f"==> {step}: {' '.join(command)}", flush=True)
    done = subprocess.run(
        command,
        cwd=REPO,
        capture_output=True,
        text=True,
        env={**os.environ, **(env or {})},
        check=False,
    )
    if done.returncode == 0:
        return None
    tail = "\n".join((done.stdout + done.stderr).strip().splitlines()[-40:])
    return tail or f"exit code {done.returncode}"


def restore(backup: Path) -> None:
    for name in FILES:
        shutil.copy2(backup / name, REPO / name)
    run("restore sync", ["uv", "sync"])


def upgrade(packages: list[str]) -> int:
    with tempfile.TemporaryDirectory(prefix="hdl-upgrade-") as folder:
        backup = Path(folder)
        for name in FILES:
            shutil.copy2(REPO / name, backup / name)
        before = locked_versions((backup / "uv.lock").read_text(encoding="utf-8"))

        def fail(step: str, tail: str) -> int:
            restore(backup)
            print(f"\nFAILED at step: {step}. pyproject.toml and uv.lock were restored.\n")
            print(tail)
            return 1

        if tail := run("lock", lock_command(packages)):
            return fail("lock", tail)
        after = locked_versions((REPO / "uv.lock").read_text(encoding="utf-8"))
        pyproject = REPO / "pyproject.toml"
        text = pyproject.read_text(encoding="utf-8")
        if "flet" in after and (pinned := rewrite_flet_pin(text, after["flet"])) != text:
            pyproject.write_text(pinned, encoding="utf-8")
        steps: list[tuple[str, list[str], dict[str, str] | None]] = [
            ("sync", ["uv", "sync"], None),
            ("qa", ["pre-commit", "run", "--all-files"], None),
            (
                "rules and integration",
                ["uv", "run", "pytest", "tests/rules", "tests/integration", "-q", "--no-cov"],
                {"HDL_REQUIRE_RULE_ENGINE": "1"},
            ),
        ]
        for step, command, env in steps:
            if tail := run(step, command, env):
                return fail(step, tail)
    summary = changes(before, after)
    print("\nGreen. Version changes:" if summary else "\nGreen. Nothing changed.")
    for line in summary:
        print(f"  {line}")
    if needs_app_build(before, after):
        print("\nFlet or pillow changed: run `make app` and check the app and the DMG by eye.")
    if summary:
        print("Add a CHANGELOG.md entry for the dependency upgrade.")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Upgrade the locked dependencies, safely.")
    parser.add_argument("--package", action="append", default=[], metavar="NAME")
    return upgrade(parser.parse_args(argv).package)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
