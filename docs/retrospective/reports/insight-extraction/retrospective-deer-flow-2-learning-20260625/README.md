+++
id = "retrospective-deer-flow-2-learning-20260625-readme"
date = "2026-06-25"
type = "index"
source = ".temp/AI/deer-flow-notes.md"
+++

# DeerFlow 2.0 学习笔记·技术洞察复盘

> **分析对象**：`deer-flow-notes.md`（`.temp/AI/` 临时学习笔记，已清理）学习笔记
> **复盘日期**：2026-06-25
> **任务类型**：开源 Agent 框架技术学习与架构对比
> **报告类型**：技术洞察分析型复盘报告

## 项目概览

### 核心指标

| 指标 | 数值 |
|------|------|
| 笔记章节数 | 10 个（概述/概念/快速开始/核心特性/模型/Python Client/文档/许可证/疑问/总结） |
| 笔记行数 | 220 行 |
| 核心组件 | 5 个（Sub-agents/Memory/Sandbox/Skills/Tools） |
| 部署模式 | 3 种（本地/Docker/Docker+K8s） |
| IM 集成渠道 | 3 个（Telegram/Slack/Feishu） |
| 推荐模型 | 3 个（Doubao-Seed-2.0-Code/DeepSeek v3.2/Kimi 2.5） |

**关键发现**：DeerFlow 2.0 是字节跳动开源的 super agent harness，定位为"让 agents 把事情做完的运行时基础设施"。它从 Deep Research 框架演进而来，2.0 版本彻底重写，采用 Sub-agents 并行执行 + Sandbox 隔离 + 长期记忆 + 按需加载 Skills 的架构设计，基于 LangGraph/LangChain 构建，提供开箱即用的完整能力，同时支持高度自定义扩展。

## 子模块导航

| 章节 | 说明 |
|------|------|
| [execution-retrospective.md](execution-retrospective.md) | 执行过程复盘：笔记结构分析、学习路径回顾、关键技术点识别 |
| [insight-extraction.md](insight-extraction.md) | 洞察萃取：Harness 架构模式、Skills 系统设计、Context Engineering、Sandbox 隔离机制、与 SpecWeave 架构对比 |
| [export-suggestions.md](export-suggestions.md) | 导出建议：可复用架构模式、SpecWeave 可借鉴点、后续研究方向 |

## 关联报告

- [retrospective-ai-code-assistant-project-analysis-20260625/](../retrospective-ai-code-assistant-project-analysis-20260625/) — AI 编程学习助手项目分析复盘
- [retrospective-trae-contest-preliminary-guide-learning-20260625/](../../competitive-analysis/retrospective-trae-contest-preliminary-guide-learning-20260625/) — TRAE 大赛初赛指南学习复盘
- [review-insight-export-loop.md](../../../patterns/methodology-patterns/review-insight-export-loop.md) — 复盘-洞察-导出闭环模式
