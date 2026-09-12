const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'search.html'), 'utf8');
for (const script of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)) new vm.Script(script[1]);
const source = html.slice(html.indexOf('        function normalizeSearchText'), html.indexOf('        async function loadBookContent'));
const context = vm.createContext({});
vm.runInContext(source, context);
const { normalizeSearchText: normalize, searchInText: search, highlightText: highlight } = context;
for (const term of ['الإسلام', 'الاسلام', 'الإِسْلَام', 'الإسلام', 'آلا', 'ٱلا']) {
    assert.equal(normalize(term), term.endsWith('لا') ? 'الا' : 'الاسلام');
}
assert.notEqual(normalize('رحمة'), normalize('رحمه'));
assert.notEqual(normalize('على'), normalize('علي'));
assert.equal(normalize('ENGLISH'), 'english');
assert.equal(search('الإسلام والاسلام', 'الاسلام').length, 1);
assert.equal(search('نص', 'َ').length, 0);
assert.equal(highlight('الإِسْلَام', 'الاسلام'), '<mark class="search-highlight">الإِسْلَام</mark>');
assert.equal(highlight('<script>', 'missing'), '&lt;script&gt;');
let files = 0, matchingLines = 0;
function walk(dir) {
    for (const entry of fs.readdirSync(dir, {withFileTypes:true})) {
        const file = path.join(dir, entry.name);
        if (entry.isDirectory()) walk(file);
        else if (entry.name === 'content.txt') {
            const text = fs.readFileSync(file, 'utf8');
            const first = search(text, 'الإسلام', Infinity);
            const second = search(text, 'الاسلام', Infinity);
            assert.equal(JSON.stringify(first), JSON.stringify(second), file);
            files++;
            matchingLines += first.length;
        }
    }
}
walk(path.join(root, 'books'));
console.log(JSON.stringify({files, matchingLines, result:'PASS'}));
