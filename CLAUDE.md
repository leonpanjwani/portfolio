# leonpanjwani.com

A single-file, no-build personal engineering portfolio. `index.html` holds the
markup, all the CSS and all the JS. Deployed on **Cloudflare Pages**, which
serves the repo root as-is — pushing to `main` on GitHub is the deploy.

```
index.html         everything
vendor/three.min.js  three.js r128, vendored — see below
cv.pdf             linked from About
favicon.png
img/leon.jpg       the About portrait (900×900, same-origin — see below)
img/               the project and carousel images — WebP, mostly (see below)
.claude/serve.py   local dev server
```

**three.js is vendored, not fetched.** It used to come from cdnjs. It was the
only thing the page needed from someone else's server, and it is the thing the
whole opening rests on: no `THREE` means no WebGL name, which means no exploded
assembly and no dimensions — the page falls back silently to the flat 2D name.
Every slow or blocked cdnjs response was an intro that "didn't load". Keep it in
the repo. Cloudflare Pages serves it same-origin, with no third-party DNS or TLS
handshake ahead of the first frame.

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

Three deliberate offsets exist, all whole (or half) squares so nothing leaves
the lattice:

| token | where | what |
|---|---|---|
| `--lift` | `.doss-in` | half a square UP, so a folder's contents sit a little above dead centre of the sheet |
| `--sklUp` | `.skl-wrap` | one square UP, pinned layouts only — a relative offset moves the paint, not the box, so on a phone it would print over the folder above |
| `margin-right` | `.about-copy` | one square LEFT, off the gutter edge; a margin rather than a transform, so the copy stays in flow and both its edges stay on lines |

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

Type: `--display` (Chakra Petch) is the drawing face — the hero, the section
headings, the header wordmark, the folder tabs **and the nav**. `--body` (Inter)
is prose. `--mono` (Share Tech Mono) is instrumentation: the readout, the tags,
the captions. The nav was set in Rokkitt, a slab serif, which was a second voice
on a page that only has one; it is cut from the tab labels' face now and set
exactly as one is: 700, 0.92rem, uppercase, .13em of tracking. At that size the
caps are signage rather than prose, which is what a nav is, and it matches the
labels on the files it points at. The shortcut panel follows it a step smaller.
Only the weights the
stylesheet actually sets are requested in the font link: ask for one nothing
uses and it costs a download, set one nothing asked for and the browser
synthesises it and the letterforms change shape.

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

**A canvas has two sizes and nothing keeps them in step.** The BITMAP
(`cv.width/height`, what `draw()` paints into) and the BOX (CSS, `width:100%` of
a square column) are independent: CSS stretches whatever bitmap is there to fill
whatever box there is. An undrawn canvas has a bitmap of 300×150, so before the
first successful draw the portrait is a 300×150 image stretched into a 550px
square — and if a draw ever fails afterwards, the last bitmap is stretched into
the new box. Nine-pixel tiles on an eleven-pixel pitch stop being either. That
is the portrait "invisible, or the wrong size and out of position".

`draw()` has three ways to quietly do nothing — the photo has not decoded, the
box has not been laid out, `getImageData` threw on a tainted canvas — and the
IntersectionObserver that started it used to disconnect after the first attempt,
so there was nothing left to try again. It stays connected now, and `sync()`
compares the BITMAP against the BOX (not the box against the box) on every
arrival, twice a second while the portrait is near the screen, and on
`visibilitychange`. A browser may throw a canvas's backing store away at any
time — a backgrounded tab, memory pressure, a GPU process restart — and nothing
tells you when it has. A canvas is not storage.

