/* ============================================================
   大道极简生存指南 · 七条判据 —— 应用逻辑
   数据忠实于知识包「04 · 大道极简生存指南」原文
   ============================================================ */

"use strict";

/* ---------- 七条判据数据（源自原文） ---------- */
const PRINCIPLES = [
  {
    num: "一",
    name: "切掉不可逆项，剩下的才是问题",
    layer: "诊断层",
    q: "问题清单里每项都能改变吗？把「已发生」「还没发生」都划掉，只留「正在发生且可干预」的。",
    short: "这件事我能改变吗？不能就划掉",
    counter: "把「我父母从小管得太严」当问题——过去不可改，分析它产生不了行动。不可逆项占比越高，越容易产出无力感。",
    t: "2 分钟",
    action: "写下你最纠结的一件事，标注时态：过去 / 现在 / 未来。只有「现在」能进清单。"
  },
  {
    num: "二",
    name: "说不清阻塞什么，就不是问题",
    layer: "诊断层",
    q: "能用一句话说清「它阻塞了什么具体结果」吗？说不出 → 是情绪。",
    short: "它阻塞了什么具体结果？",
    counter: "「提升自己」「变得更优秀」——没有具体阻塞对象，因此无法判定是否解决。",
    t: "2 分钟",
    action: "改写成「我不能___，因为___受阻」。填不出空，就是情绪。"
  },
  {
    num: "三",
    name: "先有一件做出来的东西，再谈身份",
    layer: "能力层",
    q: "技能清单里有没有至少一项有实际验证（作品 / 数据 / 他人反馈）？全无 → 先做。",
    short: "技能清单里有实际验证的项吗？",
    counter: "「我是一个终身学习者」但无任何可展示产出——用身份代替能力。叙事不是证据。",
    t: "5 分钟",
    action: "写出过去 30 天产出的一件别人能看到的东西。写不出 → 今天做一件。"
  },
  {
    num: "四",
    name: "真需求是能力或状态，不是情绪",
    layer: "能力层",
    q: "需要的东西能写成「能在___条件下做出___」或「处于___状态」吗？写不出 → 不是需求。",
    short: "能写成「能 X」或「处于 X 状态」吗？",
    counter: "「我需要被认可」——不是可训练的能力，也不是可到达的状态，是期待。期待无法通过努力满足。",
    t: "3 分钟",
    action: "把「我需要 X」改写为「我需要能 X」或「我需要处在 X 状态」。改不动的就是情绪。"
  },
  {
    num: "五",
    name: "拒绝对你有利的，比做好事更能暴露品质",
    layer: "能力层",
    q: "过去一个月，有没有拒绝过一次「对我有利、但你知道不对」的机会？没有 → 品质层需建设。",
    short: "上月拒绝过一次诱惑吗？",
    counter: "把「我做的都是好事」当品质证明——做好事在无诱惑时是容易的。品质只在诱惑面前成立。",
    t: "2 分钟",
    action: "今天做一件不告诉任何人、短期无回报的事。"
  },
  {
    num: "六",
    name: "二元对立的选项，多半有第三项",
    layer: "行动版",
    q: "面对「A 还是 B」，先花 30 秒找「三」：有没有同时含 A 和 B 的选项？",
    short: "找 30 秒，问「有没有第三项」",
    counter: "把「工作 vs 生活」当二选一——把「二的对立」当成了全部选项。不整合的对立会一直僵持。",
    t: "2 分钟",
    action: "写下当前最大的二选，在旁补一行「有没有第三项」。找不到 → 接受对立，否则会一直耗在这。"
  },
  {
    num: "七",
    name: "先设计连接方式，再设计两端",
    layer: "行动版",
    q: "做协作 / 系统 / 关系时，是否先定义了「怎么连」（接口、协议、说法、承诺）？",
    short: "谁给谁、给什么、什么格式？",
    counter: "先做完两个模块再想怎么通信 → 规则变成事后补丁，且必须跟着两端反复改。",
    t: "5 分钟",
    action: "在正在做的一件协作里写下三句——谁给谁、给什么、什么格式。只写这三句。"
  }
];

const LAYER_ORDER = ["诊断层", "能力层", "行动版"];
const LAYER_NOTES = {
  "诊断层": "真问题 · 真需求 · 真目标——回答「该做什么」",
  "能力层": "品质 · 技能 · 身份——回答「我能做什么」",
  "行动版": "六 = 「二生三」的行动版，把二元对立整合出第三项；七 = 「三 = 关系位」的行动版，先设计连接而非两端"
};

const STORE_KEY = "dao-survival-guide:v1";
const LAYER_INDEX = PRINCIPLES.reduce(function (m, p, i) {
  (m[p.layer] = m[p.layer] || []).push(i);
  return m;
}, {});

/* ---------- 状态 ---------- */
let answers = loadState(); // answers[i] ∈ null | "pass" | "fail" | "unsure"
let current = null;        // 当前提问下标 0..6

