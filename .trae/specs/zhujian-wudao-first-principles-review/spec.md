# 竹简悟道第一性原理系统性复盘分析 Spec

## Why
竹简悟道（zhujian-wudao）是一个以帛书《老子》为哲学根基的 AI 反思引导工具，从初始构思到 68 条洞察、完整 HTML 原型、双层 Skill 体系、可迁移方法论，经历了密集的迭代建设。项目积累了丰富的设计资产（项目规范/洞察库/产品规格/复盘报告/可迁移知识/HTML 原型/Skill 定义），但缺乏一次从第一性原理出发、覆盖全文件夹的系统性复盘，将分散的资产整合为对项目本质规律的统一认知，并萃取可复用的方法论。

## What Changes
- 对 `apps/zhujian-wudao/` 文件夹进行第一性原理系统性复盘分析
- 梳理三层资产：规范层（.agents 目录下 conventions/workflows/constraints/git/project）、知识层（docs 目录下的 product/insights/reviews/knowledge-transfer）、实现层（HTML 原型 + Skill 定义）
- 提炼关键洞察：从 68 条已有洞察、复盘报告、可迁移方法论中提取高阶规律
- 萃取可迁移方法论：识别可在其他项目中复用的模式与方法
- 生成结构化复盘分析报告并导出到 `apps/zhujian-wudao/.agents/docs/reviews/`

## Impact
- Affected specs: 无（新建独立分析 spec）
- Affected code: `apps/zhujian-wudao/.agents/docs/reviews/` 下新增复盘报告文件
- 不影响现有代码和文档内容

## ADDED Requirements

### Requirement: 第一性原理系统性复盘
系统 SHALL 对 `apps/zhujian-wudao/` 文件夹内的全部重要文件与组件进行第一性原理分析，覆盖规范层（.agents/ 下的 project/conventions/workflows/constraints/git）、知识层（docs/ 下的 product/insights/reviews/knowledge-transfer）、实现层（HTML 原型三件套 + 双层 Skill 体系），提炼关键洞察与核心规律。

#### Scenario: 规范层分析
- **WHEN** 分析 .agents/ 下的项目规范文件
- **THEN** 输出 project.md 核心概念词典的架构评价、conventions.md 规范设计的可迁移性评估、workflows.md 工作流设计的通用性分析、constraints.md 约束清单的哲学一致性检查、git.md 提交规范的最佳实践

#### Scenario: 知识层分析
- **WHEN** 分析 docs/ 下的知识资产
- **THEN** 输出产品规格文档（product-spec）的完整度评估、68 条洞察的三层结构（产品层/架构层/哲学层/元层）方法论、复盘报告的深度与闭环质量、可迁移知识的实际可复用性

#### Scenario: 实现层分析
- **WHEN** 分析 HTML 原型和 Skill 定义
- **THEN** 输出 HTML 三件套（styles.css/data.js/app.js）的架构设计与可扩展性、竹简洞察撰写者 Skill 的设计模式、道德经学者配图 Skill 的领域专业性

### Requirement: 洞察提炼与深度创新
系统 SHALL 从分析中提炼具有深度与创新性的关键洞察，不重复已有 68 条洞察的内容，而是从更高维度（元视角）审视项目本身的构建方法论与底层逻辑。

#### Scenario: 元洞察生成
- **WHEN** 完成全文件夹分析
- **THEN** 生成至少 5 条元洞察，覆盖项目架构设计哲学、知识管理体系、约束驱动的开发方法论、Skill 双层架构模式、可迁移方法论的萃取机制

### Requirement: 可迁移方法论萃取
系统 SHALL 从项目中萃取具有普适性与可迁移性的经验与方法论，覆盖产品设计方法论、AI 协作规范体系设计、洞察驱动开发模式、知识管理体系构建、Skill 架构设计模式五个维度。

#### Scenario: 方法论萃取
- **WHEN** 分析并提炼可复用模式
- **THEN** 输出的每条方法论包含：来源（项目中的具体实践）、核心原理（为什么有效）、适用场景（什么情况下可用）、迁移指南（如何在其他项目中应用）、注意事项（边界条件与限制）

### Requirement: 结构化报告导出
系统 SHALL 将复盘分析结果导出为结构化的 Markdown 报告，遵循竹简悟道项目复盘报告的命名与 frontmatter 规范，存放于 `apps/zhujian-wudao/.agents/docs/reviews/` 目录。

#### Scenario: 报告导出
- **WHEN** 完成分析并撰写报告
- **THEN** 报告文件以 `YYYY-MM-DD-zhujian-wudao-first-principles-review.md` 命名，frontmatter 包含 source/title/date/type/tags 字段，内容包含执行摘要、分析方法、各层分析、元洞察、可迁移方法论、结论与建议等章节
