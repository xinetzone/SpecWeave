# xmtools 客户分发文档集 Spec

## Why

`xmtools`（XMNN NPU 推理工具包）目前缺少一个专门用于直接分发给客户的文档目录。客户拿到项目后，只能查阅偏技术/内部视角的 `README.md`、`DEPLOYMENT.md` 等，内容偏构建与运维，缺乏面向非技术背景客户的、简洁友好的使用说明、功能说明与 FAQ。需要创建 `distribution/` 分发目录，提供完整、最新、客户友好的 Markdown 文档集。

## What Changes

- 在 `d:\spaces\SpecWeave\external\chaos\xmtools\distribution/` 下创建客户分发文档目录
- 文档集包含：README 索引、产品介绍、功能说明、快速开始、使用指南、常见问题（FAQ）、版本说明
- 所有文档遵循公司技术文档标准格式（frontmatter：title/description/last_updated；简洁层级；表格与代码块）
- 语言简洁易懂，面向非技术背景客户，避免内部术语与构建细节
- 文档内容基于当前项目真实状态（wheel 1.2.1-dev0、运行时镜像 xmnn:1.2.1-alpha、REST API 服务）

## Impact

- Affected specs: 无既有 spec 依赖（新任务）
- Affected code: `external/chaos/xmtools/distribution/`（新增目录，无代码改动）
- 文档数据源：`README.md`、`.agents/docs/docker/DEPLOYMENT.md`、`docker/serve/`、`sdk/`、`pyproject.toml`

## ADDED Requirements

### Requirement: 客户分发目录结构

系统 SHALL 在 `xmtools/distribution/` 下创建标准化的客户分发文档目录，包含 README 索引与全套客户文档。

#### Scenario: 创建分发目录
- **WHEN** 用户访问 `xmtools/distribution/`
- **THEN** 目录包含 README.md 索引及以下文档：产品介绍、功能说明、快速开始、使用指南、常见问题、版本说明

### Requirement: 文档格式标准

每份文档 SHALL 遵循公司技术文档标准格式：包含 YAML frontmatter（`title`、`description`、`last_updated`），使用简洁的层级结构、表格与代码块，语言简洁易懂。

#### Scenario: 校验文档格式
- **WHEN** 检查任一分发文档
- **THEN** 文档包含合法 frontmatter 元数据，标题层级清晰，无内部构建细节（如 Nuitka/CMake/LLVM 版本等）

### Requirement: 客户友好内容

文档 SHALL 面向非技术背景客户，使用通俗语言解释 XMNN 的功能、使用方法与常见问题，避免内部技术术语与构建流程。

#### Scenario: 客户阅读文档
- **WHEN** 非技术背景客户阅读使用指南
- **THEN** 可理解 XMNN 是什么、能做什么、如何快速使用、遇到问题如何解决

### Requirement: 内容真实性与最新性

文档内容 SHALL 基于当前项目真实状态，版本号、命令、功能描述与项目实际一致。

#### Scenario: 校验内容一致性
- **WHEN** 核对文档中的版本号、命令、功能描述
- **THEN** 与项目实际状态（wheel 1.2.1-dev0、镜像 xmnn:1.2.1-alpha、REST API 端点）一致