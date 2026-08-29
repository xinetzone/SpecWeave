---
id: "okf-desktop-wiki-ui-screens"
title: "03 五大界面详解"
version: "1.0"
source: "ui/src/App.jsx + ui/src/screens/{Library,Discover,Read,Chat,Settings}.jsx"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/01-agent-protocols-interfaces/okf-desktop-wiki/03-ui-screens.toml"
type: "Wiki Tutorial"
description: "okf-desktop 五个屏幕（Library/Discover/Read/Chat/Settings）逐一拆解，含链接分类与引用深链交互"
tags: ["okf-desktop", "ui", "screens", "React", "阅读器", "对话", "引用深链"]
category: "learning"
date: "2026-08-19"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "五个屏幕围绕 api.js 构建：Library 管理本地书库、Discover 从 registry 安装、Read 用 MarkdownIt 渲染并做链接分类、Chat 用 SSE 流式回答并 deep-link 引用、Settings 配置 LLM 与 keychain"
last_verified: "2026-08-19"
wiki_version: "1.0"
okf_version_target: "okf-kit 0.3.3+"
---
# 03 五大界面详解

## 3.0 顶层路由与全局状态（App.jsx）

`App.jsx` 是唯一的路由中枢，用 `useState` 管理 `view`（当前屏幕）、`books`（书库）、`status`（服务状态）、`activeBook`（当前书）、`readTarget`（阅读跳转目标）。侧边栏固定三个导航项：**Library / Discover / Settings**，Read 与 Chat 是"点开某本书后"进入的子视图。

```javascript
function open(name, mode = "read", target = null) {
  setActiveBook(name);
  setReadTarget(target);
  setView(mode);
}
```

`open` 是核心跳转函数：Chat 里点引用会调用 `openRead`，其本质就是 `open(activeBook, "read", { conceptId, anchor })`，把阅读目标传入 Read。

顶部 `Topbar` 显示一个状态"药丸"：`model · online` / `no LLM · offline`，由 `status` 派生。

## 3.1 Library —— 本地书库

**职责**：展示已装 bundle，提供阅读 / 对话 / 更新 / 删除入口。

```javascript
const [busy, setBusy] = useState({});
async function remove(name) { await api.removeBook(name); reload(); }
async function update(name) {           // 重新下载最新版本，原地替换
  setBusy((b) => ({ ...b, [name]: true }));
  try { await api.install(name, () => {}); reload(); }
  finally { setBusy((b) => { const n = { ...b }; delete n[name]; return n; }); }
}
```

每个卡片展示：`tag`（类型）、`pages`（页数）、`title`、`source_url`（去协议）、`size`（`fmtSize`）、`synced_at`（`ago` 友好时间）、`chat_count`。操作按钮：**Read / Chat / Update / Remove**。末尾一张虚线卡 **Add a book** 跳转 Discover。

## 3.2 Discover —— 社区登记中心

**职责**：浏览 registry，一键安装 bundle（带 SSE 进度）。

```javascript
const [entries, setEntries] = useState(null);
const [busy, setBusy] = useState({});   // name -> phase
async function install(name) {
  setBusy((b) => ({ ...b, [name]: "downloading" }));
  try {
    await api.install(name, (ev, data) => {
      if (ev === "progress") setBusy((b) => ({ ...b, [name]: data.phase }));
    });
    await load(); onChange?.();
  } finally { setBusy((b) => { const n = { ...b }; delete n[name]; return n; }); }
}
```

`install` 的 SSE 回调监听 `progress` 事件，`data.phase`（如 downloading / extracting / done）实时更新按钮文案。列表支持本地关键字过滤（title + name + description）。每个条目根据状态显示 `get`（未装）或 `✓ installed` + `update`（已装）。

## 3.3 Read —— 书式阅读器

**职责**：渲染 bundle 的 Markdown 正文，提供 TOC 导航、标题锚点、链接分类、前后翻页。这是最复杂的屏幕。

### 渲染管线

1. `api.toc(name)` 拉取 TOC 树，`flattenConcepts` 拍平成有序概念列表（用于编号与默认首章）
2. `api.concept(name, cid)` 拉取当前概念，`MarkdownIt` 渲染为 HTML（`html: false`，禁原始 HTML，防 XSS）
3. 渲染后 effect 做三件事：给 `h1-h4` 赋 `id`（用 `slug`）、把 `<a>` 分类、滚动到锚点

### 链接三分法（onProseClick + 渲染期分类）

渲染后，每个链接被赋予 `data-kind`：

| kind | 判定 | 行为 |
|------|------|------|
| `anchor` | `href` 以 `#` 开头 | 应用内滚动到标题 |
| `concept` | 归一化 URL 命中 resource map | 应用内跳转到另一个概念（可带 fragment） |
| `external` | 其余 http(s) | 交给操作系统浏览器 |

