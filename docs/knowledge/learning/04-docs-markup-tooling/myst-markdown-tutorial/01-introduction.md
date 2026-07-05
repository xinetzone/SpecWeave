---
id: "myst-tutorial-introduction"
title: "第1章：MyST 简介与 CommonMark 对比"
---

# 第1章：MyST 简介与 CommonMark 对比

本章将深入介绍 MyST Markdown 的设计理念、核心特性，并通过详细对比表格展示 MyST 相对于标准 CommonMark 的增强能力，帮助你理解为什么 MyST 是技术写作和科学出版的理想选择。

---

## 1.1 MyST 是什么

**MyST** 全称 **Markedly Structured Text**，是 CommonMark Markdown 的严格超集，灵感来自 Sphinx 生态和 reStructuredText（reST），专为科学写作、技术文档和可计算叙事设计。

:::{note}
**一句话定义**：MyST = 标准 Markdown 的简洁易写 + Sphinx/reST 的出版级扩展能力 + Jupyter 的可执行性。

深度参考：[ExecutableBooks 生态概览](../executablebooks-myst-guide/00-overview.md)
:::

### 1.1.1 设计理念

MyST 的设计遵循以下核心原则：

- **兼容性优先**：100% 兼容 CommonMark，现有 Markdown 文件无需修改即可使用
- **渐进式学习**：从基础 Markdown 开始，按需逐步学习高级特性
- **出版级质量**：内置学术引用、交叉引用、数学公式等专业出版功能
- **可执行性**：原生支持 Jupyter 代码块执行与输出嵌入
- **可扩展性**：通过 Directives（块级扩展）和 Roles（行内扩展）提供灵活的扩展机制
- **多格式输出**：一次编写，导出为 HTML、PDF、Word、LaTeX、JATS 等多种格式

---

## 1.2 核心特点

:::{tip}
MyST 的设计目标是成为「科学写作的 Markdown」——既保持 Markdown 的简洁语法，又具备 LaTeX/reStructuredText 的专业表达能力。
:::

| 特点 | 说明 |
|------|------|
| **CommonMark 完全兼容** | 所有标准 Markdown 语法在 MyST 中都能正常工作，零迁移成本 |
| **Sphinx/reST 基因** | 继承了 reStructuredText 的 Directives 和 Roles 扩展机制，表达能力强大 |
| **可执行文档** | 深度集成 Jupyter，代码块可直接执行，输出自动嵌入，支持可复现研究 |
| **科学出版支持** | 内置 BibTeX 引用、LaTeX 数学公式、图表/公式/章节自动编号与交叉引用 |
| **丰富的 UI 组件** | 提示框、卡片、标签页、折叠面板等组件，无需手写 HTML/CSS |
| **多格式导出** | 支持导出为响应式 HTML 网站、PDF（含学术期刊模板）、Word、LaTeX、JATS、Typst 等 |
| **活跃的生态** | 由 ExecutableBooks 社区维护，现为 Project Jupyter 官方项目 |

---

## 1.3 MyST vs CommonMark 详细对比

下表从 10+ 个维度详细对比 CommonMark 标准与 MyST 增强能力：

