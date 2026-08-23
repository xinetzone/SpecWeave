---
type: Concept
title: 桌面应用同进程架构与打包
description: okf-desktop 使用 pywebview 原生窗口与进程内 uvicorn 服务的同进程单体架构，涵盖 token 传递、PyInstaller 打包配置与跨平台差异
tags: [okf, okf-desktop, pywebview, uvicorn, pyinstaller, cross-platform, same-process]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: okf-desktop-source
    resource: "/references/okf-desktop-source.md"
    title: okf-desktop 源码
  - id: okf-kit-source
    resource: "/references/okf-kit-source.md"
    title: okf-kit 源码
  - id: facts-okf-kit
    resource: "/references/facts-okf-kit.md"
    title: okf-kit 事实清单
---

# 桌面应用同进程架构与打包

okf-desktop 是 okf-kit 的桌面阅读器与聊天客户端。它没有采用 Electron 式的多进程分离架构，而是使用 pywebview 创建原生窗口，在同一进程的 daemon 线程中运行 uvicorn ASGI 服务器。FastAPI 应用既在 `/api` 提供 JSON API，又在 `/` 托管 React 构建产物，实现「单源无 CORS」。整个应用通过 PyInstaller 冻结为单个可执行文件，且刻意排除爬取栈以保持精简。

## 架构总览

桌面应用的架构链路为 [DF-029]：

```text
pywebview window
    │
    ├── React UI (5 个屏幕组件)
    │       │
    │       └── fetch / SSE (同源，无 CORS)
    │
    └── okf serve (FastAPI + uvicorn，进程内 daemon 线程)
            │
            ├── ~/.okf/bundles/  (bundle 数据)
            ├── ~/.okf/chats/    (对话历史)
            └── OS keychain      (API 密钥)
```

`shell/app.py` 的模块文档字符串明确说明：在后台线程中进程内运行 okf-kit 本地 API（`okf serve`），然后打开原生窗口指向该 API [DF-010]。注释进一步指出，进程内运行（而非子进程）使得整个应用可冻结为单个 PyInstaller 二进制 [DF-042]。

UI 是纯 React 单页应用，不包含任何 okf-kit 业务逻辑，通过 okf-kit 本地 API 通信 [DF-007]。这意味着前端代码在浏览器和桌面中完全一致——桌面只是多了一层原生窗口壳。

## 核心组件

### Api 类

`Api` 类暴露给 pywebview 的 JavaScript 桥接（`window.pywebview.api`）[DF-013]，目前仅包含一个方法：

```python
class Api:
    def open_external(self, url):
        if isinstance(url, str) and url.startswith(("http://", "https://")):
            webbrowser.open(url)
        return True
```

`open_external` 用于在系统默认浏览器中打开外部链接，仅允许 http/https 协议 [DF-014]。前端通过 `window.pywebview.api.open_external(url)` 调用 [DF-055]。

### start_server 函数

`start_server(ui_dir)` 负责在进程内启动 HTTP 服务 [DF-016]，返回 `(base_url, token)` 元组。其流程：

1. 生成 token：`secrets.token_hex(16)` [DF-017]
2. 获取空闲端口：`_free_port()` 创建 socket 绑定 `("127.0.0.1", 0)`，获取端口后关闭 [DF-015]
3. 创建 ASGI app：延迟导入 `okf_kit.serve.app.create_app`，调用 `create_app(token, ui_dir=str(ui_dir))` [DF-016][DF-017]
4. 配置 uvicorn [DF-018]：
   ```python
   config = uvicorn.Config(
       app, host="127.0.0.1", port=port,
       log_level="warning",
       loop="asyncio", http="h11", ws="none"
   )
   ```
5. 在 daemon 线程中启动 `uvicorn.Server(config).run()` [DF-019]
6. 轮询等待就绪：最多重试 200 次，每次间隔 0.05 秒，通过 `socket.create_connection(("127.0.0.1", port), timeout=0.2)` 检测 [DF-020]
7. 返回 `(f"http://127.0.0.1:{port}", token)` [DF-021]

uvicorn 配置中 `loop="asyncio"`、`http="h11"`、`ws="none"` 是刻意选择 [DF-041]。注释说明此举使冻结包避开 uvloop、httptools、websockets 等带 C 扩展或二进制依赖的库，这些库在 PyInstaller 冻结时容易出问题。

### main 函数

`main()` 是桌面应用入口 [DF-022]：

1. 延迟导入 `webview`（pywebview），失败时退出并提示安装 `shell/requirements.txt`
2. 检查 `UI_DIST / "index.html"` 是否存在，不存在时提示构建 UI [DF-023]
3. 调用 `start_server(UI_DIST)` 获取 `(base, token)` [DF-024]
4. 设置 `webview.settings["OPEN_EXTERNAL_LINKS_IN_BROWSER"] = True` [DF-025]
5. 创建窗口 [DF-026]：
   ```python
   webview.create_window(
       "okf desktop",
       f"{base}/?token={token}",
       js_api=Api(),
       text_select=True,
       width=1200, height=820,
       min_size=(940, 620)
   )
   ```
