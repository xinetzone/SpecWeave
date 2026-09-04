# Mermaid 官方文档客观事实采集

> 说明：本文件所有事实均来自 Mermaid 官方文档（实际域名 `https://mermaid.js.org/`，而非任务清单中的 `https://mermaid.ai/`，后者无法访问）。官方文档现行路径为 `/syntax/<图表名>.html`、`/config/configuration.html`、`/config/theming.html` 等。部分页面（flowchart、classDiagram 等）因体积过大，通过 defuddle 提取正文获得。所有内容均为客观描述，不含推断。

---

## 1. 简介 / 快速入门（intro）

- Mermaid 是一个基于 JavaScript 的图表绘制与可视化工具，使用受 Markdown 启发的文本定义和渲染器来创建、修改复杂图表。（来源：https://mermaid.js.org/intro/）
- Mermaid 的核心目的是「帮助文档跟上开发进度」，解决文档与实际开发脱节（Doc-Rot）的问题。
- 每个图表类型对应一个图表「关键字」作为起始声明，例如 `flowchart`、`sequenceDiagram`、`classDiagram`、`gantt`、`erDiagram`、`journey`（用户旅程）、`quadrantChart`、`xychart-beta`、`gitGraph` 等。
- 官方提供入门示例（intro 页列出的 Diagram Types 示例代码）：
  - Flowchart：`graph TD; A-->B; A-->C; B-->D; C-->D;`
  - Sequence diagram：`sequenceDiagram` + `participant Alice/Bob` + `Alice->>John: ...`
  - Gantt：`gantt` + `dateFormat` + `title` + `excludes` + `section`
  - Class diagram：`classDiagram` + 各类关系符号（`<|--`、`*--`、`o--`、`..`、`-->` 等）
  - Git graph：`gitGraph` + `commit`/`branch`/`checkout`
  - ER 图：`erDiagram` + crow's foot 基数标记（文档标注为「experimental」）
  - User Journey：`journey` + `title` + `section`
  - Quadrant Chart：`quadrantChart` + `title`/`x-axis`/`y-axis`/`quadrant-1..4` + 点 `[x, y]`
  - XY Chart：`xychart-beta` + `x-axis`/`y-axis`/`bar`/`line`
- 安装方式：
  - CDN：`https://cdn.jsdelivr.net/npm/mermaid@<version>/dist/`，最新版为 `https://cdn.jsdelivr.net/npm/mermaid@11`。
  - npm：`npm i mermaid`；yarn：`yarn add mermaid`；pnpm：`pnpm add mermaid`。
  - 部署需要 Node v16（含 npm）。
- 无打包器部署示例：HTML 中插入 `<script type="module">import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs'; mermaid.initialize({ startOnLoad: true });</script>`，Mermaid 解析器会查找 `class="mermaid"` 的 `<div>` 或 `<pre>` 标签并渲染为 SVG。
- 布局/绘制底层依赖 d3 与 dagre-d3；时序图语法源自 js-sequence-diagram；甘特图渲染受 Jessica Peter 项目启发。
- 安全说明：对外部用户开放的站点，Mermaid 会尝试净化输入代码，并提供了在沙箱 iframe 中渲染图表的更高安全级别，但会牺牲部分交互功能。

---

## 2. Flowchart（流程图）

- 组成：**节点（node，几何形状）** 与 **边（edge，箭头/连线）**。
- 关键字：`flowchart`（也可用 `graph`）。
- 方向（方向声明语句）：`TB`（Top→Bottom）、`TD`（Top-down，同 TB）、`BT`、`RL`、`LR`。
- 节点形状（括号语法）：
  - 默认方形 `A`；带文本 `A[text]`；圆角 `A(text)`；体育场形 `A([text])`；子程序形 `A[[text]]`；圆柱形 `A[(text)]`；圆形 `A((text))`；不对称形 `A>text]`；菱形（rhombus）`A{text}`；六边形 `A{{text}}`；平行四边形 `A[/text/]`（alt 用 `A[\text\]`）；梯形 `A[/text\]`（alt 用 `A[\text/]`）；双圆 `A(((text)))`。
- 特殊字符注意（官方 WARNING）：
  - 若节点文本用到 `end`，需大写（如 `End`/`END`），否则会破坏 flowchart。
  - 若连接节点名以字母 `o` 或 `x` 开头，需加空格或大写，否则 `A---oB` 会生成「circle edge」、`A---xB` 会生成「cross edge」。
