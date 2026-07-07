# research-knowledge — 外部研究、信息获取与知识融合方法论

> 外部网站分析、竞品研究、vendor子模块学习、跨项目知识融合等依赖外部信息源和知识吸收的任务方法论

## 核心关注点

围绕外部信息获取、信息源分层兜底、访问障碍应对、多源交叉验证、vendor知识融合的研究方法论。

## 边界说明

包含外部网站访问受阻时的分层降级策略、信息源可信度评级、三角验证法在外部研究中的适配、vendor/外部知识融合三步流程；不包含内部知识复盘沉淀、文档架构治理、AI协作提示词设计或产品竞争策略本身。

## 模式清单

| 模式文件 | 一句话说明 | 成熟度 |
|---------|-----------|-------|
| [cross-vendor-knowledge-fusion.md](cross-vendor-knowledge-fusion.md) | 跨Vendor知识融合三步法：理解Vendor→认知自我→优势互补融合，避免"全盘照搬"和"NIH综合征"两个极端，融合后1+1>2 | L1 |
| [vendor-high-level-doc-first-research.md](vendor-high-level-doc-first-research.md) | Vendor仓库"自顶向下"研究法：先读AGENTS.md/CLAUDE.md等AI友好高层文档建立全局框架，再按需深入源码，效率提升5-10倍，基础设施故障时的救命稻草 | L2 |
| [external-website-analysis-fallback-strategy.md](external-website-analysis-fallback-strategy.md) | 外部网站分析四层信息源分层兜底策略（直接访问→工具增强→官方替代源→第三方权威源），含反自动化检测突破（40362/JS challenge）、云厂商SPA预判、控制台登录预判、工具间降级原则、浏览器MCP四步SOP、降级决策流程与三角验证SOP，2次实战验证（贝锐403+知乎反爬） | L2 |
| [small-sample-analysis-methodology.md](small-sample-analysis-methodology.md) | 小样本分析方法论与三层分析框架适用性边界：样本量<5时执行"保留/降级/标注"三规则，三层框架（系统性学习→深度洞察→知识萃取）各层降级映射，解决"分析精度 vs 原始内容信度"根本矛盾 | L1 |
| [progressive-spec-planning-for-external-content.md](progressive-spec-planning-for-external-content.md) | 外部内容分析渐进式Spec规划：三阶段时间盒（最小可行Spec 15min→内容获取试错30min→基于样本调整10min），核心原则"最小启动+渐进细化"，避免规划阶段耗时过长 | L1 |
| [external-article-deep-analysis-workflow.md](external-article-deep-analysis-workflow.md) | 外部文章深度分析端到端工作流：四阶段编排（defuddle获取→spec三件套→单一子智能体执行→Grep数据验证三查法），含14章节报告结构模板，4次验证（mattpocock/agent-reach/codex/mainecoon），质量可预测 | L2 |
| [external-article-deep-analysis-methodology.md](external-article-deep-analysis-methodology.md) | 外部文章深度分析方法论（六步法）：内容提取→观点提炼→逻辑分析→知识萃取→可靠性评估→批判性思考六步认知法，与端到端工作流互补（工作流聚焦"如何编排执行"，六步法聚焦"如何思考分析"），1次验证（mainecoon） | L1 |
| [entry-doc-mirror-analysis.md](entry-doc-mirror-analysis.md) | 入门文档镜像分析法：8维度信号清单+判断矩阵，系统性提取Vendor入门文档中的产品定位、能力边界、设计哲学信号 | L1 |
| [b2b-product-page-ux-five-dimensions.md](b2b-product-page-ux-five-dimensions.md) | ToB产品页UX分析五维框架（信息架构/价值传达/CTA策略/视觉呈现/信任背书），含AIDA模型对应关系、反模式识别、五维检查清单 | L2 |
| [b2b-product-seven-segment-ia.md](b2b-product-seven-segment-ia.md) | B端技术产品页面七段式认知递进信息架构（Hero→能力→优势→场景→架构→案例→CTA），严格遵循用户决策路径，含完整性检查清单和各段设计规范 | L2 |
| [b2b-value-quantification-case-validation.md](b2b-value-quantification-case-validation.md) | B端产品价值量化与案例验证双闭环模式：首屏量化亮剑→优势区解释→场景区匹配→案例区验证，形成"承诺→解释→场景→验证"完整证据链，解决空洞形容词和无效Logo墙问题 | L2 |
| [vendor-doc-info-compensation-search.md](vendor-doc-info-compensation-search.md) | 厂商技术文档信息补偿六源搜索策略：控制台需登录/文档截断时，按SDK/Skill→QuickStart→插件市场→GitHub→社区→博客优先级搜索补偿信息源，含Mermaid决策流程、DX机制解释、反模式清单 | L1 |
