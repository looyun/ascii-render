from PIL import Image
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
        formatter = ANSIFormatter(self.config.color_mode, self.config.char_set)
        return formatter.format(result)

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

        if image.mode == "RGBA":
            background = Image.new("RGB", image.size, (0, 0, 0))
            background.paste(image, mask=image.split()[3])
            return background
        return image.convert("RGB")

    def _render_to_ascii(self, image: Image.Image) -> RenderResult:
        width, height = image.size
        gray = image.convert("L")
        gray_pixels = list(gray.get_flattened_data())

        num_chars = len(self.config.char_set)
        scale = num_chars / 255.0

        if self.config.invert:
            char_indices = []
            for y in range(height):
                row = []
                for x in range(width):
                    brightness = 1.0 - gray_pixels[y * width + x] / 255.0
                    idx = int(brightness * num_chars)
                    idx = max(0, min(idx, num_chars - 1))
                    row.append(idx)
                char_indices.append(row)
        else:
            char_indices = []
            for y in range(height):
                row = []
                for x in range(width):
                    brightness = gray_pixels[y * width + x] * scale
                    idx = int(brightness)
                    idx = max(0, min(idx, num_chars - 1))
                    row.append(idx)
                char_indices.append(row)

        colors = []
        rgb_pixels = list(image.get_flattened_data())
        for y in range(height):
            row = []
            for x in range(width):
                r, g, b = rgb_pixels[y * width + x]
                row.append((r, g, b))
            colors.append(row)

        return RenderResult(
            char_indices=char_indices, colors=colors, dimensions=(width, height)
        )
