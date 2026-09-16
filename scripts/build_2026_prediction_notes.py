import json, re
from pathlib import Path

ROOT=Path('/var/minis/workspace/interior-craft')
META=ROOT/'metadata'; VAULT=Path('/var/minis/mounts/minis1/obsidian-vault/지식/실내건축기능사')
CLUES=json.loads((META/'2026_topic_clues.json').read_text())
CAND=json.loads((META/'2026_prediction_candidates.json').read_text())

WEB_EVIDENCE=[
 {'source':'Google 검색 결과','url':'https://www.google.com/search?q=%EC%8B%A4%EB%82%B4%EA%B1%B4%EC%B6%95%EA%B8%B0%EB%8A%A5%EC%82%AC+2026+1%ED%9A%8C+%EB%B3%B5%EC%9B%90','finding':'2026-1회 성안당 교재 대조 자료와 CBT 복원·해설 검색 결과가 확인되지만, 전체 공식 문제·정답 원문은 확인하지 못함.','grade':'D'},
 {'source':'Google 검색 결과','url':'https://www.google.com/search?q=site%3Aq-net.or.kr+%EC%8B%A4%EB%82%B4%EA%B1%B4%EC%B6%95%EA%B8%B0%EB%8A%A5%EC%82%AC+%EC%98%88%EC%8B%9C%EB%AC%B8제+2026','finding':'Q-Net 예시문제 자료실 검색 결과 확인. 예시문제는 실제 2026 회차 복원 원문과 동일하다고 단정하지 않음.','grade':'D'},
 {'source':'Google 검색 결과','url':'https://www.google.com/search?q=%EC%84%B1%EC%95%88%EB%8B%B9+%EC%8B%A4%EB%82%B4%EA%B1%B4%EC%B6%95%EA%B8%B0%EB%8A%A5%EC%82%AC+2026+%EA%B8%B0%EC%B6%9C','finding':'성안당 2026 교재와 공개 자료 검색 결과. 교재 페이지·문항 주제의 보조 근거로만 사용.','grade':'D'},
]

RELATED={
 '황금비': ['2021-3회#28','2025-1회#27'], '르코르뷔지에':['2021-3회#28','2025-1회#27'],
 '천장':['2024-1회#1','2024-3회#19'], '자연 환기':['2024-1회#15'], '잔향':['2017-1회#20','2024-3회#31'],
 '아스팔트':['2022-3회#26','2023-3회#38'], '조강':['2021-3회#18'], '컨시스턴시':['2021-1회#42','2024-1회#21'],
 '혼화':['2024-1회#22','2024-1회#27'], '고력 볼트':['2024-1회#60'], '스티프너':['2024-3회#41'],
 '회전문':['2022-3회#28','2025-1회#35'], '복층 유리':['2024-3회#23','2025-1회#50'],
 '삼각 스케일':['2022-3회#49','2024-3회#46'], '삼각자':['2024-1회#40'],
 '벽돌':['2020-1회#44','2024-3회#39','2025-1회#31'], '금속의 부식':['2022-3회#34','2024-3회#26'],
 '수평 블라인드':['2020-1회#4','2024-1회#9'], '블라인드':['2020-1회#4','2024-1회#9'],
 '조선시대':['2020-1회#6','2022-3회#15'], '투시도':['2019-1회#55','2023-1회#57'],
 '치수':['2018-1회#54','2021-3회#33','2024-3회#49'], '소성온도':['2024-1회#23','2025-1회#56'],
 '골든':['2024-3회#13','2025-1회#11'], '열관류':['2021-3회#52','2022-1회#39'],
 '결로':['2022-1회#40','2023-1회#40'], '점토벽돌':['2022-1회#42','2023-1회#42'],
 '스페이스':['2020-1회#57','2025-1회#32'], '자연형':['2020-1회#11','2024-1회#20'],
 '건축화 조명':['2020-1회#16','2023-1회#17'], '조명 방식':['2020-1회#16','2023-1회#17'],
 '강화유리':['2022-3회#37'], '테라코타':['2018-1회#22'], '목구조':['2021-3회#36','2024-3회#58'],
 '고객 동선':['2021-3회#10','2024-3회#20'], '사행':['2026-3회#56'],
}

def clean(s): return re.sub(r'^\s*[-•]\s*|\s*\(교재\s*\d+쪽,\s*\d+번\)','',s).strip()
def related(topic):
 out=[]
 for k,ids in RELATED.items():
  if k in topic and ids:
   for x in ids:
    if x not in out: out.append(x)
 return out[:5]
def form(topic):
 if any(k in topic for k in ['조도','열전도','열관류','잔향','강도','치수','각도','지내력']): return '정의·수치·계산형 객관식'
 if any(k in topic for k in ['표시','선긋기','제도','도면','기호','표제란']): return '도면·표시·제도 통칙형 객관식'
 if any(k in topic for k in ['종류','형식','방식','배치','가구','조명','문','재료']): return '종류·특성·적용 구분형 객관식'
 return '개념·특성 옳고 그름 판별형 객관식'
def direction(topic):
 return f'{topic}에 관한 정의·특성·적용 조건을 제시하고 옳은 설명 또는 옳지 않은 설명을 고르는 4지선다형 출제가 유력하다.'
def candidate(topic):
 for k in ['황금비','르코르뷔지에','천장','자연 환기','잔향','조강','컨시스턴시','혼화','고력 볼트','스티프너','회전문','복층 유리','삼각 스케일','벽돌','금속의 부식','투시도','치수','골든','결로','점토벽돌','스페이스','자연형','건축화 조명','강화유리','테라코타']:
  if k in topic: return f'{k}의 정의·대표 특성·대표 적용 사례 중 하나가 정답 후보가 될 수 있음'
 return None

cards=[]
for c in CAND:
 topic=clean(c['clue'])
 rel=related(topic)
 # Only the three new full questions have actual original text; all others remain predictions.
 status='예측'
 if c['source']=='new_full': status='예측(원문 있음·정답 별도 검증 필요)'
 cards.append({**c,'clean_topic':topic,'prediction_status':status,'expected_form':form(topic),'prediction':direction(topic),'candidate_answer':candidate(topic),'related_existing':rel,'web_evidence':[x['url'] for x in WEB_EVIDENCE],'evidence_grade':'C' if rel else 'D'})
(META/'2026_prediction_cards.json').write_text(json.dumps(cards,ensure_ascii=False,indent=2),encoding='utf-8')
(META/'2026_web_evidence.json').write_text(json.dumps(WEB_EVIDENCE,ensure_ascii=False,indent=2),encoding='utf-8')
print('cards',len(cards),'related',sum(bool(x['related_existing']) for x in cards),'new_full',sum(x['source']=='new_full' for x in cards))