"""
Start Early, Stay Invested — an investing explainer for college students.

Render a single scene (low quality preview):
    manim -pql investing_early.py Compounding

Render the whole video (see render_all.sh):
    ./render_all.sh            # 1080p60
    ./render_all.sh -ql        # quick 480p preview

Only Manim's Text (Pango) is used, so no LaTeX installation is required.
All figures are illustrative and assume a 7% average annual return
unless noted otherwise. This video is educational, not financial advice.
"""

from manim import *

# ---------------------------------------------------------------------------
# Style
# ---------------------------------------------------------------------------
BG = "#0B1221"
PANEL = "#16213A"
INK = "#E8EEF7"
MUTED = "#8A99B4"
GREEN = "#34D399"
GOLD = "#FBBF24"
RED = "#F87171"
BLUE = "#60A5FA"
PURPLE = "#A78BFA"
FONT = "Inter"  # falls back to the system sans-serif if Inter isn't installed

config.background_color = BG

SECTIONS = [
    "What is investing?",
    "Why index funds & ETFs?",
    "The power of compounding",
    "Why starting early wins",
    "Automate it: recurring investing",
    "Hold long, pay less tax",
    "Making investment decisions",
]

ANNUAL_RETURN = 0.07
MONTHLY_RETURN = (1 + ANNUAL_RETURN) ** (1 / 12) - 1


def T(text, size=32, color=INK, weight=NORMAL, **kwargs):
    return Text(text, font=FONT, font_size=size, color=color, weight=weight, **kwargs)


def money(x):
    return f"${x:,.0f}"


def monthly_balance(monthly, months_contributing, months_total, rate=MONTHLY_RETURN):
    """Balance after `months_total` months, contributing for the first `months_contributing`."""
    balance = 0.0
    for m in range(months_total):
        if m < months_contributing:
            balance += monthly
        balance *= 1 + rate
    return balance


def card(width, height, color=PANEL, stroke=None):
    return RoundedRectangle(
        corner_radius=0.18,
        width=width,
        height=height,
        fill_color=color,
        fill_opacity=1,
        stroke_color=stroke or color,
        stroke_width=2 if stroke else 0,
    )


def bullet_list(items, size=28, color=INK, dot_color=GREEN, buff=0.32):
    rows = VGroup()
    for item in items:
        dot = Dot(radius=0.07, color=dot_color)
        txt = T(item, size, color)
        rows.add(VGroup(dot, txt).arrange(RIGHT, buff=0.25))
    rows.arrange(DOWN, aligned_edge=LEFT, buff=buff)
    return rows


def plain_axes(x_range, y_range, x_length, y_length):
    return Axes(
        x_range=x_range,
        y_range=y_range,
        x_length=x_length,
        y_length=y_length,
        axis_config={"color": MUTED, "include_tip": False, "stroke_width": 2},
        tips=False,
    )


def label_axes(axes, xs, x_fmt, ys, y_fmt, size=20):
    """Tick labels drawn with Text so no LaTeX is needed."""
    labels = VGroup()
    for x in xs:
        labels.add(T(x_fmt(x), size, MUTED).next_to(axes.c2p(x, axes.y_range[0]), DOWN, buff=0.18))
    for y in ys:
        labels.add(T(y_fmt(y), size, MUTED).next_to(axes.c2p(axes.x_range[0], y), LEFT, buff=0.18))
    return labels


def fit(content, box, pad=0.5):
    """Center content in box, shrinking it if it would overflow."""
    if content.width > box.width - pad:
        content.scale_to_fit_width(box.width - pad)
    if content.height > box.height - pad:
        content.scale_to_fit_height(box.height - pad)
    return content.move_to(box)


def lines(text, size=20, color=MUTED, buff=0.06):
    """Multi-line Text with each line centered (Pango left-aligns '\n' text)."""
    return VGroup(*[T(line, size, color) for line in text.split("\n")]).arrange(DOWN, buff=buff)


def source_note(text):
    return T(text, 16, MUTED).to_corner(UR, buff=0.3)


class Base(Scene):
    """Stretches every pause by PACE so viewers have time to read."""

    PACE = 1.3

    def wait(self, duration=1.0, *args, **kwargs):
        super().wait(duration * self.PACE, *args, **kwargs)


class Section(Base):
    """Base scene with a consistent header and transitions."""

    number = None

    def header(self, title=None):
        title = title or SECTIONS[self.number - 1]
        kicker = T(f"PART {self.number}", 20, GOLD, weight=BOLD)
        heading = T(title, 44, weight=BOLD)
        group = VGroup(kicker, heading).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        group.to_corner(UL, buff=0.55)
        rule = Line(LEFT, RIGHT, color=GOLD, stroke_width=3).set_width(1.2)
        rule.next_to(group, DOWN, aligned_edge=LEFT, buff=0.15)
        self.play(FadeIn(kicker, shift=RIGHT * 0.3), Write(heading), run_time=1.2)
        self.play(Create(rule), run_time=0.4)
        self.header_group = VGroup(group, rule)
        return self.header_group

    def section_card(self):
        """Big centered chapter card shown at the start of each section."""
        num = T(f"{self.number:02d}", 96, GOLD, weight=BOLD)
        title = T(SECTIONS[self.number - 1], 52, weight=BOLD)
        group = VGroup(num, title).arrange(DOWN, buff=0.3)
        self.play(FadeIn(num, scale=0.8), FadeIn(title, shift=UP * 0.3), run_time=0.9)
        self.wait(0.8)
        self.play(FadeOut(group, shift=UP * 0.3), run_time=0.6)

    def clear_body(self, run_time=0.7):
        keep = set(self.header_group.get_family())
        self.play(*[FadeOut(m) for m in self.mobjects if m not in keep], run_time=run_time)

    def clear_all(self, run_time=0.8):
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=run_time)


# ---------------------------------------------------------------------------
# 0. Intro
# ---------------------------------------------------------------------------
class Intro(Base):
    def construct(self):
        # A growth curve drawing itself behind the title
        axes = plain_axes([0, 10, 1], [0, 10, 1], 12, 6).set_opacity(0)
        curve = axes.plot(lambda x: 0.4 * 1.37 ** x, x_range=[0, 10], color=GREEN, stroke_width=5)
        curve.set_stroke(opacity=0.35)
        self.play(Create(curve), run_time=2.5, rate_func=linear)

        title = T("Start Early. Stay Invested.", 64, weight=BOLD)
        subtitle = T("A college student's guide to growing your money", 30, MUTED)
        VGroup(title, subtitle).arrange(DOWN, buff=0.35)
        self.play(Write(title), run_time=1.5)
        self.play(FadeIn(subtitle, shift=UP * 0.2))
        self.wait(1.5)
        self.play(FadeOut(VGroup(title, subtitle, curve)))

        # Agenda
        heading = T("What we'll cover", 40, GOLD, weight=BOLD).to_edge(UP, buff=0.7)
        items = VGroup(
            *[
                VGroup(T(f"{i + 1:02d}", 26, GOLD, weight=BOLD), T(s, 28)).arrange(RIGHT, buff=0.35)
                for i, s in enumerate(SECTIONS)
            ]
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        items.next_to(heading, DOWN, buff=0.5)
        self.play(FadeIn(heading, shift=DOWN * 0.2))
        self.play(LaggedStart(*[FadeIn(i, shift=RIGHT * 0.3) for i in items], lag_ratio=0.15), run_time=2.5)
        self.wait(2)

        disclaimer = T("Educational content only — not financial advice.", 22, MUTED).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(disclaimer))
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects])


