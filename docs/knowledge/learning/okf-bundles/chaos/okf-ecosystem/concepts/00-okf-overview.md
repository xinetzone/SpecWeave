---
type: Concept
title: OKF 知识包生态概览
description: okf-kit 与 okf-desktop 构成的 OKF 知识包生态总览，涵盖 CLI 命令全景、模块架构、版本依赖与生态组成
tags: [okf, okf-kit, okf-desktop, cli, overview, ecosystem]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: okf-kit-source
    resource: "/references/okf-kit-source.md"
    title: okf-kit 源码
  - id: okf-desktop-source
    resource: "/references/okf-desktop-source.md"
    title: okf-desktop 源码
  - id: facts-okf-kit
    resource: "/references/facts-okf-kit.md"
    title: okf-kit 事实清单
---

# OKF 知识包生态概览

OKF（Open Knowledge Format）是一种将任意网站转化为可移植、智能体就绪（agent-ready）知识包的开放格式。okf-kit 是该格式的参考实现——一个 Python 命令行工具，能够爬取网站、清洗内容为 Markdown、构建知识图谱边，并通过 MCP、Chat、HTTP 三种模式对外提供导航与问答服务。okf-desktop 则是其桌面端封装，使用 pywebview 创建原生窗口，在进程内运行 okf-kit 的 HTTP 服务。

## 什么是 okf-kit

okf-kit 的模块文档字符串自我定义为："okf-kit — turn any website into a portable, agent-ready OKF bundle." [F-002] 包名为 `okf-kit`，当前版本 `0.3.3` [F-001][F-003]，要求 Python `>=3.10` [F-004]，采用 Apache-2.0 许可证 [F-005]。项目仓库托管于 GitHub（https://github.com/vinodborole/okf-kit）[F-020]，规范上游指向 GoogleCloudPlatform 的 knowledge-catalog 仓库中的 OKF SPEC [F-021]。

okf-kit 的核心设计理念是「纯文件即数据库」：知识包不依赖 SQLite、向量数据库或任何运行时服务，而是以 Markdown 文件加 YAML frontmatter 构成完整知识表示，配合单个 state.json 记录全局元数据。这使得知识包可 zip 打包、可离线分发、可人工阅读、可被多种消费端复用。

## CLI 命令全景

okf-kit 通过 `okf` 控制台脚本入口（`okf_kit.cli:main`）[F-015] 提供 10 个子命令，覆盖知识包的完整生命周期：

| 命令 | 用途 | 关键参数 |
|------|------|---------|
| `build` | 从 URL 爬取并构建 bundle | `url`（位置参数）、`-o/--output`、`--max-depth`（默认3）、`--max-pages`（默认200）、`--js`、`--no-robots`、`--path-prefix`、`--all-paths`、`--enrich`、`--enrich-model`、`-v/--verbose` [F-033][F-034][F-035] |
| `validate` | 校验 bundle 结构完整性 | `directory`（位置参数）、`--quiet` [F-036] |
| `zip` | 将 bundle 打包为 zip | `directory`、`-o/--output` [F-037] |
| `sync` | 增量同步已有 bundle | `directory`、`--max-depth`、`--max-pages`、`--force` [F-038] |
| `list` | 列出本地或远程 bundle | `--remote`、`--registry` [F-039] |
| `get` | 从注册表下载安装 bundle | `name`、`--registry`、`--yes/-y` [F-040] |
| `chat` | 与 bundle 对话 | `bundle`、`--provider`、`--model`、`--base-url`、`--trace`、`--resume`、`--history` [F-041] |
| `visualize` | 生成 HTML 可视化图谱 | `directory`、`-o/--output` [F-042] |
| `serve-mcp` | 启动 MCP stdio 服务 | `names`（可变参数）、`--all` [F-043] |
| `serve` | 启动 HTTP API 服务 | `--host`（默认127.0.0.1）、`--port`（默认0=自动）、`--token`（默认auto）、`--ui`、`--parent-pid` [F-044] |

CLI 使用 argparse 构建，`_build_parser()` 返回 `prog="okf"` 的解析器 [F-030]，子命令通过 `dest="command"` 分发且为必填 [F-031]。全局参数 `--version` 输出版本号 [F-032]。`main(argv)` 函数作为统一入口，根据子命令调用对应模块函数并返回退出码（0 成功，3 校验失败）[F-045][F-048][F-056]。

