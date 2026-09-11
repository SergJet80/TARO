/* ─── Логика справочника Tarot ─── */
'use strict';

const SUITS_RU = {
  wands: 'Wands', cups: 'Cups', swords: 'Swords', pentacles: 'Pentacles'
};
const SUIT_ELEMENT = {
  wands: 'Fire', cups: 'Water', swords: 'Air', pentacles: 'Earth'
};
const RANK_NUM = {
  ace: 1, two: 2, three: 3, four: 4, five: 5,
  six: 6, seven: 7, eight: 8, nine: 9, ten: 10
};
const COURT_ORDER = { page: 11, knight: 12, queen: 13, king: 14 };

const CARD_PAGE_SLUGS = {major00:'durak',major01:'mag',major02:'zhrefca',major03:'imperatrica',major04:'imperator',major05:'ierofant',major06:'vlyublyonnye',major07:'kolesnica',major08:'sila',major09:'otshelnik',major10:'koleso-fortuny',major11:'spravedlivost',major12:'poveshennyj',major13:'smert',major14:'umerennost',major15:'dyavol',major16:'bashnya',major17:'zvezda',major18:'luna',major19:'solnce',major20:'sud',major21:'mir',wandsace:'wands-ace',wandstwo:'wands-two',wandsthree:'wands-three',wandsfour:'wands-four',wandsfive:'wands-five',wandssix:'wands-six',wandsseven:'wands-seven',wandseight:'wands-eight',wandsnine:'wands-nine',wandsten:'wands-ten',wandspage:'wands-page',wandsknight:'wands-knight',wandsqueen:'wands-queen',wandsking:'wands-king',cupsace:'cups-ace',cupstwo:'cups-two',cupsthree:'cups-three',cupsfour:'cups-four',cupsfive:'cups-five',cupssix:'cups-six',cupsseven:'cups-seven',cupseight:'cups-eight',cupsnine:'cups-nine',cupsten:'cups-ten',cupspage:'cups-page',cupsknight:'cups-knight',cupsqueen:'cups-queen',cupsking:'cups-king',swordsace:'swords-ace',swordstwo:'swords-two',swordsthree:'swords-three',swordsfour:'swords-four',swordsfive:'swords-five',swordssix:'swords-six',swordsseven:'swords-seven',swordseight:'swords-eight',swordsnine:'swords-nine',swordsten:'swords-ten',swordspage:'swords-page',swordsknight:'swords-knight',swordsqueen:'swords-queen',swordsking:'swords-king',pentaclesace:'pentacles-ace',pentaclestwo:'pentacles-two',pentaclesthree:'pentacles-three',pentaclesfour:'pentacles-four',pentaclesfive:'pentacles-five',pentaclessix:'pentacles-six',pentaclesseven:'pentacles-seven',pentacleseight:'pentacles-eight',pentaclesnine:'pentacles-nine',pentaclesten:'pentacles-ten',pentaclespage:'pentacles-page',pentaclesknight:'pentacles-knight',pentaclesqueen:'pentacles-queen',pentaclesking:'pentacles-king'};

const SECTION_META = [
  ['archetype', 'Archetype and core meaning', '✧'],
  ['daily',     'Daily life',                     '🏠'],
  ['career',    'Work and career',           '💼'],
  ['love',      'Relationships',                  '❤'],
  ['health',    'Health',                   '🌿'],
  ['esoteric',  'Spiritual meaning',     '🔮'],
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
let lastFocusedCard = null;

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
      numBadge = `<span class="tile-num" title="Court card">${icons[numSlug] || ''}</span>`;
    }

    tile.innerHTML = `
      <img src="../../img/cards/${c.img}" alt="${c.name_ru}" loading="lazy" draggable="false">
      ${numBadge}
      <span class="tile-name">${c.name_ru}</span>`;
    tile.addEventListener('click', () => openCard(c, tile));
    deck.appendChild(tile);
  });
}

