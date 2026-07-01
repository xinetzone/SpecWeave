+++
id = "process-and-compliance-index"
date = "2026-06-26"
type = "index"
topic = "process-and-compliance"
+++

# 流程与合规治理

> 本主题存放流程与合规治理相关复盘报告，涵盖应用开发工作空间创建、改进建议执行闭环、启动协议合规性、阶段守卫、数据安全治理、RACI 责任矩阵，以及短指令跨会话上下文重建等内容。
>
> 本主题共包含 7 份报告，记录了开发流程从建立、执行、校验到上下文恢复的治理演进过程。

## 报告列表

| 报告目录 | 日期 | 核心内容 | 子模块导航 |
|---------|------|---------|-----------|
| [retrospective-report-create-apps-directory/](retrospective-report-create-apps-directory/) | 2026-06-23 | apps/应用开发工作空间创建与双区开发生命周期协议 | [README](retrospective-report-create-apps-directory/README.md) · [execution-retrospective.md](retrospective-report-create-apps-directory/execution-retrospective.md) · [insight-extraction.md](retrospective-report-create-apps-directory/insight-extraction.md) · [export-suggestions.md](retrospective-report-create-apps-directory/export-suggestions.md) |
| [retrospective-report-suggestion-execution-and-pattern-import/](retrospective-report-suggestion-execution-and-pattern-import/) | 2026-06-23 | 改进建议执行与模式导入闭环 | [README](retrospective-report-suggestion-execution-and-pattern-import/README.md) · [execution-retrospective.md](retrospective-report-suggestion-execution-and-pattern-import/execution-retrospective.md) · [insight-extraction.md](retrospective-report-suggestion-execution-and-pattern-import/insight-extraction.md) · [export-suggestions.md](retrospective-report-suggestion-execution-and-pattern-import/export-suggestions.md) |
| [retrospective-session-agents-md-violation-20260624/](retrospective-session-agents-md-violation-20260624/) | 2026-06-24 | AGENTS.md启动协议违反复盘，三重连锁错误根因分析 | [README](retrospective-session-agents-md-violation-20260624/README.md) · [execution-retrospective.md](retrospective-session-agents-md-violation-20260624/execution-retrospective.md) · [insight-extraction.md](retrospective-session-agents-md-violation-20260624/insight-extraction.md) · [export-suggestions.md](retrospective-session-agents-md-violation-20260624/export-suggestions.md) |
| [retrospective-stage-guardrails-logging-20260629/](retrospective-stage-guardrails-logging-20260629/) | 2026-06-29 | 阶段守卫机制落地复盘，沉淀跨阶段拦截、审批与结构化日志治理经验 | [README](retrospective-stage-guardrails-logging-20260629/README.md) · [execution-retrospective.md](retrospective-stage-guardrails-logging-20260629/execution-retrospective.md) · [insight-extraction.md](retrospective-stage-guardrails-logging-20260629/insight-extraction.md) · [export-suggestions.md](retrospective-stage-guardrails-logging-20260629/export-suggestions.md) |
| [retrospective-ai-agent-data-security-governance-20260629/](retrospective-ai-agent-data-security-governance-20260629/) | 2026-06-29 | AI 智能体互联数据安全治理体系建设复盘，覆盖分类分级、脱敏与出境治理 | [README](retrospective-ai-agent-data-security-governance-20260629/README.md) · [execution-retrospective.md](retrospective-ai-agent-data-security-governance-20260629/execution-retrospective.md) · [insight-extraction.md](retrospective-ai-agent-data-security-governance-20260629/insight-extraction.md) · [export-suggestions.md](retrospective-ai-agent-data-security-governance-20260629/export-suggestions.md) |
| [retrospective-raci-governance-matrix-20260629/](retrospective-raci-governance-matrix-20260629/) | 2026-06-29 | RACI 治理责任矩阵落地复盘，建立多命令集角色分工与审批模型 | [README](retrospective-raci-governance-matrix-20260629/README.md) · [execution-retrospective.md](retrospective-raci-governance-matrix-20260629/execution-retrospective.md) · [insight-extraction.md](retrospective-raci-governance-matrix-20260629/insight-extraction.md) · [export-suggestions.md](retrospective-raci-governance-matrix-20260629/export-suggestions.md) |
| [retrospective-short-command-context-rehydration-20260701/](retrospective-short-command-context-rehydration-20260701/) | 2026-07-01 | 短指令在新会话中的上下文重建与参数澄清复盘，补齐“对象/交付”二槽位治理经验 | [README](retrospective-short-command-context-rehydration-20260701/README.md) · [execution-retrospective.md](retrospective-short-command-context-rehydration-20260701/execution-retrospective.md) · [insight-extraction.md](retrospective-short-command-context-rehydration-20260701/insight-extraction.md) · [export-suggestions.md](retrospective-short-command-context-rehydration-20260701/export-suggestions.md) |

## 关键流程与模型

| 模型/协议 | 来源报告 | 核心要点 |
|----------|---------|---------|
| 双区开发模型 | retrospective-report-create-apps-directory | .temp/ 高熵探索区 → 质量门禁 → apps/ 低熵稳定区 |
| 应用开发生命周期协议 | retrospective-report-create-apps-directory | 创建→迁移→清理三阶段，含门禁条件 |
| 建议执行闭环 | retrospective-report-suggestion-execution-and-pattern-import | 复盘→洞察→建议→执行→验证→模式沉淀完整闭环 |
| 三重连锁错误 | retrospective-session-agents-md-violation-20260624 | 跳过启动协议导致输出格式、路径、结构三重错误 |
| 阶段守卫日志治理 | retrospective-stage-guardrails-logging-20260629 | 通过 SG-LOG/PDR-LOG 记录拦截、跳转与审批 |
| 数据安全五层治理 | retrospective-ai-agent-data-security-governance-20260629 | 以规则、角色与流程约束 AI 互联数据风险 |
| RACI 责任矩阵 | retrospective-raci-governance-matrix-20260629 | 为不同命令集建立唯一 A 与可追责责任链 |
| 短指令上下文重建 | retrospective-short-command-context-rehydration-20260701 | 新会话中先补齐“处理对象”“交付形态”再执行短指令 |

---
[返回项目治理报告索引](../README.md)
