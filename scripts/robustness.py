"""Qualitative robustness check on real Indian monsoon street photos (Wikimedia Commons; not in repo).
Images + licences listed in robust/manifest.json (outside the repo). Writes results/robustness.json."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import concurrent.futures as cf
from flood_triage import agent
ROOT = sys.argv[1] if len(sys.argv) > 1 else "../robust"
pick = [int(x) for x in sys.argv[2].split(",")]
man = json.load(open(os.path.join(ROOT, "manifest.json")))
def run(i):
    m = man[i]; b = open(os.path.join(ROOT, m["file"]), "rb").read()
    a = agent.assess(b)
    return {"idx": i, "title": m["title"], "license": m["license"], "artist": m["artist"], "page": m["desc"],
            "level": a.level, "votes": a.votes, "part": a.part, "evidence": a.evidence, "reason": a.reason, "confidence": a.confidence}
with cf.ThreadPoolExecutor(4) as ex: out = list(ex.map(run, pick))
json.dump(out, open("results/robustness.json", "w"), indent=1)
for o in out: print(o["idx"], o["level"], o["votes"], (o["evidence"] or o["reason"] or "")[:90])
