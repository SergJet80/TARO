"""Offline checks for the RU-template rune localization stage."""
from pathlib import Path
from html.parser import HTMLParser
import json, os, re, shutil, subprocess

ROOT=Path(__file__).resolve().parent

class Structure(HTMLParser):
    def __init__(self):
        super().__init__(); self.controls=[]; self.images=[]; self.tags=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag in ('main','section','article','dialog','input','select','option','button','label','details','summary','table','tr','td','th'):
            self.tags.append((tag,tuple((k,v) for k,v in attrs if k in ('id','class','type','name','value','for'))))
        if tag=='img':self.images.append(a['src'])

def check():
    from i18n_build import select,load_json
    from check_site import local_target
    from runes_localize import staves_mapping,replace_once
    errors=[]
    original=json.loads((ROOT/'data/runes.json').read_text(encoding='utf-8'))
    paired=load_json('runes.json')
    if select(paired,'ru')!=original:errors.append('Runes: bilingual Russian source changed')
    english=select(paired,'en')
    if len(english['runes'])!=24:errors.append('Runes: expected 24 entries')
    paths=['runes/index.html','runes/rasclady/index.html','runes/staves.html']+[f"runes/{r['id']}/index.html" for r in original['runes']]
    for rel in paths:
        ru=(ROOT/rel).read_text(encoding='utf-8'); en=(ROOT/'en'/rel).read_text(encoding='utf-8')
        a=Structure();a.feed(ru);b=Structure();b.feed(en)
        if a.tags!=b.tags:errors.append(f'{rel}: structural controls/table mismatch')
        if [local_target(ROOT/rel,v) for v in a.images]!=[local_target(ROOT/'en'/rel,v) for v in b.images]:errors.append(f'{rel}: image target mismatch')
        if re.findall(r'<style\b[^>]*>.*?</style>',ru,re.S)!=re.findall(r'<style\b[^>]*>.*?</style>',en,re.S):errors.append(f'{rel}: source styles/background changed')
    node=os.environ.get('NODE_BINARY') or shutil.which('node')
    if not node:
        errors.append('Runes: Node.js is required to verify the live stave dataset (set NODE_BINARY)')
        return errors
    datasets=[]
    for prefix in ('','en/'):
        text=(ROOT/f'{prefix}runes/staves.html').read_text(encoding='utf-8')
        script=text[text.index('const R='):text.index('const nm=')]
        result=subprocess.run([node,'-e',script+'\nconsole.log(JSON.stringify({R,S,data}));'],capture_output=True,encoding='utf-8')
        if result.returncode:
            errors.append(f'{prefix}staves: runtime failure: {result.stderr}');return errors
        datasets.append(json.loads(result.stdout))
    ru,en=datasets
    if len(ru['data'])!=159 or len(en['data'])!=159:errors.append('Staves: expected 159 live entries including the three graphic staves')
    if list(ru['R'])!=list(en['R']) or len(en['R'])!=24:errors.append('Staves: rune key mismatch')
    for key,value in ru['R'].items():
        if value[0]!=en['R'][key][0]:errors.append(f'Staves: glyph changed: {key}')
    for key,value in ru['S'].items():
        if value[1:3]!=en['S'][key][1:3]:errors.append(f'Staves: source URL/year changed: {key}')
    mapping=staves_mapping()
    for a,b in zip(ru['data'],en['data']):
        for key in ('id','seq'):
            if a.get(key)!=b.get(key):errors.append(f'Staves: {key} changed: {a.get("id")}')
        if a['src'][1:3]!=b['src'][1:3]:errors.append(f'Staves: source changed: {a.get("id")}')
        for key in ('title','cat','note','desc','type'):
            if key not in a:continue
            local_mapping={**mapping,a['title'].lower():b['title'].lower()}
            expected=replace_once(a[key],local_mapping)
            # The fallback purpose is assembled from the lower-case title at runtime.
            expected=expected.replace(a['title'].lower(),b['title'].lower())
            if expected!=b[key]:errors.append(f'Staves: translated {key} differs for {a["title"]}: {expected!r} != {b[key]!r}')
    if not errors:print('OK runes: 27 page structures, image targets/backgrounds, 24 glyphs and 159 live stave formulas preserved')
    return errors

if __name__=='__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    errors=check()
    print('\n'.join(errors));raise SystemExit(bool(errors))
