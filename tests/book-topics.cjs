const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const catalog=JSON.parse(fs.readFileSync('ai-index.json','utf8')).books;
const html=fs.readFileSync('search.html','utf8');
const embedded=JSON.parse(html.match(/const booksData = (\[[\s\S]*?\n\]);/)[1]);
for(const b of catalog)for(const l of ['ar','en']){
 assert.equal(b.metadata.category,'quranic_studies');
 assert.equal(embedded.find(e=>e.id===b.id).metadata.category,b.metadata.category);
 const terms=b.metadata['topics_'+l];assert(Array.isArray(terms)&&terms.length>0,b.id+l);
 assert(terms.every(t=>typeof t==='string'&&t.trim().length>0));
 assert.deepEqual(embedded.find(e=>e.id===b.id).metadata['topics_'+l],terms);
 const page=fs.readFileSync(`books/${b.id}/${l}/index.html`,'utf8');
 assert(page.includes('<meta name="keywords"'));
 let found=false;
 function inspect(o){if(!o||typeof o!=='object')return;if([].concat(o['@type']||[]).includes('Book')){assert.deepEqual(o.keywords,terms);found=true;}Object.values(o).forEach(inspect);}
 for(const m of page.matchAll(/<script\b[^>]*type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/g))inspect(JSON.parse(m[1]));assert(found,b.id+l);
}
// Exercise the actual topic-only search in both languages, without fetching book text.
const elements={localSearch:{value:''},fastSearch:{checked:false},categoryFilter:{value:'all'},scopeFilter:{value:'topics_only'},localResults:{innerHTML:''},searchProgress:{style:{}}};
const ctx=vm.createContext({document:{addEventListener(){},getElementById:id=>elements[id]},window:{},console,AbortController,setTimeout(fn,ms){if(ms===30)fn();return 1;},clearTimeout(){},fetch(){throw Error('Topic search must not fetch manuscripts');}});
vm.runInContext([...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]).join('\n'),ctx);
(async()=>{for(const [n,l,term] of [[70,'ar','الدين الخالص'],[97,'en','Conventional banking'],[133,'ar','التطهير'],[139,'en','Al-Raqim']]){
 elements.localSearch.value=term;vm.runInContext(`currentSearchLanguage='${l}'`,ctx);await ctx.performLocalSearch();assert(elements.localResults.innerHTML.includes(`books/${catalog.find(b=>b.book_number===n).id}/${l}/`),term);
}console.log('PASS: bilingual topics, search parity, Book metadata and topic-only results for '+catalog.length+' books');})().catch(e=>{console.error(e);process.exitCode=1;});
