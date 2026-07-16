---
version: 1.0
---

# SpecWeave Sphinx 文档站点创建 - Product Requirement Document

## Overview
- **Summary**: 基于 Sphinx 文档生成工具创建 SpecWeave 项目的人类可读文档站点 `d:\spaces\SpecWeave\docs`，以 `vendor/flexloop/docs` 为参考模板，复制必要配置文件、继承模板样式、保持相似目录结构，并验证 HTML 构建正常。
- **Purpose**: 解决当前项目文档分散在 `.agents/docs/`（面向 AI 智能体）缺少面向人类读者的结构化、可构建、可发布的文档站点问题，建立与 flexloop 一致的双轨文档体系（技术文档 + 通用知识 + 设计洞见）。
- **Target Users**: SpecWeave 项目开发者、贡献者、最终用户，以及希望通过 Sphinx HTML 站点浏览项目文档的读者。

## Goals
- 创建 `docs/` 目录结构，与 `vendor/flexloop/docs` 保持一致的三轨分类（tech/、general/、topics/）
- 复制并适配核心配置文件：`conf.py`、`_config.toml`、`tasks.py`
- 复制静态资源与自定义样式：`_static/` 目录下的 CSS、图片等
- 创建各模块入口 `index.md` 与根入口 `index.md`
- 根据 SpecWeave 项目特性调整配置（项目名称、作者、仓库链接、移除不需要的 autoapi 配置等）
- 验证文档能够通过 Sphinx 正常构建为 HTML，无致命错误

## Non-Goals (Out of Scope)
- 不迁移现有 `.agents/docs/` 下的所有内容到新文档站点（仅创建骨架和初始内容）
- 不配置 CI/CD 自动部署到 Read the Docs 或 GitHub Pages
- 不创建 pyproject.toml 或管理 Python 依赖环境（仅验证构建能力）
- 不修改 vendor/flexloop 内的任何文件
- 不实现 sphinx-autoapi 自动 API 文档生成（SpecWeave 是规范项目，无 Python 源码包）

## Background & Context
- **参考模板**：`vendor/flexloop/docs/` 使用 Sphinx + MyST Parser + sphinx-book-theme 构建，采用三轨文档结构：
  - `tech/`：项目技术文档（介绍、快速开始、功能、部署、贡献指南等）
  - `general/`：通用知识（哲学、宇宙学、语言学等跨学科内容）
  - `topics/`：设计洞见与深度研究（设计哲学、行业分析、架构洞察等）
- **当前状态**：SpecWeave 根目录无 `docs/` 文件夹，所有文档位于 `.agents/docs/`，该目录面向 AI 智能体而非人类读者，缺少 Sphinx 构建配置、主题样式和结构化导航。
- **技术选型**：沿用参考模板的技术栈（Sphinx + MyST + sphinx-book-theme），保持一致性；移除 autoapi 等 SpecWeave 不需要的扩展配置。
- **项目信息**：
  - 项目名称：SpecWeave
  - 作者：SpecWeave Team
  - 仓库地址：https://gitcode.com/daoCollective/SpecWeave（国内镜像）/ https://github.com/SpecWeave/SpecWeave
  - 许可证：Apache-2.0

## Functional Requirements
- **FR-1**: 创建 `docs/` 目录及其子目录结构：`_static/`、`_static/images/`、`tech/`、`general/`、`topics/`、`_templates/`
- **FR-2**: 创建适配 SpecWeave 的 `conf.py` 配置文件，包含：
  - 正确的项目信息（名称、作者、版权）
  - 中文本地化设置（language = "zh_CN"）
  - MyST Parser 扩展支持（myst_enable_extensions 配置）
  - sphinx-book-theme 主题配置
  - 必要的扩展：myst_parser、sphinx_design、sphinxcontrib.mermaid、sphinx_copybutton、sphinx.ext.intersphinx、sphinx.ext.napoleon
  - 移除 autoapi 和 bibtex 相关配置（当前不需要）
  - Windows 事件循环兼容（参考 flexloop 的处理方式）
  - 从 `_config.toml` 加载主题选项
