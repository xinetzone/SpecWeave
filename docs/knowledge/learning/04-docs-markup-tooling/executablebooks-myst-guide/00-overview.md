---
source: "https://executablebooks.org/en/latest/, https://mystmd.org/guide/overview"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/executablebooks-myst-guide/00-overview.toml"
id: "executablebooks-myst-guide-overview"
title: "ExecutableBooks 生态概览"
---
# ExecutableBooks 生态概览

## ExecutableBooks 项目介绍

ExecutableBooks 是一个国际性的开源协作项目，旨在构建使用 Jupyter 生态系统发布计算性叙事文档（computational narratives）的开源工具。

项目的核心目标是让作者能够创建包含可执行代码、丰富文本、交互式可视化和科学出版元素的文档，并将这些内容发布为多种格式（HTML、PDF、Word 等）。ExecutableBooks 社区汇聚了来自学术界、工业界的开发者和研究者，共同推动科学出版和可复现研究的工具生态发展。

ExecutableBooks 项目最初源自 Jupyter Book 项目，随着生态的发展，逐渐演化为一个包含多个模块化工具的项目集合。

## MyST Markdown 定位

MyST（Markedly Structured Text）是 CommonMark  Markdown 的超集，灵感来自 Sphinx 和 reStructuredText 生态，专为科学和计算性叙事文档设计。

MyST 的设计理念：

- **Markdown 基础**：完全兼容 CommonMark，学习曲线平缓
- **Sphinx 基因**：继承了 reStructuredText 在科学出版领域的强大能力（指令、角色、交叉引用等）
- **可执行性**：原生支持 Jupyter 代码块的执行和输出嵌入
- **可扩展性**：通过 Directives 和 Roles 机制提供灵活的扩展能力
- **出版友好**：内置对引用、参考文献、数学公式、作者信息等科学出版元素的支持

MyST 的目标是成为「科学写作的 Markdown」——既保持 Markdown 的简洁易写，又具备 LaTeX/reStructuredText 的出版级表达能力。

## mystmd 与 Jupyter Book v1 的关系

ExecutableBooks 生态中有两代核心工具：

### Jupyter Book v1（旧版）

- **技术栈**：基于 Python/Sphinx 构建
- **特点**：成熟稳定，功能完整，已被广泛使用
- **架构**：Sphinx 扩展 + Python 工具链
- **配置**：使用 `_config.yml` 和 `_toc.yml` 进行配置

### mystmd（新一代）

- **技术栈**：JavaScript/TypeScript 实现
- **特点**：本学习资料主要聚焦于此
- **架构**：现代化的 JavaScript 工具链，性能更好
- **兼容性**：可以读取现有的 `_toc.yml` 和 MyST Markdown 内容，兼容 Jupyter Book 项目

### mystmd 的增强功能

相比 Jupyter Book v1，mystmd 提供了多项改进：

- **跨引用增强**：更强大的交叉引用系统，支持跨文档、跨项目引用
- **交互性提升**：更好的交互式组件支持
- **性能优化**：基于 JavaScript 的构建速度更快
- **多格式导出增强**：支持更多输出格式，PDF 导出质量更高
- **开发体验**：更好的错误提示、热重载、开发者工具

迁移说明：现有 Jupyter Book v1 用户可以平滑迁移到 mystmd，无需重写内容。

## 核心特性介绍

### 1. Directives（块级扩展）和 Roles（行内扩展）

MyST 提供了功能强大的扩展机制，这是其区别于普通 Markdown 的核心特性：

**Directives（块级扩展）**：用于插入块级内容，如图像、代码块、警告框、表格、图表等。

示例（使用 `{note}` 指令创建提示框）：

````
```{note}
这是一个提示框，用于强调重要信息。
```
````

**Roles（行内扩展）**：用于在行内插入特殊内容，如引用、数学公式、变量、链接等。

示例（使用 `{cite}` role 添加引用）：

```
请参阅 {cite}`holdgraf_evidence_2014` 了解更多信息。
```

这两种扩展机制让 MyST 具备了接近 reStructuredText 的表达能力，同时保持了 Markdown 的简洁语法。

### 2. 多格式导出

mystmd 支持将 MyST Markdown 文档导出为多种出版格式：

- **HTML 网站**：响应式静态网站，支持导航、搜索、交互
- **PDF**：支持 400+ 学术期刊模板，可直接用于投稿
- **Microsoft Word**：导出为 .docx 格式，方便协作编辑
- **LaTeX**：导出为 LaTeX 源码，用于高级排版
- **JATS**：Journal Article Tag Suite，学术出版标准格式
- **Typst**：新兴的排版语言，编译速度快
- **Markdown**：导出为标准 Markdown 或 MyST 变体

### 3. 可执行文档

MyST 深度集成 Jupyter 生态，支持可执行文档：

- **代码执行**：文档中的代码块可以直接执行，输出（文本、图像、表格、交互式组件）自动嵌入文档
- **内核支持**：支持多种 Jupyter 内核（Python、R、Julia 等）
- **缓存机制**：执行结果可缓存，避免重复计算
- **交互式图表**：支持 Plotly、Bokeh、Altair 等交互式可视化库
- **Jupyter 部件**：支持 ipywidgets 等交互式部件

这使得 MyST 成为可复现研究（reproducible research）和 literate programming 的理想工具。

### 4. 科学出版支持

MyST 为科学写作提供了完整的支持：

- **引用与参考文献**：BibTeX/BibLaTeX 风格的引用系统，支持 CSL 样式
- **交叉引用**：图表、公式、章节、代码块的自动编号和引用
- **数学公式**：LaTeX 语法的数学公式支持，包括行内公式和块级公式
- **作者信息**：作者、机构、基金、致谢等元数据管理
- **DOI 集成**：自动解析 DOI 链接
- **脚注与边注**：灵活的注释系统

### 5. 社区驱动

MyST 和 ExecutableBooks 生态具有以下特点：

- **开源**：所有工具均为开源项目，使用 BSD/MIT 许可
- **模块化**：工具集设计为可组合的模块，用户可以按需选用
- **可组合**：可以与 Jupyter、Sphinx、Pandoc 等现有工具链配合使用
- **活跃社区**：由 ExecutableBooks 社区维护，持续迭代更新
- **互操作性**：与现有科学出版生态系统（如 LaTeX、JATS、DOI）良好互操作

## MyST 在 Project Jupyter 组织下的定位

MyST Markdown 现在是 **Project Jupyter** 官方组织下的项目，这意味着：

1. **官方地位**：MyST 已成为 Jupyter 生态中 Markdown 相关工具的官方项目之一
2. **治理保障**：在 Jupyter 基金会的治理下，项目发展更加稳健可持续
3. **生态整合**：与 Jupyter Notebook、JupyterLab、Jupyter Book 等核心项目深度整合
4. **社区资源**：获得 Jupyter 社区的开发者资源和用户基础

这一定位使 MyST 成为 Jupyter 生态中文档和科学出版的事实标准，为可复现计算叙事提供统一的创作格式。

## 参考资料

- ExecutableBooks 官方网站：https://executablebooks.org/en/latest/
- MyST Markdown 官方网站：https://mystmd.org
- MyST 概述文档：https://mystmd.org/guide/overview
