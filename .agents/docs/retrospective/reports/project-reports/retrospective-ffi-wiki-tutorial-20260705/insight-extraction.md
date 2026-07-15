---
id: "insight-extraction-ffi-wiki-tutorial-20260705"
title: "洞察提取：FFI Wiki 教程创建项目"
source: "retrospective:retrospective-ffi-wiki-tutorial-20260705"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/reports/project-reports/retrospective-ffi-wiki-tutorial-20260705/insight-extraction.toml"
category: "insight"
tags: ["insight", "ffi-wiki", "cross-reference", "agent-timeout", "spec-pattern", "5-whys"]
date: "2026-07-05"
status: "stable"
author: "SpecWeave"
analysis_target: "process"
summary: "基于 FFI Wiki 教程创建项目复盘报告的 3 个洞察进行 5-Whys 根因分析，覆盖跨 wiki 引用校验、Agent 超时策略、Spec 驱动验收标准三个维度。"
---
# 洞察提取：FFI Wiki 教程创建项目

## 洞察 1：跨 wiki 交叉引用缺乏自动化校验

### 现象

ffi-wiki 教程创建时，3 处指向 idl-wiki 的交叉引用因章节编号偏移导致断链：
- `04-use-cases.md` → `../idl-wiki/06-use-cases.md`（实际为 `07-use-cases.md`）
- `06-comparison.md` → `../idl-wiki/04-comparison.md`（实际为 `05-comparison.md`）
- `07-resources.md` → `../idl-wiki/06-use-cases.md`（实际为 `07-use-cases.md`）

### 5-Whys 根因分析

| 层 | 问题 | 回答 |
|---|---|---|
| Why 1 | 为什么出现 3 处断链？ | ffi-wiki 引用 idl-wiki 时章节编号错误 |
| Why 2 | 为什么章节编号会错误？ | 引用时假设了 idl-wiki 的章节编号，但实际编号与假设不符（idl-wiki 的章节编排为 04-major-idl-specs / 05-comparison / 06-toolchain / 07-use-cases） |
| Why 3 | 为什么没有先确认实际编号再引用？ | 创建 ffi-wiki 时，Agent 没有先读取 idl-wiki 的目录文件（00-overview.md）确认章节结构 |
| Why 4 | 为什么 Agent 没有读取目标目录？ | AGENTS.md 启动协议和 spec 模板都没有强制要求"跨 wiki 引用前先读取目标目录文件确认章节编号" |
| Why 5 | 为什么没有这个强制要求？ | 跨 wiki 引用的校验完全依赖链接检查工具的事后验证，而链接检查工具仅验证文件是否存在（不验证章节编号一致性），缺乏事前预防机制 |

### 根因总结

**根本原因**：当前工作流中，跨 wiki 引用校验完全依赖事后链接检查（`check-links.py`），缺乏事前预防机制——Agent 在创建引用时凭"假设"而非"查询"确定目标章节编号。链接检查工具功能边界仅为文件存在性验证，不涵盖章节编号一致性。

### 改进建议

1. **短期**：在 AGENTS.md 或 spec 模板中增加"跨 wiki 引用前必须读取目标 wiki 的 00-overview.md 确认章节编号"的强制步骤
2. **中期**：扩展 `check-links.py` 增加 `--verify-chapter-numbers` 模式，读取目标文件 frontmatter 的 `title` 字段验证章节一致性
3. **长期**：建立跨 wiki 引用注册表，所有交叉引用在创建时自动注册，变更时自动通知引用方

---

## 洞察 2：信息密度高的章节更适合串行生成

### 现象

01-what-is-ffi.md（251 行）和 02-working-principles.md（228 行）的 Agent 写入超时，需要人工验证文件完整性。其他 6 个章节（77-232 行）均顺利完成。

### 5-Whys 根因分析

| 层 | 问题 | 回答 |
|---|---|---|
| Why 1 | 为什么 01/02 章节 Agent 超时？ | 这两个章节的生成时间超出了 Agent 的超时阈值 |
| Why 2 | 为什么生成时间过长？ | 这两个章节信息密度最高（251 行 + 228 行），包含大量代码示例（C/Python 混合代码块）、Mermaid 图表（时序图 + 对照表）和结构化内容 |
| Why 3 | 为什么信息密度高的章节和低密度章节采用相同的生成策略？ | tasks.md 将所有 8 个章节标记为"可并行生成"，没有区分信息密度和复杂度 |
| Why 4 | 为什么 tasks.md 没有标注复杂度差异？ | spec.md 和 tasks.md 模板没有"预计复杂度"或"推荐生成策略"字段，所有章节被默认为同质任务 |
| Why 5 | 为什么没有这个字段？ | 任务拆分模板（tasks.md）是通用模板，不考虑 Agent 执行时的资源约束（超时时间、上下文窗口等），将"任务可并行"与"任务应并行"混为一谈 |