- **FR-3**: 创建 `_config.toml` 主题配置文件，包含：
  - SpecWeave 的 logo 配置（暂时复用或使用占位，优先复用 assets/brand/ 下的资源）
  - 仓库链接配置（GitCode 为主）
  - 导航栏深度、按钮显示等界面配置
  - 移除 mybinder、colab 等启动按钮配置
- **FR-4**: 创建 `tasks.py` Invoke 任务脚本，提供 build/html/clean/linkcheck 命令（适配 Windows）
- **FR-5**: 创建根入口 `index.md`：
  - 包含 README.md 内容引用（使用 include 指令）
  - 三轨 toctree 导航（tech/index、general/index、topics/index）
  - 重点阅读推荐
- **FR-6**: 创建 `tech/index.md` 技术文档入口，包含 toctree 和目录说明
- **FR-7**: 创建 `general/index.md` 通用知识入口，包含 toctree 和目录说明
- **FR-8**: 创建 `topics/index.md` 设计洞见入口，包含 toctree 和目录说明
- **FR-9**: 复制并适配 `_static/` 下的必要静态资源：
  - `local.css`（响应式样式，可直接复用）
  - `variables.css`（CSS 变量定义）
  - `mermaid.css`（Mermaid 图表样式）
  - 复制或创建 favicon 和 logo 图片
- **FR-10**: 为 tech/ 目录创建初始占位文档：`intro.md`、`quickstart.md`、`features.md`、`contributing.md`、`changelog.md`
- **FR-11**: 配置正确的 html_baseurl 和 sitemap（适配本地开发默认值）

## Non-Functional Requirements
- **NFR-1**: 所有 Markdown 文件使用 UTF-8 编码，符合项目现有规范
- **NFR-2**: 文档中的路径引用使用相对路径，符合 SpecWeave 路径引用规范
- **NFR-3**: 配置文件应具有良好的可读性，关键配置有注释说明
- **NFR-4**: 构建过程在 Windows 环境下兼容（使用 SelectorEventLoopPolicy）
- **NFR-5**: CSS 样式文件应保持与参考模板一致的响应式设计和暗色模式支持
- **NFR-6**: 文档结构应具有可扩展性，新增文档时只需在对应 index.md 的 toctree 中追加条目

## Constraints
- **Technical**:
  - Python >= 3.9 兼容（项目整体要求 >= 3.13，但 conf.py 应保持基本兼容性）
  - 使用 MyST Parser 解析 Markdown（myst_parser 而非 mystx，降低依赖要求）
  - 优先使用 sphinx-book-theme 作为主题
  - Windows 平台优先适配（参考 flexloop 的 Windows 事件循环修复）
- **Business**:
  - 不修改 vendor/flexloop 内的任何文件（只读参考）
  - 不引入不必要的依赖（仅使用 Sphinx 文档构建必需的包）
- **Dependencies**:
  - sphinx >= 7.0.0
  - myst-parser >= 2.0.0
  - sphinx-book-theme
  - sphinx-design
  - sphinx-copybutton
  - sphinxcontrib-mermaid
  - invoke（用于 tasks.py）

## Assumptions
- 用户环境中已安装或可安装 Sphinx 及必要扩展（构建验证时会检查）
- SpecWeave 现有 `assets/brand/` 下的 logo 资源可以被文档复用
- 初始内容只需要骨架和占位，后续内容迁移是另一个任务
- `_templates/` 目录可以为空（flexloop 中 templates_path 配置了但可能为空）

## Acceptance Criteria

### AC-1: 目录结构完整创建
- **Given**: 项目根目录 `d:\spaces\SpecWeave`
- **When**: 执行完目录创建任务后
- **Then**: `docs/` 目录下存在以下子目录：`_static/`、`_static/images/`、`tech/`、`general/`、`topics/`、`_templates/`
- **Verification**: `programmatic`
- **Notes**: 使用 LS 或 Glob 工具验证目录存在

