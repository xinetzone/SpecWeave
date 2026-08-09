---
id: "hermes-agent-wiki-11-glossary-faq-resources"
title: "11 术语表 / FAQ / 资源"
source: "NousResearch/hermes-agent 本地源码仓库（website/docs/reference/faq.md、environment-variables.md；README.zh-CN.md）"
type: "Wiki Tutorial"
description: "Hermes Agent 术语表、常见问题 FAQ 与官方资源链接，含相关 wiki 交叉引用"
status: "stable"
category: "learning"
tags: ["hermes", "glossary", "faq", "resources"]
date: "2026-08-10"
author: "hermes-agent-wiki knowledge-scenario"
summary: "术语速查（Hermes、prompt caching、toolset、memory provider、skill、plugin、context engine、gateway、delegation、honcho 等）、FAQ 与官方资源导航"
last_verified: "2026-08-10"
wiki_version: "1.0"
---
# 11 术语表 / FAQ / 资源

## 11.1 术语表

| 术语 | 含义 |
|------|------|
| **Hermes** | Nous Research 构建的自进化 AI Agent（本 Wiki 主角），MIT 许可 |
| **AIAgent** | 核心循环类（`run_agent.py`），服务 CLI/gateway/ACP 等所有入口 |
| **prompt caching** | 提示词缓存——复用相同前缀提示词的缓存以降低每次 API 调用成本；Hermes 视其为"神圣不可破坏"（见[00 总览](00-overview.md)） |
| **toolset** | 工具集——按平台/场景分组的工具集合（`toolsets.py`），约 28 个 |
| **tool** | 工具——模型可调用的原子能力（`tools/`，每工具一文件），70+ 个 |
| **memory provider** | 记忆提供者插件——叠加于内置记忆之上的外部记忆后端（Honcho/OpenViking 等，见[08 记忆系统](08-memory.md)） |
| **skill** | 技能——沉淀可复用步骤的 `SKILL.md` 程序性指令，随使用自改进 |
| **plugin** | 插件——外置目录的扩展模块，经 `plugin.yaml` + `register(ctx)` 注入能力（见[10 架构解析](10-architecture-source.md)） |
| **context engine** | 上下文引擎插件——替换内置上下文压缩的机制，单实例 |
| **footprint ladder** | 占用阶梯——评估改动占用的优先级（扩展现有代码 < CLI+技能 < 服务门控工具 < 插件 < MCP < 新增核心工具） |
| **gateway** | 消息网关——长驻进程，统一 25+ 平台适配器与授权、cron、hook（见[10 架构解析](10-architecture-source.md)） |
| **delegation** | 委派——经 `delegate_task` 派生隔离子代理并行工作（见[09 扩展能力](09-extensions-cron-delegation.md)） |
| **honcho** | AI 原生记忆后端，辩证式用户建模（见[08 记忆系统](08-memory.md)） |
| **MCP** | Model Context Protocol，模型上下文协议——连接外部工具服务器的开放协议（见[09 扩展能力](09-extensions-cron-delegation.md)） |
| **cron** | 定时调度机制——自然语言或 cron 表达式安排任务自动运行 |
| **FTS5** | SQLite 内置全文检索——支撑 Hermes 会话搜索 |
| **profile** | 画像——每个画像（`hermes -p <name>`）拥有独立的 HERMES_HOME/记忆/会话/网关 PID |

## 11.2 FAQ（基于官方 faq.md）

**如何切换模型？** 运行 `hermes model` 交互选择，或直接编辑 `~/.hermes/.env`；设置会持久化到 `config.yaml`。`/model` 斜杠命令在会话内切换（CLI 与 gateway 共享逻辑，见 `hermes_cli/model_switch.py`）。

**本地 / 离线模型能用吗？** 可以。`hermes model` 选 **Custom endpoint** 输入本地服务器 URL，或直接在 `config.yaml` 设 `model.provider: custom` + `base_url`。兼容 Ollama、vLLM、llama.cpp、SGLang 等。注意：本地服务器上下文窗口需匹配（Hermes 最小约 64,000）。

**数据会被发送到别处吗？** API 调用**仅**发往你配置的 LLM provider；Hermes 本身**不收集遥测/用量/分析数据**。对话、记忆、技能均本地存于 `~/.hermes/`。

**费用多少？** Hermes 本身**免费开源**（MIT）；仅需为所选 provider 的 LLM API 用量付费，本地模型完全免费。

**多人能用同一实例吗？** 可以。消息网关让多用户经 Telegram、Discord、Slack、WhatsApp、Home Assistant 与同一实例交互，通过 allowlist 与 DM 配对控制访问。

**能在自己的 Python 项目里用吗？** 可以。导入 `AIAgent` 并编程式使用：

```python
from run_agent import AIAgent
agent = AIAgent(model="anthropic/claude-opus-4.7")
response = agent.chat("Explain quantum computing briefly")
```

**`hermes: command not found`？** 安装后 shell 未刷新 PATH——`source ~/.bashrc` 或开新终端；验证 `which hermes` / `ls ~/.local/bin/hermes`。安装器会把 `~/.local/bin` 加入 PATH。

**Python 版本太旧？** Hermes 要求 Python 3.11+，安装器会自动处理；手动安装前先 `python3 --version` 确认。

## 11.3 资源链接

- **官方文档**：https://hermes-agent.nousresearch.com/docs/
- **GitHub 仓库**：https://github.com/NousResearch/hermes-agent
- **社区/支持**：Nous Research Discord（`#plugins-skills-and-skins` 等频道）——Discord 链接见仓库 README
- **中文说明**：仓库 `README.zh-CN.md`

## 11.4 相关 Wiki 交叉引用

- [Hermes Agent 集成指南](../hermes-agent-integration/README.md) — 如何把 SpecWeave 能力/知识库接入 Hermes（插件路径 + OKF 记忆层）
- [Hermes OKF Wiki 教程](../../01-agent-protocols-interfaces/okf-wiki/README.md) — OKF 开放知识格式，Hermes 记忆层常配合使用
- 本 Wiki 其余章节：[00 总览](00-overview.md) · [01 核心特性](01-core-features.md) · [08 记忆系统](08-memory.md) · [09 扩展能力](09-extensions-cron-delegation.md) · [10 架构解析](10-architecture-source.md)
