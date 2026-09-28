from __future__ import annotations
import json, subprocess, time
from pathlib import Path
from urllib.parse import quote
import requests
LECTURES=[
 {"tag":"L04","title":"Linear Regression II","video":"AyWYU2mmhKs","slides":"1PszJMMpIQoBoY5TihGsLp7QNH4xGJj7ILfzjwy0e_Fg"},
 {"tag":"L05","title":"Classification I - Logistic Regression","video":"qArmG1FPQII","slides":"1SDVyf5p_CMFsbURRWZWzW4CzwE35fykI4fj5wMfTYI0"},
 {"tag":"L06","title":"Classification II - Bayes Classifiers","video":"4SDi3kO0748","slides":"1yh6FiKvPoxiq-STNXF1Ut_UQZxNNPmpjX2PfDRn6MQg"},]
ROOT=Path('artifact'); ROOT.mkdir(exist_ok=True)
def run(cmd,log,timeout=1800):
 log.parent.mkdir(parents=True,exist_ok=True)
 with log.open('a',encoding='utf-8') as f:
  f.write('\n$ '+' '.join(map(str,cmd))+'\n')
  try:return subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,text=True,timeout=timeout).returncode
  except Exception as e:f.write(repr(e)+'\n');return 999
def get(url,path,min_bytes=1000):
 for n in range(5):
  try:
   r=requests.get(url,timeout=180,headers={'User-Agent':'Mozilla/5.0'},allow_redirects=True)
   if r.status_code==200 and len(r.content)>min_bytes:path.write_bytes(r.content);return {'ok':True,'bytes':len(r.content),'url':r.url}
   err=f'{r.status_code} {len(r.content)} {r.url}'
  except Exception as e:err=repr(e)
  time.sleep(2+n*2)
 return {'ok':False,'error':err}
def stream_get(url,path):
 try:
  with requests.get(url,timeout=600,headers={'User-Agent':'Mozilla/5.0'},stream=True) as r:
   r.raise_for_status()
   with path.open('wb') as f:
    for chunk in r.iter_content(1024*1024):
     if chunk:f.write(chunk)
  return {'ok':path.exists() and path.stat().st_size>1000,'bytes':path.stat().st_size}
 except Exception as e:return {'ok':False,'error':repr(e)}
