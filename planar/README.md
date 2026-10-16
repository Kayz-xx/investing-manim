# The utility problem: why K₃,₃ isn't planar

A short [Manim](https://www.manim.community/) video (about 4½ minutes, 1080p30, no audio) for a combinatorics class.
It starts with the puzzle, takes Euler's formula, the two sides of every edge, and the missing odd cycles one at a time, and then combines them into the proof.

- [`planar_graphs.mp4`](planar_graphs.mp4) is the whole video.
- `clips/` has one file per scene, so you can pause between them or play them like slides.

| # | Scene | On screen | The point |
|---|-------|-----------|-----------|
| 1 | `Puzzle` | Three houses and three utilities. Straight lines give 9 crossings, a live counter falls to 3 as the icons slide onto a hexagon, and then one chord goes inside and one around the outside. The ninth line is blocked both inside and outside. The icons become vertices of K₃,₃. | Every attempt gets stuck at 8 of 9. Is that a proof? |
| 2 | `Euler` | The same drawing rebuilt from a single vertex, with V − E + F updating live. Path edges add a vertex; closing edges split a face, which fills with color. | Every edge raises V and E together, or E and F together, so V − E + F = 2 never changes |
| 3 | `Faces` | The 8-edge drawing with its 4 faces colored, the outside included. Each face is traced and counted (4 edges each). A walker shows colors alternating around a loop, so a triangle is impossible. Then every edge gets two colored strokes, one on each side. | 2E = 16 sides and 4F = 16 needed: every side is already used |
| 4 | `Contradiction` | For all 9 edges, Euler forces F = 5. 18 edge sides fly into 5 faces that need 4 each, and the last face comes up 2 short. Then the general argument: three facts combine into E ≤ 2V − 4, so 9 ≤ 8 is false. Brief echo: with triangles allowed, E ≤ 3V − 6 rules out K₅ | 4F = 20 > 18 = 2E |
| 5 | `Torus` | A square with opposite edges glued. The two blocked chords leave through one edge and come back through the opposite one, so all 9 fit. On a torus V − E + F = 0, so F = 3 and only 12 sides are needed. The ending is Kuratowski's theorem with K₅ and K₃,₃ | The "2" in Euler's formula is what makes the plane too small |

## Rendering

You need the same setup as the main project (Python, `ffmpeg`, Pango) **plus LaTeX** for the equations: `texlive-latex-base`, `texlive-latex-extra` (for `standalone`) and `dvisvgm` on Debian/Ubuntu, or MacTeX.

```bash
./planar/render.sh                         # every scene at 1080p30, plus planar_graphs.mp4
./planar/render.sh -ql                     # fast 480p preview
JOBS=5 ./planar/render.sh                  # render the scenes in parallel
manim -pql planar/planar.py Contradiction  # one scene
```

It reuses the palette and Roboto from `style.py`. Houses are blue and utilities are orange throughout, which is the bipartition the proof relies on. `PClip.PACE` and `PClip.HOLD` in `planar.py` set the speed and the pauses.

## Notes on the math

- The hexagon is drawn slightly off-regular on purpose. In a regular hexagon the three long diagonals meet at one point, which would make "3 crossings" look like 1.
- The torus drawing was checked by tracing its faces from the rotation system: 3 faces of lengths 4, 4 and 10, so V − E + F = 6 − 9 + 3 = 0.
- Euler's formula is shown for connected drawings. The build-up order (a spanning path first, then the closing edges) is the standard induction on edges.
