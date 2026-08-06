---
id: "knowledge-catalog-wiki-reference-agent"
title: "03 参考Agent实现原理与运行指南"
version: "1.0"
source: "GoogleCloudPlatform/knowledge-catalog okf/src/reference_agent/"
type: "Wiki Tutorial"
description: "knowledge-catalog参考Agent实现原理深度解析，两阶段工作流（BQ pass→Web pass）详解、enrich命令参数说明、核心模块架构、CLI使用示例、单概念迭代方法、凭证配置"
tags: ["Knowledge Catalog", "OKF", "Reference Agent", "实现原理", "CLI", "BigQuery", "Web Crawler", "两阶段工作流"]
category: "learning"
date: "2026-08-06"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "从源码角度深度解析knowledge-catalog参考Agent的实现机制，包括两阶段工作流架构、enrich子命令完整参数说明、核心工具模块（bundle/source/web/context）、CLI使用示例、单概念迭代开发方法以及GCP凭证配置指南"
last_verified: "2026-08-06"
wiki_version: "1.0"
okf_version_target: "v0.2"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/knowledge/learning/01-agent-protocols-interfaces/knowledge-catalog-wiki/03-reference-agent.toml"
---

# 03 参考Agent实现原理与运行指南

> **本章定位说明**
> - 前两章从规范视角介绍了OKF格式（[01 核心概念与平台架构](./01-core-concepts.md)、[02 OKF规范深度解析](./02-okf-specification.md)）。
> - 本章从**源码实现视角**出发，系统讲解knowledge-catalog参考Agent（reference agent）的内部工作原理、模块架构和使用方法。
> - 参考Agent是OKF格式的**概念验证生产者（Proof of Concept Producer）**，演示了如何自动化从数据源（BigQuery）和权威文档自动生成OKF Bundle。
> - 首次使用建议先完成 [okf-wiki 5分钟快速入门](../okf-wiki/02-quickstart.md) 的手工实操，建立OKF Bundle的感性认识后再阅读本章。

## 3.1 架构总览：两阶段工作流设计

参考Agent采用**两阶段流水线（Two-Pass Pipeline）**架构，将结构化元数据提取与非结构化文档抓取解耦，确保知识生成的可信度和可控性。

### 3.1.1 两阶段工作流概览

```
┌─────────────────────────────────────────────────────────────────┐
│                     Reference Agent 两阶段流水线                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐     ┌──────────────┐     ┌─────────────────┐  │
│  │   BQ Pass    │────▶│   Web Pass   │────▶│ Index Regen     │  │
│  │  (第一阶段)   │     │  (第二阶段)   │     │  (索引重建)      │  │
│  └──────────────┘     └──────────────┘     └─────────────────┘  │
│         │                    │                      │           │
│         ▼                    ▼                      ▼           │
│  基于BigQuery元数据    LLM作为自主爬虫          自动生成各级       │
│  生成每个Concept的     从种子URL出发，          index.md         │
│  基础文档（Schema、    抓取权威文档，                              │
│  分区、采样等）        充实Concept内容                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

两阶段设计的核心考量：

1. **事实基础先行**：BQ Pass直接从数据源元数据生成不可篡改的结构化事实（Schema、分区、行数等），作为知识的"可信基座"。
2. **文档充实在后**：Web Pass基于已有的Concept列表，LLM自主判断哪些外部文档值得抓取、如何充实现有文档或创建独立引用文档。
3. **增强保护机制**：Web Pass阶段写入时会进行增强保护（Augmentation Guard）——禁止缩小BQ Pass生成的Schema字段集和sources列表，防止LLM覆盖结构化事实（参见 §3.4.1 bundle_tools.py）。

### 3.1.2 工作流执行顺序

执行入口位于 `runner.py:ReferenceRunner.enrich_all()`，执行顺序严格固定：

```python
# runner.py:264-285
def enrich_all(self, only: list[tuple[str, ...]] | None = None) -> int:
    concepts = self.source.list_concepts()
    # ... 过滤 only 指定的概念 ...
    
    # 阶段1：BQ Pass - 逐个概念处理
    for ref in concepts:
        self.enrich_concept(ref)
    
    # 阶段2：Web Pass - 网络文档抓取与充实
    self.run_web_pass()
    
    # 阶段3：重建所有 index.md 文件
    regenerate_indexes(self.bundle_root, model=self.model)
