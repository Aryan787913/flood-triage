"""Metrics for 5-level flood classification with abstention (pred None = can't tell)."""
from collections import Counter


def macro_f1(y, p, labels=range(5)):
    """Macro-F1 over labels; abstentions count as wrong (they are never a true positive)."""
    f1s = []
    for c in labels:
        tp = sum(1 for a, b in zip(y, p) if a == c and b == c)
        fp = sum(1 for a, b in zip(y, p) if a != c and b == c)
        fn = sum(1 for a, b in zip(y, p) if a == c and b != c)
        f1s.append(0.0 if tp == 0 else 2 * tp / (2 * tp + fp + fn))
    return sum(f1s) / len(f1s)


def summarize(y, p):
    """y: true levels; p: predicted levels or None (abstain / unparsed)."""
    y = [int(a) for a in y]; p = [None if b is None else int(b) for b in p]
    n = len(y)
    ans = [(a, b) for a, b in zip(y, p) if b is not None]
    k = len(ans)
    correct = sum(a == b for a, b in ans)
    return {
        "n": n,
        "coverage": k / n if n else 0.0,
        "accuracy_all": correct / n if n else 0.0,          # abstain = wrong
        "selective_accuracy": correct / k if k else 0.0,     # accuracy on answered
        "macro_f1_all": macro_f1(y, p),
        "macro_f1_answered": macro_f1([a for a, _ in ans], [b for _, b in ans]) if k else 0.0,
        "off_by_2plus": sum(abs(a - b) >= 2 for a, b in ans),
        "off_by_2plus_rate": (sum(abs(a - b) >= 2 for a, b in ans) / k) if k else 0.0,
        "mae_levels": (sum(abs(a - b) for a, b in ans) / k) if k else 0.0,
        "under_by_2plus": sum(b - a <= -2 for a, b in ans),  # dangerous: deep water called shallow
    }


def confusion(y, p, labels=range(5)):
    cols = list(labels) + [None]
    c = Counter(zip(y, p))
    return [[c[(a, b)] for b in cols] for a in labels]
