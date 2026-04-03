"""Interactive mouse-driven canvas with animated content area."""

import os
import select
import sys
import termios
import tty
import time
import re
from typing import Optional, Callable

_ESC = "\033"
_SGR_MOUSE = re.compile(r"<(\d+);(\d+);(\d+)([Mm])")


class _MouseTracker:
    """Low-level mouse event reader for terminals."""

    def __init__(self):
        self._old_attrs: Optional[list] = None

    def start(self):
        fd = sys.stdin.fileno()
        self._old_attrs = termios.tcgetattr(fd)
        tty.setraw(fd)
        sys.stdout.write(f"{_ESC}[?1006h{_ESC}[?1000h{_ESC}[?25l")
        sys.stdout.flush()

    def stop(self):
        sys.stdout.write(f"{_ESC}[?1006l{_ESC}[?1000l{_ESC}[?25h")
        sys.stdout.flush()
        if self._old_attrs is not None:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self._old_attrs)
        sys.stdout.write("\n")
        sys.stdout.flush()

    def poll(self, timeout: float = 0.02) -> Optional[tuple[int, int]]:
        """Drain all pending input, return latest left-click (col, row) 1-based."""
        if not select.select([sys.stdin], [], [], timeout)[0]:
            return None

        buf = ""
        deadline = time.monotonic() + 0.05
        while time.monotonic() < deadline:
            if select.select([sys.stdin], [], [], 0.002)[0]:
                buf += sys.stdin.read(1)
            else:
                break

        click: Optional[tuple[int, int]] = None
        for m in _SGR_MOUSE.finditer(buf):
            button = int(m.group(1))
            col = int(m.group(2))
            row = int(m.group(3))
            event_type = m.group(4)
            if button == 0 and event_type == "M":
                click = (col, row)

        clean = _SGR_MOUSE.sub("", buf)
        if "q" in clean:
            raise KeyboardInterrupt("quit")

        return click


