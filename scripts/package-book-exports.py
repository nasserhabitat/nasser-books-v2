"""Package only validated PDF/TXT exports, never Word sources or website files."""
import hashlib,json,zipfile
from pathlib import Path
from pypdf import PdfReader
from prepare_book_migration import ROOT
SOURCE=Path(r'C:\Users\nasse\OneDrive\Documents\google_books')
OUTPUT=SOURCE/'pdf_txt_70-112.zip'
cat=json.loads((ROOT/'ai-index.json').read_text(encoding='utf-8'))['books'][69:]
inputs=[]
for b in cat:
    for lang in ('ar','en'):
        stem=f'{b["book_number"]}-{b["id"]}-{lang}';folder=SOURCE/f'{b["book_number"]}-{b["id"]}'/lang
        for ext in ('pdf','txt'):
            path=folder/(stem+'.'+ext)
            assert path.exists() and path.stat().st_size>0,str(path)
            if ext=='pdf':assert len(PdfReader(path).pages)>0,str(path)
            else:
                expected=ROOT/'books'/b['id']/lang/path.name
                assert path.read_bytes()==expected.read_bytes(),str(path)
            inputs.append(path)
assert len(inputs)==172
if OUTPUT.exists():raise SystemExit('Existing export archive retained; choose a new destination rather than overwrite.')
with zipfile.ZipFile(OUTPUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in inputs:z.write(p,p.relative_to(SOURCE).as_posix())
    summary=json.loads((ROOT/'scripts/book-export-verification.json').read_text(encoding='utf-8'))
    z.writestr('EXPORT_VERIFICATION.json',json.dumps(summary,ensure_ascii=False,indent=2))
with zipfile.ZipFile(OUTPUT) as z:
    bad=z.testzip();assert bad is None,bad
    pdfs=sum(n.endswith('.pdf') for n in z.namelist());texts=sum(n.endswith('.txt') for n in z.namelist())
assert pdfs==86 and texts==86
print(json.dumps({'archive':str(OUTPUT),'pdf_files':pdfs,'txt_files':texts,'bytes':OUTPUT.stat().st_size,'crc_check':'passed'},ensure_ascii=False))
