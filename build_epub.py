"""
Builds a proper reflowable EPUB of The Mother's Code from the same
manuscript/ markdown source used by build_pdf.py. This is the file to
upload to KDP (or any ebook store) — KDP converts EPUB to Kindle format
automatically and it reflows correctly on any device/font size.
"""
import os
import re
import uuid

from ebooklib import epub

HERE = os.path.dirname(__file__)
MANUSCRIPT_DIR = os.path.join(HERE, "manuscript")
BUILD_DIR = os.path.join(HERE, "build")
COVER_PATH = os.path.join(BUILD_DIR, "Cover-The-Mothers-Code.jpg")
OUTPUT_PATH = os.path.join(BUILD_DIR, "The-Mothers-Code.epub")

TITLE = "The Mother's Code"
SUBTITLE = "How to Raise a Child Who Changes the World"
AUTHOR = "Aiz-El Dan"

CHAPTER_FILES = [
    ("01-introduction.md", None),
    ("02-chapter1-belief-effect.md", "1"),
    ("03-chapter2-words-that-build.md", "2"),
    ("04-chapter3-safety-behind-courage.md", "3"),
    ("05-chapter4-letting-them-fall.md", "4"),
    ("06-chapter5-presence-over-perfection.md", "5"),
    ("07-chapter6-mirror-effect.md", "6"),
    ("08-chapter7-purpose-before-pressure.md", "7"),
    ("09-chapter8-the-ripple.md", "8"),
    ("10-chapter9-repair-reflex.md", "9"),
    ("11-chapter10-naming-the-storm.md", "10"),
    ("12-chapter11-comparison-trap.md", "11"),
    ("13-chapter12-gratitude-habit.md", "12"),
    ("14-chapter13-small-hands-real-work.md", "13"),
    ("15-chapter14-screen-in-the-room.md", "14"),
    ("16-chapter15-waiting-well.md", "15"),
    ("17-chapter16-question-behind-question.md", "16"),
    ("18-chapter17-touch-that-tells-truth.md", "17"),
    ("19-chapter18-rhythm-of-rest.md", "18"),
    ("20-chapter19-discipline-shift.md", "19"),
    ("21-chapter20-long-goodbye.md", "20"),
    ("22-chapter21-village-effect.md", "21"),
]

