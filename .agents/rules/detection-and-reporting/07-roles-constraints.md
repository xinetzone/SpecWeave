---
id: "rules-detection-reporting-07-roles-constraints"
title: "检测与报告机制：角色职责与使用约束"
source: "rules/detection-and-reporting.md#角色职责划分"
x-toml-ref: "../../../.meta/toml/.agents/rules/detection-and-reporting/07-roles-constraints.toml"
---
# 检测与报告机制：角色职责与使用约束

| 角色 | 自动化扫描阶段 | 人工审查阶段 | 定期报告阶段 |
|---|---|---|---|
| developer | 修复扫描发现的 ERROR 与 WARNING 级问题；必要时添加抑制注释与例外说明 | 回应 Reviewer 的修改建议；修正后重新提交 | 关注本人模块的数据趋势，主动清理存量硬编码 |
| reviewer | 查看扫描结果标注，核对抑制注释的合理性 | 依据检查清单逐项评分，给出审查结论与修改建议 | 汇总本周期审查数据，参与复盘讨论 |
| orchestrator | 确保 CI 流水线中硬编码检测步骤正确执行 | 协调 Reviewer 资源分配，对驳回 PR 发起的必要讨论进行仲裁 | 主持迭代复盘会议，推动改进措施的落地 |
| architect | — | 对存在技术分歧的替代方案作出最终决策 | 根据趋势报告评估是否需要新增或调整扫描规则 |

# 使用约束

1. **阻断不可绕过**：ERROR 级别的扫描结果必须修复，不得通过抑制注释或手动跳过 CI 步骤的方式规避阻断。
2. **审查不可跳过**：当 PR 涉及 3 个及以上文件变更或新增代码行数超过 100 行时，硬编码审查为必选项，不得省略。
3. **报告不可延迟**：迭代报告须在迭代回顾会前生成，缺失报告视为流程执行不完整。
4. **例外不可过期**：例外清单中所有条目必须在复审日期到期前完成复审更新，逾期条目视为无效并自动回归为 WARNING 级问题。
5. **规则集可演进**：扫描规则集应根据定期报告的趋势数据持续调整，添加新规则或调整现有规则的级别。规则变更需经 architect 审批后生效。

# 相关模式

- [多信号检测](../../../docs/retrospective/patterns/methodology-patterns/tools-automation/multi-signal-detection.md)
- [周期检查缓存](../../../docs/retrospective/patterns/code-patterns/periodic-check-caching.md)
---
## 相关模式

- [多信号检测](../../../docs/retrospective/patterns/methodology-patterns/tools-automation/multi-signal-detection.md)
- [周期检查缓存](../../../docs/retrospective/patterns/code-patterns/periodic-check-caching.md)
---
← 上一章: [06 工具集成建议](06-tool-integration.md) | **[返回索引](../detection-and-reporting.md)**
