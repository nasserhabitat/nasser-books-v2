const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'search.html'), 'utf8');
const script = [...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)].map(m => m[1]).join('\n');
const elements = {localSearch:{value:'الاسلام'},fastSearch:{checked:false},localResults:{innerHTML:''},searchProgress:{style:{},innerHTML:''}};
let failing = false;
const context = vm.createContext({
    document:{addEventListener(){},getElementById:id=>elements[id]},
    window:{}, console:{warn(){}}, AbortController,
    setTimeout(fn, ms){if(ms === 30) fn(); return 1;}, clearTimeout(){},
    fetch: async url => {
        if (failing) throw Error('simulated offline');
        return {ok:true,text:async()=>fs.readFileSync(path.join(root,url),'utf8')};
    }
});
vm.runInContext(script, context);
(async () => {
    await context.performLocalSearch();
    const first = elements.localResults.innerHTML;
    assert.ok(first.includes('class="match-line"'));
    assert.ok(first.includes('العربية — السطر'));
    elements.localSearch.value = 'الإسلام';
    await context.performLocalSearch();
    assert.equal(elements.localResults.innerHTML.replaceAll('الإسلام','الاسلام'), first.replaceAll('الإسلام','الاسلام'));
    vm.runInContext('bookContentCache.clear()',context);
    failing = true;
    await context.performLocalSearch();
    assert.ok(elements.localResults.innerHTML.includes('تعذّر تحميل 138'));
    failing = false;
    await context.performLocalSearch();
    assert.ok(elements.localResults.innerHTML.includes('class="match-line"'));
    console.log('PASS: full search renders excerpts, spelling parity, load warning and retry');
})().catch(error=>{console.error(error);process.exitCode=1;});
