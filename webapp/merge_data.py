#!/usr/bin/env python3
"""Слияние JSON-частей в js/data.js + финальная валидация всех 78 карт."""
import json, os, sys

ROOT = "/home/serg/projects/tarot-guide"
DATA = os.path.join(ROOT, "data")

PARTS = [
    ("major-0-10.json", [f"major-{i:02d}" for i in range(0, 11)]),
    ("major-11-21.json", [f"major-{i:02d}" for i in range(11, 22)]),
    ("wands.json", [f"wands-{s}" for s in
        ["ace","two","three","four","five","six","seven","eight","nine","ten","page","knight","queen","king"]]),
    ("cups.json", [f"cups-{s}" for s in
        ["ace","two","three","four","five","six","seven","eight","nine","ten","page","knight","queen","king"]]),
    ("swords.json", [f"swords-{s}" for s in
        ["ace","two","three","four","five","six","seven","eight","nine","ten","page","knight","queen","king"]]),
    ("pentacles.json", [f"pentacles-{s}" for s in
        ["ace","two","three","four","five","six","seven","eight","nine","ten","page","knight","queen","king"]]),
]

FIELDS = ["short", "keywords", "archetype", "daily", "career", "love", "health", "esoteric"]
errors, all_cards = [], []

for fn, expected_ids in PARTS:
    path = os.path.join(DATA, fn)
    if not os.path.exists(path):
        errors.append(f"{fn}: ФАЙЛ НЕ НАЙДЕН")
        continue
    try:
        data = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        errors.append(f"{fn}: битый JSON: {e}")
        continue
    if not isinstance(data, list) or len(data) != len(expected_ids):
        errors.append(f"{fn}: len={len(data) if isinstance(data, list) else '?'}, нужно {len(expected_ids)}")
        continue
    ids = [c.get("id") for c in data]
    if ids != expected_ids:
        errors.append(f"{fn}: порядок id не совпадает")
        continue
    for c in data:
        cid = c.get("id", "?")
        for key in ("name_ru", "name_en", "type", "img"):
            if not c.get(key):
                errors.append(f"{cid}: нет поля {key}")
        img = os.path.join(ROOT, "img", "cards", c.get("img", "?"))
        if not os.path.exists(img):
            errors.append(f"{cid}: нет картинки {c.get('img')}")
        for pos in ("upright", "reversed"):
            p = c.get(pos)
            if not isinstance(p, dict):
                errors.append(f"{cid}.{pos}: отсутствует"); continue
            for f in FIELDS:
                v = p.get(f)
                if v is None or (isinstance(v, str) and not v.strip()):
                    errors.append(f"{cid}.{pos}.{f}: пусто")
                elif f == "keywords" and not (isinstance(v, list) and 5 <= len(v) <= 7):
                    errors.append(f"{cid}.{pos}.keywords: {len(v) if isinstance(v, list) else 'не список'}")
                elif f != "keywords" and isinstance(v, str):
                    mn = 400 if f == "archetype" else 60
                    if len(v) < mn:
                        errors.append(f"{cid}.{pos}.{f}: {len(v)} < {mn}")
        all_cards.append(c)

if errors:
    print("ОШИБКИ:")
    print("\n".join(f" - {e}" for e in errors))
    sys.exit(1)

# Пишем js/data.js
out = "/* Сгенерировано автоматически: 78 карт колоды Уэйта. Не редактировать вручную — править data/*.json */\nconst TARO_CARDS = " \
    + json.dumps(all_cards, ensure_ascii=False, indent=1) + ";\n"
with open(os.path.join(ROOT, "js", "data.js"), "w", encoding="utf-8") as f:
    f.write(out)

majors = sum(1 for c in all_cards if c["type"] == "major")
print(f"OK: {len(all_cards)} карт ({majors} старших + {len(all_cards)-majors} младших) -> js/data.js ({len(out)//1024} KB)")
