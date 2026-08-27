---
version: "1.0"
x-toml-ref: "../../../.meta/toml/.trae/specs/create-conda-dev-github-wiki-tutorial/spec.toml"
---
# conda-dev/.github 元仓库 Wiki 教程 - Product Requirement Document

## Why
GitHub 组织级 `.github` 元仓库（meta-repository）是大型开源组织统一管理"社区健康文件 + GitHub Actions 工作流 + Issue 模板 + 标签体系"的核心设施。`conda/.github`（本地镜像位于 `external/libs/conda-dev/.github`）是这一模式的**业界标杆案例**：通过 `conda/infrastructure` 中央仓库 + `template-files/config.yml` 映射清单，实现 CLA 签署校验、Issue Sorting 标签体系、Stale/Lock 自动化、标签同步、PR 自动入板、模板与文件每周自动同步等全链路自动化。

开发人员常对以下问题感到困惑：
- GitHub 组织级 `.github` 元仓库到底是什么？与普通仓库的 `.github/` 目录有何区别？
- 多个仓库的 CLA 校验、Issue 模板、标签如何做到**一处修改、处处生效**？
- GitHub Actions 的 `pull_request_target`、`concurrency`、细粒度 `permissions`、`ubuntu-slim` runner、Action 版本锁定（SHA + 注释）等高级配置如何组合使用？
- `stale`/`lock`/`labels`/`issues`/`project`/`update` 六个工作流各自的职责与协作关系？
- 如何在自有组织/仓库中复制这套模式？

本教程旨在系统回答上述问题，将 `conda/.github` 元仓库的完整结构、配置语义、实现逻辑沉淀为可复用知识，填补知识库在"GitHub 组织级社区基础设施"领域的空白。

## What Changes
- **新增** 10 个原子化 Markdown 文档，构成完整的 conda-dev/.github 元仓库 wiki 教程，放置于 `.agents/docs/knowledge/learning/08-systems-infrastructure/conda-dev-github-wiki/` 目录
- **新增** 教程总览与导航索引（`00-overview.md`）
- **新增** 仓库整体架构章节（`01-repository-structure.md`），涵盖根级文件、`.github/` 各子目录及文件作用、与普通仓库 `.github/` 的区别
- **新增** GitHub Actions 工作流详解章节（`02-workflows-deep-dive.md`），逐一对 `cla.yml`/`issues.yml`/`labels.yml`/`lock.yml`/`project.yml`/`stale.yml`/`update.yml` 七个工作流解析配置项含义、参数说明与使用场景
- **新增** Issue 模板详解章节（`03-issue-templates.md`），解析 `0_bug.yml`/`1_feature.yml`/`2_documentation.yml`/`epic.yml` 四个 GitHub Issue Form 模板的结构与字段
- **新增** 社区健康文件详解章节（`04-community-files.md`），解析 `CODE_OF_CONDUCT.md`、`HOW_WE_USE_GITHUB.md`、`profile/README.md`、`.gitignore` 的用途与内容
- **新增** 中央同步模型章节（`05-infrastructure-sync-model.md`），解析 `template-files/config.yml` 映射清单、`conda/infrastructure` → 各仓库的模板/标签/工作流同步机制
- **新增** Issue Sorting 与标签体系章节（`06-issue-sorting-labeling.md`），解析 Issue Sorting 工作流、`type`/`source`/`severity` 标签约定、Roadmap Board 流转（含 Mermaid 流程图）
- **新增** 常见操作指南章节（`07-operations-guide.md`），涵盖配置修改、功能扩展、问题排查三个场景的操作步骤与示例
- **新增** 最佳实践与注意事项章节（`08-best-practices.md`），提炼可复用的 GitHub 组织治理模式、安全最佳实践与反模式
- **新增** 术语表与参考资料章节（`09-resources.md`），含 ≥15 条 GitHub/GitHub Actions 术语与权威参考资料
- **不修改** 目标仓库 `external/libs/conda-dev/.github` 的任何内容（只读学习，不写回第三方依赖）

