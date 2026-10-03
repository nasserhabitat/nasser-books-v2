"""Connect verified public Drive PDFs to book pages; never host book binaries."""
import json,re
from html import escape
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
cat=json.loads((ROOT/'ai-index.json').read_text(encoding='utf-8'))
manifest=json.loads((ROOT/'scripts/new-pdf-drive-uploads.json').read_text(encoding='utf-8'))
uploaded={}
for f in manifest['files']:
    if not f.get('verified') or not f.get('public'):continue
    m=re.fullmatch(r'(\d+)-(.+)-(ar|en)\.pdf',f['file_name'])
    assert m and f['mime_type']=='application/pdf'
    uploaded[(int(m[1]),m[2],m[3])]=f
for b in cat['books']:
    for lang in ('ar','en'):
        f=uploaded.get((b['book_number'],b['id'],lang))
        if f:b[lang]['pdf_external']='https://drive.google.com/uc?export=download&id='+f['id']
(ROOT/'ai-index.json').write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
cloud={f['drive_id']:f for f in json.loads((ROOT/'scripts/monthly-sync-cloud-inventory.json').read_text(encoding='utf-8'))['files']}
memberships={fid:r for r in json.loads((ROOT/'scripts/monthly-sync-legacy-folders.json').read_text(encoding='utf-8')) for fid in r['file_ids']}
editions=[]
for b in cat['books']:
    for lang in ('ar','en'):
        url=b[lang].get('pdf_external','');m=re.search(r'[?&]id=([^&]+)',url);fid=m[1] if m else None
        f=uploaded.get((b['book_number'],b['id'],lang));info=cloud.get(fid);owner=memberships.get(fid)
        status='pending'
        if f:status='ready'
        elif fid:
            if not info or not info['accessible']:status='unavailable'
            elif info['mime_type']!='application/pdf':status='review'
            elif len({(u['number'],u['lang']) for u in info['uses']})>1:status='review'
            elif not owner or owner['number']!=b['book_number'] or owner['language']!=lang:status='review'
            elif not info['public']:status='private'
            else:status='ready'
        entry={'number':b['book_number'],'book_id':b['id'],'language':lang,'title':b['titles'][lang],'status':status}
        if status=='ready':entry['drive_id']=fid
        editions.append(entry)
        p=ROOT/'books'/b['id']/lang/'index.html';s=p.read_text(encoding='utf-8')
        s=re.sub(r'<!-- library-pdf-reader:start -->.*?<!-- library-pdf-reader:end -->\s*','',s,flags=re.S)
        s=re.sub(r'<!-- library-pdf-download:start -->.*?<!-- library-pdf-download:end -->\s*','',s,flags=re.S)
        if 'assets/pdf-reader.css' not in s:
            s=s.replace('</head>','<link rel="stylesheet" href="../../../assets/pdf-reader.css"><script defer src="../../../assets/pdf-reader.js"></script>\n</head>',1)
        fallback=('<p><a href="https://drive.google.com/file/d/'+fid+'/view" target="_blank" rel="noopener noreferrer">PDF — Google Drive</a></p>') if status=='ready' else '<p>PDF غير متاح للعرض العام حاليًا. / PDF is not currently available for public display.</p>'
        anchor='<footer' if '<footer' in s else '</body>'
        if anchor not in s:raise ValueError('No body insertion point: '+str(p))
        if f:
            s=s.replace(anchor,'<!-- library-pdf-download:start --><p><a href="'+escape(url,quote=True)+'" target="_blank" rel="noopener noreferrer">PDF — Google Drive</a></p><!-- library-pdf-download:end -->\n'+anchor,1)
        component='<!-- library-pdf-reader:start --><section id="pdf-reader" class="pdf-reader" data-pdf-reader="book" data-book-id="'+escape(b['id'],quote=True)+'" data-language="'+lang+'"><h2>'+('قراءة PDF داخل الموقع' if lang=='ar' else 'Read the PDF on this website')+'</h2><p>'+('جارٍ تجهيز القارئ…' if lang=='ar' else 'Preparing the reader…')+'</p><noscript>'+fallback+'</noscript></section><!-- library-pdf-reader:end -->\n'
        s=s.replace(anchor,component+anchor,1);p.write_text(s,encoding='utf-8')
