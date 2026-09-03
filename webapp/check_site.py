#!/usr/bin/env python3
"""Проверка целостности статического сайта перед публикацией."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent
ASSET_VERSION = "3.0"
REF_RE = re.compile(r"(?:href|src)\s*=\s*['\"]([^'\"]+)['\"]", re.I)
CSS_URL_RE = re.compile(r"url\(\s*['\"]?([^'\")]+)", re.I)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def local_target(source: Path, reference: str) -> Path | None:
    if reference.startswith(("http://", "https://", "//", "data:", "mailto:", "tel:", "javascript:", "#")):
        return None
    clean = unquote(urlsplit(reference).path)
    if not clean or "${" in clean or "{" in clean:
        return None
    return (source.parent / clean).resolve()


def load_cards() -> list[dict]:
    text = (ROOT / "js" / "data.js").read_text(encoding="utf-8")
    match = re.search(r"const\s+TARO_CARDS\s*=\s*(\[.*\]);\s*$", text, re.S)
    if not match:
        raise ValueError("js/data.js: не найден массив TARO_CARDS")
    return json.loads(match.group(1))


def main() -> int:
    errors: list[str] = []
    html_files = sorted(ROOT.rglob("*.html"))

    for source in [*html_files, *sorted((ROOT / "css").glob("*.css"))]:
        text = source.read_text(encoding="utf-8")
        attr_matches = list(REF_RE.finditer(text))
        refs = [m.group(1) for m in attr_matches]
        for match in attr_matches:
            if match.group(0).lstrip().lower().startswith("href"):
                target = local_target(source, match.group(1))
                if target is not None and target.is_dir():
                    errors.append(
                        f"ссылка ведёт на каталог вместо index.html: "
                        f"{source.relative_to(ROOT)} -> {match.group(1)}"
                    )
        if source.suffix == ".css":
            refs.extend(m.group(1) for m in CSS_URL_RE.finditer(text))
        for reference in refs:
            target = local_target(source, reference)
            if target is not None and not target.exists():
                errors.append(f"нет файла: {source.relative_to(ROOT)} -> {reference}")

        if source.suffix == ".html":
            if '<meta name="robots" content="noindex">' in text:
                errors.append(f"SEO: остался noindex в {source.relative_to(ROOT)}")
            for reference in refs:
                path = urlsplit(reference).path
                if (path.endswith(".css") or path.endswith(".js")) and "?v=" not in reference:
                    errors.append(f"нет версии ресурса: {source.relative_to(ROOT)} -> {reference}")
                if "?v=" in reference and f"?v={ASSET_VERSION}" not in reference:
                    errors.append(f"разная версия ресурса: {source.relative_to(ROOT)} -> {reference}")

    try:
        cards = load_cards()
    except Exception as exc:
        errors.append(str(exc))
        cards = []

    if len(cards) != 78:
        errors.append(f"Таро: найдено {len(cards)} карт вместо 78")
    if len({card.get("id") for card in cards}) != len(cards):
        errors.append("Таро: id карт не уникальны")

    for position in ("upright", "reversed"):
        gd_cards = [card for card in cards if card.get(position, {}).get("gd")]
        if len(gd_cards) != 40:
            errors.append(f"Golden Dawn {position}: найдено {len(gd_cards)} карт вместо 40")
        for card in gd_cards:
            gd = card[position]["gd"]
            if not all(isinstance(gd.get(key), str) and gd[key].strip() for key in ("title_en", "title_ru", "why")):
                errors.append(f"Golden Dawn: неполные данные {card.get('id')}.{position}")

    for card in cards:
        image = ROOT / "img" / "cards" / card.get("img", "")
        if not image.is_file():
            errors.append(f"Таро: нет изображения {card.get('id')} -> {card.get('img')}")

    wheel_data = (ROOT / "astrology" / "js" / "wheel-data.js").read_text(encoding="utf-8")
    for filename in re.findall(r"cardFile\d*:\s*['\"]([^'\"]+)['\"]", wheel_data):
        if not (ROOT / "img" / "cards" / filename).is_file():
            errors.append(f"Колесо: нет изображения карты {filename}")

    node = shutil.which("node")
    if node:
        for script in sorted((ROOT / "js").glob("*.js")) + sorted((ROOT / "astrology" / "js").glob("*.js")):
            result = subprocess.run([node, "--check", str(script)], text=True, capture_output=True)
            if result.returncode:
                errors.append(f"JavaScript: {script.relative_to(ROOT)}: {result.stderr.strip()}")

    if errors:
        print("ОШИБКИ ЦЕЛОСТНОСТИ:")
        print("\n".join(f" - {error}" for error in errors))
        return 1

    print(f"OK site: {len(html_files)} HTML, 78 карт, Golden Dawn 40/40, ссылки и JavaScript исправны")
    return 0


if __name__ == "__main__":
    sys.exit(main())
