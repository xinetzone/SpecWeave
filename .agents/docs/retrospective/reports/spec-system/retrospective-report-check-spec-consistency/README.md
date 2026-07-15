---
id: "retrospective-report-check-spec-consistency-readme"
title: "规格文档一致性检查工具 — 复盘报告"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/reports/spec-system/retrospective-report-check-spec-consistency/README.toml"
---
# 规格文档一致性检查工具 — 复盘报告

> **项目名称**：规格文档一致性检查工具（check-spec-consistency.py）
> **复盘日期**：2026-06-23
> **项目周期**：v1.0 基础开发 → v1.1 问题修复与优化 → v1.2 元文档识别升级（单次交付周期，含三轮迭代）
> **报告类型**：项目结项复盘

## 项目概览

### 1.1 项目背景

在智能体开发规范体系项目中，`spec.md`、`tasks.md`、`checklist.md` 三份文档之间存在逻辑关联与交叉引用关系。当 `spec.md` 变更时，`tasks.md` 和 `checklist.md` 可能不同步，导致规格与任务/检查清单不一致。此前，这种一致性依赖人工逐项核对，效率低且易遗漏。

本项目源于上一轮复盘报告中提出的改进建议——"开发 `check-spec-consistency.py` 脚本，当 `spec.md` 变更时自动检测 `tasks.md` 和 `checklist.md` 是否需要同步更新"。该工具旨在将规格文档的一致性检查从人工核对升级为自动化检测，作为规格驱动开发流程的质量保障基础设施。

### 1.2 项目目标

本项目的核心目标包括以下五个方面：

1. **实现 spec.md 解析器**：从 `spec.md` 中提取需求列表（Requirement）、场景列表（Scenario）、关键数据引用（如"9 个主任务、42 个子任务"）。
2. **实现 tasks.md 解析器**：从 `tasks.md` 中提取任务/子任务列表、完成状态、统计信息。
3. **实现 checklist.md 解析器**：从 `checklist.md` 中提取检查类别、检查点、完成状态、统计信息。
4. **实现一致性检查引擎**：交叉验证需求→任务覆盖、场景→检查点覆盖、数据引用一致性、路径引用有效性。
5. **实现结构化输出**：终端彩色报告（通过/警告/错误）与 JSON 格式输出，支持命令行参数控制。

v1.1 优化阶段新增三个目标：

6. **可配置语义匹配阈值**：支持 `--match-threshold` 参数，解决中文短文本匹配率低的问题。
7. **路径引用上下文感知解析**：区分项目根目录路径与 spec 相对路径，减少路径误报。
8. **自引用/外部引用数据区分**：识别复盘类 spec 中引用被复盘项目数据的情况，避免误报错误。

v1.2 优化阶段新增一个目标：

9. **元文档识别升级**：将关键词检测升级为"显式标记优先 + 关键词兜底"双层策略，消除假阳性/假阴性风险。

## 子模块导航

| 章节 | 权威来源 | 说明 |
|------|---------|------|
| 执行复盘 | [execution-retrospective.md](execution-retrospective.md) | 实施过程回顾、关键节点概览表、量化数据、成功经验与问题 |
| 关键节点v1.0 | [key-nodes-v1.0.md](key-nodes-v1.0.md) | 需求来源→三段式架构→v1.0三类问题暴露（奠基期） |
| 关键节点v1.1-v1.2 | [key-nodes-v1.1-v1.2.md](key-nodes-v1.1-v1.2.md) | 三项独立修复→增量+回归验证→元文档识别精确化（迭代优化期） |
| 洞察萃取 | [insight-extraction.md](insight-extraction.md) | 关键发现、规律认知、潜在机会 |
| 导出建议 | [export-suggestions.md](export-suggestions.md) | 改进建议、行动计划、后续优化方向 |

## 关联报告

[retrospective-report-readme-atomization/](../../atomization/retrospective-report-readme-atomization/README.md)、[retrospective-report-refactor-retrospective-docs/](../../atomization/retrospective-report-refactor-retrospective-docs/README.md)、[retrospective-report-fact-statement-correction/](../retrospective-report-fact-statement-correction/README.md)
