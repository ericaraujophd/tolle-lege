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
//   page 1  front           series name, silhouette art, title, paper boxes
//   page 2  inside front    "This notebook belongs to"
//   page 3  inside back     specifications, credits
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
// ONE COVER FOR EVERY PAPER. The front carries three small boxes, Dotted,
// Lined and Blank: tick the one that matches the paper you sewed inside. So
// each design needs only one cover file, whatever paper you use.
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

  // A small square check box followed by a label, for the paper type.
  let box-label(label) = box[
    #box(width: 6.5pt, height: 6.5pt, stroke: 0.6pt + black, baseline: 1pt)
    #h(3pt)#text(size: 8pt, tracking: 0.08em)[#upper(label)]
  ]
  // The double rule used on the book covers: heavy line outside, thin inside.
  let rule-pair(heavy-first) = {
    if heavy-first {
      line(length: 100%, stroke: 1.4pt + accent); v(-0.55em)
      line(length: 100%, stroke: 0.5pt + accent)
    } else {
      line(length: 100%, stroke: 0.5pt + accent); v(-0.55em)
      line(length: 100%, stroke: 1.4pt + accent)
    }
  }

  // ------------------------------------------------------------ 1. FRONT
  align(center)[
    #text(size: 8.5pt, tracking: 0.18em, fill: accent)[#upper(series) #h(0.35em)·#h(0.35em) NOTEBOOK]
    #v(0.1in)
    #rule-pair(true)
    #v(0.06in)
    // The silhouette is sized by HEIGHT so the front always fits on one
    // page, whatever the drawing's proportions (a tall drawing at full width
    // pushed the title onto a second page). Width follows the drawing.
    #image(art, format: "svg", height: 2.55in)
    #v(0.04in)
    #rule-pair(false)
    #v(0.1in)
    #text(size: 18pt, style: "italic")[#meta.title]
    #v(1fr)
    #box-label("Dotted") #h(0.6em) #box-label("Lined") #h(0.6em) #box-label("Blank")
  ]

  // ----------------------------------------------------- 2. INSIDE FRONT
  pagebreak()
  let head(label) = text(size: 9pt, tracking: 0.12em, fill: accent, label)
  let write-lines(n) = for i in range(n) {
    line(length: 100%, stroke: 0.4pt)
    v(0.27in)
  }
  v(0.2in)
  head[THIS NOTEBOOK BELONGS TO]
  v(0.12in)
  write-lines(2)
  v(0.12in)
  head[IF FOUND, PLEASE RETURN TO]
  v(0.12in)
  write-lines(2)
  v(0.12in)
  head[STARTED  /  FINISHED]
  v(0.12in)
  line(length: 100%, stroke: 0.4pt)

  // ------------------------------------------------------ 3. INSIDE BACK
  pagebreak()
  v(1fr)
  head[SPECIFICATIONS]
  v(0.05in)
  line(length: 100%, stroke: 0.4pt)
  {
    set text(size: 8.5pt)
    grid(columns: (1fr, 1.6fr), row-gutter: 0.75em,
      [Size], [3.5 × 5 in],
      [Pages], [#pages, sewn through the fold],
      [Paper], [#meta.at("text_paper", default: "100 g/m², dotted, lined or blank")],
      [Cover], [#meta.at("cover_paper", default: "65 lb cardstock")],
      [Cover art], [#emph(meta.title), #meta.at("designer", default: "Eric Araújo")],
      [Corners], [Rounded, 1/4 in],
      [Made], [By hand, one at a time],
    )
  }
  line(length: 100%, stroke: 0.4pt)

  // ------------------------------------------------------------ 4. BACK
  pagebreak()
  v(1fr)
  align(center)[
    #text(size: 9pt, tracking: 0.18em, fill: accent)[#upper(series)] \
    #v(1pt)
    #text(size: 7.5pt, style: "italic")[Take up and write.] \
    #v(4pt)
    #text(size: 7pt)[Pocket notebooks and books to print, fold and sew yourself. \ #series-url]
  ]
}
