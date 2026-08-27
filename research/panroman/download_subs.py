#!/usr/bin/env python3
"""Скачивает субтитры всех лекций пана Романа из manifest.json и чистит VTT -> txt."""
import subprocess, json, os, re, sys

YT = "/home/serg/.hermes/hermes-agent/venv/bin/python3"
ROOT = "/home/serg/projects/Project-TARO/research/panroman"
manifest = json.load(open(f"{ROOT}/manifest.json"))

def vtt_to_text(path):
    lines_out, prev = [], ""
    for line in open(path, encoding="utf-8", errors="ignore"):
        line = line.strip()
        if not line or "-->" in line or line.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")):
            continue
        line = re.sub(r"<[^>]+>", "", line)
        line = re.sub(r"\[[^\]]*\]", " ", line)
        half = len(line) // 2
        if len(line) > 20 and line[:half].rstrip() == line[half:].strip().rstrip():
            line = line[:half].rstrip()
        if line == prev:
            continue
        prev = line
        lines_out.append(line)
    return " ".join(lines_out)

todo = []
for kind in ("major", "minor"):
    for m in manifest[kind]:
        slug = m.get("slug")
        if not slug:
            continue
        out_txt = f"{ROOT}/{kind}/panroman-{slug}.txt"
        if os.path.exists(out_txt) and os.path.getsize(out_txt) > 5000:
            continue
        todo.append((kind, slug, m["id"]))

print(f"К скачиванию: {len(todo)}")
fails = []
for i, (kind, slug, vid) in enumerate(todo):
    out_base = f"{ROOT}/{kind}/panroman-{slug}"
    vtt_path = f"{out_base}.ru.vtt"
    try:
        r = subprocess.run([YT, "-m", "yt_dlp", "--no-warnings", "--skip-download",
                            "--write-auto-subs", "--sub-langs", "ru", "--sub-format", "vtt",
                            "-o", out_base, f"https://www.youtube.com/watch?v={vid}"],
                           capture_output=True, text=True, timeout=180)
        if os.path.exists(vtt_path):
            txt = vtt_to_text(vtt_path)
            open(out_base + ".txt", "w", encoding="utf-8").write(txt)
            os.remove(vtt_path)
            print(f"[{i+1}/{len(todo)}] {slug}: {len(txt):,} симв")
        else:
            fails.append((slug, vid, "нет vtt"))
            print(f"[{i+1}/{len(todo)}] {slug}: FAIL нет субтитров")
    except Exception as e:
        fails.append((slug, vid, str(e)[:80]))
        print(f"[{i+1}/{len(todo)}] {slug}: ERR {str(e)[:60]}")

print("\nИТОГ: скачано", len(todo)-len(fails), "| провалов:", len(fails))
for f in fails: print("  FAIL:", f)
