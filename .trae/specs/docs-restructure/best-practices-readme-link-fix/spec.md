---
version: 1.0
date: 2026-07-09
---

# Best-Practices 目录断链修复与入口文档建设 - Product Requirement Document

## Overview
- **Summary**: 对 `docs/knowledge/best-practices/` 目录下所有文件进行系统性断链检查，修复引用旧路径/已迁移文件的 Markdown 链接；创建结构化 README 入口文档（以八维检查法为核心，5分钟快速上手指南）；更新项目 CHANGELOG；最后执行完整复盘流程沉淀经验。
- **Purpose**: `docs/knowledge/best-practices/` 目录是团队最佳实践的核心沉淀区，近期从 `docs/retrospective/` 迁移了部分文档后，目录内存在多处路径错误（深度不对、目标文件已迁移/归档、frontmatter source字段过期），导致导航体验差、新成员难以快速理解最佳实践体系。需要系统性修复断链、建设入口文档、记录变更、复盘改进。
- **Target Users**: SpecWeave 团队新成员（快速理解八维检查法等最佳实践）、AI 智能体（文档导航与引用）、团队维护者（链接完整性保障）。

## Goals
- 系统性扫描并修复 `docs/knowledge/best-practices/` 下所有文件中指向 `docs/retrospective/` 的断链（包括路径深度错误、目标文件已迁移/不存在、frontmatter source字段过期）
- 在 `docs/knowledge/best-practices/` 下创建结构化 README.md，包含八维检查法核心概述、应用场景、使用流程、完整文档链接，实现新成员5分钟快速上手
- 更新项目根目录 CHANGELOG.md，按既有格式记录本次文档迁移修复的完整变更
- 执行标准化复盘流程（四步法），萃取本次文档迁移修复的经验教训与可复用最佳实践，导出复盘报告

## Non-Goals (Out of Scope)
- 不重构 `docs/retrospective/` 目录本身的结构
- 不迁移 `docs/knowledge/best-practices/` 下除 README 外的新文件
- 不修改 `docs/retrospective/patterns/` 或 `docs/retrospective/reports/` 中的任何内容
- 不修改 best-practices 下各文档的实质性内容（仅修复链接和 frontmatter 溯源字段）
- 不进行全项目范围的链接检查（仅聚焦 best-practices 目录内的引用）

## Background & Context
- 近期项目进行了多轮文档资产重构，将成熟的最佳实践文档从 `docs/retrospective/reports/` 沉淀到 `docs/knowledge/best-practices/` 目录（如 eight-dimensions-concurrent-safety-spec.md、concurrent-code-safety-review.md 等）
- 迁移后遗留了三类链接问题：
  1. **路径深度错误**：如 `b2b-product-info-collection-sop.md:145` 使用 `../retrospective/`（仅一级父目录），实际应为 `../../retrospective/`（两级父目录到达 docs/）
  2. **frontmatter source 字段过期**：多个文件的 YAML frontmatter 中 `source` 字段仍指向旧的 retrospective 路径
  3. **更新记录中的链接**：如 eight-dimensions 文件更新记录中引用了压力测试报告的路径，需确认目标文件是否存在
- best-practices 目录目前缺少统一入口 README，新成员无法快速了解有哪些最佳实践、如何使用八维检查法
- 项目已有成熟的 CHANGELOG 格式规范（`- YYYY-MM-DD | type | description`，`<!-- changelog -->` 标记区域）
- 项目已有标准化复盘流程和 retrospective-cmd 指令集

## Functional Requirements
- **FR-1**: 系统性扫描 `docs/knowledge/best-practices/` 下所有 11 个 .md 文件，识别所有包含 `retrospective` 字样的引用（Markdown 链接 `[text](path)`、frontmatter 字段、正文提及）
- **FR-2**: 对每个引用进行目标文件存在性验证，区分三类问题：(a) 路径深度错误 (b) 目标文件已归档/不存在 (c) frontmatter source 字段过期
- **FR-3**: 修复所有确认的断链，路径深度错误按正确层级修正，已迁移/不存在的目标文件标记为 inline code 或更新到正确位置，frontmatter source 字段更新为新位置
- **FR-4**: 创建 `docs/knowledge/best-practices/README.md`，包含：① 八维检查法核心概念概述（1段话+表格速览）② 关键应用场景 ③ 使用流程简介（5步上手）④ 所有 best-practices 文档的分类索引链接 ⑤ 延伸阅读指向 retrospective 体系
- **FR-5**: 更新根目录 `CHANGELOG.md`，在 `<!-- changelog -->` 标记下新增条目，格式遵循既有规范
- **FR-6**: 执行完整复盘流程，包括事实收集、过程分析、洞察萃取、最佳实践沉淀，导出 Markdown 格式复盘报告至 `docs/retrospective/reports/` 对应位置

