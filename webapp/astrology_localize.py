#!/usr/bin/env python3
"""Localize the existing astrology pages and Zodiac Wheel without rebuilding their HTML.

The current Russian files are the page templates. English prose lives under
data/i18n; only text nodes, text attributes and JavaScript string literals are
substituted. The wheel algorithm and all non-text source data stay unchanged.
"""
from __future__ import annotations

from html import escape
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess

import astrology_build
import i18n_build
import planets_build
from check_i18n import check_pending, strip_additions

ROOT = Path(__file__).resolve().parent
I18N = ROOT / "data" / "i18n"
ASTROLOGY_PATHS = sorted(
    route["ru_file"] for route in i18n_build.load_json("routes.json")
    if route["ru_file"].startswith("astrology/")
)
JS_TOKEN = re.compile(r'''"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*' '''.strip())


def read_json(name: str):
    return json.loads((I18N / name).read_text(encoding="utf-8"))


def source_wheel_data(path: Path):
    node = os.environ.get("NODE_BINARY") or shutil.which("node")
    if not node:
        raise RuntimeError("Node.js is required to read the canonical Zodiac Wheel data")
    program = (
        "global.window={};require(process.argv[1]);"
        "process.stdout.write(JSON.stringify(window.ZODIAC_WHEEL));"
    )
    result = subprocess.run(
        [node, "-e", program, str(path.resolve())],
        cwd=ROOT, encoding="utf-8", capture_output=True, check=True,
    )
    return json.loads(result.stdout)


def add_pair(mapping: dict[str, str], ru: str, en: str, context: str) -> None:
    if ru == en == "":
        return
    if not isinstance(ru, str) or not isinstance(en, str) or not en.strip():
        raise ValueError(f"Missing text in {context}")
    previous = mapping.get(ru)
    if previous is not None and previous != en:
        raise ValueError(f"Conflicting translation for {ru!r}: {previous!r} / {en!r}")
    if ru != en:
        mapping[ru] = en


