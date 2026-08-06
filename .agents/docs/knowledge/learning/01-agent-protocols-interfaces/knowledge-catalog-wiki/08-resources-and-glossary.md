---
id: "knowledge-catalog-wiki-resources-glossary"
title: "08 资源与术语表"
version: "1.0"
source: "GoogleCloudPlatform/knowledge-catalog官方资源 + okf-wiki交叉引用 + 本项目wiki"
type: "Wiki Tutorial"
description: "Knowledge Catalog核心术语表、官方资源链接、OKF SPEC文档链接、示例Bundle链接、项目内wiki交叉引用索引、学习建议"
tags: ["Knowledge Catalog", "OKF", "术语表", "资源链接", "Glossary", "References", "Dataplex", "工具链"]
category: "learning"
date: "2026-08-06"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "30+核心术语定义（覆盖Knowledge Catalog、OKF、参考Agent、工具链）、完整官方资源链接、项目内wiki交叉引用索引、学习路径建议"
last_verified: "2026-08-06"
wiki_version: "1.0"
kc_version_target: "preview"
okf_version_target: "v0.2"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/knowledge/learning/01-agent-protocols-interfaces/knowledge-catalog-wiki/08-resources-and-glossary.toml"
---

# 08 资源与术语表

## 8.1 核心术语表（Glossary）

### 8.1.1 Knowledge Catalog平台相关术语

| 术语 | 中文 | 定义 |
|------|------|------|
| Actor约定 | 参与者约定 | 标识知识生产者/验证者身份的命名规范，Agent用`<producer>/<version>`，人类用`human:<id>`，流程用`process:<id>` |
| Attested Computation | 认证计算 | 一种特殊Concept类型，不仅承载值的含义，还承载值的受认可计算方式，使消费者能确认Agent按规定运行而非编造结果 |
| BQ Pass | BigQuery阶段 | 参考Agent工作流第一阶段，仅使用BigQuery元数据为每个数据资产生成初始OKF Concept文档 |
| Bundle | 知识包 | 自包含的知识文档层次集合，是OKF分发和版本控制的基本单元，物理形态为一个Markdown文件目录树 |
| Concept | 概念文档 | Bundle内的一个知识单元，对应一个UTF-8编码的Markdown文件，可以描述有形资产或抽象概念 |
| Concept ID | 概念ID | Concept文件在Bundle内的相对路径（去掉`.md`后缀），是概念的稳定标识符，如`tables/users` |
| Cross-Link | 交叉链接 | Concept之间的Markdown链接，表示概念间的语义关系，构成知识图谱的边 |
| Dataplex | 数据湖治理服务 | Google Cloud原数据治理产品，现演进为Knowledge Catalog，增加AI驱动的知识管理能力 |
| Enrichment | 知识增强 | 参考Agent通过Web Pass抓取外部文档，补充和丰富现有Concept内容的过程 |
| Frontmatter | 前置元数据 | 文件开头以`---`分隔的YAML元数据块，承载结构化、可查询字段，`type`为唯一必填字段 |
| Git-Native | Git原生 | 格式天然适合Git版本控制，支持分支、PR、diff、blame等完整软件工程工作流 |
| Human- and Agent-Readable | 人与Agent共读 | OKF核心设计哲学：知识表示格式必须同时对人类和智能体友好，无需专用SDK即可访问 |
| Index File | 索引文件 | 即`index.md`，目录内容列表，支持渐进式披露，无frontmatter，可自动生成也可手写 |
| Knowledge Catalog | 知识目录 | Google Cloud推出的AI驱动数据目录与知识管理平台（原Dataplex），包含OKF规范、参考Agent、工具链与示例 |
| Knowledge Graph | 知识图谱 | 由Concepts节点和它们之间的Cross-Links边组成的可导航语义网络 |
| Log File | 日志文件 | 即`log.md`，记录该目录范围内的高层变更历史，按ISO日期倒序排列，类似CHANGELOG |
| Producer/Consumer Independence | 生产消费解耦 | 知识生产者与消费者彻底分离，OKF格式是唯一契约，互不绑定特定工具或平台 |
| Progressive Disclosure | 渐进式披露 | 通过index.md让人类或Agent在打开单个文档前即可了解目录内容，按需深入，避免信息过载 |
| Receipt | 执行凭证 | Attested Computation运行后产生的证据工件（如job_id、执行SQL、结果），不存储在Bundle内 |
| Reference Agent | 参考Agent | Knowledge Catalog提供的概念验证生产者，分BQ Pass和Web Pass两阶段自动生成OKF Bundle |
| Reserved Filename | 保留文件名 | `index.md`和`log.md`，任何目录层级都有特殊含义，不能用作普通Concept文件名 |
| Trust Tier | 信任层级 | 消费者从`verified`字段推导的可信度等级，分为unverified、machine-confirmed、human-reviewed三级 |
| Verdict | 认证结论 | Attester确定性代码验证Receipt后输出的结论，判定计算是否按受认可方式执行 |
| Viz | 可视化工具 | Knowledge Catalog提供的自包含交互式HTML可视化工具（viz.html），使用Cytoscape.js绘制知识图谱 |
| Web Pass | Web增强阶段 | 参考Agent工作流第二阶段，LLM作为自主爬虫抓取权威文档URL，丰富现有Concept或创建references文档 |

