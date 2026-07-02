---
id: "finding-duplication-threshold"
title: "发现1：重复代码的\"3次阈值\"规律"
source: "../insight-extraction.md#发现-1重复代码的3-次阈值规律"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/tools-and-automation/retrospective-scripts-shared-lib-extraction-20260626/insights/finding-01-duplication-threshold.toml"
---
# 发现1：重复代码的"3次阈值"规律

→ 正式模式：[large-scale-duplication-elimination.md](../../../../../patterns/methodology-patterns/document-architecture/large-scale-duplication-elimination.md)（大规模重复消除五步法）

## 事件发现

本次审计识别的 12 类重复模式中，出现次数 ≥ 3 次的有 8 类（占 67%），且这些高频重复贡献了约 220 行（占 79%）的重复代码。

## 规律

当同一代码模式在项目中出现 3 次及以上时，表明它已从"偶发便利复制"演变为"系统性重复"，此时提取为共享函数的 ROI 转正。出现 1-2 次的重复可能是特定场景的合理复用，强行提取反而增加抽象成本。

## 量化阈值

| 出现次数 | 处理策略 |
|---------|---------|
| 1-2 次 | 可接受重复，暂不提取 |
| 3-5 次 | 触发审计，评估提取必要性 |
| 6+ 次 | 强制提取，延迟成本将指数增长 |

## 验证

本次 8 类高频重复（≥3 次）全部提取；4 类低频重复（1-2 次）中 2 类也因概念聚合而提取（`discover_spec_dirs`、`update_marker_region`）。后续执行复盘建议时，check-duplication.py 首次扫描即发现 `find_markdown_files` 在 2 个文件中重复（刚好触发阈值），也被提取到共享库。

## 关联洞察

- [finding-02-refactoring-bug-finder.md](finding-02-refactoring-bug-finder.md) — 重构价值不止于消除重复
- [law-01-duplication-entropy.md](law-01-duplication-entropy.md) — 重复量超线性增长的熵增定律解释了阈值必要性

---
*来源：[脚本共享库提取复盘](../README.md)*
