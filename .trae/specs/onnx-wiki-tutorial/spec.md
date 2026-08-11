---
id: onnx-wiki-tutorial-spec
title: ONNX Wiki教程生成 - PRD
date: 2026-08-09
source:
  - https://onnx.ai/onnx/index.html
  - https://onnx.ai/get-started.html
  - https://onnx.ai/onnx/intro/index.html
  - https://onnx.ai/onnx/intro/concepts.html
  - https://onnx.ai/onnx/intro/python.html
category: spec
maturity: L1-draft
---

# ONNX Wiki教程 - Product Requirement Document

## Overview
- **Summary**: 基于ONNX官方文档，使用七概念方法论（R→I→E→V→C知识沉淀链路）系统性学习ONNX（Open Neural Network Exchange）开放神经网络交换格式，生成一套结构化、面向工程师的实用Wiki教程。
- **Purpose**: 解决ONNX官方文档分散、缺乏中文实战指导、新手入门曲线陡峭的问题，提供从核心概念到Python API实践的完整入门路径。
- **Target Users**: 深度学习工程师、推理优化工程师、需要部署模型到生产环境的AI开发者。

## Goals
- 系统性梳理ONNX核心概念（计算图、算子、张量类型、opset版本等）
- 提供可运行的Python API入门示例（线性回归从0构建到序列化）
- 提炼ONNX模型部署的最佳实践和常见陷阱
- 遵循项目Wiki规范（00-overview/01-core-concepts等原子化结构）
- 文档包含完整frontmatter元数据和交叉引用

## Non-Goals (Out of Scope)
- 不做官方文档的完整翻译
- 不覆盖所有ONNX算子（仅覆盖核心概念和常用算子）
- 不深入ONNX Runtime推理引擎优化（那是另一个主题）
- 不包含特定框架（PyTorch/TensorFlow）的导出教程细节
- 不做量化/剪枝等高级优化主题（项目已有onnx-quantized变体覆盖）

## Background & Context
- ONNX是机器学习模型的开放标准格式，实现框架互操作性
- 项目devcontainer-base已有onnx-pytorch和onnx-quantized变体
- 知识库已有protobuf-wiki等类似格式的Wiki教程作为参考
- Neural Compressor 3.x已弃用ONNX适配层，ONNX量化使用onnxruntime原生API
- 用户偏好中文文档、Markdown格式、myst-parser

## Functional Requirements
- **FR-1**: 创建onnx-wiki目录，遵循项目Wiki原子化结构
- **FR-2**: 00-overview.md：总览、TL;DR快速结论、阅读路径、速查表
- **FR-3**: 01-core-concepts.md：核心概念详解（计算图、Input/Output/Node/Initializer/Attributes、Protobuf序列化、算子域、张量类型、opset版本、子图/控制流、扩展性、函数、形状推断、工具链）
- **FR-4**: 02-python-api.md：Python API实战（线性回归示例、序列化/反序列化、Checker与形状推断、参考运行时）
- **FR-5**: 03-quickstart.md：快速上手指南（安装、模型导出/加载、可视化、常见问题）
- **FR-6**: 04-best-practices.md：最佳实践与常见陷阱（版本兼容性、类型转换、opset选择、子图避坑）
- **FR-7**: 05-faq-and-resources.md：FAQ、资源链接、术语表
- **FR-8**: README.md：Wiki入口与导航

## Non-Functional Requirements
- **NFR-1**: 所有文档使用中文撰写，技术术语保留英文
- **NFR-2**: 代码示例可直接运行（基于onnx 1.23.0/opset 28）
- **NFR-3**: 每个文件控制在500-5000字符，保持原子化
- **NFR-4**: 遵循项目文档规范（YAML frontmatter、相对路径引用、无file://绝对路径）
- **NFR-5**: 包含至少3个反模式/常见陷阱（E阶段G3质量门要求）

## Constraints
- **Technical**: 必须基于官方文档内容，不得编造API；遵循已有Wiki格式（参考protobuf-wiki）
- **Business**: 产出物存放于`.agents/docs/knowledge/learning/`下合适的分类目录
- **Dependencies**: 依赖defuddle已获取的官方文档内容、项目已有Wiki模板结构

## Assumptions
- ONNX 1.23.0/opset 28为当前稳定版本
- 用户已有Python和numpy基础
- 读者了解基本的机器学习概念（线性回归、张量、矩阵乘法）

## Acceptance Criteria

### AC-1: Wiki目录结构完整
- **Given**: Wiki生成任务执行完成
- **When**: 检查目标目录
- **Then**: 包含00-overview.md、01-core-concepts.md、02-python-api.md、03-quickstart.md、04-best-practices.md、05-faq-and-resources.md、README.md共7个文件
- **Verification**: `programmatic`
- **Notes**: 每个文件有完整YAML frontmatter

### AC-2: 核心概念覆盖完整
- **Given**: 阅读01-core-concepts.md
- **When**: 检查内容覆盖
- **Then**: 必须包含计算图、5大核心组件（Input/Output/Node/Initializer/Attributes）、Protobuf序列化、算子域（ai.onnx/ai.onnx.ml）、张量类型、opset版本机制、控制流（If/Scan/Loop）、扩展性、Functions、形状推断、工具链（Netron）共11个主题
- **Verification**: `programmatic`

### AC-3: Python示例可运行
- **Given**: 提取02-python-api.md中的代码
- **When**: 使用onnx 1.23.0执行线性回归示例
- **Then**: 代码无语法错误，check_model()通过，模型可序列化/反序列化
- **Verification**: `programmatic`

### AC-4: 最佳实践包含反模式
- **Given**: 阅读04-best-practices.md
- **When**: 检查反模式/陷阱数量
- **Then**: 至少包含3个来自官方文档的反模式或常见陷阱
- **Verification**: `human-judgment`

### AC-5: 文档格式符合规范
- **Given**: 所有生成的文档
- **When**: 检查格式
- **Then**: 相对路径引用正确、无file://绝对路径、frontmatter字段完整、中文表述通顺
- **Verification**: `human-judgment`

### AC-6: 质量门全部通过
- **Given**: 七概念方法论执行完成
- **When**: 检查G1-G3质量门
- **Then**: G1事实无因果词、G2洞察四元组完整、G3模式可迁移（含触发条件、步骤、反模式）
- **Verification**: `programmatic`

## Open Questions
- [ ] Wiki应该放在learning下哪个分类目录？（建议新建06-ai-ml-inference分类）
- [ ] 是否需要包含与项目onnx-quantized变体的交叉引用？