6. 启动 pywebview 事件循环：`webview.start(debug=bool(os.environ.get("OKF_DEBUG")))` [DF-027]

模块入口为 `if __name__ == "__main__": raise SystemExit(main())` [DF-028]。

### 资源路径解析

`_bundle_root()` 函数处理开发环境与冻结环境的路径差异 [DF-011]：

```python
def _bundle_root() -> pathlib.Path:
    if getattr(sys, "frozen", False):
        return pathlib.Path(sys._MEIPASS)
    return pathlib.Path(__file__).resolve().parent.parent
```

PyInstaller 冻结时 `sys.frozen` 为 True，资源解压到 `sys._MEIPASS` 临时目录；开发环境则使用源码根目录。`UI_DIST` 常量为 `_bundle_root() / "ui" / "dist"` [DF-012]。

## Token 传递与鉴权

桌面端的鉴权机制与 HTTP 模式完全一致，利用了同源架构的便利性 [DF-030]：

1. `start_server` 生成随机 token
2. 窗口 URL 为 `http://127.0.0.1:{port}/?token={token}`，token 通过查询参数传入
3. 前端 `api.js` 从 URL 查询参数读取 token：`const TOKEN = params.get("token") || ""` [DF-050]
4. 所有 API 请求携带 `Authorization: Bearer ${TOKEN}` 头 [DF-051]
5. 后端 `require_token()` 中间件从 Authorization 头或 token 查询参数获取并验证（使用 `hmac.compare_digest`）[F-174]

这种设计无需 CORS 配置（UI 和 API 同源），也无需复杂的 OAuth 流程。token 绑定到 `127.0.0.1`，外部网络无法访问。

## 前端架构

### API 客户端

`ui/src/api.js` 是前端与后端通信的唯一桥梁 [DF-052][DF-053]：

- `req(path, opts)`：封装 fetch，自动注入 Bearer 头，处理 204/错误/JSON 解析
- `stream(path, opts, onEvent)`：SSE 流式解析，使用 ReadableStream reader 和 TextDecoder，按 `\n\n` 分块，解析 `event: ` 和 `data: ` 前缀

导出的 `api` 对象覆盖所有后端端点 [DF-054]，包括：
- 书籍管理：`books()`、`book(name)`、`removeBook(name)`、`install(name, onEvent)`
- 阅读：`toc(name)`、`concept(name, id)`
- 对话：`chats(name)`、`newChat(name)`、`chat(name, sid)`、`delChat(name, sid)`、`ask(name, sid, question, onEvent)`
- 设置：`settings()`、`saveSettings(body)`
- 系统：`status()`、`health()`、`registry()`

工具函数包括 `openExternal(url)`（pywebview 桥接）、`fmtSize(bytes)`（文件大小格式化）、`ago(iso)`（相对时间）[DF-055][DF-056][DF-057]。

### 五个屏幕组件

前端包含 5 个屏幕组件，与 API 端点一一对应 [DF-064][DF-090]：

| 屏幕 | API 端点 | 功能 |
|------|---------|------|
| Library | `GET /api/books`、`DELETE /api/books/{name}`、`GET /api/status` | 本地 bundle 库管理与删除 |
| Discover | `GET /api/registry`、`POST /api/books/{name}/install`（SSE） | 远程注册表浏览与安装进度 |
| Read | `GET .../toc`、`GET .../concept` | Markdown 阅读、目录树、heading 锚点 |
| Chat | chats CRUD、`POST .../ask`（SSE） | 流式对话界面 |
| Settings | `GET/PUT /api/settings` | Provider/模型/API key 配置 |

### 技术栈与构建

- **框架**：React 18.3 + Vite 5.4 [DF-060][DF-061]
- **Markdown 渲染**：markdown-it 14.1
- **字体**：Newsreader、Libre Franklin、IBM Plex Mono 通过 @fontsource 自托管，Vite 将 woff2 打包到 dist，无网络依赖 [DF-063]
- **npm scripts**：`dev`（vite 开发服务器）、`build`（vite build）、`preview`（vite preview）[DF-062]

## 进程生命周期

桌面应用有两层进程生命周期保障：

1. **父进程监控**：okf-kit serve 的 `_watch_parent(pid)` 启动 daemon 线程，每 2 秒用 `os.kill(pid, 0)` 检测父进程，失败时 `os._exit(0)` [F-207]。桌面 shell 可通过 `--parent-pid` 参数传入自身 PID（不过当前 shell/app.py 未显式传此参数，而是进程内直接运行）。
2. **关闭端点**：`POST /api/shutdown` 使用 `threading.Timer(0.2, lambda: os._exit(0))` 延迟退出 [F-191]，给 HTTP 响应留出发送时间。

由于 uvicorn 运行在 daemon 线程中，主线程（pywebview 事件循环）退出时 daemon 线程自动终止，无需显式清理。

## PyInstaller 打包

### 构建流程

`build.sh` 执行三步构建 [DF-070][DF-071][DF-072][DF-073]：

