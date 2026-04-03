"""Interactive subcommand."""

import os
import sys
import time

import click
from PIL import Image

from ascii_render.core.renderer import Renderer
from ascii_render.effects.glow import GlowEffect
from ascii_render.types import RenderConfig, ColorMode
from ascii_render.interactive.ascii_canvas import AsciiArtCanvas
from ascii_render.cli.utils import download_if_url


@click.command()
@click.argument("input")
@click.option(
    "--size", "-s", default=20, type=int, help="Canvas short-side size in rows"
)
@click.option(
    "--chars",
    "-c",
    default=" .'-:_,^=;><+?rc*zLsLTv)J7(|Fi{C}fI31tlu[neoZ5Yxjya]2ESwPKP0dLhpQm@4#B8%$!",
    help="Character set for ASCII art",
)
@click.option("--invert", "-i", is_flag=True, help="Invert brightness")
@click.option("--glow", is_flag=True, help="Enable glow effect (static images only)")
@click.option("--glow-radius", default=3, type=int, help="Glow radius")
@click.option("--glow-intensity", default=0.5, type=float, help="Glow intensity (0-1)")
@click.option(
    "--color-mode",
    type=click.Choice(["8", "256", "truecolor"], case_sensitive=False),
    default="truecolor",
    help="Color mode",
)
@click.option("--loop/--no-loop", default=True, help="Loop GIF playback")
def interactive(
    input: str,
    size: int,
    chars: str,
    invert: bool,
    glow: bool,
    glow_radius: int,
    glow_intensity: float,
    color_mode: str,
    loop: bool,
):
    """Render an image or GIF as interactive ASCII art that follows mouse clicks."""
    input_path = download_if_url(input)
    temp_file = input_path if str(input_path).startswith("/tmp") else None

    image = Image.open(input_path)
    is_gif = input_path.suffix.lower() == ".gif"

    color_map = {
        "8": ColorMode.MODE_8,
        "256": ColorMode.MODE_256,
        "truecolor": ColorMode.TRUECOLOR,
    }

    config = RenderConfig(
        width=size * 2,
        height=size,
        char_set=chars,
        invert=invert,
        color_mode=color_map[color_mode.lower()],
        preserve_aspect=False,
    )

    if is_gif:
        canvas = AsciiArtCanvas(image=image, size=size, config=config, loop=loop)
        canvas.set_gif(str(input_path))
    elif glow:
        renderer = Renderer(config)
        renderer.add_effect(GlowEffect(radius=glow_radius, intensity=glow_intensity))
        processed = renderer._preprocess(image)
        for effect in renderer._effects:
            processed = effect.apply(processed)
        canvas = AsciiArtCanvas(image=processed, size=size, config=config)
    else:
        canvas = AsciiArtCanvas(image=image, size=size, config=config)

    try:
        canvas.start()
        canvas.render()
        while True:
            canvas.update()
            canvas.render()
            if is_gif and canvas._frame_delay:
                sleep_time = max(0.001, canvas._frame_delay - canvas.time_since_update)
            else:
                sleep_time = max(0.001, 1.0 / 30 - canvas.time_since_update)
            time.sleep(sleep_time)
    except KeyboardInterrupt:
        pass
    finally:
        canvas.stop()
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()
        print("Interactive session exited.")

    if temp_file and os.path.exists(temp_file):
        os.remove(temp_file)
