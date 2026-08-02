# leonpanjwani.com

A single-file, no-build personal engineering portfolio. `index.html` holds the
markup, all the CSS and all the JS. Deployed on **Cloudflare Pages**, which
serves the repo root as-is — pushing to `main` on GitHub is the deploy.

```
index.html         everything
cv.pdf             linked from About
favicon.png
img/leon.jpg       the About portrait (900×900, same-origin — see below)
img/               the project and carousel images are still MISSING
.claude/serve.py   local dev server
```

Section order is **About → Work → Skills → Contact**. About comes first
deliberately; the nav and the info block on the sheet follow the same order.

## Running it

```bash
python3 .claude/serve.py 4321
```

`.claude/launch.json` runs the same thing for Claude Code's `preview_start`.
Use a real HTTP server rather than `file://` — the WebGL canvas and the Google
Fonts preconnects behave differently on a file URL.

`python3 -m http.server` is deliberately **not** used: its module-level
argparse calls `os.getcwd()`, which the sandbox denies before any argument is
read. `serve.py` pins the directory instead.

## The one rule: the 11px grid

**Every edge on this site lands on an 11px line.** That is the whole design.
Break it and the page stops looking like a drawing sheet.

- `--u: 11px` is the cell. `55px` (5 cells) is a **square** — the bold grid line.
- Section padding, card heights, image heights, the carousel, the info block
  and the portrait are all whole squares, computed in JS, not hardcoded.
- `measure()` sizes the drawing area to a whole number of squares and centres
  it, so all four inner edges of the white frame land on lines.
- `lockGrid()` runs after layout and rounds card heights **up** to the next
  square, then pads each section so the next one still starts on a line.
- The blueprint grid is anchored to the frame's inner top-left (`--fx`/`--fy`).
  The white page's grid is anchored to `--wrapL`. Same pitch, so they join
  without a seam.

If you add a box, size it from `SQ` in `measure()` and expose it as a CSS
custom property. Do not type a pixel height into the stylesheet.

## Palette

Five colours, plus one accent. Everything else is an alpha of one of these.

| var | hex | use |
|---|---|---|
| `--blue` | `#243f8f` | the blueprint stock |
| `--navy` | `#192c64` | headings, page ink, body text |
| `--pale` | `#bdc5dd` | lines drawn on the blueprint |
| `--paper` | `#e9ebf3` | flat light panels |
| `--white` | `#ffffff` | |
| `--tomato` | `#FF6347` | accent: hover states and the cursor |

Shadow ink goes darker than any of them and is written as **literal**
`rgba(9,16,42,a)` — never `rgba(var(--x),a)`. That substitution is invalid at
computed-value time and silently makes the whole declaration transparent,
which is what once left the roll unpainted on iOS.

## How the page is put together

Stacking order, bottom to top:

| z | element | |
|---|---|---|
| 0 | `#sheet` | the blueprint. Fixed, full-viewport. **Clipped away by the roll.** |
| 10 | `.content` | the white page, scrolls up over the sheet |
| 30 | `#roll` | the tube the paper winds onto |
| 50 | `#layer` | header islands + the coordinate readout |
| 55 | `#corners` | the four peelable page corners |
| 60 | `#cursor` | the grid-cell cursor |

**Everything printed on the paper lives inside `#sheet`** — the name, the 3D
canvas, the dimensions, the view label and the info cells. `#sheet` carries a
`clip-path` driven by the roll's position, so its whole subtree is carried off
with the paper. If you add something that should roll away, put it in there;
if it should survive onto the white page, put it in `#layer`.

Scroll budget: `#stage` is `M.W + 1.5vh` tall. The first `M.W`
(`TOUR.travel` × viewport height) is the **pinned camera walkthrough** —
nothing moves but the view. After that the paper rolls up over `1.5vh`.

## The hero name

Two implementations of the same thing, and they must agree:

1. **3D** (`build3D`) — Chakra Petch outlines are embedded as raw font units in
   `FONT3D`, extruded, and drawn as white feature edges on a transparent
   orthographic canvas mapped **1 world unit = 1 CSS px**. The full stop is a
   hex screw.
2. **2D fallback** (`#name` / `.word` / `.ltr`) — the same glyphs as real text
   with a hairline stroke. Used when there is no WebGL, no three.js, or
   reduced motion. It is also the accessible label and the source of the
   baseline/width measurements the 3D layout is planted on.

The name **does not dock into the header**. It rests where the intro leaves it
— front elevation, dimensioned — and rolls away with the paper. The header
wordmark (`#brand`) is separate DOM text that fades in with the menu, styled
as the same material: hairline outline, translucent fill, `--bink`/`--bfill`
driven per frame so its ink follows the surface.

Do **not** put a `transition` on `-webkit-text-fill-color`. `update()` rewrites
the custom property every scroll frame and the computed value never leaves the
start of the animation — the fill sticks on its fallback for the life of the
page, and an inline override won't shift it either.

`EXT` samples the whole tour once at unit font size to find the worst-case
projected extents, and `measure()` sizes the name so **no view ever crosses the
frame**. That guarantee is solved at camera zoom 1, which is why `TOUR.cam`
never goes above 1.0 — pulling back is safe, pushing in is not.

Regenerate `FONT3D` with opentype.js against ChakraPetch-Bold if `NAME` ever
needs a letter that isn't in there.

## Edit points

Near the top of the `<script>`:

