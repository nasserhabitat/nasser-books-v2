"""Apply reviewed, metadata-grounded Drive URL corrections to site resources."""
import json,re
from html import escape,unescape
from prepare_book_migration import ROOT
corrections=json.loads((ROOT/'scripts/drive-link-corrections.json').read_text(encoding='utf-8'))
changed=[]
catalog=json.loads((ROOT/'ai-index.json').read_text(encoding='utf-8'))
def visit(obj,book_id=None,lang=None):
    if isinstance(obj,list):return [visit(x,book_id,lang) for x in obj]
    if isinstance(obj,dict):
        book_id=obj.get('id',obj.get('book_id',book_id))
        result={}
        for k,v in obj.items():
            scope=k if k in ('ar','en') else lang
            result[k]=visit(v,book_id,scope)
        return result
    if isinstance(obj,str):
        for c in corrections:
            if c['id'].casefold()==str(book_id).casefold() and c['language']==lang:obj=obj.replace(c['old_file_id'],c['new_file_id'])
        if obj.lstrip().startswith(('https://','http://')):obj=obj.strip()
    return obj
catalog=visit(catalog)
(ROOT/'ai-index.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
by_number={b['book_number']:b for b in catalog['books']}
for p in ROOT.rglob('*'):
    if not p.is_file() or any(s in ('.git','scripts','.agents','.codex') for s in p.relative_to(ROOT).parts):continue
    if p.suffix not in ('.html','.json') and 'api/ai-access/metadata' not in p.as_posix():continue
    raw=p.read_text(encoding='utf-8-sig');new=raw
    if p.suffix=='.json' or 'api/ai-access/metadata' in p.as_posix():
        try:
            obj=json.loads(raw);out=visit(obj,p.stem)
            if out!=obj:new=json.dumps(out,ensure_ascii=False,indent=2)+'\n'
        except json.JSONDecodeError:continue
    elif p.suffix=='.html' and 'books' not in p.relative_to(ROOT).parts:
        def anchor(m):
            original=m[0];hm=re.search(r'href\s*=\s*([\"\'])([^\"\']+)\1',original,re.I)
            if not hm:return original
            url=unescape(hm[2]);label=re.sub('<[^>]+>','',original)
            kind='docx' if re.search(r'\bDOCX\b|\bWord\b',label,re.I) else 'pdf_external' if re.search(r'\bPDF\b',label,re.I) else None
            if not kind or 'drive.google.com/' not in url:return original
            preceding=raw[:m.start()];book_id=lang=None
            if p.name=='books.html':
                tabs=list(re.finditer(r'<div\b[^>]*id=[\"\'](ar|en)(\d+)[\"\']',preceding,re.I))
                if tabs:
                    lang=tabs[-1][1];b=by_number.get(int(tabs[-1][2]));book_id=b['id'] if b else None
            else:
                paths=list(re.finditer(r'books/([^/\"\']+)/(ar|en)/',preceding))
                if paths:book_id,lang=paths[-1][1],paths[-1][2]
            for c in corrections:
                if c['id']==book_id and c['language']==lang and c['field']==kind:url=url.replace(c['old_file_id'],c['new_file_id'])
            return original[:hm.start(2)]+escape(url,quote=True)+original[hm.end(2):]
        new=re.sub(r'<a\b[^>]*>.*?</a>',anchor,raw,flags=re.I|re.S)
    if new!=raw:p.write_text(new,encoding='utf-8');changed.append(str(p.relative_to(ROOT)))
print(json.dumps({'corrected_files':len(changed),'files':changed},ensure_ascii=False))
