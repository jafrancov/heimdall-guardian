"""Downloads the analysis tools at a pinned version and verifies their SHA-256.

Usage:  python tools/fetch_tools.py [tool ...]

The binaries end up in `tools/bin/` (not versioned). A file whose hash does not
match `tools/tools.toml` is discarded without ever being installed.
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

# The repository checkout may be run without installing the package.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from heimdall_guardian.tool_install import (
    ToolInstallError,
    binary_name,
    current_platform,
    fetch_asset,
    write_extras,
)

__all__ = ["binary_name", "current_platform", "fetch", "main"]

TOOLS_DIR = Path(__file__).resolve().parent
BIN_DIR = TOOLS_DIR / "bin"
MANIFEST = TOOLS_DIR / "tools.toml"


def fetch(name: str, spec: dict[str, object], target_platform: str) -> str:
    version = str(spec["version"])
    asset = spec.get(target_platform)
    if not isinstance(asset, dict):
        return f"{name} {version}: no pinned binary for {target_platform}"

    destination = BIN_DIR / binary_name(name, target_platform)
    marker = BIN_DIR / f".{name}.sha256"
    expected = str(asset["sha256"])
    # The marker also records the extra-file patterns, so adding them refetches the tool.
    extra = [str(pattern) for pattern in asset.get("extra", [])]
    stamp = " ".join([expected, *extra])
    if (
        destination.is_file()
        and marker.is_file()
        and marker.read_text(encoding="utf-8").strip() == stamp
    ):
        return f"{name} {version}: already installed"

    try:
        data, extras, _ = fetch_asset(name, version, asset)
    except ToolInstallError as error:
        raise SystemExit(f"{name} {version}: not installing.\n{error}") from error

    BIN_DIR.mkdir(exist_ok=True)
    try:
        write_extras(extras, BIN_DIR)
    except ToolInstallError as error:
        raise SystemExit(f"{name} {version}: not installing.\n{error}") from error
    temporary = destination.with_name(destination.name + ".tmp")
    temporary.write_bytes(data)
    temporary.chmod(0o755)
    temporary.replace(destination)
    marker.write_text(stamp + "\n", encoding="utf-8")
    return f"{name} {version}: installed in {destination.relative_to(TOOLS_DIR.parent)}"


def main(argv: list[str]) -> int:
    manifest = tomllib.loads(MANIFEST.read_text(encoding="utf-8"))
    unknown = [name for name in argv if name not in manifest]
    if unknown:
        print(f"Unknown tool: {', '.join(unknown)}", file=sys.stderr)
        return 2
    target = current_platform()
    for name in argv or list(manifest):
        print(fetch(name, manifest[name], target))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
