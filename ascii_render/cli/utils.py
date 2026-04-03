"""CLI utility functions."""

import os
import platform
import select
import shutil
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from typing import Optional

try:
    import termios
    import tty

    HAS_TERMIO = True
except ImportError:
    HAS_TERMIO = False

from ascii_render.core.renderer import Renderer
from ascii_render.types import RenderConfig, RenderResult
from ascii_render.io.ansi import ANSIFormatter
from ascii_render.io.video import VideoProcessor


def get_terminal_width() -> int:
    return shutil.get_terminal_size().columns


def get_terminal_height() -> int:
    return shutil.get_terminal_size().lines


def download_if_url(path: str) -> Path:
    """Download file from URL to a temp file if path is HTTP(S)."""
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


def display_frame(
    renderer: Renderer,
    formatter: ANSIFormatter,
    frame,
    frame_num: int = 0,
    show_frame: bool = False,
) -> str:
    """Process and format a single frame to ANSI string."""
    frame = renderer._preprocess(frame)
    for effect in renderer._effects:
        frame = effect.apply(frame)
    result = renderer._render_to_ascii(frame)
    formatted = formatter.format(result)

    if show_frame and frame_num > 0:
        lines = formatted.split("\n")
        frame_text = f" [{frame_num}]"
        if lines:
            lines[0] = lines[0] + frame_text
        formatted = "\n".join(lines)

    return formatted


def play_video(
    input_path: Path,
    renderer: Renderer,
    formatter: ANSIFormatter,
    fps: Optional[int] = None,
    loop: bool = False,
    show_frame: bool = False,
):
    """Play a video or GIF in the terminal with ASCII art."""
    processor = VideoProcessor()
    is_gif = input_path.suffix.lower() == ".gif"

    if is_gif and fps is None:
        gif_fps = processor.get_gif_info(str(input_path))
        if gif_fps:
            fps = int(gif_fps)

    if fps is None:
        fps = 30

    frame_delay = 1.0 / fps

    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())
    sys.stdout.write("\033[2J\033[H\033[?25l")
    sys.stdout.flush()

    try:
        while True:
            current_width = shutil.get_terminal_size().columns
            current_height = shutil.get_terminal_size().lines

            if (
                current_width != renderer.config.width
                or current_height != renderer.config.height
            ):
                renderer.config.width = current_width
                renderer.config.height = current_height
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

                formatted = display_frame(
                    renderer, formatter, frame, frame_num, show_frame
                )

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
