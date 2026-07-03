---
id: "myst-tutorial-cross-references"
title: "第5章：高级功能 - 交叉引用"
---

# 第5章：高级功能 - 交叉引用

交叉引用是技术文档和学术出版的必备功能，让文档内的章节、图表、公式、代码块等元素之间建立可点击的智能链接。MyST 提供了出版级的交叉引用系统，支持自动编号、位置无关引用和重构友好性。

深度参考：[交叉引用示例](../executablebooks-myst-guide/examples/cross-references.md)

## 5.1 为什么需要交叉引用

在长篇文档中，硬编码的"如图3所示"、"参见第2章"有三个致命问题：

| 问题 | 说明 | 交叉引用如何解决 |
|------|------|-----------------|
| 编号失效 | 中间插入新图表后，所有后续编号全部错位 | 自动编号，插入/删除元素后自动更新 |
| 链接断裂 | 移动章节位置后，手动锚点链接失效 | 基于标签而非位置，重构不影响引用 |
| 维护成本 | 修改标题文字后，所有引用文本需手动更新 | 自动获取目标标题/题注文本 |

:::{tip}
交叉引用是**出版级文档**与**普通笔记**的核心区别。文档超过10页或包含5个以上图表/公式时，必须使用交叉引用。
:::

## 5.2 添加标签（Labels）

标签是交叉引用的目标锚点。MyST 支持自动生成标签和显式定义标签两种方式。

### 5.2.1 标题自动生成标签

对于章节标题，MyST 自动生成隐式标签，规则：小写、空格变 `-`、去除特殊字符、连续连符合并。

| 原始标题 | 自动标签 |
|---------|---------|
| `## 安装与配置` | `安装与配置` |
| `## Hello, World!` | `hello-world` |

:::{warning}
自动标签依赖标题文本，修改标题会导致标签改变、引用断裂。重要位置请使用显式标签。
:::

### 5.2.2 显式标签方法 1：`(label-name)=` 前置语法

最通用的标签定义方式，适用于标题、图表、表格、代码块等所有元素：

```markdown
(my-section)=
## 我的章节标题
```

语法规则：`(label-name)=` 单独占一行，紧跟在目标元素上方；标签名在整个项目中必须唯一。

为图表添加标签示例：

````markdown
(architecture-diagram)=
:::{figure} images/architecture.png
:alt: 系统架构图
:width: 80%

图 1：系统整体架构
:::
````

### 5.2.3 显式标签方法 2：Directive 的 `:label:` 选项

很多内置 Directive 支持 `:label:` 选项，更语义化：

````markdown
:::{figure} images/architecture.png
:alt: 系统架构图
:width: 80%
:label: fig-architecture

图 1：系统整体架构
:::
````

同样适用于表格、代码块、公式等：

````markdown
:::{list-table} 功能对比表
:header-rows: 1
:label: tbl-features

* - 功能
  - MyST
* - 交叉引用
  - ✓
:::
````

:::{tip}
两种方式功能等价：`(label)=` 更通用，`:label:` 更贴近元素语义，任选其一即可。
:::

### 5.2.4 标签命名最佳实践

1. **kebab-case 命名**：全小写，单词间用 `-` 连接
   - ✅ `fig-architecture`、`sec-installation`
   - ❌ `FigArchitecture`、`fig_architecture`、`Figure 1`

2. **带类型前缀**：章节 `sec-xxx`、图片 `fig-xxx`、表格 `tbl-xxx`、公式 `eq-xxx`、代码 `code-xxx`

3. **语义化命名**：名称反映内容而非编号
   - ✅ `fig-system-architecture`（即使变图3也不影响）
   - ❌ `fig-1`（前面插入新图就错了）

4. **全局唯一**：标签在整个项目中不能重复

## 5.3 引用方式

MyST 提供多种引用 Role，适用于不同场景。

### 5.3.1 `{ref}` - 带标题的引用

最常用的引用方式，自动获取目标元素的标题/题注作为链接文本：

```markdown
详细说明请参见 {ref}`sec-installation`。
详细说明请参见 {ref}`安装章节 <sec-installation>`。
```

:::{note}
`{ref}` 适用于引用章节等无编号元素，图表/表格等带编号元素用 `{numref}`。
:::

### 5.3.2 `{numref}` - 带自动编号的引用

专为图表、表格、代码块等需要编号的元素设计，自动生成"图1"、"表2"：

```markdown
系统架构如 {numref}`fig-architecture` 所示。
{numref}`图 %s <fig-architecture>` 展示了整体架构。
```

`%s` 是编号占位符，中文文档常用格式：
- `{numref}`图 %s <fig-xxx>`` → 图 1
- `{numref}`表 %s <tbl-xxx>`` → 表 2
- `{numref}`代码清单 %s <code-xxx>`` → 代码清单 3

