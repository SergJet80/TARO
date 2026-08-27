#!/usr/bin/env python3
"""Генерирует батч-задания для субагентов: выжимка лекций пана Романа.

Использование:
  python3 make_tasks.py major 3 6   # лекции старших арканов с индекса 3 по 5
  python3 make_tasks.py minor       # все младшие
Печатает JSON со списком {slug, kind, title, transcript, out}.
"""
import json, os, sys

ROOT = "/home/serg/projects/Project-TARO/research/panroman"
manifest = json.load(open(f"{ROOT}/manifest.json"))

kind = sys.argv[1] if len(sys.argv) > 1 else "major"
start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
end = int(sys.argv[3]) if len(sys.argv) > 3 else None

items = []
for i, m in enumerate(manifest[kind]):
    if not m.get("slug"):
        continue
    if i < start or (end is not None and i >= end):
        continue
    transcript = f"{ROOT}/{kind}/panroman-{m['slug']}.txt"
    if not (os.path.exists(transcript) and os.path.getsize(transcript) > 5000):
        continue
    items.append({
        "id": m["id"],
        "slug": m["slug"],
        "title": m["title"],
        "transcript": transcript,
        "out": f"{ROOT}/{kind}/panroman-{m['slug']}-SUMMARY.md",
    })

print(json.dumps(items, ensure_ascii=False, indent=1))
