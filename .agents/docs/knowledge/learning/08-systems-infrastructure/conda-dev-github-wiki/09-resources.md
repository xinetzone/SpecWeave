---
id: conda-dev-github-wiki-09-resources
title: "术语表与参考资料"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/08-systems-infrastructure/conda-dev-github-wiki/09-resources.toml"
source: "spec:create-conda-dev-github-wiki-tutorial"
category: "learning"
tags: ["conda", "github-actions", "glossary", "references", "resources"]
date: "2026-08-20"
status: "stable"
author: "SpecWeave"
summary: "conda .github 元仓库术语表、权威参考资料与分级阅读建议"
---
# 术语表与参考资料

## 一、术语表

| 术语 | 简短定义 |
|------|----------|
| **meta-repository** | 元仓库（如 `conda/.github`）：不承载业务代码，只承载组织治理资产（工作流、Issue/PR 模板、标签、行为规范），并通过同步机制下发到各业务仓库 |
| **pull_request_target** | 以**默认分支（main）**的代码运行的工作流事件，持有仓库 secrets，用于需要写权限的 PR 元操作（评论/打标签/入板）。PR 内容不可信（详见 08 章 2.1） |
| **pull_request** | 以 **PR 合并后代码**运行的工作流事件，默认无 secrets，适合 CI 构建/测试，不适合写权限操作 |
| **issue_comment** | Issue/PR 评论事件，`issues.yml`/`cla.yml` 用它监听评论（如 `@conda-bot check`）触发自动化 |
| **concurrency** | 并发控制：用 `group` 归并同源事件、`cancel-in-progress: true` 取消旧运行，避免标签/状态互相覆盖 |
| **permissions** | 工作流的 GitHub Token 权限声明；conda 约定顶层 `contents: read`，job 级按需放开 |
| **workflow_dispatch** | 手动触发工作流的事件，可定义 `inputs`（如 `dry-run`），由 `gh workflow run` 或 Actions 页触发 |
| **schedule（cron）** | 定时触发：五段 cron 表达式，如 `0 4 * * *`（每日 04:00 UTC）用于 stale/lock/update 定时任务 |
| **stale** | 将长期无活动（idle）的 issue/PR 标记为过期并最终关闭的机制，由 `actions/stale` 实现 |
| **lock** | 锁定已关闭的 issue/PR 禁止继续评论，由 `dessant/lock-threads` 实现 |
| **CLA** | Contributor License Agreement（贡献者许可协议）；`check-cla` 校验贡献者是否已签署，未签署则阻止合并 |
| **Issue Form** | 以 YAML 定义的结构化 Issue 模板（`.github/ISSUE_TEMPLATE/*.yml`），提供受控字段与默认标签 |
| **checkboxes** | Issue Form 的复选框元素，用于强制用户确认（如"已搜索重复 issue"） |
| **textarea** | Issue Form 的多行文本字段，带 `validations.required` 必填校验 |
| **action version pinning** | Action 版本锁定：用 `@<完整SHA> # vX.Y.Z` 固定不可变版本，杜绝可变 tag 带来的不确定性 |
| **ubuntu-slim** | conda 自定义 runner 标签：精简版 Ubuntu 运行器，用于减小镜像与加快启动 |
| **self-hosted runner** | 自托管运行器：组织自建机器上的 Actions 执行环境（`ubuntu-slim` 即部署于此），区别于 GitHub 托管 runner |
| **secrets** | 仓库/组织级加密密钥，工作流经 `secrets.X` 引用；conda 用 `PROJECT_TOKEN`/`CLA_ACTION_TOKEN` 等最小授权拆分 |
| **GitHub Projects / Board** | 组织级看板：conda 用 Roadmap Board（Refinement/Backlog/Current Sprint）与 Review Board 管理 PR 评审（`project.yml` 自动入板） |
| **dry-run / debug-only** | 预览模式：`label-sync` 的 `dry-run`、`actions/stale` 的 `debug-only`，只报告差异不实际修改 |
| **label-sync** | 标签同步：`EndBug/label-sync` 将 global+local 标签配置同步为仓库实际标签，可 `delete-unmapped` 清理多余标签 |

## 二、权威参考资料

### GitHub Docs（官方）

- Workflow 语法：https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions
- 工作流权限（permissions）：https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/about-permissions-for-github-actions
- 触发工作流的事件：https://docs.github.com/en/actions/reference/events-that-trigger-workflows
- pull_request_target 详解：https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#pull_request_target
- 使用 secrets：https://docs.github.com/en/actions/security-guides/encrypted-secrets
- 安全加固 Actions：https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions

### 关键 Action 仓库

- conda/actions（check-cla、read-yaml、combine-durations、template-files 等）：https://github.com/conda/actions
- dessant/lock-threads：https://github.com/dessant/lock-threads
- actions/stale：https://github.com/actions/stale
- EndBug/label-sync：https://github.com/EndBug/label-sync
- actions/add-to-project：https://github.com/actions/add-to-project
- peter-evans/create-pull-request：https://github.com/peter-evans/create-pull-request
- actions-ecosystem/action-add-labels / action-remove-labels：https://github.com/actions-ecosystem/action-add-labels

### conda 相关仓库

- conda/infrastructure（中央治理仓库）：https://github.com/conda/infrastructure
- conda/governance（组织治理文档）：https://github.com/conda/governance
- conda/.github（元仓库，本章研究对象）：https://github.com/conda/.github

## 三、按难度分级的扩展阅读

### 🟢 入门（第一次接触 GitHub Actions）

1. GitHub 官方入门：https://docs.github.com/en/actions/learn-github-actions/understanding-github-actions
2. 通读 `HOW_WE_USE_GITHUB.md` 了解 conda 的 Issue 流转与自动化全貌
3. 在 `conda/.github` 仓库 Actions 页逐个查看 7 个工作流的运行记录与日志

### 🟡 进阶（能独立维护本元仓库）

4. GitHub Docs 工作流语法与事件触发全文档
5. 研读 `cla.yml` 的 `pull_request_target` 用法与 `issues.yml` 的标签切换逻辑
6. 用 `gh workflow run` 手动触发 labels/stale 并观察 dry-run 输出
7. `conda/infrastructure` 的 `sync.yml` 与 `template-files/config.yml` 同步机制源码阅读

### 🔴 专家（设计组织级治理体系）

8. 官方《Security hardening for GitHub Actions》全文（含 `pull_request_target` 攻击面、pwn request 等案例）
9. 研究 `update.yml` 的 fork + create-pull-request 自动更新链路
10. 结合 `conda/governance` 与 `HOW_WE_USE_GITHUB.md`，设计自己的"单一来源 + 模板/标签分离 + 最小权限"治理模板
11. 对比自托管 runner（`ubuntu-slim`）与 GitHub 托管 runner 的调度与安全模型

---

**上一章**：[08-best-practices.md](08-best-practices.md) | **返回目录**：[00-overview.md](00-overview.md)
