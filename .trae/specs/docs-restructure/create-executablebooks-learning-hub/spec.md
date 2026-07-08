---
version: 1.0
x-toml-ref: "../../../../.meta/toml/.trae/specs/docs-restructure/create-executablebooks-learning-hub/spec.toml"
---
# ExecutableBooks 学习资料库建设 - Product Requirement Document

## Overview
- **Summary**: 系统学习 ExecutableBooks 官方文档核心内容，在项目 `docs/knowledge/learning/` 目录下创建一个专门的 `executablebooks-myst-guide/` 学习资料文件夹，包含 MyST Markdown 语法、项目结构、配置方法、最佳实践等结构化学习资料，并提供清晰的目录结构便于后续扩展wiki文档、使用示例和配置模板。
- **Purpose**: 用户偏好使用 myst-parser，需要建立系统化的 ExecutableBooks/MyST Markdown 学习资料库，为项目中 MyST 语法的标准化使用提供参考依据，方便团队成员快速查阅和学习。
- **Target Users**: SpecWeave 项目开发者、文档编写者、所有需要使用 MyST Markdown 进行技术文档编写的团队成员。

## Goals
- 创建规范命名的 ExecutableBooks 学习资料文件夹，位置符合项目文档组织逻辑
- 建立清晰的子目录结构，分类存放语法文档、使用示例、配置模板等学习资源
- 系统整理 MyST Markdown 核心语法（Directives、Roles、Fences 等）
- 整理 MyST 项目结构和配置方法（myst.yml、frontmatter、TOC 等）
- 提供可直接复用的配置模板和使用示例
- 编写入口文档（README）作为快速导航和学习路径指引
- 更新 `docs/knowledge/README.md` 索引，将新学习资料纳入知识库体系

## Non-Goals (Out of Scope)
- 不深入研究 Jupyter Book v1（Sphinx/Python 版本）的详细实现
- 不进行 mystmd CLI 工具的实际安装和运行验证
- 不创建复杂的 MyST 插件或主题开发教程
- 不将现有项目文档迁移到 MyST 格式（仅提供学习资料）
- 不覆盖 ExecutableBooks 生态的所有高级特性（仅核心内容）

## Background & Context
- 用户在 user_profile.md 中明确偏好 myst-parser
- 项目现有 `docs/knowledge/learning/` 目录已用于存放学习资料，已有 karpathy-llm-coding-guidelines/、agent-skills-wiki/ 等成熟案例
- MyST (Markedly Structured Text) 是 ExecutableBooks 项目的核心，是 CommonMark 的超集，灵感来自 Sphinx/reStructuredText 生态
- MyST 支持 directives（块级扩展）和 roles（行内扩展），广泛用于科学计算和技术文档
- mystmd 是新一代的 JavaScript 实现，支持导出 HTML/PDF/Word/LaTeX 等多种格式
- 项目现有开发规范中已提及 Markdown 的使用，但缺乏系统化的 MyST 语法参考

## Functional Requirements
- **FR-1**: 在 `docs/knowledge/learning/` 下创建 `executablebooks-myst-guide/` 主文件夹
- **FR-2**: 建立子目录结构：syntax/（语法）、examples/（示例）、templates/（配置模板）、resources/（参考资源）
- **FR-3**: 编写 00-overview.md：ExecutableBooks 生态概览、MyST 定位、核心特性介绍
- **FR-4**: 编写 01-myst-syntax.md：MyST 核心语法详解（Directives、Roles、Fences、嵌套等）
- **FR-5**: 编写 02-project-structure.md：MyST 项目结构、myst.yml 配置、目录组织规范
- **FR-6**: 编写 03-frontmatter-config.md：Frontmatter 配置详解（元数据、作者、许可、导出等）
- **FR-7**: 编写 04-table-of-contents.md：目录结构配置（TOC）、导航组织、URL Slug 规则
- **FR-8**: 创建 myst.yml 配置模板（templates/myst.yml.template），包含常用配置项和注释
- **FR-9**: 创建基础使用示例（examples/），包含常见 directives 和 roles 的演示
- **FR-10**: 编写 05-best-practices.md：MyST 使用最佳实践和注意事项
- **FR-11**: 编写 06-resources.md：官方资源链接、进一步学习指引
- **FR-12**: 编写主入口 README.md，提供学习路径、文档导航、快速参考
- **FR-13**: 更新 `docs/knowledge/README.md`，将新学习资料加入知识库索引

