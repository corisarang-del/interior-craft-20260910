#!/usr/bin/env python3
"""Build a 100-item frequency summary from recovered round OCR stems."""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from frequency import normalize_stem, top_n
from inventory import load_inventory
from ocr_frames import parse_num

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VAULT = "/var/minis/mounts/minis1/obsidian-vault/지식/실내건축기능사"
OCR_DIR = os.path.join(ROOT, "raw/youtube/ocr")
NOTE_DIR = os.path.join(ROOT, "out/notes")
META_DIR = os.path.join(ROOT, "metadata")


def load_answer_index():
    """Load per-round answer/status metadata keyed by (round, question number)."""
    index = {}
    if not os.path.isdir(META_DIR):
        return index
    for name in os.listdir(META_DIR):
        if not (name.startswith("answers_") and name.endswith(".json")):
            continue
        path = os.path.join(META_DIR, name)
        try:
            data = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        rid = data.get("round") or name[len("answers_"):-len(".json")]
        for num, info in (data.get("answers") or {}).items():
            if isinstance(info, dict):
                index[(str(rid), str(num))] = info
    return index


def format_member_answers(members, answer_index):
    values = []
    for member in members:
        rid = str(member["round"])
        num = str(member["num"])
        info = answer_index.get((rid, num), {})
        answer = info.get("answer")
        status = info.get("status")
        if not answer or status == "미확정":
            value = "미확정"
        else:
            value = str(answer)
            if status == "추론":
                value += " (추론)"
        values.append(f"{rid} {num}번 {value}")
    return "> **정답**: " + "; ".join(values)


def format_member_links(members, available_questions=None):
    """Create vault-scoped links so same-named electrician notes cannot resolve."""
    available_questions = available_questions or set()
    links = []
    for member in members:
        rid = str(member["round"])
        num = str(member["num"])
        if (rid, num) in available_questions:
            links.append(
                f"[[지식/실내건축기능사/기출문제/{rid}#{num}|{rid} {num}번]]"
            )
        else:
            links.append(f"{rid} {num}번")
    return links


def round_year(rid):
    return int(rid.split("-")[0])


def stems_from_round(rnd):
    items = []
    if rnd["source"] != "youtube":
        return items
    year = rnd["year"]
    rid = rnd["id"]
    seen = {}
    for vid in rnd["video_ids"]:
        path = os.path.join(OCR_DIR, f"{vid}.json")
        if not os.path.isfile(path):
            continue
        rows = json.load(open(path, encoding="utf-8"))
        for r in rows:
            n = r.get("num") or parse_num(r.get("text") or "")
            if not n:
                continue
            stem = normalize_stem(r.get("text") or "")
            if len(stem) < 8:
                continue
            key = str(n)
            if key not in seen or len(stem) > len(seen[key]):
                seen[key] = stem
    note = os.path.join(NOTE_DIR, f"{rid}.md")
    present = set()
    if os.path.isfile(note):
        present = {m.group(1) for m in re.finditer(r"^### (\d+)\.", open(note, encoding="utf-8").read(), re.M)}
    for num, stem in seen.items():
        if present and num not in present:
            continue
        items.append(
            {
                "id": f"{rid}#{num}",
                "stem": stem,
                "year": year,
                "round": rid,
                "num": int(num),
            }
        )
    return items


def render_summary(ranked, answer_index=None):
    answer_index = answer_index or {}
    lines = [
        "---",
        "날짜: 2026-09-11",
        "태그: [실내건축기능사, 기출핵심요약]",
        "분야: 실내건축기능사",
        "---",
        "# 실내건축기능사 필기 기출핵심요약 100",
        "",
        "OCR 지문 클러스터 + 최신 회차 1.5배 가중. 대표는 이미지(있을 때).",
        "같은 유형 링크는 원본 회차 노트가 있는 것만.",
        "",
    ]
    for i, c in enumerate(ranked, 1):
        members = sorted(c["members"], key=lambda m: (m["year"], m["round"], m["num"]))
        years = sorted({m["year"] for m in members})
        lines.append(f"## {i}. {' / '.join(str(y) for y in years)} 출제")
        lines.append("")
        rep = max(members, key=lambda m: (m["year"], len(m.get("stem") or "")))
        img = os.path.join(VAULT, "기출문제", "이미지", rep["round"], f"q{rep['num']:02d}.jpg")
        if os.path.isfile(img):
            lines.append(f"![](../기출문제/이미지/{rep['round']}/q{rep['num']:02d}.jpg)")
            lines.append("")
        else:
            lines.append(f"- 대표: {rep['round']} {rep['num']}번 (이미지 없음)")
            lines.append("")
        available_questions = set()
        for m in members:
            note = os.path.join(VAULT, "기출문제", f"{m['round']}.md")
            if os.path.isfile(note):
                available_questions.add((str(m["round"]), str(m["num"])))
        links = format_member_links(members, available_questions)
        lines.append("> **같은 유형 출제**: " + ", ".join(links))
        lines.append(format_member_answers(members, answer_index))
        lines.append("")
    return "\n".join(lines)


def main():
    data = load_inventory()
    items = []
    for rnd in data["rounds"]:
        items.extend(stems_from_round(rnd))
    ranked = top_n(items, limit=100)
    md = render_summary(ranked, load_answer_index())
    out = os.path.join(ROOT, "out/notes", "기출핵심요약.md")
    vault = os.path.join(VAULT, "기출핵심요약", "실내건축기능사.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    os.makedirs(os.path.dirname(vault), exist_ok=True)
    open(out, "w", encoding="utf-8").write(md)
    open(vault, "w", encoding="utf-8").write(md)
    print("items", len(items), "clusters", len(ranked), "wrote", vault)


if __name__ == "__main__":
    main()
