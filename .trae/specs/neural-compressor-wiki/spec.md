# Intel Neural Compressor Wiki 教程 - Product Requirement Document

## Overview
- **Summary**: 基于 Intel Neural Compressor 官方文档（<https://intel.github.io/neural-compressor/latest/docs/source/Welcome.html>）生成一份结构化的中文 wiki 教程，涵盖核心概念、安装指南、快速开始、主要量化技术、API 概览和最佳实践，采用与项目现有 wiki（如 ffi-wiki、graphql-wiki）一致的目录结构和文件命名规范。
- **Purpose**: 为项目开发者提供一份开箱即用的 Intel Neural Compressor 学习参考，降低模型压缩技术的入门门槛，沉淀可复用的 AI 模型优化知识。
- **Target Users**: 项目内需要使用模型量化/压缩技术的 AI 工程师、算法开发者、性能优化工程师。

## Goals
- 系统性梳理 Intel Neural Compressor 的核心功能与架构
- 提供清晰的安装指南与环境配置说明
- 包含可运行的快速开始示例（PyTorch 后端优先）
- 覆盖主流量化技术（静态量化、动态量化、权重量化、FP8 量化等）的使用方法
- 提供 API 概览与最佳实践
- 遵循项目知识库规范，自动生成索引与交叉引用
- 所有内容为中文，术语统一，适合国内开发者阅读

## Non-Goals (Out of Scope)
- 不覆盖 TensorFlow/JAX 后端的详细用法（仅做简要提及）
- 不深入讲解模型压缩的底层数学原理
- 不提供生产级部署的完整方案
- 不包含 Intel Gaudi HPU 的专用硬件配置细节（仅做概述）
- 不覆盖 AutoRound 等第三方集成库的高级用法

## Background & Context
- Intel Neural Compressor 是 Intel 开源的 Python 模型压缩库，支持 PyTorch、TensorFlow、JAX 等主流深度学习框架，提供静态量化、动态量化、SmoothQuant、仅权重量化、FP8 量化等多种压缩技术，广泛支持 Intel CPU/GPU/Gaudi 硬件。
- 项目已有多个技术 wiki 教程（如 ffi-wiki、graphql-wiki、tvm-ffi-wiki），统一存放在 `.agents/docs/knowledge/learning/` 目录下，采用标准化的文件结构和 frontmatter 规范。
- 现有项目中已有 ONNX 量化相关的实践经验（见项目 memory 中的 onnx-quantized 相关内容），本 wiki 可与之形成互补。

## Functional Requirements
- **FR-1**: 结构化文档组织，采用与现有 wiki 一致的目录结构（00-overview.md, 01-..., README.md 等）
- **FR-2**: 包含完整的 YAML frontmatter 元数据（标题、分类、标签、日期、摘要、source 来源）
- **FR-3**: 内容涵盖：概述与核心概念、安装指南、快速开始、主要量化技术详解、API 概览、最佳实践、常见问题、资源链接
- **FR-4**: 包含可运行的代码示例（基于 PyTorch 后端）
- **FR-5**: 术语统一，首次出现时提供解释
- **FR-6**: 所有交叉链接使用相对路径，符合项目文档规范
- **FR-7**: 生成后更新知识库索引

## Non-Functional Requirements
- **NFR-1**: 文档语言为中文，专业术语保留英文原文并附中文解释
- **NFR-2**: 每个单文件大小控制在 500-5000 字符，避免单文件过大
- **NFR-3**: 代码示例需有注释，说明每一步的作用
- **NFR-4**: 内容准确，来源于官方文档，不添加主观臆断的内容
- **NFR-5**: 遵循项目 markdown 编写规范（myst-parser 兼容）

## Constraints
- **Technical**: 必须遵循项目现有 wiki 的文件结构与命名规范；必须使用 myst-parser 兼容的 markdown 语法；所有文件存放在 `.agents/docs/knowledge/learning/neural-compressor-wiki/` 目录下
- **Business**: 内容基于公开的 Intel Neural Compressor 官方文档，遵守 Apache 2.0 许可证
- **Dependencies**: 依赖 defuddle 工具抓取网页内容；依赖项目的 docgen 脚本生成索引

## Assumptions
- 用户具备基础的深度学习和 PyTorch 使用经验
- 用户主要使用 CPU/GPU 环境，不强制要求 Gaudi HPU 硬件
- 官方文档内容准确可靠，以最新版本（3.9）为准

## Acceptance Criteria

### AC-1: 目录结构符合规范
- **Given**: 项目现有 wiki 目录结构（如 ffi-wiki）
- **When**: 完成 wiki 生成
- **Then**: 目录包含 00-overview.md、各章节文件、README.md，文件命名与现有 wiki 一致
- **Verification**: `programmatic`
- **Notes**: 检查文件是否存在，命名是否符合 `XX-<topic>.md` 格式

### AC-2: Frontmatter 完整合规
- **Given**: 项目知识库的 frontmatter 模板
- **When**: 检查所有 markdown 文件
- **Then**: 每个文件都包含 title、date、category、tags、summary、source 等必要字段
- **Verification**: `programmatic`

### AC-3: 核心内容章节齐全
- **Given**: PRD 中定义的内容范围
- **When**: 审阅文档内容
- **Then**: 涵盖概述、安装、快速开始、主要量化技术、API、最佳实践、FAQ、资源等章节
- **Verification**: `human-judgment`

### AC-4: 代码示例可运行（语法正确）
- **Given**: 文档中的 Python 代码示例
- **When**: 检查代码语法
- **Then**: 代码无语法错误，导入路径正确，步骤清晰
- **Verification**: `programmatic`
- **Notes**: 使用 Python 语法检查，不实际运行（避免硬件依赖）

### AC-5: 交叉链接有效
- **Given**: 文档中的内部链接
- **When**: 运行链接检查脚本
- **Then**: 无断链，所有相对路径正确
- **Verification**: `programmatic`

### AC-6: 内容准确无臆断
- **Given**: 官方文档原文
- **When**: 对比审阅内容
- **Then**: 核心信息与官方文档一致，无添加未经验证的内容
- **Verification**: `human-judgment`

### AC-7: 知识库索引更新
- **Given**: 新添加的 wiki 目录
- **When**: 运行索引生成脚本
- **Then**: 新 wiki 出现在分类索引中，可被检索到
- **Verification**: `programmatic`

## Open Questions
- [ ] 是否需要包含 TensorFlow/JAX 后端的示例？（当前 Non-Goals 中暂不覆盖，如需补充可后续迭代）
- [ ] 是否需要包含与项目现有 ONNX 量化流程的对比？
