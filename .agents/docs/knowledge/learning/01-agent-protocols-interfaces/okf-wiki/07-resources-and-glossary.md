---
id: "okf-wiki-resources-glossary"
title: "07 资源与术语表"
version: "1.0"
source: "okf.md官方资源 + 本项目wiki交叉引用"
type: "Wiki Tutorial"
description: "OKF核心术语表、官方资源链接、相关标准、本项目相关wiki交叉引用"
tags: ["OKF", "术语表", "资源链接", "Glossary", "References"]
category: "learning"
date: "2026-08-05"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "20+核心术语定义，完整的官方资源链接、相关标准链接、本项目内相关wiki交叉引用索引"
last_verified: "2026-08-05"
wiki_version: "1.0"
okf_version_target: "v0.2"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/knowledge/learning/01-agent-protocols-interfaces/okf-wiki/07-resources-and-glossary.toml"
---

# 07 资源与术语表

## 7.1 核心术语表（Glossary）

| 术语 | 中文 | 定义 |
|------|------|------|
| Body | 正文 | Concept文件中frontmatter之后的markdown内容部分 |
| Bundle | 知识包 | 自包含的知识文档集合，OKF的分发单元，一个目录树 |
| Bundle-Root-Relative Link | Bundle绝对链接 | 以`/`开头的链接，相对于Bundle根目录解析，移动文件时不失效 |
| Citation | 引用 | 指向外部来源的链接，用于支撑正文中的主张，帮助追溯信息来源 |
| Concept | 概念 | Bundle中一个知识单元，对应一个markdown文件，可以是实体资产或抽象概念 |
| Concept ID | 概念ID | Concept在Bundle内的文件相对路径（去掉.md后缀），如`tables/users` |
| Consumer Agent | 消费端Agent | 读取和使用OKF知识的AI Agent或工具 |
| Cross-Link | 交叉链接 | Concept之间的markdown链接，表示概念间关系 |
| Diffable | 可差分 | 纯文本格式支持版本控制系统的diff/merge，这是OKF选择Markdown的关键原因 |
| Enrichment Agent | 增强Agent | 自动生成/补充OKF知识的AI Agent |
| Frontmatter | 前置元数据 | 文件开头用`---`分隔的YAML元数据块 |
| Git-Native | Git原生 | 格式天然适合Git版本控制，支持分支、PR、diff、blame等Git工作流 |
| Index File | 索引文件 | 即index.md，目录内容列表，用于渐进式披露，无frontmatter |
| Knowledge Graph | 知识图谱 | 由Concepts和它们之间的Links组成的可导航知识网络 |
| Lifecycle Field | 生命周期字段 | v0.2新增元数据字段（status、stale_after等），标记知识生命周期状态 |
| Log File | 日志文件 | 即log.md，高层变更历史记录，按ISO日期倒序排列 |
| Markdown Body | 同Body | 见Body |
| Minimally Opinionated | 最少约定 | OKF核心设计原则：只强制最少规则（type字段），最大化采用面 |
| Non-Goals | 非目标 | OKF明确不做的事情，避免范围蔓延 |
| Portable | 可移植 | 不绑定任何平台/厂商/工具，知识可以自由迁移 |
| Producer/Consumer Independence | 生产者消费者解耦 | 知识写入方和读取方彻底分离，可独立替换 |
| Provenance | 来源元数据 | v0.2新增字段（sources、generated、verified），追踪知识来源和可信度 |
| Reserved Filename | 保留文件名 | index.md和log.md，任何目录层级都有特殊含义，不能用作Concept文件名 |
| SemVer | 语义化版本 | MAJOR.MINOR.PATCH版本号规范，用于Bundle版本管理 |
| Trust Level | 信任层级 | 由generated/verified元数据推导：unverified/machine-confirmed/human-reviewed |
| Type | 类型 | OKF唯一个强制frontmatter字段，标识Concept的类别，用于路由和过滤 |
| Typed Frontmatter | 带类型元数据 | 带type字段的YAML frontmatter，Agent无需启发式算法即可路由处理 |
| Validator | 验证器 | 官方在线工具（https://okf.md/validator），检查Bundle是否符合OKF规范 |
| YAML Frontmatter | 同Frontmatter | 见Frontmatter |

## 7.2 官方资源链接

