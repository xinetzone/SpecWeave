---
source: "https://mystmd.org/guide/table-of-contents"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/executablebooks-myst-guide/04-table-of-contents.toml"
title: "目录结构（TOC）配置指南"
---
# 目录结构（TOC）配置指南

本文档详细介绍 MyST Markdown 项目的目录结构（Table of Contents，TOC）配置，包括 TOC 概述、节点类型、嵌套结构、Glob 模式匹配、标题配置、隐藏页面、页面内 TOC 指令、URL Slug 规则、隐式 TOC 规则以及完整示例。

---

## 1. TOC 概述

### 1.1 什么是 TOC

TOC（Table of Contents，目录结构）是 MyST 项目的核心配置之一，用于：

- **定义项目文档结构**：组织页面之间的层级关系
- **生成网站导航**：自动构建侧边栏、顶部导航、面包屑等导航组件
- **控制导出顺序**：导出 PDF/Word/LaTeX 等格式时确定内容排列顺序
- **支持交叉引用**：提供页面间的结构化链接

### 1.2 配置位置

TOC 配置位于项目根目录的 `myst.yml` 文件中，在 `project.toc` 字段下定义：

```yaml
version: 1

project:
  title: "我的 MyST 项目"
  # TOC 配置在这里
  toc:
    - file: index.md
    - file: chapter1.md
    - file: chapter2.md
```

### 1.3 自动生成 TOC

使用 `myst init --write-toc` 命令可以根据项目中的文件自动生成 TOC 配置：

```bash
# 初始化项目并自动写入 TOC
myst init --write-toc

# 对于已有项目，重新生成 TOC
myst init --write-toc --force
```

该命令会：
1. 扫描项目中的所有 `.md` 和 `.ipynb` 文件
2. 按照字母/数字自然排序
3. 自动识别 `index.md`/`README.md` 作为首页
4. 将生成的 TOC 写入 `myst.yml`

### 1.4 隐式 TOC（无配置时的默认行为）

如果不在 `myst.yml` 中显式配置 `project.toc`，MyST 会自动根据文件系统生成隐式 TOC，详见第 10 节"隐式 TOC 规则"。

---

## 2. TOC 树结构节点类型

TOC 是一个树状结构，每个节点可以是以下几种类型：

### 2.1 file 节点（本地文件）

指向项目中的本地 Markdown（`.md`）或 Jupyter Notebook（`.ipynb`）文件，这是最常用的节点类型。

| 字段 | 类型 | 必需 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 文件路径，相对于项目根目录，可省略扩展名 |
| `title` | string | 否 | 覆盖页面显示标题（见第 6 节） |
| `short_title` | string | 否 | 短标题，用于空间有限的导航位置 |
| `hidden` | boolean | 否 | 是否在导航中隐藏（见第 7 节） |
| `children` | array | 否 | 子节点数组，用于嵌套 |

**示例**：

```yaml
project:
  toc:
    - file: index.md
      title: "首页"
    - file: chapters/introduction.md
      title: "引言"
      short_title: "引言"
    - file: notebooks/analysis.ipynb
      title: "数据分析"
```

### 2.2 url 节点（外部链接）

指向外部网站的链接，可用于在导航中添加参考资源、项目主页等。

| 字段 | 类型 | 必需 | 说明 |
|---|---|---|---|
| `url` | string | 是 | 外部 URL 地址 |
| `title` | string | 是 | 链接显示文本 |
| `open_in_same_tab` | boolean | 否 | 是否在当前标签页打开，默认 `false`（新标签页） |
| `children` | array | 否 | 子节点数组（注意：外部链接的子节点仅作为分组显示，不会实际嵌套） |

**示例**：

```yaml
project:
  toc:
    - file: index.md
    - url: "https://github.com/executablebooks/mystmd"
      title: "MyST GitHub 仓库"
      open_in_same_tab: false
    - url: "https://mystmd.org/guide"
      title: "官方文档"
```

### 2.3 pattern 节点（Glob 模式匹配）

使用 Glob 模式批量匹配文件，适合自动包含某个目录下的所有文件，如博客文章、章节文件等。

| 字段 | 类型 | 必需 | 说明 |
|---|---|---|---|
| `pattern` | string | 是 | Glob 匹配模式，如 `chapters/*.md`、`blog/**/*.md` |
| `title` | string | 否 | 分组标题（如果有 children 或作为分组时使用） |
| `sort` | string | 否 | 排序方式：`ascending`（默认，升序）/ `descending`（降序） |
| `children` | array | 否 | 子节点数组 |

