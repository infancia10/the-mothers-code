"""
Builds The Mother's Code into a designed A5 PDF: pastel gradients, gold
vector ornaments (frames, dividers, badges, heart emblem), and card-style
tip boxes. Run generate_assets.py first to produce the background art.
"""
import glob
import io
import os
import re

from reportlab.lib.pagesizes import A5
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak,
    NextPageTemplate, Flowable, KeepTogether, Table, TableStyle
)

HERE = os.path.dirname(__file__)
MANUSCRIPT_DIR = os.path.join(HERE, "manuscript")
ASSETS_DIR = os.path.join(HERE, "assets")
OUTPUT_PATH = os.path.join(HERE, "build", "The-Mothers-Code.pdf")

AUTHOR = "Aiz-El Dan"

PAGE_W, PAGE_H = A5  # 419.53 x 595.28 pt

# ---------------------------------------------------------------- palette --
INK = HexColor("#3D2A2B")
GOLD = HexColor("#B0894A")
GOLD_DARK = HexColor("#8C6B34")
ROSE = HexColor("#B0606A")
CREAM = HexColor("#FDF8F0")
CARD_TINT = HexColor("#F3E6E3")
WHITE = HexColor("#FFFFFF")

STATE = {"chapter_no": None}
TOC_RECORD = {}

# ------------------------------------------------------------- geometry --
SIDE = 42
BODY_TOP, BODY_BOTTOM = 56, 52
OPEN_TOP, OPEN_BOTTOM = 100, 52
TITLE_TOP, TITLE_BOTTOM = 140, 90

# ---------------------------------------------------------- vector art --

FLORAL_PATH = os.path.join(ASSETS_DIR, "bg_floral.png")


def bg(c):
    c.drawImage(FLORAL_PATH, 0, 0, width=PAGE_W, height=PAGE_H)


def gold_divider(c, cx, y, half_width=55):
    c.saveState()
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.9)
    c.line(cx - half_width, y, cx - 9, y)
    c.line(cx + 9, y, cx + half_width, y)
    d = 4.2
    c.setFillColor(GOLD)
    p = c.beginPath()
    p.moveTo(cx, y + d); p.lineTo(cx + d, y); p.lineTo(cx, y - d); p.lineTo(cx - d, y)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()


def gold_heart(c, cx, cy, size, color=GOLD):
    c.saveState()
    c.setFillColor(color)
    r = size * 0.28
    c.circle(cx - r, cy + r * 0.35, r, fill=1, stroke=0)
    c.circle(cx + r, cy + r * 0.35, r, fill=1, stroke=0)
    p = c.beginPath()
    p.moveTo(cx - size * 0.52, cy + r * 0.3)
    p.curveTo(cx - size * 0.52, cy - size * 0.05, cx - size * 0.15, cy - size * 0.35, cx, cy - size * 0.58)
    p.curveTo(cx + size * 0.15, cy - size * 0.35, cx + size * 0.52, cy - size * 0.05, cx + size * 0.52, cy + r * 0.3)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()


def gold_badge(c, cx, cy, r, text, fill=GOLD, text_color=WHITE, font_size=None):
    c.saveState()
    c.setFillColor(fill)
    c.circle(cx, cy, r, fill=1, stroke=0)
    c.setStrokeColor(WHITE)
    c.setLineWidth(0.8)
    c.circle(cx, cy, r - 2.2, fill=0, stroke=1)
    fs = font_size or r * 0.95
    if len(text) > 1:
        fs *= 0.8
    c.setFont("Times-Bold", fs)
    c.setFillColor(text_color)
    c.drawCentredString(cx, cy - fs * 0.36, text)
    c.restoreState()


def footer_pageno(c, page_num):
    c.saveState()
    cx = PAGE_W / 2
    y = 32
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.6)
    c.line(cx - 70, y + 3, cx - 14, y + 3)
    c.line(cx + 14, y + 3, cx + 70, y + 3)
    c.setFillColor(GOLD_DARK)
    c.setFont("Times-Italic", 9)
    c.drawCentredString(cx, y - 1, str(page_num))
    c.restoreState()


