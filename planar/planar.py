"""
The utility problem: why three houses can't each be connected to three utilities
without two lines crossing. A short 3b1b-style video for a combinatorics class.

    manim -pql planar/planar.py Puzzle       # preview one scene
    ./planar/render.sh                       # every scene + planar_graphs.mp4

Story: try the puzzle and get stuck at 8 of 9 edges -> Euler's formula, proved by
building the drawing one edge at a time -> every edge has two sides and every face
needs at least 4 of them (no odd cycles) -> for all 9 edges the sides run out ->
on a torus the 2 becomes a 0 and the puzzle is solvable.
"""

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from style import *  # noqa: E402,F403

RED = "#E5534B"
PURPLE = "#A78BFA"
TEAL = "#4FD1A5"
HOUSE = BLUE
UTILITY = ORANGE

CENTER = np.array([0.0, -0.25, 0.0])
# A hexagon that alternates house / utility, nudged off-regular so its three long
# diagonals don't meet in a single point.
ANGLES = {"H1": (90, 2.0), "U1": (36, 2.2), "H2": (-28, 2.0), "U2": (-72, 2.0), "H3": (-150, 2.05), "U3": (152, 2.0)}
HOUSES = ["H1", "H2", "H3"]
UTILITIES = ["U1", "U2", "U3"]
HEX = [("H1", "U1"), ("U1", "H2"), ("H2", "U2"), ("U2", "H3"), ("H3", "U3"), ("U3", "H1")]
CHORD = ("H1", "U2")  # drawn inside the hexagon
ARC = ("H2", "U3")  # drawn around the outside
LAST = ("H3", "U1")  # the ninth edge: blocked both ways
FACE_COLORS = {"A": GOLD, "B": PURPLE, "C": TEAL, "D": DEEP_BLUE}
# Faces of the 8-edge drawing as vertex cycles; D is the unbounded outside face.
FACES = {
    "A": ["H1", "U1", "H2", "U2"],
    "B": ["H1", "U2", "H3", "U3"],
    "C": ["H2", "U1", "H1", "U3"],
    "D": ["H2", "U2", "H3", "U3"],
}


def polar(angle, r, center=CENTER):
    a = math.radians(angle)
    return center + np.array([r * math.cos(a), r * math.sin(a), 0.0])


POS = {k: polar(*v) for k, v in ANGLES.items()}


def is_house(v):
    return v.startswith("H")


def mix(color, amount, base=BG):
    """Opaque blend of `color` into the background."""
    return interpolate_color(ManimColor(base), ManimColor(color), amount)


# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------
def sweep(u, v, lift, turn=1, n=80):
    """Points from u to v, swinging around the outside of the hexagon (turn=1: counterclockwise)."""
    a0, a1 = ANGLES[u][0], ANGLES[v][0]
    while turn * (a1 - a0) <= 0:
        a1 += 360 * turn
    r0 = np.linalg.norm(POS[u] - CENTER)
    r1 = np.linalg.norm(POS[v] - CENTER)
    pts = []
    for i in range(n + 1):
        s = i / n
        r = r0 + (r1 - r0) * s + lift * math.sin(math.pi * s) ** 0.6
        pts.append(polar(a0 + (a1 - a0) * s, r))
    return pts


def edge_points(u, v):
    """Polyline for the drawn edge u-v, oriented from u to v."""
    if {u, v} == set(ARC):
        pts = sweep("H2", "U3", 0.9)
        return pts if u == "H2" else pts[::-1]
    return [POS[u], POS[v]]


def resample(points, n=40):
    pts = np.array(points, dtype=float)
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    cum = np.concatenate([[0], np.cumsum(seg)])
    out = []
    for t in np.linspace(0, cum[-1], n):
        i = min(np.searchsorted(cum, t, side="right") - 1, len(seg) - 1)
        f = (t - cum[i]) / seg[i] if seg[i] else 0
        out.append(pts[i] + f * (pts[i + 1] - pts[i]))
    return out


def trim(points, a):
    """Drop length `a` from both ends of a polyline."""
    pts = resample(points, 120)
    total = sum(np.linalg.norm(pts[i + 1] - pts[i]) for i in range(len(pts) - 1))
    k = int(round(len(pts) * a / total))
    return pts[k : len(pts) - k]


def offset_left(points, d):
    pts = np.array(points)
    out = []
    for i in range(len(pts)):
        t = pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]
        t = t / np.linalg.norm(t)
        out.append(pts[i] + d * np.array([-t[1], t[0], 0.0]))
    return out


def signed_area(pts):
    return 0.5 * sum(pts[i - 1][0] * pts[i][1] - pts[i][0] * pts[i - 1][1] for i in range(len(pts)))


