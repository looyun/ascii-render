# ASCII Render Design Specification

**Date**: 2026-03-29
**Status**: Approved

## 1. Overview

**Project Name**: ascii_render
**Type**: Python Library + CLI Tool

**Goal**: Render images, GIFs, and videos into ASCII art with lighting effects (glow), outputting colored ANSI terminal format.

**Core Technologies**:
- Pillow: Image loading, preprocessing
- numpy: Matrix operations (convolution, brightness calculation)
- OpenCV: Video frame extraction

---

## 2. Architecture

```
ascii_render/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── renderer.py      # Main rendering engine
│   ├── dithering.py     # Dithering algorithms
│   └── effects.py       # Base effect class
├── effects/
│   ├── __init__.py
│   ├── glow.py          # Glow/bloom effect
│   └── scanline.py      # Scanline effect (extensible)
├── io/
│   ├── __init__.py
│   ├── loader.py        # Image loading (PNG/JPG/GIF/WebP)
│   ├── video.py         # Video/GIF processing
│   └── ansi.py          # ANSI color encoding
├── cli.py               # CLI entry point
└── types.py             # Type definitions, config classes
```

---

## 3. Core Modules

### 3.1 `core/renderer.py`
- `Renderer` class
- Input: PIL Image
- Config: `char_set`, `invert`, `color`
- Output: `RenderResult(frame_data, dimensions)`

### 3.2 `effects/glow.py`
- `GlowEffect` class, extends `Effect` base
- Parameters: `radius`, `intensity` (0-1), `threshold`
- Algorithm: Gaussian blur → blend with original → threshold cutoff

### 3.3 `io/video.py`
- `VideoProcessor` class
- Supports: GIF (direct frame reading), video files (OpenCV)
- Method: `read_frames()` returns frame iterator

### 3.4 `io/ansi.py`
- `ANSIFormatter` class
- Grayscale → ANSI 256-color mapping
- Color modes: 8-color, 256-color, Truecolor (24-bit)
- Output: String with ANSI escape codes

---

## 4. Data Flow

```
Image/Video → Loader → Preprocess (resize, crop)
                           ↓
                      Effects Pipeline
                           ↓
              ┌──────────┴──────────┐
              ↓                     ↓
         GlowEffect           Other Effects
              ↓                     ↓
              └──────────┬──────────┘
                         ↓
                    Renderer
                         ↓
                    ANSIFormatter
                         ↓
                      Output (ANSI)
```

---

## 5. CLI Design

```bash
ascii_render [OPTIONS] INPUT

INPUT: Image path / GIF path / Video path

OPTIONS:
  --width, -w         Output width in characters (default: 80)
  --height, -H        Output height (auto aspect ratio if not set)
  --chars, -c         Character set (default: " .:-=+*#%@")
  --invert, -i        Invert brightness
  --glow              Enable glow effect
  --glow-radius       Glow radius (default: 3)
  --glow-intensity    Glow intensity (default: 0.5)
  --fps               Video frame rate (default: 30)
  --output, -o        Output file (default: stdout)
  --color-mode        Color mode: 8/256/truecolor (default: truecolor)
```

---

## 6. Effect System

Plugin-based design:
```python
class Effect(ABC):
    @abstractmethod
    def apply(self, image: Image) -> Image: pass

class GlowEffect(Effect):
    def __init__(self, radius=3, intensity=0.5, threshold=0.3): ...
```

Custom effect chain:
```python
from ascii_render import Renderer, effects

renderer = Renderer(width=120)
renderer.add_effect(effects.Glow(radius=5, intensity=0.7))
result = renderer.render("image.jpg")
```

---

## 7. Key Algorithms

**Glow Effect**:
1. Apply Gaussian blur to original image (adjustable radius)
2. Calculate brightness for each pixel
3. If brightness > threshold, blend blurred version with original
4. Intensity controls blend strength

**Grayscale → ASCII Mapping**:
1. Calculate average brightness of each character (sampled rendering)
2. Map grayscale value range to character index
3. Optional dithering for improved detail

---

## 8. Dependencies

```
pillow>=10.0.0
numpy>=1.24.0
opencv-python>=4.8.0  # Video functionality only
click>=8.0.0          # CLI framework
```

---

## 9. Output Format

Output is colored ANSI terminal format:
- Bright areas use characters like `@`, `#`, `%`
- Dark areas use `.`, ` ` (space), `-`
- Colors rendered using ANSI escape codes (Truecolor by default)

Example output pattern:
```
[38;2;255;200;100m@[m[38;2;255;180;80m#[m...
```

Where `[38;2;R;G;Bm` is the Truecolor foreground code and `[m` resets formatting.
