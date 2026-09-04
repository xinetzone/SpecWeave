---
title: "OKF Spec Bundle 内容补充 - 产品需求文档"
status: "draft"
---

# OKF Spec Bundle 内容补充 - 产品需求文档

## Overview
- **Summary**: 系统学习 https://okf.md/ 官方网站全部内容（主页、/spec v0.1注释指南、/quickstart快速入门、/validator验证器、/skill Agent技能），并补充 GitHub 上 OKF v0.2 完整英文规范原文，将缺失的概念、示例、实践建议、生态工具介绍补充到现有 `bundles/okf-spec` 知识包中。
- **Purpose**: 现有 okf-spec bundle 已覆盖 OKF v0.2 规范的15个核心概念和3个示例，但信源文件缺少英文原文，且网站上的注释指南、实践建议、完整教程、生态工具等内容未收录，导致知识包作为"OKF规范中文权威参考"不够完整。
- **Target Users**: 使用 OKF 格式组织知识的 AI 智能体开发者、技术文档工程师、数据团队成员。

## Goals
- 补充 references/okf-spec.md 为完整英文 v0.2 规范原文（替换现有19行摘要）
- 收录 okf.md 网站 v0.1 Annotated Guide 中的实践注释、设计原则、示例代码作为补充参考
- 添加 Quickstart SaaS Metrics 完整教程作为示例文档
- 添加 OKF 生态工具概念（Validator、Agent Skill、Knowledge Catalog/kcmd）
- 更新根 index.md 和各子目录 index.md 以反映新增内容
- 所有新增/修改文档遵循 OKF v0.2 frontmatter 规范和 awesome-okf-xs 文档规范

## Non-Goals
- 不重构现有15个概念文档的整体结构和已准确转译的 v0.2 内容
- 不将现有 v0.2 概念文档回退或降级为 v0.1
- 不创建新的独立 bundle（所有内容归入现有 okf-spec bundle）
- 不翻译/收录 fabricioctelles/skills 仓库的全部源代码
- 不修改 projects/awesome-okf-xs 子项目的 .agents/ 规范文件