The tiles are live under the pointer: `draw()` computes them, `paint()`
renders them at sprung offsets, and a repulsion field around the cursor shoves
nearby tiles off their cells — a spring pulls each one home. The displacement
is the whole interaction: tiles keep their own colour. The rAF loop runs
only while the pointer is near the portrait or energy remains, and on sleep the
offsets are zeroed so the tiles sit exactly back on the grid. `paint()` used to
run a `fillRect` for every tile — about two thousand of them — on every frame,
in order to move the handful actually near the pointer. The resting portrait is
baked once into an off-screen canvas (`renderStill`) and blitted as a single
image; only the tiles in `moved` are lifted off their cells and set down again,
in two passes, because a displaced tile can land on another displaced tile's
home cell. Skipped on
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
- **A landed sheet is not rotated, it is moved.** A `rotate()` makes the browser
  RE-RASTER the layer every frame; a pure `translate()` only moves an existing
  raster on the compositor. A folder is about 1.34 screens in both directions —
  roughly fourteen million device pixels at 2x — and up to three are live at
  once, so this is the most expensive rasterisation on the page. A folder is
  only tilted while it is actually swinging; for the whole of the rest of its
  life the angle rounds to zero, and emitting `rotate(0.00deg)` anyway kept
  every landed sheet on the expensive path for nothing. `update()` omits the
  rotate below 0.01°.
- **A pointer move is not a scroll.** `mousemove` used to call `onScroll()`,
  which ran the whole scroll pipeline — clip-path, roll, header inks, five
  folder transforms, the skills fades — because the cursor had moved eleven
  pixels. Pointer state (the grid cursor, the corner peel) is `updatePointer()`
  now, on its own rAF gate. `update()` still calls it, because the page moving
  under a stationary pointer changes which cell it is in; the reverse is no
  longer true.
- **Writing a style property its current value is not free.** It invalidates the
  element's computed style, and for a `clip-path` on a full-viewport fixed layer
  it can cost a screen repaint. Everything written per frame goes through `wr()`
  / `wrv()`, which hold the last value written per key and skip the write when
  nothing moved.
- **`offsetTop` and `getBoundingClientRect()` FLUSH LAYOUT.** `content.offsetTop`
  was read on every scroll frame and every pointer move for a number that only
  changes when the sections are re-padded; it is `travelNow()` now, cached and
  invalidated by `measure()` and `lockGrid()`. The portrait was measuring its
  own canvas every animation frame and on every mouse move, for the same reason.
- **A skip gesture has to be a gesture.** Any wheel event at all used to end the
  opening animation, and a trackpad does not send one wheel event — it sends a
  stream, including the tail of the momentum from before the reload. A 2px drift
  was cutting the intro off. `SKIP_GRACE` (nothing counts for the first 420ms)
  and `SKIP_DY` (a wheel has to be a push, not a drift) fix it between them —
  and the SKIP listeners must NOT be `{once:true}`, because an event
  deliberately ignored would spend the listener and the real gesture would then
  never arrive.
- **`document.fonts.ready` is a promise on someone else's server.** The hero is
  SIZED from the font's own metrics, so it is the right thing to wait for — but
  if the font host is slow the reader sits on an empty blueprint until it
  answers. `boot()` races it against a 1.2s deadline and re-measures if the face
  lands late.
- **What is printed on the sheet travels with the sheet.** `.doss-in` carried a
  `--cy` counter-climb, equal and opposite to the parallax, so the contents held
  still on screen while the paper moved under them. It read as a bug rather than
  as depth. Gone. How far a project rides before the next file covers it is
  `DOSS.par` × `DOSS.step` — 0.68 × 0.55, about a third of a screen. Lower `par`
  if a project should stay readable for longer.
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
  tile carries the fine grain and the coarse mottle. Measured on the shipped
  file: mean transmission **0.9816**, sd 0.0074, range 0.965–1.000 — at most a
  3.5% darkening, which is the "nothing you can pick out at arm's length" it is
  meant to be.
