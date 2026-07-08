---
title: "A4：L0-L3 模板与现有项目目录结构冲突评估"
source: "retrospective-l0l3-template-design-20260706#A4"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/task-reports/retrospective-l0l3-template-design-20260706/a4-directory-structure-conflict-assessment.toml"
analysis_date: "2026-07-06"
type: "conflict-assessment"
tags: [l0-l3, template, directory-structure, conflict-assessment, a4]
---
# A4：L0-L3 模板与现有项目目录结构冲突评估

## 一、评估背景

L0-L3 流程分级示例模板（`.agents/templates/l0-l3-process-tier-template.md`）定义了 4 级流程框架，引用了多个现有项目资产（工作流、规则、模板、模式、运行时脚本），并提出了新的目录约定（`.temp/baby/` 探针目录）。本评估系统检查模板与现有项目目录结构是否存在潜在冲突。

## 二、评估方法

| 维度 | 检查方式 |
|---|---|
| 路径引用完整性 | 逐一验证模板中所有相对路径引用的文件是否存在 |
| 工作流步骤一致性 | 比对模板中 L2/L3 流程图步骤名称与实际工作流文件 |
| 规则覆盖一致性 | 检查 `stage-guardrails.md` 是否已包含模板声明的探针豁免规则 |
| 目录约定冲突 | 检查 `.temp/baby/` 约定与现有 `.temp/` 用法、`.gitignore` 规则 |
| 角色定义一致性 | 验证模板中 5 个角色是否与 `.agents/roles/` 一致 |
| 模板索引登记 | 确认模板已在 `.agents/templates/README.md` 中登记 |

## 三、无冲突项清单（15 项全部通过）

### 3.1 工作流引用（4 项）

| 模板引用路径 | 实际文件 | 状态 |
|---|---|---|
| `../workflows/feature-development/02-new-feature-flow.md` | `.agents/workflows/feature-development/02-new-feature-flow.md` | ✅ 存在 |
| `../workflows/feature-development/04-refactoring-flow.md` | `.agents/workflows/feature-development/04-refactoring-flow.md` | ✅ 存在 |
| `../workflows/feature-development/01-change-type-overview.md` | `.agents/workflows/feature-development/01-change-type-overview.md` | ✅ 存在 |
| `../workflows/feature-development.md` | `.agents/workflows/feature-development.md` | ✅ 存在 |

### 3.2 规则引用（1 项）

| 模板引用路径 | 实际文件 | 状态 |
|---|---|---|
| `../rules/stage-guardrails.md` | `.agents/rules/stage-guardrails.md` | ✅ 存在（但内容缺失，见冲突 1） |

### 3.3 模板引用（2 项）

| 模板引用路径 | 实际文件 | 状态 |
|---|---|---|
| `handoff-template.md` | `.agents/templates/handoff-template.md` | ✅ 存在 |
| `task-template.md` | `.agents/templates/task-template.md` | ✅ 存在 |

### 3.4 模式引用（6 项）

| 模板引用路径 | 实际文件 | 状态 |
|---|---|---|
| `governance-strategy/elastic-workflow-classification.md` | 同路径 | ✅ 存在 |
| `governance-strategy/exemption-mechanism-legalization.md` | 同路径 | ✅ 存在 |
| `governance-strategy/learn-validate-adopt.md` | 同路径 | ✅ 存在 |
| `document-architecture/two-phase-processing.md` | 同路径 | ✅ 存在 |
| `tools-automation/spec-as-code-automated-gates.md` | 同路径 | ✅ 存在 |
| `code-patterns/three-tier-check-tool.md` | 同路径 | ✅ 存在 |

### 3.5 运行时脚本引用（3 项）

| 模板引用路径 | 实际文件 | 状态 |
|---|---|---|
| `lib/stage_guardrails/boundary.py` | `.agents/scripts/lib/stage_guardrails/boundary.py` | ✅ 存在（A3 已实现 `is_baby_code()`） |
| `lib/stage_guardrails/runtime.py` | `.agents/scripts/lib/stage_guardrails/runtime.py` | ✅ 存在（A3 已实现豁免逻辑） |
| `lib/stage_guardrails/interceptor.py` | `.agents/scripts/lib/stage_guardrails/interceptor.py` | ✅ 存在（A3 已实现 `baby_code` 字段） |

