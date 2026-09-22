#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,zipfile,subprocess,io,re,requests,traceback
import numpy as np,pandas as pd,scipy.io as sio
from matio import load_from_mat
R=Path('candidate_bytes');O=Path('pemfc_final_qc');O.mkdir(exist_ok=True)
C=O/'canonical';C.mkdir(exist_ok=True)
def save(n,o):
 (O/n).write_text(json.dumps(o,ensure_ascii=False,indent=2,allow_nan=False,default=str),encoding='utf-8')
def fl(x):return float(x) if np.isfinite(x) else None
for level in range(3):
 for p in list(R.rglob('*')):
  if p.is_file() and p.suffix.lower() in ('.zip','.rar','.7z') and not p.with_name(p.name+'_unpacked').exists():
   q=p.with_name(p.name+'_unpacked');q.mkdir(exist_ok=True)
   t=subprocess.run(['7z','t',str(p)],capture_output=True,text=True,timeout=90)
   if t.returncode:raise ValueError('archive integrity '+str(p))
   subprocess.run(['7z','x','-y','-o'+str(q),str(p)],check=True,capture_output=True,timeout=90)

def stats(df):
 out={'rows':len(df),'cols':len(df.columns),'columns':[]}
 for i,n in enumerate(df.columns):
  a=pd.to_numeric(df.iloc[:,i],errors='coerce').to_numpy(dtype=float);v=a[np.isfinite(a)]
  s={'name':str(n),'nonfinite':int((~np.isfinite(a)).sum()),'unique':int(pd.Series(a).nunique()),'min':fl(v.min()) if len(v) else None,'max':fl(v.max()) if len(v) else None}
  if str(n)=='t':
   dt=np.diff(a);s['time']={'min_dt':fl(dt.min()),'max_dt':fl(dt.max()),'median_dt':fl(np.median(dt)),'negative_dt':int((dt<0).sum()),'zero_dt':int((dt==0).sum()),'span_s':fl(a[-1]-a[0])}
  out['columns'].append(s)
 out['duplicate_rows']=int(df.duplicated().sum())
 return out
