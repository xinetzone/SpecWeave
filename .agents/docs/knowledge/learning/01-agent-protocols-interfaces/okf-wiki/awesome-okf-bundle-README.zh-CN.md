---
type: Translation
title: Awesome OKF 中文翻译
description: linyiru/awesome-okf 项目 README 的中文翻译，OKF（开放知识格式）生态资源精选列表
source: vendor/awesome-okf-bundle/README.md
tags:
  - OKF
  - 开放知识格式
  - 知识图谱
  - AI Agent
  - Markdown
  - 翻译
---

# Awesome OKF [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

> 一份精心整理的 **开放知识格式（Open Knowledge Format, OKF）** 资源列表——这是 Google 推出的开放、厂商中立的规范，用于将知识表示为带有 YAML frontmatter 的 Markdown 文件，AI 智能体无需自定义集成即可读取。本列表践行了它所收录的理念：它本身就是作为一个符合规范的 OKF bundle 发布的（见下文）。

OKF 由 Google Cloud 于 2026 年 6 月发布；v0.2 版本于 2026 年 7 月跟进。它将"LLM-wiki"模式正式化为一种可移植、可互操作的格式：知识以带有结构化 frontmatter（`type`、`title`、`description`、`resource`、`tags`，以及可选的溯源、信任和生命周期字段）的纯 Markdown 文件形式存在，并通过交叉链接形成知识图谱。无需 SDK，无需运行时，无锁定——你可以将这些文件打包成 tarball、托管在 Git 中，或挂载在文件系统上。

## 目录

