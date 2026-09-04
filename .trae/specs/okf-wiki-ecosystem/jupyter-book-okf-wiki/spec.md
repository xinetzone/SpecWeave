---
status: "draft"
id: jupyter-book-okf-wiki-spec
title: Jupyter Book v2 / MySTmd 生态系统 OKF Wiki 教程生成 - PRD
date: 2026-08-23
category: spec
maturity: L0-draft
---

# Jupyter Book v2 / MySTmd 生态系统 OKF Wiki 教程 - Product Requirement Document

## Problem Statement

Jupyter Book v2 与 MySTmd（MyST Markdown Engine）是 Executable Books 组织推出的新一代技术文档工具链，采用 TypeScript 实现统一的 Markdown 解析、多格式导出（HTML/LaTeX/PDF/DOCX/JATS/Typst/Markdown）、Notebook 执行、交互式代码运行等能力。源码位于 monorepo 中，包含 13 个顶级子目录和 mystmd/packages 下 38 个 npm 包，架构复杂，模块间依赖关系紧密。现有官方文档以英文用户指南为主，缺少从源码架构角度的系统化中文教程，导致开发者理解内部机制、扩展指令/角色/导出格式、调试构建问题时学习成本高。

## Users

- **技术文档工程师**：需要理解 MyST 解析管线和主题系统以定制文档站点
- **Jupyter 生态开发者**：需要理解 Notebook 执行机制和 Thebe 交互式运行原理以扩展功能
- **Markdown 工具开发者**：需要理解 unified/micromark 插件架构和 MDAST 转换管线
- **出版工具开发者**：需要理解多格式导出器（HTML/LaTeX/DOCX/JATS/Typst）的实现机制
- **JupyterLab 扩展开发者**：需要理解 jupyterlab-myst 的渲染机制和 MIME 类型处理

## Goals

- 使用 `source-code-to-okf-wiki` 技能（R→I→E→V→C 五阶段链路）系统化学习 `external/libs/ai/jupyter-book/` 下所有有实质代码的核心子项目源码
- 在 `projects/awesome-okf-xs/bundles/jupyter-book/` 下创建 OKF v0.2 规范的知识束（Bundle），产出结构化中文源码教程
- 通过 `seven-concepts-cmd` 方法论编排知识沉淀链路，确保质量门 G1-G4 全部通过
- 每个知识束遵循 concepts/examples/references 三层结构，frontmatter 完整，交叉引用正确
- 所有文档中的 API/类名/方法名经过 Grep 级源码验证，杜绝虚构内容

## Non-Goals (Out of Scope)

- 不做官方文档的完整翻译或复述
- 不覆盖 mystmd/packages 中每个包的逐行源码解析（38个包数量过多，采用功能聚合分组策略）
- 不覆盖示例项目和网站项目（blog/, example-*/, jupyterbook.org/, mystmd.org/, team-compass/）
- 不覆盖纯配置/工具包的深度解析（tsconfig/, eslint-config-thebe/）
- 不深入 myst-plugins/（纯示例插件集合，无实质库代码）
- 不修改 awesome-okf-xs 子项目的 `.agents/` 规范文件（走子项目流程）
- 不生成 git 提交（用户未要求）
- 不覆盖旧版 Executable Books Python 生态（已有 bundles/myst/ 分组覆盖 markdown-it-py/MyST-Parser/MyST-NB 等）

## Source Code Inventory