summary={status:sum(e['status']==status for e in editions) for status in ('ready','pending','private','review','unavailable')}
# Refresh only the resource areas of new-book listings, preserving their prose.
for filename,language in [('arabic-books.html','ar'),('english-books.html','en')]:
    p=ROOT/filename;s=p.read_text(encoding='utf-8')
    for b in cat['books']:
        if b['book_number']<70:continue
        url=b[language].get('pdf_external')
        if not url:continue
        pattern=r'(<article class="book-card"[^>]*>.*?href="books/'+re.escape(b['id'])+'/'+language+r'/".*?<div class="download-links">)(.*?)(</div></div></article>)'
        def refresh(m):
            resources=re.sub(r'\s*<a\b[^>]*>PDF — Google Drive</a>','',m[2])
            return m[1]+resources+' <a href="'+escape(url,quote=True)+'" target="_blank" rel="noopener noreferrer">PDF — Google Drive</a>'+m[3]
        # Do not allow the match to start in another book card.
        pattern=pattern.replace('.*?',r'(?:(?!</article>).)*?')
        s,count=re.subn(pattern,refresh,s,flags=re.S);assert count==1,(filename,b['id'],count)
    p.write_text(s,encoding='utf-8')
p=ROOT/'books.html';s=p.read_text(encoding='utf-8')
for b in cat['books']:
    if b['book_number']<70:continue
    pattern=r'(<div class="book"><h2>'+str(b['book_number'])+r'\. .*?</div>)'
    def refresh_book(m):
        block=m[1]
        for lang,label in [('ar','العربية'),('en','English')]:
            url=b[lang].get('pdf_external')
            if not url:continue
            def refresh_paragraph(n):
                resources=re.sub(r'\s*<a\b[^>]*>PDF — Google Drive</a>','',n[1])
                return resources+' <a href="'+escape(url,quote=True)+'" target="_blank" rel="noopener noreferrer">PDF — Google Drive</a></p>'
            block,count=re.subn(r'(<p>'+label+r': .*?)</p>',refresh_paragraph,block,flags=re.S);assert count==1
        return block
    s,count=re.subn(pattern,refresh_book,s,flags=re.S);assert count==1,(b['id'],count)
p.write_text(s,encoding='utf-8')
(ROOT/'assets/pdf-reader-catalog.json').write_text(json.dumps({'updated_at':'2026-10-03','summary':summary,'editions':editions},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=ROOT/'index.html';s=p.read_text(encoding='utf-8')
s=re.sub(r'<!-- library-pdf-entry:start -->.*?<!-- library-pdf-entry:end -->\s*','',s,flags=re.S)
section='<!-- library-pdf-entry:start --><section id="pdf-library-entry"><h2>قراءة PDF داخل الموقع — Read PDFs online</h2><p>ملفات PDF على Google Drive؛ البحث النصي والأغلفة داخل الموقع.</p><a href="reader.html">فتح قارئ PDF لجميع الكتب — Open the PDF reader</a></section><!-- library-pdf-entry:end -->\n'
assert '</main>' in s;s=s.replace('</main>',section+'</main>',1)
s=s.replace('(PDF, HTML, TXT, DOCX)','(PDF, TXT, DOCX)').replace('(PDF - HTML - TXT - DOCX)','(PDF - TXT - DOCX)').replace('(PDF – HTML – TXT – DOCX)','(PDF – TXT – DOCX)').replace('بأربعة تنسيقات أساسية','بثلاثة تنسيقات أساسية').replace('in four key formats','in three key formats')
p.write_text(s,encoding='utf-8')
print(json.dumps({'pages_updated':224,'new_pdfs_linked':len(uploaded),'reader_statuses':summary},ensure_ascii=False))
