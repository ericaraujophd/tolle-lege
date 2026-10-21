// =========================================================================
// tools/templates/collection-band.typ  --  the BELLY BAND for a collection
// =========================================================================
//
// A collection is a set of notebooks given together, stacked and held by a
// paper band wrapped once around the middle and closed at the back with a
// wax seal. This template prints FOUR bands on one US Letter sheet, turned
// sideways (landscape), single-sided.
//
// THE BAND, laid flat (9.75 x 1.5 in), left to right:
//
//   |  back (left end)  | side |    FRONT, 3.5 in    | side |  back (right end)  |
//   0              2.725  3.125                6.625  7.025              9.75 in
//
// The fold positions are COMPUTED from BW (band length) and SIDE (stack
// thickness), with the front always centred, so changing either number
// keeps everything consistent.
//   * FRONT is centred, the width of a notebook (3.5 in). It carries the
//     series name, the collection name and the notebook numbers, each number
//     in that notebook's own colour.
//   * SIDES are 0.4 in: the thickness of three stacked notebooks, about 10 mm.
//   * The two BACK ends add up to 5.45 in: the 3.5 in back plus almost 2 in
//     of overlap, where the wax seal goes. The generous overlap is ROOM TO
//     SPARE (Eric, 2026-10-21): a thicker stack just uses up some of it.
//     They are left blank.
//
// Wrap: centre the front on the stack, fold at the four small grey ticks
// (printed just outside the band, above and below), bring both ends round
// the back, overlap, and seal.
//
// CUTTING. The four bands touch, so each cut serves two bands: the grey
// marks in the margins show five horizontal cuts (top, three between bands,
// bottom) and two vertical ones (the band ends). Like the books, all marks
// stay in the margins, so nothing printed is cut off.
// =========================================================================

#let series = "Tolle Lege"

#let collection-band(meta, books) = {
  let BW = 9.75in          // band length (9 in fits exactly; 0.75 in to spare)
  let BH = 1.5in           // band height
  let N = 4                // bands per sheet
  let X0 = (11in - BW) / 2           // left edge of the bands on the sheet
  let Y0 = (8.5in - N * BH) / 2      // top edge of the first band
  let mark = 0.5pt + luma(140)
  let SIDE = 0.4in         // thickness of the stacked notebooks
  let F = (BW - 3.5in) / 2           // where the front panel starts
  let folds = (F - SIDE, F, F + 3.5in, F + 3.5in + SIDE)

  set page(width: 11in, height: 8.5in, margin: 0in)
  set text(font: "Libertinus Serif", fill: black)

  // ---- what is printed on the FRONT panel of one band -------------------
  let front = {
    set align(center + horizon)
    set par(spacing: 0pt, leading: 0.5em)
    block(width: 3.5in, height: BH)[
      #text(size: 6.5pt, tracking: 0.3em, fill: luma(90))[#upper(series)#h(-0.3em)]
      #v(0.09in)
      #text(size: 15pt, style: "italic")[#meta.name]
      #v(0.1in)
      #text(size: 6.5pt, tracking: 0.25em, fill: luma(90))[NOTEBOOKS]
      #h(0.5em)
      // "No. 01 · 02 · 03", each number in its notebook's accent colour
      #text(size: 9pt, style: "italic")[No.]
      #h(0.15em)
      #for (i, b) in books.enumerate() {
        if i > 0 { text(size: 9pt, fill: luma(120))[ · ] }
        text(size: 9pt, style: "italic", fill: rgb(b.accent), b.num)
      }
    ]
  }

  // ---- the bands ----------------------------------------------------------
  for i in range(N) {
    place(dx: X0 + F, dy: Y0 + i * BH, front)
  }

  // ---- cut marks: in the margins only ------------------------------------
  // Horizontal cuts: a short line at each side, just outside the band ends.
  for i in range(N + 1) {
    let y = Y0 + i * BH
    place(dx: X0 - 0.45in, dy: y, line(length: 0.35in, stroke: mark))
    place(dx: X0 + BW + 0.1in, dy: y, line(length: 0.35in, stroke: mark))
  }
  // Vertical cuts (the two band ends): short lines above and below the stack.
  for x in (X0, X0 + BW) {
    place(dx: x, dy: Y0 - 0.45in, line(angle: 90deg, length: 0.35in, stroke: mark))
    place(dx: x, dy: Y0 + N * BH + 0.1in, line(angle: 90deg, length: 0.35in, stroke: mark))
  }
  // Fold ticks: tiny, above the top band and below the bottom one.
  for f in folds {
    place(dx: X0 + f, dy: Y0 - 0.16in, line(angle: 90deg, length: 0.1in, stroke: 0.4pt + luma(170)))
    place(dx: X0 + f, dy: Y0 + N * BH + 0.06in, line(angle: 90deg, length: 0.1in, stroke: 0.4pt + luma(170)))
  }
  // A note in the bottom margin.
  place(dx: X0, dy: 8.5in - 0.42in, text(size: 6.5pt, fill: luma(120))[
    #meta.name band · 4 per sheet · print single-sided at 100% · cut on the grey marks · fold at the small ticks · seal at the back
  ])
}
