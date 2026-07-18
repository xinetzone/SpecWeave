---
name: knowledge-graph-generator
version: 1.1.0
description: "当用户提到'知识图谱'、'knowledge graph'、'概念关系可视化'、'交互式知识图谱'、'节点关系网络'、'生成知识图谱'、'可视化知识库'、'概念网络'、'knowledge graph config'时，必须使用此技能。从结构化Markdown文档集（术语表/文档索引/时间线等）自动提取节点和关系，生成交互式vis-network HTML知识图谱。支持TOML声明式配置和Python API两种方式，内置节点去重、孤立节点检测、类型筛选、可信度分级显示。不要手动拼接vis-network代码——本Skill封装了表格解析、关系构建、HTML模板渲染和自包含输出，确保产出质量可预测。"
argument-hint: "[--config <config.toml>] [--output <path>]"
user-invocable: true
paths:
  - ".agents/scripts/generate-graph.py"
  - ".agents/scripts/lib/knowledge_graph_core.py"
  - ".agents/scripts/templates/knowledge-graph-generic.html"
title: "知识图谱生成器 Skill"
x-toml-ref: "../../../.meta/toml/.agents/skills/knowledge-graph-generator/SKILL.toml"
---
# 知识图谱生成器 Skill

> ⚠️ **本Skill是脚本命令门面（L1索引层）**，遵循[渐进式披露三层架构](../../capabilities/ARCHITECTURE.md)：
> - L0：[.agents/ONBOARDING.md](../../ONBOARDING.md)（入口速查）
> - L1：本文件（≤500行，触发词+决策树+核心命令+安全清单）
> - L2：脚本源码 [generate-graph.py](../../scripts/generate-graph.py) + [knowledge_graph_core.py](../../scripts/lib/knowledge_graph_core.py)（完整实现）

## 1. Skill ID
`knowledge-graph-generator`

## 2. 功能描述

从结构化Markdown文档集中自动提取节点和关系，生成交互式vis-network HTML知识图谱。提供两种方案：

| 方案 | 推荐场景 | 优势 |
|------|---------|------|
| **TOML配置文件（推荐）** | ⭐ 知识库交付、可复现的知识图谱 | 声明式配置、一次编写可重复运行、可版本控制 |
| **Python API** | ⭐ 高度定制、动态构建 | 灵活度最高、支持任意节点属性、可在运行时动态调整 |

核心功能：Markdown表格解析提取节点 → 自动/手工关系构建 → 节点去重与孤立节点检测 → 交互式HTML输出（搜索/筛选/详情面板）。

> **为什么需要本Skill而非手写vis-network？** 手写vis-network需要手动构造 `nodes` 和 `edges` 两个JavaScript数组，当知识库有100+术语时手动维护不可行——每次新增术语都要同时更新JSON数据，极易出错和遗漏。本Skill从Markdown表格直接提取节点（单一数据源），自动建立关系，产出可复现、可审计的知识图谱。这也体现了对抗性审查方法论中的"单一数据源"原则——知识库Markdown文件是权威数据源，知识图谱是派生产物，不应反向维护。

## 3. 何时使用本技能

当用户提到以下任何内容时触发：
- "知识图谱"、"knowledge graph"、"概念关系图"、"交互式知识图谱"
- "节点关系网络"、"概念网络"、"知识网络"
- "生成知识图谱"、"创建知识图谱"、"构建知识图谱"
- "可视化知识库"、"知识库可视化"
- 为 `docs/knowledge/learning/` 下的知识库创建配套知识图谱
- 提到 `generate-graph.py` 或 `knowledge-graph-config.toml`

> **关于触发**：即使没有明确说"用知识图谱生成器"，只要涉及从Markdown文档生成交互式概念关系可视化，就应该使用本Skill。本Skill封装了表格解析、关系构建、HTML模板渲染的完整流程，手动拼接vis-network代码不仅效率低，而且容易产生孤立节点、重复节点、样式不一致等问题。

## 4. 方案选择决策树

```
需要生成知识图谱？
├─ 知识库已有稳定的术语表/文档索引/时间线表格？ → TOML配置方案（第5.1节，推荐）
├─ 需要高度定制（动态节点、条件过滤）？ → Python API方案（第5.2节）
├─ 首次使用不确定如何配置？ → 参考示例项目（第9节，先看第一性原理配置）
└─ 为对抗性审查知识库生成图谱？ → 参考 [adversarial-review-wiki](../../docs/knowledge/learning/02-agent-engineering-methodology/adversarial-review-wiki/README.md) 的术语表结构设计配置
```

