#!/usr/bin/env python3
"""Candidate data admission audit. Candidate bytes are NOT automatically approved.
Only public datasets are downloaded. Existing data and main branch remain untouched.
"""
from pathlib import Path
from urllib.parse import urlparse,urljoin
import requests,json,hashlib,zipfile,subprocess,io,re,traceback,csv,os
import numpy as np
import pandas as pd
import scipy.io as sio
import h5py
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

ROOT=Path('candidate_bytes');E=Path('pemfc_numeric_audit');ROOT.mkdir(exist_ok=True);E.mkdir(exist_ok=True)
S=requests.Session();S.headers['User-Agent']='Public PEMFC scientific data audit (research)'
REC=[]; TOTAL=0

def write(name,obj):
    (E/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False,default=str),encoding='utf-8')

def download(url,path,size=None,checksum=None):
    global TOTAL
    path.parent.mkdir(parents=True,exist_ok=True)
    r=S.get(url,stream=True,timeout=(20,120));r.raise_for_status()
    p=path.with_name(path.name+'.part');n=0;sha=hashlib.sha256();md5=hashlib.md5();first=b''
    with p.open('wb') as f:
        for c in r.iter_content(1024*1024):
            if not first:first=c[:1000]
            n+=len(c);TOTAL+=len(c)
            if n>140_000_000 or TOTAL>450_000_000: raise ValueError('bounded download budget exceeded; NOT downloaded')
            f.write(c);sha.update(c);md5.update(c)
    if first.lstrip().lower().startswith((b'<html',b'<!doctype html')):raise ValueError('HTML response')
    if size is not None and n!=int(size):raise ValueError('provider size mismatch')
    match=None
    if checksum:
        a,want=checksum.split(':',1) if ':' in checksum else ('md5',checksum)
        actual=sha.hexdigest() if a.lower()=='sha256' else md5.hexdigest()
        match=actual.lower()==want.lower()
        if not match:raise ValueError('provider checksum mismatch')
    p.replace(path)
    rec={'url':url,'path':str(path),'size':n,'sha256':sha.hexdigest(),'md5':md5.hexdigest(),'provider_checksum':checksum,'provider_checksum_match':match,'content_type':r.headers.get('content-type')}
    REC.append(rec);return rec

def unpack(path):
    target=path.parent/(path.name+'_unpacked');target.mkdir(exist_ok=True)
    test=subprocess.run(['7z','t',str(path)],capture_output=True,text=True,timeout=90)
    if test.returncode!=0:raise ValueError('archive test failed '+test.stdout[-1500:]+test.stderr[-500:])
    listing=subprocess.run(['7z','l','-slt',str(path)],capture_output=True,text=True,timeout=60).stdout
    for line in listing.splitlines():
        if line.startswith('Path = '):
            n=line[7:]
            if n==str(path):continue
            if n.startswith(('/', '\\')) or '..' in Path(n.replace('\\','/')).parts:raise ValueError('unsafe archive path')
    res=subprocess.run(['7z','x','-y',f'-o{target}',str(path)],capture_output=True,text=True,timeout=90)
    if res.returncode!=0:raise ValueError('archive extraction failed '+res.stdout[-1000:])
    return target

def number(v):
    try:return float(v) if np.isfinite(float(v)) else None
    except Exception:return None

def dfprofile(df):
    result={'rows':len(df),'columns':len(df.columns),'headers':[str(x) for x in df.columns], 'column_stats':[]}
    for i in range(len(df.columns)):
        s=df.iloc[:,i];nums=pd.to_numeric(s,errors='coerce');finite=np.isfinite(nums.to_numpy(dtype=float));vals=nums[finite]
        row={'name':str(df.columns[i]),'missing':int(s.isna().sum()),'numeric_count':int(finite.sum()),'unique':int(s.nunique()),'min':number(vals.min()),'max':number(vals.max()),'mean':number(vals.mean()),'examples':[str(x) for x in s.head(4)]}
        if ('time' in str(df.columns[i]).lower() or i==0) and len(vals)>2:
            d=np.diff(nums.to_numpy(dtype=float));d=d[np.isfinite(d)]
            row['diff']={'zero':int((d==0).sum()),'negative':int((d<0).sum()),'median':number(np.median(d)),'min':number(np.min(d)),'max':number(np.max(d))}
        result['column_stats'].append(row)
    result['duplicate_rows']=int(df.duplicated().sum())
    return result

