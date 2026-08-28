// ═══════════════ Колесо Зодиака — логика (v1.7) ═══════════════
// Интерактивное SVG-колесо: 12 знаков по кругу, подсветка активного, клик → панель деталей.
(function () {
  "use strict";
  if (typeof window.ZODIAC_WHEEL === "undefined") return;

  var SIGNS = window.ZODIAC_WHEEL;
  var TOTAL = SIGNS.length;
  var SEG = (2 * Math.PI) / TOTAL;
  var activeIndex = 0;
  var dataIdx = {};

  var NS = "http://www.w3.org/2000/svg";
  var VB = 600, CX = VB / 2, CY = VB / 2;
  var R_OUT = 288, R_IN = 198;

  function polar(r, ang) { return [CX + r * Math.cos(ang), CY + r * Math.sin(ang)]; }

  function buildSVG() {
    var svg = document.getElementById("zodiacWheel");
    if (!svg) return;
    svg.setAttribute("viewBox", "0 0 " + VB + " " + VB);

    function el(tag, attrs) {
      var e = document.createElementNS(NS, tag);
      for (var k in attrs) e.setAttribute(k, attrs[k]);
      svg.appendChild(e);
      return e;
    }

    // фон
    el("circle", { cx: CX, cy: CY, r: R_OUT, fill: "rgba(23,18,43,.6)", stroke: "rgba(212,175,55,.35)", "stroke-width": "2" });

    for (var i = 0; i < TOTAL; i++) {
      var a0 = -Math.PI / 2 + i * SEG;
      var a1 = a0 + SEG;
      var p0 = polar(R_OUT, a0), p1 = polar(R_OUT, a1);
      var p2 = polar(R_IN, a0), p3 = polar(R_IN, a1);
      var large = SEG > Math.PI ? 1 : 0;

      var path = el("path", {
        d: "M" + p0[0] + " " + p0[1] +
           "A" + R_OUT + " " + R_OUT + " 0 " + large + " 1 " + p1[0] + " " + p1[1] +
           "L" + p3[0] + " " + p3[1] +
           "A" + R_IN + " " + R_IN + " 0 " + large + " 0 " + p2[0] + " " + p2[1] + "Z",
        "class": "z-seg", "data-i": i
      });

      var mid = a0 + SEG / 2;

      var pm = polar((R_OUT + R_IN) / 2 + 8, mid);
      el("text", { x: pm[0], y: pm[1], "text-anchor": "middle", "dominant-baseline": "central", "class": "z-sym", "data-i": i }).textContent = SIGNS[i].sym;

      var pn = polar(R_OUT - 26, mid);
      el("text", { x: pn[0], y: pn[1], "text-anchor": "middle", "dominant-baseline": "central", "class": "z-name", "data-i": i }).textContent = SIGNS[i].name;

      var pc = polar((R_OUT + R_IN) / 2 - 34, mid);
      el("text", { x: pc[0], y: pc[1], "text-anchor": "middle", "dominant-baseline": "central", "class": "z-code", "data-i": i }).textContent = SIGNS[i].code;
    }

    // центр
    el("circle", { cx: CX, cy: CY, r: R_IN - 18, fill: "rgba(13,10,26,.85)", stroke: "rgba(212,175,55,.35)", "stroke-width": "1.5" });
    el("text", { x: CX, y: CY - 16, "text-anchor": "middle", "dominant-baseline": "central", "class": "z-center-sym", id: "centerSym" });
    el("text", { x: CX, y: CY + 30, "text-anchor": "middle", "dominant-baseline": "central", "class": "z-center-name", id: "centerName" });

    // стрелка сверху
    el("polygon", { points: CX + ",26 " + (CX - 13) + ",58 " + (CX + 13) + ",58", fill: "var(--gold-bright)", id: "zNeedle" });
  }

  function setCenter(i) {
    var s = SIGNS[i];
    var cs = document.getElementById("centerSym");
    var cn = document.getElementById("centerName");
    if (cs) cs.textContent = s.sym;
    if (cn) cn.textContent = s.name;
  }

  function renderDetail(i) {
    var s = SIGNS[i];
    var panel = document.getElementById("zDetail");
    if (!panel) return;
    panel.innerHTML =
      '<div class="zd-head">' +
        '<span class="zd-sym">' + s.sym + '</span>' +
        '<div><h3 class="zd-name">' + s.name + '</h3>' +
        '<p class="zd-code">Кодовое слово: ' + s.code + '</p></div>' +
      '</div>' +
      '<div class="zd-grid">' +
        '<div class="zd-cell"><span class="zd-label">Аркан</span><span class="zd-val">' + s.arcans + '</span></div>' +
        '<div class="zd-cell"><span class="zd-label">Дом</span><span class="zd-val">' + s.house + '</span></div>' +
        '<div class="zd-cell"><span class="zd-label">Планеты</span><span class="zd-val">' + s.planets + '</span></div>' +
        '<div class="zd-cell"><span class="zd-label">Противоположность</span><span class="zd-val">' + s.opposite + '</span></div>' +
      '</div>' +
      '<p class="zd-text">' + s.text + '</p>' +
      '<p class="zd-text"><strong>Плюс:</strong> ' + s.plus + '</p>' +
      '<p class="zd-text"><strong>Негатив:</strong> ' + s.minus + '</p>' +
      '<div class="zd-month">' +
        '<p class="zd-label">Время года · сельхоз-круг</p>' +
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

    setCenter(i);
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