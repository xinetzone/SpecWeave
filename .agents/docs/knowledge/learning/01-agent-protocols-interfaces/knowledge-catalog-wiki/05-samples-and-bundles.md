---
id: "knowledge-catalog-wiki-samples-bundles"
title: "05 示例Bundle深度解析"
version: "1.0"
source: "GoogleCloudPlatform/knowledge-catalog okf/bundles/ + okf/samples/ 深度解析"
type: "Wiki Tutorial"
description: "对Knowledge Catalog官方提供的4个示例Bundle（GA4电商、Stack Overflow、比特币区块链、Acme Retail企业级）进行深度结构解析；详解okf/samples/目录下的recipe配方与Bundle的对应关系；分析每个Bundle覆盖的OKF特性与学习价值"
tags: ["Knowledge Catalog", "OKF", "Bundle", "Sample", "GA4", "Stack Overflow", "Bitcoin", "Acme Retail", "Attested Computation", "Recipe"]
category: "learning"
date: "2026-08-06"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "深度解析Google官方提供的4个OKF示例Bundle：GA4电商数据集演示单表+指标文档结构，Stack Overflow演示多表+joins+枚举引用，比特币区块链演示紧密关联表+跨表外键关系，Acme Retail演示企业级Attested Computation完整用法（metrics/computations/policies/skills/attesters）；同时详解okf/samples/目录下recipe配方与Bundle的对应关系，帮助读者通过实例掌握OKF规范"
last_verified: "2026-08-06"
wiki_version: "1.0"
okf_version_target: "v0.2"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/knowledge/learning/01-agent-protocols-interfaces/knowledge-catalog-wiki/05-samples-and-bundles.toml"
---

# 05 示例Bundle深度解析

> **本章定位说明**
> - 前四章分别介绍了Knowledge Catalog平台概述（[00 概述与知识地图](./00-overview.md)）、核心概念与架构（[01 核心概念与平台架构](./01-core-concepts.md)）、OKF规范（[02 OKF规范深度解析](./02-okf-specification.md)）、参考Agent实现（[03 参考Agent实现原理与运行指南](./03-reference-agent.md)）和工具链与可视化（[04 工具链与可视化系统](./04-toolchain-and-visualization.md)）。
> - 本章聚焦**官方示例Bundle的深度剖析**——通过逐个拆解4个由浅入深的官方示例，读者可以直观理解OKF Bundle的实际组织结构、不同类型概念的文档写法、交叉链接的建立方式，以及企业级高级特性（如Attested Computation）的完整落地形态。
> - 所有示例Bundle均位于 `okf/bundles/` 目录下，每个Bundle都已预先生成了 `viz.html` 可视化文件，读者可直接在浏览器中打开查看交互式知识图谱。

---

## 5.1 samples/配方与bundles/产物的对应关系

在深入解析每个Bundle之前，首先需要理解**配方（Recipe）**与**Bundle产物**的对应关系。Knowledge Catalog采用"配方驱动生成"的设计：`okf/samples/` 目录存放可复现的配方（包含运行命令、种子URL列表、前置条件说明），`okf/bundles/` 目录存放运行配方后生成的OKF Bundle产物。

### 5.1.1 目录结构总览

```
okf/
├── samples/                     # 配方目录（可复现实验）
│   ├── ga4_merch_store/         # GA4电商数据集配方
│   │   ├── README.md            # 运行说明、前置条件、命令示例
│   │   └── seeds.txt            # Web抓取种子URL列表
│   ├── stackoverflow/           # Stack Overflow数据集配方
│   │   ├── README.md
│   │   └── seeds.txt
│   └── crypto_bitcoin/          # 比特币区块链数据集配方
│       ├── README.md
│       └── seeds.txt
└── bundles/                     # 生成产物目录（可直接浏览）
    ├── ga4/                     # ← 对应 ga4_merch_store 配方
    ├── stackoverflow/           # ← 对应 stackoverflow 配方
    ├── crypto_bitcoin/          # ← 对应 crypto_bitcoin 配方
    └── acme_retail/             # 企业级手工编写示例（无对应自动生成配方）
```

### 5.1.2 配方文件构成

每个自动生成的配方目录包含两个核心文件：

| 文件 | 作用 | 内容示例 |
|------|------|----------|
| `README.md` | 配方说明书 | 前置条件（Python环境、gcloud认证、Gemini凭证）、完整运行命令、参数说明（`--concept`单概念调试、`--no-web`跳过Web抓取、`--web-max-pages`页面预算）、输出说明 |
| `seeds.txt` | Web抓取种子 | 每行一个URL，注释行以`#`开头；Web Agent从这些URL开始，沿着相关链接向外爬取，自动生成Reference概念文档 |

### 5.1.3 通用运行工作流

所有三个自动生成配方遵循相同的工作流：

```bash
# 步骤1：环境准备（所有配方通用）
python3.13 -m venv .venv
.venv/bin/pip install --index-url https://pypi.org/simple/ -e .[dev]
gcloud auth application-default login
gcloud config set project <your-billing-project>
# 配置Gemini凭证（二选一）
# 选项A：AI Studio
export GEMINI_API_KEY=<your-key>
# 选项B：Vertex AI
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT=<project-id>
export GOOGLE_CLOUD_LOCATION=<region>

# 步骤2：运行enrich命令生成Bundle
.venv/bin/python -m reference_agent enrich \
    --source bq \
    --dataset <dataset-id> \
    --web-seed-file samples/<recipe>/seeds.txt \
    --out ./bundles/<bundle-name>

# 步骤3：（可选）生成可视化HTML
.venv/bin/python -m reference_agent visualize \
    --bundle ./bundles/<bundle-name>
```

