---
id: "okf-desktop-wiki-quickstart"
title: "02 安装与快速入门"
version: "1.0"
source: "README.md（Download/Run it 章节）+ shell/requirements.txt + ui/package.json"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/01-agent-protocols-interfaces/okf-desktop-wiki/02-quickstart.toml"
type: "Wiki Tutorial"
description: "okf-desktop 两种安装方式：下载预构建包 / 从源码构建，三平台启动说明与首次使用流程"
tags: ["okf-desktop", "quickstart", "安装", "预构建", "源码构建", "快速上手"]
category: "learning"
date: "2026-08-19"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "两种方式运行 okf-desktop：直接下载 Releases 预构建包（免 Python/Node），或从源码构建（build UI → 装 shell 依赖 → python shell/app.py）。首次使用流程：Discover 装书 → Read 阅读 → Chat 对话"
last_verified: "2026-08-19"
wiki_version: "1.0"
okf_version_target: "okf-kit 0.3.3+"
---
# 02 安装与快速入门

okf-desktop 提供两种运行方式：**下载预构建包**（零门槛）与**从源码构建**（便于二次开发）。

## 2.1 方式一：下载预构建包

预构建包覆盖 **Linux / macOS / Windows**，无需安装 Python、Node 或 pip，每个平台的包由 CI 在对应平台自动构建。

```bash
# Linux (x64)
tar -xzf okf-desktop-linux-x64.tar.gz && ./okf-desktop/okf-desktop
```

macOS 与 Windows 的构建**未签名**（暂无代码签名证书），首次启动时操作系统会给出警告：

- **macOS**：解压得到 `okf-desktop.app`。由于是下载的未签名应用，Gatekeeper 可能提示"已损坏"。实际上并非损坏，只是隔离标志，清除即可：
  ```bash
  xattr -dr com.apple.quarantine ~/Downloads/okf-desktop.app
  open ~/Downloads/okf-desktop.app
  ```
  （或：**系统设置 → 隐私与安全性 → 仍要打开**。）

- **Windows**：解压运行 `okf-desktop\okf-desktop.exe`；SmartScreen 提示时点 **更多信息 → 仍要运行**。由于 `.exe` 是未签名的 PyInstaller 构建，部分杀软/EDR（如 SentinelOne、Defender）可能误报并隔离它——并非恶意，只是缺少代码签名身份。企业受管机器需 IT 按发布页的 SHA-256 加白，或待签名后按发布者加白。

- **Linux**：需要系统 GTK 3 + WebKit2GTK（绝大多数桌面发行版自带）。

## 2.2 方式二：从源码构建

**前置条件**：Node 18+ 与 Python 3.10+。

### 第 1 步：构建 UI

```bash
cd ui && npm install && npm run build && cd ..
```

### 第 2 步：安装 shell 依赖

```bash
pip install -r shell/requirements.txt
# Linux 额外需要：pip install pywebview[qt]
```

`requirements.txt` 内容相当精简：

```
okf-kit[serve,chat]>=0.3.3
pywebview>=5.0
```

其中 pywebview 的平台后端：
- **Windows**：内置的 Edge WebView2（无需额外安装）
- **macOS**：内置的 WKWebView（无需额外安装）
- **Linux**：需要额外安装 `pywebview[qt]` 或 `[gtk]`

### 第 3 步：启动

```bash
python shell/app.py
```

shell 会启动 `okf serve` 进程内服务器，然后打开原生窗口。若 UI 未构建，会报错提示先执行 `npm run build`。

## 2.3 首次使用流程

启动后 Library 是空的，按下面三步走：

1. **发现**：点击 **Browse registry →** 进入 Discover，浏览社区 bundle
2. **安装**：点击某个 `get`（或已安装时的 `update`），观察 SSE 进度条（downloading → phases…）
3. **阅读 / 对话**：回到 Library，对已装的书点 **Read** 或 **Chat**

## 2.4 开发 UI（热重载）

生产路径是"构建后服务"（build-then-serve），最可靠。若要快速迭代 UI，可以把 shell 指向 Vite dev server：

```bash
cd ui && npm run dev   # 启动 http://localhost:5173
```

但这需要 `okf serve` 允许 dev origin（一个小的 CORS 改动，官方标记为后续跟进项）。因此**推荐仍走 build-then-serve 流程**。

## 2.5 设置 LLM（可选）

LLM 完全可选——没有 LLM 也能做零密钥检索式回答。在 Settings 里三选一：

| Provider | 说明 |
|----------|------|
| **No LLM** | 零密钥检索，引用式回答，不联网 |
| **Ollama** | 本地模型，完全离线对话 |
| **OpenAI-compatible** | 任意托管 API，需提供 key |

API key 存储在操作系统钥匙串（OS keychain），不在 bundle 内。

## 2.6 验证是否成功

启动后顶部状态栏会显示一个"药丸"指示器，例如 `model · online` 或 `no LLM · offline`。左侧边栏显示 `~/.okf · N bundles`（N 为已安装 bundle 数量）。只要看到这行且能进入 Discover 列表，即为运行正常。

---

| 上一章 | 目录 | 下一章 |
|--------|------|--------|
| [01 架构深度解析](./01-architecture.md) | [README](./README.md) | [03 五大界面详解](./03-ui-screens.md) |