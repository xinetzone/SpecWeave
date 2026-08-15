---
id: knowledge-catalog-wiki-overview
title: 00 - 总览与架构全景
date: 2026-08-15
tags:
  - overview
  - architecture
  - positioning
source:
  - vendor/knowledge-catalog/README.md
  - vendor/knowledge-catalog/okf/README.md
maturity: L1-draft
---

# 00 - Knowledge Catalog 总览与架构全景

> TL;DR：Knowledge Catalog是Google Cloud的AI原生数据目录，其核心创新是OKF——一种用Markdown+YAML表示知识的开放格式，将"知识即代码"理念落地，为AI Agent提供可验证、可追溯、可版本控制的数据上下文。

---

## 一、产品定位：从"数据目录"到"AI上下文基础设施"

### 1.1 什么是Knowledge Catalog？

[Knowledge Catalog](https://cloud.google.com/products/knowledge-catalog)（前身为Dataplex）是Google Cloud推出的**AI驱动的数据目录和元数据管理平台**。

传统数据目录解决的问题是："人如何找到数据、理解数据Schema？"——面向数据分析师、数据工程师，提供表搜索、血缘追踪、Schema浏览等功能。

Knowledge Catalog解决的核心问题升级为：**"AI Agent如何理解数据的语义和业务上下文，并且信任这些信息？"**——面向AI智能体，提供带可信度标注、来源追溯、时效验证、计算认证的动态知识图谱。

### 1.2 核心价值主张

| 传统数据目录 | Knowledge Catalog (OKF范式) |
|-------------|---------------------------|
| 集中式元数据存储 | 去中心化知识包（文件系统+Git） |
| 专有API/Web UI访问 | Markdown+YAML，任何能读文件的工具都能消费 |
| 面向人类阅读 | 人类和Agent双重可读 |
| 仅描述Schema | 完整业务上下文+信任层级+认证计算 |
| 厂商锁定 | 厂商中立的开放格式 |
| 手工管理UI操作 | Git工作流+CI/CD+Agent自动丰富 |

### 1.3 为什么这很重要？

当AI Agent要回答"2026年Q2按GAAP口径的营收是多少？"时，它需要知道：
- "营收"这个指标在业务上是什么定义？（收入确认政策）
- 这个数字从哪张表、哪个字段计算？（SQL/数据血缘）
- 计算方法是否经过财务团队认证？（认证计算+验证人）
- 这个指标定义是最新的吗？（时效标注`stale_after`）
- 如果我自己写SQL算，结果和官方数字不一致怎么办？（确定性Attester验证）

OKF就是为回答这些问题而设计的元数据格式。

---

## 二、仓库架构全景

仓库地址：https://github.com/GoogleCloudPlatform/knowledge-catalog

```
knowledge-catalog/
├── okf/                          # 🎯 OKF开放知识格式（核心创新）
│   ├── SPEC.md                   # OKF v0.2 完整规范（1000+行）
│   ├── README.md                 # OKF介绍与快速开始
│   ├── bundles/                  # 4个预构建OKF知识包示例
│   │   ├── ga4/                  # GA4 Google Merch Store电商数据集
│   │   ├── stackoverflow/        # Stack Overflow公开数据集
│   │   ├── crypto_bitcoin/       # Bitcoin区块/交易数据集
│   │   └── acme_retail/          # Acme零售示例（含认证计算）
│   ├── src/reference_agent/      # Python参考智能体实现
│   │   ├── agent.py              # ADK智能体定义
│   │   ├── cli.py                # 命令行入口
│   │   ├── sources/bigquery.py   # BigQuery元数据源
│   │   ├── web/fetcher.py        # 网页抓取器
│   │   ├── tools/                # Agent工具集
│   │   └── viewer/               # 交互式可视化（Cytoscape.js）
│   └── samples/                  # 参考智能体的种子URL配置
│
├── samples/                      # 🤖 示例智能体（应用层）
│   ├── discovery/                # Discovery Agent：语义搜索助手
│   └── enrichment/               # Enrichment Agent：元数据丰富智能体
│
└── toolbox/                      # 🔧 生产工具链
    ├── mdcode/                   # Metadata as Code：kcmd CLI+库+MCP服务器
    │   ├── src/libts/            # TypeScript核心库
    │   ├── src/tool/             # kcmd CLI实现
    │   └── tests/                # 测试用例+语义SQL测试
    └── enrichment/               # TypeScript版Enrichment Agent
```

### 三层架构对应关系

| 层级 | 目录 | 作用 | 成熟度 |
|------|------|------|--------|
| **标准规范层** | `okf/SPEC.md` | 定义OKF格式，是唯一的真理来源 | 稳定（v0.2） |
| **参考实现层** | `okf/src/reference_agent/` | Python实现，验证OKF可行性，演示生产和消费两端 | PoC/参考 |
| **生产工具层** | `toolbox/mdcode/`, `toolbox/enrichment/` | TypeScript工具链，面向实际生产使用 | 正在开发 |
| **示例应用层** | `samples/discovery/`, `samples/enrichment/` | 智能体示例，展示如何集成使用 | 示例代码 |

---

## 三、OKF 9大设计原则（为什么选Markdown+YAML？）

OKF选择"目录层次+Markdown文件+YAML frontmatter"作为知识表示，刻意获得了以下9个特性，这些特性是传统集中式元数据存储难以同时提供的：

### 3.1 人类和Agent双重可读
无需SDK或查询语言，工程师可以直接`cat`一个概念，LLM可以逐字摄入上下文。没有中间层。

### 3.2 原生版本控制支持
知识包活在Git里。Pull Request、逐行diff、blame、代码审查工作流直接可用——知识策展变成了正常的软件工程活动。

### 3.3 可移植、无锁定
一个知识包就是一个目录。打包成tarball、托管在任意仓库、挂载到任意文件系统、同步到任何支持文件的系统——在你和你的元数据之间没有专有API。

### 3.4 刻意混合结构化与非结构化数据
- Frontmatter放需要查询、过滤、索引的字段（`type`、`resource`、`tags`、`generated`、`status`）
- Markdown正文放 prose、Schema、示例查询——人和LLM实际阅读的内容

### 3.5 信任、来源、时效是一等公民
v0.2在frontmatter中加入了可查询的可信度信号：
- **来源**：概念从哪来（`sources`带每个来源的可信度信号）
- **信任**：谁生成、谁确认（`generated`、`verified`，推导出trust tier）
- **时效**：是否仍然有效（`status`、`stale_after`）
不需要定制运行时，Agent维护的语料库就能保持可信。

### 3.6 最小约定、自由扩展
少量必填键保证互操作性，但知识包可以携带任意额外frontmatter键和正文章节，不会破坏消费者。

### 3.7 与现有工具生态组合
Notion、Obsidian、MkDocs、Hugo、Jekyll——很多知识工具原生支持Markdown+YAML frontmatter，无需定制UI就能浏览、编辑、渲染。

### 3.8 内置渐进式披露
自动生成的`index.md`让Agent或人类可以逐层导航层次结构，而不是把整个知识包一次性加载到上下文。

### 3.9 图结构而非树结构
概念之间通过普通Markdown链接互相引用，表达比目录布局隐含的父子关系更丰富的关联关系。

---

## 四、一页纸速查表

### OKF最小合法概念
```markdown
---
type: Metric
---
这是一个完全合法的OKF概念，只有必填字段type。
```

### OKF典型概念（带信任元数据）
```markdown
---
type: BigQuery Table
title: Customer Orders
description: One row per completed customer order.
resource: https://console.cloud.google.com/bigquery?p=acme&d=sales&t=orders
tags: [sales, orders]
status: stable
generated: { by: reference_agent/gemini-2.5-pro, at: 2026-05-28T14:30:00Z }
verified: { by: human:data-steward, at: 2026-06-01T09:00:00Z }
stale_after: 2026-12-31
sources:
  - id: schema-doc
    resource: https://internal.wiki/sales/orders-schema
    author: team:data-engineering
    usage_count: 1200
    last_modified: 2026-05-20
---

# Schema
| Column | Type | Description |
|--------|------|-------------|
| order_id | STRING | 全局唯一订单ID |
| customer_id | STRING | 外键，关联[customers](/tables/customers.md) |
```

### 信任层级推导规则
- 无`verified` → **unverified（未验证）**
- 仅非`human:`验证者 → **machine-confirmed（机器确认）**
- 有`human:<id>`验证 → **human-reviewed（人工审核）**（最高信任级）

### kcmd CLI常用命令
```bash
kcmd init --bigquery-dataset <project>.<dataset>  # 初始化
kcmd pull                                          # 从目录服务拉取最新元数据
kcmd status                                        # 查看本地变更
kcmd push                                          # 推送本地修改到目录服务
```

---

## 五、仓库快速体验

### 体验OKF可视化（无需GCP账号）
1. 克隆仓库：`git clone https://github.com/GoogleCloudPlatform/knowledge-catalog.git`
2. 直接打开任意预构建bundle的`viz.html`在浏览器中查看知识图谱：
   - `okf/bundles/ga4/viz.html` — GA4电商知识图谱
   - `okf/bundles/stackoverflow/viz.html` — Stack Overflow数据集知识图谱
   - `okf/bundles/crypto_bitcoin/viz.html` — Bitcoin区块链知识图谱

### 运行参考智能体生成OKF bundle（需要GCP账号）
```bash
cd okf
python3.13 -m venv .venv
.venv/bin/pip install -e .[dev]

# 配置认证
gcloud auth application-default login
export GEMINI_API_KEY=<your-key>  # 或配置Vertex AI

# 从BigQuery数据集生成OKF bundle
.venv/bin/python -m reference_agent enrich \
    --source bq \
    --dataset <project>.<dataset> \
    --out ./bundles/<name>

# 生成可视化HTML
.venv/bin/python -m reference_agent visualize --bundle ./bundles/<name>
```

---

继续阅读：[01-okf-spec.md - OKF开放知识格式规范详解](./01-okf-spec.md)
