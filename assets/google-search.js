/* Optional Google Programmable Search. Never loads during local-only search.
 * Official element API: https://developers.google.com/custom-search/docs/element
 */
(() => {
    'use strict';
    const engineId = '87a2ea74c56054f92';
    let loading = false;
    let rendered = false;
    let timer;

    function loadGoogleSearch() {
        if (loading || rendered) return;
        const status = document.getElementById('google-search-status');
        const retry = document.getElementById('google-search-retry');
        if (!status || !retry || !document.getElementById('google-search-widget')) return;
        loading = true;
        retry.hidden = true;
        status.textContent = 'جارٍ تحميل بحث Google…';

        function failure() {
            if (rendered) return;
            clearTimeout(timer);
            loading = false;
            status.textContent = 'تعذّر تحميل بحث Google. أعد المحاولة أو افتح المحرك في نافذة مستقلة. البحث المحلي متاح كالمعتاد.';
            retry.hidden = false;
        }

        window.__gcse = {
            parsetags: 'explicit',
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