### 3.6 角色引用（5 项）

| 模板中的角色 | 实际文件 | 状态 |
|---|---|---|
| orchestrator | `.agents/roles/orchestrator.md` | ✅ 存在 |
| architect | `.agents/roles/architect.md` | ✅ 存在 |
| developer | `.agents/roles/developer.md` | ✅ 存在 |
| tester | `.agents/roles/tester.md` | ✅ 存在 |
| reviewer | `.agents/roles/reviewer.md` | ✅ 存在 |

### 3.7 模板索引与锚点引用（2 项）

| 引用项 | 状态 |
|---|---|
| `.agents/templates/README.md` 第 29 行已登记 L0-L3 模板 | ✅ 已登记 |
| 复盘报告锚点 `#a3-实现说明baby-前缀运行时识别`（第 244 行） | ✅ 存在 |

## 四、潜在冲突清单

### 冲突 1：`stage-guardrails.md` 未记载探针豁免规则（高风险）✅ 已解决

**风险等级**：🔴 高 → ✅ 已解决（2026-07-07）

**现象**：
- L0-L3 模板 §8.3 声称"阶段守卫运行时已实现 `baby-` 前缀探针代码的识别与豁免"
- A3 行动项已在运行时脚本（`boundary.py`/`runtime.py`/`interceptor.py`）中实现了豁免逻辑
- 但规则文档 `stage-guardrails.md` 本身未更新——Grep 搜索 `baby|探针|probe|豁免` 在该文件中无任何匹配
- `stage-guardrails.md` 已原子化为 5 个子文档（`stage-guardrails/01-principles-governance.md` 到 `05-logging-spec.md`），但均未包含探针豁免规则

**冲突影响**：
- AI 智能体读取 `stage-guardrails.md` 时不会知道探针豁免机制，可能仍按标准 8 阶段规则拦截 `baby-` 前缀代码
- 运行时支持已就绪，但规则文档未同步——形成"代码超前于文档"的债务
- 违反 SpecWeave 的"spec 即代码"原则：规则定义与运行时实现应保持一致

**解决措施**（2026-07-07 执行）：
- ✅ 在 `stage-guardrails/04-interception-approval.md` 新增"L0 探针豁免规则"章节（含豁免触发条件、豁免范围、探针代码约束、运行时支持、豁免限制、与标准流程的关系 6 个子章节）
- ✅ 在 `stage-guardrails/03-stage-boundaries.md` 开头添加 L0 探针豁免声明，指向 04 文档详细说明
- ✅ 在 `stage-guardrails/05-logging-spec.md` 的 BOUNDARY_CHECK/PASS 章节添加 `baby_code: true` 日志示例
- ✅ 更新 `stage-guardrails.md` 主入口的文档导航表（04 描述补充"L0 探针豁免规则"）
- ✅ 主入口添加 2 个相关模式引用（豁免机制合法化、L0-L3 流程分级示例模板）
- ✅ 链接检查通过（26 个本地引用全部有效）
- ✅ 149 个阶段守卫测试全部通过，无回归

---

### 冲突 2：L1 共识级流程无独立工作流文件（中等风险）

**风险等级**：🟡 中

**现象**：
- L0-L3 模板为 L2 定义了引用 `02-new-feature-flow.md`，为 L3 定义了引用 `04-refactoring-flow.md`
- 但 L0（3 步）和 L1（4 步）流程只存在于模板内部，`.agents/workflows/` 目录下没有对应的独立工作流文件
- Grep 搜索 `l1-*` 模式在工作流目录下无匹配

**冲突影响**：
- L0/L1 流程的详细步骤定义不够正式，仅存在于模板中而非独立的工作流文档
- 与 L2/L3 的引用模式不一致——L2/L3 有独立文件可引用，L0/L1 只能内联定义
- 当其他文档需要引用 L1 流程时，无法使用标准的工作流文件路径

