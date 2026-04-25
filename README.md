# ascii_render

Render images, GIFs, and videos into ASCII art with glow effects.

## Installation

```bash
pip install ascii_render
```

For video support, install with the video extra:

```bash
pip install ascii_render[video]
```

## CLI Usage

The CLI provides two subcommands: `render` and `interactive`.

### Render Subcommand

```bash
# Render an image
ascii-render render input.jpg --width 120 --glow

# Render a video
ascii-render render video.mp4

# Render with glow effect
ascii-render render video.mp4 --glow

# Loop video playback
ascii-render render video.mp4 --loop

# Custom frame rate
ascii-render render video.mp4 --fps 24

# Full options
ascii-render render video.mp4 --width 120 --height 40 --glow --loop --fps 30
```

#### Render Options

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
| `--show-frame` | Show frame number during playback |
| `--fps` | Video frame rate |
| `-o, --output` | Output file instead of playing |
| `--color-mode` | Color mode: 8, 256, or truecolor (default: truecolor) |

Controls: Press `q` or `Ctrl+C` to stop playback.

### Interactive Subcommand

Render an image or GIF as interactive ASCII art that follows mouse clicks.

```bash
# Interactive image
ascii-render interactive input.jpg

# Interactive GIF
ascii-render interactive animation.gif

# With drag mode
ascii-render interactive input.jpg --drag

# Custom size
ascii-render interactive input.jpg --size 40
```

#### Interactive Options

| Option | Description |
|--------|-------------|
| `-s, --size` | Canvas short-side size in rows (default: 30) |
| `-c, --chars` | Character set for ASCII art |
| `-i, --invert` | Invert brightness |
| `--glow` | Enable glow effect (static images only) |
| `--glow-radius` | Glow radius (default: 3) |
| `--glow-intensity` | Glow intensity 0-1 (default: 0.5) |
| `--color-mode` | Color mode: 8, 256, or truecolor (default: truecolor) |
| `--loop / --no-loop` | Loop GIF playback (default: enabled) |
| `--drag` | Enable drag mode (click and drag canvas) |

Controls: Press `Ctrl+C` to exit interactive mode.

## Library Usage

```python
from ascii_render import Renderer, RenderConfig, GlowEffect

config = RenderConfig(width=120)
renderer = Renderer(config)
renderer.add_effect(GlowEffect(radius=3, intensity=0.5))
result = renderer.render("image.jpg")
print(result)
```
