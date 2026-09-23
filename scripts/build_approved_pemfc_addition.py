#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import csv, hashlib, json, os, re, shutil, subprocess, sys, textwrap, zipfile

ROOT=Path('source_artifacts')
OUT=Path('PEMFC_ADDITIONAL_STRICTLY_ADMITTED_2026-09-23')
REPORT_OUT=Path('pemfc_final_addition_audit')
for p in (OUT,REPORT_OUT):
    if p.exists(): shutil.rmtree(p)
    p.mkdir(parents=True)

DATASETS=[
 {'id':'ADD01_RWTH_FULL_SCALE_MPC','name':'RWTH full-scale two-stage MPC PEMFC test-bench data','source':'https://data.mendeley.com/datasets/mc46tw9t8m/1','doi':'10.17632/mc46tw9t8m.1','license':'CC BY-NC 4.0','class':'CORE — system/BoP dynamic operation','artifact':'RWTH','paper_use':'F-AAV and AUV: stack voltage/current, stack power/efficiency, air/H2/coolant commands and responses, reactant pressures, membrane hydration/temperature, stoichiometry, coolant ΔT and dynamic cycle validation.','limits':'Full-scale research test bench but not the 2×250 kW F-AAV module and not an underwater AIP plant. Includes measured raw signals and calculated internal-state channels; keep authority labels separate.'},
 {'id':'ADD02_SEVILLA_CELL_DYNAMICS','name':'Sevilla single-cell performance and NEDC load-cycling data','source':'https://doi.org/10.3390/data5020047','doi':'10.3390/data5020047','license':'CC BY 4.0','class':'CORE — variable-rich single-cell operating data','artifact':'STAGE2','paper_use':'Both manuscripts: pressure/flow/humidity/temperature/current/voltage response, temperature and pressure sensitivity, cathode stoichiometry sensitivity, NEDC transient-load replay, cell-level model qualification.','limits':'50 cm² single cell, not system-net efficiency or module start/stop evidence. Raw files are tab-delimited text without extensions and require the supplied importer and channel dictionary.'},
 {'id':'ADD03_DIFFERENTIAL_LOCAL_EIS','name':'Differential-cell local operating-condition polarization and EIS','source':'https://doi.org/10.57745/YLCIPH','doi':'10.57745/YLCIPH','license':'Etalab Open Licence 2.0','class':'CORE — EIS/polarization under controlled local conditions','artifact':'STAGE2','paper_use':'Both manuscripts and EIS/PHM papers: 37 local conditions spanning RH, temperature, pressure and gas-composition emulation at inlet/middle/outlet; polarization and EIS at 45/180/900 mA; build physically indexed electrochemical maps.','limits':'Differential cell and emulated local conditions, not a complete stack/BoP or vehicle system. One Dataverse normalized/original representation mismatch is documented; the preserved original is authoritative.'},
 {'id':'ADD04_JRC_ZERO_GRADIENT','name':'JRC ZERO-gradient hardware versus single-serpentine polarization/EIS data','source':'https://data.mendeley.com/datasets/n5csdjfg3c/2','doi':'10.17632/n5csdjfg3c.2','license':'CC BY 4.0','class':'CORE — independent hardware/flow-field electrochemical validation','artifact':'JRC','paper_use':'Both manuscripts: current-density-dependent voltage, pressure/temperature/voltage distributions, EIS and KK-oriented comparison across two hardware configurations; test robustness of cell maps to hardware geometry.','limits':'Workbook uses multi-row/merged headers and must be imported with the supplied workbook inspector; single-cell hardware, not full stack/BoP.'},
 {'id':'ADD05_OXYGEN_PURGE','name':'Oxygen-utilization and purge-strategy experimental tables with MATLAB/Simulink code','source':'https://data.mendeley.com/datasets/jy5vxystwd/2','doi':'10.17632/jy5vxystwd.2','license':'CC BY 4.0','class':'AUV-SPECIFIC SUPPORT — structured experimental DoE, not raw waveform','artifact':'OXYGEN_PURGE','paper_use':'AUV manuscript: finite-O2 operation, purge-duration/interval, load-level, temperature and oxygen-utilization surrogate map; supports purge/inventory sensitivity and AIP mode feasibility studies.','limits':'Small structured experiment/training tables (not continuous raw time series); ANN code is a reproducibility aid, not automatically a validated plant model.'},
 {'id':'ADD06_NPL_CO_DIAGNOSTICS','name':'NPL operando 13CO contamination and PEMFC response data','source':'https://data.mendeley.com/datasets/sp4pc8w9xh/1','doi':'10.17632/sp4pc8w9xh.1','license':'CC BY 4.0','class':'SPECIALIZED HIGH-QUALITY SUPPORT — contamination diagnostics','artifact':'NPL','paper_use':'High-quality PEMFC diagnostics: synchronized cell voltage/pressure with sparse CO/CO2 and high-rate isotope products/adsorbed-CO estimates; useful for contamination-state observers and recovery/diagnostic methodology.','limits':'Specialized trace-CO experiment, not representative of certified high-purity tank H2 or the main F-AAV/AUV operating map; independent time bases must not be row-joined.'},
]

