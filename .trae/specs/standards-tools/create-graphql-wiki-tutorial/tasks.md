# GraphQL 完整 Wiki 教程 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 创建 graphql-wiki 目录结构与入口 README
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 在 `.agents/docs/knowledge/learning/01-agent-protocols-interfaces/` 下创建 `graphql-wiki/` 目录
  - 创建 README.md 作为导航入口，包含文档索引表
  - README.md 遵循现有 wiki 格式（YAML frontmatter、README_INDEX_START/END 标记、相关资源链接）
  - 规划章节编号：00-overview 到 12-resources
- **Acceptance Criteria Addressed**: [AC-1, AC-5]
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录存在且包含 README.md
  - `programmatic` TR-1.2: README.md 包含有效的 YAML frontmatter，source 字段为 `spec:create-graphql-wiki-tutorial`
  - `human-judgement` TR-1.3: 导航索引表结构清晰，与 ffi-wiki 等现有 wiki 格式一致
- **Notes**: 参考 ffi-wiki/README.md 的格式

## [x] Task 2: 编写 00-overview.md - 教程总览
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 编写 GraphQL 教程总览章节
  - 内容包括：什么是 GraphQL、为什么使用 GraphQL、与 REST 的对比、本教程结构说明、前置知识要求
  - 包含一个简单的 GraphQL 查询示例和返回结果
- **Acceptance Criteria Addressed**: [AC-2, AC-3]
- **Test Requirements**:
  - `programmatic` TR-2.1: 文件存在，包含 YAML frontmatter
  - `human-judgement` TR-2.2: 内容清晰，能帮助读者快速了解 GraphQL 定位和教程结构
  - `human-judgement` TR-2.3: 包含代码示例
- **Notes**: 基于 source-introduction.md 和 source-home.md 内容编写

## [x] Task 3: 编写 01-core-concepts.md - GraphQL 核心概念
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 讲解 GraphQL 五大支柱（Five Pillars）：产品中心、层级化、强类型、客户端指定响应、自文档化
  - 核心概念：Schema、Type、Field、Resolver、Query、Mutation、Subscription
  - GraphQL 的优势：精确获取、单请求多资源、强类型、无版本化、与现有代码集成
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `programmatic` TR-3.1: 文件存在，包含 YAML frontmatter
  - `human-judgement` TR-3.2: 核心概念讲解清晰，首次出现的专业术语有 plain language 解释
- **Notes**: 专业术语首次出现必须给出一句话通俗解释

## [x] Task 4: 编写 02-queries.md - GraphQL 查询语言
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 查询（Queries）基础：字段、参数、别名、片段（Fragments）、操作名
  - 变量（Variables）：使用变量传递动态值
  - 指令（Directives）：@include、@skip
  - 变更（Mutations）：修改数据的操作
  - 内联片段、元字段
- **Acceptance Criteria Addressed**: [AC-2, AC-3]
- **Test Requirements**:
  - `programmatic` TR-4.1: 文件存在，包含 YAML frontmatter
  - `human-judgement` TR-4.2: 每个知识点包含对应的 GraphQL 查询示例
  - `human-judgement` TR-4.3: 示例代码格式正确，有对应的 JSON 返回示例
- **Notes**: 使用 Star Wars API 示例（参考官方文档）

## [x] Task 5: 编写 03-schema-types.md - Schema 与类型系统
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 类型系统（Type System）概述
  - 标量类型（Scalar Types）：Int、Float、String、Boolean、ID
  - 对象类型（Object Types）与字段
  - 枚举类型（Enum Types）
  - 接口（Interfaces）与联合类型（Union Types）
  - 输入类型（Input Types）
  - 非空修饰符（!）与列表（[]）
  - @deprecated 指令
- **Acceptance Criteria Addressed**: [AC-2, AC-3]
- **Test Requirements**:
  - `programmatic` TR-5.1: 文件存在，包含 YAML frontmatter
  - `human-judgement` TR-5.2: Schema 定义示例完整，覆盖主要类型
  - `human-judgement` TR-5.3: 类型讲解清晰，有示例 Schema 代码
- **Notes**: 这是 GraphQL 核心章节，需要确保内容准确完整

## [x] Task 6: 编写 04-validation-execution.md - 验证与执行
- **Priority**: medium
- **Depends On**: Task 5
- **Description**: 
  - 查询验证流程：语法检查、类型检查、字段存在性验证
  - 执行机制：Resolver 函数、解析链、上下文（Context）、信息（Info）参数
  - Resolver 工作原理示例
  - 错误处理：错误格式、部分错误与数据共存
- **Acceptance Criteria Addressed**: [AC-2, AC-3]
- **Test Requirements**:
  - `programmatic` TR-6.1: 文件存在，包含 YAML frontmatter
  - `human-judgement` TR-6.2: 执行流程讲解清晰，包含 Resolver 代码示例
- **Notes**: 可使用 JavaScript/Python 伪代码展示 Resolver

## [x] Task 7: 编写 05-client-basics.md - 客户端基础GraphQL 客户端基础
- **Priority**: medium
- **Depends On**: Task 4
- **Description**: 
  - GraphQL 客户端概述：为什么使用专用客户端
  - HTTP 请求格式：POST/GET、Content-Type
  - GraphiQL/GraphQL Playground 工具介绍
  - 常用客户端库简介（不绑定特定语言）
  - 查询缓存基础概念
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `programmatic` TR-7.1: 文件存在，包含 YAML frontmatter
  - `human-judgement` TR-7.2: 内容涵盖客户端核心概念和工具