### 5.1.4 四个Bundle的难度递进关系

四个示例按照从简单到复杂、从基础到企业级的顺序排列：

| 序号 | Bundle名称 | 类型 | 核心特点 | 学习难度 |
|------|-----------|------|---------|---------|
| 1 | **ga4** | 自动生成 | 单一大表（events_*分片表）+ 指标引用文档 | ★☆☆ 入门 |
| 2 | **stackoverflow** | 自动生成 | 多独立实体表 + joins路径 + 枚举引用（许可证/投票类型）+ 指标 | ★★☆ 进阶 |
| 3 | **crypto_bitcoin** | 自动生成 | 紧密关联事实表 + 跨表外键关系文档化 | ★★☆ 进阶 |
| 4 | **acme_retail** | 手工编写 | 企业级完整场景：Attested Computation、政策、技能、验证者 | ★★★ 高级 |

---

## 5.2 Bundle 1：ga4 - GA4电商数据集

**位置**：`okf/bundles/ga4/`
**对应配方**：`okf/samples/ga4_merch_store/`
**数据源**：`bigquery-public-data.ga4_obfuscated_sample_ecommerce`
**可视化**：`okf/bundles/ga4/viz.html`

### 5.2.1 目录结构

```
ga4/
├── index.md                     # Bundle根目录索引（自动生成）
├── viz.html                     # 知识图谱可视化文件
├── datasets/
│   ├── index.md                 # datasets目录索引
│   └── ga4_obfuscated_sample_ecommerce.md  # 数据集文档
├── tables/
│   ├── index.md                 # tables目录索引
│   └── events_.md               # events_*分片表文档
└── references/
    ├── index.md                 # references目录索引
    └── metrics/
        ├── index.md             # metrics目录索引
        ├── acquired_users.md    # 获客用户指标
        ├── frequently_active_users.md  # 频繁活跃用户指标
        ├── google_acquired_cohorts.md  # Google获客群组指标
        ├── highly_active_users.md      # 高活跃用户指标
        ├── n_day_active_users.md       # N日活跃用户指标
        ├── n_day_inactive_users.md     # N日不活跃用户指标
        └── purchasers.md               # 购买用户指标
```

### 5.2.2 结构特点

ga4 Bundle是**最简单的入门示例**，结构清晰，适合第一个学习：

1. **三层标准目录结构**：严格遵循OKF推荐的 `datasets/` → `tables/` → `references/` 三层组织
2. **单数据集单表**：仅包含一个数据集和一个分片表族（`events_*`），没有复杂的多表关系
3. **指标文档集中管理**：所有业务指标（7个受众细分指标）统一放在 `references/metrics/` 子目录下
4. **自动生成的index.md**：每个目录层级都有自动生成的索引页，列出子目录和文件并附带简要说明

### 5.2.3 核心概念文档解析

#### 数据集文档（datasets/ga4_obfuscated_sample_ecommerce.md）

该文档演示了 `type: BigQuery Dataset` 类型概念的标准写法：

- **frontmatter关键字段**：
  - `resource`：BigQuery Dataset API的完整URL
  - `tags`：包含`ga4`、`ecommerce`、`analytics`等领域标签
  - `generated`：记录生成Agent和时间戳
  - `sources`：列出信息来源（BigQuery元数据API + GA4官方文档），每个来源有`id`、`resource`、`title`
- **正文结构**：
  - 数据集概述（来源、时间范围、用途）
  - Schema说明（Dataset作为命名空间，本身无扁平列Schema，仅包含表）
  - 包含的表列表（链接到tables/events_.md）
  - Common query patterns（常用查询模式，附带可执行SQL示例）
  - 脚注引用（使用`[^id]`语法引用sources中的来源）

#### 表文档（tables/events_.md）

该文档演示了 `type: BigQuery Table` 类型概念的标准写法：

- **分片表表示**：`resource`字段使用通配符`events_*`表示分片表族
- **完整Schema表格**：使用Markdown表格详细列出所有字段（Field Name、Type、Mode、Description），嵌套字段使用缩进表示（如`*event_params.key*`）
- **嵌套/重复字段说明**：特别标注`event_params`和`items`是REPEATED RECORD类型，需要UNNEST操作
- **与数据集的交叉链接**：正文中链接回`../datasets/ga4_obfuscated_sample_ecommerce.md`

#### 指标文档（references/metrics/acquired_users.md）

该文档演示了 `type: Reference` 类型概念的标准写法：

- **指标定义**：清晰说明"Acquired Users"是通过特定Source/Medium/Campaign获客的用户
- **可执行SQL**：在"Common query patterns"中提供完整可运行的SQL示例
- **来源引用**：链接到Google Analytics官方帮助文档
- **与表的关联**：SQL中引用`YOUR_TABLE.events_*`，隐含与events_表的关联

### 5.2.4 覆盖的OKF特性

