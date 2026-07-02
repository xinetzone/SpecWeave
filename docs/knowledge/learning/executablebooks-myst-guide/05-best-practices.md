+++
title = "MyST Markdown 使用最佳实践"
source = "https://mystmd.org/guide, 官方文档及使用经验总结"
category = "learning"
tags = ["myst", "best-practices", "gotchas", "pitfalls", "commonmark", "compatibility"]
date = "2026-07-02"
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
label = "quickstart"
tags = ["入门", "教程"]
thumbnail = "images/quickstart-cover.png"
date = "2024-01-15"
authors = ["zhangsan"]
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

## 3. 项目结构建议

良好的项目结构可以提升文档的可维护性和协作效率。

### 文件命名规范

- **使用数字前缀排序**：控制文件在目录列表和导航中的顺序
- **使用 kebab-case**：小写字母，连字符分隔单词，避免空格和中文
- **文件名要有描述性**：见名知意

**推荐命名**：

```
01-introduction.md
02-installation.md
03-getting-started.md
04-core-concepts.md
05-api-reference.md
```

**避免的命名**：

```
introduction.md          # 没有排序前缀
第一章介绍.md             # 中文文件名，跨平台兼容性差
gettingStarted.md        # 驼峰命名
doc1.md                  # 无意义名称
```

### 文件夹组织

- **按章节/主题组织文件夹**：相关内容放在同一文件夹下
- **避免过深嵌套**：建议不超过 3 层，方便导航和链接
- **每个章节文件夹可以有自己的 images 目录**：资源就近管理

### 资源管理

- **图片放在 `images/` 或 `figures/` 目录**：与内容文件同级或统一在根目录
- **使用有意义的图片文件名**：不要用 `IMG_1234.png`，用 `architecture-diagram.png`
- **图片格式选择**：优先使用 PNG（截图、图表）、JPG（照片）、SVG（矢量图）
- **为响应式图片提供多尺寸版本**（可选）

### 参考文献

- **统一放在项目根目录的 `references.bib`**：BibTeX 格式
- **所有文档引用同一个参考文献文件**：避免重复和不一致
- **定期整理参考文献**：删除未引用的条目

### .gitignore 配置

必须将构建输出目录加入 `.gitignore`：

```gitignore
# MyST build output
_build/
.myst/
node_modules/

# Jupyter checkpoints
.ipynb_checkpoints/

# OS files
.DS_Store
Thumbs.db

# Logs
*.log
```

### 示例项目结构树

```
my-myst-project/
├── myst.yml                    # 项目配置
├── references.bib              # 统一参考文献
├── .gitignore                  # Git 忽略配置
├── README.md                   # 项目说明
├── images/                     # 全局图片资源（可选）
│   ├── logo.png
│   └── banner.jpg
├── 01-introduction/
│   ├── 01-welcome.md
│   ├── 02-background.md
│   └── images/                 # 章节图片资源
│       └── overview.png
├── 02-getting-started/
│   ├── 01-installation.md
│   ├── 02-quickstart.md
│   └── 03-examples/
│       ├── 01-basic-usage.md
│       └── 02-advanced.md
├── 03-user-guide/
│   ├── 01-syntax-basics.md
│   ├── 02-directives.md
│   └── 03-cross-references.md
├── 04-api-reference/
│   └── ...
└── templates/                  # 自定义模板（如有）
    └── ...
```

## 4. 常见陷阱和注意事项

### 陷阱 1：嵌套块时忘记增加反引号/冒号数量导致解析错误

**问题描述**：在指令内部嵌套另一个指令时，如果使用相同数量的围栏字符，解析器会提前结束外层块。

**正确做法**：每嵌套一层，围栏字符数量增加 1 个。

**示例**：

❌ **错误**：嵌套时使用相同数量的反引号

````markdown
```{note}
这是外层提示框。

```python
# 这个代码块会提前终止外层 note！
print("hello")
```
```
````

✅ **正确**：嵌套时增加反引号数量

`````markdown
````{note}
这是外层提示框。

```python
print("hello")
```
````
`````

同理，冒号围栏嵌套也要增加冒号数量：

