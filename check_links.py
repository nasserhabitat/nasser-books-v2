import json
import requests
import re

# ضع مسار ملف الفهرس الخاص بك هنا
file_path = 'search-index.json'

with open(file_path, 'r', encoding='utf-8') as file:
    data = file.read()

# استخراج جميع روابط جوجل درايف
drive_links = set(re.findall(r'https://drive\.google\.com/uc\?export=download&id=[\w-]+', data))

print(f"🔍 تم العثور على {len(drive_links)} رابط Google Drive. جاري الفحص...\n")

broken_links = []

for link in drive_links:
    try:
        # نرسل طلب HEAD لتجنب تحميل الملفات بالكامل
        response = requests.head(link, allow_redirects=True, timeout=10)
        
        # إذا كان الكود 200 فهذا يعني أن الملف موجود وصلاحياته مفتوحة
        if response.status_code == 200:
            print(f"✅ سليم: {link}")
        else:
            print(f"❌ خطأ ({response.status_code}): {link}")
            broken_links.append(link)
    except Exception as e:
        print(f"⚠️ فشل الاتصال: {link}")
        broken_links.append(link)

print("\n📊 --- ملخص الفحص ---")
if not broken_links:
    print("🎉 جميع روابط جوجل درايف تعمل بشكل مثالي!")
else:
    print(f"⚠️ يوجد {len(broken_links)} روابط تحتاج إلى مراجعة الصلاحيات أو غير موجودة.")