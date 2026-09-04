---
title: "awesome-okf-xs 文档系统 - 产品需求文档（PRD）"
status: "draft"
---

# awesome-okf-xs 文档系统 - 产品需求文档（PRD）

## Overview

- **Summary**: 以 mystx Sphinx 文档系统为模板，在 `awesome-okf-xs/doc/` 目录下创建一套完整的 Sphinx + MyST 文档构建系统，将 `bundles/` 目录作为只读子文档库集成，实现 OKF 知识束的可发布、可搜索、可导航的文档站点。
- **Purpose**: awesome-okf-xs 拥有 236 个 OKF 知识束（23 个分组），但目前仅以原始 Markdown 文件存在，缺乏统一的文档站点、全文搜索、导航侧边栏和多格式导出能力。需要一套专业的文档系统将这些知识资产发布为可浏览的网站。
- **Target Users**: 玄境项目开发者、AI 智能体、开源贡献者、中文技术学习者。

## Goals

- 在 `doc/` 下创建可独立构建的 Sphinx + MyST 文档项目
- 将 `bundles/` 作为只读子文档库集成到 Sphinx 站点中，不修改 bundles 内任何文件
- 为 bundles 创建完整的目录索引和导航结构
- 采用 mystx 的 probe-fallback 配置模式，确保多环境兼容
- 支持中文文档、响应式布局、代码复制、全文搜索
- 提供 `pyproject.toml` 管理文档构建依赖

## Non-Goals (Out of Scope)

- 不修改 `bundles/` 目录内的任何文件
- 不创建新的知识束内容（仅创建索引和框架文件）
- 不部署到 ReadTheDocs 或 GitHub Pages（仅提供构建配置，部署由后续任务处理）
- 不实现 PDF/ePub 导出配置（可后续扩展）
- 不创建自定义 Sphinx 扩展（使用现有扩展）
- 不修改 awesome-okf-xs 的 `.agents/` 规范目录

## Background & Context

### mystx 模板分析

mystx 是一个 Sphinx 文档主题项目，位于 `playground/books/libs/mystx/`，其文档系统具有以下特征：

1. **配置架构**: `docs/conf.py` 使用 probe-fallback 模式——通过 `importlib.util.find_spec` 检测可选依赖，条件启用扩展；主题回退链为 mystx → sphinx_book_theme → alabaster
2. **主题配置**: `_config.toml` 定义主题选项（继承 sphinx_book_theme），包含仓库链接、侧边栏、社交图标、启动按钮等
3. **MyST 扩展**: 启用 dollarmath、amsmath、deflist、colon_fence、replacements、substitution
4. **静态资源**: `_static/local.css` 包含完整的响应式设计（手机/平板/桌面三档断点）
5. **文档结构**: `index.md` 使用 hidden toctree 组织子文档，`readme.md` 通过 `{include}` 引入项目 README
6. **可选扩展集**: sphinx_design、sphinx_copybutton、sphinx_tippy、sphinxcontrib-bibtex、sphinx_sitemap、sphinxext-opengraph、sphinx_contributors、autoapi、graphviz、intersphinx、extlinks 等

### awesome-okf-xs 现状

