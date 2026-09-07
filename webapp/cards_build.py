#!/usr/bin/env python3
"""Пилот: 22 старших аркана. Python 3, только стандартная библиотека.

Запуск из любой папки: python путь/к/webapp/cards_build.py
Читает два исходных JSON; записывает только HTML внутри webapp/cards/.
Вступления, советы (отдельного поля advice в исходниках нет) и вопросы
написаны по смыслу исходных трактовок. Даты и случайные значения не используются.
"""
from __future__ import annotations

import json
import re
import sys
from html import escape
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "cards"
SITE = "https://taro.jetserg.top"
ROMAN = ("0", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
         "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI")

# Порядок совпадает с number в JSON. Написание slug zhrefca задано в ТЗ.
# slug, символ, мини-описание, идея для meta, вступление, совет, три вопроса.
EDITORIAL = (
    (
        "durak", "☀", "Начало пути", "новый путь и доверие к жизни",
        "Дурак появляется там, где привычный опыт ещё не подсказывает ответа. Он приглашает попробовать новое, сохранив любопытство и готовность отвечать за свой шаг.",
        "Начните с небольшого опыта, для которого не нужны полная уверенность и чужое одобрение. Проверьте самое необходимое и оставьте место неожиданностям: доверие к жизни вполне уживается с внимательностью.",
        ("Что мне хочется попробовать, даже если я пока совсем не умею этого делать?",
         "Какая простая подготовка позволит мне рискнуть осознанно?",
         "Где я называю осторожностью страх показаться новичком?"),
    ),
    (
        "mag", "✦", "Воля и действие", "сосредоточенность и сила действия",
        "Маг собирает разрозненные возможности в одно точное действие. Карта напоминает, что умение становится силой, когда вы выбираете задачу и подтверждаете намерения поступками.",
        "Выберите одно дело и используйте то, что уже умеете, вместо бесконечного поиска идеального инструмента. Обещайте лишь то, что готовы сделать, и покажите результат прежде, чем рассказывать о следующем замысле.",
        ("Какой мой навык уже позволяет сдвинуть дело с места?",
         "На какие мелочи уходит внимание, нужное главной задаче?",
         "Какой поступок подтвердит мои слова сегодня?"),
    ),
    (
        "zhrefca", "☾", "Тишина и интуиция", "интуиция и внимание к скрытому",
        "Верховная жрица предлагает не торопиться с объяснениями и прислушаться к тому, что пока трудно выразить. Тишина помогает заметить скрытые мотивы, если не путать собственное чувство с догадками о других.",
        "Отложите шумные обсуждения и запишите, что вы замечаете и чувствуете наедине с собой. Дайте ответу созреть, а важные недоговорённости проясните словами: загадочность не должна заменять честность.",
        ("Какое ощущение я отбрасываю только потому, что не могу сразу его объяснить?",
         "Что я знаю о ситуации, а что лишь додумываю в тишине?",
         "Какую недосказанность пора бережно прояснить?"),
    ),
    (
        "imperatrica", "❀", "Забота и рост", "забота, творчество и изобилие",
        "Императрица говорит о росте, которому нужны внимание, время и удовольствие от процесса. Она помогает увидеть разницу между заботой, питающей жизнь, и опекой, под которой уже трудно дышать.",
        "Поддержите то, что хотите вырастить: уделите время идее, дому или близкому разговору. Не требуйте мгновенной отдачи и проверьте, остаются ли у вас силы и радость для собственной жизни.",
        ("Что в моей жизни сейчас нуждается в регулярной, простой заботе?",
         "Где я тороплю результат, которому ещё нужно время?",
         "Как я могу поддержать близкого, не делая всё за него?"),
    ),
    (
        "imperator", "♜", "Порядок и ответственность", "порядок, границы и ответственность",
        "Император превращает намерение в понятный порядок: кто решает, что обещано и где проходят границы. Его устойчивость держится на ответственности, а чрезмерное стремление командовать делает эту опору жёсткой и неудобной.",
        "Назовите правила и договорённости, на которые действительно можно опереться. Возьмите свою часть ответственности и держите слово, сохраняя возможность пересмотреть правило, если оно уже мешает делу.",
        ("В какой области мне не хватает ясных договорённостей?",
         "За какое решение я готов отвечать лично?",
         "Где полезная граница превратилась в желание всё контролировать?"),
    ),
    (
        "ierofant", "✧", "Знание и традиция", "учёба, традиция и общие ценности",
        "Иерофант обращает внимание на знания и правила, которые передаются от человека к человеку. Он предлагает найти надёжную опору в опыте других и одновременно понять, какой смысл вы сами вкладываете в выбранную традицию.",
        "Обратитесь к человеку, чей опыт можно проверить, и разберитесь в основах выбранного дела. Следуя правилу, спрашивайте себя, чему оно служит: осмысленное обучение оставляет место собственным вопросам.",
        ("У кого я могу учиться, не отказываясь от самостоятельного суждения?",
         "Какое принятое правило поддерживает мои ценности?",
         "Что я продолжаю повторять по привычке, уже не понимая смысла?"),
    ),
    (
        "vlyublyonnye", "♡", "Союз и выбор", "честный выбор и близость ценностей",
        "Влюблённые связывают близость с выбором, за которым стоят ваши ценности. Карта спрашивает, совпадает ли то, к чему тянется сердце, с тем, как вы готовы поступать каждый день.",
        "Проговорите, что для вас важно в союзе или решении, и выслушайте другую сторону. Сделайте выбор, с которым согласны и чувства, и совесть, не перекладывая его на обстоятельства.",
        ("Какие ценности я хочу сохранить в этом выборе?",
         "В чём мои поступки расходятся с тем, что я называю любовью?",
         "От какого другого пути придётся отказаться, если я скажу «да»?"),
    ),
    (
        "kolesnica", "➶", "Курс и движение", "движение к цели и самодисциплина",
        "Колесница собирает противоречивые желания вокруг выбранного направления. Она поддерживает решимость двигаться вперёд, но напоминает, что скорость полезна только тогда, когда вы управляете движением.",
        "Определите ближайшую цель и договоритесь о направлении с теми, кто участвует в деле. Если эмоции заставляют спешить или давить, сначала верните себе управление, а затем прибавляйте темп.",
        ("Куда я хочу прийти, если убрать желание просто победить кого-то?",
         "Какие два стремления тянут меня в разные стороны?",
         "По каким признакам я замечу, что пора снизить скорость?"),
    ),
    (
        "sila", "♌", "Мягкая стойкость", "выдержка, терпение и внутренняя сила",
        "Сила показывает выдержку, которая позволяет встретить сильные чувства без борьбы с собой. Её мягкость не отменяет границ: принять живой характер другого человека не значит терпеть всё подряд.",
        "Прежде чем отвечать на давление, дайте себе время заметить гнев, усталость или страх. Выберите спокойный, твёрдый ответ и берегите силы: терпение не требует отказываться от уважения к себе.",
        ("Какое чувство я пытаюсь подавить вместо того, чтобы его понять?",
         "Как прозвучит мой твёрдый ответ без угроз и нажима?",
         "Где моё терпение перестало быть бережным по отношению ко мне?"),
    ),
    (
        "otshelnik", "✴", "Поиск в тишине", "уединение и поиск своего ответа",
        "Отшельник предлагает отойти от чужих голосов, чтобы разобраться в собственном опыте. Такая пауза приносит ясность, пока уединение остаётся осознанным выбором и не превращается в отказ от связи с людьми.",
        "Выделите время без спешки и лишних разговоров для вопроса, который давно обходите. Сохраните связь с близкими и определите, ради чего берёте паузу: тишина должна помогать жить дальше.",
        ("На какой вопрос я всё ещё жду чужого ответа, хотя нужен мой собственный?",
         "Что я понимаю о себе, когда перестаю заполнять каждую паузу делами?",
         "С кем мне важно сохранить связь во время уединения?"),
    ),
    (
        "koleso-fortuny", "☸", "Поворот обстоятельств", "перемены и повторяющиеся циклы",
        "Колесо фортуны напоминает, что обстоятельства меняются даже без нашего разрешения. Карта помогает заметить открывшуюся возможность и отделить доступное действие от попытки управлять случайностью.",
        "Посмотрите, что уже изменилось, и скорректируйте планы под новые условия. Используйте удачный момент, сохраняя запас сил на задержки: один поворот обстоятельств не определяет весь путь.",
        ("Какая перемена уже произошла, хотя я продолжаю планировать по-старому?",
         "Какой повторяющийся круг событий я могу заметить в своей жизни?",
         "Что зависит от моего выбора, а что сейчас придётся принять?"),
    ),
    (
        "spravedlivost", "⚖", "Честный итог", "честность и последствия решений",
        "Справедливость предлагает посмотреть на ситуацию без скидки на симпатии и удобные объяснения. Она связывает решение с его последствиями и возвращает вопрос о том, насколько честны условия для всех участников.",
        "Соберите факты, проверьте договорённости и признайте свою часть в происходящем. Оценивайте чужие и собственные поступки по одной мерке, даже если такой итог не самый удобный.",
        ("Какие факты я оставляю за скобками, потому что они мне невыгодны?",
         "Применяю ли я к себе те же требования, что к другому человеку?",
         "Какое последствие моего решения пора признать и исправить?"),
    ),
    (
        "poveshennyj", "⟡", "Пауза и переоценка", "пауза и новый взгляд на ситуацию",
        "Повешенный меняет точку зрения, когда привычное усилие уже не помогает. Его остановка может принести понимание, если вы знаете, ради чего ждёте и чем готовы поступиться.",
        "Используйте задержку, чтобы пересмотреть подход и собрать недостающие сведения. Честно оцените цену ожидания: если пауза больше ничего не открывает, назовите решение, которое откладываете.",
        ("Что становится видно, если посмотреть на эту историю с другой стороны?",
         "Ради чего я согласился ждать и сохраняется ли этот смысл?",
         "Чем я жертвую сейчас и действительно ли это мой выбор?"),
    ),
    (
        "smert", "❧", "Завершение и переход", "завершение этапа и глубокая перемена",
        "Смерть говорит о завершении, после которого прежний порядок уже не вернуть. В трактовках этого аркана важно освободить место для следующего этапа и не тратить все силы на удержание отжившего.",
        "Назовите, что уже закончилось, и позвольте себе прожить расставание с этим этапом. Заберите полезный опыт, завершите доступные дела и постепенно освобождайте место для нового.",
        ("Что я продолжаю удерживать, хотя прежней жизни в этом уже нет?",
         "Какой опыт завершившегося этапа я хочу взять с собой?",
         "Какое небольшое действие поможет признать переход?"),
    ),
    (
        "umerennost", "≈", "Мера и согласие", "равновесие, мера и терпение",
        "Умеренность ищет сочетание, в котором разные потребности могут сосуществовать. Она предлагает менять пропорции постепенно и замечать, где привычный ритм требует более бережной настройки.",
        "Посмотрите, чего в повседневности стало слишком много, а чему совсем не остаётся места. Внесите одно посильное изменение и дайте ему время, вместо того чтобы исправлять всё резким рывком.",
        ("Чему в моём дне достаётся слишком много места, а чему слишком мало?",
         "Какие противоположные потребности можно согласовать без крайностей?",
         "Какое небольшое изменение я смогу поддерживать спокойно и регулярно?"),
    ),
    (
        "dyavol", "♑", "Привязанности и соблазн", "привязанности и возвращение свободы",
        "Дьявол высвечивает желания и привычки, которые незаметно начинают распоряжаться выбором. Возможность освобождения появляется, когда человек видит цену своей привязанности и перестаёт называть её неизбежностью.",
        "Посмотрите без оправданий, что удерживает вас в повторяющемся сценарии и какую выгоду вы из него получаете. Назовите его цену и найдите первый доступный способ вернуть себе выбор.",
        ("Какое «я должен» на деле скрывает сильную привязанность?",
         "Что даёт мне этот сценарий и чем за это приходится платить?",
         "Какой доступный отказ вернёт мне немного свободы?"),
    ),
    (
        "bashnya", "ϟ", "Крушение иллюзий", "внезапные перемены и крушение иллюзий",
        "Башня показывает момент, когда прежние представления перестают выдерживать встречу с реальностью. Резкая перемена заставляет увидеть слабое основание и искать опору в том, что действительно осталось.",
        "Признайте факты, даже если они ломают привычное объяснение происходящего. Сосредоточьтесь на ближайших необходимых действиях и не спешите восстанавливать прежний порядок, не разобравшись в его слабых местах.",
        ("Какое представление о ситуации больше не выдерживает проверки?",
         "На что я всё ещё могу опереться после этой перемены?",
         "Что нельзя повторять, когда я начну выстраивать жизнь заново?"),
    ),
    (
        "zvezda", "☆", "Надежда и восстановление", "надежда и постепенное восстановление",
        "Звезда возвращает способность смотреть дальше пережитой трудности. Её надежда раскрывается в бережном восстановлении и небольших действиях, которые снова делают будущее желанным.",
        "Дайте место занятиям и отношениям, после которых появляется тихая уверенность в завтрашнем дне. Не требуйте от себя немедленного подъёма: поддерживайте надежду простыми, регулярными шагами.",
        ("Что помогает мне снова верить в возможность хорошего?",
         "Какую мечту я могу бережно вернуть в свою жизнь?",
         "По какому небольшому признаку я замечаю, что восстанавливаюсь?"),
    ),
    (
        "luna", "☽", "Чувства и неизвестность", "интуиция, страхи и неясность",
        "Луна описывает состояние, в котором чувства сильны, а сведений недостаточно. Она приглашает прислушаться к внутреннему миру и при этом проверять догадки, чтобы тревога не выдавала себя за знание.",
        "Запишите отдельно известные факты, свои предположения и страхи. Не торопитесь с выводами, пока картина не прояснилась, и задавайте прямые вопросы там, где воображение заполняет пробелы.",
        ("Чего я боюсь в этой ситуации и какие факты поддерживают этот страх?",
         "Как я отличаю тихое предчувствие от тревожного повторения одной мысли?",
         "Какой вопрос поможет прояснить то, о чём я сейчас только догадываюсь?"),
    ),
    (
        "solnce", "☀", "Ясность и радость", "ясность, жизненная сила и радость",
        "Солнце приносит ощущение ясности, когда можно открыто радоваться жизни и результатам своих усилий. Если удовольствие потускнело, карта предлагает снова заметить то хорошее, что уже рядом.",
        "Признайте свой успех и разделите радость с теми, кто вам дорог. Оставьте место игре и простым удовольствиям, не превращая хорошее настроение в ещё одну обязанность.",
        ("Какому своему достижению я ещё не позволил себя порадовать?",
         "С кем мне хочется разделить тепло и хорошую новость?",
         "Что приносит мне удовольствие без необходимости что-то заслуживать?"),
    ),
    (
        "sud", "♬", "Пробуждение и отклик", "переоценка жизни и новый отклик",
        "Суд зовёт пересмотреть прожитое и услышать направление, которое уже трудно игнорировать. Честный итог здесь нужен для обновления: осознанный опыт помогает ответить на зов действием.",
        "Подведите итог без самооправдания и бесконечного обвинения себя. Выделите то, что опыт просит изменить сейчас, и сделайте шаг, который давно откладывали после этого понимания.",
        ("Какое понимание своей жизни я больше не могу откладывать в сторону?",
         "Что я могу вынести из прошлого, перестав снова судить себя за него?",
         "Каким действием я отвечу на давно назревший внутренний зов?"),
    ),
    (
        "mir", "◎", "Целостность и завершение", "завершение цикла и собранный опыт",
        "Мир собирает пройденный путь в ощущение целостности: сделанное можно признать завершённым. Карта помогает заметить последний незакрытый шаг и войти в новый этап с опытом, который уже стал вашим.",
        "Завершите оставшийся шаг и отметьте, чему научились на этом пути. Дайте себе почувствовать итог, прежде чем искать следующую вершину: завершение тоже заслуживает времени и внимания.",
        ("Какой последний шаг отделяет меня от настоящего завершения?",
         "Какие разные части опыта теперь складываются для меня в одно целое?",
         "Как я хочу отметить итог, прежде чем начинать следующий путь?"),
    ),
)

