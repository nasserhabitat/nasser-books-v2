import json
import requests
import re
from pathlib import Path
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# اسم ملفك الذي أرفقته
file_path = Path(__file__).resolve().parent / 'ai-index.json'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read()
except FileNotFoundError:
    print(f"❌ لم يتم العثور على الملف: {file_path}. تأكد من أنه في نفس المجلد مع السكربت.")
    raise SystemExit(1)

drive_links = list(set(re.findall(r'https://drive\.google\.com/uc\?export=download&id=[\w-]+', data)))

print(f"🔍 تم العثور على {len(drive_links)} رابط Google Drive مميز. جاري الفحص بوقت انتظار أطول (60 ثانية)...\n")

broken_links = []
working_links = 0

# دالة فحص الرابط (تستخدم HEAD لسرعة الفحص دون تحميل الملف)
def check_url(url):
    try:
        # زيادة وقت الانتظار إلى 60 ثانية لتجنب رسالة (Read timed out) مع الملفات الضخمة
        response = requests.head(url, allow_redirects=True, timeout=60)

        with response:
            status = response.status_code
            content_type = response.headers.get('Content-Type', '').lower()
            disposition = response.headers.get('Content-Disposition', '').lower()
            if urlparse(response.url).hostname == 'accounts.google.com':
                return (False, url, f'{status}: تحويل إلى تسجيل الدخول؛ راجع المشاركة')
            if status == 200:
                if 'text/html' in content_type:
                    return (False, url, '200: صفحة HTML؛ لا تثبت إتاحة تنزيل الكتاب')
                if 'attachment' in disposition or any(kind in content_type for kind in ('application/pdf', 'officedocument', 'application/msword', 'application/octet-stream')):
                    return (True, url, '200: استجابة ملف؛ لم يُفحص المحتوى')
                return (False, url, '200: نوع الاستجابة غير محسوم؛ يحتاج مراجعة')
            if status == 404:
                return (False, url, '404: الملف غير موجود أو غير متاح لهذا الطلب؛ راجع المعرّف والمشاركة')
            if status in (408, 429) or status >= 500:
                return (False, url, f'{status}: تعذّر مؤقت؛ أعد المحاولة لاحقًا')
            return (False, url, f'{status}: يحتاج مراجعة؛ قد لا يدعم الخادم HEAD')
    except requests.Timeout:
        return (False, url, 'Timeout: انتهت مهلة الاتصال/القراءة (60 ثانية)؛ النتيجة غير محسومة')
    except requests.RequestException as e:
        return (False, url, f'خطأ اتصال ({type(e).__name__})؛ النتيجة غير محسومة')

# استخدام ThreadPool لتسريع الفحص مع عدد عمال معتدل لتجنب الحظر المؤقت
with ThreadPoolExecutor(max_workers=5) as executor:
    results = [executor.submit(check_url, url) for url in drive_links]
    for completed in as_completed(results):
        is_working, url, status = completed.result()
        if is_working:
            working_links += 1
            print(f"✅ استجابة ملف ({status}): {url.split('id=')[-1][:10]}...", flush=True)
        else:
            broken_links.append((url, status))
            print(f"⚠️ يحتاج مراجعة ({status}): {url}", flush=True)

print("\n📊 --- ملخص الفحص ---")
print(f"✅ استجابات الملفات: {working_links} من أصل {len(drive_links)}")
print('فحص HTTP لا يثبت وحده تطابق الملف مع الكتاب أو صلاحيات مشاركته.')
if not broken_links:
    print('استجابت جميع الروابط؛ لم يُفحص محتوى الملفات.')
else:
    print(f"⚠️ يوجد {len(broken_links)} رابط يحتاج مراجعة أو إعادة فحص.")
# تحديث التقرير في كل تشغيل يمنع بقاء أخطاء قديمة بعد فحص جديد.
report_path = file_path.with_name('broken_links_report.txt')
with report_path.open('w', encoding='utf-8') as f:
    for url, status in broken_links:
        f.write(f"Status: {status} - URL: {url}\n")
    if not broken_links:
        f.write('لا نتائج تحتاج مراجعة في هذا الفحص؛ لم يُفحص محتوى الملفات.\n')
print(f'📝 تم تحديث التقرير: {report_path}')
