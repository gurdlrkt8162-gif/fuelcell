#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, hashlib, json, os, re, shutil, sys, time, zipfile
from pathlib import Path
from urllib.parse import unquote, urlparse
import requests

UA='P1-P5-public-data-downloader/2026-09-15 (+reproducible academic research)'
S=requests.Session(); S.headers.update({'User-Agent':UA,'Accept':'application/json, text/plain, */*'})

SOURCES={
 'FC01':('zenodo','19068126'),'FC02':('zenodo','20715542'),'FC04':('zenodo','13166135'),'FC05':('zenodo','7054555'),
 'FC11':('direct',[('FC1_Ageing.csv','https://raw.githubusercontent.com/jianzuo/IEEE-2014-datasets/master/FC1_Ageing.csv'),('FC2_Ageing.csv','https://raw.githubusercontent.com/jianzuo/IEEE-2014-datasets/master/FC2_Ageing.csv'),('IEEE-Challenge-Details.pdf','https://raw.githubusercontent.com/jianzuo/IEEE-2014-datasets/master/IEEE-Challenge-Details.pdf')]),
 'FC16':('zenodo','3631156'),'FC17':('direct',[('pem-dataset1-v1.1.zip','https://github.com/ECSIM/pem-dataset1/archive/refs/tags/v1.1.zip')]),
 'BAT01':('direct',[('NASA_Battery_Data_Set.zip','https://phm-datasets.s3.amazonaws.com/NASA/5.+Battery+Data+Set.zip')]),
 'BAT02':('direct',[('NASA_Randomized_Battery_Usage_Data_Set.zip','https://phm-datasets.s3.amazonaws.com/NASA/11.+Randomized+Battery+Usage+Data+Set.zip')]),
 'BAT03':('direct',[('A123_OCV25-20120905.zip','https://web.calce.umd.edu/batteries/data/A123_OCV25-20120905.zip'),('A123_DST-US06-FUDS-25.zip','https://web.calce.umd.edu/batteries/data/A123_DST-US06-FUDS-25.zip')]),
 'BAT04':('direct',[('CS2_33.zip','https://web.calce.umd.edu/batteries/data/CS2_33.zip'),('CS2_36.zip','https://web.calce.umd.edu/batteries/data/CS2_36.zip'),('CX2_16.zip','https://web.calce.umd.edu/batteries/data/CX2_16.zip')]),
 'BAT10':('zenodo','15422339'),'BAT11':('zenodo','15755725'),'BAT13':('zenodo','7250553'),'BAT15':('zenodo','14555746'),
 'BAT16':('zenodo','15519550'),'BAT18':('zenodo','18471156'),
 'SC01':('zenodo','20271680'),'SC02':('zenodo','19251491'),'SC02B':('zenodo','19253322'),'SC02C':('zenodo','19257191'),'SC02D':('zenodo','19259456'),
 'SC03':('zenodo','20261313'),'SC04':('zenodo','20326305'),'SC04B':('zenodo','20324576'),'SC04C':('zenodo','20324697'),'SC04D':('zenodo','20326183'),
 'MIS01':('figshare','12683453'),'MIS02':('figshare','21997787'),'MIS03':('zenodo','11525490'),
 'BOP01':('direct',[('metropt+3+dataset.zip','https://archive.ics.uci.edu/static/public/791/metropt+3+dataset.zip')]),
}
GROUPS={
 'fuelcell-core':['FC01','FC02','FC04','FC05','FC11','FC16','FC17'],
 'battery-a':['BAT01','BAT03','BAT04','BAT10','BAT13','BAT15','BAT16','BAT18'],
 'battery-b':['BAT02','BAT11'],
 'supercap-a':['SC01','SC02','SC02B','SC02C','SC02D','SC04','SC04B','SC04C','SC04D'],
 'supercap-b':['SC03'],
 'missions':['MIS01','MIS02','MIS03'],
 'bop':['BOP01'],
}

def req(url, *, stream=False, headers=None):
    last=None
    for attempt in range(6):
        try:
            r=S.get(url,stream=stream,timeout=(45,300),allow_redirects=True,headers=headers)
            if r.status_code in (429,500,502,503,504):
                last=r; time.sleep(min(60,2**attempt)); continue
            return r
        except requests.RequestException as e:
            last=e; time.sleep(min(60,2**attempt))
    if isinstance(last,requests.Response): return last
    raise last

def safe_name(name:str)->str:
    name=unquote(name or 'download')
    name=name.replace('\\','_').replace('/','_').strip()
    name=re.sub(r'[\x00-\x1f<>:"|?*]+','_',name)
    return name[:220] or 'download'

