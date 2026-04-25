# Refactoring Design: Render & Interactive Code Reorganization

## Date: 2026-04-04

## Overview

Comprehensive refactoring to eliminate code duplication between `Renderer` and `AsciiArtCanvas`, extract CLI logic into a proper package, and unify the `Effect` type definition.

## 1. Directory Structure

### Current
```
ascii_render/
├── cli.py               # 373 lines, does too much
├── types.py             # Has Effect Protocol (duplicates ABC)
├── core/
│   ├── renderer.py      # Has _preprocess, _render_to_ascii
│   └── effects.py       # Effect ABC
├── interactive/
│   ├── mouse_canvas.py
│   └── ascii_canvas.py  # Duplicates _prepare_image, _render_frame_to_ascii
└── io/
    ├── ansi.py
    ├── loader.py
    └── video.py
```

### Target
```
ascii_render/
├── cli/
│   ├── __init__.py
│   ├── main.py              # Click group, download_if_url
│   ├── render_cmd.py        # render subcommand
│   ├── interactive_cmd.py   # interactive subcommand
│   └── utils.py             # terminal size, video playback loop, frame display
├── types.py                 # Remove Effect Protocol, keep ColorMode, RenderConfig, RenderResult
├── core/
│   ├── __init__.py
│   ├── renderer.py          # Simplified, delegates to pixel_mapper + image_utils
│   ├── effects.py           # Single Effect ABC definition
│   ├── pixel_mapper.py      # NEW: brightness → char indices + color extraction
│   └── image_utils.py       # NEW: resize + RGBA→RGB
├── effects/
│   ├── __init__.py
│   └── glow.py              # Inherits from core.effects.Effect
├── interactive/
│   ├── __init__.py
│   ├── mouse_canvas.py      # Unchanged
│   └── ascii_canvas.py      # Uses pixel_mapper + image_utils, removes duplicate logic
└── io/
    ├── __init__.py
    ├── ansi.py              # Unchanged
    ├── loader.py            # Unchanged
    └── video.py             # Unchanged
```

## 2. Core Module Design

### `core/pixel_mapper.py`

Single function that converts a PIL Image to `RenderResult`. Replaces the pixel-loop logic in both `Renderer._render_to_ascii()` and `AsciiArtCanvas._render_frame_to_ascii()`.

```python
def map_pixels_to_ascii(
    image: Image.Image,
    char_set: str,
    invert: bool = False,
) -> RenderResult:
    """Convert PIL Image to RenderResult (char_indices + colors).
    
    Args:
        image: RGB PIL Image (must be preprocessed).
        char_set: String of ASCII characters ordered by brightness.
        invert: If True, invert brightness mapping.
    
    Returns:
        RenderResult with char_indices, colors, and dimensions.
    """
```

### `core/image_utils.py`

Single function for image preprocessing. Replaces `Renderer._preprocess()` and `AsciiArtCanvas._prepare_image()`.

```python
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
```

### `core/effects.py`

Becomes the single source of truth for `Effect`. Currently `types.py` defines `Effect` as a `Protocol` and `core/effects.py` defines it as an `ABC`. We keep the ABC and remove the Protocol from `types.py`.

```python
from abc import ABC, abstractmethod
from PIL import Image

class Effect(ABC):
    @abstractmethod
    def apply(self, image: Image.Image) -> Image.Image:
        """Apply effect to image and return modified image."""
        ...
```

## 3. CLI Split Design

### `cli/main.py`

- `main()` Click group function
- `download_if_url()` helper
- Imports and registers `render_cmd` and `interactive_cmd`

### `cli/render_cmd.py`

- `render_cmd()` — the `render` subcommand with all its Click options
- Delegates video/GIF playback to `cli.utils.play_video()`
- Delegates single-frame rendering to `cli.utils.display_frame()`

### `cli/interactive_cmd.py`

- `interactive()` — the `interactive` subcommand
- `create_canvas()` helper to build the appropriate canvas (static, glow-processed, or GIF)

### `cli/utils.py`

- `get_terminal_width()` / `get_terminal_height()` — terminal size detection
- `play_video()` — encapsulates the entire video playback loop:
  - Terminal raw mode setup/teardown
  - Frame iteration with timing
  - Resize detection
  - Keyboard input (q to quit)
  - Frame counter display
- `display_frame()` — single frame: preprocess → effects → map_pixels → format → output

## 4. AsciiArtCanvas Simplification

`AsciiArtCanvas` currently duplicates:
- `_prepare_image()` → replaced by `image_utils.preprocess_image()`
- `_render_frame_to_ascii()` → replaced by `pixel_mapper.map_pixels_to_ascii()` + ANSI formatting

After refactoring:

```python
class AsciiArtCanvas(MouseCanvas):
    def _render_frame_to_ascii(self, image, rows=None, cols=None) -> list[str]:
        result = map_pixels_to_ascii(image, self._config.char_set, self._config.invert)
        # Build ANSI strings from RenderResult (canvas-specific: needs per-line formatting)
        ...

    def _prepare_image(self, image, width, height) -> Image.Image:
        return preprocess_image(image, width, height, preserve_aspect=False)
```

## 5. Public API Updates (`__init__.py`)

```python
__all__ = [
    "Renderer",
    "Effect",              # Now from core.effects (ABC)
    "GlowEffect",
    "RenderConfig",
    "RenderResult",
    "ColorMode",
    "MouseCanvas",
    "AsciiArtCanvas",
    "map_pixels_to_ascii", # New
    "preprocess_image",    # New
]
```

## 6. Import Changes

| File | Before | After |
|------|--------|-------|
| `core/renderer.py` | `from ..types import Effect` | `from .effects import Effect` |
| `core/renderer.py` | inline `_preprocess`, `_render_to_ascii` | `from .image_utils import preprocess_image`<br>`from .pixel_mapper import map_pixels_to_ascii` |
| `effects/glow.py` | `from ascii_render.core.effects import Effect` | unchanged |
| `interactive/ascii_canvas.py` | inline `_prepare_image`, `_render_frame_to_ascii` | `from ascii_render.core.image_utils import preprocess_image`<br>`from ascii_render.core.pixel_mapper import map_pixels_to_ascii` |
| `cli/main.py` | (was cli.py) | imports from `cli.render_cmd`, `cli.interactive_cmd` |
| `cli/render_cmd.py` | (was cli.py) | imports from `cli.utils`, `ascii_render.core.*` |
| `cli/interactive_cmd.py` | (was cli.py) | imports from `cli.utils`, `ascii_render.interactive.*` |
| `types.py` | `class Effect(Protocol)` | removed |

## 7. Test Updates

Tests will need import path updates:
- `test_renderer.py` — imports unchanged (Renderer public API stays the same)
- `test_interactive.py` — imports unchanged
- `test_cli.py` — update `from ascii_render.cli import main` → `from ascii_render.cli.main import main`
- `test_effects.py` — update Effect import to `from ascii_render.core.effects import Effect`
