#!/usr/bin/env python3
"""Reproducible source-format corrections; raw bytes are never edited."""
from pathlib import Path
import json,hashlib,requests,io,contextlib
import numpy as np,pandas as pd
# Execute the earlier audit with the precise input-header variation accommodated.
s=Path('scripts/pemfc_final_qc_20260922.py').read_text()
s=s.replace("header=lines[0].split('\\t')", "header=[h.strip().replace('−','-') for h in lines[0].split('\\t')]")
old="f=df['freq/Hz'].to_numpy();zr=df['Re(Z)/Ohm'].to_numpy();ni=df['-Im(Z)/Ohm'].to_numpy();mag=df['|Z|/Ohm'].to_numpy();phase=df['Phase(Z)/deg'].to_numpy()"
new="""fh=next(h for h in df.columns if h.lower().startswith('freq/')); rh=next(h for h in df.columns if h.lower().startswith('re(z)/')); ih=next(h for h in df.columns if 'im(z)' in h.lower()); mh=next(h for h in df.columns if h.lower().startswith('|z|/')); phh=next(h for h in df.columns if h.lower().startswith('phase(z)/'))
  f=df[fh].to_numpy();zr=df[rh].to_numpy();ni=df[ih].to_numpy()*(1 if ih.startswith('-') else -1);mag=df[mh].to_numpy();phase=df[phh].to_numpy();entry['imaginary_header']=ih"""
assert old in s
s=s.replace(old,new)
exec(compile(s,'source_specific_corrected_numeric_audit','exec'),{})
O=Path('pemfc_final_qc');R=Path('candidate_bytes')
def save(n,o):(O/n).write_text(json.dumps(o,ensure_ascii=False,indent=2,allow_nan=False,default=str),encoding='utf-8')
# The tabular dataset's MD5 refers to the ORIGINAL XLSX, not the transformed tab export.
m=json.loads(Path('pemfc_candidate_audit/DIFFERENTIAL_source.json').read_text());f=next(x for x in m['data']['latestVersion']['files'] if 'Operating_conditions' in x['label']);d=f['dataFile']
u='https://entrepot.recherche.data.gouv.fr/api/access/datafile/'+str(d['id'])+'?format=original'
r=requests.get(u,timeout=50);r.raise_for_status();b=r.content
assert len(b)==d['originalFileSize'];assert hashlib.md5(b).hexdigest()==d['md5']
p=R/'DIFFERENTIAL'/d['originalFileName'];p.write_bytes(b)
x=pd.read_excel(p,header=None);x.to_csv(O/'canonical'/'DIFFERENTIAL'/'Operating_conditions_Cell.csv',index=False,header=False)
save('CONDITIONS_VERIFIED.json',{'url':u,'path':str(p),'original_bytes':len(b),'provider_md5':d['md5'],'provider_md5_match':True,'sha256':hashlib.sha256(b).hexdigest(),'sheet_rows':len(x),'sheet_cols':len(x.columns),'rows':x.fillna('').astype(str).values.tolist(),'explanation':'Dataverse ingested .tab filesize differs from original XLSX. originalFileSize and originalFileName are used. Original MD5 matches. No data repair.'})
# Compact RWTH evidence table with no assertion that model states are sensor measurements.
rw=json.loads((O/'RWTH_TABLE_QC.json').read_text());brief=[]
for a in rw:
 for q in a.get('frames',[]):
  cols={v['name']:v for v in q['columns']};row={'file':Path(a['file']).name,'rows':q['rows'],'columns':q['cols'],'nonfinite':sum(v['nonfinite'] for v in q['columns']),'time':cols['t'].get('time'),'power_kW_range':[cols['P_st_kW']['min'],cols['P_st_kW']['max']],'voltage_reported_V_range':[cols['U_st_V']['min'],cols['U_st_V']['max']],'current_density_range':[cols['i_dens_A_cm2']['min'],cols['i_dens_A_cm2']['max']],'coolant_delta_check':q.get('coolant_delta_check'),'source_sha256':a['sha256']}
  frame=pd.read_csv(q['canonical'],float_precision='round_trip')
  denom=frame['i_dens_A_cm2']*frame['U_st_V'];idx=(denom>0)&np.isfinite(denom);ratio=frame.loc[idx,'P_st_kW']*1000/denom[idx]
  row['P_over_j_U_ratio_cm2']={'median':float(ratio.median()),'min':float(ratio.min()),'max':float(ratio.max()),'interpretation':'Algebraic consistency only; does NOT independently establish cell count or total stack voltage.'}
  # Per-row operating quantities, not a causal efficiency comparison.
  time=frame['t'].to_numpy();row['energy_kWh_Pst_integral']=float(np.trapezoid(frame['P_st_kW'],time)/3600)
  brief.append(row)
