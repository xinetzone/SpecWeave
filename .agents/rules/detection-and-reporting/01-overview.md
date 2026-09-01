---
id: "rules-detection-reporting-01-overview"
title: "检测与报告机制：规范说明"
source: "rules/detection-and-reporting.md#检测与报告机制"
x-toml-ref: "../../../.meta/toml/.agents/rules/detection-and-reporting/01-overview.toml"
---
# 检测与报告机制：规范说明

本规范是硬编码治理规则体系中的检测与报告层文档，旨在建立硬编码问题的多层级发现、评估与上报机制。治理体系的有效性不仅取决于识别标准是否明确，更依赖于能否在开发流程的各个环节中及时发现硬编码问题、准确评估其风险等级，并形成可追溯、可对比的治理数据。

本规范覆盖以下三个层面：

1. **自动化扫描**：在代码提交与 CI 流水线中集成静态分析工具，实现无人工介入的检测与阻断；
2. **人工审查**：在 Code Review 阶段依据标准化检查清单进行语义级审查，弥补自动化工具的盲区；
3. **定期报告**：按迭代周期汇总统计数据，生成趋势报告供团队复盘与改进决策。

三者构成"自动初筛 → 人工深审 → 周期复盘"的完整闭环，确保硬编码问题在事前、事中、事后均有相应机制覆盖。
---
## 相关模式

- [多信号检测](../../../docs/retrospective/patterns/methodology-patterns/tools-automation/multi-signal-detection.md)
- [周期检查缓存](../../../docs/retrospective/patterns/code-patterns/periodic-check-caching.md)
---
**[返回索引](../detection-and-reporting.md)** | 下一章 → [02 三层检测体系架构](02-three-layer-architecture.md)
