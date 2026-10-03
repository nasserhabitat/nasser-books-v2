"""Read-only PDF/TXT integrity audit, with source hashes and page counts."""
import hashlib,json,re
from pathlib import Path
from pypdf import PdfReader
from prepare_book_migration import ROOT

SOURCE=Path(r'C:\Users\nasse\OneDrive\Documents\google_books')
books=json.loads((ROOT/'ai-index.json').read_text(encoding='utf-8'))['books'][69:]
export_report=SOURCE/'pdf-txt-export-report.json'
records=json.loads(export_report.read_text(encoding='utf-8-sig')) if export_report.exists() else []
results=[]
for b in books:
    for lang in ('ar','en'):
        stem=f'{b["book_number"]}-{b["id"]}-{lang}'
        folder=SOURCE/f'{b["book_number"]}-{b["id"]}'/lang
        pdf=folder/(stem+'.pdf');txt=folder/(stem+'.txt');entry={'number':b['book_number'],'id':b['id'],'language':lang,'pdf':str(pdf),'txt':str(txt)}
        expected=ROOT/'books'/b['id']/lang/(stem+'.txt')
        entry['txt_ready']=txt.exists() and txt.read_bytes()==expected.read_bytes()
        entry['pdf_ready']=False
        if pdf.exists():
            try:
                reader=PdfReader(pdf)
                entry.update(pdf_ready=len(reader.pages)>0 and not reader.is_encrypted,pages=len(reader.pages),bytes=pdf.stat().st_size)
                entry['sample_text_characters']=sum(len(reader.pages[i].extract_text() or '') for i in {0,min(1,len(reader.pages)-1),len(reader.pages)-1})
                entry['english_over_30_pages']=lang=='en' and len(reader.pages)>30
            except Exception as e:entry['pdf_error']=str(e)
        source_record=next((r for r in records if r['number']==b['book_number'] and r['language']==lang),None)
        if source_record:
            raw=Path(source_record['source']).read_bytes()
            entry['word_source_unchanged']=hashlib.sha256(raw).hexdigest().upper()==source_record['source_sha256'].upper()
        results.append(entry)
summary={'expected_editions':86,'txt_ready':sum(r['txt_ready'] for r in results),'pdf_ready':sum(r['pdf_ready'] for r in results),'pdf_errors':[r for r in results if 'pdf_error' in r],'english_over_30_pages':[{'number':r['number'],'pages':r['pages']} for r in results if r.get('english_over_30_pages')],'changed_word_sources':[r for r in results if r.get('word_source_unchanged') is False],'total_pages':sum(r.get('pages',0) for r in results),'source_cover_review':[{'number':70,'language':'ar','issue':'Supplied cover says الدين القيم while document title says الدين الخالص. Source retained.'}]}
(ROOT/'scripts/book-export-verification.json').write_text(json.dumps({'summary':summary,'editions':results},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
