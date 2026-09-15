#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
from playwright.sync_api import sync_playwright

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('url'); ap.add_argument('--out',default='page-inspection'); ap.add_argument('--timeout-ms',type=int,default=180000)
    args=ap.parse_args(); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True); ctx=b.new_context(user_agent='Mozilla/5.0 public academic data verifier'); page=ctx.new_page()
        net=[]
        page.on('response',lambda r: net.append({'url':r.url,'status':r.status,'content_type':r.headers.get('content-type'),'length':r.headers.get('content-length')}))
        page.goto(args.url,wait_until='networkidle',timeout=args.timeout_ms)
        for label in ('Accept All Cookies','Accept all cookies','I agree','Accept'):
            try: page.get_by_role('button',name=label,exact=False).first.click(timeout=1500); break
            except Exception: pass
        page.wait_for_timeout(1500)
        links=page.locator('a').evaluate_all("els => els.map((e,i)=>({i,text:(e.innerText||e.textContent||'').trim(),href:e.href,download:e.getAttribute('download'),title:e.title})).filter(x=>x.text||x.href)")
        buttons=page.locator('button').evaluate_all("els => els.map((e,i)=>({i,text:(e.innerText||e.textContent||'').trim(),title:e.title,aria:e.getAttribute('aria-label'),disabled:e.disabled}))")
        inputs=page.locator('input').evaluate_all("els => els.map((e,i)=>({i,type:e.type,name:e.name,value:e.value,aria:e.getAttribute('aria-label'),placeholder:e.placeholder}))")
        (out/'page.html').write_text(page.content(),encoding='utf-8')
        (out/'links.json').write_text(json.dumps(links,ensure_ascii=False,indent=2),encoding='utf-8')
        (out/'buttons.json').write_text(json.dumps(buttons,ensure_ascii=False,indent=2),encoding='utf-8')
        (out/'inputs.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2),encoding='utf-8')
        (out/'network.json').write_text(json.dumps(net,ensure_ascii=False,indent=2),encoding='utf-8')
        page.screenshot(path=str(out/'page.png'),full_page=True)
        print('TITLE',page.title())
        print('LINKS')
        for x in links: print(x)
        print('BUTTONS')
        for x in buttons: print(x)
        b.close()
if __name__=='__main__': main()
