"""Charts for README/video from results/final_test.json (written by scripts/final_eval.py)."""
import json, os, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
F = json.load(open("results/final_test.json"))
os.makedirs("results/charts", exist_ok=True)
plt.rcParams.update({"font.size": 13, "axes.spines.top": False, "axes.spines.right": False})
names = list(F["methods"]); M = F["methods"]
# 1. macro-F1 + off-by-2 errors
fig, ax = plt.subplots(1, 2, figsize=(13, 4.8))
cols = ["#2a9d8f" if ("hybrid" in n.lower() or "stack" in n.lower()) else ("#8d99ae" if "baseline" in n.lower() else "#457b9d") for n in names]
ax[0].barh(names, [M[n]["macro_f1_all"] for n in names], color=cols); ax[0].set_xlim(0, 1); ax[0].set_title("Macro-F1 (can't tell counted as wrong)")
for i, n in enumerate(names): ax[0].text(M[n]["macro_f1_all"] + 0.01, i, f"{M[n]['macro_f1_all']:.3f}", va="center")
ax[1].barh(names, [M[n]["off_by_2plus"] for n in names], color=cols); ax[1].set_title("Gross errors: off by 2+ levels (of 340)")
for i, n in enumerate(names): ax[1].text(M[n]["off_by_2plus"] + 0.3, i, str(M[n]["off_by_2plus"]), va="center")
ax[1].set_yticklabels([])
plt.tight_layout(); plt.savefig("results/charts/test_summary.png", dpi=150); plt.close()
# 2. confusion matrices
fig, axs = plt.subplots(1, len(F["confusion"]), figsize=(5.2 * len(F["confusion"]), 4.6))
for ax, (n, cm) in zip(np.atleast_1d(axs), F["confusion"].items()):
    cm = np.array(cm); ax.imshow(cm, cmap="Blues")
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]): ax.text(j, i, cm[i, j], ha="center", va="center", color="white" if cm[i, j] > cm.max() / 2 else "black")
    ax.set_xticks(range(6)); ax.set_xticklabels(["0", "1", "2", "3", "4", "X"]); ax.set_yticks(range(5))
    ax.set_xlabel("predicted (X = can't tell)"); ax.set_ylabel("true level"); ax.set_title(n, fontsize=12)
plt.tight_layout(); plt.savefig("results/charts/confusion.png", dpi=150); plt.close()
# 3. coverage vs selective accuracy
if "curves" in F:
    plt.figure(figsize=(7, 5))
    for n, pts in F["curves"].items():
        pts = sorted(pts); plt.plot([p[0] for p in pts], [p[1] for p in pts], marker="o", ms=3, label=n)
    plt.xlabel("coverage (share of reports answered)"); plt.ylabel("accuracy on answered reports"); plt.legend(loc="lower left", fontsize=10); plt.grid(alpha=.3)
    plt.title("Answer less, be right more"); plt.tight_layout(); plt.savefig("results/charts/coverage_accuracy.png", dpi=150); plt.close()
print("charts ok")
