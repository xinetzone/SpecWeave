---
id: "okf-wiki-core-concepts"
title: "01 核心概念与设计哲学"
version: "1.0"
source: "okf.md spec v0.2 + GoogleCloudPlatform/knowledge-catalog"
type: "Wiki Tutorial"
description: "OKF三大设计原则深度解读、术语表、Bundle结构、Concept文件规范、链接规则、索引与日志"
tags: ["OKF", "设计原则", "Frontmatter", "Bundle", "Concept"]
category: "learning"
date: "2026-08-05"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "深入解析OKF的极简设计哲学：最少约定、生产者消费者解耦、格式而非平台；完整介绍Bundle/Concept/Frontmatter等核心概念和规范"
last_verified: "2026-08-05"
wiki_version: "1.0"
okf_version_target: "v0.2"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/knowledge/learning/01-agent-protocols-interfaces/okf-wiki/01-core-concepts.toml"
---

# 01 核心概念与设计哲学

## 1.1 最少约定原则（Minimally Opinionated）

OKF只强制要求**一个字段**：`type`。其他一切都是可选的、开放的。

**为什么**：知识管理标准如果规定太多就没人用了。OKF选择极端极简——不需要注册中心、不需要审批、不需要学复杂本体论，今天就能开始写。

**权衡**：自由带来混乱风险。但OKF认为命名治理是**团队层面**的问题，不是标准层面的——标准只提供互操作基础，约定通过设计文档和code review补充。

**示例自定义类型**：`type: dbt Model`、`type: Kafka Topic`、`type: 应急响应Playbook`，无需任何批准。

## 1.2 生产者-消费者解耦（Producer/Consumer Independence）

谁写知识和谁读知识彻底分离：人写的Bundle可以被Agent读，Agent生成的Bundle可以被人浏览，一个LLM生成的可以被另一个厂商LLM查询——格式是唯一契约，两端工具可独立替换。

**为什么**：避免平台锁定。就像HTML不关心是VS Code写的还是Word写的，也不关心Chrome还是Safari打开。如果绑定到某框架或某LLM厂商，知识就成了平台人质。

**权衡**：生产者无法控制消费者如何渲染。但这正是HTML的成功之道——内容和展示分离，好消费者提供更好体验，而非强迫生产者迁就单一消费者。

## 1.3 格式而非平台（Format, Not Platform）

OKF不绑定任何云厂商、数据库、模型供应商、Agent框架，永远不需要专有账号或SDK来读写。

**为什么**：HTML成功在于它是开放标准，不属于任何公司。Tim Berners-Lee没申请专利、没建中央服务器、没要求注册账号。W3C是标准组织，但HTML本身是纯文本，任何编辑器都能写，任何浏览器都能读。OKF想走同样的路——价值在于有多少人用这个格式，而不在于谁拥有它。

**权衡**：没有中心平台意味着没有官方托管/搜索/UI，需要社区和第三方建设。但这也让生态多样化——Git仓库、静态网站、IDE插件、检索工具可基于同一格式共存。

## 1.4 核心术语对照表

| 术语 | 英文 | 定义 |
|------|------|------|
| 知识包 | Knowledge Bundle | 自包含的知识文档集合，OKF分发和版本控制基本单元 |
| 概念 | Concept | Bundle内一个知识单元，对应一个markdown文件 |
| 概念ID | Concept ID | Bundle内文件相对路径（去掉.md后缀） |
| 元数据头 | Frontmatter | YAML元数据块，文件开头`---`分隔 |
| 正文 | Body | Frontmatter之后的markdown内容 |
| 链接 | Link | 概念间标准markdown链接，表示语义关系 |
| 引用 | Citation | 指向外部来源的链接，支撑正文中的主张 |
| 索引文件 | Index File | 保留文件名`index.md`，目录内容列表 |
| 日志文件 | Log File | 保留文件名`log.md`，变更历史记录 |

> **Obsidian对照**：Bundle≈Vault，Concept≈Note。区别在于OKF定义了最小互操作规则（强制type、保留文件名、链接规范），确保跨工具可读。

## 1.5 Bundle目录结构规范

Bundle是markdown文件目录树，目录结构由生产者自行组织。

