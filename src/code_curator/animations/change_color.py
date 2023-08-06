from __future__ import annotations

from typing import TYPE_CHECKING

from colour import Color
from manim import Animation
from manim import interpolate_color
from manim import smooth


if TYPE_CHECKING:
    from manim import Mobject


class ChangeColor(Animation):
    def __init__(self, mobject: Mobject, color: str | Color) -> None:
        super().__init__(mobject, run_time=1)
        self.initial_color = mobject.color
        self.target_color = color

    def interpolate(self, alpha: float) -> None:
        curr_color = interpolate_color(self.initial_color, self.target_color, smooth(alpha))
        self.mobject.set_color(curr_color)
