"""Entry point of the packaged application (`flet build`)."""

import flet as ft

from heimdall_guardian.ui import model
from heimdall_guardian.ui.app import main

ft.run(main, assets_dir=str(model.ASSETS))
