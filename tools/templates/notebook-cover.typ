// =========================================================================
// tools/templates/notebook-cover.typ  --  the shared NOTEBOOK cover
// =========================================================================
//
// The Tolle Lege notebooks are pocket notebooks (3.5 x 5 in, the same size as
// the books) whose INSIDE pages are bought ready-printed (dotted, lined or
// blank letter paper, cut in half, folded and sewn). So a notebook is only a
// cover. Like the book cover, it is four pages on one sheet, imposed by
// tools/impose.py:
//
//   page 1  front           the silhouette, and the series name, tiny
//   page 2  inside front    belongs to, if found please contact, started / finished
//   page 3  inside back     specifications and credits
//   page 4  back            series name and website
//
// A notebook folder in notebooks/ has an art.svg (the silhouette, black on
// transparent) and a notebook.toml; its cover.typ is two lines:
//
//     #import "/tools/templates/notebook-cover.typ": notebook-cover
//     #notebook-cover(toml("notebook.toml"), read("art.svg", encoding: none))
//
// The art is passed as BYTES (read in the notebook's own folder) because
// Typst resolves a file path relative to the file that calls image(), which
// would be this template, not the notebook folder.
//
// ONE COVER FOR EVERY PAPER. Nothing on the cover names the paper inside
// (dotted, lined or blank), so each design needs only one cover file.
//
// COLOUR. `accent` in notebook.toml sets the colour of the labels and the
// spec-sheet heading. All coloured text is SEMIBOLD (2026-10-24): inkjet ink
// is thin, and fine strokes in a dark colour print almost black; heavier
// strokes lay down more ink, so the colour actually shows. For the same
// reason accents should be mid-tones, not near-black (First Snow moved from
// navy #1f3a68 to a brighter blue #2a6db5).
//
// SILHOUETTES. The art is solid black shapes only (no greys, no fills of
// colour), which prints crisply on kraft or stone cardstock with any printer.
// =========================================================================

#let series = "Tolle Lege"
#let series-url = "ericaraujo.com/tolle-lege"

