"""Tests for interactive module."""

import tempfile
import os
from PIL import Image
from ascii_render.types import RenderConfig, ColorMode

TERM_SIZE = (80, 24)


def test_mouse_canvas_init():
    from ascii_render.interactive.mouse_canvas import MouseCanvas

    canvas = MouseCanvas(size=10, term_size=TERM_SIZE)
    assert canvas.size == 10
    assert canvas.rows == 10
    assert canvas.cols == 20
    assert canvas.x == 40.0
    assert canvas.y == 12.0


def test_mouse_canvas_set_target():
    from ascii_render.interactive.mouse_canvas import MouseCanvas

    canvas = MouseCanvas(size=10, term_size=TERM_SIZE)
    canvas.set_target(40, 12)
    assert canvas.target_x == 40.0
    assert canvas.target_y == 12.0


def test_mouse_canvas_update_moves_toward_target():
    from ascii_render.interactive.mouse_canvas import MouseCanvas

    canvas = MouseCanvas(size=10, term_size=TERM_SIZE)
    canvas._move_speed = 100.0  # fast speed for test
    canvas.set_target(70, 20)

    # Simulate time passing between updates
    import time

    for _ in range(100):
        canvas._last_update_time = time.monotonic() - 0.033
        canvas.update()

    assert abs(canvas.x - 70) < 1
    assert abs(canvas.y - 20) < 1


def test_mouse_canvas_on_click_callback():
    from ascii_render.interactive.mouse_canvas import MouseCanvas

    canvas = MouseCanvas(size=10, term_size=TERM_SIZE)
    clicks = []
    canvas.on_click(lambda col, row: clicks.append((col, row)))

    canvas._pending_click = (50, 20)

    result = canvas.clicked
    assert result == (50, 20)
    assert canvas.clicked is None


def test_ascii_art_canvas_init():
    from ascii_render.interactive.ascii_canvas import AsciiArtCanvas

    img = Image.new("RGB", (40, 20), color=(128, 128, 128))
    canvas = AsciiArtCanvas(image=img, size=10, term_size=TERM_SIZE)
    assert canvas.size == 10
    assert canvas.rows == 10
    assert canvas.cols == 20
    assert len(canvas._static_ascii) == 10


def test_ascii_art_canvas_render():
    from ascii_render.interactive.ascii_canvas import AsciiArtCanvas

    img = Image.new("RGB", (40, 20), color=(255, 0, 0))
    canvas = AsciiArtCanvas(image=img, size=5, term_size=TERM_SIZE)
    resized = img.resize((10, 5))
    lines = canvas._render_frame_to_ascii(resized, 5, 10)
    assert len(lines) == 5
    for line in lines:
        assert len(line) > 0


def test_ascii_art_canvas_invert():
    from ascii_render.interactive.ascii_canvas import AsciiArtCanvas

    img = Image.new("RGB", (20, 10), color=(200, 200, 200))
    config = RenderConfig(invert=True)
    canvas = AsciiArtCanvas(image=img, size=5, config=config, term_size=TERM_SIZE)
    lines = canvas._static_ascii
    assert len(lines) == 5


def test_ascii_art_canvas_gif():
    from ascii_render.interactive.ascii_canvas import AsciiArtCanvas

    frames = [
        Image.new("RGB", (20, 10), color=(255, 0, 0)),
        Image.new("RGB", (20, 10), color=(0, 255, 0)),
        Image.new("RGB", (20, 10), color=(0, 0, 255)),
    ]

    def frame_gen():
        yield from frames

    canvas = AsciiArtCanvas(
        image=frames[0],
        size=5,
        frames=frame_gen(),
        frame_delay=0.001,
        term_size=TERM_SIZE,
    )

    assert canvas._frames is not None
    assert canvas._static_ascii == []

    canvas._next_frame()
    assert canvas._frame_index == 1

    import time

    time.sleep(0.005)
    canvas._next_frame()
    assert canvas._frame_index == 2