### 8.1.2 OKF格式与工具链相关术语

| 术语 | 中文 | 定义 |
|------|------|------|
| Absolute Link | Bundle绝对链接 | 以`/`开头的链接，相对于Bundle根目录解析，移动文件时不失效 |
| Body | 正文 | Concept文件中frontmatter之后的Markdown内容部分 |
| Bundle-Root-Relative Link | 同Absolute Link | 见Absolute Link |
| Citation | 引用 | 指向外部来源的链接，用于支撑正文中的主张，帮助追溯信息来源 |
| Consumer Agent | 消费端Agent | 读取和使用OKF知识的AI Agent或工具，如RAG系统、可视化工具、搜索索引 |
| Cytoscape.js | 图渲染库 | Knowledge Catalog可视化工具使用的JavaScript图可视化库，用于绘制力导向知识图谱 |
| Diffable | 可差分 | 纯文本格式支持版本控制系统的diff/merge，这是OKF选择Markdown+YAML的关键原因 |
| Lifecycle Field | 生命周期字段 | 元数据字段家族（status、stale_after等），标记知识生命周期状态（draft/stable/deprecated） |
| marked.js | Markdown渲染库 | Knowledge Catalog可视化工具使用的Markdown渲染库，在浏览器中实时渲染Concept正文 |
| Minimally Opinionated | 最少约定 | OKF核心设计原则：只强制最少规则（仅type字段必填），最大化采用面和灵活性 |
| Non-Goals | 非目标 | OKF/Knowledge Catalog明确不做的事情，如不强制Schema、不提供中央存储，避免范围蔓延 |
| Portable | 可移植 | 不绑定任何平台/厂商/工具，知识可以自由迁移，就像HTML不绑定特定浏览器 |
| Provenance | 来源元数据 | 元数据字段家族（sources、generated、verified），追踪知识来源、生成者、验证历史和可信度 |
| references/目录 | 参考资料目录 | Bundle内约定的子目录，用于存放外部材料镜像、运行指令、验证代码等，sources/executor/attester通常指向此目录 |
| Relative Link | 相对链接 | 标准Markdown相对路径链接，相对于当前文件所在目录解析 |
| SemVer | 语义化版本 | MAJOR.MINOR.PATCH版本号规范，用于Bundle版本管理 |
| Self-Contained HTML | 自包含HTML | 可视化工具viz.html的特性：所有CSS/JS内联或从CDN加载，无需后端服务，直接在浏览器打开即可使用 |
| Source | 来源记录 | `sources`字段中的条目，记录概念衍生自的材料，包含resource、id、title及可信度信号（author、usage_count等） |
| Stale After | 过期日期 | 元数据字段，指定概念的绝对过期日期，超过此日期视为过时，需要重新验证 |
| Status | 状态字段 | 生命周期状态字段，可选值为draft（草稿）、stable（稳定）、deprecated（废弃） |
| Type | 类型字段 | OKF唯一强制frontmatter字段，标识Concept的类别（如BigQuery Table、Metric、Attested Computation），用于路由和过滤 |
| Validator | 验证器 | 官方在线工具（https://okf.md/validator），检查Bundle是否符合OKF规范 |
| YAML Frontmatter | 同Frontmatter | 见Frontmatter |

## 8.2 官方资源链接

