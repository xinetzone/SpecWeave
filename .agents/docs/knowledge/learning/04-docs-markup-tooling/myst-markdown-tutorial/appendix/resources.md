---
id: "myst-appendix-resources"
title: "附录B：资源推荐"
x-toml-ref: "../../../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/myst-markdown-tutorial/appendix/resources.toml"
---
# 附录B：资源推荐

本附录整理 MyST Markdown 学习过程中值得收藏的官方文档、工具、社区和进阶资源，帮助你在完成本教程后继续深入学习。

---

## B.1 官方文档资源

| 资源名称 | URL | 说明 | 适用场景 |
|---------|-----|------|---------|
| **MyST Parser 官方文档** | <https://myst-parser.readthedocs.io> | Sphinx 生态中 MyST 解析器的完整语法参考，包含所有指令、角色、配置项的权威说明 | 需要查阅 Sphinx + MyST 集成细节、配置选项、语法边界时 |
| **MyST Markdown 官方指南** | <https://mystmd.org/guide> | mystmd 新一代工具链的官方文档，涵盖最新语法规范、mystmd CLI 使用、主题定制等 | 使用 mystmd 工具链构建站点、需要最新语法特性参考时 |
| **Jupyter Book 官方文档** | <https://jupyterbook.org> | Jupyter Book v1 工具链完整文档，包含书籍结构配置、可执行代码、发布部署等教程 | 构建可计算书籍、教学材料、需要 Notebook 集成时 |
| **Executable Books 组织** | <https://executablebooks.org> | Executable Books 生态总览，介绍 MyST、Jupyter Book、MyST-NB 等项目的关系与发展路线 | 了解生态全貌、选择合适工具链、追踪项目动态时 |
| **Sphinx 官方文档** | <https://www.sphinx-doc.org> | Python 生态最成熟的文档构建系统文档，MyST 底层架构的参考来源 | 需要深度定制 Sphinx 扩展、理解 reST 底层概念时 |

---

## B.2 推荐学习路径

### 初学者路径（零基础入门）

1. **快速上手** → 阅读 [00-quick-start.md](../00-quick-start.md)，3 分钟完成安装和第一个文档
2. **基础语法** → 学习 02-basic-syntax-part1 和 03-basic-syntax-part2，掌握 Markdown 基础 + MyST 扩展
3. **实战练习** → 选择 mystmd 工具链，用 `myst start` 边写边预览，完成一个小文档（如笔记、README）
4. **查阅速查** → 遇到语法遗忘时直接翻 [cheat-sheet.md](cheat-sheet.md)

**目标**：1-2 天内能独立用 MyST 写日常文档。

---

### 技术文档工程师路径

1. **夯实基础** → 完整学习 04-10 章，掌握指令、角色、交叉引用、组件系统
2. **工具链集成** → 重点学习 11-tooling-sphinx.md 和 13-tooling-mystmd.md，根据团队技术栈选择
3. **API 文档模式** → 学习 14-case-study-tech-docs.md，掌握 autodoc、intersphinx、版本切换等企业级模式
4. **主题定制** → 参考 Sphinx/mystmd 官方文档学习主题开发与品牌定制
5. **CI/CD 部署** → 学习文档站点自动化构建与部署流程

**目标**：能独立搭建企业级技术文档站点，编写统一规范的项目文档。

---

### 学术研究者路径

1. **数学公式** → 重点学习 06-advanced-math-code.md，掌握 LaTeX 数学在 MyST 中的使用
2. **参考文献** → 学习 07-advanced-notes-citations.md，配置 BibTeX、引用样式
3. **交叉引用** → 精通 05-advanced-cross-references.md，实现图、表、公式、定理的自动编号引用
4. **多格式导出** → 用 mystmd 或 Jupyter Book 导出 HTML、PDF（LaTeX）、Word 等格式
5. **Jupyter Book 实战** → 学习 12-tooling-jupyter-book.md 和 15-case-study-academic.md，构建可计算论文/技术报告

**目标**：能撰写符合出版标准的学术论文、学位论文、技术报告。

---

### 团队/项目负责人路径

1. **工具链对比** → 对比 Sphinx、Jupyter Book、mystmd 三者的适用场景、学习曲线、维护成本
2. **目录结构设计** → 规划文档的信息架构、章节划分、版本管理策略
3. **协作规范** → 制定团队写作规范、PR 审核流程、风格指南
4. **部署与运维** → 选择托管平台（GitHub Pages/Read the Docs/内部服务器），配置 CI/CD
5. **自定义扩展** → 评估是否需要开发自定义指令/角色/主题，建设团队内部组件库

**目标**：能为团队选型合适的工具链，建立可持续维护的文档工程体系。

---

## B.3 实用工具推荐

### 编辑器插件

