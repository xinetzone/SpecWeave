---
id: "universal-prd-template-extraction"
title: "通用PRD/项目Spec模板萃取：基于第一性原理的复盘与提炼"
source: "用户/spec指令"
created_at: "2026-07-09"
completed_at: "2026-07-09"
status: "completed"
theme: "spec-workflow"
template_location: "docs/retrospective/patterns/methodology-patterns/spec-workflow/universal-prd-template.md"
reference_spec: ".trae/specs/retrospectives-insights/first-principles-comprehensive-research/spec.md"
version: "1.0"
total_files: 9
patterns_extracted: 1
---

# 通用PRD/项目Spec模板萃取 - Product Requirement Document

## Overview
- **Summary**: 以经过端到端验证（从规划→执行→复盘→模式沉淀完整生命周期）的`first-principles-comprehensive-research`项目Spec为高质量样本，运用第一性原理方法论进行系统性结构解析、核心逻辑梳理和关键要素识别，剥离项目特定内容，提炼出一套具有普适性、可迁移性、可复用性的通用PRD/项目Spec模板，配套编写最佳实践指南和使用说明，为后续所有新项目立项提供标准化Spec编写基础。
- **Purpose**: 当前项目中存在两种Spec格式并存（增量变更的六节Change Spec格式 vs 新项目立项的PRD格式），但PRD格式尚未形成统一模板和最佳实践，导致不同项目Spec质量参差不齐、要素缺失、结构不一致。通过对高质量样本的深度复盘和第一性原理提炼，可：（1）统一新项目Spec的结构和质量标准；（2）明确每个章节的核心目的和写作要求；（3）沉淀Spec生命周期管理的最佳实践（从候选→执行→完成的状态追踪）；（4）为自动化Spec检查脚本提供模板基准。
- **Target Users**: 智能体开发者、项目Orchestrator、Architect角色、所有需要创建新项目Spec的团队成员

## Goals
- G1: 对参考Spec进行第一性原理解构，识别其核心结构要素和设计逻辑（区分本质要素与项目特定内容）
- G2: 提炼通用YAML frontmatter元数据规范，覆盖项目从规划到完成的全生命周期追踪需求
- G3: 提炼通用PRD正文结构，明确每个章节的核心目的、必填要素、写作要求和检查要点
- G4: 明确两种Spec格式（Change Spec vs PRD Spec）的适用场景边界和选择决策树
- G5: 编写配套的最佳实践指南，包含常见陷阱、写作技巧、质量检查清单
- G6: 将模板和最佳实践沉淀为方法论模式，归档至spec-workflow模式目录
- G7: 更新spec-writing-guide，整合通用PRD模板作为新项目立项的标准规范
- G8: 完成本项目自身的复盘，验证模板的自适用性（dogfooding）

## Non-Goals (Out of Scope)
- 不替换或废弃现有增量变更的六节Change Spec格式（Why/What Changes/Impact/ADDED/MODIFIED/REMOVED）——该格式已验证适用于小范围变更
- 不开发自动化的Spec生成或检查工具（工具开发可作为后续独立项目）
- 不对历史上所有已存在的PRD Spec进行回溯性改造——仅面向未来新项目
- 不覆盖产品九节叙事弧（spec-nine-section-narrative）面向C端产品的特定章节——本模板是通用项目模板，产品九节作为特定领域适配指南在最佳实践中引用
- 不翻译为英文或其他语言——当前项目以中文为主要工作语言

## Background & Context
- **参考Spec验证基础**: `first-principles-comprehensive-research` Spec经历了完整生命周期：初始规划（v1.0）→ 执行（知识档案建立12文件）→ 迭代（指令集创建、双向关联、模式沉淀）→ 复盘v1.1 → 派生子项目v2.0候选，是经过实战验证的高质量Spec样本。
- **现有规范基础**: `.agents/rules/spec-writing-guide/` 已定义了增量变更的六节Change Spec格式，但缺少面向新项目/大项目立项的PRD模板规范。
- **相关模式沉淀**: 已有`spec-nine-section-narrative`（面向C端产品）、`spec-reference-validation`（Spec引用验证）等spec-workflow相关模式，但缺少通用项目PRD模板。
- **第一性原理应用**: 本项目自身必须践行第一性原理方法论——不是简单复制参考Spec结构，而是追问"每个章节为什么存在？它解决什么根本问题？没有它会导致什么风险？"，剥离非本质要素，保留真正不可缺少的核心。

## Functional Requirements

- **FR-1**: 参考Spec的第一性原理解构分析
  - 对参考Spec进行逐章解析，识别每个章节的核心功能（解决什么问题）
  - 区分"本质要素"（所有项目Spec都必须有）与"项目特定要素"（仅适用于第一性原理研究类项目）
  - 识别参考Spec的演进轨迹（v1.0→v1.1新增了什么、为什么新增）
  - 分析优秀设计决策：为什么用Given/When/Then格式写AC？为什么要显式列出Non-Goals？为什么要追踪Open Questions？
  - 识别可改进点：参考Spec中哪些地方可以更通用化、哪些字段命名可以更一致
  - 输出：deconstruction-analysis.md（解构分析报告）

