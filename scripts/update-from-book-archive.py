"""Compare/update new website editions from a user-supplied ZIP; never writes sources."""
import argparse,hashlib,io,json,re,zipfile,importlib.util
from pathlib import Path,PurePosixPath
from prepare_book_migration import ROOT,paragraphs

ARCHIVE=Path(r'C:\Users\nasse\OneDrive\Documents\google_books\incoming_70-112.zip')
def digest(raw):return hashlib.sha256(raw).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');args=ap.parse_args()
    cat=json.loads((ROOT/'ai-index.json').read_text(encoding='utf-8'))
    rows=[];issues=[]
    with zipfile.ZipFile(ARCHIVE) as archive:
        for book in cat['books'][69:]:
            for lang in ('ar','en'):
                prefix=f'incoming_70-112/{book["book_number"]}-{book["id"]}/{lang}/'
                names=[i.filename for i in archive.infolist() if i.filename.startswith(prefix) and '/' not in i.filename[len(prefix):] and not i.is_dir()]
                docs=[n for n in names if n.lower().endswith('.docx') and not PurePosixPath(n).name.startswith('~$')]
                images=[n for n in names if PurePosixPath(n).suffix.lower() in ('.png','.jpg','.jpeg')]
                explicit=[n for n in images if PurePosixPath(n).stem==f'{book["book_number"]}-{book["id"]}-{lang}-cover']
                if len(explicit)==1:images=explicit
                if len(docs)!=1 or len(images)!=1:
                    issues.append({'number':book['book_number'],'id':book['id'],'language':lang,'documents':docs,'images':images});continue
                raw=archive.read(docs[0]);lines=paragraphs(io.BytesIO(raw));text='\n'.join(lines)+'\n'
                sample='\n'.join(lines[:30]);arabic=len(re.findall(r'[\u0600-\u06ff]',sample));latin=len(re.findall(r'[A-Za-z]',sample))
                suspect=(lang=='en' and arabic>latin*2) or (lang=='ar' and latin>arabic*2)
                cover_raw=archive.read(images[0]);current_cover=ROOT/book[lang]['cover'] if book[lang].get('cover') else None
                row={'number':book['book_number'],'id':book['id'],'language':lang,'document':docs[0],'cover_source':images[0],'first_lines':lines[:4],'characters':len(text),'suspect_language':suspect,'text_changed':text!=(ROOT/book[lang]['txt_direct'].split('/nasser-books-v2/')[1]).read_text(encoding='utf-8'),'source_sha256':digest(raw),'cover_sha256':digest(cover_raw),'cover_changed':not current_cover or not current_cover.exists() or digest(current_cover.read_bytes())!=digest(cover_raw)}
                rows.append(row)
        report={'archive':str(ARCHIVE),'editions':rows,'issues':issues}
        (ROOT/'scripts/updated-archive-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'editions':len(rows),'changed_texts':sum(r['text_changed'] for r in rows),'suspect_language':[r for r in rows if r['suspect_language']],'issues':issues,'misnamed_documents':[{'number':r['number'],'language':r['language'],'file':r['document']} for r in rows if PurePosixPath(r['document']).name!=f'{r["number"]}-{r["id"]}-{r["language"]}.docx']},ensure_ascii=False,indent=2))
    if args.apply:
        assert len(rows)==86 and not issues and not any(r['suspect_language'] for r in rows),'Incomplete/ambiguous archive; no writes applied.'
        old_drive={(b['id'],l):{k:v for k,v in b[l].items() if isinstance(v,str) and 'drive.google.com' in v} for b in cat['books'] for l in ('ar','en')}
        replacements={};added=[]
        with zipfile.ZipFile(ARCHIVE) as archive:
            for row in rows:
                b=next(b for b in cat['books'] if b['id']==row['id']);lang=row['language'];folder=ROOT/'books'/b['id']/lang
                suffix=PurePosixPath(row['cover_source']).suffix.lower();suffix='.jpg' if suffix=='.jpeg' else suffix
                raw=archive.read(row['cover_source'])
                assert (suffix=='.png' and raw.startswith(b'\x89PNG\r\n\x1a\n')) or (suffix=='.jpg' and raw.startswith(b'\xff\xd8')),'Incorrect image format: '+row['cover_source']
                name=f'{b["id"]}-cover-{lang}{suffix}';rel=f'books/{b["id"]}/{lang}/{name}'
                old=b[lang].get('cover')
                if old and old!=rel:replacements[old]=rel
                (folder/name).write_bytes(raw);b[lang]['cover']=rel
                if old and old!=rel:
                    p=folder/'index.html';page=p.read_text(encoding='utf-8')
                    page=page.replace('src="'+PurePosixPath(old).name+'"','src="'+name+'"')
                    p.write_text(page,encoding='utf-8')
                if not old:added.append((b,lang))
                # TXT only changes if the new manuscript actually changed.
                if row['text_changed']:
                    text='\n'.join(paragraphs(io.BytesIO(archive.read(row['document']))))+'\n'
                    target=ROOT/b[lang]['txt_direct'].split('/nasser-books-v2/')[1];target.write_text(text,encoding='utf-8')
            for b in cat['books'][69:]:b['cover_image']='https://nasserhabitat.github.io/nasser-books-v2/'+b['ar']['cover']
        for p in ROOT.rglob('*'):
            if not p.is_file() or p.suffix not in ('.html','.json','.md') or any(s in ('.git','scripts') for s in p.relative_to(ROOT).parts):continue
            s=p.read_text(encoding='utf-8-sig');before=s
            for old,new in replacements.items():s=s.replace(old,new)
            if s!=before:p.write_text(s,encoding='utf-8')
        # Publish all cover references consistently, while retaining the existing catalogue metadata and Drive IDs.
        (ROOT/'ai-index.json').write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        search=json.loads((ROOT/'search-index.json').read_text(encoding='utf-8'))
        for s in search['books']:
            b=next(b for b in cat['books'] if b['id']==s['id'])
            for lang in ('ar','en'):
                if b[lang].get('cover'):s['links'][lang]['cover']=b[lang]['cover']
        (ROOT/'search-index.json').write_text(json.dumps(search,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        p=ROOT/'search.html';s=p.read_text(encoding='utf-8')
        s=re.sub(r'const booksData\s*=\s*\[.*?\];',lambda _:'const booksData = '+json.dumps(search['books'],ensure_ascii=False,indent=2)+';',s,count=1,flags=re.S);p.write_text(s,encoding='utf-8')
        for b,lang in added:
            p=ROOT/'books'/b['id']/lang/'index.html';s=p.read_text(encoding='utf-8')
            img=f'<img style="max-width:360px;width:100%" src="{PurePosixPath(b[lang]["cover"]).name}" alt="Cover" loading="lazy">'
            s=s.replace('</h1>','</h1>'+img,1);p.write_text(s,encoding='utf-8')
        # Regenerate just the newly inserted cards so formerly missing images are shown too.
        spec=importlib.util.spec_from_file_location('migration_helpers',ROOT/'scripts/migrate-books.py');helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers)
        for lang,filename in [('ar','arabic-books.html'),('en','english-books.html')]:
            p=ROOT/filename;s=p.read_text(encoding='utf-8');marker='<!-- New books 70–112 -->';start=s.index(marker)+len(marker);end=s.index('</section>',start)
            s=s[:start]+'\n'+''.join(helpers.listing(b,lang) for b in cat['books'][69:])+s[end:];p.write_text(s,encoding='utf-8')
        assert old_drive=={(b['id'],l):{k:v for k,v in b[l].items() if isinstance(v,str) and 'drive.google.com' in v} for b in cat['books'] for l in ('ar','en')},'Drive links changed unexpectedly'
        p=ROOT/'scripts/migration-report.json';report=json.loads(p.read_text(encoding='utf-8'));report['missing_covers']=[];report['latest_source_archive']=str(ARCHIVE);report['cover_refresh']={'provided_covers':86,'changed_covers':sum(r['cover_changed'] for r in rows),'changed_texts':sum(r['text_changed'] for r in rows),'newly_available_covers':len(added),'png':sum(PurePosixPath(r['cover_source']).suffix.lower()=='.png' for r in rows),'jpg':sum(PurePosixPath(r['cover_source']).suffix.lower() in ('.jpg','.jpeg') for r in rows),'source_naming_warning':'104/en contains a DOCX named ar, but its text and cover are English; source preserved.'};p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(report['cover_refresh'],ensure_ascii=False,indent=2))
if __name__=='__main__':main()
