import subprocess, sys
import numpy as np
from PIL import Image
B = "/workspace/hackathon/video/build/"
W, H, FPS = 1920, 1080, 25
TOTAL = 133.15
FULL = (960, 540, 1920)
def z(f, cx=960, cy=540): return (cx, cy, 1920 / f)
# (start, end, image, keyframes[(t_rel_frac or abs time, cx, cy, w)])  times absolute
S = [
 (0.00, 9.53, "p_problem1", [(0.00, *z(1.0)), (9.53, *z(1.05, 960, 440))]),
 (9.53, 16.06, "p_problem2", [(9.53, *z(1.12)), (16.06, *z(1.0))]),
 (16.06, 18.00, "p_title", [(16.06, *z(1.0)), (18.0, *z(1.06))]),
 (18.00, 27.93, "p_arch", [(18.0, *z(1.0)), (20.5, *z(1.0)), (24.0, *z(1.45, 620, 420)), (27.93, *z(1.45, 1150, 500))]),
 (27.93, 43.77, "s_report_R08", [(27.93, *FULL), (30.0, *FULL), (33.0, 1400, 380, 1050), (38.9, 1400, 380, 1050), (41.0, 900, 470, 1750), (43.77, 900, 470, 1750)]),
 (43.77, 52.04, "s_report_R01", [(43.77, *FULL), (46.0, 1050, 470, 1600), (52.04, 1250, 450, 1200)]),
 (52.04, 56.98, "s_queue", [(52.04, 600, 560, 1300), (54.0, 600, 560, 1300), (56.5, 1490, 500, 900), (56.98, 1490, 500, 900)]),
 (56.98, 62.50, "s_report_R04", [(56.98, *FULL), (59.0, 1200, 450, 1250), (62.5, 1200, 450, 1250)]),
 (62.50, 72.75, "s_note_keep", [(62.5, *FULL), (65.0, 960, 830, 1450), (72.75, 960, 860, 1400)]),
 (72.75, 82.12, "p_tested", [(72.75, *z(1.0)), (82.12, *z(1.08))]),
 (82.12, 94.61, "p_chart", [(82.12, *FULL), (84.5, *FULL), (86.75, 760, 560, 1100), (90.5, 760, 560, 1100), (94.61, 1440, 560, 1000)]),
 (94.61, 102.01, "p_gross", [(94.61, *z(1.15)), (97.0, *z(1.0)), (102.01, *z(1.04))]),
 (102.01, 108.30, "p_spark", [(102.01, *z(1.0)), (104.5, *z(1.4, 620, 540)), (106.0, *z(1.4, 1320, 540)), (108.3, *z(1.4, 1320, 540))]),
 (108.30, 114.59, "p_limits", [(108.3, *z(1.0)), (114.59, *z(1.07, 960, 500))]),
 (114.59, 121.14, "p_leak", [(114.59, *z(1.12)), (121.14, *z(1.0))]),
 (121.14, 127.39, "p_code", [(121.14, *z(1.0)), (124.0, *z(1.3, 960, 420)), (127.39, *z(1.3, 960, 420))]),
 (127.39, TOTAL, "p_end", [(127.39, *z(1.08)), (TOTAL, *z(1.0))]),
]
imgs = {}
def get(n):
    if n not in imgs:
        im = Image.open(B + n + ".png").convert("RGB")
        if im.size != (W, H):
            im = im.resize((W, H), Image.LANCZOS)
        imgs[n] = im
    return imgs[n]
def ease(u): return u * u * (3 - 2 * u)
def cam(kf, t):
    if t <= kf[0][0]: return kf[0][1:]
    for a, b in zip(kf, kf[1:]):
        if t <= b[0]:
            u = ease((t - a[0]) / max(1e-6, b[0] - a[0]))
            return tuple(a[i] + (b[i] - a[i]) * u for i in (1, 2, 3))
    return kf[-1][1:]
def render(name, kf, t):
    cx, cy, w = cam(kf, t); h = w * 9 / 16
    w = min(w, W); h = min(h, H)
    x0 = min(max(cx - w / 2, 0), W - w); y0 = min(max(cy - h / 2, 0), H - h)
    return get(name).resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + w, y0 + h))
XF = 0.35
out = sys.argv[1] if len(sys.argv) > 1 else B + "frames.mp4"
p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                      "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
n = int(TOTAL * FPS)
for k in range(n):
    t = k / FPS
    i = next(j for j, s in enumerate(S) if t < s[1] or j == len(S) - 1)
    s = S[i]
    fr = render(s[2], s[3], t)
    if i + 1 < len(S) and t > s[1] - XF:
        nx = S[i + 1]; a = (t - (s[1] - XF)) / XF
        fr = Image.blend(fr, render(nx[2], nx[3], nx[0]), a)
    if t < 0.5: fr = Image.blend(Image.new("RGB", (W, H)), fr, t / 0.5)
    if t > TOTAL - 0.6: fr = Image.blend(fr, Image.new("RGB", (W, H)), (t - (TOTAL - 0.6)) / 0.6)
    p.stdin.write(fr.tobytes())
p.stdin.close(); p.wait(); print("done", p.returncode)