def face_cycle(name):
    """Vertex cycle of a face, oriented so the face lies on the left of each edge."""
    cyc = FACES[name]
    pts = [p for i in range(len(cyc)) for p in edge_points(cyc[i], cyc[(i + 1) % len(cyc)])[:-1]]
    ccw = signed_area(pts) > 0
    want_ccw = name != "D"  # outside face: walk clockwise to keep it on the left
    return cyc if ccw == want_ccw else cyc[::-1]


def face_polygon(name):
    cyc = face_cycle(name)
    return [p for i in range(len(cyc)) for p in edge_points(cyc[i], cyc[(i + 1) % len(cyc)])[:-1]]


def cross(p, q, r, s):
    """Point where segments pq and rs properly cross, else None."""
    d = (q[0] - p[0]) * (s[1] - r[1]) - (q[1] - p[1]) * (s[0] - r[0])
    if abs(d) < 1e-12:
        return None
    t = ((r[0] - p[0]) * (s[1] - r[1]) - (r[1] - p[1]) * (s[0] - r[0])) / d
    u = ((r[0] - p[0]) * (q[1] - p[1]) - (r[1] - p[1]) * (q[0] - p[0])) / d
    if 1e-6 < t < 1 - 1e-6 and 1e-6 < u < 1 - 1e-6:
        return t, p + t * (q - p)
    return None


def first_hit(path, obstacles):
    """(fraction along `path`, point) of its first crossing with any obstacle polyline."""
    for k in range(len(path) - 1):
        hits = [
            h
            for ob in obstacles
            for j in range(len(ob) - 1)
            if (h := cross(path[k], path[k + 1], ob[j], ob[j + 1]))
        ]
        if hits:
            t, pt = min(hits, key=lambda h: h[0])
            return (k + t) / (len(path) - 1), pt
    return None


# ---------------------------------------------------------------------------
# Mobjects
# ---------------------------------------------------------------------------
def house_icon():
    body = Square(0.42).shift(DOWN * 0.08)
    roof = Polygon([-0.31, 0.13, 0], [0.31, 0.13, 0], [0, 0.42, 0])
    door = Rectangle(width=0.12, height=0.2).move_to(body.get_bottom() + UP * 0.1)
    icon = VGroup(Union(body, roof), door)
    icon[0].set_style(fill_color=HOUSE, fill_opacity=1, stroke_width=0)
    icon[1].set_style(fill_color=BG, fill_opacity=1, stroke_width=0)
    return icon.move_to(ORIGIN)


def drop(height=0.36):
    pts = [[0.55 * math.sin(t) * math.sin(t / 2), math.cos(t), 0] for t in np.linspace(0, 2 * math.pi, 60)]
    return VMobject().set_points_smoothly(pts).scale(height / 2)


def utility_icon(kind):
    disc = Circle(0.32).set_style(fill_color=UTILITY, fill_opacity=1, stroke_width=0)
    if kind == "water":
        glyph = drop().shift(DOWN * 0.02)
    elif kind == "power":
        glyph = Polygon(
            [0.05, 0.2, 0], [-0.12, -0.02, 0], [0.0, -0.02, 0], [-0.05, -0.2, 0], [0.12, 0.04, 0], [0.0, 0.04, 0]
        )
    else:  # gas: a three-tongued flame
        glyph = Union(
            drop(0.36).shift(UP * 0.02),
            drop(0.22).rotate(0.55).shift(LEFT * 0.09 + DOWN * 0.05),
            drop(0.22).rotate(-0.55).shift(RIGHT * 0.09 + DOWN * 0.05),
        )
    glyph.set_style(fill_color=BG, fill_opacity=1, stroke_width=0)
    return VGroup(disc, glyph)


def vertex_dot(v):
    return Dot(radius=0.12, color=HOUSE if is_house(v) else UTILITY).set_z_index(3)


def edge_mob(u, v, color=INK, width=4):
    path = VMobject(stroke_color=color, stroke_width=width)
    pts = edge_points(u, v)
    if len(pts) > 2:
        path.set_points_smoothly(pts)
    else:
        path.set_points_as_corners(pts)
    return path


def fill_mob(points, color, amount=0.3):
    return (
        VMobject()
        .set_points_as_corners([*points, points[0]])
        .set_style(fill_color=mix(color, amount), fill_opacity=1, stroke_width=0)
        .set_z_index(-2)
    )


def face_fill(name):
    return fill_mob(face_polygon(name), FACE_COLORS[name])


def outside_fill(name="D"):
    return (
        FullScreenRectangle()
        .set_style(fill_color=mix(FACE_COLORS[name], 0.16), fill_opacity=1, stroke_width=0)
        .set_z_index(-3)
    )