1. **bundles/**: 已有完整的 OKF v0.2 知识束库，根 `bundles/index.md` 包含生态关系图、推荐入门路径、分组导航表和分组详情表
2. **无 doc/ 目录**: 项目尚无 Sphinx 文档系统
3. **无 pyproject.toml**: 项目没有 Python 包管理配置
4. **文件格式**: 所有文档为 Markdown + YAML frontmatter，无 Jupyter notebook、无 BibTeX 文件
5. **项目规范**: 正文中文、文件名 kebab-case 英文、相对路径引用、OKF v0.2 frontmatter

### 技术约束

- Sphinx 默认禁止引用源目录（`doc/`）之外的文件，直接在 toctree 中引用 `../bundles/index` 会触发安全错误
- bundles/ 内文件使用相对路径互链（如 `[conda](conda/index.md)`），集成后需保持链接有效
- bundles 内 `log.md` 文件无 YAML frontmatter（OKF 保留文件名），MyST 解析需容错
- Windows 环境下符号链接需要管理员权限或开发者模式，但目录联接（junction）无需特殊权限

## Functional Requirements

- **FR-1**: 创建 `doc/conf.py`，以 mystx 模板为基础适配 awesome-okf-xs 项目
- **FR-2**: 创建 `doc/index.md` 作为文档站点首页，包含到 bundles 子文档库的 toctree 入口
- **FR-3**: 通过跨平台符号链接/联接机制将 `doc/bundles` 指向 `../bundles`，使 Sphinx 能将 bundles 作为子文档源处理
- **FR-4**: 在 `doc/conf.py` 的 `setup()` 函数中实现链接自动创建逻辑，支持 Windows junction 和 Unix symlink
- **FR-5**: 创建 `doc/_static/` 目录及基础 CSS 文件（从 mystx 适配响应式样式）
- **FR-6**: 创建 `doc/readme.md` 通过 MyST include 引入项目根 README
- **FR-7**: 创建 `pyproject.toml` 定义文档构建依赖组（sphinx、myst-parser、sphinx-book-theme 等核心依赖）
- **FR-8**: 适配主题配置：项目名称、仓库 URL、导航深度、中文界面
- **FR-9**: 配置 `suppress_warnings` 容错处理 bundles 中的 OKF frontmatter 和无 frontmatter 文件
- **FR-10**: 更新 `.gitignore` 排除 `doc/_build/`、`doc/bundles`（链接）、`doc/api/` 等构建产物

## Non-Functional Requirements

- **NFR-1（兼容性）**: 在 Windows 10+（junction）、Linux、macOS（symlink）上均可构建，无需管理员权限
- **NFR-2（幂等性）**: conf.py 中的链接创建逻辑必须幂等——链接已存在时不报错，bundles 真实目录被误创建为普通目录时给出明确错误提示
- **NFR-3（只读保证）**: 构建过程不修改 `bundles/` 内任何文件，Sphinx 构建产物输出到 `doc/_build/`
- **NFR-4（可构建性）**: `sphinx-build doc doc/_build/html` 能成功完成，无致命错误
- **NFR-5（中文支持）**: 文档语言设置为 `zh_CN`，搜索和界面元素支持中文
- **NFR-6（响应式）**: 继承 mystx 的响应式 CSS，在手机/平板/桌面三档断点下均可正常阅读

## Constraints

- **Technical**:
  - Python >= 3.14（遵循项目环境约束）
  - Sphinx >= 7.x（支持 MyST parser 和现代主题）
  - myst-parser >= 4.0（MyST Markdown 支持）
  - sphinx-book-theme >= 1.0（mystx 主题的基主题，作为 fallback）
  - 不依赖 mystx 包本身（mystx 是本地库，不一定可 pip 安装）
- **Business**: 不修改 bundles/ 只读内容
- **Dependencies**: Sphinx、myst-parser、sphinx-book-theme、sphinx-design、sphinx-copybutton、sphinx-tippy 等开源扩展

## Assumptions

- 用户的 Python 环境（py314 conda 环境）可安装 Sphinx 和相关扩展
- bundles/ 目录在文档构建期间保持稳定（不被删除或移动）
- awesome-okf-xs 项目根目录的 git 仓库允许添加 `doc/` 目录和 `pyproject.toml`
- 不需要 mystx 主题本身（使用 sphinx-book-theme 作为主主题即可），因为 mystx 是本地路径库
- bundles 内的 Markdown 文件格式兼容 MyST parser（标准 Markdown + GFM 扩展）

## Acceptance Criteria

### AC-1: 文档项目可构建

- **Given**: `doc/` 目录已创建且包含 conf.py 和 index.md
- **When**: 在项目根目录执行 `sphinx-build doc doc/_build/html`
- **Then**: 构建成功完成（exit code 0），`doc/_build/html/index.html` 文件存在
- **Verification**: `programmatic`

### AC-2: bundles 作为子文档库集成

- **Given**: `doc/bundles` 链接指向 `../bundles`
- **When**: Sphinx 构建文档站点
- **Then**: bundles/index.md 及其引用的子文档被渲染为站点页面，导航侧边栏显示 bundles 分组结构
- **Verification**: `programmatic`

### AC-3: bundles 目录不被修改

- **Given**: 构建前后 bundles 目录状态
- **When**: 执行完整文档构建
- **Then**: bundles/ 目录内无文件被创建、修改或删除
- **Verification**: `programmatic`（git status 验证）

### AC-4: 跨平台链接创建

- **Given**: Windows 或 Linux/macOS 环境
- **When**: Sphinx 初始化（触发 conf.py 的 setup 函数）
- **Then**: Windows 上创建 junction，Unix 上创建 symlink，链接指向正确的 bundles 目录；重复执行不报错
- **Verification**: `programmatic`

### AC-5: 首页导航完整

- **Given**: 构建后的文档站点
- **When**: 访问首页 index.html
- **Then**: 页面包含项目标题、bundles 知识束库入口链接、README 内容区域，侧边栏导航显示 bundles 分组
- **Verification**: `human-judgment`

### AC-6: 中文搜索可用

- **Given**: 构建后的文档站点
- **When**: 在搜索框输入中文关键词（如"Conda"、"Sphinx"）
- **Then**: 搜索结果返回 bundles 中相关文档页面
- **Verification**: `human-judgment`

### AC-7: 响应式布局

- **Given**: 构建后的文档站点
- **When**: 在不同屏幕宽度下浏览（手机 375px、平板 768px、桌面 1200px）
- **Then**: 导航栏、正文、代码块、表格均正常显示，无水平溢出
- **Verification**: `human-judgment`

### AC-8: 依赖可安装

- **Given**: 干净的 Python 3.14 环境
- **When**: 执行 `pip install -e ".[doc]"`
- **Then**: 所有文档构建依赖安装成功，无版本冲突
- **Verification**: `programmatic`

## Open Questions

- [ ] 是否需要配置 ReadTheDocs 构建（`.readthedocs.yml`）？mystx 模板中有此文件，但 awesome-okf-xs 可能暂不需要
- [ ] 是否需要配置 GitHub Actions 自动构建和部署？
- [ ] 主题选择：直接使用 sphinx-book-theme 还是尝试安装 mystx 本地包？mystx 位于 playground/books/libs/mystx，可通过 `pip install -e` 安装
- [ ] 是否需要启用 sphinx-autoapi？awesome-okf-xs 无 Python 源码，默认不启用
- [ ] bundles 中的 `log.md` 文件是否需要在站点中展示？（OKF 保留文件，通常为更新日志）
