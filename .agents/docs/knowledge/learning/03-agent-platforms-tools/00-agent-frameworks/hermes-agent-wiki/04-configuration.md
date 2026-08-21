---
id: "hermes-agent-wiki-04-configuration"
title: "04 配置体系"
source: "hermes-agent 源码 cli-config.yaml.example + user-guide/configuration.md + user-guide/profiles.md"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/hermes-agent-wiki/04-configuration.toml"
type: "Wiki Tutorial"
description: "Hermes Agent 配置体系：config.yaml 顶层 section、.env 密钥隔离、HERMES_HOME 环境变量、profiles 多实例、配置优先级"
status: "stable"
category: "learning"
tags: ["hermes", "config", "config-yaml", "env", "profiles"]
date: "2026-08-09"
author: "seven-concepts knowledge-scenario"
summary: "Hermes Agent 用 config.yaml 承载全部非密钥行为配置、.env 只放密钥、HERMES_HOME 定位数据根目录；通过 profiles 支持多实例并行，配置按『CLI 参数 > config.yaml > .env > 内置默认』的优先级解析"
last_verified: "2026-08-09"
wiki_version: "1.0"
---
# 04 配置体系

## 4.1 配置体系总览

Hermes Agent 的配置遵循一条清晰的分层原则：**行为配置进 `config.yaml`，密钥配置进 `.env`**。所有非密钥的行为设置（超时、阈值、功能开关、展示偏好）都写在 YAML 配置文件 `~/.hermes/config.yaml` 中；而 API 密钥、token、密码等敏感凭据只放在 `~/.hermes/.env` 中。

之所以这样分离，是因为配置会被加载进会话上下文甚至系统提示词，若把密钥混入 `config.yaml` 会增加泄露风险，也不利于按环境区分。Hermes 项目的贡献规范明确要求：**禁止为非密钥配置新增 `HERMES_*` 环境变量**——行为设置一律进 `config.yaml`（详见下文 4.6）。

## 4.2 `config.yaml` 顶层 section

`~/.hermes/config.yaml` 是主配置文件，顶层由若干 section（分区/段落）构成。下表基于仓库根目录的 `cli-config.yaml.example`（官方示例模板）归纳，标注其用途（示例模板，具体键名以实际发行版为准）：

| 顶层 section | 用途 |
|-------------|------|
| `database` | 会话数据库（SQLite）相关配置 |
| `model` | 主模型选择、provider 路由、OpenRouter 等 |
| `terminal` | 终端后端（local/docker/ssh/modal 等）与外壳配置 |
| `browser` | 浏览器工具配置 |
| `tool_loop_guardrails` | 工具循环防护（防失控） |
| `compression` | 上下文压缩 |
| `prompt_caching` | 提示词缓存（含 Anthropic 缓存 TTL） |
| `memory` | 持久记忆（内置 MEMORY.md/USER.md 及外部 provider） |
| `session_reset` | 会话重置策略 |
| `streaming` | 网关流式输出 |
| `skills` | 技能系统设置（含 agent 创建技能的写权限门控） |
| `agent` | 代理行为参数 |
| `platform_toolsets` | 按平台启用的工具集 |
| `stt` | 语音转文字（voice transcription） |
| `code_execution` | 代码执行沙箱 |
| `delegation` | 子代理委托（subagent delegation） |
| `display` | 展示与模型别名（display/model aliases） |
| `telemetry` | 遥测（默认需 opt-in） |
| `updates` | 更新行为 |

> 以上 section 名来自 `cli-config.yaml.example` 的顶层键；个别 section（如 `security`、`privacy`、`web` 仪表盘、`external_secret_sources` 等）也见于该文件，此处列出主要部分。具体行为请以发行版文档为准。

## 4.3 `.env` 只用于密钥

`.env` 是环境变量的兜底文件，**主要用途是存放密钥**（API keys、tokens、passwords）。其定位在官方配置优先级说明中明确为：`~/.hermes/.env` 是环境变量的 fallback，且是密钥（API keys、tokens、passwords）的必需位置。

