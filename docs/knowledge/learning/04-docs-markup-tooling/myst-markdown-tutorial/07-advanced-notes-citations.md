---
id: "myst-tutorial-notes-citations"
title: "第7章：高级功能 - 注释、脚注与参考文献"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/04-docs-markup-tooling/myst-markdown-tutorial/07-advanced-notes-citations.toml"
---
# 第7章：高级功能 - 注释、脚注与参考文献

注释用于编写过程中记录备注，脚注用于补充说明不打断正文的内容，参考文献用于学术写作中的引用管理。

## 7.1 注释（Comments）

注释是写作者的"草稿纸"——内容存在于源文件中，但不会渲染到最终输出。

### 7.1.1 行注释：`%` 开头

以百分号 `%` 开头，从 `%` 到行尾的内容都会被解析器忽略：

```markdown
这是正文内容。
% 这是一行注释，不会出现在渲染结果中
这行文字正常显示。 % 行尾也可以加注释
```

渲染效果：

> 这是正文内容。
>
> 这行文字正常显示。

`%` 必须出现在行首或空格之后才被识别为注释。出现在单词中间（如 `100%`）则作为普通字符。

### 7.1.2 块注释

多行注释有两种方式：

**方式 1：每行开头加 `%`**
```markdown
% 第一行注释
% 第二行注释
正文内容从这里开始。
```

**方式 2：`%{ %}` 包裹（推荐用于大段注释）**
```markdown
%{
这是一个块注释区域，
可以写任意多行内容，
不需要每行都加百分号。
%}
正文继续。
```

### 7.1.3 MyST 注释 vs HTML 注释

| 特性 | MyST 注释 (`%`) | HTML 注释 (`<!-- -->`) |
|------|----------------|----------------------|
| 输出结果 | **完全不出现在任何输出中**（包括 HTML 源码） | 作为 HTML 注释保留在输出源码中 |
| 适用场景 | 写作备注、草稿标记、临时隐藏内容 | 需要在 HTML 源码保留（一般不推荐） |

:::{tip}
日常写作一律使用 `%` 注释，确保草稿内容不会泄露到最终输出。
:::

### 7.1.4 使用场景

1. **写作备注**：`% TODO: 补充最新数据`
2. **临时隐藏内容**：调试文档时注释掉某段而不删除
3. **元信息记录**：在文件头部记录文档状态、作者信息

## 7.2 脚注（Footnotes）

脚注用于补充说明，读者点击标记可跳转到页脚注释，不打断正文阅读。

### 7.2.1 标准脚注语法

包含两部分：行内标记 `[^n]` 和脚注内容定义 `[^n]: 文本`：

```markdown
这是一段正文，这里有一个脚注标记[^1]。

[^1]: 这是脚注的详细说明，包含多行时后续行保持缩进即可。
    缩进对齐的行会被视为同一条脚注。
```

渲染时 `[^1]` 变成上标数字，脚注内容自动收集到页面底部，并有返回链接。

:::{note}
脚注定义不需要严格放在文末，可以放在任意位置，MyST 会自动收集到页脚。
:::

### 7.2.2 命名脚注（推荐）

数字脚注增删时需要重新编号，推荐使用**命名脚注**：

```markdown
MyST Markdown[^myst-intro] 是 CommonMark 的超集[^commonmark]。

[^myst-intro]: MyST（Markedly Structured Text）专为技术文档和学术写作设计。
[^commonmark]: CommonMark 是 Markdown 的标准化规范。
```

命名脚注的好处：无需关心编号顺序、语义清晰、便于搜索定位。

:::{tip}
脚注名称可包含字母、数字、连字符和下划线，不能有空格。推荐使用小写加连字符风格（如 `[^source-data]`）。
:::

### 7.2.3 MyST 增强特性

- **多次引用**：同一脚注可在正文多处引用，编号自动保持一致
  ```markdown
  第一章[^see-also]提到，第三章[^see-also]还会展开。
  [^see-also]: 跨章节引用示例。
  ```
- **自动编号**：命名脚注也会按引用顺序自动分配连续编号
- **位置灵活**：短脚注紧接引用段落后，长脚注统一放文末

### 7.2.4 使用场景

- 资料来源标注
- 术语或概念的补充解释
- 版本兼容性说明
- 与主题相关但展开会偏离主线的题外话

```markdown
该 API 在 v2.0 引入[^v2-note]，性能提升约 30%。
[^v2-note]: v1.x 用户需升级，迁移指南见官方文档。
```

## 7.3 参考文献（Citations）快速入门

MyST 集成 BibTeX 引用体系，支持自动生成参考文献列表和多种引用格式。

