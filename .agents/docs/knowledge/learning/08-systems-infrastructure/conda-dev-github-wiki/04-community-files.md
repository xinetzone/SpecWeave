---
id: conda-dev-github-wiki-04-community-files
title: "社区健康文件详解"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/08-systems-infrastructure/conda-dev-github-wiki/04-community-files.toml"
source: "spec:create-conda-dev-github-wiki-tutorial"
category: "learning"
tags: ["conda", "code-of-conduct", "community", "github-profile", "gitignore", "governance"]
date: "2026-08-20"
status: "stable"
author: "SpecWeave"
summary: "conda .github 元仓库社区健康文件详解"
---

# 社区健康文件详解

> 本章解析 `conda-dev/.github` 元仓库根目录下的"社区健康文件"（Community Health Files）。它们是 GitHub 组织/仓库层面的"软基础设施"，定义了社区的行为规范、协作流程与对外门面。本章对象即 04-community-files：`CODE_OF_CONDUCT.md`、`HOW_WE_USE_GITHUB.md`、`profile/README.md` 与 `.gitignore`。

## 1. 文件清单总览

| 文件 | 类型 | 作用 | 中央同步来源 |
|------|------|------|-------------|
| `CODE_OF_CONDUCT.md` | 行为准则 | 定义社区行为规范与举报途径 | `conda/governance`（config.yml 必选） |
| `HOW_WE_USE_GITHUB.md` | 协作流程 | 定义 Issue Sorting、标签、评审等社区玩法 | `conda/infrastructure`（`templates/HOW_WE_USE_GITHUB.md`） |
| `profile/README.md` | 组织主页 | GitHub 组织 profile 页展示内容 | 组织级固定文件（`profile/` 目录） |
| `.gitignore` | 忽略规则 | 标准 Python 忽略模板 | 仓库自身维护（非模板文件） |

## 2. CODE_OF_CONDUCT.md — Conda 组织行为准则

文件采用"短版先行，长版在后"的结构，短版浓缩了核心精神，长版展开细节。

### 2.1 短版（The Short Version）

- **Be kind to others**：善待他人，不侮辱、不贬低他人，行为专业。
- **No inappropriate jokes**：性骚扰、性别歧视、种族歧视或排他性玩笑不适合 Conda 组织。
- **Professional audience**：所有沟通都应适合包含不同背景人士的专业受众；不恰当的性语言与图像不被接受。
- **Harassment-free 承诺**：无论性别、性取向、性别认同与表达、残障、外貌、体型、种族或宗教，组织致力于提供无骚扰的社区环境。

### 2.2 举报途径（Report an Incident）

提供了三种举报渠道：

