"""Synchronize typed book download anchors with ai-index without changing layout."""
import json,re
from html import escape,unescape
from prepare_book_migration import ROOT
cat=json.loads((ROOT/'ai-index.json').read_text(encoding='utf-8'))
changes=[];checked=0
for b in cat['books']:
    for lang in ('ar','en'):
        p=ROOT/'books'/b['id']/lang/'index.html';raw=p.read_text(encoding='utf-8');checked+=1
        r=b[lang]
        def anchor(m):
            whole=m[0];hm=re.search(r'href\s*=\s*([\"\'])([^\"\']+)\1',whole,re.I)
            if not hm:return whole
            href=unescape(hm[2]);label=re.sub('<[^>]+>','',whole)
            if 'drive.google.com/' not in href and 'docs.google.com/' not in href:return whole
            key='docx' if re.search(r'\b(?:DOCX|Word)\b',label,re.I) else 'pdf_direct' if re.search(r'\bPDF\b',label,re.I) and re.search(r'direct|مباشر',label,re.I) else 'pdf_external' if re.search(r'\bPDF\b',label,re.I) else None
            if not key:return whole
            expected=r.get(key) or (r.get('pdf_external') if key=='pdf_direct' else None)
            if not expected:return whole
            if href!=expected:
                changes.append({'number':b['book_number'],'id':b['id'],'language':lang,'field':key,'old_url':href,'new_url':expected})
                return whole[:hm.start(2)]+escape(expected,quote=True)+whole[hm.end(2):]
            return whole
        revised=re.sub(r'<a\b[^>]*>.*?</a>',anchor,raw,flags=re.I|re.S)
        if revised!=raw:p.write_text(revised,encoding='utf-8')
report={'pages_checked':checked,'anchors_synchronized':len(changes),'changes':changes,'note':'Catalogue parity only. Drive identity/access issues are separately recorded; no Drive files or sharing were modified.'}
(ROOT/'scripts/book-resource-sync-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='changes'},ensure_ascii=False))
