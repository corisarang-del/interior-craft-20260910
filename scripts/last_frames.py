"""Pick the last (latest-ts) frame per question number."""
import os


def _pack(r, n):
    name = r.get("src_file") or r.get("file")
    d = r.get("frames_dir") or ""
    path = os.path.join(d, name) if d and name else name
    return {
        "num": n,
        "ts": r.get("ts") or 0,
        "file": name,
        "vid": r.get("vid"),
        "frames_dir": d,
        "path": path,
        "text": r.get("text") or "",
    }


def last_frames_from_rows(rows, windows=None):
    """If windows={n:(lo_ts, hi_ts)}, pick latest frame inside each question span."""
    if windows:
        last = {}
        for n, (lo, hi) in windows.items():
            cands = [r for r in rows if lo <= (r.get("ts") or 0) < hi]
            if not cands:
                continue
            tagged = [r for r in cands if r.get("num") == n]
            pick = tagged[-1] if tagged else cands[-1]
            last[int(n)] = _pack(pick, int(n))
        return last
    last = {}
    for r in rows:
        n = r.get("num")
        if n is None:
            continue
        try:
            n = int(n)
        except (TypeError, ValueError):
            continue
        ts = r.get("ts") or 0
        prev = last.get(n)
        if prev is None or ts >= prev.get("ts", 0):
            last[n] = _pack(r, n)
    return last
