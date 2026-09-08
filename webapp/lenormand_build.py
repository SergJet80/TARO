#!/usr/bin/env python3
"""Генератор раздела Ленорман: каталог + 36 страниц карт в дизайне карточки (v2).

Python 3, только стандартная библиотека. Запуск:
    python путь/к/webapp/lenormand_build.py

Читает /home/serg/projects/lenormand/lenormand.json, пишет lenormand/index.html
и lenormand/NN-slug/index.html. Картинки lenormand/img/NN-slug.webp уже есть.
"""
from __future__ import annotations

import json
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "lenormand"
DATA = Path("/home/serg/projects/lenormand/lenormand.json")
SITE = "https://taro.jetserg.top"
CSS_V = "1.3"   # lenormand.css (в whitelist чекера)
SITE_V = "3.4"  # общий style.css

# Иконки сфер — порядок фиксирован (единый для всех карт).
SPHERE_ICONS = {
    "Стандартное": "✦",
    "В быту": "🏠",
    "Работа и бизнес": "💼",
    "Отношения": "❤",
    "Характеристика личности": "👤",
    "Предметы и места": "📍",
    "Необычные и буквальные проявления": "🎲",
    "Теневая сторона": "☾",
    "Практический совет": "★",
    "Примечание по времени": "⏳",
}
POL_CLASS = {"положительная": "pol-pos", "негативная": "pol-neg",
             "отрицательная": "pol-neg", "нейтральная": "pol-neu"}
POL_TEXT = {"положительная": "положительная", "негативная": "негативная",
            "отрицательная": "отрицательная", "нейтральная": "нейтральная"}


def esc(v, quote=False):
    return escape(str(v), quote=quote)


def load() -> tuple[list[dict], list[dict]]:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    cards, pairs = data["cards"], data["pairs"]
    if len(cards) != 36:
        raise ValueError(f"ожидалось 36 карт, найдено {len(cards)}")
    for c in cards:
        if not c.get("slug"):
            raise ValueError(f"карта {c.get('n')} без slug")
    return cards, pairs


def pairs_for(card_n: int, cards: list[dict], pairs: list[dict]) -> list[dict]:
    """Направленные сочетания: card первая (a=card) и card вторая (b=card)."""
    names = {c["n"]: c["name"] for c in cards}
    rows = []
    for p in pairs:
        if p["a"] == card_n:
            rows.append({"first": False, "other_n": p["b"], "other": names[p["b"]],
                         "refine": p.get("refine", ""), "people": p.get("people", "")})
        elif p["b"] == card_n:
            rows.append({"first": True, "other_n": p["a"], "other": names[p["a"]],
                         "refine": p.get("refine", ""), "people": p.get("people", "")})
    rows.sort(key=lambda r: r["other_n"])
    return rows


def nav(rel: str, active: str) -> str:
    items = [
        ("✦", "Таро", f"{rel}index.html", "index"),
        ("♄", "Астрология", f"{rel}astrology/index.html", "astrology"),
        ("ᚠ", "Руны", f"{rel}runes/index.html", "runes"),
        ("🂠", "Ленорман", f"{rel}lenormand/index.html", "lenormand"),
        ("❿", "Теория", f"{rel}numerology/index.html", "numerology"),
    ]
    rows = []
    for icon, label, href, key in items:
        a = ' class="mn-active"' if key == active else ""
        rows.append(f'    <a href="{href}"{a}><span class="mn-icon">{icon}</span> {label}</a>')
    return ('<nav class="main-nav" aria-label="Разделы">\n  <div class="main-nav-inner">\n'
            + "\n".join(rows) + "\n  </div>\n</nav>")


