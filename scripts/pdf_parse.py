"""Parse sungandang restoration PDFs. Missing numbers stay missing."""
import re

from answers import normalize_choice
from inventory import NUM_RANGE

Q_RE = re.compile(r"(?m)^(\d{1,2})\.\s+")
ANS_RE = re.compile(r"정답\s*:?\s*([1-4①-④])")


def parse_restored_text(text):
    lo, hi = NUM_RANGE
    matches = list(Q_RE.finditer(text or ""))
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
