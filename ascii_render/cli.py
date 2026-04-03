import click
from pathlib import Path
from typing import Optional
import shutil
import time
import sys
import select
import urllib.request
import tempfile
import os
import platform

try:
    import tty
    import termios

    HAS_TERMIO = True
except ImportError:
    HAS_TERMIO = False

from .core.renderer import Renderer
from .effects.glow import GlowEffect
from .types import RenderConfig, ColorMode
from .io.video import VideoProcessor


def get_terminal_width():
    return shutil.get_terminal_size().columns


def get_terminal_height():
    return shutil.get_terminal_size().lines


def download_if_url(path: str) -> Path:
    if path.startswith(("http://", "https://")):
        suffix = Path(path).suffix or ".tmp"
        fd, temp_path = tempfile.mkstemp(suffix=suffix)
        os.close(fd)
        try:
            req = urllib.request.Request(path, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as response:
                with open(temp_path, "wb") as f:
                    f.write(response.read())
            return Path(temp_path)
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise ValueError(f"Failed to download: {path} - {e}")
    return Path(path)


@click.command()
@click.argument("input")
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
@click.option(
    "--chars",
    "-c",
    # default=" .:-=+*#%@",
    # default=" .'-:_,^=;><+?rc*zLsLTv)J7(|Fi{C}fI31tlu[neoZ5Yxjya]2ESwPKP0dLhpQm@4#B8%$!",
    default=" .'-:_,^=;><+?rc*zLsLTv)J7(|Fi{C}fI31tlu[neoZ5Yxjya]2ESwPKP0dLhpQm@4#B8%$!",
    help="Character set for ASCII art",
)
@click.option("--invert", "-i", is_flag=True, help="Invert brightness")
@click.option("--glow", is_flag=True, help="Enable glow effect")
@click.option("--glow-radius", default=3, type=int, help="Glow radius")
@click.option("--glow-intensity", default=0.5, type=float, help="Glow intensity (0-1)")
@click.option("--highlight", is_flag=True, help="Enable bold/highlight text")
@click.option("--loop", is_flag=True, help="Loop video playback")
@click.option(
    "--show-frame", is_flag=True, help="Show frame number in top-right corner"
)
@click.option(
    "--fps",
    default=None,
    type=int,
    help="Frame rate (auto-detect for GIF, force override if specified)",
)
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
    show_frame: bool,
    fps: int,
    output: Optional[str],
    color_mode: str,
):
    input_path = download_if_url(input)
    temp_file = None
    if str(input_path).startswith("/tmp"):
        temp_file = input_path

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

        if is_gif and fps is None:
            gif_fps = processor.get_gif_info(str(input_path))
            if gif_fps:
                fps = int(gif_fps)

        if fps is None:
            fps = 30

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
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)
        else:
            if HAS_TERMIO and platform.system() != "Windows":
                sys.stdout.write("\033[?25l")
                sys.stdout.flush()
                click.echo("Playing... (Ctrl+C or q to stop)", err=True)

                old_settings = termios.tcgetattr(sys.stdin)
                tty.setcbreak(sys.stdin.fileno())
                sys.stdout.write("\033[2J\033[H\033[?25l")
                sys.stdout.flush()

            try:
                while True:
                    current_width = shutil.get_terminal_size().columns
                    current_height = shutil.get_terminal_size().lines

                    if current_width != config.width or current_height != config.height:
                        config.width = current_width
                        config.height = current_height
                        renderer.config = config
                        sys.stdout.write("\033[2J\033[H")
                        sys.stdout.flush()

                    frame_iterator = (
                        processor.read_gif(str(input_path))
                        if is_gif
                        else processor.read_video_frames(str(input_path))
                    )
                    frame_num = 0
                    for frame in frame_iterator:
                        frame_start = time.time()
                        frame_num += 1

                        frame = renderer._preprocess(frame)
                        for effect in renderer._effects:
                            frame = effect.apply(frame)
                        result = renderer._render_to_ascii(frame)
                        formatted = formatter.format(result)

                        if show_frame:
                            lines = formatted.split("\n")
                            frame_text = f" [{frame_num}]"
                            if lines:
                                lines[0] = lines[0] + frame_text
                            formatted = "\n".join(lines)

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
                if HAS_TERMIO and platform.system() != "Windows":
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                sys.stdout.write("\033[?25h\033[0m\n")
                sys.stdout.flush()
                if temp_file and os.path.exists(temp_file):
                    os.remove(temp_file)
    else:
        result = renderer.render(str(input_path))
        if output:
            Path(output).write_text(result)
        else:
            click.echo(result)

    if temp_file and os.path.exists(temp_file):
        os.remove(temp_file)


if __name__ == "__main__":
    main()
