---
id: "full-lifecycle-retrospective-dedup-reorg"
title: "SpecWeave全生命周期复盘报告内容去重与重组整合"
x-toml-ref: "../../../../.meta/toml/.trae/specs/docs-restructure/full-lifecycle-retrospective-dedup-reorg/spec.toml"
version: "1.0"
date: "2026-07-05"
---
# SpecWeave全生命周期复盘报告内容去重与重组整合 - PRD

## Overview

- **Summary**: 对 `retrospective-specweave-full-lifecycle-20260705` 目录中10个文档的内容进行系统性冗余分析，识别重复信息片段，基于单一数据源（SSOT）原则和单一职责原则进行内容重组，消除重复描述，修正统计数据不一致问题，提升整体结构清晰度和可读性。重组后保持原有信息的准确性和完整性，通过交叉引用替代重复内容。
- **Purpose**: 该复盘目录经历了"初始四文件→原子化拆分→IA行动项执行→L3模式自举验证"三个阶段的增量追加，导致同一事实（核心统计、L3模式、四层防御体系、ha_api重构、IA行动项等）在多个文件中重复描述，且存在统计数字不一致（如800 vs 793提交、2800+ vs 2773+文件）。需要通过去重重组恢复文档体系的清晰结构。
- **Target Users**: 阅读该复盘报告的研究者、方法论构建者、未来复盘任务执行者

## Goals

- 识别并消除10个文档间的重复信息片段和冗余模块
- 修正统计数据不一致问题（提交数、文件数等），建立文档内SSOT
- 基于单一职责原则重新明确各文件边界，交叉引用替代重复内容
- 保持信息完整性，不丢失任何有价值的内容
- 提升整体结构清晰度和可读性
- 确保所有交叉引用链接有效

## Non-Goals (Out of Scope)

- 不改变复盘报告的核心结论和洞察
- 不重写或重新组织模式库中的L3模式文档（位于docs/retrospective/patterns/）
- 不修改.agents/目录下的规则、模板、ONBOARDING.md等IA行动项产物
- 不新增内容或新增洞察，仅做去重和重组
- 不对其他复盘报告目录做类似处理（本次仅针对目标目录）
- 不改变文档的YAML frontmatter元数据格式（id/title/version等字段保留）

## Background & Context

目标目录经历了以下增量演化过程，导致冗余累积：
1. **初始阶段**：标准四文件原子化复盘模板（README + execution-retrospective + insight-extraction + export-suggestions）
2. **原子化拆分**：应用"元原子化二分+概览"模式，拆分出execution-phases-s1-s3.md、execution-phases-s4-s7.md、l3-template-upgrade-details.md
3. **IA行动项执行阶段**：新增insight-action-backlog.md（行动清单）和final-execution-summary.md（执行总结），记录IA-01~IA-08落地情况
4. **自举验证阶段**：新增l3-pattern-application-report.md（L3模式应用报告），记录模板升级和ha_api重构验证

### 已识别的主要冗余类别

| 冗余类别 | 出现位置 | 重复次数 | 问题 |
|---------|---------|---------|------|
| 核心统计数据 | README.md、execution-retrospective.md、final-execution-summary.md | 3次 | 数字不一致：800 vs 793提交、2800+ vs 2773+文件 |
| 七阶段时间线概览 | README.md（按演化阶段表）、execution-retrospective.md（Mermaid图+概览）| 2次 | 信息重复，可保留一处+链接 |
| 5个L3模式列表 | export-suggestions.md、insight-extraction.md、l3-pattern-application-report.md、final-execution-summary.md、insight-action-backlog.md | 5-6次 | 模式描述重复列出 |
| 四层质量防御体系 | insight-extraction.md（1.10+模式5）、l3-pattern-application-report.md（§4.3）、README.md（Top3经验）、final-execution-summary.md（验证实践1）| 4次 | 架构描述重复 |
| ha_api.py零依赖重构 | execution-retrospective.md、insight-extraction.md、export-suggestions.md、l3-pattern-application-report.md、final-execution-summary.md | 5次 | 重构细节重复描述 |
| IA-01~IA-08行动项状态 | insight-action-backlog.md（主清单）、final-execution-summary.md（交付详情）、export-suggestions.md（已完成区）| 3次 | 行动项完成状态重复 |
| 16条核心成功要素 | insight-extraction.md（§二完整表）、README.md（Top3经验摘要）| 2次 | README仅摘要，问题不大但需核对 |
| 三阶段普遍规律 | insight-extraction.md、insight-action-backlog.md（IA-04）、final-execution-summary.md（IA-04交付）| 3次 | 原则描述重复 |
| 元文档优先原则 | insight-extraction.md、insight-action-backlog.md（IA-05）、final-execution-summary.md（IA-05交付）| 3次 | 原则描述重复 |
| 与6/26复盘对比 | README.md（末尾）、insight-extraction.md（§五完整对比）| 2次 | README有摘要，问题不大 |

### 统计数据不一致问题

