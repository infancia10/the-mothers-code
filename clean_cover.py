"""
Cleans the uploaded wraparound cover (assets/new cover.png):
  1. removes the author name from the front panel,
  2. removes the author name from the spine,
  3. removes the placeholder barcode block from the back panel,
then splits it into front / back panels for the PDF and website.

Text fills use row-wise linear interpolation between the pixels just outside
the rect (preserves the soft watercolor gradient). The barcode is patched
with a mirrored neighbouring region so the marble texture stays organic,
with a feathered seam.
"""
import numpy as np
from PIL import Image, ImageFilter

SRC = "assets/new cover.png"
OUT_FULL = "assets/full-cover-clean.png"
OUT_FRONT_JPG = "build/front-cover.jpg"
OUT_BACK_JPG = "build/back-cover.jpg"
OUT_SITE = "website/assets/cover.jpg"

# panel boundaries (measured)
BACK_R = 640
FRONT_L = 740

# regions to clear
FRONT_NAME = (860, 1020, 1290, 1080)
SPINE_NAME = (660, 645, 712, 1018)
BARCODE = (388, 892, 626, 1112)  # barcode box + its drop shadow + fade margin


def interp_fill(a, rect, pad=4):
    """Fill rect by linearly interpolating each row between the columns just
    outside the rect edges."""
    x0, y0, x1, y1 = rect
    left = a[y0:y1, x0 - pad:x0].mean(axis=1)     # (rows, 3)
    right = a[y0:y1, x1:x1 + pad].mean(axis=1)
    w = x1 - x0
    t = np.linspace(0.0, 1.0, w)[None, :, None]   # (1, w, 1)
    fill = left[:, None, :] * (1 - t) + right[:, None, :] * t
    # gentle noise so it doesn't look plastic-flat
    noise = np.random.default_rng(7).normal(0, 1.6, fill.shape)
    a[y0:y1, x0:x1] = np.clip(fill + noise, 0, 255)


def patch_fill(img, rect, src_left=196, fade=12):
    """Cover rect with a horizontally-mirrored copy of the SAME row band to
    its left (same colorway, so tones match the surroundings). Source starts
    at src_left to stay clear of the back-cover tagline text. The patch is
    reflection-extended rightward to reach full width, and all edges are
    feathered into the original marble."""
    x0, y0, x1, y1 = rect
    w, h = x1 - x0, y1 - y0

    src_w = x0 - src_left
    patch = Image.new("RGB", (w, h))
    band = img.crop((src_left, y0, x0, y1)).transpose(Image.FLIP_LEFT_RIGHT)
    patch.paste(band, (0, 0))
    # reflection-extend until the patch is full width
    x = src_w
    while x < w:
        take = min(x, w - x)
        ext = patch.crop((x - take, 0, x, h)).transpose(Image.FLIP_LEFT_RIGHT)
        patch.paste(ext, (x, 0))
        x += take

    # feather all four edges into the surrounding marble
    mask = Image.new("L", (w, h), 255)
    px = mask.load()
    for xx in range(w):
        for yy in range(h):
            a = 255
            if xx < fade: a = min(a, int(255 * xx / fade))
            if xx >= w - fade: a = min(a, int(255 * (w - 1 - xx) / fade))
            if yy < fade: a = min(a, int(255 * yy / fade))
            if yy >= h - fade: a = min(a, int(255 * (h - 1 - yy) / fade))
            if a != 255: px[xx, yy] = a

    img.paste(patch, (x0, y0), mask)


def main():
    img = Image.open(SRC).convert("RGB")

    # 3. barcode first (pure PIL)
    patch_fill(img, BARCODE)

    # 1-2. text fills (numpy)
    a = np.asarray(img).astype(np.float64)
    interp_fill(a, FRONT_NAME)
    interp_fill(a, SPINE_NAME)
    img = Image.fromarray(a.astype(np.uint8))

    img.save(OUT_FULL)

    W, H = img.size
    front = img.crop((FRONT_L, 0, W, H))
    back = img.crop((0, 0, BACK_R, H))

    # upscale front panel 2x for crisper display/PDF use
    front_big = front.resize((front.width * 2, front.height * 2), Image.LANCZOS)
    front_big.save(OUT_FRONT_JPG, quality=92)
    front_big.save(OUT_SITE, quality=92)

    back_big = back.resize((back.width * 2, back.height * 2), Image.LANCZOS)
    back_big.save(OUT_BACK_JPG, quality=92)

    # A5-ratio page images for the PDF (panel centered over a blurred fill,
    # so the cover page has no hard letterbox bars)
    for panel, out in ((front, "build/pdf-cover-page.jpg"), (back, "build/pdf-back-page.jpg")):
        pw, ph = 1191, 1684  # A5 @ ~144dpi
        bg = panel.resize((pw, ph), Image.LANCZOS).filter(ImageFilter.GaussianBlur(40))
        scale = ph / panel.height
        fg = panel.resize((int(panel.width * scale), ph), Image.LANCZOS)
        bg.paste(fg, ((pw - fg.width) // 2, 0))
        bg.save(out, quality=90)
        print("page :", out, bg.size)

    print("full :", OUT_FULL, img.size)
    print("front:", OUT_FRONT_JPG, front_big.size, "-> also", OUT_SITE)
    print("back :", OUT_BACK_JPG, back_big.size)


if __name__ == "__main__":
    main()
