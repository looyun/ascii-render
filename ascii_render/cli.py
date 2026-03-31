import click
from pathlib import Path
from typing import Optional
import shutil
import time
import sys
import select
import tty
import termios

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
@click.option("--highlight", is_flag=True, help="Enable bold/highlight text")
@click.option("--loop", is_flag=True, help="Loop video playback")
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
    highlight: bool,
    loop: bool,
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

        formatter = ANSIFormatter(config.color_mode, chars, highlight=highlight)

        frame_iterator = (
            processor.read_gif(str(input_path))
            if is_gif
            else processor.read_video_frames(str(input_path))
        )

        if output:
            output_file = open(output, "w")
            frame_iterator = (
                processor.read_gif(str(input_path))
                if is_gif
                else processor.read_video_frames(str(input_path))
            )
            for frame in frame_iterator:
                frame = renderer._preprocess(frame)
                result = renderer._render_to_ascii(frame)
                formatted = formatter.format(result)
                output_file.write(formatted + "\n\n")
            output_file.close()
        else:
            sys.stdout.write("\033[?25l\033[2J\033[H")
            sys.stdout.flush()
            click.echo("Playing... (Ctrl+C or q to stop)", err=True)

            old_settings = termios.tcgetattr(sys.stdin)
            try:
                tty.setcbreak(sys.stdin.fileno())
                while True:
                    frame_iterator = (
                        processor.read_gif(str(input_path))
                        if is_gif
                        else processor.read_video_frames(str(input_path))
                    )
                    for frame in frame_iterator:
                        frame_start = time.time()

                        frame = renderer._preprocess(frame)
                        for effect in renderer._effects:
                            frame = effect.apply(frame)
                        result = renderer._render_to_ascii(frame)
                        formatted = formatter.format(result)

                        sys.stdout.write("\033[H" + formatted)
                        sys.stdout.flush()

                        render_time = time.time() - frame_start
                        sleep_time = frame_delay - render_time
                        if sleep_time > 0:
                            time.sleep(sleep_time)

                        if select.select([sys.stdin], [], [], 0)[0]:
                            if sys.stdin.read(1) == "q":
                                raise KeyboardInterrupt

                    if not is_gif and not loop:
                        break
            except KeyboardInterrupt:
                pass
            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                sys.stdout.write("\033[?25h\033[0m\n")
                sys.stdout.flush()
    else:
        result = renderer.render(str(input_path))
        if output:
            Path(output).write_text(result)
        else:
            click.echo(result)


if __name__ == "__main__":
    main()
