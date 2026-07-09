---
id: "readme-completion-plan"
title: "docs/目录README补全计划"
category: "spec"
date: "2026-07-09"
version: "1.0"
source: "retrospective-best-practices-readme-link-fix-20260709 P0行动项"
---

# docs/ 目录 README 补全计划

## 概述

基于 best-practices README 建设复盘洞察——**"内容完成≠可发现，内容-入口-索引三位一体才是完整知识库"**，对 docs/ 目录进行全面扫描，发现 **80个子目录** 缺少 README 入口文档。本计划按优先级分三阶段推进，结合自动化工具降低人工成本。

## 问题规模

| 层级深度 | 缺失数量 | 主要类型 | 推荐策略 |
|---------|---------|---------|---------|
| L1（根级） | 4 | 独立主题目录 | **人工编写** |
| L2（二级分类） | 9 | knowledge/retrospective/superpowers | **半自动化（模板+填充）** |
| L3（三级分类） | 16 | 学习主题+复盘报告分类 | **半自动/自动生成** |
| L4（Wiki/模式） | 36 | 主题Wiki+方法论模式库 | **自动生成索引** |
| L5（子Wiki/SDK） | 4 | SDK文档分组+产品子Wiki | **模板生成** |
| L6（章节级） | 11 | SDK具体章节 | **自动生成** |
| **合计** | **80** | | |

## 策略分层

### 策略A：人工编写（高价值入口点，约13个）
- 定位：知识导航枢纽，影响新成员上手效率
- 要求：结构化内容（概念概述+场景+快速上手+完整索引）
- 参考模板：best-practices/README.md 模式

### 策略B：模板生成（结构一致目录，约19个）
- 定位：内容聚合页，提供分类索引+主题概览
- 方式：使用标准模板，自动提取子目录/文件列表生成索引表
- 要求：包含目录定位说明+文件索引表+导航链接

### 策略C：自动生成（纯索引目录，约48个）
- 定位：机械性索引页，无需人工内容
- 方式：脚本自动扫描目录，基于frontmatter生成索引
- 要求：文件列表+按类别分组+父目录/兄弟目录导航

---

## 第一阶段（P0）：核心知识入口（人工编写，13个）

**目标**：解决最关键的导航断点，确保 docs/ 一级/二级入口可发现。

### 任务清单

| # | 目录 | 策略 | 内容要求 | 优先级 |
|---|------|------|---------|--------|
| 1 | `architecture/` | A | 多智能体协作流程架构概览 | P0 |
| 2 | `superpowers/` | A | 超能计划索引（plans/specs双目录导航） | P0 |
| 3 | `task-summaries/` | A | 任务总结报告索引 | P0 |
| 4 | `test-plans/` | A | 测试计划索引 | P0 |
| 5 | `knowledge/decisions/` | B | ADR决策记录索引 | P0 |
| 6 | `knowledge/mdi-research/` | B | MDI研究系列索引（8篇报告导航） | P0 |
| 7 | `knowledge/operations/` | B | 运维操作指南索引（11篇分类） | P0 |
| 8 | `knowledge/troubleshooting/` | B | 故障排查指南索引（按问题类型分类） | P0 |
| 9 | `retrospective/concepts/` | B | 复盘核心概念索引（10个概念） | P0 |
| 10 | `retrospective/frameworks/` | B | 决策框架索引（4个框架） | P0 |
| 11 | `knowledge/learning/01-agent-protocols-interfaces/` | A | Agent协议与接口学习主题入口 | P0 |
| 12 | `knowledge/learning/02-agent-engineering-methodology/` | A | Agent工程方法论学习主题入口 | P0 |
| 13 | `knowledge/learning/03-agent-platforms-tools/` | A | Agent平台工具学习主题入口 |

**验收标准**：
- 每个README包含TOML frontmatter
- 链接检查100%通过
- 从docs/README.md导航到各子目录入口可达
- 新成员能从入口理解目录定位和内容组织

