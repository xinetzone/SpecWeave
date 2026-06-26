---
version: "1.0"
date: "2026-06-26"
status: "draft"
scope: "project-governance-reports-reorganization"
---

# project-governance 复盘报告系统性重组 - Product Requirement Document

## Overview

- **Summary**: 对 `docs/retrospective/reports/project-governance/` 目录下的 18 个复盘报告目录和 1 个独立报告文件进行主题分类重组，建立 5 个清晰的主题子目录，生成分类索引 README.md，确保文档组织有序、主题关联明确、查阅路径清晰。
- **Purpose**: 当前 project-governance 目录下 19 份报告平铺存放，缺乏主题分类，随着报告数量增长（从 README 记录的 12 份增长到 19 份），已出现文档定位困难、主题关联性弱、与项目整体分类体系不一致等问题。需要参照其他主题目录（atomization/insight-extraction/spec-system 等）的组织方式，建立二级分类体系。
- **Target Users**: 项目维护者、AI 智能体、查阅复盘经验的开发者

## Goals

- 建立 MECE（相互独立、完全穷尽）的 5 主题分类体系，覆盖现有全部 19 份报告
- 将 18 个报告目录和 1 个独立文件迁移至对应主题子目录
- 修复因目录迁移导致的所有相对路径引用断链
- 生成主题分类索引 README.md，包含主题定义、报告清单、Mermaid 关联图
- 更新上层文档（docs/retrospective/README.md）中的目录树与描述
- 确保所有本地链接引用有效（0 断链）

## Non-Goals (Out of Scope)

- 不修改报告文件的内部内容（仅更新因迁移导致的相对路径引用）
- 不改变报告的原子化四件套结构（README.md + execution-retrospective.md + insight-extraction.md + export-suggestions.md）
- 不将报告移出 project-governance 目录到其他顶层主题目录（所有重组在 project-governance 内部完成）
- 不重命名报告目录本身（保持现有 kebab-case 命名不变）
- 不进行内容去重或内容优化（仅做结构性重组）

## Background & Context

### 现有文档清单

通过目录扫描，project-governance 目录下现有以下资产：

| 序号 | 报告名称 | 类型 | 核心主题 |
|------|---------|------|---------|
| 1 | reports-duplication-optimization-report.md | 独立文件 | 文档重复内容优化 |
| 2 | retrospective-comprehensive-20260623/ | 目录 | 2026-06-23 综合复盘（已原子化6模块） |
| 3 | retrospective-export-20260623/ | 目录 | 复盘报告导出卡片 |
| 4 | retrospective-report-code-wiki-generation/ | 目录 | Code Wiki 文档生成工具 |
| 5 | retrospective-report-create-apps-directory/ | 目录 | apps/ 工作空间创建与流程协议 |
| 6 | retrospective-report-suggestion-execution-and-pattern-import/ | 目录 | 改进建议执行与模式导入 |
| 7 | retrospective-report-system-planning/ | 目录 | README 系统规划章节设计 |
| 8 | retrospective-report-tool-entropy-nonlinear-optimization/ | 目录 | 工具熵非线性优化 |
| 9 | retrospective-readme-sync-and-brand-naming-20260624/ | 目录 | README 同步与品牌命名一致性 |
| 10 | retrospective-session-agents-md-violation-20260624/ | 目录 | AGENTS.md 启动协议合规性复盘 |
| 11 | retrospective-project-comprehensive-20260625/ | 目录 | 项目级全面复盘（3天节点） |
| 12 | retrospective-specweave-demo-production-flow-20260625/ | 目录 | SpecWeave Demo 制作流程探索 |
| 13 | retrospective-zhujian-wudao-apps-archiving-20260625/ | 目录 | 竹简悟道参赛作品归档 |
| 14 | retrospective-xinet-content-extraction-archiving-20260625/ | 目录 | xinet 内容萃取与归档 |
| 15 | retrospective-insights-reorg-20260626/ | 目录 | 竹简悟道洞察库重组 |
| 16 | retrospective-link-fix-depth-adjustment-20260626/ | 目录 | 断链修复与链接校正工具增强 |
| 17 | retrospective-mermaid-rendering-fix-20260626/ | 目录 | Mermaid 渲染兼容性修复 |
| 18 | retrospective-specweave-full-project-comprehensive-20260626/ | 目录 | 项目全面复盘分析报告（4天结项） |

### 分类参考体系

