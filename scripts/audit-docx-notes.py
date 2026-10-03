"""Check whether full-text exports need footnotes/endnotes or equation text."""
import json,zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from prepare_book_migration import ROOT,W
source=Path(r'C:\Users\nasse\OneDrive\Documents\google_books')
cat=json.loads((ROOT/'ai-index.json').read_text(encoding='utf-8'))['books'][69:]
findings=[]
for b in cat:
 for lang in ('ar','en'):
  folder=source/f'{b["book_number"]}-{b["id"]}'/lang
  files=[p for p in folder.glob('*.docx') if not p.name.startswith('~$')]
  with zipfile.ZipFile(files[0]) as z:
   notes=[]
   for name in ('word/footnotes.xml','word/endnotes.xml'):
    if name not in z.namelist():continue
    tree=ET.fromstring(z.read(name))
    text=' '.join(t.text or '' for t in tree.iter(W+'t'))
    if text.strip():notes.append({'part':name,'characters':len(text),'sample':text[:120]})
   tree=ET.fromstring(z.read('word/document.xml'));equations=list(tree.iter('{http://schemas.openxmlformats.org/officeDocument/2006/math}t'))
   if notes or equations:findings.append({'number':b['book_number'],'language':lang,'notes':notes,'equation_text_nodes':len(equations)})
print(json.dumps(findings,ensure_ascii=False,indent=2))
