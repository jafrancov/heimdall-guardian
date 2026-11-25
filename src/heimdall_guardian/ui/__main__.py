"""`python -m heimdall_guardian.ui [--web --port N]`."""

from __future__ import annotations

import argparse

from ..i18n import SUPPORTED, set_override
from .app import run

parser = argparse.ArgumentParser(prog="heimdall_guardian.ui")
parser.add_argument("--web", action="store_true", help="sirve la interfaz en un puerto local")
parser.add_argument("--port", type=int, default=0)
parser.add_argument("--lang", choices=SUPPORTED)
args = parser.parse_args()
set_override(args.lang)
run(web=args.web, port=args.port)
