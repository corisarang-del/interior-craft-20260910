"""Frequency ranking for the interior-craft 100-question summary."""
import re
from difflib import SequenceMatcher


def normalize_stem(text):
    return re.sub(r"[^가-힣0-9]", "", text or "")


def importance(years, count, keywords=0, latest=False):
    """Actual frequency score. Recency is deliberately not multiplied in."""
    return len(set(years)) * 3 + count + keywords * 2


def cluster_score_components(cluster, latest_years=(2024, 2025)):
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


# The singleton section is intentionally a reorder of the existing 69 slots,
# not a new selection of arbitrary OCR candidates.
SINGLETON_CONCEPT_OVERRIDES = {
    "2017-1회#1": "상점계획", "2017-1회#2": "치수기입", "2017-1회#3": "금속방식",
    "2017-1회#4": "상점계획", "2017-1회#5": "디자인형태", "2017-1회#6": "의자·소파",
    "2017-1회#7": "형태지각", "2017-1회#8": "실내기본요소", "2017-1회#10": "수납",
    "2017-1회#11": "창호·문", "2017-1회#14": "판매형식", "2017-1회#15": "부엌계획",
    "2017-1회#17": "주거배치", "2017-1회#21": "휘도", "2017-1회#23": "지붕",
    "2017-1회#24": "금속방식", "2017-1회#25": "콘크리트피로", "2017-1회#26": "강재열처리",
    "2017-1회#27": "음향·잔향", "2017-1회#28": "목재강도", "2017-1회#29": "목재강도",
    "2017-1회#30": "음향재료", "2017-1회#31": "금속방식", "2017-1회#32": "금속재료",
    "2017-1회#33": "콘크리트비파괴", "2017-1회#34": "석재가공", "2017-1회#35": "철근콘크리트",
    "2017-1회#36": "목재강도", "2017-1회#37": "음향재료", "2017-1회#39": "물시멘트비",
    "2017-1회#40": "벽돌", "2017-1회#42": "벽돌쌓기", "2017-1회#44": "백화",
    "2017-1회#45": "철근", "2017-1회#46": "스티프너", "2017-1회#48": "스티프너",
    "2017-1회#49": "제도연필", "2017-1회#50": "건축제도기호", "2017-1회#51": "투시도",
    "2017-1회#53": "지붕", "2017-1회#54": "설계도", "2017-1회#55": "동바리",
    "2017-1회#56": "치수기입", "2017-1회#57": "철근콘크리트보", "2017-1회#58": "동선",
    "2017-1회#60": "허니콤보",
    "2018-1회#1": "상점계획", "2018-1회#2": "가구", "2018-1회#3": "점토",
    "2018-1회#4": "스케일", "2018-1회#5": "판매진열", "2018-1회#6": "발코니",
    "2018-1회#7": "침실계획", "2018-1회#8": "디자인점", "2018-1회#11": "일조조절",
    "2018-1회#12": "공간분할", "2018-1회#13": "황금비례", "2018-1회#14": "연색성",
    "2018-1회#15": "열전달", "2018-1회#16": "바닥", "2018-1회#18": "동선",
    "2018-1회#20": "목재방부", "2018-1회#22": "테라코타", "2018-1회#24": "질감",
    "2018-1회#25": "클리어래커", "2018-1회#26": "목재방부", "2018-1회#28": "시멘트안정성",
    "2018-1회#29": "온열요소", "2018-1회#30": "알루미나시멘트",
}

