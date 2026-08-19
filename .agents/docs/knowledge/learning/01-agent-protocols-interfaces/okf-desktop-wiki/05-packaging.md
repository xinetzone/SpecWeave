---
id: "okf-desktop-wiki-packaging"
title: "05 跨平台打包"
version: "1.0"
source: "build.sh + okf-desktop.spec + version_info.txt + README.md（Package 章节）"
type: "Wiki Tutorial"
description: "okf-desktop 的 PyInstaller 打包策略：进程内服务器冻结、依赖排除、三平台差异、签名公证"
tags: ["okf-desktop", "packaging", "pyinstaller", "冻结", "跨平台", "签名"]
category: "learning"
date: "2026-08-19"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "用 PyInstaller 把 pywebview shell + 进程内 okf serve + React UI 冻结为单一可执行文件；通过 excludes 裁剪爬虫栈与未用依赖，Linux 包约 140MB；三平台 webview 后端各异；签名公证为独立步骤"
last_verified: "2026-08-19"
wiki_version: "1.0"
okf_version_target: "okf-kit 0.3.3+"
---

# 05 跨平台打包

## 5.1 打包目标

把三样东西冻结成一个自包含可执行文件：

1. pywebview shell（启动器）
2. **进程内** okf serve API
3. 构建好的 React UI（`ui/dist`）

三个平台各出各的包（**PyInstaller 不做交叉编译**，必须在目标 OS 上构建）。构建入口是 `build.sh`，分三步：

```bash
# 1/3 构建 UI
( cd ui && npm install --no-audit --no-fund && npm run build )
# 2/3 PyInstaller 冻结
python3 -m PyInstaller okf-desktop.spec --noconfirm --log-level WARN
# 3/3 打包归档（Linux tar.gz / macOS zip）
```

## 5.2 进程内服务器：可冻结的前提

冻结后的应用运行时，`okf serve` 是**在进程内的线程上**跑的（而非 subprocess），它服务打包的 `ui/dist` + API，监听随机回环端口，再打开 pywebview 窗口。这与 `shell/app.py` 里的 `start_server` 完全一致——打包只是把同一套代码和资源塞进一个目录。

## 5.3 spec 里的隐藏导入与排除（hiddenimports / excludes）

`okf-desktop.spec` 是打包的关键配置。PyInstaller 靠静态分析找依赖，但不少模块是**动态导入**的，必须显式声明 `hiddenimports`：

```python
hiddenimports = []
hiddenimports += collect_submodules("uvicorn")      # 动态 loop/protocol 导入
hiddenimports += collect_submodules("keyring")      # 凭证后端
hiddenimports += collect_submodules("okf_kit.serve")
hiddenimports += collect_submodules("openai")       # 被 chat provider 延迟导入
hiddenimports += [
    "okf_kit", "okf_kit.serve.app", "okf_kit.chat.agent", "okf_kit.chat.retrieval",
    "okf_kit.chat.providers", "okf_kit.chat.history",
]
if sys.platform.startswith("linux"):
    # pywebview 的 GTK 后端动态拉取 gi 模块
    hiddenimports += ["gi", "gi.repository.Gtk", "gi.repository.Gdk",
                      "gi.repository.GLib", "gi.repository.WebKit2"]
```

反过来，`excludes` 裁掉了大量**未使用**的大块依赖，让包保持小巧：

```python
excludes = [
    "trafilatura", "selectolax", "lxml", "crawl4ai",   # 爬虫栈——消费端用不到
    "uvloop", "httptools", "watchfiles", "websockets", # uvicorn[standard] 扩展——本项目用 asyncio/h11
    "botocore", "boto3", "s3transfer", "zstandard",    # AWS/压缩——无关
    "tkinter", "matplotlib", "numpy", "pandas", "PIL", "scipy", "pytest", "IPython",
]
```

排除思路：okf-desktop 是**只读消费端**，不需要 crawl（爬取）能力；服务器用 `asyncio/h11` 而非 uvloop/httptools，因此可裁掉这些原生扩展。最终 Linux 包约 **140 MB**（主要是 GTK + ICU + Python）。

## 5.4 进一步瘦身：裁剪 GTK 数据

```python
_DROP = ("share/icons", "share/themes", "share/locale", "share/doc", "share/man")
a.datas = [d for d in a.datas if not d[0].startswith(_DROP)]
```

WebView 窗口不需要图标主题/主题/语言包，直接丢弃约 225 MB 的 GTK 数据。GTK 会在需要时回退到系统目录。

## 5.5 三平台 webview 差异

| 平台 | webview 后端 | 冻结方式 |
|------|--------------|----------|
| **Linux** | 系统 GTK3 + WebKit2GTK | 复用系统库，**不打进包** |
| **macOS** | WKWebView | 更自包含 |
| **Windows** | Edge WebView2 | 更自包含 |

macOS 还额外通过 `BUNDLE` 把产物包装成 `.app`，使其可临时签名（深签名含捆绑的 Python.framework），从而把 Gatekeeper 的"已损坏"死胡同变成可绕过的"未识别开发者"提示。

## 5.6 Windows 版本资源

`version_info.txt` 给 `.exe` 提供真实产品身份（公司名、产品名、版本 0.1.4.0、版权、图标元数据）。spec 里用 `version="version_info.txt"` 引用它。这有两个作用：轻微改善杀软/EDR 的声誉判定，以及是后续代码签名的必要前提。

## 5.7 签名与公证（独立步骤）

公开分发还差最后一步——**代码签名与公证**：

- **Apple notarization**：让 macOS 用户不再收到 Gatekeeper 警告
- **Windows code signing cert**：让 SmartScreen/杀软不再误报

目前项目尚未签名，故 README 详细说明了用户如何绕过 mac Gatekeeper / Windows SmartScreen 的流程。签名是独立于 PyInstaller 打包的步骤。

## 5.8 打包要点小结

1. **进程内服务器**是"可冻结"的根因（子进程没法干净打成单二进制）
2. **hiddenimports 补动态导入**、**excludes 裁无用依赖**是控制体积的两把刀
3. **每个 OS 单独构建**，webview 后端差异由平台天然决定
4. **签名公证与 PyInstaller 解耦**，分别推进

---

| 上一章 | 目录 | 下一章 |
|--------|------|--------|
| [04 API 与数据流](./04-api-and-data-flow.md) | [README](./README.md) | [06 FAQ 与术语表](./06-faq-and-resources.md) |