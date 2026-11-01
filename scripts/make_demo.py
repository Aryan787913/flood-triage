"""Build demo/demo_reports.json: test-split photos + SYNTHETIC locations/times/citizen estimates, assessed live by Spark."""
import json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flood_triage import agent, overlay, data, prompts, fewshot

PROMPT = os.environ.get("DEMO_PROMPT", "structured")
random.seed(11)
test = data.read_split("test")
by = {}
for p, y in test: by.setdefault(y, []).append(p)
# two per level, plus a same-source pair (duplicate) at level 3
pick = [p for y in range(5) for p in random.sample(by[y], 2)]
srcs = {}
for p, y in test:
    if y == 3: srcs.setdefault(data.source_id(p), []).append(p)
pair = next(v[:2] for v in srcs.values() if len(v) >= 2)
pick += pair
self_rep = ["ankle", "ankle", "ankle", "knee", "below knee", "knee", "knee", "waist", "waist", "above waist", "waist", "knee"]
base = (28.4595, 77.0266)
reports = []
for i, p in enumerate(pick):
    b = open(os.path.join(data.DATA_ROOT, p), "rb").read()
    a = agent.assess(b)
    loc = overlay.locate(b) if a.level is not None else {}
    lat, lon = base[0] + random.uniform(-0.03, 0.03), base[1] + random.uniform(-0.04, 0.04)
    if i == len(pick) - 1:  # duplicate: same spot as previous report, 20 min later
        lat, lon = reports[-1]["lat"] + 0.0004, reports[-1]["lon"] + 0.0003
    r = {"id": f"R{i+1:02d}", "path": p, "true_level": int(p.split("Level")[1][0]), "place": f"Demo point {chr(65+i)}",
         "lat": lat, "lon": lon, "minute": 18 * 60 + random.randint(0, 90) if i < len(pick) - 1 else reports[-1]["minute"] + 20,
         "self_report": self_rep[i], "level": a.level, "votes": a.votes, "confidence": a.confidence, "part": a.part,
         "evidence": a.evidence, "reason": a.reason, "loc": {k: loc.get(k) for k in ("box", "waterline")}, "hash": agent.ahash(b)}
    r["check"] = agent.self_report_check(r["self_report"], r["level"])
    reports.append(r); print(r["id"], r["true_level"], r["level"], r["votes"], r["check"], flush=True)
dups = agent.find_duplicates([{"id": r["id"], "hash": r["hash"], "latlon": (r["lat"], r["lon"]), "minute": r["minute"]} for r in reports])
for r in reports: r["dup_of"] = dups.get(r["id"])
os.makedirs("demo", exist_ok=True)
json.dump({"ward": "Demo ward (synthetic)", "note": "Locations, times and citizen estimates are SYNTHETIC. Photos: STURM-FloodDepth test split (CC BY 4.0).",
           "prompt": PROMPT, "reports": reports}, open("demo/demo_reports.json", "w"), indent=1)
print("dups", dups)