function loadState() {
  try {
    const raw = localStorage.getItem(STORE_KEY);
    if (!raw) return new Array(PRINCIPLES.length).fill(null);
    const data = JSON.parse(raw);
    const arr = new Array(PRINCIPLES.length).fill(null);
    (data || []).forEach(function (v, i) {
      if (v === "pass" || v === "fail" || v === "unsure") arr[i] = v;
    });
    return arr;
  } catch (e) {
    return new Array(PRINCIPLES.length).fill(null);
  }
}

function saveState() {
  try { localStorage.setItem(STORE_KEY, JSON.stringify(answers)); } catch (e) { /* 忽略 */ }
}

function isPassed(i) { return answers[i] === "pass"; }
function isFailed(i) { return answers[i] === "fail" || answers[i] === "unsure"; }
function answeredCount() {
  return answers.reduce(function (n, v) { return n + (v !== null ? 1 : 0); }, 0);
}
function passedCount() {
  return answers.reduce(function (n, v) { return n + (v === "pass" ? 1 : 0); }, 0);
}

/* ---------- 视图路由 ---------- */
const VIEWS = ["view-intro", "view-judge", "view-result", "view-table"];
const STEP_LABEL = { "view-intro": "序", "view-judge": "判", "view-result": "状", "view-table": "表" };

function showView(id) {
  VIEWS.forEach(function (v) {
    document.getElementById(v).hidden = v !== id;
  });
  document.getElementById("topbar-step").textContent = STEP_LABEL[id] || "";
  window.scrollTo(0, 0);
}

function goIntro() { showView("view-intro"); }
function goJudge(i) {
  if (i < 0 || i >= PRINCIPLES.length) i = 0;
  current = i;
  renderProgress();
  renderJudge();
  showView("view-judge");
}
function goResult() { renderResult(); showView("view-result"); }
function goTable() { showView("view-table"); }

/* ---------- 进度路径（盖印节点） ---------- */
function renderProgress() {
  const box = document.getElementById("progress");
  box.innerHTML = "";
  PRINCIPLES.forEach(function (p, i) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "progress-cell";
    btn.textContent = p.num;
    btn.setAttribute("aria-label", "第 " + p.num + " 问：" + p.name + (answers[i] ? "（已判）" : "（未判）"));
    if (isPassed(i)) btn.classList.add("done-pass");
    else if (isFailed(i)) btn.classList.add("done-fail");
    if (i === current) btn.classList.add("current");
    btn.addEventListener("click", function () { goJudge(i); });
    box.appendChild(btn);
  });
}

/* ---------- 判纸（单问卡片） ---------- */
function renderJudge() {
  const p = PRINCIPLES[current];
  const a = answers[current];
  const card = document.getElementById("judge-card");

  const top = document.createElement("div");
  top.className = "judge-top";
  top.innerHTML =
    '<span class="judge-num">原则 ' + p.num + '</span>' +
    '<span class="judge-name">' + p.name + '</span>' +
    '<span class="layer-chip">' + p.layer + '</span>';

  const qlabel = document.createElement("p");
  qlabel.className = "judge-qlabel";
  qlabel.textContent = "判 据";

  const q = document.createElement("p");
  q.className = "judge-question";
  q.textContent = p.q;

  const rule = document.createElement("div");
  rule.className = "judge-rule";

  const row = document.createElement("div");
  row.className = "answer-row";
  const opts = [
    { key: "pass", label: "是 · 已过", note: "本判成立" },
    { key: "fail", label: "否 · 未过", note: "本判未过" },
    { key: "unsure", label: "说不清", note: "先存疑，按动作澄清" }
  ];
  opts.forEach(function (o) {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "btn btn-seal";
    b.innerHTML = o.label + "<small>" + o.note + "</small>";
    if (a === o.key) b.classList.add(o.key === "pass" ? "sel-pass" : "sel-" + o.key);
    b.addEventListener("click", function () {
      answers[current] = o.key;
      saveState();
      renderJudge();
      renderProgress();
      enableNext();
    });
    row.appendChild(b);
  });

  // 反例（可展开）
  const toggle = document.createElement("button");
  toggle.type = "button";
  toggle.className = "counter-toggle";
  toggle.textContent = "▸ 看反例";
  const body = document.createElement("div");
  body.className = "counter-body";
  body.innerHTML = '<span class="label">反例</span>' + escapeHtml(p.counter);

  const showBody = function () {
    body.classList.add("show");
    toggle.textContent = "▾ 收起反例";
  };
  const hideBody = function () {
    body.classList.remove("show");
    toggle.textContent = "▸ 看反例";
  };
  toggle.addEventListener("click", function () {
    if (body.classList.contains("show")) hideBody(); else showBody();
  });

  // 答后提示
  const hint = document.createElement("p");
  hint.className = "judge-hint";
  if (a === "pass") {
    hint.classList.add("show", "pass-hint");
    hint.innerHTML = "<strong>已过</strong>——本判成立，继续下一问。";
  } else if (a === "fail" || a === "unsure") {
    hint.classList.add("show");
    const note = a === "unsure"
      ? "存疑视同未过——先按动作澄清，再回来重判。"
      : "未过——这一条需要建设，动作就在判状里。";
    hint.innerHTML = "<strong>未过 · " + p.t + "</strong>" + escapeHtml(p.action) + "　" + note;
  }

  card.innerHTML = "";
  card.appendChild(top);
  card.appendChild(qlabel);
  card.appendChild(q);
  card.appendChild(rule);
  card.appendChild(row);
  card.appendChild(hint);
  card.appendChild(toggle);
  card.appendChild(body);

  enableNext();
}

