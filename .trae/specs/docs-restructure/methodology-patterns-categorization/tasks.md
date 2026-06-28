# 方法论模式主题分类整理 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 创建主题子目录并完成文件移动分类
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 在 methodology-patterns/ 下创建7个主题子目录
  - 按照预先定义的分类清单，将94个模式文件移动到对应子目录
  - 使用PowerShell的Move-Item命令完成移动，确保Git可识别为重命名
  - 分类清单如下（总计94个文件）：
  
  **1. retrospective-knowledge/（复盘与知识生命周期）- 21个文件**
  - actionable-suggestion-five-elements.md
  - closed-loop-pdca-mapping.md
  - counterfactual-debt-analysis.md
  - experience-transfer-mapping.md
  - export-four-channel-progressive.md
  - extraction-four-layer-funnel.md
  - five-category-asset-coverage.md
  - insight-iceberg-model.md
  - insight-library-evolution.md
  - insight-two-tier-structure.md
  - methodology-critical-mass.md
  - methodology-five-level-maturity.md
  - multi-source-intelligence-iteration.md
  - report-as-tracking.md
  - retrospective-acceleration-effect.md
  - retrospective-four-step-method.md
  - review-insight-export-loop.md
  - rolling-retro-eight-steps.md
  - suggestion-priority-driven-execution.md
  - three-part-retrospective.md
  - three-tier-knowledge-sedimentation.md
  
  **2. document-architecture/（文档架构与原子化）- 21个文件**
  - atomization-three-criteria-test.md
  - atomization-three-tier-classification.md
  - content-migration-workflow.md
  - document-entropy-three-strategies.md
  - document-system-refactoring.md
  - dual-audience-extraction-model.md
  - entry-container-separation.md
  - fact-statement-consistency-loop.md
  - i18n-anchor-page-strategy.md
  - large-scale-duplication-elimination.md
  - link-decay-laws.md
  - meta-document-leverage.md
  - modularization-interface-design.md
  - mermaid-layered-visualization.md
  - pattern-merge-boundary.md
  - post-atomization-content-merge-back.md
  - progressive-readme-growth.md
  - scripted-batch-correction.md
  - source-document-downgrade.md
  - synthetic-stats-source-of-truth.md
  - two-phase-processing.md
  
  **3. tools-automation/（工具工程与自动化）- 15个文件**
  - auto-generate-threshold.md
  - best-practice-hidden-cost.md
  - capability-matrix.md
  - diff-driven-refactoring.md
  - dry-run-first.md
  - explicit-maturity-tracking.md
  - package-structure-leverage.md
  - path-discipline.md
  - precision-over-recall.md
  - refactoring-hidden-bug-discovery.md
  - search-replace-fragility.md
  - tool-automation-decision-model.md
  - tool-bootstrap-effect.md
  - tool-workflow-composition.md
  - toolchain-maturity.md
  
  **4. governance-strategy/（治理与优先级策略）- 14个文件**
  - amphibious-positioning-model.md
  - convention-driven-creation.md
  - governance-tier-priority.md
  - progressive-requirement-clarification.md
  - prove-usefulness-check.md
  - reference-as-trigger.md
  - root-cause-diagnosis.md
  - self-referential-spec-system.md
  - short-command-patterns.md
  - spec-level-defense-in-depth.md
  - structure-first-extension.md
  - three-level-problem-solving.md
  - three-tier-board-system.md
  - three-tier-governance.md
  
  **5. ai-collaboration/（AI协作与提示词设计）- 9个文件**
  - ai-skill-judgment-layer.md
  - bilingual-prompt-engineering.md
  - dual-zone-development-model.md
  - output-behavior-specification.md
  - progressive-context-disclosure.md
  - progressive-templating.md
  - skill-three-layer-value-model.md
  - style-creativity-separation-control.md
  - symptom-prescription-qa.md
  
  **6. creative-design/（创意与设计原则）- 7个文件**
  - character-driven-design-system.md
  - cognitive-anchor-visualization.md
  - constraint-driven-creativity.md
  - intentional-friction-design.md
  - programmable-creativity-algorithm.md
  - spec-driven-development.md
  - visual-atomization-principle.md
  
  **7. product-growth/（产品开发与竞争策略）- 7个文件**
  - contest-funnel-aperture.md
  - contest-growth-flywheel.md
  - controlled-uncontrollable-ugc-rules.md
  - positioning-drift-correction.md
  - spec-nine-section-narrative.md
  - three-layer-delivery-pipeline.md
  - zero-sum-rule-inversion.md
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-9
- **Test Requirements**:
  - `programmatic` TR-1.1: 7个主题子目录全部创建成功，名称符合kebab-case
  - `programmatic` TR-1.2: 7个子目录中.md文件数量之和等于94（不含README.md）
  - `programmatic` TR-1.3: 根目录下除README.md外无其他散落的模式文件
  - `programmatic` TR-1.4: 抽查5个模式文件，确认其frontmatter元数据完整