REJECTED=[
 ('HAEOLUS Project fuel-cell data','REJECT','Ten tiny ts/value files are not sufficiently self-describing: authoritative units, test protocol and common clock/channel semantics are missing.'),
 ('Loughborough 2018 PEMFC rig CSV','HOLD','Rich 24-channel data but contains invalid/sentinel channels (e.g. one temperature channel near −64,000) and undocumented startup/sensor-validity intervals. Not added until a verified quality mask and event/label ledger are constructed.'),
 ('Loughborough 2016 practical fault data','HOLD','Institutional and real, but legacy workbook schema and labels are insufficiently explicit for immediate leakage-safe reuse; newer cleaner alternatives exist.'),
 ('Two-system flooding/dehydration workbook','HOLD','Large dataset across two systems, but worksheet columns are grouped with ambiguous multi-row headers and no machine-readable channel/episode registry in the deposited file.'),
 ('Flooding versus humidity-sensor-abnormality CSV','HOLD','Useful fault concept, but one implausible sensor column and insufficient explicit route/episode labels prevent strict admission without manual reconstruction.'),
 ('AC voltage-response dataset','REJECT FOR THIS PACKAGE','Very large and narrowly focused; marginal benefit is low relative to already admitted EIS/fault resources, so it is not added merely because it is downloadable.'),
 ('HAEOLUS/industrial non-PEMFC proxy data','REJECT','Not sufficiently specific or documented to calibrate the target PEMFC plant.'),
 ('100 kW/250 kW mobility-module or integrated underwater-AIP operational raw data','NOT FOUND','No public raw dataset meeting the required synchronized stack+BoP+thermal+reactant+mode-transition quality was verified. D-class assumptions remain assumptions.'),
]


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()

def is_html(path):
    b=Path(path).read_bytes()[:512].lstrip().lower()
    return b.startswith((b'<html',b'<!doctype html'))

def archive_test(path):
    r=subprocess.run(['7z','t',str(path)],text=True,capture_output=True,timeout=300)
    if r.returncode:raise RuntimeError(f'Archive integrity failure {path}: {r.stdout[-1500:]} {r.stderr[-500:]}')

def find_one(root,patterns):
    c=[]
    for pat in patterns:c+=list(Path(root).rglob(pat))
    c=[x for x in c if x.is_file() and not x.name.endswith('.part')]
    if len(c)!=1:raise RuntimeError(f'Expected exactly one file under {root} for {patterns}, found {[str(x) for x in c]}')
    return c[0]

def copy_raw_dataset(tag, artifact_folder, outdir, patterns):
    src=find_one(ROOT/artifact_folder,patterns)
    archive_test(src)
    dst=outdir/'original'/src.name; dst.parent.mkdir(parents=True); shutil.copy2(src,dst)
    for p in (ROOT/artifact_folder).rglob('*.json'):
        d=outdir/'source_receipts'/p.name; d.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,d)
    return [dst]

# Unpack the stage2 Actions artifact, which contains one candidate ZIP.
stage2_outer=find_one(ROOT/'STAGE2',['PEMFC_STAGE2_CANDIDATES_NOT_APPROVED.zip'])
archive_test(stage2_outer)
stage2_extract=Path('stage2_selected_extract')
if stage2_extract.exists():shutil.rmtree(stage2_extract)
stage2_extract.mkdir()
with zipfile.ZipFile(stage2_outer) as z:z.extractall(stage2_extract)
inner=find_one(stage2_extract,['PEMFC_STAGE2_CANDIDATES_NOT_APPROVED.zip'])
archive_test(inner)
stage2_inner=Path('stage2_inner')
if stage2_inner.exists():shutil.rmtree(stage2_inner)
stage2_inner.mkdir()
with zipfile.ZipFile(inner) as z:z.extractall(stage2_inner)

