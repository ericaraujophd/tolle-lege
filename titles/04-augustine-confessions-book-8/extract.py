#!/usr/bin/env python3
"""
extract.py  (titles No. 03 and No. 04, Augustine, Confessions)
==============================================================

Turns one book of Augustine's Confessions, in Albert C. Outler's translation,
into Typst markup (content.typ) for a booklet. The same script serves both
titles; each folder's copy differs only in BOOK below. (No. 04's copy reads
the source file kept in No. 03's folder, so the 850 KB text is stored once.)

THE SOURCE
  source/outler-confessions.txt: CCEL's plain-text edition of Outler's
  translation, "Confessions and Enchiridion" (Westminster Press, 1955;
  Library of Christian Classics, vol. 7). CCEL marks it "Rights: Public
  Domain"; Wikisource records that the copyright holder released it to the
  public domain. Downloaded 2026-11-09 from
  https://ccel.org/ccel/a/augustine/confessions/cache/confessions.txt

WHAT THE SCRIPT DOES, STEP BY STEP
  1. Cuts out the chosen book: from the line "BOOK ONE" (or "BOOK EIGHT")
     to the next "BOOK ..." heading.
  2. Splits it into Outler's one-paragraph SUMMARY (printed in italics under
     the book title), the TEXT, and Outler's NOTES, which follow the text
     at the end of each book as lines "[231] Ps. 35:10."
  3. Sorts the notes in two kinds:
       * Scripture references (e.g. "Ps. 35:10", "Cf. Rom. 1:21") are put
         back into the text right where the marker was, in small grey type:
         "...thou art there." (Ps. 139:8). A pocket book has no room for
         footnotes, and the reader needs only the reference.
       * Explanatory notes (Virgil, Plotinus, the imperial agents...) are
         renumbered 1, 2, 3... in the order they occur, marked in the text
         with a small raised number, and printed on a Notes page at the end.
  4. Keeps Augustine's standard numbering, so anyone can follow along in any
     edition (e.g. VIII.12.29): each "CHAPTER XII" becomes a small heading,
     each numbered paragraph ("29. ...") starts with its number in bold.
  5. Keeps Outler's punctuation, turning his typewriter "--" into a true dash.
  6. Writes content.typ (the text) and notes.typ (the endnotes).

Run it from anywhere:   python3 titles/03-augustine-confessions-book-1/extract.py
"""

import re
from pathlib import Path

BOOK = "EIGHT"          # "ONE" for No. 03, "EIGHT" for No. 04

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "03-augustine-confessions-book-1" / "source" / "outler-confessions.txt"
ORDER = ["ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE",
         "TEN", "ELEVEN", "TWELVE", "THIRTEEN"]

# A note counts as a Scripture reference when it is nothing but book-chapter-
# verse references, e.g. "Ps. 35:10.", "Cf. Ps. 116:16, 17.", "1 Cor. 13:12.",
# "Cf. Luke, ch. 15." Anything else is an explanatory note.
REF = r"(?:Cf\.\s+|See\s+)?(?:\d\s)?[A-Z][a-z]+\.?(?:,\s*ch\.)?\s*\d+(?::[\d,\s\-]+)?"
# After a ";" or "and" a reference may give only chapter:verse ("Ps. 6:3; 79:8").
CV = r"\d+:[\d,\s\-]+"
SCRIPTURE = re.compile(rf"^{REF}(?:\s*(?:;|,|and)\s*(?:{REF}|{CV}))*\.?$")

# Typing slips in the CCEL transcription, fixed here: (wrong, right, why).
# Each must occur exactly once in the book's notes or text, or the script
# stops, so a changed source is noticed.
CORRECTIONS = {
    # Book One: the CCEL text lacks the heading of chapter XIX (which begins
    # at paragraph 30) and so calls the last chapter XIX instead of XX. The
    # standard division is ch. XIX = para. 30, ch. XX = para. 31. The first
    # fix renames the last heading, the second inserts the missing one.
    "ONE": [("   CHAPTER XIX\n", "   CHAPTER XX\n", "last chapter is XX"),
            ("\n   30. These were the customs", "\n   CHAPTER XIX\n\n   30. These were the customs",
             "missing chapter XIX heading")],
    "EIGHT": [("agentesin rebus", "agentes in rebus", "missing space")],
}


