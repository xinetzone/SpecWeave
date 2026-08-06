---
id: "knowledge-catalog-wiki-toolchain-visualization"
title: "04 工具链与可视化系统"
version: "1.0"
source: "GoogleCloudPlatform/knowledge-catalog okf/src/reference_agent/viewer/ + toolbox/"
type: "Wiki Tutorial"
description: "Knowledge Catalog交互式可视化系统详解，包括力导向知识图谱、详情面板、反向链接、搜索筛选布局、Cytoscape.js+marked.js技术架构、自包含HTML特性；TypeScript工具箱（mdcode元数据即代码、enrichment智能充实Agent）功能与使用指南；官方样例Bundle概览"
tags: ["Knowledge Catalog", "OKF", "Visualization", "Cytoscape.js", "Toolchain", "Metadata as Code", "Enrichment Agent", "MCP", "BigQuery"]
category: "learning"
date: "2026-08-06"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "系统讲解Knowledge Catalog可视化系统的功能特性与技术架构，包括力导向图谱、详情面板、反向链接、搜索筛选等交互功能；详解mdcode元数据即代码工具（语义层、BigQuery集成、MCP服务器、pull/push双向同步）和enrichment智能充实Agent；介绍GA4、Stack Overflow、比特币区块链三个官方样例项目"
last_verified: "2026-08-06"
wiki_version: "1.0"
okf_version_target: "v0.2"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/knowledge/learning/01-agent-protocols-interfaces/knowledge-catalog-wiki/04-toolchain-and-visualization.toml"
---

# 04 工具链与可视化系统

> **本章定位说明**
> - 前三章分别介绍了Knowledge Catalog平台概述（[00 概述与知识地图](./00-overview.md)）、核心概念与架构（[01 核心概念与平台架构](./01-core-concepts.md)）、OKF规范（[02 OKF规范深度解析](./02-okf-specification.md)）和参考Agent实现（[03 参考Agent实现原理与运行指南](./03-reference-agent.md)）。
> - 本章聚焦**消费端工具链**：可视化系统是OKF格式的概念验证消费者（Proof of Concept Consumer），与参考Agent（生产者）形成完整的生产-消费闭环；工具箱提供企业级元数据管理与智能充实能力。
> - 可视化系统生成**零依赖自包含HTML**，无需后端、无需安装，直接在浏览器打开即可交互式浏览知识图谱，完美体现OKF"可移植、无锁定"的设计哲学。
> - 工具箱（toolbox/）是Google官方提供的TypeScript实现，包含mdcode（元数据即代码）和enrichment（智能充实Agent）两大组件，面向生产环境使用。

## 4.1 可视化系统概述

可视化系统通过`reference_agent visualize`子命令将任意OKF Bundle渲染为**单个自包含的交互式HTML文件**。它是OKF格式的概念验证消费者——参考Agent（生产者）演示如何自动生成OKF Bundle，可视化系统（消费者）演示如何消费和展示OKF知识。

### 4.1.1 核心设计理念

| 设计特性 | 说明 |
|---------|------|
| **零后端依赖** | 纯静态HTML文件，无需服务器、无需数据库、无需构建工具 |
| **零安装查看** | 接收方只需现代浏览器，双击即可打开，无需任何依赖安装 |
| **数据完全内嵌** | Bundle的所有概念、链接、正文都序列化为JSON嵌入HTML，单文件即可完整分发 |
| **离线可用** | CDN资源加载失败不影响已生成文件的核心功能（可将库文件本地化） |
| **可分享可归档** | 可作为CI产物附加到PR、上传到静态文件服务器、直接邮件发送、纳入Git版本控制 |

### 4.1.2 功能特性概览

可视化系统提供以下核心交互功能（参见 `okf/src/reference_agent/viewer/templates/viz.html`）：

1. **力导向知识图谱**：Bundle中所有概念以节点表示，Markdown正文中的交叉链接以有向边表示，节点按类型着色
2. **详情面板**：点击节点查看该概念的完整frontmatter元数据和渲染后的Markdown正文
3. **反向链接列表**：自动计算"Cited by"（被引用）列表，展示哪些概念链接到当前概念
4. **搜索功能**：支持按标题、概念ID、标签进行实时搜索过滤
5. **类型筛选**：下拉选择按概念类型过滤节点（如仅显示表、仅显示数据集）
6. **多种布局切换**：支持cose（力导向）、concentric（同心圆）、breadthfirst（广度优先）、circle（环形）、grid（网格）五种布局算法
7. **内部链接导航**：详情面板中的内部Markdown链接（`[text](/path/to/concept.md)`）自动重写为查看器内导航，点击即可跳转，无需离开页面

---

## 4.2 可视化界面详解

### 4.2.1 力导向知识图谱

力导向图是可视化系统的核心视图，基于物理模拟算法自动布局节点：

**节点表示**（参见 `viewer/generator.py:45-65` `Concept.to_node()`）：

