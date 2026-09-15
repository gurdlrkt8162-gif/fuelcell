#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

def safe(s:str)->str:
    return re.sub(r'[^A-Za-z0-9._-]+','_',s).strip('._') or 'dataset.zip'

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('dataset_id')
    ap.add_argument('version')
    ap.add_argument('--out',default='downloads')
    ap.add_argument('--timeout-ms',type=int,default=180000)
    args=ap.parse_args()
    url=f'https://data.mendeley.com/datasets/{args.dataset_id}/{args.version}'
    out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        ctx=browser.new_context(accept_downloads=True,user_agent='Mozilla/5.0 P1-P5 research data verifier')
        page=ctx.new_page()
        responses=[]
        def on_response(resp):
            u=resp.url
            if any(k in u.lower() for k in ('download','dataset','file')):
                responses.append({'url':u,'status':resp.status,'content_type':resp.headers.get('content-type'),'content_length':resp.headers.get('content-length')})
        page.on('response',on_response)
        page.goto(url,wait_until='networkidle',timeout=args.timeout_ms)
        for label in ('Accept All Cookies','Accept all cookies','I agree','Accept'):
            try:
                page.get_by_role('button',name=label,exact=False).first.click(timeout=1500)
                break
            except Exception:
                pass
        buttons=page.get_by_text('Download All',exact=False)
        if buttons.count()==0:
            (out/f'{args.dataset_id}_page.html').write_text(page.content(),encoding='utf-8')
            (out/f'{args.dataset_id}_network.json').write_text(json.dumps(responses,indent=2),encoding='utf-8')
            print('Download All button not found',file=sys.stderr)
            sys.exit(2)
        with page.expect_download(timeout=args.timeout_ms) as info:
            buttons.first.click()
        dl=info.value
        name=safe(dl.suggested_filename or f'{args.dataset_id}_v{args.version}.zip')
        target=out/name
        dl.save_as(str(target))
        failure=dl.failure()
        metadata={'dataset_id':args.dataset_id,'version':args.version,'page_url':url,
                  'suggested_filename':dl.suggested_filename,'saved_as':str(target),
                  'failure':failure,'network':responses}
        (out/f'{args.dataset_id}_download.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
        if failure:
            print(f'Download failure: {failure}',file=sys.stderr)
            sys.exit(3)
        print(target)
        browser.close()

if __name__=='__main__':
    main()
