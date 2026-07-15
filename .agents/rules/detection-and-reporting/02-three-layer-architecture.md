---
id: "rules-detection-reporting-02-three-layer-architecture"
title: "检测与报告机制：三层检测体系架构"
source: "rules/detection-and-reporting.md#三层检测体系架构"
x-toml-ref: "../../../.meta/toml/.agents/rules/detection-and-reporting/02-three-layer-architecture.toml"
---
# 检测与报告机制：三层检测体系架构

三层检测体系按照执行时序与介入深度递进排列。第一层自动化扫描承担大规模初筛职责，第二层人工审查负责语义级深度判断，第三层定期报告则从宏观视角提供治理数据与趋势洞察。

```mermaid
flowchart TD
    subgraph L1["第一层：自动化扫描（CI 流程）"]
        A1["代码提交 / PR 创建"] --> A2["触发扫描任务"]
        A2 --> A3["正则模式扫描 + 自定义规则集"]
        A3 --> A4{"结果分级"}
        A4 -->|"ERROR"| A5["阻断合并"]
        A4 -->|"WARNING"| A6["标记不阻断"]
        A4 -->|"INFO"| A7["仅记录"]
    end
    subgraph L2["第二层：人工审查（Code Review）"]
        B1["Reviewer 接收 PR"] --> B2["查看自动扫描结果"]
        B2 --> B3["按检查清单逐项审查"]
        B3 --> B4["关注自动化工具无法检测的语义级硬编码"]
        B4 --> B5{"评分判定"}
        B5 -->|"≥ 1.5"| B6["通过"]
        B5 -->|"1.0 ~ 1.5"| B7["修改后通过"]
        B5 -->|"< 1.0"| B8["驳回"]
    end
    subgraph L3["第三层：定期报告（迭代周期）"]
        C1["收集扫描日志与审查记录"] --> C2["统计新增、修复、例外状态"]
        C2 --> C3["生成趋势报告"]
        C3 --> C4["团队复盘 → 改进措施"]
    end
    L1 --> L2
    L2 --> L3
```

三层体系的分工原则：

| 层级 | 介入时机 | 覆盖范围 | 判定精度 | 阻断能力 |
|---|---|---|---|---|
| 自动化扫描 | pre-commit / PR 提交 | 全量代码变更 | 高（模式匹配） | 可阻断 ERROR 级别 |
| 人工审查 | Code Review | 语义级硬编码 | 最高（人工判断） | 可拒绝合并 |
| 定期报告 | 迭代周期结束 | 全仓库累积数据 | 宏观统计 | 驱动流程改进 |
---
## 相关模式

- [多信号检测](../../docs/retrospective/patterns/methodology-patterns/tools-automation/multi-signal-detection.md)
- [周期检查缓存](../../docs/retrospective/patterns/code-patterns/periodic-check-caching.md)
---
← 上一章: [01 规范说明](01-overview.md) | **[返回索引](../detection-and-reporting.md)** | 下一章 → [03 自动化扫描规范](03-automated-scanning.md)