CSS = """
@namespace epub "http://www.idpf.org/2007/ops";
body { font-family: Georgia, "Times New Roman", serif; color: #3D2A2B; line-height: 1.5; margin: 1em; }
h1.chapter-title { text-align: center; font-size: 1.5em; color: #3D2A2B; margin: 0.4em 0 0.9em; }
p.kicker { text-align: center; color: #9C7526; letter-spacing: 2px; font-size: 0.8em; }
h2.section { color: #B0606A; font-size: 1.15em; margin-top: 1.4em; }
p { margin: 0 0 0.9em; text-align: justify; }
p.lead { font-style: italic; }
.tip { background: #F3E6E3; border-radius: 10px; padding: 0.9em 1.1em; margin: 1.2em 0; }
.tip h3 { color: #9C7526; margin: 0 0 0.5em; font-size: 1.05em; }
.tip ul { margin: 0; padding-left: 1.2em; }
.tip li { margin-bottom: 0.5em; }
h1.book-title { text-align: center; font-size: 2.1em; margin-bottom: 0.2em; }
p.book-subtitle { text-align: center; font-style: italic; color: #B0606A; font-size: 1.1em; }
p.byline { text-align: center; color: #9C7526; font-style: italic; }
p.tagline { text-align: center; font-style: italic; }
p.center { text-align: center; }
hr.divider { width: 30%; border: none; border-top: 1px solid #B0894A; margin: 1.6em auto; }
.qr-item { background: #F3E6E3; border-radius: 10px; padding: 0.8em 1em; margin: 0 0 0.9em; }
.qr-item b { color: #3D2A2B; }
"""


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(text):
    text = esc(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
    return text


def read_lines(name):
    with open(os.path.join(MANUSCRIPT_DIR, name), encoding="utf-8") as f:
        return f.read().split("\n")


def chapter_html(fname):
    lines = read_lines(fname)
    out = []
    pending_bullets = []
    in_tip = False

    def flush():
        nonlocal pending_bullets, in_tip
        if pending_bullets:
            items = "".join(f"<li>{b}</li>" for b in pending_bullets)
            if in_tip:
                out.append(f'<div class="tip"><h3>&#10038; Try This</h3><ul>{items}</ul></div>')
            else:
                out.append(f"<ul>{items}</ul>")
            pending_bullets = []

    for l in lines:
        s = l.strip()
        if not s:
            continue
        if s.startswith("## "):
            flush()
            heading = s[3:]
            in_tip = "try this" in heading.lower()
            if not in_tip:
                out.append(f'<h2 class="section">{inline(heading)}</h2>')
        elif s.startswith("# "):
            flush()
            out.append(f'<h1 class="chapter-title">{inline(s[2:])}</h1>')
        elif s.startswith("- "):
            pending_bullets.append(inline(s[2:]))
        else:
            flush()
            out.append(f"<p>{inline(s)}</p>")
    flush()
    return "\n".join(out)


def title_page_html():
    lines = read_lines("00-title-page.md")
    idx = lines.index("\\newpage")
    front = lines[:idx]
    title_txt = subtitle_txt = tagline_txt = byline_txt = ""
    for l in front:
        s = l.strip()
        if s.startswith("# "):
            title_txt = s[2:]
        elif s.startswith("### "):
            subtitle_txt = s[4:]
        elif s.startswith("**") and s.endswith("**"):
            byline_txt = s.strip("*")
        elif s.startswith("*") and s.endswith("*"):
            tagline_txt = s.strip("*")
    return f"""
<h1 class="book-title">{inline(title_txt)}</h1>
<p class="book-subtitle">{inline(subtitle_txt)}</p>
<hr class="divider"/>
<p class="tagline">{inline(tagline_txt)}</p>
<p class="byline">by {inline(byline_txt)}</p>
"""


def copyright_page_html():
    lines = read_lines("00-title-page.md")
    idx = lines.index("\\newpage")
    back = lines[idx + 1:]
    parts = []
    for l in back:
        s = l.strip()
        if s:
            parts.append(f'<p class="center">{inline(s)}</p>')
    return "\n".join(parts)


def quickref_html():
    lines = read_lines("23-quick-reference.md")
    item_re = re.compile(r"^\d+\.\s+\*\*(.+?)\*\*\s+—\s+(.+)$")
    out = ['<h1 class="chapter-title">The Mother\'s Code — Quick Reference</h1>']
    footer = []
    seen = False
    for l in lines:
        s = l.strip()
        m = item_re.match(s)
        if m:
            seen = True
            out.append(f'<div class="qr-item"><b>{inline(m.group(1))}</b><br/>{inline(m.group(2))}</div>')
        elif s.startswith("*") and s.endswith("*") and seen:
            footer.append(s.strip("*"))
    for fl in footer:
        out.append(f'<p class="tagline center">{inline(fl)}</p>')
    return "\n".join(out)


def closing_html():
    return chapter_html("24-closing-letter.md")


def build():
    book = epub.EpubBook()
    book.set_identifier(f"urn:uuid:{uuid.uuid4()}")
    book.set_title(TITLE)
    book.set_language("en")
    book.add_author(AUTHOR)
    book.add_metadata("DC", "description", SUBTITLE)

    with open(COVER_PATH, "rb") as f:
        book.set_cover("cover.jpg", f.read())

    css_item = epub.EpubItem(uid="style", file_name="style/style.css", media_type="text/css", content=CSS)
    book.add_item(css_item)

    def make_page(uid, filename, title, html_body):
        page = epub.EpubHtml(title=title, file_name=filename, lang="en")
        page.content = (
            f"<html><head><title>{esc(title)}</title>"
            f'<link rel="stylesheet" type="text/css" href="style/style.css"/>'
            f"</head><body>{html_body}</body></html>"
        )
        page.add_item(css_item)
        book.add_item(page)
        return page

    spine = ["cover", "nav"]
    toc = []

    title_pg = make_page("title", "title.xhtml", TITLE, title_page_html())
    spine.append(title_pg)

    copyright_pg = make_page("copyright", "copyright.xhtml", "Copyright", copyright_page_html())
    spine.append(copyright_pg)

    for fname, num in CHAPTER_FILES:
        heading = ""
        for l in read_lines(fname):
            s = l.strip()
            if s.startswith("# "):
                heading = s[2:]
                break
        page_id = fname.replace(".md", "")
        pg = make_page(page_id, f"{page_id}.xhtml", heading, chapter_html(fname))
        spine.append(pg)
        toc.append(pg)

    qr_pg = make_page("quickref", "quickref.xhtml", "Quick Reference", quickref_html())
    spine.append(qr_pg)
    toc.append(qr_pg)

    closing_pg = make_page("closing", "closing.xhtml", "A Closing Letter to the Reader", closing_html())
    spine.append(closing_pg)
    toc.append(closing_pg)

    book.toc = tuple(toc)
    book.spine = spine
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    os.makedirs(BUILD_DIR, exist_ok=True)
    epub.write_epub(OUTPUT_PATH, book)
    print(f"Built: {OUTPUT_PATH}")


if __name__ == "__main__":
    build()
