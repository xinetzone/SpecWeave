# KaTeX 官网学习与 OKF Wiki 更新 - Product Requirement Document

## Overview
- **Summary**：系统学习 https://katex.org/ 的 17 个公开页面，采用“融合增强”方式更新 [katex bundle](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/bundles/katex)，保留现有源码级架构分析，同时补齐官网文档中的安装、浏览器/Node 运行时、CLI、配置、字体、安全、错误处理、支持函数表、常见问题、迁移指南和生态信息。
- **Purpose**：现有 bundle 已覆盖 KaTeX v0.18.4 的核心源码架构，但对官网用户文档覆盖不完整，且部分配置默认值与官网存在偏差。本次更新将官网作为权威用户文档信源，形成“会用 + 懂原理 + 能扩展 + 可排障”的完整中文 OKF Wiki。
- **Target Users**：KaTeX 使用者、前端/Node.js 开发者、数学排版扩展开发者、OKF 文档维护者、希望通过源码与官方文档双向学习 KaTeX 的工程师。

## Goals
- 完整覆盖 KaTeX 官网 17 个公开页面，并将其内容映射到 OKF bundle。
- 保留并修正现有 15 篇源码概念文档，避免丢失 Lexer、MacroExpander、Parser、渲染管线等深度架构内容。
- 新增官网导向的概念文档和示例，补齐 Browser/Node、CLI、Font、Security、Supported Functions、Support Table、Common Issues、Migration、Ecosystem 等主题。
- 建立官网页面信源登记，使所有新增或修正事实可追溯到具体官网 URL。
- 按 OKF v0.2 规范补齐 frontmatter、目录索引、更新日志和交叉链接。
- 执行独立验证，确保无断链、无虚构 API、配置项默认值与官网一致。

## Non-Goals (Out of Scope)
- 不逐字翻译 KaTeX 官网；所有内容需重组为中文 OKF 教程，并保留源码洞察。
- 不修改 KaTeX 上游源码或构建产物。
- 不扩展到 v0.18.4 以外的历史版本深度教程；历史版本仅在迁移指南中按官网信息概述。
- 不对第三方生态库（React、Vue、Angular、Rust、Ruby 等）做逐个深度使用教程，只做生态索引和选型说明。
- 不执行 git commit；提交由用户另行决定。
- 不创建与本次更新无关的通用模式文档或主权区文档。

## Background & Context
- 用户明确要求使用 `seven-concepts-cmd` 与 `source-code-to-okf-wiki`。本次属于知识沉淀场景，采用 R→I→E→V→C 闭环：事实采集、架构/文档洞察、批量生成、独立验证、更新闭环。
- 当前 bundle 位于 [projects/awesome-okf-xs/bundles/katex](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/bundles/katex)，已有根索引、15 篇 concepts、5 篇 examples、1 篇 reference、2 个 spec 文件。
- 当前 bundle 缺少 concepts/examples/references 子目录索引和 log.md；部分文档仍需补齐官网信源。
- 官网盘点发现 17 个公开页面：首页、Users、Versions、Node、Browser、API、CLI、Auto-render、Extensions & Libraries、Options、Security、Handling Errors、Font、Supported Functions、Support Table、Common Issues、Migration。
- 官网信息与现有事实清单存在需要复核的偏差，例如 Options 页面显示 `strict` 默认值为 `"warn"`、`maxExpand` 默认值为 `Infinity`，而现有文档写为 `false` 与 `1000`。R 阶段必须以官网和必要源码复核后修正。

## Functional Requirements
- **FR-1：官网事实采集**：采集 17 个官网页面的可验证事实，写入 `spec/facts.md`，每条事实标注官网页面或源码来源。
- **FR-2：洞察与知识地图更新**：更新 `spec/insights.md`，说明官网文档与源码架构如何对应，并明确新增/更新文档清单。
- **FR-3：信源登记**：新增或更新 references 文档，登记官网 17 个页面与 GitHub 源码信源，供所有文档 `sources` 字段引用。
- **FR-4：入门与运行时文档**：更新简介、快速开始，新增/补齐浏览器、Node.js、CDN、字体托管、模块加载等安装运行时主题。
- **FR-5：API、CLI 与配置文档**：更新核心 API、Options、Auto-render，新增 CLI 文档，修正配置默认值、类型、行为和安全说明。
- **FR-6：扩展、字体、安全与错误文档**：更新函数注册、宏系统、contrib 扩展；补齐字体、单位、安全策略、错误处理和 HTML 消毒要求。
- **FR-7：支持函数与排障文档**：新增 Supported Functions、Support Table、Common Issues、Migration 文档，覆盖支持范围、差异、兼容问题和升级注意事项。
- **FR-8：生态文档**：新增生态/版本页面，覆盖 Users、Versions、官方扩展和第三方库索引。
- **FR-9：示例更新**：更新现有 5 个示例，并新增 CLI、Node SSR、安全信任等可运行/可复制示例。
- **FR-10：索引与日志**：生成根索引、子目录索引和 log.md，确保导航完整。
- **FR-11：独立验证**：检查 frontmatter、链接、信源、事实一致性、官网覆盖度和格式规范，并修复问题。

