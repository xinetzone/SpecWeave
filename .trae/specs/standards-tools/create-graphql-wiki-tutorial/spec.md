# GraphQL 完整 Wiki 教程 - Product Requirement Document

## Overview
- **Summary**: 基于 GraphQL 官方文档（graphql.org）创建一份系统性的 GraphQL 技术 Wiki 教程，覆盖核心概念、查询语言、类型系统、Schema 设计、执行机制、Python 生态工具与最佳实践，以原子化章节形式组织，便于开发者系统学习。
- **Purpose**: 当前项目知识库中缺少 GraphQL 相关的系统性学习资料。GraphQL 作为现代 API 开发的重要查询语言和运行时，是构建灵活、高效 API 的关键技术，需要一份结构清晰、内容完整的 Wiki 教程供项目开发者参考使用。
- **Target Users**: 后端开发者、前端开发者、全栈工程师、需要学习或使用 GraphQL 进行 API 开发的技术人员。

## Goals
- 在 `.agents/docs/knowledge/learning/01-agent-protocols-interfaces/` 下创建 `graphql-wiki/` 原子化教程目录
- 基于 GraphQL 官方文档（https://graphql.org/、https://graphql.org/learn/introduction/、https://graphql.org/community/tools-and-libraries/?tags=python）编写完整教程
- 教程覆盖：GraphQL 概述与核心概念、查询语言（Queries/Mutations/Subscriptions）、Schema 与类型系统、验证与执行机制、客户端使用、服务端开发、Python 生态工具链、最佳实践、FAQ 与资源
- 包含入口导航文档（README.md）和独立的原子化章节文档
- 遵循项目文档规范：YAML frontmatter（含 `source` 溯源字段）、相对路径引用、双向导航、术语表（≥15条核心术语）

## Non-Goals (Out of Scope)
- 不深入特定编程语言（除 Python 工具章节外）的服务端/客户端实现细节
- 不包含 Apollo Federation、GraphQL 联邦等高级架构主题的深度实现
- 不包含实时订阅（Subscriptions）的复杂生产环境部署指南
- 不创建可运行的示例项目仓库（仅提供代码片段示例）

## Background & Context
- GraphQL 是 Facebook 于 2012 年内部使用、2015 年开源的 API 查询语言和运行时
- 目前由 Linux 基金会下的 GraphQL 基金会支持，被全球众多行业领先公司使用
- GraphQL 提供强类型 Schema、精确数据获取、单请求多资源、无版本演进等核心优势
- Python 生态有丰富的 GraphQL 工具库（Graphene、Strawberry、Ariadne、gql 等）
- 项目现有知识库中已有 FFI、Protobuf、IDL 等 API/接口相关 Wiki，GraphQL 作为重要补充

## Functional Requirements
- **FR-1**: Wiki 教程目录结构完整，包含 README.md 导航入口和原子化章节文档
- **FR-2**: 教程内容全面覆盖 GraphQL 核心知识领域：概念、查询、类型系统、Schema、执行、客户端、服务端、Python 工具、最佳实践
- **FR-3**: 每个章节包含代码示例（查询示例、Schema 定义、Python 代码片段）
- **FR-4**: 文档包含完整术语表（≥15条核心术语），符合项目专业术语规范
- **FR-5**: 所有文档遵循项目格式规范：YAML frontmatter、相对路径引用、双向导航、source 溯源
- **FR-6**: Python 工具章节覆盖主流 Python GraphQL 库（Graphene、Strawberry、Ariadne、gql 等）

## Non-Functional Requirements
- **NFR-1**: 文档语言为中文，使用标准现代汉语书面语，专业术语首次出现附 plain language 解释
- **NFR-2**: 章节原子化，每章聚焦单一主题，文件大小适中（建议单文件≤800行）
- **NFR-3**: 文档结构与现有 Wiki（如 ffi-wiki、protobuf-wiki）保持一致，便于知识体系统一
- **NFR-4**: 所有外部引用使用官方文档 URL，确保可追溯性

## Constraints
- **Technical**: 文档格式为 Markdown，遵循项目 Markdown 规范（YAML frontmatter、ASCII 锚点、相对路径）
- **Business**: 基于公开的 GraphQL 官方文档编写，不包含私有或付费内容
- **Dependencies**: 需要抓取并参考 graphql.org 官方文档内容（已抓取源文件）

## Assumptions
- 用户希望教程侧重 Python 生态（根据提供的 Python tools URL 判断）
- 教程面向有一定 API 开发基础（了解 REST）的开发者
- 遵循现有 Wiki 的 00-overview.md、01-xxx.md 编号命名模式

## Acceptance Criteria

### AC-1: Wiki 目录结构完整
- **Given**: 教程创建完成
- **When**: 检查 `graphql-wiki/` 目录
- **Then**: 目录包含 README.md 导航入口 + ≥8 个原子化章节文档
- **Then**: 每个文档包含 YAML frontmatter，其中 `source` 字段标注来源为 `spec:create-graphql-wiki-tutorial`
- **Verification**: `programmatic`

### AC-2: 内容覆盖核心领域
- **Given**: 开发者阅读完整教程
- **When**: 按章节顺序学习
- **Then**: 应能理解：GraphQL 是什么与为什么使用、GraphQL 查询语言基础（Queries/Mutations）、Schema 与类型系统（标量/对象/枚举/接口/联合/输入类型）、GraphQL 验证与执行流程、GraphQL 客户端基础、GraphQL 服务端基础概念、Python 生态主流工具介绍、GraphQL 最佳实践与常见问题
- **Verification**: `human-judgment`

### AC-3: 包含代码示例
- **Given**: 技术章节文档
- **When**: 阅读对应章节
- **Then**: 查询/Schema 相关章节包含 GraphQL 代码示例
- **Then**: Python 工具章节包含 Python 代码片段
- **Verification**: `human-judgment`

### AC-4: 术语表符合规范
- **Given**: 术语表章节（11-glossary.md 或 README 中）
- **When**: 检查术语条目
- **Then**: 包含 ≥15 条核心 GraphQL 术语，每条术语包含 plain language 解释
- **Verification**: `programmatic`

### AC-5: 文档格式合规
- **Given**: 所有生成的 Markdown 文档
- **When**: 运行项目格式检查
- **Then**: 文件名符合 kebab-case + 数字前缀规范
- **Then**: 使用相对路径交叉引用，无 `file:///` 绝对路径
- **Then**: 锚点链接使用 ASCII 格式（显式 `<a id="..."></a>`）
- **Verification**: `programmatic`

### AC-6: 与现有知识体系关联
- **Given**: 教程中涉及相关概念
- **When**: 阅读相关章节
- **Then**: 应引用项目内已有的相关 Wiki（如 IDL Wiki、API/ABI/Protocol Wiki）
- **Verification**: `human-judgment`

## Open Questions
- 无（需求明确，基于官方公开文档和现有 Wiki 模式即可执行）
