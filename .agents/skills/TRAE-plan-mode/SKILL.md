---
name: TRAE-plan-mode
version: 1.0.1
description: '有界仓库变更的规划-批准-执行工作流（Plan Mode）。当需要先调研仓库或向用户澄清才能确定实施步骤、且单一实施计划+一次批准门即可提供足够控制时，必须使用此技能。触发词：规划、实施计划、plan mode、计划批准、先规划后执行、有界变更、调研后规划。复杂工作（需持久化需求、验收标准、任务队列或独立审查）请勿使用，改用 TRAE-spec-mode。'
argument-hint: "[有界变更：调研|规划|批准|执行]"
user-invocable: true
paths:
  - ".agents/skills/TRAE-plan-mode/**"
source: "镜像自 Trae IDE builtin/trae/doutops（源镜像已清理，原路径 external/dao/xinzo/.trae-cn/builtin/trae/doutops/skills/TRAE-plan-mode/SKILL.md；本文件为独立适配版，以本地为准）"
title: Plan Mode — 有界变更规划与执行
x-toml-ref: "../../../.meta/toml/.agents/skills/TRAE-plan-mode/SKILL.toml"
---
# TRAE-plan-mode — 有界变更规划与执行（Plan Mode）

> **本地独立适配版**（SpecWeave Skill 五要素规范，中文）。Trae 内置 doutops 同步可能以英文原版覆盖本文件——覆盖后按 git 历史（自 `0931e42df` 起）恢复本版即可，无需重新适配。工作流语义与上游保持一致。

## 1. Skill ID

`TRAE-plan-mode`（姊妹技能：[TRAE-spec-mode](../TRAE-spec-mode/SKILL.md)）

## 2. 功能描述

在实施前对**有界变更**进行规划，经批准后执行。核心操作：调研仓库 → 生成单一实施计划 → 请求批准 → 按计划实施并验证 → 汇报结果。

### 与 TRAE-spec-mode 的选型决策树

```text
需要实施仓库变更？
├─ 需要调研或向用户澄清才能确定实施步骤，且一个计划+一次批准足够 → 本技能（Plan Mode）
├─ 需要持久化需求产物、rule/rubric 验收标准、受管任务队列或独立 Review 门 → [TRAE-spec-mode](../TRAE-spec-mode/SKILL.md)
└─ 非编辑请求（解释/调查/分析/讨论）→ 直接回应，计划与批准可选
```

## 3. 适用范围（Scope）

满足以下条件时使用本技能：

- 需要仓库调研或用户澄清才能确定实施步骤；
- 单一实施计划 + 一次批准门即可提供足够控制；
- 期望结果可被一个计划覆盖。

当工作需要持久化需求产物、`rule`/`rubric` 验收标准、受管任务或修复队列、独立 Review 门时，改用 Spec Mode。

## 4. 工作流

### 4.1 Understand（理解）

阅读相关代码与文档，理解请求与当前实现；用可用的用户输入工具消除实质性歧义。

非编辑请求（解释、调查、分析、讨论）可跳过计划文档与批准——直接回应即可。

### 4.2 Plan（规划）

在以下位置创建唯一一份实施计划：

```text
$(cwd)/.trae/documents/{NAME}_plan.md
```

用简短描述性命名，使用与最新用户请求相同的自然语言书写。内容包含：

- 仓库调研结论；
- 待变更的文件与模块；
- 按依赖排序的实施步骤；
- 相关依赖与注意事项；
- 实施后所需验证；
- 风险及其处置。

计划体量与任务成比例；不写开发时间或排期估算。

> **为什么禁止写时间/排期估算？** 模型对工时的估计既不可靠也不可验证，写进计划会诱导过度承诺与错误预期。计划的价值在依赖顺序、影响面与风险预判，不在日历。

### 4.3 Approve（批准）

计划写完后，用 `NotifyUser`（可用时）请求审查与批准；不可用时改用其他可用的交互机制。**计划文档本身即预览**——它完整呈现将要发生的变更，用户审查批准即完成预览确认。

**除计划文档本身外，显式批准前不得修改任何文件或系统状态。**

> **为什么批准前禁止一切实现性写入？** 批准门是本技能唯一的安全防线——用户审查的是"将要发生什么"。若批准前已产生副作用，批准就失去了对执行的控制权。

### 4.4 Implement（实施）

批准后按计划执行并完成其验证。当批准范围或实施步骤发生实质变化时，保持计划文档与实际一致；发生实质性范围变更时，先重新请求批准再继续。

### 4.5 Respond（汇报）

汇总已完成的工作与验证结果。

## 5. 计划模板

```markdown
# [Change Name] Implementation Plan

## Repository Research
[Relevant current behavior, architecture, and constraints]

## Files and Modules
- `[path]`: [expected change]

## Implementation Steps
1. [Dependency-ordered step]

## Dependencies and Considerations
- [Dependency, compatibility concern, or important assumption]

## Validation
- [Test, check, or inspection]

## Risks
- [Risk]: [handling or fallback]
```

> 模板骨架保留英文（运行时按用户语言生成内容）；简单任务可裁剪到与任务成比例的最小集。

## 6. 工作流验证清单

- 实施前仅创建了一份计划。
- 计划包含调研、影响面、步骤、注意事项、验证与风险。
- 批准发生在计划创建之后、实施之前。
- 批准前没有任何实现性状态变更。
- 工作流不创建 Spec Mode 产物，也不要求独立 Review 门。

## 7. 安全检查清单

- [ ] 计划文档已作为预览提交用户审查（含调研、影响面、步骤、验证与风险）
- [ ] 显式批准前未修改任何实现文件或系统状态（预检：写入范围仅限计划文档）
- [ ] 计划与任务成比例，未夹带时间/排期估算
- [ ] 范围实质变化已重新走批准门，未"顺手做掉"
- [ ] 实施完成后已按计划执行验证并汇报结果

## 8. Gotchas

- 计划文档是实施辅助，不是需求规格——不要把它扩展成 Spec Mode 的产物与审查生命周期。
- 范围实质变化必须重新走批准门，不能"顺手做掉"。
- 计划落盘路径是 `.trae/documents/`，与 Spec Mode 的 `.trae/specs/` 不同，两者不要混用。
- Trae 内置同步覆盖本文件后内容会回退为英文原版——发现 language/五要素缺失即触发恢复（git 历史含本版全文）。

## 9. Changelog

- **v1.0.1** (2026-09-01): Trae 内置同步覆盖后恢复重写；目录名随同步路径采用大写 TRAE-*（终止命名拉锯，接受开放标准 name.format 2 项 WARN）；新增同步覆盖恢复指引。
- **v1.0.0** (2026-09-01): 自 Trae 内置 doutops skill 集成并适配为中文版。