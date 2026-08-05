---
id: agency-agents-wiki-10-summary-resources
title: "The Agency 完全指南 — 总结与资源"
source: "https://github.com/msitarzewski/agency-agents"
date: "2026-08-05"
category: "learning"
tags: ["agency-agents", "the-agency", "ai-agent", "summary", "resources", "glossary", "license", "tutorial"]
---

# The Agency 完全指南 — 总结与资源

> 一句话摘要：本章作为教程的收尾，用一句话总结 The Agency 的核心价值、回顾教程要点、给出分角色学习路径，汇总 GitHub 仓库、桌面应用、社区翻译等核心资源，并附一份覆盖核心术语的术语表，助你完成从入门到实战的闭环。

---

## 1. 教程总结

### 1.1 The Agency 的核心价值（一句话）

> **The Agency 是一支由 230+ 个经过生产环境检验、高度专精且富有个性的 AI Agent 组成的「即插即用」专家团队，配合统一转换/安装脚本与多工具集成，让你在 Claude Code、Cursor、Codex 等任意 AI 编程助手中，一键组建可协作、可自定义、可度量成果的 AI 工作力量。**

它的独一无二之处在于——**不是通用的"假装你是专家"提示词，而是结构化、可交付、可复用的 Agent 系统**。

### 1.2 教程要点回顾

本教程共 11 章，从概念到实战逐步深入：

| 章节 | 主题 | 核心要点 |
|------|------|---------|
| 00 | 概述 | 项目定位、230+ Agent、17 部门、16 工具集成 |
| 01 | 文件夹架构 | 顶层文件、divisions.json / tools.json、17 个部门目录 |
| 02 | Agent 文件格式解析 | frontmatter 字段、正文 8 大章节、AI Engineer 实例拆解 |
| 03 | 部门名册 | 17 个部门及标志性 Agent 逐一手册、选型建议 |
| 04 | 脚本体系 | convert.sh / install.sh / lint 系列脚本、CI 校验 |
| 05 | 多工具集成 | per-agent / roster / plugin 三种机制、16 种工具 |
| 06 | 使用示例 | 桌面应用 / Claude Code / 多工具脚本安装与实战场景 |
| 07 | 策略与运行手册 | NEXUS 策略、Playbook/Runbook、多 Agent 编排 |
| 08 | 常见问题解答 | 六大类 FAQ、排查对照表与流程图 |
| 09 | 最佳实践指南 | 选择、安装、使用、自定义、团队落地最佳实践 |
| 10 | 总结与资源（本文） | 概念总结、学习路径、资源清单、术语表 |

---

## 2. 学习路径建议

根据你的角色和目标，选择最适合的路径：

### 🟢 初学者路径（先跑起来）

```
00 概述 → 01 文件夹架构 → 06 使用示例 → 08 FAQ
```

1. 读 [概述](00-overview.md) 理解 The Agency 是什么。
2. 按 [文件夹架构](01-architecture.md) 了解仓库如何组织 Agent。
3. 跟着 [使用示例](06-usage-examples.md) 安装激活第一个 Agent。
4. 遇到问题查 [FAQ](08-faq-troubleshooting.md)。

> 完成此路径后，你能在常用 AI 助手中按需激活 The Agency 的 Agent。

### 🔵 团队 Leader 路径（团队落地）

```
00 → 03 部门名册 → 09 最佳实践 → 07 策略与运行手册 → 05 多工具集成
```

1. 理解 17 个部门的覆盖范围，规划团队选型。
2. 学习 [最佳实践](09-best-practices.md) 的团队落地章节（统一标准、质量门、NEXUS）。
3. 掌握 [策略与运行手册](07-strategy-playbooks.md) 的多 Agent 编排与 Runbook。
4. 用 [多工具集成](05-integrations.md) 统一团队所用工具。

> 完成此路径后，你能为团队建立标准化、可度量、可复用的 Agent 工作体系。

### 🟣 Agent 开发者路径（自定义与贡献）

```
00 → 02 Agent 文件格式 → 05 多工具集成 → 09 自定义章节 → 10 社区资源
```

1. 研究 [Agent 文件格式](02-agent-format.md) 的 frontmatter 与章节模板。
2. 理解 [多工具集成](05-integrations.md)（per-agent/roster/plugin）以兼容各工具。
3. 按 [最佳实践](09-best-practices.md) 自定义与校验。
4. 遵循 Fork + PR 流程贡献回上游，参与社区翻译与讨论。

