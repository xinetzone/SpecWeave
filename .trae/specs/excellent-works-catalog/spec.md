---
title: 优秀作品结构化归档与目录索引系统 - PRD
date: 2026-07-22
content_sensitivity: private
---

# 优秀作品结构化归档与目录索引系统 - Product Requirement Document

## Overview

- **Summary**: 系统梳理 SpecWeave 工作区内所有经过验证、达到质量标准的优秀产出物（可复用模式、最佳实践、项目报告、工具脚本、学习wiki等），建立多维度分类体系，为每件作品添加结构化元数据描述，最终生成一份可检索、可浏览、可导航的统一目录索引。
- **Purpose**: 解决当前工作区"资产散落在各处、优秀成果难以发现、复用率低"的问题。工作区已积累 380+ 可复用模式、25+ 最佳实践、数十份项目报告和大量学习wiki，但缺乏统一入口和元数据标注，导致知识沉淀与实际复用之间存在断层。
- **Target Users**: SpecWeave 内部运营团队、项目开发者、AI智能体协作时的资产检索。

## Goals

1. **全面盘点**：识别并收录工作区内所有符合"优秀作品"标准的产出物
2. **多维分类**：建立按作品类型、技术领域、成熟度等级、创作时间、应用场景的五维分类体系
3. **元数据标注**：为每件作品添加结构化元数据（创作背景、核心特点、技术亮点、应用效果、文件路径等）
4. **索引生成**：产出一份清晰的 Markdown 目录索引，支持快速检索和导航
5. **原始保留**：不移动、不修改任何原始文件，仅做元数据增强和索引编排

## Non-Goals (Out of Scope)

- 不对原始作品文件做任何内容修改或重构
- 不创建新的模式/最佳实践/报告（仅整理已有内容）
- 不建立数据库或Web应用（仅生成静态Markdown索引）
- 不包含外部链接的第三方内容（仅工作区内的本地产出物）
- 不对L1实验性模式做深度元数据标注（仅基础索引信息）
- 不迁移或重构现有目录结构

## Background & Context

SpecWeave 工作区经过长期积累，已形成丰富的知识资产体系：

| 资产类型 | 位置 | 数量 | 质量标记 |
|---------|------|------|---------|
| 可复用模式 | `.agents/docs/retrospective/patterns/` | ~380个 | 成熟度L1-L4（L4已集成CI） |
| 最佳实践 | `.agents/docs/knowledge/best-practices/` | ~25篇 | 经过实战验证 |
| 项目复盘报告 | `.agents/docs/retrospective/` 根目录 | ~15份 | R-I-E完整闭环 |
| 项目分析报告 | `playground/reports/` | ~6个项目 | 完整分析+洞察+模式萃取 |
| 大赛作品分析 | `playground/semi-final-analysis/` | 4份 | TRAE大赛350件复赛作品分析 |
| 学习wiki | `.agents/docs/knowledge/learning/` | ~30+个wiki | 结构化学习笔记 |
| 可复用脚本 | `.agents/scripts/` | ~数十个 | 有测试覆盖 |
| 模板/清单 | `.agents/templates/` `.agents/checklists/` | ~数十个 | 标准化模板 |

当前存在的问题：
- 资产分散在 `.agents/` 和 `playground/` 两个大区域，缺乏统一视图
- patterns/ 有 TOML frontmatter 元数据但缺乏统一的人类可读索引
- best-practices/ 和 reports/ 缺乏统一的元数据标准
- 没有按"应用场景"或"问题类型"的导航入口
- 新人或AI智能体难以快速找到"遇到X问题该看哪个模式"

## Functional Requirements

- **FR-1 优秀作品识别标准**：制定明确的入选标准（Tier 1/2/3三级）
- **FR-2 五维分类体系**：作品类型、技术领域、成熟度、创作时间、应用场景
- **FR-3 元数据Schema**：定义统一的元数据字段（必选+可选）
- **FR-4 原始文件扫描**：遍历工作区识别符合标准的文件
- **FR-5 元数据提取**：从现有frontmatter/README中自动提取基础元数据
- **FR-6 元数据补充**：对Tier 1/Tier 2作品补充详细描述
- **FR-7 分类索引生成**：按五个维度分别生成分类视图
- **FR-8 总目录索引**：生成统一的入口文档（README形式）
- **FR-9 路径可导航**：所有文件引用使用可点击的相对路径链接
- **FR-10 Mermaid可视化**：生成分类体系概览图和作品分布统计图

