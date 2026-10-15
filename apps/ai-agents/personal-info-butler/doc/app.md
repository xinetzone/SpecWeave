---
id: app
html_theme.sidebar_secondary.remove: true
---

# 工作台

下面这一整块就是产品界面：录入、检索、问答、提取、整理、总结都在这一页完成。
顶部横幅会如实告诉你后端的连接状态——**没连上就是没连上**，不会假装在正常工作。

```{raw} html
<div class="butler" id="butler-app">

  <div class="butler-banner is-info" id="butler-banner">
    <strong>正在连接后端…</strong>
  </div>

  <div class="butler-bar">
    <span class="butler-chip" id="status-storage">存储：检测中</span>
    <span class="butler-chip" id="status-llm">模型：检测中</span>
    <span class="butler-bar-spacer"></span>
    <button type="button" class="butler-btn butler-btn-ghost" id="btn-reconnect">重新连接</button>
    <button type="button" class="butler-btn butler-btn-ghost" id="btn-toggle-settings">设置</button>
  </div>

  <section class="butler-panel">
    <h2 class="butler-h">① 随手录入</h2>
    <p class="butler-hint">不用先想清楚类型，写下来就行——自动判定类型、生成标题摘要标签，并从内容里派生待办。</p>
    <textarea id="composer" class="butler-textarea" rows="4"
      placeholder="想到什么就写什么：一个念头、一段摘录、一件要做的事……"></textarea>
    <div class="butler-row">
      <button type="button" class="butler-btn" id="btn-capture">智能入库</button>
      <span class="butler-hint">内容越具体，派生出的待办与关联越准</span>
    </div>
    <div id="capture-result" class="butler-result"></div>
  </section>

  <section class="butler-panel">
    <h2 class="butler-h">② 关键词检索</h2>
    <div class="butler-row">
      <input id="search-input" class="butler-input" type="search" placeholder="输入关键词，回车检索">
      <button type="button" class="butler-btn" id="btn-search">检索</button>
    </div>
    <div class="butler-row butler-filters" id="filter-kind">
      <button type="button" class="butler-tag is-on" data-kind="">全部</button>
      <button type="button" class="butler-tag" data-kind="idea">想法</button>
      <button type="button" class="butler-tag" data-kind="material">资料</button>
      <button type="button" class="butler-tag" data-kind="todo">待办</button>
    </div>
    <div id="item-list" class="butler-list"></div>
  </section>

  <section class="butler-panel">
    <h2 class="butler-h">③ 智能问答</h2>
    <div class="butler-row">
      <input id="ask-input" class="butler-input" type="text" placeholder="就我的记录问我点什么">
      <button type="button" class="butler-btn" id="btn-ask">提问</button>
    </div>
    <div id="ask-result" class="butler-result"></div>
  </section>

  <section class="butler-panel">
    <h2 class="butler-h">④ 重点提取 · 待办整理 · 阶段总结</h2>
    <div class="butler-row">
      <button type="button" class="butler-btn" id="btn-extract">重点信息提取</button>
      <button type="button" class="butler-btn" id="btn-todos">待办整理</button>
      <button type="button" class="butler-btn" id="btn-summary">生成阶段总结</button>
    </div>
    <div id="extract-result" class="butler-result"></div>
    <div id="todos-result" class="butler-result"></div>
    <div id="summary-result" class="butler-result"></div>
  </section>

  <section class="butler-panel" id="llm-card">
    <h2 class="butler-h">大模型（BYOK，可选）</h2>
    <p class="butler-hint">不配也能用：没有密钥时，分类、摘要、关联、问答全部退化为启发式规则，结果依旧可用。
      填上你自己的端点后，这些能力才由模型接管——凭据随请求头发给后端、由后端转给你填的地址，
      后端不落盘、不写日志，也不参与服务端配置。</p>
    <div class="butler-grid">
      <label>Base URL<input id="set-llm-base" class="butler-input" type="text" placeholder="https://api.deepseek.com/v1"></label>
      <label>API Key<input id="set-llm-key" class="butler-input" type="password" placeholder="sk-..." autocomplete="off"></label>
      <label>模型名称<input id="set-llm-model" class="butler-input" type="text" placeholder="deepseek-chat"></label>
    </div>
    <div class="butler-row">
      <button type="button" class="butler-btn" id="btn-llm-test">验证并保存</button>
      <button type="button" class="butler-btn butler-btn-ghost" id="btn-llm-clear">清除模型凭据</button>
      <span class="butler-hint">验证只发一条 1 token 的探针，几乎不花钱</span>
    </div>
    <div id="llm-result" class="butler-result"></div>
  </section>

  <section class="butler-panel" id="settings-panel" hidden>
    <h2 class="butler-h">设置</h2>
    <p class="butler-hint">API 基址填后端<strong>根地址</strong>即可（形如 <code>https://info-butler-api.example.com</code>），
      不要把 <code>/api</code> 后缀写进来。所有内容只保存在本机浏览器的 localStorage，
      随请求头发送给后端，后端不落盘。</p>
    <div class="butler-grid">
      <label>API 基址<input id="set-api-base" class="butler-input" type="text" placeholder="https://your-api.example.com"></label>
      <label>访问令牌 APP_TOKEN<input id="set-token" class="butler-input" type="password" placeholder="后端设置了才需要填"></label>
    </div>
    <div class="butler-row">
      <button type="button" class="butler-btn" id="btn-save-settings">保存并重新连接</button>
      <button type="button" class="butler-btn butler-btn-ghost" id="btn-clear-settings">清除本机设置</button>
    </div>
  </section>

</div>
```

## 界面背后的四个动作

| 动作 | 打到哪个接口 | 没有大模型时会怎样 |
|---|---|---|
| 智能入库 | `POST /api/items` | 启发式判定类型与标签，仍会建立关联 |
| 关键词检索 | `GET /api/items?q=` | 完全不受影响，本来就不走模型 |
| 智能问答 | `POST /api/ask` | 返回相关度最高的原文片段 |
| 重点提取 / 待办整理 / 阶段总结 | `POST /api/extract`、`GET /api/todos`、`POST /api/summary` | 退化为统计直出，结构与有模型时一致 |

## 连不上时先看哪

| 横幅说什么 | 真正的意思 | 你该做什么 |
|---|---|---|
| 还没有连接后端 | 构建时没注入 `BUTLER_API_BASE`，你也没在页面里填 | 点「填写后端地址」，填后端根地址 |
| 请求打到的是一个网页 | 地址指向了静态站，接口不存在 | 基址填后端服务地址，不要带 `/api` |
| 请求没有发出去 | 地址写错 / 后端没起 / 后端没放行跨域 | 本地先 `info-butler serve`，线上检查 `CORS_ORIGINS` |
| 混合内容被拦截 | HTTPS 页面请求了 HTTP 后端 | 后端换成 https 地址 |
| 后端出错了（HTTP 5xx） | 后端收到了请求但内部失败 | 看折叠块里的原始响应，多半是 Supabase 配置 |
