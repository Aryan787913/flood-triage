"""Parse model replies of the form 'LEVEL=2; CONFIDENCE=high; PART=tyre top; EVIDENCE=...'."""
import re

_FIELD = re.compile(r"(LEVEL|CONFIDENCE|PART|EVIDENCE)\s*[=:]\s*([^;\n]*)", re.I)


def parse_reply(text):
    """Return dict(level=int|None, abstain=bool, confidence, part, evidence, ok=bool).

    level None + abstain True  -> model said X (can't tell)
    level None + abstain False -> unparseable / empty reply
    The last line starting with LEVEL= is the answer line.
    """
    out = {"level": None, "abstain": False, "confidence": None, "part": None, "evidence": None, "ok": False}
    if not text:
        return out
    # The answer line is the last line that STARTS with LEVEL= (ignores 'LEVEL=4' mentioned mid-sentence in notes).
    lines = [l for l in text.splitlines() if re.match(r"^\W*LEVEL\s*[=:]", l.strip(), re.I)]
    src = lines[-1] if lines else text
    fields = {}
    for k, v in _FIELD.findall(src):
        fields[k.upper()] = v.strip().strip("*`").strip()
    lv = fields.get("LEVEL")
    if lv is None:
        return out
    m = re.match(r"^\s*([0-4]|X)\b", lv, re.I)
    if not m:
        return out
    tok = m.group(1).upper()
    out["ok"] = True
    if tok == "X":
        out["abstain"] = True
    else:
        out["level"] = int(tok)
    conf = (fields.get("CONFIDENCE") or "").lower()
    out["confidence"] = next((c for c in ("high", "medium", "low") if c in conf), None)
    out["part"] = fields.get("PART") or None
    out["evidence"] = fields.get("EVIDENCE") or None
    return out
