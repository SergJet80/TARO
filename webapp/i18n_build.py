"""Shared bilingual static rendering. Python standard library; no network access."""
from __future__ import annotations
from pathlib import Path
from html import escape, unescape
from html.parser import HTMLParser
from urllib.parse import urlsplit, urlunsplit, unquote
import json, posixpath, re
from functools import lru_cache

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'/'i18n'
SITE='https://taro.jetserg.top'
MANIFEST=DATA/'routes.json'

@lru_cache(maxsize=None)
def load_json(name):
    return json.loads((DATA/name).read_text(encoding='utf-8'))

def select(value, lang):
    if lang not in ('ru','en'): raise ValueError(f'Unsupported language: {lang}')
    if isinstance(value,dict):
        if set(value)=={'ru','en'}:
            result=value[lang]
            if not isinstance(result,str) or not result.strip():
                raise ValueError(f'Missing {lang} translation: {value["ru"][:100]}')
            return result
        return {k:select(v,lang) for k,v in value.items()}
    if isinstance(value,list): return [select(v,lang) for v in value]
    return value

def route_url(path):
    return SITE+'/'+path.removesuffix('index.html') if path.endswith('index.html') else SITE+'/'+path

@lru_cache(maxsize=None)
def ready_paths():
    return {r['ru_file'] for r in load_json('routes.json') if r['status']=='ready'}

def translate_ui(text, *mapping_files):
    if not mapping_files:
        mapping_files=('lenormand-ui.json',)
    mapping={}
    for mapping_file in mapping_files:
        mapping.update({p['ru']:p['en'] for p in load_json(mapping_file)})
    # One pass avoids interpreting English output as another translation key.
    pattern=re.compile('|'.join(re.escape(s) for s in sorted(mapping,key=len,reverse=True)))
    # Comments and styles are not language content.
    chunks=re.split(r'(<!--.*?-->|<style\b[^>]*>.*?</style>)',text,flags=re.S|re.I)
    return ''.join(chunk if re.match(r'<!--|<style\b',chunk,re.I) else pattern.sub(lambda m:mapping[m.group()],chunk) for chunk in chunks)

def render_template(name,lang):
    template=(ROOT/'templates'/f'{name}.html.tmpl').read_text(encoding='utf-8')
    content=load_json(f'{name}.json')
    return re.sub(r'@@(g\d+)@@',lambda m:select(content[m[1]],lang),template)

class Head(HTMLParser):
    def __init__(self):
        super().__init__(); self.title=''; self.description=''; self.in_title=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='title': self.in_title=True
        if tag=='meta' and a.get('name')=='description': self.description=a.get('content','')
    def handle_endtag(self,tag):
        if tag=='title': self.in_title=False
    def handle_data(self,s):
        if self.in_title:self.title+=s

def english_refs(text,ru_path):
    available=ready_paths()
    en_path='en/'+ru_path
    def replace(m):
        reference=unescape(m['url'])
        parts=urlsplit(reference)
        if parts.scheme or parts.netloc or not parts.path or reference.startswith('//') or '${' in reference:
            return m.group()
        old=posixpath.normpath(posixpath.join(posixpath.dirname(ru_path),unquote(parts.path)))
        if parts.path.startswith('/'): old=parts.path.lstrip('/')
        if (ROOT/old).is_dir():old=old.rstrip('/')+'/index.html'
        target='en/'+old if old in available else old
        local=posixpath.relpath(target,posixpath.dirname(en_path))
        result=urlunsplit(('', '', local,parts.query,parts.fragment))
        return m['prefix']+escape(result,quote=True)+m['quote']
    return re.sub(r'''(?P<prefix>\b(?:href|src)\s*=\s*(?P<quote>["']))(?P<url>.*?)(?P=quote)''',replace,text,flags=re.I)

