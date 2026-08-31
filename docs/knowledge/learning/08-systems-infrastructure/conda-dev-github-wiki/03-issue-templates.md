---
type: Wiki Tutorial

id: conda-dev-github-wiki-03-issue-templates
title: "Issue 模板详解"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/08-systems-infrastructure/conda-dev-github-wiki/03-issue-templates.toml"
source: "spec:create-conda-dev-github-wiki-tutorial"
category: "learning"
tags: ["conda", "issue-template", "github-forms", "triage", "epic", "labels"]
date: "2026-08-20"
status: "stable"
author: "SpecWeave"
summary: "conda .github 元仓库 4 个 Issue 模板（bug/feature/documentation/epic）详解"
---
# Issue 模板详解

conda/.github 元仓库通过 `.github/ISSUE_TEMPLATE/` 下的 4 个 GitHub Forms（YAML）模板规范 issue 提交流程，并在创建时自动打上类型标签，与 Issue Sorting 标签体系联动。本文逐一拆解各模板的字段语义、block 类型与 validations 用法。

## 1. 模板体系总览

| 文件 | name | 描述 | 自动标签 |
|------|------|------|---------|
| 0_bug.yml | Bug Report | 创建 bug 报告 | `type::bug` |
| 1_feature.yml | Feature Request | 创建功能请求 | `type::feature` |
| 2_documentation.yml | Documentation | 文档相关问题 | `type::documentation` |
| epic.yml | Epic | 相关 ticket 的集合 | `epic` |

所有模板均为 GitHub Forms（`*.yml`）而非 Markdown 模板，声明式结构可被 GitHub 渲染为带校验的表单。

## 2. 通用表单结构：三段式 body

每个模板的 `body` 都由三类 block 按固定顺序组成：

1. **markdown 引导块**：表单顶部的说明文案
2. **checkboxes 清单块**（`id: checks`）：强制勾选确认
3. **textarea 文本块**：问题描述主体（若干 `id` 各异的字段）

### 2.1 markdown 引导块语义

`type: markdown` 的 `attributes.value` 为展示文本，不产生可提交字段。所有模板共用如下文案逻辑：

- **NOTICE 提示**（`> [!NOTE]`）：不完整或缺失信息的提交**可能被关闭为 inactionable**——这是与 stale 流程协同的"低质量提交拦截"声明
- **查重引导**：请先搜索现有 open issue，找到相关则 upvote 并补充细节
- **致谢**：感谢社区贡献，增强提交通道友好度（`0_bug`/`1_feature`/`epic` 为 `conda/.github` 仓库致谢，`2_documentation` 为 `conda` 项目致谢）

### 2.2 checkboxes 清单语义

`type: checkboxes` 的 `attributes.options` 是数组，每项含 `label` 与 `required`：

| 选项文本 | required |
|---------|----------|
| I added a descriptive title | true |
| I searched open reports [requests/issues] and couldn't find a duplicate | true |

两项均 `required: true`，**未勾选则无法提交表单**，从入口强制保证 issue 标题描述性与查重率。注意不同模板查重关键词不同：bug/documentation 用 "reports"，feature 用 "requests"，epic 用 "issues"。

### 2.3 textarea 块与 validations

`type: textarea` 支持 `id`（字段标识）、`attributes.label`（显示名）、`attributes.description`（帮助文案）、`attributes.value`（默认值）、`attributes.placeholder`（占位符）与 `validations.required`（是否必填）。**`validations.required: true` 的字段为空将阻止提交**；未声明该键则字段为选填。这一机制是模板与 stale 拦截之间"质量守门"的输入端。

## 3. Bug Report（0_bug.yml）

```yaml
name: Bug Report
description: Create a bug report.
labels:
  - type::bug
body:
  - type: markdown      # NOTICE + 查重引导 + 致谢
  - type: checkboxes
    id: checks          # 描述性标题 + 查重，均 required
  - type: textarea
    id: what            # What happened? —— required
  - type: textarea
    id: context         # Additional Context —— 选填
```

**字段语义**：`what`（What happened?）为唯一必填描述字段，说明"实际发生了什么、应发生什么、复现所需细节"；`context`（Additional Context）选填，可附截图等补充信息。**使用场景**：用户报告缺陷的标准入口，自动打 `type::bug` 标签进入 bug 分流队列。

## 4. Feature Request（1_feature.yml）

```yaml
labels: [type::feature]
body:
  - type: textarea
    id: idea     # What is the idea? —— required
  - type: textarea
    id: why      # Why is this needed? —— 选填
  - type: textarea
    id: what     # What should happen? —— 选填
  - type: textarea
    id: context  # Additional Context —— 选填
```

