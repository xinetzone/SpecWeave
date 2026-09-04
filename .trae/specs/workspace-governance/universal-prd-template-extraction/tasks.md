# 通用PRD/项目Spec模板萃取 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 0: 参考Spec深度解构与第一性原理分析
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 逐章逐节解析first-principles-comprehensive-research/spec.md
  - 应用第一性原理追问每个章节的核心目的（"为什么需要这个章节？没有它会出什么问题？"）
  - 区分本质要素（所有项目通用）vs 项目特定要素（仅适用于该研究项目）
  - 分析Spec演进轨迹（v1.0→v1.1新增了FR-9/FR-10，追踪了commits和patterns，这些是本质要素还是特定要素？）
  - 识别优秀设计决策和可改进点
  - 输出至模板归档目录下的deconstruction-analysis.md
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `human-judgement` TR-0.1: 解构分析覆盖参考Spec的所有章节（frontmatter + 10个正文章节）
  - `human-judgement` TR-0.2: 每个章节都有"核心功能"分析（回答"为什么存在"）
  - `human-judgement` TR-0.3: 明确区分至少10个本质要素和5个项目特定要素
  - `human-judgement` TR-0.4: 识别至少5个优秀设计决策和2个可改进点
  - `programmatic` TR-0.5: deconstruction-analysis.md文件存在，YAML frontmatter正确，单文件不超过500行
- **Notes**: 这是整个项目的基础——后续所有模板设计都基于这次解构分析的结论，必须扎实

## [x] Task 1: YAML frontmatter元数据规范设计
- **Priority**: high
- **Depends On**: [Task 0]
- **Description**: 
  - 基于解构分析结果，提炼必填和推荐元数据字段
  - 定义每个字段的含义、取值规范、填写时机
  - 设计status字段的生命周期状态机
  - 参考其他已完成项目的Spec，验证字段的普适性
  - 输出frontmatter-specification.md
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `programmatic` TR-1.1: 明确定义必填字段（6-8个）和推荐字段（不超过10个）
  - `human-judgement` TR-1.2: 每个字段有清晰的含义说明和填写时机（规划时/执行中/完成后）
  - `human-judgement` TR-1.3: status状态机覆盖完整项目生命周期（candidate→planning→in-progress→completed→archived）
  - `programmatic` TR-1.4: frontmatter-specification.md符合文件规范
- **Notes**: 元数据是项目可追踪性的基础，不要贪多——只保留真正有用的字段

## [x] Task 2: PRD正文结构与章节指南编写
- **Priority**: high
- **Depends On**: [Task 0]
- **Description**: 
  - 定义每个核心章节的目的、必填要素、写作要求
  - 为关键章节编写正反示例
  - 为每个章节设计检查要点
  - 明确FR/NFR/AC之间的追溯关系
  - 输出prd-structure-guide.md
- **Acceptance Criteria Addressed**: [AC-3]
- **Test Requirements**:
  - `programmatic` TR-2.1: 覆盖所有10个核心章节（Overview/Goals/Non-Goals/Background/FR/NFR/Constraints/Assumptions/AC/Open Questions）
  - `human-judgement` TR-2.2: 每个章节都有核心目的说明和必填要素清单
  - `human-judgement` TR-2.3: 至少5个章节有正反示例对比（好的写法vs不好的写法）
  - `human-judgement` TR-2.4: 每个章节有明确的检查要点（用于自检）
  - `programmatic` TR-2.5: prd-structure-guide.md符合文件规范
- **Notes**: 这是模板的核心——指南必须足够具体，让不同人写出来的Spec结构一致、质量可靠

## [x] Task 3: Spec格式选择决策框架与最佳实践编写
- **Priority**: medium
- **Depends On**: [Task 2]
- **Description**: 
  - 明确PRD Spec vs Change Spec的适用场景边界
  - 设计简单易用的格式选择决策树
  - 收集整理Spec写作常见陷阱和应对方法
  - 编写质量自检清单
  - 关联已有相关模式
  - 输出format-selection-guide.md和best-practices.md
- **Acceptance Criteria Addressed**: [AC-4, AC-5]
- **Test Requirements**:
  - `human-judgement` TR-3.1: 决策树包含至少3个判断维度，5个测试场景能得出明确结论
  - `human-judgement` TR-3.2: 列出至少8个常见陷阱，每个陷阱有反面示例和正确做法
  - `human-judgement` TR-3.3: 质量自检清单包含10-15个检查项
  - `human-judgement` TR-3.4: 引用至少3个已有相关模式（如spec-nine-section-narrative、spec-reference-validation等）
  - `programmatic` TR-3.5: 两个输出文件均符合文件规范
- **Notes**: 格式选择不搞"一刀切"——两种格式各有适用场景，关键是帮助用户快速选对