- 每个OKF文档（除index.md外）对应一个图节点
- **节点颜色**按`type`字段着色，内置调色板：
  - `BigQuery Dataset`：紫色 `#8b5cf6`
  - `BigQuery Table`：蓝色 `#3b82f6`
  - `Reference`：绿色 `#10b981`
  - 其他类型/未知类型：灰色 `#94a3b8`
- **节点大小**与正文长度正相关（基础30px + 正文长度/200，最大90px），正文越长节点越大，直观反映概念的信息量
- **节点标签**显示frontmatter中的`title`字段，无title时使用概念ID

**边表示**（参见 `viewer/generator.py:131-151` `_build_graph()`）：

- Markdown正文中的每个相对路径`.md`链接对应一条有向边
- 边从源概念指向目标概念，表示"引用"或"相关"关系
- 自动去重：同一对概念间的多条链接只显示一条边
- 自动过滤：外部URL（含`://`）、绝对路径（以`/`开头）、指向Bundle外的链接不生成边
- 自动忽略：自引用（链接到自身）、指向不存在概念的链接不生成边

**链接提取逻辑**（参见 `viewer/generator.py:68-86` `_extract_links()`）：

- 使用正则表达式 `\]\(([^)\s]+\.md)(?:#[A-Za-z0-9_\-]*)?\)` 匹配Markdown链接
- 支持锚点片段（`#section`），提取时自动忽略
- 相对路径相对于当前文档所在目录解析，再转换为相对于Bundle根目录的路径
- 解析失败（路径越界、目标不存在）的链接静默跳过

### 4.2.2 详情面板

点击任意节点时，右侧（或下方，视屏幕尺寸）显示详情面板，展示该概念的完整信息：

**面板结构**（参见 `viz.html:38-59`）：

```
┌─────────────────────────────────┐
│ [类型标签]                       │
│ 概念标题（大标题）                │
│ 概念ID（灰色小字）                │
├─────────────────────────────────┤
│ [信任徽章] [过时标记] [状态标签]  │
├─────────────────────────────────┤
│ Description: 描述文本            │
│ Resource:    资源链接（可点击）   │
│ Tags:        标签列表            │
│ Generated:   生成信息            │
│ Verified:    验证信息            │
│ Sources:     来源列表            │
├─────────────────────────────────┤
│ （渲染后的Markdown正文）          │
│ （代码块、表格、列表正常渲染）     │
├─────────────────────────────────┤
│ Cited by (反向链接列表)           │
│ └─ 概念A → 概念B → ...          │
└─────────────────────────────────┘
```

**关键交互**：

- 正文内的Markdown链接自动重写：点击Bundle内部链接时，不跳转页面，而是在查看器内选中对应节点并更新详情面板
- 外部链接（`http://`、`https://`）正常在新标签页打开
- 资源链接（`resource`字段）如果是URL，可直接点击跳转
- 标签显示为可点击的徽章样式

### 4.2.3 反向链接（Cited by）

反向链接是知识图谱的重要特性，自动展示"哪些文档引用了当前概念"：

**实现原理**（参见 `viewer/static/viz.js` 逻辑）：

- 生成图数据时同时构建正向邻接表（`links_to`）和反向邻接表
- 反向链接通过反转边的方向计算：对于节点A，所有存在边 `X → A` 的节点X都是A的反向链接来源
- 反向链接列表在选中节点时动态计算和渲染

**价值**：

- 发现隐式关联：如表A被哪些指标文档引用
- 评估影响范围：修改某个概念前，可查看哪些文档依赖它
- 导航辅助：从被引用文档快速跳转到引用来源

### 4.2.4 搜索、筛选与布局控制

可视化系统顶部工具栏提供三组控制控件（参见 `viz.html:18-31`）：

| 控件 | 类型 | 功能 |
|------|------|------|
| **搜索框** | 文本输入 | 实时搜索，匹配节点的title、id、tags字段，输入时动态高亮匹配节点并隐藏不匹配节点 |
| **类型筛选** | 下拉选择 | 按概念type过滤，选择"All types"显示全部，选择某一类型仅显示该类节点 |
| **布局选择** | 下拉选择 | 切换5种图布局算法 |
| **重置视图** | 按钮 | 重置缩放、平移、筛选，恢复初始视图 |

**五种布局算法**：

| 布局名称 | 算法类型 | 适用场景 |
|---------|---------|---------|
| `cose` | 力导向（Compound Spring Embedder） | 默认布局，模拟弹簧力自然分布，适合展示整体关系网络 |
| `concentric` | 同心圆布局 | 按节点度数（连接数）分层排列，中心节点向外辐射，适合识别核心概念 |
| `breadthfirst` | 广度优先布局 | 层次化树状布局，适合展示有明显层级的目录结构 |
| `circle` | 环形布局 | 所有节点均匀分布在圆周上，适合比较节点间距离 |
| `grid` | 网格布局 | 节点整齐排列在网格中，适合节点数量较多时的概览 |

