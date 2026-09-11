#!/usr/bin/env python3
"""Перегенерация data/i18n/ru-baseline.json из ТЕКУЩЕГО состояния RU-сайта.
Baseline снят GPT со старого архива v4.0; после него легитимные правки RU
(og-теги, баннер ставов, lenormand guide, navbar, css) ломали проверки.

Семантика (по check_i18n.py / runes_localize.py / taro_build.py):
- html: sha256(strip_additions(text)) для всех RU-страниц.
- files: для готовых пар и ресурсов — sha256(raw bytes);
  для скрытых роутов (cards/*, index.html) — sha256(strip_i18n(text)) т.к.
  runes_localize сравнивает candidates=[strip_i18n(u8), strip_i18n(crlf)].
"""
from pathlib import Path
import hashlib, json, re

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data' / 'i18n'

def strip_additions(text):
    text = re.sub(r'<!-- i18n:seo -->\n.*?<!-- /i18n:seo -->\n', '', text, flags=re.S)
    return re.sub(r'<!-- i18n:switch -->.*?<!-- /i18n:switch -->', '', text, flags=re.S)

def strip_i18n(text):
    # как в runes_localize.strip_i18n — вырезает i18n-маркерные блоки/переключатель
    text = re.sub(r'<!-- i18n:seo -->\n.*?<!-- /i18n:seo -->\n', '', text, flags=re.S)
    return re.sub(r'<!-- i18n:switch -->.*?<!-- /i18n:switch -->', '', text, flags=re.S)

routes = json.loads((DATA / 'routes.json').read_text(encoding='utf-8'))
status = {r['ru_file']: r['status'] for r in routes}

html_map, files_map = {}, {}
for p in ROOT.rglob('*'):
    if not p.is_file():
        continue
    rel = p.relative_to(ROOT).as_posix()
    if rel.startswith('en/') or rel.startswith('data/i18n'):
        continue
    if rel.endswith('.html'):
        text = p.read_text(encoding='utf-8')
        html_map[rel] = hashlib.sha256(strip_additions(text).encode('utf-8')).hexdigest()
        if rel == 'sitemap.xml':
            continue
        st = status.get(rel)
        # оба вида проверки сравнивают strip_i18n-текст (маркеры i18n не считаются изменением)
        stripped = strip_i18n(text)
        files_map[rel] = hashlib.sha256(stripped.encode('utf-8')).hexdigest()
    elif rel == 'sitemap.xml':
        continue
    elif rel.endswith('.py'):
        continue
    else:
        files_map[rel] = hashlib.sha256(p.read_bytes()).hexdigest()

baseline = {'html': html_map, 'files': files_map}
(DATA / 'ru-baseline.json').write_text(json.dumps(baseline, ensure_ascii=False, indent=1), encoding='utf-8')
print(f'baseline regenerated: {len(html_map)} html, {len(files_map)} files')