OVERRIDE_CANONICAL = {
    "상점계획": "상점계획", "치수기입": "치수기입", "금속방식": "금속방식",
    "디자인형태": "디자인·형태", "의자·소파": "의자·소파", "형태지각": "디자인·형태",
    "실내기본요소": "실내기본요소", "수납": "수납", "창호·문": "창호·문",
    "판매형식": "판매형식", "부엌계획": "부엌계획", "주거배치": "주거배치",
    "휘도": "휘도", "지붕": "지붕", "콘크리트피로": "콘크리트·피로",
    "강재열처리": "강재·열처리", "음향·잔향": "음향·잔향", "목재강도": "목재·강도",
    "음향재료": "음향재료", "금속재료": "금속재료", "콘크리트비파괴": "콘크리트·비파괴",
    "철근콘크리트": "철근콘크리트", "석재가공": "석재가공", "철근": "철근",
    "물시멘트비": "물시멘트비", "벽돌": "벽돌", "벽돌쌓기": "벽돌쌓기",
    "백화": "백화", "제도연필": "제도용구", "건축제도기호": "제도기호",
    "투시도": "투시도", "설계도": "설계도", "동바리": "동바리", "허니콤보": "허니콤보",
    "스케일": "제도용구", "발코니": "주거배치", "클리어래커": "도장",
    "연색성": "연색성", "열전달": "열전달", "바닥": "실내기본요소",
    "디자인점": "디자인·형태", "공간분할": "공간분할", "질감": "질감",
    "침실계획": "침실계획", "온열요소": "온열요소", "알루미나시멘트": "시멘트",
    "점토": "점토", "시멘트안정성": "시멘트",
}

# Generic reference rules intentionally avoid broad words such as 구조, 재료,
# 문, 가구, 배치, and 콘크리트 alone. They are only used to count related
# concepts in the full 2017~2025 question population.
REFERENCE_RULES = (
    ("조도", ("조도",)), ("휘도", ("휘도",)),
    ("음향·잔향", ("잔향시간", "잔향", "음향계획", "흡음", "소음")),
    ("자연환기", ("자연환기", "환기량", "중력환기", "풍력환기")),
    ("강제환기", ("강제환기", "기계환기", "압입식", "제1종환기", "제2종환기", "제3종환기")),
    ("결로", ("결로",)), ("열관류·열전도", ("열관류", "열전도율", "열전도")),
    ("디자인·황금비", ("황금비례", "황금비", "피보나치", "르코르뷔지에")),
    ("디자인·형태", ("형태의지각", "형태지각", "균형의원리", "디자인의원리", "착시")),
    ("부엌계획", ("작업삼각형", "부엌의", "부억의", "주방의")),
    ("상점동선", ("상점의동선", "고객동선", "종업원동선", "상품동선")),
    ("판매형식", ("대면판매", "측면판매", "판매형식")),
    ("판매진열", ("상품진열", "진열및판매대")),
    ("가구배치", ("가구배치", "가구의배치", "배치방법", "배치유형")),
    ("수납", ("기능적인수납", "수납용가구", "수납장")),
    ("의자·소파", ("세티", "스툴", "오토만", "체스터필드", "바실리의자")),
    ("창호·문", ("창호", "창문", "개구부", "블라인드", "커튼", "쇼윈도")),
    ("주거·상업계획", ("주택계획", "침실계획", "욕실계획", "주거공간", "소요실", "파사드")),
    ("목재·강도", ("목재의강도", "목재강도", "목재의응력", "함수율", "공극율")),
    ("목재·접합", ("목재접합", "이음과맞춤", "연귀맞춤", "산지", "장부")),
    ("목재·보드", ("합판", "파티클보드", "파티클", "mdf", "섬유판", "목질보드")),
    ("목구조", ("목구조", "토대", "가새", "왕대공", "서까래")),
    ("석재·타일", ("테라코타", "암면", "대리석", "화강암", "석재가공", "타일")),
    ("콘크리트·컨시스턴시", ("컨시스턴시", "슬럼프")),
    ("콘크리트·혼화", ("혼화재", "혼화제", "플라이애시", "감수제", "방청제")),
    ("콘크리트·거푸집", ("거푸집", "측압", "동바리")),
    ("콘크리트·슬래브", ("플랫슬래브", "플랫슬라브", "슬래브")),
    ("콘크리트·배합", ("물시멘트비", "배합설계", "블리딩", "워커빌리티")),
    ("콘크리트·피로", ("피로파괴", "콘크리트피로")),
    ("철근콘크리트", ("철근콘크리트", "철근콘크리트조")),
    ("시멘트", ("조강시멘트", "중용열시멘트", "포틀랜드시멘트", "시멘트안정성")),
    ("금속·부식", ("금속의부식", "금속부식", "금속방식", "방청도료", "부식", "방식")),
    ("강재·열처리", ("열처리", "풀림", "담금질", "뜨임", "탄소량")),
    ("철골·접합", ("고력볼트", "볼트접합", "용접결함", "용접", "스티프너", "허니콤보")),
    ("철골·구조", ("철골구조", "트러스보", "스페이스프레임", "좌굴", "주각")),
    ("유리·수지·도장", ("복층유리", "강화유리", "망입유리", "소다석회유리", "유리", "수지", "페인트", "도료", "플라스터", "아스팔트", "접착제")),
    ("건축제도·치수", ("치수기입", "표제란", "도면의크기", "치수선")),
    ("건축제도·선", ("선긋기", "실선", "파선", "쇄선", "선의종류")),
    ("건축제도·도구", ("제도용구", "디바이더", "삼각스케일", "삼각자", "컴퍼스", "지우개")),
    ("건축제도·투시", ("투시도", "투상도", "평면도", "단면도", "입면도")),
    ("건축제도·기호", ("표시기호", "평면표시", "재료표시", "일점쇄선")),
    ("건축구조·기초", ("지내력", "독립기초", "온통기초", "기초평면도")),
    ("건축구조·철근", ("철근", "주근", "늑근", "스터럽", "배근")),
    ("건축구조·보", ("보의", "보강", "전단력", "휨모멘트")),
)