## Impact
- **Affected specs**: 无（独立新增 wiki 教程，不修改已有 spec）
- **Affected code**: 无代码改动，仅文档新增
- **Affected files**:
  - 新增：`.agents/docs/knowledge/learning/08-systems-infrastructure/conda-dev-github-wiki/00-overview.md` ~ `09-resources.md` + `README.md` 共 11 个文件
  - 可能由 `docgen-cmd` 后续自动纳入 Learning Wiki 索引（不在本 spec 范围内）
- **Related wikis**:
  - [git-advanced-wiki](../../../.agents/docs/knowledge/learning/08-systems-infrastructure/git-advanced-wiki/00-overview.md) — 同属 08 系统与基础设施主题，Git 底层操作与 GitHub 组织治理互补
  - [git-baidu-sync](../../../.agents/docs/knowledge/learning/08-systems-infrastructure/git-baidu-sync/README.md) — 同主题，Git 仓库同步工作流实践

## Background & Context
GitHub 通过 `.github` 特殊目录约定提供组织级（organization）和仓库级社区功能配置：
- 组织级 `.github` 仓库（如 `conda/.github`）的社区健康文件（CODE_OF_CONDUCT 等）、Issue 模板、PR 模板可被该组织下**所有仓库**继承
- `.github/workflows/` 存放 GitHub Actions 工作流定义；`profile/README.md` 是组织主页展示内容

conda 组织在此基础上进一步引入 **`conda/infrastructure` 中央治理仓库**模式：所有模板、标签、工作流、文档先在中央仓库维护，再通过 `template-files/config.yml` 映射清单 + `update.yml` 每周同步 + `sync.yml`（中央侧）推送到各成员仓库。`conda/.github` 元仓库本身也是该同步体系的接收方之一（从 `config.yml` 可见 `CODE_OF_CONDUCT.md` 来自 `conda/governance`，其余文件来自 `conda/infrastructure`）。

本教程以本地 `external/libs/conda-dev/.github`（Git 提交 a9dc789）为事实来源，逐文件核实后撰写，保证内容专业、准确、可追溯。

## ADDED Requirements

### Requirement: 教程总览与导航
The system SHALL provide a `00-overview.md` file containing the tutorial overview, target audience, reading path, chapter navigation table, and a Mermaid diagram positioning the conda `.github` meta-repo in the GitHub org governance stack.

#### Scenario: 用户访问教程入口
- **WHEN** 用户打开 `00-overview.md`
- **THEN** 文档包含：教程简介、章节导航表（00-09 + README）、Mermaid 概念定位图、目标读者说明、阅读路径建议、与 08 主题下其他 wiki 的关联指引

### Requirement: 仓库整体架构文档
The system SHALL provide a `01-repository-structure.md` file explaining the complete folder structure of the conda `.github` meta-repo and the purpose of every subdirectory and file.

#### Scenario: 用户理解仓库全貌
- **WHEN** 用户阅读 `01-repository-structure.md`
- **THEN** 文档包含：完整目录树（根级 + `.github/` 各子目录）、每个文件/目录的作用说明表、组织级 `.github` 元仓库与普通仓库 `.github/` 目录的区别对比、本仓库在同步体系中的角色定位

### Requirement: 工作流详解文档
The system SHALL provide a `02-workflows-deep-dive.md` file explaining all 7 GitHub Actions workflows in the `.github/workflows/` directory, covering each workflow's configuration semantics, parameters, and usage scenarios.

