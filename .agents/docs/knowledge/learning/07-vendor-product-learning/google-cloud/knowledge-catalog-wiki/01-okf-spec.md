---
id: knowledge-catalog-wiki-okf-spec
title: 01 - OKF开放知识格式规范详解
date: 2026-08-15
tags:
  - okf
  - specification
  - format
  - frontmatter
  - trust
  - provenance
  - attested-computation
source:
  - vendor/knowledge-catalog/okf/SPEC.md (OKF v0.2)
maturity: L1-draft
---

# 01 - OKF开放知识格式规范详解（v0.2）

> 本章基于OKF v0.2官方规范编写，完整覆盖Bundle结构、Frontmatter字段、信任/来源/生命周期体系、认证计算(Attested Computation)四大核心主题。

---

## 一、OKF 设计动机与目标

### 1.1 为什么需要OKF？

AI Agent的知识表示领域正在快速演进，但出现了许多不兼容的约定。OKF的立场是：知识最好用普遍可访问的、成熟的格式表示，这些格式需要：

- **无需工具即可被人类阅读**
- **无需定制SDK即可被Agent解析**
- **在版本控制中可diff**
- **跨工具、跨组织、跨时间可移植**

越来越多的知识语料库不是一次写完然后读——而是**由Agent持续编写和维护**。当大多数概念由机器生成时，普通的Markdown+frontmatter约定无法原生回答以下问题：

1. 这是从什么创建的？如何验证的？（**来源 provenance**）
2. 我应该在多大程度上信任它？（**信任 trust**）
3. 它现在仍然正确吗？（**新鲜度 freshness**）
4. 这是当前版本吗？（**生命周期 lifecycle**）
5. 这个数字是按我们规定的方式产生的吗？（**认证 attestation**）

OKF v0.2将来源、信任、生命周期、认证作为一等公民，同时保持格式最小化约定。

### 1.2 目标与非目标

**目标**：
1. 定义一个生产者（人、Agent、导出管道）可以写入的通用格式
2. 指导消费者（Agent、UI、搜索索引、确定性代码）如何读取和遍历
3. 促进跨系统、跨组织的知识交换
4. 标准化使Agent维护的语料库**可信**所需的最小frontmatter字段集，不规定任何运行时

**非目标**：
- 定义固定的概念类型分类法
- 规定存储、服务或查询基础设施
- 取代领域特定Schema（Avro、Protobuf、OpenAPI等）——OKF引用它们，而非包含它们
- 指定执行器或认证器指向的代码的打包或调用标准——OKF固定接口，不固定打包

---

## 二、核心术语

| 术语 | 定义 |
|------|------|
| **Knowledge Bundle（知识包）** | 自包含的、层次化的知识文档集合，分发单元 |
| **Concept（概念）** | Bundle中的单个知识单元，表示为一个Markdown文档。可以描述有形资产（表、API）或抽象概念（指标、业务流程） |
| **Concept ID** | 概念文件在Bundle内的路径，去掉`.md`后缀 |
| **Frontmatter** | Markdown文件顶部由`---`分隔的YAML元数据块 |
| **Body（正文）** | Frontmatter之后的文件全部内容 |
| **Link（链接）** | 从一个概念到另一个概念的标准Markdown链接，用于表达目录层次之外的关系 |
| **Source（来源）** | 概念派生自的材料（Bundle外部或内部），记录在`sources` frontmatter字段中 |
| **Actor（执行者）** | 标识执行动作的人或物的字符串，约定为`<producer>/<version>`（Agent）、`human:<id>`（人）、`process:<id>`（自动化流程） |
| **Trust Tier（信任层级）** | 从`verified`字段推导出的级别：unverified / machine-confirmed / human-reviewed |
| **Attested Computation（认证计算）** | 类型为`Attested Computation`的概念，携带计算值的认可方式，消费者可以确认该值是通过运行它产生的 |

---

## 三、Bundle结构

### 3.1 目录布局

Bundle是Markdown文件的目录树。目录结构独立于领域——生产者按照对所捕获知识有意义的方式组织概念。

```
path/to/bundle/
  index.md                      # 可选。目录列表，用于渐进式披露
  log.md                        # 可选。更新时间线历史
  <concept>.md                  # Bundle根目录的概念
  <subdirectory>/               # 子目录将概念分组
    index.md
    <concept>.md
    <subdirectory>/
      ...
```