| 工具 | 说明 |
|------|------|
| **VS Code MyST 语法高亮** | 搜索 "MyST Markdown" 插件，提供语法高亮、指令/角色补全、预览功能 |
| **VS Code Jupyter 插件** | 编辑 `.ipynb` 笔记本文件，配合 Jupyter Book/mystmd 使用 |
| **MyST Preview** | 部分编辑器支持实时预览 MyST 渲染效果，推荐边写边看 |

### 在线编辑器

| 工具 | URL | 说明 |
|------|-----|------|
| **MyST Sandbox** | <https://mystmd.org/sandbox> | 官方在线 Playground，无需安装即可试用 MyST 语法，即时查看渲染效果 |

### 引用管理

| 工具 | 说明 |
|------|------|
| **Zotero** | 开源文献管理工具，支持一键导出 BibTeX 格式，浏览器插件抓取文献非常方便 |
| **JabRef** | 专业 BibTeX/BibLaTeX 编辑器，适合需要精细调整 `.bib` 文件的用户 |

### LaTeX 工具

| 工具 | URL | 说明 |
|------|-----|------|
| **Overleaf** | <https://www.overleaf.com> | 在线 LaTeX 编辑器，可用于测试复杂数学公式、调试 BibTeX 引用样式，确认无误后再复制到 MyST 文档 |

### 格式转换工具

| 工具 | 说明 |
|------|------|
| **Pandoc** | 通用文档转换工具，支持 MyST ↔ Markdown ↔ reST ↔ LaTeX ↔ Word 等格式互转，适合迁移旧文档 |

---

## B.4 社区资源

| 社区 | URL | 用途 |
|------|-----|------|
| **Executable Books Discourse 论坛** | <https://discourse.jupyter.org/c/executable-books> | 提问、讨论最佳实践、追踪生态动态的首选社区 |
| **Jupyter Book GitHub Discussions** | <https://github.com/executablebooks/jupyter-book/discussions> | Jupyter Book 具体使用问题、功能建议、Showcase 分享 |
| **MyST Parser GitHub Issues** | <https://github.com/executablebooks/myst-parser/issues> | 报告 Bug、查询已知问题、查看 Roadmap |
| **MySTmd GitHub Discussions** | <https://github.com/executablebooks/mystmd/discussions> | mystmd 新一代工具链的讨论区 |

### 相关会议与教程

- **JupyterCon**：Jupyter 生态年度会议，常有 Executable Books/MyST 相关专题
- **SciPy**：Python 科学计算会议，可计算叙事、Jupyter Book 教程常见于此
- **PyCon**：Python 社区大会，技术文档、Sphinx/MyST 相关分享

---

## B.5 进阶阅读

| 资源 | 说明 | 为什么值得读 |
|------|------|-------------|
| **Sphinx reST 语法参考** | reStructuredText 官方指南 | MyST 的指令/角色系统设计源自 reST，理解 reST 概念能帮你更透彻理解 MyST 的扩展机制，遇到问题也能参考 reST 解决方案 |
| **CommonMark 规范** | <https://commonmark.org> | MyST 是 CommonMark 的严格超集，理解 CommonMark 的解析规则有助于写出无歧义的 Markdown 基础语法 |
| **Markdown 变体对比文章** | 搜索 "CommonMark vs GFM vs MyST vs R Markdown" | 了解不同 Markdown 变体的定位差异，在混合使用场景（如 GitHub README + 项目文档）中能写出兼容性更好的文档 |

---

## B.6 本项目配套资源

### 深度参考

- [ExecutableBooks 生态深度指南](../../executablebooks-myst-guide/00-overview.md)：本项目中对 Executable Books 生态的深度解读，包含工具链架构、核心设计理念、高级特性等内容，适合完成本教程后继续深入。

### 配套示例

- [examples/](../examples/README.md) 目录下的所有 Demo 文件可直接复制修改：
  - `admonitions-demo.md` - 各类提示框组件示例
  - `figures-tables-demo.md` - 图表与表格示例
  - `ui-components-demo.md` - 卡片、标签页、折叠面板等 UI 组件
  - `tech-doc-template.md` - 技术文档项目模板
  - `paper-template.md` - 学术论文/报告模板

---

## B.7 结语

恭喜你完成了 MyST Markdown 技术教程的学习！

写作是一门实践的艺术。语法规则只是工具，真正掌握 MyST 的方式是**开始写作**——用它写你的下一篇技术文档、项目 README、学习笔记或学术报告。遇到遗忘的语法就回来翻速查表，遇到问题就查阅官方文档或到社区提问。

随着写作的深入，你会逐渐体会到 MyST 在"易写性"和"表达力"之间的精妙平衡：既保留了 Markdown 的简洁流畅，又拥有出版级文档所需的强大扩展能力。

期待看到你用 MyST 创作出的优秀作品！

---

## 导航

[« 返回目录](../README.md) | [上一章：速查表](cheat-sheet.md) | 教程结束
