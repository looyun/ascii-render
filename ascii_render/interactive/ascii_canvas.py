"""ASCII art canvas that renders images inside a mouse-driven canvas.

Caches pre-rendered frames for static images. Supports GIF animation with
frame iteration.
"""

import time
from typing import Optional, Iterator

from PIL import Image

from ascii_render.types import RenderConfig
from ascii_render.interactive.mouse_canvas import MouseCanvas
from ascii_render.core.pixel_mapper import map_pixels_to_ascii
from ascii_render.core.image_utils import preprocess_image

_ESC = "\033"
_RESET = f"{_ESC}[0m"


class AsciiArtCanvas(MouseCanvas):
    """A MouseCanvas that renders an image as colored ASCII art.

    For static images the output is pre-rendered once and cached. For GIFs,
    frames are rendered on-the-fly and iterated at the GIF's native FPS.

    The canvas size (in terminal cells) determines the ASCII render resolution.
    When the terminal resizes the canvas re-centers but keeps its configured
    ``size`` (short-side rows).

    Args:
        image: PIL Image to render (or first frame of a GIF).
        size: Short-side dimension of the canvas in terminal rows.
        config: Optional RenderConfig for the ASCII renderer.
        frames: Optional iterator of PIL Image frames (for GIF/animation).
        frame_delay: Seconds between frames (auto-detected from GIF if frames
                     provided but delay is None).
        loop: Whether to loop GIF playback.
        term_size: Explicit terminal ``(cols, rows)`` for testing.
    """

    def __init__(
        self,
        image: Image.Image,
        size: int = 12,
        config: Optional[RenderConfig] = None,
        frames: Optional[Iterator[Image.Image]] = None,
        frame_delay: Optional[float] = None,
        loop: bool = True,
        term_size: Optional[tuple[int, int]] = None,
    ):
        self._config = config or RenderConfig(
            width=size * 2,
            height=size,
            preserve_aspect=False,
        )
        self._chars = list(self._config.char_set)
        self._num_chars = len(self._chars)

        # Frame management
        self._frames = frames
        self._frame_delay = frame_delay
        self._loop = loop
        self._current_frame: Optional[Image.Image] = None
        self._frame_index = 0
        self._next_frame_time = 0.0
        self._gif_path: Optional[str] = None

        # Pre-rendered static ASCII
        self._static_ascii: list[str] = []

        # Prepare initial image
        init_image = self._prepare_image(image, size * 2, size)
        if frames is None:
            self._static_ascii = self._render_frame_to_ascii(init_image, size, size * 2)

        self._current_frame = init_image

        super().__init__(size=size, term_size=term_size)

    # -- GIF support --

    def set_gif(self, path: str):
        """Load a GIF for animated playback."""
        from ascii_render.io.video import VideoProcessor

        self._gif_path = path
        self._frames = VideoProcessor.read_gif(path)

        if self._frame_delay is None:
            fps = VideoProcessor.get_gif_info(path)
            if fps:
                self._frame_delay = 1.0 / fps
            else:
                self._frame_delay = 0.1

        try:
            frame = next(self._frames)
            self._current_frame = self._prepare_image(frame, self.cols, self.rows)
            self._static_ascii = self._render_frame_to_ascii(self._current_frame)
            self._frame_index = 1
        except StopIteration:
            self._frames = None

    def _next_frame(self):
        """Advance to the next animation frame if applicable."""
        if self._frames is None:
            return

        now = time.monotonic()
        if now < self._next_frame_time:
            return

        try:
            frame = next(self._frames)
            self._current_frame = self._prepare_image(frame, self.cols, self.rows)
            self._frame_index += 1

            if self._frame_delay is None:
                dur = getattr(frame, "info", {}).get("duration")
                if dur:
                    self._frame_delay = dur / 1000.0
                else:
                    self._frame_delay = 0.1

            self._next_frame_time = now + self._frame_delay

        except StopIteration:
            if self._loop and self._gif_path:
                self._frames = None
                self.set_gif(self._gif_path)

    # -- image preparation & rendering --

    def _prepare_image(
        self, image: Image.Image, width: int, height: int
    ) -> Image.Image:
        """Resize and convert image to RGB."""
        return preprocess_image(image, width, height, preserve_aspect=False)

    def _render_frame_to_ascii(
        self, image: Image.Image, rows: Optional[int] = None, cols: Optional[int] = None
    ) -> list[str]:
        """Render a single frame to ANSI-colored ASCII lines."""
        r = rows or self.rows
        c = cols or self.cols

        result = map_pixels_to_ascii(image, self._config.char_set, self._config.invert)

        lines: list[str] = []
        for y in range(r):
            parts: list[str] = []
            for x in range(c):
                red, green, blue = result.colors[y][x]
                ch = self._chars[result.char_indices[y][x]]
                parts.append(f"{_ESC}[38;2;{red};{green};{blue}m{ch}")
            lines.append("".join(parts) + _RESET)

        return lines

    # -- MouseCanvas override --

    def _draw_content_str(self, x: int, y: int) -> str:
        self._next_frame()

        if self._frames is None and not self._gif_path:
            ascii_lines = self._static_ascii
        else:
            ascii_lines = self._render_frame_to_ascii(self._current_frame)

        parts: list[str] = []
        for i, line in enumerate(ascii_lines):
            parts.append(f"{_ESC}[{y + i};{x}H")
            parts.append(line)
        return "".join(parts)

    def update(self):
        """Advance animation state and poll mouse input."""
        super().update()
        if self._frames is None and not self._gif_path and not self._static_ascii:
            self._static_ascii = self._render_frame_to_ascii(self._current_frame)