def document(title: str, description: str, url: str, body: str, schema_type: str,
             rel: str, og_img: str = "", css_rel: str = "../css/") -> str:
    structured = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "headline" if schema_type == "Article" else "name": title,
        "description": description,
        "url": url,
        "inLanguage": "ru",
    }
    schema = json.dumps(structured, ensure_ascii=False, indent=2).replace("<", "\\u003c")
    og = f'\n<meta property="og:image" content="{SITE}/lenormand/img/{esc(og_img)}">' if og_img else ""
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description, quote=True)}">
<link rel="canonical" href="{esc(url, quote=True)}">
<meta property="og:title" content="{esc(title, quote=True)}">
<meta property="og:description" content="{esc(description, quote=True)}">
<meta property="og:type" content="{'article' if schema_type == 'Article' else 'website'}">
<meta property="og:url" content="{esc(url, quote=True)}">{og}
<link rel="stylesheet" href="{rel}fonts/fonts.css?v={SITE_V}">
<link rel="stylesheet" href="{rel}css/style.css?v={SITE_V}">
<link rel="stylesheet" href="{css_rel}lenormand.css?v={CSS_V}">
<style>
/* ── v2: карточный лист в духе Таро ── */
.tarot-sheet {{ max-width: 760px; margin: 0 auto; background: linear-gradient(170deg, var(--ln-bg-card), #1b101d);
  border: 1px solid var(--ln-accent-dim); border-radius: 20px; padding: 26px 22px 30px;
  box-shadow: 0 18px 50px rgba(0,0,0,.45), 0 0 60px rgba(217,138,166,.1); }}
.sheet-head {{ display: flex; gap: 24px; align-items: center; margin-bottom: 20px; }}
.sheet-head .card-scene {{ flex-shrink: 0; }}
.sheet-head .card-scene img {{ width: 150px; aspect-ratio: 516/909; object-fit: cover; display: block;
  border-radius: 10px; border: 1px solid var(--ln-accent-dim); box-shadow: 0 6px 22px rgba(0,0,0,.55); }}
.head-info {{ min-width: 0; }}
.m-arcana {{ font-size: .8rem; letter-spacing: .25em; text-transform: uppercase; color: var(--ln-accent); margin-bottom: 4px; }}
.m-title {{ font-family: 'Cormorant Garamond', Georgia, serif; font-weight: 700;
  font-size: clamp(1.7rem, 5vw, 2.3rem); color: var(--ln-accent-bright); line-height: 1.15; margin: 0; }}
.card-number {{ display: block; font-size: 1.9rem; color: var(--ln-accent); margin-bottom: 4px; }}
.m-en {{ color: var(--ln-text-dim); font-style: italic; margin: 2px 0 8px; }}
.m-meta {{ font-size: .92rem; color: var(--ln-text-dim); margin: 0; }}
.m-meta b {{ color: var(--ln-text); font-weight: 500; }}
/* ── Вкладки (radio, без JS) ── */
.pos-tabs {{ display: flex; flex-wrap: wrap; gap: 6px; border-bottom: 1px solid var(--ln-accent-dim); margin-bottom: 18px; }}
.pos-tab {{ padding: 10px 20px; border: none; border-bottom: 2px solid transparent; color: var(--ln-text-dim);
  font-family: inherit; font-size: 1rem; cursor: pointer; transition: all .25s; background: none; display: block; }}
.pos-tab:hover {{ color: var(--ln-text); }}
.pos-state {{ position: absolute; opacity: 0; pointer-events: none; }}
.pos-state.s-vals:checked ~ .pos-tabs label[for="ln-vals"],
.pos-state.s-sph:checked ~ .pos-tabs label[for="ln-sph"] {{
  color: var(--ln-accent-bright); border-bottom-color: var(--ln-accent); text-shadow: 0 0 12px rgba(217,138,166,.4); }}
.pos-state.s-pairs:checked ~ .pos-tabs label[for="ln-pairs"] {{
  color: var(--ln-accent-bright); border-bottom-color: var(--ln-accent); text-shadow: 0 0 12px rgba(217,138,166,.4); }}
.pos-pane {{ display: none; animation: ln-fade .3s ease; }}
.pos-state.s-vals:checked ~ .pos-pane.pane-vals {{ display: block; }}
.pos-state.s-sph:checked ~ .pos-pane.pane-sph {{ display: block; }}
.pos-state.s-pairs:checked ~ .pos-pane.pane-pairs {{ display: block; }}
@keyframes ln-fade {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
/* ── Секции внутри вкладок ── */
.info-section {{ margin-bottom: 20px; }}
.info-section h3 {{ font-family: 'Cormorant Garamond', Georgia, serif; font-size: 1.22rem; font-weight: 600;
  letter-spacing: .04em; color: var(--ln-accent); margin-bottom: 7px; display: flex; align-items: center; gap: 9px; }}
.info-section h3::after {{ content: ''; flex: 1; height: 1px; background: linear-gradient(90deg, var(--ln-accent-dim), transparent); }}
.info-section p {{ white-space: pre-line; color: var(--ln-text); font-size: .98rem; line-height: 1.65; margin: 0; }}
.kw-row {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }}
.kw {{ padding: 5px 14px; border-radius: 999px; background: rgba(217,138,166,.12);
  border: 1px solid var(--ln-accent-dim); color: var(--ln-accent-bright); font-size: .85rem; }}
.short-value {{ font-family: 'Cormorant Garamond', Georgia, serif; font-size: 1.18rem; font-style: italic;
  color: var(--ln-accent-bright); padding: 12px 18px; border-left: 3px solid var(--ln-accent);
  background: rgba(217,138,166,.06); border-radius: 0 10px 10px 0; margin-bottom: 20px; line-height: 1.5; }}
.sig-note {{ color: var(--ln-text-dim); font-size: .95rem; line-height: 1.6; margin: 0 0 16px; }}
.sig-note b {{ color: var(--ln-accent); font-weight: 600; }}
/* ── Сочетания ── */
.pair-note {{ color: var(--ln-text-dim); font-size: .93rem; line-height: 1.6; margin: 0 0 14px; }}
.pair-list {{ list-style: none; padding: 0; margin: 0; }}
.pair-list li {{ padding: 12px 4px; border-top: 1px solid rgba(217,138,166,.14);
  line-height: 1.6; color: var(--ln-text); font-size: .95rem; }}
.pair-list li:first-child {{ border-top: none; }}
.pair-list strong {{ color: var(--ln-accent-bright); font-weight: 600; }}
.pair-people {{ color: var(--ln-accent); }}
/* ── Каталог ── */
.ln-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 16px; list-style: none; padding: 0; }}
.ln-grid li {{ min-width: 0; }}
/* ── Адаптив ── */
@media (max-width: 640px) {{
  .tarot-sheet {{ padding: 20px 14px 24px; }}
  .sheet-head {{ flex-wrap: nowrap; align-items: flex-start; gap: 12px; margin-bottom: 12px; }}
  .sheet-head .card-scene img {{ width: 104px; }}
  .pos-tab {{ padding: 9px 12px; font-size: .9rem; }}
  .pos-tab-tab3 {{ flex-basis: 100%; }}
  .ln-grid {{ grid-template-columns: repeat(auto-fill, minmax(104px, 1fr)); gap: 10px; }}
}}
</style>
<script type="application/ld+json">
{schema}
</script>
<!-- Microsoft Clarity -->
<script>
    (function(c,l,a,r,i,t,y){{
        c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};
        t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i+"?ref=bwt";
        y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
    }})(window, document, "clarity", "script", "yejlmmd6nr");
