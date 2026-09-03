#!/usr/bin/env python3
"""Создаёт WebP-копии всех JPEG-изображений, сохраняя исходники."""
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parent
QUALITY = 82


def main():
    converted = 0
    skipped = 0
    before = 0
    after = 0

    for source in sorted(ROOT.rglob("*.jpg")):
        target = source.with_suffix(".webp")
        before += source.stat().st_size

        if target.exists() and target.stat().st_mtime >= source.stat().st_mtime:
            skipped += 1
            after += target.stat().st_size
            continue

        with Image.open(source) as image:
            image = ImageOps.exif_transpose(image)
            if image.mode not in ("RGB", "RGBA"):
                image = image.convert("RGB")
            image.save(target, "WEBP", quality=QUALITY, method=6)

        converted += 1
        after += target.stat().st_size

    saved = before - after
    percent = (saved / before * 100) if before else 0
    print(
        f"OK images: {converted} converted, {skipped} current; "
        f"WebP saves {saved / 1024 / 1024:.2f} MiB ({percent:.1f}%)"
    )


if __name__ == "__main__":
    main()
