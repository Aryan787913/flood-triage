"""Triage agent: assess each citizen report photo with Muse Spark Open, cross-check the citizen's own depth
estimate, flag likely duplicates, rank worst-first, and draft a note for the ward officer.

Nothing here produces centimetre depths, safe routes or official warnings: levels are relative to vehicle parts.
"""
import hashlib, io, math
from collections import Counter
from dataclasses import dataclass, field, asdict
from typing import Optional
from PIL import Image
from . import client, prompts, parse

# Citizen self-estimates as offered on civic portals, mapped to the vehicle levels they are roughly consistent with.
# Heuristic only (a typical car tyre is roughly knee height); used to flag clear mismatches, never to state depth.
SELF_REPORT_LEVELS = {
    "ankle": {0, 1},
    "below knee": {1, 2},
    "knee": {2, 3},
    "waist": {3, 4},
    "above waist": {4},
}


@dataclass
class Assessment:
    level: Optional[int]          # None = can't tell
    votes: list
    confidence: Optional[str]
    part: Optional[str]
    evidence: Optional[str]
    reason: Optional[str] = None  # why can't tell
    raw: list = field(default_factory=list)


def _fewshot_call(image_bytes, prompt):
    from . import fewshot, data
    import os
    content = [{"type": "text", "text": prompts.FEWSHOT_INTRO}]
    for p in fewshot.pick_examples():
        content += [{"type": "text", "text": f"Example: level {p.split('Level')[1][0]}"},
                    client.image_part(os.path.join(data.DATA_ROOT, p))]
    content += [{"type": "text", "text": "Now the photo to classify:"}, client.image_part(image_bytes),
                {"type": "text", "text": prompt}]
    return client.chat([{"role": "user", "content": content}])


def assess(image_bytes, samples=3, prompt=prompts.STRUCTURED, max_workers=3, fewshot=True):
    """Few-shot (5 reference crops) + self-consistency: `samples` independent reads; majority answer, else can't tell."""
    import concurrent.futures as cf
    call = (lambda _: _fewshot_call(image_bytes, prompt)) if fewshot else (lambda _: client.classify(image_bytes, prompt))
    with cf.ThreadPoolExecutor(max_workers) as ex:
        outs = list(ex.map(call, range(samples)))
    parsed = [parse.parse_reply(o["content"]) for o in outs]
    votes = [p["level"] if p["ok"] else None for p in parsed]
    c = Counter(v for v in votes if v is not None)
    level = None; reason = None
    n_abstain = sum(1 for v in votes if v is None)
    top, n = c.most_common(1)[0] if c else (None, 0)
    if n > samples / 2:
        level = top
    elif n_abstain > samples / 2:
        reason = next((p["evidence"] for p in parsed if p["abstain"] and p["evidence"]), "vehicle or waterline not visible")
    else:
        reason = "readings disagree (" + ", ".join("X" if v is None else str(v) for v in votes) + ")"
    best = next((p for p in parsed if p["level"] == level and level is not None), None) or next((p for p in parsed if p["ok"]), {})
    return Assessment(level=level, votes=votes, confidence=best.get("confidence"), part=best.get("part"),
                      evidence=best.get("evidence"), reason=reason, raw=[o["content"] for o in outs])


def self_report_check(self_report, level):
    if level is None or not self_report:
        return "unverified"
    ok = SELF_REPORT_LEVELS.get(self_report.lower())
    if ok is None:
        return "unverified"
    if level in ok:
        return "consistent"
    return "photo shows deeper water" if level > max(ok) else "photo shows shallower water"


def ahash(image_bytes, size=8):
    im = Image.open(io.BytesIO(image_bytes)).convert("L").resize((size, size))
    px = list(im.getdata()); m = sum(px) / len(px)
    return int("".join("1" if p > m else "0" for p in px), 2)


def haversine_m(a, b):
    R = 6371000; la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def find_duplicates(reports, radius_m=150, max_minutes=120, hash_bits=10):
    """Pairs of reports close in space and time, or near-identical images. Returns {id: duplicate_of_id}."""
    dup = {}
    for i, a in enumerate(reports):
        for b in reports[:i]:
            if b["id"] in dup: continue
            same_img = bin(a["hash"] ^ b["hash"]).count("1") <= hash_bits
            near = a.get("latlon") and b.get("latlon") and haversine_m(a["latlon"], b["latlon"]) <= radius_m \
                and abs(a.get("minute", 0) - b.get("minute", 0)) <= max_minutes
            if same_img or near:
                dup[a["id"]] = b["id"]; break
    return dup


def rank(reports):
    """Worst first; can't-tell reports go right after level-3+ so a human looks at them early."""
    def key(r):
        lv = r["assessment"].level
        return (-(lv if lv is not None else 2.5), r.get("minute", 0))
    return sorted(reports, key=key)


def ward_note(reports, ward="Ward (demo)"):
    lines = []
    for r in reports:
        a = r["assessment"]
        lv = "can't tell" if a.level is None else f"L{a.level} {prompts.LEVEL_NAMES[a.level]}"
        lines.append(f"- {r['id']} @ {r.get('place','?')}: {lv}; evidence: {a.evidence or a.reason}; "
                     f"citizen said '{r.get('self_report','-')}' -> {r.get('check','-')}"
                     + (f"; likely duplicate of {r['dup_of']}" if r.get("dup_of") else ""))
    msg = ("You draft short operational notes for a municipal ward officer during urban flooding. Use only the "
           "reports below. Levels are relative to vehicle parts (L0 not flooded ... L4 window or above), NOT depths in cm. "
           "Do not invent locations, depths, routes, casualties or instructions to the public. Write at most 120 words: "
           "which locations to inspect first and why, which reports need a human look (can't tell, mismatches), "
           "and which look like duplicates. Plain text, no markdown headings.\n\nReports (worst first):\n" + "\n".join(lines))
    out = client.chat([{"role": "user", "content": msg}], max_tokens=4000)
    return out["content"], lines
