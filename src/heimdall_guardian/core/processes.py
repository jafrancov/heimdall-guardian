"""Options shared by every child process the app or the CLI launches."""

from __future__ import annotations

import subprocess
import sys
from typing import Any


def no_window() -> dict[str, Any]:
    """Keyword arguments for `subprocess.run` that keep Windows from opening a console.

    The desktop app has no console of its own, so on Windows every console program it runs
    (Python, git, the tools) would flash a window of its own. Elsewhere this is empty.
    """
    if sys.platform == "win32":
        return {"creationflags": subprocess.CREATE_NO_WINDOW}
    return {}
