---
id: "karpathy-llm-coding-guidelines-tutorial"
title: "Karpathy LLM 编程准则完整教程"
category: learning
tags: [karpathy, llm, coding, agent, guidelines, claude, ai-programming, agentic-engineering, claude-code, cursor, skills, plugin, mdc, multica, multica-cli, managed-agents]
date: "2026-07-02"
status: stable
author: "新智元 & multica-ai"
summary: "源自Andrej Karpathy对LLM编程陷阱观察的四条行为准则（编码前先思考/简约至上/精确编辑/目标驱动），一个CLAUDE.md文件管住AI编程最常犯的毛病。GitHub 61.6k星项目完整教程，包含背景故事、核心原则详解、真实代码正反例、四种分发格式安装指南（CLAUDE.md/Cursor Rules/SKILL.md/插件）、Multica平台架构与multica-cli Skill使用指南、仓库文件结构说明，以及在SpecWeave项目中的整合情况。本文档已原子化，详细内容见 karpathy-llm-coding-guidelines/ 子目录。"
source: "https://www.36kr.com/p/3774954488349441 + https://github.com/multica-ai/andrej-karpathy-skills + https://github.com/multica-ai/multica + https://github.com/multica-ai/multica-cli"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/knowledge/learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines-tutorial.toml"
---
# Karpathy LLM 编程准则完整教程

> **原文标题**：《一个毫无代码的文本，竟连霸GitHub热榜第一。Karpathy的编程神技被化作「AI紧箍咒」，让乱写Bug的大模型瞬间老实！》
> **来源 URL**：https://www.36kr.com/p/3774954488349441
> **公众号**：新智元
> **发布日期**：2026-04-20
> **GitHub 仓库**：https://github.com/multica-ai/andrej-karpathy-skills（61.6k stars）

---

## 一、概述

2026年4月，一个毫无代码的 Markdown 配置文件 `CLAUDE.md` 冲爆了整个 GitHub：本周新增 44,465 颗星，总星数 61.6k，连续三天 Trending 日榜第一。

它源自 Andrej Karpathy 对 LLM 编程陷阱的观察，由华人开发者 Jiayuan Zhang（Multica 创始人兼 CEO）提炼为四条简洁的行为准则，相当于在 Agent 脑子里装了一套"紧箍咒"：

| 原则 | 口诀 | 解决什么问题 |
|------|------|-------------|
| **编码前先思考** | 不确定的先问别瞎猜 | 错误假设、隐藏困惑、缺少权衡 |
| **简约至上** | 代码能简短就别写长 | 过度复杂、臃肿抽象、过度设计 |
| **精确编辑** | 没让你改的地方别碰 | 无关编辑、顺手重构、触碰不应改的代码 |
| **目标驱动** | 给目标别给步骤 | 缺乏验证、需要不断介入澄清 |

本仓库提供**四种分发格式**适配不同工具：CLAUDE.md（Claude Code）、.cursor/rules（Cursor）、SKILL.md（Agent Skill）、.claude-plugin（插件市场）。同时也是 **Multica 平台** 的标准 Skill——可直接导入 Multica 让 Agent 团队全员遵守。

把配置放进项目，AI 编程 Agent 就会自动读取并遵守里面的规则。正如 Karpathy 所说：

> "LLM 非常擅长循环执行直到达成特定目标……不要告诉它该做什么，给它成功标准，然后看着它完成。"

---

## 二、核心背景

故事始于 2026 年 1 月 26 日，Karpathy 在 X 上发长帖吐槽 AI 编程 Agent 的三大通病：

1. **乱猜不提问**：模型会代你做错误假设，然后不假思索地执行，不寻求澄清、不展示权衡
2. **过度设计**：明明 100 行能搞定的事情，非要实现成 1000 行的臃肿架构
3. **顺手乱改**：改动或删除与任务无关的代码和注释

Karpathy 自己的工作流已经从「80% 手写 + 20% AI 辅助」翻转成了「80% 交给 Agent + 20% 自己修补」，但他也预言了 **Slopacolypse**（低质量内容灾难）——AI 生成的低质量代码会大量涌现。

这个项目之所以火，核心在于它把顶级工程师的隐性知识打包成了 Agent 可以直接读取的格式：Karpathy 不再只是一个你读的人，而是一个你的 Agent 可以直接继承行为的人。

**作者 Jiayuan Zhang 同时是 Multica 的创始人**——Multica 是开源的 Managed Agents 平台，将编码 Agent 变成真正的队友（分配任务、跟踪进度、积累技能）。Karpathy 准则是 Multica Skill 生态的第一个明星项目。

---

## 三、文档导航

本文档已原子化为多个子文件，详细内容见 [karpathy-llm-coding-guidelines/](karpathy-llm-coding-guidelines/README.md) 子目录：

### 第一部分：Karpathy 准则核心

| 章节 | 内容 |
|------|------|
| [00 - 概述与背景](karpathy-llm-coding-guidelines/00-overview.md) | 故事背景、三大问题、Agentic Engineering 概念、作者介绍 |
| [01 - 四条核心原则详解](karpathy-llm-coding-guidelines/01-four-principles.md) | 每条原则的详细说明、具体要求、检验标准 + CLAUDE.md 英文原文 |
| [02 - 真实代码正反例](karpathy-llm-coding-guidelines/02-code-examples.md) | Python 代码示例，❌ 错误做法 vs ✅ 正确做法，含反模式总结 |

