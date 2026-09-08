#!/usr/bin/env python3
"""Генератор статических страниц карт Таро: все 78 карт в дизайне модалки.

Python 3, только стандартная библиотека. Запуск из любой папки:
    python путь/к/webapp/cards_build.py

Читает data/major-*.json + data/{wands,cups,swords,pentacles}.json и
js/data_roman.js (Школа Современного Таро). Пишет только HTML внутри webapp/cards/.
"""
from __future__ import annotations

import json
import re
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "cards"
SITE = "https://taro.jetserg.top"

# ─── Редакционный слой: slugs, символы, краткие идеи, вступления, советы, вопросы ───
# Для старших арканов slugs сохранены прежние (уже в индексе поисковиков).
EDITORIAL = {
    "major-00": ("durak", "☀", "Начало пути", "новый путь и доверие к жизни",
        "Дурак появляется там, где привычный опыт ещё не подсказывает ответа. Он приглашает попробовать новое, сохранив любопытство и готовность отвечать за свой шаг.",
        "Начните с небольшого опыта, для которого не нужны полная уверенность и чужое одобрение. Проверьте самое необходимое и оставьте место неожиданностям: доверие к жизни вполне уживается с внимательностью.",
        ("Что мне хочется попробовать, даже если я пока совсем не умею этого делать?",
         "Какая простая подготовка позволит мне рискнуть осознанно?",
         "Где я называю осторожностью страх показаться новичком?")),
    "major-01": ("mag", "✦", "Воля и действие", "сосредоточенность и сила действия",
        "Маг собирает разрозненные возможности в одно точное действие. Карта напоминает, что умение становится силой, когда вы выбираете задачу и подтверждаете намерения поступками.",
        "Выберите одно дело и используйте то, что уже умеете, вместо бесконечного поиска идеального инструмента. Обещайте лишь то, что готовы сделать, и покажите результат прежде, чем рассказывать о следующем замысле.",
        ("Какой мой навык уже позволяет сдвинуть дело с места?",
         "На какие мелочи уходит внимание, нужное главной задаче?",
         "Какой поступок подтвердит мои слова сегодня?")),
    "major-02": ("zhrefca", "☾", "Тишина и интуиция", "интуиция и внимание к скрытому",
        "Верховная жрица предлагает не торопиться с объяснениями и прислушаться к тому, что пока трудно выразить. Тишина помогает заметить скрытые мотивы, если не путать собственное чувство с догадками о других.",
        "Отложите шумные обсуждения и запишите, что вы замечаете и чувствуете наедине с собой. Дайте ответу созреть, а важные недоговорённости проясните словами: загадочность не должна заменять честность.",
        ("Какое ощущение я отбрасываю только потому, что не могу сразу его объяснить?",
         "Что я знаю о ситуации, а что лишь додумываю в тишине?",
         "Какую недосказанность пора бережно прояснить?")),
    "major-03": ("imperatrica", "❀", "Забота и рост", "забота, творчество и изобилие",
        "Императрица говорит о росте, которому нужны внимание, время и удовольствие от процесса. Она помогает увидеть разницу между заботой, питающей жизнь, и опекой, под которой уже трудно дышать.",
        "Поддержите то, что хотите вырастить: уделите время идее, дому или близкому разговору. Не требуйте мгновенной отдачи и проверьте, остаются ли у вас силы и радость для собственной жизни.",
        ("Что в моей жизни сейчас нуждается в регулярной, простой заботе?",
         "Где я тороплю результат, которому ещё нужно время?",
         "Как я могу поддержать близкого, не делая всё за него?")),
    "major-04": ("imperator", "♜", "Порядок и ответственность", "порядок, границы и ответственность",
        "Император превращает намерение в понятный порядок: кто решает, что обещано и где проходят границы. Его устойчивость держится на ответственности, а чрезмерное стремление командовать делает эту опору жёсткой и неудобной.",
        "Назовите правила и договорённости, на которые действительно можно опереться. Возьмите свою часть ответственности и держите слово, сохраняя возможность пересмотреть правило, если оно уже мешает делу.",
        ("В какой области мне не хватает ясных договорённостей?",
         "За какое решение я готов отвечать лично?",
         "Где полезная граница превратилась в желание всё контролировать?")),
    "major-05": ("ierofant", "✧", "Знание и традиция", "учёба, традиция и общие ценности",
        "Иерофант обращает внимание на знания и правила, которые передаются от человека к человеку. Он предлагает найти надёжную опору в опыте других и одновременно понять, какой смысл вы сами вкладываете в выбранную традицию.",
        "Обратитесь к человеку, чей опыт можно проверить, и разберитесь в основах выбранного дела. Следуя правилу, спрашивайте себя, чему оно служит: осмысленное обучение оставляет место собственным вопросам.",
        ("У кого я могу учиться, не отказываясь от самостоятельного суждения?",
         "Какое принятое правило поддерживает мои ценности?",
         "Что я продолжаю повторять по привычке, уже не понимая смысла?")),
    "major-06": ("vlyublyonnye", "♡", "Союз и выбор", "честный выбор и близость ценностей",
        "Влюблённые связывают близость с выбором, за которым стоят ваши ценности. Карта спрашивает, совпадает ли то, к чему тянется сердце, с тем, как вы готовы поступать каждый день.",
        "Проговорите, что для вас важно в союзе или решении, и выслушайте другую сторону. Сделайте выбор, с которым согласны и чувства, и совесть, не перекладывая его на обстоятельства.",
        ("Какие ценности я хочу сохранить в этом выборе?",
         "В чём мои поступки расходятся с тем, что я называю любовью?",
         "От какого другого пути придётся отказаться, если я скажу «да»?")),
    "major-07": ("kolesnica", "➶", "Курс и движение", "движение к цели и самодисциплина",
        "Колесница собирает противоречивые желания вокруг выбранного направления. Она поддерживает решимость двигаться вперёд, но напоминает, что скорость полезна только тогда, когда вы управляете движением.",
        "Определите ближайшую цель и договоритесь о направлении с теми, кто участвует в деле. Если эмоции заставляют спешить или давить, сначала верните себе управление, а затем прибавляйте темп.",
        ("Куда я хочу прийти, если убрать желание просто победить кого-то?",
         "Какие два стремления тянут меня в разные стороны?",
         "По каким признакам я замечу, что пора снизить скорость?")),
    "major-08": ("sila", "♌", "Мягкая стойкость", "выдержка, терпение и внутренняя сила",
        "Сила показывает выдержку, которая позволяет встретить сильные чувства без борьбы с собой. Её мягкость не отменяет границ: принять живой характер другого человека не значит терпеть всё подряд.",
        "Прежде чем отвечать на давление, дайте себе время заметить гнев, усталость или страх. Выберите спокойный, твёрдый ответ и берегите силы: терпение не требует отказываться от уважения к себе.",
        ("Какое чувство я пытаюсь подавить вместо того, чтобы его понять?",
         "Как прозвучит мой твёрдый ответ без угроз и нажима?",
         "Где моё терпение перестало быть бережным по отношению ко мне?")),
    "major-09": ("otshelnik", "✴", "Поиск в тишине", "уединение и поиск своего ответа",
        "Отшельник предлагает отойти от чужих голосов, чтобы разобраться в собственном опыте. Такая пауза приносит ясность, пока уединение остаётся осознанным выбором и не превращается в отказ от связи с людьми.",
        "Выделите время без спешки и лишних разговоров для вопроса, который давно обходите. Сохраните связь с близкими и определите, ради чего берёте паузу: тишина должна помогать жить дальше.",
        ("На какой вопрос я всё ещё жду чужого ответа, хотя нужен мой собственный?",
         "Что я понимаю о себе, когда перестаю заполнять каждую паузу делами?",
         "С кем мне важно сохранить связь во время уединения?")),
    "major-10": ("koleso-fortuny", "☸", "Поворот обстоятельств", "перемены и повторяющиеся циклы",
        "Колесо фортуны напоминает, что обстоятельства меняются даже без нашего разрешения. Карта помогает заметить открывшуюся возможность и отделить доступное действие от попытки управлять случайностью.",
        "Посмотрите, что уже изменилось, и скорректируйте планы под новые условия. Используйте удачный момент, сохраняя запас сил на задержки: один поворот обстоятельств не определяет весь путь.",
        ("Какая перемена уже произошла, хотя я продолжаю планировать по-старому?",
         "Какой повторяющийся круг событий я могу заметить в своей жизни?",
         "Что зависит от моего выбора, а что сейчас придётся принять?")),
    "major-11": ("spravedlivost", "⚖", "Честный итог", "честность и последствия решений",
        "Справедливость предлагает посмотреть на ситуацию без скидки на симпатии и удобные объяснения. Она связывает решение с его последствиями и возвращает вопрос о том, насколько честны условия для всех участников.",
        "Соберите факты, проверьте договорённости и признайте свою часть в происходящем. Оценивайте чужие и собственные поступки по одной мерке, даже если такой итог не самый удобный.",
        ("Какие факты я оставляю за скобками, потому что они мне невыгодны?",
         "Применяю ли я к себе те же требования, что к другому человеку?",
         "Какое последствие моего решения пора признать и исправить?")),
    "major-12": ("poveshennyj", "⟡", "Пауза и переоценка", "пауза и новый взгляд на ситуацию",
        "Повешенный меняет точку зрения, когда привычное усилие уже не помогает. Его остановка может принести понимание, если вы знаете, ради чего ждёте и чем готовы поступиться.",
        "Используйте задержку, чтобы пересмотреть подход и собрать недостающие сведения. Честно оцените цену ожидания: если пауза больше ничего не открывает, назовите решение, которое откладываете.",
        ("Что становится видно, если посмотреть на эту историю с другой стороны?",
         "Ради чего я согласился ждать и сохраняется ли этот смысл?",
         "Чем я жертвую сейчас и действительно ли это мой выбор?")),
    "major-13": ("smert", "❧", "Завершение и переход", "завершение этапа и глубокая перемена",
        "Смерть говорит о завершении, после которого прежний порядок уже не вернуть. В трактовках этого аркана важно освободить место для следующего этапа и не тратить все силы на удержание отжившего.",
        "Назовите, что уже закончилось, и позвольте себе прожить расставание с этим этапом. Заберите полезный опыт, завершите доступные дела и постепенно освобождайте место для нового.",
        ("Что я продолжаю удерживать, хотя прежней жизни в этом уже нет?",
         "Какой опыт завершившегося этапа я хочу взять с собой?",
         "Какое небольшое действие поможет признать переход?")),
    "major-14": ("umerennost", "≈", "Мера и согласие", "равновесие, мера и терпение",
        "Умеренность ищет сочетание, в котором разные потребности могут сосуществовать. Она предлагает менять пропорции постепенно и замечать, где привычный ритм требует более бережной настройки.",
        "Посмотрите, чего в повседневности стало слишком много, а чему совсем не остаётся места. Внесите одно посильное изменение и дайте ему время, вместо того чтобы исправлять всё резким рывком.",
        ("Чему в моём дне достаётся слишком много места, а чему слишком мало?",
         "Какие противоположные потребности можно согласовать без крайностей?",
         "Какое небольшое изменение я смогу поддерживать спокойно и регулярно?")),
    "major-15": ("dyavol", "♑", "Привязанности и соблазн", "привязанности и возвращение свободы",
        "Дьявол высвечивает желания и привычки, которые незаметно начинают распоряжаться выбором. Возможность освобождения появляется, когда человек видит цену своей привязанности и перестаёт называть её неизбежностью.",
        "Посмотрите без оправданий, что удерживает вас в повторяющемся сценарии и какую выгоду вы из него получаете. Назовите его цену и найдите первый доступный способ вернуть себе выбор.",
        ("Какое «я должен» на деле скрывает сильную привязанность?",
         "Что даёт мне этот сценарий и чем за это приходится платить?",
         "Какой доступный отказ вернёт мне немного свободы?")),
    "major-16": ("bashnya", "ϟ", "Крушение иллюзий", "внезапные перемены и крушение иллюзий",
        "Башня показывает момент, когда прежние представления перестают выдерживать встречу с реальностью. Резкая перемена заставляет увидеть слабое основание и искать опору в том, что действительно осталось.",
        "Признайте факты, даже если они ломают привычное объяснение происходящего. Сосредоточьтесь на ближайших необходимых действиях и не спешите восстанавливать прежний порядок, не разобравшись в его слабых местах.",
        ("Какое представление о ситуации больше не выдерживает проверки?",
         "На что я всё ещё могу опереться после этой перемены?",
         "Что нельзя повторять, когда я начну выстраивать жизнь заново?")),
    "major-17": ("zvezda", "☆", "Надежда и восстановление", "надежда и постепенное восстановление",
        "Звезда возвращает способность смотреть дальше пережитой трудности. Её надежда раскрывается в бережном восстановлении и небольших действиях, которые снова делают будущее желанным.",
        "Дайте место занятиям и отношениям, после которых появляется тихая уверенность в завтрашнем дне. Не требуйте от себя немедленного подъёма: поддерживайте надежду простыми, регулярными шагами.",
        ("Что помогает мне снова верить в возможность хорошего?",
         "Какую мечту я могу бережно вернуть в свою жизнь?",
         "По какому небольшому признаку я замечаю, что восстанавливаюсь?")),
    "major-18": ("luna", "☽", "Чувства и неизвестность", "интуиция, страхи и неясность",
        "Луна описывает состояние, в котором чувства сильны, а сведений недостаточно. Она приглашает прислушаться к внутреннему миру и при этом проверять догадки, чтобы тревога не выдавала себя за знание.",
        "Запишите отдельно известные факты, свои предположения и страхи. Не торопитесь с выводами, пока картина не прояснилась, и задавайте прямые вопросы там, где воображение заполняет пробелы.",
        ("Чего я боюсь в этой ситуации и какие факты поддерживают этот страх?",
         "Как я отличаю тихое предчувствие от тревожного повторения одной мысли?",
         "Какой вопрос поможет прояснить то, о чём я сейчас только догадываюсь?")),
    "major-19": ("solnce", "☀", "Ясность и радость", "ясность, жизненная сила и радость",
        "Солнце приносит ощущение ясности, когда можно открыто радоваться жизни и результатам своих усилий. Если удовольствие потускнело, карта предлагает снова заметить то хорошее, что уже рядом.",
        "Признайте свой успех и разделите радость с теми, кто вам дорог. Оставьте место игре и простым удовольствиям, не превращая хорошее настроение в ещё одну обязанность.",
        ("Какому своему достижению я ещё не позволил себя порадовать?",
         "С кем мне хочется разделить тепло и хорошую новость?",
         "Что приносит мне удовольствие без необходимости что-то заслуживать?")),
    "major-20": ("sud", "♬", "Пробуждение и отклик", "переоценка жизни и новый отклик",
        "Суд зовёт пересмотреть прожитое и услышать направление, которое уже трудно игнорировать. Честный итог здесь нужен для обновления: осознанный опыт помогает ответить на зов действием.",
        "Подведите итог без самооправдания и бесконечного обвинения себя. Выделите то, что опыт просит изменить сейчас, и сделайте шаг, который давно откладывали после этого понимания.",
        ("Какое понимание своей жизни я больше не могу откладывать в сторону?",
         "Что я могу вынести из прошлого, перестав снова судить себя за него?",
         "Каким действием я отвечу на давно назревший внутренний зов?")),
    "major-21": ("mir", "◎", "Целостность и завершение", "завершение цикла и собранный опыт",
        "Мир собирает пройденный путь в ощущение целостности: сделанное можно признать завершённым. Карта помогает заметить последний незакрытый шаг и войти в новый этап с опытом, который уже стал вашим.",
        "Завершите оставшийся шаг и отметьте, чему научились на этом пути. Дайте себе почувствовать итог, прежде чем искать следующую вершину: завершение тоже заслуживает времени и внимания.",
        ("Какой последний шаг отделяет меня от настоящего завершения?",
         "Какие разные части опыта теперь складываются для меня в одно целое?",
         "Как я хочу отметить итог, прежде чем начинать следующий путь?")),
}