def sides_of(name, d=0.09, gap=0.2):
    """One short stroke per edge of the face, on the face's side of that edge."""
    cyc = face_cycle(name)
    group = VGroup()
    for i in range(len(cyc)):
        pts = offset_left(trim(edge_points(cyc[i], cyc[(i + 1) % len(cyc)]), gap), d)
        group.add(VMobject(stroke_color=FACE_COLORS[name], stroke_width=5).set_points_smoothly(pts))
    return group.set_z_index(1)


def graph_8(with_faces=False):
    """The best attempt: hexagon, one chord inside, one around the outside."""
    edges = VGroup(*[edge_mob(*e) for e in HEX + [CHORD, ARC]])
    dots = VGroup(*[vertex_dot(v) for v in POS]).set_z_index(3)
    for d, v in zip(dots, POS):
        d.move_to(POS[v])
    faces = VGroup(*[face_fill(n) for n in "ABC"], outside_fill()) if with_faces else VGroup()
    return edges, dots, faces


def tex_row(values, colors=None):
    row = MathTex(*[str(v) for v in values], font_size=56, color=INK)
    for i, c in (colors or {}).items():
        row[i].set_color(c)
    return row


class PClip(Clip):
    PACE = 1.25
    HOLD = 3.0


# ---------------------------------------------------------------------------
# 1. The puzzle
# ---------------------------------------------------------------------------
class Puzzle(PClip):
    def construct(self):
        rows = {
            "H1": [-3.2, 1.6, 0], "H2": [0, 1.6, 0], "H3": [3.2, 1.6, 0],
            "U1": [-3.2, -1.9, 0], "U2": [0, -1.9, 0], "U3": [3.2, -1.9, 0],
        }
        icons = {h: house_icon().move_to(rows[h]) for h in HOUSES}
        for u, kind in zip(UTILITIES, ["water", "power", "gas"]):
            icons[u] = utility_icon(kind).move_to(rows[u])
        for m in icons.values():
            m.set_z_index(3)
        names = VGroup(
            *[T(k, 20, MUTED).next_to(icons[u], DOWN, buff=0.15) for u, k in zip(UTILITIES, ["water", "power", "gas"])]
        )
        rule = caption("Connect every house to every utility, with no two lines crossing.", 28)

        self.play(LaggedStart(*[FadeIn(icons[v], scale=0.6) for v in HOUSES + UTILITIES], lag_ratio=0.12))
        self.play(FadeIn(names), FadeIn(rule))
        self.hold()

        # Straight lines everywhere, with live crossing markers.
        live = [(h, u) for h in HOUSES for u in UTILITIES]
        lines = {
            e: always_redraw(lambda e=e: Line(icons[e[0]].get_center(), icons[e[1]].get_center(), color=INK, stroke_width=4))
            for e in live
        }

        def crossings():
            pts = []
            for i, a in enumerate(live):
                for b in live[i + 1 :]:
                    h = cross(icons[a[0]].get_center(), icons[a[1]].get_center(),
                              icons[b[0]].get_center(), icons[b[1]].get_center())
                    if h:
                        pts.append(h[1])
            return pts

        marks = always_redraw(
            lambda: VGroup(*[Dot(p, radius=0.09, color=RED).set_z_index(4) for p in crossings()])
        )
        count = always_redraw(
            lambda: T(f"{len(crossings())} crossings", 30, RED, weight=MEDIUM).to_corner(UR, buff=0.5)
        )
        self.play(LaggedStart(*[Create(lines[e]) for e in live], lag_ratio=0.1), run_time=2.5)
        self.add(marks)
        self.play(FadeIn(count))
        self.hold()

        # Untangle: slide the icons onto a hexagon that alternates house / utility.
        self.play(FadeOut(names), FadeOut(rule))
        self.play(*[icons[v].animate.move_to(POS[v]) for v in POS], run_time=3)
        self.hold(2)

        # Keep the hexagon, take out the three long diagonals, then add them back one at a time.
        diagonals = [CHORD, ARC, LAST]
        keyed = {frozenset(e): lines[e] for e in live}
        diag_mobs = [keyed[frozenset(e)] for e in diagonals]
        for e in diagonals:
            live.remove(next(x for x in live if set(x) == set(e)))
        self.play(*[FadeOut(m) for m in diag_mobs], FadeOut(count))
        self.remove(marks)
        for m in diag_mobs:
            m.clear_updaters()
        self.hold(1.5)

        inside = edge_mob(*CHORD)
        outside = edge_mob(*ARC)
        self.play(Create(inside), run_time=1.2)
        self.play(Create(outside), run_time=2)
        tally = T("8 of 9", 34, INK, weight=MEDIUM).to_corner(UR, buff=0.5)
        self.play(FadeIn(tally))
        self.hold(2)

        # The ninth edge is blocked inside and outside.
        obstacles = [edge_points(*e) for e in HEX + [CHORD, ARC]]
        attempts = [
            [POS["H3"], POS["U1"]],
            sweep("H3", "U1", 0.5),
        ]
        for pts in attempts:
            frac, hit = first_hit(pts, obstacles)
            path = VMobject(stroke_color=GOLD, stroke_width=4)
            if len(pts) > 2:
                path.set_points_smoothly(pts)
            else:
                path.set_points_as_corners(pts)
            grow = ValueTracker(0.001)
            piece = always_redraw(lambda path=path: _partial(path, grow.get_value()))
            self.add(piece)
            self.play(grow.animate.set_value(frac), run_time=2, rate_func=smooth)
            bang = Dot(hit, radius=0.13, color=RED).set_z_index(4)
            self.play(Flash(hit, color=RED, line_length=0.25, flash_radius=0.3), FadeIn(bang, scale=2), run_time=0.8)
            self.wait(0.8)
            self.play(grow.animate.set_value(0.001), FadeOut(bang), run_time=1.2)
            self.remove(piece)

        stuck = caption("Every arrangement gets stuck at 8. Is the 9th truly impossible?", 28)
        self.play(FadeIn(stuck))
        self.hold()

        # Abstract: houses and utilities are just two kinds of vertex.
        dots = {v: vertex_dot(v).move_to(POS[v]) for v in POS}
        self.play(
            *[ReplacementTransform(icons[v], dots[v]) for v in POS],
            FadeOut(stuck),
            FadeOut(tally),
            run_time=1.5,
        )
        name = MathTex(r"K_{3,3}", font_size=64, color=INK).to_corner(UL, buff=0.6)
        sub = T("6 vertices, 9 edges:\nevery house joined\nto every utility", 24, MUTED, line_spacing=0.9).next_to(name, DOWN, aligned_edge=LEFT)
        q = caption("Can K₃,₃ be drawn in the plane with no crossings? Is it planar?", 28)
        self.play(Write(name), FadeIn(sub))
        self.play(FadeIn(q))
        self.hold()
        self.clear()


