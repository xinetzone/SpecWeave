---
id: "okf-desktop-wiki-architecture"
title: "01 架构深度解析"
version: "1.0"
source: "shell/app.py + ui/src/api.js + ui/src/links.js + ui/src/App.jsx"
type: "Wiki Tutorial"
description: "okf-desktop 三层架构深度解析：shell 启动器、api.js 唯一集成点、单源无 CORS、token 传递、进程内服务器"
tags: ["okf-desktop", "architecture", "pywebview", "SSE", "单源无CORS", "进程内服务器"]
category: "learning"
date: "2026-08-19"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "okf-desktop 由三层组成：pywebview shell（启动器）、React UI（纯客户端）、okf serve（本地 API）。shell 在进程内线程上启动 okf serve，UI 通过 api.js 唯一集成点以 Bearer token 调用同源 API"
last_verified: "2026-08-19"
wiki_version: "1.0"
okf_version_target: "okf-kit 0.3.3+"
---

# 01 架构深度解析

## 1.1 三层架构总览

okf-desktop 是严格的**三层**结构，每一层的边界都清晰可见：

| 层 | 目录/组件 | 职责 | 是否含业务逻辑 |
|----|-----------|------|----------------|
| **启动器层** | `shell/app.py` | 启动本地服务器、打开原生窗口、桥接外部链接 | 否 |
| **客户端层** | `ui/`（React + Vite） | 渲染 5 个屏幕、管理 UI 状态、发起数据请求 | 否（纯 UI） |
| **服务层** | okf-kit 的 `okf serve` | bundle 读写、registry、检索、对话、设置 | 是（全部逻辑） |

> 业务逻辑 100% 落在 okf-kit 里。okf-desktop 的两层（shell + ui）都是"外壳"，只做展示与转发。这就是「零逻辑客户端」的含义。

## 1.2 启动器层：shell/app.py

