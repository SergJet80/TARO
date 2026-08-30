// ═══════════════ Колесо Зодиака — логика (v1.9) ═══════════════
// Структура по описанию: внешний обод — месяцы (сдвинуты на половину сектора, по одному),
// числа куспидов в углах секторов, символ знака + глифы планет в секторе,
// в центре — карта(ы) старшего аркана. Кодовые слова и надписи — только в панели снизу.

(function () {
  "use strict";
  if (typeof window.ZODIAC_WHEEL === "undefined") return;

  var SIGNS = window.ZODIAC_WHEEL;
  var TOTAL = SIGNS.length;
  var SEG = (2 * Math.PI) / TOTAL;
  var activeIndex = 0;
  var dataIdx = {};

  var NS = "http://www.w3.org/2000/svg";
  var VB = 620, CX = VB / 2, CY = VB / 2;
  var R_OUT = 296;
  var R_CARD = 132;
  var CARDPATH = "../img/cards/";

  // Названия месяцев по порядку (старт: март у Овна)
  var MONTHS = ["Март","Апрель","Май","Июнь","Июль","Август",
                "Сентябрь","Октябрь","Ноябрь","Декабрь","Январь","Февраль"];

  function polar(r, ang) { return [CX + r * Math.cos(ang), CY + r * Math.sin(ang)]; }

  function arcPath(r, a0, a1) {
    var p0 = polar(r, a0), p1 = polar(r, a1);
    var large = (a1 - a0) > Math.PI ? 1 : 0;
    return "M" + p0[0] + " " + p0[1] +
           "A" + r + " " + r + " 0 " + large + " 1 " + p1[0] + " " + p1[1];
  }

  // извлечь два куспид-числа из строки дат вида "20/21 марта – 20/21 апреля"
  function cuspNumbers(dates) {
    var m = dates.match(/(\d{1,2})\/(\d{1,2})/);
    if (m) { var a = parseInt(m[1],10), b = parseInt(m[2],10); return a < b ? [a,b] : [b,a]; }
    return [20, 21];
  }

  function buildSVG() {
    var svg = document.getElementById("zodiacWheel");
    if (!svg) return;
    svg.setAttribute("viewBox", "0 0 " + VB + " " + VB);

    function el(tag, attrs, parent) {
      var e = document.createElementNS(NS, tag);
      for (var k in attrs) e.setAttribute(k, attrs[k]);
      (parent || svg).appendChild(e);
      return e;
    }

    // ─── Центральная зона под карту(ы) ───
    el("circle", { cx: CX, cy: CY, r: R_CARD + 8, fill: "#0d0a1a", stroke: "rgba(212,175,55,.45)", "stroke-width": "2" });
    el("image", { id: "centerCardA", x: CX - 34, y: CY - 50, width: 68, height: 100, href: "", preserveAspectRatio: "xMidYMid meet" });
    el("image", { id: "centerCardB", x: CX - 34, y: CY - 50, width: 68, height: 100, href: "", preserveAspectRatio: "xMidYMid meet" });

    // ─── Сектора знаков + символ + планеты + куспид-числа по углам ───
    for (var i = 0; i < TOTAL; i++) {
      var a0 = -Math.PI / 2 + i * SEG;
      var a1 = a0 + SEG;
      var mid = a0 + SEG / 2;

      // сектор
      var rIn = R_CARD + 42;
      var p0o = polar(R_OUT, a0), p1o = polar(R_OUT, a1);
      var p0i = polar(rIn, a0), p1i = polar(rIn, a1);
      var large = SEG > Math.PI ? 1 : 0;
      el("path", {
        d: "M" + p0o[0] + " " + p0o[1] +
           "A" + R_OUT + " " + R_OUT + " 0 " + large + " 1 " + p1o[0] + " " + p1o[1] +
           "L" + p1i[0] + " " + p1i[1] +
           "A" + rIn + " " + rIn + " 0 " + large + " 0 " + p0i[0] + " " + p0i[1] + "Z",
        "class": "z-seg", "data-i": i
      });

      // символ знака
      var pm = polar((R_OUT + rIn) / 2 + 10, mid);
      el("text", { x: pm[0], y: pm[1], "text-anchor": "middle", "dominant-baseline": "central",
                   "class": "z-sym", "data-i": i }).textContent = SIGNS[i].sym;

      // глифы планет
      var pp = polar((R_OUT + rIn) / 2 - 30, mid);
      el("text", { x: pp[0], y: pp[1], "text-anchor": "middle", "dominant-baseline": "central",
                   "class": "z-planets", "data-i": i }).textContent = SIGNS[i].planetsGlyph;

      // куспид-числа в углах сектора (на внешнем ободе, у границ)
      var nums = cuspNumbers(SIGNS[i].dates);
      var cR = R_OUT - 38;
      // ближний угол (a0) — число nums[0], дальний (a1) — nums[1]
      var pn0 = polar(cR, a0 + SEG * 0.08);
      var pn1 = polar(cR, a1 - SEG * 0.08);
      el("text", { x: pn0[0], y: pn0[1], "text-anchor": "middle", "dominant-baseline": "central",
                   "class": "z-cusp", "data-i": i }).textContent = nums[0];
      el("text", { x: pn1[0], y: pn1[1], "text-anchor": "middle", "dominant-baseline": "central",
                   "class": "z-cusp", "data-i": i }).textContent = nums[1];
    }

    // ─── Обод месяцев (СВОЁ смещённое колесо: месяц на границе знака) ───
    // месяц i стоит на куспиде-границе перед сектором i (убрали +SEG/2 → сдвиг на полсектора)
    for (var i = 0; i < TOTAL; i++) {
      var mid = -Math.PI / 2 + i * SEG;
      var ma0 = mid - SEG * 0.42;
      var ma1 = mid + SEG * 0.42;
      var mr = R_OUT - 14;
      var pid = "zMonth" + i;
      el("path", { id: pid, d: arcPath(mr, ma0, ma1), fill: "none", stroke: "none" });
      var txt = el("text", { "class": "z-month", "pointer-events": "none" });
      var tp = el("textPath", { href: "#" + pid, startOffset: "50%", "text-anchor": "middle" });
      tp.textContent = MONTHS[i];
      txt.appendChild(tp);
    }

    // ─── Кружки возраста (шкала 7..84) на линиях куспидов ───
    // возрастной ряд: [84,7,14,21,28,35,42,49,56,63,70,77] на границах секторов
    var ageNums = [84, 7, 14, 21, 28, 35, 42, 49, 56, 63, 70, 77];
    for (var ag = 0; ag < TOTAL; ag++) {
      var lineAng = -Math.PI / 2 + ag * SEG;   // линия куспида перед сектором ag
      var pr = R_CARD + 42;                    // в САМОМ низу секторов, у внутренней границы (над картами)
      var pnt = polar(pr, lineAng);
      var circ = el("circle", { cx: pnt[0], cy: pnt[1], r: 15, "class": "z-age-dot" });
      el("text", { x: pnt[0], y: pnt[1], "text-anchor": "middle", "dominant-baseline": "central",
                   "class": "z-age-num" }).textContent = ageNums[ag];
    }


    // декоративные границы
    el("circle", { cx: CX, cy: CY, r: R_OUT, fill: "none", stroke: "rgba(212,175,55,.4)", "stroke-width": "2" });
    el("circle", { cx: CX, cy: CY, r: R_CARD + 42, fill: "none", stroke: "rgba(212,175,55,.3)", "stroke-width": "1.5" });
    el("circle", { cx: CX, cy: CY, r: R_CARD + 8, fill: "none", stroke: "rgba(212,175,55,.35)", "stroke-width": "1.5" });
  }

  // ─── Центральная карта(ы) ───
  function setCenterCard(i) {
    var s = SIGNS[i];
    var imgA = document.getElementById("centerCardA");
    var imgB = document.getElementById("centerCardB");
    if (!imgA) return;
    var hasB = !!s.cardFile2;

    if (hasB) {
      // две карты рядом
      imgA.setAttribute("x", CX - 68); imgA.setAttribute("width", 56); imgA.setAttribute("height", 88); imgA.setAttribute("y", CY - 44);
      imgA.setAttribute("href", CARDPATH + s.cardFile);
      imgA.setAttribute("xlink:href", CARDPATH + s.cardFile);
      imgB.setAttribute("x", CX + 12); imgB.setAttribute("width", 56); imgB.setAttribute("height", 88); imgB.setAttribute("y", CY - 44);
      imgB.setAttribute("href", CARDPATH + s.cardFile2);
      imgB.setAttribute("xlink:href", CARDPATH + s.cardFile2);
      imgB.setAttribute("opacity", "1");
    } else {
      // одна карта по центру
      imgA.setAttribute("x", CX - 45); imgA.setAttribute("width", 90); imgA.setAttribute("height", 132); imgA.setAttribute("y", CY - 66);
      imgA.setAttribute("href", CARDPATH + s.cardFile);
      imgA.setAttribute("xlink:href", CARDPATH + s.cardFile);
      imgB.setAttribute("opacity", "0");
    }
  }

  function renderDetail(i) {
    var s = SIGNS[i];
    var panel = document.getElementById("zDetail");
    if (!panel) return;
    panel.innerHTML =
      '<div class="zd-head">' +
        '<span class="zd-sym">' + s.sym + '</span>' +
        '<div><h3 class="zd-name">' + s.name + ' <span class="zd-arcan">' + s.arcans + '</span></h3>' +
        '<p class="zd-code">Кодовое слово: ' + s.code + '</p></div>' +
      '</div>' +
      '<div class="zd-grid">' +
        '<div class="zd-cell"><span class="zd-label">Дом</span><span class="zd-val">' + s.house + '</span></div>' +
        '<div class="zd-cell"><span class="zd-label">Планеты</span><span class="zd-val">' + s.planets + '</span></div>' +
        '<div class="zd-cell"><span class="zd-label">Главная планета</span><span class="zd-val">' + s.mainPlanet + '</span></div>' +
        '<div class="zd-cell"><span class="zd-label">Противоположность</span><span class="zd-val">' + s.opposite + '</span></div>' +
      '</div>' +
      '<p class="zd-text">' + s.text + '</p>' +
      '<p class="zd-text"><strong>Плюс:</strong> ' + s.plus + '</p>' +
      '<p class="zd-text"><strong>Негатив:</strong> ' + s.minus + '</p>' +
      '<div class="zd-month">' +
        '<p class="zd-label">Даты ' + s.dates + '</p>' +
        '<p class="zd-m"><strong>' + s.month + '</strong> — ' + s.work + '</p>' +
      '</div>' +
      '<div class="zd-actions">' +
        '<a class="zd-link" href="' + s.slug + '/">Открыть страницу знака →</a>' +
        '<button class="zd-btn" type="button" data-opp="' + s.oppositeSlug + '">Тень (' + s.opposite + ')</button>' +
      '</div>';

    var btn = panel.querySelector("[data-opp]");
    if (btn) btn.onclick = function () {
      var oi = dataIdx[btn.dataset.opp];
      if (oi !== undefined) selectSign(oi);
    };
  }

  function selectSign(i) {
    activeIndex = i;
    var segs = document.querySelectorAll(".z-seg");
    for (var k = 0; k < segs.length; k++) segs[k].classList.remove("active");
    var sel = document.querySelector('.z-seg[data-i="' + i + '"]');
    if (sel) sel.classList.add("active");

    setCenterCard(i);
    renderDetail(i);

    var dots = document.querySelectorAll(".z-nav-dot");
    for (var j = 0; j < dots.length; j++)
      dots[j].classList.toggle("active", parseInt(dots[j].dataset.i, 10) === i);
  }

  function onWheelClick(ev) {
    var target = ev.target;
    if (!target.closest) return;
    var el = target.closest("[data-i]");
    if (el) { var i = parseInt(el.getAttribute("data-i"), 10); selectSign(i); }
  }

  function buildNav() {
    var nav = document.getElementById("zNav");
    if (!nav) return;
    for (var i = 0; i < TOTAL; i++) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "z-nav-dot";
      b.dataset.i = i;
      b.title = SIGNS[i].name;
      b.textContent = SIGNS[i].sym;
      (function (idx) { b.onclick = function () { selectSign(idx); }; })(i);
      nav.appendChild(b);
    }
  }

  function init() {
    for (var i = 0; i < SIGNS.length; i++) dataIdx[SIGNS[i].slug] = i;
    buildSVG();
    buildNav();

    var svg = document.getElementById("zodiacWheel");
    if (svg) svg.addEventListener("click", onWheelClick);

    var prevB = document.getElementById("zPrev"), nextB = document.getElementById("zNext");
    if (prevB) prevB.onclick = function () { selectSign((activeIndex - 1 + TOTAL) % TOTAL); };
    if (nextB) nextB.onclick = function () { selectSign((activeIndex + 1) % TOTAL); };

    selectSign(0);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();