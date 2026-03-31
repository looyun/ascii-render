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

### Video/GIF Options

```bash
# Play video
ascii-render video.mp4

# Play with glow effect
ascii-render video.mp4 --glow

# Loop video playback
ascii-render video.mp4 --loop

# Custom frame rate
ascii-render video.mp4 --fps 24

# Full options
ascii-render video.mp4 --width 120 --height 40 --glow --loop --fps 30
```

### All Options

| Option | Description |
|--------|-------------|
| `-w, --width` | Output width in characters (auto-detect by default) |
| `-H, --height` | Output height (auto-detect if not set) |
| `-c, --chars` | Character set for ASCII art |
| `-i, --invert` | Invert brightness |
| `--glow` | Enable glow effect |
| `--glow-radius` | Glow radius (default: 3) |
| `--glow-intensity` | Glow intensity 0-1 (default: 0.5) |
| `--highlight` | Enable bold/highlight text |
| `--loop` | Loop video playback |
| `--fps` | Video frame rate (default: 30) |
| `-o, --output` | Output file instead of playing |
| `--color-mode` | Color mode: 8, 256, or truecolor (default: truecolor) |

Controls: Press `q` or `Ctrl+C` to stop playback.

## Library Usage

```python
from ascii_render import Renderer, effects

renderer = Renderer(width=120)
renderer.add_effect(effects.Glow(radius=3, intensity=0.5))
result = renderer.render("image.jpg")
print(result)
```
