"""Core ASCII renderer."""

from PIL import Image
from typing import List, Optional

from .effects import Effect
from .pixel_mapper import map_pixels_to_ascii
from .image_utils import preprocess_image
from ..types import RenderConfig
from ..io.loader import load_image
from ..io.ansi import ANSIFormatter


class Renderer:
    def __init__(self, config: Optional[RenderConfig] = None):
        self.config = config or RenderConfig()
        self._effects: List[Effect] = []

    def add_effect(self, effect: Effect) -> "Renderer":
        self._effects.append(effect)
        return self

    def render(self, image_path: str) -> str:
        image = load_image(image_path)
        image = self._preprocess(image)

        for effect in self._effects:
            image = effect.apply(image)

        result = self._render_to_ascii(image)
        formatter = ANSIFormatter(self.config.color_mode, self.config.char_set)
        return formatter.format(result)

    def _preprocess(self, image: Image.Image) -> Image.Image:
        return preprocess_image(
            image,
            self.config.width or 0,
            self.config.height or 0,
            self.config.preserve_aspect,
        )

    def _render_to_ascii(self, image: Image.Image):
        return map_pixels_to_ascii(
            image,
            self.config.char_set,
            self.config.invert,
        )