| OKF特性 | 覆盖情况 | 说明 |
|---------|---------|------|
| YAML frontmatter | ✅ 完整覆盖 | type/resource/title/description/tags/generated/sources等核心字段 |
| 相对路径交叉链接 | ✅ 完整覆盖 | 数据集↔表、指标→表之间的双向链接 |
| 自动生成index.md | ✅ 完整覆盖 | 每个目录层级都有自动索引 |
| sources与脚注引用 | ✅ 完整覆盖 | 使用`[^id]`语法在正文引用来源 |
| Common query patterns | ✅ 完整覆盖 | 数据集和指标文档都提供SQL示例 |
| 多类型概念 | ✅ 覆盖3种 | BigQuery Dataset、BigQuery Table、Reference |
| tags分类 | ✅ 完整覆盖 | 每个概念都有领域相关标签 |

### 5.2.5 学习价值

ga4 Bundle是OKF入门的最佳起点：

1. **结构简单清晰**：没有复杂的目录嵌套，三层结构一目了然
2. **概念类型少**：仅包含3种核心类型（Dataset、Table、Reference），容易理解
3. **真实业务场景**：GA4是数据分析领域最常用的数据集之一，读者可直接对照自己的GA4导出数据
4. **文档范式标准**：每个类型的文档都写得非常规范，可直接作为模板复制
5. **可视化效果直观**：打开viz.html可以看到清晰的星型结构——数据集在中心，表和指标围绕在周围

### 5.2.6 动手练习建议

1. 打开 `ga4/viz.html`，观察节点颜色区分（Dataset紫色、Table蓝色、Reference绿色）
2. 点击 `ga4_obfuscated_sample_ecommerce` 节点，查看详情面板中的反向链接（Cited by）
3. 阅读 `tables/events_.md`，对比BigQuery控制台中的真实Schema
4. 尝试在BigQuery中运行 `references/metrics/acquired_users.md` 中的SQL示例

---

## 5.3 Bundle 2：stackoverflow - Stack Overflow公开数据集

**位置**：`okf/bundles/stackoverflow/`
**对应配方**：`okf/samples/stackoverflow/`
**数据源**：`bigquery-public-data.stackoverflow`
**可视化**：`okf/bundles/stackoverflow/viz.html`

### 5.3.1 目录结构

```
stackoverflow/
├── index.md                     # Bundle根目录索引
├── viz.html                     # 知识图谱可视化
├── datasets/
│   ├── index.md
│   └── stackoverflow.md         # Stack Overflow数据集文档
├── tables/
│   ├── index.md
│   ├── badges.md                # 徽章表
│   ├── comments.md              # 评论表
│   ├── post_history.md          # 帖子历史表
│   ├── post_links.md            # 帖子链接表
│   ├── posts_answers.md         # 回答帖子表
│   ├── posts_moderator_nomination.md  # 版主任命表
│   ├── posts_orphaned_tag_wiki.md     # 孤立标签维基表
│   ├── posts_privilege_wiki.md        # 权限维基表
│   ├── posts_questions.md       # 问题帖子表
│   ├── posts_tag_wiki.md        # 标签维基表
│   ├── posts_tag_wiki_excerpt.md # 标签维基摘要表
│   ├── posts_wiki_placeholder.md # 维基占位符表
│   ├── stackoverflow_posts.md   # 通用帖子表
│   ├── tags.md                 # 标签表
│   ├── users.md                # 用户表
│   └── votes.md                # 投票表
└── references/
    ├── index.md
    ├── content_licenses.md     # 内容许可证引用（枚举查找表）
    ├── post_types.md           # 帖子类型枚举
    ├── vote_types.md           # 投票类型枚举
    ├── joins/                  # 表连接路径
    │   ├── index.md
    │   ├── comments__posts.md
    │   ├── post_links__posts.md
    │   ├── posts__votes.md
    │   └── posts_answers__posts_questions.md
    └── metrics/                # 社区健康指标
        ├── index.md
        ├── accepted_answer_rate.md  # 接受回答率
        └── bad_question_flag_ratio.md # 坏问题标记率
```

### 5.3.2 结构特点

stackoverflow Bundle演示了**多独立实体+关系文档化**的场景，相比ga4复杂度明显提升：

1. **多表结构**：包含16个表，覆盖Stack Overflow的所有核心实体（问题、回答、用户、投票、评论、徽章、标签等）
2. **joins子目录**：专门的 `references/joins/` 目录存放表间连接路径，每个join一个独立文档
3. **枚举引用文档**：`content_licenses.md`、`post_types.md`、`vote_types.md` 作为枚举查找表，不对应数据库表，而是提供枚举值到业务含义的映射
4. **多概念充实特性**：这是该配方的核心练习点——单个Schema文档页面通常描述多个表，Web Agent需要在一次页面抓取后更新多个Concept

### 5.3.3 核心概念文档解析

#### 枚举引用文档（references/content_licenses.md）

这是stackoverflow Bundle最有特色的文档类型，演示了如何用OKF表示**非表型参考数据**：

- **type: Reference**：与ga4中的指标相同类型，但用途不同——它不是SQL查询模式，而是业务枚举的查找表
- **表格化枚举值**：使用Markdown表格清晰列出所有枚举值：
  - ContentLicense Value（数据库中存储的值）
  - Date Start / Date End（生效时间范围）
  - License Link（许可证官方URL）
- **历史版本追溯**：CC BY-SA 2.5 → 3.0 → 4.0的许可证演进历史完整记录
- **价值**：Agent在查询数据时遇到`ContentLicense`字段，可以自动链接到该文档理解字段含义，无需硬编码枚举值

