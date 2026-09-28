from __future__ import annotations
import asyncio,json,sys
from pathlib import Path
from playwright.async_api import async_playwright
sys.path.insert(0,str(Path(__file__).parent))
from hydrogen_transcript_probe import URLS
OUT=Path('export_probe_out');OUT.mkdir(exist_ok=True)
async def main():
 async with async_playwright() as p:
  b=await p.chromium.launch(headless=True)
  ctx=await b.new_context(accept_downloads=True,viewport={'width':1440,'height':1100})
  for name,url in URLS.items():
   page=await ctx.new_page(); reqs=[]
   def record_request(r):
    try:reqs.append({'method':r.method,'url':r.url})
    except Exception as e:reqs.append({'error':repr(e)})
   page.on('request',record_request)
   await page.goto(url,wait_until='domcontentloaded',timeout=120000);await page.wait_for_timeout(3000)
   buttons=await page.locator('button').all_inner_texts()
   links=await page.locator('a').evaluate_all("els=>els.map(e=>({text:e.innerText,href:e.href}))")
   print('PAGE',name,'buttons',buttons,'links',links[:50])
   (OUT/f'{name}_buttons.json').write_text(json.dumps(buttons,ensure_ascii=False,indent=2),encoding='utf-8')
   (OUT/f'{name}_links.json').write_text(json.dumps(links,ensure_ascii=False,indent=2),encoding='utf-8')
   for label in ['View Full Transcript','전체 스크립트 보기','Show Full Transcript','Show more','더보기']:
    try:
     loc=page.get_by_text(label,exact=False)
     if await loc.count():
      print('CLICK FULL',name,label,await loc.count());await loc.first.click(timeout=5000);await page.wait_for_timeout(1500)
    except Exception as e: print('FULL ERR',name,label,repr(e))
   for label in ['TXT','SRT','VTT','JSON','DOCX','PDF']:
    try:
     loc=page.get_by_text(label,exact=True)
     if not await loc.count(): loc=page.locator(f'button:has-text("{label}")')
     if await loc.count():
      print('TRY EXPORT',name,label,await loc.count())
      try:
       async with page.expect_download(timeout=7000) as di: await loc.first.click()
       dl=await di.value; path=OUT/f'{name}_{label}_{dl.suggested_filename}'
       await dl.save_as(str(path));print('DOWNLOADED',path,path.stat().st_size)
      except Exception as e:
       print('NO DOWNLOAD',name,label,repr(e));await page.wait_for_timeout(1000)
       body=await page.locator('body').inner_text();(OUT/f'{name}_{label}_body.txt').write_text(body,encoding='utf-8')
    except Exception as e: print('EXPORT ERR',name,label,repr(e))
   body=await page.locator('body').inner_text()
   (OUT/f'{name}_final_body.txt').write_text(body,encoding='utf-8')
   (OUT/f'{name}_requests.json').write_text(json.dumps(reqs,ensure_ascii=False,indent=2),encoding='utf-8')
   print('FINAL BODY',name,len(body),body[:300].replace('\n',' | '),body[-300:].replace('\n',' | '))
   await page.close()
  await b.close()
if __name__=='__main__':asyncio.run(main())