---

## 4.3 visualize命令参数详解

`visualize`是reference_agent的子命令，用于生成可视化HTML文件。

### 4.3.1 命令语法

```bash
.venv/bin/python -m reference_agent visualize --bundle ./bundles/<name> [OPTIONS]
```

### 4.3.2 参数说明

| 参数 | 类型 | 默认值 | 必填 | 说明 |
|------|------|--------|------|------|
| `--bundle` | Path | - | 是 | Bundle根目录路径，必须是包含OKF文档的目录 |
| `--out` | Path | `<bundle>/viz.html` | 否 | 输出HTML文件路径，默认输出到Bundle根目录下的viz.html |
| `--name` | string | Bundle目录名 | 否 | 查看器标题栏显示的名称，默认使用Bundle所在目录的目录名 |

### 4.3.3 使用示例

**示例1：最简调用（使用默认输出路径和名称）**

```bash
.venv/bin/python -m reference_agent visualize \
    --bundle ./bundles/ga4
```

此命令在`./bundles/ga4/viz.html`生成可视化文件，标题显示为"ga4"。

**示例2：自定义输出路径和标题**

```bash
.venv/bin/python -m reference_agent visualize \
    --bundle ./bundles/crypto_bitcoin \
    --out /tmp/bitcoin-knowledge-graph.html \
    --name "Bitcoin Blockchain OKF Knowledge Graph"
```

此命令将可视化文件输出到`/tmp/bitcoin-knowledge-graph.html`，标题显示为自定义名称。

**示例3：完整工作流（生成Bundle后立即可视化）**

```bash
# 第一步：生成Bundle
.venv/bin/python -m reference_agent enrich \
    --source bq \
    --dataset bigquery-public-data.ga4_obfuscated_sample_ecommerce \
    --out ./bundles/ga4 \
    --no-web

# 第二步：生成可视化
.venv/bin/python -m reference_agent visualize \
    --bundle ./bundles/ga4

# 第三步：在浏览器中打开（macOS）
open ./bundles/ga4/viz.html
# 或（Linux）
xdg-open ./bundles/ga4/viz.html
# 或（Windows）
start ./bundles/ga4/viz.html
```

### 4.3.4 生成输出信息

`generate_visualization()`函数（参见 `viewer/generator.py:172-208`）执行完成后返回统计信息：

```python
{
    "concepts": N,  # 处理的概念数量（节点数）
    "edges": M,     # 图中的边数（链接数）
    "bytes": K      # 生成的HTML文件字节数
}
```

CLI运行时会打印类似以下的摘要：

```
Generated viz.html: 42 concepts, 67 edges, 156234 bytes
```

---

## 4.4 技术架构深度解析

### 4.4.1 整体生成流程

可视化文件的生成采用**构建时序列化+浏览器端渲染**架构，所有数据处理在生成阶段完成，浏览器端仅负责交互渲染：

