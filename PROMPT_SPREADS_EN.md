# Промт для GPT: перевод spreads.html (Атлас раскладов) на английский

Скопируй текст ниже и отдай его GPT целиком.

---

## Задача

Перевести страницу `spreads.html` (Атлас раскладов Таро) сайта taro.jetserg.top на английский язык. У тебя нет доступа к прошлому контексту проекта — вся нужная информация ниже.

## Что за проект

Статический справочник по Таро на русском языке. Недавно сделана английская версия: каталог `en/` внутри `webapp/` зеркально повторяет структуру RU-страниц. Все разделы уже переведены (Ленорман, Руны, Астрология, Нумерология, Таро — SPA + 78 карт). Осталась одна страница: `spreads.html` (Атлас раскладов) — она интерактивная, ~116 КБ, содержит SPA-подобный фильтр раскладов на JavaScript и встроенные JSON-данные схем.

## Что уже есть

- RU-оригинал: `webapp/spreads.html` (не трогать!)
- Терминологический глоссарий: `webapp/data/i18n/glossary.json` — используй устоявшиеся термины из него
- Пример стиля EN-переводов: `webapp/en/taro/index.html`, `webapp/en/cards/` — ориентируйся на тон и формат
- Маршрут уже прописан в `webapp/data/i18n/routes.json`: ru_file `spreads.html` → en_file `en/spreads.html`, статус `planned`

## Требования к переводу

1. Создай `webapp/en/spreads.html` — полный перевод `webapp/spreads.html`.
2. Переводи ВСЁ: заголовки, тексты, названия раскладов, вопросы позиций, описания, подсказки, JS-строки пользовательского интерфейса (тексты внутри `<script>`, которые выводятся на экран: названия схем, фильтры, сообщения поиска).
3. Встроенные JSON-данные (если есть названия раскладов и описания) — тоже перевести.
4. HTML-атрибуты: `lang="en"` в теге `<html>`; title и meta description — уникальные, переведённые.
5. SEO-блок (обязателен):
   - `<link rel="canonical" href="https://taro.jetserg.top/en/spreads.html">`
   - `<link rel="alternate" hreflang="ru" href="https://taro.jetserg.top/spreads.html">`
   - `<link rel="alternate" hreflang="en" href="https://taro.jetserg.top/en/spreads.html">`
   - `<link rel="alternate" hreflang="x-default" href="https://taro.jetserg.top/spreads.html">`
   - og:title, og:description, og:type=article, og:url=`https://taro.jetserg.top/en/spreads.html`, og:image=`https://taro.jetserg.top/img/cards/major-10-wheel.webp`
   - JSON-LD Article с inLanguage: en
6. Пути к CSS/JS/img: страница в корне `en/`, поэтому `css/...` → `../css/...`, `js/...` → `../js/...` и т.д. Проверь каждую ссылку.
7. Языковой переключатель в навбаре: добавь после ссылки «О проекте»:
   `<a class="mn-language" href="../spreads.html" hreflang="ru" lang="ru" aria-label="Switch to Russian" style="color:var(--ln-accent,var(--gold));border:1px solid var(--ln-accent-dim,var(--gold));border-radius:6px;padding:6px 10px;white-space:nowrap">RU | EN</a>`
   И оберни его маркерами: `<!-- i18n:switch -->` перед и `<!-- /i18n:switch -->` после.
8. Терминология: esoteric — только для обозначения традиций (Western esotericism); для практики используй spiritual practice / modern spiritual schools. Постсоветские особенности трактовок помечай «(feature of the post-Soviet Eastern European tarot school)» — только в EN.
9. Дисклеймеры: переведи дословно по смыслу, для EN усиль (это не предсказание фактов, не медицинский/финансовый совет).
10. НЕ меняй: структуру разметки, id/class для JS, порядок секций, вёрстку.

## Ограничения

- НЕ изменяй `webapp/spreads.html` (RU-оригинал).
- НЕ трогай другие файлы.
- НЕ добавляй новых зависимостей.

## Проверь себя перед сдачей

- Открой файл и убедись: нет кириллицы в видимых текстах (кроме цитат-оригиналов, если они намеренные).
- Все ссылки локальных ресурсов существуют (../css/..., ../js/...).
- Отсутствуют html-комментарии с RU-текстом, попавшим в видимый вывод.
- JS синтаксически валиден.

## Формат сдачи

Собери zip-архив `spreads-en-deploy.zip` ТОЛЬКО с изменёнными/новыми файлами: `en/spreads.html` + обновлённый `data/i18n/routes.json` (статус spreads.html → ready) + файл-манифест sha256. Плюс короткий отчёт: что переведено, какие места вызвали сомнения.

---