const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),vm=require('node:vm');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const cat=JSON.parse(read('ai-index.json')).books,search=JSON.parse(read('search-index.json')).books;
assert(cat.length>=117);assert.equal(new Set(cat.map(b=>b.id)).size,cat.length);
assert.equal(new Set(cat.map(b=>b.book_number)).size,cat.length);
for(const number of [116,117])for(const lang of ['ar','en']){
 const b=cat.find(b=>b.book_number===number),s=search.find(s=>s.id===b.id);
 const folder=number===116?'116-SHIRK_Engineering_of_Illusion':'117-THE_BOOK_AS_WITNESS';
 const name=number===116?`SHIRK_Engineering_of_Illusion-${lang}.txt`:`116-THE_BOOK_AS_WITNESS-${lang}.txt`;
 const source=path.resolve(root,'../../google_books',folder,lang);
 assert.deepEqual(fs.readFileSync(path.join(root,s.links[lang].text)),fs.readFileSync(path.join(source,name)),'Source text changed');
 const sourceCover=fs.readdirSync(source).find(n=>n.endsWith('.png'));
 assert.deepEqual(fs.readFileSync(path.join(root,b[lang].cover)),fs.readFileSync(path.join(source,sourceCover)),'Source image changed');
 const page=read(`books/${b.id}/${lang}/index.html`);
 assert(page.includes(b[lang].docx.replaceAll('&','&amp;')));
 assert(page.includes(b[lang].pdf_external.replaceAll('&','&amp;')));
 if(number===116){assert(b.metadata.edition_notes[lang]);assert(page.includes('role="note"'));}
 assert(!/archive\.org|content\.html?/.test(page));
}
assert.notEqual(cat.find(b=>b.book_number===115).id,cat.find(b=>b.book_number===116).id);
for(const file of ['arabic-books.html','english-books.html','books.html']){
 const text=read(file),positions=[117,116,115].map(n=>text.indexOf(`<h2>${n}. `));
 assert(positions.every(p=>p>=0));assert.deepEqual(positions,[...positions].sort((a,b)=>a-b));
}
const html=read('search.html'),script=[...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]).join('\n');
const elements={localSearch:{value:''},fastSearch:{checked:false},categoryFilter:{value:'all'},scopeFilter:{value:'content_only'},localResults:{innerHTML:''},searchProgress:{style:{}}};
const ctx=vm.createContext({document:{addEventListener(){},getElementById:id=>elements[id]},window:{},console,AbortController,setTimeout(fn,ms){if(ms===30)fn();return 1;},clearTimeout(){},fetch:async url=>({ok:true,text:async()=>read(url)})});
vm.runInContext(script,ctx);
(async()=>{
 for(const [number,term] of [[116,'القلب'],[117,'المساءلة']]){
  elements.localSearch.value=term;await ctx.performLocalSearch();
  const book=cat.find(b=>b.book_number===number),out=elements.localResults.innerHTML;
  assert(out.includes(`books/${book.id}/ar/`));assert(out.includes('class="match-line"'));
 }
 console.log('PASS: books 116–117, verbatim source texts/covers, edition warning, newest-first lists and search excerpts');
})().catch(e=>{console.error(e);process.exitCode=1;});