```
┌─────────────────────────────────────────────────────────────────┐
│                    构建时（generate阶段）                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 遍历Bundle目录递归查找所有.md文件（跳过index.md）             │
│  2. 逐个解析OKFDocument，分离frontmatter和body                   │
│  3. 提取frontmatter字段（type/title/description/resource/tags等）│
│  4. 正则提取正文中的相对Markdown链接，构建邻接表                  │
│  5. 计算信任层级、过时状态等派生字段                              │
│  6. 构建图数据结构：nodes（含颜色、大小）、edges、bodies（正文）  │
│  7. 加载HTML模板，嵌入CSS、JS、bundle数据JSON                    │
│  8. 写入单个自包含HTML文件                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    运行时（浏览器端）                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 浏览器加载HTML，从CDN加载Cytoscape.js和marked.js             │
│  2. 读取window.BUNDLE获取内嵌的图数据                            │
│  3. 使用Cytoscape.js初始化力导向图实例                           │
│  4. 绑定节点点击事件：点击时渲染详情面板                          │
│  5. 使用marked.js将Markdown正文渲染为HTML                        │
│  6. 重写内部链接的点击事件，实现查看器内导航                      │
│  7. 绑定搜索框、类型筛选、布局切换的事件监听                      │
│  8. 计算并渲染反向链接列表                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.4.2 技术栈选型

可视化系统基于两个成熟的开源JavaScript库构建，均从CDN加载：

**Cytoscape.js（图渲染引擎）**

- **版本**：v3.28.1（从jsDelivr CDN加载）
- **用途**：高性能图论/网络可视化库
- **能力**：力导向布局、节点/边样式定制、交互事件处理、缩放平移、动画
- **官网**：https://js.cytoscape.org/
- **在项目中的作用**：负责知识图谱的渲染、布局计算、节点交互、缩放平移等所有图相关功能

**marked.js（Markdown渲染引擎）**

- **版本**：v12.0.0（从jsDelivr CDN加载）
- **用途**：快速的Markdown解析器和编译器
- **能力**：支持CommonMark规范、代码高亮（需额外库）、可扩展渲染器
- **官网**：https://marked.js.org/
- **在项目中的作用**：将OKF概念的Markdown正文在浏览器中实时渲染为HTML展示在详情面板

### 4.4.3 自包含HTML实现机制

可视化文件的"自包含"特性通过以下机制实现（参见 `viewer/generator.py:194-200`）：

```python
html = (
    template
    .replace("/*__VIZ_CSS__*/", css)           # 内联CSS
    .replace("/*__VIZ_JS__*/", js)             # 内联JavaScript
    .replace("__BUNDLE_NAME__", json.dumps(name))  # 嵌入Bundle名称
    .replace("__BUNDLE_DATA__", json.dumps(graph, default=str))  # 嵌入图数据JSON
)
```

**嵌入内容**：

1. **CSS样式**：`viewer/static/viz.css`的全部内容直接内联到`<style>`标签中
2. **JavaScript逻辑**：`viewer/static/viz.js`的全部内容直接内联到`<script>`标签中
3. **Bundle数据**：整个图数据（节点、边、正文、类型列表、调色板）序列化为JSON，直接赋值给`window.BUNDLE`全局变量
4. **Bundle名称**：序列化后赋值给`window.BUNDLE_NAME`全局变量

**外部依赖**：

- 仅Cytoscape.js和marked.js从CDN加载（约几百KB）
- 如需完全离线使用，可将这两个库下载到本地并修改模板中的script标签引用本地文件
- 除这两个库外无任何外部依赖，无网络请求（除CDN资源）

### 4.4.4 源代码模块结构

可视化系统的Python源代码位于`okf/src/reference_agent/viewer/`，结构清晰：

```
viewer/
├── __init__.py          # 包初始化，导出generate_visualization函数
├── generator.py         # 核心生成逻辑：遍历Bundle、构建图、渲染HTML
├── static/
│   ├── viz.css          # 查看器样式（内联到HTML中）
│   └── viz.js           # 浏览器端交互逻辑（内联到HTML中）
└── templates/
    └── viz.html         # HTML模板，包含占位符用于嵌入资源
```

**核心数据类**（`generator.py:28-44`）：

`Concept`数据类承载单个概念的所有信息，包括：
- 标识字段：`id`、`type`、`title`
- 元数据字段：`description`、`resource`、`tags`、`status`、`stale_after`
- 信任字段：`generated`、`verified`、`sources`、`trust_tier`、`stale`
- 内容字段：`body`（Markdown原文）
- 图结构字段：`links_to`（该概念链接到的其他概念ID列表）

---

## 4.5 工具箱（Toolbox）概述

`toolbox/`目录是Google官方提供的**生产级TypeScript工具集**，与`okf/`目录下的Python参考实现不同，工具箱面向企业生产环境，提供元数据即代码（Metadata as Code）和智能充实（Enrichment）能力。

```
toolbox/
├── README.md              # 工具箱总览
├── mdcode/                # Metadata as Code - 元数据即代码工具
│   ├── src/               # TypeScript源代码
│   ├── docs/              # 设计文档
│   ├── tests/             # 测试用例
│   ├── demo/              # 演示脚本
│   ├── package.json       # npm包配置
│   └── README.md          # mdcode使用文档
└── enrichment/           # Enrichment Agent - 智能充实Agent
    ├── src/               # TypeScript源代码
    ├── README.md          # enrichment使用文档
    └── package.json       # npm包配置
```

### 4.5.1 工具箱与okf/参考实现的关系

| 维度 | okf/（Python参考实现） | toolbox/（TypeScript工具箱） |
|------|----------------------|---------------------------|
| **定位** | OKF规范的概念验证（PoC） | 生产环境可用的企业级工具 |
| **语言** | Python 3.13+ | TypeScript（编译为Node.js） |
| **目标用户** | 开发者学习、原型验证 | 数据工程师、生产环境部署 |
| **核心能力** | 从BigQuery+网页抓取生成OKF Bundle，可视化 | 元数据双向同步、语义层、MCP服务器、Agent充实 |
| **平台集成** | 仅BigQuery | GCP Dataplex/Knowledge Catalog服务深度集成 |
| **分发形式** | 源码安装（pip install -e .） | 独立二进制CLI、npm库、MCP服务器 |

---

## 4.6 mdcode：元数据即代码

mdcode（Metadata as Code）是Knowledge Catalog提供的元数据管理工具，让数据管理员、数据生产者和AI Agent可以通过源代码制品的方式管理元数据和上下文工程。

### 4.6.1 核心设计理念

mdcode的核心思想是**将元数据表示为人类和Agent都友好的源代码文件**（YAML + Markdown），使用开发者熟悉的工作流（版本控制、CI/CD、PR评审）进行元数据管理。

**关键特性**：

| 特性 | 说明 |
|------|------|
| **代码化表示** | 元数据直观表示为YAML和Markdown文件，目录层次镜像数据/元数据资产的资源层次 |
| **双向同步** | 本地工作区与Catalog服务之间双向同步（pull/push），支持冲突检测 |
| **三方元数据支持** | 同时支持Google官方元数据结构和第三方/自定义元数据扩展 |
| **多形态分发** | TypeScript库、Python库、CLI工具（kcmd）、MCP服务器四种使用形态 |

### 4.6.2 目录布局与制品格式

元数据在本地工作区按标准目录结构组织，镜像云端资源层次：

```
path/to/root/
├── catalog.yaml                       # 清单文件 - 配置与范围定义
└── catalog/                           # 元数据快照目录
    └── <dir1>/
        └── <entry-id1>.yaml           # Entry YAML文件 - 结构化元数据
        └── <dir2>/
            ├── <entry-id2>.yaml       # Entry主文件
            └── <entry-id2>.aspect.md  # 侧边Markdown文件 - 非结构化文档
