#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, hashlib, json, re, time, zipfile
from pathlib import Path
from urllib.parse import urlparse
import requests

UA='P1-P5-OSF-public-data-verifier/2026-09-15'
S=requests.Session(); S.headers.update({'User-Agent':UA,'Accept':'application/vnd.api+json, application/json'})

def get(url,stream=False):
    last=None
    for a in range(6):
        try:
            r=S.get(url,timeout=(45,300),allow_redirects=True,stream=stream)
            if r.status_code in (429,500,502,503,504): last=r; time.sleep(2**a); continue
            return r
        except requests.RequestException as e: last=e; time.sleep(2**a)
    if isinstance(last,requests.Response): return last
    raise last

def safe(s):
    s=(s or 'file').replace('\\','_').replace('/','_')
    return re.sub(r'[\x00-\x1f<>:"|?*]+','_',s)[:220]

def sha256(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
    return h.hexdigest()

def download(url,dest,expected=None):
    dest.parent.mkdir(parents=True,exist_ok=True); tmp=dest.with_suffix(dest.suffix+'.part')
    if tmp.exists(): tmp.unlink()
    r=get(url,stream=True)
    if r.status_code!=200: raise RuntimeError(f'HTTP {r.status_code} {url}')
    ctype=(r.headers.get('content-type') or '').lower()
    if 'text/html' in ctype: raise RuntimeError(f'HTML response for {url}')
    n=0
    with tmp.open('wb') as f:
        for c in r.iter_content(8*1024*1024):
            if c: f.write(c); n+=len(c)
    if expected and int(expected)!=n: raise RuntimeError(f'size mismatch {n}!={expected}')
    tmp.replace(dest)
    if zipfile.is_zipfile(dest):
        with zipfile.ZipFile(dest) as z:
            bad=z.testzip()
            if bad: raise RuntimeError(f'bad zip member {bad}')
    return {'size':n,'sha256':sha256(dest),'content_type':ctype,'final_url':r.url}

def paged(url):
    while url:
        r=get(url)
        if r.status_code!=200: raise RuntimeError(f'OSF API HTTP {r.status_code}: {r.text[:500]}')
        j=r.json()
        for x in j.get('data') or []: yield x
        url=(j.get('links') or {}).get('next')

def walk(url,prefix=''):
    for x in paged(url):
        a=x.get('attributes') or {}; links=x.get('links') or {}; rel=x.get('relationships') or {}
        kind=a.get('kind')
        name=safe(a.get('name') or x.get('id'))
        path=f'{prefix}/{name}'.strip('/')
        if kind=='file':
            yield {'path':path,'name':name,'size':a.get('size'),'date_modified':a.get('date_modified'),'resource_id':x.get('id'),'download_url':links.get('download'),'raw':x}
        elif kind=='folder':
            child=(((rel.get('files') or {}).get('links') or {}).get('related') or {}).get('href')
            if child: yield from walk(child,path)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('node'); ap.add_argument('--id',required=True); ap.add_argument('--out',default='bundle')
    args=ap.parse_args(); root=Path(args.out)/args.id; root.mkdir(parents=True,exist_ok=True)
    providers=list(paged(f'https://api.osf.io/v2/nodes/{args.node}/files/'))
    files=[]
    for p in providers:
        rel=p.get('relationships') or {}; href=(((rel.get('files') or {}).get('links') or {}).get('related') or {}).get('href')
        provider=(p.get('attributes') or {}).get('name') or p.get('id')
        if href:
            for f in walk(href,safe(provider)): files.append(f)
    (root/'SOURCE_METADATA.json').write_text(json.dumps({'node':args.node,'providers':providers,'files':files},ensure_ascii=False,indent=2),encoding='utf-8')
    rows=[]; errors=[]
    for f in files:
        try:
            dest=root/'original'/f['path']
            result=download(f['download_url'],dest,f.get('size'))
            row={'id':args.id,'node':args.node,'path':str(dest.relative_to(root)),'source_path':f['path'],'source_url':f['download_url'],**result}
            rows.append(row); print('verified',f['path'],result['size'],flush=True)
        except Exception as e:
            errors.append({'file':f,'error':repr(e)}); print('ERROR',f['path'],e,flush=True)
    (root/'VERIFICATION.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    (root/'ERRORS.json').write_text(json.dumps(errors,ensure_ascii=False,indent=2),encoding='utf-8')
    with (root/'VERIFICATION.csv').open('w',newline='',encoding='utf-8-sig') as fp:
        keys=sorted({k for r in rows for k in r}) or ['id']; w=csv.DictWriter(fp,fieldnames=keys); w.writeheader(); w.writerows(rows)
    (root/'SHA256SUMS.txt').write_text(''.join(f"{r['sha256']}  {r['path']}\n" for r in rows),encoding='utf-8')
    (root/'README.md').write_text(f"# {args.id}\n\nOSF node: {args.node}\nVerified files: {len(rows)}\nErrors: {len(errors)}\n",encoding='utf-8')
    if errors or not rows: raise SystemExit(4)

if __name__=='__main__': main()