# ---------------------------------------------------------------------------
# 1. What is investing?
# ---------------------------------------------------------------------------
class WhatIsInvesting(Section):
    number = 1

    def construct(self):
        self.section_card()
        self.header()

        # Definition
        definition = VGroup(
            T("Investing = putting money into assets today", 34),
            T("that can grow in value or pay you over time.", 34),
        ).arrange(DOWN, buff=0.15)
        definition[0][:9].set_color(GOLD)
        self.play(Write(definition), run_time=2)
        self.wait(1.5)
        self.play(definition.animate.scale(0.75).next_to(self.header_group, DOWN, buff=0.35).set_x(0).to_edge(LEFT, buff=0.6))

        # Saving vs investing
        def compare_card(title, color, lines):
            box = card(5.6, 3.4, stroke=color)
            head = T(title, 32, color, weight=BOLD)
            body = bullet_list(lines, 24, dot_color=color, buff=0.22)
            content = VGroup(head, body).arrange(DOWN, buff=0.35)
            return VGroup(box, fit(content, box))

        saving = compare_card(
            "Saving", BLUE, ["Bank account, very safe", "Easy to access anytime", "Earns little interest"]
        )
        investing = compare_card(
            "Investing", GREEN, ["You own assets", "Higher long-term growth", "Prices go up AND down"]
        )
        pair = VGroup(saving, investing).arrange(RIGHT, buff=0.6).shift(DOWN * 0.7)
        self.play(FadeIn(saving, shift=UP * 0.3))
        self.wait(1)
        self.play(FadeIn(investing, shift=UP * 0.3))
        self.wait(2.5)
        note = T("Saving is for short-term needs. Investing is for long-term goals.", 26, GOLD)
        note.next_to(pair, DOWN, buff=0.35)
        self.play(Write(note))
        self.wait(2)
        self.clear_body()

        # What can you buy?
        q = T("What can you actually buy?", 34, weight=BOLD).next_to(self.header_group, DOWN, buff=0.5).set_x(0)
        self.play(FadeIn(q))

        # Stocks: a slice of a company
        pie = VGroup(
            *[
                AnnularSector(
                    inner_radius=0,
                    outer_radius=0.9,
                    angle=TAU / 8,
                    start_angle=i * TAU / 8,
                    fill_color=GREEN if i == 0 else PANEL,
                    fill_opacity=1,
                    stroke_color=BG,
                    stroke_width=3,
                )
                for i in range(8)
            ]
        )
        pie[0].shift(RIGHT * 0.12 + UP * 0.05)
        stock_icon = pie

        # Bonds: an IOU
        iou = VGroup(
            card(1.9, 1.2, PANEL, stroke=BLUE),
            T("IOU", 30, BLUE, weight=BOLD),
        )
        bond_icon = VGroup(iou, T("+ interest", 20, BLUE).next_to(iou, DOWN, buff=0.12))

        # Funds: a basket of many things
        basket_box = card(2.0, 1.6, PANEL, stroke=PURPLE)
        dots = VGroup(
            *[Dot(radius=0.09, color=[GREEN, BLUE, GOLD, PURPLE][i % 4]) for i in range(20)]
        ).arrange_in_grid(4, 5, buff=0.16)
        dots.move_to(basket_box)
        fund_icon = VGroup(basket_box, dots)

        def asset_column(icon, name, color, desc1, desc2):
            icon.set_height(1.8)
            return VGroup(
                icon,
                T(name, 30, color, weight=BOLD),
                T(desc1, 22, MUTED),
                T(desc2, 22, MUTED),
            ).arrange(DOWN, buff=0.18)

        cols = VGroup(
            asset_column(stock_icon, "Stocks", GREEN, "Own a slice", "of a company"),
            asset_column(bond_icon, "Bonds", BLUE, "Lend money and", "earn interest"),
            asset_column(fund_icon, "Funds", PURPLE, "A basket holding", "many stocks/bonds"),
        ).arrange(RIGHT, buff=1.4)
        cols.next_to(q, DOWN, buff=0.55)
        for c in cols:
            self.play(FadeIn(c, shift=UP * 0.3), run_time=0.8)
            self.wait(1.2)

        stock_line = T(
            "1 share = a tiny piece of a business. If the business grows profits, your piece is worth more.",
            22,
            GOLD,
        ).to_edge(DOWN, buff=0.5)
        self.play(Indicate(cols[0][0], color=GREEN), FadeIn(stock_line))
        self.wait(3)
        self.clear_body()

        # Why not just keep cash? Inflation
        q2 = T("Why not just keep cash?", 34, weight=BOLD).next_to(self.header_group, DOWN, buff=0.5).set_x(0)
        self.play(FadeIn(q2))
        sub = T("Inflation: prices rise ~3% per year, so cash buys less every year.", 26, MUTED)
        sub.next_to(q2, DOWN, buff=0.25)
        self.play(FadeIn(sub))

        year = ValueTracker(0)
        bill = card(4.4, 2.2, "#14532D", stroke=GREEN).shift(DOWN * 1.2)
        bill_label = always_redraw(
            lambda: T(money(1000 / 1.03 ** year.get_value()), 56, INK, weight=BOLD).move_to(bill)
        )
        bill_caption = always_redraw(
            lambda: T(
                f"What $1,000 buys after {year.get_value():.0f} years",
                24,
                MUTED,
            ).next_to(bill, DOWN, buff=0.3)
        )
        self.play(FadeIn(bill), FadeIn(bill_label), FadeIn(bill_caption))
        self.wait(0.5)
        self.play(
            year.animate.set_value(20),
            bill.animate.scale(0.72).set_fill("#3F1D1D").set_stroke(RED),
            run_time=4,
            rate_func=linear,
        )
        self.wait(0.5)
        punch = T("Cash under the mattress quietly loses ~45% of its power in 20 years.", 26, RED)
        punch.to_edge(DOWN, buff=0.4)
        self.play(Write(punch))
        self.wait(2.5)
        self.clear_all()


