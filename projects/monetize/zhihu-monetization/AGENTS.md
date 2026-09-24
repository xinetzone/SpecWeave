---
title: "知乎变现执行工作区 · 智能体入口"
date: 2026-09-23
updated: 2026-09-23
rule_snapshot: "2026-09-23（创作打卡挑战赛第五十三期进行中；科学季报名窗 9.3–9.30，活动窗 09.30–10.30 未开启）"
status: flagged
stale_after: 2026-12-31
source: "定义层：docs/retrospective/reports/competitive-analysis/zhihu-monetization-path-20260923/；知识层：projects/awesome-okf-xs/doc/bundles/sheke/industry/zhihu-monetization/"
tags: [知乎, 变现, 执行工作区, 智能体入口]
---

# 知乎变现执行工作区 · 智能体入口

> **本文件是什么**：`projects/monetize/zhihu-monetization/` 的智能体入口。进入本目录前先读本文件，再按「五、路由表」定位事实来源；本工作区只承载**执行状态与记录**，不复制定义层与知识层正文。

## 一、项目定位

- 位于 `projects/monetize/zhihu-monetization/`，归属 **projects 区域**（容器路由见 [../AGENTS.md](../AGENTS.md)；区域路由见 [../../AGENTS.md](../../AGENTS.md)、目录总览见 [../../README.md](../../README.md)——均已登记本项目）。
- **形态：主仓库直接跟踪的普通目录（非 git 子模块）**，文件直接纳入主仓库版本控制，形态参照 `projects/tvm-ffi`；不受 projects 区域「子模块不可直接修改」条款约束。
- 定位：把定义层的行动清单落成可勾选、可记录、可复核的执行台账——**执行层工作区**，不生产新的事实口径。

## 二、文件地图

| 文件 | 职责 | 读写纪律 |
|---|---|---|
| `README.md` | 入口与链接矩阵 | **只读参考**——导航性质，不承载执行状态 |
| `tracker.md` | 执行台账（行动项勾选与进度） | **可写**——须遵守勾选纪律：完成后勾选并加日期戳（如 `[x] 2026-09-24`），**不删除条目** |
| `records.md` | 记录表模板（到账记录等） | **可写**——仅保留表结构与占位，**真实数据一律写入 `local/`、不落本文件**；表头与列定义不擅改｜【V 修订·2026-09-23】与 README §四「真实数据写 `local/`」、`records.md` 顶部「零真实数据入库」对齐 |
| `content-plan.md` | 内容与选题规划框架：领域定位 / 问题池 / 双轨排期 / 模板 | **只读参考**——方法与模板；真实填写放 `local/`（不入库） |
| `local/` | 本地数据隔离区（截图、原始留痕等） | **禁入库**——仅 `local/README.md` 入库，其余内容永不提交 |
| `.gitignore` | 隔离规则（维持 `local/` 不入库） | 只随隔离需求变更 |

## 三、读写纪律

1. **可写**：`tracker.md` 与 `records.md`，且必须保持既有格式纪律（表头、编号、日期戳不擅改）。
2. **只读外链**：docs 报告与 bundle **一律只读外链**，不在本工作区复制或改写其正文。
3. **bundle 位于子模块内**（`projects/awesome-okf-xs/`），**禁止任何修改**；如需修订走子模块流程。
4. **禁止复制**：定义层（docs 报告）与知识层（bundle）正文不得粘贴进本工作区，保持单一可信源；唯**纪律条文与自检条目**可原文摘引，须标注「源文原文」并给出出处链接，不得改写或另立新规【V 修订·2026-09-23：明确「原文摘引 + 标注来源」的合法引用形态，与 P5「纪律不重定义」及 `records.md` §五 的引用体例对齐】。
5. **数字必须溯源**：任何平台口径数字（奖池、盐粒、门槛、时间窗）必须挂 **F 编号**并链接对应 bundle 页面，禁止裸写数字。

## 四、纪律传导（引用不重定义）

| 纪律 | 出处（引用，不重定义） |
|---|---|
| 勾选纪律（勾选 + 日期戳、不删除条目） | `tracker.md` 顶部声明 |
| 发布前三问自检 + 边缘场景留痕 | [主路径 §五](../../../docs/retrospective/reports/competitive-analysis/zhihu-monetization-path-20260923/ai-creator-main-path.md) |
| 规则快照 O-5（每期开赛重读活动页并存档快照；门槛逐期变动先例 F-067） | [docs TODO](../../../docs/retrospective/reports/competitive-analysis/zhihu-monetization-path-20260923/todo.md) |
| 时效强制复核 | 本文件 `status: flagged` + `stale_after: 2026-12-31`，到期强制复核规则快照 |
| 防画饼口径 | **奖池 ≠ 个人收益**；个人实得待验证，不得据活动页奖池推算个人收入 |

## 五、路由表（何处取何物）

| 需要什么 | 去哪里取 |
|---|---|
| 知识事实（F 编号、机制洞察、风险边界） | bundle 索引 [`../../awesome-okf-xs/doc/bundles/sheke/industry/zhihu-monetization/index.md`](../../awesome-okf-xs/doc/bundles/sheke/industry/zhihu-monetization/index.md) |
| 定义 / 验收标准 / 排期 / 风险 | docs 报告四篇：[README.md](../../../docs/retrospective/reports/competitive-analysis/zhihu-monetization-path-20260923/README.md)（三角色路径与轨道切换）、[ai-creator-main-path.md](../../../docs/retrospective/reports/competitive-analysis/zhihu-monetization-path-20260923/ai-creator-main-path.md)（主路径与 18 条行动项验收标准）、[risks-and-boundaries.md](../../../docs/retrospective/reports/competitive-analysis/zhihu-monetization-path-20260923/risks-and-boundaries.md)（风险与边界）、[todo.md](../../../docs/retrospective/reports/competitive-analysis/zhihu-monetization-path-20260923/todo.md)（日历排期视图） |
| 执行状态 / 记录数据 | 本工作区 `tracker.md` / `records.md` |
| projects 区域路由与目录总览 | [../../AGENTS.md](../../AGENTS.md) / [../../README.md](../../README.md) |