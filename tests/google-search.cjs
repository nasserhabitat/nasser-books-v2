const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const html=read('search.html');
assert(html.includes('id="local-search"')&&html.includes('tab-content active" id="local-search"'));
assert(html.includes('assets/google-search.js'));
assert(html.includes('https://cse.google.com/cse?cx=87a2ea74c56054f92'));
assert(!html.includes('src="https://cse.google.com/cse.js'));
function setup(hash='',readyState='loading'){
 const events={},tab={},retry={hidden:true},status={},widget={},scripts=[];let timeout;
 function node(active=false){const classes=new Set(active?['active']:[]);return {classList:{add:c=>classes.add(c),remove:c=>classes.delete(c),contains:c=>classes.has(c)}};}
 const googleTab=Object.assign(node(),{addEventListener:(name,fn)=>tab[name]=fn}),googleSection=node(),localTab=node(true),localSection=node(true);
 const ctx=vm.createContext({window:{location:{hash},addEventListener:(name,fn)=>events[name]=fn},document:{readyState,
  addEventListener:(name,fn)=>events[name]=fn,
  querySelector:()=>googleTab,
  querySelectorAll:()=>[googleTab,googleSection,localTab,localSection],
  getElementById:id=>({'google-search':googleSection,'google-search-status':status,'google-search-retry':{get hidden(){return retry.hidden},set hidden(v){retry.hidden=v},addEventListener:(name,fn)=>retry[name]=fn},'google-search-widget':widget,'google-search-loader':scripts.at(-1)})[id],
  createElement:()=>({remove(){scripts.splice(scripts.indexOf(this),1)}}),
  head:{appendChild:s=>scripts.push(s)}
 },setTimeout:fn=>{timeout=fn;return 1},clearTimeout(){}});
 vm.runInContext(read('assets/google-search.js'),ctx);
 if(readyState==='loading')events.DOMContentLoaded();
 return {ctx,tab,retry,status,scripts,events,googleTab,googleSection,localTab,localSection,failTimeout:()=>timeout()};
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
for(const hash of ['#gsc.tab=0&gsc.sort=','#gsc.q=reflection','#gsc.tab=0&gsc.q=%D8%A7'])for(const ready of ['loading','interactive','complete']){
 const direct=setup(hash,ready);assert.equal(direct.scripts.length,1);assert(direct.googleTab.classList.contains('active'));assert(direct.googleSection.classList.contains('active'));assert(!direct.localSection.classList.contains('active'));
 direct.events.hashchange();assert.equal(direct.scripts.length,1,'Hash changes must not duplicate loader');
}
for(const hash of ['','#local-search','#not-gsc.q=test','#note=gsc.q=test'])assert.equal(setup(hash).scripts.length,0,'Unrelated anchors must not load Google');
const changed=setup();changed.ctx.window.location.hash='#gsc.q=tree';changed.events.hashchange();assert.equal(changed.scripts.length,1);assert(changed.googleSection.classList.contains('active'));
console.log('PASS: Google lazy load, direct hash tab activation, hash changes, DOM timing, failure/retry and local-search default');
