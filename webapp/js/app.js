/* ─── Логика справочника Таро ─── */
'use strict';

const SUITS_RU = {
  wands: 'Жезлы', cups: 'Кубки', swords: 'Мечи', pentacles: 'Пентакли'
};
const SUIT_ELEMENT = {
  wands: 'Огонь', cups: 'Вода', swords: 'Воздух', pentacles: 'Земля'
};
const RANK_NUM = {
  ace: 1, two: 2, three: 3, four: 4, five: 5,
  six: 6, seven: 7, eight: 8, nine: 9, ten: 10
};
const COURT_ORDER = { page: 11, knight: 12, queen: 13, king: 14 };

const SECTION_META = [
  ['archetype', 'Архетип и основное значение', '✧'],
  ['daily',     'В быту',                     '🏠'],
  ['career',    'Работа и карьера',           '💼'],
  ['love',      'Отношения',                  '❤'],
  ['health',    'Здоровье',                   '🌿'],
  ['esoteric',  'Эзотерическое значение',     '🔮'],
];

const deck = document.getElementById('deck');
const tabsEl = document.getElementById('tabs');
const searchEl = document.getElementById('search');
const emptyMsg = document.getElementById('emptyMsg');
const modal = document.getElementById('modal');
const modalClose = document.getElementById('modalClose');
const mImg = document.getElementById('mImg');
const posTabs = document.getElementById('posTabs');

let currentSuit = 'major';
let currentQuery = '';
let currentCard = null;
let currentPos = 'upright';

const GOLDEN_DAWN_RANKS = new Set([
  'ace', 'two', 'three', 'four', 'five',
  'six', 'seven', 'eight', 'nine', 'ten'
]);

function isGoldenDawnCard(card) {
  if (!card || card.type === 'major' || !card.suit) return false;
  return GOLDEN_DAWN_RANKS.has(card.id.split('-')[1]);
}

function validGoldenDawn(data) {
  return data
    && typeof data.title_en === 'string' && data.title_en.trim()
    && typeof data.title_ru === 'string' && data.title_ru.trim()
    && typeof data.why === 'string' && data.why.trim();
}

/* ─── Порядок карт внутри масти ─── */
function sortKey(c) {
  if (c.type === 'major') return c.number;
  const slug = c.id.split('-')[1];
  return RANK_NUM[slug] || COURT_ORDER[slug];
}

function cardsForSuit(suit) {
  return TARO_CARDS.filter(c => suit === 'major' ? c.type === 'major' : c.suit === suit)
    .sort((a, b) => sortKey(a) - sortKey(b));
}

/* ─── Рендер сетки ─── */
function renderDeck() {
  const q = currentQuery.trim().toLowerCase();
  let cards = cardsForSuit(currentSuit);

  if (q) {
    // Поиск идёт по всем 78 картам, независимо от вкладки
    cards = TARO_CARDS.filter(c => {
      const hay = [c.name_ru, c.name_en, c.suit && SUITS_RU[c.suit]]
        .concat(Object.values(c.upright.keywords), Object.values(c.reversed.keywords))
        .join(' ').toLowerCase();
      return hay.includes(q);
    });
  }

  emptyMsg.hidden = cards.length > 0;
  deck.innerHTML = '';

  cards.forEach((c, i) => {
    const numSlug = c.id.split('-')[1];
    const tile = document.createElement('button');
    tile.className = 'card-tile';
    tile.style.animationDelay = `${Math.min(i * 0.03, .5)}s`;
    tile.setAttribute('aria-label', c.name_ru);

    let numBadge = '';
    if (c.type === 'major') numBadge = `<span class="tile-num">${c.number}</span>`;
    else if (RANK_NUM[numSlug]) {
      // Для числовых масти показываем номинал римскими не надо — оставим пусто/точку
      numBadge = '';
    } else {
      const icons = { page: '🂡', knight: '🂢', queen: '🂣', king: '🂤' };
      numBadge = `<span class="tile-num" title="Придворная карта">${icons[numSlug] || ''}</span>`;
    }

    tile.innerHTML = `
      <img src="img/cards/${c.img}" alt="${c.name_ru}" loading="lazy" draggable="false">
      ${numBadge}
      <span class="tile-name">${c.name_ru}</span>`;
    tile.addEventListener('click', () => openCard(c));
    deck.appendChild(tile);
  });
}

