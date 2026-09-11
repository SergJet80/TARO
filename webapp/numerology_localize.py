"""Localize the existing Russian numerology page; preserve its markup and scripts.

All translations are maintained in data/i18n/numerology.json.
"""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
import hashlib,json,re
import i18n_build
from check_i18n import strip_additions,check_pending

ROOT=Path(__file__).resolve().parent
REL='numerology/index.html'
DATA=ROOT/'data/i18n/numerology.json'

def translate(source):
    records=json.loads(DATA.read_text(encoding='utf-8'))['strings']
    mapping={p['ru']:p['en'] for p in records}
    if len(mapping)!=len(records) or any(not v.strip() for v in mapping.values()):raise ValueError('Missing or duplicate numerology translation')
    missing=[k for k in mapping if k not in source]
    if missing:raise ValueError(f'Russian source changed; update translation records: {missing}')
    pattern=re.compile('|'.join(re.escape(k) for k in sorted(mapping,key=len,reverse=True)))
    chunks=re.split(r'(<!--.*?-->|<(?:script|style)\b[^>]*>.*?</(?:script|style)>)',source,flags=re.S|re.I)
    return ''.join(s if re.match(r'<!--|<(?:script|style)\b',s,re.I) else pattern.sub(lambda m:escape(mapping[m.group()],quote=True),s) for s in chunks)

class Structure(HTMLParser):
    def __init__(self):super().__init__();self.body=False;self.tags=[];self.refs=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='body':self.body=True
        if self.body:self.tags.append((tag,tuple((k,v) for k,v in attrs if k not in ('href','src','aria-label','title','alt'))))
        for k in ('href','src'):
            if k in a:self.refs.append((tag,k,a[k]))
    def handle_endtag(self,tag):
        if self.body:self.tags.append(('/'+tag,()))

def check():
    from check_site import local_target
    errors=[]
    ru=strip_additions((ROOT/REL).read_text(encoding='utf-8'))
    en=strip_additions((ROOT/'en'/REL).read_text(encoding='utf-8'))
    a=Structure();a.feed(ru);b=Structure();b.feed(en)
    if a.tags!=b.tags:errors.append('Numerology: body structure or element attributes changed')
    scripts=lambda s:[body for attrs,body in re.findall(r'<script\b([^>]*)>(.*?)</script>',s,re.S) if 'application/ld+json' not in attrs]
    if scripts(ru)!=scripts(en):errors.append('Numerology: original interactive scripts changed')
    original_refs=[local_target(ROOT/REL,v) for tag,k,v in a.refs if tag!='link' or k=='href']
    en_refs=[local_target(ROOT/'en'/REL,v) for tag,k,v in b.refs if tag!='link' or k=='href']
    original_local=[p for p in original_refs if p is not None]
    en_local=[p for p in en_refs if p is not None]
    expected=[ROOT/'en'/REL if p==(ROOT/REL).resolve() else p for p in original_local]
    if expected!=en_local:errors.append('Numerology: local resources or RU section links changed')
    clean=re.sub(r'<!--.*?-->|<style\b[^>]*>.*?</style>','',en,flags=re.S)
    if re.search(r'post[ -]Soviet|esoteric (?:practice|schools)',clean,re.I):errors.append('Numerology: disallowed terminology')
    if 'Symbolism is not a diagnosis, a prediction, or financial advice.' not in en:errors.append('Numerology: required disclaimer missing')
    if not errors:print('OK numerology: source body structure, scripts and resources preserved; links to other sections target RU')
    return errors

def main():
    source=strip_additions((ROOT/REL).read_text(encoding='utf-8'))
    baseline=i18n_build.load_json('ru-baseline.json')['html'][REL]
    if hashlib.sha256(source.encode('utf-8')).hexdigest()!=baseline:raise ValueError('Russian numerology source differs from baseline')
    routes=i18n_build.load_json('routes.json')
    for route in routes:
        if route['ru_file']==REL:route['status']='ready'
    (ROOT/'data/i18n/routes.json').write_text(json.dumps(routes,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    i18n_build.load_json.cache_clear();i18n_build.ready_paths.cache_clear()
    pending={ROOT/REL:i18n_build.finalize(source,REL,'ru'),ROOT/'en'/REL:i18n_build.finalize(translate(source),REL,'en',template=True,english_disclaimer=False,other_sections_ru=True)}
    errors=check_pending(pending)
    if errors:raise ValueError('\n'.join(errors))
    for p,text in pending.items():p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8',newline='\n')
    i18n_build.update_sitemaps()
    errors=check()
    if errors:raise ValueError('\n'.join(errors))
    print('OK: numerology RU base + EN translation (1 page)')

if __name__=='__main__':main()
