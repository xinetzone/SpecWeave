+++
description = "可复用模式库总索引 - 架构/代码/方法论三层模式体系"
+++

# 可复用模式库（patterns）

本目录存放经过验证的可复用模式，按层级分为架构模式、代码模式、方法论模式三类。

## 目录结构

| 目录 | 层级 | 说明 | 入口 |
|------|------|------|------|
| architecture-patterns/ | 架构层 | 文件依赖拓扑、级联更新策略、系统结构设计 | [README.md](architecture-patterns/README.md) |
| code-patterns/ | 代码层 | 具体代码编写、文件操作、编辑策略 | [README.md](code-patterns/README.md) |
| methodology-patterns/ | 方法论层 | 按主题分为7个子目录（复盘知识/文档架构/工具自动化/治理策略/AI协作/创意设计/产品增长） | [README.md](methodology-patterns/README.md) |

## 模式成熟度评估标准

### 成熟度等级定义

| 等级 | 名称 | 定义 | 量化条件 |
|------|------|------|---------|
| L1 | 实验性 | 仅 1 次成功案例，待更多验证 | `validation_count = 1` |
| L2 | 已验证 | ≥ 2 次成功案例，模式稳定 | `validation_count ≥ 2` |
| L3 | 可复用 | 已被其他任务复用，有文档化示例 | `reuse_count ≥ 1` 且 `validation_count ≥ 2` |
| L4 | 标准化 | 已纳入规范体系，有自动化验证 | 已集成至 CI/工具链 |

### 量化指标说明

| 指标 | 字段名 | 定义 | 计数方式 |
|------|--------|------|---------|
| 验证次数 | `validation_count` | 模式被成功应用并验证的次数 | 每次成功应用后 +1 |
| 复用次数 | `reuse_count` | 模式被其他任务（非原作者）复用的次数 | 每次复用后 +1 |
| 文档化程度 | `documentation_level` | 模式文档的完整性 | basic/standard/comprehensive |

### 成熟度升级路径

```mermaid
flowchart LR
    L1["L1 实验性<br/>validation_count=1"] --> L2["L2 已验证<br/>validation_count≥2"]
    L2 --> L3["L3 可复用<br/>reuse_count≥1"]
    L3 --> L4["L4 标准化<br/>集成CI/工具链"]
```

### 成熟度标注规范

每个模式文件的 TOML frontmatter 必须包含以下字段：

```toml
+++
id = "pattern-id"
domain = "methodology|code|architecture"
layer = "methodology|code|architecture"
maturity = "L1|L2|L3|L4"
validation_count = 1
reuse_count = 0
documentation_level = "basic|standard|comprehensive"
source = "来源文档路径"

[bindings]
rules = []
references = []
skills = []
+++
```

### 成熟度更新流程

1. **验证次数更新**：每次成功应用模式后，在模式文件 frontmatter 中 `validation_count + 1`
2. **复用次数更新**：其他任务复用模式成功后，在模式文件 frontmatter 中 `reuse_count + 1`
3. **成熟度升级**：满足升级条件后，更新 `maturity` 字段
4. **文档化升级**：补充正反例、检查清单后，更新 `documentation_level` 字段

## 模式统计

| 目录 | 模式数 | L1 | L2 | L3 | L4 |
|------|--------|----|----|----|----|
| architecture-patterns/ | 8 | 1 | 7 | 0 | 0 |
| code-patterns/ | 11 | 1 | 5 | 0 | 2 |
| methodology-patterns/ | 96 | 51 | 38 | 7 | 0 |
| **合计** | **115** | **53** | **50** | **7** | **2** |

> > 注：统计数据截至 2026-06-30，由 pattern-maturity.py check-index --fix 自动更新。
> - TuyaOpen 学习报告优化（2 个方法论模式）：governance-strategy/`file-creation-precheck-pattern`（L2）、governance-strategy/`spec-discoverability-guarantee`（L1）
> - Specs 主题任务看板体系构建（3 个方法论模式）：governance-strategy/`three-tier-board-system`（L1）、governance-strategy/`progressive-requirement-clarification`（L1）、document-architecture/`mermaid-layered-visualization`（L2）
> - Ian Xiaohei 源码分析（6 个方法论模式 + 1 个架构模式）：ai-collaboration/`progressive-context-disclosure`、ai-collaboration/`output-behavior-specification`、ai-collaboration/`bilingual-prompt-engineering`、creative-design/`programmable-creativity-algorithm`、ai-collaboration/`symptom-prescription-qa`、ai-collaboration/`style-creativity-separation-control`（全部 L2）；architecture-patterns/ 新增 `dual-interface-repository`（L2）
> - 竹简悟道 Specs 分析（7 个方法论模式 + 1 个架构模式）：retrospective-knowledge/`insight-two-tier-structure`（L2）、retrospective-knowledge/`rolling-retro-eight-steps`（L3）、product-growth/`spec-nine-section-narrative`（L2）、document-architecture/`dual-audience-extraction-model`（L2）、product-growth/`three-layer-delivery-pipeline`（L3）、document-architecture/`document-entropy-three-strategies`（L3）、retrospective-knowledge/`insight-library-evolution`（L2）；architecture-patterns/ 新增 `five-layer-document-architecture`（L2）
> - Mermaid 渲染修复归档（2 个代码模式 + 1 个方法论模式更新）：code-patterns/`mermaid-safe-coding-rules`（L4）、code-patterns/`mermaid-trap-cheatsheet`（L4）；governance-strategy/`root-cause-diagnosis` 从 L1 升级为 L2，新增分层错误屏蔽概念
> - 此前已包含全链原子化、元级复盘萃取模式，以及 methodology-analysis-report 原子化的 8 个 L1 模式。

## 使用方式

1. 根据任务类型定位模式目录（架构/代码/方法论）
2. 在目录 README.md 中查找匹配场景的模式
3. 阅读模式正文了解规则与正反例
4. 按模式规则执行操作
5. 验证成功后更新模式成熟度（若适用）

## 相关文档

| 文档 | 说明 | 入口 |
|------|------|------|
| 复盘体系总览 | 复盘流程、报告结构、模式萃取 | [docs/retrospective/README.md](../README.md) |
| 资产清单 | 可复用资产索引 | [docs/retrospective/assets/asset-inventory.md](../assets/asset-inventory.md) |
