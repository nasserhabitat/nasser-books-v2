"""Inspect new sources and map existing Drive objects without changing them."""
import csv, json, re, unicodedata, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(r'C:\Users\nasse\OneDrive\Documents\google_books')
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
def paragraphs(path):
    with zipfile.ZipFile(path) as z:
        doc = ET.fromstring(z.read('word/document.xml'))
    # Only actual text nodes, never XML properties, deleted text or field code.
    lines = []
    for p in doc.iter(W+'p'):
        for deleted in list(p.iter(W+'del')):
            for t in deleted.iter(W+'t'):
                t.text = ''
        parts=[]
        for node in p.iter():
            if node.tag==W+'t':parts.append(node.text or '')
            elif node.tag==W+'tab':parts.append('\t')
            elif node.tag in (W+'br',W+'cr'):parts.append('\n')
        text = ''.join(parts).strip()
        if text:
            lines.append(text)
    return lines
def norm(s):
    return re.sub(r'[\W_]+', '', unicodedata.normalize('NFKC',s).casefold())
def main():
    rows=list(csv.DictReader((SOURCE/'books-manifest.csv').open(encoding='utf-8-sig')))
    tree=json.loads((ROOT/'scripts/drive-new-books.json').read_text(encoding='utf-8'))
    drive=[f for folder in tree for f in folder['files'].get('files',[]) if f['mime_type']!='application/vnd.google-apps.folder']
    entries=[]
    for row in rows:
        lines=paragraphs(SOURCE/row['organized_path'])
        name=Path(row['source_file']).stem
        match=[f for f in drive if norm(f['title'])==norm(name+'.docx')]
        with zipfile.ZipFile(SOURCE/row['organized_path']) as z:
            media=[n for n in z.namelist() if n.startswith('word/media/') and n.endswith('.png')]
        entries.append({**row,'first_lines':lines[:6],'characters':sum(map(len,lines)),
                        'drive_matches':[{'id':f['id'],'title':f['title'],'url':f['url']} for f in match],
                        'png_count':len(media)})
    (ROOT/'scripts/new-books-plan.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for e in entries:
        print(e['number'],e['language'],json.dumps(e['first_lines'][:3],ensure_ascii=False),'drive',len(e['drive_matches']),'png',e['png_count'])
if __name__=='__main__':main()