```

**catalog.yaml清单文件**示例：

```yaml
scope: bq-dataset.prod-data.ecommerce

aliases:
  ca-guidelines:
    aspect: data-agents-project.global.ca-guidelines
  ecommerce:
    aspect: data-agents-project.global.ecommerce

snapshot:
  entries:
    - bigquery-table
    - bigquery-view
    - entry-group
  aspects:
    - overview
    - descriptions

publishing:
  aspects:
    - overview
    - descriptions
```

**Entry YAML文件**示例（`catalog/prod-data.ecommerce/products.yaml`）：

```yaml
id: products
type: bigquery-table

resource:
  name: projects/prod-data/datasets/ecommerce/tables/products
  displayName: Products Table
  description: All products in the catalog
  labels:
    env: prod
  createTime: 2026-04-23T00:44:03Z
  updateTime: 2026-04-23T00:44:03Z

schema:
  ...  # 表结构定义

contacts:
  ...  # 联系人信息
```

**侧边Markdown文件**示例（`catalog/prod-data.ecommerce/products.overview.md`）：

```markdown
---
userManaged: true
links:
  ...
---
[overview.content]
（自由格式的Markdown文档内容）
```

### 4.6.3 语义层与BigQuery集成

mdcode内置了强大的**语义层（Semantic Layer）**能力，支持BigQuery数据集的语义建模：

**语义层核心功能**（参见 `toolbox/mdcode/src/libts/semantic/`）：

1. **语义模型加载**：从YAML定义加载度量（Measures）、维度（Dimensions）、实体（Entities）、连接（Joins）等语义对象
2. **SQL表达式工具**：`sql_expr_utils.ts`提供SQL表达式解析、操作和生成工具
3. **度量下推（Measure Lowering）**：将高层语义度量自动转换为可在BigQuery执行的SQL
4. **方言支持**：针对BigQuery SQL方言的特定优化和代码生成
5. **测试覆盖**：包含丰富的测试用例（TPC-DS、星型模式、无键维度等场景），参见 `tests/libts/semantic/fixtures/`

**BigQuery集成模块**（`src/libts/gcp/bigquery.ts`）：

- 数据集和表的元数据读取
- 直接执行语义模型生成的SQL查询
- 与Dataplex Catalog API的深度集成
- 通过gcloud ADC（Application Default Credentials）认证

### 4.6.4 MCP服务器能力

mdcode内置MCP（Model Context Protocol）服务器，可直接为AI Agent提供元数据操作工具：

**MCP配置**：在MCP设置文件中添加以下配置即可使用：

```json
{
  "mcpServers": {
    "kc-mac": {
      "command": "kcmd",
      "args": ["mcp", "--path", "/path/to/root"]
    }
  }
}
```

**MCP提供的工具**：

| 工具名 | 功能 |
|--------|------|
| `pull` | 从Catalog服务拉取最新元数据到本地 |
| `push` | 将本地修改的元数据推送到Catalog服务 |
| `list-entries` | 列出当前快照中的所有Entry |
| `lookup-entry` | 查找指定Entry及其元数据 |
| `modify-entry` | 修改快照中的Entry及其元数据 |

MCP服务器同样使用gcloud ADC认证，与CLI保持一致的认证方式。

### 4.6.5 CLI命令详解（kcmd）

mdcode提供`kcmd`命令行工具，分发为独立二进制文件。

**常用命令**：

| 命令 | 功能 |
|------|------|
| `kcmd init` | 初始化新的目录快照 |
| `kcmd pull` | 从Knowledge Catalog服务拉取最新元数据 |
| `kcmd push` | 将本地更改推送到Knowledge Catalog服务 |
| `kcmd status` | 检查本地修改状态 |
| `kcmd mcp` | 启动MCP服务器 |

**init命令参数**：

```bash
# 初始化单个BigQuery数据集
kcmd init --bigquery-dataset <projectId>.<datasetId>

