---
source: "https://mystmd.org/guide/frontmatter"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/executablebooks-myst-guide/03-frontmatter-config.toml"
id: "executablebooks-myst-guide-frontmatter-config"
title: "Frontmatter 配置详解"
---
# Frontmatter 配置详解

本文档详细介绍 MyST Markdown 的 Frontmatter（元数据）配置，包括页面级和项目级元数据的字段说明、作用范围、常用配置和完整示例。

---

## 1. Frontmatter 概述

### 1.1 什么是 Frontmatter

Frontmatter 是位于文档开头的 YAML 元数据块，使用 `---` 包裹，用于定义文档的标题、作者、日期、引用、导出选项等元信息。MyST 解析器会在处理 Markdown 内容前首先读取这些元数据，用于生成页面标题、导航、引用、导出等功能。

基本格式：

```yaml
---
title: "我的第一篇 MyST 文档"
author: "张三"
date: 2024-01-15
---

文档正文内容从这里开始...
```

### 1.2 两种配置位置

Frontmatter 可以在两个位置配置，具有不同的作用范围：

| 位置 | 说明 | 作用范围 |
|---|---|---|
| **页面级** | 每个 `.md`/`.ipynb` 文件开头的 `---` 块 | 仅对当前页面生效 |
| **项目级** | `myst.yml` 配置文件中的 `project:` 块 | 对整个项目生效，页面可覆盖 |

### 1.3 作用范围分类

根据字段的作用范围，可分为以下四类：

| 分类 | 说明 |
|---|---|
| **page only** | 仅在页面 Frontmatter 中有效，项目级配置无效 |
| **project only** | 仅在 `myst.yml` 的 `project:` 块中有效 |
| **page & project** | 两处均可配置，页面级和项目级配置会合并 |
| **page can override project** | 页面配置优先级高于项目配置，页面可覆盖项目默认值 |

### 1.4 标题自动提取规则

如果页面 Frontmatter 中未显式指定 `title` 字段，MyST 会按以下规则自动提取：

1. 查找文档中第一个 Markdown 一级标题（`# 标题`）
2. 如果没有一级标题，使用文件名（去除扩展名和序号前缀）作为标题
3. 自动提取的标题仅作为 fallback，建议显式配置以获得更准确的结果

---

## 2. 基础元数据字段

### 2.1 标题相关字段

| 字段 | 类型 | 作用范围 | 说明 |
|---|---|---|---|
| `title` | string | page & project | 文档/项目的完整标题，显示在页面标题、导航、导出文档封面等位置 |
| `subtitle` | string | page & project | 副标题，显示在主标题下方，用于补充说明 |
| `short_title` | string | page & project | 短标题，用于导航栏、面包屑等空间有限的位置，建议不超过 20 字符 |

示例：

```yaml
---
title: "MyST Markdown 完整指南：从入门到精通"
subtitle: "面向科学写作的现代 Markdown 工具"
short_title: "MyST 指南"
---
```

### 2.2 描述与关键词

| 字段 | 类型 | 作用范围 | 说明 |
|---|---|---|---|
| `description` | string | page & project | 文档描述，用于 HTML meta 标签、SEO、搜索结果摘要，建议不超过 500 字符 |
| `keywords` | string[] | page & project | 关键词列表，用于 SEO 和分类 |
| `tags` | string[] | page & project | 标签列表，用于内容分类和筛选，比 keywords 更面向内容组织 |

示例：

```yaml
---
description: "一份全面的 MyST Markdown 学习指南，涵盖语法、配置、导出和科学出版功能，适合学术写作者和技术文档作者。"
keywords:
  - MyST
  - Markdown
  - 科学写作
  - Jupyter
  - 可复现研究
tags:
  - 入门指南
  - 技术文档
  - 学术出版
---
```

### 2.3 日期与图片

| 字段 | 类型 | 作用范围 | 说明 |
|---|---|---|---|
| `date` | string | page & project | 文档日期，支持 ISO 8601（`2024-01-15` 或 `2024-01-15T10:30:00Z`）和 RFC 2822（`Mon, 15 Jan 2024 10:30:00 +0800`）格式 |
| `thumbnail` | string | page & project | 缩略图路径，用于社交分享、列表预览等场景 |
| `banner` | string | page & project | 横幅图路径，显示在页面顶部作为标题背景 |

示例：

```yaml
---
date: 2024-01-15
thumbnail: images/thumbnail.png
banner: images/banner.jpg
---
```