```

两阶段通过**独立Agent实例**执行（`agent.py:build_bq_agent()` 和 `agent.py:build_web_agent()`），各自拥有独立的工具集和提示词，确保职责分离。

## 3.2 BQ Pass详解：结构化元数据生成

BQ Pass是第一阶段，负责从BigQuery数据源直接提取结构化元数据，为每个Concept生成基础OKF文档。

### 3.2.1 BQ Agent工具集

BQ Agent（`agent.py:27-39`）配备5个工具：

| 工具 | 源码位置 | 功能 |
|------|----------|------|
| `list_concepts` | `tools/source_tools.py:18-27` | 列出数据源中所有可用Concept（表、数据集等） |
| `read_concept_raw` | `tools/source_tools.py:30-42` | 获取单个Concept的原始结构化元数据（Schema、分区、聚簇、行数、时间戳等） |
| `sample_rows` | `tools/source_tools.py:45-64` | 从底层资产抽取少量样例行（支持时） |
| `read_existing_doc` | `tools/bundle_tools.py:73-87` | 读取Bundle中已存在的文档（增量更新时使用） |
| `write_concept_doc` | `tools/bundle_tools.py:90-191` | 写入/覆写OKF Concept文档 |

注意：BQ Agent**没有**`fetch_url`工具，确保第一阶段无法访问网络，完全基于数据源元数据生成。

### 3.2.2 BQ Pass执行流程

对每个Concept，Runner发送标准用户消息（`runner.py:113-120`）触发Agent执行标准工作流：

```
Enrich the concept with id: {ref.id_str}
OKF type: {ref.type}
Follow the standard workflow and write exactly one document for this concept.
```

Agent按照提示词（`prompts/reference_instruction.md`）执行：
1. 调用 `read_concept_raw` 获取完整元数据
2. 必要时调用 `sample_rows` 查看数据样例
3. 调用 `read_existing_doc` 检查是否已有文档（增量模式）
4. 生成符合OKF规范的Markdown文档，包含 `# Schema`、`# Common query patterns` 等章节
5. 调用 `write_concept_doc` 写入文件

## 3.3 Web Pass详解：LLM自主爬虫与文档充实

Web Pass是第二阶段，LLM作为自主爬虫从种子URL出发，抓取权威文档并充实Bundle内容。

### 3.3.1 Web Agent工具集

Web Agent（`agent.py:42-54`）配备5个工具，比BQ Agent多了网页抓取能力：

| 工具 | 源码位置 | 功能 |
|------|----------|------|
| `list_concepts` | `tools/source_tools.py:18-27` | 列出Bundle中所有已有Concept（用于判断链接是否相关） |
| `read_concept_raw` | `tools/source_tools.py:30-42` | 重新读取数据源元数据（验证事实） |
| `read_existing_doc` | `tools/bundle_tools.py:73-87` | 读取现有Concept文档（以便增强而非覆写） |
| `write_concept_doc` | `tools/bundle_tools.py:90-191` | 写入文档（带增强保护机制） |
| `fetch_url` | `tools/web_tools.py:10-101` | 抓取网页，返回Markdown内容和出站链接 |

### 3.3.2 爬取预算与安全约束

Web Pass的核心设计原则是**严格预算控制**——所有约束在工具层强制执行，而非依赖LLM自觉（`tools/web_tools.py`）：

| 约束类型 | 参数 | 默认值 | 执行位置 |
|----------|------|--------|----------|
| **页面数硬上限** | `--web-max-pages` | 100 | `web_tools.py:62-63` 计数检查 |
| **跳数深度上限** | `--web-max-depth` | 2 | `web_tools.py:75-78` 深度检查（种子=0，种子链接=1） |
| **允许主机名** | `--web-allowed-host` | 仅种子主机名 | `web_tools.py:44-48` 主机白名单 |
| **允许路径前缀** | `--web-allowed-path-prefix` | 无限制 | `web_tools.py:50-56` 路径前缀过滤 |
| **拒绝路径子串** | `--web-denied-path-substring` | 无 | `web_tools.py:57-59` 路径黑名单（如`/login`、`/pricing`） |
| **已访问去重** | 自动 | - | `web_tools.py:60-61` visited集合 |

