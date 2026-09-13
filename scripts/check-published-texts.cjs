const fs=require('node:fs'),cp=require('node:child_process');
const books=JSON.parse(fs.readFileSync('ai-index.json','utf8')).books;
const urls=books.flatMap(b=>['ar','en'].map(l=>b[l].txt_direct.replace('/nasser-books/','/nasser-books-v2/')));
let cursor=0;const failures=[];
async function worker(){while(cursor<urls.length){const url=urls[cursor++];await new Promise(resolve=>cp.execFile('curl.exe',['-L','-sS','--max-time','30','--retry','1','-o','NUL','-w','%{http_code}',url],(error,stdout)=>{if(error||stdout.trim()!=='200')failures.push({url,status:stdout.trim(),error:error?.message});resolve();}));}}
Promise.all(Array.from({length:6},worker)).then(()=>console.log(JSON.stringify({checked:urls.length,failures},null,2)));
