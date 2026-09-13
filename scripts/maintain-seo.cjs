// Reproducible metadata-only maintenance; never rewrites book bodies or licenses.
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const base = 'https://nasserhabitat.github.io/nasser-books-v2/';
const read = p => process.argv.includes('--baseline') && p.endsWith('.html')
 ? require('node:child_process').execFileSync('git',['show','HEAD:'+p],{cwd:root,encoding:'utf8',maxBuffer:20*1024*1024})
 : fs.readFileSync(path.join(root,p),'utf8');
const exists = p => fs.existsSync(path.join(root,p));
const esc = s => String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const catalog = JSON.parse(read('ai-index.json')).books;
const changes = new Map(), issues = [], bookUrls = [];
const migrate = s => s.replaceAll('https://nasserhabitat.github.io/nasser-books/',base);
function update(file,url,book,lang,alternates) {
 const original=read(file);
 const match=original.match(/<head\b[^>]*>([\s\S]*?)<\/head>/i);
 if(!match) throw Error('Missing head: '+file);
 let head=match[1];
 head=head.replace(/<link\b[^>]*>/gi,tag=> /\brel\s*=\s*["']canonical["']/i.test(tag)||/\bhreflang\s*=/i.test(tag)?'':tag);
 let extra=`\n    <link rel="canonical" href="${esc(url)}">\n`;
 if(alternates) for(const l of ['ar','en']) extra+=`    <link rel="alternate" hreflang="${l}" href="${esc(alternates[l])}">\n`;
 head=head.replace(/<meta\b[^>]*>/gi,tag=> /\bproperty\s*=\s*["']og:(url|image)["']/i.test(tag)?migrate(tag):tag);
 head=head.replace(/<meta\b[^>]*property\s*=\s*["']og:url["'][^>]*>/gi,'');
 extra+=`    <meta property="og:url" content="${esc(url)}">\n`;
 let bookFound=false;
 head=head.replace(/<script\b([^>]*type\s*=\s*["']application\/ld\+json["'][^>]*)>([\s\S]*?)<\/script>/gi,(whole,attrs,body)=>{
  let data; try {data=JSON.parse(body);} catch {issues.push({file,issue:'Invalid existing JSON-LD; retained'});return whole;}
  function visit(value) {
   if(Array.isArray(value)) return value.map(visit);
   if(value&&typeof value==='object') {
    const primary=book && (value['@type']==='Book'||Array.isArray(value['@type'])&&value['@type'].includes('Book')) && !bookFound;
    if(primary) bookFound=true;
    const out=Object.fromEntries(Object.entries(value).map(([k,v])=>[k,visit(v)]));
    if(primary) {
     out.url=url; out['@id']=url+'#book'; out.inLanguage=lang;
     out.image=base+book[lang].cover.replace(/^.*\/books\//,'books/');
     if(!out.name) out.name=book.titles[lang];
     if(!out.description) out.description=book.description[lang];
     if(!out.author) out.author={'@type':'Person',name:lang==='ar'?'ناصر ابن داوود':'Nasser Ibn Dawood'};
     if(!out.license) issues.push({file,issue:'Missing license; requires author decision'});
     else if(!String(out.license).includes('/by-sa/4.0')) issues.push({file,issue:'License differs from catalog',license:out.license});
    }
    return out;
   }
   return typeof value==='string'?migrate(value):value;
  }
  return `<script${attrs}>\n${JSON.stringify(visit(data),null,2).replace(/</g,'\\u003c')}\n</script>`;
 });
 if(book&&!bookFound) {
  const data={'@context':'https://schema.org','@type':'Book','@id':url+'#book',url,name:book.titles[lang],description:book.description[lang],inLanguage:lang,author:{'@type':'Person',name:lang==='ar'?'ناصر ابن داوود':'Nasser Ibn Dawood'},image:base+book[lang].cover.replace(/^.*\/books\//,'books/')};
  extra+=`    <script type="application/ld+json">${JSON.stringify(data).replace(/</g,'\\u003c')}</script>\n`;
  issues.push({file,issue:'New Book metadata; license requires review'});
 }
 if(book&&!/<meta\b[^>]*name=["']description["']/i.test(head)) extra+=`    <meta name="description" content="${esc(book.description[lang])}">\n`;
 const next=original.replace(match[0],match[0].replace(match[1],(head+extra).replace(/[ \t]+(?=\r?$)/gm,'')));
 if(original.slice(original.indexOf('</head>'))!==next.slice(next.indexOf('</head>'))) throw Error('Body changed: '+file);
 changes.set(file,next);
}
for(const book of catalog) {
 const folders=Object.fromEntries(['ar','en'].map(lang=>[lang,book[lang].txt_direct.replace(/^.*\/books\//,'books/').replace(/content\.txt$/,'')]));
 const urls=Object.fromEntries(['ar','en'].map(lang=>[lang,base+folders[lang]]));
 for(const lang of ['ar','en']) {
  if(!exists(folders[lang]+'index.html')||!exists(book[lang].cover.replace(/^.*\/books\//,'books/'))) throw Error('Missing page/cover: '+book.id+lang);
  update(folders[lang]+'index.html',urls[lang],book,lang,urls);bookUrls.push(urls[lang]);
 }
}
const main=['index.html','books.html','books-index.html','arabic-books.html','english-books.html','search.html','ai-recommendations.html'];
const mainUrls=[];
for(const file of main) if(exists(file)){const url=base+(file==='index.html'?'':file);update(file,url);mainUrls.push(url);}
const xml=urls=>'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+urls.map(url=>`  <url><loc>${esc(url)}</loc></url>`).join('\n')+'\n</urlset>\n';
changes.set('sitemap.xml',xml([...mainUrls,...bookUrls]));
changes.set('sitemap-books.xml',xml(bookUrls));
changes.set('sitemap-bing.xml',xml([...mainUrls,...bookUrls]));
let robots=migrate(read('robots.txt')).replace(/^Sitemap: https:\/\/a520098.*\r?\n/gm,'').replace(/^Disallow: \/books\/\*\/cover-\*\.png\r?\n/gm,'').replace('32 كتاباً','69 كتابًا');
changes.set('robots.txt',robots);
if(process.argv.includes('--write')) for(const [file,text] of changes) fs.writeFileSync(path.join(root,file),text);
console.log(JSON.stringify({pages:bookUrls.length+mainUrls.length,books:catalog.length,sitemapUrls:bookUrls.length+mainUrls.length,issues},null,2));