# --------------------------------------------------------- page templates --

COVER_IMG = os.path.join(HERE, "build", "pdf-cover-page.jpg")
BACKCOVER_IMG = os.path.join(HERE, "build", "pdf-back-page.jpg")


def on_cover(c, doc):
    c.drawImage(COVER_IMG, 0, 0, width=PAGE_W, height=PAGE_H)


def on_backcover(c, doc):
    c.drawImage(BACKCOVER_IMG, 0, 0, width=PAGE_W, height=PAGE_H)


def on_title(c, doc):
    bg(c)
    gold_heart(c, PAGE_W / 2, PAGE_H - 108, 24)


def on_copyright(c, doc):
    bg(c)
    c.saveState()
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.6)
    c.setStrokeAlpha(0.55)
    c.line(SIDE, PAGE_H - 46, PAGE_W - SIDE, PAGE_H - 46)
    c.restoreState()


def on_chapter_open(c, doc):
    bg(c)
    n = STATE["chapter_no"]
    cy = PAGE_H - 68
    if n:
        gold_badge(c, PAGE_W / 2, cy, 19, n, font_size=16)
    else:
        gold_heart(c, PAGE_W / 2, cy, 18)
    gold_divider(c, PAGE_W / 2, PAGE_H - 98)
    footer_pageno(c, STATE_PAGE_NO(c))


def on_body(c, doc):
    bg(c)
    c.saveState()
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.5)
    c.setStrokeAlpha(0.5)
    c.line(SIDE, PAGE_H - 38, PAGE_W - SIDE, PAGE_H - 38)
    c.restoreState()
    footer_pageno(c, STATE_PAGE_NO(c))


def on_closing(c, doc):
    bg(c)
    gold_heart(c, PAGE_W / 2, PAGE_H - 96, 22)
    gold_divider(c, PAGE_W / 2, PAGE_H - 124)


def on_quickref(c, doc):
    bg(c)
    footer_pageno(c, STATE_PAGE_NO(c))


FRONT_PAGES = 3  # cover + title + copyright, unnumbered


def STATE_PAGE_NO(c):
    return max(1, c.getPageNumber() - FRONT_PAGES)


# -------------------------------------------------------------- CardBox --

class CardBox(Flowable):
    def __init__(self, flowables, fill_color, pad=12, radius=9, top_gap=6, bottom_gap=10):
        Flowable.__init__(self)
        self.flowables = flowables
        self.fill_color = fill_color
        self.pad = pad
        self.radius = radius
        self.top_gap = top_gap
        self.bottom_gap = bottom_gap

    def wrap(self, availWidth, availHeight):
        inner_w = availWidth - 2 * self.pad
        total_h = 2 * self.pad
        self._sizes = []
        for f in self.flowables:
            fw, fh = f.wrap(inner_w, availHeight)
            self._sizes.append(fh)
            total_h += fh
        self.width = availWidth
        self.height = total_h + self.top_gap + self.bottom_gap
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        box_h = self.height - self.top_gap - self.bottom_gap
        box_y = self.bottom_gap
        c.setFillColor(self.fill_color)
        c.roundRect(0, box_y, self.width, box_h, self.radius, fill=1, stroke=0)
        c.restoreState()
        y = box_y + box_h - self.pad
        for f, fh in zip(self.flowables, self._sizes):
            y -= fh
            f.drawOn(self.canv, self.pad, y)


class SetMeta(Flowable):
    def __init__(self, **kwargs):
        Flowable.__init__(self)
        self.kwargs = kwargs

    def wrap(self, aw, ah):
        return (0, 0)

    def draw(self):
        STATE.update(self.kwargs)


