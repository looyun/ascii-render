# ASCII Render Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python library + CLI tool to render images/GIFs/videos into colored ASCII art with glow effects.

**Architecture:** Modular design with core renderer, plugin-based effects system, and separate IO modules for image loading and ANSI output.

**Tech Stack:** Python 3.10+, Pillow, numpy, opencv-python, click

---

## File Structure

```
ascii_render/
├── ascii_render/
│   ├── __init__.py           # Public API exports
│   ├── __main__.py           # CLI entry point
│   ├── types.py              # Config classes, types
│   ├── core/
│   │   ├── __init__.py
│   │   ├── renderer.py       # Main rendering (grayscale → ASCII)
│   │   ├── dithering.py      # Dithering algorithms
│   │   └── effects.py        # Base Effect class
│   ├── effects/
│   │   ├── __init__.py
│   │   └── glow.py           # Glow/bloom effect
│   └── io/
│       ├── __init__.py
│       ├── loader.py         # Image loading
│       ├── video.py          # Video/GIF processing
│       └── ansi.py           # ANSI color encoding
├── tests/
│   ├── __init__.py
│   ├── test_renderer.py
│   ├── test_effects.py
│   └── test_io.py
├── pyproject.toml
└── README.md
```

---

## Task 1: Project Setup

**Files:**
- Create: `pyproject.toml`
- Create: `README.md`

- [ ] **Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "ascii_render"
version = "0.1.0"
description = "Render images/videos to colored ASCII art with glow effects"
requires-python = ">=3.10"
dependencies = [
    "pillow>=10.0.0",
    "numpy>=1.24.0",
    "opencv-python>=4.8.0",
    "click>=8.0.0",
]

[project.scripts]
ascii-render = "ascii_render.cli:main"

