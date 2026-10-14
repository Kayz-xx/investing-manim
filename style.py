"""Shared look for every scene: palette, Roboto text, axes and data loading."""

import json
from pathlib import Path

import manimpango
from manim import *

ROOT = Path(__file__).parent

for ttf in sorted((ROOT / "fonts").glob("*.ttf")):
    manimpango.register_font(str(ttf))

FONT = "Roboto"

# Blue vs. orange carries every two-way comparison (it stays distinct for colorblind
# viewers, unlike red vs. green). Gold is reserved for the one number that matters.
BG = "#111318"
INK = "#ECEDEE"
MUTED = "#8B9099"
FAINT = "#3A3F48"
BLUE = "#58C4DD"
DEEP_BLUE = "#3E7FD9"
ORANGE = "#F08A3C"
GOLD = "#F4D345"

config.background_color = BG


def T(text, size=26, color=INK, weight=NORMAL, **kwargs):
    return Text(text, font=FONT, font_size=size, color=color, weight=weight, **kwargs)


def money(x, decimals=0):
    return f"${x:,.{decimals}f}"


def load_data():
    with open(ROOT / "data" / "derived.json") as f:
        return json.load(f)


def axes(x_range, y_range, x_length=10, y_length=5, **kwargs):
    return Axes(
        x_range=x_range,
        y_range=y_range,
        x_length=x_length,
        y_length=y_length,
        tips=False,
        axis_config={"color": FAINT, "stroke_width": 2, "include_ticks": False},
        **kwargs,
    )


def x_labels(ax, values, fmt=str, size=20):
    y0 = ax.y_range[0]
    return VGroup(*[T(fmt(v), size, MUTED).next_to(ax.c2p(v, y0), DOWN, buff=0.2) for v in values])


def y_labels(ax, values, fmt=str, size=20, grid=True):
    """Labels on the left plus faint horizontal gridlines."""
    x0, x1 = ax.x_range[0], ax.x_range[1]
    group = VGroup()
    for v in values:
        group.add(T(fmt(v), size, MUTED).next_to(ax.c2p(x0, v), LEFT, buff=0.2))
        if grid:
            group.add(Line(ax.c2p(x0, v), ax.c2p(x1, v), color=FAINT, stroke_width=1, stroke_opacity=0.6))
    return group


def source(text):
    return T(text, 15, MUTED).to_corner(DR, buff=0.25)


def caption(text, size=32, color=INK, **kwargs):
    return T(text, size, color, **kwargs).to_edge(DOWN, buff=0.45)


def end_label(ax, x, y, text, color, size=24, direction=RIGHT):
    return T(text, size, color, weight=MEDIUM).next_to(ax.c2p(x, y), direction, buff=0.15)


def series_path(ax, xs, ys, color, width=4):
    path = VMobject(stroke_color=color, stroke_width=width)
    path.set_points_as_corners([ax.c2p(x, y) for x, y in zip(xs, ys)])
    return path


class Clip(Scene):
    """A clip the speaker talks over: it ends on a held frame, then clears."""

    HOLD = 2.5

    def hold(self, seconds=None):
        self.wait(self.HOLD if seconds is None else seconds)

    def clear(self, run_time=0.8):
        if self.mobjects:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=run_time)