---

## 3. 作者与机构配置

### 3.1 authors 数组（作者信息）

`authors` 是一个数组，每个元素是一个作者对象，支持丰富的字段配置。

| 字段 | 类型 | 说明 |
|---|---|---|
| `name` | string | 作者全名（**必需**） |
| `id` | string | 作者唯一标识符，用于在文档中交叉引用 |
| `orcid` | string | ORCID 标识符（格式：`0000-0000-0000-0000`），学术作者的唯一身份标识 |
| `corresponding` | boolean | 是否为通讯作者，默认 `false` |
| `email` | string | 作者邮箱，通讯作者建议配置 |
| `roles` | string[] | CRediT 贡献者角色列表，说明作者在项目中的具体贡献 |
| `equal_contributor` | boolean | 是否为共同第一作者，默认 `false` |
| `deceased` | boolean | 作者是否已故，默认 `false` |
| `note` | string | 作者备注信息，如 "当前单位：XXX" |
| `affiliations` | string[] | 关联机构的 `id` 列表或机构名称列表 |
| `url` | string | 作者个人主页 URL |
| `github` | string | GitHub 用户名 |
| `twitter` | string | Twitter/X 用户名 |
| `linkedin` | string | LinkedIn 用户名 |

**CRediT 贡献者角色**（常用值）：

- `Conceptualization`：概念构思
- `Data curation`：数据整理
- `Formal analysis`：形式分析
- `Funding acquisition`：经费获取
- `Investigation`：研究调查
- `Methodology`：研究方法
- `Project administration`：项目管理
- `Resources`：资源提供
- `Software`：软件开发
- `Supervision`：指导监督
- `Validation`：验证
- `Visualization`：可视化
- `Writing – original draft`：初稿撰写
- `Writing – review & editing`：审阅与编辑

### 3.2 affiliations 数组（机构信息）

`affiliations` 是一个数组，每个元素是一个机构对象。

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | string | 机构唯一标识符，用于在 `authors[].affiliations` 中引用 |
| `name` | string | 机构全称（**必需**） |
| `institution` | string | 所属机构（如大学、研究所名称） |
| `department` | string | 院系/部门名称 |
| `doi` | string | 机构的 DOI 标识符 |
| `ror` | string | Research Organization Registry 标识符 |
| `isni` | string | International Standard Name Identifier |
| `ringgold` | string | Ringgold 机构标识符 |
| `address` | string | 街道地址 |
| `city` | string | 城市 |
| `state` | string | 省/州 |
| `country` | string | 国家 |
| `postal_code` | string | 邮政编码 |
| `email` | string | 机构联系邮箱 |
| `url` | string | 机构网站 URL |

### 3.3 reviewers / editors（评审与编辑）

| 字段 | 类型 | 作用范围 | 说明 |
|---|---|---|---|
| `reviewers` | list[] | page & project | 评审者列表，格式同 authors |
| `editors` | list[] | page & project | 编辑列表，格式同 authors |

### 3.4 作者配置示例

```yaml
---
authors:
  - id: author1
    name: "张三"
    orcid: "0000-0001-2345-6789"
    corresponding: true
    email: "zhangsan@example.edu.cn"
    equal_contributor: true
    roles:
      - Conceptualization
      - Methodology
      - Writing – original draft
    affiliations:
      - aff1
      - aff2
    github: "zhangsan"
    url: "https://zhangsan.example.com"
  - id: author2
    name: "李四"
    orcid: "0000-0002-3456-7890"
    equal_contributor: true
    roles:
      - Software
      - Validation
      - Visualization
    affiliations:
      - aff2
    note: "当前工作单位：某科技公司"
affiliations:
  - id: aff1
    name: "某大学计算机科学与技术系"
    institution: "某大学"
    department: "计算机科学与技术系"
    city: "北京"
    country: "中国"
    postal_code: "100084"
  - id: aff2
    name: "某国家重点实验室"
    institution: "某研究院"
    city: "上海"
    country: "中国"
    ror: "https://ror.org/0xxxxxxx"
reviewers:
  - name: "王五"
    affiliations:
      - "某知名大学"
editors:
  - name: "赵六"
    email: "editor@journal.example.com"
---
```

---

## 4. 出版与许可配置

### 4.1 license（许可协议）

`license` 字段支持两种格式：简单字符串或对象。

**简单字符串格式**：

```yaml
---
license: CC-BY-4.0
---
```