| 指标 | README.md | execution-retrospective.md | final-execution-summary.md | 应统一为 |
|------|-----------|---------------------------|---------------------------|---------|
| Git提交数 | 800次 | 800次 | 793次（IA执行前）/ 800次（含后续5次提交）| 需核实Git log确认最终值 |
| 核心区文件数 | 2800+ | 2,800+ | 2773+（IA执行前）| 需统一口径 |
| Python脚本数 | ~155个（5.3万行）| ~155+ | ~155 | 统一为~155 |
| 可复用模式 | 237+（含5个L3）| 237+ | 237+ | 一致 |

## Functional Requirements

- **FR-1**: 系统性扫描10个文档，建立重复内容映射表（哪个内容在哪些文件的哪些位置出现）
- **FR-2**: 为每类重复信息确定单一数据源（SSOT）文件，其他文件改为链接引用+一句话摘要
- **FR-3**: 修正所有统计数据不一致问题，统一口径，并在SSOT位置明确数据的统计时间点和统计口径
- **FR-4**: 重新明确各文件的单一职责边界，确保每个文件聚焦一个主题
- **FR-5**: 将重复的详细描述从非SSOT文件中移除，替换为指向SSOT的链接
- **FR-6**: 更新README.md导航结构，反映重组后的文件职责
- **FR-7**: 确保所有交叉引用链接正确可访问

## Non-Functional Requirements

- **NFR-1**: 信息完整性——去重后不丢失任何有价值的具体信息（数据、事实、洞察、证据）
- **NFR-2**: 链接有效性——所有内部链接（相对路径+锚点）必须可正确跳转
- **NFR-3**: 可读性——重组后各文件职责清晰，阅读路径自然，不产生"需要来回跳转才能理解上下文"的问题
- **NFR-4**: 结构一致性——遵循项目已有的原子化文档规范（frontmatter、单一职责、入口精简）
- **NFR-5**: 最小变更原则——尽量保持文件结构稳定，不新增文件、不删除文件，仅修改文件内容

## Constraints

- **Technical**: 必须遵循项目Markdown规范（相对路径引用、无file:///绝对路径、frontmatter格式）
- **Business**: 不改变复盘结论，仅做去重和结构优化
- **Dependencies**: Python脚本`.agents/scripts/check-links.py`用于链接验证

## Assumptions

- 10个文档当前的整体结构（四文件+拆分文件+IA执行产物+L3验证报告）是合理的，不需要合并或删除文件
- 核心统计数据以Git历史最终状态为准（commit 5d4642c）
- 重复内容的SSOT选择遵循"最详细描述所在位置即为SSOT"原则
- final-execution-summary.md的"闭环后自举验证"部分（L3模式嵌入模板+ha_api重构+报告生成）是独特内容，不应删除，但其前置的IA-01~IA-08交付详情可精简为链接

## Acceptance Criteria

### AC-1: 重复内容消除
- **Given**: 识别出的9类主要冗余内容
- **When**: 完成重组后
- **Then**: 每类重复信息在目录中只有一处完整详细描述（SSOT），其他引用位置仅保留一句话摘要+链接
- **Verification**: `human-judgment`
- **Notes**: 评审者对照冗余映射表逐一检查

### AC-2: 统计数据一致性
- **Given**: 存在统计数字不一致问题
- **When**: 完成重组后
- **Then**: 所有核心统计指标（提交数、文件数、脚本数、模式数等）在所有文件中保持一致；SSOT位置标注统计口径和时间点
- **Verification**: `programmatic` + `human-judgment`
- **Notes**: 通过grep搜索关键数字，人工核对一致性

### AC-3: 文件职责清晰
- **Given**: 10个文件
- **When**: 完成重组后
- **Then**: 每个文件有明确的单一职责，无职责重叠；README.md保持入口导航性质（<120行）
- **Verification**: `human-judgment`
- **Notes**: 评审者按文件职责表检查

### AC-4: 链接全部有效
- **Given**: 重组可能涉及链接调整
- **When**: 运行链接检查
- **Then**: `python .agents/scripts/check-links.py --path <目标目录>` 报告零断链
- **Verification**: `programmatic`

### AC-5: 信息无丢失
- **Given**: 去重过程
- **When**: 完成重组后
- **Then**: 原始文档中的所有事实数据、洞察结论、关键证据均可在重组后的文档中找到（直接存在或通过链接可访问）
- **Verification**: `human-judgment`

### AC-6: 核心文件体量优化
- **Given**: 存在重复描述导致文件膨胀
- **When**: 完成重组后
- **Then**: README.md ≤ 120行；execution-retrospective.md概览性质保留，不重复细节；final-execution-summary.md精简IA交付重复部分
- **Verification**: `programmatic`

## Open Questions

- [ ] 核心统计数据（Git提交数800 vs 793）的最终口径：以哪个commit为准？建议以目录中记录的commit 5d4642c时的最终数据为准。
- [ ] final-execution-summary.md的IA交付详情部分：是完全精简为链接还是保留关键摘要表格？建议保留完成总览表+关键结论，详细交付物链接到insight-action-backlog.md。
