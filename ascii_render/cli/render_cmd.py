"""Render subcommand."""

import os
from pathlib import Path
from typing import Optional

import click

from ascii_render.core.renderer import Renderer
from ascii_render.effects.glow import GlowEffect
from ascii_render.types import RenderConfig, ColorMode
from ascii_render.io.video import VideoProcessor
from ascii_render.io.ansi import ANSIFormatter
from ascii_render.cli.utils import (
    get_terminal_width,
    get_terminal_height,
    play_video,
    download_if_url,
)


@click.command()
@click.argument("input")
@click.option(
    "--width", "-w", default=None, type=int, help="Output width in characters"
)
@click.option("--height", "-H", default=None, type=int, help="Output height")
@click.option(
    "--chars",
    "-c",
    default=" .'-:_,^=;><+?rc*zLsLTv)J7(|Fi{C}fI31tlu[neoZ5Yxjya]2ESwPKP0dLhpQm@4#B8%$!",
    help="Character set for ASCII art",
)
@click.option("--invert", "-i", is_flag=True, help="Invert brightness")
@click.option("--glow", is_flag=True, help="Enable glow effect")
@click.option("--glow-radius", default=3, type=int, help="Glow radius")
@click.option("--glow-intensity", default=0.5, type=float, help="Glow intensity (0-1)")
@click.option("--highlight", is_flag=True, help="Enable bold/highlight text")
@click.option("--loop", is_flag=True, help="Loop video playback")
@click.option("--show-frame", is_flag=True, help="Show frame number")
@click.option("--fps", default=None, type=int, help="Frame rate")
@click.option("--output", "-o", type=click.Path(), default=None, help="Output file")
@click.option(
    "--color-mode",
    type=click.Choice(["8", "256", "truecolor"], case_sensitive=False),
    default="truecolor",
    help="Color mode",
)
def render_cmd(
    input: str,
    width: int,
    height: Optional[int],
    chars: str,
    invert: bool,
    glow: bool,
    glow_radius: int,
    glow_intensity: float,
    highlight: bool,
    loop: bool,
    show_frame: bool,
    fps: int,
    output: Optional[str],
    color_mode: str,
):
    """Render an image, video, or GIF to colored ASCII art."""
    input_path = download_if_url(input)
    temp_file = input_path if str(input_path).startswith("/tmp") else None

    if width is None:
        width = get_terminal_width()
    if height is None:
        height = get_terminal_height()

    config = RenderConfig(
        width=width,
        height=height,
        char_set=chars,
        invert=invert,
        color_mode=ColorMode.from_string(color_mode),
    )

    renderer = Renderer(config)
    if glow:
        renderer.add_effect(GlowEffect(radius=glow_radius, intensity=glow_intensity))

    is_video = input_path.suffix.lower() in (".mp4", ".avi", ".mov", ".mkv")
    is_gif = input_path.suffix.lower() == ".gif"

    if is_video or is_gif:
        formatter = ANSIFormatter(config.color_mode, chars, highlight=highlight)

        if output:
            frame_iterator = (
                VideoProcessor.read_gif(str(input_path))
                if is_gif
                else VideoProcessor.read_video_frames(str(input_path))
            )
            with open(output, "w") as f:
                for frame in frame_iterator:
                    ascii_result = renderer.process(frame)
                    formatted = formatter.format(ascii_result)
                    f.write(formatted + "\n\n")
        else:
            play_video(
                input_path,
                renderer,
                formatter,
                fps=fps,
                loop=loop,
                show_frame=show_frame,
            )
    else:
        formatter = ANSIFormatter(config.color_mode, chars, highlight=highlight)
        result = renderer.render(str(input_path))
        formatted = formatter.format(result)
        if output:
            Path(output).write_text(formatted)
        else:
            click.echo(formatted)

    if temp_file and os.path.exists(temp_file):
        os.remove(temp_file)
