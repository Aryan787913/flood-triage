"""Learned hybrid: logistic regression on [baseline class probs, Spark answer one-hot (0-4, X)].
Fit on VAL only (grouped 5-fold CV reported for model selection), then applied once to TEST.
usage: python scripts/stack.py --spark fewshot [--apply_test]
"""
import argparse, json, os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from flood_triage import metrics, data
from analyze import load, spark_preds

def feats(split, sparks, backbone="clip", variant="official"):
    base = {r["path"]: r for r in load(f"results/raw/baseline_{backbone}_{variant}_{split}.jsonl")}
    sp = [spark_preds(load(f"results/raw/spark_{s}_{split}.jsonl"), "first") for s in sparks]
    paths = [p for p in base if all(p in d for d in sp)]
    X = []
    for p in paths:
        f = list(base[p]["prob"])
        for d in sp:
            oh = [0] * 6; oh[5 if d[p] is None else d[p]] = 1; f += oh
        X.append(f)
    return paths, np.array(X), np.array([base[p]["label"] for p in paths]), [base[p]["pred"] for p in paths], [sp[0][p] for p in paths]

ap = argparse.ArgumentParser(); ap.add_argument("--spark", default="fewshot"); ap.add_argument("--apply_test", action="store_true")
a = ap.parse_args(); sparks = a.spark.split(",")
P, X, y, bp, spp = feats("val", sparks)
groups = [data.source_id(p) for p in P]
best = None
for C in [0.03, 0.1, 0.3, 1, 3, 10, 30]:
    pred = np.zeros(len(y), int)
    for tr, te in GroupKFold(5).split(X, y, groups):
        pred[te] = LogisticRegression(C=C, max_iter=2000, class_weight="balanced").fit(X[tr], y[tr]).predict(X[te])
    s = metrics.summarize(list(y), list(pred))
    print(f"C={C} CV-on-val F1={s['macro_f1_all']:.3f} acc={s['accuracy_all']:.3f} off2={s['off_by_2plus']} under2={s['under_by_2plus']}")
    if best is None or s["macro_f1_all"] > best[0]: best = (s["macro_f1_all"], C, s)
print("best", best[1], round(best[0], 3))
json.dump({"spark": sparks, "C": best[1], "cv_val": best[2]}, open(f"results/stack_{'+'.join(sparks)}_val.json", "w"), indent=1)
if a.apply_test:
    clf = LogisticRegression(C=best[1], max_iter=2000, class_weight="balanced").fit(X, y)
    Pt, Xt, yt, _, _ = feats("test", sparks)
    pt = clf.predict(Xt); s = metrics.summarize(list(yt), list(pt))
    json.dump({"summary": s, "pred": {p: int(q) for p, q in zip(Pt, pt)}}, open(f"results/stack_{'+'.join(sparks)}_test.json", "w"), indent=1)
    print("TEST", s)