- 扩展形状（v11.3.0+）：新增 30 个形状，通用语法 `A@{ shape: rect }`（等价于 `A["A"]` 或 `A`）。短名/别名例如 `rect`(process)、`diam`(decision)、`hex`(hexagon)、`cyl`(database)、`stadium`(terminal)、`circle`(start)、`dbl-circ`(stop)、`bolt`(com-link)、`doc`(document)、`datastore`、`flag`(paper-tape) 等约 30 种。
- 特殊形状（v11.3.0+）：`icon`（需先注册图标包，参数 form/label/pos/h）与 `image`（参数 img/label/pos/w/h/constraint）。
- 连线类型：
  - 箭头 `A-->B`；开放线 `A---B`；带文本 `A-- text ---B` 或 `A---|text|B`；箭头+文本 `A-->|text|B` 或 `A-- text -->B`；虚线 `A-.->B`；虚线+文本 `A-. text .->B`；粗线 `A==>B`；粗线+文本 `A== text ==>B`；隐形线 `A~~~B`。
  - 圆形边 `--o`、交叉边 `--x`；多方向箭头 `A<-->B`、`A<---B`、`A<==>B`。
  - 给边赋 ID：在边语法前加 `ID@`，如 `e1@-->`；可对边开启动画（`{ animate: true }`，速度 `fast`/`slow`）。
- 连线长度：可多加短横线/等号/点使边跨更多层级（normal `---`、thick `===`、dotted `-.-` 等）。
- 特殊字符转义：用引号包裹，或用实体码（如 `#` 编码为 `#35;`，支持 HTML 字符名）。
- Subgraph：`subgraph title ... end`；可设显式 ID；`graph` 类型可对 subgraph 设方向（用 `direction` 语句）；若 subgraph 节点有外部链接，则 subgraph 方向被忽略，继承父图方向。
- Markdown Strings：支持节点标签、边标签、subgraph 标签的粗体（`**`）与斜体（`*`），并自动换行；可用 `markdownAutoWrap: false` 关闭自动换行。
- 交互：`click nodeId callback` / `click nodeId callback() "tooltip"` / `click nodeId href "url"`；`securityLevel='strict'` 时禁用，`loose` 时启用；链接目标支持 `_self`/`_blank`/`_parent`/`_top`。tooltip 样式由 `.mermaidTooltip` 类控制。
- 注释：行首 `%%` 表示注释。
- 样式：
  - `classDef className fill:#f9f,stroke:#333,stroke-width:4px;`
  - `class nodeId className`；简写 `node:::className`。
  - 名为 `default` 的类会应用到所有节点。
  - 连线样式用 `linkStyle 序号 属性`，如 `linkStyle 3 stroke:#ff3,stroke-width:4px,color:red;`（序号为边定义顺序）。
  - 曲线类型：`basis`、`bumpX`、`bumpY`、`cardinal`、`catmullRom`、`linear`、`monotoneX`、`monotoneY`、`natural`、`step`、`stepAfter`、`stepBefore`（源自 d3-shape）。
  - 外部 CSS 覆盖节点样式不可靠（内部样式带 `!important` 且作用域限于 SVG 元素 ID），推荐用 `classDef`。
- FontAwesome：`fa:#icon class name#`；支持前缀 `fa/fab/fas/far/fal/fad`（v11.7.0+ 可注册 pack），自定义图标用 `fak` 前缀。
- 渲染器（Renderer）：默认 `dagre`；v9.4+ 可用 `elk`（更适合大型/复杂图，实验性）。配置文件 `flowchart.defaultRenderer: "elk"`。
- 配置：`mermaid.flowchartConfig`（如 `width: 100%`）。

---

## 3. Sequence diagram（时序图）

- 关键字：`sequenceDiagram`。
- Participant（参与者）：可隐式声明（按出现顺序渲染），可显式 `participant Alice`；`actor` 用 actor 符号；`participant`/`actor` 支持 `as` 定义别名（如 `Alice as A`），也可在配置对象中用 `"alias"` 字段；外部别名（`as`）优先于内联别名。
- 参与者符号类型（JSON 配置）：boundary、control、entity、database、collections、queue 等。
- 创建/销毁参与者（v10.3.0+）：`create participant B`、`destroy A`；被销毁的参与者需有对应的销毁消息。若报错且修复代码无效，需升级到 v10.7.0+。
- 分组（Box）：`box 颜色/描述 ... end`；组名若为颜色可加 `transparent` 强制透明。
- 消息语法：`[Actor][Arrow][Actor]:消息文本`。
  - 标准箭头类型表：`->`(实线无箭头)、`-->`(虚线无箭头)、`->>`(实线箭头)、`-->>`(虚线箭头)、`<<->>`(双向实线，v11.0.0+)、`<<-->>`(双向虚线，v11.0.0+)、`-x`(实线末端交叉)、`--x`(虚线末端交叉)、`-)`(实线开放箭头/异步)、`--)`(虚线开放箭头/异步)。
  - 半箭头（v11.12.3+）：`-\|\\`、`--\|\\`、`-\|/`、`--\|/` 等 16 种。
  - 中央连接（v11.12.3+）：在箭头语法后追加 `()` 表示连接到中央生命线。
