const fs=require('node:fs'),cp=require('node:child_process'),assert=require('node:assert/strict');
const base='https://nasserhabitat.github.io/nasser-books-v2/';
const catalog=JSON.parse(fs.readFileSync('ai-index.json','utf8')).books;
const main=['index.html','books.html','books-index.html','arabic-books.html','english-books.html','search.html','ai-recommendations.html','reader.html'];
const files=[...main,...catalog.flatMap(b=>['ar','en'].map(l=>`books/${b.id}/${l}/index.html`))];
for(const file of files){
 const text=fs.readFileSync(file,'utf8');
 // Resource links and file names intentionally changed in this migration.
 // Use --preserve-bodies only for a subsequent metadata-only maintenance pass.
 if(process.argv.includes('--preserve-bodies')) {
  const old=cp.execFileSync('git',['show','HEAD:'+file],{encoding:'utf8',maxBuffer:20*1024*1024});
  assert.equal(text.slice(text.indexOf('</head>')),old.slice(old.indexOf('</head>')),file+' body');
 }
 const head=text.slice(0,text.indexOf('</head>'));
 const canonical=[...head.matchAll(/<link rel="canonical" href="([^"]+)"/g)];
 assert.equal(canonical.length,1,file);assert.ok(canonical[0][1].startsWith(base));
 for(const m of head.matchAll(/<script\b[^>]*type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/g)) JSON.parse(m[1]);
 if(file.startsWith('books/')){
  assert.equal([...head.matchAll(/hreflang="(?:ar|en)"/g)].length,2,file);
  for(const m of head.matchAll(/hreflang="(?:ar|en)" href="([^"]+)"/g)) assert.ok(fs.existsSync(m[1].replace(base,'')+'index.html'));
 }
}
for(const file of ['sitemap.xml','sitemap-books.xml','sitemap-bing.xml']){
 const urls=[...fs.readFileSync(file,'utf8').matchAll(/<loc>([^<]+)<\/loc>/g)].map(m=>m[1]);
 assert.equal(urls.length,new Set(urls).size);
 assert.equal(urls.length,file==='sitemap-books.xml'?catalog.length*2:catalog.length*2+8);
 for(const url of urls){assert.ok(url.startsWith(base));const p=url.slice(base.length);assert.ok(fs.existsSync(!p?'index.html':p.endsWith('/')?p+'index.html':p));}
}
console.log('PASS: '+files.length+' changed pages; canonical, language links, JSON-LD and sitemap targets valid');
