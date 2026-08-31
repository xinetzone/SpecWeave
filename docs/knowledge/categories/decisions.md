---
type: Reference
title: "分类索引：decisions"
---

# 分类索引：decisions

- [返回分类总索引](../category-index.md)
- [返回知识库首页](../README.md)
- [按标签检索](../tags/README.md)

> 本分片收录 **1** 个子分类，共 **6** 条条目。

### decisions

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [ADR: libs/ 目录重命名为 vendor/](../decisions/libs-rename-to-vendor.md) | 记录将第三方依赖目录从 libs/ 重命名为 vendor/ 的架构决策及其理由 | 2026-06-23 | architecture、naming、directory、vendor、convention |
| [ADR: VsDevShell通用模块提取与NativeBuild推广决策](../decisions/nativebuild-vsdevshell-module-extraction.md) | 记录NativeBuild模块在vendor/flexloop推广评估中的三项关键决策：NativeBuild不直接推广到vendor、Conda逻辑不适配uv、提取VsDevShell为独立通用模块 | 2026-08-02 | native-build、powershell、module-design、visual-studio、conda、uv、decoupling |
| [SpecWeave 外部代理资产绑定边界](../decisions/p0-04-specweave-binding-decision.md) | 记录 chaos 与 SpecWeave 的跨工作区代理资产绑定决策，包括绑定路径、用途、访问顺序、适用边界和维护规则。 |  | - |
| [已批准治理 Specs 稳定决策集合](../decisions/p0-08-governance-specs-decisions.md) | 从 7 个已批准治理 specs 中提炼的稳定决策结论集合，覆盖协作文档三件套基线、临时知识库管道、归档自动化、SpecWeave 外部绑定、任务分类骨架、待办治理口径与归档优先级分级。 |  | - |
| [DAO Apps 商业计划书结论摘要](../decisions/p1-12-daoapps-business-plan.md) | DAO Apps 商业计划书结论，定义以「道法自然」为哲学基石的 AI 智能体应用生态，包含产品矩阵、商业模式、市场定位与 500 万元融资需求。 |  | - |
| [ADR: torch-dev 双索引下载与 CUDA 硬断言决策](../decisions/torch-dev-extra-index-cuda-assertion.md) | 记录 torch-dev 镜像构建中为解决 files.pythonhosted.org IPv6 不可达而引入 --extra-index-url 双索引下载，以及对抗审查后补充的 CUDA 编译版本硬断言，防止主索引故障时静默降级为 CPU 版 torch | 2026-08-20 | devcontainer、torch-dev、pip-mirror、cuda、extra-index、silent-downgrade、verify、镜像构建 |

---

*索引自动生成于 2026-08-21 15:32:36*
