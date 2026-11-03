"""Register four author-supplied books; preserve original manuscripts and prior records."""
import hashlib, importlib.util, json, re, shutil, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from prepare_book_migration import paragraphs, W

DETAILS = {
134: ('The-Beautiful-Names-in-Quranic-Part-II', 'الأسماء الحسنى في اللسان القرآني — الجزء الثاني', 'The Beautiful Names in Qur’anic Discourse — Part II',
      'بحث مرحلي في البنية والاقتران والوظيفة، يميز النص والبيان والاستنباط والفرضية والنموذج التشغيلي، دون ادعاء اكتمال الحصر أو التحقيق.',
      'An ongoing study of structure, pairing, and function, distinguishing textual evidence, explanation, inference, hypotheses, and operational models.'),
135: ('Hajj_Quranic_Reflections', 'تدبّرات في آيات الحج — الشعيرة ومقاصدها وآفاق المعرفة والعمران', 'Qur’anic Reflections on Hajj',
      'الكتاب الثاني من ثلاثية الحج القرآني؛ دراسة استقرائية وفق QCROS، تقابل الفرضيات بالآيات وسياقاتها وتبيّن حدود الاستنباط والنماذج البشرية.',
      'The second book of the Qur’anic Hajj trilogy: contextual inquiry using QCROS, testing hypotheses against verses and distinguishing evidence from interpretive models.'),
136: ('Philosophy_of_Hajj_and_Stewardship', 'فلسفة الحج والاستخلاف', 'Philosophy of Hajj and Stewardship',
      'من تزكية النفس ونقد الطقسية إلى مدارس العلم ونهوض العمران؛ الكتاب الثالث من ثلاثية الحج، يعرض قراءات فلسفية ومقاصدية ونماذج قابلة للمراجعة.',
      'From self-purification and the critique of ritualism to schools of knowledge and human flourishing: philosophical inquiry in the third book of the Hajj trilogy.'),
137: ('Lisan-al-Tasami', 'لسان التسامي: نحو قراءة باطنية-تكاشفية للنص القرآني والوجود', 'The Language of Transcendence — Lisan al-Tasami',
      'دراسة في القراءة التكاشفية والتأويل الرمزي والتحليل الروحي، تعرض اجتهاد المؤلف في العلاقة بين النص والوعي والوجود.',
      'An inquiry into unveiling interpretation, symbolism, and spiritual analysis, presenting the author’s reading of text, awareness, and existence.'),
}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    spec=importlib.util.spec_from_file_location('registration',Path(__file__).with_name('register-books-113-115.py'))
    r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
    manifest=json.loads(Path(__file__).with_name('books-134-137-sources.json').read_text(encoding='utf8'))
    originals=r.SOURCE
    r.SOURCE=Path('C:/Users/nasse/.codex/visualizations/2026/08/28/01a0480f-df98-7951-bb38-a60dec78bce5/books-134-137')
    r.EXPECTED_COUNT=133;r.DATE='2026-11-03';r.SPECS=[];manifest['assets']=[]
    for n,(bid,ar,en,da,de) in DETAILS.items():
        local=next(originals.glob(str(n)+'-*'));ids=[];r.SOURCE_FOLDERS[n]=str(n)
        r.EDITION_NOTES[n]={'ar':'النسخة الإنجليزية تكييف مفاهيمي مختصر؛ يبقى النص العربي المرجع الأساسي.',
                            'en':'Condensed conceptual adaptation; the Arabic work remains the primary source.'}
        for lang in ('ar','en'):
            files=[f for f in manifest['files'] if f['number']==n and f['language']==lang]
            for f in files:
                p=next(local.rglob(f['name']));assert p.stat().st_size==f['size'],p
                f['local_sha256']=sha(p);f['public_readable']=True
            folder=r.SOURCE/str(n)/lang;folder.mkdir(parents=True,exist_ok=True)
            txt=folder/'source.txt';t=next((f for f in files if f['name'].endswith('.txt')),None)
            if t: shutil.copy2(next(local.rglob(t['name'])),txt)
            else:
                doc=next(local.rglob(next(f['name'] for f in files if f['name'].endswith('.docx'))))
                lines=paragraphs(doc)
                with zipfile.ZipFile(doc) as z:
                    for part in ('word/footnotes.xml','word/endnotes.xml'):
                        if part in z.namelist():
                            for p in ET.fromstring(z.read(part)).iter(W+'p'):
                                text=''.join(t.text or '' for t in p.iter(W+'t'))
                                if text.strip():lines.append(text)
                    math=ET.fromstring(z.read('word/document.xml')).findall('.//{http://schemas.openxmlformats.org/officeDocument/2006/math}t')
                    assert not math,'Review equation extraction'
                txt.write_text('\n\n'.join(lines)+'\n',encoding='utf8')
                r.EDITION_NOTES[n][lang]+= (' النص القابل للبحث مستخرج من Word؛ راجع الأصل للجداول والصور والتنسيق. PDF غير متاح بعد.' if lang=='ar' else ' Search text extracted from Word; consult the original for tables, images, and formatting. PDF is not yet available.')
            covers=[p for p in local.rglob('*.png') if '-'+lang+'-cover' in p.name];assert len(covers)==1,covers
            cover=folder/f'{bid}-{lang}-cover.png';shutil.copy2(covers[0],cover)
            r.SOURCE_TEXT_NAMES[n,lang]='source.txt';r.SOURCE_COVER_NAMES[n,lang]=r.COVER_NAMES[n,lang]=cover.name
            ids.extend(next((f['id'] for f in files if f['name'].endswith(ext)),None) for ext in ('.docx','.pdf'))
            manifest['assets'].append({'number':n,'language':lang,'text_source':'original_drive_txt' if t else 'docx_extraction', 'text_sha256':sha(txt),'cover_sha256':sha(cover)})
        if n==134:
            r.EDITION_NOTES[n]['ar']+=' يصف الكتاب حصيلة مرحلية، ولا يعلن اكتمال الحصر الشامل أو مطابقة جميع الإحالات.'
            r.EDITION_NOTES[n]['en']+=' Work in progress; comprehensive enumeration and reference verification are not claimed complete.'
        r.SPECS.append((n,bid,ar,en,da,de,['اللسان القرآني','التدبر'],['Quranic language','Contemplation'],ids))
    original_page=r.page
    def page(b,lang):
        html=original_page(b,lang)
        if not b[lang]['pdf_external']:html=re.sub(r'<noscript>.*?</noscript>','<noscript>PDF غير متاح بعد. / PDF is not yet available.</noscript>',html)
        return html
    r.page=page;r.main()
    r.write('.gitattributes',r.read('.gitattributes')+'\n# Preserve author-supplied and extracted text bytes for books 134-137\n'+''.join(f'books/{d[0]}/*/*.txt -text\n' for d in DETAILS.values()))
    r.write('README.md',r.read('README.md').replace('تحققت صلاحية anyone/reader بتاريخ 2026-11-03','تحققت إتاحة القراءة العامة بتاريخ 2026-11-03')+'\nإضافة 134–137: PDF متاح للكتابين 135 و136 بلغتيهما. نصوص 134 و137 مستخرجة من Word، وملفات PDF لهما غير متاحة بعد. النسخ الإنجليزية تكييفات مفاهيمية مختصرة، والكتاب 134 بحث مرحلي.\n')
    r.dump('scripts/books-134-137-sources.json',manifest)

if __name__=='__main__':main()