**示例**：

```yaml
project:
  toc:
    - file: index.md
    - title: "博客文章"
      children:
        - pattern: "blog/*.md"
          sort: descending
    - pattern: "appendices/*.md"
```

### 2.4 title 节点（纯分组标题）

创建一个没有对应文件的纯分组标题，用于在导航中创建下拉菜单分组。该节点本身不指向任何页面，仅作为容器组织子节点。

| 字段 | 类型 | 必需 | 说明 |
|---|---|---|---|
| `title` | string | 是 | 分组标题文本 |
| `children` | array | 是 | 子节点数组（分组必须包含 children） |

**示例**：

```yaml
project:
  toc:
    - file: index.md
    - title: "高级主题"
      children:
        - file: advanced/citations.md
        - file: advanced/math.md
        - file: advanced/interactive.md
    - title: "附录"
      children:
        - file: appendices/glossary.md
        - file: appendices/references.md
```

### 2.5 children 字段（子节点嵌套）

`children` 是一个数组，用于定义节点的子节点，从而构建多层级的树状结构。所有节点类型（file/url/pattern/title）都可以拥有 children。

---

## 3. 基础文件列表示例

### 3.1 简单线性 TOC

对于简单的文档项目，可以直接列出文件，按顺序线性排列：

```yaml
project:
  toc:
    - file: index.md
    - file: 01-introduction.md
    - file: 02-installation.md
    - file: 03-getting-started.md
    - file: 04-basic-usage.md
    - file: 05-advanced-topics.md
    - file: 06-faq.md
    - file: references.md
```

### 3.2 路径写法说明

- **相对路径**：所有 `file` 路径均相对于**项目根目录**（即 `myst.yml` 所在目录），不是相对于当前文件
- **扩展名**：可以省略 `.md` 或 `.ipynb` 扩展名，MyST 会自动识别
- **斜杠方向**：Windows 系统也使用正斜杠 `/` 作为路径分隔符（跨平台兼容）
- **索引文件**：`index.md` 通常作为第一个节点，代表网站首页

**推荐写法**：

```yaml
# 推荐：省略扩展名，使用正斜杠
- file: chapters/01-intro
- file: chapters/02-methods

# 也可以写完整路径
- file: chapters/01-intro.md
- file: notebooks/results.ipynb
```

---

## 4. 嵌套页面和下拉菜单

### 4.1 使用 children 嵌套子页面

通过 `children` 字段可以创建页面层级，父页面可以包含子页面，在导航中显示为可展开/折叠的树状结构：

```yaml
project:
  toc:
    - file: index.md
      title: "首页"
    - file: guide/index.md
      title: "用户指南"
      children:
        - file: guide/installation.md
        - file: guide/quickstart.md
        - file: guide/basics.md
          children:
            - file: guide/basics/syntax.md
            - file: guide/basics/frontmatter.md
            - file: guide/basics/toc.md
        - file: guide/advanced.md
    - file: api/index.md
      title: "API 参考"
      children:
        - file: api/cli.md
        - file: api/python-api.md
```

上述配置创建了三级结构：
- 一级：首页、用户指南、API 参考
- 二级：用户指南下的安装、快速开始、基础、高级
- 三级：基础下的语法、Frontmatter、TOC

### 4.2 title + children 创建无父文件的下拉分组

使用 `title` 节点创建不对应任何文件的纯分组，在导航中显示为下拉菜单，点击展开子项：

```yaml
project:
  toc:
    - file: index.md
    - title: "学习资源"
      children:
        - file: resources/tutorials.md
        - file: resources/examples.md
        - file: resources/videos.md
    - title: "社区"
      children:
        - url: "https://github.com/example/discussions"
          title: "讨论区"
        - url: "https://discord.gg/example"
          title: "Discord 聊天"
        - file: community/contributing.md
          title: "贡献指南"
```

### 4.3 2-3 层嵌套结构示例

这是一个书籍/教程类项目的典型 TOC 结构：

