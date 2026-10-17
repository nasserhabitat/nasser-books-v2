"""Register the six author-supplied books without editing manuscripts or sharing.

TXT inputs are the original Drive downloads listed in books-120-125-sources.json.
Covers come from the author's local google_books directory. Word and PDF remain
external. Publication candidates retain their declared status in both languages.
Run with --texts-root pointing to number/language folders of verified TXT files.
"""
import argparse
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path


DETAILS = {
    120: (
        'وظيفة الرسول في اللسان القرآني — قراءة بنيوية في شبكة البعث والإرسال والبلاغ والبيان',
        'The Function of the Messenger in the Qur’anic Tongue — A Structural Analysis of Commission, Dispatch, Proclamation, and Clarification',
        'دراسة لشبكة وظائف الرسول والتمييز بين البعث والإرسال والبلاغ والبيان، تقترح إطارًا لفحص الأخبار ونطاق الإلزام، مع فصل الشاهد القرآني عن استنباط الباحث ونموذجه التشغيلي. الإنجليزية تكييف مفاهيمي مختصر.',
        'A study of the Messenger’s functions and the relations among commissioning, sending, proclamation, and clarification. It proposes a framework for examining reports and their scope of authority while distinguishing Qur’anic evidence from authorial inference. Condensed conceptual English adaptation.',
        ['وظيفة الرسول', 'البعث', 'الإرسال', 'البلاغ', 'البيان', 'النبي والرسول', 'المرويات', 'QCROS'],
        ['Messenger', 'Commission', 'Dispatch', 'Proclamation', 'Clarification', 'Narrated reports', 'QCROS']),
    121: (
        'هل يُباع العلم أم يُباع الحق؟ — هندسة الشراء والثمن والكتمان في اللسان القرآني',
        'Is Knowledge Sold, or Is Truth Sold? — The Qur’anic Language of Exchange, Price, Concealment, and Disclosure',
        'بحث في الشراء والثمن والكتمان وأجر البلاغ وأخلاق التأليف والنشر، يميز الوحي المنزل من الاجتهاد البشري ويختبر التعميمات بالموارد المقابلة. يعرض نماذج عقود وإتاحة بوصفها اجتهادات تشغيلية لا أحكامًا قرآنية منصوصة. الإنجليزية مختصرة.',
        'An inquiry into exchange, price, concealment, the reward of proclamation, and publishing ethics. It distinguishes revelation from human scholarship and tests generalizations against counter-evidence. Contract and access models remain operational proposals, not explicit Qur’anic legislation. Condensed English adaptation.',
        ['العلم', 'الحق', 'الشراء', 'الثمن', 'الكتمان', 'أجر البلاغ', 'حقوق المؤلف', 'النشر', 'QCROS'],
        ['Knowledge', 'Truth', 'Exchange', 'Price', 'Concealment', 'Authorship', 'Publishing ethics', 'QCROS']),
    122: (
        'القرآن والبيان النبوي والمرويات — مساءلة المرجعية واختبار اللسان',
        "The Qur'an, the Prophetic Elucidation, and the Narrated Reports",
        'يعرض المؤلف قراءته لعلاقة القرآن بالبيان النبوي والمرويات، ومسائل المرجعية والتشريع والتدوين واختبار الدلالة. ما يقدمه من تأويلات وأحكام تاريخية يُقرأ بوصفه أطروحة المؤلف، لا نصًا قرآنيًا. الإنجليزية ترجمة مفاهيمية مختصرة.',
        'The author’s inquiry into the relation between the Qur’an, prophetic elucidation, and narrated reports, addressing authority, legislation, transmission, and linguistic interpretation. Interpretive and historical conclusions belong to the author’s thesis, not to Qur’anic wording. Condensed conceptual translation.',
        ['القرآن', 'البيان النبوي', 'المرويات', 'المرجعية', 'التشريع', 'التدوين', 'اللسان القرآني'],
        ['Qur’an', 'Prophetic elucidation', 'Narrated reports', 'Authority', 'Legislation', 'Transmission', 'Qur’anic language']),
    123: (
        'الذِّكْر في اللسان القرآني — هندسة الحضور والوعي والرجوع إلى الله',
        'Dhikr in the Qur’anic Language — The Architecture of Presence, Awareness, and Returning to God',
        'نسخة بحثية خاضعة للمراجعة العلمية النهائية قبل الإتاحة العامة وفق تنبيه المصدر. تستقرئ استعمالات الذكر والوحي والتذكير والصلاة وآثار التذكر، مع إبقاء الفرضيات البنيوية والحالات المفتوحة معلنة. الإنجليزية تكييف مفاهيمي مختصر مرشح للمراجعة.',
        'Research candidate: the source states that final scholarly review precedes public release. A contextual study of dhikr, revelation, reminding, prayer, and the effects of remembrance, preserving open questions and the provisional status of structural hypotheses. Condensed conceptual English adaptation.',
        ['الذكر', 'التذكر', 'الوحي', 'الحضور', 'الوعي', 'الصلاة', 'المثاني', 'QCROS', 'نسخة بحثية'],
        ['Dhikr', 'Remembrance', 'Revelation', 'Presence', 'Awareness', 'Prayer', 'Mathani', 'QCROS', 'Research candidate']),
    124: (
        'الاستغفار في اللسان القرآني — دراسة في الطلب والمغفرة والتوبة وإصلاح النفس والعمران',
        'Istighfār in the Qur’anic Language — A Study of Seeking Forgiveness, Divine Forgiveness, Repentance, and the Renewal of Self and Society',
        'نسخة أكاديمية مرشحة للنشر، غير معتمدة طبعةً محققة نهائية. تبحث علاقات الاستغفار والمغفرة والتوبة والإصلاح وحقوق الآخرين، مع الفصل بين طلب المغفرة وحصولها وبين الدليل والنموذج التفسيري. المقابلة المصحفية والتحقيق والمراجعة النهائية ما تزال مفتوحة؛ الإنجليزية مختصرة.',
        'Publication-candidate academic study, not a final verified edition. It examines seeking forgiveness, divine forgiveness, repentance, rectification, and others’ rights, distinguishing petition from outcome and evidence from interpretive models. Qur’anic collation and final scholarly review remain open. Condensed English edition.',
        ['الاستغفار', 'المغفرة', 'التوبة', 'الإصلاح', 'حقوق الآخرين', 'النفس', 'العمران', 'QCROS', 'مرشح للنشر'],
        ['Istighfar', 'Forgiveness', 'Repentance', 'Rectification', 'Human rights', 'Self', 'Society', 'QCROS', 'Publication candidate']),
    125: (
        'المسيح والدجال: من البيان القرآني إلى صناعة الأسطورة',
        'The Messiah and the Dajjal — From Qur’anic Discourse to the Making of Myth',
        'دراسة في اللسان القرآني والمرويات والتاريخ المقارن وتلقي مفهوم المسيح الدجال، تفصل الجرد النصي عن نقد الرواية والفرضية التاريخية والنموذج التفسيري، وتحفظ القضايا المفتوحة دون إسقاطات قسرية على أشخاص أو تقنيات. الإنجليزية تكييف مفاهيمي مختصر.',
        'A study of Qur’anic language, narrated traditions, comparative history, and the reception of the Dajjal concept. It distinguishes corpus observations, report criticism, historical hypotheses, and interpretive models, preserving open issues without forced identifications with people or technologies. Condensed conceptual English edition.',
        ['المسيح', 'الدجال', 'المرويات', 'التاريخ المقارن', 'الفتنة', 'سورة الكهف', 'الأمان المعرفي', 'QCROS'],
        ['Messiah', 'Dajjal', 'Narrated traditions', 'Comparative history', 'Fitna', 'The Cave', 'Epistemic safety', 'QCROS']),
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--texts-root', required=True, type=Path)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('registration', Path(__file__).with_name('register-books-113-115.py'))
    registration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(registration)
    manifest = json.loads(Path(__file__).with_name('books-120-125-sources.json').read_text(encoding='utf-8'))
    local_root = registration.SOURCE
    registration.EXPECTED_COUNT = 119
    registration.DATE = manifest['checked_at']
    registration.SOURCE = args.texts_root.resolve()
    registration.SPECS = []
    for b in manifest['books']:
        n, bid = b['number'], b['id']
        registration.SOURCE_FOLDERS[n] = str(n)
        ids = []
        for lang, edition in b['editions'].items():
            folder = registration.SOURCE / str(n) / lang
            text = folder / edition['text']['name']
            cover = local_root / b['source_folder'] / edition['cover']['source_name']
            assert sha256(text) == edition['text']['sha256'], text
            assert sha256(cover) == edition['cover']['sha256'], cover
            assert all(f['anyone_reader'] for f in edition['files'])
            registration.SOURCE_TEXT_NAMES[(n, lang)] = text.name
            registration.SOURCE_COVER_NAMES[(n, lang)] = edition['cover']['site_name']
            registration.COVER_NAMES[(n, lang)] = edition['cover']['site_name']
            ids.extend(next(f['id'] for f in edition['files'] if f['name'].endswith(ext)) for ext in ('.docx', '.pdf'))
        registration.SPECS.append((n, bid, *DETAILS[n], ids))
        registration.EDITION_NOTES[n] = {
            'ar': 'النسخة الإنجليزية مختصرة ومفاهيمية، وليست ترجمة حرفية كاملة؛ يبقى النص العربي المرجع الأساسي للتفصيل والإحالات.',
            'en': 'This is a condensed conceptual English edition, not a complete word-for-word translation. The Arabic text remains the primary source for detailed analysis and references.'
        }
    registration.EDITION_NOTES[123]['ar'] += ' تنبيه الحالة: يصرح المصدر بأن المراجعة العلمية النهائية قبل الإتاحة العامة ما تزال مطلوبة؛ ليست طبعة محققة نهائية.'
    registration.EDITION_NOTES[123]['en'] += ' Status: research candidate; the source requires final scholarly review before public release, not a final verified edition.'
    registration.EDITION_NOTES[124]['ar'] += ' تنبيه الحالة: نسخة أكاديمية مرشحة للنشر لم تُعتمد نهائيًا؛ المقابلة المصحفية والتحقيق والمراجعة النهائية ما تزال مفتوحة.'
    registration.EDITION_NOTES[124]['en'] += ' Status: publication candidate, not finally approved; Qur’anic collation, verification, and final review remain open.'
    # All original assets are validated before staging any cover or updating the site.
    for b in manifest['books']:
        for lang, edition in b['editions'].items():
            src = local_root / b['source_folder'] / edition['cover']['source_name']
            dest = registration.SOURCE / str(b['number']) / lang / edition['cover']['site_name']
            if dest.exists():
                assert sha256(dest) == edition['cover']['sha256'], dest
            else:
                shutil.copy2(src, dest)
    original_page = registration.page

    def page_with_status(book, lang):
        if book['book_number'] in (123, 124):
            book['metadata']['publication_status'] = 'research_candidate' if book['book_number'] == 123 else 'publication_candidate'
            book['metadata']['final_scholarly_review'] = 'pending_as_stated_in_source'
        return original_page(book, lang)

    registration.page = page_with_status
    registration.main()
    readme = registration.ROOT / 'README.md'
    note = ('نُقلت نصوص Drive الأصلية والأغلفة المحلية دون تحرير المحتوى أو تغيير المشاركة. '
            'الإنجليزية مختصرة ومفاهيمية؛ والكتابان 123 و124 يحتفظان بتنبيه الحالة البحثية/الترشيح للنشر، دون ادعاء الاعتماد النهائي. '
            'لم تُحدّث بيانات الإتاحة التاريخية داخل النصوص الأصلية. سجل المطابقة والبصمات: scripts/books-120-125-sources.json.\n\n')
    readme.write_text(readme.read_text(encoding='utf-8').replace('## التحديث الشهري', note + '## التحديث الشهري', 1), encoding='utf-8')


if __name__ == '__main__':
    main()