/* ─── Модалка ─── */
function openCard(card, trigger) {
  lastFocusedCard = trigger || document.activeElement;
  currentCard = card;
  currentPos = 'upright';

  mImg.src = `../../img/cards/${card.img}`;
  mImg.alt = `${card.name_ru} — upright position`;
  mImg.classList.remove('reversed');
  document.getElementById('mArcana').textContent =
    card.type === 'major'
      ? `Major Arcana · ${card.number}`
      : `Minor Arcana · ${SUITS_RU[card.suit]}`;

  document.getElementById('mTitle').textContent = card.name_ru;
  document.getElementById('mEn').textContent = card.name_en;

  const metaParts = [];
  if (card.element) metaParts.push(`Element: <b>${card.element}</b>`);
  else if (card.suit) metaParts.push(`Element: <b>${SUIT_ELEMENT[card.suit]}</b>`);
  if (card.astro) metaParts.push(`Astrology: <b>${card.astro}</b>`);
  document.getElementById('mMeta').innerHTML = metaParts.join(' &nbsp;·&nbsp; ');

  posTabs.querySelectorAll('.pos-tab').forEach(t =>
    t.classList.toggle('active', t.dataset.pos === 'upright'));

  renderPosition();
  modal.classList.add('open');
  modal.scrollTop = 0;
  modal.setAttribute('aria-hidden', 'false');
  document.body.style.overflow = 'hidden';
  modalClose.focus();
}

function closeModal() {
  if (!modal.classList.contains('open')) return;
  modal.classList.remove('open');
  modal.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = '';
  if (lastFocusedCard && document.contains(lastFocusedCard)) lastFocusedCard.focus();
  lastFocusedCard = null;
}

function renderPosition() {
  if (currentPos !== 'upright' && currentPos !== 'reversed') currentPos = 'upright';
  const p = currentCard[currentPos];
  if (!p) { currentPos = 'upright'; return renderPosition(); }
  const label = currentPos === 'upright' ? 'upright position' : 'reversed position';

  const html = [];
  html.push(`<div class="pos-content">`);
  html.push(`<div class="kw-row">${p.keywords.map(k => `<span class="kw">${k}</span>`).join('')}</div>`);
  html.push(`<p class="short-value">${p.short}</p>`);
  const expectsGoldenDawn = isGoldenDawnCard(currentCard);
  if (expectsGoldenDawn && validGoldenDawn(p.gd)) {
    html.push(`<aside class="gd-block" data-card-id="${currentCard.id}" data-position="${currentPos}" aria-label="Card meaning in the Golden Dawn tradition">`
      + `<div class="gd-head"><span class="gd-symbol" aria-hidden="true">☉</span> Golden Dawn tradition</div>`
      + `<p class="gd-title">«${p.gd.title_en}» — ${p.gd.title_ru}</p>`
      + `<p class="gd-why">${p.gd.why}</p></aside>`);
  } else if (expectsGoldenDawn) {
    // Не скрываем секцию при рассинхронизации публикации: ошибка становится видимой.
    html.push(`<aside class="gd-block gd-missing" data-card-id="${currentCard.id}" data-position="${currentPos}">`
      + `<div class="gd-head">Golden Dawn tradition</div>`
      + `<p class="gd-why">This card's data did not load. Refresh the page without cache.</p></aside>`);
    console.error(`Golden Dawn data is missing for ${currentCard.id}.${currentPos}`);
  }
  for (const [key, title, icon] of SECTION_META) {
    html.push(`<div class="info-section"><h3><span>${icon}</span> ${title}</h3><p>${p[key]}</p></div>`);
  }
  html.push(`<div class="card-page-link"><a href="/en/cards/${CARD_PAGE_SLUGS[currentCard.id.replace('-', '')]}.html" target="_blank" rel="noopener">${"Full page for “"}${currentCard.name_ru}${"” →"}</a></div>`);
  html.push(`</div>`);

  document.getElementById('mContent').innerHTML = html.join('');
  renderPosition.label = label;
}

function para(text) {
  const t = text.trim();
  if (t.includes('\n\n')) return '<p>' + t.split(/\n{2,}/).map(s => s.replace(/\n/g, '<br>')).join('</p><p>') + '</p>';
  return '<p>' + t.replace(/\n/g, '<br>') + '</p>';
}