SUIT_ORDER = ("wands", "cups", "swords", "pentacles")
SUIT_RU = {"wands": "Жезлы", "cups": "Кубки", "swords": "Мечи", "pentacles": "Пентакли"}
SUIT_ELEMENT = {"wands": "Огонь", "cups": "Вода", "swords": "Воздух", "pentacles": "Земля"}
RANK_RU = {"ace": "Туз", "two": "Двойка", "three": "Тройка", "four": "Четвёрка",
           "five": "Пятёрка", "six": "Шестёрка", "seven": "Семёрка", "eight": "Восьмёрка",
           "nine": "Девятка", "ten": "Десятка", "page": "Паж", "knight": "Рыцарь",
           "queen": "Королева", "king": "Король"}
ROMAN = ("0", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
         "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI")
RANK_ROMAN = {"ace": "I", "two": "II", "three": "III", "four": "IV", "five": "V",
              "six": "VI", "seven": "VII", "eight": "VIII", "nine": "IX", "ten": "X",
              "page": "XI", "knight": "XII", "queen": "XIII", "king": "XIV"}

# Секции позиции с иконками — как в модалке на главной.
POSITION_SECTIONS = (
    ("archetype", "✧", "Архетип и основное значение"),
    ("daily",     "🏠", "В быту"),
    ("career",    "💼", "Работа и карьера"),
    ("love",      "❤", "Отношения"),
    ("health",    "🌿", "Здоровье"),
    ("esoteric",  "🔮", "Эзотерическое значение"),
)

