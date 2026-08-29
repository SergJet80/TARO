// ═══════════════ Колесо Зодиака — логика (v1.8) ═══════════════
// Структура (по описанию структуры колеса): внешнее кольцо — месяц+даты по дуге,
// сектора — символ знака + глифы планет; в центре — карта активного старшего аркана.
// Кодовые слова и горизонтальные названия убраны с колеса (они в панели внизу).

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
  var R_OUT = 296;      // внешний радиус
  var R_CARD = 132;     // радиус отверстия в центре под карту
  var CARDPATH = "../img/cards/";

  function polar(r, ang) { return [CX + r * Math.cos(ang), CY + r * Math.sin(ang)]; }

  // дуга между двумя углами (описывает окружность по часовой)
  function arcPath(r, a0, a1) {
    var p0 = polar(r, a0), p1 = polar(r, a1);
    var large = (a1 - a0) > Math.PI ? 1 : 0;
    return "M" + p0[0] + " " + p0[1] +
           "A" + r + " " + r + " 0 " + large + " 1 " + p1[0] + " " + p1[1];
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

    // ─── Центральная зона: круглая подложка под активную карту ───
    el("circle", { cx: CX, cy: CY, r: R_CARD + 6, fill: "#0d0a1a", stroke: "rgba(212,175,55,.45)", "stroke-width": "2" });

    // изображение активной карты (в центре), будет обновляться selectSign
    var img = el("image", { id: "centerCard", x: CX - 62, y: CY - 92, width: 124, height: 184, href: "", preserveAspectRatio: "xMidYMid meet" });
    img.setAttribute("xlink:href", "");
    // обводка-рамка карты
    // (clip нет — карта вписывается по высоте)

    // ─── Сектора ───
    for (var i = 0; i < TOTAL; i++) {
      var a0 = -Math.PI / 2 + i * SEG;
      var a1 = a0 + SEG;
      var mid = a0 + SEG / 2;

      // 1) сектор внешнего кольца (от R_OUT до R_CARD+30)
      var rIn = R_CARD + 34;
      var p0o = polar(R_OUT, a0), p1o = polar(R_OUT, a1);
      var p0i = polar(rIn, a0), p1i = polar(rIn, a1);
      var large = SEG > Math.PI ? 1 : 0;
      var path = el("path", {
        d: "M" + p0o[0] + " " + p0o[1] +
           "A" + R_OUT + " " + R_OUT + " 0 " + large + " 1 " + p1o[0] + " " + p1o[1] +
           "L" + p1i[0] + " " + p1i[1] +
           "A" + rIn + " " + rIn + " 0 " + large + " 0 " + p0i[0] + " " + p0i[1] + "Z",
        "class": "z-seg", "data-i": i
      });

      // 2) символ знака — по центру сектора (крупно)
      var pm = polar((R_OUT + rIn) / 2 + 6, mid);
      el("text", { x: pm[0], y: pm[1], "text-anchor": "middle", "dominant-baseline": "central", "class": "z-sym", "data-i": i }).textContent = SIGNS[i].sym;

      // 3) глифы планет — чуть ближе к центру под символом
      var pp = polar((R_OUT + rIn) / 2 - 34, mid);
      el("text", { x: pp[0], y: pp[1], "text-anchor": "middle", "dominant-baseline": "central", "class": "z-planets", "data-i": i }).textContent = SIGNS[i].planetsGlyph;

      // 4) месяц + дата по дуге (внешняя кромка сектора)
      //    путь-дуга для textPath (в середине кольца месяца)
      var mr = R_OUT - 20;
      var arc = arcPath(mr, a0, a1);
      var pid = "zArc" + i;
      el("path", { id: pid, d: arc, fill: "none", stroke: "none" });
      var txt = el("text", { "class": "z-month", "pointer-events": "none" });
      var tp = el("textPath", { href: "#" + pid, startOffset: "50%", "text-anchor": "middle" });
      tp.textContent = SIGNS[i].month;
      txt.appendChild(tp);

      // 5) даты — чуть ближе к центру чем месяц, по дуге
      var dr = R_OUT - 42;
      var arcD = arcPath(dr, a0, a1);
      var pidD = "zArcD" + i;
      el("path", { id: pidD, d: arcD, fill: "none", stroke: "none" });
      var txtD = el("text", { "class": "z-dates", "pointer-events": "none" });
      var tpD = el("textPath", { href: "#" + pidD, startOffset: "50%", "text-anchor": "middle" });
      tpD.textContent = SIGNS[i].dates;
      txtD.appendChild(tpD);
    }

    // декоративные границы колец
    el("circle", { cx: CX, cy: CY, r: R_OUT, fill: "none", stroke: "rgba(212,175,55,.4)", "stroke-width": "2" });
    el("circle", { cx: CX, cy: CY, r: R_CARD + 34, fill: "none", stroke: "rgba(212,175,55,.3)", "stroke-width": "1.5" });
    el("circle", { cx: CX, cy: CY, r: R_CARD + 6, fill: "none", stroke: "rgba(212,175,55,.35)", "stroke-width": "1.5" });

    // название активного аркана под картой в центре
    el("text", { x: CX, y: CY + 118, "text-anchor": "middle", "dominant-baseline": "central", "class": "z-center-card-name", id: "centerCardName" });
  }

  // Обновление центральной карты
  function setCenterCard(i) {
    var s = SIGNS[i];
    var img = document.getElementById("centerCard");
    if (img) {
      img.setAttribute("href", CARDPATH + s.cardFile);
      img.setAttribute("xlink:href", CARDPATH + s.cardFile);
    }
    var nm = document.getElementById("centerCardName");
    if (nm) nm.textContent = s.name + " · " + s.arcans;
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