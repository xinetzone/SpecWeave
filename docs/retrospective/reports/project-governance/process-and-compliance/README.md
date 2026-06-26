+++
id = "process-and-compliance-index"
date = "2026-06-26"
type = "index"
topic = "process-and-compliance"
+++

# 流程与合规治理

> 本主题存放流程与合规治理相关复盘报告，涵盖应用开发工作空间创建、改进建议执行闭环、启动协议合规性等内容。重点记录了双区开发模型、知识闭环机制、以及规范违反复盘的三重连锁错误根因分析。
>
> 本主题共包含 3 份报告，记录了开发流程从建立到合规校验的治理过程。

## 报告列表

| 报告目录 | 日期 | 核心内容 | 子模块导航 |
|---------|------|---------|-----------|
| [retrospective-report-create-apps-directory/](retrospective-report-create-apps-directory/) | 2026-06-23 | apps/应用开发工作空间创建与双区开发生命周期协议 | [README](retrospective-report-create-apps-directory/README.md) · [execution-retrospective.md](retrospective-report-create-apps-directory/execution-retrospective.md) · [insight-extraction.md](retrospective-report-create-apps-directory/insight-extraction.md) · [export-suggestions.md](retrospective-report-create-apps-directory/export-suggestions.md) |
| [retrospective-report-suggestion-execution-and-pattern-import/](retrospective-report-suggestion-execution-and-pattern-import/) | 2026-06-23 | 改进建议执行与模式导入闭环 | [README](retrospective-report-suggestion-execution-and-pattern-import/README.md) · [execution-retrospective.md](retrospective-report-suggestion-execution-and-pattern-import/execution-retrospective.md) · [insight-extraction.md](retrospective-report-suggestion-execution-and-pattern-import/insight-extraction.md) · [export-suggestions.md](retrospective-report-suggestion-execution-and-pattern-import/export-suggestions.md) |
| [retrospective-session-agents-md-violation-20260624/](retrospective-session-agents-md-violation-20260624/) | 2026-06-24 | AGENTS.md启动协议违反复盘，三重连锁错误根因分析 | [README](retrospective-session-agents-md-violation-20260624/README.md) · [execution-retrospective.md](retrospective-session-agents-md-violation-20260624/execution-retrospective.md) · [insight-extraction.md](retrospective-session-agents-md-violation-20260624/insight-extraction.md) · [export-suggestions.md](retrospective-session-agents-md-violation-20260624/export-suggestions.md) |

## 关键流程与模型

| 模型/协议 | 来源报告 | 核心要点 |
|----------|---------|---------|
| 双区开发模型 | retrospective-report-create-apps-directory | .temp/ 高熵探索区 → 质量门禁 → apps/ 低熵稳定区 |
| 应用开发生命周期协议 | retrospective-report-create-apps-directory | 创建→迁移→清理三阶段，含门禁条件 |
| 建议执行闭环 | retrospective-report-suggestion-execution-and-pattern-import | 复盘→洞察→建议→执行→验证→模式沉淀完整闭环 |
| 三重连锁错误 | retrospective-session-agents-md-violation-20260624 | 跳过启动协议导致输出格式、路径、结构三重错误 |

---
[返回项目治理报告索引](../README.md)
