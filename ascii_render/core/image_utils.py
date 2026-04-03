"""Image preprocessing utilities.

Handles resizing (with optional aspect ratio correction) and
RGBA to RGB conversion.
"""

from PIL import Image


def preprocess_image(
    image: Image.Image,
    width: int,
    height: int,
    preserve_aspect: bool = True,
) -> Image.Image:
    """Resize and convert image to RGB.

    Args:
        image: Input PIL Image.
        width: Target width in pixels.
        height: Target height in pixels.
        preserve_aspect: If True, maintain aspect ratio with char correction.

    Returns:
        Resized RGB PIL Image.
    """
    if width or height:
        target_width = width or 80
        target_height = height or 24

        if preserve_aspect:
            orig_w, orig_h = image.size
            aspect = orig_w / orig_h
            char_aspect = 0.5

            height_from_width = int(target_width * char_aspect / aspect)
            width_from_height = int(target_height * aspect / char_aspect)

            if height_from_width <= target_height:
                target_height = height_from_width
            else:
                target_width = width_from_height

        image = image.resize((target_width, target_height))

    if image.mode == "RGBA":
        background = Image.new("RGB", image.size, (0, 0, 0))
        background.paste(image, mask=image.split()[3])
        return background
    return image.convert("RGB")
