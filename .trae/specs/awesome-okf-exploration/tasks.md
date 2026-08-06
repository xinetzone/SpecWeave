---
id: awesome-okf-exploration-tasks
title: Awesome OKF 七概念探索 - 实施计划
type: Tasks
timestamp: 2026-08-06
---

# Awesome OKF 七概念探索 - 实施计划

## [ ] Task 0: 前置阅读 - 熟悉okf-wiki现有知识
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 阅读okf-wiki的8篇文档（00-07），了解已覆盖的OKF通用知识范围
  - 重点标记okf-wiki中未覆盖的内容（如中文生态具体项目案例、零依赖工具链实现细节、Skill工作流设计模式）
  - 理解okf-wiki的frontmatter风格、链接风格、章节组织方式，确保新报告风格一致
- **Acceptance Criteria Addressed**: AC-1, AC-7
- **Test Requirements**:
  - `human-judgement` TR-0.1: 能说出okf-wiki 8篇文档各自的核心内容
  - `human-judgement` TR-0.2: 能识别okf-wiki已覆盖vs未覆盖的内容边界
- **Notes**: 本任务已部分完成（已读README、00-overview、07-resources），执行时补读01-06

## [ ] Task 1: R阶段 - 事实采集（Retrospective）
- **Priority**: high
- **Depends On**: Task 0
- **Description**: 
  - 系统性扫描awesome-okf仓库，聚焦项目特有事实，四个维度：
    1. **Producer插件维度**：读取plugins/下7个工具的源代码结构（pyproject.toml、cli.py、核心模块），记录：零依赖验证、CLI入口分发机制、包结构、输入输出格式
    2. **Skill维度**：读取skills/下7个SKILL.md及附带脚本，记录：工作流步骤、核心原则、反模式、配套脚本、引用约定
    3. **提案维度**：读取docs/下3份扩展提案，记录：扩展字段设计、向后兼容策略、与上游规范的关系
    4. **Dogfooding维度**：分析awesome-okf自身如何作为OKF bundle（哪些.md有frontmatter、type字段取值、index.md/log.md结构、交叉链接模式）
  - 每条事实必须：(1) 纯客观描述无因果词；(2) 附带awesome-okf具体文件路径和行号证据；(3) 编号F01、F02...
  - OKF通用概念（如"什么是frontmatter"）不重复采集，用链接指向okf-wiki对应章节
  - 目标≥20条事实
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: 事实清单中不含"因为/所以/导致/错误/失误/问题"等因果判断词
  - `human-judgement` TR-1.2: 每条事实附带awesome-okf具体文件路径和行号，可验证
  - `human-judgement` TR-1.3: 事实总数≥20条，覆盖插件/Skill/提案/dogfooding四个维度
  - `human-judgement` TR-1.4: 事实聚焦awesome-okf项目特有内容，不重复okf-wiki已覆盖的OKF通用概念
- **Notes**: 禁止先有结论再找事实；事实只描述"是什么"，不解释"为什么"

## [ ] Task 2: I阶段+F阶段 - 本质洞察（Insight + First Principles）
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 基于Task 1的事实清单，运用第一性原理追问：
    - awesome-okf为什么选择"零第三方依赖，全部标准库"？这带来什么trade-off？
    - Producer（Python脚本）和Skill（Markdown工作流）为什么分两层？它们各自承担什么职责？
    - 3份扩展提案为什么都采用"新增可选字段、不动MUST"的策略？这与OKF的什么核心哲学一致？
    - awesome-okf自身作为OKF bundle（dogfooding）验证了什么？有哪些不完美的地方？
    - 这些模式中哪些可以迁移到SpecWeave？迁移时需要做什么适配？
  - 产出≥3条核心洞察，每条必须包含四元组：
    1. 陈述（Insight Statement）：洞察的核心观点
    2. 证据（Evidence）：引用哪些事实编号（Fxx）支撑
    3. 反常识（Counter-intuitive）：为什么这个洞察反直觉或容易被忽略
    4. 下次行动（Actionable Next Step）：基于洞察应该做什么
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `human-judgement` TR-2.1: 每条洞察完整包含四元组四要素，无缺失
  - `human-judgement` TR-2.2: 洞察有深度，不是事实的简单复述，揭示了设计trade-off
  - `human-judgement` TR-2.3: 反常识部分确实揭示了容易被忽略的设计取舍
