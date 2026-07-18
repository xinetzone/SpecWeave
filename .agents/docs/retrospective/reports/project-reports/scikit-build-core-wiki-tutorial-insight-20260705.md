---
version: "1.0"
id: "insight-scikit-build-core-wiki-tutorial-20260705"
title: "scikit-build-core Wiki 教程创建洞察萃取"
source: "retrospective:scikit-build-core-wiki-tutorial-20260705"
category: retrospective
type: insight-extraction
tags: ["insight", "scikit-build-core", "source-anchor-verification", "pattern-upgrade", "contract-document"]
date: "2026-07-05"
status: "stable"
author: "SpecWeave"
summary: "从 scikit-build-core Wiki 教程创建任务中萃取 3 个洞察：源码锚点二次校验协议（新模式）、navigation-hub-filename-contract 升级 L2、spec-driven-batch-doc-generation 升级 L2"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/reports/project-reports/scikit-build-core-wiki-tutorial-insight-20260705.toml"
---
# scikit-build-core Wiki 教程创建 — 洞察萃取

## 洞察概览

从本次任务中萃取 3 个可复用洞察，其中 1 个为 P0 级新模式，2 个为现有模式升级。

| 洞察 | 类别 | 优先级 | 处理方式 |
|------|------|--------|---------|
| 1. 源码锚点二次校验协议 | 工程模式 | P0 | 新建模式 `source-anchor-verification-protocol` |
| 2. navigation-hub-filename-contract 升级 L2 | 模式成熟度 | P0 | 升级现有模式 L1→L2 |
| 3. spec-driven-batch-doc-generation 升级 L2 | 模式成熟度 | P1 | 升级现有模式 L1→L2 |

---

## 洞察 1：源码锚点二次校验协议（P0 新模式）

### 5-Whys 根因分析

- **问题**：02-project-structure.md sub-agent 发现研究摘要记录的源码行号多处偏差达 300+ 行（process_overrides 实际 L354 vs 研究摘要记录 L38，偏差 316 行）
- **Why1**：为什么研究摘要的行号有偏差？→ 研究 sub-agent 在快速浏览源码时记录行号，未通过 Grep/Read 二次校验
- **Why2**：为什么研究 sub-agent 未进行二次校验？→ 研究 sub-agent 的任务模板中没有"行号二次校验"必填项
- **Why3**：为什么任务模板中没有这一项？→ 研究阶段被定位为"快速产出摘要"，行号被视为"线索"而非"事实"，没有意识到下游 sub-agent 会直接引用这些行号
- **Why4**：为什么没有意识到下游会直接引用？→ 研究阶段和章节编写阶段之间没有明确的"行号准确度契约"——研究 sub-agent 不知道下游会直接引用，章节 sub-agent 不知道上游未校验
- **Why5**：**根因**→ 缺乏"研究-编写"阶段间的质量传递机制——研究阶段的产出（行号、文件名、API 签名等）应标注"已校验"或"未校验"状态，章节 sub-agent 应根据状态决定是否二次校验

### 模式描述

**名称**：源码锚点二次校验协议（Source Anchor Verification Protocol）

**触发条件**：
- 研究 sub-agent 产出包含源码行号、API 签名、文件路径等技术引用的摘要文档
- 下游 sub-agent（章节编写、文档生成）需要引用这些技术锚点
- 锚点偏差会导致下游产出物的可追溯性受损

**核心动作**：

1. **研究阶段标注校验状态**：研究 sub-agent 在记录每个源码锚点（行号、API 签名、文件路径）时，必须通过 Grep/Read 二次校验，并在研究文档中标注校验状态：
   - `✅ 已校验`：通过 Grep/Read 确认行号准确
   - `⚠️ 未校验`：基于快速浏览记录，需下游校验
   - `🔍 待校验`：基于推测，必须下游校验

2. **章节阶段根据状态决策**：章节 sub-agent 引用研究摘要的锚点时，根据校验状态决定是否二次校验：
   - `✅ 已校验`：可直接引用
   - `⚠️ 未校验`：引用前必须 Grep/Read 校验
   - `🔍 待校验`：禁止直接引用，必须 Grep/Read 校验后引用

3. **校验成本权衡**：
   - 研究阶段校验：1 次校验成本，下游 N 个章节受益
   - 章节阶段校验：N 次校验成本（每个引用锚点的章节都要校验）
   - 推荐策略：研究阶段对高频引用的关键锚点（≥3 个章节会引用）进行校验，低频锚点交给章节阶段校验