**对象格式**（分别指定代码和内容许可）：

```yaml
---
license:
  content: CC-BY-4.0
  code: MIT
---
```

**常用开源许可**：

- `CC-BY-4.0`：Creative Commons Attribution 4.0（推荐用于文档/内容）
- `CC-BY-SA-4.0`：Creative Commons Attribution-ShareAlike 4.0
- `CC0-1.0`：公共领域贡献
- `MIT`：MIT License（推荐用于代码）
- `Apache-2.0`：Apache License 2.0
- `GPL-3.0`：GNU General Public License v3.0
- `BSD-3-Clause`：3-Clause BSD License

### 4.2 版权与学术标识符

| 字段 | 类型 | 作用范围 | 说明 |
|---|---|---|---|
| `copyright` | string | page & project | 版权声明文本，如 `"Copyright 2024 作者姓名"` |
| `doi` | string | page & project | 数字对象标识符（Digital Object Identifier），如 `"10.1000/xyz123"` |
| `arxiv` | string | page & project | arXiv 预印本 ID，如 `"2401.12345"` |
| `pmid` | string | page & project | PubMed ID（生物医学文献） |
| `pmcid` | string | page & project | PubMed Central ID |
| `open_access` | boolean/string | page & project | 开放获取标记，`true` 表示 OA，也可指定 OA 类型如 `"gold"`、`"green"` |

示例：

```yaml
---
copyright: "Copyright 2024 作者团队，保留部分权利"
doi: "10.1234/myst-guide.2024.001"
arxiv: "2401.12345"
open_access: true
---
```

### 4.3 期刊/会议与卷期信息

| 字段 | 类型 | 作用范围 | 说明 |
|---|---|---|---|
| `venue` | string/object | page & project | 期刊或会议名称 |
| `volume` | string/number | page & project | 卷号 |
| `issue` | string/number | page & project | 期号 |
| `first_page` | string/number | page & project | 起始页码 |
| `last_page` | string/number | page & project | 结束页码 |

示例：

```yaml
---
venue:
  title: "第 XX 届学术年会论文集"
  type: conference
  url: "https://conference.example.com"
volume: 12
issue: 3
first_page: 1
last_page: 15
---
```

### 4.4 funding（基金信息）

`funding` 是一个数组，用于记录研究资助信息。

```yaml
---
funding:
  - id: "grant1"
    statement: "本研究由国家自然科学基金（项目编号：12345678）资助"
    funder: "国家自然科学基金委员会"
    award: "12345678"
    doi: "10.13039/501100001809"
    url: "https://www.nsfc.gov.cn"
    recipients:
      - author1
  - statement: "部分工作得到某科技公司的支持"
    funder: "某科技公司"
---
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | string | 基金项目唯一 ID |
| `statement` | string | 基金致谢声明文本 |
| `funder` | string | 资助机构名称 |
| `award` | string | 项目/奖励编号 |
| `doi` | string | 资助机构的 DOI（如 FundRef DOI） |
| `url` | string | 资助项目网页链接 |
| `recipients` | string[] | 受资助作者的 `id` 列表 |

---

## 5. 引用与参考文献

| 字段 | 类型 | 作用范围 | 说明 |
|---|---|---|---|
| `bibliography` | string/string[] | page & project | 参考文献文件路径，支持 BibTeX（`.bib`）、BibLaTeX、CSL-JSON 等格式 |

**bibliography 配置示例**：

```yaml
---
# 单个参考文献文件
bibliography: references.bib

# 多个参考文献文件
bibliography:
  - references/main.bib
  - references/appendix.bib
  - https://example.com/remote-bibliography.bib
