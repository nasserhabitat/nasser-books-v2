"""One-time, local-only migration. Original Word files and Drive objects are untouched."""
import copy, json, re, shutil, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from html import escape
from prepare_book_migration import ROOT, SOURCE, paragraphs

BASE='https://nasserhabitat.github.io/nasser-books-v2/'
OLD='https://nasserhabitat.github.io/nasser-books/'
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
TITLE_OVERRIDES={
 74:('القراءة البنائية لآيات التعدد والقوامة في سورة النساء','A Structural Reading of the Verses on Polygamy and Qiwamah in Surah An-Nisa'),
 75:('هندسة الوعي والوجود: السماء والأرض في فقه اللسان القرآني','Engineering Consciousness and Existence'),
 77:('هندسة الوجود والردع الكوني: تفكيك البنية الفيزيائية للأشهر الحرم ونظام المثاني','Engineering Existence and Cosmic Restraint'),
 79:('هندسة الوعي القرآني بين الهداية والسلطة: قراءة بنيوية في النموذج المحمدي','Engineering Qur’anic Consciousness: Between Guidance and Authority'),
 80:('فقه العلم واللسان القرآني: نحو هندسة الوعي المعرفي',"Fiqh al-Ilm wal Lisan al-Qur'ani: Towards the Engineering of Cognitive Consciousness"),
 81:('QCROS V1.2 — الدستور المعياري الموحد لحوكمة إنتاج المعرفة القرآنية','QCROS — Governance of Qur’anic Knowledge Production'),
 84:('كرامة المرأة في القرآن','The Dignity of Women in the Qur’an'),
 85:('الحرام في القرآن الكريم','The Forbidden in the Qur’an'),
 86:('الموسوعة المعرفية الكبرى: من تيه الظنون إلى بصر الحديد','The Great Encyclopedia of Knowledge'),
 87:('موسوعة هندسة الجزاء في القرآن — المجلد الأول: معجم الجزاء','Quranic Penalty Engineering — The Lexical Control Layer (Volume I)'),
 88:('موسوعة هندسة الجزاء في القرآن — المجلد الثاني: هندسة الابتلاء',"The Engineering of Affliction: The Operator's Manual for the Quranic Human"),
 89:('موسوعة هندسة الجزاء في القرآن — المجلد الثالث: هندسة الأثر والسنن','The Engineering of Recompense in the Quran — Volume III: Impact and Divine Laws (Sunan)'),
 90:('موسوعة هندسة الجزاء في القرآن — المجلد الرابع: ميزان الجزاء','The Engineering of Recompense in the Qur’an — Volume IV: The Measure of Recompense'),
 91:('هندسة الجزاء في القرآن — المجلد الخامس: هندسة الحجب والعذاب','The Engineering of Veiling and ʿAdhāb — Volume V'),
 92:('موسوعة هندسة الجزاء في القرآن — المجلد السادس: الجنة والنار بين الحضور والمآل','The Architecture of Recompense in the Qur’an — Volume VI: Paradise and Fire'),
 93:('موسوعة هندسة الجزاء في القرآن — المجلد السابع: الرجوع والتوبة واستعادة الميزان','The Engineering of Recompense in the Qur’an — Volume VII: Return, Repentance, and the Restoration of Balance'),
 94:('موسوعة هندسة الجزاء في القرآن — المجلد الثامن: هندسة العلاقات في منظومة الجزاء','The Engineering of Recompense in the Qur’an — Volume VIII: The Engineering of Relations'),
 95:('الخمر في القرآن: بين التحريم المادي والتغطية الإدراكية','Wine in the Quran: Between Material Prohibition and Perceptual Covering'),
 96:('الربا في القرآن والنظام المصرفي المعاصر — المجلد الأول','Riba in the Qur’an and the Contemporary Banking System — Volume I'),
 97:('الربا في القرآن والنظام المصرفي المعاصر — المجلد الثاني: البنك التقليدي والبنك الإسلامي كمختبرين','Riba in the Qur’an and the Contemporary Banking System — Volume II'),
 101:('معمارية الكرامة','The Architecture of Karamah'),
 102:('سلسلة هندسة النصر — المجلد الأول: QCROS — حوكمة إنتاج المعرفة القرآنية','The Victory Engineering Series — Volume One: QCROS'),
 103:('سلسلة هندسة النصر — المجلد الثاني: هندسة النصرة','The Victory Engineering Series — Volume Two: Nusrah Engineering'),
 105:('سورة التكوير: قراءة بنيوية في هندسة الوعي والكون','Surah Al-Takwir: A Structural Reading in the Engineering of Consciousness and the Cosmos'),
 108:('معنى الإبل في القرآن','The Meaning of Ibil in the Qur’an'),
 109:('هندسة التدبر القرآني — آدم نموذجًا','Engineering Quranic Contemplation — Adam as a Case Study'),
 110:('هندسة السماوات في القرآن',"The Architecture of the Heavens in the Qur'an"),
 111:('هندسة المكر وسنن الإبادة الذاتية في النظام القرآني','Engineering of Deception and Self-Eradication Sunnah in the Quranic System'),
}
def write_json(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def textfile(p,s):p.write_text(s,encoding='utf-8')
def page_links(book,lang,prefix=''):
    items=[('txt_direct','TXT'),('docx','Word — Google Drive'),('pdf_external','PDF — Google Drive')]
    return ' '.join(f'<a href="{escape(book[lang][k],quote=True)}" target="_blank" rel="noopener noreferrer">{label}</a>' for k,label in items if book[lang].get(k))
def listing(book,lang):
    cover=book[lang].get('cover')
    img=f'<img src="{escape(cover)}" alt="{escape(book["titles"][lang])}" loading="lazy">' if cover else ''
    return f'<article class="book-card" data-lang="{lang}"><div class="book-cover">{img}</div><div class="book-info"><h2>{book["book_number"]}. {escape(book["titles"][lang])}</h2><p>{escape(book["description"][lang])}</p><div class="book-actions"><a href="books/{book["id"]}/{lang}/">'+('عرض الكتاب' if lang=='ar' else 'Book page')+f'</a></div><div class="download-links">{page_links(book,lang)}</div></div></article>\n'
def cover_from_docx(path,dest):
    with zipfile.ZipFile(path) as z:
        doc=ET.fromstring(z.read('word/document.xml'))
        rels=ET.fromstring(z.read('word/_rels/document.xml.rels'))
        targets={r.attrib['Id']:r.attrib.get('Target','') for r in rels}
        for blip in doc.findall('.//a:blip',NS):
            target=targets.get(blip.get('{'+NS['r']+'}embed'),'')
            if not target or not target.lower().endswith('.png'):continue
            name='word/'+target.lstrip('/')
            if name not in z.namelist():continue
            raw=z.read(name)
            if len(raw)>100000:
                dest.write_bytes(raw);return True
    return False
def main():
    catalogue=json.loads((ROOT/'ai-index.json').read_text(encoding='utf-8-sig'))
    assert len(catalogue['books'])==69,'Migration has already run; do not run it twice.'
    old_books=copy.deepcopy(catalogue['books'])
    plans=json.loads((ROOT/'scripts/new-books-plan.json').read_text(encoding='utf-8'))
    replacements={}
    missing=[]
    for b in catalogue['books']:
        for lang in ('ar','en'):
            folder=ROOT/'books'/b['id']/lang
            assert folder.is_dir(),str(folder)
            for old,new in [('content.txt',f'{b["book_number"]}-{b["id"]}-{lang}.txt'),(f'cover-{lang}.png',f'{b["id"]}-cover-{lang}.png')]:
                source=folder/old;dest=folder/new
                assert source.exists() and not dest.exists(),str(source)
                source.rename(dest)
                old_rel=f'books/{b["id"]}/{lang}/{old}'
                new_rel=f'books/{b["id"]}/{lang}/{new}'
                replacements[old_rel]=new_rel
                # Relative links within a book landing page.
                p=folder/'index.html'
                s=p.read_text(encoding='utf-8-sig')
                s=re.sub(r'(?<![/\w-])'+re.escape(old)+r'(?![\w-])',new,s)
                textfile(p,s)
            b[lang]['txt_direct']=BASE+f'books/{b["id"]}/{lang}/{b["book_number"]}-{b["id"]}-{lang}.txt'
            b[lang]['cover']=f'books/{b["id"]}/{lang}/{b["id"]}-cover-{lang}.png'
            b[lang].pop('html',None)
            b[lang].pop('archive',None)
        b['cover_image']=BASE+b['ar']['cover']
    for num in range(70,113):
        pair={e['language']:e for e in plans if int(e['number'])==num}
        bid=pair['ar']['id']
        titles=dict(zip(('ar','en'),TITLE_OVERRIDES[num])) if num in TITLE_OVERRIDES else {lang:pair[lang]['first_lines'][0] for lang in ('ar','en')}
        book={'id':bid,'book_number':num,'titles':titles,'description':{lang:('نسخة نصية مستخرجة من ملف Word الذي قدمه المؤلف؛ راجع المصدر الأصلي.' if lang=='ar' else 'Text extracted from the author-supplied Word edition; consult the original source.') for lang in ('ar','en')},'metadata':{'author':'ناصر ابن داوود','category':'quranic_studies','language_ar':'arabic','language_en':'english','ai_accessible':True,'structured_data':True,'topics_ar':[],'topics_en':[],'source_status':'author_supplied','pages_ar':None,'pages_en':None}}
        for lang,e in pair.items():
            folder=ROOT/'books'/bid/lang;folder.mkdir(parents=True,exist_ok=True)
            source=SOURCE/e['organized_path']
            name=f'{num}-{bid}-{lang}.txt'
            textfile(folder/name,'\n'.join(paragraphs(source))+'\n')
            res={'txt_direct':BASE+f'books/{bid}/{lang}/{name}'}
            matches=e['drive_matches']
            if num==82 and lang=='en':matches=[{'id':'1m_NG6_CTHZK4W-bFR_wgJCeBMPmIRVzM'}]
            if len(matches)==1:res['docx']='https://drive.google.com/uc?export=download&id='+matches[0]['id']
            else:missing.append({'number':num,'id':bid,'language':lang,'source_file':e['source_file']})
            cover=f'{bid}-cover-{lang}.png'
            if cover_from_docx(source,folder/cover):res['cover']=f'books/{bid}/{lang}/{cover}'
            book[lang]=res
        if book['ar'].get('cover'):book['cover_image']=BASE+book['ar']['cover']
        for lang in ('ar','en'):
            title=escape(titles[lang]);ar=lang=='ar'
            url=BASE+f'books/{bid}/{lang}/'
            data={'@context':'https://schema.org','@type':'Book','name':titles[lang],'inLanguage':lang,'url':url,'author':{'@type':'Person','name':'ناصر ابن داوود' if ar else 'Nasser Ibn Dawood'},'isAccessibleForFree':True,'license':'https://creativecommons.org/licenses/by-sa/4.0/'}
            if book[lang].get('cover'):data['image']=BASE+book[lang]['cover']
            img=f'<img style="max-width:360px;width:100%" src="{Path(book[lang]["cover"]).name}" alt="{title}">' if book[lang].get('cover') else ''
            other='en' if ar else 'ar'
            notice='' if book[lang].get('docx') else '<p>رابط Google Drive لهذه النسخة لم يُضف بعد. / Google Drive link pending.</p>'
            page=f'<!doctype html><html lang="{lang}" dir="'+('rtl' if ar else 'ltr')+f'"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title><link rel="canonical" href="{url}"><link rel="alternate" hreflang="ar" href="{BASE}books/{bid}/ar/"><link rel="alternate" hreflang="en" href="{BASE}books/{bid}/en/"><script type="application/ld+json">{json.dumps(data,ensure_ascii=False)}</script><style>body{{font-family:Arial;max-width:900px;margin:auto;padding:24px;line-height:1.8}}a{{display:inline-block;margin:8px}}img{{display:block}}</style></head><body><nav><a href="../../../index.html">المكتبة / Library</a><a href="../../../search.html">البحث / Search</a><a href="../{other}/">'+('English' if ar else 'العربية')+f'</a></nav><h1>{num}. {title}</h1><p>'+('ناصر ابن داوود' if ar else 'Nasser Ibn Dawood')+f'</p>{img}<p>{escape(book["description"][lang])}</p><section>{page_links(book,lang)}</section>{notice}<footer><a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a></footer></body></html>\n'
            textfile(ROOT/'books'/bid/lang/'index.html',page)
        catalogue['books'].append(book)
    # Mechanical rewrite of site resources. Do not touch manuscripts, image folders, Git or verification HTML.
    def replace(s):
        s=s.replace(OLD,BASE)
        for old,new in replacements.items():s=s.replace(old,new)
        return s
    html_ids={re.search(r'(?:id=|/d/)([\w-]+)',b[l]['html']).group(1) for b in old_books for l in ('ar','en') if b[l].get('html') and re.search(r'(?:id=|/d/)([\w-]+)',b[l]['html'])}
    def remove_anchor(m):
        a=m.group(0)
        href=re.search(r'href=[\"\']([^\"\']+)',a,re.I)
        if not href:return a
        h=href.group(1)
        if any(i in h for i in html_ids) or ('drive.google.com' in h and re.search(r'\bHTML\b',a,re.I)) or 'archive.org/details/' in h or re.search(r'/content\.html?(?:$|[?#])',h):return ''
        return a
    for p in ROOT.rglob('*'):
        if not p.is_file() or any(part in ('.git','scripts','content.files') for part in p.relative_to(ROOT).parts):continue
        if p.suffix.lower() not in ('.html','.js','.json','.xml','.md','.txt'):continue
        if p.name=='googlecf8d734095ac1dc2.html' or (p.suffix=='.txt' and 'books' in p.relative_to(ROOT).parts):continue
        original=p.read_text(encoding='utf-8-sig');s=replace(original)
        if p.suffix=='.html':s=re.sub(r'<a\b[^>]*>.*?</a>',remove_anchor,s,flags=re.I|re.S)
        if s!=original:textfile(p,s)
    # Remove HTML/Archive resources from all JSON catalogues while preserving metadata.
    def clean(obj):
        if isinstance(obj,dict):
            return {k:clean(v) for k,v in obj.items() if k!='txt_external' and not(k in ('html','archive') and isinstance(v,str) and v.startswith(('http','books/')))}
        if isinstance(obj,list):return [clean(v) for v in obj if v!='html']
        return replace(obj) if isinstance(obj,str) else obj
    for p in ROOT.rglob('*.json'):
        if '.git' in p.parts or 'scripts' in p.relative_to(ROOT).parts:continue
        try:obj=json.loads(p.read_text(encoding='utf-8-sig'))
        except json.JSONDecodeError:continue
        cleaned=clean(obj)
        if cleaned!=obj:write_json(p,cleaned)
    catalogue=clean(catalogue)
    catalogue['library'].update(total_books_arabic=112,total_books_english=112,total_books=224,formats=['txt','docx','pdf'],last_updated='2026-10-03')
    catalogue['last_updated']='2026-10-03'
    write_json(ROOT/'ai-index.json',catalogue)
    search=[]
    for b in catalogue['books']:
        item={k:copy.deepcopy(b[k]) for k in ('id','book_number','titles','description','metadata')}
        item['links']={lang:{'text':b[lang]['txt_direct'].replace(BASE,''),**({'cover':b[lang]['cover']} if b[lang].get('cover') else {})} for lang in ('ar','en')}
        search.append(item)
    write_json(ROOT/'search-index.json',{'books':search})
    # Keep the embedded offline catalogue in sync without changing search behavior.
    p=ROOT/'search.html';s=p.read_text(encoding='utf-8')
    s,n=re.subn(r'const booksData\s*=\s*\[.*?\];',lambda _: 'const booksData = '+json.dumps(search,ensure_ascii=False,indent=2)+';',s,count=1,flags=re.S)
    assert n==1
    s=s.replace("book.metadata.pages_ar : book.metadata.pages_en","(book.metadata.pages_ar ?? '—') : (book.metadata.pages_en ?? '—')")
    textfile(p,s)
    # Add static cards to existing listings, preserving current presentation and existing content.
    for lang,filename in [('ar','arabic-books.html'),('en','english-books.html')]:
        p=ROOT/filename;s=p.read_text(encoding='utf-8')
        pos=s.rfind('</section>');assert pos>=0
        cards='\n<!-- New books 70–112 -->\n'+''.join(listing(b,lang) for b in catalogue['books'][69:])
        s=s[:pos]+cards+s[pos:]
        s=re.sub(r'\b(?:68|69)(?=\s*(?:books|كتاب))','112',s)
        s=re.sub(r'(collectionSize[\"\s]+content=\")(?:68|69)(\")',r'\g<1>112\2',s)
        textfile(p,s)
    p=ROOT/'books.html';s=p.read_text(encoding='utf-8');pos=s.rfind('<footer>');assert pos>=0
    cards=''.join(f'<div class="book"><h2>{b["book_number"]}. {escape(b["titles"]["ar"])}</h2><h3>{escape(b["titles"]["en"])}</h3><p>العربية: {page_links(b,"ar")}</p><p>English: {page_links(b,"en")}</p><a href="books/{b["id"]}/ar/">صفحة الكتاب</a></div>\n' for b in catalogue['books'][69:])
    s=s[:pos]+cards+s[pos:];s=s.replace('138 إصدارًا (69 كتابًا بالعربية و69 بالإنجليزية)','224 إصدارًا (112 كتابًا بالعربية و112 بالإنجليزية)');textfile(p,s)
    p=ROOT/'index.html';s=p.read_text(encoding='utf-8')
    s=re.sub(r'\b69(?=\s*(?:كتاب|books|Volumes|مجلد)|\))','112',s)
    s=s.replace('138','224')
    # Home page intentionally remains curated; expose the complete updated catalogue.
    pos=s.rfind('</main>');s=s[:pos]+'<section><h2>الكتب الجديدة — New books</h2><p>43 كتابًا جديدًا، بترقيم 70–112.</p><a href="books-index.html">الفهرس الكامل — Full catalogue</a></section>\n'+s[pos:];textfile(p,s)
    for filename in ('sitemap.xml','sitemap-books.xml','sitemap-bing.xml'):
        p=ROOT/filename;root=ET.fromstring(p.read_text(encoding='utf-8'));ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
        urls={el.text for el in root.iter(ns+'loc')}
        for b in catalogue['books'][69:]:
            for lang in ('ar','en'):
                url=BASE+f'books/{b["id"]}/{lang}/'
                if url not in urls:
                    node=ET.SubElement(root,ns+'url');ET.SubElement(node,ns+'loc').text=url
        ET.register_namespace('',ns[1:-1]);p.write_bytes(ET.tostring(root,encoding='utf-8',xml_declaration=True))
write_json(ROOT/'scripts/migration-report.json',{'books':112,'language_editions':224,'new_books':43,'missing_drive_links':missing,'missing_covers':[{'number':b['book_number'],'id':b['id'],'language':l} for b in catalogue['books'][69:] for l in ('ar','en') if not b[l].get('cover')],'review_before_publication':[75,81,87,89,101,110],'old_google_links_preserved':all(catalogue['books'][i][l].get(k)==b[l].get(k) for i,b in enumerate(old_books) for l in ('ar','en') for k in ('docx','pdf_direct','pdf_external'))})
    print('Prepared 112 books / 224 editions. Missing new Drive links:',len(missing))
if __name__=='__main__':main()
