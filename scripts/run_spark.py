"""Run Muse Spark Open over a split. Resumable: appends to JSONL, skips done items.
usage: python scripts/run_spark.py --split test --prompt zero_shot --out results/raw/spark_zero_shot_test.jsonl
"""
import argparse, json, os, sys, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flood_triage import prompts, client, parse, data

ap = argparse.ArgumentParser()
ap.add_argument("--split", default="test"); ap.add_argument("--prompt", default="zero_shot")
ap.add_argument("--out", required=True); ap.add_argument("--workers", type=int, default=8)
ap.add_argument("--samples", type=int, default=1); ap.add_argument("--temperature", type=float, default=None)
ap.add_argument("--limit", type=int, default=0); ap.add_argument("--splits_dir", default="splits")
a = ap.parse_args()
P = {"zero_shot": prompts.ZERO_SHOT, "structured": prompts.STRUCTURED, "fewshot": prompts.STRUCTURED}[a.prompt]
EX = None
if a.prompt == "fewshot":
    from flood_triage import fewshot
    EX = fewshot.pick_examples(); print("examples:", EX)
items = data.read_split(a.split, a.splits_dir)
if a.limit: items = items[: a.limit]
done = set()
if os.path.exists(a.out):
    for l in open(a.out):
        r = json.loads(l)
        if r.get("content") or r.get("tries", 0) >= 2: done.add((r["path"], r["sample"]))
jobs = [(p, y, s) for p, y in items for s in range(a.samples) if (p, s) not in done]
print(f"{len(jobs)} calls to run", flush=True)

def work(j):
    p, y, s = j
    img = os.path.join(data.DATA_ROOT, p)
    call = (lambda **kw: client.chat(fewshot.build_messages(img, EX, P, prompts.FEWSHOT_INTRO), temperature=a.temperature, **kw)) \
        if EX else (lambda **kw: client.classify(img, P, temperature=a.temperature, **kw))
    r = call()
    if not r["content"]:  # empty content: retry once with a larger budget
        r = call(max_tokens=8000); r["tries"] = 2
    pr = parse.parse_reply(r["content"])
    return {"path": p, "label": y, "sample": s, "prompt": a.prompt, **r, "parsed": pr}

with open(a.out, "a") as f, cf.ThreadPoolExecutor(a.workers) as ex:
    futs = [ex.submit(work, j) for j in jobs]
    for i, fu in enumerate(cf.as_completed(futs)):
        rec = fu.result()
        f.write(json.dumps(rec) + "\n"); f.flush()
        if i % 20 == 0: print(i, rec["label"], rec["parsed"]["level"], rec["latency_s"], flush=True)
print("done")