- **Notes**: 洞察必须可证伪；避免"awesome-okf设计得很好"这类无信息量评价

## [ ] Task 3: E阶段 - 模式萃取（Extraction）
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 从Task 2的洞察中萃取可复用模式，目标1-2个高质量模式
  - 候选模式方向：
    1. **零依赖CLI聚合模式**：myokf-cli如何用纯标准库+子命令分发实现7个工具的统一入口（参考plugins/myokf-cli/src/myokf/cli.py）
    2. **Skill+Producer双层架构模式**：工具层（Python脚本，确定性执行）与Skill层（Markdown工作流，指导Agent行为）如何分工协作
    3. **向后兼容规范扩展模式**：如何在不修改上游MUST的前提下，通过可选frontmatter字段实现规范扩展（参考i18n的lang/canonical设计）
    4. **Dogfooding自举验证模式**：项目自身如何作为规范的合规范例，实现"用自己规范写自己"
  - 每个模式文档必须包含：
    - TOML frontmatter（id/domain/layer/maturity/validation_count/reuse_count等）
    - 触发场景（When to use）
    - 核心步骤/结构（How it works），配合awesome-okf中的具体代码/文件示例
    - 反模式（What not to do）
    - 迁移验证（Migration validation）：给出在SpecWeave中的具体应用场景（如迁移到.agents/scripts/或.agents/skills/）
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `human-judgement` TR-3.1: 模式包含完整的TOML frontmatter字段
  - `human-judgement` TR-3.2: 模式明确说明触发场景和反模式
  - `human-judgement` TR-3.3: 迁移验证给出SpecWeave中的具体应用示例，不是空泛描述
- **Notes**: 模式抽象层级要合适——不能太具体（只适用于OKF）也不能太抽象（变成空话）

## [ ] Task 4: V阶段 - 对抗性审查（Adversarial Review）
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 组织四视角对抗审查，对Task 2的洞察和Task 3的模式进行攻击：
    1. 🔴 **魔鬼代言人（Devil's Advocate）**：逻辑攻击——找逻辑漏洞、因果跳跃、证据不足、过度泛化
    2. 🔵 **新手开发者（Novice Developer）**：可读性攻击——找术语未解释、步骤跳步、理解门槛、缺少具体示例
    3. 🟡 **成本敏感CTO（Cost-sensitive CTO）**：ROI攻击——找投入产出比不合理、过度工程、维护成本被低估、"学这个模式值不值"
    4. 🟢 **学术研究员（Academic Researcher）**：准确性攻击——找定义不严谨、边界未声明、v0.1/v0.2版本差异未处理、对比不公平
  - 硬指标：每个视角≥2条具体意见，总计≥10条；禁止"写得很好""很有启发"这类客套话
  - 对审查意见进行分类处理并记录回应：🔴关键问题100%修正；🟡次要问题≥30%修正；🟢观察性问题记录即可
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `human-judgement` TR-4.1: 四视角各产出≥2条具体审查意见，总计≥10条
  - `human-judgement` TR-4.2: 无"写得很好"类无信息量客套意见
  - `human-judgement` TR-4.3: 🔴关键问题100%修正，🟡次要问题≥30%修正
  - `human-judgement` TR-4.4: 每条审查意见有回应记录（采纳/部分采纳/不采纳+理由）
- **Notes**: 审查要具体到段落/句子/模式要素，不能泛泛而谈

