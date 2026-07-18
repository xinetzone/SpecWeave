---
version: 1.0
x-toml-ref: "../../../../.meta/toml/.trae/specs/standards-tools/create-myst-markdown-tutorial/spec.toml"
---
# MyST Markdown 技术教程 - Product Requirement Document

## Overview
- **Summary**: 创建一份全面的、面向团队的 MyST Markdown 技术教程，系统覆盖 MyST 的定义与特点、与标准 Markdown 的区别、基础语法、高级功能、扩展组件、工具链集成（Sphinx/Jupyter Book/mystmd）以及实际应用案例，配备语法示例、使用场景说明和常见问题解答。
- **Purpose**: 团队成员需要一份统一、系统、可直接上手的 MyST Markdown 学习资源，降低学习曲线，确保团队技术文档编写风格一致，充分利用 MyST 的出版级表达能力。现有资料库偏向 mystmd 新工具链，缺少面向初学者的完整教程路径和 Sphinx/Jupyter Book 集成指南。
- **Target Users**: SpecWeave 团队成员，包括技术文档编写者、开发工程师、研究人员，以及需要编写技术文档/学术文档/项目文档的所有团队成员。

## Goals
- 提供从零基础到进阶应用的完整 MyST Markdown 学习路径
- 清晰对比 MyST 与标准 Markdown（CommonMark）的区别，帮助已有 Markdown 经验的用户快速迁移
- 系统讲解基础语法（标题、列表、链接、图片等）与 MyST 特有高级功能（交叉引用、数学公式、代码块、注释、Directives/Roles）
- 详细介绍常用扩展组件（提示框、卡片、标签页、折叠面板等）的使用方法
- 覆盖三种主流工具链集成方式：Sphinx（Python 生态）、Jupyter Book v1（经典可执行书籍）、mystmd（新一代工具）
- 提供至少2个完整的实际应用案例（技术文档项目、学术论文/书籍章节）
- 配备可直接复制的语法示例、使用场景说明和常见问题解答（FAQ）
- 与现有 `docs/knowledge/learning/executablebooks-myst-guide/` 资料库形成互补而非重复，本教程定位为"系统性入门→进阶实战教程"，现有资料库定位为"参考手册+深度专题"

## Non-Goals (Out of Scope)
- 不替代官方文档，官方文档是最权威的参考来源
- 不覆盖 MyST 扩展开发（自定义 Directive/Role），这属于进阶开发内容
- 不深入讲解 Sphinx 插件开发或 mystmd 插件开发
- 不提供 Jupyter Notebook 执行环境的详细运维指南
- 不包含 PDF/LaTeX 排版的高级定制（仅介绍基础导出配置）
- 不重复现有资料库中已有的深度专题内容（如完整的 frontmatter 字段参考、TOC  glob 模式详解），而是提供教程式引导并链接到现有参考文档

## Background & Context
- 项目已有 MyST 学习资料库位于 [docs/knowledge/learning/executablebooks-myst-guide/](../../../../.agents/docs/knowledge/learning/04-docs-markup-tooling/executablebooks-myst-guide/README.md)，包含7个核心参考文档和示例
- 现有资料库的定位是"参考手册"，按功能模块组织，缺少按学习路径组织的教程式内容
- 团队偏好使用 myst-parser（见 user_profile），这是 Sphinx 生态中使用 MyST 的标准方式
- SpecWeave 项目自身大量使用 Markdown，并且已有 MDI（Markdown as Interface）研究基础
- 文档交叉引用规范已在项目中确立（相对路径、行号锚点等），教程需要与项目现有规范保持一致

