# Project TARO

Справочник значений карт Таро (колода Universal Waite) + материалы школы Таро пана Романа.

## Структура

- `webapp/` — офлайн-справочник 78 карт (статик-сайт: HTML+CSS+JS, без зависимостей).
  - Открыть: `webapp/index.html` в браузере, работает без интернета.
  - Публикация: https://taro.jetserg.top (Cloudflare Tunnel → localhost:8090 на VPS).
- `research/panroman/` — материалы школы пана Романа:
  - `{major,minor}/` — выжимки лекций: `*.txt` (сырые транскрипты, в git не входят) и `*-SUMMARY.md` (итоговые конспекты).
  - `manifest.json` — реестр лекций с video_id.
  - `download_subs.py` — скачивание субтитров через yt-dlp.
  - `make_tasks.py` — генератор брифов для выжимок.
  - `simplified_majors.md` — упрощённая версия трактовок старших арканов.

## Данные справочника

Правки значений карт — только в `webapp/data/*.json` (6 частей), затем пересборка:

```bash
cd webapp && python3 merge_data.py
```

Данные школы Романа для сайта — `webapp/js/data_roman.js` (генерируется из research-материалов).

## systemd-сервисы на VPS

- `taro-site.service` — python http.server :8090 (WorkingDirectory: webapp/)
- `taro-tunnel.service` — cloudflared tunnel `taro-guide` (токен в `~/.cloudflared/taro-token.env`)

## Примечание

Материалы школы пана Романа — конспекты открытых лекций YouTube (2020–2021), для личного использования.