---
```

**注意事项**：

1. 路径相对于当前文件所在目录
2. 支持本地文件和远程 URL
3. 多个文件会合并处理
4. 项目级配置的 bibliography 对所有页面生效，页面可添加额外的参考文献文件

---

## 6. 导出配置（exports）

`exports` 是一个数组，定义需要导出的格式、模板和输出路径。**注意：exports 仅在项目级 `myst.yml` 的 `project:` 块中有效**，属于 project only 字段。

### 6.1 exports 字段详解

| 字段 | 类型 | 说明 |
|---|---|---|
| `format` | string | 导出格式（见下方支持格式列表） |
| `template` | string | 模板名称（内置模板或本地模板路径） |
| `output` | string | 输出文件路径（相对于项目根目录） |
| `zip` | boolean | 是否将输出打包为 ZIP 文件，默认 `false` |
| `articles` | string[] | 包含的文章（页面）文件路径列表，按顺序合并 |
| `toc` | boolean/string | 是否使用 `_toc.yml` 定义文档顺序，设置为 `true` 使用项目 TOC，或指定 `_toc.yml` 文件路径 |
| `id` | string | 导出配置的唯一 ID，用于引用 |
| `title` | string | 导出文档标题，覆盖项目/页面标题 |
| `subtitle` | string | 导出文档副标题 |

### 6.2 支持的导出格式

| 格式值 | 说明 |
|---|---|
| `pdf` | PDF 文档（推荐用于正式出版） |
| `tex` | LaTeX 源文件 |
| `pdf+tex` | 同时导出 PDF 和 LaTeX 源文件 |
| `typst` | Typst 源文件（新兴排版语言，编译速度快） |
| `docx` | Microsoft Word 文档（.docx） |
| `md` | Markdown 文件 |
| `jats` | JATS（Journal Article Tag Suite）XML，学术出版标准格式 |
| `meca` | MECA（Manuscript Exchange Common Approach）打包格式 |

### 6.3 导出示例

**示例 1：导出单篇文章为 PDF**

```yaml
project:
  exports:
    - format: pdf
      template: arxiv_two_column
      output: _build/exports/paper.pdf
      articles:
        - paper.md
```

**示例 2：导出整本书籍（使用 TOC）**

```yaml
project:
  exports:
    - format: pdf
      template: book
      output: _build/exports/my-book.pdf
      toc: true
      zip: true
```

**示例 3：多格式导出**

```yaml
project:
  exports:
    # PDF（使用 arXiv 双栏模板）
    - format: pdf
      template: arxiv_two_column
      output: _build/exports/paper.pdf
      articles:
        - index.md
        - methodology.md
        - results.md
        - discussion.md
    
    # Word 文档
    - format: docx
      output: _build/exports/paper.docx
      articles:
        - index.md
    
    # LaTeX 源文件（打包 ZIP）
    - format: tex
      output: _build/exports/latex-source.zip
      zip: true
      articles:
        - index.md
    
    # JATS XML
    - format: jats
      output: _build/exports/paper.xml
      articles:
        - index.md
```

**示例 4：使用本地模板**

```yaml
project:
  exports:
    - format: pdf
      template: templates/my-university-template
      output: _build/exports/thesis.pdf
      toc: true
```

---

## 7. 下载配置（downloads）

`downloads` 是一个数组，定义网站上可供用户下载的文件。

| 字段 | 类型 | 作用范围 | 说明 |
|---|---|---|---|
| `id` | string | page & project | 下载项唯一 ID |
| `file` | string | page & project | 文件路径（相对于项目根目录或 URL） |
| `title` | string | page & project | 下载链接显示的标题文本 |
| `filename` | string | page & project | 下载时建议的文件名 |

**配置示例**：

```yaml
---
downloads:
  - id: download-pdf
    file: _build/exports/paper.pdf
    title: "下载 PDF 版本"
    filename: "my-paper.pdf"
  - id: download-code
    file: https://github.com/example/repo/archive/main.zip
    title: "下载源代码"
    filename: "source-code.zip"
---
```

---

## 8. 其他重要配置

### 8.1 GitHub 集成

| 字段 | 类型 | 作用范围 | 说明 |
|---|---|---|---|
| `github` | string | page & project | GitHub 仓库 URL，如 `"https://github.com/owner/repo"` |
| `edit_url` | string | page & project | 编辑页面的 URL 模板，用于"在 GitHub 上编辑"按钮 |
| `source_url` | string | page & project | 页面源文件的 URL |

示例：

```yaml
project:
  github: "https://github.com/executablebooks/mystmd"
  edit_url: "https://github.com/owner/repo/edit/main/{path}"
```

### 8.2 Binder 配置

`binder` 字段用于配置 Binder 链接，允许用户在浏览器中交互式运行 Notebook。

```yaml
---
binder:
  repo: "owner/repo"
  url: "https://mybinder.org"
  ref: "main"
  provider: "github"
---
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `repo` | string | Binder 仓库地址 |
| `url` | string | Binder 服务 URL，默认 `https://mybinder.org` |
| `ref` | string | Git 分支/标签/提交，默认 `main` |
| `provider` | string | 代码托管平台，支持 `github`、`gitlab`、`gist` |

