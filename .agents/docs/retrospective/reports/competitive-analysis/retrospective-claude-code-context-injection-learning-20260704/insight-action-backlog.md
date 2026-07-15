---
title: Claude Code 上下文注入机制深度分析复盘 - 洞察行动项 Backlog
version: "1.0"
date: 2026-07-06
type: insight-action-backlog
source: "external: 模板引用-comprehensive-retrospective-template/insight-action-backlog.md"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/reports/competitive-analysis/retrospective-claude-code-context-injection-learning-20260704/insight-action-backlog.toml"
project: retrospective-claude-code-context-injection-learning-20260704
template_upgrade: 2026-07-06（模板v1.2补建）
ssot:
  suggestions_source: export-suggestions.md
  insight_source: insight-extraction.md
---
# 洞察行动项 Backlog

> 本文件记录从本次复盘洞察和改进建议转化的可执行行动项。当前行动项均待执行。

## 行动项总览

| ID | 来源 | 标题 | 优先级 | 状态 | DoD（完成定义） | 完成日期 |
|---|---|---|---|---|---|---|
| IMP-001 | 行动项§高优 | 规范体系审查（事实-流程-护栏分类） | 高 | ⏳ 待执行 | 完成审查并输出审查报告，列出需要调整的内容清单（如有） | - |
| IMP-002 | 行动项§高优 | 对抗验证模式试点 | 高 | ⏳ 待执行 | 完成至少1次试点，记录单窗口自检 vs 对抗验证的质量对比结果 | - |
| IMP-003 | 行动项§中优 | 子代理委派规范更新 | 中 | ⏳ 待执行 | 更新subagent-atomic-task-template.md，纳入任务粒度原则、完整内容返回要求、截断兜底策略 | - |
| IMP-004 | 行动项§中优 | 长会话关键决策备份机制 | 中 | ⏳ 待执行 | 完成PreCompact备份机制可行性分析，如可行则实现 | - |
| IMP-005 | 行动项§低优 | 路径限定Rules机制研究 | 低 | ⏳ 待执行 | 完成目录局部规范自动加载机制设计方案 | - |
| IMP-006 | 行动项§低优 | 模式正式入库 | 低 | ⏳ 待执行 | 2个L2成熟度模式文件创建，索引更新 | - |
| IMP-007 | 知识沉淀§1.1 | 结构化学习笔记沉淀 | 中 | ⏳ 待执行 | 学习笔记整理为Markdown知识条目归档至docs/knowledge/learning/，含核心概念速查表、8种机制对比矩阵、Hooks速查表、6种编排模式、误区对照表、决策指南、10条最佳实践 | - |

## 行动项详情

### IMP-001: 规范体系审查（事实-流程-护栏分类）
- **优先级**: 高
- **来源**: 行动项§高优
- **执行方案**: 使用"事实-流程-护栏-隔离任务"四象限框架审查现有 `.agents/` 规范体系，包括：AGENTS.md和全局核心规则审查、"必须/禁止"类约束审查、Skills体系审查
- **DoD**: 完成审查并输出审查报告，列出需要调整的内容清单（如有）
- **执行结果**: -
- **产出物**: -（审查报告待创建）
- **提交**: -

---

### IMP-002: 对抗验证模式试点
- **优先级**: 高
- **来源**: 行动项§高优
- **执行方案**: 选择1-2个高质量要求任务（如代码审查、规范符合性检查）试点Adversarial verification模式：执行agent完成任务后，委派独立验证agent在新上下文中验证结果；验证agent只接收输出结果和验收标准，不接收执行过程；对比单窗口自检 vs 对抗验证的结果质量差异
- **DoD**: 完成至少1次试点，记录质量对比结果
- **执行结果**: -
- **产出物**: -（试点记录待创建）
- **提交**: -

---

### IMP-003: 子代理委派规范更新
- **优先级**: 中
- **来源**: 行动项§中优
- **执行方案**: 更新子代理委派规范和模板：在subagent任务模板中增加"返回完整详细内容，不要摘要性总结"的明确要求；明确任务粒度原则：一次委派一个原子Task，不合并多个不相关子任务；增加兜底策略：若子代理返回摘要/截断，主会话应基于已有内容整合而非反复重试
- **DoD**: 更新subagent-atomic-task-template.md，纳入上述原则
- **执行结果**: -
- **产出物**: -（待更新模板文件）
- **提交**: -

---

### IMP-004: 长会话关键决策备份机制
- **优先级**: 中
- **来源**: 行动项§中优
- **执行方案**: 研究PreCompact备份机制在SpecWeave中的实现可能：长会话（超过一定轮次或token量）中，在上下文压缩前自动备份关键决策、TODO、约束到文件；参考Claude Code的PreCompact Hook设计
- **DoD**: 完成可行性分析，如可行则实现
- **执行结果**: -
- **产出物**: -（可行性分析报告待创建）
- **提交**: -

---

### IMP-005: 路径限定Rules机制研究
- **优先级**: 低
- **来源**: 行动项§低优
- **执行方案**: 研究目录局部规范自动加载机制：当智能体访问特定目录（如`vendor/`、`.agents/scripts/`）时，自动加载该目录下的局部规范文件；减少全局上下文不必要的内容占用
- **DoD**: 完成设计方案
- **执行结果**: -
- **产出物**: -（设计方案待创建）
- **提交**: -

---

### IMP-006: 模式正式入库
- **优先级**: 低
- **来源**: 行动项§低优
- **执行方案**: 将L2成熟度的2个模式正式入库到patterns目录：上下文生命周期分层管理、架构优先于提示；对抗验证工作流先作为L1候选模式记录
- **DoD**: 模式文件创建，索引更新
- **执行结果**: -
- **产出物**: -（待创建模式文件）
- **提交**: -

---

### IMP-007: 结构化学习笔记沉淀
- **优先级**: 中
- **来源**: 知识沉淀§1.1
- **执行方案**: 将对话中已完成的结构化学习笔记（核心概念速查表、8种机制对比矩阵、Hooks速查表、6种编排模式、误区对照表、决策指南、10条最佳实践）整理为Markdown知识条目归档至docs/knowledge/learning/
- **DoD**: 学习笔记整理完成并归档，标签：`claude-code`, `context-injection`, `agent-engineering`, `skills`, `subagents`, `hooks`, `dynamic-workflows`
- **执行结果**: -
- **产出物**: -（待创建知识条目）
- **提交**: -

## 已完成项

- ✅ 微信公众号双路径决策：此前复盘已沉淀为 [wechat-mp-content-extraction.md](../../../../knowledge/operations/wechat-mp-content-extraction.md)，本次验证了defuddle首选策略的有效性

## 执行记录

| IMP-ID | 完成日期 | 提交/变更 | 执行结果 |
|---|---|---|---|
| - | - | - | 所有行动项待执行 |

## Changelog

- 2026-07-06 | create | 模板v1.2升级补建：从export-suggestions.md迁移行动项至独立backlog文件
