---
name: trae-spec-mode
version: 1.0.0
description: '复杂仓库变更的端到端规范工作流（Spec Mode）。当工作复杂、高影响、跨多组件或跨会话、存在实质性歧义或质量风险、需要可追溯的决策/进度/完成证据，或需要恢复被中断的规范工作流时，必须使用此技能。触发词：规范模式、spec mode、需求澄清、验收标准、任务队列、独立审查、修复队列、恢复中断工作流。简单局部修改、纯头脑风暴、无后续实施的需求文档、代码审查、调试请勿使用；有界变更用 trae-plan-mode。'
argument-hint: "[复杂变更：需求|规划|实施|审查|恢复]"
user-invocable: true
paths:
  - ".agents/skills/trae-spec-mode/**"
source: "../../../external/dao/xinzo/.trae-cn/builtin/trae/doutops/skills/TRAE-spec-mode/SKILL.md（Trae 内置 doutops skill，2026-09-01 集成，本地适配为中文）"
title: Spec Mode — 复杂变更端到端规范工作流
x-toml-ref: "../../../.meta/toml/.agents/skills/trae-spec-mode/SKILL.toml"
---
# trae-spec-mode — 复杂变更端到端规范工作流（Spec Mode）

> 派生自 Trae 内置 doutops skill（溯源见 frontmatter `source`），按 SpecWeave Skill 五要素规范适配为中文。工作流语义、验收词汇与产物模板与上游保持一致；`external/` 非 git 目录，本文件为本地维护版本。

## 1. Skill ID

`trae-spec-mode`（姊妹技能：[trae-plan-mode](../trae-plan-mode/SKILL.md)）

## 2. 功能描述

将**复杂仓库变更**从需求澄清一路推进到独立审查通过的实现。核心能力：

- 需求与验收标准的澄清与持久化（`spec.md`）；
- 原子化、按依赖排序的实施队列（`tasks.md`）；
- 实施者自验 + 独立 Review 双重验收（`review.md`）；
- 中断恢复：从既有产物续跑工作流。

### 与 trae-plan-mode 的选型决策树

```text
需要实施仓库变更？
├─ 变更有界、单一计划 + 一次批准即可控制 → [trae-plan-mode](../trae-plan-mode/SKILL.md)
├─ 复杂/高影响/跨组件或跨会话/需持久化需求与独立审查 → 本技能（Spec Mode）
├─ 被中断的 Spec Mode 工作流需要恢复 → 本技能（从既有产物续跑）
└─ 仅头脑风暴/需求文档（无后续实施）/代码审查/调试/局部小改 → 都不用
```

> **为什么不能把 Specify 和 Plan 合并？** 需求定义"做什么"，任务定义"怎么做"。合并会让实现细节污染需求、验收标准失去稳定性，后续审查也失去对照基准。

## 3. 适用范围（Scope）

满足以下任一条件时使用本技能：

- 工作复杂、高影响，或横跨多个组件/多个会话；
- 需求与验收期望需要澄清并持久化记录；
- 实施需要受管理的任务队列与修复（remediation）队列；
- 完成需要可追溯证据与独立 Review 门；
- 被中断的 Spec Mode 工作流需要从既有产物恢复。

不要用于简单局部修改、纯头脑风暴、无后续实施的需求文档、规划、代码审查、调试、解释或仓库分析。有界且结果清晰的变更用 [trae-plan-mode](../trae-plan-mode/SKILL.md)。

## 4. 输入与产物

**输入**：最新用户请求及其自然语言；仓库根目录与当前代码库状态。

**产物**：在 `$(cwd)/.trae/specs/` 下创建一个描述性文件夹，包含：

| 产物 | 用途 | 可写阶段 |
|---|---|---|
| `spec.md` | 需求与验收标准 | Specify；经批准的需求变更 |
| `tasks.md` | 实施队列、审查 issue、状态与证据 | Plan 与 Implement |
| `review.md` | 独立检查点、证据、Review History | 仅 Review |

所有产物一律使用与最新用户请求相同的自然语言书写。

## 5. 委托策略（Delegation Policy）

任何创建独立工作上下文的机制都视为委托工具（子代理派生、`general_purpose_subagent`、`assign_tasks` 等子任务委托）。对每个委托任务：

- 按信息边界分解；
- 提供目标、先行阅读路径、上下文、范围、成功标准、停止条件与输出契约；
- 防止并发任务写同一文件或共享状态；
- 独立验证并整合返回结果。

分阶段规则：

