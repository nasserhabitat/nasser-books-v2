"""Mechanical URL casing and whitespace cleanup; never modifies manuscript text."""
import json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
books=json.loads((ROOT/'ai-index.json').read_text(encoding='utf-8'))['books']
changed=set(subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True,encoding='utf-8').splitlines())
for p in ROOT.rglob('*'):
    if not p.is_file() or any(x in ('.git','scripts','content.files') for x in p.relative_to(ROOT).parts):continue
    if p.suffix not in ('.html','.json','.js','.xml','.md'):continue
    rel=p.relative_to(ROOT).as_posix();s=p.read_text(encoding='utf-8-sig');old=s
    for b in books:
        s=re.sub(re.escape('books/'+b['id']+'/'),lambda _: 'books/'+b['id']+'/',s,flags=re.I)
        for lang in ('ar','en'):
            prefix='books/'+b['id']+'/'+lang+'/'
            s=s.replace(prefix+'content.txt',prefix+f'{b["book_number"]}-{b["id"]}-{lang}.txt')
            s=s.replace(prefix+f'cover-{lang}.png',prefix+f'{b["id"]}-cover-{lang}.png')
    if rel.casefold() in {v.casefold() for v in changed}:s=re.sub(r'[ \t]+$', '',s,flags=re.M)
    if s!=old:p.write_text(s,encoding='utf-8')