例如 `model` 配置中用到的 provider 密钥，通常通过 `.env` 中的 `ANTHROPIC_API_KEY`、`OPENAI_API_KEY`、`XAI_API_KEY` 等形式提供（示例/需验证——具体变量名以 provider 文档为准）。

**规则**：凡需在多个会话/平台间共享的行为配置都应写入 `config.yaml`，`.env` 只承担密钥。这是 Hermes 的硬性设计约束（见 4.6）。

## 4.4 `HERMES_HOME` 环境变量

`HERMES_HOME` 指定 Hermes 数据根目录，默认值为 `~/.hermes`。它承载：

- 主配置：`$HERMES_HOME/config.yaml`
- 密钥：`$HERMES_HOME/.env`
- 记忆：`$HERMES_HOME/memories/`（内置 MEMORY.md / USER.md）
- 技能：`$HERMES_HOME/skills/`
- 状态库：`$HERMES_HOME/state.db`（会话与 FTS5 全文搜索）
- 身份文件：`$HERMES_HOME/SOUL.md`（主要代理身份）

官方文档强调 `HERMES_HOME` 是 **profile（配置档/实例）** 划分的边界——不同 profile 通过不同的 `HERMES_HOME` 隔离状态。若两个代理进程指向同一个 `HERMES_HOME`，会互相污染记忆，故**一个代理对应一个 Hermes home**。

在终端后端上下文里，`HERMES_HOME` 与真实用户主目录 `HOME` 是分开的：例如 `auto` 模式下工具子进程使用 `{HERMES_HOME}/home` 作为 `HOME`，容器/SSH 等远程后端据此隔离。

## 4.5 profiles 多实例

**profile** 是 Hermes 的配置隔离单元，让同一套安装可以并行运行多个彼此独立的代理实例。核心命令：

```bash
hermes profile create coder        # 创建 profile + 生成 "coder" 命令别名
hermes profile create work --clone # 仅克隆配置（config 等，不含历史）
hermes profile create backup --clone-all  # 克隆全部（配置/密钥/记忆/技能等）
hermes --profile=coder doctor      # 用 -p 临时指定 profile
hermes profile use coder           # 设置 sticky 默认 profile
hermes profile list                # 列出所有 profile 及状态
```

profile 是**刻意隔离的独立小岛**：默认 profile 不向其他 profile 提供运行时配置继承，避免互相耦合；需要"从默认起步"的合法场景用 `--clone` 在创建时拷贝。

profile 与 gateway（网关）也联动——不同 profile 可运行各自独立的 gateway 服务（不同 bot token），并支持 token 锁定与持久化服务管理。

## 4.6 配置优先级

官方配置文档给出了配置的解析优先级（从高到低）：

1. **CLI 参数**——如 `hermes chat --model anthropic/claude-sonnet-4`（单次调用覆盖）
2. **`~/.hermes/config.yaml`**——所有非密钥设置的主配置
3. **`~/.hermes/.env`**——环境变量兜底，密钥必需
4. **内置默认**——未设置时的硬编码安全默认值

**延伸规则**（源自 AGENTS.md 贡献规范）：

- 不新增 `HERMES_*` 环境变量承载非密钥配置；行为设置一律入 `config.yaml`
- `config.yaml` 支持**环境变量替换**（Environment Variable Substitution），可在配置值中引用环境变量
- 密钥只走 `.env`

## 4.7 与集成章节的衔接

本 wiki 系列描述的是 Hermes Agent 自身的能力。若需将 SpecWeave 工作区接入 Hermes，请参见[集成章节](../hermes-agent-integration/README.md)的配置说明与 `x-toml-ref` 侧的 `.toml` 元数据（如需）。

| 上一章 | 目录 | 下一章 |
|--------|------|--------|
| [03 CLI 与斜杠命令](./03-cli-commands.md) | [README](./README.md) | [05 消息网关](./05-messaging-gateway.md) |
