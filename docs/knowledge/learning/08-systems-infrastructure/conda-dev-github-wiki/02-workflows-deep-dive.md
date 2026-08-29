---
id: conda-dev-github-wiki-02-workflows
title: "GitHub Actions 工作流详解"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/08-systems-infrastructure/conda-dev-github-wiki/02-workflows-deep-dive.toml"
source: "spec:create-conda-dev-github-wiki-tutorial"
category: "learning"
tags: ["conda", "github-actions", "workflow", "cla", "stale-bot", "ci"]
date: "2026-08-20"
status: "stable"
author: "SpecWeave"
summary: "conda .github 元仓库 7 个 GitHub Actions 工作流详解"
---
# GitHub Actions 工作流详解

conda/.github 元仓库通过 7 个工作流自动化大部分仓库治理工作。它们全部集中在 `.github/workflows/`，本文逐一拆解触发事件、权限声明、任务步骤与关键配置语义，最后提炼跨工作流共性模式。

## 1. 工作流总览

| 文件 | name | 触发方式 | 核心职责 |
|------|------|---------|---------|
| cla.yml | CLA | `issue_comment(created)` + `pull_request_target` | 校验贡献者 CLA 签署 |
| issues.yml | Automate Issues | `issue_comment(created)` | Issue 标签分流（feedback → support） |
| labels.yml | Sync Labels | `workflow_dispatch`（手动） | 同步全局/本地标签配置 |
| lock.yml | Lock | `workflow_dispatch` + `schedule` | 锁定不活跃的已关闭线程 |
| project.yml | Add to Project | `pull_request_target(opened)` | 新 PR 自动加入 Review 项目板 |
| stale.yml | Stale | `workflow_dispatch` + `schedule` | 标记/关闭陈旧 issue 与 PR |
| update.yml | Update Repository | `schedule` + `workflow_dispatch` | 每周同步上游基础设施文件 |

## 2. CLA：贡献者许可协议校验

**触发事件**：`issue_comment(created)`（收到 `@conda-bot check` 评论时）+ `pull_request_target`（PR 创建/更新时）。

```yaml
on:
  issue_comment:
    types: [created]
  pull_request_target:
jobs:
  check:
    if: >-
      !github.event.repository.fork
      && ( github.event.issue.pull_request
           && github.event.comment.body == '@conda-bot check'
           || github.event_name == 'pull_request_target' )
    runs-on: ubuntu-slim
    permissions:
      contents: read
      pull-requests: write   # 更新 PR 标签与评论
      statuses: write        # 发布 CLA 提交状态
```

**任务步骤**：调用 `conda/actions/check-cla@7f6830b1428a9bd47f0b068892c77eae95207037 # v26.1.0`，配置两个 token 与标签：

- `token`（CLA_ACTION_TOKEN）：需要 `pull-requests: write` + `statuses: write` 权限（fine-grained PAT）或 `repo`（classic PAT），用于评论、打标签、写提交状态
- `cla_token`（CLA_FORK_TOKEN）：用于在 `cla_repo` 中为签署者开启 PR（fine-grained 需 `pull-requests: write`，classic 需 `repo` + `workflow`）
- `label: cla-signed`：签署成功后给 PR 打上的标签

**使用场景**：所有对外部贡献者开放 PR 的 conda 组织仓库。**注意**：job 级 `if` 用 `github.event.repository.fork` 排除 fork 仓库（fork 内不校验），注释触发分支要求评论内容精确等于 `@conda-bot check`，且 `issue.pull_request` 为真（必须是 PR 而非 issue）。

## 3. Automate Issues：Issue 标签分流

**触发事件**：`issue_comment(created)`——任何人在带 `pending::feedback` 标签的 issue 上评论。

```yaml
env:
  FEEDBACK_LBL: pending::feedback
  SUPPORT_LBL: pending::support
jobs:
  pending_support:
    if: >-
      !github.event.repository.fork
      && !github.event.issue.pull_request
      && contains(github.event.issue.labels.*.name, 'pending::feedback')
    permissions:
      contents: read
      issues: write          # 移除/添加 triage 标签
```

**任务步骤**（两步）：

1. `actions-ecosystem/action-remove-labels@2ce5d41b4b6aa8503e285553f75ed56e0a40bae0 # v1.3.0`：移除 `pending::feedback`
2. `actions-ecosystem/action-add-labels@18f1af5e3544586314bbe15c0273249c770b2daf # v1.1.3`（`if: github.event.issue.state == 'open'`）：添加 `pending::support`

两步骤共用 `github_token: ${{ secrets.PROJECT_TOKEN }}`。

**关键配置语义**：源码注释明确——**任何人的评论都会触发标签更新**（不限 issue 作者/报告者）；存在 TODO：未来建立 `conda-issue-sorting` 团队，按"评论者是否为 issue-sorting 工程师"决定是否切换标签。**使用场景**：issue 分流——维护者标记"待反馈"后，用户一回应即自动转入"待支持"队列。