| 阶段 | 委托规则 |
|---|---|
| Specify / Plan | 有用时委托独立探索；否则直接继续。 |
| Implement | 委托可用且协调值得时，并发委托独立、不重叠的子任务；耦合的实现与测试保持在同一任务内，否则串行。 |
| Review | 委托可用时，向全新上下文委托恰好一次只读独立审查；否则单独执行一轮审查，绝不把实施者自验当最终权威。 |

> **为什么实施者自验不算独立审查证据？** 自验存在确认偏差——实施者倾向于验证"自己做的符合自己的理解"。独立 Review 用全新上下文对照 spec 复核，是验收的最终门。

## 6. 工作流

按顺序跟踪五个阶段：

- [ ] Specify（需求）
- [ ] Plan（规划）
- [ ] Approve（批准）
- [ ] Implement（实施）
- [ ] Review（审查）

### 6.1 Specify

先检查代码库与相关文档再框定需求；用可用的用户输入工具消除实质性歧义。创建 `spec.md`，包含：

- 问题、用户、目标与非目标；
- 功能性与非功能性需求；
- 约束、依赖、假设与待决问题；
- 验收标准（Acceptance Criteria），类型只能为 `rule` 或 `rubric`。

实现分解不得进入 `spec.md`。

### 6.2 Plan

从完成的规格派生 `tasks.md`：

- 将每条验收标准映射到实施工作；
- 创建原子化、按依赖排序的垂直切片；
- 分配 `high`/`medium`/`low` 优先级；
- 派生任务级测试要求（Test Requirements），类型只能为 `rule` 或 `rubric`；
- 除非更窄的 `rule` 能为 `rubric` 提供证据，否则保持父标准类型。

Specify 与 Plan 阶段不得创建 `review.md`。

首次创建 `spec.md` 或 `tasks.md` 前，先读[产物模板](./references/artifact-templates.md)。

### 6.3 Approve

校验 `spec.md` 与 `tasks.md`，将两者作为完整预览提交用户审查（用可用的交互机制通知/请求）。**获得显式批准前不得开始实施。**

> **为什么批准门设在实施之前？** 批准门即预检——用户在产物上确认"做什么、做到什么程度"，实施只发生在已批准的范围内。若批准后再变更需求，必须回到 Specify 重新对齐，否则验收标准与实现脱节。

若批准过程改变了需求：回到 Specify，再重新生成受影响的 Plan 部分，然后重新请求批准。

### 6.4 Implement

一次只处理一个就绪项：

1. 恢复 `in_progress` 的工作；否则选择优先级最高的就绪 `pending` 项。
2. 置 `Status: in_progress`。
3. 应用 Implement 委托策略。
4. 对每条 `rule` TR 与每条 `rubric` TR 自验；记录 rubric 得分、理由与证据。
5. 迭代直到所有任务级 TR 通过。
6. 补充 `Completion Evidence`，然后置 `Status: completed`。
7. 持续直到队列清空。

Implement 期间 `review.md` 只读（即使先前 Review 轮次创建过它）。

队列清空的判定：

```text
所有任务/issue ∈ {completed, cancelled}
且 无一 ∈ {pending, in_progress, blocked}
且 每个 cancelled 项都有显式用户批准
且 所需验收覆盖保持完整
```

受阻工作阻止推进时，持久化 `Blocked By` 与 `Unblock Condition` 并请求所需解决。受阻队列不算清空。

### 6.5 Review

仅在队列清空后进入 Review：

1. 将当前所有 AC/TR 与 `review.md` 对账。
2. `review.md` 缺失则创建；已存在则保留历史，并为修复项或经批准的需求变更补齐缺失检查点。
3. 应用 Review 委托策略，向审查者提供独立审查契约；不要求专用审查者 agent 类型或工具。
4. 结构化结果路由：
   - `pass`：更新 `review.md` 并结束；
   - `fail`：更新 `review.md`，回到 Implement，并在选取工作前把每条可行动发现固化为 pending issue；
   - `blocked`：把阻塞记录进 Review History 并请求解决。

修复清空队列后，用新审查者开启新一轮 Review。blocked 的 Review 解除阻塞后，同样用新审查者开启新一轮。

每个新审查者应获得：

- 用户目标与仓库根目录；
- `spec.md`、`tasks.md`、`review.md` 的绝对路径；
- 相关运行说明与环境约束；
- 实现产物与任务完成证据。

生成 `review.md`、构建审查者提示词或创建审查 issue 前，先读[产物模板](./references/artifact-templates.md)。

## 7. 验收词汇（Verification Vocabulary）