项目已有的其他复盘主题目录采用单层主题分类，每个主题下直接存放报告目录：
- `atomization/` - 原子化与文档重构
- `insight-extraction/` - 洞察与萃取
- `spec-system/` - 规范体系建设
- `roles-teams/` - 角色与团队管理
- `competitive-analysis/` - 竞品分析

本次重组参照此模式，在 project-governance 下建立二级主题分类。

## Functional Requirements

- **FR-1**: 建立 5 个主题子目录，每个目录有明确的主题定义与边界
- **FR-2**: 19 份报告全部迁移至对应主题子目录，无遗漏
- **FR-3**: 迁移过程中保留所有文件内容，不做修改（路径引用除外）
- **FR-4**: 自动或手动修复因目录层级变化导致的相对路径断链
- **FR-5**: 生成 project-governance/README.md 作为主题分类索引
- **FR-6**: 每个主题子目录下生成 README.md 作为该主题的导航索引
- **FR-7**: 更新 docs/retrospective/README.md 中的目录树、统计数字和报告描述
- **FR-8**: 所有 Markdown 文档的 TOML frontmatter 保持完整有效

## Non-Functional Requirements

- **NFR-1**: 重组后所有本地 Markdown 链接 100% 有效（使用 check-links.py 验证 0 断链）
- **NFR-2**: 重组后的目录结构遵循 MECE 原则，主题边界清晰无重叠
- **NFR-3**: 索引文档遵循项目既有模板风格（参考 docs/retrospective/README.md 和其他主题 README）
- **NFR-4**: 迁移操作原子化，可通过 Git 追溯
- **NFR-5**: 所有文件名保持 kebab-case 规范

## Constraints

- **Technical**: 必须使用 PowerShell 5 兼容命令；Python 脚本仅使用标准库；遵循 Mermaid 安全编码五规则
- **Business**: 不得改变报告的原子化四件套结构；不得删除任何现有报告内容；路径引用必须使用相对路径，禁止 `file:///` 绝对路径
- **Dependencies**: `check-links.py` 链接验证脚本；`check-mermaid.py` Mermaid 语法检查；现有目录结构与命名规范

## Assumptions

- 所有现有报告已遵循原子化四件套结构（README.md + 三个子模块文件）
- 报告之间的交叉引用均使用相对路径
- docs/retrospective/README.md 中对 project-governance 的描述需要同步更新
- 主题分类体系一旦建立，后续新增报告可直接归入对应主题

## 主题分类体系定义

### Theme 1: comprehensive-reviews/（项目综合复盘）

**主题定义**：跨里程碑、全项目范围的系统性、综合性复盘报告，涵盖项目全周期执行数据、关键决策、整体成就与战略路线图。

**包含报告**：
1. retrospective-comprehensive-20260623/ - 2026-06-23 综合复盘（已原子化为6个子模块）
2. retrospective-project-comprehensive-20260625/ - 项目级全面复盘（3天节点）
3. retrospective-specweave-full-project-comprehensive-20260626/ - SpecWeave 项目全面复盘分析报告（4天结项版）

### Theme 2: documentation-governance/（文档体系治理）

**主题定义**：聚焦文档结构优化、内容重组、链接维护、可视化兼容性、入口文档一致性、知识组织等文档体系层面的治理任务复盘。

**包含报告**：
1. reports-duplication-optimization-report.md - 复盘报告体系重复内容优化（独立报告文件）
2. retrospective-report-system-planning/ - README 系统规划章节设计与入口架构
3. retrospective-readme-sync-and-brand-naming-20260624/ - README 同步与 SpecWeave 品牌命名一致性
4. retrospective-insights-reorg-20260626/ - 竹简悟道洞察库重组（四层结构均衡化）
5. retrospective-link-fix-depth-adjustment-20260626/ - 断链修复与链接自动校正工具增强
6. retrospective-mermaid-rendering-fix-20260626/ - Mermaid 渲染兼容性修复与安全编码规则

### Theme 3: tools-and-automation/（工具与自动化治理）

**主题定义**：自动化工具开发、工具熵优化、文档生成工具、工具链增强等工具层治理任务的复盘。

**包含报告**：
1. retrospective-report-tool-entropy-nonlinear-optimization/ - 工具熵非线性优化与自动化规模不经济规律
2. retrospective-report-code-wiki-generation/ - Code Wiki 自动化文档生成任务

### Theme 4: process-and-compliance/（流程与合规治理）

**主题定义**：工作流程建立、协议执行、规范遵守、合规性审查、改进建议落实等流程与合规层面的治理复盘。