def _reference_key(source):
    source = (source or "").lower().replace(" ", "")
    matches = []
    for key, words in REFERENCE_RULES:
        for word in words:
            if word in source:
                matches.append((len(word), key))
    return max(matches)[1] if matches else "기타"


def concrete_concept_key(topic, text="", item_id=None):
    if item_id in SINGLETON_CONCEPT_OVERRIDES:
        raw = SINGLETON_CONCEPT_OVERRIDES[item_id]
        return OVERRIDE_CANONICAL.get(raw, raw)
    topic_key = _reference_key(topic)
    if topic_key != "기타":
        return topic_key
    return _reference_key(text)


def extract_concept_key(topic, text=""):
    return concrete_concept_key(topic, text)


def _topic_score(topic, text):
    key = concrete_concept_key(topic, text)
    combined = f"{topic or ''} {text or ''}"
    core_keys = {"조도", "휘도", "음향·잔향", "자연환기", "강제환기", "결로", "열관류·열전도", "목재·강도", "콘크리트·컨시스턴시", "콘크리트·배합", "철근콘크리트", "건축제도·치수", "건축구조·철근"}
    numeric_words = ("조도", "휘도", "열전도", "열관류", "잔향", "강도", "치수", "규격", "단위", "온도", "각도", "두께", "높이", "면적", "비중", "기준", "탄소량")
    utility_words = ("옳지", "종류", "방법", "원리", "비교", "기준", "특성", "설명", "구분")
    core = 5 if key in core_keys else (4 if key != "기타" else 2)
    numeric = 2 if any(x in combined for x in numeric_words) else 0
    utility = 2 if any(x in combined for x in utility_words) else 1
    return core, numeric, utility


def singleton_score_components(cluster):
    years = sorted(set(cluster.get("related_years") or []))
    count = int(cluster.get("related_count") or 0)
    core = int(cluster.get("core") or 0)
    numeric = int(cluster.get("numeric") or 0)
    utility = int(cluster.get("utility") or 0)
    return {
        "related_years": years,
        "related_year_count": len(years),
        "related_count": count,
        "core_score": core,
        "numeric_score": numeric,
        "utility_score": utility,
        "singleton_score": len(years) * 3 + count + core * 2 + numeric + utility,
    }


