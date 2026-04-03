# Render & Interactive Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate code duplication between Renderer and AsciiArtCanvas, extract CLI logic into a proper package, and unify the Effect type definition.

**Architecture:** Extract shared rendering logic (`pixel_mapper.py`, `image_utils.py`) into `core/`, split `cli.py` into a `cli/` package, consolidate Effect to a single ABC in `core/effects.py`.

**Tech Stack:** Python 3.10+, Pillow, Click, pytest

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `ascii_render/core/pixel_mapper.py` | Create | Brightness → char indices + color extraction |
| `ascii_render/core/image_utils.py` | Create | Image resize + RGBA→RGB conversion |
| `ascii_render/core/effects.py` | Modify | Keep as single Effect ABC source |
| `ascii_render/core/renderer.py` | Modify | Delegate to pixel_mapper + image_utils |
| `ascii_render/core/__init__.py` | Modify | Export new modules |
| `ascii_render/types.py` | Modify | Remove Effect Protocol |
| `ascii_render/cli/main.py` | Create | Click group + download_if_url |
| `ascii_render/cli/render_cmd.py` | Create | Render subcommand |
| `ascii_render/cli/interactive_cmd.py` | Create | Interactive subcommand |
| `ascii_render/cli/utils.py` | Create | Terminal helpers, video playback loop |
| `ascii_render/cli/__init__.py` | Create | Re-export main |
| `ascii_render/interactive/ascii_canvas.py` | Modify | Use pixel_mapper + image_utils |
| `ascii_render/__init__.py` | Modify | Update exports |
| `ascii_render/__main__.py` | Modify | Update import path |
| `run_cli.py` | Modify | Update import path |
| `tests/test_cli.py` | Modify | Update import paths |
| `tests/test_effects.py` | Modify | Update Effect import |
| `tests/test_renderer.py` | Modify | No changes expected (same public API) |
| `tests/test_interactive.py` | Modify | No changes expected (same public API) |
| `tests/test_core.py` | Create | Tests for pixel_mapper + image_utils |

---

### Task 1: Create `core/pixel_mapper.py`

**Files:**
- Create: `ascii_render/core/pixel_mapper.py`
- Test: `tests/test_core.py`

- [ ] **Step 1: Write tests for pixel_mapper**

Add to `tests/test_core.py`:

```python
"""Tests for core pixel_mapper and image_utils."""
from PIL import Image
from ascii_render.core.pixel_mapper import map_pixels_to_ascii
from ascii_render.core.image_utils import preprocess_image


def test_map_pixels_to_ascii_basic():
    img = Image.new("RGB", (4, 4), color=(128, 128, 128))
    result = map_pixels_to_ascii(img, " .:-=+*#%@")
    assert result.dimensions == (4, 4)
    assert len(result.char_indices) == 4
    assert len(result.colors) == 4
    assert all(len(row) == 4 for row in result.char_indices)
    assert all(len(row) == 4 for row in result.colors)


def test_map_pixels_to_ascii_invert():
    img = Image.new("RGB", (2, 2), color=(0, 0, 0))
    result = map_pixels_to_ascii(img, " .:-=+*#%@", invert=True)
    assert result.dimensions == (2, 2)
    # Black (0) inverted should map to highest brightness → highest char index


def test_map_pixels_to_ascii_colors():
    img = Image.new("RGB", (1, 1), color=(255, 100, 50))
    result = map_pixels_to_ascii(img, " .:-=+*#%@")
    assert result.colors[0][0] == (255, 100, 50)


def test_map_pixels_to_ascii_char_indices_range():
    """All char indices should be within valid range."""
    img = Image.new("RGB", (10, 10), color=(200, 200, 200))
    result = map_pixels_to_ascii(img, " .:-=+*#%@")
    num_chars = 10
    for row in result.char_indices:
        for idx in row:
            assert 0 <= idx < num_chars
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_core.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Implement `pixel_mapper.py`**

Create `ascii_render/core/pixel_mapper.py`:

```python
"""Pixel-to-ASCII mapping utilities.

Converts PIL Images to RenderResult objects by mapping pixel brightness
to character indices and extracting RGB color data.
"""

from PIL import Image

from ..types import RenderResult