def translation_mapping() -> dict[str, str]:
    mapping: dict[str, str] = {}
    ui = read_json("astrology-ui.json")
    for item in ui["strings"]:
        add_pair(mapping, item["ru"], item["en"], "astrology-ui.json")

    sign_en = read_json("astrology-signs-en.json")
    if list(sign_en["signs"]) != [row[0] for row in astrology_build.SIGNS]:
        raise ValueError("Astrology sign IDs or order do not match astrology_build.py")
    if len(sign_en["section_titles"]) != 9:
        raise ValueError("Expected nine translated sign section titles")
    st = ui["templates"]
    for slug, name, _symbol, tagline, blocks in astrology_build.SIGNS:
        en = sign_en["signs"][slug]
        if len(en["blocks"]) != len(blocks):
            raise ValueError(f"{slug}: translated sign block count differs")
        add_pair(mapping, name, en["name"], slug)
        add_pair(mapping, tagline, en["tagline"], slug)
        add_pair(mapping, st["sign_title_ru"].format(name=name), st["sign_title_en"].format(name=en["name"]), slug)
        add_pair(mapping, st["sign_description_ru"].format(name=name), st["sign_description_en"].format(name=en["name"]), slug)
        add_pair(mapping, st["sign_alt_ru"].format(name=name), st["sign_alt_en"].format(name=en["name"]), slug)
        add_pair(mapping, st["sign_footer_ru"].format(name=name), st["sign_footer_en"].format(name=en["name"]), slug)
        for index, ((ru_title, ru_text), en_title, en_text) in enumerate(zip(blocks.items(), sign_en["section_titles"], en["blocks"])):
            add_pair(mapping, ru_title, en_title, f"{slug} title {index}")
            add_pair(mapping, ru_text, en_text, f"{slug} block {index}")

    planet_en = read_json("astrology-planets-en.json")
    if list(planet_en["planets"]) != [row[0] for row in planets_build.PLANETS]:
        raise ValueError("Planet IDs or order do not match planets_build.py")
    if len(planet_en["section_titles"]) != 6:
        raise ValueError("Expected six translated planet section titles")
    add_pair(mapping, planets_build.DISCLAIMER_INDEX, planet_en["catalog_disclaimer"], "planet catalogue disclaimer")
    for slug, name, _symbol, tagline, alt, _image in planets_build.PLANETS:
        en = planet_en["planets"][slug]
        if len(en["blocks"]) != len(planets_build.PAGES[slug]):
            raise ValueError(f"{slug}: translated planet block count differs")
        add_pair(mapping, name, en["name"], slug)
        add_pair(mapping, tagline, en["tagline"], slug)
        add_pair(mapping, alt, en["alt"], slug)
        add_pair(mapping, st["planet_title_ru"].format(name=name), st["planet_title_en"].format(name=en["name"]), slug)
        add_pair(mapping, st["planet_description_ru"].format(name=name), st["planet_description_en"].format(name=en["name"]), slug)
        add_pair(mapping, st["planet_footer_ru"].format(name=name), st["planet_footer_en"].format(name=en["name"]), slug)
        for index, ((ru_title, ru_text), en_title, en_text) in enumerate(zip(planets_build.PAGES[slug], planet_en["section_titles"], en["blocks"])):
            add_pair(mapping, ru_title, en_title, f"{slug} title {index}")
            add_pair(mapping, ru_text, en_text, f"{slug} block {index}")

    wheel_ru = source_wheel_data(ROOT / "astrology" / "js" / "wheel-data.js")
    wheel_en = read_json("astrology-wheel-en.json")
    if [row["slug"] for row in wheel_ru] != list(wheel_en["signs"]):
        raise ValueError("Wheel sign IDs or order do not match wheel-data.js")
    for ru, en in zip(wheel_ru, wheel_en["signs"].values()):
        for key, en_value in en.items():
            if key not in ru:
                raise ValueError(f"Wheel field {key!r} does not exist for {ru['slug']}")
            add_pair(mapping, ru[key], en_value, f"wheel {ru['slug']}.{key}")
    months_ru = ["Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь", "Январь", "Февраль"]
    for ru, en in zip(months_ru, wheel_en["months"]):
        add_pair(mapping, ru, en, "wheel month")
    outside_ru = [
        {"name": "Шут", "text": "Альфа и омега, «божественная глупость». Точка входа в колесо и начала пути."},
        {"name": "Мир", "text": "«Обнуление», завершение цикла. Выход из колеса и готовность к новому началу."},
    ]
    if len(wheel_en.get("outside", [])) != len(outside_ru):
        raise ValueError("Expected two translated Arcana outside the Wheel")
    for ru, en in zip(outside_ru, wheel_en["outside"]):
        add_pair(mapping, ru["name"], en["name"], "wheel outside Arcana")
        add_pair(mapping, ru["text"], en["text"], "wheel outside Arcana")
    for ru, en in wheel_en["ui"].items():
        add_pair(mapping, ru, en, "wheel UI")
    # Shared navigation, About and donation copy fills only keys that are not
    # astrology terms (for example, Рыбы means Pisces here, not The Fish).
    for item in read_json("lenormand-ui.json"):
        mapping.setdefault(item["ru"], item["en"])
    return mapping


def replace_text(text: str, mapping: dict[str, str], html: bool = False) -> str:
    pattern = re.compile("|".join(re.escape(key) for key in sorted(mapping, key=len, reverse=True) if key))
    return pattern.sub(lambda match: escape(mapping[match.group()], quote=True) if html else mapping[match.group()], text)


def translate_script(source: str, mapping: dict[str, str]) -> str:
    def literal(match):
        raw = match.group()
        if not re.search(r"[А-Яа-яЁё]", raw):
            return raw
        try:
            value = json.loads(raw) if raw.startswith('"') else raw[1:-1].replace("\\'", "'").replace('\\"', '"')
        except json.JSONDecodeError as exc:
            raise ValueError(f"Cannot decode JavaScript literal {raw[:80]!r}") from exc
        translated = replace_text(value, mapping)
        if re.search(r"[А-Яа-яЁё]", translated):
            raise ValueError(f"Untranslated JavaScript literal: {value}")
        return json.dumps(translated, ensure_ascii=False).replace("</", "<\\/")
    return JS_TOKEN.sub(literal, source)


