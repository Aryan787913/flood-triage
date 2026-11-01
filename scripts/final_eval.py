"""One-shot test evaluation of every config frozen on val. Writes results/final_test.json + results/results.md.
usage: python scripts/final_eval.py
"""
import json, os, sys, statistics as st
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flood_triage import metrics, data
from analyze import load, spark_preds, usage_stats
import hybrid as H

PRICE_IN, PRICE_OUT = 1.25e-6, 4.25e-6   # Baseten Model API, USD per token (baseten.co/library/muse-spark-open, Oct 2026)
CFG = json.load(open("results/final_config.json"))   # written after val selection
truth = dict(data.read_split("test")); paths = list(truth)
y = [truth[p] for p in paths]
methods, conf, preds = {}, {}, {}

def add(name, pmap, show_conf=False):
    p = [pmap.get(q) for q in paths]; preds[name] = p
    methods[name] = metrics.summarize(y, p)
    if show_conf: conf[name] = metrics.confusion(y, p)

for v in ("official", "grouped"):
    b = {r["path"]: r["pred"] for r in load(f"results/raw/baseline_clip_{v}_test.jsonl")}
    add(f"Baseline CLIP probe ({v} split)", b, show_conf=(v == "official"))
zs = load("results/raw/spark_zero_shot_test.jsonl"); add("Spark zero-shot", spark_preds(zs, "first"), True)
fs = load("results/raw/spark_fewshot_test.jsonl")
add("Spark few-shot (1 read)", spark_preds(fs, "first"))
add("Spark few-shot x3 (majority)", spark_preds(fs, "majority"))
rows = H.rows_for("test", CFG["hybrid_spark"], "clip", "official")
rule, t = CFG["hybrid_rule"], CFG["hybrid_t"]
add("Hybrid (baseline + Spark)", {r[0]: H.RULES[rule](r[2], r[3], r[4], r[5], t) for r in rows}, True)
if os.path.exists("results/stack_fewshot_test.json"):
    add("Learned stack (secondary, fit on val)", json.load(open("results/stack_fewshot_test.json"))["pred"])
# coverage / selective accuracy curves: baseline by max-prob threshold, hybrid by abstaining when Spark reads disagree & baseline unsure
base = {r["path"]: r for r in load("results/raw/baseline_clip_official_test.jsonl")}
curves = {"Baseline (abstain if max prob < t)": [], "Hybrid (abstain if Spark reads disagree and baseline p < t)": []}
spm = spark_preds(fs, "majority"); spu = spark_preds(fs, "unanimous")
for i in range(0, 20):
    tt = 0.2 + 0.04 * i
    bp = [base[q]["pred"] if max(base[q]["prob"]) >= tt else None for q in paths]
    s = metrics.summarize(y, bp); curves["Baseline (abstain if max prob < t)"].append([s["coverage"], s["selective_accuracy"]])
    hp = []
    for r in rows:
        h = H.RULES[rule](r[2], r[3], r[4], r[5], t)
        if spu.get(r[0]) is None and r[3] < tt: h = None
        hp.append(h)
    s = metrics.summarize([r[1] for r in rows], hp); curves["Hybrid (abstain if Spark reads disagree and baseline p < t)"].append([s["coverage"], s["selective_accuracy"]])
u_zs, u_fs = usage_stats(zs), usage_stats(fs)
cost = lambda u: (u["prompt_tokens_mean"] * PRICE_IN + u["completion_tokens_mean"] * PRICE_OUT)
usage = {"zero_shot": {**u_zs, "usd_per_call": cost(u_zs)}, "fewshot": {**u_fs, "usd_per_call": cost(u_fs)}}
json.dump({"config": CFG, "methods": methods, "confusion": conf, "curves": curves, "usage": usage}, open("results/final_test.json", "w"), indent=1)
L = ["| Method (test, n=340) | Macro-F1 | Accuracy | Coverage | Acc. on answered | Off by 2+ levels | Under-called by 2+ |", "|---|---|---|---|---|---|---|"]
for n, s in methods.items():
    L.append(f"| {n} | {s['macro_f1_all']:.3f} | {s['accuracy_all']:.3f} | {s['coverage']:.2f} | {s['selective_accuracy']:.3f} | {s['off_by_2plus']} | {s['under_by_2plus']} |")
open("results/test_table.md", "w").write("\n".join(L) + "\n")
print("\n".join(L)); print(json.dumps(usage, indent=1))

# ablation on val (where choices were made)
V = json.load(open("results/metrics.json")); hv = json.load(open("results/hybrid_fewshot_val.json"))
steps = [("Baseline: CLIP ViT-B/16 linear probe", V["baseline_clip_official_val"]),
         ("Spark zero-shot (own level wording)", V["spark_zero_shot_val:first"]),
         ("+ structured prompt, official level definitions", V["spark_structured_val:first"]),
         ("+ self-consistency x3 (structured)", V["spark_structured_val:majority"]),
         ("Spark few-shot (structured + 5 reference crops)", V["spark_fewshot_val:first"]),
         ("+ self-consistency x3 (few-shot)", V["spark_fewshot_val:majority"]),
         ("Hybrid: Spark decides when baseline p < 0.70", hv[CFG["hybrid_rule"]])]
A = ["| Step (val, n=335) | Macro-F1 | Coverage | Acc. on answered | Off by 2+ | Under-called by 2+ |", "|---|---|---|---|---|---|"]
for n, s_ in steps:
    A.append(f"| {n} | {s_['macro_f1_all']:.3f} | {s_['coverage']:.2f} | {s_['selective_accuracy']:.3f} | {s_['off_by_2plus']} | {s_['under_by_2plus']} |")
open("results/ablation_val.md", "w").write("\n".join(A) + "\n"); print("\n".join(A))