```markdown
::::{important}
重要提示框。

:::{note}
嵌套的提示框。
:::
::::
```

### 陷阱 2：Directive 选项缩进错误

**问题描述**：指令的选项（以 `:` 开头的参数）必须与指令内容保持相同的缩进级别，缩进不一致会导致解析失败。

**正确做法**：选项和内容都相对于指令起始位置缩进 3 个空格（或保持一致的缩进）。

**示例**：

❌ **错误**：选项没有正确缩进

````markdown
```{image} images/photo.jpg
:align: center
:width: 500px
这是图片说明。
```
````

✅ **正确**：选项和内容正确缩进

````markdown
```{image} images/photo.jpg
:align: center
:width: 500px

这是图片说明。
```
````

或者使用一致的缩进：

````markdown
:::{figure} images/architecture.png
---
align: center
width: 80%
---
系统架构图
:::
````

### 陷阱 3：使用 file:/// 绝对路径链接

**问题描述**：`file:///` 开头的绝对路径只在本地文件系统有效，构建网站后链接会失效，且在其他开发者的机器上也无法访问。

**正确做法**：始终使用相对路径引用项目内的文件。

**示例**：

❌ **错误**：使用绝对路径

```markdown
![图片](file:///D:/projects/my-docs/images/diagram.png)

参见 [附录](file:///D:/projects/my-docs/appendix.md)
```

✅ **正确**：使用相对路径

```markdown
![图片](images/diagram.png)

参见 [附录](appendix.md)
```

**路径引用小技巧**：
- 同级文件：直接写文件名 `other-file.md`
- 子目录：`subdirectory/file.md`
- 上级目录：`../parent-file.md`（尽量少用）
- 项目根目录：可以用 `/` 开头表示根路径 `/chapter1/intro.md`

### 陷阱 4：YAML frontmatter 中特殊字符未加引号导致解析失败

**问题描述**：YAML 中某些特殊字符（如 `:`, `#`, `{`, `}`, `[`, `]`, `&`, `*`, `!`, `|`, `>`, `'`, `"`, `%`, `@`, `` ` ``）如果出现在值中且未加引号，会导致 YAML 解析错误。

**正确做法**：包含特殊字符的值用双引号包裹。

**示例**：

❌ **错误**：特殊字符未加引号

```yaml
title: MyST: 完整指南
description: 学习使用 #标签 和 {变量}
```

✅ **正确**：特殊字符加引号

```yaml
title: "MyST: 完整指南"
description: "学习使用 #标签 和 {变量}"
```

**TOML frontmatter 同样注意**：

```toml
+++
title = "MyST: 完整指南"
description = "包含特殊字符的值: 如冒号、#号等"
+++
```

### 陷阱 5：在 GitHub 等平台上预览时 MyST 语法不渲染

**问题描述**：GitHub 的 Markdown 渲染器不支持 MyST 的扩展语法，因此 directive、role、交叉引用等不会被渲染，可能显示为原始文本。这是正常现象，不是错误。

**正确做法**：
- 使用冒号围栏包裹文本类指令，提升降级显示效果
- 理解这是平台限制，使用 `myst start` 在本地预览真实效果
- 在 README 中说明需要使用 MyST 构建才能看到完整效果

**降级效果对比**：

| 语法 | GitHub 显示效果 | 使用建议 |
|------|----------------|---------|
| `:::{note}...:::` | 显示为普通文本，Markdown 语法正常工作 | ✅ 推荐 |
| ` ```{note}...``` ` | 显示在代码块中，Markdown 不渲染 | ⚠️ 仅用于代码/公式 |
| `{cite}` 引用 | 显示为原始文本 `{cite}` | 正常，构建后显示 |
| `{ref}` 交叉引用 | 显示为原始文本 `{ref}` | 正常，构建后显示 |

### 陷阱 6：Label 命名冲突

**问题描述**：`label` 必须在整个项目中全局唯一，如果两个页面或两个元素使用相同的 label，交叉引用会指向错误的目标或导致构建错误。

**正确做法**：
- 使用有前缀的命名空间，避免冲突
- 页面 label 使用章节前缀：`sec-intro`、`sec-installation`
- 图片 label 使用 `fig-` 前缀：`fig-architecture`、`fig-flowchart`
- 表格 label 使用 `tab-` 前缀：`tab-comparison`
- 公式 label 使用 `eq-` 前缀：`eq-euler`
- 代码块 label 使用 `code-` 前缀：`code-hello-world`

**示例**：

❌ **错误**：label 过于通用，容易冲突

```toml
+++
label = "intro"
+++
```

````markdown
```{figure} diagram.png
:label: diagram