**保留文件名**（任何层级不能用作Concept文件名）：
- `index.md`：目录列表/渐进式披露（见1.9）
- `log.md`：更新历史（见1.10）

其他所有`.md`文件都是Concept文档。

**分发形式**：Git仓库（推荐，天然支持版本控制和PR评审）、zip/tarball、monorepo子目录（最常见实践：`knowledge/`或`docs/catalog/`）。

**目录树示例**：
```
my-catalog/
├── index.md
├── log.md
├── concepts/tables/
│   ├── customers.md
│   ├── orders.md
│   └── index.md
├── concepts/metrics/
│   ├── ltv.md
│   └── churn.md
└── playbooks/incident-response.md
```

## 1.6 Concept文件结构

每个Concept是UTF-8编码markdown文件，分两部分：YAML frontmatter + markdown body。

### Frontmatter字段家族

| 字段 | 必填 | 说明 |
|------|------|------|
| `type` | ✅ | 概念类型（Metric/Table/Playbook等），不集中注册，生产者自描述 |
| `title` | ⭐推荐 | 人类可读名称，省略则从文件名推导 |
| `description` | ⭐推荐 | 一句话摘要，用于索引/搜索/预览卡片 |
| `resource` | 可选 | 所描述资产的规范URI（如BigQuery表链接），抽象概念可省略 |
| `tags` | 可选 | YAML列表，横切分类标签 |
| `timestamp` | 可选 | ISO 8601格式，最后重大更新时间 |
| `sources` | v0.2 | 来源数组：resource/id/title/author/usage_count/last_modified |
| `generated` | v0.2 | 生成者信息（用于可信度评估） |
| `verified` | v0.2 | 验证者列表（人类/机器验证记录） |
| `status` | v0.2 | 生命周期状态（draft/stable/deprecated等） |
| `stale_after` | v0.2可选 | 过期时间，知识保鲜机制 |
| 扩展字段 | 允许 | 生产者可添加自定义key，消费者必须保留未知字段 |

> **为什么type不集中注册？** 自由但需治理：同一公司可能有人用`type: Table`有人用`type: BigQuery Table`指同一事物。这不是标准要解决的，而是团队需提前约定命名规范。

## 1.7 Body编写规范

- 标准markdown，优先结构化内容（标题、列表、表格、围栏代码块）
- 约定标题（**非强制，强烈推荐**）：`# Schema`（资产字段描述）、`# Examples`（使用示例）、`# Citations`（外部引用）

**为什么结构对Agent重要**：清晰标题让RAG检索更准——Agent可直接跳到`# Schema`获取字段定义，而非解析大段自由文本，大幅减少幻觉。结构化 = 更高检索准确率。

## 1.8 跨链接规则

两种链接形式：
- **Bundle绝对链接**（推荐）：以`/`开头，相对于Bundle根目录解析，如`[customers](/tables/customers.md)`，移动子目录时稳定
- **相对链接**：标准markdown相对路径，如`[neighbor](./other.md)`

**链接语义**：A链接到B表示有关系（父子/连接/依赖/相关），关系类型由上下文文字表达，不由链接语法表达。OKF不做RDF式谓词标准化。

### 重要特性：断链是特性，不是bug

- 可以先写`[refunds table](/tables/refunds.md)`再创建文件
- 引用先行，填充在后——支持增量式文档化
- 不要求所有引用必须存在才是"有效"Bundle
- 消费者**必须**容忍断链：断链只表示知识尚未编写，不是格式错误

这就像维基百科的红链——告诉你"这里该有篇文章但还没写"，而不是报错。

## 1.9 Index Files（索引文件）

- 任何目录（包括Bundle根）都可以有`index.md`
- **index.md没有frontmatter**（保留文件特性）
- 作用：渐进式披露——不用打开每个文件就知道目录里有什么
- 结构：按逻辑分组，列出Concept链接 + description
- 可自动生成，也可手写；没有index.md时消费者可动态扫描生成

**Shell自动化生成示例**：
```bash
#!/bin/bash
echo "# Concepts Index" > index.md
for f in *.md; do
  if [ "$f" != "index.md" ] && [ "$f" != "log.md" ]; then
    desc=$(grep -m1 '^description:' "$f" | cut -d'"' -f2)
    title=$(grep -m1 '^title:' "$f" | cut -d'"' -f2)
    echo "- [$title](./$f) — $desc" >> index.md
  fi
done
```

