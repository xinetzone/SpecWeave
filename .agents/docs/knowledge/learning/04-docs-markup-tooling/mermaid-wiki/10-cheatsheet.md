---
id: "mermaid-wiki-10-cheatsheet"
title: "Mermaid 命令速查表（Cheatsheet）"
source: "https://mermaid.js.org/"
category: "learning"
tags: ["mermaid","cheatsheet","速查","flowchart","sequenceDiagram","classDiagram","stateDiagram","erDiagram","gantt","pie","journey","timeline","sankey","quadrantChart","gitGraph","requirementDiagram","mindmap","block","c4","zenuml","markup"]
date: "2026-08-06"
status: "stable"
author: "SpecWeave"
summary: "Mermaid 命令速查表：覆盖全部 17 种图表类型（flowchart/sequenceDiagram/classDiagram/stateDiagram-v2/erDiagram/gantt/pie/journey/timeline/sankey/quadrantChart/gitGraph/requirementDiagram/mindmap/block/C4/zenuml）的关键字与核心语法行，常用配置速查（initialize/主题/securityLevel/渲染器），以及 mermaid.live 使用速查。"
---
# Mermaid 命令速查表（Cheatsheet）

本章是 Mermaid 的**快速查阅手册**，覆盖全部 17 种图表类型的关键字与核心语法行、常用配置速查、以及 mermaid.live 使用速查。所有事实均以 Mermaid 官方文档（https://mermaid.js.org/）为准。

> **排版约定**：语法行示例放在 `text` 代码块或表格中，便于快速复制与对照；`<...>` 为占位符，使用时应替换为实际内容。

## 一、图表类型速查（17 种）

### 1. flowchart 流程图

关键字：`flowchart`（别名 `graph`）

```text
flowchart LR
    A["文本"] --> B{"判断"}
    B -->|"是"| C["处理"]
    B -->|"否"| D["结束"]
```

常用：方向 `TB/TD/BT/RL/LR`；节点形状 `A[ ]` `A( )` `A{[ ]}` `A(( ))` `A[[ ]]` `A[( )]`；连线 `-->` `---` `-.->` `==>` `--o` `--x`；subgraph。

### 2. sequenceDiagram 时序图

关键字：`sequenceDiagram`

```text
sequenceDiagram
    participant U as "用户"
    participant S as "服务"
    U->>S: "请求"
    S-->>U: "响应"
    Note over U,S: "说明"
```

常用：箭头 `->` `-->` `->>` `-->>` `-x` `-)`；`activate`/`deactivate`；`Note right of/left of/over`；`loop/alt/opt/par/critical ... end`；`autonumber`。

### 3. classDiagram 类图

关键字：`classDiagram`

```text
classDiagram
    class Animal
    Animal <|-- Dog
    Dog : +name String
    Dog : +bark() void
```

常用：可见性 `+ - # ~`；泛型 `~T~`；关系 `<|--` `*--` `o--` `-->` `..>` `..|>` `--` `..`；基数 `"1" "0..*"`；`namespace`。

### 4. stateDiagram-v2 状态图

关键字：`stateDiagram-v2`

```text
stateDiagram-v2
    [*] --> Idle
    Idle --> Running : "启动"
    Running --> [*] : "完成"
```

常用：`[*]` 开始/结束；复合状态 `state X { ... }`；`<<choice>>`；`note right of A`；`direction LR`。

### 5. erDiagram ER 图

关键字：`erDiagram`

```text
erDiagram
    CUSTOMER ||--o{ ORDER : "下单"
    CUSTOMER { string name }
    ORDER { int id }
```

常用：基数 `|o` `||` `}o` `}|`；识别 `--`、非识别 `..`；属性块 `{ type name }`；`direction`；`layout: elk`。

### 6. gantt 甘特图

关键字：`gantt`

```text
gantt
    title 项目排期
    dateFormat YYYY-MM-DD
    section 阶段一
    任务A :a1, 2026-08-01, 3d
```

常用：`dateFormat`/`axisFormat`/`tickInterval`；标签 `active/done/crit/milestone`；`excludes`；`todayMarker`；`until`（v10.9.0+）。