def _partial(path, alpha):
    piece = path.copy()
    piece.pointwise_become_partial(path, 0, min(max(alpha, 1e-4), 1))
    return piece


# ---------------------------------------------------------------------------
# 2. Euler's formula, built one edge at a time
# ---------------------------------------------------------------------------
class Euler(PClip):
    def construct(self):
        head = MathTex("V", "-", "E", "+", "F", "=", "2", font_size=56, color=INK).to_edge(UP, buff=0.35).shift(LEFT * 4.3)
        state = {"V": 1, "E": 0, "F": 1}

        def numbers(changed=()):
            vals = [state["V"], "-", state["E"], "+", state["F"], "=", state["V"] - state["E"] + state["F"]]
            colors = {i: GOLD for i, k in zip((0, 2, 4), "VEF") if k in changed}
            row = tex_row(vals, colors)
            for a, b in zip(row, head):
                a.set_x(b.get_x())
            return row.next_to(head, DOWN, buff=0.35).set_x(head.get_x())

        row = numbers()
        dots = {v: vertex_dot(v).move_to(POS[v]) for v in POS}

        self.play(FadeIn(dots["H1"], scale=0.5))
        self.play(Write(head), FadeIn(row))
        note = caption("One vertex. The whole plane is a single face.", 28)
        self.play(FadeIn(note))
        self.hold()

        def step(anims, changed, text=None, hold=None, face=None):
            nonlocal row, note
            for k in changed:
                state[k] += 1
            new_row = numbers(changed)
            extra = [FadeIn(face)] if face is not None else []
            if text is not None:
                new_note = caption(text, 28)
                extra += [FadeOut(note), FadeIn(new_note)]
                note = new_note
            self.play(*anims, run_time=1.2)
            self.play(Transform(row, new_row), *extra, run_time=0.8)
            self.hold(hold)

        # A path around the hexagon: each edge brings a new vertex.
        path = ["H1", "U1", "H2", "U2", "H3", "U3"]
        for i, (u, v) in enumerate(zip(path, path[1:])):
            e = edge_mob(u, v)
            text = "A new edge out to a new vertex: V and E both go up by 1." if i == 0 else None
            step([Create(e), FadeIn(dots[v], scale=0.5)], "VE", text, hold=None if i == 0 else 0.6)

        # Edges between existing vertices: each one splits a face in two.
        hex_fill = fill_mob([POS[v] for v in path], FACE_COLORS["B"])
        step(
            [Create(edge_mob("U3", "H1"))],
            "EF",
            "An edge between two existing vertices splits a face: E and F both go up by 1.",
            face=hex_fill,
        )
        step([Create(edge_mob(*CHORD))], "EF", hold=1, face=face_fill("A"))
        step([Create(edge_mob(*ARC), run_time=1.6)], "EF", hold=1, face=face_fill("C"))

        done = caption("Every step keeps V − E + F = 2, for any connected planar drawing.", 28)
        self.play(FadeOut(note), FadeIn(done), Transform(row, numbers()))
        self.play(Circumscribe(VGroup(head, row), color=GOLD, buff=0.15))
        self.hold()
        self.clear()


