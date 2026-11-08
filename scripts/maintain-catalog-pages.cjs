// Generate public catalogue views from the authoritative catalogue, without editing books.
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const books=JSON.parse(fs.readFileSync(path.join(root,'ai-index.json'),'utf8')).books.slice().sort((a,b)=>a.book_number-b.book_number);
const base='https://nasserhabitat.github.io/nasser-books-v2/';
const license='https://creativecommons.org/licenses/by-sa/4.0/';
const esc=s=>String(s||'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const url=(b,l)=>`${base}books/${b.id}/${l}/`;
const cover=(b,l)=>new URL(b[l].cover,base).href;
const schema=(b,l)=>({'@type':'Book','@id':url(b,l)+'#book',url:url(b,l),name:b.titles[l],description:b.description[l],inLanguage:l,image:cover(b,l),author:{'@type':'Person',name:'ناصر ابن داوود'},license,isAccessibleForFree:true});
function shell(file,title,body,data){return `<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(title)} — مكتبة ناصر ابن داوود</title><link rel="canonical" href="${base+file}"><meta property="og:url" content="${base+file}">
<style>body{font:18px/1.8 system-ui;margin:0;background:#f4f6f8;color:#193347}main{max-width:1100px;margin:auto;padding:24px}a{color:#075985;overflow-wrap:anywhere}.book{background:white;padding:24px;border:1px solid #d8e0e7;border-radius:12px;margin:24px 0}.editions{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:24px}img{max-width:120px;height:170px;object-fit:contain}nav,.resources{display:flex;flex-wrap:wrap;gap:16px}h1,h2,h3{line-height:1.5}a:focus-visible{outline:3px solid #b45309;outline-offset:4px}</style>
${data?'<script type="application/ld+json">'+JSON.stringify(data).replaceAll('<','\\u003c')+'</script>':''}</head>
<body><main><nav><a href="index.html">المكتبة</a><a href="books-index.html">الفهرس التفصيلي</a><a href="search.html">البحث</a><a href="reader.html">قارئ PDF</a></nav>
<h1>${esc(title)}</h1><p>${books.length} كتابًا، بإجمالي ${books.length*2} إصدارًا بالعربية والإنجليزية. تتفاوت صيغ التنزيل المتاحة بحسب الإصدار.</p>
${body}<footer><a href="${license}">CC BY-SA 4.0</a> · ناصر ابن داوود</footer></main></body></html>\n`;}
function edition(b,l,micro=false){const r=b[l],p=micro?' itemprop="':'';return `<section lang="${l}" dir="${l==='ar'?'rtl':'ltr'}"${micro?' itemscope itemtype="https://schema.org/Book"':''}>
<h3${micro?' itemprop="name"':''}>${esc(b.titles[l])}</h3><img ${micro?'itemprop="image" ':''}src="${esc(cover(b,l))}" alt="${esc(b.titles[l])}" loading="lazy">
<p${micro?' itemprop="description"':''}>${esc(b.description[l])}</p>
${micro?`<meta itemprop="inLanguage" content="${l}"><span itemprop="author">ناصر ابن داوود</span> · <a itemprop="license" href="${license}">CC BY-SA 4.0</a>`:''}
<div class="resources"><a ${micro?'itemprop="url" ':''}href="${esc(url(b,l))}">${l==='ar'?'صفحة الكتاب':'Book page'}</a>${[['txt_direct','TXT'],['docx','Word'],['pdf_external','PDF']].filter(([key])=>r[key]).map(([key,label])=>`<a href="${esc(r[key])}">${label}</a>`).join(' ')}</div></section>`;}
const cards=micro=>books.map(b=>`<div class="book"><h2>${b.book_number}. ${esc(b.titles.ar)}</h2><div class="editions">${edition(b,'ar',micro)}${edition(b,'en',micro)}</div></div>`).join('\n');
const outputs={
 'books.html':shell('books.html','جميع الكتب',cards(false)),
 'microdata-books.html':shell('microdata-books.html','فهرس الكتب — البيانات المهيكلة',cards(true)),
 'structured-data.html':shell('structured-data.html','فهرس المكتبة المنظم',books.map(b=>`<div class="book"><h2>${b.book_number}. ${esc(b.titles.ar)}</h2><a href="${esc(url(b,'ar'))}">العربية</a> · <a href="${esc(url(b,'en'))}" lang="en">${esc(b.titles.en)}</a></div>`).join('\n'),{'@context':'https://schema.org','@type':'ItemList',numberOfItems:books.length*2,itemListElement:books.flatMap(b=>['ar','en'].map(l=>schema(b,l))).map((item,i)=>({'@type':'ListItem',position:i+1,item}))})
};
for(const [file,text] of Object.entries(outputs)){const p=path.join(root,file);if(process.argv.includes('--check')){if(fs.readFileSync(p,'utf8')!==text)throw Error(file+' is out of date');}else fs.writeFileSync(p,text);}
console.log('PASS: three catalogue views synchronized with '+books.length+' books');
