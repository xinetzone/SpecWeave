---
id: "agent-workspace-starter-guide-readme"
title: "60 分钟上手路径总览——智能体工作区起步套件"
source: "原创（Agent Workspace Starter）"
created_at: "2026-10-07"
---

# 60 分钟上手路径总览

欢迎使用「智能体工作区起步套件」（Agent Workspace Starter）。本套件把 SpecWeave 中面向 AI 智能体的规范体系，萃取成一份可在 60 分钟内走完的学习路径：装载最小化工作区 → 跑通第一个规格驱动任务 → 拿到可验证的产出物。

## 学习路径（时间盒表）

| 段位 | 时长 | 教程文件 | 本段目标 | 本段产出（可观察） |
|---|---|---|---|---|
| 00 概览 | 10 min | [00-overview.md](00-overview.md) | 认识「根契约 + 规范容器」二元结构与类目地图 | 能说出 ≥5 个类目的作用 |
| 01 装载 | 15 min | [01-bootstrap.md](01-bootstrap.md) | 用一句话提示词把 starter 拷入自有项目并自检 | 自检脚本 exit 0；根 `AGENTS.md` 命中「启动协议」 |
| 02 首个任务 | 25 min | [02-first-task.md](02-first-task.md) | 按「规格驱动」四步完成一个小工具 | `spec/` + `tree_view.py` + 运行输出 + 验收记录 |
| 03 进阶 | 10 min | [03-next-steps.md](03-next-steps.md) | 选定 rules/protocols 深潜条目与后续路径 | 1 个深潜条目 + 一句话后续动作 |
| **合计** | **60 min** | — | — | — |

> 时间盒为学习节奏指引；每段末都有「完成检查点」，勾完再进入下一段。

## 前置条件

- 一个可装载智能体的工具（Trae 或兼容的 AI 编码工具）。
- 本套件文件已下载到本地（`starter/`、`guide/`、`walkthrough/`、`scripts/`）。
- 一个想让它变「规范」的自有项目目录（空目录亦可）。
- 无需第三方依赖：套件是纯 Markdown，自检脚本只用 Python 标准库（Python 3.10+）。

## 每段目标与产出

见上表。四段递进关系：

- 00 概览 → 只读不写，建立「这是什么样的工作区」的心智地图。
- 01 装载 → 把地图落到你自己的项目里，并程序化验证装载完整。
- 02 首个任务 → 用一次完整的小任务，体会「先写规格、再实施、后验收」。
- 03 进阶 → 从「能用」到「知道往哪深挖」。

## 走完之后你会得到什么

1. 一个已装载最小化智能体工作区的自有项目（根 `AGENTS.md` + `.agents/` 导览）。
2. 一份可复用的装载提示词（[../bootstrap-prompt.md](../bootstrap-prompt.md)）。
3. 一个跑通过一次「规格驱动开发」的小工具产出物与验收记录。
4. 一张清晰的后续深潜地图（rules / protocols 入口）。

---

下一段 → [00-overview.md](00-overview.md)（概览，10 分钟）