## Non-Functional Requirements
- **NFR-1：语言与命名**：正文中文，文件名 kebab-case 英文。
- **NFR-2：OKF 规范**：所有非保留 Markdown 文档必须包含 YAML frontmatter 和非空 `type`；根 `index.md` 可声明 `okf_version: "0.2"`；子目录 `index.md` 不写 frontmatter。
- **NFR-3：溯源**：新增或重大更新文档必须包含 `sources`，至少指向官网信源或源码信源。
- **NFR-4：路径风格**：bundle 内交叉引用使用 `/` 开头的 bundle-relative 路径；禁止 `file:///` 绝对路径进入产物文档。
- **NFR-5：事实纪律**：R 阶段事实不得出现“用于/目的是/设计为”等推断性表述；解释性内容放入 I 阶段或概念正文。
- **NFR-6：批量生成纪律**：每批生成/更新文档不超过 7 个，references 先于 concepts/examples，index 最后生成。
- **NFR-7：可验证性**：API、Options、CLI 参数、默认值必须可追溯到官网页面；涉及源码内部 API 的内容必须可追溯到现有源码事实或源码信源。
- **NFR-8：最小改动**：保留现有高质量源码分析内容，仅在事实错误、缺口或导航需要时修改。

## Constraints
- **Technical**：Markdown + YAML frontmatter；静态 OKF bundle；不引入构建工具或新依赖。
- **Business**：目标版本锁定 KaTeX v0.18.4 官网当前稳定版；内容为公开资料，按公开内容工作流处理。
- **Dependencies**：官网 https://katex.org/、KaTeX GitHub 仓库、现有 bundle 文件、awesome-okf-xs OKF v0.2 规范。
- **Process**：遵循 [AGENTS.md](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/AGENTS.md) 与 [frontmatter.md](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/.agents/rules/frontmatter.md)；实现任务必须委派给子智能体，主智能体不直接写入实现内容。

## Assumptions
- 用户选择“融合增强”：保留源码级文档，同时新增官网导向文档。
- 官网当前显示的 v0.18.4 是本次文档版本基准；若官网页面与源码事实冲突，优先在事实清单中标注冲突并复核官网/源码后再修正文档。
- 示例以可复制代码片段为主，不需要搭建可运行测试工程。
- 不需要执行 git commit。

## Acceptance Criteria

### AC-1: 官网 17 页全部覆盖
- **Given**：KaTeX 官网公开页面清单已盘点
- **When**：检查最终 bundle 的 concepts、examples、references 和 index
- **Then**：17 个官网页面均被至少一篇文档或信源条目覆盖，并有明确映射
- **Verification**: `programmatic`

### AC-2: 事实清单通过 G1
- **Given**：`spec/facts.md` 更新完成
- **When**：审查事实条目
- **Then**：每条事实均可追溯到官网 URL 或源码路径，且不包含因果推断、主观评价或无来源断言
- **Verification**: `human-judgment`

### AC-3: 洞察与知识地图通过 G2
- **Given**：`spec/insights.md` 更新完成
- **When**：审查洞察章节
- **Then**：包含陈述、证据、反常识/差异、行动四元组，并给出新增/更新文档与官网页映射
- **Verification**: `human-judgment`

### AC-4: References 信源先行且完整
- **Given**：进入文档生成阶段
- **When**：检查 references 目录
- **Then**：官网 17 页和源码信源已登记，后续文档 `sources.resource` 均能解析到已有 reference 或外部 URL
- **Verification**: `programmatic`

### AC-5: 入门、运行时、API、CLI、配置内容完整
- **Given**：用户按路径1学习 KaTeX 使用
- **When**：阅读 00、01、10、13、15、16 及相关 examples
- **Then**：能完成浏览器/Node 安装、核心 API 调用、Auto-render 配置、CLI 使用和 Options 设置
- **Verification**: `human-judgment`

### AC-6: 深度架构内容保留且与官网衔接
- **Given**：用户按路径2阅读源码架构
- **When**：阅读 02-09、11、12、14
- **Then**：仍可理解 Lexer→MacroExpander→Parser→BuildTree→DOM 输出，并能链接到官网 Options、Font、Extensions 等用户文档
- **Verification**: `human-judgment`

### AC-7: 支持范围、排障和迁移内容补齐
- **Given**：用户查询支持函数、常见问题或升级变更
- **When**：阅读 19-22
- **Then**：能找到函数分类、字母索引、常见兼容问题、v0.13-v0.18 迁移要点
- **Verification**: `human-judgment`

### AC-8: 示例与官网 API 一致
- **Given**：examples 中代码片段
- **When**：对照官网 API、Options、Auto-render、Security、CLI 页面
- **Then**：代码调用、选项名称、默认值和安全注意事项一致，无虚构参数
- **Verification**: `programmatic`

### AC-9: OKF frontmatter 合规
- **Given**：所有非保留 Markdown 文档
- **When**：解析 YAML frontmatter
- **Then**：每个文档均有非空 `type`，推荐字段和溯源字段按文档性质补齐，子目录 index 无 frontmatter
- **Verification**: `programmatic`

### AC-10: 内部链接无断裂
- **Given**：bundle 内所有 `/` 开头交叉引用
- **When**：解析链接目标
- **Then**：目标文件均存在；根索引和子目录索引列出的文件均存在且无遗漏
- **Verification**: `programmatic`

### AC-11: 已知事实偏差被修正
- **Given**：官网 Options 页面与现有 facts/docs 的默认值差异
- **When**：检查 facts、settings/options 文档和示例
- **Then**：`strict`、`maxExpand` 等差异均已复核并给出一致表述
- **Verification**: `programmatic`

### AC-12: 独立验证完成并闭环
- **Given**：所有内容更新完成
- **When**：执行 V 阶段检查
- **Then**：存在验证结果摘要，发现的问题均已修复或在任务清单中标记完成
- **Verification**: `human-judgment`

## Open Questions
- 无；用户已确认采用“融合增强”范围。
