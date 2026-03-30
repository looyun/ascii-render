import click
from pathlib import Path
from typing import Optional
import shutil
import time
import sys

from .core.renderer import Renderer
from .effects.glow import GlowEffect
from .types import RenderConfig, ColorMode
from .io.video import VideoProcessor


def get_terminal_width():
    return shutil.get_terminal_size().columns


def get_terminal_height():
    return shutil.get_terminal_size().lines


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

    if height is None:
        height = get_terminal_height()

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
        frame_delay = 1.0 / fps

        from .io.ansi import ANSIFormatter

        formatter = ANSIFormatter(config.color_mode)

        frames = (
            processor.read_gif(str(input_path))
            if is_gif
            else processor.read_video_frames(str(input_path))
        )

        if output:
            output_file = open(output, "w")
            for frame in frames:
                result = renderer._render_to_ascii(frame)
                formatted = formatter.format(result, frame)
                output_file.write(formatted + "\n\n")
            output_file.close()
        else:
            click.echo("Loading frames...", err=True)
            frames_list = list(frames)
            total_frames = len(frames_list)

            click.echo(f"Rendering {total_frames} frames...", err=True)
            rendered_frames = []
            for i, frame in enumerate(frames_list):
                result = renderer._render_to_ascii(frame)
                formatted = formatter.format(result, frame)
                rendered_frames.append(formatted)
                if (i + 1) % 10 == 0 or i + 1 == total_frames:
                    click.echo(
                        f"\rRendered {i + 1}/{total_frames} frames", err=True, nl=False
                    )

            click.echo("\nPlaying... (Ctrl+C to stop)", err=True)
            click.echo("\033[2J\033[H", nl=False)

            try:
                while True:
                    for formatted in rendered_frames:
                        start_time = time.time()

                        click.echo("\033[H", nl=False)
                        sys.stdout.write(formatted)
                        sys.stdout.flush()

                        elapsed = time.time() - start_time
                        sleep_time = frame_delay - elapsed
                        if sleep_time > 0:
                            time.sleep(sleep_time)

                    if not is_gif:
                        break
            except KeyboardInterrupt:
                click.echo("\n\033[0mPlayback stopped.")
    else:
        result = renderer.render(str(input_path))
        if output:
            Path(output).write_text(result)
        else:
            click.echo(result)


if __name__ == "__main__":
    main()
