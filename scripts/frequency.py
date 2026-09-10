"""Frequency clustering for a 100-question summary."""
import re
from difflib import SequenceMatcher


def normalize_stem(text):
    return re.sub(r"[^가-힣0-9]", "", text or "")


def importance(years, count, keywords=0, latest=False):
    score = len(set(years)) * 3 + count + keywords * 2
    if latest:
        score *= 1.5
    return score


def _similar(a, b, threshold):
    if not a or not b:
        return False
    return SequenceMatcher(None, a, b).ratio() > threshold


def cluster_items(items, threshold=0.6):
    clusters = []
    for item in items:
        stem = item.get("stem") or normalize_stem(item.get("text", ""))
        placed = False
        for c in clusters:
            if stem == c["stem"] or _similar(stem, c["stem"], threshold):
                c["members"].append(item)
                placed = True
                break
        if not placed:
            clusters.append({"stem": stem, "members": [item]})
    return clusters


def top_n(items, limit=100):
    clusters = cluster_items(items)
    ranked = []
    for c in clusters:
        years = [m.get("year") for m in c["members"] if m.get("year")]
        latest = any((y or 0) >= 2024 for y in years)
        score = importance(years, len(c["members"]), latest=latest)
        ranked.append({"stem": c["stem"], "score": score, "members": c["members"]})
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked[:limit]