```yaml
project:
  toc:
    # 第一部分：首页
    - file: index.md
      title: "封面"
    - file: preface.md
      title: "前言"
    
    # 第一部分：入门
    - title: "第一部分：入门"
      children:
        - file: part1/01-what-is-myst.md
          title: "第 1 章：什么是 MyST"
        - file: part1/02-installation.md
          title: "第 2 章：安装与配置"
          children:
            - file: part1/install/windows.md
              title: "Windows 安装"
            - file: part1/install/mac.md
              title: "macOS 安装"
            - file: part1/install/linux.md
              title: "Linux 安装"
        - file: part1/03-first-document.md
          title: "第 3 章：创建第一个文档"
    
    # 第二部分：核心功能
    - title: "第二部分：核心功能"
      children:
        - file: part2/04-syntax.md
          title: "第 4 章：MyST 语法"
        - file: part2/05-frontmatter.md
          title: "第 5 章：Frontmatter 配置"
        - file: part2/06-toc.md
          title: "第 6 章：目录结构"
        - file: part2/07-citations.md
          title: "第 7 章：引用与参考文献"
          children:
            - file: part2/citations/bibtex.md
            - file: part2/citations/cross-refs.md
    
    # 附录
    - title: "附录"
      children:
        - file: appendix/faq.md
        - file: appendix/changelog.md
        - file: appendix/glossary.md
```

---

## 5. Glob 模式匹配

### 5.1 pattern 字段基本用法

`pattern` 字段使用标准 Glob 语法批量匹配文件，避免逐个列出文件：

| Glob 模式 | 说明 |
|---|---|
| `*.md` | 匹配当前目录下所有 `.md` 文件 |
| `chapters/*.md` | 匹配 `chapters/` 目录下的 `.md` 文件（不递归子目录） |
| `chapters/**/*.md` | 递归匹配 `chapters/` 及其所有子目录下的 `.md` 文件 |
| `blog/*.{md,ipynb}` | 匹配 `blog/` 下的 `.md` 和 `.ipynb` 文件 |
| `**/index.md` | 匹配所有目录下的 `index.md` 文件 |

**示例：自动包含 chapters 目录下的所有章节**：

```yaml
project:
  toc:
    - file: index.md
    - title: "章节"
      children:
        - pattern: "chapters/*.md"
    - file: references.md
```

### 5.2 sort 排序选项

通过 `sort` 字段控制匹配文件的排序方式：

- `ascending`（默认）：字母/数字升序排列，适合章节、教程等
- `descending`：字母/数字降序排列，适合博客文章（最新文章在前）

**示例：博客文章按日期倒序**

```yaml
project:
  toc:
    - file: index.md
    - file: about.md
    - title: "博客"
      children:
        - file: blog/index.md
          title: "博客首页"
        - pattern: "blog/posts/*.md"
          sort: descending
```

假设文件命名为 `2024-01-15-hello.md`、`2024-02-20-new-release.md`、`2024-03-10-tutorial.md`，使用 `sort: descending` 会按最新到最旧排列。

### 5.3 显式文件优先与去重

- **显式列出的文件不会被 pattern 重复包含**：如果一个文件已经在 TOC 中显式列出，即使它匹配 pattern 也不会重复出现
- **显式文件优先级更高**：显式列出的位置决定了文件的最终位置，pattern 匹配到的同一文件会被忽略

**示例**：

```yaml
project:
  toc:
    - file: index.md
    - file: chapters/first-chapter.md  # 显式列出，放在最前面
    - pattern: "chapters/*.md"         # 匹配其他章节，不会重复包含 first-chapter.md
```

在这个例子中，`chapters/first-chapter.md` 会出现在第二个位置，其他章节按字母顺序跟在后面，不会重复。

### 5.4 文件夹结构保留规则

使用 `**` 递归匹配时，MyST 会根据文件夹结构自动创建嵌套层级吗？

- 默认情况下，`pattern: "chapters/**/*.md"` 会**打平**所有匹配的文件，不自动创建分组
- 如需保留目录结构，可以使用多个 pattern 分别匹配子目录，或显式定义嵌套结构

**示例：手动保留目录结构**：

```yaml
project:
  toc:
    - file: index.md
    - title: "章节"
      children:
        - pattern: "chapters/*.md"
        - title: "进阶"
          children:
            - pattern: "chapters/advanced/*.md"
        - title: "案例"
          children:
            - pattern: "chapters/cases/*.md"
```

### 5.5 Glob 模式综合示例

