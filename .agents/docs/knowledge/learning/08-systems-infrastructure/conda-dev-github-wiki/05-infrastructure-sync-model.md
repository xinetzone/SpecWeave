---
id: conda-dev-github-wiki-05-infrastructure-sync-model
title: "中央同步模型"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/08-systems-infrastructure/conda-dev-github-wiki/05-infrastructure-sync-model.toml"
source: "spec:create-conda-dev-github-wiki-tutorial"
category: "learning"
tags: ["conda", "infrastructure", "config.yml", "sync", "workflows", "template-files"]
date: "2026-08-20"
status: "stable"
author: "SpecWeave"
summary: "conda .github 元仓库中央同步模型解析"
---
# 中央同步模型

> 本章解析 Conda 社区如何用**一份 `config.yml` + 一个中央仓库（`conda/infrastructure`）**，把社区文件、工作流、Issue/PR 模板统一批量下发到 conda 组织内的所有仓库。核心文件为本元仓库的 `.github/template-files/config.yml` 与 `update.yml`。

## 1. 同步模型定位

Conda 组织有大量仓库（conda、conda-build、rattler 等）。若每个仓库各自维护行为准则、Issue 模板、自动化工作流，必然产生漂移。解决方案是：

- **中央权威**：`conda/infrastructure` 仓库持有所有模板、全局标签、自动化配置。
- **配置清单**：每个仓库通过自身 `.github/template-files/config.yml` 声明"我想要哪些文件、放在哪里"。
- **双向同步**：目标仓库的 `update.yml` 按调度拉取中央内容（Pull）；中央仓库的 `sync.yml` 主动推送（Push）。

`config.yml` 本质上是一张**"文件采购清单"**，逐条声明 `src`（中央仓库模板路径）与 `dst`（本仓库落盘路径）。

## 2. config.yml 完整映射清单

文件分为两大块：`conda/governance`（社区文件）与 `conda/infrastructure`（工作流/模板）。全部条目如下：

### 2.1 conda/governance：必选社区文件

```yaml
conda/governance:
  # [required] community files
  - CODE_OF_CONDUCT.md
```

- 只含 `CODE_OF_CONDUCT.md` 一项，标记为 `[required]`。
- 该项**没有** `src/dst` 映射，属于"原样放置"：中央的 `CODE_OF_CONDUCT.md` 内容直接落到各仓库根目录同名文件。

### 2.2 conda/infrastructure：必选工作流

```yaml
conda/infrastructure:
  # [required] general workflows
  - .github/workflows/cla.yml
  - .github/workflows/update.yml
```

两项 `[required]` 基础工作流：

- **cla.yml**：合并前校验贡献者已签署 CLA；未签署则阻塞合并直至人工复核。
- **update.yml**：本章主角，负责按调度从中央拉取模板并生成更新 PR（见第 5 节）。

### 2.3 可选：Projects 入板工作流（三件套）

```yaml
  # [optional] to include repo in https://github.com/orgs/conda/projects/2
  - .github/workflows/issues.yml
  - .github/workflows/labels.yml
  - .github/workflows/project.yml
```

- 注释明示加入这三项可将仓库纳入 `https://github.com/orgs/conda/projects/2` 看板体系。
- **issues.yml**：Issue 评论自动化（`pending::feedback` → `pending::support` 标签切换）。
- **labels.yml**：同步全局 + 本地标签配置。
- **project.yml**：新 PR 自动加入 Review 板（`orgs/conda/projects/16`）。

### 2.4 可选：stale bot 工作流

```yaml
  # [optional] stale bot workflows
  - .github/workflows/stale.yml
  - .github/workflows/lock.yml
```

- **stale.yml**：标记/关闭长期无活动的 Issue 与 PR。
- **lock.yml**：锁定长期无活动的已关闭 Issue/PR 线程。

### 2.5 可选：HOW_WE_USE_GITHUB.md

```yaml
  # [optional] general processes for the conda org
  - src: templates/HOW_WE_USE_GITHUB.md
    dst: HOW_WE_USE_GITHUB.md
```