**写操作（生成HTML）原则**：生成HTML是纯输出操作，不修改源文件，无需dry-run。但需注意输出路径不要覆盖已有文件。

> **为什么推荐TOML配置而非Python API？** TOML声明式配置遵循"配置即文档"原则——其他人阅读 `.toml` 文件即可理解知识图谱的数据来源、节点类型、关系类型，无需阅读Python代码。同时TOML配置可纳入版本控制，修改记录可追溯（git diff友好），符合对抗性审查的可审计性要求。

## 5. 核心命令（快速开始）

脚本路径：[generate-graph.py](../../scripts/generate-graph.py)

### 5.1 TOML配置方案（推荐）

```bash
cd d:\AI

# 基于配置文件生成知识图谱
python .agents/scripts/generate-graph.py --config docs/knowledge/learning/<知识库目录>/knowledge-graph-config.toml

# 指定输出路径（覆盖配置中的output设置）
python .agents/scripts/generate-graph.py --config <config.toml> --output <自定义路径>.html
```

配置文件结构（完整示例见 [第一性原理配置](../../docs/knowledge/learning/first-principles/knowledge-graph-config.toml)）：

```toml
input_dir = "."
output = "knowledge-graph.html"

[graph]
title = "知识图谱标题"
subtitle = "副标题 · __NODE_COUNT__个节点 · __EDGE_COUNT__条关系"

[graph.node_types.concept]
label = "概念"
color = "#43A047"
size = 18

[graph.edge_types.related_to]
label = "相关"
color = "#999"
width = 1

[[parsers]]
type = "table"
file = "glossary.md"
section = "## 术语表"
node_type = "concept"
id_prefix = "concept_"
id_from = "name"
columns = {name = 0, definition = 1}

[[manual_nodes]]
id = "root"
label = "核心主题"
type = "concept"
```

### 5.2 Python API方案（高度定制）

```python
from pathlib import Path
import sys
sys.path.insert(0, ".agents/scripts")
from lib.knowledge_graph_core import KnowledgeGraphBuilder

config = {
    "graph": {
        "title": "我的知识图谱",
        "node_types": {
            "concept": {"label": "概念", "color": "#43A047", "size": 18},
            "document": {"label": "文档", "color": "#00897B", "size": 22},
        },
        "edge_types": {
            "related_to": {"label": "相关", "color": "#999", "width": 1},
            "defined_in": {"label": "定义于", "color": "#4CAF50", "width": 1, "dashes": [2, 3]},
        },
    },
    "parsers": [
        {"type": "table", "file": "glossary.md", "section": "## 术语表",
         "node_type": "concept", "id_prefix": "concept_", "id_from": "name",
         "columns": {"name": 0, "definition": 1}},
    ],
    "manual_nodes": [],
    "manual_edges": [],
    "auto_relations": [],
}

builder = KnowledgeGraphBuilder(config, Path("docs/my-knowledge-base"))
for p in config["parsers"]:
    nodes, edges = builder.parse_table_nodes(p)
    builder.nodes.extend(nodes)
    builder.edges.extend(edges)

builder.add_manual_data()
builder.build_auto_relations()
builder.deduplicate()
isolated = builder.check_isolated()
builder.print_stats(isolated)
builder.generate_html(Path("docs/my-knowledge-base/knowledge-graph.html"))
```

> 完整参数表和高级用法（解析器配置、自动关系类型、节点属性、样式配置）见脚本源码 `--help` 和 [knowledge_graph_core.py](../../scripts/lib/knowledge_graph_core.py)。

## 6. 解析器关键配置速查

| 配置项 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `file` | str | 源Markdown文件（相对input_dir） | `"glossary.md"` |
| `section` | str | 表格所在章节标题（精确匹配） | `"### 2.1 核心概念类"` |
| `node_type` | str | 节点类型（对应graph.node_types） | `"concept"` |
| `id_prefix` | str | 节点ID前缀，避免不同类型冲突 | `"concept_"` |
| `id_from` | str | 用哪一列生成节点ID | `"name"` |
| `columns` | dict | 列名→列索引映射 | `{name = 0, definition = 1}` |
| `link_column` | str | 含Markdown链接的列名（自动提取关系） | `"related"` |
| `filename_from_link` | bool | 从链接提取文件名（文档节点用） | `true` |
| `label_from` | str | 显示标签用哪一列（不同于id_from） | `"title"` |
| `domain_mapping` | dict | 领域关键词→颜色分类 | `{"哲学" = "哲学"}` |

