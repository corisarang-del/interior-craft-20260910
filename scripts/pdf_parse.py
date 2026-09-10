"""Parse sungandang restoration PDFs. Missing numbers stay missing."""
import re

from answers import normalize_choice
from inventory import NUM_RANGE

Q_RE = re.compile(r"(?:^|[\n\f])\s*(\d{1,2})\.\s+")
ANS_RE = re.compile(r"정답\s*:?\s*([1-4①-④])")
MAP_FULL_RE = re.compile(r"^\s*(\d{1,2})\s+(\d+)\s+(\d+)\s+(.+?)\s*$")
MAP_NEW_RE = re.compile(r"^\s*(\d{1,2})\s+신규")
MAP_TOPIC_RE = re.compile(r"^\s*(\d{1,2})\s+(.+?)\s*$")
NEW_HEADER = "[신규 출제 문제]"


def parse_restored_text(text):
    lo, hi = NUM_RANGE
    text = (text or "").replace("\x0c", "\n")
    matches = list(Q_RE.finditer(text))
    questions = {}
    for i, m in enumerate(matches):
        num = int(m.group(1))
        if num < lo or num > hi:
            continue
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[start:end].strip()
        ans = None
        am = ANS_RE.search(block)
        if am:
            ans = normalize_choice(am.group(1))
        questions[str(num)] = {
            "text": block,
            "answer": ans,
            "image_confirmed": False,
            "file": None,
        }
    return questions


def parse_catalog_text(text):
    """Book-map rows 1-60 plus full new-only questions after the header."""
    lo, hi = NUM_RANGE
    body = text or ""
    split = body.find(NEW_HEADER)
    map_part = body if split < 0 else body[:split]
    new_part = "" if split < 0 else body[split + len(NEW_HEADER) :]
    mapping = {}
    for raw in map_part.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        m = MAP_FULL_RE.match(line)
        if m:
            n = int(m.group(1))
            if lo <= n <= hi:
                mapping[str(n)] = {
                    "page": m.group(2),
                    "book_num": m.group(3),
                    "topic": m.group(4).strip(),
                    "is_new": False,
                }
            continue
        m = MAP_NEW_RE.match(line)
        if m:
            n = int(m.group(1))
            if lo <= n <= hi:
                rest = line[m.end() :].strip()
                mapping[str(n)] = {
                    "page": None,
                    "book_num": None,
                    "topic": rest or "신규 출제 문제",
                    "is_new": True,
                }
            continue
        m = MAP_TOPIC_RE.match(line)
        if m:
            n = int(m.group(1))
            topic = m.group(2).strip()
            if lo <= n <= hi and n >= 50 and "쪽수" not in topic and "문항" not in topic:
                mapping.setdefault(
                    str(n),
                    {
                        "page": None,
                        "book_num": None,
                        "topic": topic,
                        "is_new": True,
                    },
                )
    new_qs = parse_restored_text(new_part)
    for k, q in new_qs.items():
        q["answer"] = None
        if k in mapping:
            mapping[k]["is_new"] = True
            if not mapping[k].get("topic"):
                mapping[k]["topic"] = q["text"].splitlines()[0]
        else:
            mapping[k] = {
                "page": None,
                "book_num": None,
                "topic": q["text"].splitlines()[0],
                "is_new": True,
            }
    return {"map": mapping, "new": new_qs}