#### Join路径文档（references/joins/posts_answers__posts_questions.md）

这是stackoverflow Bundle引入的新概念类型，用于文档化**表间外键关系**：

```markdown
---
type: Reference
title: Posts Answers ↔ Posts Questions Join
description: Join path between posts_answers and posts_questions tables.
tags: [join, posts, answers, questions]
---

# posts_answers ↔ posts_questions

Join relationship between Stack Overflow questions and their answers.

```sql
ON posts_answers.parent_id = posts_questions.id
```

## Usage

Use this join path to correlate answers directly back to their parent questions
to aggregate answer counts, verify metrics like Accepted Answer rate, or compare
question/answer scores.
```

- **命名约定**：使用双下划线`__`连接两个表名（如`posts_answers__posts_questions`），清晰表达关系方向
- **最小必要信息**：只包含JOIN条件（核心SQL片段）和使用场景说明，不重复表Schema
- **交叉链接价值**：Agent在生成跨表查询时，可以自动发现和使用这些预定义的join路径，避免错误的连接条件

#### 指标文档（references/metrics/accepted_answer_rate.md）

与ga4中的指标不同，stackoverflow的指标演示了**基于多表join的聚合计算**：

```sql
SAFE_DIVIDE(
  COUNT(AcceptedAnswerId),
  COUNT(Id)
)
```

- 使用`SAFE_DIVIDE`处理除零情况
- 隐含了对`posts_questions`表的引用（`AcceptedAnswerId`和`Id`都是该表字段）
- 指标定义简洁明了，配合join文档可组合出完整查询

### 5.3.4 覆盖的OKF特性

| OKF特性 | 覆盖情况 | 说明 |
|---------|---------|------|
| 多表组织 | ✅ 完整覆盖 | 16个表的独立文档，规模接近真实项目 |
| joins子目录 | ✅ 新增特性 | 专门目录存放表间连接路径，每个join独立文档 |
| 枚举引用文档 | ✅ 新增特性 | 非表型参考数据（许可证、类型枚举）的文档化 |
| 多概念充实 | ✅ 核心练习点 | 单Web页面更新多个Concept的能力 |
| 命名约定 | ✅ 完整覆盖 | join文档使用`表A__表B.md`命名约定 |
| 多对多关系 | ✅ 覆盖 | post_links等多对多关系表的文档化 |

### 5.3.5 学习价值

stackoverflow Bundle适合从入门到进阶的过渡学习：

1. **理解大规模Bundle的组织方式**：当有十几个甚至几十个表时，如何通过目录结构和index.md保持可导航性
2. **掌握表间关系的文档化方法**：joins目录的设计模式可直接套用到自己的项目中
3. **学习非表型概念的表示**：枚举值、查找表、状态码等参考数据如何用OKF表示
4. **理解多概念充实**：Web Agent如何从单个文档页面提取信息更新多个Concept
5. **真实的社区数据模型**：Stack Overflow的数据模型是公开数据集的经典设计，具有很高的参考价值

### 5.3.6 动手练习建议

1. 打开 `stackoverflow/viz.html`，观察比ga4复杂得多的图结构——16个表节点+多个join节点+指标节点
2. 点击 `posts_questions` 节点，查看Cited by列表——可以看到哪些join和指标引用了它
3. 对比 `content_licenses.md` 与表文档的区别——理解Reference类型的多种用途
4. 尝试组合 `accepted_answer_rate` 指标 + `posts_answers__posts_questions` join，写出完整的查询SQL

---

## 5.4 Bundle 3：crypto_bitcoin - 比特币区块链数据集

**位置**：`okf/bundles/crypto_bitcoin/`
**对应配方**：`okf/samples/crypto_bitcoin/`
**数据源**：`bigquery-public-data.crypto_bitcoin`
**可视化**：`okf/bundles/crypto_bitcoin/viz.html`

### 5.4.1 目录结构

```
crypto_bitcoin/
├── index.md                     # Bundle根目录索引
├── viz.html                     # 知识图谱可视化
├── datasets/
│   ├── index.md
│   └── crypto_bitcoin.md        # 比特币区块链数据集文档
├── tables/
│   ├── index.md
│   ├── blocks.md                # 区块表
│   ├── transactions.md          # 交易表
│   ├── inputs.md                # 交易输入表（扁平化）
│   └── outputs.md               # 交易输出表（扁平化）
└── references/
    ├── index.md
    ├── joins/                   # 跨表外键关系
    │   ├── index.md
    │   ├── blocks___transactions.md    # 区块→交易（三下划线）
    │   ├── inputs___transactions.md    # 输入→交易
    │   └── outputs___transactions.md   # 输出→交易
    └── metrics/
        ├── index.md
        └── duplicate_transactions.md  # 重复交易异常检测指标
```

### 5.4.2 结构特点

crypto_bitcoin Bundle演示了**紧密关联事实表+外键关系深度文档化**的场景：

1. **表数量少但关系紧密**：仅4个核心表（blocks、transactions、inputs、outputs），但通过外键形成紧密的关联网络
2. **三下划线命名约定**：join文档使用三下划线`___`（区别于stackoverflow的双下划线），表示**一对多/多对一的从属关系**而非简单关联：
   - `blocks___transactions`：一个区块包含多个交易
   - `transactions___inputs`：一个交易包含多个输入（注意：实际文件名是`inputs___transactions.md`，从从属方指向主方）