- 激活（Activation）：`activate Alice`/`deactivate Alice`；快捷方式在消息箭头后加 `+`/`-` 后缀；同一 actor 可叠加激活。
- 注释（Note）：`Note [right of | left of | over] [Actor]: 文本`，可跨两个参与者（`Note over A,B`）。
- 换行：Note 和 Message 支持换行；actor 名换行需用别名。
- 循环/分支块：
  - `loop 文本 ... end`
  - `alt 文本 ... else ... end`；`opt 文本 ... end`（if 无 else）
  - `par [Action] ... and [Action] ... end`（并行，可嵌套）
  - `critical [...] ... option [...] ... end`（临界区，可嵌套）
  - `break [...] ... end`
  - 背景高亮：`rect rgb(...) ... end` / `rect rgba(...) ... end`
- 实体码转义：数字为十进制（`#` → `#35;`），支持 HTML 字符名；分号用 `#59;`。
- 序号：`mermaid.initialize({ sequence: { showSequenceNumbers: true } })` 或图内 `autonumber`；可自定义起始值/增量（v11.15.0+）：`autonumber <start> <increment>`。
- Actor 菜单：`link <actor>: <label> @ <url>`；进阶 JSON 语法 `links <actor>: ...`。
- 样式：通过 CSS 类（来自 `src/themes/sequence.scss`），如 `.actor`、`.actor-line`、`.messageLine0/1`、`.messageText`、`.labelBox`、`.labelText`、`.loopText`、`.loopLine`、`.note`、`.noteText` 等。
- 配置：`mermaid.sequenceConfig`，参数含 `diagramMarginX`、`diagramMarginY`、`boxTextMargin`、`noteMargin`、`messageMargin`、`mirrorActors`（默认 false）等；`mirrorActors`、`actorFontSize`(14)、`noteFontSize`(14)、`messageFontSize`(16) 等如表所示。

---

## 4. Class diagram（类图）

- 关键字：`classDiagram`。
- 类定义两种方式：显式 `class Animal`；通过关系隐式定义（如 `Vehicle <|-- Car`）。
- 类名命名：仅由字母数字（含 unicode）、下划线、短横线组成。
- 类标签：可用 `class "标签" as Animal` 或反引号转义特殊字符。
- 成员定义：
  - 用 `:` 逐个定义（有 `()` 视为方法，否则视为属性）；用 `{}` 块一次定义多个。
  - 返回类型：方法末尾加类型（`name() int`，`()` 与返回类型间需空格）。
  - 泛型：用 `~`（如 `List~int~`），支持嵌套如 `List~List~int~~`；含逗号的泛型暂不支持。
  - 可见性前缀：`+` 公开、`-` 私有、`#` 受保护、`~` 包内/内部。
  - 方法分类符后缀：`*` 抽象、`$` 静态；字段可用 `$` 静态。
- 关系类型（8 种）：`<|--` 继承、`*--` 组合、`o--` 聚合、`-->` 关联、`--` 实线链接、`..>` 依赖、`..|>` 实现、`..` 虚线链接。
- 关系标签：`[classA][Arrow][ClassB]:LabelText`。
- 双向关系：`[关系类型][连线][关系类型]`，如 `<|`/`*`/`o`/`>`/`<`/`|>` 与 `--`(实线)/`..`(虚线)。
- Lollipop 接口：`bar ()-- foo`、`foo --() bar`。
- 命名空间：`namespace name { ... }`；标签（v11.15.0+，方括号）、嵌套（v11.15.0+，点号或语法嵌套）；`hierarchicalNamespaces: false` 切换紧凑渲染。
- 基数/多重性（Cardinality）：`1`、`0..1`、`1..*`、`*`、`n`、`0..n`、`1..n`；置于箭头两侧引号内：`[classA] "cardinality1" [Arrow] "cardinality2" [ClassB]:LabelText`。
- 注解：`<<Interface>>`、`<<Abstract>>`、`<<Service>>`、`<<Enumeration>>` 等，可内联、单独行、或嵌套结构。
- 交互：`action className "ref" "tooltip"`、`click className callback() "tooltip"`、`click className href "url"`；`securityLevel='strict'` 禁用交互。
- 注释：`note "line1\nline2"`、`note for <CLASS> "..."`。
- 方向：`direction` 语句。
- 样式：`style` 关键字、`classDef`、`cssClass "nodeId" className`、`:::` 简写；`classDef default` 应用到所有节点。
- 配置：`hideEmptyMembersBox`（默认 false）可隐藏空成员框。

---

## 5. State diagram（状态图）

- 关键字：`stateDiagram-v2`（另有旧渲染器）。语法尽量与 PlantUML 兼容。
- 状态声明方式：仅 id；`state 描述`；`state id : 描述`。
- 转换：`A --> B`（未定义的状态会自动创建）；转换文本 `A --> B : 文本`。
- 开始/结束：`[*]` 特殊状态，根据转换方向决定是开始或结束。
- 复合状态（Composite）：`state id { ... }`，可多层嵌套，可在复合状态间设转换；**不能在不同复合状态的内部状态之间设转换**。
- 选择（choice）：`<<choice>>`；分叉（fork/join）：`<<fork>>`、`<<join>>`。
- 注释（Note）：`note right of A` / `note left of A`。
- 并发：用 `--` 符号。
- 方向：`direction` 语句。
- 注释：`%%`。
- 样式（classDef）：限制——不能应用于开始/结束状态，不能应用于复合状态或其内部（开发中）。
  - `classDef 名称 属性:值,属性:值`；应用方式：`class 状态1,状态2 样式名`，或三冒号 `[state]:::[style name]`。
