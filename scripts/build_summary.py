#!/usr/bin/env python3
"""Build a 100-item frequency summary from recovered round OCR stems."""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from frequency import normalize_stem, top_n, importance
from inventory import load_inventory
from ocr_frames import parse_num

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VAULT = "/var/minis/mounts/minis1/obsidian-vault/지식/실내건축기능사"
OCR_DIR = os.path.join(ROOT, "raw/youtube/ocr")
NOTE_DIR = os.path.join(ROOT, "out/notes")
META_DIR = os.path.join(ROOT, "metadata")
REVIEW_DIR = os.path.join(ROOT, "out")

# Image review found OCR/frame-assignment clusters that are not one type.
# Each list is a deliberately reviewed same-type group within the old rank.
SUMMARY_SPLIT_GROUPS = {
    4: [["2024-3회#34"], ["2024-3회#36"], ["2017-1회#22"]],
    5: [["2021-1회#12", "2024-3회#16"], ["2024-3회#14"]],
    18: [["2021-3회#18"], ["2024-3회#29"]],
    22: [["2022-3회#37"], ["2024-1회#26"]],
    34: [["2019-1회#7"], ["2021-3회#5"]],
    41: [["2021-3회#41"], ["2022-1회#1"]],
    47: [["2024-1회#15"], ["2024-1회#18"]],
    50: [["2024-3회#4"], ["2024-3회#41"]],
    52: [["2025-1회#1"], ["2025-1회#17"]],
    54: [["2022-1회#59"], ["2022-3회#6"], ["2022-3회#56"]],
    55: [["2022-3회#23"], ["2022-3회#25", "2022-3회#29"]],
}


def load_image_review_index():
    paths = [
        os.path.join(META_DIR, "summary_image_review.json"),
        os.path.join(REVIEW_DIR, "image_review_index.json"),
    ]
    for path in paths:
        if not os.path.isfile(path):
            continue
        try:
            return json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError):
            continue
    return {}


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


def format_frequency_line(cluster):
    members = cluster.get('members') or []
    years = {m.get('year') for m in members if m.get('year')}
    score = cluster.get('score', 0)
    score_text = str(int(score)) if float(score).is_integer() else str(score)
    return f"> **출제빈도**: {len(members)}회 / {len(years)}개년 / 점수 {score_text}"


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


def split_reviewed_clusters(ranked):
    result = []
    for old_rank, cluster in enumerate(ranked, 1):
        groups = SUMMARY_SPLIT_GROUPS.get(old_rank)
        if not groups:
            result.append(cluster)
            continue
        member_map = {f"{m['round']}#{m['num']}": m for m in cluster['members']}
        used = set()
        for group in groups:
            members = [member_map[x] for x in group if x in member_map]
            if not members:
                continue
            used.update(f"{m['round']}#{m['num']}" for m in members)
            years = [m['year'] for m in members]
            result.append({
                'stem': members[0].get('stem', ''),
                'members': members,
                'score': importance(years, len(members), latest=any(y >= 2024 for y in years)),
            })
        leftovers = [m for key, m in member_map.items() if key not in used]
        if leftovers:
            years = [m['year'] for m in leftovers]
            result.append({
                'stem': leftovers[0].get('stem', ''),
                'members': leftovers,
                'score': importance(years, len(leftovers), latest=any(y >= 2024 for y in years)),
            })
    result.sort(key=lambda c: c['score'], reverse=True)
    return result


def review_number_match(members, image_review):
    """Only retain members whose image number agrees with their question label."""
    good = set()
    for m in members:
        key = f"{m['round']}#{m['num']}"
        row = image_review.get(key)
        if not row or row.get('displayed_number') in (None, m['num']):
            good.add((str(m['round']), str(m['num'])))
    return good


