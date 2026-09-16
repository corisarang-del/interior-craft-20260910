import json,re
from pathlib import Path
ROOT=Path('/var/minis/workspace/interior-craft'); META=ROOT/'metadata'; OCR=ROOT/'raw/youtube/ocr'
inv=json.loads((META/'inventory.json').read_text())
video_round={}
for r in inv.get('rounds',[]):
 for vid in r.get('video_ids',[]): video_round[vid]=r['id']
by={}
for p in OCR.glob('*.json'):
 vid=p.stem
 rid=video_round.get(vid)
 if not rid: continue
 try: rows=json.loads(p.read_text())
 except: continue
 for x in rows:
  n=x.get('num'); text=x.get('text') or ''
  if not n or len(re.sub(r'\s','',text))<10: continue
  key=(rid,str(int(n)))
  # Retain the longest OCR frame for each question; it usually contains
  # the complete stem and choices without relying on subtitle answers.
  if key not in by or len(text)>len(by[key]['text']):
   by[key]={'id':f'{rid}#{int(n)}','round':rid,'number':int(n),'text':text,'video_id':vid,'frame':x.get('file'),'ts':x.get('ts')}
out=sorted(by.values(),key=lambda x:(x['round'],x['number']))
(META/'existing_question_ocr_index.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print('questions',len(out),'rounds',len(set(x['round'] for x in out)))
