# QuantDinger 开源AI量化交易平台学习与深度洞察分析 - Product Requirement Document

## Overview
- **Summary**: 对微信公众号文章《QuantDinger：开源的AI量化交易基础设施层》进行系统性学习与深度洞察分析，产出完整的Wiki学习教程和方法论洞察总结。教程涵盖项目概述、架构解析、核心功能详解、MCP Agent Gateway集成、安全模型设计、快速上手指南、关键技术洞察等内容。
- **Purpose**: 系统梳理QuantDinger这一"自托管AI量化交易基础设施"的技术架构与设计理念，重点分析其MCP协议集成、双轨策略开发模式、自托管安全模型等创新点，萃取可复用的工程方法论模式，为AI Agent在垂直行业（金融交易）的落地提供参考案例。
- **Target Users**: AI Agent开发者、量化交易从业者、MCP协议研究者、自托管开源项目爱好者、金融科技架构师。

## Goals
- 系统性提取并整理QuantDinger项目的全部核心信息，形成结构化学习笔记
- 深度解析Agent Gateway（MCP协议集成）的设计思路与实现价值
- 分析"自托管+默认安全"设计模式在金融类应用中的实践意义
- 萃取双轨策略开发模式（IndicatorStrategy/ScriptStrategy）的架构设计思想
- 形成可复用的工程方法论洞察，为类似垂直领域AI Agent平台建设提供参考
- 更新知识库索引，确保文档可被检索和复用

## Non-Goals (Out of Scope)
- 不进行QuantDinger项目的实际部署或二次开发
- 不提供量化交易策略建议或投资指导
- 不进行实盘交易相关的操作或测试
- 不深入分析具体交易算法或金融模型
- 不对项目前端（未开源部分）进行逆向工程或详细分析

## Background & Context
- QuantDinger是GitHub上的开源项目（github.com/brokermr810/quantdinger），Apache 2.0协议（后端）
- 项目定位为"开源的AI量化交易基础设施层"，采用Docker Compose一键部署
- 核心创新点在于通过MCP协议让AI编程助手（Cursor/Claude Code等）直接操作量化交易平台
- 安全设计采用"默认模拟盘、显式开启实盘"的双开关机制
- 项目作者brokermr810文档详尽，体现了成熟的开源项目工程实践
- 本项目是SpecWeave知识库中"AI Agent+垂直行业"类别的重要案例补充

## Functional Requirements
- **FR-1**: 提取文章完整内容，包括项目简介、安装方式、6大核心功能、UI展示、总结评价
- **FR-2**: 生成结构化Wiki教程，包含目录导航、核心概念解析、架构图解、功能详解
- **FR-3**: 重点章节深度解析MCP Agent Gateway的设计原理与调用流程
- **FR-4**: 分析安全模型（自托管、双开关实盘、审计日志）的设计考量
- **FR-5**: 对比IndicatorStrategy与ScriptStrategy双轨模式的适用场景
- **FR-6**: 萃取可复用的工程方法论模式（自托管安全、MCP垂直集成、双模式开发等）
- **FR-7**: 提供快速上手指南与常见问题解答
- **FR-8**: 整理相关资源链接与延伸阅读材料
- **FR-9**: 更新docs/knowledge/README.md知识库索引
- **FR-10**: 创建符合MDI v1.0规范的YAML frontmatter和外部TOML元数据文件

## Non-Functional Requirements
- **NFR-1**: Wiki教程语言通俗易懂，适合不同技术水平读者阅读
- **NFR-2**: 文档结构清晰，逻辑层次分明，目录导航完整
- **NFR-3**: 关键技术点配有架构分析和设计理念解读
- **NFR-4**: 洞察总结具有深度，超越原文内容进行方法论层面的提炼
- **NFR-5**: 所有引用信息准确，与原文内容保持一致
- **NFR-6**: 文件名遵循kebab-case纯英文命名规范
- **NFR-7**: Markdown格式符合项目规范，YAML frontmatter完整

## Constraints
- **Technical**: 基于微信公众号文章内容进行分析，不进行外部网络爬取（除必要的GitHub链接验证外）
- **Business**: 内容聚焦技术学习与方法论分析，不涉及投资建议或金融产品推荐
- **Dependencies**: 依赖defuddle内容提取结果、现有Wiki文档格式模板、MDI v1.0规范

## Assumptions
- 文章内容已完整提取，核心信息无遗漏
- 读者具备基本的Docker、Python和AI Agent概念基础
- MCP协议作为AI Agent工具调用标准已被读者基本了解
- 量化交易的基本概念（回测、实盘、指标、策略等）可被简要说明

## Acceptance Criteria

### AC-1: Wiki教程完整性
- **Given**: 文章内容已提取完成
- **When**: 生成Wiki学习教程
- **Then**: 教程包含目录导航、项目概述、安装指南、6大核心功能详解、MCP专题、安全模型、UI介绍、总结展望、FAQ、资源链接共10个以上章节
- **Verification**: `human-judgment`
- **Notes**: 章节结构参考现有learning目录下Wiki文档格式

### AC-2: MCP Agent Gateway深度解析
- **Given**: 文章中关于Agent Gateway的描述
- **When**: 编写MCP专题章节
- **Then**: 包含Gateway架构、调用流程、Token权限模型、审计机制、与Cursor/Claude Code集成方式等内容
- **Verification**: `human-judgment`

### AC-3: 方法论洞察萃取
- **Given**: 对项目整体架构和设计的分析
- **When**: 生成洞察总结
- **Then**: 至少萃取3个可复用模式（如自托管安全双开关、MCP垂直领域集成、研究→回测→实盘双模式迁移等）
- **Verification**: `human-judgment`

### AC-4: 文档格式合规
- **Given**: Wiki文档创建完成
- **When**: 检查文档格式
- **Then**: 使用YAML frontmatter（---包裹），包含id/title/source/date/tags/x-toml-ref字段，文件名kebab-case纯英文
- **Verification**: `programmatic`
- **Notes**: 通过文件名规范检查脚本验证

### AC-5: 知识库索引更新
- **Given**: Wiki文档创建完成
- **When**: 更新知识库索引
- **Then**: docs/knowledge/README.md的learning分类中新增QuantDinger Wiki条目
- **Verification**: `programmatic`

### AC-6: 洞察深度超越原文
- **Given**: 完整阅读并理解原文
- **When**: 编写洞察分析章节
- **Then**: 不仅复述原文内容，还包含对设计理念的解读、与同类项目对比、可复用模式提炼、实践启示等延伸分析
- **Verification**: `human-judgment`

## Open Questions
- [ ] 是否需要对QuantDinger GitHub仓库进行补充验证以获取更多技术细节？
- [ ] 洞察萃取的模式是否需要单独入库到docs/retrospective/patterns/目录？
- [ ] Wiki文档是否需要原子化为多个子文件（参考mopmonk和agent-skills的做法）？
