---
id: "mermaid-quote-rules-checklist"
title: "Mermaid 引号规则检查清单"
source: "从02-06文件修复实践中萃取"
category: "learning"
tags: ["mermaid", "checklist", "quote-rules", "syntax", "best-practices", "troubleshooting"]
date: "2026-08-06"
status: "stable"
author: "SpecWeave"
summary: "Mermaid 各图表类型引号使用规则速查：16类图表引号矩阵、7条快速判断口诀、Top 5反模式、4步验证方法。解决Mermaid文档中最常见的引号误用问题（约70%语法错误源于引号）。"
---
# Mermaid 引号规则检查清单

> **适用场景**：编写或审查包含 Mermaid 代码块的 Markdown 文档时，快速核对引号使用是否正确。
>
> **背景**：在修复 mermaid-wiki 系列文档的实践中发现，约 70% 的 Mermaid 语法错误源于引号误用。Mermaid 不同图表类型的引号规则高度不统一——该加的不加、不该加的乱加，是最常见的错误来源。

---

## 核心原则

> **标识符（ID/Name/Key）含空格或中文时加引号；纯文本标签、描述、title 一律不加引号。**

- "标识符"指被解析器当作语法元素名称处理的部分（实体名、需求名、数据标签、轴标签、点名称、C4宏参数标签）。
- "纯文本"指仅用于显示、不被解析器用于语法匹配的部分（title、section、箭头标签、state描述、note文本、消息文本）。
- 遇到不确定的位置，**先用无引号版本测试**——大多数位置加引号反而报错。

---

## 一、按图表类型引号规则矩阵

| 图表类型 | title | section | 节点/实体标签 | 关系/箭头标签 | 数据值/属性 | 特殊语法注意 |
|---------|:-----:|:-------:|:------------:|:------------:|:----------:|------------|
| **flowchart** | ❌不加 | — | ✅ `ID["文本"]` 方括号内可加中文 | ❌ `--> label` 不加 | — | 不对称形 `G>"文本"]`（不多加`[`） |
| **sequenceDiagram** | ❌不加 | — | `participant A as "别名"` 别名加 | ❌ `->> msg` 不加 | — | Note 文本不加 |
| **classDiagram** | — | — | ✅ `class ID["中文"]` 方括号标签 | ❌ `<|-- : 标签` 不加 | 泛型`~T~`不加 | `<<interface>>` **全小写**；不要用 `class "中文" as ID` |
| **stateDiagram-v2** | — | — | ⚠️ `state "中文" as ID` 别名语法才加 | ❌ `--> : 事件` 不加 | — | **`state ID : 描述` 冒号后不加引号！**（最易踩坑） |
| **erDiagram** | — | — | ✅ `"中文实体"` 中文实体名必须加 | ❌ `: 关系标签` 不加 | 属性块`{}`内中文不加 | 属性key(PK/FK/UK)不加 |
| **gantt** | ❌不加 | ❌不加 | ❌任务名不加 | — | ❌日期/时长不加 | `vert`作任务标签（`名称 : vert, id, 日期, 时长`），不单独成行 |
| **pie** | ❌ `pie title 标题` | — | ✅ 数据标签必须加（`"Chrome" : 60`） | — | ❌数值不加 | `showData` 后 title 也不加 |
| **journey** | ❌不加 | ❌不加 | ❌任务名不加 | — | ❌score/actor不加 | `Task: score: actor` 格式 |
| **timeline** | ❌不加 | ❌不加 | ❌时间周期/事件均不加 | — | — | `direction TD/LR` 无引号 |
| **sankey** | — | — | ⚠️ v11.x **不支持中文节点名**；英文不加引号 | — | CSV三列不加 | 节点名含逗号时才加引号；建议用英文/拼音 |
| **quadrantChart** | ❌不加 | — | ✅ 轴标签/象限名/点名称必须加 | — | ❌坐标`[x,y]`不加 | `"产品A" : [0.6, 0.8]` |
| **gitGraph** | — | — | ⚠️ 分支名与关键字冲突时加（`branch "dev"`） | — | ✅ `id:"..."`/`tag:"..."` 属性值加 | `TB:`/`LR:` 方向冒号紧贴，无引号 |
| **requirementDiagram** | — | — | ✅ 中文名必须加（`requirement "登录功能"`） | ❌ `- contains ->` 不加 | ⚠️ `risk:high`/`verifymethod:test` 小写不加 | `docRef`驼峰；`text: "..."` 文本值加引号 |
| **mindmap** | — | — | ❌形状语法内直接写文本 | — | — | `root((文本))` 无引号 |
| **block** | — | — | ✅ `ID["文本"]` 方括号内可加中文 | ❌ `--> label` 不加 | — | 圆角 `A("文本")`，不是体育场形 `A(["文本"])` |
| **C4** | ❌ `title 标题` | — | ✅ 宏参数标签必须加（`Person(id, "标签", "描述")`） | ✅ `Rel()`中标签加引号 | — | 宏参数按位置或`$name=`命名 |
| **zenuml** | — | — | ❌参与者名不加 | ❌ `-> msg` 消息标签不加 | — | 需外部插件；**`if`/`while`条件中文必须加引号**（`if ("条件")`）；sync方法名`A.method()`需英文 |

**图例**：✅ = 必须/可以加引号　❌ = 不加引号　⚠️ = 特殊情况（见说明）　— = 该语法位置不存在

---

## 二、7 条快速判断口诀

写 Mermaid 代码块时，按以下顺序逐条检查：

