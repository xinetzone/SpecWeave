---
title: "阅读运行报告"
category: "learning"
source: "https://www.minitap.ai/docs/minitest/runs/run-report"
x-toml-ref: "../../../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/03-running-tests/03-reading-run-report.toml"
date: "2026-07-07"
tags: ["minitest", "run-report", "运行报告", "verdict", "fix-prompt"]
summary: "详细介绍运行报告的结构，包括判定结果、验收标准列表、视频时间线、修复提示，以及无法处理状态的排查方法。"
---
> 来源：https://www.minitap.ai/docs/minitest/runs/run-report

# 阅读运行报告

运行报告是每个故事的视图：一个用户故事、一个构建、一个设备。通过点击运行视图中的任意行来打开它。

![Run report — left rail with per-story verdicts, right pane with criterion detail and video timeline](https://mintcdn.com/minitap-30239763/wLvqfpOkfUc7rcKB/minitest/images/run-report.png?w=2500&fit=max&auto=format&n=wLvqfpOkfUc7rcKB&q=85&s=8c8c21d5cb0448ee2d9b03370f2fa514)

*运行报告 — 左侧栏显示每个故事的判定结果，右侧窗格显示标准详情和视频时间线*

## 判定结果头部

- **✅ Passed（通过）** — 每个关键标准都成立。
- **⚠️ Warning（警告）** — 每个关键标准都成立，但至少有一个警告标准不成立。
- **❌ Failed（失败）** — 至少有一个关键标准不成立。
- **⚙️ Unprocessable（无法处理）** — Mini运行了故事但无法对其评分。

前三个是您需要分类的正常结果。**Unprocessable**意味着在测试甚至有机会之前就出了问题 — 请参阅[下文](#当判定结果为无法处理时)。

## 标准列表

每个标准都显示其状态和代理的证据：

- **✅ Passed（通过）** — 代理看到的符合预期的内容。
- **❌ Failed（失败）** — 预期内容与代理实际看到的内容对比，并附有固定在失败时刻的截图。
- **⚠️ Warning（警告）** — 该标准非关键但不成立。

点击任意标准可跳转到视频中的该时刻。

## 视频 + 时间线

代理操作应用的连续录制。下方的时间线标记了每个标准的开始/结束，因此您可以直接跳转到失败位置。

## 修复提示

每个失败的标准都有一个 **Copy fix prompt（复制修复提示）** 按钮。该提示是Mini在运行故事时编写的可直接粘贴的文本块，包含三部分内容：

1. **根本原因** — 出了什么问题以及为什么。
2. **复现步骤** — 代理进入失败状态的路径。
3. **具体的修复建议** — 一个起点，而非最终答案。

将其粘贴到Cursor或Claude Code中。您的IDE拥有代码库的其余上下文，因此修复提示加上该上下文通常足以让代理打开PR。

![Run report — Prompt to fix tab on a failed criterion with the Copy for Cursor / Claude button](https://mintcdn.com/minitap-30239763/wLvqfpOkfUc7rcKB/minitest/images/fix-prompt-criterion.png?w=2500&fit=max&auto=format&n=wLvqfpOkfUc7rcKB&q=85&s=785c900b240cae98357389ea031ff5d8)

*运行报告 — 失败标准上的"Prompt to fix"标签页，带有"Copy for Cursor / Claude"按钮*

修复提示故意采用散文形式 — 没有截图URL，没有日志转储。视频和上方的标准详情已经涵盖了证据；修复提示是您交给IDE的内容。

### 构建修复提示

当构建本身无法编译或安装时 — 与健康构建上的故事失败不同 — 构建状态面板会显示其自己的 **Copy fix prompt（复制修复提示）** 按钮。形式相同：根本原因、复现、建议修复。当运行显示为Unprocessable因为构建从未安装到设备上时使用它。

## 当判定结果为无法处理时

Unprocessable意味着Mini运行了故事但无法产生真实评分 — 每个验收标准最终要么无法评估，要么被上游的某些东西阻塞。头部解释了是哪种情况。常见情况：

- **构建损坏** — 无法安装、启动时崩溃、或bundle格式错误。打开构建面板并使用其修复提示。
- **登录失败** — Mini无法通过身份验证，因此下游的任何内容都无法测试。为用户故事附加一个可用的[配置文件](https://www.minitap.ai/docs/minitest/suite/anatomy#profiles)。
- **标准不适合应用** — 通常是从另一个应用复制的故事，或要求应用不做的事情的标准。编辑故事。
- **故事中途的硬阻塞** — 流程中较早的某些东西使所有剩余标准无法到达。第一个失败的标准是需要阅读的。

如果您在同一构建的多个故事中反复看到Unprocessable，请在怀疑套件之前先怀疑构建。

---

> **返回章节**：[测试运行总览 →](00-overview.md)
>
> **下一章**：[问题分类与集成 →](../04-triage-and-integrations/00-overview.md)
