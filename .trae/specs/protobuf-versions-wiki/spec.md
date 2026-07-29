---
version: "1.0"
---
# Protocol Buffers 版本演进知识库 - Product Requirement Document

## Overview
- **Summary**: 创建一个结构化的 Protocol Buffers（protobuf）版本演进知识 wiki（`protobuf-wiki/`），系统梳理 protobuf 从 Google 内部诞生到 Editions 时代的完整版本历史，包括各版本的发布时间线、核心特性、重要改进、兼容性情况、适用场景，以及版本间关键差异对比和功能演进历程。使用七概念方法论（R→I→E→V 知识沉淀链路）确保内容的事实准确性、洞察深度和模式可复用性。
- **Purpose**: 团队成员在技术选型（proto2 vs proto3 vs Editions）、版本迁移决策、遗留系统维护（如 Caffe proto2）时，需要一份权威、系统、可快速查阅的版本指南。现有知识库（idl-wiki）仅在 04-major-idl-specs.md 中提供了约 40 行 protobuf 简介，缺乏版本演进的深度分析和迁移决策支持。
- **Target Users**: 后端工程师、架构师、AI 智能体（用于技术选型决策）、Caffe 等遗留 proto2 项目维护者、需要在多个 protobuf 版本间做决策的开发团队。

## Goals
- **G1**: 系统梳理 protobuf 从 Google 内部版本（proto1/proto2）到开源 proto2、proto3 再到 Editions（2023/2024）的完整版本时间线，每个版本包含发布时间、背景、核心特性、改进、兼容性
- **G2**: 提供 proto2/proto3/Editions 三版本的多维度差异对比矩阵，覆盖语法、语义、API、生态、迁移成本
- **G3**: 提炼关键功能的演进历程（字段 presence、枚举、扩展机制、默认值、JSON映射、未知字段处理），解释"为什么变"而不仅仅是"变了什么"
- **G4**: 形成可复用的"序列化 IDL 版本选型决策模型"，帮助团队在不同场景下选择合适版本
- **G5**: 提供版本迁移路径指南（proto2→proto3、proto2/proto3→Editions），包含风险检查清单
- **G6**: 作为独立的 `protobuf-wiki/` 专题放置于 `01-agent-protocols-interfaces/` 下，与 idl-wiki、caffe-architecture-wiki 形成交叉引用

## Non-Goals (Out of Scope)
- 不编写 protobuf 语法入门教程（idl-wiki 已覆盖基础语法）
- 不涉及 protobuf 具体语言绑定的 API 使用细节（如 C++/Java/Python 特定 API）
- 不创建与 idl-wiki 现有章节重复的内容（如类型系统详解、工具链操作步骤）
- 不进行 protobuf 与其他序列化格式（Thrift/Avro/FlatBuffers）的对比（idl-wiki/05-comparison.md 已覆盖）
- 不修改或迁移现有 caffe-architecture-wiki 中的 proto2 vs proto3 分析文档（保持独立，建立交叉引用）
- 不涵盖 protobuf 在 Google 内部非公开的历史版本细节

