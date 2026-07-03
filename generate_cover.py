"""
Generates the front cover for The Mother's Code: pastel + gold, a mother/child
cameo medallion, botanical flourishes, and an emotional tagline ribbon.
Renders via reportlab (vector) then rasterizes to a high-res PNG with PyMuPDF.
"""
import os
import math

from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.lib.colors import HexColor

HERE = os.path.dirname(__file__)
ASSETS = os.path.join(HERE, "assets")
BUILD = os.path.join(HERE, "build")

W, H = 480, 768  # 1:1.6 ratio -> rasterized to 1600x2560
TMP_PDF = os.path.join(BUILD, "_cover_tmp.pdf")
OUT_PNG = os.path.join(BUILD, "Cover-The-Mothers-Code.png")
OUT_JPG = os.path.join(BUILD, "Cover-The-Mothers-Code.jpg")

INK = HexColor("#3D2A2B")
GOLD = HexColor("#B0894A")
GOLD_DARK = HexColor("#8C6B34")
ROSE = HexColor("#B0606A")
ROSE_DEEP = HexColor("#8C5062")
CREAM = HexColor("#FFFBF3")
MEDALLION_FILL = HexColor("#FCEFE6")


def frame(c, margin=18):
    c.saveState()
    c.setStrokeColor(GOLD)
    c.setLineWidth(2.0)
    c.rect(margin, margin, W - 2 * margin, H - 2 * margin, fill=0, stroke=1)
    c.setLineWidth(0.8)
    c.rect(margin + 6, margin + 6, W - 2 * (margin + 6), H - 2 * (margin + 6), fill=0, stroke=1)
    r = 3.4
    for cx, cy in [(margin, margin), (margin, H - margin), (W - margin, margin), (W - margin, H - margin)]:
        c.setFillColor(GOLD)
        c.circle(cx, cy, r, fill=1, stroke=0)
    c.restoreState()


def aura_rings(c, cx, cy, count=5, base_r=40, gap=16, color=GOLD, max_alpha=0.32):
    c.saveState()
    c.setStrokeColor(color)
    for i in range(count):
        r = base_r + i * gap
        alpha = max_alpha * (1 - i / count)
        c.setStrokeAlpha(alpha)
        c.setLineWidth(1.1)
        c.circle(cx, cy, r, fill=0, stroke=1)
    c.restoreState()


def divider(c, cx, y, half_width=48):
    c.saveState()
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.0)
    c.line(cx - half_width, y, cx - 8, y)
    c.line(cx + 8, y, cx + half_width, y)
    d = 4.4
    c.setFillColor(GOLD)
    p = c.beginPath()
    p.moveTo(cx, y + d); p.lineTo(cx + d, y); p.lineTo(cx, y - d); p.lineTo(cx - d, y)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()


def leaf(c, x, y, angle_deg, length=13, width=5.5, color=GOLD):
    c.saveState()
    c.translate(x, y)
    c.rotate(angle_deg)
    c.setFillColor(color)
    p = c.beginPath()
    p.moveTo(0, 0)
    p.curveTo(length * 0.3, width, length * 0.75, width * 0.7, length, 0)
    p.curveTo(length * 0.75, -width * 0.7, length * 0.3, -width, 0, 0)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()


def sprig(c, x, y, mirror=1):
    c.saveState()
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.1)
    base_angle = 180 if mirror < 0 else 0
    length = 58
    ex = x + mirror * length
    c.line(x, y, ex, y - 6)
    positions = [0.18, 0.42, 0.64, 0.86]
    for i, t in enumerate(positions):
        lx = x + mirror * length * t
        ly = y - 6 * t
        up = i % 2 == 0
        ang = (25 if up else -25) * (1 if mirror > 0 else 1) + (0 if mirror > 0 else 180)
        leaf(c, lx, ly, ang, length=15, width=5.5)
    c.restoreState()


