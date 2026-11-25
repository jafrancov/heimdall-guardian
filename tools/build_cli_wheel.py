"""Builds the command-line-only wheel: rules, legal files and the pin list, no binaries.

Usage:  python tools/build_cli_wheel.py

Runs `build_bundle.py --no-binaries` and then `uv build --wheel` into `dist/cli/`. The wheel is
`py3-none-any`; the tools come later with `hdl tools --install`. It overwrites
`src/heimdall_guardian/_bundle/` (not versioned), so run `tools/build_bundle.py` again before
building the desktop app.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUTPUT = REPO / "dist" / "cli"


def main() -> int:
    bundle = subprocess.run(
        [sys.executable, str(REPO / "tools" / "build_bundle.py"), "--no-binaries"],
        cwd=REPO,
        check=False,
    )
    if bundle.returncode != 0:
        return bundle.returncode
    OUTPUT.mkdir(parents=True, exist_ok=True)
    build = subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(OUTPUT)], cwd=REPO, check=False
    )
    if build.returncode != 0:
        return build.returncode
    for wheel in sorted(OUTPUT.glob("*.whl")):
        print(f"{wheel.relative_to(REPO)}  {wheel.stat().st_size / 1_048_576:.2f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
