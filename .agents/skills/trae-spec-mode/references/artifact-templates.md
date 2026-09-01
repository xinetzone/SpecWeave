# Spec Mode 产物模板（Artifact Templates）

> 派生自 Trae 内置 doutops skill，按 SpecWeave 规范适配为中文说明；模板骨架保留英文（运行时按用户请求语言生成内容）。

在 Spec Mode 工作流创建或更新持久化产物时使用以下模板。只包含适用的字段；保留既有证据与历史。

## 目录

- `spec.md`
- `tasks.md`
- `review.md`
- 独立审查报告（Independent Review Report）
- 审查 issue（Review Issue）

## `spec.md`

```markdown
# [Project Title] - Product Requirements Document

## Overview
- **Summary**: [What is being built]
- **Purpose**: [Why]
- **Target Users**: [Who]

## Goals
- [Goal]

## Non-Goals
- [Excluded scope]

## Background & Context
- [Evidence and prior decisions]

## Functional Requirements
- **FR-1**: [Required behavior]

## Non-Functional Requirements
- **NFR-1**: [Quality requirement]

## Constraints
- **Technical**: [...]
- **Business**: [...]
- **Dependencies**: [...]

## Assumptions
- [...]

## Acceptance Criteria

### AC-1: [Rule title]
- **Type**: `rule`
- **Given**: [...]
- **When**: [...]
- **Then**: [...]
- **Pass Condition**: [...]
- **Evidence**: [...]

### AC-2: [Rubric title]
- **Type**: `rubric`
- **Dimension**: [...]
- **Scale**: 1-5
- **Anchors**: 1 = [...]; 3 = [...]; 5 = [...]
- **Pass Threshold**: >= 4
- **Evidence**: [...]

## Open Questions
- [ ] [...]
```

## `tasks.md`

```markdown
# [Project Title] - Implementation Plan

## Task 1: [Descriptive title]
- **Status**: `pending`
- **Priority**: high | medium | low
- **Depends On**: [Item IDs or "None"]
- **Description**:
  - [Implementation outcome]
- **Acceptance Criteria Addressed**: [AC IDs]
- **Test Requirements**:
  - `rule` TR-1.1: [Binary condition and evidence]
  - `rubric` TR-1.2: [Dimension]; scale 1-5; anchors 1/3/5; threshold >= 4; evidence [...]
- **Notes**: [Optional]
```

示例同时展示了两种 TR 类型；只包含适用的类型，且每个条目至少一条 TR。仅在对应状态发生时才添加该状态的专属字段。

### 状态专属字段（Status-Specific Fields）

completed：

```markdown
- **Status**: `completed`
- **Completion Evidence**:
  - [Rule result, command output, or artifact]
  - [Rubric score, rationale, and evidence]
```

blocked：

```markdown
- **Status**: `blocked`
- **Blocked By**: [Observable blocker]
- **Unblock Condition**: [Condition that permits resumption]
```

cancelled：

```markdown
- **Status**: `cancelled`
- **Cancellation Reason**: [Why the work is no longer required]
- **Cancellation Approved By**: [User approval evidence]
```

## `review.md`

仅在实施队列清空后创建本文件。

```markdown
# [Project Title] - Independent Review

- [ ] CP-R1: [Binary product outcome]
  - **Type**: `rule`
  - **Covers**: [AC/TR IDs]
  - **Evidence**: Pending

- [ ] CP-U1: [Evaluative product outcome]
  - **Type**: `rubric`
  - **Covers**: [AC/TR IDs]
  - **Scale**: 1-5
  - **Anchors**: 1 = [...]; 3 = [...]; 5 = [...]
  - **Pass Threshold**: >= 4
  - **Evidence**: Pending

## Review History

### Review R1
- **Result**: `pass` | `fail` | `blocked`
- **Evidence**: [...]
- **Blocked By**: [Only when blocked]
- **Resume When**: [Only when blocked]
```

每条 AC/TR 都必须被覆盖；仅当单个连贯、可观察的检查点能同时验证它们时才合并相关 AC/TR。

## 独立审查报告（Independent Review Report）

```markdown
# Review R[N]
- **Result**: `pass` | `fail` | `blocked`
- **Checks Performed**:
  - [Check and command/action]
- **Evidence**:
  - [Observed result]
- **Checkpoint Results**:
  - CP-R1 (`rule`): `pass` | `fail` | `blocked`
  - CP-U1 (`rubric`): `pass` | `fail` | `blocked`; score [1-5]; rationale [...]
- **Findings**:
  - [ID]: `actionable` | `advisory`; severity; reproduction; expected outcome
- **Recommended Issues**:
  - [Title, priority, AC/checkpoint links, regression requirement]
```

适用以下不变量：

- `pass` 要求所有检查点通过、每条 AC 有独立证据，且无可行动发现或受阻检查。
- `fail` 要求至少存在一条可行动发现。
- 每个失败检查点映射到一条可行动发现。
- 每条可行动发现映射到一条 pending 审查 issue。
- `blocked` 记录环境、权限或依赖不可得，而非实现缺陷。

## 审查 issue（Review Issue）

失败的 Review 在 `review.md` 记录发现后，转入 Implement 并在选取工作前用以下模板把每条可行动发现固化为 issue。

```markdown
## Issue I-[N]: [Finding title]
- **Status**: `pending`
- **Priority**: high | medium | low
- **Depends On**: [Item IDs or "None"]
- **Discovered By**: Review R[N]
- **Description**:
  - [Observable gap and reproduction]
- **Acceptance Criteria Addressed**: [AC IDs]
- **Test Requirements**:
  - `rule` TR-I-[N].1: [Regression condition and evidence]
  - `rubric` TR-I-[N].2: [Dimension; scale; anchors; threshold; evidence]
- **Notes**: [Optional]
```

只包含适用的 TR 类型，且至少一条 TR。优先新建 issue 而非重开已完成工作；仅当其本地完成证据无效时才重开。