3. **嵌套与扁平化并存**：`transactions`表中包含嵌套的`inputs`和`outputs` RECORD字段，同时也提供扁平化的独立`inputs`和`outputs`表，文档中明确说明这两种表示的关系
4. **分区表文档化**：特别说明`transactions`表按`block_timestamp_month`分区，以及查询时的分区裁剪注意事项

### 5.4.3 核心概念文档解析

#### 交易表文档（tables/transactions.md）节选

该文档的亮点在于**清晰说明表间关系和嵌套/扁平化的设计选择**：

> This table links directly to several sibling tables in the crypto_bitcoin dataset, such as blocks. While inputs and outputs are nested as repeated records here, they are also flattened into dedicated sibling tables: inputs and outputs.

- **显式关系说明**：明确指出与哪些兄弟表有直接关联
- **设计权衡说明**：解释为什么同时存在嵌套字段和独立扁平化表——嵌套字段适合单交易内快速访问，扁平化表适合跨交易聚合分析
- **完整Schema细节**：对inputs和outputs嵌套字段的每个子字段都有详细说明
- **分区策略文档化**：专门说明`block_timestamp_month`分区字段的作用

#### Join路径文档（references/joins/blocks___transactions.md）

与stackoverflow的join相比，比特币的join文档更加**业务导向**，不仅给出JOIN条件，还说明业务用途：

```sql
SELECT
  b.number AS block_height,
  b.hash AS block_hash,
  b.timestamp AS block_timestamp,
  t.hash AS transaction_hash,
  t.fee AS transaction_fee
FROM
  `bigquery-public-data.crypto_bitcoin.blocks` AS b
JOIN
  `bigquery-public-data.crypto_bitcoin.transactions` AS t
ON
  b.number = t.block_number;
```

- **完整SELECT示例**：不仅给出ON条件，还提供完整的示例查询，选择了常用字段
- **业务场景说明**：明确说明"分析区块密度、矿工费分成、验证交易确认时间"等具体用途
- **三下划线命名**：`blocks___transactions`使用三下划线，表示这是"主从"或"包含"关系（一个区块包含多个交易），区别于stackoverflow中对等实体间的双下划线

#### 异常检测指标（references/metrics/duplicate_transactions.md）

该指标演示了OKF在**数据质量/异常检测**场景的应用——不仅有业务指标，还可以有数据质量指标。

### 5.4.4 覆盖的OKF特性

| OKF特性 | 覆盖情况 | 说明 |
|---------|---------|------|
| 紧密关联表文档化 | ✅ 核心特性 | 4个表形成紧密的外键网络 |
| 嵌套vs扁平化设计说明 | ✅ 新增特性 | 明确说明两种数据表示的适用场景 |
| 三下划线join命名约定 | ✅ 新增特性 | `___`表示主从/包含关系，`__`表示对等关联 |
| 完整JOIN示例查询 | ✅ 增强特性 | join文档提供完整SELECT而非仅ON条件 |
| 分区策略文档化 | ✅ 新增特性 | 明确说明分区字段和查询注意事项 |
| 数据质量指标 | ✅ 新增特性 | duplicate_transactions用于异常检测 |

### 5.4.5 学习价值

crypto_bitcoin Bundle适合学习**高度关联数据的OKF建模**：

1. **理解外键关系的文档化深度**：当表间关系不是简单的多对多，而是有明确的主从/包含关系时，如何通过命名约定和文档内容清晰表达
2. **掌握嵌套vs扁平化的权衡说明**：在实际项目中经常遇到类似的设计选择（如订单中嵌套订单项vs独立订单项表），OKF文档应该如何解释这种设计
3. **学习性能相关信息的文档化**：分区键、表大小、查询成本等性能相关信息应该在表文档中明确说明，帮助Agent生成高效查询
4. **区块链领域知识**：比特币区块链数据结构是区块链分析的基础，具有很高的行业参考价值
5. **对比stackoverflow的join设计**：通过两个Bundle的对比，理解不同关系类型（对等关联vs主从包含）的不同文档化策略

### 5.4.6 动手练习建议

1. 打开 `crypto_bitcoin/viz.html`，观察图结构——4个表形成紧密的菱形结构，3个join文档在中间连接它们
2. 对比 `blocks___transactions`（三下划线）和stackoverflow的 `posts_answers__posts_questions`（双下划线），理解命名约定的区别
3. 阅读 `transactions.md` 中关于嵌套vs扁平化的说明，思考你自己项目中是否有类似的设计选择需要文档化
4. 运行joins目录中的示例查询，观察比特币区块链的真实数据

---

## 5.5 Bundle 4：acme_retail - Acme Retail企业级示例

**位置**：`okf/bundles/acme_retail/`
**对应配方**：无（纯手工编写的企业级示例，非reference_agent自动生成）
**数据源**：虚构的Acme零售公司内部数据（BigQuery）
**可视化**：`okf/bundles/acme_retail/viz.html`

> ⚠️ **重要提示**：acme_retail是四个示例中**唯一非自动生成**的Bundle，它由Google的OKF设计团队手工编写，目的是展示OKF在企业级场景中的**完整能力边界**——特别是Attested Computation（认证计算）这一核心高级特性。这是最值得深入研究的示例。