```yaml
project:
  toc:
    # 首页
    - file: index.md
    
    # 文档（手动控制顺序）
    - file: docs/introduction.md
    - file: docs/installation.md
    - file: docs/quickstart.md
    
    # 指南（自动扫描）
    - title: "用户指南"
      children:
        - pattern: "docs/guides/*.md"
    
    # 教程 Notebooks（自动扫描）
    - title: "教程"
      children:
        - pattern: "tutorials/*.ipynb"
    
    # 博客文章（按日期倒序）
    - title: "博客"
      children:
        - file: blog/index.md
          title: "全部文章"
        - pattern: "blog/posts/*.md"
          sort: descending
    
    # 外部资源
    - url: "https://github.com/example/project"
      title: "GitHub"
    - file: changelog.md
```

---

## 6. 页面标题配置

### 6.1 标题来源优先级

MyST 按照以下优先级决定页面在导航中显示的标题（从高到低）：

1. **TOC 中的 `title` 字段**：在 `myst.yml` 的 TOC 节点中显式指定的 `title`
2. **页面的 `short_title` 字段**：页面 Frontmatter 中的 `short_title`
3. **页面的 `title` 字段**：页面 Frontmatter 中的 `title`
4. **第一个 Markdown 一级标题**：页面正文中的第一个 `# 标题`
5. **文件名**：如果以上都没有，使用文件名（去除扩展名和序号前缀）

**优先级示例**：

```yaml
# myst.yml 中的配置
project:
  toc:
    - file: chapters/01-intro.md
      title: "入门指南"  # 优先级最高，会覆盖页面内的任何标题设置
```

即使 `chapters/01-intro.md` 中设置了 `title: "引言"`，导航中仍会显示"入门指南"。

### 6.2 在 TOC 中覆盖页面标题

在 TOC 中指定 `title` 是最灵活的标题控制方式，可以在不同位置给同一页面不同的标题（虽然不常见，但在导出场景中有用）：

```yaml
project:
  toc:
    - file: index.md
      title: "首页"
    - file: guide/getting-started.md
      title: "快速入门"  # 覆盖页面本身的标题
    - title: "参考资料"
      children:
        - file: guide/getting-started.md
          title: "新手入门教程"  # 同一页面在不同位置显示不同标题
        - file: reference/api.md
```

### 6.3 short_title 短标题

`short_title` 用于导航栏、面包屑、移动端菜单等空间有限的位置，建议不超过 10-15 个字符：

```yaml
project:
  toc:
    - file: chapters/01-introduction-to-myst-markdown.md
      title: "第 1 章：MyST Markdown 简介"
      short_title: "简介"  # 在窄屏导航中显示这个
    - file: chapters/02-installation-and-configuration.md
      title: "第 2 章：安装与配置指南"
      short_title: "安装"
```

页面 Frontmatter 中也可以设置 `short_title`，在 TOC 未指定时作为 fallback：

```yaml
---
title: "第 1 章：MyST Markdown 简介"
short_title: "简介"
---
```

---

## 7. 隐藏页面（hidden: true）

### 7.1 hidden 字段作用

使用 `hidden: true` 标记的页面会被正常构建（生成 HTML、可被交叉引用），但**不会出现在导航菜单**中。

| 特性 | 普通页面 | hidden 页面 |
|---|---|---|
| 构建输出 | ✅ 生成 HTML | ✅ 生成 HTML |
| 导航栏显示 | ✅ 显示 | ❌ 不显示 |
| 侧边栏显示 | ✅ 显示 | ❌ 不显示 |
| 交叉引用 | ✅ 可引用 | ✅ 可引用 |
| 直接 URL 访问 | ✅ 可访问 | ✅ 可访问 |
| 上/下一页导航 | ✅ 有 | ⚠️ 取决于位置 |

### 7.2 使用场景

`hidden: true` 适用于以下场景：

- **致谢页**（Acknowledgements）
- **参考文献页**（如果单独成页但不需要主导航入口）
- **附录中的细节内容**
- **着陆页/营销页**（希望用户通过特定链接访问而不是浏览导航）
- **草稿页/未完成页**（暂时发布但不希望出现在导航中）
- **404 页面**、**搜索页面**等功能页

### 7.3 隐藏页面仍可被交叉引用

隐藏页面仍然可以通过 MyST 的交叉引用语法正常引用：

```markdown
请参阅 [](acknowledgements.md) 了解致谢名单。
```

点击链接仍然可以正常跳转到隐藏页面。

