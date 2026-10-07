---
id: "starter-walkthrough-readme"
title: "演练剧本总览：规格驱动小任务（目录树查看器）"
source: "原创（Agent Workspace Starter）"
created_at: "2026-10-07"
---

# 演练剧本：规格驱动小任务

> 对应教程 `../guide/02-first-task.md`（25 分钟段位）。本目录是一份**可从零照抄**的端到端剧本：
> 先写规格（spec）→ 再实施 → 最后验收，全程无需第三方依赖、无需联网。

## 一、任务书（一句话）

> 用规格驱动方式实现单文件 Python 小工具 `tree_view.py`：扫描指定目录并按缩进输出目录树，
> 支持 `--max-depth` 限制层级；先写 `spec.md`（目标 + 功能需求 + 验收标准），再实施，最后运行验证。

## 二、完成后你能得到什么

- 一份可复用的 `spec.md` —— 学会把「一句话需求」拆成目标 / 功能需求 / 可验收标准
- 一个能跑的小工具 `tree_view.py` —— 仅标准库，Python 3.10+，Windows 可运行
- 一次真实验收记录 —— 用 Given-When-Then 逐条核对，而不是「看起来对了」
- 一条完整链路认知：任务书 → spec → 实施 → 产出物 → 验收

## 三、4 项产出物清单

| # | 产出物 | 形态 | 验收方式 |
|---|---|---|---|
| 1 | `spec/tree-viewer/spec.md` | 目标 / 功能需求（FR-1~3）/ 验收标准（AC-1~3，Given-When-Then） | 三类章节齐备 |
| 2 | `tree_view.py` | 单文件实现，仅标准库 `os` / `argparse` | 无第三方 import |
| 3 | 运行输出样例 | `python tree_view.py . --max-depth 2` 的缩进树文本 | 层级与缩进匹配 |
| 4 | 验收记录 | 3 条 AC 的逐条核对结果 | 3/3 勾选 |

## 四、7 步导航

| 步 | 动作 | 在哪做 | 验收点 |
|---|---|---|---|
| 1 | 读任务书，复述 1 个目标 + 3 条 AC | 本文件 §一 | 能说清「做什么」 |
| 2 | 写 spec | [step-1-write-spec.md](step-1-write-spec.md) | 落盘 `spec/tree-viewer/spec.md` |
| 3 | 创建前预检两问 | [step-1-write-spec.md](step-1-write-spec.md) §三 | 位置 + 格式两问通过 |
| 4 | 实施工具 | [step-2-implement.md](step-2-implement.md) | `tree_view.py` 存在且无第三方依赖 |
| 5 | 运行验证 | [step-2-implement.md](step-2-implement.md) §四-五 | 输出缩进树，无 traceback |
| 6 | 验收核对 | [step-3-verify.md](step-3-verify.md) §二 | 3/3 AC 勾选 |
| 7 | （可选）交接 | [step-3-verify.md](step-3-verify.md) §四 | 产出交接记录一份 |

> 步骤 1 在本文件完成；步骤 2-3 在 step-1；步骤 4-5 在 step-2；步骤 6-7 在 step-3。

## 五、25 分钟时间分配建议

| 时段 | 分钟 | 动作 |
|---|---|---|
| 读任务书 | 2 | 复述目标与 3 条 AC |
| 写 spec | 8 | 照抄 spec 骨架并落盘 |
| 实施 | 8 | 写 `tree_view.py` |
| 运行验证 | 4 | 跑命令看输出 |
| 验收核对 | 3 | 逐条勾选 AC，记录结果 |

## 六、配套参考（starter 内）

- 规格标准章节结构：[../starter/.agents/rules/spec-writing-guide.md](../starter/.agents/rules/spec-writing-guide.md)
- 创建前预检规则：[../starter/.agents/rules/spec-creation-precheck.md](../starter/.agents/rules/spec-creation-precheck.md)
- 任务模板：[../starter/.agents/templates/task-template.md](../starter/.agents/templates/task-template.md)
- 交接模板：[../starter/.agents/templates/handoff-template.md](../starter/.agents/templates/handoff-template.md)