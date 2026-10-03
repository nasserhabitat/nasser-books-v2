const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),cp=require('node:child_process');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const cat=JSON.parse(read('ai-index.json'));
const search=JSON.parse(read('search-index.json')).books;
const old=JSON.parse(cp.execFileSync('git',['show','HEAD:ai-index.json'],{cwd:root,encoding:'utf8',maxBuffer:10e6})).books;
const corrections=JSON.parse(read('scripts/drive-link-corrections.json'));
assert.equal(cat.books.length,112);assert.equal(search.length,112);
assert.equal(new Set(cat.books.map(b=>b.id)).size,112);
let texts=0,covers=0;
for(const b of cat.books) for(const lang of ['ar','en']) {
 const p=`books/${b.id}/${lang}/`,name=`${b.book_number}-${b.id}-${lang}.txt`;
 assert.equal(b[lang].txt_direct,`https://nasserhabitat.github.io/nasser-books-v2/${p}${name}`);
 assert(fs.existsSync(path.join(root,p,name)));texts++;
 assert(fs.existsSync(path.join(root,p,'index.html')));
 assert(!fs.existsSync(path.join(root,p,'content.txt')));
 assert(!('html' in b[lang]));assert(!('archive' in b[lang]));
 if(b[lang].cover){assert(fs.existsSync(path.join(root,b[lang].cover)));covers++;}
 const s=search.find(s=>s.id===b.id);assert.equal(s.links[lang].text,p+name);
 assert(!('txt_external' in b[lang]));
 if(b.book_number<=69) for(const key of ['docx','pdf_direct','pdf_external']) {
  let expected=old.find(o=>o.id===b.id)[lang][key]?.trim();
  for(const c of corrections) if(c.id===b.id&&c.language===lang&&expected) expected=expected.replace(c.old_file_id,c.new_file_id);
  assert.equal(b[lang][key],expected);
 }
 else assert(!('archive' in b[lang]));
}
const page=read('search.html'),scripts=[...page.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)].filter(m=>!m[1].includes('application/ld+json')&&!m[1].includes('src='));
const context=vm.createContext({document:{addEventListener(){}},Map,console,setTimeout,clearTimeout,AbortController});
scripts.forEach((m,i)=>{new vm.Script(m[2],{filename:`search-${i}`}).runInContext(context)});
assert.equal(vm.runInContext('booksData.length',context),112);
assert.equal(vm.runInContext("normalizeSearchText('الإسلام') === normalizeSearchText('الاسلام')",context),true);
assert.equal(vm.runInContext("searchInText('سطر سابق\\nالأعداد في القرآن\\nسطر لاحق','الاعداد')[0].lineNumber",context),2);
assert.equal(vm.runInContext("searchInText('سطر سابق\\nالأعداد في القرآن\\nسطر لاحق','الاعداد')[0].context.length",context),3);
for(const b of cat.books.filter(b=>b.book_number>=70)) {
 const txt=read(search.find(s=>s.id===b.id).links.ar.text);
 context.sourceText=txt;
 assert(vm.runInContext("searchInText(sourceText,'القرآن').length",context)>0,`New book not searchable: ${b.id}`);
}
let syntax=0;
// TXT is served internally only; Drive resources are Word/PDF.
function checkTextPolicy(dir){for(const e of fs.readdirSync(dir,{withFileTypes:true})){if(['.git','scripts','content.files'].includes(e.name))continue;const p=path.join(dir,e.name);if(e.isDirectory()){checkTextPolicy(p);continue;}if(!p.endsWith('.html'))continue;for(const m of fs.readFileSync(p,'utf8').matchAll(/<a\b[^>]*>.*?<\/a>/gis)){if(!/href\s*=\s*["'][^"']*drive\.google\.com\//i.test(m[0]))continue;const label=m[0].replace(/<[^>]+>/g,'');assert(!/\b(?:TXT|Text)\b|نص/i.test(label),`External text resource: ${p}`);}}}
checkTextPolicy(root);
function walk(dir){for(const entry of fs.readdirSync(dir,{withFileTypes:true})){if(['.git','content.files'].includes(entry.name))continue;const p=path.join(dir,entry.name);if(entry.isDirectory()){walk(p);continue;}if(!p.endsWith('.html'))continue;let i=0;for(const m of fs.readFileSync(p,'utf8').matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)){if(m[1].includes('application/ld+json')){JSON.parse(m[2]);continue;}if(!m[1].includes('src=')){new vm.Script(m[2],{filename:p+':'+i++});syntax++;}}}}
walk(root);
console.log(JSON.stringify({books:112,textFiles:texts,availableCovers:covers,inlineScriptsChecked:syntax,oldDriveLinksPreserved:true,searchNormalizationAndSnippets:'passed'},null,2));