## Non-Functional Requirements
- **NFR-1**: 链接修复后，best-practices 目录下不应有任何指向 retrospective 的断链（使用 `check-links.py --path docs/knowledge/best-practices` 验证通过）
- **NFR-2**: README.md 应控制在 200 行以内，确保新成员5分钟内可读完核心内容
- **NFR-3**: README.md 中的所有链接必须是有效相对路径，无 `file:///` 绝对路径
- **NFR-4**: 所有修改遵循项目 Markdown 规范和 YAML frontmatter 规范
- **NFR-5**: CHANGELOG 条目格式与既有条目一致，使用中文描述

## Constraints
- **Technical**: 使用项目已有的 `.agents/scripts/check-links.py` 进行链接验证；遵循既有的 Markdown/YAML 格式规范
- **Business**: 不破坏现有有效引用；不修改 best-practices 文档的实质性技术内容
- **Dependencies**: 依赖 `docs/retrospective/patterns/` 和 `docs/retrospective/reports/` 现有文件结构

## Assumptions
- `docs/retrospective/patterns/` 目录下的模式文件路径保持稳定（大多数 `../../retrospective/patterns/...` 引用是有效的）
- `docs/retrospective/reports/task-reports/` 和 `docs/retrospective/reports/project-reports/` 下近期复盘报告文件仍然存在
- README 面向的读者已经有基本的 Markdown 和项目导航能力
- 复盘流程使用项目既有的 retrospective-cmd / retrospective 相关技能

## Acceptance Criteria

### AC-1: 断链全面识别
- **Given**: best-practices 目录下有11个Markdown文件，部分文件包含 retrospective 路径引用
- **When**: 执行系统性扫描
- **Then**: 生成一份完整的引用清单，记录每个文件中所有 retrospective 引用的位置、当前路径、目标文件是否存在、问题分类
- **Verification**: `programmatic`
- **Notes**: 使用 Grep + 文件存在性检查脚本，确保覆盖 Markdown 链接、frontmatter、正文路径提及

### AC-2: 所有断链已修复
- **Given**: 扫描出的断链清单
- **When**: 逐一修复所有路径深度错误、过期 source 字段、失效目标链接
- **Then**: `python .agents/scripts/check-links.py --path docs/knowledge/best-practices` 执行通过，0 个断链
- **Verification**: `programmatic`

### AC-3: README 入口文档创建完成
- **Given**: best-practices 目录无 README 文件
- **When**: 创建结构化 README.md
- **Then**: README 包含八维检查法概述（含8维度表格速览）、3+个应用场景、5步使用流程、所有11个文档的分类索引、延伸阅读链接；总行数 ≤ 200；所有链接有效
- **Verification**: `human-judgment`

### AC-4: CHANGELOG 已更新
- **Given**: 项目 CHANGELOG.md 有既定格式
- **When**: 添加本次变更条目
- **Then**: CHANGELOG 在 `<!-- changelog -->` 后新增条目，格式为 `- 2026-07-09 | docs | description`，描述包含背景、迁移范围、优化内容和影响
- **Verification**: `programmatic`

### AC-5: 复盘报告完成
- **Given**: 本次文档迁移修复任务完成
- **When**: 执行四步复盘流程
- **Then**: 复盘报告包含 ① 事实收集（变更统计）② 过程分析（经验教训）③ 洞察萃取（关键发现）④ 最佳实践（标准化操作指南）⑤ 后续行动计划；报告导出至 `docs/retrospective/reports/` 对应目录
- **Verification**: `human-judgment`

### AC-6: 跨文件引用一致性
- **Given**: best-practices 目录下文件互引
- **When**: 修复链接后
- **Then**: best-practices 内部文件间的互链（如 eight-dimensions 与 concurrent-code-safety-review 互引）也必须有效
- **Verification**: `programmatic`

## Open Questions
- [ ] 是否需要在 knowledge/README.md 中更新 best-practices 条目数量（当前显示8个，实际已有11个文档+新增README）？—— 建议同步更新以保持索引一致性
- [ ] 复盘报告应放在 `docs/retrospective/reports/task-reports/` 下还是其他分类下？—— 建议放在 task-reports/ 下，遵循既有命名约定
