---
id: "english-grammar-okf-wiki"
title: "旋元佑英语语法 OKF Wiki 教程"
---

# 旋元佑《语法俱乐部》OKF Wiki 教程 - Product Requirement Document

## Overview
- **Summary**: 将 flexloop vendor 中 `vendor/flexloop/docs/general/linguistics/english-grammar/` 目录下的旋元佑《语法俱乐部》（英语语法进阶教程）Markdown 文档，按照 OKF v0.2 规范转换为结构化 Wiki Bundle，输出到 `bundles/chaos/english-grammar/` 目录。采用 source-code-to-okf-wiki 技能的 R→I→E→V→C 五阶段知识沉淀工作流，遵循信源先行、分批生成、Grep 验证（内容溯源）、Index 最后写等核心防护机制。
- **Purpose**: 旋元佑《语法俱乐部》是华人英语学习领域的经典语法教程，以"广读"理念和理解型语法教学著称。原始文档为 MyST/Sphinx 格式（含 toctree、note 等指令），需要转换为标准 OKF Bundle 格式以便在 OKF 生态中检索、导航和复用。
- **Target Users**: 英语学习者、语法研究者、OKF 知识生态用户

## Goals
- 将 25 章语法教程 + 序/引言/指南/术语表共约 30 个 Markdown 文件转换为 OKF v0.2 规范格式
- 创建符合 OKF 规范的目录结构（concepts/、examples/、references/、index.md、log.md）
- 添加正确的 YAML frontmatter（type、title、description、tags、sources、generated、verified 等字段）
- 移除 MyST/Sphinx 特有语法（`{note}`、`{toctree}`、````{code-block}``` 等），转换为标准 Markdown
- 建立文档间交叉链接，使用 `/` 开头的 bundle-relative 绝对路径
- 生成学习路径和概念索引，便于系统化学习
- 信源溯源：每个转换后的文档通过 sources 字段指向原始文件信源登记

## Non-Goals (Out of Scope)
- 不修改原始语法教程的内容（保持旋元佑原文完整）
- 不添加练习题目、测试题或额外教学内容
- 不翻译为英文（保持中文原文）
- 不生成 PDF/HTML 等导出格式
- 不对语法观点进行学术评审或纠错
- 不修改 vendor/flexloop/ 内的任何原始文件

## Background & Context
- **源文档位置**: `d:\spaces\SpecWeave\vendor\flexloop\docs\general\linguistics\english-grammar\`
- **源文档数量**: 约 30 个 Markdown 文件
  - 入口文件: index.md（旋元佑进阶语法笔记）、intro.md（引：广读学英语）、preface.md（序：我学英语的经验）、guide.md
  - 25 章正文章节: chapter/chapter-01-simple-sentences.md 至 chapter/chapter-25-adverb-clauses-reduced.md
  - 附录: appendix/terminology.md（术语表）
- **源文档格式**: MyST Markdown（Sphinx 文档格式），含 `{note}`、`{toctree}` 等指令
- **输出目标**: `d:\spaces\SpecWeave\bundles\chaos\english-grammar\`（遵循 bundles/chaos/ 下现有 bundle 的目录结构，如 apache-tvm）
- **参考 Bundle**: `bundles/chaos/apache-tvm/` 作为 OKF v0.2 格式参考实例

## Functional Requirements
- **FR-1**: 创建 OKF v0.2 Bundle 标准目录结构
  - `english-grammar/index.md`（根索引，含 okf_version frontmatter）
  - `english-grammar/log.md`（变更日志）
  - `english-grammar/concepts/`（25 章 + 序/引言/指南作为概念文档）
  - `english-grammar/concepts/index.md`（概念导航，无 frontmatter）
  - `english-grammar/examples/`（示例文档，如广读材料推荐可作为示例）
  - `english-grammar/examples/index.md`
  - `english-grammar/references/`（信源登记，指向原始 flexloop 文件）
  - `english-grammar/references/index.md`

- **FR-2**: 为每个文档添加合规的 YAML frontmatter
  - type: Concept/Example/Reference/Index
  - title: 文档标题
  - description: 30-80 字一句话描述
  - tags: 语法相关标签（如 "grammar", "english", "syntax", "clauses" 等）
  - generated: { by: "source-code-to-okf-wiki/E", at: ISO8601 时间 }
  - verified: { by: "source-code-to-okf-wiki/V", at: ISO8601 时间 }
  - status: "stable"
  - stale_after: 2027-08-25
  - sources: 指向 references/ 下信源文件的引用列表

- **FR-3**: MyST/Sphinx 语法转换为标准 Markdown
  - `{note}`  admonition 转换为标准 Markdown 引用块（`> `）或粗体提示
  - `{toctree}` 指令移除（由 OKF index.md 导航替代）
  - 保留原有标题层级、表格、列表、代码块、下划线强调等
  - 代码块标注语言（如有）

- **FR-4**: 建立文档间交叉链接网络
  - 所有交叉引用使用 `/` 开头 bundle-relative 路径（如 `/concepts/01-simple-sentences.md`）
  - 每个概念文档结尾添加「相关概念」章节
  - 根 index.md 按学习路径分组（基础篇/进阶篇/高级篇）

- **FR-5**: 信源登记与溯源
  - references/ 下为每个原始文件创建信源登记文件
  - 信源文件记录原始路径、作者（旋元佑）、来源（liby/codeyu 整理版本）等元数据
  - 所有转换后文档的 sources 字段正确指向对应信源文件

- **FR-6**: 事实清单与洞察文档
  - references/facts.md 记录可验证的文档结构事实（文件数量、章节数、主题分类等）
  - references/insights.md 记录架构洞察（知识地图、学习路径设计、核心语法体系）

## Non-Functional Requirements
- **NFR-1**: 文档完整性 - 原始文档内容 100% 保留，无遗漏章节或段落
- **NFR-2**: 格式一致性 - 所有文档遵循统一的 OKF frontmatter 规范和 Markdown 风格
- **NFR-3**: 链接有效性 - 所有内部交叉链接可正确解析，无断链
- **NFR-4**: 中文撰写 - 文档主体保持中文，英文术语首次出现保留原文括号注释
- **NFR-5**: 分批生成质量 - 每批生成不超过 7 个文档，防止上下文过载导致质量下降

## Constraints
- **Technical**: 只能使用现有工具链（general_purpose_task 子代理、文件读写工具），不修改 vendor/ 目录
- **Business**: 遵循 OKF v0.2 规范，与 bundles/chaos/ 下现有 bundle 格式保持一致
- **Dependencies**: source-code-to-okf-wiki 技能方法论、现有 apache-tvm bundle 作为格式参考

## Assumptions
- 用户希望在 `bundles/chaos/` 下创建子目录（与现有 bundle 组织方式一致）
- 原始文档的 MyST 语法可以无损转换为标准 Markdown
- 旋元佑《语法俱乐部》内容为公开可整理的语法学习材料
- 不需要创建 C 阶段的模式沉淀文档（除非执行过程中发现可复用模式）

## Acceptance Criteria

### AC-1: Bundle 目录结构完整
- **Given**: Bundle 已生成
- **When**: 检查 `bundles/chaos/english-grammar/` 目录结构
- **Then**: 包含 index.md、log.md、concepts/、examples/、references/ 五个标准组成部分，各子目录有对应的 index.md
- **Verification**: `programmatic`
- **Notes**: 参考 apache-tvm bundle 的目录结构

### AC-2: Frontmatter 合规
- **Given**: 所有 Markdown 文件
- **When**: 检查每个 .md 文件的 YAML frontmatter
- **Then**: 根 index.md 包含 okf_version: "0.2"，所有 Concept/Example/Reference 文档包含完整必填字段（type/title/description/tags/generated/verified/status/stale_after/sources）
- **Verification**: `programmatic`

### AC-3: 内容完整性
- **Given**: 原始 30 个文档
- **When**: 对比原始文档和转换后文档
- **Then**: 所有章节标题、正文内容、例句、表格、列表完整保留，无内容遗漏或篡改
- **Verification**: `human-judgment` + 抽样 `programmatic` 检查

### AC-4: MyST 语法清理
- **Given**: 转换后文档
- **When**: 搜索 `{toctree}`、`{note}`、` ```{` 等 MyST 指令
- **Then**: 无残留 MyST/Sphinx 特有语法，所有 admonition 转换为标准 Markdown 格式
- **Verification**: `programmatic`（Grep 搜索）

