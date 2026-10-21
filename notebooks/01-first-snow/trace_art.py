#!/usr/bin/env python3
"""
trace_art.py  --  makes art.svg, the silhouette for Notebook 01, First Snow
==========================================================================

Run:  python3 notebooks/01-first-snow/trace_art.py
Needs: pip install pillow numpy potracer   (potracer = pure-Python potrace)

WHERE THE PICTURE COMES FROM
  source/first-snow-gemini.png is a black-and-white illustration Eric made
  with Google Gemini (2026-10-20): a girl in a winter coat and pompom hat
  looking up into snow falling through the light of a street lamp. Eric
  asked for it to be used AS IT IS, so the whole picture is traced, with no
  crop and nothing removed (CROP = None, ERASE empty). To use part of a
  picture instead, set CROP to a box and list areas to paint out in ERASE.

WHAT THE SCRIPT DOES, STEP BY STEP
  1. Optionally crop the source (CROP, in pixels; None keeps it whole).
  2. Optionally paint out areas (ERASE boxes, in pixels; empty here).
  3. Enlarge 4x with smooth resampling. Tracing a bigger, smoother image
     gives smoother curves than tracing the small original's jagged pixels.
  4. Threshold: every pixel darker than mid-grey becomes ink.
  5. Trace the ink into Bezier curves with potrace (the classic bitmap-to-
     vector tracer). TURDSIZE drops specks smaller than that many pixels;
     ALPHAMAX sets how round the corners are (higher = smoother).
  6. Write art.svg: one path, filled with the ink colour, using the
     "evenodd" rule so the white highlights INSIDE the coat (its quilted
     folds, the hair strands) stay as holes and show the paper through.

The result is pure vector, so it prints sharp at any size, and it is one
ink colour, so it prints cleanly on kraft or stone.
"""
from pathlib import Path

import numpy as np
import potrace
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source" / "first-snow-gemini.png"
OUT = HERE / "art.svg"

CROP = None                        # None = the WHOLE picture, unchanged (Eric, 2026-10-20)
ERASE = []                         # nothing painted out
SCALE = 4                          # enlarge before tracing
THRESHOLD = 128                    # 0 black .. 255 white; darker = ink
TURDSIZE = 6 * SCALE * SCALE       # ignore specks smaller than this (pixels)
ALPHAMAX = 1.1
INK = "#1a1a1a"


def main():
    img = Image.open(SOURCE).convert("L")
    if CROP:
        img = img.crop(CROP)
    draw = ImageDraw.Draw(img)
    for box in ERASE:
        draw.rectangle(box, fill=255)
    w, h = img.size
    img = img.resize((w * SCALE, h * SCALE), Image.LANCZOS)
    ink = np.array(img) < THRESHOLD                 # True where there is ink

    # potracer's Bitmap traces the pixels that are FALSE (its convention is the
    # opposite of what one expects), so we hand it the paper, not the ink.
    paths = potrace.Bitmap(~ink).trace(turdsize=TURDSIZE, alphamax=ALPHAMAX)

    # Build one SVG path. potrace curves start at start_point and are made of
    # segments (points have .x and .y) that are either corners (two straight lines via point c) or
    # cubic Beziers (control points c1, c2).
    d = []
    for curve in paths:
        p = curve.start_point; x, y = p.x, p.y
        d.append(f"M{x:.1f} {y:.1f}")
        for seg in curve.segments:
            ex, ey = seg.end_point.x, seg.end_point.y
            if seg.is_corner:
                cx, cy = seg.c.x, seg.c.y
                d.append(f"L{cx:.1f} {cy:.1f}L{ex:.1f} {ey:.1f}")
            else:
                ax, ay, bx, by = seg.c1.x, seg.c1.y, seg.c2.x, seg.c2.y
                d.append(f"C{ax:.1f} {ay:.1f} {bx:.1f} {by:.1f} {ex:.1f} {ey:.1f}")
        d.append("Z")

    W, H = w * SCALE, h * SCALE
    OUT.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">'
        f'<path d="{"".join(d)}" fill="{INK}" fill-rule="evenodd"/></svg>\n',
        encoding="utf-8")
    print(f"art.svg written: {len(paths)} shapes, {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
