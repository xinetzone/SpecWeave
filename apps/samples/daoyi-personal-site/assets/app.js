/* 道一 daoyi — 个人站交互
   克制原则：只保留一次性淡入上移 + 轻微悬停反馈，无循环动效、无视差、无跟随光标。 */
(function () {
  "use strict";

  var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ── 一次性滚动揭示 ───────────────────── */
  (function reveal() {
    var targets = Array.prototype.slice.call(document.querySelectorAll("[data-reveal]"));
    if (!targets.length) return;

    if (reducedMotion || !("IntersectionObserver" in window)) {
      targets.forEach(function (el) { el.classList.add("is-visible"); });
      return;
    }

    document.documentElement.classList.add("motion-ready");

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target); /* 一次性：触发即停止观察 */
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
    );

    targets.forEach(function (el) { observer.observe(el); });
  })();

  /* ── 导航分隔线：滚过顶部才出现 ───────── */
  (function stickyNav() {
    var nav = document.querySelector(".site-nav");
    if (!nav) return;

    var ticking = false;
    function update() {
      nav.classList.toggle("is-stuck", window.scrollY > 8);
      ticking = false;
    }

    window.addEventListener(
      "scroll",
      function () {
        if (ticking) return;
        ticking = true;
        window.requestAnimationFrame(update);
      },
      { passive: true }
    );
    update();
  })();
})();
