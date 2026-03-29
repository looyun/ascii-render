from abc import ABC, abstractmethod
from PIL import Image


class Effect(ABC):
    @abstractmethod
    def apply(self, image: Image.Image) -> Image.Image:
        """Apply the effect to the image and return the modified image."""
        pass