### 根因总结

**根本原因**：任务拆分模板缺乏"复杂度标注"机制，导致所有任务被无差别地标记为可并行。Agent 的资源约束（超时时间、上下文窗口）在任务规划阶段不被考虑，信息密度高的章节在并行模式下超出单 Agent 的时间预算。

### 改进建议

1. **短期**：在 tasks.md 中为每个章节添加"预计行数"和"复杂度（高/中/低）"标注，高复杂度章节采用串行生成
2. **中期**：在 spec 模板中增加"任务复杂度矩阵"，映射复杂度→推荐生成策略（串行/并行/拆分）
3. **长期**：建立 Agent 资源预算模型，根据章节预估行数和代码块数量自动选择生成策略

---

## 洞察 3：Spec 驱动的验收标准是可复用的质量保证模式

### 现象

spec.md 中 11 条 Acceptance Criteria 采用了"程序化验证 + 人工判断"双轨模式，覆盖了目录结构、内容、元数据、导航、链接、代码质量 6 个维度。checklist.md 的 94 项检查点全部基于这些标准，质量验证过程系统化、可追溯。

### 5-Whys 根因分析

| 层 | 问题 | 回答 |
|---|---|---|
| Why 1 | 为什么这次质量验证特别高效？ | spec.md 定义了清晰的验收标准，每条 AC 都有明确的验证方式 |
| Why 2 | 为什么 AC 定义得如此清晰？ | spec.md 采用了"programmatic + human-judgment"双轨验证，将可自动化验证的指标（行数、链接、frontmatter）与需人工判断的指标（内容质量、技术深度）分离 |
| Why 3 | 为什么这种双轨模式是有效的？ | 它避免了两个极端：纯程序化验证无法评估内容质量（"格式正确但内容空洞"），纯人工判断无法保证客观指标的一致性（"看起来差不多"） |
| Why 4 | 为什么这个模式没有被标准化为模板？ | 当前 spec 模板是通用模板，没有针对 wiki 教程的专门变体，AC 的验证方式标注是可选的而非强制的 |
| Why 5 | 为什么没有强制要求？ | 项目对 spec 的验收标准约定是"建议实践"而非"强制规范"，缺乏 AC 验证方式标注的合规检查 |

### 根因总结

**根本原因**：spec 模板中 AC 验证方式标注是可选的非强制约定，导致不同 spec 的验收标准质量参差不齐。本次 spec 的 AC 定义质量高，是因为创建者主动采用了最佳实践，而非流程强制保证。

### 改进建议

1. **短期**：将 AC 验证方式标注（programmatic/human-judgment）从"建议"升级为 spec 模板的"必填字段"
2. **中期**：创建 wiki 教程专用 spec 模板（`spec-template-wiki-tutorial.md`），内置 AC 验证方式标注和 checklist 生成规则
3. **长期**：在 `check-spec-consistency.py` 中增加"AC 验证方式标注检查"规则，未标注的 AC 标记为警告

---

## 洞察优先级矩阵

| 洞察 | 影响范围 | 发生频率 | 修复成本 | 优先级 |
|---|---|---|---|---|
| 跨 wiki 引用校验缺失 | 所有跨教程引用 | 每次新建 wiki 教程 | 低（流程约束） | **高** |
| 复杂度标注缺失 | 所有并行任务 | 信息密度高时 | 中（模板修改） | **中** |
| AC 验证方式非强制 | 所有 spec 质量 | 新建 spec 时 | 中（模板 + 检查工具） | **中** |

---

## 关联资源

- [复盘报告](retrospective-report.md)
- [spec:create-ffi-wiki-tutorial](../../../../../../.trae/specs/core-foundation/create-ffi-wiki-tutorial/spec.md)
- [链接检查工具](../../../../../scripts/check-links.py)
- [Spec 一致性检查工具](../../../../../scripts/check-spec-consistency.py)