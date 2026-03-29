import numpy as np
from PIL import Image, ImageFilter
from ..core.effects import Effect


class GlowEffect(Effect):
    def __init__(self, radius: int = 3, intensity: float = 0.5, threshold: float = 0.3):
        self.radius = radius
        self.intensity = intensity
        self.threshold = threshold

    def apply(self, image: Image.Image) -> Image.Image:
        img_array = np.array(image).astype(np.float32) / 255.0
        brightness = np.mean(img_array, axis=2)

        mask = brightness > self.threshold

        blurred = image.filter(ImageFilter.GaussianBlur(radius=self.radius))
        blur_array = np.array(blurred).astype(np.float32) / 255.0

        result = img_array.copy()
        for c in range(3):
            result[:, :, c] = np.where(
                mask,
                img_array[:, :, c]
                + (blur_array[:, :, c] - img_array[:, :, c]) * self.intensity,
                img_array[:, :, c],
            )

        result = np.clip(result * 255, 0, 255).astype(np.uint8)
        return Image.fromarray(result)
