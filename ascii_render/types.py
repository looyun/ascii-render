from dataclasses import dataclass, field
from typing import List, Optional, Protocol
from enum import Enum
from PIL import Image


class ColorMode(Enum):
    MODE_8 = 8
    MODE_256 = 256
    TRUECOLOR = "truecolor"


@dataclass
class RenderConfig:
    width: int = 80
    height: Optional[int] = None
    char_set: str = " .:-=+*#%@"
    invert: bool = False
    color_mode: ColorMode = ColorMode.TRUECOLOR
    preserve_aspect: bool = True


@dataclass
class RenderResult:
    frame_data: List[List[str]]
    dimensions: tuple[int, int]
    colors: List[List[tuple[int, int, int]]] | None = None


class Effect(Protocol):
    def apply(self, image: Image.Image) -> Image.Image:
        """Apply effect to image and return modified image."""
        ...
