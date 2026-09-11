// ═══════════════ Колесо Зодиака — данные (Школа Современного Таро) v1.7 ═══════════════
// Источник: лекция «Скрытая сила твоего характера в Таро» + research/zodiac/zodiac-wheel-notes.md
// Порядок арканов — ПО ШКОЛЕ СОВРЕМЕННОГО ТАРО (лекция). НЕ по Хану/Уэйту.

window.ZODIAC_WHEEL = [
  {
    slug: "oven", name: "Aries", sym: "♈", code: "‘I’",
    arcans: "The Magician (background — The High Priestess)", arcansNote: "The Magician, accumulated power",
    house: "First house",
    planets: "Mars · Pluto", planetsGlyph: "♂·♇",
    mainPlanet: "Mars", feedPlanet: "Pluto",
    cardFile: "major-01-magician.webp",
    opposite: "Libra", oppositeSlug: "vesy",
    month: "March–April", dates: "March 20/21 – April 20/21",
    work: "The beginning of the agricultural year. Lead the herds out, take possession of land, ‘set boundary markers’: this is mine, I will sow here.",
    text: "A sign of beginnings and force that breaks through obstacles. Aries needs to choose the direction independently and cannot bear being held back.",
    plus: "Determination, courage, initiative, the ability to start from nothing.",
    minus: "Impatience, a quick temper, beginning before understanding the consequences."
  },
  {
    slug: "telec", name: "Taurus", sym: "♉", code: "‘Mine’",
    arcans: "The Empress / The Emperor", arcansNote: "",
    house: "Second house",
    planets: "Venus · Chiron", planetsGlyph: "♀·⚷",
    mainPlanet: "Venus", feedPlanet: "Chiron",
    cardFile: "major-03-empress.webp", cardFile2: "major-04-emperor.webp",
    opposite: "Scorpio", oppositeSlug: "skorpion",
    month: "April–May", dates: "April 20/21 – May 20/21",
    work: "Nature comes into bloom. ‘The Emperor marks boundaries’ — he pulls the plow and cuts the earth into straight lines.",
    text: "Practicality and stability. Taurus creates a reliable, enduring world and dislikes abrupt change.",
    plus: "Patience, reliability, practicality, the ability to preserve what has been accumulated.",
    minus: "Inertia, stubbornness, holding on to the familiar for too long."
  },
  {
    slug: "bliznecy", name: "Gemini", sym: "♊", code: "‘Those close to me’",
    arcans: "The Hierophant / The Lovers", arcansNote: "",
    house: "Third house",
    planets: "Mercury · Proserpina", planetsGlyph: "☿",
    mainPlanet: "Mercury", feedPlanet: "Proserpina",
    cardFile: "major-05-hierophant.webp", cardFile2: "major-06-lovers.webp",
    opposite: "Sagittarius", oppositeSlug: "strelec",
    month: "June–July", dates: "May 20/21 – June 21/22",
    work: "Seeking a mate; ‘birds build nests.’ The principle of choosing the right from the wrong (weeding).",
    text: "They learn about the world through contact and information. They learn quickly and switch easily.",
    plus: "Curiosity, flexibility, sociability, connecting people and ideas.",
    minus: "Scattered attention, poor concentration, too many things at once."
  },
  {
    slug: "rak", name: "Cancer", sym: "♋", code: "‘Emotions within’",
    arcans: "The Chariot (VII)", arcansNote: "",
    house: "Fourth house",
    planets: "Moon", planetsGlyph: "☽",
    mainPlanet: "Moon", feedPlanet: "—",
    cardFile: "major-07-chariot.webp",
    opposite: "Capricorn", oppositeSlug: "kozerog",
    month: "July", dates: "June 21/22 – July 22/23",
    work: "Cut the grass, hide it in stacks, and take it by cart beneath the protection of structures — hay for winter.",
    text: "Experiences the world emotionally. Needs protection, personal space, and a sense of home.",
    plus: "Empathy, care, memory, intuition, emotional depth.",
    minus: "Touchiness, anxiety, dependence on mood."
  },
  {
    slug: "lev", name: "Leo", sym: "♌", code: "‘What I want to do’",
    arcans: "Strength (VIII)", arcansNote: "",
    house: "Fifth house",
    planets: "Sun", planetsGlyph: "☉",
    mainPlanet: "Sun", feedPlanet: "—",
    cardFile: "major-08-strength.webp",
    opposite: "Aquarius", oppositeSlug: "vodoley",
    month: "August", dates: "July 22/23 – August 23/24",
    work: "Harvest time, ‘the most important time of the year.’ One must master oneself — the desire to be idle is strong, but work cannot stop.",
    text: "Putting oneself into a task and feeling that one’s presence matters. Vivid self-expression and recognition.",
    plus: "Creativity, confidence, generosity, leadership, the ability to inspire.",
    minus: "Pride, a painful response to being disregarded, a need for praise."
  },
  {
    slug: "deva", name: "Virgo", sym: "♍", code: "‘Make everything clear’",
    arcans: "The Hermit (IX)", arcansNote: "",
    house: "Sixth house",
    planets: "Mercury · Proserpina", planetsGlyph: "☿",
    mainPlanet: "Mercury", feedPlanet: "Proserpina",
    cardFile: "major-09-hermit.webp", cardFile2: "major-10-wheel-of-fortune.webp",
    opposite: "Pisces", oppositeSlug: "ryby",
    month: "September", dates: "August 23/24 – September 23/24",
    work: "Working alone as the day grows shorter. Separate grain from chaff, sort it, spin yarn.",
    text: "Notices details, analyzes, corrects, and improves. Sees what can be adjusted more precisely.",
    plus: "Analytical ability, accuracy, practicality, breaking a task into parts.",
    minus: "Perfectionism, criticism, anxiety over details."
  },
  {
    slug: "vesy", name: "Libra", sym: "♎", code: "‘Not me’",
    arcans: "Justice / The Hanged Man", arcansNote: "",
    house: "Seventh house",
    planets: "Venus · Chiron", planetsGlyph: "♀·⚷",
    mainPlanet: "Venus", feedPlanet: "Chiron",
    cardFile: "major-11-justice.webp", cardFile2: "major-12-hanged-man.webp",
    opposite: "Aries", oppositeSlug: "oven",
    month: "Late September–October", dates: "September 23/24 – October 23/24",
    work: "Fairs and scales; negotiating with merchants; taxes and tithes — ‘an offering to authority.’",
    text: "Naturally sees the opposing point of view. Partnership, fairness, and harmony matter.",
    plus: "Diplomacy, negotiating ability, a sense of proportion, seeing several points of view.",
    minus: "Indecision, weighing options for too long."
  },
  {
    slug: "skorpion", name: "Scorpio", sym: "♏", code: "‘What belongs to another’",
    arcans: "Death (XIII)", arcansNote: "",
    house: "Eighth house",
    planets: "Pluto · Mars", planetsGlyph: "♇·♂",
    mainPlanet: "Pluto", feedPlanet: "Mars",
    cardFile: "major-13-death.webp",
    opposite: "Taurus", oppositeSlug: "telec",
    month: "October–November", dates: "October 23/24 – November 22/23",
    work: "Sowing winter crops, the ‘burial of the grain.’ We hide what cannot be eaten and give it to God/Pluto.",
    text: "An intense inner life. Drawn to hidden causes, crises, power, and transformation.",
    plus: "Insight, resilience, depth of feeling, the ability to rebuild after crisis.",
    minus: "Suspicion, jealousy, possessiveness, a drive to control."
  },
  {
    slug: "strelec", name: "Sagittarius", sym: "♐", code: "‘Beyond the familiar’",
    arcans: "The Devil (XV)", arcansNote: "",
    house: "Ninth house",
    planets: "Jupiter · Neptune", planetsGlyph: "♃·♆",
    mainPlanet: "Jupiter", feedPlanet: "Neptune",
    cardFile: "major-15-devil.webp",
    opposite: "Gemini", oppositeSlug: "bliznecy",
    month: "November–December", dates: "November 22/23 – December 21/22",
    work: "The last attempt to gather acorns using pigs, forest grazing. Weddings and celebrations marking the end of the year.",
    text: "Seeks to move beyond the known. Drawn to new knowledge, philosophy, and broad prospects.",
    plus: "Optimism, broad thinking, curiosity, inspiration through an idea.",
    minus: "Scattered effort, overestimating one’s strength, promising more than one can deliver."
  },
  {
    slug: "kozerog", name: "Capricorn", sym: "♑", code: "‘Outside’",
    arcans: "The Tower (XVI)", arcansNote: "",
    house: "Tenth house",
    planets: "Saturn · Uranus", planetsGlyph: "♄·♅",
    mainPlanet: "Saturn", feedPlanet: "Uranus",
    cardFile: "major-16-tower.webp",
    opposite: "Cancer", oppositeSlug: "rak",
    month: "December–January", dates: "December 21/22 – January 20/21",
    work: "The ‘turning of the year,’ Christmas/Saturnalia — the hourglass turns over. Survival on stored supplies.",
    text: "Thinks in terms of results, structure, time, and responsibility. Sets long-term goals.",
    plus: "Responsibility, patience, discipline, strategy, endurance under pressure.",
    minus: "Excessive seriousness, pessimism, rigidity, postponing life until ‘later.’"
  },
  {
    slug: "vodoley", name: "Aquarius", sym: "♒", code: "‘Does what must be done’",
    arcans: "The Star (XVII)", arcansNote: "",
    house: "Eleventh house",
    planets: "Uranus · Saturn", planetsGlyph: "♅·♄",
    mainPlanet: "Uranus", feedPlanet: "Saturn",
    cardFile: "major-17-star.webp",
    opposite: "Leo", oppositeSlug: "lev",
    month: "February", dates: "January 20/21 – February 20/21",
    work: "Wash barrels, channel meltwater, carry out active communal work. Protect livestock from wolves.",
    text: "Views familiar rules from the outside. Drawn to new ideas, technology, and freedom of thought.",
    plus: "Independence, originality, inventiveness, seeing new options.",
    minus: "Detachment, stubbornness, rebellion for its own sake, difficulty with commitments."
  },
  {
    slug: "ryby", name: "Pisces", sym: "♓", code: "‘The unknown’",
    arcans: "The Sun and Judgement (XIX/XX)", arcansNote: "",
    house: "Twelfth house",
    planets: "Neptune · Jupiter", planetsGlyph: "♆·♃",
    mainPlanet: "Neptune", feedPlanet: "Jupiter",
    cardFile: "major-19-sun.webp", cardFile2: "major-20-judgement.webp",
    opposite: "Virgo", oppositeSlug: "deva",
    month: "February", dates: "February 20/21 – March 20/21",
    work: "The hardest time of year — supplies have run out. ‘One fish moves forward, the other back; one is black, the other white.’",
    text: "Receptive to the atmosphere and other people’s moods. A rich imagination and strong intuition.",
    plus: "Empathy, imagination, intuition, creativity, compassion.",
    minus: "Blurred boundaries, indecision, withdrawal from reality, self-sacrifice."
  }
];

// Арканы вне колеса (Шут и Мир)
window.ZODIAC_WHEEL_OUT = [
  { name: "The Fool", sym: "0", text: "Alpha and omega, ‘divine folly.’ The entry point into the wheel and the beginning of the journey." },
  { name: "The World", sym: "21", text: "A ‘reset,’ completion of the cycle. The exit from the wheel and readiness for a new beginning." }
];