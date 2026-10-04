"""Sort Arabic or English book cards without rewriting their contents or links."""
import json,re,sys
from pathlib import Path
from html.parser import HTMLParser
root=Path(r'C:\Users\nasse\OneDrive\Documents\GitHub\nasser-books')
if '--root' in sys.argv:root=Path(sys.argv[sys.argv.index('--root')+1])
language=sys.argv[sys.argv.index('--language')+1] if '--language' in sys.argv else 'ar'
assert language in ('ar','en')
page=root/('arabic-books.html' if language=='ar' else 'english-books.html')
raw=page.read_text(encoding='utf-8-sig')
offsets=[0]
for line in raw.splitlines(keepends=True):offsets.append(offsets[-1]+len(line))
class Cards(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=False);self.active=None;self.depth=0;self.cards=[]
    def position(self):line,column=self.getpos();return offsets[line-1]+column
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if self.active:
            if tag==self.active[0]:self.depth+=1
        elif tag in ('div','article') and 'book-card' in attrs.get('class','').split():
            self.active=(tag,self.position());self.depth=1
    def handle_endtag(self,tag):
        if self.active and tag==self.active[0]:
            self.depth-=1
            if not self.depth:
                begin=self.active[1];end=raw.index('>',self.position())+1
                self.cards.append((begin,end,raw[begin:end]));self.active=None
parser=Cards();parser.feed(raw)
catalog=json.loads((root/'ai-index.json').read_text(encoding='utf-8-sig'))['books']
numbers={b['id'].lower():b['book_number'] for b in catalog}
assert len(parser.cards)==len(catalog)==112
items=[]
for begin,end,card in parser.cards:
    match=re.search(r'books/([^/]+)/'+language+'/',card)
    assert match,card[:100]
    items.append((numbers[match[1].lower()],card))
assert sorted(n for n,_ in items)==list(range(1,113))
first=parser.cards[0][0];last=parser.cards[-1][1]
section_end=raw.index('</section>',last)
gaps=''.join(raw[a[1]:b[0]] for a,b in zip(parser.cards,parser.cards[1:]))+raw[last:section_end]
unrecognized=re.sub(r'<!--.*?-->|</div>|\s','',gaps,flags=re.S)
assert not unrecognized,('Unexpected non-card content',unrecognized[:300])
prefix=re.sub(r'<!--\s*(?:الكتاب|Book)\s+1\s*:.*?-->\s*$','',raw[:first],flags=re.S|re.I)
assert prefix.rstrip().endswith('<div class="book-grid">')
ordered=sorted(items,reverse=True)
updated=prefix+'\n'+ '\n\n'.join(card for _,card in ordered)+'\n</div>\n'+raw[section_end:]
assert len(re.findall(r'class="book-card"',updated))==112
assert sorted(re.findall(r'href\s*=\s*["\']([^"\']+)',raw))==sorted(re.findall(r'href\s*=\s*["\']([^"\']+)',updated))
if '--apply' in sys.argv:page.write_text(updated,encoding='utf-8')
print(json.dumps({'cards':112,'order':[n for n,_ in ordered],'links_unchanged':True,'applied':'--apply' in sys.argv}))
