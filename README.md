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