### AC-5: 交叉链接正确
- **Given**: 所有内部链接
- **When**: 检查链接路径格式和目标文件存在性
- **Then**: 所有交叉链接使用 `/` 开头的 bundle-relative 路径，目标文件存在，无 `../` 相对路径
- **Verification**: `programmatic`（链接检查）

### AC-6: 信源溯源完整
- **Given**: references/ 目录
- **When**: 检查信源登记和 sources 字段
- **Then**: 每个概念文档的 sources 字段指向有效的 references/ 文件，references/ 包含原始文件元数据
- **Verification**: `programmatic`

### AC-7: Index 导航合理
- **Given**: 根 index.md 和子目录 index.md
- **When**: 审阅导航结构
- **Then**: 根 index.md 按学习路径分组（基础→进阶→高级），子目录 index.md 列出该目录所有文档，无遗漏无多余
- **Verification**: `human-judgment`

### AC-8: Log 变更日志
- **Given**: log.md
- **When**: 检查 log.md 内容
- **Then**: 记录 Bundle 创建时间、来源、转换方法、版本信息
- **Verification**: `human-judgment`

## Open Questions
- [ ] guide.md 的具体内容是什么？（待 R 阶段阅读确认其定位，可能是使用指南或术语导读）
- [ ] 是否需要将25章按难度分组（基础/进阶/高级），还是严格按原书章节顺序排列？
- [ ] appendix/terminology.md 术语表应放在 references/ 还是 concepts/ 下？