# ---------------------------------------------------------------------------
# 2. Index funds & ETFs
# ---------------------------------------------------------------------------
class IndexFunds(Section):
    number = 2

    def construct(self):
        self.section_card()
        self.header()

        # One stock vs. the whole market
        left_title = T("Picking 1 stock", 30, RED, weight=BOLD)
        right_title = T("An index fund", 30, GREEN, weight=BOLD)

        one = Square(1.2, fill_color=RED, fill_opacity=0.85, stroke_width=0)
        one_lbl = T("1 company", 22, MUTED).next_to(one, DOWN, buff=0.2)
        left = VGroup(left_title, VGroup(one, one_lbl)).arrange(DOWN, buff=0.5)

        grid = VGroup(
            *[Square(0.14, fill_color=GREEN, fill_opacity=0.85, stroke_width=0) for _ in range(500)]
        ).arrange_in_grid(20, 25, buff=0.035)
        grid_lbl = T("500 companies", 22, MUTED).next_to(grid, DOWN, buff=0.2)
        right = VGroup(right_title, VGroup(grid, grid_lbl)).arrange(DOWN, buff=0.5)

        VGroup(left, right).arrange(RIGHT, buff=2.8).shift(DOWN * 0.3)
        self.play(FadeIn(left_title), GrowFromCenter(one), FadeIn(one_lbl))
        self.wait(0.5)
        self.play(
            FadeIn(right_title),
            LaggedStart(*[FadeIn(s, scale=0.5) for s in grid], lag_ratio=0.004),
            FadeIn(grid_lbl),
            run_time=2.5,
        )
        self.wait(1)

        # Some companies fail; one bad pick hurts a lot, one bad company in 500 barely matters
        import random

        random.seed(7)
        losers = random.sample(range(500), 60)
        self.play(
            one.animate.set_fill("#5B1A1A"),
            *[grid[i].animate.set_fill(RED) for i in losers],
            run_time=1.2,
        )
        l_note = T("It drops 60%?\nYou lose 60%.", 24, RED).next_to(one_lbl, DOWN, buff=0.4)
        r_note = T("A few companies stumble?\nThe winners carry the rest.", 24, GREEN).next_to(
            grid_lbl, DOWN, buff=0.4
        )
        self.play(FadeIn(l_note), FadeIn(r_note))
        self.wait(3)
        self.clear_body()

        # What is an index fund
        what = VGroup(
            T("An index fund buys every company in an index", 32),
            T("(like the 500 largest U.S. companies in the S&P 500)", 26, MUTED),
            T("in a single, low-cost purchase.", 32),
        ).arrange(DOWN, buff=0.2)
        what.next_to(self.header_group, DOWN, buff=0.6).set_x(0)
        self.play(FadeIn(what, shift=UP * 0.2), run_time=1.2)
        perks = bullet_list(
            [
                "Instant diversification across hundreds of companies",
                "Very low fees (often under 0.10% per year)",
                "No stock-picking skill or research required",
                "You match the market instead of guessing",
            ],
            28,
        ).next_to(what, DOWN, buff=0.6)
        self.play(LaggedStart(*[FadeIn(p, shift=RIGHT * 0.3) for p in perks], lag_ratio=0.4), run_time=3)
        self.wait(2.5)
        self.clear_body()

        # Even professionals struggle to beat the index
        claim = T("Even the professionals struggle to beat the index", 32, weight=BOLD)
        claim.next_to(self.header_group, DOWN, buff=0.6).set_x(0)
        self.play(FadeIn(claim))
        people = VGroup()
        for i in range(10):
            head = Circle(0.22, fill_opacity=1, stroke_width=0)
            body = RoundedRectangle(corner_radius=0.2, width=0.6, height=0.7, fill_opacity=1, stroke_width=0)
            body.next_to(head, DOWN, buff=0.06)
            people.add(VGroup(head, body).set_fill(MUTED))
        people.arrange(RIGHT, buff=0.35).next_to(claim, DOWN, buff=0.8)
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.2) for p in people], lag_ratio=0.08))
        self.play(
            *[people[i].animate.set_fill(RED) for i in range(9)],
            people[9].animate.set_fill(GREEN),
            run_time=1.2,
        )
        stat = T("About 9 in 10 actively managed U.S. large-cap funds", 28)
        stat2 = T("trailed the S&P 500 over 15 years.", 28)
        stats = VGroup(stat, stat2).arrange(DOWN, buff=0.15).next_to(people, DOWN, buff=0.6)
        stat[5:10].set_color(RED)  # "9 in 10" (Text drops spaces)
        self.play(Write(stats), run_time=1.8)
        self.add(source_note("Source: S&P Dow Jones Indices, SPIVA U.S. Scorecard"))
        self.wait(3)
        self.clear_body()

        # ETF vs index mutual fund
        def fund_card(title, color, lines):
            box = card(6.0, 3.3, stroke=color)
            head = T(title, 28, color, weight=BOLD)
            body = bullet_list(lines, 23, dot_color=color, buff=0.2)
            return VGroup(box, fit(VGroup(head, body).arrange(DOWN, buff=0.3), box))

        etf = fund_card(
            "ETF (Exchange-Traded Fund)",
            GREEN,
            ["Trades like a stock, all day", "Low or no minimum to start", "Very tax-efficient", "Fractional shares at many brokers"],
        )
        mf = fund_card(
            "Index Mutual Fund",
            BLUE,
            ["Priced once per day", "Some have minimums", "Easy automatic investing", "Same idea: own the whole index"],
        )
        VGroup(etf, mf).arrange(RIGHT, buff=0.5).next_to(self.header_group, DOWN, buff=0.5).set_x(0)
        self.play(FadeIn(etf, shift=UP * 0.3))
        self.wait(1.5)
        self.play(FadeIn(mf, shift=UP * 0.3))
        self.wait(1.5)
        bottom = T("Both are great. What matters most: broad diversification + low fees.", 26, GOLD)
        bottom.next_to(VGroup(etf, mf), DOWN, buff=0.45)
        self.play(Write(bottom))
        self.wait(2.5)
        self.clear_body()

        # Fees matter: 0.03% vs 1.00%
        title = T("Why low fees matter: $200/month from age 22 to 65", 28)
        title.next_to(self.header_group, DOWN, buff=0.35).set_x(0)
        self.play(FadeIn(title))
        axes = plain_axes([0, 43, 10], [0, 700000, 200000], 9.0, 4.2).next_to(title, DOWN, buff=0.4).shift(LEFT * 0.8)
        labels = label_axes(
            axes,
            [0, 10, 20, 30, 40],
            lambda x: f"{22 + x}",
            [200000, 400000, 600000],
            lambda y: f"${y // 1000:.0f}k",
        )
        self.play(Create(axes), FadeIn(labels))

        def growth(rate):
            mr = (1 + rate) ** (1 / 12) - 1
            return lambda yrs: monthly_balance(200, int(yrs * 12), int(yrs * 12), mr)

        low_fee = axes.plot(growth(0.0697), x_range=[0, 43, 0.25], color=GREEN, stroke_width=5)
        high_fee = axes.plot(growth(0.06), x_range=[0, 43, 0.25], color=RED, stroke_width=5)
        self.play(Create(low_fee), Create(high_fee), run_time=3, rate_func=linear)

        low_end, high_end = growth(0.0697)(43), growth(0.06)(43)
        low_lbl = VGroup(Line(ORIGIN, RIGHT * 0.5, color=GREEN, stroke_width=5), T(f"0.03% fee: {money(low_end)}", 24, GREEN))
        high_lbl = VGroup(Line(ORIGIN, RIGHT * 0.5, color=RED, stroke_width=5), T(f"1.00% fee: {money(high_end)}", 24, RED))
        for lbl in (low_lbl, high_lbl):
            lbl.arrange(RIGHT, buff=0.2)
        VGroup(low_lbl, high_lbl).arrange(DOWN, aligned_edge=LEFT, buff=0.2).next_to(axes.c2p(2, 650000), DR, buff=0)
        gap = DoubleArrow(axes.c2p(43.6, high_end), axes.c2p(43.6, low_end), color=GOLD, buff=0, stroke_width=4, tip_length=0.18)
        gap_lbl = T(f"~{money(low_end - high_end)}\nlost to fees", 22, GOLD).next_to(gap, RIGHT, buff=0.15)
        self.play(FadeIn(low_lbl), FadeIn(high_lbl))
        self.play(GrowFromCenter(gap), FadeIn(gap_lbl))
        self.add(source_note("Assumes 7% average annual return before fees. Illustrative only."))
        self.wait(3.5)
        self.clear_body()

        # Common broad index fund types
        kinds = T("Popular broad, low-cost choices", 32, weight=BOLD).next_to(self.header_group, DOWN, buff=0.6).set_x(0)
        self.play(FadeIn(kinds))
        tiles = VGroup()
        for name, desc, color in [
            ("Total U.S. Stock Market", "Nearly every public U.S. company", GREEN),
            ("S&P 500", "500 of the largest U.S. companies", BLUE),
            ("Total International", "Companies outside the U.S.", PURPLE),
            ("Target-Date Fund", "All-in-one mix that adjusts with age", GOLD),
        ]:
            box = card(5.8, 1.35, stroke=color)
            txt = VGroup(T(name, 26, color, weight=BOLD), T(desc, 20, MUTED)).arrange(DOWN, buff=0.12)
            tiles.add(VGroup(box, fit(txt, box)))
        tiles.arrange_in_grid(2, 2, buff=0.4).next_to(kinds, DOWN, buff=0.5)
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.2) for t in tiles], lag_ratio=0.3), run_time=2.5)
        tip = T("Tip: check the expense ratio — look for roughly 0.10% or less.", 24, GOLD).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(tip))
        self.wait(3)
        self.clear_all()


