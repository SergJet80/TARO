#!/usr/bin/env python3
"""Structural and terminology checks for the faithful English astrology copy."""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import json
import os
import re
import shutil
import subprocess

import i18n_build
from check_i18n import strip_additions
from check_site import local_target

ROOT = Path(__file__).resolve().parent
CYRILLIC = re.compile(r"[А-Яа-яЁё]")
JS_TOKEN = re.compile(r'''"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*' '''.strip())
NOTE = "(A feature of the Eastern European esoteric tradition.)"


class Body(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inside = False
        self.tags = []
        self.refs = []
        self.images = []

    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self.inside = True
        if not self.inside:
            return
        values = dict(attrs)
        self.tags.append((tag, tuple((key, value) for key, value in attrs if key not in ("href", "src", "alt", "title", "aria-label"))))
        for key in ("href", "src"):
            if key in values:
                self.refs.append((tag, key, values[key]))
        if tag == "img":
            self.images.append(values.get("src", ""))

    def handle_endtag(self, tag):
        if self.inside:
            self.tags.append(("/" + tag, ()))
        if tag == "body":
            self.inside = False


def normalize_script(source: str) -> str:
    return JS_TOKEN.sub('"TEXT"', source)


def read_wheel(path: Path):
    node = os.environ.get("NODE_BINARY") or shutil.which("node")
    if not node:
        raise RuntimeError("Node.js is unavailable")
    code = (
        "global.window={};require(process.argv[1]);"
        "process.stdout.write(JSON.stringify({wheel:window.ZODIAC_WHEEL,out:window.ZODIAC_WHEEL_OUT}));"
    )
    result = subprocess.run([node, "-e", code, str(path.resolve())], cwd=ROOT, encoding="utf-8", capture_output=True, check=True)
    return json.loads(result.stdout)


def check():
    errors = []
    routes = [route for route in i18n_build.load_json("routes.json") if route["ru_file"].startswith("astrology/")]
    if len(routes) != 28 or any(route["status"] != "ready" for route in routes):
        errors.append(f"Astrology: expected 28 ready routes, found {len(routes)}")
        return errors
    route_targets = {(ROOT / route["ru_file"]).resolve(): (ROOT / route["en_file"]).resolve() for route in routes}
    special_targets = {
        (ROOT / "astrology/js/wheel-data.js").resolve(): (ROOT / "en/astrology/js/wheel-data.js").resolve(),
        (ROOT / "astrology/js/wheel.js").resolve(): (ROOT / "en/astrology/js/wheel.js").resolve(),
    }

    for route in routes:
        ru_path = ROOT / route["ru_file"]
        en_path = ROOT / route["en_file"]
        ru = strip_additions(ru_path.read_text(encoding="utf-8"))
        en = strip_additions(en_path.read_text(encoding="utf-8"))
        a, b = Body(), Body()
        a.feed(ru)
        b.feed(en)
        if a.tags != b.tags:
            errors.append(f"{route['en_file']}: body structure or non-text attributes changed")
        if len(a.images) != len(b.images):
            errors.append(f"{route['en_file']}: image count changed")
        expected_refs = []
        for tag, key, reference in a.refs:
            target = local_target(ru_path, reference)
            if target is None:
                expected_refs.append(None)
            else:
                expected_refs.append(route_targets.get(target, special_targets.get(target, target)))
        actual_refs = [local_target(en_path, reference) for _tag, _key, reference in b.refs]
        if expected_refs != actual_refs:
            errors.append(f"{route['en_file']}: internal section or asset targets changed")
        for source in b.images:
            target = local_target(en_path, source)
            if target is not None and not target.is_file():
                errors.append(f"{route['en_file']}: missing image {source}")
        clean = re.sub(r"<!--.*?-->|<style\b[^>]*>.*?</style>", "", en, flags=re.S | re.I)
        if CYRILLIC.search(clean):
            errors.append(f"{route['en_file']}: Cyrillic remains in English page")
        if re.search(r"post[ -]Soviet|esoteric (?:practice|school)s?", clean, re.I):
            errors.append(f"{route['en_file']}: disallowed cultural terminology")
        if "diagnosis" not in en or "financial" not in en:
            errors.append(f"{route['en_file']}: required disclaimer is incomplete")
        if "ko-fi.com" in en.lower():
            errors.append(f"{route['en_file']}: Ko-fi was restored")

        def inline_scripts(text):
            return [body for attrs, body in re.findall(r"<script\b([^>]*)>(.*?)</script>", text, re.S | re.I) if "application/ld+json" not in attrs and body.strip()]
        if [normalize_script(body) for body in inline_scripts(ru)] != [normalize_script(body) for body in inline_scripts(en)]:
            errors.append(f"{route['en_file']}: inline script logic changed beyond string localization")

    proserpina = (ROOT / "en/astrology/planety/prozerpina/index.html").read_text(encoding="utf-8")
    wheel_html = (ROOT / "en/astrology/wheel.html").read_text(encoding="utf-8")
    if NOTE not in proserpina:
        errors.append("Proserpina: required Eastern European cultural note missing")
    if NOTE not in wheel_html:
        errors.append("Zodiac Wheel: required Eastern European cultural note missing")

    source_data = read_wheel(ROOT / "astrology/js/wheel-data.js")
    english_data = read_wheel(ROOT / "en/astrology/js/wheel-data.js")
    if len(source_data["wheel"]) != 12 or len(english_data["wheel"]) != 12:
        errors.append("Zodiac Wheel: expected 12 signs in both data files")
    locked = ("slug", "sym", "planetsGlyph", "cardFile", "cardFile2", "oppositeSlug")
    for ru, en in zip(source_data["wheel"], english_data["wheel"]):
        if list(ru) != list(en):
            errors.append(f"Zodiac Wheel {ru.get('slug')}: data field structure changed")
        for key in locked:
            if ru.get(key) != en.get(key):
                errors.append(f"Zodiac Wheel {ru.get('slug')}: non-text field {key} changed")
    if len(source_data.get("out", [])) != len(english_data.get("out", [])):
        errors.append("Zodiac Wheel: outside-Arcana structure changed")

    for name in ("wheel-data.js", "wheel.js"):
        source = (ROOT / "astrology/js" / name).read_text(encoding="utf-8")
        english = (ROOT / "en/astrology/js" / name).read_text(encoding="utf-8")
        if normalize_script(source) != normalize_script(english):
            errors.append(f"Zodiac Wheel: executable structure changed in {name}")
        node = os.environ.get("NODE_BINARY") or shutil.which("node")
        if node:
            result = subprocess.run([node, "--check", str(ROOT / "en/astrology/js" / name)], encoding="utf-8", capture_output=True)
            if result.returncode:
                errors.append(f"Zodiac Wheel: invalid {name}: {result.stderr.strip()}")

    # Only terms present in the Russian source are asserted; the source does
    # not contain element/modality/ruler or a transpersonal-planet taxonomy.
    required_terms = {
        "natal chart": ROOT / "en/astrology/planety/index.html",
        "Proserpina": ROOT / "en/astrology/planety/prozerpina/index.html",
    }
    all_text = "\n".join(path.read_text(encoding="utf-8") for path in required_terms.values())
    for term in required_terms:
        if term.lower() not in all_text.lower():
            errors.append(f"Astrology terminology: expected {term!r}")
    if not errors:
        print("OK astrology: 28 source-based pairs; DOM, links, images, terminology and Wheel code/data preserved")
    return errors


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    problems = check()
    print("\n".join(problems))
    raise SystemExit(bool(problems))
