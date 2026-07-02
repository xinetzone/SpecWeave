---
id: "meta-feedback-wording-diagnosis"
title: "Meta洞察4：用户反馈措辞是诊断线索——快速分类问题类型"
source: "../insight-extraction.md#发现9用户纠错的问题措辞是诊断线索"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/tools-and-automation/retrospective-forum-posting-skill-optimization-20260629/insights/meta-04-feedback-wording-diagnosis.toml"
---
# Meta洞察4：用户反馈措辞是诊断线索——快速分类问题类型

→ 正式模式：[feedback-wording-diagnosis.md](../../../../../patterns/methodology-patterns/governance-strategy/feedback-wording-diagnosis.md)（已入库L1）

## 事件事实

用户问的不是"你为什么这样优化"（结果导向），而是"为何没有使用skill-creator"（流程导向）。

## 信号解读

这个问题措辞本身揭示了问题性质：**不是结果质量问题，而是流程合规问题**。即使用户没有明说"你违反了三层路由"，"为何没有使用X"这个句式直接指向"存在一个既定的X应该被使用但你没用"。

## 反馈措辞→问题类型映射

| 用户反馈措辞模式 | 问题类型 | 优先排查方向 |
|----------------|---------|------------|
| "为何没有X？"、"为什么不用X？" | **流程缺失** | 检查协议合规性、是否遗漏了规定步骤/工具/规范 |
| "X不好用"、"X有问题"、"X出错了" | **质量问题** | 检查实现正确性、边界情况处理、测试覆盖 |
| "X应该是Y"、"不是X是Y"、"我要的是Y" | **需求偏差** | 重新确认需求理解、检查需求对齐情况 |

## 应用方法

收到用户反馈时，首先分析反馈的"问题类型"（流程/质量/需求），再决定响应方式：
1. **流程缺失类**：不要先急着改结果，先检查协议合规性，补走遗漏流程，再基于正确流程重新审视结果
2. **质量问题类**：直接定位代码/文档缺陷，修复并补充测试
3. **需求偏差类**：暂停实现，重新确认需求，对齐后再继续

## 关联洞察

- [meta-01-process-vs-experience.md](meta-01-process-vs-experience.md) — 流程合规vs结果质量的优先级

---
*来源：[forum-posting Skill优化复盘](../README.md)*
