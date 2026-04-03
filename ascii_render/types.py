from dataclasses import dataclass
from typing import Optional
from enum import Enum


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
    char_indices: list[list[int]]
    colors: list[list[tuple[int, int, int]]]
    dimensions: tuple[int, int]
