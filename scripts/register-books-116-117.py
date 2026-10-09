"""Register distinct editions, preserving Drive names/IDs and author text bytes."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('registration', Path(__file__).with_name('register-books-113-115.py'))
registration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(registration)
registration.EXPECTED_COUNT = 115
registration.SOURCE_FOLDERS = {116: '116-SHIRK_Engineering_of_Illusion', 117: '117-THE_BOOK_AS_WITNESS'}
registration.SOURCE_TEXT_NAMES = {(116, lang): f'SHIRK_Engineering_of_Illusion-{lang}.txt' for lang in ('ar','en')}
registration.SOURCE_TEXT_NAMES.update({(117, lang): f'116-THE_BOOK_AS_WITNESS-{lang}.txt' for lang in ('ar','en')})
registration.COVER_NAMES = {(number, lang): f'{bid}-cover-{lang}.png'
                            for number, bid in [(116, 'SHIRK_Engineering_of_Illusion_simplified'), (117, 'THE_BOOK_AS_WITNESS')]
                            for lang in ('ar','en')}
registration.EDITION_NOTES = {116: {
    'ar': 'النسخة العربية طبعة ميسّرة. الملف الإنجليزي المرفق تكييف للدراسة الأصلية، وليس ترجمة مطابقة لهذه الطبعة الميسّرة.',
    'en': 'Edition warning: this supplied English file adapts the original research study (book 115). It is a companion resource, not a matching translation of the simplified Arabic edition (book 116).'
}}
registration.SPECS = [
    (116, 'SHIRK_Engineering_of_Illusion_simplified',
     'الشِّرْك: كيف أحفظ قلبي لله؟ — الطبعة الميسّرة',
     'SHIRK — Companion English Adaptation of the Original Study',
     'من هندسة الوهم إلى التحرر والتزكية: دليل عملي لفهم الشرك وحفظ القلب، مبني على دراسة الشرك الأصلية. المورد الإنجليزي تكييف للدراسة الأصلية وليس ترجمة مطابقة للطبعة الميسّرة.',
     'Companion adaptation of the original study on shirk, illusion, and human awareness. The Arabic text in this entry is a separate simplified practical edition; this English resource is not its matching translation.',
     ['الشرك', 'التزكية', 'القلب', 'التوبة', 'الطبعة الميسّرة'],
     ['Shirk', 'Awareness', 'Illusion', 'Companion adaptation'],
     ['1GW-LsVuqJ-Ts7UFFC8zloNdXPsMgxXbn', '10dcNJcZHrlkICUgOmRF4Sfxk_dwclj6-',
      '1MSMaZ2mRvc1nLdd4f_pzMcTMJL3ASsYv', '1v1pIByP-83l7vTud-y5EqRBTodOSv2yn']),
    (117, 'THE_BOOK_AS_WITNESS',
     'الكِتَابُ الشَّاهِد',
     'The Book as Witness',
     'مقاربة نسقية لحضور الوحي في شبكة المساءلة والإثبات يوم الحساب. لفظ الشاهد في العنوان اصطلاح تحليلي وظيفي، لا دعوى بأن الكتاب المنزل هو سجل الأعمال الأخروي.',
     'A systemic study of revelation, accountability, and evidence in Qur’anic discourse. Witness is an analytical term in the title, not a claim that revealed scripture is identical to the record of deeds.',
     ['الكتاب', 'الشهادة', 'الوحي', 'المساءلة', 'الإثبات', 'QCROS'],
     ['Book', 'Witness', 'Revelation', 'Accountability', 'Evidence', 'QCROS'],
     ['169W3KTM-0qbpz_c__fOhRZ5PJNXyY72x', '1pvauQqwtIcmxP__OfIFrWM4R5ekF9T1F',
      '1xmizNdq6jIe86L8mjy4OmxT79aqkdd0G', '1wQ1uZgoSJCEu56610DbxeBicJQHpjbtC']),
]

if __name__ == '__main__':
    registration.main()
