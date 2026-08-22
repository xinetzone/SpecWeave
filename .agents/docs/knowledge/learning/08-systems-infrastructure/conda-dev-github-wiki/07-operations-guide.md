---
id: conda-dev-github-wiki-07-operations-guide
title: "常见操作指南"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/08-systems-infrastructure/conda-dev-github-wiki/07-operations-guide.toml"
source: "spec:create-conda-dev-github-wiki-tutorial"
category: "learning"
tags: ["conda", "github-actions", "operations", "troubleshooting", "workflow"]
date: "2026-08-20"
status: "stable"
author: "SpecWeave"
summary: "conda .github 元仓库配置修改、功能扩展与问题排查指南"
---

# 常见操作指南

> 本章基于 `conda-dev/.github` 元仓库（`external/libs/conda-dev/.github`）的 7 个工作流、4 个 Issue 模板与 `template-files/config.yml` 实际结构编写。修改 `.github/` 下的文件时，请注意大部分文件由 `conda/infrastructure` 中央仓库同步而来，正确入口见下文"单一来源"说明。

## 一、配置修改

### 1.1 修改工作流触发条件 / 权限 / 参数

每个工作流由三个关键区组成：`on`（触发条件）、`permissions`（权限）、`jobs.*.with`（Action 参数）。以 `labels.yml` 为例，其触发条件与输入参数如下（节选）：

```yaml
# .github/workflows/labels.yml
name: Sync Labels

on:
  workflow_dispatch:
    inputs:
      delete-unmapped:
        description: Delete labels not mapped in either global or local label configurations.
        default: false
        type: boolean
      dry-run:
        description: Run label synchronization workflow without making any changes.
        default: false
        type: boolean

permissions:
  contents: read

jobs:
  sync:
    name: Sync labels
    if: '!github.event.repository.fork'
    runs-on: ubuntu-slim
    permissions:
      contents: read
      issues: write  # Required to create, update, and delete repository issue labels.
    steps:
      - uses: EndBug/label-sync@52074158190acb45f3077f9099fea818aa43f97a # v2.3.3
        with:
          config-file: |
            ${{ env.GLOBAL }}
            ${{ env.LOCAL }}
          delete-other-labels: ${{ inputs.delete-unmapped }}
          dry-run: ${{ inputs.dry-run }}
```

**修改步骤**：

1. **改触发条件**（`on`）：增加 `schedule` 定时触发、修改 `workflow_dispatch.inputs` 的默认值/类型，或调整事件类型列表。
2. **改权限**（`permissions`）：全局权限在 `permissions:` 顶层声明，job 级权限在 `jobs.<id>.permissions` 覆盖。conda 约定：顶层一律 `contents: read`，仅在需要的 job 内按需放开（如 labels 需要 `issues: write`）。
3. **改参数**（`with`）：修改 Action 输入，如 `delete-other-labels`、`dry-run` 等。
4. **验证**：修改后通过 `gh workflow run` 手动触发一次（见 3.4），或在仓库 Actions 页选择对应 workflow 手动 Run。

> 注意：`if: '!github.event.repository.fork'` 是 conda 所有工作流的标准守卫，禁止删除——它避免 fork 仓库自动触发写操作。

### 1.2 修改标签

- **本地标签**：编辑 `.github/labels.yml`（本仓库持有，可自由增删）。
- **全局标签**：编辑 `conda/infrastructure` 仓库的 `.github/global.yml`，再由同步机制下发到各仓库。`labels.yml` 通过 `env.GLOBAL` 直接引用中央仓库的 `global.yml`：

```yaml
env:
  GLOBAL: https://raw.githubusercontent.com/conda/infra/main/.github/global.yml
  LOCAL: .github/labels.yml
```

修改后运行 `Sync Labels` 工作流（勾选 `delete-unmapped` 可清理未被映射的旧标签，建议先只勾 `dry-run` 预览）。

### 1.3 修改 Issue 模板

Issue 模板位于 `.github/ISSUE_TEMPLATE/*.yml`，以 `0_bug.yml` 为例，其结构为：`name`、`description`、`labels`（提交后自动打标签）、`body`（表单元素数组）：

```yaml
# .github/ISSUE_TEMPLATE/0_bug.yml
name: Bug Report
description: Create a bug report.
labels:
  - type::bug
body:
  - type: checkboxes
    id: checks
    attributes:
      label: Checklist
      options:
        - label: I added a descriptive title
          required: true
  - type: textarea
    id: what
    attributes:
      label: What happened?
    validations:
      required: true
```

**修改步骤**：增删 `body` 中的表单元素（`markdown`/`checkboxes`/`textarea` 等）、调整 `labels` 默认标签、修改 `validations.required`。模板文件头部注释 `# edit this in https://github.com/conda/infrastructure` 表明其上游来源——若需全组织生效应在 `conda/infrastructure` 修改。

## 二、功能扩展

> 本节示例为**扩展示例**，为演示目的基于本地实际结构合理设计，并非 conda 仓库现有文件。

### 2.1 新增一个工作流（自定义 triage.yml）

以"新 Issue 自动打 `needs::triage` 标签"为例，参照 `issues.yml` 的事件与 `actions-ecosystem` 用法：

```yaml
# .github/workflows/triage.yml（扩展示例）
name: Triage

on:
  issues:
    types: [opened]

concurrency:
  group: ${{ github.workflow }}-${{ github.event.issue.number || github.run_id }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  triage:
    name: Add triage label
    if: '!github.event.repository.fork'
    runs-on: ubuntu-slim
    permissions:
      contents: read
      issues: write  # Required to add issue triage labels.
    steps:
      - uses: actions-ecosystem/action-add-labels@18f1af5e3544586314bbe15c0273249c770b2daf # v1.1.3
        with:
          labels: needs::triage
          github_token: ${{ secrets.PROJECT_TOKEN }}
```

