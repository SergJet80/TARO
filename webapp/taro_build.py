#!/usr/bin/env python3
"""Build the English Tarot SPA and its pre-rendered hidden card pages."""
from __future__ import annotations

from copy import deepcopy
from html import escape
import hashlib
import json
from pathlib import Path
import re
import sys

import cards_build


ROOT = Path(__file__).resolve().parent
I18N = ROOT / "data" / "i18n"
MAIN_OUT = ROOT / "en" / "taro"
CARDS_OUT = ROOT / "en" / "cards"
SITE = "https://taro.jetserg.top"
SOURCE_FILES = (
    "major-0-10.json", "major-11-21.json", "wands.json",
    "cups.json", "swords.json", "pentacles.json",
)
CYRILLIC = re.compile(r"[А-Яа-яЁё]")


def load_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")


def source_cards() -> list[dict]:
    cards: list[dict] = []
    for filename in SOURCE_FILES:
        cards.extend(load_json(ROOT / "data" / filename))
    if len(cards) != 78 or len({card["id"] for card in cards}) != 78:
        raise ValueError("Tarot source must contain 78 unique cards")
    return cards


def same_shape(source, translated, path="") -> None:
    if isinstance(source, dict):
        if not isinstance(translated, dict) or set(source) != set(translated):
            raise ValueError(f"Translation shape differs at {path or '<root>'}")
        for key in source:
            same_shape(source[key], translated[key], f"{path}.{key}" if path else key)
    elif isinstance(source, list):
        if not isinstance(translated, list) or len(source) != len(translated):
            raise ValueError(f"Translation list differs at {path}")
        for index, (left, right) in enumerate(zip(source, translated)):
            same_shape(left, right, f"{path}[{index}]")
    elif isinstance(source, str):
        if not isinstance(translated, str) or (source.strip() and not translated.strip()):
            raise ValueError(f"Missing translated text at {path}")
    elif source is None:
        if translated is not None:
            raise ValueError(f"Null value changed at {path}")
    elif type(source) is not type(translated):
        raise ValueError(f"Value type differs at {path}")


def localized_cards() -> list[dict]:
    source = source_cards()
    translated = load_json(I18N / "tarot-classic-en.json")["cards"]
    if set(translated) != {card["id"] for card in source}:
        raise ValueError("Classic Tarot translation IDs do not match the Russian source")
    result = []
    for card in source:
        en = translated[card["id"]]
        for position in ("upright", "reversed"):
            same_shape(card[position], en[position], f"{card['id']}.{position}")
        item = deepcopy(card)
        item["name_ru"] = en["name"]
        item["name_en"] = ""
        item["element"] = en["element"]
        item["astro"] = en["astro"]
        item["upright"] = en["upright"]
        item["reversed"] = en["reversed"]
        result.append(item)
    return result


def localized_roman() -> dict[str, dict]:
    source = cards_build.load_roman()
    translated = load_json(I18N / "tarot-roman-en.json")["cards"]
    if set(source) != set(translated):
        raise ValueError("School translation IDs do not match the Russian source")
    for card_id in source:
        # The five Russian section names intentionally become stable English keys.
        normalized = deepcopy(source[card_id])
        normalized["full"] = {
            {
                "Суть карты": "Essence of the card",
                "Прямое положение": "Upright position",
                "Негативное значение": "Negative meaning",
                "Акценты и фишки школы": "School emphases and distinctive points",
                "Ключевые слова": "Keywords",
            }.get(key, key): value for key, value in normalized["full"].items()
        }
        same_shape(normalized, translated[card_id], card_id)
    return translated


def apply_replacements(value: str, ui: dict) -> str:
    for source, target in sorted(ui["replacements"].items(), key=lambda item: len(item[0]), reverse=True):
        value = value.replace(source, target)
    return value


def fix_generated_scripts(html: str) -> str:
    """The legacy card renderer emits doubled braces in its Clarity snippet."""
    def repair(match: re.Match) -> str:
        return match.group(0).replace("{{", "{").replace("}}", "}")
    return re.sub(r'<!-- Microsoft Clarity -->.*?</script>', repair, html, count=1, flags=re.S)


