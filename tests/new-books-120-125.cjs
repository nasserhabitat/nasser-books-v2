const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto'),cp=require('node:child_process'),vm=require('node:vm');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const cat=JSON.parse(read('ai-index.json')),search=JSON.parse(read('search-index.json')).books;
const sources=JSON.parse(read('scripts/books-120-125-sources.json'));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
assert(cat.books.length>=125);assert.equal(search.length,cat.books.length);
assert.equal(cat.library.total_books,cat.books.length*2);
assert.equal(new Set(cat.books.map(b=>b.id)).size,cat.books.length);
assert.equal(new Set(cat.books.map(b=>b.book_number)).size,cat.books.length);
const baseline=JSON.parse(cp.execFileSync('git',['show','HEAD:ai-index.json'],{cwd:root,encoding:'utf8',maxBuffer:20e6})).books;
for(const old of baseline)assert.deepEqual(cat.books.find(b=>b.id===old.id),old,'Prior metadata changed');
const reader=JSON.parse(read('assets/pdf-reader-catalog.json')).editions;
for(const source of sources.books){
 const b=cat.books.find(b=>b.book_number===source.number),s=search.find(b=>b.id===source.id);
 assert.equal(b.id,source.id);assert.deepEqual(s.titles,b.titles);
 for(const [lang,edition] of Object.entries(source.editions)){
  assert.equal(hash(s.links[lang].text),edition.text.sha256,'Downloaded TXT bytes changed');
  assert.equal(hash(b[lang].cover),edition.cover.sha256,'Cover bytes changed');
  const page=read(`books/${b.id}/${lang}/index.html`);
  assert(page.includes('role="note"'));assert(b.metadata.edition_notes[lang]);
  assert(!/archive\.org|content\.html?/.test(page));
  assert(!fs.readdirSync(path.join(root,'books',b.id,lang)).some(f=>/\.(docx|pdf)$/i.test(f)));
  for(const [ext,key] of [['.docx','docx'],['.pdf','pdf_external']]){
   const file=edition.files.find(f=>f.name.endsWith(ext));assert(file.anyone_reader);
   assert(b[lang][key].endsWith('id='+file.id));assert(page.includes(b[lang][key].replaceAll('&','&amp;')));
  }
  const pdf=edition.files.find(f=>f.name.endsWith('.pdf'));
  const r=reader.find(e=>e.number===source.number&&e.language===lang);
  assert.equal(r.status,'ready');assert.equal(r.drive_id,pdf.id);
  for(const file of ['sitemap.xml','sitemap-books.xml','sitemap-bing.xml'])assert.equal(read(file).split(`books/${b.id}/${lang}/</loc>`).length-1,1);
  if([123,124].includes(source.number)){
   assert.equal(b.metadata.final_scholarly_review,'pending_as_stated_in_source');
   assert(page.includes(lang==='ar'?'تنبيه الحالة':'Status:'));
   assert(b.description[lang].includes(lang==='ar'?'نسخة':'candidate'));
  }
 }
}
for(const file of ['arabic-books.html','english-books.html','books.html']){
 const html=read(file);
 for(let n=125;n>=120;n--)assert(html.indexOf(`<h2>${n}. `)<html.indexOf(`<h2>${n-1}. `),'Newest first');
}
const code=[...read('search.html').matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]).join('\n');
const elements={localSearch:{value:''},fastSearch:{checked:false},categoryFilter:{value:'all'},scopeFilter:{value:'content_only'},localResults:{innerHTML:''},searchProgress:{style:{}}};
const ctx=vm.createContext({document:{addEventListener(){},getElementById:id=>elements[id]},window:{},console,AbortController,setTimeout(fn,ms){if(ms===30)fn();return 1;},clearTimeout(){},fetch:async url=>({ok:true,text:async()=>read(url)})});
vm.runInContext(code,ctx);
(async()=>{
 for(const [number,lang,term] of [[120,'ar','مصفوفة وظائف الرسول'],[121,'en','IS KNOWLEDGE SOLD'],[122,'ar','مساءلة المرجعية واختبار اللسان'],[123,'en','Architecture of Presence'],[124,'ar','الاستغفار في اللسان القرآني'],[125,'en','The Messiah and the Dajjal']]){
  elements.localSearch.value=term;await ctx.performLocalSearch();
  const b=cat.books.find(b=>b.book_number===number);
  assert(elements.localResults.innerHTML.includes(`books/${b.id}/${lang}/`),`Full text missing: ${number}/${lang}`);
  assert(elements.localResults.innerHTML.includes('class="match-line"'));
 }
 console.log('PASS: books 120–125, preserved source bytes and prior records, Drive IDs, edition status, reader, maps, ordering and full-text excerpts');
})().catch(e=>{console.error(e);process.exitCode=1;});
