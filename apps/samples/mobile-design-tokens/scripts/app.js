/* =============================================================
   Design Token 工作台 —— 交互逻辑
   · 渲染：由 scripts/tokens.js 的数据生成色阶 / 语义色 / 圆角 / 阴影
   · 换肤：<html> 上切换 theme-root / theme-dark / theme-auto 类名
           （语义变量的 Mode 切换，组件属性不变）
   · 工具：搜索过滤、点击复制变量、导出 tokens.css / tokens.json
   ============================================================= */

(function () {
  "use strict";

  var T = window.DESIGN_TOKENS;
  var THEME_KEY = "specweave.design-tokens.theme";

  /* ------------------------- 工具函数 ------------------------- */

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = text;
    return node;
  }

  /** 相对亮度，用于决定色块上的文字取深色还是白色 */
  function luminance(hex) {
    var c = hex.replace("#", "");
    var r = parseInt(c.slice(0, 2), 16) / 255;
    var g = parseInt(c.slice(2, 4), 16) / 255;
    var b = parseInt(c.slice(4, 6), 16) / 255;
    var lin = function (v) {
      return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
    };
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
  }

  function inkOn(hex) {
    return luminance(hex) < 0.35 ? "#FFFFFF" : "#1A1F29";
  }

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }
    // file:// 场景兜底
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    try {
      document.execCommand("copy");
    } catch (e) {
      /* 忽略：仅提示 */
    }
    document.body.removeChild(ta);
    return Promise.resolve();
  }

  var toast = document.getElementById("toast");
  var toastTimer = null;

  function showToast(label, value) {
    toast.innerHTML = "";
    toast.appendChild(document.createTextNode(label + "："));
    toast.appendChild(el("span", "toast__code", value));
    toast.classList.add("is-visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () {
      toast.classList.remove("is-visible");
    }, 1800);
  }

  /* ------------------------- 主题切换 ------------------------- */

  var themeButtons = Array.prototype.slice.call(
    document.querySelectorAll(".switch__btn")
  );

  function applyTheme(mode) {
    var html = document.documentElement;
    html.classList.remove("theme-root", "theme-dark", "theme-auto");
    html.classList.add(mode === "dark" ? "theme-dark" : mode === "auto" ? "theme-auto" : "theme-root");
    themeButtons.forEach(function (btn) {
      btn.setAttribute(
        "aria-pressed",
        btn.dataset.theme === mode ? "true" : "false"
      );
    });
    try {
      localStorage.setItem(THEME_KEY, mode);
    } catch (e) {
      /* 隐私模式下忽略 */
    }
  }

  themeButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      applyTheme(btn.dataset.theme);
      showToast("主题模式", btn.textContent.trim());
    });
  });

  var saved = null;
  try {
    saved = localStorage.getItem(THEME_KEY);
  } catch (e) {
    saved = null;
  }
  applyTheme(saved === "dark" || saved === "auto" ? saved : "light");

  /* ------------------------- 元信息 ------------------------- */

  var metaText =
    T.meta.collections +
    " 组变量集合 · " +
    T.meta.variables +
    " 个变量 · " +
    T.meta.modes +
    " 套主题模式 · " +
    T.meta.summary;

  document.getElementById("app-meta").textContent =
    T.semantic.length + " 个语义变量 · 明暗 Mode 切换";
  document.getElementById("page-meta").textContent = metaText;
  document.getElementById("foot-meta").textContent =
    "由 Ardot 设计稿《移动端 Design Token 体系》生成 · " + metaText;

  /* ------------------------- 01 原始色阶 ------------------------- */

  var primitiveHost = document.getElementById("primitives-groups");

  T.primitives.forEach(function (group) {
    var wrap = el("div", "ramp-group");
    wrap.dataset.group = group.id;
    wrap.appendChild(el("span", "ramp-group__title", group.title));

    var row = el("div", "ramp-row");
    row.style.gridTemplateColumns =
      "repeat(" + group.swatches.length + ", minmax(0, 1fr))";

    group.swatches.forEach(function (sw) {
      var chip = el("button", "chip");
      chip.type = "button";
      chip.style.background = sw.hex;
      chip.dataset.search =
        (group.id + " " + sw.step + " " + sw.hex).toLowerCase();
      chip.dataset.copy = sw.hex;

      var label = el("span", "chip__label", sw.step + "\n" + sw.hex);
      label.style.color = inkOn(sw.hex);
      chip.appendChild(label);

      chip.addEventListener("click", function () {
        copyText(sw.hex).then(function () {
          showToast("已复制色值", sw.hex);
        });
      });

      row.appendChild(chip);
    });

    wrap.appendChild(row);
    primitiveHost.appendChild(wrap);
  });

  /* ------------------------- 02 语义色 ------------------------- */

  function renderSemantic(hostId, modeKey) {
    var host = document.getElementById(hostId);
    T.semantic.forEach(function (token) {
      var value = token[modeKey];

      var unit = el("button", "token");
      unit.type = "button";
      unit.dataset.search = (token.name + " " + value).toLowerCase();
      unit.dataset.copy = "var(--" + token.name + ")";

      var swatch = el("span", "token__swatch");
      swatch.style.setProperty("--swatch", "var(--" + token.name + ")");
      unit.appendChild(swatch);
      unit.appendChild(el("span", "token__name", token.name));
      unit.appendChild(el("span", "token__value", value));

      unit.addEventListener("click", function () {
        copyText("var(--" + token.name + ")").then(function () {
          showToast("已复制 CSS 变量", "--" + token.name);
        });
      });

      host.appendChild(unit);
    });
  }

  renderSemantic("semantic-light", "light");
  renderSemantic("semantic-dark", "dark");

  /* ------------------------- 03 圆角 ------------------------- */

  var radiusHost = document.getElementById("radius-grid");

  T.radius.forEach(function (r) {
    var unit = el("button", "radius-unit");
    unit.type = "button";
    unit.dataset.search = (r.name + " " + r.px + " " + r.usage).toLowerCase();
    unit.dataset.copy = "var(--" + r.name + ")";

    var preview = el("span", "radius-unit__preview");
    preview.style.setProperty("--unit-radius", "var(--" + r.name + ")");
    unit.appendChild(preview);

    unit.appendChild(
      el("span", "radius-unit__name", r.name + " · " + r.px + "px")
    );
    unit.appendChild(el("span", "radius-unit__usage", r.usage));

    unit.addEventListener("click", function () {
      copyText("var(--" + r.name + ")").then(function () {
        showToast("已复制圆角变量", "--" + r.name);
      });
    });

    radiusHost.appendChild(unit);
  });

  /* ------------------------- 04 阴影 ------------------------- */

  function renderShadows(hostId) {
    var host = document.getElementById(hostId);
    T.shadow.forEach(function (s) {
      var params =
        "y " + s.y + " · blur " + s.blur + " · spread " + s.spread;

      var card = el("div", "shadow-card");
      card.style.setProperty("--card-shadow", "var(--" + s.name + ")");
      card.dataset.search = (s.name + " " + params).toLowerCase();
      card.appendChild(el("span", "shadow-card__name", s.name));
      card.appendChild(el("span", "shadow-card__params", params));
      host.appendChild(card);
    });
  }

  renderShadows("shadow-light");
  renderShadows("shadow-dark");

  /* ------------------------- 搜索过滤 ------------------------- */

  var searchInput = document.getElementById("search");
  var navChips = Array.prototype.slice.call(
    document.querySelectorAll(".nav__chip")
  );

  function filterTokens(keyword) {
    var kw = keyword.trim().toLowerCase();
    var nodes = Array.prototype.slice.call(
      document.querySelectorAll("[data-search]")
    );

    if (!kw) {
      nodes.forEach(function (n) {
        n.classList.remove("is-dimmed");
      });
      document
        .querySelectorAll(".is-empty-hidden")
        .forEach(function (n) {
          n.classList.remove("is-empty-hidden");
        });
      navChips.forEach(function (c) {
        c.classList.remove("is-hidden");
      });
      return;
    }

    var hits = 0;
    nodes.forEach(function (n) {
      var match = n.dataset.search.indexOf(kw) !== -1;
      n.classList.toggle("is-dimmed", !match);
      if (match) hits += 1;
    });

    // 命中的区块才保留导航入口
    var visibleSections = {};
    nodes.forEach(function (n) {
      if (n.classList.contains("is-dimmed")) return;
      var section = n.closest(".section");
      if (section) visibleSections[section.id] = true;
    });

    navChips.forEach(function (chip) {
      var target = chip.getAttribute("href").replace("#", "");
      chip.classList.toggle("is-hidden", !visibleSections[target]);
    });

    if (hits === 0) {
      showToast("没有匹配", kw);
    }
  }

  searchInput.addEventListener("input", function (e) {
    filterTokens(e.target.value);
  });

  searchInput.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      searchInput.value = "";
      filterTokens("");
      searchInput.blur();
    }
  });

  /* ------------------------- 章节高亮 ------------------------- */

  if ("IntersectionObserver" in window) {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var id = entry.target.id;
          navChips.forEach(function (chip) {
            var active = chip.getAttribute("href") === "#" + id;
            if (active) {
              chip.setAttribute("aria-current", "true");
            } else {
              chip.removeAttribute("aria-current");
            }
          });
        });
      },
      { rootMargin: "-96px 0px -60% 0px" }
    );

    document.querySelectorAll(".section").forEach(function (s) {
      observer.observe(s);
    });
  }

  /* ------------------------- 导出 ------------------------- */

  function download(filename, content, mime) {
    var blob = new Blob([content], { type: mime });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(function () {
      URL.revokeObjectURL(url);
    }, 1000);
  }

  function buildCss() {
    var lines = [];
    lines.push("/* 移动端 Design Token 体系 —— 导出自 Ardot 设计稿 */");
    lines.push(":root {");

    lines.push("  /* Primitives */");
    var allGroups = T.primitives;
    var families = [
      { key: "neutral", prefix: "neutral" },
      { key: "brand", prefix: "brand" },
    ];
    families.forEach(function (f) {
      var g = allGroups.filter(function (x) {
        return x.id === f.key;
      })[0];
      g.swatches.forEach(function (s) {
        lines.push("  --" + f.prefix + "-" + s.step + ": " + s.hex + ";");
      });
    });
    [
      ["success-100", "#E7F8EF"],
      ["success-500", "#17B26A"],
      ["success-700", "#087443"],
      ["warning-100", "#FEF0DC"],
      ["warning-500", "#F79009"],
      ["warning-700", "#B54708"],
      ["danger-100", "#FEE4E2"],
      ["danger-500", "#F04438"],
      ["danger-700", "#B42318"],
    ].forEach(function (p) {
      lines.push("  --" + p[0] + ": " + p[1] + ";");
    });

    lines.push("");
    lines.push("  /* Radius */");
    T.radius.forEach(function (r) {
      lines.push("  --" + r.name + ": " + r.px + "px;");
    });

    lines.push("");
    lines.push("  /* Semantic（Light 模式取值） */");
    T.semantic.forEach(function (t) {
      lines.push("  --" + t.name + ": " + t.light.split(" ")[0] + ";");
    });

    lines.push("");
    lines.push("  /* Shadow（Light 模式取值） */");
    T.shadow.forEach(function (s) {
      lines.push(
        "  --" +
          s.name +
          ": 0 " +
          s.y +
          "px " +
          s.blur +
          "px " +
          s.spread +
          "px rgba(14, 18, 24, " +
          s.rgba +
          ");"
      );
    });

    lines.push("}");
    lines.push("");
    lines.push('[data-theme="dark"] {');
    lines.push("  /* Semantic（Dark 模式取值） */");
    T.semantic.forEach(function (t) {
      lines.push("  --" + t.name + ": " + t.dark.split(" ")[0] + ";");
    });
    lines.push("");
    lines.push("  /* Shadow（Dark：纯黑 @ 30%–60%） */");
    [
      ["shadow-1", 1, 2, 0, 0.3],
      ["shadow-2", 2, 8, -2, 0.36],
      ["shadow-3", 4, 16, -4, 0.42],
      ["shadow-4", 8, 24, -6, 0.5],
      ["shadow-5", 16, 40, -8, 0.6],
    ].forEach(function (s) {
      lines.push(
        "  --" +
          s[0] +
          ": 0 " +
          s[1] +
          "px " +
          s[2] +
          "px " +
          s[3] +
          "px rgba(0, 0, 0, " +
          s[4] +
          ");"
      );
    });
    lines.push("}");
    lines.push("");

    return lines.join("\n");
  }

  document.getElementById("export-css").addEventListener("click", function () {
    download("tokens.css", buildCss(), "text/css;charset=utf-8");
    showToast("已导出", "tokens.css");
  });

  document.getElementById("export-json").addEventListener("click", function () {
    var payload = {
      meta: T.meta,
      primitives: T.primitives,
      semantic: T.semantic,
      radius: T.radius,
      shadow: T.shadow,
    };
    download(
      "tokens.json",
      JSON.stringify(payload, null, 2),
      "application/json;charset=utf-8"
    );
    showToast("已导出", "tokens.json");
  });

  document.getElementById("reset-theme").addEventListener("click", function () {
    searchInput.value = "";
    filterTokens("");
    applyTheme("light");
    showToast("已重置", "浅色模式");
  });
})();
