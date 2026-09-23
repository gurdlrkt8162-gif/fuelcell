#!/usr/bin/env python3
"""Specialized PEMFC candidate audit; no automatic research admission."""
from pathlib import Path
import json, zipfile
import pemfc_stage2_admission_audit as m

m.RAW=Path('pemfc_stage3_raw'); m.AUD=Path('pemfc_stage3_audit')
m.RAW.mkdir(exist_ok=True); m.AUD.mkdir(exist_ok=True)
m.RECEIPTS=[]; m.ERRORS=[]

TASKS=[
 ('JRC_ZERO_GRADIENT',lambda:m.take_mendeley('JRC_ZERO_GRADIENT','n5csdjfg3c',2)),
 ('NPL_CO_CONTAMINATION',lambda:m.take_mendeley('NPL_CO_CONTAMINATION','sp4pc8w9xh',1)),
 ('AC_RESPONSE',lambda:m.take_mendeley('AC_RESPONSE','pn95bsbhv9',1)),
]
for tag,fn in TASKS:
    print('==',tag,'==',flush=True)
    try: fn()
    except Exception as e:
        m.ERRORS.append({'tag':tag,'task_error':repr(e)})
        print('ERROR',tag,e,flush=True)
m.expand_archives()
for root in sorted(p for p in m.RAW.iterdir() if p.is_dir()):
    profiles=[]
    for p in sorted(root.rglob('*')):
        if not p.is_file() or p.name.endswith('.part'): continue
        profiles.append({'path':str(p),'bytes':p.stat().st_size,'sha256':m.hash_file(p),'state':'parser-size-gate'} if p.stat().st_size>180*1024*1024 else m.inspect(p))
    m.dump(f'{root.name}_PROFILES.json',profiles)
    m.dump(f'{root.name}_SUMMARY.json',{'files':len(profiles),'parse_errors':[x for x in profiles if 'error' in x],'bytes_including_extracted':sum(int(x.get('bytes',0)) for x in profiles)})
m.dump('DOWNLOAD_RECEIPTS.json',m.RECEIPTS)
m.dump('ERRORS.json',m.ERRORS)
m.dump('AUDIT_SUMMARY.json',{'datasets_requested':[x[0] for x in TASKS],'downloaded_files':len(m.RECEIPTS),'downloaded_bytes':sum(x['bytes'] for x in m.RECEIPTS),'errors':m.ERRORS,'state':'PARSED_FOR_MANUAL_ADMISSION_REVIEW_NOT_APPROVED'})
out=Path('PEMFC_STAGE3_SPECIALIZED_CANDIDATES_NOT_APPROVED.zip')
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=4,allowZip64=True) as z:
    for p in m.RAW.rglob('*'):
        if p.is_file() and '__unpacked' not in str(p) and not p.name.endswith('.part'): z.write(p,p)
    for p in m.AUD.rglob('*'):
        if p.is_file(): z.write(p,p)
print(json.dumps({'artifact':str(out),'bytes':out.stat().st_size,'sha256':m.hash_file(out),'errors':len(m.ERRORS)},indent=2))