def review_topic_key(topic):
    """Collapse obvious wording variants while keeping unrelated topics apart."""
    t = (topic or '').replace(' ', '')
    aliases = (
        ('벽돌' in t and ('쌓기' in t or '끝부분' in t), 'brick_masonry'),
        ('방풍' in t or '회전문' in t, 'revolving_door'),
        ('강구조' in t and ('좌굴' in t or '하중집중' in t), 'steel_column_buckling'),
        ('잔향' in t or '음환경' in t, 'room_acoustics'),
        ('석재' in t and '내화' in t, 'stone_fire_resistance'),
        ('투시도' in t, 'perspective_drawing'),
        ('치수' in t and '제도' in t, 'dimensioning'),
        ('두께' in t and '기호' in t, 'thickness_symbol'),
        ('혼화재' in t and ('종류' in t or '기능' in t), 'concrete_admixture'),
    )
    for matched, key in aliases:
        if matched:
            return key
    return t


def apply_image_review(ranked, image_review):
    """Remove mislabeled images and split clusters with different reviewed topics."""
    result = []
    for cluster in ranked:
        groups = {}
        unknown = []
        for member in cluster['members']:
            key = f"{member['round']}#{member['num']}"
            review = image_review.get(key)
            if review and review.get('displayed_number') not in (None, member['num']):
                continue
            # A mismatched member is discarded; do not let it remain in the
            # original cluster through the no-groups/unknown fallback.
            if key in image_review and review.get('displayed_number') not in (None, member['num']):
                continue
            topic = review.get('topic') if review else None
            if topic:
                groups.setdefault(review_topic_key(topic), []).append(member)
            else:
                # An unreviewed member must not inherit a reviewed cluster's topic.
                unknown.append(member)
        if not groups:
            for member in unknown:
                result.append({
                    'stem': member.get('stem', ''),
                    'members': [member],
                    'score': importance([member['year']], 1, latest=member['year'] >= 2024),
                })
            continue
        for members in groups.values():
            years = [m['year'] for m in members]
            result.append({
                'stem': members[0].get('stem', ''),
                'members': members,
                'score': importance(years, len(members), latest=any(y >= 2024 for y in years)),
            })
        # Unreviewed members are not silently attached to a reviewed topic.
        for member in unknown:
            result.append({
                'stem': member.get('stem', ''),
                'members': [member],
                'score': importance([member['year']], 1, latest=member['year'] >= 2024),
            })
    result.sort(key=lambda c: c['score'], reverse=True)
    return result


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


def render_summary(ranked, answer_index=None, image_review=None):
    answer_index = answer_index or {}
    image_review = image_review or {}
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
        number_matched = review_number_match(members, image_review)
        for m in members:
            note = os.path.join(VAULT, "기출문제", f"{m['round']}.md")
            key = (str(m["round"]), str(m["num"]))
            if os.path.isfile(note) and key in number_matched:
                available_questions.add(key)
        links = format_member_links(members, available_questions)
        if len(members) > 1:
            lines.append("> **같은 유형 출제**: " + ", ".join(links))
        else:
            lines.append("> **단독 출제 확인**: " + ", ".join(links))
        lines.append(format_frequency_line(c))
        lines.append(format_member_answers(members, answer_index))
        lines.append("")
    return "\n".join(lines)


def main():
    data = load_inventory()
    items = []
    for rnd in data["rounds"]:
        items.extend(stems_from_round(rnd))
    ranked = top_n(items, limit=len(items))
    image_review = load_image_review_index()
    # Image-reviewed topic groups are the final authority; do not re-merge them.
    ranked = apply_image_review(ranked, image_review)
    ranked.sort(key=lambda c: c['score'], reverse=True)
    md = render_summary(ranked[:100], load_answer_index(), image_review)
    out = os.path.join(ROOT, "out/notes", "기출핵심요약.md")
    vault = os.path.join(VAULT, "기출핵심요약", "실내건축기능사.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    os.makedirs(os.path.dirname(vault), exist_ok=True)
    open(out, "w", encoding="utf-8").write(md)
    open(vault, "w", encoding="utf-8").write(md)
    print("items", len(items), "clusters", len(ranked), "wrote", vault)


if __name__ == "__main__":
    main()