- 带空格状态名：先定义 id，再引用 id。

---

## 6. ER diagram（ER 图）

- 关键字：`erDiagram`。
- 语法与 PlantUML 兼容，扩展了关系标签。语句：`<first-entity> [<relationship> <second-entity> : <relationship-label>]`。实体名支持任意 unicode，含空格需用双引号。
- 基数（crow's foot 标记）：`|o`/`o|` 零或一、`||` 恰好一、`}o`/`o{` 零或多、`}|`/`|{` 一或多；支持别名（zero or one、one or more、1+、0+ 等）。
- 识别（Identification）：`--` 识别（实线）、`..` 非识别（虚线）；别名 `to`（识别）、`optionally to`（非识别）。
- 属性：实体名后跟 `{ type name }` 块；`type` 需以字母开头，可含数字、连字符、下划线、括号、方括号；`name` 可用 `*` 表示主键。可选类型后缀 `?` 表示可空（v11.16.0+）。
- 实体别名：方括号 `ENTITY[alias]`。
- 属性键/注释（v11.16.0+ 相关）：key 可为 `PK`/`FK`/`UK`，可逗号分隔（如 `PK, FK`）；注释用末尾双引号（注释内不能含双引号）。
- 方向：`direction`，取值 `TB`/`BT`/`RL`/`LR`。
- 样式：`style`、`classDef`、`class`、`:::`（可一次多类）。
- 布局：默认 `dagre`；可配置 `layout: elk`（需 mermaid 9.4+ 并启用懒加载）。

---

## 7. Gantt（甘特图）

- 关键字：`gantt`。可渲染为 SVG、PNG 或 Markdown 链接。
- 任务默认顺序执行，开始日期默认取前一任务结束日期。
- 任务元数据：冒号分隔标题与元数据，元数据用逗号分隔；合法标签 `active`、`done`、`crit`、`milestone`（标签可选，若用须最先写）。
- 元数据组合（开始/结束/ID）：`<taskID>,<startDate>,<endDate>`、`<taskID>,after <otherTaskID>,<length>`、`until`（v10.9.0+，表示运行到某任务/里程碑开始）等约 20 种组合。
- 时长单位：`ms`、`s`、`m`、`h`、`d`、`w`、`M`(月)、`y`(年)；支持小数（如 `1.5d`）；非法 token 忽略并默认零时长。
- `title`（可选，图表标题）；`section`（必需命名，划分部分）；`excludes`（排除日期，接受 YYYY-MM-DD、星期名、"weekends"，不支持 "weekdays"）；`weekend`（v11.0.0+，可设 weekend 为 friday 或 saturday 起始）。
- Milestone：`milestone` 关键字，位置 = 初始日期 + 时长/2。
- Vertical Markers（垂直标记线）：`vert` 关键字，不占行。
- 日期格式：
  - 输入 `dateFormat`（默认 `YYYY-MM-DD`，基于 day.js）。
  - 输出轴 `axisFormat`（默认 `YYYY-MM-DD`，基于 d3-time-format，如 `%Y-%m-%d`）。
  - 刻度 `tickInterval`（v10.3.0+，如 `1day`/`1week`；`millisecond`/`second` 支持也属 v10.3.0）。
- 紧凑模式（compact mode，多任务同行）：通过前置 YAML 配置 `displayMode`。
- 样式：CSS 类来自 `src/diagrams/gantt/styles.js`，如 `.grid .tick`、`.grid path`、`.taskText`、`.taskTextOutsideRight/Left`、`todayMarker`。
- Today marker：`todayMarker` 键设置样式，设为 `off` 隐藏。
- 配置：`mermaid.ganttConfig`，参数如 `titleTopMargin`、`barHeight`、`barGap`、`topPadding`、`rightPadding`、`leftPadding`、`gridLineStartPadding`、`fontSize`、`sectionFontSize`、`numberSectionStyles`、`axisFormat`、`tickInterval`、`topAxis`、`displayMode`、`weekday`。配置表另含 `mirrorActor`、`bottomMarginAdj`。
- 交互：`click taskId call callback(arguments)`、`click taskId href URL`；`securityLevel='strict'` 禁用。

---

## 8. Pie（饼图）