---

## 第二阶段（P1）：内容聚合与主题Wiki（模板+自动，40个）

**目标**：补全所有知识聚合目录的入口，完善三级导航体系。

### 任务清单

#### B1：learning剩余主题（人工+模板，5个）

| # | 目录 | 策略 |
|---|------|------|
| 14 | `knowledge/learning/04-docs-markup-tooling/` | B |
| 15 | `knowledge/learning/05-ai-multimodal-content/` | B |
| 16 | `knowledge/learning/06-business-trends-analysis/` | B |
| 17 | `knowledge/learning/07-vendor-product-learning/` | A |
| 18 | `knowledge/learning/08-systems-infrastructure/` | B |

#### B2：retrospective报告分类目录（自动生成，8个）

| # | 目录 | 策略 |
|---|------|------|
| 19 | `retrospective/reports/atomization/` | C |
| 20 | `retrospective/reports/competitive-analysis/` | C |
| 21 | `retrospective/reports/insight-extraction/` | C |
| 22 | `retrospective/reports/roles-teams/` | C |
| 23 | `retrospective/reports/spec-system/` | C |
| 24 | `retrospective/reports/standards-tools/` | C |
| 25 | `retrospective/reports/task-reports/` | B |
| 26 | `retrospective/archives/` | C |

#### B3：retrospective模式库分类（自动生成，7个）

| # | 目录 | 文件数 | 策略 |
|---|------|--------|------|
| 27 | `retrospective/patterns/ai-collaboration/` | 46 | C |
| 28 | `retrospective/patterns/creative-design/` | 7 | C |
| 29 | `retrospective/patterns/document-architecture/` | 40 | C |
| 30 | `retrospective/patterns/governance-strategy/` | 61 | C |
| 31 | `retrospective/patterns/product-growth/` | 41 | C |
| 32 | `retrospective/patterns/retrospective-knowledge/` | 34 | C |
| 33 | `retrospective/patterns/tools-automation/` | 34 | C |

#### B4：各主题Wiki内容页（自动生成，20个）

| # | 目录 | 文件数 | 策略 |
|---|------|--------|------|
| 34 | `knowledge/learning/01-.../agent-communication-protocols/` | 12 | C |
| 35 | `knowledge/learning/01-.../agent-interface-deep-dive/` | 7 | C |
| 36 | `knowledge/learning/01-.../agent-skills-wiki/` | 15 | C |
| 37 | `knowledge/learning/01-.../ffi-wiki/` | 8 | C |
| 38 | `knowledge/learning/01-.../idl-wiki/` | 10 | C |
| 39 | `knowledge/learning/01-.../interface-api-abi-protocol-wiki/` | 7 | C |
| 40 | `knowledge/learning/02-.../agent-skills-wiki/` | 8 | C |
| 41 | `knowledge/learning/02-.../harness-engineering-wiki/` | 10 | C |
| 42 | `knowledge/learning/02-.../headroom-context-compression-wiki/` | 11 | C |
| 43 | `knowledge/learning/02-.../karpathy-llm-coding-guidelines/` | 8 | C |
| 44 | `knowledge/learning/02-.../longcat-agent-learning-wiki/` | 9 | C |
| 45 | `knowledge/learning/03-.../claude-tag-article/` | 8 | C |
| 46 | `knowledge/learning/03-.../minitest-mobile-use-wiki/` | B |
| 47 | `knowledge/learning/03-.../mopmonk-security-agent-wiki/` | 7 | C |
| 48 | `knowledge/learning/03-.../open-code-review-wiki/` | 11 | C |
| 49 | `knowledge/learning/03-.../rainman-translate-book-wiki/` | 8 | C |
| 50 | `knowledge/learning/04-.../scikit-build-core-wiki/` | 7 | C |
| 51 | `knowledge/learning/06-.../ai-monetization-wiki/` | 13 | C |
| 52 | `knowledge/learning/06-.../papi-jiang-solo-ip-trend-wiki/` | 9 | C |
| 53 | `knowledge/learning/okr-wiki/` | B |

