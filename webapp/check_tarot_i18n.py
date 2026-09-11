"""Structural and content checks for the English Tarot stage."""
from __future__ import annotations

from html import unescape
import hashlib
import json
from pathlib import Path
import re

import cards_build


ROOT = Path(__file__).resolve().parent
I18N = ROOT / "data" / "i18n"
CYRILLIC = re.compile(r"[А-Яа-яЁё]")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def text_digest(path: Path) -> str:
    return hashlib.sha256(path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()


def tag_value(html: str, pattern: str) -> str:
    match = re.search(pattern, html, re.S | re.I)
    return unescape(re.sub(r"<[^>]+>", "", match.group(1)).strip()) if match else ""


def visible_cyrillic(text: str) -> bool:
    text = re.sub(r"<!--.*?-->|<style\b[^>]*>.*?</style>|/\*.*?\*/|//[^\n]*", "", text, flags=re.S | re.I)
    return bool(CYRILLIC.search(text))


def check() -> list[str]:
    errors: list[str] = []
    baseline = load(I18N / "ru-baseline.json")
    protected = ["index.html", *sorted(rel for rel in baseline["html"] if rel.startswith("cards/"))]
    for rel in protected:
        path = ROOT / rel
        if not path.is_file() or text_digest(path) != baseline["html"][rel]:
            errors.append(f"Russian Tarot changed: {rel}")

    routes = load(I18N / "routes.json")
    hidden = [route for route in routes if route["status"] == "hidden"]
    expected_ru = {"index.html", *{f"cards/{name}" for name in ["index.html", *[path.name for path in (ROOT / "cards").glob("*.html") if path.name != "index.html"]]}}
    if len(hidden) != 80 or {route["ru_file"] for route in hidden} != expected_ru:
        errors.append("Tarot route set must contain the main page, hidden catalog and 78 hidden card pages")

    classic = load(I18N / "tarot-classic-en.json")["cards"]
    roman = load(I18N / "tarot-roman-en.json")["cards"]
    editorial = load(I18N / "tarot-editorial-en.json")["cards"]
    source = cards_build.load_cards()
    source_ids = [card["id"] for card in source]
    if len(source_ids) != 78 or set(classic) != set(source_ids) or set(roman) != set(source_ids):
        errors.append("Tarot data IDs/count do not match the 78-card Russian source")
    if set(editorial) != set(cards_build.EDITORIAL):
        errors.append("Major Arcana editorial IDs do not match the Russian source")
    for filename in ("tarot-classic-en.json", "tarot-roman-en.json", "tarot-editorial-en.json"):
        text = (I18N / filename).read_text(encoding="utf-8")
        if CYRILLIC.search(text):
            errors.append(f"Cyrillic remains in translation data: {filename}")
        if "post-Soviet" in text or "ko-fi.com" in text:
            errors.append(f"Prohibited wording/link in {filename}")

    main_path = ROOT / "en" / "taro" / "index.html"
    main = main_path.read_text(encoding="utf-8") if main_path.is_file() else ""
    if not main:
        errors.append("Missing en/taro/index.html")
    else:
        required = (
            '<html lang="en">', '<link rel="canonical" href="https://taro.jetserg.top/en/taro/">',
            '"inLanguage": "en"', 'id="deck"', 'id="modal"', 'id="modalClose"',
            'data-pos="upright"', 'data-pos="reversed"', 'data-pos="roman"',
        )
        for marker in required:
            if marker not in main:
                errors.append(f"English Tarot main missing marker: {marker}")
        if visible_cyrillic(main):
            errors.append("Visible Cyrillic remains on English Tarot main")
        if "ko-fi.com" in main or main.count("(UA-friendly)") != 4:
            errors.append("Tarot main donation block differs from accepted English sections")
        cards_link = re.search(r'<a\b[^>]*href="\.\./cards/index\.html"[^>]*>', main)
        if not cards_link or "display:none" not in cards_link.group(0) or 'aria-hidden="true"' not in cards_link.group(0):
            errors.append("Hidden card catalog is visible in the Tarot main navigation")

    app_path = ROOT / "en" / "taro" / "js" / "app.js"
    app = app_path.read_text(encoding="utf-8") if app_path.is_file() else ""
    for marker in (
        "modalClose.addEventListener('click', closeModal)",
        "if (e.target === modal) closeModal()",
        "if (e.key === 'Escape') closeModal()",
        "modalClose.focus()", "lastFocusedCard.focus()",
        'href="/en/cards/${cardPage}.html"',
    ):
        if marker not in app:
            errors.append(f"Tarot modal behavior missing: {marker}")
    if visible_cyrillic(app):
        errors.append("Visible Cyrillic remains in English Tarot application data")
    data_text = (ROOT / "en" / "taro" / "js" / "data.js").read_text(encoding="utf-8")
    generated = json.loads(data_text[data_text.find("["):data_text.rfind("]") + 1])
    if [card["id"] for card in generated] != source_ids:
        errors.append("English Tarot card order differs from Russian")
    if len(generated) != 78 or visible_cyrillic(data_text):
        errors.append("English Tarot SPA data is incomplete or untranslated")

    pages = sorted((ROOT / "en" / "cards").glob("*.html"))
    card_pages = [path for path in pages if path.name != "index.html"]
    if len(pages) != 79 or len(card_pages) != 78:
        errors.append(f"Expected hidden catalog + 78 card pages, found {len(pages)} pages")
    titles, descriptions, headings = set(), set(), set()
    for path in card_pages:
        html = path.read_text(encoding="utf-8")
        title = tag_value(html, r"<title>(.*?)</title>")
        description = tag_value(html, r'<meta name="description" content="(.*?)">')
        heading = tag_value(html, r"<h1\b[^>]*>(.*?)</h1>")
        if not title or title in titles:
            errors.append(f"Missing or duplicate title: {path.relative_to(ROOT)}")
        if not description or description in descriptions:
            errors.append(f"Missing or duplicate description: {path.relative_to(ROOT)}")
        if not heading or heading in headings:
            errors.append(f"Missing or duplicate h1: {path.relative_to(ROOT)}")
        titles.add(title); descriptions.add(description); headings.add(heading)
        expected_url = f"https://taro.jetserg.top/en/cards/{path.name}"
        if f'<link rel="canonical" href="{expected_url}">' not in html or '"inLanguage": "en"' not in html:
            errors.append(f"SEO URL/language mismatch: {path.relative_to(ROOT)}")
        image = re.search(r'<div class="card-scene"><img src="([^"]+)"', html)
        if not image or not (path.parent / image.group(1)).resolve().is_file():
            errors.append(f"Missing card image: {path.relative_to(ROOT)}")
        nav_card = re.search(r'<nav class="main-nav".*?</nav>', html, re.S)
        catalog_link = re.search(r'<a\b[^>]*href="index\.html"[^>]*>', nav_card.group(0) if nav_card else "")
        if not catalog_link or "display:none" not in catalog_link.group(0):
            errors.append(f"Hidden catalog visible in navigation: {path.relative_to(ROOT)}")
        if visible_cyrillic(html):
            errors.append(f"Visible Cyrillic remains: {path.relative_to(ROOT)}")

    for sitemap in (ROOT / "sitemap.xml", ROOT / "en" / "sitemap.xml"):
        content = sitemap.read_text(encoding="utf-8")
        if "/en/taro/" in content or "/en/cards/" in content:
            errors.append(f"Hidden Tarot URLs were added to {sitemap.relative_to(ROOT)}")

    return errors


if __name__ == "__main__":
    if hasattr(__import__("sys").stdout, "reconfigure"):
        __import__("sys").stdout.reconfigure(encoding="utf-8")
    problems = check()
    if problems:
        print("\n".join(problems))
        raise SystemExit(1)
    print("OK Tarot EN: 78-card SPA, modal controls/focus, 78 static pages, unique SEO, hidden navigation, Russian files preserved")