## Background & Context
- **现有知识资产**:
  - [idl-wiki/04-major-idl-specs.md](file:///d:/spaces/SpecWeave/.agents/docs/knowledge/learning/01-agent-protocols-interfaces/idl-wiki/04-major-idl-specs.md) 中有 protobuf 简要介绍（约40行）
  - [caffe-architecture-wiki/04-proto2-vs-proto3-serialization-analysis.md](file:///d:/spaces/SpecWeave/.agents/docs/knowledge/learning/caffe-architecture-wiki/04-proto2-vs-proto3-serialization-analysis.md) 中有 proto2/proto3 详细对比（七概念方法论产出）
  - Caffe 项目（external/chaos/caffe）使用 proto2 作为配置 DSL，是典型的 proto2 遗留系统实例
- **技术背景**:
  - Protobuf 经历了：Google 内部原型（2001）→ 开源 proto2（2008）→ proto3（2016，随 gRPC 推广）→ Editions（2022 提出，2023/2024 正式发布）四个主要阶段
  - proto3 对 proto2 做了大量减法（移除 required、取消自定义默认值、枚举首值必须为0），但在后续版本（3.15+）又逐步恢复了部分特性（optional presence）
  - Editions 是 Google 推出的新范式，用 feature 选项机制替代 proto2/proto3 硬二分，代表 protobuf 的未来方向
  - 团队需要理解这些版本变化背后的设计哲学演进，而非仅记忆语法差异

## Functional Requirements
- **FR-1**: 版本时间线文档（01-version-timeline.md）
  - 覆盖所有主要版本：Google 内部版（proto1）、开源 proto2（v2.0-v3.0 前）、proto3（v3.0-v3.x 各重要里程碑）、Editions（2023/2024）
  - 每个版本包含：版本号/标识、发布年份、发布背景、核心特性列表、重要改进点、已知问题/局限
- **FR-2**: 三版对比矩阵文档（02-version-comparison.md）
  - 至少覆盖 12 个对比维度：语法声明、字段修饰符、字段 presence、默认值、枚举规则、扩展机制、Any 类型、JSON 映射、map 类型、oneof、未知字段处理、线格式兼容性
  - 每个维度包含 proto2/proto3/Editions 三列对比
  - 标注每个差异的兼容性影响（线格式兼容/API不兼容/线格式不兼容）
- **FR-3**: 关键功能演进史文档（03-feature-evolution.md）
  - 至少覆盖 6 个核心功能的演进历程：字段 presence、枚举类型、扩展机制（extensions→Any）、默认值语义、packed 编码、未知字段处理
  - 每个功能演进包含：问题背景、各版本中的行为、变化原因（设计哲学）、迁移影响
- **FR-4**: 选型决策指南文档（04-selection-guide.md）
  - 提供决策树：场景→约束→推荐版本
  - 包含适用场景矩阵：RPC/gRPC、配置DSL、持久化存储、跨语言微服务、遗留系统维护、新项目启动
  - 提炼"序列化 IDL 版本选型"可复用模式
- **FR-5**: 迁移路径与风险清单文档（05-migration-guide.md）
  - proto2→proto3 迁移：逐项检查清单、渐进式迁移策略、常见陷阱
  - proto2/proto3→Editions 迁移：Prototiller 工具使用、feature 映射表
  - 线格式兼容性边界说明
- **FR-6**: 总览与导航（00-overview.md）+ README 索引
  - 提供文档结构图、推荐阅读路径、快速查阅表
  - 与 idl-wiki、caffe-architecture-wiki 建立交叉引用
- **FR-7**: 使用七概念方法论（R→I→E→V）产出，确保事实无因果词、洞察有四元组、模式可迁移、经对抗审查

## Non-Functional Requirements
- **NFR-1**: 事实准确性：所有版本发布时间、特性描述必须可溯源到官方文档（protobuf.dev）或权威来源
- **NFR-2**: 结构一致性：文档结构遵循项目 wiki 惯例（frontmatter、编号、标题层级、交叉引用格式）
- **NFR-3**: 可导航性：每个文档有"上一章/返回目录/下一章"导航，README 有完整索引表
- **NFR-4**: 可复用性：提炼的模式和决策模型可迁移到其他 IDL/序列化格式版本对比场景
- **NFR-5**: 中文输出：所有文档使用中文撰写（与现有知识库一致）

## Constraints
- **Technical**:
  - 文档格式为 Markdown，遵循项目现有 frontmatter 规范（YAML frontmatter，含 id、title、date、tags、source 等字段）
  - 文件链接使用 `file:///` 绝对路径格式（与 idl-wiki、caffe-architecture-wiki 现有风格保持一致）
  - 输出目录：`.agents/docs/knowledge/learning/01-agent-protocols-interfaces/protobuf-wiki/`
- **Dependencies**:
  - protobuf 官方文档（protobuf.dev）作为主要信息来源
  - 现有 caffe-architecture-wiki 中的 proto2/proto3 分析作为事实基础
  - 七概念方法论作为分析框架

## Assumptions
- 用户期望的"主要版本"包括：Google 内部版、开源 proto2、proto3（含重要子版本里程碑）、Editions（2023/2024）
- 文档面向有一定 protobuf 使用经验的开发者，而非完全零基础的初学者
- 七概念方法论的 R→I→E→V 链路适用于此知识沉淀任务
- 创建新的 protobuf-wiki 目录（而非在 idl-wiki 中扩展），因为这是深度专题内容，与 idl-wiki 的教程定位不同

## Acceptance Criteria

### AC-1: 版本时间线完整性
- **Given**: 文档 01-version-timeline.md 已创建
- **When**: 审阅版本覆盖范围
- **Then**: 至少覆盖 Google内部版(proto1)、proto2开源版、proto3初版、proto3重要里程碑(3.5/3.14/3.15+)、Editions 2023、Editions 2024 共6个以上版本节点，每个节点有发布年份和核心特性
- **Verification**: `human-judgment`
- **Notes**: 信息源为 protobuf 官方文档和 release notes

### AC-2: 三版对比矩阵覆盖度
- **Given**: 文档 02-version-comparison.md 已创建
- **When**: 检查对比维度
- **Then**: 覆盖至少12个对比维度（语法声明、字段修饰符、presence、默认值、枚举、扩展、Any、JSON、map、oneof、未知字段、线格式），每个维度有 proto2/proto3/Editions 三列
- **Verification**: `human-judgment`

### AC-3: 功能演进解释深度
- **Given**: 文档 03-feature-evolution.md 已创建
- **When**: 阅读功能演进章节
- **Then**: 每个功能演进不仅描述"变了什么"，还解释"为什么变"（设计动机），包含至少6个核心功能的演进历程
- **Verification**: `human-judgment`

### AC-4: 选型决策模型可用性
- **Given**: 文档 04-selection-guide.md 已创建
- **When**: 根据具体场景（如"新建gRPC微服务"、"维护Caffe类配置系统"）查阅决策指南
- **Then**: 能得到明确的版本推荐和理由，决策树覆盖至少6种典型场景
- **Verification**: `human-judgment`

### AC-5: 迁移检查清单实用性
- **Given**: 文档 05-migration-guide.md 已创建
- **When**: 对照 caffe.proto 评估 proto2→proto3 迁移
- **Then**: 检查清单能识别出 caffe.proto 中所有需要修改的 proto2 特性（required/default/extensions/packed/enum首值）
- **Verification**: `programmatic` + `human-judgment`
- **Notes**: 以 caffe.proto 为验证实例

### AC-6: 七概念方法论质量门通过
- **Given**: 所有文档完成后
- **When**: 对照七概念质量门检查
- **Then**: G1（事实无因果词）、G2（洞察四元组完整）、G3（模式可迁移）、V（对抗审查≥2视角）全部通过
- **Verification**: `human-judgment`

### AC-7: 文档结构规范
- **Given**: 所有文档已写入目标目录
- **When**: 检查文件结构
- **Then**: 包含 00-overview.md、01-05 专题文档、README.md（自动索引）；每个文档有完整 YAML frontmatter；导航链接正确；交叉引用有效
- **Verification**: `programmatic`（链接检查器）+ `human-judgment`

### AC-8: 交叉引用正确
- **Given**: 所有文档完成
- **When**: 运行链接检查
- **Then**: 所有 file:/// 链接和相对路径链接均有效，无断链；与 idl-wiki 和 caffe-architecture-wiki 的交叉引用正确
- **Verification**: `programmatic`（运行 check-links.py）

## Open Questions
- [ ] Editions 2024 的具体 feature 变更细节是否需要深入到每个 feature 开关级别？（初步计划：覆盖主要 feature，不深入所有细节）
- [ ] proto3 子版本（如 3.5/3.12/3.14/3.15/3.19 等）需要覆盖到多细的粒度？（初步计划：以重要里程碑为主，不覆盖每个 patch 版本）
- [ ] 是否需要包含 protobuf 各语言实现（protobuf-java/protobuf-go/protobuf-python 等）的版本差异？（初步计划：不包含，聚焦核心 IDL 规范层面）
