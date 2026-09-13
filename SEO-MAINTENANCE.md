# صيانة الفهرسة — nasser-books-v2

تغطي هذه الدفعة 138 صفحة كتاب و7 صفحات رئيسية. أضيفت روابط canonical ذاتية وروابط ar/en متبادلة لصفحات الكتب. حُفظت نصوص الصفحات وروابط القراءة دون تغيير. لم يُعدّل أي عنوان فكري أو وصف موجود في البيانات المنظمة؛ أُكملت الحقول الناقصة فقط من ai-index.json.

خرائط الموقع:

- sitemap.xml: الصفحات الرئيسية وصفحات الكتب، 145 عنوانًا.
- sitemap-books.xml: صفحات الكتب، 138 عنوانًا.
- sitemap-bing.xml: نفس تغطية الخريطة الرئيسية، مع إبقاء اسم الملف القديم متاحًا.

لم تُخترع تواريخ تعديل أو أرقام ISBN أو روابط Google Books. سلامة JSON-LD لا تضمن قبول Google أو عرض نتائج غنية.

## يحتاج قرار المؤلف

124 صفحة كتاب تحمل ترخيصًا مخالفًا لـ CC BY-SA 4.0 الوارد في الفهرس. خمس صفحات لها بيانات Book دون ترخيص، وسبع صفحات أُضيفت لها بيانات Book أساسية دون افتراض ترخيص. بقيت التراخيص الحالية دون تغيير. شغّل أداة المراجعة للحصول على أسماء الملفات:

```shell
node scripts/maintain-seo.cjs
```

## Search Console وrobots.txt

بعد النشر، أضف خاصية URL-prefix بعنوان https://nasserhabitat.github.io/nasser-books-v2/ وأثبت ملكيتها، ثم قدّم https://nasserhabitat.github.io/nasser-books-v2/sitemap.xml.

Google يقرأ robots.txt من جذر النطاق https://nasserhabitat.github.io/robots.txt وليس من مجلد المشروع. صُححت نسخة المشروع، لكن تعديل ملف جذر النطاق يحتاج عملًا منفصلًا في المستودع الذي يخدم ذلك الجذر. لم تُعدّل ملكية Search Console أو إعداداتها ولم تُقدّم الخريطة تلقائيًا.

المراجع:

- https://developers.google.com/search/docs/crawling-indexing/robots/intro
- https://developers.google.com/search/docs/specialty/international/localized-versions

## الاختبار

```shell
node tests/seo.cjs
node tests/search-normalization.cjs
node tests/search-results.cjs
```

اختبار SEO يقارن محتوى الصفحات بعد head بالالتزام الحالي، لذلك يُستخدم قبل حفظ تغييرات الدفعة. أداة الصيانة تعمل للقراءة افتراضيًا، و--write يطبق تحديثاتها؛ لا تستخدم --baseline مع تعديلات HTML غير محفوظة لأنه يستند إلى النسخة المحفوظة في Git.