/* ─── Модалка ─── */
function openCard(card) {
  currentCard = card;
  currentPos = 'upright';

  mImg.src = `img/cards/${card.img}`;
  mImg.alt = `${card.name_ru} — прямое положение`;
  mImg.classList.remove('reversed');
  document.getElementById('mArcana').textContent =
    card.type === 'major'
      ? `Старший аркан · ${card.number}`
      : `Младший аркан · ${SUITS_RU[card.suit]}`;

  document.getElementById('mTitle').textContent = card.name_ru;
  document.getElementById('mEn').textContent = card.name_en;

  const metaParts = [];
  if (card.element) metaParts.push(`Стихия: <b>${card.element}</b>`);
  else if (card.suit) metaParts.push(`Стихия: <b>${SUIT_ELEMENT[card.suit]}</b>`);
  if (card.astro) metaParts.push(`Астрология: <b>${card.astro}</b>`);
  document.getElementById('mMeta').innerHTML = metaParts.join(' &nbsp;·&nbsp; ');

  posTabs.querySelectorAll('.pos-tab').forEach(t =>
    t.classList.toggle('active', t.dataset.pos === 'upright'));

  renderPosition();
  modal.classList.add('open');
  modal.scrollTop = 0;
  modal.setAttribute('aria-hidden', 'false');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  modal.classList.remove('open');
  modal.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = '';
}

function renderPosition() {
  if (currentPos !== 'upright' && currentPos !== 'reversed') currentPos = 'upright';
  const p = currentCard[currentPos];
  if (!p) { currentPos = 'upright'; return renderPosition(); }
  const label = currentPos === 'upright' ? 'прямое положение' : 'перевёрнутое положение';

  const html = [];
  html.push(`<div class="pos-content">`);
  html.push(`<div class="kw-row">${p.keywords.map(k => `<span class="kw">${k}</span>`).join('')}</div>`);
  html.push(`<p class="short-value">${p.short}</p>`);
  const expectsGoldenDawn = isGoldenDawnCard(currentCard);
  if (expectsGoldenDawn && validGoldenDawn(p.gd)) {
    html.push(`<aside class="gd-block" data-card-id="${currentCard.id}" data-position="${currentPos}" aria-label="Значение карты по ордену Золотая Заря">`
      + `<div class="gd-head"><span class="gd-symbol" aria-hidden="true">☉</span> По ордену «Золотая Заря»</div>`
      + `<p class="gd-title">«${p.gd.title_en}» — ${p.gd.title_ru}</p>`
      + `<p class="gd-why">${p.gd.why}</p></aside>`);
  } else if (expectsGoldenDawn) {
    // Не скрываем секцию при рассинхронизации публикации: ошибка становится видимой.
    html.push(`<aside class="gd-block gd-missing" data-card-id="${currentCard.id}" data-position="${currentPos}">`
      + `<div class="gd-head">По ордену «Золотая Заря»</div>`
      + `<p class="gd-why">Данные этой карты не загрузились. Обновите страницу без кеша.</p></aside>`);
    console.error(`Golden Dawn data is missing for ${currentCard.id}.${currentPos}`);
  }
  for (const [key, title, icon] of SECTION_META) {
    html.push(`<div class="info-section"><h3><span>${icon}</span> ${title}</h3><p>${p[key]}</p></div>`);
  }
  html.push(`</div>`);

  document.getElementById('mContent').innerHTML = html.join('');
  renderPosition.label = label;
}

function para(text) {
  const t = text.trim();
  if (t.includes('\n\n')) return '<p>' + t.split(/\n{2,}/).map(s => s.replace(/\n/g, '<br>')).join('</p><p>') + '</p>';
  return '<p>' + t.replace(/\n/g, '<br>') + '</p>';
}

