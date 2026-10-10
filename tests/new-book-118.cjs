const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),cp=require('node:child_process'),vm=require('node:vm');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const cat=JSON.parse(read('ai-index.json')).books,search=JSON.parse(read('search-index.json')).books;
const id='Engineering_Reflection_Qur’anic_Linguistic_Inquiry_and_the_Numerical_Measure_19';
const b=cat.find(b=>b.book_number===118),s=search.find(s=>s.id===id);
assert.equal(b.id,id);assert.equal(cat.length,118);assert.equal(search.length,118);
assert.equal(new Set(cat.map(b=>b.id)).size,118);
const baseline=JSON.parse(cp.execFileSync('git',['show','HEAD:ai-index.json'],{cwd:root,encoding:'utf8',maxBuffer:20e6})).books;
for(const old of baseline)assert.deepEqual(cat.find(n=>n.id===old.id),old);
const ids={ar:['1W_PY9DRfFFVoMYsmMZaMYGgzkoRltz3X','1CKB_JYyuMTO81Zo3H90qF017zC8xZFfl'],en:['1gndWasrjTXo9gPNpmxwu0CCTl064ds6C','1eoxFy4bQBsOCOTanGk-wzRQ9OKg9jUN8']};
for(const lang of ['ar','en']){
 const source=path.resolve(root,'../../google_books','118-'+id,lang);
 assert(b[lang].docx.endsWith(ids[lang][0]));assert(b[lang].pdf_external.endsWith(ids[lang][1]));
 assert.deepEqual(fs.readFileSync(path.join(root,b[lang].cover)),fs.readFileSync(path.join(source,fs.readdirSync(source).find(n=>n.endsWith('.png')))));
 if(lang==='en')assert.deepEqual(fs.readFileSync(path.join(root,s.links.en.text)),fs.readFileSync(path.join(source,'118_'+id+'-en.txt')));
 const page=read(`books/${id}/${lang}/index.html`);
 assert(page.includes(b[lang].docx.replaceAll('&','&amp;')));assert(page.includes(b[lang].pdf_external.replaceAll('&','&amp;')));
 assert(page.includes('role="note"'));assert(b.metadata.edition_notes[lang]);
 assert(!/archive\.org|content\.html?/.test(page));
 assert(!fs.readdirSync(path.join(root,'books',id,lang)).some(n=>/\.(pdf|docx)$/i.test(n)));
 for(const file of ['sitemap.xml','sitemap-books.xml','sitemap-bing.xml'])assert(read(file).includes(`books/${id}/${lang}/`));
}
assert(read(s.links.ar.text).startsWith('هندسة التدبر: فقه اللسان والختم السيبراني للوحي'));
assert(read(s.links.ar.text).includes('● '),'Word bullet markers omitted');
for(const file of ['arabic-books.html','english-books.html','books.html'])assert(read(file).indexOf('<h2>118. ')<read(file).indexOf('<h2>117. '));
const script=[...read('search.html').matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]).join('\n');
const elements={localSearch:{value:''},fastSearch:{checked:false},categoryFilter:{value:'all'},scopeFilter:{value:'content_only'},localResults:{innerHTML:''},searchProgress:{style:{}}};
const ctx=vm.createContext({document:{addEventListener(){},getElementById:id=>elements[id]},window:{},console,AbortController,setTimeout(fn,ms){if(ms===30)fn();return 1;},clearTimeout(){},fetch:async url=>({ok:true,text:async()=>read(url)})});
vm.runInContext(script,ctx);
(async()=>{
 for(const [lang,term] of [['ar','الختم السيبراني'],['en','Numerical']]){
  elements.localSearch.value=term;await ctx.performLocalSearch();
  assert(elements.localResults.innerHTML.includes(`books/${id}/${lang}/`));
  assert(elements.localResults.innerHTML.includes('class="match-line"'));
 }
 console.log('PASS: book 118, preserved prior records and source assets, verified Drive IDs, edition notes, maps and bilingual full-text search');
})().catch(e=>{console.error(e);process.exitCode=1;});
