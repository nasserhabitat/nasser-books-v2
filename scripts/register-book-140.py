# -*- coding: utf-8 -*-
"""Register book 140 (author-supplied DOCX + covers) into the local clone."""
import importlib.util, re, sys
from pathlib import Path

REPO = Path(r"C:\Users\nasse\OneDrive\Documents\GitHub\nasser-books-v2")
SRC = Path(r"C:\Users\nasse\OneDrive\Documents\deepseek-harness\default-workspace\work\book140\src")

spec = importlib.util.spec_from_file_location("registration", REPO / "scripts" / "register-books-113-115.py")
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)

BID = "The_measure_of_stewardship_in_surah_sad"
r.SOURCE = SRC
r.EXPECTED_COUNT = 139
r.DATE = "2026-11-12"
r.COVER_NAMES = {(140, lang): f"{BID}-{lang}-cover.png" for lang in ("ar", "en")}
r.EDITION_NOTES = {140: {
    "ar": "النسخة الإنجليزية تكييف مفاهيمي مختصر؛ يبقى النص العربي المرجع الأساسي. النص القابل للبحث مستخرج من ملف Word؛ راجع الأصل للجداول والصور والتنسيق. PDF غير متاح بعد.",
    "en": "Condensed conceptual adaptation; the Arabic work remains the primary source. Search text extracted from Word; consult the original for tables, images, and formatting. PDF is not yet available.",
}}
r.SPECS = [(
    140, BID,
    "نبأ الخصم وميزان الاستخلاف في سورة «ص» — مفهوم «النعجة» بين أنثى الضأن والأرض الناعجة وحاضنة الأفكار والتأويلات",
    "The Disputants’ Account and the Measure of Stewardship in Surah Sad — The Concept of al-Naʿjah: From the Ewe to Productive Land and the Incubator of Ideas and Interpretations",
    "دراسة بنيوية تدبّرية في نبأ الخصم بسورة «ص» (الآيات ٢١–٢٦): تفصل منطوق النص القرآني والاستعمال المعجمي للفظ «النعجة» وشاهد «الأرض الناعجة» عن سيناريو الأرض وحقوق الارتفاق، وتوازن بين خمس أطروحات تفسيرية، وتضبط طبقات الفهم بمراتب الإثبات، وتفحص دعوى «المئة كلمة» وفق معيار عدّ معلن. النسخة الإنجليزية تكييف مفاهيمي مختصر.",
    "A structural, contemplative study of the disputants’ account in Surah Sad (38:21–26). It distinguishes the Qur’anic wording and the lexical sense of naʿjah (ewe) from the attested expression ard nāʿijah (productive land) and from an agrarian property-and-easement hypothesis, compares five interpretive approaches, and holds that complementary layers of understanding carry unequal evidential weight. Condensed English adaptation.",
    ["سورة ص", "نبأ الخصم", "النعجة", "الأرض الناعجة", "الاستخلاف", "العدل", "حقوق الارتفاق", "فقه اللسان القرآني", "QCROS"],
    ["Surah Sad", "Disputants’ account", "Naʿjah", "Productive land", "Stewardship", "Justice", "Easement", "Qur’anic semantics", "QCROS"],
    ["12SOmgy3pw8SScK0Llwr6SsHTHv_C7yzV", "",
     "1flcS52T5tb1A0w7_B6PLComstIRK9g6A", ""]
)]

r.main()

# The base pages carry the generic reader fallback; state the missing PDF plainly,
# and add the reviewed bilingual keywords to each page's Book JSON-LD.
import json
from html import escape
for lang in ("ar", "en"):
    page = REPO / "books" / BID / lang / "index.html"
    text = page.read_text(encoding="utf-8")
    text = re.sub(r"<noscript>.*?</noscript>",
                  "<noscript>PDF غير متاح بعد. / PDF is not yet available.</noscript>", text)
    topics = r.SPECS[0][6 if lang == "ar" else 7]
    m = re.search(r'(<script type="application/ld\+json">)(.*?)(</script>)', text, re.S)
    data = json.loads(m.group(2))
    data["keywords"] = topics
    text = text[:m.start()] + m.group(1) + json.dumps(data, ensure_ascii=False) + m.group(3) + text[m.end():]
    if 'name="keywords"' not in text:
        text = text.replace("</head>", f'<meta name="keywords" content="{escape(", ".join(topics))}">\n</head>', 1)
    page.write_text(text, encoding="utf-8")
print("registered", BID)
