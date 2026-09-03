#!/usr/bin/env python3
"""Единая пересборка и проверка всего статического сайта."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
STEPS = [
    "optimize_images.py",
    "merge_data.py",
    "astrology_build.py",
    "planets_build.py",
    "runes_build.py",
    "numerology_build.py",
    "update_nav.py",
    "check_site.py",
]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def main() -> int:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    for script in STEPS:
        print(f"\n[{script}]", flush=True)
        subprocess.run([sys.executable, str(ROOT / script)], cwd=ROOT, env=env, check=True)
    print("\nOK: сайт полностью собран и проверен")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except subprocess.CalledProcessError as exc:
        print(f"\nСборка остановлена на шаге с кодом {exc.returncode}", file=sys.stderr)
        sys.exit(exc.returncode)
