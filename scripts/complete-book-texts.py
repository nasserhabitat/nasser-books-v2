"""Faithful text export including Word equations and footnote/endnote text."""
import argparse,json,zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from prepare_book_migration import ROOT,W
M='{http://schemas.openxmlformats.org/officeDocument/2006/math}'
SOURCE=Path(r'C:\Users\nasse\OneDrive\Documents\google_books')
def math_text(node):
    tag=node.tag.removeprefix(M)
    if tag=='t':return node.text or ''
    if tag.endswith('Pr'):return ''
    def part(name):
        child=node.find(M+name)
        return math_text(child) if child is not None else ''
    if tag=='f':return '('+part('num')+')/('+part('den')+')'
    if tag=='sSup':return part('e')+'^('+part('sup')+')'
    if tag=='sSub':return part('e')+'_('+part('sub')+')'
    if tag=='sSubSup':return part('e')+'_('+part('sub')+')^('+part('sup')+')'
    if tag=='rad':return ('root('+part('deg')+', '+part('e')+')') if part('deg') else 'sqrt('+part('e')+')'
    if tag=='func':return part('fName')+'('+part('e')+')'
    if tag in ('limLow','limUpp'):return part('e')+('_' if tag=='limLow' else '^')+'('+part('lim')+')'
    if tag=='d':
        props=node.find(M+'dPr');beg='(';end=')'
        if props is not None:
            x=props.find(M+'begChr');y=props.find(M+'endChr')
            if x is not None:beg=x.get(M+'val','')
            if y is not None:end=y.get(M+'val','')
        return beg+', '.join(math_text(x) for x in node.findall(M+'e'))+end
    if tag=='nary':
        prop=node.find(M+'naryPr/'+M+'chr');char=prop.get(M+'val','∫') if prop is not None else '∫'
        return char+('_('+part('sub')+')' if part('sub') else '')+('^('+part('sup')+')' if part('sup') else '')+' '+part('e')
    return ''.join(math_text(child) for child in node)
def visible(node):
    if node.tag==W+'del' or node.tag==W+'instrText':return ''
    if node.tag==W+'t':return node.text or ''
    if node.tag in (W+'br',W+'cr'):return '\n'
    if node.tag==W+'tab':return '\t'
    if node.tag in (M+'oMath',M+'oMathPara'):return math_text(node)
    if node.tag in (W+'footnoteReference',W+'endnoteReference'):
        kind='حاشية' if node.tag==W+'footnoteReference' else 'هامش ختامي'
        return ' ['+kind+' '+node.get(W+'id','')+'] '
    return ''.join(visible(c) for c in node)
def extract(path):
    with zipfile.ZipFile(path) as z:
        doc=ET.fromstring(z.read('word/document.xml'))
        lines=[visible(p).strip() for p in doc.iter(W+'p')]
        notes=0;equations=len(list(doc.iter(M+'oMath')))
        for filename,kind in [('word/footnotes.xml','footnote'),('word/endnotes.xml','endnote')]:
            if filename not in z.namelist():continue
            tree=ET.fromstring(z.read(filename));sections=[]
            for note in tree.findall(W+kind):
                if note.get(W+'type') in ('separator','continuationSeparator') or int(note.get(W+'id','0'))<=0:continue
                text='\n'.join(visible(p).strip() for p in note.iter(W+'p')).strip()
                if text:sections.append('['+('حاشية' if kind=='footnote' else 'هامش ختامي')+' '+note.get(W+'id','')+'] '+text);notes+=1
            if sections:lines+=['','الحواشي' if kind=='footnote' else 'الهوامش الختامية']+sections
        return '\n'.join(line for line in lines if line.strip())+'\n',notes,equations
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');args=ap.parse_args()
    books=json.loads((ROOT/'ai-index.json').read_text(encoding='utf-8'))['books'][69:];rows=[]
    for b in books:
        for lang in ('ar','en'):
            stem=f'{b["book_number"]}-{b["id"]}-{lang}';folder=SOURCE/f'{b["book_number"]}-{b["id"]}'/lang
            doc=next(p for p in folder.glob('*.docx') if not p.name.startswith('~$'));text,notes,equations=extract(doc)
            site=ROOT/'books'/b['id']/lang/(stem+'.txt');changed=text!=site.read_text(encoding='utf-8')
            rows.append({'number':b['book_number'],'language':lang,'notes':notes,'equations':equations,'text_enriched':changed})
            if args.apply:
                site.write_text(text,encoding='utf-8');(folder/(stem+'.txt')).write_text(text,encoding='utf-8')
    (ROOT/'scripts/full-text-export-report.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'editions':len(rows),'enriched_texts':sum(r['text_enriched'] for r in rows),'notes':sum(r['notes'] for r in rows),'equations':sum(r['equations'] for r in rows)},ensure_ascii=False))
if __name__=='__main__':main()
