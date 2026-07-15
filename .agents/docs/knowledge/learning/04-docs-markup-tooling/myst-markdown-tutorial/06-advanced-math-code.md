---
id: "myst-tutorial-math-code"
title: "第6章：高级功能 - 数学公式与代码块"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/myst-markdown-tutorial/06-advanced-math-code.toml"
---
# 第6章：高级功能 - 数学公式与代码块

数学公式和代码块是技术文档与学术写作的两大核心要素。MyST 提供了出版级的 LaTeX 数学支持和增强型代码块功能，同时解决了 Markdown 中代码块嵌套展示的经典难题。

## 6.1 数学公式

MyST 完整支持 LaTeX 数学语法，提供行内公式、块级公式、自动编号、交叉引用等完整数学排版能力。

### 6.1.1 行内公式

行内公式用于在正文中嵌入数学表达式，有两种等价语法：

**语法 1：`{math}` role（推荐，无需扩展）**

```markdown
勾股定理：{math}`a^2 + b^2 = c^2` 是平面几何的基本定理。
```

渲染效果：勾股定理：$a^2 + b^2 = c^2$ 是平面几何的基本定理。

**语法 2：`$...$` 美元符号（需启用 dollarmath 扩展）**

```markdown
勾股定理：$a^2 + b^2 = c^2$ 是平面几何的基本定理。
```

:::{tip}
使用 `$...$` 语法需在 `myst.yml` 中启用 `dollarmath` 扩展：
```yaml
project:
  myst_extensions:
    - dollarmath
```
`{math}` role 是标准语法，无需任何扩展即可使用，兼容性更好。
:::

### 6.1.2 块级公式

独立成段的数学公式使用 `{math}` 指令（三个反引号包裹）：

````markdown
```{math}
E = mc^2
```
````

块级公式支持多个选项：

| 选项 | 说明 |
|------|------|
| `:label: eq-name` | 为公式添加标签，用于交叉引用 |
| `:nowrap:` | 禁止公式自动换行（长公式慎用） |

**带标签和编号的公式示例：**

````markdown
```{math}
:label: eq-einstein

E = mc^2
```
````

添加 `:label:` 后公式自动编号，可通过 `{eq}` role 引用。

### 6.1.3 公式编号与引用

使用 `{eq}` role 引用带标签的公式，自动显示编号：

```markdown
质能方程 {eq}`eq-einstein` 揭示了质量与能量的等价关系。
```

渲染效果：质能方程 (1) 揭示了质量与能量的等价关系。

编号格式可在 `myst.yml` 中自定义（参见第5章）。

### 6.1.4 常用 LaTeX 数学符号速查表

下表列出技术写作中最常用的 25+ 个数学符号：

| 类别 | 符号 | LaTeX 命令 | 示例效果 |
|------|------|-----------|---------|
| **希腊字母** | α β γ δ | `\alpha \beta \gamma \delta` | α β γ δ |
| | ε ζ η θ | `\epsilon \zeta \eta \theta` | ε ζ η θ |
| | λ μ ν π | `\lambda \mu \nu \pi` | λ μ ν π |
| | ρ σ τ φ | `\rho \sigma \tau \phi` | ρ σ τ φ |
| | ω Ω | `\omega \Omega` | ω Ω |
| **上下标** | 上标 | `x^2` | $x^2$ |
| | 下标 | `x_i` | $x_i$ |
| | 组合 | `x_{i}^{2}` | $x_{i}^{2}$ |
| **运算** | 分数 | `\frac{a}{b}` | $\frac{a}{b}$ |
| | 根号 | `\sqrt{x}` | $\sqrt{x}$ |
| | n次根 | `\sqrt[n]{x}` | $\sqrt[n]{x}$ |
| | 求和 | `\sum_{i=1}^{n}` | $\sum_{i=1}^{n}$ |
| | 积分 | `\int_{a}^{b}` | $\int_{a}^{b}$ |
| | 极限 | `\lim_{x \to \infty}` | $\lim_{x \to \infty}$ |
| | 乘积 | `\prod_{i=1}^{n}` | $\prod_{i=1}^{n}$ |
| **关系** | 不等于 | `\neq` | $\neq$ |
| | 约等于 | `\approx` | $\approx$ |
| | 小于等于 | `\leq` | $\leq$ |
| | 大于等于 | `\geq` | $\geq$ |
| | 正比于 | `\propto` | $\propto$ |
| **箭头** | 右箭头 | `\to` / `\rightarrow` | $\to$ |
| | 左箭头 | `\leftarrow` | $\leftarrow$ |
| | 双向箭头 | `\leftrightarrow` | $\leftrightarrow$ |
| | 推出 | `\Rightarrow` | $\Rightarrow$ |
| **矩阵** | 简单矩阵 | `\begin{matrix} a & b \\ c & d \end{matrix}` | $\begin{matrix} a & b \\ c & d \end{matrix}$ |
| | 圆括号矩阵 | `\begin{pmatrix} a & b \\ c & d \end{pmatrix}` | $\begin{pmatrix} a & b \\ c & d \end{pmatrix}$ |

