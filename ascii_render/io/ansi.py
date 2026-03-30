import numpy as np
from ..types import ColorMode, RenderResult


class ANSIFormatter:
    ESCAPE = "\033"
    RESET = f"{ESCAPE}[0m"

    def __init__(
        self, mode: ColorMode = ColorMode.TRUECOLOR, char_set: str = " .:-=+*#%@"
    ):
        self.mode = mode
        self.char_set = char_set
        self._chars = list(char_set)
        self._num_chars = len(char_set)

    def format(self, result: RenderResult) -> str:
        char_indices = result.char_indices
        colors = result.colors
        width, height = result.dimensions

        lines = []
        escape = self.ESCAPE
        reset = self.RESET

        if self.mode == ColorMode.TRUECOLOR:
            for y in range(height):
                row_chars = []
                for x in range(width):
                    r, g, b = colors[y, x]
                    c = self._chars[char_indices[y, x]]
                    row_chars.append(f"{escape}[38;2;{r};{g};{b}m{c}")
                lines.append("".join(row_chars) + reset)
        elif self.mode == ColorMode.MODE_256:
            gray_weights = np.array([30, 59, 11])
            gray = np.dot(colors[:, :, :3], gray_weights) // 100
            gray = np.minimum(232 + gray, 255).astype(np.int32)
            for y in range(height):
                row_chars = []
                for x in range(width):
                    c = self._chars[char_indices[y, x]]
                    g = gray[y, x]
                    row_chars.append(f"{escape}[38;5;{g}m{c}")
                lines.append("".join(row_chars) + reset)
        else:
            r = colors[:, :, 0]
            g = colors[:, :, 1]
            b = colors[:, :, 2]
            color_idx = 30 + np.where(
                r > 128, 1, np.where(g > 128, 4, np.where(b > 128, 2, 0))
            )
            for y in range(height):
                row_chars = []
                for x in range(width):
                    c = self._chars[char_indices[y, x]]
                    ci = color_idx[y, x]
                    row_chars.append(f"{escape}[{ci}m{c}")
                lines.append("".join(row_chars) + reset)

        return "\n".join(lines)
