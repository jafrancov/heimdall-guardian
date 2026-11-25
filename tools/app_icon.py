"""Composes the application icon at full size from the original art.

The packaged `icono.png` is a 512 px copy for the interface; installers need 1024 px,
so the icon is drawn here from `assets/Heimdall_logo_transparente.png`: the emblem
without lettering on a black rounded square (824 px body on a 1024 px canvas, radius 185,
no outline), the same proportions as `icono.png`.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "assets" / "Heimdall_logo_transparente.png"
CANVAS = 1024
BODY = (100, 100, 923, 923)
RADIUS = 185
# Height of the visible emblem and its center, measured on the canvas.
EMBLEM_HEIGHT = 668
EMBLEM_CENTER = (511, 510)


def make_icon(size: int = CANVAS) -> Image.Image:
    """The application icon as an RGBA image of `size` x `size` pixels."""
    emblem = Image.open(SOURCE).convert("RGBA")
    emblem = emblem.crop(emblem.split()[3].getbbox())
    # The visible part of the emblem (bright pixels over black), not its transparent halo.
    over_black = Image.new("RGBA", emblem.size, (0, 0, 0, 255))
    over_black.alpha_composite(emblem)
    left, top, right, bottom = over_black.convert("L").point(
        lambda v: 255 if v > 60 else 0
    ).getbbox() or (0, 0, 1, 1)
    scale = EMBLEM_HEIGHT / (bottom - top)
    emblem = emblem.resize(
        (round(emblem.width * scale), round(emblem.height * scale)), Image.Resampling.LANCZOS
    )
    offset = (
        round(EMBLEM_CENTER[0] - (left + right) / 2 * scale),
        round(EMBLEM_CENTER[1] - (top + bottom) / 2 * scale),
    )

    mask = Image.new("L", (CANVAS, CANVAS), 0)
    ImageDraw.Draw(mask).rounded_rectangle(BODY, radius=RADIUS, fill=255)
    icon = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    icon.paste(Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 255)), (0, 0), mask)
    layer = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    layer.paste(emblem, offset, emblem)
    icon = Image.alpha_composite(icon, layer)
    icon.putalpha(ImageChops.multiply(icon.split()[3], mask))
    if size != CANVAS:
        icon = icon.resize((size, size), Image.Resampling.LANCZOS)
    return icon


def write_icon(target: Path, size: int = CANVAS) -> Path:
    """Writes the icon as PNG to `target` and returns it."""
    target.parent.mkdir(parents=True, exist_ok=True)
    make_icon(size).save(target, optimize=True)
    return target