### 7.4 隐藏页面示例

```yaml
project:
  toc:
    - file: index.md
    - file: chapters/01-intro.md
    - file: chapters/02-methods.md
    - file: chapters/03-results.md
    - file: chapters/04-discussion.md
    
    # 以下页面不显示在导航中，但可通过链接访问
    - file: acknowledgements.md
      hidden: true
      title: "致谢"
    - file: supplementary-materials.md
      hidden: true
      title: "补充材料"
    - file: raw-data.md
      hidden: true
    - file: 404.md
      hidden: true
```

---

## 8. 页面内 TOC 指令（{toc} directive）

### 8.1 什么是 {toc} 指令

除了站点级的导航 TOC，MyST 还提供了 `{toc}` 指令，可以在**页面内部**动态生成目录内容。这对于在首页生成站点地图、在章节页生成子章节列表、在长文开头生成本文目录等场景非常有用。

基本语法：

````markdown
```{toc}
:context: <context-type>
:depth: <number>
```
````

### 8.2 :context: 参数详解

`:context:` 参数控制 TOC 生成的范围，有四个可选值：

| context 值 | 说明 |
|---|---|
| `section` | 列出当前章节的子标题（从指令所在位置开始，向下查找同级/下级标题） |
| `page` | 列出当前页面的所有标题（生成当前页面的目录） |
| `children` | 列出当前页面在站点 TOC 中的直接子页面 |
| `project` | 列出整个项目的完整 TOC 结构（站点地图） |

### 8.3 :depth: 参数

`:depth:` 参数控制显示的目录深度，为正整数：

- `:depth: 1`：只显示一级
- `:depth: 2`：显示到二级（默认值）
- `:depth: 3`：显示到三级
- 以此类推

### 8.4 各种 context 的示例

#### 示例 1：context: page — 生成本文目录

在长文章开头插入页面内目录：

````markdown
# 第 3 章：高级配置

本文将介绍以下内容：

```{toc}
:context: page
:depth: 2
```

## 3.1 环境变量配置
...

## 3.2 多环境部署
...

### 3.2.1 开发环境
...

### 3.2.2 生产环境
...
```
````

效果：显示从"3.1 环境变量配置"开始的所有标题，直到二级。

#### 示例 2：context: section — 列出当前章节的小节

在章节简介中列出本章小节：

````markdown
# 第一部分：基础入门

本部分包含以下章节：

```{toc}
:context: section
:depth: 1
```

## 第 1 章：什么是 MyST
...

## 第 2 章：安装
...

## 第 3 章：快速开始
...
```
````

#### 示例 3：context: children — 列出子页面

在一个"父页面"上列出其所有子页面（类似 Jupyter Book 的 `{tableofcontents}` 行为）：

````markdown
# 用户指南

本指南包含以下主题：

```{toc}
:context: children
:depth: 1
```
````

假设 `guide/index.md` 在 TOC 中有以下子页面：

```yaml
- file: guide/index.md
  title: "用户指南"
  children:
    - file: guide/installation.md
    - file: guide/quickstart.md
    - file: guide/syntax.md
    - file: guide/configuration.md
```

那么 `{toc}` 指令会自动生成这四个子页面的列表，带链接。

#### 示例 4：context: project — 生成完整站点地图

在首页或"目录页"生成整个项目的目录树：

````markdown
# 目录

```{toc}
:context: project
:depth: 3
```
````

### 8.5 {toc} 指令组合使用

可以在同一页面使用多个 `{toc}` 指令实现不同效果：

````markdown
# MyST Markdown 完整指南

## 本文内容

```{toc}
:context: page
:depth: 2
```

## 文档结构

```{toc}
:context: children
```

---

（正文开始）
```
````

---

## 9. URL Slug 规则

### 9.1 什么是 Slug

Slug 是页面 URL 中可理解的部分，用于生成人类可读、SEO 友好的 URL 地址。例如：

- 文件：`chapters/01_introduction.md`
- Slug：`introduction`
- URL：`https://example.com/introduction`

### 9.2 Slug 生成步骤

MyST 按照以下步骤从文件路径生成 Slug：

