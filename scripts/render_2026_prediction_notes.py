import json
from pathlib import Path

ROOT=Path('/var/minis/workspace/interior-craft')
META=ROOT/'metadata'; VAULT=Path('/var/minis/mounts/minis1/obsidian-vault/지식/실내건축기능사')
cards=json.loads((META/'2026_prediction_cards.json').read_text())
web=json.loads((META/'2026_web_evidence.json').read_text())
outdir=VAULT/'2026-예상복원'; outdir.mkdir(parents=True,exist_ok=True)

def render(rid, rows):
 lines=['---',f'회차: {rid}','태그: [실내건축기능사, 예상복원, 2026]','상태: 예측','---','',f'# {rid} 예상복원 카드','', '> 주제·교재 위치·기존 유사문항을 바탕으로 만든 예측 자료다. 실제 문제·보기·공식 정답이 아니며, 기존 복원 노트와 핵심요약에는 반영하지 않았다.','']
 for c in rows:
  n=c['number']; lines += [f'## {n}. {c["clean_topic"]}', '', f'- 상태: **{c["prediction_status"]}**',f'- 교재 위치: {c.get("page")}쪽 {c.get("book_number")}번' if c.get('page') else '- 출처: 신규 문제 전문',f'- 신뢰도: {c["confidence"]}',f'- 예상 문제 형식: {c["expected_form"]}', '', '### 표시된 주제·원문', c['clue'], '', '### 예상 출제 방향', c['prediction'], '']
  if c['candidate_answer']: lines += ['### 예상 후보', c['candidate_answer'],'','> 예상 후보는 정답이 아니다. 실제 보기·공식 정답 확인 전 확정하지 않는다.','']
  if c['related_existing']:
   links=', '.join(f'[[지식/실내건축기능사/기출문제/{x.split("#")[0]}#{x.split("#")[1]}|{x}]]' for x in c['related_existing'])
   lines += ['### 기존 유사문제',links,'','유사문항은 핵심 개념·풀이법 참고용이며 동일 출제를 보장하지 않는다.','']
  else: lines += ['### 기존 유사문제','확인된 직접 유사문항 없음.','']
  lines += ['### 웹 근거','- 검색 결과는 교재·공개 CBT·Q-Net 자료의 존재 확인용이며, 이 문항의 실제 원문·정답을 확정하는 근거로 사용하지 않았다.','']
  lines += ['---','']
 lines += ['## 공통 주의','- 이 노트의 모든 답·문제 재구성은 `예측` 상태다.','- 실제 문제 이미지·복원 원문·공식 정답이 확보되면 별도 검수 후에만 `추론` 또는 `확정`으로 승격한다.','- 기존 `기출문제/2026-*.md`와 `기출핵심요약`은 수정하지 않았다.','']
 return '\n'.join(lines)

for rid in ['2026-1회','2026-2회','2026-3회']:
 (outdir/f'{rid}-예상복원.md').write_text(render(rid,[x for x in cards if x['round']==rid]),encoding='utf-8')
print('written',len(list(outdir.glob('*-예상복원.md'))),'cards',len(cards))
