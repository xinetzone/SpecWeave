---
id: "myst-markdown-tutorial-readme"
title: "MyST Markdown 技术教程"
---
# MyST Markdown 技术教程

## 简介

本教程是一套系统、实战导向的 MyST Markdown 学习指南，从入门到进阶全面覆盖 MyST 的核心语法、高级特性、组件系统和工具链生态。

**MyST（Markedly Structured Text）** 是 CommonMark Markdown 的超集，专为技术文档、学术写作和可计算叙事设计。它在保持 Markdown 简洁易写的基础上，融合了 reStructuredText/Sphinx 的强大扩展能力，支持指令（Directives）、角色（Roles）、交叉引用、数学公式、学术引用、UI 组件等出版级功能。

本教程采用"概念+示例+实战"三段式教学，配合 [examples/](./examples/) 目录中的可运行代码示例，帮助读者从零基础到熟练运用 MyST 构建专业文档。

---

## 适用人群

- 技术文档工程师：需要编写高质量项目文档、API 文档
- 学术研究者：撰写论文、技术报告、学位论文
- 开源项目维护者：构建项目文档站点、README、贡献指南
- Jupyter 用户：从 Notebook 迁移到可发布的技术书籍
- 内容创作者：追求 Markdown 之外更强表达能力的写作者
- Sphinx/reStructuredText 用户：希望用更简洁的 Markdown 语法替代 RST

---

## 前置知识

- **Markdown 基础**：熟悉标准 Markdown 语法（标题、列表、链接、图片等）
- **命令行基础**：能够使用终端执行 npm/pip 等包管理命令
- **（可选）Git 基础**：用于版本管理和协作
- **（可选）Python/Node.js 基础**：理解工具链配置

---

## 快速开始

3 分钟体验 MyST：

1. **安装 mystmd 命令行工具**
   ```bash
   npm install -g mystmd
   ```

2. **创建第一个 MyST 文档**
   ```bash
   mkdir my-first-myst && cd my-first-myst
   myst init
   ```

3. **启动本地预览服务器**
   ```bash
   myst start
   ```
   访问 http://localhost:3000 即可预览文档效果

> 💡 详细安装与配置见 [00-quick-start.md](./00-quick-start.md)

---

## 目录导航

按学习路径排列的完整教程章节：

### 第一部分：入门基础

| 文档 | 说明 |
|------|------|
| [00-quick-start.md](./00-quick-start.md) | 快速上手：安装、初始化、第一个文档 |
| [01-introduction.md](./01-introduction.md) | MyST 简介：设计理念、与 CommonMark/RST 的关系、生态概览 |
| [02-basic-syntax-part1.md](./02-basic-syntax-part1.md) | 基础语法（上）：标题、段落、列表、链接、图片、强调 |
| [03-basic-syntax-part2.md](./03-basic-syntax-part2.md) | 基础语法（下）：代码块、表格、分隔线、转义字符 |

### 第二部分：高级语法

| 文档 | 说明 |
|------|------|
| [04-advanced-directives-roles.md](./04-advanced-directives-roles.md) | 指令与角色：MyST 扩展系统的核心机制 |
| [05-advanced-cross-references.md](./05-advanced-cross-references.md) | 交叉引用：文档内引用、文档间引用、自动编号 |
| [06-advanced-math-code.md](./06-advanced-math-code.md) | 数学公式与代码：LaTeX 数学、代码块增强、可执行代码 |
| [07-advanced-notes-citations.md](./07-advanced-notes-citations.md) | 脚注与引用：脚注、尾注、参考文献、BibTeX 集成 |

### 第三部分：组件系统

| 文档 | 说明 |
|------|------|
| [08-components-admonitions.md](./08-components-admonitions.md) | 提示框组件：注意、警告、提示、重要、危险等各类提示框 |
| [09-components-ui.md](./09-components-ui.md) | UI 组件：卡片、标签页、折叠面板、按钮、下拉菜单 |
| [10-components-figures.md](./10-components-figures.md) | 图表组件：图片增强、图表标题、子图布局、图注 |

### 第四部分：工具链与实战

| 文档 | 说明 |
|------|------|
| [11-tooling-sphinx.md](./11-tooling-sphinx.md) | Sphinx 集成：在 Sphinx 项目中使用 MyST 解析器 |
| [12-tooling-jupyter-book.md](./12-tooling-jupyter-book.md) | Jupyter Book：构建可计算书籍和文档站点 |
| [13-tooling-mystmd.md](./13-tooling-mystmd.md) | mystmd 工具链：新一代 MyST 命令行工具与构建系统 |
| [14-case-study-tech-docs.md](./14-case-study-tech-docs.md) | 实战案例：技术文档站点构建全流程 |
| [15-case-study-academic.md](./15-case-study-academic.md) | 实战案例：学术论文与技术报告写作 |
| [16-faq.md](./16-faq.md) | 常见问题与排错指南 |

### 附录

| 文档 | 说明 |
|------|------|
| [appendix/cheat-sheet.md](./appendix/cheat-sheet.md) | 语法速查表：常用语法快速查阅 |
| [appendix/resources.md](./appendix/resources.md) | 学习资源：官方文档、社区、工具推荐 |

---

## 学习路径建议

- **零基础入门**：按顺序阅读 00 → 03，配合 examples/basic/ 目录示例动手练习
- **快速查语法**：直接查阅 [appendix/cheat-sheet.md](./appendix/cheat-sheet.md)
- **技术文档作者**：重点学习 04、05、08-10、14 章节
- **学术写作**：重点学习 06、07、15 章节
- **工具链集成**：根据需求选择 11-13 章节
- **遇到问题**：先查阅 [16-faq.md](./16-faq.md)，再参考 [appendix/resources.md](./appendix/resources.md)

---

## 子目录说明

### [examples/](./examples/) - 可直接运行的代码示例

本目录包含与教程各章节配套的完整示例文件，所有示例均可直接复制使用：

- `basic/` - 基础语法示例
- `directives/` - 指令用法示例
- `components/` - UI 组件示例
- `math/` - 数学公式示例
- `citations/` - 参考文献示例
- `projects/` - 完整项目示例（Sphinx/Jupyter Book/mystmd）

### [appendix/](./appendix/) - 附录资料

- `cheat-sheet.md` - MyST 语法速查表（一页纸版本）
- `resources.md` - 官方链接、社区资源、推荐工具清单
- `migration-guide.md` - 从 reStructuredText/CommonMark 迁移指南

---

## 相关资源

- **MyST 官方文档**：[https://mystmd.org/guide](https://mystmd.org/guide)
- **ExecutableBooks 官网**：[https://executablebooks.org](https://executablebooks.org)
- **Jupyter Book 文档**：[https://jupyterbook.org](https://jupyterbook.org)
- **Sphinx MyST Parser**：[https://myst-parser.readthedocs.io](https://myst-parser.readthedocs.io)
- **配套学习资料库**：[../executablebooks-myst-guide/README.md](../executablebooks-myst-guide/README.md)
