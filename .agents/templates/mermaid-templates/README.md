# Mermaid 安全编码模板

本目录提供遵循项目 Mermaid 安全编码规范的常用图表模板，内置安全格式，从生产端杜绝渲染问题。

## 模板列表

| 模板文件 | 适用场景 |
|---------|---------|
| [flowchart-left-right.md](flowchart-left-right.md) | 流程图（左→右布局） |
| [flowchart-top-bottom.md](flowchart-top-bottom.md) | 流程图（上→下布局） |
| [flowchart-with-subgraphs.md](flowchart-with-subgraphs.md) | 分层流程图（含 subgraph 分组） |
| [flowchart-decision.md](flowchart-decision.md) | 决策/判断流程图（含菱形判断节点） |
| [sequence-diagram.md](sequence-diagram.md) | 时序图 |

## 使用方法

1. 复制对应模板的 Mermaid 代码块内容
2. 替换占位符文本（保持双引号包裹）
3. 修改节点连接关系
4. 运行 `python .agents/scripts/check-mermaid.py` 验证语法

## 安全编码五规则速查

1. **禁止空行**：代码块内无空行
2. **文本加引号**：中文/特殊字符节点用双引号包裹
3. **避免列表触发**：不用「数字+英文句点+空格」，改用中文冒号「1：」
4. **Subgraph 格式**：`subgraph EN_ID ["中文标题"]`
5. **边标签格式**：`-->|"标签"|目标节点`
