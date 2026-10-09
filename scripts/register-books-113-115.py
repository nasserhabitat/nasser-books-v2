"""Append author-supplied books without rewriting existing records or manuscripts.

Drive IDs were matched to numbered files and anyone/reader metadata on 2026-10-09.
Only TXT and PNG assets are copied; Word/PDF remain external resources.
"""
import copy
import json
import re
import shutil
from collections import Counter
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parents[1] / 'google_books'
BASE = 'https://nasserhabitat.github.io/nasser-books-v2/'
DATE = '2026-10-09'
EXPECTED_COUNT = 112
SOURCE_FOLDERS = {}
SOURCE_TEXT_NAMES = {}
COVER_NAMES = {(114, lang): f'Fiqh_al-Wijdan-{lang}-cover.png' for lang in ('ar', 'en')}
EDITION_NOTES = {}
SPECS = [
    (113, 'Engineering_Transgression_Temptation_and_the_Tree',
     'هندسة المخالفة والإغواء والشجرة في القرآن',
     "Engineering Transgression, Temptation, and the Tree in the Qur'an",
     'دراسة بنيوية في قصة آدم وإبليس: من الأمر والحد إلى الخلد والسوءة واللباس، مع تمييز الاستنباط والفرضيات عن النص القرآني.',
     'A structural study of Adam and Iblis, from command and boundary to immortality, exposure, and garment, distinguishing textual evidence from hypotheses.',
     ['آدم', 'إبليس', 'الشجرة', 'الإغواء', 'اللباس'],
     ['Adam', 'Iblis', 'Tree', 'Temptation', 'Garment'],
     ['15Rk5F-tU0tSTDhRXsf4C3_zbVdnghpk2', '1plDwIheeqLsravNDSNicMy0SGJykkw4m',
      '1sfih_LkbvFmRIRjDvWgssLeq7gIFsJBT', '10tN7_xImyOox7oRNLdD1UdV8C6y82vxW']),
    (114, 'Fiqh_al-Wijdan',
     'فقه الوجدان في اللسان القرآني',
     'The Jurisprudence of Human Consciousness in the Qur’anic Language',
     'هندسة المودة والسكن والكرامة في العلاقة الإنسانية؛ دراسة بنيوية وفق QCROS ونظام المثاني، تعرض نموذج الكرامة الوجدانية بوصفه مرشحًا قابلًا للاختبار لا قانونًا قرآنيًا نهائيًا.',
     'The architecture of affection, tranquility, and dignity in human relationships: a structural study using QCROS and the Mathani system, presenting testable models rather than final Qur’anic laws.',
     ['الوجدان', 'المودة', 'السكن', 'الكرامة', 'الميزان', 'QCROS'],
     ['Consciousness', 'Affection', 'Tranquility', 'Dignity', 'QCROS', 'Mathani'],
     ['13A75uXXW4peYL1V3WSBvE2h2qoRe15FS', '1kvAYbtqKe3vearLbD2TE5ihyKK75BKI9',
      '1HsVPgLaWxnP2PcBKpNOrF206VnH7yEjU', '1oMq2lhTVxOVpgNMsR1kaEyRX7ffMawPD']),
    (115, 'SHIRK_Engineering_of_Illusion',
     'الشِّرْك: هندسة الوهم وتحرير الوعي الإنساني',
     'SHIRK: The Engineering of Illusion and the Liberation of Human Awareness',
     'دراسة بنيوية لشبكة الشرك والمرجعية والولاء والتوجه، وفق فقه اللسان القرآني ومنهج QCROS ونظام المثاني، مع فصل النماذج النفسية والحضارية عن الخبر القرآني.',
     'A structural study of shirk, reference, allegiance, and orientation using Qur’anic linguistic jurisprudence, QCROS, and Mathani, separating contemporary models from Qur’anic statements.',
     ['الشرك', 'التوحيد', 'الوعي', 'المرجعية', 'QCROS', 'المثاني'],
     ['Shirk', 'Tawhid', 'Awareness', 'Reference', 'QCROS', 'Mathani'],
     ['1LWPnPCsXavJc6RVO7Oht8ahRLfdvXIR6', '1o5IpKPHhQwAYtTwda3cLkF_sOA_a2M0G',
      '1lzGr87t_9KV3scngQUk4VG_ZKPLRd-QS', '1FEo2HIuVgryIsudhsE6j9UFOjVvOghTO']),
]


