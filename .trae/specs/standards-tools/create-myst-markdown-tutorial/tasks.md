---
version: 1.0
---
# MyST Markdown 技术教程 - The Implementation Plan

## [x] Task 1: 创建教程目录结构与 README 入口
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建目标目录 `docs/knowledge/learning/myst-markdown-tutorial/`
  - 创建子目录：`examples/`（示例文件）、`appendix/`（附录）
  - 创建 README.md 作为教程入口，包含：教程简介、适用人群、学习路径建议、完整目录导航（按章节列出所有文档链接）、前置知识说明
  - README.md 需遵循现有知识库风格，与同目录下其他教程入口格式一致
- **Acceptance Criteria Addressed**: AC-1, AC-8
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录结构正确创建（主目录 + examples/ + appendix/）
  - `programmatic` TR-1.2: README.md 存在且包含 YAML frontmatter（id, title）
  - `programmatic` TR-1.3: README.md 列出所有计划中的章节文档链接
  - `human-judgement` TR-1.4: README 风格与 existing executablebooks-myst-guide/README.md 保持一致
- **Notes**: 参考现有 `docs/knowledge/learning/executablebooks-myst-guide/README.md` 的风格和格式

## [x] Task 2: 编写第0章 - 快速上手（Quick Start）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `00-quick-start.md`，提供三种工具链的5分钟快速启动
  - 内容包含：
    1. mystmd 快速启动（npm install → myst init → myst start）
    2. Jupyter Book v1 快速启动（pip install → jupyter-book create → jupyter-book build）
    3. Sphinx + myst-parser 快速启动（pip install sphinx → sphinx-quickstart → conf.py 配置 myst_parser → make html）
  - 每个工具链提供最小可运行配置示例和构建命令
  - 结尾包含"下一步学习建议"，引导到后续章节
  - 添加双向导航（返回目录 / 下一章：MyST 简介）
- **Acceptance Criteria Addressed**: AC-1, AC-8, FR-8
- **Test Requirements**:
  - `programmatic` TR-2.1: 文件存在，包含 YAML frontmatter，<300行
  - `programmatic` TR-2.2: 三种工具链均有安装→初始化→构建三个步骤
  - `programmatic` TR-2.3: 每种工具链都有最小配置示例（myst.yml / _config.yml / conf.py）
  - `programmatic` TR-2.4: 双向导航链接有效（README 和下一章）

## [x] Task 3: 编写第1章 - MyST 简介与 CommonMark 对比
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `01-introduction.md`
  - 内容包含：
    1. MyST 是什么（定义、全称、设计理念、定位："科学写作的 Markdown"）
    2. 核心特点（CommonMark 超集、Sphinx/reST 基因、可执行文档、科学出版支持、可扩展）
    3. MyST vs CommonMark 对比表格，清晰列出：
       - 标准 Markdown 已支持、MyST 完全兼容的功能
       - MyST 新增的核心功能（Directives、Roles、交叉引用、数学公式增强、脚注增强等）
       - 语法差异点（如注释语法、链接扩展）
    4. 适用场景（技术文档、学术论文/书籍、可复现研究报告、项目文档、API 文档）
    5. 生态概览（mystmd、Jupyter Book、Sphinx+myst-parser、MyST-Parser for Python）
  - 适当链接到现有 `executablebooks-myst-guide/00-overview.md` 获取更详细的生态介绍
  - 添加双向导航（上一章：快速上手 / 返回目录 / 下一章：基础语法）
- **Acceptance Criteria Addressed**: AC-1, AC-8, AC-9, FR-1, FR-2
- **Test Requirements**:
  - `programmatic` TR-3.1: 文件存在，frontmatter 完整，<300行
  - `programmatic` TR-3.2: 包含 MyST 定义、设计理念、核心特点章节
  - `programmatic` TR-3.3: 包含 MyST vs CommonMark 对比表格，至少列出10个差异点/增强点
  - `programmatic` TR-3.4: 链接到现有 executablebooks-myst-guide/00-overview.md
  - `human-judgement` TR-3.5: 对比表格清晰易懂，适合已有 Markdown 经验的开发者快速理解差异

