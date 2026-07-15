---
title: "问题分类"
category: "learning"
source: "https://www.minitap.ai/docs/minitest/triage/issues"
x-toml-ref: "../../../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/04-triage-and-integrations/01-triaging-issues.toml"
date: "2026-07-07"
tags: ["minitest", "issues", "triage", "问题分类", "bug", "criticality"]
summary: "详细介绍问题分类流程，包括问题结构、三种分类操作、严重性覆盖以及在仪表板和Slack中的分类方式。"
---
> 来源：https://www.minitap.ai/docs/minitest/triage/issues

# 问题分类

当一个标准失败时，miniTest会在 **Issues（问题）** 标签页中创建一个**issue（问题）**。每个失败的标准对应一个问题，跨运行去重，因此单个损坏的用户故事不会扩散成N个副本。

无论您在哪里 — 仪表板或Slack线程 — 分类工作方式都相同。状态在各界面之间共享，因此一个地方的操作会立即更新另一个地方。

![Issues tab — left rail lists issues with criticality + age, right pane shows before/after, expected/actual, and suggestions](https://mintcdn.com/minitap-30239763/wLvqfpOkfUc7rcKB/minitest/images/issues.png?w=2500&fit=max&auto=format&n=wLvqfpOkfUc7rcKB&q=85&s=707b37c57b46e7c11cabb74099bca15d)

*问题标签页 — 左侧栏按严重性和存在时间列出问题，右侧窗格显示前后对比、预期/实际情况和建议*

## 问题内部结构

### 标准（Criterion）

不成立的确切措辞。

### 严重性（Criticality）

`Critical（严重）`、`Warning（警告）`或`Pass（通过）`。由Mini根据观察到的情况推断，当推断不符合您的业务实际时，可以按问题覆盖。

### 状态（Status）

问题在下面分类工作流中的位置。

### 最后出现（Last seen）

问题复现的最近一次运行。

### 证据（Evidence）

失败的短视频片段，以及指向正确时刻的[运行报告](https://www.minitap.ai/docs/minitest/runs/run-report)的深层链接。

### 修复提示（Fix prompt）

与运行报告中相同的可粘贴块，一键即可获取。

## 分类操作

每个问题都显示三个按钮。选择一个 — 这就是整个循环。

### 确认（Acknowledge）

您已看到它；暂时没有其他要说的。问题在队列中保持打开状态。

### 非bug（Not a bug）

有意的更改、不稳定的标准、误报。系统会要求您提供简短说明，解释为什么这不是bug。该问题不再计入应用统计。

### 已解决（Resolved）

底层问题已修复。系统会要求您提供关于修复内容的反馈，下一次干净运行将真正关闭它。

每个已分类的问题都保留一个 **Back to review（返回审核）** 按钮，如果您改变主意，可以将其返回到打开队列。

您在**非bug**或**已解决**上写的每条备注都会反馈到[Mini的记忆](https://www.minitap.ai/docs/minitest/suite/mini-maintains-your-suite)中。下次它看到类似情况时，会参考您的推理，因此相同的误报不会第二次出现，相同的修复模式会为未来的建议提供信息。

## 覆盖严重性

Mini根据观察到的情况推断严重性，但您最了解您的产品。如果推断错误，请在问题本身上覆盖它：

- 一个看起来很小但保护收入的标准（`订单总额与商品总和匹配`）→ 提升为**严重（Critical）**。
- 一个看起来很严重但实际上是外观问题的标准（`显示一个小的"Beta"徽标`）→ 降级为**警告（Warning）**。

覆盖在该问题上是持久的，并反映在问题出现的所有地方。

## 问题存在的位置

### 在仪表板中

每个应用上的 **Issues（问题）** 标签页。左侧栏按严重性和存在时间列出未解决问题，右侧窗格显示标准、证据和分类操作。

### 在Slack中

相同的操作位于运行心跳线程中。在对话已存在的地方进行分类 — 点击时仪表板会立即更新。

---

> **下一章**：[Mini改进建议 →](02-mini-suggestions.md)