def describe_mat(x,depth=0):
    if depth>5:return {'type':str(type(x))}
    if isinstance(x,dict):return {k:describe_mat(v,depth+1) for k,v in x.items() if not k.startswith('__')}
    if hasattr(x,'_fieldnames'):return {k:describe_mat(getattr(x,k),depth+1) for k in x._fieldnames}
    if isinstance(x,np.ndarray):
        out={'shape':list(x.shape),'dtype':str(x.dtype)}
        if x.dtype.names:out['fields']={k:describe_mat(x[k],depth+1) for k in x.dtype.names}
        elif x.dtype.kind in 'biufc':
            if x.dtype.kind=='c':out['complex']=True
            else:
                a=x.astype(float);ok=np.isfinite(a);out.update({'nonfinite':int((~ok).sum()),'min':number(a[ok].min()) if ok.any() else None,'max':number(a[ok].max()) if ok.any() else None})
                if a.ndim<=2 and a.size and max(a.shape)<=250000 and min(a.shape or [0])<=120 and a.size<6000000:
                    a=a.reshape(-1,1) if a.ndim==1 else a
                    if a.shape[0]<a.shape[1] and a.shape[0]<=120:a=a.T
                    out['tabular_numeric_profile']=dfprofile(pd.DataFrame(a))
        elif x.dtype.kind in 'US':out['values']=x.ravel()[:120].tolist()
        elif x.dtype.kind=='O':out['first_elements']=[describe_mat(v,depth+1) for v in x.ravel()[:5]]
        return out
    if isinstance(x,(int,float,np.number)):return number(x)
    return str(x)[:1000]

def inspect(path):
    out={'path':str(path),'size':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()};suffix=path.suffix.lower()
    try:
        if suffix in ('.7z','.rar','.zip'):
            t=unpack(path);out['archive_test']='PASS';out['members']=[{'path':str(p.relative_to(t)),'size':p.stat().st_size} for p in t.rglob('*') if p.is_file()]
        elif suffix=='.mat':
            try:
                d=sio.loadmat(path,squeeze_me=True,struct_as_record=False);out['mat']=describe_mat(d)
            except NotImplementedError:
                with h5py.File(path) as f:
                    ds=[]
                    f.visititems(lambda n,o: ds.append({'name':n,'shape':list(o.shape),'dtype':str(o.dtype)}) if isinstance(o,h5py.Dataset) else None)
                    out['hdf5_datasets']=ds
        elif suffix in ('.xlsx','.xls'):
            x=pd.ExcelFile(path);out['sheets']={n:dfprofile(pd.read_excel(path,sheet_name=n)) for n in x.sheet_names}
        elif suffix in ('.txt','.csv','.dat','.asc','.m','.md','.names'):
            text=path.read_bytes().decode('utf-8-sig',errors='replace');out['text_preview']=text[:18000];out['line_count']=len(text.splitlines())
            if suffix not in ('.md','.m','.names') and len(text.splitlines())>5:
                try:
                    if suffix=='.csv':df=pd.read_csv(path,sep=None,engine='python')
                    else:df=pd.read_csv(io.StringIO(text),sep='\t',engine='python')
                    if len(df.columns)>1:out['table']=dfprofile(df)
                except Exception as e:out['table_error']=str(e)
        else:out['state']='unparsed_filetype'
    except Exception as e:out['error']=str(e)
    return out

# Public full archives for two useful but not yet accepted Mendeley candidates.
for tag,id_,ver in [('RWTH','mc46tw9t8m','1'),('OXYGEN_PURGE','jy5vxystwd','2')]:
    try:
        meta=json.loads(Path(f'pemfc_candidate_audit/{tag}_browser.json').read_text())
        link=next(x['url'] for x in meta['links'] if 'Download All' in x['text'])
        download(link,ROOT/tag/(id_+'.zip'))
    except Exception as e:REC.append({'tag':tag,'error':str(e)})
# Institutional raw diagnostic sources.
for tag in ('LOUGH2016','LOUGH2018'):
    try:
        meta=json.loads(Path(f'pemfc_candidate_audit/{tag}_source.json').read_text())
        for f in meta['files']:
            download(f['download_url'],ROOT/tag/f['name'],f['size'],f.get('supplied_md5'))
    except Exception as e:REC.append({'tag':tag,'error':str(e)})