# ---------------------------------------------------------------------------
# 3. Compounding
# ---------------------------------------------------------------------------
class Compounding(Section):
    number = 3

    def construct(self):
        self.section_card()
        self.header()

        idea = VGroup(
            T("You earn returns on your money...", 32),
            T("...and then returns on your returns.", 32, GREEN),
        ).arrange(DOWN, buff=0.2).next_to(self.header_group, DOWN, buff=0.45).set_x(0)
        self.play(FadeIn(idea[0]))
        self.play(FadeIn(idea[1]))
        self.wait(1)

        # Stacked bars: principal (blue) + growth (green), $1,000 at 7%
        base_y = -2.6
        scale = 2.2 / 1000  # units per dollar
        bars = VGroup()
        for i, yr in enumerate([0, 1, 2, 3]):
            value = 1000 * 1.07 ** yr
            principal = Rectangle(width=1.3, height=1000 * scale, fill_color=BLUE, fill_opacity=0.9, stroke_width=0)
            growth_h = max((value - 1000) * scale, 0.001)
            growth = Rectangle(width=1.3, height=growth_h, fill_color=GREEN, fill_opacity=0.95, stroke_width=0)
            principal.move_to([-4.6 + i * 2.3, base_y + principal.height / 2, 0])
            growth.next_to(principal, UP, buff=0)
            value_lbl = T(f"${value:,.2f}", 22, INK, weight=BOLD).next_to(growth, UP, buff=0.12)
            year_lbl = T(f"Year {yr}", 22, MUTED).next_to(principal, DOWN, buff=0.15)
            gain = T(f"+${value - 1000 * 1.07 ** (yr - 1):,.2f}" if yr else "start", 20, GREEN if yr else MUTED)
            gain.next_to(value_lbl, UP, buff=0.08)
            bars.add(VGroup(principal, growth, value_lbl, year_lbl, gain))
        for b in bars:
            self.play(FadeIn(b, shift=UP * 0.2), run_time=0.8)
            self.wait(0.4)
        legend = VGroup(
            VGroup(Square(0.25, fill_color=BLUE, fill_opacity=1, stroke_width=0), T("Your $1,000", 20, MUTED)).arrange(RIGHT, buff=0.15),
            VGroup(Square(0.25, fill_color=GREEN, fill_opacity=1, stroke_width=0), T("Growth at 7%/yr", 20, MUTED)).arrange(RIGHT, buff=0.15),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).to_edge(RIGHT, buff=0.7).shift(DOWN * 0.6)
        self.play(FadeIn(legend))
        note = T("Each year's gain is bigger than the last: $70 → $74.90 → $80.14", 24, GOLD).to_edge(DOWN, buff=0.25)
        self.play(FadeIn(note))
        self.wait(3)
        self.clear_body()

        # 40-year curve with doubling markers
        title = T("$1,000 invested once, left alone for 40 years", 28).next_to(self.header_group, DOWN, buff=0.35).set_x(0)
        self.play(FadeIn(title))
        axes = plain_axes([0, 40, 10], [0, 16000, 4000], 10, 4.4).next_to(title, DOWN, buff=0.4)
        labels = label_axes(
            axes,
            [0, 10, 20, 30, 40],
            lambda x: f"Yr {x}",
            [4000, 8000, 12000, 16000],
            lambda y: f"${y // 1000:.0f}k",
        )
        self.play(Create(axes), FadeIn(labels))

        t = ValueTracker(0)
        f = lambda x: 1000 * 1.07 ** x
        curve = always_redraw(
            lambda: axes.plot(f, x_range=[0, max(t.get_value(), 0.01)], color=GREEN, stroke_width=5)
        )
        dot = always_redraw(lambda: Dot(axes.c2p(t.get_value(), f(t.get_value())), color=GOLD, radius=0.08))
        counter = always_redraw(
            lambda: T(money(f(t.get_value())), 30, GOLD, weight=BOLD).next_to(dot, UL, buff=0.1)
        )
        self.add(curve, dot, counter)
        self.play(t.animate.set_value(40), run_time=6, rate_func=linear)
        self.wait(0.5)

        doubles = VGroup()
        for n in range(1, 4):
            x = n * 72 / 7
            doubles.add(
                DashedLine(axes.c2p(x, 0), axes.c2p(x, f(x)), color=MUTED, stroke_width=2),
                T(f"{2 ** n}x", 20, MUTED).next_to(axes.c2p(x, f(x)), DR, buff=0.08),
            )
        rule = VGroup(
            T("Rule of 72", 28, GOLD, weight=BOLD),
            T("72 ÷ 7% ≈ 10 years to double", 24),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        rule.next_to(axes.c2p(2, 14500), DR, buff=0).shift(DOWN * 0.1)
        self.play(LaggedStart(*[Create(d) for d in doubles], lag_ratio=0.2), FadeIn(rule))
        self.wait(2.5)

        # Highlight the last decade
        last = Polygon(
            axes.c2p(30, 0), *[axes.c2p(x, f(x)) for x in [30 + i * 0.5 for i in range(21)]], axes.c2p(40, 0),
            fill_color=GOLD, fill_opacity=0.25, stroke_width=0,
        )
        final_note = VGroup(
            T("About half the final value appears", 26, GOLD),
            T("in the LAST 10 years.", 26, GOLD),
            T("Time is your biggest advantage —", 24, INK),
            T("and you have more of it than anyone.", 24, INK),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        final_note[2].shift(DOWN * 0.15)
        final_note[3].shift(DOWN * 0.15)
        final_note.move_to(rule, aligned_edge=UL)
        self.play(FadeIn(last), FadeOut(rule))
        self.play(FadeIn(final_note))
        self.wait(3.5)
        self.clear_all()


# ---------------------------------------------------------------------------
# 4. Start early
# ---------------------------------------------------------------------------
class StartEarly(Section):
    number = 4

    def construct(self):
        self.section_card()
        self.header()

        def person(name, color, lines):
            avatar = VGroup(
                Circle(0.32, fill_color=color, fill_opacity=1, stroke_width=0),
                RoundedRectangle(corner_radius=0.3, width=0.9, height=0.9, fill_color=color, fill_opacity=1, stroke_width=0),
            ).arrange(DOWN, buff=0.06)
            info = VGroup(T(name, 32, color, weight=BOLD), *[T(l, 22, INK) for l in lines]).arrange(
                DOWN, aligned_edge=LEFT, buff=0.12
            )
            return VGroup(avatar, info).arrange(RIGHT, buff=0.35)

        emma = person("Early Emma", GREEN, ["$200/month from age 22 to 32", "Then stops forever", "Total put in: $24,000"])
        liam = person("Late Liam", BLUE, ["$200/month from age 32 to 65", "Never misses a month", "Total put in: $79,200"])
        VGroup(emma, liam).arrange(RIGHT, buff=1.4).next_to(self.header_group, DOWN, buff=0.7).set_x(0)
        self.play(FadeIn(emma, shift=UP * 0.3))
        self.wait(1.5)
        self.play(FadeIn(liam, shift=UP * 0.3))
        self.wait(1)
        q = T("Both earn 7% a year. Who has more at 65?", 30, GOLD).shift(DOWN * 1.6)
        self.play(Write(q))
        self.wait(2.5)
        self.play(FadeOut(q), VGroup(emma, liam).animate.scale(0.6).next_to(self.header_group, DOWN, buff=0.25).set_x(0))

        axes = plain_axes([22, 65, 5], [0, 350000, 100000], 9.5, 3.9).to_edge(DOWN, buff=0.75).shift(LEFT * 0.3)
        labels = label_axes(
            axes,
            [22, 32, 42, 52, 65],
            lambda x: f"Age {x}",
            [100000, 200000, 300000],
            lambda y: f"${y // 1000:.0f}k",
        )
        self.play(Create(axes), FadeIn(labels))

        emma_f = lambda age: monthly_balance(200, 120, int((age - 22) * 12))
        liam_f = lambda age: monthly_balance(200, 396, int(max(age - 32, 0) * 12))
        emma_curve = axes.plot(emma_f, x_range=[22, 65, 0.25], color=GREEN, stroke_width=5)
        liam_curve = axes.plot(liam_f, x_range=[32, 65, 0.25], color=BLUE, stroke_width=5)
        stop = DashedLine(axes.c2p(32, 0), axes.c2p(32, 200000), color=MUTED, stroke_width=2)
        stop_lbl = T("Emma stops,\nLiam starts", 18, MUTED).next_to(axes.c2p(32, 200000), RIGHT, buff=0.1)
        self.play(Create(emma_curve), run_time=4, rate_func=linear)
        self.play(Create(stop), FadeIn(stop_lbl))
        self.play(Create(liam_curve), run_time=3, rate_func=linear)

        e_end, l_end = emma_f(65), liam_f(65)
        e_lbl = T(money(e_end), 26, GREEN, weight=BOLD).next_to(axes.c2p(65, e_end), RIGHT, buff=0.15).shift(UP * 0.15)
        l_lbl = T(money(l_end), 26, BLUE, weight=BOLD).next_to(axes.c2p(65, l_end), RIGHT, buff=0.15).shift(DOWN * 0.15)
        self.play(FadeIn(e_lbl), FadeIn(l_lbl))
        self.wait(1)
        verdict = VGroup(
            T("Emma put in 3x less money...", 26, GOLD),
            T("and still ends up with more.", 26, GOLD),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        verdict.next_to(axes.c2p(23, 340000), DR, buff=0)
        self.play(Write(verdict))
        self.add(source_note("7% avg annual return, monthly contributions. Illustrative."))
        self.wait(3.5)
        self.clear_body()

        # Cost of waiting: start at 22 vs 32 vs 42
        title = T("$200/month until age 65 — what does waiting cost?", 30).next_to(self.header_group, DOWN, buff=0.4).set_x(0)
        self.play(FadeIn(title))
        base_y = -2.75
        max_h = 2.9
        top = monthly_balance(200, 43 * 12, 43 * 12)
        bars = VGroup()
        for i, start in enumerate([22, 32, 42]):
            n = (65 - start) * 12
            total = monthly_balance(200, n, n)
            contributed = 200 * n
            c_h = contributed / top * max_h
            g_h = (total - contributed) / top * max_h
            c_bar = Rectangle(width=1.8, height=c_h, fill_color=BLUE, fill_opacity=0.9, stroke_width=0)
            g_bar = Rectangle(width=1.8, height=g_h, fill_color=GREEN, fill_opacity=0.95, stroke_width=0)
            c_bar.move_to([-3.5 + i * 3.5, base_y + c_h / 2, 0])
            g_bar.next_to(c_bar, UP, buff=0)
            total_lbl = T(money(total), 28, INK, weight=BOLD).next_to(g_bar, UP, buff=0.12)
            start_lbl = T(f"Start at {start}", 24, INK).next_to(c_bar, DOWN, buff=0.15)
            put_in = T(f"put in {money(contributed)}", 20, BLUE).next_to(start_lbl, DOWN, buff=0.1)
            bars.add(VGroup(c_bar, g_bar, total_lbl, start_lbl, put_in))
        for b in bars:
            self.play(GrowFromEdge(b[0], DOWN), run_time=0.6)
            self.play(GrowFromEdge(b[1], DOWN), FadeIn(b[2:]), run_time=1)
        legend = VGroup(
            VGroup(Square(0.25, fill_color=BLUE, fill_opacity=1, stroke_width=0), T("Money you put in", 20, MUTED)).arrange(RIGHT, buff=0.15),
            VGroup(Square(0.25, fill_color=GREEN, fill_opacity=1, stroke_width=0), T("Growth from compounding", 20, MUTED)).arrange(RIGHT, buff=0.15),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_edge(RIGHT, buff=0.4).shift(DOWN * 0.4)
        self.play(FadeIn(legend))
        msg = T("Waiting 10 years cuts the result by more than half.", 26, GOLD).next_to(title, DOWN, buff=0.25)
        self.play(Write(msg))
        self.wait(3.5)
        self.clear_body()

        # Start small
        small = VGroup(
            T("Can't spare $200? Start with $25 or $50.", 34, weight=BOLD),
            T(f"$50/month from age 20 to 65 at 7% ≈ {money(monthly_balance(50, 540, 540))}", 30, GREEN),
            T("(you'd only put in $27,000)", 24, MUTED),
            T("The habit matters more than the amount. Increase it as your income grows.", 26, GOLD),
        ).arrange(DOWN, buff=0.4)
        for line in small:
            self.play(FadeIn(line, shift=UP * 0.2), run_time=0.9)
            self.wait(0.8)
        self.wait(2.5)
        self.clear_all()


# ---------------------------------------------------------------------------
# 5. Recurring investing / dollar-cost averaging
# ---------------------------------------------------------------------------
class RecurringInvesting(Section):
    number = 5

    def construct(self):
        self.section_card()
        self.header()

        intro = VGroup(
            T("Dollar-cost averaging: invest the same amount on a schedule,", 28),
            T("no matter what the market is doing.", 28),
        ).arrange(DOWN, buff=0.12).next_to(self.header_group, DOWN, buff=0.4).set_x(0)
        self.play(FadeIn(intro))

        prices = [10, 8, 5, 7, 9, 11]
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        axes = plain_axes([0, 5, 1], [0, 12, 4], 7, 1.8).to_edge(LEFT, buff=1.3)
        axes.set_y(-0.4)
        p_labels = label_axes(axes, range(6), lambda i: months[i], [4, 8, 12], lambda y: f"${y}", size=18)
        price_line = VMobject(color=GOLD, stroke_width=4).set_points_as_corners([axes.c2p(i, p) for i, p in enumerate(prices)])
        price_dots = VGroup(*[Dot(axes.c2p(i, p), color=GOLD, radius=0.07) for i, p in enumerate(prices)])
        price_title = T("Share price", 22, GOLD).next_to(axes, UP, buff=0.15).align_to(axes, LEFT)
        self.play(Create(axes), FadeIn(p_labels), FadeIn(price_title))
        self.play(Create(price_line), FadeIn(price_dots), run_time=2)

        # Shares bought each month with $100
        share_axes_origin = axes.get_corner(DL) + DOWN * 2.45
        share_bars = VGroup()
        for i, p in enumerate(prices):
            shares = 100 / p
            bar = Rectangle(width=0.55, height=shares * 0.06, fill_color=GREEN, fill_opacity=0.9, stroke_width=0)
            x = axes.c2p(i, 0)[0]
            bar.move_to([x, share_axes_origin[1] + bar.height / 2, 0])
            lbl = T(f"{shares:.1f}", 18, GREEN).next_to(bar, UP, buff=0.06)
            share_bars.add(VGroup(bar, lbl))
        shares_title = T("Shares bought with $100 each month", 22, GREEN).next_to(p_labels, DOWN, buff=0.25).align_to(axes, LEFT)
        self.play(FadeIn(shares_title))
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in share_bars], lag_ratio=0.25), run_time=2.5)
        self.play(Indicate(share_bars[2], color=GOLD), Indicate(price_dots[2], color=RED))

        total_shares = sum(100 / p for p in prices)
        summary_box = card(4.6, 3.3, stroke=GREEN).to_edge(RIGHT, buff=0.5).set_y(-0.95)
        summary = VGroup(
            T("After 6 months", 26, GREEN, weight=BOLD),
            T("Invested: $600", 24),
            T(f"Shares owned: {total_shares:.1f}", 24),
            T(f"Avg price paid: ${600 / total_shares:.2f}", 24, GREEN),
            T(f"Avg market price: ${sum(prices) / 6:.2f}", 24, MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to(summary_box)
        self.play(FadeIn(summary_box), LaggedStart(*[FadeIn(s) for s in summary], lag_ratio=0.3), run_time=2)
        dip = VGroup(T("When prices drop, your", 24, GOLD), T("$100 buys MORE shares.", 24, GOLD)).arrange(DOWN, buff=0.08)
        dip.next_to(summary_box, DOWN, buff=0.3)
        self.play(Write(dip))
        self.wait(3.5)
        self.clear_body()

        # Why automate
        why = T("Why automate it?", 34, weight=BOLD).next_to(self.header_group, DOWN, buff=0.5).set_x(0)
        self.play(FadeIn(why))
        reasons = bullet_list(
            [
                "Removes emotion: no panic-selling, no FOMO buying",
                "No need to predict the market (nobody can, reliably)",
                "Builds the habit: pay yourself first, every payday",
                "Takes 10 minutes to set up at most brokerages",
            ],
            28,
        ).next_to(why, DOWN, buff=0.5)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.3) for r in reasons], lag_ratio=0.5), run_time=3)
        self.wait(3)
        self.clear_body()

        # Time in the market vs timing the market
        tt = T("Time in the market beats timing the market", 32, weight=BOLD).next_to(self.header_group, DOWN, buff=0.45).set_x(0)
        sub = T("$10,000 in the S&P 500, 2005–2024", 24, MUTED).next_to(tt, DOWN, buff=0.15)
        self.play(FadeIn(tt), FadeIn(sub))
        data = [("Stayed invested", 71750, GREEN), ("Missed the 10 best days", 32871, RED)]
        base_y = -2.9
        bars = VGroup()
        for i, (name, val, color) in enumerate(data):
            h = val / 71750 * 3.6
            bar = Rectangle(width=2.6, height=h, fill_color=color, fill_opacity=0.9, stroke_width=0)
            bar.move_to([-4.6 + i * 3.6, base_y + h / 2, 0])
            val_lbl = T(f"~{money(val)}", 30, INK, weight=BOLD).next_to(bar, UP, buff=0.12)
            name_lbl = T(name, 22, MUTED).next_to(bar, DOWN, buff=0.15)
            bars.add(VGroup(bar, val_lbl, name_lbl))
        for b in bars:
            self.play(GrowFromEdge(b[0], DOWN), FadeIn(b[1:]), run_time=1)
        fact = VGroup(
            T("Many of the best days come", 26, GOLD),
            T("right after the worst ones.", 26, GOLD),
            T("Selling in a panic often means", 24, INK),
            T("missing the rebound.", 24, INK),
        ).arrange(DOWN, buff=0.12, aligned_edge=LEFT).to_edge(RIGHT, buff=0.5).shift(DOWN * 0.6)
        self.play(FadeIn(fact))
        self.add(source_note("Source: J.P. Morgan Asset Management analysis of S&P 500 returns (approx.)"))
        self.wait(4)
        self.clear_all()


