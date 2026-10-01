"""Launch-thread draft page for X, in the layout of the Video2Skill draft.

Each post is written once below. The character count follows X: a URL counts as 23, an emoji
as 2. Posts over 280 fold behind "Show more" at the point X would cut them.

    python3 tools/make_thread.py   ->  webpage/thread-draft/index.html
"""
import html, os, re

OUT = os.path.join(os.path.dirname(__file__), '..', 'webpage', 'thread-draft', 'index.html')
PAGE = 'https://andyzworks.github.io/progresscompass/'
PDF = PAGE + 'static/paper/ProgressCompass.pdf'
CODE = 'https://github.com/andyzworks/progresscompass'

# text: **bold**, blank line = paragraph, [label](url) = link shown as label
POSTS = [
    ('Main post', '1_main.gif', '16 / 10',
     'Animated loop: a robot covers three blocks and uncovers them in colour order. Beside the video, the '
     'instruction of the current step is shown as the context. On the right, the frozen PRM without context '
     'jumps around and ends near 20, while ProgressCompass follows the true progress to 100; MAE 33 to 3.',
     """🤖 **Progress Reward Models (PRMs)** score how far a robot task has come at every step. They serve as dense rewards, step verifiers and execution monitors.

⏳ But in long tasks, **the current frame often can't tell.** Two frames can look the same and sit at very different progress, because what matters happened earlier.

🧭 So we ask: **are PRMs blind, or just lost?**

🧵 **ProgressCompass: Embodied Progress Reward Models Are Lost Without the Right Context**

Our answer: **not blind, but lost.** Given the right context, every PRM we test cuts its error by 77–82%. ProgressCompass supplies that context to a frozen PRM with general-purpose VLMs, with no training.

📄 Paper: [andyzworks.github.io/progr…]({PDF})
🌐 Project: [andyzworks.github.io/progr…]({PAGE})"""),

    ('The problem', '2_problem.gif', '16 / 9',
     'Animated figure: one instruction, move each red block to the green mat and back, from left to right. '
     'Three moments are highlighted in turn: State Recall, Sequence Tracking and Recurrence Disambiguation.',
     """🎯 **The problem: context-dependent progress estimation.** One instruction: move each red block to the green mat and back, from left to right. Three moments the current frame can't score:

1️⃣ **State Recall**: which mat did this block come from? That fact has left the frame.
2️⃣ **Sequence Tracking**: is the leftmost block done? The order isn't visible in one frame.
3️⃣ **Recurrence Disambiguation**: just before and just after a placement, the frames look the same."""),

    ('The benchmark', '3_bench.gif', '16 / 9',
     'ContextProgress-Bench statistics: 24 hand-selected tasks, 120 episodes, 552 annotated subtasks, 3 context '
     'settings; charts of settings per episode, totals per setting, episode length and steps per episode.',
     """📏 **ContextProgress-Bench.** Existing progress benchmarks mostly use short tasks that one frame can answer.

We hand-select **24 tasks** where it can't, from RMBench, RoboDojo and LIBERO-Mem: **120 episodes** (5 sampled at random per task) and **552 annotated subtask intervals**, each with the context it needs."""),

    ('Finding', '4_finding.gif', '16 / 9',
     'Animated explainer: the single episode instruction is struck through and replaced by one instruction per '
     'step. Then the progress error of five PRMs shrinks from without context to with the right context, '
     'by 77 to 82 percent for each model.',
     """🔍 **Finding: PRMs are not blind, but lost.** We run 5 PRMs twice with the same input format. In one run, the instruction carries the right context: the step that is underway.

❌ **Without it**: MAE 15.6–31.0 on a 0–100 scale. Even PRMs that read the whole history get lost.
✅ **With it**: every PRM cuts its error by **77–82%**, and the gain holds on 93.3% of paired intervals."""),

    ('ProgressCompass', '5_method.gif', '16 / 9',
     'Diagram of the ProgressCompass loop: the Navigator runs the loop; the Orienter gives the context to the '
     'frozen PRM and the expected transition to the Verifier; the PRM proposes a completion and the Verifier '
     'checks it until the step is accepted.',
     """🧭 **ProgressCompass.** A PRM scores a step well once it knows the step, but it can't work out the step from the history. A VLM is the reverse: a poor progress estimator, but good at understanding a task and its steps.

So we pair them in an agentic loop, with the PRM frozen:
🧭 **Orienter** (VLM) states the current step and the expected transition
📈 **PRM** scores progress within that step
✅ **Verifier** (VLM) checks that the step is really done
🗺️ **Navigator** (text-only) runs the loop and keeps the verified plan"""),

    ('Results', '6_results.gif', '16 / 9',
     'Animated results: MAE of the frozen RoboMeter falls from 25.4 to 9.3 and rank agreement rises from 0.53 to '
     '0.93 inside ProgressCompass, with progress curves on three episodes. Then deviation on Early stop, Extra '
     'steps and Mismatch, and time per episode falling from 114.7 to 39.5 seconds.',
     """📊 **Results.** Wrapped in the loop, the same frozen RoboMeter goes from **MAE 25.4 → 9.3** (−63%) and **rank agreement 0.53 → 0.93** (+76%). It is the best method on every context form, ahead of every frozen PRM and of R²VLM.

🛡️ It stays robust when the video stops early, does more than asked, or follows an unrelated task.

⚡ Parallelizing the loop, so that no component sits idle, cuts wall-clock time by 65.6%."""),

    ('Takeaway and links', None, '16 / 9', 'Two-minute walkthrough of ProgressCompass, with captions.',
     """💡 **Takeaway:** a PRM doesn't need to interpret the whole history itself. It needs to be **told where in the task it is.** For long tasks, the right context matters more than more history.

📝 Limits: we study robot manipulation so far, and the loop relies on the VLMs reading the scene correctly.

👥 Joint work with Keliang Wu (co-first), Chengxuan Qian, Xiyuan Yang, @zhangce1203, Ariel Tian, Anbang Liu, Haoran Lu, and Han Liu (Northwestern, UCSB, UIUC, CMU).
🌐 [andyzworks.github.io/progr…]({PAGE})
🎬 2-min walkthrough below."""),
]

