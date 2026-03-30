from PIL import Image
import numpy as np
from typing import List, Optional

from ..types import RenderConfig, RenderResult, Effect


class Renderer:
    def __init__(self, config: Optional[RenderConfig] = None):
        self.config = config or RenderConfig()
        self._effects: List[Effect] = []

    def add_effect(self, effect: Effect) -> "Renderer":
        self._effects.append(effect)
        return self

    def render(self, image_path: str) -> str:
        from ..io.loader import load_image
        from ..io.ansi import ANSIFormatter

        image = load_image(image_path)
        image = self._preprocess(image)

        for effect in self._effects:
            image = effect.apply(image)

        result = self._render_to_ascii(image)
        formatter = ANSIFormatter(self.config.color_mode)
        return formatter.format(result, image)

    def _preprocess(self, image: Image.Image) -> Image.Image:
        if self.config.width or self.config.height:
            target_width = self.config.width or 80
            target_height = self.config.height or 24

            if self.config.preserve_aspect:
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

        return image.convert("RGB")

    def _render_to_ascii(self, image: Image.Image) -> RenderResult:
        img_array = np.array(image)
        height, width = img_array.shape[:2]

        brightness = np.mean(img_array, axis=2) / 255.0

        if self.config.invert:
            brightness = 1.0 - brightness

        chars = self.config.char_set
        num_chars = len(chars)

        frame_data = []
        colors = []

        for y in range(height):
            row_chars = []
            row_colors = []
            for x in range(width):
                bright = brightness[y, x]
                char_idx = min(int(bright * num_chars), num_chars - 1)
                char_idx = max(0, char_idx)
                row_chars.append(chars[char_idx])
                row_colors.append(tuple(img_array[y, x]))
            frame_data.append(row_chars)
            colors.append(row_colors)

        return RenderResult(
            frame_data=frame_data, dimensions=(width, height), colors=colors
        )
