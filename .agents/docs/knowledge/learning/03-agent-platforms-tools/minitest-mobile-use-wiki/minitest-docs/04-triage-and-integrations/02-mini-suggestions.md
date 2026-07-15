---
title: "Mini改进建议"
category: "learning"
source: "https://www.minitap.ai/docs/minitest/triage/suggestions"
x-toml-ref: "../../../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/04-triage-and-integrations/02-mini-suggestions.toml"
date: "2026-07-07"
tags: ["minitest", "suggestions", "改进建议", "ux", "edge-cases"]
summary: "介绍Mini在测试过程中主动发现的UX问题和边缘情况，建议与问题的区别，以及建议的生命周期。"
---
> 来源：https://www.minitap.ai/docs/minitest/triage/suggestions

# Mini改进建议

在Mini运行您的用户故事时，它有时会注意到您没有要求它检查的事情。这些成为**建议（suggestions）**：一个与问题分开的收件箱，可选择是否采取行动，永远不会阻止发布。

这里最终出现的内容是开放式的。它可能是一个小的UI不一致、读起来奇怪的文案，或者关于功能在运行时实际行为的产品级观察。没有固定的分类法。如果Mini认为某些东西值得再看一眼，您会在这里看到它。

## 建议与问题的区别

### 问题（Issues）

失败的验收标准或Mini自己发现的bug。与用户故事关联，有判定结果。在[问题分类](https://www.minitap.ai/docs/minitest/triage/issues)中分类。

### 建议（Suggestions）

Mini在验收标准之外注意到的东西。没有判定结果，永远不会阻塞，存在于自己的标签页中。

两者都来自相同的运行。问题是出错的事情，无论您是否为其编写了标准。建议是Mini主动提出的观察。

## 建议存在的位置

在[仪表板](https://app.minitap.ai/)中，每个应用在侧边栏都有一个 **Suggestions（建议）** 标签页。该页面分为三个标签：

### 提议（Proposal）

新建议，等待您的决定。侧边栏徽标仅统计这些。

### 无用（Not useful）

您标记为不可操作的建议。它们在这里保持可见。

### 已确认（Acknowledged）

已阅读并接受，但您现在不打算做任何事情。

建议不会出现在运行报告、PR评论或Slack中。建议标签页是它们唯一存在的地方。

## 建议卡片上的内容

每张卡片显示一个简短标题、Mini的可选描述，以及观察到它的用户故事（如果Mini在故事之间注意到它，则显示"No linked story"）。您还会获得Mini注意到它的时刻的嵌入视频，以及平台和相同观察在运行中最后一次出现的时间。

建议上没有修复提示。它们是观察，而不是具有复现路径的失败。

## 建议如何停用

当Mini在接触应用该部分的故事中停止注意到某个建议时，该建议会自行消失。您无需采取任何行动。

将建议标记为**Not useful（无用）**不会抑制未来的观察。如果Mini在以后的运行中看到相同的东西，卡片会保留在您的Not useful标签页中，并带有新鲜的"last seen（最后出现）"时间。它不会弹回Proposal，但在Mini停止注意到它之前也不会消失。

## 舰队汇总

在[应用页面](https://app.minitap.ai/)上，每个应用都显示仍处于Proposal状态的建议计数 — 快速了解您整个舰队中有多少分类工作是开放的。如果您想专注于未处理建议最多的应用，可以按此过滤和排序。该计数永远不会阻塞任何事情。

---

> **下一章**：[Cursor和Claude集成 →](03-cursor-claude-integration.md)