Bundle可以分发为：
- Git仓库（推荐，因为提供历史、归属和diff）
- 目录的tarball或zip归档
- 更大仓库中的子目录

### 3.2 保留文件名

以下文件名在层次结构的任何级别都有定义含义，**不得**用于概念文档：

| 文件名 | 用途 |
|--------|------|
| `index.md` | 目录列表，见§8 |
| `log.md` | 更新历史，见§9 |

所有其他`.md`文件都是概念文档。

---

## 四、概念文档

每个概念是一个UTF-8 Markdown文件，包含两部分：

1. **YAML frontmatter块**：以文件开头单独一行的`---`开始，以单独一行的`---`结束
2. **Markdown正文**：自由格式内容

### 4.1 Frontmatter字段

```yaml
---
type: <Type name>                  # 必填
title: <可选显示名称>
description: <可选单行摘要>
resource: <可选底层资产的规范URI>
tags: [<tag>, <tag>, ...]          # 可选
# ... 信任、生命周期、来源和计算族字段（见§5、§10）
# ... 其他生产者定义的键值对
---
```

#### 必填字段

**`type`**：标识概念类型的短字符串。消费者用于路由、过滤和展示。示例值：
- `BigQuery Table`、`BigQuery Dataset`、`API Endpoint`、`Metric`
- `Playbook`、`Reference`、`Attested Computation`

类型值**不**集中注册。生产者应选择描述性、不言自明的值；消费者必须优雅容忍未知类型，通常将它们视为通用概念。

`type`是唯一始终必填的键；仅携带`type`的概念就是完全符合规范的。

#### 推荐字段

| 字段 | 用途 |
|------|------|
| `title` | 人类可读的显示名称。省略时消费者可从文件名推导 |
| `description` | 概括概念的单句话，用于`index.md`生成器、搜索摘要和预览 |
| `resource` | 唯一标识概念描述的底层资产的URI。描述抽象概念而非物理资源时省略 |
| `tags` | 短字符串YAML列表，用于跨领域分类 |

还可以出现可选的**来源、信任、生命周期**族（§5）和认证计算概念的**计算**字段（§10）。

#### 扩展机制

生产者**可以**包含任何额外键。消费者在往返时应保留未知键，且**不得**因无法识别的字段拒绝文档。

### 4.2 正文

正文是标准Markdown。生产者应优先使用结构化Markdown（标题、列表、表格、围栏代码块）而非自由散文，因为结构有助于人类阅读和Agent检索。

没有必需的正文章节。以下标题具有**约定俗成**的含义，适用时应使用：

| 标题 | 用途 |
|------|------|
| `# Schema` | 资产列/字段的结构化描述 |
| `# Examples` | 具体使用示例，通常为围栏代码块 |
| `# Computation` | 认证计算的认可计算，见§10 |

### 4.3 示例：绑定到资源的概念

```markdown
---
type: BigQuery Table
title: Customer Orders
description: One row per completed customer order across all channels.
resource: https://console.cloud.google.com/bigquery?p=acme&d=sales&t=orders
tags: [sales, orders, revenue]
generated: { by: reference_agent/gemini-2.5-pro, at: 2026-05-28T14:30:00Z }
---

# Schema

| Column        | Type      | Description                              |
|---------------|-----------|------------------------------------------|
| `order_id`    | STRING    | 全局唯一订单标识符                        |
| `customer_id` | STRING    | 外键，关联[customers](/tables/customers.md) |
| `total_usd`   | NUMERIC   | 订单总金额（美元）                        |
| `placed_at`   | TIMESTAMP | 客户提交订单时间                          |

# Joins

通过`customer_id`与[customers](/tables/customers.md)关联。
```

### 4.4 示例：不绑定到资源的概念

```markdown
---
type: Playbook
title: "事件响应：数据新鲜度告警"
description: 对订单管道新鲜度告警进行分诊的步骤。
tags: [oncall, incident]
generated: { by: human:ahormati, at: 2026-04-12T09:00:00Z }
---

# 触发条件

当`orders`滞后于预期SLA超过30分钟时触发新鲜度告警。参见[orders表](/tables/orders.md)。

# 步骤

1. 检查[摄入作业仪表板](https://example.com/dash)
2. ...
```