**Knowledge Catalog核心资源：**
- [GitHub官方仓库](https://github.com/GoogleCloudPlatform/knowledge-catalog) - GoogleCloudPlatform官方开源仓库，包含OKF规范、参考Agent、工具链和所有示例Bundle
- [Google Cloud产品页](https://cloud.google.com/products/knowledge-catalog) - Knowledge Catalog官方产品介绍页面
- [OKF官网](https://okf.md/) - Open Knowledge Format项目首页
- [OKF规范完整版](https://okf.md/spec) - OKF v0.2带注释规范文档
- [OKF 5分钟快速入门](https://okf.md/quickstart) - 官方Quickstart教程
- [OKF在线验证器](https://okf.md/validator) - 浏览器中直接验证Bundle合规性（零安装）
- [OKF Agent Skill安装](https://okf.md/skill) - 让Claude/Codex/Cursor生成合规OKF的Skill

**示例Bundle（GitHub仓库bundles/目录）：**
- [GA4电商数据集](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/bundles/ga4) - Google Analytics 4电子商务分析示例
- [Stack Overflow公开数据集](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/bundles/stackoverflow) - Stack Overflow问题与标签知识图谱
- [比特币区块链数据集](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/bundles/crypto_bitcoin) - 区块链区块、交易、地址元数据
- [Acme Retail示例](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/bundles/acme_retail) - 零售业务指标、认证计算示例

## 8.3 项目内Wiki交叉引用

### 8.3.1 OKF Wiki完整章节交叉引用

| 章节 | 路径 | 关联说明 |
|------|------|---------|
| OKF概述与知识地图 | [../okf-wiki/00-overview.md](../okf-wiki/00-overview.md) | OKF基础概念、设计哲学、学习路径，Knowledge Catalog的前置知识 |
| OKF核心概念 | [../okf-wiki/01-core-concepts.md](../okf-wiki/01-core-concepts.md) | Bundle/Concept/Frontmatter等OKF格式层核心概念详解 |
| OKF快速入门 | [../okf-wiki/02-quickstart.md](../okf-wiki/02-quickstart.md) | 5分钟创建第一个OKF Bundle实操指南 |
| OKF使用模式 | [../okf-wiki/03-usage-patterns.md](../okf-wiki/03-usage-patterns.md) | OKF典型应用场景与使用模式 |
| OKF局限性与对比 | [../okf-wiki/04-limitations-and-comparison.md](../okf-wiki/04-limitations-and-comparison.md) | OKF与其他知识表示方案的对比、适用边界分析 |
| OKF架构与集成 | [../okf-wiki/05-architecture-and-integration.md](../okf-wiki/05-architecture-and-integration.md) | OKF架构设计、与现有系统集成方案 |
| OKF FAQ与最佳实践 | [../okf-wiki/06-faq-and-best-practices.md](../okf-wiki/06-faq-and-best-practices.md) | 常见问题解答、编写OKF的最佳实践 |
| OKF资源与术语表 | [../okf-wiki/07-resources-and-glossary.md](../okf-wiki/07-resources-and-glossary.md) | OKF专属术语表与资源链接 |

### 8.3.2 Knowledge Catalog Wiki内部章节交叉引用

| 章节 | 路径 | 核心内容 |
|------|------|---------|
| Knowledge Catalog概述与知识地图 | [./00-overview.md](./00-overview.md) | 平台背景动机、设计哲学、整体架构、9章导航、三条阅读路径 |
| 核心概念与平台架构 | [./01-core-concepts.md](./01-core-concepts.md) | 知识图谱、动态元数据、Bundle/Concept/Frontmatter核心概念、四层平台架构 |
| OKF开放知识格式规范深度解析 | [./02-okf-specification.md](./02-okf-specification.md) | OKF v0.2规范详解、frontmatter字段定义、信任层级与来源溯源、链接规则 |
| 参考Agent实现原理与运行指南 | [./03-reference-agent.md](./03-reference-agent.md) | BQ Pass与Web Pass双阶段工作流、生产端配置、单概念迭代开发、凭证配置 |
| 工具链与可视化系统 | [./04-toolchain-and-visualization.md](./04-toolchain-and-visualization.md) | 交互式知识图谱浏览器、Cytoscape.js图渲染、Markdown实时渲染、搜索与过滤 |
| 示例Bundle深度解析 | [./05-samples-and-bundles.md](./05-samples-and-bundles.md) | GA4电商、Stack Overflow、比特币区块链、Acme Retail示例剖析 |
| 集成模式与最佳实践 | [./06-integration-patterns.md](./06-integration-patterns.md) | 企业落地四阶段路径、与现有数据目录集成、Git工作流集成、生产消费解耦模式 |
| 架构决策与方案对比 | [./07-architecture-decisions.md](./07-architecture-decisions.md) | 与Unity Catalog/Collibra等方案对比、OKF局限性分析、选型决策树、风险评估 |

### 8.3.3 相关Wiki交叉引用

| Wiki | 路径 | 关联说明 |
|------|------|---------|
| Agent协议与接口技术栈首页 | [../README.md](../README.md) | 本系列Wiki的目录首页，包含所有Agent协议主题导航 |
| Agent Skills Wiki | [../agent-skills-wiki/README.md](../agent-skills-wiki/README.md) | Skills是程序层，OKF是知识层，两者互补共同构成Agent能力栈 |
| Agent通信协议 | [../agent-communication-protocols/README.md](../agent-communication-protocols/README.md) | MCP/A2A/ACP等Agent协议，OKF与MCP互补（MCP连接工具，OKF文档化工具知识） |
| 接口/API/ABI/Protocol概念辨析 | [../interface-api-abi-protocol-wiki/README.md](../interface-api-abi-protocol-wiki/README.md) | OKF本质是知识层的接口标准，与API/Protocol概念一脉相承 |
| Harness七组件 | [../../02-agent-engineering-methodology/harness-seven-components-wiki/README.md](../../02-agent-engineering-methodology/harness-seven-components-wiki/README.md) | Harness中的Knowledge Base组件与OKF定位深度契合 |
| 七概念方法论 | [../../02-agent-engineering-methodology/seven-concepts-prompt-wiki/README.md](../../02-agent-engineering-methodology/seven-concepts-prompt-wiki/README.md) | 本教程使用七概念方法论知识沉淀场景产出 |
| 知识库首页 | [../../../../README.md](../../../../README.md) | 整个技术知识库的总入口 |

## 8.4 学习建议

### 8.4.1 按角色选择学习路径

**如果你是AI Agent开发者：**
1. 先完成快速上手路径（00→01→02→05→08），建立整体认知
2. 重点阅读[03参考Agent实现](./03-reference-agent.md)和[04工具链](./04-toolchain-and-visualization.md)，理解如何生产和消费OKF知识
3. 动手做一个小Bundle（从你的业务领域选3-5个核心概念），运行参考Agent或手动编写
4. 尝试用viz.html可视化你的Bundle，体验知识图谱导航
5. 思考OKF如何与你现有RAG/知识库系统集成——可以先从非核心业务试点

**如果你是数据工程师/数据治理专家：**
1. 先走架构决策路径（00→01→02→06→07→08），判断是否适合团队
2. 重点阅读[06集成模式](./06-integration-patterns.md)和[07架构决策](./07-architecture-decisions.md)，理解落地路径
3. 对比现有数据目录（Unity Catalog/Collibra等），思考OKF的互补价值而非替代价值
4. 从元数据导出开始试点：用脚本从现有系统导出几个核心表的元数据为OKF格式
5. 建立Git工作流规范，让元数据变更像代码一样走PR评审

**如果你是架构师/技术决策者：**
1. 完整阅读所有章节，特别关注[07架构决策](./07-architecture-decisions.md)的风险评估和选型决策树
2. 理解三层定位：模型是租的、框架是工具、Skills是招式，知识才是企业自己的护城河
3. 评估当前阶段（技术预览版）适合的投入程度：建议小范围试点而非All-in
4. 关注生态发展：OKF目前极早期（v0.2），建议每3-6个月复查一次生态成熟度
5. 思考与现有技术栈的集成点：Git工作流、CI/CD、数据目录、RAG系统

**如果你是知识工程师/技术写作者：**
1. 阅读00→01→02→05，理解OKF的结构化写作要求
2. 对比Obsidian/Notion等工具：理解开放格式vs平台锁定的权衡
3. 尝试用OKF格式重写现有团队文档，体验frontmatter元数据带来的结构化好处
4. 建立团队的type字段约定和tags分类规范

### 8.4.2 实践建议

1. **从小处开始**：不要试图一开始就构建完整的企业知识图谱，从3-5个概念的微型Bundle开始
2. **Git工作流先行**：Bundle就是Git仓库，先用好Git的版本控制、分支、PR能力，这是OKF的核心优势
3. **结构化优先**：写Concept时鼓励使用标题、列表、表格、代码块等结构化Markdown，而非自由文本——这既提升人类阅读体验，也显著提高RAG准确率
4. **来源意识**：养成标注sources的习惯，这是对抗AI幻觉的关键机制
5. **迭代式完善**：先有草稿（status: draft），再逐步验证（verified）到稳定（status: stable），不要追求一次完美
6. **关注Attested Computation**：如果涉及指标计算、报表生成等场景，认证计算是防止Agent编造数字的关键机制，值得深入理解

---

Knowledge Catalog与OKF代表了一个重要方向：数据与知识应该像HTML和代码一样开放、可互操作、不被平台锁定，能被人类和Agent共同使用，能像源代码一样工程化管理。但方向正确不代表现在就该All-in——保持关注、小范围试点、积累经验，是这个技术预览阶段最理性的策略。

> "知识应该像代码一样被版本控制、被评审、被协作、被复用，而不是被锁定在专有系统中难以迁移。" —— Knowledge Catalog设计哲学

---

| 上一章 | 目录 | 下一章 |
|--------|------|--------|
| [07 架构决策与方案对比](./07-architecture-decisions.md) | [README](./README.md) | **本教程结束** 🎉 |