源码根目录：`d:\spaces\SpecWeave\external\libs\ai\jupyter-book\`

### 子项目清单（13个顶级目录）

| 子项目 | 语言 | 代码规模 | 包含级别 | 说明 |
|--------|------|---------|---------|------|
| **jupyter-book/** | Python + TypeScript | 小 | Tier 2 | Jupyter Book v2 CLI：Python薄包装(jupyter_book/__main__.py)调用TS构建的CJS bundle，核心功能委托给myst-cli |
| **mystmd/** | TypeScript (monorepo, 38 packages) | 极大（核心项目） | Tier 1 | MyST 引擎主仓库：解析器、转换器、导出器、CLI、配置、指令、角色、执行等核心能力 |
| **jupyterlab-myst/** | TypeScript + Python | 中 | Tier 2 | JupyterLab MyST 扩展：在 JupyterLab 中渲染 MyST Markdown，支持富文本输出 |
| **myst-theme/** | TypeScript + CSS | 中 | Tier 2 | MyST 主题系统：Book/Article 双主题、Remix 框架、CSS 组件库、模板系统 |
| **thebe/** | TypeScript (monorepo, 6 packages) | 中 | Tier 2 | Thebe 交互式代码执行：连接 Binder/Jupyter 内核，实现页面内代码运行 |
| **myst-plugins/** | Markdown | 小（示例） | 排除 | 插件示例集合，无实质库代码 |
| **blog/** | Markdown | 排除 | - | Jupyter Book 博客网站，纯内容 |
| **example-js-anywidget/** | JS/MD | 排除 | - | anywidget 示例 |
| **example-outputs/** | MD | 排除 | - | 输出格式示例 |
| **example-widgets/** | JS/MD | 排除 | - | 小部件示例 |
| **jupyterbook.org/** | MD/TS | 排除 | - | Jupyter Book 官网 |
| **mystmd.org/** | MD/TS | 排除 | - | MyST 官网（Remix应用） |
| **team-compass/** | MD/JS | 排除 | - | 团队指南针文档 |

### mystmd/packages 功能分组（38个包 → 聚合为知识束）

mystmd 是核心 monorepo，38个包按功能聚合为知识束（避免每个包独立建bundle导致碎片化）：

| 知识束 | 聚合的 npm 包 | Tier | 说明 |
|--------|-------------|------|------|
| **mystmd** | myst-parser, myst-transforms, myst-common, myst-config, myst-frontmatter, myst-spec, myst-spec-ext, simple-validators, mystmd, mystmd-py, markdown-it-myst, citation-js-utils | Tier 1 | MyST 引擎核心：解析器（micromark/mdast插件）、MDAST转换管线、公共类型/工具、配置加载、frontmatter解析、MyST规范定义、主包入口、Python绑定 |
| **myst-cli** | myst-cli, myst-cli-utils, myst-migrate, myst-toc, myst-templates | Tier 1 | 命令行工具：build/start/init/clean 命令、项目加载、TOC生成、模板管理、版本迁移、会话缓存 |
| **myst-syntax** | myst-directives, myst-roles, myst-ext-button, myst-ext-card, myst-ext-exercise, myst-ext-grid, myst-ext-icon, myst-ext-proof, myst-ext-reactive, myst-ext-tabs | Tier 2 | 语法扩展：核心指令（code/figure/table/embed/math/toc/include等）、核心角色（cite/ref/abbr/math/doc/eq等）、UI扩展组件（按钮/卡片/练习/网格/图标/证明/响应式/标签页） |
| **myst-exporters** | myst-to-html, myst-to-tex, myst-to-docx, myst-to-jats, myst-to-md, myst-to-typst, jtex, jats-to-myst, tex-to-myst | Tier 2 | 多格式导出：HTML/LaTeX/DOCX/JATS XML/Markdown/Typst 输出、jtex LaTeX/Typst模板引擎、JATS/LaTeX导入 |
| **myst-execute** | myst-execute | Tier 2 | Notebook执行：Jupyter内核管理、代码缓存、输出转换、执行配置 |

### 独立子项目知识束

| 知识束 | 源码目录 | Tier | 说明 |
|--------|---------|------|------|
| **jupyter-book** | jupyter-book/ | Tier 2 | Jupyter Book v2 CLI（Python包装层 + TS CLI入口） |
| **thebe** | thebe/ (core/lite/react/build-config) | Tier 2 | 交互式代码执行库：核心API、Binder/Jupyter连接、React hooks、Lite(pyodide)支持 |
| **jupyterlab-myst** | jupyterlab-myst/ | Tier 3 | JupyterLab扩展：MyST渲染器、MIME类型、插件激活、IPython集成 |
| **myst-theme** | myst-theme/ (themes/book+article, styles/, template/) | Tier 2 | 主题系统：Book/Article双主题、CSS组件、Remix路由、模板服务器 |

**总计：8个知识束**（4个Tier 1/2核心mystmd包组 + 4个独立子项目）

## Functional Requirements

### FR-1: 创建 Jupyter Book 生态分类目录
- 在 `bundles/jupyter-book/` 下创建分类索引 `index.md`，列出所有 8 个子项目知识束
- 分类索引包含 `okf_version: "0.2"` frontmatter 和生态关系概览图
- 生态关系图展示从解析→转换→导出→主题→交互→CLI的完整管线

### FR-2: mystmd 核心引擎知识束（Tier 1，最高深度）
- 创建 `bundles/jupyter-book/mystmd/` 目录
- **concepts/**（10-14 篇）：MySTmd 整体架构、unified/micromark/mdast 插件体系、MyST 解析器（myst-parser）、MDAST 转换管线（myst-transforms）、公共类型与节点选择（myst-common）、配置系统（myst-config）、Frontmatter 解析（myst-frontmatter）、MyST 语法规范（myst-spec）、验证器（simple-validators）、引用工具（citation-js-utils）、markdown-it-myst 兼容层、Python 绑定（mystmd-py）
- **examples/**（3-5 篇）：使用 myst-parser 解析 Markdown、编写自定义 transform、配置项目、解析 frontmatter
- **references/**（5-8 篇）：myst-parser/src/fromMarkdown.ts、myst-transforms 核心转换、myst-common/types.ts、myst-config 配置加载、myst-frontmatter 解析入口

### FR-3: myst-cli 命令行工具知识束（Tier 1）
- 创建 `bundles/jupyter-book/myst-cli/` 目录
- **concepts/**（8-10 篇）：CLI 架构与命令注册、build 命令管线（多格式导出）、start 开发服务器、init 项目初始化、clean 清理、项目加载与TOC生成（myst-toc）、模板系统（myst-templates）、版本迁移（myst-migrate）、会话缓存与日志
- **examples/**（3-4 篇）：初始化MyST项目、构建静态站点、启动开发服务器、迁移旧版项目
- **references/**（3-5 篇）：myst-cli/src/cli/index.ts、build 流程入口、project/load.ts、session/session.ts

### FR-4: myst-syntax 语法扩展知识束（Tier 2）
- 创建 `bundles/jupyter-book/myst-syntax/` 目录
- **concepts/**（7-9 篇）：指令系统架构（myst-directives）、角色系统架构（myst-roles）、核心指令（admonition/code/figure/table/embed/include/math/toc）、核心角色（cite/ref/abbr/term/doc/eq）、UI扩展-按钮与卡片（button/card）、UI扩展-布局（grid/tabs/icon）、UI扩展-学术（proof/exercise）、响应式扩展（reactive）
- **examples/**（2-3 篇）：使用核心指令、自定义指令开发、使用UI扩展组件
- **references/**（3-4 篇）：myst-directives/src/index.ts 指令注册、myst-roles/src/index.ts 角色注册、扩展组件入口

### FR-5: myst-exporters 多格式导出知识束（Tier 2）
- 创建 `bundles/jupyter-book/myst-exporters/` 目录
- **concepts/**（7-9 篇）：导出器架构与统一接口、HTML导出（myst-to-html）、LaTeX导出（myst-to-tex）、PDF导出流程、DOCX导出（myst-to-docx）、JATS XML导出（myst-to-jats）、Markdown导出（myst-to-md）、Typst导出（myst-to-typst）、jtex模板引擎、JATS/LaTeX导入
- **examples/**（2-3 篇）：导出为多格式、自定义jtex模板、从LaTeX导入
- **references/**（3-4 篇）：各导出器入口文件、jtex/src/jtex.ts、统一导出接口

### FR-6: jupyter-book CLI 知识束（Tier 2）
- 创建 `bundles/jupyter-book/jupyter-book/` 目录
- **concepts/**（4-6 篇）：Jupyter Book v2 架构、Python入口与Node环境管理（nodeenv.py）、TS CLI命令（init/build/clean/site/templates）、与myst-cli的关系、模板系统
- **examples/**（2 篇）：创建Jupyter Book、构建与发布
- **references/**（2-3 篇）：py/jupyter_book/__main__.py、ts/clirun.ts、ts/index.ts

### FR-7: myst-execute 与 thebe 交互式执行知识束（Tier 2，合并执行能力）
- 创建 `bundles/jupyter-book/myst-execute/` 目录
- **concepts/**（6-8 篇）：代码执行架构概览、myst-execute内核管理、执行缓存与输出转换、Thebe核心API（core/entrypoint）、Thebe配置与选项、Thebe Binder/Jupyter服务器连接、Thebe Lite（Pyodide）支持、Thebe React集成
- **examples/**（2-3 篇）：配置Notebook执行、使用Thebe实现页面内交互、Thebe Lite无服务器执行
- **references/**（3-4 篇）：myst-execute/src/execute.ts、thebe/core/src/index.ts、thebe/lite/src/index.ts、thebe/react/src/index.ts

### FR-8: jupyterlab-myst JupyterLab扩展知识束（Tier 3）
- 创建 `bundles/jupyter-book/jupyterlab-myst/` 目录
- **concepts/**（4-5 篇）：扩展架构与激活、MyST渲染器（renderers.tsx）、MIME类型处理（mime.tsx）、IPython widget集成（widget.tsx）、JupyterLab集成
- **examples/**（1-2 篇）：在JupyterLab中使用MyST
- **references/**（2 篇）：src/index.ts 插件入口、src/renderers.tsx 渲染器

### FR-9: myst-theme 主题系统知识束（Tier 2）
- 创建 `bundles/jupyter-book/myst-theme/` 目录
- **concepts/**（5-7 篇）：主题系统架构、Book主题、Article主题、CSS组件库（styles/）、Remix路由与导航、模板服务器（template/）、主题定制
- **examples/**（2 篇）：定制Book主题、使用Article主题
- **references/**（2-3 篇）：themes/book/、styles/index.js、template/

### FR-10: 每个知识束的 OKF 结构完整性
- 每个 bundle 包含：`index.md`（根索引，含 okf_version）、`log.md`（变更日志）、`concepts/index.md`（概念索引，无 frontmatter）、`examples/index.md`（示例索引）、`references/index.md`（信源索引）
- 每个内容文档包含完整 YAML frontmatter：`type`、`title`、`description`、`tags`、`generated`、`verified`、`status`、`stale_after`、`sources`
- 子目录 `index.md` 不含 frontmatter

### FR-11: 方法论遵循
- 每个知识束严格遵循 source-code-to-okf-wiki 五阶段流程：R（事实采集）→ I（架构洞察）→ E（批量生成）→ V（独立验证）→ C（模式沉淀）
- 通过 seven-concepts-cmd 编排知识沉淀场景链路（R→I→E）
- R 阶段：每个子项目提取编号事实清单（F-xxx），写入各 bundle 的 `spec/facts.md`，零推测
- I 阶段：每个子项目提炼 3-5 个核心洞察（陈述+证据+反常识+行动四元组），写入 `spec/insights.md`
- E 阶段：信源先行（references/ 先生成）、分批生成（每批≤7 文件）、index 最后写
- V 阶段：Grep 级 API 真实性验证、链接检查、frontmatter 检查
- 所有事实和洞察的中间产物存放于 `.trae/specs/okf-wiki-ecosystem/jupyter-book-okf-wiki/` 下对应子项目的 spec 子目录

### FR-12: 更新 bundles 总索引
- 在 `bundles/index.md` 中新增"📖 Jupyter Book v2 / MySTmd 生态"分组
- 更新 total_bundles 和 groups 计数
- 注意：现有 `bundles/myst/` 分组覆盖旧版 Executable Books Python 生态，新分组 `jupyter-book/` 覆盖新一代 TypeScript 生态，两者互不冲突

## Non-Functional Requirements

- **NFR-1（语言）**：所有文档正文使用中文，技术术语保留英文并在首次出现时括号注释
- **NFR-2（文件命名）**：文件名使用 kebab-case 纯英文，概念文档按学习路径编号（00-xxx.md, 01-xxx.md, ...）
- **NFR-3（路径引用）**：交叉引用使用 `/` 开头的 bundle-relative 绝对路径
- **NFR-4（溯源）**：每个文档的 `sources` 字段指向对应 references/ 信源文件和事实编号
- **NFR-5（真实性）**：所有引用的类名、方法名、API 签名必须能在源码中通过 Grep 验证存在（TypeScript 类/函数/接口/导出）
- **NFR-6（代码示例）**：代码块标注语言（ts/tsx/python/css等），代码示例基于实际源码 API 编写，不凭记忆编造
- **NFR-7（原子性）**：每个概念文档聚焦单一主题，控制在合理长度（避免单文件过长）
- **NFR-8（stale_after）**：统一设置为 `2027-12-31`（MySTmd 核心架构稳定，大版本变更需重新评估）
- **NFR-9（TypeScript特性）**：TypeScript 代码需准确呈现类型签名、接口定义、泛型参数，区分命名导出与默认导出

## Constraints

- **规范约束**：产出物必须符合 OKF v0.2 规范和 awesome-okf-xs frontmatter 规范
- **格式参考**：以现有 `bundles/onnx/onnx/` 为格式范本（Tier 1 深度）
- **源码路径**：源码位于 `external/libs/ai/jupyter-book/`，为第三方代码（禁止修改）
- **目标路径**：产出物位于 `projects/awesome-okf-xs/bundles/jupyter-book/`，该子项目是 git submodule
- **禁止修改范围**：不修改 awesome-okf-xs 子项目的 `.agents/` 目录、AGENTS.md 等规范文件
- **分批约束**：E 阶段每批生成不超过 7 个文件，防止上下文过载
- **验证约束**：V 阶段必须对每个文档中引用的关键类名/方法名/接口名执行 Grep 验证
- **包聚合约束**：mystmd/packages 下的 38 个包按功能聚合为 4 个知识束（mystmd/myst-cli/myst-syntax/myst-exporters），不为每个包单独建bundle

## Dependencies

- `source-code-to-okf-wiki` Skill：提供 R→I→E→V→C 五阶段工作流和质量门
- `seven-concepts-cmd` Skill：提供知识沉淀场景的方法论编排
- 现有 OKF 规范文档：`bundles/meta/okf-spec/` 作为格式标准
- 现有 ONNX bundle：`bundles/onnx/` 作为格式参考范本（同等级别复杂度的 monorepo）

## Assumptions

- 源码目录 `external/libs/ai/jupyter-book/` 已通过 git submodule 初始化，代码可读取
- Jupyter Book/MySTmd 使用 MIT 许可证，文档生成属于合理使用
- 用户已有 JavaScript/TypeScript 和 Markdown 基础，了解基本的 Node.js 工具链概念
- 不需要安装 Node.js 或运行代码（静态源码分析为主），V 阶段通过 Grep 验证而非运行时测试
- mystmd/packages 下 38 个包功能聚合为 4 个知识束是合理的抽象粒度，避免碎片化同时保持知识结构清晰
- 每个 Tier 1 知识束预计产出 18-27 个内容文档，Tier 2 预计 10-16 个，Tier 3 预计 7-9 个，总计约 100-140 个内容文档
- 现有 `bundles/myst/` 分组（Python Sphinx 生态）与新 `bundles/jupyter-book/` 分组（TypeScript 新生态）是代际关系，两者可交叉引用但不合并

## Acceptance Criteria

### AC-1: Jupyter Book 生态分类目录创建
- **type**: rule
- **Pass condition**: `bundles/jupyter-book/index.md` 存在，包含 `okf_version: "0.2"` frontmatter，列出所有 8 个子项目知识束，包含生态管线图
- **Evidence source**: 文件系统检查 + 文件内容检查

### AC-2: 8 个子项目知识束结构完整
- **type**: rule
- **Pass condition**: 每个 `bundles/jupyter-book/<project>/` 目录包含 index.md、log.md、concepts/、examples/、references/ 五个必要部分，子目录下均有 index.md
- **Evidence source**: 文件系统检查（8 bundles × 5 结构要素 = 40 项）

### AC-3: 内容文档数量达标
- **type**: rule
- **Pass condition**:
  - mystmd/: ≥18 内容文档（≥10 concepts + ≥3 examples + ≥5 references）
  - myst-cli/: ≥14 内容文档（≥8 concepts + ≥3 examples + ≥3 references）
  - myst-syntax/: ≥12 内容文档（≥7 concepts + ≥2 examples + ≥3 references）
  - myst-exporters/: ≥12 内容文档（≥7 concepts + ≥2 examples + ≥3 references）
  - jupyter-book/: ≥8 内容文档（≥4 concepts + ≥2 examples + ≥2 references）
  - myst-execute/: ≥11 内容文档（≥6 concepts + ≥2 examples + ≥3 references）
  - jupyterlab-myst/: ≥7 内容文档（≥4 concepts + ≥1 examples + ≥2 references）
  - myst-theme/: ≥9 内容文档（≥5 concepts + ≥2 examples + ≥2 references）
- **Evidence source**: 文件系统统计

### AC-4: Frontmatter 规范合规
- **type**: rule
- **Pass condition**: 每个非 index.md/log.md 的 .md 文件包含可解析的 YAML frontmatter，含 type/title/description/tags/generated/verified/status/stale_after/sources 字段；type 值为 concept/example/reference 之一
- **Evidence source**: 逐文件 frontmatter 检查

### AC-5: 无虚构 API（Grep 验证）
- **type**: rule
- **Pass condition**: 每个知识束随机抽取 ≥10 个引用的类名/方法名/函数名/接口名在源码中 Grep 验证，命中率 100%；对于发现虚构的情况必须修正
- **Evidence source**: Grep 命令验证记录

### AC-6: 交叉引用无断链
- **type**: rule
- **Pass condition**: 所有内部交叉引用（/concepts/xxx.md, /examples/xxx.md, /references/xxx.md）目标文件存在
- **Evidence source**: 链接检查

### AC-7: 七概念质量门通过
- **type**: rule
- **Pass condition**:
  - G1（R 阶段）：每个子项目 facts.md 存在，事实编号 F-xxx，无"用于"/"目的是"等推断词
  - G2（I 阶段）：每个子项目 insights.md 存在，洞察包含陈述/证据/反常识/行动四元组
  - G3（E 阶段）：references/ 先于 concepts/ 生成，分批≤7 文件，index 最后写
  - G4（V 阶段）：Grep 验证、链接检查、frontmatter 检查全部通过
- **Evidence source**: 各阶段质量门检查记录

### AC-8: bundles 总索引更新
- **type**: rule
- **Pass condition**: `bundles/index.md` 中新增"📖 Jupyter Book v2 / MySTmd 生态"分组，total_bundles 和 groups 计数正确更新
- **Evidence source**: 文件内容检查

### AC-9: 文档质量（中文表达与结构清晰度）
- **type**: rubric
- **Dimension**: 文档可读性、结构清晰度、知识地图合理性、TypeScript 类型准确性
- **Scale**: 0-2
  - 0: 文档结构混乱、中文表达不通顺、概念排列无逻辑、TS类型错误
  - 1: 文档基本可读，概念排列有基本逻辑，但有少量表述不清或类型不准确
  - 2: 文档结构清晰、中文表达流畅、概念按学习路径递进、TS类型准确、有架构图/表格辅助理解
- **Pass threshold**: ≥1.5（平均每个 bundle 的抽评文档）
- **Evidence source**: 独立审查抽评

## Open Questions

1. myst-execute 与 thebe 合并为一个知识束是否合理？（两者都涉及代码执行，但 myst-execute 是构建时执行，thebe 是运行时交互，概念上有联系也有区别）
2. mystmd 核心引擎包聚合粒度是否合适？（myst-parser 和 myst-transforms 是否应该独立为更细粒度的 bundle？当前方案聚合为一个 mystmd bundle 以避免过度碎片化）
3. 是否需要在 jupyter-book/ bundle 中深入 TS CLI 源码，还是因为它主要委托 myst-cli 而简化处理？（当前方案：jupyter-book 聚焦 Python 包装层和 CLI 差异，核心 CLI 能力在 myst-cli bundle 中覆盖）
4. myst-theme 的 CSS 样式系统需要覆盖到什么深度？（当前方案：聚焦主题架构和定制机制，不逐一解析每个 CSS 组件类）