/* ─── Вкладка «Школа Пана Романа» (только старшие арканы) ─── */
const ROMAN_SECTIONS_FULL = [
  ['Суть карты',              '✧'],
  ['Прямое положение',        '☀'],
  ['Негативное значение',     '☾'],
  ['Акценты и фишки школы',   '★'],
  ['Ключевые слова',          '🗝'],
];

function romanDataFor(card) {
  if (typeof ROMAN_SCHOOL === 'undefined' || !Array.isArray(ROMAN_SCHOOL)) return null;
  return ROMAN_SCHOOL.find(r => r.id === card.id) || null;
}

function renderRoman(card) {
  const data = romanDataFor(card);
  const html = ['<div class="pos-content roman-content">'];

  if (!data) {
    html.push(`<div class="roman-empty">
      <p class="short-value">Для этой карты материалы школы Пана Романа пока не готовы.</p>
    </div>`);
    html.push('</div>');
    document.getElementById('mContent').innerHTML = html.join('');
    return;
  }

  /* Простая часть */
  const isMinor = !card.id.startsWith('major');
  html.push(`<h3 class="roman-subtitle"><span>🌿</span> ${isMinor ? 'Как школа читает этот ранг' : 'Кратко и просто'}</h3>`);
  for (const b of data.simple) {
    html.push(`<div class="info-section"><h3>${b.t}</h3>${para(b.x)}</div>`);
  }

  /* Астрология школы (Юрий Хан) — отличается от классики Уэйта */
  if (data.astro) {
    html.push(`<div class="roman-astro">
      <span class="ra-label">✷ Астрология школы</span>
      <b>${data.astro.pos}</b><span class="ra-sep">·</span>${data.astro.planets}
      ${data.astro.classic ? `<div class="ra-classic">У классики Уэйта: ${data.astro.classic}</div>` : ''}
    </div>`);
  }

  /* Развёрнутая версия — аккордеон, «Суть карты» открыта по умолчанию */
  html.push(`<h3 class="roman-subtitle"><span>📜</span> ${isMinor ? 'Развёрнуто — из лекции по рангу' : 'Развёрнуто — выжимки лекций'}</h3>`);
  for (const [sec, icon] of ROMAN_SECTIONS_FULL) {
    const text = data.full[sec];
    if (!text) continue;
    html.push(`<details class="roman-details"${sec === 'Суть карты' ? ' open' : ''}>
      <summary><span class="rd-icon">${icon}</span> ${sec}</summary>
      <div class="rd-body">${para(text)}</div>
    </details>`);
  }

  html.push('</div>');
  document.getElementById('mContent').innerHTML = html.join('');
}

/* ─── События ─── */
tabsEl.addEventListener('click', e => {
  const tab = e.target.closest('.tab');
  if (!tab) return;
  tabsEl.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t === tab));
  currentSuit = tab.dataset.suit;
  if (currentQuery) { searchEl.value = ''; currentQuery = ''; }
  renderDeck();
});

searchEl.addEventListener('input', () => {
  currentQuery = searchEl.value;
  renderDeck();
});

modalClose.addEventListener('click', closeModal);
modal.addEventListener('click', e => { if (e.target === modal) closeModal(); });
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeModal();
});

posTabs.addEventListener('click', e => {
  const tab = e.target.closest('.pos-tab');
  if (!tab) return;
  posTabs.querySelectorAll('.pos-tab').forEach(t => t.classList.toggle('active', t === tab));
  currentPos = tab.dataset.pos;

  if (currentPos === 'roman') {
    // Вкладка школы — карту не крутим, показываем материалы школы
    mImg.classList.remove('reversed');
    if (currentCard) mImg.alt = `${currentCard.name_ru} — школа Пана Романа`;
    renderRoman(currentCard);
    return;
  }

  if (currentPos !== 'upright' && currentPos !== 'reversed') currentPos = 'upright';

  // Перевёрнутое положение — поворачиваем саму карту
  mImg.classList.toggle('reversed', currentPos === 'reversed');
  mImg.alt = `${currentCard.name_ru} — ${currentPos === 'reversed' ? 'перевёрнутое' : 'прямое'} положение`;
  renderPosition();
});

/* ─── Старт ─── */
renderDeck();
