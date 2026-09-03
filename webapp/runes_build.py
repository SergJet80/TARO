#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор раздела «Руны» (Старший Футарк, 24 руны).
Источник контента: data/runes.json (собран из предоставленного Markdown, без правок смысла).
Запуск:  python3 runes_build.py   (из каталога webapp/)
Создаёт: runes/index.html и runes/<id>/index.html
"""
import json
import html
import os
import re

WEBAPP = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(WEBAPP, 'data', 'runes.json')
CSS_V = '3.0'

with open(DATA, encoding='utf-8') as f:
    SRC = json.load(f)

RUNES = SRC['runes']
INTRO = SRC['intro']
TAIL = SRC.get('tail', '')

# ── вспомогательные ──────────────────────────────────────────────────────────

def esc(s):
    return html.escape(s or '', quote=False)

def paras(text):
    """Текст → список абзацев (по пустым строкам)."""
    return [p.strip() for p in (text or '').split('\n\n') if p.strip()]

def kv_to_items(text):
    """Список вида '- Ключ: значение' → [(ключ, значение)]."""
    out = []
    for line in (text or '').splitlines():
        m = re.match(r'- (.+?): (.+)', line.strip())
        if m:
            out.append((m.group(1), m.group(2)))
    return out

def bold_inline(text):
    """**bold** → <strong>, остальное экранируем."""
    parts = re.split(r'(\*\*.+?\*\*)', text or '')
    out = []
    for p in parts:
        if p.startswith('**') and p.endswith('**'):
            out.append('<strong>' + esc(p[2:-2]) + '</strong>')
        else:
            out.append(esc(p))
    return ''.join(out)

def section_html(title, inner, extra=''):
    cls = 'sign-sec' + ((' ' + extra) if extra else '')
    return f'      <section class="{cls}">\n        <h2 class="sec-title">{esc(title)}</h2>\n{inner}\n      </section>'

def ps(text):
    return '\n'.join(f'        <p>{bold_inline(p)}</p>' for p in paras(text))

def ul_items(items):
    if not items:
        return ''
    lis = '\n'.join(f'          <li><strong>{esc(k)}:</strong> {bold_inline(v)}</li>' for k, v in items)
    return f'        <ul class="rune-list">\n{lis}\n        </ul>'

# ── page shells ──────────────────────────────────────────────────────────────

def shell(title, desc, css_prefix, nav_prefix, active, body):
    return f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='0.9em' font-size='90'%3E%E1%9A%A0%3C/text%3E%3C/svg%3E">
<link rel="stylesheet" href="{css_prefix}fonts/fonts.css?v={CSS_V}">
<link rel="stylesheet" href="{css_prefix}css/style.css?v={CSS_V}">
<link rel="stylesheet" href="{css_prefix}css/astrology.css?v={CSS_V}">
<link rel="stylesheet" href="{css_prefix}css/runes.css?v={CSS_V}">
</head>

<body>

<div class="stars" aria-hidden="true"></div>
<div class="stars stars2" aria-hidden="true"></div>

<nav class="main-nav" aria-label="Разделы">
  <div class="main-nav-inner">
    <a href="{nav_prefix}index.html"><span class="mn-icon">✦</span> Таро</a>
    <a href="{nav_prefix}astrology/index.html"><span class="mn-icon">♄</span> Астрология</a>
    <a href="{nav_prefix}runes/index.html"{' class="mn-active"' if active == 'runes' else ''}><span class="mn-icon">ᚠ</span> Руны</a>
    <a href="{nav_prefix}numerology/index.html"><span class="mn-icon">❿</span> Теория</a>
  </div>
</nav>

{body}
</body>
</html>
'''

FOOTER = '''<footer class="site-footer">
  <p>Руны · Старший Футарк — справочник значений</p>
  <p class="footer-note">Материалы носят справочный и развлекательный характер</p>
</footer>'''

# ── index раздела ────────────────────────────────────────────────────────────

def rune_card(r):
    return f'''    <a class="sign-card rune-card" href="{r['id']}/index.html" data-aett="{esc(r['aett'])}" data-search="{esc((r['name'] + ' ' + r['nameRu'] + ' ' + ' '.join(r['keywords']) + ' ' + r['short']).lower())}">
      <div class="sign-card-body">
        <span class="sign-sym rune-sym">{r['symbol']}</span>
        <h2 class="sign-name">{esc(r['nameRu'])}</h2>
        <p class="sign-sub">{esc(r['literal'])}</p>
        <p class="rune-kw">{esc(' · '.join(r['keywords'][:4]))}</p>
      </div>
      <div class="sign-card-img"><img src="{r['image']}" alt="Руна {esc(r['name'])} ({esc(r['nameRu'])}) — мистическая иллюстрация" loading="lazy"></div>
    </a>'''

def build_index():
    cards = '\n'.join(rune_card(r) for r in RUNES)
    body = f'''<header class="site-header">
  <div class="header-inner">
    <h1 class="site-title"><span class="title-star">ᚠ</span> Руны <span class="title-sub">Старший Футарк</span></h1>
    <p class="site-tagline">24 руны · значение, мантика, магия, диагностика</p>
    <div class="search-wrap">
      <input type="search" id="search" placeholder="Поиск: деньги, защита, дорога, конфликт…" autocomplete="off">
    </div>
  </div>
</header>

<nav class="tabs" aria-label="Фильтр по аттам">
  <div class="tabs-inner" id="tabs">
    <button class="tab active" data-aett="">ᛝ Все</button>
    <button class="tab" data-aett="I атт">I атт · Фрейя</button>
    <button class="tab" data-aett="II атт">II атт · Хагаль</button>
    <button class="tab" data-aett="III атт">III атт · Тюр</button>
  </div>
</nav>

<main class="astro-wrap runes-wrap">
  <p class="astro-into">{esc(INTRO)}</p>

  <a class="wheel-banner" href="rasclady/index.html">
    <span class="wb-icon">🎲</span>
    <span class="wb-text"><strong>Расклады и таблица</strong> — диагностика на 1/3/7 рун, сводная шпаргалка, магия по категориям</span>
    <span class="wb-arrow">→</span>
  </a>

  <div class="signs-grid" id="deck">
{cards}
  </div>
  <p class="empty-msg" id="emptyMsg" hidden>Ничего не найдено. Попробуйте другое слово.</p>
</main>

{FOOTER}

<script>
(function() {{
  var inp = document.getElementById('search');
  var tabs = document.getElementById('tabs');
  var cards = Array.prototype.slice.call(document.querySelectorAll('#deck .rune-card'));
  var empty = document.getElementById('emptyMsg');
  var aett = '';
  function apply() {{
    var q = inp.value.trim().toLowerCase();
    var shown = 0;
    cards.forEach(function(c) {{
      var ok = (!aett || c.dataset.aett === aett) && (!q || c.dataset.search.indexOf(q) !== -1);
      c.style.display = ok ? '' : 'none';
      if (ok) shown++;
    }});
    empty.hidden = shown > 0;
  }}
  inp.addEventListener('input', apply);
  tabs.addEventListener('click', function(e) {{
    var b = e.target.closest('.tab');
    if (!b) return;
    tabs.querySelectorAll('.tab').forEach(function(t) {{ t.classList.remove('active'); }});
    b.classList.add('active');
    aett = b.dataset.aett;
    apply();
  }});
}})();
</script>'''
    out = shell('Руны — Старший Футарк · Справочник значений',
                'Справочник всех 24 рун Старшего Футарка: значение, историческая основа, мантика, магия, сочетания и диагностика.',
                '../', '../', 'runes', body)
    with open(os.path.join(WEBAPP, 'runes', 'index.html'), 'w', encoding='utf-8') as f:
        f.write(out)

# ── страница руны ────────────────────────────────────────────────────────────

def tabbed(r):
    t = []

    # ✦ Значение
    s = []
    s.append(section_html('Краткая суть', ps(r['short'])))
    s.append(section_html('Историческая традиция',
        ps(r['history']) + (ul_items([('Ключевые значения', ', '.join(r['keywords']))]) if r['keywords'] else '')))
    dv = r['divination']
    dv_html = ul_items([
        ('Положительное проявление', dv.get('positive', '')),
        ('Негативное проявление', dv.get('negative', '')),
        ('Совет', dv.get('advice', '')),
        ('Предупреждение', dv.get('warning', '')),
        ('Итог ситуации', dv.get('outcome', '')),
    ])
    s.append(section_html('Современная мантика', '<p class="rune-layer-note">Мантические значения относятся к современной рунической практике.</p>' + (dv_html or ps(r['divination'].get('general','')))))
    s.append(section_html('Психологическое состояние', ps(r['psychology'])))
    s.append(section_html('Духовное значение', ps(r['spiritual'])))
    s.append(section_html('Прямое и перевёрнутое положение', ps(r['reversedNote'])))
    s.append(section_html('Отличия трактовок разных школ', ps(r['schools'])))
    s.append(section_html('Итог', ps(r['summary'])))
    t.append(('✦', 'Значение', s))

    # ♥ Отношения и сферы
    s = []
    sph = r['spheres']
    order = ['Финансы', 'Работа', 'Отношения', 'Семья и быт']
    s.append(section_html('Финансы', ps(sph.get('Финансы', ''))))
    s.append(section_html('Работа', ps(sph.get('Работа', ''))))
    s.append(section_html('Отношения', ps(sph.get('Отношения', ''))))
    s.append(section_html('Семья и быт', ps(sph.get('Семья и быт', ''))))
    per = r['person']
    s.append(section_html('Руна как характеристика человека',
        ps(per.get('general', '')) + ul_items([('Мысли', per.get('thoughts', '')),
                                               ('Чувства', per.get('feelings', '')),
                                               ('Действия', per.get('actions', ''))])))
    t.append(('♥', 'Сферы жизни', s))

    # ◈ Магия
    s = []
    mag = r['magic']
    s.append(section_html('Современное магическое значение',
        '<p class="rune-layer-note">Это современная эзотерическая практика, а не исторически подтверждённая традиция.</p>'
        + ul_items(list(mag.items()))))
    s.append(section_html('Руна в формулах и ставах', ps(r['formulas'])))
    t.append(('◈', 'Магия', s))

    # ᛉ Диагностика
    d = r['diagnostics']
    s = []
    s.append(section_html('Эзотерическая трактовка',
        f'<p class="rune-layer-note">В современной эзотерической трактовке</p>' + ps(d.get('esoteric', '')), 'diag-eso'))
    s.append(section_html('Возможное бытовое объяснение',
        f'<p class="rune-layer-note">Альтернативное объяснение</p>' + ps(d.get('household', '')), 'diag-house'))
    t.append(('ᛉ', 'Диагностика', s))

    # ⛓ Сочетания
    s = []
    combs = r['combinations']
    if combs:
        items = [(f"{c['rune1'].capitalize()} + {c['rune2'].capitalize()}", c['interpretation']) for c in combs]
        s.append(section_html('Характерные сочетания', ul_items(items)))
    s.append(section_html('Руна в формулах и ставах', ps(r['formulas'])))
    t.append(('⛓', 'Сочетания', s))

    return t

def build_rune_page(r, prev, nxt):
    tabs = tabbed(r)
    tab_btns = '\n'.join(
        f'      <button class="rt-btn{" active" if i == 0 else ""}" data-tab="{i}">{icon} {esc(label)}</button>'
        for i, (icon, label, _) in enumerate(tabs))
    tab_panes = []
    for i, (icon, label, secs) in enumerate(tabs):
        inner = '\n'.join(secs)
        tab_panes.append(f'    <div class="rt-pane{" active" if i == 0 else ""}" data-pane="{i}">\n{inner}\n    </div>')
    panes = '\n'.join(tab_panes)

    # prev / next
    def nb(other, arrow, before):
        if other:
            align = '' if before else ' <span>→</span>'
            return f'    <a class="sign-nav-btn" href="../{other["id"]}/index.html">{arrow} {esc(other["nameRu"])}{align}</a>'
        return f'    <a class="sign-nav-btn" style="visibility:hidden" href="#">{arrow} ·</a>'

    body = f'''<header class="site-header">
  <div class="header-inner">
    <h1 class="site-title"><span class="title-star rune-hero-sym">{r['symbol']}</span> {esc(r['nameRu'])} <span class="title-sub">{esc(r['name'])}</span></h1>
    <p class="sign-hero-sub">{esc(r['aett'])} · звук «{esc(r['sound'])}» · {esc(r['literal'])}</p>
  </div>
</header>

<main class="sign-page rune-page">
  <div class="sign-hero">
    <img src="../{r['image']}" alt="Руна {esc(r['name'])} ({esc(r['nameRu'])}) — мистическая иллюстрация" class="sign-hero-img">
  </div>

  <p class="rune-short">{bold_inline(r['short'])}</p>

  <nav class="rune-tabs" aria-label="Разделы руны">
{tab_btns}
  </nav>

  <div class="sign-blocks" id="runePanes">
{panes}
  </div>

  <p class="astro-disclaimer">Мантические, магические и диагностические значения относятся к современной рунической практике. Историческая часть опирается на рунические поэмы и эпиграфику. Материалы носят справочный и развлекательный характер.</p>

  <nav class="sign-nav" aria-label="Навигация по рунам">
{nb(prev, '←', True)}
    <a class="sign-nav-btn back" href="../index.html">ᚠ Все руны</a>
{nb(nxt, '', False) if nxt else '    <a class="sign-nav-btn" style="visibility:hidden" href="#">→ ·</a>'}
  </nav>
</main>

{FOOTER}

<script>
(function() {{
  var bar = document.querySelector('.rune-tabs');
  var btns = Array.prototype.slice.call(bar.querySelectorAll('.rt-btn'));
  var panes = Array.prototype.slice.call(document.querySelectorAll('#runePanes .rt-pane'));
  bar.addEventListener('click', function(e) {{
    var b = e.target.closest('.rt-btn');
    if (!b) return;
    btns.forEach(function(x) {{ x.classList.remove('active'); }});
    panes.forEach(function(x) {{ x.classList.remove('active'); }});
    b.classList.add('active');
    var p = panes.filter(function(x) {{ return x.dataset.pane === b.dataset.tab; }})[0];
    if (p) p.classList.add('active');
  }});
}})();
</script>'''
    title = f"{r['name']} ({r['nameRu']}) — значение руны | Справочник"
    desc = r['short'][:160]
    out = shell(title, desc, '../../', '../../', 'runes', body)
    os.makedirs(os.path.join(WEBAPP, 'runes', r['id']), exist_ok=True)
    with open(os.path.join(WEBAPP, 'runes', r['id'], 'index.html'), 'w', encoding='utf-8') as f:
        f.write(out)

# ── Markdown-фрагменты → HTML ────────────────────────────────────────────────

def md_inline(text):
    """**bold**, *italic* → HTML, остальное экранируем."""
    s = bold_inline(text)
    # single *italic* (не путать с уже обработанным **)
    parts = re.split(r'(\*[^*]+\*)', s)
    out = []
    for part in parts:
        if part.startswith('*') and part.endswith('*') and len(part) > 2 and not part.startswith('**'):
            out.append('<em>' + part[1:-1] + '</em>')
        else:
            out.append(part)
    return ''.join(out)

def md_to_html(text):
    """Простой конвертер: заголовки, абзацы, списки, таблицы, нумерованные списки."""
    lines = text.splitlines()
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('### '):
            out.append(f'<h3 class="rd-h3">{md_inline(line[4:].strip())}</h3>')
        elif line.startswith('## '):
            out.append(f'<h3 class="rd-h2">{md_inline(line[3:].strip())}</h3>')
        elif line.startswith('# '):
            out.append(f'<h3 class="rd-h1">{md_inline(line[2:].strip())}</h3>')
        elif line.strip().startswith('|'):
            # таблица
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?', c) for c in cells):
                    rows.append(cells)
                i += 1
            i -= 1
            if rows:
                head = rows[0]
                t = ['<div class="rune-table-wrap"><table class="rune-table"><thead><tr>']
                t += [f'<th>{md_inline(c)}</th>' for c in head]
                t.append('</tr></thead><tbody>')
                for row in rows[1:]:
                    t.append('<tr>' + ''.join(f'<td>{md_inline(c)}</td>' for c in row) + '</tr>')
                t.append('</tbody></table></div>')
                out.append(''.join(t))
        elif re.match(r'^\d+\. ', line.strip()):
            items = []
            while i < len(lines) and re.match(r'^\d+\. ', lines[i].strip()):
                items.append(re.sub(r'^\d+\. ', '', lines[i].strip()))
                i += 1
            i -= 1
            out.append('<ol class="rune-ol">' + ''.join(f'<li>{md_inline(x)}</li>' for x in items) + '</ol>')
        elif line.strip().startswith('- '):
            items = []
            while i < len(lines) and lines[i].strip().startswith('- '):
                items.append(lines[i].strip()[2:])
                i += 1
            i -= 1
            out.append('<ul class="rune-ul">' + ''.join(f'<li>{md_inline(x)}</li>' for x in items) + '</ul>')
        elif line.strip():
            para = [line]
            while i + 1 < len(lines) and lines[i+1].strip() and not re.match(r'^(#|\||\d+\. |- )', lines[i+1].strip()):
                i += 1
                para.append(lines[i])
            out.append('<p>' + md_inline(' '.join(para)) + '</p>')
        i += 1
    return '\n'.join(out)

# ── страница «Расклады и таблица» ────────────────────────────────────────────

def build_rasclady():
    sec = SRC['sections']
    tabs = [
        ('🎲', 'Расклады', md_to_html(sec['rasclady'])),
        ('▦', 'Сводная таблица', md_to_html(sec['table'])),
        ('⚒', 'Магия по категориям', md_to_html(sec['magicCats'])),
        ('📜', 'Источники', md_to_html(sec['outro'])),
    ]
    btns = '\n'.join(f'      <button class="rt-btn{" active" if i == 0 else ""}" data-tab="{i}">{icon} {esc(label)}</button>'
                     for i, (icon, label, _) in enumerate(tabs))
    panes = '\n'.join(f'    <div class="rt-pane{" active" if i == 0 else ""}" data-pane="{i}">\n{html_}\n    </div>'
                      for i, (icon, label, html_) in enumerate(tabs))
    body = f'''<header class="site-header">
  <div class="header-inner">
    <h1 class="site-title"><span class="title-star">🎲</span> Расклады <span class="title-sub">и сводная таблица</span></h1>
    <p class="site-tagline">Диагностика · шпаргалка по 24 рунам · магический функционал</p>
  </div>
</header>

<main class="sign-page rune-page">
  <nav class="rune-tabs" aria-label="Разделы">
{btns}
  </nav>

  <div class="sign-blocks" id="runePanes">
{panes}
  </div>

  <p class="astro-disclaimer">Описанное — современная эзотерическая практика и справочный материал, а не исторически подтверждённая система древних германцев. Материалы носят справочный и развлекательный характер.</p>

  <nav class="sign-nav" aria-label="Навигация">
    <a class="sign-nav-btn back" href="index.html">ᚠ Все руны</a>
  </nav>
</main>

{FOOTER}

<script>
(function() {{
  var bar = document.querySelector('.rune-tabs');
  var btns = Array.prototype.slice.call(bar.querySelectorAll('.rt-btn'));
  var panes = Array.prototype.slice.call(document.querySelectorAll('#runePanes .rt-pane'));
  bar.addEventListener('click', function(e) {{
    var b = e.target.closest('.rt-btn');
    if (!b) return;
    btns.forEach(function(x) {{ x.classList.remove('active'); }});
    panes.forEach(function(x) {{ x.classList.remove('active'); }});
    b.classList.add('active');
    var p = panes.filter(function(x) {{ return x.dataset.pane === b.dataset.tab; }})[0];
    if (p) p.classList.add('active');
  }});
}})();
</script>'''
    out = shell('Расклады и сводная таблица рун | Справочник Старшего Футарка',
                'Руническая диагностика: расклады на одну, три и семь рун, сводная таблица 24 рун, магический функционал по категориям, источники и методология.',
                '../../', '../../', 'runes', body)
    os.makedirs(os.path.join(WEBAPP, 'runes', 'rasclady'), exist_ok=True)
    with open(os.path.join(WEBAPP, 'runes', 'rasclady', 'index.html'), 'w', encoding='utf-8') as f:
        f.write(out)

# ── main ─────────────────────────────────────────────────────────────────────

def main():
    build_index()
    build_rasclady()
    for i, r in enumerate(RUNES):
        prev = RUNES[i - 1] if i > 0 else None
        nxt = RUNES[i + 1] if i < len(RUNES) - 1 else None
        build_rune_page(r, prev, nxt)
    print(f'OK: index + rasclady + {len(RUNES)} rune pages, css v{CSS_V}')

if __name__ == '__main__':
    main()