**预期收益**：
- 行号准确率从 ~98%（偶发偏差 300+ 行）提升至 100%
- 避免章节 sub-agent 盲目信任研究摘要导致的连锁修正成本
- 建立研究-编写阶段的质量传递契约

**反模式**：
- ❌ 研究 sub-agent 不标注校验状态，章节 sub-agent 盲目信任
- ❌ 章节 sub-agent 对所有锚点都二次校验（成本过高）
- ❌ 研究 sub-agent 对所有锚点都校验（可能延误研究进度）

**与现有模式关系**：
- 补充 [triangular-source-verification](../../patterns/methodology-patterns/retrospective-knowledge/triangular-source-verification.md)（三源验证法）的"单源内部校验"维度——三源验证法解决"跨源一致性"，本模式解决"单源内部准确度"
- 补充 [navigation-hub-filename-contract](../../patterns/methodology-patterns/ai-collaboration/navigation-hub-filename-contract.md)（导航枢纽文件名契约）的"契约传递"维度——前者解决文件名契约，本模式解决行号契约

---

## 洞察 2：navigation-hub-filename-contract 升级 L2（P0 模式升级）

### 5-Whys 根因分析

- **问题**：`navigation-hub-filename-contract` 模式在 IDL wiki 任务（首次验证）中识别，本次 scikit-build-core wiki 任务是否再次验证其有效性？
- **Why1**：为什么本次任务可以再次验证？→ 本次任务通过 60.5KB 契约文档传递完整文件命名契约，7 个 sub-agent 全部正确命名
- **Why2**：为什么契约文档传递有效？→ 契约文档包含 7 文件清单、YAML frontmatter 模板、相对路径规则、导航链接格式，sub-agent 读取后无需推断
- **Why3**：为什么对比 IDL wiki 任务效果更好？→ IDL wiki 任务的 00-overview.md sub-agent 未收到完整契约，自行推断 6 个文件名错误；本次所有 sub-agent 都收到完整契约
- **Why4**：为什么本次所有 sub-agent 都收到完整契约？→ 主 agent 从 IDL wiki 复盘洞察中学习了"文件名契约必须显式锁定"的教训
- **Why5**：**根因**→ 模式可复用性已通过两次独立任务验证（IDL wiki + scikit-build-core wiki），从 L1（首次验证）升级为 L2（二次验证）

### 模式升级方案

**模式**：[navigation-hub-filename-contract](../../patterns/methodology-patterns/ai-collaboration/navigation-hub-filename-contract.md)

**升级内容**：
- 成熟度：L1 → L2
- validation_count：1 → 2
- reuse_count：0 → 1
- 新增验证证据：scikit-build-core wiki 任务（7 sub-agent 全部正确命名，0 断链）

**升级依据**：
- L1 首次验证（IDL wiki）：9 个 sub-agent 中 8 个文件名正确（仅 00-overview.md 因未收到契约而错误），10 个断链集中在导航枢纽文件
- L2 第二次验证（scikit-build-core wiki）：7 个 sub-agent 全部正确，0 断链——通过 60.5KB 契约文档传递完整文件命名契约

**模式扩展**：
- 原模式聚焦"导航枢纽文件的全局文件名清单"
- 本次验证发现，契约文档（≥30KB）可以作为更通用的协调机制，不仅传递文件名，还传递 frontmatter 模板、相对路径规则、导航链接格式
- 建议在模式文档中补充"契约文档作为协调中枢"的扩展说明

---

## 洞察 3：spec-driven-batch-doc-generation 升级 L2（P1 模式升级）

### 5-Whys 根因分析

- **问题**：`spec-driven-batch-doc-generation` 模式在 MyST 统一化生态体系阶段1（2026-07-04）中识别为 L1，本次 scikit-build-core wiki 任务是否再次验证？
- **Why1**：为什么本次任务可以再次验证？→ 本次任务采用 Spec 驱动（spec.md + tasks.md + checklist.md）+ 并行 sub-agent（7 个）+ 统一验证（30/30 检查点）的工作流
- **Why2**：为什么这个工作流有效？→ Spec 模式将大任务分解为可验证的小任务，每个 sub-agent 收到精确的契约文档，避免大模型一次性生成大尺寸产出物时的"前重后轻"问题
- **Why3**：为什么避免了"前重后轻"问题？→ 契约文档提供了精确的章节大纲，sub-agent 只需"填充"而非"设计"，注意力集中在内容质量而非结构设计
- **Why4**：为什么 30/30 检查点全部通过？→ checklist.md 提供了严格的质量门，覆盖源码准备、目录结构、内容完整性、文档规范、索引链接、交叉引用 6 大类
- **Why5**：**根因**→ 模式可复用性已通过多次独立任务验证（MyST 统一化 + IDL wiki + scikit-build-core wiki + tvm-ffi wiki），从 L1 升级为 L2

