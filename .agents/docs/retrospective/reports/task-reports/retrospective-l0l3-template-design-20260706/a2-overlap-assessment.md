---
title: "A2 行动项：L0-L3 模板与 elastic-workflow-classification 模式重叠评估"
source: "retrospective-l0l3-template-design-20260706#A2"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/retrospective/reports/task-reports/retrospective-l0l3-template-design-20260706/a2-overlap-assessment.toml"
analysis_date: "2026-07-06"
type: "action-item-assessment"
tags: [l0-l3, elastic-workflow, overlap-assessment, action-item, a2]
---
# A2 行动项：L0-L3 模板与 elastic-workflow-classification 模式重叠评估

## 一、评估背景

本评估是 L0-L3 流程分级示例模板设计复盘的 A2 行动项产出。复盘 S2 阶段识别出"设计前未搜索模式库"的改进点，复盘中发现 `elastic-workflow-classification.md` 模式可能与新设计的 L0-L3 模板存在重叠。本评估旨在明确两者边界，给出"保持独立"或"合并"的建议。

## 二、对照对象概览

| 维度 | elastic-workflow-classification.md | l0-l3-process-tier-template.md |
|---|---|---|
| **文件类型** | 模式文档（methodology-pattern） | 示例模板（template） |
| **所在目录** | `docs/retrospective/patterns/methodology-patterns/governance-strategy/` | `.agents/templates/` |
| **来源** | retrospective-stage-guardrails-logging-20260629 洞察5 | Codex 产品哲学文章深度洞察分析报告 §9.5 + §10.2 |
| **成熟度** | L2 验证模式 | 示例模板（尚未验证） |
| **抽象层级** | 抽象方法论（"变更风险适配"原则） | 具体实施工具（4 级流程模板） |
| **核心命题** | 流程严格度与变更风险成正比 | 流程形态与任务复杂度相匹配 |

## 三、维度对照分析

### 3.1 核心机制对比

| 项 | elastic-workflow-classification | l0-l3-process-tier-template |
|---|---|---|
| **决策机制** | 变更类型判定决策树（3 路径） | 流程分级判定决策树（4 层级） |
| **路径/层级数** | 3 路径：New Feature / Extension / Refactoring | 4 层级：L0 探索 / L1 共识 / L2 生产 / L3 重构 |
| **判定问题** | 是否从零构建？是否改动核心？ | 探索还是交付？需建立共识？新增还是改动？涉及数据模型？ |
| **风险等级** | 3 级（中/低/高） | 4 级（极低/低/中/高） |

### 3.2 三路径 vs 四层级对应关系

| elastic-workflow 路径 | l0-l3 层级 | 对应关系 | 说明 |
|---|---|---|---|
| —（无对应） | **L0 探索级** | 🆕 l0-l3 新增 | elastic-workflow 未覆盖探索性假设验证场景 |
| Extension（6步轻量） | **L1 共识级**（4步） | ⚠️ 部分重叠 | 两者都属轻量流程，但定位不同（见 §3.3） |
| New Feature（8步完整） | **L2 生产级**（8步） | ✅ 完全对应 | l0-l3 的 L2 直接引用 elastic-workflow 对应的 8 步流程 |
| Refactoring（7步重量） | **L3 重构级**（7步） | ✅ 完全对应 | l0-l3 的 L3 直接引用 elastic-workflow 对应的 7 步流程 |

### 3.3 L1 共识级 vs Extension 路径的差异

这是两者最可能产生混淆的对照点，需明确区分：

| 维度 | Extension 路径 | L1 共识级 |
|---|---|---|
| **关注点** | 增量扩展不改核心 | 跨方共识建立 |
| **典型场景** | 添加一个 API 端点、修改文案 | 边界澄清、跨方对齐 |
| **步骤数** | 6 步（跳过 S2 简化方案） | 4 步（共识边界→原型→审查→合并） |
| **关键差异** | 假设共识已具备，只是技术增量 | 假设共识未具备，需先建立共识 |
| **覆盖率要求** | 未明确降低 | 明确可降至 60%（区別于 L2 的 80%） |
| **媒介选择** | 未涉及 | 四维判定（受众×频率×认知×协作） |

