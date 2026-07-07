# Minitap官方文档完整Wiki教程 - Product Requirement Document

## Overview
- **Summary**: 系统学习并深度解析Minitap官方技术文档（minitest产品文档 + mobile-use SDK文档，共48个页面），创建一份结构清晰、内容全面的中文Wiki教程，涵盖核心概念、详细操作步骤、API参考、常见问题解答及最佳实践。
- **Purpose**: 为开发者提供一份完整的、基于官方文档的中文学习资源，降低miniTest AI QA平台和mobile-use SDK的学习门槛，确保信息准确反映原文档的技术要点和使用规范。
- **Target Users**: 移动端测试工程师、AI Agent开发者、移动应用开发团队、对AI驱动测试和移动自动化感兴趣的技术人员。

## Goals
- 完整提取并系统梳理minitest官方文档（21个页面）的全部技术内容
- 完整提取并系统梳理mobile-use SDK官方文档（27个页面）的全部技术内容
- 创建原子化的Wiki教程结构，包含总览页和分章节子页面
- 准确翻译技术术语，保持中文技术文档的专业性和可读性
- 涵盖核心概念、快速开始、详细操作指南、API/CLI参考、集成指南、故障排除、最佳实践
- 确保所有技术细节与官方文档一致，不添加未经证实的内容
- 提供交叉引用和相关资源链接，方便深入学习

## Non-Goals (Out of Scope)
- 不包含Minitap官网营销页面内容（已有minitap-official-wiki.md覆盖）
- 不进行技术架构的深度二次分析或学术研究
- 不开发与Minitap相关的代码或工具
- 不包含博客文章、新闻报道、融资信息等非技术文档内容
- 不创建英文版本（仅中文）

## Background & Context
- Minitap是AI驱动的移动端测试平台，核心产品minitest是自主AI QA工程师
- mobile-use是Minitap开源的移动端自动化SDK，基于LangGraph和LLM Agent
- 官方文档站点：https://www.minitap.ai/docs/minitest 和 https://www.minitap.ai/docs/mobile-use-sdk/introduction
- 文档索引文件：https://www.minitap.ai/docs/llms.txt（包含48个页面链接）
- 项目已有基于营销内容的wiki，但缺少基于官方技术文档的系统教程
- Learning Wiki目录采用原子化结构：总览页 + 子目录分章节存储

## Functional Requirements
- **FR-1**: 使用defuddle工具批量提取全部48个官方文档页面的内容
- **FR-2**: 对提取内容进行结构化整理，分为minitest和mobile-use两大模块
- **FR-3**: 创建Wiki总览页（minitest-mobile-use-official-docs-wiki.md）作为入口
- **FR-4**: 创建minitest子目录，包含以下章节：
  - 入门指南（Meet Mini、Quickstart）
  - 测试套件管理（Anatomy、Authoring、Mini Maintains Suite）
  - 测试运行（Builds、Triggering Runs、Run Reports）
  - 问题分类（Issues Triage、Suggestions）
  - 集成（Cursor/Claude、GitHub、Slack）
  - 参考文档（Capabilities、CLI Commands、Glossary、MCP Tools、Mini Commands、GitHub Action）
- **FR-5**: 创建mobile-use-sdk子目录，包含以下章节：
  - 介绍与安装
  - 快速开始（Local Quickstart、Platform Quickstart、Cloud Quickstart、BrowserStack Quickstart、Physical iOS）
  - 核心概念（Architecture Overview、Agent、Builders、Observability、Profiles、Tasks）
  - 使用示例（Photo Organizer、Notification Assistant、App Lock Messaging、Platform Task、Video Recording）
  - SDK参考（Agent Class、AgentConfigBuilder、TaskRequestBuilder、Types、Exceptions）
  - 故障排除与反馈
- **FR-6**: 每个章节准确翻译技术术语，保留代码示例、命令示例的原始格式
- **FR-7**: 添加常见问题（FAQ）章节，汇总两个产品的常见问题
- **FR-8**: 添加最佳实践章节，从官方文档中提取最佳实践建议
- **FR-9**: 添加术语表，统一技术术语翻译
- **FR-10**: 添加资源链接章节，链接到官方文档、GitHub仓库等

## Non-Functional Requirements
- **NFR-1**: 文档准确性：所有技术细节必须与官方文档一致，不得臆造或篡改
- **NFR-2**: 结构清晰：遵循现有Learning Wiki的原子化结构，每个文件职责单一
- **NFR-3**: 中文表达：使用规范的技术中文，术语统一，语句通顺
- **NFR-4**: 可追溯性：每个章节注明来源URL
- **NFR-5**: 格式规范：使用标准Markdown格式，frontmatter符合项目规范
- **NFR-6**: 链接有效：内部交叉引用链接正确，外部链接可访问

## Constraints
- **Technical**: Markdown格式，中文技术文档，原子化文件结构
- **Business**: 仅基于官方文档内容，不添加外部信息
- **Dependencies**: defuddle CLI工具用于内容提取

## Assumptions
- 所有48个官方文档页面均可通过公开URL访问
- defuddle工具能够正确提取文档页面的主要内容
- 现有Learning Wiki目录结构可作为参考模板
- 项目已有的同类Wiki（如ffi-wiki、idl-wiki）可作为格式参考

## Acceptance Criteria

### AC-1: 文档内容完整性
- **Given**: 官方文档站点可访问
- **When**: 完成Wiki创建
- **Then**: 覆盖minitest全部21个页面和mobile-use-sdk全部27个页面的核心技术内容
- **Verification**: `programmatic`
- **Notes**: 通过检查每个官方文档页面是否在Wiki中有对应内容来验证

### AC-2: 结构符合项目规范
- **Given**: 现有Learning Wiki目录结构
- **When**: 完成Wiki创建
- **Then**: 文件组织结构、frontmatter格式、命名规范与现有同类Wiki一致
- **Verification**: `human-judgment`
- **Notes**: 参考ffi-wiki、idl-wiki等已完成的Wiki结构

### AC-3: 技术内容准确性
- **Given**: 官方文档原文
- **When**: 审阅Wiki内容
- **Then**: 技术概念、API签名、命令参数、代码示例与官方文档一致
- **Verification**: `human-judgment`

### AC-4: 中文表达质量
- **Given**: Wiki内容
- **When**: 审阅中文表达
- **Then**: 术语翻译准确统一，语句通顺，符合中文技术文档规范
- **Verification**: `human-judgment`

### AC-5: 核心模块完整性
- **Given**: Wiki总览和子页面
- **When**: 检查章节完整性
- **Then**: 包含核心概念、操作步骤、API/CLI参考、集成指南、FAQ、最佳实践、术语表
- **Verification**: `programmatic`

### AC-6: 链接有效性
- **Given**: Wiki中的所有链接
- **When**: 验证链接
- **Then**: 内部交叉引用正确，外部官方文档链接准确
- **Verification**: `programmatic`

## Open Questions
- 无
