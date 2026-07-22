---
title: SpecWeave复赛作品技术支持资源指南 - PRD
date: 2026-07-22
content_sensitivity: private
---

# SpecWeave复赛作品技术支持资源指南 - Product Requirement Document

## Overview

- **Summary**: 系统梳理SpecWeave项目在技术实现、功能开发、资源支持、性能优化等方面能够为TRAE大赛复赛作品提供的全部可复用资源。以结构化文档形式，清晰呈现可复用代码模块、API接口、开发工具、技术文档、性能测试支持、兼容性解决方案、容器化模板、优秀作品参考案例等具体内容及应用方式，帮助复赛选手快速理解和复用项目沉淀的工程能力。
- **Purpose**: 解决复赛选手"不了解SpecWeave能提供什么支持、不知道有哪些现成资源可用、不清楚如何集成项目能力"的问题。当前项目已沉淀563件优秀作品、20+质量检查脚本、18个Skill门面、6类可复用代码模块、3套容器化模板、Mermaid MCP服务器、提示词萃取系统等丰富资源，但缺乏一份面向复赛选手的、清晰的支持资源说明文档，导致选手难以有效利用项目能力加速开发。
- **Target Users**: TRAE大赛复赛选手、SpecWeave内部技术支持团队、评审专家、后续参赛开发者。

## Goals

1. **全面盘点支持资源**：系统梳理代码模块、API接口、工具脚本、模板、文档、测试、容器化、案例参考8大类支持资源
2. **明确应用方式**：为每项资源提供具体的接入步骤、代码示例、使用场景说明，而非仅罗列文件路径
3. **按开发阶段组织**：按"项目初始化→核心开发→质量保障→性能优化→部署交付→文档撰写"6个开发阶段组织资源，匹配选手实际工作流
4. **提供快速上手路径**：为不同类型作品（AI Agent类、工具类、Web应用类、文档/知识库类）提供定制化资源包推荐
5. **建立更新机制**：文档结构支持后续新增资源时快速补充

## Non-Goals (Out of Scope)

- 不开发新的功能模块或API（仅整理现有资源）
- 不为特定参赛作品做定制化开发指导（提供通用资源指南）
- 不包含外部第三方服务的接入教程（仅SpecWeave自有资源）
- 不做商业承诺或SLA保证（资源按现状提供）
- 不创建新的代码仓库或发布包
- 不翻译为英文（中文输出为主）

## Background & Context

SpecWeave 经过1538+次提交迭代，已构建完整的AI协作工程体系，核心资源储备如下：

| 资源类别 | 数量/规模 | 位置 | 成熟度 |
|---------|----------|------|--------|
| 可复用Python代码模块 | 9个核心库 | `.agents/scripts/lib/` | L3-L4（有测试覆盖） |
| 质量检查/自动化脚本 | 35+ | `.agents/scripts/` | L3-L4（CI集成） |
| Skill技能门面 | 18个 | `.agents/skills/`、内置Skill | L3（封装完善） |
| 可复用模式(patterns) | 488个 | `.agents/docs/retrospective/patterns/` | L1-L4 |
| 最佳实践(best-practices) | 21个 | `.agents/docs/knowledge/best-practices/` | L3-L4 |
| 容器化模板 | 3套 | `apps/`（PyTorch/Docker-DIND/XMNN） | L2-L3 |
| MCP服务器实现 | 1个 | `.agents/scripts/mdi/` | L3 |
| 提示词萃取系统 | 1套完整Pipeline | `apps/prompt_extraction/` | L3 |
| 多智能体冲突解决库 | 1套 | `.agents/scripts/lib/collaboration/` | L4（测试覆盖90%+） |
| 测试场景生成器 | 1套 | `.agents/scripts/lib/testing/` | L4 |
| 论坛自动化Bot | 1套 | `.agents/scripts/forum_bot/` | L3 |
| Home Assistant API封装 | 1套 | `.agents/scripts/ha_api.py` | L3 |
| 技术文档/Wiki | 100+ | `.agents/docs/` | L2-L4 |
| 优秀作品参考案例 | 563件 | `playground/excellent-works-catalog/` | 已分类归档 |
| AI代码助手Demo | 1个Flask应用 | `apps/ai-code-assistant/` | L2 |
| Chaos混沌工程 | 1套 | `vendor/flexloop/apps/chaos/` | L2 |

