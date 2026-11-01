"""Combine the linear-probe baseline with Spark. All rules/thresholds are chosen on VAL; --split test applies them once.
usage: python scripts/hybrid.py --spark structured --split val
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flood_triage import metrics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import load, spark_preds

def rows_for(split, spark, backbone, variant):
    base = {r["path"]: r for r in load(f"results/raw/baseline_{backbone}_{variant}_{split}.jsonl")}
    sp_rows = load(f"results/raw/spark_{spark}_{split}.jsonl")
    sp1 = spark_preds(sp_rows, "first")
    spm = spark_preds(sp_rows, "majority") if max(r["sample"] for r in sp_rows) > 0 else sp1
    conf = {r["path"]: r["parsed"]["confidence"] for r in sp_rows if r["sample"] == 0}
    paths = [p for p in base if p in sp1]
    return [(p, base[p]["label"], base[p]["pred"], max(base[p]["prob"]), spm[p], conf.get(p)) for p in paths]

RULES = {
    "baseline": lambda b, pb, s, c, t: b,
    "baseline+abstain(p<t)": lambda b, pb, s, c, t: b if pb >= t else None,
    "spark": lambda b, pb, s, c, t: s,
    "arbitrate: spark overrides when |diff|>=2": lambda b, pb, s, c, t: s if (s is not None and abs(s - b) >= 2) else b,
    "arbitrate: spark when baseline unsure (p<t)": lambda b, pb, s, c, t: (s if s is not None else b) if pb < t else b,
    "agree-or-abstain (|diff|<=1 -> spark)": lambda b, pb, s, c, t: s if (s is not None and abs(s - b) <= 1) else None,
    "spark, else baseline if confident (p>=t)": lambda b, pb, s, c, t: s if s is not None else (b if pb >= t else None),
}

def evaluate(rows, rule, t):
    return metrics.summarize([r[1] for r in rows], [RULES[rule](r[2], r[3], r[4], r[5], t) for r in rows])

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--spark", default="structured"); ap.add_argument("--split", default="val")
    ap.add_argument("--backbone", default="clip"); ap.add_argument("--variant", default="official")
    ap.add_argument("--thresholds", default="results/hybrid_thresholds.json")
    a = ap.parse_args()
    rows = rows_for(a.split, a.spark, a.backbone, a.variant)
    grid = [round(0.3 + 0.05 * i, 2) for i in range(13)]
    chosen = json.load(open(a.thresholds)) if a.split == "test" else {}
    out = {}
    for rule in RULES:
        if a.split == "val":
            # pick t maximising macro-F1 (abstain counts wrong), tie-break by fewer off-by-2
            best = max(grid, key=lambda t: (round(evaluate(rows, rule, t)["macro_f1_all"], 4), -evaluate(rows, rule, t)["off_by_2plus"]))
            chosen[f"{a.spark}|{rule}"] = best
        t = chosen.get(f"{a.spark}|{rule}", 0.5)
        out[rule] = {**evaluate(rows, rule, t), "t": t}
        s = out[rule]
        print(f"{rule:45s} t={t:.2f} n={s['n']} cov={s['coverage']:.2f} F1={s['macro_f1_all']:.3f} acc={s['accuracy_all']:.3f} sel={s['selective_accuracy']:.3f} off2={s['off_by_2plus']} under2={s['under_by_2plus']}")
    if a.split == "val":
        old = json.load(open(a.thresholds)) if os.path.exists(a.thresholds) else {}
        old.update(chosen); json.dump(old, open(a.thresholds, "w"), indent=1)
    json.dump(out, open(f"results/hybrid_{a.spark}_{a.split}.json", "w"), indent=1)
