import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flood_triage.parse import parse_reply
from flood_triage.metrics import summarize, macro_f1


def test_simple():
    r = parse_reply("LEVEL=2; EVIDENCE=water at tyre top")
    assert r["level"] == 2 and r["evidence"] == "water at tyre top" and r["ok"]

def test_abstain():
    r = parse_reply("LEVEL=X; CONFIDENCE=low; PART=none; EVIDENCE=too blurry")
    assert r["abstain"] and r["level"] is None and r["confidence"] == "low"

def test_ignores_mid_sentence_level():
    r = parse_reply("LEVEL=0; EVIDENCE=wet ground\n\nNote: mud line suggests prior peak LEVEL=4 at window.")
    assert r["level"] == 0

def test_last_answer_line_and_markdown():
    r = parse_reply("Step 1 ...\nLEVEL=1; draft\n**LEVEL=3; CONFIDENCE=High; PART=door; EVIDENCE=door bottom under water**")
    assert r["level"] == 3 and r["confidence"] == "high" and r["part"] == "door"

def test_empty_and_garbage():
    assert not parse_reply("")["ok"] and not parse_reply("I think level two")["ok"]
    assert not parse_reply("LEVEL=7")["ok"]

def test_metrics():
    y = [0, 1, 2, 3, 4, 4]
    p = [0, 1, 2, None, 2, 4]
    s = summarize(y, p)
    assert s["coverage"] == 5 / 6 and s["selective_accuracy"] == 4 / 5
    assert s["off_by_2plus"] == 1 and s["under_by_2plus"] == 1
    assert abs(macro_f1([0, 1], [0, 1], labels=[0, 1]) - 1.0) < 1e-9


def test_assess_vote_logic(monkeypatch):
    from flood_triage import agent
    replies = iter(["LEVEL=3; EVIDENCE=door", "LEVEL=X; EVIDENCE=blur", "LEVEL=3; EVIDENCE=door sill"])
    monkeypatch.setattr(agent, "_fewshot_call", lambda b, p: {"content": next(replies)})
    a = agent.assess(b"x", max_workers=1)
    assert a.level == 3 and a.reason is None
    replies2 = iter(["LEVEL=X; EVIDENCE=too dark", "LEVEL=X; EVIDENCE=too dark", "LEVEL=1; EVIDENCE=tyre"])
    monkeypatch.setattr(agent, "_fewshot_call", lambda b, p: {"content": next(replies2)})
    a = agent.assess(b"x", max_workers=1)
    assert a.level is None and a.reason == "too dark"
