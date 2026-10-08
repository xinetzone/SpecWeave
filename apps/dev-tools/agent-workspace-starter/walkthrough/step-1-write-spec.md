---
id: "starter-walkthrough-step-1-write-spec"
title: "演练第 1 步：写规格（spec.md）"
source: "原创（Agent Workspace Starter）"
created_at: "2026-10-07"
---

# 第 1 步 · 写规格（spec.md）

## 一、步骤目标

把「一句话任务书」转写成结构化规格：目标（Goals）+ 功能需求（FR）+ 可验收标准（AC）。
落盘到 `spec/tree-viewer/spec.md`。**先写规格、后写代码**，是本次演练的核心纪律。

## 二、照抄块：spec.md 完整样例

> 新建 `spec/tree-viewer/spec.md`，把下面全文复制进去即可（`source` 已标注为演练产物）。

```markdown
---
id: "tree-viewer-spec"
title: "目录树查看器（tree_view.py）"
source: "原创（Agent Workspace Starter 演练）"
created_at: "2026-10-07"
status: "draft"
---

# 目录树查看器 - Spec

## Overview

- **Summary**: 实现单文件 Python 小工具 `tree_view.py`，扫描指定目录并按缩进打印目录树。
- **Purpose**: 提供一个零依赖的目录结构可视化命令，用于快速理解项目布局。
- **Target Users**: 需要快速查看目录结构的开发者。

## Goals

- **G1**: 命令行调用即可输出指定目录的缩进树。
- **G2**: 支持 `--max-depth N` 限制展示层级，避免大目录刷屏。
- **G3**: 仅使用 Python 标准库，兼容 Python 3.10+，跨平台（含 Windows）。

## Functional Requirements

- **FR-1**: `python tree_view.py <dir>` 输出 `<dir>` 的目录树，目录名以 `/` 结尾，逐层缩进 4 空格。
- **FR-2**: 提供 `--max-depth N`，仅展示前 N 层（根目录为第 0 层）。
- **FR-3**: 目标目录不存在时，输出中文错误信息并以非 0 退出码结束。

## Acceptance Criteria

### AC-1: 基础输出

- **Type**: `rule`
- **Given**: 存在目录 `demo/`，内含 `README.md` 与子目录 `src/`（内含 `main.py`）
- **When**: 执行 `python tree_view.py demo --max-depth 2`
- **Then**: 输出包含 `demo/`、缩进后的 `README.md`、`src/` 与其下再缩进的 `main.py`
- **Pass Condition**: 每层缩进 4 空格，目录名带 `/` 后缀

### AC-2: 深度限制

- **Type**: `rule`
- **Given**: 目录 `demo/` 层级 ≥3
- **When**: 执行 `python tree_view.py demo --max-depth 2`
- **Then**: 仅出现至多 2 层子项，第 3 层及更深不出现
- **Pass Condition**: 输出行数不随更深层级增长

### AC-3: 异常处理

- **Type**: `rule`
- **Given**: 目标目录 `not-exist/` 不存在
- **When**: 执行 `python tree_view.py not-exist`
- **Then**: 打印错误提示，退出码为 2
- **Pass Condition**: `$LASTEXITCODE -eq 2`
```

## 三、创建前预检两问

创建 `spec.md` 前，先回答两问（依据 [../starter/.agents/rules/spec-creation-precheck.md](../starter/.agents/rules/spec-creation-precheck.md)）：

| # | 预检项 | 本演练的答案 |
|---|---|---|
| 1 | **位置**：spec 应放在哪？ | 自建 `spec/tree-viewer/spec.md`；单文件小任务无需主题子目录 README |
| 2 | **格式**：产物对齐哪份规范？ | 对齐 [../starter/.agents/rules/spec-writing-guide.md](../starter/.agents/rules/spec-writing-guide.md) 的标准章节；**只产出 `spec.md` 单文件**，不创建 `checklist.md` 等非规范产物 |

**两问都答得上 → 才允许落盘。**

## 四、操作说明

1. 在项目根下创建目录：`spec/tree-viewer/`
2. 新建文件 `spec/tree-viewer/spec.md`，粘贴 §二 全文并保存（UTF-8）
3. 通读一遍，确认 Goals 与 FR/AC 一一对应（3 条 FR ↔ 3 条 AC）
4. 如需更完整的任务字段，可参照 [../starter/.agents/templates/task-template.md](../starter/.agents/templates/task-template.md) 补充

## 五、验收点（可勾选）

- [ ] `spec/tree-viewer/spec.md` 已存在且非空
- [ ] 含 Overview / Goals / Functional Requirements / Acceptance Criteria 四类章节
- [ ] 功能需求 FR-1 ~ FR-3 齐备
- [ ] 验收标准 AC-1 ~ AC-3 齐备，且均为 Given-When-Then 结构
- [ ] 预检两问（位置、格式）均能答出