# ---------------------------------------------------------------------------
# 3. Faces and the sides of edges
# ---------------------------------------------------------------------------
class Faces(PClip):
    def construct(self):
        edges, dots, _ = graph_8()
        fills = {n: face_fill(n) for n in "ABC"}
        outside = outside_fill()
        self.add(edges, dots, *fills.values())
        note = caption("Our best attempt: 8 edges and 4 faces. The outside counts as a face.", 28)
        self.play(FadeIn(outside), FadeIn(note))
        self.hold()

        # Count each face's edges.
        spots = {
            "A": None, "B": None,
            "C": polar(52, 2.42),
            "D": polar(-120, 2.75),
        }
        labels = {}
        for n in "ABCD":
            pts = face_polygon(n)
            spot = spots[n] if spots[n] is not None else np.mean(pts, axis=0)
            labels[n] = MathTex("4", font_size=48, color=FACE_COLORS[n]).move_to(spot).set_z_index(5)
        new_note = caption("Walk around any face: it is bounded by 4 edges.", 28)
        self.play(FadeOut(note), FadeIn(new_note))
        note = new_note
        for i, n in enumerate("ABCD"):
            loop = VMobject(stroke_color=FACE_COLORS[n], stroke_width=8).set_points_as_corners(
                [*face_polygon(n), face_polygon(n)[0]]
            ).set_z_index(2)
            self.play(Create(loop), run_time=1.6 if i == 0 else 1.0)
            self.play(FadeIn(labels[n], scale=1.5), FadeOut(loop), run_time=0.6)
        self.hold(2)

        # Why never fewer than 4: colours alternate around any cycle.
        new_note = caption("Lines only run house to utility, so colors alternate around every loop.", 28)
        self.play(FadeOut(note), FadeIn(new_note))
        note = new_note
        cyc = face_cycle("A")
        walker = Dot(POS[cyc[0]], radius=0.2, color=GOLD).set_z_index(4)
        self.play(FadeIn(walker))
        for i in range(4):
            u, v = cyc[i], cyc[(i + 1) % 4]
            self.play(MoveAlongPath(walker, edge_mob(u, v)), Indicate(dots[list(POS).index(v)], scale_factor=1.6), run_time=0.7)
        self.play(FadeOut(walker))

        tri = VGroup(
            Dot([4.9, 1.6, 0], radius=0.14, color=HOUSE),
            Dot([4.1, 0.3, 0], radius=0.14, color=UTILITY),
            Dot([5.7, 0.3, 0], radius=0.14, color=MUTED),
        ).set_z_index(3)
        tri_edges = VGroup(
            Line(tri[0].get_center(), tri[1].get_center(), color=INK),
            Line(tri[1].get_center(), tri[2].get_center(), color=INK),
            Line(tri[2].get_center(), tri[0].get_center(), color=INK),
        )
        qmark = T("?", 28, INK, weight=MEDIUM).next_to(tri[2], RIGHT, buff=0.12)
        new_note = caption("A triangle would need its third corner to be both. So every face has at least 4 edges.", 26)
        self.play(FadeOut(note), FadeIn(new_note), Create(tri_edges), FadeIn(tri), FadeIn(qmark))
        note = new_note
        for c in (HOUSE, UTILITY, HOUSE, UTILITY):
            self.play(tri[2].animate.set_color(c), run_time=0.35)
        self.play(tri[2].animate.set_color(RED), tri_edges.animate.set_color(RED), run_time=0.4)
        self.hold()
        self.play(FadeOut(VGroup(tri, tri_edges, qmark)))

        # Every edge has two sides; each face uses 4 of them.
        sides = {n: sides_of(n) for n in "ABCD"}
        new_note = caption("Every edge has two sides, one for each face it touches.", 28)
        self.play(FadeOut(note), FadeIn(new_note), edges.animate.set_stroke(opacity=0.35))
        note = new_note
        for n in "ABCD":
            self.play(LaggedStart(*[Create(s) for s in sides[n]], lag_ratio=0.2), run_time=1.0)
        self.hold(2)

        tally = VGroup(
            MathTex(r"2E", "=", r"2 \times 8", "=", "16", font_size=48, color=INK),
            MathTex(r"4F", "=", r"4 \times 4", "=", "16", font_size=48, color=INK),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).to_corner(UR, buff=0.5)
        tally[0][0].set_color(MUTED)
        tally[1][0].set_color(MUTED)
        labels_t = VGroup(
            T("sides", 22, MUTED).next_to(tally[0], LEFT, buff=0.3),
            T("needed", 22, MUTED).next_to(tally[1], LEFT, buff=0.3),
        )
        new_note = caption("16 sides, and the 4 faces need 4 each. Every side is already used.", 28)
        self.play(FadeOut(note), FadeIn(new_note), FadeIn(tally[0]), FadeIn(labels_t[0]))
        self.play(FadeIn(tally[1]), FadeIn(labels_t[1]))
        self.play(tally[0][4].animate.set_color(GOLD), tally[1][4].animate.set_color(GOLD))
        self.hold()
        self.clear()


