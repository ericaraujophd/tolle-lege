#!/usr/bin/env python3
"""
impose.py
=========

STEP 3 OF THE PIPELINE: arrange the booklet pages on letter paper so that,
after printing double-sided, cutting once, folding, nesting and sewing,
the pages come out in the right order.

This is called "imposition". It is the only genuinely tricky part of making a
booklet, so this file explains it in detail.


THE BIG PICTURE
---------------

Input:  a PDF of single pages at the FINAL size, 3.5 x 5 in, in reading
        order (the reading copy of a title, or its 4-page cover).

Output: a PDF of US Letter pages (8.5 x 11 in), meant to be printed
        DOUBLE-SIDED, "flip on LONG edge". Each letter sheet carries TWO
        identical copies of the same "spread", one above the other:

            8.5 in wide
          +-------------------+
          |                   |  <- 0.25 in waste (head)
          |   +-----+-----+   |  <- copy A: left page | right page
          |   |  L  |  R  |   |     (each 3.5 x 5 in, touching the fold)
          |   +-----+-----+   |
          |                   |  <- 0.25 in waste (foot)
          |- - - - - - - - - -|  <- CUT HERE (exactly half way, 5.5 in)
          |                   |  <- 0.25 in waste (head)
          |   +-----+-----+   |  <- copy B: identical
          |   |  L  |  R  |   |
          |   +-----+-----+   |
          |                   |  <- 0.25 in waste (foot)
          +-------------------+
              ^    ^    ^
              |  fold   |
          fore-edge   fore-edge (trimmed after binding)

        So one print run makes two complete booklets.

Why this layout?  The 7 x 5 in spread sits in the middle of a half-letter
(8.5 x 5.5). After the one cut across the middle, every half sheet is
8.5 x 5.5 in, and its centre line is the fold. Around each spread there is
waste: 0.75 in at each side and 0.25 in at the top and bottom. All of it is
trimmed AFTER sewing, with three cuts on the finished booklet
(fore-edge, head, foot). Trimming after binding hides any wobble from
printing, cutting and folding, which is why the page is never cut to size
before it is folded.


WHICH PAGES GO ON WHICH SHEET  (the saddle-stitch rule)
-------------------------------------------------------

A saddle-stitched booklet of N pages (N must be a multiple of 4) is made of
S = N / 4 sheets, each folded once and nested inside the previous one.
Number the sheets k = 0, 1, ..., S-1 from the OUTSIDE in. Pages are counted
from 1. Then sheet k carries:

    FRONT side:  left = N - 2k        right = 2k + 1
    BACK  side:  left = 2k + 2        right = N - 2k - 1

Example, N = 8 (two sheets):
    sheet 0 front: 8 | 1     sheet 0 back: 2 | 7
    sheet 1 front: 6 | 3     sheet 1 back: 4 | 5

Check it with a real piece of paper once: fold two sheets, nest them, number
the pages 1-8, unfold. You will see exactly the table above. The function
`check_order` below does the same thing in code and stops the script if the
rule were ever broken.

Why does the BACK side have the left/right pair it has?  Because "flip on
long edge" on a portrait page turns the paper over like a book page, around
its vertical centre line. What is on the right of the front ends up on the
left when you look at the back. Page 2 is the back of page 1, so it must sit
on the LEFT of the back side, directly behind page 1. The top and bottom stay
where they are with this kind of flip, so copy A stays on top on both sides.


PRINTING INSTRUCTIONS (also in the README)
------------------------------------------
* Print at 100% / "Actual size". NEVER "fit to page": scaling would break the
  measurements.
* Double-sided, flip on LONG edge.
* Interior on text paper; cover on kraft cardstock (cover_print.pdf).


MARKS PRINTED ON THE SHEET
--------------------------
All marks sit in waste that is cut off, so none shows in the finished book.
On the FRONT side of each sheet only (the back would be shifted by the
printer correction and disagree):
* CUT: a dashed line across the whole sheet at 5.5 in, labelled "cut".
* FOLD: a short solid tick on the centre line next to the cut, labelled "fold".
* TRIM: thin unlabelled ticks at the finished page edges (fore-edges, head,
  foot), to check the cutter's back gauge setting on the first booklet.
On both sides:
* A small, grey label naming the sheet ("sheet 3 of 6, front"). Keep the
  stack in order using these labels.
TRIM_MARKS = False prints the labels only.

Normally you do not run this file yourself: the top-level build.py imports it
and calls impose() for every title. It still works on its own:
    python3 tools/impose.py reading.pdf interior.pdf --label "No. 01 interior"
    python3 tools/impose.py --test alignment-test.pdf     (duplex alignment check)
"""