class RecordTOC(Flowable):
    """Zero-size flowable dropped at the top of a section; records the page
    it lands on so a second build pass can render an accurate TOC."""

    def __init__(self, key):
        Flowable.__init__(self)
        self.key = key

    def wrap(self, aw, ah):
        return (0, 0)

    def draw(self):
        TOC_RECORD[self.key] = STATE_PAGE_NO(self.canv)


# ------------------------------------------------------------------ styles --
ss = getSampleStyleSheet()

body = ParagraphStyle("Body", parent=ss["Normal"], fontName="Times-Roman", fontSize=9.9,
                       leading=14.9, spaceAfter=8, alignment=TA_JUSTIFY, textColor=INK)
italic_lead = ParagraphStyle("ItalicLead", parent=body, fontName="Times-Italic", fontSize=10.4,
                              leading=15.5, spaceAfter=10, textColor=INK)
h1_chapter = ParagraphStyle("H1Chapter", parent=ss["Heading1"], fontName="Times-Bold", fontSize=19,
                             leading=23, alignment=TA_CENTER, textColor=INK, spaceBefore=2, spaceAfter=15)
h2_sub = ParagraphStyle("H2Sub", parent=ss["Heading2"], fontName="Times-Bold", fontSize=12.2,
                         leading=15.5, textColor=ROSE, spaceBefore=14, spaceAfter=8)
bullet_style = ParagraphStyle("Bullet", parent=body, leftIndent=13, spaceAfter=6, fontSize=9.5, leading=13.8)
tip_title = ParagraphStyle("TipTitle", parent=ss["Normal"], fontName="Times-Bold", fontSize=11.3,
                            leading=14, textColor=GOLD_DARK, spaceAfter=4)
title_main = ParagraphStyle("TitleMain", parent=ss["Normal"], fontName="Times-Bold", fontSize=30,
                             leading=35, alignment=TA_CENTER, textColor=INK, spaceAfter=10)
title_sub = ParagraphStyle("TitleSub", parent=ss["Normal"], fontName="Times-Italic", fontSize=13.5,
                            leading=19, alignment=TA_CENTER, textColor=ROSE, spaceAfter=22)
title_tag = ParagraphStyle("TitleTag", parent=ss["Normal"], fontName="Times-Italic", fontSize=10,
                            leading=15, alignment=TA_CENTER, textColor=INK)
copyright_style = ParagraphStyle("Copyright", parent=ss["Normal"], fontName="Times-Roman", fontSize=8.3,
                                  leading=12.4, alignment=TA_CENTER, textColor=INK, spaceAfter=9)
qr_heading = ParagraphStyle("QRHeading", parent=ss["Normal"], fontName="Times-Bold", fontSize=11,
                             leading=14, textColor=INK, spaceAfter=2)
qr_body = ParagraphStyle("QRBody", parent=body, fontSize=9, leading=12.8, spaceAfter=0)
qr_page_title = ParagraphStyle("QRPageTitle", parent=ss["Normal"], fontName="Times-Bold", fontSize=17,
                                leading=21, alignment=TA_CENTER, textColor=INK, spaceAfter=4)
qr_page_sub = ParagraphStyle("QRPageSub", parent=ss["Normal"], fontName="Times-Italic", fontSize=9.5,
                              leading=13, alignment=TA_CENTER, textColor=ROSE, spaceAfter=16)
byline_style = ParagraphStyle("Byline", parent=ss["Normal"], fontName="Times-Italic", fontSize=11.5,
                               leading=16, alignment=TA_CENTER, textColor=GOLD_DARK)
toc_title_style = ParagraphStyle("TOCTitle", parent=ss["Normal"], fontName="Times-Roman", fontSize=10.3,
                                  leading=14, textColor=INK)
toc_num_style = ParagraphStyle("TOCNum", parent=ss["Normal"], fontName="Times-Bold", fontSize=10.3,
                                leading=14, textColor=ROSE, alignment=TA_RIGHT)