- 关键字：`pie`；可选 `showData`（在图例后显示实际数值）、可选 `title`。
- 数据格式：`"label": positive numeric value`（数值支持最多两位小数）。
- 数值必须为**正的、大于零的数**，负值会报错。
- Donut 环形图（v11.16.0+）：配置 `donutHole`（合法值 0–0.9，默认 0）。
- 图例位置（v11.16.0+）：配置 `legendPosition`，合法值 `top`/`bottom`/`left`/`right`/`center`（默认 right）。
- 高亮切片（v11.16.0+）：配置 `highlightSlice`（按 label 高亮，设 `hover` 悬停高亮）。
- 配置参数表：`textPosition`(0.75)、`donutHole`(0)、`legendPosition`(right)、`highlightSlice`。

---

## 9. User Journey（用户旅程图）

- 关键字：`journey`。
- 结构：`title` + `section 名称` + 任务。
- 任务语法：`Task name: <score>: <逗号分隔的 actor 列表>`。
- Score 为 1 到 5 的整数（含端点）。

---

## 10. Timeline（时间线图）

- 实验性图表（语法可随版本变化；除图标集成外语法稳定）。
- 关键字：`timeline`；可选 `title`。
- 数据语法：`{时间周期} : {事件}`，可用第二个冒号加更多事件，或换行多行事件。
- 时间周期与事件均为纯文本，不限于数字。
- 分组：`section 名称`，其后续时间周期归入该 section（同 section 用相似配色）。
- 换行：默认自动换行；可用 `<br>` 强制换行。
- 方向（v11.14.0+）：`LR`（左右，默认）、`TD`（上下）。
- 配色：无 section 时每个时间周期默认独立配色；配置 `timeline.disableMulticolor: false` 可让所有周期同色。
- 主题变量：`cScale0`–`cScale11`（背景色，最多 12 个 section，超出循环）、`cScaleLabel0`–`cScaleLabel11`（前景色）。
- 主题：`base`、`forest`、`dark`、`default`、`neutral`。
- 集成：使用实验性懒加载/异步渲染；CDN 引入方式同前。

---

## 11. Sankey（桑基图）

- 关键字：`sankey`（v10.3.0+），实验性图表。
- 语法接近纯 CSV：需 3 列（`source`、`target`、`value`）；允许无逗号分隔的空行；逗号需用双引号包裹；双引号用成对双引号转义。
- 配置：`width`、`height`、`linkColor`、`nodeAlignment`。
- `linkColor` 取值：`source`、`target`、`gradient`（渐变），或十六进制颜色。
- `nodeAlignment` 取值：`justify`、`center`、`left`、`right`。
- 标签样式（v11.15.0+）：`labelStyle`，`legacy`（默认）或 `outlined`。
- 节点尺寸（v11.15.0+）：`nodeWidth`（默认 10）、`nodePadding`（默认 12）。
- 自定义节点颜色（v11.15.0+）：`nodeColors` 映射，值须为合法 CSS 颜色。

---

## 12. Quadrant Chart（象限图）

- 关键字：`quadrantChart`。
- 语法：`title`、`x-axis <text> --> <text>`（可只写左侧）、`y-axis <text> --> <text>`、`quadrant-1..4 <text>`、点 `<text>: [x, y]`。
- 点坐标 x/y 范围：0–1。quadrant-1 右上、quadrant-2 左上、quadrant-3 左下、quadrant-4 右下。
- 布局说明：有点时 x 轴标签渲染在象限左侧及图表底部，y 轴标签在象限底部，象限文本在象限顶部；无点时轴文本与象限位于象限中心。
- 配置参数表：`chartWidth`(500)、`chartHeight`(500)、`titlePadding`(10)、`titleFontSize`(20)、`quadrantPadding`(5)、`quadrantTextTopPadding`(5)、`quadrantLabelFontSize`(16)、`quadrantInternalBorderStrokeWidth`(1)、`quadrantExternalBorderStrokeWidth`(2)、`xAxisLabelPadding`(5)、`xAxisLabelFontSize`(16)、`xAxisPosition`(top)、`yAxisLabelPadding`(5)、`yAxisLabelFontSize`(16)、`yAxisPosition`(left)、`pointTextPadding`(5)、`pointLabelFontSize`(12)、`pointRadius`(5)。
- 主题变量：`quadrant1Fill`–`quadrant4Fill`、`quadrant1TextFill`–`quadrant4TextFill`、`quadrantPointFill`、`quadrantPointTextFill`、`quadrantXAxisTextFill`、`quadrantYAxisTextFill`、`quadrantInternalBorderStrokeFill`、`quadrantExternalBorderStrokeFill`、`quadrantTitleFill`。
- 点样式可用属性：`color`、`radius`、`stroke-width`、`stroke-color`；优先级：直接样式 > 类样式 > 主题样式。

---

## 13. Gitgraph（Git 图）