1. **去除数字前缀**：去除开头的序号前缀（如 `01_`、`02-`、`chapter1_`）
2. **非 URL 字符转横杠**：将下划线 `_`、空格、其他非字母数字字符替换为横杠 `-`
3. **转为小写**：所有字母转为小写
4. **去除扩展名**：去掉 `.md`/`.ipynb` 扩展名
5. **截断到 50 字符**：如果过长，截断到 50 个字符（在词边界处截断）
6. **合并连续横杠**：多个连续横杠合并为一个
7. **去除首尾横杠**：去掉开头和结尾的横杠

### 9.3 Slug 转换示例

| 文件路径 | 生成的 Slug | 说明 |
|---|---|---|
| `index.md` | `/` | 首页是根路径 |
| `01_my_article.md` | `my-article` | 去除前缀和下划线 |
| `folder1/folder2/01_my_article.md` | `my-article` | 默认不保留文件夹路径 |
| `HelloWorld.md` | `hello-world` | 驼峰转横杠（通过非字母字符规则） |
| `chapter10_advanced-topics.md` | `advanced-topics` | 去除数字前缀 |
| `my_very_long_filename_that_exceeds_fifty_characters.md` | `my-very-long-filename-that-exceeds` | 截断到 50 字符 |
| `notebooks/Analysis_Results.ipynb` | `analysis-results` | 同样适用于 ipynb |

### 9.4 重复 Slug 自动加后缀

如果多个文件生成了相同的 Slug，MyST 会自动添加数字后缀避免冲突：

- `chapters/intro.md` → `intro`
- `appendix/intro.md` → `intro-1`
- `misc/intro.md` → `intro-2`

### 9.5 folders 选项：保留文件夹结构

默认情况下，Slug 只使用文件名，不包含文件夹路径。如果希望保留文件夹结构以组织 URL，需要在 `site` 配置中设置 `folders: true`：

```yaml
site:
  folders: true  # 保留文件夹结构
```

启用后，前面的例子会变成：

| 文件路径 | Slug（folders: false，默认） | Slug（folders: true） |
|---|---|---|
| `folder1/folder2/01_my_article.md` | `my-article` | `folder1/folder2/my-article` |

这对于大型项目中保持 URL 结构清晰很有用。

---

## 10. 隐式 TOC 规则（无显式配置时）

如果不在 `myst.yml` 中配置 `project.toc`，MyST 会自动扫描文件系统生成隐式 TOC。了解这些规则有助于理解默认行为。

### 10.1 自动扫描的文件类型

MyST 会自动扫描项目目录下的以下文件：

- `.md`：Markdown 文件
- `.ipynb`：Jupyter Notebook 文件
- `.myst.md`：MyST 专用扩展名（可选）

### 10.2 排序规则

扫描到的文件按以下规则排序：

1. **字母排序 + 数字自然排序**：使用自然排序（natural sort），确保 `chapter10` 排在 `chapter9` 之后，而不是按字符串排序 `chapter10` 在 `chapter2` 前面
   - ✅ 正确顺序：`chapter1.md` → `chapter2.md` → ... → `chapter9.md` → `chapter10.md`
   - ❌ 字符串排序：`chapter1.md` → `chapter10.md` → `chapter2.md` → ...
2. **索引文件优先**：根目录的 `index.md`/`README.md`/`main.md` 始终排在最前面
3. **子目录文件**：子目录中的文件会出现在父目录文件之后（按目录名排序）

### 10.3 自动忽略的目录

以下目录中的文件会被自动忽略，不会出现在隐式 TOC 中：

- `.git/`：Git 版本控制目录
- `_build/`：MyST 构建输出目录
- `node_modules/`：Node.js 依赖目录
- `__pycache__/`：Python 缓存目录
- `.venv/`、`venv/`：Python 虚拟环境
- 以 `.` 开头的隐藏目录（如 `.github/`、`.vscode/` 等）
- `site-packages/`、`.tox/` 等构建/测试目录

### 10.4 Root 页面选择优先级

MyST 按以下优先级选择根页面（首页）：

1. **`index.md`**（最高优先级）
2. **`README.md`**
3. **`main.md`**
4. 按排序找到的第一个文件（如果以上都不存在）

找到根页面后，其余文件按排序规则排列。

### 10.5 隐式 TOC 的局限性

隐式 TOC 虽然方便，但有以下局限性：

- ❌ 无法控制页面的精确顺序（只能按文件名字母排序）
- ❌ 无法创建嵌套/分组结构
- ❌ 无法添加外部链接
- ❌ 无法覆盖页面标题
- ❌ 无法隐藏页面
- ❌ 无法使用 Glob 模式的高级排序

