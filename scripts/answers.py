"""Conservative subtitle answer extraction. Prefer fewer correct hits."""
import re

from inventory import ANSWER_CAP

CIRCLED = {1: "①", 2: "②", 3: "③", 4: "④"}
CLEAR_PATTERNS = [
    re.compile(r"정답은\s*([1-4①-④])\s*번이\s*됩니다"),
    re.compile(r"답이\s*([1-4①-④])\s*번"),
    re.compile(r"정답은\s*([1-4①-④])\s*번"),
]


def normalize_choice(raw):
    if raw is None or raw == "":
        return None
    s = str(raw).strip()
    if s in CIRCLED.values():
        return s
    if s.isdigit() and s.isascii() and int(s) in CIRCLED:
        return CIRCLED[int(s)]
    found = re.findall(r"[①②③④]|[1-4]", s)
    uniq = []
    for ch in found:
        mark = CIRCLED[int(ch)] if ch in "1234" else ch
        if mark not in uniq:
            uniq.append(mark)
    if len(uniq) == 1:
        return uniq[0]
    return None


def extract_answers(text):
    hits = []
    for pat in CLEAR_PATTERNS:
        for m in pat.finditer(text or ""):
            hits.append((m.start(), normalize_choice(m.group(1))))
    hits.sort()
    out = []
    last_pos = -999
    last_ans = None
    for pos, ans in hits:
        if ans is None:
            continue
        if pos - last_pos <= 20 and ans == last_ans:
            continue
        out.append(ans)
        last_pos = pos
        last_ans = ans
        if len(out) >= ANSWER_CAP:
            break
    return out