架构图
```
````

✅ **正确**：使用前缀命名空间

```toml
+++
label = "ch01-intro"
+++
```

````markdown
```{figure} diagram.png
:label: fig-ch01-architecture

第一章系统架构图
```
````

### 陷阱 7：myst start 时端口被占用

**问题描述**：运行 `myst start` 启动开发服务器时，默认端口 3000 可能被其他程序占用，导致启动失败或启动在其他端口。

**正确做法**：
- mystmd 会自动检测端口占用并选择其他可用端口（如 3001、3002）
- 注意终端输出中显示的实际访问 URL
- 可以手动指定端口：`myst start --port 4000`
- 启动前可以先关闭占用端口的程序

**示例**：端口被占用时的输出

```
warning: port 3000 is already in use, using 3001 instead

  ✨✨✨  MyST  ✨✨✨

  📖  Built in 1.23s
  🔌  Server:  http://localhost:3001
  🎯  Target:  ./_build
```

### 陷阱 8：混用 Jupyter Book v1 和 mystmd 配置导致不兼容

**问题描述**：Jupyter Book v1 使用 `_config.yml` 和 `_toc.yml`，而 mystmd 使用 `myst.yml`。如果混用配置文件，可能导致部分配置不生效或行为不一致。

**正确做法**：
- 新项目直接使用 `myst.yml` 作为唯一配置文件
- 从 Jupyter Book v1 迁移时，mystmd 可以读取 `_toc.yml`，但建议逐步迁移到 `myst.yml`
- 不要同时维护两套配置
- 检查项目中是否存在遗留的 `_config.yml`，如果有需要清理或迁移

**迁移检查清单**：

1. 确认项目根目录有 `myst.yml`
2. 将 `_config.yml` 中的配置迁移到 `myst.yml`
3. `_toc.yml` 可以保留使用，或迁移到 `myst.yml` 的 `site.nav`
4. 删除或归档旧的 `_config.yml`
5. 运行 `myst build` 验证构建是否正常
6. 检查所有页面和交叉引用是否正常工作

## 5. 与 CommonMark 的兼容性建议

MyST 是 CommonMark Markdown 的超集，标准 Markdown 语法完全兼容。合理利用这一点可以让你的文档在更多平台上正确显示。

### 优先使用 CommonMark 语法

**原则**：能用标准 Markdown 表达的，就不要用 MyST 特有的指令。

**示例**：

| 需求 | CommonMark 写法 | MyST 扩展写法 | 推荐 |
|------|----------------|--------------|------|
| 标题 | `# 标题` | 不需要 | ✅ CommonMark |
| 加粗 | `**文本**` | 不需要 | ✅ CommonMark |
| 斜体 | `*文本*` | 不需要 | ✅ CommonMark |
| 链接 | `[文本](url)` | 不需要 | ✅ CommonMark |
| 图片 | `![alt](url)` | `{image}` 指令 | ⚠️ 需要尺寸/对齐时用 MyST |
| 无序列表 | `- 项目` | 不需要 | ✅ CommonMark |
| 代码块 | ` ```lang ` | `{code-block}` | ⚠️ 需要标题/标签时用 MyST |
| 简单表格 | Markdown 表格 | `{list-table}` | ✅ 简单表格用 CommonMark |

### 在不支持 MyST 的平台上的降级显示优化

1. **使用冒号围栏**：如前面章节所述，admonitions 等文本容器用 `:::` 而非 ` ``` `
2. **避免过度依赖 role 语法**：行内 `{role}` 在 GitHub 上显示为原始文本，对于关键信息考虑用标准 Markdown 替代
3. **图片使用标准 Markdown 语法**：`![alt](path)` 在任何平台都能显示图片
4. **交叉引用补充说明**：对于 `{ref}` 引用，可以在旁边补充文字说明链接目标

