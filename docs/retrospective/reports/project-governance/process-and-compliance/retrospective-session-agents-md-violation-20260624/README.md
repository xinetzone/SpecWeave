+++
id = "retrospective-session-agents-md-violation-20260624-readme"
date = "2026-06-24"
type = "index"
source = "会话内用户纠错记录"
+++

# 复盘报告：AGENTS.md 启动协议违反导致的三重连锁错误

> **复盘对象**：本轮会话（TRAE AI 创造力大赛 FAQ 分析任务）
> **复盘日期**：2026-06-24
> **会话轮次**：6 轮（含 4 轮用户纠错）
> **报告类型**：智能体执行合规性复盘

## 项目概览

### 1.1 核心指标

| 指标 | 数值 |
|------|------|
| 会话总轮次 | 6 轮 |
| 用户纠错轮次 | 4 轮（第 3-6 轮均为纠错） |
| 产出物重新生成次数 | 3 次（DOCX → MD 根目录 → reports/ → 正确路径） |
| 错误类型 | 3 类（格式错误、路径错误、结构错误） |
| 根本原因 | 1 项（跳过 AGENTS.md 启动协议） |
| 最终产出 | 4 个原子化文件，位于正确路径 |

**关键信号**：本轮会话中，智能体在未读取 AGENTS.md 的情况下直接执行任务，导致输出格式（DOCX 而非 Markdown）、文件路径（根目录而非 docs/retrospective/reports/）、文档结构（单文件而非原子化四件套）三重错误，且每轮仅修正表层症状而未触及根因，直至第 5 轮用户明确要求「按照 AGENTS.md 来」后才完成全量修正。

## 子模块导航

| 章节 | 权威来源 | 说明 |
|------|---------|------|
| 执行复盘 | [execution-retrospective.md](execution-retrospective.md) | 全流程 6 轮会话回顾、错误序列时间线 |
| 洞察萃取 | [insight-extraction.md](insight-extraction.md) | 4 项核心洞察、根因分析与系统性反思 |
| 导出建议 | [export-suggestions.md](export-suggestions.md) | 改进措施、行动计划、可复用模式登记 |

## 关联报告

[short-command-patterns.md](../../../../patterns/methodology-patterns/governance-strategy/short-command-patterns.md)、[review-insight-export-loop.md](../../../../patterns/methodology-patterns/retrospective-knowledge/review-insight-export-loop.md)、[convention-driven-creation.md](../../../../patterns/methodology-patterns/governance-strategy/convention-driven-creation.md)