#let notebook-cover(meta, art) = {
  let accent = rgb(meta.at("accent", default: "#9e1b1f"))
  let pages = meta.at("pages", default: 48)

  set page(width: 3.5in, height: 5in, margin: 0.36in)
  set text(font: "Libertinus Serif", size: 8pt, fill: black)
  set par(justify: false)

  // ------------------------------------------------------------ 1. FRONT
  // MINIMAL ON PURPOSE (Eric, 2026-10-20): no rules, no title. The page is
  // empty except for the BOTTOM-RIGHT corner, where the small silhouette
  // sits with the series name, tiny and grey, just above it.
  //   v(1fr)      pushes everything down to the foot of the page
  //   align(right + bottom, stack(...))  puts name and art in that corner,
  //   the name centred over the art (the stack is only as wide as the art).
  // The art is sized by HEIGHT (1.35 in, about a quarter of the page).
  v(1fr)
  // box(...) shrinks to the width of its widest child (the art), so
  // "center" inside the stack means centred over the art, not the page.
  align(right, box(stack(dir: ttb, spacing: 0.1in,
    // Tracking adds space after the last letter too; h(-0.3em) removes it
    // so the name is truly centred.
    align(center, text(size: 6pt, tracking: 0.3em, fill: luma(80))[#upper(series)#h(-0.3em)]),
    image(art, format: "svg", height: 1.35in),
  )))

  // ----------------------------------------------------- 2. INSIDE FRONT
  // The owner's page (redesigned 2026-10-20). A small series mark, then
  // three blocks a fixed `gap` apart, the whole group centred on the page
  // (v(1fr) above and below):
  //   This notebook belongs to   one writing line
  //   If found, please contact   two writing lines (name; phone or email)
  //   Started / Finished         two rows, each a date to fill in as
  //                              MM / DD / YYYY, with the small guide
  //                              letters printed under each blank
  // Labels are small letter-spaced capitals in the accent colour; writing
  // lines are thin and grey so handwriting, not print, is what stands out.
  pagebreak()
  let label(t) = text(size: 7pt, tracking: 0.16em, fill: accent, weight: "semibold", upper(t))
  let rule-grey = 0.5pt + luma(150)
  // Heading style for the inside back (spec sheet).
  let head(t) = text(size: 9pt, tracking: 0.12em, fill: accent, weight: "semibold", t)
  // A writing line with room above it for handwriting (0.3 in).
  let write-line() = { v(0.3in); line(length: 100%, stroke: rule-grey) }
  // A date row, as a grid so everything lines up:
  //   row 1:  STARTED   ______ / ______ / __________
  //   row 2:             MM       DD       YYYY       (tiny grey guides)
  // Each blank is a box whose line sits at its BOTTOM, and row 1 is
  // bottom-aligned, so the lines rest on the same baseline as the label.
  let blank = box(width: 100%, height: 9pt, align(bottom, line(length: 100%, stroke: rule-grey)))
  let guide(t) = align(center, text(size: 5pt, tracking: 0.12em, fill: luma(120), t))
  let slash = align(center + bottom, text(size: 9pt, fill: luma(150))[/])
  let date-row(name) = grid(
    columns: (1fr, 0.36in, 0.15in, 0.36in, 0.15in, 0.58in),
    row-gutter: 3pt, align: bottom,
    label(name), blank, slash, blank, slash, blank,
    [], guide[MM], [], guide[DD], [], guide[YYYY],
  )
  let gap = 0.42in        // the space between the blocks

  v(1fr)
  align(center, text(size: 6pt, tracking: 0.3em, fill: luma(110))[#upper(series) #h(0.2em)·#h(0.2em) NOTEBOOK#h(-0.3em)])
  v(gap)
  label("This notebook belongs to")
  write-line()
  v(gap)
  label("If found, please contact")
  write-line()
  write-line()
  v(gap)
  date-row("Started")
  v(0.22in)
  date-row("Finished")
  v(1fr)

  // ------------------------------------------------------ 3. INSIDE BACK
  pagebreak()
  v(1fr)
  // The notebook's number in the collection, set like a small title above
  // the spec sheet: "NOTEBOOK" in letter-spaced capitals, then "No. 01"
  // large and in italics, both in the accent colour. From `num` in
  // notebook.toml.
  if "num" in meta {
    align(center)[
      #text(size: 7pt, tracking: 0.3em, fill: accent, weight: "semibold")[NOTEBOOK#h(-0.3em)] \
      #v(2pt)
      #text(size: 20pt, style: "italic", fill: accent, weight: "semibold")[No. #meta.num]
    ]
    v(0.3in)
  }
  head[SPECIFICATIONS]
  v(0.05in)
  line(length: 100%, stroke: 0.4pt)
  {
    set text(size: 8.5pt)
    grid(columns: (1fr, 1.6fr), row-gutter: 0.75em,
      [Size], [3.5 × 5 in],
      [Pages], [#pages, sewn through the fold],
      [Paper], [#meta.at("text_paper", default: "100 g/m²")],
      [Cover], [#meta.at("cover_paper", default: "65 lb cardstock")],
      [Cover art], [#meta.at("designer", default: "Eric Araújo")],
      // Optional extra line, e.g. how the illustration was made.
      ..if "art_tool" in meta { ([Illustration], [#meta.art_tool]) } else { () },
      [Corners], [Rounded, 1/4 in],
      [Made], [By hand, one at a time],
    )
  }
  line(length: 100%, stroke: 0.4pt)

  // ------------------------------------------------------------ 4. BACK
  pagebreak()
  v(1fr)
  align(center)[
    #text(size: 9pt, tracking: 0.18em, fill: accent, weight: "semibold")[#upper(series)] \
    #v(1pt)
    #text(size: 7.5pt, style: "italic")[Take up and write.] \
    #v(4pt)
    #text(size: 7pt)[Pocket notebooks and books to print, fold and sew yourself. \ #series-url]
  ]
}