[project.optional-dependencies]
dev = ["pytest>=7.0.0", "pytest-cov>=4.0.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Create basic README.md**

```markdown
# ascii_render

Render images, GIFs, and videos into ASCII art with glow effects.

## Installation

```bash
pip install ascii_render
```

## CLI Usage

```bash
ascii-render input.jpg --width 120 --glow
```

## Library Usage

```python
from ascii_render import Renderer, effects

renderer = Renderer(width=120)
renderer.add_effect(effects.Glow(radius=3, intensity=0.5))
result = renderer.render("image.jpg")
print(result)
```
```

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml README.md
git commit -m "chore: project setup"
```

---

## Task 2: Types and Configuration

**Files:**
- Create: `ascii_render/types.py`

- [ ] **Step 1: Create types.py**

```python
from dataclasses import dataclass, field
from typing import List, Optional, Protocol
from enum import Enum
from PIL import Image


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
    frame_data: List[List[str]]
    dimensions: tuple[int, int]
    colors: List[List[tuple[int, int, int]]] | None = None


class Effect(Protocol):
    def apply(self, image: Image.Image) -> Image.Image:
        """Apply effect to image and return modified image."""
        ...
```

- [ ] **Step 2: Commit**

```bash
git add ascii_render/types.py
git commit -m "feat: add types and configuration classes"
```

---

## Task 3: Core Renderer

**Files:**
- Create: `ascii_render/core/renderer.py`
- Create: `ascii_render/core/__init__.py`

- [ ] **Step 1: Create core/__init__.py**

```python
from .renderer import Renderer

__all__ = ["Renderer"]
```

- [ ] **Step 2: Create core/renderer.py**

```python
from PIL import Image
import numpy as np
from typing import List, Optional

from ..types import RenderConfig, RenderResult, Effect


class Renderer:
    def __init__(self, config: Optional[RenderConfig] = None):
        self.config = config or RenderConfig()
        self._effects: List[Effect] = []

    def add_effect(self, effect: Effect) -> "Renderer":
        self._effects.append(effect)
        return self

    def render(self, image_path: str) -> str:
        from ..io.loader import load_image
        from ..io.ansi import ANSIFormatter
        
        image = load_image(image_path)
        image = self._preprocess(image)
        
        for effect in self._effects:
            image = effect.apply(image)
        
        result = self._render_to_ascii(image)
        formatter = ANSIFormatter(self.config.color_mode)
        return formatter.format(result, image)
    
    def _preprocess(self, image: Image.Image) -> Image.Image:
        if self.config.width or self.config.height:
            target_width = self.config.width or 80
            target_height = self.config.height
            
            if self.config.preserve_aspect:
                orig_w, orig_h = image.size
                aspect = orig_w / orig_h
                char_aspect = 0.5
                target_height = int(target_width / aspect / char_aspect)
            
            image = image.resize((target_width, target_height or target_width // 2))
        
        return image.convert("RGB")
    
    def _render_to_ascii(self, image: Image.Image) -> RenderResult:
        img_array = np.array(image)
        height, width = img_array.shape[:2]
        
        brightness = np.mean(img_array, axis=2) / 255.0
        
        if self.config.invert:
            brightness = 1.0 - brightness
        
        chars = self.config.char_set
        num_chars = len(chars)
        
        frame_data = []
        colors = []
        
        for y in range(height):
            row_chars = []
            row_colors = []
            for x in range(width):
                bright = brightness[y, x]
                char_idx = min(int(bright * num_chars), num_chars - 1)
                char_idx = max(0, char_idx)
                row_chars.append(chars[char_idx])
                row_colors.append(tuple(img_array[y, x]))
            frame_data.append(row_chars)
            colors.append(row_colors)
        
        return RenderResult(
            frame_data=frame_data,
            dimensions=(width, height),
            colors=colors
        )
```

- [ ] **Step 3: Create tests/test_renderer.py**

```python
import pytest
from PIL import Image
import numpy as np
import tempfile
import os

from ascii_render.core.renderer import Renderer
from ascii_render.types import RenderConfig


def test_renderer_basic():
    img = Image.new("RGB", (10, 10), color=(128, 128, 128))
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        img.save(f.name)
        renderer = Renderer(RenderConfig(width=10))
        result = renderer.render(f.name)
        os.unlink(f.name)
        assert len(result) > 0


def test_renderer_invert():
    img = Image.new("RGB", (10, 10), color=(0, 0, 0))
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        img.save(f.name)
        renderer = Renderer(RenderConfig(width=10, invert=True))
        result = renderer.render(f.name)
        os.unlink(f.name)
        assert len(result) > 0
```

- [ ] **Step 4: Run tests**

```bash
pip install -e ".[dev]"
pytest tests/test_renderer.py -v
```

- [ ] **Step 5: Commit**

```bash
git add ascii_render/core/ tests/test_renderer.py
git commit -m "feat: add core renderer with ASCII conversion"
```

---

## Task 4: Effects System

**Files:**
- Create: `ascii_render/core/effects.py`
- Create: `ascii_render/effects/glow.py`
- Create: `ascii_render/effects/__init__.py`
- Modify: `ascii_render/__init__.py`

- [ ] **Step 1: Create core/effects.py**

```python
from abc import ABC, abstractmethod
from PIL import Image


class Effect(ABC):
    @abstractmethod
    def apply(self, image: Image.Image) -> Image.Image:
        """Apply the effect to the image and return the modified image."""
        pass
```

- [ ] **Step 2: Create effects/glow.py**

```python
import numpy as np
from PIL import Image, ImageFilter
from ..core.effects import Effect


class GlowEffect(Effect):
    def __init__(self, radius: int = 3, intensity: float = 0.5, threshold: float = 0.3):
        self.radius = radius
        self.intensity = intensity
        self.threshold = threshold

    def apply(self, image: Image.Image) -> Image.Image:
        img_array = np.array(image).astype(np.float32) / 255.0
        brightness = np.mean(img_array, axis=2)
        
        mask = brightness > self.threshold
        
        blurred = image.filter(ImageFilter.GaussianBlur(radius=self.radius))
        blur_array = np.array(blurred).astype(np.float32) / 255.0
        
        result = img_array.copy()
        for c in range(3):
            result[:, :, c] = np.where(
                mask,
                img_array[:, :, c] + (blur_array[:, :, c] - img_array[:, :, c]) * self.intensity,
                img_array[:, :, c]
            )
        
        result = np.clip(result * 255, 0, 255).astype(np.uint8)
        return Image.fromarray(result)
```

- [ ] **Step 3: Create effects/__init__.py**

```python
from .glow import GlowEffect

__all__ = ["GlowEffect"]
```

- [ ] **Step 4: Create ascii_render/__init__.py**

```python
from .core.renderer import Renderer
from .core.effects import Effect
from .effects.glow import GlowEffect
from .types import RenderConfig, RenderResult, ColorMode

__all__ = [
    "Renderer",
    "Effect",
    "GlowEffect",
    "RenderConfig",
    "RenderResult",
    "ColorMode",
]
```

- [ ] **Step 5: Create tests/test_effects.py**

```python
import pytest
from PIL import Image
import tempfile
import os

from ascii_render.effects.glow import GlowEffect
from ascii_render.core.renderer import Renderer
from ascii_render.types import RenderConfig, ColorMode


def test_glow_effect():
    img = Image.new("RGB", (50, 50), color=(255, 255, 200))
    glow = GlowEffect(radius=2, intensity=0.5, threshold=0.3)
    result = glow.apply(img)
    assert result.size == img.size


def test_renderer_with_glow():
    img = Image.new("RGB", (20, 20), color=(200, 180, 150))
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        img.save(f.name)
        renderer = Renderer(RenderConfig(width=10, color_mode=ColorMode.MODE_8))
        renderer.add_effect(GlowEffect())
        result = renderer.render(f.name)
        os.unlink(f.name)
        assert len(result) > 0
```

- [ ] **Step 6: Run tests**

```bash
pytest tests/test_effects.py -v
```

- [ ] **Step 7: Commit**

```bash
git add ascii_render/core/effects.py ascii_render/effects/ ascii_render/__init__.py tests/test_effects.py
git commit -m "feat: add effects system with glow effect"
```

---

## Task 5: IO Modules

**Files:**
- Create: `ascii_render/io/loader.py`
- Create: `ascii_render/io/video.py`
- Create: `ascii_render/io/ansi.py`
- Create: `ascii_render/io/__init__.py`

- [ ] **Step 1: Create io/loader.py**

```python
from PIL import Image
from pathlib import Path
from typing import Union


def load_image(path: Union[str, Path]) -> Image.Image:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")
    return Image.open(path)
```

- [ ] **Step 2: Create io/ansi.py**

```python
from PIL import Image
from ..types import ColorMode, RenderResult


class ANSIFormatter:
    ESCAPE = "\033"
    RESET = f"{ESCAPE}[0m"
    BOLD = f"{ESCAPE}[1m"

    def __init__(self, mode: ColorMode = ColorMode.TRUECOLOR):
        self.mode = mode

    def _truecolor(self, r: int, g: int, b: int) -> str:
        return f"{self.ESCAPE}[38;2;{r};{g};{b}m"

    def _color_256(self, r: int, g: int, b: int) -> str:
        gray = (r * 30 + g * 59 + b * 11) // 100
        return f"{self.ESCAPE}[38;5;{min(232 + gray, 255)}m"

    def _color_8(self, r: int, g: int, b: int) -> str:
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        brightness = (max_c + min_c) // 2
        color_idx = 30 + (1 if r > 128 else 4 if g > 128 else 2 if b > 128 else 0)
        return f"{self.ESCAPE}[{color_idx}m"

    def format(self, result: RenderResult, image: Image.Image) -> str:
        if self.mode == ColorMode.TRUECOLOR:
            color_fn = self._truecolor
        elif self.mode == ColorMode.MODE_256:
            color_fn = self._color_256
        else:
            color_fn = self._color_8

        lines = []
        for y, row in enumerate(result.frame_data):
            line_chars = []
            for x, char in enumerate(row):
                if result.colors and x < len(result.colors[y]):
                    r, g, b = result.colors[y][x]
                    line_chars.append(f"{color_fn(r, g, b)}{char}")
                else:
                    line_chars.append(char)
            lines.append("".join(line_chars) + self.RESET)
        
        return "\n".join(lines)
```

- [ ] **Step 3: Create io/video.py**

```python
from PIL import Image
from typing import Iterator, Union, Optional
import numpy as np


class VideoProcessor:
    @staticmethod
    def read_gif(path: str) -> Iterator[Image.Image]:
        img = Image.open(path)
        try:
            while True:
                yield img.copy()
                img.seek(img.tell() + 1)
        except EOFError:
            pass

    @staticmethod
    def read_video_frames(
        path: str,
        max_frames: Optional[int] = None
    ) -> Iterator[Image.Image]:
        try:
            import cv2
        except ImportError:
            raise ImportError("opencv-python is required for video processing")
        
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {path}")
        
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            yield Image.fromarray(frame_rgb)
            frame_count += 1
            if max_frames and frame_count >= max_frames:
                break
        
        cap.release()
```

- [ ] **Step 4: Create io/__init__.py**

```python
from .loader import load_image
from .video import VideoProcessor
from .ansi import ANSIFormatter

__all__ = ["load_image", "VideoProcessor", "ANSIFormatter"]
```

- [ ] **Step 5: Create tests/test_io.py**

```python
import pytest
from PIL import Image
import tempfile
import os

from ascii_render.io.ansi import ANSIFormatter
from ascii_render.io.loader import load_image
from ascii_render.types import RenderResult, ColorMode


def test_ansi_formatter_truecolor():
    formatter = ANSIFormatter(ColorMode.TRUECOLOR)
    result = RenderResult(
        frame_data=[["@", "#"], [".", " "]],
        dimensions=(2, 2),
        colors=[[(255, 100, 50), (0, 0, 0)], [(128, 128, 128), (255, 255, 255)]]
    )
    img = Image.new("RGB", (2, 2))
    formatted = formatter.format(result, img)
    assert "\033[38;2;" in formatted
    assert "@" in formatted


def test_load_image():
    img = Image.new("RGB", (10, 10), color=(100, 100, 100))
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        img.save(f.name)
        loaded = load_image(f.name)
        os.unlink(f.name)
        assert loaded.size == (10, 10)
```

- [ ] **Step 6: Run tests**

```bash
pytest tests/test_io.py -v
```

- [ ] **Step 7: Commit**

```bash
git add ascii_render/io/ tests/test_io.py
git commit -m "feat: add IO modules for image loading, video processing, and ANSI formatting"
```

---

## Task 6: CLI Interface

**Files:**
- Create: `ascii_render/__main__.py`
- Create: `ascii_render/cli.py`

- [ ] **Step 1: Create cli.py**

```python
import click
from pathlib import Path
from typing import Optional

from .core.renderer import Renderer
from .effects.glow import GlowEffect
from .types import RenderConfig, ColorMode
from .io.video import VideoProcessor


@click.command()
@click.argument("input", type=click.Path(exists=True))
@click.option("--width", "-w", default=80, help="Output width in characters")
@click.option("--height", "-H", default=None, type=int, help="Output height (auto if not set)")
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
    help="Color mode"
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
    
    color_map = {"8": ColorMode.MODE_8, "256": ColorMode.MODE_256, "truecolor": ColorMode.TRUECOLOR}
    
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
        frames = processor.read_gif(str(input_path)) if is_gif else processor.read_video_frames(str(input_path))
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
```

- [ ] **Step 2: Create __main__.py**

```python
from .cli import main

if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Create tests/test_cli.py**

```python
import pytest
from click.testing import CliRunner
import tempfile
import os
from PIL import Image

from ascii_render.cli import main


@pytest.fixture
def temp_image():
    img = Image.new("RGB", (20, 20), color=(150, 100, 50))
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        img.save(f.name)
        yield f.name
    os.unlink(f.name)


def test_cli_basic(temp_image):
    runner = CliRunner()
    result = runner.invoke(main, [temp_image, "--width", "20"])
    assert result.exit_code == 0
    assert len(result.output) > 0


def test_cli_with_glow(temp_image):
    runner = CliRunner()
    result = runner.invoke(main, [temp_image, "--width", "20", "--glow"])
    assert result.exit_code == 0


def test_cli_output_file(temp_image):
    runner = CliRunner()
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        output_path = f.name
    result = runner.invoke(main, [temp_image, "--width", "20", "--output", output_path])
    os.unlink(output_path)
    assert result.exit_code == 0
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_cli.py -v
```

- [ ] **Step 5: Commit**

```bash
git add ascii_render/cli.py ascii_render/__main__.py tests/test_cli.py
git commit -m "feat: add CLI interface with glow effect support"
```

---

## Task 7: Final Integration

**Files:**
- Modify: `ascii_render/__init__.py` (add io exports if needed)
- Create: `tests/__init__.py`

- [ ] **Step 1: Create tests/__init__.py**

```python
```

- [ ] **Step 2: Run all tests**

```bash
pytest tests/ -v
```

- [ ] **Step 3: Test CLI manually**

```bash
pip install -e .
echo "Test image" | python -c "from PIL import Image; img = Image.new('RGB', (40, 20), (200, 150, 100)); img.save('/tmp/test.png')"
ascii-render /tmp/test.png --width 60 --glow
```

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: complete ASCII render library with glow effects"
```

---

## Self-Review Checklist

- [ ] Spec coverage: All features from design spec implemented
- [ ] No placeholders: All code blocks filled, no TODOs
- [ ] Type consistency: RenderConfig, Effect, RenderResult used consistently
- [ ] Tests: Each task has corresponding tests
- [ ] Dependencies: All listed in pyproject.toml

---

**Plan complete and saved to `docs/superpowers/plans/2026-03-29-ascii-render-plan.md`.**

**Two execution options:**

**1. Subagent-Driven (recommended)** - Dispatch fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