# ---------------------------------------------------------------------------
# 6. Taxes: hold for the long term
# ---------------------------------------------------------------------------
class TaxesLongTerm(Section):
    number = 6

    def construct(self):
        self.section_card()
        self.header()

        what = VGroup(
            T("Capital gains = profit when you sell an investment for more than you paid.", 26),
            T("The IRS taxes that profit — but HOW LONG you held it changes the rate.", 26, GOLD),
        ).arrange(DOWN, buff=0.18).next_to(self.header_group, DOWN, buff=0.4).set_x(0)
        self.play(FadeIn(what[0]))
        self.wait(1)
        self.play(FadeIn(what[1]))

        # Timeline
        line = NumberLine(x_range=[0, 2, 1], length=10, color=MUTED, include_numbers=False, include_tip=False)
        line.shift(DOWN * 0.3)
        buy = VGroup(Dot(line.n2p(0), color=INK), T("Buy", 22).next_to(line.n2p(0), UP, buff=0.2))
        one_year = VGroup(
            Line(line.n2p(1) + UP * 0.35, line.n2p(1) + DOWN * 0.35, color=GOLD, stroke_width=4),
            T("1 year", 22, GOLD).next_to(line.n2p(1), UP, buff=0.45),
        )
        short = Line(line.n2p(0), line.n2p(1), color=RED, stroke_width=10)
        long = Line(line.n2p(1), line.n2p(2), color=GREEN, stroke_width=10)
        self.play(Create(line), FadeIn(buy))
        self.play(FadeIn(one_year))
        self.play(Create(short))
        st = VGroup(
            T("Short-term gain", 26, RED, weight=BOLD),
            T("Sold within 1 year", 20, MUTED),
            T("Taxed like your paycheck: 10%–37%", 22),
        ).arrange(DOWN, buff=0.1).next_to(short, DOWN, buff=0.35)
        self.play(FadeIn(st))
        self.play(Create(long))
        lt = VGroup(
            T("Long-term gain", 26, GREEN, weight=BOLD),
            T("Held more than 1 year", 20, MUTED),
            T("Lower rates: 0%, 15%, or 20%", 22),
        ).arrange(DOWN, buff=0.1).next_to(long, DOWN, buff=0.35)
        self.play(FadeIn(lt))
        self.wait(3)
        self.clear_body()

        # Example: $10,000 profit
        ex = T("Example: you sell with a $10,000 profit", 30, weight=BOLD).next_to(self.header_group, DOWN, buff=0.45).set_x(0)
        self.play(FadeIn(ex))
        cases = [
            ("Short-term\n(22% bracket)", 2200, RED),
            ("Long-term\n(15% rate)", 1500, GOLD),
            ("Long-term, low income\n(0% rate)", 0, GREEN),
        ]
        base_y = -2.7
        scale = 3.3 / 10000
        bars = VGroup()
        for i, (name, tax, color) in enumerate(cases):
            keep = 10000 - tax
            k_bar = Rectangle(width=2.4, height=keep * scale, fill_color=color, fill_opacity=0.9, stroke_width=0)
            k_bar.move_to([-4 + i * 4, base_y + k_bar.height / 2, 0])
            group = VGroup(k_bar)
            if tax:
                t_bar = Rectangle(width=2.4, height=tax * scale, fill_color=MUTED, fill_opacity=0.35, stroke_color=MUTED, stroke_width=1)
                t_bar.next_to(k_bar, UP, buff=0)
                t_lbl = T(f"tax {money(tax)}", 18, INK).move_to(t_bar)
                group.add(t_bar, t_lbl)
            keep_lbl = VGroup(T("You keep", 20, INK), T(money(keep), 28, INK, weight=BOLD)).arrange(DOWN, buff=0.08)
            keep_lbl.move_to(k_bar)
            name_lbl = lines(name).next_to(k_bar, DOWN, buff=0.15)
            group.add(keep_lbl, name_lbl)
            bars.add(group)
        for b in bars:
            self.play(GrowFromEdge(b[0], DOWN), FadeIn(b[1:]), run_time=0.9)
            self.wait(0.6)
        student = T("Many students have low taxable income, so the 0% long-term rate can apply.", 22, GOLD)
        student.next_to(ex, DOWN, buff=0.2)
        self.play(FadeIn(student))
        self.add(source_note("Simplified U.S. federal example. State taxes and exact brackets vary."))
        self.wait(3.5)
        self.clear_body()

        # Buy and hold avoids tax drag
        drag = VGroup(
            T("Every sale can trigger a tax bill.", 30, weight=BOLD),
            T("If you don't sell, you don't owe capital gains tax yet —", 26),
            T("so 100% of your money keeps compounding.", 26, GREEN),
            T("Frequent trading = more taxes + more mistakes.", 26, RED),
        ).arrange(DOWN, buff=0.3).next_to(self.header_group, DOWN, buff=0.7).set_x(0)
        self.play(LaggedStart(*[FadeIn(d, shift=UP * 0.2) for d in drag], lag_ratio=0.5), run_time=3)
        self.wait(3)
        self.clear_body()

        # Tax-advantaged accounts
        accts = T("Use tax-advantaged accounts first", 32, weight=BOLD).next_to(self.header_group, DOWN, buff=0.45).set_x(0)
        self.play(FadeIn(accts))

        def acct_card(title, color, items, w=6.4, h=3.6):
            box = card(w, h, stroke=color)
            head = T(title, 30, color, weight=BOLD)
            body = bullet_list(items, 21, dot_color=color, buff=0.18)
            return VGroup(box, fit(VGroup(head, body).arrange(DOWN, buff=0.3), box))

        roth = acct_card(
            "Roth IRA",
            GREEN,
            [
                "Contribute money you've already paid tax on",
                "Grows tax-free; withdraw tax-free in retirement",
                "Requires earned income (part-time jobs count!)",
                "2026 limit: $7,500 per year",
                "Ideal for students: your tax rate is low now",
            ],
        )
        k401 = acct_card(
            "401(k) with employer match",
            BLUE,
            [
                "Retirement account offered by many employers",
                "Employer match = free money",
                "Often 50–100% of what you put in, up to a limit",
                "Contribute at least enough to get the full match",
            ],
        )
        VGroup(roth, k401).arrange(RIGHT, buff=0.35).next_to(accts, DOWN, buff=0.4)
        self.play(FadeIn(roth, shift=UP * 0.3))
        self.wait(2.5)
        self.play(FadeIn(k401, shift=UP * 0.3))
        self.add(source_note("Contribution limits change yearly; check IRS.gov for current rules."))
        self.wait(4)
        self.clear_all()


