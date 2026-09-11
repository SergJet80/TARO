#!/usr/bin/env python3
"""Build the Russian rune section and its faithful English counterpart."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json
import re
import shutil
import hashlib
from html import escape, unescape

import i18n_build
import runes_build

ROOT = Path(__file__).resolve().parent
I18N = ROOT / "data" / "i18n"
RUNE_PATHS = ["runes/index.html", "runes/rasclady/index.html"]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def strip_i18n(text: str) -> str:
    text = re.sub(r'<!-- i18n:seo -->\n.*?<!-- /i18n:seo -->\n', '', text, flags=re.S)
    return re.sub(r'<!-- i18n:switch -->.*?<!-- /i18n:switch -->', '', text, flags=re.S)


def update_route_stage() -> None:
    routes = read_json(I18N / "routes.json")
    for route in routes:
        route["status"] = "ready" if route["ru_file"].startswith(("lenormand/", "runes/")) else "planned"
    (I18N / "routes.json").write_text(json.dumps(routes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    i18n_build.load_json.cache_clear()
    i18n_build.ready_paths.cache_clear()


def cleanup_rejected_english_output() -> None:
    en_root = (ROOT / "en").resolve()
    for target in (en_root / "astrology", en_root / "cards", en_root / "numerology"):
        resolved = target.resolve()
        if en_root not in resolved.parents:
            raise RuntimeError(f"Refusing to remove path outside English output: {resolved}")
        if resolved.is_dir():
            shutil.rmtree(resolved)
    for name in ("index.html", "spreads.html"):
        path = en_root / name
        if path.is_file():
            path.unlink()


def build_table(runes: list[dict]) -> str:
    lines = ["# 4. Summary Reference for the 24 Runes", "", "| Rune | Main idea | Finances | Work | Relationships | Modern magical function | Shadow |", "|---|---|---|---|---|---|---|"]
    for rune in runes:
        lines.append("| {symbol} {name} | {idea} | {finance} | {work} | {relations} | {magic} | {shadow} |".format(
            symbol=rune["symbol"], name=rune["name"], idea=rune["keywords"][0],
            finance=rune["spheres"]["Finances"], work=rune["spheres"]["Work"], relations=rune["spheres"]["Relationships"],
            magic=rune["magic"]["Modern magical interpretation"], shadow=rune["divination"]["negative"]))
    return "\n".join(lines)


def english_source(original: dict) -> dict:
    translated = read_json(I18N / "runes-en.json")
    expected = [rune["id"] for rune in original["runes"]]
    if list(translated["runes"]) != expected:
        raise ValueError("English rune IDs or order do not match data/runes.json")
    result = deepcopy(original)
    for rune in result["runes"]:
        localized = translated["runes"][rune["id"]]
        required = set(rune) - {"id", "symbol", "name", "sound", "image", "hasReversed"}
        missing = required - set(localized)
        if missing:
            raise ValueError(f"{rune['id']}: missing English fields: {sorted(missing)}")
        for key in required:
            rune[key] = deepcopy(localized[key])
        spheres = rune["spheres"]
        rune["spheres"] = {
            "Финансы": spheres["Finances"], "Работа": spheres["Work"],
            "Отношения": spheres["Relationships"], "Семья и быт": spheres["Family and home"],
        }
    result["intro"] = translated["intro"]
    result["sections"].update(translated["sections"])
    table_runes = []
    for rune in result["runes"]:
        row = deepcopy(rune)
        row["spheres"] = {
            "Finances": rune["spheres"]["Финансы"], "Work": rune["spheres"]["Работа"],
            "Relationships": rune["spheres"]["Отношения"], "Family and home": rune["spheres"]["Семья и быт"],
        }
        table_runes.append(row)
    result["sections"]["table"] = build_table(table_runes)
    return result


def common_mapping():
    return {p['ru']:p['en'] for p in read_json(I18N/'lenormand-ui.json')}


def replace_once(text, mapping):
    pattern=re.compile('|'.join(re.escape(s) for s in sorted(mapping,key=len,reverse=True) if s))
    return pattern.sub(lambda m:mapping[m.group()],text)


def paired_source(ru, en):
    if isinstance(ru,dict):
        if len(ru)!=len(en): raise ValueError('Source object shape mismatch')
        return {k:paired_source(v,ev) for (k,v),(_,ev) in zip(ru.items(),en.items())}
    if isinstance(ru,list):
        if len(ru)!=len(en): raise ValueError('Source array shape mismatch')
        return [paired_source(a,b) for a,b in zip(ru,en)]
    if isinstance(ru,str) and ru!=en: return {'ru':ru,'en':en}
    if ru!=en: raise ValueError('Non-text source value changed')
    return ru


def rune_mapping(original, english):
    mapping=common_mapping()
    mapping.update({p['ru']:p['en'] for p in read_json(I18N/'runes-ui.json')})
    def walk(ru,en):
        if isinstance(ru,dict):
            for (k,v),(ek,ev) in zip(ru.items(),en.items()):
                if k!=ek:mapping[k]=ek
                walk(v,ev)
        elif isinstance(ru,list):
            for a,b in zip(ru,en):walk(a,b)
        elif isinstance(ru,str) and ru!=en:
            mapping[ru]=en
            mapping[runes_build.bold_inline(ru)]=runes_build.bold_inline(en)
            mapping[escape(ru,quote=False)]=escape(en,quote=False)
    walk(original,english)
    for key in original['sections']:
        mapping[runes_build.md_to_html(original['sections'][key])]=runes_build.md_to_html(english['sections'][key])
    for ru,en in zip(original['runes'],english['runes']):
        def search(r):return escape((r['name']+' '+r['nameRu']+' '+' '.join(r['keywords'])+' '+r['short']).lower(),quote=False)
        mapping[search(ru)]=search(en)
        mapping[escape(ru['short'][:160],quote=False)]=escape(en['short'][:160],quote=False)
    return mapping


def staves_mapping():
    mapping=common_mapping()
    for name in ('titles','visible','descriptions','ui'):
        mapping.update(read_json(I18N/f'runes-staves-{name}.json'))
    return mapping


def translate_staves(source: str) -> str:
    mapping=staves_mapping()
    # The original purpose rules classify Russian titles. Compile each rule to
    # the exact translated title set, keeping its order and selection behavior.
    titles=read_json(I18N/'runes-staves-titles.json')
    purpose=re.search(r'function purpose\(t,c\)\{.*?\n\}',source,re.S)
    if not purpose:raise ValueError('Source purpose function missing')
    def rule(m):
        matches=[en for ru,en in titles.items() if re.search(m[1],ru,re.I)]
        escaped=[re.sub(r'([.*+?^${}()|\[\]\\/])',r'\\\1',s) for s in matches]
        return '/^(?:'+'|'.join(escaped)+')$/i' if matches else '/(?!) /i'
    compiled=re.sub(r'/([^/\n]+)/i',rule,purpose.group())
    source=source[:purpose.start()]+compiled+source[purpose.end():]
    token=re.compile(r'''"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*' '''.strip())
    def script_translate(script):
        script=re.sub(r'/\*.*?\*/',lambda m:m.group() if not re.search('[А-Яа-яЁё]',m.group()) else '/* Localized source data. */',script,flags=re.S)
        def literal(m):
            raw=m.group()
            if not re.search('[А-Яа-яЁё]',raw):return raw
            # All translated source literals are ordinary quoted strings.
            value=raw[1:-1].replace("\\'", "'").replace('\\"','"')
            en=replace_once(value,mapping)
            return json.dumps(en,ensure_ascii=False).replace('</','<\\/')
        return token.sub(literal,script).replace("localeCompare(y.cat,'ru')","localeCompare(y.cat,'en')").replace("localeCompare(y.title,'ru')","localeCompare(y.title,'en')")
    parts=re.split(r'(<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>|<!--.*?-->)',source,flags=re.S|re.I)
    translated=[]
    for part in parts:
        if part.startswith('<script'):translated.append(script_translate(part))
        elif part.startswith(('<style','<!--')):translated.append(part)
        else:translated.append(replace_once(part,{k:escape(v,quote=True) for k,v in mapping.items()}))
    return ''.join(translated)


def main() -> int:
    update_route_stage()
    original = read_json(ROOT / "data" / "runes.json")
    english=english_source(original)
    bilingual=paired_source(original,english)
    if i18n_build.select(bilingual,'ru')!=original:raise ValueError('Russian projection changed')
    (I18N/'runes.json').write_text(json.dumps(bilingual,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    paths=RUNE_PATHS+[f"runes/{r['id']}/index.html" for r in original['runes']]
    ru_pages={p:strip_i18n((ROOT/p).read_text(encoding='utf-8')) for p in paths}
    mapping=rune_mapping(original,english)
    en_pages={p:replace_once(text,mapping) for p,text in ru_pages.items()}

    pending: dict[Path, str] = {}
    for relative, text in ru_pages.items():
        pending[ROOT / relative] = i18n_build.finalize(strip_i18n(text), relative, "ru", english_disclaimer=False)
    for relative, text in en_pages.items():
        pending[ROOT / "en" / relative] = i18n_build.finalize(
            text, relative, "en", template=True, english_disclaimer=False)

    staves_path = ROOT / "runes" / "staves.html"
    staves_ru = strip_i18n(staves_path.read_text(encoding="utf-8"))
    pending[staves_path] = i18n_build.finalize(staves_ru, "runes/staves.html", "ru", english_disclaimer=False)
    pending[ROOT / "en" / "runes" / "staves.html"] = i18n_build.finalize(
        translate_staves(staves_ru), "runes/staves.html", "en", template=True, english_disclaimer=False)

    from check_i18n import check_pending
    errors=check_pending(pending)
    if errors:raise ValueError('\n'.join(errors))
    cleanup_rejected_english_output()
    for route in read_json(I18N/'routes.json'):
        if route['status']!='ready':
            p=ROOT/route['ru_file']
            text=strip_i18n(p.read_text(encoding='utf-8'))
            expected=read_json(I18N/'ru-baseline.json')['files'][route['ru_file']]
            candidates=[text.encode('utf-8'),text.replace('\n','\r\n').encode('utf-8')]
            match=next((b for b in candidates if hashlib.sha256(b).hexdigest()==expected),None)
            if match is None:raise ValueError(f'Planned Russian page differs from original: {route["ru_file"]}')
            p.write_bytes(match)
    for path, text in pending.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    i18n_build.update_sitemaps()
    print(f"OK: {len(original['runes'])} rune pages + catalogue + casts + staves in RU/EN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