def set_meta(html: str, *, title: str, description: str, url: str, page_type: str, image: str = "") -> str:
    html = re.sub(r"<title>.*?</title>", f"<title>{escape(title)}</title>", html, count=1, flags=re.S)
    html = re.sub(r'<meta name="description" content="[^"]*">',
                  f'<meta name="description" content="{escape(description, quote=True)}">', html, count=1)
    html = re.sub(r'<link rel="canonical" href="[^"]*">',
                  f'<link rel="canonical" href="{url}">', html, count=1)
    for prop, content in (("og:title", title), ("og:description", description), ("og:url", url)):
        html = re.sub(fr'<meta property="{re.escape(prop)}" content="[^"]*">',
                      f'<meta property="{prop}" content="{escape(content, quote=True)}">', html, count=1)
    structured = {
        "@context": "https://schema.org",
        "@type": page_type,
        "headline" if page_type == "Article" else "name": title,
        "description": description,
        "url": url,
        "inLanguage": "en",
    }
    schema = json.dumps(structured, ensure_ascii=False, indent=2).replace("<", "\\u003c")
    html = re.sub(
        r'(<script type="application/ld\+json">).*?(</script>)',
        lambda match: match.group(1) + "\n" + schema + "\n" + match.group(2),
        html, count=1, flags=re.S,
    )
    if image:
        html = re.sub(r'<meta property="og:image" content="[^"]*">',
                      f'<meta property="og:image" content="{image}">', html, count=1)
    return html


def configure_card_renderer(cards: list[dict], ui: dict) -> dict[str, dict]:
    editorial_data = load_json(I18N / "tarot-editorial-en.json")["cards"]
    if set(editorial_data) != set(cards_build.EDITORIAL):
        raise ValueError("Editorial translation IDs do not match the source")
    cards_build.EDITORIAL = {
        card_id: (
            item["slug"], item["symbol"], item["label"], item["idea"],
            item["intro"], item["advice"], tuple(item["questions"]),
        ) for card_id, item in editorial_data.items()
    }
    cards_build.SUIT_RU = ui["suits"]
    cards_build.SUIT_ELEMENT = ui["elements"]
    cards_build.POSITION_SECTIONS = tuple(
        (field, icon, ui["sections"][field])
        for field, icon, _title in cards_build.POSITION_SECTIONS
    )
    cards_build.ROMAN_SECTIONS_FULL = tuple(
        (title, icon) for title, icon in (
            ("Essence of the card", "✧"),
            ("Upright position", "☀"),
            ("Negative meaning", "☾"),
            ("School emphases and distinctive points", "★"),
            ("Keywords", "🗝"),
        )
    )
    cards_build.meta_description = lambda card, _cards: ui["card"]["description"].format(name=card["name_ru"])
    return localized_roman()


def finish_card_page(html: str, card: dict, ui: dict) -> str:
    slug = cards_build.slug_for(card)
    title = ui["card"]["title"].format(name=card["name_ru"])
    description = ui["card"]["description"].format(name=card["name_ru"])
    url = f"{SITE}/en/cards/{slug}.html"
    html = apply_replacements(html, ui)
    html = fix_generated_scripts(html)
    html = html.replace('<html lang="ru">', '<html lang="en">')
    html = html.replace('href="../css/', 'href="../../css/')
    html = html.replace('src="../img/', 'src="../../img/')
    html = html.replace(f'{SITE}/cards/{slug}.html', url)
    html = html.replace(
        '<a href="index.html" class="mn-active">Cards</a>',
        '<a href="index.html" class="mn-active" style="display:none" aria-hidden="true">Cards</a>',
    )
    html = html.replace(
        f'<nav class="card-crumbs" aria-label="Breadcrumbs"><a href="../index.html">Tarot</a> / <a href="index.html">Cards</a> / <span aria-current="page">{escape(card["name_ru"])}</span></nav>',
        f'<nav class="card-crumbs" aria-label="Breadcrumbs"><a href="../taro/index.html">Tarot</a> / <span aria-current="page">{escape(card["name_ru"])}</span></nav>',
    )
    html = html.replace('href="../index.html"', 'href="../taro/index.html"')
    html = html.replace('href="../spreads.html"', 'href="../../spreads.html"')
    # Переключатель языка: EN-карта ссылается на RU-карту
    html = html.replace('href="../en/taro/index.html"', f'href="../../cards/{slug}.html"')
    html = html.replace('aria-label="Switch to English"', 'aria-label="Switch to Russian"')
    html = html.replace('hreflang="en" lang="en"', 'hreflang="ru" lang="ru"')
    html = html.replace('>EN | RU<', '>RU | EN<')
    # Golden Dawn титул: в EN показываем только оригинал (RU «eng — перевод» не нужен)
    html = re.sub(r'<p class="gd-title">«([^<]+)»\s—\s[^<]*</p>', r'<p class="gd-title">«\1»</p>', html)
    html = set_meta(
        html, title=title, description=description, url=url, page_type="Article",
        image=f"{SITE}/img/cards/{card['img']}",
    )
    return html


