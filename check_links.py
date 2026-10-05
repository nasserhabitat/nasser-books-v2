import json
import requests
import re
from concurrent.futures import ThreadPoolExecutor

file_path = 'ai-index.json'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read()
except FileNotFoundError:
    print(f"❌ لم يتم العثور على الملف: {file_path}. تأكد من أنه في نفس المجلد مع السكربت.")
    exit()

drive_links = list(set(re.findall(r'https://drive\.google\.com/uc\?export=download&id=[\w-]+', data)))

print(f"🔍 تم العثور على {len(drive_links)} رابط Google Drive. جاري الفحص بوقت انتظار أطول (60 ثانية)...\n")

broken_links = []
working_links = 0

def check_url(url):
    try:
        # زيادة وقت الانتظار إلى 60 ثانية لتجنب رسالة (Read timed out) مع الملفات الضخمة
        response = requests.head(url, allow_redirects=True, timeout=60)
        
        if response.status_code in [200, 302, 303]:
            return (True, url, response.status_code)
        else:
            return (False, url, response.status_code)
    except Exception as e:
        return (False, url, str(e))

# تقليل عدد المسارات المتوازية إلى 5 لتخفيف الضغط على الاتصال وتجنب الحظر المؤقت
with ThreadPoolExecutor(max_workers=5) as executor:
    results = executor.map(check_url, drive_links)

for is_working, url, status in results:
    if is_working:
        working_links += 1
        print(f"✅ سليم ({status}): {url.split('id=')[-1][:10]}...")
    else:
        broken_links.append((url, status))
        print(f"❌ خطأ ({status}): {url}")

print("\n📊 --- ملخص الفحص ---")
print(f"✅ الروابط السليمة: {working_links} من أصل {len(drive_links)}")
if not broken_links:
    print("🎉 جميع روابط جوجل درايف تعمل بشكل مثالي ومفتوحة الصلاحيات!")
else:
    print(f"⚠️ يوجد {len(broken_links)} رابط لم ينجح الفحص. يرجى مراجعتها:")
    with open('broken_links_report.txt', 'w', encoding='utf-8') as f:
        for url, status in broken_links:
            f.write(f"Status: {status} - URL: {url}\n")
    print("📝 تم حفظ قائمة الأخطاء في ملف 'broken_links_report.txt'")