import argparse
import io
import sys

from pypdf import PdfReader, PdfWriter, Transformation, PageObject
from reportlab.lib.colors import Color
from reportlab.pdfgen import canvas

# ---------------------------------------------------------------- geometry
# PDF units are "points": 72 points = 1 inch. Every measurement below is
# written in inches and multiplied by IN, so you can read it as inches.
IN = 72.0

SHEET_W = 8.5 * IN   # US Letter, portrait
SHEET_H = 11.0 * IN
PAGE_W = 3.5 * IN    # final booklet page
PAGE_H = 5.0 * IN

FOLD_X = SHEET_W / 2          # the fold is the vertical centre of the sheet
CUT_Y = SHEET_H / 2           # the cut is the horizontal centre of the sheet
# Each half sheet is 5.5 in tall and each page 5 in, so 0.5 in is left over.
# We split it evenly: 0.25 in of waste above and below each copy (HEAD_FOOT).
# Bottom edge of each copy: copy B (lower half) starts 0.25 in above the paper
# edge; copy A (upper half) starts 0.25 in above the cut line.
HEAD_FOOT = (CUT_Y - PAGE_H) / 2          # = 0.25 in
COPY_Y = {"A": CUT_Y + HEAD_FOOT, "B": HEAD_FOOT}

# ------------------------------------------------- printer offset correction
# Many printers do not put the back side exactly behind the front (1-2 mm off
# is common). We measure the error once with alignment_test.pdf and cancel it
# by printing the back side slightly moved the other way.
#
# HOW TO MEASURE: print alignment_test.pdf, hold it to a window with the FRONT
# side facing you, and read where the BACK crosshair sits compared with the
# front one (ticks are 1 mm apart):
#     dx = mm to the RIGHT (negative if to the left)
#     dy = mm UP           (negative if down)
# Put those two numbers in PRINTER_OFFSET_MM (or pass --back-offset DX DY).
#
# The default is NO correction, (0, 0): the files on the website must work on
# anyone's printer, and most printers are within a millimetre or two.
# For your own printer, measure once and pass the numbers to the build:
#     python3 build.py --back-offset DX DY      (writes into build/, not docs/)
# Example: the Calvin CS department printer, measured 2026-10-02, put the back
# crosshair 2 mm to the right and 1 mm up, so it uses --back-offset 2 1.
PRINTER_OFFSET_MM = (0.0, 0.0)

# The small centre crosshair (section 2c of marks_overlay) helped diagnose
# printer drift. It is off for normal printing.
REGISTRATION_MARK = False

# Cut, fold and trim marks (see marks_overlay for what each looks like).
# Printed on the FRONT side of each sheet only. Redesigned 2026-10-14 after
# the first version proved misleading:
#   * its cut ticks sat only at the far left and right edges, so trimming the
#     sides first removed them; the cut is now a dashed line across the whole
#     sheet;
#   * the cut tick and the head/foot ticks looked alike and sat 1/4 in apart;
#     now the cut is dashed and labelled, the fold is labelled, and the trim
#     ticks are short plain hairlines;
#   * the back side carried its own marks, shifted by PRINTER_OFFSET_MM; now
#     only the front has marks.
# Set to False to print the sheet labels only.
TRIM_MARKS = True