**核心资源：**
- [OKF官网](https://okf.md/) - 项目首页
- [OKF规范完整版](https://okf.md/spec) - v0.2带注释规范
- [5分钟快速入门](https://okf.md/quickstart) - 官方Quickstart教程
- [在线验证器](https://okf.md/validator) - 浏览器中直接验证Bundle合规性（零安装）
- [Agent Skill安装](https://okf.md/skill) - 让Claude/Codex/Cursor生成合规OKF的Skill
- [GitHub参考实现](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf) - Google CloudPlatform官方仓库

## 7.3 相关标准与格式

- [Markdown](https://daringfireball.net/projects/markdown/) - OKF正文格式基础
- [YAML](https://yaml.org/) - OKF frontmatter格式基础
- [OpenAPI](https://www.openapis.org/) - API规范（互补，OKF补充业务上下文）
- [Protocol Buffers](https://protobuf.dev/) - 数据序列化Schema（互补）
- [JSON Schema](https://json-schema.org/) - JSON结构验证（OKF选择不强制Schema）
- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) - Agent工具连接协议（互补，MCP连接工具，OKF文档化工具知识）
- [RDF/OWL](https://www.w3.org/RDF/) - 语义网知识表示（更严格更复杂，不同定位）
- [Obsidian](https://obsidian.md/) - 个人知识管理工具（理念相似，定位不同）
- [dbt Docs](https://docs.getdbt.com/docs/collaborate/build-and-view-your-docs) - 数据文档自动生成（互补）

## 7.4 知乎深度分析文章

- 《AI 时代的"HTML 时刻"：一个被严重低估的知识标准 OKF》- 贾克斯的平行世界
  - https://zhuanlan.zhihu.com/p/2067345601977640539
- 《OKF 深度解析：为什么开放知识格式是Agent生态的关键基础设施》
  - https://zhuanlan.zhihu.com/p/2051665837967380596
- 《从 Markdown 到知识图谱：OKF 的设计哲学与实践路径》
  - https://zhuanlan.zhihu.com/p/2050505404975788824

## 7.5 本项目相关Wiki交叉引用

| Wiki | 路径 | 关联说明 |
|------|------|---------|
| Knowledge Catalog工具链 | [knowledge-catalog-wiki](../knowledge-catalog-wiki/README.md) | Google Cloud官方OKF参考实现、参考Agent、可视化工具、enrichment/mdcode工具箱 |
| Agent Skills Wiki | [agent-skills-wiki](../agent-skills-wiki/README.md) | Skills是程序层，OKF是知识层，互补 |
| Agent通信协议 | [agent-communication-protocols](../agent-communication-protocols/README.md) | MCP/A2A/ACP等Agent协议，OKF与MCP互补 |
| Harness七组件 | [harness-seven-components-wiki](../../02-agent-engineering-methodology/harness-seven-components-wiki/README.md) | Harness中的Knowledge Base组件与OKF定位 |
| 七概念方法论 | [seven-concepts-prompt-wiki](../../02-agent-engineering-methodology/seven-concepts-prompt-wiki/README.md) | 本教程使用七概念方法论知识沉淀场景产出 |
| 接口/API/ABI/Protocol概念辨析 | [interface-api-abi-protocol-wiki](../interface-api-abi-protocol-wiki/README.md) | OKF本质是知识层的接口标准 |

## 7.6 延伸阅读建议

1. 如果你是开发者：读完本教程后，直接动手做一个小Bundle（5分钟Quickstart）
2. 如果你是架构师：重点阅读04-05章，思考OKF在你现有架构中的定位
3. 如果你关心知识管理：可以对比Obsidian/Notion，理解开放格式 vs 平台锁定的权衡
4. 关注生态发展：OKF目前极早期，建议每3-6个月复查一次生态成熟度

---

OKF代表了一个重要方向：知识应该像HTML一样开放、可互操作、不被平台锁定。但方向正确不代表现在就该All-in——保持关注、小范围试点、积累经验，是这个阶段最理性的策略。

> "完美的标准不是没有东西可以加，而是没有东西可以去掉。" —— 圣埃克苏佩里（OKF极简设计哲学的最好注脚）

---

| 上一章 | 目录 | 下一章 |
|--------|------|--------|
| [06 FAQ与最佳实践](./06-faq-and-best-practices.md) | [README](./README.md) | （已完成，是最后一章） |