def laurel_wreath(c, cx, cy, radius, mirror=1, leaves=9, start_deg=-16, end_deg=210, color=GOLD):
    """A classic laurel arc, built from paired leaves along a circle — used
    to frame the medallion with real visual weight instead of a thin sprig."""
    c.saveState()
    for i in range(leaves):
        t = i / (leaves - 1)
        ang = math.radians(start_deg + (end_deg - start_deg) * t)
        lx = cx + mirror * math.cos(ang) * radius
        ly = cy - math.sin(ang) * radius
        tangent = math.degrees(ang) + 90
        leaf_ang = (tangent if mirror > 0 else 180 - tangent)
        leaf_len = 20 - 6 * abs(0.5 - t)
        leaf(c, lx, ly, leaf_ang, length=leaf_len, width=8, color=color)
    c.restoreState()


def mother_child_silhouette(c, cx, cy, scale=1.0, color=ROSE_DEEP):
    """Simplified cameo-style mark: a mother's cloak silhouette with a
    smaller child silhouette held against her."""
    c.saveState()
    c.setFillColor(color)

    def s(v):
        return v * scale

    def pt(x, y):
        return (cx + s(x), cy + s(y))

    # mother's cloak/dress (soft trapezoid, rounded shoulders)
    p = c.beginPath()
    p.moveTo(*pt(-44, -52))
    p.curveTo(*pt(-48, -18), *pt(-34, 12), *pt(-25, 20))
    p.lineTo(*pt(-7, 20))
    p.curveTo(*pt(2, 12), *pt(8, -6), *pt(9, -52))
    p.close()
    c.drawPath(p, fill=1, stroke=0)

    # mother's head + bun
    c.circle(*pt(-16, 36), s(15.5), fill=1, stroke=0)
    c.circle(*pt(-27, 46), s(6), fill=1, stroke=0)

    # child's cloak/dress, smaller, nested in front of mother's right side
    p2 = c.beginPath()
    p2.moveTo(*pt(-2, -52))
    p2.curveTo(*pt(-5, -28), *pt(4, -10), *pt(11, -6))
    p2.lineTo(*pt(23, -6))
    p2.curveTo(*pt(29, -10), *pt(33, -26), *pt(34, -52))
    p2.close()
    c.drawPath(p2, fill=1, stroke=0)

    # child's head
    c.circle(*pt(16, 6), s(10.5), fill=1, stroke=0)

    # mother's arm resting over the child's shoulder
    p3 = c.beginPath()
    p3.moveTo(*pt(-8, 16))
    p3.curveTo(*pt(2, 8), *pt(10, 2), *pt(20, -4))
    p3.curveTo(*pt(22, -1), *pt(23, 2), *pt(24, 5))
    p3.curveTo(*pt(14, 10), *pt(4, 16), *pt(-5, 22))
    p3.close()
    c.drawPath(p3, fill=1, stroke=0)

    c.restoreState()


def shadow_centred_text(c, cx, y, text, font, size, color, shadow_color, offset=1.6):
    c.setFont(font, size)
    c.setFillColor(shadow_color)
    c.drawCentredString(cx + offset, y - offset, text)
    c.setFillColor(color)
    c.drawCentredString(cx, y, text)


def ribbon(c, cx, y, text, width=330, height=40, fill=GOLD, text_color=CREAM):
    c.saveState()
    x = cx - width / 2
    notch = 12
    c.setFillColor(fill)
    p = c.beginPath()
    p.moveTo(x, y)
    p.lineTo(x + width, y)
    p.lineTo(x + width - notch, y + height / 2)
    p.lineTo(x + width, y + height)
    p.lineTo(x, y + height)
    p.lineTo(x + notch, y + height / 2)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.setFillColor(text_color)
    c.setFont("Times-Italic", 12.5)
    c.drawCentredString(cx, y + height / 2 - 4.5, text)
    c.restoreState()


def title_rule(c, cx, y, half_width=118):
    c.saveState()
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.3)
    c.line(cx - half_width, y, cx + half_width, y)
    c.restoreState()


