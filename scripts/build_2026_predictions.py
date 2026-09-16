import json,re
from pathlib import Path
from difflib import SequenceMatcher

ROOT=Path('/var/minis/workspace/interior-craft')
META=ROOT/'metadata'
CLUES=json.loads((META/'2026_topic_clues.json').read_text())
EXIST=json.loads((META/'existing_question_ocr_index.json').read_text()) if (META/'existing_question_ocr_index.json').exists() else json.loads((META/'existing_question_index.json').read_text())
ANS={}
for p in META.glob('answers_*.json'):
 try:
  d=json.loads(p.read_text()); rid=d.get('round')
  for n,v in (d.get('answers') or {}).items(): ANS[(rid,str(n))]=v
 except Exception: pass

STOP={'교재','쪽','번','회','기능사','필기','문제','설명','종류','방법','계획','원리','요소','성질','재료','대한','관한','옳지','옳은','다음','중','것','내용','출제'}
def clean_clue(s):
 s=re.sub(r'^\s*[-•]\s*','',s)
 s=re.sub(r'\(교재\s*\d+쪽,\s*\d+번\)','',s)
 s=re.sub(r'[()]',' ',s)
 s=re.sub(r'\s+',' ',s).strip()
 return s

def topic_tokens(s):
 s=clean_clue(s)
 return {x for x in re.findall(r'[가-힣A-Za-z0-9]+',s.lower()) if len(x)>=2 and x not in STOP}

def norm(s): return re.sub(r'[^가-힣0-9]','',s or '')
def infer_question_form(clue):
 c=clean_clue(clue)
 if any(x in c for x in ('열전도','조도','환기','조립률','치수','강도','비중','온도')): return '정의·수치·계산 특성'
 if any(x in c for x in ('표시','기호','선의','도면','제도')): return '표시·도면·제도 원칙'
 if any(x in c for x in ('종류','형식','방식','배치','의자','가구','문','조명')): return '종류·특성·적용 구분'
 return '개념·특성 설명 중 옳지 않은 것 판별'

def match_score(clue,q):
 ct=topic_tokens(clue); qt=topic_tokens(q['text'])
 overlap=len(ct&qt)/max(1,len(ct))
 # Match the cleaned topic to the first meaningful question text.
 seq=SequenceMatcher(None,norm(' '.join(sorted(ct))),norm(q['text'][:900])).ratio()
 return round(overlap*.72+seq*.28,4)

def build():
 rows=[]
 for c in CLUES:
  ranked=sorted(((match_score(c['clue'],q),q) for q in EXIST),key=lambda x:x[0],reverse=True)
  top=[];seen=set()
  for s,q in ranked:
   if s<.12 or q['id'] in seen: continue
   seen.add(q['id'])
   ans=ANS.get((q['round'],str(q['number'])))
   top.append({'id':q['id'],'score':s,'text':q['text'][:700],'answer':ans.get('answer') if ans else None,'answer_status':ans.get('status') if ans else None})
   if len(top)>=8: break
  best=top[0]['score'] if top else 0
  conf='중간' if best>=.35 and len(top)>=2 else ('낮음' if best<.25 else '중간')
  if c['source']=='new_full': conf='중간'
  rows.append({**c,'clean_topic':clean_clue(c['clue']),'question_form':infer_question_form(c['clue']),'confidence':conf,'matches':top,'prediction_status':'예측','web_evidence':[]})
 (META/'2026_prediction_candidates.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
 print('clues',len(rows),'with_matches',sum(bool(x['matches']) for x in rows),'medium',sum(x['confidence']=='중간' for x in rows))
 return rows

if __name__=='__main__': build()
