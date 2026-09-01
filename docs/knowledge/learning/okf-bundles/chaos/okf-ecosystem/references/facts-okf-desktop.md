---
type: Facts
title: "okf-desktop 事实清单"
---

# okf-desktop 事实清单

> R阶段事实采集。源码路径：d:\AI\.chaos\libs\tests\okf-desktop\
> 采集日期：2026-08-23

## 项目元信息

- F-001: package.json 中 `name` 值为 `"okf-desktop-ui"`，`private` 为 true，`version` 值为 `"0.1.0"` — 源码：`ui/package.json:2-4`
- F-002: package.json 中 `type` 值为 `"module"` — 源码：`ui/package.json:5`
- F-003: package.json 中 `license` 值为 `"AGPL-3.0-only"`，`author` 值为 `"Vinod Borole"` — 源码：`ui/package.json:23-24`
- F-004: shell/requirements.txt 声明依赖 `okf-kit[serve,chat]>=0.3.3` 和 `pywebview>=5.0` — 源码：`shell/requirements.txt:2-3`
- F-005: README 声明许可证为 AGPL-3.0 — 源码：`README.md:8,144`
- F-006: README 声明支持平台为 Linux、macOS、Windows — 源码：`README.md:6`
- F-007: README 说明 UI 不包含 okf-kit 逻辑，UI 是纯 React 通过 okf-kit 本地 API（`okf serve`）通信 — 源码：`README.md:19-21`

## 桌面应用架构

- F-010: `shell/app.py` 模块文档字符串说明：在后台线程中进程内运行 okf-kit 本地 API（`okf serve`），然后打开原生窗口指向该 API — 源码：`shell/app.py:1-9`
- F-011: 函数 `_bundle_root() -> pathlib.Path`，`getattr(sys, "frozen", False)` 为真时返回 `pathlib.Path(sys._MEIPASS)`，否则返回 `pathlib.Path(__file__).resolve().parent.parent` — 源码：`shell/app.py:24-28`
- F-012: 模块级变量 `UI_DIST = _bundle_root() / "ui" / "dist"` — 源码：`shell/app.py:31`
- F-013: 类 `Api`，文档字符串说明为 `window.pywebview.api`，包含方法 `open_external(self, url)` — 源码：`shell/app.py:34-41`
- F-014: `Api.open_external` 方法判断 url 为字符串且以 `http://` 或 `https://` 开头时调用 `webbrowser.open(url)`，返回 True — 源码：`shell/app.py:38-41`
- F-015: 函数 `_free_port() -> int` 创建 socket 绑定 `("127.0.0.1", 0)`，获取端口后关闭 socket — 源码：`shell/app.py:44-49`
- F-016: 函数 `start_server(ui_dir: pathlib.Path) -> tuple[str, str]` 延迟导入 uvicorn 和 `okf_kit.serve.app.create_app` — 源码：`shell/app.py:52-56`
- F-017: `start_server` 生成 token 为 `secrets.token_hex(16)`，调用 `_free_port()` 获取端口，调用 `create_app(token, ui_dir=str(ui_dir))` 创建 ASGI app — 源码：`shell/app.py:58-60`
- F-018: `start_server` 创建 `uvicorn.Config`，参数 `host="127.0.0.1"`、`port=port`、`log_level="warning"`、`loop="asyncio"`、`http="h11"`、`ws="none"` — 源码：`shell/app.py:62-63`
- F-019: `start_server` 在 daemon 线程中启动 `uvicorn.Server(config).run` — 源码：`shell/app.py:64-66`
- F-020: `start_server` 最多重试 200 次，每次间隔 0.05 秒，通过 `socket.create_connection(("127.0.0.1", port), timeout=0.2)` 等待服务就绪 — 源码：`shell/app.py:69-74`
- F-021: `start_server` 返回 `(f"http://127.0.0.1:{port}", token)` — 源码：`shell/app.py:75`
- F-022: 函数 `main() -> int` 延迟导入 `webview`（pywebview），导入失败时退出并提示安装 `shell/requirements.txt` — 源码：`shell/app.py:78-82`
- F-023: `main` 检查 `UI_DIST / "index.html"` 是否存在，不存在时退出并提示构建 UI — 源码：`shell/app.py:84-85`
- F-024: `main` 调用 `start_server(UI_DIST)` 获取 `(base, token)` — 源码：`shell/app.py:87`
- F-025: `main` 设置 `webview.settings["OPEN_EXTERNAL_LINKS_IN_BROWSER"] = True` — 源码：`shell/app.py:89`
- F-026: `main` 调用 `webview.create_window("okf desktop", f"{base}/?token={token}", js_api=Api(), text_select=True, width=1200, height=820, min_size=(940, 620))` — 源码：`shell/app.py:90-91`
- F-027: `main` 调用 `webview.start(debug=bool(os.environ.get("OKF_DEBUG")))` — 源码：`shell/app.py:92`
- F-028: 模块入口 `if __name__ == "__main__": raise SystemExit(main())` — 源码：`shell/app.py:96-97`
- F-029: README 中的架构图描述：pywebview window → React UI → fetch/SSE → okf serve (okf-kit) → ~/.okf + OS keychain — 源码：`README.md:62-65`
- F-030: README 说明 `okf serve` 在 `/` 托管构建后的 UI，在 `/api` 提供 API，为单源无 CORS；shell 通过 `?token=` 传递 bearer token — 源码：`README.md:67-68`

