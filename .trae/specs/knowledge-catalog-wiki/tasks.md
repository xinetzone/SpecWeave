# Knowledge Catalog Wiki 教程 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 创建 knowledge-catalog-wiki 目录和 README.md 入口文件
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 在 `d:\AI\.agents\docs\knowledge\learning\01-agent-protocols-interfaces\` 下创建 `knowledge-catalog-wiki` 目录
  - 创建 README.md 文件，遵循现有wiki入口格式：包含frontmatter、概述、文档索引表、阅读路径建议、相关资源链接
  - 参考 okf-wiki/README.md 和 agent-skills-wiki/README.md 的格式
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录和README.md文件存在
  - `human-judgement` TR-1.2: README.md包含完整frontmatter、索引表、阅读路径，格式与现有wiki一致
- **Notes**: 先确定frontmatter字段（id、title、category、date、tags等），确保与同目录其他wiki一致

## [x] Task 2: 创建 00-overview.md 概述章节
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 编写Knowledge Catalog概述：项目定位（原Dataplex，AI驱动的数据目录与知识管理平台）、核心价值、与OKF的关系
  - 包含核心组件全景图（Mermaid流程图）、学习目标、前置知识、章节导航表、阅读路径
  - 添加指向okf-wiki的交叉链接（在OKF相关部分）
  - 底部添加上一章/目录/下一章导航
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-5
- **Test Requirements**:
  - `programmatic` TR-2.1: 文件存在，包含指向okf-wiki的链接
  - `human-judgement` TR-2.2: 内容准确，结构清晰，导航完整，符合格式规范
- **Notes**: 基于knowledge-catalog/README.md和okf/SPEC.md、okf/README.md内容编写

## [x] Task 3: 创建 01-core-concepts.md 核心概念章节
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 详解Knowledge Catalog核心设计理念与核心概念：Bundle、Concept、Frontmatter、Source、Trust Tier、Attested Computation、Index/Log文件
  - 每个概念的职责、定义、核心功能
  - 平台架构分层与组件关系图（Mermaid）
  - 底部导航
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-5
- **Test Requirements**:
  - `programmatic` TR-3.1: 文件存在，链接到okf-wiki
  - `human-judgement` TR-3.2: 组件覆盖完整，描述准确，关系图清晰

## [x] Task 4: 创建 02-okf-specification.md OKF规范章节
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 从实现视角深度解析OKF v0.2规范
  - Bundle结构、Concept文件结构、frontmatter字段详解、信任与来源字段、交叉链接规则、Index/Log文件格式、Attested Computation规范、v0.1到v0.2变更
  - 与okf-wiki/02规范章节交叉引用
  - 底部导航
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-5
- **Test Requirements**:
  - `programmatic` TR-4.1: 文件存在
  - `human-judgement` TR-4.2: 规范描述与okf/SPEC.md一致

## [x] Task 5: 创建 03-reference-agent.md 参考Agent章节
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 
  - 参考Agent架构：两阶段流程（BQ pass → Web pass）
  - enrich命令详解：参数说明、使用方法、运行示例
  - 核心模块解析：bundle工具、source工具、web工具、context管理
  - CLI使用方式、单Concept迭代方法、凭证配置
  - 底部导航
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-5
- **Test Requirements**:
  - `programmatic` TR-5.1: 文件存在
  - `human-judgement` TR-5.2: 架构描述准确，命令参数与okf/cli.py和okf/README.md一致

## [x] Task 6: 创建 04-toolchain-and-visualization.md 工具链与可视化章节
- **Priority**: high
- **Depends On**: Task 5
- **Description**: 
  - 可视化系统功能：力导向图、详情面板、反向链接、搜索/筛选/多种布局
  - visualize命令使用方法、参数说明、技术架构（Cytoscape.js + marked.js，自包含HTML）
  - enrichment工具（TypeScript实现的Agent enrich命令）
  - mdcode工具：语义层、BigQuery集成、MCP服务能力、pull/push命令
  - 底部导航
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-5
- **Test Requirements**:
  - `programmatic` TR-6.1: 文件存在
  - `human-judgement` TR-6.2: 覆盖可视化、enrichment、mdcode，描述与toolbox目录下的README一致

## [x] Task 7: 创建 05-samples-and-bundles.md 示例Bundle章节
- **Priority**: medium
- **Depends On**: Task 4
- **Description**: 
  - 解析okf/bundles/下的四个示例Bundle：GA4、Stack Overflow、crypto_bitcoin、acme_retail
  - samples/目录与bundles/目录的关系（recipes vs products）
  - 每个Bundle的结构、特点、覆盖的OKF特性、学习价值
  - 底部导航
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-5
- **Test Requirements**:
  - `programmatic` TR-7.1: 文件存在
  - `human-judgement` TR-7.2: 四个Bundle都覆盖到，特点描述准确

## [x] Task 8: 创建 06-integration-patterns.md 集成模式章节
- **Priority**: medium
- **Depends On**: Task 6, Task 7
- **Description**: 
  - 企业落地四阶段路径
  - 三种典型集成场景（数据目录同步、Agent知识库构建、企业Runbook/Playbook管理）
  - 与现有数据目录集成模式、Git工作流集成
  - 扩展字段设计最佳实践、核心最佳实践清单
  - 底部导航
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-5
- **Test Requirements**:
  - `programmatic` TR-8.1: 文件存在
  - `human-judgement` TR-8.2: 集成场景覆盖完整，最佳实践可操作

## [x] Task 9: 创建 07-architecture-decisions.md 架构决策章节
- **Priority**: medium
- **Depends On**: Task 8
- **Description**: 
  - OKF/Knowledge Catalog v0.2已知局限性与风险
  - 不适用场景
  - 与8种主流方案客观对比（RAG向量库、Notion/Obsidian、Unity Catalog、Collibra、Confluence、MkDocs、dbt docs、其他Agent知识方案）
  - 选型决策树（Mermaid）、风险评估与缓解建议
  - 交叉链接到okf-wiki/04-limitations-and-comparison.md
  - 底部导航
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-5
- **Test Requirements**:
  - `programmatic` TR-9.1: 文件存在，包含指向okf-wiki的链接
  - `human-judgement` TR-9.2: 对比客观中立，决策树清晰

## [x] Task 10: 创建 08-resources-and-glossary.md 资源与术语表章节
- **Priority**: medium
- **Depends On**: Task 9
- **Description**: 
  - 核心术语表（≥30个术语，按主题分类，每个一句话通俗解释）
  - 官方资源链接（GitHub仓库、Google Cloud产品页、OKF SPEC文档、示例Bundle）
  - 项目内wiki交叉引用（okf-wiki全部章节、knowledge-catalog-wiki内部章节、相关wiki）
  - 分角色学习建议
  - 底部导航
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-5
- **Test Requirements**:
  - `programmatic` TR-10.1: 文件存在，包含指向okf-wiki的链接
  - `human-judgement` TR-10.2: 术语数量≥30，资源链接准确，交叉引用完整

## [x] Task 11: 在 okf-wiki 中添加反向链接
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 10
- **Description**: 
  - 更新 okf-wiki/README.md：在相关资源部分添加knowledge-catalog-wiki链接
  - 更新 okf-wiki/00-overview.md：在背景/相关实现部分添加链接（新增0.10节）
  - 更新 okf-wiki/05-architecture-and-integration.md：在参考实现/工具部分添加链接（新增5.7节）
  - 更新 okf-wiki/07-resources-and-glossary.md：在资源部分添加链接
  - 确保所有链接使用正确的相对路径
- **Acceptance Criteria Addressed**: AC-3, AC-6
- **Test Requirements**:
  - `programmatic` TR-11.1: 四个okf-wiki文件都包含指向knowledge-catalog-wiki的链接
  - `human-judgement` TR-11.2: 链接位置合理，上下文自然，路径正确
- **Notes**: 仅添加链接，不修改okf-wiki的其他内容

## [x] Task 12: 更新父目录 README.md 索引
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 更新 `d:\AI\.agents\docs\knowledge\learning\01-agent-protocols-interfaces\README.md`
  - 在子Wiki索引表中添加knowledge-catalog-wiki条目（专题数从10更新为11）
  - 条目描述准确："Knowledge Catalog工具链完整指南：Google Cloud官方OKF参考实现、参考Agent、可视化工具、enrichment/mdcode工具箱、4个示例Bundle深度解析、快速入门、架构选型决策"
  - 在快速导航部分添加"知识管理"场景学习路径
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `human-judgement` TR-12.1: 父目录README的子Wiki索引表中包含新wiki条目，格式与现有条目一致，描述准确

## [x] Task 13: 验证所有链接无断链，整体检查
- **Priority**: high
- **Depends On**: Task 11, Task 12
- **Description**: 
  - 检查所有新创建文件中的相对路径链接，确保都指向存在的文件
  - 检查okf-wiki中新增链接的正确性
  - 检查父目录README中链接的正确性
  - 统一检查所有文件的frontmatter完整性、导航链接完整性
  - 确保文件命名符合kebab-case规范，无中文文件名
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-6
- **Test Requirements**:
  - `programmatic` TR-13.1: 所有相对路径链接可访问，无404
  - `human-judgement` TR-13.2: 整体格式统一，frontmatter完整，导航正确
