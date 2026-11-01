"""Extract frozen image embeddings (CPU) for every image in train/val/test.
usage: python scripts/embed.py --backbone clip   (or dinov2)
"""
import argparse, os, sys, numpy as np, torch
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PIL import Image
from flood_triage import data
ap = argparse.ArgumentParser(); ap.add_argument("--backbone", default="clip"); ap.add_argument("--out", default="results/emb")
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); torch.set_num_threads(os.cpu_count())
print_every = 10
if a.backbone == "clip":
    import open_clip
    model, _, pre = open_clip.create_model_and_transforms("ViT-B-16", pretrained="openai")
    enc = model.encode_image
else:
    import timm
    model = timm.create_model("vit_small_patch14_dinov2.lvd142m", pretrained=True, num_classes=0)
    cfg = timm.data.resolve_data_config({}, model=model); pre = timm.data.create_transform(**cfg); enc = model
model.eval()
for split in ["train", "val", "test"]:
    if os.path.exists(f"{a.out}/{a.backbone}_{split}.npz"): continue
    items = data.read_split(split); X = []
    with torch.no_grad():
        for i in range(0, len(items), 32):
            b = torch.stack([pre(Image.open(os.path.join(data.DATA_ROOT, p)).convert("RGB")) for p, _ in items[i:i+32]])
            X.append(torch.nn.functional.normalize(enc(b), dim=-1).numpy())
    np.savez(f"{a.out}/{a.backbone}_{split}.npz", X=np.concatenate(X), y=np.array([y for _, y in items]),
             paths=np.array([p for p, _ in items]))
    print(split, len(items), flush=True)