# ---------------------------------------------------------------------------
# 4. Nine edges: the sides run out
# ---------------------------------------------------------------------------
class Contradiction(PClip):
    def construct(self):
        top = T("Suppose all 9 edges could be drawn.", 30, INK).to_edge(UP, buff=0.5)
        self.play(FadeIn(top))

        euler = MathTex("F", "=", "2", "-", "V", "+", "E", font_size=52, color=INK)
        euler_n = MathTex("F", "=", "2", "-", "6", "+", "9", "=", "5", font_size=52, color=INK)
        VGroup(euler, euler_n).next_to(top, DOWN, buff=0.45)
        euler_n[-1].set_color(GOLD)
        tag = T("Euler", 22, MUTED).next_to(euler_n, LEFT, buff=0.5)
        self.play(Write(euler), FadeIn(tag))
        self.play(TransformMatchingTex(euler, euler_n))
        self.hold(2)

        # Nine edges, each with two sides.
        edges, sides = VGroup(), VGroup()
        for i in range(9):
            a, b = np.array([-0.3, 0, 0]), np.array([0.3, 0, 0])
            edges.add(VGroup(
                Line(a, b, color=INK, stroke_width=3),
                Dot(a, radius=0.07, color=HOUSE), Dot(b, radius=0.07, color=UTILITY),
            ).shift(RIGHT * 0.95 * i))
            for dy in (0.13, -0.13):
                sides.add(Line(a * 0.6, b * 0.6, color=GOLD, stroke_width=5).shift(RIGHT * 0.95 * i + UP * dy))
        VGroup(edges, sides).move_to([0.9, 0.55, 0])
        sides_label = T("9 edges, 18 sides", 24, MUTED).next_to(edges, LEFT, buff=0.5)
        self.play(LaggedStart(*[FadeIn(e) for e in edges], lag_ratio=0.08), FadeIn(sides_label))
        self.play(LaggedStart(*[Create(s) for s in sides], lag_ratio=0.05))
        self.hold(1)

        # Five faces, each needing four sides.
        boxes = VGroup()
        for _ in range(5):
            slots = VGroup(
                *[RoundedRectangle(width=0.62, height=0.2, corner_radius=0.06, stroke_color=FAINT, stroke_width=2) for _ in range(4)]
            ).arrange(DOWN, buff=0.14)
            frame = SurroundingRectangle(slots, buff=0.16, corner_radius=0.12, stroke_color=MUTED, stroke_width=2)
            boxes.add(VGroup(frame, slots))
        boxes.arrange(RIGHT, buff=0.45).move_to([0.9, -1.75, 0])
        box_label = T("5 faces, 4 sides each", 24, MUTED).next_to(boxes, LEFT, buff=0.5)
        self.play(FadeIn(boxes), FadeIn(box_label))

        slots = [s for b in boxes for s in b[1]]
        moves = [sides[i].animate.move_to(slots[i]).set_stroke(width=6) for i in range(18)]
        self.play(LaggedStart(*moves, lag_ratio=0.12), edges.animate.set_opacity(0.3), run_time=4)
        empty = VGroup(*slots[18:])
        self.play(empty.animate.set_stroke(RED, width=4), boxes[4][0].animate.set_stroke(RED), run_time=0.6)
        self.play(Indicate(empty, color=RED, scale_factor=1.3))
        verdict = MathTex(r"4F", "=", "20", ">", "18", "=", "2E", font_size=56, color=INK)
        verdict[2].set_color(RED)
        verdict[4].set_color(GOLD)
        verdict.to_edge(DOWN, buff=0.5)
        self.play(Write(verdict))
        self.hold()
        self.clear()

        # The same argument in general: three facts, one inequality.
        facts = VGroup(
            MathTex(r"V - E + F = 2", font_size=48),
            MathTex(r"\textstyle\sum_{\text{faces}} \text{(edges around it)} = 2E", font_size=48),
            MathTex(r"\text{every face has} \ge 4 \text{ edges}", font_size=48),
        ).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        reasons = VGroup(
            T("Euler's formula", 24, MUTED),
            T("every edge has two sides", 24, MUTED),
            T("no odd cycles in K₃,₃", 24, MUTED),
        )
        facts.set_color(INK).move_to([1.3, 1.6, 0])
        for f, r in zip(facts, reasons):
            r.next_to(facts, LEFT, buff=0.6).set_y(f.get_y())
        for f, r in zip(facts, reasons):
            self.play(FadeIn(r), Write(f), run_time=1.2)
            self.wait(0.6)
        self.hold(2)

        chain = VGroup(
            MathTex(r"4F \le 2E", font_size=50),
            MathTex(r"2 = V - E + F \le V - \tfrac{E}{2}", font_size=50),
            MathTex(r"E \le 2V - 4", font_size=56),
        ).arrange(RIGHT, buff=0.8).move_to([0, -0.9, 0])
        arrows = VGroup(*[MathTex(r"\Rightarrow", font_size=50, color=MUTED).move_to((chain[i].get_right() + chain[i + 1].get_left()) / 2) for i in range(2)])
        chain.set_color(INK)
        chain[2].set_color(GOLD)
        self.play(TransformFromCopy(VGroup(facts[1], facts[2]), chain[0]))
        self.play(FadeIn(arrows[0]), TransformFromCopy(VGroup(facts[0], chain[0]), chain[1]))
        self.play(FadeIn(arrows[1]), TransformFromCopy(chain[1], chain[2]))
        self.hold(1.5)

        k33 = MathTex(r"K_{3,3}:\quad 9 \le 2 \cdot 6 - 4 = 8", font_size=52, color=INK).move_to([0, -2.4, 0])
        nope = T("✗", 52, RED, weight=BOLD).next_to(k33, RIGHT, buff=0.4)
        self.play(Write(k33))
        self.play(FadeIn(nope, scale=1.6))
        self.hold()

        # The same three facts, with triangles allowed, rule out K5.
        self.play(FadeOut(VGroup(k33, nope, chain, arrows)))
        pent = [np.array([math.cos(math.radians(90 + 72 * i)), math.sin(math.radians(90 + 72 * i)), 0]) * 1.1 + np.array([4.6, -1.7, 0]) for i in range(5)]
        k5 = VGroup(
            *[Line(pent[i], pent[j], color=INK, stroke_width=3) for i in range(5) for j in range(i + 1, 5)],
            *[Dot(p, radius=0.1, color=INK) for p in pent],
        )
        k5_name = MathTex("K_5", font_size=44, color=INK).next_to(k5, UP, buff=0.2)
        alt = VGroup(
            MathTex(r"\text{faces} \ge 3 \text{ edges}", r"\;\Rightarrow\;", r"E \le 3V - 6", font_size=48),
            MathTex(r"K_5:\quad 10 \le 3 \cdot 5 - 6 = 9", font_size=48),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4).move_to([-1.4, -1.7, 0])
        alt.set_color(INK)
        nope5 = T("✗", 48, RED, weight=BOLD).next_to(alt[1], RIGHT, buff=0.35)
        aside = T("Allow triangles and the same three facts rule out K₅.", 24, MUTED).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(aside), Create(k5), FadeIn(k5_name))
        self.play(Write(alt[0]))
        self.play(Write(alt[1]), FadeIn(nope5, scale=1.6))
        self.hold()
        self.clear()


