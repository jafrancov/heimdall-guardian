"""Prepares the resources that ship inside the installable application.

Usage:  python tools/build_bundle.py [--no-binaries]

With `--no-binaries` only the rules, legal files and the pin list are copied: that is what the
command-line-only wheel carries (`tools/build_cli_wheel.py`); the tools are downloaded later
with `hdl tools --install`.

Copies the own rules and the binaries from `tools/bin/` (already verified by
`fetch_tools.py`) to `src/heimdall_guardian/_bundle/`, which is not versioned. With that,
the package works without the repository and without internet. Without `--no-binaries` it
also places the `hdl` installer and the light CLI wheel (from `dist/cli/`) in `_bundle/cli/`.
"""

from __future__ import annotations

import shutil
import sys
import tarfile
import tomllib
from fnmatch import fnmatch
from pathlib import Path

from fetch_tools import BIN_DIR, MANIFEST, binary_name, current_platform, fetch

from heimdall_guardian import __version__
from heimdall_guardian.tool_install import tools_key

REPO = Path(__file__).resolve().parents[1]
CLI_WHEELS = REPO / "dist" / "cli"
CLI_SCRIPT = REPO / "packaging" / "cli" / "install_hdl.py"
BUNDLE = REPO / "src" / "heimdall_guardian" / "_bundle"


def main(argv: list[str]) -> int:
    with_binaries = "--no-binaries" not in argv
    manifest = tomllib.loads(MANIFEST.read_text(encoding="utf-8"))
    target = current_platform()
    if with_binaries:
        for name, spec in manifest.items():
            print(fetch(name, spec, target))

    if BUNDLE.exists():
        shutil.rmtree(BUNDLE)
    shutil.copytree(REPO / "rules" / "heimdall", BUNDLE / "rules")
    # The pin list ships with the package: `hdl tools --install` downloads from it.
    shutil.copy2(MANIFEST, BUNDLE / "tools.toml")
    versions = [f"{name} {spec['version']}" for name, spec in manifest.items()]
    if with_binaries:
        # The binaries ship compressed and are extracted on first use: as loose
        # executables, the macOS packager tries to process them and fails.
        with tarfile.open(BUNDLE / "tools.tar.gz", "w:gz", compresslevel=6) as archive:
            for name in manifest:
                source = BIN_DIR / binary_name(name, target)
                if not source.is_file():
                    print(
                        f"Missing {name} for {target}: package would not be self-contained.",
                        file=sys.stderr,
                    )
                    return 1
                archive.add(source, arcname=binary_name(name, target))
                # Files that must sit next to the binary (the DLLs of a Windows build).
                asset = manifest[name].get(target, {})
                patterns = [str(p) for p in asset.get("extra", [])]
                for extra in sorted(BIN_DIR.iterdir()):
                    if extra.is_file() and any(fnmatch(extra.name, p) for p in patterns):
                        archive.add(extra, arcname=extra.name)
        (BUNDLE / "tools.key").write_text(tools_key(manifest, target) + "\n", encoding="utf-8")
        # Application icon: `flet build` takes it from `src/assets/icon.png` and needs 1024 px.
        from app_icon import write_icon

        write_icon(REPO / "src" / "assets" / "icon.png")
        # The app offers to install the `hdl` command: it carries the installer and the light
        # wheel that `build_cli_wheel.py` built first (that script rebuilds this folder).
        wheel = CLI_WHEELS / f"heimdall_guardian-{__version__}-py3-none-any.whl"
        if not wheel.is_file():
            print(
                f"Missing {wheel.relative_to(REPO)}: run tools/build_cli_wheel.py first "
                "(tools/build_app.py does both in order).",
                file=sys.stderr,
            )
            return 1
        (BUNDLE / "cli").mkdir()
        # Stored as text: `flet build` would compile a `.py` for the app's own Python.
        shutil.copy2(CLI_SCRIPT, BUNDLE / "cli" / (CLI_SCRIPT.name + ".txt"))
        shutil.copy2(wheel, BUNDLE / "cli" / wheel.name)
    # The application distributes third-party binaries: it carries their full licenses.
    legal = BUNDLE / "legal"
    legal.mkdir()
    for name in ("LICENSE", "NOTICE", "THIRD-PARTY-NOTICES.md"):
        shutil.copy2(REPO / name, legal / name)
    shutil.copytree(REPO / "licenses", legal / "licenses")
    (BUNDLE / "VERSIONES.txt").write_text("\n".join(versions) + "\n", encoding="utf-8")
    size = sum(p.stat().st_size for p in BUNDLE.rglob("*") if p.is_file()) / 1_048_576
    print(f"Resources ready in {BUNDLE.relative_to(REPO)} ({size:.0f} MB, {target}).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
