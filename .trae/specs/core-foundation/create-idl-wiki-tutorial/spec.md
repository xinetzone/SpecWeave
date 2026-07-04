---
version: "1.0"
---
# IDL（接口定义语言）Wiki 教程 - Product Requirement Document

## Why
当前项目知识库已有 `interface-api-abi-protocol-wiki` 等系统性技术教程，但缺少对 **IDL（Interface Definition Language，接口定义语言）** 这一关键技术的系统讲解。IDL 是分布式系统、跨语言调用、序列化协议设计的基石，且 MDI 项目复盘中明确提到 IDL 概念在 AI Agent 工具定义场景下的应用价值（参见 [insight-extraction.md#L45-L47](../../../../docs/retrospective/reports/project-reports/retrospective-mdi-project-completion-20260702/insight-extraction.md#L45-L47)）。

开发人员常对以下问题感到困惑：
- Protocol Buffers、Thrift、CORBA IDL、COM IDL 这些"接口定义语言"到底有什么区别？
- IDL 与 OpenAPI、GraphQL Schema 是什么关系？是同一类东西吗？
- IDL 文件写完后是如何被编译成多语言代码的？工具链如何选择？
- 在 AI 协作开发场景下，Markdown 也可以作为 IDL 吗？

本教程旨在系统回答上述问题，填补知识库在 IDL 领域的空白。

## What Changes
- **新增** 9 个原子化 Markdown 文档，构成完整的 IDL wiki 教程，放置于 `docs/knowledge/learning/idl-wiki/` 目录
- **新增** 教程总览与导航索引（`00-overview.md`）
- **新增** IDL 定义与作用章节（`01-what-is-idl.md`）
- **新增** IDL 基本语法结构章节（`02-syntax-basics.md`），涵盖类型定义、接口声明、方法描述
- **新增** 主要 IDL 规范介绍章节（`03-major-idl-specs.md`），覆盖 Protocol Buffers、Thrift、CORBA IDL、COM IDL、Avro IDL
- **新增** IDL 规范对比章节（`04-comparison.md`），含 Mermaid 图与对比表格
- **新增** IDL 编译流程与工具链章节（`05-toolchain.md`）
- **新增** 实际应用案例与最佳实践章节（`06-use-cases.md`）
- **新增** 与现代接口描述方式对比章节（`07-vs-modern-formats.md`），对比 OpenAPI/GraphQL Schema/JSON Schema/AsyncAPI
- **新增** 学习资源与参考资料章节（`08-resources.md`），含术语表、权威资料、扩展阅读
- **不修改** 现有 `interface-api-abi-protocol-wiki`（IDL 与 Interface/API/ABI/Protocol 是不同维度的概念，本教程为独立新增）

## Impact
- **Affected specs**: 无（独立新增 wiki 教程，不修改已有 spec）
- **Affected code**: 无代码改动，仅文档新增
- **Affected files**:
  - 新增：`docs/knowledge/learning/idl-wiki/00-overview.md` ~ `08-resources.md` 共 9 个文件
  - 后续可能由 `docgen-cmd` 自动纳入 `docs/knowledge/learning/` 索引（不在本 spec 范围内）
- **Related wikis**:
  - [interface-api-abi-protocol-wiki](../../../../docs/knowledge/learning/interface-api-abi-protocol-wiki/) — 互补关系，本教程在 `00-overview.md` 与 `07-vs-modern-formats.md` 中引用该 wiki 作为延伸阅读
  - [agent-interface-deep-dive](../../../../docs/knowledge/learning/agent-interface-deep-dive/) — AI Agent 接口视角，本教程在 `06-use-cases.md` 中交叉引用

## Background & Context
IDL（Interface Definition Language）是一种用于以语言中立方式描述软件接口的特殊语言。它的核心价值是 **平台中立 + 语言中立**：用 IDL 写一次接口定义，通过编译器生成多种目标语言的客户端/服务端桩代码，避免人工维护多语言重复定义。

IDL 的发展经历了三个阶段：
1. **RPC 时代（1980s-1990s）**：CORBA IDL、COM/DCOM IDL、ONC RPC（XDR）—— 用于分布式对象计算
2. **序列化框架时代（2000s-2010s）**：Protocol Buffers、Thrift、Avro —— 用于高效跨语言序列化与 RPC
3. **现代接口描述时代（2010s-至今）**：OpenAPI、GraphQL Schema、gRPC IDL（基于 Protobuf）—— 用于 Web API、API 网关、微服务

本教程采用原子化文档结构，遵循项目已有 wiki 规范（参考 `interface-api-abi-protocol-wiki` 的文件组织、YAML frontmatter、导航链接模式）。

## ADDED Requirements

### Requirement: IDL Wiki 教程目录与总览
The system SHALL provide a `00-overview.md` file at `docs/knowledge/learning/idl-wiki/` containing a complete tutorial overview with reading guide, chapter navigation table, and Mermaid concept hierarchy diagram.

#### Scenario: 用户访问 IDL wiki 入口
- **WHEN** 用户打开 `docs/knowledge/learning/idl-wiki/00-overview.md`
- **THEN** 文档包含：教程简介、9 章导航表、IDL 在接口技术栈中的定位图（Mermaid）、目标读者说明、阅读路径建议

### Requirement: IDL 定义与作用文档
The system SHALL provide a `01-what-is-idl.md` file explaining the definition, core characteristics, historical evolution, and value proposition of IDL.

#### Scenario: 用户学习 IDL 基本概念
- **WHEN** 用户阅读 `01-what-is-idl.md`
- **THEN** 文档包含：IDL 标准定义、≥5 个核心特征（语言中立/平台中立/可编译生成/支持类型系统/契约式设计）、IDL 发展三阶段时间线（Mermaid）、IDL 解决的核心问题（多语言重复定义痛点）、与编程语言原生接口的对比

### Requirement: IDL 基本语法结构文档
The system SHALL provide a `02-syntax-basics.md` file covering the common syntax elements of IDL: type definitions, interface declarations, method descriptions, annotations/comments.

#### Scenario: 用户学习 IDL 语法
- **WHEN** 用户阅读 `02-syntax-basics.md`
- **THEN** 文档包含：基本数据类型（标量/复合类型/枚举/容器）、接口声明语法、方法描述（参数/返回值/异常）、注解与注释机制，每项配 ≥1 个代码示例（至少包含 Protocol Buffers 与 CORBA IDL 两种语法对照）

### Requirement: 主要 IDL 规范介绍文档
The system SHALL provide a `03-major-idl-specs.md` file introducing at least 5 major IDL specifications with code examples and use cases.

#### Scenario: 用户了解主流 IDL 实现
- **WHEN** 用户阅读 `03-major-idl-specs.md`
- **THEN** 文档覆盖以下 5 种 IDL，每种含：起源背景、语法示例、典型应用场景、生态工具
  - Protocol Buffers（Google，2001）
  - Apache Thrift（Facebook，2007）
  - CORBA IDL（OMG，1991）
  - COM/DCOM IDL（Microsoft，1993）
  - Apache Avro IDL（Hadoop，2009）

### Requirement: IDL 规范对比文档
The system SHALL provide a `04-comparison.md` file comparing different IDL specifications across multiple dimensions.

#### Scenario: 用户选择 IDL 方案
- **WHEN** 用户阅读 `04-comparison.md`
- **THEN** 文档包含：多维度对比表格（语法风格/类型系统/二进制格式/Schema 演进/工具链生态/学习曲线/性能）、Mermaid 雷达图或决策树、选型决策指南（按场景推荐）

### Requirement: IDL 编译流程与工具链文档
The system SHALL provide a `05-toolchain.md` file explaining the IDL compilation pipeline and toolchain ecosystem.

#### Scenario: 用户理解 IDL 工作流
- **WHEN** 用户阅读 `05-toolchain.md`
- **THEN** 文档包含：IDL 编译流程图（Mermaid，source → IDL → compiler → codegen → target language stubs）、主流编译器介绍（protoc/thrift/avro-tools/idl2java 等）、构建系统集成（Maven/Gradle/Bazel）、Schema 演进与兼容性管理、代码生成配置示例

### Requirement: 实际应用案例与最佳实践文档
The system SHALL provide a `06-use-cases.md` file presenting real-world application cases and best practices.

#### Scenario: 用户参考 IDL 实践
- **WHEN** 用户阅读 `06-use-cases.md`
- **THEN** 文档包含：≥3 个完整应用案例（如 gRPC 服务定义、Thrift 微服务接口、CORBA 遗留系统集成），每个案例含 IDL 源码 + 生成代码片段 + 调用示例；最佳实践清单（命名规范、版本管理、向后兼容、字段编号规则、错误处理）

### Requirement: 与现代接口描述方式对比文档
The system SHALL provide a `07-vs-modern-formats.md` file comparing traditional IDL with modern interface description formats (OpenAPI, GraphQL Schema, JSON Schema, AsyncAPI).

#### Scenario: 用户区分 IDL 与现代格式
- **WHEN** 用户阅读 `07-vs-modern-formats.md`
- **THEN** 文档包含：传统 IDL vs 现代 IDL 的边界划分、对比表格（关注点/序列化/传输协议/工具链/AI 友好度）、Mermaid 演进关系图、各格式适用场景说明、与 MDI（Markdown Interface）的关联（引用项目内 MDI 复盘洞察）

### Requirement: 学习资源与参考资料文档
The system SHALL provide a `08-resources.md` file providing a glossary, authoritative references, and further reading recommendations.

#### Scenario: 用户深入学习
- **WHEN** 用户阅读 `08-resources.md`
- **THEN** 文档包含：术语表（≥15 个 IDL 相关术语）、权威参考资料链接（OMG 规范、Google Protobuf 官方文档、Apache Thrift 文档等）、按难度分级的扩展阅读建议、与项目内相关 wiki 的交叉引用（`interface-api-abi-protocol-wiki`、`agent-interface-deep-dive`）

### Requirement: 文档元数据与导航规范
The system SHALL ensure all 9 wiki files follow consistent metadata and navigation conventions matching the existing `interface-api-abi-protocol-wiki` pattern.

#### Scenario: 验证文档元数据
- **WHEN** 检查任意 wiki 文件 frontmatter
- **THEN** 包含完整 YAML frontmatter 字段：`id`、`title`、`x-toml-ref`、`source`（值为 `spec:create-idl-wiki-tutorial`）、`category`（值为 `learning`）、`tags`、`date`、`status`、`author`、`summary`

#### Scenario: 验证双向导航
- **WHEN** 检查分章文档（01-07）
- **THEN** 每个文档底部包含双向导航：上一章、返回目录（`00-overview.md`）、下一章

## Non-Functional Requirements
- **NFR-1**: 每个原子文档不超过 300 行，遵循单一职责原则
- **NFR-2**: 技术术语准确，参考权威来源（OMG 规范、Google Protobuf 官方文档、Apache Thrift 文档、RFC 等）
- **NFR-3**: 语言专业准确同时保持可读性，适合初中级到高级开发人员阅读
- **NFR-4**: 所有内部链接使用相对路径，无 `file:///` 绝对路径，通过链接检查
- **NFR-5**: 代码示例可运行或具有明确说明性，标注语言类型
- **NFR-6**: 遵循项目文档命名规范（kebab-case，数字前缀排序）
- **NFR-7**: 每个文档携带 `x-toml-ref` 字段指向 `.meta/toml/` 下的对应 TOML 文件路径

## Constraints
- **Technical**: 使用 Markdown + Mermaid 图表，遵循项目现有 wiki 格式（参考 `interface-api-abi-protocol-wiki` 结构）
- **Business**: 教程内容需引用项目内已有的 MDI 复盘洞察（`docs/retrospective/reports/project-reports/retrospective-mdi-project-completion-20260702/insight-extraction.md`），体现 IDL 在 AI 协作场景下的延伸价值
- **Dependencies**:
  - 依赖项目现有知识库结构与 `generate_index.py` 索引脚本
  - 依赖 `interface-api-abi-protocol-wiki` 作为延伸阅读引用对象（不修改该 wiki）

## Assumptions
- 读者具备基础编程知识，了解至少一门编程语言（Python/Go/Java/TS 等）
- 读者对分布式系统、序列化有基本认知（不要求深入）
- 文档放置于 `docs/knowledge/learning/idl-wiki/` 目录
- 完成后可通过 `generate_index.py` / `docgen-cmd` 自动纳入知识库索引

## Acceptance Criteria

### AC-1: 目录结构完整
- **Given**: 教程创建完成
- **When**: 查看目标目录 `docs/knowledge/learning/idl-wiki/`
- **Then**: 包含 `00-overview.md` 到 `08-resources.md` 共 9 个文件，每个文件 < 300 行
- **Verification**: `programmatic`
- **Notes**: 运行 `python .agents/scripts/check-file-size.py --path docs/knowledge/learning/idl-wiki/` 验证

### AC-2: IDL 定义与作用完整
- **Given**: `01-what-is-idl.md` 文档
- **When**: 阅读文档
- **Then**: 包含标准定义、≥5 个核心特征、发展三阶段时间线（Mermaid）、与编程语言原生接口的对比
- **Verification**: `human-judgment`

### AC-3: 基本语法结构完整
- **Given**: `02-syntax-basics.md` 文档
- **When**: 阅读文档
- **Then**: 包含类型定义、接口声明、方法描述、注解/注释，每项配 ≥1 个代码示例，至少包含 Protobuf 与 CORBA IDL 两种语法对照
- **Verification**: `human-judgment`

### AC-4: 主要 IDL 规范覆盖完整
- **Given**: `03-major-idl-specs.md` 文档
- **When**: 阅读文档
- **Then**: 覆盖 Protocol Buffers、Thrift、CORBA IDL、COM IDL、Avro IDL 共 5 种，每种含起源、语法示例、应用场景、生态工具
- **Verification**: `human-judgment`

### AC-5: 规范对比系统
- **Given**: `04-comparison.md` 文档
- **When**: 阅读文档
- **Then**: 包含多维度对比表格、Mermaid 决策图、选型决策指南
- **Verification**: `human-judgment`

### AC-6: 工具链章节完整
- **Given**: `05-toolchain.md` 文档
- **When**: 阅读文档
- **Then**: 包含编译流程 Mermaid 图、≥3 个主流编译器介绍、构建系统集成示例、Schema 演进与兼容性管理说明
- **Verification**: `human-judgment`

### AC-7: 应用案例充分
- **Given**: `06-use-cases.md` 文档
- **When**: 阅读文档
- **Then**: 包含 ≥3 个完整应用案例（含 IDL 源码 + 生成代码片段 + 调用示例），≥5 条最佳实践
- **Verification**: `human-judgment`

### AC-8: 与现代格式对比完整
- **Given**: `07-vs-modern-formats.md` 文档
- **When**: 阅读文档
- **Then**: 包含传统 IDL vs 现代 IDL 边界、对比表格（覆盖 OpenAPI/GraphQL Schema/JSON Schema/AsyncAPI）、Mermaid 演进图、与 MDI 的关联引用
- **Verification**: `human-judgment`

### AC-9: 元数据规范
- **Given**: 所有 9 个文档
- **When**: 检查 frontmatter
- **Then**: 每个文档包含完整 YAML frontmatter，`source` 字段值为 `spec:create-idl-wiki-tutorial`，`category` 为 `learning`
- **Verification**: `programmatic`

### AC-10: 链接有效
- **Given**: 教程完成
- **When**: 运行链接检查
- **Then**: 所有内部相对路径链接有效，无 `file:///` 绝对路径断链
- **Verification**: `programmatic`
- **Notes**: 运行 `python .agents/scripts/check-links.py --path docs/knowledge/learning/idl-wiki/` 验证

### AC-11: 双向导航
- **Given**: 分章文档（01-07）
- **When**: 检查导航链接
- **Then**: 每个文档包含上一章、返回目录、下一章的双向导航链接
- **Verification**: `human-judgment`

### AC-12: 参考资料完整
- **Given**: `08-resources.md` 文档
- **When**: 阅读文档
- **Then**: 包含 ≥15 条术语表、权威参考资料链接、分难度扩展阅读建议、与项目内相关 wiki 的交叉引用
- **Verification**: `human-judgment`

## Open Questions
- [ ] 是否需要在 `02-syntax-basics.md` 中加入 FlatBuffers/Cap'n Proto 等零拷贝序列化的 IDL 语法示例？（当前仅在 `04-comparison.md` 提及，不在 `03-major-idl-specs.md` 详述）
- [ ] `06-use-cases.md` 中 gRPC 案例是否需要展示完整的客户端调用流程（含拦截器、超时、重试）？还是仅展示 IDL 定义层？
- [ ] `07-vs-modern-formats.md` 中 MDI 关联部分是否需要补充 MDI 项目复盘中"洞察1"的完整引用，还是仅简述并链接？
