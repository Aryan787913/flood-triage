"""Linear-probe baseline: frozen embeddings + logistic regression (C tuned on val).
Reports official split AND a leakage-free variant (train crops whose source photo also appears in test removed).
usage: python scripts/baseline.py --backbone clip
"""
import argparse, json, os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sklearn.linear_model import LogisticRegression
from flood_triage import data, metrics
ap = argparse.ArgumentParser(); ap.add_argument("--backbone", default="clip"); a = ap.parse_args()
L = lambda s: np.load(f"results/emb/{a.backbone}_{s}.npz")
tr, va, te = L("train"), L("val"), L("test")
sid = lambda P: np.array([data.source_id(p) for p in P])
te_ids = set(sid(te["paths"]))
out = {}
for variant in ["official", "grouped"]:
    keep = np.ones(len(tr["y"]), bool) if variant == "official" else ~np.isin(sid(tr["paths"]), list(te_ids))
    vkeep = np.ones(len(va["y"]), bool) if variant == "official" else ~np.isin(sid(va["paths"]), list(te_ids))
    best = None
    for C in [0.1, 0.3, 1, 3, 10, 30, 100, 300]:
        clf = LogisticRegression(C=C, max_iter=3000, class_weight="balanced").fit(tr["X"][keep], tr["y"][keep])
        f = metrics.macro_f1(list(va["y"][vkeep]), list(clf.predict(va["X"][vkeep])))
        if best is None or f > best[0]: best = (f, C)
    clf = LogisticRegression(C=best[1], max_iter=3000, class_weight="balanced").fit(tr["X"][keep], tr["y"][keep])
    prob = clf.predict_proba(te["X"]); pred = prob.argmax(1)
    s = metrics.summarize(list(te["y"]), [int(x) for x in pred])
    s.update(C=float(best[1]), val_macro_f1=float(best[0]), n_train=int(keep.sum()))
    out[variant] = s
    rows = [{"path": str(p), "label": int(y), "pred": int(q), "prob": [round(float(v), 4) for v in pr]}
            for p, y, q, pr in zip(te["paths"], te["y"], pred, prob)]
    with open(f"results/raw/baseline_{a.backbone}_{variant}_test.jsonl", "w") as f:
        f.write("\n".join(json.dumps(r) for r in rows) + "\n")
    # val predictions (for hybrid tuning) from the same model
    vp = clf.predict_proba(va["X"])
    with open(f"results/raw/baseline_{a.backbone}_{variant}_val.jsonl", "w") as f:
        f.write("\n".join(json.dumps({"path": str(p), "label": int(y), "pred": int(q.argmax()), "prob": [round(float(v), 4) for v in q]})
                          for p, y, q in zip(va["paths"], va["y"], vp)) + "\n")
print(json.dumps(out, indent=1))
json.dump(out, open(f"results/baseline_{a.backbone}.json", "w"), indent=1)
