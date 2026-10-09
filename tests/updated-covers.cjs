const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const books=JSON.parse(read('ai-index.json')).books;
const search=JSON.parse(read('search-index.json')).books;
let covers=0;
for(const b of books)for(const l of ['ar','en']){
 assert(b[l].cover,`${b.id}/${l}: missing cover`);
 const p=b[l].cover;assert(fs.existsSync(path.join(root,p)),p);covers++;
 if(b.book_number>=70){
  const name=path.basename(p);
  assert([`${b.id}-cover-${l}.png`,`${b.id}-cover-${l}.jpg`,`${b.book_number}-${b.id}-${l}-cover.png`,`${b.id}-${l}-cover.png`].includes(name));
  assert.equal(search.find(s=>s.id===b.id).links[l].cover,p);
  const page=read(`books/${b.id}/${l}/index.html`);
  assert(page.includes(`src="${path.basename(p)}"`),`${b.id}/${l}: image element missing`);
  const schema=[...page.matchAll(/<script\b[^>]*type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/g)].map(m=>JSON.parse(m[1]));
  assert(schema.some(s=>s.image==='https://nasserhabitat.github.io/nasser-books-v2/'+p),`${b.id}/${l}: structured cover incorrect`);
 }
}
const reviewFile=path.join(root,'scripts/updated-archive-review.json');
const conversions=JSON.parse(read('scripts/migration-report.json')).site_cover_conversions||[];
if(fs.existsSync(reviewFile))for(const r of JSON.parse(fs.readFileSync(reviewFile,'utf8')).editions){
 const b=books.find(b=>b.id===r.id);const raw=fs.readFileSync(path.join(root,b[r.language].cover));
 const converted=conversions.find(c=>c.Cover===b[r.language].cover);
 assert.equal(crypto.createHash('sha256').update(raw).digest('hex'),converted?.Sha256||r.cover_sha256,`${r.id}/${r.language}: source image changed`);
}
assert.equal(covers,books.length*2);console.log(`PASS: ${covers} covers, new edition image elements, metadata, and supplied-image checksums`);