</script>
</head>
<body>
<div class="stars" aria-hidden="true"></div>
<div class="stars stars2" aria-hidden="true"></div>
{nav(rel, 'lenormand')}
{body}
<footer class="site-footer">
  <p>Личный справочник · не официальный доклад и не исследовательская статья · JeT</p>

<div class="footer-contact">
  <a href="https://t.me/JetGres" target="_blank" rel="noopener">Telegram: @JetGres</a>
  <a href="mailto:jetjarret@gmail.com">jetjarret@gmail.com</a>
  <span class="fc-sep" aria-hidden="true">·</span>
  <span class="fc-support">Поддержать проект:
    <a href="https://donatello.to/JeTJarret" target="_blank" rel="noopener">Donatello</a> ·
    <a href="https://www.privat24.ua/send/4x8ww" target="_blank" rel="noopener">Privat24</a>
  </span>
</div>
</footer>
</body>
</html>
"""


def render_card(card: dict, cards: list[dict], pairs: list[dict]) -> str:
    n = int(card["n"])
    slug = card["slug"]
    name = card["name"]
    img = f"{slug}-card.webp" if False else None  # имя файла строим ниже по номеру
    img_name = f"{n:02d}-{slug}.webp"
    idx = next(i for i, c in enumerate(cards) if c["n"] == card["n"])
    prev, nxt = cards[(idx - 1) % 36], cards[(idx + 1) % 36]
    title = f"{name} — карта Ленорман №{n}: значение и сочетания"
    description = (f"Карта Ленорман №{n} {name} ({card['insert']}): значения по сферам жизни, "
                   f"сигнификатор, время и 35 сочетаний с другими картами оракула.")
    url = f"{SITE}/lenormand/{n:02d}-{slug}/"
    pol = POL_TEXT.get(card.get("polarity", ""), card.get("polarity", ""))

    # Вкладка «Значения»
    keywords = "".join(f'<span class="kw">{esc(w.strip())}</span>'
                       for w in card["keywords"].split(",") if w.strip())
    vals = [f'<div class="kw-row">{keywords}</div>']
    vals.append(f'<div class="info-section"><h3><span aria-hidden="true">✦</span> Ключевые значения</h3>'
                f'<p>{esc(card["keywords"])}</p></div>')
    vals.append(f'<p class="sig-note"><b>Сигнификатор:</b> {esc(card["significator"])}</p>')
    vals.append(f'<div class="info-section"><h3><span aria-hidden="true">🂠</span> Игральная карта и факты</h3>'
                f'<p>{esc(name)} — {esc(card["insert"])}. Полярность: {esc(pol)}. '
                f'Время: {esc(card["time"])}</p></div>')
    vals_html = "\n".join(vals)

    # Вкладка «Сферы»
    sph = []
    std = next((x for t, x in card["spheres"] if t == "Стандартное"), "")
    if std:
        sph.append(f'<p class="short-value">{esc(std)}</p>')
    for t, x in card["spheres"]:
        if t == "Стандартное":
            continue
        icon = SPHERE_ICONS.get(t, "✧")
        sph.append(f'<div class="info-section"><h3><span aria-hidden="true">{icon}</span> {esc(t)}</h3>'
                   f'<p>{esc(x)}</p></div>')
    sph_html = "\n".join(sph)

    # Вкладка «Сочетания»
    rows = pairs_for(n, cards, pairs)
    li = []
    for r in rows:
        pair_title = f"{name} + {r['other']}" if not r["first"] else f"{r['other']} + {name}"
        people = (f' <span class="pair-people">Люди:</span> {esc(r["people"])}'
                  if r.get("people") else "")
        li.append(f'<li><strong>{esc(pair_title)}</strong> — {esc(r["refine"])}{people}</li>')
    pairs_note = (f"{esc(name)} задаёт тему, вторая карта уточняет её. Всего 35 направленных сочетаний; "
                  f"пары «{esc(name)} + X» и «X + {esc(name)}» могут читаться по-разному.")
    pairs_html = (f'<p class="pair-note">{pairs_note}</p>'
                  f'<ul class="pair-list">{"".join(li)}</ul>')

    body = f"""<main class="ln-wrap ln-card-page">