## [x] Task 4: 编写第2章 - 基础语法（上）
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 创建 `02-basic-syntax-part1.md`，讲解基础文本语法
  - 内容包含：
    1. 标题（6级标题语法、锚点自动生成、MyST 中标题交叉引用增强）
    2. 段落与换行（标准换行 vs 硬换行、MyST 段落处理特点）
    3. 文本强调：粗体、斜体、粗斜体、删除线、行内代码、标记（==高亮==，如果支持）
    4. 水平线
    5. 转义字符（哪些字符需要转义、MyST 新增的转义场景）
    6. HTML 支持（MyST 中如何使用原生 HTML、安全限制说明）
  - 每个语法点配：语法说明 + 代码示例 + 效果说明 + 使用场景
  - 标注 MyST 对标准语法的增强点（如标题可自动生成标签用于引用）
  - 添加双向导航
- **Acceptance Criteria Addressed**: AC-2, AC-8, AC-10, FR-3
- **Test Requirements**:
  - `programmatic` TR-4.1: 文件存在，frontmatter 完整，<300行
  - `programmatic` TR-4.2: 覆盖标题、段落换行、文本强调（粗/斜/删/行内代码）、水平线、转义、HTML 共7类基础语法
  - `programmatic` TR-4.3: 每个语法点都有代码示例（使用代码块包裹）
  - `human-judgement` TR-4.4: 示例清晰，使用场景说明实用

## [x] Task 5: 编写第2章 - 基础语法（下）
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 创建 `03-basic-syntax-part2.md`，讲解列表、链接、图片
  - 内容包含：
    1. 列表：无序列表、有序列表、嵌套列表、任务列表（- [ ] / - [x]）、定义列表（MyST 增强）
    2. 链接：外部链接、内部文档链接、锚点链接、邮箱链接、引用式链接、MyST 链接增强（自动识别DOI等）
    3. 图片：基础图片语法 `![]()`、图片标题、带标题图片（figure directive 预览）、图片尺寸/对齐选项
  - 每个语法点配：语法说明 + 代码示例 + 效果说明 + 使用场景 + 常见陷阱
  - 标注 MyST 增强点（如任务列表的原生支持、定义列表、figure 指令的引用能力）
  - 添加双向导航
- **Acceptance Criteria Addressed**: AC-2, AC-8, FR-3
- **Test Requirements**:
  - `programmatic` TR-5.1: 文件存在，frontmatter 完整，<300行
  - `programmatic` TR-5.2: 覆盖列表（无序/有序/嵌套/任务/定义）、链接（6种类型）、图片（基础→figure预览）
  - `programmatic` TR-5.3: 每个语法点都有代码示例
  - `human-judgement` TR-5.4: 常见陷阱说明实用（如列表缩进、链接路径问题）

