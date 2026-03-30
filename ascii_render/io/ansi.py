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
        frame_data = result.frame_data
        colors = result.colors

        for y in range(len(frame_data)):
            row = frame_data[y]
            row_colors = colors[y] if colors else None
            line_parts = []

            for x in range(len(row)):
                char = row[x]
                if row_colors and x < len(row_colors):
                    r, g, b = row_colors[x]
                    line_parts.append(color_fn(r, g, b))
                    line_parts.append(char)
                else:
                    line_parts.append(char)

            line_parts.append(self.RESET)
            lines.append("".join(line_parts))

        return "\n".join(lines)
