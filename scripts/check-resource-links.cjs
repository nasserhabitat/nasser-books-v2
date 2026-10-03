const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),cp=require('node:child_process');
const root=path.resolve(__dirname,'..');
const catalog=JSON.parse(fs.readFileSync(path.join(root,'ai-index.json'),'utf8')).books;
const baseline=JSON.parse(cp.execFileSync('git',['show','HEAD:ai-index.json'],{cwd:root,encoding:'utf8',maxBuffer:10e6})).books;
const oldHtmlIds=new Set(baseline.flatMap(b=>['ar','en'].map(l=>b[l].html?.match(/[?&]id=([\w-]+)/)?.[1])).filter(Boolean));
const missing=[],deprecated=[];let anchors=0;
function walk(folder){for(const d of fs.readdirSync(folder,{withFileTypes:true})){if(['.git','scripts','content.files'].includes(d.name))continue;const p=path.join(folder,d.name);if(d.isDirectory()){walk(p);continue;}if(!p.endsWith('.html'))continue;const source=fs.readFileSync(p,'utf8');for(const m of source.matchAll(/<a\b[^>]*href=["']([^"']+)["'][^>]*>([\s\S]*?)<\/a>/gi)){anchors++;let url=m[1].replaceAll('&amp;','&');if([...oldHtmlIds].some(id=>url.includes(id))||url.includes('archive.org/details/')||(/drive\.google\.com/.test(url)&&/\bHTML\b/i.test(m[2])))deprecated.push({file:path.relative(root,p),url});let match=url.match(/books\/([^/]+)\/(ar|en)\/([^?#]+\.txt)/);if(match){const book=catalog.find(b=>b.id.toLowerCase()===match[1].toLowerCase());if(book){const expected=`${book.book_number}-${book.id}-${match[2]}.txt`;if(match[1]!==book.id||match[3]!==expected)missing.push({file:path.relative(root,p),url,expected});}}}}
}
walk(root);assert.deepEqual(deprecated,[]);assert.deepEqual(missing,[]);console.log(JSON.stringify({anchorsChecked:anchors,deprecatedBookDownloads:deprecated.length,incorrectTextPaths:missing.length},null,2));
