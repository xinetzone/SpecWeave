---
source: "https://executablebooks.org, https://mystmd.org"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/executablebooks-myst-guide/06-resources.toml"
id: "executablebooks-myst-guide-resources"
title: "参考资源与链接汇总"
---
# 参考资源与链接汇总

本文档汇总了 MyST Markdown 相关的官方资源、GitHub 仓库、核心文档、社区资源、相关项目以及学习路径建议，方便快速查找和深入学习。

## 1. 官方资源链接

### ExecutableBooks 生态

- [ExecutableBooks 官网](https://executablebooks.org)
  ExecutableBooks 组织官方网站，介绍整个生态系统的项目、愿景和社区信息，是了解 MyST 生态的起点。

- [MyST Markdown 官方文档](https://mystmd.org/guide)
  mystmd 工具的完整用户指南，包含语法参考、配置说明、功能教程等，是日常使用的主要参考文档。

- [MyST Markdown 规范](https://mystmd.org/spec)
  MyST 语法的正式规范文档，详细定义了所有语法元素的解析规则，适合需要深入理解或实现 MyST 解析器的开发者。

- [mystmd CLI 工具](https://mystmd.org/guide/quickstart)
  mystmd 命令行工具快速入门指南，介绍如何安装、初始化项目、启动开发服务器、构建和导出文档。

### Jupyter Book 相关

- [Jupyter Book（v1）](https://jupyterbook.org)
  Jupyter Book v1 官方文档，基于 MyST Parser（Python/Sphinx）构建书籍和文档的工具，适合 Python 技术栈用户。

- [MyST Parser（Python/Sphinx）](https://myst-parser.readthedocs.io)
  Python 实现的 MyST 解析器，可作为 Sphinx 扩展使用，允许在 Sphinx 项目中编写 MyST Markdown。

- [MyST-NB（Notebook 支持）](https://myst-nb.readthedocs.io)
  Sphinx 扩展，为 MyST Parser 添加 Jupyter Notebook 支持，可以解析和执行 `.ipynb` 文件和 Markdown 中的代码单元格。

## 2. GitHub 仓库

### 核心仓库

- [mystmd 主仓库](https://github.com/executablebooks/mystmd)
  mystmd 命令行工具和 JavaScript/TypeScript 引擎的源代码仓库，包含最新的功能开发、Issue 追踪和发布版本。

- [Jupyter Book](https://github.com/executablebooks/jupyter-book)
  Jupyter Book v1 的源代码仓库，基于 Python/Sphinx 生态构建。

- [MyST Parser](https://github.com/executablebooks/MyST-Parser)
  Python 实现的 MyST 解析器源代码，作为 Sphinx 扩展使用。

### 官方示例与模板

- [mystmd 模板仓库](https://github.com/executablebooks/mystmd/tree/main/packages/myst-templates)
  mystmd 内置的文档和论文模板集合，包含多种期刊模板和网站主题。

- [myst-theme](https://github.com/executablebooks/myst-theme)
  MyST 网站主题组件，基于 React 构建，提供可定制的文档网站界面。

- [jupyter-book/examples](https://github.com/executablebooks/jupyter-book/tree/master/examples)
  Jupyter Book v1 官方示例集合，展示各种功能的使用方法。

## 3. 核心功能文档链接（按主题分类）

### 语法与格式

- [语法概览](https://mystmd.org/guide/syntax-overview)
  MyST Markdown 语法快速概览，对比 CommonMark 标准语法，介绍 MyST 扩展功能。

- [Directives（指令）](https://mystmd.org/guide/directives)
  块级扩展机制详解，包括指令语法、参数、选项以及内置指令列表。

- [Roles（角色）](https://mystmd.org/guide/roles)
  行内扩展机制详解，介绍如何使用角色在文本中插入特殊内容。

### 项目配置

- [配置参考](https://mystmd.org/guide/configuration)
  `myst.yml` 完整配置项参考，包括项目配置、网站配置、导出配置等。

- [Frontmatter](https://mystmd.org/guide/frontmatter)
  页面级元数据配置说明，支持 TOML 和 YAML 两种格式的 frontmatter。

- [目录结构（TOC）](https://mystmd.org/guide/table-of-contents)
  如何组织文档目录结构、配置导航菜单、控制章节排序。

### 内容类型

- [Admonitions（提示框）](https://mystmd.org/guide/admonitions)
  各种提示框类型（note、warning、tip、important、caution 等）的使用方法。

- [代码块](https://mystmd.org/guide/code)
  代码块语法、语法高亮、代码单元格、代码块标题和标签。

- [图片与图表](https://mystmd.org/guide/figures)
  图片插入、尺寸调整、对齐方式、带标题的 figure 指令。

- [表格](https://mystmd.org/guide/tables)
  Markdown 表格、网格表格、列表表格等多种表格格式。

- [数学公式](https://mystmd.org/guide/math)
  LaTeX 数学公式支持，行内公式和块级公式，公式编号和交叉引用。

- [引用与参考文献](https://mystmd.org/guide/citations)
  BibTeX 参考文献管理、引用语法、参考文献列表格式化。

- [交叉引用](https://mystmd.org/guide/cross-references)
  文档内交叉引用，引用章节、图片、表格、公式等，自动编号和链接。

- [图表与可视化（Mermaid 等）](https://mystmd.org/guide/diagrams)
  Mermaid 流程图、时序图、甘特图等图表的嵌入方法。

### 输出与部署

- [网站部署](https://mystmd.org/guide/deployment)
  如何将 MyST 文档部署到 GitHub Pages、Read the Docs、Netlify、Vercel 等平台。

- [PDF/Word 导出](https://mystmd.org/guide/exports)
  导出为 PDF、Word（DOCX）、LaTeX、JATS XML 等格式的配置和使用方法。

- [主题模板](https://mystmd.org/guide/themes-and-templates)
  网站主题选择、自定义主题、期刊模板使用指南。

### 交互式内容

- [Jupyter Notebook 集成](https://mystmd.org/guide/jupyter-notebooks)
  如何在 MyST 文档中嵌入 Jupyter Notebook，执行代码单元格，集成计算内容。

- [交互式组件](https://mystmd.org/guide/interactive-notebooks)
  MyST 中的交互式功能，如 Jupyter Widgets、可交互图表等。

## 4. 社区资源

### 博客与文章

- [ExecutableBooks 博客](https://executablebooks.org/en/latest/blog.html)
  官方博客，发布版本更新、功能介绍、使用案例等文章。

- [MyST Markdown 发布公告](https://www.2i2c.org/blog/2023/mystmd/)
  2i2c 博客上关于 mystmd 发布的介绍文章，讲述 mystmd 的设计理念和愿景。

### 讨论区与社区渠道

- [GitHub Discussions](https://github.com/executablebooks/mystmd/discussions)
  mystmd 官方讨论区，提问、分享使用经验、讨论功能需求的主要场所。

- [ExecutableBooks Discord](https://discord.gg/vbmPrJbm)
  社区 Discord 服务器，实时交流、获取帮助、与开发者和其他用户互动。

- [Jupyter Discourse](https://discourse.jupyter.org/)
  Jupyter 社区论坛，Jupyter Book 和 MyST 相关讨论也在这里进行。

### 示例项目

- [Jupyter Book Gallery](https://executablebooks.org/en/latest/gallery.html)
  官方展示的使用 Jupyter Book/MyST 构建的优秀文档和书籍案例。

- [MyST 文档自身](https://mystmd.org)
  MyST 官方文档就是用 mystmd 构建的，是学习 MyST 用法的优秀范例。

- [Thebe 示例](https://github.com/executablebooks/thebe)
  将 MyST 文档与交互式 Jupyter 计算集成的示例项目。

## 5. 相关项目

### 文档工具链

- [Sphinx 文档生成器](https://www.sphinx-doc.org)
  Python 生态最流行的文档生成器，MyST Parser 可以作为其扩展，让 Sphinx 支持 MyST Markdown 语法。MyST 的指令和角色机制借鉴自 Sphinx 的 reStructuredText 扩展系统。

- [Pandoc 文档转换](https://pandoc.org)
  通用文档转换工具，可以在多种标记语言格式之间转换，包括 Markdown、reStructuredText、LaTeX、HTML、DOCX 等。mystmd 在导出功能中部分依赖 Pandoc。

### 标记语言与规范

- [reStructuredText](https://docutils.sourceforge.io/rst.html)
  Python 社区传统的标记语言，Sphinx 的原生格式。MyST 的指令和角色概念源自 reStructuredText，但采用了更现代的 Markdown 语法。

- [CommonMark 规范](https://commonmark.org)
  Markdown 的标准化规范，MyST 是 CommonMark 的严格超集，所有 CommonMark 语法在 MyST 中都可以正常使用。

- [GitHub Flavored Markdown (GFM)](https://github.github.com/gfm/)
  GitHub 扩展的 Markdown 规范，MyST 兼容大部分 GFM 语法，如表格、任务列表、删除线等。

### Markdown 解析器

- [markdown-it-py](https://markdown-it-py.readthedocs.io)
  Python 实现的 Markdown 解析器，MyST Parser 基于它构建，支持插件扩展。

- [myst-parser（JS）](https://github.com/executablebooks/mystmd/tree/main/packages/myst-parser)
  mystmd 使用的 JavaScript/TypeScript MyST 解析器。

## 6. 学习路径建议

### 初学者路径（从零开始）

如果你是 MyST 新手，建议按以下顺序学习：

1. **快速体验**：阅读 [Quickstart](https://mystmd.org/guide/quickstart)，安装 mystmd，创建第一个项目，运行 `myst start` 预览效果
2. **语法概览**：阅读 [语法概览](https://mystmd.org/guide/syntax-overview)，了解 MyST 与标准 Markdown 的异同
3. **项目结构**：学习本指南第 02 章「项目结构」，理解 MyST 项目的组织方式
4. **基础语法**：学习本指南第 01 章「MyST 语法基础」，掌握指令、角色、提示框等常用功能
5. **Frontmatter 配置**：学习本指南第 03 章「Frontmatter 配置」，学会配置页面元数据
6. **目录配置**：学习本指南第 04 章「目录结构」，组织文档导航
7. **动手实践**：创建一个小型文档项目，尝试各种功能
8. **最佳实践**：学习本指南第 05 章「最佳实践」，养成良好的写作习惯
9. **查阅参考**：在实际使用中根据需要查阅官方文档中的功能专题

### Jupyter Book v1 迁移路径

如果你有 Jupyter Book v1 使用经验，建议按以下顺序迁移：

1. **了解差异**：阅读 mystmd 文档中关于 [Jupyter Book 迁移](https://mystmd.org/guide/quickstart-jupyter-book) 的说明
2. **安装 mystmd**：使用 npm 安装最新版 mystmd CLI 工具
3. **配置迁移**：将 `_config.yml` 配置迁移到 `myst.yml`
4. **目录迁移**：可以暂时保留 `_toc.yml`，或逐步迁移到 `myst.yml` 的 `site.nav`
5. **语法兼容**：大部分 MyST 语法在 mystmd 中同样适用，注意围栏语法的细微差异
6. **构建测试**：运行 `myst build` 检查是否有构建错误
7. **功能验证**：检查交叉引用、参考文献、图片等是否正常工作
8. **学习新功能**：探索 mystmd 新增的功能，如更现代的主题、更快的构建速度、更好的 PDF 导出

### 进阶主题

掌握基础后，可以按以下顺序深入学习高级功能：

1. **引用与参考文献**：学习 BibTeX 管理、引用格式化
2. **数学公式**：掌握 LaTeX 公式、公式编号、公式交叉引用
3. **交叉引用**：学习高级交叉引用技巧、自动编号
4. **图表与可视化**：Mermaid 图表、图片高级配置
5. **Notebook 集成**：Jupyter Notebook 嵌入、代码单元格执行
6. **自定义模板**：创建自定义网站主题和导出模板
7. **部署发布**：学习各种部署平台的配置方法
8. **PDF/Word 导出**：配置导出格式、期刊模板、字体等

## 7. 词汇表/术语

- **Directive（指令）**
  MyST 的块级扩展机制，用于插入提示框、代码块、图片、表格等复杂内容块，使用 `{directive-name}` 语法，通常配合围栏使用。

- **Role（角色）**
  MyST 的行内扩展机制，用于在普通文本行内插入特殊内容（如引用、数学符号、缩写等），使用 `{role-name}` 语法。

- **Frontmatter**
  文件开头的元数据块，用于配置页面标题、作者、日期、标签、引用标签等信息，MyST 支持 TOML（`+++`）和 YAML（`---`）两种格式。

- **TOC（Table of Contents）**
  目录结构，定义文档的章节组织和导航顺序，在 `myst.yml` 的 `site.nav` 中配置。

- **MyST（Markedly Structured Text）**
  一种基于 Markdown 的结构化标记语言，是 CommonMark 的超集，增加了指令、角色、交叉引用、参考文献等技术文档所需的扩展功能。

- **mystmd**
  MyST 的官方命令行工具和 JavaScript/TypeScript 引擎，提供项目初始化、开发服务器、构建、导出等功能，是新一代 MyST 工具链。

- **Jupyter Book**
  基于 MyST 构建书籍和可计算文档的工具，v1 版本基于 Python/Sphinx 生态，新版本与 mystmd 深度整合。

- **Sphinx**
  Python 生态最流行的文档生成器，最初为 Python 官方文档而开发，支持 reStructuredText，通过 MyST Parser 扩展可以支持 MyST Markdown。

- **ExecutableBooks**
  开发和维护 MyST、Jupyter Book 等可计算文档工具的开源组织，致力于推动科学计算和技术文档领域的开放工具发展。

- **Admonition（提示框）**
  用于突出显示特定类型信息的块级元素，常见类型有 note（提示）、warning（警告）、tip（技巧）、important（重要）、caution（危险）等。

- **Label（标签）**
  为文档中的元素（章节、图片、表格、公式等）分配的唯一标识符，用于交叉引用，格式为 `:label: my-label`。

- **Cross-reference（交叉引用）**
  在文档中引用其他位置的内容（如"参见图 3"、"如公式 5 所示"），MyST 可以自动生成编号和链接。

- **BibTeX**
  一种常用的参考文献管理格式，MyST 支持通过 `.bib` 文件管理参考文献，使用 `{cite}` 角色进行引用。

- **Build（构建）**
  将 MyST Markdown 源文件转换为 HTML、PDF 等输出格式的过程，使用 `myst build` 命令执行。

- **CommonMark**
  Markdown 的标准化规范，旨在消除不同 Markdown 实现之间的差异，MyST 严格遵循 CommonMark 规范并在此基础上进行扩展。
