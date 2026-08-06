---
id: "codewhale-tech-deploy"
title: 安装渠道与提供商配置
description: CodeWhale 安装渠道对比、分平台安装步骤、中国用户镜像加速、配置目录结构、提供商配置示例、生命周期 Hook、搜索后端与上下文分层、沙箱安全配置
last_updated: 2026-08-04
source: CodeWhale v0.9.3/v0.9.4 官方文档与源码
---

# 安装渠道与提供商配置

> 本文档覆盖 CodeWhale 的完整安装与配置流程，从安装渠道选择到提供商（Provider）配置、生命周期 Hook、搜索后端、上下文分层管理和沙箱安全，为不同平台的用户提供一站式部署指南。

## 1. 安装渠道对比

CodeWhale 提供 **7 种安装渠道**，覆盖主流包管理器和构建方式：

| 渠道 | 命令 | 适用平台 | 说明 |
|---|---|---|---|
| npm | `npm install -g codewhale` | 全平台 | Node.js 18+，npm wrapper 从 GitHub Releases 下载经 SHA-256 校验的二进制 |
| Cargo | `cargo install codewhale` | 全平台 | Rust 生态用户首选 |
| Homebrew | `brew install codewhale` | macOS / Linux | macOS 用户最便捷 |
| Docker | `docker pull ghcr.io/hmbown/codewhale` | 全平台 | 容器化部署，隔离运行 |
| 预编译二进制 | [GitHub Releases](https://github.com/Hmbown/CodeWhale/releases) | 全平台 | 零依赖，直接下载运行 |
| Nix | `nix profile install` | Linux / macOS | Nix 生态用户 |
| 源码编译 | `cargo build --release` | 全平台 | 开发者/定制需求 |

## 2. 分平台安装步骤

### 2.1 支持的平台矩阵

| 平台 | 架构 | 状态 |
|---|---|---|
| Linux | x64 / arm64 / riscv64 | ✅ 正式支持 |
| macOS | x64 / arm64（Apple Silicon） | ✅ 正式支持 |
| Windows | x64 / arm64 | ✅ 正式支持 |
| Android / Termux | arm64 | ⚠️ 预览阶段 |

> **注意**：自 v0.8.65 起，Linux x64 发布资产为静态 musl 构建，无需 glibc 依赖，可在任意 Linux 发行版上运行。

### 2.2 Linux

```bash
# 预编译二进制（推荐）
curl -L https://github.com/Hmbown/CodeWhale/releases/latest/download/codewhale-linux-x64.tar.gz | tar xz
sudo mv codewhale /usr/local/bin/

# Cargo
cargo install codewhale

# npm
npm install -g codewhale
```

### 2.3 macOS

```bash
# Homebrew（推荐）
brew install codewhale

# 预编译二进制（Apple Silicon）
curl -L https://github.com/Hmbown/CodeWhale/releases/latest/download/codewhale-macos-arm64.tar.gz | tar xz
sudo mv codewhale /usr/local/bin/
```

### 2.4 Windows

```powershell
# 预编译二进制（推荐）
# 下载 .zip 包后解压至 PATH 目录，或使用 winget/scoop

# npm
npm install -g codewhale
```

### 2.5 Docker

```bash
# 拉取镜像
docker pull ghcr.io/hmbown/codewhale:latest

# 运行（挂载配置目录）
docker run -it --rm \
  -v $HOME/.codewhale:/root/.codewhale \
  -v $(pwd):/workspace \
  ghcr.io/hmbown/codewhale:latest
```

### 2.6 Android / Termux（预览）

```bash
# Termux 环境
pkg install codewhale
```

## 3. 中国用户镜像加速

国内用户可通过以下镜像站点加速下载：

| 镜像源 | 预编译二进制 | 说明 |
|---|---|---|
| CNB（Cloud Native Build） | ✅ | 国内 CDN 加速 |
| TUNA（清华大学开源软件镜像站） | ✅ | 教育网用户首选 |

```bash
# CNB 镜像加速示例
curl -L https://cnb.cool/Hmbown/CodeWhale/-/releases/latest/download/codewhale-linux-x64.tar.gz | tar xz
```

## 4. 配置目录结构

### 4.1 全局配置目录

CodeWhale 的全局配置存储在 `~/.codewhale/`，可通过环境变量 `CODEWHALE_HOME` 自定义路径：

```
~/.codewhale/
├── config.toml          # 主配置文件（API 密钥、模型、钩子）
├── mcp.json             # MCP 服务器配置
├── skills/              # 用户自定义技能
├── sessions/            # 会话检查点
├── tasks/               # 后台任务
└── audit.log            # 审计日志
```

### 4.2 项目级配置目录

每个仓库可有独立的项目级配置，存放于 `./.codewhale/`：

```
./.codewhale/
├── constitution.json    # 仓库本地宪法
├── fleet.jsonl          # Fleet 状态台账
└── config.toml          # 项目级配置覆盖
```

### 4.3 兼容路径

旧版 `~/.deepseek` 和 `./.deepseek` 路径仍作为兼容回退读取，确保从 deepseek-tui 升级的用户配置不丢失。

## 5. 提供商配置示例

配置文件 `config.toml` 约 1364 行，包含 33 个 provider 配置段。以下为常用提供商配置示例：

### 5.1 DeepSeek

```toml
[provider.deepseek]
endpoint = "https://api.deepseek.com/v1"
api_key = "sk-your-deepseek-api-key"

[model.deepseek-chat]
provider = "deepseek"
name = "deepseek-chat"

[model.deepseek-reasoner]
provider = "deepseek"
name = "deepseek-reasoner"
```

### 5.2 OpenAI

```toml
[provider.openai]
endpoint = "https://api.openai.com/v1"
api_key = "sk-your-openai-api-key"

[model.gpt-4o]
provider = "openai"
name = "gpt-4o"
```

### 5.3 Ollama（本地）

```toml
[provider.ollama]
endpoint = "http://localhost:11434/v1"
api_key = ""  # 本地运行无需 API 密钥

[model.ollama-qwen]
provider = "ollama"
name = "qwen2.5-coder:14b"
```

### 5.4 多提供商并存

```toml
# 可同时配置多个提供商，CodeWhale 按需切换
[provider.deepseek]
endpoint = "https://api.deepseek.com/v1"
api_key = "sk-xxx"

[provider.anthropic]
endpoint = "https://api.anthropic.com/v1"
api_key = "sk-ant-xxx"

[provider.ollama]
endpoint = "http://localhost:11434/v1"
api_key = ""
```

## 6. 生命周期 Hook 配置

CodeWhale 支持 **11 个生命周期 Hook 事件**，可在特定时机执行自定义脚本：

| Hook 事件 | 触发时机 | 典型用途 |
|---|---|---|
| `session_start` | 会话开始时 | 环境初始化 |
| `session_end` | 会话结束时 | 清理临时文件 |
| `message_submit` | 消息提交时 | 上下文注入 |
| `tool_call_before` | 工具调用前 | 参数校验 |
| `tool_call_after` | 工具调用后 | 结果后处理 |
| `mode_change` | 模式切换时 | 状态记录 |
| `on_error` | 发生错误时 | 错误通知 |
| `turn_end` | 回合结束时 | 响应日志 |
| `subagent_spawn` | 子 Agent 启动时 | 预检查 |
| `subagent_complete` | 子 Agent 完成时 | 结果汇总 |
| `shell_env` | Shell 环境准备时 | 环境变量注入 |

```toml
# config.toml — Hook 配置示例
[hooks]
session_start = "echo 'Session started at $(date)' >> ~/.codewhale/session.log"
session_end = "echo 'Session ended at $(date)' >> ~/.codewhale/session.log"
on_error = "echo 'Error occurred' >> ~/.codewhale/error.log"
```

## 7. 搜索后端配置

CodeWhale 支持 **9 个搜索后端**，为 Agent 提供联网检索能力：

| 搜索后端 | 标识 | 说明 |
|---|---|---|
| DuckDuckGo | `duckduckgo` | 免费，无需 API 密钥 |
| Bing | `bing` | 需要 Azure API 密钥 |
| Tavily | `tavily` | AI 优化搜索，需要 API 密钥 |
| Bocha | `bocha` | 国内搜索服务 |
| Metaso | `metaso` | 国内 AI 搜索 |
| SearXNG | `searxng` | 自托管，可私有化部署 |
| Baidu | `baidu` | 国内搜索引擎 |
| Volcengine | `volcengine` | 火山引擎搜索 |
| Sofya | `sofya` | 代码搜索专用 |

```toml
# config.toml — 搜索后端配置示例
[search]
backend = "duckduckgo"  # 默认免费后端

[search.tavily]
api_key = "tvly-xxx"

[search.bing]
api_key = "your-azure-api-key"
endpoint = "https://api.bing.microsoft.com/v7.0/search"
```

## 8. 上下文分层管理

CodeWhale 采用三层上下文分层策略，按 token 使用量动态管理上下文窗口：

| 层级 | 阈值 | 用途 |
|---|---|---|
| L1（热上下文） | 192k tokens | 最近交互，全量保留 |
| L2（温上下文） | 384k tokens | 压缩摘要，关键信息保留 |
| L3（冷上下文） | 576k tokens | 索引化存储，按需检索 |

| 参数 | 默认值 | 说明 |
|---|---|---|
| `verbatim_window_turns` | 16 | 完整保留的最近对话轮数 |
| `l1_threshold` | 192k | L1 热上下文阈值 |
| `l2_threshold` | 384k | L2 温上下文阈值 |
| `l3_threshold` | 576k | L3 冷上下文阈值 |

```toml
# config.toml — 上下文分层配置
[context]
verbatim_window_turns = 16
l1_threshold = 192000
l2_threshold = 384000
l3_threshold = 576000
```

## 9. 沙箱安全配置

CodeWhale 支持操作系统级沙箱隔离：

| 平台 | 沙箱机制 | 启用方式 |
|---|---|---|
| macOS | Seatbelt（内置） | 默认启用 |
| Linux | bubblewrap | 需显式启用 |

```toml
# config.toml — 沙箱配置
[sandbox]
enabled = true
backend = "bubblewrap"  # Linux 需显式指定
```

```bash
# Linux 安装 bubblewrap 依赖
sudo apt install bubblewrap   # Debian/Ubuntu
sudo dnf install bubblewrap   # Fedora
```

## 10. 配置速查

| 配置项 | 路径 | 格式 | 说明 |
|---|---|---|---|
| 主配置 | `~/.codewhale/config.toml` | TOML | API 密钥、模型、钩子、搜索等 |
| MCP 服务器 | `~/.codewhale/mcp.json` | JSON | 模型上下文协议服务器 |
| 用户技能 | `~/.codewhale/skills/` | 目录 | 自定义 Skill 文件 |
| 会话检查点 | `~/.codewhale/sessions/` | 目录 | 会话状态持久化 |
| 后台任务 | `~/.codewhale/tasks/` | 目录 | 后台异步任务 |
| 审计日志 | `~/.codewhale/audit.log` | 文本 | 操作审计记录 |
| 项目宪法 | `./.codewhale/constitution.json` | JSON | 仓库本地宪法 |
| Fleet 台账 | `./.codewhale/fleet.jsonl` | JSONL | Fleet 状态记录 |

## 延伸阅读

- [核心功能详解](features.md)
- [版本演进记录](changelog.md)
- [CodeWhale 快速上手](quickstart.md)