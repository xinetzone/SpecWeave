---
id: "hermes-agent-wiki-06-tools-toolsets"
title: "06 工具与工具集"
source: "hermes-agent 源码 tools/ + reference/tools-reference.md + reference/toolsets-reference.md + AGENTS.md + user-guide/features/tools.md"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/hermes-agent-wiki/06-tools-toolsets.toml"
type: "Wiki Tutorial"
description: "Hermes Agent 工具与工具集：40+ 内置工具、TOOLSETS 工具集系统、Footprint Ladder 决策、服务门控 check_fn、终端后端"
status: "stable"
category: "learning"
tags: ["hermes", "tools", "toolsets", "footprint-ladder"]
date: "2026-08-09"
author: "seven-concepts knowledge-scenario"
summary: "Hermes 内置 40+ 模型工具并按工具集（toolset）组织，可按平台启停；新能力按 Footprint Ladder 决策（扩展→CLI+skill→service-gated check_fn→plugin→MCP→core tool），核心保持窄腰设计"
last_verified: "2026-08-09"
wiki_version: "1.0"
---
# 06 工具与工具集

## 6.1 工具与工具集的概念

**工具（tool）** 是扩展代理能力、可在模型调用中被执行的函数（model tool）；**工具集（toolset）** 是把若干相关工具逻辑分组、可整体启用或禁用的单元。Hermes 用工具集来管理庞大工具注册表：按平台/会话配置启用哪些工具集，从而控制模型可见的工具面。

**核心设计哲学（窄腰，narrow waist）**：每个模型工具都会在每次 API 调用中随 schema 发送，因此**核心工具的新增门槛很高**——新增能力应优先放在边缘（CLI 命令 + skill、服务门控工具、插件），而非扩展核心工具面（见 6.5 Footprint Ladder）。

## 6.2 内置工具（40+）

Hermes 内置 **40+ 个工具**（官方 `tools-reference.md` 逐条列出），覆盖：网页搜索、浏览器自动化、终端执行、文件编辑、记忆、委托、定时任务、Home Assistant 等。常见内置工具示例：

| 工具 | 用途 |
|------|------|
| `read_file` / `write_file` / `patch` / `search_files` | 文件读写与搜索（替代 cat/sed/grep 等） |
| `web_search` / `browser_navigate` | 网页搜索与浏览器导航 |
| `terminal` | 终端命令执行 |
| `memory` | 持久记忆管理（add/replace/remove） |
| `session_search` | 历史会话全文检索 |
| `delegation` | 子代理委托 |
| `cronjob` | 定时任务 |

> 具体工具清单会随版本演进，权威代码派生的完整清单见官方 `tools-reference.md` 与 `toolsets-reference.md`，此处仅列代表性示例。

## 6.3 工具集系统（TOOLSETS）

工具集按类别组织。官方 `toolsets-reference.md` 将工具集分为三类：

- **核心工具集（Core Toolsets）**：基础能力，如 `web`、`search`、`terminal`、`file`、`browser`、`vision`、`image_gen`、`skills`、`tts`、`todo`、`memory`、`session_search`、`cronjob`、`code_execution`、`delegation`、`clarify`、`safe` 等
- **平台工具集（Platform Toolsets）**：按平台预设，如 `hermes-cli`、`hermes-telegram` 等
- **动态工具集（Dynamic Toolsets）**：运行时生成的，如 MCP server 工具集（`mcp-<server>`）、插件工具集、自定义工具集、通配符（wildcards）等

**启用方式**：

```bash
hermes chat --toolsets "web,terminal"   # 会话级指定工具集
# 平台级：在 config.yaml 的 platform_toolsets 中按平台配置
```

也可用 `hermes tools` 交互式管理工具与工具集（启用/禁用）。全局工具集可通过配置整体禁用（Global Toolset Disable）。

## 6.4 终端后端

**终端工具**需要一个后端来执行命令，支持多种远程/沙箱后端：local（本机）、docker（容器）、ssh（远程）、modal（无服务器云）、daytona、vercel sandbox、singularity/apptainer 等。`config.yaml` 的 `terminal` section 配置后端类型与相关选项（`~/.hermes/config.yaml` 中 `auto` 模式用 `{HERMES_HOME}/home` 作为工具子进程的 `HOME`）。

终端后端还支持后台进程管理、sudo 支持、容器安全与卷挂载等。

## 6.5 Footprint Ladder：新能力决策

Hermes 用 **Footprint Ladder（足迹阶梯）** 决定一项新能力应以何种"永久表面积"接入核心。每一级比上一级增加更多永久表面积，**选择能正确解决问题的最高的（足迹最小）一级**：

1. **扩展现有代码**——能力是既有功能的变体，零新增表面积
2. **CLI 命令 + skill**——能力可表达为 shell 命令并受 skill 引导，模型零足迹；默认选项（如 `hermes webhook`、`hermes cron`、`hermes tools`）
3. **服务门控工具（`check_fn`）**——需要结构化参数/返回值，且**仅在前提配置就绪时出现**，否则零足迹
4. **插件（Plugin）**——第三方/小众/用户特定能力，不进入核心，运行时发现
5. **MCP server（在目录中）**——确需作为工具但非核心基础时，优先做成 MCP server 加入 MCP 目录
6. **新核心工具**——仅当能力基础、对几乎所有用户通用、且终端+文件（或 MCP server）无法触达时才新增（正确例子：terminal、read_file、web_search、browser_navigate）

> 当 3+ 个开放 PR 要集成同一*类别*的能力（memory 后端、provider、notifier）时，应设计一个 ABC + 编排器，把内置实现作为首个 provider，其余竞争者转成针对该接口的插件，而不是逐个合并。

## 6.6 服务门控工具（`check_fn`）

**服务门控工具**是 Footprint Ladder 第 3 级的关键机制：工具通过 `check_fn` 判断其服务前提是否就绪，**未就绪时该工具从 schema 中剥离**，模型根本看不到它，从而零足迹。官方 AGENTS.md 明确举例：

- **Home Assistant 工具**——以 token 为门控前提
- **memory-provider 工具**——以外部 memory provider 是否激活为门控前提

另有官方文档提到的 x_search（X/Twitter 搜索）以 xAI 凭据为门控，默认关闭，需通过 `hermes tools` 显式开启。

## 6.7 表面能力是会话属性

一条重要设计约束：**表面能力（surface capability）是会话（session）的属性，而非进程环境变量的属性**。一个工具之所以可用，取决于*连接的另一端是谁*（桌面应用的窗格、应用内浏览器、消息回复、Projects），因此其可用性必须从**会话自身来源**解析，而非从后端进程的环境变量解析。任何以环境变量键控的 GUI 门控在后端其他拓扑下会成为静默空操作（工具在模型看到之前就被剥离）。

| 上一章 | 目录 | 下一章 |
|--------|------|--------|
| [05 消息网关](./05-messaging-gateway.md) | [README](./README.md) | [07 技能系统](./07-skills.md) |
