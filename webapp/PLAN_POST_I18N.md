# План финальной доводки после завершения EN-версии (один заход)

Когда все разделы переведены (руны ✓, нумерология, астрология, таро) и слиты — прогнать одним заходом:

## 1. Терминология "esoteric" (EN-версия)
- 87 вхождений на 34 страницах EN (данные: grep 'esoteric' en/).
- Правило: "esoteric" оставлять ТОЛЬКО в обозначениях традиций
  ("Western esotericism", "Eastern European esoteric tradition" — сноски не трогать).
- В текстах про практику/школы заменить на: "spiritual practice",
  "modern spiritual schools", "contemporary practice".
- Промт для GPT (уже передан): в новых разделах использовать
  "spiritual practice / modern spiritual schools" для практики,
  "esoteric" — только для традиций.

## 2. Донаты (когда Серж даст ссылки)
- Ko-fi удалён со всех 65 EN-страниц (был заглушкой).
- Добавить PayPal + Patreon в футер и модалку About:
  EN-версии и RU-версии. Места: *_build.py (RU) + данные i18n (EN).
- Порядок в EN: Patreon, PayPal, Donatello (UA-friendly), Privat24 (UA-friendly).

## 3. Мелочи по EN (копить по ходу)
- "About the project" -> "About" в навигации EN (унификация с RU «О проекте»?)
- Проверить спорные места из отчётов GPT (PILOT_REPORT раздел 5,
  FINAL_REPORT раздел 5): Ship "disruption", Sun significator,
  Крест-сочетания, Клевер+Крест, "Station for Two".

## Статус разделов EN
- [x] Ленорман (принят)
- [x] Руны + ставы (принят, слит на прод 09.09.2026)
- [ ] Нумерология (GPT в работе)
- [ ] Астрология
- [ ] Таро (последним: главная SPA, каталог, 78 карт)