**关键安全设计**：
- 所有约束在`fetch_url`工具内部强制执行，LLM收到拒绝响应时必须停止或选择其他URL，禁止重试被拒URL（`web_tools.py:18-19`）。
- 未知URL（非种子且未被任何已抓取页面作为链接返回）直接拒绝（`web_tools.py:66-74`），防止LLM"编造"URL绕过爬取图。
- 深度通过`WebState.url_depth`字典追踪：种子URL预注册为深度0，其子链接自动设为深度1，依此类推（`web_tools.py:88-90`）。

### 3.3.3 每页三决策机制

对于每个成功抓取的页面，Agent必须做出三选一决策（由提示词`prompts/web_ingestion_instruction.md`指导）：

| 决策 | 动作 | 适用场景 |
|------|------|----------|
| **(a) 充实现有Concept** | 调用 `read_existing_doc` 读取后，调用 `write_concept_doc` 合并新内容 | 页面是某个已有表/指标的权威文档 |
| **(b) 创建独立引用文档** | 调用 `write_concept_doc` 写入 `references/<slug>.md` | 页面是跨Concept的通用参考（如API文档、最佳实践） |
| **(c) 跳过** | 不写入任何文件 | 导航页、营销页、登录页等无关内容 |

Runner启动Web Pass时的用户消息（`runner.py:123-157`）明确指示：不要在单页后停止——种子页通常是索引或Schema引用，应跟随域内链接到高价值页面（示例查询、烹饪手册、指标定义、字段/枚举引用），直到相关材料覆盖完毕或页面预算耗尽。

## 3.4 核心模块架构详解

### 3.4.1 bundle工具模块（tools/bundle_tools.py）

bundle工具模块负责OKF文档的读写和验证，是Agent与文件系统交互的唯一入口。

**文档写入的增强保护机制（Augmentation Guard）**（`bundle_tools.py:143-183`）：

在Web Pass期间写入已存在的`BigQuery Table`类型文档时，工具强制执行两项保护：

1. **Schema字段保护**：新文档的`# Schema`章节必须包含BQ Pass生成的所有字段，禁止缩减。检测通过正则匹配反引号中的字段名（`bundle_tools.py:46-50`）。
2. **Sources列表保护**：新文档的`sources` frontmatter条目数不得少于现有条目数，防止BQ数据源引用被意外删除。

违反任一保护时，`write_concept_doc`返回结构化错误，提示Agent先调用`read_existing_doc`读取当前内容再合并写入。

**Frontmatter自动填充**（`bundle_tools.py:113-124`）：

