---
name: book-to-skill-wiki-spec
version: 1.0.0
created: 2026-08-03
source: book-to-skill v1.3.0 codebase analysis
methodology: seven-concepts R→I→E→V
---

# book-to-skill Wiki 教程 - 产品需求文档

## Overview
- **Summary**: 为 book-to-skill（书籍转Agent Skill工具）生成完整的结构化wiki教程，涵盖架构设计、核心原理、安装使用、扩展开发、安全设计和可复用模式。
- **Purpose**: 帮助SpecWeave开发者理解book-to-skill的设计哲学和实现机制，提取可复用的工程模式（编译时付费、规范驱动生成、文档供应链安全）。
- **Target Users**: SpecWeave开发者、Agent工具构建者、对知识工程感兴趣的工程师。

## Goals
- 系统梳理book-to-skill的双层架构（Python提取器 + SKILL.md生成规范）
- 解释"编译时付费vs运行时付费"的核心架构决策和token经济学
- 提供从安装到高级用法的完整操作指南
- 提炼文档→Agent供应链安全的分层防御模式
- 提取可迁移到SpecWeave的工程模式

## Non-Goals (Out of Scope)
- 不逐行解释所有Python代码实现
- 不提供逐章转换书籍的操作手册（SKILL.md本身已提供）
- 不做与RAG系统的深度技术对比（只说明核心差异）
- 不覆盖Calibre等外部依赖的安装细节

## Background & Context
- book-to-skill v1.3.0 是一个开源工具，位于 `external/libs/book-to-skill/`
- 遵循Agent Skills开放标准，兼容GitHub Copilot CLI、Amp、Claude Code
- 核心创新在于SKILL.md作为可执行生成规范，而非硬编码逻辑
- Discovery Loop Tax测量显示相比上下文dump节省24×-51× tokens
- 包含多层文档安全防护，是处理不可信文档的参考实现

## Functional Requirements
- **FR-1**: 提供00-overview.md总览章节
- **FR-2**: 提供01-core-architecture.md架构解析章节
- **FR-3**: 提供02-extractor-deep-dive.md提取器深度解析章节
- **FR-4**: 提供03-skill-md-spec.md SKILL.md生成规范章节
- **FR-5**: 提供04-token-economics.md token经济学与性能章节
- **FR-6**: 提供05-security-model.md安全模型章节
- **FR-7**: 提供06-installation-usage.md安装与使用章节
- **FR-8**: 提供07-extending-development.md扩展开发章节
- **FR-9**: 提供08-transferable-patterns.md可复用模式章节
- **FR-10**: 提供09-summary-faq.md总结与FAQ章节

## Non-Functional Requirements
- **NFR-1**: 所有章节为中文，技术术语保留英文并附中文解释
- **NFR-2**: 每个章节聚焦单一主题，文件大小控制在合理范围
- **NFR-3**: 代码引用使用file:///绝对路径链接
- **NFR-4**: 可复用模式章节必须包含"适用于"、"不适用于"、"核心步骤"、"反模式"
- **NFR-5**: 事实引用必须可追溯到R阶段事实编号（F-xxx）

## Constraints
- **Technical**: 基于book-to-skill v1.3.0代码分析，不添加未在代码中验证的内容
- **Business**: 输出为Markdown格式，符合SpecWeave docs/knowledge/learning/目录约定
- **Dependencies**: 遵循现有wiki教程的章节编号和命名风格

## Assumptions
- 读者具备基本Python和CLI使用能力
- 读者了解Agent Skill基本概念
- 不需要逐字翻译README，而是提炼和重构知识结构

## Acceptance Criteria

### AC-1: Wiki结构完整
- **Given**: wiki目录已创建
- **When**: 检查文件列表
- **Then**: 包含00-09共10个章节文件，命名符合xxx-slug.md格式
- **Verification**: `programmatic`

### AC-2: 架构解析准确
- **Given**: 01-core-architecture.md
- **When**: 对照代码base阅读
- **Then**: 双层架构描述（Python提取器+SKILL.md规范）与实际代码结构一致
- **Verification**: `human-judgment`

### AC-3: 可复用模式可迁移
- **Given**: 08-transferable-patterns.md
- **When**: 应用到SpecWeave其他模块设计
- **Then**: 至少3个模式（编译时付费、规范驱动生成、文档安全分层）可直接迁移
- **Verification**: `human-judgment`

### AC-4: 代码引用可追溯
- **Given**: 所有章节
- **When**: 点击代码引用链接
- **Then**: 链接指向正确的文件和行范围
- **Verification**: `programmatic`

### AC-5: 安全模型完整
- **Given**: 05-security-model.md
- **When**: 对照sanitize.py、docx.py、scan_generated_skill.py
- **Then**: 覆盖5层安全防护（Unicode清理、XXE防护、路径防注入、生成扫描、CI）
- **Verification**: `programmatic`

## Open Questions
- 无
