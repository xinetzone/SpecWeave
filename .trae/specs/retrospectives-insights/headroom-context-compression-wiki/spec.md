# Headroom AI Agent上下文压缩中间件 - Product Requirement Document

## Overview
- **Summary**: 基于微信公众号文章《给AI Agent装个"压缩层"：1万token压到1千，质量不降反升》，系统学习Headroom开源项目——一个夹在AI Agent和LLM之间的上下文压缩中间层。本教程将涵盖项目架构、6种压缩算法、CCR可逆机制、4种接入方式、跨Agent记忆共享、自动学习教训等核心功能，形成完整的学习笔记与深度分析报告。
- **Purpose**: 系统性沉淀Headroom项目的核心技术原理、使用方法和设计思想，为AI Agent开发者提供上下文压缩领域的实用参考，帮助理解如何在不损失质量的前提下大幅降低Token消耗。
- **Target Users**: AI Agent开发者、Claude Code/Codex/Cursor等编程Agent深度用户、关注LLM成本优化的技术人员、对上下文工程(Context Engineering)感兴趣的研究者。

## Goals
- 完整提取并结构化Headroom项目的核心概念、技术架构和使用方法
- 深度分析CCR(Compress-Cache-Retrieve)可逆压缩机制的设计思想
- 提供详细的快速上手指南，覆盖4种接入方式
- 对比Headroom与同类压缩方案的差异和优势
- 萃取可复用的工程模式和设计洞察
- 按照项目规范生成原子化的Wiki教程，包含索引页和分章节原子文件

## Non-Goals (Out of Scope)
- 不进行Headroom源码的深度逐行分析
- 不提供Headroom的生产环境部署最佳实践（原文未涉及）
- 不进行Headroom与所有上下文压缩方案的全面横向评测
- 不修改或扩展Headroom项目本身的功能
- 不创建Headroom的集成Demo项目

## Background & Context
- **来源文章**: 微信公众号"逛逛GitHub"发布的Headroom项目介绍文章
- **开源地址**: https://github.com/chopratejas/headroom
- **行业背景**: Token成本仍是AI Coding的主要瓶颈和成本痛点，长任务、日志、grep结果等大量冗余信息消耗大量Token但有效信息密度低
- **同类问题**: 现有压缩方案多采用简单截断或小模型统一压缩，且压缩后不可逆，关键信息丢失后无法找回
- **项目规范遵循**: 遵循SpecWeave项目MDI v1.0规范，使用YAML frontmatter，采用原子化目录结构，文件命名使用kebab-case英文

## Functional Requirements
- **FR-1**: 生成Headroom项目概述章节，包含项目定位、核心价值、解决的痛点问题
- **FR-2**: 生成核心架构章节，详细说明Headroom在AI Agent与LLM之间的中间层定位和工作原理
- **FR-3**: 生成6种压缩算法详解章节，包括SmartCrusher(JSON压缩)、CodeCompressor(基于AST的代码压缩)、Kompress-v2-base(自然语言压缩)等
- **FR-4**: 生成CCR可逆机制深度解析章节，阐述压缩-缓存-检索的完整工作流设计
- **FR-5**: 生成4种接入方式详解章节（Library/Proxy/Agent Wrap/MCP Server），包含代码示例和配置步骤
- **FR-6**: 生成效果验证与数据章节，包含Token压缩率数据、质量评估数据、与同类工具对比
- **FR-7**: 生成进阶功能章节，涵盖跨Agent共享记忆、headroom learn自动学习教训功能
- **FR-8**: 生成快速上手指南章节，包含安装、配置、基础使用步骤
- **FR-9**: 生成FAQ章节，解答常见使用问题
- **FR-10**: 生成资源链接章节，包含原文、GitHub仓库、相关参考资料
- **FR-11**: 生成索引页(headroom-context-compression-wiki.md)作为入口，包含完整目录导航
- **FR-12**: 所有原子文件使用YAML frontmatter，包含id、title、source、x-toml-ref字段
- **FR-13**: 为所有原子文件创建对应的TOML元数据文件在.meta/toml/目录下

