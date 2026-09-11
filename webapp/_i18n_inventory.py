from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def walk_strings(value, path=""):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from walk_strings(child, f"{path}/{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_strings(child, f"{path}/{index}")
    elif isinstance(value, str):
        yield path, value


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=("rune", "sections", "staves", "staves_titles", "staves_visible", "builder", "stats"))
    parser.add_argument("value", nargs="?")
    args = parser.parse_args()
    source = json.loads((ROOT / "data" / "runes.json").read_text(encoding="utf-8"))
    if args.kind == "rune":
        requested = args.value.split(",")
        runes = [item for item in source["runes"] if item["id"] in requested]
        print(json.dumps(runes[0] if len(runes) == 1 else runes, ensure_ascii=False, indent=2))
    elif args.kind == "sections":
        value = source["sections"] if not args.value else source["sections"][args.value]
        print(json.dumps(value, ensure_ascii=False, indent=2))
    elif args.kind == "stats":
        rows = [(path, text) for path, text in walk_strings(source) if re.search(r"[А-Яа-яЁё]", text)]
        print(f"runes.json: {len(rows)} Cyrillic strings, {sum(len(text) for _, text in rows)} characters")
        for key, value in source["sections"].items():
            print(f"section {key}: {len(value)} characters")
    elif args.kind == "builder":
        tree = ast.parse((ROOT / "runes_build.py").read_text(encoding="utf-8"))
        values = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and re.search(r"[А-Яа-яЁё]", node.value):
                values.append(node.value)
        for index, value in enumerate(dict.fromkeys(values), 1):
            print(f"{index:03d}\t{value}")
    elif args.kind == "staves_titles":
        text = (ROOT / "runes" / "staves.html").read_text(encoding="utf-8")
        titles = []
        for body in re.findall(r"add\('[^']+',S\.\w+,'([^']*)'", text):
            titles.extend(row.split("|", 1)[0] for row in body.split(";") if "|" in row)
        titles.extend(re.findall(r"(?:entry|extra)\('([^']*)'", text))
        for index, value in enumerate(dict.fromkeys(titles), 1): print(f"{index:03d}\t{value}")
    elif args.kind == "staves_visible":
        class Visible(HTMLParser):
            def __init__(self):
                super().__init__(); self.skip = 0; self.values = []
            def handle_starttag(self, tag, attrs):
                if tag in ("script", "style"): self.skip += 1
            def handle_endtag(self, tag):
                if tag in ("script", "style"): self.skip -= 1
            def handle_data(self, data):
                value = data.strip()
                if not self.skip and value and re.search(r"[А-Яа-яЁё]", value): self.values.append(value)
        parser_ = Visible(); parser_.feed((ROOT / "runes" / "staves.html").read_text(encoding="utf-8"))
        for index, value in enumerate(dict.fromkeys(parser_.values), 1): print(f"{index:03d}\t{value}")
    else:
        text = (ROOT / "runes" / "staves.html").read_text(encoding="utf-8")
        values = []
        for match in re.finditer(r"(?P<q>['\"])(?P<s>(?:\\.|(?!\1).)*)(?P=q)", text):
            raw = match.group("q") + match.group("s") + match.group("q")
            try:
                value = ast.literal_eval(raw)
            except Exception:
                continue
            if isinstance(value, str) and re.search(r"[А-Яа-яЁё]", value):
                values.append(value)
        unique = list(dict.fromkeys(values))
        print(f"staves.html: {len(values)} Cyrillic literals, {len(unique)} unique")
        for index, value in enumerate(unique, 1):
            print(f"{index:03d}\t{value}")


if __name__ == "__main__":
    main()