def checksum_spec(value):
    if not value: return None,None
    v=str(value).strip()
    if ':' in v:
        a,h=v.split(':',1); return a.lower(),h.lower()
    if re.fullmatch(r'[0-9a-fA-F]{32}',v): return 'md5',v.lower()
    if re.fullmatch(r'[0-9a-fA-F]{64}',v): return 'sha256',v.lower()
    return None,None

def resolve(id_):
    kind,arg=SOURCES[id_]
    if kind=='zenodo':
        r=req(f'https://zenodo.org/api/records/{arg}')
        if r.status_code!=200: raise RuntimeError(f'Zenodo {arg}: HTTP {r.status_code}: {r.text[:300]}')
        j=r.json(); files=[]
        for f in j.get('files',[]):
            links=f.get('links') or {}
            files.append({'name':f.get('key'),'url':links.get('content') or links.get('self'),'size':f.get('size'),'checksum':f.get('checksum'),'mimetype':f.get('mimetype')})
        return {'id':id_,'kind':kind,'record':arg,'landing_url':f'https://zenodo.org/records/{arg}','metadata':j.get('metadata',{}),'access':j.get('access',{}),'files':files}
    if kind=='figshare':
        r=req(f'https://api.figshare.com/v2/articles/{arg}')
        if r.status_code!=200: raise RuntimeError(f'Figshare {arg}: HTTP {r.status_code}: {r.text[:300]}')
        j=r.json(); files=[]
        for f in j.get('files',[]):
            files.append({'name':f.get('name'),'url':f.get('download_url'),'size':f.get('size'),'checksum':f.get('supplied_md5') or f.get('computed_md5')})
        return {'id':id_,'kind':kind,'record':arg,'landing_url':j.get('url_public_api') or f'https://figshare.com/articles/dataset/{arg}','metadata':{k:j.get(k) for k in ('title','description','doi','license','published_date','modified_date')},'files':files}
    files=[{'name':n,'url':u,'size':None,'checksum':None} for n,u in arg]
    return {'id':id_,'kind':kind,'record':None,'landing_url':files[0]['url'] if files else None,'metadata':{},'files':files}

def hash_file(path:Path,alg='sha256'):
    h=hashlib.new(alg)
    with path.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
    return h.hexdigest()

def inspect_file(path:Path):
    with path.open('rb') as f: head=f.read(512)
    result={'magic_hex':head[:32].hex(),'zip_test':'not_zip','readability':'not_tested'}
    low=head.lower().lstrip()
    if low.startswith(b'<!doctype html') or low.startswith(b'<html') or b'<html' in low[:200]:
        raise RuntimeError(f'HTML response saved as data: {path}')
    if zipfile.is_zipfile(path):
        result['zip_test']='opening'
        with zipfile.ZipFile(path) as z:
            bad=z.testzip()
            result['zip_entries']=len(z.infolist()); result['zip_bad_entry']=bad; result['zip_test']='pass' if bad is None else 'fail'
            if bad is not None: raise RuntimeError(f'Corrupt ZIP {path}; first bad entry {bad}')
    elif path.suffix.lower() in ('.csv','.txt','.tsv','.names','.md'):
        with path.open('rb') as f: sample=f.read(65536)
        try:
            text=sample.decode('utf-8-sig')
        except UnicodeDecodeError:
            text=sample.decode('latin-1')
        result['readability']='pass'; result['first_line']=text.splitlines()[0][:500] if text.splitlines() else ''
    elif path.suffix.lower()=='.mat':
        result['readability']='binary-mat'; result['mat_v73_hdf5']=head.startswith(b'\x89HDF')
    else:
        result['readability']='binary'
    return result

