#!/usr/bin/env python3
from pathlib import Path
import re, json
root=Path('debug_artifact/work/browser/electro_260907')
api=set(); keys=set(); matches=[]
patterns=[
 r"[\"'](/api/[^\"'\s<>]+)",
 r"[\"'](/trpc/[^\"'\s<>]+)",
 r"[\"'](https?://[^\"'\s<>]+(?:api|transcrib|audio|video|download|export)[^\"'\s<>]*)",
]
needles=['4a2a26e5-5a63-4b8b-9c01-e1bb5385d9e3','f47bde5b-aada-4551-9036-a17b9ec06f8a','안녕하세요 수소 에너지','signedUrl','presigned','audioCache','getAudio','getTranscript','transcript','subtitle','originalFile','fileUrl','mediaUrl','audioUrl','videoUrl','downloadUrl','storageUrl','objectKey','fileKey']
for p in sorted(root.glob('response_*.txt'))+[root/'page.html']:
    if not p.exists(): continue
    s=p.read_text(encoding='utf-8',errors='ignore')
    for pat in patterns:
        for m in re.findall(pat,s,re.I): api.add(m.replace('\\/','/').replace('\\u0026','&'))
    for n in needles:
        start=0
        while True:
            i=s.lower().find(n.lower(),start)
            if i<0: break
            ctx=s[max(0,i-350):min(len(s),i+700)].replace('\n',' ')
            matches.append({'file':p.name,'needle':n,'context':ctx})
            start=i+len(n)
            if sum(1 for x in matches if x['file']==p.name and x['needle']==n)>=10: break
    for k in re.findall(r'[\"']([A-Za-z][A-Za-z0-9_]{2,40}(?:Url|URL|Key|Path|Transcript|Subtitle|Audio|Video|File))[\"']\s*:',s):
        keys.add(k)
Path('debug_api_paths.txt').write_text('\n'.join(sorted(api)),encoding='utf-8')
Path('debug_api_keys.txt').write_text('\n'.join(sorted(keys)),encoding='utf-8')
Path('debug_id_context.json').write_text(json.dumps(matches,ensure_ascii=False,indent=2),encoding='utf-8')
print('api',len(api),'keys',len(keys),'contexts',len(matches))
