---
id: "myst-tutorial-directives-roles"
title: "第4章：高级功能 - Directives 和 Roles"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/myst-markdown-tutorial/04-advanced-directives-roles.toml"
---
# 第4章：高级功能 - Directives 和 Roles

Directives（指令）和 Roles（角色）是 MyST 扩展 Markdown 表达能力的两大核心机制。理解这两个概念是掌握 MyST 的关键。

深度参考：[ExecutableBooks MyST 语法指南](../executablebooks-myst-guide/01-myst-syntax.md)

---

## 4.1 Directives（块级扩展）

### 4.1.1 什么是 Directives

Directives 是 **多行块级容器**，用于插入标准 Markdown 无法表达的复杂内容：提示框、图片增强、表格、代码块、图表、数学公式等。它们是 MyST 强大扩展能力的基石。

---

### 4.1.2 两种围栏语法

MyST 提供两种围栏语法，分别适用于不同场景：

#### 1. 冒号围栏 `:::`（推荐用于 Markdown 内容）

用于包含 Markdown 格式内容的指令（如提示框、折叠面板等）：

````markdown
:::{note}
这是一个 **提示框**，内容支持 *Markdown* 格式。
- 支持列表
- 支持链接
:::
````

:::{note}
这是一个 **提示框**，内容支持 *Markdown* 格式。
- 支持列表
- 支持链接
:::

#### 2. 反引号围栏 ```` ``` ````（推荐用于代码/公式）

用于包含代码、数学公式等纯文本内容的指令：

`````markdown
````{code-block} python
def hello():
    print("Hello, MyST!")
````
`````

:::{tip}
记忆技巧：**Markdown 内容用冒号，代码/公式用反引号**。两种语法功能等价。
:::

---

### 4.1.3 Directive 完整结构

一个标准 Directive 由五部分组成：

```
围栏标记  {directivename}  参数1 参数2
:option1: value1
:option2: value2
---
内容区域
围栏结束标记
```

- **围栏标记**：`:::` 或 ```，数量可嵌套增加
- **`{directivename}`**：指令标识符，大括号包裹
- **参数**：紧跟指令名的位置参数（可选）
- **选项**：控制指令行为的键值对（可选）
- **内容**：指令包裹的主体内容（可选）

最简示例：
```markdown
:::{note}
简单提示框
:::
```

带参数示例（`image` 指令的参数是图片路径）：
````markdown
```{image} images/diagram.png
:alt: 架构图
:width: 500px
```
````

---

### 4.1.4 选项的三种写法

#### 1. 短格式 `:key: value`

最常用，适用于少量选项：
````markdown
```{image} photo.jpg
:alt: 示例图片
:width: 400px
:align: center
```
````

#### 2. YAML 块格式 `---`

适用于多个选项或复杂值，更清晰：
````markdown
:::{figure} chart.png
---
alt: 销售数据图表
width: 70%
align: center
---
这是图注，支持 **Markdown**。
:::
````

:::{tip}
选项超过3个时推荐使用 YAML 格式，可读性更好。
:::

#### 3. 内联选项（类CSS写法）

适用于简单的类名、ID、键值对：
```markdown
:::{div} .my-class #my-id key="value"
这是一个带类名和ID的 div 容器。
:::
```

常用内联选项：`.classname`（添加CSS类）、`#idname`（设置元素ID）、`key="value"`（设置属性）。

---

### 4.1.5 嵌套规则

Directives 支持嵌套，关键规则：**每嵌套一层，围栏符号数量 +1**。

#### 冒号嵌套示例

外层4个冒号，内层3个冒号：

`````markdown
::::{warning}
这是外层警告框。

:::{note}
这是嵌套在内层的提示框。
:::

外层内容继续。
::::
`````

::::{warning}
这是外层警告框。

:::{note}
这是嵌套在内层的提示框。
:::

外层内容继续。
::::

#### 代码块嵌套示例

在外层展示指令示例时，需要用更多反引号：

``````markdown
`````markdown
````{note}
这是提示框内部的代码块：
```python
print("嵌套代码")
```
````
`````
``````

:::{warning}
围栏数量从内向外逐层+1，内层结束标记数量必须与开始标记一致。
:::

**层级对应关系**：
- 普通代码块：3个反引号
- 指令包裹代码块：4个反引号
- 文档中展示指令示例：5个反引号

---

## 4.2 Roles（行内扩展）

### 4.2.1 什么是 Roles

Roles 是 **单行内联扩展**，用于在段落文本中插入特殊格式或语义标记，相当于"行内指令"。

语法格式：
```markdown
{rolename}`content`
```

- `{rolename}`：角色名，大括号包裹
- `` `content` ``：反引号包裹的内容

---

### 4.2.2 Roles vs Directives

| 特性 | Directives | Roles |
|------|------------|-------|
| 作用范围 | 块级（多行段落） | 行内（文本流中） |
| 语法 | 围栏包裹 `:::/```` | 单引号包裹 `` {name}`content` `` |
| 内容结构 | 可包含复杂结构 | 通常是单行文本 |
| 类比 | HTML 的 `<div>` 块元素 | HTML 的 `<span>` 行内元素 |

:::{note}
简单判断：影响整段/整块内容用 Directive，只影响几个字词用 Role。
:::

---

### 4.2.3 常用内置 Roles

#### 1. `{abbr}` - 缩写（鼠标悬停显示全称）
```markdown
{abbr}`HTML (HyperText Markup Language)` 是网页的基础语言。
```

#### 2. `{sub}` - 下标（化学式、数学下标）
```markdown
水的化学式是 H{sub}`2`O，二氧化碳是 CO{sub}`2`。
```

#### 3. `{sup}` - 上标（指数、商标）
```markdown
爱因斯坦质能方程：E=mc{sup}`2`
```

#### 4. `{math}` - 行内数学
```markdown
勾股定理：{math}`a^2 + b^2 = c^2`
```

#### 5. `{ref}` - 交叉引用（引用文档内带标签的位置）
```markdown
请参阅 {ref}`myst-tutorial-directives-roles` 了解更多。
```

#### 6. `{eq}` - 公式引用（引用带编号的数学公式，第6章详解）
```markdown
如公式 {eq}`eq-pythagoras` 所示
```

#### 7. `{cite}` - 文献引用（参考文献引用，第7章详解）
```markdown
已有研究表明 {cite}`knuth1984tex`
```

#### 8. `{doc}` - 文档引用（自动使用目标文档标题作为链接文本）
```markdown
详细安装说明见 {doc}`00-quick-start`。
```

#### 9. `{literal}` - 行内代码样式
```markdown
运行 {literal}`myst start` 启动预览服务器。
```

---

## 4.3 小结

Directives 和 Roles 是 MyST 的两大扩展支柱：

- **Directives**（块级）：用围栏语法包裹多行内容，支持参数和选项，用于复杂组件
- **Roles**（行内）：用 `` {name}`content` `` 语法，嵌入文本流中，用于字词级增强

掌握了这两个机制，你就掌握了 MyST 80% 的扩展能力。后续章节将逐一详解各类常用指令和角色。

---

## 导航

[« 上一章：基础语法（下）](03-basic-syntax-part2.md) | [返回目录](README.md) | [下一章：交叉引用 »](05-advanced-cross-references.md)
