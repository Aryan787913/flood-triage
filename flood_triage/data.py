import os, re
DATA_ROOT = os.environ.get("FLOOD_DATA", "data/upscaled_images")

def read_split(split, splits_dir="splits"):
    """List of (relpath, level) with forward slashes."""
    out = []
    for l in open(os.path.join(splits_dir, f"{split}.txt")):
        l = l.strip().replace("\\", "/")
        if l:
            out.append((l, int(re.search(r"Level(\d)", l).group(1))))
    return out

def source_id(relpath):
    """Crops of the same source photo share 'car-N' / 'car2-N'."""
    return re.match(r"(car\d*-\d+)-Level", os.path.basename(relpath)).group(1)