复赛选手的核心痛点：
1. **信息过载**：项目结构复杂（.agents/scripts/lib/skills/commands等多层目录），难以快速定位可用资源
2. **缺乏使用指南**：知道文件存在但不知道如何调用、参数是什么、适用什么场景
3. **集成成本高**：不清楚哪些模块可以直接import、哪些是独立脚本、哪些需要配置
4. **案例参考缺失**：不知道类似作品如何实现，缺乏可参考的完整项目结构
5. **质量标准不明确**：不清楚项目的编码规范、提交规范、测试要求

## Functional Requirements

- **FR-1 资源分类体系**：将支持资源分为8大类——可复用代码模块、API接口与服务、开发工具链、模板与脚手架、技术文档与知识库、测试与质量保障、容器化与部署、优秀作品参考案例
- **FR-2 开发阶段映射**：按6个开发阶段（初始化/核心开发/质量保障/性能优化/部署交付/文档撰写）组织资源，每个阶段列出相关资源及快速使用方式
- **FR-3 代码模块详细说明**：对9个核心Python库模块（frontmatter, markdown, cli, patterns, atomic_write, io_safety, rules, spec_loader, process, collaboration/conflict_resolution, testing）提供：功能说明、核心API列表、导入方式、代码示例、适用场景
- **FR-4 API接口文档**：对Flask API（/api/explain, /api/ask, /api/learning-path）、MCP服务器端点、Home Assistant API封装、论坛Bot API提供：接口地址、请求/响应格式、调用示例
- **FR-5 开发工具使用指南**：对18个Skill和35+脚本提供：命令格式、参数说明、典型使用场景、输出示例
- **FR-6 模板资源索引**：对容器化模板（PyTorch/Docker-DIND/XMNN）、文档模板（handoff/task/pattern）、项目模板提供：文件位置、定制方法、使用步骤
- **FR-7 质量保障方案**：整合CI检查流程（10项检查）、测试框架（pytest+场景生成器）、兼容性方案（跨平台Python脚本、Mermaid跨环境渲染）
- **FR-8 性能优化支持**：列出可用的性能分析工具、并发处理方案（原子写入/IO安全）、缓存机制、资源限制方法
- **FR-9 作品类型资源包**：为4类作品（AI Agent类/工具CLI类/Web应用类/文档知识库类）分别推荐资源组合和快速启动路径
- **FR-10 快速参考卡片**：生成一页式快速参考表（常用命令+关键路径+常见问题）

## Non-Functional Requirements

- **NFR-1 实用性**：每项资源必须附带具体的使用方式或代码示例，禁止仅列文件路径无说明
- **NFR-2 准确性**：所有API、命令、路径必须经过验证，确保与代码实际实现一致
- **NFR-3 可导航性**：文档中所有代码引用使用可点击的相对路径链接，支持快速跳转到源文件
- **NFR-4 结构清晰**：使用目录/表格/代码块/折叠块等Markdown元素组织信息，层次分明
- **NFR-5 可扩展性**：文档按模块化结构组织，新增资源时只需在对应章节追加条目
- **NFR-6 产出位置**：文档放在 `playground/semi-final-support/` 目录下（私域工作流）
- **NFR-7 格式规范**：Mermaid图表通过check-mermaid.py检查，链接通过link-check验证

## Constraints

- **Technical**: 输出格式为Markdown，可内嵌Mermaid图表；代码示例使用Python/Shell/Markdown，与项目技术栈一致；仅使用Python标准库的模块可直接import，有第三方依赖的需标注
- **Business**: 文档面向复赛选手，语言通俗易懂，避免过度内部术语；资源说明必须客观，不夸大能力
- **Dependencies**: 依赖现有代码文件的实际实现（不能虚构API）；依赖已整理的优秀作品库作为案例参考来源；依赖check-mermaid.py验证图表