def inline(text: str) -> str:
    text = text.replace("&", "&amp;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)
    return text


# ------------------------------------------------------------ content build --

def read_lines(name):
    with open(os.path.join(MANUSCRIPT_DIR, name), encoding="utf-8") as f:
        return f.read().split("\n")


def build_title_and_copyright(story):
    lines = read_lines("00-title-page.md")
    idx = lines.index("\\newpage")
    front, back = lines[:idx], lines[idx + 1:]

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

    # image cover page first, then flow onto the interior title page
    story.append(Spacer(1, 1))  # cover page carries only the background image
    story.append(NextPageTemplate("title"))
    story.append(PageBreak())

    story.append(Spacer(1, 92))
    story.append(Paragraph(inline(title_txt), title_main))
    story.append(Paragraph(inline(subtitle_txt), title_sub))
    story.append(Spacer(1, 30))
    story.append(Paragraph(inline(tagline_txt), title_tag))
    story.append(Spacer(1, 26))
    story.append(Paragraph(f"by {byline_txt}", byline_style))

    story.append(NextPageTemplate("copyright"))
    story.append(PageBreak())

    for l in back:
        s = l.strip()
        if not s:
            continue
        story.append(Paragraph(inline(s), copyright_style))


def parse_body_lines(lines, target):
    """Append paragraphs/bullets to `target`, folding a Try-This bullet run into a CardBox."""
    i = 0
    pending_bullets = []
    in_tip = False

    def flush_bullets():
        nonlocal pending_bullets, in_tip
        if pending_bullets:
            if in_tip:
                card_flow = [Paragraph("&#10038;&nbsp; Try This", tip_title)]
                card_flow += pending_bullets
                target.append(Spacer(1, 4))
                target.append(CardBox(card_flow, CARD_TINT))
            else:
                target.extend(pending_bullets)
            pending_bullets = []

    while i < len(lines):
        s = lines[i].strip()
        if s == "":
            i += 1
            continue
        if s.startswith("## "):
            flush_bullets()
            heading = s[3:]
            in_tip = "try this" in heading.lower()
            if not in_tip:
                target.append(Paragraph(inline(heading), h2_sub))
        elif s.startswith("# "):
            flush_bullets()
            target.append(Paragraph(inline(s[2:]), h1_chapter))
        elif s.startswith("- "):
            style = bullet_style
            pending_bullets.append(
                Paragraph('<font color="#C49B4A">&#8226;&nbsp;</font>' + inline(s[2:]), style)
            )
        else:
            flush_bullets()
            target.append(Paragraph(inline(s), body))
        i += 1
    flush_bullets()


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


def get_title(fname):
    for l in read_lines(fname):
        s = l.strip()
        if s.startswith("# "):
            return s[2:]
    return fname


def get_toc_entries():
    entries = [(get_title(fname), fname) for fname, _ in CHAPTER_FILES]
    entries.append((get_title("23-quick-reference.md"), "23-quick-reference.md"))
    entries.append((get_title("24-closing-letter.md"), "24-closing-letter.md"))
    return entries


def build_toc(story):
    story.append(NextPageTemplate("body"))
    story.append(PageBreak())
    story.append(RecordTOC("toc"))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Contents", qr_page_title))
    story.append(Spacer(1, 14))

    rows = []
    for title, key in get_toc_entries():
        pageno = TOC_RECORD.get(key, "")
        rows.append([Paragraph(inline(title), toc_title_style), Paragraph(str(pageno), toc_num_style)])

    tbl = Table(rows, colWidths=[PAGE_W - 2 * SIDE - 34, 34])
    style_cmds = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]
    for i in range(len(rows) - 1):
        style_cmds.append(("LINEBELOW", (0, i), (-1, i), 0.5, GOLD, None, (1, 2)))
    tbl.setStyle(TableStyle(style_cmds))
    story.append(tbl)


