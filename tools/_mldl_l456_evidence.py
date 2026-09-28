from __future__ import annotations
import json, subprocess, time
from pathlib import Path
from urllib.parse import quote
import requests
LECTURES=[
 {"tag":"L04","title":"Linear Regression II","video":"AyWYU2mmhKs","slides":"1PszJMMpIQoBoY5TihGsLp7QNH4xGJj7ILfzjwy0e_Fg"},
 {"tag":"L05","title":"Classification I - Logistic Regression","video":"qArmG1FPQII","slides":"1SDVyf5p_CMFsbURRWZWzW4CzwE35fykI4fj5wMfTYI0"},
 {"tag":"L06","title":"Classification II - Bayes Classifiers","video":"4SDi3kO0748","slides":"1yh6FiKvPoxiq-STNXF1Ut_UQZxNNPmpjX2PfDRn6MQg"},]
ROOT=Path('artifact');ROOT.mkdir(exist_ok=True)
def run(cmd,log,timeout=180):
 log.parent.mkdir(parents=True,exist_ok=True)
 with log.open('a',encoding='utf-8') as f:
  f.write('\n$ '+' '.join(map(str,cmd))+'\n')
  try:return subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,text=True,timeout=timeout).returncode
  except Exception as e:f.write(repr(e)+'\n');return 999
def get(url,path,min_bytes=1000):
 err='not attempted'
 for n in range(2):
  try:
   r=requests.get(url,timeout=35,headers={'User-Agent':'Mozilla/5.0'},allow_redirects=True)
   if r.status_code==200 and len(r.content)>min_bytes:path.write_bytes(r.content);return {'ok':True,'bytes':len(r.content),'url':r.url}
   err=f'{r.status_code} {len(r.content)} {r.url}'
  except Exception as e:err=repr(e)
  time.sleep(2)
 return {'ok':False,'error':err}
manifest=[]
for item in LECTURES:
 tag=item['tag'];vid=item['video'];d=ROOT/tag;d.mkdir(parents=True,exist_ok=True);logs=d/'logs';logs.mkdir(exist_ok=True);rec=dict(item)
 rec['slide_download']=get(f'https://docs.google.com/presentation/d/{item["slides"]}/export/pdf',d/f'{tag}_slides.pdf')
 if (d/f'{tag}_slides.pdf').exists():
  sd=d/'slide_images';sd.mkdir(exist_ok=True);run(['pdftoppm','-jpeg','-r','105',str(d/f'{tag}_slides.pdf'),str(sd/'slide')],logs/'slides.log');rec['slide_images']=len(list(sd.glob('*.jpg')))
 target=f'https://youtube-transcript.ai/transcript/{vid}.txt?lang=a-ko';proxy='https://api.allorigins.win/raw?url='+quote(target,safe='')
 subs=d/'subtitles';subs.mkdir(exist_ok=True);rec['thirdparty_transcript']=get(proxy,subs/f'{tag}_ko_auto_thirdparty.md',min_bytes=5000)
 try:
  info_url='https://weirddl.sbs/api/info?quality=360&url='+quote(f'https://youtu.be/{vid}',safe='')
  ir=requests.get(info_url,timeout=35,headers={'User-Agent':'Mozilla/5.0'});(logs/'weirddl.log').write_text(f'{ir.status_code}\n{ir.text[:5000]}',encoding='utf-8')
  if ir.status_code==200:
   info=ir.json();(d/f'{tag}_weirddl.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
   rec.update({'youtube_title':info.get('title'),'duration':info.get('duration'),'author':info.get('author'),'thumbnail':info.get('thumbnail'),'media_count':len(info.get('media',[]))})
 except Exception as e:rec['media_info_error']=repr(e)
 manifest.append(rec)
(ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8');(ROOT/'README.txt').write_text('Lecture 4-6 official slide PDFs, full Korean auto-caption transcripts, and public video metadata inventory.\n',encoding='utf-8');print(json.dumps(manifest,ensure_ascii=False,indent=2))