def finish_catalog(html: str, ui: dict) -> str:
    title = ui["card"]["catalog_title"]
    description = ui["card"]["catalog_description"]
    url = f"{SITE}/en/cards/"
    html = apply_replacements(html, ui)
    html = fix_generated_scripts(html)
    html = html.replace('<html lang="ru">', '<html lang="en">')
    html = html.replace('href="../css/', 'href="../../css/')
    html = html.replace('src="../img/', 'src="../../img/')
    html = html.replace(
        '<a href="index.html" class="mn-active">Cards</a>',
        '<a href="index.html" class="mn-active" style="display:none" aria-hidden="true">Cards</a>',
    )
    html = html.replace('href="../index.html"', 'href="../taro/index.html"')
    html = html.replace('href="../spreads.html"', 'href="../../spreads.html"')
    # Переключатель языка: EN-каталог ссылается на RU-каталог
    html = html.replace('href="../en/taro/index.html"', 'href="../../cards/index.html"')
    html = html.replace('aria-label="Switch to English"', 'aria-label="Switch to Russian"')
    html = html.replace('hreflang="en" lang="en"', 'hreflang="ru" lang="ru"')
    html = html.replace('>EN | RU<', '>RU | EN<')
    html = re.sub(r'<p class="gd-title">«([^<]+)»\s—\s[^<]*</p>', r'<p class="gd-title">«\1»</p>', html)
    html = html.replace(f"{SITE}/cards/", url)
    return set_meta(html, title=title, description=description, url=url, page_type="CollectionPage")


def seo_block(ui: dict) -> str:
    main = ui["main"]
    structured = json.dumps({
        "@context": "https://schema.org", "@type": "CollectionPage",
        "name": main["title"], "description": main["description"],
        "url": main["url"], "inLanguage": "en",
    }, ensure_ascii=False, indent=2).replace("<", "\\u003c")
    return (
        f'<link rel="canonical" href="{main["url"]}">\n'
        f'<meta property="og:title" content="{escape(main["title"], quote=True)}">\n'
        f'<meta property="og:description" content="{escape(main["description"], quote=True)}">\n'
        '<meta property="og:type" content="website">\n'
        f'<meta property="og:url" content="{main["url"]}">\n'
        f'<meta property="og:image" content="{main["image"]}">\n'
        '<link rel="alternate" hreflang="ru" href="https://taro.jetserg.top/">\n'
        f'<link rel="alternate" hreflang="en" href="{main["url"]}">\n'
        '<link rel="alternate" hreflang="x-default" href="https://taro.jetserg.top/">\n'
        f'<script type="application/ld+json">\n{structured}\n</script>'
    )


