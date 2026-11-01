"""Architecture diagram -> docs/architecture.png"""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
fig, ax = plt.subplots(figsize=(14, 6.2)); ax.set_xlim(0, 14); ax.set_ylim(0, 6.2); ax.axis("off")
def box(x, y, w, h, title, body, col):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.15", fc=col, ec="#1d3557", lw=1.5))
    ax.text(x + w / 2, y + h - 0.3, title, ha="center", va="top", fontsize=12.5, weight="bold", color="#1d3557")
    ax.text(x + w / 2, y + h - 0.75, body, ha="center", va="top", fontsize=10, color="#1d3557", linespacing=1.4)
def arrow(x1, y1, x2, y2, t=""):
    ax.annotate("", (x2, y2), (x1, y1), arrowprops=dict(arrowstyle="-|>", lw=1.8, color="#1d3557"))
    if t: ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.15, t, ha="center", fontsize=9, color="#457b9d")
box(0.2, 2.2, 2.4, 2.0, "Citizen report", "street photo\n+ location, time\n+ own depth guess\n(ankle/knee/waist)", "#f1faee")
box(3.3, 3.6, 3.6, 2.3, "Muse Spark Open (Meta)", "few-shot: 5 labelled reference crops\nlocate vehicle -> waterline -> level\n3 independent reads (self-consistency)\nL0-L4 or X = can't tell + evidence", "#a8dadc")
box(3.3, 0.4, 3.6, 2.3, "Open image baseline", "CLIP ViT-B/16 (frozen)\n+ logistic regression\ntrained on STURM-FloodDepth\ntrain split", "#e9ecef")
box(7.6, 2.0, 2.8, 2.3, "Hybrid decision", "baseline unsure (p < t)\n-> Spark decides\nreadings disagree\n-> can't tell (human)\nt chosen on val only", "#ffe8a3")
box(11.0, 3.6, 2.8, 2.3, "Triage agent (Spark)", "self-report check\nduplicate flags\nworst-first queue + map\ndraft note for ward officer", "#a8dadc")
box(11.0, 0.4, 2.8, 2.3, "Evidence view", "waterline + vehicle box\ndescribed by Spark\n(SAM 3.1 masks: optional,\nneeds gated access)", "#f1faee")
arrow(2.6, 3.6, 3.3, 4.6); arrow(2.6, 2.8, 3.3, 1.6)
arrow(6.9, 4.6, 7.6, 3.6); arrow(6.9, 1.6, 7.6, 2.6)
arrow(10.4, 3.4, 11.0, 4.5); arrow(10.4, 2.8, 11.0, 1.6)
ax.text(7, 6.05, "flood-triage: decision support for civic flood-report portals (levels relative to vehicle parts, not cm)", ha="center", fontsize=12, style="italic", color="#1d3557")
plt.savefig("docs/architecture.png", dpi=150, bbox_inches="tight"); print("ok")