- **Notes**: 本章节不深入特定语言客户端，留待后续章节/文档

## [x] Task 8: 编写 06-server-concepts.md - 服务端开发基础
- **Priority**: medium
- **Depends On**: Task 6
- **Description**: 
  - GraphQL 服务端工作流程概述
  - Schema-first vs Code-first 开发模式
  - Resolver 最佳实践基础：N+1 问题与 DataLoader 概念
  - 上下文传递、认证授权基础
  - 分页：Offset-based vs Cursor-based Connections 概念
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `programmatic` TR-8.1: 文件存在，包含 YAML frontmatter
  - `human-judgement` TR-8.2: 服务端核心概念讲解清晰
- **Notes**: 本章节为概念性介绍，不做特定语言实现

## [x] Task 9: 编写 07-python-ecosystem.md - Python GraphQL 生态
- **Priority**: high
- **Depends On**: Task 8
- **Description**: 
  - Python GraphQL 生态概述
  - 主流服务端库：Graphene、Strawberry、Ariadne、tartiflette 特点对比
  - 客户端库：gql、python-graphql-client、Apollo Client Python
  - 集成框架：Graphene-Django、Strawberry-FastAPI、Flask-GraphQL
  - 简单示例：使用 Strawberry/FastAPI 创建一个最小 GraphQL 服务
  - 简单示例：使用 gql 客户端查询 GraphQL API
- **Acceptance Criteria Addressed**: [AC-2, AC-3, AC-6]
- **Test Requirements**:
  - `programmatic` TR-9.1: 文件存在，包含 YAML frontmatter
  - `human-judgement` TR-9.2: 覆盖至少 3 个主流 Python 库（Graphene、Strawberry、gql）
  - `human-judgement` TR-9.3: 包含可运行的 Python 代码示例
- **Notes**: 基于 source-python-tools.md 筛选 Python 相关内容

## [x] Task 10: 编写 08-best-practices.md - 最佳实践GraphQL 最佳实践
- **Priority**: medium
- **Depends On**: Task 8
- **Description**: 
  - Schema 设计最佳实践：命名规范、字段设计、类型组织
  - 查询性能：避免过度获取、批量解析、DataLoader 使用
  - 错误处理最佳实践
  - 版本化与演进：使用 @deprecated、渐进式变更
  - 安全考虑：查询深度限制、查询复杂度分析、认证授权
  - 测试 GraphQL API
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `programmatic` TR-10.1: 文件存在，包含 YAML frontmatter
  - `human-judgement` TR-10.2: 最佳实践条目清晰，有实际指导意义
- **Notes**: 结合官方文档最佳实践章节

## [x] Task 11: 编写 11-glossary.md - 术语表与参考资料
- **Priority**: high
- **Depends On**: All previous chapters
- **Description**: 
  - 核心术语表（≥15 条）：Query、Mutation、Subscription、Schema、Type、Field、Resolver、Scalar、Enum、Interface、Union、Input Type、Fragment、Directive、Introspection、DataLoader 等
  - 每个术语包含：中文名称、英文原文、一句话通俗解释、相关章节交叉引用
  - 参考资料列表：官方文档链接、规范链接、推荐学习资源
  - 项目内相关 Wiki 交叉引用：IDL Wiki、API/ABI Wiki 等
- **Acceptance Criteria Addressed**: [AC-4, AC-6]
- **Test Requirements**:
  - `programmatic` TR-11.1: 文件存在，包含 YAML frontmatter
  - `programmatic` TR-11.2: 术语数量 ≥ 15 条
  - `human-judgement` TR-11.3: 每条术语有 plain language 解释，有交叉引用
  - `human-judgement` TR-11.4: 包含项目内相关 Wiki 的链接
- **Notes**: 术语表是强制要求项，必须满足 ≥15 条要求

## [x] Task 12: 更新 README.md 导航索引与父目录引用
- **Priority**: high
- **Depends On**: Task 11
- **Description**: 
  - 更新 graphql-wiki/README.md，在 <!-- README_INDEX_START --> 和 <!-- README_INDEX_END --> 之间填充完整的文档索引表
  - 确保每个章节都有正确的链接和说明
  - 更新父目录 `.agents/docs/knowledge/learning/01-agent-protocols-interfaces/README.md`，添加 graphql-wiki 入口
  - 检查所有交叉引用链接正确性
- **Acceptance Criteria Addressed**: [AC-1, AC-5, AC-6]
- **Test Requirements**:
  - `programmatic` TR-12.1: README.md 索引表包含所有章节
  - `programmatic` TR-12.2: 父目录 README 已添加 graphql-wiki 链接
  - `human-judgement` TR-12.3: 双向导航正确，可通过目录树找到教程
- **Notes**: 确保所有相对路径正确，无断链

## [x] Task 13: 格式验证与收尾检查
- **Priority**: high
- **Depends On**: Task 12
- **Description**: 
  - 运行文件名规范检查（python .agents/scripts/check-filename-convention.py）
  - 检查所有文档的 YAML frontmatter 完整性
  - 检查链接有效性（相对路径、锚点）
  - 确认无 `file:///` 绝对路径引用
  - 确认锚点使用 ASCII 格式（如需要）
  - 清理临时抓取的 source-*.md 文件（可选保留作为参考）
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `programmatic` TR-13.1: 文件名符合 kebab-case + 数字前缀规范
  - `programmatic` TR-13.2: 所有 YAML frontmatter 有效且包含 source 字段
  - `human-judgement` TR-13.3: 整体格式符合项目文档规范
- **Notes**: 使用项目现有脚本进行自动化验证
