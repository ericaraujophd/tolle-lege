#!/usr/bin/env python3
"""
extract.py  (title No. 02, Pascal, On Diversion)
================================================

Turns the selected fragments of Pascal's Pensees, in W. F. Trotter's
translation, into Typst markup (content.typ) for this booklet.

What this script does, in plain words
-------------------------------------
1. Reads source/pensees-trotter.txt: the whole Trotter translation (see the
   header of that file for where it came from). In it every fragment starts
   with a line holding only its number (Brunschvicg's numbering, the one
   Trotter uses), followed by the text.
2. Picks the fragments listed in PARTS below, in that order, grouped in
   three parts. The order is the editorial argument of the booklet:
     Part One   our restless condition (why we cannot sit still)
     Part Two   diversion (what we do about it)
     Part Three the remedy (what Pascal thinks would actually help)
3. Cleans each fragment:
     * removes the footnote markers like [69] (the notes are almost all
       references to Montaigne; the intro mentions that debt instead);
     * turns Trotter's "--" into a true dash, since this is the
       translator's punctuation and should look as printed;
     * pulls out a leading title such as "_Diversion._--" so the booklet
       can set it as the fragment's small heading;
     * keeps Trotter's square brackets [ ... ] around passages Pascal
       himself struck out in the manuscript (explained in the intro).
4. Writes content.typ: a #chapter(...) for each part and a #section(...)
   (from tools/templates/booklet.typ) for each fragment, followed by its
   paragraphs. content.typ is committed, so building does not need this
   script; run it only if you change the selection.

CORRECTIONS lists every change made to the words of the translation (one
transcription slip so far). TRIMS lists the one fragment shortened on purpose (425, which runs on into
an argument about the philosophers; we keep its opening, which is the part
everyone quotes). Each trim must match exactly once or the script stops.

Run it from anywhere:   python3 titles/02-pascal-on-diversion/extract.py
"""

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source" / "pensees-trotter.txt"

# ---------------------------------------------------------------------------
# THE SELECTION: (part label, part title, [fragment numbers in order])
# ---------------------------------------------------------------------------
PARTS = [
    ("Part One", "Our Restless Condition", [127, 129, 131, 172, 205, 206]),
    ("Part Two", "Diversion", [139, 140, 141, 142, 143, 164, 165, 166, 168,
                               169, 170, 171]),
    ("Part Three", "The Remedy", [146, 347, 348, 425]),
]

# ---------------------------------------------------------------------------
# TRIMS: (fragment, text that starts the part we DROP, why)
# Everything from that text to the end of the fragment is left out.
# ---------------------------------------------------------------------------
TRIMS = [
    (425, "Some seek good in authority",
     "keep the opening; the rest is a long digression on the philosophers"),
]

# ---------------------------------------------------------------------------
# CORRECTIONS: (fragment, wrong text, right text, why)
# Slips in the online transcription, fixed to match the printed translation.
# Each "wrong text" must occur exactly once in its fragment, or the script
# stops (so a changed source is noticed, not silently skipped).
# ---------------------------------------------------------------------------
CORRECTIONS = [
    (171, "and yet this it the greatest", "and yet this is the greatest",
     "transcription slip: 'it' for 'is'"),
]

# Fragment 425 opens with a heading that belongs to Pascal's plan for the
# whole book ("Second part.--That man without faith..."), not to this
# passage. It is dropped; the fragment number still identifies it.
DROP_LEADING = {
    425: "_Second part.--That man without faith cannot know the true good, nor\njustice._",
}


def read_fragments():
    """Return {number: text} for every fragment in the source file.

    A fragment header is a line holding only a number (1 to 3 digits).
    The text runs until the next such line. The notes at the end of the file
    start with a line reading NOTES, where we stop."""
    text = SOURCE.read_text(encoding="utf-8")
    text = text.split("\nNOTES\n")[0]
    fragments, current, buf = {}, None, []
    for line in text.split("\n"):
        if re.fullmatch(r"\d{1,3}", line.strip()):
            if current is not None:
                fragments[current] = "\n".join(buf).strip()
            current, buf = int(line.strip()), []
        elif current is not None:
            buf.append(line)
    if current is not None:
        fragments[current] = "\n".join(buf).strip()
    return fragments


def typst_escape(text: str) -> str:
    """Escape Typst's special characters, EXCEPT the underscore, which
    Trotter uses for italics exactly as Typst does (_word_)."""
    for ch in ["\\", "#", "*", "$", "<", ">", "@", "[", "]", "`", "~"]:
        text = text.replace(ch, "\\" + ch)
    return text


def clean(n: int, text: str):
    """Return (title or None, [paragraphs]) for fragment n."""
    if n in DROP_LEADING:
        lead = DROP_LEADING[n]
        if not text.startswith(lead):
            raise SystemExit(f"Fragment {n}: expected leading text not found")
        text = text[len(lead):].strip()
    for frag, start, why in TRIMS:
        if frag == n:
            if text.count(start) != 1:
                raise SystemExit(f"Trim for {n} expected once: {start!r} ({why})")
            text = text[: text.index(start)].strip()

    for frag, wrong, right, why in CORRECTIONS:
        if frag == n:
            if text.count(wrong) != 1:
                raise SystemExit(f"Correction for {n} expected once: {wrong!r} ({why})")
            text = text.replace(wrong, right)

    text = re.sub(r"\[\d+\]", "", text)          # footnote markers
    # A leading title: "_Diversion._--" or "_A thinking reed._--".
    title = None
    m = re.match(r"_([^_]+?)\._--", text)
    if m:
        title = m.group(1)
        text = text[m.end():].lstrip()

    paras = []
    for p in re.split(r"\n\s*\n", text):
        p = re.sub(r"\s+", " ", p).strip()
        if not p:
            continue
        p = p.replace("--", "—")              # Trotter's dash, as printed
        p = p.replace("...", "…")
        paras.append(typst_escape(p))
    return title, paras


def to_typst(fragments) -> str:
    out = []
    for label, name, numbers in PARTS:
        out.append(f'#chapter("{label}", "{name}")\n')
        for n in numbers:
            title, paras = clean(n, fragments[n])
            if title:
                out.append(f'#section("{n}", title: "{typst_escape(title)}")\n')
            else:
                out.append(f'#section("{n}")\n')
            for p in paras:
                out.append(p + "\n")
            out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    frags = read_fragments()
    markup = to_typst(frags)
    (HERE / "content.typ").write_text(markup, encoding="utf-8")
    n = sum(len(nums) for _, _, nums in PARTS)
    words = len(re.sub(r"#\w+\([^)]*\)", "", markup).split())
    print(f"content.typ written: {n} fragments, about {words} words")