**包含报告**：
1. retrospective-report-create-apps-directory/ - apps/ 应用开发工作空间创建与生命周期协议
2. retrospective-report-suggestion-execution-and-pattern-import/ - 改进建议执行与模式导入闭环
3. retrospective-session-agents-md-violation-20260624/ - AGENTS.md 启动协议违反复盘与合规性反思

### Theme 5: archiving-and-migration/（归档与内容迁移）

**主题定义**：应用归档、内容萃取与迁移、Demo 制作流程、报告导出等涉及资产移动、整理和归档的任务复盘。

**包含报告**：
1. retrospective-export-20260623/ - 复盘报告导出卡片
2. retrospective-zhujian-wudao-apps-archiving-20260625/ - 竹简悟道参赛作品归档至 apps/
3. retrospective-xinet-content-extraction-archiving-20260625/ - xinet 目录系统性内容萃取与归档方案
4. retrospective-specweave-demo-production-flow-20260625/ - SpecWeave Demo 制作流程探索与验证

## Acceptance Criteria

### AC-1: 主题目录创建与完整性

- **Given**: project-governance 目录下 19 份报告平铺存放
- **When**: 执行重组操作
- **Then**: 5 个主题子目录（comprehensive-reviews/, documentation-governance/, tools-and-automation/, process-and-compliance/, archiving-and-migration/）全部创建成功，19 份报告全部迁移至对应主题目录，project-governance 根目录下仅保留子目录和 README.md，无遗留平铺报告
- **Verification**: `programmatic`
- **Notes**: 通过目录列表和文件计数验证

### AC-2: 文件内容完整性

- **Given**: 所有报告已迁移至主题子目录
- **When**: 检查迁移后的文件
- **Then**: 所有文件的内部内容（Markdown 正文、TOML frontmatter、Mermaid 图表代码块）保持完整，未发生非预期修改
- **Verification**: `programmatic`
- **Notes**: 通过 Git diff 确认仅路径引用相关行被修改

### AC-3: 内部链接修复

- **Given**: 目录迁移增加了一层 `../` 路径深度
- **When**: 运行链接验证
- **Then**: 所有报告内部的相对路径引用（子模块间互链、关联报告链接、模式/概念引用）均已正确调整深度，0 个断链
- **Verification**: `programmatic`
- **Notes**: 使用 `python .agents/scripts/check-links.py --path docs/retrospective/reports/project-governance/` 验证

### AC-4: 分类索引 README.md 生成

- **Given**: 主题目录已创建并完成报告迁移
- **When**: 查看 project-governance/README.md
- **Then**: 索引文档包含：主题分类定义表、各主题报告清单与简要说明、Mermaid 主题关系图、目录结构树、快速导航指南；风格与 docs/retrospective/README.md 保持一致
- **Verification**: `human-judgment`
- **Notes**: 参考其他主题目录的 README 风格

### AC-5: 主题子目录 README.md 生成

- **Given**: 5 个主题子目录已创建
- **When**: 查看各主题子目录下的 README.md
- **Then**: 每个主题子目录包含 README.md，内含主题定义、该主题下的报告列表、每个报告的一句话简介、子模块导航链接
- **Verification**: `human-judgment`

### AC-6: 上层文档同步更新

- **Given**: 重组完成
- **When**: 查看 docs/retrospective/README.md
- **Then**: project-governance 部分的目录树、报告计数（从"12份+1独立报告"更新为"19份"）、各报告描述均已更新以反映新的二级分类结构
- **Verification**: `programmatic` + `human-judgment`
- **Notes**: 需同步更新目录树、统计数字、报告列表描述

### AC-7: Mermaid 图表语法正确

- **Given**: 所有索引文档已生成
- **When**: 运行 Mermaid 语法检查
- **Then**: 新增的 Mermaid 图表（主题关系图等）全部通过语法检查，遵循 Mermaid 安全编码五规则
- **Verification**: `programmatic`
- **Notes**: 使用 `python .agents/scripts/check-mermaid.py` 验证

### AC-8: 全项目链接验证

- **Given**: 所有路径引用已调整
- **When**: 在项目根目录运行全量链接检查
- **Then**: 全项目 0 个本地断链（与重组前一致，未引入新断链）
- **Verification**: `programmatic`
- **Notes**: 使用 `python .agents/scripts/check-links.py --path .` 验证

## Open Questions

- [ ] retrospective-report-four-topic-structure-optimization-20260624/ 在目录列表中存在但实际文件不存在（Glob 未找到），是否需要处理？—— 经检查，该目录在 LS 结果中列出但 Glob 搜索和 Read 均确认不存在，可能为历史残留记录，本次重组忽略该条目
