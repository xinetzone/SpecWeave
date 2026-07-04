# TVM FFI 完整 Wiki 教程 Spec

## Why
TVM FFI（Foreign Function Interface）是 Apache TVM 项目提供的跨语言 C++/Python 互操作框架，也是 SpecWeave 项目 vendor 子模块中的重要外部依赖。当前项目知识库中缺少对 TVM FFI 的系统性学习资料，需要基于源码深度阅读和官方文档研究，创建一份全面、系统的 wiki 教程。

## What Changes
- 在 `docs/knowledge/learning/` 下创建 `tvm-ffi-wiki/` 原子化教程目录
- 基于 `external/ffi/tvm-ffi/` 源码和 `https://tvm.apache.org/ffi/` 官方文档编写教程
- 教程覆盖：核心概念、架构设计、C++ API、Python 绑定、容器类型、反射系统、CUDA 支持、ORCJIT 扩展、编译构建、跨语言互操作、实战示例、FAQ 与最佳实践
- 包含入口导航文档（README.md）和独立的原子化章节文档
- 遵循项目文档规范：YAML frontmatter（含 `source` 溯源）、相对路径引用、双向导航

## Impact
- Affected specs: 无（新知识条目，不涉及现有 spec 修改）
- Affected code: 无（纯文档产出）
- Affected knowledge: 在 `docs/knowledge/learning/` 下新增 tvm-ffi-wiki/ 目录

## ADDED Requirements

### Requirement: TVM FFI Wiki 教程目录结构
系统 SHALL 在 `docs/knowledge/learning/tvm-ffi-wiki/` 下创建原子化的 wiki 教程，每章一个独立文件，包含入口导航文档。

#### Scenario: 目录结构完整
- **WHEN** 教程创建完成
- **THEN** 目录包含 README.md 导航入口 + 至少 10 个原子化章节文档
- **THEN** 每个文档包含 YAML frontmatter（`source: "spec:create-tvm-ffi-wiki-tutorial"`）

### Requirement: 教程内容覆盖核心领域
系统 SHALL 确保教程覆盖 TVM FFI 的所有核心概念和功能模块。

#### Scenario: 内容覆盖全面
- **WHEN** 开发者阅读教程
- **THEN** 应能了解：TVM FFI 定位与架构概览、C++ 核心 API（Any/Object/Function/Tensor）、容器类型（Array/Map/Dict/List/Tuple）、类型系统（DType/Enum/Optional）、反射与注册机制、序列化与序列化、Python 绑定机制、CUDA 支持（cubin launcher）、ORCJIT 扩展、编译构建流程、跨语言互操作最佳实践、常见问题与解决方案
- **THEN** 每个章节应包含代码示例（C++ 和 Python）

### Requirement: 源码溯源与文档引用
系统 SHALL 在教程中标注信息来源于源码的具体文件和行号，确保可验证性。

#### Scenario: 源码引用可追溯
- **WHEN** 教程描述某个 API 或功能
- **THEN** 应引用对应源码文件路径（如 `include/tvm/ffi/any.h`）
- **THEN** 应引用官方文档章节（如 `https://tvm.apache.org/ffi/concepts/any.html`）

### Requirement: 教程与现有知识体系关联
系统 SHALL 在教程中关联项目内已有的相关知识文档。

#### Scenario: 知识体系关联
- **WHEN** 教程涉及 ABI/FFI 概念
- **THEN** 应引用 `docs/knowledge/learning/interface-api-abi-protocol-wiki/` 中的 ABI 章节
- **WHEN** 教程涉及 IDL 概念
- **THEN** 应引用 `docs/knowledge/learning/idl-wiki/` 中的 IDL 教程