**验收标准**：
- 所有P1目录有README.md
- 自动生成的README格式统一，索引准确
- 链接检查100%通过

---

## 第三阶段（P2）：产品Wiki与SDK章节（自动生成，27个）

**目标**：补全最深层级的导航断点，实现全目录README覆盖。

### 任务清单

| # | 目录 | 文件数 | 策略 |
|---|------|--------|------|
| 54-58 | `knowledge/learning/okr-wiki/{concepts,implementation,methods,scoring,tools}/` | 2-6 | C |
| 59 | `knowledge/learning/07-.../openai/` | 0+1 | B |
| 60 | `knowledge/learning/07-.../sunlogin/` | 14+3 | B |
| 61 | `knowledge/learning/07-.../tuya/` | 3 | C |
| 62 | `knowledge/learning/07-.../volcengine/` | 11 | C |
| 63 | `retrospective/.../myst-to-agentspec-migration-analysis/` | 13 | C |
| 64 | `.../minitest-mobile-use-wiki/minitest-docs/` | 0+5 | B |
| 65 | `.../minitest-mobile-use-wiki/mobile-use-sdk-docs/` | 0+6 | B |
| 66 | `.../sunlogin/sunlogin-bootbox-analysis/` | 10 | C |
| 67 | `.../sunlogin/sunlogin-offline-hardware-wiki/` | 11 | C |
| 68-72 | `.../minitest-docs/{01..05}-*/` (5个) | 4-7 | C |
| 73-78 | `.../mobile-use-sdk-docs/{01..06}-*/` (6个) | 3-7 | C |
| 79 | `superpowers/plans/` | 6 | B |
| 80 | `superpowers/specs/` | 5 | B |

**验收标准**：
- docs/下所有含内容的子目录均有README
- 全目录链接检查100%通过
- 生成README门禁检查（新子目录必须含README）

---

## 工具建设需求

为支持策略B和C的自动化，需建设以下工具：

### 工具1：README自动生成脚本
- **路径**：`.agents/scripts/generate-readme.py`
- **功能**：扫描指定目录，基于frontmatter元数据自动生成索引型README
- **参数**：`--path <dir>` `--template <index|category|wiki>` `--title <title>`
- **产出**：包含目录标题、描述（从父目录README或默认模板）、子目录/文件索引表、导航链接

### 工具2：README门禁检查
- **路径**：扩展 `.agents/scripts/check-links.py` 或新建 `check-readme.py`
- **功能**：检查所有含.md文件的目录是否有README.md
- **集成**：加入CI检查链（ci-check.ps1）

---

## 前置依赖

| 依赖项 | 说明 | 阶段 |
|--------|------|------|
| README模板标准化 | 定义A/B/C三种策略的标准模板 | 第一阶段前 |
| generate-readme.py脚本 | 支持策略B/C的自动生成 | 第二阶段前 |
| frontmatter规范检查 | 确保所有.md文件frontmatter完整（title/summary/tags） | 第一阶段同步 |

## 风险与注意事项

1. **自动生成质量**：策略C的自动生成README不包含人工撰写的概述，但能保证导航完整性——后续可逐步升级为B/A策略
2. **frontmatter缺失**：扫描中发现部分文件缺少frontmatter字段（status/author/summary），需在补全README的同时修复
3. **索引维护**：新增文件/目录时需要更新README，通过门禁检查强制保障
4. **避免冗余**：自动生成的README应包含"此文件由脚本自动生成"标记，避免人工编辑被覆盖

## 预期效果

完成三阶段补全后：
- docs/ 下**80个缺失入口**全部补齐（覆盖率从~30%提升到100%）
- 新团队成员可从任何目录入口理解"我在哪、这里有什么、怎么导航"
- 链接检查从85个→预计覆盖500+本地引用
- 形成"目录必有入口"的文档基础设施规范
