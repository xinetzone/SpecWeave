# 方法论模式主题分类说明

基于模式的核心主题思想进行分类，而非成熟度等级或来源。共划分为8个主题类别，便于按场景快速定位相关模式。

> **数据来源**：以下计数基于各目录实际 `.md` 文件数（排除README.md），最后更新：2026-07-06（PDU复盘2个候选模式升级入库L2后重新校正）。

## 分类索引

| 主题目录 | 中文名称 | 模式数量 | 核心关注点 |
|---------|---------|---------|-----------|
| [retrospective-knowledge](#retrospective-knowledge--复盘与知识生命周期) | 复盘与知识生命周期 | 32 | 项目复盘流程、知识萃取、洞察沉淀、经验迁移 |
| [research-knowledge](#research-knowledge--外部研究与知识融合) | 外部研究与知识融合 | 3 | 外部网站分析、Vendor仓库高层文档优先研究、跨Vendor知识融合、信息源分层兜底、访问障碍应对、多源验证 |
| [document-architecture](#document-architecture--文档架构与原子化) | 文档架构与原子化 | 38 | 文档体系重构、原子化拆分、文档治理、结构设计 |
| [tools-automation](#tools-automation--工具工程与自动化) | 工具工程与自动化 | 28 | 工具决策、工具故障降级、自动化实施、工具链建设、批量操作安全 |
| [governance-strategy](#governance-strategy--治理与优先级策略) | 治理与优先级策略 | 58 | 体系治理、优先级排序、问题解决、规范防护 |
| [ai-collaboration](#ai-collaboration--ai协作与提示词设计) | AI协作与提示词设计 | 35 | AI Skill设计、人机协作模式、提示词工程、输出行为规范、团队共享AI同事、主动介入Agent、安全信任设计、源码锚点二次校验、契约文档协调中枢、模块级agents扩展、references渐进式披露、Gotchas领域特化、视觉通用操作、输出格式-协作能力映射、生态壁垒评估 |
| [creative-design](#creative-design--创意与设计原则) | 创意与设计原则 | 7 | 创意生成、视觉设计、认知锚点、角色驱动设计 |
| [product-growth](#product-growth--产品开发与竞争策略) | 产品开发与竞争策略 | 27 | 产品定位、赛事增长、竞争策略、交付流水线、硬件产品设计、To B合规策略、三层商业模式、IoT技术架构、本地保底信任、双版本矩阵、AI转型MCP路径、专业能力平民化 |

---

## retrospective-knowledge — 复盘与知识生命周期

**核心关注点**：围绕项目复盘流程、知识萃取、洞察沉淀、经验迁移的全生命周期模式。

**边界说明**：包含复盘方法论框架、洞察加工转化漏斗、知识沉淀分层体系、经验跨领域迁移验证、知识资产演化规律；不包含具体的文档操作工具实现、AI提示词设计或产品增长策略。

| 模式文件 | 一句话说明 | 成熟度 |
|---------|-----------|-------|
| [actionable-suggestion-five-elements.md](retrospective-knowledge/actionable-suggestion-five-elements.md) | 可执行建议五要素：交付物+验收+优先级+集成+状态，含1:1无冗余映射原则 | L1 |
| [bug-as-asset.md](retrospective-knowledge/bug-as-asset.md) | Bug即资产转化机制：三条件萃取标准（可命名+可复现+可防护），架构级Bug优先萃取 | L2 |
| [closed-loop-pdca-mapping.md](retrospective-knowledge/closed-loop-pdca-mapping.md) | 闭环PDCA映射：四步闭环与戴明环的映射，含双正反馈回路机制 | L1 |
| [counterfactual-debt-analysis.md](retrospective-knowledge/counterfactual-debt-analysis.md) | 反事实推演与技术债复利分析：通过时间线推演表量化"不做改进"的复利代价 | L1 |
| [experience-transfer-mapping.md](retrospective-knowledge/experience-transfer-mapping.md) | 经验迁移映射：三列表（本经验→可迁移到→迁移示例）区分核心机制vs上下文细节，≥3个跨领域验证通用性 | L1 |
| [export-four-channel-progressive.md](retrospective-knowledge/export-four-channel-progressive.md) | 导出四渠道递进：文档化→模板化→工具化→制度化，含渐进式策略与决策准则速查 | L1 |
| [extraction-four-layer-funnel.md](retrospective-knowledge/extraction-four-layer-funnel.md) | 萃取四层漏斗：去噪→结构化→标准化→可操作化，含"四可"质量标准 | L1 |
| [five-category-asset-coverage.md](retrospective-knowledge/five-category-asset-coverage.md) | 五类资产覆盖原则：概念/模式/脚本/报告/索引五类互补覆盖 | L2 |
| [insight-iceberg-model.md](retrospective-knowledge/insight-iceberg-model.md) | 洞察冰山模型：现象层→模式层→原理层三层递进分析，含关键转折点与高质量洞察三特征 | L1 |
| [insight-library-evolution.md](retrospective-knowledge/insight-library-evolution.md) | 洞察库演化规律：三阶段（描述期/展开期/系统期）、概念完备线信号、5个锚点洞察识别 | L2 |
| [insight-two-tier-structure.md](retrospective-knowledge/insight-two-tier-structure.md) | 洞察两档结构：基础档/完整档双轨写作，10-20%核心概念承担80%解释力（帕累托法则） | L2 |
| [knowledge-compound-interest.md](retrospective-knowledge/knowledge-compound-interest.md) | 知识沉淀复利模型：产出价值=基础×抽象层级^复用次数，复盘萃取是唯一能升级产出层级的活动 | L1 |
| [methodology-critical-mass.md](retrospective-knowledge/methodology-critical-mass.md) | 方法论临界质量效应：模式数突破 6 后从线性累积跃迁至组合爆炸，知识生产边际收益递增 | L1 |
| [methodology-five-level-maturity.md](retrospective-knowledge/methodology-five-level-maturity.md) | 方法论五级成熟度：借鉴CMMI的五级评估框架，含跃迁路径与评估方法 | L1 |
| [multi-source-intelligence-iteration.md](retrospective-knowledge/multi-source-intelligence-iteration.md) | 多源增量情报迭代法：五子系统构成的多轮决策分析引擎 | L2 |
| [report-as-tracking.md](retrospective-knowledge/report-as-tracking.md) | 报告即追踪载体，每执行一个建议后立即更新报告状态形成闭环 | L2 |
| [retrospective-acceleration-effect.md](retrospective-knowledge/retrospective-acceleration-effect.md) | 复盘加速效应：高频复盘→低延迟改进→知识转化率递增 | L1 |
| [retrospective-four-step-method.md](retrospective-knowledge/retrospective-four-step-method.md) | 复盘四步法：回顾目标→还原事实→分析偏差→提炼经验，含四步产出物对照表与误区清单 | L1 |
| [review-insight-export-loop.md](retrospective-knowledge/review-insight-export-loop.md) | 复盘→洞察→导出知识闭环，含报告结构模板 | L2 |
| [rolling-retro-eight-steps.md](retrospective-knowledge/rolling-retro-eight-steps.md) | 滚动复盘八步：文档一致性的低成本保障机制，每轮15-30分钟维持多轮迭代一致性 | L3 |
| [suggestion-priority-driven-execution.md](retrospective-knowledge/suggestion-priority-driven-execution.md) | 建议执行优先级驱动模型，高/中/低优先级分类 + 投入估算 + 状态追踪 | L2 |
| [three-part-retrospective.md](retrospective-knowledge/three-part-retrospective.md) | 三段式复盘改进法：事实层→认知层→行动层严格单向依赖，含检查清单，100%建议落地率验证 | L3 |
| [three-tier-knowledge-sedimentation.md](retrospective-knowledge/three-tier-knowledge-sedimentation.md) | 三层知识沉淀体系：洞察原文（第三层）→ 专题报告（第二层）→ README 条目（第一层）的递进式知识网络 | L1 |

---

## research-knowledge — 外部研究与知识融合

**核心关注点**：围绕外部网站分析、竞品研究、vendor子模块学习、跨项目知识融合等依赖外部信息源和知识吸收的任务方法论，重点解决信息访问受阻、信息源质量参差不齐、多源验证、外部知识如何有效融入自有体系等问题。

**边界说明**：包含外部网站访问受阻时的分层降级策略、信息源可信度评级、三角验证法、Vendor仓库高层文档优先研究法、跨Vendor知识融合三步流程；不包含内部知识复盘沉淀（见retrospective-knowledge）、文档架构治理、AI协作提示词设计或产品竞争策略本身。

| 模式文件 | 一句话说明 | 成熟度 |
|---------|-----------|-------|
| [cross-vendor-knowledge-fusion.md](research-knowledge/cross-vendor-knowledge-fusion.md) | 跨Vendor知识融合三步法：理解Vendor→认知自我→优势互补融合，避免"全盘照搬"和"NIH综合征"两个极端，融合后1+1>2 | L1 |
| [vendor-high-level-doc-first-research.md](research-knowledge/vendor-high-level-doc-first-research.md) | Vendor仓库"自顶向下"研究法：先读AGENTS.md/CLAUDE.md等AI友好高层文档建立全局框架，再按需深入源码，效率提升5-10倍，基础设施故障时的救命稻草 | L2 |
| [external-website-analysis-fallback-strategy.md](research-knowledge/external-website-analysis-fallback-strategy.md) | 外部网站分析四层信息源分层兜底策略（直接访问→工具增强→官方替代源→第三方权威源），含工具间降级原则、Windows环境注意事项、降级决策流程、五秒诊断清单与三角验证SOP | L2 |

---

## document-architecture — 文档架构与原子化

**核心关注点**：围绕文档体系重构、原子化拆分、文档治理、结构设计的模式。

**边界说明**：包含文档拆分策略、入口设计、链接管理、元文档策略、模块化接口设计、双受众内容萃取、双阶段加工流程；不包含开发流程规范、工具自动化实现细节或AI提示词设计。

| 模式文件 | 一句话说明 | 成熟度 |
|---------|-----------|-------|
| [atomization-three-criteria-test.md](document-architecture/atomization-three-criteria-test.md) | 原子化三标准检验：单一职责/独立可测/命名聚合三准则互验 | L1 |
| [atomization-three-tier-classification.md](document-architecture/atomization-three-tier-classification.md) | 原子化三级分类策略：新建模式/已有覆盖/原地保留三级判断，替代"每个发现都新建模式" | L1 |
| [bidirectional-navigation-links.md](document-architecture/bidirectional-navigation-links.md) | 原子文件双向导航三链路：prev/next/返回目录，解决原子化后阅读路径断裂问题 | L1 |
| [blockquote-code-block-rendering-fix.md](document-architecture/blockquote-code-block-rendering-fix.md) | 引用块嵌套代码块渲染修复：Markdown引用块内代码块链接/加粗失效问题的解决方案 | L1 |
| [blockquote-code-block-rendering-usage-guide.md](document-architecture/blockquote-code-block-rendering-usage-guide.md) | 引用块代码块渲染修复深度指南：5种变体、8组正反例、渲染器兼容性说明 | L2 |
| [content-migration-workflow.md](document-architecture/content-migration-workflow.md) | 文档内容迁移标准操作流程，存量盘点→缺口计算→富化归档→验证闭环 | L2 |
| [document-content-funnel.md](document-architecture/document-content-funnel.md) | 文档内容加工四层漏斗：外部网页→L1去噪→L2观点标记→L3信息架构（含原子化决策检查点）→L4知识库集成，每跳步对应质量问题 | L3 |
| [document-entropy-three-strategies.md](document-architecture/document-entropy-three-strategies.md) | 文档声明熵增三策：人工同步字段过时是必然，推荐"移除变量+免责声明"零成本方案 | L3 |
| [document-system-refactoring.md](document-architecture/document-system-refactoring.md) | 文档体系原子化重构方法论，含六步流程 | L2 |
| [dual-audience-extraction-model.md](document-architecture/dual-audience-extraction-model.md) | 双受众萃取模型：一次投入产出两类资产——面向Agent的模板+面向人类的方法论，分开撰写效果更好 | L2 |
| [entry-container-separation.md](document-architecture/entry-container-separation.md) | 入口-容器分离原则：README（人类）最大精简、AGENTS（AI）路由级保留、.agents/ 全量承载（793次提交验证，L3标准化） | L3 |
| [fact-statement-consistency-loop.md](document-architecture/fact-statement-consistency-loop.md) | 事实表述一致性闭环，修正一处→搜索同类→统一修正 | L2 |
| [i18n-anchor-page-strategy.md](document-architecture/i18n-anchor-page-strategy.md) | 国际化锚定页策略：仅翻译核心索引表 + 路由指引，避免全量翻译的维护成本爆炸 | L1 |
| [large-scale-duplication-elimination.md](document-architecture/large-scale-duplication-elimination.md) | 大规模重复消除法：审计→分类→共享库先行→并行迁移→全量验证五步法 | L2 |
| [link-decay-laws.md](document-architecture/link-decay-laws.md) | 文档链接衰变四规律：下移断链多/上移影响小/跨目录最脆弱/同目录最稳定 | L1 |
| [meta-document-leverage.md](document-architecture/meta-document-leverage.md) | 元文档杠杆效应：<20%篇幅贡献>50%采纳率，元文档（入口/索引/门面）ROI最高，资源有限时优先投资（量化验证，L3标准化） | L3 |
| [knowledge-base-three-stage.md](document-architecture/knowledge-base-three-stage.md) | 知识库建设三阶段：生成→重组→精确化，顺序不可颠倒，跳过中间阶段导致返工（59个Wiki验证） | L2 |
| [modularization-interface-design.md](document-architecture/modularization-interface-design.md) | 模块化接口设计四步法：边界→接口→耦合→版本，含七级耦合标尺与 30 秒准则 | L1 |
| [mermaid-layered-visualization.md](document-architecture/mermaid-layered-visualization.md) | Mermaid 分层可视化：一图一义+分层独立，时间/决策/依赖/流程四维度分层策略与状态标注规范 | L2 |
| [meta-atomization-bisect-overview.md](document-architecture/meta-atomization-bisect-overview.md) | 元原子化二分+概览模式：中型文档单章节膨胀的轻量拆分法（时间二分法/概览详情分离法），6步操作指南 | L2 |
| [one-stop-operation-guide.md](document-architecture/one-stop-operation-guide.md) | 一站式操作指南：高频任务单文件整合入口，将规则/模板/工具/排错压缩为单文件直达 | L2 |
| [pattern-merge-boundary.md](document-architecture/pattern-merge-boundary.md) | 模式合并边界判断：三维重叠度（场景/机制/建议）>70% 合并，30-70% 独立判断，<30% 独立创建 | L1 |
| [post-atomization-content-merge-back.md](document-architecture/post-atomization-content-merge-back.md) | 原子化后内容回源合并：深度分析提取后源文档降级为概要+引用，模式文件为唯一权威来源 | L1 |
| [progressive-readme-growth.md](document-architecture/progressive-readme-growth.md) | 渐进式 README 生长：每完成一轮知识产出即追加一行技术创新点，最低成本持续提升 README 价值密度 | L1 |
| [scripted-batch-correction.md](document-architecture/scripted-batch-correction.md) | 脚本化批量修正安全决策：根据旧名称出现模式（路径引用/代码标识符）选择脚本化或手动 | L1 |
| [source-document-downgrade.md](document-architecture/source-document-downgrade.md) | 源文档降级模式：大型文档原子化后不删除源文档，降级为引用导航页 | L2 |
| [synthetic-stats-source-of-truth.md](document-architecture/synthetic-stats-source-of-truth.md) | 合成统计的权威数据来源：跨文件统计数据应从 metadata 全量重算，而非增量推算，避免偏差累积 | L1 |
| [tutorial-cognitive-ladder.md](document-architecture/tutorial-cognitive-ladder.md) | 教程认知阶梯：技术教程六层递进结构（概述→原则→示例→快速开始→本地整合→生态上下文），按读者认知路径组织 | L2 |
| [two-phase-processing.md](document-architecture/two-phase-processing.md) | 双阶段加工策略：大型文档先横切（原子化）再纵切（模块化）的固定先后顺序 | L1 |
| [product-learning-five-tier-pyramid.md](document-architecture/product-learning-five-tier-pyramid.md) | 产品学习文档5层价值金字塔：信息→理解→场景→商业→前瞻，越往上层价值半衰期越长、可复用性越高 | L1 |
| [sunlogin-hardware-wiki-structure.md](document-architecture/sunlogin-hardware-wiki-structure.md) | 向日葵硬件系列Wiki标准结构（13章）：4次验证的硬件产品学习Wiki文档模板，从产品概述到行业趋势覆盖认知全链路 | L2 |

---

## tools-automation — 工具工程与自动化

**核心关注点**：围绕工具自动化决策、安全实施策略、工具链成熟度建设、批量操作风险控制的工程模式。

**边界说明**：包含自动化ROI判断模型、dry-run安全修改流程、工具链五阶段演进、路径幂等性纪律、批量替换脆弱性规避、精度优先于召回原则；不包含文档架构设计决策、治理优先级策略或知识萃取方法论。

| 模式文件 | 一句话说明 | 成熟度 |
|---------|-----------|-------|
| [auto-generate-threshold.md](tools-automation/auto-generate-threshold.md) | 自动化阈值判断：手动条目占比 30% 阈值 + 模式成熟度 validation_count≥2 自动升级规则 | L2 |
| [best-practice-hidden-cost.md](tools-automation/best-practice-hidden-cost.md) | 最佳实践隐性成本：推广实践须配套吸收成本的工具链（如原子化的"链接税"） | L1 |
| [capability-matrix.md](tools-automation/capability-matrix.md) | 能力清单/功能矩阵：显式声明工具能力边界与精确度，三重价值（用户/维护者/规划） | L1 |
| [depth-reference-table.md](tools-automation/depth-reference-table.md) | 深度参考表：预计算常见目录深度的相对路径前缀，将易错心算转化为查表操作，降低80%路径错误 | L2 |
| [defuddle-web-extraction-preferred.md](tools-automation/defuddle-web-extraction-preferred.md) | defuddle网页提取首选+双工具兜底模式：提取网页文章正文优先defuddle，提取后做完整性检查，关键信息缺失时WebFetch兜底补全，替代WebFetch+手动清理 | L2 |
| [diff-driven-refactoring.md](tools-automation/diff-driven-refactoring.md) | 差异驱动重构：逐段对比→标注重复/相似/独有→分类提取→回归验证 | L2 |
| [dry-run-first.md](tools-automation/dry-run-first.md) | dry-run 安全修改模式：默认预览→用户确认→执行写入→立即验证，零误报信任建立 | L3 |
| [explicit-maturity-tracking.md](tools-automation/explicit-maturity-tracking.md) | 成熟度显式追踪：L1-L4统一分级，frontmatter标准字段，四重价值与升级规则 | L1 |
| [git-local-clone-safety-protocol.md](tools-automation/git-local-clone-safety-protocol.md) | 本地路径Git克隆异常最小破坏处置协议：Windows下git clone本地路径BUG的检测→留痕→稳妥重试流程 | L1 |
| [legacy-exposure-effect.md](tools-automation/legacy-exposure-effect.md) | 新检测规则存量暴露效应：落地新linter/checker前先扫描历史存量问题，避免CI一片红 | L1 |
| [metric-tool-exclusion-profiling.md](tools-automation/metric-tool-exclusion-profiling.md) | 度量工具排除机制与配置画像：内置默认exclude+按目录类型预设profile（docs/specs/agents/code），消除一刀切权重误判 | L1 |
| [model-to-test-matrix.md](tools-automation/model-to-test-matrix.md) | 理论模型→测试矩阵转化：边界界定→优先级映射→风险点展开→用例生成，模型层级即测试边界 | L2 |
| [multi-signal-detection.md](tools-automation/multi-signal-detection.md) | 多信号组合检测：N个独立信号源或逻辑组合，按可靠性排序，反向信号辅助，DEBUG模式输出完整JSON诊断 | L2 |
| [package-structure-leverage.md](tools-automation/package-structure-leverage.md) | 包结构杠杆效应：三层结构（定义层+导出层+兼容层）使新增功能成本从 O(n) 降至 O(1) | L1 |
| [path-discipline.md](tools-automation/path-discipline.md) | 高强度编辑中的路径与幂等性纪律：路径确认三步走+回滚备份规则，防止文件污染与不可恢复断裂 | L1 |
| [precision-over-recall.md](tools-automation/precision-over-recall.md) | 精度优先于召回率：破坏性工具零误报原则，"宁可不修不可错修"，三层安全保障 | L1 |
| [refactoring-hidden-bug-discovery.md](tools-automation/refactoring-hidden-bug-discovery.md) | 重构中隐藏 Bug 发现：重构真实 ROI = 消除重复 + 隐藏问题发现 + 结构基础 | L1 |
| [search-replace-fragility.md](tools-automation/search-replace-fragility.md) | SearchReplace 并发脆弱性与大块替换策略：多轮 SearchReplace 可靠性指数级下降，大块替换用整体读写策略 | L1 |
| [shared-lib-gravity.md](tools-automation/shared-lib-gravity.md) | 共享库引力定律：覆盖≥5概念域触发正反馈循环，覆盖面越大复用率越高，指导多脚本项目代码复用 | L2 |
| [spec-as-code-automated-gates.md](tools-automation/spec-as-code-automated-gates.md) | 规范即代码自动化门禁：将文档规范写成检查脚本作为提交强制门禁，而非靠人自觉遵守 | L1 |
| [tool-automation-decision-model.md](tools-automation/tool-automation-decision-model.md) | 工具自动化决策模型：3 次手动触发评估 + 成本公式 + ROI 度量 + 熵分类体系 | L2 |
| [tool-bootstrap-effect.md](tools-automation/tool-bootstrap-effect.md) | 工具自举效应：dogfooding正反馈循环，使用工具→发现不足→增强工具→发现更多问题 | L1 |
| [tool-self-validation.md](tools-automation/tool-self-validation.md) | 工具自生验证：新linter提交前7项检查清单（自扫描→真阳性→误报过滤→信噪比→输出可用→CI兼容→边界场景） | L2 |
| [tool-workflow-composition.md](tools-automation/tool-workflow-composition.md) | 工具工作流组合：事前评估→事中操作→事后收尾→验证→门禁，组合价值>单个工具之和 | L1 |
| [toolchain-maturity.md](tools-automation/toolchain-maturity.md) | 工具链五阶段成熟度模型：手动检测→自动检测→自动修复→流程预防→门禁保障，含维度评估表与跃迁规律 | L1 |
| [tool-failure-three-tier-degradation.md](tools-automation/tool-failure-three-tier-degradation.md) | 工具故障三级降级策略：Level1委托sub-agent→Level2挖掘附带信息/替代工具→Level3基于已有知识推进，含defuddle常见故障处理、Windows环境注意事项，核心铁则"连续失败2次禁止第3次重试" | L2 |

---

## governance-strategy — 治理与优先级策略

**核心关注点**：围绕体系化治理、优先级排序、问题分层解决、规范防护机制的决策模式。

**边界说明**：包含三层治理模型、治理层级优先级、问题解决三层跃迁、约定驱动创建、规范纵深防御、自指性规范体系、递进式需求澄清；不包含具体工具实现细节、文档原子化操作步骤或知识萃取流程。

| 模式文件 | 一句话说明 | 成熟度 |
|---------|-----------|-------|
| [amphibious-positioning-model.md](governance-strategy/amphibious-positioning-model.md) | 两栖定位模型：通过资产清单+泛化路径图+落地案例三支柱支撑双重定位 | L1 |
| [chapter-type-tiered-file-size.md](governance-strategy/chapter-type-tiered-file-size.md) | 章节类型分层文件大小策略：按概念型/API参考型/实战案例型/参考型分层设置行数上限，替代一刀切的300行限制 | L1 |
| [commit-quality-gate-staging-inspection.md](governance-strategy/commit-quality-gate-staging-inspection.md) | 提交质量门三查暂存法：git status→git diff逐文件审查→显式add，禁止git add .，在add阶段防止脏提交混入 | L2 |
| [convention-driven-creation.md](governance-strategy/convention-driven-creation.md) | 约定驱动创建模型，先读范例提取模板再填充内容，零结构决策 | L2 |
| [cross-wiki-reference-directory-first.md](governance-strategy/cross-wiki-reference-directory-first.md) | 跨Wiki引用目录优先验证：创建跨wiki引用前必须先读取目标wiki的00-overview.md确认章节编号，用事实替代假设；5次验证4次复用，已达L3升级门槛 | L2 |
| [governance-tier-priority.md](governance-strategy/governance-tier-priority.md) | 治理层级优先级排序：🔴防复发→🟡提效率→🟢拓边界，与战术层投入估算互补 | L1 |
| [progressive-requirement-clarification.md](governance-strategy/progressive-requirement-clarification.md) | 递进式需求澄清：先定范围再定细节的两轮策略，互斥选项+互补选项设计规范 | L1 |
| [prove-usefulness-check.md](governance-strategy/prove-usefulness-check.md) | 证明有用性自检模式：好的组件不可减去，去掉后系统功能受损才保留 | L2 |
| [reference-as-trigger.md](governance-strategy/reference-as-trigger.md) | 引用即触发协作模式：用户选中行号触发精确实施 | L2 |
| [root-cause-diagnosis.md](governance-strategy/root-cause-diagnosis.md) | 根因诊断模式：收到纠错反馈时先暂停追溯知识缺口，再全量修正，避免表层症状修补循环 | L2 |
| [self-referential-spec-system.md](governance-strategy/self-referential-spec-system.md) | 自指性规范体系：规范定义自身，形成"规范即测试"效应——规范变更触发全景验证 | L1 |
| [session-boundary-commit.md](governance-strategy/session-boundary-commit.md) | 原子提交会话边界原则：双重单一职责（功能+会话），归属分析→会话筛选→功能分组→排除确认 | L1 |
| [short-command-patterns.md](governance-strategy/short-command-patterns.md) | 短指令模式库：登记已验证的 AI 协作快捷指令 | L2 |
| [spec-level-defense-in-depth.md](governance-strategy/spec-level-defense-in-depth.md) | 规范层纵深防御模型，权限定义+验证机制+防滥用+审计追溯四维防护 | L1 |
| [structure-first-extension.md](governance-strategy/structure-first-extension.md) | 结构阅读先行：扩展前先完整阅读包结构，同概念域追加、异概念域新建 | L3 |
| [three-level-problem-solving.md](governance-strategy/three-level-problem-solving.md) | 问题解决三层跃迁：L1症状治疗→L2病因根治→L3系统免疫，架构师思考L3 | L1 |
| [three-tier-board-system.md](governance-strategy/three-tier-board-system.md) | 三层看板体系：全局看板→主题看板→创建模板，覆盖看-管-建全生命周期，含自维护闭环 | L1 |
| [three-tier-governance.md](governance-strategy/three-tier-governance.md) | 三层治理模型（原子化→自动化→验证），含实施检查清单（150+脚本验证，L3标准化） | L3 |
| [three-zone-boundary-model.md](governance-strategy/three-zone-boundary-model.md) | 三区域边界模型：主项目区/接口层/外部依赖区主权划分，定义允许/禁止操作清单 | L2 |
| [file-creation-precheck-pattern.md](governance-strategy/file-creation-precheck-pattern.md) | 文件创建前置检查模式：三步检查流程（确定归属目录→确定文件名格式→自动化验证）确保文件创建合规 | L2 |
| [format-evidence-over-memory-pattern.md](governance-strategy/format-evidence-over-memory-pattern.md) | 格式证据优先于记忆模式：创建新文件前必须读取同目录现有文档确认格式，实际文档是唯一权威来源 | L2 |
| [spec-discoverability-guarantee.md](governance-strategy/spec-discoverability-guarantee.md) | 规范可发现性保障模式：三层映射模型（AGENTS.md引用→路由表条目→自动化脚本）确保规范不会"存在但不可发现" | L1 |
| [three-layer-spec-constraint.md](governance-strategy/three-layer-spec-constraint.md) | 规范约束三层次模型：规则定义层→路由发现层→自动化验证层，确保规范不会"存在但不可发现" | L2 |
| [two-dimension-document-governance.md](governance-strategy/two-dimension-document-governance.md) | 文档治理双维度检查模型：位置维度（目录归属）+ 命名维度（kebab-case），双重违规暴露流程漏洞 | L2 |
| [spec-triple-sync.md](governance-strategy/spec-triple-sync.md) | 规范三同步原则：新规范发布必须完成①总览引用②入口更新③存量迁移示范，解决"规范悬空"问题 | L2 |
| [dev-env-dockerfile-optimization.md](governance-strategy/dev-env-dockerfile-optimization.md) | 开发环境Dockerfile优化法：优先排序而非最小化，整合变化频率分层+.dockerignore三重价值+层缓存涟漪效应 | L1 |
| [toolchain-five-stage-evolution.md](governance-strategy/toolchain-five-stage-evolution.md) | 工具链项目五阶段演进路径：脚本堆砌→模块化→工作流标准化→测试体系→基础设施优化，自底向上演进 | L1 |
| [test-coverage-diminishing-returns.md](governance-strategy/test-coverage-diminishing-returns.md) | 测试覆盖率边际收益递减拐点：70%处策略转换，从追求覆盖率数字转向关注关键路径测试质量 | L1 |
| [immutable-constraint-documentation.md](governance-strategy/immutable-constraint-documentation.md) | 不可变约束清单模式：每条约束包含内容+历史踩坑原因+代码位置三要素，踩坑经验工程化沉淀 | L1 |
| [wiki-dual-track-frontmatter.md](governance-strategy/wiki-dual-track-frontmatter.md) | Wiki双轨Frontmatter规范：单文件wiki和原子化wiki使用不同字段集，模板/检查清单必须类型感知，禁止混用字段 | L1 |
| [meta-retrospective-closed-loop.md](governance-strategy/meta-retrospective-closed-loop.md) | 元复盘闭环：交付后主动元复盘→纠偏→行动落地→工具化五步闭环，防止错误入库并加速方法论资产周转 | L1 |
| [pattern-tooling-progressive-extraction.md](governance-strategy/pattern-tooling-progressive-extraction.md) | 模式渐进式工具提取：L1实验阶段即可提取轻量检查清单/模板，工具使用反哺模式验证，打破"等L2才工具化"的死循环 | L1 |
| [four-negatives-external-dependency.md](governance-strategy/four-negatives-external-dependency.md) | 外部依赖四不原则+零依赖原则：不侵入/不直引/不跟版/不裸考/不滥引，150+脚本零第三方依赖跨平台验证（L3标准化） | L3 |
| [bootstrap-driven-self-evolution.md](governance-strategy/bootstrap-driven-self-evolution.md) | 规范自举性驱动持续演化：达到自举点（分类/模板/检查/复盘/导航全部闭环）后项目进入持续演化阶段，里程碑从"功能完成"变为"能力建立"（793次提交验证） | L2 |
| [governance-three-stage-evolution.md](governance-strategy/governance-three-stage-evolution.md) | 治理演化三阶段：修复→预防→闭环，禁止跳过任何阶段；跳过预防导致问题复发，多个场景验证（Mermaid/断链/事实漂移） | L2 |

---

## ai-collaboration — AI协作与提示词设计

**核心关注点**：围绕AI Skill产品化设计、人机协作交互模式、提示词工程策略、输出行为规范的模式。

**边界说明**：包含AI Skill判断层设计、双语提示词分层、双区开发模型、输出行为四维约束、上下文渐进式披露、风格-创意分离控制、症状-处方QA闭环、团队共享AI同事、主动介入Agent、模块级agents扩展继承、references渐进式披露、Gotchas领域特化、安全信任设计、源码锚点二次校验、契约文档协调中枢、输出格式-协作能力映射、生态壁垒评估；不包含通用文档模式、产品增长策略或工具工程实现。

| 模式文件 | 一句话说明 | 成熟度 |
|---------|-----------|-------|
| [ai-skill-judgment-layer.md](ai-collaboration/ai-skill-judgment-layer.md) | AI Skill 判断层设计模式：工具负责生产，判断负责选择，三层能力模型 | L2 |
| [bilingual-prompt-engineering.md](ai-collaboration/bilingual-prompt-engineering.md) | 双语提示词工程：按目标模型最优语言做提示词分层，Agent 推理语言与模型执行语言各司其职 | L2 |
| [context-recovery-protocol.md](ai-collaboration/context-recovery-protocol.md) | Context 恢复协议重执行模式：收到会话历史摘要/中断恢复时必须重新执行完整启动协议 | L1 |
| [dual-zone-development-model.md](ai-collaboration/dual-zone-development-model.md) | 双区开发模型（非正式区→质量门禁→正式区） | L2 |
| [markdown-as-interface.md](ai-collaboration/markdown-as-interface.md) | Markdown即接口：用Markdown同时承载人类阅读与机器调用，三层架构（L0叙事/L1接口/L2检查清单） | L4 |
| [navigation-hub-filename-contract.md](ai-collaboration/navigation-hub-filename-contract.md) | 导航枢纽文件名契约：全局文件清单vs局部清单，并行sub-agent任务中导航枢纽文件需传递全部章节文件名（L2扩展：契约文档作为协调中枢） | L2 |
| [output-behavior-specification.md](ai-collaboration/output-behavior-specification.md) | 输出行为规范：四维约束模型的第四维度——何时说话、说什么、说多少、什么时候沉默 | L2 |
| [progressive-context-disclosure.md](ai-collaboration/progressive-context-disclosure.md) | 上下文渐进式披露：入口索引 + 按需加载，工作流阶段绑定加载条件，节省 60%+ 上下文消耗 | L2 |
| [progressive-templating.md](ai-collaboration/progressive-templating.md) | 渐进式模板化：硬编码验证→模板分离→多类型扩展三阶段 | L1 |
| [skill-discovery-protocol.md](ai-collaboration/skill-discovery-protocol.md) | Skill 发现协议增强 SOP：三层发现机制（Onboarding/任务执行/新Skill注册）快速定位能力 | L1 |
| [skill-five-elements-model.md](ai-collaboration/skill-five-elements-model.md) | Skill 五要素模型：定义高质量 AI Skill 必须包含的五个核心要素 | L1 |
| [skill-three-layer-value-model.md](ai-collaboration/skill-three-layer-value-model.md) | AI Skill 三层价值模型：能力层快速贬值，判断层和风格层是持续竞争优势 | L2 |
| [source-anchor-verification-protocol.md](ai-collaboration/source-anchor-verification-protocol.md) | 源码锚点二次校验协议：研究阶段产出的行号/API签名/文件路径须标注校验状态（✅已校验/⚠️未校验/🔍待校验），编写sub-agent根据状态决策是否二次校验 | L1 |
| [spec-driven-batch-doc-generation.md](ai-collaboration/spec-driven-batch-doc-generation.md) | Spec驱动+知识库驱动的文档批量产出模式：知识库素材+统一模板+并行Agent+统一验证（L2扩展：研究-契约-编写三阶段） | L2 |
| [spec-mode-doc-creation-workflow.md](ai-collaboration/spec-mode-doc-creation-workflow.md) | Spec Mode文档创建工作流：前置规划（阶段0内容提取→阶段1规范阅读）→阶段2 Spec三件套→阶段3原子执行→阶段4即时验证→阶段5门禁验证，五阶段闭环 | L2 |
| [style-creativity-separation-control.md](ai-collaboration/style-creativity-separation-control.md) | 风格-创意分离控制：正向约束控风格一致性 + 负向约束（禁止复刻清单）保创意多样性 | L2 |
| [subagent-atomic-task-template.md](ai-collaboration/subagent-atomic-task-template.md) | 子代理原子任务描述模板：六要素精确委托法（路径+frontmatter+大纲+导航+硬约束+Mermaid规则）消除歧义 | L2 |
| [symptom-prescription-qa.md](ai-collaboration/symptom-prescription-qa.md) | 症状-处方 QA 系统：故障诊断手册式 QA，每条症状对应可执行修改指令，Agent 可自主闭环 | L2 |
| [task-type-precheck-bias-defense.md](ai-collaboration/task-type-precheck-bias-defense.md) | 任务类型预检防偏差：对抗就近直觉偏差的防御机制，文件搜索前先做任务类型匹配 | L1 |
| [template-variance-control.md](ai-collaboration/template-variance-control.md) | 模板质量方差控制模式：保证一类产出物质量下限、降低不同执行者之间质量方差 | L1 |
| [team-shared-ai-colleague.md](ai-collaboration/team-shared-ai-colleague.md) | 团队共享 AI 同事模式：从个人独占式聊天窗口到频道共享同一 AI，上下文共享+角色分工+知识沉淀三位一体 | L2 |
| [two-stage-outline-then-expand.md](ai-collaboration/two-stage-outline-then-expand.md) | 篇幅控制两阶段模式：阶段1输出大纲→主代理审核→阶段2按大纲展开正文，避免子代理一次性长文跑偏 | L1 |
| [ambient-proactive-agent.md](ai-collaboration/ambient-proactive-agent.md) | 主动介入 Agent 模式：AI 从被动响应到主动介入，主动监测→主动介入→主动汇报，异步执行后主动通知 | L2 |
| [ai-agent-workspace-handbook.md](ai-collaboration/ai-agent-workspace-handbook.md) | AI Agent 工作手册模式：.agents/ 目录存放面向智能体的架构/约束/命令/排障文档，让 AI 高效参与项目 | L1 |
| [batched-creation-independent-review.md](ai-collaboration/batched-creation-independent-review.md) | 分批创作+独立质检模式：长文档分N批委托子代理创作，独立质检子代理按checklist统一检查，突破上下文限制并捕获创作者自查盲区 | L2 |
| [user-sovereignty-default.md](ai-collaboration/user-sovereignty-default.md) | 用户主权默认模式：被代理方始终拥有最高权限，操作可见+可感知+可干预+可终止，代理系统的核心信任设计原则 | L1 |
| [non-intrusive-security-ux.md](ai-collaboration/non-intrusive-security-ux.md) | 安全不打扰UX模式：默认安全但验证只在风险场景触发，风险分级响应矩阵+信任累积机制，平衡安全与效率 | L2 |
| [fine-grained-least-privilege.md](ai-collaboration/fine-grained-least-privilege.md) | 细粒度最小权限模式：权限四级拆解(L0-L3)+授权生命周期管理(默认最小→按需申请→用完收回)，PoLP原则在Agent系统中的操作化落地 | L1 |
| [gotchas-domain-specialization.md](ai-collaboration/gotchas-domain-specialization.md) | Gotchas 领域特化：在 SKILL-TEMPLATE.md 通用 Gotchas 框架基础上，为模块级 Skill 新增领域特化小节（12.4），补充模块特有陷阱与反直觉行为 | L1 |
| [module-level-agents-extension.md](ai-collaboration/module-level-agents-extension.md) | 模块级 .agents/ 扩展模式：子模块通过 extends 继承父角色，仅补充模块特化职责和技能，避免重复定义和维护成本翻倍 | L1 |
| [references-progressive-disclosure.md](ai-collaboration/references-progressive-disclosure.md) | references/ 渐进式披露：通过 references/index.md 引用已有知识文档，避免 SKILL.md 中内容复制导致的信息不一致和维护成本翻倍 | L1 |
| [visual-universal-operation.md](ai-collaboration/visual-universal-operation.md) | 视觉通用操作模式：AI通过屏幕视觉识别+键鼠模拟操作任意异构系统（不依赖API），四层架构+操作后验证+人在回路兜底，是AI Agent操作闭源/遗留系统的务实路线 | L2 |
| [output-format-collaboration-capability.md](ai-collaboration/output-format-collaboration-capability.md) | 输出格式-协作能力映射：输出格式决定协作可能性，云文档链接>真文件格式>Markdown>纯文本，格式即承诺 | L2 |
| [ecosystem-barrier-evaluation.md](ai-collaboration/ecosystem-barrier-evaluation.md) | 生态壁垒评估框架：AI Agent的长期竞争力取决于底层生态的深度和广度，生态深度不可速成，评估应看生态而非仅看模型能力 | L2 |

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
| [spec-driven-development.md](creative-design/spec-driven-development.md) | Spec-driven 开发流程，"先设计后实施"的完整方法论 | L3 |
| [visual-atomization-principle.md](creative-design/visual-atomization-principle.md) | 视觉原子化原则：一张图一个认知锚点，跨领域同构验证文档与视觉原子化 | L2 |

---

## product-growth — 产品开发与竞争策略

**核心关注点**：围绕产品定位、赛事运营增长、竞争策略博弈、交付流水线管控的业务模式。

**边界说明**：包含赛事增长飞轮模型、可控UGC传播杠杆、漏斗孔径设计、定位漂移修正、零和规则反利用、三层递进交付流水线、Spec九节叙事弧；不包含文档架构模式、AI协作提示词或工具工程实现。

| 模式文件 | 一句话说明 | 成熟度 |
|---------|-----------|-------|
| [contest-funnel-aperture.md](product-growth/contest-funnel-aperture.md) | 赛事漏斗孔径设计，每层最优「筛孔径」与衔接原则 | L1 |
| [contest-growth-flywheel.md](product-growth/contest-growth-flywheel.md) | 赛事增长飞轮模型，将参赛步骤映射为产品增长触点 | L1 |
| [controlled-uncontrollable-ugc-rules.md](product-growth/controlled-uncontrollable-ugc-rules.md) | 「可控的不可控」UGC 传播杠杆，精细化规则引导用户自主传播 | L1 |
| [positioning-drift-correction.md](product-growth/positioning-drift-correction.md) | 定位漂移修正法：三阶段（识别→剥离→重构）修正产品定位中"借用外部标签"导致的品类窄化与时效风险 | L1 |
| [spec-nine-section-narrative.md](product-growth/spec-nine-section-narrative.md) | Spec九节叙事弧：产品定义的完整Checklist（定位→功能→交互→内容→留存→合规→商业→技术→价值） | L2 |
| [three-layer-delivery-pipeline.md](product-growth/three-layer-delivery-pipeline.md) | 三层递进流水线：文档先行→原型验证→对外包装，严格顺序禁止颠倒，防止过度承诺 | L3 |
| [zero-sum-rule-inversion.md](product-growth/zero-sum-rule-inversion.md) | 零和规则反利用：将竞争场景中的限制性条款从障碍转换为策略聚焦器，在 Best Shot 模式下最大化先发优势的边际回报 | L1 |
| [software-company-hardware-entry-framework.md](product-growth/software-company-hardware-entry-framework.md) | 软件公司跨界硬件5步切入框架：生态引流→体验降维→场景闭环→定价下沉→生态协同，用软件优势重构硬件体验 | L2 |
| [hardware-generic-interface-service-differentiation.md](product-growth/hardware-generic-interface-service-differentiation.md) | 硬件通用接口+服务差异化：硬件层遵循通用标准降低门槛，软件/服务层构建差异化壁垒，硬件引流+服务变现 | L2 |
| [scenario-driven-parameter-tradeoff.md](product-growth/scenario-driven-parameter-tradeoff.md) | 场景驱动参数取舍：不为参数表堆料，每个参数锚定目标场景回答"是否需要"，保守选择降低成本/功耗/故障率 | L1 |
| [dual-product-matrix-portable-comfort.md](product-growth/dual-product-matrix-portable-comfort.md) | 消费电子双产品矩阵：入门便携款（低门槛引流）+进阶舒适款（高品质变现），参数形成鲜明反差而非同质化竞争，共享软件生态 | L1 |
| [parameter-difference-quantification.md](product-growth/parameter-difference-quantification.md) | 参数差异量化方法：不满足定性描述，计算量化差异倍数，≥10倍数量级差异暗示技术架构根本不同，数字必须场景化翻译为体验差异 | L1 |
| [saas-hardware-three-layer-funnel.md](product-growth/saas-hardware-three-layer-funnel.md) | SaaS硬件三层漏斗黄金范式：软件引流→硬件变现→服务留存（含AI服务/企业订阅四收入支柱），硬件是生态物理增强器而非独立产品，跨12个产品/场景验证（L3标准化） | L3 |
| [three-tier-iot-architecture.md](product-growth/three-tier-iot-architecture.md) | 三层IoT技术架构范式：硬件端极简+App端灵活+云端增值，三层职责分离避免某层承担过多职责，全系列硬件8次验证 | L2 |
| [local-capability-guarantee.md](product-growth/local-capability-guarantee.md) | 本地能力保底云端增强：核心功能离线可用不依赖云端，云端提供AI/协同/增值能力，是建立用户长期信任的关键设计原则（6次验证） | L2 |
| [dual-version-matrix-entry-professional.md](product-growth/dual-version-matrix-entry-professional.md) | 双版本矩阵通用策略：入门版覆盖（低门槛扩大基数）+专业版变现（高ARPU利润），五原则（卖点互补/不阉割核心/2-4倍价差/共享生态/升级顺畅），跨软件硬件10个行业案例验证 | L2 |
| [vertical-saas-mcp-capability-exposure.md](product-growth/vertical-saas-mcp-capability-exposure.md) | 垂直SaaS AI转型务实路径：不做通用大模型，通过MCP协议开放核心领域能力给Claude/GPT等通用大脑，六步MCP化转型+视觉兜底路径，4个行业可复用 | L2 |
| [professional-capability-democratization.md](product-growth/professional-capability-democratization.md) | 专业能力平民化增量市场框架：五维下沉分析（价格/人员/场景/配置/管理），保留完整专业能力+体验重构+成本重构开辟增量蓝海，8次跨产品验证 | L2 |
| [hardware-price-scenario-matrix.md](product-growth/hardware-price-scenario-matrix.md) | 硬件产品线价格梯度×场景细分矩阵：全价位段覆盖+场景精准切割，核心架构共享+功能模块差异化，入门款保留核心价值 | L1 |
| [compliance-pre-positioning.md](product-growth/compliance-pre-positioning.md) | 合规资质前置：To B产品从入场券到竞争壁垒的五层跃迁——准入资质→内生合规→国产化适配→资质前置展示→主动审计开放 | L1 |
