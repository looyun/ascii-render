import pytest
from click.testing import CliRunner
import tempfile
import os
from PIL import Image

from ascii_render.cli import main


@pytest.fixture
def temp_image():
    img = Image.new("RGB", (20, 20), color=(150, 100, 50))
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        img.save(f.name)
        yield f.name
    os.unlink(f.name)


def test_cli_basic(temp_image):
    runner = CliRunner()
    result = runner.invoke(main, [temp_image, "--width", "20"])
    assert result.exit_code == 0
    assert len(result.output) > 0


def test_cli_with_glow(temp_image):
    runner = CliRunner()
    result = runner.invoke(main, [temp_image, "--width", "20", "--glow"])
    assert result.exit_code == 0


def test_cli_output_file(temp_image):
    runner = CliRunner()
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        output_path = f.name
    result = runner.invoke(main, [temp_image, "--width", "20", "--output", output_path])
    os.unlink(output_path)
    assert result.exit_code == 0