## Non-Functional Requirements
- **NFR-1**: 文档语言为标准现代汉语，逻辑清晰，通俗易懂，适合不同技术水平读者
- **NFR-2**: 所有技术信息准确，与原文内容一致，不添加原文未提及的虚假信息
- **NFR-3**: 章节结构清晰，导航完整，各章节间通过相对链接互联
- **NFR-4**: 遵循项目kebab-case文件命名规范，不使用中文文件名
- **NFR-5**: 遵循原子化拆分原则，每个文件聚焦单一主题，文件行数控制在合理范围
- **NFR-6**: 代码示例格式规范，使用正确的markdown代码块标记语言类型
- **NFR-7**: 关键数据和对比信息使用表格呈现，提升可读性

## Constraints
- **Technical**: Must follow existing project conventions (YAML frontmatter, atomic directory structure, TOML metadata files in .meta/toml/)
- **Business**: Must complete within this session, following Spec Mode workflow
- **Dependencies**: Relies on the already extracted web content; no additional web scraping needed beyond what's already fetched

## Assumptions
- 原文内容已完整提取，包含Headroom项目的所有核心信息
- 无需访问GitHub仓库进行源码验证，基于原文信息撰写即可
- 用户期望遵循项目现有Wiki教程的原子化格式（类似longcat-agent-learning-wiki、mopmonk-security-agent-wiki等）
- 文档将放置在docs/knowledge/learning/目录下

## Acceptance Criteria

### AC-1: 内容完整性
- **Given**: 已提取的微信公众号文章内容
- **When**: 完成所有Wiki文档生成
- **Then**: 文章中所有核心信息（6种算法、4种接法、CCR机制、效果数据、进阶功能）均被完整覆盖，无关键信息遗漏
- **Verification**: `human-judgment`
- **Notes**: 对照原文7个章节逐一核查覆盖度

### AC-2: 结构规范性
- **Given**: 项目现有Wiki格式规范
- **When**: 生成所有文档文件
- **Then**: 采用"索引页+原子目录"结构，每个原子文件有正确的YAML frontmatter，文件名使用kebab-case英文，导航链接正确
- **Verification**: `programmatic` + `human-judgment`
- **Notes**: 运行文件名规范检查脚本，人工检查frontmatter格式

### AC-3: 索引页导航完整性
- **Given**: 生成的索引页和原子文件
- **When**: 用户访问索引页
- **Then**: 索引页包含完整的目录表格，每个章节都有正确的相对链接，点击可跳转到对应原子文件
- **Verification**: `human-judgment`
- **Notes**: 检查每个导航链接的有效性

### AC-4: TOML元数据完整性
- **Given**: 生成的Markdown文件
- **When**: 检查元数据
- **Then**: 每个Markdown文件都有对应的TOML元数据文件，路径与x-toml-ref字段一致，元数据字段完整
- **Verification**: `programmatic`
- **Notes**: 验证x-toml-ref路径与实际TOML文件存在性一致

### AC-5: 知识库索引更新
- **Given**: 新生成的Wiki教程
- **When**: 完成文档编写
- **Then**: docs/knowledge/README.md中learning分类下新增Headroom Wiki条目，包含标题、摘要、日期、标签
- **Verification**: `human-judgment`
- **Notes**: 遵循现有README.md的表格格式

### AC-6: 语言表达质量
- **Given**: 生成的所有文档内容
- **When**: 人工审阅
- **Then**: 使用标准现代汉语，逻辑清晰，通俗易懂，无网络流行语，技术术语解释准确
- **Verification**: `human-judgment`
- **Notes**: 遵循用户规则中的语言要求

### AC-7: 深度分析质量
- **Given**: 学习笔记与分析内容
- **When**: 审阅核心分析章节
- **Then**: 不仅复述原文内容，还包含对Headroom设计思想的深度洞察、与上下文工程(Context Engineering)趋势的关联分析、可复用模式萃取
- **Verification**: `human-judgment`
- **Notes**: 体现"学习与洞察分析"的深度要求

## Open Questions
- [ ] 是否需要在本Wiki中补充与SpecWeave项目现有规范（如AGENTS.md、阶段守卫等）的关联分析？
- [ ] 深度洞察部分应侧重哪些方向（工程模式、行业趋势、技术选型等）？
