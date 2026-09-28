from __future__ import annotations
import asyncio,re,json
from pathlib import Path
import requests
from playwright.async_api import async_playwright
URLS={
'electro':'https://accuratescribe.ai/transcribe/share/4a2a26e5-5a63-4b8b-9c01-e1bb5385d9e3/n05freurcvuvb/260907-1',
'eis':'https://accuratescribe.ai/transcribe/share/e1d90393-e564-4eda-a091-bd28c782b2e3/oq33deknwq8x8/video-project',
'pemfc1':'https://accuratescribe.ai/transcribe/share/701851df-5d9f-4174-b81c-9b7a8bbd1a43/fu1i7pedxsx95/260914-2-pemfc',
'pemfc2':'https://accuratescribe.ai/transcribe/share/4c5e0485-968d-4ac3-9ecc-c53bd331b181/3o017sck57ecb/260916-2-pemfc'}
OUT=Path('probe_out');OUT.mkdir(exist_ok=True)
TS=re.compile(r'\((\d{1,2}:\d{2}(?::\d{2})?)\)\s*')
def parse(text):
 m=list(TS.finditer(text)); out=[]
 for i,x in enumerate(m):
  y=m[i+1].start() if i+1<len(m) else len(text)
  s=' '.join(text[x.end():y].split())
  if s: out.append((x.group(1),s))
 return out
async def main():
 async with async_playwright() as p:
  b=await p.chromium.launch(headless=True)
  ctx=await b.new_context(viewport={'width':1440,'height':1000})
  for name,url in URLS.items():
   page=await ctx.new_page(); responses=[]
   page.on('response',lambda r: responses.append((r.url,r.headers.get('content-type',''),r.status)))
   await page.goto(url,wait_until='networkidle',timeout=120000)
   for label in ['View Full Transcript','전체 스크립트 보기','Show more','더보기']:
    try:
     loc=page.get_by_text(label,exact=False)
     if await loc.count(): await loc.first.click(timeout=3000)
    except: pass
   for _ in range(20):
    await page.mouse.wheel(0,5000); await page.wait_for_timeout(200)
   body=await page.locator('body').inner_text(); html=await page.content()
   seg=parse(body)
   print('RESULT',name,'body',len(body),'segments',len(seg),'first',seg[:2],'last',seg[-2:])
   print('MEDIA',name,[u for u,ct,st in responses if 'video' in ct or '.mp4' in u or '.m3u8' in u][:10])
   (OUT/f'{name}_body.txt').write_text(body,encoding='utf-8')
   (OUT/f'{name}_segments.json').write_text(json.dumps(seg,ensure_ascii=False,indent=2),encoding='utf-8')
   (OUT/f'{name}_responses.json').write_text(json.dumps(responses,ensure_ascii=False,indent=2),encoding='utf-8')
   await page.close()
  await b.close()
if __name__=='__main__':asyncio.run(main())
