---
type: Example
title: CLI 命令使用示例
description: okf 命令行工具 build/validate/sync/list/get/chat/visualize/serve-mcp/serve 各命令的实际用法与参数说明
tags: [okf, cli, example, usage, command-line]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: okf-kit-source
    resource: "/references/okf-kit-source.md"
    title: okf-kit 源码
  - id: facts-okf-kit
    resource: "/references/facts-okf-kit.md"
    title: okf-kit 事实清单
---

# CLI 命令使用示例

本文档提供 `okf` 命令行工具各子命令的实际用法示例。所有参数均来自 `okf_kit/cli.py` 中的 argparse 定义。

## 全局用法

```bash
okf [--version] <command> [options]
```

`--version` 输出版本号（格式为 `okf 0.3.3`）。`<command>` 为必填项。

## build：构建知识包

从网站 URL 爬取并构建 OKF bundle。

```bash
# 基本用法：爬取网站，输出到 ./{host}-okf 目录
okf build https://docs.example.com

# 指定输出目录
okf build https://docs.example.com -o ./my-docs

# 限制爬取深度和页面数
okf build https://docs.example.com --max-depth 2 --max-pages 50

# 使用浏览器渲染模式（需安装 okf-kit[js]）
okf build https://spa.example.com --js

# 不遵守 robots.txt
okf build https://docs.example.com --no-robots

# 限定爬取路径前缀
okf build https://docs.example.com --path-prefix /guide/

# 爬取所有路径（不按前缀限定范围）
okf build https://docs.example.com --all-paths

# 构建后使用 LLM 自动生成摘要和标签（需安装 okf-kit[enrich]）
okf build https://docs.example.com --enrich

# 指定 enrich 使用的模型
okf build https://docs.example.com --enrich --enrich-model gpt-4o

# 详细输出
okf build https://docs.example.com -v
```

**参数说明**：
- `url`（位置参数）：根 URL
- `-o, --output DIR`：输出目录
- `--max-depth int`：BFS 最大深度，默认 3
- `--max-pages int`：最大页面数，默认 200
- `--js`：使用浏览器渲染（BrowserFetcher）
- `--no-robots`：不遵守 robots.txt
- `--path-prefix PATH`：限定爬取路径前缀
- `--all-paths`：不限定路径范围
- `--enrich`：构建后 LLM 增强
- `--enrich-model`：enrich 模型，默认 `gpt-4o-mini`
- `-v, --verbose`：详细输出

## validate：校验知识包

校验 bundle 目录结构完整性。

```bash
# 校验指定目录
okf validate ./my-docs

# 静默模式（仅通过退出码判断结果）
okf validate ./my-docs --quiet
```

校验规则：遍历所有 `.md` 文件（跳过 `.okf-kit/` 和保留文件），检查 frontmatter 是否存在且 `type` 字段非空。成功返回退出码 0，失败返回 3。

## zip：打包知识包

将 bundle 目录打包为 zip 文件。

```bash
# 打包为 zip（输出文件名默认为目录名.zip）
okf zip ./my-docs

# 指定输出文件
okf zip ./my-docs -o ./my-docs-v1.zip
```

使用 ZIP_DEFLATED 压缩，顶层文件夹名为 bundle 目录名。

## sync：增量同步

增量更新已有 bundle，仅同步变化的页面。

```bash
# 基本同步（沿用 build 时的配置）
okf sync ./my-docs

# 覆盖深度和页面数限制
okf sync ./my-docs --max-depth 5 --max-pages 500

# 强制同步（绕过安全阀门）
okf sync ./my-docs --force
```

**参数说明**：
- `directory`（位置参数）：bundle 目录
- `--max-depth int`：最大深度，默认 None（沿用原配置）
- `--max-pages int`：最大页面数，默认 None（沿用原配置）
- `--force`：强制同步，绕过安全阀门

安全阀门：非 force 模式下，若旧页面数 > 4 且新页面数 < 旧页面数 × 0.5，将拒绝同步。

## list：列出知识包

列出本地已安装或远程注册表中的 bundle。

```bash
# 列出本地已安装的 bundle
okf list

# 列出远程注册表中的 bundle
okf list --remote

# 指定自定义注册表 URL 或本地文件
okf list --remote --registry https://example.com/registry.yaml
```

## get：下载安装知识包

从注册表下载并安装 bundle。

```bash
# 下载安装指定 bundle（需确认）
okf get my-docs

# 指定注册表
okf get my-docs --registry https://example.com/registry.yaml

# 自动确认，跳过提示
okf get my-docs -y
okf get my-docs --yes
```