STYLE = """
.main-nav-inner { flex-wrap: wrap; justify-content: center; border-radius: 24px; }
.card-page { position: relative; z-index: 1; max-width: 900px; margin: 0 auto; padding: 28px 24px 48px; }
.card-page a { color: var(--gold-bright); text-underline-offset: .2em; }
.card-page a:focus-visible, .main-nav a:focus-visible { outline: 2px solid var(--gold-bright); outline-offset: 5px; }
.card-crumbs { color: var(--text-dim); font-size: .9rem; margin-bottom: 28px; }
.card-hero { text-align: center; padding: 14px 0 34px; }
.card-symbol { display: block; font-family: Georgia, serif; font-size: 5rem; line-height: 1.2; color: var(--gold-bright); text-shadow: 0 0 30px var(--gold-dim); }
.card-eyebrow { color: var(--text-dim); letter-spacing: .15em; text-transform: uppercase; font-size: .76rem; margin: 18px 0 8px; }
.card-hero h1 { font-family: Georgia, serif; font-weight: 500; font-size: clamp(2rem, 6vw, 3.3rem); line-height: 1.2; color: var(--gold-bright); overflow-wrap: anywhere; }
.card-number { display: block; font-size: 2.2rem; color: var(--gold); margin-bottom: 10px; }
.card-hero > p:last-child { margin-top: 16px; color: var(--text-dim); }
.card-section { margin: 0 0 22px; padding: 28px 32px; border: 1px solid var(--gold-dim); border-radius: var(--radius); background: rgba(23, 18, 43, .88); }
.card-section h2 { color: var(--gold-bright); font-family: Georgia, serif; font-weight: 500; font-size: 1.6rem; line-height: 1.3; margin-bottom: 18px; }
.card-section h3 { color: var(--gold-bright); font-size: 1rem; margin: 22px 0 10px; }
.card-section p + p { margin-top: 16px; }
.card-intro { background: linear-gradient(135deg, rgba(124, 92, 191, .2), var(--bg-panel)); font-size: 1.1rem; }
.card-keywords { display: flex; flex-wrap: wrap; gap: 8px; list-style: none; margin: 18px 0; }
.card-keywords li { border: 1px solid var(--gold-dim); border-radius: 999px; padding: 4px 12px; font-size: .85rem; color: var(--gold-bright); }
.card-questions { padding-left: 24px; }
.card-questions li { padding: 4px 0 10px 6px; }
.card-questions li::marker { color: var(--gold); }
.card-pagination { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 32px; }
.card-pagination a { padding: 20px; border: 1px solid var(--gold-dim); border-radius: var(--radius); text-decoration: none; background: var(--bg-panel); }
.card-pagination a:last-child { text-align: right; }
.card-pagination span { display: block; font-size: .8rem; color: var(--text-dim); margin-bottom: 6px; }
.card-pagination a:hover, .card-tile:hover { background: var(--bg-hover); border-color: var(--gold); }
.card-catalog { max-width: 1120px; }
.card-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; list-style: none; }
.card-grid li { min-width: 0; }
.card-tile { display: flex; flex-direction: column; align-items: flex-start; height: 100%; padding: 24px; border: 1px solid var(--gold-dim); border-radius: var(--radius); background: var(--bg-panel); text-decoration: none; }
.card-tile-symbol { font-size: 2rem; line-height: 1.3; }
.card-tile-number { color: var(--text-dim); font-size: .85rem; margin: 18px 0 4px; }
.card-tile strong { font-family: Georgia, serif; font-size: 1.4rem; font-weight: 500; }
.card-tile-desc { color: var(--text-dim); font-size: .9rem; margin-top: 6px; }
@media (max-width: 700px) { .card-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 480px) {
  .main-nav { padding: 12px 12px 0; }
  .main-nav a { padding: 8px 12px; font-size: .9rem; }
  .card-page { padding: 22px 16px 36px; }
  .card-section { padding: 22px 20px; }
  .card-tile { padding: 18px 14px; }
  .card-tile strong { font-size: 1.16rem; }
  .card-pagination { gap: 10px; }
  .card-pagination a { padding: 16px 12px; }
}
@media (max-width: 350px) { .card-grid { grid-template-columns: 1fr; } }
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } .stars2 { animation: none; } }
"""

