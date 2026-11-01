"""Model-described evidence overlay (no SAM): Spark returns a vehicle box and a waterline segment as image fractions."""
import io, re
from PIL import Image, ImageDraw
from . import client

PROMPT = ("Locate the vehicle and the floodwater line in this photo. Give coordinates as fractions of image width/height "
          "(0,0 = top-left, 1,1 = bottom-right). Reply only on one line: VEHICLE_BOX=x0,y0,x1,y1; WATERLINE=xa,ya,xb,yb "
          "(a straight segment along where the water surface meets the vehicle, or NONE if no water touches it)")

def _nums(s):
    v = [float(x) for x in re.findall(r"[0-9]*\.?[0-9]+", s or "")]
    return v[:4] if len(v) >= 4 and all(0 <= x <= 1 for x in v[:4]) else None

def locate(image_bytes):
    txt = client.classify(image_bytes, PROMPT)["content"]
    box = re.search(r"VEHICLE_BOX\s*=\s*([^;\n]*)", txt or ""); wl = re.search(r"WATERLINE\s*=\s*([^;\n]*)", txt or "")
    return {"box": _nums(box.group(1)) if box else None, "waterline": _nums(wl.group(1)) if wl else None, "raw": txt}

def draw(image_bytes, loc, colour=(230, 57, 70)):
    im = Image.open(io.BytesIO(image_bytes)).convert("RGB"); W, H = im.size; d = ImageDraw.Draw(im)
    lw = max(3, W // 120)
    if loc.get("box"):
        b = loc["box"]; d.rectangle([b[0] * W, b[1] * H, b[2] * W, b[3] * H], outline=(0, 180, 255), width=lw)
    if loc.get("waterline"):
        w = loc["waterline"]; d.line([w[0] * W, w[1] * H, w[2] * W, w[3] * H], fill=colour, width=lw + 2)
    return im
