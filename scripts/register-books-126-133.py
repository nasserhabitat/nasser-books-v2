"""Register author-supplied books, preserving manuscripts and existing records."""
import argparse, hashlib, importlib.util, json, re, shutil, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from prepare_book_migration import paragraphs, W

DETAILS = {
126: ('Jinn_and_Devils_Quran_Volume_II', 'الجن والشياطين في القرآن — الجزء الثاني', 'Jinn and Devils in the Qur’an — Volume Two',
      'دراسة لدلالة الجن والتكليف وحدود السلطان، من الخلق الأول إلى الخفاء النسبي، تختبر الفرضيات بالموارد المقابلة وتفصل استنباط المؤلف عن النص القرآني.',
      'A study of jinn, moral responsibility, and limits of authority, distinguishing authorial hypotheses from Qur’anic evidence.'),
127: ('The_Mosque_and_the_House_in_Quranic', 'المسجد والبيت في اللسان القرآني', 'The Mosque and the House in Quranic Language',
      'دراسة سياقية مثانية في المكان والوعي والعمران، تعرض النماذج المعرفية بوصفها استنباطات بشرية قابلة للاختبار.',
      'A contextual and structural study of place, awareness, and civilization, distinguishing spatial meanings from interpretive models.'),
128: ('Rabb_al_Alamin', 'رَبُّ الْعَالَمِينَ وَرَبُّ «الْعَلِمِينَ»؟', 'Lord of the Worlds, and Lord of “Al-ʿIlmīn”?',
      'من هندسة الخلق والأمر إلى هندسة العلم والهداية؛ دراسة تدبرية بنيوية مفتوحة. عبارة «رب العَلِمين» سؤال تدبري للمؤلف وليست قراءة قرآنية مثبتة.',
      'From creation and command to knowledge and guidance. “Rabb al-ʿIlmīn” is the author’s contemplative question, not an established Qur’anic reading.'),
129: ('Isfar_AlSubh', 'إسفار الصبح المعرفي — قراءة لسانية روحية في هندسة الوعي القرآني', 'The Dawning of Understanding',
      'دراسة تطبيقية في سورة المزمل، تعرض قراءة المؤلف اللسانية والروحية في هندسة الوعي مع الفصل بين الشاهد القرآني والتأويل والنموذج.',
      'A linguistic and spiritual inquiry into Qur’anic awareness through Surat al-Muzzammil, distinguishing evidence, interpretation, and models.'),
130: ('death-vocabulary-in-quran-part2-106-B', 'الموت والميتة والأموات والموتى في القرآن — الجزء الثاني (106-B)', 'Death, the Dead, and Mortality in the Quran — Part II (106-B)',
      'هندسة المآل ودوائر الوعي وأطلس الفرضيات الممتدة خارج مدونة جذر (م و ت). يميز البحث النص والبيان والاستنباط الشبكي والنماذج التشغيلية، ويحفظ حالات الفرضيات المفتوحة.',
      'Engineering of destiny, consciousness trajectories, and the extended atlas of hypotheses, distinguishing text, inference, and operational models.'),
131: ('riba-quran-banking-vol3-96', 'الربا في القرآن والنظام المصرفي المعاصر — المجلد الثالث', 'Riba in the Qur’an and the Contemporary Banking System — Volume Three',
      'دراسة المصارف التقليدية والإسلامية والديون السيادية ومختبر المنتجات، من هندسة الاستحقاق إلى اختبار بنية المعاملة؛ أدوات التدقيق نماذج بحثية للمؤلف.',
      'Conventional and Islamic banking, sovereign debt, and structural auditing of financial products through the author’s research framework.'),
132: ('riba-quran-banking-vol4-96', 'الربا في القرآن والنظام المصرفي المعاصر — المجلد الرابع', 'Riba in the Qur’an and the Contemporary Banking System — Volume Four',
      'دراسة المنتجات المالية ومصفوفة المتغيرات الموحدة وإعادة الاختبار المستقل، مع إبقاء نتائج النماذج التشغيلية في مرتبتها البحثية.',
      'Financial products, the unified variable matrix, and independent re-testing, preserving the research status of operational models.'),
133: ('Al-Muddaththir-in-the-Qurani', 'المُدَّثِّر في اللسان القرآني — هندسة الإنذار والتطهير والتذكرة', 'Al-Muddaththir in the Qur’anic Language',
      'نسخة تحريرية معدة للنشر، تدرس شبكة الإنذار والتطهير والتذكرة في سورة المدثر، مع ملخص ودليل قراءة ومخططات بصرية، وتمييز البيان عن استنباط المؤلف.',
      'An editorial edition prepared for publication, studying warning, purification, and reminder, distinguishing textual statement from authorial inference.'),
}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--texts-root', type=Path, required=True)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('registration', Path(__file__).with_name('register-books-113-115.py'))
    r = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(r)
    manifest = json.loads(Path(__file__).with_name('books-126-133-sources.json').read_text(encoding='utf-8'))
    r.EXPECTED_COUNT, r.DATE = 125, manifest['checked_at']
    local_root, r.SOURCE = r.SOURCE, args.texts_root.resolve()
    r.SPECS = []
    manifest['assets'] = []
    for n, (bid, ar, en, da, de) in DETAILS.items():
        local = next(local_root.glob(str(n)+'-*'))
        ids = []
        r.SOURCE_FOLDERS[n] = str(n)
        r.EDITION_NOTES[n] = {
            'ar': 'النسخة الإنجليزية تكييف مفاهيمي مختصر وليست ترجمة حرفية كاملة؛ يبقى النص العربي المرجع الأساسي.',
            'en': 'Condensed conceptual English adaptation; the Arabic text remains the primary source for detailed analysis and references.'
        }
        for lang in ('ar', 'en'):
            folder = r.SOURCE / str(n) / lang
            files = [f for f in manifest['files'] if f['number'] == n and f['language'] == lang]
            assert files and all(f['public_readable'] for f in files)
            txt, source_hash = folder / ('supplied.txt' if (n == 128 and lang == 'en') or n == 130 else 'source.txt'), None
            if n == 128 and lang == 'ar':
                docx = folder / 'source.docx'
                expected = next(f for f in files if f['name'].endswith('.docx'))
                assert docx.stat().st_size == expected['size']
                source_hash = sha(docx)
                lines = paragraphs(docx)
                with zipfile.ZipFile(docx) as z:
                    for part in ('word/footnotes.xml', 'word/endnotes.xml'):
                        if part in z.namelist():
                            for p in ET.fromstring(z.read(part)).iter(W+'p'):
                                line = ''.join(t.text or '' for t in p.iter(W+'t'))
                                if line.strip(): lines.append(line)
                    math = list(ET.fromstring(z.read('word/document.xml')).iter('{http://schemas.openxmlformats.org/officeDocument/2006/math}t'))
                    assert not math, 'Review equation extraction'
                txt.write_text('\n\n'.join(lines)+'\n', encoding='utf-8')
                r.EDITION_NOTES[n][lang] += (' النص القابل للبحث مستخرج من Word؛ راجع الأصل للجداول والصور والتنسيق.' if lang == 'ar' else ' Searchable text is extracted from Word; consult the original for tables, images, and formatting.')
            else:
                expected = next(f for f in files if f['name'].endswith('.txt'))
                assert txt.stat().st_size == expected['size']
            cover_lang = 'ar' if n == 132 and lang == 'en' else lang
            candidates = list((local / cover_lang).glob('*.png')) or [p for p in local.glob('*.png') if re.search(r'-'+cover_lang+r'(?:-cover)?\.png$', p.name)]
            assert len(candidates) == 1, candidates
            cover = candidates[0]
            name = f'{bid}-{lang}-cover.png'
            shutil.copy2(cover, folder / name)
            r.SOURCE_TEXT_NAMES[(n, lang)] = txt.name
            r.SOURCE_COVER_NAMES[(n, lang)] = r.COVER_NAMES[(n, lang)] = name
            ids.extend(next((f['id'] for f in files if f['name'].endswith(ext)), None) for ext in ('.docx', '.pdf'))
            manifest['assets'].append({'number': n, 'id': bid, 'language': lang,
                'text_sha256': sha(txt), 'text_source': 'docx_extraction' if source_hash else 'original_drive_txt',
                'docx_sha256': source_hash, 'cover_source': str(cover.relative_to(local_root)),
                'cover_name': name, 'cover_sha256': sha(cover)})
        r.SPECS.append((n, bid, ar, en, da, de, ['اللسان القرآني', 'التدبر', 'QCROS'], ['Quranic language', 'QCROS'], ids))
    r.EDITION_NOTES[132]['en'] += ' The supplied Volume Four cover from the Arabic source folder is used with the author’s approval.'
    original_page = r.page
    def page(book, lang):
        html = original_page(book, lang)
        if not book[lang]['pdf_external']:
            html = re.sub(r'<noscript>.*?</noscript>', '<noscript>PDF غير متوفر لهذه النسخة بعد. / PDF is not available for this edition yet.</noscript>', html)
        return html
    r.page = page
    r.main()
    r.write('.gitattributes', r.read('.gitattributes') + '\n# Preserve new-book text bytes\n' + ''.join(f'books/{d[0]}/*/*.txt -text\n' for d in DETAILS.values()))
    manifest['notes'] = ['132 English filenames say vol3; text identifies Volume Four. Correct Volume Four English-language cover from Arabic source folder used by author approval.',
        'All new editions have supplied PDF links; 128 English and both 130 texts are original author-supplied TXT.',
        'Only 128 Arabic searchable text extracted from original Drive DOCX; documents unchanged.']
    r.dump('scripts/books-126-133-sources.json', manifest)
    readme = r.read('README.md').replace('تحققت صلاحية anyone/reader بتاريخ 2026-10-26', 'تحققت إتاحة القراءة العامة بتاريخ 2026-10-26')
    r.write('README.md', readme + '\nإضافة 126–133: جميع النسخ مرتبطة بملفات PDF. نص 128 العربي مستخرج من Word، وبقية نصوص الكتب الجديدة ملفات TXT أصلية من المؤلف. غلاف 132 الإنجليزي مأخوذ من مجلد المصدر العربي بموافقة المؤلف؛ الصورة نفسها إنجليزية وتحمل المجلد الرابع الصحيح؛ أسماء الملفات الإنجليزية تذكر vol3 بينما المتن يحدد المجلد الرابع.\n')

if __name__ == '__main__':
    main()
