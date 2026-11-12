const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),cp=require('node:child_process'),vm=require('node:vm');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const cat=JSON.parse(read('ai-index.json')).books,search=JSON.parse(read('search-index.json')).books;
const id='The_measure_of_stewardship_in_surah_sad',n=140;
assert.equal(cat.length,140);assert.equal(search.length,cat.length);
assert.equal(new Set(cat.map(b=>b.id)).size,cat.length);assert.equal(new Set(cat.map(b=>b.book_number)).size,cat.length);
const baseline=JSON.parse(cp.execFileSync('git',['show','HEAD:ai-index.json'],{cwd:root,encoding:'utf8',maxBuffer:20e6})).books;
for(const old of baseline.filter(b=>b.book_number!==n))assert.deepEqual(cat.find(b=>b.id===old.id),old,'Prior metadata changed');
const b=cat.find(b=>b.book_number===n),s=search.find(b=>b.id===id);
assert(b);assert(s);assert.equal(b.id,id);assert.equal(s.book_number,n);
assert(b.metadata.topics_ar.length>=5&&b.metadata.topics_en.length>=5);
assert(b.ar.docx.endsWith('12SOmgy3pw8SScK0Llwr6SsHTHv_C7yzV'));
assert(b.en.docx.endsWith('1flcS52T5tb1A0w7_B6PLComstIRK9g6A'));
assert.equal(b.ar.pdf_external,'');assert.equal(b.en.pdf_external,'');
for(const lang of ['ar','en']){
 assert.ok(fs.statSync(b[lang].txt_direct.replace(/^.*\/books\//,'books/')).size>0);
 assert.ok(fs.statSync(b[lang].cover).size>0);
 const page=read(`books/${id}/${lang}/index.html`);
 assert(page.includes(`rel="canonical" href="https://nasserhabitat.github.io/nasser-books-v2/books/${id}/${lang}/"`));
 for(const l of ['ar','en'])assert(page.includes(`hreflang="${l}"`));
 assert(page.includes('book-page.css'));assert(page.includes('name="keywords"'));
 assert(page.includes(b[lang].docx.replaceAll('&','&amp;')));
 assert(page.includes('PDF غير متاح بعد'));
 assert(!fs.readdirSync(path.join(root,'books',id,lang)).some(f=>/\.(docx|pdf)$/i.test(f)));
 for(const file of ['sitemap.xml','sitemap-books.xml','sitemap-v2.xml','sitemap-bing.xml'])assert(read(file).includes(`books/${id}/${lang}/`));
 const edition=JSON.parse(read('assets/pdf-reader-catalog.json')).editions.find(e=>e.number===n&&e.language===lang);
 assert.equal(edition.status,'pending');assert.equal(edition.drive_id,null);
}
for(const file of ['arabic-books.html','english-books.html']){const text=read(file);assert(text.includes(`<h2>${n}. `));assert(text.indexOf(`<h2>${n}. `)<text.indexOf('<h2>139. '));}
for(const file of ['books.html']){const text=read(file);assert(text.includes(`<h2>${n}. `));assert(text.indexOf('<h2>139. ')<text.indexOf(`<h2>${n}. `));}
const all=read('search.html');assert(all.includes(`books/${id}/ar/`));
assert(all.indexOf(`books/${id}/ar/`)<all.indexOf('books/Mirrors_of_the_Cave_Vol_II/ar/'));
const script=[...all.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]).join('\n');
const elements={localSearch:{value:''},fastSearch:{checked:false},categoryFilter:{value:'all'},scopeFilter:{value:'content_only'},localResults:{innerHTML:''},searchProgress:{style:{}}};
const ctx=vm.createContext({document:{addEventListener(){},getElementById:k=>elements[k]},window:{},console,AbortController,setTimeout(fn,ms){if(ms===30)fn();return 1;},clearTimeout(){},fetch:async url=>({ok:true,text:async()=>read(url)})});
vm.runInContext(script,ctx);
(async()=>{for(const [lang,term] of [['ar','الأرض الناعجة'],['en','productive land']]){elements.localSearch.value=term;await ctx.performLocalSearch();assert(elements.localResults.innerHTML.includes(`books/${id}/${lang}/`));assert(elements.localResults.innerHTML.includes('class="match-line"'));}console.log('PASS: book 140, bilingual TXT/covers, prior records, Drive Word IDs, pending PDF, maps, newest-first lists and full-text excerpts');})().catch(e=>{console.error(e);process.exitCode=1;});
