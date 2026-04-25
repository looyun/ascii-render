"""Core ASCII renderer."""

from PIL import Image
from typing import List, Optional

from .effects import Effect
from .pixel_mapper import map_pixels_to_ascii
from .image_utils import preprocess_image
from ..types import RenderConfig, RenderResult
from ..io.loader import load_image


class Renderer:
    def __init__(self, config: Optional[RenderConfig] = None):
        self.config = config or RenderConfig()
        self._effects: List[Effect] = []

    def add_effect(self, effect: Effect) -> "Renderer":
        self._effects.append(effect)
        return self

    def render(self, image_path: str) -> RenderResult:
        """Render an image to a RenderResult.

        Args:
            image_path: Path to the image file.

        Returns:
            RenderResult containing char indices, colors, and dimensions.
        """
        image = load_image(image_path)
        return self.process(image)

    def process(self, image: Image.Image) -> RenderResult:
        """Process a PIL Image and return a RenderResult.

        Args:
            image: Input PIL Image.

        Returns:
            RenderResult containing char indices, colors, and dimensions.
        """
        image = self.prepare(image)
        return self._render_to_ascii(image)

    def prepare(self, image: Image.Image) -> Image.Image:
        """Preprocess and apply effects to a PIL Image.

        Args:
            image: Input PIL Image.

        Returns:
            Processed PIL Image ready for ASCII mapping.
        """
        image = self._preprocess(image)
        for effect in self._effects:
            image = effect.apply(image)
        return image

    def _preprocess(self, image: Image.Image) -> Image.Image:
        return preprocess_image(
            image,
            self.config.width or 0,
            self.config.height or 0,
            self.config.preserve_aspect,
        )

    def _render_to_ascii(self, image: Image.Image) -> RenderResult:
        return map_pixels_to_ascii(
            image,
            self.config.char_set,
            self.config.invert,
        )
