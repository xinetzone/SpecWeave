---
id: conda-dev-github-wiki-08-best-practices
title: "最佳实践与注意事项"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/08-systems-infrastructure/conda-dev-github-wiki/08-best-practices.toml"
source: "spec:create-conda-dev-github-wiki-tutorial"
category: "learning"
tags: ["conda", "github-actions", "best-practices", "security", "governance", "pull-request-target"]
date: "2026-08-20"
status: "stable"
author: "SpecWeave"
summary: "conda .github 元仓库可迁移治理模式、安全最佳实践与反模式清单"
---
# 最佳实践与注意事项

> 本章从 `conda-dev/.github` 元仓库的实际设计中提炼可迁移的治理模式，聚焦安全性与可维护性。每个模式均可在其他组织/仓库复制。

## 一、可迁移治理模式

### 1.1 单一来源原则（Single Source of Truth）

conda 将治理资产集中在 **`conda/infrastructure`** 中央仓库，其他仓库的 `.github/` 只是其"下游副本"。同步链路有三条：

1. **文件同步**：`template-files/config.yml` 声明 `src → dst` 映射，由 `update.yml` 工作流拉取中央仓库文件到本仓库（如 `templates/issues/bug.yml → .github/ISSUE_TEMPLATE/0_bug.yml`）。
2. **运行时引用**：`labels.yml` 通过 `env.GLOBAL` 直接引用 `https://raw.githubusercontent.com/conda/infra/main/.github/global.yml`；`stale.yml` 通过 `conda/actions/read-yaml` 读取中央仓库 `messages.yml`。
3. **模板同步**：Issue/PR 模板头部均标注 `# edit this in https://github.com/conda/infrastructure`。

**要点**：修改全组织共用的治理资产时应改中央仓库，而非各个下游仓库；本地仓库只维护真正属于自身的 `labels.yml` 等。

### 1.2 模板与标签分离

- **全局 vs 本地**：全局标签放 `infrastructure/.github/global.yml`，仓库专属标签放 `.github/labels.yml`；`label-sync` 将两者合并同步。
- **模板即标签源**：Issue Form 的 `labels` 字段在创建时自动打标签，保持模板 `labels` 与标签配置一致，避免"模板打了不存在的标签"。

### 1.3 Action 版本锁定（SHA + 版本注释）

所有 Action 使用 `owner/action@<完整SHA> # vX.Y.Z` 格式锁定，例如：

```yaml
- uses: EndBug/label-sync@52074158190acb45f3077f9099fea818aa43f97a # v2.3.3
- uses: actions/stale@eb5cf3af3ac0a1aa4c9c45633dd1ae542a27a899 # v10.3.0
- uses: peter-evans/create-pull-request@5f6978faf089d4d20b00c7766989d076bb2fc7f1 # v8.1.1
```

SHA 保证不可变、可审计；注释保留人类可读版本号便于升级。升级走 Dependabot 或手动替换 SHA+注释（见 07 章 3.2）。

### 1.4 最小权限声明（Least Privilege）

conda 的权限模型：**顶层一律 `permissions: contents: read`，job 级按需放开**。

- 需要打/删标签 → job 加 `issues: write`
- 需要评论 PR/改 commit status → job 加 `pull-requests: write` + `statuses: write`（见 `cla.yml`）
- 需要提交并开 PR → job 加 `contents: write` + `pull-requests: write`（见 `update.yml`）

### 1.5 concurrency 并发控制

所有工作流均声明 `concurrency.group`，防止同源事件并发互相覆盖：

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.event.issue.number || github.run_id }}
  cancel-in-progress: true
