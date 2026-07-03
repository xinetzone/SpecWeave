---
version: 1.0
---

# MyST Directives/Roles 系统在 Agent Spec 开发中的可迁移性技术评估 - Product Requirement Document

<!-- changelog -->
## Changelog
- 2026-07-02 | added | 初始版本：定义评估范围、核心分析维度、报告结构和验收标准
<!-- changelog -->

## Overview
- **Summary**: 基于已系统学习的 ExecutableBooks/MyST Markdown 官方文档（特别是 Directives 块级扩展和 Roles 行内扩展机制），结合项目现有 MDI（Markdown as Interface）v1.0 工具链的实现现状，产出一份深度技术评估报告，分析 MyST 指令/角色系统在 AI Agent 开发规范说明文档（Spec）中的可迁移性。报告涵盖核心概念适配性、技术挑战、实施路径、架构兼容性、优劣势评估及前瞻性洞察。
- **Purpose**: 当前项目的 Spec 文档采用 YAML frontmatter + 自由 Markdown 正文结构，MDI Parser 已部分借鉴 MyST-style directives（反引号围栏的 `{endpoint}`/`{param}` 等），但对冒号围栏（`:::`）、Roles 行内扩展、YAML 选项块、嵌套规则等 MyST 核心特性缺乏系统性评估。本评估旨在为后续是否、如何、在多大程度上将 MyST 语法体系迁移到 Agent Spec 领域提供决策依据，避免盲目引入不兼容的语法扩展或错过有价值的结构化表达能力。
- **Target Users**: Agent 开发者、MDI 工具链维护者、Spec 标准化设计者、技术架构决策者

## Goals
- 系统性分析 MyST Directives/Roles 核心概念与 Agent Spec 场景的映射关系和适配度
- 识别迁移过程中的关键技术挑战（解析器、兼容性、降级显示、学习曲线等）
- 提出至少 2-3 种潜在实施路径（保守/平衡/激进），并给出推荐方案
- 评估 MyST 语法与现有 MDI 架构、markdown-it-py 解析器、三类 Profile（Skill/WebApi/CliTool）的兼容性
- 分析迁移后带来的具体优势（结构化、可验证、代码生成、一致性等）与局限性（复杂度、工具链依赖、可移植性等）
- 结合 Agent 开发典型场景（技能定义、API 接口、CLI 工具、工作流编排、协作协议等）给出场景化建议
- 产出具有前瞻性的洞察，包括 MyST 生态演进趋势对 Agent Spec 长期发展的启示

## Non-Goals (Out of Scope)
- 不直接修改 MDI Parser 代码或扩展 directives/roles 支持（本任务仅产出评估报告）
- 不引入完整的 myst-parser（Sphinx/docutils 生态依赖，与现有轻量架构冲突）
- 不强制要求现有 Spec 文档迁移到新语法
- 不实现完整的 Roles 行内解析器
- 不构建 MyST 到其他 IDL（OpenAPI/JSON Schema）的双向转换工具
- 不评估 reStructuredText 本身（仅评估 MyST 对 rST 概念的 Markdown 化移植）
- 不涉及 Jupyter Notebook 执行和计算性叙事（这是 MyST 的核心场景但非 Agent Spec 需求）

## Background & Context
- **MyST 语法体系**（已学习并整理在 [01-myst-syntax.md](../../../../docs/knowledge/learning/executablebooks-myst-guide/01-myst-syntax.md)）：
  - Directives 是块级扩展容器，支持两种围栏（`:::` 冒号围栏用于 Markdown 内容、`` ``` `` 反引号围栏用于代码/公式/图表）
  - 选项支持三种写法：`:key: value` 短格式、`---` YAML 块格式、内联 `.class #label key=val` 格式
  - Roles 是行内扩展，语法 `{rolename}`content``，支持内联选项
  - 嵌套通过增加围栏符号数量实现（每嵌套一层符号数+1）
  - Frontmatter 支持 TOML(`+++`) 和 YAML(`---`) 两种格式
