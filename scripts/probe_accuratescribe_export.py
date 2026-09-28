#!/usr/bin/env python3
from pathlib import Path
import json, re, time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

URL='https://accuratescribe.ai/transcribe/share/4a2a26e5-5a63-4b8b-9c01-e1bb5385d9e3/n05freurcvuvb/260907-1'
out=Path('export_probe'); out.mkdir(exist_ok=True)
responses=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    ctx=browser.new_context(accept_downloads=True,viewport={'width':1440,'height':1800},locale='ko-KR')
    page=ctx.new_page()
    def on_response(resp):
        try:
            ct=(resp.headers.get('content-type') or '').lower()
            if any(k in resp.url.lower() for k in ['export','download','transcript','subtitle','srt','vtt','json','txt']) or any(k in ct for k in ['json','text/plain','octet-stream','subtitle']):
                body=''
                try: body=resp.text()[:200000]
                except Exception: pass
                responses.append({'url':resp.url,'status':resp.status,'content_type':ct,'body':body})
        except Exception: pass
    page.on('response',on_response)
    page.goto(URL,wait_until='domcontentloaded',timeout=120000)
    page.wait_for_timeout(6000)
    (out/'before.txt').write_text(page.locator('body').inner_text(),encoding='utf-8')
    for label in ['Export','TXT','SRT','VTT','JSON','DOCX','PDF']:
        try:
            loc=page.get_by_text(label,exact=True)
            if not loc.count():
                loc=page.get_by_text(label,exact=False)
            if not loc.count():
                continue
            try:
                with page.expect_download(timeout=10000) as di:
                    loc.first.click(timeout=5000)
                dl=di.value
                path=out/(label.lower()+'_'+dl.suggested_filename)
                dl.save_as(str(path))
                print('download',label,path,path.stat().st_size)
            except PlaywrightTimeoutError:
                try:
                    loc.first.click(timeout=5000)
                    page.wait_for_timeout(3000)
                except Exception as e:
                    print('clickfail',label,e)
            except Exception as e:
                print('error',label,e)
        except Exception as e:
            print('outer',label,e)
    (out/'after.txt').write_text(page.locator('body').inner_text(),encoding='utf-8')
    (out/'after.html').write_text(page.content(),encoding='utf-8')
    (out/'responses.json').write_text(json.dumps(responses,ensure_ascii=False,indent=2),encoding='utf-8')
    page.screenshot(path=str(out/'after.png'),full_page=True)
    browser.close()
