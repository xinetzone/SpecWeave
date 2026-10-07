---
id: "agent-workspace-starter-guide-02-first-task"
title: "02 首个任务（25 分钟）——规格驱动开发"
source: "原创（Agent Workspace Starter）"
created_at: "2026-10-07"
---

# 02 首个任务（25 分钟）

**本段目标**：跟着演练剧本，用「规格驱动」方式完成第一个小任务，拿到可验证的产出物。

**前置**：01 装载完成——你的项目里已有 `AGENTS.md` 与 `.agents/`，自检脚本退出码为 0。

## 1. 什么是「规格驱动开发」

核心思想：**先写规格，再写实现，最后逐条验收**。智能体不是「凭感觉写代码」，而是对着你写下的规格干活，你也能逐条核对它是否达标。

四步：

1. **写 spec**：用一段话把任务写成 `spec.md`——目标 + 功能需求（FR）+ 验收标准（AC，Given/When/Then）。
2. **创建前预检**：在动手前核对 spec 的**位置**与**格式**是否符合规范，避免返工。
3. **实施**：按 spec 落实现代码/文档。
4. **验收**：逐条对照 AC 勾选，而不是「看起来能用」。

对应规范依据：[../starter/.agents/rules/spec-writing-guide.md](../starter/.agents/rules/spec-writing-guide.md)（Spec 标准章节结构）与 [../starter/.agents/rules/spec-creation-precheck.md](../starter/.agents/rules/spec-creation-precheck.md)（创建前位置/格式预检）。

## 2. 本次任务：目录树查看器

一句话任务书：

> 用规格驱动方式实现单文件 Python 小工具 `tree_view.py`：扫描指定目录并按缩进输出目录树，支持 `--max-depth` 限制层级；先写 `spec.md`，再实施，最后运行验证。

预期产出物（25 分钟内可完成）：

| # | 产出物 | 形态 | 验收方式 |
|---|---|---|---|
| 1 | `spec/tree-viewer/spec.md` | 目标 / FR-1~FR-3 / AC-1~AC-3 | 含三类章节，AC 可勾选 |
| 2 | `tree_view.py` | 单文件，仅标准库 | 存在且无第三方 import |
| 3 | 运行输出样例 | `--max-depth 2` 的缩进树 | 行数与层级匹配 |
| 4 | 验收记录 | 3 条 AC 逐条核对 | 3/3 勾选 |

## 3. 实操：跟着演练剧本走

完整剧本（含每步「照抄块」与可观察验收点）见 [../walkthrough/](../walkthrough/)（由并行任务产出）。

七步概览：

1. **读任务书**——复述 1 个目标 + 3 条 AC。
2. **写 spec**——照抄 spec 骨架，落到 `spec/tree-viewer/spec.md`。
3. **创建前预检**——核对位置与格式两问。
4. **实施**——照抄 `tree_view.py` 参考骨架，`import os, argparse`。
5. **运行验证**——`python tree_view.py . --max-depth 2`。
6. **验收核对**——AC 逐条 Given/When/Then 勾选。
7. **（可选）交接**——用 [../starter/.agents/templates/handoff-template.md](../starter/.agents/templates/handoff-template.md) 留一份交接记录。

**照抄（运行验证）：**

```powershell
python tree_view.py . --max-depth 2
```

**验收点**：终端输出缩进树，无 traceback。

> 关键体会：先写 spec 的 3 分钟，能省掉后面反复返工的 10 分钟。这就是工作区里 rules 想要的「可预测」。

## 4. 让智能体按工作区规范干活

在实际项目里，你可以把任务直接交给已装载的智能体，它会：

- 按 [../starter/.agents/context-routing.md](../starter/.agents/context-routing.md) 找到「功能开发」工作流；
- 按 [../starter/.agents/workflows/feature-development.md](../starter/.agents/workflows/feature-development.md) 走开发流程；
- 按 `rules/spec-writing-guide.md` 写 spec，按 `rules/spec-creation-precheck.md` 做预检。

参考路径：[../starter/.agents/workflows/](../starter/.agents/workflows/) 与 [../starter/.agents/context-routing.md](../starter/.agents/context-routing.md)。

## 完成检查点

- [ ] 能说出规格驱动开发的四步顺序。
- [ ] `spec/tree-viewer/spec.md` 已落盘，含目标 / FR / AC 三类章节。
- [ ] `tree_view.py` 已实现，无第三方依赖。
- [ ] 运行输出样例已保存，无 traceback。
- [ ] 3 条 AC 逐条核对，3/3 勾选。

---

下一段 → [03-next-steps.md](03-next-steps.md)（进阶，10 分钟）