- `NAME` — the two hero lines
- `CELLS` — the info block printed bottom-right on the sheet
- `REEL` — carousel slides
- `GRID` — unit, inset, cell counts
- `HEAD` — how far in the coordinate readout sits, and the gap to the wordmark
- `ROLL` — tube thickness range
- `TOUR` — walkthrough length, extrusion depth, rest offset, view segments,
  camera dolly keyframes

## The portrait (About)

Portrait left, copy right, spanning the full page width. `img/leon.jpg` is not
placed as an image: it is downsampled to **one sample per grid cell**, then
painted back as 9px tiles on the 11px pitch — the cursor's exact geometry — so
it reads as the background grid lit up, and dissolves cell by cell into that
grid at its edges rather than stopping at a frame.

Everything in the `FACE` constant exists to make a face survive being reduced
to ~45 cells across. Each was necessary; removing any one visibly breaks it:

- **`greenKey`** — the subject is a head against out-of-focus foliage, and
  foliage is almost exactly as dark as hair. Luminance alone merges them into
  one silhouette-less rectangle. They are far apart in *hue*, so green cells
  are dropped outright.
- **`sharpen`** — averaging down to 45px destroys eyes and mouths: small dark
  features surrounded by light ones average to the background. An unsharp pass
  **on the cell grid** puts that contrast back. Without it the face has no eyes.
- **auto-levels** (`clip`) — computed from the **subject only**. Leave the keyed
  foliage in the histogram and it owns one end, the stretch becomes a no-op,
  and the face stays squashed into a corner of the range.
- **`sat` / `tint`** — greyscale pulled toward `--navy`. Full colour fights a
  page built from five blues; a straight palette duotone loses the eyes again,
  because the hue differences carry more of the face than they appear to.
  `sat: 1` restores the photograph's own colour.

A tuning change is one constant — but check it against the real photo, not by
reasoning about it. The failure mode is a navy blob that looks plausible in
code review.

The tiles are live under the pointer: `draw()` computes them, `paint()`
renders them at sprung offsets, and a repulsion field around the cursor shoves
nearby tiles off their cells — a spring pulls each one home. The displacement
is the whole interaction: tiles keep their own colour. The rAF loop runs
only while the pointer is near the portrait or energy remains, and on sleep
the offsets are zeroed so the tiles sit exactly back on the grid. Skipped on
coarse pointers and under reduced motion.

The image must be same-origin or `getImageData` taints the canvas and the
portrait removes itself. Missing file → the canvas removes itself too and the
placeholder frame shows, exactly as the project plates behave.

## Traps that have already bitten

- **`vh` vs `svh`** — mobile `vh` is measured with the URL bar hidden, but
  `clientHeight` is the height right now. Use `svh` for the stage, and read the
  height fresh (`vhNow()`) every frame in `update()`, taking the **max** of
  `clientHeight` and `innerHeight` (iOS reports both, differently, mid-scroll).
- **`background:` shorthand on `.content`** would reset `background-image` and
  wipe the page grid. Only ever set the longhand you mean.
- **Mobile resize storms** — mobile browsers fire `resize` every time the URL
  bar slides. `update()` ignores height-only resizes on coarse pointers.
- **Positioned children eat clicks** — `.island .grid/.wear/.noise` are
  absolutely positioned and paint above in-flow content, so they need
  `pointer-events:none` or the menu becomes unclickable while looking fine.
- **Stacked `drop-shadow` on a per-frame `clip-path`** (the corner peel) is the
  most expensive thing on the page. Three shadows on mobile, four on desktop.
- **Five folders is four too many.** Each `.doss` is a sheet wider and taller
  than the screen, carrying a `mix-blend-mode` grain layer and a video. All
  five exist for the whole Work section, so the browser was compositing five
  oversized blended layers and decoding five videos on every scroll frame —
  which is what made the projects section stutter. `update()` now culls: a
  folder that is faded out, still below the fold, or buried under a landed
  sheet gets `visibility:hidden` and its videos paused. Worst case three
  folders live, average two. The burial test compares against the **top of the
  viewport**, not against the folder's own `y` — once a folder has climbed
  away both numbers are off-screen and comparing them says it is still showing.
- **`visibility` is inherited, and a child can undo it.** `.pl-slide.on` used to
  set `visibility:visible`, which reappears inside a `visibility:hidden`
  ancestor — so a culled folder still painted its carousel image, left hanging
  over whatever you had scrolled to. It is `visibility:inherit` now. Anything
  that has to disappear with a culled folder must inherit, not assert.
- **Never call `getBoundingClientRect()` inside the scroll loop** if the number
  can be arithmetic. The last sheet's foot used to be measured every frame,
  which is a forced layout every frame; it is now `y + tabH + M.faceH`, with
  `faceH` read once per `measure()`. `update()` also caches the last transform,
  opacity and visibility it wrote per folder and skips unchanged writes.

## Conventions

- Comments explain **why**, not what. This file is dense and the reasoning is
  the only thing that makes it maintainable — match that density.
- Respect `prefers-reduced-motion`: the 3D canvas, dimensions, view label and
  and the corner peel all switch off, and the page still reads.
- Respect `pointer: coarse`: no hover anywhere is load-bearing. The corner peel
  becomes a drag, the custom cursor is hidden, the menu collapses to a burger.
- No build step, no framework, no npm. Keep it that way unless there's a
  reason worth the cost.