save('RWTH_COMPACT_QC.json',{'files':brief,'total_rows':sum(x['rows'] for x in brief),'voltage_semantic_correction':'README calls U_st_V stack voltage but author plot_U labels U_cell, and values are cell-scale. Preserve raw name; use as reported cell-level voltage, never total stack V. No supplier-scale transfer.','mixed_signal_warning':'Recorded raw signals and calculated quantities are mixed. Internal partial pressures, catalyst-layer concentrations, membrane hydration/temperature are NOT approved measured ground truth.','unqualified':['FCS net efficiency and measured tank consumption','Cold start/shutdown/standby cycle costs','Absolute RUL','250 kW module qualification','Pure-oxygen AIP qualification']})
# Lin-KK: fixed full-frequency settings, no deleting bad points or choosing a band after seeing results.
from impedance.validation import linKK
from impedance.models.circuits.elements import circuit_elements
circuit_elements['np']=np # compatibility fix documented by upstream for NumPy 2 scalar repr
results=[]
for p in sorted((O/'canonical'/'DIFFERENTIAL').glob('*.csv')):
 if '_EIS_' not in p.stem and 'EIS' not in p.stem:continue
 df=pd.read_csv(p);df.columns=[str(x).strip() for x in df.columns]
 try:
  fh=next(h for h in df.columns if h.lower().startswith('freq/'));rh=next(h for h in df.columns if h.lower().startswith('re(z)/'));ih=next(h for h in df.columns if 'im(z)' in h.lower())
  f=df[fh].to_numpy();z=df[rh].to_numpy()+1j*df[ih].to_numpy()*(-1 if ih.startswith('-') else 1)
  if not np.isfinite(z).all() or not np.all(f>0):raise ValueError('invalid input')
  with contextlib.redirect_stdout(io.StringIO()):M,mu,zfit,rr,ri=linKK(f,z,c=0.85,max_M=40,fit_type='complex',add_cap=False)
  res=np.abs((z-zfit)/np.maximum(np.abs(z),1e-15));r={'file':p.name,'points':len(f),'M':int(M),'mu':float(mu),'rms_relative':float(np.sqrt(np.mean(res**2))),'max_relative':float(res.max()),'fraction_gt_1pct':float((res>0.01).mean()),'screen_pass_rms1pct_max5pct':bool(np.sqrt(np.mean(res**2))<=0.01 and res.max()<=0.05),'interpretation':'Heuristic audit screen, not a universal EIS standard or proof of linearity/stationarity'}
  results.append(r)
 except Exception as e:results.append({'file':p.name,'error':str(e)})
save('EIS_LINKK_FULL_BAND.json',{'settings':{'c':0.85,'max_M':40,'fit_type':'complex','add_cap':False,'band':'all original positive frequencies; no exclusions'},'results':results,'pass_count':sum(x.get('screen_pass_rms1pct_max5pct',False) for x in results),'errors':sum('error' in x for x in results),'limitation':'Residuals alone cannot certify linearity or stationarity; additional amplitude and repeat tests may still be needed.'})
# Save exact original condition file and canonical exports together with evidence.
import zipfile
with zipfile.ZipFile('PEMFC_FOCUSED_QC_EVIDENCE.zip','w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
 for p in O.rglob('*'):
  if p.is_file():z.write(p,p)
 p=R/'DIFFERENTIAL'/d['originalFileName'];z.write(p,p)
print('RAW_ADMISSION_AUDIT_DONE; inspect findings before approving any source')