### 自动关系类型

| type | 功能 | 适用场景 |
|------|------|---------|
| `belongs_to` | 节点→时期的归属关系 | 人物/事件按时间归类 |
| `preceded` | 按时间排序的事件时序 | 时间线节点前后关系 |
| `defined_in` | 概念→文档的定义位置 | 术语表概念与文档的映射 |

## 7. 安全检查清单（生成前逐项确认）

- [ ] 源Markdown文件存在且表格格式正确（标准管道表格 `| col | col |`）
- [ ] 章节标题（`section`）与源文件中的标题精确匹配（含 `###` 层级和emoji）
- [ ] 列索引（`columns`）与表格实际列顺序一致（从0开始计数）
- [ ] 节点类型已定义对应的 `node_types` 颜色/大小/形状
- [ ] 边类型已定义对应的 `edge_types` 颜色/宽度/箭头
- [ ] 输出路径不覆盖已有同名文件（如已存在，先确认是否需要覆盖）
- [ ] HTML输出文件能在浏览器中正常打开（CDN可访问vis-network库）
- [ ] 生成后检查孤立节点数量（isolated > 10% 时需排查配置）
- [ ] 知识库文档更新后重新生成知识图谱（保持数据同步）

> **为什么章节标题必须精确匹配？** 解析器直接按字符串匹配 `section` 参数值定位表格——多一个空格、少一个emoji、层级不对（`##` vs `###`）都会导致解析失败且不报错（静默返回0个节点）。这是最高频的配置错误，建议从源文件直接复制标题，而非手动输入。

## 8. 常见错误处理

| 错误场景 | 原因 | 处理方式 |
|---------|------|---------|
| 生成0个节点无报错 | section标题不匹配或表格格式错误 | 检查源文件中的实际标题，从文件复制精确匹配 |
| 节点ID冲突 | 不同类型节点使用了相同id_prefix | 为每种类型设置不同的前缀（如 `concept_`、`bias_`） |
| TOML解析报错 | 中文键名未加引号 | 包含中文的键名必须用引号包围 `"概念"` |
| `tomllib.TOMLDecodeError: Invalid initial character for a key part` | Python 3.11+ 内置 `tomllib` 对中文键名的内联表（inline table）解析存在兼容性缺陷 | 已内置 `tomli` fallback（优先使用 `tomli`，不可用时回退 `tomllib`）；如仍报错，手动安装 `pip install tomli` |
| HTML打开空白 | vis-network CDN加载失败（离线环境） | 确认网络连接，或将CDN资源本地化 |
| 节点显示中文乱码 | 脚本输出编码问题 | 设置环境变量 `PYTHONIOENCODING=utf-8` |
| 表格列数不足导致跳过行 | `min_columns` 设置过高 | 调整 `min_columns` 为实际有效列数 |

## 9. Gotchas（陷阱与反直觉行为）

> **为什么需要Gotchas？** 错误处理记录"已知错误码及修复方式"，Gotchas记录"容易踩的坑、反直觉行为、容易被忽略的约束条件"——不会产生明确错误码但会导致结果不符合预期的隐性陷阱。

