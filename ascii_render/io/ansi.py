from ..types import ColorMode, RenderResult


class ANSIFormatter:
    ESCAPE = "\033"
    RESET = f"{ESCAPE}[0m"
    BOLD = f"{ESCAPE}[1m"

    def __init__(
        self,
        mode: ColorMode = ColorMode.TRUECOLOR,
        char_set: str = " .:-=+*#%@",
        highlight: bool = False,
    ):
        self.mode = mode
        self.char_set = char_set
        self.highlight = highlight
        self._chars = list(char_set)
        self._num_chars = len(char_set)

    def format(self, result: RenderResult) -> str:
        char_indices = result.char_indices
        colors = result.colors
        width, height = result.dimensions

        lines = []
        escape = self.ESCAPE
        reset = self.RESET
        prefix = self.BOLD if self.highlight else ""

        if self.mode == ColorMode.TRUECOLOR:
            for y in range(height):
                row_chars = []
                for x in range(width):
                    r, g, b = colors[y][x]
                    c = self._chars[char_indices[y][x]]
                    row_chars.append(f"{escape}[38;2;{r};{g};{b}m{prefix}{c}")
                lines.append("".join(row_chars) + reset)
        elif self.mode == ColorMode.MODE_256:
            for y in range(height):
                row_chars = []
                for x in range(width):
                    r, g, b = colors[y][x]
                    gray = (30 * r + 59 * g + 11 * b) // 100
                    code = min(232 + gray, 255)
                    c = self._chars[char_indices[y][x]]
                    row_chars.append(f"{escape}[38;5;{code}m{prefix}{c}")
                lines.append("".join(row_chars) + reset)
        else:
            for y in range(height):
                row_chars = []
                for x in range(width):
                    r, g, b = colors[y][x]
                    if r > 128:
                        ci = 31
                    elif g > 128:
                        ci = 34
                    elif b > 128:
                        ci = 32
                    else:
                        ci = 30
                    c = self._chars[char_indices[y][x]]
                    row_chars.append(f"{escape}[{ci}m{prefix}{c}")
                lines.append("".join(row_chars) + reset)

        return "\n".join(lines)