raw_files={}
# Mendeley candidates
raw_files['ADD01_RWTH_FULL_SCALE_MPC']=copy_raw_dataset('RWTH','RWTH',OUT/'01_RWTH_FULL_SCALE_MPC',['*.zip'])
raw_files['ADD04_JRC_ZERO_GRADIENT']=copy_raw_dataset('JRC','JRC',OUT/'04_JRC_ZERO_GRADIENT',['*.zip'])
raw_files['ADD05_OXYGEN_PURGE']=copy_raw_dataset('OXYGEN_PURGE','OXYGEN_PURGE',OUT/'05_OXYGEN_PURGE',['*.zip'])
raw_files['ADD06_NPL_CO_DIAGNOSTICS']=copy_raw_dataset('NPL','NPL',OUT/'06_NPL_CO_DIAGNOSTICS',['*.zip'])
# Sevilla original official supplement
sev=find_one(stage2_inner,['Experimental_performance_load_cycling_PEMFC.rar'])
archive_test(sev); sd=OUT/'02_SEVILLA_CELL_DYNAMICS'/'original'/sev.name; sd.parent.mkdir(parents=True); shutil.copy2(sev,sd); raw_files['ADD02_SEVILLA_CELL_DYNAMICS']=[sd]
# Differential original files (exclude audit/extracted copies; preserve source tree)
diff_candidates=list(stage2_inner.rglob('pemfc_stage2_raw/DIFFERENTIAL'))
if len(diff_candidates)!=1:raise RuntimeError(f'Differential raw root not unique: {diff_candidates}')
diffroot=diff_candidates[0]; dd=OUT/'03_DIFFERENTIAL_LOCAL_EIS'/'original'; shutil.copytree(diffroot,dd)
raw_files['ADD03_DIFFERENTIAL_LOCAL_EIS']=[p for p in dd.rglob('*') if p.is_file()]

# Copy selected machine-readable audit evidence.
evidence_map={
 '01_RWTH_FULL_SCALE_MPC':['pemfc_mendeley_parsed_audit/RWTH_SUMMARY.json','pemfc_mendeley_parsed_audit/RWTH_PROFILES.json'],
 '02_SEVILLA_CELL_DYNAMICS':['pemfc_stage2_audit/SEVILLA_DATA2020_SUMMARY.json','pemfc_stage2_audit/SEVILLA_DATA2020_PROFILES.json','pemfc_stage2_audit_sevilla_format/FORMAT_AUDIT.json','pemfc_stage2_audit_sevilla_format/FORMAT_AUDIT.csv'],
 '03_DIFFERENTIAL_LOCAL_EIS':['pemfc_stage2_audit/DIFFERENTIAL_SUMMARY.json','pemfc_stage2_audit/DIFFERENTIAL_PROFILES.json','pemfc_stage2_audit/DIFFERENTIAL_metadata.json'],
 '04_JRC_ZERO_GRADIENT':['pemfc_mendeley_parsed_audit/JRC_ZERO_GRADIENT_SUMMARY.json','pemfc_mendeley_parsed_audit/JRC_ZERO_GRADIENT_PROFILES.json'],
 '05_OXYGEN_PURGE':['pemfc_mendeley_parsed_audit/OXYGEN_PURGE_SUMMARY.json','pemfc_mendeley_parsed_audit/OXYGEN_PURGE_PROFILES.json'],
 '06_NPL_CO_DIAGNOSTICS':['pemfc_mendeley_parsed_audit/NPL_CO_CONTAMINATION_SUMMARY.json','pemfc_mendeley_parsed_audit/NPL_CO_CONTAMINATION_PROFILES.json'],
}
for folder,files in evidence_map.items():
    for f in files:
        p=Path(f)
        if not p.exists():raise RuntimeError(f'Missing audit evidence {p}')
        d=OUT/folder/'audit_evidence'/p.name; d.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,d)

