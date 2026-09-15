#!/usr/bin/env python3
from __future__ import annotations
import csv, json, os, time
from pathlib import Path
import requests

SOURCES = [
('FC01','zenodo','19068126'),('FC02','zenodo','20715542'),
('FC03','mendeley','n5csdjfg3c','2'),('FC04','zenodo','13166135'),('FC05','zenodo','7054555'),
('FC06','mendeley','zdz65vcjzc','1'),('FC07','mendeley','mc46tw9t8m','1'),('FC08','mendeley','m9m2gmcr6k','1'),
('FC09','mendeley','4sfyzcc39j','1'),('FC10','zenodo','17905711'),
('FC11','direct','https://raw.githubusercontent.com/jianzuo/IEEE-2014-datasets/master/FC1_Ageing.csv','https://raw.githubusercontent.com/jianzuo/IEEE-2014-datasets/master/FC2_Ageing.csv'),
('FC12','mendeley','sp4pc8w9xh','1'),('FC13','mendeley','jy5vxystwd','1'),('FC14','mendeley','pn95bsbhv9','1'),
('FC15','mendeley','5wj6zj3sv4','1'),('FC16','zenodo','3631156'),
('FC17','direct','https://github.com/ECSIM/pem-dataset1/archive/refs/tags/v1.1.zip'),
('BAT01','direct','https://phm-datasets.s3.amazonaws.com/NASA/5.+Battery+Data+Set.zip'),
('BAT02','direct','https://phm-datasets.s3.amazonaws.com/NASA/11.+Randomized+Battery+Usage+Data+Set.zip'),
('BAT03','direct','https://web.calce.umd.edu/batteries/data/A123_OCV25-20120905.zip','https://web.calce.umd.edu/batteries/data/A123_DST-US06-FUDS-25.zip'),
('BAT04','direct','https://web.calce.umd.edu/batteries/data/CS2_33.zip','https://web.calce.umd.edu/batteries/data/CS2_36.zip','https://web.calce.umd.edu/batteries/data/CX2_16.zip'),
('BAT05','direct','https://ora.ox.ac.uk/objects/uuid:03ba4b01-cfed-46d3-9b1a-7d4a7bdf6fac'),
('BAT06','direct','https://data.matr.io/1/'),('BAT07','direct','https://data.matr.io/11/RawData.zip','https://data.matr.io/11/StructuredData.zip'),
('BAT08','mendeley','n3b54nsw8m','9'),('BAT09','mendeley','q4p8d7kfw4','1'),
('BAT10','zenodo','15422339'),('BAT11','zenodo','15755725'),('BAT12','direct','https://osf.io/j2sn4/'),
('BAT13','zenodo','7250553'),('BAT14','direct','https://osf.io/9ceav/'),('BAT15','zenodo','14555746'),
('BAT16','zenodo','15519550'),('BAT17','zenodo','14577286'),('BAT18','zenodo','18471156'),
('BAT19','direct','https://data.nasa.gov/dataset/randomized-and-recommissioned-battery-dataset'),
('SC01','zenodo','20271680'),('SC02','zenodo','19251491'),('SC02B','zenodo','19253322'),('SC02C','zenodo','19257191'),('SC02D','zenodo','19259456'),
('SC03','zenodo','20261313'),('SC04','zenodo','20326305'),('SC04B','zenodo','20324576'),('SC04C','zenodo','20324697'),('SC04D','zenodo','20326183'),
('MIS01','figshare','12683453'),('MIS02','figshare','21997787'),('MIS03','zenodo','11525490'),
('MIS04','mendeley','tf4ym6fsvc','1'),('MIS05','mendeley','ypt9mwg5nt','1'),
('BOP01','uci','791'),('BOP02','zenodo','3384388'),
('BOP03','direct','https://phm-datasets.s3.amazonaws.com/NASA/12.+Capacitor+Electrical+Stress.zip'),
('BOP04','mendeley','m268jsw339','3'),('BOP05','mendeley','x2hrn4vfrt','1'),('BOP06','mendeley','63gjxpn7s6','1'),
('BOP07','mendeley','zjspz5gffh','1'),('BOP08','mendeley','mn2wwp9r23','1')]

UA='P1-P5-public-data-audit/2026-09-15 (+research reproducibility)'
S=requests.Session(); S.headers.update({'User-Agent':UA,'Accept':'application/json, text/plain, */*'})

def get(url, **kw):
    last=None
    for a in range(5):
        try:
            r=S.get(url,timeout=60,allow_redirects=True,**kw)
            if r.status_code in (429,500,502,503,504):
                time.sleep(2**a); last=r; continue
            return r
        except requests.RequestException as e:
            last=e; time.sleep(2**a)
    if isinstance(last,requests.Response): return last
    raise last

def headish(url):
    try:
        r=S.head(url,timeout=45,allow_redirects=True)
        if r.status_code>=400 or 'content-length' not in r.headers:
            r=S.get(url,timeout=45,allow_redirects=True,headers={'Range':'bytes=0-0','User-Agent':UA},stream=True)
        return {'url':url,'status':r.status_code,'final_url':r.url,'size':int(r.headers.get('content-length','0') or 0),
                'content_type':r.headers.get('content-type'),'etag':r.headers.get('etag'),'content_range':r.headers.get('content-range')}
    except Exception as e:
        return {'url':url,'error':repr(e)}