### 5.3.3 `{eq}` - 公式专用引用

引用带编号的数学公式，只显示公式编号：

```markdown
根据勾股定理 {eq}`eq-pythagoras`，可计算斜边长度。
```

渲染效果：根据勾股定理 (1)，可计算斜边长度。

带标签公式示例：

````markdown
```{math}
:label: eq-pythagoras

a^2 + b^2 = c^2
```
````

或用 `$$` 语法：

```markdown
(eq-pythagoras)=
$$
a^2 + b^2 = c^2
$$ (eq-pythagoras)
```

### 5.3.4 `{doc}` - 引用其他文档

引用项目中的其他文档，自动使用目标文档标题作为链接文本：

```markdown
快速入门请阅读 {doc}`00-quick-start`。
快速入门请阅读 {doc}`这里 <00-quick-start>`。
```

:::{warning}
`{doc}` 路径相对于当前文档，不需要 `.md` 后缀。跨文件夹引用注意路径层级。
:::

### 5.3.5 隐式引用：按标题文本引用

没有显式标签时，可直接用标题文本隐式引用：

```markdown
请参阅 {ref}`5.2 添加标签（Labels）`。
```

:::{warning}
隐式引用强烈不推荐：修改标题会断裂、标题重复时无法确定目标、重构易出错。重要位置始终用显式标签。
:::

## 5.4 常见问题与排错

### 5.4.1 "WARNING: undefined label" 错误

最常见的交叉引用错误，原因和解决：

| 原因 | 解决方法 |
|------|---------|
| 标签拼写错误 | 核对大小写、连字符 |
| 标签不存在 | 添加 `(label)=` 或 `:label:` 选项 |
| 文档未包含在 TOC | 确保被引用文档在 `_toc.yml` 中 |
| 标签重复定义 | 搜索整个项目删除重复标签 |
| 跨文档引用找不到 | 确保路径正确且文档在TOC中 |

### 5.4.2 跨文档引用注意事项

跨文档引用三条件：
1. 标签全局唯一
2. 被引用文档在 `_toc.yml` 目录树中
3. 完整项目构建（单文件预览可能无法解析）

### 5.4.3 编号格式自定义

在 `myst.yml` 中可配置默认编号格式：

```yaml
project:
  reference:
    figure: "图 %s"
    table: "表 %s"
    code: "代码清单 %s"
    equation: "(%s)"
```

配置后 `{numref}`fig-xxx`` 自动显示"图 1"，无需每次写自定义文本。

## 5.5 完整示例：迷你技术文档

包含章节、图、表、公式、代码块引用的完整可复制示例：

````markdown
---
title: "迷你示例文档"
---
(introduction)=
# 简介
本文档演示交叉引用：数学原理 {eq}`eq-sum`、架构 {numref}`fig-arch`、
性能对比 {numref}`tbl-perf`，实现见 {numref}`code-algorithm`。

(mathematics)=
## 数学原理
(eq-sum)=
$$S = \sum_{i=1}^{n} x_i$$ (eq-sum)

如 {eq}`eq-sum` 所示，计算从 1 到 n 的和。

:::{figure} images/architecture.png
:alt: 架构图
:width: 70%
:label: fig-arch
图 1：系统架构
:::
如 {numref}`fig-arch` 所示，{numref}`图 %s <fig-arch>` 中数据层负责存储。

:::{list-table} 性能对比
:header-rows: 1
:label: tbl-perf
* - 算法
  - 时间复杂度
* - 暴力法
  - O(n²)
* - 优化版
  - O(n)
:::
详见 {numref}`tbl-perf`。

:::{code-block} python
:label: code-algorithm
def optimized_sum(arr):
    total = 0
    for x in arr:
        total += x
    return total
:::
完整实现见 {numref}`code-algorithm`。

## 总结
- 数学原理参见 {ref}`mathematics`
- 更多内容见 {doc}`06-advanced-math-code`
````

## 5.6 小结

- **标签定义**：`(label)=` 前置语法或 `:label:` 选项，二选一
- **引用方式**：`{ref}` 引用章节显示标题、`{numref}` 引用图表显示编号、`{eq}` 引用公式、`{doc}` 引用其他文档
- **命名规范**：kebab-case + 类型前缀（sec-/fig-/tbl-/eq-/code-）
- **排错**：undefined label 时检查拼写、重复、TOC 包含

## 导航

[« 上一章：Directives 和 Roles](04-advanced-directives-roles.md) | [返回目录](README.md) | [下一章：数学公式与代码块 »](06-advanced-math-code.md)
