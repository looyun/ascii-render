"""Tests for core pixel_mapper and image_utils."""

from PIL import Image
from ascii_render.core.pixel_mapper import map_pixels_to_ascii
from ascii_render.core.image_utils import preprocess_image


def test_map_pixels_to_ascii_basic():
    img = Image.new("RGB", (4, 4), color=(128, 128, 128))
    result = map_pixels_to_ascii(img, " .:-=+*#%@")
    assert result.dimensions == (4, 4)
    assert len(result.char_indices) == 4
    assert len(result.colors) == 4
    assert all(len(row) == 4 for row in result.char_indices)
    assert all(len(row) == 4 for row in result.colors)


def test_map_pixels_to_ascii_invert():
    img = Image.new("RGB", (2, 2), color=(0, 0, 0))
    result = map_pixels_to_ascii(img, " .:-=+*#%@", invert=True)
    assert result.dimensions == (2, 2)
    # Black (0) inverted should map to highest brightness → highest char index


def test_map_pixels_to_ascii_colors():
    img = Image.new("RGB", (1, 1), color=(255, 100, 50))
    result = map_pixels_to_ascii(img, " .:-=+*#%@")
    assert result.colors[0][0] == (255, 100, 50)


def test_map_pixels_to_ascii_char_indices_range():
    """All char indices should be within valid range."""
    img = Image.new("RGB", (10, 10), color=(200, 200, 200))
    result = map_pixels_to_ascii(img, " .:-=+*#%@")
    num_chars = 10
    for row in result.char_indices:
        for idx in row:
            assert 0 <= idx < num_chars


def test_preprocess_resize():
    img = Image.new("RGB", (100, 100), color=(128, 128, 128))
    result = preprocess_image(img, 20, 10, preserve_aspect=False)
    assert result.size == (20, 10)
    assert result.mode == "RGB"


def test_preprocess_rgba_to_rgb():
    img = Image.new("RGBA", (10, 10), color=(128, 128, 128, 200))
    result = preprocess_image(img, 10, 10, preserve_aspect=False)
    assert result.mode == "RGB"


def test_preprocess_preserve_aspect():
    img = Image.new("RGB", (200, 100), color=(128, 128, 128))
    result = preprocess_image(img, 40, 20, preserve_aspect=True)
    assert result.mode == "RGB"
    assert result.size[0] <= 40
    assert result.size[1] <= 20