ROMAN_SECTIONS_FULL = (
    ("Суть карты", "✧"),
    ("Прямое положение", "☀"),
    ("Негативное значение", "☾"),
    ("Акценты и фишки школы", "★"),
    ("Ключевые слова", "🗝"),
)


def paragraphs(value: str) -> str:
    return "\n".join(f"<p>{escape(part.strip())}</p>"
                     for part in re.split(r"\n\s*\n", value) if part.strip())


def bullet_list(value: str) -> str:
    """Тексты школы содержат строки «• …» — превращаем их в список."""
    parts = [p.strip().lstrip("•").strip() for p in re.split(r"\n\s*\n|\n", value) if p.strip()]
    if len(parts) > 1 and any(p.startswith(("•", "-")) for p in re.split(r"\n\s*\n|\n", value)):
        items = "".join(f"<li>{escape(p.lstrip('•').strip())}</li>" for p in parts if p.lstrip("•").strip())
        return f"<ul class=\"st-list\">{items}</ul>"
    return paragraphs(value)


def slug_for(card: dict) -> str:
    if card["type"] == "major":
        return EDITORIAL[card["id"]][0]
    return card["id"]


def load_cards() -> list[dict]:
    cards: list[dict] = []
    for filename in ("major-0-10.json", "major-11-21.json", "wands.json", "cups.json",
                     "swords.json", "pentacles.json"):
        cards.extend(json.loads((ROOT / "data" / filename).read_text(encoding="utf-8")))
    ids = [c["id"] for c in cards]
    if len(ids) != 78 or len(set(ids)) != 78:
        raise ValueError("Ожидались 78 карт с уникальными id")
    for card in cards:
        for position in ("upright", "reversed"):
            for field in ("short", "keywords", "archetype"):
                if position == "upright" or field != "keywords":
                    pass
            for field in ("short", "archetype", "daily", "career", "love", "health", "esoteric"):
                value = card[position].get(field)
                if not isinstance(value, str) or not value.strip():
                    raise ValueError(f"{card['id']}: пустое поле {position}.{field}")
            words = card[position]["keywords"]
            if not isinstance(words, list) or not words or not all(isinstance(w, str) and w.strip() for w in words):
                raise ValueError(f"{card['id']}: неверные ключевые слова")
    return cards


