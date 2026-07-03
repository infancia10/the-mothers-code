"""
Generates ONE consistent watercolor-floral background used across every page
of The Mother's Code: light cream wash, muted sage/dusty-rose corner florals,
soft painterly petals — kept light and legible, not dark or heavy.
"""
import os
import math
import random
from PIL import Image, ImageDraw, ImageFilter

random.seed(11)

# A5 at 300dpi
W, H = 1748, 2480

BASE = (255, 255, 255)          # white
SAGE = (150, 168, 132)
SAGE_DARK = (108, 128, 92)
ROSE = (204, 138, 143)
ROSE_DEEP = (176, 96, 105)
MAUVE = (176, 137, 158)
PEACH = (228, 175, 132)
GOLD_MUTED = (176, 138, 74)


def new_layer(w, h):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))


def soft_petal(draw, cx, cy, length, width, angle_deg, color, alpha):
    """One petal: an ellipse stretched and rotated, drawn on its own tiny
    canvas then pasted rotated (PIL ellipses can't rotate directly)."""
    pad = int(max(length, width))
    tile = Image.new("RGBA", (pad * 2, pad * 2), (0, 0, 0, 0))
    td = ImageDraw.Draw(tile)
    td.ellipse([pad - width / 2, pad - length / 2, pad + width / 2, pad + length / 2],
               fill=color + (alpha,))
    tile = tile.rotate(-angle_deg, resample=Image.BICUBIC, center=(pad, pad))
    draw.bitmap  # no-op to keep draw referenced
    return tile, pad


def paste_petal(layer, cx, cy, length, width, angle_deg, color, alpha):
    tmp = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    d.ellipse([cx - width / 2, cy - length / 2, cx + width / 2, cy + length / 2], fill=color + (alpha,))
    tmp = tmp.rotate(-angle_deg, resample=Image.BICUBIC, center=(cx, cy))
    layer.alpha_composite(tmp)


def painterly_flower(layer, cx, cy, r, petal_color, center_color, petals=6, jitter=8):
    for i in range(petals):
        ang = i * (360 / petals) + random.uniform(-jitter, jitter)
        rad = math.radians(ang)
        dist = r * 0.5
        px = cx + math.cos(rad) * dist
        py = cy + math.sin(rad) * dist
        tone = tuple(min(255, max(0, c + random.randint(-14, 14))) for c in petal_color)
        paste_petal(layer, px, py, r * random.uniform(0.95, 1.15), r * random.uniform(0.55, 0.68),
                    ang, tone, random.randint(150, 195))
    # center
    d = ImageDraw.Draw(layer)
    cr = r * 0.24
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=center_color + (215,))


def bud(layer, cx, cy, r, color):
    paste_petal(layer, cx, cy, r * 1.3, r * 0.8, random.uniform(0, 360), color, 190)


def leaf(layer, x, y, angle_deg, length, width, color, alpha=165):
    paste_petal(layer, x, y, length, width, angle_deg, color, alpha)


def stem(draw, x1, y1, x2, y2, color, width=3, alpha=140):
    steps = 20
    pts = []
    for i in range(steps + 1):
        t = i / steps
        bow = math.sin(t * math.pi) * (x2 - x1) * 0.08
        pts.append((x1 + (x2 - x1) * t + bow, y1 + (y2 - y1) * t))
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i + 1]], fill=color + (alpha,), width=width)


def flower_cluster(layer, cx, cy, scale=1.0, mirror=1):
    d = ImageDraw.Draw(layer)
    s = scale

    def m(dx):
        return dx * mirror

    stem(d, cx, cy, cx + m(20 * s), cy - 140 * s, SAGE_DARK, width=int(4 * s))
    stem(d, cx + m(20 * s), cy - 60 * s, cx + m(90 * s), cy - 120 * s, SAGE_DARK, width=int(3 * s))

    for lx, ly, ang, ln in [
        (cx + m(10 * s), cy - 40 * s, 40 * mirror, 55 * s),
        (cx + m(30 * s), cy - 90 * s, -30 * mirror, 60 * s),
        (cx + m(55 * s), cy - 118 * s, 20 * mirror, 50 * s),
    ]:
        leaf(layer, lx, ly, ang, ln, ln * 0.34, SAGE)

    painterly_flower(layer, cx, cy - 150 * s, 46 * s, ROSE, ROSE_DEEP, petals=7)
    painterly_flower(layer, cx + m(85 * s), cy - 128 * s, 34 * s, PEACH, ROSE_DEEP, petals=6)
    bud(layer, cx + m(48 * s), cy - 70 * s, 16 * s, MAUVE)


