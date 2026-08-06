---
id: "knowledge-catalog-wiki-okf-specification"
title: "02 OKF开放知识格式规范深度解析"
version: "1.0"
source: "GoogleCloudPlatform/knowledge-catalog okf/SPEC.md v0.2"
type: "Wiki Tutorial"
description: "OKF v0.2规范实现视角深度解析，Bundle结构规范、Frontmatter字段详解、链接规则、Index/Log文件格式、信任与来源字段、Attested Computation规范、Conformance合规性规则、v0.1到v0.2变更"
tags: ["Knowledge Catalog", "OKF", "规范解析", "Bundle", "Frontmatter", "Attested Computation", "Conformance"]
category: "learning"
date: "2026-08-06"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "从knowledge-catalog参考实现视角深度解析OKF v0.2规范，覆盖Bundle结构、Frontmatter必填/推荐字段、链接规则、信任与来源机制、认证计算、合规性规则及版本变更，大量交叉链接指向okf-wiki完整教程"
last_verified: "2026-08-06"
wiki_version: "1.0"
okf_version_target: "v0.2"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/knowledge/learning/01-agent-protocols-interfaces/knowledge-catalog-wiki/02-okf-specification.toml"
---

# 02 OKF开放知识格式规范深度解析

> **本章定位说明**
> - [okf-wiki](../okf-wiki/README.md) 是OKF开放知识格式的**完整教程**，从背景动机、设计哲学到使用实践进行了全面介绍。
> - 本章从 **knowledge-catalog 参考实现视角**出发，聚焦OKF v0.2规范的**实现要点**，提供精确的字段定义、约束规则和代码实现视角的解读。
> - 阅读本章前建议先阅读 [okf-wiki核心概念](../okf-wiki/01-core-concepts.md) 建立整体认知，本章侧重规范的精确性和可实现性。

## 2.1 Bundle结构规范实现要点