**流程**：新建文件 → 复用仓库内已锁定的 Action 版本（见 3.2）→ 声明最小权限 → 合并后到 Actions 页验证。注意与 `labels.yml` 配合：若 `needs::triage` 不在任何标签配置中，先按 2.2 新增标签再触发。

### 2.2 新增标签类别

在全局 `global.yml` 或本地 `labels.yml` 中新增标签条目，conda 使用 `category::topic` 作用域语法：

```yaml
# .github/labels.yml（扩展示例）
- name: priority::p1
  description: High priority, should be addressed in the current sprint.
  color: d93f0b
- name: priority::p2
  description: Medium priority work.
  color: fbca04
```

**流程**：按 `[category::topic]` 语法设计名称 → 增补到 `global.yml`（全局）或 `labels.yml`（本地）→ 运行 `Sync Labels` 工作流 → 勾选 `delete-unmapped` 时注意会被视为删除源，勿误删其他标签（先用 `dry-run` 校验）。

### 2.3 扩展 Issue 模板字段

在 `0_bug.yml` 的 `body` 中新增表单元素。conda 模板未使用 `dropdown`/`input` 类型，但 GitHub Issue Form 支持，可按需扩展（扩展示例）：

```yaml
# 追加到 body 列表末尾（扩展示例）
  - type: dropdown
    id: os
    attributes:
      label: Operating System
      options:
        - Linux
        - macOS
        - Windows
    validations:
      required: true
```

**验证方式**：提交后打开仓库的 `Issues → New issue`，预览表单是否渲染新字段、必填校验是否生效、提交后默认标签是否正确打上。

## 三、问题排查

### 3.1 工作流不触发的常见原因

| 原因 | 表现 | 对策 |
|------|------|------|
| **触发条件不匹配** | 事件类型、分支、`types` 未命中 | 核对 `on` 配置；如 `project.yml` 只监听 `pull_request_target` 的 `opened` |
| **fork 限制** | fork 仓库不跑任务 | conda 工作流均含 `if: '!github.event.repository.fork'`，fork 的 PR 默认不执行写操作 |
| **权限不足** | 步骤因 403/Resource not accessible 失败 | 检查 job 级 `permissions` 是否声明了对应 `issues: write`/`pull-requests: write` 等 |
| **schedule 未触发** | 定时工作流静默跳过 | 默认只作用于默认分支；schedule 运行可能延迟，勿立即判定失败 |
| **`pull_request_target` 与 `pull_request` 混淆** | PR 内改动触发了错误的工作流 | `pull_request` 以 PR 合并后代码运行、无 secrets；`pull_request_target` 以默认分支代码运行、可用 secrets（详见 08 安全章节） |

### 3.2 Action 版本更新与 SHA 锁定

conda 所有 Action 均用 **SHA + 版本注释** 锁定，如 `EndBug/label-sync@5207415... # v2.3.3`。更新方式：

- **Dependabot**：在 `.github/dependabot.yml` 配置 `github-actions` 生态，可自动提交升级 PR（保持 SHA+注释 格式）。
- **手动更新**：到目标 Action 仓库找到新版本 tag 对应的 commit SHA，替换 `@<sha>` 并更新 `# vX.Y.Z` 注释；**禁止**直接写 `@v2` 这类可变 tag（见 08 反模式）。

```bash
# 示例：手动更新 label-sync 到 v2.4.0（扩展示例）
# 1) 查询新版本 SHA
gh api repos/EndBug/label-sync/git/ref/tags/v2.4.0 --jq '.object.sha'
# 2) 编辑 labels.yml，将 @5207415... 与 # v2.3.3 替换为查询结果与新版本号
```

### 3.3 dry-run / debug-only 调试模式

- **labels.yml 的 `dry-run`**：`Sync Labels` 工作流的 `dry-run` 输入，勾选后只输出差异、不实际修改标签，是标签变更的安全预览方式。
- **stale.yml 的 `debug-only`**：`actions/stale` 的 `debug-only` 参数取自 `workflow_dispatch` 输入 `dryrun`（默认 `true`），用于只报告"将被标记为 stale 的 issue/PR"而不真正打标：

```yaml
# .github/workflows/stale.yml（节选）
on:
  workflow_dispatch:
    inputs:
      dryrun:
        description: 'dryrun: Preview stale issues/prs without marking them (true|false)'
        required: true
        type: boolean
        default: true
  schedule:
    - cron: 0 4 * * *
# ...
      debug-only: ${{ github.event.inputs.dryrun || false }}
```

> `schedule` 触发时 `github.event.inputs` 为空，`debug-only` 退化为 `false`，即定时运行会真实执行；手动触发时默认 `true` 预览。

### 3.4 使用 gh CLI 手动触发 workflow_dispatch

对声明了 `workflow_dispatch` 的工作流（labels/stale/lock/update 等）可手动触发：

```bash
# 列出工作流
gh workflow list --repo conda/.github

# 手动触发（带输入参数）
gh workflow run "Sync Labels" --repo conda/.github \
  -f dry-run=true -f delete-unmapped=false

# 带 boolean 输入时注意用 -F（raw）还是 -f（string）：
gh workflow run "Stale" --repo conda/.github -F dryrun=true

# 查看运行状态
gh run list --repo conda/.github
```

`workflow_dispatch` 输入在 `github.event.inputs` 中均为字符串；`debug-only: ${{ github.event.inputs.dryrun || false }}` 这种写法即依赖该特性。

---

**上一章**：[06-issue-sorting-labeling.md](06-issue-sorting-labeling.md) | **返回目录**：[00-overview.md](00-overview.md) | **下一章**：[08-best-practices.md](08-best-practices.md)