def back_correction(offset_mm):
    """Turn an offset AS SEEN FROM THE FRONT into the move we apply to the
    back side's content, in PDF points, in the back page's own coordinates.

    Vertical: a long-edge flip keeps top as top, so if the back prints 1 mm
    too high we simply draw its content 1 mm lower: dy_pdf = -dy.

    Horizontal (the tricky one): a long-edge flip turns the sheet over like a
    book page, so left and right swap between the two sides. When you look
    through the paper from the front, a mark that the printer put too far to
    the LEFT on the back (in the back's own view) shows up too far to the
    RIGHT. So "2 mm to the right, seen from the front" means the printer moved
    the back content 2 mm to the left in its own frame, and we correct it by
    drawing the back content 2 mm to the RIGHT in its own frame:
    dx_pdf = +dx. (Same sign as seen, which feels backwards but is right.)
    """
    dx_mm, dy_mm = offset_mm
    mm = IN / 25.4
    return dx_mm * mm, -dy_mm * mm

MARK_GREY = Color(0.35, 0.35, 0.35)
# The trim crosses are lighter, so a sliver left by a slightly-off cut barely shows.
FRAME_GREY = Color(0.5, 0.5, 0.5)


# ------------------------------------------------------------ the page order
def sheet_layout(n_pages):
    """Return a list with one entry per sheet:
        [(front_left, front_right), (back_left, back_right)], ...
    Page numbers are 1-based, exactly as in the docstring table."""
    if n_pages % 4 != 0:
        sys.exit(f"Page count {n_pages} is not a multiple of 4. "
                 "build.py pads the book with notes pages; use it.")
    sheets = []
    for k in range(n_pages // 4):
        front = (n_pages - 2 * k, 2 * k + 1)
        back = (2 * k + 2, n_pages - 2 * k - 1)
        sheets.append((front, back))
    return sheets


def check_order(sheets, n_pages):
    """Simulate the finished booklet and confirm the reading order is 1..N.

    Reading a nested, folded booklet from front to back you meet, for each
    sheet from the outside in, its front-right page then its back-left page;
    after the centre spread you come back out, meeting each sheet's back-right
    page then its front-left page, from the inside out."""
    order = []
    for front, back in sheets:                 # going in
        order += [front[1], back[0]]
    for front, back in reversed(sheets):       # coming back out
        order += [back[1], front[0]]
    if order != list(range(1, n_pages + 1)):
        sys.exit(f"Imposition self-check failed: {order}")


# ---------------------------------------------------------------- the marks
def marks_overlay(label, with_marks=True):
    """Draw the cut line, fold ticks, trim ticks and sheet label on a blank
    letter page. Returned as a pypdf page that we merge UNDER the booklet
    pages.

    with_marks: True on the FRONT side only. The back side gets just its
    label. Why: the back side is shifted by PRINTER_OFFSET_MM (and by any
    printer drift), so a second set of marks there would sit 1 to 2 mm away
    from the front's and you would not know which to trust. One set, on the
    side you look at while cutting and folding, is unambiguous.

    THE THREE KINDS OF MARK, each with its own look so they cannot be mixed up
    (this replaces an earlier design whose cut ticks sat only at the far left
    and right edges: trimming the sides first removed them, and they looked
    exactly like the head/foot ticks a quarter inch away):

      CUT   a long DASHED line across the whole sheet at the half-way line
            (5.5 in), with the word "cut" at each end. Because it runs the
            full width, it survives any edge you trim first.
      CROSS a light-grey cross at every page corner. Each line runs past the
            corner both into the waste and 0.35 in along the page edge, so no
            trim removes the line for another trim: any cutting order works.
      FOLD  a short stem on the fold line, in the head and foot waste of
            every copy.

    CUTTING ORDER (also printed in the right margin): the middle cut first,
    then the four trims in ANY order, cutting on the grey corner crosses
    (see the TRIM CROSSES block below for why this works).

    All marks sit in waste that is cut off, so none shows in the finished
    book. Nothing is drawn within 0.2 in of the paper edge, because most
    office printers cannot print there and would silently drop it.
    """
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(SHEET_W, SHEET_H))
    c.setStrokeColor(MARK_GREY)
    c.setFillColor(MARK_GREY)
    c.setLineWidth(0.4)

    if with_marks and TRIM_MARKS:
        # ---- CUT: dashed line across the full width, at exactly 5.5 in.
        # It runs from 0.2 in to 8.3 in. Between the two copies there is a
        # 0.5 in band of waste (0.25 in below copy A, 0.25 in above copy B),
        # and the line runs down its middle, 0.25 in clear of every page.
        c.setLineWidth(0.5)
        c.setDash(4, 3)                       # 4 pt on, 3 pt off
        c.line(0.2 * IN, CUT_Y, SHEET_W - 0.2 * IN, CUT_Y)
        c.setDash()                           # back to solid for the rest
        c.setFont("Helvetica", 5)
        # The word sits just above the line, inside the side waste.
        c.drawString(0.22 * IN, CUT_Y + 2, "cut")
        c.drawRightString(SHEET_W - 0.22 * IN, CUT_Y + 2, "cut")

        # ---- TRIM CROSSES: a cross at every page corner.
        #
        # History. 2026-10-14: short ticks, then triangles and "T" marks at
        # the fold; 2026-10-17: ticks above and below every copy, then
        # full-length lines along every edge. The short marks all failed the
        # same way: a mark for one trim sat in the waste of ANOTHER trim, so
        # some cutting order removed it. Full-length lines fixed that but were
        # more ink than needed (Eric's suggestion: just the crosses).
        #
        # A cross at each corner is enough. Each of its two lines continues
        # PAST the corner in both directions:
        #   * outward, into the waste (the usual crop mark), and
        #   * inward, ALONG the page edge (0.35 in).
        # The inward part of each line lies along its own trim line, so it
        # survives the OTHER trim: cut the top first and the vertical arms
        # running down the side edges are still there; cut the sides first
        # and the horizontal arms running along the top are still there.
        # Any cutting order works.
        #
        # PRECISION: 0.3 pt hairlines whose PAGE-SIDE edge lies EXACTLY on
        # the trim line (the stroke is centred half a line-width into the
        # waste). Cut ON the line. A cut a hair outside can leave a faint
        # sliver near the corners, so the crosses use the lighter FRAME_GREY.
        frame_lw = 0.3
        half = frame_lw / 2
        arm_in = 0.35 * IN     # along the page edge
        arm_out_x = 0.30 * IN  # into the side waste (0.75 in wide)
        arm_out_y = 0.20 * IN  # into the head/foot waste (0.25 in tall)
        c.setStrokeColor(FRAME_GREY)
        c.setLineWidth(frame_lw)
        left_x, right_x = FOLD_X - PAGE_W, FOLD_X + PAGE_W   # the fore-edges
        for base_y in COPY_Y.values():
            for y, ydir in ((base_y + PAGE_H, +1), (base_y, -1)):    # head, foot
                for x, xdir in ((left_x, -1), (right_x, +1)):        # left, right
                    # xdir/ydir point OUTWARD (into the waste) from the corner.
                    yl = y + ydir * half          # head/foot line, in the waste
                    xl = x + xdir * half          # fore-edge line, in the waste
                    # horizontal arm: outward into side waste, inward along the edge
                    c.line(x + xdir * arm_out_x, yl, x - xdir * arm_in, yl)
                    # vertical arm: outward into head/foot waste, inward along the edge
                    c.line(xl, y + ydir * arm_out_y, xl, y - ydir * arm_in)
        c.setStrokeColor(MARK_GREY)

        # ---- FOLD: a short stem on the fold line, in the head and foot waste
        # of every copy, starting at the head/foot line and pointing away from
        # the page. Crease so the fold runs through these stems.
        c.setLineWidth(0.4)
        for base_y in COPY_Y.values():
            for y0, d in ((base_y + PAGE_H, +1), (base_y, -1)):
                c.line(FOLD_X, y0 + d * (half + 0.01 * IN), FOLD_X, y0 + d * 0.15 * IN)

        # ---- CUTTING ORDER reminder: tiny rotated text in the RIGHT side
        # margin of each copy. With the corner crosses, any order works;
        # only the middle cut has to come first.
        c.setFont("Helvetica", 5)
        for base_y in COPY_Y.values():
            c.saveState()
            c.translate(SHEET_W - 0.3 * IN, base_y + 0.6 * IN)
            c.rotate(90)
            c.drawString(0, 0, "cut the middle first, then cut ON the grey crosses, in any order")
            c.restoreState()
        c.setLineWidth(0.4)

    # 2c. Registration mark: a small crosshair with 1 mm ticks at the very
    #     centre of the sheet (where the fold line meets the cut line). That
    #     spot is in the 0.5 in waste band between the two copies, so the
    #     final trim removes it. Front and back both carry it, so holding ANY
    #     sheet to a window shows whether that sheet's sides line up. It is
    #     the same test as alignment_test.pdf, but on every real sheet.
    # Off by default (REGISTRATION_MARK below the geometry): it was only a
    # diagnostic for printer drift. Set it to True to print it again.
    if REGISTRATION_MARK:
        c.setLineWidth(0.3)
        arm = 0.2 * IN
        c.line(FOLD_X - arm, CUT_Y, FOLD_X + arm, CUT_Y)
        c.line(FOLD_X, CUT_Y - arm, FOLD_X, CUT_Y + arm)
        for i in range(-5, 6):
            t = 1.5 if i % 5 else 3
            d = i * IN / 25.4
            c.line(FOLD_X + d, CUT_Y - t, FOLD_X + d, CUT_Y + t)
            c.line(FOLD_X - t, CUT_Y + d, FOLD_X + t, CUT_Y + d)
    c.setLineWidth(0.4)

    # 3. Sheet label, rotated, in the left waste margin of each copy.
    c.setFont("Helvetica", 5.5)
    for base_y in COPY_Y.values():
        c.saveState()
        c.translate(0.35 * IN, base_y + 0.5 * IN)
        c.rotate(90)
        c.drawString(0, 0, label)
        c.restoreState()

    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


