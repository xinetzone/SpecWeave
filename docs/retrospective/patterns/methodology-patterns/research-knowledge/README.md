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
| [external-website-analysis-fallback-strategy.md](external-website-analysis-fallback-strategy.md) | 外部网站分析四层信息源分层兜底策略（直接访问→工具增强→官方替代源→第三方权威源），含反自动化检测突破（40362/JS challenge）、降级决策流程与三角验证SOP，2次实战验证（贝锐403+知乎反爬） | L2 |
| [small-sample-analysis-methodology.md](small-sample-analysis-methodology.md) | 小样本分析方法论与三层分析框架适用性边界：样本量<5时执行"保留/降级/标注"三规则，三层框架（系统性学习→深度洞察→知识萃取）各层降级映射，解决"分析精度 vs 原始内容信度"根本矛盾 | L1 |
| [progressive-spec-planning-for-external-content.md](progressive-spec-planning-for-external-content.md) | 外部内容分析渐进式Spec规划：三阶段时间盒（最小可行Spec 15min→内容获取试错30min→基于样本调整10min），核心原则"最小启动+渐进细化"，避免规划阶段耗时过长 | L1 |