#### Scenario: 用户学习工作流配置
- **WHEN** 用户阅读 `02-workflows-deep-dive.md`
- **THEN** 文档覆盖以下 7 个工作流，每个含：触发事件、权限声明、任务步骤、关键配置项语义、使用场景：
  - `cla.yml`（CLA 签署校验：`pull_request_target` 触发、`conda/actions/check-cla`）
  - `issues.yml`（Issue 自动化：`pending::feedback` ↔ `pending::support` 标签切换）
  - `labels.yml`（标签同步：`EndBug/label-sync` + global/local 双源合并）
  - `lock.yml`（线程锁定：`dessant/lock-threads` 每日调度）
  - `project.yml`（PR 自动入板：`actions/add-to-project`）
  - `stale.yml`（过期清理：`actions/stale` + matrix 双策略 + 消息模板外部化）
  - `update.yml`（仓库文件自动更新：`conda/actions/template-files` + 自动 fork + PR）
- 并提炼跨工作流共性配置模式（`concurrency`、最小 `permissions`、`pull_request_target` 安全注意、Action 版本锁定方式、`ubuntu-slim` runner）

### Requirement: Issue 模板详解文档
The system SHALL provide a `03-issue-templates.md` file explaining the structure, fields, validations, and labels of the 4 GitHub Issue Form templates.

#### Scenario: 用户学习 Issue 模板
- **WHEN** 用户阅读 `03-issue-templates.md`
- **THEN** 文档覆盖 `0_bug.yml`/`1_feature.yml`/`2_documentation.yml`/`epic.yml` 四个模板，每个含：`name`/`description`/`labels`/`body` 各字段语义、block 类型（markdown/checkboxes/textarea）与 `validations` 用法、模板如何与 Issue Sorting 标签联动、以及"编辑源在 conda/infrastructure"的单一来源说明

### Requirement: 社区健康文件详解文档
The system SHALL provide a `04-community-files.md` file explaining the purpose and content of `CODE_OF_CONDUCT.md`, `HOW_WE_USE_GITHUB.md`, `profile/README.md`, and `.gitignore`.

#### Scenario: 用户了解社区健康文件
- **WHEN** 用户阅读 `04-community-files.md`
- **THEN** 文档包含：各文件用途说明、`HOW_WE_USE_GITHUB.md` 的知识产权（Issue Sorting 定义、标签约定、代码评审流程、合并规范）、`profile/README.md` 的组织主页内容解析（conda/conda-incubator/conda-archive 三组织架构）、`.gitignore` 的 Python 模板来源说明

### Requirement: 中央同步模型文档
The system SHALL provide a `05-infrastructure-sync-model.md` file explaining the `template-files/config.yml` mapping manifest and the `conda/infrastructure` central governance sync mechanism.

#### Scenario: 用户理解中央同步机制
- **WHEN** 用户阅读 `05-infrastructure-sync-model.md`
- **THEN** 文档包含：`config.yml` 完整映射清单解析（必选/可选文件、`src`/`dst` 映射、`with.placeholder` 参数化）、`conda/infrastructure` 中央仓库的角色、同步触发方式（`update.yml` 每周调度拉取 + 中央 `sync.yml` 推送）、对 `external/libs` 镜像仓库的维护启示

### Requirement: Issue Sorting 与标签体系文档
The system SHALL provide a `06-issue-sorting-labeling.md` file explaining the Issue Sorting workflow, label conventions (`type`/`source`/`severity`), and Roadmap Board progression, with Mermaid flowcharts.

#### Scenario: 用户理解 Issue 治理流程
- **WHEN** 用户阅读 `06-issue-sorting-labeling.md`
- **THEN** 文档包含：Issue Sorting 概念与目的、四种优先级分类（Do now/Do sometime/Support/Never）、标签体系语法（`[category::topic]`）与互斥/并发规则、Roadmap Board 流转流程（Refinement→Backlog→Current Sprint，Mermaid 图）、`HOW_WE_USE_GITHUB.md` 提供的常见回复模板（Duplicate/Anaconda/Off-topic）

### Requirement: 常见操作指南文档
The system SHALL provide a `07-operations-guide.md` file covering hands-on operations: configuration modification, feature extension, and troubleshooting.

