+++
id = "retrospective-report-check-spec-consistency-overview"
date = "2026-06-23"
type = "project-overview"
source = "docs/retrospective/reports/retrospective-report-check-spec-consistency.md#一、项目概述"
+++

# 项目概述

## 1.1 项目背景

在智能体开发规范体系项目中，`spec.md`、`tasks.md`、`checklist.md` 三份文档之间存在逻辑关联与交叉引用关系。当 `spec.md` 变更时，`tasks.md` 和 `checklist.md` 可能不同步，导致规格与任务/检查清单不一致。此前，这种一致性依赖人工逐项核对，效率低且易遗漏。

本项目源于上一轮复盘报告中提出的改进建议——"开发 `check-spec-consistency.py` 脚本，当 `spec.md` 变更时自动检测 `tasks.md` 和 `checklist.md` 是否需要同步更新"。该工具旨在将规格文档的一致性检查从人工核对升级为自动化检测，作为规格驱动开发流程的质量保障基础设施。

## 1.2 项目目标

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

## 1.3 交付物清单

| 类别       | 交付物                                      | 数量 | 说明                                    |
| ---------- | ------------------------------------------- | ---- | --------------------------------------- |
| 核心脚本   | `.agents/scripts/check-spec-consistency.py` | 1    | ~950 行 Python 脚本，16 个函数/模块（v1.2 新增 `detect_meta_document()`） |
| 脚本说明   | `.agents/scripts/README.md`                 | 1    | 更新现有文件，新增脚本条目               |
| 规格文档   | `.trae/specs/check-spec-consistency/spec.md` | 1    | 19 个需求、30+ 场景（含 v1.1、v1.2 新增） |
| 任务清单   | `.trae/specs/check-spec-consistency/tasks.md` | 1    | 14 个主任务、36 个子任务                |
| 检查清单   | `.trae/specs/check-spec-consistency/checklist.md` | 1    | 12 个检查类别、52 个检查点              |
| **合计**   |                                             | **5** | 1 核心脚本 + 1 说明更新 + 3 规格文档    |