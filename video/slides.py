import glob, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import ImageFormatter

B = "/workspace/hackathon/video/build/"
R = "/workspace/hackathon/repo/"
W, H = 1920, 1080
BG = (15, 27, 45); FG = (245, 247, 250); MUTED = (160, 176, 200); TEAL = (42, 157, 143); ORANGE = (244, 162, 97); RED = (230, 57, 70)
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"; FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def font(s, b=False): return ImageFont.truetype(FB if b else F, s)

def canvas(): return Image.new("RGB", (W, H), BG)

def text_c(d, y, s, f, fill=FG):
    w = d.textlength(s, font=f); d.text(((W - w) / 2, y), s, font=f, fill=fill)

def panel(img, box, pad=24, bg=(255, 255, 255)):
    x0, y0, x1, y1 = box
    pnl = Image.new("RGB", (x1 - x0, y1 - y0), bg)
    im = img.copy(); im.thumbnail((x1 - x0 - 2 * pad, y1 - y0 - 2 * pad), Image.LANCZOS)
    pnl.paste(im, ((pnl.width - im.width) // 2, (pnl.height - im.height) // 2))
    m = Image.new("L", pnl.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, pnl.width, pnl.height], 28, fill=255)
    return pnl, m

def put_panel(c, img, box, **kw):
    p, m = panel(img, box, **kw); c.paste(p, box[:2], m)

# 1. problem: collage of real dataset flood photos
cands = sorted(glob.glob("/workspace/hackathon/data/upscaled_images/Level3/*.jpg") + glob.glob("/workspace/hackathon/data/upscaled_images/Level4/*.jpg"), key=os.path.getsize, reverse=True)
picks = [cands[i] for i in (0, 15, 31, 47, 63, 79)]
def collage():
    c = canvas(); d = ImageDraw.Draw(c)
    tw, th = 600, 330
    for i, p in enumerate(picks):
        im = Image.open(p).convert("RGB")
        r = max(tw / im.width, th / im.height); im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
        im = im.crop(((im.width - tw) // 2, (im.height - th) // 2, (im.width - tw) // 2 + tw, (im.height - th) // 2 + th))
        x = 30 + (i % 3) * (tw + 30); y = 30 + (i // 3) * (th + 30)
        m = Image.new("L", (tw, th), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, tw, th], 22, fill=255); c.paste(im, (x, y), m)
    return c
c = collage(); d = ImageDraw.Draw(c)
d.rectangle([0, 740, W, H], fill=BG)
text_c(d, 760, "Every monsoon, cities ask citizens for flood photos", font(62, True))
text_c(d, 845, "Gurugram's flood portal also asks people to guess the depth themselves", font(36), MUTED)
c.save(B + "p_problem1.png")

c = collage().filter(ImageFilter.GaussianBlur(9)); ov = Image.new("RGB", (W, H), BG); c = Image.blend(c, ov, 0.62); d = ImageDraw.Draw(c)
text_c(d, 300, "Hundreds of photos. Hundreds of guesses.", font(64, True))
text_c(d, 420, "Which street needs help first?", font(64, True), ORANGE)
text_c(d, 590, "Photos in this video: STURM-FloodDepth dataset (CC BY 4.0)", font(30), MUTED)
c.save(B + "p_problem2.png")

# 2. title
c = canvas(); d = ImageDraw.Draw(c)
text_c(d, 330, "flood-triage", font(150, True))
text_c(d, 540, "Ranks citizen flood photos worst-first", font(54), FG)
text_c(d, 630, "with Meta's open-weight Muse Spark Open", font(54), TEAL)
c.save(B + "p_title.png")

# 3. architecture
c = canvas(); d = ImageDraw.Draw(c)
text_c(d, 40, "How it works", font(56, True))
put_panel(c, Image.open(R + "docs/architecture.png").convert("RGB"), (60, 140, 1860, 900))
c.save(B + "p_arch.png")

# results slides
c = canvas(); d = ImageDraw.Draw(c)
text_c(d, 150, "Tested honestly", font(80, True))
rows = [("340", "held-out test photos (STURM-FloodDepth)"), ("val only", "every prompt and threshold chosen on validation"), ("once", "test set scored a single time")]
for i, (a, b) in enumerate(rows):
    y = 330 + i * 150
    d.rounded_rectangle([200, y, 1720, y + 120], 24, fill=(27, 43, 68))
    d.text((240, y + 25), a, font=font(60, True), fill=TEAL)
    d.text((620, y + 38), b, font=font(40), fill=FG)
c.save(B + "p_tested.png")

c = canvas(); d = ImageDraw.Draw(c)
text_c(d, 40, "Results on 340 test photos", font(56, True))
put_panel(c, Image.open(R + "results/charts/test_summary.png").convert("RGB"), (60, 140, 1860, 880))
c.save(B + "p_chart.png")

c = canvas(); d = ImageDraw.Draw(c)
text_c(d, 120, "Dangerous mistakes (off by 2+ levels)", font(60, True))
d.text((420, 300), "29", font=font(260, True), fill=RED)
d.text((830, 360), "\u2192", font=font(200, True), fill=FG)
d.text((1200, 300), "17", font=font(260, True), fill=TEAL)
d.text((370, 620), "image classifier", font=font(44), fill=MUTED)
d.text((1170, 620), "hybrid with Spark", font=font(44), fill=MUTED)
text_c(d, 760, "Macro-F1  0.619  \u2192  0.647", font(64, True), FG)
c.save(B + "p_gross.png")

c = canvas(); d = ImageDraw.Draw(c)
text_c(d, 180, "Spark on its own", font(76, True))
d.rounded_rectangle([260, 360, 930, 720], 30, fill=(27, 43, 68)); d.rounded_rectangle([990, 360, 1660, 720], 30, fill=(27, 43, 68))
text_c_box = lambda x0, x1, y, s, f, col: d.text((x0 + (x1 - x0 - d.textlength(s, font=f)) / 2, y), s, font=f, fill=col)
text_c_box(260, 930, 400, "5", font(150, True), TEAL); text_c_box(260, 930, 600, "big misses out of 340", font(38), FG)
text_c_box(990, 1660, 400, "-1", font(150, True), ORANGE); text_c_box(990, 1660, 600, "level: tends to read low", font(38), FG)
c.save(B + "p_spark.png")

# honesty
c = canvas(); d = ImageDraw.Draw(c)
text_c(d, 110, "What it doesn't do", font(72, True))
for i, s in enumerate(["No depth in centimetres: levels are relative to the vehicle", "Vehicle sizes vary: bikes, buses, SUVs", "Mostly tested on car photos", "A triage hint for an officer, not a public warning"]):
    y = 280 + i * 125
    d.ellipse([300, y + 18, 330, y + 48], fill=ORANGE); d.text((370, y), s, font=font(46), fill=FG)
c.save(B + "p_limits.png")

c = canvas(); d = ImageDraw.Draw(c)
text_c(d, 150, "We found a leak, and report it", font(72, True))
d.text((330, 340), "232", font=font(200, True), fill=ORANGE)
d.text((760, 360), "of 340 test crops share a source", font=font(50), fill=FG)
d.text((760, 430), "photo with train or validation", font=font(50), fill=FG)
text_c(d, 640, "So we also report a leak-free baseline: 0.580 macro-F1", font(46), MUTED)
c.save(B + "p_leak.png")

code = '''BASE_URL = "https://inference.baseten.co/v1"
MODEL = "meta-models/muse-spark-open-1026"   # Meta, open weights

def classify(image, prompt, **kw):
    return chat([{"role": "user", "content": [
        {"type": "text", "text": prompt}, image_part(image)]}], **kw)

# 3 independent reads -> majority vote; disagreement -> "can't tell"
votes = [parse_level(classify(photo, FEWSHOT_PROMPT)) for _ in range(3)]
'''
ci = Image.open(__import__("io").BytesIO(highlight(code, PythonLexer(), ImageFormatter(font_name="DejaVu Sans Mono", font_size=34, line_numbers=False, style="monokai", image_pad=30)))).convert("RGB")
c = canvas(); d = ImageDraw.Draw(c)
text_c(d, 60, "Open weights: a city can run it on its own servers", font(54, True))
c.paste(ci, ((W - ci.width) // 2, 200))
text_c(d, 220 + ci.height, "Simplified from flood_triage/client.py and scripts/run_spark.py", font(30), MUTED)
c.save(B + "p_code.png")

c = canvas(); d = ImageDraw.Draw(c)
text_c(d, 300, "flood-triage", font(140, True))
text_c(d, 500, "github.com/Aryan787913/flood-triage", font(56), TEAL)
text_c(d, 610, "Built during the Meta Global AI Developer Hackathon by Aaryan Singh", font(36), FG)
text_c(d, 670, "Muse Spark Open (Meta) via Baseten \u00b7 Data: STURM-FloodDepth, CC BY 4.0 \u00b7 AI voiceover", font(30), MUTED)
c.save(B + "p_end.png")
print("ok")
