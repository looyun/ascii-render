import pytest
from PIL import Image
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
