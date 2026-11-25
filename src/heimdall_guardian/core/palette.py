"""Colors shared by the interface and the reports.

Structure (panels, covers, headings) comes from the logo: night black and
gold. Severity uses the colors anyone recognizes: crimson, orange, yellow,
blue and gray.
"""

from __future__ import annotations

from pathlib import Path

from .finding import Severity

# Structure: taken from the Heimdall Guardian logo.
NIGHT = "#02040A"  # the logo's background (it blends with it); dark surfaces and text
CHARCOAL = "#14171F"  # relief over NIGHT
GOLD = "#F2B23A"  # the bright gold of the helmet; accent on a dark background
GOLD_LIGHT = "#FBCB55"
BRONZE = "#8A5412"  # the gold in shadow; accent and links on a light background
SAND = "#D8CDB4"  # secondary text on a dark background
GRAY_DARK = "#57534C"
GRAY_MID = "#918B80"
GRAY_LIGHT = "#CFC9BD"
LINE = "#E4DFD4"
PAPER = "#F3F2EF"
WHITE = "#FFFFFF"

# Severity: (solid color, text on the solid, background tint, text on the tint).
SEVERITY_COLORS: dict[Severity, tuple[str, str, str, str]] = {
    Severity.CRITICAL: ("#8B1A2B", "#FFFFFF", "#F8E1E5", "#8B1A2B"),
    Severity.HIGH: ("#D9480F", "#FFFFFF", "#FDE6D8", "#A8370B"),
    Severity.MEDIUM: ("#F2B705", "#3D2F00", "#FFF3C4", "#7A5B00"),
    Severity.LOW: ("#2F7FBF", "#FFFFFF", "#DDEBF7", "#1F5F92"),
    Severity.INFO: ("#8A9099", "#FFFFFF", "#ECEEF0", "#5B6168"),
}
GOOD = ("#1E7D4F", "#FFFFFF", "#DFF2E7", "#17603C")  # passed, fixed, with authentication

ART_NOTICE = (
    "Los elementos gráficos de HEIMDALL fueron desarrollados mediante un proceso creativo "
    "asistido por herramientas de inteligencia artificial, con decisiones de selección, "
    "adaptación y definición de identidad realizadas durante el desarrollo del proyecto. "
    "Su utilización y protección estarán sujetas a los derechos efectivamente reconocidos "
    "por la legislación aplicable."
)

ASSETS = Path(__file__).resolve().parents[1] / "assets"


def rgb(color: str) -> tuple[int, int, int]:
    """`#RRGGBB` → (r, g, b), for libraries that do not accept hex."""
    value = color.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)
