---
id: "templates-mermaid-templates-state-diagram"
title: "状态图模板"
source: "AGENTS.md#模板"
x-toml-ref: "../../../.meta/toml/.agents/templates/mermaid-templates/state-diagram.toml"
---
# 状态图模板

```mermaid
stateDiagram-v2
    [*] --> 待处理
    待处理 --> 处理中 : 开始执行
    处理中 --> 已完成 : 执行成功
    处理中 --> 失败 : 执行失败
    失败 --> 待处理 : 重试
    已完成 --> [*]
```

## 状态图语法要点

- 使用 `stateDiagram-v2`（v2版本兼容性更好）
- **状态名引号规则**：
  - 裸中文/英文标识符（无空格、无特殊字符）不需要引号：`待处理 --> 处理中`
  - 含空格或特殊字符（`/`、`:`、`{`、`}`等）的状态名需双引号包裹：`"等级 A/B"`
- **迁移标签**（`:` 后）：含空格/特殊字符时建议加双引号：`: "执行成功"`
- `state 状态ID : "中文描述"` 格式为状态添加描述，描述文本含空格时加引号
- `[*]` 表示起始/结束状态
- 复合状态：`state EN_ID { ... }` 或 `state "中文名称" as EN_ID { ... }`
- 代码块内禁止空行
- 避免列表触发：状态名/标签中不使用 `"1. 步骤"`、`"- 项目"` 等模式

## 含复合状态示例

```mermaid
stateDiagram-v2
    [*] --> 待机
    待机 --> RUNNING : 启动
    state "运行中" as RUNNING {
        [*] --> 初始化
        初始化 --> 执行任务
        执行任务 --> 等待
        等待 --> 执行任务 : 新任务到达
    }
    RUNNING --> 待机 : 停止
    待机 --> [*]
```
