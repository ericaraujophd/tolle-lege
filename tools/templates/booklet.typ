// =========================================================================
// tools/templates/booklet.typ  --  the shared INTERIOR template
// =========================================================================
//
// Every title in titles/ uses this file for its inside pages. It lays out
// pages one by one, at the FINAL trimmed size of 3.5 x 5 inches, in reading
// order. It does NOT do imposition (putting pages on letter sheets in the
// right order); tools/impose.py does that. Keeping the two apart means the
// "reading copy" PDF can be read like a normal book for proofreading.
//
// HOW A TITLE USES IT
// -------------------
// Each title folder has a tiny book.typ that imports this file and calls
// its pieces in order, for example:
//
//     #import "/tools/templates/booklet.typ": *
//     #let meta = toml("title.toml")
//     #show: book.with(meta)          // page size, type, page numbers
//     #title-page(meta)               // page 1
//     #edition-note(meta)             // page 2
//     #pagebreak()
//     #include "intro.typ"            // the title's own introduction
//     ... the text ...
//     #include "reflection.typ"       // questions, glossary
//     #notes(meta)                    // ruled pages + colophon
//
// The paths that start with "/" are relative to the REPOSITORY ROOT; the
// build compiles with the repository as Typst's root folder so that every
// title can reach the shared tools/ folder.
//
// THE PAGE COUNT
// --------------
// A booklet made of folded sheets must have a multiple of 4 pages (one
// folded sheet = 4 pages). The build compiles once, counts the pages, and
// compiles again telling this template how many ruled "Notes" pages to add
// at the end (sys.inputs "notes"). The last notes page also carries the
// colophon, so there is always at least one.
//
// Everything that changes from title to title (title, author, translation,
// cover quote...) lives in that title's title.toml, read into `meta`.
// =========================================================================

// How many ruled notes pages to add at the end; the build passes this in.
// Compiled by hand it defaults to 1.
#let notes-count = int(sys.inputs.at("notes", default: "1"))

// ------------------------------------------------------------- page setup
// Apply with `#show: book.with(meta)` at the top of a title's book.typ.
//
// The page is the FINAL size after trimming. Margins are mirrored: the
// "inside" margin is next to the sewn fold and the "outside" margin is at the
// fore-edge (the edge you open). The outside is wider because the fore-edge
// is trimmed after binding, and because inner sheets of a folded booklet
// stick out slightly ("creep"); the extra room keeps text safe.
#let book(meta, body) = {
  set page(
    width: 3.5in,
    height: 5in,
    margin: (inside: 0.36in, outside: 0.42in, top: 0.42in, bottom: 0.52in),
    // Page number centred at the bottom, small. The title page (page 1) and
    // the last page (colophon) are left unnumbered.
    footer: context {
      let n = counter(page).get().first()
      let last = counter(page).final().first()
      if n > 1 and n < last {
        align(center, text(size: 6.5pt, fill: luma(90), str(n)))
      }
    },
    footer-descent: 40%,
  )
  // Libertinus Serif ships inside Typst, so the build works on any computer
  // without installing fonts. 9 pt on a 2.7 in measure gives about 43
  // characters per line, comfortable for a pocket book.
  set text(font: "Libertinus Serif", size: 9pt, lang: "en", hyphenate: true)
  set par(justify: true, leading: 0.58em, spacing: 0.9em, first-line-indent: 0pt)
  body
}

// -------------------------------------------------------- small headings
// A centred, letter-spaced small-caps style heading ("ABOUT THIS BOOKLET").
// Titles' intro.typ and reflection.typ use it for their section heads.
#let small-head(label) = {
  align(center, text(size: 7pt, tracking: 0.12em, upper(label)))
  v(0.08in)
}

// ------------------------------------------------- chapter-level headings
// Generic chapter opener for any title: always starts on a new page (but not
// forced to a right-hand page, which would leave blank pages).
//   label: small line above, e.g. "QUESTION 166" or "PART ONE" (may be none)
//   name:  the chapter name, set large in italics
#let chapter(label, name) = {
  pagebreak(weak: true)
  v(0.5in)
  align(center)[
    #if label != none [#text(size: 7pt, tracking: 0.12em)[#upper(label)] \ ]
    #v(2pt)
    #text(size: 14pt, style: "italic")[#name]
  ]
  v(0.18in)
}