def load_roman() -> dict[str, dict]:
    text = (ROOT / "js" / "data_roman.js").read_text(encoding="utf-8")
    data = json.loads(text[text.find("["): text.rfind("]") + 1])
    return {row["id"]: row for row in data}


def position_html(card: dict, position: str, pane_id: str) -> str:
    data = card[position]
    pane_class = "pane-reversed" if position == "reversed" else "pane-upright"
    keywords = "".join(f"<span class=\"kw\">{escape(w)}</span>" for w in data["keywords"])
    parts = [f"<div class=\"pos-pane {pane_class}\" id=\"{pane_id}\" role=\"tabpanel\">"]
    parts.append(f"<div class=\"kw-row\">{keywords}</div>")
    parts.append(f"<p class=\"short-value\">{escape(data['short'])}</p>")
    gd = data.get("gd")
    if gd:
        parts.append(
            "<aside class=\"gd-block\" aria-label=\"Значение карты по ордену Золотая Заря\">"
            "<div class=\"gd-head\"><span class=\"gd-symbol\" aria-hidden=\"true\">☉</span> По ордену «Золотая Заря»</div>"
            f"<p class=\"gd-title\">«{escape(gd['title_en'])}» — {escape(gd['title_ru'])}</p>"
            f"<p class=\"gd-why\">{escape(gd['why'])}</p></aside>")
    for field, icon, title in POSITION_SECTIONS:
        parts.append(
            "<div class=\"info-section\">"
            f"<h3><span aria-hidden=\"true\">{icon}</span> {escape(title)}</h3>"
            f"{paragraphs(data[field])}</div>")
    parts.append("</div>")
    return "\n".join(parts)


