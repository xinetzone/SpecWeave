---
id: "retrospective-first-principles-command-creation-20260709-backlog"
title: "洞察行动项 Backlog：第一性原理指令集创建任务"
date: 2026-07-09
type: insight-action-backlog
status: completed
source: "第一性原理指令集创建任务"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/task-reports/retrospective-first-principles-command-creation-20260709/insight-action-backlog.toml"
ssot:
  suggestions_source: export-suggestions.md
  insight_source: insight-extraction.md
---
# 洞察行动项 Backlog

> 本文件记录从本次任务复盘中转化的可执行行动项。核心包含：**1项高优先级改进**（spec模板引用验证）+ 2项中优先级改进（modules清单+指令集检查清单）。

## 行动项总览

| ID | 行动项 | 优先级 | 类型 | 状态 | 预期收益 |
|----|--------|--------|------|------|---------|
| ACT-001 | 在 spec 模板中增加引用验证检查项 | 🔴高 | 流程改进 | ✅ 已完成（通过模式沉淀） | 减少 spec 阶段引用错误，降低返工成本 |
| ACT-002 | 创建 modules 目录文件清单 | 🟡中 | 资源建设 | ⏳ 待执行 | spec 阶段可快速查询可用模块 |
| ACT-003 | 建立指令集关联模块存在性检查清单 | 🟡中 | 检查清单 | ⏳ 待执行 | 针对指令集场景的专项验证 |

---

## 🔴 高优先级行动项

### ACT-001：在 spec 模板中增加引用验证检查项

- **优先级**：🔴 高
- **来源**：洞察提取 §系统性问题分析
- **责任人**：spec 模板维护者
- **预期收益**：在 spec 阶段发现引用错误，避免实施阶段返工
- **验收标准（DoD）**：
  1. spec 模板中新增"引用验证"检查项
  2. 检查项明确说明：列出所有引用 → 使用 Glob 验证存在性 → 修正无效引用
  3. 检查项在 spec 创建流程中被实际执行
- **时间计划**：2026-07-16 前完成
- **完成情况**：✅ **已完成** — 通过模式沉淀方式实现：
  - 已沉淀两个互补模式：
    - [spec-reference-validation-pattern.md](../../../patterns/methodology-patterns/spec-workflow/spec-reference-validation-pattern.md)（L1 已验证，spec工作流版本，含具体实施步骤）
    - [spec-reference-validation.md](../../../patterns/methodology-patterns/governance-strategy/spec-reference-validation.md)（L2 已验证，治理策略版本，含四步验证法+质量门槛）
  - 模式包含完整的"列出引用→Glob验证→修正无效→记录结果"实施步骤
  - 已在后续第一性原理综合研究复盘（retrospective-first-principles-comprehensive-research-20260709）中再次验证，成熟度提升至L2

---

## 🟡 中优先级行动项

### ACT-002：创建 modules 目录文件清单

- **优先级**：🟡 中
- **来源**：洞察提取 §系统性问题分析·资源原因
- **责任人**：modules 目录维护者
- **预期收益**：spec 阶段创建引用时可快速查询 modules 目录下有哪些文件可用
- **验收标准（DoD）**：
  1. 在 `.agents/modules/` 目录下创建文件清单（README.md 或独立清单文件）
  2. 清单包含所有 modules 文件的名称、用途、关联指令集
  3. 清单在新增 module 时同步更新
- **时间计划**：2026-07-23 前完成
- **实施步骤**：
  1. 遍历 `.agents/modules/` 目录，收集所有 `.md` 文件
  2. 为每个文件提取名称、用途摘要
  3. 创建 `modules/README.md` 或更新现有 README，添加文件清单表格
  4. 建立"新增 module 时更新清单"的约定

### ACT-003：建立指令集关联模块存在性检查清单

- **优先级**：🟡 中
- **来源**：洞察提取 §改进建议
- **责任人**：指令集维护者
- **预期收益**：针对指令集创建场景，提供专项的关联模块验证清单
- **验收标准（DoD）**：
  1. 在指令集创建流程中新增"关联模块存在性检查"步骤
  2. 检查步骤说明：列出指令集引用的所有模块 → 验证每个模块文件存在 → 修正无效引用
  3. 在指令集创建的 spec 模板中体现该检查
- **时间计划**：2026-07-23 前完成
- **实施步骤**：
  1. 分析现有指令集（`.agents/commands/`）引用的 modules 文件
  2. 建立"指令集→关联模块"映射表
  3. 在指令集创建流程中新增关联模块验证步骤
  4. 更新指令集创建的 spec 模板（如有）

---

## 行动项依赖关系

```
ACT-001（spec模板引用验证）
    ├── 独立可执行
    └── 可参考 ACT-002 的清单作为验证数据源

ACT-002（modules文件清单）
    └── 为 ACT-003 提供数据基础

ACT-003（指令集关联模块检查清单）
    └── 依赖 ACT-002 的清单（可选，有清单更好，无清单也可手动检查）
```

## 完成追踪

| ID | 状态 | 完成日期 | 验证结果 |
|----|------|---------|---------|
| ACT-001 | ✅ 已完成 | 2026-07-09 | 两个模式文件已沉淀，L2已验证（2次验证） |
| ACT-002 | ⏳ 待执行 | - | - |
| ACT-003 | ⏳ 待执行 | - | - |

---

**行动项总结**：3项行动项中，ACT-001（spec模板引用验证）为高优先级，是解决系统性问题的核心改进。ACT-002 和 ACT-003 为中优先级，提供辅助支撑。所有行动项均设有明确的验收标准和时间计划。
