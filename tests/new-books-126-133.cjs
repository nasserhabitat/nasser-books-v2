const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto'),cp=require('node:child_process');
process.chdir(path.resolve(__dirname,'..'));
const read=p=>fs.readFileSync(p,'utf8'),hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const cat=JSON.parse(read('ai-index.json')),search=JSON.parse(read('search-index.json')).books;
const manifest=JSON.parse(read('scripts/books-126-133-sources.json'));
const pdf=JSON.parse(read('assets/pdf-reader-catalog.json')).editions;
assert.equal(cat.books.length,133);assert.equal(search.length,133);assert.equal(cat.library.total_books,266);
const baseline=JSON.parse(cp.execFileSync('git',['show','HEAD:ai-index.json'],{encoding:'utf8',maxBuffer:20e6})).books;
for(const b of baseline.filter(b=>b.book_number<=125))assert.deepEqual(cat.books.find(x=>x.id===b.id),b);
assert.equal(manifest.assets.length,16);
for(const a of manifest.assets){
 const b=cat.books.find(x=>x.book_number===a.number),s=search.find(x=>x.id===b.id),lang=a.language;
 assert.equal(hash(s.links[lang].text),a.text_sha256);
 assert.equal(hash(b[lang].cover),a.cover_sha256);
 assert.deepEqual(s.metadata,b.metadata);assert.deepEqual(s.titles,b.titles);
 const html=read('books/'+b.id+'/'+lang+'/index.html');
 assert(!html.includes('href=""'));assert(html.includes('role="note"'));
 const files=manifest.files.filter(f=>f.number===a.number&&f.language===lang);
 for(const [ext,key] of [['.docx','docx'],['.pdf','pdf_external']]){
  const f=files.find(f=>f.name.endsWith(ext));
  if(f){assert(f.public_readable);assert(b[lang][key].endsWith('id='+f.id));}
  else assert.equal(b[lang][key],'');
 }
 const p=pdf.find(x=>x.number===a.number&&x.language===lang);
 assert.equal(p.status,'ready');
 assert(p.drive_id);
 if(a.number===130||(a.number===128&&lang==='en'))assert.equal(a.text_source,'original_drive_txt');
 for(const map of ['sitemap.xml','sitemap-books.xml','sitemap-bing.xml'])
  assert.equal(read(map).split('books/'+b.id+'/'+lang+'/</loc>').length-1,1);
}
const covers=manifest.assets.filter(a=>a.number===132);
assert.equal(covers[0].cover_sha256,covers[1].cover_sha256);
console.log('PASS: 8 books, 16 editions, exact source/cover hashes, preserved prior records, Drive links, all PDFs ready and sitemap entries');