**示例**：

```markdown
:::{note}
**提示**：这部分内容在 GitHub 上也能正常阅读。

参见 [快速入门](#快速入门) 章节了解更多。
:::
```

### 文档可移植性建议

- **避免平台特定的扩展**：如果你需要在多个平台发布文档，谨慎使用 MyST 特有的功能
- **保持语法简单**：复杂的嵌套指令虽然强大，但会降低文档的可移植性
- **导出测试**：定期测试导出为 Markdown、PDF、Word 等格式，确保内容完整
- **分离内容和样式**：使用 MyST 的语义化指令（note、warning 等），不要过多使用原始 HTML/CSS

## 6. 写作风格建议

### 每个文件开头使用 H1 标题

MyST 会自动将文件中的第一个 H1 标题（`# 标题`）提取为页面标题，无需在 frontmatter 中重复指定。

**示例**：

```markdown
+++
# 不需要在这里写 title
description = "页面描述"
+++

# 快速入门指南

这里是正文内容...
```

如果 frontmatter 中显式设置了 `title`，它会覆盖从 H1 提取的标题。

### 合理使用 heading 层级

- **不要跳级**：H1 下直接用 H3 会导致文档结构混乱
- **保持层级一致**：同级标题使用相同的层级
- **H1 唯一**：每个文件只应该有一个 H1 标题
- **层级不要过深**：建议不超过 4 层（H1-H4），过深的层级说明文档应该拆分

❌ **不推荐**：跳级使用标题

```markdown
# 第一章

### 1.1 小节  # 跳级了！应该是 H2

##### 1.1.1 子小节  # 跳级太多！
```

✅ **推荐**：按顺序使用标题层级

```markdown
# 第一章

## 1.1 小节

### 1.1.1 子小节
```

### 长文档建议拆分

- **每个文件聚焦一个主题**：一个文件只讲一件事，方便阅读和维护
- **单文件长度建议**：建议控制在 200-500 行以内，超过则考虑拆分
- **拆分粒度适中**：不要拆得太碎（每个小节一个文件），也不要一个文件包含整章内容
- **使用数字前缀控制顺序**：如 `01-xxx.md`、`02-xxx.md`

### 使用 admonitions 突出重要信息，但不要过度使用

Admonitions（提示框）可以有效突出重要信息，但滥用会导致视觉噪音：

- **note**：一般性提示、补充说明
- **tip**：有用的小技巧、快捷方式
- **important**：需要特别注意的重要内容
- **warning**：可能导致问题的警告
- **caution**：危险操作、数据丢失风险
- **seealso**：相关参考资料

**使用原则**：
- 每页 admonitions 数量建议不超过 3-5 个
- 只把真正需要强调的内容放在提示框中
- 不要把普通正文都放在提示框里
- 选择正确的 admonition 类型

❌ **不推荐**：过度使用 admonitions

```markdown
:::{note}
这是第一段正文...
:::

:::{note}
这是第二段正文...
:::

:::{tip}
这是第三段...
:::
```

✅ **推荐**：适度使用，突出真正重要的内容

```markdown
这是第一段正文，普通内容不需要放在提示框里。

这是第二段正文，正常写作即可。

:::{warning}
这是需要读者特别注意的警告信息！
:::
```

### 图片添加 alt 文本提升可访问性

所有图片都应该添加描述性的 alt 文本，这对可访问性（屏幕阅读器）和 SEO 都很重要：

❌ **不推荐**：alt 文本缺失或过于简单

```markdown
![](./images/diagram.png)
![图片](./images/screenshot.png)
```

✅ **推荐**：描述性的 alt 文本

```markdown
![系统架构图：展示了前端、后端、数据库三层架构以及它们之间的数据流](./images/architecture.png)
![登录界面截图：显示了用户名、密码输入框和登录按钮，右上角有"忘记密码"链接](./images/login-screenshot.png)
```

