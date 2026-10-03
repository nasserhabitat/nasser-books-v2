"""Apply the requested internal-TXT / external-Word-PDF resource policy.

Mechanical migration only: manuscripts and Google Drive objects are untouched.
"""
import json,re
from pathlib import Path
from prepare_book_migration import ROOT

catalog=json.loads((ROOT/'ai-index.json').read_text(encoding='utf-8'))
before={(b['id'],lang,key):b[lang].get(key) for b in catalog['books'] for lang in ('ar','en') for key in ('docx','pdf_direct','pdf_external')}
removed_fields=0;removed_anchors=0;changed=[]
def clean(obj):
    global removed_fields
    if isinstance(obj,dict):
        result={}
        for k,v in obj.items():
            if k=='txt_external':removed_fields+=1;continue
            result[k]=clean(v)
        return result
    if isinstance(obj,list):return [clean(v) for v in obj if v!='txt_external']
    return obj
for p in ROOT.rglob('*'):
    if not p.is_file() or any(part in ('.git','scripts','.codex','.agents','content.files') for part in p.relative_to(ROOT).parts):continue
    if p.suffix=='.json' or 'api/ai-access/metadata' in p.as_posix():
        raw=p.read_text(encoding='utf-8-sig')
        try:
            original=json.loads(raw);updated=clean(original)
            revised=json.dumps(updated,ensure_ascii=False,indent=2)+'\n' if updated!=original else raw
        except json.JSONDecodeError:
            revised,n=re.subn(r'^\s*"txt_external"\s*:\s*"[^"\n]*"\s*,?\s*$', '',raw,flags=re.M);removed_fields+=n
        if revised!=raw:p.write_text(revised,encoding='utf-8');changed.append(str(p.relative_to(ROOT)))
    elif p.suffix=='.html':
        raw=p.read_text(encoding='utf-8-sig')
        def anchor(m):
            global removed_anchors
            label=re.sub('<[^>]+>','',m[0]);href=re.search(r'href\s*=\s*[\"\']([^\"\']+)',m[0],re.I)
            if href and 'drive.google.com/' in href[1] and re.search(r'\b(?:TXT|Text)\b|نص',label,re.I):
                removed_anchors+=1;return ''
            return m[0]
        revised=re.sub(r'<a\b[^>]*>.*?</a>',anchor,raw,flags=re.I|re.S)
        revised=re.sub(r'^[ \t]*<li>\s*</li>\s*\n','',revised,flags=re.M)
        # Embedded JSON resource properties are not manuscript text.
        revised=re.sub(r'^\s*"txt_external"\s*:\s*"[^"\n]*"\s*,?\s*$', '',revised,flags=re.M)
        if revised!=raw:p.write_text(revised,encoding='utf-8');changed.append(str(p.relative_to(ROOT)))
after=json.loads((ROOT/'ai-index.json').read_text(encoding='utf-8'))
after['library']['resource_policy']={'internal':['txt','png'],'external_google_drive':['docx','pdf']}
(ROOT/'ai-index.json').write_text(json.dumps(after,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert before=={(b['id'],lang,key):b[lang].get(key) for b in after['books'] for lang in ('ar','en') for key in ('docx','pdf_direct','pdf_external')}
report={'removed_external_txt_fields':removed_fields,'removed_external_txt_anchors':removed_anchors,'word_pdf_links_unchanged':True,'changed_files':changed}
(ROOT/'scripts/internal-text-only-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='changed_files'},ensure_ascii=False));print('Changed files:',len(changed))
pending=[{'number':b['book_number'],'id':b['id'],'language':lang,'format':key,'expected_filename':f'{b["book_number"]}-{b["id"]}-{lang}.{key}'} for b in after['books'][69:] for lang in ('ar','en') for key,field in [('docx','docx'),('pdf','pdf_external')] if not b[lang].get(field)]
(ROOT/'scripts/pending-drive-resources.json').write_text(json.dumps(pending,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Missing new Drive resources:',len(pending))