### 5.5.1 目录结构

```
acme_retail/
├── index.md                     # Bundle根目录索引（手工编写）
├── log.md                       # 变更日志
├── viz.html                     # 知识图谱可视化
├── tables/
│   ├── index.md
│   └── orders.md                # 客户订单表
├── metrics/                     # 业务指标定义（业务语义层）
│   ├── index.md
│   ├── revenue.md               # 收入指标（当前FY2026政策）
│   ├── gross-margin.md          # 毛利指标
│   └── gross-margin-legacy.md   # 旧版毛利指标（FY2026之前，已废弃）
├── computations/                # 认证计算（SQL实现）
│   ├── index.md
│   ├── revenue-ytd.md           # 年初至今收入计算（Attested Computation）
│   └── gross-margin-period.md   # 期间毛利计算
├── policies/                    # 业务政策（业务规则来源）
│   ├── index.md
│   ├── revenue-recognition.md   # 收入确认政策（FY2026）
│   └── margin-standard.md       # 成本分摊标准
├── skills/                      # 执行技能（Agent可调用的执行器）
│   ├── index.md
│   └── run-on-bq.md             # 在BigQuery上运行计算的技能
└── attesters/                   # 验证者（确定性验证代码）
    ├── index.md
    └── sql_equality.py          # SQL相等性验证脚本（Python）
```

### 5.5.2 结构特点

acme_retail展示了OKF在企业级场景中的**完整概念类型体系**，形成一个可信的业务指标闭环：

1. **六层概念结构**：从底层数据表到上层业务政策，形成完整的语义栈：
   ```
   tables/        → 物理数据层（BigQuery表）
   policies/      → 业务规则层（收入确认政策等，由财务部门制定）
   metrics/       → 业务语义层（指标的业务定义，引用政策）
   computations/  → 计算实现层（SQL实现，引用表和政策）
   skills/        → 执行能力层（Agent如何运行计算）
   attesters/     → 验证层（确定性代码验证计算结果的真实性）
   ```
2. **Attested Computation（认证计算）**：这是OKF最核心的企业级特性——指标的SQL计算不是随意编写的，而是经过"认证"的，只有执行认证过的SQL得到的结果才被信任
3. **完整的信任链**：从政策（人制定）→指标定义→SQL实现→执行技能→验证代码，形成一条完整的可审计信任链
4. **版本化与废弃管理**：`gross-margin-legacy.md`明确标注为废弃版本，保留用于历史可重现性
5. **新鲜度与过期时间**：所有企业级概念都有`stale_after`字段，明确标注过期时间
6. **人工验证记录**：`verified`字段记录人工审核者和审核时间，建立人与AI的协作信任
7. **代码与Markdown混合**：attesters目录下不仅有.md文档，还有实际的Python验证脚本，形成文档与可执行代码的统一

### 5.5.3 Attested Computation完整工作流

acme_retail的核心价值在于演示了**认证计算的完整闭环**。理解这一流程是掌握OKF企业级用法的关键。

#### 信任链全景图

```
┌─────────────────────────────────────────────────────────────────────┐
│                        业务政策层 (Policies)                         │
│  policies/revenue-recognition.md                                    │
│  - 由VP Finance制定和维护                                           │
│  - 明确收入确认的四条规则：交付状态、30天退货期、金额计算、币种转换  │
│  - 每年12月31日审核，stale_after: 2026-12-31                        │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ 引用（sources）
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        指标定义层 (Metrics)                          │
│  metrics/revenue.md                                                 │
│  - 业务语言定义"收入"是什么                                         │
│  - 明确声明：消费者必须使用认证计算，不得自行编写SUM                 │
│  - verified: 财务负责人人工审核签字                                 │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ 对应（computation）
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      计算实现层 (Computations)                      │
│  computations/revenue-ytd.md  (type: Attested Computation)          │
│  - 包含经过批准的标准SQL（"Sanctioned SQL"）                        │
│  - 明确声明executor（用什么技能运行）和attester（用什么验证）        │
│  - 参数声明（@year年份参数）                                        │
│  -  receipt字段要求（必须返回job_id、executed_sql、result）         │
└──────────────────────┬───────────────────────────┬──────────────────┘
                       │ 引用（executor）           │ 引用（attester）
                       ▼                           ▼
┌──────────────────────────────┐    ┌─────────────────────────────────┐
│     执行技能层 (Skills)       │    │      验证层 (Attesters)          │
│  skills/run-on-bq.md         │    │  attesters/sql_equality.py       │
│  (type: Skill)               │    │  - 纯Python确定性代码            │
│  - 说明前置条件（权限、参数） │    │  - 不使用LLM，不发起网络请求     │
│  - 标准化执行步骤            │    │  - 两项核心验证：                │
│  - 禁止修改SQL，必须参数绑定 │    │    1. 执行的SQL与批准的SQL一致   │
│  - 标准化收据格式            │    │    2. 声称的值与实际结果一致     │
└──────────────────────────────┘    └─────────────────────────────────┘
```

#### 各层概念文档深度解析

**1. 政策文档（policies/revenue-recognition.md）**