NAV = """<nav class="main-nav" aria-label="Разделы">
  <div class="main-nav-inner">
    <a href="/">Главная</a>
    <a href="/cards/" class="mn-active">Карты</a>
    <a href="/astrology/">Астрология</a>
    <a href="/runes/">Руны</a>
    <a href="/spreads.html">Расклады</a>
  </div>
</nav>"""


def paragraphs(value: str) -> str:
    return "\n".join(f"<p>{escape(part.strip())}</p>"
                     for part in re.split(r"\n\s*\n", value) if part.strip())


def description_for(name: str, idea: str) -> str:
    """Полные фразы без обрезания слов; ограничение проверяется перед записью."""
    prefix = f"{name} — {idea}. "
    for ending in (
        "Значение карты Таро в прямом и перевёрнутом положении, в любви и карьере. Совет карты и вопросы для размышления.",
        "Прямое и перевёрнутое значение карты Таро, толкование в любви и карьере, совет и вопросы для размышления.",
        "Прямое и перевёрнутое положение, любовь и карьера. Толкование карты Таро, совет и вопросы для размышления.",
    ):
        result = prefix + ending
        if 140 <= len(result) <= 160:
            return result
    raise ValueError(f"Описание {name}: нужна фраза длиной 140–160 символов")


def document(title: str, description: str, url: str, body: str, article: bool) -> str:
    structured = {
        "@context": "https://schema.org",
        "@type": "Article" if article else "CollectionPage",
        "headline" if article else "name": title,
        "description": description,
        "url": url,
        "inLanguage": "ru",
    }
    # Не допускаем закрытия script данными, если исходный текст изменится.
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
<link rel="stylesheet" href="/css/style.css?v=3.1">
<link rel="stylesheet" href="/css/astrology.css?v=3.1">
<style>{STYLE}</style>
<script type="application/ld+json">
{schema}
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