# ------------------------------------------------------------- assembling
def place(sheet_page, src_page, left_edge_x, bottom_y):
    """Draw `src_page` onto `sheet_page` with its lower-left corner at
    (left_edge_x, bottom_y). Booklet pages are already 3.5 x 5 in, so this
    is a pure translation: no scaling, ever."""
    sheet_page.merge_transformed_page(
        src_page, Transformation().translate(left_edge_x, bottom_y))


def impose(src_path, out_path, label_prefix, offset_mm=PRINTER_OFFSET_MM):
    src = PdfReader(src_path)
    pages = src.pages
    n = len(pages)

    # Sanity check: every page must be 3.5 x 5 in (within a hair).
    for i, p in enumerate(pages, 1):
        w, h = float(p.mediabox.width), float(p.mediabox.height)
        if abs(w - PAGE_W) > 1 or abs(h - PAGE_H) > 1:
            sys.exit(f"Page {i} is {w/IN:.2f} x {h/IN:.2f} in, expected 3.5 x 5 in")

    sheets = sheet_layout(n)
    check_order(sheets, n)

    # The front side is drawn where it belongs. The back side, marks
    # included, is moved by (bx, by) to cancel the printer's offset.
    bx, by = back_correction(offset_mm)

    out = PdfWriter()
    for k, (front, back) in enumerate(sheets):
        for side_name, (left, right), (sx, sy) in (
            ("front", front, (0.0, 0.0)),
            ("back", back, (bx, by)),
        ):
            label = f"{label_prefix}  sheet {k + 1} of {len(sheets)}, {side_name}"
            sheet = PageObject.create_blank_page(width=SHEET_W, height=SHEET_H)
            # Marks on the front only; the back gets just its sheet label.
            sheet.merge_transformed_page(
                marks_overlay(label, with_marks=(side_name == "front")),
                Transformation().translate(sx, sy))
            for y in COPY_Y.values():
                # Left page ends at the fold; right page starts at the fold.
                place(sheet, pages[left - 1], FOLD_X - PAGE_W + sx, y + sy)
                place(sheet, pages[right - 1], FOLD_X + sx, y + sy)
            out.add_page(sheet)

    with open(out_path, "wb") as f:
        out.write(f)
    print(f"{out_path}: {n} pages -> {len(sheets)} sheets "
          f"({2 * len(sheets)} printed sides, 2 booklets per print run)")