<nav class="card-crumbs" aria-label="Хлебные крошки"><a href="../">Ленорман</a> / <span aria-current="page">{esc(name)}</span></nav>
<article class="tarot-sheet">
<header class="sheet-head">
<div class="card-scene"><img src="../img/{img_name}" alt="Карта Ленорман №{n} {esc(name)}" width="150" height="264"></div>
<div class="head-info">
<p class="m-arcana">Оракул Ленорман · карта №{n}</p>
<h1 class="m-title"><span class="card-number">{n:02d}</span>{esc(name)}</h1>
<p class="m-en">{esc(card['insert'])}</p>
<p class="m-meta">Полярность: <b>{esc(pol)}</b> &nbsp;·&nbsp; Время: <b>{esc(card['time'])}</b></p>
</div>
</header>
<input class="pos-state s-vals" type="radio" name="lnpos" id="ln-vals" checked>
<input class="pos-state s-sph" type="radio" name="lnpos" id="ln-sph">
<input class="pos-state s-pairs" type="radio" name="lnpos" id="ln-pairs">
<div class="pos-tabs" role="tablist" aria-label="Разделы карты">
<label class="pos-tab" for="ln-vals">Значения</label>
<label class="pos-tab" for="ln-sph">Сферы жизни</label>
<label class="pos-tab pos-tab-tab3" for="ln-pairs">Сочетания (35)</label>
</div>
<div class="pos-pane pane-vals" id="pane-vals" role="tabpanel">
{vals_html}
</div>
<div class="pos-pane pane-sph" id="pane-sph" role="tabpanel">
{sph_html}
</div>
<div class="pos-pane pane-pairs" id="pane-pairs" role="tabpanel">
{pairs_html}
</div>
<nav class="ln-pag" aria-label="Навигация по картам">
  <a href="../{int(prev['n']):02d}-{prev['slug']}/">← {int(prev['n']):02d} {esc(prev['name'])}</a>
  <a href="../{int(nxt['n']):02d}-{nxt['slug']}/">{int(nxt['n']):02d} {esc(nxt['name'])} →</a>