## Functional Requirements
- **FR-1**: 教程必须包含 MyST Markdown 的定义、核心设计理念和主要特点章节
- **FR-2**: 教程必须包含 MyST vs CommonMark（标准 Markdown）对比章节，以表格形式清晰列出差异点和新增功能
- **FR-3**: 教程必须包含基础语法章节，系统讲解标题、段落、强调、列表（有序/无序/任务列表）、链接、图片、水平线、转义字符等标准 Markdown 语法，并标注 MyST 中的增强点
- **FR-4**: 教程必须包含高级功能章节，详细讲解 Directives（块级扩展）、Roles（行内扩展）、交叉引用、数学公式（行内/块级）、代码块（语法高亮、行号、强调行）、注释、脚注等 MyST 特有功能
- **FR-5**: 教程必须包含扩展组件章节，介绍常用 UI 组件：提示框（admonitions）系列、卡片（card）、标签页（tab-set/tab-item）、折叠面板（dropdown）、侧边栏（sidebar）、边注（margin）等
- **FR-6**: 教程必须包含工具链集成章节，分别讲解：
  - Sphinx + myst-parser 集成（conf.py 配置、常用扩展、构建命令）
  - Jupyter Book v1 集成（_config.yml、_toc.yml、构建与发布）
  - mystmd 集成（myst.yml 初始化、开发服务器、多格式导出）
- **FR-7**: 教程必须包含至少2个完整的实际应用案例：
  - 案例1：技术文档项目（如 API 文档或项目指南）
  - 案例2：学术/技术报告（含参考文献、数学公式、图表引用）
- **FR-8**: 教程必须包含"快速上手"章节，提供3种工具链的5分钟快速启动步骤
- **FR-9**: 教程必须包含常见问题解答（FAQ）章节，至少覆盖15个常见问题（语法陷阱、渲染问题、构建错误、迁移问题等）
- **FR-10**: 每个语法点必须配备可直接复制的代码示例和渲染效果说明
- **FR-11**: 教程必须采用原子化文档结构，按学习阶段拆分多个文档，每个文档聚焦单一主题
- **FR-12**: 教程必须包含双向导航（上一章/下一章/返回目录），与现有知识库的导航风格保持一致
- **FR-13**: 教程文档必须包含 YAML frontmatter（id, title, source 等字段），遵循项目文档规范
- **FR-14**: 教程必须在适当位置链接到现有 `executablebooks-myst-guide/` 中的深度参考文档，实现内容互补
- **FR-15**: 教程必须包含语法速查表（Cheat Sheet）作为附录，方便快速查阅

## Non-Functional Requirements
- **NFR-1**: 教程语言为中文，专业术语可保留英文原文并附中文解释
- **NFR-2**: 每个原子文档行数不超过300行，遵循项目原子化原则
- **NFR-3**: 示例代码必须正确可运行，语法示例必须符合 MyST 规范
- **NFR-4**: 文档间交叉引用使用相对路径，禁止使用 `file:///` 绝对路径
- **NFR-5**: 教程整体结构清晰，学习路径从易到难，初学者可按顺序逐章学习
- **NFR-6**: 教程放置在 `docs/knowledge/learning/myst-markdown-tutorial/` 目录下，与现有 learning 目录风格一致
- **NFR-7**: 完成后必须通过链接有效性检查（`python .agents/scripts/check-links.py`），确保无断链

## Constraints
- **Technical**: 教程本身使用 MyST Markdown 编写；遵循项目现有文档规范（原子化、YAML frontmatter、相对路径引用）
- **Business**: 必须与现有 MyST 资料库互补而非重复；面向团队内部使用
- **Dependencies**: 依赖现有项目文档结构；链接到现有参考文档而不是重复内容

## Assumptions
- 读者具备基本的 Markdown 使用经验（知道标题、列表、链接等基础语法）
- 读者对命令行操作有基本了解（安装工具、运行构建命令）
- 现有 `executablebooks-myst-guide/` 资料库内容保持稳定，链接目标不会大幅变动
- 团队技术栈包含 Python（用于 Sphinx/Jupyter Book）和 Node.js（用于 mystmd）

## Acceptance Criteria

### AC-1: 教程结构完整性
- **Given**: 教程文档全部创建完成
- **When**: 检查教程目录结构和内容
- **Then**: 必须包含：概述与快速上手、MyST 简介与对比、基础语法、高级功能（Directives/Roles）、扩展组件、工具链集成（Sphinx/Jupyter Book/mystmd）、应用案例、FAQ、语法速查表，共9大模块
- **Verification**: `programmatic`
- **Notes**: 每个模块可拆分为多个原子文档

