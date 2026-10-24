#!/usr/bin/env python3
"""
tools/trace_art.py  --  makes a notebook's art.svg from its source picture
=========================================================================

Run:  python3 tools/trace_art.py notebooks/02-apple-tree
      (or with no argument: every notebook folder in notebooks/)
Needs: pip install pillow numpy potracer   (potracer = pure-Python potrace)

WHERE THE PICTURES COME FROM
  Each notebook folder has ONE picture in source/ (png or jpg): Eric's
  illustration for that cover, made with Google Gemini. It is used AS IT IS:
  the whole picture, no crop, nothing removed.

TWO LAYERS: BLACK AND COLOUR (2026-10-24)
  Most pictures are black only. Some have a few COLOURED parts too (First
  Snow's snowflakes are light blue). A plain black/white threshold would
  silently drop a light colour, so every pixel is sorted into one of three
  groups:
    * paper   light and grey-ish (white, or the faint grey of JPEG noise)
    * colour  clearly coloured: its strongest and weakest of R, G, B differ
              by at least COLOUR_SPREAD (white, grey and black all have
              R ~ G ~ B, so they never count as colour)
    * black   dark and not coloured
  Each group of ink (black, colour) is traced on its own and written as its
  own path. The colour path is filled with the MEDIAN colour of its pixels,
  so it matches the picture without anyone typing a colour in. A picture
  with no coloured pixels simply gets no colour layer.

WHAT THE SCRIPT DOES, STEP BY STEP
  1. Loads the picture in RGB.
  2. Resizes it so its height is about TARGET_HEIGHT pixels (small pictures
     are enlarged, which gives smoother curves than tracing their jagged
     pixels; very large ones are reduced, which keeps the SVG small).
  3. Sorts the pixels into black / colour / paper (above).
  4. Traces each ink group into Bezier curves with potrace (the classic
     bitmap-to-vector tracer). TURDSIZE drops specks smaller than that many
     pixels (JPEG noise); ALPHAMAX sets how round the corners are.
  5. Writes art.svg: one path per group, with the "evenodd" fill rule, so
     the white details INSIDE shapes (leaves, coat folds, the lamp's panes)
     stay as holes and show the paper through.

The result is pure vector, so it prints sharp at any size.
"""

import sys
from pathlib import Path

import numpy as np
import potrace
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TARGET_HEIGHT = 3000               # trace at about this many pixels tall
THRESHOLD = 128                    # black ink: darker than this (0..255)
COLOUR_SPREAD = 40                 # colour ink: max(R,G,B) - min(R,G,B) >= this
TURDSIZE = 60                      # ignore specks smaller than this (pixels)
ALPHAMAX = 1.1
INK = "#1a1a1a"                    # the colour used for the black layer


def to_path(mask: np.ndarray) -> tuple[str, int]:
    """Trace a boolean mask (True = ink) and return (SVG path data, shapes).

    potracer's Bitmap traces the pixels that are FALSE (its convention is the
    opposite of what one expects), so we hand it the paper, not the ink.
    potrace curves start at start_point and are made of segments (points
    have .x and .y) that are either corners (two straight lines via point c)
    or cubic Beziers (control points c1, c2)."""
    paths = potrace.Bitmap(~mask).trace(turdsize=TURDSIZE, alphamax=ALPHAMAX)
    d = []
    for curve in paths:
        p = curve.start_point
        d.append(f"M{p.x:.1f} {p.y:.1f}")
        for seg in curve.segments:
            e = seg.end_point
            if seg.is_corner:
                d.append(f"L{seg.c.x:.1f} {seg.c.y:.1f}L{e.x:.1f} {e.y:.1f}")
            else:
                d.append(f"C{seg.c1.x:.1f} {seg.c1.y:.1f} {seg.c2.x:.1f} {seg.c2.y:.1f} "
                         f"{e.x:.1f} {e.y:.1f}")
        d.append("Z")
    return "".join(d), len(paths)


def trace(folder: Path) -> None:
    pics = sorted(p for p in (folder / "source").iterdir()
                  if p.suffix.lower() in (".png", ".jpg", ".jpeg"))
    if len(pics) != 1:
        sys.exit(f"{folder}: expected exactly one picture in source/, found {len(pics)}")
    img = Image.open(pics[0]).convert("RGB")
    w, h = img.size
    k = TARGET_HEIGHT / h
    W, H = round(w * k), round(h * k)
    rgb = np.array(img.resize((W, H), Image.LANCZOS)).astype(int)

    # Sort the pixels (see TWO LAYERS above).
    spread = rgb.max(axis=2) - rgb.min(axis=2)       # 0 for any grey
    grey = rgb.mean(axis=2)
    colour = spread >= COLOUR_SPREAD
    black = (grey < THRESHOLD) & ~colour

    layers = []                                      # (path data, fill colour)
    d, n_black = to_path(black)
    layers.append((d, INK))
    n_colour = 0
    if colour.sum() > TURDSIZE:
        r, g, b = np.median(rgb[colour], axis=0).astype(int)
        d, n_colour = to_path(colour)
        layers.append((d, f"#{r:02x}{g:02x}{b:02x}"))

    out = folder / "art.svg"
    out.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">'
        + "".join(f'<path d="{d}" fill="{c}" fill-rule="evenodd"/>' for d, c in layers)
        + "</svg>\n", encoding="utf-8")
    extra = f" + {n_colour} in {layers[1][1]}" if n_colour else ""
    print(f"{out.relative_to(ROOT)}: {n_black} black shapes{extra}, "
          f"{out.stat().st_size // 1024} KB")


def main():
    folders = [Path(a).resolve() for a in sys.argv[1:]] or \
        sorted(p for p in (ROOT / "notebooks").iterdir() if (p / "source").is_dir())
    for folder in folders:
        trace(folder)


if __name__ == "__main__":
    main()