EMOJI = re.compile('[\U0001F000-\U0001FAFF☀-➿⬀-⯿️⃣]')
LINK = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')


def x_len(s):
    """Character count as X computes it: links are 23, emoji 2 (keycap sequences count once)."""
    s = LINK.sub('x' * 23, s).replace('**', '')
    s = re.sub(r'[0-9]️⃣', 'EE', s)
    return len(EMOJI.sub('', s)) + 2 * len(re.findall('[\U0001F000-\U0001FAFF☀-➿⬀-⯿]', s))


def render(s):
    out = html.escape(s)
    out = re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
                 lambda m: f'<a href="{m.group(2)}" target="_blank" rel="noopener">{m.group(1)}</a>', out)
    out = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', out)
    return out.replace('\n', '<br>')


def split_at(s, limit=280):
    """Cut the raw text where X would fold it: the last space before the limit."""
    if x_len(s) <= limit:
        return s, ''
    cut = 0
    for m in re.finditer(r'\s', s):
        if x_len(s[:m.start()]) > limit - 6:
            break
        if s.count('**', 0, m.start()) % 2 == 0 and s.count('[', 0, m.start()) == s.count(']', 0, m.start()):
            cut = m.start()
    return s[:cut], s[cut:]


posts = []
n = len(POSTS)
for i, (role, media, ratio, alt, text) in enumerate(POSTS, 1):
    text = text.replace('{PDF}', PDF).replace('{PAGE}', PAGE)
    count = x_len(text)
    shown, rest = split_at(text)
    if rest:
        body = (f'<span class="shown">{render(shown)}</span><span class="dots">… </span>'
                f'<button class="more" type="button">Show more</button><span class="rest" hidden>{render(rest)}</span>')
        badge = f'<span class="count fold">{count} chars · folds</span>'
    else:
        body = render(text)
        badge = f'<span class="count">{count}/280</span>'
    if media:
        fig = (f'<figure class="media" style="aspect-ratio:{ratio}"><img src="m/{media}" alt="{html.escape(alt)}" '
               f'loading="{"eager" if i < 3 else "lazy"}"><span class="badge">GIF</span></figure>')
    else:
        fig = (f'<figure class="media" style="aspect-ratio:{ratio}"><video controls preload="metadata" playsinline '
               f'poster="../static/video/poster.jpg" src="../static/video/progresscompass_overview.mp4"></video></figure>')
    line = '<span class="line"></span>' if i < n else ''
    posts.append(f'''<article class="post{' lead' if i == 1 else ''}">
  <div class="rail"><img class="av" src="m/avatar.jpg" alt="">{line}</div>
  <div class="body">
    <header><span class="name">Jianshu Zhang</span> <span class="handle">@SterZhang</span><span class="role">{i}/{n} · {role}</span>{badge}</header>
    <p class="text">{body}</p>{fig}<details class="alt"><summary>Alt text</summary><p>{html.escape(alt)}</p></details>
  </div>
</article>''')
    print(f'{i}/{n} {role:20s} {count:5d} chars{"  folds" if rest else ""}')

css = open(os.path.join(os.path.dirname(__file__), 'thread.css')).read()
page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex, nofollow">
<title>ProgressCompass Thread Draft</title>
<style>*,*::before,*::after{{box-sizing:border-box}} body{{margin:0}} img{{max-width:100%}} [hidden]{{display:none!important}}</style>
</head>
<body>
<style>
{css}
</style>
<main class="wrap">
  <section class="intro">
    <span class="tag">Draft preview · not posted</span>
    <h1>ProgressCompass launch thread</h1>
    <p>{n} posts for a Premium account, following the abstract: a main post on why progress reward models matter and
    where they fail, then the problem, the benchmark, the finding, the method, the results, and a takeaway. Posts longer
    than about 280 characters fold behind "Show more" in the timeline, as shown here.</p>
  </section>
  <section class="thread" aria-label="Thread draft">
{chr(10).join(posts)}
  </section>
</main>
<script>
document.querySelectorAll('.more').forEach(function (b) {{
  b.addEventListener('click', function () {{
    var p = b.parentElement;
    p.querySelector('.rest').hidden = false; p.querySelector('.dots').hidden = true; b.hidden = true;
  }});
}});
</script>
</body>
</html>
'''
open(OUT, 'w').write(page)
print('wrote', os.path.abspath(OUT))
