"""Render Obsidian round notes. Images use relative markdown only."""
import hashlib
import os
from collections import defaultdict

from inventory import digit_keys, question_image_md


def render_round_note(round_id, questions, source="youtube", zettel_id=None):
    if source == "none" or not questions:
        return None
    keys = digit_keys(questions)
    lines = [
        "---",
        "날짜: 2026-09-10",
        "태그: [실내건축기능사, 기출문제, 복원]",
        "분야: 실내건축기능사",
        f"회차: {round_id}",
    ]
    if zettel_id:
        lines.append(f"zettel_id: {zettel_id}")
    lines.extend(
        [
            "---",
            f"# 실내건축기능사 필기 {round_id} 기출 (복원)",
            "",
            "## 개요",
            f"- **회차**: {round_id}",
            f"- **출처**: {source}",
            "",
        ]
    )
    for k in keys:
        q = questions[k]
        n = int(k)
        lines.append(f"### {n}.")
        lines.append("")
        if q.get("image_confirmed") and q.get("file"):
            lines.append(question_image_md(round_id, n))
            lines.append("")
        if q.get("kind") == "book_map":
            bits = []
            if q.get("page"):
                bits.append(f"교재 {q['page']}쪽")
            if q.get("book_num"):
                bits.append(f"{q['book_num']}번")
            topic = q.get("topic") or ""
            extra = f" ({', '.join(bits)})" if bits else ""
            lines.append(f"- {topic}{extra}")
            lines.append("")
        elif q.get("kind") == "new" and q.get("text"):
            lines.append(q["text"].strip())
            lines.append("")
        ans = q.get("answer")
        if ans:
            lines.append(f"**정답: {ans}**")
        else:
            lines.append("**정답: 미확정**")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def image_md5_duplicates(paths):
    groups = defaultdict(list)
    for p in paths:
        h = hashlib.md5()
        with open(p, "rb") as f:
            h.update(f.read())
        groups[h.hexdigest()].append(p)
    return {k: v for k, v in groups.items() if len(v) > 1}
