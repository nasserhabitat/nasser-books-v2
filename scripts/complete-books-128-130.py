"""Apply the author's subsequently supplied TXT/PDF editions without publishing."""
import argparse, copy, hashlib, importlib.util, json, re, shutil
from pathlib import Path
from collections import Counter

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--texts-root',type=Path,required=True)
    args=parser.parse_args()
    spec=importlib.util.spec_from_file_location('registration',Path(__file__).with_name('register-books-113-115.py'))
    r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
    update=json.loads(r.read('scripts/books-128-130-format-update.json'))
    manifest=json.loads(r.read('scripts/books-126-133-sources.json'))
    cat=json.loads(r.read('ai-index.json'))
    search=json.loads(r.read('search-index.json'))
    reader=json.loads(r.read('assets/pdf-reader-catalog.json'))
    targets={(f['number'],f['language']) for f in update['files']}
    for number,lang in sorted(targets):
        b=next(b for b in cat['books'] if b['book_number']==number)
        old=copy.deepcopy(b)
        files=[f for f in update['files'] if (f['number'],f['language'])==(number,lang)]
        assert all(f['public_readable'] for f in files)
        txtfile=next(f for f in files if f['name'].endswith('.txt'))
        source=args.texts_root/str(number)/lang/'supplied.txt'
        assert source.stat().st_size==txtfile['size']
        target=r.ROOT/b[lang]['txt_direct'].removeprefix(r.BASE)
        shutil.copyfile(source,target)
        for ext,key in (('.docx','docx'),('.pdf','pdf_external')):
            f=next(f for f in files if f['name'].endswith(ext))
            b[lang][key]='https://drive.google.com/uc?export=download&id='+f['id']
        note=b['metadata']['edition_notes'][lang]
        note=note.replace(' النص القابل للبحث مستخرج من Word؛ راجع الأصل للجداول والصور والتنسيق.','')
        note=note.replace(' Searchable text is extracted from Word; consult the original for tables, images, and formatting.','')
        b['metadata']['edition_notes'][lang]=note
        r.EDITION_NOTES[number]=b['metadata']['edition_notes']
        r.write(f'books/{b["id"]}/{lang}/index.html',r.page(b,lang))
        listing='arabic-books.html' if lang=='ar' else 'english-books.html'
        s=r.read(listing)
        assert r.card(old,lang) in s
        r.write(listing,s.replace(r.card(old,lang),r.card(b,lang),1))
        s=r.read('books.html')
        assert r.links(old,lang) in s
        r.write('books.html',s.replace(r.links(old,lang),r.links(b,lang),1))
        item=next(x for x in search['books'] if x['id']==b['id'])
        item['metadata']=copy.deepcopy(b['metadata'])
        p=next(x for x in reader['editions'] if (x['number'],x['language'])==(number,lang))
        p.update(status='ready',drive_id=next(f['id'] for f in files if f['name'].endswith('.pdf')))
        manifest['files']=[f for f in manifest['files'] if (f['number'],f['language'])!=(number,lang)]+files
        asset=next(a for a in manifest['assets'] if (a['number'],a['language'])==(number,lang))
        asset.update(text_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),text_source='original_drive_txt',docx_sha256=None)
    r.dump('ai-index.json',cat);r.dump('search-index.json',search)
    html,n=re.subn(r'const booksData\s*=\s*\[.*?\];',lambda _: 'const booksData = '+json.dumps(search['books'],ensure_ascii=False,indent=2)+';',r.read('search.html'),count=1,flags=re.S)
    assert n==1;r.write('search.html',html)
    reader['summary']=dict(Counter(e['status'] for e in reader['editions']))
    reader['summary'].setdefault('pending',0)
    r.dump('assets/pdf-reader-catalog.json',reader)
    manifest['notes']=[manifest['notes'][0],
        'All new editions have supplied PDF links. Author supplied TXT replaces extraction for 128 English and both 130 editions.',
        'Only 128 Arabic searchable text remains extracted from the original Word document.']
    r.dump('scripts/books-126-133-sources.json',manifest)
    readme=r.read('README.md')
    start=readme.index('إضافة 126–133: PDF الإنجليزي')
    readme=readme[:start]+'استُكملت ملفات TXT وPDF للكتاب 128 بالإنجليزية والكتاب 130 بلغتيه من الملفات التي أضافها المؤلف بتاريخ 2026-10-26. أصبحت جميع نسخ الكتب الجديدة مرتبطة بملفات PDF؛ بقي TXT العربي للكتاب 128 مستخرجًا من Word. غلاف 132 مأخوذ من مجلد المصدر العربي، والصورة إنجليزية للمجلد الرابع الصحيح بموافقة المؤلف.\n'
    r.write('README.md',readme)
    print('Completed 3 editions: original TXT files and verified public PDF links.')

if __name__=='__main__':
    main()
