---
id: "raci-law-02-r-not-equal-a"
title: "R≠A分离原则：执行与审批必须解耦"
source: "insight-extraction.md#law-02"
x-toml-ref: "../../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/process-and-compliance/retrospective-raci-governance-matrix-20260629/insights/law-02-r-not-equal-a.toml"
---
# R≠A分离原则：执行与审批必须解耦

## 规律陈述

执行操作类活动（代码实现、文件修改、提交等）必须遵循"执行者(R)≠审批者(A)"原则。developer执行→reviewer审批是标准模式，防止自我审批。

## 触发条件

- 活动涉及实际代码/文件/配置修改
- 活动产出物需要质量验收
- 定义审批层级模型

## 例外说明

reviewer独立执行的质量门禁类活动（如安全审计、常规检查）允许reviewer R/A，因为：
1. 不涉及修改产出物（仅检查和判断）
2. reviewer本身就是质量门禁角色
3. 这类活动的异常会升级到co-founder

## 正例

```markdown
| 代码实现 | I | C | **R** | **A** | I | I |  <!-- developer R, reviewer A -->
| 代码安全审查 | I | I | C | **R/A** | I | I |  <!-- reviewer自理 -->
```

## 反例（Layer 4修正前）

```markdown
| 执行操作层 | developer | developer | 代码实现...  <!-- R=A=developer，自我审批，违规 -->
```