def build_main(cards: list[dict], roman: dict[str, dict], ui: dict) -> None:
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    html = apply_replacements(html, ui)
    html = html.replace('<html lang="ru">', '<html lang="en">')
    html = re.sub(r"<title>.*?</title>", f'<title>{escape(ui["main"]["title"])}</title>', html, count=1)
    html = re.sub(r'<meta name="description" content="[^"]*">',
                  f'<meta name="description" content="{escape(ui["main"]["description"], quote=True)}">', html, count=1)
    html = html.replace('</head>', seo_block(ui) + '\n</head>', 1)
    html = html.replace('href="fonts/', 'href="../../fonts/')
    html = html.replace('href="css/', 'href="../../css/')
    for section in ("lenormand", "astrology", "runes", "numerology", "cards"):
        html = html.replace(f'href="{section}/', f'href="../{section}/')
    # EN spreads.html пока не переведён (planned) — ведём на RU-атлас
    html = html.replace('href="spreads.html"', 'href="../../spreads.html"')  # webapp/spreads.html (RU-атлас)
    # Языковой переключатель: EN-SPA ссылается на RU главную (/)
    html = html.replace('href="en/taro/index.html"', 'href="../../index.html"')
    html = html.replace('aria-label="Switch to English"', 'aria-label="Switch to Russian"')
    html = html.replace('hreflang="en" lang="en"', 'hreflang="ru" lang="ru"')
    html = html.replace('>EN | RU<', '>RU | EN<')
    html = html.replace('src="js/data.js', 'src="js/data.js')
    write_text(MAIN_OUT / "index.html", html)

    js_cards = "const TARO_CARDS = " + json.dumps(cards, ensure_ascii=False, separators=(",", ":")) + ";\n"
    js_roman = "const ROMAN_SCHOOL = " + json.dumps(list(roman.values()), ensure_ascii=False, separators=(",", ":")) + ";\n"
    write_text(MAIN_OUT / "js" / "data.js", js_cards)
    write_text(MAIN_OUT / "js" / "data_roman.js", js_roman)

    app = (ROOT / "js" / "app.js").read_text(encoding="utf-8")
    app = apply_replacements(app, ui)
    # Golden Dawn титул в EN: без «— перевод»
    app = app.replace('«${p.gd.title_en}» — ${p.gd.title_ru}', '«${p.gd.title_en}»')
    app = app.replace('img/cards/${c.img}', '../../img/cards/${c.img}')
    app = app.replace('img/cards/${card.img}', '../../img/cards/${card.img}')
    app = app.replace('href="/cards/${cardPage}.html"', 'href="/en/cards/${cardPage}.html"')
    slug_declaration = re.search(r"const CARD_PAGE_SLUGS = \{.*?\};", app, re.S)
    if not slug_declaration:
        raise ValueError("Card-page slug table is missing from the Russian application")
    app = app.replace(
        "const COURT_ORDER = { page: 11, knight: 12, queen: 13, king: 14 };",
        "const COURT_ORDER = { page: 11, knight: 12, queen: 13, king: 14 };\n\n" + slug_declaration.group(0),
        1,
    )
    position_end = """  for (const [key, title, icon] of SECTION_META) {
    html.push(`<div class=\"info-section\"><h3><span>${icon}</span> ${title}</h3><p>${p[key]}</p></div>`);
  }
  html.push(`<div class=\"card-page-link\"><a href=\"/en/cards/${CARD_PAGE_SLUGS[currentCard.id.replace('-', '')]}.html\" target=\"_blank\" rel=\"noopener\">${%s}${currentCard.name_ru}${%s}</a></div>`);
  html.push(`</div>`);""" % (
        json.dumps(ui["replacements"]["Подробнее о карте «"], ensure_ascii=False),
        json.dumps(ui["replacements"]["» — отдельная страница →"], ensure_ascii=False),
    )
    app = app.replace("""  for (const [key, title, icon] of SECTION_META) {
    html.push(`<div class=\"info-section\"><h3><span>${icon}</span> ${title}</h3><p>${p[key]}</p></div>`);
  }
  html.push(`</div>`);""", position_end, 1)
    app = app.replace("let currentPos = 'upright';", "let currentPos = 'upright';\nlet lastFocusedCard = null;")
    app = app.replace("tile.addEventListener('click', () => openCard(c));", "tile.addEventListener('click', () => openCard(c, tile));")
    app = app.replace("function openCard(card) {", "function openCard(card, trigger) {\n  lastFocusedCard = trigger || document.activeElement;")
    app = app.replace("  document.body.style.overflow = 'hidden';\n}\n\nfunction closeModal() {",
                      "  document.body.style.overflow = 'hidden';\n  modalClose.focus();\n}\n\nfunction closeModal() {\n  if (!modal.classList.contains('open')) return;")
    app = app.replace("  document.body.style.overflow = '';\n}\n\nfunction renderPosition() {",
                      "  document.body.style.overflow = '';\n  if (lastFocusedCard && document.contains(lastFocusedCard)) lastFocusedCard.focus();\n  lastFocusedCard = null;\n}\n\nfunction renderPosition() {")
    write_text(MAIN_OUT / "js" / "app.js", app)