```

## 二、安全最佳实践

### 2.1 pull_request_target 的风险与缓解

**风险**：`pull_request_target` 触发的代码运行在**默认分支（main）**，而不是 PR 分支——这意味着它持有仓库级 secrets 权限，而 PR 内容（Issue 文本、PR 标题/分支名）来自**不可信的贡献者**。攻击者可构造恶意 PR 内容，诱导 workflow 表达式执行危险操作（如注入脚本）。

**conda 的缓解措施**：

1. **严格限定用途**：`pull_request_target` 仅用于需要 secrets 的元操作——`cla.yml`（检查 CLA 签名、打 `cla-signed` 标签、写 commit status）、`project.yml`（PR 入 Board）。不用于 checkout PR 代码或运行测试。
2. **fork 守卫**：`if: '!github.event.repository.fork'` 拒绝 fork 仓库触发写路径。
3. **内容不可信原则**：永远不要把 `github.event.pull_request.title/body` 之类用户可控内容拼进 `run:` 脚本或 `with:` 的自由文本参数，需拼接时先做安全校验。

> 对比：`pull_request` 以 PR 合并后的代码运行、默认无 secrets，适合 CI 构建/测试，但不适合"评论、打标签、改状态"等需要写权限的操作。

### 2.2 密钥管理最小授权

conda 通过 4 类 PAT 拆分职责，每个 token 只授予其任务所需的最小 scope：

| Secret | 用途 | 最小授权 |
|--------|------|----------|
| `CLA_ACTION_TOKEN` | 评论、打标签、写 commit status | `pull_request: write` + `statuses: write` |
| `CLA_FORK_TOKEN` | 在 `cla_repo` 开 signee PR | `pull_request: write`（+ `workflow`） |
| `PROJECT_TOKEN` | 标签操作、PR 入 Board | `issues/pull-requests` 写 + 目标 Project 访问 |
| `SYNC_TOKEN` | fork + 开 update PR | `repo` 中 fork/PR 所需最小集 |
| `STALE_OPERATIONS_PER_RUN` | 单次 stale 操作上限 | 数字类型，可留空用默认 `100` |

**要点**：token 之间互相独立，即使一个泄露，攻击者也无法同时做"评论+入板+开 PR"；不要在仓库里硬编码明文密钥。

## 三、反模式（Anti-Patterns）

1. **对 fork 的 PR 用普通 `pull_request` 触发需 secrets 的步骤**。`pull_request` 在 PR 分支上运行且不提供 secrets，需要 secrets 的评论/打标步骤会静默失败或触发安全风险。应改用 `pull_request_target`（并遵守 2.1 的用途限制）或显式校验 `!github.event.repository.fork`。
2. **`permissions` 全开**。省略 `permissions` 或用 `permissions: write-all`，使工作流获得超出需要的仓库写权限，扩大攻击面。应遵循 1.4 最小权限声明。
3. **Action 用可变 tag（`@v2`）而非锁定 SHA**。可变 tag 会被上游恶意/错误更新，导致"昨天还能跑、今天行为大变"且不可审计。必须 `@<SHA> # vX.Y.Z` 锁定。
4. **不加 `concurrency` 导致并发冲突**。多个同源事件同时运行时，标签同步/标签打标互相覆盖，产生不可复现的状态。应声明 1.5 的 concurrency 组。
5. **无 dry-run 直接改标签**。跳过 `label-sync` 的 `dry-run`、`actions/stale` 的 `debug-only` 预览，直接全量执行，可能误删/误关大量 issue。标签类变更务必先预览。

## 四、检验标准清单（Checklist）

- [ ] 所有 Action 均以 SHA 锁定并带版本注释，无 `@vX` 可变 tag
- [ ] 工作流顶层 `permissions: contents: read`，job 级仅放开任务所需权限
- [ ] 需要 secrets 的步骤使用 `pull_request_target` 且严格限定用途，无用户可控内容注入脚本
- [ ] fork 守卫 `if: '!github.event.repository.fork'` 存在于所有写路径 job
- [ ] 每个工作流声明了 `concurrency` group 与 `cancel-in-progress`
- [ ] 标签变更可先 `dry-run`/`debug-only` 预览再执行
- [ ] 密钥全部走 `secrets.*` 引用，仓库内无明文令牌
- [ ] 全局治理资产修改已回到 `conda/infrastructure` 中央仓库而非只改下游
- [ ] 模板 `labels` 与标签配置（global/labels.yml）保持一致
- [ ] 变更后已通过 `gh workflow run` 或 Actions 页手动触发验证

---

**上一章**：[07-operations-guide.md](07-operations-guide.md) | **返回目录**：[00-overview.md](00-overview.md) | **下一章**：[09-resources.md](09-resources.md)
