"""Offline bilingual completeness, SEO and Russian preservation checks."""
from pathlib import Path
from html.parser import HTMLParser
from html import unescape
import hashlib, json, re
import os, shutil, subprocess
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'/'i18n'

def strip_additions(text):
    text=re.sub(r'<!-- i18n:seo -->\n.*?<!-- /i18n:seo -->\n','',text,flags=re.S)
    return re.sub(r'<!-- i18n:switch -->.*?<!-- /i18n:switch -->','',text,flags=re.S)

class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.lang=None;self.links=[];self.meta={};self.ids=[];self.title='';self.in_title=False;self.switch=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='html':self.lang=a.get('lang')
        if tag=='link':self.links.append(a)
        if tag=='meta':self.meta[a.get('name') or a.get('property')]=a.get('content','')
        if tag=='title':self.in_title=True
        if a.get('id'):self.ids.append(a['id'])
        if tag=='a' and 'mn-language' in a.get('class','').split():self.switch.append(a)
    def handle_endtag(self,tag):
        if tag=='title':self.in_title=False
    def handle_data(self,text):
        if self.in_title:self.title+=text

def digest(text):return hashlib.sha256(text.encode('utf-8')).hexdigest()

def check_pending(pages):
    errors=[]
    baseline=json.loads((DATA/'ru-baseline.json').read_text(encoding='utf-8'))
    for path,text in pages.items():
        rel=path.relative_to(ROOT).as_posix()
        if not rel.startswith('en/'):
            if digest(strip_additions(text))!=baseline['html'][rel]:errors.append(f'Russian content changed beyond allowed additions: {rel}')
            continue
        clean=strip_additions(text)
        clean=re.sub(r'<!--.*?-->|<style\b[^>]*>.*?</style>','',clean,flags=re.S|re.I)
        clean=clean.replace(".replaceAll('ё','е')",'')
        cyr=re.findall(r'.{0,40}[А-Яа-яЁё]+.{0,80}',clean)
        if cyr:errors.append(f'{rel}: untranslated content: {cyr[:4]}')
        if '@@g' in text:errors.append(f'{rel}: unresolved template slots')
        p=Page();p.feed(text)
        if p.lang!='en':errors.append(f'{rel}: lang is not en')
        if len(p.ids)!=len(set(p.ids)):errors.append(f'{rel}: duplicate IDs')
        if not p.title.strip() or not p.meta.get('description'):errors.append(f'{rel}: missing title/description')
        for k in ('og:title','og:description','og:url'):
            if not p.meta.get(k):errors.append(f'{rel}: missing {k}')
        for body in re.findall(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',text,re.S):
            try:
                value=json.loads(body)
                if value.get('inLanguage')!='en':errors.append(f'{rel}: JSON-LD language')
            except Exception as exc:errors.append(f'{rel}: invalid JSON-LD: {exc}')
    return errors

def check():
    from i18n_build import route_url,select,load_json
    errors=[]
    routes=load_json('routes.json')
    ready=[r for r in routes if r['status']=='ready']
    expected_ready={r['ru_file'] for r in routes if r['ru_file'].startswith(('lenormand/','runes/'))}
    if len(routes)!=175 or len(ready)!=65 or {r['ru_file'] for r in ready}!=expected_ready:
        errors.append(f'Route manifest: expected 65 ready Lenormand/Runes pairs, found {len(ready)}/{len(routes)}')
    pages={}
    for r in ready:
        for key in ('ru_file','en_file'):
            p=ROOT/r[key]
            if not p.is_file():errors.append(f'Missing paired page: {r[key]}')
            else:pages[p]=p.read_text(encoding='utf-8')
    errors.extend(check_pending(pages))
    for r in ready:
        expected={'ru':route_url(r['ru_file']),'en':route_url(r['en_file']),'x-default':route_url(r['ru_file'])}
        for key,lang in [('ru_file','ru'),('en_file','en')]:
            path=ROOT/r[key]
            if path not in pages:continue
            p=Page();p.feed(pages[path])
            links=[a for a in p.links if a.get('rel')=='alternate']
            if len(links)!=3 or {a.get('hreflang'):a.get('href') for a in links}!=expected:errors.append(f'{r[key]}: hreflang mismatch')
            if len(p.switch)!=1:errors.append(f'{r[key]}: expected one language switch')
            else:
                target=(path.parent/p.switch[0].get('href','')).resolve()
                wanted=(ROOT/r['en_file' if lang=='ru' else 'ru_file']).resolve()
                if target!=wanted:errors.append(f'{r[key]}: language switch target mismatch')
            if lang=='en':
                canonical=[a.get('href') for a in p.links if a.get('rel')=='canonical']
                if canonical!=[expected['en']]:errors.append(f'{r[key]}: canonical mismatch')
                ru_text=pages[ROOT/r['ru_file']]
                if re.findall(r'<input\b[^>]*\bid="(ln-[^"]+)"',ru_text)!=re.findall(r'<input\b[^>]*\bid="(ln-[^"]+)"',pages[path]):errors.append(f'{r[key]}: card tab structure changed')
                if 'fc-donate' in pages[path]:
                    for body in re.findall(r'<div class="(?:fc-links fc-donate|about-donate)">(.*?)</div>',pages[path],re.S):
                        urls=re.findall(r'href="([^"]+)"',body)
                        if not urls or urls[0]!='https://ko-fi.com/jetjarret':errors.append(f'{r[key]}: Ko-fi is not first')
    actual_en={p.relative_to(ROOT).as_posix() for p in (ROOT/'en').rglob('*.html')}
    if actual_en!={r['en_file'] for r in ready}:errors.append('Unexpected or missing English pages for the accepted stage')
    from check_runes_i18n import check as check_runes
    errors.extend(check_runes())
    try:
        d=load_json('lenormand.json');en=select(d,'en');ru=select(d,'ru')
        original=json.loads((ROOT/'data'/'lenormand.json').read_text(encoding='utf-8'))
        if ru!=original:errors.append('Bilingual Lenormand RU source does not match supplied JSON')
        for lang,value in [('ru',ru),('en',en)]:
            cards=value['cards'];pairs=value['pairs']
            if {c['n'] for c in cards}!=set(range(1,37)) or len(cards)!=36:errors.append(f'{lang}: expected cards 1–36')
            expected={(a,b) for a in range(1,37) for b in range(1,37) if a!=b}
            if len(pairs)!=1260 or {(p['a'],p['b']) for p in pairs}!=expected:errors.append(f'{lang}: incomplete directed pairs')
            if any(len(c['spheres'])!=10 for c in cards):errors.append(f'{lang}: expected ten meaning areas per card')
        select(load_json('lenormand-guide.json'),'en')
    except Exception as exc:errors.append(str(exc))
    baseline=load_json('ru-baseline.json')
    paired={r['ru_file'] for r in ready}
    for rel,hash_ in baseline['files'].items():
        if rel.endswith('.py') or rel=='sitemap.xml' or rel in paired:continue
        p=ROOT/rel
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=hash_:errors.append(f'Protected original changed: {rel}')
    ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
    for name in ('sitemap.xml','en/sitemap.xml'):
        try:
            urls=[e.text for e in ET.parse(ROOT/name).findall('s:url/s:loc',ns)]
            expected={route_url(r['en_file']) for r in ready}
            if not expected.issubset(set(urls)):errors.append(f'{name}: missing English URLs')
            if len(urls)!=len(set(urls)):errors.append(f'{name}: duplicate URLs')
            if name.startswith('en/') and set(urls)!=expected:errors.append(f'{name}: unexpected URLs')
        except Exception as exc:errors.append(f'{name}: {exc}')
    node=os.environ.get('NODE_BINARY') or shutil.which('node')
    if node:
        scripts={}
        for path,text in pages.items():
            for attrs,body in re.findall(r'<script\b([^>]*)>(.*?)</script>',text,re.S|re.I):
                if 'application/ld+json' not in attrs and body.strip():scripts.setdefault(body,path)
        for body,path in scripts.items():
            result=subprocess.run([node,'--check'],input=body,encoding='utf-8',capture_output=True)
            if result.returncode:errors.append(f'{path.relative_to(ROOT)}: inline JavaScript: {result.stderr.strip()}')
    if not errors:print(f'OK i18n: {len(ready)} RU/EN pairs; translations, reciprocal SEO, original content and assets preserved')
    return errors