def position_section(card: dict, position: str, heading: str) -> str:
    data = card[position]
    keywords = "".join(f"<li>{escape(word)}</li>" for word in data["keywords"])
    return f"""<section class="card-section" aria-labelledby="{position}">
<h2 id="{position}">{heading}</h2>
{paragraphs(data['short'])}
<ul class="card-keywords" aria-label="Ключевые слова">{keywords}</ul>
{paragraphs(data['archetype'])}
</section>"""


def topic_section(card: dict, field: str, heading: str) -> str:
    return f"""<section class="card-section" aria-labelledby="{field}">
<h2 id="{field}">{heading}</h2>
<h3>Прямое положение</h3>
{paragraphs(card['upright'][field])}
<h3>Перевёрнутое положение</h3>
{paragraphs(card['reversed'][field])}
</section>"""


def render_card(card: dict, cards: list[dict]) -> str:
    number = card["number"]
    slug, symbol, mini, idea, intro, advice, questions = EDITORIAL[number]
    name = card["name_ru"]
    title = f"{name} — значение и толкование | Таро Справочник"
    prev, nxt = (number - 1) % 22, (number + 1) % 22
    question_list = "\n".join(f"<li>{escape(q)}</li>" for q in questions)
    body = f"""<main class="card-page">
<nav class="card-crumbs" aria-label="Хлебные крошки"><a href="/">Главная</a> / <a href="/cards/">Карты</a> / <span aria-current="page">{escape(name)}</span></nav>
<article>
<header class="card-hero">
<span class="card-symbol" aria-hidden="true">{symbol}</span>
<p class="card-eyebrow">Старшие арканы</p>
<h1><span class="card-number">{ROMAN[number]}</span>{escape(name)}</h1>
<p>{escape(mini)}</p>
</header>
<section class="card-section card-intro" aria-labelledby="brief">
<h2 id="brief">Краткое значение</h2>
{paragraphs(intro)}
</section>
{position_section(card, 'upright', 'Прямое положение')}
{position_section(card, 'reversed', 'Перевёрнутое положение')}
{topic_section(card, 'love', 'В любви')}
{topic_section(card, 'career', 'В карьере')}
<section class="card-section" aria-labelledby="advice">
<h2 id="advice">Совет карты</h2>
{paragraphs(advice)}
</section>
<section class="card-section" aria-labelledby="questions">
<h2 id="questions">Вопросы для размышления</h2>
<ol class="card-questions">{question_list}</ol>
</section>
</article>
<nav class="card-pagination" aria-label="Предыдущая и следующая карта">
<a rel="prev" href="{EDITORIAL[prev][0]}.html"><span>← Предыдущая карта</span>{escape(cards[prev]['name_ru'])}</a>
<a rel="next" href="{EDITORIAL[nxt][0]}.html"><span>Следующая карта →</span>{escape(cards[nxt]['name_ru'])}</a>
</nav>
</main>"""
    return document(title, description_for(name, idea), f"{SITE}/cards/{slug}.html", body, True)