// The Summa's own structure, used by No. 01 (content.typ calls these).
// A Question opens like a chapter; an Article gets a small rule, its number
// and the question it asks.
#let question(num, name) = chapter("Question " + num, name)

#let article(num, title) = {
  v(0.6em)
  block(breakable: false, below: 0.6em)[
    #line(length: 30%, stroke: 0.4pt + luma(120))
    #v(-0.2em)
    #text(size: 7pt, tracking: 0.1em)[ARTICLE #num] \
    #text(size: 9pt, style: "italic")[#title]
  ]
}

// A numbered section within a chapter, for titles made of short numbered
// pieces (Pascal's fragments, for example): a small number and an optional
// title, kept together with the first lines that follow.
#let section(num, title: none) = {
  v(0.5em)
  block(breakable: false, below: 0.45em)[
    #text(size: 7pt, tracking: 0.1em)[#num]
    #if title != none [ #h(0.4em) #text(style: "italic")[#title]]
  ]
}

// ------------------------------------------------------------- title page
#let title-page(meta) = align(center)[
  #v(0.35in)
  #text(size: 6.5pt, tracking: 0.15em)[#upper(meta.number)]
  #v(0.45in)
  #text(size: 17pt, style: "italic")[#meta.title] \
  #v(1pt)
  #text(size: 10pt, style: "italic")[#meta.subtitle]
  #v(0.25in)
  #line(length: 18%, stroke: 0.5pt)
  #v(0.2in)
  #text(size: 9pt, tracking: 0.08em)[#upper(meta.author)]
  #v(1fr)
  #text(size: 6.5pt)[#meta.source]
  #v(0.15in)
]

// ------------------------------------------- edition note (back of title)
// Bibliographic facts at the foot of page 2. `meta.edition_note` is the
// title's own paragraph about where the text came from and what was fixed.
#let edition-note(meta) = {
  pagebreak()
  v(1fr)
  set par(justify: false)
  text(size: 6.5pt)[
    *#meta.title #meta.subtitle* \
    #meta.author, #meta.source.

    #meta.translation The translation is in the public domain.

    #meta.edition_note

    Part of Tolle Lege, pocket classics to print, fold and sew yourself.
    This booklet may be freely copied and shared.
  ]
}

// ------------------------------------------------------------- notes pages
// A ruled page for handwritten notes. Line spacing about 6.5 mm, close to
// Field Notes ruled memo books.
//   heading:  a small title above the lines ("Notes"), or none.
//   colophon: content to print at the foot of the page, below the lines.
#let ruled-page(heading: none, colophon: none) = {
  pagebreak(weak: true)
  // The text area is 5 - 0.42 - 0.52 = 4.06 in tall. The lines are drawn
  // with `place`, which positions each one absolutely inside a fixed-height
  // block, so they can never spill onto a second page (they did once, when
  // drawn as ordinary content).
  let area = 4.0in
  if heading != none {
    align(center, text(size: 7pt, tracking: 0.12em, upper(heading)))
    area -= 0.35in
  }
  if colophon != none { area -= 0.65in }   // room for the colophon
  let gap = 0.255in
  let count = int(area / gap)
  block(height: area, width: 100%, spacing: 0pt, {
    for i in range(count) {
      place(top + left, dy: (i + 1) * gap - 0.05in,
            line(length: 100%, stroke: 0.35pt + luma(160)))
    }
  })
  if colophon != none {
    v(1fr)
    colophon
  }
}

// The colophon: how the book was made. It sits at the foot of the LAST notes
// page, so it never needs a page of its own.
#let colophon(meta) = {
  set par(justify: false, leading: 0.45em)
  align(center, text(size: 6.5pt)[
    #line(length: 15%, stroke: 0.4pt)
    #v(2pt)
    Set in Libertinus Serif. \
    Printed, folded, sewn and trimmed by hand. \
    #meta.date
  ])
}

// All the notes pages: the first gets the "Notes" heading, the last the
// colophon. With a single notes page, that one page gets both.
#let notes(meta) = {
  let n = calc.max(notes-count, 1)
  for i in range(n) {
    ruled-page(
      heading: if i == 0 { "Notes" } else { none },
      colophon: if i == n - 1 { colophon(meta) } else { none },
    )
  }
}
