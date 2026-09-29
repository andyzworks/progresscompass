"""Animated publication thumbnail (480 x 300 GIF, 150 frames at 70 ms), in the style of the
Video2Skill one: a real benchmark episode plays on the left with the step instruction
ProgressCompass supplies as context; on the right the progress curves are drawn in sync:
ground truth, the frozen PRM without context, and ProgressCompass.

    python3 tools/make_thumb_gif.py OUT.gif
"""
import json, os, subprocess, sys, tempfile, textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFont

G = '/projects/b1222/userdata/jianshu/code_keliang/02_Graph'
CAT, EP = 'state', 'episode17'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'progresscompass.gif'
S = 2                                     # draw at 2x, then downsample
W, H = 480 * S, 300 * S
N_PLAY, N_HOLD, MS = 132, 18, 70

F = '/usr/share/fonts/dejavu/DejaVuSans.ttf'
FB = '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf'
font = lambda sz, b=False: ImageFont.truetype(FB if b else F, sz * S)

BG0, BG1 = (18, 9, 38), (48, 24, 92)
WHITE, SEC, GRID = (244, 238, 255), (178, 165, 205), (70, 52, 110)
YEL, RED, GREEN, GT = (255, 216, 120), (232, 104, 118), (96, 214, 150), (190, 182, 210)

# ------------------------------------------------------------------ data
fw = json.load(open(f'{G}/{CAT}/framework/{EP}.json'))
bl = json.load(open(f'{G}/{CAT}/baseline/{EP}_result.json'))
n = int(fw['n_frames_native'])
subs = fw['subtasks']
K = len(subs)


def gt(f):
    for k, (s, e, _) in enumerate(subs):
        if f <= e:
            return (k + (f - s) / max(e - s, 1)) / K * 100
    return 100.0


def curve(d):
    x = np.array(d['frame_indices'], float)
    y = np.array([np.nan if v is None else v for v in d['scores_100']], float)
    m = ~np.isnan(y)
    return x[m], y[m]


fx, fy = curve(fw)
bx, by = curve(bl)
# the frozen PRM on the same frame grid as ProgressCompass, as in the paper's Figure 6
pick = [int(np.argmin(np.abs(bx - x))) for x in fx]
bx, by = fx.copy(), by[pick]
g = lambda xs: np.array([gt(v) for v in xs])
mae_b = np.mean(np.abs(by - g(bx)))
mae_f = np.mean(np.abs(fy - g(fx)))

# ---------------------------------------------------------------- frames
tmp = tempfile.mkdtemp()
subprocess.run(['ffmpeg', '-v', 'error', '-i', f'{G}/{CAT}/progress_{EP}.mp4', '-vf',
                f'crop=474:319:32:94,fps={N_PLAY}/{n / 30.0}', f'{tmp}/%04d.png'], check=True)
shots = sorted(os.listdir(tmp))

# -------------------------------------------------------------- layout
VX, VY, VW = 16 * S, 34 * S, 222 * S
VH = round(VW * 319 / 474)
PX0, PY0, PX1, PY1 = 280 * S, 40 * S, 464 * S, 222 * S       # plot box
bgimg = Image.new('RGB', (W, H))
px = bgimg.load()
for x in range(W):
    u = x / (W - 1)
    c = tuple(int(BG0[i] + (BG1[i] - BG0[i]) * u ** 1.4) for i in range(3))
    for y in range(H):
        px[x, y] = c


def to_xy(f, p):
    return (PX0 + (PX1 - PX0) * f / (n - 1), PY1 - (PY1 - PY0) * p / 100)


def polyline(d, xs, ys, upto, col, w):
    pts = [to_xy(a, b) for a, b in zip(xs, ys) if a <= upto]
    if len(pts) > 1:
        d.line(pts, fill=col, width=w, joint='curve')
    return pts[-1] if pts else None


