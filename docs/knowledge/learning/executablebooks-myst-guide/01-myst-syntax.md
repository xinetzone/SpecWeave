+++
title = "MyST Markdown 核心语法"
source = "https://mystmd.org/guide/syntax-overview, https://mystmd.org/guide/directives, https://mystmd.org/guide/roles"
+++

# MyST Markdown 核心语法

## 1. 概述

MyST（Markedly Structured Text）是 CommonMark Markdown 的超集，在完全兼容标准 Markdown 语法的基础上，引入了来自 reStructuredText/Sphinx 生态的两大核心扩展机制：

- **Directives（指令）**：块级扩展容器，用于插入提示框、图片、代码块、表格、图表等多行内容
- **Roles（角色）**：行内扩展，用于在行内插入缩写、上下标、数学公式、交叉引用等单行内容

这两种机制使 MyST 既保持了 Markdown 的简洁易写，又具备了科学出版级别的表达能力。所有标准 Markdown 语法在 MyST 中均可正常使用。

---

## 2. Directives（块级扩展）详解

### 2.1 什么是 Directives

Directives 是 MyST 的多行块级容器，一个完整的 Directive 包含四个组成部分：

1. **围栏标记**：`:::` 或 ```` ``` ```` 包裹
2. **标识符**：`{directivename}` 指定指令类型
3. **参数**：紧跟在标识符后面的词（可选）
4. **选项**：键值对配置（可选）
5. **内容**：指令的主体内容（可选）

基本结构示意：

````
```{directivename} 参数
:key1: value1
:key2: value2

这是指令的内容部分...
```
````

### 2.2 两种围栏语法

MyST 提供两种围栏语法，适用于不同场景：

#### 冒号围栏（`:::`）

用于包含 Markdown 内容的指令（如 admonitions、theorems、卡片等），优点是在非 MyST 渲染器中有更好的降级显示效果。

**示例 - note 提示框：**

```
:::{note}
这是一个使用冒号围栏的提示框。
在普通 Markdown 阅读器中，这部分内容也能以文本形式正常显示。
:::
```

渲染效果：

:::{note}
这是一个使用冒号围栏的提示框。
在普通 Markdown 阅读器中，这部分内容也能以文本形式正常显示。
:::

#### 反引号围栏（```` ``` ````）

用于包含代码类内容的指令（如 math、diagrams、literal code blocks），可以防止内容被自动格式化工具误处理。

**示例 - math 数学公式块：**

````
```{math}
:label: euler-equation
e^{i\pi} + 1 = 0
```
````

渲染效果：

```{math}
:label: euler-equation
e^{i\pi} + 1 = 0
```

> **选择建议**：内容是 Markdown 文本用 `:::`，内容是代码/公式/图表用 ```` ``` ````。

### 2.3 Directive 参数

参数是紧跟在 `{directivename}` 后面的词，作为指令的主要输入。

**示例 - figure 指令带图片路径参数：**

````
```{figure} https://example.com/image.png
---
align: center
width: 80%
---
图片标题说明
```
````

**示例 - code-block 指令带语言参数：**

````
```{code-block} python
def hello():
    print("Hello, MyST!")
```
````

### 2.4 Directive 选项的三种写法

#### 写法一：`:key: value` 键值对格式

适用于只有 1-2 个选项的简单场景，简洁直观。

**示例：**

````
```{image} image.png
:align: center
:width: 300px
```
````

#### 写法二：`---` YAML 块格式

适用于多个选项或选项值包含多行的场景，YAML 语法支持更复杂的数据结构。

**示例：**

````
```{figure} https://example.com/chart.png
---
align: center
width: 90%
height: 400px
name: my-figure
figclass: margin-caption
---
这是图表的标题说明，可以包含多行文本。
```
````

#### 写法三：内联选项格式

在大括号内直接使用 `.class`、`#label`、`key="value"` 形式，适用于简单的样式和标识设置。

**示例：**

```
:::{note} .important #note-1
这是一个带有自定义类和标签的提示框。
:::
```

**示例 - 组合使用：**

````
```{code-block} python .linenos #code-example lineno-start=10 emphasize-lines="2,3"
def greet(name):
    message = f"Hello, {name}!"
    print(message)
    return message
```
````

