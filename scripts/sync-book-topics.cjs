// Add reviewed subject terms; preserve existing terms and all manuscript content.
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const write=(p,s)=>{if(read(p)!==s)fs.writeFileSync(path.join(root,p),s);};
const catalog=JSON.parse(read('ai-index.json'));
const additions=JSON.parse(read('scripts/book-topic-additions.json'));
let enriched=0;
for(const b of catalog.books){
 const extra=additions[b.book_number];
 b.metadata.category='quranic_studies';
 if(extra){for(const [i,l] of ['ar','en'].entries())b.metadata['topics_'+l]=[...new Set([...(b.metadata['topics_'+l]||[]),...extra[i]])];enriched++;}
 for(const l of ['ar','en'])if(!b.metadata['topics_'+l]?.length)throw Error('Missing topics: '+b.id+' '+l);
}
write('ai-index.json',JSON.stringify(catalog,null,2)+'\n');
const byId=new Map(catalog.books.map(b=>[b.id.toLowerCase(),b]));
// The local search intentionally embeds its own offline-capable catalogue.
const search=read('search.html'),match=search.match(/const booksData = (\[[\s\S]*?\n\]);/);
if(!match)throw Error('Search catalogue not found');
const embedded=JSON.parse(match[1]);
for(const b of embedded){const source=byId.get(b.id.toLowerCase());if(!source)throw Error(b.id);b.metadata.category=source.metadata.category;for(const l of ['ar','en'])b.metadata['topics_'+l]=source.metadata['topics_'+l];}
write('search.html',search.replace(match[0],()=> 'const booksData = '+JSON.stringify(embedded,null,2).replaceAll('<','\\u003c')+';'));
const esc=s=>s.replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;').replaceAll('>','&gt;');
for(const b of catalog.books)for(const l of ['ar','en']){
 const file=`books/${b.id}/${l}/index.html`,original=read(file),terms=b.metadata['topics_'+l];
 const split=original.indexOf('</head>');if(split<0)throw Error(file);
 let head=original.slice(0,split);
 const tag=`<meta name="keywords" content="${esc(terms.join(', '))}">`;
 if(/<meta\b[^>]*name=["']keywords["'][^>]*>/i.test(head))head=head.replace(/<meta\b[^>]*name=["']keywords["'][^>]*>/gi,tag);
 else head+='    '+tag+'\n';
 head=head.replace(/(<script\b[^>]*type=["']application\/ld\+json["'][^>]*>)([\s\S]*?)(<\/script>)/gi,(_,start,body,end)=>{
  const obj=JSON.parse(body);let changed=false;
  function visit(o){if(!o||typeof o!=='object')return;const types=[].concat(o['@type']||[]);if(types.includes('Book')){o.keywords=terms;changed=true;}for(const v of Object.values(o))if(typeof v==='object')visit(v);}
  visit(obj);return changed?start+'\n'+JSON.stringify(obj,null,2).replaceAll('<','\\u003c')+'\n'+end:start+body+end;
 });
 write(file,head+original.slice(split));
}
for(const name of fs.readdirSync(path.join(root,'api/ai-access/metadata'))){
 const file='api/ai-access/metadata/'+name;if(!fs.statSync(path.join(root,file)).isFile())continue;
 let obj;try{obj=JSON.parse(read(file));}catch{continue;}
 const b=byId.get(String(obj.book?.id||obj.id||'').toLowerCase());if(!b)continue;
 const target=obj.book||obj;target.metadata||={};target.metadata.category=b.metadata.category;for(const l of ['ar','en'])target.metadata['topics_'+l]=b.metadata['topics_'+l];write(file,JSON.stringify(obj,null,2)+'\n');
}
console.log(`PASS: ${enriched} enriched books; bilingual keywords synchronized for ${catalog.books.length} books.`);
