---
version: 1.0
change_id: create-scikit-build-core-wiki-tutorial
theme: standards-tools
status: pending
created: 2026-07-04
---

# scikit-build-core 全面 Wiki 教程创建 Spec

## Why

scikit-build-core 是现代 Python 包构建后端（PEP 517），基于 CMake，对需要编译 C/C++/Fortran 的 Python 包至关重要。项目知识库（`docs/knowledge/learning/`）目前已有 IDL Wiki、MyST 教程、Agent Skills Wiki 等系统性学习资料，但缺少 scikit-build-core 的全面教程。用户要求整合三方资源——`external/tools/scikit-build-core` 源码、readthedocs 官方文档、daobook pygallery 教程——创建一份从概念到进阶的完整 wiki，填补知识库在 Python 构建系统领域的空白。

## What Changes

- **克隆源码**：将 scikit-build-core 源码克隆到 `external/tools/scikit-build-core`（当前 `external/` 目录为空，需新建 `external/tools/` 目录层级）
- **创建 Wiki 目录**：在 `docs/knowledge/learning/scikit-build-core-wiki/` 下创建原子化教程文档
- **编写核心章节**：
  1. 概述与背景（scikit-build-core 是什么、为何存在、与 setuptools/distutils/flit/hatch 的关系）
  2. 基本概念与架构解析（PEP 517/660 构建后端、CMake 集成机制、wheel 构建流程）
  3. 项目目录结构及各模块功能说明（基于源码的 `src/scikit_build_core/` 模块树解析）
  4. 核心 API 使用方法与示例代码（`build`、`build_editable`、配置项、`pyproject.toml` 集成）
  5. 常见问题解决方案与最佳实践（跨平台编译、依赖管理、可编辑安装、CI 集成）
  6. 从入门到进阶的完整操作指南（最小示例 → 真实项目 → 高级配置）
- **导航枢纽**：编写 `00-overview.md` 作为入口，含目录导航表与阅读路径
- **索引同步**：更新 `docs/knowledge/README.md`（由 docgen 自动生成）

## Impact

- **新增源码**：`external/tools/scikit-build-core/`（GitHub 仓库镜像，参考 `external/` 历史存放 TuyaOpen/WSL/agentskills 的惯例）
- **新增文档**：`docs/knowledge/learning/scikit-build-core-wiki/*.md`（预计 8-10 个原子化文档）
- **修改文档**：`docs/knowledge/README.md`（索引自动生成，无需手动编辑）
- **不影响**：现有 `.agents/` 规范、`vendor/` 子模块、已发布的 spec 文档
- **关联知识**：可与现有 `interface-api-abi-protocol-wiki`（构建工具链 ABI 层）、`karpathy-llm-coding-guidelines`（Python 工程实践）形成交叉引用

## ADDED Requirements

### Requirement: scikit-build-core 全面 Wiki 教程

系统 SHALL 在 `docs/knowledge/learning/scikit-build-core-wiki/` 目录下提供一套原子化的 scikit-build-core 教程文档，整合源码研究、官方文档与教程资源三方内容。

#### Scenario: 源码克隆与目录建立

- **WHEN** `external/tools/scikit-build-core` 目录不存在
- **THEN** 系统从 GitHub 克隆 scikit-build-core 仓库到该路径
- **AND** 保留 `.git` 目录以便后续 `git log` 溯源（遵循 `external/TuyaOpen`、`external/WSL` 的既有惯例）

#### Scenario: 概述与背景章节

- **WHEN** 读者打开 `00-overview.md`
- **THEN** 文档 SHALL 说明 scikit-build-core 的定位、与 setuptools/distutils/scikit-build(旧版) 的关系、PEP 517 构建后端的角色
- **AND** 提供完整目录导航表，链接到所有章节

#### Scenario: 概念与架构章节

- **WHEN** 读者阅读架构章节
- **THEN** 文档 SHALL 解释 PEP 517/660、CMake 集成机制、wheel 构建流程、可编辑安装原理
- **AND** 包含至少一张 Mermaid 架构图（构建流程图或模块关系图）

#### Scenario: 项目目录结构章节

- **WHEN** 读者阅读目录结构章节
- **THEN** 文档 SHALL 基于 `external/tools/scikit-build-core` 实际源码，准确描述 `src/scikit_build_core/` 下的模块树（`build/`、`settings/`、`_compat/`、`program_search/` 等）
- **AND** 每个模块说明 SHALL 标注源码文件路径锚点（如 `#L行号`），便于追溯

#### Scenario: 核心 API 与示例章节

- **WHEN** 读者阅读 API 章节
- **THEN** 文档 SHALL 覆盖 `build`、`build_editable` 钩子、`pyproject.toml` 配置项（`[tool.scikit-build]` 全部字段）、CMakeLists.txt 集成示例
- **AND** 每个示例 SHALL 包含可复制的最小代码块

#### Scenario: 常见问题与最佳实践章节

- **WHEN** 读者遇到跨平台编译、依赖冲突、可编辑安装失败等问题
- **THEN** 文档 SHALL 提供问题诊断流程与解决方案
- **AND** 涵盖 CI 集成（GitHub Actions）、abi3 限定 wheel、交叉编译等进阶主题

#### Scenario: 入门到进阶操作指南

- **WHEN** 读者按指南操作
- **THEN** 文档 SHALL 提供三级递进路径：最小 CMake 项目 → 真实 C++ 扩展包 → 高级配置（自定义 CMake 选项、Ninja、缓存复用）
- **AND** 每级 SHALL 有可验证的验收标准

#### Scenario: 文档规范一致性

- **WHEN** 教程文档创建完成
- **THEN** 每个文档 SHALL 携带 YAML frontmatter（含 `source` 字段标注溯源，如 `source: "spec:create-scikit-build-core-wiki-tutorial"`）
- **AND** 文档间引用 SHALL 使用相对路径（禁止 `file:///` 绝对路径）
- **AND** 所有源码引用 SHALL 可追溯（标注文件路径与行号锚点）

#### Scenario: 索引与导航更新

- **WHEN** 所有 wiki 文档编写完成
- **THEN** 运行 docgen 工具更新 `docs/knowledge/README.md` 索引
- **AND** 运行链接检查工具确保无断链
