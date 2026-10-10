"""One-shot addition of book 118; never changes author sources or Drive objects.

Arabic searchable text is extracted from the supplied DOCX. English TXT and
covers are copied byte-for-byte. Only TXT/PNG and book pages enter the site.
"""
import importlib.util
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

BOOK_ID = 'Engineering_Reflection_Qur’anic_Linguistic_Inquiry_and_the_Numerical_Measure_19'
SOURCE_STEM = '118_' + BOOK_ID
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


def extract_text(docx):
    """Read visible OOXML text, including table cells, without editing the DOCX."""
    with zipfile.ZipFile(docx) as archive:
        root = ET.fromstring(archive.read('word/document.xml'))
        if root.findall('.//' + W + 'del') or root.findall('.//' + W + 'ins'):
            raise ValueError('Tracked changes require an explicit extraction policy.')
        if root.findall('.//{http://schemas.openxmlformats.org/officeDocument/2006/math}oMath'):
            raise ValueError('Native equations need a dedicated text extraction policy.')
        body = root.find(W + 'body')
        numbering = ET.fromstring(archive.read('word/numbering.xml'))
        abstract = {a.get(W + 'abstractNumId'): a for a in numbering.findall(W + 'abstractNum')}
        numbers = {n.get(W + 'numId'): n for n in numbering.findall(W + 'num')}
        counters = {}
        lines = []
        for paragraph in body.iter(W + 'p'):
            pieces = []
            for element in paragraph.iter():
                if element.tag == W + 't':
                    pieces.append(element.text or '')
                elif element.tag == W + 'tab':
                    pieces.append('\t')
                elif element.tag in (W + 'br', W + 'cr'):
                    pieces.append('\n')
            prefix = ''
            num = paragraph.find(W + 'pPr/' + W + 'numPr')
            if num is not None:
                num_id = num.find(W + 'numId').get(W + 'val')
                level_element = num.find(W + 'ilvl')
                level = int(level_element.get(W + 'val')) if level_element is not None else 0
                definition = numbers[num_id]
                if definition.findall(W + 'lvlOverride'):
                    raise ValueError('Numbering overrides require an explicit extraction policy.')
                levels = {int(l.get(W + 'ilvl')): l for l in abstract[definition.find(W + 'abstractNumId').get(W + 'val')].findall(W + 'lvl')}
                current = levels[level]
                fmt = current.find(W + 'numFmt').get(W + 'val')
                if fmt not in ('bullet', 'decimal'):
                    raise ValueError('Unsupported numbering format: ' + fmt)
                for key in list(counters):
                    if key[0] == num_id and key[1] > level:
                        del counters[key]
                key = (num_id, level)
                start = int(current.find(W + 'start').get(W + 'val'))
                counters[key] = counters.get(key, start - 1) + 1
                label = current.find(W + 'lvlText').get(W + 'val')
                label = re.sub(r'%([1-9])', lambda m: str(counters.get((num_id, int(m[1]) - 1), int(levels[int(m[1]) - 1].find(W + 'start').get(W + 'val')))), label)
                prefix = '  ' * level + label + ' '
            lines.append(prefix + ''.join(pieces))
        # This source has no footnotes, equations or tracked changes. Do not
        # silently omit these if a future source revision introduces them.
        for part in ('word/footnotes.xml', 'word/endnotes.xml'):
            if part in archive.namelist():
                notes = ET.fromstring(archive.read(part))
                if any(n.findall('.//' + W + 't') for n in notes
                       if n.get(W + 'id', '0') not in ('-1', '0')):
                    raise ValueError('Notes require a dedicated extraction policy.')
    return '\n'.join(lines) + '\n'


def main():
    spec = importlib.util.spec_from_file_location('registration', Path(__file__).with_name('register-books-113-115.py'))
    registration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(registration)
    source = registration.SOURCE / ('118-' + BOOK_ID)
    arabic = extract_text(source / 'ar' / (SOURCE_STEM + '-ar.docx'))
    assert arabic.startswith('هندسة التدبر: فقه اللسان والختم السيبراني للوحي')
    registration.EXPECTED_COUNT = 117
    registration.SOURCE_FOLDERS = {118: 'b118'}
    registration.DATE = '2026-10-10'
    registration.COVER_NAMES = {(118, lang): BOOK_ID + '-cover-' + lang + '.png' for lang in ('ar', 'en')}
    registration.EDITION_NOTES = {118: {
        'ar': 'النسخة الإنجليزية تكييف معنوي مختصر؛ يبقى النص العربي المرجع الأساسي للتحليل التفصيلي.',
        'en': 'This English edition is a meaning-centered condensed adaptation. The complete Arabic manuscript remains the primary source for detailed analysis.'
    }}
    registration.SPECS = [(
        118, BOOK_ID,
        'هندسة التدبر: فقه اللسان والختم السيبراني للوحي',
        'Engineering Reflection: Qur’anic Linguistic Inquiry and the Numerical Measure 19',
        'منظومة التشغيل بين الكود اللغوي والميزان العددي 19؛ دراسة تجمع فقه اللسان القرآني والقراءة البنيوية والحساب وفق قاعدة معلنة، مع التمييز بين النص والبيان والنتيجة الحسابية واستنباط المؤلف. النسخة الإنجليزية تكييف معنوي مختصر.',
        'A meaning-centered condensed adaptation connecting Qur’anic linguistic inquiry, structural reading, and the numerical measure 19. It distinguishes Qur’anic text, linguistic explanation, arithmetic results, and the author’s interpretive models; the Arabic manuscript remains the primary source.',
        ['التدبر', 'فقه اللسان القرآني', 'المثاني', 'الرسم القرآني', 'الميزان العددي', '19', 'QCROS'],
        ['Reflection', 'Qur’anic linguistic inquiry', 'Numerical measure 19', 'Rasm', 'Mathani', 'QCROS'],
        ['1W_PY9DRfFFVoMYsmMZaMYGgzkoRltz3X', '1CKB_JYyuMTO81Zo3H90qF017zC8xZFfl',
         '1gndWasrjTXo9gPNpmxwu0CCTl064ds6C', '1eoxFy4bQBsOCOTanGk-wzRQ9OKg9jUN8']
    )]
    # Stage extraction within a temporary folder, never in the author workspace.
    with tempfile.TemporaryDirectory(prefix='.book118-', dir=registration.ROOT) as temporary:
        registration.SOURCE = Path(temporary)
        for lang in ('ar', 'en'):
            destination = Path(temporary) / 'b118' / lang
            destination.mkdir(parents=True)
            covers = list((source / lang).glob('*.png'))
            assert len(covers) == 1
            shutil.copy2(covers[0], destination / covers[0].name)
            text_path = destination / ('118-' + BOOK_ID + '-' + lang + '.txt')
            if lang == 'ar':
                text_path.write_text(arabic, encoding='utf-8')
            else:
                shutil.copy2(source / lang / (SOURCE_STEM + '-en.txt'), text_path)
        registration.main()
    readme = registration.ROOT / 'README.md'
    text = readme.read_text(encoding='utf-8')
    text = text.replace('إضافة الكتب 118–118', 'إضافة الكتاب 118').replace('للكتب 118–118، ونصوصها وأغلفتها', 'للكتاب 118، ونصوصه وأغلفته')
    readme.write_text(text, encoding='utf-8')


if __name__ == '__main__':
    main()