### 8.3 math（数学宏定义）

`math` 字段用于定义全局 LaTeX 数学宏，避免在每个公式中重复定义。

```yaml
---
math:
  macros:
    "\\RR": "\\mathbb{R}"
    "\\vec": "\\mathbf{#1}"
    "\\diff": "\\mathop{\\mathrm{d}#1}"
---
```

定义后可在文档中直接使用：

```markdown
函数 $f: \RR \to \RR$ 定义为 $f(x) = x^2$。
```

### 8.4 abbreviations（缩写表）

`abbreviations` 定义缩写词，首次出现时自动显示全称。

```yaml
---
abbreviations:
  MyST: "Markedly Structured Text"
  HTML: "HyperText Markup Language"
  API: "Application Programming Interface"
---
```

在文档中使用：

```markdown
MyST 是一种强大的 Markdown 扩展。
```

首次渲染时会显示为 "MyST (Markedly Structured Text)"，后续出现只显示 MyST。

### 8.5 numbering（编号自定义）

`numbering` 自定义章节、图表、公式等的编号方式。

```yaml
---
numbering:
  heading_1: true
  heading_2: true
  heading_3: false
  figure: true
  table: true
  equation: true
  code: false
---
```

### 8.6 jupyter/thebe（Jupyter 执行配置）

配置 Jupyter 代码块的执行和交互式计算：

```yaml
---
jupyter:
  kernel: python3
  execute: false
  binder: true
thebe:
  enable: true
  binder:
    repo: "owner/repo"
    ref: "main"
---
```

| 字段 | 说明 |
|---|---|
| `jupyter.kernel` | Jupyter 内核名称 |
| `jupyter.execute` | 构建时是否执行代码块，`true`/`false`/`"auto"` |
| `thebe.enable` | 是否启用 Thebe（浏览器内交互式执行） |

### 8.7 references（Intersphinx 外部引用）

`references` 配置 Intersphinx 映射，用于跨项目引用其他 Sphinx/MyST 文档的对象。

```yaml
project:
  references:
    python:
      url: "https://docs.python.org/3"
    numpy:
      url: "https://numpy.org/doc/stable/"
    myst:
      url: "https://mystmd.org/guide"
```

配置后可使用标准引用语法链接到外部文档：

```markdown
请参阅 {external:py:class}`list` 了解更多信息。
```

---

## 9. 完整 Frontmatter 示例

### 9.1 页面级 Frontmatter 完整示例

```yaml
---
# ========== 标题与描述 ==========
title: "基于 MyST Markdown 的学术论文写作指南"
subtitle: "从草稿到投稿的完整流程"
short_title: "MyST 学术写作"
description: "本文详细介绍如何使用 MyST Markdown 撰写学术论文，包括元数据配置、参考文献管理、图表插入、多格式导出等功能，帮助作者高效完成学术写作。"
date: 2024-01-15
thumbnail: images/thumbnail.png
banner: images/banner.jpg

# ========== 关键词与标签 ==========
keywords:
  - MyST Markdown
  - 学术写作
  - 科学出版
  - 可复现研究
  - Jupyter
tags:
  - 指南
  - 学术出版
  - 工具教程

# ========== 作者信息 ==========
authors:
  - id: zhangsan
    name: "张三"
    orcid: "0000-0001-2345-6789"
    corresponding: true
    email: "zhangsan@university.edu.cn"
    equal_contributor: true
    roles:
      - Conceptualization
      - Writing – original draft
      - Funding acquisition
    affiliations:
      - cs-dep
      - ai-lab
    github: "zhangsan"
  - id: lisi
    name: "李四"
    orcid: "0000-0002-3456-7890"
    equal_contributor: true
    roles:
      - Software
      - Validation
      - Visualization
    affiliations:
      - ai-lab
    github: "lisi"

# ========== 机构信息 ==========
affiliations:
  - id: cs-dep
    name: "某大学计算机科学与技术系"
    institution: "某大学"
    department: "计算机科学与技术系"
    city: "北京"
    country: "中国"
    postal_code: "100084"
  - id: ai-lab
    name: "人工智能国家重点实验室"
    city: "北京"
    country: "中国"

# ========== 出版信息 ==========
doi: "10.1234/myst-guide.2024.001"
arxiv: "2401.12345"
open_access: true
license: CC-BY-4.0
copyright: "Copyright 2024 作者团队"
venue: "MyST 学术写作研讨会"
volume: 1
first_page: 1
last_page: 20

# ========== 基金资助 ==========
funding:
  - statement: "本研究受国家自然科学基金（项目编号：61234567）资助"
    award: "61234567"
    recipients:
      - zhangsan

# ========== 参考文献 ==========
bibliography:
  - references/paper.bib

# ========== 下载配置 ==========
downloads:
  - title: "下载 PDF"
    file: _build/exports/paper.pdf
  - title: "下载源码"
    file: https://github.com/example/paper/archive/main.zip

# ========== GitHub 集成 ==========
github: "https://github.com/example/myst-paper-guide"
edit_url: "https://github.com/example/paper/edit/main/{path}"

# ========== 数学宏 ==========
math:
  macros:
    "\\RR": "\\mathbb{R}"
    "\\E": "\\mathbb{E}"
    "\\argmin": "\\mathop{\\mathrm{argmin}}"

# ========== 缩写表 ==========
abbreviations:
  MyST: "Markedly Structured Text"
  JATS: "Journal Article Tag Suite"
  OA: "Open Access"

# ========== 编号配置 ==========
numbering:
  figure: true
  table: true
  equation: true
---
```

