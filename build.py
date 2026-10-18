#!/usr/bin/env python3
"""
build.py  --  ONE COMMAND TO BUILD EVERYTHING
=============================================

    python3 build.py                     # every title + the website, into docs/
    python3 build.py --extract           # also re-run each title's extract.py
    python3 build.py --back-offset 2 1   # print files corrected for YOUR printer
                                         # (written into build/, never docs/)

Requirements:  pip install -r requirements.txt   (typst, pypdf, reportlab;
beautifulsoup4 only for --extract)


WHAT IT DOES, FOR EACH TITLE IN titles/
---------------------------------------
A title is a folder in titles/ with a title.toml. If its status is
"available", the build:

  1. (with --extract) runs the title's extract.py, which regenerates its
     content.typ from the saved source text. Normally content.typ is already
     committed, so this step is skipped.

  2. compiles book.typ into the READING COPY, one 3.5 x 5 in page per PDF
     page, in reading order. It compiles twice: first with one notes page to
     count the pages, then with as many ruled notes pages as needed to make
     the total a multiple of 4 (a folded sheet carries exactly 4 pages).
     Example: 23 pages of text + 1 notes page = 24, which is already a
     multiple of 4, so 1 notes page. 25 pages of text would get 3.

  3. compiles cover.typ into the 4 cover pages (front, inside front, inside
     back, back), telling it the interior page count for the spec sheet.

  4. imposes both with tools/impose.py: pages placed on US Letter sheets in
     saddle-stitch order, two copies per sheet, with the cut line, the corner
     crosses and the sheet labels. These are the files people PRINT.

  5. renders the front cover as a PNG for the website.

Titles with status "in-preparation" only get a card on the website.

Then it writes the duplex alignment test and the website page
(docs/index.html) from tools/site/index.template.html, with one card per
title. GitHub Pages serves the docs/ folder as the website.


WHY docs/ HOLDS THE PDFs
------------------------
The website links straight to the PDFs, so they live where the website
lives: docs/books/<slug>/. They are committed to the repository on purpose,
so anyone can download and print without installing anything.
"""

import argparse
import html
import shutil
import subprocess
import sys
import tomllib
from datetime import date
from pathlib import Path

import typst
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
TITLES = ROOT / "titles"
DOCS = ROOT / "docs"
SITE_TEMPLATES = ROOT / "tools" / "site"

# tools/impose.py is imported as a module so we can call its functions.
sys.path.insert(0, str(ROOT / "tools"))
import impose  # noqa: E402

MIN_NOTES = 1   # fewest ruled notes pages (the last one carries the colophon)
REPRODUCIBLE_TIMESTAMP = 1767225600   # 2026-01-01 00:00 UTC, see compile_typst


# ------------------------------------------------------------------ helpers
def page_count(pdf: Path) -> int:
    return len(PdfReader(str(pdf)).pages)


def compile_typst(src: Path, out: Path, **inputs) -> None:
    """Compile a Typst file with the REPOSITORY as Typst's root folder, so the
    title files can import "/tools/templates/...". `inputs` become
    sys.inputs inside Typst (all values must be strings)."""
    out.parent.mkdir(parents=True, exist_ok=True)
    fmt = out.suffix.lstrip(".")
    kwargs = {
        "root": str(ROOT),
        "sys_inputs": {k: str(v) for k, v in inputs.items()},
        # A FIXED timestamp makes the PDFs reproducible: building twice gives
        # byte-identical files, so git only shows a PDF as changed when its
        # content really changed (not just its embedded creation date).
        "timestamp": REPRODUCIBLE_TIMESTAMP,
    }
    if fmt == "png":
        kwargs.update(format="png", ppi=160)
    typst.compile(str(src), output=str(out), **kwargs)


def human_size(path: Path) -> str:
    n = path.stat().st_size
    return f"{n / 1024:.0f} KB" if n < 1024 * 1024 else f"{n / 1024 / 1024:.1f} MB"


def load_titles():
    """All titles, sorted by folder name (which starts with the number)."""
    titles = []
    for folder in sorted(p for p in TITLES.iterdir() if (p / "title.toml").exists()):
        meta = tomllib.loads((folder / "title.toml").read_text(encoding="utf-8"))
        meta["folder"] = folder
        titles.append(meta)
    return titles