1. **`title`/`section`/`direction`** → 一律**不加**引号
2. **节点/实体/需求的"标识符"本身是中文/含空格** → **加**引号（如 erDiagram `"客户"`、requirementDiagram `"登录功能"`、C4 宏参数）
3. **方括号标签内的文本**（`ID["中文"]`） → 方括号内可直接写中文（classDiagram/flowchart/block）
4. **箭头/关系/消息后的标签文本**（`--> label`、`: label`） → 一律**不加**引号
5. **`state ID : 描述`** → 冒号后描述**不加**引号！（最容易踩的坑，加引号会触发别名解析歧义导致 Parse error）
6. **pie 数据标签**（`"Chrome" : 60`）、**quadrantChart 轴标签/象限名/点名称** → **必须加**引号
7. **实验性图表（sankey）** → v11.x JISON 解析器不支持中文 Unicode 节点名，用英文/拼音，不加引号

---

## 三、Top 5 最常见反模式（来自实际修复案例）

| # | ❌ 错误写法 | ✅ 正确写法 | 错误后果 | 适用图表 |
|---|-----------|-----------|---------|---------|
| 1 | `state Idle : "空闲"` | `state Idle : 空闲` | Parse error: Expecting 'AS', got 'ID'（解析器误判为别名语法） | stateDiagram-v2 |
| 2 | `title "项目排期计划"` | `title 项目排期计划` | 标题显示异常或解析失败 | gantt/pie/journey/timeline/quadrantChart/C4 |
| 3 | `class "动物" as Animal` | `class Animal["动物"]` | 类无法渲染，标签不显示 | classDiagram |
| 4 | `<<Interface>>` | `<<interface>>` | 注解（stereotype）无法识别渲染 | classDiagram |
| 5 | `A --> B : "处理"` | `A --> B : 处理` | 标签显示带引号或解析异常 | stateDiagram/flowchart/classDiagram/zenuml |

### 其他高频错误（非引号类，但经常伴随出现）

| ❌ 错误 | ✅ 正确 | 说明 |
|---------|---------|------|
| `G>["不对称形"]` | `G>"不对称形"]` | flowchart 不对称形节点，多了一个 `[` |
| `A(["圆角"])` | `A("圆角")` | block 圆角形，`(["..."])` 是体育场（stadium）形 |
| `vert 2026-08-05`（独立行） | `截止线 : vert, v1, 2026-08-05, 1d` | gantt 中 vert 是任务标签，不是独立指令 |
| `docref` | `docRef` | requirementDiagram 中驼峰命名 |
| `risk: High` | `risk: high` | requirementDiagram 中枚举值小写 |

---

## 四、4 步验证方法

写完 Mermaid 代码块后，按以下顺序验证：

1. **静态检查（30秒）**
   - 对照本清单的"7条口诀"逐条过一遍
   - 重点检查 stateDiagram 冒号描述、各类 title、箭头标签
   - 检查 `<<interface>>` 是否全小写

2. **本地 HTTP 验证（推荐，1分钟）**
   - 创建临时 HTML 文件，引入 `https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js`
   - 用 `mermaid.render(id, code)` 逐个渲染代码块
   - 捕获异常，打印 Parse error 信息定位问题行

3. **Mermaid Live Editor（最权威）**
   - 粘贴代码到 <https://mermaid.live/>
   - 观察右侧预览是否正常渲染
   - 注意：Live Editor 可能比本地 CDN 版本更新，语法以本地使用版本为准

4. **中文特殊检查**
   - 含中文的位置额外留意：sankey v11.x 不支持中文节点名
   - stateDiagram 中文状态名建议用 `state "中文名" as ID` 别名语法
   - erDiagram 中文实体名必须用引号包裹

---

## 五、补充说明

### 为什么 Mermaid 引号规则这么"乱"？

Mermaid 各图表的解析器是独立开发的（基于 JISON），没有统一的词法分析层，导致引号处理逻辑不一致：

- 早期图表（flowchart/classDiagram/sequenceDiagram）使用 JISON 解析器，对引号敏感
- 数据类图表（pie/quadrantChart/requirementDiagram）从其他工具借鉴语法，数据标签用引号
- 实验性图表（sankey/zenuml/C4）解析器实现较新，规则又不同
- gantt/pie/journey 的 `title` 是"关键字+空格+文本"模式，文本不需要引号

**记忆技巧**：凡是 Mermaid 语法中"文本作为数据"（pie切片名、象限名、需求名、C4标签）的位置加引号；凡是"文本作为显示标签"（title、section、箭头标签、state描述、note）的位置不加引号。

### 版本差异提醒

- 本文档基于 Mermaid **v11.x**（CDN `mermaid@11`）验证。
- v10.x 及更早版本可能在个别图表上有不同行为，建议统一使用 v11。
- sankey 的中文支持可能在未来版本改进，使用前请用 Live Editor 验证当前版本。
- zenuml 需要额外注册 `@mermaid-js/mermaid-zenuml` 插件，CDN 默认不含此渲染器。

---

> **相关文档**：
> - [Mermaid 教程总览](00-overview.md)
> - [类图/状态图/ER图](04-class-state-er.md)
> - [Gantt/Pie/Journey/Timeline/Sankey/QuadrantChart](05-aggregate-diagrams.md)
> - [GitGraph/Requirement/Mindmap/Block/C4/ZenUML](06-advanced-diagrams.md)
> - [FAQ 与最佳实践](09-faq-best-practices.md)
> - [速查表](10-cheatsheet.md)