- **现有 MDI 实现现状**（[parser.py](file:///d:/spaces/SpecWeave/.agents/scripts/mdi/parser.py)）：
  - 基于 markdown-it-py（CommonMark 100% 兼容），配合 front_matter_plugin 和 tasklists_plugin
  - 已支持 MyST-style directives：仅反引号围栏形式（`` ```{name} args ``），选项仅支持 `:key: value` 格式
  - 已实现 directives：`{endpoint}`、`{param}`、`{response}`、`{error}`、`{note}/{warning}/{danger}/{tip}/{important}/{caution}/{hint}/{info}/{seealso}`
  - 不支持：冒号围栏（`:::`）、YAML 选项块（`---`）、Roles 行内扩展（`{role}`text``）、内联选项（`.class #label`）、嵌套围栏规则
  - frontmatter 仅支持 YAML(`---`)，TOML(`+++`) 通过 `x-toml-ref` 外部引用支持
- **现有决策约束**（[markdown-as-interface-research/spec.md FR-2.9](../markdown-as-interface-research/spec.md)）：
  - 决策记录："不引入完整 myst-parser（Sphinx 扩展，依赖 docutils/Jinja2 过重），仅借鉴其 directive 语法设计，在 markdown-it-py fence token 基础上自行解析"
  - directives 与传统"标题+表格"格式双模式并存，完全向后兼容现有 14 个 SKILL.md
- **Agent Spec 文档现状**：
  - spec.md 采用固定章节结构（Why/What Changes/Impact/ADDED/MODIFIED/REMOVED Requirements + Scenario WHEN/THEN）
  - tasks.md 采用任务列表格式，含 Priority/Depends On/Description/Test Requirements
  - checklist.md 采用 Markdown 复选框列表
  - 所有文档使用 YAML frontmatter，部分开始使用 TOML frontmatter（学习资料库文档）
  - 现有 check-spec-format.py 做格式验证

## Functional Requirements
- **FR-1**: 核心概念适配性分析矩阵
  - FR-1.1: 建立 MyST 核心概念（Directives、Roles、Fences、Options、Arguments、Nesting、Frontmatter）与 Agent Spec 需求的映射表，标注"高度适配/部分适配/不适配"及理由
  - FR-1.2: 逐项分析每种 MyST 内置 Directive（admonitions、figure、code-block、math、table、list-table、toc、include、dropdown、card、tab-set 等）在 Agent Spec 中的潜在用途
  - FR-1.3: 逐项分析每种常见 MyST Role（abbr、sub/sup、math、ref/numref/doc/cite、download/link、kbd/file、emphasis/strong/literal 等）在 Agent Spec 中的潜在用途
  - FR-1.4: 分析两种围栏语法（`:::` vs `` ``` ``）在 Agent Spec 文档中的适用性差异（包括编辑器支持、GitHub 降级显示、AI 可解析性）

- **FR-2**: 关键技术挑战识别与分析
  - FR-2.1: 解析器扩展挑战：在 markdown-it-py 基础上增加冒号围栏支持、YAML 选项块解析、Roles 行内扩展、嵌套规则的技术复杂度评估
  - FR-2.2: 双格式兼容挑战：directives 与现有"标题+表格"格式长期并存的维护成本和一致性问题
  - FR-2.3: 降级显示挑战：在 GitHub/IDE 预览/普通 Markdown 阅读器中 MyST 语法的可读性表现
  - FR-2.4: AI 理解挑战：LLM 对 MyST 语法的理解准确度与传统 Markdown 格式的对比分析（基于训练数据分布）
  - FR-2.5: Frontmatter 格式统一挑战：TOML(`+++`) vs YAML(`---`) 双格式在知识库索引、MDI 解析、编辑器支持方面的权衡
  - FR-2.6: 向后兼容挑战：现有 40+ 个 Spec 文档和 14 个 SKILL.md 的迁移成本评估

- **FR-3**: 实施路径设计（2-3 种方案）
  - FR-3.1: 方案一（保守）：仅补充现有 MyST-style directives 对 YAML 选项块的支持，不引入冒号围栏和 Roles，保持轻量架构
  - FR-3.2: 方案二（平衡/推荐）：引入冒号围栏支持（基于 mdit-py-plugins 的 colon_fence 插件）+ 有限的 Roles 集合（ref/abbr/doc/kbd 等高频行内扩展），不引入完整 Roles 系统
  - FR-3.3: 方案三（激进）：引入 mdformat-myst 或 myst-docutils 等更完整的 MyST 解析链，支持 Roles 系统、交叉引用、include 指令等完整能力
  - FR-3.4: 每个方案包含：具体变更范围、代码影响评估、新增依赖、性能影响、兼容性影响、适用场景分析
  - FR-3.5: 给出明确推荐方案及推荐理由

- **FR-4**: 与 Agent 架构的兼容性考量
  - FR-4.1: mdit-py-plugins 生态分析：colon_fence、dollarmath、amsmath、container 等现成插件的可用性和成熟度
  - FR-4.2: 三类 Profile（Skill/WebApi/CliTool）各自最需要的 Directive/Role 类型分析
  - FR-4.3: 代码生成器（Python/TypeScript/OpenAPI/MCP）如何从增强后的 directives 中提取更多结构化信息
  - FR-4.4: Spec 验证器（check-spec-format.py）如何利用 directives 提供更精确的结构验证
  - FR-4.5: 与现有 frontmatter.py、markdown.py 共享库的集成点分析

- **FR-5**: 优势与局限性评估
  - FR-5.1: 结构化优势：directives 提供的语义标记如何提升 AI 理解精度、自动化验证能力、代码生成质量
  - FR-5.2: 可维护性优势：统一语法 vs 自由格式的长期维护成本对比
  - FR-5.3: 生态优势：与 MyST 工具链（mystmd、Jupyter Book、Sphinx）互操作的可能性评估
  - FR-5.4: 学习曲线局限：开发者需要学习 MyST 特有语法的成本
  - FR-5.5: 工具链依赖局限：脱离 MyST 生态后语法的可移植性问题
  - FR-5.6: 过度工程风险：引入过多 directive 类型导致 Spec 写作负担加重的风险

- **FR-6**: Agent 开发场景化建议
  - FR-6.1: 技能定义（SKILL.md）场景：哪些 directives/roles 最有价值，哪些是不必要的
  - FR-6.2: Web API 接口定义场景：`{endpoint}` 指令的 YAML 选项块扩展是否值得
  - FR-6.3: CLI 工具定义场景：参数表格 vs `{param}` directive 的取舍
  - FR-6.4: 工作流/协议文档场景：`dropdown`/`tab-set`/`card` 等 UI 组件类 directive 是否适用于 Spec
  - FR-6.5: 协作规范/治理文档场景：admonitions、include、toc 等指令的适用性
  - FR-6.6: 学习资料/Wiki 场景：MyST 完整语法的适用度（当前知识库已使用 TOML frontmatter）

- **FR-7**: 前瞻性洞察
  - FR-7.1: MyST 生态演进趋势（mystmd 作为独立工具链、与 Jupyter Book v2 的关系、Typst 支持等）对 Agent Spec 的长期影响
  - FR-7.2: AI 原生文档（AI-native documentation）趋势下，结构化标记语言的价值判断
  - FR-7.3: Markdown 作为 IDL 的长期演进路径预测（MDI 在其中的定位）
  - FR-7.4: 跨 Agent 互操作场景下，MyST 作为标准化文档格式的潜力评估

## Non-Functional Requirements
- **NFR-1**: 报告深度：每个分析维度必须包含具体技术论据（代码引用、语法对比、性能数据引用），不能只有泛泛而谈的结论
- **NFR-2**: 代码引用准确性：所有引用现有代码（parser.py、models.py、spec.md 等）的位置必须精确到文件路径和行号范围
- **NFR-3**: 实用性：建议必须可操作（包含具体的下一步动作、优先级排序），避免纯理论分析
- **NFR-4**: 客观性：对每个方案的优势和局限性都要客观陈述，避免预设立场
- **NFR-5**: 可读性：报告使用中文编写，配合 Mermaid 图表（架构图、决策树、对比矩阵）增强理解
- **NFR-6**: 字数：报告主体不少于 6000 字，确保分析深度

## Constraints
- **Technical**:
  - 基于现有 Python 3.13+ 技术栈和 markdown-it-py 解析器
  - 不引入 docutils、Sphinx、Jinja2 等重量级依赖
  - 报告中所有 MyST 语法示例必须正确（参考已验证的学习资料库文档）
  - Windows 环境兼容（PowerShell 7+、UTF-8 编码）
- **Business**:
  - 报告产出后不要求立即实施代码变更，仅作为决策参考
  - 评估结论需要与现有 MDI v1.0 的"轻量架构"决策保持一致，除非有充分论据支持调整
- **Dependencies**:
  - 依赖已完成的 ExecutableBooks 学习资料库（作为 MyST 语法的权威参考）
  - 依赖现有 MDI 工具链代码作为分析基线
  - 依赖现有 Spec 文档样本（.trae/specs/ 下 40+ 个spec）作为使用场景参考

## Assumptions
- 现有 MDI Parser 中的 MyST-style directives 实现可以作为扩展基础，无需重写
- mdit-py-plugins 的 colon_fence 插件质量足够用于生产环境（需要在报告中验证）
- Agent 开发者对学习 5-10 个常用 directive 的成本是可接受的
- LLM 对 MyST 语法的理解不会显著差于对自由格式 Markdown 的理解（需要在报告中分析验证）
- 本报告是技术评估而非最终决策文档，最终是否实施取决于架构评审

## Acceptance Criteria

### AC-1: 核心概念适配性矩阵完整性
- **Given**: 评估报告完成
- **When**: 审查"核心概念适配性"章节
- **Then**: 包含至少 6 个 MyST 核心概念、10+ 个内置 Directive、8+ 个常见 Role 的适配性评估，每个有"适配度评级+理由+示例场景"
- **Verification**: `human-judgment`

### AC-2: 技术挑战分析的具体性
- **Given**: 评估报告完成
- **When**: 审查"关键技术挑战"章节
- **Then**: 识别至少 5 个技术挑战，每个包含：问题描述、影响范围、技术复杂度评级（低/中/高）、潜在解决方案方向
- **Verification**: `human-judgment`

### AC-3: 实施路径方案完整性
- **Given**: 评估报告完成
- **When**: 审查"实施路径"章节
- **Then**: 包含 3 种方案，每个方案有：变更清单、依赖影响、性能影响、兼容性评估、适用场景；且有明确的推荐方案和推荐理由
- **Verification**: `human-judgment`

### AC-4: 代码引用精确性
- **Given**: 评估报告完成
- **When**: 检查报告中对现有代码的引用
- **Then**: 所有代码引用使用 clickable 绝对路径格式（`file:///`），引用的行号范围可验证，函数名/变量名准确
- **Verification**: `programmatic` + `human-judgment`

### AC-5: 场景化建议覆盖度
- **Given**: 评估报告完成
- **When**: 审查"场景化建议"章节
- **Then**: 覆盖至少 5 个 Agent 开发典型场景，每个场景给出"推荐使用/可选使用/不推荐使用"的语法元素清单和理由
- **Verification**: `human-judgment`

### AC-6: 前瞻性洞察的质量
- **Given**: 评估报告完成
- **When**: 审查"前瞻性洞察"章节
- **Then**: 包含至少 4 个前瞻性观点，每个观点有论据支撑（引用官方路线图、行业趋势、技术类比等），而非主观臆测
- **Verification**: `human-judgment`

### AC-7: 报告格式规范
- **Given**: 评估报告完成
- **When**: 检查报告文件
- **Then**: 使用 TOML frontmatter、包含目录导航、包含 Mermaid 图表（至少 2 张：适配性映射图、实施路径决策树）、使用表格做对比分析、中文编写、字数≥6000字
- **Verification**: `human-judgment` + `programmatic`

### AC-8: Mermaid 图表有效性
- **Given**: 评估报告完成
- **When**: 在支持 Mermaid 的 Markdown 预览器中查看报告
- **Then**: 所有 Mermaid 图表正确渲染，无语法错误
- **Verification**: `programmatic`（运行 mermaid 语法检查）

### AC-9: 客观性检查
- **Given**: 评估报告完成
- **When**: 通读全文
- **Then**: 每个推荐方案都同时陈述了优势和劣势/风险；没有出现"显然"、"毫无疑问"等预设立场词汇；对"不引入完整myst-parser"的既有决策进行了重新评估但未轻易否定
- **Verification**: `human-judgment`

## Open Questions
- [ ] mdit-py-plugins 的 colon_fence 插件当前稳定性和维护状态如何？是否有已知 bug？
- [ ] LLM 训练数据中 MyST 语法的覆盖度是否有公开数据？（可能需要基于经验推断）
- [ ] 现有社区是否有"轻量 MyST 子集"的先例或规范可供参考？
- [ ] mystmd 团队未来是否有计划提供独立的 JS/Python 解析库（不依赖 Sphinx）？