- **FR-2**: 通用YAML frontmatter元数据规范
  - 提炼必填元数据字段：id、title、source、created_at、status、theme
  - 提炼推荐元数据字段：version、completed_at、archive_location、total_files、parent_spec、child_specs、key_commits、patterns_extracted
  - 定义每个字段的含义、取值规范、填写时机（规划时填什么、执行中更新什么、完成后补充什么）
  - 定义status字段的生命周期状态机：candidate → planning → in-progress → completed → archived
  - 建立元数据字段与项目管理的映射关系（如key_commits用于追踪里程碑）
  - 输出：frontmatter-specification.md（元数据规范）

- **FR-3**: 通用PRD正文结构提炼
  - Overview章节：Summary/Purpose/Target Users三要素的核心目的和写作要求
  - Goals章节：G1/G2...编号目标的写作要求（可衡量、可达成、与AC对应）
  - Non-Goals章节：显式范围边界的重要性、写作原则、常见陷阱
  - Background & Context章节：如何提供足够上下文而不冗余
  - Functional Requirements章节：FR编号、层级结构、颗粒度要求
  - Non-Functional Requirements章节：NFR分类维度、可验证性要求
  - Constraints章节：Technical/Business/Dependencies三分法
  - Assumptions章节：显式化隐含假设的重要性
  - Acceptance Criteria章节：Given/When/Then格式、verification类型（programmatic/human-judgment）、与Goals/FR的追溯关系
  - Open Questions章节：追踪未决问题的方式、解决后如何标记
  - 每个章节包含：核心目的、必填要素、写作要求、正反示例、检查要点
  - 输出：prd-structure-guide.md（正文结构指南）

- **FR-4**: Spec格式选择决策框架
  - 明确两种Spec格式的适用场景：
    - PRD Spec格式：新项目立项、大型研究课题、跨多文件/多模块的大型工作
    - Change Spec格式：小范围增量变更、单文件修改、已有Spec的补充修改
  - 建立决策树：根据项目规模、影响范围、是否新项目等维度快速判断使用哪种格式
  - 说明混合使用场景：大项目用PRD Spec，大项目内部的小变更用Change Spec补充
  - 输出：format-selection-guide.md（格式选择指南）

- **FR-5**: 最佳实践与常见陷阱
  - 收集整理Spec写作中的常见陷阱：如Non-Goals写得太模糊、AC不可验证、Assumptions隐而不写、Goals与AC不对应等
  - 提炼最佳实践：如Spec演进时如何更新、如何派生子Spec、如何追踪里程碑提交、如何进行dogfooding验证
  - 编写Spec质量自检清单（10-15项关键检查点）
  - 引用相关已有模式：spec-nine-section-narrative（产品类项目适配）、spec-reference-validation（引用验证）、spec-triple-sync（三同步原则）等
  - 输出：best-practices.md（最佳实践指南）

- **FR-6**: 通用PRD模板文件生成
  - 生成可直接复制使用的空白模板文件，包含所有必填章节和填写提示
  - 模板中包含注释说明每个部分应该填写什么内容
  - 模板遵循项目所有现有规范：kebab-case命名、MDI v1.0 frontmatter、Markdown格式、单文件不超过500行
  - 输出：universal-prd-template.md（通用模板文件，归档至模式目录）

- **FR-7**: 整合至现有规范体系
  - 更新`.agents/rules/spec-writing-guide/`，新增章节介绍通用PRD模板和格式选择决策框架
  - 在spec-workflow模式目录创建README索引（如不存在），将新模板作为模式归档
  - 确保新模板与现有spec-writing-guide、check-spec-format.py等工具链兼容
  - 为新模板和指南建立双向导航链接

- **FR-8**: 自适用性验证（Dogfooding）
  - 使用新提炼的通用PRD模板重新审视本项目自身的Spec
  - 验证模板是否能够完整覆盖本项目的需求，是否有缺失要素
  - 根据验证结果迭代优化模板
  - 在复盘中记录dogfooding过程和发现的问题

## Non-Functional Requirements
- **NFR-1**: 通用性 - 模板必须能够适配不同类型项目：研究类项目、开发类项目、文档类项目、工具类项目，不绑定特定领域
- **NFR-2**: 实用性 - 每个章节的指南必须有可操作的写作要求和正反示例，不能只有抽象原则
- **NFR-3**: 简洁性 - 模板本身不应过于冗长，核心模板文件控制在200行以内（不含示例和注释）
- **NFR-4**: 兼容性 - 必须与现有项目规范、工具链（check-spec-format.py、check-links.py等）兼容
- **NFR-5**: 可演进性 - 模板设计需支持后续迭代更新，元数据和章节扩展不应破坏向后兼容性
- **NFR-6**: 可追溯性 - 每个设计决策必须有依据（来自参考Spec的验证经验或第一性原理分析），不能凭空发明
- **NFR-7**: 文件规范 - 所有输出文件遵循项目命名规范、Markdown格式、YAML frontmatter标准、单文件不超过500行

## Constraints
- **Technical**: 
  - 基于现有Markdown/MDI格式，不引入新的文件格式
  - 必须兼容现有工具链脚本（无需修改工具脚本即可使用新模板）
