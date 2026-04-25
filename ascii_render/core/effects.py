from typing import Protocol
from PIL import Image


class Effect(Protocol):
    def apply(self, image: Image.Image) -> Image.Image:
        """Apply the effect to the image and return the modified image."""
        ...