# ----------------------------------------------------- duplex alignment test
def alignment_test(out_path, correct_back=None):
    """Two-page PDF: a crosshair and ruler at the same spot on both sides.

    Print it double-sided (flip on long edge) and hold it up to a window.
    If the crosshairs coincide, your printer is aligned. Otherwise read the
    back crosshair's offset as seen from the front and put it in
    PRINTER_OFFSET_MM (see the explanation above that constant).
    This test itself is never corrected, so it always shows the raw error.
    """
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(SHEET_W, SHEET_H))
    # With correct_back = an offset in mm, the BACK crosshair is drawn with
    # the same correction the booklets get. Printed, the two crosshairs should
    # then coincide: that verifies the correction (alignment_check.pdf).
    bx, by = back_correction(correct_back) if correct_back else (0.0, 0.0)
    for side in ("FRONT", "BACK"):
        c.setLineWidth(0.3)
        cx, cy = FOLD_X, CUT_Y
        if side == "BACK":
            cx, cy = cx + bx, cy + by
        c.line(cx - 2 * IN, cy, cx + 2 * IN, cy)
        c.line(cx, cy - 2 * IN, cx, cy + 2 * IN)
        # millimetre ticks along both arms, to read the offset
        for i in range(-40, 41):
            t = (2.5 if i % 5 else 5) * (0.5 if i % 10 else 1.4)
            x = cx + i * IN / 25.4
            y = cy + i * IN / 25.4
            c.line(x, cy - t, x, cy + t)
            c.line(cx - t, y, cx + t, y)
        c.setFont("Helvetica", 9)
        c.drawCentredString(cx, cy + 2.3 * IN, f"{side} SIDE  (ticks every 1 mm)")
        c.drawCentredString(cx, cy - 2.5 * IN,
                            "Print at 100%, double-sided, flip on long edge. "
                            "Hold to a window and compare.")
        c.showPage()
    c.save()
    with open(out_path, "wb") as f:
        f.write(buf.getvalue())
    print(f"{out_path}: duplex alignment test written")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Saddle-stitch 2-up imposition on US Letter.")
    ap.add_argument("src", nargs="?", help="booklet PDF at 3.5 x 5 in")
    ap.add_argument("out", nargs="?", help="output PDF to print")
    ap.add_argument("--label", default="interior", help="name printed in the sheet label")
    ap.add_argument("--back-offset", type=float, nargs=2, metavar=("DX", "DY"),
                    default=PRINTER_OFFSET_MM,
                    help="back crosshair offset seen from the front, in mm: right, up "
                         "(default: PRINTER_OFFSET_MM)")
    ap.add_argument("--test", action="store_true", help="write the duplex alignment test instead")
    ap.add_argument("--check", action="store_true",
                    help="write the alignment test WITH the back correction applied, to verify it")
    a = ap.parse_args()
    if a.test:
        # With --test there is no source; the single path given is the output.
        alignment_test(a.out or a.src)
    elif a.check:
        alignment_test(a.out or a.src, correct_back=tuple(a.back_offset))
    else:
        if not (a.src and a.out):
            ap.error("give both the booklet PDF and the output PDF")
        impose(a.src, a.out, a.label, tuple(a.back_offset))