### AC-2: 基础语法覆盖完整
- **Given**: 基础语法章节
- **When**: 检查基础语法内容
- **Then**: 必须覆盖：标题（6级）、段落与换行、文本强调（粗体/斜体/删除线/行内代码）、列表（有序/无序/任务列表/定义列表）、链接（外部/内部/锚点/邮箱）、图片（基础图片/带标题图片）、水平线、转义字符、HTML 支持，每个语法点配示例
- **Verification**: `programmatic`

### AC-3: 高级功能覆盖完整
- **Given**: 高级功能章节
- **When**: 检查高级功能内容
- **Then**: 必须覆盖：Directives 语法（两种围栏、参数、选项三种写法、嵌套规则）、Roles 语法、交叉引用（label/ref/numref）、数学公式（行内/块级/标签/编号）、代码块（语言指定/行号/强调行/标题）、注释、脚注、参考文献（cite），每个功能配示例
- **Verification**: `programmatic`

### AC-4: 扩展组件覆盖完整
- **Given**: 扩展组件章节
- **When**: 检查扩展组件内容
- **Then**: 必须至少覆盖6类组件：admonitions（note/warning/tip/important/caution等8种以上）、card、dropdown、tab-set/tab-item、table/list-table、figure，每种组件配代码示例和效果说明
- **Verification**: `programmatic`

### AC-5: 三种工具链集成指南完整
- **Given**: 工具链集成章节
- **When**: 检查工具链内容
- **Then**: Sphinx 部分必须包含 myst-parser 安装、conf.py 最小配置、扩展启用、构建命令；Jupyter Book 部分必须包含安装、_config.yml 最小配置、_toc.yml 结构、构建命令；mystmd 部分必须包含安装、myst init、myst start、myst build 导出多格式
- **Verification**: `programmatic`

### AC-6: 实际案例可运行
- **Given**: 应用案例章节
- **When**: 读者按照案例步骤操作
- **Then**: 案例必须包含完整的项目目录结构示例、配置文件示例、关键文档示例、构建步骤，读者按步骤可成功构建出可访问的文档站点
- **Verification**: `human-judgment`
- **Notes**: 案例不需要读者真的执行构建，但步骤必须清晰无遗漏

### AC-7: FAQ 覆盖常见问题
- **Given**: FAQ 章节
- **When**: 检查 FAQ 内容
- **Then**: FAQ 至少包含15个问题，覆盖：语法常见错误（如围栏嵌套错误）、渲染问题（如指令不生效）、构建错误（如交叉引用找不到标签）、工具安装问题、从标准 Markdown 迁移问题、Sphinx 特定问题、Jupyter Book 特定问题
- **Verification**: `programmatic`

### AC-8: 文档符合项目规范
- **Given**: 所有教程文档
- **When**: 运行项目规范检查
- **Then**: 每个文档包含 YAML frontmatter（id、title 字段）；所有文件 <300行；所有内部链接为相对路径；双向导航（上一章/返回目录/下一章）存在；通过 `check-links.py` 链接有效性检查；无 `file:///` 绝对路径
- **Verification**: `programmatic`

### AC-9: 与现有资料库互补不重复
- **Given**: 教程和现有 executablebooks-myst-guide 资料库
- **When**: 对比两者内容
- **Then**: 教程定位为"学习路径式教程"（按学习顺序组织，含大量引导性说明、场景解释、FAQ），现有资料库定位为"深度参考手册"（按功能模块组织，含完整字段参考、高级配置）；教程在适当位置链接到现有资料库的深度内容（如 frontmatter 完整字段参考链接到现有03文档，TOC glob 模式详解链接到现有04文档），不重复大段相同内容
- **Verification**: `human-judgment`

### AC-10: 语法速查表实用
- **Given**: 语法速查表附录
- **When**: 读者查阅速查表
- **Then**: 速查表以紧凑表格形式列出最常用的30+语法/Directive/Role，包含简短示例，适合快速查阅和记忆
- **Verification**: `human-judgment`

## Open Questions
- [ ] 是否需要在教程中包含 SpecWeave 项目自身的 MyST 使用规范（如项目特有的 frontmatter 字段、交叉引用约定）？
- [ ] 应用案例是否需要包含一个基于本项目实际文档结构的案例？
- [ ] mystmd 工具链目前处于快速迭代中，教程应锁定哪个版本范围？
