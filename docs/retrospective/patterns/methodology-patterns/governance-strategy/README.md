---
id: "docs-retrospective-patterns-methodology-patterns-governance-strategy-index"
title: "治理策略模式"
category: "retrospective"
date: "2026-07-09"
---

# 治理策略模式

> 本目录 README 由 `generate-readme.py` 自动生成，可根据需要补充概述和导航说明。

<!-- README_INDEX_START -->

## 📄 文档索引

| 文档 | 说明 | 成熟度 | 标签 |
|------|------|--------|------|
| [两栖定位模型（Amphibious Positioning Model）](amphibious-positioning-model.md) | 两栖定位模型（Amphibious Positioning Model） | L1 |  |
| [可得性启发结构性防范模式（Availability Heuristic Structural Guard）](availability-heuristic-structural-guard.md) | 可得性启发结构性防范模式（Availability Heuristic Structural Guard） | L1 |  |
| [规范自举性驱动持续演化](bootstrap-driven-self-evolution.md) | 规范自举性驱动持续演化 | L2 | `meta-methodology` `lifecycle` `bootstrap` |
| [瓶颈优先重构法：按全局瓶颈而非实施难度排序重构优先级](bottleneck-first-refactoring.md) | 瓶颈优先重构法：按全局瓶颈而非实施难度排序重构优先级 | L2 |  |
| [章节类型分层文件大小策略](chapter-type-tiered-file-size.md) | 章节类型分层文件大小策略 | L1 |  |
| [指令集↔知识库关联对应性前提（Command-Knowledge Link Pattern）](command-knowledge-link.md) | 指令集↔知识库关联对应性前提（Command-Knowledge Link Pattern） | L2 |  |
| [提交质量门——三查暂存法（Commit Quality Gate: Three-Check Staging Inspection）](commit-quality-gate-staging-inspection.md) | 提交质量门——三查暂存法（Commit Quality Gate: Three-Check Staging Inspection） | L2 |  |
| [合规驱动规则建设五步法](compliance-driven-rule-building.md) | 合规驱动规则建设五步法 | L1 |  |
| [约定驱动创建模型：范例即模板](convention-driven-creation.md) | 约定驱动创建模型：范例即模板 | L2 |  |
| [跨Wiki引用目录优先验证模式](cross-wiki-reference-directory-first.md) | 跨Wiki引用目录优先验证模式 | L2 |  |
| [量化数据验证四查法](data-validation-four-checks.md) | 量化数据验证四查法 | L2 | `data-validation` `documentation` `drift-detection` |
| [开发环境 Dockerfile 优化法：优先排序而非最小化](dev-env-dockerfile-optimization.md) | 开发环境 Dockerfile 优化法：优先排序而非最小化 | L1 |  |
| [双模式子模块治理框架：分类管理 Git Submodule](dual-mode-submodule-governance.md) | 双模式子模块治理框架：分类管理 Git Submodule | L2 |  |
| [子代理双重质量门模式（事前约束+事后校验）](dual-quality-gate-subagent.md) | 子代理双重质量门模式（事前约束+事后校验） | L2 |  |
| [重复代码利息模型：复制一时爽，维护火葬场](duplication-interest-model.md) | 重复代码有利息成本：复制时节省几秒钟本金，但每次修改需同步改所有副本付利息，遗漏副本导致bug付违约金。维护成本与需要同步修改的位置数量成正比。决策矩阵：重复2次+逻辑可能变→应该提取；重复≥3次→必须提取。 | L1 | `重复代码` `DRY` `技术债务` |
| [弹性流程分级：按变更风险选择流程路径](elastic-workflow-classification.md) | 弹性流程分级：按变更风险选择流程路径 | L2 |  |
| [豁免机制合法化](exemption-mechanism-legalization.md) | 豁免机制合法化 | L2 | `exemption` `governance` `legalization` |
| [用户反馈措辞诊断模式（Feedback Wording Diagnosis）](feedback-wording-diagnosis.md) | 用户反馈措辞诊断模式（Feedback Wording Diagnosis） | L1 |  |
| [文件创建前置检查模式（File Creation Precheck Pattern）](file-creation-precheck-pattern.md) | 文件创建前置检查模式（File Creation Precheck Pattern） | L3 |  |
| [五层治理体系架构模式](five-layer-governance-architecture.md) | 五层治理体系架构模式 | L2 |  |
| [格式证据优先于记忆模式（Format Evidence Over Memory Pattern）](format-evidence-over-memory-pattern.md) | 格式证据优先于记忆模式（Format Evidence Over Memory Pattern） | L2 |  |
| [外部依赖四不原则](four-negatives-external-dependency.md) | 外部依赖四不原则 | L3 | `governance` `external-dependency` `vendor` |
| [治理基建四层递进模型](governance-four-layer-progressive.md) | 治理基建四层递进模型 | L2 |  |
| [治理演化三阶段：修复→预防→闭环](governance-three-stage-evolution.md) | 治理演化三阶段：修复→预防→闭环 | L2 | `meta-methodology` `governance` `quality` |
| [治理层级优先级排序法（Governance Tier Priority）](governance-tier-priority.md) | 治理层级优先级排序法（Governance Tier Priority） | L1 |  |
| [不可变约束清单模式：踩坑经验的工程化沉淀](immutable-constraint-documentation.md) | 每一条都对应过真实的失败现场，**禁止凭印象撤销**。 | - |  |
| [Learn-Validate-Adopt：外部标准采用三步法](learn-validate-adopt.md) | Learn-Validate-Adopt：外部标准采用三步法 | L1 |  |
| [元复盘闭环：交付后主动自我审查的完整改进循环](meta-retrospective-closed-loop.md) | 元复盘闭环：交付后主动自我审查的完整改进循环 | L1 | `meta-retrospective` `closed-loop` `self-correction` |
| [方法论构造性验证](methodology-constructive-validation.md) | 方法论构造性验证 | L1 |  |
| [模块大小-Bug密度非线性相关模式（Module Size-Bug Density Correlation）](module-size-bug-correlation.md) | 模块大小-Bug密度非线性相关模式（Module Size-Bug Density Correlation） | - |  |
| [MVP未验证代码债务模式（MVP Unvalidated Code Debt）](mvp-unvalidated-code-debt.md) | MVP未验证代码债务模式（MVP Unvalidated Code Debt） | - |  |
| [不重构清单：明确划定不改动边界防止范围蔓延](no-touch-list.md) | 不重构清单：明确划定不改动边界防止范围蔓延 | L2 |  |
| [协议违规非线性纠偏成本模式（Nonlinear Correction Cost for Protocol Violations）](nonlinear-correction-cost.md) | 协议违规非线性纠偏成本模式（Nonlinear Correction Cost for Protocol Violations） | L1 |  |
| [模式渐进式工具提取：L1实验阶段即可提取轻量工具](pattern-tooling-progressive-extraction.md) | 模式渐进式工具提取：L1实验阶段即可提取轻量工具 | L1 | `pattern-tooling` `progressive-extraction` `checklist` |
| [方法论推广渐进式验证模式](phased-rollout-validation.md) | 方法论推广渐进式验证模式 | L2 |  |
| [流程合规 vs 经验直觉区分模式（Process Compliance vs Experience Intuition）](process-vs-experience-intuition.md) | 流程合规 vs 经验直觉区分模式（Process Compliance vs Experience Intuition） | L2 |  |
| [递进式需求澄清：先定范围、再定细节](progressive-requirement-clarification.md) | 递进式需求澄清：先定范围、再定细节 | L2 |  |
| [证明有用性自检模式](prove-usefulness-check.md) | 证明有用性自检模式 | L2 |  |
| [引用即触发（Reference-as-Trigger）协作模式](reference-as-trigger.md) | 引用即触发（Reference-as-Trigger）协作模式 | L2 |  |
| [角色最小化原则（RACI扩展优先于角色新增）](role-minimization-principle.md) | 角色最小化原则（RACI扩展优先于角色新增） | L1 |  |
| [根因诊断模式](root-cause-diagnosis.md) | 根因诊断模式 | L2 |  |
| [自指性规范体系（Self-Referential Specification System）](self-referential-spec-system.md) | 自指性规范体系（Self-Referential Specification System） | L1 |  |
| [原子提交会话边界原则（Session-Boundary-Commit）](session-boundary-commit.md) | 原子提交会话边界原则（Session-Boundary-Commit） | L1 |  |
| [短指令模式](short-command-patterns.md) | 短指令模式 | L2 |  |
| [规范可发现性保障模式（Spec Discoverability Guarantee）](spec-discoverability-guarantee.md) | 规范可发现性保障模式（Spec Discoverability Guarantee） | L1 |  |
| [规范层纵深防御模型：安全设计前置](spec-level-defense-in-depth.md) | 规范层纵深防御模型：安全设计前置 | L2 |  |
| [Spec引用验证通用原则（Specification Reference Validation Pattern）](spec-reference-validation.md) | Spec引用验证通用原则（Specification Reference Validation Pattern） | L2 |  |
| [规范三同步原则：新规范落地必须完成的三个同步动作](spec-triple-sync.md) | 新规范发布后必须立即完成三个同步动作：①顶层开发规范引用 ②导航入口更新 ③存量迁移示范，三个动作缺一不可，解决"规范悬空"问题——规范写了但没人看、看到了不会用、想用但没示例 | L2 | `规范落地` `治理策略` `文档索引` |
| [结构阅读先行（Structure-First Extension）](structure-first-extension.md) | 结构阅读先行（Structure-First Extension） | L3 |  |
| [任务类型优先索引模式（Task-Type-First Indexing）](task-type-first-indexing.md) | 任务类型优先索引模式（Task-Type-First Indexing） | L1 |  |
| [测试覆盖率边际收益递减拐点](test-coverage-diminishing-returns.md) | 测试覆盖率边际收益递减拐点 | L1 |  |
| [规则落地三层模型：定义+痕迹+验证](three-layer-rule-enforcement.md) | 规则落地三层模型：定义+痕迹+验证 | L2 |  |
| [规范约束三层次模型（Three-Layer Spec Constraint Model）](three-layer-spec-constraint.md) | 规范约束三层次模型（Three-Layer Spec Constraint Model） | L2 |  |
| [问题解决三层跃迁范式（Three-Level Problem Solving Paradigm）](three-level-problem-solving.md) | 问题解决三层跃迁范式（Three-Level Problem Solving Paradigm） | L1 |  |
| [三段式内容验证模式：任务级→专项→终验](three-stage-content-validation.md) | 三段式内容验证模式：任务级→专项→终验 | L1 |  |
| [三层看板体系：看-管-建全生命周期覆盖](three-tier-board-system.md) | 三层看板体系：看-管-建全生命周期覆盖 | L1 |  |
| [三层治理模型：原子化→自动化→验证](three-tier-governance.md) | 三层治理模型：原子化→自动化→验证 | L3 | `governance` `quality` `three-tier` |
| [三区域边界模型](three-zone-boundary-model.md) | 三区域边界模型 | L2 | `governance` `external-dependency` `boundary` |
| [工具链项目五阶段演进路径](toolchain-five-stage-evolution.md) | 工具链项目五阶段演进路径 | L1 |  |
| [三角困境→架构级解决框架](trilemma-architectural-resolution.md) | 三角困境→架构级解决框架 | L1 | `三角困境` `架构级突破` `困境突破` |
| [文档治理双维度检查模型（Two-Dimension Document Governance Model）](two-dimension-document-governance.md) | 文档治理双维度检查模型（Two-Dimension Document Governance Model） | L2 |  |
| [两阶段开发模式（Two-Phase Development: Validate First, Optimize Later）](two-phase-development.md) | 两阶段开发模式（Two-Phase Development: Validate First, Optimize Later） | - |  |
| [第三方供应商全生命周期治理模型](vendor-lifecycle-governance.md) | 第三方供应商全生命周期治理模型 | L1 |  |
| [Wiki双轨Frontmatter规范模式](wiki-dual-track-frontmatter.md) | Wiki双轨Frontmatter规范模式 | L1 |  |
| [Wiki创作三查流程模式（Wiki Pre-Creation Three Checks Pattern）](wiki-pre-creation-three-checks.md) | Wiki创作三查流程模式（Wiki Pre-Creation Three Checks Pattern） | L3 |  |


<!-- README_INDEX_END -->

## 🔗 相关资源

- [🏠 返回上级：方法论模式](../README.md)
- [📚 文档首页](../../../../README.md)

---

<!-- generated by generate-readme.py on 2026-07-10 -->