def flower_cluster_hanging(layer, cx, cy, scale=1.0, mirror=1):
    """Same cluster, but drooping downward — for top-corner placement."""
    d = ImageDraw.Draw(layer)
    s = scale

    def m(dx):
        return dx * mirror

    stem(d, cx, cy, cx + m(20 * s), cy + 140 * s, SAGE_DARK, width=int(4 * s))
    stem(d, cx + m(20 * s), cy + 60 * s, cx + m(90 * s), cy + 120 * s, SAGE_DARK, width=int(3 * s))

    for lx, ly, ang, ln in [
        (cx + m(10 * s), cy + 40 * s, -40 * mirror, 55 * s),
        (cx + m(30 * s), cy + 90 * s, 30 * mirror, 60 * s),
        (cx + m(55 * s), cy + 118 * s, -20 * mirror, 50 * s),
    ]:
        leaf(layer, lx, ly, ang, ln, ln * 0.34, SAGE)

    painterly_flower(layer, cx, cy + 150 * s, 46 * s, ROSE, ROSE_DEEP, petals=7)
    painterly_flower(layer, cx + m(85 * s), cy + 128 * s, 34 * s, PEACH, ROSE_DEEP, petals=6)
    bud(layer, cx + m(48 * s), cy + 70 * s, 16 * s, MAUVE)


def butterfly(layer, cx, cy, scale=1.0, color=MAUVE):
    d = ImageDraw.Draw(layer)
    s = scale
    for mirror in (-1, 1):
        paste_petal(layer, cx + mirror * 14 * s, cy - 6 * s, 30 * s, 20 * s, mirror * 20, color, 110)
        paste_petal(layer, cx + mirror * 10 * s, cy + 14 * s, 18 * s, 12 * s, mirror * -10, color, 100)
    d.line([cx, cy - 14 * s, cx, cy + 16 * s], fill=SAGE_DARK + (150,), width=max(1, int(2 * s)))


def make_book_bg():
    img = Image.new("RGB", (W, H), BASE)
    layer = new_layer(W, H)

    # kept tight to the corners so they never intrude on the text frame
    flower_cluster_hanging(layer, W * 0.90, H * -0.02, scale=1.0, mirror=-1)
    flower_cluster(layer, W * 0.06, H * 1.03, scale=1.25, mirror=1)
    d = ImageDraw.Draw(layer)
    for i in range(6):
        bx = W * (0.02 + i * 0.025)
        stem(d, bx, H * 1.0, bx + random.uniform(-20, 20), H * 1.0 - random.uniform(60, 120), SAGE_DARK, width=3)
        leaf(layer, bx, H * 1.0 - random.uniform(35, 90), random.uniform(-40, 40), 36, 13, SAGE)

    blurred = layer.filter(ImageFilter.GaussianBlur(3))
    img = img.convert("RGBA")
    img.alpha_composite(blurred)
    img.convert("RGB").save("assets/bg_floral.png")
    print("wrote assets/bg_floral.png")


def make_cover_bg():
    cw, ch = 1600, 2560
    img = Image.new("RGB", (cw, ch), BASE)
    layer = new_layer(cw, ch)

    flower_cluster_hanging(layer, cw * 0.92, ch * -0.015, scale=1.4, mirror=-1)
    flower_cluster(layer, cw * 0.06, ch * 1.01, scale=1.9, mirror=1)
    flower_cluster(layer, cw * 0.98, ch * 1.02, scale=1.5, mirror=-1)
    d = ImageDraw.Draw(layer)
    for i in range(8):
        bx = cw * (0.02 + i * 0.022)
        stem(d, bx, ch * 1.0, bx + random.uniform(-30, 30), ch * 1.0 - random.uniform(80, 170), SAGE_DARK, width=4)
        leaf(layer, bx, ch * 1.0 - random.uniform(45, 120), random.uniform(-40, 40), 50, 17, SAGE)

    blurred = layer.filter(ImageFilter.GaussianBlur(4))
    img = img.convert("RGBA")
    img.alpha_composite(blurred)
    img.convert("RGB").save("assets/bg_cover_floral.png")
    print("wrote assets/bg_cover_floral.png")


if __name__ == "__main__":
    os.makedirs("assets", exist_ok=True)
    make_book_bg()
    make_cover_bg()