## 4. Sync Labels：标签配置同步

**触发事件**：仅 `workflow_dispatch`，提供两个布尔 inputs（均默认 `false`）：

- `delete-unmapped`：删除 global/local 配置中未映射的标签
- `dry-run`：只预览不实际变更

**任务步骤**：

1. `actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0 # v7.0.0`（`persist-credentials: false`）
2. `andstor/file-existence-action@558493d6c74bf472d87c84eab196434afc2fa029 # v3.1.0` 检测本地文件 `.github/labels.yml` 是否存在
3. 分支同步：存在本地文件 → `EndBug/label-sync@52074158190acb45f3077f9099fea818aa43f97a # v2.3.3` 用 **GLOBAL + LOCAL 合并**配置同步；不存在 → 只用 **GLOBAL** 配置同步

```yaml
env:
  GLOBAL: https://raw.githubusercontent.com/conda/infra/main/.github/global.yml
  LOCAL: .github/labels.yml
```

**关键配置语义**：`GLOBAL` 指向 `conda/infra` 仓库的统一标签定义（全组织唯一事实源），`LOCAL` 允许单仓库在 `.github/labels.yml` 追加仓库专属标签。`delete-other-labels` 与 `dry-run` 均透传自 workflow_dispatch inputs。**使用场景**：组织级标签变更后手动触发，保证各仓库标签与 infra 全局配置一致。权限 `issues: write`（创建/更新/删除标签）。

## 5. Lock：锁定不活跃线程

**触发事件**：`workflow_dispatch` + `schedule`（`cron: 0 6 * * *`，每天 06:00 UTC）。

**任务步骤**：单步调用 `dessant/lock-threads@89ae32b08ed1a541efecbab17912962a5e38981c # v6.0.2`。关键参数语义：

| 参数 | 值 | 语义 |
|------|----|------|
| `issue-inactive-days` | 180 | 已关闭 issue 不活跃 180 天即锁定 |
| `pr-inactive-days` | 365 | 已关闭 PR 不活跃 365 天即锁定 |
| `add-issue-labels` / `add-pr-labels` | locked | 锁定前先打上 `locked` 标签 |
| `issue-lock-reason` / `pr-lock-reason` | resolved | 锁定原因（可选：resolved/off-topic/too heated/spam） |
| `process-only` | issues, prs | 仅处理 issue 与 PR（不处理 discussions） |

**使用场景**：防止陈年已关闭 issue/PR 被反复"挖坟"评论，锁定后仅维护者可回复。权限 `issues: write` + `pull-requests: write`。

## 6. Add to Project：新 PR 自动入板

**触发事件**：`pull_request_target(opened)`——新 PR 创建即触发。

**任务步骤**：`actions/add-to-project@5afcf98fcd03f1c2f92c3c83f58ae24323cc57fd # v2.0.0`，`project-url: https://github.com/orgs/conda/projects/16`（Review 板），`github-token: ${{ secrets.PROJECT_TOKEN }}`。

**关键配置语义**：所有新 PR 自动加入组织级 Review 项目板，无需人工拖拽。**使用场景**：配合 conda 组织的 Review 看板做 PR 队列管理。注意 `pull_request_target` 在 base 分支上下文运行（可访问 secrets），因此必须配合 `if: '!github.event.repository.fork'` 防 fork 滥用。

## 7. Stale：陈旧线程清理

**触发事件**：`workflow_dispatch`（`dryrun` 布尔 input，必填，默认 `true`，用于预览）+ `schedule`（`cron: 0 4 * * *`，每天 04:00 UTC）。

**核心机制——matrix 双策略**：

```yaml
strategy:
  matrix:
    include:
      - only-issue-labels: ''
        days-before-issue-stale: 365
        days-before-issue-close: 30
      - only-issue-labels: type::support   # support 类更激进
        days-before-issue-stale: 90
        days-before-issue-close: 21
```

**任务步骤**：

1. `conda/actions/read-yaml@7f6830b1428a9bd47f0b068892c77eae95207037 # v26.1.0`：从 `https://raw.githubusercontent.com/conda/infra/main/.github/messages.yml` 读取 stale 消息模板，通过 `fromJSON(steps.read_yaml.outputs.value)['stale-issue']` / `['stale-pr']` 注入
2. `actions/stale@eb5cf3af3ac0a1aa4c9c45633dd1ae542a27a899 # v10.3.0` 执行标记/关闭

**关键配置项语义**：

