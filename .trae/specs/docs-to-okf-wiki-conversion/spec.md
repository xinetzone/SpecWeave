# docs/ 全量转换为 OKF v0.2 Wiki 教程 - 产品需求文档

## Overview

- **Summary**：将 `d:\AI\docs\` 目录下全部 280 个 Markdown 文件（涵盖技术文档、知识库、复盘模式库、通用知识、设计洞见五大板块）原地转换为符合 OKF v0.2（Open Knowledge Format）开放知识格式规范的 Wiki Bundle 体系。每个独立主题/Wiki 成为一个自包含的 OKF Bundle，包含 `concepts/`、`examples/`、`references/` 标准子目录、合规 frontmatter、Bundle 绝对路径交叉链接和 `index.md`/`log.md` 导航文件。
- **Purpose**：当前 docs/ 文档存在三大问题——(1) frontmatter 格式不统一（部分有 YAML 元数据、部分完全缺失、字段命名不一致）；(2) 文件组织缺乏 OKF 标准的 concepts/examples/references 分层，导致知识类型边界模糊；(3) 交叉链接使用相对路径，文件移动后易断裂。转换为 OKF v0.2 格式后，文档具备可审计的信任链（sources/generated/verified）、统一的类型系统、稳定的 Bundle 绝对链接和渐进式披露导航，可被 OKF 兼容工具链（okf-kit、自研 okf CLI）直接消费。
- **Target Users**：SpecWeave 项目维护者、AI 智能体（通过 OKF 工具链消费知识）、外部开发者（通过 OKF Bundle 格式学习项目知识）。

## Goals

- G1：将 docs/ 下全部 280 个 Markdown 文件转换为合规的 OKF v0.2 Concept 文档，每个文件包含必填 `type` 字段和推荐字段
- G2：将 31 个独立主题（14 个现有 Wiki 教程 + 5 个分析报告 + 5 个其他知识主题 + 4 个项目文档 + 3 个复盘内容组）组织为独立 OKF Bundle
- G3：所有 Bundle 内部交叉链接统一使用 `/` 开头的 Bundle 绝对路径，消除相对路径脆弱性
- G4：为每个 Bundle 创建标准 `index.md`（根索引含 `okf_version`）和 `log.md`（变更日志）
- G5：为每个 Bundle 创建 `concepts/`、`examples/`、`references/` 子目录及对应子索引文件
- G6：转换过程遵循 source-code-to-okf-wiki Skill 的 R→I→E→V→C 五阶段工作流和 seven-concepts-cmd 的知识沉淀场景链路（R→I→E），确保事实可溯源、无虚构内容
- G7：保留原始内容完整性——正文内容不做语义改写，仅做结构化重组和 frontmatter 补全

## Non-Goals (Out of Scope)

- **不重写正文内容**：不改变 Markdown 正文的语义和叙述，仅调整 frontmatter、文件位置和链接路径
- **不处理非 Markdown 资源**：`.css`、`.png`、`.html`、`.py`、`.toml`、`.txt` 等静态资源和配置文件保持原位不动
- **不修改 Sphinx/Jupyter Book 构建配置**：`conf.py`、`_config.toml`、`requirements.txt`、`tasks.py` 等构建文件不在转换范围内
- **不合并或拆分知识主题**：现有目录边界作为 Bundle 边界的基础，不做跨主题内容合并
- **不生成 Attested Computation 类型文档**：当前内容不涉及认证计算场景
- **不创建新的知识内容**：仅重组和标注现有内容，不补充正文中不存在的知识
- **不处理 `.agents/docs/` 目录**：该目录是规范容器，不在 docs/ 公共文档树转换范围内

## Background & Context

### 当前文档体系现状

docs/ 是基于 Sphinx/Jupyter Book 的文档站点，包含：

| 板块 | 目录 | Markdown 文件数 | 内容类型 |
|------|------|:---:|------|
| 技术文档 | `tech/` | 10 | 项目介绍、快速开始、功能说明、贡献指南、变更日志等 |
| 知识库 | `knowledge/` | ~200+ | 14 个 Wiki 教程、5 个微信文章分析、AI 工程化、算法艺术、工程研究 |
| 复盘模式库 | `retrospective/` | ~40+ | 16 个方法论模式、里程碑复盘、对抗审查、竞争分析 |
| 通用知识 | `general/` | 2 | README 和索引 |
| 设计洞见 | `topics/` | 2 | README 和索引 |
| 重构笔记 | `refactor/` | 1 | 并发安全检查器重构文档 |
| 根目录 | `docs/*.md` | ~5 | index.md、README.md 等 |

### 现有 frontmatter 格式不一致问题

- **Wiki 教程文件**：有 YAML frontmatter，使用 `id`、`title`、`date`、`category`、`tags`、`source`（部分）等字段，但缺少 OKF 必填的 `type` 和推荐的 `description`、`generated`、`verified`、`status`、`stale_after`、`sources`（OKF 格式）
- **技术文档文件**：大部分完全没有 frontmatter
- **复盘/模式文件**：frontmatter 格式各异，部分有 `id`、`type`、`title` 等字段
- **索引文件**：`index.md` 多数无 frontmatter（符合 OKF 规范），但根 `index.md` 缺少 `okf_version`

### OKF v0.2 核心规范要点

- 每个非保留 `.md` 文件必须有可解析的 YAML frontmatter，包含非空 `type` 字段
- `index.md` 不含 frontmatter（唯一例外：Bundle 根 index.md 可含 `okf_version`）
- `log.md` 使用 ISO 8601 日期格式记录变更
- 交叉链接推荐使用 `/` 开头的 Bundle 绝对路径
- 信任字段家族：`sources`（来源）、`generated`（生成）、`verified`（验证）、`status`（状态）、`stale_after`（过期日期）
- `type` 值不集中注册，生产者选择描述性值（如 `Concept`、`Reference`、`Pattern`、`Tutorial`、`Report`）
- 消费者必须容忍断链、未知类型和缺失可选字段

### 方法论框架

本项目同时使用两个 Skill：
- **seven-concepts-cmd**：场景识别为"知识沉淀"（场景4），链路为 R→I→E（复盘事实→洞察共性→萃取模式）
- **source-code-to-okf-wiki**：适配为"文档→OKF Wiki"工作流，R→I→E→V→C 五阶段（事实采集→架构洞察→批量生成→独立验证→模式沉淀）

## Functional Requirements

### FR-1：Bundle 结构重组

- FR-1.1：每个独立主题目录转换为 OKF Bundle，根目录包含 `index.md`（含 `okf_version: "0.2"`）和 `log.md`
- FR-1.2：Bundle 内创建 `concepts/` 子目录，将编号主题文件（`NN-topic.md`）移入其中
- FR-1.3：Bundle 内创建 `references/` 子目录，用于登记外部来源材料
- FR-1.4：当原文档包含可独立运行的代码示例或使用教程时，创建 `examples/` 子目录
- FR-1.5：每个子目录（concepts/examples/references）包含无 frontmatter 的 `index.md` 导航文件
- FR-1.6：`00-overview.md` 或等效总览文件转换为 Bundle 根 `index.md`（合并 `okf_version` frontmatter）

### FR-2：Frontmatter 转换与补全

- FR-2.1：所有 Concept 文件必须包含 `type` 字段，根据内容性质映射为 `Tutorial`、`Concept`、`Reference`、`Pattern`、`Report`、`Example` 之一
- FR-2.2：补全 `title`（从现有标题或文件名推导）
- FR-2.3：补全 `description`（30-80 字一句话摘要，从正文首段或现有摘要提取）
- FR-2.4：补全 `tags`（保留现有标签，必要时补充 OKF 相关标签）
- FR-2.5：补全 `generated` 字段：`{ by: "process:docs-to-okf-conversion", at: "<ISO8601时间戳>" }`
- FR-2.6：补全 `verified` 字段：`{ by: "process:seven-concepts-v", at: "<ISO8601时间戳>" }`
- FR-2.7：补全 `status` 字段（默认 `stable`，草稿性质内容标为 `draft`）
- FR-2.8：补全 `stale_after` 字段（默认设置为转换日期后一年）
- FR-2.9：将现有 `source` 字段（列表格式）转换为 OKF `sources` 字段格式（含 id/resource/title）
- FR-2.10：保留现有 `id`、`date`、`category`、`maturity` 等自定义字段作为扩展字段（OKF 允许生产者自定义键值对）

### FR-3：交叉链接修正

- FR-3.1：Bundle 内部文档间的链接从相对路径（如 `02-contextlib.md`）转换为 Bundle 绝对路径（如 `/concepts/02-contextlib.md`）
- FR-3.2：指向 Bundle 外部的链接保持原样（绝对 URL 或跨 Bundle 相对路径）
- FR-3.3：图片和静态资源链接保持原样（`_static/` 等目录不移动）
- FR-3.4：Sphinx 特有的 `{ref}`、`{toctree}` 等指令保持原样，不做转换

### FR-4：Bundle 清单（31 个 Bundle）

#### 第一批：现有 Wiki 教程（14 Bundle）

| # | Bundle 名称 | 源目录 | 文件数 | type 映射 |
|---|------------|--------|:---:|---------|
| 1 | agency-agents-wiki | `knowledge/learning/03-agent-platforms-tools/agency-agents-wiki/` | 12 | Tutorial/Concept |
| 2 | cordis-wiki | `knowledge/learning/03-agent-platforms-tools/cordis-spatiotemporal-composability-wiki/` | 14 | Tutorial/Concept |
| 3 | deepseek-harness-wiki | `knowledge/learning/03-agent-platforms-tools/deepseek-harness-wiki/` | 17 | Tutorial/Concept |
| 4 | okf-kit-wiki | `knowledge/learning/03-agent-platforms-tools/okf-kit-wiki/` | 13 | Tutorial/Concept |
| 5 | open-code-review-wiki | `knowledge/learning/03-agent-platforms-tools/open-code-review-wiki/` | 11 | Tutorial/Concept |
| 6 | agent-runtime-protocol-wiki | `knowledge/learning/agent-runtime-protocol-wiki/` | 14 | Tutorial/Concept |
| 7 | ai-engineering-milestones-wiki | `knowledge/learning/ai-engineering-four-milestones-wiki/` | 8 | Tutorial/Concept |
| 8 | baidu-ocr-wiki | `knowledge/learning/baidu-unlimited-ocr-wiki/` | 9 | Tutorial/Concept |
| 9 | book-to-skill-wiki | `knowledge/learning/book-to-skill-wiki/` | 10 | Tutorial/Concept |
| 10 | github-cli-wiki | `knowledge/learning/github-cli-wiki/` | 9 | Tutorial/Concept |
| 11 | headroom-wiki | `knowledge/learning/headroom-context-compression-wiki/` | 11 | Tutorial/Concept |
| 12 | minit2i-wiki | `knowledge/learning/minit2i-minimalist-t2i-wiki/` | 8 | Tutorial/Concept |
| 13 | python314-cpython-wiki | `knowledge/learning/python314-cpython-wiki/` | 17 | Tutorial/Concept |
| 14 | python314-stdlib-wiki | `knowledge/learning/python314-stdlib-wiki/` | 18 | Tutorial/Concept |

#### 第二批：微信文章分析报告（5 Bundle）

| # | Bundle 名称 | 源目录 | 文件数 | type 映射 |
|---|------------|--------|:---:|---------|
| 15 | wechat-ai-switch-governance | `knowledge/learning/analyze-wechat-article-ai-switch-governance/` | 4 | Report/Analysis |
| 16 | wechat-causal-ai | `knowledge/learning/analyze-wechat-article-causal-ai/` | 3 | Report/Analysis |
| 17 | wechat-mainecoon | `knowledge/learning/analyze-wechat-article-mainecoon/` | 11 | Report/Analysis |
| 18 | wechat-quantdinger | `knowledge/learning/analyze-wechat-article-quantdinger/` | 3 | Report/Analysis |
| 19 | wechat-rqndd | `knowledge/learning/analyze-wechat-article-rqndd/` | 1 | Report/Analysis |

#### 第三批：其他知识主题（5 Bundle）

| # | Bundle 名称 | 源目录 | 文件数 | type 映射 |
|---|------------|--------|:---:|---------|
| 20 | codewhale | `knowledge/learning/codewhale/` | 9 | Tutorial/Concept |
| 21 | three-ai-tools | `knowledge/learning/three-ai-tools-learning-wiki/` | 2 | Report/Analysis |
| 22 | ai-engineering | `knowledge/ai-engineering/` | 3 | Reference/Concept |
| 23 | atomic-emergence | `knowledge/algorithmic-art/atomic-emergence/` | 1 | Concept |
| 24 | deep-learning-atomic-design | `knowledge/engineering/deep-learning-atomic-design/` | 3 | Reference/Concept |

#### 第四批：项目文档（4 Bundle）

| # | Bundle 名称 | 源目录 | 文件数 | type 映射 |
|---|------------|--------|:---:|---------|
| 25 | specweave-tech-docs | `tech/` | 10 | Tutorial/Reference |
| 26 | general-knowledge | `general/` | 2 | Reference |
| 27 | design-topics | `topics/` | 2 | Reference/Concept |
| 28 | refactor-notes | `refactor/` | 1 | Report |

#### 第五批：复盘内容（3 Bundle）

| # | Bundle 名称 | 源目录 | 文件数 | type 映射 |
|---|------------|--------|:---:|---------|
| 29 | methodology-patterns | `retrospective/patterns/methodology-patterns/` | 16 | Pattern |
| 30 | retrospective-reports | `retrospective/reports/`（递归） | ~28 | Report |
| 31 | retrospective-root | `retrospective/`（根索引） | 1 | Reference |

#### 第六批：根级导航文件

- 更新 `docs/index.md`（添加 `okf_version: "0.2"` frontmatter，作为全站根索引）
- 更新 `docs/README.md`（同步导航）
- 更新 `docs/knowledge/index.md`（知识库板块索引）
- 更新 `docs/knowledge/learning/03-agent-platforms-tools/README.md`（Wiki 组索引）
- 处理 `knowledge/learning/` 下的散文件（okf-topic-index.md、ai-engineering-four-milestones-wiki.md 等 5 个文件）

### FR-5：索引文件生成

- FR-5.1：Bundle 根 `index.md` 列出所有 Concept 文件链接和一句话描述
- FR-5.2：`concepts/index.md` 列出所有概念文档
- FR-5.3：`examples/index.md` 列出所有示例文档（如存在 examples/ 目录）
- FR-5.4：`references/index.md` 列出所有信源文件
- FR-5.5：索引条目使用各文档 frontmatter 中的 `description` 字段

### FR-6：变更日志生成

- FR-6.1：每个 Bundle 创建 `log.md`，记录初始转换事件
- FR-6.2：日期使用 ISO 8601 格式（`YYYY-MM-DD`）
- FR-6.3：初始条目为 `**Initialization**: 从 docs/ 原有结构转换为 OKF v0.2 Bundle 格式`

## Non-Functional Requirements

- **NFR-1（完整性）**：280 个 Markdown 文件全部完成转换，无遗漏；通过文件计数验证
- **NFR-2（合规性）**：所有文件通过 OKF v0.2 合规性检查——每个非保留 `.md` 有 frontmatter 和非空 `type`，`index.md`/`log.md` 格式正确
- **NFR-3（链接完整性）**：Bundle 内部交叉链接无断裂（Bundle 绝对路径指向的文件存在）；跨 Bundle 和外部链接保持原样
- **NFR-4（内容保真）**：正文内容字节级保留——仅修改 frontmatter 和链接路径，不改动正文文字
- **NFR-5（批次安全）**：每批转换不超过 7 个 Bundle（遵循 source-code-to-okf-wiki Skill 的批次限制），每批完成后验证再推进
- **NFR-6（可回滚性）**：转换在 Git 版本控制下进行，每个 Batch 作为一个原子提交，可随时回滚
- **NFR-7（Windows 兼容性）**：所有文件操作使用 Windows 兼容路径（`\` 分隔符），但 Markdown 链接内统一使用 `/` 路径

## Constraints

- **Technical**：
  - 操作系统：Windows（PowerShell 环境）
  - 文件系统：NTFS，路径长度限制 260 字符（深层嵌套需注意）
  - 现有静态站点构建：Sphinx/Jupyter Book（`conf.py`、`_config.toml`），转换后 toctree 路径需要同步更新以维持构建（但配置文件本身不在转换范围）
  - 编码：UTF-8（OKF 规范要求）
- **Business**：
  - 转换工作量大（31 Bundle、280 文件），必须分批执行
  - 原地转换存在风险——需确保 Git 工作区干净，每个 Batch 可独立回滚
- **Dependencies**：
  - OKF v0.2 规范定义（参考 `.agents/docs/knowledge/learning/01-agent-protocols-interfaces/knowledge-catalog-wiki/02-okf-specification.md`）
  - source-code-to-okf-wiki Skill 工作流（`d:\AI\.agents\skills\source-code-to-okf-wiki\SKILL.md`）
  - seven-concepts-cmd Skill 编排逻辑
  - Git 版本控制（原子提交）

## Assumptions

- A1：现有文档的正文内容质量已达标，无需在转换过程中进行内容审核或重写
- A2：现有 frontmatter 中的 `id` 字段可作为稳定标识符保留，不与 OKF 的字段冲突
- A3：`source` 字段引用的 `.temp/` 目录下的信源文件可能不存在，但仍按 OKF `sources` 格式记录（消费者容忍断链）
- A4：Sphinx 特有的 admonition 语法（`::{note}`、````{toctree}`` 等）在 OKF 中作为生产者自定义内容保留，不影响 OKF 合规性
- A5：散落在 `knowledge/learning/` 根目录的 .md 文件（如 okf-topic-index.md）归入最近的相关 Bundle 或作为板块级索引保留
- A6：`00-overview.md` 文件中已包含导航表格，可直接复用于根 `index.md` 的正文内容
- A7：转换日期统一使用 2026-08-22，`stale_after` 统一设为 2027-08-22
- A8：`generated.by` 使用 `process:docs-to-okf-conversion`，`verified.by` 使用 `process:seven-concepts-v`

## Acceptance Criteria

### AC-1：Bundle 结构合规

- **Given**：转换完成后的任意 Bundle 目录
- **When**：检查目录结构
- **Then**：根目录包含 `index.md`（含 `okf_version: "0.2"` frontmatter）和 `log.md`；存在 `concepts/` 子目录（含 `index.md`，无 frontmatter）；如有示例则存在 `examples/` 子目录；如有外部信源则存在 `references/` 子目录
- **Verification**: `programmatic`
- **Notes**：通过目录遍历和文件存在性检查验证

### AC-2：Frontmatter 合规

- **Given**：任意非保留 `.md` Concept 文件
- **When**：解析 YAML frontmatter
- **Then**：包含非空 `type` 字段；包含 `title`、`description`、`tags`、`generated`（含 `by` 和 `at`）、`verified`（含 `by` 和 `at`）、`status`；`generated.at` 和 `verified.at` 为合法 ISO 8601 格式
- **Verification**: `programmatic`
- **Notes**：通过 YAML 解析和字段存在性检查验证

### AC-3：Index 文件格式合规

- **Given**：任意子目录中的 `index.md`（非 Bundle 根）
- **When**：检查文件内容
- **Then**：不包含 YAML frontmatter；使用 Markdown 列表链接到目录内 Concept；链接文本包含文档 title 和 description
- **Verification**: `programmatic`

### AC-4：Bundle 根 Index 特殊字段

- **Given**：Bundle 根目录的 `index.md`
- **When**：检查 frontmatter
- **Then**：包含 `okf_version: "0.2"` 字段；其他 frontmatter 字段可选
- **Verification**: `programmatic`

### AC-5：交叉链接路径正确

- **Given**：任意 Concept 文件中的内部 Markdown 链接
- **When**：检查链接路径格式
- **Then**：Bundle 内部链接以 `/` 开头（Bundle 绝对路径）；链接目标文件存在
- **Verification**: `programmatic`
- **Notes**：跨 Bundle 链接和外部 URL 不做此要求

### AC-6：内容保真

- **Given**：转换前后的同一文件
- **When**：比较正文内容（排除 frontmatter 部分和已修正的链接路径）
- **Then**：正文字符内容保持一致（链接路径修正除外）
- **Verification**: `programmatic`
- **Notes**：通过 diff 工具验证正文部分未被修改

### AC-7：文件计数完整

- **Given**：转换后的 docs/ 目录
- **When**：统计所有 `.md` 文件数量
- **Then**：总数不少于 280（原文件数），新增文件为 index.md 和 log.md
- **Verification**: `programmatic`

### AC-8：Log 文件格式

- **Given**：任意 Bundle 的 `log.md`
- **When**：检查文件格式
- **Then**：使用 `## YYYY-MM-DD` 日期标题；条目以粗体词开头（如 `**Initialization**`）
- **Verification**: `programmatic`

### AC-9：类型映射合理

- **Given**：每个 Concept 文件的 `type` 字段
- **When**：人工审查类型与内容的匹配度
- **Then**：教程章节为 `Tutorial` 或 `Concept`，复盘报告为 `Report`，模式文档为 `Pattern`，参考资料为 `Reference`，示例代码为 `Example`
- **Verification**: `human-judgment`

### AC-10：分批提交可追溯

- **Given**：Git 提交历史
- **When**：查看转换期间的提交记录
- **Then**：每个 Batch 对应一个原子提交，提交信息遵循 Conventional Commits 格式（`feat(docs): convert <batch-name> to OKF v0.2 bundle`）
- **Verification**: `programmatic`

## Open Questions

- [ ] Q1：`knowledge/learning/` 根目录下的散文件（okf-topic-index.md、ai-engineering-four-milestones-wiki.md、anthropic-financial-services-wiki.md、octo-platform-wiki.md、three-ai-tools-wiki.md）应归入相邻 Bundle 还是作为独立 Bundle？建议：okf-topic-index.md 作为知识库级索引保留；其余 4 个文件内容若与已有 Wiki 重复则归入对应 Bundle，否则创建独立 Bundle
- [ ] Q2：`retrospective/reports/` 下嵌套的子目录（如 `milestone/retrospective-agency-deep-learning-20260706/`）是各自成为独立 Bundle 还是统一归入 retrospective-reports Bundle？建议：统一归入 retrospective-reports Bundle，在 concepts/ 下用子目录分组
- [ ] Q3：`codewhale/` 目录已有自己的嵌套结构（general/domain、tech、topics），是否保留其内部子目录结构还是展平为 concepts/ 下的文件？建议：在 concepts/ 下保留子目录结构
- [ ] Q4：Sphinx toctree 指令在文件移动后路径会失效，是否需要在本项目中同步更新 toctree 路径？建议：作为后续任务，不在本次转换范围内，但需要在 log.md 中记录此已知影响
- [ ] Q5：部分 Wiki 已有 `seven-concepts-report.md` 等非教程文件，这些应归入 `references/` 还是 `concepts/`？建议：方法论报告归入 `references/`，教程章节归入 `concepts/`
