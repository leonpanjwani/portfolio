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
- **`mix-blend-mode` is a backdrop read; `background-blend-mode` is not.** The
  folder grain used to be a blended pseudo-element, which forced a sheet 2.35×
  the screen into its own composited group every frame. It is now a single
  tile multiplied into the stock by the face and tab themselves.
- **The grain is a baked PNG (`img/grain.png`), not turbulence.** Two attempts
  at doing it live both went wrong in the same way: `feTurbulence` writes an
  **alpha** channel as well as colour, so a filter tuned as if it produced
  opaque grey lands at about half the intended weight — and one written
  straight into alpha is a flat black wash with no grain in it at all. The
  tile carries the fine grain and the coarse mottle at the transmission the
  original two-layer version worked out to: `0.745 + 0.17·fine + 0.085·mottle`,
  mean **0.8725**. Multiply, so each stock keeps its own hue. Regenerate at
  that mean if it ever needs redoing.
- **`visibility` is inherited, and a child can undo it.** `.pl-slide.on` used to
  set `visibility:visible`, which reappears inside a `visibility:hidden`
  ancestor — so a culled folder still painted its carousel image, left hanging
  over whatever you had scrolled to. It is `visibility:inherit` now. Anything
  that has to disappear with a culled folder must inherit, not assert.
- **A `backdrop-filter` does not compound through a nested one.** The mobile
  drawer is glass; the Projects sub-list inside it was reading as a solid white
  slab because the mobile block reset the desktop popover's `padding`, `border`
  and `box-shadow` but not its `background`. The fix is `background:transparent`,
  not a second `backdrop-filter` on the sub-list: the filter blurs what has
  *already been painted behind* the element, which by then is the drawer's own
  blurred result — so nesting one costs a second full-screen pass per frame and
  looks identical. Inherit the glass; don't restate it.
- **The phone layout's glass is ONE material, `--glass` / `--glassfx` on
  `:root` inside the mobile block.** The drawer, its sub-list and the header bar
  are the same sheet; a value written out three times is a value that ends up
  different in two of them.
- **The drawer's white is an alpha/blur trade, and the numbers came from
  measurement.** Alpha is how much of the page is hidden; blur is how legible
  whatever still shows through is. Opened at fourteen positions down the page,
  the tomato labels' worst backdrop is a navy folder header, and the contrast
  against it goes `.86`+`blur(18px)` → **2.3:1**, `.79`+`blur(26px)` → **2.0:1**,
  the current `.72`+`blur(34px)` → **1.8:1**. Raising the blur alongside the
  alpha is what makes that survivable: what hurts small type is a *structured*
  backdrop more than a dark one, and at 34px there is no structure left. If this
  is retuned again, re-run the sweep — the average backdrop is not the one that
  breaks, and a white section will tell you everything is fine.
- **Two sheets of glass overlapping is a bright patch, not a thicker sheet.**
  `.72` over `.72` composites to `.92`. The header bar therefore stops at the
  drawer's left edge while the drawer is out (`#layer:has(#menu.open)`), so the
  two TILE the top edge rather than stack — measured, the drawer's top strip
  reads 219 against its own body's 210 with the inset, and 236 without it.
- **The header bar rides on the header's own published motion.** `update()`
  publishes the islands' ride as `--hdrop` and their fade as `--hop`;
  `measure()` publishes the size of the ride as `--hdropMax`. The bar wears the
  same transform and is extended UPWARDS by exactly `--hdropMax`, so its bottom
  edge tracks the wordmark at every point of the arrival (measured: a constant
  2px clearance at every scroll position) and its top edge is never on screen.
  A bar at a fixed height would have had the wordmark hanging out of the bottom
  of it for the whole animation. Nothing is timed against anything.
- **One edge moved by `clip-path`, another by `transform`, is how the roll and
  the paper come apart.** clip-path needs a repaint; a transform does not, so the
  compositor is free to present the tube in its new position over a stale raster
  of the sheet, and under a fast scroll the paper's edge trails the roll. Both
  are written from the same `rollY` in the same frame, so no amount of staring at
  the JS finds it. `#roll` is driven by `top` for this reason: a layout property
  puts it in the same commit as the clip. Do not "optimise" it back to a
  transform.
- **Measuring this needs a majority, not a sample.** Three attempts to detect the
  fault from pixels all failed, each by trusting one pixel: the LAST blue row on
  screen finds a navy folder tab further down the page; the FIRST non-blue row
  finds a ruler tick 23px in; a row-majority scan that stops at the first
  non-blue row stops at the frame line. Score whole rows and keep going.

- **`headTop` is 0 on the phone and `U` on desktop, and everything else
  follows from it.** On desktop the islands float a cell down from the top —
  the inset is what makes them read as objects ON the page rather than as
  chrome. On the phone the glass behind them IS a bar, and a bar is attached to
  the edge it runs along; the cell of inset was making it 66px tall to hold
  21px of ink. At 0 it is exactly one square, 55px, with the ink centred (16
  above, 18 below). `--headZ`, the ride distance `--hdropMax`, the bar's height
  and its overhang are all derived from it, so that one line is the whole
  change — resist adding a second number for the bar.
- **DOM order, not z-index, puts the bar under the islands.** `#hdrglass` is
  first in `#layer`; the islands after it are positioned, and positioned
  elements paint above in-flow siblings.
- **The header is inert over the hero.** `#menu` carries `pointer-events:none`
  and `#stage` paints over it for roughly the first quarter of the page, so any
  test that opens the drawer must skip those positions (or assert, and discover
  it the hard way as this one did).

- **Never call `getBoundingClientRect()` inside the scroll loop** if the number
  can be arithmetic. The last sheet's foot used to be measured every frame,
  which is a forced layout every frame; it is now `y + tabH + M.faceH`, with
  `faceH` read once per `measure()`. `update()` also caches the last transform,
  opacity and visibility it wrote per folder and skips unchanged writes.

## Conventions

- **No em or en dashes anywhere in reader-facing copy.** Where one feels
  necessary the sentence usually wants a comma, a full stop, or a paired
  construction (`either… or…`).
- **No setup-then-payoff punctuation.** A colon or semicolon mid-sentence whose
  second half is the interesting bit reads as advertising rather than as a
  person talking: "We bid for it; 75,000 tonnes a year, 98% kept out of
  landfill" had no verb in it at all. Make the withheld thing the subject of an
  ordinary clause. It usually gets shorter.
- Every `.beat` ends with `&nbsp;` between its last two words, so a paragraph
  cannot strand one word on its own line in a narrow folder column.
- Comments explain **why**, not what. This file is dense and the reasoning is
  the only thing that makes it maintainable — match that density.
- Respect `prefers-reduced-motion`: the 3D canvas, dimensions, view label and
  and the corner peel all switch off, and the page still reads.
- Respect `pointer: coarse`: no hover anywhere is load-bearing. The corner peel
  becomes a drag, the custom cursor is hidden, the menu collapses to a burger.
- No build step, no framework, no npm. Keep it that way unless there's a
  reason worth the cost.