:::{note}
本节仅提供**最小可工作示例**帮助快速上手。CSL 样式自定义、多文献库等深度配置请参考 [MyST 官方引用文档](https://mystmd.org/guide/citations)。
:::

### 7.3.1 基本概念

| 概念 | 说明 | 文件格式 |
|------|------|---------|
| **BibTeX 文件** | 存储参考文献元数据（作者、标题、年份、期刊等） | `.bib` |
| **CSL 样式** | 定义引用排版格式（APA、GB/T 7714、IEEE 等） | `.csl` |
| **引用命令** | 在正文中标记引用位置 | `{cite}` role |

### 7.3.2 第一步：准备 `.bib` 文件

创建 `references.bib` 存放文献条目：

```bibtex
@article{knuth1984literate,
  author  = {Knuth, Donald E.},
  title   = {Literate Programming},
  journal = {The Computer Journal},
  year    = {1984},
  volume  = {27},
  pages   = {97--111}
}

@book{lamport1994latex,
  author    = {Lamport, Leslie},
  title     = {\LaTeX: A Document Preparation System},
  publisher = {Addison-Wesley},
  year      = {1994}
}
```

每个条目格式：`@类型{引用键, 字段1=值, 字段2=值, ...}`，引用键（如 `knuth1984literate`）用于在正文中引用。

:::{tip}
引用键推荐使用「作者年份关键词」风格（如 `knuth1984literate`），易记忆且避免重复。
:::

### 7.3.3 第二步：配置 bibliography

在 `myst.yml` 中指定 BibTeX 文件路径：

```yaml
project:
  title: 我的文档
  bibliography: references.bib
```

Sphinx 用户在 `conf.py` 中配置：`bibtex_bibfiles = ["references.bib"]`。

### 7.3.4 第三步：在正文中引用

使用 `{cite}` role 插入引用标记：

```markdown
文学编程由 {cite:t}`knuth1984literate` 提出，是一种重要的方法论 {cite:p}`knuth1984literate`。
LaTeX 经典参考见 {cite}`lamport1994latex`。
```

cite 变体：

| Role | 渲染效果 | 说明 |
|------|---------|------|
| `{cite}`key`` | [1] | 默认括号式编号引用 |
| `{cite:t}`key`` | Knuth (1984) | **文本式**：作者融入正文 |
| `{cite:p}`key`` | (Knuth, 1984) | **括号式**：作者年份都在括号中 |

多篇文献同时引用用逗号分隔：`{cite}`knuth1984literate,lamport1994latex``。

### 7.3.5 第四步：生成参考文献列表

在文档末尾使用 `bibliography` 指令，自动收集引用过的文献并生成格式化列表：

````markdown
## 参考文献

```{bibliography}
:style: plain
```
````

常用样式：`plain`（数字编号，按引用顺序）、`alpha`（作者年份缩写标签）。

:::{note}
GB/T 7714、APA 7th、IEEE 等特定格式需要额外配置 CSL 样式文件，超出本章范围。
:::

### 7.3.6 最小完整示例

**文件 1：`references.bib`**
```bibtex
@book{goossens1994latex,
  author    = {Goossens, Michel and Mittelbach, Frank},
  title     = {The \LaTeX{} Companion},
  publisher = {Addison-Wesley},
  year      = {1994}
}
```

**文件 2：`myst.yml`**
```yaml
project:
  title: 参考文献最小示例
  bibliography: references.bib
```

**文件 3：`index.md`**
`````markdown
---
title: 参考文献演示
---

# 参考文献演示

LaTeX 经典参考指南包括 {cite:t}`goossens1994latex`。

## 参考文献

```{bibliography}
```
`````

运行 `myst start` 即可看到引用自动编号、参考文献列表自动生成的效果。

## 7.4 边注简介

MyST 提供 `margin` 和 `sidebar` 指令创建边注——内容显示在页面右侧边栏，适合术语表、关键要点等内容：

````markdown
```{margin}
**术语**：边注显示在页面右侧，不占用正文流位置。
```

正文内容继续...
````

`sidebar` 类似但创建带标题的浮动面板。边注组件在后续章节不单独深入讲解，需要时可查阅官方文档。

## 7.5 小结

- **注释**：`%` 行注释，`%{ %}` 块注释，完全不渲染到输出
- **脚注**：`[^name]` 标记 + `[^name]: 内容` 定义，推荐使用命名脚注
- **参考文献**：准备 `.bib` → 配置 `bibliography` → `{cite}` 引用 → ````{bibliography}```` 生成列表
- **引用变体**：`{cite:t}` 文本式，`{cite:p}` 括号式
- **边注**：`margin`/`sidebar` 指令用于页边内容

## 导航

[« 上一章：数学公式与代码块](06-advanced-math-code.md) | [返回目录](README.md) | [下一章：扩展组件：提示框 »](08-components-admonitions.md)
