const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),vm=require('node:vm');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const data=JSON.parse(read('assets/pdf-reader-catalog.json'));
const cat=JSON.parse(read('ai-index.json')).books;
const uploads=JSON.parse(read('scripts/new-pdf-drive-uploads.json')).files;
assert.equal(data.editions.length,cat.length*2);assert.equal(uploads.length,86);
assert(uploads.every(f=>f.verified&&f.public&&f.mime_type==='application/pdf'));
assert.equal(data.summary.ready,data.editions.filter(e=>e.status==='ready').length);assert.equal(data.summary.pending,0);
for(const e of data.editions){
 const book=cat.find(b=>b.id===e.book_id),s=read(`books/${e.book_id}/${e.language}/index.html`);
 assert.equal((s.match(/library-pdf-reader:start/g)||[]).length,1);
 assert.equal((s.match(/assets\/pdf-reader.js/g)||[]).length,1);
 assert(!/<iframe\b/i.test(s),'PDF should load only on request');
 if(e.status==='ready')assert(book[e.language].pdf_external.endsWith(e.drive_id));
 else assert(!e.drive_id,'Unverified PDFs must not be embedded');
 if(e.number>=70){
  assert.equal(e.status,'ready');assert(s.includes(e.drive_id));
  assert(read(e.language==='ar'?'arabic-books.html':'english-books.html').includes(e.drive_id));
  assert(read('books.html').includes(e.drive_id));
 }
}
new vm.Script(read('assets/pdf-reader.js'));
const js=read('assets/pdf-reader.js');assert(js.includes("button.addEventListener('click'"));assert(js.includes('/preview'));
assert(read('index.html').includes('href="reader.html"'));
assert(read('books-index.html').includes('reader.html?book='));
console.log(`PASS: 86 verified historical PDF uploads, ${data.editions.length} edition states, lazy reader and listing links`);
