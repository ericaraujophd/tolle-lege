#!/usr/bin/env python3
"""
tools/trace_art.py  --  makes a notebook's art.svg from its source picture
=========================================================================

Run:  python3 tools/trace_art.py notebooks/02-apple-tree
      (or with no argument: every notebook folder in notebooks/)
Needs: pip install pillow numpy potracer   (potracer = pure-Python potrace)

WHERE THE PICTURES COME FROM
  Each notebook folder has ONE picture in source/ (png or jpg): Eric's
  black-and-white illustration for that cover, made with Google Gemini.
  It is used AS IT IS: the whole picture, no crop, nothing removed.

WHAT THE SCRIPT DOES, STEP BY STEP
  1. Loads the picture as greyscale.
  2. Resizes it so its height is about TARGET_HEIGHT pixels (small pictures
     are enlarged, which gives smoother curves than tracing their jagged
     pixels; very large ones are reduced, which keeps the SVG small).
  3. Threshold: every pixel darker than mid-grey becomes ink.
  4. Traces the ink into Bezier curves with potrace (the classic bitmap-to-
     vector tracer). TURDSIZE drops specks smaller than that many pixels
     (JPEG noise); ALPHAMAX sets how round the corners are.
  5. Writes art.svg: one path in the ink colour with the "evenodd" fill
     rule, so the white details INSIDE the black shapes (leaves, coat
     folds) stay as holes and show the paper through.

The result is pure vector, so it prints sharp at any size, and it is one
ink colour, so it prints cleanly on kraft or stone.
"""

from pathlib import Path

import numpy as np
import potrace
from PIL import Image

import sys

ROOT = Path(__file__).resolve().parent.parent
TARGET_HEIGHT = 3000               # trace at about this many pixels tall
THRESHOLD = 128                    # 0 black .. 255 white; darker = ink
TURDSIZE = 60                      # ignore specks smaller than this (pixels)
ALPHAMAX = 1.1
INK = "#1a1a1a"


def trace(folder: Path) -> None:
    pics = sorted(p for p in (folder / "source").iterdir()
                  if p.suffix.lower() in (".png", ".jpg", ".jpeg"))
    if len(pics) != 1:
        sys.exit(f"{folder}: expected exactly one picture in source/, found {len(pics)}")
    img = Image.open(pics[0]).convert("L")
    w, h = img.size
    k = TARGET_HEIGHT / h
    W, H = round(w * k), round(h * k)
    img = img.resize((W, H), Image.LANCZOS)
    ink = np.array(img) < THRESHOLD                 # True where there is ink

    # potracer's Bitmap traces the pixels that are FALSE (its convention is the
    # opposite of what one expects), so we hand it the paper, not the ink.
    paths = potrace.Bitmap(~ink).trace(turdsize=TURDSIZE, alphamax=ALPHAMAX)

    # Build one SVG path. potrace curves start at start_point and are made of
    # segments (points have .x and .y) that are either corners (two straight
    # lines via point c) or cubic Beziers (control points c1, c2).
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

    out = folder / "art.svg"
    out.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">'
        f'<path d="{"".join(d)}" fill="{INK}" fill-rule="evenodd"/></svg>\n',
        encoding="utf-8")
    print(f"{out.relative_to(ROOT)}: {len(paths)} shapes, {out.stat().st_size // 1024} KB")


def main():
    folders = [Path(a).resolve() for a in sys.argv[1:]] or \
        sorted(p for p in (ROOT / "notebooks").iterdir() if (p / "source").is_dir())
    for folder in folders:
        trace(folder)


if __name__ == "__main__":
    main()
