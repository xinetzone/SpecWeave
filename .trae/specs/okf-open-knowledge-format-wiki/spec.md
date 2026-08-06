---
id: "okf-open-knowledge-format-wiki-spec"
title: "OKF开放知识格式Wiki教程产品需求文档"
source: "seven-concepts knowledge-scenario: okf.md + 知乎系列文章"
date: "2026-08-05"
tags: ["OKF", "Open Knowledge Format", "知识标准", "Agent知识层", "wiki教程"]
---

# OKF开放知识格式Wiki教程 - Product Requirement Document

## Overview
- **Summary**: 基于OKF官方规范（okf.md）、GitHub参考实现、以及3篇知乎深度分析文章，系统创建一份原子化的OKF（Open Knowledge Format）Wiki教程，全面覆盖OKF的设计理念、格式规范、快速上手、最佳实践、Agent集成、与相关标准对比等内容。教程采用8章节标准结构，输出到`.agents/docs/knowledge/learning/01-agent-protocols-interfaces/okf-wiki/`目录。
- **Purpose**: 帮助开发者、架构师、AI工程师快速掌握OKF开放知识格式，理解其作为Agent四层架构中"知识层"独立标准的核心价值，能够从零开始创建符合规范的Knowledge Bundle，并将其应用于企业知识管理、Agent系统构建等场景。
- **Target Users**: AI应用开发者、Agent系统架构师、数据/知识工程师、技术决策者、企业知识管理负责人。

## Goals
- 基于多源资料（官方spec、quickstart、知乎深度分析）整合形成结构化学习教程
- 清晰解释OKF的设计哲学、三大原则、与其他知识表示方案的区别
- 提供从0到1创建OKF Bundle的完整实操指南（含代码示例）
- 阐述OKF在Agent四层架构（模型/MCP/Skills/OKF）中的定位和价值
- 提供完整的术语表、FAQ、最佳实践和落地路径建议
- 包含版本说明（V0.1极早期阶段警示），避免过度承诺

## Non-Goals (Out of Scope)
- 不实现OKF验证器或任何工具链代码
- 不创建完整的生产级OKF Bundle示例（仅提供教学示例）
- 不深度对比所有RAG/向量数据库方案（仅做定位对比）
- 不覆盖OKF未来V1.0+可能新增的特性（仅基于V0.1现有规范）
- 不翻译整个okf.md官网（提炼整合+本地化解读+中文语境最佳实践）

## Background & Context
- OKF（Open Knowledge Format）是2026年6月Google Cloud发布的开放知识表示规范
- 定位为"AI时代的HTML"——极简、可Git管理、人和Agent共读的Markdown+YAML格式
- 核心是三个规则：index.md入口、typed frontmatter、Git-native历史
- 项目已有七概念方法论分析沉淀，形成了"四层Agent架构知识优先"模式
- 现有wiki目录结构中，`01-agent-protocols-interfaces/`是Agent协议/接口类wiki的归属地
- 参考示例：`agent-communication-protocols/`（12章原子化结构）作为格式参考

## Functional Requirements
- **FR-1**: 教程采用原子化wiki结构（目录+多个编号章节文件+README.md）
- **FR-2**: 包含8个核心章节（00-overview到07-resources），符合标准wiki模板
- **FR-3**: frontmatter遵循现有原子化wiki格式（id/title/source/x-toml-ref等字段）
- **FR-4**: 包含官方规范的完整解读（Bundle结构、Concept文件、frontmatter字段、链接规则）
- **FR-5**: 包含5分钟Quickstart完整实操教程（SaaS Metrics示例或更贴合中国开发者的示例）
- **FR-6**: 包含OKF三层设计哲学（Minimally opinionated / Producer-consumer independence / Format not platform）
- **FR-7**: 包含OKF在Agent四层架构中的定位分析，与MCP/Skills的关系
- **FR-8**: 包含与现有方案对比（Markdown无结构、Notion/Confluence、专有向量库RAG、知识图谱、Obsidian等）
- **FR-9**: 包含局限性分析（V0.1极早期警示、生态成熟度、Google历史产品风险、企业落地注意事项）
- **FR-10**: 包含渐进式落地路径建议（从小试点到全面推广的四阶段）
- **FR-11**: 包含完整术语表（Bundle/Concept/Frontmatter等核心术语定义）
- **FR-12**: 包含FAQ（8-12个常见问题及解答）
- **FR-13**: 包含所有来源引用（官网链接、GitHub、知乎文章）
- **FR-14**: 包含Mermaid架构图（OKF Bundle结构、Agent四层架构、知识生产消费流程）

## Non-Functional Requirements
- **NFR-1**: 所有内容使用标准现代汉语书面语，专业术语统一
- **NFR-2**: 章节粒度适中，单文件<300行（遵循原子化原则）
- **NFR-3**: 代码示例完整可运行（至少一个完整的Bundle示例）
- **NFR-4**: 风险提示明确（V0.1阶段警示放在overview和limitations章节显著位置）
- **NFR-5**: 交叉链接正确，文件间引用使用相对路径
- **NFR-6**: frontmatter字段与现有wiki保持一致，不添加额外无依据字段
- **NFR-7**: 三级标题使用x.y编号格式（1.1、2.3等，从x.1开始）