- **Business**: 
  - 聚焦于通用项目模板，不针对特定行业或领域做过度定制
- **Dependencies**: 
  - 参考Spec（first-principles-comprehensive-research/spec.md）作为解构分析样本
  - 现有spec-writing-guide作为规范整合基础
  - 已有spec-workflow相关模式作为关联参考

## Assumptions
- 假设两种Spec格式并存是合理的——不需要强行统一为单一格式，不同场景适用不同格式
- 假设参考Spec的质量足够高，其核心结构设计具有普适性——如果解构发现重大缺陷，将在分析中明确指出并提出改进方案
- 假设用户期望的是"经过实战验证"的模板，而非从零发明的理论模板——因此参考Spec的实践经验是核心输入
- 假设本项目完成后，后续新项目将采用该模板作为Spec编写标准

## Acceptance Criteria

### AC-1: 第一性原理解构分析质量
- **Given**: 参考Spec作为输入
- **When**: 完成解构分析报告
- **Then**: （1）参考Spec每个章节都有核心功能分析；（2）明确区分本质要素与项目特定要素；（3）分析参考Spec的演进逻辑（v1.0→v1.1）；（4）至少识别5个优秀设计决策和2个可改进点
- **Verification**: `human-judgment`
- **Notes**: 解构不是简单描述，要回答"为什么这个章节存在"

### AC-2: Frontmatter元数据规范完整性
- **Given**: 元数据规范文档
- **When**: 检查元数据字段定义
- **Then**: （1）明确区分必填字段和推荐字段；（2）每个字段有含义、取值规范、填写时机说明；（3）定义了完整的status生命周期状态机；（4）字段数量合理（必填6-8个，推荐不超过10个）
- **Verification**: `programmatic`

### AC-3: PRD正文结构指南质量
- **Given**: 正文结构指南文档
- **When**: 检查每个章节的指南内容
- **Then**: （1）覆盖Overview/Goals/Non-Goals/Background/FR/NFR/Constraints/Assumptions/AC/Open Questions所有核心章节；（2）每个章节有核心目的、必填要素、写作要求；（3）至少5个章节有正反示例对比；（4）每个章节有明确的检查要点
- **Verification**: `human-judgment`

### AC-4: 格式选择决策框架清晰度
- **Given**: 格式选择指南
- **When**: 按照决策树判断5个不同场景的项目应该用哪种格式
- **Then**: （1）决策树有明确的判断维度（至少3个）；（2）5个测试场景都能得出明确结论（PRD/Change）；（3）混合使用场景有清晰说明
- **Verification**: `human-judgment`

### AC-5: 最佳实践实用性
- **Given**: 最佳实践指南
- **When**: 检查内容实用性
- **Then**: （1）至少列出8个常见陷阱，每个陷阱有反面示例和正确做法；（2）质量自检清单包含10-15个检查项；（3）引用至少3个已有相关模式
- **Verification**: `human-judgment`

### AC-6: 通用模板文件可用性
- **Given**: 通用PRD模板文件
- **When**: 尝试基于模板创建一个简单项目Spec
- **Then**: （1）模板包含所有必填章节和frontmatter字段；（2）有清晰的填写提示；（3）模板本身（不含注释示例）不超过200行；（4）遵循项目文件规范（kebab-case、YAML格式正确）
- **Verification**: `programmatic`

### AC-7: 规范体系整合完成
- **Given**: 所有模板和指南文件完成
- **When**: 检查与现有规范体系的整合
- **Then**: （1）spec-writing-guide已更新，包含PRD模板介绍和格式选择；（2）spec-workflow模式目录有索引；（3）所有双向导航链接有效（check-links验证通过）；（4）不破坏现有Change Spec格式的规范
- **Verification**: `programmatic`

### AC-8: Dogfooding自适用性验证
- **Given**: 本项目使用新模板
- **When**: 完成项目复盘
- **Then**: （1）本项目Spec可以用新模板完整覆盖，无重大缺失；（2）Dogfooding发现的问题已记录并在模板中修复；（3）复盘报告中包含自验证过程
- **Verification**: `human-judgment`

### AC-9: 文件规范符合性
- **Given**: 所有输出文件生成完毕
- **When**: 运行项目规范检查
- **Then**: 所有文件名符合kebab-case英文命名，YAML frontmatter格式正确，单文件不超过500行，无文件放置在项目根目录，所有本地链接验证通过
- **Verification**: `programmatic`

## Open Questions
- [ ] 模板是否应该包含"RACI责任矩阵"作为可选章节？（部分项目明确需要，部分项目不需要）
- [ ] 对于非常小的项目（单文件、<1天工作量），是否需要一个"迷你PRD"简化版模板？
- [ ] 元数据中是否需要增加"estimated_effort"或"priority"字段用于项目排期？
- [ ] 模板归档位置：作为模式放在patterns/methodology-patterns/spec-workflow/，还是作为规则放在.agents/rules/spec-writing-guide/，还是两者都有链接？
- [ ] 是否需要提供一个"填写示例"（用一个简单示例项目展示如何填写模板）？
