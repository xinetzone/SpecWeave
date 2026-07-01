---
id: "retrospective-report-tool-entropy-nonlinear-optimization-execution"
source: "docs/retrospective/reports/retrospective-report-tool-entropy-nonlinear-optimization.md#三、最优规模阈值"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/reports/project-governance/tools-and-automation/retrospective-report-tool-entropy-nonlinear-optimization/execution-retrospective.toml"
---
# 执行复盘

## 最优规模阈值

根据本项目实证数据，工具链的最优规模约为 **5-6 个脚本**。超过此阈值后，应优先考虑以下策略：

| 策略 | 适用场景 | 示例 |
|------|---------|------|
| 合并重构 | 多个工具存在 ≥ 30% 功能重叠 | 将 check-role-permissions 与 check-spec-consistency 合并为统一的 spec-validator |
| 配置化 | 多个工具共享相同的执行框架但参数不同 | 将多个 check-*.py 统一为单一的 check 命令 + 配置文件 |
| 优先级排序 | 资源有限时聚焦高 ROI 工具 | 优先维护 ROI > 10x 的工具，低 ROI 工具降级为手动检查清单 |

## 量化决策模型

该发现已被纳入 [工具自动化决策模型](../../../../patterns/methodology-patterns/tools-automation/tool-automation-decision-model.md)，核心公式为：

```
手动总成本 = 操作频率 × 单次耗时 × 预期生命周期
熵减收益   = 手动总成本 - 工具开发成本
工具 ROI   = 熵减收益 / 工具开发成本
```

### 决策规则

| 条件 | 决策 |
|------|------|
| 手动执行次数 < 3 | 继续观察，不开发工具 |
| ROI < 3 | 优先流程改进，而非自动化 |
| ROI ≥ 3 且工具链 < 6 | 启动工具开发 |
| ROI ≥ 3 但工具链 ≥ 6 | 先审计功能重叠，优先合并而非新增 |