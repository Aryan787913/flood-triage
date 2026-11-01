"""Compute metrics tables for every raw run in results/raw and write results/metrics.json."""
import glob, json, os, sys, statistics as st
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from collections import defaultdict, Counter
from flood_triage import metrics, data

def load(f): return [json.loads(l) for l in open(f) if l.strip()]

def spark_preds(rows, mode="first"):
    """Group by path; mode first = sample 0; vote = majority over samples, ties/disagreement -> None."""
    g = defaultdict(list)
    for r in rows: g[r["path"]].append(r)
    out = {}
    for p, rs in g.items():
        rs.sort(key=lambda r: r["sample"])
        if mode == "first":
            out[p] = rs[0]["parsed"]["level"]
        else:
            lv = [r["parsed"]["level"] for r in rs]
            c = Counter(lv).most_common()
            out[p] = c[0][0] if c[0][1] == len(lv) or (mode == "majority" and c[0][1] > len(lv) / 2) else None
    return out

def usage_stats(rows):
    lat = [r["latency_s"] for r in rows if r.get("latency_s")]
    pt = [r["usage"].get("prompt_tokens", 0) for r in rows]; ct = [r["usage"].get("completion_tokens", 0) for r in rows]
    return {"calls": len(rows), "errors": sum(1 for r in rows if not r["content"]),
            "latency_median_s": st.median(lat) if lat else None,
            "latency_p90_s": sorted(lat)[int(0.9 * len(lat)) - 1] if lat else None,
            "prompt_tokens_mean": sum(pt) / len(pt), "completion_tokens_mean": sum(ct) / len(ct)}

if __name__ == "__main__":
    res = {}
    for f in sorted(glob.glob("results/raw/spark_*.jsonl")):
        name = os.path.basename(f)[:-6]; rows = load(f)
        split = name.rsplit("_", 1)[1]
        truth = dict(data.read_split(split))
        modes = ["first"] + (["majority", "unanimous"] if max(r["sample"] for r in rows) > 0 else [])
        for m in modes:
            pr = spark_preds(rows, m); paths = [p for p in truth if p in pr]
            s = metrics.summarize([truth[p] for p in paths], [pr[p] for p in paths])
            s["abstain_X"] = sum(1 for r in rows if r["sample"] == 0 and r["parsed"]["abstain"])
            s["unparsed"] = sum(1 for r in rows if r["sample"] == 0 and not r["parsed"]["ok"])
            res[f"{name}:{m}"] = {**s, **usage_stats(rows)}
    for f in sorted(glob.glob("results/raw/baseline_*.jsonl")):
        rows = load(f); name = os.path.basename(f)[:-6]
        res[name] = metrics.summarize([r["label"] for r in rows], [r["pred"] for r in rows])
    json.dump(res, open("results/metrics.json", "w"), indent=1)
    for k, v in res.items():
        print(f"{k:45s} n={v['n']:3d} cov={v['coverage']:.2f} acc={v['accuracy_all']:.3f} sel={v['selective_accuracy']:.3f} "
              f"F1={v['macro_f1_all']:.3f} F1ans={v['macro_f1_answered']:.3f} off2={v['off_by_2plus']} under2={v['under_by_2plus']}")