def build_chapters(story):
    for pos, (fname, num) in enumerate(CHAPTER_FILES):
        story.append(SetMeta(chapter_no=num))
        story.append(NextPageTemplate("chapter_open"))
        story.append(PageBreak())
        story.append(RecordTOC(fname))
        lines = read_lines(fname)
        # first heading rendered, then switch to plain body template for overflow
        chapter_flow = []
        parse_body_lines(lines, chapter_flow)
        # insert body-template switch right after the first flowable (the heading)
        story.append(chapter_flow[0])
        story.append(NextPageTemplate("body"))
        story.extend(chapter_flow[1:])


def build_quickref(story):
    lines = read_lines("23-quick-reference.md")
    story.append(NextPageTemplate("quickref"))
    story.append(PageBreak())
    story.append(RecordTOC("23-quick-reference.md"))
    story.append(Spacer(1, 46))
    story.append(Paragraph("The Mother's Code", qr_page_title))
    story.append(Paragraph("Quick Reference — twenty-one principles, distilled", qr_page_sub))

    item_re = re.compile(r"^\d+\.\s+\*\*(.+?)\*\*\s+—\s+(.+)$")
    footer_lines = []
    seen_items = False
    for l in lines:
        s = l.strip()
        m = item_re.match(s)
        if m:
            seen_items = True
            head_p = Paragraph(inline(m.group(1)), qr_heading)
            body_p = Paragraph(inline(m.group(2)), qr_body)
            card = CardBox([head_p, Spacer(1, 2), body_p], CARD_TINT, pad=10)
            story.append(card)
            story.append(Spacer(1, 8))
        elif s.startswith("*") and s.endswith("*") and seen_items:
            footer_lines.append(s.strip("*"))

    for fl in footer_lines:
        story.append(Spacer(1, 6))
        story.append(Paragraph(inline(fl), title_tag))


def build_closing(story):
    story.append(NextPageTemplate("closing"))
    story.append(PageBreak())
    story.append(RecordTOC("24-closing-letter.md"))
    lines = read_lines("24-closing-letter.md")
    flow = []
    parse_body_lines(lines, flow)
    story.extend(flow)


# --------------------------------------------------------------- assemble --

def make_doc(target):
    doc = BaseDocTemplate(
        target, pagesize=A5,
        title="The Mother's Code", author=AUTHOR,
    )

    def frame(top, bottom):
        return Frame(SIDE, bottom, PAGE_W - 2 * SIDE, PAGE_H - top - bottom, id="f")

    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[frame(TITLE_TOP, TITLE_BOTTOM)], onPage=on_cover),
        PageTemplate(id="title", frames=[frame(TITLE_TOP, TITLE_BOTTOM)], onPage=on_title),
        PageTemplate(id="copyright", frames=[frame(90, 70)], onPage=on_copyright),
        PageTemplate(id="chapter_open", frames=[frame(OPEN_TOP, OPEN_BOTTOM)], onPage=on_chapter_open),
        PageTemplate(id="body", frames=[frame(BODY_TOP, BODY_BOTTOM)], onPage=on_body),
        PageTemplate(id="quickref", frames=[frame(30, BODY_BOTTOM)], onPage=on_quickref),
        PageTemplate(id="closing", frames=[frame(160, 90)], onPage=on_closing),
        PageTemplate(id="backcover", frames=[frame(TITLE_TOP, TITLE_BOTTOM)], onPage=on_backcover),
    ])
    return doc


def assemble_story():
    story = []
    build_title_and_copyright(story)
    build_toc(story)
    build_chapters(story)
    build_quickref(story)
    build_closing(story)
    # image back-cover as the final page
    story.append(NextPageTemplate("backcover"))
    story.append(PageBreak())
    story.append(Spacer(1, 1))
    return story


def build():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    # Pass 1: throwaway render, purely to discover each section's page number.
    make_doc(io.BytesIO()).build(assemble_story())

    # Pass 2: real render, now the TOC can show accurate page numbers.
    make_doc(OUTPUT_PATH).build(assemble_story())
    print(f"Built: {OUTPUT_PATH}")


if __name__ == "__main__":
    build()
