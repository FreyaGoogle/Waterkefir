#!/usr/bin/env python3
"""
build_epub.py — Zet tekstbestanden uit input/ om naar één EPUB in output/bundel.epub
"""

import sys
import subprocess
import os
from pathlib import Path
from datetime import datetime


# ---------------------------------------------------------------------------
# Afhankelijkheden automatisch installeren
# ---------------------------------------------------------------------------
def _ensure_packages():
    missing = []
    try:
        import ebooklib  # noqa: F401
    except ImportError:
        missing.append("ebooklib")
    try:
        from bs4 import BeautifulSoup  # noqa: F401
    except ImportError:
        missing.append("beautifulsoup4")
    if missing:
        print(f"Ontbrekende pakketten gevonden: {', '.join(missing)}. Worden nu geïnstalleerd...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
        print("Installatie voltooid.\n")


_ensure_packages()

# Na eventuele installatie pas importeren
from ebooklib import epub  # noqa: E402
from bs4 import BeautifulSoup  # noqa: E402, F401


# ---------------------------------------------------------------------------
# Constanten
# ---------------------------------------------------------------------------
INPUT_DIR = Path(__file__).parent / "input"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_FILE = OUTPUT_DIR / "bundel.epub"

BUNDLE_TITLE = "AI Report Bundel"
BUNDLE_LANGUAGE = "nl"
BUNDLE_LOCALE = "nl-NL"

STYLE = """
body {
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 1em;
    line-height: 1.75;
    margin: 2em 2.5em;
    color: #1a1a1a;
    background-color: #ffffff;
}

h1 {
    font-size: 1.6em;
    font-weight: bold;
    margin-top: 1em;
    margin-bottom: 0.25em;
    line-height: 1.3;
    color: #111111;
}

h2 {
    font-size: 1.25em;
    font-weight: bold;
    margin-top: 2em;
    margin-bottom: 0.5em;
    color: #222222;
    border-bottom: 1px solid #cccccc;
    padding-bottom: 0.25em;
}

p.meta {
    font-size: 0.85em;
    color: #666666;
    margin-top: 0;
    margin-bottom: 1.5em;
    font-style: italic;
}

p {
    margin-top: 0;
    margin-bottom: 1em;
    text-align: left;
}

ul {
    margin-top: 0;
    margin-bottom: 1em;
    padding-left: 1.5em;
}

li {
    margin-bottom: 0.4em;
    line-height: 1.6;
}

hr {
    border: none;
    border-top: 1px solid #dddddd;
    margin: 2.5em 0;
}

.cover {
    text-align: center;
    padding: 4em 2em;
}

.cover h1 {
    font-size: 2em;
    margin-bottom: 0.5em;
}

.cover p {
    font-size: 1em;
    color: #555555;
}

.toc-list {
    list-style: none;
    padding-left: 0;
}

.toc-category {
    font-weight: bold;
    font-size: 1em;
    margin-top: 1.5em;
    margin-bottom: 0.4em;
    color: #333333;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-size: 0.8em;
}

.toc-item {
    margin: 0.3em 0 0.3em 1em;
}

.toc-item a {
    text-decoration: none;
    color: #1a1a1a;
}
"""


# ---------------------------------------------------------------------------
# Parseren van tekstbestanden
# ---------------------------------------------------------------------------
def parse_text_file(path: Path) -> dict:
    """Lees één tekstbestand en geef een dict terug met metadata + html-body."""
    raw = path.read_text(encoding="utf-8")

    # Splits op scheidingslijn ---
    if "---" in raw:
        header_part, body_part = raw.split("---", 1)
    else:
        header_part, body_part = "", raw

    # Metadata uit header
    meta = {"TITEL": path.stem, "DATUM": "", "CATEGORIE": "Algemeen"}
    for line in header_part.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip().upper()
            value = value.strip()
            if key in meta:
                meta[key] = value

    # Body omzetten naar HTML
    html_body = _body_to_html(body_part.strip())

    return {
        "titel": meta["TITEL"],
        "datum": meta["DATUM"],
        "categorie": meta["CATEGORIE"],
        "html_body": html_body,
        "filename": path.stem,
    }


def _body_to_html(text: str) -> str:
    """Verwerk platte tekst naar HTML met <p>- en <ul>-tags."""
    paragraphs = text.split("\n\n")
    html_parts = []

    for block in paragraphs:
        block = block.strip()
        if not block:
            continue

        lines = block.splitlines()

        # Controleer of alle niet-lege regels bullets zijn
        bullet_lines = [l for l in lines if l.strip().startswith("- ")]
        non_bullet_lines = [l for l in lines if l.strip() and not l.strip().startswith("- ")]

        if bullet_lines and not non_bullet_lines:
            # Volledig bullet-blok
            items = "".join(
                f"<li>{_escape(l.strip()[2:])}</li>"
                for l in lines
                if l.strip().startswith("- ")
            )
            html_parts.append(f"<ul>{items}</ul>")
        elif bullet_lines and non_bullet_lines:
            # Gemengd blok: splits eerst tekst dan bullets
            current_text_lines = []
            current_bullet_lines = []
            for line in lines:
                if line.strip().startswith("- "):
                    if current_text_lines:
                        html_parts.append(f"<p>{_escape(' '.join(current_text_lines))}</p>")
                        current_text_lines = []
                    current_bullet_lines.append(line.strip()[2:])
                else:
                    if current_bullet_lines:
                        items = "".join(f"<li>{_escape(b)}</li>" for b in current_bullet_lines)
                        html_parts.append(f"<ul>{items}</ul>")
                        current_bullet_lines = []
                    if line.strip():
                        current_text_lines.append(line.strip())
            if current_text_lines:
                html_parts.append(f"<p>{_escape(' '.join(current_text_lines))}</p>")
            if current_bullet_lines:
                items = "".join(f"<li>{_escape(b)}</li>" for b in current_bullet_lines)
                html_parts.append(f"<ul>{items}</ul>")
        else:
            # Gewone alinea — voeg regels samen
            joined = " ".join(l.strip() for l in lines if l.strip())
            html_parts.append(f"<p>{_escape(joined)}</p>")

    return "\n".join(html_parts)


def _escape(text: str) -> str:
    """Minimale HTML-escaping."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------------------
# EPUB-bouwstenen aanmaken
# ---------------------------------------------------------------------------
def make_cover_page(book: epub.EpubBook, title: str, date_str: str) -> epub.EpubHtml:
    content = (
        "<html xmlns='http://www.w3.org/1999/xhtml' xml:lang='nl' lang='nl'>"
        "<head><title>Cover</title>"
        "<link rel='stylesheet' type='text/css' href='Styles/style.css'/>"
        "</head><body>"
        f"<div class='cover'><h1>{_escape(title)}</h1><p>{_escape(date_str)}</p></div>"
        "</body></html>"
    )
    page = epub.EpubHtml(title="Cover", file_name="cover.xhtml", lang="nl")
    page.content = content
    return page


def make_toc_page(book: epub.EpubBook, articles: list) -> epub.EpubHtml:
    """Bouw een HTML-inhoudsopgave, gegroepeerd op categorie."""
    categories = {}
    for art in articles:
        cat = art["categorie"]
        categories.setdefault(cat, []).append(art)

    items_html = ""
    multi_cat = len(categories) > 1

    for cat, arts in categories.items():
        if multi_cat:
            items_html += f'<li class="toc-category">{_escape(cat)}</li>\n'
        for art in arts:
            link = f'Text/{art["filename"]}.xhtml'
            items_html += (
                f'<li class="toc-item">'
                f'<a href="{link}">{_escape(art["titel"])}</a>'
                f'</li>\n'
            )

    content = (
        "<html xmlns='http://www.w3.org/1999/xhtml' xml:lang='nl' lang='nl'>"
        "<head><title>Inhoudsopgave</title>"
        "<link rel='stylesheet' type='text/css' href='Styles/style.css'/>"
        "</head><body>"
        "<h1>Inhoudsopgave</h1>"
        f"<ul class='toc-list'>{items_html}</ul>"
        "</body></html>"
    )
    page = epub.EpubHtml(title="Inhoudsopgave", file_name="toc.xhtml", lang="nl")
    page.content = content
    return page


def make_article_page(book: epub.EpubBook, art: dict) -> epub.EpubHtml:
    meta_parts = []
    if art["datum"]:
        meta_parts.append(art["datum"])
    if art["categorie"]:
        meta_parts.append(art["categorie"])
    meta_str = " · ".join(meta_parts)

    content = (
        "<html xmlns='http://www.w3.org/1999/xhtml' xml:lang='nl' lang='nl'>"
        f"<head><title>{_escape(art['titel'])}</title>"
        "<link rel='stylesheet' type='text/css' href='../Styles/style.css'/>"
        "</head><body>"
        f"<h1>{_escape(art['titel'])}</h1>"
        f"<p class='meta'>{_escape(meta_str)}</p>"
        "<hr/>"
        f"{art['html_body']}"
        "</body></html>"
    )
    page = epub.EpubHtml(
        title=art["titel"],
        file_name=f'Text/{art["filename"]}.xhtml',
        lang="nl",
    )
    page.content = content
    return page


# ---------------------------------------------------------------------------
# Hoofd-build-functie
# ---------------------------------------------------------------------------
def build_epub():
    # Invoerbestanden ophalen
    txt_files = sorted(INPUT_DIR.glob("*.txt"))
    if not txt_files:
        print(f"Geen .txt-bestanden gevonden in {INPUT_DIR}. Voeg bestanden toe en probeer opnieuw.")
        sys.exit(1)

    print(f"{len(txt_files)} tekstbestand(en) gevonden in {INPUT_DIR}.")

    articles = [parse_text_file(f) for f in txt_files]

    # EPUB-boek aanmaken
    book = epub.EpubBook()
    book.set_identifier("ai-report-bundel-" + datetime.now().strftime("%Y%m%d%H%M%S"))
    book.set_title(BUNDLE_TITLE)
    book.set_language(BUNDLE_LANGUAGE)
    book.add_metadata("DC", "language", BUNDLE_LOCALE)

    today = datetime.now().strftime("%d %B %Y").lstrip("0")
    book.add_metadata("DC", "date", datetime.now().strftime("%Y-%m-%d"))

    # Stijlblad
    style_item = epub.EpubItem(
        uid="style",
        file_name="Styles/style.css",
        media_type="text/css",
        content=STYLE.encode("utf-8"),
    )
    book.add_item(style_item)

    # Cover
    cover_page = make_cover_page(book, BUNDLE_TITLE, today)
    book.add_item(cover_page)

    # Artikelpagina's
    article_pages = []
    for art in articles:
        page = make_article_page(book, art)
        book.add_item(page)
        article_pages.append(page)

    # Inhoudsopgave (HTML)
    toc_page = make_toc_page(book, articles)
    book.add_item(toc_page)

    # Leesvolgorde (spine)
    book.spine = ["nav", cover_page, toc_page] + article_pages

    # Navigatie-TOC (NCX / nav)
    categories = {}
    for art, page in zip(articles, article_pages):
        categories.setdefault(art["categorie"], []).append((art, page))

    multi_cat = len(categories) > 1
    toc_entries = []

    if multi_cat:
        for cat, items in categories.items():
            section_links = [epub.Link(p.file_name, a["titel"], a["filename"]) for a, p in items]
            toc_entries.append((epub.Section(cat), section_links))
    else:
        for art, page in zip(articles, article_pages):
            toc_entries.append(epub.Link(page.file_name, art["titel"], art["filename"]))

    book.toc = toc_entries

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Wegschrijven
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    epub.write_epub(str(OUTPUT_FILE), book)
    print(f"EPUB aangemaakt: {OUTPUT_FILE}")


if __name__ == "__main__":
    build_epub()