:::{tip}
不需要记忆所有符号，写文档时查表即可。复杂公式建议先在 [Overleaf](https://www.overleaf.com) 或 [KaTeX 官网](https://katex.org/docs/supported.html) 验证语法。
:::

### 6.1.5 align 多公式对齐环境

需要多个公式对齐排列时，使用 LaTeX 的 `align` 环境（`&` 标记对齐位置，`\\` 换行）：

````markdown
```{math}
:label: eq-align-demo

\begin{align}
(x + y)^2 &= x^2 + 2xy + y^2 \\
(x - y)^2 &= x^2 - 2xy + y^2 \\
(x + y)(x - y) &= x^2 - y^2
\end{align}
```
````

注意：`align` 环境中每行公式自动独立编号。如需某行不编号，在该行末尾加 `\nonumber`。

## 6.2 代码块

代码块是技术文档的核心展示内容。MyST 在标准 Markdown 代码块基础上提供了行号、强调、标题、标签等增强功能。

### 6.2.1 标准代码块语法回顾

标准 Markdown 围栏代码块使用三个反引号，后接语言标识：

````markdown
```python
def hello():
    print("Hello, MyST!")
```
````

支持常见语言：`python`、`javascript`、`bash`、`yaml`、`json`、`html`、`css`、`cpp`、`java`、`go`、`rust` 等。

### 6.2.2 `code-block` 指令增强选项

需要行号、代码标题、行强调等增强功能时，使用 `code-block` 指令（而非简单的三个反引号）：

| 选项 | 说明 |
|------|------|
| `:linenos:` | 显示行号 |
| `:emphasize-lines: n,m` | 强调第 n、m 行（高亮显示） |
| `:lineno-start: N` | 行号从 N 开始（显示代码片段时有用） |
| `:caption: "标题文本"` | 添加代码块标题（显示在代码块上方） |
| `:label: code-name` | 添加标签，用于 `{numref}` 引用 |

**综合示例：**

`````markdown
````{code-block} python
:linenos:
:emphasize-lines: 3,5
:lineno-start: 10
:caption: "带行号和强调的代码示例"
:label: code-enhanced-demo

def fibonacci(n):
    """计算斐波那契数列第n项"""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
````
`````

上述示例渲染效果：
- 代码从第 10 行开始编号（而非 1）
- 第 3 行（`if n <= 1:`）和第 5 行（`a, b = 0, 1`）高亮强调
- 代码上方显示标题"带行号和强调的代码示例"
- 可通过标签 `code-enhanced-demo` 引用

### 6.2.3 使用 `{numref}` 引用代码块

带 `:label:` 的代码块可使用 `{numref}` 引用，自动编号：

```markdown
完整实现参见 {numref}`code-enhanced-demo`。
斐波那契算法见 {numref}`代码清单 %s <code-enhanced-demo>`。
```

与图表引用类似，`%s` 是编号占位符，中文文档建议使用"代码清单 %s"格式。

### 6.2.4 行内代码

正文中嵌入短代码片段有两种语法：

**语法 1：反引号（标准 Markdown）**

```markdown
使用 `print()` 函数输出内容，变量通过 `=` 赋值。
```

**语法 2：`{literal}` role**

```markdown
使用 {literal}`print()` 函数输出内容。
```

两种语法效果等价，反引号更简洁，`{literal}` 在某些复杂嵌套场景下更可靠。

## 6.3 代码块嵌套技巧

Markdown 中一个经典难题是：**如何在代码块中展示代码块本身？**

比如你想写一篇教程，教别人"如何写 Markdown 代码块"，你需要在代码块里展示三个反引号的写法，但三个反引号会被解析器当成外层代码块结束。

### 6.3.1 解决方案：围栏数量递增规则

MyST 遵循通用的围栏嵌套规则：**外层围栏使用 N 个反引号，内层展示 N-1 个反引号的围栏时，外层需要至少 N+1 个反引号。**

简单记忆：**展示 k 个反引号的代码块，需要用 k+1 个反引号包裹。**

| 你想展示 | 外层需要使用 |
|---------|------------|
| 3 个反引号的代码块 | 4 个反引号包裹 |
| 4 个反引号的代码块 | 5 个反引号包裹 |
| 5 个反引号的代码块 | 6 个反引号包裹 |
| n 个反引号的代码块 | n+1 个反引号包裹 |

### 6.3.2 嵌套示例

**示例 1：展示 3 个反引号的普通代码块**

使用 4 个反引号（````）包裹：

`````markdown
````markdown
```python
print("Hello, World!")
```
````
`````

渲染效果：

```python
print("Hello, World!")
```

**示例 2：展示 4 个反引号的嵌套代码块**

使用 5 个反引号（`````）包裹：

``````markdown
`````markdown
````markdown
```python
def hello():
    print("嵌套三层")
```
````
`````
``````

**实战：展示 code-block 指令的写法**

这是写 MyST 教程时最常用的嵌套场景——展示 `code-block` 指令本身（它内部已用了4个反引号），需要用5个反引号包裹。本节 6.2.2 中的示例就是用这种方式实现的。

:::{note}
反引号嵌套规则同样适用于波浪号（`~`）围栏，但反引号更常用。关键是外层围栏长度必须严格长于内层所有围栏。
:::

## 6.4 小结

- **数学公式**：行内用 `{math}` 角色或 `$...$`（需 dollarmath 扩展），块级用 ` ```{math} ` 指令
- **公式引用**：`{math}` 指令加 `:label:`，用 `{eq}` role 引用
- **常用符号**：记住希腊字母、分数\frac、根号\sqrt、求和\sum、积分\int、极限\lim即可，其他查表
- **代码块增强**：用 `code-block` 指令获得 `:linenos:` 行号、`:emphasize-lines:` 强调、`:caption:` 标题、`:label:` 标签
- **代码块引用**：带标签的代码块用 `{numref}` 引用
- **嵌套技巧**：展示 k 个反引号的代码块，外层用 k+1 个反引号包裹

## 导航

[« 上一章：交叉引用](05-advanced-cross-references.md) | [返回目录](README.md) | [下一章：注释、脚注与参考文献 »](07-advanced-notes-citations.md)