政策文档是整个信任链的**源头**，特点：
- `type: Policy`：明确标记为政策类型
- **责任人明确**：Owner字段明确标注VP Finance及其邮箱
- **生效时间与审核周期**：Effective日期、Next scheduled review日期
- **规则清晰无歧义**：四条收入确认规则用业务语言明确写出
- **授权声明**：明确说明"引用本政策的Attested Computation必须实现上述四条规则，偏离需要政策附录"
- **Cited by反向链接**：自动列出哪些指标和计算引用了本政策

**2. 指标文档（metrics/revenue.md）**

指标文档是**业务语义层**，连接业务人员和技术实现：
- `type: Metric`：明确标记为指标类型
- **业务定义**：用业务语言精确定义指标——哪些订单算收入、如何处理多币种、退货期如何处理
- **强制认证声明**："Consumers MUST run and attest that computation rather than composing their own SUM."——消费者必须运行认证计算，不得自行编写SQL
- **口径说明**：哪些维度拆分是被允许的（如按渠道、按品类），哪些是被禁止的（如修改核心SQL）
- **信任与新鲜度**：verified记录人工审核，stale_after标注过期时间
- **交叉链接**：链接到政策来源和计算实现

**3. 计算文档（computations/revenue-ytd.md）**

计算文档是**技术实现层**，核心类型是 `Attested Computation`：

```yaml
---
type: Attested Computation
runtime: bigquery
parameters:
  - { name: year, type: integer, required: true }
executor:
  resource: skills/run-on-bq.md
  receipt: [job_id, executed_sql, result]
attester:
  resource: attesters/sql_equality.py
---
```

frontmatter中的特殊字段：
- `runtime: bigquery`：声明运行时环境
- `parameters`：声明参数列表（名称、类型、是否必填）
- `executor`：指定执行技能（哪个Skill负责运行这个计算），以及收据必须包含的字段
- `attester`：指定验证者（哪个脚本负责验证结果）

正文结构：
- `# Computation`围栏：包含经过批准的标准SQL（Sanctioned SQL）
- 规则映射：明确说明SQL如何对应政策中的四条规则
- 验证说明：说明attester检查什么（SQL一致性、结果一致性）
- 新鲜度：与政策保持一致的过期时间

**4. 技能文档（skills/run-on-bq.md）**

技能文档是**Agent的执行说明书**，告诉AI如何安全地运行计算：
- `type: Skill`：明确标记为技能类型
- **When to use**：什么时候应该使用这个技能
- **Preconditions**：前置条件（权限、参数完整性）
- **Steps**：标准化执行步骤：
  1. 加载计算（从# Computation围栏读取SQL）
  2. 参数绑定（必须使用BigQuery命名参数，禁止字符串拼接——防止SQL注入！）
  3. 提交作业（设置标签用于审计）
  4. 等待完成（区分运行时错误和SQL错误）
  5. 组装收据（严格按照receipt要求的字段）
  6. **永远不要修改SQL**——这是红线
- **Post-conditions**：后决条件——收据必须交给attester验证，验证通过前不得展示给用户

**5. 验证脚本（attesters/sql_equality.py）**

这是最具特色的部分——**可执行的验证代码**直接放在Bundle中：

- **纯Python、零依赖、确定性**：不使用LLM，不发起网络调用，可以在消费者端安全运行
- **两项核心检查**：
  1. **Provenance（来源验证）**：规范化后比较实际执行的SQL与批准的SQL是否一致——规范化包括去除注释、压缩空白、关键字大写，任何修改（交换表、添加过滤条件、删除JOIN）都会失败
  2. **Fidelity（保真度验证）**：声称展示给用户的值是否与收据中第一个结果单元格一致
- **规范化函数_canonicalize()**：智能处理——只大写SQL关键字，不修改标识符（表名、字段名保持大小写）
- **符号化参数比较**：命名参数（@name）只做符号比较，不检查参数值（信任执行器正确绑定）

### 5.5.4 覆盖的OKF高级特性

| OKF特性 | 覆盖情况 | 说明 |
|---------|---------|------|
| Policy类型 | ✅ 企业级特性 | 业务政策文档，作为信任链源头 |
| Metric类型 | ✅ 企业级特性 | 业务指标定义，强制认证要求 |
| Attested Computation类型 | ✅ 核心高级特性 | 认证计算，包含SQL、参数、执行器、验证者声明 |
| Skill类型 | ✅ 企业级特性 | Agent执行技能，标准化执行流程 |
| 可执行attester代码 | ✅ 核心高级特性 | Python验证脚本与Markdown文档同存 |
| verified人工验证记录 | ✅ 企业级特性 | 记录审核者和时间，建立人机信任 |
| stale_after新鲜度管理 | ✅ 企业级特性 | 所有概念都有过期时间，过期需重新验证 |
| 版本化与废弃管理 | ✅ 企业级特性 | gross-margin-legacy明确标注废弃 |
| 完整信任链 | ✅ 完整展示 | policy→metric→computation→skill→attester六层闭环 |
| 文档+代码混合 | ✅ 高级用法 | attesters目录同时包含.md和.py文件 |

### 5.5.5 学习价值

acme_retail是四个示例中**最有价值的一个**，它展示了OKF超越普通数据目录工具的核心能力：