- **And the multiply is baked, not computed.** `background-blend-mode: multiply`
  is far cheaper than `mix-blend-mode` (it never reads the backdrop) but it is
  not free: it is recomputed every time the layer rasters, and these layers run
  to about 9.5 million device pixels each with up to three live. The multiply is
  arithmetic that never changes, so it is done offline — `img/stock-*.png`, one
  tile per stock with the grain already multiplied into its own colour, selected
  by `--stock-grain` alongside `--stock`. The blend is gone and the paint is a
  plain image tile, which is the cheapest thing a background can be.
  `img/grain.png` stays as the master; regenerate all five if a stock colour
  changes. `background-color` stays underneath as the fallback, so a folder
  whose tile fails to load is flat paper rather than no paper.
- **One ink mask per block, not one per element.** `--ink-mask` used to name
  five selectors, which came to **39 separately masked elements** across the
  five folders — every heading, tag line, paragraph and link its own masked
  layer, inside sheets that raster whenever they move. `.doss-ink` is a wrapper
  built in script around the heading, the tags and the paragraphs; the mask goes
  on that, so the ink runs continuously down the block instead of restarting at
  every paragraph — which is what a real press does anyway. 39 down to 19.
  **`.plate-links` is deliberately left outside it:** a mask CLIPS its element
  to the border box, and the link-preview cards are absolutely positioned and
  hang below theirs. Mask any ancestor of those cards and they are cut off.
- **A square sized from the width lives in a box sized from the height.** The
  project plate is `aspect-ratio: 1` at 95% of its COLUMN — half the viewport
  width — inside a row whose height comes from `--contentH`, which is solved
  from the viewport HEIGHT. Past about a 2:1 window those two disagree: the
  square comes out taller than the row, and the face clips, so the top and
  bottom of every picture were cut off. It reads as the images having stopped
  responding to the window; in fact they were responding to one axis of it.
  `measure()` publishes `--plateMax` — the content area less its own padding
  and the plate's margins — and the plate takes `min(95%, var(--plateMax))`.
  Because a square's height IS its width, a max on the width is what caps the
  height. The browser-window plate is not square (a 38px chrome bar over a 16:10
  shot, plus 1px of border each side), so its cap is `1.6 × (plateMax − 40px)`.
  Below 2:1 the column is still the smaller of the two and NOTHING changes —
  verified identical at 1440×900, 1512×982, 1680×1050, 1920×1080, 2560×1440.
- **Images are WebP — except three that are not.** Re-encoding is only a saving
  if the source has headroom. `efw`, `eyh` and `pv-eyh-presentation` are already
  such aggressive JPEGs that WebP has to spend bits reproducing their own
  artefacts, and comes out 3–17% BIGGER. Each file is whichever format is
  actually smaller; the mix is deliberate, not an oversight. Five files that
  were being served far larger than they are ever displayed were also capped at
  1400px on the long side. 2408 KB → 1587 KB, at ≥42 dB PSNR against the
  original, which is visually indistinguishable. `img/grain.png` and the
  `stock-*.png` tiles stay PNG: they are flat, few-colour images, and lossless
  WebP is *larger* than a palette PNG for those.
- **`--ovY` is a skirt, and it was nearly half margin.** It has to cover the
  climb a landed sheet makes before the next lands on it — `par × step` = 0.374
  of a screen, plus the tab, about 376px at 1440×900. It was 558px. It is 420px
  now. Do not reason about this one: a sweep of the whole Work section at every
  scroll step, counting bare-page pixels anywhere on screen, is the way to check
  it — that sweep is clean at half the current value, and a control with no
  skirt at all lights up with thousands of exposed pixels. Between the two
  trims a folder face is 1668×1280 rather than 1794×1419: 8.5 megapixels at 2x
  instead of 10.2, none of which was ever visible.
- **`DOSS.rise` and `--ovX` are one number.** The overhang needed to keep a
  tilted corner out of shot is `1.3 × screen height × tan(rise)`. At 7° that is
  0.16 of a screen; at 4° it is 0.091. Change one without the other and either a
  corner swings into view or you are paying to raster sheet nobody can see. It
  is 4° now — still plainly paper being swung up, with 43% less overhang.
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