def annotate_singletons(clusters, all_items, review_index=None):
    """Attach related-concept frequency to singleton clusters only."""
    review_index = review_index or {}
    concept_items = {}
    for item in all_items:
        key = f"{item.get('round', '')}#{item.get('num', '')}"
        topic = review_index.get(key, {}).get("topic", "")
        concept = concrete_concept_key(topic, item.get("stem", ""), None)
        if concept != "기타":
            concept_items.setdefault(concept, []).append(item)
    out = []
    for cluster in clusters:
        if len(cluster.get("members") or []) != 1:
            out.append(cluster)
            continue
        member = cluster["members"][0]
        key = f"{member.get('round', '')}#{member.get('num', '')}"
        topic = review_index.get(key, {}).get("topic", "")
        concept = concrete_concept_key(topic, member.get("stem", ""), key)
        related = [x for x in concept_items.get(concept, []) if x.get("id") != member.get("id")]
        enriched = dict(cluster)
        enriched["concept_key"] = concept
        enriched["related_years"] = sorted({x.get("year") for x in related if x.get("year")})
        enriched["related_count"] = len(related)
        enriched["core"], enriched["numeric"], enriched["utility"] = _topic_score(topic, member.get("stem", ""))
        enriched.update(singleton_score_components(enriched))
        out.append(enriched)
    return out


def _stable_key(cluster):
    ids = [f"{m.get('round', '')}#{int(m.get('num', 0)):02d}" for m in cluster.get("members", [])]
    return min(ids) if ids else str(cluster.get("stable_key", ""))


def rank_singletons(clusters):
    ranked = []
    for cluster in clusters:
        enriched = dict(cluster)
        enriched.update(singleton_score_components(enriched))
        ranked.append(enriched)
    ranked.sort(key=lambda x: (
        -x["singleton_score"], -x["related_year_count"], -x["related_count"],
        -x["core_score"], -x["numeric_score"], -x["utility_score"],
        x.get("stable_key", _stable_key(x)),
    ))
    return ranked


def rank_clusters(clusters):
    ranked = []
    for cluster in clusters:
        scores = cluster_score_components(cluster)
        repeated = scores["repeat_count"] > 1
        extra = {} if repeated else singleton_score_components(cluster)
        ranked.append({
            **cluster, **scores, **extra,
            "score": scores["frequency_score"],
            "category": "반복 출제 핵심 유형" if repeated else "단독 출제 참고",
            "stable_key": _stable_key(cluster),
        })
    ranked.sort(key=lambda x: (
        0 if x["category"] == "반복 출제 핵심 유형" else 1,
        -(x["frequency_score"] if x["category"] == "반복 출제 핵심 유형" else x.get("singleton_score", 0)),
        -(x["unique_years"] if x["category"] == "반복 출제 핵심 유형" else x.get("related_year_count", 0)),
        -(x["repeat_count"] if x["category"] == "반복 출제 핵심 유형" else x.get("related_count", 0)),
        -x.get("core_score", 0), x["stable_key"],
    ))
    return ranked


def _similar(a, b, threshold):
    return bool(a and b and SequenceMatcher(None, a, b).ratio() > threshold)


def cluster_items(items, threshold=0.6):
    clusters = []
    for item in items:
        stem = item.get("stem") or normalize_stem(item.get("text", ""))
        for cluster in clusters:
            if stem == cluster["stem"] or _similar(stem, cluster["stem"], threshold):
                cluster["members"].append(item)
                break
        else:
            clusters.append({"stem": stem, "members": [item]})
    return clusters


def top_n(items, limit=100):
    return rank_clusters(cluster_items(items))[:limit]
