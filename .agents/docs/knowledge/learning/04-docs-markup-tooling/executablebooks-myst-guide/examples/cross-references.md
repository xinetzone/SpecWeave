---
source: "https://mystmd.org/guide/cross-references"
x-toml-ref: "../../../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/executablebooks-myst-guide/examples/cross-references.toml"
id: "examples-cross-references"
title: "交叉引用示例"
---
# 交叉引用示例

本示例演示如何使用 label 和 ref 进行交叉引用。交叉引用是学术文档和技术文档中的重要功能，可以方便地引用文档中的章节、图表、表格等元素。

> **注意**：这是语法演示文档，标签引用需要在真实的 MyST 项目环境中才能正确解析和显示编号。在普通 Markdown 查看器中，引用可能不会显示为链接或编号。

## 为元素添加标签（Label）

使用 `(label)=` 语法可以为章节、图表、表格等元素添加标签，标签名称在整个文档中必须唯一。

### 章节标签

在标题前添加标签：

```
(my-chapter)=
## 这是一个带标签的章节

这个章节可以通过标签被其他位置引用。
```

渲染效果（语法演示）：

(my-chapter)=
### 示例章节：MyST 简介

MyST（Markedly Structured Text）是一种功能强大的 Markdown 扩展格式，专为科学出版和技术文档设计。

---

## 使用 {ref} 引用章节

`{ref}` role 用于通过标签引用文档中的元素，渲染时会自动生成链接并显示元素的标题文本。

### 基本用法

```
请参阅 {ref}`my-chapter` 了解更多信息。
```

渲染效果（语法演示）：

请参阅 {ref}`my-chapter` 了解更多信息。

### 自定义链接文本

你也可以为引用指定自定义的显示文本，而不是使用元素的原始标题：

```
请参阅 {ref}`这里 <my-chapter>` 了解更多信息。
```

渲染效果（语法演示）：

请参阅 {ref}`这里 <my-chapter>` 了解更多信息。

---

(my-intro-section)=
## 被引用的示例章节

这是一个用于演示引用效果的示例章节。在实际文档中，当其他位置使用 {ref}`my-intro-section` 引用这里时，会自动生成指向本章节的链接。

---

## 使用 {numref} 引用带编号的元素

`{numref}` role 用于引用带自动编号的元素，如图表、表格、代码块等，渲染时会显示自动生成的编号（如"图 1"、"表 2"等）。

### 为图片添加标签和引用

使用 `{figure}` directive 插入图片并添加标签：

````
(my-figure)=
:::{figure} https://example.com/image.png
:width: 80%
:align: center

这是图片的说明文字（caption）
:::
````

使用 {numref} 引用图片：

```
如 {numref}`my-figure` 所示，系统架构包含三个核心模块。
```

自定义编号显示格式：

```
{numref}`图 %s <my-figure>` 展示了系统的整体架构。
```

渲染效果（语法演示）：

(my-figure-demo)=
:::{note}
📊 **图片示例位置**（此处为演示，实际使用时替换为 figure directive）
:::

引用示例：
- 自动格式：如 {numref}`my-figure-demo` 所示
- 自定义格式：{numref}`图 %s <my-figure-demo>` 展示了相关内容

---

### 为表格添加标签和引用

为表格添加标签并引用：

````
(my-table)=
:::{list-table} 示例表格
:header-rows: 1
:align: center

* - 功能
  - 说明
* - 交叉引用
  - 自动编号和链接
* - 数学公式
  - LaTeX 语法支持
* - Admonitions
  - 多种提示框样式
:::
````

引用表格：

```
详细对比见 {numref}`my-table`。
```

渲染效果（语法演示）：

(my-table-demo)=
:::{list-table} MyST 核心功能
:header-rows: 1
:align: center

* - 功能
  - 说明
* - 交叉引用
  - 自动编号和链接
* - 数学公式
  - LaTeX 语法支持
* - Admonitions
  - 多种提示框样式
* - Roles
  - 行内内容扩展
:::

引用示例：详细功能对比见 {numref}`my-table-demo`。

---

(my-code-block)=
### 为代码块添加标签和引用

代码块也可以添加标签并被引用：

````
(my-code-block)=
:::{code-block} python
:linenos:

def hello():
    print("Hello, MyST!")
:::
````

引用代码块：

```
示例代码见 {numref}`my-code-block`。
```

---

## 引用语法总结

### 添加标签的方式

| 元素类型 | 标签语法示例 |
|---|---|
| 章节/标题 | `(label)=` 紧跟在标题前一行 |
| 图片（figure） | 在 `:::{figure}` 块前一行添加 `(label)=` |
| 表格 | 在表格 directive 前一行添加 `(label)=` |
| 代码块 | 在 code-block directive 前一行添加 `(label)=` |

### 引用方式对比

| Role | 用途 | 显示效果示例 |
|---|---|---|
| `{ref}` | 引用章节等无编号元素 | 显示标题文本并生成链接 |
| `{numref}` | 引用图表、表格等带编号元素 | 显示"图 1"、"表 2"等编号并生成链接 |

### 引用语法格式

```
{ref}`label`                          使用目标元素的原始文本作为链接文本
{ref}`自定义文本 <label>`             使用自定义文本作为链接文本
{numref}`label`                       使用自动编号格式（如"Figure 1"）
{numref}`图 %s <label>`               自定义编号格式，%s 会被替换为编号
```

---

(my-usage-notes)=
## 使用注意事项

1. **标签唯一性**：标签名称在整个文档项目中必须唯一，避免重复定义
2. **标签命名规范**：建议使用小写字母、数字和连字符（如 `my-chapter`、`figure-1`），不要使用空格或特殊字符
3. **引用范围**：标签可以跨文档引用（在多文档项目中），但需要确保文档在同一项目中
4. **编译依赖**：交叉引用需要 MyST 构建工具（mystmd）处理才能正确解析，普通 Markdown 编辑器不会处理这些引用

:::{tip}
良好的交叉引用可以大大提升文档的可读性和导航体验，让读者能够快速跳转到相关内容。在编写长篇技术文档或学术论文时，建议充分利用交叉引用功能。
:::