def roman_html(card: dict, roman: dict | None) -> str:
    parts = ["<div class=\"pos-pane pane-roman roman-content\" id=\"pane-roman\" role=\"tabpanel\">"]
    if not roman:
        parts.append("<p class=\"short-value\">Для этой карты материалы школы Современного Таро пока не готовы.</p>")
    else:
        is_minor = card["type"] != "major"
        parts.append(f"<h3 class=\"roman-subtitle\"><span>🌿</span> "
                     f"{'Как школа читает этот ранг' if is_minor else 'Кратко и просто'}</h3>")
        for block in roman["simple"]:
            parts.append(f"<div class=\"info-section\"><h3>{escape(block['t'])}</h3>{paragraphs(block['x'])}</div>")
        astro = roman.get("astro")
        if astro:
            classic = (f"<div class=\"ra-classic\">У классики Уэйта: {escape(astro['classic'])}</div>"
                       if astro.get("classic") else "")
            parts.append(
                "<div class=\"roman-astro\">"
                "<span class=\"ra-label\">✷ Астрология школы</span>"
                f"<b>{escape(astro['pos'])}</b><span class=\"ra-sep\">·</span>{escape(astro['planets'])}"
                f"{classic}</div>")
        parts.append(f"<h3 class=\"roman-subtitle\"><span>📜</span> "
                     f"{'Развёрнуто — из лекции по рангу' if is_minor else 'Развёрнуто — выжимки лекций'}</h3>")
        for sec, icon in ROMAN_SECTIONS_FULL:
            text = roman["full"].get(sec)
            if not text:
                continue
            parts.append(
                f"<details class=\"roman-details\"{' open' if sec == 'Суть карты' else ''}>"
                f"<summary><span class=\"rd-icon\" aria-hidden=\"true\">{icon}</span> {escape(sec)}</summary>"
                f"<div class=\"rd-body\">{bullet_list(text)}</div></details>")
    parts.append("</div>")
    return "\n".join(parts)


def meta_description(card: dict, cards: list[dict]) -> str:
    name = card["name_ru"]
    if card["type"] == "major":
        idea = EDITORIAL[card["id"]][3]
        prefix = f"{name} — {idea}. "
        endings = (
            "Значение карты Таро в прямом и перевёрнутом положении, в любви и карьере. Совет карты и вопросы для размышления.",
            "Прямое и перевёрнутое значение карты Таро, толкование в любви и карьере, совет и вопросы для размышления.",
            "Прямое и перевёрнутое положение, любовь и карьера. Толкование карты Таро, совет и вопросы для размышления.",
        )
        for ending in endings:
            result = prefix + ending
            if 140 <= len(result) <= 160:
                return result
        raise ValueError(f"Описание {name}: нужна фраза длиной 140–160 символов")
    suit = SUIT_RU[card["suit"]]
    element = SUIT_ELEMENT[card["suit"]]
    candidates = (
        f"{name} — значение карты Таро младшего аркана: масть {suit.lower()}, стихия {element.lower()}. Толкование в прямом и перевёрнутом положении, в любви и работе.",
        f"{name} (масть {suit.lower()}, стихия {element.lower()}): значение в прямом и перевёрнутом положении. Толкование карты Таро в любви, работе и повседневных делах.",
        f"Значение карты Таро {name} младшего аркана: масть {suit.lower()}, стихия {element.lower()}. Прямое и перевёрнутое толкование, любовь, работа и бытовые вопросы.",
        f"{name} — толкование карты Таро младшего аркана колоды Уэйта. Значения в прямом и перевёрнутом положении, в любви, карьере и быту.",
        f"{name} — полное значение карты Таро младшего аркана колоды Уэйта: толкование в прямом и перевёрнутом положении, в любви, работе, здоровье и быту.",
    )
    for candidate in candidates:
        if 140 <= len(candidate) <= 160:
            return candidate
    raise ValueError(f"Описание {name}: не подобрана фраза 140–160 символов: {[len(c) for c in candidates]}")


def hero_title(card: dict) -> str:
    if card["type"] == "major":
        return f"<span class=\"card-number\">{ROMAN[card['number']]}</span>{escape(card['name_ru'])}"
    rank_slug = card["id"].rsplit("-", 1)[1]
    return f"<span class=\"card-number\">{RANK_ROMAN[rank_slug]}</span>{escape(card['name_ru'])}"


def eyebrow_for(card: dict) -> str:
    if card["type"] == "major":
        return f"Старший аркан · {ROMAN[card['number']]}"
    return f"Младший аркан · {SUIT_RU[card['suit']]}"


def meta_line(card: dict) -> str:
    parts = []
    if card["type"] == "major":
        if card.get("element"):
            parts.append(f"Стихия: <b>{escape(card['element'])}</b>")
        if card.get("astro"):
            parts.append(f"Астрология: <b>{escape(card['astro'])}</b>")
    else:
        parts.append(f"Масть: <b>{SUIT_RU[card['suit']]}</b>")
        parts.append(f"Стихия: <b>{SUIT_ELEMENT[card['suit']]}</b>")
        if card.get("astro"):
            parts.append(f"Классика: <b>{escape(card['astro'])}</b>")
    return " &nbsp;·&nbsp; ".join(parts)