# 初始化多个BigQuery数据集
kcmd init --bigquery-dataset <project>.<ds1> --bigquery-dataset <project>.<ds2>

# 指定Entry类型和Aspect类型初始化
kcmd init --bigquery-dataset <project>.<dataset> \
  --entry bigquery-table --entry bigquery-view \
  --aspect overview --aspect description

# 初始化自定义EntryGroup
kcmd init --entry-group <projectId>.<locationId>.<entryGroupId>
```

**pull命令**：

```bash
# 拉取最新元数据（自动检测冲突）
kcmd pull

# 空运行（预览变更但不应用）
kcmd pull --dry-run
```

pull命令会报告冲突：如果存在尚未推送到Catalog的本地更改，将列出冲突项。

**push命令**：

```bash
# 推送本地更改
kcmd push

# 空运行（预览将推送的内容）
kcmd push --dry-run
```

push命令遵循乐观并发控制：仅推送自上次pull以来的本地更改，如果云端元数据在此期间被修改则推送失败，需要先pull解决冲突后再push。

### 4.6.6 TypeScript库使用

mdcode也可作为TypeScript库直接在代码中调用：

```typescript
import * as kcmd from 'kcmd';

// 从头创建Catalog清单
const manifest = new kcmd.CatalogManifest(...);
manifest.save('/path/to/root');

// 从文件系统加载Catalog快照
const snapshot = kcmd.CatalogSnapshot.fromPath('/path/to/root');

// 从Catalog服务拉取最新元数据
const pullResult = await snapshot.pull();
if (pullResult.success) {
  console.log('Metadata pulled successfully');
} else {
  console.error('Metadata pull failed:', pullResult.error);
}

// 将修改后的元数据推送到Catalog服务
const pushResult = await snapshot.push();
if (pushResult.success) {
  console.log('Metadata pushed successfully');
} else {
  console.error('Metadata push failed:', pushResult.error);
}
```

---

## 4.7 enrichment：智能充实Agent

enrichment是Knowledge Catalog提供的可定制Agentic工作流工具，用于从各种来源提取信息，构建数据资产的元数据文档，供AI Agent作为上下文使用。

### 4.7.1 定位与依赖关系

enrichment Agent定位为**元数据生产工具**，它依赖mdcode能力：

1. 首先使用`kcmd`从Catalog服务拉取元数据快照
2. enrichment Agent读取本地元数据和配置的知识源
3. Agent使用LLM自动生成和充实文档
4. 充实后的元数据可通过`kcmd push`推送回Catalog服务

### 4.7.2 CLI工具（kcagent）

enrichment提供`kcagent` CLI工具，分发为独立二进制文件。

**典型工作流**：

```bash
# 步骤1：初始化BigQuery数据集的目录快照
kcmd init --bigquery-dataset <projectId>.<datasetId>

# 步骤2：从Knowledge Catalog服务拉取最新元数据
kcmd pull

# 步骤3：运行enrichment工具
kcagent enrich --catalog-path . --tools-path tools --prompt-path prompt.md
```

**enrich命令参数**：

| 参数 | 说明 |
|------|------|
| `--catalog-path` | 元数据快照目录路径（包含catalog.yaml的目录） |
| `--tools-path` | MCP工具配置和Skills目录路径 |
| `--prompt-path` | 自定义充实提示词文件路径 |

### 4.7.3 TypeScript实现架构

enrichment的TypeScript源代码位于`toolbox/enrichment/src/`：

```
src/
├── agent/
│   ├── enrich/
│   │   ├── agent.ts      # Agent核心逻辑
│   │   └── command.ts    # enrich命令实现
│   ├── utils/
│   │   ├── patchadk.ts   # ADK（Agent Development Kit）补丁
│   │   └── patchpb.ts    # Protocol Buffers补丁
│   ├── main.ts           # Agent入口
│   └── tools.ts          # Agent工具注册
└── tools/
    └── md/
        ├── fileset.ts    # Markdown文件集工具实现
        ├── main.ts       # fileset MCP服务器入口
        └── server.ts     # MCP服务器实现
```

**内置MCP服务器：md-fileset**

enrichment内置了`md-fileset` MCP服务器，提供从Markdown文件目录层次提取信息的能力：

| 工具名 | 功能 |
|--------|------|
| `list_fileset_contents` | 浏览目录树，列出指定路径的内容（文件或子目录） |
| `read_fileset_file` | 读取知识库中文件的完整内容，提取相关信息 |
| `search_fileset_content` | 搜索知识库，返回匹配文件、行号和代码片段 |

**md-fileset配置示例**（`tools/mcp.json`）：

```json
{
  "mcpServers": {
    "md-fileset": {
      "command": "../dist/md-fileset",
      "args": ["--dir", "fileset"]
    }
  }
}
```

**Skill配置示例**（`tools/skills/fileset-source/SKILL.md`）：

```markdown
---
name: fileset-source
description: >
  Use the fileset source to find relevant markdown documents and extract information
  about assets.
