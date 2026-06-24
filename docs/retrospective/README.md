# 复盘文档体系

> 本目录存放项目复盘分析报告、可复用的知识资产、方法论、模板与决策框架，以模块化、结构化的方式组织，便于查阅与维护。

## 目录树

```
docs/retrospective/
├── README.md                          ← 目录索引与模块说明
├── prompt-extraction.md               ← 提示词工程可迁移模式、模板与方法论
├── templates/                         ← 可复用模板
│   ├── spec-template.md               · spec.md 规格文档模板
│   ├── tasks-template.md              · tasks.md 任务清单模板
│   ├── checklist-template.md          · checklist.md 检查清单模板
│   ├── retrospective-report-template.md · 复盘报告模板
│   └── directory-readme-template.md    · 目录索引 README 模板
├── patterns/                          ← 可复用模式
│   ├── code-patterns/                 ← 代码模式
│   │   ├── three-tier-check-tool.md   · 三段式检查工具架构
│   │   ├── context-aware-path-resolution.md · 上下文感知路径解析
│   │   ├── meta-document-detection.md · 元文档识别
│   │   ├── gitignore-validation.md    · Git 忽略规则验证
│   │   └── regex-markdown-parsing.md  · 正则驱动的 Markdown 解析
│   ├── architecture-patterns/         ← 架构模式
│   │   ├── perception-check-report-model.md · 感知→检查→报告三层模型
│   │   ├── multi-agent-parallel-execution.md · 多智能体并行执行模式
│   │   └── incremental-regression-verification.md · 增量验证+回归验证双层策略
│   └── methodology-patterns/          ← 方法论模式
│       ├── README.md                   · 方法论模式索引
│       ├── spec-driven-development.md · Spec-driven 开发流程
│       ├── review-insight-export-loop.md · 复盘→洞察→导出知识闭环
│       ├── document-system-refactoring.md · 文档体系原子化重构方法论
│       ├── tool-trigger-mechanism.md · 工具开发触发器机制
│       ├── three-tier-governance.md · 三层治理模型（原子化→自动化→验证）
│       ├── tool-entropy-metrics.md · 工具熵减度量体系
│       ├── fact-statement-consistency-loop.md · 事实表述一致性闭环
│       ├── convention-driven-creation.md · 约定驱动创建模型（范例即模板）
│       └── spec-level-defense-in-depth.md · 规范层纵深防御模型（安全设计前置）
├── frameworks/                        ← 决策框架
│   ├── directory-naming-matrix.md     · 目录命名决策矩阵
│   ├── dependency-management-matrix.md · 临时依赖管理决策矩阵
│   ├── meta-document-processing-matrix.md · 元文档处理决策矩阵
│   └── semantic-match-threshold-matrix.md · 语义匹配阈值决策矩阵
├── concepts/                          ← 知识概念
│   ├── meta-document.md               · 元文档（Meta-Document）
│   ├── context-awareness.md           · 上下文感知（Context Awareness）
│   ├── orthogonal-verification.md     · 正交验证（Orthogonal Verification）
│   ├── zero-dependency-principle.md   · 零依赖原则（Zero-Dependency Principle）
│   ├── semantic-prefix.md             · 语义前缀（Semantic Prefix）
│   └── specification-bootstrapping.md · 规范自举性（Specification Bootstrapping）
├── reports/                           ← 项目复盘报告
│   ├── retrospective-report-agents-spec-system.md · 智能体开发规范体系项目复盘（初版）
│   ├── retrospective-report-agents-spec-system-comprehensive.md · 智能体开发规范体系全面复盘（深度版）
│   ├── retrospective-report-readme-atomization.md · README.md 原子化拆分复盘
│   ├── retrospective-report-check-spec-consistency.md · 规格文档一致性检查工具项目复盘
│   ├── retrospective-report-refactor-retrospective-docs.md · 复盘文档体系重构项目复盘
│   ├── retrospective-insight-optimization-cycle.md · 优化循环洞察报告（元模式与深层规律）
│   ├── retrospective-report-insight-execution.md · 洞察→执行闭环复盘（自我验证）
│   ├── retrospective-report-fact-statement-correction.md · 事实表述修正复盘
│   ├── retrospective-report-system-planning.md · README 系统规划章节新增复盘
│   ├── retrospective-report-cofounder-role-marker.md · 联合创始角色特殊标记复盘
│   └── retrospective-report-cofounder-improvement-execution.md · 联合创始改进建议执行复盘·洞察·萃取
└── assets/                            ← 资产清单
    └── asset-inventory.md             · 资产清单与复用指南
```

