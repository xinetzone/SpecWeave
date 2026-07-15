---
version: "1.0"
x-toml-ref: "../../../../.meta/toml/.trae/specs/core-foundation/create-ffi-wiki-tutorial/spec.toml"
---
# FFI（外部函数接口）Wiki 教程 - Product Requirement Document

## Why
当前项目知识库已有 `interface-api-abi-protocol-wiki`（接口/API/ABI/协议）和 `idl-wiki`（接口定义语言）两套系统性技术教程，但缺少对 **FFI（Foreign Function Interface，外部函数接口）** 这一关键跨语言调用机制的系统讲解。FFI 是实现多语言互操作性的核心技术，将 ABI 层面的理论转化为可实践的跨语言调用方案，且与 ABI 章节（[03-abi.md#L48-L49](../../../../.agents/docs/knowledge/learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/03-abi.md#L48-L49)）和 IDL 教程中的代码生成实践（[06-use-cases.md](../../../../docs/knowledge/learning/idl-wiki/06-use-cases.md)）形成知识互补。

开发人员常对以下问题感到困惑：
- FFI 和 API、ABI 到底是什么关系？分别解决什么问题？
- Python 的 `ctypes`、Java 的 JNI、Node.js 的 `ffi-napi`、Rust 的 FFI —— 它们底层原理一样吗？
- 调用约定（calling convention）、名称修饰（name mangling）、数据封送（marshalling）这些概念到底怎么回事？
- 什么时候应该用 FFI，什么时候应该用 RPC 或 IPC？
- FFI 的性能开销有多大？安全性问题如何防范？

本教程旨在系统回答上述问题，填补知识库在 FFI 领域的空白，形成 Interface/API/ABI/Protocol → IDL → FFI 三阶段递进知识体系。

## What Changes
- **新增** 8 个原子化 Markdown 文档，构成完整的 FFI wiki 教程，放置于 `docs/knowledge/learning/ffi-wiki/` 目录
- **新增** 教程总览与导航索引（`00-overview.md`）
- **新增** FFI 定义与核心概念章节（`01-what-is-ffi.md`），涵盖定义、历史演进、核心概念
- **新增** FFI 工作原理章节（`02-working-principles.md`），涵盖调用约定、名称修饰、数据封送、内存管理、绑定生成
- **新增** 不同编程语言中的 FFI 实现章节（`03-language-implementations.md`），覆盖 C→Python/Java/Go/Rust/Node.js/C# 六种主流实现
- **新增** 应用场景与代码示例章节（`04-use-cases.md`），≥3 个完整实战案例
- **新增** 优势与局限性章节（`05-advantages-limitations.md`），含性能开销分析、安全性考量
- **新增** 相关概念对比章节（`06-comparison.md`），对比 FFI vs ABI/API/RPC/IPC/IDL
- **新增** 术语表与参考资料章节（`07-resources.md`），含 ≥15 条术语
- **不修改** 现有 `interface-api-abi-protocol-wiki` 和 `idl-wiki`（FFI 是独立维度，通过交叉引用关联）

## Impact
- **Affected specs**: 无（独立新增 wiki 教程，不修改已有 spec）
- **Affected code**: 无代码改动，仅文档新增
- **Affected files**:
  - 新增：`docs/knowledge/learning/ffi-wiki/00-overview.md` ~ `07-resources.md` 共 8 个文件
  - 后续可能由 `docgen-cmd` 自动纳入 `docs/knowledge/learning/` 索引（不在本 spec 范围内）
- **Related wikis**:
  - [interface-api-abi-protocol-wiki](../../../../.agents/docs/knowledge/learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/) — 互补关系，本教程在 `01-what-is-ffi.md` 与 `06-comparison.md` 中引用该 wiki 的 ABI/API 章节
  - [idl-wiki](../../../../.agents/docs/knowledge/learning/01-agent-protocols-interfaces/idl-wiki/) — 互补关系，IDL 代码生成与 FFI 手动绑定形成对比，在 `04-use-cases.md` 与 `06-comparison.md` 中交叉引用

## Background & Context
FFI（Foreign Function Interface）是一种允许用某种编程语言编写的代码调用用另一种编程语言编写的代码的机制。它直接操作底层 ABI（Application Binary Interface），通过遵循目标语言的调用约定、数据类型映射规则和内存管理协议，实现跨语言边界的函数调用。

FFI 的技术发展脉络：
1. **早期阶段（1970s-1980s）**：C 语言成为系统编程标准，Fortran 与 C 的互调用需求催生最早的 FFI 实践
2. **标准化阶段（1990s-2000s）**：Java JNI 出现（1997），.NET P/Invoke 出现（2002），Python ctypes 加入标准库
3. **现代阶段（2010s-至今）**：Rust FFI 的安全封装、Node.js 的 `ffi-napi`/`bun:ffi`、Go 的 cgo、自动绑定生成工具（bindgen/cffi/SWIG）成熟

本教程采用原子化文档结构，遵循项目已有 wiki 规范（参考 `idl-wiki` 和 `interface-api-abi-protocol-wiki` 的文件组织、YAML frontmatter、导航链接模式）。

## ADDED Requirements

### Requirement: FFI Wiki 教程目录与总览
The system SHALL provide a `00-overview.md` file at `docs/knowledge/learning/ffi-wiki/` containing a complete tutorial overview with reading guide, chapter navigation table, and Mermaid concept hierarchy diagram.

#### Scenario: 用户访问 FFI wiki 入口
- **WHEN** 用户打开 `docs/knowledge/learning/ffi-wiki/00-overview.md`
- **THEN** 文档包含：教程简介、8 章导航表、FFI 在跨语言技术栈中的定位图（Mermaid）、目标读者说明、阅读路径建议、与 `interface-api-abi-protocol-wiki` 和 `idl-wiki` 的关联指引

### Requirement: FFI 定义与核心概念文档
The system SHALL provide a `01-what-is-ffi.md` file explaining the definition, core concepts, historical evolution, and value proposition of FFI.

#### Scenario: 用户学习 FFI 基本概念
- **WHEN** 用户阅读 `01-what-is-ffi.md`
- **THEN** 文档包含：FFI 标准定义（Wikipedia 风格）、≥5 个核心概念（跨语言调用/调用约定/数据封送/内存边界/符号解析）、FFI 发展时间线（Mermaid）、与 ABI/API 的关系辨析、FFI 解决的核心问题（打破语言孤岛/复用已有 C 库/性能关键路径优化）

### Requirement: FFI 工作原理文档
The system SHALL provide a `02-working-principles.md` file covering the technical mechanisms of FFI: calling conventions, name mangling, data marshalling, memory management, and binding generation.

#### Scenario: 用户理解 FFI 底层机制
- **WHEN** 用户阅读 `02-working-principles.md`
- **THEN** 文档包含：调用约定详解（cdecl/stdcall/fastcall/system V AMD64，配 Mermaid 时序图）、名称修饰（C++ name mangling 原理与 `extern "C"` 解决方案）、数据封送（基本类型映射/结构体对齐/字符串传递/回调函数指针，每项配代码示例）、内存管理（所有权边界/分配释放策略）、绑定生成（手动绑定 vs 自动绑定工具）

### Requirement: 不同编程语言中的 FFI 实现文档
The system SHALL provide a `03-language-implementations.md` file covering FFI implementations in at least 6 mainstream programming languages with code examples.

#### Scenario: 用户了解各语言 FFI 方案
- **WHEN** 用户阅读 `03-language-implementations.md`
- **THEN** 文档覆盖以下 6 种实现，每种含：实现机制、核心 API、代码示例、适用场景
  - Python ctypes/cffi（C 库调用）
  - Java JNI/JNA（本地方法调用）
  - Go cgo（C 互操作）
  - Rust FFI（`extern "C"` + `unsafe` + bindgen）
  - Node.js ffi-napi/bun:ffi（动态库调用）
  - C# P/Invoke（平台调用）

### Requirement: 实际应用案例与代码示例文档
The system SHALL provide a `04-use-cases.md` file presenting real-world application cases with complete code examples.

#### Scenario: 用户参考 FFI 实践
- **WHEN** 用户阅读 `04-use-cases.md`
- **THEN** 文档包含：≥3 个完整应用案例（如 Python 调用 C 实现矩阵运算加速、Rust 集成 C 图形库、Go 通过 cgo 调用 C 压缩库），每个案例含源代码 + 调用示例 + 输出说明；最佳实践清单（错误处理/内存安全/线程安全/版本兼容/绑定测试）

### Requirement: 优势与局限性文档
The system SHALL provide a `05-advantages-limitations.md` file analyzing the advantages, limitations, performance overhead, and security considerations of FFI.

#### Scenario: 用户评估 FFI 适用性
- **WHEN** 用户阅读 `05-advantages-limitations.md`
- **THEN** 文档包含：优势（性能接近原生/复用成熟 C 库/跨语言生态整合）、局限性（类型安全损失/内存安全风险/调试困难/平台依赖/构建复杂度）、性能开销分析（调用开销分解图/基准对比数据）、安全性考量（缓冲区溢出/未定义行为/输入校验/沙箱隔离）

### Requirement: 相关概念对比文档
The system SHALL provide a `06-comparison.md` file comparing FFI with related concepts: ABI, API, RPC, IPC, and IDL.

#### Scenario: 用户辨析 FFI 与相关概念
- **WHEN** 用户阅读 `06-comparison.md`
- **THEN** 文档包含：FFI vs ABI/API/RPC/IPC/IDL 多维度对比表格（抽象层次/通信方式/性能/安全/使用场景）、Mermaid 关系图展示各概念在技术栈中的位置、选型决策树（何时用 FFI vs 何时用 RPC vs 何时用 IDL 代码生成），与 `interface-api-abi-protocol-wiki` 和 `idl-wiki` 的交叉引用

### Requirement: 术语表与参考资料文档
The system SHALL provide a `07-resources.md` file providing a comprehensive glossary, authoritative references, and further reading recommendations.

#### Scenario: 用户深入学习
- **WHEN** 用户阅读 `07-resources.md`
- **THEN** 文档包含：术语表（≥15 个 FFI 相关术语：FFI/Calling Convention/Name Mangling/Marshalling/Stub/Trampoline/Thunk/C ABI/extern "C"/P/Invoke/JNI/cgo/ctypes/cffi/bindgen 等）、权威参考资料链接（语言官方文档/经典论文/书籍）、按难度分级的扩展阅读建议、与项目内相关 wiki 的交叉引用

### Requirement: 文档元数据与导航规范
The system SHALL ensure all 8 wiki files follow consistent metadata and navigation conventions matching the existing `idl-wiki` pattern.

#### Scenario: 验证文档元数据
- **WHEN** 检查任意 wiki 文件 frontmatter
- **THEN** 包含完整 YAML frontmatter 字段：`id`、`title`、`x-toml-ref`、`source`（值为 `spec:create-ffi-wiki-tutorial`）、`category`（值为 `learning`）、`tags`、`date`、`status`、`author`、`summary`

#### Scenario: 验证双向导航
- **WHEN** 检查分章文档（01-06）
- **THEN** 每个文档底部包含双向导航：上一章、返回目录（`00-overview.md`）、下一章

## Non-Functional Requirements
- **NFR-1**: 每个原子文档不超过 300 行，遵循单一职责原则
- **NFR-2**: 技术术语准确，参考权威来源（编程语言官方文档、Wikipedia、学术论文、经典书籍）
- **NFR-3**: 语言专业准确同时保持 Wikipedia 风格——客观中立、结构清晰、适合技术读者参考
- **NFR-4**: 所有内部链接使用相对路径，无 `file:///` 绝对路径，通过链接检查
- **NFR-5**: 代码示例可运行或具有明确说明性，标注语言类型，优先使用 C/Python/Rust/Go 等主流语言
- **NFR-6**: 遵循项目文档命名规范（kebab-case，数字前缀排序）

## Constraints
- **Technical**: 使用 Markdown + Mermaid 图表，遵循项目现有 wiki 格式（参考 `idl-wiki` 结构）
- **Business**: 教程内容需与 `interface-api-abi-protocol-wiki`（ABI 章节）和 `idl-wiki`（代码生成章节）形成知识互补，通过交叉引用建立三套教程的关联体系
- **Dependencies**:
  - 依赖项目现有知识库结构与 `generate_index.py` 索引脚本
  - 依赖 `interface-api-abi-protocol-wiki` 与 `idl-wiki` 作为关联引用对象（不修改这两套 wiki）

## Assumptions
- 读者具备基础编程知识，了解至少一门编程语言（Python/Go/Rust/Java/C 等）
- 读者对 C 语言基础语法有基本了解（C 是 FFI 的通用中间语言）
- 文档放置于 `docs/knowledge/learning/ffi-wiki/` 目录
- 完成后可通过 `generate_index.py` / `docgen-cmd` 自动纳入知识库索引

## Acceptance Criteria

### AC-1: 目录结构完整
- **Given**: 教程创建完成
- **When**: 查看目标目录 `docs/knowledge/learning/ffi-wiki/`
- **Then**: 包含 `00-overview.md` 到 `07-resources.md` 共 8 个文件，每个文件 < 300 行
- **Verification**: `programmatic`
- **Notes**: 运行 `python .agents/scripts/check-file-size.py --path docs/knowledge/learning/ffi-wiki/` 验证

### AC-2: FFI 定义与核心概念完整
- **Given**: `01-what-is-ffi.md` 文档
- **When**: 阅读文档
- **THEN**: 包含 Wikipedia 风格的标准定义、≥5 个核心概念、发展时间线（Mermaid）、与 ABI/API 的关系辨析
- **Verification**: `human-judgment`

### AC-3: 工作原理覆盖完整
- **Given**: `02-working-principles.md` 文档
- **When**: 阅读文档
- **THEN**: 包含调用约定详解（含 Mermaid 图）、名称修饰、数据封送（4 种类型）、内存管理、绑定生成，每项配代码示例
- **Verification**: `human-judgment`

### AC-4: 语言实现覆盖 6 种
- **Given**: `03-language-implementations.md` 文档
- **When**: 阅读文档
- **THEN**: 覆盖 Python/Java/Go/Rust/Node.js/C# 共 6 种 FFI 实现，每种含实现机制 + 核心 API + 代码示例 + 适用场景
- **Verification**: `human-judgment`

### AC-5: 应用案例充分
- **Given**: `04-use-cases.md` 文档
- **When**: 阅读文档
- **THEN**: 包含 ≥3 个完整应用案例（含源码 + 调用示例 + 输出说明），≥5 条最佳实践
- **Verification**: `human-judgment`

### AC-6: 优势与局限性分析完整
- **Given**: `05-advantages-limitations.md` 文档
- **When**: 阅读文档
- **THEN**: 包含优势分析、局限性分析、性能开销分析（含基准数据）、安全性考量（含防护建议）
- **Verification**: `human-judgment`

### AC-7: 相关概念对比完整
- **Given**: `06-comparison.md` 文档
- **When**: 阅读文档
- **THEN**: 包含 FFI vs ABI/API/RPC/IPC/IDL 多维度对比表格、Mermaid 关系图、选型决策树、与项目内 wiki 的交叉引用
- **Verification**: `human-judgment`

### AC-8: 元数据规范
- **Given**: 所有 8 个文档
- **When**: 检查 frontmatter
- **THEN**: 每个文档包含完整 YAML frontmatter，`source` 字段值为 `spec:create-ffi-wiki-tutorial`，`category` 为 `learning`
- **Verification**: `programmatic`

### AC-9: 链接有效
- **Given**: 教程完成
- **When**: 运行链接检查
- **THEN**: 所有内部相对路径链接有效，无 `file:///` 绝对路径断链
- **Verification**: `programmatic`
- **Notes**: 运行 `python .agents/scripts/check-links.py --path docs/knowledge/learning/ffi-wiki/` 验证

### AC-10: 双向导航
- **Given**: 分章文档（01-06）
- **When**: 检查导航链接
- **THEN**: 每个文档包含上一章、返回目录、下一章的双向导航链接
- **Verification**: `human-judgment`

### AC-11: 参考资料完整
- **Given**: `07-resources.md` 文档
- **When**: 阅读文档
- **THEN**: 包含 ≥15 条术语表、权威参考资料链接、分难度扩展阅读建议、与项目内相关 wiki 的交叉引用
- **Verification**: `human-judgment`

## Open Questions
- [ ] 是否需要包含 C++ FFI 的专门讨论（如 `extern "C++"` 与 C++ 类的跨语言调用），还是主要聚焦 C ABI 作为通用中间层？
- [ ] 性能基准数据是否需要实测（如编写 benchmark 代码），还是引用权威来源的已有数据？
- [ ] 是否需要在 `04-use-cases.md` 中涵盖 WebAssembly 作为 FFI 特殊场景（WASM 与 JS 的互操作）？