---

## 五、来源、信任与生命周期

这些frontmatter族使"这从哪来"、"我该多信任它"、"它现在还有效吗"可以从frontmatter回答。全部可选。它们的缺失本身有意义：未验证的概念与已验证的概念可区分，但永远不会被拒绝。

### 5.1 来源：`sources`

`sources`记录概念派生自的材料，外部或Bundle内部。

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

每个`sources`条目：
- `resource`：条目内**必填**。命名消费者可以跟随的具体工件（绝对URL、Bundle相对路径、`references/`子目录路径），或无法跟随的范围描述符（例如`BigQuery项目X中的所有查询`）
- `id`：可选。用于归属单个声明的稳定键。正文引用来源时应存在
- `title`：可选。来源的人类可读标签
- 可选的可信度信号`author`、`usage_count`、`last_modified`，如下所述

**来源可信度信号**：OKF记录客观的、每个来源的信号，消费者可以通过判断概念提取自的来源来判断信任度。它不存储可信度分数——分数是主观的、跨消费者不可移植、会过时。可信度从信号*推断*，与信任层级一样（§5.3），而非存储。

| 信号 | 含义 | 说明 |
|------|------|------|
| `author` | 谁/什么产生了来源（Actor约定§7） | 权威性信号 |
| `usage_count` | 在`usage_window`内`resource`被使用的次数 | 采用度和活跃度信号 |
| `last_modified` | 来源本身最后更改日期(`YYYY-MM-DD`) | 新近度信号 |
| `usage_window` | 作为`sources`兄弟节点一次写入，为每个`usage_count`框定`{from, to}`日期范围 | 时间窗口上下文 |

**逐声明归属**：要归属特定声明，使用Markdown脚注，其标签为`sources[].id`：

```markdown
`events_`表按日分片为`events_YYYYMMDD`。[^ga4-schema]

[^ga4-schema]: GA4 BigQuery Export schema
```

脚注标签是`sources`的连接键；消费者通过匹配条目解析归属，而非解析脚注散文。使用键式标签而非位置式（`sources[0]`）是因为Agent不断重写这些文档：列表重新排序时位置索引会静默错误归属，而稳定的`id`在重排序后仍然有效。

### 5.2 信任：`generated`和`verified`

`generated`记录当前内容是如何产生的。`verified`记录谁/什么已根据其来源或`resource`确认了内容。它们保持区分，因为*编写*概念的人不一定是*确认*它的人。

```yaml
generated: { by: reference_agent/gemini-2.5-pro, at: 2026-06-20T22:53:05Z }
```

- `generated.by`：`generated`内**必填**。执行者（§7）
- `generated.at`：ISO 8601日期时间，标记内容最后一次有意义更改的时间

```yaml
verified:
  - { by: human:ahormati, at: 2026-06-25T09:00:00Z }
  - { by: process:finance-nightly, at: 2026-06-26T02:00:00Z }
```

- `verified`：验证事件列表，每个有`by`（执行者）和`at`（ISO 8601日期时间）。多个条目捕获独立检查，例如人工签署加夜间流程
- `verified`独立于`generated.at`：内容可以更改而不重新确认，事实可以重新确认而不重新生成
- 单个验证者可以写为一个`{by, at}`映射而不用列表破折号。消费者必须将裸映射视为单元素列表：

```yaml
verified: { by: human:ahormati, at: 2026-06-25T09:00:00Z }
```

### 5.3 信任层级

消费者从`verified`推导出信任层级（从低到高）：
- 无`verified`键 → **unverified（未验证）**
- 仅由非`human:`执行者验证 → **machine-confirmed（机器确认）**
- 由`human:<id>`执行者验证 → **human-reviewed（人工审核）**

没有信任frontmatter的概念仍然可以消费；消费者**不得**拒绝它。信任层级是建议性信号，不是访问控制。

### 5.4 生命周期：`status`

```yaml
status: stable        # draft | stable | deprecated
```

- `draft`：尚未审核；可能不完整
- `stable`：默认值；可供消费
- `deprecated`：保留用于链接和历史；不再最新

省略`status` → `stable`。

### 5.5 生命周期：`stale_after`