## shell/app.py 的 API 端点调用

- F-040: `shell/app.py` 不直接定义 HTTP 端点，而是调用 `okf_kit.serve.app.create_app(token, ui_dir=str(ui_dir))` 创建完整的 FastAPI 应用 — 源码：`shell/app.py:56,60`
- F-041: `shell/app.py` 中 uvicorn 配置使用 `loop="asyncio"`、`http="h11"`、`ws="none"`，注释说明此举使冻结包避开 uvloop/httptools/websockets — 源码：`shell/app.py:61-63`
- F-042: `shell/app.py` 中进程内运行（而非子进程），注释说明这使得整个应用可冻结为单个 PyInstaller 二进制 — 源码：`shell/app.py:4-6`

## ui/src/api.js 的前端 API 调用

- F-050: 文件开头从 URL 查询参数读取 `base` 和 `token`：`const BASE = params.get("base") || ""`、`const TOKEN = params.get("token") || ""` — 源码：`ui/src/api.js:5-7`
- F-051: 常量 `headers` 为 `{ Authorization: \`Bearer ${TOKEN}\`, "Content-Type": "application/json" }` — 源码：`ui/src/api.js:9`
- F-052: 异步函数 `req(path, opts = {})` 调用 `fetch(BASE + path, { ...opts, headers: { ...headers, ...(opts.headers || {}) } })`，非 ok 时抛出 Error，204 状态返回 null，否则返回 `res.json()` — 源码：`ui/src/api.js:11-19`
- F-053: 异步函数 `stream(path, opts, onEvent)` 调用 fetch 获取 Response，使用 `ReadableStream` reader 和 `TextDecoder` 解析 SSE，按 `\n\n` 分块，每行解析 `event: ` 和 `data: ` 前缀，调用 `onEvent(ev, data)` — 源码：`ui/src/api.js:22-42`
- F-054: 导出对象 `api` 的方法：
  - `status: () => req("/api/status")` — 源码：`ui/src/api.js:45`
  - `health: () => req("/api/health")` — 源码：`ui/src/api.js:46`
  - `registry: () => req("/api/registry")` — 源码：`ui/src/api.js:48`
  - `books: () => req("/api/books")` — 源码：`ui/src/api.js:49`
  - `book: (name) => req(\`/api/books/${name}\`)` — 源码：`ui/src/api.js:50`
  - `removeBook: (name) => req(\`/api/books/${name}\`, { method: "DELETE" })` — 源码：`ui/src/api.js:51`
  - `install: (name, onEvent) => stream(\`/api/books/${name}/install\`, { method: "POST" }, onEvent)` — 源码：`ui/src/api.js:52`
  - `toc: (name) => req(\`/api/books/${name}/toc\`)` — 源码：`ui/src/api.js:54`
  - `concept: (name, id) => req(\`/api/books/${name}/concept?id=${encodeURIComponent(id)}\`)` — 源码：`ui/src/api.js:55`
  - `chats: (name) => req(\`/api/books/${name}/chats\`)` — 源码：`ui/src/api.js:57`
  - `newChat: (name) => req(\`/api/books/${name}/chats\`, { method: "POST" })` — 源码：`ui/src/api.js:58`
  - `chat: (name, sid) => req(\`/api/books/${name}/chats/${sid}\`)` — 源码：`ui/src/api.js:59`
  - `delChat: (name, sid) => req(\`/api/books/${name}/chats/${sid}\`, { method: "DELETE" })` — 源码：`ui/src/api.js:60`
  - `ask: (name, sid, question, onEvent) => stream(\`/api/books/${name}/chats/${sid}/ask\`, { method: "POST", body: JSON.stringify({ question }) }, onEvent)` — 源码：`ui/src/api.js:61-62`
  - `settings: () => req("/api/settings")` — 源码：`ui/src/api.js:64`
  - `saveSettings: (body) => req("/api/settings", { method: "PUT", body: JSON.stringify(body) })` — 源码：`ui/src/api.js:65`