## Background & Context
- 现有 bundle 位于 `d:\spaces\SpecWeave\projects\awesome-okf-xs\bundles\okf-spec\`
- 现有结构：根 index.md + log.md + concepts/(15个概念) + examples/(3个示例) + references/(2个信源)
- 权威信源有两个：(a) GitHub GoogleCloudPlatform/knowledge-catalog 仓库中的 SPEC.md（v0.2正式规范）；(b) okf.md 官方网站（含v0.1注释指南、Quickstart、Validator、Skill页面）
- v0.2 规范在 v0.1 基础上新增了溯源(sources)、信任(generated/verified)、生命周期(status/stale_after)、可认证计算(Attested Computation)、actor约定等字段族
- 网站 /spec 页面是 v0.1 Draft 的"Annotated Guide"（开发者带注释走查版），包含大量v0.2正式规范中没有的实践建议、设计理由、代码示例和作者观点

## Functional Requirements
- **FR-1**: references/okf-spec.md 必须包含 OKF v0.2 完整英文规范原文（来自 GitHub raw SPEC.md），并保留现有frontmatter元数据
- **FR-2**: 添加 v0.1 Annotated Guide 作为参考信源，收录其中有价值的实践注释内容（设计原则、type治理建议、自动化index脚本、断链即特性解释、log.md vs git log、结构对RAG的重要性、Metric示例、Obsidian对比等）
- **FR-3**: 添加 concepts/design-principles.md 概念文档，阐述OKF三大设计原则（最小意见化/生产者消费者独立/格式而非平台）
- **FR-4**: 添加 concepts/practical-guidance.md 概念文档，收录v0.1注释版中的实践建议（type治理、扩展字段用法、自动化index脚本、断链设计意图、body结构建议、Citations vs footnotes演进说明）
- **FR-5**: 添加 examples/saas-metrics-quickstart.md 示例文档，收录Quickstart教程的SaaS Metrics完整bundle（MRR/Churn/NPS三个概念+index+log）
- **FR-6**: 添加 concepts/tooling-validator.md 概念文档，介绍OKF Validator在线验证工具
- **FR-7**: 添加 concepts/tooling-agent-skill.md 概念文档，介绍OKF Agent Skill（安装方式、能力、validate.sh脚本、使用示例）
- **FR-8**: 添加 concepts/tooling-knowledge-catalog.md 概念文档，介绍Google Cloud Knowledge Catalog集成（kcmd CLI/MCP服务器）
- **FR-9**: 更新根 index.md、concepts/index.md、examples/index.md、references/index.md 以完整列出所有新增文档
- **FR-10**: 更新 log.md 记录本次补充变更

## Non-Functional Requirements
- **NFR-1**: 所有新增文档必须使用中文撰写（英文技术术语首次出现时括号注释原文）
- **NFR-2**: 所有 .md 文件必须包含合法的 YAML frontmatter，`type` 字段为唯一必填
- **NFR-3**: 文件名使用 kebab-case 纯英文命名
- **NFR-4**: 交叉引用使用 `/` 开头的 bundle-relative 路径（如 `/concepts/xxx.md`）
- **NFR-5**: 派生产物通过 frontmatter `sources` 字段溯源到 references/ 中的信源登记
- **NFR-6**: 保留现有文档的 `verified: { by: process:seven-concepts-v }` 信任层级；新增文档设置 `status: draft`，经审查后升级

## Constraints
- **Technical**: 必须遵循 OKF v0.2 规范（frontmatter规则、保留文件名、交叉引用路径）；必须遵循 awesome-okf-xs AGENTS.md 文档规范
- **Business**: 不修改子项目 .agents/ 规范；不破坏现有 stable 文档
- **Dependencies**: 信源可从 https://okf.md/ 和 https://raw.githubusercontent.com/GoogleCloudPlatform/knowledge-catalog/main/okf/SPEC.md 获取

## Assumptions
- 用户网络环境可访问 okf.md 和 GitHub raw 内容
- v0.1 Annotated Guide 中的实践建议虽然针对 v0.1，但其设计思想和实践指导对 v0.2 同样适用，可作为补充概念收录
- 现有3个示例文档（Customer Orders、Freshness Alert、Income Statement）不需要修改
- 现有15个概念文档不需要大幅重写，仅在必要时添加指向新增概念的交叉链接

## Acceptance Criteria

### AC-1: v0.2 英文规范原文完整收录
- **Type**: `rule`
- **Given**: references/okf-spec.md 已更新
- **When**: 检查文件内容
- **Then**: 文件包含 OKF v0.2 SPEC.md 完整英文原文（§1-§13全部章节），且保留合规的 YAML frontmatter
- **Pass Condition**: 文件正文包含从 "# Open Knowledge Format (OKF)" 到 "§13 Changes from v0.1" 的完整内容，行数与GitHub原始SPEC.md一致（约400+行）
- **Evidence**: 读取 references/okf-spec.md 验证章节完整性

### AC-2: v0.1 注释指南内容已系统化收录
- **Type**: `rule`
- **Given**: 新增 references/okf-annotated-v01.md 和相关概念文档
- **When**: 检查新增文件
- **Then**: v0.1 Annotated Guide 中的设计原则、实践建议、示例代码等增量内容（非v0.2已有内容）已通过概念文档或参考信源收录
- **Pass Condition**: (a) references/ 下有v0.1注释指南的信源登记；(b) concepts/design-principles.md 存在且覆盖三大设计原则；(c) concepts/practical-guidance.md 存在且覆盖至少5条实践建议
- **Evidence**: 检查新增文件存在性和内容覆盖

### AC-3: Quickstart教程作为示例收录
- **Type**: `rule`
- **Given**: 新增 examples/saas-metrics-quickstart.md
- **When**: 检查文件
- **Then**: 文件包含完整的SaaS Metrics bundle教程内容（目录结构、MRR/Churn/NPS三个概念、index.md、log.md、验证步骤）
- **Pass Condition**: 文件包含MRR/Churn/NPS三个Metric的frontmatter示例、公式、基准数据，以及index.md和log.md的代码示例
- **Evidence**: 读取 examples/saas-metrics-quickstart.md 验证内容完整性

### AC-4: 生态工具概念文档完整
- **Type**: `rule`
- **Given**: 新增3个工具概念文档
- **When**: 检查 concepts/tooling-*.md
- **Then**: Validator、Agent Skill、Knowledge Catalog 三个概念文档均存在且包含核心信息
- **Pass Condition**: (a) tooling-validator.md 介绍验证功能和三个合规规则；(b) tooling-agent-skill.md 介绍安装方式、6项能力、validate.sh用法；(c) tooling-knowledge-catalog.md 介绍kcmd和MCP集成
- **Evidence**: 读取三个文件验证核心内容存在

### AC-5: 索引文件完整更新
- **Type**: `rule`
- **Given**: 所有新增文档已创建
- **When**: 检查根index.md和各子目录index.md
- **Then**: 所有新增文档在对应的index.md中列出，无遗漏
- **Pass Condition**: 根index.md列出所有新增concepts/examples/references；concepts/index.md列出所有新增概念；examples/index.md列出saas-metrics-quickstart；references/index.md列出新增信源
- **Evidence**: 读取四个index.md交叉验证

### AC-6: 所有文档符合OKF v0.2和子项目规范
- **Type**: `rubric`
- **Dimension**: 文档规范合规性
- **Scale**: 1-5
- **Anchors**: 1 = 多个文档缺少frontmatter或type字段，路径引用错误；3 = 大部分文档合规但有少量frontmatter字段遗漏或路径不一致；5 = 所有文档frontmatter完整合法、中文正文、kebab-case文件名、`/`开头bundle-relative路径、sources溯源正确
- **Pass Threshold**: >= 4
- **Evidence**: 逐个检查新增/修改文档的frontmatter、文件名、路径引用、sources字段

### AC-7: 现有文档不被破坏
- **Type**: `rule`
- **Given**: 现有15个概念文档和3个示例文档
- **When**: 对比修改前后
- **Then**: 现有文档的核心v0.2内容保持完整准确，不出现内容回退或错误
- **Pass Condition**: 现有15+3个文档的frontmatter保持兼容，v0.2特有的字段族内容（sources/generated/verified/status/stale_after/attested computation等）不丢失
- **Evidence**: 抽查关键概念文档（motivation、provenance-sources、attested-computations、conformance）确认内容未被破坏

### AC-8: log.md记录变更
- **Type**: `rule`
- **Given**: log.md已更新
- **When**: 检查log.md
- **Then**: 包含本次内容补充的变更记录，使用YYYY-MM-DD日期分组
- **Pass Condition**: log.md顶部有2026-08-21日期分组，记录新增的所有文档
- **Evidence**: 读取log.md验证

## Open Questions
- [ ] v0.1 Annotated Guide 中的内容是作为独立concept文档收录，还是整合到现有概念文档中作为补充段落？（建议：新增独立概念文档，避免破坏现有stable文档结构）
- [ ] references/ 下是创建子目录存放v0.1信源，还是直接放在references/根目录？（建议：直接放在references/根目录，与okf-spec.md平级）