# ---------------------------------------------------------------------------
# 7. Making decisions
# ---------------------------------------------------------------------------
class MakingDecisions(Section):
    number = 7

    def construct(self):
        self.section_card()
        self.header()

        # Order of operations staircase
        sub = T("A simple order of operations", 30, weight=BOLD).next_to(self.header_group, DOWN, buff=0.35).set_x(0)
        self.play(FadeIn(sub))
        steps = [
            ("Emergency fund", "Start with $1,000, grow to 3–6 months of expenses", BLUE),
            ("Kill high-interest debt", "Credit cards charge ~20%+ — paying them off is a guaranteed return", RED),
            ("Get the 401(k) match", "If your job offers one, it's free money", PURPLE),
            ("Open a Roth IRA", "Buy broad, low-cost index funds or ETFs", GREEN),
            ("Invest more", "Regular brokerage account, same simple funds", GOLD),
        ]
        rows = VGroup()
        for i, (name, desc, color) in enumerate(steps):
            badge = VGroup(
                Circle(0.3, fill_color=color, fill_opacity=1, stroke_width=0),
                T(str(i + 1), 26, BG, weight=BOLD),
            )
            txt = VGroup(T(name, 26, color, weight=BOLD), T(desc, 20, MUTED)).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
            rows.add(VGroup(badge, txt).arrange(RIGHT, buff=0.3))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.22).next_to(sub, DOWN, buff=0.35)
        for i, r in enumerate(rows):
            r.shift(RIGHT * i * 0.55)
        for r in rows:
            self.play(FadeIn(r, shift=RIGHT * 0.3), run_time=0.7)
            self.wait(1.3)
        self.wait(2)
        self.clear_body()

        # Asset allocation by age
        aa = T("How much in stocks vs. bonds?", 30, weight=BOLD).next_to(self.header_group, DOWN, buff=0.35).set_x(0)
        self.play(FadeIn(aa))

        def pie(stock_pct, label):
            s_angle = TAU * stock_pct / 100
            stocks = AnnularSector(inner_radius=0.6, outer_radius=1.3, angle=s_angle, start_angle=PI / 2, fill_color=GREEN, fill_opacity=1, stroke_width=0)
            bonds = AnnularSector(inner_radius=0.6, outer_radius=1.3, angle=TAU - s_angle, start_angle=PI / 2 + s_angle, fill_color=BLUE, fill_opacity=1, stroke_width=0)
            center = T(f"{stock_pct}/{100 - stock_pct}", 26, INK, weight=BOLD)
            cap = T(label, 22, MUTED).next_to(VGroup(stocks, bonds), DOWN, buff=0.25)
            return VGroup(stocks, bonds, center, cap)

        pies = VGroup(pie(90, "In your 20s"), pie(75, "Around 45"), pie(55, "Near retirement")).arrange(RIGHT, buff=1.2)
        pies.next_to(aa, DOWN, buff=0.5)
        legend = VGroup(
            VGroup(Square(0.25, fill_color=GREEN, fill_opacity=1, stroke_width=0), T("Stocks (growth)", 20, MUTED)).arrange(RIGHT, buff=0.15),
            VGroup(Square(0.25, fill_color=BLUE, fill_opacity=1, stroke_width=0), T("Bonds (stability)", 20, MUTED)).arrange(RIGHT, buff=0.15),
        ).arrange(RIGHT, buff=0.6).next_to(pies, DOWN, buff=0.35)
        self.play(LaggedStart(*[FadeIn(p, scale=0.8) for p in pies], lag_ratio=0.4), FadeIn(legend), run_time=2.5)
        expl = VGroup(
            T("Decades until you need the money = time to ride out the dips.", 22, INK),
            T("A target-date index fund handles this shift for you automatically.", 22, GOLD),
        ).arrange(DOWN, buff=0.1).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(expl))
        self.add(source_note("Example mixes, not recommendations."))
        self.wait(4)
        self.clear_body()

        # Crashes happen — and recoveries
        cr = T("Crashes are normal. Recoveries are too.", 30, weight=BOLD).next_to(self.header_group, DOWN, buff=0.35).set_x(0)
        self.play(FadeIn(cr))
        axes = plain_axes([0, 20, 5], [0, 10, 2], 11, 3.8).next_to(cr, DOWN, buff=0.4)
        # Stylized market path (not real index data)
        pts = [(0, 3), (2, 3.6), (4, 4.3), (5, 4.6), (6.5, 2.0), (8, 3.2), (10, 4.8), (12, 6.0), (13, 6.6),
               (13.6, 4.4), (14.5, 6.8), (16, 7.6), (17.5, 6.4), (19, 8.6), (20, 9.2)]
        path = VMobject(color=GREEN, stroke_width=4).set_points_smoothly([axes.c2p(x, y) for x, y in pts])
        self.play(Create(axes))
        self.play(Create(path), run_time=4, rate_func=linear)
        c1 = VGroup(
            Arrow(axes.c2p(6.5, 0.6) + UP * 0.1, axes.c2p(6.5, 1.8), color=RED, buff=0.05, stroke_width=4),
            T("2008: about −57%", 20, RED),
        )
        c1[1].next_to(c1[0], DOWN, buff=0.05)
        c2 = VGroup(
            Arrow(axes.c2p(13.6, 2.6), axes.c2p(13.6, 4.2), color=RED, buff=0.05, stroke_width=4),
            T("2020: about −34%", 20, RED),
        )
        c2[1].next_to(c2[0], DOWN, buff=0.05)
        self.play(FadeIn(c1), FadeIn(c2))
        lessons = VGroup(
            T("Don't panic-sell. For a recurring investor, a down market = stocks on sale.", 22, GOLD),
            T("Only invest money you won't need for at least 5 years.", 22, INK),
        ).arrange(DOWN, buff=0.1).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(lessons))
        self.add(source_note("Stylized chart. Drops are approximate S&P 500 peak-to-trough declines."))
        self.wait(4)
        self.clear_body()

        # Decision checklist + red flags
        def list_card(title, color, items, mark):
            box = card(6.1, 4.4, stroke=color)
            head = T(title, 28, color, weight=BOLD)
            rows = VGroup(
                *[VGroup(T(mark, 22, color, weight=BOLD), T(it, 21)).arrange(RIGHT, buff=0.2) for it in items]
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.24)
            return VGroup(box, fit(VGroup(head, rows).arrange(DOWN, buff=0.35), box))

        ask = list_card(
            "Ask before you invest",
            GREEN,
            ["Do I understand what I'm buying?", "What are the fees?", "Is it diversified?", "When will I need this money?", "Am I acting on hype or fear?"],
            "✓",
        )
        flags = list_card(
            "Red flags",
            RED,
            ["\"Guaranteed\" high returns", "Get-rich-quick or meme hype", "Borrowing money to invest", "Everything in one stock or coin", "Pressure to act right now"],
            "✗",
        )
        VGroup(ask, flags).arrange(RIGHT, buff=0.45).next_to(self.header_group, DOWN, buff=0.45).set_x(0)
        self.play(FadeIn(ask, shift=UP * 0.3))
        self.wait(3)
        self.play(FadeIn(flags, shift=UP * 0.3))
        self.wait(4)
        self.clear_all()


