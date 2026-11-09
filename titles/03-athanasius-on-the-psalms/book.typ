// book.typ -- the INTERIOR of No. 03, Athanasius, On the Psalms.
// All layout lives in the shared template (tools/templates/booklet.typ);
// this file only says what goes in, and in which order.
#import "/tools/templates/booklet.typ": *
#let meta = toml("title.toml")
#show: book.with(meta)

#title-page(meta)                // page 1
#edition-note(meta)              // page 2
#pagebreak()
#include "intro.typ"              // About this booklet; About this translation

// The text. content.typ is the translation, one long letter, with the
// editor's headings (#subhead) and set-off quotations (#psalm). Typst
// includes are isolated, so we read the file and evaluate it with the
// functions it uses in scope.
// Paragraph spacing a touch tighter than the default (0.9em) for this long
// letter, so the text ends cleanly at the foot of a page.
#set par(spacing: 0.8em)
#eval(read("content.typ"), mode: "markup",
      scope: (chapter: chapter, subhead: subhead, psalm: psalm))

#set par(spacing: 0.9em)
#include "reflection.typ"         // Questions for reflection; glossary
#notes(meta)                     // ruled notes pages, colophon on the last