def add_seo(text,ru_path,lang):
    ru_url=route_url(ru_path); en_url=route_url('en/'+ru_path)
    if lang=='en':
        text=re.sub(r'(<html\b[^>]*\blang=)["\'][^"\']*["\']',r'\1"en"',text,count=1,flags=re.I)
        text=text.replace(ru_url,en_url)
        text=re.sub(r'(<link\b[^>]*\brel=["\']canonical["\'][^>]*>)','',text,flags=re.I)
        text=text.replace('</head>',f'<link rel="canonical" href="{en_url}">\n</head>',1)
        text=text.replace('"inLanguage": "ru"','"inLanguage": "en"')
        h=Head();h.feed(text)
        additions=[]
        for property_,value in [('og:title',h.title),('og:description',h.description),('og:url',en_url),('og:type','website')]:
            if not re.search(r'property=["\']'+re.escape(property_)+r'["\']',text):
                additions.append(f'<meta property="{property_}" content="{escape(value,quote=True)}">')
        if 'application/ld+json' not in text:
            schema={'@context':'https://schema.org','@type':'Article','headline':h.title,'description':h.description,'url':en_url,'inLanguage':'en'}
            additions.append('<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('<','\\u003c')+'</script>')
        text=text.replace('</head>','\n'.join(additions)+'\n</head>',1)
    # Marker block makes the only permitted RU additions easy to verify.
    links='\n'.join(f'<link rel="alternate" hreflang="{code}" href="{url}">' for code,url in [('ru',ru_url),('en',en_url),('x-default',ru_url)])
    text=text.replace('</head>','<!-- i18n:seo -->\n'+links+'\n<!-- /i18n:seo -->\n</head>',1)
    return text

def finalize(text,ru_path,lang,template=False,english_disclaimer=True):
    if lang=='en':
        if not template: text=translate_ui(text)
        text=english_refs(text,ru_path)
        # Localisation of a string argument; the trainer algorithm is unchanged.
        text=text.replace("toLocaleLowerCase('ru')","toLocaleLowerCase('en')")
        kofi='<a href="https://ko-fi.com/jetjarret" target="_blank" rel="noopener" class="fc-donate-btn">♥ Ko-fi</a>\n'
        text=re.sub(r'(<div class="(?:fc-links fc-donate|about-donate)">)',lambda m:m.group()+'\n'+kofi,text)
        text=re.sub(r'(<a\b[^>]*href="https://(?:donatello\.to|www\.privat24\.ua)/[^>]*>)(.*?)(</a>)',r'\1\2 (UA-friendly)\3',text)
        if english_disclaimer:
            disclaimer='<p class="ln-note">For reference, reflection and entertainment. Card readings do not establish facts, diagnose illness or predict an inevitable future. This is not medical, legal, financial or investment advice; seek qualified help for decisions in those areas.</p>'
            text=text.replace('<footer class="site-footer">','<footer class="site-footer">\n'+disclaimer,1)
    text=add_seo(text,ru_path,lang)
    page=ru_path if lang=='ru' else 'en/'+ru_path
    target='en/'+ru_path if lang=='ru' else ru_path
    href=posixpath.relpath(target,posixpath.dirname(page))
    other='en' if lang=='ru' else 'ru'
    label='EN | RU' if lang=='ru' else 'RU | EN'
    switch=f'<!-- i18n:switch --><a class="mn-language" href="{href}" hreflang="{other}" lang="{other}" aria-label="{("Switch to English" if lang=="ru" else "Switch to Russian")}" style="color:var(--ln-accent,var(--gold));border:1px solid var(--ln-accent-dim,var(--gold));border-radius:6px;padding:6px 10px;white-space:nowrap">{label}</a><!-- /i18n:switch -->'
    nav=re.search(r'<nav class="main-nav"\b[^>]*>.*?</nav>',text,re.S)
    if not nav: # \b after the closing quote is not a word boundary.
        nav=re.search(r'<nav class="main-nav"[^>]*>.*?</nav>',text,re.S)
    if not nav:raise ValueError(f'{page}: main-nav missing')
    new_nav=nav.group().replace('</div>',switch+'</div>',1)
    return text[:nav.start()]+new_nav+text[nav.end():]

def update_sitemaps():
    import xml.etree.ElementTree as ET
    ns='http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('',ns)
    original=ROOT/'sitemap.xml'
    tree=ET.parse(original); root=tree.getroot()
    ready_en={route_url('en/'+path) for path in ready_paths()}
    for entry in list(root.findall(f'{{{ns}}}url')):
        loc=entry.find(f'{{{ns}}}loc')
        if loc is not None and loc.text and '/en/' in loc.text and loc.text not in ready_en:
            root.remove(entry)
    existing={e.text for e in root.findall(f'{{{ns}}}url/{{{ns}}}loc')}
    enroot=ET.Element(f'{{{ns}}}urlset')
    for path in sorted(ready_paths()):
        url=route_url('en/'+path)
        entry=ET.SubElement(enroot,f'{{{ns}}}url')
        ET.SubElement(entry,f'{{{ns}}}loc').text=url
        if url not in existing:
            entry=ET.SubElement(root,f'{{{ns}}}url')
            ET.SubElement(entry,f'{{{ns}}}loc').text=url
    tree.write(original,encoding='utf-8',xml_declaration=True)
    ET.ElementTree(enroot).write(ROOT/'en'/'sitemap.xml',encoding='utf-8',xml_declaration=True)
