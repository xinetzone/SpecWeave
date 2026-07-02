+++
title = "MyST Markdown 使用最佳实践"
source = "https://mystmd.org/guide, 官方文档及使用经验总结"
+++

# MyST Markdown 使用最佳实践

本文档汇总了 MyST Markdown 在日常使用中的最佳实践，结合官方文档推荐和实际项目经验，帮助你写出清晰、可维护、兼容性好的 MyST 文档。

## 1. 围栏选择指南（重要）

MyST 支持两种围栏语法：冒号围栏（`:::`）和反引号围栏（` ``` `）。正确选择围栏类型对文档可读性和跨平台兼容性至关重要。

### 什么时候用冒号围栏（:::）

**适用场景**：指令内容是 Markdown 文本，需要在 GitHub 等非 MyST 渲染器中有更好的降级显示。

**典型指令**：
- `admonitions`（note、warning、tip、important、caution 等）
- `theorems`、`proofs`、`definitions`
- `dropdowns`、`tabs`
- 其他包含 Markdown 文本的容器类指令

**优势**：
- 在 GitHub 等平台上会降级显示为普通文本，不会显示为代码块
- 阅读原始 Markdown 时更易读
- 编辑器对冒号围栏的缩进处理更友好

**示例**：

```markdown
:::{note}
这是一个提示，在 GitHub 上会显示为普通文本，不会被当作代码块。

你可以在这里正常使用 **加粗**、*斜体*、[链接](https://example.com) 等 Markdown 语法。
:::
```

### 什么时候用反引号围栏（```）

**适用场景**：指令内容是代码类内容，需要防止编辑器/格式化工具自动修改内容。

**典型指令**：
- `math` 公式块
- `mermaid`、`diagrams` 图表
- `code-block`、`code-cell` 代码块
- 其他包含代码、特殊语法的内容块

**优势**：
- 内容被视为代码，编辑器不会自动格式化
- 防止 Prettier 等工具破坏特殊语法
- 明确标识这是代码/特殊内容区域

**示例**：

````markdown
```{math}
:label: euler-equation
e^{i\pi} + 1 = 0
```

```{mermaid}
flowchart LR
    A[开始] --> B{判断}
    B -->|是| C[执行]
    B -->|否| D[结束]
```
````

### 选择原则总结表格

| 内容类型 | 推荐围栏 | 理由 |
|---------|---------|------|
| Admonitions（提示框） | `:::` | 降级显示友好，Markdown 可正常渲染 |
| 定理/证明/定义 | `:::` | 内容是自然语言，降级可读 |
| 下拉菜单/标签页 | `:::` | 内含 Markdown 内容 |
| Math 数学公式 | ` ``` ` | 防止编辑器修改 LaTeX 语法 |
| Mermaid 图表 | ` ``` ` | 防止格式化破坏图表语法 |
| 代码块/代码单元格 | ` ``` ` | 明确标识代码区域 |
| 表格/图片 | 无需围栏 | 使用标准 Markdown 语法或简单指令 |

### 正反例对比

❌ **错误示例**：用反引号围栏包裹 admonition（在 GitHub 上显示为代码块，难以阅读）

````markdown
```{note}
这是一个提示。

在 GitHub 上这段内容会显示在代码块里，**加粗**等格式也不会渲染。
```
````

✅ **正确示例**：用冒号围栏包裹 admonition（降级显示友好）

```markdown
:::{note}
这是一个提示。

在 GitHub 上这段内容显示为普通文本，**加粗**等格式正常渲染。
:::
```

❌ **错误示例**：用冒号围栏包裹 Mermaid 图表（编辑器可能自动格式化破坏语法）

```markdown
:::{mermaid}
flowchart LR
    A --> B
    B --> C
:::
```

✅ **正确示例**：用反引号围栏包裹 Mermaid 图表（保护代码内容）

````markdown
```{mermaid}
flowchart LR
    A --> B
    B --> C
```
````

## 2. Frontmatter 组织建议

MyST 支持两级配置：项目级（`myst.yml`）和页面级（文件内 TOML frontmatter）。合理分工可以避免重复配置，保持项目整洁。

### 项目级 vs 页面级的分工

**项目级统一配置**（在 `myst.yml` 中定义）：

| 字段 | 说明 |
|------|------|
| `authors` | 作者信息，统一在项目级定义，页面通过 id 引用 |
| `license` | 项目许可证 |
| `bibliography` | 参考文献文件路径 |
| `github` | GitHub 仓库链接 |
| `keywords` | 项目关键词 |
| `exports` | 导出配置（PDF、Word 等） |
| `site` | 网站配置（导航、logo、标题等） |

**页面级单独配置**（在文件 frontmatter 中定义）：

| 字段 | 说明 |
|------|------|
| `title` | 页面标题（如果不从 H1 自动提取） |
| `description` | 页面描述，用于 SEO 和搜索 |
| `label` | 页面唯一标签，用于交叉引用 |
| `tags` | 页面标签/分类 |
| `thumbnail` | 缩略图路径 |
| `date` | 发布日期/更新日期 |
| `subject` | 主题 |

**示例：项目级 `myst.yml`**

```yaml
version: 1
project:
  title: "我的技术文档"
  authors:
    - id: zhangsan
      name: "张三"
      email: "zhangsan@example.com"
      affiliations:
        - id: tech
          name: "技术部"
  license:
    content: CC-BY-4.0
    code: MIT
  bibliography: references.bib
  github: https://github.com/username/repo
site:
  template: book-theme
  nav:
    - title: "简介"
      file: intro.md
```

**示例：页面级 frontmatter**

```toml
+++
title = "快速入门指南"
description = "本章节介绍如何快速上手使用本工具"
label: quickstart
tags = ["入门", "教程"]
thumbnail = images/quickstart-cover.png
date = 2024-01-15
authors:
  - zhangsan
+++
```

### Frontmatter 字段组织顺序建议

按"从通用到特定"的顺序组织字段，提升可读性：

```toml
+++
# 1. 基础标识
title = "页面标题"
label = unique-page-label

# 2. 描述与分类
description = "页面简短描述"
tags = ["标签1", "标签2"]
subject = "主题分类"

# 3. 资源与视觉
thumbnail = images/cover.png

# 4. 时间信息
date = 2024-01-15
updated = 2024-03-20

# 5. 作者引用
authors = ["zhangsan", "lisi"]

# 6. 页面特定配置
exports = []
+++
```

### 避免重复配置

页面级配置会覆盖项目级配置。遵循以下原则：

1. **能放项目级就不放页面级**：共性配置统一在 `myst.yml` 中管理
2. **不要复制粘贴项目级配置**：页面级只定义差异部分
3. **作者信息必须项目级统一定义**：避免在每个页面重复写作者详情

❌ **不推荐**：在页面重复定义作者信息

```toml
+++
title = "章节一"
# 重复定义作者信息，难以维护
authors:
  - name: "张三"
    email: "zhangsan@example.com"
+++
```

✅ **推荐**：页面只通过 id 引用作者

```toml
+++
title = "章节一"
authors = ["zhangsan"]
+++
```

## 3.