## Non-Functional Requirements

- **NFR-1 可检索性**：索引文档支持Ctrl+F关键词搜索，标签体系覆盖同义词
- **NFR-2 可维护性**：元数据Schema简洁，新增作品时易于补充索引
- **NFR-3 零侵入性**：不修改任何原始文件的内容和frontmatter
- **NFR-4 路径准确性**：所有链接必须可点击跳转，无死链
- **NFR-5 一致性**：元数据字段命名、分类标签、成熟度标注保持统一
- **NFR-6 产出位置**：最终索引文档放在 `playground/excellent-works-catalog/` 目录下（私域工作流）

## Constraints

- **Technical**: 仅使用Markdown格式，不引入数据库或外部工具；Mermaid图表需通过check-mermaid.py语法检查
- **Business**: 这是知识整理任务，不涉及代码功能开发；工作量需控制在合理范围（Tier 3仅做基础索引）
- **Dependencies**: 依赖现有文件的frontmatter和README作为基础元数据源；依赖check-mermaid.py进行图表验证

## Assumptions

1. L3-L4模式（约15个）和L2模式（约60个）是核心优秀作品，需要详细元数据
2. L1模式（约80+个）处于实验阶段，仅做基础索引不做深度标注
3. 所有.patterns文件已包含TOML frontmatter（id/domain/maturity等字段）
4. best-practices文件可能没有统一的frontmatter，需要从标题和内容推断
5. playground/reports/下的项目报告通过目录结构判断完整性
6. 用户期望的"优秀作品"范围是工作区内已有的高质量产出，而非TRAE大赛的外部参赛作品

## Acceptance Criteria

### AC-1: 优秀作品入选标准明确
- **Given**: 工作区文件系统
- **When**: 执行优秀作品识别
- **Then**: 形成清晰的Tier 1/2/3三级入选标准，每级有明确的判定条件
- **Verification**: `human-judgment`

### AC-2: 五维分类体系完整
- **Given**: 已识别的优秀作品列表
- **When**: 应用分类体系
- **Then**: 每件作品至少被标注到3个维度（类型+领域+成熟度），分类标签互斥且穷尽
- **Verification**: `human-judgment`

### AC-3: Tier 1作品元数据完整
- **Given**: Tier 1精选作品（L3-L4模式+核心best-practices+重大报告）
- **When**: 生成元数据
- **Then**: 每件Tier 1作品包含：标题、创作背景、核心特点、技术亮点、应用效果、成熟度、验证次数、原始路径、关联模式 共9个字段
- **Verification**: `human-judgment`

### AC-4: 目录索引可导航无死链
- **Given**: 生成的索引文档
- **When**: 检查所有文件链接
- **Then**: 所有相对路径链接可正确跳转到对应文件，无404/死链
- **Verification**: `programmatic`（通过link-check-cmd或手动验证）

### AC-5: Mermaid分类概览图正确渲染
- **Given**: 生成的Mermaid图表
- **When**: 通过check-mermaid.py检查
- **Then**: 0错误0警告，在VS Code预览中正确渲染
- **Verification**: `programmatic`

### AC-6: 原始文件零修改
- **Given**: 整理前后的工作区
- **When**: 对比git status
- **Then**: 除新增的catalog目录外，无其他文件被修改
- **Verification**: `programmatic`

### AC-7: 多维度索引视图
- **Given**: 完成的总索引
- **When**: 浏览索引文档
- **Then**: 至少包含按类型、按领域、按成熟度、按时间四种分类视图，加上一个全量字母序索引
- **Verification**: `human-judgment`

### AC-8: 产出位置符合私域规范
- **Given**: 生成的所有文件
- **When**: 检查文件位置
- **Then**: 所有产出文件位于 `playground/excellent-works-catalog/` 下，包含frontmatter标记content_sensitivity
- **Verification**: `programmatic`

## Open Questions

- [ ] 是否需要包含apps/目录下的应用代码作为"优秀作品"？（apps/目前只有chaos一个demo项目）
- [ ] learning wiki中有大量外部学习笔记（如MaineCoon/Codex分析），是否纳入"优秀作品"？
- [ ] 目录索引是否需要生成HTML版本以便于浏览？
- [ ] 元数据中的"应用效果"字段，如果原始文档没有明确记录，是否留空或标注"待补充"？