1. **表单**：通过 [举报表单](https://form.jotform.com/221527028480048) 举报事件。
2. **邮件**：发送至 [conduct@conda.org](mailto:conduct@conda.org)。
3. **委员会成员**：可私下联系委员会成员或 CoC 事件代表举报（源码中对应 `#committee-membership` 与 `#coc-representatives` 锚点章节）。

### 2.3 多元化声明（Diversity Statement）

组织欢迎所有背景与身份的人参与社区，致力于培养"相互尊重、宽容与学习"的文化。声明强调：

- 多元社区更强大、更有活力，能产出更好的软件与更好的科学。
- 多元社区拥有更多潜在贡献者、更多思想来源、更少的阻碍开发的共享假设。
- 虽采用包容一切的通用措辞，但承认存在受到系统性歧视与边缘化的特定身份群体，欢迎所有人参与。

### 2.4 适用范围与行为标准

- **适用范围**：适用于所有参与 Conda 组织社区的人，在组织的所有相关活动中、以任何身份代表组织时（含活动志愿者、演讲者）均须遵守；覆盖组织管理的所有空间（公开/私密邮件列表、Issue 跟踪器、Wiki、论坛及其他沟通渠道），同样适用于组织的线下活动（与会者、演讲者、志愿者、展台人员、活动赞助商）。
- **行为标准**：长版展开为"友善共情耐心、协作、求知、谨慎措辞"等鼓励性标准，以及"不可接受行为"清单（组织致力于让社区参与成为无骚扰体验）。
- 文件强调"本准则并非详尽无遗，重在领会其精神而不只是字面"。

### 2.5 与 governance 仓库的关系

本文件由 `conda/governance` 中央维护，`config.yml` 将 `CODE_OF_CONDUCT.md` 列为 `conda/governance` 下的**必选**社区文件（见下一章）。`profile/README.md` 中的 `[coc]` 链接也指向 `conda/governance` 中的短版章节，确保全文只有一处权威出处。

## 3. HOW_WE_USE_GITHUB.md — 我们如何使用 GitHub

### 3.1 文档定位

这是 Conda 社区关于"如何在 GitHub 上协作"的**权威流程文档**，采用 FAQ 风格编写，目标是：

> 描述社区如何利用 GitHub Issues 跟踪 Bug 与功能请求，同时兼顾开发实践与项目管理（发布周期、功能规划、优先级排序等）。

### 3.2 编辑规范

文件第一行为注释 `<!-- edit this in https://github.com/conda/infrastructure -->`，明确其**权威编辑位置在 `conda/infrastructure`**，由中央同步机制下发到各仓库（详见下一章）。这意味着本文件属于"中央管治资产"而非各仓库自主内容。

### 3.3 内容总览（Topics）

| 章节 | 要点 |
|------|------|
| What is "Issue Sorting"? | 四种优先级、排序流程与目标 |
| Labeling | 标签语法、互斥/并发规则、必需标签 |
| Types of Issues | 标准 Issue、Epics、Spikes |
| Working on Issues | 认领 Issue 的流程与超时回收 |
| Development Processes | 功能开发、变更流程、Campsite Rule |
| Code Review and Merging | 评审要求、最佳实践、合并方式 |

> 这些内容是 Conda 社区的"知识产权"（过程与方法论资产），通过 `config.yml` 的可选条目 `src: templates/HOW_WE_USE_GITHUB.md` → `dst: HOW_WE_USE_GITHUB.md` 同步到各仓库。详细解读见第 06 章（Issue Sorting 与标签体系）与第 07 章（运营指南）。

## 4. profile/README.md — 组织主页

`profile/README.md` 是 GitHub 组织的 profile 展示内容（组织主页横幅）。Conda 社区在 GitHub 上由**三个组织**构成，本文件即其门面。

### 4.1 三组织架构

| 组织 | 定位 |
|------|------|
| [conda](https://github.com/conda) | 官方支持的项目所在 |
| [conda-incubator](https://github.com/conda-incubator) | 社区孵化中的项目所在 |
| [conda-archive](https://github.com/conda-archive) | 不活跃、已归档的项目所在 |

### 4.2 三组织流转 Mermaid 图

```mermaid
flowchart LR
    community(Community):::community
    incubator(conda-incubator):::github
    conda(conda):::github
    archive(conda-archive):::github

    community-- invitation -->incubator
    incubator-- graduation -->conda
    conda-- inactive -->archive

    classDef community fill:#fff,stroke:#24292f,stroke-width:2,stroke-dasharray: 5 5
    classDef github fill:#24292f,stroke:none,color:#fff
```

流转语义：

- **Community → conda-incubator**：社区项目经邀请进入孵化。
- **conda-incubator → conda**：孵化成熟后"毕业"进入官方组织。
- **conda → conda-archive**：官方项目不活跃后归档。
- 源码中注释掉的边（incubator→archive 等）表示预留但未启用的流转路径。
- 源码附注：项目也可应请求直接加入 conda 组织（需向 steering council 申请，参考 governance 仓库的 "Incorporate a Software Project into the main conda Organization"）。

### 4.3 重要仓库（Important Repositories）

重点推荐三个核心仓库：

- [conda](https://github.com/conda/conda)：conda 包管理器本体。
- [conda-build](https://github.com/conda/conda-build)：构建工具。
- [rattler](https://github.com/conda/rattler)：新一代跨平台依赖求解/构建引擎。

### 4.4 Projects（组织级看板）

| 看板 | 链接 | 用途 |
|------|------|------|
| 🧭 Anaconda's Planning Board | `orgs/conda/projects/22` | Anaconda Inc. 主导的专项规划看板 |
| 📚 Epics | `orgs/conda/projects/14` | 全组织各项目的 Epic 列表 |
| 🔎 Review | `orgs/conda/projects/16` | 全组织进行中/已完成的 PR 评审列表 |

### 4.5 重要社区入口（Important Community Places）

- [conda.org](https://conda.org/)：Conda 社区站点。
- [conda.io](https://conda.io/)：Conda 文档站点。
- [Governance](https://github.com/conda/governance)：社区如何运作的治理定义。
- [CEPs](https://github.com/conda/ceps)：Conda Enhancement Proposals（增强提案）。
- [Zulip](https://conda.zulipchat.com/)：实时聊天。
- [BlueSky](https://bsky.app/profile/conda.org)：最新动态。

文件末尾声明：Conda 组织内的所有互动受[行为准则](https://github.com/conda/governance/blob/main/CODE_OF_CONDUCT.md#the-short-version)约束，与第 2 节内容呼应。

## 5. .gitignore — 标准 Python 模板

`.gitignore` 是典型的 **GitHub 标准 Python .gitignore 模板**（与 `github/gitignore` 仓库的 Python 模板一致），覆盖以下类别：

- **字节码/优化文件**：`__pycache__/`、`*.py[cod]`、`*$py.class`。
- **C 扩展**：`*.so`。
- **分发/打包**：`build/`、`dist/`、`eggs/`、`*.egg-info/`、`wheels/` 等。
- **安装器日志**：`pip-log.txt`、`pip-delete-this-directory.txt`。
- **单元测试/覆盖率**：`htmlcov/`、`.tox/`、`.pytest_cache/`、`.coverage` 等。
- **环境**：`.env`、`.venv`、`venv/`、`ENV/` 等。
- **其他框架产物**：Django（`db.sqlite3`）、Flask（`instance/`）、Sphinx（`docs/_build/`）、Jupyter（`.ipynb_checkpoints`）、mypy、pyre 等。

要点：该文件为仓库自身维护（不在 `config.yml` 映射清单内），属于元仓库自身的开发规范而非下发资产。

## 6. 本章小结

| 文件 | 一句话定位 |
|------|-----------|
| `CODE_OF_CONDUCT.md` | 行为准则（短版 + 举报途径 + 多元化声明 + 适用范围），必选中央同步 |
| `HOW_WE_USE_GITHUB.md` | 社区协作流程知识产权，编辑于 `conda/infrastructure` |
| `profile/README.md` | 三组织架构门面 + 组织级 Projects/社区入口 |
| `.gitignore` | 标准 Python 忽略模板，仓库自身维护 |

四个文件共同构成元仓库的"社区健康层"：准则管行为、流程管协作、profile 管门面、gitignore 管仓库卫生。下一章将揭示它们如何通过 `config.yml` 与 `conda/infrastructure` 中央仓库实现批量下发。

---

**上一章**：[03-issue-templates.md](03-issue-templates.md) | **返回目录**：[00-overview.md](00-overview.md) | **下一章**：[05-infrastructure-sync-model.md](05-infrastructure-sync-model.md)