- `generated.by`：未提供时自动填充为 `reference_agent/<model>`，遵循Actor约定（参见 [02 OKF规范 §2.3.1](./02-okf-specification.md#231-actor约定统一身份标识)）。
- `generated.at`：未提供时自动填充为当前UTC ISO 8601时间戳。
- 字段按`_PREFERRED_KEY_ORDER`排序输出，保持frontmatter键顺序一致。

**文档序列化与验证**（`bundle/document.py`）：

- `OKFDocument.parse()`：解析Markdown文件，分离YAML frontmatter和正文。
- `OKFDocument.validate()`：验证必填字段`type`存在（OKF v0.2唯一强制字段）。
- `OKFDocument.serialize()`：序列化为标准OKF格式（`---\nYAML\n---\n\n正文`）。
- 辅助函数：`normalize_verified()`处理单验证者简写形式，`trust_tier()`推导信任层级，`is_stale()`判断是否过时。

### 3.4.2 source工具模块（tools/source_tools.py）

source工具模块提供数据源抽象层，当前仅实现BigQuery源，但架构支持扩展其他源。

**BigQuery源实现**（`sources/bigquery.py`）通过以下方法提供元数据：

- `list_concepts()`：列出数据集中所有表，返回`ConceptRef`列表（含id、type、resource、hint）。
- `read_concept(ref)`：获取表的完整元数据（Schema含嵌套RECORD字段、分区配置、聚簇配置、行数、创建/修改时间等）。
- `sample_rows(ref, n)`：执行`SELECT * FROM table LIMIT n`获取样例行，结果强制字符串化防止类型问题。

Concept ID采用斜杠分隔的路径格式（如`tables/events_`、`datasets/ga4`），通过`bundle/paths.py`中的函数在ID和文件路径间转换：

- `parse_concept_id(s)`：`"tables/events_"` → `("tables", "events_")`
- `concept_id_to_path(root, cid)`：`("tables", "events_")` → `root/tables/events_.md`
- `path_to_concept_id(root, path)`：反向转换

### 3.4.3 web抓取模块（tools/web_tools.py + web/fetcher.py）

web抓取模块分为两层：工具层（预算控制）和抓取层（HTTP获取与解析）。

**WebState状态管理**（`tools/context.py:16-26`）：

```python
@dataclass
class WebState:
    allowed_hosts: set[str]              # 允许的主机名白名单
    max_pages: int                       # 页面抓取硬上限
    allowed_path_prefixes: tuple[str, ...]  # 允许的路径前缀
    denied_path_substrings: tuple[str, ...] # 拒绝的路径子串
    max_depth: int                       # 最大跳数深度
    visited: set[str]                    # 已访问URL集合（去重）
    fetched_count: int                   # 已抓取计数
    url_depth: dict[str, int]            # URL → 深度映射
```

WebState通过`set_web_state()`/`get_web_state()`/`clear_web_state()`管理生命周期，Runner在Web Pass开始前设置，结束后清除（`runner.py:236-262`）。`is_web_pass()`函数供bundle工具判断当前所处阶段。

**HTTP抓取与解析**（`web/fetcher.py`）：

- 使用标准库`urllib.request`发送HTTP请求，设置自定义User-Agent（`okf-reference-agent/0.1 (+...)`）。
- 仅接受HTML内容类型，非HTML响应抛出`FetchError`。
- 使用`markdownify`库将HTML转换为Markdown，限制最大40KB，超出截断并添加`[...truncated...]`标记。
- 提取页面标题（`<title>`标签）和所有出站链接（`href`属性），相对链接自动转为绝对URL，去除片段标识符（`#`部分）。

### 3.4.4 context管理模块（tools/context.py）

context模块提供**进程内全局上下文**，使工具函数无需显式传递参数即可访问运行时状态。

**ToolContext**（`context.py:9-13`）存储BQ Pass和Web Pass共用的基础上下文：
- `source`：当前数据源实例（BigQuerySource）
- `bundle_root`：Bundle输出根目录路径
- `model`：使用的Gemini模型ID

通过`set_context()`在Runner初始化时设置（`runner.py:179`），工具通过`get_context()`获取。

**WebState**（见§3.4.3）作为独立全局变量管理，仅在Web Pass期间存在。

## 3.5 enrich命令参数完整说明

`enrich`是参考Agent的核心子命令，用于从数据源生成OKF Bundle。以下是所有参数的完整说明（基于`cli.py:63-143`）。

### 3.5.1 必填参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `--source` | 选择项 | 数据源类型，当前仅支持`bq`（BigQuery） |
| `--out` | Path | Bundle输出根目录，不存在时自动创建 |

### 3.5.2 数据源参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--dataset` | string | - | BigQuery数据源专用，格式为`project.dataset`；`--source bq`时必填 |
| `--billing-project` | string | ADC默认项目 | BigQuery查询计费项目ID |

### 3.5.3 增量与模型参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--concept` | string（可重复） | 所有Concept | 仅处理指定Concept ID（如`tables/events_`）；可重复多次指定多个；支持单概念迭代开发 |
| `--model` | string | `gemini-flash-latest` | 使用的Gemini模型ID |

### 3.5.4 Web Pass参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--web-seed` | string（可重复） | - | Web Pass种子URL；可重复多次指定多个 |
| `--web-seed-file` | Path（可重复） | - | 种子URL文件路径，每行一个URL（`#`开头为注释）；可重复 |
| `--no-web` | flag | `false` | 完全跳过Web Pass，仅运行BQ Pass |
| `--web-max-pages` | int | 100 | Web Pass抓取页面数硬上限 |
| `--web-max-depth` | int | 2 | 从种子URL开始的最大跳数深度（种子=0） |
| `--web-allowed-host` | string（可重复） | 仅种子主机名 | 额外允许抓取的主机名；可重复 |
| `--web-allowed-path-prefix` | string（可重复） | 无限制 | 仅抓取路径以此前缀开头的URL（如`/docs/`）；可重复 |
| `--web-denied-path-substring` | string（可重复） | 无 | 拒绝路径包含此子串的URL（如`/login`、`/pricing`）；可重复 |

### 3.5.5 调试参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `-v`, `--verbose` | flag | `false` | 详细日志模式，输出完整的工具调用参数和响应 |

## 3.6 CLI使用示例

### 3.6.1 最小调用（仅BQ Pass）

最简化的调用，仅运行BQ Pass从BigQuery数据集生成Bundle：

```bash
.venv/bin/python -m reference_agent enrich \
    --source bq \
    --dataset bigquery-public-data.ga4_obfuscated_sample_ecommerce \
    --out ./bundles/ga4-sample \
    --no-web
```

此命令将：
1. 连接到指定的BigQuery数据集
2. 列出所有表并逐个生成OKF文档（含Schema、分区信息等）
3. 跳过Web Pass
4. 重建index.md索引文件

### 3.6.2 完整调用（BQ + Web Pass）

带Web种子文件的完整调用：

```bash
# 首先创建种子文件 seeds.txt
cat > seeds.txt << 'EOF'
# GA4 BigQuery Export 官方文档
https://developers.google.com/analytics/bigquery/export-schema
https://support.google.com/analytics/answer/7029846
EOF

# 运行完整两阶段流水线
.venv/bin/python -m reference_agent enrich \
    --source bq \
    --dataset bigquery-public-data.ga4_obfuscated_sample_ecommerce \
    --web-seed-file seeds.txt \
    --web-max-pages 50 \
    --web-allowed-path-prefix /analytics/ \
    --web-denied-path-substring /login \
    --web-denied-path-substring /pricing \
    --out ./bundles/ga4
```

### 3.6.3 单概念迭代开发

调试或增量更新时使用`--concept`参数仅处理单个Concept（参见 §3.7）：

```bash
# 仅重新生成 events_ 表的文档
.venv/bin/python -m reference_agent enrich \
    --source bq \
    --dataset bigquery-public-data.ga4_obfuscated_sample_ecommerce \
    --concept tables/events_ \
    --out ./bundles/ga4 \
    --no-web
```

可重复`--concept`参数指定多个Concept：

```bash
.venv/bin/python -m reference_agent enrich \
    --source bq \
    --dataset my-project.my-dataset \
    --concept tables/users \
    --concept tables/orders \
    --web-seed https://docs.example.com/schema \
    --out ./bundles/my-bundle
```

### 3.6.4 详细日志模式

添加`-v`参数查看完整的工具调用和响应，便于调试Agent行为：

```bash
.venv/bin/python -m reference_agent enrich \
    --source bq \
    --dataset my-project.my-dataset \
    --out ./bundles/my-bundle \
    -v
```

详细模式下输出完整JSON参数和响应，普通模式下输出压缩摘要（字符串截断、字典显示键数、列表显示项数）。

## 3.7 单概念迭代方法

`--concept`参数支持**单概念迭代开发工作流**，这是调试和完善Bundle的核心方法。

### 3.7.1 迭代工作流

1. **首次全量运行**：不带`--concept`运行完整两阶段流水线，生成Bundle初始版本。
2. **发现问题**：浏览生成的文档，发现某个Concept描述不充分、缺少查询示例、来源链接有误等问题。
3. **单Concept迭代**：使用`--concept <id>`重新运行，仅重新生成该Concept。可配合`--no-web`跳过Web Pass快速迭代。
4. **人工审查**：检查生成的文档，如不满意可调整提示词或修改后再次迭代。
5. **全量验证**：单个Concept满意后，可再次全量运行确保一致性。

### 3.7.2 Concept ID格式

Concept ID采用斜杠分隔的路径格式，与Bundle内文件路径对应：

| Concept类型 | ID格式示例 | 对应文件路径 |
|-------------|-----------|-------------|
| 表 | `tables/events_` | `tables/events_.md` |
| 数据集 | `datasets/ga4` | `datasets/ga4.md` |
| 引用文档 | `references/api-docs` | `references/api-docs.md` |

可通过查看`list_concepts`工具的输出或Bundle目录结构获取有效Concept ID。指定不存在的Concept ID时，CLI抛出错误并列出可用Concept（`runner.py:270-273`）。

### 3.7.3 增量更新特性

`write_concept_doc`工具设计为支持增量更新：

- 调用`read_existing_doc`读取现有文档的frontmatter和body
- 在现有内容基础上增强，而非从头生成
- Web Pass阶段自动保留BQ Pass生成的Schema字段和sources列表（增强保护）

这使得多次迭代运行可以累积改进，而不会丢失之前的工作成果。

## 3.8 凭证配置

参考Agent需要两类凭证：BigQuery访问凭证和Gemini API凭证。

### 3.8.1 BigQuery凭证配置

使用Google Cloud Application Default Credentials (ADC)：

```bash
# 1. 安装gcloud CLI（如未安装）
# 参见 https://cloud.google.com/sdk/docs/install

# 2. 登录并设置默认凭证
gcloud auth application-default login

# 3. 设置计费项目（查询公共数据集也需要计费项目）
gcloud config set project <your-billing-project-id>
```

也可通过`--billing-project`参数显式指定计费项目，覆盖gcloud默认设置。

**权限要求**：
- 对于公共数据集（如`bigquery-public-data.*`）：仅需要`bigquery.jobs.create`权限（在计费项目上）。
- 对于私有数据集：还需要`bigquery.tables.get`、`bigquery.tables.getData`、`bigquery.datasets.get`权限。

### 3.8.2 Gemini凭证配置

两种认证方式二选一：

**方式一：AI Studio API Key（推荐快速开始）**

```bash
# 获取API Key：https://aistudio.google.com/apikey
export GEMINI_API_KEY=<your-api-key>
```

**方式二：Vertex AI（生产环境推荐）**

```bash
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT=<your-gcp-project-id>
export GOOGLE_CLOUD_LOCATION=<region>  # 如 us-central1
```

Vertex AI方式需要GCP项目启用Vertex AI API，且凭证拥有`aiplatform.endpoints.predict`权限。

### 3.8.3 Python环境配置

推荐使用Python 3.13虚拟环境：

```bash
# 在 okf/ 目录下
python3.13 -m venv .venv
.venv/bin/pip install --index-url https://pypi.org/simple/ -e .[dev]
```

`-e .[dev]`以可编辑模式安装包并包含开发依赖（pytest等）。

## 3.9 本章小结与延伸阅读

reference_agent展示了如何基于OKF规范构建自动化知识生产Agent，关键设计要点：

1. **两阶段架构**：BQ Pass生成事实基座，Web Pass充实文档内容，职责分离且有增强保护防止事实被覆盖。
2. **工具层安全**：爬取预算、主机白名单、路径过滤、深度限制等约束在工具层强制执行，不依赖LLM自觉。
3. **全局上下文**：通过`ToolContext`和`WebState`管理运行时状态，工具函数无需显式传参。
4. **迭代友好**：`--concept`参数支持单概念增量开发，`read_existing_doc`支持文档增强而非覆写。
5. **来源与信任**：自动填充`generated`字段，遵循Actor约定，为后续人工验证留下审计轨迹。

**延伸阅读**：

- OKF快速入门实操：[okf-wiki 02 5分钟快速入门](../okf-wiki/02-quickstart.md)
- OKF规范深度解析：[02 OKF开放知识格式规范深度解析](./02-okf-specification.md)
- OKF核心概念：[01 核心概念与平台架构](./01-core-concepts.md)
- 可视化工具：[04 工具链与可视化](./04-toolchain-and-visualization.md)（下一章）
- 官方示例Recipes：参见 `okf/samples/` 目录下各数据集的运行配方

| 上一章 | 目录 | 下一章 |
|--------|------|--------|
| [02 OKF开放知识格式规范深度解析](./02-okf-specification.md) | [README](./README.md) | [04 工具链与可视化](./04-toolchain-and-visualization.md) |