### AC-2: 配置文件存在且语法正确
- **Given**: `docs/` 目录已创建
- **When**: 检查配置文件
- **Then**: `conf.py`、`_config.toml`、`tasks.py` 文件存在，且 Python 语法检查通过（`python -m py_compile docs/conf.py docs/tasks.py` 无错误）
- **Verification**: `programmatic`

### AC-3: conf.py 项目信息正确配置
- **Given**: `docs/conf.py` 已创建
- **When**: 读取配置文件检查
- **Then**: project = "SpecWeave"、author 包含 SpecWeave Team、language = "zh_CN"、html_theme 为 sphinx-book-theme 或降级主题、MyST 扩展已配置
- **Verification**: `programmatic` + `human-judgment`

### AC-4: 入口文档存在且 toctree 正确
- **Given**: 各 index.md 文件已创建
- **When**: 检查入口文档
- **Then**: `index.md`、`tech/index.md`、`general/index.md`、`topics/index.md` 存在，且根 index.md 的 toctree 正确引用三个子入口
- **Verification**: `programmatic`

### AC-5: 静态资源已复制
- **Given**: `_static/` 目录已创建
- **When**: 检查静态文件
- **Then**: `local.css`、`variables.css`、`mermaid.css` 存在，`images/` 目录下有 favicon 和 logo 文件
- **Verification**: `programmatic`

### AC-6: tech 目录初始文档存在
- **Given**: `tech/` 目录已创建
- **When**: 检查初始文档
- **Then**: `intro.md`、`quickstart.md`、`features.md`、`contributing.md`、`changelog.md` 文件存在，且在 `tech/index.md` 的 toctree 中正确引用
- **Verification**: `programmatic`

### AC-7: Sphinx 配置检查通过（无致命错误）
- **Given**: 所有配置文件已就位
- **When**: 运行 `sphinx-build -b html docs docs/_build/html -W --keep-going` 或等价命令（如果环境有依赖）
- **Then**: 构建过程能够完成，无 Configuration error 类致命错误（允许内容警告如文档未找到，但不允许配置错误）
- **Verification**: `programmatic`
- **Notes**: 如果环境未安装 Sphinx 依赖，至少验证 `sphinx-build -b html -c docs -D html_theme=alabaster docs docs/_build/html` 的配置解析能力；或在安装依赖后执行完整构建

### AC-8: HTML 输出文件生成
- **Given**: Sphinx 构建成功执行
- **When**: 检查构建输出目录
- **Then**: `docs/_build/html/index.html` 存在，且可在浏览器中打开显示基本页面结构
- **Verification**: `programmatic` + `human-judgment`

### AC-9: Windows 兼容性处理
- **Given**: 在 Windows 环境下运行
- **When**: 执行 conf.py 或构建
- **Then**: 无 asyncio 事件循环相关错误（SelectorEventLoopPolicy 已配置）
- **Verification**: `programmatic`

### AC-10: tasks.py 任务可列出
- **Given**: `tasks.py` 已创建
- **When**: 在 docs 目录下运行 `invoke --list` 或 `python -m invoke --list`
- **Then**: 能列出 build、html、clean、linkcheck、help 等任务
- **Verification**: `programmatic`
- **Notes**: 如果 invoke 未安装，至少验证 Python 语法正确且任务函数存在

## Open Questions
- [ ] SpecWeave 的官方 logo 是否有标准深色/浅色版本？目前 `assets/brand/` 下只有 xuantong-logo.png
- [ ] 文档站点的最终部署目标是什么（Read the Docs / GitHub Pages / GitCode Pages / 本地使用）？
- [ ] 是否需要配置 BibTeX 参考文献支持？当前 flexloop 使用了但 SpecWeave 初始可能不需要
- [ ] 现有 `.agents/docs/` 下的内容迁移计划是否在本任务范围内？（PRD 中暂列为 Non-Goal）