| 功能 | CommonMark 标准 | MyST 增强 | 示例 |
|------|----------------|-----------|------|
| **注释语法** | 无标准注释语法，通常用 HTML 注释 `<!-- ... -->` | 支持百分号注释 `% ...`，更简洁，不会输出到最终文档 | `% 这是一行注释，不会显示` |
| **脚注增强** | 基础脚注支持 `[^1]`，但功能有限 | 增强脚注支持，支持命名脚注、脚注内联、脚注反向链接优化 | `[^named]` + `[^named]: 脚注内容` |
| **任务列表** | GitHub Flavored Markdown 支持，非 CommonMark 标准 | 原生支持任务列表，带复选框样式，支持嵌套 | `- [x] 已完成任务`<br>`- [ ] 待办任务` |
| **定义列表** | 无标准定义列表语法 | 原生支持定义列表，术语与解释清晰分离 | `术语`<br>`: 术语的定义说明` |
| **数学公式** | 无标准数学公式支持 | 原生 LaTeX 数学公式，行内 `$...$` 和块级 `$$...$$` | 行内：`$E=mc^2$`<br>块级：`$$\int_0^\infty e^{-x}dx = 1$$` |
| **交叉引用** | 仅支持锚点链接，无自动编号 | 支持标题、图表、公式、代码块的自动编号与语义化引用 | `{ref}`label`` 引用自动编号的图表或章节 |
| **提示框/Admonitions** | 无标准提示框，需手写 HTML | 内置 note/tip/warning/important/danger 等提示框类型，支持自定义标题 | `:::{note}`<br>`这是提示内容`<br>`:::` |
| **Directives 块扩展** | 无扩展机制，只能用原生 HTML | 强大的块级指令系统，支持图表、代码块、表格、嵌入内容等扩展 | ````{figure} image.png`<br>`图注内容`<br>```` |
| **Roles 行内扩展** | 无行内扩展机制 | 灵活的行内角色系统，支持引用、数学、缩写、下标、上标等行内语义标记 | `{cite}`holdgraf2014`` 行内引用文献 |
| **表格增强** | 基础管道表格，对齐支持有限 | 支持网格表格、CSV 表格导入、表格标题、单元格合并、列宽控制 | ````{table}` 表格标题`<br>`:align: center`<br>表格内容<br>```` |
| **代码块增强** | 基础围栏代码块，仅支持语言标注 | 支持代码块标题、行号高亮、代码块编号与交叉引用、执行输出嵌入 | ````{code-block} python`<br>`:linenos: true`<br>`print("Hello")`<br>```` |
| **参考文献引用** | 无内置引用支持 | 原生 BibTeX/BibLaTeX 集成，支持 CSL 引用样式，自动生成参考文献列表 | `{cite}`paper1,paper2`` 引用多篇文献 |

:::{note}
这只是 MyST 增强功能的一部分，完整特性列表请参阅后续章节。MyST 的设计是渐进式的——你不需要一开始就掌握所有特性，从标准 Markdown 开始，按需学习即可。
:::

---

## 1.4 适用场景

MyST 特别适合以下场景：

### 1.4.1 技术文档与 API 文档
- 开源项目文档站点
- SDK/API 参考手册
- 内部技术知识库
- 产品帮助文档

### 1.4.2 学术论文与书籍
- 学术期刊论文投稿（支持 400+ 期刊模板）
- 学位论文与技术报告
- 学术专著与教材
- 会议论文集

### 1.4.3 可复现研究报告
- 数据分析报告
- 计算科学实验记录
- Jupyter Notebook 发布
- Literate Programming（文学编程）作品

### 1.4.4 课程材料与教学文档
- 在线课程讲义
- 编程教程
- 实验指导书
- 学生作业与项目文档

### 1.4.5 项目文档
- 软件架构文档
- 需求规格说明书
- 设计文档
- 项目复盘报告

---

## 1.5 生态概览

MyST 生态经过多年发展，已经形成了覆盖不同使用场景的工具链：

| 工具 | 技术栈 | 定位 | 适用场景 |
|------|--------|------|----------|
| **mystmd** | JavaScript/TypeScript | 新一代官方工具链 | 新手入门、快速原型、现代文档站点 |
| **Jupyter Book v1** | Python/Sphinx | 经典学术出版工具 | 可计算书籍、课程材料、Notebook 发布 |
| **Sphinx + myst-parser** | Python/Sphinx | 传统 Sphinx 生态集成 | 已有 Sphinx 项目、Python 技术文档 |
| **MyST-Parser** | Python | 底层 Markdown 解析库 | 需要在 Python 项目中解析 MyST 的开发者 |

:::{tip}
**工具链选择建议**：
- 新手优先选择 **mystmd**：零配置、热重载、现代 UI、多格式导出
- 学术写作/含 Notebook 选择 **Jupyter Book**：原生 Notebook 支持、成熟稳定
- 已有 Sphinx 项目选择 **Sphinx + myst-parser**：无缝集成、插件丰富
:::

详细工具链使用指南请参阅 [第0章：快速上手](00-quick-start.md)。

---

## 导航

[« 上一章：快速上手](00-quick-start.md) | [返回目录](README.md) | [下一章：基础语法（上） »](02-basic-syntax-part1.md)