## 核心运行时依赖

okf-kit 的核心依赖精简而专注 [F-006]：

- **httpx**（`>=0.27`）：异步 HTTP 客户端，支持连接池、重定向跟随、超时控制
- **trafilatura**（`>=1.8`）：正文提取库，将 HTML 转为 Markdown，支持表格、格式、链接
- **lxml-html-clean**（`>=0.1`）：HTML 清理
- **selectolax**（`>=0.3.21`）：基于 lexbor 的快速 HTML 解析器，用于提取标题、描述、链接
- **pyyaml**（`>=6.0`）：YAML frontmatter 与 state.json 序列化

可选依赖按功能分组 [F-007~F-013]，用户可按需安装：`js`（浏览器渲染爬取）、`chat`（OpenAI 对话）、`anthropic`（Claude 对话）、`enrich`（LLM 摘要）、`mcp`（MCP 协议）、`serve`（HTTP 服务）。`all` 组包含全部功能。

## 生态组成：kit + desktop

OKF 生态由两个互补项目构成：

**okf-kit**（后端核心）：Python 包，提供 CLI 命令、爬取引擎、数据模型、三种服务模式。它既是知识包的生产工具（build/sync），也是消费工具（chat/serve-mcp/serve）。桌面端依赖 `okf-kit[serve,chat]>=0.3.3` [DF-004]。

**okf-desktop**（桌面阅读器）：版本 `0.1.0` [DF-001]，采用 AGPL-3.0 许可证 [DF-003]，支持 Linux/macOS/Windows [DF-006]。它不包含任何 okf-kit 业务逻辑，UI 是纯 React 应用 [DF-007]，通过 okf-kit 本地 API（`okf serve`）通信。桌面 shell 在后台线程中进程内运行 uvicorn + FastAPI，用 pywebview 创建原生窗口指向该服务 [DF-010][DF-029]。

两个项目的职责在打包时被物理隔离：okf-desktop 的 PyInstaller spec 刻意排除爬取栈（trafilatura/selectolax/lxml/crawl4ai）[DF-079]，桌面应用是 bundle 的「阅读器/聊天器」而非「生产器」。

## 模块架构

okf-kit 的 Python 包 `okf_kit/` 包含以下模块群：

- **核心层**：`okf.py`（校验/索引/打包）、`model.py`（数据类）、`mapper.py`（URL映射）、`writer.py`（写入器）、`config.py`（路径配置）
- **生产层**：`crawl.py`（BFS爬取）、`fetch/`（HttpFetcher/BrowserFetcher）、`enrich.py`（LLM增强）、`sync.py`（增量同步）
- **导航层**：`bundle_nav.py`（三原语）、`bundle_reader.py`（读取/边重建）、`visualize.py`（可视化）
- **分发层**：`registry.py`（远程注册表）
- **服务层**：`mcp.py`（MCP服务）、`chat/`（对话代理）、`serve/`（HTTP API）

这种分层使得「生产」与「消费」解耦：构建好的 bundle 是纯数据，任何服务模式都不需要知道爬取细节。

## 配置与数据目录

okf-kit 使用 `OKF_HOME` 环境变量配置主目录，默认为 `~/.okf/` [F-270]。目录结构如下：

```text
~/.okf/
├── bundles/       # 已安装的 bundle 目录 [F-271]
├── chats/         # 对话历史（JSONL）[F-272]
├── settings.json  # 服务设置（provider/model/base_url）[F-209]
└── .secrets.json  # API 密钥（keyring 不可用时的回退）[F-212]
```

每个 bundle 目录内有一个 `.okf-kit/` 子目录存放 `state.json` [F-273]，记录生成器版本、根 URL、页面清单（含 content_hash）和边表，是 bundle 的「目录索引」。

## 相关概念

- [Bundle 数据模型与语义边](/concepts/01-bundle-data-model.md)
- [网站爬取与 Bundle 构建流水线](/concepts/02-crawl-build-pipeline.md)
- [MCP/Chat/HTTP 三模服务架构](/concepts/04-service-modes.md)
- [桌面应用同进程架构与打包](/concepts/05-desktop-architecture.md)
