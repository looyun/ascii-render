from PIL import Image, ImageFilter, ImageChops
from ..core.effects import Effect


class GlowEffect(Effect):
    def __init__(self, radius: int = 3, intensity: float = 0.5, threshold: float = 0.5):
        self.radius = radius
        self.intensity = intensity
        self.threshold = threshold

    def apply(self, image: Image.Image) -> Image.Image:
        gray = image.convert("L")
        mask = gray.point(lambda p: 255 if p / 255.0 > self.threshold else 0)

        blurred = image.filter(ImageFilter.GaussianBlur(radius=self.radius))

        glow = Image.blend(image, blurred, self.intensity)

        return Image.composite(glow, image, mask.convert("1"))
