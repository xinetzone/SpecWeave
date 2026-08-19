---
id: "okf-desktop-wiki-faq-resources"
title: "06 FAQ 与术语表"
version: "1.0"
source: "README.md（Notes/Download 章节）+ 源码注释"
type: "Wiki Tutorial"
description: "okf-desktop 常见问题解答、核心术语表、官方资源链接"
tags: ["okf-desktop", "faq", "术语表", "glossary", "resources", "checklist"]
category: "learning"
date: "2026-08-19"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "回答覆盖运行、打包、安全、扩展等 8 个常见问题；提供 20+ 核心术语表与官方资源链接"
last_verified: "2026-08-19"
wiki_version: "1.0"
okf_version_target: "okf-kit 0.3.3+"
---

# 06 FAQ 与术语表

## 6.1 常见问题

### Q1：okf-desktop 和 okf-kit 是什么关系？
okf-desktop 是 okf-kit 的桌面图形前端，**不包含任何 okf-kit 逻辑**。它只是一个纯 React UI，通过 HTTP API（`okf serve`）调用 okf-kit 的能力。升级 okf-kit 即可让桌面应用免费获得新功能。

### Q2：为什么 Windows 上杀软会误报？
因为 `.exe` 是未签名的 PyInstaller 构建，没有代码签名身份为其背书。程序本身并非恶意。解决方式：用发布页的 SHA-256 加白、待签名后按发布者加白，或直接从源码运行。

### Q3：mac 提示"已损坏"怎么办？
它是 Gateskeeper 的隔离标志误判，不是真损坏。清除隔离属性即可：
```bash
xattr -dr com.apple.quarantine ~/Downloads/okf-desktop.app
open ~/Downloads/okf-desktop.app
```

### Q4：没有 LLM 能用吗？
能。选 **No LLM** 就是零密钥检索，返回带引用的答案，不联网。LLM 仅用于对话增强。

### Q5：API key 存在哪里？
存在系统的钥匙串（OS keychain），**不会**写进 bundle。Settings 界面显示 `•stored ✓` 表示已保存，且输入框仅回显掩码。

### Q6：为什么聊天回答不是逐字流式？
后端目前是**把完整答案分块返回**，真正的 token 级流式被列为 okf-kit v1 的改动。前端已按 token 事件逐段渲染，后端升级后 UI 无需改动。

### Q7：为什么 UI 从源码启动要分两步（build + serve）？
生产路径是"构建后服务"：`okf serve` 同时托管 `ui/dist`（静态）与 `/api`（接口），同源无 CORS。Vite 热重载需要后端额外允许 dev origin（官方标记为后续项），所以推荐 build-then-serve。

### Q8：能交叉编译出一个跨平台安装包吗？
不能。PyInstaller 不交叉编译，必须在每个目标 OS 上分别运行 `build.sh`，由该平台的 CI 各出各的包。

### Q9：字体为什么完全离线可用？
Newsreader / Libre Franklin / IBM Plex Mono 通过 `@fontsource` 自托管，Vite 把 woff2 打包进 `dist`，无 CDN、无网络依赖。

### Q10：打包体积还能更小吗？
Linux 包约 140 MB 主要来自 GTK + ICU + Python。spec 已通过 `excludes`（爬虫栈/uvloop/等）和裁剪 GTK 数据（约 225 MB）显著瘦身，进一步压需要换更轻的运行时或分段分发。

## 6.2 核心术语表（Glossary）

| 术语 | 中文 | 定义 |
|------|------|------|
| okf-kit | OKF 工具链 | Vinod Borole 开发的便携 OKF 工具链，提供 `okf serve`/`get`/`chat` 等命令与本地 API |
| okf serve | okf 本地服务 | okf-kit 启动的本地 ASGI 服务，托管 UI（`/`）与 API（`/api`） |
| bundle / book | 知识包 / 书 | 一个 OKF 知识包，桌面应用里称"书" |
| registry | 登记中心 | 社区 bundle 的分发目录，Discover 界面从中发现并安装 |
| concept | 概念 | bundle 中的一个知识单元，对应一个 Markdown 内容 |
| TOC (tree) | 目录树 | `GET /toc` 返回的概念层级结构，含 section 与 concept 节点 |
| pywebview | Python 原生窗口库 | 用系统 webview 创建原生窗口的库，shell 用它承载 React UI |
| js_api | Python↔JS 桥 | pywebview 机制，把 Python 类方法暴露给前端 `window.pywebview.api` |
| Shell | 启动器 | `shell/app.py`，负责启动服务器、打开窗口、桥接外链 |
| SSE | 服务端推送事件 | Server-Sent Events，用于安装进度与对话回答的流式传输 |
| Bearer token | 承载令牌 | shell 每次启动生成的随机令牌，前端放入 `Authorization` 头做鉴权 |
| 引用深链 | deep-link to source | 点击对话引用 chips 跳回阅读器对应章节的交互 |
| resource map | 资源映射 | 原始 URL → concept id 的 Map，用于判断链接是否书内跳转 |
| normUrl | URL 归一化 | 去协议/query/fragment/尾部斜杠，得到可比较的 URL key |
| 零逻辑客户端 | zero-logic client | 客户端不含业务逻辑、只做展示与转发的架构原则 |
| 进程内服务器 | in-process server | 用线程在进程内跑服务器，是 PyInstaller 单文件冻结的前提 |
| 单源无 CORS | single-origin no CORS | UI 与 API 同源托管，前端请求无需跨域处理 |
| keychain | 系统钥匙串 | macOS Keychain / Windows 凭据库等，LLM key 的安全存储处 |
| ~/.okf | okf 数据目录 | okf-kit 的默认数据目录，存放 bundle 与聊天记录 |
| PyInstaller | Python 打包器 | 把 Python 应用及其依赖冻结为独立可执行文件的工具 |
| excludes / hiddenimports | 排除 / 隐藏导入 | spec 中两处配置：裁掉未用依赖、补全动态导入模块 |
| AGPL-3.0 | 网络版 GPL v3 | okf-desktop 的许可证，要求网络服务场景也开源衍生代码 |

## 6.3 官方资源链接

- [okf-desktop 仓库](https://github.com/vinodborole/okf-desktop) - 源码与 Issues
- [okf-desktop Releases](https://github.com/vinodborole/okf-desktop/releases) - 三平台预构建包下载
- [okf-kit 仓库](https://github.com/vinodborole/okf-kit) - 所依赖的工具链（Apache-2.0）
- [pywebview](https://pywebview.flowrl.com/) - 原生窗口库
- [OKF 官网](https://okf.md/) - Open Knowledge Format 规范

## 6.4 延伸阅读

1. 想理解 bundle 格式细节 → 读 [OKF 开放知识格式](../okf-wiki/README.md)
2. 想理解 bundle 如何分发/注册 → 读 [OKF 生态基建知识](../okf-wiki/okf-ecosystem-wiki/README.md)
3. 想用命令行消费知识 → 参考 okf-kit 的 `okf get` / `okf chat` 命令
4. 想二次开发桌面应用 → 重点研读 `shell/app.py` 与 `ui/src/api.js`，这两个文件承载了全部胶水逻辑

---

| 上一章 | 目录 | 下一章 |
|--------|------|--------|
| [05 跨平台打包](./05-packaging.md) | [README](./README.md) | （已完成，是最后一章） |