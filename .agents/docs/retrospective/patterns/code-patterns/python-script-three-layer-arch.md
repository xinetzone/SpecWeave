---
id: "python-script-three-layer-arch"
source: "../../reports/task-reports/retrospective-first-principles-knowledge-graph-20260709/insight-extraction.md"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/code-patterns/python-script-three-layer-arch.toml"
---
# Python脚本三层架构：主脚本+数据模块+模板分离

## 模式概述

当Python生成/转换脚本超过项目规定的行数限制（通常500行）时，采用三层架构拆分，将代码按职责分离到三个独立文件中，保持主脚本精简可维护。

## 问题现象

Python脚本在迭代过程中容易膨胀：
1. **HTML/CSS/JS模板代码嵌入Python字符串**：三引号包裹的大段HTML/CSS/JS使Python文件迅速膨胀到500+行
2. **静态数据字典/列表堆在主脚本**：手工编码的配置数据、映射表、常量定义占用大量行
3. **主脚本职责混乱**：流程编排、数据定义、模板渲染、CLI解析全在一个文件中
4. **违反行数限制**：项目规范要求单个Python脚本≤500行，超限文件无法通过质量门禁
5. **难以测试**：模板字符串和静态数据与逻辑混合，单元测试需要mock大量内容

## 解决方案

将脚本拆分为三层，每层单一职责：

```
project/
├── generate-xxx.py          # 主脚本：核心逻辑+CLI入口+流程编排（≤500行）
├── xxx_data.py              # 数据模块：静态数据+配置常量+手工编码数据
└── templates/
    └── xxx-template.html    # 模板文件：HTML/CSS/JS/文本模板
```

### 层1：主脚本（generate-xxx.py）
职责：
- CLI参数解析（使用项目共享lib.cli）
- 核心算法和业务逻辑
- 流程编排（调用各层函数）
- 输入/输出协调

不应包含：
- 大段HTML/CSS/JS模板字符串（→提取到templates/）
- 大段静态数据字典/列表（→提取到_data.py）
- 内联CSS样式或JavaScript代码

示例结构：
```python
#!/usr/bin/env python3
"""XXX生成脚本：从XXX自动提取YYY并生成ZZZ。"""
import sys, json
from pathlib import Path
# 项目共享库
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from cli import add_common_args, print_pass, print_warn, print_summary
from project import resolve_project_root
# 数据模块
from xxx_data import STATIC_CONFIG, MANUAL_RELATIONS
# 模板函数
def render_template(nodes, edges):
    template = (TEMPLATES_DIR / "xxx-template.html").read_text(encoding="utf-8")
    return template.replace("__DATA__", json.dumps(nodes))
def main():
    args = parse_args()
    data = extract_data(args.input)
    data.update(MANUAL_RELATIONS)
    output = render_template(data)
    write_output(output, args.output)
    print_summary(pass_count=..., warn_count=...)
```

### 层2：数据模块（xxx_data.py）
职责：
- 静态配置常量
- 手工编码的补充数据（映射表、关系定义、枚举值）
- 默认参数值

示例：
```python
"""XXX生成脚本的数据模块：手工编码的补充数据和配置常量。"""

# 节点类型颜色配置
NODE_COLORS = {
    "concept": "#43A047",
    "person": "#E53935",
    "event": "#8E24AA",
}
# 手工编码的语义关系（无法自动提取）
MANUAL_RELATIONS = [
    {"source": "aristotle", "target": "first-principles", "type": "contributed"},
]
# 时期分类规则
PERIOD_RULES = {...}
```

### 层3：模板文件（templates/xxx-template.html等）
职责：
- HTML/CSS/JS/Markdown等输出格式的模板
- 通过占位符（如`__DATA__`、`__NODES__`）接收注入数据
- 独立于Python逻辑，可单独预览和调试

示例（HTML模板）：
```html
<!DOCTYPE html>
<html>
<head><style>/* 独立维护的CSS */</style></head>
<body>
<div id="app"></div>
<script src="https://cdn.example.com/lib.js"></script>
<script>
const data = __DATA__;  // 占位符，Python替换为JSON
// 独立维护的JS逻辑
</script>
</body>
</html>
```

## 拆分决策原则

| 内容类型 | 拆分到 | 判断依据 |
|---------|--------|---------|
| 函数定义、流程控制 | 主脚本 | 核心逻辑，频繁修改 |
| CLI参数解析 | 主脚本 | 入口逻辑 |
| ≥20行的字符串常量（HTML/JS/CSS/Markdown） | templates/ | 视图/格式层，独立维护 |
| ≥10个键值的字典/列表常量 | _data.py | 数据层，偶尔更新 |
| 可独立测试的纯函数 | 主脚本或按需提取 | 逻辑核心 |
| import语句、工具函数 | 主脚本 | 基础设施 |

## 拆分触发条件
- 主脚本行数接近或超过500行（预警线450行）
- 单个字符串常量（三引号块）超过30行
- 静态数据定义（字典/列表）合计超过50行
- 发现HTML/CSS/JS代码与Python逻辑混在一起难以阅读

## 验证数据（ACT-011实例）
拆分前：主脚本~530行（含HTML模板~200行+静态数据~80行），违反500行限制
拆分后：
- generate-knowledge-graph.py：422行（≤500，合规）
- knowledge_graph_data.py：129行
- templates/knowledge-graph-template.html：373行
单元测试在拆分后29/29通过，0.35秒完成验证。

## 正反例

### 正例
```
generate-knowledge-graph.py    422行  ← 核心逻辑+CLI
knowledge_graph_data.py        129行  ← 手工关系数据
templates/
  knowledge-graph-template.html 373行 ← HTML/CSS/JS视图
```

### 反例
```
generate-knowledge-graph.py    530行  ← 超限！含200行HTML+80行数据
```

## 与其他模式的关系
- **Markdown→知识图谱自动化生成（markdown-to-knowledge-graph）**：本模式是该模式推荐的代码组织方式
- **脚本生成器模式（script-generator-pattern）**：本模式是Python代码组织层面的模式，脚本生成器是Shell脚本动态生成层面的模式
- **临时sys.path修改（temporary-syspath-modification）**：主脚本中引用数据模块和共享库时需要配合使用