### 第二部分：安装与使用

| 章节 | 内容 |
|------|------|
| [03 - 快速上手指南](karpathy-llm-coding-guidelines/03-quickstart.md) | **四种安装方式**：插件市场、CLAUDE.md、Cursor Rules(.mdc)、Agent Skill(SKILL.md)；Claude Code vs Cursor 对比；贡献者同步指南；项目定制示例 |

### 第三部分：Multica 生态（上下文补充）

| 章节 | 内容 |
|------|------|
| [06 - Multica 平台介绍](karpathy-llm-coding-guidelines/06-multica-platform.md) | **Multica 开源 Managed Agents 平台**：核心概念词典、系统架构、功能模块（Agent/Runtime/Daemon/Skill/Autopilot/Squad/Chat/Inbox）、与 Karpathy 准则的关系、5步快速开始 |
| [07 - Multica CLI Skill 使用指南](karpathy-llm-coding-guidelines/07-multica-cli-skill.md) | **multica-cli Skill 详解**：让外部 Agent（Claude Code/Cursor/Codex）安全操作 Multica；安装方法、安全启动流程、完整命令参考、读写工作流、Mention 副作用处理、安全检查清单、具体示例 |

### 第四部分：整合与资源

| 章节 | 内容 |
|------|------|
| [04 - SpecWeave 项目整合](karpathy-llm-coding-guidelines/04-specweave-integration.md) | 本项目如何整合这些准则、对应规范文件位置、团队使用指南 |
| [05 - 资源与参考](karpathy-llm-coding-guidelines/05-resources.md) | **仓库文件结构树**、关键文件对照表、官方资源链接、原帖、相关概念（MDC/Skill格式）、关键语录 |

---

## 四、四种分发格式速查

| 格式 | 文件位置 | 适用工具 | 作用范围 | Frontmatter |
|------|---------|---------|---------|-------------|
| **CLAUDE.md** | 项目根目录 | Claude Code、Codex CLI | 单项目 | 无 |
| **Cursor Rules** | `.cursor/rules/*.mdc` | Cursor 编辑器 | 单项目 | `description`, `alwaysApply: true` |
| **Agent Skill** | `skills/.../SKILL.md` | Claude Code插件、支持Skills的工具、Multica平台 | 跨项目 | `name`, `description`, `license` |
| **Claude Plugin** | `.claude-plugin/` | Claude Code | 跨项目 | JSON配置（plugin.json + marketplace.json） |

> 💡 **提示**：Cursor 默认**不**读取 `CLAUDE.md`，必须通过 `.cursor/rules/` 配置。Multica 平台会自动把 Skill 注入到 Agent 工作目录的对应位置。详见 [03 - 快速上手指南](karpathy-llm-coding-guidelines/03-quickstart.md)。

---

## 五、Multica 生态速览

Karpathy 准则是 Multica Skill 生态的标杆项目。Multica 是开源的 AI Agent 协作管理平台：

**核心理念**：把编码 Agent 变成真正的队友——和人共用同一个 Issue 看板，有名字、有头像、能被分配任务、能汇报进度、能积累技能。

| 组件 | 作用 |
|------|------|
| **Agent** | AI 工作者身份（绑定 Runtime、Provider、Instructions、Skills） |
| **Runtime & Daemon** | 本地守护进程，自动探测 CLI、认领任务、隔离执行 |
| **Skill** | 可复用说明文档（Karpathy 准则就是一个 Skill），任务开始时注入上下文 |
| **Autopilot** | 定时/Webhook 自动触发 Agent 开工（日报、Bug Triage、安全扫描） |
| **Squad** | Agent + 人组成小队，由 Leader 路由任务 |
| **multica-cli** | CLI 工具 + Skill，让外部 Agent 安全读写 Issue、回复评论 |

> 架构关键：Server 不直接调用 LLM，Agent 在用户本地机器上执行，代码和密钥不出你的设备。详见 [06 - Multica 平台介绍](karpathy-llm-coding-guidelines/06-multica-platform.md)。

---

## 六、一分钟速查表

| 原则 | 反例 | 正例 |
|------|------|------|
| **编码前先思考** | 你说"加验证"，AI直接写全套企业级认证 | "请问需要验证什么？有几种理解方式：[列出选项]" |
| **简约至上** | 要个Hello World，给你搭微服务架构 | 50行能解决就不写200行；只用一次的代码不抽象 |
| **精确编辑** | 让修bug，结果重构整个模块删了你注释 | 只改该改的行；匹配现有风格；无关问题只提不改 |
| **目标驱动** | "写个函数实现X"，结果不对你也不知道 | "先写测试用例，然后让所有测试通过" |

---

## 七、SpecWeave 整合情况

SpecWeave 项目已将四条准则整合到现有规范体系中：

- **歧义主动澄清** → [global-core-rules.md](../../../../global-core-rules.md)
- **简约设计原则** → [development-standards.md](../../../development-standards.md)
- **外科手术式精确编辑** → [developer.md](../../../../roles/developer.md)
- **完整规则文档（含速查表）** → [ai-coding-guidelines.md](../../../../rules/ai-coding-guidelines.md)
