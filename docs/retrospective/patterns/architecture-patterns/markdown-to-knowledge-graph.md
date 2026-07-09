---
id: "markdown-to-knowledge-graph"
source: "docs/retrospective/reports/task-reports/retrospective-first-principles-knowledge-graph-20260709/insight-extraction.md"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/patterns/architecture-patterns/markdown-to-knowledge-graph.toml"
---
# Markdown→知识图谱自动化生成模式

## 模式概述

对于遵循统一模板的结构化Markdown知识档案（表格结构+章节组织），通过"自动解析+手工补充"的四层混合策略快速生成交互式知识图谱：

1. **自动解析层**：用正则提取Markdown表格中的结构化数据（节点基础属性+显式声明关系）
2. **手工补充层**：在独立数据模块中编码语义关系（传承链、归属关系、贡献关系等无法从表格结构自动推导的关系）
3. **模板渲染层**：数据与视图分离，Python生成JSON注入HTML模板
4. **可视化层**：使用vis-network等成熟力导向图库渲染

## 问题现象

从零构建知识图谱时常见问题：

1. **全自动提取准确率低**：自由文本和跨文档语义关系难以用正则/NLP准确提取，过度追求自动化导致大量错误关系
2. **全手工编码效率低**：所有节点和关系都手工定义，73个节点/176条边的小图谱也需要数天
3. **数据与视图耦合**：HTML/CSS/JS硬编码在Python字符串中，维护困难，修改样式需要改Python代码
4. **不可复用**：每次新知识库都从零开始，没有沉淀可复用的生成框架
5. **脚本超限**：所有逻辑堆在一个Python文件中，容易超过500行限制

## 解决方案（核心架构）

四层架构：

- **数据模型层**：提前定义Node类型（5种：Concept/Person/Event/Document/Period）和Edge类型（6种：related_to/influenced/preceded/belongs_to/defined_in/contributed）的schema
- **自动解析器**：正则提取Markdown表格（术语表→Concept+related_to、时间线→Event/Person+belongs_to、导航表→Document+defined_in）
- **手工数据模块**：独立Python文件（knowledge_graph_data.py）编码语义关系（influenced传承链、contributed人物贡献）
- **HTML模板**：独立templates/目录下的HTML文件，通过`__NODES_DATA__`和`__EDGES_DATA__`占位符注入JSON

```python
# 主脚本流程
def main():
    args = parse_args()
    nodes, edges = [], []
    
    # 1. 自动解析层（覆盖~60%数据）
    nodes += parse_concepts_table(args.input_dir / "06-concepts-glossary.md")
    nodes += parse_events_table(args.input_dir / "07-timeline.md")
    nodes += parse_persons_table(args.input_dir / "07-timeline.md")
    nodes += parse_documents_table(args.input_dir / "README.md")
    edges += extract_concept_relations(nodes)  # related_to
    edges += build_belongs_to_relations(nodes)  # belongs_to
    edges += build_preceded_relations(nodes)   # preceded
    
    # 2. 手工补充层（覆盖~40%语义关系）
    from knowledge_graph_data import INFLUENCED_RELATIONS, CONTRIBUTED_RELATIONS, DEFINED_IN_RELATIONS
    edges += build_influenced_edges(nodes, INFLUENCED_RELATIONS)
    edges += build_contributed_edges(nodes, CONTRIBUTED_RELATIONS)
    edges += build_defined_in_edges(nodes, DEFINED_IN_RELATIONS)
    
    # 3. 去重+组装
    nodes = deduplicate_nodes(nodes)
    edges = deduplicate_edges(edges)
    
    # 4. 模板渲染层
    generate_html(nodes, edges, args.output)
```

HTML模板占位符模式：

```python
def generate_html(nodes, edges, output_path):
    template = (SCRIPTS_DIR / "templates" / "knowledge-graph-template.html").read_text(encoding="utf-8")
    html = template.replace("__NODES_DATA__", json.dumps(nodes, ensure_ascii=False))
    html = html.replace("__EDGES_DATA__", json.dumps(edges, ensure_ascii=False))
    output_path.write_text(html, encoding="utf-8")
```

## 验证数据

- **ACT-011验证**：73节点/176边，2小时内完成从spec到交付
- **自动解析覆盖率**：60+32+18=110/176=62.5%
- **手工补充率**：19+14+33=66/176=37.5%
- **脚本行数**：主脚本422行+数据模块129行+模板373行，均在各自限制内
- **单元测试**：29个，0.35秒全量通过

## 模式优势

| 优势 | 说明 |
|------|------|
| **高效交付** | 60%数据自动提取，仅需手工补充40%语义关系，2小时完成小图谱 |
| **准确率可控** | 关键语义关系手工编码保证准确性，结构化数据自动提取保证效率 |
| **数据视图分离** | HTML模板独立维护，修改样式/交互无需改Python逻辑 |
| **可复用** | 四层架构可推广到其他结构化Markdown知识库 |
| **幂等生成** | 相同输入产生相同输出，支持CI自动化 |
| **测试友好** | 解析逻辑纯函数化，便于单元测试 |

## 适用场景

- 已有结构化Markdown文档（术语表+时间线+导航表）的知识库可视化
- 概念关系网络展示（知识图谱、依赖关系图、影响力网络）
- 需要从文档自动生成可视化导航的项目
- 节点规模在50-200之间的中小型图谱

## 不适用场景

- 非结构化/自由文本文档（需要NLP提取，超出正则能力）
- 超大规模图谱（>500节点，力导向布局性能下降）
- 需要实时编辑/协作的图数据库场景
- 关系类型高度动态变化的场景（手工编码关系维护成本高）

## 核心要素

1. **数据模型先行**：提前定义节点类型、边类型、字段schema，避免实现中反复调整
2. **自动+手工混合**：接受60/40或70/30的自动/手工比例，不追求100%自动化
3. **数据与模板分离**：JSON数据注入HTML模板，Python不拼接HTML字符串
4. **幂等生成**：纯函数式解析+去重，相同输入产生相同输出
5. **容错解析**：表格格式异常时输出警告而非崩溃

## 与其他模式的关系

- **正则驱动的Markdown解析（regex-markdown-parsing）**：本模式的自动解析层依赖此模式
- **Python脚本三层架构（python-script-three-layer-arch）**：本模式推荐的代码组织方式
- **脚本生成器模式（script-generator-pattern）**：同属"生成器"类架构模式，本模式专注于知识图谱领域
- **三层解析生成器（three-layer-parser-generator）**：本模式是解析→生成范式在可视化领域的应用

## 正反例

### 正例

```python
# ✅ 四层架构：数据模型→自动解析→手工补充→模板渲染
nodes, edges = [], []
nodes += parse_concepts_table(glossary_path)  # 自动
edges += load_manual_relations(data_module)    # 手工
generate_html(nodes, edges, template_path)     # 模板分离
```

### 反例

```python
# ❌ 全Python字符串拼接HTML，数据视图耦合
html = "<html><head><style>..."  # 数百行HTML/CSS/JS硬编码
html += f"var nodes = {json.dumps(nodes)};"
html += "var edges = ...; var network = new vis.Network(...);"
# 主脚本>600行，修改样式需改Python代码，无法独立测试
```
