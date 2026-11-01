"""Pick one reference image per level from TRAIN (source photos never shared with val/test)."""
import os, random
from PIL import Image
from . import data

# Hand-checked train examples (source photos not in val/test), chosen by eye on 1 Nov from seeds 0-2.
FIXED = ["Level0/car-2122-Level0_3.jpg", "Level1/car-1964-Level1_2.jpg", "Level2/car-603-Level2_1.jpg",
         "Level3/car-308-Level3_1.jpg", "Level4/car-187-Level4_1.jpg"]

def pick_examples(seed=None, min_side=280, splits_dir="splits"):
    if seed is None:
        return list(FIXED)
    banned = {data.source_id(p) for s in ("val", "test") for p, _ in data.read_split(s, splits_dir)}
    rng = random.Random(seed); out = {}
    tr = data.read_split("train", splits_dir); rng.shuffle(tr)
    for p, y in tr:
        if y in out or data.source_id(p) in banned: continue
        w, h = Image.open(os.path.join(data.DATA_ROOT, p)).size
        if min(w, h) >= min_side: out[y] = p
        if len(out) == 5: break
    return [out[k] for k in sorted(out)]

def build_messages(image_path, examples, prompt_text, intro):
    from .client import image_part
    content = [{"type": "text", "text": intro}]
    for p in examples:
        lvl = int(p.split("Level")[1][0])
        content += [{"type": "text", "text": f"Example: level {lvl}"}, image_part(os.path.join(data.DATA_ROOT, p))]
    content += [{"type": "text", "text": "Now the photo to classify:"}, image_part(image_path), {"type": "text", "text": prompt_text}]
    return [{"role": "user", "content": content}]