内联选项支持的语法：
- `.classname`：添加 CSS 类
- `#label`：设置标签用于交叉引用
- `key="value"`：设置任意选项键值

---

## 3. Roles（行内扩展）详解

### 3.1 什么是 Roles

Roles 是 MyST 的单行内联扩展机制，语法格式为：

```
{rolename}`content`
```

与 Directives 不同，Roles 只在文本行内使用，用于插入特殊格式或语义标记。

### 3.2 Roles 基础示例

**缩写示例 - abbr：**

```
{abbr}`MyST (Markedly Structured Text)` 是一种强大的 Markdown 超集。
```

渲染效果：鼠标悬停在 "MyST" 上会显示全称提示。

**下标示例 - sub：**

```
水的化学式是 H{sub}`2`O，二氧化碳是 CO{sub}`2`。
```

渲染效果：水的化学式是 H{sub}`2`O，二氧化碳是 CO{sub}`2`。

**上标示例 - sup：**

```
爱因斯坦质能方程 E = mc{sup}`2`，2{sup}`10` = 1024。
```

渲染效果：爱因斯坦质能方程 E = mc{sup}`2`，2{sup}`10` = 1024。

**行内数学示例 - math：**

```
勾股定理可以表示为 {math}`a^2 + b^2 = c^2`。
```

渲染效果：勾股定理可以表示为 {math}`a^2 + b^2 = c^2`。

### 3.3 常见 Roles 列表

| Role | 用途 | 示例 |
|---|---|---|
| `abbr` | 缩写（带全称提示） | `{abbr}`HTML (HyperText Markup Language)`` |
| `sub` | 下标 | `H{sub}`2``O` |
| `sup` | 上标 | `x{sup}`2`` + y{sup}`2`` |
| `math` | 行内数学公式 | `{math}`\sum_{i=1}^n i`` |
| `ref` | 交叉引用（带标题） | `{ref}`my-figure`` |
| `eq` | 公式引用 | `见公式 {eq}`euler-equation`` |
| `cite` | 文献引用 | `{cite}`holdgraf2014`` |
| `doc` | 文档引用 | `{doc}`../intro`` |
| `download` | 下载链接 | `{download}`data.csv`` |
| `link` | 外部链接 | `{link}`https://example.com`` |
| `emphasis` | 强调（斜体） | `{emphasis}`重要内容`` |
| `strong` | 加粗 | `{strong}`警告`` |
| `literal` | 行内代码样式 | `{literal}`print()`` |

### 3.4 Roles 内联选项

Roles 也支持内联选项，语法与 Directives 类似：

```
{span #my-id .highlight style="color: red"}`这是自定义样式的文本`
```

**示例 - 带标签的文本：**

```
这是一段普通文本，{span #target-point .important data-value="42"}`这部分文本带有标识符和类`，可以被其他地方引用。
```

---

## 4. 嵌套内容块规则

### 4.1 嵌套原理

MyST 通过增加围栏符号（反引号或冒号）的数量来实现内容块的嵌套。外层围栏的符号数量必须多于内层，以确保解析器能够正确识别边界。

### 4.2 嵌套 Admonitions 示例

使用不同数量的冒号来嵌套提示框：

```
:::::{important}
这是外层重要提示框的内容。

::::{note}
这是嵌套在内部的 note 提示框。

:::{tip}
这是更内层的小提示！
:::
::::
:::::
```

渲染效果：

:::::{important}
这是外层重要提示框的内容。

::::{note}
这是嵌套在内部的 note 提示框。

:::{tip}
这是更内层的小提示！
:::
::::
:::::

### 4.3 代码块嵌套技巧

当需要在代码块示例中展示代码块本身（嵌套代码块）时，使用更多数量的反引号作为外层围栏：

**示例：展示 Markdown 代码块的写法（四个反引号包裹三个反引号）：**

`````
````markdown
```{note}
这是一个提示框
```
````
`````

渲染效果：展示的代码块示例中正确显示了三个反引号的围栏。

**示例：三层嵌套代码块（五个反引号包裹四个反引号包裹三个反引号）：**

``````
`````markdown
````
```{python}
print("Hello!")
```
````
`````
``````

### 4.4 嵌套最佳实践

