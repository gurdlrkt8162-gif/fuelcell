#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,requests,zipfile,subprocess,re,io,contextlib
import numpy as np,pandas as pd
from matio import load_from_mat
R=Path('candidate_bytes'); O=Path('pemfc_complete_qc');O.mkdir(exist_ok=True);C=O/'canonical';C.mkdir(exist_ok=True)
def save(n,x):(O/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False,default=str),encoding='utf-8')
def num(x):return float(x) if np.isfinite(x) else None
for level in range(3):
 for p in list(R.rglob('*')):
  if p.is_file() and p.suffix.lower() in ('.zip','.rar','.7z') and not p.with_name(p.name+'_unpacked').exists():
   q=p.with_name(p.name+'_unpacked');q.mkdir(exist_ok=True)
   t=subprocess.run(['7z','t',str(p)],capture_output=True,text=True,timeout=90)
   if t.returncode:raise ValueError('archive integrity failed '+str(p))
   subprocess.run(['7z','x','-y','-o'+str(q),str(p)],capture_output=True,check=True,timeout=90)
# MATLAB class tables: use a reader that supports the class, not scipy's struct fallback.
rw=[]
for p in sorted((R/'RWTH').rglob('*.mat')):
 a={'file':p.name,'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 try:
  d=load_from_mat(str(p),raw_data=False,add_table_attrs=True);frames=[x for x in d.values() if isinstance(x,pd.DataFrame)];assert len(frames)==1;df=frames[0]
  a.update({'rows':len(df),'cols':len(df.columns),'channels':list(df.columns),'column_stats':[]})
  for k in df:
   v=pd.to_numeric(df[k],errors='coerce').to_numpy(dtype=float);valid=v[np.isfinite(v)]
   a['column_stats'].append({'name':k,'nonfinite':int((~np.isfinite(v)).sum()),'min':num(valid.min()) if len(valid) else None,'max':num(valid.max()) if len(valid) else None})
  a['nonfinite_total']=sum(x['nonfinite'] for x in a['column_stats']);t=df.t.to_numpy();dt=np.diff(t)
  a['time']={'start_s':num(t[0]),'end_s':num(t[-1]),'median_dt_s':num(np.median(dt)),'min_dt_s':num(dt.min()),'max_dt_s':num(dt.max()),'duplicate_dt':int((dt==0).sum()),'negative_dt':int((dt<0).sum())}
  a['exact_duplicate_rows']=int(df.duplicated().sum())
  rr=df.DeltaT_cool_K-(df.T_out_cool_gradC-df.T_in_cool_gradC);a['coolant_delta_max_abs_K']=num(np.abs(rr).max())
  den=df.i_dens_A_cm2*df.U_st_V;ok=(den>0)&np.isfinite(den);ratio=df.loc[ok,'P_st_kW']*1000/den[ok]
  a['P_over_jU_cm2']={'median':num(ratio.median()),'min':num(ratio.min()),'max':num(ratio.max())}
  a['stack_energy_integral_kWh']=num(np.trapezoid(df.P_st_kW,t)/3600)
  out=C/'RWTH';out.mkdir(exist_ok=True);df.to_csv(out/(p.stem+'.csv'),index=False)
 except Exception as e:a['error']=str(e)
 rw.append(a)
save('RWTH_QC.json',rw)
save('RWTH_SUMMARY.json',{'files':[{'file':a['file'],'rows':a.get('rows'),'cols':a.get('cols'),'time':a.get('time'),'nonfinite_total':a.get('nonfinite_total'),'P_over_jU_cm2':a.get('P_over_jU_cm2'),'error':a.get('error')} for a in rw],'total_rows':sum(a.get('rows',0) for a in rw),'total_nonfinite':sum(a.get('nonfinite_total',0) for a in rw),'errors':sum('error' in a for a in rw),'mixed_signal_warning':'Record includes measurements, derived variables and model states. Internal states are not independently measured labels. U_st_V is cell-scale voltage in the author plotting code despite stack-voltage README label.'})
# Dataverse's checksum refers to the original XLSX, not ingested TAB size.
m=json.loads(Path('pemfc_candidate_audit/DIFFERENTIAL_source.json').read_text());flist=m['data']['latestVersion']['files'];f=next(f for f in flist if 'Operating_conditions' in f['label']);d=f['dataFile'];u='https://entrepot.recherche.data.gouv.fr/api/access/datafile/'+str(d['id'])+'?format=original';res=requests.get(u,timeout=50);res.raise_for_status();b=res.content
assert len(b)==d['originalFileSize'];assert hashlib.md5(b).hexdigest()==d['md5'];p=R/'DIFFERENTIAL'/d['originalFileName'];p.write_bytes(b)
x=pd.read_excel(p,header=None)
save('CONDITIONS_VERIFIED.json',{'url':u,'bytes':len(b),'md5':d['md5'],'provider_md5_match':True,'sha256':hashlib.sha256(b).hexdigest(),'original_name':d['originalFileName'],'cells':x.fillna('').astype(str).values.tolist()})
from impedance.validation import linKK
from impedance.models.circuits.elements import circuit_elements
circuit_elements['np']=np
qc=[];header_sets={};kk=[]
for p in sorted((R/'DIFFERENTIAL').rglob('*.txt')):
 rec={'file':str(p.relative_to(R/'DIFFERENTIAL')),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'md5':hashlib.md5(p.read_bytes()).hexdigest()}
 try:
  text=p.read_bytes().decode('utf-8-sig');lines=text.splitlines();headers=[h.strip().replace('−','-') for h in lines[0].split('\t')]
  # Normalise spaces only, without changing physical identity, unit or sign.
  norm=[re.sub(r'\s+','',h).lower() for h in headers];header_sets[str(headers)]=header_sets.get(str(headers),0)+1
  values=[];replacements=0
  for line in lines[1:]:
   if not line.strip():continue
   toks=line.split('\t');assert len(toks)==len(headers), 'ragged row';row=[]
   for tok in toks:
    tok=tok.strip()
    if re.fullmatch(r'[+-]?\d+,\d+(?:[eE][+-]?\d+)?',tok):tok=tok.replace(',','.');replacements+=1
    row.append(float(tok))
   values.append(row)
  a=np.array(values);df=pd.DataFrame(a,columns=headers);rec.update({'rows':len(df),'cols':len(headers),'headers':headers,'nonfinite':int((~np.isfinite(a)).sum()),'locale_replacements':replacements})
  expected=next((z['dataFile'].get('md5') for z in flist if z['dataFile']['filename']==p.name),None)
  rec['provider_md5_match']=(rec['md5']==expected) if expected else None
  out=C/'DIFFERENTIAL';out.mkdir(exist_ok=True);df.to_csv(out/p.with_suffix('.csv').name,index=False)
  if any('freq' in n for n in norm):
   rec['kind']='EIS'
   def ix(match):
    found=[i for i,n in enumerate(norm) if match(n)]
    if len(found)!=1:raise ValueError('unresolved header '+str(headers))
    return found[0]
   fi=ix(lambda n:n.startswith('freq/') and n.endswith('hz'));ri=ix(lambda n:n.startswith('re(z)/') and n.endswith('ohm'));ii=ix(lambda n:'im(z)' in n and n.endswith('ohm'))
   mi=next((i for i,n in enumerate(norm) if n.startswith('|z|/')),None);pi=next((i for i,n in enumerate(norm) if n.startswith('phase(z)/')),None)
   freq=a[:,fi];real=a[:,ri];imag=a[:,ii]*(-1 if norm[ii].startswith('-') else 1);z=real+1j*imag
   rec.update({'freq_min_Hz':num(freq.min()),'freq_max_Hz':num(freq.max()),'unique_freq':int(len(np.unique(freq))),'negative_real_points':int((real<0).sum()),'inductive_points':int((imag>0).sum()),'imaginary_sign':norm[ii],'magnitude_relative_error_max':num((np.abs(np.abs(z)-a[:,mi])/np.maximum(a[:,mi],1e-12)).max()) if mi is not None else None})
   if pi is not None:rec['phase_error_deg_max']=num(np.abs((np.degrees(np.angle(z))-a[:,pi]+180)%360-180).max())
   if len(freq)>40 and np.isfinite(z).all() and (freq>0).all():
    try:
     with contextlib.redirect_stdout(io.StringIO()):M,mu,zfit,_,_=linKK(freq,z,c=.85,max_M=40,fit_type='complex',add_cap=False)
     rr=np.abs(z-zfit)/np.maximum(np.abs(z),1e-15);rms=np.sqrt(np.mean(rr**2));mx=rr.max()
     kk.append({'file':rec['file'],'M':int(M),'mu':num(mu),'rms_relative':num(rms),'max_relative':num(mx),'screen_pass':bool(rms<=.01 and mx<=.05)})
    except Exception as e:kk.append({'file':rec['file'],'error':str(e)})
  else:rec['kind']='IV'
 except Exception as e:rec['error']=str(e)
 qc.append(rec)
save('DIFFERENTIAL_FILE_QC.json',qc);save('DIFFERENTIAL_HEADERS.json',header_sets)
save('DIFFERENTIAL_SUMMARY.json',{'files':len(qc),'eis':sum(x.get('kind')=='EIS' for x in qc),'iv':sum(x.get('kind')=='IV' for x in qc),'rows':sum(x.get('rows',0) for x in qc),'nonfinite':sum(x.get('nonfinite',0) for x in qc),'provider_md5_matches':sum(x.get('provider_md5_match') is True for x in qc),'locale_replacements':sum(x.get('locale_replacements',0) for x in qc),'errors':[{'file':x['file'],'error':x['error']} for x in qc if 'error' in x],'negative_real_points':sum(x.get('negative_real_points',0) for x in qc),'max_magnitude_relative_error':max((x.get('magnitude_relative_error_max') or 0 for x in qc))})
save('LINKK_FULL_BAND.json',{'settings':{'c':.85,'max_M':40,'fit_type':'complex','add_cap':False,'band':'all original frequencies','heuristic_rms_limit':.01,'heuristic_max_limit':.05},'results':kk,'pass_count':sum(x.get('screen_pass',False) for x in kk),'errors':sum('error' in x for x in kk),'caveat':'Heuristic screen only, not proof of stationarity/linearity. No point deletion, no frequency-band selection.'})
# Hash every original and build reproducible audit artifact (not an approval).
with zipfile.ZipFile('PEMFC_COMPLETE_QC_EVIDENCE.zip','w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
 for p in O.rglob('*'):
  if p.is_file():z.write(p,p)
 z.write(R/'DIFFERENTIAL'/d['originalFileName'],R/'DIFFERENTIAL'/d['originalFileName'])
print('COMPLETE_QC_OUTPUT_WRITTEN; read failures and limitations before source admission')
