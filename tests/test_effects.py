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