def build_cover():
    os.makedirs(BUILD, exist_ok=True)
    c = pdfcanvas.Canvas(TMP_PDF, pagesize=(W, H))

    c.drawImage(os.path.join(ASSETS, "bg_cover_floral.png"), 0, 0, width=W, height=H)

    # kicker
    c.setFont("Helvetica", 9.5)
    c.setFillColor(GOLD_DARK)
    kicker = "A  R E S E A R C H - B A C K E D  G U I D E  F O R  M O T H E R S"
    c.drawCentredString(W / 2, H - 72, kicker)

    # medallion, framed by a full laurel wreath for real visual weight
    med_cx, med_cy, med_r = W / 2, H - 232, 72
    laurel_wreath(c, med_cx, med_cy, med_r + 20, mirror=-1)
    laurel_wreath(c, med_cx, med_cy, med_r + 20, mirror=1)

    c.saveState()
    c.setFillColor(MEDALLION_FILL)
    c.circle(med_cx, med_cy, med_r, fill=1, stroke=0)
    c.restoreState()
    c.saveState()
    c.setStrokeColor(GOLD)
    c.setLineWidth(2.4)
    c.circle(med_cx, med_cy, med_r, fill=0, stroke=1)
    c.setLineWidth(0.8)
    c.circle(med_cx, med_cy, med_r - 7, fill=0, stroke=1)
    c.restoreState()
    mother_child_silhouette(c, med_cx, med_cy + 6, scale=1.05)

    # title block — solid, confident, framed by thin gold rules
    title_y = H - 388
    title_rule(c, W / 2, title_y + 34)
    c.setFont("Times-Bold", 44)
    c.setFillColor(INK)
    c.drawCentredString(W / 2, title_y, "The Mother's")
    c.drawCentredString(W / 2, title_y - 52, "Code")
    title_rule(c, W / 2, title_y - 78)

    c.setFont("Times-Italic", 16)
    c.setFillColor(ROSE)
    c.drawCentredString(W / 2, title_y - 106, "How to Raise a Child Who")
    c.drawCentredString(W / 2, title_y - 127, "Changes the World")

    c.setFont("Times-Italic", 13)
    c.setFillColor(GOLD_DARK)
    c.drawCentredString(W / 2, title_y - 156, "by Aiz-El Dan")

    # emotional tagline ribbon (single connected band, two lines)
    ribbon_y, ribbon_h = 84, 78
    x = W / 2 - 196
    width = 392
    notch = 14
    c.saveState()
    c.setFillColor(INK)
    c.setFillAlpha(0.18)
    p = c.beginPath()
    p.moveTo(x + 3, ribbon_y - 3)
    p.lineTo(x + width + 3, ribbon_y - 3)
    p.lineTo(x + width - notch + 3, ribbon_y + ribbon_h / 2 - 3)
    p.lineTo(x + width + 3, ribbon_y + ribbon_h - 3)
    p.lineTo(x + 3, ribbon_y + ribbon_h - 3)
    p.lineTo(x + notch + 3, ribbon_y + ribbon_h / 2 - 3)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()
    c.saveState()
    c.setFillColor(GOLD)
    p = c.beginPath()
    p.moveTo(x, ribbon_y)
    p.lineTo(x + width, ribbon_y)
    p.lineTo(x + width - notch, ribbon_y + ribbon_h / 2)
    p.lineTo(x + width, ribbon_y + ribbon_h)
    p.lineTo(x, ribbon_y + ribbon_h)
    p.lineTo(x + notch, ribbon_y + ribbon_h / 2)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.setFillColor(CREAM)
    c.setFont("Times-Italic", 13.5)
    c.drawCentredString(W / 2, ribbon_y + ribbon_h - 32, "“Every extraordinary child had a")
    c.drawCentredString(W / 2, ribbon_y + ribbon_h - 56, "mother who believed first.”")
    c.restoreState()

    c.showPage()
    c.save()
    print("wrote", TMP_PDF)


def rasterize():
    import fitz
    doc = fitz.open(TMP_PDF)
    page = doc[0]
    zoom = 1600 / W
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    pix.save(OUT_PNG)
    from PIL import Image
    Image.open(OUT_PNG).convert("RGB").save(OUT_JPG, quality=92)
    print("wrote", OUT_PNG)
    print("wrote", OUT_JPG)


if __name__ == "__main__":
    build_cover()
    rasterize()