def read(name):
    return (ROOT / name).read_text(encoding='utf-8-sig')


def write(name, text):
    (ROOT / name).write_text(text, encoding='utf-8')


def dump(name, obj):
    write(name, json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def links(book, lang):
    return ' '.join(f'<a href="{escape(book[lang][key], quote=True)}" target="_blank" rel="noopener noreferrer">{label}</a>'
                    for key, label in [('txt_direct', 'TXT'), ('docx', 'Word — Google Drive'), ('pdf_external', 'PDF — Google Drive')])


def card(book, lang):
    title = escape(book['titles'][lang])
    return f'<article class="book-card" data-lang="{lang}"><div class="book-cover"><img src="{book[lang]["cover"]}" alt="{title}" loading="lazy"></div><div class="book-info"><h2>{book["book_number"]}. {title}</h2><p>{escape(book["description"][lang])}</p><div class="book-actions"><a href="books/{book["id"]}/{lang}/">'+('عرض الكتاب' if lang == 'ar' else 'Book page')+f'</a></div><div class="download-links">{links(book, lang)}</div></div></article>\n'


def page(book, lang):
    title = book['titles'][lang]
    url = BASE + f'books/{book["id"]}/{lang}/'
    schema = {'@context': 'https://schema.org', '@type': 'Book', 'name': title,
              'description': book['description'][lang], 'inLanguage': lang, 'url': url,
              'image': BASE + book[lang]['cover'], 'isAccessibleForFree': True,
              'author': {'@type': 'Person', 'name': 'ناصر ابن داوود' if lang == 'ar' else 'Nasser Ibn Dawood'},
              'license': 'https://creativecommons.org/licenses/by-sa/4.0/'}
    cover = Path(book[lang]['cover']).name
    return f'''<!doctype html>
<html lang="{lang}" dir="{'rtl' if lang == 'ar' else 'ltr'}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title><meta name="description" content="{escape(book['description'][lang], quote=True)}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="ar" href="{BASE}books/{book['id']}/ar/">
<link rel="alternate" hreflang="en" href="{BASE}books/{book['id']}/en/">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
<link rel="stylesheet" href="../../../assets/pdf-reader.css"><script defer src="../../../assets/pdf-reader.js"></script>
<style>body{{font:18px/1.8 system-ui;margin:auto;padding:24px;max-width:1000px;background:#f6f4ed;color:#222}}main{{background:white;padding:24px;border-radius:12px}}a{{color:#075a8c}}nav,.resources{{display:flex;flex-wrap:wrap;gap:18px}}.cover{{max-width:100%;width:320px;height:auto}}footer{{margin-top:24px}}</style>
</head><body><nav><a href="../../../index.html">المكتبة / Library</a><a href="../../../search.html">البحث / Search</a><a href="../{'en' if lang == 'ar' else 'ar'}/">{'English' if lang == 'ar' else 'العربية'}</a></nav>
<main><h1>{book['book_number']}. {escape(title)}</h1><img class="cover" src="{cover}" alt="{escape(title, quote=True)}"><p>{escape(book['description'][lang])}</p>
{('<p role="note">'+escape(EDITION_NOTES.get(book['book_number'], {}).get(lang, ''))+'</p>') if EDITION_NOTES.get(book['book_number'], {}).get(lang) else ''}
<div class="resources">{links(book, lang)}</div>
<!-- library-pdf-reader:start --><section id="pdf-reader" class="pdf-reader" data-pdf-reader="book" data-book-id="{book['id']}" data-language="{lang}"><h2>قراءة PDF داخل الموقع / Read the PDF on this website</h2><p>جارٍ تجهيز القارئ… / Preparing the reader…</p><noscript><a href="{escape(book[lang]['pdf_external'], quote=True)}">PDF — Google Drive</a></noscript></section><!-- library-pdf-reader:end -->
</main><footer>ناصر ابن داوود / Nasser Ibn Dawood · <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a></footer></body></html>
'''


def main():
    cat = json.loads(read('ai-index.json'))
    original = copy.deepcopy(cat['books'])
    assert len(original) == EXPECTED_COUNT, 'Already integrated or catalogue changed: inspect before running.'
    assert not ({b['id'] for b in original} & {s[1] for s in SPECS}), 'Duplicate book ID'
    assert not ({b['book_number'] for b in original} & {s[0] for s in SPECS}), 'Duplicate book number'
    additions = []
    # Validate every source first, before changing the catalogue or copying assets.
    for number, bid, *_ in SPECS:
        for lang in ('ar', 'en'):
            folder = SOURCE / SOURCE_FOLDERS.get(number, f'{number}-{bid}') / lang
            assert (folder / SOURCE_TEXT_NAMES.get((number, lang), f'{number}-{bid}-{lang}.txt')).stat().st_size > 0
            assert len(list(folder.glob('*.png'))) == 1, folder
    for number, bid, ar, en, da, de, ta, te, ids in SPECS:
        b = {'id': bid, 'book_number': number, 'titles': {'ar': ar, 'en': en},
             'description': {'ar': da, 'en': de},
             'metadata': {'author': 'ناصر ابن داوود', 'category': 'quranic_studies',
                          'language_ar': 'arabic', 'language_en': 'english', 'ai_accessible': True,
                          'structured_data': True, 'source_status': 'author_supplied',
                          'pages_ar': None, 'pages_en': None, 'topics_ar': ta, 'topics_en': te}}
        for i, lang in enumerate(('ar', 'en')):
            source = SOURCE / SOURCE_FOLDERS.get(number, f'{number}-{bid}') / lang
            dest = ROOT / 'books' / bid / lang
            dest.mkdir(parents=True, exist_ok=True)
            name = f'{number}-{bid}-{lang}.txt'
            cover = next(source.glob('*.png'))
            source_text = source / SOURCE_TEXT_NAMES.get((number, lang), name)
            # Book 113 already has identical covers under an earlier filename.
            existing_cover = dest / f'{bid}-{lang}-cover.png'
            if existing_cover.exists():
                assert existing_cover.read_bytes() == cover.read_bytes()
                cover = existing_cover
            cover_name = COVER_NAMES.get((number, lang), cover.name)
            for asset, target_name in ((source_text, name), (cover, cover_name)):
                target = dest / target_name
                if target.exists():
                    assert target.read_bytes() == asset.read_bytes(), f'Different existing asset: {target}'
                else:
                    shutil.copy2(asset, target)
            b[lang] = {'txt_direct': BASE + f'books/{bid}/{lang}/{name}',
                       'cover': f'books/{bid}/{lang}/{cover_name}',
                       'docx': 'https://drive.google.com/uc?export=download&id=' + ids[i*2],
                       'pdf_external': 'https://drive.google.com/uc?export=download&id=' + ids[i*2+1]}
        b['cover_image'] = BASE + b['ar']['cover']
        if number in EDITION_NOTES:
            b['metadata']['edition_notes'] = EDITION_NOTES[number]
        for lang in ('ar', 'en'):
            target = f'books/{bid}/{lang}/index.html'
            assert not (ROOT / target).exists(), target
            write(target, page(b, lang))
        additions.append(b)
    cat['books'].extend(additions)
    assert cat['books'][:EXPECTED_COUNT] == original, 'Existing metadata/links must be untouched.'
    count = len(cat['books'])
    cat['library'].update(total_books_arabic=count, total_books_english=count,
                          total_books=count*2, last_updated=DATE)
    cat['last_updated'] = DATE
    dump('ai-index.json', cat)
    search = json.loads(read('search-index.json'))
    for b in additions:
        item = {k: copy.deepcopy(b[k]) for k in ('id', 'book_number', 'titles', 'description', 'metadata')}
        item['links'] = {lang: {'text': b[lang]['txt_direct'].removeprefix(BASE), 'cover': b[lang]['cover']} for lang in ('ar', 'en')}
        search['books'].append(item)
    dump('search-index.json', search)
    s, n = re.subn(r'const booksData\s*=\s*\[.*?\];', lambda _: 'const booksData = '+json.dumps(search['books'], ensure_ascii=False, indent=2)+';', read('search.html'), count=1, flags=re.S)
    assert n == 1
    write('search.html', s)
    for lang, file in [('ar', 'arabic-books.html'), ('en', 'english-books.html')]:
        s = read(file)
        pos = s.index('<article class="book-card"')
        s = s[:pos] + ''.join(card(b, lang) for b in reversed(additions)) + s[pos:]
        s = re.sub(r'\b'+str(EXPECTED_COUNT)+r'(?=\s*(?:books|كتاب|Volumes))', str(count), s)
        write(file, s)
    s = read('books.html')
    pos = s.index('<div class="book">')
    cards = ''.join(f'<div class="book"><h2>{b["book_number"]}. {escape(b["titles"]["ar"])}</h2><h3>{escape(b["titles"]["en"])}</h3><p>العربية: {links(b,"ar")}</p><p>English: {links(b,"en")}</p><a href="books/{b["id"]}/ar/">صفحة الكتاب</a></div>\n' for b in reversed(additions))
    write('books.html', (s[:pos]+cards+s[pos:]).replace(f'{EXPECTED_COUNT*2} إصدارًا ({EXPECTED_COUNT} كتابًا بالعربية و{EXPECTED_COUNT} بالإنجليزية)', f'{count*2} إصدارًا ({count} كتابًا بالعربية و{count} بالإنجليزية)'))
    s = read('index.html')
    s = re.sub(r'\b'+str(EXPECTED_COUNT)+r'(?=\s*(?:كتاب|books|Volumes|مجلد)|\))', str(count), s)
    s = re.sub(r'\b'+str(EXPECTED_COUNT*2)+r'(?=\s|\))', str(count*2), s)
    s = s.replace(f'{EXPECTED_COUNT-69} كتابًا جديدًا، بترقيم 70–{EXPECTED_COUNT}.', f'{count-69} كتابًا جديدًا، بترقيم 70–{count}.')
    marker = '<h2>الكتب الجديدة — New books</h2>'
    s = s.replace(marker, marker + '<ul>' + ''.join(f'<li><a href="books/{b["id"]}/ar/">{b["book_number"]}. {escape(b["titles"]["ar"])}</a> · <a href="books/{b["id"]}/en/">English</a></li>' for b in reversed(additions)) + '</ul>')
    write('index.html', s)
    for file in ('sitemap.xml', 'sitemap-books.xml', 'sitemap-bing.xml'):
        s = read(file)
        urls = ''.join(f'  <url><loc>{BASE}books/{b["id"]}/{lang}/</loc></url>\n' for b in additions for lang in ('ar','en'))
        assert s.count('</urlset>') == 1
        write(file, s.replace('</urlset>', urls + '</urlset>'))
    pdf = json.loads(read('assets/pdf-reader-catalog.json'))
    for b in additions:
        for lang in ('ar','en'):
            pdf['editions'].append({'number': b['book_number'], 'book_id': b['id'], 'language': lang,
                                    'title': b['titles'][lang], 'status': 'ready',
                                    'drive_id': b[lang]['pdf_external'].split('id=')[-1]})
    pdf['updated_at'] = DATE
    pdf['summary'] = dict(Counter(e['status'] for e in pdf['editions']))
    pdf['summary'].setdefault('pending', 0)
    dump('assets/pdf-reader-catalog.json', pdf)
    write('api/ai-access/index.json', re.sub(r'\b'+str(EXPECTED_COUNT)+r'(?=\s*كتاب)', str(count), read('api/ai-access/index.json')))
    s = read('README.md').replace(f'**{EXPECTED_COUNT} كتابًا و{EXPECTED_COUNT*2} نسخة لغوية**', f'**{count} كتابًا و{count*2} نسخة لغوية**')
    s = s.replace(f'الكتب الـ{EXPECTED_COUNT}', f'الكتب الـ{count}')
    s = s.replace(f'منها {EXPECTED_COUNT-69} كتابًا جديدًا بترقيم 70–{EXPECTED_COUNT}', f'منها {count-69} كتابًا جديدًا بترقيم 70–{count}')
    label=f'{additions[0]["book_number"]}–{additions[-1]["book_number"]}'
    s = s.replace('## التحديث الشهري', f'## إضافة الكتب {label}\n\nأضيفت صفحات عربية وإنجليزية للكتب {label}، ونصوصها وأغلفتها إلى الفهرس والبحث والقوائم وخرائط الموقع. روابط Word وPDF مطابقة للملفات في Google Drive؛ تحققت صلاحية anyone/reader بتاريخ {DATE} دون تغيير المشاركة. بقيت بيانات وروابط الكتب 1–{EXPECTED_COUNT} كما هي.\n\n## التحديث الشهري', 1)
    write('README.md', s)
    print(f'Integrated {len(additions)} books: {count} books / {count*2} language editions; existing {EXPECTED_COUNT} records preserved.')


if __name__ == '__main__':
    main()