### 数学公式建议在单独行使用块级 math 指令

对于较长或重要的数学公式，使用块级 math 指令而非行内公式，可以添加 label 方便交叉引用：

❌ **不推荐**：复杂公式挤在正文中

```markdown
根据欧拉公式 $e^{i\\theta} = \\cos\\theta + i\\sin\\theta$，我们可以得到...，当 $\\theta = \\pi$ 时，$e^{i\\pi} + 1 = 0$，这就是著名的欧拉恒等式。
```

✅ **推荐**：重要公式使用块级并添加标签

```markdown
根据欧拉公式：

```{math}
:label: eq-euler-formula
e^{i\theta} = \cos\theta + i\sin\theta
```

当 $\theta = \pi$ 时，我们得到著名的欧拉恒等式：

```{math}
:label: eq-euler-identity
e^{i\pi} + 1 = 0
```

如公式 {eq}`eq-euler-identity` 所示...
```

## 7. 性能和可访问性建议

### 图片优化

- **压缩图片**：使用工具压缩图片减小文件大小，推荐工具：
  - PNG: pngquant, TinyPNG
  - JPG: jpegoptim, mozjpeg
  - 通用: Squoosh (https://squoosh.app/)
- **使用适当尺寸**：不要放 4000px 宽的图片然后只显示为 800px，提前缩放到合适尺寸
- **提供缩略图**：对于大图，提供缩略图并链接到原图
- **优先使用矢量图**：图表、图标、logo 等使用 SVG 格式，缩放不失真且文件小
- **选择正确的格式**：
  - 照片/复杂图像：JPG/WebP
  - 截图/图表/插画：PNG
  - 图标/Logo/矢量图：SVG
  - 简单动画：GIF（但注意文件大小）

### 避免过深的 TOC 嵌套

目录（TOC）嵌套层级建议不超过 3 层，过深的嵌套会让读者难以导航：

**推荐层级结构**：

```
第一部分（H1）
├── 第一章（H2）
│   ├── 1.1 小节（H3）
│   └── 1.2 小节（H3）
└── 第二章（H2）
```

在 `myst.yml` 中配置 TOC 深度：

```yaml
site:
  options:
    toc_depth: 3  # 只显示到 H3
```

### 为所有图片添加描述性 alt 文本

这既是可访问性要求，也是最佳实践：
- 屏幕阅读器用户依赖 alt 文本理解图片内容
- 图片加载失败时 alt 文本会显示
- 帮助搜索引擎理解图片内容
- 描述要简洁但包含关键信息，建议 1-2 句话

### 使用语义化的 directives

MyST 提供了多种语义化的 admonition 和指令，使用它们而非通用容器，可以让文档结构更清晰：

| 语义化指令 | 用途 | 替代通用写法 |
|-----------|------|------------|
| `{note}` | 一般性提示 | `{admonition}` 自定义类型 |
| `{warning}` | 警告信息 | 加粗文本或通用容器 |
| `{tip}` | 技巧建议 | 无序列表项 |
| `{important}` | 重要信息 | 大写或强调 |
| `{seealso}` | 参考资料 | 普通链接 |
| `{figure}` | 带标题的图片 | 图片+独立标题段落 |
| `{table}` | 带标题的表格 | 表格+独立标题段落 |

✅ **推荐**：使用语义化指令

````markdown
:::{warning}
运行此命令会删除所有数据，请确保已备份！
:::

```{figure} images/workflow.png
:label: fig-workflow

数据处理工作流程图
```
````

❌ **不推荐**：使用通用容器或普通文本

````markdown
**警告**：运行此命令会删除所有数据，请确保已备份！

![工作流程](images/workflow.png)
图 1：数据处理工作流程图
```
````

### 导出 PDF 时注意字体和图片分辨率

导出为 PDF 时，印刷质量比屏幕显示要求更高：

- **图片分辨率**：至少 300 DPI（屏幕显示通常是 72/96 DPI）
- **字体嵌入**：确保所有字体都已嵌入 PDF，避免在其他设备上显示异常
- **矢量图优先**：图表尽量使用 SVG/Mermaid 等矢量格式，PDF 中可无限缩放
- **颜色模式**：印刷时考虑转换为 CMYK（电子版保持 RGB 即可）
- **检查分页**：导出后检查分页是否合理，避免标题在页末、图片被截断等问题
- **选择合适模板**：mystmd 提供了多种期刊模板，选择与目标出版物匹配的模板

## 8. 版本控制建议

### `_build` 目录必须加入 `.gitignore`

`_build` 目录是 mystmd 的构建输出目录，包含生成的 HTML、PDF 等文件，这些文件是派生产物，不应该纳入版本控制：

```gitignore
# MyST 构建输出
_build/
.myst/

# 依赖目录
node_modules/

# Jupyter 相关
.ipynb_checkpoints/

# 操作系统文件
.DS_Store
Thumbs.db

# 编辑器文件
.vscode/
.idea/
*.swp
*.swo

# 日志文件
*.log
```

### `myst.yml` 纳入版本控制

`myst.yml` 是项目的核心配置文件，必须纳入版本控制：
- 它定义了项目结构、作者、导出配置等
- 团队成员需要相同的配置才能构建一致的文档
- 配置变更应该通过代码审查流程

### 内容文件纳入版本控制

所有源内容文件都应该纳入版本控制：
- `.md` 文件：MyST Markdown 源文件
- `.ipynb` 文件：Jupyter Notebook 文件（如果使用可执行文档）
- `references.bib`：参考文献文件
- 图片资源：`images/`、`figures/` 等目录下的图片文件

**注意**：如果图片文件过大，可以考虑使用 Git LFS（Large File Storage）管理。

### `templates` 目录如果有自定义模板也应纳入

如果你有自定义的导出模板、主题等，它们也是源文件的一部分，应该纳入版本控制：

```
templates/
├── my-custom-template/
│   ├── template.tex
│   ├── template.yml
│   └── assets/
│       ├── logo.png
│       └── style.css
```

### 其他建议

- **不要提交构建产物**：永远不要提交 `_build/` 目录下的任何文件到 Git
- **使用 .gitattributes**：对于特定文件类型可以配置 Git 行为
- **考虑文档版本发布**：可以使用 Git tags 标记文档版本，如 `v1.0`、`v2.0`
- **CI/CD 自动构建**：配置 CI 自动构建文档并部署到 GitHub Pages/Read the Docs 等平台
- **审查配置变更**：`myst.yml` 的变更应该像代码一样进行审查

**推荐的仓库文件清单**：

```
✅ 纳入版本控制：
├── myst.yml                 # 项目配置
├── references.bib           # 参考文献
├── .gitignore               # Git 忽略配置
├── README.md                # 项目说明
├── **/*.md                  # 所有 Markdown 源文件
├── **/*.ipynb               # 所有 Notebook 文件
├── images/**/*              # 图片资源
├── templates/**/*           # 自定义模板（如有）
└── package.json             # 依赖配置（如果需要）

❌ 不纳入版本控制：
├── _build/                  # 构建输出
├── .myst/                   # MyST 缓存
├── node_modules/            # 依赖
├── .ipynb_checkpoints/      # Jupyter 检查点
└── *.log                    # 日志文件
```

## 总结

本文档涵盖了 MyST Markdown 使用中的 8 个方面的最佳实践：

1. **围栏选择**：文本类内容用冒号围栏，代码/公式/图表用反引号围栏
2. **Frontmatter 组织**：项目级统一配置共性内容，页面级只放差异配置
3. **项目结构**：数字前缀排序、kebab-case 命名、资源就近管理
4. **常见陷阱**：注意嵌套、缩进、路径、特殊字符、label 冲突等问题
5. **CommonMark 兼容**：优先使用标准 Markdown，优化降级显示
6. **写作风格**：规范标题层级、适度使用提示框、图片加 alt 文本
7. **性能可访问性**：优化图片、避免过深层级、使用语义化指令
8. **版本控制**：正确配置 .gitignore，只提交源文件不提交构建产物

遵循这些最佳实践，可以帮助你创建结构清晰、易于维护、兼容性好的 MyST 文档项目。
