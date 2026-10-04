const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),assert=require('node:assert/strict');
const source=path.resolve(__dirname,'..'),target='C:/Users/nasse/OneDrive/Documents/GitHub/nasser-books';
const report=JSON.parse(fs.readFileSync(path.join(source,'scripts/legacy-site-sync-report.json'),'utf8'));
const books=JSON.parse(fs.readFileSync(path.join(target,'ai-index.json'),'utf8')).books;
const tracked=new Set(cp.execFileSync('git',['-C',target,'-c','core.quotepath=false','ls-files'],{encoding:'utf8'}).trim().split('\n'));
assert.equal(books.length,112);
let aliases=0;
for(const b of books)for(const lang of ['ar','en']){
 const sourceFolder=`books/${b.id}/${lang}/`;
 const folder=`books/${b.id==='numbers-as-legislation'?'numbers-as-Legislation':b.id}/${lang}/`,txt=`${b.book_number}-${b.id}-${lang}.txt`,cover=`${b.id}-cover-${lang}.png`;
 for(const name of ['index.html',txt,cover,'content.txt',`cover-${lang}.png`])assert(tracked.has(folder+name),`Exact Git path missing: ${folder+name}`);
 for(const [name,alias] of [[txt,'content.txt'],[cover,`cover-${lang}.png`]]){
  const original=fs.readFileSync(path.join(source,sourceFolder,name));
  assert(original.equals(fs.readFileSync(path.join(target,folder,name))));
  assert(original.equals(fs.readFileSync(path.join(target,folder,alias))));aliases++;
 }
 assert.equal(b[lang].txt_direct,`https://nasserhabitat.github.io/nasser-books/${folder}${txt}`);
 const html=fs.readFileSync(path.join(target,folder,'index.html'),'utf8');
 assert(html.includes(`rel="canonical" href="https://nasserhabitat.github.io/nasser-books/${folder}"`));
 assert(!html.includes('nasser-books-v2'));
}
const textExtensions=new Set(['.html','.htm','.json','.xml','.js','.cjs','.css','.md','.py','.ps1','.yml','.yaml']);
for(const relative of report.managed_paths){
 if(!textExtensions.has(path.extname(relative))&&relative!=='robots.txt')continue;
 assert(!fs.readFileSync(path.join(target,relative),'utf8').includes('nasser-books-v2'),relative);
}
console.log(JSON.stringify({books:books.length,compatibilityAliases:aliases,exactCasePaths:true,internalUrls:'nasser-books',manuscriptBinariesPreservedBySync:report.protected_book_files}));