## [x] Task 6: 编写第3章 - 高级功能：Directives 和 Roles
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 创建 `04-advanced-directives-roles.md`
  - 内容包含：
    1. Directives 核心概念：两种围栏语法（::: 和 ```）、4部分结构（围栏/标识符/参数/选项/内容）、什么时候用哪种围栏
    2. Directive 选项三种写法：`:key: value`、YAML 块（---包裹）、内联选项（.class/#id/key="value"）
    3. 嵌套规则：逐层递增围栏数量、代码块嵌套技巧、混合嵌套示例
    4. Roles 核心概念：语法格式 `{rolename}`content``、与 Directives 的区别（行内 vs 块级）
    5. 常用内置 Roles 快速介绍（abbr/sub/sup/math/ref/eq/cite/doc）并配示例
    6. 本节重点是理解机制，常用 Directives/Roles 的具体使用在后续章节展开
  - 适当链接到现有 `executablebooks-myst-guide/01-myst-syntax.md` 获取更完整的语法参考
  - 添加双向导航
- **Acceptance Criteria Addressed**: AC-3, AC-8, AC-9, FR-4
- **Test Requirements**:
  - `programmatic` TR-6.1: 文件存在，frontmatter 完整，<300行
  - `programmatic` TR-6.2: 覆盖 Directives 两种围栏、选项三种写法、嵌套规则
  - `programmatic` TR-6.3: 覆盖 Roles 语法和与 Directives 的区别
  - `programmatic` TR-6.4: 至少介绍8个常用 Roles 并配示例
  - `programmatic` TR-6.5: 链接到现有 01-myst-syntax.md 深度参考

## [x] Task 7: 编写第3章 - 高级功能：交叉引用
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 创建 `05-advanced-cross-references.md`
  - 内容包含：
    1. 为什么需要交叉引用（自动编号、位置无关、重构友好）
    2. 添加标签：如何为章节、图片、表格、代码块、公式添加 label
       - 标题自动生成标签的规则
       - 显式标签（使用 `:label:` 选项或 `(label)=` 语法）
    3. 引用方式：
       - `{ref}`label``：带标题的引用
       - `{numref}`label``：带编号的引用（如图1、表2、公式3）
       - `{eq}`label``：公式专用引用
       - `{doc}`path``：文档间引用
       - 隐式引用（直接写 `{ref}`Title Text`` 按标题查找）
    4. 常见问题：标签找不到怎么办、跨文档引用注意事项、编号格式自定义
  - 配完整示例：一个带图表引用的小文档，展示从打标签到引用的完整流程
  - 添加双向导航
- **Acceptance Criteria Addressed**: AC-3, AC-8, FR-4
- **Test Requirements**:
  - `programmatic` TR-7.1: 文件存在，frontmatter 完整，<300行
  - `programmatic` TR-7.2: 覆盖标签添加（自动+显式两种方式）
  - `programmatic` TR-7.3: 覆盖 ref/numref/eq/doc 四种主要引用方式并配示例
  - `programmatic` TR-7.4: 包含至少一个完整的引用示例文档
  - `human-judgement` TR-7.5: 常见问题部分实用，覆盖"标签找不到"等高频问题

## [x] Task 8: 编写第3章 - 高级功能：数学公式与代码块
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 创建 `06-advanced-math-code.md`
  - 内容包含：
    1. 数学公式：
       - 行内公式 `{math}`...`` 或 `$...$`（说明两种语法的区别和配置）
       - 块级公式 ````{math}``` 指令（带标签、编号、对齐选项）
       - 常用 LaTeX 数学符号快速参考表（最常用的20+个符号/命令）
       - 公式编号与引用
       - 公式环境（align、gather 等，如支持）
    2. 代码块：
       - 标准代码块 ```language 语法回顾
       - code-block 指令增强：行号显示（:linenos:）、强调行（:emphasize-lines:）、行号起始（:lineno-start:）、代码块标题（:caption:）
       - 代码块标签与引用（{numref}）
       - 行内代码 literal role
    3. 代码块嵌套技巧（展示代码块的代码块需要增加反引号数量）
  - 每个功能配代码示例和渲染效果说明
  - 添加双向导航
- **Acceptance Criteria Addressed**: AC-3, AC-8, AC-10, FR-4
- **Test Requirements**:
  - `programmatic` TR-8.1: 文件存在，frontmatter 完整，<300行
  - `programmatic` TR-8.2: 覆盖行内公式和块级公式，配标签和引用示例
  - `programmatic` TR-8.3: 覆盖 code-block 指令的至少4个选项（linenos/emphasize-lines/caption/label）
  - `programmatic` TR-8.4: 包含常用数学符号参考表
  - `human-judgement` TR-8.5: 代码块嵌套示例清晰

## [x] Task 9: 编写第3章 - 高级功能：注释、脚注与参考文献
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - 创建 `07-advanced-notes-citations.md`
  - 内容包含：
    1. 注释（Comments）：MyST 注释语法（% 开头行注释、块注释）、与 HTML 注释的区别
    2. 脚注（Footnotes）：标准 Markdown 脚注语法 `[^1]`、MyST 中脚注的增强（编号自动管理、可交叉引用）、命名脚注、脚注内容位置
    3. 参考文献（Citations）：
       - 基本概念（BibTeX 文件、CSL 样式）
       - cite role 基础用法 `{cite}`key``
       - cite 变体：{cite:t}（文本式）、{cite:p}（括号式）等
       - 参考文献列表自动生成
       - 快速入门示例（一个最小可工作的参考文献配置）
    4. 边注与页边内容（margin/sidebar 指令简介）
  - 注：参考文献完整配置较复杂，本节提供快速入门，深度配置链接到现有参考资料
  - 添加双向导航
- **Acceptance Criteria Addressed**: AC-3, AC-8, FR-4
- **Test Requirements**:
  - `programmatic` TR-9.1: 文件存在，frontmatter 完整，<300行
  - `programmatic` TR-9.2: 覆盖注释、脚注、参考文献三类内容
  - `programmatic` TR-9.3: 参考文献提供最小可工作示例（BibTeX 示例 + 引用语法 + 参考文献列表指令）
  - `human-judgement` TR-9.4: 脚注语法和注释语法示例清晰易区分

## [x] Task 10: 编写第4章 - 扩展组件：提示框（Admonitions）
- **Priority**: high
- **Depends On**: Task 7, Task 8, Task 9
- **Description**:
  - 创建 `08-components-admonitions.md`
  - 内容包含：
    1. Admonitions 概述：什么是提示框、8种标准样式（note/warning/tip/important/caution/attention/hint/seealso/danger/error）
    2. 基本语法（::: 围栏）
    3. 自定义标题（默认标题 vs 自定义标题）
    4. 嵌套提示框
    5. 样式自定义（CSS 类、内联选项）
    6. 每种提示框的使用场景建议（什么时候用 note、什么时候用 warning、什么时候用 danger）
  - 在 examples/ 目录创建 `admonitions-demo.md` 展示所有样式效果
  - 链接到现有 `executablebooks-myst-guide/examples/admonitions.md` 的完整示例
  - 添加双向导航
- **Acceptance Criteria Addressed**: AC-4, AC-8, AC-9, FR-5
- **Test Requirements**:
  - `programmatic` TR-10.1: 文件存在，frontmatter 完整，<300行
  - `programmatic` TR-10.2: 介绍至少8种 admonition 样式，每种配示例
  - `programmatic` TR-10.3: 创建 examples/admonitions-demo.md 示例文件
  - `programmatic` TR-10.4: 链接到现有 admonitions 示例
  - `human-judgement` TR-10.5: 使用场景建议清晰实用

## [x] Task 11: 编写第4章 - 扩展组件：卡片、折叠、标签页
- **Priority**: high
- **Depends On**: Task 10
- **Description**:
  - 创建 `09-components-ui.md`
  - 内容包含：
    1. 卡片（card）：基本语法、标题、页脚、卡片链接、卡片网格
    2. 折叠面板（dropdown）：基本语法、默认展开状态、标题自定义、适用场景（FAQ、可选详细信息）
    3. 标签页（tab-set + tab-item）：基本语法、同步标签组、适用场景（多语言示例、多平台说明、替代方案对比）
    4. 表格增强：table 指令、list-table 指令、表格标题、表格标签与引用
  - 在 examples/ 目录创建 `ui-components-demo.md` 展示这些组件的组合使用
  - 每个组件配：语法示例 + 效果说明 + 典型使用场景
  - 添加双向导航
- **Acceptance Criteria Addressed**: AC-4, AC-8, FR-5
- **Test Requirements**:
  - `programmatic` TR-11.1: 文件存在，frontmatter 完整，<300行
  - `programmatic` TR-11.2: 覆盖 card、dropdown、tab-set/tab-item、table/list-table 共四类组件
  - `programmatic` TR-11.3: 创建 examples/ui-components-demo.md 示例文件
  - `human-judgement` TR-11.4: 每个组件的典型使用场景说明实用

## [x] Task 12: 编写第4章 - 扩展组件：图片与图表
- **Priority**: medium
- **Depends On**: Task 10
- **Description**:
  - 创建 `10-components-figures.md`
  - 内容包含：
    1. image 指令回顾：基础选项（align/width/height/alt）
    2. figure 指令详解：标题、标签、对齐、尺寸、编号与引用、figclass 选项
    3. 图片格式建议（SVG 优先、WebP、PNG/JPG 适用场景）
    4. 图表支持简介：Mermaid 图表（mermaid 指令）、PlantUML（如支持）
    5. 图片路径最佳实践（相对路径、资源目录组织）
  - 在 examples/ 目录创建 `figures-demo.md` 示例
  - 链接到项目 Mermaid 指南（`docs/knowledge/best-practices/mermaid-guide.md`）
  - 添加双向导航
- **Acceptance Criteria Addressed**: AC-4, AC-8, FR-5
- **Test Requirements**:
  - `programmatic` TR-12.1: 文件存在，frontmatter 完整，<300行
  - `programmatic` TR-12.2: 覆盖 image 和 figure 指令的主要选项
  - `programmatic` TR-12.3: 创建 examples/figures-demo.md 示例文件
  - `programmatic` TR-12.4: 链接到项目现有的 Mermaid 指南
  - `human-judgement` TR-12.5: 图片路径最佳实践实用

## [x] Task 13: 编写第5章 - 工具链集成：Sphinx + myst-parser
- **Priority**: high
- **Depends On**: Task 11, Task 12
- **Description**:
  - 创建 `11-tooling-sphinx.md`
  - 内容包含：
    1. 适用场景说明：什么时候选择 Sphinx（Python 项目文档、已有 Sphinx 生态、需要复杂扩展）
    2. 环境准备：Python 版本、pip 安装 sphinx 和 myst-parser
    3. 最小配置示例（conf.py）：
       - extensions 中添加 myst_parser
       - myst 配置项（myst_enable_extensions：常用扩展清单）
       - source_suffix 配置
    4. 常用 MyST 扩展说明（dollarmath/linkify/tasklist/deflist/colon_fence等）
    5. 项目结构建议
    6. 构建命令（make html / sphinx-build）
    7. 常用 Sphinx 扩展推荐（与 MyST 配合使用）
    8. 从 reStructuredText 迁移到 MyST 的建议
  - 提供最小可运行的 conf.py 示例
  - 添加双向导航
- **Acceptance Criteria Addressed**: AC-5, AC-8, FR-6
- **Test Requirements**:
  - `programmatic` TR-13.1: 文件存在，frontmatter 完整，<300行
  - `programmatic` TR-13.2: 包含完整的最小 conf.py 示例（含 myst_parser 配置、常用扩展列表）
  - `programmatic` TR-13.3: 包含构建命令说明
  - `programmatic` TR-13.4: 列出至少5个常用 myst_enable_extensions 并说明用途
  - `human-judgement` TR-13.5: 适用场景说明清晰，帮助读者选择工具链

## [x] Task 14: 编写第5章 - 工具链集成：Jupyter Book v1
- **Priority**: high
- **Depends On**: Task 13
- **Description**:
  - 创建 `12-tooling-jupyter-book.md`
  - 内容包含：
    1. 适用场景：什么时候选择 Jupyter Book（课程材料、可执行书籍、含代码的技术书籍、研究报告）
    2. 环境准备：pip install jupyter-book
    3. 创建项目：jupyter-book create 命令、项目目录结构解析
    4. _config.yml 最小配置：title/author、execute 配置（是否执行代码）、repository 配置、html 配置
    5. _toc.yml 目录配置：文件格式（format: jb-book）、chapters/sections 结构、示例
    6. 内容编写：Markdown 文件、Jupyter Notebook 文件、MyST 语法支持
    7. 构建与发布：jupyter-book build 命令、HTML 输出位置、GitHub Pages 发布简述
    8. 常见配置：代码执行配置、交互性设置（ThebeLab）、参考文献配置
  - 提供最小 _config.yml 和 _toc.yml 示例
  - 适当链接到现有 `executablebooks-myst-guide/02-project-structure.md` 和 `04-table-of-contents.md`
  - 添加双向导航
- **Acceptance Criteria Addressed**: AC-5, AC-8, AC-9, FR-6
- **Test Requirements**:
  - `programmatic` TR-14.1: 文件存在，frontmatter 完整，<300行
  - `programmatic` TR-14.2: 包含 _config.yml 最小配置示例和 _toc.yml 结构示例
  - `programmatic` TR-14.3: 包含构建命令和输出位置说明
  - `programmatic` TR-14.4: 链接到现有 02-project-structure.md 深度参考
  - `human-judgement` TR-14.5: TOC 配置示例清晰，易于理解 chapters/sections 嵌套

## [x] Task 15: 编写第5章 - 工具链集成：mystmd
- **Priority**: high
- **Depends On**: Task 13
- **Description**:
  - 创建 `13-tooling-mystmd.md`
  - 内容包含：
    1. 适用场景：什么时候选择 mystmd（新项目、需要多格式导出、追求构建速度、现代 JavaScript 工具链）
    2. 环境准备：Node.js 版本要求、npm/pnpm 安装 mystmd
    3. 初始化项目：myst init 命令、生成的 myst.yml 配置解析
    4. 本地开发：myst start 启动开发服务器、热重载、访问地址
    5. myst.yml 核心配置：project/title/site/nav/exports 等核心字段
    6. 多格式导出：
       - myst build --html（静态网站）
       - myst build --pdf（PDF导出）
       - myst build --docx（Word文档）
       - myst build --tex（LaTeX）
       - myst build --meca（学术投稿格式）
    7. 部署简介
    8. 与 Jupyter Book v1 的关系和迁移说明
  - 提供最小 myst.yml 示例
  - 链接到现有 `executablebooks-myst-guide/02-project-structure.md` 的完整配置参考
  - 添加双向导航
- **Acceptance Criteria Addressed**: AC-5, AC-8, AC-9, FR-6
- **Test Requirements**:
  - `programmatic` TR-15.1: 文件存在，frontmatter 完整，<300行
  - `programmatic` TR-15.2: 包含 myst.yml 最小配置示例
  - `programmatic` TR-15.3: 包含 myst init/start/build 三个核心命令说明
  - `programmatic` TR-15.4: 列出至少4种导出格式的命令
  - `programmatic` TR-15.5: 链接到现有 02-project-structure.md 深度参考

## [x] Task 16: 编写第6章 - 实际应用案例1：技术文档项目
- **Priority**: high
- **Depends On**: Task 14, Task 15
- **Description**:
  - 创建 `14-case-study-tech-docs.md`
  - 案例：使用 Sphinx + myst-parser 构建一个开源 Python 库的技术文档
  - 内容包含：
    1. 项目背景与目标（文档类型、目标读者、预期输出）
    2. 工具链选择理由（为什么选 Sphinx）
    3. 完整项目目录结构展示
    4. conf.py 完整配置示例（含扩展、主题、myst 配置）
    5. index.md 首页示例（项目介绍、快速导航、toctree）
    6. 典型页面示例：
       - 安装指南（含 admonitions 提示）
       - API 文档（含代码块、交叉引用）
       - 教程页面（含图片、提示框）
    7. 构建脚本与自动化
    8. 最终效果展示
  - 在 examples/case-tech-docs/ 目录下放置最小可运行的项目骨架（配置文件+示例文档）
  - 添加双向导航
- **Acceptance Criteria Addressed**: AC-6, AC-8, FR-7
- **Test Requirements**:
  - `programmatic` TR-16.1: 文件存在，frontmatter 完整，<300行
  - `programmatic` TR-16.2: 提供完整的目录结构和配置文件示例
  - `programmatic` TR-16.3: 在 examples/ 下创建案例的最小骨架文件
  - `human-judgement` TR-16.4: 案例步骤清晰，读者可参照搭建自己的技术文档

## [x] Task 17: 编写第6章 - 实际应用案例2：学术/技术报告
- **Priority**: medium
- **Depends On**: Task 16
- **Description**:
  - 创建 `15-case-study-academic.md`
  - 案例：使用 mystmd 构建一篇包含数学公式、图表、参考文献的技术报告
  - 内容包含：
    1. 报告背景与目标
    2. 工具链选择理由（为什么选 mystmd：多格式导出、PDF质量高）
    3. 项目目录结构
    4. myst.yml 配置（含作者、机构、参考文献、导出配置）
    5. 报告内容示例：
       - 摘要与 frontmatter 元数据
       - 引言章节
       - 公式展示（带标签和引用）
       - 图表插入（figure 指令，带编号和引用）
       - 参考文献引用
       - 结论
    6. 多格式导出演示：HTML、PDF、Word 导出命令
  - 在 examples/case-academic/ 目录下放置最小项目骨架
  - 添加双向导航
- **Acceptance Criteria Addressed**: AC-6, AC-8, FR-7
- **Test Requirements**:
  - `programmatic` TR-17.1: 文件存在，frontmatter 完整，<300行
  - `programmatic` TR-17.2: 提供包含参考文献配置的 myst.yml 示例
  - `programmatic` TR-17.3: 示例包含公式引用、图表引用、文献引用三种引用
  - `programmatic` TR-17.4: 在 examples/ 下创建案例的最小骨架文件
  - `human-judgement` TR-17.5: 案例展示了 MyST 在科学写作场景的核心优势

## [x] Task 18: 编写第7章 - 常见问题解答（FAQ）
- **Priority**: high
- **Depends On**: Task 16, Task 17
- **Description**:
  - 创建 `16-faq.md`
  - 整理至少15个常见问题，分类组织：
    1. 语法问题类（至少4个）：
       - 为什么我的 directive 没有被正确渲染？
       - 嵌套代码块时围栏数量怎么确定？
       - 为什么交叉引用报"WARNING: undefined label"？
       - 标题自动生成的标签名是什么规则？
    2. 构建问题类（至少4个）：
       - 构建时出现 WARNING 怎么解决？
       - 图片不显示怎么办（路径问题排查）？
       - 参考文献不显示怎么配置？
       - Sphinx 中 myst-parser 不生效怎么办？
    3. 工具链问题类（至少3个）：
       - 我该选择 Sphinx、Jupyter Book 还是 mystmd？
       - Jupyter Book 和 mystmd 是什么关系？
       - 可以和 reStructuredText 文件混用吗？
    4. 迁移问题类（至少2个）：
       - 从标准 Markdown 迁移需要注意什么？
       - 从 reStructuredText 迁移到 MyST 容易踩什么坑？
    5. 编辑器问题类（至少2个）：
       - VS Code 有 MyST 预览插件吗？
       - 如何实时预览 MyST 文档？
  - 每个问题包含：问题描述 + 原因分析 + 解决方案/建议
  - 添加双向导航
- **Acceptance Criteria Addressed**: AC-7, AC-8, FR-9
- **Test Requirements**:
  - `programmatic` TR-18.1: 文件存在，frontmatter 完整，<300行
  - `programmatic` TR-18.2: FAQ 至少包含15个问题，按上述分类组织
  - `programmatic` TR-18.3: 每个问题有明确的解决方案或建议
  - `human-judgement` TR-18.4: 问题确实是实际使用中高频遇到的，解决方案实用

## [x] Task 19: 编写附录A - MyST 语法速查表（Cheat Sheet）
- **Priority**: high
- **Depends On**: Task 18
- **Description**:
  - 创建 `appendix/cheat-sheet.md`
  - 内容以紧凑表格形式组织，包含：
    1. 基础语法速查表（12+项基础语法，语法+简短示例）
    2. 常用 Directives 速查表（15+个常用指令，语法+简短说明）
    3. 常用 Roles 速查表（12+个常用 role，语法+简短说明）
    4. 三种工具链核心命令对照表（安装/初始化/构建/开发服务器）
    5. 常用 Admonitions 样式一览（8种，带样式说明）
  - 目标：一页纸（或两页纸）容纳最常用的语法，适合打印或贴在显示器边查阅
  - 添加返回目录的导航链接
- **Acceptance Criteria Addressed**: AC-10, AC-8, FR-15
- **Test Requirements**:
  - `programmatic` TR-19.1: 文件存在，frontmatter 完整，<300行
  - `programmatic` TR-19.2: 基础语法速查表至少12项
  - `programmatic` TR-19.3: Directives 速查表至少15个
  - `programmatic` TR-19.4: Roles 速查表至少12个
  - `human-judgement` TR-19.5: 表格紧凑实用，适合快速查阅，没有冗余内容

## [x] Task 20: 编写附录B - 参考资源与延伸阅读
- **Priority**: medium
- **Depends On**: Task 18
- **Description**:
  - 创建 `appendix/resources.md`
  - 内容包含：
    1. 官方资源链接（MyST 官网、mystmd 文档、ExecutableBooks、Jupyter Book 文档、Sphinx MyST Parser 文档）
    2. 本项目现有 MyST 资料库链接（executablebooks-myst-guide/ 下的深度参考文档）
    3. 推荐教程与文章
    4. 社区支持渠道（GitHub Discussions、Discord/Slack 等）
    5. 相关工具（编辑器插件、转换器等）
  - 分类组织，每个链接附简短说明
  - 添加返回目录导航
- **Acceptance Criteria Addressed**: AC-9, AC-8
- **Test Requirements**:
  - `programmatic` TR-20.1: 文件存在，frontmatter 完整，<300行
  - `programmatic` TR-20.2: 包含官方网站、官方文档、GitHub 仓库三类官方资源链接
  - `programmatic` TR-20.3: 链接到本项目现有 MyST 深度参考资料
  - `human-judgement` TR-20.4: 资源分类清晰，每个链接有说明文字

## [x] Task 21: 质量检查与索引更新
- **Priority**: high
- **Depends On**: Task 19, Task 20
- **Description**:
  - 执行质量检查：
    1. 检查所有文档 YAML frontmatter 完整（id、title 字段）
    2. 运行 `python .agents/scripts/check-links.py --path docs/knowledge/learning/myst-markdown-tutorial/` 验证所有内部链接有效，无 file:/// 绝对路径
    3. 检查每个文档 <300 行
    4. 检查双向导航在所有章节中都存在且有效
    5. 检查所有相对路径引用正确（包括到现有 executablebooks-myst-guide/ 的链接）
  - 更新知识库索引：在 [docs/knowledge/README.md](file:///d:/spaces/SpecWeave/docs/knowledge/README.md) 中添加本教程的条目
  - 确保 examples/ 目录下的示例文件完整
- **Acceptance Criteria Addressed**: AC-8, AC-9
- **Test Requirements**:
  - `programmatic` TR-21.1: check-links.py 通过，零断链
  - `programmatic` TR-21.2: 所有文档行数 <300行
  - `programmatic` TR-21.3: 无 file:/// 绝对路径
  - `programmatic` TR-21.4: docs/knowledge/README.md 已添加教程条目
  - `human-judgement` TR-21.5: 整体学习路径连贯，导航顺畅
