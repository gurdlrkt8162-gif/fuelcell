#!/usr/bin/env python3
"""Public-only discovery and bounded inspection; NO scientific acceptance is automatic.
No private documents, account tokens or user research are sent to data providers.
"""
from pathlib import Path
import json, time, re, hashlib, zipfile, io, traceback
import requests
from playwright.sync_api import sync_playwright

ROOT=Path('pemfc_candidate_audit'); ROOT.mkdir(exist_ok=True)
S=requests.Session(); S.headers['User-Agent']='PEMFC-public-data-quality-audit/1.0'
CATALOG=[]

def save(name, obj):
    (ROOT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')

def getjson(url):
    r=S.get(url,timeout=(20,60)); r.raise_for_status(); return r.json()

def bounded_file(tag,f):
    size=f.get('size'); url=f.get('download_url') or f.get('url')
    if not url or not size or size>16000000: return {'state':'NOT_DOWNLOADED_SIZE_GATE'}
    r=S.get(url,stream=True,timeout=(20,90));r.raise_for_status()
    b=bytearray()
    for c in r.iter_content(262144):
        b.extend(c)
        if len(b)>16000000: raise ValueError('stream exceeds audit sample byte gate')
    if len(b)!=int(size): raise ValueError(f'byte mismatch {len(b)} != {size}')
    b=bytes(b); sha=hashlib.sha256(b).hexdigest();md5=hashlib.md5(b).hexdigest()
    want=f.get('checksum') or f.get('supplied_md5') or f.get('computed_md5')
    if want and str(want).startswith('md5:'): want=want[4:]
    match=(md5==want) if want else None
    if match is False: raise ValueError('provider checksum mismatch')
    name=f.get('name') or f.get('key') or 'data'
    out={'state':'BYTES','name':name,'bytes':len(b),'sha256':sha,'md5':md5,'provider_checksum_match':match,'content_type':r.headers.get('Content-Type'),'final_url':r.url}
    if b.lstrip().lower().startswith((b'<!doctype html',b'<html')): raise ValueError('HTML not data')
    if zipfile.is_zipfile(io.BytesIO(b)):
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            out['zip_bad_member']=z.testzip();out['members']=[{'name':x.filename,'bytes':x.file_size} for x in z.infolist()]
            out['text_previews']={x.filename:z.read(x).decode('utf-8',errors='replace')[:16000] for x in z.infolist() if x.file_size<120000 and x.filename.lower().endswith(('.txt','.md','.csv'))}
    elif name.lower().endswith(('.csv','.txt','.md')):
        out['text']=b.decode('utf-8-sig',errors='replace')[:22000]
    save(tag+'__'+re.sub('[^A-Za-z0-9._-]','_',name)+'.inspection.json',out)
    return out

for typ,tag,id_ in [('zenodo','HAEOLUS','11395583'),('figshare','LOUGH2016','4009959'),('figshare','LOUGH2018','5759667')]:
    try:
        url=f'https://zenodo.org/api/records/{id_}' if typ=='zenodo' else f'https://api.figshare.com/v2/articles/{id_}'
        j=getjson(url);save(tag+'_source.json',j)
        if typ=='zenodo':
            fs=[{'name':f['key'],'size':f['size'],'checksum':f.get('checksum'),'url':f['links'].get('content') or f['links'].get('self')} for f in j['files']]
            meta=j.get('metadata',{})
        else: fs=j.get('files',[]);meta={k:j.get(k) for k in ('title','doi','license','description','references')}
        row={'tag':tag,'source_url':url,'metadata':meta,'files':fs,'inspections':[]}
        for f in fs:
            try: row['inspections'].append(bounded_file(tag,f))
            except Exception as e: row['inspections'].append({'file':f.get('name'),'error':str(e)})
        CATALOG.append(row)
    except Exception as e: CATALOG.append({'tag':tag,'error':str(e)})

try:
    url='https://entrepot.recherche.data.gouv.fr/api/datasets/:persistentId/?persistentId=doi:10.57745/YLCIPH'
    j=getjson(url);save('DIFFERENTIAL_source.json',j)
    fs=j.get('data',{}).get('latestVersion',{}).get('files',[])
    CATALOG.append({'tag':'DIFFERENTIAL','source_url':url,'files':fs,'metadata':j.get('data',{}).get('latestVersion',{}).get('metadataBlocks',{})})
except Exception as e: CATALOG.append({'tag':'DIFFERENTIAL','error':str(e)})

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    for tag,id_,ver in [('RWTH','mc46tw9t8m','1'),('OXYGEN_PURGE','jy5vxystwd','2'),('TWO_SYSTEM_FAULT','m9m2gmcr6k','1'),('NPL_CO','sp4pc8w9xh','1')]:
        row={'tag':tag,'url':f'https://data.mendeley.com/datasets/{id_}/{ver}','network_json':[],'links':[]}
        ctx=browser.new_context(accept_downloads=False);page=ctx.new_page()
        def onresp(resp):
            if 'public-api' not in resp.url: return
            if resp.status==200 and 'json' in resp.headers.get('content-type',''):
                try:
                    js=resp.json()
                    if len(json.dumps(js))<1500000: row['network_json'].append({'url':resp.url,'body':js})
                except Exception: pass
        page.on('response',onresp)
        try:
            page.goto(row['url'],wait_until='domcontentloaded',timeout=90000)
            page.wait_for_timeout(12000)
            row['page_text']=page.locator('body').inner_text(timeout=10000)
            row['links']=page.locator('a').evaluate_all('(els)=>els.map(e=>({text:e.innerText,url:e.href}))')
            scripts=page.locator('script').all_text_contents()
            row['embedded_state']=[s[:250000] for s in scripts if any(k in s for k in ('__NEXT_DATA__','INITIAL_STATE','download_url','content_details'))]
        except Exception as e: row['error']=str(e)
        save(tag+'_browser.json',row)
        CATALOG.append({'tag':tag,'page_text':row.get('page_text','')[:20000],'metadata_response_urls':[x['url'] for x in row['network_json']],'error':row.get('error')})
        ctx.close()
    browser.close()
save('CATALOG.json',CATALOG)
for x in CATALOG:
    print('\nCANDIDATE',x['tag'],json.dumps({k:v for k,v in x.items() if k!='inspections'},ensure_ascii=False)[:18000],flush=True)
print('METADATA_AND_BOUNDED_BYTE_INSPECTION_COMPLETE; NOT SCIENTIFICALLY_APPROVED')