**结论**：L1 与 Extension 不是替代关系，而是互补关系——一个 Extension 任务若需要跨方共识建立，应升级到 L1；一个 L1 任务在共识建立后若技术上是增量扩展，可参考 Extension 的实施要点。

### 3.4 设计哲学对比

| 维度 | elastic-workflow-classification | l0-l3-process-tier-template |
|---|---|---|
| **理论来源** | SpecWeave 内部复盘沉淀 | Codex 产品哲学三大概念（baby Codex / home base / AGI-pilled） |
| **治理视角** | 风险适配——给低风险留通道，给高风险加护栏 | 探索合法化 + 形态-能力匹配 |
| **设计原则** | 决策前置、客观判定、权限升级、文档差异、禁止降级 | 概念映射、引用而非重复、豁免机制合法化、形态-能力匹配 |
| **反模式警示** | 一刀切、主观选择、路径跳变 | 用生产流程约束探索、把工作锁进超级流程、用重型流程押注未来复杂度 |

### 3.5 特色机制对比

| 特色机制 | elastic-workflow | l0-l3 | 说明 |
|---|---|---|---|
| **探针实现豁免** | ❌ 无 | ✅ `baby-` 前缀 + `.temp/baby/` + 30 天生命周期 | l0-l3 独有，将探索合法化 |
| **AGI-pilled 形态-能力匹配检查** | ❌ 无 | ✅ 4 项检查 × 3-4 子项，≥2 项未通过降级 | l0-l3 独有，防止 L3 过度治理 |
| **媒介选择决策矩阵** | ❌ 无 | ✅ 四维判定（受众×频率×认知×协作） | l0-l3 独有，L1 步骤①的关键差异点 |
| **角色参与矩阵** | ❌ 无 | ✅ 5 角色 × 4 层级 = 20 单元格 | l0-l3 独有，明确各层级角色职责 |
| **PDR-LOG 分级要求** | ❌ 无 | ✅ 4 级日志粒度 | l0-l3 独有，日志要求与流程层级匹配 |
| **回滚策略差异** | ✅ 功能开关/直接回退/迁移脚本 | ❌ 未明确（L3 引用现有流程） | elastic-workflow 独有 |

## 四、重叠点分析

### 4.1 实质重叠（需处理）

1. **L2/L3 与 New Feature/Refactoring 的流程定义**：l0-l3 已通过引用方式处理（"详见 02/04 文档"），未重复定义，符合 DRY 原则——**无需额外处理**
2. **决策树结构相似**：两者都采用前置判定的 Mermaid 决策树——但这是治理模式的通用结构，不属于重复

### 4.2 表面重叠（无需处理）

1. **L1 与 Extension 都属"轻量流程"**：但定位不同（共识建立 vs 增量扩展），已在 §3.3 明确区分
2. **都涉及"风险等级"概念**：但 elastic-workflow 基于"变更风险"，l0-l3 基于"任务复杂度"，维度不同

### 4.3 非重叠（互补扩展）

1. **L0 探索级**：elastic-workflow 完全未覆盖，是 l0-l3 的纯扩展
2. **AGI-pilled 检查清单**：elastic-workflow 的 Refactoring 路径没有前置检查，l0-l3 新增了"形态-能力匹配"治理
3. **探针豁免机制**：elastic-workflow 无此概念，l0-l3 通过 `baby-` 前缀合法化探索
4. **媒介选择决策矩阵**：elastic-workflow 未涉及，l0-l3 独有

## 五、边界建议

### 5.1 结论：保持两者独立，不合并

**理由**：

| 理由维度 | 说明 |
|---|---|
| **定位不同** | elastic-workflow 是"治理方法论"（抽象原则），l0-l3 是"流程实施模板"（具体工具） |
| **类别不同** | governance-strategy 模式 vs templates 模板——所属目录和用途不同 |
| **成熟度不同** | L2 验证模式 vs 未验证示例模板——合并会混淆成熟度层级 |
| **抽象层级不同** | elastic-workflow 是"变更类型判定原则"，l0-l3 是"流程分级实施模板"——后者是前者的具体化+扩展 |
| **DRY 已保持** | l0-l3 通过引用方式复用 elastic-workflow 的 L2/L3 流程定义，未重复 |

### 5.2 边界划分

