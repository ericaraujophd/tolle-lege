#!/usr/bin/env python3
"""
extract.py  (title No. 01, Aquinas, On Curiosity)
==================================================

STEP 1 OF THE PIPELINE: turn the New Advent web pages into clean Typst markup.

What this script does, in plain words
-------------------------------------
1. Reads the two saved web pages (source/q166.htm and source/q167.htm). These are the
   pages from https://www.newadvent.org/summa/3166.htm and 3167.htm, which
   carry the 1920 English Dominican translation of the Summa Theologiae.
   That translation is in the public domain in the US.
2. Pulls out each article title and each paragraph, throwing away the
   site navigation, the hyperlinks and the copyright footer of the website
   (the website's own HTML is not what we reproduce, only the 1920 text).
3. Applies a short, explicit list of corrections (CORRECTIONS below). These
   fix transcription slips in the online edition (for example "On like
   manner" where the printed 1920 text reads "In like manner"). Every
   correction is listed so you can see exactly what was changed.
4. Writes `content.typ` (in this title folder), which book.typ evaluates.
   content.typ is committed to the repository, so building the PDFs does NOT
   need this script or BeautifulSoup; run it only if you change the source
   pages or the corrections.
   The labels "Objection 1.", "On the contrary,", "I answer that," and
   "Reply to Objection 1." are set in bold so the reader can see the
   structure of a scholastic article at a glance.

Why a separate step?
--------------------
Keeping the text extraction separate from the layout means that, for the
next booklet (Pascal, Augustine, Brother Lawrence...), you only write a new
extract step. The template, the cover and the imposition (all in tools/) stay
the same.

Run it from anywhere:   python3 titles/01-aquinas-on-curiosity/extract.py
(or let the top-level build do it:  python3 build.py --extract)
"""

import json
import re
from pathlib import Path

from bs4 import BeautifulSoup  # HTML parser; installed in most Python setups

HERE = Path(__file__).parent

# The saved web pages, in reading order. Each one is one "Question".
SOURCES = ["source/q166.htm", "source/q167.htm"]

# ---------------------------------------------------------------------------
# CORRECTIONS
# ---------------------------------------------------------------------------
# Each entry is (wrong text, right text, why). The script REFUSES to run if a
# "wrong text" is not found exactly once. That guard matters: if the source
# changes, we want to know, rather than silently skipping a fix.
CORRECTIONS = [
    ("curiosity. wherefore, on account", "curiosity. Wherefore, on account",
     "sentence starts lowercase in the online text"),
    ("nature inclines us. chiefly", "nature inclines us chiefly",
     "stray period in the online text"),
    ("(Ethic. ii, 93)", "(Ethic. ii, 9)",
     "the reference is Ethics book ii, chapter 9"),
    ("As stated above (141, 3,4,5)", "As stated above (II-II:141:3-5)",
     "make the cross-reference match the style of the others"),
    ("Jerome [Comment. in Ep. ad Ephes. iv, 17 says:",
     "Jerome (Comment. in Ep. ad Ephes. iv, 17) says:",
     "unclosed bracket in the online text"),
    ("On like manner", "In like manner", "transcription slip"),
    ("On the second place", "In the second place", "transcription slip"),
    ("detraction. on the other hand", "detraction. On the other hand",
     "sentence starts lowercase in the online text"),
]

# Quotation marks in the online text sometimes have a stray space inside them,
# e.g. '" Knowledge puffeth up,"'. These regexes close that gap.
SPACE_FIXES = [
    (re.compile(r'(^|[\s(])" (\w)'), r'\1"\2'),   # opening quote + space
    (re.compile(r'(\w) "([\s,.;:)]|$)'), r'\1"\2'),  # space + closing quote
]

# The structural labels that open a paragraph in a scholastic article.
LABEL = re.compile(
    r"^(Objection \d+\.|On the contrary,|I answer that,|Reply to Objection \d+\.)\s*"
)