因此，**对于正式项目，建议显式配置 `project.toc`**。

---

## 11. 与 Jupyter Book v1 的兼容性说明

### 11.1 读取旧版 _toc.yml

MySTmd 可以读取 Jupyter Book v1 风格的 `_toc.yml` 文件，无需立即迁移。如果项目中存在 `_toc.yml`，MyST 会自动识别并使用它。

**Jupyter Book v1 `_toc.yml` 示例**：

```yaml
format: jb-book
root: index
chapters:
  - file: 01-intro
  - file: 02-install
  - file: 03-getting-started
    sections:
      - file: 03.1-first-notebook
      - file: 03.2-markdown
  - file: references
```

### 11.2 主要差异

| 特性 | Jupyter Book v1 (_toc.yml) | MySTmd (myst.yml project.toc) |
|---|---|---|
| 配置文件 | `_toc.yml`（独立文件） | `myst.yml` 的 `project.toc` 字段 |
| 根节点 | `root: index` 单独指定 | 第一个 `file: index.md` 节点 |
| 章节字段 | `chapters:` | 直接是 TOC 数组 |
| 子章节 | `sections:` | `children:` |
| 分组标题 | 不支持（需要用 caption） | `title:` 节点（直接支持） |
| 外部链接 | `url:` 但支持有限 | 原生支持，有 `open_in_same_tab` |
| Glob 模式 | `glob:` | `pattern:` 字段 |
| 隐藏页面 | 不支持 | `hidden: true` |
| 短标题 | 不支持 | `short_title:` |

### 11.3 迁移提示

从 Jupyter Book v1 迁移到 MySTmd TOC：

1. 将 `root: index` 移到数组第一个位置，改为 `- file: index.md`
2. 将 `chapters:` 下的项直接作为数组元素
3. 将 `sections:` 改为 `children:`
4. 将 `glob:` 改为 `pattern:`
5. 在 `myst.yml` 的 `project.toc` 下配置

**迁移示例**：

**旧版（_toc.yml）**：
```yaml
format: jb-book
root: intro
chapters:
  - file: 01-getting-started
  - file: 02-theory
    sections:
      - file: 02.1-markov
      - file: 02.2-common
  - glob: 03-*/
  - file: references
```

**新版（myst.yml）**：
```yaml
project:
  toc:
    - file: intro.md
    - file: 01-getting-started.md
    - file: 02-theory.md
      children:
        - file: 02.1-markov.md
        - file: 02.2-common.md
    - pattern: "03-*"
    - file: references.md
```

---

## 12. 完整 TOC 配置示例

以下是一个完整的技术书籍项目 TOC 配置，综合展示了所有节点类型和功能：

