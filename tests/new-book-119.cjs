const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),cp=require('node:child_process'),vm=require('node:vm');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const cat=JSON.parse(read('ai-index.json')).books,search=JSON.parse(read('search-index.json')).books,id='fiqh-al-ilm-wal-lisan-part2';
assert.equal(cat.length,119);assert.equal(search.length,119);assert.equal(new Set(cat.map(b=>b.id)).size,119);
assert.equal(new Set(cat.map(b=>b.book_number)).size,119);
const baseline=JSON.parse(cp.execFileSync('git',['show','HEAD:ai-index.json'],{cwd:root,encoding:'utf8',maxBuffer:20e6})).books;
for(const old of baseline)assert.deepEqual(cat.find(b=>b.id===old.id),old,'Prior metadata changed');
const b=cat.find(b=>b.book_number===119),s=search.find(b=>b.id===id);assert.equal(b.id,id);
const ids={ar:['1txg0IarnXFM19OXd19q5jvQqAnVPjbMI','14sZWmJFpnTFdPj2LCqsEu9G4a2VTcTK-'],en:['1kSyl7OL9Wxv9Qu-dqg94vCvToNXiidmE','1UWV8drx60jAH-8GhUwACfW6sfDB94Z3Z']};
for(const lang of ['ar','en']){
 const source=path.resolve(root,'../../google_books','119-'+id,lang);
 assert.deepEqual(fs.readFileSync(path.join(root,s.links[lang].text)),fs.readFileSync(path.join(source,`119-${id}-${lang}.txt`)));
 assert.deepEqual(fs.readFileSync(path.join(root,b[lang].cover)),fs.readFileSync(path.join(source,`119-${id}-${lang}-cover.png`)));
 assert(b[lang].docx.endsWith(ids[lang][0]));assert(b[lang].pdf_external.endsWith(ids[lang][1]));
 const page=read(`books/${id}/${lang}/index.html`);
 assert(page.includes('role="note"'));assert(page.includes(b[lang].docx.replaceAll('&','&amp;')));assert(page.includes(b[lang].pdf_external.replaceAll('&','&amp;')));
 assert(!/archive\.org|content\.html?/.test(page));
 assert(!fs.readdirSync(path.join(root,'books',id,lang)).some(n=>/\.(docx|pdf)$/i.test(n)));
 for(const file of ['sitemap.xml','sitemap-books.xml','sitemap-bing.xml'])assert(read(file).includes(`books/${id}/${lang}/`));
 const edition=JSON.parse(read('assets/pdf-reader-catalog.json')).editions.find(e=>e.number===119&&e.language===lang);assert.equal(edition.status,'ready');assert.equal(edition.drive_id,ids[lang][1]);
}
for(const file of ['arabic-books.html','english-books.html','books.html']){const text=read(file);assert(text.indexOf('<h2>119. ')>=0);assert(text.indexOf('<h2>119. ')<text.indexOf('<h2>118. '));}
const script=[...read('search.html').matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]).join('\n');
const elements={localSearch:{value:''},fastSearch:{checked:false},categoryFilter:{value:'all'},scopeFilter:{value:'content_only'},localResults:{innerHTML:''},searchProgress:{style:{}}};
const ctx=vm.createContext({document:{addEventListener(){},getElementById:id=>elements[id]},window:{},console,AbortController,setTimeout(fn,ms){if(ms===30)fn();return 1;},clearTimeout(){},fetch:async url=>({ok:true,text:async()=>read(url)})});vm.runInContext(script,ctx);
(async()=>{for(const [lang,term] of [['ar','الرزق المعرفي'],['en','epistemic provision']]){elements.localSearch.value=term;await ctx.performLocalSearch();assert(elements.localResults.innerHTML.includes(`books/${id}/${lang}/`));assert(elements.localResults.innerHTML.includes('class="match-line"'));}console.log('PASS: book 119, verbatim bilingual TXT/covers, prior records, Drive IDs, reader, maps, newest-first lists and full-text excerpts');})().catch(e=>{console.error(e);process.exitCode=1;});