rw=[]
for p in (R/'RWTH').rglob('*.mat'):
 out={'file':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 try:
  obj=load_from_mat(str(p),raw_data=False,add_table_attrs=True)
  out['top_types']={k:str(type(v)) for k,v in obj.items()}
  frames=[]
  def visit(x,name,depth=0):
   if depth>7:return
   if isinstance(x,pd.DataFrame):frames.append((name,x))
   elif isinstance(x,dict):
    out.setdefault('object_keys',{})[name]=list(x.keys())
    for k,v in x.items():visit(v,name+'.'+str(k),depth+1)
   elif isinstance(x,np.ndarray):
    out.setdefault('arrays',[]).append({'name':name,'shape':list(x.shape),'dtype':str(x.dtype)})
    if x.dtype.kind=='O' and x.size<200:
     for i,v in enumerate(x.ravel()):visit(v,name+f'[{i}]',depth+1)
  visit(obj,'root')
  out['frames']=[]
  for name,df in frames:
   pr=stats(df);pr['name']=name;pr['attrs']=str(df.attrs)[:12000]
   target=C/(p.stem+'_'+re.sub('[^A-Za-z0-9]','_',name)+'.csv');df.to_csv(target,index=False);pr['canonical']=str(target)
   if set(['DeltaT_cool_K','T_in_cool_gradC','T_out_cool_gradC']).issubset(df.columns):
    r=df['DeltaT_cool_K']-(df['T_out_cool_gradC']-df['T_in_cool_gradC']);pr['coolant_delta_check']={'max_abs_K':fl(np.abs(r).max()),'median_abs_K':fl(np.abs(r).median())}
   out['frames'].append(pr)
 except Exception as e:
  out['error']=str(e);out['trace']=traceback.format_exc()[-1500:]
  try:
   d=sio.loadmat(p,struct_as_record=False,squeeze_me=True);out['scipy_keys']={k:repr(v)[:3000] for k,v in d.items() if not k.startswith('__')}
  except Exception as e2:out['scipy_error']=str(e2)
 rw.append(out)
save('RWTH_TABLE_QC.json',rw)
# Test the known tabular-format discrepancy without claiming that a mismatch is a pass.
m=json.loads(Path('pemfc_candidate_audit/DIFFERENTIAL_source.json').read_text())
cond=[f for f in m['data']['latestVersion']['files'] if 'Operating_conditions' in f['label']]
cr=[]
for f in cond:
 d=f['dataFile'];rec={'metadata':d,'attempts':[]}
 for suffix in ('?format=original','?format=tab',''):
  u='https://entrepot.recherche.data.gouv.fr/api/access/datafile/'+str(d['id'])+suffix
  try:
   q=requests.get(u,timeout=40);q.raise_for_status();b=q.content
   rec['attempts'].append({'url':u,'bytes':len(b),'md5':hashlib.md5(b).hexdigest(),'sha256':hashlib.sha256(b).hexdigest(),'headers':dict(q.headers),'text':b.decode('utf-8',errors='replace'),'normalized_lf_md5':hashlib.md5(b.replace(b'\r\n',b'\n')).hexdigest(),'normalized_crlf_md5':hashlib.md5(b.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n')).hexdigest()})
  except Exception as e:rec['attempts'].append({'url':u,'error':str(e)})
 cr.append(rec)
save('DIFFERENTIAL_CONDITIONS_RESPONSE_QC.json',cr)
# Preserve raw numeric exports and create deterministic locale-normalized derivatives.
eis=[];iv=[];replacement_total=0
for p in (R/'DIFFERENTIAL').rglob('*.txt'):
 text=p.read_bytes().decode('utf-8-sig');lines=text.splitlines();header=lines[0].split('\t');vals=[];changes=[]
 for r,line in enumerate(lines[1:],start=2):
  if not line.strip():continue
  row=[]
  for c,tok in enumerate(line.split('\t')):
   s=tok.strip()
   if re.fullmatch(r'[+-]?\d+,\d+(?:[eE][+-]?\d+)?',s):changes.append({'line':r,'column':c+1,'original':s});s=s.replace(',','.')
   row.append(float(s))
  if len(row)!=len(header):raise ValueError('EIS/IV ragged row '+str(p))
  vals.append(row)
 df=pd.DataFrame(vals,columns=header);a=df.to_numpy(dtype=float);entry={'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'rows':len(df),'columns':header,'nonfinite':int((~np.isfinite(a)).sum()),'locale_replacements':len(changes),'replacements':changes[:20]}
 replacement_total+=len(changes)
 if 'freq/Hz' in df.columns:
  f=df['freq/Hz'].to_numpy();zr=df['Re(Z)/Ohm'].to_numpy();ni=df['-Im(Z)/Ohm'].to_numpy();mag=df['|Z|/Ohm'].to_numpy();phase=df['Phase(Z)/deg'].to_numpy()
  residual=np.abs(np.hypot(zr,ni)-mag)/np.maximum(mag,1e-12)
  ph=np.degrees(np.arctan2(-ni,zr));pr=(ph-phase+180)%360-180
  entry.update({'freq_min_Hz':float(f.min()),'freq_max_Hz':float(f.max()),'nonpositive_frequency':int((f<=0).sum()),'unique_freq':len(np.unique(f)),'nondecreasing_steps':int((np.diff(f)>=0).sum()),'negative_real_points':int((zr<0).sum()),'inductive_points':int((ni<0).sum()),'magnitude_relative_error_max':float(residual.max()),'phase_error_deg_max':float(np.abs(pr).max()),'voltage_mean_V':float(df['Ewe/V'].mean()),'current_mean_A':float(df['I/A'].mean()),'KK_status':'NOT_PERFORMED','stationarity_linearity_status':'NOT_INDEPENDENTLY_VALIDATED'})
  eis.append(entry)
 else:iv.append(entry)
 outdir=C/'DIFFERENTIAL';outdir.mkdir(exist_ok=True);df.to_csv(outdir/p.with_suffix('.csv').name,index=False)
save('DIFFERENTIAL_EIS_QC.json',eis);save('DIFFERENTIAL_IV_QC.json',iv)
save('DIFFERENTIAL_QC_SUMMARY.json',{'eis_files':len(eis),'iv_files':len(iv),'eis_rows':sum(x['rows'] for x in eis),'iv_rows':sum(x['rows'] for x in iv),'nonfinite':sum(x['nonfinite'] for x in eis+iv),'locale_replacements':replacement_total,'magnitude_relative_error_max':max(x['magnitude_relative_error_max'] for x in eis),'phase_error_deg_max':max(x['phase_error_deg_max'] for x in eis),'negative_real_total':sum(x['negative_real_points'] for x in eis),'eis_semantics':'Header-mapped: Ewe V first, I A second; stored minus imaginary; no invented frequencies. Format normalization only. No KK/DRT acceptance.'})
# Multi-channel diagnostic data integrity; missing units stay missing.
l=[]
for p in (R/'LOUGH2016').rglob('*.xls'):
 if 'sensor measurement' not in str(p):continue
 df=pd.read_excel(p,sheet_name=0,header=None);st=stats(df);st['file']=p.name
 st['rows_all_constant']=False;l.append(st)
save('LOUGH2016_SENSOR_QC.json',l)
save('LOUGH2016_QC_SUMMARY.json',{'files':len(l),'rows':sum(x['rows'] for x in l),'cols':sorted(set(x['cols'] for x in l)),'nonfinite':sum(c['nonfinite'] for x in l for c in x['columns']),'normal_files':sum(x['file'].startswith('normal') for x in l),'faulty_files':sum(x['file'].startswith('faulty') for x in l),'unknown_files':sum(x['file'].startswith('unknown') for x in l),'limitations':['No timestamp column in 20-column array','Sensor dictionary names channels but omits engineering units','No voltage channel among the 20 documented channels','Unknown diagnosis predictions are not independently observed ground truth']})
# Numerical subset already summarized: no need to infer physical meanings.
ox=json.loads(Path('pemfc_semantic_audit/OXYGEN_PURGE_OVERVIEW.json').read_text());save('OXYGEN_FILE_SUMMARY.json',[{k:v for k,v in x.items() if k in ['path','bytes','sheets','mat_variables','error']} for x in ox])
print('FINAL_QC_COMPLETE',flush=True)
with zipfile.ZipFile('PEMFC_FOCUSED_QC_EVIDENCE.zip','w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
 for p in O.rglob('*'):
  if p.is_file():z.write(p,p)
