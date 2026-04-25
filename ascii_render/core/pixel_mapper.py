"""Pixel-to-ASCII mapping utilities.

Converts PIL Images to RenderResult objects by mapping pixel brightness
to character indices and extracting RGB color data.
"""

import numpy as np
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
        RenderResult with char indices, colors, and dimensions.
    """
    width, height = image.size
    arr = np.array(image)
    gray = np.array(image.convert("L"))

    num_chars = len(char_set)
    scale = num_chars / 255.0
    max_idx = num_chars - 1

    if invert:
        char_indices_arr = ((255.0 - gray) * scale).astype(np.int32)
    else:
        char_indices_arr = (gray.astype(np.float32) * scale).astype(np.int32)

    np.clip(char_indices_arr, 0, max_idx, out=char_indices_arr)

    char_indices = char_indices_arr.tolist()
    colors = [
        [tuple(int(v) for v in pixel) for pixel in row]
        for row in arr
    ]

    return RenderResult(
        char_indices=char_indices,
        colors=colors,
        dimensions=(width, height),
    )
