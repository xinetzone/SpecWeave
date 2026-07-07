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
| [external-website-analysis-fallback-strategy.md](external-website-analysis-fallback-strategy.md) | 外部网站分析四层信息源分层兜底策略（直接访问→工具增强→官方替代源→第三方权威源），含云厂商SPA预判、控制台登录预判、工具间降级原则、浏览器MCP四步SOP | L2 |
| [entry-doc-mirror-analysis.md](entry-doc-mirror-analysis.md) | 入口文档镜像分析法 | L1 |
| [b2b-product-page-ux-five-dimensions.md](b2b-product-page-ux-five-dimensions.md) | ToB产品页UX分析五维框架（信息架构/价值传达/CTA策略/视觉呈现/信任背书），含AIDA模型对应关系、反模式识别、五维检查清单 | L1 |
| [b2b-product-seven-segment-ia.md](b2b-product-seven-segment-ia.md) | B端技术产品页面七段式认知递进信息架构（Hero→能力→优势→场景→架构→案例→CTA），严格遵循用户决策路径，含完整性检查清单和各段设计规范 | L2 |
