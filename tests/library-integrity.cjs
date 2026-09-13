const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
process.chdir(path.resolve(__dirname,'..'));
const books=JSON.parse(fs.readFileSync('ai-index.json','utf8')).books;
const base='https://nasserhabitat.github.io/nasser-books-v2/';
let pages=0;
for(const book of books)for(const lang of ['ar','en']){
 const txt=book[lang].txt_direct.replace(/^.*\/books\//,'books/');
 assert.ok(fs.statSync(txt).size>0,txt);
 const file=txt.replace(/content\.txt$/,'index.html');
 const html=fs.readFileSync(file,'utf8');
 const canonical=base+file.replace(/index\.html$/,'');
 assert.ok(html.includes(`rel="canonical" href="${canonical}"`),file);
 for(const l of ['ar','en'])assert.ok(html.includes(`hreflang="${l}"`),file);
 const schemas=[...html.matchAll(/<script\b[^>]*type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/g)].map(m=>JSON.parse(m[1]));
 assert.ok(schemas.length,file);
 assert.ok(html.includes('https://creativecommons.org/licenses/by-sa/4.0/'),file);
 pages++;
}
for(const name of ['sitemap.xml','sitemap-books.xml','sitemap-bing.xml']){
 const urls=[...fs.readFileSync(name,'utf8').matchAll(/<loc>([^<]+)<\/loc>/g)].map(m=>m[1]);
 assert.equal(urls.length,new Set(urls).size);
 for(const url of urls){assert.ok(url.startsWith(base));const p=url.slice(base.length);assert.ok(fs.existsSync(p.endsWith('/')||!p?p+'index.html':p),url);}
}
console.log(`PASS: ${pages} book pages, text files, metadata and sitemap targets`);
