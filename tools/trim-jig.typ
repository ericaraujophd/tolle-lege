// =========================================================================
// tools/trim-jig.typ  --  a printable TRIM JIG for a rotary paper trimmer
// =========================================================================
//
// THE PROBLEM. Booklets and notebooks are trimmed after sewing, and cutting
// each one "by eye" or by measuring gives sizes that drift by a millimetre
// or two. Consistency comes from cutting every book against the same fixed
// stop (a "fence") at the same distance from the blade.
//
// THE TRICK. A rotary trimmer cuts along its rail. If you lay this sheet on
// the trimmer and CUT IT ALONG THE BLADE LINE with the trimmer itself, the
// sheet's new edge lies exactly on the blade path. Tape the sheet down
// without moving it: every line on it is now an exact distance from the
// blade, measured perpendicular to the cut.
//
// THE FENCES. Lines at 3.5 in, 5.25 in and 5 in from the blade edge. Tape a
// steel ruler (or glue a strip of cardstock) with its edge on the line you
// need; the book is pushed against it and cut:
//
//   cut 1  FORE-EDGE  fence at 3.5 in   spine against the fence
//   cut 2  HEAD       fence at 5.25 in  foot against the fence (trims about
//                                       1/4 in off the head of a 5.5 in book)
//   cut 3  FOOT       fence at 5 in     freshly cut head against the fence
//
// The finished size is 3.5 x 5 in. Do each cut for the whole batch before
// moving the fence: resetting between books is where sizes drift.
//
// A square line, perpendicular to the blade, is printed too: line the
// spine or a cut edge up with it so the book sits square.
//
// PRINT AT 100% ("Actual size"). The 1-inch and 5 cm scales at the top
// let you check with a ruler that the printer did not shrink the page.
// =========================================================================

#set page(width: 11in, height: 8.5in, margin: 0in)
#set text(font: "Libertinus Serif", size: 9pt)

#let BLADE = 7.9in            // y of the blade line, from the top edge
#let ink = luma(30)
#let soft = luma(140)

// A fence line at distance d (inches) above the blade line, with labels.
#let fence(d, name, how, accent) = {
  let y = BLADE - d * 1in
  place(dx: 0.6in, dy: y, line(length: 9.8in, stroke: 1.2pt + accent))
  place(dx: 0.7in, dy: y - 0.2in,
    text(size: 9pt, weight: "bold", fill: accent)[#name: fence at #d in])
  place(dx: 3.6in, dy: y - 0.2in, text(size: 8pt, fill: ink, how))
}

// --- the blade line: cut the sheet along it with the trimmer first ------
#place(dx: 0in, dy: BLADE, line(length: 11in, stroke: (paint: ink, thickness: 0.8pt, dash: "dashed")))
#place(dx: 0.7in, dy: BLADE + 0.08in, text(size: 9pt, weight: "bold")[
  BLADE LINE. Step 1: lay this sheet on the trimmer and cut ALONG THIS LINE with
  the trimmer. Step 2: without moving it, tape the sheet down. Throw away the strip below.])

// --- the three fences ----------------------------------------------------
#fence(3.5, "1. FORE-EDGE", [Spine against the fence. Cut the open side.], rgb("#9e1b1f"))
#fence(5.0, "3. FOOT", [Freshly cut head against the fence. Cut the foot. Done: 3.5 × 5 in.], rgb("#2f7fd6"))
#fence(5.25, "2. HEAD", [Foot against the fence. Cut about 1/4 in off the head.], rgb("#3a8a4f"))

// --- the square line (perpendicular to the blade) ------------------------
#place(dx: 1.0in, dy: BLADE - 6.2in, line(angle: 90deg, length: 6.2in, stroke: 0.8pt + soft))
#place(dx: 0.35in, dy: BLADE - 6.45in, text(size: 7.5pt, fill: soft)[square line: keep the book's edge on it])

// --- check-the-scale rulers, top left -----------------------------------
#let ruler(len, n, unit, label) = {
  for i in range(n + 1) {
    place(dx: i * len, dy: 0in, line(angle: 90deg, length: if calc.rem(i, 5) == 0 { 0.14in } else { 0.08in }, stroke: 0.5pt + ink))
  }
  place(dx: 0in, dy: 0in, line(length: n * len, stroke: 0.5pt + ink))
  place(dx: n * len + 0.08in, dy: -0.03in, text(size: 7pt)[#label])
}
#place(dx: 0.6in, dy: 0.45in, ruler(0.1in, 10, "in", [1 inch: check with a ruler]))
#place(dx: 0.6in, dy: 0.8in, ruler(1cm, 5, "cm", [5 cm]))
#place(dx: 4.2in, dy: 0.42in, text(size: 8pt, fill: ink)[
  *Tolle Lege trim jig* · print at 100% on cardstock · if the scales are off,
  print again with scaling turned off.\
  Tape a steel ruler (or glue a cardstock strip) with its edge exactly on the
  fence you need. Do each cut for the whole batch before moving the fence.])
