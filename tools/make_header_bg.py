"""Header background for the project page.

Real benchmark frames (robot manipulation) laid out as a two-row film strip, tinted in the
paper's purple, with a stepwise progress curve drawn across them and a faint compass rose.
The left side is kept dark for the title text.

    python3 tools/make_header_bg.py FRAME_DIR  ->  webpage/static/img/header_bg.jpg
FRAME_DIR holds f0.png ... f9.png, 474 x 300 crops of benchmark episodes in time order.
"""
import math, os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

W, H = 2560, 1100
frames_dir = sys.argv[1]
out = os.path.join(os.path.dirname(__file__), '..', 'webpage', 'static', 'img', 'header_bg.jpg')

# ---------------------------------------------------------------- base gradient
base = Image.new('RGB', (W, H))
px = base.load()
c0, c1 = (18, 9, 38), (74, 38, 132)
for x in range(W):
    u = x / (W - 1)
    col = tuple(int(c0[k] + (c1[k] - c0[k]) * u ** 1.3) for k in range(3))
    for y in range(H):
        v = y / (H - 1)
        px[x, y] = tuple(int(col[k] * (1.08 - 0.25 * v)) for k in range(3))

# ------------------------------------------------------------------- film strip
frames = [Image.open(os.path.join(frames_dir, f'f{i}.png')).convert('RGB') for i in range(10)]
fw, fh, gap = 470, 300, 22
strip = Image.new('RGBA', (5 * fw + 4 * gap, 2 * fh + gap), (0, 0, 0, 0))
mask_r = Image.new('L', (fw, fh), 0)
ImageDraw.Draw(mask_r).rounded_rectangle((0, 0, fw - 1, fh - 1), radius=18, fill=255)
purple = Image.new('RGB', (fw, fh), (96, 58, 170))
for i, im in enumerate(frames):
    im = im.resize((fw, fh), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(0.85)
    im = Image.blend(im, purple, 0.30)
    im = ImageEnhance.Brightness(im).enhance(0.92)
    strip.paste(im, ((i % 5) * (fw + gap), (i // 5) * (fh + gap)), mask_r)
# shear the strip a little so it reads as a moving timeline
strip = strip.transform(strip.size, Image.AFFINE, (1, 0.10, -0.10 * strip.height, 0, 1, 0),
                        resample=Image.BICUBIC)
sx, sy = 760, (H - strip.height) // 2 + 10
# fade in from the left so the title side stays clean
fade = Image.new('L', strip.size, 0)
fp = fade.load()
for x in range(strip.width):
    a = max(0.0, min(1.0, (x - 60) / 900)) ** 1.4
    for y in range(strip.height):
        fp[x, y] = int(255 * a)
alpha = Image.composite(strip.getchannel('A'), Image.new('L', strip.size, 0), fade)
strip.putalpha(Image.eval(Image.merge('L', [alpha]), lambda v: int(v * 0.92)))
canvas = base.convert('RGBA')
canvas.alpha_composite(strip, (sx, sy))

# ------------------------------------------------------------- progress curve
layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(layer)
x0, x1, yb, yt = 900, 2480, H - 170, 170
K = 8
pts = []
for k in range(K):
    xa, xb = x0 + (x1 - x0) * k / K, x0 + (x1 - x0) * (k + 1) / K
    ya = yb - (yb - yt) * k / K
    yb2 = yb - (yb - yt) * (k + 1) / K
    pts += [(xa, ya), (xa + (xb - xa) * 0.35, ya), (xb, yb2)]
glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
ImageDraw.Draw(glow).line(pts, fill=(214, 190, 255, 200), width=22, joint='curve')
glow = glow.filter(ImageFilter.GaussianBlur(16))
canvas.alpha_composite(glow)
d.line(pts, fill=(246, 238, 255, 255), width=7, joint='curve')
for k in range(K + 1):
    x = x0 + (x1 - x0) * k / K
    y = yb - (yb - yt) * k / K
    r = 13
    d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 227, 154, 255), outline=(255, 255, 255, 255), width=3)
    d.line((x, H - 110, x, H - 88), fill=(230, 220, 250, 150), width=4)
d.line((x0, H - 99, x1, H - 99), fill=(230, 220, 250, 110), width=3)
canvas.alpha_composite(layer)

# ------------------------------------------------------------- compass rose
rose = Image.new('RGBA', (W, H), (0, 0, 0, 0))
r = ImageDraw.Draw(rose)
cx, cy, R = 2290, 250, 190
r.ellipse((cx - R, cy - R, cx + R, cy + R), outline=(255, 255, 255, 60), width=5)
r.ellipse((cx - R * 0.78, cy - R * 0.78, cx + R * 0.78, cy + R * 0.78), outline=(255, 255, 255, 40), width=3)
for k in range(8):
    a = k * math.pi / 4
    L = R * (0.95 if k % 2 == 0 else 0.55)
    w = 0.16
    tip = (cx + L * math.sin(a), cy - L * math.cos(a))
    l = (cx + R * 0.12 * math.sin(a - math.pi / 2), cy - R * 0.12 * math.cos(a - math.pi / 2))
    rr = (cx + R * 0.12 * math.sin(a + math.pi / 2), cy - R * 0.12 * math.cos(a + math.pi / 2))
    r.polygon([tip, l, (cx, cy), rr], fill=(255, 255, 255, 55 if k else 95))
canvas.alpha_composite(rose)

# ------------------------------------------------ darken the left for the text
shade = Image.new('RGBA', (W, H), (0, 0, 0, 0))
sp = shade.load()
for x in range(W):
    a = max(0.0, 1 - x / 1500) ** 1.6
    for y in range(H):
        sp[x, y] = (14, 6, 30, int(215 * a))
canvas.alpha_composite(shade)

canvas.convert('RGB').save(out, quality=86, optimize=True, progressive=True)
print('wrote', os.path.abspath(out))
