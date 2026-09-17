"""Frequency clustering and deterministic ranking for the 100-question summary."""
import re
from difflib import SequenceMatcher


def normalize_stem(text):
    return re.sub(r"[^가-힣0-9]", "", text or "")


def importance(years, count, keywords=0, latest=False):
    """Legacy-compatible frequency score; recency is never multiplied in."""
    return len(set(years)) * 3 + count + keywords * 2


def cluster_score_components(cluster, latest_years=(2024, 2025)):
    """Return frequency and recency independently, without multiplying them."""
    members = cluster.get("members") or []
    years = sorted({m.get("year") for m in members if m.get("year")})
    recent = sorted(y for y in years if y in set(latest_years))
    return {
        "frequency_score": len(years) * 3 + len(members),
        "repeat_count": len(members),
        "unique_years": len(years),
        "years": years,
        "latest_years": recent,
        "latest_score": len(recent),
    }


def _stable_key(cluster):
    ids = [
        f"{m.get('round', '')}#{int(m.get('num', 0)):02d}"
        for m in cluster.get("members", [])
    ]
    return min(ids) if ids else ""


def rank_clusters(clusters):
    """Rank repeated types before singletons with deterministic tie-breaking."""
    ranked = []
    for cluster in clusters:
        scores = cluster_score_components(cluster)
        category = "반복 출제 핵심 유형" if scores["repeat_count"] > 1 else "단독 출제 참고"
        ranked.append({
            **cluster,
            **scores,
            "score": scores["frequency_score"],
            "category": category,
            "stable_key": _stable_key(cluster),
        })
    ranked.sort(
        key=lambda x: (
            0 if x["category"] == "반복 출제 핵심 유형" else 1,
            -x["frequency_score"],
            -x["unique_years"],
            -x["repeat_count"],
            x["stable_key"],
        )
    )
    return ranked


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
    """Return deterministically ranked clusters under the new policy."""
    return rank_clusters(cluster_items(items))[:limit]