- 把中央 `templates/HOW_WE_USE_GITHUB.md` 下发为各仓库根目录的 `HOW_WE_USE_GITHUB.md`（即第 04 章解读的协作流程文档）。

### 2.6 可选：4 个标准 Issue 模板

```yaml
  # [optional] standard issue templates
  - src: templates/issues/bug.yml
    dst: .github/ISSUE_TEMPLATE/0_bug.yml
  - src: templates/issues/feature.yml
    dst: .github/ISSUE_TEMPLATE/1_feature.yml
  - src: templates/issues/documentation.yml
    dst: .github/ISSUE_TEMPLATE/2_documentation.yml
  - src: templates/issues/epic.yml
    dst: .github/ISSUE_TEMPLATE/epic.yml
```

- 四个模板（Bug/Feature/Documentation/Epic）按 `0_/1_/2_` 前缀 + 名称映射到目标仓库的 `.github/ISSUE_TEMPLATE/` 目录。
- 前缀编号决定 GitHub Issue 创建页面中的排序顺序。

### 2.7 可选：PR 模板

```yaml
  # [optional] standard PR template
  # - src: templates/pull_requests/news_tests_docs.md
  #   dst: .github/template-files/templates/pull_request_template_details.md
  - src: templates/pull_requests/base.md
    dst: .github/PULL_REQUEST_TEMPLATE.md
```

- 启用 `templates/pull_requests/base.md` → `.github/PULL_REQUEST_TEMPLATE.md`。
- 另一条 `news_tests_docs.md` 被注释掉（备用，未启用）。

### 2.8 注释掉的 rever 发布文件（含参数化机制）

```yaml
  # [optional] rever release files
  # - src: templates/releases/RELEASE.md
  #   dst: RELEASE.md
  #   with:
  #     placeholder: YY.M
  # - src: templates/releases/rever.xsh
  #   dst: rever.xsh
  # - src: templates/releases/TEMPLATE
  #   dst: news/TEMPLATE
```

- 三条 rever 发布相关文件全部注释掉（默认不启用）：`RELEASE.md`、`rever.xsh`、`news/TEMPLATE`。
- 其中 `RELEASE.md` 演示了 **`with.placeholder: YY.M` 参数化机制**：同步时用仓库的发布版本（形如 `YY.M` 的年月版本号）替换模板中的占位符，实现"同一模板、按仓库版本实例化"。

## 3. src/dst 映射与参数化机制

| 机制 | 说明 |
|------|------|
| **src** | 相对 `conda/infrastructure` 仓库的模板路径（`templates/...`） |
| **dst** | 相对目标仓库根目录的落盘路径（如 `.github/ISSUE_TEMPLATE/0_bug.yml`） |
| **无 src/dst 条目** | 如 `CODE_OF_CONDUCT.md`，中央同名文件直接原样放置 |
| **with.placeholder** | 模板内占位符替换（如发布版本 `YY.M`），按目标仓库参数实例化 |
| **注释掉 = 未启用** | 默认关闭的能力（rever 发布文件、可选 PR 模板），仓库需时自行取消注释 |

模板文件头部普遍带注释 `# edit this in https://github.com/conda/infrastructure`，提示读者：这些文件的**权威出处是中央仓库**，本地直接修改会在下次同步时被覆盖。

## 4. conda/infrastructure 中央仓库角色

`conda/infrastructure` 是 Conda 社区 GitHub 治理的**中央仓库（单点权威）**，承担以下职责：

| 资产 | 位置 |
|------|------|
| 模板文件（社区文件/Issue/PR/发布） | `templates/` |
| 全局标签定义 | `.github/global.yml` |
| 自动化配置（stale 消息等） | `.github/messages.yml` 等 |
| 中央推送工作流 | `.github/workflows/sync.yml` |

其在 `HOW_WE_USE_GITHUB.md` 中被明确定义为"全局自动化过程的同步源"（global automation procedures synced out from the conda/infrastructure repo）。标签的**全局**定义（适用于所有仓库）放 `global.yml`，各仓库**局部**标签放各自 `.github/labels.yml`，由 `labels.yml` 工作流合并同步。

## 5. 同步触发方式：双通道