### 7. pie 饼图

关键字：`pie`

```text
pie title 数据分布
    "A类" : 50
    "B类" : 30
    "C类" : 20
```

可选 `showData`；数值须为正数；v11.16.0+ 支持 `donutHole`、`legendPosition`、`highlightSlice`。

### 8. journey 用户旅程图

关键字：`journey`

```text
journey
    title 购物流程
    section 下单
    浏览商品: 4: 用户
    提交订单: 5: 用户, 客服
```

任务语法：`Task name: <score>: <actor 列表>`，score 为 1–5 整数。

### 9. timeline 时间线图

关键字：`timeline`

```text
timeline
    title 项目里程碑
    2026 Q1 : 需求评审
    2026 Q2 : 开发
```

`section 名称` 分组；`<br>` 强制换行；v11.14.0+ 支持 `LR`/`TD` 方向。

### 10. sankey 桑基图

关键字：`sankey`（v10.3.0+，实验性）

```text
sankey-beta
    源节点,目标节点,数值
    上游,中游,100
```

语法接近纯 CSV：3 列（source/target/value），含逗号的值用双引号包裹；配置 `linkColor`、`nodeAlignment`、`nodeWidth`、`nodePadding`。

### 11. quadrantChart 象限图

关键字：`quadrantChart`

```text
quadrantChart
    title 优先级矩阵
    x-axis 低影响 --> 高影响
    y-axis 低价值 --> 高价值
    quadrant-1 重要
    项目A: [0.8, 0.8]
```

点坐标 `[x, y]` 范围 0–1；`quadrant-1..4 <text>`。

### 12. gitGraph Git 图

关键字：`gitGraph`

```text
gitGraph
    commit id: "c1"
    branch "feature"
    checkout "feature"
    commit
    checkout main
    merge "feature"
```

命令：`commit`/`branch`/`checkout`（或 `switch`）/`merge`/`cherry-pick`；方向 `LR:`（默认）/`TB:`/`BT:`。

### 13. requirementDiagram 需求图

关键字：`requirementDiagram`

```text
requirementDiagram
    requirement 登录 { id: 1, text: "支持登录", risk: Medium, verifymethod: Test }
    element 登录模块 { type: 软件 }
    登录 - satisfies -> 登录模块
```

类：`requirement`/`element`/relationship；关系类型 `contains`/`derives`/`satisfies`/`verifies`/`refines`/`traces`/`copies`。

### 14. mindmap 思维导图

关键字：`mindmap`

```text
mindmap
    root((项目))
        前端
            页面
            组件
        后端
            API
            数据库
```

依赖缩进定义层级；形状 `(( ))` 圆形、`[ ]` 方形等；`layout: tidy-tree`。

### 15. block 块图

关键字：`block`

```text
block-beta
    columns 3
    A["块A"] B["块B"] block C
        C1["子块"]
    end
```

说明：`block-beta` 为块图渲染标识；`columns` 控制列数；`space` 占用列；块可用 `style`。

### 16. C4 架构图

关键字：`C4Context`（及 `C4Container`/`C4Component`/`C4Dynamic`/`C4Deployment`）

```text
C4Context
    title 系统上下文
    Person(用户, "普通用户")
    System(核心系统, "核心系统")
    Rel(用户, 核心系统, "使用")
```

宏：`Person`/`System`/`Container`/`Component`/`Rel`/`BiRel`/`Boundary`；样式更新 `UpdateElementStyle`/`UpdateRelStyle`。

### 17. zenuml 增强时序图

关键字：`zenuml`

```text
zenuml
    Alice -> Bob : "同步调用"
    Bob -> Alice : @return
    while (重试)
        Alice -> Bob : "尝试"
    end
```

语法与原生时序图不同：`new` 创建、`@return` 返回、`{}` 嵌套；`while/for/forEach/loop`；`if/else`；`par`；`try/catch/finally`；注释 `//`。

## 二、图表类型速查总表

