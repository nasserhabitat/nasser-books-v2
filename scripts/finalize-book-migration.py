"""Finalize derived text and legacy metadata after the migration."""
import json,re
from prepare_book_migration import ROOT,SOURCE,paragraphs

BASE='https://nasserhabitat.github.io/nasser-books-v2/'
catalogue=json.loads((ROOT/'ai-index.json').read_text(encoding='utf-8'))
plan=json.loads((ROOT/'scripts/new-books-plan.json').read_text(encoding='utf-8'))
for book in catalogue['books']:
    folder=next(p for p in (ROOT/'books').iterdir() if p.is_dir() and p.name.casefold()==book['id'].casefold())
    if folder.name!=book['id']:
        temp=folder.with_name('_case_migration_'+book['id'])
        folder.rename(temp);temp.rename(ROOT/'books'/book['id'])
search=json.loads((ROOT/'search-index.json').read_text(encoding='utf-8'))
for book in search['books']:
    for key in ('topics_ar','topics_en'):
        if not isinstance(book['metadata'].get(key),list):book['metadata'][key]=[]
(ROOT/'search-index.json').write_text(json.dumps(search,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
page=ROOT/'search.html';s=page.read_text(encoding='utf-8')
s=re.sub(r'const booksData\s*=\s*\[.*?\];',lambda _: 'const booksData = '+json.dumps(search['books'],ensure_ascii=False,indent=2)+';',s,count=1,flags=re.S)
page.write_text(s,encoding='utf-8')
for row in plan:
    name=f'{row["number"]}-{row["id"]}-{row["language"]}.txt'
    target=ROOT/'books'/row['id']/row['language']/name
    target.write_text('\n'.join(paragraphs(SOURCE/row['organized_path']))+'\n',encoding='utf-8')

def clean(obj):
    if isinstance(obj,dict):
        return {k:clean(v) for k,v in obj.items() if k!='txt_external' and not (k in ('html','archive') and isinstance(v,str) and v.startswith(('http','books/')))}
    if isinstance(obj,list):return [clean(v) for v in obj if v!='html']
    if isinstance(obj,str):
        obj=obj.replace('https://nasserhabitat.github.io/nasser-books/',BASE)
        for book in catalogue['books']:
            for lang in ('ar','en'):
                prefix=f'books/{book["id"]}/{lang}/'
                obj=obj.replace(prefix+'content.txt',prefix+f'{book["book_number"]}-{book["id"]}-{lang}.txt')
                obj=obj.replace(prefix+f'cover-{lang}.png',prefix+f'{book["id"]}-cover-{lang}.png')
        return obj
    return obj

invalid=[]
for path in (ROOT/'api/ai-access/metadata').iterdir():
    if not path.is_file():continue
    try:data=json.loads(path.read_text(encoding='utf-8-sig'))
    except json.JSONDecodeError as e:
        invalid.append({'path':str(path.relative_to(ROOT)),'error':str(e)})
        # Retain legacy syntax/content, but remove explicitly deprecated download fields.
        raw=clean(path.read_text(encoding='utf-8-sig'))
        raw=re.sub(r'^\s*"(?:html|archive)"\s*:\s*"(?:https?://|books/)[^"\n]*"\s*,?\s*$', '',raw,flags=re.M)
        path.write_text(raw,encoding='utf-8')
        continue
    revised=clean(data)
    if revised!=data:path.write_text(json.dumps(revised,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report_path=ROOT/'scripts/migration-report.json'
report=json.loads(report_path.read_text(encoding='utf-8'))
report['legacy_metadata_parse_errors']=invalid
report['review_notes']={
 '75':'اسم ملف المصدر العربي يحمل مسودة؛ لم تُحذف العلامة أو يُنشر الملف.',
 '81':'نسخة مرتبطة بـ QCROS والمجلد 102؛ لم يُفترض أنهما كتاب واحد ولم يُدمجا.',
 '87':'تبدأ النسخة الإنجليزية ببيان الإتاحة قبل عنوان الكتاب.',
 '89':'تبدأ النسخة الإنجليزية بعبارة تقديمية لترجمة وتحليل؛ حُفظت دون تحرير صامت.',
 '101':'تبدأ النسخة الإنجليزية ببيان الإتاحة قبل عنوان الكتاب.',
 '110':'يتضمن أول النص العربي عبارة مخاطبة تحريرية؛ حُفظت ولم تُحذف بصمت.'}
report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for filename in ('api/ai-access/index.json',):
    p=ROOT/filename;s=p.read_text(encoding='utf-8').replace('69 كتاب','112 كتاب');p.write_text(s,encoding='utf-8')
print(json.dumps({'refreshed_texts':len(plan),'legacy_metadata_parse_errors':invalid},ensure_ascii=False))