/* ─── Вкладка «School of Modern Tarot» (только старшие арканы) ─── */
const ROMAN_SECTIONS_FULL = [
  ['Essence of the card',              '✧'],
  ['Upright position',        '☀'],
  ['Negative meaning',     '☾'],
  ['School emphases and distinctive points',   '★'],
  ['Keywords',          '🗝'],
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
      <p class="short-value">School of Modern Tarot material is not yet available for this card.</p>
    </div>`);
    html.push('</div>');
    document.getElementById('mContent').innerHTML = html.join('');
    return;
  }

  /* Простая часть */
  const isMinor = !card.id.startsWith('major');
  html.push(`<h3 class="roman-subtitle"><span>🌿</span> ${isMinor ? 'How the school reads this rank' : 'In brief'}</h3>`);
  for (const b of data.simple) {
    html.push(`<div class="info-section"><h3>${b.t}</h3>${para(b.x)}</div>`);
  }

  /* School astrology (Юрий Хан) — отличается от классики Уэйта */
  if (data.astro) {
    html.push(`<div class="roman-astro">
      <span class="ra-label">✷ School astrology</span>
      <b>${data.astro.pos}</b><span class="ra-sep">·</span>${data.astro.planets}
      ${data.astro.classic ? `<div class="ra-classic">In the Waite tradition: ${data.astro.classic}</div>` : ''}
    </div>`);
  }

  /* Развёрнутая версия — аккордеон, «Essence of the card» открыта по умолчанию */
  html.push(`<h3 class="roman-subtitle"><span>📜</span> ${isMinor ? 'In detail — from the rank lecture' : 'In detail — lecture extracts'}</h3>`);
  for (const [sec, icon] of ROMAN_SECTIONS_FULL) {
    const text = data.full[sec];
    if (!text) continue;
    html.push(`<details class="roman-details"${sec === 'Essence of the card' ? ' open' : ''}>
      <summary><span class="rd-icon">${icon}</span> ${sec}</summary>
      <div class="rd-body">${para(text)}</div>
    </details>`);
  }

/* ─── Ссылка на статическую страницу карты (SEO) ─── */
const CARD_PAGE_SLUGS = {major00:'durak',major01:'mag',major02:'zhrefca',major03:'imperatrica',major04:'imperator',major05:'ierofant',major06:'vlyublyonnye',major07:'kolesnica',major08:'sila',major09:'otshelnik',major10:'koleso-fortuny',major11:'spravedlivost',major12:'poveshennyj',major13:'smert',major14:'umerennost',major15:'dyavol',major16:'bashnya',major17:'zvezda',major18:'luna',major19:'solnce',major20:'sud',major21:'mir',wandsace:'wands-ace',wandstwo:'wands-two',wandsthree:'wands-three',wandsfour:'wands-four',wandsfive:'wands-five',wandssix:'wands-six',wandsseven:'wands-seven',wandseight:'wands-eight',wandsnine:'wands-nine',wandsten:'wands-ten',wandspage:'wands-page',wandsknight:'wands-knight',wandsqueen:'wands-queen',wandsking:'wands-king',cupsace:'cups-ace',cupstwo:'cups-two',cupsthree:'cups-three',cupsfour:'cups-four',cupsfive:'cups-five',cupssix:'cups-six',cupsseven:'cups-seven',cupseight:'cups-eight',cupsnine:'cups-nine',cupsten:'cups-ten',cupspage:'cups-page',cupsknight:'cups-knight',cupsqueen:'cups-queen',cupsking:'cups-king',swordsace:'swords-ace',swordstwo:'swords-two',swordsthree:'swords-three',swordsfour:'swords-four',swordsfive:'swords-five',swordssix:'swords-six',swordsseven:'swords-seven',swordseight:'swords-eight',swordsnine:'swords-nine',swordsten:'swords-ten',swordspage:'swords-page',swordsknight:'swords-knight',swordsqueen:'swords-queen',swordsking:'swords-king',pentaclesace:'pentacles-ace',pentaclestwo:'pentacles-two',pentaclesthree:'pentacles-three',pentaclesfour:'pentacles-four',pentaclesfive:'pentacles-five',pentaclessix:'pentacles-six',pentaclesseven:'pentacles-seven',pentacleseight:'pentacles-eight',pentaclesnine:'pentacles-nine',pentaclesten:'pentacles-ten',pentaclespage:'pentacles-page',pentaclesknight:'pentacles-knight',pentaclesqueen:'pentacles-queen',pentaclesking:'pentacles-king'};
const cardPage = CARD_PAGE_SLUGS[currentCard.id.replace('-','')];
if (cardPage) {
  html.push(`<div class="card-page-link"><a href="/en/cards/${cardPage}.html" target="_blank" rel="noopener">Full page for “${currentCard.name_ru}” →</a></div>`);
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
    if (currentCard) mImg.alt = `${currentCard.name_ru} — School of Modern Tarot`;
    renderRoman(currentCard);
    return;
  }

  if (currentPos !== 'upright' && currentPos !== 'reversed') currentPos = 'upright';

  // Reversed position — поворачиваем саму карту
  mImg.classList.toggle('reversed', currentPos === 'reversed');
  mImg.alt = `${currentCard.name_ru} — ${currentPos === 'reversed' ? 'reversed' : 'upright'} position`;
  renderPosition();
});

/* ─── Старт ─── */
renderDeck();
