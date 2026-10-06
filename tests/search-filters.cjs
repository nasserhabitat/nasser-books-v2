const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(require('node:path').join(__dirname,'../search.html'),'utf8');
const script=[...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]).join('\n');
const elements={localSearch:{value:'needle'},fastSearch:{checked:false},categoryFilter:{value:'all'},scopeFilter:{value:'all'},localResults:{innerHTML:''},searchProgress:{style:{}}};
let requests=[];
const ctx=vm.createContext({document:{addEventListener(){},getElementById:id=>elements[id]},window:{},console,AbortController,setTimeout(fn,ms){if(ms===30)fn();return 1;},clearTimeout(){},fetch:async url=>{requests.push(url);return {ok:true,text:async()=>url.includes('body')?'before\nneedle\nafter':'no match'};}});
vm.runInContext(script,ctx);
vm.runInContext(`booksData.splice(0,booksData.length,...['title','topic','body'].map((id,i)=>({id,titles:{ar:id==='title'?'needle':'عنوان',en:id},description:{ar:'وصف',en:'description'},metadata:{category:i===2?'digital_projects':'quranic_studies',topics_ar:id==='topic'?['needle']:[],topics_en:[]},links:{ar:{text:id+'_ar'},en:{text:id+'_en'}}})));currentSearchLanguage='ar';`,ctx);
async function run(scope,category='all'){elements.scopeFilter.value=scope;elements.categoryFilter.value=category;requests=[];vm.runInContext('bookContentCache.clear()',ctx);await ctx.performLocalSearch();return elements.localResults.innerHTML;}
(async()=>{
 let out=await run('title_only');assert(out.includes('books/title/ar/'));assert(!out.includes('books/topic/ar/'));assert.equal(requests.length,0);
 out=await run('topics_only');assert(out.includes('books/topic/ar/'));assert(!out.includes('books/title/ar/'));assert.equal(requests.length,0);
 elements.fastSearch.checked=true;out=await run('content_only','digital_projects');assert(out.includes('books/body/ar/'));assert(out.includes('class="match-line"'));assert.deepEqual(requests,['body_ar']);
 ctx.updateSearchScope();assert.equal(elements.fastSearch.checked,false);assert.equal(elements.fastSearch.disabled,true);
 out=await run('title_only','digital_projects');assert(!out.includes('class="book-card"'));assert.equal(requests.length,0);
 out=await run('all');assert(out.indexOf('books/title/ar/')<out.indexOf('books/body/ar/'));assert(out.indexOf('books/body/ar/')<out.indexOf('books/topic/ar/'));
 elements.scopeFilter.value='all';ctx.updateSearchScope();assert.equal(elements.fastSearch.disabled,false);
 console.log('PASS: category, title/topics/content scopes, fetch isolation, excerpts, scoring and fast-search conflict');
})().catch(e=>{console.error(e);process.exitCode=1;});
