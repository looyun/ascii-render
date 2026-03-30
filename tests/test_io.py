import pytest
from PIL import Image
import tempfile
import os
import numpy as np

from ascii_render.io.ansi import ANSIFormatter
from ascii_render.io.loader import load_image
from ascii_render.types import RenderResult, ColorMode


def test_ansi_formatter_truecolor():
    formatter = ANSIFormatter(ColorMode.TRUECOLOR, " .:-=+*#%@")
    char_indices = np.array([[0, 1], [2, 3]])
    colors = np.array([[[255, 100, 50], [0, 0, 0]], [[128, 128, 128], [255, 255, 255]]])
    result = RenderResult(
        char_indices=char_indices,
        dimensions=(2, 2),
        colors=colors,
    )
    formatted = formatter.format(result)
    assert "\033[38;2;" in formatted
    assert " " in formatted or "." in formatted


def test_load_image():
    img = Image.new("RGB", (10, 10), color=(100, 100, 100))
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        img.save(f.name)
        loaded = load_image(f.name)
        os.unlink(f.name)
        assert loaded.size == (10, 10)
