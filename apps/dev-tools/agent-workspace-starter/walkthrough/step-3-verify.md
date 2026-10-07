---
id: "starter-walkthrough-step-3-verify"
title: "演练第 3 步：验收（AC 逐条核对）"
source: "原创（Agent Workspace Starter）"
created_at: "2026-10-07"
---

# 第 3 步 · 验收（AC 逐条核对）

## 一、步骤目标

不靠「看起来对了」，而是按 `spec.md` 的 3 条 AC 逐条复现并勾选，形成可追溯的验收记录。

## 二、3 条 AC 逐条核对表

| AC | Given | When | Then | 实际结果 | 结论 |
|---|---|---|---|---|---|
| AC-1 基础输出 | 目录 `demo/`（`README.md` + `src/main.py`） | `python tree_view.py demo --max-depth 2` | 出现 `demo/`、缩进的 `README.md`、`src/` 与再缩进的 `main.py` | 与预期一致，缩进 4 空格 | ☑ |
| AC-2 深度限制 | 目录层级 ≥3 | `python tree_view.py demo --max-depth 2` | 仅至多 2 层子项 | 第 3 层未出现 | ☑ |
| AC-3 异常处理 | `not-exist/` 不存在 | `python tree_view.py not-exist` | 打印错误提示，退出码 2 | 打印「错误：目录不存在 -> not-exist」，退出码 2 | ☑ |

> AC-3 复核命令（PowerShell 查看退出码）：

```powershell
python tree_view.py not-exist; $LASTEXITCODE
```

## 三、完成检查

- [ ] AC-1 勾选（基础输出正确）
- [ ] AC-2 勾选（深度限制生效）
- [ ] AC-3 勾选（异常退出码为 2）
- [ ] `spec/tree-viewer/spec.md` 与 `tree_view.py` 均在位
- [ ] 4 项产出物齐备（spec / 工具 / 输出样例 / 验收记录）

**3/3 勾选 → 本次演练完成。**

## 四、可选：交接记录

若要把成果交给他人（或另一个智能体），按 [../starter/.agents/templates/handoff-template.md](../starter/.agents/templates/handoff-template.md) 写一份交接记录：

```markdown
## 任务上下文
交接方: 你
接收方: 协作者
任务名称: 目录树查看器（tree_view.py）
交接时间: 2026-10-07

## 已完成工作
- [x] 写 spec：spec/tree-viewer/spec.md
- [x] 实施：tree_view.py
- [x] 验收：3/3 AC 勾选

## 待办事项
- [ ] （可选）扩展 `--show-file-size` 选项

## 风险提示
- 超大目录（>10 万项）输出较慢，建议配合 `--max-depth` 使用
```

## 五、验收点（可勾选）

- [ ] 3 条 AC 均有实际结果记录，非空勾
- [ ] 交接记录（可选）已产出
- [ ] 记录中无「应该 / 大概」等模糊结论