def update_routes() -> None:
    path = I18N / "routes.json"
    routes = load_json(path)
    for route in routes:
        ru_file = route["ru_file"]
        if ru_file == "index.html":
            route["en_file"] = "en/taro/index.html"
            route["en_url"] = f"{SITE}/en/taro/"
            route["status"] = "hidden"
        elif ru_file.startswith("cards/"):
            route["status"] = "hidden"
    path.write_text(json.dumps(routes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def assert_output(cards: list[dict]) -> None:
    pages = sorted(CARDS_OUT.glob("*.html"))
    if len(pages) != 79:
        raise ValueError(f"Expected 79 hidden pages, found {len(pages)}")
    for path in [MAIN_OUT / "index.html", MAIN_OUT / "js" / "data.js", MAIN_OUT / "js" / "data_roman.js", MAIN_OUT / "js" / "app.js", *pages]:
        text = path.read_text(encoding="utf-8")
        visible = re.sub(r"/\*.*?\*/|//[^\n]*|<!--.*?-->|<style\b[^>]*>.*?</style>", "", text, flags=re.S | re.I)
        if CYRILLIC.search(visible):
            match = CYRILLIC.search(visible)
            raise ValueError(f"Untranslated text in {path.relative_to(ROOT)} near {visible[max(0, match.start()-60):match.start()+120]!r}")
    ids = [card["id"] for card in cards]
    if len(ids) != 78 or len(set(ids)) != 78:
        raise ValueError("Generated Tarot data does not contain 78 unique IDs")


def verify_russian() -> None:
    baseline = load_json(I18N / "ru-baseline.json")
    protected = ["index.html", *sorted(baseline["html"])]
    protected = list(dict.fromkeys(path for path in protected if path == "index.html" or path.startswith("cards/")))
    def strip_additions(text: str) -> str:
        # маркеры i18n (hreflang-блок, языковой переключатель) — разрешённые добавления
        text = re.sub(r"<!-- i18n:seo -->\n.*?<!-- /i18n:seo -->\n", "", text, flags=re.S)
        return re.sub(r"<!-- i18n:switch -->.*?<!-- /i18n:switch -->", "", text, flags=re.S)
    for rel in protected:
        path = ROOT / rel
        digest = hashlib.sha256(strip_additions(path.read_text(encoding="utf-8")).encode("utf-8")).hexdigest()
        if digest != baseline["html"][rel]:
            raise ValueError(f"Russian Tarot file changed: {rel}")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    verify_russian()
    ui = load_json(I18N / "tarot-ui.json")
    cards = localized_cards()
    roman = configure_card_renderer(cards, ui)
    CARDS_OUT.mkdir(parents=True, exist_ok=True)
    for card in cards:
        page = cards_build.render_card(card, cards, roman)
        write_text(CARDS_OUT / f"{cards_build.slug_for(card)}.html", finish_card_page(page, card, ui))
    write_text(CARDS_OUT / "index.html", finish_catalog(cards_build.render_index(cards, roman), ui))
    build_main(cards, roman, ui)
    update_routes()
    assert_output(cards)
    verify_russian()
    print("OK Tarot EN: SPA + 78 static card pages + hidden catalog; Russian Tarot unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