function enableNext() {
  const next = document.getElementById("btn-next");
  const answered = answers[current] !== null;
  next.disabled = !answered;
  next.textContent = (current === PRINCIPLES.length - 1) ? "看判状 →" : "下一问 →";
}

/* ---------- 判状（结果） ---------- */
function renderResult() {
  const passed = passedCount();
  document.getElementById("stamp-line1").textContent = "已过";
  document.getElementById("stamp-line2").textContent = passed + " / " + PRINCIPLES.length;

  const list = document.getElementById("layer-list");
  list.innerHTML = "";
  LAYER_ORDER.forEach(function (layer) {
    const idxs = LAYER_INDEX[layer] || [];
    const passedN = idxs.filter(isPassed).length;
    const row = document.createElement("div");
    row.className = "layer-row";

    const head = document.createElement("div");
    head.className = "layer-head";
    const left = document.createElement("div");
    left.innerHTML =
      '<span class="layer-name">' + layer + '</span>' +
      '<span class="layer-ask">　' + LAYER_NOTES[layer] + '</span>';
    const count = document.createElement("span");
    count.className = "layer-count";
    count.textContent = "过 " + passedN + " / " + idxs.length;
    head.appendChild(left);
    head.appendChild(count);

    const items = document.createElement("ul");
    items.className = "layer-items";
    idxs.forEach(function (i) {
      const p = PRINCIPLES[i];
      const li = document.createElement("li");
      const pass = isPassed(i);
      li.className = "layer-item " + (pass ? "pass" : "fail");
      const status = document.createElement("span");
      status.className = "status";
      status.textContent = pass ? "过" : "未过";
      const body = document.createElement("span");
      body.className = "item-body";
      body.innerHTML =
        '<span class="item-name">' + p.num + " · " + p.name + '</span>' +
        (pass
          ? '<span class="item-act">判据成立，保持。</span>'
          : '<span class="item-act"><strong>' + p.t + "</strong>：" + escapeHtml(p.action) + "</span>");
      li.appendChild(status);
      li.appendChild(body);
      items.appendChild(li);
    });

    row.appendChild(head);
    row.appendChild(items);
    list.appendChild(row);
  });

  // 顺序警告：诊断层未全过
  const diagIdx = LAYER_INDEX["诊断层"] || [];
  const diagOk = diagIdx.every(isPassed);
  document.getElementById("order-warn").hidden = diagOk || answeredCount() === 0;
}

/* ---------- 重置 ---------- */
function resetAll() {
  answers = new Array(PRINCIPLES.length).fill(null);
  saveState();
  goJudge(0);
}

/* ---------- 工具 ---------- */
function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

/* ---------- 事件绑定 ---------- */
document.getElementById("btn-start").addEventListener("click", function () { goJudge(0); });
document.getElementById("brand-btn").addEventListener("click", goIntro);
document.getElementById("btn-prev").addEventListener("click", function () {
  goJudge(Math.max(0, current - 1));
});
document.getElementById("btn-next").addEventListener("click", function () {
  if (current >= PRINCIPLES.length - 1) { goResult(); return; }
  goJudge(current + 1);
});
document.getElementById("btn-retry").addEventListener("click", resetAll);
document.getElementById("btn-restart").addEventListener("click", resetAll);
document.getElementById("btn-table").addEventListener("click", goTable);
document.getElementById("btn-back-result").addEventListener("click", goResult);

/* ---------- 键盘：左右方向键翻问 ---------- */
document.addEventListener("keydown", function (e) {
  if (document.getElementById("view-judge").hidden) return;
  if (e.key === "ArrowLeft") {
    const b = document.getElementById("btn-prev");
    if (!b.disabled) goJudge(Math.max(0, current - 1));
  } else if (e.key === "ArrowRight") {
    const b = document.getElementById("btn-next");
    if (!b.disabled) {
      if (current >= PRINCIPLES.length - 1) goResult(); else goJudge(current + 1);
    }
  }
});

/* ---------- 启动：恢复到上次判到的地方 ---------- */
(function boot() {
  const firstOpen = answers.findIndex(function (v) { return v === null; });
  if (firstOpen === -1 && answeredCount() > 0) { goResult(); return; }
  goJudge(firstOpen === -1 ? 0 : firstOpen);
})();
