---
name: "knowledge-graph-generator"
description: "从结构化Markdown文档集生成交互式vis-network知识图谱。Invoke when user asks to create knowledge graph, visualize concept relationships, or build interactive network graph from Markdown files."
---

# 知识图谱生成器 Skill

从结构化Markdown文档中自动提取节点和关系，生成交互式vis-network HTML知识图谱。基于四层混合策略（参考 markdown-to-knowledge-graph 架构模式）。

## 何时使用

当用户需要：
- 为知识库/学习笔记创建交互式知识图谱
- 可视化概念、人物、事件、文档之间的关系网络
- 从Markdown表格自动提取节点和边
- 生成可点击、可搜索、可筛选的关系网络可视化

## 核心文件

| 文件 | 用途 |
|------|------|
| [.agents/scripts/generate-graph.py](file:///d:/.agents/scripts/generate-graph.py) | 命令行入口 |
| [.agents/scripts/lib/knowledge_graph_core.py](file:///d:/.agents/scripts/lib/knowledge_graph_core.py) | 核心库（KnowledgeGraphBuilder） |
| [.agents/scripts/templates/knowledge-graph-generic.html](file:///d:/.agents/scripts/templates/knowledge-graph-generic.html) | 通用HTML模板 |
| [docs/knowledge/learning/first-principles/knowledge-graph-config.toml](file:///d:/AI/docs/knowledge/learning/first-principles/knowledge-graph-config.toml) | 第一性原理配置示例 |

## 快速开始

### 方式一：Python API（推荐，灵活度最高）

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
            "person": {"label": "人物", "color": "#E53935", "size": 22},
        },
        "edge_types": {
            "related_to": {"label": "相关", "color": "#999", "width": 1},
            "influenced": {"label": "影响", "color": "#1565C0", "width": 2, "arrows": "to"},
        },
    },
    "parsers": [
        {
            "type": "table",
            "file": "glossary.md",
            "section": "## 术语表",
            "node_type": "concept",
            "id_prefix": "concept_",
            "id_from": "name",
            "columns": {"name": 0, "definition": 1, "related": 2},
            "link_column": "related",
            "link_relation": "related_to",
        },
    ],
    "manual_nodes": [
        {"id": "root", "label": "核心主题", "type": "concept"},
    ],
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

### 方式二：TOML配置文件

创建 `knowledge-graph-config.toml`：

```toml
input_dir = "."
output = "knowledge-graph.html"

[graph]
title = "我的知识图谱"

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
min_columns = 3

[[manual_nodes]]
id = "root"
label = "核心主题"
type = "concept"

[[auto_relations]]
type = "preceded"
source_type = "event"
time_field = "time"
relation = "preceded"
```

运行：
```bash
python .agents/scripts/generate-graph.py --config docs/my-knowledge-base/knowledge-graph-config.toml
```

## 解析器配置说明

### 表格解析器（type = "table"）

| 配置项 | 说明 | 必填 |
|--------|------|------|
| file | Markdown文件名（相对于input_dir） | ✅ |
| section | 表格所在章节标题（如 `## 术语表`） | ✅ |
| node_type | 节点类型标识 | ✅ |
| id_prefix | 节点ID前缀（如 `concept_`） | ✅ |
| id_from | 用哪一列作为节点名称/ID生成依据 | ✅ |
| columns | 列映射 `{字段名: 列索引}` | ✅ |
| min_columns | 最小列数（少于则跳过该行） | ❌ 默认2 |
| link_column | 包含Markdown链接的列（自动提取关系） | ❌ |
| link_relation | 链接对应的关系类型 | ❌ 默认related_to |
| split_names_by | 名称分隔符正则（一列多人时分割） | ❌ |
| filename_from_link | 从链接单元格提取文件名（文档节点） | ❌ |
| label_from | 节点显示标签使用哪一列（而非id_from） | ❌ |
| domain_mapping | 领域关键词到分类的映射 | ❌ |

### 自动关系类型

| type | 功能 | 必要配置 |
|------|------|----------|
| `belongs_to` | 建立Event/Person→Period的归属关系 | source_types, target_type, period_field |
| `preceded` | 按时间排序建立事件间时序关系 | source_type, time_field |
| `defined_in` | 建立Concept→Document的定义位置关系 | concept_type, doc_type |

## 节点属性说明

生成的节点可以包含任意自定义字段，这些字段会在详情面板中自动显示。常用字段：

- `label`: 节点显示名称
- `type`: 节点类型（对应node_types配置）
- `definition`: 定义/描述文本
- `source_url`: 源文档链接（file:///格式）
- `domain`: 领域分类
- `rating`: 可信度等级（'A'/'B'等，影响节点大小和详情显示）
- `time`/`period`: 时间/时期字段
- `contribution`: 人物贡献
- `introduction`: 文档简介

## 样式配置

在 `graph.node_types.<type>` 中配置：
- `color`: 节点颜色（十六进制）
- `size`: 节点基础大小
- `shape`: 节点形状（'dot'/'diamond'等）
- `domain_colors`: 概念节点按领域分色的颜色映射
- `rating_bonus`: true时A级节点大2px

在 `graph.edge_types.<relation>` 中配置：
- `color`: 边颜色
- `width`: 边宽度
- `dashes`: 虚线样式（false/true/[6,4]等）
- `arrows`: 箭头方向（'to'/''/middle等）

## 示例项目

参考第一性原理知识图谱的完整配置和实现：
- 配置：[knowledge-graph-config.toml](file:///d:/AI/docs/knowledge/learning/first-principles/knowledge-graph-config.toml)
- 生成结果：[12-knowledge-graph.html](file:///d:/AI/docs/knowledge/learning/first-principles/12-knowledge-graph.html)

## 注意事项

1. **CSS Grid零尺寸陷阱**：嵌入其他页面时确保可视化容器设置了`min-height:0`（Grid/Flex布局）
2. **vis-network需要联网**：HTML通过CDN加载vis-network库，离线环境需本地化
3. **中文TOML键名**：包含中文的键必须用引号包围
4. **表格格式要求**：必须是标准Markdown管道表格，且位于指定章节标题下方

## 功能特性

- ✅ 自动从Markdown表格提取节点
- ✅ 自动解析Markdown链接建立节点关系
- ✅ 支持多类型节点（概念/人物/事件/文档/时期等任意自定义类型）
- ✅ 支持自动关系构建（时期归属/时序先后/定义位置等）
- ✅ 手工节点和边配置（补充无法自动提取的关系）
- ✅ 节点去重、孤立节点检测
- ✅ 交互式可视化：搜索、类型筛选、领域筛选、点击查看详情
- ✅ 自包含HTML输出（单文件，可直接分享）
- ✅ 可配置颜色、大小、形状、边样式
- ✅ 力导向布局自动稳定
- ✅ 降级显示（vis-network加载失败时显示文本列表）