```yaml
stale_after: 2026-09-23   # 绝对日期；此日当天及之后内容过时
```

可选。绝对日期（`YYYY-MM-DD`）。当`today >= stale_after`时概念过时。使用绝对日期而非相对TTL，使过时判断成为简单的日期比较，无需引用概念读取时间。

---

## 六、交叉链接与路径

### 6.1 概念之间的链接

概念可以使用标准Markdown链接链接到其他概念。支持两种形式：

- **绝对（Bundle相对）**：以`/`开头，相对于Bundle根解释。**推荐**形式，因为文档在其子目录内移动时稳定。
  ```markdown
  参见[customers表](/tables/customers.md)了解连接键。
  ```

- **相对**：标准Markdown相对路径。
  ```markdown
  参见[相邻概念](./other.md)。
  ```

从概念A到概念B的链接断言一个*关系*。具体类型（父子、引用、连接、依赖）由周围散文传达，而非链接本身。构建图视图的消费者通常将所有链接视为无类型关系的有向边。

消费者必须容忍断链：目标不存在于Bundle中的链接不是格式错误；它可能只是表示尚未编写的知识。

### 6.2 路径值字段

几个字段命名路径或URI：`resource`、`sources[].resource`、`computation`、`executor.resource`、`attester.resource`（§10）。`sources[].resource`可以是范围描述符（§5.1），这种情况下它不是路径。每个路径值字段接受：
- 绝对URL（例如`https://...`）
- 以`/`开头的Bundle相对路径，或
- 相对路径（例如`../computations/revenue.md`）

### 6.3 `references/`约定

`references/`子目录约定俗成地将外部材料、运行指令或代码镜像为Bundle中的一等公民概念。来源、执行器和认证器通常指向其中（例如`references/attesters/revenue.py`）。这是命名约定，不是要求。

---

## 七、执行者约定

记录身份的字段（`generated.by`、`verified[].by`）使用单一执行者约定：

- `<producer>/<version>` 用于Agent和工具，例如`reference_agent/gemini-2.5-pro`
- `human:<id>` 用于人，例如`human:ahormati`
- `process:<id>` 用于自动化流程，例如`process:finance-nightly`

对信任进行分类的消费者（§5.3）以`human:`前缀为键，因此生产者必须对手工编写或人工确认的内容使用该前缀。

---

## 八、索引文件

`index.md`文件可以出现在任何目录中，包括Bundle根目录。它枚举目录内容以支持**渐进式披露**：让人类或Agent在打开单个文档之前先了解有什么可用。

索引文件不包含frontmatter，除了一个例外：Bundle根`index.md`可以携带`okf_version`键（§12）。正文使用一个或多个章节，每个章节在标题下分组概念：

```markdown
# 章节/分组标题

* [标题1](relative-url-1) - 条目1的简短描述
* [标题2](relative-url-2) - 条目2的简短描述

# 另一个章节

* [子目录](subdir/) - 子目录的简短描述
```

条目应包含链接概念frontmatter中的描述。生产者可以自动生成`index.md`；不存在时消费者可以即时合成一个。

---

## 九、日志文件

`log.md`文件可以出现在层次结构的任何级别，以记录该范围变更的历史。格式为按日期分组的条目平面列表，最新在前：

```markdown
# 目录更新日志

## 2026-05-22
* **Update**：为[Customer Metrics](/tables/customer-metrics.md)添加了BigQuery表引用。
* **Creation**：建立了[Dataplex Playbook](/playbooks/dataplex.md)。

## 2026-05-15
* **Initialization**：创建了基础目录结构。
```

日期标题必须使用ISO 8601 `YYYY-MM-DD`格式。日志条目是散文；开头粗体词（`**Update**`、`**Creation**`、`**Deprecation**`）是约定，不是要求。

---

## 十、认证计算概念

认证计算概念不仅携带值的*含义*，还携带*计算*它的认可方式，消费者可以确认Agent运行了受祝福的计算而非即兴自己编写。来源（§5.1）回答"这个声明从哪来"；认证回答"这个数字是按我们说的方式产生的吗"。OKF记录计算和检查它的方法；它自己不执行任何东西。

### 10.1 计算是独立概念

认可计算是`type: Attested Computation`的独立概念。需要该值的概念（`Metric`、`BigQuery Table`）使用普通Markdown链接链接到它（§6）。三个特性促使独立概念：

