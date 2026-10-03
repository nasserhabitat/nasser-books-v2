"""Match local cover image names to catalogue references after an extension change."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
books=json.loads((ROOT/'ai-index.json').read_text(encoding='utf-8'))['books']
for b in books[69:]:
    for lang in ('ar','en'):
        page=ROOT/'books'/b['id']/lang/'index.html'
        text=page.read_text(encoding='utf-8');name=Path(b[lang]['cover']).name
        pattern=r'(\bsrc=")'+re.escape(b['id']+'-cover-'+lang)+r'\.(?:png|jpg|jpeg)(")'
        revised=re.sub(pattern,lambda m:m[1]+name+m[2],text)
        if revised!=text:page.write_text(revised,encoding='utf-8')