```javascript
function onProseClick(e) {
  const a = e.target.closest("a");
  if (!a) return;
  const kind = a.dataset.kind;
  if (kind === "anchor")  { e.preventDefault(); scrollToId(a.dataset.anchor); return; }
  if (kind === "concept") {
    e.preventDefault();
    const t = a.dataset.cid, frag = a.dataset.frag || null;
    if (t === cid) scrollToId(frag);
    else { setJump({ conceptId: t, anchor: frag }); setCid(t); }
    return;
  }
  if (kind === "external") { if (openExternal(a.getAttribute("href"))) e.preventDefault(); }
}
```

`openExternal` 优先走 pywebview 桥（`window.pywebview.api.open_external`，在系统浏览器可靠打开），失败则回退到原生 `target=_blank`。

### MarkdownIt 安全配置

```javascript
const md = new MarkdownIt({ html: false, linkify: true, breaks: false });
md.renderer.rules.link_open = (tokens, idx, opts, env, self) => {
  const href = tokens[idx].attrGet("href") || "";
  if (/^https?:\/\//i.test(href)) {           // 绝对链接预加 _blank + noopener
    tokens[idx].attrSet("target", "_blank");
    tokens[idx].attrSet("rel", "noopener noreferrer");
  }
  return self.renderToken(tokens, idx, opts);
};
```

`html: false` 关键——正文来自外部 bundle，禁用内联 HTML 防止脚本注入。

## 3.4 Chat —— 引用式对话

**职责**：管理会话、流式问答、引用 chips 深链回 Read。

### 会话管理

启动时 `api.chats(name)` 拉取会话列表，有则选中第一条，无则 `newChat()` 新建。`selectSession(id)` 加载历史消息，`newChat()` 创建一个空会话。

### 流式问答（SSE）

```javascript
async function send() {
  const q = input.trim();
  if (!q || busy) return;
  setInput(""); setBusy(true);
  setMessages((m) => [...m, { role: "user", text: q }, { role: "assistant", text: "", sources: [] }]);
  try {
    await api.ask(name, sid, q, (ev, data) => {
      if (ev === "token")   setMessages((m) => bumpLast(m, (b) => ({ ...b, text: b.text + data.text })));
      else if (ev === "sources") setMessages((m) => bumpLast(m, (b) => ({ ...b, sources: data.sources })));
    });
  } catch (e) {
    setMessages((m) => bumpLast(m, (b) => ({ ...b, text: b.text || `⚠ ${e.message}` })));
  } finally { setBusy(false); loadSessions(); }
}
```

- `token` 事件：追加回答文本（实现 token 级打字机效果）
- `sources` 事件：一次性注入引用列表
- 错误兜底：把错误信息渲染进气泡

### 引用深链

底部渲染引用 chips（`📖 section`），点击调用 `openRead(s.concept_id, s.anchor)`，跳回 Read 并滚动到对应锚点。答案正文里的链接也经 `onAnswerClick` 分类：命中 resource map 则应用内打开，否则走系统浏览器。

```javascript
function onAnswerClick(e) {
  const a = e.target.closest("a");
  if (!a) return;
  const href = a.getAttribute("href");
  if (!href) return;
  const hit = resourceMap.get(normUrl(href));
  if (hit) { e.preventDefault(); openRead(hit, frag); return; }
  if (openExternal(href)) e.preventDefault();
}
```

## 3.5 Settings —— LLM 配置

**职责**：切换 LLM provider、配置 model、存储 API key。

```javascript
const PROVIDERS = [
  { id: "none",   name: "No LLM",            desc: "Zero-key retrieval. Cited answers, no network." },
  { id: "ollama", name: "Ollama",            desc: "Local models, fully offline chat." },
  { id: "openai", name: "OpenAI-compatible", desc: "Any hosted API with a key." },
];
```

- `needsKey = s.provider === "openai"`：仅 OpenAI 兼容 provider 需要 API key
- `showModel = s.provider !== "none"`：非 No LLM 才显示 model 输入框
- API key 存储说明明确写着 **"Key is stored in your OS keychain, never in the bundle"**
- 保存走 `PUT /api/settings`，key 字段通过 `has_key` 显示为 `•••••••• (saved)`

## 3.6 设计系统（theme.css）

视觉延续了 okf 生态的"松绿 + 暖纸"风格：

- **字体**：Newsreader（衬线，正文/标题）、Libre Franklin（无衬线，UI）、IBM Plex Mono（等宽，标签/代码）
- **配色**：`--green: #2e6b4e`、`--paper: #f6f3ec`、`--ink: #211d15`
- **可选中性**：chrome 元素（侧栏/顶栏/按钮）`user-select: none`，阅读内容（`.prose`）`user-select: text`——桌面应用该有的"原生手感"

字体全部经 `@fontsource` 自托管，Vite 打包为 woff2 进 `dist`，无网络依赖，完全离线。

---

| 上一章 | 目录 | 下一章 |
|--------|------|--------|
| [02 安装与快速入门](02-quickstart.md) | [README](README.md) | [04 API 与数据流](04-api-and-data-flow.md) |