def translate_html(source: str, mapping: dict[str, str]) -> str:
    parts = re.split(r"(<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>|<!--.*?-->)", source, flags=re.S | re.I)
    translated = []
    for part in parts:
        if re.match(r"<script\b", part, re.I):
            translated.append(translate_script(part, mapping))
        elif re.match(r"<style\b|<!--", part, re.I):
            translated.append(part)
        else:
            translated.append(replace_text(part, mapping, html=True))
    result = "".join(translated)
    unresolved = re.findall(r".{0,45}[А-Яа-яЁё]+.{0,90}", re.sub(r"<!--.*?-->|<style\b[^>]*>.*?</style>", "", result, flags=re.S | re.I))
    if unresolved:
        raise ValueError("Untranslated astrology HTML: " + " | ".join(unresolved[:8]))
    return result


def update_routes() -> None:
    routes = read_json("routes.json")
    for route in routes:
        if route["ru_file"].startswith("astrology/"):
            route["status"] = "ready"
    (I18N / "routes.json").write_text(json.dumps(routes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    i18n_build.load_json.cache_clear()
    i18n_build.ready_paths.cache_clear()


def main() -> int:
    if len(ASTROLOGY_PATHS) != 28:
        raise ValueError(f"Expected 28 astrology routes, found {len(ASTROLOGY_PATHS)}")
    baseline = i18n_build.load_json("ru-baseline.json")["html"]
    source_pages = {}
    for relative in ASTROLOGY_PATHS:
        source = strip_additions((ROOT / relative).read_text(encoding="utf-8"))
        if hashlib.sha256(source.encode("utf-8")).hexdigest() != baseline[relative]:
            raise ValueError(f"Russian astrology source differs from baseline: {relative}")
        source_pages[relative] = source

    mapping = translation_mapping()
    update_routes()
    pending: dict[Path, str] = {}
    for relative, source in source_pages.items():
        pending[ROOT / relative] = i18n_build.finalize(source, relative, "ru", english_disclaimer=False)
        english = i18n_build.finalize(
            translate_html(source, mapping), relative, "en", template=True,
            english_disclaimer=False, section_prefix="astrology/",
        )
        if relative == "astrology/wheel.html":
            english = english.replace('src="../../astrology/js/wheel-data.js', 'src="js/wheel-data.js')
            english = english.replace('src="../../astrology/js/wheel.js', 'src="js/wheel.js')
        # Переключатель на EN-колесо в RU-исходнике ('../en/astrology/wheel.html') в EN-копии
        # должен указывать на тот же файл (/../en/astrology/wheel.html от en/astrology/)
        english = english.replace('href="../../astrology/wheel.html"', 'href="../../astrology/wheel.html"')  # RU-колесо: тот же путь валиден от en/astrology (up2 = webapp)
        # Соседние разделы (lenormand/runes/numerology) в EN-астрологии остаются ссылками на RU
        # (чекер требует «links to other sections target RU»). Глубина EN = глубина RU + 1:
        # считаем вверх от текущей EN-страницы до корня webapp и ставим абсолютный префикс.
        en_rel = 'en/' + relative
        en_dir = en_rel.rsplit('/', 1)[0]
        def _ru_neighbor(m):
            # цель: ROOT/<section>/ → относительный путь от каталога EN-страницы
            depth = en_dir.count('/') + 1  # en/astrology/X → 3 сегмента → 3 up до webapp
            section = re.search(r'(lenormand|runes|numerology)/', m.group()).group(1)
            return 'href="' + '../' * depth + section + '/'
        english = re.sub(r'href="(?:\.\./)+(?:lenormand|runes|numerology)/', _ru_neighbor, english)

        pending[ROOT / "en" / relative] = english

    errors = check_pending(pending)
    if errors:
        raise ValueError("\n".join(errors))
    for path, text in pending.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")

    js_dir = ROOT / "en" / "astrology" / "js"
    js_dir.mkdir(parents=True, exist_ok=True)
    js_dir.joinpath("wheel-data.js").write_text(
        translate_script((ROOT / "astrology" / "js" / "wheel-data.js").read_text(encoding="utf-8"), mapping),
        encoding="utf-8", newline="\n",
    )
    wheel_js = translate_script((ROOT / "astrology" / "js" / "wheel.js").read_text(encoding="utf-8"), mapping)
    wheel_js = wheel_js.replace('var CARDPATH = "../img/cards/";', 'var CARDPATH = "../../img/cards/";')
    js_dir.joinpath("wheel.js").write_text(wheel_js, encoding="utf-8", newline="\n")
    i18n_build.update_sitemaps()
    print("OK: 28 astrology RU bases + EN translations, including interactive Zodiac Wheel")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