# All original differential-cell files; individually compare provider MD5.
try:
    meta=json.loads(Path('pemfc_candidate_audit/DIFFERENTIAL_source.json').read_text())
    for f in meta['data']['latestVersion']['files']:
        d=f['dataFile']
        if f.get('restricted'):raise ValueError('restricted file not accepted')
        download('https://entrepot.recherche.data.gouv.fr/api/access/datafile/'+str(d['id'])+'?format=original',ROOT/'DIFFERENTIAL'/f.get('directoryLabel','')/d['filename'],d['filesize'],d.get('md5'))
except Exception as e:REC.append({'tag':'DIFFERENTIAL','error':str(e)})
# Discover supplementary archive from the primary publisher; no inferred download URLs.
try:
    url='https://www.mdpi.com/2306-5729/5/2/47'
    r=S.get(url,timeout=45);r.raise_for_status();soup=BeautifulSoup(r.text,'html.parser')
    links=[{'text':a.get_text(' ',strip=True),'url':urljoin(url,a.get('href',''))} for a in soup.find_all('a',href=True)]
    write('SEVILLA_publisher_links.json',links)
    raw=[x for x in links if re.search(r'\.(rar|zip)(\?|$)',x['url'],re.I)]
    for i,x in enumerate(raw):download(x['url'],ROOT/'SEVILLA'/('supplement'+str(i)+('.rar' if '.rar' in x['url'].lower() else '.zip')))
except Exception as e:REC.append({'tag':'SEVILLA','error':str(e)})
# Inspect published Tongji availability, without using the private draft token in the paper.
try:
    u='https://data.mendeley.com/public-api/datasets/w65jjt8v5w/versions';r=S.get(u,timeout=45)
    write('TONGJI_availability.json',{'url':u,'status':r.status_code,'text':r.text[:16000]})
except Exception as e:REC.append({'tag':'TONGJI','error':str(e)})
# Unpack recursively within a fixed depth, then parse every numeric/text file.
for depth in range(3):
    archives=[p for p in ROOT.rglob('*') if p.is_file() and p.suffix.lower() in ('.7z','.rar','.zip') and not p.with_name(p.name+'_unpacked').exists()]
    if not archives:break
    for p in archives:
        try:unpack(p)
        except Exception as e:REC.append({'path':str(p),'unpack_error':str(e)})
for tag in [p for p in ROOT.iterdir() if p.is_dir()]:
    profiles=[]
    for p in tag.rglob('*'):
        if not p.is_file():continue
        if p.stat().st_size>140000000:profiles.append({'path':str(p),'state':'SKIP_SIZE'});continue
        profile=inspect(p);profiles.append(profile)
        # Preserve full small readmes and channel dictionaries for manual scientific audit.
        if p.suffix.lower() in ('.txt','.md','.m','.names') and (p.stat().st_size<60000):
            name=re.sub('[^A-Za-z0-9._-]','_',str(p.relative_to(tag)))
            (E/(tag.name+'__'+name)).write_text(p.read_bytes().decode('utf-8-sig',errors='replace'),encoding='utf-8')
    write(tag.name+'_profiles.json',profiles)
    brief=[{k:v for k,v in r.items() if k in ('path','size','sha256','error','archive_test','members','mat','hdf5_datasets','sheets','table','table_error')} for r in profiles]
    write(tag.name+'_numeric.json',brief)
    print(tag.name,'FILES',len(profiles),'ERRORS',sum('error' in x for x in profiles),flush=True)
write('DOWNLOAD_RECEIPTS.json',REC)
write('SUMMARY.json',{'downloaded_bytes':TOTAL,'download_records':len(REC),'download_errors':[x for x in REC if 'error' in x or 'unpack_error' in x],'status':'FILES_PARSED_MANUAL_SCIENTIFIC_REVIEW_REQUIRED'})
# Consolidated original payload for possible later approval, not yet a research admission.
with zipfile.ZipFile('PEMFC_CANDIDATE_RAW_NOT_APPROVED.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=3) as z:
    for p in ROOT.rglob('*'):
        if p.is_file() and '_unpacked' not in str(p) and not p.name.endswith('.part'):z.write(p,p)
    for p in E.rglob('*'):
        if p.is_file():z.write(p,p)
print('AUDIT_DONE; NO AUTOMATIC SCIENTIFIC APPROVAL',flush=True)