| # | 图表 | 关键字 | 核心语法行 |
|---|------|--------|-----------|
| 1 | flowchart | `flowchart` | `A["文本"] --> B{"判断"}` |
| 2 | sequenceDiagram | `sequenceDiagram` | `A->>B: "消息"` |
| 3 | classDiagram | `classDiagram` | `Animal <|-- Dog` |
| 4 | stateDiagram-v2 | `stateDiagram-v2` | `Idle --> Running : "启动"` |
| 5 | erDiagram | `erDiagram` | `CUSTOMER \|\|--o{ ORDER : "下单"` |
| 6 | gantt | `gantt` | `任务A :a1, 2026-08-01, 3d` |
| 7 | pie | `pie` | `"A类" : 50` |
| 8 | journey | `journey` | `任务: 4: 用户` |
| 9 | timeline | `timeline` | `2026 Q1 : 里程碑` |
| 10 | sankey | `sankey-beta` | `源,目标,100` |
| 11 | quadrantChart | `quadrantChart` | `点A: [0.8, 0.8]` |
| 12 | gitGraph | `gitGraph` | `commit` / `branch "f"` |
| 13 | requirementDiagram | `requirementDiagram` | `需求 - satisfies -> 元素` |
| 14 | mindmap | `mindmap` | `root((父))` |
| 15 | block | `block-beta` | `block { ... }` |
| 16 | C4 | `C4Context` | `Rel(用户, 系统, "使用")` |
| 17 | zenuml | `zenuml` | `A -> B : "调用"` |

## 三、常用配置速查

### initialize 初始化

`mermaid.initialize(config)` 在站点级覆盖默认配置，**只调用一次**。

```text
mermaid.initialize({ startOnLoad: true, theme: 'base', securityLevel: 'loose' })
```

### 5 个内置主题

| 主题名 | 说明 |
|--------|------|
| `default` | 所有图的默认主题 |
| `neutral` | 适合黑白/打印文档 |
| `dark` | 深色模式（可结合 `darkMode: true`） |
| `forest` | 绿色系 |
| `base` | 唯一可修改的主题，自定义配色的基础 |

用 frontmatter 的 `themeVariables` 自定义主题（仅 `base` 可修改）；主题引擎只识别十六进制颜色（如 `#ff0000`）。

### securityLevel 安全级别

```text
securityLevel: 'strict'    # 默认，禁用 click 交互
securityLevel: 'loose'     # 启用交互
securityLevel: 'antiscript'
securityLevel: 'sandbox'
```

### 渲染器

| 渲染器 | 说明 |
|--------|------|
| `dagre` | flowchart 默认渲染器 |
| `elk` | v9.4+ 实验性渲染器，适合大型/复杂图，需 `flowchart.defaultRenderer: "elk"` |

### frontmatter 配置示例

```yaml
---
config:
  theme: base
  themeVariables:
    primaryColor: "#ff0000"
  flowchart:
    defaultRenderer: "dagre"
---
```

## 四、mermaid.live 使用速查

**地址**：https://mermaid.live/ ｜ **仓库**：`mermaid-js/mermaid-live-editor`

| 操作 | 说明 |
|------|------|
| 左侧写代码 | 输入图表定义 |
| 右侧实时渲染 | 输入即生成 SVG |
| 导出 PNG / SVG | 下载为图片资产 |
| 生成分享链接 | 便于协作分享 |
| 浏览器端处理 | 数据不上传，隐私友好 |
| 视频教程 | 官方 intro 页提供（Ecosystem/Tutorials） |

> **建议**：先用 mermaid.live 验证语法，确认无误后再嵌入项目文档，并运行 `check-mermaid.py` 校验（见上一章安全编码规范）。

## 五、mermaid-cli 速查

```bash
npm install -g @mermaid-js/mermaid-cli
mmdc -i input.mmd -o output.png
mmdc -i input.mmd -o output.png -w 1200
```

配置文件为 JSON（可配主题、字体、日志级别等）。

---

**上一章**：[第 9 章 — 常见问题与最佳实践 ←](09-faq-best-practices.md) | **返回**：[教程总览 →](00-overview.md)