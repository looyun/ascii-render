from dataclasses import dataclass
from typing import Optional
from enum import Enum


class ColorMode(Enum):
    MODE_8 = 8
    MODE_256 = 256
    TRUECOLOR = "truecolor"

    @classmethod
    def from_string(cls, value: str) -> "ColorMode":
        """Parse a ColorMode from a string (e.g., '8', '256', 'truecolor')."""
        mapping = {
            "8": cls.MODE_8,
            "256": cls.MODE_256,
            "truecolor": cls.TRUECOLOR,
        }
        try:
            return mapping[value.lower()]
        except KeyError as exc:
            raise ValueError(f"Invalid color mode: {value}") from exc


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