frames = []
for i in range(N_PLAY + N_HOLD):
    k = min(i, N_PLAY - 1)
    fcur = (n - 1) * k / (N_PLAY - 1)
    im = bgimg.copy()
    d = ImageDraw.Draw(im)
    # title strip
    d.text((VX, 11 * S), 'PROGRESS ESTIMATION', font=font(11, True), fill=YEL)
    a = min(1.0, max(0.0, (i - N_PLAY + 4) / 8))
    if a < 1:
        d.text((PX0 - 14 * S, 11 * S), 'progress', font=font(11, True), fill=SEC)
    if a > 0:                                  # punchline once the episode has played
        c = tuple(int(BG1[j] + (YEL[j] - BG1[j]) * a) for j in range(3))
        d.text((PX0 - 14 * S, 11 * S), f'MAE {mae_b:.0f} \u2192 {mae_f:.0f}  \u00b7  lost \u2192 found',
               font=font(11, True), fill=c)
    # video, rounded
    shot = Image.open(f'{tmp}/{shots[min(len(shots) - 1, k)]}').convert('RGB').resize((VW, VH), Image.LANCZOS)
    mask = Image.new('L', (VW, VH), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, VW - 1, VH - 1), radius=10 * S, fill=255)
    im.paste(shot, (VX, VY), mask)
    d.rounded_rectangle((VX + 6 * S, VY + 6 * S, VX + 70 * S, VY + 22 * S), radius=5 * S, fill=(18, 9, 38))
    d.text((VX + 12 * S, VY + 8 * S), f't = {round(100 * fcur / (n - 1)):d}%', font=font(10, True), fill=WHITE)
    # the context: instruction of the current step
    step = next(k2 for k2, (s, e, _) in enumerate(subs) if fcur <= e)
    cy = VY + VH + 10 * S
    d.rounded_rectangle((VX, cy, VX + VW, H - 12 * S), radius=10 * S, fill=(38, 22, 72), outline=(116, 88, 170), width=S)
    d.text((VX + 10 * S, cy + 8 * S), f'THE RIGHT CONTEXT  ·  step {step + 1}/{K}', font=font(9, True), fill=YEL)
    for m, line in enumerate(textwrap.wrap(subs[step][2] + '.', 27)[:3]):
        d.text((VX + 10 * S, cy + 24 * S + m * 16 * S), line, font=font(12, True), fill=WHITE)
    # plot frame and grid
    for p in (0, 50, 100):
        y = to_xy(0, p)[1]
        d.line((PX0, y, PX1, y), fill=GRID, width=S)
        d.text((PX0 - 6 * S, y), f'{p}', font=font(9), fill=SEC, anchor='rm')
    for s, e, _ in subs[1:]:
        x = to_xy(s, 0)[0]
        d.line((x, PY1, x, PY1 + 4 * S), fill=SEC, width=S)
    # curves up to now
    xs = np.linspace(0, n - 1, 300)
    gpts = [to_xy(a, gt(a)) for a in xs if a <= fcur]
    for a in range(0, len(gpts) - 1, 2):                       # dashed ground truth
        d.line(gpts[a:a + 2], fill=GT, width=2 * S)
    pb = polyline(d, bx, by, fcur, RED, 3 * S)
    pf = polyline(d, fx, fy, fcur, GREEN, 3 * S)
    for p, col in ((pb, RED), (pf, GREEN)):
        if p:
            r = 5 * S
            d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=col, outline=WHITE, width=S)
    # legend
    ly = PY1 + 14 * S
    for m, (col, lbl) in enumerate(((GT, 'ground truth'), (RED, 'frozen PRM, no context'), (GREEN, 'ProgressCompass'))):
        yy = ly + m * 15 * S
        d.line((PX0, yy + 6 * S, PX0 + 16 * S, yy + 6 * S), fill=col, width=3 * S)
        d.text((PX0 + 22 * S, yy), lbl, font=font(10, m == 2), fill=WHITE if m == 2 else SEC)
    frames.append(im.resize((W // S, H // S), Image.LANCZOS))

# one shared palette keeps the file small and stops colours flickering
pal = frames[len(frames) // 2].quantize(colors=250, method=Image.Quantize.MEDIANCUT)
q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
q[0].save(OUT, save_all=True, append_images=q[1:], duration=MS, loop=0, optimize=True, disposal=1)
print(f'wrote {OUT}: {len(q)} frames, MAE {mae_b:.1f} -> {mae_f:.1f}, {os.path.getsize(OUT) / 1e6:.2f} MB')
