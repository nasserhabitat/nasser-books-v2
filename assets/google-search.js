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
    let activeSearchToken = 0;

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

    function highlightSnippet(text, query) {
        if (typeof window !== 'undefined' && typeof window.highlightText === 'function') {
            return window.highlightText(text, query);
        }
        return escapeHtml(text);
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

    function setHasResultsClass(hasResults) {
        const section = document.getElementById('google-search');
        if (!section || !section.classList) return;
        if (hasResults) section.classList.add('has-supplement-results');
        else section.classList.remove('has-supplement-results');
    }

    // Filter out any external non-library results (e.g. random facebook.com posts) from Google CSE
    function sanitizeGoogleResults(widget) {
        if (!widget || typeof widget.querySelectorAll !== 'function') return;
        let validLibraryResults = 0;
        const resultNodes = widget.querySelectorAll('.gsc-webResult.gsc-result');
        resultNodes.forEach(node => {
            if (node.querySelector && node.querySelector('.gs-no-results-result')) {
                node.style.display = 'none';
                return;
            }
            const link = node.querySelector ? node.querySelector('a.gs-title[href], a[href]') : null;
            const href = link ? (link.getAttribute('data-ctorig') || link.getAttribute('href') || '') : '';
            const text = node.textContent || '';
            const isLibrarySite = href.includes('nasserhabitat.github.io') || text.includes('nasserhabitat.github.io');
            if (!isLibrarySite) {
                node.style.display = 'none';
            } else {
                node.style.display = '';
                validLibraryResults++;
            }
        });
        const resultsBox = widget.querySelector ? widget.querySelector('.gsc-resultsbox-visible') : null;
        if (resultsBox) {
            resultsBox.style.display = validLibraryResults > 0 ? '' : 'none';
        }
    }

    function renderSupplement(rawQuery) {
        const supplement = document.getElementById('google-search-supplement');
        const widget = document.getElementById('google-search-widget');
        if (widget) sanitizeGoogleResults(widget);
        if (!supplement) return;
        const query = String(rawQuery || '').trim();
        if (!query) {
            supplement.innerHTML = '';
            lastSupplementQuery = '';
            setHasResultsClass(false);
            return;
        }
        lastSupplementQuery = query;
        const token = ++activeSearchToken;
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
            const author = normalizeText((book.metadata && book.metadata.author) || 'ناصر ابن داوود Nasser Ibn Dawood');
            const bookNum = String(book.book_number || '');
            const bookId = normalizeText(book.id || '');
            const hay = `${titleAr} ${titleEn} ${descAr} ${descEn} ${topicsAr} ${topicsEn} ${author} ${bookNum} ${bookId}`;

            const fullPhrase = hay.includes(q);
            const matchedTerms = terms.filter(t => hay.includes(t)).length;
            if (fullPhrase || matchedTerms === terms.length || (terms.length > 1 && matchedTerms >= Math.ceil(terms.length * 0.6))) {
                let score = 0;
                if (titleAr.includes(q) || titleEn.includes(q)) score += 10;
                if (topicsAr.includes(q) || topicsEn.includes(q)) score += 6;
                if (descAr.includes(q) || descEn.includes(q)) score += 4;
                if (author.includes(q)) score += 2;
                score += matchedTerms * 2;
                matches.push({ book, score, excerpts: [] });
            }
        }

        matches.sort((a, b) => b.score - a.score || b.book.book_number - a.book.book_number);
        setHasResultsClass(matches.length > 0);

        function buildCardHtml(item) {
            const { book, excerpts } = item;
            const excerptHtml = (excerpts && excerpts.length)
                ? `<div style="margin-top:8px;padding:8px 10px;background:#f1f5f9;border-radius:6px;font-size:0.92rem;">
                    ${excerpts.map(ex => `<div style="margin-bottom:4px;"><span style="color:#64748b;font-size:0.82rem;">[${escapeHtml(ex.language)} — سطر ${ex.lineNumber}]</span> ${highlightSnippet(ex.text, query)}</div>`).join('')}
                   </div>`
                : '';
            return `
                <div class="book-card" style="margin-top:12px;border-right:4px solid #1a5276;">
                    <h4 class="book-title" style="margin-bottom:4px;">
                        <a href="books/${escapeHtml(book.id)}/ar/" style="color:#1a5276;text-decoration:none;">
                            ${book.book_number}. ${highlightSnippet(book.titles.ar, query)}
                        </a>
                        <span style="font-weight:normal;color:#475569;font-size:0.92rem;"> — ${highlightSnippet(book.titles.en, query)}</span>
                    </h4>
                    <div style="font-size:0.88rem;color:#0f5132;margin-bottom:6px;direction:ltr;text-align:right;">
                        https://nasserhabitat.github.io/nasser-books-v2/books/${escapeHtml(book.id)}/ar/
                    </div>
                    <p class="book-description" style="margin-bottom:6px;">${highlightSnippet(book.description.ar, query)}</p>
                    <p class="book-description" style="margin-bottom:8px;color:#555;font-size:0.9rem;" dir="ltr">${highlightSnippet(book.description.en, query)}</p>
                    ${excerptHtml}
                    <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:8px;">
                        <a href="books/${escapeHtml(book.id)}/ar/" class="book-link">📚 النسخة العربية</a>
                        <a href="books/${escapeHtml(book.id)}/en/" class="book-link" style="background:#e74c3c;">📘 English Edition</a>
                    </div>
                </div>
            `;
        }

        function updateContainer(isSearchingFullText) {
            const cardsHtml = matches.slice(0, 40).map(buildCardHtml).join('');
            supplement.innerHTML = `
                <div style="margin-top:1rem;padding:1.25rem;background:#f8fafc;border:1px solid #cbd5e1;border-radius:12px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:0.75rem;">
                        <h3 style="color:#1a5276;margin:0;font-size:1.15rem;">
                            🔎 نتائج محرك المكتبة الشامل لـ «${escapeHtml(query)}» (${matches.length} كتابًا مطابقًا)
                            ${isSearchingFullText ? '<span style="font-size:0.85rem;color:#2980b9;font-weight:normal;"> — جارٍ فحص النصوص الكاملة…</span>' : ''}
                        </h3>
                        <button type="button" id="google-to-local-fulltext" class="search-btn" style="padding:8px 16px;font-size:0.9rem;">
                            📖 عرض جميع المقتطفات التفصيلية (278 إصدارًا)
                        </button>
                    </div>
                    ${matches.length
                        ? cardsHtml
                        : `<p style="color:#475569;">${isSearchingFullText ? 'جارٍ البحث في النصوص الكاملة للكتب الـ 139…' : 'لم يتم العثور على تطابق لهذا المصطلح في النصوص.'}</p>`}
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

        const canFullText = typeof window !== 'undefined' &&
            typeof window.loadBookContent === 'function' &&
            typeof window.searchInText === 'function';

        updateContainer(canFullText);

        if (canFullText) {
            (async () => {
                const byId = new Map(matches.map(m => [m.book.id, m]));
                const queue = [
                    ...matches.slice(0, 12).map(m => m.book),
                    ...(matches.length < 10 ? books.filter(b => !byId.has(b.id)) : [])
                ];
                let changed = false;
                for (const book of queue) {
                    if (token !== activeSearchToken) return;
                    if (!book.links || !book.links.ar || !book.links.en) continue;
                    const foundExcerpts = [];
                    const arText = await window.loadBookContent(book.id + '_ar', book.links.ar.text);
                    if (token !== activeSearchToken) return;
                    if (arText) {
                        const arHits = window.searchInText(arText, query, 2);
                        for (const h of arHits) foundExcerpts.push({ ...h, language: 'العربية' });
                    }
                    if (!foundExcerpts.length) {
                        const enText = await window.loadBookContent(book.id + '_en', book.links.en.text);
                        if (token !== activeSearchToken) return;
                        if (enText) {
                            const enHits = window.searchInText(enText, query, 2);
                            for (const h of enHits) foundExcerpts.push({ ...h, language: 'English' });
                        }
                    }
                    if (foundExcerpts.length) {
                        let entry = byId.get(book.id);
                        if (!entry) {
                            entry = { book, score: foundExcerpts.length * 4, excerpts: foundExcerpts };
                            matches.push(entry);
                            byId.set(book.id, entry);
                        } else {
                            entry.excerpts = foundExcerpts;
                        }
                        changed = true;
                        setHasResultsClass(true);
                        updateContainer(true);
                    }
                }
                if (token === activeSearchToken) {
                    setHasResultsClass(matches.length > 0);
                    if (changed || canFullText) updateContainer(false);
                }
            })();
        }
    }

    function bindWidgetInputMonitor(widget) {
        if (!widget || typeof widget.addEventListener !== 'function') return;
        const readCurrentInput = () => {
            if (typeof widget.querySelector !== 'function') return '';
            const input = widget.querySelector('input.gsc-input');
            return (input && typeof input.value === 'string') ? input.value.trim() : '';
        };
        const triggerFromWidget = () => {
            sanitizeGoogleResults(widget);
            const val = readCurrentInput() || getQueryFromHash();
            if (val && val !== lastSupplementQuery) {
                renderSupplement(val);
            }
        };
        widget.addEventListener('keydown', e => {
            if (e && e.key === 'Enter') setTimeout(triggerFromWidget, 10);
        }, true);
        widget.addEventListener('keyup', e => {
            if (!e || e.key === 'Enter') triggerFromWidget();
        }, true);
        widget.addEventListener('click', () => {
            setTimeout(triggerFromWidget, 30);
        }, true);
        widget.addEventListener('submit', () => {
            setTimeout(triggerFromWidget, 10);
        }, true);
        if (typeof MutationObserver === 'function') {
            try {
                const observer = new MutationObserver(() => {
                    triggerFromWidget();
                });
                observer.observe(widget, { childList: true, subtree: true });
            } catch (_) {}
        }
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
                        sanitizeGoogleResults(widget);
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
                        gname: 'nasser-library-google-search',
                        attributes: {
                            as_sitesearch: 'nasserhabitat.github.io/nasser-books-v2'
                        }
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