def render_card(card: dict, cards: list[dict], roman: dict[str, dict]) -> str:
    idx = cards.index(card)
    slug = slug_for(card)
    name = card["name_ru"]
    prev, nxt = cards[(idx - 1) % 78], cards[(idx + 1) % 78]
    title = f"{name} — значение и толкование | Таро Справочник"
    description = meta_description(card, cards)
    roman_data = roman.get(card["id"])
    roman_tab = (
        "\n<label class=\"pos-tab pos-tab-school\" for=\"pos-roman\">Школа Современного Таро</label>"
        if roman_data else "")
    roman_input = ('<input class="pos-state s-roman" type="radio" name="pos" id="pos-roman">\n' if roman_data else "")
    body = f"""<main class="card-page">
<nav class="card-crumbs" aria-label="Хлебные крошки"><a href="/">Главная</a> / <a href="/cards/">Карты</a> / <span aria-current="page">{escape(name)}</span></nav>
<article class="tarot-sheet">
<header class="modal-head">
<div class="card-scene"><img src="/img/cards/{escape(card['img'])}" alt="{escape(name)} — карта Таро Уэйта" width="132" height="211"></div>
<div class="head-info">
<p class="m-arcana">{escape(eyebrow_for(card))}</p>
<h1 class="m-title">{hero_title(card)}</h1>
<p class="m-en">{escape(card['name_en'])}</p>
<p class="m-meta">{meta_line(card)}</p>
</div>
</header>
<input class="pos-state s-upright" type="radio" name="pos" id="pos-upright" checked>
<input class="pos-state s-reversed" type="radio" name="pos" id="pos-reversed">
{roman_input}<div class="pos-tabs" role="tablist" aria-label="Положения карты">
<label class="pos-tab" for="pos-upright">Прямое положение</label>
<label class="pos-tab" for="pos-reversed">Перевёрнутое положение</label>{roman_tab}
</div>
{position_html(card, 'upright', 'pane-upright')}
{position_html(card, 'reversed', 'pane-reversed')}
{roman_html(card, roman_data)}
<nav class="card-pagination" aria-label="Предыдущая и следующая карта">
<a rel="prev" href="{slug_for(prev)}.html"><span>← Предыдущая карта</span>{escape(prev['name_ru'])}</a>
<a rel="next" href="{slug_for(nxt)}.html"><span>Следующая карта →</span>{escape(nxt['name_ru'])}</a>
</nav>
</article>
</main>"""
    return document(title, description, f"{SITE}/cards/{slug}.html", body, True, card["img"])


def render_index(cards: list[dict], roman: dict[str, dict]) -> str:
    suits = [("major", "Старшие арканы")] + [(s, f"Масть {SUIT_RU[s]}") for s in SUIT_ORDER]
    groups = []
    for suit, label in suits:
        subset = [c for c in cards if (c["type"] == "major") == (suit == "major")
                  and (suit == "major" or c["suit"] == suit)]
        tiles = []
        for card in subset:
            slug = slug_for(card)
            rank_label = ROMAN[card["number"]] if card["type"] == "major" else RANK_ROMAN[card["id"].rsplit("-", 1)[1]]
            tiles.append(
                f"<li><a class=\"card-tile\" href=\"{slug}.html\">"
                f"<img src=\"/img/cards/{escape(card['img'])}\" alt=\"{escape(card['name_ru'])}\" loading=\"lazy\" width=\"132\" height=\"211\">"
                f"<span class=\"card-tile-number\">{rank_label}</span>"
                f"<strong>{escape(card['name_ru'])}</strong></a></li>")
        groups.append(f"<h2 class=\"suit-title\">{escape(label)}</h2>\n<ol class=\"card-grid\" aria-label=\"{escape(label)}\">\n"
                      + "\n".join(tiles) + "\n</ol>")
    body = """<main class="card-page card-catalog">
<nav class="card-crumbs" aria-label="Хлебные крошки"><a href="/">Главная</a> / <span aria-current="page">Карты</span></nav>
<header class="card-hero">
<span class="card-symbol" aria-hidden="true">✦</span>
<p class="card-eyebrow">Все 78 карт колоды Уэйта</p>
<h1>Карты Таро: значения и толкования</h1>
<p>Выберите карту: её значения, школа и подробное досье на отдельной странице.</p>
</header>
""" + "\n".join(groups) + "\n</main>"
    description = ("Все 78 карт Таро колоды Уэйта: старшие и младшие арканы. Значения карт в прямом и перевёрнутом "
                   "положении, в любви и карьере, толкования школы Современного Таро и ордена Золотая Заря.")
    return document("Карты Таро — значения всех 78 карт | Таро Справочник",
                    description, f"{SITE}/cards/", body, False)