- F-055: 导出函数 `openExternal(url)` 尝试调用 `window.pywebview?.api?.open_external(url)`，成功返回 true，异常时返回 false — 源码：`ui/src/api.js:71-81`
- F-056: 导出函数 `fmtSize(bytes)`，bytes 为假值返回 `"0 KB"`，>=1MB 返回 `"X.X MB"`，否则返回 KB 值 — 源码：`ui/src/api.js:83-87`
- F-057: 导出函数 `ago(iso)`，将 ISO 日期转为相对时间字符串：0 天为 `"today"`，1 天为 `"yesterday"`，N 天为 `"N days ago"` — 源码：`ui/src/api.js:89-93`

## 前端依赖与构建

- F-060: package.json `dependencies` 包含：
  - `@fontsource/ibm-plex-mono: ^5.2.7`
  - `@fontsource/libre-franklin: ^5.2.8`
  - `@fontsource/newsreader: ^5.2.10`
  - `markdown-it: ^14.1.0`
  - `react: ^18.3.1`
  - `react-dom: ^18.3.1`
  — 源码：`ui/package.json:11-18`
- F-061: package.json `devDependencies` 包含 `@vitejs/plugin-react: ^4.3.1` 和 `vite: ^5.4.0` — 源码：`ui/package.json:19-22`
- F-062: npm scripts 定义：`dev: "vite"`、`build: "vite build"`、`preview: "vite preview"` — 源码：`ui/package.json:6-10`
- F-063: README 说明字体（Newsreader / Libre Franklin / IBM Plex Mono）通过 @fontsource 自托管，Vite 将 woff2 打包到 dist，无网络依赖 — 源码：`README.md:131-133`
- F-064: 前端源码目录包含 5 个屏幕组件：`Chat.jsx`、`Discover.jsx`、`Library.jsx`、`Read.jsx`、`Settings.jsx`，以及 `App.jsx`、`api.js`、`links.js`、`main.jsx`、`theme.css` — 源码：`ui/src/` 目录结构

## Electron/PyInstaller 打包方式