**字段语义**：相比 bug 模板，feature 用 4 个字段逐步展开：`idea`（想法是什么，必填）→ `why`（为什么需要，受益者/价值/解决的问题）→ `what`（期望的用户体验）→ `context`（补充信息）。仅 `idea` 必填，鼓励但不强制完整填写。**使用场景**：新功能提案的标准入口，自动打 `type::feature` 标签。

## 5. Documentation（2_documentation.yml）

```yaml
labels: [type::documentation]
body:
  - type: textarea
    id: what     # What happened? —— required（文档/CLI 帮助中的错误）
  - type: textarea
    id: context  # Additional Context —— 选填
```

**字段语义**：与 bug 模板结构一致，但 `what` 的 description 明确指出适用范围——**文档中的 typo、坏链、缺失/不完整/过期信息**（conda docs 或 CLI help）。**使用场景**：纯文档问题入口，与代码 bug 区分，自动打 `type::documentation` 标签，便于文档维护者单独分流。

## 6. Epic（epic.yml）

Epic 是体量最大的模板，7 个 textarea 字段覆盖"问题/功能的大颗粒度打包"：

```yaml
labels: [epic]
body:
  - type: textarea
    id: what          # What? —— required
  - type: textarea
    id: why           # Why? —— required，默认含 checklist
  - type: textarea
    id: user_impact   # User impact —— required
  - type: textarea
    id: goals         # Goals —— required，默认含 checklist
  - type: textarea
    id: tasks         # Tasks —— 非必填，默认含 checklist
  - type: textarea
    id: blocked_by    # This epic is blocked by —— 非必填，默认含 checklist
  - type: textarea
    id: blocks        # This epic blocks —— 非必填，默认含 checklist
```

**字段语义**：`what`/`why`/`user_impact`/`goals` 必填（Why 的 description 提示可在此链接 research/spike issue）；`tasks`（实施任务）、`blocked_by`（本 epic 的依赖项）、`blocks`（被本 epic 阻塞的项）三个关系字段非必填。**关键点**：`why`/`goals`/`tasks`/`blocked_by`/`blocks` 的 `attributes.value` 预填 `- [ ] <...>` 形式的 Markdown checklist，引导用户以可勾选清单组织内容。**使用场景**：维护者/核心团队用 epic 聚合一批相关 ticket，评估问题/功能的范围（scope）与依赖关系；markdown 引导块明确说明"报 bug / 提 feature / 代码变更请用其他表单"，避免 epic 被滥用为通用 issue。

## 7. 模板与 Issue Sorting 标签联动

模板是 Issue Sorting 流水线的**上游输入**：

- 每个模板通过 `labels:` 数组在**创建时自动打上类型标签**（`type::bug` / `type::feature` / `type::documentation` / `epic`），无需人工分类
- 这些标签是 [02-workflows-deep-dive.md](02-workflows-deep-dive.md) 中多个工作流的匹配依据：
  - `issues.yml` 匹配 `pending::feedback` / `pending::support` 分流标签（与类型标签正交，属处理阶段标签）
  - `stale.yml` 的 matrix 第二策略按 `only-issue-labels: type::support` 走激进 90/21 天清理通道
  - `stale.yml` 将 `epic` 标签列入 `exempt-issue/pr-labels`，epic 永不视为 stale
- 完整标签定义统一在 `conda/infra` 仓库的 `.github/global.yml`（由 `labels.yml` 同步），保证"模板声明的标签"与"工作流依赖的标签"始终一致，避免标签漂移

## 8. 单一来源原则（Single Source of Truth）

每个模板文件**首行**均为固定注释：

```yaml
# edit this in https://github.com/conda/infrastructure
```

**语义**：这些模板的真正权威版本维护在 `conda/infrastructure` 仓库（与 `conda/infra` 的 global.yml/messages.yml 同一体系）。各仓库 `.github/ISSUE_TEMPLATE/` 下的文件只是同步副本——**不要在此直接编辑**，应在上游仓库修改后经 [02-workflows-deep-dive.md](02-workflows-deep-dive.md) 的 `update.yml` 每周同步流程分发到各仓库。该注释同时是对维护者的强提示：避免本地改动被下次同步覆盖。

**实践要点**：

1. 新增/修改模板 → 在 `conda/infrastructure` 仓库编辑
2. 等待 `update.yml` 每周同步（或手动 `workflow_dispatch`）
3. 若涉及新标签 → 同步更新 `conda/infra` 的 global.yml，确保 labels.yml 可同步
4. 提交前用 `validations.required` 把关必填字段，用 `> [!NOTE]` 声明"不完整将被关闭"，与 stale 的 inactionable 关闭形成闭环

---
**上一章**：[02-workflows-deep-dive.md](02-workflows-deep-dive.md) | **返回目录**：[00-overview.md](00-overview.md) | **下一章**：[04-community-files.md](04-community-files.md)
