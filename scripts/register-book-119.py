"""Register book 119 without editing author sources or Drive sharing.

Only supplied TXT and PNG assets enter the site. Word/PDF remain on Drive;
file names, sizes and anyone/reader permissions checked on 2026-10-11.
"""
import importlib.util
from pathlib import Path


def main():
    spec = importlib.util.spec_from_file_location('registration', Path(__file__).with_name('register-books-113-115.py'))
    registration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(registration)
    registration.EXPECTED_COUNT = 118
    registration.DATE = '2026-10-11'
    registration.COVER_NAMES = {(119, lang): f'119-fiqh-al-ilm-wal-lisan-part2-{lang}-cover.png' for lang in ('ar', 'en')}
    registration.EDITION_NOTES = {119: {
        'ar': 'النسخة الإنجليزية تكييف مفاهيمي مختصر، وليست ترجمة حرفية؛ يبقى النص العربي المرجع الأساسي للتحليل التفصيلي والإحالات.',
        'en': 'This is a condensed conceptual English adaptation, not a word-for-word translation. The Arabic edition remains the primary source for detailed analysis and references.'
    }}
    registration.SPECS = [(
        119, 'fiqh-al-ilm-wal-lisan-part2',
        'فقه العلم واللسان القرآني — الجزء الثاني: شبكة العلم والاستخلاف والحضارة والأخلاق',
        'Understanding Knowledge and the Qurʾanic Language — Part Two: Knowledge Networks, Stewardship, Civilization and Ethics',
        'دراسة في بناء شبكة العلم وصلاتها بالاستخلاف والحضارة والأخلاق، تتناول الرزق المعرفي والذكاء الاصطناعي وحوكمة المعرفة وميثاقًا مقترحًا لشبكة العلم، مع التمييز بين الشواهد القرآنية والمقترحات التفسيرية والتطبيقات الافتراضية. النسخة الإنجليزية تكييف مفاهيمي مختصر.',
        'A condensed conceptual adaptation exploring knowledge networks, stewardship, civilization and ethics, epistemic provision, artificial intelligence, knowledge governance, and a proposed network charter. It distinguishes Qurʾanic evidence from interpretive proposals and hypothetical applications; the Arabic edition remains the primary source.',
        ['فقه العلم', 'اللسان القرآني', 'شبكة العلم', 'الاستخلاف', 'الحضارة', 'الأخلاق', 'الرزق المعرفي', 'الذكاء الاصطناعي', 'حوكمة المعرفة'],
        ['Knowledge networks', 'Qurʾanic language', 'Stewardship', 'Civilization', 'Ethics', 'Epistemic provision', 'Artificial intelligence', 'Knowledge governance'],
        ['1txg0IarnXFM19OXd19q5jvQqAnVPjbMI', '14sZWmJFpnTFdPj2LCqsEu9G4a2VTcTK-',
         '1kSyl7OL9Wxv9Qu-dqg94vCvToNXiidmE', '1UWV8drx60jAH-8GhUwACfW6sfDB94Z3Z']
    )]
    registration.main()
    readme = registration.ROOT / 'README.md'
    text = readme.read_text(encoding='utf-8')
    text = text.replace('إضافة الكتب 119–119', 'إضافة الكتاب 119').replace('للكتب 119–119، ونصوصها وأغلفتها', 'للكتاب 119، ونصوصه وأغلفته')
    marker = '## التحديث الشهري'
    note = 'نُقلت نصوص الكتاب 119 وأغلفته كما وردت دون تغيير المحتوى. النسخة الإنجليزية تكييف مفاهيمي مختصر، وقد أُثبت التنبيه في صفحات الكتاب وبياناته. بيان الإتاحة داخلها يصف العدد السابق (118 كتابًا) وصيغًا تاريخية؛ بقي النص الأصلي كما هو.\n\n'
    text = text.replace(marker, note + marker, 1)
    readme.write_text(text, encoding='utf-8')


if __name__ == '__main__':
    main()
