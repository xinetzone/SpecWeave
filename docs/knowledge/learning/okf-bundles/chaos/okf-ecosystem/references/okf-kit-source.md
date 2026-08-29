---
type: Reference
title: okf-kit 源码
description: okf-kit 0.3.3 源码仓库登记，包含核心模块文件清单与许可证信息
tags: [okf, okf-kit, source, reference]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: pending, at: pending }
status: draft
stale_after: 2027-08-23
sources:
  - id: facts-okf-kit
    resource: "/references/facts-okf-kit.md"
    title: okf-kit 事实清单
---

# okf-kit 源码

## 仓库信息

| 属性 | 值 |
|------|-----|
| 包名 | `okf-kit` |
| 版本 | `0.3.3` |
| 许可证 | Apache-2.0 |
| Python 要求 | `>=3.10` |
| 仓库地址 | https://github.com/vinodborole/okf-kit |
| Homepage | https://github.com/vinodborole/okf-kit |
| Issues | https://github.com/vinodborole/okf-kit/issues |
| OKF 规范 | https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md |
| 构建后端 | setuptools (`>=68`) |
| 控制台入口 | `okf = "okf_kit.cli:main"` |

## 核心依赖

| 依赖 | 版本约束 | 用途 |
|------|---------|------|
| `httpx` | `>=0.27` | HTTP 异步客户端 |
| `trafilatura` | `>=1.8` | HTML 正文提取为 Markdown |
| `lxml-html-clean` | `>=0.1` | HTML 清理 |
| `selectolax` | `>=0.3.21` | HTML 解析与链接提取 |
| `pyyaml` | `>=6.0` | frontmatter 与 state.json 序列化 |

### 可选依赖组

| 组名 | 包含包 | 用途 |
|------|--------|------|
| `js` | `crawl4ai>=0.6.0`, `trafilatura>=1.8,<2.1` | 浏览器渲染爬取（SPA/JS 站点） |
| `chat` | `openai>=1.60` | OpenAI 兼容对话 |
| `anthropic` | `anthropic>=0.40` | Anthropic Claude 对话 |
| `enrich` | `openai>=1.60` | LLM 自动生成摘要与标签 |
| `mcp` | `mcp>=1.2.0` | MCP stdio 服务 |
| `serve` | `fastapi>=0.110`, `uvicorn>=0.27`, `keyring>=24` | HTTP API 服务 |
| `all` | 以上全部 | 完整功能安装 |
| `dev` | `pytest>=7.0`, `pytest-asyncio>=0.23`, `ruff>=0.6`, `build>=1.0` | 开发与测试 |

## 关键源文件清单

源码根路径：`d:\AI\.chaos\libs\tests\okf-kit\`

### 核心模块（`okf_kit/`）

| 文件路径 | 职责 |
|---------|------|
| `okf_kit/__init__.py` | 包初始化，定义 `__version__ = "0.3.3"` 与模块文档字符串 |
| `okf_kit/cli.py` | argparse CLI 定义与 `main()` 入口，9 个子命令分发 |
| `okf_kit/okf.py` | bundle 校验、frontmatter 生成、保留名处理、目录索引写入、zip 打包 |
| `okf_kit/model.py` | `Page`/`PageRecord` 数据类、`content_hash`、`clean_markdown`、`utcnow_iso` |
| `okf_kit/mapper.py` | URL 规范化、`url_to_relpath` 路径映射、不安全字符处理 |
| `okf_kit/writer.py` | 单页写入、边计算、bundle 元数据聚合写入 state.json |
| `okf_kit/crawl.py` | BFS 爬取主循环、`build_bundle`、fetcher 工厂、质量启发式 |
| `okf_kit/bundle_nav.py` | 导航三原语：`list_directory`、`read_concept`、`search_bundle` |
| `okf_kit/bundle_reader.py` | bundle 读取、frontmatter 解析、边集重建（Markdown 链接 + state.json） |
| `okf_kit/sync.py` | 增量同步、三集合 diff、安全阀门、post_sync 钩子 |
| `okf_kit/visualize.py` | 自包含 HTML 可视化（力导向图 + 树形导航 + 搜索） |
| `okf_kit/enrich.py` | LLM 摘要与标签生成，写回 frontmatter |
| `okf_kit/config.py` | `home_dir()`/`bundles_dir()`/`chats_dir()` 路径管理，`STATE_DIRNAME` 常量 |
| `okf_kit/registry.py` | 远程注册表加载、bundle 安装下载、名称解析 |
| `okf_kit/mcp.py` | MCP Server 实现，4 个工具注册与 stdio 分发 |

### Fetch 子系统（`okf_kit/fetch/`）

| 文件路径 | 职责 |
|---------|------|
| `okf_kit/fetch/__init__.py` | Fetcher 插件抽象文档 |
| `okf_kit/fetch/http.py` | `HttpFetcher`：httpx 异步抓取、robots.txt、trafilatura 提取、selectolax 解析 |
| `okf_kit/fetch/browser.py` | `BrowserFetcher`：crawl4ai 无头浏览器抓取 |

### Chat 子系统（`okf_kit/chat/`）

| 文件路径 | 职责 |
|---------|------|
| `okf_kit/chat/__init__.py` | Chat 模块文档 |
| `okf_kit/chat/agent.py` | LLM 工具调用循环（`ask`），SYSTEM prompt 与 TOOLS 定义，MAX_STEPS=16 |
| `okf_kit/chat/history.py` | JSONL 会话历史持久化（`History` 类） |
| `okf_kit/chat/providers.py` | Provider 抽象：OpenAI 兼容、Anthropic、Ollama 预设，`make_provider` 工厂 |
| `okf_kit/chat/repl.py` | 交互式 REPL（`run_chat`），resume/history/trace |
| `okf_kit/chat/retrieval.py` | 无 LLM 时的纯关键词检索降级路径（`answer`） |

### Serve 子系统（`okf_kit/serve/`）

| 文件路径 | 职责 |
|---------|------|
| `okf_kit/serve/__init__.py` | Serve 模块文档 |
| `okf_kit/serve/app.py` | FastAPI 应用工厂（`create_app`），全部路由、SSE 流式、token 鉴权 |
| `okf_kit/serve/reader.py` | TOC 树构建、concept 视图（heading 锚点 + prev/next）、来源丰富 |
| `okf_kit/serve/run.py` | uvicorn 启动、空闲端口发现、父进程监控、ready JSON 行 |
| `okf_kit/serve/settings.py` | 设置持久化（settings.json）、keyring 密钥存储 |

### 项目配置文件

| 文件路径 | 职责 |
|---------|------|
| `pyproject.toml` | 项目元数据、依赖声明、构建配置、pytest/ruff 配置 |
| `README.md` | 项目说明 |
| `LICENSE` | Apache-2.0 许可证全文 |
| `CHANGELOG.md` | 变更日志 |
| `CONTRIBUTING.md` | 贡献指南 |
| `Dockerfile` | 容器构建定义 |

### 测试（`tests/`）

测试框架为 pytest，配置 `asyncio_mode = "auto"`，`testpaths = ["tests"]`。包含 20+ 测试文件，覆盖构建、导航、MCP、Chat、Serve、同步、注册、映射等模块。