- **Notes**: 移动前先确认文件清单准确，避免移动错误

## [x] Task 2: 创建CATEGORIES.md主题划分说明文档
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 在methodology-patterns/根目录创建CATEGORIES.md
  - 文档包含：分类原则、7个主题的详细定义（名称、中文描述、核心关注点、边界说明）、每个主题下的完整模式列表（带链接和一句话说明）
  - 模式说明从原README的表格中提取，保持简洁
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `human-judgement` TR-2.1: CATEGORIES.md结构清晰，包含分类原则和7个主题章节
  - `programmatic` TR-2.2: 每个主题下列出的文件数与实际目录中的文件数一致
  - `programmatic` TR-2.3: 所有文件链接使用正确的相对路径（指向子目录中的文件）
- **Notes**: 文档开头说明分类基于核心主题思想，而非成熟度或来源

## [x] Task 3: 重写methodology-patterns/README.md为主题导航索引
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Description**: 
  - 更新README.md，保留模式库介绍、成熟度定义
  - 将原来的长表格替换为7个主题的导航卡片/表格，每个主题显示：名称、中文描述、模式数量、链接到CATEGORIES.md的对应锚点
  - 保留使用指南，但更新其中的链接路径
  - 简化Mermaid关系图，改为展示主题之间的关系而非单个模式
  - 移除原有的单模式长列表，避免重复维护
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `human-judgement` TR-3.1: README结构清晰，主题导航一目了然
  - `programmatic` TR-3.2: 所有主题描述链接正确指向CATEGORIES.md对应章节
  - `programmatic` TR-3.3: 成熟度定义和使用指南保留完整
- **Notes**: 遵循"入口文档精简"原则，详细列表在CATEGORIES.md中维护

## [x] Task 4: 修复所有内部链接引用
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 3
- **Description**: 
  - 运行链接检查工具：`python .agents/scripts/check-links.py --path docs/retrospective/patterns/methodology-patterns --fix`
  - 自动修复因文件移动导致的相对路径错误
  - 手动检查并修复README.md中Mermaid图内标注的文件名引用（不影响链接但影响可读性）
  - 检查模式文件之间的交叉引用（如果有）
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-4.1: 运行check-links.py后输出显示0 errors, 0 warnings
  - `programmatic` TR-4.2: CATEGORIES.md中的所有链接可正常访问
  - `programmatic` TR-4.3: README.md中的所有内部链接可正常访问
- **Notes**: 使用--fix参数自动修复大部分相对路径问题

## [x] Task 5: 更新上层文档引用
- **Priority**: medium
- **Depends On**: Task 4
- **Description**: 
  - 更新docs/retrospective/patterns/README.md：
    - 更新目录结构表格中的路径说明
    - 更新模式统计数字（确认总数为94）
    - 更新"使用方式"章节中指向具体模式的链接（如有）
  - 更新docs/retrospective/README.md：
    - 更新methodology-patterns下列举的模式文件路径
    - 更新目录树图示
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-5.1: patterns/README.md中所有指向methodology-patterns的链接正确
  - `programmatic` TR-5.2: docs/retrospective/README.md中目录树正确反映新结构
  - `programmatic` TR-5.3: 运行check-links.py --path docs/retrospective/patterns无断链
- **Notes**: 注意patterns/README.md中统计数字需要更新为94

## [x] Task 6: 全量链接验证与收尾
- **Priority**: medium
- **Depends On**: Task 5
- **Description**: 
  - 运行finalize-atomization.py完成原子化收尾：导航更新、看板刷新
  - 运行全量链接检查：`python .agents/scripts/check-links.py --path docs/retrospective`
  - 检查整个docs/目录下是否有其他文件引用了旧路径（使用grep搜索）
  - 验证所有模式文件的frontmatter中source字段路径（如需要更新则更新）
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `programmatic` TR-6.1: docs/retrospective目录下所有链接检查通过，0断链
  - `programmatic` TR-6.2: 整个项目中搜索旧路径（methodology-patterns/xxx.md直接在根目录）无遗漏引用
  - `programmatic` TR-6.3: 最终文件计数确认：94个模式文件 + README.md + CATEGORIES.md = 96个文件在methodology-patterns目录树中
- **Notes**: 这是最终验证步骤，必须确保所有引用都正确