## 模块说明

### [templates/](templates/)
存放可复用的文档模板，涵盖规格文档、任务清单、检查清单、复盘报告与目录索引五类模板，可直接用于新项目初始化。

- [spec-template.md](templates/spec-template.md) — `spec.md` 规格文档模板，包含 Why、What Changes、Impact、ADDED/MODIFIED/REMOVED Requirements 标准结构
- [tasks-template.md](templates/tasks-template.md) — `tasks.md` 任务清单模板，包含主任务、子任务与依赖关系声明
- [checklist-template.md](templates/checklist-template.md) — `checklist.md` 检查清单模板，支持按类别分组
- [retrospective-report-template.md](templates/retrospective-report-template.md) — 项目复盘报告模板，遵循"事实 → 分析 → 洞察 → 建议"逻辑结构
- [directory-readme-template.md](templates/directory-readme-template.md) — 目录索引 README 模板，适用于模块化文档体系的根目录索引文件

### [patterns/code-patterns/](patterns/code-patterns/)
存放可直接复用的代码片段与实现模式，每个模式包含完整代码、来源说明与复用场景。

- [three-tier-check-tool.md](patterns/code-patterns/three-tier-check-tool.md) — 三段式检查工具架构（输入层→检查引擎→输出层），含完整代码骨架
- [context-aware-path-resolution.md](patterns/code-patterns/context-aware-path-resolution.md) — 上下文感知路径解析，通过语义前缀判断路径基准
- [meta-document-detection.md](patterns/code-patterns/meta-document-detection.md) — 元文档识别，区分自引用与外部引用数据
- [gitignore-validation.md](patterns/code-patterns/gitignore-validation.md) — Git 忽略规则验证，检查 `.gitignore` 规则完整性
- [regex-markdown-parsing.md](patterns/code-patterns/regex-markdown-parsing.md) — 正则驱动的 Markdown 章节与任务列表解析器

### [patterns/architecture-patterns/](patterns/architecture-patterns/)
存放可复用的架构设计模式与系统级最佳实践。

- [perception-check-report-model.md](patterns/architecture-patterns/perception-check-report-model.md) — 感知→检查→报告三层模型，自动化检查工具的设计蓝图
- [multi-agent-parallel-execution.md](patterns/architecture-patterns/multi-agent-parallel-execution.md) — 多智能体并行执行模式，含决策矩阵与适用场景
- [incremental-regression-verification.md](patterns/architecture-patterns/incremental-regression-verification.md) — 增量验证+回归验证双层策略
- [lifecycle-protocol-three-phase.md](patterns/architecture-patterns/lifecycle-protocol-three-phase.md) — 生命周期协议三阶段结构（创建→迁移→清理），每阶段含进入条件、执行规范、退出标准与门禁条件

### [patterns/methodology-patterns/](patterns/methodology-patterns/)
存放可复用的开发方法论与工作流程模式。

