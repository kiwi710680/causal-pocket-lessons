/* 因果口袋講義 — shared deck behaviour (AGENTS.md §5).
 * Paging, keyboard, URL hash, auto footer, quiz, reveal. No dependencies. */
(function () {
  "use strict";
  var body = document.body;
  var code = body.dataset.code || "";
  var title = body.dataset.title || document.title;
  var slides = Array.prototype.slice.call(document.querySelectorAll(".deck .slide"));
  var total = slides.length;
  var mobile = window.matchMedia("(max-width: 760px)");
  var current = 0;

  // ---- Auto footer on every slide ----
  slides.forEach(function (s, i) {
    var foot = document.createElement("div");
    foot.className = "slide-foot";
    foot.innerHTML = "<span></span><span></span>";
    foot.children[0].textContent = code + " · " + title;
    foot.children[1].textContent = pad(i + 1) + " / " + pad(total);
    s.appendChild(foot);
  });

  // ---- Wrap deck in a scaled stage + nav ----
  var deck = document.querySelector(".deck");
  var wrap = document.createElement("div");
  wrap.className = "stage-wrap";
  var stage = document.createElement("div");
  stage.className = "stage";
  deck.parentNode.insertBefore(wrap, deck);
  wrap.appendChild(stage);
  stage.appendChild(deck);
  body.classList.add("deck-body");

  var bar = document.createElement("div");
  bar.className = "progress";
  body.appendChild(bar);

  var nav = document.createElement("nav");
  nav.className = "deck-nav";
  nav.setAttribute("aria-label", "翻頁");
  nav.innerHTML =
    '<a href="../../">← 講義目錄</a>' +
    '<button type="button" aria-label="上一頁">‹</button>' +
    '<span class="count"></span>' +
    '<button type="button" aria-label="下一頁">›</button>';
  body.appendChild(nav);
  var prevBtn = nav.querySelectorAll("button")[0];
  var nextBtn = nav.querySelectorAll("button")[1];
  var count = nav.querySelector(".count");
  prevBtn.addEventListener("click", function () { go(current - 1); });
  nextBtn.addEventListener("click", function () { go(current + 1); });

  function pad(n) { return n < 10 ? "0" + n : String(n); }

  function fit() {
    if (mobile.matches) { stage.style.transform = ""; return; }
    var w = wrap.clientWidth - 32, h = wrap.clientHeight - 24;
    var k = Math.min(w / 1280, h / 720);
    stage.style.transform = "translate(-50%, -50%) scale(" + k + ")";
  }

  function go(i) {
    if (i < 0 || i >= total) return;
    current = i;
    slides.forEach(function (s, j) { s.classList.toggle("is-active", j === i); });
    count.textContent = pad(i + 1) + " / " + pad(total);
    prevBtn.disabled = i === 0;
    nextBtn.disabled = i === total - 1;
    bar.style.width = ((i + 1) / total * 100) + "%";
    if (location.hash !== "#" + (i + 1)) history.replaceState(null, "", "#" + (i + 1));
  }

  document.addEventListener("keydown", function (e) {
    if (mobile.matches) return;
    var t = e.target.tagName;
    if (t === "INPUT" || t === "TEXTAREA" || t === "SELECT") return;
    if (e.key === "ArrowRight" || e.key === "PageDown" || (e.key === " " && t !== "BUTTON")) { e.preventDefault(); go(current + 1); }
    else if (e.key === "ArrowLeft" || e.key === "PageUp") { e.preventDefault(); go(current - 1); }
    else if (e.key === "Home") go(0);
    else if (e.key === "End") go(total - 1);
  });

  // ---- Quiz: <div class="quiz" data-answer="b"> + button[data-opt][data-why] ----
  document.querySelectorAll(".quiz").forEach(function (q) {
    var ans = q.dataset.answer;
    var why = q.querySelector(".quiz-why");
    q.querySelectorAll("button[data-opt]").forEach(function (b) {
      b.addEventListener("click", function () {
        var ok = b.dataset.opt === ans;
        q.querySelectorAll("button[data-opt]").forEach(function (o) { o.classList.remove("right", "wrong"); });
        b.classList.add(ok ? "right" : "wrong");
        if (why) {
          why.className = "quiz-why " + (ok ? "right" : "wrong");
          why.textContent = (ok ? "答對了。" : "再想想。") + (b.dataset.why || "");
        }
      });
    });
  });

  // ---- Reveal: .reveal > .reveal-btn + .reveal-body ----
  document.querySelectorAll(".reveal").forEach(function (r) {
    var btn = r.querySelector(".reveal-btn");
    var label = btn.textContent;
    btn.setAttribute("aria-expanded", "false");
    btn.addEventListener("click", function () {
      var open = r.classList.toggle("is-open");
      btn.setAttribute("aria-expanded", String(open));
      btn.textContent = open ? "收起" : label;
    });
  });

  window.addEventListener("resize", fit);
  mobile.addEventListener("change", fit);
  fit();
  var start = parseInt(location.hash.slice(1), 10);
  go(start >= 1 && start <= total ? start - 1 : 0);
  if (mobile.matches) slides.forEach(function (s) { s.classList.add("is-active"); });
  mobile.addEventListener("change", function () {
    if (mobile.matches) slides.forEach(function (s) { s.classList.add("is-active"); });
    else go(current);
  });
})();
