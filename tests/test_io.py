import pytest
from PIL import Image
import tempfile
import os

from ascii_render.io.ansi import ANSIFormatter
from ascii_render.io.loader import load_image
from ascii_render.io.video import VideoProcessor
from ascii_render.types import RenderResult, ColorMode


def test_ansi_formatter_truecolor():
    formatter = ANSIFormatter(ColorMode.TRUECOLOR, " .:-=+*#%@")
    char_indices = [[0, 1], [2, 3]]
    colors = [[(255, 100, 50), (0, 0, 0)], [(128, 128, 128), (255, 255, 255)]]
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


def test_color_mode_from_string():
    assert ColorMode.from_string("8") == ColorMode.MODE_8
    assert ColorMode.from_string("256") == ColorMode.MODE_256
    assert ColorMode.from_string("truecolor") == ColorMode.TRUECOLOR
    assert ColorMode.from_string("TRUECOLOR") == ColorMode.TRUECOLOR
    assert ColorMode.from_string("TrueColor") == ColorMode.TRUECOLOR

    with pytest.raises(ValueError):
        ColorMode.from_string("invalid")


def test_video_processor_read_gif_streaming():
    """read_gif should yield frames without loading all into memory first."""
    frames = [
        Image.new("RGB", (10, 10), color=(255, 0, 0)),
        Image.new("RGB", (10, 10), color=(0, 255, 0)),
        Image.new("RGB", (10, 10), color=(0, 0, 255)),
    ]

    with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as f:
        frames[0].save(
            f.name,
            save_all=True,
            append_images=frames[1:],
            duration=100,
            loop=0,
        )
        path = f.name

    try:
        count = 0
        for frame in VideoProcessor.read_gif(path):
            assert isinstance(frame, Image.Image)
            assert frame.size == (10, 10)
            count += 1
        assert count == 3

        fps = VideoProcessor.get_gif_info(path)
        assert fps is not None
        assert fps == 10.0
    finally:
        os.unlink(path)
