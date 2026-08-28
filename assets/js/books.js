// تصحيح روابط الكتب الخارجية
function fixBookPaths() {
    document.querySelectorAll('.book-actions a, .ai-access-links a').forEach(link => {
        let correctedPath = link.getAttribute('href');
        
        // إزالة المسافات وتحويل إلى حروف صغيرة إذا لزم الأمر
        correctedPath = correctedPath.replace(/\s+/g, '-').toLowerCase();
        
        // التأكد من أن الرابط يبدأ بـ http أو https
        if (!correctedPath.startsWith('http://') && !correctedPath.startsWith('https://')) {
            correctedPath = 'https://' + correctedPath;
        }
        
        // تحديث الرابط إذا كان مختلفاً
        if (link.getAttribute('href') !== correctedPath) {
            link.setAttribute('href', correctedPath);
        }
    });
}

// تهيئة الصفحة عند التحميل
document.addEventListener('DOMContentLoaded', function() {
    fixBookPaths();
});