common=['yt-dlp','--remote-components','ejs:github','--js-runtimes','node','--extractor-args','youtube:player_client=android,web']
manifest=[]
for item in LECTURES:
 tag=item['tag'];vid=item['video'];url=f'https://www.youtube.com/watch?v={vid}';d=ROOT/tag;d.mkdir(parents=True,exist_ok=True);logs=d/'logs';logs.mkdir(exist_ok=True);rec=dict(item)
 rec['slide_download']=get(f'https://docs.google.com/presentation/d/{item["slides"]}/export/pdf',d/f'{tag}_slides.pdf')
 if (d/f'{tag}_slides.pdf').exists():
  sd=d/'slide_images';sd.mkdir(exist_ok=True);run(['pdftoppm','-jpeg','-r','105',str(d/f'{tag}_slides.pdf'),str(sd/'slide')],logs/'slides.log');rec['slide_images']=len(list(sd.glob('*.jpg')))
 try:
  cp=subprocess.run(common+['--dump-single-json','--skip-download',url],capture_output=True,text=True,timeout=300);(logs/'metadata.log').write_text(cp.stderr,encoding='utf-8')
  if cp.returncode==0:
   (d/f'{tag}_metadata.json').write_text(cp.stdout,encoding='utf-8');md=json.loads(cp.stdout);rec.update({'youtube_title':md.get('title'),'duration':md.get('duration'),'channel':md.get('channel'),'subtitles_meta':list((md.get('subtitles') or {}).keys()),'auto_captions_meta':list((md.get('automatic_captions') or {}).keys())})
 except Exception as e:rec['metadata_error']=repr(e)
 subs=d/'subtitles';subs.mkdir(exist_ok=True);run(common+['--write-subs','--write-auto-subs','--sub-langs','ko.*,en.*','--sub-format','vtt','--skip-download','-o',str(subs/f'{tag}.%(ext)s'),url],logs/'yt_subtitles.log')
 tracks=[]
 try:
  from youtube_transcript_api import YouTubeTranscriptApi
  api=YouTubeTranscriptApi();tlist=api.list(vid)
  for tr in tlist:
   try:
    raw=tr.fetch().to_raw_data();lang=tr.language_code+('_generated' if tr.is_generated else '_manual');(subs/f'{tag}_{lang}.json').write_text(json.dumps(raw,ensure_ascii=False,indent=2),encoding='utf-8');(subs/f'{tag}_{lang}.txt').write_text('\n'.join(f"[{x.get('start',0):.3f}] {x.get('text','')}" for x in raw),encoding='utf-8');tracks.append(lang)
   except Exception as e:(logs/'transcript_api.log').open('a',encoding='utf-8').write(f'{tr.language_code}: {e!r}\n')
 except Exception as e:(logs/'transcript_api.log').write_text(repr(e),encoding='utf-8')
 # Reliable public transcript mirror fallback, preserving bracketed timestamps.
 target=f'https://youtube-transcript.ai/transcript/{vid}.txt?lang=a-ko'
 proxy='https://api.allorigins.win/raw?url='+quote(target,safe='')
 rec['thirdparty_transcript']=get(proxy,subs/f'{tag}_ko_auto_thirdparty.md',min_bytes=5000)
 rec['transcript_api_tracks']=tracks;rec['subtitle_files']=[p.name for p in subs.glob('*')]
 vd=d/'video';vd.mkdir(exist_ok=True);run(common+['-f','worst[height<=360]/worstvideo[height<=360]+worstaudio/worst','--no-playlist','-o',str(vd/f'{tag}.%(ext)s'),url],logs/'video.log')
 videos=[p for p in vd.glob(f'{tag}.*') if p.suffix.lower() in {'.mp4','.webm','.mkv'}]
 # Public media-info fallback for visual verification if YouTube blocks the runner IP.
 if not videos:
  try:
   info_url='https://weirddl.sbs/api/info?quality=360&url='+quote(f'https://youtu.be/{vid}',safe='')
   ir=requests.get(info_url,timeout=180,headers={'User-Agent':'Mozilla/5.0'});(logs/'weirddl.log').write_text(f'{ir.status_code}\n{ir.text[:5000]}',encoding='utf-8')
   if ir.status_code==200:
    info=ir.json();(d/f'{tag}_weirddl.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
    candidates=[m for m in info.get('media',[]) if m.get('hasVideo') and m.get('url')]
    if candidates:
     candidates.sort(key=lambda m:(m.get('height') or 9999,m.get('filesize') or 10**18));vp=vd/f'{tag}_proxy.mp4';rec['proxy_video']=stream_get(candidates[0]['url'],vp)
  except Exception as e:(logs/'weirddl.log').write_text(repr(e),encoding='utf-8')
  videos=[p for p in vd.glob('*') if p.suffix.lower() in {'.mp4','.webm','.mkv'}]
 if videos:
  vf=videos[0];frames=d/'frames_15s';frames.mkdir(exist_ok=True);run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(vf),'-vf','fps=1/15,scale=640:-2','-q:v','4',str(frames/'frame_%05d.jpg')],logs/'ffmpeg.log');rec['frames_15s']=len(list(frames.glob('*.jpg')));rec['video_bytes_temp']=vf.stat().st_size
  for p in videos:p.unlink(missing_ok=True)
 else:run(common+['--write-thumbnail','--skip-download','--convert-thumbnails','jpg','-o',str(d/f'{tag}.%(ext)s'),url],logs/'thumbnail.log')
 manifest.append(rec)
(ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8');(ROOT/'README.txt').write_text('Lecture 4-6 slide PDFs, public automatic-caption transcripts, metadata, and 15-second visual verification frames.\n',encoding='utf-8');print(json.dumps(manifest,ensure_ascii=False,indent=2))
