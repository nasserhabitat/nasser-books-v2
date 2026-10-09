const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),cp=require('node:child_process'),vm=require('node:vm');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const cat=JSON.parse(read('ai-index.json')).books,search=JSON.parse(read('search-index.json')).books;
const baseline=JSON.parse(cp.execFileSync('git',['show','HEAD:ai-index.json'],{cwd:root,encoding:'utf8',maxBuffer:20e6})).books;
// Compare all original records, not just Drive URLs; safe after this change is committed too.
for(const b of baseline)assert.deepEqual(cat.find(n=>n.id===b.id),b,`Existing record changed: ${b.id}`);
assert(cat.length>=115);assert.equal(new Set(cat.map(b=>b.id)).size,cat.length);
const additions=cat.filter(b=>b.book_number>=113&&b.book_number<=115);
assert.equal(additions.length,3);
for(const b of additions)for(const lang of ['ar','en']){
 const entry=search.find(s=>s.id===b.id);
 const source=path.join(root,'../../google_books',`${b.book_number}-${b.id}`,lang,`${b.book_number}-${b.id}-${lang}.txt`);
 assert.deepEqual(fs.readFileSync(path.join(root,entry.links[lang].text)),fs.readFileSync(source),'Author text must be copied verbatim');
 const page=read(`books/${b.id}/${lang}/index.html`);
 assert(page.includes(b[lang].docx.replaceAll('&','&amp;')));
 assert(page.includes(b[lang].pdf_external.replaceAll('&','&amp;')));
 assert(!/archive\.org|content\.html?/.test(page));
 for(const file of ['sitemap.xml','sitemap-books.xml','sitemap-bing.xml'])assert(read(file).includes(`books/${b.id}/${lang}/`));
}
for(const file of ['arabic-books.html','english-books.html']){
 const text=read(file),positions=[115,114,113,112].map(n=>text.indexOf(`<h2>${n}. `));
 assert(positions.every(p=>p>=0));assert.deepEqual(positions,[...positions].sort((a,b)=>a-b));
}
const html=read('search.html'),script=[...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]).join('\n');
const elements={localSearch:{value:''},fastSearch:{checked:false},categoryFilter:{value:'all'},scopeFilter:{value:'content_only'},localResults:{innerHTML:''},searchProgress:{style:{}}};
const ctx=vm.createContext({document:{addEventListener(){},getElementById:id=>elements[id]},window:{},console,AbortController,setTimeout(fn,ms){if(ms===30)fn();return 1;},clearTimeout(){},fetch:async url=>({ok:true,text:async()=>read(url)})});
vm.runInContext(script,ctx);
(async()=>{
 for(const [number,term] of [[113,'الشجرة'],[114,'الوجدان'],[115,'الشرك']]){
  elements.localSearch.value=term;await ctx.performLocalSearch();
  const b=cat.find(b=>b.book_number===number),out=elements.localResults.innerHTML;
  assert(out.includes(`books/${b.id}/ar/`),`${number} missing from full-text results`);
  assert(out.includes('class="match-line"'),'Full-text excerpts missing');
 }
 console.log('PASS: books 113–115, original metadata preservation, verbatim texts, newest-first listings and full-text excerpts');
})().catch(e=>{console.error(e);process.exitCode=1;});