## Assumptions

1. 复赛选手有基本的Python开发能力和Git使用经验
2. 选手使用Trae IDE作为开发环境（项目Skill体系基于Trae）
3. 选手作品可能涉及AI Agent、工具开发、Web应用、文档系统等方向
4. 项目中的vendor子模块（flexloop/ark-cli）可作为参考但核心支持来自.agents/和apps/
5. Python 3.13+是推荐版本，但代码示例应兼容Python 3.10+
6. 部分资源（如Home Assistant API、论坛Bot）是特定场景专用，不作为通用推荐
7. 提示词萃取系统(prompt_extraction)使用pandas等第三方依赖，需标注安装要求

## Acceptance Criteria

### AC-1: 8大资源类别全覆盖
- **Given**: SpecWeave项目现有资源
- **When**: 完成资源盘点
- **Then**: 文档包含可复用代码模块、API接口、开发工具、模板、技术文档、测试质量、容器部署、案例参考8个类别，每个类别至少有3项具体资源
- **Verification**: `human-judgment`

### AC-2: 开发阶段组织清晰
- **Given**: 完成的支持指南文档
- **When**: 按开发阶段浏览
- **Then**: 6个阶段（初始化/核心开发/质量保障/性能优化/部署交付/文档撰写）每个阶段都有对应的资源推荐和使用步骤
- **Verification**: `human-judgment`

### AC-3: 代码模块有可执行示例
- **Given**: 文档中的代码模块章节
- **When**: 选手按照示例操作
- **Then**: 每个核心库模块至少有一个可运行的Python代码片段（import+核心调用），示例代码语法正确
- **Verification**: `programmatic`（Python语法检查）+ `human-judgment`

### AC-4: API接口文档完整
- **Given**: 文档中的API章节
- **When**: 开发者查阅API文档
- **Then**: 每个列出的API包含端点/方法、请求参数、响应格式、curl或Python调用示例
- **Verification**: `human-judgment`

### AC-5: 工具命令可直接执行
- **Given**: 文档中的工具章节
- **When**: 选手复制文档中的命令
- **Then**: 命令格式正确，参数与实际脚本一致（通过--help验证）
- **Verification**: `programmatic`（抽样执行--help验证）

### AC-6: 链接有效无死链
- **Given**: 生成的Markdown文档
- **When**: 运行链接检查
- **Then**: 所有相对路径链接可正确跳转，无404
- **Verification**: `programmatic`（通过check-links.py）

### AC-7: Mermaid图表正确渲染
- **Given**: 文档中的Mermaid图表（如资源全景图、开发阶段流程图）
- **When**: 通过check-mermaid.py检查
- **Then**: 0错误0警告
- **Verification**: `programmatic`

### AC-8: 4类作品资源包完整
- **Given**: 作品类型推荐章节
- **When**: 不同类型作品开发者查阅
- **Then**: AI Agent类/工具CLI类/Web应用类/文档知识库类各有明确的推荐资源清单和快速启动步骤
- **Verification**: `human-judgment`

### AC-9: 产出位置符合私域规范
- **Given**: 生成的所有文件
- **When**: 检查文件位置和frontmatter
- **Then**: 所有文件位于 `playground/semi-final-support/`，包含content_sensitivity: private标记
- **Verification**: `programmatic`

### AC-10: 快速参考卡片实用
- **Given**: 快速参考卡片
- **When**: 选手需要快速查找命令或路径
- **Then**: 一页内包含最常用的10+命令、5+关键路径、3+常见问题解答
- **Verification**: `human-judgment`

## Open Questions

- [ ] 是否需要为复赛选手提供一个"一键初始化"脚本，自动配置推荐的开发环境和pre-commit hooks？
- [ ] 文档是否需要包含FAQ章节，收集选手可能遇到的常见问题？
- [ ] 容器化模板是否需要提供docker-compose.yml以便选手一键启动？
- [ ] 是否需要为每个代码模块提供更完整的Jupyter Notebook教程？
- [ ] 优秀作品案例部分，是链接到已有的catalog索引，还是需要精选10-20个最相关案例做深度说明？