```
elastic-workflow-classification.md（治理方法论层）
  ├─ 定义"变更风险适配"原则
  ├─ 定义 3 路径判定决策树（New Feature / Extension / Refactoring）
  └─ 定义路径间差异（步骤数/前置文档/审批要求/回滚策略）

l0-l3-process-tier-template.md（流程实施模板层）
  ├─ 扩展为 4 层级（新增 L0 探索级）
  ├─ L2/L3 引用 elastic-workflow 的对应流程定义（DRY）
  ├─ 新增 L0 探针豁免机制（baby- 前缀合法化）
  ├─ 新增 L3 AGI-pilled 形态-能力匹配检查清单
  ├─ 新增 L1 媒介选择决策矩阵
  └─ 新增角色参与矩阵 + PDR-LOG 分级要求
```

### 5.3 使用场景区分

| 场景 | 应使用的文档 | 理由 |
|---|---|---|
| 理解"为什么需要流程分级" | elastic-workflow-classification.md | 治理原则和反模式警示 |
| 启动新任务时选择流程层级 | l0-l3-process-tier-template.md | 具体的 4 级判定决策树和步骤详情 |
| 设计阶段守卫运行时规则 | 两者结合 | elastic-workflow 提供原则，l0-l3 提供分级应用 |
| 评估是否过度治理 | l0-l3-process-tier-template.md §6.2 | AGI-pilled 检查清单 |
| 探索性任务的合法化 | l0-l3-process-tier-template.md §3 | L0 探针豁免机制 |

## 六、交叉引用更新建议

为避免"模式已存在但使用者不知道"的断链，建议在两个文件中添加双向引用：

### 6.1 elastic-workflow-classification.md 应添加

在"关联模式"区域添加：

```markdown
> 扩展模板：[l0-l3-process-tier-template.md](../../../../../.agents/templates/l0-l3-process-tier-template.md)
> 
> 该模板将本模式的 3 路径扩展为 4 层级（新增 L0 探索级），并为 L3 路径增加了 AGI-pilled 形态-能力匹配前置检查。本模式定义变更风险适配原则，该模板提供具体的流程分级实施工具。
```

### 6.2 l0-l3-process-tier-template.md 应添加

在"十一、相关模式"区域添加：

```markdown
- [弹性工作流分类](../../../patterns/methodology-patterns/governance-strategy/elastic-workflow-classification.md)——本模板的 L2/L3 流程定义源自该模式的 New Feature/Refactoring 路径；该模式定义变更风险适配原则，本模板将其扩展为 4 层级并新增 L0 探索级
```

## 七、评估结论

| 评估项 | 结论 |
|---|---|
| **是否重复？** | ❌ 不重复——关注点、抽象层级、定位均不同 |
| **是否重叠？** | ⚠️ 部分重叠——L2/L3 流程定义重叠，但已通过引用方式处理（DRY） |
| **是否需要合并？** | ❌ 不合并——两者是"方法论"与"实施模板"的互补关系 |
| **是否需要交叉引用？** | ✅ 需要——添加双向引用，避免使用者找不到关联资产 |
| **L1 与 Extension 是否冲突？** | ❌ 不冲突——定位不同（共识建立 vs 增量扩展），互补使用 |
| **L0 是否是 elastic-workflow 的扩展？** | ✅ 是——L0 探索级是 elastic-workflow 未覆盖的纯扩展 |

## 八、后续建议

1. **立即执行**：按 §6 更新两个文件的双向交叉引用
2. **A2 完成**：本评估文档创建后，A2 行动项标记为"已完成"
3. **未来迭代**：若 L0 探针豁免机制和 AGI-pilled 检查清单经过验证（≥2 次），可考虑沉淀为独立的 governance-strategy 模式文档，届时与 elastic-workflow-classification.md 形成三模式互补

## 关联资源

- [L0-L3 模板设计复盘报告](./README.md)
- [L0-L3 流程分级示例模板](../../../../../templates/l0-l3-process-tier-template.md)
- [弹性工作流分类模式](../../../patterns/methodology-patterns/governance-strategy/elastic-workflow-classification.md)
- [上游分析报告（已归档）](../../insight-extraction/external-learning/retrospective-codex-article-analysis-20260706/analysis-report.md)
