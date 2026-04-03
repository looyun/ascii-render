"""Pixel-to-ASCII mapping utilities.

Converts PIL Images to RenderResult objects by mapping pixel brightness
to character indices and extracting RGB color data.
"""

from PIL import Image

from ..types import RenderResult


def map_pixels_to_ascii(
    image: Image.Image,
    char_set: str,
    invert: bool = False,
) -> RenderResult:
    """Convert a PIL Image to RenderResult.

    Args:
        image: RGB PIL Image (must be preprocessed).
        char_set: String of ASCII characters ordered by brightness.
        invert: If True, invert brightness mapping.

    Returns:
        RenderResult with char_indices, colors, and dimensions.
    """
    width, height = image.size
    gray = image.convert("L")
    gray_pixels = list(gray.get_flattened_data())
    rgb_pixels = list(image.get_flattened_data())

    num_chars = len(char_set)
    scale = num_chars / 255.0

    char_indices: list[list[int]] = []
    colors: list[list[tuple[int, int, int]]] = []

    for y in range(height):
        char_row: list[int] = []
        color_row: list[tuple[int, int, int]] = []
        for x in range(width):
            offset = y * width + x
            brightness = gray_pixels[offset]
            if invert:
                brightness = 255 - brightness
            idx = int(brightness * scale)
            if idx < 0:
                idx = 0
            elif idx >= num_chars:
                idx = num_chars - 1
            char_row.append(idx)

            r, g, b = rgb_pixels[offset]
            color_row.append((r, g, b))

        char_indices.append(char_row)
        colors.append(color_row)

    return RenderResult(
        char_indices=char_indices,
        colors=colors,
        dimensions=(width, height),
    )