def map_pixels_to_ascii(
    image: Image.Image,
    char_set: str,
    invert: bool = False,
) -> RenderResult:
    """Convert a PIL Image to RenderResult.

    Args:
        image: RGB PIL Image (must be preprocessed).
        char_set: String of ASCII characters ordered by brightness.
        invert: If True, invert brightness mapping.

    Returns:
        RenderResult with char_indices, colors, and dimensions.
    """
    width, height = image.size
    gray = image.convert("L")
    gray_pixels = list(gray.get_flattened_data())
    rgb_pixels = list(image.get_flattened_data())

    num_chars = len(char_set)
    scale = num_chars / 255.0

    char_indices: list[list[int]] = []
    colors: list[list[tuple[int, int, int]]] = []

    for y in range(height):
        char_row: list[int] = []
        color_row: list[tuple[int, int, int]] = []
        for x in range(width):
            offset = y * width + x
            brightness = gray_pixels[offset]
            if invert:
                brightness = 255 - brightness
            idx = int(brightness * scale)
            if idx < 0:
                idx = 0
            elif idx >= num_chars:
                idx = num_chars - 1
            char_row.append(idx)

            r, g, b = rgb_pixels[offset]
            color_row.append((r, g, b))

        char_indices.append(char_row)
        colors.append(color_row)

    return RenderResult(
        char_indices=char_indices,
        colors=colors,
        dimensions=(width, height),
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_core.py -v`
Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add ascii_render/core/pixel_mapper.py tests/test_core.py
git commit -m "feat: add pixel_mapper module for shared ASCII rendering"
```

---

### Task 2: Create `core/image_utils.py`

**Files:**
- Create: `ascii_render/core/image_utils.py`
- Test: `tests/test_core.py` (append)

- [ ] **Step 1: Write tests for image_utils**

Append to `tests/test_core.py`:

```python
def test_preprocess_resize():
    img = Image.new("RGB", (100, 100), color=(128, 128, 128))
    result = preprocess_image(img, 20, 10, preserve_aspect=False)
    assert result.size == (20, 10)
    assert result.mode == "RGB"


def test_preprocess_rgba_to_rgb():
    img = Image.new("RGBA", (10, 10), color=(128, 128, 128, 200))
    result = preprocess_image(img, 10, 10, preserve_aspect=False)
    assert result.mode == "RGB"


def test_preprocess_preserve_aspect():
    img = Image.new("RGB", (200, 100), color=(128, 128, 128))
    result = preprocess_image(img, 40, 20, preserve_aspect=True)
    assert result.mode == "RGB"
    # Should fit within 40x20 while preserving aspect ratio
    assert result.size[0] <= 40
    assert result.size[1] <= 20
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_core.py -v`
Expected: FAIL — image_utils module not found

- [ ] **Step 3: Implement `image_utils.py`**

Create `ascii_render/core/image_utils.py`:

```python
"""Image preprocessing utilities.

Handles resizing (with optional aspect ratio correction) and
RGBA to RGB conversion.
"""

from PIL import Image


def preprocess_image(
    image: Image.Image,
    width: int,
    height: int,
    preserve_aspect: bool = True,
) -> Image.Image:
    """Resize and convert image to RGB.

    Args:
        image: Input PIL Image.
        width: Target width in pixels.
        height: Target height in pixels.
        preserve_aspect: If True, maintain aspect ratio with char correction.

    Returns:
        Resized RGB PIL Image.
    """
    if width or height:
        target_width = width or 80
        target_height = height or 24

        if preserve_aspect:
            orig_w, orig_h = image.size
            aspect = orig_w / orig_h
            char_aspect = 0.5

            height_from_width = int(target_width * char_aspect / aspect)
            width_from_height = int(target_height * aspect / char_aspect)

            if height_from_width <= target_height:
                target_height = height_from_width
            else:
                target_width = width_from_height

        image = image.resize((target_width, target_height))

    if image.mode == "RGBA":
        background = Image.new("RGB", image.size, (0, 0, 0))
        background.paste(image, mask=image.split()[3])
        return background
    return image.convert("RGB")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_core.py -v`
Expected: All 7 tests PASS

- [ ] **Step 5: Commit**

```bash
git add ascii_render/core/image_utils.py tests/test_core.py
git commit -m "feat: add image_utils module for shared image preprocessing"
```

---

### Task 3: Update `core/renderer.py` to use new modules

**Files:**
- Modify: `ascii_render/core/renderer.py`
- Modify: `ascii_render/core/__init__.py`
- Modify: `ascii_render/types.py` (remove Effect Protocol)
- Modify: `ascii_render/core/effects.py` (keep as single Effect source)

- [ ] **Step 1: Update `core/renderer.py`**

Replace the entire file content:

```python
"""Core ASCII renderer."""

from PIL import Image
from typing import List, Optional

from .effects import Effect
from .pixel_mapper import map_pixels_to_ascii
from .image_utils import preprocess_image
from ..types import RenderConfig
from ..io.loader import load_image
from ..io.ansi import ANSIFormatter


class Renderer:
    def __init__(self, config: Optional[RenderConfig] = None):
        self.config = config or RenderConfig()
        self._effects: List[Effect] = []

    def add_effect(self, effect: Effect) -> "Renderer":
        self._effects.append(effect)
        return self

    def render(self, image_path: str) -> str:
        image = load_image(image_path)
        image = self._preprocess(image)

        for effect in self._effects:
            image = effect.apply(image)

        result = self._render_to_ascii(image)
        formatter = ANSIFormatter(self.config.color_mode, self.config.char_set)
        return formatter.format(result)

    def _preprocess(self, image: Image.Image) -> Image.Image:
        return preprocess_image(
            image,
            self.config.width or 0,
            self.config.height or 0,
            self.config.preserve_aspect,
        )

    def _render_to_ascii(self, image: Image.Image) -> "RenderResult":
        from ..types import RenderResult
        return map_pixels_to_ascii(
            image,
            self.config.char_set,
            self.config.invert,
        )
```

- [ ] **Step 2: Update `core/__init__.py`**

```python
from .renderer import Renderer
from .effects import Effect
from .pixel_mapper import map_pixels_to_ascii
from .image_utils import preprocess_image

__all__ = ["Renderer", "Effect", "map_pixels_to_ascii", "preprocess_image"]
```

- [ ] **Step 3: Remove Effect Protocol from `types.py`**

Remove the `Effect` class and its import. Final `types.py`:

```python
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class ColorMode(Enum):
    MODE_8 = 8
    MODE_256 = 256
    TRUECOLOR = "truecolor"


@dataclass
class RenderConfig:
    width: int = 80
    height: Optional[int] = None
    char_set: str = " .:-=+*#%@"
    invert: bool = False
    color_mode: ColorMode = ColorMode.TRUECOLOR
    preserve_aspect: bool = True


@dataclass
class RenderResult:
    char_indices: list[list[int]]
    colors: list[list[tuple[int, int, int]]]
    dimensions: tuple[int, int]
```

- [ ] **Step 4: Update `core/effects.py`**

Keep it as the single Effect ABC. Ensure it has proper docstring:

```python
"""Abstract effect base class."""

from abc import ABC, abstractmethod
from PIL import Image


class Effect(ABC):
    """Base class for image effects.

    Subclasses must implement apply() to transform an image.
    """

    @abstractmethod
    def apply(self, image: Image.Image) -> Image.Image:
        """Apply effect to image and return modified image."""
        ...
```

- [ ] **Step 5: Run all tests**

Run: `pytest tests/ -v`
Expected: All tests PASS (renderer tests use same public API)

- [ ] **Step 6: Commit**

```bash
git add ascii_render/core/renderer.py ascii_render/core/__init__.py ascii_render/types.py ascii_render/core/effects.py
git commit -m "refactor: unify renderer to use pixel_mapper and image_utils"
```

---

### Task 4: Update `interactive/ascii_canvas.py`

**Files:**
- Modify: `ascii_render/interactive/ascii_canvas.py`

- [ ] **Step 1: Rewrite `ascii_canvas.py` to use shared modules**

Replace the entire file:

```python
"""ASCII art canvas that renders images inside a mouse-driven canvas.

Caches pre-rendered frames for static images. Supports GIF animation with
frame iteration.
"""

import os
import sys
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
```

- [ ] **Step 2: Run interactive tests**

Run: `pytest tests/test_interactive.py -v`
Expected: All tests PASS

- [ ] **Step 3: Commit**

```bash
git add ascii_render/interactive/ascii_canvas.py
git commit -m "refactor: ascii_canvas uses shared pixel_mapper and image_utils"
```

---

### Task 5: Split `cli.py` into `cli/` package

This is the largest task. We create 4 new files and remove the old `cli.py`.

**Files:**
- Create: `ascii_render/cli/__init__.py`
- Create: `ascii_render/cli/main.py`
- Create: `ascii_render/cli/utils.py`
- Create: `ascii_render/cli/render_cmd.py`
- Create: `ascii_render/cli/interactive_cmd.py`
- Delete: `ascii_render/cli.py`
- Modify: `ascii_render/__main__.py`
- Modify: `run_cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Create `cli/__init__.py`**

```python
from .main import main

__all__ = ["main"]
```

- [ ] **Step 2: Create `cli/utils.py`**

```python
"""CLI utility functions."""

import os
import platform
import select
import shutil
import sys
import time
from pathlib import Path
from typing import Optional

try:
    import termios
    import tty

    HAS_TERMIO = True
except ImportError:
    HAS_TERMIO = False

from ascii_render.core.renderer import Renderer
from ascii_render.core.effects import Effect
from ascii_render.types import RenderConfig, RenderResult
from ascii_render.io.ansi import ANSIFormatter
from ascii_render.io.video import VideoProcessor


def get_terminal_width() -> int:
    return shutil.get_terminal_size().columns


def get_terminal_height() -> int:
    return shutil.get_terminal_size().lines


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
    """Play a video or GIF in the terminal with ASCII art.

    Handles terminal raw mode, frame timing, resize detection, and quit input.
    """
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

            if current_width != renderer.config.width or current_height != renderer.config.height:
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

                formatted = display_frame(renderer, formatter, frame, frame_num, show_frame)

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
```

- [ ] **Step 3: Create `cli/render_cmd.py`**

```python
"""Render subcommand."""

import os
import sys
from pathlib import Path

import click

from ascii_render.core.renderer import Renderer
from ascii_render.effects.glow import GlowEffect
from ascii_render.types import RenderConfig, ColorMode
from ascii_render.io.video import VideoProcessor
from ascii_render.io.ansi import ANSIFormatter
from ascii_render.cli.utils import get_terminal_width, get_terminal_height, play_video, HAS_TERMIO
from ascii_render.cli.main import download_if_url


@click.command()
@click.argument("input")
@click.option("--width", "-w", default=None, type=int, help="Output width in characters")
@click.option("--height", "-H", default=None, type=int, help="Output height")
@click.option(
    "--chars", "-c",
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
        formatter = ANSIFormatter(config.color_mode, chars, highlight=highlight)

        if output:
            processor = VideoProcessor()
            frame_iterator = (
                processor.read_gif(str(input_path))
                if is_gif
                else processor.read_video_frames(str(input_path))
            )
            with open(output, "w") as f:
                for frame in frame_iterator:
                    result = renderer._preprocess(frame)
                    for effect in renderer._effects:
                        result = effect.apply(result)
                    ascii_result = renderer._render_to_ascii(result)
                    formatted = formatter.format(ascii_result)
                    f.write(formatted + "\n\n")
        else:
            play_video(input_path, renderer, formatter, fps=fps, loop=loop, show_frame=show_frame)
    else:
        result = renderer.render(str(input_path))
        if output:
            Path(output).write_text(result)
        else:
            click.echo(result)

    if temp_file and os.path.exists(temp_file):
        os.remove(temp_file)
```

- [ ] **Step 4: Create `cli/interactive_cmd.py`**

```python
"""Interactive subcommand."""

import os
import sys
import time
from pathlib import Path

import click
from PIL import Image

from ascii_render.core.renderer import Renderer
from ascii_render.effects.glow import GlowEffect
from ascii_render.types import RenderConfig, ColorMode
from ascii_render.interactive.ascii_canvas import AsciiArtCanvas
from ascii_render.cli.main import download_if_url


@click.command()
@click.argument("input")
@click.option("--size", "-s", default=20, type=int, help="Canvas short-side size in rows")
@click.option(
    "--chars", "-c",
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
```

- [ ] **Step 5: Create `cli/main.py`**

```python
"""CLI entry point."""

import os
import tempfile
import urllib.request
from pathlib import Path

import click

from ascii_render.cli.render_cmd import render_cmd
from ascii_render.cli.interactive_cmd import interactive


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


@click.group()
def main():
    """Render images/videos to colored ASCII art with glow effects."""
    pass


main.add_command(render_cmd)
main.add_command(interactive)


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Update `__main__.py`**

```python
from .cli.main import main

if __name__ == "__main__":
    main()
```

- [ ] **Step 7: Update `run_cli.py`**

```python
from ascii_render.cli.main import main
import sys

if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 8: Update `tests/test_cli.py`**

Replace the import line at the top:

```python
from ascii_render.cli.main import main
from ascii_render.cli.utils import get_terminal_width, get_terminal_height
```

Update the patch in `test_cli_auto_width_detection`:

```python
def test_cli_auto_width_detection(temp_image):
    runner = CliRunner()
    with patch("ascii_render.cli.render_cmd.get_terminal_width", return_value=120):
        result = runner.invoke(main, ["render", temp_image])
    assert result.exit_code == 0
    assert len(result.output) > 0
```

Note: The patch target needs to match where `get_terminal_width` is imported. Since `render_cmd.py` imports it from `ascii_render.cli.utils`, the patch target should be `ascii_render.cli.render_cmd.get_terminal_width`.

Full updated `test_cli.py`:

```python
import pytest
from click.testing import CliRunner
import tempfile
import os
from unittest.mock import patch
from PIL import Image

from ascii_render.cli.main import main
from ascii_render.cli.utils import get_terminal_width, get_terminal_height


@pytest.fixture
def temp_image():
    img = Image.new("RGB", (20, 20), color=(150, 100, 50))
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        img.save(f.name)
        temp_path = f.name
    yield temp_path
    if os.path.exists(temp_path):
        os.unlink(temp_path)


def test_cli_basic(temp_image):
    runner = CliRunner()
    result = runner.invoke(main, ["render", temp_image, "--width", "20"])
    assert result.exit_code == 0
    assert len(result.output) > 0


def test_cli_with_glow(temp_image):
    runner = CliRunner()
    result = runner.invoke(main, ["render", temp_image, "--width", "20", "--glow"])
    assert result.exit_code == 0


def test_cli_output_file(temp_image):
    runner = CliRunner()
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        output_path = f.name
    result = runner.invoke(
        main, ["render", temp_image, "--width", "20", "--output", output_path]
    )
    os.unlink(output_path)
    assert result.exit_code == 0


def test_get_terminal_width():
    width = get_terminal_width()
    assert isinstance(width, int)
    assert width > 0


def test_get_terminal_height():
    height = get_terminal_height()
    assert isinstance(height, int)
    assert height > 0


def test_cli_auto_width_detection(temp_image):
    runner = CliRunner()
    with patch("ascii_render.cli.render_cmd.get_terminal_width", return_value=120):
        result = runner.invoke(main, ["render", temp_image])
    assert result.exit_code == 0
    assert len(result.output) > 0
```

- [ ] **Step 9: Delete old `cli.py`**

```bash
rm ascii_render/cli.py
```

- [ ] **Step 10: Run all tests**

Run: `pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 11: Run linter**

Run: `ruff check .`
Run: `ruff format .`
Expected: No errors

- [ ] **Step 12: Commit**

```bash
git add ascii_render/cli/__init__.py ascii_render/cli/main.py ascii_render/cli/utils.py ascii_render/cli/render_cmd.py ascii_render/cli/interactive_cmd.py ascii_render/__main__.py run_cli.py tests/test_cli.py && git rm ascii_render/cli.py
git commit -m "refactor: split cli.py into cli/ package with separated commands"
```

---

### Task 6: Update `__init__.py` and final verification

**Files:**
- Modify: `ascii_render/__init__.py`

- [ ] **Step 1: Update `__init__.py`**

```python
from .core.renderer import Renderer
from .core.effects import Effect
from .core.pixel_mapper import map_pixels_to_ascii
from .core.image_utils import preprocess_image
from .effects.glow import GlowEffect
from .types import RenderConfig, RenderResult, ColorMode
from .interactive.mouse_canvas import MouseCanvas
from .interactive.ascii_canvas import AsciiArtCanvas

__all__ = [
    "Renderer",
    "Effect",
    "GlowEffect",
    "RenderConfig",
    "RenderResult",
    "ColorMode",
    "MouseCanvas",
    "AsciiArtCanvas",
    "map_pixels_to_ascii",
    "preprocess_image",
]
```

- [ ] **Step 2: Run full test suite**

Run: `pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 3: Run linter and formatter**

Run: `ruff check .`
Run: `ruff format .`

- [ ] **Step 4: Final commit**

```bash
git add ascii_render/__init__.py
git commit -m "refactor: update public API exports with new modules"
```

---

## Verification Summary

After all tasks:
- `pytest tests/ -v` — all tests pass
- `ruff check .` — no lint errors
- `ruff format .` — no formatting issues
- `ascii-render render <image>` — works as before
- `ascii-render interactive <image>` — works as before
- No NumPy dependency added
- No duplicate Effect definitions
- No duplicate rendering logic between Renderer and AsciiArtCanvas
