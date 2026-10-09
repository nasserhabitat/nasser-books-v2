const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const html=read('search.html');
assert(html.includes('id="local-search"')&&html.includes('tab-content active" id="local-search"'));
assert(html.includes('assets/google-search.js'));
assert(html.includes('https://cse.google.com/cse?cx=87a2ea74c56054f92'));
assert(!html.includes('src="https://cse.google.com/cse.js'));
function setup(){
 const events={},tab={},retry={hidden:true},status={},widget={},scripts=[];let timeout;
 const ctx=vm.createContext({window:{},document:{
  addEventListener:(name,fn)=>events[name]=fn,
  querySelector:()=>({addEventListener:(name,fn)=>tab[name]=fn}),
  getElementById:id=>({'google-search-status':status,'google-search-retry':{get hidden(){return retry.hidden},set hidden(v){retry.hidden=v},addEventListener:(name,fn)=>retry[name]=fn},'google-search-widget':widget,'google-search-loader':scripts.at(-1)})[id],
  createElement:()=>({remove(){scripts.splice(scripts.indexOf(this),1)}}),
  head:{appendChild:s=>scripts.push(s)}
 },setTimeout:fn=>{timeout=fn;return 1},clearTimeout(){}});
 vm.runInContext(read('assets/google-search.js'),ctx);
 events.DOMContentLoaded();
 return {ctx,tab,retry,status,scripts,failTimeout:()=>timeout()};
}
const s=setup();assert.equal(s.scripts.length,0,'Google must not load by default');
s.tab.click();assert.equal(s.scripts.length,1);assert(s.scripts[0].src.endsWith('cx=87a2ea74c56054f92'));
s.tab.click();assert.equal(s.scripts.length,1,'No duplicate load');
let renders=0;s.ctx.window.google={search:{cse:{element:{render:config=>{renders++;assert.equal(config.div,'google-search-widget');assert.equal(config.tag,'search')}}}}};
s.ctx.window.__gcse.initializationCallback();assert.equal(renders,1);assert(s.status.textContent.includes('جاهز'));
s.tab.click();assert.equal(renders,1);
const failed=setup();failed.tab.click();failed.scripts[0].onerror();assert.equal(failed.retry.hidden,false);
assert(failed.status.textContent.includes('البحث المحلي متاح'));failed.retry.click();assert.equal(failed.scripts.length,1);
failed.failTimeout();assert.equal(failed.retry.hidden,false);
console.log('PASS: Google search lazy load, engine ID, explicit rendering, failure/retry, local search remains default');