Bundle是OKF分发和版本控制的基本单元，knowledge-catalog参考实现严格遵循以下结构规范（参见 [okf-wiki Bundle结构](../okf-wiki/01-core-concepts.md#15-bundle目录结构规范)）。

### 2.1.1 目录树约束

Bundle是UTF-8编码Markdown文件的目录树，目录结构由生产者自行组织，规范不强制特定分类方式。参考实现中的典型结构如下：

```
path/to/bundle/
  index.md                      # 可选：目录列表，支持渐进式披露
  log.md                        # 可选：更新历史
  <concept>.md                  # Bundle根目录下的Concept
  <subdirectory>/               # 子目录用于分组组织Concept
    index.md
    <concept>.md
    <subdirectory>/
      ...
```

**分发形式（实现支持）**：

1. **Git仓库**（推荐）：天然提供版本历史、归属追溯和diff能力，knowledge-catalog默认采用此形式。
2. **tarball/zip归档**：目录的压缩归档形式，适用于离线分发。
3. **大型仓库子目录**：monorepo中的子目录（最常见实践是`knowledge/`或`docs/catalog/`）。

### 2.1.2 保留文件名严格约束

以下文件名在目录树任意层级均具有定义含义，**严禁**用作Concept文档文件名：

| 文件名 | 用途 | 规范章节 |
|--------|------|----------|
| `index.md` | 目录内容列表，支持渐进式披露 | §2.5 |
| `log.md` | 高层变更历史记录 | §2.6 |

其他所有`.md`文件均为Concept文档。

**实现注意事项**：标签（Tags）通过frontmatter的`tags`字段作为一类Concept存在，OKF不定义单独的标签聚合文件格式；需要标签浏览视图的消费者可在消费时通过扫描frontmatter动态合成。

## 2.2 Concept文件结构与Frontmatter字段详解

每个Concept是UTF-8编码Markdown文件，由两部分组成：YAML frontmatter元数据块 + Markdown正文（参见 [okf-wiki Concept结构](../okf-wiki/01-core-concepts.md#16-concept文件结构)）。

### 2.2.1 Frontmatter基础结构

```yaml
---
type: <Type name>                  # ✅ 必填
title: <Optional display name>
description: <Optional one-line summary>
resource: <Optional canonical URI for the underlying asset>
tags: [<tag>, <tag>, ...]          # 可选
# 信任、生命周期、来源、计算家族字段（见§2.3、§2.7）
# 其他生产者自定义键值对
---
```

### 2.2.2 必填字段详解

| 字段 | 类型 | 约束 | 实现说明 |
|------|------|------|----------|
| `type` | 字符串 | **必填，非空** | 标识Concept类型，消费者用于路由、过滤和展示。示例值：`BigQuery Table`、`BigQuery Dataset`、`API Endpoint`、`Metric`、`Playbook`、`Reference`、`Attested Computation`。 |

**关键实现约束**：

- `type`值**不集中注册**，生产者应选择描述性、自解释的值。
- 消费者**必须**优雅容忍未知类型，通常将其作为通用Concept处理。
- 仅包含`type`字段的Concept也是完全合规的（见§2.8 Conformance）。

### 2.2.3 推荐字段详解

| 字段 | 类型 | 推荐度 | 实现说明 |
|------|------|--------|----------|
| `title` | 字符串 | ⭐推荐 | 人类可读显示名称。省略时，消费者可从文件名推导标题。 |
| `description` | 字符串 | ⭐推荐 | 单句摘要，用于`index.md`生成、搜索片段、预览卡片。 |
| `resource` | URI | ⭐推荐 | 唯一标识Concept所描述底层资产的规范URI。描述抽象概念（如业务流程）的Concept可省略。 |
| `tags` | YAML列表 | ⭐推荐 | 短字符串列表，用于横切分类。 |

### 2.2.4 扩展字段规则

- 生产者**可**包含任意额外键值对。
- 消费者往返处理时**应**保留未知键。
- 消费者**不得**因包含无法识别的字段而拒绝文档。

## 2.3 信任与来源字段家族详解（v0.2核心新增）

v0.2最重要的增强是将**来源（Provenance）**、**信任（Trust）**、**生命周期（Lifecycle）**作为一类字段引入frontmatter，使Agent维护的知识语料库具备可审计的可信度基础（参见 [okf-wiki 完整示例](../okf-wiki/01-core-concepts.md#112-完整代码示例)）。

这些字段均为可选。它们的缺失本身具有含义：未验证的Concept与已验证的Concept可区分，但**不会被拒绝**。

### 2.3.1 Actor约定（统一身份标识）

记录身份的字段（`generated.by`、`verified[].by`）使用统一的Actor约定：

| Actor类型 | 格式 | 示例 |
|-----------|------|------|
| Agent/工具 | `<producer>/<version>` | `reference_agent/gemini-2.5-pro` |
| 人类 | `human:<id>` | `human:ahormati` |
| 自动化流程 | `process:<id>` | `process:finance-nightly` |

**实现约束**：进行信任分类的消费者依据`human:`前缀判断，因此生产者**必须**对手工编写或人工确认的内容使用此前缀。

### 2.3.2 来源字段：`sources`

`sources`记录Concept衍生自的材料（Bundle内部或外部），是对抗幻觉的关键机制。

```yaml
sources:
  - id: ga4-schema
    resource: https://developers.google.com/analytics/bigquery/export-schema
    title: GA4 BigQuery Export schema
    author: team:ga4-docs
    usage_count: 5000
    last_modified: 2026-05-30
usage_window: { from: 2026-06-01, to: 2026-06-30 }
```

**每个sources条目字段**：

| 字段 | 必填 | 说明 |
|------|------|------|
| `resource` | ✅（在条目内） | 命名消费者可跟随的具体工件（绝对URL、Bundle相对路径、`references/`子目录路径），或无法跟随的范围描述符（如"BigQuery项目X中的所有查询"）。 |
| `id` | 推荐（正文引用时必须） | 稳定键，用于正文逐句归因。 |
| `title` | 可选 | 来源的人类可读标签。 |

**来源可信度信号**（客观逐来源记录，消费者据此推断信任度，不存储主观评分）：

| 信号字段 | 说明 | 信号类型 |
|----------|------|----------|
| `author` | 来源的生产者（遵循Actor约定） | 权威性信号 |
| `usage_count` | `usage_window`内`resource`被使用的次数（仪表盘浏览量、查询执行次数、页面阅读量） | 采用度与活跃度信号 |
| `last_modified` | 来源本身最后变更日期（`YYYY-MM-DD`） | 时效性信号（注意：与`generated.at`记录Concept编写时间不同） |

**`usage_count`使用注意**：这是一个粗粒度信号，适用于存活/死亡判断和数量级比较，以及与来源自身历史对比，但不适用于精确跨类型排名——定时查询的执行次数与人类刻意的仪表盘浏览量不具备同等权重。消费者应将其解读为活跃度和趋势，而非评分。

**`usage_window`**：作为`sources`的同级字段一次性写入，用`{ from, to }`日期范围框定所有`usage_count`的统计窗口。单个条目可携带自己的`usage_window`覆盖共享窗口。

**血统表达**：血统通过链接表达，而非专用字段。当`resource`指向另一个OKF Concept时，派生边已存在于Bundle图中，消费者可递归进入该来源自身的`sources`，让可信度传播。更深层次的血统（显式外部`derived_from`或数据血统）不在v0.2范围内。

**逐句归因实现**：对特定主张进行归因时，使用Markdown脚注，其标签为`sources[].id`：

```markdown
`events_`表按日分片为`events_YYYYMMDD`。[^ga4-schema]

[^ga4-schema]: GA4 BigQuery Export schema
```

脚注标签是连接到`sources`的键；消费者通过匹配条目解析归因，而非解析脚注文本。使用键而非位置索引（`sources[0]`）是因为Agent会不断重写这些文档：列表重新排序时位置索引会静默错误归因，而稳定的`id`在重排序后仍然有效。

### 2.3.3 生成字段：`generated`

`generated`记录当前内容是如何产生的。

```yaml
generated: { by: reference_agent/gemini-2.5-pro, at: 2026-06-20T22:53:05Z }
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `generated.by` | ✅（在generated内） | Actor（遵循§2.3.1约定）。 |
| `generated.at` | 可选 | ISO 8601日期时间，标记内容最后一次有意义变更的时间。消费者用它区分近期编辑与过时事实。 |

### 2.3.4 验证字段：`verified`

`verified`记录谁/什么对照来源或`resource`确认了内容。`generated`和`verified`保持分离，因为编写Concept的人不一定是确认它的人。

```yaml
verified:
  - { by: human:ahormati, at: 2026-06-25T09:00:00Z }
  - { by: process:finance-nightly, at: 2026-06-26T02:00:00Z }
```

- `verified`是验证事件列表，每个条目包含`by`（Actor）和`at`（ISO 8601日期时间）。多个条目捕获独立检查，例如人工签署加夜间流程验证。"最近程度"是最新的`at`值。
- `verified`独立于`generated.at`：内容可以变更而不重新确认，事实可以重新确认而不重新生成。
- 单个验证者**可**写为单个`{ by, at }`映射而不使用列表短横线。消费者**必须**将裸映射视为单元素列表：

```yaml
verified: { by: human:ahormati, at: 2026-06-25T09:00:00Z }
```

### 2.3.5 信任层级推导（消费者实现逻辑）

消费者从`verified`推导信任层级，从低到高：

| 层级 | 条件 |
|------|------|
| **unverified（未验证）** | 无`verified`键 |
| **machine-confirmed（机器确认）** | `verified`仅包含非`human:`执行者 |
| **human-reviewed（人类审核）** | `verified`包含`human:<id>`执行者 |

没有信任frontmatter的Concept仍然可消费；消费者**不得**拒绝它。信任层级是建议性信号，而非访问控制。

### 2.3.6 生命周期字段：`status`

```yaml
status: stable        # draft | stable | deprecated
```

| 状态值 | 含义 |
|--------|------|
| `draft` | 尚未审核；可能不完整 |
| `stable` | 默认值；可供消费 |
| `deprecated` | 保留用于链接和历史；不再是当前版本 |

缺失`status`时默认为`stable`。

### 2.3.7 生命周期字段：`stale_after`

```yaml
stale_after: 2026-09-23
```

- 可选。绝对日期（`YYYY-MM-DD`）。
- 当`today >= stale_after`时Concept视为过时。
- 使用绝对日期而非相对TTL，使过时判断成为纯日期比较，无需参考Concept读取时间。

## 2.4 跨链接规则实现要点

Concept之间使用标准Markdown链接表示关系（参见 [okf-wiki 链接规则](../okf-wiki/01-core-concepts.md#18-跨链接规则)）。

### 2.4.1 两种链接形式

| 形式 | 语法 | 解析方式 | 推荐场景 |
|------|------|----------|----------|
| **Bundle绝对链接（推荐）** | 以`/`开头 | 相对于Bundle根目录解析 | 推荐使用，在子目录内移动文档时保持稳定 |
| **相对链接** | 标准Markdown相对路径 | 相对于当前文件目录解析 | 相邻文件间引用 |

**Bundle绝对链接示例**：
```markdown
参见 [customers表](/tables/customers.md) 获取连接键。
```

**相对链接示例**：
```markdown
参见 [相邻概念](./other.md)。
```

### 2.4.2 链接语义与断链容忍

- 从Concept A到Concept B的链接断言一种**关系**。具体类型（父子、引用、连接、依赖）由周围上下文表达，而非由链接本身表达。构建图谱视图的消费者通常将所有链接视为无类型关系的有向边。
- 消费者**必须**容忍断链：目标在Bundle中不存在的链接不是格式错误；它可能仅表示尚未编写的知识。这类似维基百科的红链——提示"这里应该有一篇文章但还没写"，而非报错。

### 2.4.3 路径值字段统一规则

以下字段命名路径或URI：`resource`、`sources[].resource`、`computation`、`executor.resource`、`attester.resource`（见§2.7）。`sources[].resource`也可以是范围描述符，此时它不是路径。每个路径值字段接受：

1. 绝对URL（如`https://...`）
2. 以`/`开头的Bundle相对路径
3. 相对路径（如`../computations/revenue.md`）

### 2.4.4 `references/`目录约定

`references/`子目录是约定性组织模式，用于将外部材料、运行指令、代码镜像为Bundle内的一类Concept。sources、executors、attesters通常指向该目录（例如`references/attesters/revenue.py`）。这是命名约定，而非强制要求。

## 2.5 Index文件格式规范

`index.md`文件可出现在任何目录（包括Bundle根目录），枚举目录内容以支持**渐进式披露**：让人类或Agent在打开单个文档前即可了解可用内容（参见 [okf-wiki Index文件](../okf-wiki/01-core-concepts.md#19-index-files索引文件)）。

### 2.5.1 结构约束

- Index文件**不包含frontmatter**，唯一例外：Bundle根`index.md`可携带`okf_version`键（见§2.9版本控制）。
- 正文使用一个或多个章节，每个章节在标题下对Concept进行分组：

```markdown
# 章节/分组标题

* [标题1](相对url-1) - 条目1的简短描述
* [标题2](相对url-2) - 条目2的简短描述

# 另一个章节

* [子目录](subdir/) - 子目录的简短描述
```

### 2.5.2 实现要点

- 条目应包含链接Concept的frontmatter中的`description`。
- 生产者可自动生成`index.md`；无`index.md`时消费者可动态扫描合成。
- knowledge-catalog参考实现提供Shell脚本自动化生成index，遍历目录提取frontmatter的title和description字段。

## 2.6 Log文件格式规范

`log.md`文件可出现在层次结构的任意层级，记录该范围的变更历史（参见 [okf-wiki Log文件](../okf-wiki/01-core-concepts.md#110-log-files日志文件)）。

### 2.6.1 格式约束

格式为按日期分组的条目的扁平列表，最新在前：

```markdown
# 目录更新日志

## 2026-05-22
* **Update**: 为[Customer Metrics](/tables/customer-metrics.md)添加了BigQuery表引用。
* **Creation**: 建立了[Dataplex Playbook](/playbooks/dataplex.md)。

## 2026-05-15
* **Initialization**: 创建了基础目录结构。
```

### 2.6.2 实现要点

- 日期标题**必须**使用ISO 8601 `YYYY-MM-DD`格式。
- 日志条目为自由文本；开头粗体词（`**Update**`、`**Creation**`、`**Deprecation**`）是约定，而非强制要求。
- **log.md vs git log**：git log是供开发者查看的细粒度提交历史（如"修复typo"）；log.md是供人类/Agent快速浏览演变脉络的高层摘要（如"5月新增客户指标表"），类似CHANGELOG而非逐条commit记录。

## 2.7 Attested Computation（认证计算）规范详解

Attested Computation是OKF v0.2引入的新Concept类型（`type: Attested Computation`），不仅承载值的含义，还承载值的**受认可计算方式**，使消费者能够确认Agent运行了指定计算而非自行编造（参见 [okf-wiki 认证计算概念](../okf-wiki/01-core-concepts.md#16-concept文件结构)中对type字段的说明）。

来源（Provenance）回答"这个主张从哪里来"；认证（Attestation）回答"这个数字是否按规定方式产生"。OKF记录计算和检查方式；它本身不执行任何内容。

### 2.7.1 设计动机：计算作为独立Concept

受认可的计算是`type: Attested Computation`的独立Concept。需要该值的Concept（`Metric`、`BigQuery Table`）通过普通Markdown链接指向它。三个属性支撑独立Concept设计：

1. **`runtime`定义`parameters`的含义**：参数是SQL绑定变量、dbt变量还是Python参数取决于运行时。将`runtime`和`parameters`保存在同一frontmatter中使绑定语义不言自明。
2. **一次计算，多个消费者**：同一计算可支撑指标、仪表盘Concept、报表；作为Concept一次引用多次复用。
3. **信任状态按计算独立**：`verified`、`stale_after`和单个`attester`描述一件事。收入、利润、毛利各自独立验证和认证，因此是三个Concept，而非一个frontmatter中的三个条目。

### 2.7.2 契约字段详解

契约是Concept的顶层frontmatter。除来源、信任、生命周期家族外，Attested Computation Concept携带：

| 字段 | 必填（本类型） | 说明 |
|------|----------------|------|
| `runtime` | ✅ | 单一字段，说明如何运行计算，因此executor和attester如何解释它以及`parameters`的含义。示例值：`bigquery`、`postgres`、`dbt`、`python`、`Looker`。 |
| `parameters` | 可选 | 类型化命名参数列表，Agent可填充。每个条目：`{ name, type, required }`。绑定语义遵循`runtime`。 |
| `computation` | 可选 | 指向包含计算的文件的路径（§2.4.3），用于替代正文内联围栏（见§2.7.3）。缺失时⇒正文`# Computation`围栏为计算内容。 |
| `executor` | 可选 | 计算运行方式：`resource`命名运行指令或代码；运行器（Agent或确定性消费者代码）遵循它。`receipt`声明运行必须返回的字段列表，即attester检查的证据（例如BigQuery `job_id`和作业实际执行的SQL）。 |
| `attester` | 可选 | 确定性检查：`resource`命名（无LLM）代码，接收receipt并返回结论。设计为在消费者侧运行。 |

`resource`背后是什么（Skill、脚本、容器）是打包选择；OKF修复接口，而非打包。

**完整示例**：
```markdown
---
type: Attested Computation
title: Revenue for fiscal year
description: Recognized revenue for a fiscal year, per Finance's definition.
status: stable
runtime: bigquery
parameters:
  - { name: year, type: integer, required: true }
executor:
  resource: references/skills/run-on-bq.md
  receipt: [job_id, executed_sql, result]
attester:
  resource: references/attesters/revenue.py
generated: { by: reference_agent/gemini-2.5-pro, at: 2026-06-20T22:53:05Z }
verified: { by: human:ahormati, at: 2026-06-25T09:00:00Z }
stale_after: 2026-09-23
sources:
  - id: rev-policy
    resource: https://wiki.acme/finance/revenue-recognition
    title: Revenue recognition policy
---

# Computation

    SELECT SUM(amount) AS revenue
    FROM finance.recognized_revenue
    WHERE fiscal_year = @year

The computation binds only the declared `parameters`, per the recognition policy.[^rev-policy]

[^rev-policy]: Revenue recognition policy
```

### 2.7.3 计算提供方式

以两种方式之一提供计算：

- **内联**：正文`# Computation`下的单个围栏代码块。适合与契约一同评审的短计算。
- **文件引用**：将`computation`设置为路径（§2.4.3）并省略正文围栏。适合较长或生成的计算，或已作为真实文件与非OKF工具共享的计算。

```yaml
runtime: bigquery
computation: references/computations/lib/revenue.sql
parameters:
  - { name: year, type: integer, required: true }
```

**关键实现约束**：Agent**只能**为声明的`parameters`提供**值**；它**不得**编写或编辑计算本身。将`computation`与参数值绑定到可执行工件是消费者的工作，attester独立重新推导相同绑定以与实际运行的内容进行比较。因为比较是在receipt携带的展开、编译工件（`executed_sql`、`compiled_sql`）上进行的，重写查询、交换计算文件或变异依赖都会导致检查失败。类型化、仅参数的表面是使"是否运行了受认可的内容"成为机械比较而非主观判断的关键。

### 2.7.4 使用计算的Concept

文档很少是单个计算。讨论收入、利润和毛利的损益表概览保持为一个可读Concept，并为每个数字链接一个Attested Computation：

```markdown
---
type: Metric
title: Revenue
description: Recognized revenue for a fiscal year.
tags: [finance, revenue]
status: stable
generated: { by: reference_agent/gemini-2.5-pro, at: 2026-06-20T22:53:05Z }
---

# Definition

Recognized revenue sums `amount` over rows booked to the fiscal year,
computed by [the revenue computation](../computations/revenue.md).
```

因为每个计算是自己的Concept，收入可以是新鲜的而利润已过`stale_after`，每个计算在自己的运行上独立认证。将它们共置是目录选择（带`index.md`的`computations/`文件夹），而非frontmatter选择。

### 2.7.5 消费者使用流程（参考实现）

以下为信息性说明，非规范性。运行时工件**不**存储在Bundle中。

1. **发现**：通过`type: Attested Computation`（可提升到`index.md`的frontmatter信号）；消费者直接到达或通过使用它的Concept链接到达。
2. **加载**：从frontmatter加载契约，从正文（或`computation`命名的文件）加载计算。
3. **参数化**：Agent为声明的参数提供值。
4. **执行**：executor运行绑定后的计算，返回由`executor.receipt`塑形的receipt。
5. **认证**：消费者在receipt上运行attester。它确认来源（运行的计算等于绑定了声明参数的`computation`，而非Agent编写的SQL）和保真度（显示值与receipt的权威来源匹配，通过job id重新读取而非取自Agent文本）。
6. **门禁**：拒绝显示认证失败的结果；当`today >= stale_after`时警告或拒绝。成功时展示结论（例如作业日志链接）使信任可见。

### 2.7.6 Verification与Attestation的区别

`verified`（§2.3.4）和Attestation是不同的，两者都存在：

- `verified`确认**定义**仍符合策略。它是文档级别的、慢速的、记录在Bundle中。
- Attestation确认单次**运行**按受认可方式产生值。它是每次调用、运行时的、不存储在Bundle中。

定义过时的Concept仍然可以干净地通过认证，新验证的定义在每次运行时仍需要认证，这就是两者都需要的原因。

## 2.8 Conformance（合规性）规则

Bundle符合OKF v0.2规范当且仅当满足以下条件：

### 2.8.1 强制合规条件

1. 树中每个非保留`.md`文件包含可解析的YAML frontmatter块。
2. 每个frontmatter块包含非空`type`字段。
3. 存在的每个保留文件名（`index.md`、`log.md`）分别遵循§2.5和§2.6中的结构。

### 2.8.2 存在时的遵循要求

当信任、生命周期、来源或计算家族字段存在时，生产者应遵循§2.3至§2.7，消费者：

- **必须**将裸`verified`映射视为单元素列表（§2.3.4）。
- **不得**因缺失任一家族字段而拒绝Concept（§2.3.5）。
- **应**仅从本文档指定的字段推导信任层级和过时性，**应**展示而非静默丢弃认证失败（§2.7.5）。

### 2.8.3 消费者宽容原则（不得拒绝的情形）

消费者应将所有其他约束视为软指导。特别是，消费者**不得**因以下原因拒绝Bundle：

- 缺失可选frontmatter字段。
- 未知`type`值。
- 未知额外frontmatter键。
- 断链。
- 缺失`index.md`文件。

## 2.9 版本控制规范

本文档指定OKF版本**0.2**。修订版本版本化为`<major>.<minor>`：

- **次要**版本 bump引入向后兼容的新增内容（新可选字段、新约定章节标题）。
- **主要**版本 bump可能进行破坏性变更（重命名字段、更改保留文件名）。

Bundle可在Bundle根`index.md`的frontmatter块中使用`okf_version: "0.2"`声明其目标版本（这是`index.md`中允许frontmatter的唯一位置）。不理解声明版本的消费者应尝试尽力消费而非拒绝Bundle。

### 2.9.1 考虑并推迟到未来版本的内容

以下内容有意留待未来修订：

- 完整运行时协议：receipt和verdict有线格式，以及围绕运行的认证生命周期。
- attester ABI、可移植性和沙箱，可能与未来服务和Skills工作捆绑。
- 认证缓存。
- 语义层模板（Looker、dbt），其中attester比较从SQL相等转移到模型和绑定相等。

## 2.10 v0.1到v0.2的变更详解

v0.2取代OKF v0.1，根据§2.9版本控制规则是次要版本bump，但有两个 deliberate 破坏性变更如下所述，因为它们重命名或废弃了v0.1字段。在以下说明的回退机制下，v0.1 Bundle可由v0.2消费者消费（参见 [okf-wiki 快速入门](../okf-wiki/02-quickstart.md) 了解新版本使用方式）。

### 2.10.1 破坏性变更

| 变更项 | 说明 | 消费者兼容策略 |
|--------|------|----------------|
| **`timestamp`被`generated.at`取代** | Concept的最后内容变更现在记录为`generated: { by, at }`（§2.3.3）。 | 当`generated`缺失时，消费者可回退到遗留`timestamp`。 |
| **正文`# Citations`列表被`sources`取代** | 来源移至frontmatter（§2.3.2）。 | 消费者应读取`sources`，对于v0.1文档仍可解析遗留`# Citations`正文列表。 |

### 2.10.2 新增内容（向后兼容）

以下所有内容均为新增：新可选键、一个新概念类型、一个新约定标题。它们的缺失产生普通v0.1 Concept。

- 新frontmatter家族：`sources`及其逐来源可信度信号（`author`、`usage_count`、`last_modified`）和同级`usage_window`；`generated`、`verified`；`status`、`stale_after`（§2.3）。
- 新概念类型`Attested Computation`及其计算键`runtime`、`parameters`、`computation`、`executor`、`attester`（§2.7）。
- 新约定正文标题`# Computation`（§2.2）。
- `generated.by`和`verified[].by`的Actor约定（§2.3.1）。

其他所有内容（Bundle结构、保留文件名、必填`type`、推荐`title`/`description`/`resource`/`tags`、跨链接、index文件、log文件、宽容合规性）均保持不变向前传递。

### 2.10.3 迁移示例：损益表演进

为直观展示v0.1到v0.2的迁移，考虑一个包含收入和毛利两个数字的损益表：

**v0.1形式**：单个文档，两个数字在一个Concept中，SQL在Agent可读取、忽略或重写的散文中，引用为扁平列表，唯一时间戳是`timestamp`。

**v0.2形式**：两个数字拆分为认证计算，从叙述Concept链接。每个家族都被填充，两个计算处于故意不同的状态，使一个消费者得到两个结论。

```
bundles/finance/
  metrics/income-statement.md      type: Metric （叙述，链接两者）
  computations/revenue.md          type: Attested Computation （runtime: bigquery）
  computations/profit.md           type: Attested Computation （runtime: dbt）
  references/skills/run-on-bq.md, run-dbt.md
  references/attesters/sql-equality.py, dbt-binding.py
```

- `metrics/income-statement.md`：可读文档；信任存在于它链接的内容上，而非此处。
- `computations/revenue.md`：BigQuery SQL，人工验证、新鲜，并由带有可信度信号的实时仪表盘来源佐证。
- `computations/profit.md`：dbt模型，流程验证，已过`stale_after`。

这种拆分使每个数字可独立验证、独立认证、独立判断新鲜度，而不是将所有状态混在单个文档中——这正是v0.2信任机制设计的核心价值。

## 2.11 本章小结与延伸阅读

本章从knowledge-catalog参考实现视角精确解析了OKF v0.2规范的结构约束、字段定义和实现规则。关键要点回顾：

1. **极简核心**：仅强制`type`一个必填字段，其他均为可选，遵循"最少约定"设计哲学。
2. **信任机制**：v0.2通过`sources`/`generated`/`verified`/`status`/`stale_after`家族字段，使Agent生成知识的可信度可审计、可追溯。
3. **认证计算**：`Attested Computation`类型将"数字如何产生"作为一类Concept独立出来，通过确定性attester在消费时验证，防止Agent编造计算结果。
4. **宽容合规**：消费者必须容忍断链、未知类型、缺失可选字段，确保格式演进时的向后兼容性。

**延伸阅读**：

- OKF完整教程：[okf-wiki目录](../okf-wiki/README.md)
- OKF核心概念：[okf-wiki 01 核心概念](../okf-wiki/01-core-concepts.md)
- OKF快速入门实操：[okf-wiki 02 快速入门](../okf-wiki/02-quickstart.md)
- OKF架构与Agent集成：[okf-wiki 05 架构定位与Agent集成](../okf-wiki/05-architecture-and-integration.md)
- Knowledge Catalog平台架构：[01 核心概念与平台架构](./01-core-concepts.md)

| 上一章 | 目录 | 下一章 |
|--------|------|--------|
| [01 核心概念与平台架构](./01-core-concepts.md) | [README](./README.md) | [03 参考Agent实现](./03-reference-agent.md) |