## 1.10 Log Files（日志文件）

- 任何层级都可以有`log.md`
- 作用：该范围的**高层变更历史**（类似CHANGELOG），不是逐条commit记录
- 格式：按ISO日期（YYYY-MM-DD）倒序排列，每个日期下是条目

**log.md vs git log**：git log是细粒度提交历史（"修复typo"）给开发者看；log.md是高层摘要（"5月新增客户指标表"）给人类/Agent快速浏览演变脉络。

**格式约定**（非强制）：每条目以粗体动词开头——**Create**/**Update**/**Deprecation**。

## 1.11 Citations引用规范

Body中主张基于外部资料时，必须在文档末尾`# Citations`下列出编号来源。v0.2支持markdown脚注（`[^source-id]`）逐句归因，关联到sources条目。

**为什么对Agent重要**：当LLM说"X表新鲜度SLA是30分钟"时，citation让你能追溯来源——是SLI文档？监控仪表盘？还是某人口头说的？没有引用，Agent就会自信地幻觉——引用是对抗幻觉的关键机制。

## 1.12 完整代码示例

### 示例一：BigQuery表（有资源链接）

````markdown
---
type: Table
title: Customer Orders
description: 客户订单核心事实表
resource: bigquery://my-project/analytics.orders
tags: [core, fact-table]
status: stable
owner: data-team@company.com
---
# Schema
| 字段 | 类型 | 说明 |
|------|------|------|
| order_id | STRING | 订单唯一ID |
| customer_id | STRING | 关联 [customers](/tables/customers.md) |
| amount | FLOAT64 | 订单金额（USD） |
| created_at | TIMESTAMP | 下单时间 |
# Examples
```sql
SELECT DATE(created_at) dt, COUNT(*) orders
FROM `analytics.orders` WHERE created_at > '2026-01-01' GROUP BY 1
```
# Citations
[^1]: Data Catalog entry, updated 2026-07-15
````

### 示例二：SRE Playbook（抽象概念）

```markdown
---
type: Playbook
title: 生产故障响应流程
description: P0/P1故障响应标准步骤
tags: [incident, oncall, sre]
status: stable
stale_after: P6M
---
# Trigger
- PagerDuty告警触发
- 客户报告大面积不可用
- 监控指标异常超阈值5分钟
# Steps
1. **确认（0-5min）**：值班SRE确认真实性，#incident开线程
2. **定级（5-10min）**：根据影响面定P0/P1/P2
3. **缓解（10-30min）**：优先回滚而非debug，参考[rollback](/playbooks/rollback.md)
4. **沟通（全程）**：每30分钟更新状态
5. **根因（事后）**：24小时内提交RCA
# Citations
[^1]: SRE Handbook v2.3, Chapter 5
```

### 示例三：Metric指标定义

````markdown
---
type: Metric
title: 90天LTV
description: 用户首次付费后90天累计收入
tags: [revenue, retention, core-metric]
status: stable
owner: growth-team@company.com
---
# Definition
```sql
WITH first_pay AS (
  SELECT user_id, MIN(paid_at) first_paid_at FROM payments GROUP BY 1
)
SELECT DATE_TRUNC(fp.first_paid_at, MONTH) cohort,
       AVG(COALESCE(SUM(p.amount), 0)) ltv_90d
FROM first_pay fp LEFT JOIN payments p ON fp.user_id = p.user_id
  AND p.paid_at BETWEEN fp.first_paid_at
      AND TIMESTAMP_ADD(fp.first_paid_at, INTERVAL 90 DAY)
GROUP BY 1
```
# Limitations
- 只统计付费用户，免费用户LTV视为0
- 不含退款调整，需结合[refund-rate](/metrics/refund-rate.md)修正
- 新cohort（不足90天）为预测值
# Citations
[^1]: Growth Metrics Spec v1.2, 2026-06-01
````

| 上一章 | 目录 | 下一章 |
|--------|------|--------|
| [00 概述与知识地图](./00-overview.md) | [README](./README.md) | [02 快速入门](./02-quickstart.md) |
