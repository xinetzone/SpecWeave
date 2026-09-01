---
type: Pattern
id: "categories"
title: "方法论模式主题分类说明"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/CATEGORIES.toml"
---

# 方法论模式主题分类说明

基于模式的核心主题思想进行分类，而非成熟度等级或来源。共划分为8个主题类别，便于按场景快速定位相关模式。

> **数据来源**：以下计数基于各目录实际 `.md` 文件数（排除README.md与子目录），由 `generate-categories.py` 自动重建，最后更新：2026-08-18。

## 分类索引

| 主题目录 | 中文名称 | 模式数量 | 核心关注点 |
|---------|---------|---------|-----------|
| [retrospective-knowledge](#retrospective-knowledge--复盘与知识生命周期) | 复盘与知识生命周期 | 35 | 项目复盘流程、知识萃取、洞察沉淀、经验迁移 |
| [research-knowledge](#research-knowledge--外部研究与知识融合) | 外部研究与知识融合 | 36 | 外部网站分析、Vendor仓库高层文档优先研究、跨Vendor/跨领域知识融合、信息源分层兜底、访问障碍应对、多源验证、外部文章深度分析端到端工作流、语义漂移防御、知识系统五维根基、B2B AI产品定位、外部产品学习模板 |
| [document-architecture](#document-architecture--文档架构与原子化) | 文档架构与原子化 | 52 | 文档体系重构、原子化拆分、文档治理、结构设计 |
| [tools-automation](#tools-automation--工具工程与自动化) | 工具工程与自动化 | 49 | 工具决策、工具故障降级、自动化实施、工具链建设、批量操作安全 |
| [governance-strategy](#governance-strategy--治理与优先级策略) | 治理与优先级策略 | 139 | 体系治理、优先级排序、问题解决、规范防护、方法论构造性验证 |
| [ai-collaboration](#ai-collaboration--ai协作与提示词设计) | AI协作与提示词设计 | 70 | AI Skill设计、人机协作模式、提示词工程、输出行为规范、团队共享AI同事、主动介入Agent、安全信任设计、源码锚点二次校验、契约文档协调中枢、模块级agents扩展、references渐进式披露、Gotchas领域特化、视觉通用操作、输出格式-协作能力映射、生态壁垒评估、诚实承认局限性信任构建 |
| [creative-design](#creative-design--创意与设计原则) | 创意与设计原则 | 10 | 创意生成、视觉设计、认知锚点、角色驱动设计 |
| [product-growth](#product-growth--产品开发与竞争策略) | 产品开发与竞争策略 | 44 | 产品定位、赛事增长、竞争策略、交付流水线、硬件产品设计、To B合规策略、三层商业模式、IoT技术架构、本地保底信任、双版本矩阵、AI转型MCP路径、专业能力平民化、垂直场景AI三要素、全链路闭环、风控前置、爆款复刻、双模式分层、多触点AIDA转化 |

---

## retrospective-knowledge — 复盘与知识生命周期

**核心关注点**：围绕项目复盘流程、知识萃取、洞察沉淀、经验迁移的全生命周期模式。

**边界说明**：包含复盘方法论框架、洞察加工转化漏斗、知识沉淀分层体系、经验跨领域迁移验证、知识资产演化规律；不包含具体的文档操作工具实现、AI提示词设计或产品增长策略。

| 模式文件 | 一句话说明 | 成熟度 |
|---------|-----------|-------|
| [actionable-suggestion-five-elements.md](retrospective-knowledge/actionable-suggestion-five-elements.md) | 可执行建议五要素：交付物+验收+优先级+集成+状态，含1:1无冗余映射原则 | L1 |
| [bug-as-asset.md](retrospective-knowledge/bug-as-asset.md) | Bug即资产转化机制：三条件萃取标准（可命名+可复现+可防护），架构级Bug优先萃取 | L2 |
| [closed-loop-pdca-mapping.md](retrospective-knowledge/closed-loop-pdca-mapping.md) | 闭环PDCA映射：四步闭环与戴明环的映射，含双正反馈回路机制 | L1 |
| [constraint-driven-fix-path-priority-matrix.md](retrospective-knowledge/constraint-driven-fix-path-priority-matrix.md) | 约束驱动的修复路径优先级矩阵（Constraint-Driven Fix Path Priority Matrix） | L1 |
| [counterfactual-debt-analysis.md](retrospective-knowledge/counterfactual-debt-analysis.md) | 反事实推演与技术债复利分析：通过时间线推演表量化"不做改进"的复利代价 | L1 |
| [dual-track-retrospective-cadence.md](retrospective-knowledge/dual-track-retrospective-cadence.md) | 双轨复盘节奏：时间驱动与事件驱动互补 | L1 |
| [experience-transfer-mapping.md](retrospective-knowledge/experience-transfer-mapping.md) | 经验迁移映射：三列表（本经验→可迁移到→迁移示例）区分核心机制vs上下文细节，≥3个跨领域验证通用性 | L1 |
| [export-four-channel-progressive.md](retrospective-knowledge/export-four-channel-progressive.md) | 导出四渠道递进：文档化→模板化→工具化→制度化，含渐进式策略与决策准则速查 | L1 |
| [export-suggestions-pattern-catalog.md](retrospective-knowledge/export-suggestions-pattern-catalog.md) | 导出建议通用模式目录（Export Suggestions Pattern Catalog） | L1 |
| [extraction-four-layer-funnel.md](retrospective-knowledge/extraction-four-layer-funnel.md) | 萃取四层漏斗：去噪→结构化→标准化→可操作化，含"四可"质量标准 | L1 |
| [five-category-asset-coverage.md](retrospective-knowledge/five-category-asset-coverage.md) | 五类资产覆盖原则：概念/模式/脚本/报告/索引五类互补覆盖 | L2 |
| [immediate-retrospective-sedimentation.md](retrospective-knowledge/immediate-retrospective-sedimentation.md) | 即时复盘沉淀模式 | L2 |
| [information-source-tiered-collection.md](retrospective-knowledge/information-source-tiered-collection.md) | 信息源分层采集策略 | L2 |
| [insight-iceberg-model.md](retrospective-knowledge/insight-iceberg-model.md) | 洞察冰山模型：现象层→模式层→原理层三层递进分析，含关键转折点与高质量洞察三特征 | L1 |
| [insight-library-evolution.md](retrospective-knowledge/insight-library-evolution.md) | 洞察库演化规律：三阶段（描述期/展开期/系统期）、概念完备线信号、5个锚点洞察识别 | L2 |
| [insight-two-tier-structure.md](retrospective-knowledge/insight-two-tier-structure.md) | 洞察两档结构：基础档/完整档双轨写作，10-20%核心概念承担80%解释力（帕累托法则） | L2 |
| [integration-notes-explicitness.md](retrospective-knowledge/integration-notes-explicitness.md) | 整合阶段信息显性化模式（Integration Notes Explicitness Pattern） | - |
| [knowledge-compound-interest.md](retrospective-knowledge/knowledge-compound-interest.md) | 知识沉淀复利模型：产出价值=基础×抽象层级^复用次数，复盘萃取是唯一能升级产出层级的活动 | L1 |
| [knowledge-sedimentation-workflow-sop.md](retrospective-knowledge/knowledge-sedimentation-workflow-sop.md) | 增强版知识沉淀工作流SOP（Enhanced Knowledge Sedimentation Workflow SOP） | L1 |
| [meta-retrospective-two-round-method.md](retrospective-knowledge/meta-retrospective-two-round-method.md) | 元复盘双轮法 | L2 |
| [methodology-critical-mass.md](retrospective-knowledge/methodology-critical-mass.md) | 方法论临界质量效应：模式数突破 6 后从线性累积跃迁至组合爆炸，知识生产边际收益递增 | L1 |
| [methodology-five-level-maturity.md](retrospective-knowledge/methodology-five-level-maturity.md) | 方法论五级成熟度：借鉴CMMI的五级评估框架，含跃迁路径与评估方法 | L1 |
| [multi-source-intelligence-iteration.md](retrospective-knowledge/multi-source-intelligence-iteration.md) | 多源增量情报迭代法：五子系统构成的多轮决策分析引擎 | L3 |
| [pre-check-duplication-layered-sedimentation.md](retrospective-knowledge/pre-check-duplication-layered-sedimentation.md) | 知识沉淀前置查重与分层沉淀工作流 | - |
| [report-as-tracking.md](retrospective-knowledge/report-as-tracking.md) | 报告即追踪载体，每执行一个建议后立即更新报告状态形成闭环 | L2 |
| [retrospective-acceleration-effect.md](retrospective-knowledge/retrospective-acceleration-effect.md) | 复盘加速效应：高频复盘→低延迟改进→知识转化率递增 | L1 |
| [retrospective-four-step-method.md](retrospective-knowledge/retrospective-four-step-method.md) | 复盘四步法：回顾目标→还原事实→分析偏差→提炼经验，含四步产出物对照表与误区清单 | L1 |
| [review-insight-export-loop.md](retrospective-knowledge/review-insight-export-loop.md) | 复盘→洞察→导出知识闭环，含报告结构模板 | L2 |
| [rolling-retro-eight-steps.md](retrospective-knowledge/rolling-retro-eight-steps.md) | 滚动复盘八步：文档一致性的低成本保障机制，每轮15-30分钟维持多轮迭代一致性 | L3 |
| [second-exposure-governance-loop.md](retrospective-knowledge/second-exposure-governance-loop.md) | 二次暴露触发治理闭环 | L2 |
| [suggestion-priority-driven-execution.md](retrospective-knowledge/suggestion-priority-driven-execution.md) | 建议执行优先级驱动模型，高/中/低优先级分类 + 投入估算 + 状态追踪 | L2 |
| [three-part-retrospective.md](retrospective-knowledge/three-part-retrospective.md) | 三段式复盘改进法：事实层→认知层→行动层严格单向依赖，含检查清单，100%建议落地率验证 | L3 |
| [three-tier-knowledge-sedimentation.md](retrospective-knowledge/three-tier-knowledge-sedimentation.md) | 三层知识沉淀体系：洞察原文（第三层）→ 专题报告（第二层）→ README 条目（第一层）的递进式知识网络 | L1 |
| [triangular-source-verification.md](retrospective-knowledge/triangular-source-verification.md) | 三源信息三角验证法 SOP | L2 |
| [wave-workday-rhythm.md](retrospective-knowledge/wave-workday-rhythm.md) | 波次式工作日节奏 | L1 |

---

## research-knowledge — 外部研究与知识融合

**核心关注点**：围绕外部网站分析、竞品研究、vendor子模块学习、跨项目知识融合等依赖外部信息源和知识吸收的任务方法论，重点解决信息访问受阻、信息源质量参差不齐、多源验证、外部知识如何有效融入自有体系等问题。

**边界说明**：包含外部网站访问受阻时的分层降级策略、信息源可信度评级、三角验证法、Vendor仓库高层文档优先研究法、跨Vendor知识融合三步流程；不包含内部知识复盘沉淀（见retrospective-knowledge）、文档架构治理、AI协作提示词设计或产品竞争策略本身。

| 模式文件 | 一句话说明 | 成熟度 |
|---------|-----------|-------|
| [adversarial-review-protocol.md](research-knowledge/adversarial-review-protocol.md) | 对抗性审查协议：六模块框架（来源三级分类+可信度四级评分+五维验证+九种偏差清单+异常标记+验证日志），质量内建而非事后质检，实现77.3%一级来源、0D级内容 | L2 |
| [b2b-ai-last-mile-positioning-framework.md](research-knowledge/b2b-ai-last-mile-positioning-framework.md) | B2B AI产品最后一公里定位分析框架：区分"开发框架(0→1)"与"生产平台(1→100)"的本质差异，四大价值支柱（安全合规/可观测性/集成生态/成本治理）识别企业AI落地真正壁垒，避免功能列表对比陷阱 | - |
| [b2b-product-page-ux-five-dimensions.md](research-knowledge/b2b-product-page-ux-five-dimensions.md) | ToB产品页UX分析五维框架（信息架构/价值传达/CTA策略/视觉呈现/信任背书），含AIDA模型对应关系、反模式识别、五维检查清单 | - |
| [b2b-product-seven-segment-ia.md](research-knowledge/b2b-product-seven-segment-ia.md) | B端技术产品页面七段式认知递进信息架构（Hero→能力→优势→场景→架构→案例→CTA），严格遵循用户决策路径，含完整性检查清单和各段设计规范 | - |
| [b2b-value-quantification-case-validation.md](research-knowledge/b2b-value-quantification-case-validation.md) | B端产品价值量化与案例验证双闭环模式：首屏量化亮剑→优势区解释→场景区匹配→案例区验证，形成"承诺→解释→场景→验证"完整证据链，解决空洞形容词和无效Logo墙问题 | - |
| [classic-patterns-reuse-heuristic.md](research-knowledge/classic-patterns-reuse-heuristic.md) | 经典模式优先复用启发式（Classic Patterns First Heuristic） | L2 |
| [core-scenario-dual-layer.md](research-knowledge/core-scenario-dual-layer.md) | 核心-场景双层知识架构（Core-Scenario Dual-Layer Architecture） | L1 |
| [credibility-dual-track.md](research-knowledge/credibility-dual-track.md) | 可信度评分+验证日志双轨制：正文简洁标注A/B/C/D等级不干扰阅读，独立验证日志完整记录审计过程，实现"快速获取"和"严谨审计"两类需求的分离 | L2 |
| [cross-cultural-reverse-hermeneutics-defense.md](research-knowledge/cross-cultural-reverse-hermeneutics-defense.md) | 跨文化比较反向格义防御七步法（Cross-Cultural Reverse Hermeneutics Defense） | L1 |
| [cross-domain-semantic-drift.md](research-knowledge/cross-domain-semantic-drift.md) | 跨领域语义漂移防御：Spec阶段概念扫描→歧义术语显式标注→术语表单一事实源，解决跨领域知识整合中"同一术语不同含义"的隐性陷阱，防御可降低15%+返工 | L2 |
| [cross-vendor-knowledge-fusion.md](research-knowledge/cross-vendor-knowledge-fusion.md) | 跨Vendor知识融合三步法：理解Vendor→认知自我→优势互补融合，避免"全盘照搬"和"NIH综合征"两个极端，融合后1+1>2 | - |
| [entry-doc-mirror-analysis.md](research-knowledge/entry-doc-mirror-analysis.md) | 入门文档镜像分析法：8维度信号清单+判断矩阵，系统性提取Vendor入门文档中的产品定位、能力边界、设计哲学信号 | - |
| [essential-contradiction-three-step.md](research-knowledge/essential-contradiction-three-step.md) | 技术方案本质矛盾三步法 | L1 |
| [example-first-alignment.md](research-knowledge/example-first-alignment.md) | 示例优先对齐模式（Example-First Alignment / Reference Before Create） | L2 |
| [external-article-deep-analysis-methodology.md](research-knowledge/external-article-deep-analysis-methodology.md) | 外部文章深度分析方法论（六步法）：内容提取→观点提炼→逻辑分析→知识萃取→可靠性评估→批判性思考六步认知法，与端到端工作流互补（工作流聚焦"如何编排执行"，六步法聚焦"如何思考分析"），1次验证（mainecoon） | L1 |
| [external-article-deep-analysis-workflow.md](research-knowledge/external-article-deep-analysis-workflow.md) | 外部文章深度分析端到端工作流：四阶段编排（defuddle获取→spec三件套→单一子智能体执行→Grep数据验证三查法），含14章节报告结构模板，4次验证（mattpocock/agent-reach/codex/mainecoon），质量可预测 | L2 |
| [external-website-analysis-fallback-strategy.md](research-knowledge/external-website-analysis-fallback-strategy.md) | 外部网站分析四层信息源分层兜底策略（直接访问→工具增强→官方替代源→第三方权威源），含反自动化检测突破（403/JS challenge）、云厂商SPA预判、控制台登录预判、工具间降级原则、浏览器MCP四步SOP、降级决策流程与三角验证SOP，2次实战验证（贝锐403+知乎反爬） | L2 |
| [falsifiable-claim-evaluation.md](research-knowledge/falsifiable-claim-evaluation.md) | 可证伪愿景检验法（Falsifiable Vision Check） | L1 |
| [first-principles-feature-analysis.md](research-knowledge/first-principles-feature-analysis.md) | 第一性原理功能分析法 | L1 |
| [five-layer-progressive-analysis.md](research-knowledge/five-layer-progressive-analysis.md) | 五层递进分析框架（Five-Layer Progressive Analysis） | L1 |
| [knowledge-archive-four-layer.md](research-knowledge/knowledge-archive-four-layer.md) | 知识档案四层架构：规则层(00)→领域内容层(01-N)→跨领域整合层→索引层(README)，规则先行、内容解耦、整合后置、索引最后，解决索引过早固化问题 | L2 |
| [knowledge-system-construction-template.md](research-knowledge/knowledge-system-construction-template.md) | 知识体系构建SOP模板（Knowledge System Construction Template） | L2 |
| [knowledge-system-evolution-three-stages.md](research-knowledge/knowledge-system-evolution-three-stages.md) | 知识体系三阶段演化模型（Knowledge System Evolution Three Stages） | L2 |
| [knowledge-system-five-foundations.md](research-knowledge/knowledge-system-five-foundations.md) | 知识系统五维根基框架：设计知识系统时从五个基础学科原理推导出必须回答的根本问题（知识质量/认知防御/信任架构/术语统一/质量生成），避免凭直觉/类比搭建导致的维度缺失，五维完备则0返工，缺失一维则返工率15-30% | L1 |
| [methodology-overflow-paradigm.md](research-knowledge/methodology-overflow-paradigm.md) | 方法论溢出范式（Methodology Overflow Paradigm） | L1 |
| [open-source-repo-four-layer-identification.md](research-knowledge/open-source-repo-four-layer-identification.md) | 开源仓库四层架构识别法 | L1 |
| [platform-gap-filling-base-reuse-model.md](research-knowledge/platform-gap-filling-base-reuse-model.md) | 「断层填补+基座复用」产业平台化模式 | - |
| [progressive-spec-planning-for-external-content.md](research-knowledge/progressive-spec-planning-for-external-content.md) | 外部内容分析渐进式Spec规划：三阶段时间盒（最小可行Spec 15min→内容获取试错30min→基于样本调整10min），核心原则"最小启动+渐进细化"，避免规划阶段耗时过长 | L1 |
| [riev-doc-learning-method.md](research-knowledge/riev-doc-learning-method.md) | RIEV文档学习法 | L2-validated |
| [small-sample-analysis-methodology.md](research-knowledge/small-sample-analysis-methodology.md) | 小样本分析方法论与三层分析框架适用性边界：样本量<5时执行"保留/降级/标注"三规则，三层框架（系统性学习→深度洞察→知识萃取）各层降级映射，解决"分析精度 vs 原始内容信度"根本矛盾 | L1 |
| [source-pipeline-penetration-method.md](research-knowledge/source-pipeline-penetration-method.md) | 源码学习管线穿透法 | L1 |
| [spec-anchored-questioning.md](research-knowledge/spec-anchored-questioning.md) | Spec锚定提问法（Spec-Anchored Questioning） | L1 |
| [vendor-doc-info-compensation-search.md](research-knowledge/vendor-doc-info-compensation-search.md) | 厂商技术文档信息补偿六源搜索策略：控制台需登录/文档截断时，按SDK/Skill→QuickStart→插件市场→GitHub→社区→博客优先级搜索补偿信息源，含Mermaid决策流程、DX机制解释、反模式清单 | - |
| [vendor-high-level-doc-first-research.md](research-knowledge/vendor-high-level-doc-first-research.md) | Vendor仓库"自顶向下"研究法：先读AGENTS.md/CLAUDE.md等AI友好高层文档建立全局框架，再按需深入源码，效率提升5-10倍，基础设施故障时的救命稻草 | - |
| [vendor-neutral-three-layer-learning.md](research-knowledge/vendor-neutral-three-layer-learning.md) | 厂商项目三层剥离学习法 | L2 |
| [vendor-product-learning-twelve-step-template.md](research-knowledge/vendor-product-learning-twelve-step-template.md) | 外部产品系统性学习分析十二步任务模板：标准化任务分解确保产品学习全面深入可复用，支持技术工具类和商业模式类两类产品，4次验证（SearchInfinity/Sandbox/Ark双产品/方舟入门文档），催生镜像分析法和默认配置探针法 | - |

---

## document-architecture — 文档架构与原子化

**核心关注点**：围绕文档体系重构、原子化拆分、文档治理、结构设计的模式。

**边界说明**：包含文档拆分策略、入口设计、链接管理、元文档策略、模块化接口设计、双受众内容萃取、双阶段加工流程；不包含开发流程规范、工具自动化实现细节或AI提示词设计。

| 模式文件 | 一句话说明 | 成熟度 |
|---------|-----------|-------|
| [antipattern-first-best-practices.md](document-architecture/antipattern-first-best-practices.md) | 反模式优先最佳实践写作法 | L1 |
| [atomization-quick-reference-dual-layer.md](document-architecture/atomization-quick-reference-dual-layer.md) | 原子化+速查手册双层架构 | L1 |
| [atomization-three-criteria-test.md](document-architecture/atomization-three-criteria-test.md) | 原子化三标准检验：单一职责/独立可测/命名聚合三准则互验 | L1 |
| [atomization-three-tier-classification.md](document-architecture/atomization-three-tier-classification.md) | 原子化三级分类策略：新建模式/已有覆盖/原地保留三级判断，替代"每个发现都新建模式" | L1 |
| [bare-url-autolink-wrap.md](document-architecture/bare-url-autolink-wrap.md) | 裸URL自动链接包裹（Bare URL Autolink Wrap） | L1 |
| [bidirectional-navigation-links.md](document-architecture/bidirectional-navigation-links.md) | 原子文件双向导航三链路：prev/next/返回目录，解决原子化后阅读路径断裂问题 | L1 |
| [blockquote-code-block-rendering-fix.md](document-architecture/blockquote-code-block-rendering-fix.md) | 引用块嵌套代码块渲染修复：Markdown引用块内代码块链接/加粗失效问题的解决方案 | L1 |
| [blockquote-code-block-rendering-usage-guide.md](document-architecture/blockquote-code-block-rendering-usage-guide.md) | 引用块代码块渲染修复深度指南：5种变体、8组正反例、渲染器兼容性说明 | L1 |
| [classification-disposition-decision-tree.md](document-architecture/classification-disposition-decision-tree.md) | 文档原子化分类处置决策树模式 | L2 |
| [cognitive-closure-document-split.md](document-architecture/cognitive-closure-document-split.md) | 认知闭环划分原则（Cognitive Closure Document Split） | - |
| [concept-comparison-tutorial-structure.md](document-architecture/concept-comparison-tutorial-structure.md) | 概念对比中心教程结构：多易混技术概念讲解法 | L1 |
| [content-entry-index-trinity.md](document-architecture/content-entry-index-trinity.md) | 内容-入口-索引三位一体原则 | L1 |
| [content-migration-workflow.md](document-architecture/content-migration-workflow.md) | 文档内容迁移标准操作流程，存量盘点→缺口计算→富化归档→验证闭环 | L2 |
| [document-atomization-u-curve.md](document-architecture/document-atomization-u-curve.md) | 文档原子化U型演进曲线（Document Atomization U-Curve） | - |
| [document-content-funnel.md](document-architecture/document-content-funnel.md) | 文档内容加工四层漏斗：外部网页→L1去噪→L2观点标记→L3信息架构（含原子化决策检查点）→L4知识库集成，每跳步对应质量问题 | L3 |
| [document-entropy-three-strategies.md](document-architecture/document-entropy-three-strategies.md) | 文档声明熵增三策：人工同步字段过时是必然，推荐"移除变量+免责声明"零成本方案 | L3 |
| [document-system-refactoring.md](document-architecture/document-system-refactoring.md) | 文档体系原子化重构方法论，含六步流程 | L2 |
| [document-update-first-principles.md](document-architecture/document-update-first-principles.md) | 文档更新第一性原理模式 | L2 |
| [dual-audience-extraction-model.md](document-architecture/dual-audience-extraction-model.md) | 双受众萃取模型：一次投入产出两类资产——面向Agent的模板+面向人类的方法论，分开撰写效果更好 | L2 |
| [engineering-article-seven-techniques-template.md](document-architecture/engineering-article-seven-techniques-template.md) | 工程方法论文章七技法·实战填空模板 | L1 |
| [engineering-article-seven-techniques.md](document-architecture/engineering-article-seven-techniques.md) | 工程方法论文章七技法 | L1 |
| [entry-comparison-table.md](document-architecture/entry-comparison-table.md) | 入口对比表模式（Entry Comparison Table Pattern） | L3 |
| [entry-container-separation.md](document-architecture/entry-container-separation.md) | 入口-容器分离原则：README（人类）最大精简、AGENTS（AI）路由级保留、.agents/ 全量承载（793次提交验证，L3标准化） | L3 |
| [external-tech-doc-wiki-structure.md](document-architecture/external-tech-doc-wiki-structure.md) | 外部技术文档Wiki标准结构与创建流程 | L2 |
| [fact-statement-consistency-loop.md](document-architecture/fact-statement-consistency-loop.md) | 事实表述一致性闭环，修正一处→搜索同类→统一修正 | L2 |
| [i18n-anchor-page-strategy.md](document-architecture/i18n-anchor-page-strategy.md) | 国际化锚定页策略：仅翻译核心索引表 + 路由指引，避免全量翻译的维护成本爆炸 | L1 |
| [knowledge-base-three-stage.md](document-architecture/knowledge-base-three-stage.md) | 知识库建设三阶段：生成→重组→精确化，顺序不可颠倒，跳过中间阶段导致返工（59个Wiki验证） | L2 |
| [large-document-atomization-method.md](document-architecture/large-document-atomization-method.md) | 大文档原子化拆分法（索引页+原子文件+TOML元数据） | L2 |
| [large-scale-duplication-elimination.md](document-architecture/large-scale-duplication-elimination.md) | 大规模重复消除法：审计→分类→共享库先行→并行迁移→全量验证五步法 | L2 |
| [link-decay-laws.md](document-architecture/link-decay-laws.md) | 文档链接衰变四规律：下移断链多/上移影响小/跨目录最脆弱/同目录最稳定 | L1 |
| [mermaid-layered-visualization.md](document-architecture/mermaid-layered-visualization.md) | Mermaid 分层可视化：一图一义+分层独立，时间/决策/依赖/流程四维度分层策略与状态标注规范 | L2 |
| [meta-atomization-bisect-overview.md](document-architecture/meta-atomization-bisect-overview.md) | 元原子化二分+概览模式：中型文档单章节膨胀的轻量拆分法（时间二分法/概览详情分离法），6步操作指南 | L2 |
| [meta-document-leverage.md](document-architecture/meta-document-leverage.md) | 元文档杠杆效应：<20%篇幅贡献>50%采纳率，元文档（入口/索引/门面）ROI最高，资源有限时优先投资（量化验证，L3标准化） | L3 |
| [methodology-evolution-cross-refs.md](document-architecture/methodology-evolution-cross-refs.md) | 方法论演进交叉引用链：知识网络双向链接模式 | - |
| [modularization-interface-design.md](document-architecture/modularization-interface-design.md) | 模块化接口设计四步法：边界→接口→耦合→版本，含七级耦合标尺与 30 秒准则 | L1 |
| [multi-product-comparison-structure.md](document-architecture/multi-product-comparison-structure.md) | 多产品对比学习四段式结构：产品线系统学习文档组织法 | L2 |
| [one-stop-operation-guide.md](document-architecture/one-stop-operation-guide.md) | 一站式操作指南：高频任务单文件整合入口，将规则/模板/工具/排错压缩为单文件直达 | L2 |
| [pattern-merge-boundary.md](document-architecture/pattern-merge-boundary.md) | 模式合并边界判断：三维重叠度（场景/机制/建议）>70% 合并，30-70% 独立判断，<30% 独立创建 | L1 |
| [post-atomization-content-merge-back.md](document-architecture/post-atomization-content-merge-back.md) | 原子化后内容回源合并：深度分析提取后源文档降级为概要+引用，模式文件为唯一权威来源 | L1 |
| [product-learning-five-tier-pyramid.md](document-architecture/product-learning-five-tier-pyramid.md) | 产品学习文档5层价值金字塔：信息→理解→场景→商业→前瞻，越往上层价值半衰期越长、可复用性越高 | L2 |
| [progressive-doc-consolidation.md](document-architecture/progressive-doc-consolidation.md) | 渐进式文档合并（Progressive Document Consolidation） | - |
| [progressive-readme-growth.md](document-architecture/progressive-readme-growth.md) | 渐进式 README 生长：每完成一轮知识产出即追加一行技术创新点，最低成本持续提升 README 价值密度 | L1 |
| [protocol-reference-distill-verify.md](document-architecture/protocol-reference-distill-verify.md) | 协议文档「参考-提炼-验证」三步法（Reference-Distill-Verify Three-Step Method） | L2 |
| [scripted-batch-correction.md](document-architecture/scripted-batch-correction.md) | 脚本化批量修正安全决策：根据旧名称出现模式（路径引用/代码标识符）选择脚本化或手动 | L1 |
| [source-document-downgrade.md](document-architecture/source-document-downgrade.md) | 源文档降级模式：大型文档原子化后不删除源文档，降级为引用导航页 | L2 |
| [spec-narrative-separation.md](document-architecture/spec-narrative-separation.md) | 技术规格与叙述报告分离原则 | L2 |
| [sunlogin-hardware-wiki-structure.md](document-architecture/sunlogin-hardware-wiki-structure.md) | 向日葵硬件系列Wiki标准结构（13章）：4次验证的硬件产品学习Wiki文档模板，从产品概述到行业趋势覆盖认知全链路 | L2 |
| [synthetic-stats-source-of-truth.md](document-architecture/synthetic-stats-source-of-truth.md) | 合成统计的权威数据来源：跨文件统计数据应从 metadata 全量重算，而非增量推算，避免偏差累积 | L1 |
| [tech-wiki-four-layer-need-structure.md](document-architecture/tech-wiki-four-layer-need-structure.md) | 技术wiki四层需求结构 | L1 |
| [trust-first-content-funnel.md](document-architecture/trust-first-content-funnel.md) | 信任前置内容漏斗（Trust-First Content Funnel） | - |
| [tutorial-cognitive-ladder.md](document-architecture/tutorial-cognitive-ladder.md) | 教程认知阶梯：技术教程六层递进结构（概述→原则→示例→快速开始→本地整合→生态上下文），按读者认知路径组织 | L2 |
| [two-phase-processing.md](document-architecture/two-phase-processing.md) | 双阶段加工策略：大型文档先横切（原子化）再纵切（模块化）的固定先后顺序 | L1 |

---

## tools-automation — 工具工程与自动化

**核心关注点**：围绕工具自动化决策、安全实施策略、工具链成熟度建设、批量操作风险控制的工程模式。

**边界说明**：包含自动化ROI判断模型、dry-run安全修改流程、工具链五阶段演进、路径幂等性纪律、批量替换脆弱性规避、精度优先于召回原则；不包含文档架构设计决策、治理优先级策略或知识萃取方法论。

| 模式文件 | 一句话说明 | 成熟度 |
|---------|-----------|-------|
| [auto-generate-threshold.md](tools-automation/auto-generate-threshold.md) | 自动化阈值判断：手动条目占比 30% 阈值 + 模式成熟度 validation_count≥2 自动升级规则 | L2 |
| [automation-idempotent-four-elements.md](tools-automation/automation-idempotent-four-elements.md) | 自动化幂等四要素：install/verify面向结果建模+幂等+可回滚+可判定，全分支验证（install.py验证） | L1 |
| [best-practice-hidden-cost.md](tools-automation/best-practice-hidden-cost.md) | 最佳实践隐性成本：推广实践须配套吸收成本的工具链（如原子化的"链接税"） | L1 |
| [capability-matrix.md](tools-automation/capability-matrix.md) | 能力清单/功能矩阵：显式声明工具能力边界与精确度，三重价值（用户/维护者/规划） | L1 |
| [defuddle-web-extraction-preferred.md](tools-automation/defuddle-web-extraction-preferred.md) | defuddle网页提取首选+双工具兜底模式：提取网页文章正文优先defuddle，含四步预检查法、双工具兜底、llms.txt索引优先发现、SPA场景浏览器优先、PowerShell URL特殊字符处理（8次验证，L3） | L3 |
| [depth-reference-table.md](tools-automation/depth-reference-table.md) | 深度参考表：预计算常见目录深度的相对路径前缀+methodology-patterns子目录交叉引用速查表，将易错心算转化为查表操作（2次验证，L3） | L3 |
| [derived-file-auto-generation.md](tools-automation/derived-file-auto-generation.md) | 衍生文件全自动原则（禁手编辑原则） | L2 |
| [dict-comprehension-simplification.md](tools-automation/dict-comprehension-simplification.md) | 字典推导式简化转换循环：消除样板代码 | L1 |
| [diff-driven-refactoring.md](tools-automation/diff-driven-refactoring.md) | 差异驱动重构：逐段对比→标注重复/相似/独有→分类提取→回归验证 | L2 |
| [dry-run-first.md](tools-automation/dry-run-first.md) | dry-run 安全修改模式：默认预览→用户确认→执行写入→立即验证，零误报信任建立 | L3 |
| [encapsulation-contract-essence.md](tools-automation/encapsulation-contract-essence.md) | 封装的契约本质：内部重构零风险安全模式 | L1 |
| [explicit-maturity-tracking.md](tools-automation/explicit-maturity-tracking.md) | 成熟度显式追踪：L1-L4统一分级，frontmatter标准字段，四重价值与升级规则 | L1 |
| [feishu-doc-dom-extraction.md](tools-automation/feishu-doc-dom-extraction.md) | 飞书云文档DOM提取模式（Feishu/Lark Cloud Document DOM Extraction Pattern） | L1 |
| [full-workflow-integration.md](tools-automation/full-workflow-integration.md) | 全流程整合模式：识别高频切换点→原生集成外部工具→单一界面完整体验，保持用户心流减少中断 | - |
| [git-complex-config-file-first.md](tools-automation/git-complex-config-file-first.md) | Git复杂配置文件优先原则：跨平台Shell转义陷阱规避 | L1 |
| [git-hooks-three-tier-trust.md](tools-automation/git-hooks-three-tier-trust.md) | Git钩子三层信任模型：L1 pre-commit(<5s)→L2 pre-push(<30s)→L3 CI(<10min)，按时间预算分层部署检查 | L2 |
| [git-local-clone-safety-protocol.md](tools-automation/git-local-clone-safety-protocol.md) | 本地路径Git克隆异常最小破坏处置协议：Windows下git clone本地路径BUG的检测→留痕→稳妥重试流程 | L1 |
| [implicit-contract-pitfalls.md](tools-automation/implicit-contract-pitfalls.md) | 隐式契约陷阱：语言隐藏行为导致的Bug | L1 |
| [legacy-exposure-effect.md](tools-automation/legacy-exposure-effect.md) | 新检测规则存量暴露效应：落地新linter/checker前先扫描历史存量问题，避免CI一片红 | L2 |
| [link-check-dual-coverage.md](tools-automation/link-check-dual-coverage.md) | 链接检查双覆盖原则 | L1 |
| [metric-tool-exclusion-profiling.md](tools-automation/metric-tool-exclusion-profiling.md) | 度量工具排除机制与配置画像：内置默认exclude+按目录类型预设profile（docs/specs/agents/code），消除一刀切权重误判 | L1 |
| [model-to-test-matrix.md](tools-automation/model-to-test-matrix.md) | 理论模型→测试矩阵转化：边界界定→优先级映射→风险点展开→用例生成，模型层级即测试边界 | L1 |
| [multi-signal-detection.md](tools-automation/multi-signal-detection.md) | 多信号组合检测：N个独立信号源或逻辑组合，按可靠性排序，反向信号辅助，DEBUG模式输出完整JSON诊断 | L2 |
| [n-scaling-test-matrix.md](tools-automation/n-scaling-test-matrix.md) | N-scaling测试矩阵：调度/仲裁/选择类算法的参与者规模覆盖法 | L2 |
| [package-structure-leverage.md](tools-automation/package-structure-leverage.md) | 包结构杠杆效应：三层结构（定义层+导出层+兼容层）使新增功能成本从 O(n) 降至 O(1) | L1 |
| [parameterization-over-duplication.md](tools-automation/parameterization-over-duplication.md) | 参数化优于复制：提取公共函数时用参数抽象差异 | L1 |
| [path-discipline.md](tools-automation/path-discipline.md) | 高强度编辑中的路径与幂等性纪律：路径确认三步走+回滚备份规则，防止文件污染与不可恢复断裂 | L2 |
| [pattern-driven-refactoring.md](tools-automation/pattern-driven-refactoring.md) | 模式驱动重构（Pattern-Driven Refactoring） | - |
| [precision-over-recall.md](tools-automation/precision-over-recall.md) | 精度优先于召回率：破坏性工具零误报原则，"宁可不修不可错修"，三层安全保障 | L1 |
| [quoting-scope-limits.md](tools-automation/quoting-scope-limits.md) | 引号/包裹机制作用边界定律（Quoting Scope Limits） | L2 |
| [refactoring-hidden-bug-discovery.md](tools-automation/refactoring-hidden-bug-discovery.md) | 重构中隐藏 Bug 发现：重构真实 ROI = 消除重复 + 隐藏问题发现 + 结构基础 | L1 |
| [relative-path-pitfalls.md](tools-automation/relative-path-pitfalls.md) | 相对路径四类特殊踩坑案例：replace_all子串级联+归档深度计算错误+前缀误判+兄弟子目录交叉引用，用工具验证替代心算（2次验证，L3） | L3 |
| [saas-doc-extraction-adaptation-draft.md](tools-automation/saas-doc-extraction-adaptation-draft.md) | 企业SaaS云文档DOM提取适配方案（草案） | - |
| [search-replace-fragility.md](tools-automation/search-replace-fragility.md) | SearchReplace 并发脆弱性与大块替换策略：多轮 SearchReplace 可靠性指数级下降，大块替换用整体读写策略 | L2 |
| [semi-structured-parsing-complexity-budget.md](tools-automation/semi-structured-parsing-complexity-budget.md) | 半结构化解析复杂度预算模式（Semi-structured Parsing Complexity Budget） | - |
| [shared-lib-gravity.md](tools-automation/shared-lib-gravity.md) | 共享库引力定律：覆盖≥5概念域触发正反馈循环，覆盖面越大复用率越高，指导多脚本项目代码复用 | L2 |
| [signal-identification-four-step.md](tools-automation/signal-identification-four-step.md) | 信号识别四步法：人工Checklist→自动化工具转化方法论，规则翻译→信号评估→消歧设计→边界接受 | L2 |
| [spec-as-code-automated-gates.md](tools-automation/spec-as-code-automated-gates.md) | 规范即代码自动化门禁：将文档规范写成检查脚本作为提交强制门禁，而非靠人自觉遵守 | L1 |
| [tdd-static-analysis-five-test-suites.md](tools-automation/tdd-static-analysis-five-test-suites.md) | TDD测试五件套：静态分析工具TDD方法论——阳性/阴性/边界/CLI/集成五类测试，阴性测试防误报最重要 | L2 |
| [three-layer-separation-progressive-migration.md](tools-automation/three-layer-separation-progressive-migration.md) | 三层分离·渐进迁移 | L2-validated |
| [three-tier-tool-fallback.md](tools-automation/three-tier-tool-fallback.md) | 网页内容提取三级回退链（Three-Tier Web Content Extraction Fallback Chain） | L1 |
| [tool-automation-decision-model.md](tools-automation/tool-automation-decision-model.md) | 工具自动化决策模型：3 次手动触发评估 + 成本公式 + ROI 度量 + 熵分类体系 | L2 |
| [tool-bootstrap-effect.md](tools-automation/tool-bootstrap-effect.md) | 工具自举效应：dogfooding正反馈循环，使用工具→发现不足→增强工具→发现更多问题 | L1 |
| [tool-failure-three-tier-degradation.md](tools-automation/tool-failure-three-tier-degradation.md) | 工具故障三级降级策略：Level1委托sub-agent→Level2挖掘附带信息/替代工具→Level3基于已有知识推进，含defuddle常见故障处理、Windows环境注意事项，核心铁则"连续失败2次禁止第3次重试" | - |
| [tool-fix-triple-protection.md](tools-automation/tool-fix-triple-protection.md) | 工具修复三重防护模式（Tool Fix Triple Protection Pattern） | - |
| [tool-self-validation.md](tools-automation/tool-self-validation.md) | 工具自生验证：新linter提交前7项检查清单（自扫描→真阳性→误报过滤→信噪比→输出可用→CI兼容→边界场景） | L2 |
| [tool-workflow-composition.md](tools-automation/tool-workflow-composition.md) | 工具工作流组合：事前评估→事中操作→事后收尾→验证→门禁，组合价值>单个工具之和 | L1 |
| [toolchain-maturity.md](tools-automation/toolchain-maturity.md) | 工具链五阶段成熟度模型：手动检测→自动检测→自动修复→流程预防→门禁保障，含维度评估表与跃迁规律 | L1 |
| [validation-semantic-gap.md](tools-automation/validation-semantic-gap.md) | 验证层级语义缺口模式（Validation Semantic Gap） | L2 |

---

## governance-strategy — 治理与优先级策略

**核心关注点**：围绕体系化治理、优先级排序、问题分层解决、规范防护机制的决策模式。

**边界说明**：包含三层治理模型、治理层级优先级、问题解决三层跃迁、约定驱动创建、规范纵深防御、自指性规范体系、递进式需求澄清；不包含具体工具实现细节、文档原子化操作步骤或知识萃取流程。

| 模式文件 | 一句话说明 | 成熟度 |
|---------|-----------|-------|
| [adversarial-perspective-weighting.md](governance-strategy/adversarial-perspective-weighting.md) | V阶段对抗审查「用户视角优先」权重分配模式 | L1 |
| [amphibious-positioning-model.md](governance-strategy/amphibious-positioning-model.md) | 两栖定位模型：通过资产清单+泛化路径图+落地案例三支柱支撑双重定位 | L1 |
| [architecture-over-algorithm.md](governance-strategy/architecture-over-algorithm.md) | 信息架构优先于算法补全：结构决定连接 | L1 |
| [asset-reuse-last-mile-integration-guide.md](governance-strategy/asset-reuse-last-mile-integration-guide.md) | 资产复用最后一公里：配套集成指南 | L1-实验性 |
| [automated-stats-three-defense-lines.md](governance-strategy/automated-stats-three-defense-lines.md) | 自动化统计三防线模式：路径校验→环比告警→人工复盘 | L1 |
| [availability-heuristic-structural-guard.md](governance-strategy/availability-heuristic-structural-guard.md) | 可得性启发结构性防范模式（Availability Heuristic Structural Guard） | L1 |
| [axiom-system-consistency-principle.md](governance-strategy/axiom-system-consistency-principle.md) | 公理系统一致性第一性原理（Axiom System: Consistency Enables Composability） | L2 |
| [bootstrap-driven-self-evolution.md](governance-strategy/bootstrap-driven-self-evolution.md) | 规范自举性驱动持续演化：达到自举点（分类/模板/检查/复盘/导航全部闭环）后项目进入持续演化阶段，里程碑从"功能完成"变为"能力建立"（793次提交验证） | L2 |
| [bottleneck-first-refactoring.md](governance-strategy/bottleneck-first-refactoring.md) | 瓶颈优先重构法：按全局瓶颈而非实施难度排序重构优先级 | L2 |
| [bounded-iteration-budget.md](governance-strategy/bounded-iteration-budget.md) | 有界迭代预算：长时程自主系统的强制收敛契约 | L1-draft |
| [capability-replication-boundary.md](governance-strategy/capability-replication-boundary.md) | 能力复制边界判断法 | L1 |
| [chapter-type-tiered-file-size.md](governance-strategy/chapter-type-tiered-file-size.md) | 章节类型分层文件大小策略：按概念型/API参考型/实战案例型/参考型分层设置行数上限，替代一刀切的300行限制 | L1 |
| [cognitive-practice-gap-recursive-defense.md](governance-strategy/cognitive-practice-gap-recursive-defense.md) | 认知偏差递归防御体系（Cognitive Practice Gap Recursive Defense） | L2 |
| [combination-value-triple-test.md](governance-strategy/combination-value-triple-test.md) | 组合价值评估三原则（Combination Value Triple Test） | L1 |
| [command-knowledge-link.md](governance-strategy/command-knowledge-link.md) | 指令集↔知识库关联对应性前提（Command-Knowledge Link Pattern） | L2 |
| [command-vs-skill-boundary.md](governance-strategy/command-vs-skill-boundary.md) | 指令集与Skill边界判断（Command vs Skill Boundary） | L1 |
| [commit-quality-gate-staging-inspection.md](governance-strategy/commit-quality-gate-staging-inspection.md) | 提交质量门三查暂存法：git status→git diff逐文件审查→显式add，禁止git add .，在add阶段防止脏提交混入 | L2 |
| [compliance-driven-rule-building.md](governance-strategy/compliance-driven-rule-building.md) | 合规驱动规则建设五步法 | L1 |
| [config-persistence-full-chain-coverage.md](governance-strategy/config-persistence-full-chain-coverage.md) | 配置持久化全链路覆盖模式 | L1 实验性 |
| [convention-driven-creation.md](governance-strategy/convention-driven-creation.md) | 约定驱动创建模型，先读范例提取模板再填充内容，零结构决策 | L2 |
| [cross-wiki-reference-directory-first.md](governance-strategy/cross-wiki-reference-directory-first.md) | 跨Wiki引用目录优先验证：创建跨wiki引用前必须先读取目标wiki的00-overview.md确认章节编号，用事实替代假设；5次验证4次复用，已达L3升级门槛 | L2 |
| [data-validation-four-checks.md](governance-strategy/data-validation-four-checks.md) | 量化数据验证四查法 | L2 |
| [defensive-programming-first-principles.md](governance-strategy/defensive-programming-first-principles.md) | 防御性编程第一性原理：7项根因原则 | L2 |
| [dev-env-dockerfile-optimization.md](governance-strategy/dev-env-dockerfile-optimization.md) | 开发环境Dockerfile优化法：优先排序而非最小化，整合变化频率分层+.dockerignore三重价值+层缓存涟漪效应 | L1 |
| [docker-canonical-build-environment.md](governance-strategy/docker-canonical-build-environment.md) | Docker 作为规范构建环境——构建验证的黄金标准 | L2-validated |
| [dual-mode-submodule-governance.md](governance-strategy/dual-mode-submodule-governance.md) | 双模式子模块治理框架：分类管理 Git Submodule | L2 |
| [dual-quality-gate-subagent.md](governance-strategy/dual-quality-gate-subagent.md) | 子代理双重质量门模式（事前约束+事后校验） | L2 |
| [dual-track-metadata-consistency.md](governance-strategy/dual-track-metadata-consistency.md) | 双轨元数据一致性模式：Frontmatter-正文漂移与TOML双星同步 | L1 |
| [dual-track-progressive-evolution.md](governance-strategy/dual-track-progressive-evolution.md) | 双轨演进制：在依赖生态不成熟阶段内部化实现先行、外部依赖后置，按就绪度渐进切换轨道 | L1 |
| [duplication-interest-model.md](governance-strategy/duplication-interest-model.md) | 重复代码利息模型：复制一时爽，维护火葬场 | L1 |
| [elastic-workflow-classification.md](governance-strategy/elastic-workflow-classification.md) | 弹性流程分级：按变更风险选择流程路径 | L2 |
| [entropy-law-automation-principle.md](governance-strategy/entropy-law-automation-principle.md) | 熵增定律自动化第一性原理（Entropy Law: Automation Against Chaos） | L2 |
| [exemption-mechanism-legalization.md](governance-strategy/exemption-mechanism-legalization.md) | 豁免机制合法化：通过显式标注（前缀/路径/标记）创建合法例外通道，6设计要素（标注+隔离+生命周期+主干隔离+审计+运行时识别），4次验证（baby-前缀/.temp目录/skip审批/选择性归档） | L2 |
| [explainer-self-violation-effect.md](governance-strategy/explainer-self-violation-effect.md) | 讲解自犯效应（Explainer Self-Violation Effect） | L2 |
| [fail-loud-over-silent-fallback.md](governance-strategy/fail-loud-over-silent-fallback.md) | 显式报错优于静默降级：自动化系统故障显性化原则 | L1 |
| [feedback-wording-diagnosis.md](governance-strategy/feedback-wording-diagnosis.md) | 用户反馈措辞诊断模式（Feedback Wording Diagnosis） | L1 |
| [file-creation-precheck-pattern.md](governance-strategy/file-creation-precheck-pattern.md) | 文件创建前置检查模式：三步检查流程（确定归属目录→确定文件名格式→自动化验证）确保文件创建合规 | L3 |
| [first-principles-debugging.md](governance-strategy/first-principles-debugging.md) | 第一性原理调试法（First-Principles Debugging） | L2 |
| [first-principles-decision-quality-gate.md](governance-strategy/first-principles-decision-quality-gate.md) | 第一性原理决策质量门禁（First Principles Decision Quality Gate） | L1 |
| [five-factor-skill-format-standardization.md](governance-strategy/five-factor-skill-format-standardization.md) | 五要素Skill格式标准化：从通用工具文档到项目标准Skill的改造 | L1 |
| [five-layer-governance-architecture.md](governance-strategy/five-layer-governance-architecture.md) | 五层治理体系架构模式 | L2 |
| [format-evidence-over-memory-pattern.md](governance-strategy/format-evidence-over-memory-pattern.md) | 格式证据优先于记忆模式：创建新文件前必须读取同目录现有文档确认格式，实际文档是唯一权威来源 | L2 |
| [four-dimension-margin-framework.md](governance-strategy/four-dimension-margin-framework.md) | 四维留余框架：不确定环境下长期存续的冗余管理策略 | L2 |
| [four-negatives-external-dependency.md](governance-strategy/four-negatives-external-dependency.md) | 外部依赖四不原则+零依赖原则：不侵入/不直引/不跟版/不裸考/不滥引，150+脚本零第三方依赖跨平台验证（L3标准化） | L3 |
| [governance-four-layer-progressive.md](governance-strategy/governance-four-layer-progressive.md) | 治理基建四层递进模型 | L2 |
| [governance-three-stage-evolution.md](governance-strategy/governance-three-stage-evolution.md) | 治理演化三阶段：修复→预防→闭环，禁止跳过任何阶段；跳过预防导致问题复发，多个场景验证（Mermaid/断链/事实漂移） | L2 |
| [governance-tier-priority.md](governance-strategy/governance-tier-priority.md) | 治理层级优先级排序：🔴防复发→🟡提效率→🟢拓边界，与战术层投入估算互补 | L1 |
| [harness-architecture-layered-model.md](governance-strategy/harness-architecture-layered-model.md) | Harness架构分层模式 | L1 |
| [immutable-constraint-documentation.md](governance-strategy/immutable-constraint-documentation.md) | 不可变约束清单模式：每条约束包含内容+历史踩坑原因+代码位置三要素，踩坑经验工程化沉淀 | - |
| [implement-review-harden-sop.md](governance-strategy/implement-review-harden-sop.md) | "实现→审查→加固"三段式SOP：核心机制类代码开发流程 | L2 |
| [index-over-memorization.md](governance-strategy/index-over-memorization.md) | 索引优于记忆原则（Index Over Memorization Principle） | L2 |
| [knowledge-crystallization-second-validation-sop.md](governance-strategy/knowledge-crystallization-second-validation-sop.md) | 知识沉淀二次验证SOP | L1 |
| [knowledge-dual-layer-architecture.md](governance-strategy/knowledge-dual-layer-architecture.md) | 知识沉淀「中间产物→质量门→最终产出」双层架构模式 | L1 |
| [knowledge-lifecycle-extract-archive-delete.md](governance-strategy/knowledge-lifecycle-extract-archive-delete.md) | 知识资产「萃取→归档→删除」生命周期闭环模式 | L1-draft |
| [knowledge-to-command-pipeline.md](governance-strategy/knowledge-to-command-pipeline.md) | 知识库→指令集转化管道（Knowledge-to-Command Pipeline） | L1 |
| [layered-chained-spec.md](governance-strategy/layered-chained-spec.md) | 分层链式规格：AI 编程工作流的阶段分离与链式传递 | L1.5 |
| [layered-priority-dimension-reduction.md](governance-strategy/layered-priority-dimension-reduction.md) | 分层分级降维模式（Layered Priority Dimension Reduction） | L1 |
| [layered-repair-verification.md](governance-strategy/layered-repair-verification.md) | 分层修复验证法（Layered Repair Verification） | L1 |
| [learn-validate-adopt.md](governance-strategy/learn-validate-adopt.md) | Learn-Validate-Adopt：外部标准采用三步法 | L1 |
| [local-dependency-cache-proxy.md](governance-strategy/local-dependency-cache-proxy.md) | 本地依赖缓存代理体系：多层缓存加速构建 | L1-draft |
| [meta-bootstrap-action-plan.md](governance-strategy/meta-bootstrap-action-plan.md) | 元方法论自举行动计划——七概念触发匹配CLI工具 | L1 |
| [meta-methodology-bootstrap.md](governance-strategy/meta-methodology-bootstrap.md) | 元方法论自举模式 | L2 |
| [meta-retrospective-closed-loop.md](governance-strategy/meta-retrospective-closed-loop.md) | 元复盘闭环：交付后主动元复盘→纠偏→行动落地→工具化五步闭环，防止错误入库并加速方法论资产周转 | L1 |
| [meta-review-in-command.md](governance-strategy/meta-review-in-command.md) | 指令集元审查设计模式（Meta-Review-in-Command） | L1 |
| [methodology-constructive-validation.md](governance-strategy/methodology-constructive-validation.md) | 方法论构造性验证 | L2 |
| [methodology-reflexivity-test.md](governance-strategy/methodology-reflexivity-test.md) | 方法论自反性测试（Methodology Reflexivity Test） | L2 |
| [milestone-breakthrough-assetization-process.md](governance-strategy/milestone-breakthrough-assetization-process.md) | 专项突破资产化标准流程 | L1-experimental |
| [module-size-bug-correlation.md](governance-strategy/module-size-bug-correlation.md) | 模块大小-Bug密度非线性相关模式（Module Size-Bug Density Correlation） | - |
| [mvp-unvalidated-code-debt.md](governance-strategy/mvp-unvalidated-code-debt.md) | MVP未验证代码债务模式（MVP Unvalidated Code Debt） | - |
| [no-touch-list.md](governance-strategy/no-touch-list.md) | 不重构清单：明确划定不改动边界防止范围蔓延 | L2 |
| [nonlinear-correction-cost.md](governance-strategy/nonlinear-correction-cost.md) | 缺陷放大与非线性纠偏成本模式（Defect Amplification & Nonlinear Correction Cost） | L2 |
| [orchestration-execution-layering.md](governance-strategy/orchestration-execution-layering.md) | 编排-执行分层法 | L1 |
| [P-AGENT-SELECT-001-agent-platform-selection-framework.md](governance-strategy/P-AGENT-SELECT-001-agent-platform-selection-framework.md) | 企业级AI Agent平台9维度选型评估框架 | L1 |
| [P-AGENT-SELECT-001-agent-platform-selection-scorecard.md](governance-strategy/P-AGENT-SELECT-001-agent-platform-selection-scorecard.md) | AI Agent 平台选型 9 维度评分卡（可直接套用） | - |
| [P-DEMO-TO-PROD-003-demo-to-prod-checklist.md](governance-strategy/P-DEMO-TO-PROD-003-demo-to-prod-checklist.md) | 智能体从Demo到生产的12项检查清单 | L1 |
| [P-LEGACY-AI-UPGRADE-002-legacy-ai-upgrade-sop.md](governance-strategy/P-LEGACY-AI-UPGRADE-002-legacy-ai-upgrade-sop.md) | 存量业务系统智能化改造5步SOP | L1 |
| [P-SPEC-AC-DUAL-TRACK-004-spec-hard-soft-ac-dual-track-acceptance.md](governance-strategy/P-SPEC-AC-DUAL-TRACK-004-spec-hard-soft-ac-dual-track-acceptance.md) | 知识类项目Spec「硬软AC双轨验收」模式 | L1 |
| [pattern-tooling-progressive-extraction.md](governance-strategy/pattern-tooling-progressive-extraction.md) | 模式渐进式工具提取：L1实验阶段即可提取轻量检查清单/模板，工具使用反哺模式验证，打破"等L2才工具化"的死循环 | L1 |
| [performance-optimization-five-step-method.md](governance-strategy/performance-optimization-five-step-method.md) | 性能优化五步法：测量→诊断→优化→验证→萃取 | L1-实验性 |
| [phased-incremental-optimization.md](governance-strategy/phased-incremental-optimization.md) | 分层渐进优化策略：安全场景先行+复杂场景后置的风险控制方法论 | L2-validated |
| [phased-rollout-validation.md](governance-strategy/phased-rollout-validation.md) | 方法论推广渐进式验证模式 | L2 |
| [plugin-bridge-standard-integration.md](governance-strategy/plugin-bridge-standard-integration.md) | 插件桥接规范集成法：以插件+技能叠加方式把工作区规范接入已有Agent平台，目录感知自动生效+verify可判定（Hermes-SpecWeave集成验证） | L1 |
| [practice-gap-recursive-practice.md](governance-strategy/practice-gap-recursive-practice.md) | 践行鸿沟与递归践行定律（Practice Gap & Recursive Practice Law） | L3 |
| [process-vs-experience-intuition.md](governance-strategy/process-vs-experience-intuition.md) | 流程合规 vs 经验直觉区分模式（Process Compliance vs Experience Intuition） | L2 |
| [progressive-requirement-clarification.md](governance-strategy/progressive-requirement-clarification.md) | 递进式需求澄清：先定范围再定细节的两轮策略，互斥选项+互补选项设计规范 | L2 |
| [prove-usefulness-check.md](governance-strategy/prove-usefulness-check.md) | 证明有用性自检模式：好的组件不可减去，去掉后系统功能受损才保留 | L2 |
| [python-stdlib-systematic-optimization-four-steps.md](governance-strategy/python-stdlib-systematic-optimization-four-steps.md) | Python 标准库系统优化四步法：基线采集→能力映射→量化验证→测试兜底 | L1-draft |
| [quality-asset-accumulation-loop.md](governance-strategy/quality-asset-accumulation-loop.md) | 质量资产沉淀闭环模式（Quality Asset Accumulation Loop） | L1 |
| [quality-assurance-three-layer-model.md](governance-strategy/quality-assurance-three-layer-model.md) | 质量保证三层分工模型（Quality Assurance Three-Layer Model） | L2 |
| [reference-as-trigger.md](governance-strategy/reference-as-trigger.md) | 引用即触发协作模式：用户选中行号触发精确实施 | L2 |
| [risk-transfer-unintended-consequences.md](governance-strategy/risk-transfer-unintended-consequences.md) | 风险转移非意图后果模型 | L1 |
| [role-minimization-principle.md](governance-strategy/role-minimization-principle.md) | 角色最小化原则（RACI扩展优先于角色新增） | L1 |
| [root-cause-diagnosis.md](governance-strategy/root-cause-diagnosis.md) | 根因诊断模式：收到纠错反馈时先暂停追溯知识缺口，再全量修正，避免表层症状修补循环 | L2 |
| [self-referential-spec-system.md](governance-strategy/self-referential-spec-system.md) | 自指性规范体系：规范定义自身，形成"规范即测试"效应——规范变更触发全景验证 | L1 |
| [session-boundary-commit.md](governance-strategy/session-boundary-commit.md) | 原子提交会话边界原则：双重单一职责（功能+会话），归属分析→会话筛选→功能分组→排除确认 | L1 |
| [seven-concepts-adversarial-review.md](governance-strategy/seven-concepts-adversarial-review.md) | 七概念方法论自举对抗性审查报告 | L2 |
| [seven-concepts-core-workflows.md](governance-strategy/seven-concepts-core-workflows.md) | 七概念五种核心组合应用流程 | L2 |
| [seven-concepts-interaction-spec.md](governance-strategy/seven-concepts-interaction-spec.md) | 七概念交互机制与接口规范 | L2 |
| [seven-concepts-methodology-index.md](governance-strategy/seven-concepts-methodology-index.md) | 七概念方法论体系索引 | L2 |
| [seven-concepts-positioning-model.md](governance-strategy/seven-concepts-positioning-model.md) | 七概念本质定位与五层层级模型 | L2 |
| [seven-concepts-quality-standards.md](governance-strategy/seven-concepts-quality-standards.md) | 七概念方法论质量标准与检查清单 | L2 |
| [seven-concepts-quick-reference.md](governance-strategy/seven-concepts-quick-reference.md) | 七概念方法论统一速查手册 | L2 |
| [seven-concepts-retrospective-report.md](governance-strategy/seven-concepts-retrospective-report.md) | 七概念方法论体系-项目全面系统性复盘报告 | L2 |
| [seven-concepts-trigger-decision-tree.md](governance-strategy/seven-concepts-trigger-decision-tree.md) | 七概念组合触发决策树 | L2 |
| [short-command-patterns.md](governance-strategy/short-command-patterns.md) | 短指令模式库：登记已验证的 AI 协作快捷指令 | L2 |
| [simple-task-high-risk.md](governance-strategy/simple-task-high-risk.md) | 简单任务高风险定律（Simple Task High-Risk Law） | L2 |
| [skill-migration-position-governance.md](governance-strategy/skill-migration-position-governance.md) | Skill迁移位置治理：统一Skill存放位置的五步标准化流程 | L1 |
| [spec-discoverability-guarantee.md](governance-strategy/spec-discoverability-guarantee.md) | 规范可发现性保障模式：三层映射模型（AGENTS.md引用→路由表条目→自动化脚本）确保规范不会"存在但不可发现" | L1 |
| [spec-level-defense-in-depth.md](governance-strategy/spec-level-defense-in-depth.md) | 规范层纵深防御模型，权限定义+验证机制+防滥用+审计追溯四维防护 | L2 |
| [spec-reference-validation.md](governance-strategy/spec-reference-validation.md) | Spec引用验证通用原则（Specification Reference Validation Pattern） | L2 |
| [spec-triple-sync.md](governance-strategy/spec-triple-sync.md) | 规范三同步原则：新规范发布必须完成①总览引用②入口更新③存量迁移示范，解决"规范悬空"问题 | L2 |
| [strong-constraint-self-check.md](governance-strategy/strong-constraint-self-check.md) | 强约束语言自检启发式 | L1 |
| [structure-first-extension.md](governance-strategy/structure-first-extension.md) | 结构阅读先行：扩展前先完整阅读包结构，同概念域追加、异概念域新建 | L3 |
| [style-anchoring-consistency.md](governance-strategy/style-anchoring-consistency.md) | 风格锚定一致性保证法 | L1 |
| [subagent-responsibility-layering.md](governance-strategy/subagent-responsibility-layering.md) | 子代理职责分层模式 | L1 |
| [submodule-directory-convention.md](governance-strategy/submodule-directory-convention.md) | 子模块目录约定模式（Submodule Directory Convention） | - |
| [symmetric-directory-structure.md](governance-strategy/symmetric-directory-structure.md) | 对称目录结构设计（Symmetric Directory Structure） | L3 |
| [task-type-first-indexing.md](governance-strategy/task-type-first-indexing.md) | 任务类型优先索引模式（Task-Type-First Indexing） | L1 |
| [tech-selection-three-checks.md](governance-strategy/tech-selection-three-checks.md) | 技术选型「偏好-惯例-本质」三查法（Preference-Convention-Essence Three Checks） | L2 |
| [technical-debt-workaround-tracking.md](governance-strategy/technical-debt-workaround-tracking.md) | 权宜之计技术债追踪（Technical Debt Workaround Tracking） | L1 |
| [template-cross-platform-validation.md](governance-strategy/template-cross-platform-validation.md) | 模板跨平台验证模式（Template Cross-Platform Validation） | - |
| [template-placeholder-granularity-design.md](governance-strategy/template-placeholder-granularity-design.md) | 模板占位符的粒度设计原则 | L2 |
| [test-coverage-diminishing-returns.md](governance-strategy/test-coverage-diminishing-returns.md) | 测试覆盖率边际收益递减拐点：70%处策略转换，从追求覆盖率数字转向关注关键路径测试质量 | L1 |
| [three-layer-rule-enforcement.md](governance-strategy/three-layer-rule-enforcement.md) | 规则落地三层模型：定义+痕迹+验证 | L2 |
| [three-layer-spec-constraint.md](governance-strategy/three-layer-spec-constraint.md) | 规范约束三层次模型：规则定义层→路由发现层→自动化验证层，确保规范不会"存在但不可发现" | L2 |
| [three-level-problem-solving.md](governance-strategy/three-level-problem-solving.md) | 问题解决三层跃迁：L1症状治疗→L2病因根治→L3系统免疫，架构师思考L3 | L1 |
| [three-stage-content-validation.md](governance-strategy/three-stage-content-validation.md) | 三段式内容验证模式：任务级→专项→终验 | L1 |
| [three-state-decision.md](governance-strategy/three-state-decision.md) | 三态决策模式：做/明确不做/推迟（Do/Explicitly-No/Defer） | L1 |
| [three-tier-board-system.md](governance-strategy/three-tier-board-system.md) | 三层看板体系：全局看板→主题看板→创建模板，覆盖看-管-建全生命周期，含自维护闭环 | L1 |
| [three-tier-governance.md](governance-strategy/three-tier-governance.md) | 三层治理模型（原子化→自动化→验证），含实施检查清单（150+脚本验证，L3标准化） | L3 |
| [three-zone-boundary-model.md](governance-strategy/three-zone-boundary-model.md) | 三区域边界模型：主项目区/接口层/外部依赖区主权划分，定义允许/禁止操作清单 | L2 |
| [toolchain-five-stage-evolution.md](governance-strategy/toolchain-five-stage-evolution.md) | 工具链项目五阶段演进路径：脚本堆砌→模块化→工作流标准化→测试体系→基础设施优化，自底向上演进 | L1 |
| [trilemma-architectural-resolution.md](governance-strategy/trilemma-architectural-resolution.md) | 三角困境→架构级解决框架：三步法（困境识别→根因分析→架构重定义），区分本质矛盾（取舍）与架构遗留（突破），从目标场景倒推架构重设计，1次验证（mainecoon成本/速度/时长困境突破） | L1 |
| [two-dimension-document-governance.md](governance-strategy/two-dimension-document-governance.md) | 文档治理双维度检查模型：位置维度（目录归属）+ 命名维度（kebab-case），双重违规暴露流程漏洞 | L2 |
| [two-phase-development.md](governance-strategy/two-phase-development.md) | 两阶段开发模式（Two-Phase Development: Validate First, Optimize Later） | - |
| [vendor-lifecycle-governance.md](governance-strategy/vendor-lifecycle-governance.md) | 第三方供应商全生命周期治理模型 | L1 |
| [version-ripple-grep-sweep.md](governance-strategy/version-ripple-grep-sweep.md) | 版本涟漪Grep清扫模式：单点更新后的多点引用同步 | L2 |
| [wiki-dual-track-frontmatter.md](governance-strategy/wiki-dual-track-frontmatter.md) | Wiki双轨Frontmatter规范：单文件wiki和原子化wiki使用不同字段集，模板/检查清单必须类型感知，禁止混用字段 | L1 |
| [wiki-pre-creation-three-checks.md](governance-strategy/wiki-pre-creation-three-checks.md) | Wiki创作三查流程模式（Wiki Pre-Creation Three Checks Pattern） | L3 |

---

## ai-collaboration — AI协作与提示词设计

**核心关注点**：围绕AI Skill产品化设计、人机协作交互模式、提示词工程策略、输出行为规范的模式。

**边界说明**：包含AI Skill判断层设计、双语提示词分层、双区开发模型、输出行为四维约束、上下文渐进式披露、风格-创意分离控制、症状-处方QA闭环、团队共享AI同事、主动介入Agent、模块级agents扩展继承、references渐进式披露、Gotchas领域特化、安全信任设计、源码锚点二次校验、契约文档协调中枢、输出格式-协作能力映射、生态壁垒评估；不包含通用文档模式、产品增长策略或工具工程实现。

| 模式文件 | 一句话说明 | 成熟度 |
|---------|-----------|-------|
| [action-first-output-paradigm.md](ai-collaboration/action-first-output-paradigm.md) | 行动优先Agent输出模式 | L2 已验证 |
| [adversarial-review-prompt-pattern.md](ai-collaboration/adversarial-review-prompt-pattern.md) | 对抗式审查Prompt模式：多Agent并发+攻击者视角（安全/性能/边界/时序四类攻击者），与第一性原理构成"生成-验证"闭环，保证AI生成代码稳健上线 | L2 |
| [ai-agent-workspace-handbook.md](ai-collaboration/ai-agent-workspace-handbook.md) | AI Agent 工作手册模式：.agents/ 目录存放面向智能体的架构/约束/命令/排障文档，让 AI 高效参与项目 | - |
| [ai-multimodal-fullstack-dev-loop.md](ai-collaboration/ai-multimodal-fullstack-dev-loop.md) | AI 多模态全栈开发闭环（AI Multimodal Full-Stack Development Loop） | - |
| [ai-skill-judgment-layer.md](ai-collaboration/ai-skill-judgment-layer.md) | AI Skill 判断层设计模式：工具负责生产，判断负责选择，三层能力模型 | L2 |
| [ai-transparency-over-cleverness.md](ai-collaboration/ai-transparency-over-cleverness.md) | AI系统透明优先原则（Transparency Over Cleverness Principle / Human-in-the-Loop by Default） | L2 |
| [ambient-proactive-agent.md](ai-collaboration/ambient-proactive-agent.md) | 主动介入 Agent 模式：AI 从被动响应到主动介入，主动监测→主动介入→主动汇报，异步执行后主动通知 | - |
| [batched-creation-independent-review.md](ai-collaboration/batched-creation-independent-review.md) | 分批创作+独立质检模式：长文档分N批委托子代理创作，独立质检子代理按checklist统一检查，突破上下文限制并捕获创作者自查盲区 | L2 |
| [bilingual-prompt-engineering.md](ai-collaboration/bilingual-prompt-engineering.md) | 双语提示词工程：按目标模型最优语言做提示词分层，Agent 推理语言与模型执行语言各司其职 | L2 |
| [context-lifecycle-layering.md](ai-collaboration/context-lifecycle-layering.md) | 上下文生命周期分层管理模式 | L2 |
| [context-recovery-protocol.md](ai-collaboration/context-recovery-protocol.md) | Context 恢复协议重执行模式：收到会话历史摘要/中断恢复时必须重新执行完整启动协议 | L2 |
| [dialog-agent-four-layer-evaluation.md](ai-collaboration/dialog-agent-four-layer-evaluation.md) | 对话Agent四层评测模式（Dialog Agent Four-Layer Evaluation） | L1 |
| [dual-zone-development-model.md](ai-collaboration/dual-zone-development-model.md) | 双区开发模型（非正式区→质量门禁→正式区） | L2 |
| [ecosystem-barrier-evaluation.md](ai-collaboration/ecosystem-barrier-evaluation.md) | 生态壁垒评估框架：AI Agent的长期竞争力取决于底层生态的深度和广度，生态深度不可速成，评估应看生态而非仅看模型能力 | L2 |
| [edit-verify-separation.md](ai-collaboration/edit-verify-separation.md) | 编辑-验证分离模式 | L2 |
| [external-content-fact-verification.md](ai-collaboration/external-content-fact-verification.md) | 外部内容事实验证 | L2 |
| [external-tech-article-learning-closed-loop.md](ai-collaboration/external-tech-article-learning-closed-loop.md) | 外部技术文章学习三阶段闭环（LAV模型） | L1 |
| [file-existence-verification-gate.md](ai-collaboration/file-existence-verification-gate.md) | 文件存在性验证门模式（File Existence Verification Gate） | L2 |
| [fine-grained-least-privilege.md](ai-collaboration/fine-grained-least-privilege.md) | 细粒度最小权限模式：权限四级拆解(L0-L3)+授权生命周期管理(默认最小→按需申请→用完收回)，PoLP原则在Agent系统中的操作化落地 | L1 |
| [first-citizen-abstraction.md](ai-collaboration/first-citizen-abstraction.md) | 一等公民抽象模式 | - |
| [first-principles-prompt-pattern.md](ai-collaboration/first-principles-prompt-pattern.md) | 第一性原理Prompt模式：七个字打断AI类比推理快思考，逼其回到基本事实重新推导，修BUG治本+架构设计从本质出发，与对抗式审查构成"生成-验证"闭环 | L3 |
| [generation-validation-closed-loop.md](ai-collaboration/generation-validation-closed-loop.md) | 生成-验证闭环模式（Generation-Validation Closed Loop） | L2 |
| [gotchas-domain-specialization.md](ai-collaboration/gotchas-domain-specialization.md) | Gotchas 领域特化：在 SKILL-TEMPLATE.md 通用 Gotchas 框架基础上，为模块级 Skill 新增领域特化小节（12.4），补充模块特有陷阱与反直觉行为 | L1 |
| [honest-limitation-acknowledgment.md](ai-collaboration/honest-limitation-acknowledgment.md) | 诚实承认局限性信任构建策略：三步法（主动承认当前局限→说明改进方向与时间表→用局限性衬托核心优势），将局限性从信任减分项转化为信任加分项，与用户主权默认模式互补，1次验证（mainecoon文章可信度构建） | L1 |
| [human-ai-collaboration-70-30-rule.md](ai-collaboration/human-ai-collaboration-70-30-rule.md) | 人机协作70/30分工定律（Human-AI Collaboration 70/30 Rule） | L2 |
| [human-in-the-loop-augmentation.md](ai-collaboration/human-in-the-loop-augmentation.md) | 「辅助人工」而非「全自动」的人机协作设计 | L2 |
| [isolation-over-sharing.md](ai-collaboration/isolation-over-sharing.md) | 隔离优于共享模式 | - |
| [layered-caching-pattern.md](ai-collaboration/layered-caching-pattern.md) | 分层缓存模式 | L2-validated |
| [lazy-loading-pattern.md](ai-collaboration/lazy-loading-pattern.md) | 按需加载懒加载模式 | L2-validated |
| [llm-token-optimization-anti-patterns.md](ai-collaboration/llm-token-optimization-anti-patterns.md) | LLM Token优化反模式集 | L2-validated |
| [mapreduce-divide-conquer.md](ai-collaboration/mapreduce-divide-conquer.md) | 分层分治MapReduce模式 | L2-validated |
| [markdown-as-interface.md](ai-collaboration/markdown-as-interface.md) | Markdown即接口：用Markdown同时承载人类阅读与机器调用，三层架构（L0叙事/L1接口/L2检查清单） | L4 |
| [medium-task-merged-delegation-strategy.md](ai-collaboration/medium-task-merged-delegation-strategy.md) | 中等规模任务合并委派策略：紧耦合+产出<500行的相邻任务合并给单子代理递进执行，减少上下文传递损失、保证风格统一、降低整合成本 | L2 |
| [module-level-agents-extension.md](ai-collaboration/module-level-agents-extension.md) | 模块级 .agents/ 扩展模式：子模块通过 extends 继承父角色，仅补充模块特化职责和技能，避免重复定义和维护成本翻倍 | L1 |
| [navigation-hub-filename-contract.md](ai-collaboration/navigation-hub-filename-contract.md) | 导航枢纽文件名契约：全局文件清单vs局部清单，并行sub-agent任务中导航枢纽文件需传递全部章节文件名（L2扩展：契约文档作为协调中枢） | L2 |
| [non-intrusive-security-ux.md](ai-collaboration/non-intrusive-security-ux.md) | 安全不打扰UX模式：默认安全但验证只在风险场景触发，风险分级响应矩阵+信任累积机制，平衡安全与效率 | L1 |
| [output-behavior-specification.md](ai-collaboration/output-behavior-specification.md) | 输出行为规范：四维约束模型的第四维度——何时说话、说什么、说多少、什么时候沉默 | L2 |
| [output-format-collaboration-capability.md](ai-collaboration/output-format-collaboration-capability.md) | 输出格式-协作能力映射：输出格式决定协作可能性，云文档链接>真文件格式>Markdown>纯文本，格式即承诺 | - |
| [pre-decision-three-checks.md](ai-collaboration/pre-decision-three-checks.md) | 决策前三查检查清单（Pre-Decision Three Checks） | L2 |
| [progressive-context-disclosure.md](ai-collaboration/progressive-context-disclosure.md) | 上下文渐进式披露：入口索引 + 按需加载，工作流阶段绑定加载条件，节省 60%+ 上下文消耗 | L2 |
| [progressive-optimization-pattern.md](ai-collaboration/progressive-optimization-pattern.md) | 渐进式优化模式 | L2-validated |
| [progressive-templating.md](ai-collaboration/progressive-templating.md) | 渐进式模板化：硬编码验证→模板分离→多类型扩展三阶段 | L1 |
| [prompt-to-product-seven-steps.md](ai-collaboration/prompt-to-product-seven-steps.md) | 提示词到产品七步法 | L1 |
| [ps5-defensive-prompt.md](ai-collaboration/ps5-defensive-prompt.md) | PS5防御性Prompt模板模式（PS5-Defensive-Prompt） | L1 |
| [quality-cost-dynamic-balance.md](ai-collaboration/quality-cost-dynamic-balance.md) | 质量-成本动态平衡模式 | L2-validated |
| [references-progressive-disclosure.md](ai-collaboration/references-progressive-disclosure.md) | references/ 渐进式披露：通过 references/index.md 引用已有知识文档，避免 SKILL.md 中内容复制导致的信息不一致和维护成本翻倍 | L1 |
| [seven-concepts-wiki-creation-methodology.md](ai-collaboration/seven-concepts-wiki-creation-methodology.md) | 七概念驱动的技术Wiki创作方法论 | L1 |
| [skill-discovery-protocol.md](ai-collaboration/skill-discovery-protocol.md) | Skill 发现协议增强 SOP：三层发现机制（Onboarding/任务执行/新Skill注册）快速定位能力 | L1 |
| [skill-five-elements-model.md](ai-collaboration/skill-five-elements-model.md) | Skill 五要素模型：定义高质量 AI Skill 必须包含的五个核心要素 | L1 |
| [skill-progressive-disclosure-encapsulation.md](ai-collaboration/skill-progressive-disclosure-encapsulation.md) | Skill渐进式披露封装模式（SKILL.md Metadata + Python Executor） | L1 |
| [skill-standardized-workflow-pattern.md](ai-collaboration/skill-standardized-workflow-pattern.md) | Skill标准化操作流程模式（Four Principles for Workflow Skill Design） | L1 |
| [skill-three-layer-value-model.md](ai-collaboration/skill-three-layer-value-model.md) | AI Skill 三层价值模型：能力层快速贬值，判断层和风格层是持续竞争优势 | L2 |
| [socratic-questioning-correction.md](ai-collaboration/socratic-questioning-correction.md) | 苏格拉底提问纠错模式（Socratic Questioning Correction） | L1 |
| [source-anchor-verification-protocol.md](ai-collaboration/source-anchor-verification-protocol.md) | 源码锚点二次校验协议：研究阶段产出的行号/API签名/文件路径须标注校验状态（✅已校验/⚠️未校验/🔍待校验），编写sub-agent根据状态决策是否二次校验 | L1 |
| [spec-driven-batch-doc-generation.md](ai-collaboration/spec-driven-batch-doc-generation.md) | Spec驱动+知识库驱动的文档批量产出模式：知识库素材+统一模板+并行Agent+统一验证（L2扩展：研究-契约-编写三阶段） | - |
| [spec-driven-subagent-execution.md](ai-collaboration/spec-driven-subagent-execution.md) | Spec 驱动子代理执行模式 | - |
| [spec-mode-doc-creation-workflow.md](ai-collaboration/spec-mode-doc-creation-workflow.md) | Spec Mode文档创建工作流：前置规划（阶段0内容提取→阶段1规范阅读）→阶段2 Spec三件套→阶段3原子执行→阶段4即时验证→阶段5门禁验证，五阶段闭环 | L2 |
| [spec-stage7-independent-validation.md](ai-collaboration/spec-stage7-independent-validation.md) | Spec 模式第七阶段独立验证机制 | L1 |
| [style-creativity-separation-control.md](ai-collaboration/style-creativity-separation-control.md) | 风格-创意分离控制：正向约束控风格一致性 + 负向约束（禁止复刻清单）保创意多样性 | L2 |
| [subagent-atomic-task-template.md](ai-collaboration/subagent-atomic-task-template.md) | 子代理原子任务描述模板：六要素精确委托法（路径+frontmatter+大纲+导航+硬约束+Mermaid规则）消除歧义 | L2 |
| [subagent-git-three-prohibitions.md](ai-collaboration/subagent-git-three-prohibitions.md) | 子代理"三不准"执行规范（Subagent Git Three Prohibitions） | L1 |
| [symptom-prescription-qa.md](ai-collaboration/symptom-prescription-qa.md) | 症状-处方 QA 系统：故障诊断手册式 QA，每条症状对应可执行修改指令，Agent 可自主闭环 | L2 |
| [task-type-precheck-bias-defense.md](ai-collaboration/task-type-precheck-bias-defense.md) | 任务类型预检防偏差：对抗就近直觉偏差的防御机制，文件搜索前先做任务类型匹配 | L2 |
| [team-shared-ai-colleague.md](ai-collaboration/team-shared-ai-colleague.md) | 团队共享 AI 同事模式：从个人独占式聊天窗口到频道共享同一 AI，上下文共享+角色分工+知识沉淀三位一体 | - |
| [template-variance-control.md](ai-collaboration/template-variance-control.md) | 模板质量方差控制模式：保证一类产出物质量下限、降低不同执行者之间质量方差 | L1 |
| [tool-adoption-funnel.md](ai-collaboration/tool-adoption-funnel.md) | 工具采纳漏斗（Tool Adoption Funnel） | - |
| [two-stage-outline-then-expand.md](ai-collaboration/two-stage-outline-then-expand.md) | 篇幅控制两阶段模式：阶段1输出大纲→主代理审核→阶段2按大纲展开正文，避免子代理一次性长文跑偏 | L1 |
| [user-sovereignty-default.md](ai-collaboration/user-sovereignty-default.md) | 用户主权默认模式：被代理方始终拥有最高权限，操作可见+可感知+可干预+可终止，代理系统的核心信任设计原则 | L1 |
| [visual-operation-closed-loop.md](ai-collaboration/visual-operation-closed-loop.md) | 视觉操作闭环模式（Screenshot-Locate-Operate-Verify Loop） | L1 |
| [visual-universal-operation.md](ai-collaboration/visual-universal-operation.md) | 视觉通用操作模式：AI通过屏幕视觉识别+键鼠模拟操作任意异构系统（不依赖API），四层架构+操作后验证+人在回路兜底，是AI Agent操作闭源/遗留系统的务实路线 | L2 |

---

## creative-design — 创意与设计原则

**核心关注点**：围绕创意生成机制、视觉设计原则、认知锚点可视化、角色驱动设计系统的模式。

**边界说明**：包含约束驱动创造力、可编程创意生成算法、视觉原子化原则、认知锚点可视化、角色驱动设计系统、spec驱动开发；不包含AI提示词工程细节、文档治理策略或产品竞争策略。

| 模式文件 | 一句话说明 | 成熟度 |
|---------|-----------|-------|
| [character-driven-design-system.md](creative-design/character-driven-design-system.md) | 角色驱动设计系统模式：功能性角色而非吉祥物，五条核心原则+五维自检框架 | L2 |
| [cognitive-anchor-visualization.md](creative-design/cognitive-anchor-visualization.md) | 认知锚点可视化模式：将配图从装饰升级为认知传递，先识别锚点再选择其一可视化 | L2 |
| [constraint-driven-creativity.md](creative-design/constraint-driven-creativity.md) | 约束驱动创造力模式：通过严格视觉约束聚焦核心信息，色彩功能分工体系 | L2 |
| [intentional-friction-design.md](creative-design/intentional-friction-design.md) | 「有意图的摩擦」设计原则，区分战略转化节点与无意义障碍 | L1 |
| [programmable-creativity-algorithm.md](creative-design/programmable-creativity-algorithm.md) | 可编程创意生成算法：三步隐喻转换（概念→动作→物件→画面）替代自由联想式 prompt | L2 |
| [reverse-adaptation-innovation.md](creative-design/reverse-adaptation-innovation.md) | 逆向适配创新模式 | L2 已验证 |
| [spec-driven-development.md](creative-design/spec-driven-development.md) | Spec-driven 开发流程，"先设计后实施"的完整方法论 | L3 |
| [three-track-constraint-review.md](creative-design/three-track-constraint-review.md) | 约束审查三轨制 | L2-validated |
| [visual-atomization-principle.md](creative-design/visual-atomization-principle.md) | 视觉原子化原则：一张图一个认知锚点，跨领域同构验证文档与视觉原子化 | L2 |
| [zhengyan-ruofan-writing.md](creative-design/zhengyan-ruofan-writing.md) | 正言若反写作法 | L2-validated |

---

## product-growth — 产品开发与竞争策略

**核心关注点**：围绕产品定位、赛事运营增长、竞争策略博弈、交付流水线管控、AI产品设计、营销转化的业务模式。

**边界说明**：包含赛事增长飞轮模型、可控UGC传播杠杆、漏斗孔径设计、定位漂移修正、零和规则反利用、三层递进交付流水线、Spec九节叙事弧、垂直场景AI三要素、全链路闭环、风控前置副驾驶、爆款数字化复刻、双模式用户分层、多触点AIDA转化；不包含文档架构模式、AI协作提示词或工具工程实现。

| 模式文件 | 一句话说明 | 成熟度 |
|---------|-----------|-------|
| [ai-api-extreme-parameterization.md](product-growth/ai-api-extreme-parameterization.md) | AI API极致参数化模式 | - |
| [ai-consumption-metadata-design.md](product-growth/ai-consumption-metadata-design.md) | AI消费元数据增强模式 | - |
| [ai-native-user-reversal-design.md](product-growth/ai-native-user-reversal-design.md) | AI原生用户逆向定位模式 | - |
| [ai-reliability-four-layer-defense.md](product-growth/ai-reliability-four-layer-defense.md) | AI可靠性四层纵深防御模型 | - |
| [b2b-ai-developer-experience-six-elements.md](product-growth/b2b-ai-developer-experience-six-elements.md) | B2B AI产品开发者体验六要素 | - |
| [b2b-product-metaphor-mapping.md](product-growth/b2b-product-metaphor-mapping.md) | B2B产品业务隐喻映射：技术概念→客户熟悉的业务概念转换，降低理解门槛改变采购决策逻辑（Agent→数字员工、模型训练→员工培训） | L1 |
| [blockbuster-digital-replication.md](product-growth/blockbuster-digital-replication.md) | 爆款数字化复刻方法：爆款样本输入→多维度元素拆解→元素级变体生成→批量输出→数据反馈迭代，内容工业化生产核心方法论 | L3 |
| [compliance-pre-positioning.md](product-growth/compliance-pre-positioning.md) | 合规资质前置：To B产品从入场券到竞争壁垒的五层跃迁——准入资质→内生合规→国产化适配→资质前置展示→主动审计开放 | L2 |
| [contest-funnel-aperture.md](product-growth/contest-funnel-aperture.md) | 赛事漏斗孔径设计，每层最优「筛孔径」与衔接原则 | L1 |
| [contest-growth-flywheel.md](product-growth/contest-growth-flywheel.md) | 赛事增长飞轮模型，将参赛步骤映射为产品增长触点 | L1 |
| [controlled-uncontrollable-ugc-rules.md](product-growth/controlled-uncontrollable-ugc-rules.md) | 「可控的不可控」UGC 传播杠杆，精细化规则引导用户自主传播 | L1 |
| [deadline-breakpoint-first.md](product-growth/deadline-breakpoint-first.md) | 时效断点优先——截止期转化页优化方法论 | L1-draft |
| [dual-mode-user-tiering.md](product-growth/dual-mode-user-tiering.md) | 双模式用户分层架构：共享底层引擎+极简模式（零门槛）+专业模式（全控制）+平滑升级路径，解决生产力工具"简单吓跑专家/复杂吓跑小白"两难，剪映/Figma/Canva/KickArt验证（L4标准化） | L4 |
| [dual-product-matrix-portable-comfort.md](product-growth/dual-product-matrix-portable-comfort.md) | 消费电子双产品矩阵：入门便携款（低门槛引流）+进阶舒适款（高品质变现），参数形成鲜明反差而非同质化竞争，共享软件生态 | L1 |
| [dual-version-matrix-entry-professional.md](product-growth/dual-version-matrix-entry-professional.md) | 双版本矩阵通用策略：入门版覆盖（低门槛扩大基数）+专业版变现（高ARPU利润），五原则（卖点互补/不阉割核心/2-4倍价差/共享生态/升级顺畅），跨软件硬件10个行业案例验证 | L2 |
| [full-workflow-closed-loop.md](product-growth/full-workflow-closed-loop.md) | 全链路闭环设计原则：工作流起点到终点完整覆盖+环节间数据自动流转+消除用户手动拼接成本，闭环价值大于单点极致，3个跨品类SaaS验证 | L3 |
| [hardware-generic-interface-service-differentiation.md](product-growth/hardware-generic-interface-service-differentiation.md) | 硬件通用接口+服务差异化：硬件层遵循通用标准降低门槛，软件/服务层构建差异化壁垒，硬件引流+服务变现 | L2 |
| [hardware-minimal-software-complex.md](product-growth/hardware-minimal-software-complex.md) | 硬件极简软件复杂模式（把复杂性留给云端和软件） | L2 |
| [hardware-price-scenario-matrix.md](product-growth/hardware-price-scenario-matrix.md) | 硬件产品线价格梯度×场景细分矩阵：全价位段覆盖+场景精准切割，核心架构共享+功能模块差异化，入门款保留核心价值 | L1 |
| [hidden-prize-channel-identification.md](product-growth/hidden-prize-channel-identification.md) | 隐性奖项通道识别法 | L1 |
| [interaction-value-directionality.md](product-growth/interaction-value-directionality.md) | 信息流方向性价值判据（Interaction Value: Directionality over Modality） | L1 |
| [local-capability-guarantee.md](product-growth/local-capability-guarantee.md) | 本地能力保底云端增强：核心功能离线可用不依赖云端，云端提供AI/协同/增值能力，是建立用户长期信任的关键设计原则（6次验证） | L2 |
| [multi-touchpoint-aida-conversion.md](product-growth/multi-touchpoint-aida-conversion.md) | 多触点AIDA转化设计：首屏主CTA+模块间隔CTA+场景后CTA+底部最终CTA，不同位置CTA文案差异化匹配用户决策阶段，营销页面经典设计范式（L4标准化） | L4 |
| [pain-point-first-entry.md](product-growth/pain-point-first-entry.md) | 痛点刚需切入模式（单点突破优先于功能堆砌） | L2 |
| [parameter-difference-quantification.md](product-growth/parameter-difference-quantification.md) | 参数差异量化方法：不满足定性描述，计算量化差异倍数，≥10倍数量级差异暗示技术架构根本不同，数字必须场景化翻译为体验差异 | L1 |
| [positioning-drift-correction.md](product-growth/positioning-drift-correction.md) | 定位漂移修正法：三阶段（识别→剥离→重构）修正产品定位中"借用外部标签"导致的品类窄化与时效风险 | L1 |
| [professional-capability-democratization.md](product-growth/professional-capability-democratization.md) | 专业能力平民化增量市场框架：五维下沉分析（价格/人员/场景/配置/管理），保留完整专业能力+体验重构+成本重构开辟增量蓝海，8次跨产品验证 | L2 |
| [progressive-capability-tiering.md](product-growth/progressive-capability-tiering.md) | 渐进式能力分层设计：零门槛入口层（模板/低代码）→高上限能力层（三方模型/代码定制）→企业级管控层（权限/审计/私有化）三层架构，同时满足新手/专家/企业需求 | L1 |
| [reverse-leverage-rule-constraints.md](product-growth/reverse-leverage-rule-constraints.md) | 反向借势——从规则约束中读出最优解 | L1 |
| [risk-control-copilot-pre-positioned.md](product-growth/risk-control-copilot-pre-positioned.md) | 风控前置副驾驶模式：规则引擎内嵌创作流程+实时风险提示+一键自动修正+平台规则同步更新，从成本中心变为价值中心 | L2 |
| [saas-hardware-three-layer-funnel.md](product-growth/saas-hardware-three-layer-funnel.md) | SaaS硬件三层漏斗黄金范式：软件引流→硬件变现→服务留存（含AI服务/企业订阅四收入支柱），硬件是生态物理增强器而非独立产品，跨12个产品/场景验证（L3标准化） | L3 |
| [scenario-driven-parameter-tradeoff.md](product-growth/scenario-driven-parameter-tradeoff.md) | 场景驱动参数取舍：不为参数表堆料，每个参数锚定目标场景回答"是否需要"，保守选择降低成本/功耗/故障率 | L1 |
| [scenario-naming-user-language.md](product-growth/scenario-naming-user-language.md) | 场景化命名模式（用户语言优先于技术语言） | L2 |
| [software-company-hardware-entry-framework.md](product-growth/software-company-hardware-entry-framework.md) | 软件公司跨界硬件5步切入框架：生态引流→体验降维→场景闭环→定价下沉→生态协同，用软件优势重构硬件体验 | L2 |
| [spec-nine-section-narrative.md](product-growth/spec-nine-section-narrative.md) | Spec九节叙事弧：产品定义的完整Checklist（定位→功能→交互→内容→留存→合规→商业→技术→价值） | L2 |
| [system-equation-validation.md](product-growth/system-equation-validation.md) | 系统等式验证法（System Equation Validation） | L1 |
| [tech-product-commercialization-evolution.md](product-growth/tech-product-commercialization-evolution.md) | 技术驱动型产品商业化演进五维分析框架 | - |
| [technology-encapsulation-user-simplicity.md](product-growth/technology-encapsulation-user-simplicity.md) | 技术封装体验上浮模式（复杂性下沉，简单性上浮） | L2 |
| [template-homogenization-escape.md](product-growth/template-homogenization-escape.md) | 模板同质化避让策略 | L2 |
| [three-layer-delivery-pipeline.md](product-growth/three-layer-delivery-pipeline.md) | 三层递进流水线：文档先行→原型验证→对外包装，严格顺序禁止颠倒，防止过度承诺 | L3 |
| [three-tier-iot-architecture.md](product-growth/three-tier-iot-architecture.md) | 三层IoT技术架构范式：硬件端极简+App端灵活+云端增值，三层职责分离避免某层承担过多职责，全系列硬件8次验证 | L2 |
| [vertical-saas-mcp-capability-exposure.md](product-growth/vertical-saas-mcp-capability-exposure.md) | 垂直SaaS AI转型务实路径：不做通用大模型，通过MCP协议开放核心领域能力给Claude/GPT等通用大脑，六步MCP化转型+视觉兜底路径，4个行业可复用 | L2 |
| [vertical-scenario-ai-three-elements.md](product-growth/vertical-scenario-ai-three-elements.md) | 垂直场景AI产品三要素：行业专属功能+场景化工作流+领域合规风控，AI应用层竞争从通用能力竞赛转向场景解决方案竞赛，3个跨领域产品验证 | L3 |
| [zero-sum-rule-inversion.md](product-growth/zero-sum-rule-inversion.md) | 零和规则反利用：将竞争场景中的限制性条款从障碍转换为策略聚焦器，在 Best Shot 模式下最大化先发优势的边际回报 | L1 |