# ---------------------------------------------------------------------------
# 8. Recap
# ---------------------------------------------------------------------------
class Recap(Base):
    def construct(self):
        title = T("Your investing playbook", 48, weight=BOLD).to_edge(UP, buff=0.6)
        self.play(Write(title))
        items = [
            "Investing = owning assets that grow; cash loses to inflation",
            "Buy broad, low-cost index funds or ETFs",
            "Start early: time does the heavy lifting",
            "Automate a recurring amount, even $25–$50",
            "Hold for years: lower taxes, fewer mistakes",
            "Use a Roth IRA and any 401(k) match",
            "Ignore the noise and stay the course",
        ]
        rows = VGroup(
            *[VGroup(T("✓", 28, GREEN, weight=BOLD), T(t, 28)).arrange(RIGHT, buff=0.3) for t in items]
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).next_to(title, DOWN, buff=0.55)
        for r in rows:
            self.play(FadeIn(r, shift=RIGHT * 0.3), run_time=0.6)
            self.wait(0.6)
        self.wait(2.5)
        self.play(FadeOut(rows), FadeOut(title))

        q1 = T("The best time to start investing was yesterday.", 38)
        q2 = T("The second best time is today.", 38, GOLD, weight=BOLD)
        VGroup(q1, q2).arrange(DOWN, buff=0.3)
        self.play(Write(q1), run_time=1.5)
        self.play(Write(q2), run_time=1.2)
        self.wait(2.5)
        disclaimer = T(
            "Educational only — not financial advice. Returns are not guaranteed; past performance does not predict future results.",
            18,
            MUTED,
        ).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(disclaimer))
        self.wait(3)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.2)