- 关键字：`gitGraph`。
- 支持命令：`commit`、`branch`、`checkout`（与 `switch` 可互换）、`merge`。
- 默认主分支 `main`（初始为当前分支）。
- `commit` 属性：`id: "..."`（自定义 ID）、`type: NORMAL/REVERSE/HIGHLIGHT`（默认 NORMAL）、`tag: "..."`。
- `branch 名称`：创建并切换；名称与关键字冲突需加引号。
- `checkout 名称`：切换已有分支；找不到报错。
- `merge 名称`：合并到当前分支，产生 merge commit（实心双圆）；可带 `id`/`tag`/`type` 属性。
- `cherry-pick id: "..."`：从其他分支挑选提交；规则：须提供存在的提交 ID、被挑提交须在不同分支、当前分支须至少有一个提交、挑 merge commit 须提供父提交 ID 且必须为其直接父提交。
- 配置选项：`showBranches`(true)、`showCommitLabel`(true)、`mainBranchName`(main)、`mainBranchOrder`(0)、`parallelCommits`(false)、`rotateCommitLabel`(true)。
- 方向（Orientation）：`LR:`（默认，左右）、`TB:`（上下）、`BT:`（下上，v11.0.0+）。
- 并行提交（v10.8.0+）：`parallelCommits: true`。
- 主题变量：`git0`–`git7`（分支颜色，最多 8 个分支，循环复用）、`gitBranchLabel0`–`gitBranchLabel7`、`commitLabelColor`/`commitLabelBackground`/`commitLabelFontSize`、`tagLabelFontSize`/`tagLabelColor`/`tagLabelBackground`/`tagLabelBorder`、`gitInv0`–`gitInv7`（高亮提交颜色）。
- 主题：`base`、`forest`、`dark`、`default`、`neutral`。

---

## 14. Requirement diagram（需求图）

- 关键字：`requirementDiagram`（需求类型为 `requirement`）。建模规格遵循 SysML v1.6。
- 三种组件：requirement（需求）、element（元素）、relationship（关系）。
- Requirement 定义：`<type> 名称 { id: ...; text: ...; risk: <风险>; verifymethod: <方法> }`。
  - Type 枚举：`requirement`、`functionalRequirement`、`interfaceRequirement`、`performanceRequirement`、`physicalRequirement`、`designConstraint`。
  - Risk 枚举：`Low`、`Medium`、`High`。
  - VerificationMethod 枚举：`Analysis`、`Inspection`、`Test`、`Demonstration`。
- Element 定义：`element 名称 { type: ...; docref: ... }`。
- 文本可加引号并使用 Markdown（如 `"**bold** and *italics*"`）。
- Relationship：`{源} - <类型> -> {目标}` 或反向；类型为 `contains`、`copies`、`derives`、`satisfies`、`verifies`、`refines`、`traces`。
- 方向：`direction`，`TB`(默认)/`BT`/`LR`/`RL`。
- 样式：`style`、`classDef`、`:::`；`classDef default` 应用到所有节点。

---

## 15. Mindmap（思维导图）

- 实验性图表（语法稳定，除图标集成外）。
- 关键字：`mindmap`；依赖缩进定义层级。
- 形状：Square、Rounded square、Circle、Bang、Cloud、Hexagon、Default（与 flowchart 形状语法相近）。
- 图标：`::icon()` 语法（图标字体需由站点管理员/集成者注册）。
- 类（CSS classes）：`:::` 后跟多个以空格分隔的 css 类（类需站点管理员提供）。
- 缩进不明确时的处理：Mermaid 依据「第一个更小缩进的父节点」规则选择父级。
- Markdown Strings：支持粗体/斜体与自动换行。
- 布局：支持 `layout: tidy-tree`（Tidy Tree 布局）。
- 集成：v9.4.0 起内置，采用懒加载/异步渲染；旧版需 `import mindmap ... registerExternalDiagrams`。

---

## 16. Block（块图）

- 关键字：`block`。
- 核心特点：给作者完全控制形状位置（不同于 flowchart 的自动布局）。
- 简单块：连续文本标签即生成水平排列的块。
- 列控制：可指定列数，块按列换行。
- 块宽度：可跨多列（设置宽度）。
- 复合块：块内嵌套块。
- 列宽动态：按该列最宽块调整。
- 形状：圆角、体育场形、子程序形、圆柱形、圆形、不对称、菱形、六边形、平行四边形、梯形、双圆，以及块箭头和 space 块（`space` 占用列，`space:num` 指定占用 n 列）。
- 连接：基本箭头 `A --> B`（注意与 `A - B` 错误的区别，块间距需留空格）；连线可带文本；可加样式。
- 样式：`style` 关键字、类（`classDef`）。
- 注释：`%%`。

---

## 17. C4 架构图（C4）