STYLE = """
.main-nav-inner { flex-wrap: wrap; justify-content: center; border-radius: 24px; }
.card-page { position: relative; z-index: 1; max-width: 900px; margin: 0 auto; padding: 28px 24px 48px; }
.card-page a { color: var(--gold-bright); text-underline-offset: .2em; }
.card-page a:focus-visible, .main-nav a:focus-visible { outline: 2px solid var(--gold-bright); outline-offset: 5px; }
.card-crumbs { color: var(--text-dim); font-size: .9rem; margin-bottom: 28px; }
/* ── Лист карты в дизайне модалки ── */
.tarot-sheet { max-width: 760px; margin: 0 auto; background: linear-gradient(170deg, var(--bg-panel), #120e24);
  border: 1px solid rgba(212,175,55,.28); border-radius: 20px; padding: 26px 22px 30px;
  box-shadow: var(--shadow), 0 0 60px rgba(124,92,191,.15); }
.tarot-sheet .modal-head { display: flex; gap: 24px; align-items: center; margin-bottom: 20px; }
.tarot-sheet .card-scene { flex-shrink: 0; }
.tarot-sheet .card-scene img { width: 132px; aspect-ratio: 400/640; object-fit: cover; display: block;
  border-radius: 10px; border: 1px solid var(--gold-dim); box-shadow: 0 6px 22px rgba(0,0,0,.55); }
.head-info { min-width: 0; }
.m-arcana { font-size: .8rem; letter-spacing: .25em; text-transform: uppercase; color: var(--accent-purple); margin-bottom: 4px; }
.m-title { font-family: 'Cormorant Garamond', Georgia, serif; font-weight: 700;
  font-size: clamp(1.7rem, 5vw, 2.3rem); color: var(--gold-bright); line-height: 1.15; }
.card-number { display: block; font-size: 2rem; color: var(--gold); margin-bottom: 4px; }
.m-en { color: var(--text-dim); font-style: italic; margin: 2px 0 8px; }
.m-meta { font-size: .92rem; color: var(--text-dim); }
.m-meta b { color: var(--text); font-weight: 500; }
/* ── Вкладки положений: radio + :checked, работают без JS ── */
.pos-tabs { display: flex; flex-wrap: wrap; gap: 6px; border-bottom: 1px solid rgba(212,175,55,.18); margin-bottom: 18px; }
.pos-tab { padding: 10px 20px; border: none; border-bottom: 2px solid transparent; color: var(--text-dim);
  font-family: inherit; font-size: 1rem; cursor: pointer; transition: all .25s; background: none; display: block; }
.pos-tab:hover { color: var(--text); }
.tarot-sheet .pos-state { position: absolute; opacity: 0; pointer-events: none; }
.tarot-sheet .pos-state.s-upright:checked ~ .pos-tabs label[for="pos-upright"],
.tarot-sheet .pos-state.s-reversed:checked ~ .pos-tabs label[for="pos-reversed"] {
  color: var(--gold-bright); border-bottom-color: var(--gold); text-shadow: 0 0 12px rgba(212,175,55,.4); }
.tarot-sheet .pos-state.s-roman:checked ~ .pos-tabs label[for="pos-roman"] {
  color: #cdbef0; border-bottom-color: var(--accent-purple); text-shadow: 0 0 12px rgba(124,92,191,.55); }
.pos-pane { display: none; animation: sheet-fade .3s ease; }
.tarot-sheet .pos-state.s-upright:checked ~ .pos-pane.pane-upright { display: block; }
.tarot-sheet .pos-state.s-reversed:checked ~ .pos-pane.pane-reversed { display: block; }
.tarot-sheet .pos-state.s-roman:checked ~ .pos-pane.pane-roman { display: block; }
@keyframes sheet-fade { from { opacity: 0; } to { opacity: 1; } }
/* ── Контент позиции (общие классы из style.css) ── */
.kw-row { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
.short-value { font-family: 'Cormorant Garamond', Georgia, serif; font-size: 1.18rem; font-style: italic;
  color: var(--gold-bright); padding: 12px 18px; border-left: 3px solid var(--gold);
  background: rgba(212,175,55,.06); border-radius: 0 10px 10px 0; margin-bottom: 20px; line-height: 1.5; }
.gd-block { padding: 16px 18px; border: 1px solid rgba(240,201,79,.5); border-left: 5px solid var(--gold-bright);
  background: linear-gradient(135deg, rgba(212,175,55,.18), rgba(124,92,191,.12));
  border-radius: 0 12px 12px 0; margin: 0 0 22px; color: var(--text);
  box-shadow: inset 0 0 24px rgba(212,175,55,.08), 0 7px 22px rgba(0,0,0,.2); }
.gd-head { font-size: .86rem; font-weight: 700; text-transform: uppercase; letter-spacing: .12em;
  color: var(--gold-bright); margin-bottom: 8px; }
.gd-symbol { display: inline-block; margin-right: 5px; }
.gd-title { font-family: 'Cormorant Garamond', Georgia, serif; font-size: 1.15rem; font-weight: 600;
  font-style: italic; color: var(--gold-bright); margin-bottom: 7px; }
.gd-why { font-size: .98rem; color: #f1ebf7; line-height: 1.6; }
.info-section { margin-bottom: 20px; }
.info-section h3 { font-family: 'Cormorant Garamond', Georgia, serif; font-size: 1.22rem; font-weight: 600;
  letter-spacing: .04em; color: var(--gold); margin-bottom: 7px; display: flex; align-items: center; gap: 9px; }
.info-section h3::after { content: ''; flex: 1; height: 1px; background: linear-gradient(90deg, var(--gold-dim), transparent); }
.info-section p { white-space: pre-line; color: var(--text); font-size: .98rem; }
.kw { padding: 5px 14px; border-radius: 999px; background: rgba(124,92,191,.16);
  border: 1px solid rgba(124,92,191,.4); color: #cdbef0; font-size: .85rem; }
/* ── Школа Современного Таро ── */
.roman-subtitle { display: flex; align-items: center; gap: 9px; font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 1.28rem; font-weight: 600; letter-spacing: .04em; color: #cdbef0; margin: 22px 0 4px; }
.roman-subtitle::after { content: ''; flex: 1; height: 1px; background: linear-gradient(90deg, rgba(124,92,191,.45), transparent); }
.roman-content .info-section h3, .pane-roman .info-section h3 { color: #b7a5e8; font-size: 1.08rem; }
.roman-details { border: 1px solid rgba(124,92,191,.3); border-radius: 10px; margin-bottom: 10px;
  background: rgba(124,92,191,.07); overflow: hidden; }
.roman-details summary { list-style: none; cursor: pointer; display: flex; align-items: center; gap: 10px;
  padding: 11px 14px; font-family: 'Cormorant Garamond', Georgia, serif; font-size: 1.12rem; font-weight: 600;
  letter-spacing: .03em; color: #cdbef0; user-select: none; transition: background .2s; }
.roman-details summary::-webkit-details-marker { display: none; }
.roman-details summary::after { content: '▾'; margin-left: auto; color: var(--accent-purple); transition: transform .25s; flex-shrink: 0; }
.roman-details[open] summary::after { transform: rotate(180deg); }
.roman-details summary:hover { background: rgba(124,92,191,.12); }
.rd-icon { width: 1.2em; text-align: center; color: var(--accent-purple); }
.rd-body { padding: 4px 16px 14px; border-top: 1px solid rgba(124,92,191,.18); }
.rd-body p { white-space: normal; color: var(--text); font-size: .95rem; line-height: 1.6; margin-top: 10px; }
.rd-body p:first-child { margin-top: 8px; }
.roman-astro { margin: 14px 0 4px; padding: 10px 14px; border-radius: 10px;
  border: 1px solid rgba(124,92,191,.3); background: rgba(124,92,191,.1);
  font-size: .9rem; color: var(--text); line-height: 1.55; }
.ra-label { display: block; font-size: .72rem; letter-spacing: .22em; text-transform: uppercase;
  color: var(--accent-purple); margin-bottom: 3px; }
.roman-astro b { color: #cdbef0; font-weight: 600; }
.ra-sep { margin: 0 7px; color: var(--accent-purple); }
.ra-classic { margin-top: 6px; padding-top: 6px; border-top: 1px dashed rgba(124,92,191,.3);
  border-top: 1px dashed rgba(124,92,191,.3); font-size: .82rem; color: var(--text-dim); }
/* ── Каталог ── */
.suit-title, .card-catalog h2 { color: var(--gold-bright); font-family: Georgia, serif; font-weight: 500;
  font-size: 1.6rem; margin: 34px 0 18px; }
.card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 14px; list-style: none; }
.card-grid li { min-width: 0; }
.card-tile { display: flex; flex-direction: column; align-items: center; height: 100%; padding: 16px 12px;
  border: 1px solid var(--gold-dim); border-radius: var(--radius); background: var(--bg-panel);
  text-decoration: none; text-align: center; }
.card-tile img { width: 100%; max-width: 120px; aspect-ratio: 400/640; object-fit: cover; border-radius: 8px;
  border: 1px solid var(--gold-dim); }
.card-tile-number { color: var(--text-dim); font-size: .8rem; margin: 12px 0 4px; }
.card-tile strong { font-family: Georgia, serif; font-size: 1.05rem; font-weight: 500; color: var(--gold-bright); }
.card-tile:hover { background: var(--bg-hover); border-color: var(--gold); }
.card-pagination { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 32px; }
.card-pagination a { padding: 20px; border: 1px solid var(--gold-dim); border-radius: var(--radius);
  text-decoration: none; background: var(--bg-panel); }
.card-pagination a:last-child { text-align: right; }
.card-pagination span { display: block; font-size: .8rem; color: var(--text-dim); margin-bottom: 6px; }
.card-pagination a:hover { background: var(--bg-hover); border-color: var(--gold); }
@media (max-width: 480px) {
  .main-nav { padding: 12px 12px 0; }
  .main-nav a { padding: 8px 12px; font-size: .9rem; }
  .card-page { padding: 22px 12px 36px; }
  .tarot-sheet { padding: 20px 14px 24px; }
  .tarot-sheet .modal-head { flex-wrap: nowrap; align-items: flex-start; gap: 12px; margin-bottom: 12px; }
  .tarot-sheet .card-scene img { width: 96px; }
  .pos-tab { padding: 9px 12px; font-size: .9rem; }
  .pos-tab-school { margin-left: 0; flex-basis: 100%; text-align: left; padding-left: 12px; }
  .card-pagination { gap: 10px; }
  .card-pagination a { padding: 16px 12px; }
}
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } .stars2 { animation: none; } }
"""

