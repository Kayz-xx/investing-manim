"""
Visual aids for a talk on investing early, for college students.

Each scene is a standalone clip meant to sit behind a speaker: the visuals carry the
idea, and text appears only for labels and the one number worth remembering.

    manim -pql investing.py Compounding      # preview one clip
    ./render_all.sh                          # render every clip + the combined video

Market data comes from data/derived.json (built by data/prepare.py from real S&P 500
history). Projections assume 7% a year and are labelled as such.
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from style import *  # noqa: E402,F403

DATA = load_data()
RATE = 0.07
MONTHLY = (1 + RATE) ** (1 / 12) - 1


def balance(monthly, months_paying, months_total, rate=MONTHLY):
    b = 0.0
    for m in range(months_total):
        if m < months_paying:
            b += monthly
        b *= 1 + rate
    return b


def partial(path, alpha):
    """Copy of `path` drawn from its start up to fraction `alpha`."""
    piece = path.copy()
    piece.pointwise_become_partial(path, 0, min(max(alpha, 1e-4), 1))
    return piece


def year_of(date):
    """'2008-10-13' or '2008-10' -> decimal year."""
    parts = [int(p) for p in date.split("-")]
    month = parts[1] if len(parts) > 1 else 1
    day = parts[2] if len(parts) > 2 else 15
    return parts[0] + (month - 1) / 12 + (day - 1) / 365


def segments(points, color, width=1.5, opacity=1.0):
    """Many disjoint line segments as one mobject (fast to render)."""
    mob = VMobject(stroke_color=color, stroke_width=width, stroke_opacity=opacity)
    for a, b in points:
        mob.start_new_path(a)
        mob.add_line_to(b)
    return mob


def squarify(values, x, y, w, h):
    """Squarified treemap: rectangles (x, y, w, h) for values summing to w*h."""
    rects, vals = [], list(values)
    while vals:
        short = min(w, h)

        def worst(row):
            s = sum(row)
            return max(max(short**2 * r / s**2, s**2 / (short**2 * r)) for r in row)

        row = [vals.pop(0)]
        while vals and worst(row + [vals[0]]) <= worst(row):
            row.append(vals.pop(0))
        s = sum(row)
        if w >= h:
            cw, cy = s / h, y
            for r in row:
                rects.append((x, cy, cw, r / cw))
                cy += r / cw
            x, w = x + cw, w - cw
        else:
            rh, cx = s / w, x
            for r in row:
                rects.append((cx, y, r / rh, rh))
                cx += r / rh
            y, h = y + rh, h - rh
    return rects


# ---------------------------------------------------------------------------
# What investing is
# ---------------------------------------------------------------------------
class Ownership(Clip):
    """A share is a slice of a business; the slice grows with the business."""

    def construct(self):
        cells = VGroup(
            *[Square(0.32, stroke_width=0, fill_color=DEEP_BLUE, fill_opacity=0.6) for _ in range(100)]
        ).arrange_in_grid(10, 10, buff=0.06)
        cells.move_to(RIGHT * 2.6 + DOWN * 0.2)
        worth = T("A company worth $10,000", 28).next_to(cells, UP, buff=0.4)
        split = T("split into 100 shares", 22, MUTED).next_to(cells, DOWN, buff=0.3)
        self.play(LaggedStart(*[FadeIn(c, scale=0.5) for c in cells], lag_ratio=0.01), FadeIn(worth), run_time=1.6)
        self.play(FadeIn(split))
        self.hold(1.5)

        share = cells[0]
        ghost = DashedVMobject(Square(0.32, stroke_color=MUTED, stroke_width=1.5), num_dashes=12).move_to(share)
        self.add(ghost)
        self.play(share.animate.set_fill(BLUE, 1).scale(2.4).move_to(LEFT * 3.8 + DOWN * 0.2), run_time=1.4)
        you = T("you buy 1 share", 24, MUTED).next_to(share, UP, buff=0.35)
        price = T("$100", 40, weight=MEDIUM).next_to(share, DOWN, buff=0.35)
        pct = T("= 1% of the company", 22, MUTED).next_to(price, DOWN, buff=0.15)
        self.play(FadeIn(you), FadeIn(price), FadeIn(pct))
        self.hold(2)

        # The business grows: every slice grows with it
        grown_worth = T("Now worth $16,000", 28).move_to(worth)
        grown_price = T("$160", 40, GOLD, weight=MEDIUM).move_to(price)
        self.play(
            cells[1:].animate.scale(1.26, about_point=cells.get_center()),
            share.animate.scale(1.26),
            FadeOut(ghost),
            Transform(worth, grown_worth.shift(UP * 0.35)),
            Transform(price, grown_price.shift(DOWN * 0.12)),
            pct.animate.shift(DOWN * 0.12),
            split.animate.shift(DOWN * 0.4),
            run_time=2,
        )
        self.hold(1.5)

        # Part of the profit is paid out to owners
        coins = VGroup(*[Dot(radius=0.09, color=GOLD) for _ in range(6)])
        for i, c in enumerate(coins):
            c.move_to(cells[1:].get_left() + UP * (0.8 - 0.3 * i))
        payout = T("+ a share of the profits (dividends)", 22, GOLD).next_to(pct, DOWN, buff=0.35)
        self.play(
            LaggedStart(*[c.animate(path_arc=-0.6).move_to(share.get_right() + LEFT * 0.1) for c in coins], lag_ratio=0.15),
            run_time=1.6,
        )
        self.play(FadeOut(coins), FadeIn(payout))
        self.hold(3)
        self.clear()


class CashVsInflation(Clip):
    """$1,000 kept as cash vs. invested, in today's dollars (real data)."""

    def construct(self):
        d = DATA["inflation"]
        xs = [year_of(m) for m in d["months"]]
        ax = axes([2006, 2023.6], [0, 3500], 9.8, 5).shift(DOWN * 0.35 + LEFT * 0.2)
        title = VGroup(
            T("$1,000 set aside in January 2006", 30),
            T("What it buys, in today's dollars", 22, MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_corner(UL, buff=0.55)
        self.play(FadeIn(title), Create(ax), FadeIn(x_labels(ax, [2006, 2010, 2014, 2018, 2022])),
                  FadeIn(y_labels(ax, [1000, 2000, 3000], lambda v: f"${v:,}")))
        start_line = DashedLine(ax.c2p(2006, 1000), ax.c2p(2023.6, 1000), color=MUTED, stroke_width=1.5)
        self.play(Create(start_line))

        cash = series_path(ax, xs, d["cash_real"], ORANGE)
        stocks = series_path(ax, xs, d["stocks_real"], BLUE)
        self.play(Create(cash), Create(stocks), run_time=6, rate_func=linear)
        x_end = xs[-1]
        c_end, s_end = d["cash_real"][-1], d["stocks_real"][-1]
        self.play(
            FadeIn(VGroup(Dot(ax.c2p(x_end, c_end), color=ORANGE), Dot(ax.c2p(x_end, s_end), color=BLUE))),
            FadeIn(VGroup(T("Kept as cash", 22, ORANGE), T(money(c_end), 30, weight=MEDIUM)).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
                   .next_to(ax.c2p(x_end, c_end), RIGHT, buff=0.2)),
            FadeIn(VGroup(T("In the S&P 500", 22, BLUE), T(money(s_end), 30, weight=MEDIUM)).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
                   .next_to(ax.c2p(x_end, s_end), RIGHT, buff=0.2)),
        )
        self.add(source("S&P 500 with dividends reinvested, adjusted by CPI. Shiller data, Jan 2006 – Jun 2023."))
        self.hold(4)
        self.clear()


# ---------------------------------------------------------------------------
# Why index funds
# ---------------------------------------------------------------------------
class StockPicking(Clip):
    """Most stocks lose to T-bills; a few winners make the market (Bessembinder 2018)."""

    def construct(self):
        rng = random.Random(3)
        kinds = ["win"] * 4 + ["ok"] * 39 + ["lose"] * 57
        rng.shuffle(kinds)
        color = {"win": GOLD, "ok": DEEP_BLUE, "lose": ORANGE}

        def grid_positions(center):
            g = VGroup(*[Square(0.42) for _ in range(100)]).arrange_in_grid(10, 10, buff=0.08).move_to(center)
            return [s.get_center() for s in g]

        home = grid_positions(LEFT * 3)
        cells = VGroup(*[Square(0.42, stroke_width=0, fill_color="#4A505A", fill_opacity=1).move_to(p) for p in home])
        intro = T("Every U.S. stock since 1926, as 100 squares", 26).to_corner(UL, buff=0.55)
        self.play(FadeIn(intro), LaggedStart(*[FadeIn(c, scale=0.6) for c in cells], lag_ratio=0.01), run_time=1.8)
        self.hold(1)
        self.play(LaggedStart(*[c.animate.set_fill(color[k]) for c, k in zip(cells, kinds)], lag_ratio=0.01), run_time=2)
        self.hold(1)

        # Sort by outcome and label each group
        order = sorted(range(100), key=lambda i: ["win", "ok", "lose"].index(kinds[i]))
        self.play(*[cells[i].animate.move_to(home[slot]) for slot, i in enumerate(order)], run_time=2)
        legend = VGroup()
        for kind, pct, text in [
            ("win", "4%", "made all of the market's net gains"),
            ("ok", "39%", "beat Treasury bills"),
            ("lose", "57%", "did worse than Treasury bills"),
        ]:
            row = VGroup(T(pct, 40, color[kind], weight=MEDIUM), T(text, 24)).arrange(RIGHT, buff=0.3)
            legend.add(row)
        legend.arrange(DOWN, aligned_edge=LEFT, buff=0.55).next_to(cells, RIGHT, buff=0.8)
        for row in legend:
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.7)
            self.hold(1.2)
        self.add(source("Bessembinder (2018), \"Do stocks outperform Treasury bills?\" U.S. common stocks 1926–2016."))
        self.hold(2.5)

        # Pick 10 at random, a few times
        self.play(FadeOut(legend), FadeOut(intro),
                  *[cells[i].animate.move_to(home[i]) for i in range(100)], run_time=1.5)
        prompt = T("Pick 10 stocks at random", 26).to_corner(UL, buff=0.55)
        self.play(FadeIn(prompt))
        tally = VGroup()
        anchor = cells.get_right() + RIGHT * 0.8 + UP * 2.0
        for n, picks in enumerate([rng.sample(range(100), 10) for _ in range(5)]):
            rings = VGroup(*[Square(0.5, stroke_color=INK, stroke_width=3).move_to(cells[i]) for i in picks])
            dim = [cells[i].animate.set_opacity(0.25) for i in range(100) if i not in picks]
            self.play(Create(rings), *dim, run_time=0.6)
            found = sum(kinds[i] == "win" for i in picks)
            line = T(f"Try {n + 1}:  {found} winner" + ("" if found == 1 else "s"), 24, GOLD if found else MUTED)
            line.move_to(anchor + DOWN * 0.5 * n, aligned_edge=LEFT)
            self.play(FadeIn(line), run_time=0.4)
            self.wait(0.6)
            self.play(FadeOut(rings), *[c.animate.set_opacity(1) for c in cells], run_time=0.4)
            tally.add(line)
        odds = VGroup(T("65%", 52, GOLD, weight=MEDIUM), T("chance that 10 random picks\nmiss every one of the winners", 24))
        odds.arrange(RIGHT, buff=0.3).next_to(tally, DOWN, buff=0.6).align_to(tally, LEFT)
        self.play(FadeIn(odds))
        self.hold(3)

        # The index holds them all
        frame = SurroundingRectangle(cells, color=BLUE, buff=0.18, corner_radius=0.12, stroke_width=4)
        own_all = T("An index fund owns all 100,\nincluding the 4% that matter", 28).next_to(frame, RIGHT, buff=0.8)
        self.play(FadeOut(tally), FadeOut(odds), FadeOut(prompt))
        self.play(Create(frame), FadeIn(own_all))
        self.hold(4)
        self.clear()


class ActiveFunds(Clip):
    """100 managed funds vs. the index over 15 years (simulation calibrated to SPIVA)."""

    def construct(self):
        months = 180
        rng = random.Random(4)
        paths = []
        for _ in range(100):
            x, pts = 0.0, [0.0]
            for _ in range(months):
                x += rng.gauss(-0.011 / 12, 0.035 / 12**0.5)
                pts.append(x)
            paths.append(pts)

        low = math.floor(min(min(p) for p in paths) * 10) / 10
        ax = axes([0, 15], [low, 0.2], 9.8, 5.2).shift(DOWN * 0.3 + LEFT * 0.5)
        title = VGroup(
            T("100 professionally managed funds vs. the index", 28),
            T("Return relative to an S&P 500 index fund", 22, MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_corner(UL, buff=0.55)
        self.play(FadeIn(title), Create(ax), FadeIn(x_labels(ax, [0, 5, 10, 15], lambda v: f"{v} yrs")),
                  FadeIn(y_labels(ax, [v / 10 for v in range(round(low * 10) + 1, 2) if v], lambda v: f"{v:+.0%}")))
        index = Line(ax.c2p(0, 0), ax.c2p(15, 0), color=BLUE, stroke_width=5)
        self.play(Create(index), FadeIn(T("Index fund", 22, BLUE).next_to(index, RIGHT, buff=0.15).shift(UP * 0.2)))

        xs = [m / 12 for m in range(months + 1)]
        funds = VGroup(*[series_path(ax, xs, p, MUTED, width=1.5).set_stroke(opacity=0.55) for p in paths])
        t = ValueTracker(0)
        counter = always_redraw(
            lambda: VGroup(
                T(f"{sum(p[int(t.get_value() * 12)] > 0 for p in paths)}", 44, GOLD, weight=MEDIUM),
                T("of 100 still ahead", 22),
            ).arrange(RIGHT, buff=0.2).move_to(ax.c2p(3.2, low * 0.8))
        )
        self.add(counter)
        self.play(*[Create(f) for f in funds], t.animate.set_value(15), run_time=8, rate_func=linear)
        ahead = [i for i, p in enumerate(paths) if p[-1] > 0]
        self.play(*[funds[i].animate.set_stroke(GOLD if i in ahead else ORANGE, opacity=1 if i in ahead else 0.35)
                    for i in range(100)], run_time=1)
        self.add(source("Simulated: index − 1.1%/yr fees ± random luck. Real-world check (S&P SPIVA): "
                        "~9 in 10 U.S. large-cap funds trailed the S&P 500 over 15 years."))
        self.hold(4)
        self.clear()


class IndexFund(Clip):
    """One share of an index fund = a sliver of 500 companies, sized by value."""

    def construct(self):
        share = Square(1.2, stroke_width=0, fill_color=BLUE, fill_opacity=1)
        label = T("1 share of an S&P 500 index fund", 28).next_to(share, UP, buff=0.4)
        self.play(GrowFromCenter(share), FadeIn(label))
        self.hold(1.5)

        w, h = 9.0, 5.4
        weights = [1 / (i + 1.5) for i in range(500)]
        total = sum(weights)
        values = [v / total * w * h for v in weights]
        rects = VGroup()
        for x, y, rw, rh in squarify(values, -w / 2, -h / 2, w, h):
            rects.add(
                Rectangle(width=rw, height=rh, stroke_color=BG, stroke_width=1.2, fill_color=BLUE, fill_opacity=1)
                .move_to([x + rw / 2, y + rh / 2, 0])
            )
        rects.shift(DOWN * 0.35)
        self.play(share.animate.stretch_to_fit_width(w).stretch_to_fit_height(h).move_to(rects),
                  label.animate.next_to(rects, UP, buff=0.3), run_time=1.2)
        self.add(rects)
        self.remove(share)
        self.play(rects.animate.set_fill(DEEP_BLUE), run_time=0.6)
        self.play(LaggedStart(*[r.animate.set_fill(BLUE) for r in rects], lag_ratio=0.004), run_time=2.5)
        sub = T("= a sliver of all 500 companies, bigger companies get bigger slices", 22, MUTED)
        sub.next_to(rects, DOWN, buff=0.25)
        self.play(FadeIn(sub))
        self.hold(3.5)
        self.clear()


class Fees(Clip):
    """0.03% vs 1% a year: the gap compounds too."""

    def construct(self):
        def curve(rate):
            mr = (1 + rate) ** (1 / 12) - 1
            return [balance(200, m, m, mr) for m in range(0, 43 * 12 + 1, 3)]

        ages = [22 + m / 12 for m in range(0, 43 * 12 + 1, 3)]
        low, high = curve(0.0697), curve(0.06)
        ax = axes([22, 65], [0, 700000], 9.6, 5).shift(DOWN * 0.35 + LEFT * 0.7)
        title = VGroup(
            T("$200 a month from age 22 to 65", 30),
            T("7% a year before fees", 22, MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_corner(UL, buff=0.55)
        self.play(FadeIn(title), Create(ax), FadeIn(x_labels(ax, [22, 32, 42, 52, 65], lambda v: f"age {v}")),
                  FadeIn(y_labels(ax, [200000, 400000, 600000], lambda v: f"${v // 1000}k")))
        a, b = series_path(ax, ages, low, BLUE), series_path(ax, ages, high, ORANGE)
        self.play(Create(a), Create(b), run_time=5, rate_func=linear)
        gap = Polygon(*[ax.c2p(x, y) for x, y in zip(ages, low)], *[ax.c2p(x, y) for x, y in reversed(list(zip(ages, high)))],
                      stroke_width=0, fill_color=ORANGE, fill_opacity=0.3)
        self.play(FadeIn(gap),
                  FadeIn(VGroup(T("0.03% fee", 22, BLUE), T(money(low[-1]), 26, weight=MEDIUM)).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
                         .next_to(ax.c2p(65, low[-1]), RIGHT, buff=0.2)),
                  FadeIn(VGroup(T("1.00% fee", 22, ORANGE), T(money(high[-1]), 26, weight=MEDIUM)).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
                         .next_to(ax.c2p(65, high[-1]), RIGHT, buff=0.2)))
        lost = VGroup(T(money(low[-1] - high[-1]), 44, GOLD, weight=MEDIUM), T("paid in fees", 24))
        lost.arrange(DOWN, buff=0.1).move_to(ax.c2p(36, 420000))
        self.play(FadeIn(lost))
        self.hold(4)
        self.clear()


# ---------------------------------------------------------------------------
# Compounding and time
# ---------------------------------------------------------------------------
class Compounding(Clip):
    """$1,000 at 7%: what the final balance is made of."""

    def construct(self):
        years = 40
        ax = axes([0, 41], [0, 16000], 9.4, 5.4).shift(DOWN * 0.3 + LEFT * 1.0)
        title = T("$1,000 at 7% a year, never touched", 30).to_corner(UL, buff=0.55)
        self.play(FadeIn(title), Create(ax), FadeIn(x_labels(ax, [1, 10, 20, 30, 40], lambda v: f"year {v}")),
                  FadeIn(y_labels(ax, [5000, 10000, 15000], lambda v: f"${v // 1000}k")))
        unit = ax.c2p(0, 1)[1] - ax.c2p(0, 0)[1]
        width = (ax.c2p(1, 0)[0] - ax.c2p(0, 0)[0]) * 0.7

        def bar(n):
            total = 1000 * 1.07**n
            parts = [(1000, DEEP_BLUE), (70 * n, BLUE), (total - 1000 - 70 * n, GOLD)]
            stack, y = VGroup(), 0
            for value, col in parts:
                if value <= 0:
                    continue
                r = Rectangle(width=width, height=value * unit, stroke_width=0, fill_color=col, fill_opacity=1)
                r.move_to(ax.c2p(n, y + value / 2))
                stack.add(r)
                y += value
            return stack

        bars = VGroup(*[bar(n) for n in range(1, years + 1)])
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.12), run_time=7)

        for n, mult in [(10, "2×"), (21, "4×"), (31, "8×")]:
            self.add(T(mult, 18, MUTED).next_to(bars[n - 1], UP, buff=0.1))
        final = 1000 * 1.07**years
        last = bars[-1]
        labels = VGroup(
            VGroup(T(money(final - 3800), 30, GOLD, weight=MEDIUM), T("growth on growth", 22)),
            VGroup(T("$2,800", 30, BLUE, weight=MEDIUM), T("growth on your $1,000", 22)),
            VGroup(T("$1,000", 30, DEEP_BLUE, weight=MEDIUM), T("what you put in", 22)),
        )
        for lab, seg in zip(labels, [last[2], last[1], last[0]]):
            lab.arrange(DOWN, aligned_edge=LEFT, buff=0.06).next_to(seg, RIGHT, buff=0.35)
        labels[2].align_to(labels[1], LEFT).next_to(labels[1], DOWN, buff=0.25)
        for lab in labels:
            self.play(FadeIn(lab, shift=RIGHT * 0.2), run_time=0.6)
            self.wait(0.8)
        self.hold(4)
        self.clear()


class StartEarly(Clip):
    """Emma invests for 10 years and stops; Liam invests for 33 years."""

    def construct(self):
        ax = axes([22, 65], [0, 350000], 9.6, 4.4).shift(UP * 0.35 + LEFT * 0.6)
        self.play(Create(ax), FadeIn(x_labels(ax, [22, 32, 42, 52, 65], lambda v: f"age {v}")),
                  FadeIn(y_labels(ax, [100000, 200000, 300000], lambda v: f"${v // 1000}k")))
        title = T("$200 a month, 7% a year", 26, MUTED).to_corner(UL, buff=0.5)
        self.add(title)

        def emma(age):
            return balance(200, 120, round((age - 22) * 12))

        def liam(age):
            return balance(200, 396, round(max(age - 32, 0) * 12))

        ages = [22 + m / 12 for m in range(43 * 12 + 1)]
        e_path = series_path(ax, ages, [emma(a) for a in ages], BLUE)
        l_ages = [a for a in ages if a >= 32]
        l_path = series_path(ax, l_ages, [liam(a) for a in l_ages], ORANGE)

        rail_y = ax.c2p(22, 0)[1] - 0.85
        e_rail = Line([ax.c2p(22, 0)[0], rail_y, 0], [ax.c2p(32, 0)[0], rail_y, 0], color=BLUE, stroke_width=10)
        l_rail = Line([ax.c2p(32, 0)[0], rail_y - 0.45, 0], [ax.c2p(65, 0)[0], rail_y - 0.45, 0], color=ORANGE, stroke_width=10)
        e_tag = T("Emma pays in $24,000, then stops", 22, BLUE).next_to(e_rail, RIGHT, buff=0.25)
        l_tag = T("Liam pays in $79,200", 22, ORANGE).next_to(l_rail.get_start(), DOWN, buff=0.2, aligned_edge=LEFT)
        self.play(FadeIn(e_tag), FadeIn(l_tag))

        t = ValueTracker(22)
        e_now = always_redraw(lambda: partial(e_path, (t.get_value() - 22) / 43))
        l_now = always_redraw(lambda: partial(l_path, (t.get_value() - 32) / 33) if t.get_value() > 32 else VMobject())
        e_rail_now = always_redraw(lambda: partial(e_rail, (t.get_value() - 22) / 10))
        l_rail_now = always_redraw(lambda: partial(l_rail, (t.get_value() - 32) / 33) if t.get_value() > 32 else VMobject())
        self.add(e_now, l_now, e_rail_now, l_rail_now)
        self.play(t.animate.set_value(65), run_time=9, rate_func=linear)
        self.play(
            FadeIn(VGroup(T("Emma", 22, BLUE), T(money(emma(65)), 28, weight=MEDIUM)).arrange(DOWN, aligned_edge=LEFT, buff=0.05)
                   .next_to(ax.c2p(65, emma(65)), RIGHT, buff=0.2).shift(UP * 0.2)),
            FadeIn(VGroup(T("Liam", 22, ORANGE), T(money(liam(65)), 28, weight=MEDIUM)).arrange(DOWN, aligned_edge=LEFT, buff=0.05)
                   .next_to(ax.c2p(65, liam(65)), RIGHT, buff=0.2).shift(DOWN * 0.3)),
        )
        self.hold(4)
        self.clear()

        # What each decade of waiting costs
        title = T("$200 a month until 65, 7% a year", 26, MUTED).to_corner(UL, buff=0.5)
        self.play(FadeIn(title))
        base, scale = -2.6, 4.6 / 620000
        bars = VGroup()
        for i, start in enumerate([22, 32, 42]):
            n = (65 - start) * 12
            total, paid = balance(200, n, n), 200 * n
            x = -3.6 + i * 3.6
            paid_bar = Rectangle(width=1.9, height=paid * scale, stroke_width=0, fill_color=DEEP_BLUE, fill_opacity=1)
            paid_bar.move_to([x, base + paid * scale / 2, 0])
            grow_bar = Rectangle(width=1.9, height=(total - paid) * scale, stroke_width=0, fill_color=BLUE, fill_opacity=1)
            grow_bar.next_to(paid_bar, UP, buff=0.03)
            top = T(money(total), 30, weight=MEDIUM).next_to(grow_bar, UP, buff=0.15)
            under = VGroup(T(f"start at {start}", 24), T(f"paid in {money(paid)}", 20, MUTED)).arrange(DOWN, buff=0.08)
            under.next_to(paid_bar, DOWN, buff=0.2)
            bars.add(VGroup(paid_bar, grow_bar, top, under))
        for b in bars:
            self.play(GrowFromEdge(b[0], DOWN), FadeIn(b[3]), run_time=0.6)
            self.play(GrowFromEdge(b[1], DOWN), FadeIn(b[2]), run_time=0.9)
            self.wait(0.6)
        key = VGroup(
            VGroup(Square(0.22, stroke_width=0, fill_color=DEEP_BLUE, fill_opacity=1), T("paid in", 20, MUTED)).arrange(RIGHT, buff=0.12),
            VGroup(Square(0.22, stroke_width=0, fill_color=BLUE, fill_opacity=1), T("growth", 20, MUTED)).arrange(RIGHT, buff=0.12),
        ).arrange(RIGHT, buff=0.4).to_corner(UR, buff=0.55)
        self.play(FadeIn(key))
        self.hold(4)
        self.clear()


class TimeHorizon(Clip):
    """Every start month since 1927: the longer you hold, the narrower the outcomes."""

    def construct(self):
        r = DATA["rolling"]["returns"]
        ax = axes([0, 4], [-0.7, 1.5], 9.6, 5.0).shift(UP * 0.05 + RIGHT * 0.4)
        title = VGroup(
            T("S&P 500 average yearly return, for every start month since 1927", 26),
            T("Held for…", 22, MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_corner(UL, buff=0.5)
        zero = Line(ax.c2p(0, 0), ax.c2p(4, 0), color=MUTED, stroke_width=2)
        self.play(FadeIn(title), FadeIn(y_labels(ax, [-0.5, 0.5, 1.0], lambda v: f"{v:+.0%}")), Create(zero),
                  FadeIn(T("0%", 20, MUTED).next_to(ax.c2p(0, 0), LEFT, buff=0.2)))
        rng = random.Random(1)
        for col, years in enumerate(["1", "5", "10", "20"]):
            values = r[years][::2]
            dots = VGroup(
                *[Dot(ax.c2p(col + 0.5 + rng.uniform(-0.32, 0.32), v), radius=0.028, color=ORANGE if v < 0 else BLUE,
                      fill_opacity=0.8) for v in values]
            )
            lost = sum(v < 0 for v in r[years]) / len(r[years])
            label = VGroup(
                T(f"{years} year" + ("" if years == "1" else "s"), 24),
                T(f"{lost:.0%} lost money", 20, ORANGE if lost > 0 else BLUE),
            ).arrange(DOWN, buff=0.1).next_to(ax.c2p(col + 0.5, -0.7), DOWN, buff=0.2)
            self.play(LaggedStart(*[FadeIn(d, scale=2) for d in dots], lag_ratio=0.002), FadeIn(label), run_time=1.8)
            self.hold(1.2)
        self.add(source("S&P 500 with dividends reinvested, before inflation. Monthly averages, Dec 1926 – Jun 2023 (Shiller)."))
        self.hold(4)
        self.clear()


class Crashes(Clip):
    """Every bear market since 1928, and what came after (real data, log scale)."""

    def construct(self):
        h = DATA["history"]
        xs = [year_of(d) for d, _ in h["points"]]
        ys = [math.log10(p) for _, p in h["points"]]
        ax = axes([1928, 2027], [0.55, 4.3], 11.6, 5.6).shift(DOWN * 0.3 + RIGHT * 0.3)
        title = VGroup(T("S&P 500, 1928 – 2026", 28), T("log scale: equal steps are equal % changes", 20, MUTED))
        title.arrange(DOWN, aligned_edge=LEFT, buff=0.1).to_corner(UL, buff=0.5)
        self.play(FadeIn(title), Create(ax),
                  FadeIn(x_labels(ax, [1930, 1950, 1970, 1990, 2010])),
                  FadeIn(y_labels(ax, [1, 2, 3], lambda v: f"{10 ** v:,}")))
        line = series_path(ax, xs, ys, BLUE, width=2.5)
        self.play(Create(line), run_time=8, rate_func=linear)

        shades, tags = VGroup(), VGroup()
        for d in h["drawdowns"]:
            x0, x1 = year_of(d["peak"]), year_of(d["recovered"])
            shades.add(Rectangle(width=ax.c2p(x1, 0)[0] - ax.c2p(x0, 0)[0], height=ax.y_length, stroke_width=0,
                                 fill_color=ORANGE, fill_opacity=0.16).move_to([(ax.c2p(x0, 0)[0] + ax.c2p(x1, 0)[0]) / 2, ax.get_center()[1], 0]))
            if d["depth"] <= -0.3:
                level = 4.15 - 0.25 * (len(tags) % 2)
                tags.add(T(f"{d['depth']:.0%}".replace("-", "−"), 20, ORANGE, weight=MEDIUM)
                         .move_to(ax.c2p(year_of(d["trough"]), level)))
        self.play(FadeIn(shades), LaggedStart(*[FadeIn(t, shift=UP * 0.1) for t in tags], lag_ratio=0.15), run_time=2)
        self.bring_to_front(line)
        self.add(source("Shaded: peak to full recovery, drops of 20% or more. Daily closes 1928–2019, monthly averages after. Price only."))
        self.hold(5)
        self.clear()


# ---------------------------------------------------------------------------
# Recurring investing and timing
# ---------------------------------------------------------------------------
class DollarCostAveraging(Clip):
    """$100 every month through the 2008 crash (real monthly prices)."""

    def construct(self):
        d = DATA["dca"]
        prices, months = d["prices"], d["months"]
        n = len(prices)
        ax = axes([0, n - 1], [600, 1600], 11, 2.4).to_edge(UP, buff=0.9).shift(RIGHT * 0.3)
        title = T("$100 into the S&P 500 every month, 2008 – 2010", 26).to_corner(UL, buff=0.35)
        self.play(FadeIn(title), Create(ax), FadeIn(y_labels(ax, [800, 1200, 1600], lambda v: f"{v:,}", size=18)),
                  FadeIn(x_labels(ax, [0, 12, 24, 35], lambda i: ["Jan 2008", "Jan 2009", "Jan 2010", "Dec 2010"][[0, 12, 24, 35].index(i)], size=18)))
        price_lbl = T("price", 18, GOLD).next_to(ax.c2p(0, 1600), RIGHT, buff=0.1)
        self.add(price_lbl)

        base_y = -3.55
        shares_lbl = T("shares bought (each dot = 0.01 share)", 18, MUTED).move_to([ax.c2p(0, 0)[0], base_y - 0.3, 0], aligned_edge=LEFT)
        self.add(shares_lbl)
        steps = []
        dots_all = VGroup()
        for i, p in enumerate(prices):
            x = ax.c2p(i, 600)[0]
            k = round(10000 / p)
            col = VGroup(*[Dot([x, base_y + 0.13 * j, 0], radius=0.05, color=BLUE) for j in range(k)])
            dots_all.add(col)
            pt = Dot(ax.c2p(i, p), radius=0.05, color=GOLD)
            seg = Line(ax.c2p(i - 1, prices[i - 1]), ax.c2p(i, p), color=GOLD, stroke_width=3) if i else VMobject()
            steps.append(AnimationGroup(Create(seg), FadeIn(pt), LaggedStart(*[FadeIn(dot, shift=DOWN * 0.2) for dot in col], lag_ratio=0.05)))
        self.play(LaggedStart(*steps, lag_ratio=0.6), run_time=10)
        self.hold(1.5)

        shares = sum(100 / p for p in prices)

        paid, worth = 100 * n, shares * prices[-1]
        lump = paid * prices[-1] / prices[0]
        result = VGroup(
            VGroup(T(f"{money(paid)} in, monthly", 22), T(money(worth), 36, BLUE, weight=MEDIUM)).arrange(DOWN, buff=0.08),
            VGroup(T(f"{money(paid)} in, all in Jan 2008", 22), T(money(lump), 36, ORANGE, weight=MEDIUM)).arrange(DOWN, buff=0.08),
        ).arrange(RIGHT, buff=1.2).move_to(ax.get_center() + DOWN * 2.35 + RIGHT * 2.8)
        self.play(FadeIn(result))
        self.add(source("S&P 500 monthly average prices (Shiller), price only. Value at Dec 2010.").to_corner(UR, buff=0.25))
        self.hold(4)
        self.clear()


class BeatTheCouch(Clip):
    """The beatthecouch.com game: a sensible-sounding timing rule vs. buy-and-hold."""

    def construct(self):
        g = DATA["game"]
        prices, flags = g["prices"], g["in_market"]
        n = len(prices)
        couch = [10000 * p / prices[0] for p in prices]
        you = [10000.0]
        for i in range(1, n):
            you.append(you[-1] * (prices[i] / prices[i - 1] if flags[i - 1] else 1))

        ax = axes([0, n - 1], [8000, 12000], 8.6, 4.8).shift(LEFT * 1.6 + DOWN * 0.45)
        title = VGroup(
            T("A hidden 2-year stretch of the S&P 500", 28),
            T("Your rule: sell after a 10% drop, buy back after a 10% bounce", 22, MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_corner(UL, buff=0.5)
        self.play(FadeIn(title), Create(ax), FadeIn(y_labels(ax, [9000, 10000, 11000, 12000], lambda v: f"${v // 1000}k")))

        xs = list(range(n))
        couch_path = series_path(ax, xs, couch, BLUE, width=3)
        you_path = series_path(ax, xs, you, ORANGE, width=3)
        out_spans = []
        i = 0
        while i < n:
            if not flags[i]:
                j = i
                while j < n and not flags[j]:
                    j += 1
                out_spans.append((i, j))
                i = j
            else:
                i += 1

        t = ValueTracker(0)

        def shading():
            now = t.get_value()
            group = VGroup()
            for a, b in out_spans:
                if a < now:
                    b = min(b, now)
                    x0, x1 = ax.c2p(a, 8000)[0], ax.c2p(b, 8000)[0]
                    group.add(Rectangle(width=max(x1 - x0, 0.01), height=ax.y_length, stroke_width=0,
                                        fill_color=ORANGE, fill_opacity=0.14).move_to([(x0 + x1) / 2, ax.get_center()[1], 0]))
            return group

        def markers():
            group = VGroup()
            for action, idx in g["trades"]:
                if idx <= t.get_value():
                    tri = Triangle(color=ORANGE if action == "sell" else BLUE, fill_opacity=1, stroke_width=0).scale(0.12)
                    if action == "sell":
                        tri.rotate(PI)
                    tri.next_to(ax.c2p(idx, couch[idx]), UP if action == "sell" else DOWN, buff=0.08)
                    group.add(tri)
            return group

        def scoreboard():
            k = min(int(t.get_value()), n - 1)
            rows = VGroup(
                VGroup(T("Couch", 24, BLUE), T("buys day 1, never trades", 16, MUTED), T(money(couch[k]), 36, weight=MEDIUM)),
                VGroup(T("You", 24, ORANGE), T("follow the rule", 16, MUTED), T(money(you[k]), 36, weight=MEDIUM)),
            )
            for r in rows:
                r.arrange(DOWN, aligned_edge=LEFT, buff=0.06)
            return rows.arrange(DOWN, aligned_edge=LEFT, buff=0.5).next_to(ax, RIGHT, buff=0.6).shift(UP * 0.4)

        shade = always_redraw(shading)
        self.add(shade)
        self.add(always_redraw(lambda: partial(couch_path, t.get_value() / (n - 1))),
                 always_redraw(lambda: partial(you_path, t.get_value() / (n - 1))),
                 always_redraw(markers), always_redraw(scoreboard))
        self.play(t.animate.set_value(n - 1), run_time=14, rate_func=linear)
        self.hold(2)
        reveal = T("June 2015 – May 2017", 24, GOLD).next_to(ax, DOWN, buff=0.3)
        self.play(FadeIn(reveal, shift=UP * 0.1))
        self.hold(3)
        self.clear()

        # Audit: was it skill? Compare with 1,000 random replays of the same trades
        replays = [10000 * r for r in g["replays"]]
        lo, hi, bins = 500 * math.floor(min(replays) / 500), 500 * math.ceil(max(replays) / 500), 40
        counts = [0] * bins
        for v in replays:
            counts[min(max(int((v - lo) / (hi - lo) * bins), 0), bins - 1)] += 1
        hax = axes([lo, hi], [0, max(counts) * 1.15], 10.4, 4.0).shift(DOWN * 0.2)
        title = VGroup(
            T("Was it the market or the timing?", 28),
            T("1,000 random replays: same 4 trades, same days out of the market, random dates", 22, MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_corner(UL, buff=0.5)
        self.play(FadeIn(title), Create(hax), FadeIn(x_labels(hax, range(lo, hi + 1, 1000), lambda v: f"${v / 1000:g}k")))
        bw = (hi - lo) / bins
        hist = VGroup(*[
            Rectangle(width=hax.c2p(lo + bw, 0)[0] - hax.c2p(lo, 0)[0] - 0.03, height=max(c, 0.01) * (hax.c2p(0, 1)[1] - hax.c2p(0, 0)[1]),
                      stroke_width=0, fill_color=MUTED, fill_opacity=0.7).move_to(hax.c2p(lo + bw * (i + 0.5), c / 2))
            for i, c in enumerate(counts)
        ])
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in hist], lag_ratio=0.03), run_time=2)
        for value, name, col in [(you[-1], "You", ORANGE), (couch[-1], "Couch", BLUE)]:
            mark = Line(hax.c2p(value, 0), hax.c2p(value, max(counts) * 1.1), color=col, stroke_width=4)
            self.play(Create(mark), FadeIn(VGroup(T(name, 22, col), T(money(value), 26, weight=MEDIUM))
                                           .arrange(DOWN, buff=0.05).next_to(mark, UP, buff=0.1)))
        worse = sum(r > you[-1] for r in replays) / len(replays)
        self.play(FadeIn(caption(f"Your rule did worse than {worse:.1%} of random timings", 30, GOLD)))
        self.add(source("Game idea: beatthecouch.com. S&P 500 daily closes, price only."))
        self.hold(4)
        self.clear()


class TimingRules(Clip):
    """The same rule on every 2-year window since 1928, then 16 variations of it."""

    def construct(self):
        w = DATA["all_windows"]
        xs = [year_of(x["start"]) for x in w]
        edges = [x["edge"] for x in w]
        lo, hi = math.floor(min(edges) * 10) / 10, math.ceil(max(edges) * 10) / 10
        ax = axes([1928, 2018], [lo, hi], 11.4, 5).shift(DOWN * 0.3 + RIGHT * 0.3)
        title = VGroup(
            T("Your rule vs. the couch, every 2-year stretch from 1928 to 2019", 26),
            T("Ending balance of the rule, compared with the couch", 22, MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_corner(UL, buff=0.5)
        self.play(FadeIn(title), Create(ax), FadeIn(x_labels(ax, [1930, 1950, 1970, 1990, 2010])),
                  FadeIn(y_labels(ax, [v for v in (-0.3, 0.5, 1.0, 1.5, 2.0, 2.5) if lo <= v <= hi], lambda v: f"{v:+.0%}")))
        self.add(Line(ax.c2p(1928, 0), ax.c2p(2018, 0), color=MUTED, stroke_width=1.5))
        ahead = segments([(ax.c2p(x, 0), ax.c2p(x, e)) for x, e in zip(xs, edges) if e > 0], ORANGE, 1.6)
        behind = segments([(ax.c2p(x, 0), ax.c2p(x, e)) for x, e in zip(xs, edges) if e <= 0], BLUE, 1.6)
        self.play(Create(ahead), Create(behind), run_time=5, rate_func=linear)
        wins = sum(e > 0 for e in edges)
        self.play(
            FadeIn(T(f"rule ahead: {wins / len(edges):.0%} of the time", 22, ORANGE).next_to(ax.c2p(2018, hi * 0.8), LEFT, buff=0)),
            FadeIn(T(f"couch ahead: {1 - wins / len(edges):.0%}", 22, BLUE).next_to(ax.c2p(2018, lo * 0.8), LEFT, buff=0)),
        )
        self.add(source(f"{len(edges)} overlapping 2-year windows (one per month) in which the rule traded. S&P 500 daily closes, price only."))
        self.hold(4)
        self.clear()

        # Maybe the thresholds were wrong? Try 16 rules
        grid = DATA["rule_grid"]
        levels = grid["levels"]
        title = VGroup(
            T("Maybe it's the numbers? Try 16 versions of the rule", 28),
            T("How often each one beat the couch, 1928 – 2019", 22, MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_corner(UL, buff=0.5)
        cells = VGroup()
        for r, row in enumerate(grid["win_rate"]):
            for c, rate in enumerate(row):
                fill = interpolate_color(ManimColor(FAINT), ManimColor(ORANGE), min(rate / 0.5, 1))
                sq = Square(1.15, stroke_color=BG, stroke_width=4, fill_color=fill, fill_opacity=1)
                sq.move_to([c * 1.15, -r * 1.15, 0])
                cells.add(VGroup(sq, T(f"{rate:.0%}", 26, INK, weight=MEDIUM).move_to(sq)))
        cells.move_to(DOWN * 0.75 + RIGHT * 0.6)
        cols = VGroup(*[T(f"{v:.0%}", 20, MUTED).next_to(cells[c][0], UP, buff=0.15) for c, v in enumerate(levels)])
        rows = VGroup(*[T(f"{v:.0%}", 20, MUTED).next_to(cells[r * 4][0], LEFT, buff=0.15) for r, v in enumerate(levels)])
        col_title = T("buy back after a bounce of", 20).next_to(cols, UP, buff=0.2)
        row_title = T("sell after\na drop of", 20).next_to(rows, LEFT, buff=0.3)
        self.play(FadeIn(title), FadeIn(cols), FadeIn(rows), FadeIn(col_title), FadeIn(row_title))
        self.play(LaggedStart(*[FadeIn(c, scale=0.85) for c in cells], lag_ratio=0.08), run_time=2.5)
        best = max(max(row) for row in grid["win_rate"])
        self.play(FadeIn(caption(f"Best of all 16: the rule won {best:.0%} of the time", 30, GOLD)))
        self.hold(4)
        self.clear()


class BestDays(Clip):
    """The best days cluster around the worst ones, and missing them is costly."""

    def construct(self):
        d = DATA["best_days"]
        dates, rets = d["dates"][1:], d["returns"]
        xs = [year_of(x) for x in dates]
        ax = axes([2000, 2020], [-0.1, 0.12], 11.4, 4.4).shift(UP * 0.05 + RIGHT * 0.3)
        title = VGroup(
            T("Every trading day of the S&P 500, 2000 – 2019", 28),
            T(f"{len(rets):,} days, height = that day's move", 22, MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_corner(UL, buff=0.5)
        self.play(FadeIn(title), Create(ax), FadeIn(x_labels(ax, [2000, 2005, 2010, 2015, 2020])),
                  FadeIn(y_labels(ax, [-0.08, -0.04, 0.04, 0.08], lambda v: f"{v:+.0%}")))
        days = segments([(ax.c2p(x, 0), ax.c2p(x, r)) for x, r in zip(xs, rets)], MUTED, 1, 0.6)
        self.play(Create(days), run_time=4, rate_func=linear)
        best = segments([(ax.c2p(xs[i], 0), ax.c2p(xs[i], rets[i])) for i in d["best10"]], BLUE, 4)
        worst = segments([(ax.c2p(xs[i], 0), ax.c2p(xs[i], rets[i])) for i in d["worst10"]], ORANGE, 4)
        self.play(days.animate.set_stroke(opacity=0.25), Create(best), Create(worst))
        self.play(FadeIn(T("10 best days", 22, BLUE).next_to(ax.c2p(2013, 0.1), RIGHT, buff=0)),
                  FadeIn(T("10 worst days", 22, ORANGE).next_to(ax.c2p(2013, -0.085), RIGHT, buff=0)))
        crisis = [i for i in d["best10"] if "2008-09" <= dates[i] <= "2009-03-31"]
        self.play(FadeIn(caption(f"{len(crisis)} of the 10 best days came in the same months as the worst", 28)))
        self.hold(4)
        self.clear()

        # $10,000 fully invested vs. missing those 10 days
        full, missed = d["full"], d["missed10"]
        yrs = [2000 + 20 * i / (len(full) - 1) for i in range(len(full))]
        gax = axes([2000, 2020], [0, 25000], 9.2, 5).shift(DOWN * 0.3 + LEFT * 1.0)
        title = T("$10,000 in the S&P 500 on Jan 1, 2000", 28).to_corner(UL, buff=0.5)
        self.play(FadeIn(title), Create(gax), FadeIn(x_labels(gax, [2000, 2005, 2010, 2015, 2020])),
                  FadeIn(y_labels(gax, [10000, 20000], lambda v: f"${v // 1000}k")))
        a, b = series_path(gax, yrs, full, BLUE, 3), series_path(gax, yrs, missed, ORANGE, 3)
        self.play(Create(a), Create(b), run_time=5, rate_func=linear)
        self.play(
            FadeIn(VGroup(T("stayed invested", 22, BLUE), T(money(d["final_full"]), 30, weight=MEDIUM))
                   .arrange(DOWN, aligned_edge=LEFT, buff=0.05).next_to(gax.c2p(2020, full[-1]), RIGHT, buff=0.2)),
            FadeIn(VGroup(T("missed the 10 best days", 22, ORANGE), T(money(d["final_missed"]["10"]), 30, weight=MEDIUM))
                   .arrange(DOWN, aligned_edge=LEFT, buff=0.05).next_to(gax.c2p(2020, missed[-1]), RIGHT, buff=0.2)),
        )
        self.add(source("S&P 500 daily closes, price only (excludes dividends), Dec 31 1999 – Dec 23 2019."))
        self.hold(4)
        self.clear()


# ---------------------------------------------------------------------------
# Taxes
# ---------------------------------------------------------------------------
class Taxes(Clip):
    """Holding over a year lowers the rate; holding for decades defers the bill."""

    def construct(self):
        line = Line(LEFT * 5, RIGHT * 5, color=FAINT, stroke_width=3).shift(UP * 0.6)
        buy = VGroup(Dot(line.get_start(), color=INK), T("buy", 22).next_to(line.get_start(), UP, buff=0.2))
        mark = Line(UP * 0.3, DOWN * 0.3, color=GOLD, stroke_width=4).move_to(line.get_center())
        year = T("1 year", 22, GOLD).next_to(mark, UP, buff=0.15)
        short = Line(line.get_start(), line.get_center(), color=ORANGE, stroke_width=10)
        long = Line(line.get_center(), line.get_end(), color=BLUE, stroke_width=10)
        self.play(Create(line), FadeIn(buy))
        self.play(Create(mark), FadeIn(year))
        self.play(Create(short))
        st = VGroup(T("sell within a year", 22, MUTED), T("10 – 37%", 40, ORANGE, weight=MEDIUM),
                    T("taxed like your paycheck", 20, MUTED)).arrange(DOWN, buff=0.1).next_to(short, DOWN, buff=0.4)
        self.play(FadeIn(st))
        self.play(Create(long))
        lt = VGroup(T("hold over a year", 22, MUTED), T("0%, 15% or 20%", 40, BLUE, weight=MEDIUM),
                    T("many students qualify for 0%", 20, MUTED)).arrange(DOWN, buff=0.1).next_to(long, DOWN, buff=0.4)
        self.play(FadeIn(lt))
        self.add(source("U.S. federal capital-gains rates; brackets depend on income."))
        self.hold(4)
        self.clear()

        # Tax drag: pay every year vs. once at the end
        ax = axes([0, 40], [0, 160000], 8.6, 5).shift(DOWN * 0.35 + LEFT * 1.4)
        title = VGroup(
            T("$10,000 earning 7% a year, for 40 years", 28),
            T("Same returns. Only the timing of the tax bill differs.", 22, MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_corner(UL, buff=0.5)
        self.play(FadeIn(title), Create(ax), FadeIn(x_labels(ax, [0, 10, 20, 30, 40], lambda v: f"year {v}")),
                  FadeIn(y_labels(ax, [50000, 100000, 150000], lambda v: f"${v // 1000}k")))
        yrs = [i / 4 for i in range(161)]
        hold_path = series_path(ax, yrs, [10000 * 1.07**y for y in yrs], BLUE)
        trade_rate = 1 + 0.07 * (1 - 0.22)
        trade_path = series_path(ax, yrs, [10000 * trade_rate**y for y in yrs], ORANGE)
        self.play(Create(hold_path), Create(trade_path), run_time=5, rate_func=linear)
        pre = 10000 * 1.07**40
        after = 10000 + (pre - 10000) * 0.85
        bite = Line(ax.c2p(40, pre), ax.c2p(40, after), color=BLUE, stroke_width=4)
        self.play(Create(bite))
        traded = 10000 * trade_rate**40
        self.play(
            FadeIn(VGroup(T("hold, pay 15% at the end", 20, BLUE), T(money(after), 30, weight=MEDIUM))
                   .arrange(DOWN, aligned_edge=LEFT, buff=0.05).next_to(ax.c2p(40, after), RIGHT, buff=0.2)),
            FadeIn(VGroup(T("sell yearly, pay 22% each time", 20, ORANGE), T(money(traded), 30, weight=MEDIUM))
                   .arrange(DOWN, aligned_edge=LEFT, buff=0.05).next_to(ax.c2p(40, traded), RIGHT, buff=0.2)),
        )
        self.hold(4)
        self.clear()


class Accounts(Clip):
    """401(k) match and Roth IRA: where the tax-free money is."""

    def construct(self):
        # Employer match
        you = VGroup(Circle(0.75, fill_color=BLUE, fill_opacity=1, stroke_width=0), T("$1", 34, BG, weight=BOLD))
        boss = VGroup(Circle(0.75, fill_color=GOLD, fill_opacity=1, stroke_width=0), T("$1", 34, BG, weight=BOLD))
        you_lbl = T("you put in", 22, MUTED).next_to(you, DOWN, buff=0.25)
        self.play(FadeIn(you, scale=0.6), FadeIn(you_lbl))
        self.hold(1)
        boss.next_to(you, RIGHT, buff=0.4)
        boss_lbl = T("employer match", 22, MUTED).next_to(boss, DOWN, buff=0.25)
        self.play(FadeIn(boss, shift=LEFT * 0.5), FadeIn(boss_lbl))
        gain = VGroup(T("+100%", 60, GOLD, weight=MEDIUM), T("before the market does anything", 22, MUTED))
        gain.arrange(DOWN, buff=0.1).next_to(VGroup(you, boss), UP, buff=0.6)
        self.play(FadeIn(gain, shift=UP * 0.2))
        self.add(source("A 401(k) match is often 50–100% of what you put in, up to a limit."))
        self.hold(4)
        self.clear()

        # Roth IRA vs. a taxable account: same growth, different exit
        title = VGroup(
            T("$1,000 invested at age 22, grown at 7% until 62", 28),
            T("Roth IRA: you pay tax on the money going in, never on what it grows into", 22, MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_corner(UL, buff=0.5)
        self.play(FadeIn(title))
        final = 1000 * 1.07**40
        tax = (final - 1000) * 0.15
        scale = 4.6 / final
        base = -2.6
        cols = VGroup()
        for i, (name, color, keep) in enumerate([("Roth IRA", BLUE, final), ("Taxable account", ORANGE, final - tax)]):
            x = -2.2 + i * 4.4
            bar = Rectangle(width=2.2, height=keep * scale, stroke_width=0, fill_color=color, fill_opacity=1)
            bar.move_to([x, base + keep * scale / 2, 0])
            parts = VGroup(bar, T(name, 24).next_to(bar, DOWN, buff=0.2))
            top = T(money(keep), 32, weight=MEDIUM)
            if keep < final:
                cut = Rectangle(width=2.2, height=tax * scale, stroke_color=ORANGE, stroke_width=2, fill_opacity=0)
                cut = DashedVMobject(cut, num_dashes=30).next_to(bar, UP, buff=0)
                parts.add(cut, T(f"−{money(tax)} tax on gains", 20, ORANGE).next_to(cut, RIGHT, buff=0.2))
                top.next_to(cut, UP, buff=0.12)
            else:
                top.next_to(bar, UP, buff=0.12)
            parts.add(top)
            cols.add(parts)
        for c in cols:
            self.play(GrowFromEdge(c[0], DOWN), FadeIn(c[1:]), run_time=1)
            self.hold(1)
        self.add(source("Assumes a 15% long-term capital-gains rate. Roth IRA limit: $7,500 for 2026; requires earned income."))
        self.hold(4)
        self.clear()


# ---------------------------------------------------------------------------
# Making decisions
# ---------------------------------------------------------------------------
class Priorities(Clip):
    """Where each dollar goes first: buckets that overflow into the next."""

    def construct(self):
        names = [
            ("Emergency fund", "3–6 months of costs"),
            ("Credit-card debt", "~20%+ interest"),
            ("401(k) match", "free money"),
            ("Roth IRA", "up to $7,500 a year"),
            ("Brokerage account", "no limit"),
        ]
        buckets, fills, labels = [], [], VGroup()
        bw, bh = 1.7, 1.15
        for i, (name, note) in enumerate(names):
            center = np.array([-5.4 + i * 2.7, 1.45 - i * 0.95, 0])
            u = VMobject(stroke_color=MUTED, stroke_width=3)
            u.set_points_as_corners([center + [-bw / 2, bh / 2, 0], center + [-bw / 2, -bh / 2, 0],
                                     center + [bw / 2, -bh / 2, 0], center + [bw / 2, bh / 2, 0]])
            buckets.append(u)
            labels.add(VGroup(T(name, 22), T(note, 18, MUTED)).arrange(DOWN, buff=0.06).next_to(u, DOWN, buff=0.2))
            fills.append((center, ValueTracker(0)))
        source_pt = buckets[0].get_top() + UP * 1.0 + LEFT * 0.2
        paycheck = T("each paycheck", 22, GOLD).next_to(source_pt, UP, buff=0.1)
        self.play(*[Create(b) for b in buckets], FadeIn(labels), FadeIn(paycheck))

        def water(center, level, color=BLUE):
            h = max(level * (bh - 0.1), 0.001)
            return Rectangle(width=bw - 0.1, height=h, stroke_width=0, fill_color=color, fill_opacity=0.85).move_to(
                center + [0, -bh / 2 + 0.05 + h / 2, 0])

        for center, level in fills:
            self.add(always_redraw(lambda c=center, lv=level: water(c, lv.get_value())))
        for i, (center, level) in enumerate(fills):
            if i == 0:
                stream = Line(source_pt, center + [-0.2, bh / 2 - 0.25, 0], color=BLUE, stroke_width=6)
            else:
                lip = fills[i - 1][0] + [bw / 2, bh / 2, 0]
                drop_x = center[0] - bw / 2 + 0.4
                stream = VMobject(stroke_color=BLUE, stroke_width=6).set_points_as_corners(
                    [lip, [drop_x, lip[1], 0], [drop_x, center[1] + bh / 2 - 0.25, 0]])
            self.play(Create(stream), run_time=0.5)
            self.play(level.animate.set_value(1 if i < 4 else 0.55), run_time=1.4)
            self.wait(0.6)
        self.hold(4)
        self.clear()

        # How the mix shifts with age
        ax = axes([20, 65], [0, 1], 10, 4.8).shift(DOWN * 0.3)
        title = VGroup(
            T("How a typical target-date fund invests as you age", 28),
            T("It shifts from stocks to bonds automatically", 22, MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_corner(UL, buff=0.5)
        self.play(FadeIn(title), Create(ax), FadeIn(x_labels(ax, [20, 30, 40, 50, 65], lambda v: f"age {v}")),
                  FadeIn(y_labels(ax, [0.5, 1.0], lambda v: f"{v:.0%}", grid=False)))

        def stocks(age):
            return 0.9 if age <= 40 else 0.9 - 0.4 * (age - 40) / 25

        ages = [20 + i * 0.5 for i in range(91)]
        stock_area = Polygon(ax.c2p(20, 0), *[ax.c2p(a, stocks(a)) for a in ages], ax.c2p(65, 0),
                             stroke_width=0, fill_color=BLUE, fill_opacity=0.9)
        bond_area = Polygon(*[ax.c2p(a, stocks(a)) for a in ages], ax.c2p(65, 1), ax.c2p(20, 1),
                            stroke_width=0, fill_color=DEEP_BLUE, fill_opacity=0.9)
        self.play(FadeIn(stock_area), run_time=1)
        self.play(FadeIn(bond_area), run_time=1)
        self.play(FadeIn(T("stocks", 28, BG, weight=MEDIUM).move_to(ax.c2p(32, 0.45))),
                  FadeIn(T("bonds", 24, INK, weight=MEDIUM).move_to(ax.c2p(58, 0.85))))
        self.add(source("Illustrative glide path; each fund family sets its own."))
        self.hold(4)
        self.clear()