---

The `md-fileset` mcp server provides the following tools to extract relevant
information from a directory hierarchy of markdown files:

* **list_fileset_contents** - browse and navigate the directory tree to list the
  contents of the specified path.

* **read_fileset_file** - read the contents of a file in the knowledge base.

* **search_fileset_content** - searches the knowledge base and returns the matching files.

To work with a fileset effectively create search queries (use simple keyword queries
with individual tokens) to find relevant files, and then read the files to find relevant information.
```

---

## 4.8 官方样例项目（Samples）

Knowledge Catalog仓库提供了多个开箱即用的样例，每个样例都包含**配方（Recipe）**和**生成的Bundle**两部分。配方是运行参考Agent的精确命令和种子文件，Bundle是运行后生成的可直接浏览结果。

### 4.8.1 okf/目录下的参考样例

`okf/samples/`目录包含三个官方数据集样例配方，`okf/bundles/`目录包含对应的已生成Bundle（含viz.html可视化文件）。

#### 样例1：GA4 Google Merchandise Store（GA4电商数据集）

| 项 | 说明 |
|----|------|
| **数据源** | `bigquery-public-data.ga4_obfuscated_sample_ecommerce` - Google Merchandise Store的GA4 BigQuery导出数据 |
| **特点** | 单个非规范化事件表（`events_`），典型的电商事件数据 |
| **Web种子** | GA4 BigQuery Export官方文档URL |
| **配方位置** | `okf/samples/ga4_merch_store/README.md` |
| **Bundle位置** | `okf/bundles/ga4/` |
| **可视化** | `okf/bundles/ga4/viz.html` |

**运行命令**：
```bash
.venv/bin/python -m reference_agent enrich \
    --source bq \
    --dataset bigquery-public-data.ga4_obfuscated_sample_ecommerce \
    --web-seed-file samples/ga4_merch_store/seeds.txt \
    --out ./bundles/ga4
```

**输出内容**：
- 数据集文档 + `events_`表文档（含完整Schema、分区信息、常见查询模式）
- 从GA4官方文档自动生成的参考文档（指标定义、字段说明等）
- 各级目录自动生成的index.md
- 知识图谱可视化文件viz.html

#### 样例2：Stack Overflow公开数据集

| 项 | 说明 |
|----|------|
| **数据源** | `bigquery-public-data.stackoverflow` - Stack Exchange Data Dump的镜像 |
| **特点** | 多个独立实体表（`posts_questions`、`posts_answers`、`users`、`votes`、`comments`、`badges`、`tags`、`post_history`、`post_links`等） |
| **核心练习点** | **多概念充实**：单个Schema文档页面通常描述多个表，Web Agent每页需要更新多个Concept |
| **Web种子** | Stack Exchange社区维护的权威Schema引用 |
| **配方位置** | `okf/samples/stackoverflow/README.md` |
| **Bundle位置** | `okf/bundles/stackoverflow/` |
| **可视化** | `okf/bundles/stackoverflow/viz.html` |

**注意事项**：Stack Overflow表数据量较大，迭代开发时建议保持`--web-max-pages`适中，并使用`--concept`参数单概念调试。

**运行命令**：
```bash
.venv/bin/python -m reference_agent enrich \
    --source bq \
    --dataset bigquery-public-data.stackoverflow \
    --web-seed-file samples/stackoverflow/seeds.txt \
    --out ./bundles/stackoverflow
```

#### 样例3：Bitcoin（crypto_bitcoin）区块链数据集

| 项 | 说明 |
|----|------|
| **数据源** | `bigquery-public-data.crypto_bitcoin` - 开源`bitcoin-etl`管道生成的比特币区块链数据 |
| **特点** | 一小组紧密关联的事实表：`blocks`（区块）、`transactions`（交易）、`inputs`（输入）、`outputs`（输出），通过外键紧密关联 |
| **核心练习点** | **跨表外键关系**：`transactions`表每行引用`blocks`、`inputs`、`outputs`中的行，适合观察Agent如何在文档中展示表间关系 |
| **Web种子** | blockchain-etl权威Schema源、Google Cloud官方区块链BigQuery发布公告 |
| **配方位置** | `okf/samples/crypto_bitcoin/README.md` |
| **Bundle位置** | `okf/bundles/crypto_bitcoin/` |
| **可视化** | `okf/bundles/crypto_bitcoin/viz.html` |

**注意事项**：`crypto_bitcoin`表数据量极大（`transactions`表约数百GB），迭代开发时建议使用`--concept`参数做冒烟测试。

**运行命令**：
```bash
.venv/bin/python -m reference_agent enrich \
    --source bq \
    --dataset bigquery-public-data.crypto_bitcoin \
    --web-seed-file samples/crypto_bitcoin/seeds.txt \
    --out ./bundles/crypto_bitcoin