- **section匹配是精确字符串匹配**：不是模糊搜索、不是正则、不是子串匹配。`section = "## 术语表"` 只会匹配源文件中恰好是 `## 术语表` 的行，`## 2. 术语表` 或 `## 📄 术语表` 都不会匹配。建议从源文件直接复制标题。
- **TOML数组表语法必须放在最后**：`[[parsers]]` 是TOML数组表语法，在TOML文件中必须放在所有 `[graph]` 和 `[manual_nodes]` 等键值表之后，否则TOML解析器报错。这是TOML规范要求，不是本脚本的限制。
- **节点ID自动生成规则**：`id_from` 指定的列值会被转换为ASCII兼容的ID（中文转拼音、特殊字符移除），如果两个术语转换后ID相同会触发去重，后出现的被跳过。建议在术语表中避免同名术语。
- **vis-network的CDN依赖**：生成的HTML通过CDN加载vis-network库（`unpkg.com`），离线环境会显示降级文本列表而非交互式图谱。如需离线使用，需将vis-network库本地化嵌入HTML。
- **知识图谱是派生产物而非数据源**：知识图谱从Markdown文档生成，更新知识库后必须重新生成图谱。不要在HTML中手动修改节点/边——修改会被下次生成覆盖。这遵循"单一数据源"原则，与对抗性审查的"可审计性"要求一致。
- **`tomllib` 对中文内联表（inline table）存在已知兼容性缺陷**：Python 3.11+ 内置的 `tomllib` 模块在解析包含中文键名的内联表（如 `{概念 = "文档.md"}`）时会抛出 `TOMLDecodeError: Invalid initial character for a key part`。`knowledge_graph_core.py` 已内置 `tomli` fallback（`try: import tomli as tomllib except ImportError: import tomllib`），优先使用第三方 `tomli` 库。如果环境中未安装 `tomli` 且遇到此错误，执行 `pip install tomli` 即可解决。配置文件中应优先使用 `extra_links` 数组格式替代 `concept_doc_map` 内联表格式，从根源规避此问题。

## 10. 关键参考

| 参考 | 层级 | 路径 | 何时查阅 |
|------|------|------|---------|
| 脚本源码（完整参数） | L2 | [generate-graph.py](../../scripts/generate-graph.py) | 需要高级参数时 |
| 核心库（KnowledgeGraphBuilder） | L2 | [knowledge_graph_core.py](../../scripts/lib/knowledge_graph_core.py) | 理解解析逻辑、自定义扩展 |
| HTML模板 | L2 | [knowledge-graph-generic.html](../../scripts/templates/knowledge-graph-generic.html) | 自定义可视化样式 |
| 第一性原理配置示例 | L2 | [knowledge-graph-config.toml](../../docs/knowledge/learning/first-principles/knowledge-graph-config.toml) | 参考完整TOML配置写法 |
| 第一性原理知识图谱 | L2 | [12-knowledge-graph.html](../../docs/knowledge/learning/first-principles/12-knowledge-graph.html) | 查看生成效果 |
| 对抗性审查指令集 | L1 | [adversarial-review.md](../../commands/adversarial-review.md) | 知识库构建的质量标准（自举验证、可信度评级） |
| 对抗性审查知识库 | L2 | [adversarial-review-wiki/](../../docs/knowledge/learning/02-agent-engineering-methodology/adversarial-review-wiki/README.md) | 术语表结构参考（11-glossary.md含6类术语表） |

## 11. 与对抗性审查的协同

本Skill生成的知识图谱与对抗性审查方法论存在两层协同关系：

1. **知识图谱作为审查工具**：知识图谱可视化概念之间的关系，帮助审查者快速识别"孤立概念"（缺少交叉引用）、"过度连接的概念"（可能过度泛化）、"缺失关系"（应有关联但未建立），这是对抗性审查阶段0跨领域扫描的有效辅助手段。

2. **知识图谱构建过程的审查**：按照对抗性审查指令集的自举验证原则，知识图谱的配置文件和生成结果本身也应接受审查——节点是否完整覆盖了知识库内容？关系是否准确反映了文档中的实际关联？孤立节点是否意味着知识库中存在未被充分引用的概念？

> **为什么知识图谱需要对抗性审查？** 知识图谱本质上是对知识库的"压缩表示"——节点提取和关系建立过程中不可避免地会丢失细节、引入偏差。确认偏差可能导致只提取了"熟悉的"概念而遗漏"陌生的"概念；权威偏差可能导致过度重视权威来源的概念而忽略同级别但来源不同的概念。对知识图谱配置执行快速审查（检查节点覆盖率、关系准确性、孤立节点原因）是低成本高收益的质量保障措施。

## 12. Changelog

- **v1.1.0** (2026-07-10): 从.trae/skills/迁移至.agents/skills/，按五要素模型重写为脚本命令门面格式（frontmatter/决策树/Why解释/安全检查清单/Gotchas/关键参考）；新增§11"与对抗性审查的协同"章节，建立与adversarial-review.md指令集的双向关联；新增对抗性审查知识库（adversarial-review-wiki/）作为术语表结构参考。
- **v1.0.0** (2026-07-10): 初始版本，基于generate-graph.py和knowledge_graph_core.py封装，提供TOML配置和Python API两种方案，支持多类型节点、自动关系构建、交互式HTML输出。