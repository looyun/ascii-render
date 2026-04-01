# AGENTS.md

## Project Overview

This is an ASCII renderer library that converts images and videos to colored ASCII art with optional glow effects. It uses Pillow for image processing, NumPy for numerical operations, OpenCV for video processing, and Click for the CLI.

## Commands

### Development Environment

```bash
# Activate virtual environment
source venv/bin/activate
# Or with uv
uv sync
```

### Build & Install

```bash
# Install in editable mode
pip install -e .

# Install with dev dependencies
pip install -e ".[dev]"
```

### Linting & Formatting

```bash
# Run ruff linter
ruff check .

# Run ruff with auto-fix
ruff check --fix .

# Format with ruff
ruff format .
```

### Testing

```bash
# Run all tests
pytest

# Run a specific test file
pytest tests/test_renderer.py

# Run a specific test by name
pytest tests/test_renderer.py::test_renderer_basic -v

# Run with coverage
pytest --cov=ascii_render --cov-report=term-missing
```

## Code Style Guidelines

### Imports

- Standard library imports first, then third-party, then local
- Use absolute imports (e.g., `from ascii_render.core.renderer import Renderer`)
- Group imports: stdlib, third-party, local
- Avoid wildcard imports (`from xxx import *`)

```python
# Correct
import os
import sys
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image
from PIL.ImageFilter import GaussianBlur

from ascii_render.types import ColorMode, RenderConfig
from ascii_render.effects.glow import GlowEffect
```

### Types

- Use Python 3.10+ type hints throughout
- Use `Optional[X]` instead of `X | None` for broader compatibility
- Use dataclasses for configuration objects and results
- Use Protocol for interface definitions

```python
from dataclasses import dataclass
from typing import Protocol, Iterator, Optional
from enum import Enum

class ColorMode(Enum):
    MODE_8 = 8
    MODE_256 = 256
    TRUECOLOR = "truecolor"

@dataclass
class RenderConfig:
    width: int = 80
    height: Optional[int] = None

class Effect(Protocol):
    def apply(self, image: Image.Image) -> Image.Image:
        ...
```

### Naming Conventions

- **Classes**: PascalCase (e.g., `Renderer`, `GlowEffect`)
- **Functions/methods**: snake_case (e.g., `render()`, `_preprocess()`)
- **Constants**: SCREAMING_SNAKE_CASE (e.g., `ESCAPE = "\033"`)
- **Private methods**: prefix with underscore (e.g., `_render_to_ascii()`)
- **Instance variables**: snake_case (e.g., `self.config`)

### Functions

- Keep functions small and focused
- Use descriptive names that explain intent
- Add docstrings for public APIs
- Use type hints for all parameters and return values

```python
def render(self, image_path: str) -> str:
    """Render an image to ASCII art.
    
    Args:
        image_path: Path to the image file.
        
    Returns:
        ANSI-escaped ASCII art string.
    """
```

### Error Handling

- Use specific exception types
- Provide helpful error messages with context
- Handle errors at appropriate levels (don't catch everything)

```python
# Good
if not path.exists():
    raise FileNotFoundError(f"Image not found: {path}")

# Good
if not cap.isOpened():
    raise ValueError(f"Cannot open video: {path}")
```

### Classes

- Use dataclasses for simple data containers
- Use Protocol for duck-typing interfaces
- Keep classes focused on single responsibility
- Use method chaining where appropriate

```python
class Renderer:
    def add_effect(self, effect: Effect) -> "Renderer":
        self._effects.append(effect)
        return self
```

### NumPy Best Practices

- Use `np.float32` for intermediate calculations to save memory
- Use in-place operations where possible (e.g., `np.clip(..., out=...)`)
- Prefer vectorized operations over loops

```python
# Good
char_indices = (brightness * num_chars).astype(np.int32)
np.clip(char_indices, 0, num_chars - 1, out=char_indices)

# Avoid
for i in range(height):
    for j in range(width):
        char_indices[i, j] = int(brightness[i, j] * num_chars)
```

### PIL/Image Handling

- Convert RGBA to RGB before processing when needed
- Use `np.array()` and `Image.fromarray()` for conversions
- Handle transparency explicitly

```python
if image.mode == "RGBA":
    background = Image.new("RGB", image.size, (0, 0, 0))
    background.paste(image, mask=image.split()[3])
    return background
return image.convert("RGB")
```

### CLI (Click)

- Use Click decorators for argument parsing
- Provide sensible defaults
- Use type hints for CLI functions
- Handle cleanup in finally blocks

## Testing Guidelines

- Create test files in `tests/` directory
- Name test files `test_<module>.py`
- Use pytest fixtures for setup
- Test one thing per test function
- Use temporary files for file I/O tests

```python
def test_renderer_basic():
    img = Image.new("RGB", (10, 10), color=(128, 128, 128))
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        img.save(f.name)
        renderer = Renderer(RenderConfig(width=10))
        result = renderer.render(f.name)
        os.unlink(f.name)
        assert len(result) > 0
```

## File Structure

```
ascii_render/
├── __init__.py          # Public API exports
├── cli.py               # Command-line interface
├── types.py             # Type definitions, enums, dataclasses
├── core/
│   ├── renderer.py      # Main renderer class
│   └── effects.py       # Effect protocol
├── effects/
│   └── glow.py          # Glow effect implementation
└── io/
    ├── ansi.py          # ANSI color formatting
    ├── loader.py        # Image loading
    └── video.py         # Video/GIF processing

tests/
├── test_renderer.py
├── test_effects.py
├── test_io.py
└── test_cli.py
```