# Dataset-level Korean readmes.
for d in DATASETS:
    folder=next(p for p in OUT.iterdir() if p.is_dir() and p.name.startswith(d['id'][3:5]+'_'))
    txt=f"""# {d['name']}

- ID: `{d['id']}`
- Source: {d['source']}
- DOI: `{d['doi']}`
- License: {d['license']}
- Admission class: **{d['class']}**

## 두 논문에서의 사용
{d['paper_use']}

## 주장 한계
{d['limits']}

`original/`은 공급자 파일을 수정하지 않고 보관합니다. `audit_evidence/`는 다운로드·압축·파싱 감사 결과입니다. 원본과 전처리 결과를 같은 파일로 덮어쓰지 마십시오.
"""
    (folder/'README_KO.md').write_text(txt,encoding='utf-8')

# MATLAB/Python import aids.
scripts=OUT/'90_IMPORT_AND_QC'; scripts.mkdir()
(scripts/'import_rwth.m').write_text("""function S = import_rwth(rootDir)
% Load official RWTH MAT structures. Requires a MATLAB release able to restore the saved class/structure.
files = dir(fullfile(rootDir,'**','cycle_*.mat'));
assert(~isempty(files),'RWTH MAT files not found');
S = struct;
for k=1:numel(files)
    f=fullfile(files(k).folder,files(k).name);
    x=load(f); names=fieldnames(x); assert(numel(names)==1);
    S.(matlab.lang.makeValidName(erase(files(k).name,'.mat'))) = x.(names{1});
end
end
""",encoding='utf-8')
(scripts/'import_sevilla.m').write_text("""function T = import_sevilla(rawTextFile)
% Sevilla files are tab-delimited text with no extension.
opts = detectImportOptions(rawTextFile,'FileType','text','Delimiter','\t','VariableNamingRule','preserve');
T = readtable(rawTextFile,opts);
assert(width(T) >= 50,'Unexpected Sevilla schema');
% FECHA and HORA must be combined explicitly by the analyst; do not row-merge separate tests.
end
""",encoding='utf-8')
(scripts/'import_differential_eis.m').write_text("""function T = import_differential_eis(file)
opts = detectImportOptions(file,'FileType','text','VariableNamingRule','preserve');
T = readtable(file,opts);
required = {'freq/Hz','Re(Z)/Ohm','-Im(Z)/Ohm'};
assert(all(ismember(required,T.Properties.VariableNames)),'Required EIS columns missing');
assert(all(isfinite(T.('freq/Hz'))) && all(T.('freq/Hz')>0));
end
""",encoding='utf-8')
(scripts/'inspect_jrc_workbooks.m').write_text("""function out = inspect_jrc_workbooks(rootDir)
files=dir(fullfile(rootDir,'**','*.xlsx')); assert(~isempty(files)); out=struct;
for k=1:numel(files)
  f=fullfile(files(k).folder,files(k).name); sheets=sheetnames(f);
  key=matlab.lang.makeValidName(erase(files(k).name,'.xlsx')); out.(key)=struct;
  for s=1:numel(sheets)
    out.(key).(matlab.lang.makeValidName(sheets(s)))=readcell(f,'Sheet',sheets(s));
  end
end
% Multi-row/merged headers must be mapped deliberately before numerical fitting.
end
""",encoding='utf-8')
(scripts/'import_oxygen_purge.m').write_text("""function D = import_oxygen_purge(rootDir)
files=dir(fullfile(rootDir,'**','*.xlsx')); D=struct;
for k=1:numel(files)
 f=fullfile(files(k).folder,files(k).name); T=readtable(f,'VariableNamingRule','preserve');
 D.(matlab.lang.makeValidName(erase(files(k).name,'.xlsx')))=T;
end
% These are structured experiments/training tables, not continuous raw waveforms.
end
""",encoding='utf-8')
(scripts/'import_npl_co.m').write_text("""function T = import_npl_co(csvFile)
T=readtable(csvFile,'VariableNamingRule','preserve');
% The file contains multiple independent time bases separated by blank columns.
% Never align CO/CO2, isotope and adsorbed-CO columns by row number without using their own time columns.
end
""",encoding='utf-8')
(scripts/'verify_package.py').write_text("""from pathlib import Path
import csv,hashlib,sys
root=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((root/'SOURCE_MANIFEST.csv').open(encoding='utf-8-sig')))
bad=[]
for r in rows:
 p=root/r['relative_path']; h=hashlib.sha256()
 if not p.exists(): bad.append((r['relative_path'],'missing')); continue
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 if h.hexdigest()!=r['sha256']:bad.append((r['relative_path'],'sha256'))
print('files',len(rows),'errors',bad)
sys.exit(bool(bad))
""",encoding='utf-8')