- 实验性图表；语法与 PlantUML 的 C4-PlantUML 兼容。
- 支持 5 种 C4 图表类型：`C4Context`（系统上下文）、`C4Container`（容器）、`C4Component`（组件）、`C4Dynamic`（动态）、`C4Deployment`（部署）。
- 元素/关系常用宏：`Person`、`Person_Ext`、`System`、`System_Ext`、`SystemDb`、`SystemQueue`、`Container`、`ContainerDb`、`ContainerQueue`、`Component`、`Deployment_Node`/`Node`、`Rel`、`BiRel`、`Rel_L/R/U/D`、`Rel_Back`、`RelIndex`、`Boundary`、`Enterprise_Boundary`、`System_Boundary`、`Container_Boundary`。
- 固定样式（固定 css 颜色），不同皮肤下不提供不同 css。
- 布局不使用全自动布局算法，靠调整语句书写顺序控制位置；不支持 Layout 语句（`Lay_U` 等）。
- 样式更新：`UpdateElementStyle`、`UpdateRelStyle`（可带 `offsetX`/`offsetY` 偏移文本）、`UpdateLayoutConfig`（更新 `c4ShapeInRow`=4、`c4BoundaryInRow`=2）。
- 参数可命名赋值（名称以 `$` 开头）或按顺序赋值。
- 未完成功能（短期不支持）：sprite、tags、link、Legend、自定义标签/型版支持等。

---

## 18. Zenuml

- 关键字：`zenuml`；语法与 Mermaid 原生时序图不同。
- Participant：可隐式声明/显式排序；`annotator` 可用符号替代矩形；参与者可设别名。
- 消息类型：同步（sync）、异步（async）、创建（`new` 关键字）、回复（reply，三种写法，`@return` 用于返回上一层）。
- 嵌套：同步/创建消息可用 `{}` 嵌套。
- 注释：`// comment`（渲染在消息/片段上方，其他位置忽略），支持 Markdown。
- 循环：`while`、`for`、`forEach`/`foreach`、`loop`。
- 条件：`if ... else if ... else ...`；`opt` 片段；`par` 并行；`try ... catch ... finally ...`（异常/中断）。
- 集成：实验性懒加载/异步渲染；早期需 `import zenuml ... registerExternalDiagrams`。

---

## 19. 配置（Configuration）

- 配置来源（3 个）：默认配置、站点级 `initialize` 覆盖（siteConfig）、图前 frontmatter（v10.5.0+，仅覆盖选定参数）；directives（图内指令）已被 frontmatter 取代（弃用）。
- render config 是最终用于渲染的配置。
- `mermaid.initialize(config)`：站内集成者在站点级覆盖默认配置，**只调用一次**。
- `mermaid.configApi.reset`：将某图配置重置为站点级配置；每次渲染前都会被调用。
- 常用初始化示例：`mermaid.initialize({ startOnLoad: true, theme: 'base', securityLevel: 'loose' })`。
- frontmatter 用图顶部 YAML 块（`---config: ...---`）覆盖（除 secure 配置外几乎所有配置）。
- 主题名（5 个内置）：`default`、`neutral`、`dark`、`forest`、`base`。
- 安全级别 `securityLevel` 取值：`strict`、`loose`、`antiscript`、`sandbox`（第三方 Edge 工具印证，默认 `strict`）。`strict` 下禁用 click 交互。
- 渲染器：flowchart 默认 `dagre`，可选 `elk`（v9.4+，实验性）。

---

## 20. 主题（Theming）

- 动态、集成式主题配置从 Mermaid **v8.7.0** 引入。
- 站点级用 `initialize` 配置；单图用 frontmatter 配置。
- 内置主题（5 个）：
  - `default`：所有图的默认主题。
  - `neutral`：适合黑白/打印文档。
  - `dark`：适合深色元素/深色模式；需结合 `darkMode: true`（dark 主题改的是 schema 本身，darkMode 设背景）。
  - `forest`：绿色系。
  - `base`：唯一可修改的主题，作为自定义的基础。