| 类型 | 用途 | 必需形态 |
|---|---|---|
| `rule` | 客观可验证的二元条件 | 可观察的通过条件与证据来源 |
| `rubric` | 评价性质量维度 | 维度、数值量表、低/中/高锚点、通过阈值、证据来源 |

每条 AC/TR 有且只有一个类型：`rule` 或 `rubric`。实施者自验任务级 rule 与 rubric 并记录证据；独立 Review 单独复核两类并作为最终验收门。

## 8. 条目状态（Item Status）

| 状态 | 含义 | 必需副作用 |
|---|---|---|
| `pending` | 未开始 | 无 |
| `in_progress` | 实施或修复中 | 移除过期的阻塞字段 |
| `blocked` | 无法自主推进 | 添加 `Blocked By` 与 `Unblock Condition` |
| `completed` | 所有任务级 rule/rubric TR 自验通过 | 添加 `Completion Evidence`（含 rubric 得分、理由与证据） |
| `cancelled` | 经用户批准移出范围 | 添加原因与批准证据；保留依赖与 AC 覆盖 |

使用稳定标题（如 `## Task 1: ...`），状态只存于 `Status` 字段。本地验证失败保持 `in_progress`；不设 `failed` 状态。

> **为什么没有 `failed` 状态？** 失败是实施的中间态而非终态——队列项要么还在做（in_progress），要么被批准移出（cancelled）。引入 failed 会诱导"标记失败就跳过"的逃避路径。

## 9. Review 结果契约

| 结果 | 必需条件 | 路由 |
|---|---|---|
| `pass` | 所有必需检查点通过、每条 AC 有独立证据、无可行动发现且无受阻检查 | 结束 |
| `fail` | 至少存在一条可行动发现，且每个失败检查点都映射到一条 | 回 Implement，且在选取工作前创建非空 pending 修复队列 |
| `blocked` | 必需检查因环境、权限或依赖无法运行 | 记录阻塞并请求解决 |

当"证据不可得"是唯一问题时用 `blocked` 而非 `fail`。建议性（advisory）发现不阻塞验收。

## 10. 完成判定（Completion）

仅当以下全部成立才可结束：

```text
所有任务/issue ∈ {completed, 经用户批准的 cancelled}
且 所有必需审查检查点已勾选
且 每条 rule 都有通过的独立证据
且 每条 rubric 达到阈值并有理由与证据
且 最新 Review 结果 == pass
且 无遗留可行动发现
```

## 11. 工作流验证

先跑 rule 再跑 rubric。

### Rules

- `spec.md` 与 `tasks.md` 先于批准与实施存在。
- `review.md` 仅在 Review 阶段创建或修改。
- AC/TR 类型只能是 `rule` 或 `rubric`。
- 任务标题不含状态标记。
- 每个 completed 条目有 `Completion Evidence`。
- 每次失败的 Review 至少产生一条 pending 修复 issue。
- 通过的 Review 是唯一成功出口。

### Rubrics

- **工作流保真度（0-2）**：
  - `2`：五个阶段与产物边界全部严格遵守；
  - `1`：工作流成功但有一处非关键边界错误；
  - `0`：跳过阶段或审查独立性被破坏。
- **适应性（0-2）**：
  - `2`：任务分解与证据选择贴合仓库实际；
  - `1`：可用但过于僵化或泛化；
  - `0`：工作流无法适应该请求。

## 12. 安全检查清单

- [ ] 产物（spec/tasks）已作为预览完整呈现并获显式批准（批准门即预检）
- [ ] 批准前未修改任何实现文件（仅产物区写入）
- [ ] 每条 AC/TR 类型为 `rule` 或 `rubric`（无第三种）
- [ ] 实施逐项推进并记录 `Completion Evidence`
- [ ] Review 由独立上下文执行（实施者自验不作为最终验收）
- [ ] 每次 `fail` 都已固化为 pending 修复 issue
- [ ] 中断恢复时先对账既有产物再续跑

## 13. Gotchas

- 不要合并 Specify 与 Plan：需求定义"做什么"，任务定义"怎么做"。
- 不要把实施者自验当作独立 Review 证据。
- Review 在 `review.md` 记录发现；Implement 在选取工作前把可行动发现固化到 `tasks.md`。
- 队列含 `blocked` 项时不算清空，不得进入 Review。
- "证据不可得"用 `blocked`，实现缺陷才用 `fail`。

## 14. Changelog

- **v1.0.0** (2026-09-01): 自 Trae 内置 doutops skill（原名 TRAE-spec-mode）集成并适配为中文版（产物模板保留英文骨架，见 references/artifact-templates.md）；目录名小写化为 trae-spec-mode 以符合开放标准 kebab-case 规范。