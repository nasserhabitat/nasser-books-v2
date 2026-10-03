// تصحيح روابط الكتب الخارجية
function fixBookPaths() {
    document.querySelectorAll('.book-actions a, .ai-access-links a').forEach(link => {
        let correctedPath = link.getAttribute('href');

        // Drive IDs and local filenames are case-sensitive. Preserve their spelling
        // and leave relative site URLs relative.
        if (!correctedPath) return;
        correctedPath = correctedPath.trim();

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