下载的 zip 解压到 `~/.okf/bundles/{name}/`，并自动校验。

## chat：与知识包对话

启动交互式对话，基于 bundle 内容回答问题。

```bash
# 使用纯关键词检索（无需 LLM）
okf chat my-docs

# 使用 OpenAI
okf chat my-docs --provider openai --model gpt-4o

# 使用 Anthropic Claude
okf chat my-docs --provider anthropic --model claude-sonnet-5

# 使用 Ollama（本地）
okf chat my-docs --provider ollama

# 使用 OpenRouter
okf chat my-docs --provider openrouter --model openai/gpt-4o-mini

# 使用自定义 OpenAI 兼容端点
okf chat my-docs --provider custom --base-url http://localhost:8000/v1 --model my-model

# 恢复上次会话
okf chat my-docs --resume

# 查看历史会话列表
okf chat my-docs --history

# 启用追踪（显示工具调用步骤）
okf chat my-docs --provider openai --trace
```

**参数说明**：
- `bundle`（位置参数）：bundle 名称或目录路径
- `--provider`：LLM 提供商（openai/anthropic/ollama/openrouter/custom/none）
- `--model`：模型名称
- `--base-url`：自定义 API 基础 URL
- `--trace`：显示工具调用追踪
- `--resume`：恢复最新会话
- `--history`：列出历史会话

无 provider 时使用纯关键词检索（`provider=none`）。LLM 模式下 agent 最多执行 16 步工具调用（list_directory/read_concept）。

## visualize：生成可视化

生成自包含 HTML 可视化图谱。

```bash
# 生成可视化（默认输出到 {bundle}/viz.html）
okf visualize ./my-docs

# 指定输出文件
okf visualize ./my-docs -o ./graph.html
```

生成的 HTML 包含力导向图、树形导航、搜索、Markdown 渲染、链接和反向链接展示，支持暗色模式，无外部依赖。

## serve-mcp：启动 MCP 服务

启动 MCP（Model Context Protocol）stdio 服务，供 AI IDE 调用。

```bash
# 服务指定 bundle
okf serve-mcp my-docs

# 服务多个 bundle
okf serve-mcp docs1 docs2 docs3

# 服务所有已安装的 bundle
okf serve-mcp --all
```

提供四个 MCP 工具：`list_bundles`、`list_directory`、`read_concept`、`search_bundle`。需安装 `okf-kit[mcp]`。

## serve：启动 HTTP 服务

启动本地 HTTP API 服务，供 Web 前端或桌面端消费。

```bash
# 基本启动（自动选择端口和 token）
okf serve

# 指定主机和端口
okf serve --host 0.0.0.0 --port 8080

# 指定固定 token
okf serve --token my-secret-token

# 托管 UI 静态文件
okf serve --ui ./path/to/ui/dist

# 监控父进程（父进程退出时自动关闭）
okf serve --parent-pid 12345
```

**参数说明**：
- `--host`：监听地址，默认 `127.0.0.1`
- `--port`：端口，默认 0（自动选择空闲端口）
- `--token`：鉴权 token，默认 `auto`（自动生成随机 token）
- `--ui`：UI 静态文件目录，提供时在 `/` 托管
- `--parent-pid`：父进程 PID，父进程退出时服务自动关闭

启动后输出 JSON 格式的 ready 行：

```json
{"event": "ready", "url": "http://127.0.0.1:52341", "token": "abc123...", "pid": 5678}
```

API 端点包括：`/api/health`、`/api/status`、`/api/books`、`/api/registry`、`/api/books/{name}/toc`、`/api/books/{name}/concept`、`/api/books/{name}/chats`、`/api/settings` 等。需安装 `okf-kit[serve]`。

## 安装可选依赖

```bash
# 仅核心功能
pip install okf-kit

# 浏览器渲染爬取
pip install "okf-kit[js]"

# 对话功能（OpenAI）
pip install "okf-kit[chat]"

# Anthropic 支持
pip install "okf-kit[anthropic]"

# LLM 增强
pip install "okf-kit[enrich]"

# MCP 服务
pip install "okf-kit[mcp]"

# HTTP 服务
pip install "okf-kit[serve]"

# 全部功能
pip install "okf-kit[all]"

# 开发依赖
pip install "okf-kit[dev]"
```

## 相关概念

- [OKF 知识包生态概览](/concepts/00-okf-overview.md)
- [网站爬取与 Bundle 构建流水线](/concepts/02-crawl-build-pipeline.md)
- [增量同步与安全阀门](/concepts/03-sync-incremental.md)
- [MCP/Chat/HTTP 三模服务架构](/concepts/04-service-modes.md)