- 可用 frontmatter 的 `themeVariables` 自定义主题（仅 `base` 主题可修改）。
- 颜色计算：部分变量默认值由其他变量推导（如 `primaryBorderColor` 由 `primaryColor` 推导，会做反色/色调变化/加减 10% 等调整）。
- 主题引擎只识别十六进制颜色（如 `#ff0000`），不识别颜色名（如 `red`）。
- 常用主题变量及默认值：`darkMode`(false)、`background`(#f4f4f4)、`fontFamily`(trebuchet ms, verdana, arial)、`fontSize`(16px)、`primaryColor`(#fff4dd)、`primaryTextColor`(由 darkMode 推导)、`secondaryColor`、`primaryBorderColor`、`noteBkgColor`(#fff5ad)、`noteTextColor`(#333)、`noteBorderColor`、`lineColor`、`textColor`、`mainBkg`、`errorBkgColor`、`errorTextColor`。
- 专项变量：Flowchart（`nodeBorder`、`clusterBkg`、`clusterBorder`、`defaultLinkColor`、`titleColor`、`edgeLabelBackground`、`nodeTextColor`）；Sequence（`actorBkg`、`actorBorder`、`actorTextColor`、`actorLineColor`、`signalColor`、`signalTextColor`、`labelBoxBkgColor`、`labelBoxBorderColor`、`labelTextColor`、`loopTextColor`、`activationBorderColor`、`activationBkgColor`、`sequenceNumberColor`）；Pie（`pie1`–`pie12`、`pieTitleTextSize`、`pieSectionTextSize`、`pieLegendTextSize`、`pieStrokeColor`、`pieStrokeWidth`、`pieOpacity`）；State（`labelColor`、`altBackground`）；Class（`classText`）；Journey（`fillType0`–`fillType7`）。

---

## 21. 集成（Integration）

### mermaid-cli
- 官方文档页（`/config/mermaidCLI.html`）已声明：mermaid CLI **已迁移到独立仓库** `https://github.com/mermaid-js/mermaid-cli`，请阅读其文档。
- 安装（第三方/社区印证）：`npm install -g @mermaid-js/mermaid-cli`；命令为 `mmdc`。
- 典型用法：`mmdc -i input.mmd -o output.png`（可指定宽度 `-w 1200`）；也用于将 `.mmd` 文件转换为 PNG 等图片资产，便于 CI 集成。
- 配置文件为 JSON 格式，可配置主题、字体、日志级别等（如 `{ "theme": "forest", "logLevel": "info" }`）。

### mermaid.live 在线编辑器
- 官方线上实时编辑器（`https://mermaid.live/`，仓库 `mermaid-js/mermaid-live-editor`）。
- 功能（intro 及社区印证）：左侧写代码、右侧实时渲染；图表数据在浏览器端处理；支持导出 PNG、SVG、可分享链接等。
- 官方文档 intro 页提到入门可通过 Mermaid Live Editor 创建图表，并提供视频教程（Ecosystem/Tutorials）。

### 渲染器/CDN 支持
- 图表默认渲染为 **SVG**（Gantt 可渲染为 SVG、PNG 或 Markdown 链接）。
- CDN：`https://cdn.jsdelivr.net/npm/mermaid@<version>/dist/`；ESM 入口 `mermaid.esm.min.mjs`。
- 布局渲染器：dagre（默认）、elk（可选，实验性）。

---

## 22. 版本信息

- 官方 CDN 推荐的当前大版本为 **v11**（`https://cdn.jsdelivr.net/npm/mermaid@11`）；intro 页大量示例使用 `mermaid@11`。
- 社区/工具印证（2026 年）：Mermaid **v11 为当前稳定版本**，以 ES module 分发；第三方工具默认集成版本如 `mermaid@11.14.0`（Mermaid Studio 2026.2.2 默认引擎）、`11.15.0`（某插件固定默认）。
- 各功能版本标注汇总（来自各文档页）：
  - `v8.7.0`：动态主题配置引入。
  - `v9.4`：elk 渲染器引入；mindmap 内置（更早的 9.3 需手动注册外部图）。
  - `v10.3.0`：sankey 引入；gitgraph 方向（LR/TB）、actor 创建/销毁、gantt tickInterval。
  - `v10.5.0`：frontmatter 配置引入（取代 directives）。
  - `v10.7.0`：修复 actor 创建/删除错误所需版本。
  - `v10.8.0`：gitgraph 并行提交。
  - `v10.9.0`：gantt `until` 关键字。
  - `v11.0.0`：时序图双向箭头；gantt `weekend`；gitgraph `BT` 方向。
  - `v11.3.0`：flowchart 30 个新形状、icon/image 特殊形状。
  - `v11.7.0`：fontawesome 图标包注册。
  - `v11.10.0`：flowchart 边级曲线样式（edge ID）。
  - `v11.12.3`：时序图半箭头、中央连接。
  - `v11.14.0`：timeline 方向（LR/TD）。
  - `v11.15.0`：classDiagram 命名空间标签/嵌套；sankey labelStyle/nodeWidth/nodePadding/nodeColors；时序图 autonumber 起始/增量。
  - `v11.16.0`：pie donutHole/legendPosition/highlightSlice；ER 可空属性类型后缀 `?`、属性 key/注释。

---

## 附：采集说明

- 任务清单中的域名 `https://mermaid.ai/` 无法访问（WebFetch 失败），官方文档实际域名为 `https://mermaid.js.org/`。
- 官方文档现行路径与任务清单不同：语法页为 `/syntax/<名称>.html`（如 `stateDiagram.html` 而非 `stateDiagram-v2.html`、`entityRelationshipDiagram.html` 而非 `erDiagram`）；mermaid-cli 文档已迁移至 `github.com/mermaid-js/mermaid-cli`（原 `/config/mermaidCLI.html` 仅作跳转说明）。
- `mermaid-live-editor` 在 `mermaid.js.org` 下无独立文档页（404），其功能依据官方 intro 页、官方仓库及社区资料补充。
- 部分绘制代码示例（mermaid 代码块内容）在提取过程中被文档渲染器省略，本文件仅记录官方文档中以文字/表格形式明确给出的语法关键字、参数与说明。