def discover_zenodo(rec):
    r=get(f'https://zenodo.org/api/records/{rec}')
    out={'api_url':r.url,'status':r.status_code}
    if r.status_code!=200:
        out['body']=r.text[:1000]; return out
    j=r.json(); out['title']=j.get('metadata',{}).get('title'); out['access']=j.get('access',{}); out['license']=j.get('metadata',{}).get('rights') or j.get('metadata',{}).get('license')
    fs=[]
    for f in j.get('files',[]):
        links=f.get('links',{})
        fs.append({'name':f.get('key'),'size':f.get('size'),'checksum':f.get('checksum'),
                   'url':links.get('content') or links.get('self'),'mimetype':f.get('mimetype')})
    out['files']=fs; out['total_size']=sum((f.get('size') or 0) for f in fs); return out

def discover_mendeley(dsid,ver):
    endpoints=[
      f'https://data.mendeley.com/public-api/datasets/{dsid}/versions/{ver}/files',
      f'https://api.data.mendeley.com/datasets/{dsid}/versions/{ver}/files',
      f'https://data.mendeley.com/public-api/datasets/{dsid}/versions/{ver}'
    ]
    attempts=[]
    for u in endpoints:
        r=get(u); attempts.append({'url':u,'status':r.status_code,'content_type':r.headers.get('content-type'),'body':r.text[:500] if r.status_code!=200 else None})
        if r.status_code==200:
            try: j=r.json()
            except Exception: continue
            arr=j if isinstance(j,list) else j.get('files') or j.get('data') or []
            files=[]
            for f in arr:
                if not isinstance(f,dict): continue
                url=f.get('download_url') or f.get('downloadUrl') or f.get('url') or f.get('content_details',{}).get('download_url')
                name=f.get('filename') or f.get('name') or f.get('file_name') or f.get('id')
                size=f.get('size') or f.get('filesize') or f.get('file_size') or f.get('content_details',{}).get('size')
                files.append({'name':name,'size':size,'checksum':f.get('checksum') or f.get('md5'),'url':url,'raw':f})
            if files:
                return {'api_url':u,'status':200,'files':files,'total_size':sum(int(f.get('size') or 0) for f in files),'attempts':attempts}
    return {'status':'unresolved','attempts':attempts}

def discover_figshare(article):
    r=get(f'https://api.figshare.com/v2/articles/{article}')
    out={'api_url':r.url,'status':r.status_code}
    if r.status_code!=200: out['body']=r.text[:1000]; return out
    j=r.json(); fs=[]
    for f in j.get('files',[]): fs.append({'name':f.get('name'),'size':f.get('size'),'checksum':f.get('supplied_md5') or f.get('computed_md5'),'url':f.get('download_url')})
    out.update(title=j.get('title'),license=j.get('license'),files=fs,total_size=sum((f.get('size') or 0) for f in fs)); return out

def discover_uci(dsid):
    urls=[f'https://archive.ics.uci.edu/api/dataset?id={dsid}',f'https://archive.ics.uci.edu/static/public/{dsid}/metropt+3+dataset.zip']
    out={'attempts':[]}
    for u in urls:
        r=get(u,stream=True); out['attempts'].append({'url':u,'status':r.status_code,'content_type':r.headers.get('content-type'),'size':r.headers.get('content-length'),'final_url':r.url})
    out['files']=[{'name':'metropt+3+dataset.zip','url':urls[1],'size':None}]; return out

def main():
    root=Path('discovery'); root.mkdir(exist_ok=True)
    results=[]
    for src in SOURCES:
        did,kind,*args=src; print(f'[{did}] {kind} {args}',flush=True)
        try:
            if kind=='zenodo': d=discover_zenodo(args[0])
            elif kind=='mendeley': d=discover_mendeley(args[0],args[1])
            elif kind=='figshare': d=discover_figshare(args[0])
            elif kind=='uci': d=discover_uci(args[0])
            else: d={'files':[headish(u) for u in args]}; d['total_size']=sum(f.get('size') or 0 for f in d['files'])
            status='ok' if d.get('files') else 'no_files'
        except Exception as e:
            d={'error':repr(e)}; status='error'
        results.append({'id':did,'source':kind,'args':args,'discovery_status':status,'data':d})
    (root/'discovery.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    rows=[]
    for x in results:
        files=x['data'].get('files') or []
        if files:
            for f in files:
                rows.append({'id':x['id'],'source':x['source'],'status':x['discovery_status'],'name':f.get('name'),'size':f.get('size'),'checksum':f.get('checksum'),'url':f.get('url'),'content_type':f.get('content_type'),'http_status':f.get('status')})
        else: rows.append({'id':x['id'],'source':x['source'],'status':x['discovery_status'],'name':'','size':'','checksum':'','url':'','content_type':'','http_status':''})
    with (root/'files.csv').open('w',newline='',encoding='utf-8-sig') as fp:
        w=csv.DictWriter(fp,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    ok=sum(1 for x in results if x['discovery_status']=='ok')
    (root/'SUMMARY.md').write_text(f'# Source discovery\n\nResolved with files: **{ok}/{len(results)}**\n\nGenerated by GitHub Actions at commit {os.getenv("GITHUB_SHA","")}.\n',encoding='utf-8')
    print(f'Resolved {ok}/{len(results)}')

if __name__=='__main__': main()
