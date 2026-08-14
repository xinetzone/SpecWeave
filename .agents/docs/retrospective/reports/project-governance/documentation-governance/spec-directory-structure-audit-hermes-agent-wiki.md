---
id: "spec-directory-structure-audit-hermes-agent-wiki"
title: "spec 目录结构对比审计报告：hermes-agent-learning-wiki"
source: "check-spec-output-archive.py 校验结果 + git 提交历史（7b4a4629 → e58938c0）"
type: "Governance Audit Report"
description: "记录 .trae/specs/hermes-agent-learning-wiki 目录在 check-spec-output-archive 白名单校验下，从违规（FAIL）到修正（通过）的前后结构对比，供后续审计追溯"
date: "2026-08-10"
tags: ["spec治理", "spec-output-archive", "原子提交", "文档治理", "审计"]
status: "stable"
summary: "对比 hermes-agent-learning-wiki spec 目录在校验前后的文件结构：修正前含 adversarial-review.md 产出物（触发 FAIL），修正后仅保留 spec.md/tasks.md/checklist.md 白名单文件（通过）。产出物已归档至 docs/retrospective/reports/adversarial-reviews/"
last_verified: "2026-08-10"
---

# spec 目录结构对比审计报告：hermes-agent-learning-wiki

## 1. 审计背景

本次审计针对 `check-spec-output-archive.py`（[atomic-commit 规范](../../../../../skills/atomic-commit-cmd/SKILL.md) 的 spec 白名单校验）对 `.trae/specs/hermes-agent-learning-wiki/` 目录的校验结果。该脚本规定：**spec 规划目录仅允许保留 `spec.md / tasks.md / checklist.md / README.md / .gitkeep`**，其余分析报告、任务输出、文章内容等产出物必须归档至 `docs/` 对应目录。

初始提交（`7b4a4629`）将 `adversarial-review.md` 放入 spec 目录，触发校验 FAIL。本次审计记录该目录从违规到修正的全过程与前后结构对比，供后续审计追溯。

## 2. 校验规则（白名单）

| 允许保留 | 不允许保留（须归档） |
|---------|---------------------|
| `spec.md` / `tasks.md` / `checklist.md` / `README.md` / `.gitkeep` | `adversarial-review.md`、`analysis-report.md`、`task*-*.md`、`article-content.md`、`facts.md`、`insights.md`、`patterns.md`、`*report.md` 等产出物 |

> 校验脚本：`python .agents/scripts/check-spec-output-archive.py`

## 3. 前后结构对比

### 3.1 修正前（BEFORE）— 提交 `7b4a4629`

```
.trae/specs/hermes-agent-learning-wiki/
├── spec.md              ✅ 白名单文件
├── tasks.md             ✅ 白名单文件
├── checklist.md         ✅ 白名单文件
└── adversarial-review.md ❌ 产出物（触发 FAIL）
```

**校验结果**：
```
[FAIL] .trae\specs\hermes-agent-learning-wiki (✅已完成)
  产出物文件: adversarial-review.md
```

### 3.2 修正后（AFTER）— 提交 `e58938c0`

```
.trae/specs/hermes-agent-learning-wiki/
├── spec.md              ✅ 白名单文件
├── tasks.md             ✅ 白名单文件
└── checklist.md         ✅ 白名单文件
```

**校验结果**：`hermes-agent-learning-wiki` 不再出现在 FAIL 列表，完全通过。

### 3.3 结构对比速览

| 维度 | 修正前（7b4a4629） | 修正后（e58938c0） |
|------|-------------------|-------------------|
| spec 目录文件数 | 4 | 3 |
| 白名单合规文件 | spec.md / tasks.md / checklist.md | spec.md / tasks.md / checklist.md |
| 产出物遗留 | `adversarial-review.md` ❌ | 无 ✅ |
| check-spec-output-archive | FAIL | 通过 |

## 4. 产出物归档详情

| 字段 | 内容 |
|------|------|
| 原路径 | `.trae/specs/hermes-agent-learning-wiki/adversarial-review.md` |
| 归档路径 | `.agents/docs/retrospective/reports/adversarial-reviews/adversarial-review-20260810T000044Z.md` |
| 归档方式 | `git mv`（保留重命名追踪，`R100`） |
| 命名约定 | `adversarial-review-<UTC时间戳>Z.md`，与 `reports/adversarial-reviews/` 既有文件一致 |

## 5. 提交历史

| 提交 | 说明 | 状态 |
|------|------|------|
| `7b4a4629` | 初始提交：spec 目录混入 adversarial-review.md，校验 FAIL | 已修正（amend） |
| `e58938c0` | 修正提交：adversarial-review 归档至 docs，spec 目录合规 | ✅ 当前 HEAD |

> 修正采用 `git commit --amend` 保持历史干净（单一职责、无冗余提交）。两次提交均为 **31 files changed, 1992 insertions(+), 1 deletion(-)**。

## 6. 校验复验结果

```
检查摘要: 通过 330 项, 警告 4 项, 错误 56 项
```

- ✅ `hermes-agent-learning-wiki`（本审计对象）：**通过**，不在 FAIL 列表
- ⚠️ 全仓仍报 56 项错误，均为**其他历史 spec 目录的存量遗留问题**（如 `volcengine-agentkit-wiki`、`web-content-analysis`、`retrospectives-insights`、`standards-tools` 等），与本提交无关

## 7. 审计结论

1. **本次 spec 目录结构已完全合规**，通过 `check-spec-output-archive` 白名单校验。
2. 产出物已按项目约定归档至 `docs/retrospective/reports/adversarial-reviews/`，命名遵循 UTC 时间戳规范。
3. 提交历史经 amend 保持干净，可追溯、可回滚。

## 8. 后续改进建议（待办）

- [ ] 全仓仍存在 56 项历史 spec 产出物遗留（`volcengine-agentkit-wiki` 等），建议单独发起一轮"历史 spec 产出物归档"清理任务，统一执行 `git mv` 归档并 commit
- [ ] 清理完成后，可将 `check-spec-output-archive` 从 warn-only 升级为 error 门禁，强制约束未来提交

## 9. 相关资源

- [atomic-commit 规范（spec 白名单）](../../../../../skills/atomic-commit-cmd/SKILL.md)
- [归档后的对抗审查报告](../../adversarial-reviews/adversarial-review-20260810T000044Z.md)
- [spec 规划文档](../../../../../../.trae/specs/hermes-agent-learning-wiki/spec.md)