def render_index(cards: list[dict]) -> str:
    tiles = []
    for card, (slug, symbol, mini, *_rest) in zip(cards, EDITORIAL):
        tiles.append(f"""<li><a class="card-tile" href="{slug}.html">
<span class="card-tile-symbol" aria-hidden="true">{symbol}</span>
<span class="card-tile-number">{ROMAN[card['number']]}</span>
<strong>{escape(card['name_ru'])}</strong>
<span class="card-tile-desc">{escape(mini)}</span>
</a></li>""")
    body = """<main class="card-page card-catalog">
<nav class="card-crumbs" aria-label="Хлебные крошки"><a href="/">Главная</a> / <span aria-current="page">Карты</span></nav>
<header class="card-hero">
<span class="card-symbol" aria-hidden="true">✦</span>
<p class="card-eyebrow">От первого шага до целого мира</p>
<h1>22 старших аркана</h1>
<p>Выберите карту: её значения, совет и вопросы для размышления.</p>
</header>
<ol class="card-grid" aria-label="Старшие арканы от Дурака до Мира">
""" + "\n".join(tiles) + "\n</ol>\n</main>"
    description = ("22 старших аркана Таро: от Дурака до Мира. Значения карт в прямом и перевёрнутом положении, "
                   "в любви и карьере, советы и вопросы для размышления.")
    return document("Старшие арканы — значения 22 карт | Таро Справочник",
                    description, f"{SITE}/cards/", body, False)