# ---------------------------------------------------------------------------
# 5. On a torus it works
# ---------------------------------------------------------------------------
class Torus(PClip):
    def construct(self):
        S = 2.5
        shift = np.array([-2.6, -0.25, 0])
        pos = {k: (POS[k] - CENTER) * 0.68 + shift for k in POS}

        sq = Square(2 * S, stroke_color=MUTED, stroke_width=3).move_to(shift)
        corners = [sq.get_corner(c) for c in (DL, DR, UR, UL)]

        def chevrons(a, b, n, color):
            mid = (a + b) / 2
            d = (b - a) / np.linalg.norm(b - a)
            return VGroup(*[
                Arrow(mid + d * (k * 0.22 - 0.25), mid + d * (k * 0.22 + 0.05), buff=0, color=color,
                      stroke_width=4, max_tip_length_to_length_ratio=0.6, tip_length=0.18)
                for k in range(n)
            ])

        marks = VGroup(
            chevrons(corners[0], corners[1], 2, PURPLE), chevrons(corners[3], corners[2], 2, PURPLE),
            chevrons(corners[0], corners[3], 1, TEAL), chevrons(corners[1], corners[2], 1, TEAL),
        )
        note = caption("Glue the square's opposite edges together and it becomes a torus.", 28)
        self.play(Create(sq), FadeIn(marks), FadeIn(note))
        self.hold(2)

        def line(a, b):
            return Line(a, b, color=INK, stroke_width=4)

        dots = VGroup(*[vertex_dot(v).move_to(pos[v]) for v in pos])
        base = VGroup(*[line(pos[u], pos[v]) for u, v in HEX + [CHORD]])
        self.play(FadeIn(dots), Create(base), run_time=1.5)
        new_note = caption("The hexagon and one chord, as before. Now the other two can leave the square.", 28)
        self.play(FadeOut(note), FadeIn(new_note))
        note = new_note
        self.hold(1.5)

        # H2 -> right edge, reappear on the left -> U3.
        y = pos["H2"][1]
        right, left = np.array([shift[0] + S, y, 0]), np.array([shift[0] - S, y, 0])
        x = pos["U1"][0]
        topp, bot = np.array([x, shift[1] + S, 0]), np.array([x, shift[1] - S, 0])
        for a, out, back, b, color in ((pos["H2"], right, left, pos["U3"], TEAL), (pos["U1"], topp, bot, pos["H3"], PURPLE)):
            first, second = line(a, out), line(back, b)
            p_out, p_in = Dot(out, radius=0.09, color=color), Dot(back, radius=0.09, color=color)
            self.play(Create(first), run_time=1.0)
            self.play(Flash(out, color=color, flash_radius=0.25), FadeIn(p_out), FadeIn(p_in), run_time=0.6)
            self.play(Create(second), run_time=1.0)
            self.wait(0.5)

        all9 = T("9 of 9", 34, GOLD, weight=MEDIUM).to_corner(UR, buff=0.5)
        new_note = caption("On a torus, all nine connections fit with no crossings.", 28)
        self.play(FadeOut(note), FadeIn(new_note), FadeIn(all9))
        note = new_note
        self.hold()

        eq = VGroup(
            MathTex(r"V - E + F = 0", font_size=48),
            MathTex(r"F = 0 - 6 + 9 = 3", font_size=48),
            MathTex(r"4F = 12 \le 18 = 2E", font_size=48),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.45).move_to([3.9, 0.2, 0])
        eq.set_color(INK)
        eq[0][0][-1].set_color(GOLD)
        tag = T("torus", 24, MUTED).next_to(eq, UP, buff=0.4).align_to(eq, LEFT)
        new_note = caption("On a torus Euler's formula ends in 0, not 2, and the sides no longer run out.", 28)
        self.play(FadeOut(note), FadeIn(new_note), FadeIn(tag), Write(eq[0]))
        note = new_note
        self.play(Write(eq[1]))
        self.play(Write(eq[2]))
        self.hold()
        self.clear()

        # Kuratowski: these two graphs are the only obstructions.
        k5_pts = [np.array([math.cos(math.radians(90 + 72 * i)), math.sin(math.radians(90 + 72 * i)), 0]) * 1.4 + np.array([-3, 0.3, 0]) for i in range(5)]
        k5 = VGroup(
            *[Line(k5_pts[i], k5_pts[j], color=INK, stroke_width=3) for i in range(5) for j in range(i + 1, 5)],
            *[Dot(p, radius=0.11, color=INK).set_z_index(3) for p in k5_pts],
        )
        hs = [np.array([1.6 + 1.4 * i, 1.3, 0]) for i in range(3)]
        us = [np.array([1.6 + 1.4 * i, -0.7, 0]) for i in range(3)]
        k33 = VGroup(
            *[Line(h, u, color=INK, stroke_width=3) for h in hs for u in us],
            *[Dot(h, radius=0.11, color=HOUSE).set_z_index(3) for h in hs],
            *[Dot(u, radius=0.11, color=UTILITY).set_z_index(3) for u in us],
        )
        names = VGroup(
            MathTex("K_5", font_size=48, color=INK).next_to(k5, DOWN, buff=0.35),
            MathTex("K_{3,3}", font_size=48, color=INK).next_to(k33, DOWN, buff=0.35),
        )
        names[1].set_y(names[0].get_y())
        thm = VGroup(
            T("Kuratowski (1930)", 26, MUTED),
            T("A graph is planar exactly when it contains neither of these, even with edges subdivided.", 26, INK),
        ).arrange(DOWN, buff=0.2).to_edge(DOWN, buff=0.5)
        self.play(Create(k5), Create(k33), run_time=2)
        self.play(FadeIn(names), FadeIn(thm))
        self.hold(5)