NAV = """<nav class="main-nav" aria-label="Разделы">
  <div class="main-nav-inner">
    <a href="/">Главная</a>
    <a href="/cards/" class="mn-active">Карты</a>
    <a href="/astrology/">Астрология</a>
    <a href="/lenormand/">Ленорман</a>
    <a href="/runes/">Руны</a>
    <a href="/spreads.html">Расклады</a>
  </div>
</nav>"""


def document(title: str, description: str, url: str, body: str, article: bool, og_img: str = "") -> str:
    structured = {
        "@context": "https://schema.org",
        "@type": "Article" if article else "CollectionPage",
        "headline" if article else "name": title,
        "description": description,
        "url": url,
        "inLanguage": "ru",
    }
    schema = json.dumps(structured, ensure_ascii=False, indent=2).replace("<", "\\u003c")
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description, quote=True)}">
<link rel="canonical" href="{escape(url, quote=True)}">
<meta property="og:title" content="{escape(title, quote=True)}">
<meta property="og:description" content="{escape(description, quote=True)}">
<meta property="og:type" content="{'article' if article else 'website'}">
<meta property="og:url" content="{escape(url, quote=True)}">
{f'<meta property="og:image" content="{SITE}/img/cards/{escape(og_img, quote=True)}">' if og_img else ''}
<link rel="stylesheet" href="/css/style.css?v=3.4">
<link rel="stylesheet" href="/css/astrology.css?v=3.4">
<style>{STYLE}</style>
<script type="application/ld+json">
{schema}
</script>
<!-- Microsoft Clarity -->
<script>
    (function(c,l,a,r,i,t,y){{
        c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};
        t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i+"?ref=bwt";
        y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
    }})(window, document, "clarity", "script", "yejlmmd6nr");
</script>
</head>
<body>
<div class="stars" aria-hidden="true"></div>
<div class="stars stars2" aria-hidden="true"></div>
{NAV}
{body}
<footer class="site-footer">
  <p>Таро · Справочник значений карт</p>
  <p class="footer-note">Материалы носят справочный и развлекательный характер</p>
</footer>
</body>
</html>
"""


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    cards = load_cards()
    roman = load_roman()
    pages: dict[str, str] = {}
    for card in cards:
        slug = slug_for(card)
        pages[f"{slug}.html"] = render_card(card, cards, roman)
    pages["index.html"] = render_index(cards, roman)
    if len(pages) != 79:
        raise ValueError(f"Ожидалось 79 страниц, получено {len(pages)}")
    OUTPUT.mkdir(exist_ok=True)
    for filename, html in pages.items():
        (OUTPUT / filename).write_text(html, encoding="utf-8", newline="\n")
    print(f"OK: создано {len(pages)} страниц в cards/ (78 карт + каталог).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
