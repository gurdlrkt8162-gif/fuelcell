#!/usr/bin/env python3
"""Subset curation, not blanket scientific certification. No private user documents."""
from pathlib import Path
import json,hashlib,zipfile,shutil,csv,re,subprocess
import numpy as np,pandas as pd
from matio import load_from_mat
R=Path('candidate_bytes');Q=Path('pemfc_complete_qc');P=Path('PEMFC_CURATED_ADDITIONS_20260922');P.mkdir(exist_ok=True)
for f in ('01_RWTH_TSOS_ONLY/raw','01_RWTH_TSOS_ONLY/numeric_export','01_RWTH_TSOS_ONLY/source_notes','02_CEA_POLARIZATION_ONLY/raw','02_CEA_POLARIZATION_ONLY/numeric_export','90_AUDIT','91_REPRODUCE'):(P/f).mkdir(parents=True,exist_ok=True)
def out(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False,default=str),encoding='utf-8')
# Source archive CRC before extracting the selected original files.
p=R/'RWTH'/'mc46tw9t8m.zip'
with zipfile.ZipFile(p) as z:
 assert z.testzip() is None
 for info in z.infolist():
  name=Path(info.filename).name
  if name in ('cycle_1_TSOS.mat','cycle_2_TSOS.mat'):
   (P/'01_RWTH_TSOS_ONLY/raw'/name).write_bytes(z.read(info))
  elif name in ('00_readme.txt','plot_U.m'):
   (P/'01_RWTH_TSOS_ONLY/source_notes'/name).write_bytes(z.read(info))
assert len(list((P/'01_RWTH_TSOS_ONLY/raw').glob('*.mat')))==2
rw=[]
for p in sorted((P/'01_RWTH_TSOS_ONLY/raw').glob('*.mat')):
 obj=load_from_mat(str(p),raw_data=False,add_table_attrs=True);d=next(v for v in obj.values() if isinstance(v,pd.DataFrame));a=d.to_numpy(dtype=float)
 assert np.isfinite(a).all();assert np.all(np.diff(d.t)>0)
 destination=P/'01_RWTH_TSOS_ONLY/numeric_export'/(p.stem+'.csv');d.to_csv(destination,index=False)
 back=pd.read_csv(destination,float_precision='round_trip').to_numpy(dtype=float);assert np.array_equal(a,back)
 den=d.i_dens_A_cm2*d.U_st_V;ratio=d.P_st_kW*1000/den
 rw.append({'file':p.name,'rows':len(d),'columns':len(d.columns),'nonfinite':0,'start_s':float(d.t.iloc[0]),'end_s':float(d.t.iloc[-1]),'dt_s':float(np.median(np.diff(d.t))),'csv_numeric_round_trip_exact':True,'power_kW_min':float(d.P_st_kW.min()),'power_kW_max':float(d.P_st_kW.max()),'cell_scale_voltage_min_V':float(d.U_st_V.min()),'cell_scale_voltage_max_V':float(d.U_st_V.max()),'P_over_jU_median_cm2':float(ratio.median()),'P_over_jU_relative_deviation_max':float(np.abs(ratio/ratio.median()-1).max()),'coolant_difference_residual_max_K':float(np.abs(d.DeltaT_cool_K-(d.T_out_cool_gradC-d.T_in_cool_gradC)).max())})
# Only polarization rows with an intact, explicit header. All EIS stays OUT of this package.
meta=json.loads(Path('pemfc_candidate_audit/DIFFERENTIAL_source.json').read_text());listed=meta['data']['latestVersion']['files'];iv=[]
for p in sorted((R/'DIFFERENTIAL').rglob('*_IV.txt')):
 b=p.read_bytes();provider=next(f['dataFile'] for f in listed if f['dataFile']['filename']==p.name);assert hashlib.md5(b).hexdigest()==provider['md5']
 text=b.decode('utf-8-sig');lines=text.splitlines();head=lines[0].split('\t');assert head==['Ewe/V','I/A']
 vals=[];changes=0
 for line in lines[1:]:
  if not line.strip():continue
  toks=line.split('\t');assert len(toks)==2;row=[]
  for x in toks:
   x=x.strip()
   if re.fullmatch(r'[+-]?\d+,\d+(?:[eE][+-]?\d+)?',x):x=x.replace(',','.');changes+=1
   row.append(float(x))
  vals.append(row)
 a=np.asarray(vals);assert np.isfinite(a).all();assert a.shape[1]==2
 shutil.copy2(p,P/'02_CEA_POLARIZATION_ONLY/raw'/p.name)
 d=pd.DataFrame(a,columns=['voltage_V','current_A']);d['condition_id']='Break-in' if p.stem.startswith('Break') else p.stem.split('_')[0];d['source_row']=np.arange(2,len(d)+2);d['current_density_A_cm2']=d.current_A/1.8
 # This is a recommended modeling-domain indicator from the descriptor, NOT a safety label.
 d['descriptor_reproducibility_region_V_ge_0p6']=d.voltage_V>=.6
 d.to_csv(P/'02_CEA_POLARIZATION_ONLY/numeric_export'/p.with_suffix('.csv').name,index=False)
 iv.append({'file':p.name,'rows':len(d),'provider_md5_match':True,'nonfinite':0,'locale_replacements':changes,'voltage_min_V':float(a[:,0].min()),'voltage_max_V':float(a[:,0].max()),'current_min_A':float(a[:,1].min()),'current_max_A':float(a[:,1].max()),'points_voltage_ge_0p6':int((a[:,0]>=.6).sum())})