1. **逐层递增**：每嵌套一层，围栏符号数量至少增加 1 个
2. **保持对称**：开始围栏和结束围栏的符号数量必须一致
3. **清晰缩进**：适当缩进可以让嵌套结构更易读（虽然 MyST 不强制要求）
4. **混合使用**：冒号围栏和反引号围栏可以混合嵌套（外层 `:::` 包裹内层 ```` ``` ```` 或反之）

**混合嵌套示例：**

````
:::{card} 卡片标题
卡片内容...

```{code-block} python
print("卡片中的代码块")
```
:::
````

---

## 5. 常用 Directives 速查表

| 类别 | Directive | 用途 | 基本示例 |
|---|---|---|---|
| **提示框类** | `note` | 信息提示 | `:::{note}` 内容 `:::` |
| | `warning` | 警告提示 | `:::{warning}` 警告内容 `:::` |
| | `tip` | 小技巧/建议 | `:::{tip}` 技巧内容 `:::` |
| | `important` | 重要提示 | `:::{important}` 重要内容 `:::` |
| | `caution` | 注意事项 | `:::{caution}` 注意内容 `:::` |
| | `seealso` | 另见参考 | `:::{seealso}` 参考链接 `:::` |
| **图片类** | `figure` | 带标题的图片（支持编号引用） | ```{figure} path/to/img.png --- align: center --- 标题 ``` |
| | `image` | 简单图片 | ````{image} path/to/img.png :align: center ````` |
| **代码类** | `code-block` | 带语法高亮的代码块 | ```{code-block} python def f(): pass ``` |
| | `code` | 代码块别名（同 code-block） | 同上 |
| **数学类** | `math` | 块级数学公式（支持标签引用） | ```{math} :label: eq1 a^2 + b^2 = c^2 ``` |
| **表格类** | `table` | 表格容器 | `:::{table}` 标题 --- Markdown表格 `:::` |
| | `list-table` | 列表格式定义表格 | ```{list-table} 标题 --- * - 单元格1 - 单元格2 ``` |
| **导航类** | `toc` | 目录树 | ```{toc} :maxdepth: 2 ``` |
| **包含类** | `include` | 包含其他文件内容 | ```{include} relative/path.md ``` |
| **UI组件类** | `dropdown` | 可折叠下拉内容 | `:::{dropdown}` 标题 :open: 折叠内容 `:::` |
| | `card` | 卡片容器 | `:::{card}` 标题 卡片内容 `:::` |
| | `tab-set` | 标签页组 | `:::{tab-set}` :::{tab-item} 标签1 内容 ::: `:::` |

---

## 6. 常用 Roles 速查表

| 类别 | Role | 用途 | 示例 |
|---|---|---|---|
| **格式类** | `abbr` | 缩写（悬停显示全称） | `{abbr}`MyST (Markedly Structured Text)`` |
| | `sub` | 下标 | `H{sub}`2``O` |
| | `sup` | 上标 | `x{sup}`2`` |
| | `emphasis` | 强调（斜体） | `{emphasis}`重点内容`` |
| | `strong` | 加粗强调 | `{strong}`警告`` |
| | `literal` | 行内代码样式 | `{literal}`variable_name`` |
| **数学类** | `math` | 行内数学公式 | `{math}`\alpha + \beta`` |
| | `eq` | 公式引用 | `{eq}`euler-equation`` |
| **引用类** | `ref` | 交叉引用（自动获取标题） | `{ref}`my-section`` |
| | `numref` | 带编号的引用（如图1、表2） | `{numref}`my-figure`` |
| | `doc` | 引用其他文档 | `{doc}`./other-doc`` |
| | `cite` | 文献引用 | `{cite}`author2024`` |
| | `cite:t` | 文本式引用（作者在行文内） | `如 {cite:t}`knuth1984`` 所述` |
| **链接类** | `download` | 文件下载链接 | `{download}`report.pdf`` |
| | `link` | 外部超链接 | `{link}`https://mystmd.org`` |

---

## 参考资料

- MyST 语法概览：https://mystmd.org/guide/syntax-overview
- Directives 详细文档：https://mystmd.org/guide/directives
- Roles 详细文档：https://mystmd.org/guide/roles