## Non-Functional Requirements
- **NFR-1**: 所有 Markdown 文档遵循项目现有 Markdown 编写规范（相对路径引用、TOML frontmatter、source 溯源）
- **NFR-2**: 文档命名采用数字前缀 + kebab-case 风格，与现有 learning 目录保持一致
- **NFR-3**: 文档内容准确，基于官方文档（mystmd.org、executablebooks.org）整理，不编造信息
- **NFR-4**: 目录结构具有可扩展性，预留后续添加更多 wiki 文档和示例的空间
- **NFR-5**: 代码示例和配置模板可直接复用，包含必要的注释说明

## Constraints
- **Technical**: 文档使用 Markdown 格式，遵循项目现有 frontmatter 规范（TOML 格式的 source 字段）
- **Business**: 学习资料聚焦核心内容，避免过度深入高级特性导致范围蔓延
- **Dependencies**: 参考官方文档 https://mystmd.org 和 https://executablebooks.org/en/latest/

## Assumptions
- 用户需要的是 mystmd（新一代 JavaScript 实现）的核心内容，而非旧版 Jupyter Book v1
- 学习资料主要用于参考查阅，不需要立即在项目中实际部署 mystmd
- 现有项目的 Markdown 编写规范仍适用，MyST 是扩展而非替代
- 文件夹命名使用 executablebooks-myst-guide/ 清晰表达内容，符合项目命名惯例

## Acceptance Criteria

### AC-1: 文件夹结构创建
- **Given**: 项目已存在 `docs/knowledge/learning/` 目录
- **When**: 完成学习资料文件夹创建
- **Then**: `docs/knowledge/learning/executablebooks-myst-guide/` 存在，包含 syntax/、examples/、templates/、resources/ 子目录
- **Verification**: `programmatic`
- **Notes**: 子目录可先创建空目录并添加 .gitkeep 文件

### AC-2: 入口文档和学习路径
- **Given**: 文件夹结构已创建
- **When**: 查看主入口 README.md
- **Then**: README.md 包含项目简介、学习路径指引、所有子文档的导航链接、快速参考表
- **Verification**: `human-judgment`

### AC-3: MyST 核心语法文档
- **Given**: 语法文档编写完成
- **When**: 阅读 01-myst-syntax.md
- **Then**: 文档清晰解释 Directives、Roles、Fences（冒号围栏 vs 反引号围栏）、嵌套语法、选项配置（key:value、YAML、inline options），并配有示例
- **Verification**: `human-judgment`

### AC-4: 项目结构和配置文档
- **Given**: 配置文档编写完成
- **When**: 阅读 02-project-structure.md 和 03-frontmatter-config.md
- **Then**: 文档说明 myst.yml 的 project 和 site 配置、frontmatter 字段分类（page/project/override）、常用字段（title/authors/license/bibliography等）
- **Verification**: `human-judgment`

### AC-5: 配置模板和示例
- **Given**: 模板和示例文件创建完成
- **When**: 查看 templates/myst.yml.template 和 examples/ 目录
- **Then**: 配置模板包含常用配置项和中文注释，示例文件展示至少 5 种常用 directives/roles 的用法
- **Verification**: `human-judgment`

### AC-6: 目录结构配置文档
- **Given**: TOC 文档编写完成
- **When**: 阅读 04-table-of-contents.md
- **Then**: 文档说明 TOC 树结构（file/url/pattern/children）、嵌套页面、glob 模式匹配、隐藏页面、页面内 TOC 指令
- **Verification**: `human-judgment`

### AC-7: 最佳实践和资源
- **Given**: 最佳实践和资源文档编写完成
- **When**: 阅读 05-best-practices.md 和 06-resources.md
- **Then**: 最佳实践包含围栏选择建议、frontmatter 组织建议、常见陷阱；资源文档包含官方链接、进一步学习路径
- **Verification**: `human-judgment`

### AC-8: 知识库索引更新
- **Given**: 所有学习资料编写完成
- **When**: 查看 docs/knowledge/README.md
- **Then**: 新的 executablebooks-myst-guide 已添加到知识库索引中，与其他学习资料并列
- **Verification**: `programmatic`

### AC-9: 文档规范合规
- **Given**: 所有文档编写完成
- **When**: 检查所有 Markdown 文件
- **Then**: 所有文档包含 TOML frontmatter（含 source 字段）、使用相对路径引用、命名规范一致、无 file:/// 绝对路径
- **Verification**: `programmatic`

## Open Questions
- [ ] 是否需要同时包含 Jupyter Book v1（Python/Sphinx 版本）的相关内容，还是仅聚焦 mystmd？
- [ ] examples/ 目录下需要提供哪些具体场景的示例？（建议：基础语法、学术论文、书籍项目、网站配置）
- [ ] 是否需要提供与现有项目 Markdown 规范的对比说明（CommonMark vs MyST 差异）？
