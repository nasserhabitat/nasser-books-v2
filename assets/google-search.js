/* Optional Google Programmable Search. Never loads during local-only search.
 * Official element API: https://developers.google.com/custom-search/docs/element
 */
(() => {
    'use strict';
    const engineId = '87a2ea74c56054f92';
    let loading = false;
    let rendered = false;
    let timer;
    let lastSupplementQuery = '';

    function normalizeText(text) {
        if (typeof window !== 'undefined' && typeof window.normalizeSearchText === 'function') {
            return window.normalizeSearchText(text);
        }
        return String(text || '').normalize('NFC').toLowerCase()
            .replace(/[أإآٱ]/g, 'ا')
            .replace(/[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E4\u06E7-\u06E8\u06EA-\u06ED\u0640]/g, '');
    }

    function escapeHtml(text) {
        if (typeof window !== 'undefined' && typeof window.escapeSearchHtml === 'function') {
            return window.escapeSearchHtml(text);
        }
        return String(text || '').replace(/[&<>"']/g, c => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        }[c]));
    }

    function getQueryFromHash() {
        const hash = (window.location && window.location.hash ? window.location.hash : '').slice(1);
        for (const part of hash.split('&')) {
            if (part.startsWith('gsc.q=')) {
                try {
                    return decodeURIComponent(part.slice(6).replace(/\+/g, ' ')).trim();
                } catch (_) {
                    return part.slice(6).trim();
                }
            }
        }
        return '';
    }

    function renderSupplement(rawQuery) {
        const supplement = document.getElementById('google-search-supplement');
        if (!supplement) return;
        const query = String(rawQuery || '').trim();
        if (!query) {
            supplement.innerHTML = '';
            lastSupplementQuery = '';
            return;
        }
        lastSupplementQuery = query;
        const books = (typeof window !== 'undefined' && Array.isArray(window.booksData)) ? window.booksData : [];
        if (!books.length) return;

        const q = normalizeText(query);
        const terms = q.split(/\s+/).filter(Boolean);
        if (!terms.length) return;

        const matches = [];
        for (const book of books) {
            const titleAr = normalizeText(book.titles && book.titles.ar);
            const titleEn = normalizeText(book.titles && book.titles.en);
            const descAr = normalizeText(book.description && book.description.ar);
            const descEn = normalizeText(book.description && book.description.en);
            const topicsAr = ((book.metadata && book.metadata.topics_ar) || []).map(normalizeText).join(' ');
            const topicsEn = ((book.metadata && book.metadata.topics_en) || []).map(normalizeText).join(' ');
            const hay = `${titleAr} ${titleEn} ${descAr} ${descEn} ${topicsAr} ${topicsEn}`;

            const fullPhrase = hay.includes(q);
            const matchedTerms = terms.filter(t => hay.includes(t)).length;
            if (fullPhrase || matchedTerms === terms.length || (terms.length > 1 && matchedTerms >= Math.ceil(terms.length * 0.6))) {
                let score = 0;
                if (titleAr.includes(q) || titleEn.includes(q)) score += 10;
                if (topicsAr.includes(q) || topicsEn.includes(q)) score += 6;
                if (descAr.includes(q) || descEn.includes(q)) score += 4;
                score += matchedTerms * 2;
                matches.push({ book, score });
            }
        }

        matches.sort((a, b) => b.score - a.score || b.book.book_number - a.book.book_number);

        const cardsHtml = matches.slice(0, 25).map(({ book }) => `
            <div class="book-card" style="margin-top:12px;border-right:4px solid #1a5276;">
                <h4 class="book-title" style="margin-bottom:6px;">
                    <a href="books/${escapeHtml(book.id)}/ar/" style="color:#1a5276;text-decoration:none;">
                        ${book.book_number}. ${escapeHtml(book.titles.ar)}
                    </a>
                </h4>
                <div style="font-size:0.9rem;color:#0f5132;margin-bottom:6px;direction:ltr;text-align:right;">
                    https://nasserhabitat.github.io/nasser-books-v2/books/${escapeHtml(book.id)}/ar/
                </div>
                <p class="book-description" style="margin-bottom:8px;">${escapeHtml(book.description.ar)}</p>
                <p class="book-description" style="margin-bottom:10px;color:#555;font-size:0.92rem;" dir="ltr">${escapeHtml(book.description.en)}</p>
                <div style="display:flex;gap:10px;flex-wrap:wrap;">
                    <a href="books/${escapeHtml(book.id)}/ar/" class="book-link">📚 النسخة العربية</a>
                    <a href="books/${escapeHtml(book.id)}/en/" class="book-link" style="background:#e74c3c;">📘 English Edition</a>
                </div>
            </div>
        `).join('');

        supplement.innerHTML = `
            <div style="margin-top:1.25rem;padding:1.25rem;background:#f8fafc;border:1px solid #cbd5e1;border-radius:12px;">
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:0.75rem;">
                    <h3 style="color:#1a5276;margin:0;font-size:1.15rem;">
                        🔎 نتائج فهرس المكتبة المباشر لـ «${escapeHtml(query)}» (${matches.length} كتابًا مطابقًا)
                    </h3>
                    <button type="button" id="google-to-local-fulltext" class="search-btn" style="padding:8px 16px;font-size:0.9rem;">
                        📖 البحث في النصوص الكاملة للكتب (278 إصدارًا)
                    </button>
                </div>
                ${matches.length
                    ? cardsHtml
                    : `<p style="color:#475569;">لم يظهر تطابق مباشر في عناوين الكتب؛ اضغط «البحث في النصوص الكاملة للكتب» أعلاه للبحث داخل فصول ومحتويات جميع الكتب.</p>`}
            </div>
        `;

        const fulltextBtn = document.getElementById('google-to-local-fulltext');
        if (fulltextBtn && typeof fulltextBtn.addEventListener === 'function') {
            fulltextBtn.addEventListener('click', () => {
                const localInput = document.getElementById('localSearch');
                const fastCheckbox = document.getElementById('fastSearch');
                const localTab = document.querySelector('.search-tab[data-tab="local-search"]');
                if (localInput) localInput.value = query;
                if (fastCheckbox) fastCheckbox.checked = false;
                if (localTab && typeof localTab.click === 'function') localTab.click();
                if (typeof window.performLocalSearch === 'function') window.performLocalSearch();
            });
        }
    }

    function bindWidgetInputMonitor(widget) {
        if (!widget || typeof widget.addEventListener !== 'function') return;
        const checkInput = () => {
            if (typeof widget.querySelector !== 'function') return;
            const input = widget.querySelector('input.gsc-input');
            if (input && typeof input.value === 'string' && input.value.trim() && input.value.trim() !== lastSupplementQuery) {
                renderSupplement(input.value.trim());
            }
        };
        widget.addEventListener('keyup', e => {
            if (!e || e.key === 'Enter') checkInput();
        });
        widget.addEventListener('click', () => {
            setTimeout(checkInput, 50);
        });
    }

    function loadGoogleSearch() {
        if (loading || rendered) return;
        const status = document.getElementById('google-search-status');
        const retry = document.getElementById('google-search-retry');
        const widget = document.getElementById('google-search-widget');
        if (!status || !retry || !widget) return;
        loading = true;
        retry.hidden = true;
        status.textContent = 'جارٍ تحميل بحث Google…';
        bindWidgetInputMonitor(widget);

        const initialQuery = getQueryFromHash();
        if (initialQuery) renderSupplement(initialQuery);

        function failure() {
            if (rendered) return;
            clearTimeout(timer);
            loading = false;
            status.textContent = 'تعذّر تحميل بحث Google. أعد المحاولة أو افتح المحرك في نافذة مستقلة. البحث المحلي متاح كالمعتاد.';
            retry.hidden = false;
        }

        window.__gcse = {
            parsetags: 'explicit',
            searchCallbacks: {
                web: {
                    starting(_gname, query) {
                        renderSupplement(query);
                    },
                    ready(_gname, query) {
                        renderSupplement(query);
                    }
                }
            },
            initializationCallback() {
                if (rendered) return;
                try {
                    window.google.search.cse.element.render({
                        div: 'google-search-widget',
                        tag: 'search',
                        gname: 'nasser-library-google-search'
                    });
                    rendered = true;
                    loading = false;
                    clearTimeout(timer);
                    retry.hidden = true;
                    status.textContent = 'بحث Google جاهز. هذه النتائج مستقلة عن البحث المحلي.';
                    const hashQuery = getQueryFromHash();
                    if (hashQuery) renderSupplement(hashQuery);
                } catch (_) {
                    failure();
                }
            }
        };

        const previous = document.getElementById('google-search-loader');
        if (previous) previous.remove();
        const script = document.createElement('script');
        script.id = 'google-search-loader';
        script.async = true;
        script.src = `https://cse.google.com/cse.js?cx=${engineId}`;
        script.onerror = failure;
        timer = setTimeout(failure, 20000);
        document.head.appendChild(script);
    }

    function activateGoogleTabFromHash() {
        // Match Google parameters, not arbitrary anchors containing "gsc".
        const hash = window.location.hash.slice(1);
        if (!/(?:^|&)gsc\.[^=&]+(?:=|&|$)/.test(hash)) return;
        const tab = document.querySelector('.search-tab[data-tab="google-search"]');
        if (!tab) return;
        // Activate explicitly: tab click handlers may not be registered yet.
        document.querySelectorAll('.search-tab, .tab-content').forEach(node => {
            node.classList.remove('active');
        });
        tab.classList.add('active');
        const section = document.getElementById('google-search');
        if (section) section.classList.add('active');
        loadGoogleSearch();
        const hashQuery = getQueryFromHash();
        if (hashQuery) renderSupplement(hashQuery);
    }

    function init() {
        const tab = document.querySelector('.search-tab[data-tab="google-search"]');
        const retry = document.getElementById('google-search-retry');
        if (tab) tab.addEventListener('click', loadGoogleSearch);
        if (retry) retry.addEventListener('click', loadGoogleSearch);
        window.addEventListener('hashchange', activateGoogleTabFromHash);
        activateGoogleTabFromHash();
        if (tab && tab.classList.contains('active')) loadGoogleSearch();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
