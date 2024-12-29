# Copyright 2024 Science project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True)
class Colors:
    use_color: bool

    def red(self, text) -> str:
        return self.color(text, fg="red")

    def yellow(self, text) -> str:
        return self.color(text, fg="yellow")

    def color(self, text, fg: str):
        if not self.use_color:
            return text

        import colors

        return colors.color(text, fg=fg)


@contextmanager
def color_support(use_color: bool | None = None) -> Iterator[Colors]:
    if use_color in (True, None):
        try:
            import colorama
        except ImportError:
            pass
        else:
            colorama.just_fix_windows_console()

    if use_color is None:

        def _use_color() -> bool:
            # Used in Python 3.13+
            python_colors = os.environ.get("PYTHON_COLORS")
            if python_colors in ("0", "1"):
                return python_colors == "1"

            # A common convention; see: https://no-color.org/
            if "NO_COLOR" in os.environ:
                return False

            # A less common convention; see: https://force-color.org/
            if "FORCE_COLOR" in os.environ:
                return True

            return sys.stderr.isatty() and "dumb" != os.environ.get("TERM")

        use_color = _use_color()

    yield Colors(use_color=use_color)