# ------------------------------------------------------------- one title
def build_title(meta, out_dir: Path, offset_mm, extract: bool, thumbnail: bool):
    """Build one available title into out_dir. Returns facts for the site."""
    folder, slug = meta["folder"], meta["slug"]
    print(f"\n== {meta['number']}  {meta['title']}  ({slug})")

    # 1. Text extraction (optional; content.typ is normally committed).
    if extract and (folder / "extract.py").exists():
        subprocess.run([sys.executable, str(folder / "extract.py")], check=True)

    reading = out_dir / f"{slug}-reading.pdf"
    cover_pages = out_dir / f"{slug}-cover-pages.pdf"     # temporary
    interior = out_dir / f"{slug}-interior.pdf"
    cover = out_dir / f"{slug}-cover.pdf"

    # 2. Reading copy, padded to a multiple of 4 pages with notes pages.
    compile_typst(folder / "book.typ", reading, notes=MIN_NOTES)
    first = page_count(reading)
    text_pages = first - MIN_NOTES
    total = -(-first // 4) * 4                   # round UP to a multiple of 4
    notes = total - text_pages
    compile_typst(folder / "book.typ", reading, notes=notes)
    got = page_count(reading)
    if got != total:
        # Would happen if, say, a ruled page overflowed onto a second page.
        sys.exit(f"{slug}: expected {total} pages after adding {notes} notes pages, got {got}")
    print(f"   reading copy: {text_pages} pages of text + {notes} notes = {total} pages")

    # 3. Cover (the spec sheet prints the interior page count).
    compile_typst(folder / "cover.typ", cover_pages, pages=total)

    # 4. Imposition: the files to print.
    impose.impose(str(reading), str(interior), f"{meta['number']} interior", offset_mm)
    impose.impose(str(cover_pages), str(cover), f"{meta['number']} cover", offset_mm)
    cover_pages.unlink()

    # 5. Front-cover picture for the website. Typst writes one PNG per page
    #    ({p} is the page number); we keep page 1 and delete the rest.
    if thumbnail:
        compile_typst(folder / "cover.typ", out_dir / "cover-{p}.png", pages=total)
        for png in out_dir.glob("cover-*.png"):
            if png.name == "cover-1.png":
                png.replace(out_dir / "cover.png")
            else:
                png.unlink()

    return {
        "pages": total,
        "sheets": total // 4,
        "files": {
            "interior": interior,
            "cover": cover,
            "reading": reading,
        },
    }


# ---------------------------------------------------------------- website
def esc(s) -> str:
    return html.escape(str(s), quote=True)


def card_html(meta, facts) -> str:
    """One book card for the website. Available titles get a cover picture
    and download buttons; titles in preparation get a placeholder."""
    slug = meta["slug"]
    head = f"""
      <p class="num">{esc(meta['number'])}</p>
      <h3>{esc(meta['title'])}</h3>
      <p class="sub">{esc(meta.get('subtitle', ''))}</p>
      <p class="author">{esc(meta['author'])}</p>
      <p class="summary">{esc(meta.get('summary', ''))}</p>"""
    if facts is None:
        return f"""
    <article class="book soon">
      <div class="cover-wrap placeholder"><span>In preparation</span></div>
      <div class="info">{head}
        <p class="meta">{esc(meta.get('translation', ''))}</p>
      </div>
    </article>"""
    f = facts["files"]
    base = f"books/{slug}/"
    return f"""
    <article class="book" id="{esc(slug)}">
      <div class="cover-wrap"><img src="{base}cover.png" alt="Front cover of {esc(meta['title'])}" loading="lazy"></div>
      <div class="info">{head}
        <p class="meta">{facts['pages']} pages · {facts['sheets']} interior sheets + 1 cover sheet · {esc(meta['translation'])}</p>
        <div class="downloads">
          <a class="btn primary" href="{base}{f['interior'].name}" download>Interior <small>{facts['sheets']} sheets · {human_size(f['interior'])}</small></a>
          <a class="btn primary" href="{base}{f['cover'].name}" download>Cover <small>1 sheet · {human_size(f['cover'])}</small></a>
          <a class="btn" href="{base}{f['reading'].name}">Read online <small>{human_size(f['reading'])}</small></a>
        </div>
      </div>
    </article>"""


def write_site(cards):
    template = (SITE_TEMPLATES / "index.template.html").read_text(encoding="utf-8")
    page = (template
            .replace("{{BOOKS}}", "\n".join(cards))
            .replace("{{UPDATED}}", date.today().strftime("%B %-d, %Y")))
    (DOCS / "index.html").write_text(page, encoding="utf-8")
    (DOCS / "assets").mkdir(parents=True, exist_ok=True)
    shutil.copy(SITE_TEMPLATES / "style.css", DOCS / "assets" / "style.css")
    # An empty .nojekyll file tells GitHub Pages to serve the files as they
    # are, without running them through its Jekyll site generator.
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    print("\nwebsite: docs/index.html")


# ------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Build every title and the website.")
    ap.add_argument("--extract", action="store_true",
                    help="re-run each title's extract.py first (needs beautifulsoup4)")
    ap.add_argument("--back-offset", type=float, nargs=2, metavar=("DX", "DY"),
                    help="correct the back side for YOUR printer (mm right, mm up, as "
                         "measured with the alignment test). Writes into build/ only.")
    ap.add_argument("--only", metavar="SLUG", help="build just this title folder")
    a = ap.parse_args()

    personal = a.back_offset is not None
    offset = tuple(a.back_offset) if personal else (0.0, 0.0)

    cards = []
    for meta in load_titles():
        if a.only and meta["slug"] != a.only:
            continue
        if meta.get("status") != "available":
            print(f"\n== {meta['number']}  {meta['title']}: in preparation (card only)")
            cards.append(card_html(meta, None))
            continue
        out_dir = (ROOT / "build" / meta["slug"]) if personal else (DOCS / "books" / meta["slug"])
        facts = build_title(meta, out_dir, offset, a.extract, thumbnail=not personal)
        cards.append(card_html(meta, facts))

    if personal:
        print(f"\nPrinter-corrected files (back offset {offset} mm) are in build/.")
        return

    (DOCS / "tools").mkdir(parents=True, exist_ok=True)
    impose.alignment_test(str(DOCS / "tools" / "alignment-test.pdf"))
    if not a.only:
        write_site(cards)


if __name__ == "__main__":
    main()