#### Scenario: 用户按指南操作
- **WHEN** 用户阅读 `07-operations-guide.md`
- **THEN** 文档包含三个操作场景：
  - 配置修改：修改工作流触发条件/权限/参数、修改标签、修改 Issue 模板的具体步骤（含 YAML 修改示例）
  - 功能扩展：新增一个工作流、新增一种标签类别、扩展 Issue 模板字段的完整流程（含代码示例与验证方式）
  - 问题排查：工作流不触发的常见原因（权限不足/触发条件不匹配/fork 限制）、Action 版本更新与 SHA 锁定、`dry-run`/`debug-only` 调试模式、`gh` CLI 手动触发 `workflow_dispatch`

### Requirement: 最佳实践与注意事项文档
The system SHALL provide a `08-best-practices.md` file distilling reusable GitHub org governance patterns, security best practices, and anti-patterns.

#### Scenario: 用户借鉴最佳实践
- **WHEN** 用户阅读 `08-best-practices.md`
- **THEN** 文档包含：可迁移到自有组织/仓库的治理模式（单一来源原则、模板与标签分离、Action 版本锁定、最小权限声明）、安全最佳实践（`pull_request_target` 风险与缓解、密钥管理 `secrets.PROJECT_TOKEN`/`CLA_ACTION_TOKEN`/`SYNC_TOKEN` 的最小授权）、≥3 个反模式（来自实际配置教训）、检验标准清单

### Requirement: 术语表与参考资料文档
The system SHALL provide a `09-resources.md` file providing a comprehensive glossary and authoritative references.

#### Scenario: 用户深入学习
- **WHEN** 用户阅读 `09-resources.md`
- **THEN** 文档包含：术语表（≥15 条：meta-repository/pull_request_target/concurrency/permissions/workflow_dispatch/issue_comment/stale/lock/CLA/Issue Form/action version pinning/ubuntu-slim 等）、权威参考资料链接（GitHub Docs、GitHub Actions 官方文档、conda/infrastructure、conda/governance）、按难度分级的扩展阅读建议

### Requirement: 文档元数据与导航规范
The system SHALL ensure all wiki files follow consistent metadata and navigation conventions matching the existing `git-advanced-wiki`/`wsl-wiki` pattern.

#### Scenario: 验证文档元数据
- **WHEN** 检查任意 wiki 文件 frontmatter
- **THEN** 包含完整 YAML frontmatter 字段：`id`、`title`、`x-toml-ref`、`source`（值为 `spec:create-conda-dev-github-wiki-tutorial`）、`category`（值为 `learning`）、`tags`、`date`、`status`、`author`、`summary`

#### Scenario: 验证双向导航
- **WHEN** 检查分章文档（01-08）
- **THEN** 每个文档底部包含双向导航：上一章、返回目录（`00-overview.md`）、下一章

## Non-Functional Requirements
- **NFR-1**: 每个原子文档不超过 300 行，遵循单一职责原则
- **NFR-2**: 技术术语准确，所有配置解析基于本地仓库文件事实（`external/libs/conda-dev/.github`），禁止臆造未验证的配置项
- **NFR-3**: 语言专业准确同时保持 Wiki 风格——客观中立、结构清晰、适合技术读者参考
- **NFR-4**: 所有内部链接使用相对路径，无 `file:///` 绝对路径，通过链接检查
- **NFR-5**: 代码/配置示例须标注语言类型（yaml/mermaid/bash），示例与本地仓库实际内容一致或明确标注为"扩展示例"
- **NFR-6**: 遵循项目文档命名规范（kebab-case，数字前缀排序）

## Constraints
- **Technical**: 使用 Markdown + Mermaid 图表，遵循项目现有 wiki 格式（参考 `08-systems-infrastructure/wsl-wiki/` 结构）
- **Business**: 教程内容聚焦 GitHub 组织级治理可复用知识，与 08 主题下现有 Git wiki 形成互补
- **Dependencies**:
  - 依赖本地仓库 `external/libs/conda-dev/.github` 的只读事实来源
  - 依赖项目现有知识库结构与链接检查工具