- **PR 统一策略**：`days-before-pr-stale: 365`，`days-before-pr-close: 30`
- **标签体系**：stale 标记 `stale`、关闭 `stale::closed`、恢复 `stale::recovered`；`remove-stale-when-updated: true`（有更新即移除），unstale 时加 `stale::recovered` 并移除 `stale,stale::closed`
- **豁免规则**：`exempt-issue/pr-labels: stale::recovered,epic`、`exempt-all-milestones: true`、`exempt-assignees: mingwandroid`
- **资源/安全**：`operations-per-run: ${{ secrets.STALE_OPERATIONS_PER_RUN || 100 }}`（可配上限，默认 100）、`debug-only: ${{ github.event.inputs.dryrun || false }}`（dry-run 透传）、`ascending: true`、`delete-branch: false`
- 关闭原因 `close-issue-reason: not_planned`

**使用场景**：自动标记 1 年不活跃的 issue/PR，警告后 30 天关闭；`type::support` 的 issue 走更短的 90/21 天通道；epic、带里程碑、被 mingwandroid 指派的线程豁免。

## 8. Update Repository：基础设施文件自动同步

**触发事件**：`schedule`（`cron: 36 2 * * 0`，每周日 00:36 UTC）+ `workflow_dispatch`。

**权限声明**：job 级 `contents: write`（提交同步的模板与工作流更新）、`pull-requests: write`（开启更新 PR）、`issues: write`（PR 元数据）。

**任务步骤**（依次）：

1. `actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0 # v7.0.0`（`persist-credentials: false`）
2. **配置 git 用户**：`user.name 'Conda Bot'`、`user.email '18747875+conda-bot@users.noreply.github.com'`
3. `conda/actions/combine-durations@7f6830b1428a9bd47f0b068892c77eae95207037 # v26.1.0` 与 `conda/actions/template-files@7f6830b1428a9bd47f0b068892c77eae95207037 # v26.1.0`（均 `continue-on-error: true`，产出 summary）
4. **Commit changes**（`continue-on-error: true`，无更新则 no-op）：`git add .` + `git commit "🤖 updated file(s)"`
5. **Create fork**：`gh repo fork --clone=false --default-branch-only`（已 fork 则 no-op），解析出 fork 名写入 `FORK` 环境变量（`GH_TOKEN: SYNC_TOKEN`）
6. `peter-evans/create-pull-request@5f6978faf089d4d20b00c7766989d076bb2fc7f1 # v8.1.1`：`push-to-fork: ${{ env.FORK }}`、`branch: update`、`delete-branch: true`、标题 `🤖 Update infrastructure file(s)`，body 附上 durations/templates 摘要与 workflow 自引用链接

**使用场景**：每周自动把 `conda/infra`（template-files）和 duration 数据的最新变更同步进本仓库并开 PR，实现"仓库基础配置持续跟上组织标准"。这是唯一**未加 `!fork` 条件**的工作流（同步逻辑依赖 fork 机制本身）。

## 9. 跨工作流共性配置模式

1. **concurrency 并发控制**：每个工作流均声明 `concurrency` 组 + `cancel-in-progress: true`。组名按作用域区分——事件相关型用 `${{ github.workflow }}-${{ github.event.pull_request.number || github.event.issue.number || github.run_id }}`（按 PR/issue 隔离），仓库级批量任务用 `${{ github.workflow }}-${{ github.repository }}`（仓库内串行，防止 stale/lock 并发冲突）
2. **最小权限原则**：顶层统一 `permissions: contents: read`（只读兜底），job 级按需增量授权（如 `pull-requests: write`、`issues: write`、`statuses: write`），并保留说明注释。杜绝顶层 `write-all`
3. **pull_request_target 安全注意**：cla.yml 与 project.yml 使用 `pull_request_target`（在 base 上下文运行、可访问 secrets），必须**显式 `if: '!github.event.repository.fork'`** 防止 fork 提交注入恶意代码后读取 secrets；同时这两个工作流**不 checkout PR 代码**，进一步缩小攻击面
4. **Action 版本锁定（SHA + 注释）**：所有第三方 Action 均以**完整 commit SHA** 引用（如 `7f6830b1428a9bd47f0b068892c77eae95207037 # v26.1.0`），SHA 后追加 `# vX.Y.Z` 注释便于人读。这保证供应链不可变（防 Action 维护者篡改标签指向），同时保留可读版本号
5. **ubuntu-slim runner**：全部 job 统一 `runs-on: ubuntu-slim`，避免标准 `ubuntu-latest` 的镜像体积与启动开销
6. **fork 守卫**：除 update.yml 外，所有工作流均含 `if: '!github.event.repository.fork'`，防止 fork 仓库滥用工作流与 secrets
7. **secrets 集中化**：CLI token 统一走组织级 secrets（`CLA_ACTION_TOKEN`、`CLA_FORK_TOKEN`、`PROJECT_TOKEN`、`SYNC_TOKEN`、`STALE_OPERATIONS_PER_RUN`），仓库内不硬编码任何凭据

---
**上一章**：[01-repository-structure.md](01-repository-structure.md) | **返回目录**：[00-overview.md](00-overview.md) | **下一章**：[03-issue-templates.md](03-issue-templates.md)
