---
type: Reference
title: okf-desktop 源码
description: okf-desktop 0.1.0 桌面应用源码登记，包含 shell、UI、打包配置与跨平台信息
tags: [okf, okf-desktop, source, reference, pywebview]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: pending, at: pending }
status: draft
stale_after: 2027-08-23
sources:
  - id: facts-okf-desktop
    resource: "/references/facts-okf-desktop.md"
    title: okf-desktop 事实清单
---

# okf-desktop 源码

## 仓库信息

| 属性 | 值 |
|------|-----|
| 包名（UI） | `okf-desktop-ui` |
| 版本 | `0.1.0` |
| 许可证 | AGPL-3.0-only |
| 作者 | Vinod Borole |
| 支持平台 | Linux、macOS、Windows |
| UI 类型 | `module`（ESM） |
| 核心依赖 | `okf-kit[serve,chat]>=0.3.3`、`pywebview>=5.0` |

## 架构概要

okf-desktop 是 okf-kit 的桌面阅读器/聊天器。它在后台线程中进程内运行 `okf serve`（FastAPI + uvicorn），然后用 pywebview 创建原生窗口指向该 API。UI 是纯 React 单页应用，通过 fetch/SSE 与同源 API 通信，不含任何 okf-kit 业务逻辑。

架构链路：

```text
pywebview window → React UI → fetch/SSE → okf serve (okf-kit) → ~/.okf + OS keychain
```

## 关键源文件清单

源码根路径：`d:\AI\.chaos\libs\tests\okf-desktop\`

### Python Shell（`shell/`）

| 文件路径 | 职责 |
|---------|------|
| `shell/app.py` | 桌面主程序：`Api` 类、`start_server`、`main`，约 100 行 |
| `shell/requirements.txt` | Python 依赖：`okf-kit[serve,chat]>=0.3.3`、`pywebview>=5.0` |

### 前端 UI（`ui/`）

| 文件路径 | 职责 |
|---------|------|
| `ui/package.json` | npm 包定义，React 18 + Vite 5 + markdown-it |
| `ui/index.html` | HTML 入口 |
| `ui/vite.config.js` | Vite 构建配置 |
| `ui/src/main.jsx` | React 应用入口 |
| `ui/src/App.jsx` | 根组件，屏幕路由 |
| `ui/src/api.js` | API 客户端：fetch 封装、SSE 流式解析、token 处理 |
| `ui/src/links.js` | 链接处理工具 |
| `ui/src/theme.css` | 全局样式与主题 |

### 前端屏幕组件（`ui/src/screens/`）

| 文件路径 | 对应 API | 功能 |
|---------|---------|------|
| `ui/src/screens/Library.jsx` | `GET /api/books`、`DELETE /api/books/{name}`、`GET /api/status` | 本地 bundle 库管理 |
| `ui/src/screens/Discover.jsx` | `GET /api/registry`、`POST /api/books/{name}/install`（SSE） | 远程注册表浏览与安装 |
| `ui/src/screens/Read.jsx` | `GET .../toc`、`GET .../concept` | Markdown 阅读、目录导航、heading 锚点 |
| `ui/src/screens/Chat.jsx` | chats CRUD、`POST .../ask`（SSE） | 对话界面 |
| `ui/src/screens/Settings.jsx` | `GET/PUT /api/settings` | Provider/模型/API key 配置 |

### 前端依赖

**运行时依赖**：
- `react@^18.3.1`、`react-dom@^18.3.1`
- `markdown-it@^14.1.0`（Markdown 渲染）
- `@fontsource/ibm-plex-mono@^5.2.7`、`@fontsource/libre-franklin@^5.2.8`、`@fontsource/newsreader@^5.2.10`（自托管字体）

**开发依赖**：
- `vite@^5.4.0`、`@vitejs/plugin-react@^4.3.1`

**npm scripts**：`dev`（vite）、`build`（vite build）、`preview`（vite preview）

### 打包配置

| 文件路径 | 职责 |
|---------|------|
| `okf-desktop.spec` | PyInstaller spec 文件，定义入口、datas、hiddenimports、excludes |
| `build.sh` | 构建脚本：npm build → PyInstaller → 平台打包 |
| `version_info.txt` | Windows EXE 版本信息资源 |

### PyInstaller Spec 要点

- **入口脚本**：`shell/app.py`
- **数据文件**：`ui/dist`（React 构建产物）、`collect_data_files("webview")`
- **hiddenimports**：uvicorn、keyring、okf_kit.serve、okf_kit.chat.* 子模块、openai；Linux 额外包含 gi/GTK/WebKit2
- **excludes**：爬取栈（trafilatura、selectolax、lxml、crawl4ai）、uvicorn 高性能 extras（uvloop、httptools、watchfiles、websockets）、重型科学计算库（numpy、pandas、scipy、PIL、matplotlib）、tkinter
- **uvicorn 配置**：`loop="asyncio"`、`http="h11"`、`ws="none"`（冻结兼容性）
- **EXE**：`console=False`（GUI 模式）、`upx=False`
- **macOS BUNDLE**：`okf-desktop.app`，bundle identifier `com.vinodborole.okf-desktop`

### 跨平台差异

| 平台 | WebView 引擎 | 包大小 | 备注 |
|------|-------------|--------|------|
| Linux | GTK3 + WebKit2GTK | ~140 MB | 依赖系统 GTK3 |
| macOS | WKWebView | 较自包含 | 需 `xattr -dr com.apple.quarantine` 清除隔离 |
| Windows | Edge WebView2 | 较自包含 | SmartScreen 需手动确认运行 |

PyInstaller 不支持交叉编译，需在每个目标 OS 上分别构建。

### 项目根文件

| 文件路径 | 职责 |
|---------|------|
| `README.md` | 项目说明、架构图、端点映射表、构建指南 |
| `LICENSE` | AGPL-3.0 许可证全文 |
| `build.sh` | 一键构建脚本 |
| `assets/demo.gif` | 演示动画 |
| `assets/social-preview.png` | 社交分享预览图 |
