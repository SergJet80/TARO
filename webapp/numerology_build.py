#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор раздела «Нумерология» (системное чтение числовых Младших Арканов).
Источник контента: data/numerology.json (из docx, без правок смысла).
Запуск:  python3 numerology_build.py   (из каталога webapp/)
Создаёт: numerology/index.html (одна страница, 4 вкладки)
"""
import json
import html
import os
import re

WEBAPP = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(WEBAPP, 'data', 'numerology.json')
CSS_V = '3.0'

with open(DATA, encoding='utf-8') as f:
    SRC = json.load(f)

def esc(s):
    return html.escape(s or '', quote=False)

def bold_inline(text):
    parts = re.split(r'(\*\*.+?\*\*)', text or '')
    out = []
    for p in parts:
        if p.startswith('**') and p.endswith('**'):
            out.append('<strong>' + esc(p[2:-2]) + '</strong>')
        else:
            out.append(esc(p))
    return ''.join(out)

SUIT_ICON = {'Жезлы': '🜂', 'Мечи': '🜁', 'Кубки': '🜄', 'Пентакли': '🜃'}

def table_html(rows, cls='num-table'):
    head, body = rows[0], rows[1:]
    t = [f'<div class="num-table-wrap"><table class="{cls}"><thead><tr>']
    t += [f'<th>{bold_inline(c)}</th>' for c in head]
    t.append('</tr></thead><tbody>')
    for row in body:
        t.append('<tr>' + ''.join(f'<td>{bold_inline(c)}</td>' for c in row) + '</tr>')
    t.append('</tbody></table></div>')
    return ''.join(t)

def callout(text):
    return f'<div class="num-callout">{bold_inline(text)}</div>'

def card_meaning(text):
    """'Туз Жезлов — «Я хочу». ...' → карточка."""
    m = re.match(r'^([^—]+)—\s*(.+)$', text, re.S)
    if m:
        return (f'<div class="num-card"><div class="num-card-head">{esc(m.group(1).strip())}</div>'
                f'<div class="num-card-body">{bold_inline(m.group(2).strip())}</div></div>')
    return f'<div class="num-card"><div class="num-card-body">{bold_inline(text)}</div></div>'

# ── вкладки ──────────────────────────────────────────────────────────────────

def tab_system():
    s = []
    s.append('<section class="sign-sec"><h2 class="sec-title">Системное чтение числовых Младших Арканов</h2>'
             + ''.join(f'<p>{bold_inline(p)}</p>' for p in SRC['intro']['lead']) + '</section>')
    s.append('<section class="sign-sec"><h2 class="sec-title">Ключевая формула</h2>'
             + callout(SRC['intro']['formula'])
             + '<p class="num-layer-note">Формула не является математическим умножением — это способ соединить два слоя смысла.</p>'
             + ''.join(f'<div class="num-card"><div class="num-card-body">{bold_inline(re.sub(r"^• ", "", p))}</div></div>'
                       for p in SRC['intro']['section2']) + '</section>')
    s.append('<section class="sign-sec"><h2 class="sec-title">Зачем нужна нумерология Младших Арканов</h2>'
             + ''.join(f'<p>{bold_inline(p)}</p>' for p in SRC['intro']['section1']) + '</section>')
    s.append('<section class="sign-sec"><h2 class="sec-title">Четыре масти как четыре сферы жизни</h2>'
             + table_html(SRC['suits']['table'])
             + ''.join(f'<p>{bold_inline(p)}</p>' for p in SRC['suits']['note'])
             + ''.join(f'<p class="num-layer-note">{esc(p)}</p>' for p in SRC['suits']['minor'][:1]) + '</section>')
    s.append('<section class="sign-sec"><h2 class="sec-title">Десять чисел как один жизненный цикл</h2>'
             + callout(SRC['cycle']['line'])
             + table_html(SRC['cycle']['table']) + '</section>')
    return ('✦', 'Система', ''.join(s))

def tab_numbers():
    s = []
    for n in SRC['numbers']:
        head = f"<h2 class=\"sec-title\">{n['num']}. {esc(n['title'])} — {esc(n['subtitle'])}</h2>"
        body = ''.join(f'<p>{bold_inline(p)}</p>' for p in n['text'])
        cards = ''.join(card_meaning(c) for c in n['cards'])
        rem = callout('Как запомнить: ' + n['remember']) if n['remember'] else ''
        s.append(f'<section class="sign-sec num-num-sec">{head}{body}{cards}{rem}</section>')
    return ('❿', 'Числа 1–10', ''.join(s))

def tab_cheatsheet():
    s = []
    s.append('<section class="sign-sec"><h2 class="sec-title">Шпаргалка: 40 карт через одну систему</h2>'
             '<p>Скелет значения, который легко восстановить в памяти. Не заменяет подробные трактовки.</p>'
             + table_html(SRC['cheatsheet'], cls='num-table num-cheat') + '</section>')
    s.append('<section class="sign-sec"><h2 class="sec-title">Практический алгоритм: значение без зубрёжки</h2>'
             + '<ol class="num-ol">' + ''.join(f'<li>{bold_inline(step)}</li>' for step in SRC['algorithm']) + '</ol></section>')
    s.append('<section class="sign-sec"><h2 class="sec-title">Примеры системного разбора</h2>'
             + ''.join(card_meaning(e) for e in SRC['examples']) + '</section>')
    s.append('<section class="sign-sec"><h2 class="sec-title">Почему одинаковое число даёт разные карты</h2>'
             + ''.join(f'<div class="num-card"><div class="num-card-body">{bold_inline(re.sub(r"^• ", "", p))}</div></div>'
                       for p in SRC['whyDifferent']) + '</section>')
    return ('▦', 'Шпаргалка', ''.join(s))

def tab_major():
    s = []
    s.append('<section class="sign-sec"><h2 class="sec-title">Связь чисел со Старшими Арканами</h2>'
             '<p class="num-layer-note">Полезная ассоциация, но не жёсткое правило: Старший Аркан — общий архетип, числовая карта — его бытовое проявление в масти.</p>'
             + ''.join(f'<div class="num-card"><div class="num-card-body">{bold_inline(re.sub(r"^• ", "", p))}</div></div>'
                       for p in SRC['majorLinks'])
             + callout(SRC['eightNote']) + '</section>')
    s.append('<section class="sign-sec"><h2 class="sec-title">Что даёт этот подход на практике</h2>'
             + ''.join(f'<div class="num-card"><div class="num-card-body">{bold_inline(re.sub(r"^• ", "", p))}</div></div>'
                       for p in SRC['practice']) + '</section>')
    src_html = []
    for src in SRC['sources']:
        t = src['text']
        t = re.sub(r'\s*Открыть источник\s*$', '', t)
        src_html.append(f'<p class="num-src">{esc(t)}</p>')
    s.append('<section class="sign-sec"><h2 class="sec-title">Источники и примечания</h2>'
             '<p class="num-layer-note">Основной материал — систематизация лекции по числовым Младшим Арканам; реконструированные фрагменты сверены с перечисленными источниками.</p>'
             + ''.join(src_html)
             + '<p class="num-layer-note">Таро и нумерологические соответствия — символическая и эзотерическая традиция, описываемая как учебная система чтения карт, а не научно подтверждённый способ предсказания.</p>'
             '</section>')
    return ('☾', 'Старшие и итоги', ''.join(s))

# ── page ─────────────────────────────────────────────────────────────────────

def shell(title, desc, css_prefix, nav_prefix, active, body):
    return f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='0.9em' font-size='90'%3E%E2%9D%BF%3C/text%3E%3C/svg%3E">
<link rel="stylesheet" href="{css_prefix}fonts/fonts.css?v={CSS_V}">
<link rel="stylesheet" href="{css_prefix}css/style.css?v={CSS_V}">
<link rel="stylesheet" href="{css_prefix}css/astrology.css?v={CSS_V}">
<link rel="stylesheet" href="{css_prefix}css/runes.css?v={CSS_V}">
<link rel="stylesheet" href="{css_prefix}css/numerology.css?v={CSS_V}">
</head>

<body>

<div class="stars" aria-hidden="true"></div>
<div class="stars stars2" aria-hidden="true"></div>

{body}
</body>
</html>
'''

def build_index():
    tabs = [tab_system(), tab_numbers(), tab_cheatsheet(), tab_major()]
    btns = '\n'.join(
        f'      <button class="rt-btn{" active" if i == 0 else ""}" data-tab="{i}">{icon} {esc(label)}</button>'
        for i, (icon, label, _) in enumerate(tabs))
    panes = '\n'.join(
        f'    <div class="rt-pane{" active" if i == 0 else ""}" data-pane="{i}">\n{html_}\n    </div>'
        for i, (icon, label, html_) in enumerate(tabs))
    body = f'''<nav class="main-nav" aria-label="Разделы">
  <div class="main-nav-inner">
    <a href="{'../'}index.html"><span class="mn-icon">✦</span> Таро</a>
    <a href="{'../'}astrology/index.html"><span class="mn-icon">♄</span> Астрология</a>
    <a href="{'../'}runes/index.html"><span class="mn-icon">ᚠ</span> Руны</a>
    <a href="{'../'}numerology/index.html" class="mn-active"><span class="mn-icon">❿</span> Теория</a>
  </div>
</nav>

<header class="site-header">
  <div class="header-inner">
    <h1 class="site-title"><span class="title-star">❿</span> Нумерология <span class="title-sub">и масти Таро</span></h1>
    <p class="site-tagline">Системное чтение числовых Младших Арканов: 10 этапов × 4 сферы = 40 карт</p>
  </div>
</header>

<main class="sign-page rune-page">
  <nav class="rune-tabs" aria-label="Разделы">
{btns}
  </nav>

  <div class="sign-blocks" id="numPanes">
{panes}
  </div>

  <p class="astro-disclaimer">Материал — учебная система чтения числовых Младших Арканов (традиция Rider–Waite–Smith и современные системные школы). Описанное — символическая традиция, а не научно подтверждённый способ предсказания. Материалы носят справочный и развлекательный характер.</p>

  <nav class="sign-nav" aria-label="Навигация">
    <a class="sign-nav-btn back" href="../index.html">✦ Все карты Таро</a>
  </nav>
</main>

<footer class="site-footer">
  <p>Нумерология и масти Таро — системное чтение Младших Арканов</p>
  <p class="footer-note">Материалы носят справочный и развлекательный характер</p>
</footer>

<script>
(function() {{
  var bar = document.querySelector('.rune-tabs');
  var btns = Array.prototype.slice.call(bar.querySelectorAll('.rt-btn'));
  var panes = Array.prototype.slice.call(document.querySelectorAll('#numPanes .rt-pane'));
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
    out = shell('Нумерология и масти Таро — системное чтение Младших Арканов | Справочник',
                'Как читать 40 числовых Младших Арканов как систему: число задаёт этап, масть — сферу. Цикл из 10 этапов, 4 масти, шпаргалка 10×4 и алгоритм чтения без зубрёжки.',
                '../', '../', 'numerology', body)
    os.makedirs(os.path.join(WEBAPP, 'numerology'), exist_ok=True)
    with open(os.path.join(WEBAPP, 'numerology', 'index.html'), 'w', encoding='utf-8') as f:
        f.write(out)

def main():
    build_index()
    print(f'OK: numerology/index.html, css v{CSS_V}')

if __name__ == '__main__':
    main()
