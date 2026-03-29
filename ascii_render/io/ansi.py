from PIL import Image
from ..types import ColorMode, RenderResult


class ANSIFormatter:
    ESCAPE = "\033"
    RESET = f"{ESCAPE}[0m"
    BOLD = f"{ESCAPE}[1m"

    def __init__(self, mode: ColorMode = ColorMode.TRUECOLOR):
        self.mode = mode

    def _truecolor(self, r: int, g: int, b: int) -> str:
        return f"{self.ESCAPE}[38;2;{r};{g};{b}m"

    def _color_256(self, r: int, g: int, b: int) -> str:
        gray = (r * 30 + g * 59 + b * 11) // 100
        return f"{self.ESCAPE}[38;5;{min(232 + gray, 255)}m"

    def _color_8(self, r: int, g: int, b: int) -> str:
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        brightness = (max_c + min_c) // 2
        color_idx = 30 + (1 if r > 128 else 4 if g > 128 else 2 if b > 128 else 0)
        return f"{self.ESCAPE}[{color_idx}m"

    def format(self, result: RenderResult, image: Image.Image) -> str:
        if self.mode == ColorMode.TRUECOLOR:
            color_fn = self._truecolor
        elif self.mode == ColorMode.MODE_256:
            color_fn = self._color_256
        else:
            color_fn = self._color_8

        lines = []
        for y, row in enumerate(result.frame_data):
            line_chars = []
            for x, char in enumerate(row):
                if result.colors and x < len(result.colors[y]):
                    r, g, b = result.colors[y][x]
                    line_chars.append(f"{color_fn(r, g, b)}{char}")
                else:
                    line_chars.append(char)
            lines.append("".join(line_chars) + self.RESET)

        return "\n".join(lines)