- [spec-driven-development.md](patterns/methodology-patterns/spec-driven-development.md) — Spec-driven 开发流程，"先设计后实施"的完整方法论
- [review-insight-export-loop.md](patterns/methodology-patterns/review-insight-export-loop.md) — 复盘→洞察→导出知识闭环，含报告结构模板
- [document-system-refactoring.md](patterns/methodology-patterns/document-system-refactoring.md) — 文档体系原子化重构方法论，含内容审计、原子化拆分、模块化归类、命名规范、引用追溯、索引生成六个步骤
- [tool-trigger-mechanism.md](patterns/methodology-patterns/tool-trigger-mechanism.md) — 工具开发触发器机制，当操作被手动执行 3 次以上时触发自动化评估
- [three-tier-governance.md](patterns/methodology-patterns/three-tier-governance.md) — 三层治理模型（原子化→自动化→验证），含依赖关系与实施检查清单
- [tool-entropy-metrics.md](patterns/methodology-patterns/tool-entropy-metrics.md) — 工具熵减度量体系，含 ROI 计算公式与已实施工具的熵减分析
- [fact-statement-consistency-loop.md](patterns/methodology-patterns/fact-statement-consistency-loop.md) — 事实表述一致性闭环，修正一处→搜索同类→统一修正，含决策矩阵与实施检查清单
- [dual-zone-development-model.md](patterns/methodology-patterns/dual-zone-development-model.md) — 双区开发模型（非正式区→质量门禁→正式区），代码与文档先在高熵区探索再迁移至低熵区
- [short-command-patterns.md](patterns/methodology-patterns/short-command-patterns.md) — 短指令模式库：登记已验证的 AI 协作快捷指令（如 复盘+洞察+萃取、跟进行动项 等）
- [five-category-asset-coverage.md](patterns/methodology-patterns/five-category-asset-coverage.md) — 五类资产覆盖原则：概念/模式/脚本/报告/索引五类互补覆盖的方法论
- [reference-as-trigger.md](patterns/methodology-patterns/reference-as-trigger.md) — 引用即触发协作模式：用户选中行号触发精确实施的方法论
- [structure-first-extension.md](patterns/methodology-patterns/structure-first-extension.md) — 结构阅读先行：扩展前先完整阅读包结构，同概念域追加、异概念域新建
- [amphibious-positioning-model.md](patterns/methodology-patterns/amphibious-positioning-model.md) — 两栖定位模型：通过资产清单+泛化路径图+落地案例三支柱支撑具体规范与元框架双重定位
- [diff-driven-refactoring.md](patterns/methodology-patterns/diff-driven-refactoring.md) — 差异驱动重构：逐段对比→标注三类标记→分类提取→回归验证
- [progressive-templating.md](patterns/methodology-patterns/progressive-templating.md) — 渐进式模板化：硬编码验证→模板分离→多类型扩展三阶段
- [retrospective-acceleration-effect.md](patterns/methodology-patterns/retrospective-acceleration-effect.md) — 复盘加速效应：高频批次复盘实现知识转化率 1×→3× 递增
- [two-phase-processing.md](patterns/methodology-patterns/two-phase-processing.md) — 双阶段加工策略：大型文档先横切（原子化）再纵切（模块化）的固定先后顺序

### [frameworks/](frameworks/)
存放可复用的决策框架与矩阵，帮助在不同场景下做出标准化决策。

- [directory-naming-matrix.md](frameworks/directory-naming-matrix.md) — 目录命名决策矩阵，覆盖第三方依赖、构建产物、文档等 7 类目录
- [dependency-management-matrix.md](frameworks/dependency-management-matrix.md) — 临时依赖管理决策矩阵，含存放位置、Git 跟踪、清理策略
- [meta-document-processing-matrix.md](frameworks/meta-document-processing-matrix.md) — 元文档处理决策矩阵，含识别优先级与处理级别
- [semantic-match-threshold-matrix.md](frameworks/semantic-match-threshold-matrix.md) — 语义匹配阈值决策矩阵，按场景推荐匹配阈值

### [concepts/](concepts/)
存放项目中提炼的核心知识概念，每个概念含定义、特征、示例与推广建议。

- [meta-document.md](concepts/meta-document.md) — 元文档：描述其他文档/项目的文档，引用外部数据时需特殊处理
- [context-awareness.md](concepts/context-awareness.md) — 上下文感知：检查逻辑在执行前先感知上下文属性
- [orthogonal-verification.md](concepts/orthogonal-verification.md) — 正交验证：多项优化各自独立验证，精确归因
- [zero-dependency-principle.md](concepts/zero-dependency-principle.md) — 零依赖原则：工具脚本仅依赖语言标准库
- [semantic-prefix.md](concepts/semantic-prefix.md) — 语义前缀：路径中隐含的、指示解析基准的前缀
- [specification-bootstrapping.md](concepts/specification-bootstrapping.md) — 规范自举性：规范本身规定如何扩展规范，使体系具备自我演化能力
- [pattern-maturity-levels.md](concepts/pattern-maturity-levels.md) — 模式成熟度分级体系：L1 实验性 → L2 已验证 → L3 标准化，含升级规则与当前资产快照
- [self-referentiality.md](concepts/self-referentiality.md) — 自指性：规范体系定义自身，当规范被精炼时，所有依赖派生产物被追踪和验证
- [critical-mass-of-methods.md](concepts/critical-mass-of-methods.md) — 方法论临界质量效应：模式数超 6 个后知识生产从线性累积进入组合爆炸
- [meta-document-leverage.md](concepts/meta-document-leverage.md) — 元文档杠杆效应：元文档篇幅占 <20% 但对采纳率贡献 >50%