> 完成此路径后，你能自由扩展 Agent 名册，并反向贡献给社区。

---

## 3. 相关资源链接

### 3.1 核心资源

| 资源 | 链接 | 说明 |
|------|------|------|
| **GitHub 仓库** | [github.com/msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) | 主仓库：Agent 源码、脚本、文档 |
| **桌面应用** | [agencyagents.app](https://agencyagents.app) | 原生桌面应用（macOS/Linux/Windows），一键浏览与安装 |
| **应用下载** | [Releases](https://github.com/msitarzewski/agency-agents-app/releases/latest) | 下载最新版桌面应用 |
| **GitHub Discussions** | [Discussions](https://github.com/msitarzewski/agency-agents/discussions) | 分享使用故事、交流经验 |
| **Issues** | [Issues](https://github.com/msitarzewski/agency-agents/issues) | 报告 bug、请求新 Agent |
| **awesome-openclaw-agents** | [awesome-openclaw-agents](https://github.com/mergisi/awesome-openclaw-agents) | 社区维护的 OpenClaw Agent 集合（源自本仓库） |
| **赞助** | [Sponsor](https://github.com/sponsors/msitarzewski) | 支持项目持续发展 |

> **Mac 用户**可用 Homebrew 快速安装桌面应用：`brew install --cask msitarzewski/agency-agents/agency-agents`。

### 3.2 社区翻译仓库

The Agency 有活跃的社区翻译与本地化生态，由社区独立维护：

| 语言 | 维护者 | 仓库 | 备注 |
|------|--------|------|------|
| 🇨🇳 简体中文 (zh-CN) | @jnMetaCode | [agency-agents-zh](https://github.com/jnMetaCode/agency-agents-zh) | 141 个翻译 Agent + 46 个中国本土原创 |
| 🇨🇳 简体中文 (zh-CN) | @dsclca12 | [agent-teams](https://github.com/dsclca12/agent-teams) | 独立翻译，含 Bilibili/微信/小红书本地化 |
| 🇧🇷 Português (pt-BR) | @jnMetaCode | [agency-agents-pt-BR](https://github.com/jnMetaCode/agency-agents-pt-BR) | 184 个上游 Agent 翻译 |
| 🇷🇺 Русский (ru) | @jnMetaCode | [agency-agents-ru](https://github.com/jnMetaCode/agency-agents-ru) | 184 个上游 Agent 翻译 |
| 🇮🇩 Bahasa Indonesia (id) | @jnMetaCode | [agency-agents-id](https://github.com/jnMetaCode/agency-agents-id) | 184 个上游 Agent 翻译 |
| 🇸🇦 العربية (ar) | @jnMetaCode | [agency-agents-ar](https://github.com/jnMetaCode/agency-agents-ar) | 184 个上游 Agent 翻译 |
| 🇰🇷 한국어 (ko) | @jnMetaCode | [agency-agents-ko](https://github.com/jnMetaCode/agency-agents-ko) | 184 个上游 Agent 全量翻译 |
| 🇯🇵 日本語 (ja-JP) | @sscodeai | [agency-agents-ja](https://github.com/sscodeai/agency-agents-ja) | 281 个日本本地化 Agent + 97 个日本原创 + 27 个工作流 |
| 🇻🇳 Tiếng Việt (vi-VN) | @rodonguyen | [agency-agents](https://github.com/rodonguyen/agency-agents) | 越南语起步本地化（README 与入门文档） |

> 想添加翻译？在 Issues 提一个 issue，官方会把它链接到这份清单。

---

## 4. 许可证说明

The Agency 采用 **MIT 许可证**：

- ✅ **可自由使用**：个人或商业用途均可。
- ✅ **可自由修改**：Fork、自定义、再分发。
- ✅ **无需署名（但推荐）**：署名推荐但不强制。
- 📌 **不附带任何担保**：按"现状"提供，使用者自行承担风险。

> 一句话：这是最宽松的开源许可证之一，你可以放心把 Agent 用在自己的项目甚至商业产品中。

---

## 5. 术语表

以下是本教程中反复出现的核心术语的通俗解释：

| 术语 | 通俗解释 |
|------|---------|
| **Agent** | 一个有专属身份、个性、使命与交付物的 AI 专家角色，本质是一份结构化的 Markdown 定义文件 |
| **部门（Division）** | 按业务领域对 Agent 分组的概念，共 17 个，如 Engineering、Marketing、Security |
| **frontmatter** | Agent 文件顶部的 YAML 元数据块，定义 `name`、`description`、`color`、`emoji` 等属性 |
| **slug** | 用于文件和引用的短横线英文标识，如 `engineering-frontend-developer` |
| **per-agent** | 一种集成机制：每个 Agent 生成一个独立文件/目录，如 Claude Code、Cursor |
| **roster** | 一种集成机制：所有 Agent 合并成一个文件，如 Aider 的 `CONVENTIONS.md`、Windsurf 的 `.windsurfrules` |
| **plugin** | 一种集成机制：构建成一个插件产物而非按 Agent 渲染，如 Hermes，仅 CLI 可装 |
| **convert（convert.sh）** | 把源 Agent 转换为各工具所需格式的脚本，新增/修改 Agent 后需重新运行 |
| **install（install.sh）** | 把转换好的集成文件安装到具体工具目录的脚本 |
| **dry-run** | 只预览安装效果、不实际写入的预览模式，用于安全验证 |
| **NEXUS 策略** | The Agency 提供的多 Agent 协同方法论，用于多个 Agent 并行、编排、分工完成复杂任务 |
| **Playbook** | `strategy/playbooks/` 中的阶段推进方案，phase-0 到 phase-6 覆盖从发现到运营的完整生命周期 |
| **Runbook** | `strategy/runbooks/` 中的场景化执行套路，如 enterprise-feature、incident-response、marketing-campaign |
| **scope** | 安装范围，分为 user（用户级）与 project（项目级），决定 Agent 装到全局目录还是项目目录 |
| **台式应用（Agency Agents）** | agencyagents.app 提供的原生桌面应用，可一键浏览、安装并自动更新 Agent |
| **OpenCode 119 限制** | OpenCode 上游 bug（issue #27988）导致运行时只注册约 119 个 Agent，需用子集规避 |
| **质量门（Quality Gate）** | 一组验收指标，只有达到标准的交付才被放行，常由 Reality Checker 等质检 Agent 把关 |

---

## 6. 结语

The Agency 把"搭建一支 AI 专家团队"这件事，从**手写提示词**升级为**结构化、可复用、可协作的工程实践**。无论你是个人开发者想快速获得一个专精助手，还是团队 Leader 想统一团队的 AI 工作力量，这里都有一份开箱即用、且永远可自定义的答案。

**下一步行动**：

1. 试试 [桌面应用](https://agencyagents.app) 或脚本，装上你需要的 Agent。
2. 组合 2-3 个 Agent 跑通一个真实小任务。
3. 复用官方 Use Cases 与 Runbook，逐步搭建你的工作流水线。
4. 在 [Discussions](https://github.com/msitarzewski/agency-agents/discussions) 分享你的成果，或 Fork + PR 贡献一个 Agent。

> 🎭 The Agency：你的 AI 梦之队，只等你召唤。

---

## 7. 本教程完整导航

| 章节 | 标题 | 链接 |
|------|------|------|
| 00 | 概述 | [00-overview.md](00-overview.md) |
| 01 | 文件夹架构 | [01-architecture.md](01-architecture.md) |
| 02 | Agent 文件格式解析 | [02-agent-format.md](02-agent-format.md) |
| 03 | 部门名册 | [03-roster-divisions.md](03-roster-divisions.md) |
| 04 | 脚本体系 | [04-scripts-tooling.md](04-scripts-tooling.md) |
| 05 | 多工具集成 | [05-integrations.md](05-integrations.md) |
| 06 | 使用示例 | [06-usage-examples.md](06-usage-examples.md) |
| 07 | 策略与运行手册 | [07-strategy-playbooks.md](07-strategy-playbooks.md) |
| 08 | 常见问题解答 | [08-faq-troubleshooting.md](08-faq-troubleshooting.md) |
| 09 | 最佳实践指南 | [09-best-practices.md](09-best-practices.md) |
| 10 | 总结与资源（本文） | [10-summary-resources.md](10-summary-resources.md) |

---

- [上一章：最佳实践指南](09-best-practices.md)