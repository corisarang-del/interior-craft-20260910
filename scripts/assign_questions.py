"""Assign frames to question numbers 1-60."""
from difflib import SequenceMatcher


def _best_monotonic(seq, decreasing=False):
    """Longest monotonic subsequence on numbers; seq is time-sorted."""
    if not seq:
        return []
    n = len(seq)
    lengths = [1] * n
    prev = [-1] * n
    for i in range(n):
        for j in range(i):
            ok = seq[j][1] > seq[i][1] if decreasing else seq[j][1] < seq[i][1]
            if ok and lengths[j] + 1 > lengths[i]:
                lengths[i] = lengths[j] + 1
                prev[i] = j
    k = max(range(n), key=lambda i: (lengths[i], -i if decreasing else i))
    out = []
    while k >= 0:
        out.append(seq[k])
        k = prev[k]
    out.reverse()
    return out


def detect_first_starts(badges, num_range=(1, 60), neighbor_slack=180):
    """First occurrence per number; drop timestamps far from both neighbors."""
    lo, hi = num_range
    first = {}
    for ts, n in sorted(badges):
        if lo <= n <= hi and n not in first:
            first[n] = ts
    kept = {}
    all_ts = list(first.values())
    for n, ts in first.items():
        neighbors = [first[k] for k in (n - 1, n + 1) if k in first]
        ref = neighbors or [x for x in all_ts if x != ts]
        if ref and min(abs(ts - x) for x in ref) > neighbor_slack:
            continue
        kept[n] = ts
    return sorted((ts, n) for n, ts in kept.items())


def detect_starts(badges, num_range=(1, 60), reverse=False):
    """badges: list of (ts, num). Keep in-range, then longest monotonic path."""
    lo, hi = num_range
    filtered = [(ts, n) for ts, n in badges if lo <= n <= hi]
    if reverse:
        latest = {}
        for ts, n in sorted(filtered):
            latest[n] = ts
        seq = sorted((ts, n) for n, ts in latest.items())
        return _best_monotonic(seq, decreasing=True)
    first = {}
    for ts, n in sorted(filtered):
        if n not in first:
            first[n] = ts
    seq = sorted((ts, n) for n, ts in first.items())
    starts = _best_monotonic(seq, decreasing=False)
    taken = {n for _, n in starts}
    for n, ts in first.items():
        if n in taken:
            continue
        prevs = [(pts, pn) for pts, pn in starts if pn < n]
        nexts = [(pts, pn) for pts, pn in starts if pn > n]
        if not prevs or not nexts:
            continue
        prev_ts, prev_n = max(prevs, key=lambda x: x[1])
        next_ts, next_n = min(nexts, key=lambda x: x[1])
        if (
            n == prev_n + 1
            and next_n - n <= 2
            and ts >= prev_ts
            and min(abs(ts - prev_ts), abs(ts - next_ts)) <= 90
        ):
            starts.append((ts, n))
            taken.add(n)
    starts.sort(key=lambda x: x[0])
    return starts


def assign_questions(groups, starts, margin=90):
    """Map start numbers to nearest group within margin seconds."""
    result = {}
    for ts, num in starts:
        best = None
        best_dt = None
        for g in groups:
            dt = g["ts"] - ts
            if dt < -margin:
                continue
            adt = abs(dt)
            if best is None or adt < best_dt:
                best = g
                best_dt = adt
        if best is None:
            continue
        result[str(num)] = {
            "ts": best["ts"],
            "file": best["file"],
            "text": best.get("text", ""),
            "image_confirmed": True,
        }
    return result


def mark_duplicate_stems(questions, threshold=0.95):
    seen = []
    for k in sorted(questions, key=lambda x: int(x)):
        q = questions[k]
        stem = (q.get("text") or "").strip()
        file = q.get("file")
        dup = False
        for prev in seen:
            if file and file == prev.get("file"):
                dup = True
                break
            if stem and SequenceMatcher(None, stem, prev.get("text") or "").ratio() >= threshold:
                dup = True
                break
        if dup:
            q["image_confirmed"] = False
        else:
            seen.append(q)
    return questions