def download_file(url:str,dest:Path,expected_size=None,expected_checksum=None):
    dest.parent.mkdir(parents=True,exist_ok=True)
    tmp=dest.with_suffix(dest.suffix+'.part')
    if tmp.exists(): tmp.unlink()
    r=req(url,stream=True)
    if r.status_code!=200: raise RuntimeError(f'HTTP {r.status_code} for {url}: {r.text[:300] if not r.raw.closed else ""}')
    ctype=(r.headers.get('content-type') or '').lower()
    if 'text/html' in ctype: raise RuntimeError(f'HTML content type for {url}')
    total=0
    with tmp.open('wb') as f:
        for chunk in r.iter_content(chunk_size=8*1024*1024):
            if chunk: f.write(chunk); total+=len(chunk)
    if total<=0: raise RuntimeError(f'Empty download: {url}')
    if expected_size not in (None,'',0,'0') and int(expected_size)!=total:
        raise RuntimeError(f'Size mismatch {dest.name}: got {total}, expected {expected_size}')
    alg,want=checksum_spec(expected_checksum)
    got_provider=None
    if alg and want:
        got_provider=hash_file(tmp,alg)
        if got_provider.lower()!=want.lower(): raise RuntimeError(f'{alg} mismatch {dest.name}: got {got_provider}, expected {want}')
    tmp.replace(dest)
    details=inspect_file(dest)
    sha=hash_file(dest,'sha256')
    return {'url':url,'final_url':r.url,'http_status':r.status_code,'content_type':ctype,'size':total,'provider_checksum':expected_checksum,'provider_checksum_verified':bool(alg and want),'computed_provider_checksum':got_provider,'sha256':sha,**details}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--group',choices=GROUPS)
    ap.add_argument('--ids',nargs='*')
    ap.add_argument('--out',default='bundle')
    args=ap.parse_args()
    ids=args.ids or GROUPS[args.group]
    root=Path(args.out); root.mkdir(parents=True,exist_ok=True)
    resolved=[]; verification=[]; errors=[]; seen_provider={}; seen_sha={}
    for id_ in ids:
        print(f'== {id_} ==',flush=True)
        try:
            rec=resolve(id_); resolved.append(rec)
            d=root/id_; (d/'original').mkdir(parents=True,exist_ok=True)
            (d/'SOURCE_METADATA.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
            for index,f in enumerate(rec.get('files') or [],1):
                if not f.get('url'):
                    errors.append({'id':id_,'name':f.get('name'),'error':'missing download URL'}); continue
                name=safe_name(f.get('name') or urlparse(f['url']).path.rsplit('/',1)[-1] or f'file_{index}')
                alg,want=checksum_spec(f.get('checksum'))
                pkey=f'{alg}:{want}' if alg and want else None
                if pkey and pkey in seen_provider:
                    ptr={'duplicate_of':seen_provider[pkey],'provider_checksum':f.get('checksum'),'size':f.get('size'),'source_url':f.get('url')}
                    (d/f'{name}.DUPLICATE_POINTER.json').write_text(json.dumps(ptr,indent=2),encoding='utf-8')
                    verification.append({'id':id_,'name':name,'status':'deduplicated-provider-checksum',**ptr})
                    continue
                dest=d/'original'/name
                try:
                    result=download_file(f['url'],dest,f.get('size'),f.get('checksum'))
                    if result['sha256'] in seen_sha:
                        other=seen_sha[result['sha256']]
                        dest.unlink()
                        ptr={'duplicate_of':other,'sha256':result['sha256'],'size':result['size'],'source_url':f.get('url')}
                        (d/f'{name}.DUPLICATE_POINTER.json').write_text(json.dumps(ptr,indent=2),encoding='utf-8')
                        verification.append({'id':id_,'name':name,'status':'deduplicated-sha256',**ptr})
                    else:
                        rel=str(dest.relative_to(root)); seen_sha[result['sha256']]=rel
                        if pkey: seen_provider[pkey]=rel
                        verification.append({'id':id_,'name':name,'path':rel,'status':'verified',**result})
                        print(f"  verified {name}: {result['size']} bytes",flush=True)
                except Exception as e:
                    errors.append({'id':id_,'name':name,'url':f.get('url'),'error':repr(e)})
                    print(f'  ERROR {name}: {e}',file=sys.stderr,flush=True)
        except Exception as e:
            errors.append({'id':id_,'error':repr(e)})
            print(f'ERROR resolving {id_}: {e}',file=sys.stderr,flush=True)
    (root/'RESOLVED_SOURCES.json').write_text(json.dumps(resolved,ensure_ascii=False,indent=2),encoding='utf-8')
    (root/'VERIFICATION.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2),encoding='utf-8')
    (root/'ERRORS.json').write_text(json.dumps(errors,ensure_ascii=False,indent=2),encoding='utf-8')
    with (root/'VERIFICATION.csv').open('w',newline='',encoding='utf-8-sig') as fp:
        keys=sorted({k for row in verification for k in row}) or ['id','status']
        w=csv.DictWriter(fp,fieldnames=keys,extrasaction='ignore'); w.writeheader(); w.writerows(verification)
    with (root/'SHA256SUMS.txt').open('w',encoding='utf-8') as fp:
        for row in verification:
            if row.get('status')=='verified': fp.write(f"{row['sha256']}  {row['path']}\n")
    summary=f"# Verified public data group\n\nGroup: `{args.group or 'custom'}`\n\nRequested dataset IDs: {', '.join(ids)}\n\nVerified physical files: {sum(r.get('status')=='verified' for r in verification)}\n\nExact duplicate pointers: {sum(str(r.get('status','')).startswith('deduplicated') for r in verification)}\n\nErrors: {len(errors)}\n"
    (root/'README.md').write_text(summary,encoding='utf-8')
    print(summary)
    if errors:
        raise SystemExit(4)

if __name__=='__main__': main()