## Constraints
- **Technical**: 输出为纯Markdown文件+YAML frontmatter，无额外依赖
- **Business**: 基于现有公开资料，不虚构OKF未公开的特性
- **Dependencies**: 
  - 参考现有wiki格式：`volcengine-agentkit-wiki/`、`agent-communication-protocols/`
  - 资料来源：okf.md/spec、okf.md/quickstart、GitHub knowledge-catalog、3篇知乎文章
  - 输出路径：`d:\AI\.agents\docs\knowledge\learning\01-agent-protocols-interfaces\okf-wiki\`

## Assumptions
- 输出目录归类在`01-agent-protocols-interfaces/`下是合理的（OKF是Agent知识层的接口标准）
- 原子化wiki结构（而非单文件）更适合OKF这种内容较丰富、章节独立性高的主题
- 现有原子化wiki的frontmatter格式（含category/tags/date/status等字段）是当前标准
- 已有七概念分析的3条核心洞察可直接整合到对应章节

## Acceptance Criteria

### AC-1: Wiki目录结构完整
- **Given**: 教程创建完成
- **When**: 查看输出目录
- **Then**: 存在`okf-wiki/`目录，包含README.md和00-07共8个以上章节文件
- **Verification**: `programmatic`
- **Notes**: 验证文件存在和命名规范

### AC-2: Frontmatter格式合规
- **Given**: 每个章节文件
- **When**: 检查frontmatter
- **Then**: 包含id/title/source/x-toml-ref字段，格式与现有原子化wiki一致
- **Verification**: `programmatic`
- **Notes**: 参考volcengine-agentkit-wiki的frontmatter格式

### AC-3: 核心规范覆盖完整
- **Given**: 01-core-concepts.md章节
- **When**: 阅读内容
- **Then**: 覆盖Bundle结构、Concept文件、frontmatter必填/推荐字段、链接规则、index.md、log.md、Citations所有官方spec内容
- **Verification**: `human-judgment`

### AC-4: Quickstart可实操
- **Given**: 02-installation.md或03-usage.md章节
- **When**: 按步骤操作
- **Then**: 可以在5分钟内创建一个符合OKF v0.1规范的完整Bundle（含至少3个Concept、index.md、log.md）
- **Verification**: `human-judgment`
- **Notes**: 步骤清晰，代码块完整可复制

### AC-5: 设计哲学阐述清晰
- **Given**: 00-overview.md或01-core-concepts.md
- **When**: 阅读设计原则部分
- **Then**: 清晰阐述三大设计原则（Minimally opinionated / Producer-consumer independence / Format not platform），并解释其背后的权衡
- **Verification**: `human-judgment`

### AC-6: Agent架构定位准确
- **Given**: 相关章节
- **When**: 阅读架构分析
- **Then**: 清晰说明OKF作为Agent四层架构独立第四层（知识层）的定位，与模型层、MCP连接层、Skills程序层的关系
- **Verification**: `human-judgment`

### AC-7: 风险提示充分
- **Given**: 04-limitations.md章节
- **When**: 阅读局限性分析
- **Then**: 明确标注OKF处于V0.1极早期阶段（发布2个月）、生态成熟度风险、Google产品历史风险、企业落地注意事项
- **Verification**: `human-judgment`

### AC-8: 对比分析客观
- **Given**: 04-limitations.md或06-summary.md
- **When**: 阅读对比部分
- **Then**: 客观对比OKF与Obsidian/Notion/Confluence/专有RAG/知识图谱等方案的优缺点，给出适用场景
- **Verification**: `human-judgment`

### AC-9: 落地路径可执行
- **Given**: 相关章节
- **When**: 阅读落地建议
- **Then**: 提供渐进式四阶段落地路径（试点→单领域→Agent集成→治理），每阶段有明确动作
- **Verification**: `human-judgment`

### AC-10: FAQ与资源完整
- **Given**: 06-faq.md和07-resources.md
- **When**: 检查内容
- **Then**: FAQ包含8个以上常见问题；resources包含所有来源链接（官网、GitHub、知乎）以及相关wiki交叉引用
- **Verification**: `programmatic` + `human-judgment`

### AC-11: Mermaid图表正确
- **Given**: 包含Mermaid图表的章节
- **When**: 渲染Mermaid代码
- **Then**: 图表语法正确，可正常渲染，清晰表达OKF Bundle结构或Agent架构关系
- **Verification**: `human-judgment`

### AC-12: 交叉链接有效
- **Given**: 所有章节文件
- **When**: 检查markdown链接
- **Then**: 文件间相对链接路径正确，指向目标文件存在
- **Verification**: `programmatic`

## Open Questions
- [ ] 是否需要在02章节单独放安装（其实OKF零安装，可能合并到快速上手）
- [ ] Quickstart示例是沿用官网SaaS Metrics还是换一个更贴近AI Agent场景的示例？
- [ ] 是否需要单独增加一个"与SpecWeave知识库的关系"章节，说明OKF如何应用到本项目？
- [ ] GitHub上的GoogleCloudPlatform/knowledge-catalog具体内容在执行阶段获取并整合
