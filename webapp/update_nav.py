#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Обновить main-nav и версию CSS на всех HTML-страницах сайта."""
import os, re

WEBAPP = os.path.dirname(os.path.abspath(__file__))
CSS_V = '3.0'

NAV = '''<nav class="main-nav" aria-label="Разделы">
  <div class="main-nav-inner">
{items}
  </div>
</nav>'''

def nav_html(rel_prefix, active):
    items = [
        ('✦', 'Таро', f'{rel_prefix}index.html', 'index'),
        ('♄', 'Астрология', f'{rel_prefix}astrology/index.html', 'astrology'),
        ('ᚠ', 'Руны', f'{rel_prefix}runes/index.html', 'runes'),
        ('❿', 'Теория', f'{rel_prefix}numerology/index.html', 'numerology'),
    ]
    rows = []
    for icon, label, href, key in items:
        a = ' class="mn-active"' if key == active else ''
        rows.append(f'    <a href="{href}"{a}><span class="mn-icon">{icon}</span> {label}</a>')
    return NAV.format(items='\n'.join(rows))

def active_for(rel):
    if rel.startswith('astrology/'): return 'astrology'
    if rel.startswith('runes/'): return 'runes'
    if rel.startswith('numerology/'): return 'numerology'
    return 'index'

changed = 0
checked = 0
broken_pages = []
for root, dirs, files in os.walk(WEBAPP):
    dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', 'research'}]
    for fn in files:
        if not fn.endswith('.html'):
            continue
        path = os.path.join(root, fn)
        rel = os.path.relpath(path, WEBAPP).replace(os.sep, '/')
        depth = rel.count('/')
        prefix = '../' * depth
        active = active_for(rel)
        with open(path, encoding='utf-8') as f:
            html_old = f.read()
        html_new = html_old
        # nav
        m = re.search(r'<nav class="main-nav".*?</nav>', html_new, re.S)
        if m:
            html_new = html_new[:m.start()] + nav_html(prefix, active) + html_new[m.end():]
        else:
            broken_pages.append(rel + ' (no nav)')
        # css version bump
        html_new = re.sub(r'(\.css\?v=)[\d.]+', rf'\g<1>{CSS_V}', html_new)
        if html_new != html_old:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html_new)
            changed += 1
        checked += 1

print(f'checked={checked} changed={changed} problems={broken_pages}')