shell 用 [pywebview](https://pywebview.flowrl.com/) 创建一个原生窗口，并在后台启动 okf 服务。核心流程在 `main()` 中：

```python
def main() -> int:
    import webview                            # 1. 导入 pywebview
    if not (UI_DIST / "index.html").exists(): # 2. 校验 UI 已构建
        sys.exit("UI not found ... Build it: cd ui && npm install && npm run build")

    base, token = start_server(UI_DIST)       # 3. 进程内启动 okf serve
    webview.settings["OPEN_EXTERNAL_LINKS_IN_BROWSER"] = True
    webview.create_window("okf desktop", f"{base}/?token={token}",
                          js_api=Api(), text_select=True,
                          width=1200, height=820, min_size=(940, 620))
    webview.start()                           # 4. 进入原生窗口事件循环
    return 0
```

几个值得注意的细节：

- **`UI_DIST` 的路径自适应**：`_bundle_root()` 判断 `sys.frozen`。冻结运行时资源在 `sys._MEIPASS` 下，开发时在仓库根目录。这让同一份代码既能开发又能打包。

```python
def _bundle_root() -> pathlib.Path:
    if getattr(sys, "frozen", False):
        return pathlib.Path(sys._MEIPASS)
    return pathlib.Path(__file__).resolve().parent.parent

UI_DIST = _bundle_root() / "ui" / "dist"
```

- **外部链接桥接**：`Api` 类暴露给 JS 的 `open_external(url)` 用 `webbrowser.open` 在用户真实浏览器打开链接，避免引用/外链把应用窗口导航走。这是 pywebview 的 `js_api` 机制——Python 方法对前端暴露为 `window.pywebview.api.*`。

## 1.3 唯一集成点：ui/src/api.js

前端所有后端交互都收敛在 `api.js`，这是 README 明确强调的"唯一集成点"。其余屏幕组件不直接 `fetch`，而是 `import { api } from "../api.js"`。

### Token 与 Base 的注入

```javascript
const params = new URLSearchParams(location.search);
const BASE = params.get("base") || "";   // 生产环境同源，留空即可
const TOKEN = params.get("token") || "";
const headers = { Authorization: `Bearer ${TOKEN}`, "Content-Type": "application/json" };
```

shell 在 URL 里带上 `?token=<十六进制随机串>`，前端据此设置 `Authorization: Bearer`。okf serve 用这个 token 鉴权，防止本机其他进程访问该随机端口。

### 请求封装 `req`

```javascript
async function req(path, opts = {}) {
  const res = await fetch(BASE + path, { ...opts, headers: { ...headers, ...(opts.headers || {}) } });
  if (!res.ok) {
    let msg = res.statusText;
    try { msg = (await res.json()).error?.message || msg; } catch {}
    throw new Error(`${res.status}: ${msg}`);
  }
  return res.status === 204 ? null : res.json();
}
```

统一做三件事：合并鉴权头、解析错误体、把 `204 No Content` 归一为 `null`。

### SSE 流封装 `stream`

安装进度与对话回答都是服务端推送事件（Server-Sent Events）。`stream` 手动解析 SSE 帧：

```javascript
async function stream(path, opts, onEvent) {
  const res = await fetch(BASE + path, { ...opts, headers: { ...headers, ...(opts.headers || {}) } });
  const reader = res.body.getReader();
  const dec = new TextDecoder();
  let buf = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    const blocks = buf.split("\n\n");   // SSE 事件以空行分隔
    buf = blocks.pop();                 // 保留不完整尾部
    for (const block of blocks) {
      let ev = null, data = null;
      for (const line of block.split("\n")) {
        if (line.startsWith("event: ")) ev = line.slice(7);
        else if (line.startsWith("data: ")) data = JSON.parse(line.slice(6));
      }
      if (ev) onEvent(ev, data);        // 按事件名回调
    }
  }
}
```

### API 对象全景

`api` 对象把所有端点组织为语义方法：`status/health/registry/books/book/removeBook/install/toc/concept/chats/newChat/chat/delChat/ask/settings/saveSettings`。其中 `install` 与 `ask` 走 `stream`（SSE），其余走 `req`。

## 1.4 单源无 CORS 设计

okf-desktop 规避跨域问题的办法很巧妙：

```
okf serve 把构建后的 UI 托管在  /
okf serve 把 API 托管在        /api
```

因为静态资源和 API 是**同一个源、同一个端口**，前端的 `fetch("/api/...")` 属于同源请求，根本不会触发 CORS。`okf serve --ui ui/dist` 就是这个作用——让 UI 由后端自己托管。

对比之下，如果 UI 跑在 Vite dev server（`localhost:5173`）而 API 跑在 `localhost:8000`，就必然要处理 CORS。README 也承认"hot reload 需要 okf serve 允许 dev origin（一个待跟进的小改动）"。

## 1.5 进程内服务器：为何能冻结为单文件

`start_server` 是整套架构能否打包成单文件的关键：

```python
def start_server(ui_dir: pathlib.Path) -> tuple[str, str]:
    import uvicorn
    from okf_kit.serve.app import create_app

    token = secrets.token_hex(16)          # 每次启动生成随机 token
    port = _free_port()                     # 随机回环端口
    app = create_app(token, ui_dir=str(ui_dir))
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning",
                            loop="asyncio", http="h11", ws="none")
    server = uvicorn.Server(config)
    threading.Thread(target=server.run, daemon=True).start()  # 后台 daemon 线程

    for _ in range(200):                    # 轮询等待端口就绪
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                break
        except OSError:
            time.sleep(0.05)
    return f"http://127.0.0.1:{port}", token
```

关键点：

1. **线程而非子进程**：用 `threading.Thread` 在进程内跑 uvicorn。子进程无法被 PyInstaller 干净地打包成一个二进制。
2. **约束 uvicorn 选项**：`loop="asyncio"`、`http="h11"`、`ws="none"`，刻意不用 uvloop/httptools/websockets，避免打包进一堆原生二进制（也呼应 spec 里的 excludes）。
3. **随机端口 + 随机 token**：每次启动都不同，降低本机固定端口冲突与安全风险。
4. **就绪轮询**：启动后阻塞等待端口可连接，再返回 URL，避免窗口过早打开白屏。

## 1.6 Token 传递链路

1. `start_server` 生成 `secrets.token_hex(16)`（32 字符十六进制）
2. `create_app(token, ...)` 把 token 注入 okf serve，用于后续请求鉴权
3. shell 把 URL 拼成 `http://127.0.0.1:{port}/?token={token}` 交给 pywebview
4. 前端 `api.js` 从 URL 读取 token，设置 `Authorization: Bearer`
5. 每次 fetch/SSE 都携带该头，服务端校验通过才放行

## 1.7 链接分类与引用深链（预备）

阅读器与对话的一个核心体验是"点击引用直达原文"。这部分依赖 `links.js` 的链接分类算法，在 `04-api-and-data-flow.md` 中会完整展开。这里先给出它依赖的数据结构：

- **概念树（concept tree）**：`GET /toc` 返回树，叶子节点是 concept（`kind === "concept"`，含 `id`、`resource` 原始 URL）。
- **资源映射（resource map）**：`buildResourceMap(toc)` 把「原始 URL 归一化 → concept id」建立 Map。
- **归一化（normUrl）**：剔除协议、query/fragment、尾部斜杠、index.html，得到可比较的 key。

当正文里出现一个链接时，先归一化再查映射：命中即为"书内链接"（应用内跳转），未命中即为"外链"（交给操作系统浏览器）。

---

| 上一章 | 目录 | 下一章 |
|--------|------|--------|
| [00 概述与知识地图](./00-overview.md) | [README](./README.md) | [02 安装与快速入门](./02-quickstart.md) |