def clean(text: str) -> str:
    """Collapse whitespace and fix the spacing the HTML-to-text step leaves
    around punctuation (BeautifulSoup inserts a space at every link)."""
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r" ([,.;:?!)\]])", r"\1", text)  # "word ," -> "word,"
    text = re.sub(r"([(\[]) ", r"\1", text)        # "( word" -> "(word"
    for pattern, repl in SPACE_FIXES:
        text = pattern.sub(repl, text)
    return text


def extract():
    """Return a list of questions: [{title, articles: [{title, paras}]}]."""
    questions = []
    for name in SOURCES:
        soup = BeautifulSoup((HERE / name).read_text(encoding="utf-8", errors="replace"),
                             "html.parser")
        q = {"title": clean(soup.find("h1").get_text(" ")), "articles": []}
        current = None
        # New Advent puts each article title in an <h2> and every paragraph
        # (objections, answer, replies) in a <p>. Anything before the first
        # article heading (the table of contents) is skipped because
        # `current` is still None.
        for el in soup.find_all(["h2", "p"]):
            t = clean(el.get_text(" "))
            if el.name == "h2" and t.startswith("Article"):
                current = {"title": t, "paras": []}
                q["articles"].append(current)
            elif el.name == "p" and current is not None:
                # The footer starts with the edition credit; stop there.
                if t.startswith("The Summa Theolog") or "Copyright" in t:
                    current = None
                    continue
                current["paras"].append(t)
        questions.append(q)
    return questions


def apply_corrections(questions):
    """Apply CORRECTIONS, checking each matches exactly once in the whole text."""
    # Work on a JSON string so a single search covers every paragraph.
    blob = json.dumps(questions, ensure_ascii=False)
    for wrong, right, why in CORRECTIONS:
        n = blob.count(wrong)
        if n != 1:
            raise SystemExit(f"Correction expected once, found {n}: {wrong!r} ({why})")
        blob = blob.replace(wrong, right)
    return json.loads(blob)


def typst_escape(text: str) -> str:
    """Escape characters that mean something in Typst markup.
    In Typst, *bold*, _italic_, #code, $math$, <label>, @ref, [ ] and \\ are
    special. The Summa text contains brackets and the odd asterisk-free
    symbols, so we escape conservatively."""
    for ch in ["\\", "#", "*", "_", "$", "<", ">", "@", "[", "]", "`", "~"]:
        text = text.replace(ch, "\\" + ch)
    # Typst turns "--" into an en dash; that's fine. "..." stays literal.
    return text


def short_title(article_title: str) -> str:
    """'Article 1. Whether the proper matter...' -> ('1', 'Whether the proper matter...')."""
    m = re.match(r"Article (\d+)\. (.*)", article_title)
    return m.group(1), m.group(2)


def to_typst(questions) -> str:
    """Build the Typst markup for the body of the booklet."""
    out = []
    for q in questions:
        # "Question 166. Studiousness" -> number 166, name Studiousness
        num, name = re.match(r"Question (\d+)\. (.*)", q["title"]).groups()
        # #question(...) and #article(...) are functions defined in
        # tools/templates/booklet.typ and passed in by book.typ.
        out.append(f'#question("{num}", "{name}")\n')
        for a in q["articles"]:
            anum, atitle = short_title(a["title"])
            out.append(f'#article("{anum}", "{typst_escape(atitle)}")\n')
            for p in a["paras"]:
                m = LABEL.match(p)
                if m:
                    label, rest = m.group(1), p[m.end():]
                    out.append(f"*{label}* {typst_escape(rest)}\n")
                else:
                    out.append(typst_escape(p) + "\n")
                out.append("")  # blank line = new paragraph in Typst
    return "\n".join(out)


if __name__ == "__main__":
    qs = apply_corrections(extract())
    (HERE / "content.typ").write_text(to_typst(qs), encoding="utf-8")
    words = sum(len(p.split()) for q in qs for a in q["articles"] for p in a["paras"])
    print(f"content.typ written: {len(qs)} questions, {words} words")
