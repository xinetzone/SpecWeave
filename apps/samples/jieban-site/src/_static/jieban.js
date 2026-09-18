/* 结伴 · 站点行为层
 *
 * 只做一件事：滚动淡入（IntersectionObserver），与落地页 .reveal 的节奏一致。
 * 这是纯渐进增强——JS 未执行时内容完整可见，只是没有入场动效。
 *
 * 曾在此注入「印章 + 品牌 + 菜单」顶栏：那是拆掉左侧栏后的补救。
 * 侧栏已恢复（品牌与主导航本就挂在左侧栏内），注入即重复，故移除。
 *
 * 刻意不做：落地页的频道选择器与入群弹窗——站点一期公开承诺「不设表单、不收集信息」，
 * 引入它们会与公约页自相矛盾（见 tests/test_site_contract.py 的相应断言）。
 */
(function () {
  "use strict";

  var REVEAL_SEL = [
    ".jb-seal",
    ".jb-sub",
    ".jb-quote",
    ".jb-cta",
    ".jb-manifesto",
    ".jb-card",
    ".jb-rules",
    ".jb-origin-grid",
    ".jb-federal",
    ".jb-timeline",
    ".jb-choices",
    ".jb-privacy",
    "article.bd-article h2",
    "table",
    "pre.mermaid",
  ].join(",");

  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("jb-in");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12 }
    );
    document.querySelectorAll(REVEAL_SEL).forEach(function (el) {
      el.classList.add("jb-reveal");
      io.observe(el);
    });
  }
})();