### 5.1 update.yml：目标仓库按调度拉取（Pull）

本元仓库 `.github/workflows/update.yml` 的完整流程：

1. **调度**：`schedule: cron 36 2 * * 0`（每周日运行）+ `workflow_dispatch` 手动触发。
2. **检出 + 配置 git 用户**：以 `Conda Bot`（`18747875+conda-bot@users.noreply.github.com`）身份操作，`persist-credentials: false`。
3. **拉取模板**：调用 `conda/actions/template-files` action，读取本仓库 `.github/template-files/config.yml`，按 `src/dst` 从中央仓库拉取并落盘。
4. **提交**：`git add .` + `git commit --message "🤖 updated file(s)"`（无变化则 no-op）。
5. **创建 fork**：`gh repo fork`（使用 `SYNC_TOKEN`）。
6. **开 PR**：`peter-evans/create-pull-request` 从 fork 的 `update` 分支开 PR，标题 `🤖 Update infrastructure file(s)`，正文附 `combine-durations` 与 `template-files` 的摘要。

即：**每周日拉取中央模板 → 提交 → 自动开 PR**，由维护者审阅合并，保证各仓库文件与中央一致。

### 5.2 sync.yml：中央仓库推送（Push）

中央仓库 `conda/infrastructure/.github/workflows/sync.yml` 负责**主动推送**模板、标签、工作流与文档到其他仓库（`HOW_WE_USE_GITHUB.md` 的 automation 清单第 6 项明确列出此工作流）。Pull 与 Push 双通道互为补充，确保即使目标仓库未配置 `update.yml`，也能通过中央推送获得更新。

### 5.3 双通道对比

| 维度 | update.yml（Pull） | sync.yml（Push） |
|------|--------------------|------------------|
| 执行位置 | 各目标仓库 | conda/infrastructure |
| 触发 | 每周日 cron + 手动 | 中央维护侧触发 |
| 产物 | 自动开更新 PR | 直接下发/更新文件 |
| 依赖 | `SYNC_TOKEN` | 中央侧 token |

## 6. 对 external/libs 镜像仓库维护启示

本项目将 `conda-dev/.github` 镜像至 `external/libs/conda-dev/.github`，上述模型带来以下维护启示：

1. **识别权威出处**：镜像内带 `edit this in https://github.com/conda/infrastructure` 注释的文件（模板、HOW_WE_USE_GITHUB.md、工作流），其真实权威在 `conda/infrastructure`；本地直接编辑会被上游同步覆盖。
2. **版本跟踪**：config.yml 中所有条目构成"期望状态清单"，镜像更新时应对照上游 `conda-dev/.github` 的 config.yml 与中央 `conda/infrastructure` 的 templates/ 变化，而不是仅对比镜像自身差异。
3. **参数化意识**：`with.placeholder`（如 `YY.M`）说明部分模板按仓库实例化，镜像时需保留占位符语义，勿将某个仓库的解析结果当作模板本身。
4. **避免复制粘贴**：本镜像的学习价值在于"理解同步机制本身"，若在自有项目中复用，应复刻"中央清单 + 中央仓库 + 双向同步"的模式，而非复制单个文件内容。

## 7. 本章小结

- `config.yml` = 文件采购清单：`conda/governance`（必选社区文件）+ `conda/infrastructure`（必选 cla/update、可选 projects 三件套/stale+lock/HOW_WE_USE_GITHUB/4 Issue 模板/PR 模板/注释掉的 rever 发布文件）。
- `src/dst` 声明来源与落盘路径，`with.placeholder` 实现按仓库参数化。
- `conda/infrastructure` 是唯一权威中央仓库（templates/、global.yml、sync.yml）。
- 同步双通道：各仓库 `update.yml` 每周日拉取开 PR（Pull）+ 中央 `sync.yml` 推送（Push）。

下一章深入 `HOW_WE_USE_GITHUB.md` 的核心机制：Issue Sorting 与标签体系。

---

**上一章**：[04-community-files.md](04-community-files.md) | **返回目录**：[00-overview.md](00-overview.md) | **下一章**：[06-issue-sorting-labeling.md](06-issue-sorting-labeling.md)