# Reports
report="# 추가 PEMFC 공개데이터 엄격 선별 보고\n\n"
report+="이번 패키지는 기존 Google Drive 패키지를 대체하지 않고, 추가로 검증 가치가 확인된 데이터만 담습니다. 후보를 많이 모으는 것이 아니라 **물리적 관련성, 측정변수, 프로토콜, 권리, 파일 무결성, 파싱 가능성, 두 원고의 주장 경계**를 모두 통과한 자료만 승인했습니다.\n\n"
report+="## 승인 데이터\n\n|ID|분류|핵심 가치|주요 한계|\n|---|---|---|---|\n"
for d in DATASETS:report+=f"|{d['id']}|{d['class']}|{d['paper_use']}|{d['limits']}|\n"
report+="\n## 제외·보류 데이터\n\n|후보|판정|이유|\n|---|---|---|\n"
for a,b,c in REJECTED:report+=f"|{a}|{b}|{c}|\n"
report+="\n## 결론\n\n두 원고를 실측자료 기반으로 크게 강화할 수 있는 추가자료는 확보했습니다. 그러나 **2×250 kW F-AAV용 완전 PEMFC 시스템 지도**와 **잠항체용 폐쇄형 H₂/O₂ AIP의 start–stop–restart–thermal–reactant 통합 운전 RAW**는 공개자료에서 확인하지 못했습니다. 이 부분은 공개데이터로 대체하지 않고 불확정/D-class 또는 후속 자체시험으로 유지해야 합니다.\n"
(OUT/'00_READ_ME_FIRST_KO.md').write_text(report,encoding='utf-8')
(OUT/'91_REJECTED_AND_HELD.md').write_text('\n'.join(['# 제외·보류 후보','']+[f'## {a}\n- 판정: **{b}**\n- 이유: {c}\n' for a,b,c in REJECTED]),encoding='utf-8')
(OUT/'92_LICENSE_AND_CITATION.md').write_text('# License and citation ledger\n\n'+ '\n'.join(f"- **{d['id']}** — {d['license']}; DOI `{d['doi']}`; source {d['source']}" for d in DATASETS)+'\n\n다운로드 가능성과 재배포 허용은 같은 뜻이 아닙니다. 각 라이선스의 저작자표시·비상업 조건을 준수하고 원 DOI와 연관 논문을 함께 인용하십시오.\n',encoding='utf-8')

# Manifest all package files excluding manifest itself.
rows=[]
for p in sorted(OUT.rglob('*')):
    if not p.is_file() or p.name in {'SOURCE_MANIFEST.csv','SOURCE_MANIFEST.json','SHA256SUMS.txt'}:continue
    head=p.read_bytes()[:512].lstrip().lower()
    if head.startswith((b'<html',b'<!doctype html')):raise RuntimeError(f'HTML saved as data: {p}')
    rows.append({'relative_path':str(p.relative_to(OUT)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':sha(p)})
with (OUT/'SOURCE_MANIFEST.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=['relative_path','bytes','sha256']);w.writeheader();w.writerows(rows)
(OUT/'SOURCE_MANIFEST.json').write_text(json.dumps({'datasets':DATASETS,'files':rows,'rejected':REJECTED},ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'SHA256SUMS.txt').write_text(''.join(f"{r['sha256']}  {r['relative_path']}\n" for r in rows),encoding='utf-8')

# Copy reports to branch evidence folder.
for p in ['00_READ_ME_FIRST_KO.md','91_REJECTED_AND_HELD.md','92_LICENSE_AND_CITATION.md','SOURCE_MANIFEST.csv','SOURCE_MANIFEST.json','SHA256SUMS.txt']:
    shutil.copy2(OUT/p,REPORT_OUT/p)

# Final archive and receipt.
archive=Path(OUT.name+'.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=5,allowZip64=True) as z:
    for p in OUT.rglob('*'):
        if p.is_file():z.write(p,p)
with zipfile.ZipFile(archive) as z:
    bad=z.testzip()
    if bad:raise RuntimeError('Final ZIP corrupt at '+bad)
receipt={'archive':archive.name,'bytes':archive.stat().st_size,'sha256':sha(archive),'dataset_count':len(DATASETS),'manifest_file_count':len(rows),'zip_test':'PASS'}
(REPORT_OUT/'FINAL_RECEIPT.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps(receipt,indent=2))