assert len(iv)==37
condition=R/'DIFFERENTIAL'/'Operating_conditions_Cell.xlsx';cb=condition.read_bytes();assert len(cb)==12519;assert hashlib.md5(cb).hexdigest()=='854ca98a8ae9ca186ec26609a25981a6';shutil.copy2(condition,P/'02_CEA_POLARIZATION_ONLY/raw'/condition.name)
# Source inventories preserve provenance but contain no discarded dataset bytes.
out('90_AUDIT/RWTH_ADMITTED_QC.json',rw);out('90_AUDIT/CEA_ADMITTED_IV_QC.json',iv)
for name in ('RWTH_SUMMARY.json','RWTH_QC.json','DIFFERENTIAL_SUMMARY.json','DIFFERENTIAL_HEADERS.json','DIFFERENTIAL_FILE_QC.json','LINKK_FULL_BAND.json','CONDITIONS_VERIFIED.json'):
 shutil.copy2(Q/name,P/'90_AUDIT'/name)
# Correct automatic classification: two headerless EIS files were initially counted as non-EIS.
fields=json.loads((Q/'DIFFERENTIAL_FILE_QC.json').read_text());eis=[x for x in fields if 'EIS' in x['file']];missing=[x['file'] for x in eis if not any('freq' in h.lower() for h in x.get('headers',[]))];bad=[x['file'] for x in eis if '#NOM?' in x.get('headers',[])]
kk=json.loads((Q/'LINKK_FULL_BAND.json').read_text())
out('90_AUDIT/FINAL_EXCLUSIONS.json',{'RWTH_MPC_runs':'Not admitted to this working supplement: instantaneous P/(j*U) differs substantially from its nominal constant; actual-versus-command current and timing semantics remain unresolved. This is not proof that experiments are invalid.','RWTH_INTERNAL_STATE_LABELS':'Hydration, internal partial pressures, catalyst-layer vapor concentration and modeled membrane temperatures are NOT independent measured ground truth.','CEA_EIS_total_by_path':len(eis),'CEA_EIS_missing_header':missing,'CEA_EIS_damaged_header':bad,'CEA_EIS_analyzed_full_band':len(kk['results']),'CEA_EIS_screen_pass':kk['pass_count'],'CEA_EIS_exclusion_reason':'All EIS withheld: header defects and full-original-band Lin-KK residual screen not passed. Screen does not prove physical invalidity. No frequency deletion or post-hoc favorable band selection.','automatic_classification_correction':'Earlier DIFFERENTIAL_SUMMARY counted 109 EIS and 39 IV based only on headers. Filename+folder audit confirms 111 EIS and 37 IV. Two headerless files are EIS, not IV; neither is delivered as IV.','LOUGH2016':'20 named channels but absent engineering-unit/time-axis mapping and no voltage among documented 20 signals; not admitted for coupled electrothermal/efficiency analysis.','LOUGH2018':'24-column CSV has unresolved metadata rows/units and negative values under RH heading; not admitted.','OXYGEN_PURGE':'Experimental DOE summary and ANN derivatives, not dense operational RAW; kJ/L is energy-per-oxygen-volume, not a dimensionless oxygen utilization fraction. Not admitted.','HAEOLUS':'Meaning/unit/state-code mapping insufficient for an unambiguous operating model; not admitted.','SEVILLA2020':'Promising documented protocol; original supplementary raw archive was not successfully retrieved in this audit. Access HOLD, not a low-quality verdict.','WATERLOO120CHANNELS':'Data available upon reasonable request, not verified open downloadable raw.','limitations':'The existing 4.75GB Drive archive was not fully rebuilt and byte-deduplicated against these source files in this run. Comparison was against current Drive guide and prior dataset inventory.'})
(P/'README_KO.md').write_text('''# PEMFC 추가 엄선본 — 2026-09-22

## 최종 구성과 승인 범위
대량 수집본이 아니라 공개 데이터 2종에서 용도가 확인된 부분만 보관한 연구용 추가본입니다.
1. RWTH Two-Stage MPC 실험자료 중 cycle_1_TSOS, cycle_2_TSOS 원본 MAT 2개와 수치 동일성이 확인된 CSV.
2. CEA/LEPMI differential cell의 37조건 분극곡선 TXT와 원본 시험조건 XLSX, 파생 CSV.

기존 Drive 파일을 덮어쓰지 않습니다. 단독 완결된 추가 ZIP이며 분할파일 복원이 필요하지 않습니다.

## RWTH: 사용할 수 있는 것
전류밀도, 전압 관련 기록, 입출구 압력, 가스 유량·습도, 냉각수 입출구 온도와 유량의 운전 기록을 이용한 공개 시험대 범위의 입력–출력/열적 응답 분석.
두 기록 합계 103,142행. 30개 열에는 시간, 측정/변환값, 계산량과 모델 상태가 섞여 있습니다. 30개 독립 센서가 아닙니다.
원본 U_st_V는 README에서 stack voltage라고 설명되지만 값은 단셀 크기이고 저자 plot_U.m의 축은 U_cell입니다. 전체 스택 전압으로 사용하지 마십시오. 실제 셀수·면적 확인 없이 kW 자료에 곱해 전체 전류를 역산하지 마십시오.
막 함수율, 막 내부 온도, 내부 기체 분압 등은 독립 계측 정답으로 승인하지 않습니다. 모델 생성량을 학습 입력과 정답에 함께 넣어 인공적으로 성능을 높이지 마십시오.
MPC 3개 운전 파일은 순간 전류–전압–출력 대응/명령값 의미가 미확인되어 이번 작업본에서 제외했습니다. 시험 전체가 잘못되었다는 뜻은 아닙니다.
각 기록은 같은 장치 계열의 운전 조건이지 독립 스택 수명시험이 아닙니다. 압력 기준(절대/게이지), 센서 지연, 열매체 물성, 보조장치 소비전력은 별도 확인 대상입니다.
이 자료로 실제 시스템 net 효율, 탱크 수소 인출량, 냉시동·OFF·STANDBY·재시작 비용 또는 절대 수명을 검증했다고 주장할 수 없습니다.

## CEA/LEPMI: 사용할 수 있는 것
실제 1.8 cm² differential 단셀에서 얻은 37조건 분극곡선입니다. 국부 조건은 COMSOL 예측으로 선택했지만 공개 I–V 값은 그 조건을 실험적으로 재현한 측정값입니다. 실대형 스택 내부 위치를 직접 측정한 자료는 아닙니다.
열은 원파일 헤더에 따라 전압 Ewe/V, 전류 I/A 순서로 해석합니다. 논문 본문 열 설명과 반대이므로 헤더를 보존했습니다.
CSV의 j=I/1.8, V>=0.6V 표시는 파생값입니다. 후자는 원 논문이 재현성 한계를 설명한 구간을 나타내는 모델링 참고 마스크일 뿐, 안전/정상 고장 라벨이 아닙니다. 0.6V 미만의 물방울 관련 변동을 제거하거나 임의 정상화하지 않았습니다.
전체 조건 공간이 완전 요인실험은 아니므로 단일 인자의 순수 인과효과나 모든 상호작용을 식별한다고 주장하지 마십시오.
원 조건 XLSX는 Dataverse original 형식으로 받아 originalFileSize 12,519bytes와 제공자 MD5를 확인했습니다. 자동 변환 TAB의 filesize와 혼용하지 마십시오.
EIS 원본 111개는 이번 추가본에 전혀 포함하지 않습니다. 두 파일에 헤더가 없고 한 파일은 #NOM? 헤더이며, 나머지 108개 전 대역 자동 Lin-KK 검사가 이 감사의 RMS1%/최대5% 기준을 통과하지 못했습니다. 이는 진위 부정이나 보편적인 EIS 부적합 판정이 아닙니다. 특정 대역 선별/배선 인덕턴스·이상점/선형성·정상성 검토가 필요합니다.

## 허가조건과 인용
RWTH: https://data.mendeley.com/datasets/mc46tw9t8m/1 ; DOI 10.17632/mc46tw9t8m.1 ; CC BY-NC 4.0. 비상업 조건을 확인하십시오.
관련 논문: Weber et al., Two-stage model predictive stack control for PEM fuel cell systems, DOI 10.1016/j.compchemeng.2026.109791.
CEA: https://doi.org/10.57745/YLCIPH ; 공식 레코드 라이선스 Etalab Open Licence 2.0. 논문에는 CC0가 기재되어 있어 불일치를 기록합니다. 원저자와 DOI를 인용하고 적용 라이선스를 확인하십시오.
관련 논문: Cornet et al., Advanced Methodology for Emulating Local Operating Conditions in Proton Exchange Membrane Fuel Cells, Data 2024,9,152; DOI 10.3390/data9120152.

## 증거 수준
수행: 원문/metadata 확인, 실제 다운로드, 원본 보존, 제공자 체크섬이 존재하는 파일의 일치 확인, ZIP 무결성, MAT/TXT/XLSX 파싱, 비유한값·시간축·수치 항등식 검사, EIS 전대역 적합성 스크리닝.
미수행: 계측기 교정 인증, 센서 지연 실험, 모든 파라미터 식별, 실제 MATLAB/Simulink 모델 실행, 통합 시스템 검증, 전체 기존 Drive 압축본 해제·중복 대조.
실행 성공 상태와 논문 주장 승인 상태를 혼동하지 마십시오.

원본은 raw 폴더에서 수정하지 않습니다. numeric_export는 MATLAB table을 범용 CSV로 변환하거나 명시적 단위 변환/마스크를 추가한 파생물이며 raw로 재분류하지 않습니다.
''',encoding='utf-8')
# Keep reference README and machine-readable dictionaries together.
metaout={'RWTH':{'doi':'10.17632/mc46tw9t8m.1','license':'CC BY-NC 4.0','authors':['Nikolai Weber','Daniel Sallach'],'source_url':'https://data.mendeley.com/datasets/mc46tw9t8m/1','selection':['cycle_1_TSOS.mat','cycle_2_TSOS.mat'],'source_archive_sha256':hashlib.sha256((R/'RWTH'/'mc46tw9t8m.zip').read_bytes()).hexdigest()},'CEA':{'doi':'10.57745/YLCIPH','license_record':'Etalab Open Licence 2.0','license_paper':'CC0','authors':['Marine Cornet','Arnaud Morin','Jean-Philippe Poirot-Crouvezier','Yann Bultel'],'selection':'37 polarization TXT and original conditions XLSX; no EIS raw'}}
out('90_AUDIT/SOURCES.json',metaout)
for n in ('pemfc_complete_qc_20260922.py','package_curated_pemfc_20260922.py'):shutil.copy2(Path('scripts')/n,P/'91_REPRODUCE'/n)
if (Q/'requirements_executed.txt').exists():shutil.copy2(Q/'requirements_executed.txt',P/'91_REPRODUCE/requirements_executed.txt')
# Public provenance metadata from provider, not private manuscript material.
shutil.copy2(Path('pemfc_candidate_audit/DIFFERENTIAL_source.json'),P/'90_AUDIT/CEA_PROVIDER_METADATA.json')
files=[]
for p in sorted(P.rglob('*')):
 if p.is_file():files.append({'path':str(p.relative_to(P)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
out('90_AUDIT/FILE_MANIFEST.json',files)
(P/'90_AUDIT/SHA256SUMS.txt').write_text('\n'.join(f"{x['sha256']}  {x['path']}" for x in files)+'\n',encoding='utf-8')
summary={'status':'SCOPED_SUBSETS_ADMITTED_NOT_SYSTEM_CERTIFICATION','RWTH_files':2,'RWTH_rows':sum(x['rows'] for x in rw),'CEA_IV_files':len(iv),'CEA_IV_rows':sum(x['rows'] for x in iv),'CEA_conditions_files':1,'EIS_raw_files_in_package':0,'MPC_raw_files_in_package':0,'payload_files_before_manifest':len(files),'RWTH_QC':rw,'CEA_IV_locale_replacements':sum(x['locale_replacements'] for x in iv),'CEA_EIS_excluded':len(eis),'CEA_EIS_parsed_and_screened':len(kk['results']),'CEA_EIS_screen_pass':kk['pass_count']}
out('90_AUDIT/PACKAGE_SUMMARY.json',summary)
assert not any('EIS' in p.name for p in (P/'02_CEA_POLARIZATION_ONLY/raw').iterdir())
assert not any('MPC.mat' in p.name for p in (P/'01_RWTH_TSOS_ONLY/raw').iterdir())
with zipfile.ZipFile('PEMFC_CURATED_ADDITIONS_20260922.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(P.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(P))
with zipfile.ZipFile('PEMFC_CURATED_ADDITIONS_20260922.zip') as z:assert z.testzip() is None
z=Path('PEMFC_CURATED_ADDITIONS_20260922.zip');summary['zip_bytes']=z.stat().st_size;summary['zip_sha256']=hashlib.sha256(z.read_bytes()).hexdigest();summary['zip_crc']='PASS'
Path('pemfc_delivery_receipt_20260922.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False),flush=True)
