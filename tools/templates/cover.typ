// =========================================================================
// tools/templates/cover.typ  --  the shared COVER template
// =========================================================================
//
// The cover is printed on a separate, heavier sheet (65 lb cardstock), so it
// is laid out on its own: four pages at 3.5 x 5 in, which tools/impose.py
// treats exactly like a 4-page booklet (one sheet, folded once).
//
//   page 1  front cover          (outside)
//   page 2  inside front cover   (inside)  "This book belongs to"
//   page 3  inside back cover    (inside)  specifications
//   page 4  back cover           (outside) quote and blurb
//
// A title's cover.typ is just:
//
//     #import "/tools/templates/cover.typ": cover
//     #cover(toml("title.toml"))
//
// Everything title-specific comes from title.toml: number, title, subtitle,
// author, source, cover quote and its reference, the blurb, and optionally
// the accent colour and the paper descriptions on the spec sheet.
//
// INK ON KRAFT. Inkjet and toner are transparent, so on brown kraft every
// colour is "multiplied" by the brown: light or bright colours nearly vanish
// and only dark, saturated ones read. That is why there are no filled areas
// and why the default accent is a deep red. On lighter cover stock (cream,
// oatmeal, grey) the same red reads much brighter.
// =========================================================================

// The total page count of the interior, for the spec sheet. The build passes
// it in after it has counted the interior pages.
#let interior-pages = sys.inputs.at("pages", default: "24")

#let cover(meta) = {
  // One accent colour, Field Notes style. Default: deep red, chosen to match
  // a red top-stitch thread on the spine. A title may set `accent` in its
  // title.toml (any CSS-style hex colour).
  let accent = rgb(meta.at("accent", default: "#9e1b1f"))

  set page(width: 3.5in, height: 5in, margin: 0.36in)
  set text(font: "Libertinus Serif", size: 8pt, fill: black)
  set par(justify: false)

  // TYPE SIZES (2026-10-17): every size on the cover was enlarged, because
  // the pages have plenty of room and larger type reads better on kraft,
  // where contrast is low. Front: number 8.5, title 28, subtitle 14,
  // author 12, source 8 pt. Inside: headings 9, spec sheet 8.5 pt.
  // Back: quote and blurb 9.5, reference 8, footer 7.5 pt.

  // ---------------------------------------------------------- 1. FRONT
  // A double rule above and below the title, heavier line outside: a nod to
  // the plain kraft covers of Field Notes and to old pocket editions. The
  // rules are fairly heavy (1.4 pt + 0.5 pt) so the colour reads at arm's
  // length on kraft; thinner red lines looked almost black.
  align(center)[
    #text(size: 8.5pt, tracking: 0.18em, fill: accent)[#upper(meta.number)]
    #v(0.45in)
    #line(length: 100%, stroke: 1.4pt + accent)
    #v(-0.55em)
    #line(length: 100%, stroke: 0.5pt + accent)
    #v(0.12in)
    #text(size: meta.at("cover_title_size", default: 28) * 1pt, style: "italic")[#meta.title] \
    #v(2pt)
    #text(size: 14pt, style: "italic")[#meta.subtitle]
    #v(0.16in)
    #line(length: 100%, stroke: 0.5pt + accent)
    #v(-0.55em)
    #line(length: 100%, stroke: 1.4pt + accent)
    #v(0.24in)
    #text(size: 12pt, tracking: 0.12em)[#upper(meta.author)]
    #v(1fr)
    #text(size: 8pt)[#meta.source]
  ]

  // ------------------------------------------- 2. INSIDE FRONT COVER
  // "This book belongs to" lines, like Field Notes.
  pagebreak()
  let head(label) = text(size: 9pt, tracking: 0.12em, fill: accent, label)
  let write-lines(n) = for i in range(n) {
    line(length: 100%, stroke: 0.4pt)
    v(0.27in)
  }
  v(0.2in)
  head[THIS BOOK BELONGS TO]
  v(0.12in)
  write-lines(3)
  v(0.15in)
  head[READ WITH]
  v(0.12in)
  write-lines(2)
  v(0.15in)
  head[STARTED  /  FINISHED]
  v(0.12in)
  line(length: 100%, stroke: 0.4pt)

  // -------------------------------------------- 3. INSIDE BACK COVER
  // A short spec sheet, again in the Field Notes manner. The paper lines can
  // be overridden per title in title.toml (text_paper, cover_paper).
  pagebreak()
  v(1fr)
  head[SPECIFICATIONS]
  v(0.05in)
  line(length: 100%, stroke: 0.4pt)
  {
    set text(size: 8.5pt)
    grid(columns: (1fr, 1.4fr), row-gutter: 0.75em,
      [Size], [3.5 × 5 in],
      [Pages], [#interior-pages, sewn through the fold],
      [Paper], [#meta.at("text_paper", default: "24 lb cream")],
      [Cover], [#meta.at("cover_paper", default: "65 lb kraft cardstock")],
      [Corners], [Rounded, 1/4 in],
      [Type], [Libertinus Serif],
      [Made], [By hand, one at a time],
    )
  }
  line(length: 100%, stroke: 0.4pt)

  // ------------------------------------------------------- 4. BACK
  pagebreak()
  {
    set text(size: 9.5pt)
    v(0.3in)
    align(center)[
      #text(style: "italic")[#meta.quote]
      #v(0.05in)
      #text(size: 8pt, fill: accent)[#meta.quote_ref]
      #v(0.3in)
      #eval(meta.blurb, mode: "markup")
    ]
    v(1fr)
    align(center, text(size: 7.5pt)[Public-domain text. Free to copy and share.])
  }
}