### 9.2 项目级 myst.yml 中 project 块完整示例

```yaml
version: 1

project:
  # ========== 项目基础信息 ==========
  title: "MyST Markdown 完整学习指南"
  subtitle: "面向科学作者的现代写作工具"
  short_title: "MyST 指南"
  description: "一份系统、全面的 MyST Markdown 学习资料，涵盖基础语法、项目配置、高级功能和出版导出。"
  date: 2024-01-15
  
  # ========== 关键词 ==========
  keywords:
    - MyST
    - Markdown
    - 科学写作
    - Jupyter
    - 可复现研究
  
  # ========== 项目作者与机构 ==========
  authors:
    - name: "MyST 社区贡献者"
      email: "community@mystmd.org"
      url: "https://mystmd.org"
  license:
    content: CC-BY-4.0
    code: MIT
  github: "https://github.com/example/myst-guide"
  
  # ========== 参考文献（全局） ==========
  bibliography:
    - references/main.bib
    - references/glossary.bib
  
  # ========== Intersphinx 外部引用 ==========
  references:
    python:
      url: "https://docs.python.org/3"
    numpy:
      url: "https://numpy.org/doc/stable/"
  
  # ========== 目录结构（TOC） ==========
  toc:
    - file: index.md
      title: 首页
    - file: 01-overview.md
      title: 第一章 概述
    - file: 02-syntax.md
      title: 第二章 核心语法
    - file: 03-frontmatter.md
      title: 第三章 Frontmatter 配置
    - title: 第四章 高级功能
      children:
        - file: advanced/citations.md
          title: 引用与参考文献
        - file: advanced/math.md
          title: 数学公式
        - file: advanced/jupyter.md
          title: 可执行代码
  
  # ========== 导出配置（仅项目级有效） ==========
  exports:
    # 完整书籍 PDF（使用书籍模板）
    - format: pdf
      template: book
      output: _build/exports/myst-guide-book.pdf
      toc: true
      zip: true
    
    # 单页快速参考 PDF（使用文章模板）
    - format: pdf
      template: article
      output: _build/exports/myst-quickref.pdf
      articles:
        - quickreference.md
    
    # Word 版本
    - format: docx
      output: _build/exports/myst-guide.docx
      toc: true
    
    # LaTeX 源文件
    - format: tex
      output: _build/exports/latex-source.zip
      zip: true
      toc: true
    
    # JATS XML（用于学术出版系统）
    - format: jats
      output: _build/exports/myst-guide.xml
      articles:
        - index.md

# ========== 网站配置 ==========
site:
  template: book-theme
  title: "MyST Markdown 学习指南"
  options:
    logo: images/logo.png
    logo_text: "MyST Guide"
    favicon: images/favicon.ico
  nav:
    - title: 文档
      url: /
    - title: GitHub
      url: https://github.com/example/myst-guide
      external: true
  actions:
    - title: 开始阅读
      url: /01-overview
      style: primary
```

---

## 参考资料

- MyST Frontmatter 官方文档：https://mystmd.org/guide/frontmatter
- MyST Configuration 配置文档：https://mystmd.org/guide/configuration
- CRediT 贡献者角色分类：https://credit.niso.org/
- Creative Commons 许可选择器：https://creativecommons.org/choose/