```

#### 额外样例：Acme Retail（虚构零售公司）

| 项 | 位置 | 说明 |
|----|------|------|
| Bundle | `okf/bundles/acme_retail/` | 虚构零售公司示例Bundle，包含metrics（指标）、computations（计算逻辑）、policies（政策）、attesters（验证者）、skills（技能）、tables（表）等完整目录结构，是一个更贴近企业实际使用的示例 |
| 可视化 | `okf/bundles/acme_retail/viz.html` | 可直接打开查看企业级知识图谱结构 |

Acme Retail示例特别值得研究，因为它展示了OKF在企业场景中的扩展用法：
- **metrics/**：业务指标定义（gross-margin、revenue等）
- **computations/**：指标计算逻辑文档
- **policies/**：业务政策（收入确认政策、毛利标准等）
- **skills/**：Agent可使用的技能文档（如run-on-bq）
- **attesters/**：验证者和验证脚本（如SQL相等性验证）

### 4.8.2 samples/目录下的通用样例

`samples/`目录（仓库根目录下，非okf/下）包含工具箱的使用演示：

| 样例 | 目录 | 说明 |
|------|------|------|
| **Discovery** | `samples/discovery/` | 演示如何基于Catalog提供的搜索API构建搜索和发现Agent |
| **Enrichment** | `samples/enrichment/` | 完整的enrichment工具端到端演示，包含创建BigQuery数据集、Dataplex EntryGroup、拉取元数据、配置MCP工具和Skills、运行充实Agent的完整流程 |

---

## 4.9 本章小结与延伸阅读

### 4.9.1 关键要点总结

**可视化系统**：

1. **单文件分发**：生成的viz.html是完全自包含的HTML文件，所有数据内嵌，零后端、零安装即可查看
2. **Cytoscape.js + marked.js技术栈**：成熟的开源库保证渲染性能和稳定性
3. **构建时处理**：所有数据解析、链接提取、图构建在生成阶段完成，浏览器端仅负责交互
4. **丰富交互**：力导向图、详情面板、反向链接、搜索、类型筛选、多种布局切换
5. **概念验证消费者**：可视化是OKF的PoC消费者，证明OKF格式可被通用工具消费，无需特殊SDK

**工具箱（mdcode + enrichment）**：

1. **生产级TypeScript实现**：与Python参考实现不同，面向企业生产环境设计
2. **mdcode元数据即代码**：将元数据表示为YAML+Markdown文件，支持Git工作流、PR评审、CI/CD
3. **双向同步**：pull/push命令实现本地工作区与GCP Knowledge Catalog服务的双向同步，支持冲突检测
4. **语义层能力**：内置语义建模和SQL生成，支持度量、维度、连接等高层语义对象
5. **MCP原生支持**：mdcode提供MCP服务器，AI Agent可直接通过标准MCP协议操作元数据
6. **enrichment智能充实**：可定制Agent工作流，自动从各种来源提取信息充实元数据文档

**官方样例**：

1. **GA4电商**：单一大表场景，适合入门
2. **Stack Overflow**：多表场景，练习多概念充实
3. **比特币区块链**：紧密关联表场景，观察跨表关系文档化
4. **Acme Retail**：企业级扩展场景，展示metrics/policies/skills等高级用法

### 4.9.2 交叉引用与延伸阅读

**OKF Wiki相关章节**：

- OKF可视化理念与"图状而非树状"设计：[okf-wiki 01 核心概念与设计哲学](../okf-wiki/01-core-concepts.md)
- OKF纯文本、Git原生特性如何支撑工具链：[okf-wiki 00 OKF概述与知识地图](../okf-wiki/00-overview.md)
- 手工创建OKF Bundle的快速入门：[okf-wiki 02 5分钟快速入门](../okf-wiki/02-quickstart.md)

**Knowledge Catalog Wiki相关章节**：

- 参考Agent（生产者）实现原理：[03 参考Agent实现原理与运行指南](./03-reference-agent.md)
- OKF规范中links字段和图结构定义：[02 OKF开放知识格式规范深度解析](./02-okf-specification.md)
- 样例Bundle深度剖析：[05 示例Bundle深度解析](./05-samples-and-bundles.md)（下一章）
- 企业集成模式与最佳实践：[06 集成模式与最佳实践](./06-integration-patterns.md)

**官方资源**：

- 官方GitHub仓库：https://github.com/googlecloudplatform/knowledge-catalog
- 可视化源码：`okf/src/reference_agent/viewer/`
- mdcode源码：`toolbox/mdcode/`
- enrichment源码：`toolbox/enrichment/`

---

| 上一章 | 目录 | 下一章 |
|--------|------|--------|
| [03 参考Agent实现原理与运行指南](./03-reference-agent.md) | [README](./README.md) | [05 示例Bundle深度解析](./05-samples-and-bundles.md) |