def typst_escape(text: str) -> str:
    """Escape the characters that mean something in Typst markup."""
    for ch in ["\\", "#", "*", "$", "<", ">", "@", "[", "]", "`", "~", "_"]:
        text = text.replace(ch, "\\" + ch)
    return text


def clean(text: str) -> str:
    """One paragraph: rejoin its lines, true dashes, then escape."""
    text = re.sub(r"_{5,}", "", text)       # CCEL's separator lines
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace("--", "—")
    return text


def cut_book(lines):
    """Return the lines of the chosen book (heading excluded)."""
    start = next(i for i, l in enumerate(lines) if l.strip() == f"BOOK {BOOK}")
    nxt = ORDER.index(BOOK) + 1
    if nxt < len(ORDER):
        end = next(i for i, l in enumerate(lines) if l.strip() == f"BOOK {ORDER[nxt]}")
    else:
        end = len(lines)
    return lines[start + 1:end]


def main():
    lines = SOURCE.read_text(encoding="utf-8").split("\n")
    book = cut_book(lines)
    joined = "\n".join(book)
    for wrong, right, why in CORRECTIONS.get(BOOK, []):
        if joined.count(wrong) != 1:
            raise SystemExit(f"Correction expected once: {wrong!r} ({why})")
        joined = joined.replace(wrong, right)
    book = joined.split("\n")
    paras = [p for p in re.split(r"\n\s*\n", "\n".join(book)) if p.strip()]
    paras = [p for p in paras if not set(p.strip()) <= set("_")]

    # Outler's summary is the first paragraph; the notes are the trailing
    # paragraphs that start with "[n] ".
    summary = clean(paras[0])
    k = len(paras)
    while k > 0 and re.match(r"^\s*\[\d+\]\s", paras[k - 1]):
        k -= 1
    body, note_paras = paras[1:k], paras[k:]
    notes = {}
    for p in note_paras:
        m = re.match(r"^\s*\[(\d+)\]\s+(.*)$", p, flags=re.S)
        txt = re.sub(r"\s+", " ", m.group(2)).strip().rstrip("_").strip()
        notes[m.group(1)] = txt.replace("--", "—")

    endnotes = []                      # explanatory notes, in order

    def marker(m):
        n = m.group(1)
        note = notes.get(n)
        if note is None:
            return ""                  # a stray marker: drop it
        if SCRIPTURE.match(note):
            return f'#ref[({typst_escape(note.rstrip("."))})]'
        endnotes.append(note)
        return f"#super[{len(endnotes)}]"

    out = [f"// content.typ -- Confessions, Book {BOOK.title()}, in Outler's translation.",
           "// GENERATED by extract.py from source/outler-confessions.txt: edit the",
           "// script, not this file.", "",
           f'#chapter(none, "Book {BOOK.title()}")', "",
           f"#summary[{typst_escape(clean(summary))}]", ""]
    for p in body:
        p = clean(p)
        m = re.match(r"^CHAPTER ([IVXLC]+)$", p)
        if m:
            out += [f'#section("Chapter {m.group(1)}")', ""]
            continue
        num = None
        m = re.match(r"^(\d+)\.\s+(.*)$", p)
        if m:
            num, p = m.group(1), m.group(2)
        # escape first, then turn the note markers (escaped as \[n\]) into
        # Typst calls
        p = typst_escape(p)
        p = re.sub(r"\s*\\\[(\d+)\\\]", lambda mm: " " + marker(mm) if notes.get(mm.group(1)) and SCRIPTURE.match(notes[mm.group(1)]) else marker(mm), p)
        if num:
            p = f"#pnum[{num}] " + p
        out += [p, ""]
    (HERE / "content.typ").write_text("\n".join(out), encoding="utf-8")

    nt = ["// notes.typ -- Outler's explanatory notes for this book, renumbered.",
          "// GENERATED by extract.py.", ""]
    for i, n in enumerate(endnotes, 1):
        nt += [f"+ {typst_escape(n)}", ""]
    (HERE / "notes.typ").write_text("\n".join(nt), encoding="utf-8")
    words = len(" ".join(body).split())
    print(f"content.typ written: Book {BOOK}, about {words} words, "
          f"{len(endnotes)} endnotes, {len(notes) - len(endnotes)} Scripture references inline")


if __name__ == "__main__":
    main()