1. **理解OKF的企业级定位**：OKF不是dbt docs或Data Catalog的替代品，它解决的是**业务语义可信度**问题——如何让Agent提供的数字是可审计、可验证、符合业务政策的
2. **掌握Attested Computation模式**：这是OKF最核心的创新——不是简单地写SQL，而是建立一套"批准-执行-验证"的可信计算流程
3. **学习人机协作信任模型**：人工制定政策和审核，Agent执行计算，确定性代码验证结果——三者各司其职
4. **理解合规与审计设计**：审计标签、收据机制、SQL禁止修改——这些都是为合规场景设计的
5. **版本化和生命周期管理**：如何处理指标定义变更（如gross-margin从legacy版本更新到新版本），如何保留历史可重现性
6. **Agent安全执行规范**：Skill中的"不要字符串拼接参数"、"永远不要修改SQL"等规则是Agent安全执行的最佳实践

### 5.5.6 动手练习建议

1. 打开 `acme_retail/viz.html`，观察这是最"稠密"的知识图谱——metrics、computations、policies、skills、attesters形成高度互连的网络
2. 从 `metrics/revenue.md` 开始，沿着链接依次点击：revenue → revenue-ytd → run-on-bq → sql_equality.py → revenue-recognition，走完整条信任链
3. 阅读 `attesters/sql_equality.py` 代码，理解它是如何做SQL规范化比较的
4. 思考你自己业务中的哪些指标需要这种级别的可信认证——财务报表指标、合规KPI、对外披露数据都是潜在场景
5. 对比三个自动生成Bundle和acme_retail的区别——理解自动生成的基础文档和手工编写的企业级语义层之间的差距和互补关系

---

## 5.6 四个Bundle的对比总结

| 维度 | ga4 | stackoverflow | crypto_bitcoin | acme_retail |
|------|-----|--------------|----------------|-------------|
| **生成方式** | reference_agent自动生成 | 同左 | 同左 | 手工编写 |
| **表数量** | 1 | 16 | 4 | 1 |
| **核心概念类型** | Dataset, Table, Reference | + Join, 枚举Reference | + 嵌套关系说明 | + Policy, Metric, Attested Computation, Skill, Attester |
| **表间关系** | 无（单表） | 多对等实体，双下划线join | 紧密关联，三下划线主从join | 不涉及（单表示例） |
| **信任机制** | sources来源引用 | 同左 | 同左 | 完整六层信任链+人工验证+确定性attester |
| **学习难度** | ★☆☆ | ★★☆ | ★★☆ | ★★★ |
| **适用场景** | 入门学习、单表数据集 | 多实体数据仓库、关系文档化 | 高度关联事实表、区块链/时序数据 | 企业级可信指标、合规场景、财务数据 |
| **viz.html节点数** | ~10 | ~25 | ~10 | ~12 |

---

## 5.7 本章小结与延伸阅读

### 5.7.1 关键要点总结

**samples与bundles的关系**：
1. `samples/`是配方（可复现实验），包含README.md运行说明和seeds.txt种子URL
2. `bundles/`是配方运行后的产物，包含完整OKF文档和viz.html可视化
3. 三个公共数据集配方（GA4、Stack Overflow、比特币）可通过`reference_agent enrich`命令重新生成
4. acme_retail是手工编写的企业级示例，无对应自动生成配方

**四个Bundle的学习路径**：
1. 从ga4开始——掌握OKF基础结构和三种核心概念类型
2. 学习stackoverflow——掌握多表组织、join路径、枚举引用
3. 学习crypto_bitcoin——掌握紧密关联表、嵌套/扁平化设计、性能信息文档化
4. 深入研究acme_retail——掌握企业级高级特性，特别是Attested Computation

**Acme Retail核心启示**：
1. OKF的核心价值不是文档化表结构，而是建立**可审计、可验证的业务语义信任链**
2. Attested Computation通过"批准SQL→标准执行→确定性验证"三步保证Agent返回的数字可信
3. 人制定政策、Agent执行、代码验证——三者协作建立人机信任
4. 新鲜度（stale_after）、版本化、废弃管理都是企业级场景不可或缺的

### 5.7.2 交叉引用与延伸阅读

**OKF Wiki相关章节**：
- OKF核心概念与类型系统：[okf-wiki 01 核心概念与设计哲学](../okf-wiki/01-core-concepts.md)
- OKF快速入门（手工创建Bundle）：[okf-wiki 02 5分钟快速入门](../okf-wiki/02-quickstart.md)
- OKF使用模式（包括认证计算模式）：[okf-wiki 03 使用模式与最佳实践](../okf-wiki/03-usage-patterns.md)

**Knowledge Catalog Wiki相关章节**：
- OKF规范中type字段和概念类型定义：[02 OKF开放知识格式规范深度解析](./02-okf-specification.md)
- 参考Agent如何自动生成Bundle：[03 参考Agent实现原理与运行指南](./03-reference-agent.md)
- 可视化系统如何呈现Bundle结构：[04 工具链与可视化系统](./04-toolchain-and-visualization.md)
- 企业集成模式与最佳实践：[06 集成模式与最佳实践](./06-integration-patterns.md)（下一章）

**官方资源**：
- 官方GitHub仓库：https://github.com/googlecloudplatform/knowledge-catalog
- 示例Bundle源码：`okf/bundles/`
- 示例配方源码：`okf/samples/`
- BigQuery公共数据集：https://cloud.google.com/bigquery/public-data

---

| 上一章 | 目录 | 下一章 |
|--------|------|--------|
| [04 工具链与可视化系统](./04-toolchain-and-visualization.md) | [README](./README.md) | [06 集成模式与最佳实践](./06-integration-patterns.md) |