## Assumptions
- 读者具备基础 GitHub 使用经验（Issue/PR/分支），了解 YAML 语法
- 读者了解 GitHub Actions 基本概念（workflow/job/step/event）
- 教程放置于 `.agents/docs/knowledge/learning/08-systems-infrastructure/conda-dev-github-wiki/` 目录
- 完成后可由 `docgen-cmd` 自动纳入 Learning Wiki 索引（不在本 spec 验收范围内）

## Acceptance Criteria

### AC-1: 目录结构完整
- **Given**: 教程创建完成
- **When**: 查看目标目录
- **Then**: 包含 `00-overview.md` ~ `09-resources.md` + `README.md` 共 11 个文件，每个原子文档 < 300 行
- **Verification**: `programmatic`

### AC-2: 工作流覆盖完整
- **Given**: `02-workflows-deep-dive.md`
- **When**: 阅读文档
- **Then**: 覆盖全部 7 个工作流，每个含触发事件、权限、步骤、关键配置语义、使用场景
- **Verification**: `human-judgment`

### AC-3: 配置解析准确
- **Given**: 全部章节中的配置引用
- **When**: 对照本地仓库 `external/libs/conda-dev/.github` 逐项核对
- **Then**: 每个被引用的工作流名、Action 名、参数名、触发事件均与本地仓库文件一致，无臆造
- **Verification**: `programmatic`（抽样核对）

### AC-4: 含 Mermaid 流程图
- **Given**: 教程完成
- **When**: 检索 Mermaid 代码块
- **Then**: 至少包含 2 处 Mermaid 流程图（如 00-overview 定位图、06-issue-sorting 流转图）
- **Verification**: `programmatic`

### AC-5: 元数据规范
- **Given**: 所有 11 个文档
- **When**: 检查 frontmatter
- **Then**: 每个文档包含完整 YAML frontmatter，`source` 字段值为 `spec:create-conda-dev-github-wiki-tutorial`，`category` 为 `learning`
- **Verification**: `programmatic`

### AC-6: 链接有效
- **Given**: 教程完成
- **When**: 运行链接检查
- **Then**: 所有内部相对路径链接有效，无 `file:///` 绝对路径断链
- **Verification**: `programmatic`

### AC-7: 双向导航
- **Given**: 分章文档（01-08）
- **When**: 检查导航链接
- **Then**: 每个文档包含上一章、返回目录、下一章的双向导航链接
- **Verification**: `human-judgment`

### AC-8: 术语表完整
- **Given**: `09-resources.md`
- **When**: 阅读文档
- **Then**: 包含 ≥15 条术语、权威参考资料链接、分难度扩展阅读建议
- **Verification**: `human-judgment`

### AC-9: 操作指南可执行
- **Given**: `07-operations-guide.md`
- **When**: 阅读文档
- **Then**: 包含配置修改/功能扩展/问题排查三个场景，每个场景有具体步骤与可复制示例
- **Verification**: `human-judgment`

### AC-10: 最佳实践可迁移
- **Given**: `08-best-practices.md`
- **When**: 阅读文档
- **Then**: 包含可迁移治理模式、安全最佳实践、≥3 个反模式、检验标准清单
- **Verification**: `human-judgment`

## Open Questions
- [ ] 教程是否需要将"组织级 `.github` 元仓库"与"仓库级 `.github/` 目录"的继承规则单独成章，还是并入 `01-repository-structure.md`？
- [ ] `conda/infrastructure` 中央仓库的 `sync.yml` 推送机制在本地镜像中不可见，是否需要在 `05-infrastructure-sync-model.md` 中补充 GitHub Actions 复用（`actions/`）机制作为推断依据？
