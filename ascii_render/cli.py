import click
from pathlib import Path
from typing import Optional
import shutil

from .core.renderer import Renderer
from .effects.glow import GlowEffect
from .types import RenderConfig, ColorMode
from .io.video import VideoProcessor


def get_terminal_width():
    return shutil.get_terminal_size().columns


@click.command()
@click.argument("input", type=click.Path(exists=True))
@click.option(
    "--width",
    "-w",
    default=None,
    type=int,
    help="Output width in characters (auto-detect by default)",
)
@click.option(
    "--height", "-H", default=None, type=int, help="Output height (auto if not set)"
)
@click.option("--chars", "-c", default=" .:-=+*#%@", help="Character set for ASCII art")
@click.option("--invert", "-i", is_flag=True, help="Invert brightness")
@click.option("--glow", is_flag=True, help="Enable glow effect")
@click.option("--glow-radius", default=3, type=int, help="Glow radius")
@click.option("--glow-intensity", default=0.5, type=float, help="Glow intensity (0-1)")
@click.option("--fps", default=30, type=int, help="Video frame rate")
@click.option("--output", "-o", type=click.Path(), default=None, help="Output file")
@click.option(
    "--color-mode",
    type=click.Choice(["8", "256", "truecolor"], case_sensitive=False),
    default="truecolor",
    help="Color mode",
)
def main(
    input: str,
    width: int,
    height: Optional[int],
    chars: str,
    invert: bool,
    glow: bool,
    glow_radius: int,
    glow_intensity: float,
    fps: int,
    output: Optional[str],
    color_mode: str,
):
    input_path = Path(input)

    if width is None:
        width = get_terminal_width()

    color_map = {
        "8": ColorMode.MODE_8,
        "256": ColorMode.MODE_256,
        "truecolor": ColorMode.TRUECOLOR,
    }

    config = RenderConfig(
        width=width,
        height=height,
        char_set=chars,
        invert=invert,
        color_mode=color_map[color_mode.lower()],
    )

    renderer = Renderer(config)

    if glow:
        renderer.add_effect(GlowEffect(radius=glow_radius, intensity=glow_intensity))

    is_video = input_path.suffix.lower() in (".mp4", ".avi", ".mov", ".mkv")
    is_gif = input_path.suffix.lower() == ".gif"

    if is_video or is_gif:
        processor = VideoProcessor()
        frames = (
            processor.read_gif(str(input_path))
            if is_gif
            else processor.read_video_frames(str(input_path))
        )
        output_file = open(output, "w") if output else None

        for frame in frames:
            result = renderer._render_to_ascii(frame)
            from .io.ansi import ANSIFormatter

            formatter = ANSIFormatter(config.color_mode)
            formatted = formatter.format(result, frame)

            if output_file:
                output_file.write(formatted + "\n\n")
            else:
                click.echo(formatted)
                click.echo("\n")

        if output_file:
            output_file.close()
    else:
        result = renderer.render(str(input_path))
        if output:
            Path(output).write_text(result)
        else:
            click.echo(result)


if __name__ == "__main__":
    main()