**建议处理**：
- **方案 A（推荐）**：保持现状，在模板中明确声明"L0/L1 流程定义仅存在于本模板，不另建工作流文件"——理由是 L0/L1 是轻量流程，不需要完整的工作流文档
- **方案 B**：创建 `.agents/workflows/feature-development/00-l0-l1-lightweight-flow.md`，将模板中的 L0/L1 步骤提取为独立文件
- **决策建议**：采用方案 A，因为 L0/L1 的设计初衷就是"轻量"，创建独立工作流文件会增加文档负担，与 L0/L1 的"实现便宜"理念相悖

---

### 差异 3：L2 步骤名称简称与全称不一致（低风险）

**风险等级**：🟢 低

**现象**：
- L0-L3 模板 L2 流程图标注：`①需求接收 / ②方案设计 / ③任务分配 / ④代码实现 / ⑤测试编写 / ⑥代码审查 / ⑦合并代码 / ⑧完成确认`
- 实际 `02-new-feature-flow.md` 步骤 1 全称：`步骤 1：需求接收与分解`
- 模板使用简称"需求接收"，实际全称"需求接收与分解"

**影响**：轻微，简称便于流程图展示，但可能引起引用混淆

**建议处理**：在模板 §5.1（L2 流程引用）中补充说明"流程图中为步骤简称，完整步骤名称见 [02 新功能完整流程](../../../../../.agents/workflows/feature-development/02-new-feature-flow.md)"

---

### 差异 4：`.temp/` 目录已在 `.gitignore` 中被忽略（设计符合，非冲突）

**风险等级**：✅ 无风险（设计符合）

**现象**：
- `.gitignore` 第 2 行：`.temp/` 整个目录被忽略
- L0-L3 模板要求探针代码放置在 `.temp/baby/` 目录下
- 现有 `.temp/` 目录已有其他用途（`commit-msg-*.txt` 提交消息缓存）

**评估**：
- `.temp/baby/` 作为 `.temp/` 的子目录，自然被 `.gitignore` 忽略——这符合模板设计意图（探针代码"不入主干、不进 CI"）
- 现有 `.temp/` 的其他用途（提交消息缓存）与 `.temp/baby/` 互不干扰
- **结论**：非冲突，是设计符合

## 五、附带发现（非 A4 范围）

### 附带发现 1：`stage-guardrails.md` frontmatter 重复 ✅ 已修复

**现象**：`stage-guardrails.md` 第 1-14 行存在重复的 frontmatter 块（两个 `---` 块内容完全相同）

**影响**：文档解析器可能只读取第一个 frontmatter 块，第二个被忽略，但形式上不规范

**修复**（2026-07-07）：在冲突 1 解决过程中一并修复，删除了重复的 frontmatter 块

## 六、结论与建议

### 6.1 总体评估

| 维度 | 结果 |
|---|---|
| 路径引用完整性 | ✅ 15 项引用全部存在，无断链 |
| 工作流步骤一致性 | 🟢 轻微差异（简称 vs 全称） |
| 规则覆盖一致性 | ✅ 已解决（规则文档已同步探针豁免规则，2026-07-07） |
| 目录约定冲突 | ✅ 无冲突（`.temp/baby/` 符合设计） |
| 角色定义一致性 | ✅ 5 个角色全部存在 |
| 模板索引登记 | ✅ 已登记 |

### 6.2 建议行动项

| 优先级 | 行动项 | 责任 | 预估工作量 |
|---|---|---|---|
| 高 | ~~在 `stage-guardrails/` 子文档中新增"L0 探针豁免"章节，同步规则文档与运行时实现~~ | ✅ 已完成（2026-07-07） | — |
| 低 | 在 L0-L3 模板 §5.1 中补充 L2 步骤简称说明 | 可选，下次模板修订时处理 | 5 分钟 |
| 信息 | 在模板中明确声明"L0/L1 流程定义仅存在于本模板" | 可选，下次模板修订时处理 | 5 分钟 |

### 6.3 决策结论

L0-L3 模板与现有项目目录结构**总体兼容**，15 项路径引用全部有效，无断链。原 1 个高风险冲突（规则文档未同步探针豁免规则）已于 2026-07-07 解决，1 个中等风险差异（L1 无独立工作流文件）建议保持现状。当前无阻塞 L0-L3 模板使用的冲突。

---

← 返回 [复盘报告](README.md) | 上级 [任务复盘索引](../../README.md)