```yaml
version: 1

project:
  title: "MyST Markdown 权威指南"
  subtitle: "从入门到精通"
  authors:
    - name: "MyST 社区"
  github: "https://github.com/example/myst-book"
  
  # ========== 完整 TOC 配置 ==========
  toc:
    # ---------- 首页与前言 ----------
    - file: index.md
      title: "封面"
      short_title: "封面"
    - file: foreword.md
      title: "推荐序"
      hidden: true
    - file: preface.md
      title: "前言"
    - file: about.md
      title: "关于本书"
    - file: acknowledgements.md
      title: "致谢"
      hidden: true
    
    # ---------- 第一部分：入门 ----------
    - title: "第一部分：开始使用"
      children:
        - file: part1/01-what-is-myst.md
          title: "第 1 章：什么是 MyST"
          short_title: "MyST 简介"
        - file: part1/02-installation.md
          title: "第 2 章：安装与配置"
          children:
            - file: part1/install/windows.md
              title: "2.1 Windows 环境安装"
            - file: part1/install/macos.md
              title: "2.2 macOS 环境安装"
            - file: part1/install/linux.md
              title: "2.3 Linux 环境安装"
            - file: part1/install/docker.md
              title: "2.4 Docker 方式使用"
              hidden: true
        - file: part1/03-quickstart.md
          title: "第 3 章：快速上手"
        - file: part1/04-project-structure.md
          title: "第 4 章：项目结构"
    
    # ---------- 第二部分：核心语法 ----------
    - title: "第二部分：核心语法"
      children:
        - file: part2/05-basic-syntax.md
          title: "第 5 章：基础 Markdown 语法"
        - file: part2/06-myst-extensions.md
          title: "第 6 章：MyST 扩展语法"
          children:
            - file: part2/syntax/roles.md
              title: "6.1 角色（Roles）"
            - file: part2/syntax/directives.md
              title: "6.2 指令（Directives）"
            - file: part2/syntax/admonitions.md
              title: "6.3 提示框"
            - file: part2/syntax/figures.md
              title: "6.4 图表"
            - file: part2/syntax/tables.md
              title: "6.5 表格"
            - file: part2/syntax/math.md
              title: "6.6 数学公式"
        - file: part2/07-frontmatter.md
          title: "第 7 章：Frontmatter 元数据"
        - file: part2/08-toc.md
          title: "第 8 章：目录结构配置"
        - file: part2/09-cross-references.md
          title: "第 9 章：交叉引用"
        - file: part2/10-citations.md
          title: "第 10 章：引用与参考文献"
    
    # ---------- 第三部分：进阶功能（自动扫描）----------
    - title: "第三部分：进阶功能"
      children:
        - file: part3/index.md
          title: "第三部分概述"
        # 自动扫描 advanced 目录下所有章节
        - pattern: "part3/topics/*.md"
        # Jupyter 交互相关
        - title: "交互式计算"
          children:
            - pattern: "part3/jupyter/*.ipynb"
    
    # ---------- 第四部分：导出与出版 ----------
    - title: "第四部分：导出与出版"
      children:
        - file: part4/11-exports.md
          title: "第 11 章：多格式导出"
        - file: part4/12-pdf.md
          title: "12.1 PDF 导出"
        - file: part4/12-docx.md
          title: "12.2 Word 文档导出"
        - file: part4/12-latex.md
          title: "12.3 LaTeX 导出"
          hidden: true
        - file: part4/13-web-publishing.md
          title: "第 13 章：网站发布"
        - file: part4/14-themes.md
          title: "第 14 章：主题定制"
    
    # ---------- 教程与案例 ----------
    - title: "教程与案例"
      children:
        - file: tutorials/index.md
          title: "教程首页"
        # 教程 Notebooks 按文件名排序
        - pattern: "tutorials/notebooks/*.ipynb"
        # 博客文章按日期倒序
        - title: "博客文章"
          children:
            - file: tutorials/blog/index.md
              title: "博客首页"
            - pattern: "tutorials/blog/posts/*.md"
              sort: descending
    
    # ---------- 参考资料 ----------
    - title: "参考资料"
      children:
        - file: reference/faq.md
          title: "常见问题"
        - file: reference/glossary.md
          title: "术语表"
        - file: reference/cli.md
          title: "命令行参考"
        - file: reference/api.md
          title: "Python API"
          hidden: true
        - file: reference/changelog.md
          title: "更新日志"
        - file: reference/migration-guide.md
          title: "迁移指南"
          hidden: true
    
    # ---------- 附录（部分隐藏）----------
    - title: "附录"
      children:
        - file: appendix/quick-reference.md
          title: "快速参考卡"
        - file: appendix/syntax-cheatsheet.md
          title: "语法速查表"
        - file: appendix/templates.md
          title: "模板集合"
          hidden: true
        - file: appendix/supplementary-data.md
          title: "补充数据"
          hidden: true
    
    # ---------- 外部资源 ----------
    - url: "https://mystmd.org"
      title: "MyST 官网"
    - url: "https://github.com/executablebooks/mystmd"
      title: "GitHub 仓库"
    - url: "https://mystmd.org/guide"
      title: "官方文档（英文）"
      open_in_same_tab: false
    - url: "https://jupyterbook.org"
      title: "Jupyter Book"

# ========== 网站配置 ==========
site:
  template: book-theme
  title: "MyST Markdown 权威指南"
  # folders: true  # 如需保留 URL 文件夹结构，取消注释
  options:
    logo: images/logo.png
    logo_text: "MyST Guide"
  nav:
    - title: "首页"
      url: /
    - title: "GitHub"
      url: https://github.com/example/myst-book
      external: true
```

---

## 参考资料

- MyST Table of Contents 官方文档：https://mystmd.org/guide/table-of-contents
- MyST Configuration 配置文档：https://mystmd.org/guide/configuration
- MyST Frontmatter 配置：03-frontmatter-config.md
- MyST 项目结构：02-project-structure.md
