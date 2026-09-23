#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json, re

ROOT=Path('pemfc_mendeley_parsed_audit')
OUT=Path('pemfc_admission_facts'); OUT.mkdir(exist_ok=True)
TAGS=['RWTH','OXYGEN_PURGE','TWO_SYSTEM_FAULT','SENSOR_FAULT','JRC_ZERO_GRADIENT','NPL_CO_CONTAMINATION']

def slim(x,depth=0):
    if depth>6:return '...'
    if isinstance(x,dict):
        keep={}
        for k,v in x.items():
            if k in {'path','bytes','sha256','archive_test','members','line_count','headers','rows','columns','header_mode','shape','dtype','finite','nonfinite','min','max','sheets','mat','hdf5','paragraphs','tables','preview','text_preview','table','inferred','header_none','stats','error','state'}:
                keep[k]=slim(v,depth+1)
        return keep
    if isinstance(x,list):return [slim(v,depth+1) for v in x[:80]]
    if isinstance(x,str):return x[:8000]
    return x

def walk_mat(obj,prefix=''):
    rows=[]
    if isinstance(obj,dict):
        if 'shape' in obj and 'dtype' in obj:rows.append({'path':prefix,'shape':obj.get('shape'),'dtype':obj.get('dtype'),'min':obj.get('min'),'max':obj.get('max'),'finite':obj.get('finite'),'nonfinite':obj.get('nonfinite')})
        for k,v in obj.items():
            if k not in {'shape','dtype','min','max','finite','nonfinite'}:rows+=walk_mat(v,prefix+'.'+k if prefix else k)
    elif isinstance(obj,list):
        for i,v in enumerate(obj[:10]):rows+=walk_mat(v,f'{prefix}[{i}]')
    return rows

facts={}; md=['# Parsed PEMFC candidate facts','', 'Machine-generated reduction of the raw-file audit. Scientific admission still requires manual interpretation.','']
for tag in TAGS:
    path=ROOT/f'{tag}_PROFILES.json'
    data=json.loads(path.read_text(encoding='utf-8'))
    entry={'file_count':len(data),'files':[]}
    md += [f'## {tag}', '']
    for rec in data:
        s=slim(rec)
        item={'path':rec.get('path'),'bytes':rec.get('bytes'),'sha256':rec.get('sha256'),'archive_test':rec.get('archive_test'),'state':rec.get('state'),'error':rec.get('error')}
        if 'members' in rec:item['members']=rec['members']
        if 'line_count' in rec:item['line_count']=rec['line_count']
        if 'preview' in rec:item['preview']=rec['preview'][:5000]
        if 'text_preview' in rec:item['text_preview']=rec['text_preview'][:5000]
        if 'table' in rec:item['table']=slim(rec['table'])
        if 'sheets' in rec:item['sheets']=slim(rec['sheets'])
        if 'mat' in rec:item['mat_arrays']=walk_mat(rec['mat'])[:300]
        if 'hdf5' in rec:item['hdf5']=rec['hdf5'][:300]
        if 'paragraphs' in rec:item['paragraphs']=rec['paragraphs'][:100]
        if 'tables' in rec:item['tables']=rec['tables'][:30]
        entry['files'].append(item)
        md.append(f"### `{rec.get('path')}`")
        md.append(f"- bytes: {rec.get('bytes')}; sha256: `{rec.get('sha256')}`; archive: {rec.get('archive_test')}; state: {rec.get('state')}; error: {rec.get('error')}")
        if rec.get('members'):md.append('- members: '+', '.join(f"{x.get('path')} ({x.get('bytes')})" for x in rec['members'][:50]))
        if rec.get('table'):
            t=rec['table']; md.append(f"- table: {t.get('rows')} rows × {t.get('columns')} columns; headers: {t.get('headers')}")
            md.append('- ranges: '+json.dumps([{x.get('name'):{'min':x.get('min'),'max':x.get('max'),'numeric':x.get('numeric')}} for x in t.get('stats',[])],ensure_ascii=False)[:7000])
        if rec.get('sheets'):
            for n,v in rec['sheets'].items():
                q=v.get('inferred') or {}; md.append(f"- sheet `{n}`: {q.get('rows')}×{q.get('columns')}; headers={q.get('headers')}")
        if rec.get('mat'):
            arrays=walk_mat(rec['mat']); md.append('- MAT arrays: '+json.dumps(arrays[:100],ensure_ascii=False)[:12000])
        if rec.get('hdf5'):md.append('- HDF5 datasets: '+json.dumps(rec['hdf5'][:100],ensure_ascii=False)[:12000])
        text=rec.get('preview') or rec.get('text_preview')
        if text:md.append('```text\n'+text[:4000]+'\n```')
        if rec.get('paragraphs'):md.append('- DOCX paragraphs: '+json.dumps(rec['paragraphs'][:40],ensure_ascii=False)[:8000])
        if rec.get('tables'):md.append('- DOCX tables: '+json.dumps(rec['tables'][:10],ensure_ascii=False)[:10000])
        md.append('')
    facts[tag]=entry
(OUT/'CANDIDATE_FACTS.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'CANDIDATE_FACTS.md').write_text('\n'.join(md),encoding='utf-8')
print('\n'.join(md)[:60000])