1. **`runtime`定义`parameters`的含义**：参数是SQL绑定变量、dbt变量还是Python参数取决于runtime。将`runtime`和`parameters`保持在一个frontmatter中使绑定语义不言自明
2. **一个计算，多个消费者**：同一计算可以支撑指标、仪表板概念和报告；作为概念它被引用一次并复用
3. **信任状态按计算独立**：`verified`、`stale_after`和单个`attester`描述一件事。收入、利润和利润率各自独立验证和认证，这是三个概念，不是一个frontmatter中的三个条目

### 10.2 契约字段

契约是概念的顶层frontmatter。除了来源、信任、生命周期族（§5），认证计算概念还携带：

- `runtime`：此类型**必填**。说明如何运行计算的单个字段，因此执行器和认证器如何解释它以及`parameters`的含义。示例值：`bigquery`、`postgres`、`dbt`、`python`、`Looker`
- `parameters`：Agent可以填充的类型化、命名洞的列表。每个条目：`{name, type, required}`。绑定语义遵循`runtime`
- `computation`：可选。包含计算的文件路径（§6.2），用于替代内联正文围栏（见§10.3）。省略 ⇒ 正文`# Computation`围栏就是计算
- `executor`：计算如何运行。`resource`命名运行指令或代码；运行器（Agent或确定性消费者代码）遵循它。`receipt`声明运行必须返回的字段——认证器检查的证据（例如BigQuery `job_id`和作业实际执行的SQL）
- `attester`：确定性检查。`resource`命名（非LLM）代码，它接收receipt并返回裁决。它旨在消费者侧运行。

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

计算仅绑定声明的`parameters`，按确认政策。[^rev-policy]

[^rev-policy]: Revenue recognition policy
```

### 10.3 计算提供方式

以两种方式之一提供计算：

- **内联**：正文`# Computation`下的单个围栏代码块。最适合与契约一起审查的短计算
- **文件**：将`computation`设置为路径（§6.2）并省略正文围栏。最适合长的或生成的计算，或已作为与非OKF工具共享的真实文件保存的计算

```yaml
runtime: bigquery
computation: references/computations/lib/revenue.sql
parameters:
  - { name: year, type: integer, required: true }
```

Agent**只能**为声明的`parameters`提供*值*；它**不得**编写或编辑计算。将`computation`与参数值绑定到可执行工件中是消费者的工作，认证器独立重新推导相同绑定以与实际运行的进行比较。因为比较是在receipt携带的扩展、编译工件上进行的（`executed_sql`、`compiled_sql`），重写的查询、交换的计算文件或变异的依赖项都会使检查失败。类型化、仅参数的表面是"是否运行了认可的内容"成为机械比较而非判断调用的原因。

---

## 十一、符合规范

Bundle符合OKF v0.2的条件是：

1. 树中每个非保留`.md`文件包含可解析的YAML frontmatter块
2. 每个frontmatter块包含非空的`type`字段
3. 每个保留文件名（`index.md`、`log.md`）存在时分别遵循§8和§9的结构

当存在信任、生命周期、来源或计算族时，生产者应遵循§5至§10，消费者：
- 必须将裸`verified`映射视为单元素列表（§5.2）
- 不得因缺少任意味族拒绝概念（§5.3）
- 应仅从此处指定的字段推导信任层级和过时性，并应展示而非静默丢弃失败的认证（§10.5）

消费者应将所有其他约束视为软指导。特别是，消费者**不得**因以下原因拒绝Bundle：
- 缺少可选frontmatter字段
- 未知`type`值
- 未知额外frontmatter键
- 断链
- 缺少`index.md`文件

---

## 十二、版本控制

- **次版本号**增加：引入向后兼容的添加（新可选字段、新约定章节标题）
- **主版本号**增加：可能进行破坏性更改（重命名字段、更改保留文件名）

Bundle可以在Bundle根`index.md` frontmatter块中用`okf_version: "0.2"`声明目标版本（`index.md`中唯一允许frontmatter的地方）。不理解声明版本的消费者应尝试尽力消费而非拒绝Bundle。

---

继续阅读：[02-reference-agent.md - 参考智能体实现](./02-reference-agent.md)