## [x] Task 4: 通用PRD模板文件生成
- **Priority**: high
- **Depends On**: [Task 1, Task 2]
- **Description**: 
  - 基于元数据规范和正文结构指南，生成可直接复制使用的空白模板
  - 模板中包含清晰的填写提示和注释
  - 确保模板本身简洁（核心内容<200行）
  - 输出universal-prd-template.md至spec-workflow模式目录
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `programmatic` TR-4.1: 模板包含所有必填frontmatter字段和核心正文章节
  - `human-judgement` TR-4.2: 填写提示清晰，不会产生歧义
  - `programmatic` TR-4.3: 模板核心内容（不含注释和示例）不超过200行
  - `programmatic` TR-4.4: 文件名符合kebab-case规范，YAML frontmatter格式正确
  - `programmatic` TR-4.5: 文件归档至正确位置（docs/retrospective/patterns/methodology-patterns/spec-workflow/）
- **Notes**: 模板要"开箱即用"——用户复制过去就能开始填写，不需要再猜每个部分写什么

## [x] Task 5: 整合至现有规范体系
- **Priority**: medium
- **Depends On**: [Task 3, Task 4]
- **Description**: 
  - 更新.agents/rules/spec-writing-guide/，新增PRD模板相关章节
  - 为spec-workflow模式目录创建/更新README索引
  - 在模板和现有规范之间建立双向导航链接
  - 验证所有链接有效
  - 确保不破坏现有Change Spec格式的规范
- **Acceptance Criteria Addressed**: [AC-7]
- **Test Requirements**:
  - `programmatic` TR-5.1: spec-writing-guide已更新，包含PRD模板介绍和格式选择决策框架
  - `programmatic` TR-5.2: spec-workflow目录有README索引文件
  - `programmatic` TR-5.3: 所有内部链接通过check-links验证无断链
  - `human-judgement` TR-5.4: 现有Change Spec格式的规范内容完整保留，未被破坏
- **Notes**: 整合是关键——新模板不能成为"孤儿文档"，必须融入现有规范体系才能被真正采用

## [x] Task 6: Dogfooding自验证与模板优化
- **Priority**: high
- **Depends On**: [Task 4, Task 5]
- **Description**: 
  - 使用新模板重新审视本项目的Spec
  - 检查本项目Spec是否符合新模板的所有要求
  - 识别模板中缺失或不合理的要素
  - 根据验证结果迭代优化模板
  - 记录Dogfooding过程和发现的问题
- **Acceptance Criteria Addressed**: [AC-8]
- **Test Requirements**:
  - `human-judgement` TR-6.1: 完成本项目Spec与新模板的对照检查
  - `human-judgement` TR-6.2: 所有发现的问题都已记录，合理的改进已纳入模板
  - `human-judgement` TR-6.3: Dogfooding验证过程有明确记录（在复盘中体现）
- **Notes**: Dogfooding是最好的验证——如果模板连我们自己用着都别扭，那肯定有问题

## [x] Task 7: 文件规范检查与链接验证
- **Priority**: medium
- **Depends On**: [Task 5, Task 6]
- **Description**: 
  - 运行文件名规范检查
  - 运行frontmatter格式检查
  - 运行所有链接有效性检查
  - 运行单文件行数检查
  - 修复所有检查发现的问题
- **Acceptance Criteria Addressed**: [AC-9]
- **Test Requirements**:
  - `programmatic` TR-7.1: python .agents/scripts/check-filename-convention.py通过
  - `programmatic` TR-7.2: python .agents/scripts/check-frontmatter.py通过
  - `programmatic` TR-7.3: python .agents/scripts/check-links.py --path <output-dir>通过
  - `programmatic` TR-7.4: 所有单文件不超过500行
- **Notes**: 作为规范类项目，自身必须100%符合规范——这是最低要求

## [x] Task 8: 项目复盘与模式沉淀
- **Priority**: medium
- **Depends On**: [Task 7]
- **Description**: 
  - 对本项目执行过程进行复盘
  - 萃取过程中发现的新模式或洞察
  - 更新所有文档状态为completed
  - 补充frontmatter元数据（completed_at、key_commits等）
  - 准备原子提交
- **Acceptance Criteria Addressed**: [AC-8]
- **Test Requirements**:
  - `human-judgement` TR-8.1: 完成项目复盘，包含执行过程总结、问题记录、经验萃取
  - `programmatic` TR-8.2: 所有文档frontmatter元数据更新完整（status: completed, completed_at等）
  - `human-judgement` TR-8.3: 识别并记录至少1个新的方法论洞察（如果有）
- **Notes**: 用第一性原理做模板，也要用我们自己的复盘方法论做复盘——知行合一