class MouseCanvas:
    """An animated content area that follows mouse clicks.

    The canvas occupies a fixed-size region of the terminal. When the user
    clicks anywhere on the screen, an indicator appears at the click position
    and the canvas smoothly moves toward it. On arrival the indicator fades.

    Usage::

        canvas = MouseCanvas(size=10)
        canvas.start()
        while True:
            canvas.render()
            canvas.update()
            if canvas.clicked:
                # handle click
            time.sleep(1/30)
        canvas.stop()

    Args:
        size: Short-side dimension of the canvas (rows). The canvas is
              ``size x (size*2)`` cells to roughly match character aspect ratio.
    """

    def __init__(self, size: int = 10, term_size: Optional[tuple[int, int]] = None):
        self.size = size
        self.cols = size * 2
        self.rows = size

        tw, th = term_size or os.get_terminal_size()
        self.x = float(tw // 2)
        self.y = float(th // 2)
        self.target_x = self.x
        self.target_y = self.y
        self._prev_target_x = int(self.x)
        self._prev_target_y = int(self.y)
        self._prev_box_x = 0
        self._prev_box_y = 0
        self._first_render = True
        self._arrived = True
        self._term_w = tw
        self._term_h = th

        self._mouse = _MouseTracker()
        self._click_handler: Optional[Callable[[int, int], None]] = None
        self._pending_click: Optional[tuple[int, int]] = None
        self._last_update_time = time.monotonic()
        self._move_speed = 45.0  # cells per second

    # -- public API --

    def start(self):
        """Enter raw terminal mode and enable mouse tracking."""
        self._mouse.start()

    def stop(self):
        """Restore terminal to normal mode."""
        self._mouse.stop()

    def on_click(self, handler: Callable[[int, int], None]) -> "MouseCanvas":
        """Register a callback invoked after each click.

        The callback receives ``(col, row)`` in 1-based terminal coordinates.
        """
        self._click_handler = handler
        return self

    @property
    def clicked(self) -> Optional[tuple[int, int]]:
        """The most recent click position, or None. Consumed on read."""
        result = self._pending_click
        self._pending_click = None
        return result

    def set_target(self, col: int, row: int):
        """Programmatically set the movement target."""
        self._prev_target_x = int(self.target_x)
        self._prev_target_y = int(self.target_y)
        self.target_x = float(col)
        self.target_y = float(row)
        self._arrived = False

    def update(self):
        """Advance animation state and poll mouse input."""
        try:
            w, h = os.get_terminal_size()
        except OSError:
            w, h = self._term_w, self._term_h
        self._term_w, self._term_h = w, h

        try:
            event = self._mouse.poll(timeout=0.02)
        except (OSError, ValueError):
            event = None

        if event is not None:
            col, row = event
            self._prev_target_x = int(self.target_x)
            self._prev_target_y = int(self.target_y)
            self.target_x = float(col)
            self.target_y = float(row)
            self._arrived = False
            self._pending_click = (col, row)
            if self._click_handler is not None:
                self._click_handler(col, row)

        # Time-based smooth movement
        now = time.monotonic()
        dt = now - self._last_update_time
        self._last_update_time = now

        if dt > 0 and not self._arrived:
            # Move toward target at constant speed (cells/sec)
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            dist = (dx * dx + dy * dy) ** 0.5
            if dist > 0.5:
                step = self._move_speed * dt
                # Clamp step so we don't overshoot
                step = min(step, dist - 0.5)
                self.x += dx / dist * step
                self.y += dy / dist * step
            else:
                self.x = self.target_x
                self.y = self.target_y
                self._arrived = True

        self._last_update_time = time.monotonic()

    @property
    def time_since_update(self) -> float:
        """Seconds since last update() call."""
        return time.monotonic() - self._last_update_time

    def render(self):
        """Render one frame of the canvas."""
        w, h = os.get_terminal_size()

        # Detect terminal resize
        if w != self._term_w or h != self._term_h:
            self._first_render = True
            self._term_w = w
            self._term_h = h
            self.x = float(w // 2)
            self.y = float(h // 2)
            self.target_x = self.x
            self.target_y = self.y
            self._prev_target_x = int(self.x)
            self._prev_target_y = int(self.y)
            self._prev_box_x = 0
            self._prev_box_y = 0

        bx = max(1, min(int(self.x) - self.cols // 2, w - self.cols))
        by = max(3, min(int(self.y) - self.rows // 2, h - self.rows - 1))

        out: list[str] = []

        if self._first_render:
            out.append(f"{_ESC}[2J{_ESC}[H")
            out.append(f"{_ESC}[1;1H{_ESC}[1;36m")
            out.append("Click ANYWHERE to move the canvas. Press 'q' to quit.")
            out.append(f"{_ESC}[0m")
            self._first_render = False
        else:
            # Clear old target marker
            out.append(f"{_ESC}[{self._prev_target_y};{self._prev_target_x}H ")
            # Clear old box area (only non-overlapping rows)
            if (bx, by) != (self._prev_box_x, self._prev_box_y):
                for r in range(self._prev_box_y, self._prev_box_y + self.rows):
                    if r < by or r >= by + self.rows:
                        # Row doesn't overlap vertically, clear entire row
                        out.append(f"{_ESC}[{r};{self._prev_box_x}H{' ' * self.cols}")
                    elif self._prev_box_x != bx:
                        # Same row but different column, clear old columns
                        old_end = self._prev_box_x + self.cols
                        new_end = bx + self.cols
                        if self._prev_box_x < bx:
                            # Old is to the left, clear left portion
                            width = bx - self._prev_box_x
                            out.append(f"{_ESC}[{r};{self._prev_box_x}H{' ' * width}")
                        if old_end > new_end:
                            # Old extends to the right, clear right portion
                            width = old_end - new_end
                            out.append(f"{_ESC}[{r};{new_end}H{' ' * width}")

        # Draw new content at new position
        content = self._draw_content_str(bx, by)
        out.append(content)

        # Show target crosshair only while moving
        if not self._arrived:
            out.append(f"{_ESC}[{int(self.target_y)};{int(self.target_x)}H")
            out.append(f"{_ESC}[1;31m×{_ESC}[0m")

        # Single flush — no intermediate visible state
        sys.stdout.write("".join(out))
        sys.stdout.flush()

        self._prev_box_x = bx
        self._prev_box_y = by

    def _draw_content_str(self, x: int, y: int) -> str:
        """Return a string that draws the content at (x, y).

        Subclasses should override this instead of ``_draw_content``.
        The default implementation delegates to ``_draw_content`` for
        backward compatibility.
        """
        import io

        old = sys.stdout
        buf = io.StringIO()
        sys.stdout = buf
        try:
            self._draw_content(x, y)
            return buf.getvalue()
        finally:
            sys.stdout = old

    # -- override point --

    def _draw_content(self, x: int, y: int):
        """Draw the canvas content at terminal position (x, y).

        Subclasses should override this method to render custom content.
        The default draws a simple bordered box with coordinates.
        """
        border_top = "┌" + "─" * (self.cols - 2) + "┐"
        border_bot = "└" + "─" * (self.cols - 2) + "┘"

        sys.stdout.write(f"{_ESC}[{y};{x}H")
        sys.stdout.write(f"{_ESC}[1;33m{border_top}{_ESC}[0m")

        for r in range(1, self.rows - 1):
            mid = ""
            if r == self.rows // 2:
                mid = f"  ({int(self.x):3d}, {int(self.y):3d})  "
            sys.stdout.write(f"{_ESC}[{y + r};{x}H")
            sys.stdout.write(f"{_ESC}[1;33m│{_ESC}[0m")
            if mid:
                sys.stdout.write(f"{_ESC}[{y + r};{x + 2}H{mid}")
            sys.stdout.write(f"{_ESC}[{y + r};{x + self.cols - 1}H")
            sys.stdout.write(f"{_ESC}[1;33m│{_ESC}[0m")

        sys.stdout.write(f"{_ESC}[{y + self.rows - 1};{x}H")
        sys.stdout.write(f"{_ESC}[1;33m{border_bot}{_ESC}[0m")
