#!/usr/bin/env python3
"""Build a 100-item frequency summary from recovered round OCR stems."""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from frequency import normalize_stem, cluster_items, importance, annotate_singletons, rank_clusters, rank_singletons, singleton_score_components
from inventory import load_inventory
from ocr_frames import parse_num

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VAULT = "/var/minis/mounts/minis1/obsidian-vault/지식/실내건축기능사"
OCR_DIR = os.path.join(ROOT, "raw/youtube/ocr")
NOTE_DIR = os.path.join(ROOT, "out/notes")
META_DIR = os.path.join(ROOT, "metadata")
REVIEW_DIR = os.path.join(ROOT, "out")

# Image review is applied to every raw cluster before ranking. No year cap is used.


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


def format_singleton_line(cluster):
    return (
        f"> **단독 출제 참고**: {cluster.get('concept_key', '기타')} / "
        f"단독우선점수 {cluster.get('singleton_score', 0)} / "
        f"관련개념 {cluster.get('related_year_count', 0)}개년·{cluster.get('related_count', 0)}회 / "
        f"핵심성 {cluster.get('core_score', 0)} / 수치·규정성 {cluster.get('numeric_score', 0)} / "
        f"활용성 {cluster.get('utility_score', 0)} / 최신점수 {cluster.get('latest_score', 0)}"
    )


def format_frequency_line(cluster):
    members = cluster.get('members') or []
    years = {m.get('year') for m in members if m.get('year')}
    frequency = cluster.get('frequency_score', cluster.get('score', 0))
    latest = cluster.get('latest_score', 0)
    category = cluster.get('category', '미분류')
    frequency_text = str(int(frequency)) if float(frequency).is_integer() else str(frequency)
    return f"> **출제빈도**: {category} / {len(members)}회 / {len(years)}개년 / 빈도점수 {frequency_text} / 최신점수 {latest}"


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
                'score': len(set(years)) * 3 + len(members),
            })
        # Unreviewed members are not silently attached to a reviewed topic.
        for member in unknown:
            result.append({
                'stem': member.get('stem', ''),
                'members': [member],
                'score': importance([member['year']], 1, latest=member['year'] >= 2024),
            })
    return result


def rank_reviewed_clusters(clusters):
    """Rank by category, actual frequency, year count, then stable ID.

    Recency is displayed separately but deliberately does not alter ranking.
    No per-year cap is applied, per the project requirement.
    """
    ranked = rank_clusters(clusters)
    for cluster in ranked:
        cluster['score'] = cluster['frequency_score']
    return ranked


def reorder_singleton_section(ranked, baseline_ids=None):
    """Keep the original singleton candidates and reorder only their slots.

    The summary composition is intentionally fixed: reviewed repeated types
    plus the singleton candidates already selected in the previous summary.
    This changes order without silently adding arbitrary OCR candidates.
    No year cap is applied.
    """
    if baseline_ids is None:
        path = os.path.join(META_DIR, 'baseline_singleton_ids.json')
        if not os.path.isfile(path):
            return ranked
        try:
            baseline_ids = json.load(open(path, encoding='utf-8'))
        except (OSError, ValueError):
            return ranked
    baseline = set(baseline_ids)

    repeated = [c for c in ranked if c.get('category') == '반복 출제 핵심 유형']
    singleton = []
    for cluster in ranked:
        if cluster.get('category') != '단독 출제 참고':
            continue
        ids = {f"{m['round']}#{m['num']}" for m in cluster.get('members', [])}
        if ids & baseline:
            singleton.append(cluster)
    return repeated + rank_singletons(singleton)


def write_singleton_priority_metadata(ranked, output_path=None):
    """Persist the selected singleton rankings for audit/reproduction."""
    rows = []
    for rank, cluster in enumerate(
        [c for c in ranked if c.get("category") == "단독 출제 참고"], 1
    ):
        member = (cluster.get("members") or [None])[0]
        if not member:
            continue
        rows.append({
            "rank": rank,
            "id": f"{member['round']}#{member['num']}",
            "concept_key": cluster.get("concept_key", "기타"),
            "singleton_score": cluster.get("singleton_score", 0),
            "related_years": cluster.get("related_years", []),
            "related_year_count": cluster.get("related_year_count", 0),
            "related_count": cluster.get("related_count", 0),
            "core_score": cluster.get("core_score", 0),
            "numeric_score": cluster.get("numeric_score", 0),
            "utility_score": cluster.get("utility_score", 0),
            "latest_score": cluster.get("latest_score", 0),
        })
    path = output_path or os.path.join(META_DIR, "singleton_priority.json")
    with open(path, "w", encoding="utf-8") as fp:
        json.dump(rows, fp, ensure_ascii=False, indent=2)
    return rows


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
        "반복 출제 유형 우선. 빈도점수(출제 연도 수×3 + 출제 횟수)와 최신점수를 분리 표시하며 순위는 빈도 우선. 연도별 상한 없음.",
        "대표는 확인된 이미지가 있을 때 표시하며, 같은 유형 링크는 의미 검수된 반복 문항만 연결.",
        "",
    ]
    for i, c in enumerate(ranked, 1):
        members = sorted(c["members"], key=lambda m: (m["year"], m["round"], m["num"]))
        years = sorted({m["year"] for m in members})
        category = c.get('category', '미분류')
        lines.append(f"## {i}. {category} | {' / '.join(str(y) for y in years)} 출제")
        lines.append("")
        rep = max(members, key=lambda m: (m["year"], len(m.get("stem") or "")))
        img = os.path.join(VAULT, "기출문제", "이미지", rep["round"], f"q{rep['num']:02d}.jpg")
        problem_name = f"{rep['round']}-q{rep['num']:02d}-problem.jpg"
        full_name = f"{rep['round']}-q{rep['num']:02d}-full.jpg"
        problem_img = os.path.join(VAULT, "기출핵심요약", "이미지확대", problem_name)
        full_img = os.path.join(VAULT, "기출핵심요약", "이미지확대", full_name)
        if os.path.isfile(problem_img) and os.path.isfile(full_img):
            lines.append(f"[![](이미지확대/{problem_name})](이미지확대/{full_name})")
            lines.append("")
        elif os.path.isfile(img):
            lines.append(f"[원본 이미지 확대](../기출문제/이미지/{rep['round']}/q{rep['num']:02d}.jpg)")
            lines.append("")
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
        if c.get('category') == '단독 출제 참고':
            lines.append(format_singleton_line(c))
        else:
            lines.append(format_frequency_line(c))
        lines.append(format_member_answers(members, answer_index))
        lines.append("")
    return "\n".join(lines)


def main():
    data = load_inventory()
    items = []
    for rnd in data["rounds"]:
        items.extend(stems_from_round(rnd))
    clusters = cluster_items(items)
    image_review = load_image_review_index()
    # Image-reviewed topic groups are the final authority; do not re-merge them.
    ranked = apply_image_review(clusters, image_review)
    ranked = annotate_singletons(ranked, items, image_review)
    ranked = rank_reviewed_clusters(ranked)
    ranked = reorder_singleton_section(ranked)
    write_singleton_priority_metadata(ranked[:100])
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