class PageValidator(HTMLParser):
    """Строгая проверка вложенности нашего шаблона и JSON-LD без зависимостей."""

    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
            "meta", "param", "source", "track", "wbr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.ids: set[str] = set()
        self.labels: list[str] = []
        self.metadata: dict[str, str] = {}
        self.schema: list[dict] = []
        self.script: list[str] | None = None
        self.links: dict[str, str] = {}
        self.headings = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if len(a) != len(attrs):
            raise ValueError(f"Повтор атрибутов: {tag}")
        if tag not in self.VOID:
            self.stack.append(tag)
        if a.get("id"):
            if a["id"] in self.ids:
                raise ValueError(f"Повтор id: {a['id']}")
            self.ids.add(a["id"])
        self.labels.extend((a.get("aria-labelledby") or "").split())
        if tag == "h1":
            self.headings += 1
        if tag == "meta":
            self.metadata[a.get("name") or a.get("property") or ""] = a.get("content", "")
        if tag == "a" and a.get("rel") in {"prev", "next"}:
            self.links[a["rel"]] = a.get("href", "")
        if tag == "script":
            if a.get("type") != "application/ld+json":
                raise ValueError("Шаблон не должен подключать исполняемый JavaScript")
            self.script = []

    def handle_endtag(self, tag: str) -> None:
        if not self.stack or self.stack.pop() != tag:
            raise ValueError(f"Неверная вложенность перед </{tag}>")
        if tag == "script" and self.script is not None:
            self.schema.append(json.loads("".join(self.script)))
            self.script = None

    def handle_data(self, data: str) -> None:
        if self.script is not None:
            self.script.append(data)