1. **UI 构建**：在 ui 目录执行 `npm install --no-audit --no-fund && npm run build`
2. **Python 打包**：安装 PyInstaller，清理 build/dist，执行 `python3 -m PyInstaller okf-desktop.spec --noconfirm --log-level WARN`
3. **平台归档**：
   - Linux：`tar -C dist -czf dist/okf-desktop-linux-x64.tar.gz okf-desktop`
   - macOS：`zip -qry okf-desktop-macos.zip okf-desktop`
   - 其他：仅提示手动打包

### Spec 文件配置

`okf-desktop.spec` 的关键配置 [DF-074~DF-083]：

**入口与数据**：
- 入口脚本：`shell/app.py`
- `pathex=["."]`
- `datas`：`("ui/dist", "ui/dist")` 打包 React 构建产物；`collect_data_files("webview")` 收集 pywebview 数据文件

**hiddenimports**（确保冻结后可导入）：
- `collect_submodules("uvicorn")`、`collect_submodules("keyring")`
- `collect_submodules("okf_kit.serve")`、`collect_submodules("openai")`
- 显式列出：`okf_kit`、`okf_kit.serve.app`、`okf_kit.chat.agent`、`okf_kit.chat.retrieval`、`okf_kit.chat.providers`、`okf_kit.chat.history`
- Linux 额外：`gi`、`gi.repository.Gtk`、`gi.repository.Gdk`、`gi.repository.GLib`、`gi.repository.WebKit2`

**excludes**（减小体积、避免冻结问题）：
- 爬取栈：`trafilatura`、`selectolax`、`lxml`、`crawl4ai`
- uvicorn 高性能 extras：`uvloop`、`httptools`、`watchfiles`、`websockets`
- 云 SDK：`botocore`、`boto3`、`s3transfer`
- 科学计算：`numpy`、`pandas`、`scipy`、`PIL`、`matplotlib`
- 其他：`zstandard`、`tkinter`、`pytest`、`IPython`

**数据过滤**：排除以 `share/icons`、`share/themes`、`share/locale`、`share/doc`、`share/man` 开头的路径 [DF-080]，进一步减小体积。

**EXE 配置**：`name="okf-desktop"`、`console=False`（GUI 应用无终端窗口）、`upx=False`、`debug=False` [DF-081]。Windows 平台使用 `version_info.txt` 作为版本资源 [DF-082]。

**macOS BUNDLE** [DF-084]：
- `name="okf-desktop.app"`
- `bundle_identifier="com.vinodborole.okf-desktop"`
- `info_plist` 包含：
  - `NSHighResolutionCapable: True`（Retina 支持）
  - `LSApplicationCategoryType: "public.app-category.developer-tools"`
  - `CFBundleShortVersionString: "0.1.2"`

## 跨平台差异

| 维度 | Linux | macOS | Windows |
|------|-------|-------|---------|
| WebView 引擎 | GTK3 + WebKit2GTK | WKWebView | Edge WebView2 |
| 包大小 | ~140 MB（含 GTK+ICU+Python） | 较自包含 | 较自包含 |
| 系统依赖 | 需安装 GTK3、WebKit2GTK | 无（系统内置 WKWebView） | 需 WebView2 Runtime（Win10/11 通常已内置） |
| 打包格式 | tar.gz | .app zip | 目录（手动打包） |
| 签名 | 未签名 | 未签名 | 未签名 |
| 安全提示 | — | 需 `xattr -dr com.apple.quarantine` 清除隔离 | SmartScreen 需点击"更多信息→仍要运行" |

PyInstaller 不支持交叉编译，需在每个目标 OS 上分别构建 [DF-085]。

Linux 包最大（约 140 MB）主要因为包含 GTK、ICU 和 Python 运行时 [DF-086]。macOS 和 Windows 的 WebView 引擎由系统提供，冻结包更为自包含 [DF-087]。macOS/Windows 构建均未签名，用户首次运行需手动绕过安全提示 [DF-088]。

## 设计要点

桌面端的「同进程单体」架构有几个关键设计决策：

1. **职责物理隔离**：spec 文件排除爬取栈，桌面应用只能阅读和聊天，不能构建 bundle。构建与运行的职责在打包时分离。
2. **代码复用最大化**：shell 仅约 100 行，所有业务逻辑在 `okf_kit.serve` 层。`create_app(token, ui_dir)` 被 CLI serve 和桌面 shell 共同使用。
3. **前端代码同构**：React UI 在浏览器（`okf serve --ui dist/`）和桌面中完全一致，区别仅在于 token 传递方式（URL 参数 vs 命令行输出）。
4. **无 IPC 层**：不使用 Electron 的 IPC、不使用子进程通信、不使用端口协商。uvicorn 在 daemon 线程中运行，函数调用即 API 调用。
5. **无运行时依赖**：冻结后的二进制不依赖系统 Python、Node.js 或其他运行时（Linux 除外，依赖系统 GTK3/WebKit2GTK）。

## 相关概念

- [MCP/Chat/HTTP 三模服务架构](/concepts/04-service-modes.md)
- [OKF 知识包生态概览](/concepts/00-okf-overview.md)
- [CLI 使用示例](/examples/cli-usage.md)