- [OKF 概览](#okf-概览)
- [规范文档](#规范文档)
- [官方工具与参考实现](#官方工具与参考实现)
- [示例 Bundles](#示例-bundles)
- [社区工具](#社区工具)
- [文章与指南](#文章与指南)
- [背景与起源](#背景与起源)
- [基于 LLM-Wiki 模式构建](#基于-llm-wiki-模式构建)
- [相关格式与概念](#相关格式与概念)
- [社区](#社区)

## OKF 概览

一个 bundle 是一个 Markdown 文件的目录树，目录结构与领域无关。以下是 v0.2 规范的要点：

| 方面 | 规则 |
| --- | --- |
| 概念 | 一个 Markdown 文件：YAML frontmatter 加上自由格式的 Markdown 正文。 |
| 必填字段 | `type`——标识概念类型的非空字符串。 |
| 推荐字段 | `title`、`description`、`resource`（底层资产的 URI）、`tags`。 |
| 溯源与信任 | 可选的 `sources`（带有每个来源的可信度信号）、`generated`（`{ by, at }`；取代 v0.1 的 `timestamp`）和 `verified`——消费者可派生信任层级（未验证/机器确认/人工审核）。 |
| 生命周期 | 可选的 `status`（`draft`/`stable`/`deprecated`；缺省表示 `stable`）和 `stale_after`（绝对日期）。 |
| 认证计算 | `type: Attested Computation` 概念携带经过批准的计算（`runtime`、`parameters`、`executor`、`attester`），以便消费者可以确认某个值是以受认可的方式产生的，而非临时编造。 |
| 参与者 | `generated.by`/`verified[].by` 对智能体使用 `<producer>/<version>`，对人员使用 `human:<id>`，对流程使用 `process:<id>`。 |
| 保留文件名 | `index.md`（用于渐进式披露的目录列表）和 `log.md`（更新历史）；其他所有 `.md` 文件都是概念。bundle 根目录的 `index.md` 可以在 frontmatter 中声明 `okf_version`。 |
| 链接 | 从概念 A 到 B 的链接断言一种关系；使用 bundle 相对路径（以 `/` 开头）或普通相对路径。 |
| 一致性 | 每个非保留的 `.md` 文件都具有可解析的 frontmatter，其中包含非空的 `type`；保留文件在存在时遵循其定义的结构。 |
| 消费者容错 | 消费者必须容忍缺失可选字段（包括所有信任和溯源族字段）、未知的 `type` 值、断链和缺失的 `index.md`。 |
| 扩展 | 生产者可以添加自定义键；消费者必须保留未知字段。 |

> 本列表也作为符合规范的 OKF v0.2 bundle 发布在 [`bundle/`](bundle) 目录下，由 [`scripts/build-okf-bundle.mjs`](scripts/build-okf-bundle.mjs) 从此 README 生成。

## 规范文档

- [OKF v0.2 规范（SPEC.md）](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)——通用、厂商中立的规范，包括一致性标准和保留文件名。v0.2（2026 年 7 月）将溯源（`sources`）、信任（`generated`/`verified`）、生命周期（`status`/`stale_after`）和认证计算提升为一等公民；它取代了 v0.1 的 `timestamp` 字段和正文 `# Citations` 列表。[v0.1 文本在固定提交处保持可读](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/ee67a5ca27044ebe7c38385f5b6cffc2305a9c1a/okf/SPEC.md)。
- [GoogleCloudPlatform/knowledge-catalog `okf/`](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf)——该格式的主仓库、参考代码和示例。
- [OKF README](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/README.md)——OKF 理念、安装和使用概述。

## 官方工具与参考实现

- [参考智能体](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf/src/reference_agent)——Python 实现（基于 Google 的 Agent Development Kit 构建），用于生成和可视化 OKF bundles：它从 BigQuery 源起草 OKF 文档，通过网络爬取的溯源信息丰富它们（自 v0.2 起的 `sources` frontmatter，带有每个声明的脚注归属），并附带一个 `viewer/generator.py`，将 bundle 渲染为一个自包含的交互式图谱。
- [Knowledge Catalog 丰富工具箱](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/toolbox/enrichment)——即用型智能体和可定制框架（TypeScript），用于在 Knowledge Catalog 中生成、演进和维护元数据。包含一个将 Markdown 文件集公开为 MCP 服务器的服务器。
- [Knowledge Catalog mdcode](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/toolbox/mdcode)——将元数据作为源代码工件管理，支持 OKF Markdown 与 BigQuery/Dataplex/Knowledge Catalog 之间类似 git 的 pull/push 同步。

## 示例 Bundles

来自主仓库的四个符合规范、可直接浏览的 bundles，每个都带有一个自包含的交互式 `viz.html` 图谱查看器。前三个是从公共 BigQuery 数据集构建的：

- [GA4 电子商务](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf/bundles/ga4)——Google Analytics 4 电子商务元数据。
- [Stack Overflow](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf/bundles/stackoverflow)——公共问答数据集的模式图谱。
- [Bitcoin](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf/bundles/crypto_bitcoin)——来自公共区块链数据集的链上概念。
- [ACME Retail](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf/bundles/acme_retail)——v0.2 展示案例：一个虚构零售商的财务知识，运用了认证计算（带有确定性的 `sql_equality.py` 证明者）、执行器技能和 `deprecated` 生命周期状态。

## 社区工具

- [okft](https://github.com/PoorvaJ-WW/okft)——OKF bundles 的 linter 和 MCP 服务器（`pip install okft`）：`okft lint` 验证规范一致性和卫生状况（断链、孤立文件、时间戳），带有 CI 友好的退出码和 JSON 输出；`okft serve` 将 bundle 作为确定性导航工具暴露给任何支持 MCP 的智能体。Apache-2.0 许可。
- [BundleDex](https://bundledex.net)——包含 440+ OKF bundles 的目录，提供搜索、去重、分类和面向智能体的 JSON API。
- [OKF Bundle 生成器](https://suganthan.com/okf-generator/)——Suganthan Mohanadasan 开发的免费网络工具：粘贴 URL 或 sitemap，它会爬取最多 100 个页面，将每个页面转换为干净的 OKF 概念，将它们链接成图谱，并输出可下载的 v0.2 bundle（记录 `generated` 和 `sources`；`verified` 留给你处理）。
- [SchemaCrawler Scribe](https://www.schemacrawler.com/scribe.html)——直接从实时模式元数据生成结构化数据库文档，采用 Google 开放知识格式（OKF）。参见[《AI 就绪的数据库文档，你可以保存在 Git 中》](https://dev.to/sualeh/schemacrawler-scribe-google-okf-ai-ready-database-docs-you-can-keep-in-git-2off)快速了解。
- [samemind](https://github.com/alexgrebeshok-coder/samemind)——AI 编码智能体的个人记忆，存储为 OKF bundle：身份、仅追加的工作台账和纯 Markdown 格式的看板。`export`/`import` 直接支持 OKF v0.1 线格式；零依赖 CLI 加上 MCP 服务器，带有 12 引擎指令文件安装器。
- [knowledge-mcp](https://github.com/chirag127/knowledge-mcp)——公共 MCP 服务器，通过 `search`、`read`、`list` 和 `related` 工具暴露 OKF bundle；部署在 Cloudflare Workers 上，无需认证。可指向任何 OKF v0.1 bundle，因此任何 MCP 客户端（Claude Code、Cursor 等）都可以将其作为知识图谱查询。
- [okf-gem](https://github.com/serradura/okf-gem)——Ruby 框架，覆盖 bundle 的整个生命周期：智能体技能创作和策展概念，CLI 和库检查它们（`validate` 用于 v0.1 一致性，`lint` 作为单独的非阻塞策展报告，排名 `search` 用于检索），`okf server`/`okf render` 发布交互式图谱（实时或作为一个自包含的 HTML 文件）。完全本地运行；`gem install okf` 或 Docker；[在线演示](https://demo.okfgem.com)。Apache-2.0 许可。
- [okf-skills](https://github.com/scaccogatto/okf-skills)——面向 Claude Code 的 OKF 工具包：插件、智能体技能和 GitHub Action，用于创作、验证和可视化 bundles。基于 v0.2 构建——支持信任层级、溯源、过时性和认证计算。MIT 许可。
- [EchoesVault](https://github.com/psinetron/echoes-vault-opencode)——OpenCode 的持久记忆插件，将其 vault 存储为符合 OKF 规范的 bundle——同时也是一个有效的 Obsidian vault。MIT 许可。
- [claude-mega-brain](https://github.com/guhcostan/claude-mega-brain)——Claude Code 插件，在会话开始时注入 OKF 知识库，并针对 Obsidian+MCP 设置进行智能体基准测试。MIT 许可。
- [OWOX Model Canvas](https://github.com/OWOX/models)——可视化、类似 Miro 的数据模型编辑器，以 OKF 作为原生格式进行读写；该仓库还发布真实 bundles。Apache-2.0 许可。

## 文章与指南

- [开放知识格式如何改善数据共享](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing)——Google Cloud 官方公告（Sam McVeety & Amir Hormati）。从这里开始。
- [OKF v0.2 增加信任信号](https://cloud.google.com/blog/products/data-analytics/okf-v0-2-adds-trust-signals)——官方 v0.2 公告（2026 年 7 月）：为什么智能体维护的语料库需要直接从 frontmatter 可回答的溯源、信任、新鲜度、生命周期和认证。
- [介绍 Google Cloud Knowledge Catalog](https://cloud.google.com/blog/products/data-analytics/introducing-the-google-cloud-knowledge-catalog)——OKF 与之共同设计的配套产品；Knowledge Catalog 生成和消费 OKF 作为其开放、可移植的格式。
- [OKF，作者 Marie Haynes](https://www.mariehaynes.com/okf/)——为什么 OKF 对 SEO/AI 很重要：从"被搜索引擎找到"到"使知识可访问以便智能体可以据此行动"的转变。
- [像我一样构建一个 OKF 大脑！](https://www.mariehaynes.com/build-an-okf-brain-like-mine/)——Marie Haynes 的后续文章：她个人 OKF 大脑的演练（概念、实体、剧本、参考、系统），带有构建你自己的提示词。
- [开放知识格式（OKF）：Google 面向 AI 智能体的新 Markdown 格式](https://suganthan.com/blog/open-knowledge-format/)——Suganthan Mohanadasan 的实用解释，针对 v0.2 的信任和溯源字段进行了更新。
- [Google 发布了一种开放格式（OKF）。我的网站已经在使用它了。](https://suganthan.com/notes/google-shipped-okf/)——构建首批社区 bundles 之一的实践笔记。
- [Google Cloud 宣布开放知识格式](https://www.searchenginejournal.com/google-cloud-announces-the-open-knowledge-format/579253/)——Search Engine Journal 报道。
- [什么是 Google 的开放知识格式（OKF）？面向网站所有者的简明英语指南](https://nexterwp.com/blog/open-knowledge-format/)——面向网站所有者的初学者友好指南。
- [开放知识格式（OKF）：Google AI 智能体标准](https://www.explainx.ai/blog/google-open-knowledge-format-okf-ai-agents-2026)——在智能体 AI 背景下的 OKF 概述。
- [开放知识格式：Google 实际发布了什么](https://www.iloveseo.net/the-open-knowledge-format-what-google-really-shipped/)——Gianluca Fiorelli 的长篇分析：OKF 作为企业智能体记忆而非 SEO 策略，包含早期采用者访谈和 ARD 关系映射。
- [在 specification.website 上组合 OKF 和 ARD](https://joost.blog/okf-ard/)——Joost de Valk 在一个网站上实现了这两个规范，遇到了它们之间真实的字段名冲突，并向上游提交了问题。

## 背景与起源

- [LLM Wiki，作者 Andrej Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)——OKF 正式化的"LLM-wiki"模式。OKF 的保留 `index.md` 和 `log.md` 文件及其 raw-sources/wiki/schema 分层直接追溯到此 gist。
- [《诚如所思》，作者 Vannevar Bush（1945）](https://en.wikipedia.org/wiki/As_We_May_Think)——Karpathy 引用为更深层祖先的 Memex 文章：一个个人的、策展的知识存储，其中文档之间的链接与文档本身同样重要。

## 基于 LLM-Wiki 模式构建

OKF 正式化的 LLM-wiki 模式的社区实现。这些不是 OKF 原生的，但它们共享其"知识作为智能体维护的交叉链接 Markdown"的理念。

- [AutoSci](https://github.com/skyllwt/AutoSci)——基于 LLM-wiki 愿景构建的全生命周期 AI 研究平台，带有 28 个智能体技能（Claude Code 中的斜杠命令，适配 Codex 和 OpenCode），用于摄取和综合论文。
- [karpathy-llm-wiki](https://github.com/Astro-Han/karpathy-llm-wiki)——面向 Claude Code、Cursor 和 Codex 的智能体技能兼容 LLM wiki，可摄取来源、编译 wiki 页面、带引用回答，并进行一致性检查。
- [llmwiki](https://github.com/lucasastorian/llmwiki)——开源实现：上传文档，通过 MCP 连接 Claude，让智能体编写和维护 wiki。
- [Synto](https://github.com/kytmanov/synto)——本地优先的 wiki 构建器，在消费级硬件上使用双层 Ollama 管道（小模型提取概念，大模型编写交叉链接文章）。
- [llm_wiki](https://github.com/nashsu/llm_wiki)——跨平台桌面应用，自动将文档转换为有组织的、交叉链接的知识库。

## 相关格式与概念

- [智能体资源发现（ARD）](https://github.com/ards-project/ard-spec)——Google 发布的姊妹规范，在 OKF 发布几天后公布：联合目录通告资源——包括 OKF bundles——以便智能体可以发现它们。OKF 打包知识；ARD 找到它。
- [llms.txt](https://llmstxt.org/)——一个提议的标准，用于帮助 LLM 使用网站内容的 Markdown 文件。
- [模型上下文协议（MCP）](https://modelcontextprotocol.io/)——用于连接 AI 智能体与工具和数据源的开放协议。
- [AGENTS.md](https://agents.md/)——一个简单、开放的约定，用于给编码智能体提供项目指令。
- [Obsidian](https://obsidian.md/)——带有反向链接的 Markdown vault；OKF 笔记目录模型的近亲。
- [Dataview](https://blacksmithgu.github.io/obsidian-dataview/)——基于 Markdown frontmatter 的查询语言，用于从 OKF 风格的结构化字段构建动态视图很有用。
- [Marp](https://marp.app/)——Markdown 演示生态系统；将 Markdown 知识文件转换为幻灯片。

## 社区

- [Google Cloud Tech 在 X 上](https://x.com/GoogleCloudTech/status/2067012903337664886)——发布公告。
- [Google 提出基于 Markdown 的开放知识格式（Hacker News）](https://news.ycombinator.com/item?id=48517735)——发布讨论：怀疑、现有技术和替代方案。
- [awesome-okf（中文）](https://github.com/yzfly/awesome-okf)——中文姊妹列表，附带飞书、Obsidian、Notion 和 GitHub-to-OKF 转换器。

## 贡献

欢迎贡献！请先阅读[贡献指南](CONTRIBUTING.md)。OKF 生态系统是全新的——如果你构建了生产者、消费者、查看器或 bundle，请在这里添加。