def load_cards() -> list[dict]:
    cards = []
    for filename in ("major-0-10.json", "major-11-21.json"):
        cards.extend(json.loads((ROOT / "data" / filename).read_text(encoding="utf-8")))
    cards.sort(key=lambda c: c["number"])
    if [c["number"] for c in cards] != list(range(22)):
        raise ValueError("Ожидались ровно 22 карты с уникальными номерами от 0 до 21")
    for card in cards:
        if card.get("type") != "major" or not card.get("name_ru"):
            raise ValueError("Неверный тип или пустое название карты")
        for position in ("upright", "reversed"):
            for field in ("short", "archetype", "love", "career"):
                value = card[position][field]
                if not isinstance(value, str) or not value.strip():
                    raise ValueError(f"{card['id']}: пустое поле {position}.{field}")
            words = card[position]["keywords"]
            if not isinstance(words, list) or not words or not all(isinstance(w, str) and w.strip() for w in words):
                raise ValueError(f"{card['id']}: неверные ключевые слова")
    return cards


def validate_pages(pages: dict[str, str]) -> None:
    expected = {f"{row[0]}.html" for row in EDITORIAL} | {"index.html"}
    if set(pages) != expected or len(pages) != 23:
        raise ValueError("Неверный набор выходных страниц")
    for filename, html in pages.items():
        parser = PageValidator()
        parser.feed(html)
        parser.close()
        if parser.stack or parser.headings != 1 or len(parser.schema) != 1:
            raise ValueError(f"{filename}: незакрытые теги, неверный h1 или JSON-LD")
        if not set(parser.labels).issubset(parser.ids):
            raise ValueError(f"{filename}: aria-labelledby указывает на отсутствующий id")
        description = parser.metadata.get("description", "")
        if not 140 <= len(description) <= 160:
            raise ValueError(f"{filename}: description длиной {len(description)}")
        schema = parser.schema[0]
        if schema.get("description") != description or parser.metadata.get("og:description") != description:
            raise ValueError(f"{filename}: описания не совпадают")
        if filename != "index.html":
            number = next(i for i, row in enumerate(EDITORIAL) if filename == f"{row[0]}.html")
            if schema.get("@type") != "Article" or not schema.get("headline"):
                raise ValueError(f"{filename}: неверная схема Article")
            if parser.links != {"prev": f"{EDITORIAL[(number - 1) % 22][0]}.html",
                                "next": f"{EDITORIAL[(number + 1) % 22][0]}.html"}:
                raise ValueError(f"{filename}: неверная навигация по кругу")
        # Разрешены только слова о любовном романе и романтике.
        for word in re.findall(r"\b[А-Яа-яЁё]*роман[А-Яа-яЁё]*\b", html, re.IGNORECASE):
            if word.lower() not in {"роман", "романа", "романе", "романом", "роману", "романы", "романов"} and not word.lower().startswith("романти"):
                raise ValueError(f"{filename}: проверьте нежелательное имя {word}")
        if re.search(r"\bпан[а-яё]*\s+роман[а-яё]*\b", html, re.IGNORECASE):
            raise ValueError(f"{filename}: запрещённое упоминание имени")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    cards = load_cards()
    pages = {f"{EDITORIAL[card['number']][0]}.html": render_card(card, cards) for card in cards}
    pages["index.html"] = render_index(cards)
    validate_pages(pages)
    # Все данные и страницы проверены до первой записи. Не следуем ссылкам наружу.
    if OUTPUT.resolve() != OUTPUT:
        raise ValueError("Папка cards не должна перенаправлять запись в другое место")
    for filename in pages:
        target = OUTPUT / filename
        if target.is_symlink() or target.resolve().parent != OUTPUT:
            raise ValueError(f"Небезопасный выходной путь: {target}")
        if target.exists() and target.stat().st_nlink > 1:
            raise ValueError(f"Выходной файл имеет жёсткие ссылки: {target}")
    OUTPUT.mkdir(exist_ok=True)
    for filename, html in pages.items():
        with (OUTPUT / filename).open("w", encoding="utf-8", newline="\n") as output:
            output.write(html)
    print("OK: созданы 22 страницы карт и cards/index.html; HTML, метаданные и ссылки проверены.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