</nav>
</article>
</main>"""
    return document(title, description, url, body, "Article", "../../", img_name)


def render_index(cards: list[dict]) -> str:
    tiles = []
    for c in cards:
        n = int(c["n"])
        pol = POL_CLASS.get(c.get("polarity", ""), "pol-neu")
        tiles.append(
            f'<li><a class="ln-tile {pol}" href="{n:02d}-{c["slug"]}/">'
            f'<img src="img/{n:02d}-{c["slug"]}.webp" alt="Карта Ленорман {n:02d} {esc(c["name"])}" loading="lazy">'
            f'<span class="ln-tile-num">{n:02d}</span>'
            f'<span class="ln-tile-name">{esc(c["name"])}</span></a></li>')
    title = "Ленорман — значения 36 карт оракула"
    description = ("Значения всех 36 карт оракула Ленорман: по сферам жизни, сигнификаторы, "
                   "полярность, время и 1260 сочетаний пар.")
    url = f"{SITE}/lenormand/"
    intro = ("Оракулы Ленорман — это уникальные колоды карт, которые берут своё начало в XVIII веке, и обязаны "
             "своей популярностью знаменитой французской гадалке Марии Ленорман. Она использовала карты для "
             "предсказаний судьбоносных событий и давала консультации известным личностям своего времени. "
             "Стандартная колода Ленорман состоит из 36 карт, каждая из которых содержит символы, легко "
             "интерпретируемые даже теми, кто только начинает знакомство с миром гадания. Эти символы — Лиса, "
             "Корабль, Солнце, Дерево и другие — представляют собой архетипические образы, связанные с "
             "повседневной жизнью. Карты Ленорман отличаются своей доступностью и прямолинейностью: в отличие "
             "от более сложных систем, таких как Таро, они дают быстрые и точные ответы, фокусируясь на реальных "
             "событиях и практических советах.")
    body = f"""<main class="ln-wrap">
<header class="site-header">
  <div class="header-inner">
    <h1 class="site-title"><span class="title-star">🂠</span> Ленорман <span class="title-sub">Оракул · 36 карт</span></h1>
    <p class="site-tagline">значения по сферам · время · 1260 сочетаний пар</p>
    <p class="ln-intro">{esc(intro)}</p>
  </div>
</header>
<p class="ln-note">Полярность карт — рабочая подсказка, а не приговор: соседние карты и вопрос меняют тон прочтения.</p>
<ol class="ln-grid">
{chr(10).join(tiles)}
</ol>
</main>"""
    return document(title, description, url, body, "CollectionPage", "../", css_rel="css/")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    cards, pairs = load()
    pages: dict[str, str] = {"index.html": render_index(cards)}
    for c in cards:
        n = int(c["n"])
        pages[f"{n:02d}-{c['slug']}/index.html"] = render_card(c, cards, pairs)
    if len(pages) != 37:
        raise ValueError(f"ожидалось 37 страниц, получено {len(pages)}")
    for rel, html in pages.items():
        path = OUT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8", newline="\n")
    print(f"OK: Ленорман v2 — {len(pages)} страниц (каталог + 36 карт).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