### [reports/](reports/)
存放项目复盘分析报告，每份报告遵循"项目概述 → 复盘 → 洞察 → 导出"四段式结构。

- [retrospective-report-agents-spec-system.md](reports/retrospective-report-agents-spec-system.md) — 智能体开发规范体系项目复盘分析报告（初版）
- [retrospective-report-agents-spec-system-comprehensive.md](reports/retrospective-report-agents-spec-system-comprehensive.md) — 智能体开发规范体系项目全面复盘分析报告（深度版，含方法论萃取与行动指南）
- [retrospective-report-readme-atomization.md](reports/retrospective-report-readme-atomization.md) — README.md 原子化拆分复盘分析报告（含三要素模型与收益递减曲线）
- [retrospective-report-check-spec-consistency.md](reports/retrospective-report-check-spec-consistency.md) — 规格文档一致性检查工具项目复盘分析报告
- [retrospective-report-refactor-retrospective-docs.md](reports/retrospective-report-refactor-retrospective-docs.md) — 复盘文档体系重构项目复盘分析报告
- [retrospective-insight-optimization-cycle.md](reports/retrospective-insight-optimization-cycle.md) — 优化循环洞察报告，从 45 个原子提交中提取六大元模式与深层规律
- [retrospective-report-insight-execution.md](reports/retrospective-report-insight-execution.md) — 洞察→执行闭环复盘，验证 5 项行动建议全部执行的自我改进循环
- [retrospective-report-fact-statement-correction.md](reports/retrospective-report-fact-statement-correction.md) — 事实表述修正复盘，提炼"事实表述一致性闭环"方法论
- [retrospective-report-system-planning.md](reports/retrospective-report-system-planning.md) — README 系统规划章节新增任务复盘分析报告（含增量式需求扩展与四层闭环架构洞察）
- [retrospective-report-teams-module.md](reports/retrospective-report-teams-module.md) — 团队管理模块创建复盘分析报告（含约定驱动创建、规范层纵深防御、自举规范三大洞察）
- [retrospective-report-cofounder-role-marker.md](reports/retrospective-report-cofounder-role-marker.md) — 联合创始角色特殊标记复盘分析报告（含零侵入扩展范式与双点一致原则）
- [retrospective-report-cofounder-improvement-execution.md](reports/retrospective-report-cofounder-improvement-execution.md) — 联合创始改进建议执行复盘·洞察·萃取（含声明即校验模式与知识形态三阶跃迁）
- [retrospective-report-create-apps-directory.md](reports/retrospective-report-create-apps-directory.md) — apps/ 应用开发工作空间创建复盘·洞察·萃取（含双区开发模型、生命周期协议三阶段结构、目录创建三件套模式）
- [retrospective-insight-create-apps-directory-meta-analysis.md](reports/retrospective-insight-create-apps-directory-meta-analysis.md) — 单项目全流程协作元洞察报告（含拒批精度决定成本、复盘闭环四阶段进化、短指令低摩擦协作等 5 大洞察）
- [retrospective-meta-analysis-cross-project.md](reports/retrospective-meta-analysis-cross-project.md) — 跨项目元分析报告（含高频模式、顽固问题、演化趋势、资产增长率）
- [retrospective-report-insight-opportunities-implementation.md](reports/retrospective-report-insight-opportunities-implementation.md) — 洞察报告潜在机会实施复盘·洞察·萃取（含洞察→实施零延迟、五类资产覆盖原则）

### [assets/](assets/)
存放资产清单与复用指南，汇总项目中可直接复用的文件、需实例化的模式及需适配的决策框架。

- [asset-inventory.md](assets/asset-inventory.md) — 资产清单与复用指南，含 3 类资产表格

## 命名规范

所有文件名遵循 `kebab-case`（小写字母 + 连字符）命名规范，不含空格、中文、下划线或驼峰命名。

## 来源说明

本目录体系由 `docs/retrospective/knowledge-extraction.md`（2026-06-23 萃取）原子化拆分而来，所有内容均来自实际项目中的成功实践，而非理论推演。每个模块文件均标注了原始来源与关联模块，便于追溯与导航。

> 最后更新：2026-06-23