## [ ] Task 5: A阶段 - 原子行动项（Atomization）
- **Priority**: medium
- **Depends On**: Task 4
- **Description**: 
  - 将Task 2洞察中的"下次行动"部分拆解为原子行动项，目标3-5个
  - 每个行动项必须符合5项原子标准：
    1. **单一职责**：只做一件事
    2. **可验证**：有明确的"完成"定义
    3. **有Owner**：明确负责角色
    4. **有时间**：预估完成时间
    5. **可独立交付**：不依赖其他未完成项
  - 行动项方向建议（基于awesome-okf的可迁移模式）：
    - 评估零依赖CLI聚合模式在.agents/scripts/中的适用性
    - 评估为.agents/skills/建立dogfooding自举验证机制
    - 研究向后兼容规范扩展模式在MDI规范演进中的应用
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `human-judgement` TR-5.1: 行动项数量3-5个
  - `human-judgement` TR-5.2: 每项符合5项原子标准
  - `human-judgement` TR-5.3: 行动项与洞察有明确对应关系
- **Notes**: 行动项不要求立即执行，作为知识沉淀的落地钩子

## [ ] Task 6: 双向链接建立
- **Priority**: high
- **Depends On**: Task 5
- **Description**: 
  - 报告内链接：在分析报告中，OKF通用概念（如frontmatter、Bundle、Concept、index.md/log.md保留文件）使用相对路径链接到okf-wiki对应章节
  - okf-wiki反向链接：
    1. 在 [07-resources-and-glossary.md](file:///d:/AI/.agents/docs/knowledge/learning/01-agent-protocols-interfaces/okf-wiki/07-resources-and-glossary.md) 的"7.5 本项目相关Wiki交叉引用"表格中添加awesome-okf深度分析的条目
    2. 在 [README.md](file:///d:/AI/.agents/docs/knowledge/learning/01-agent-protocols-interfaces/okf-wiki/README.md) 的"🔗 相关资源"区添加本报告链接
  - 创建报告目录：`.agents/docs/knowledge/learning/01-agent-protocols-interfaces/okf-wiki/awesome-okf-analysis/`
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-6.1: 运行链接检查脚本，所有双向链接可达
  - `human-judgement` TR-6.2: 报告→okf-wiki的链接语义正确（通用概念链到正确章节）
  - `human-judgement` TR-6.3: okf-wiki→报告的链接在README和07-resources中都有添加
- **Notes**: 使用相对路径链接，格式参考okf-wiki中现有交叉引用风格

## [ ] Task 7: 产出物整理与合规检查
- **Priority**: medium
- **Depends On**: Task 6
- **Description**: 
  - 将所有阶段产出物整理为结构化分析报告，存放于`okf-wiki/awesome-okf-analysis/`：
    - `README.md` — 执行摘要与导航
    - `01-facts.md` — R阶段事实清单（≥20条，编号Fxx）
    - `02-insights.md` — I阶段核心洞察（≥3条，四元组格式）
    - `03-patterns.md` — E阶段模式萃取（1-2个模式，TOML frontmatter）
    - `04-adversarial-review.md` — V阶段对抗审查记录（四视角意见+修正回应）
    - `05-action-items.md` — A阶段原子行动项（3-5个）
  - 执行合规检查：
    1. 文件名规范检查（kebab-case、纯英文）
    2. frontmatter检查（YAML格式、必要字段与okf-wiki风格一致）
    3. 路径引用检查（相对路径，无file:///绝对路径）
    4. 链接有效性检查
    5. 内容非重复检查（不重复okf-wiki已有内容）
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-7.1: 运行文件名规范检查脚本无错误
  - `human-judgement` TR-7.2: 所有.md文件有正确的YAML frontmatter，风格与okf-wiki一致
  - `human-judgement` TR-7.3: 路径引用使用相对路径
  - `human-judgement` TR-7.4: 报告6个文件结构完整
  - `human-judgement` TR-7.5: 内容聚焦awesome-okf深度分析，不重复okf-wiki通用教程
- **Notes**: 报告语言为中文；frontmatter字段参考okf-wiki现有文档（id/title/version/source/type/description/tags/category/date等）
