"""GIFs for the launch-thread draft, cut from the scenes of the intro video (no captions).

    python3 tools/make_thread_media.py   ->  webpage/thread-draft/m/2_problem.gif ... 6_results.gif
"""
import os, sys
from PIL import Image

VID = '/gpfs/projects/b1222/userdata/jianshu/code_keliang/Benchmark_Results_7_Methods/video_intro'
sys.path.insert(0, VID)
import make_video as mv                                      # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), '..', 'webpage', 'thread-draft', 'm')
os.makedirs(OUT, exist_ok=True)
GW, GH, FPS = 800, 450, 10


def clip(scene, base, speed=1.0, t0=0.6, t1=None):
    """Frames of one scene from t0 to t1 (scene time), played `speed` times faster."""
    t1 = base - 0.5 if t1 is None else t1
    n = int((t1 - t0) / speed * FPS)
    out = []
    for i in range(n):
        f = Image.new('RGBA', (mv.W, mv.H), mv.BG + (255,))
        scene(f, t0 + i * speed / FPS)
        out.append(f.convert('RGB').resize((GW, GH), Image.LANCZOS))
    return out


def save(name, frames, hold=12):
    frames = frames + [frames[-1]] * hold                   # rest on the last frame before looping
    pal = frames[len(frames) // 2].quantize(colors=240, method=Image.Quantize.MEDIANCUT)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    p = os.path.join(OUT, name)
    q[0].save(p, save_all=True, append_images=q[1:], duration=int(1000 / FPS), loop=0, optimize=True)
    print(f'{name}: {len(q)} frames, {os.path.getsize(p) / 1e6:.2f} MB')


save('2_problem.gif', clip(mv.s_forms, 16.0, speed=1.2))
save('3_bench.gif', clip(mv.s_bench, 12.0, speed=1.2))
save('4_finding.gif', clip(mv.s_context, 13.0, speed=1.4, t1=11.0) + clip(mv.s_diag, 16.0, speed=1.3))
save('5_method.gif', clip(mv.s_method, 20.0, speed=1.4))
save('6_results.gif', clip(mv.s_results, 16.0, speed=1.3) + clip(mv.s_robust, 14.0, speed=1.3))