- F-070: 构建脚本 `build.sh` 使用 `set -euo pipefail`，切换到脚本所在目录 — 源码：`build.sh:1-5`
- F-071: `build.sh` 第 1 步在 ui 目录执行 `npm install --no-audit --no-fund && npm run build` — 源码：`build.sh:7-8`
- F-072: `build.sh` 第 2 步执行 `python3 -m pip install --quiet --upgrade pyinstaller`，删除 build/dist 目录，执行 `python3 -m PyInstaller okf-desktop.spec --noconfirm --log-level WARN` — 源码：`build.sh:10-13`
- F-073: `build.sh` 第 3 步打包：Linux 执行 `tar -C dist -czf dist/okf-desktop-linux-x64.tar.gz okf-desktop`；macOS 执行 `zip -qry okf-desktop-macos.zip okf-desktop`；其他系统仅提示手动打包 — 源码：`build.sh:15-22`
- F-074: PyInstaller spec 文件 `okf-desktop.spec` 入口脚本为 `shell/app.py`，`pathex=["."]` — 源码：`okf-desktop.spec:44-46`
- F-075: spec 文件 `datas` 包含 `("ui/dist", "ui/dist")` 和 `collect_data_files("webview")` — 源码：`okf-desktop.spec:17-18`
- F-076: spec 文件 `hiddenimports` 包含 `collect_submodules("uvicorn")`、`collect_submodules("keyring")`、`collect_submodules("okf_kit.serve")`、`collect_submodules("openai")` — 源码：`okf-desktop.spec:20-24`
- F-077: spec 文件显式 hiddenimports 包含 `"okf_kit"`、`"okf_kit.serve.app"`、`"okf_kit.chat.agent"`、`"okf_kit.chat.retrieval"`、`"okf_kit.chat.providers"`、`"okf_kit.chat.history"` — 源码：`okf-desktop.spec:25-28`
- F-078: Linux 平台额外 hiddenimports 包含 `"gi"`、`"gi.repository.Gtk"`、`"gi.repository.Gdk"`、`"gi.repository.GLib"`、`"gi.repository.WebKit2"` — 源码：`okf-desktop.spec:29-32`
- F-079: spec 文件 `excludes` 列表包含 `"trafilatura"`、`"selectolax"`、`"lxml"`、`"crawl4ai"`（爬取栈）、`"uvloop"`、`"httptools"`、`"watchfiles"`、`"websockets"`（uvicorn standard extras）、`"botocore"`、`"boto3"`、`"s3transfer"`、`"zstandard"`、`"tkinter"`、`"matplotlib"`、`"numpy"`、`"pandas"`、`"PIL"`、`"scipy"`、`"pytest"`、`"IPython"` — 源码：`okf-desktop.spec:35-40`
- F-080: spec 文件过滤 `a.datas`，排除以 `"share/icons"`、`"share/themes"`、`"share/locale"`、`"share/doc"`、`"share/man"` 开头的路径 — 源码：`okf-desktop.spec:62-63`
- F-081: EXE 配置 `name="okf-desktop"`、`console=False`（GUI 应用无终端窗口）、`upx=False`、`debug=False` — 源码：`okf-desktop.spec:67-80`
- F-082: Windows 平台 EXE 的 `version` 参数为 `"version_info.txt"` — 源码：`okf-desktop.spec:79`
- F-083: COLLECT 配置 `name="okf-desktop"` — 源码：`okf-desktop.spec:82-90`
- F-084: macOS 平台（`sys.platform == "darwin"`）创建 BUNDLE，`name="okf-desktop.app"`、`bundle_identifier="com.vinodborole.okf-desktop"`，info_plist 包含 `NSHighResolutionCapable: True`、`LSApplicationCategoryType: "public.app-category.developer-tools"`、`CFBundleShortVersionString: "0.1.2"` — 源码：`okf-desktop.spec:95-105`
- F-085: README 说明 PyInstaller 不支持交叉编译，需在每个目标 OS 上分别构建 — 源码：`README.md:109`
- F-086: README 说明 Linux 包约 140 MB（主要为 GTK + ICU + Python），使用系统 GTK3 + WebKit2GTK — 源码：`README.md:120-124`
- F-087: README 说明 macOS 使用 WKWebView，Windows 使用 Edge WebView2，冻结更为自包含 — 源码：`README.md:125`
- F-088: README 说明 macOS 和 Windows 构建未签名，macOS 需执行 `xattr -dr com.apple.quarantine` 清除隔离属性；Windows  SmartScreen 需点击"更多信息→仍要运行" — 源码：`README.md:34-51`

## 前端屏幕与 API 对应关系

- F-090: README 中的端点映射表：
  - Library 屏幕使用 `GET /api/books`、`DELETE /api/books/{name}`、`GET /api/status`
  - Discover 屏幕使用 `GET /api/registry`、`POST /api/books/{name}/install`（SSE）
  - Read 屏幕使用 `GET .../toc`、`GET .../concept`（markdown + heading anchors）
  - Chat 屏幕使用 chats CRUD、`POST .../ask`（SSE）
  - Settings 屏幕使用 `GET/PUT /api/settings`
  — 源码：`README.md:98-104`