### 模式升级方案

**模式**：[spec-driven-batch-doc-generation](../../patterns/methodology-patterns/ai-collaboration/spec-driven-batch-doc-generation.md)

**升级内容**：
- 成熟度：L1 → L2
- validation_count：1 → 4（MyST 统一化 + IDL wiki + scikit-build-core wiki + tvm-ffi wiki）
- reuse_count：0 → 3
- 新增验证证据：scikit-build-core wiki 任务（7 文件 12.3 万字符，30/30 检查点通过）

**升级依据**：
- L1 首次验证（MyST 统一化）：批量产出风格一致的技术文档
- L2 多次验证：
  - IDL wiki（9 文件 1969 行）
  - scikit-build-core wiki（7 文件 12.3 万字符）
  - tvm-ffi wiki（17 文件分组并行）
- 四次任务均采用 Spec 驱动 + 并行 sub-agent + 统一验证的工作流

**模式扩展**：
- 原模式聚焦"知识库素材 + Spec 模板"
- 本次验证发现，当知识库素材不足时（如 scikit-build-core 需要从源码研究），可以通过"研究 sub-agent + 契约文档"补充素材
- 建议在模式文档中补充"研究-契约-编写"三阶段扩展说明

---

## 行动项更新

| 行动项 | 优先级 | 来源洞察 | 验收标准 | 状态 |
|--------|--------|---------|---------|------|
| A1: 沉淀"源码锚点二次校验协议"为新模式 | 🔴 高 | 洞察 1 | 新建 `source-anchor-verification-protocol.md`，入库 `docs/retrospective/patterns/methodology-patterns/ai-collaboration/`，标注 L1 成熟度 | 🗓️ 待执行 |
| A2: 升级 navigation-hub-filename-contract 至 L2 | 🔴 高 | 洞察 2 | 更新模式文档的 validation_count（1→2）、reuse_count（0→1）、maturity（L1→L2），补充"契约文档作为协调中枢"扩展说明 | 🗓️ 待执行 |
| A3: 升级 spec-driven-batch-doc-generation 至 L2 | 🟡 中 | 洞察 3 | 更新模式文档的 validation_count（1→4）、reuse_count（0→3）、maturity（L1→L2），补充"研究-契约-编写"三阶段扩展说明 | 🗓️ 待执行 |

---

## 与其他洞察报告的关系

| 洞察报告 | 任务 | 关键洞察 | 模式沉淀 |
|---------|------|---------|---------|
| [idl-wiki-tutorial-retro-20260704.md](idl-wiki-tutorial-retro-20260704.md) | IDL Wiki 教程 | 文件名契约锁定 | navigation-hub-filename-contract（L1） |
| [retrospective-tvm-ffi-wiki-tutorial-20260705/insight-extraction.md](../task-reports/retrospective-tvm-ffi-wiki-tutorial-20260705/insight-extraction.md) | TVM FFI Wiki 教程 | 高层文档优先研究法、工具故障降级、主题分组并行写作 | 待沉淀（P0×2 + P1×1） |
| **本报告** | scikit-build-core Wiki 教程 | 源码锚点二次校验、模式升级 L2 | source-anchor-verification-protocol（L1 新建）+ 模式升级×2 |

**三份 wiki 教程洞察报告互补关系**：
- IDL wiki（首次）：识别"文件名契约"问题 → 沉淀 `navigation-hub-filename-contract`（L1）
- tvm-ffi wiki（第三次）：识别"研究方法"和"降级策略"问题 → 待沉淀 3 个新模式
- scikit-build-core wiki（第二次）：识别"行号准确度"问题 → 沉淀 `source-anchor-verification-protocol`（L1），同时验证前序模式可升级 L2

## Changelog

<!-- changelog -->
- 2026-07-05 | docs | v1.0：scikit-build-core Wiki 教程创建洞察萃取，3 个洞察（源码锚点二次校验协议 P0 新模式 + navigation-hub-filename-contract 升级 L2 + spec-driven-batch-doc-generation 升级 L2），3 项行动项
