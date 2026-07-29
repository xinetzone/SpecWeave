---
version: "1.0"
source: "spec: .trae/specs/core-foundation/create-github-cli-wiki-tutorial/spec.md"
date: 2026-07-24
scope: task
tags: ["github-cli", "wiki-tutorial", "knowledge-base", "retrospective", "seven-concepts"]
---

# GitHub CLI Wiki 教程创建 — 复盘报告

> **生成日期**：2026-07-24
> **任务范围**：task 级别
> **方法论**：七概念方法论 R→I→E→Export 知识沉淀链路（场景4：知识沉淀）
> **方法论场景**：场景4 — 知识沉淀（R→I→E→C），本次复盘覆盖 R→I→E→Export 四个阶段

---

## 执行摘要

本次任务基于三个互补学习源（GitHub CLI 中文手册、官方英文文档、源码仓库），创建了一套完整的 GitHub CLI Wiki 教程，共 11 个文件（8 个 Wiki 章节 + 3 个 Spec 文件），总计 7,082 行。任务采用 Spec 驱动 + 并行 sub-agent 批量写作 + 原子化提交策略，45/45 个 checklist 项全部通过验证。执行过程中遇到 Windows PowerShell heredoc 语法兼容性问题，通过切换单行 commit message 格式解决。本次复盘按七概念方法论四阶段展开：事实收集（R）→ 洞察提炼（I）→ 模式萃取（E）→ 导出归档（Export）。

---

## R 阶段：事实收集

> **原则**：纯客观事实，不含因果词（"因为""所以""导致""由于"）。仅陈述可验证的客观数据。

### 基本信息

| 属性 | 值 |
|------|-----|
| 任务名称 | 创建 GitHub CLI Wiki 教程 |
| 任务类型 | 知识沉淀 — 多源 Wiki 教程创建 |
| 执行日期 | 2026-07-24 |
| 方法论 | 七概念方法论场景4（知识沉淀 R→I→E→C） |
| 执行环境 | Windows PowerShell（Trae IDE） |
| Sub-agent 使用 | 是（两批共 8 个并行 sub-agent） |

### 学习源

| # | 来源 | URL | 用途 |
|---|------|-----|------|
| 1 | GitHub CLI 中文手册 | https://cli.githubdocs.cn/manual/ | 命令结构与中文参考 |
| 2 | GitHub CLI 官方文档 | https://cli.github.com/ | 详细参数与英文原文 |
| 3 | GitHub CLI 源码仓库 | https://github.com/cli/cli | 实现细节与扩展机制 |

### 产出物清单

| 文件 | 类型 | 行数 |
|------|------|------|
| 00-overview.md | Wiki 章节 | 191 |
| 01-installation.md | Wiki 章节 | 507 |
| 02-basic-commands.md | Wiki 章节 | 842 |
| 03-pr-workflow.md | Wiki 章节 | 1,022 |
| 04-actions-cicd.md | Wiki 章节 | 1,178 |
| 05-advanced-usage.md | Wiki 章节 | 1,134 |
| 06-faq-troubleshooting.md | Wiki 章节 | 1,113 |
| 07-cheatsheet.md | Wiki 章节 | 772 |
| spec.md | Spec 定义 | 135 |
| tasks.md | 任务拆分 | 90 |
| checklist.md | 质量检查清单 | 98 |
| **合计** | **11 个文件** | **7,082** |

### 内容覆盖范围

覆盖 13+ 个 gh 子命令组：

`auth`, `repo`, `issue`, `pr`, `actions`, `release`, `gist`, `api`, `extension`, `alias`, `config`, `search`, `secret`/`variable`

### 提交记录

| # | 提交信息 | 包含文件 |
|---|---------|---------|
| 1 | `docs(gh-cli-wiki): add spec.md` | spec.md |
| 2 | `docs(gh-cli-wiki): add 00-overview.md` | 00-overview.md |
| 3 | `docs(gh-cli-wiki): add 01-installation.md` | 01-installation.md |
| 4 | `docs(gh-cli-wiki): add 02-basic-commands.md` | 02-basic-commands.md |
| 5 | `docs(gh-cli-wiki): add 03-pr-workflow.md` | 03-pr-workflow.md |
| 6 | `docs(gh-cli-wiki): add 04-actions-cicd.md` | 04-actions-cicd.md |
| 7 | `docs(gh-cli-wiki): add 05-advanced-usage.md` | 05-advanced-usage.md |
| 8 | `docs(gh-cli-wiki): add 06-faq-troubleshooting.md` | 06-faq-troubleshooting.md |
| 9 | `docs(gh-cli-wiki): add 07-cheatsheet.md` | 07-cheatsheet.md |
| 10 | `docs(gh-cli-wiki): update tasks.md and checklist.md status` | tasks.md, checklist.md |

- **提交总数**：10 次原子提交
- **提交风格**：Conventional Commits（`docs(gh-cli-wiki): <subject>`）
- **每次提交文件数**：1 个文件（最后一次提交为 2 个关联文件）
- **Pre-commit hooks 通过率**：10/10

### 质量验证

| 指标 | 结果 |
|------|------|
| Checklist 总项数 | 45 |
| 通过项数 | 45 |
| 未通过项数 | 0 |
| 通过率 | 100% |

### 格式规范

| 规范项 | 实际采用 |
|--------|---------|
| 元数据格式 | YAML frontmatter（含 `source` 字段） |
| 交叉引用 | 相对路径（如 `[01-installation.md](01-installation.md)`） |
| 文件命名 | kebab-case（如 `03-pr-workflow.md`） |
| 写作语言 | 中文 |

### 并行执行详情

| 批次 | Sub-agent 数量 | 分配文件 |
|------|---------------|---------|
| 第1批 | 4 | 00-overview.md, 01-installation.md, 02-basic-commands.md, 03-pr-workflow.md |
| 第2批 | 4 | 04-actions-cicd.md, 05-advanced-usage.md, 06-faq-troubleshooting.md, 07-cheatsheet.md |

### 异常事件

1. **PowerShell heredoc 语法不兼容**：`git commit -m "$(cat <<'EOF' ...)"` 在 Windows PowerShell 中执行失败。PowerShell 不支持 bash heredoc 语法。最终采用单行 commit message 格式提交。

---

## I 阶段：洞察提炼

> **原则**：每个洞察以四元组形式呈现——现象 + 根因 + 影响 + 建议。

### 洞察 1：并行 sub-agent 分组写作显著提升效率（P0）

- **现象**：8 个 Wiki 文件分两批，每批 4 个并行 sub-agent 完成编写。每批在单次工具调用中完成 4 个文件的生成。
- **根因**：Wiki 章节之间内容独立，无跨文件依赖关系。每个章节覆盖单一主题（概述/安装/基础命令/PR 工作流/Actions/高级用法/FAQ/速查表），可独立编写。
- **影响**：与串行逐文件编写相比，总编写时间缩短约 4 倍。每个 sub-agent 的上下文更聚焦，单文件内容质量更高。
- **建议**：对于 Wiki 教程创建任务，在 Phase 2（I 阶段）预先设计章节结构，在 Phase 3（E 阶段）将所有章节并行分配给 sub-agent 编写。分组原则：每组 3-5 个主题相关的文件，单组内文件数量不超过 sub-agent 上下文窗口容量。

### 洞察 2：原子化提交产生干净、可追溯的历史（P0）

- **现象**：10 次提交，每次提交包含恰好一个文件变更（最后一次提交包含 2 个关联文件）。
- **根因**：每个文档覆盖单一主题，天然映射到"一次提交一个文件"的原子化原则。Wiki 章节的独立性使得文件粒度和提交粒度一致。
- **影响**：提交历史易于导航和审查；回退或审查特定章节仅需定位到对应 commit；`git log --oneline` 输出即为章节清单。
- **建议**：对所有 Wiki/文档创建任务强制执行原子化提交规范。规则：每个文件对应一次独立 commit，commit message 格式为 `docs(<scope>): <subject>`，提交前确保 pre-commit hooks 通过。

### 洞察 3：三源交叉验证提升内容质量（P0）

- **现象**：中文手册提供了命令结构和中文语境，英文官方文档提供了详细参数说明，源码仓库提供了实现细节和扩展机制（如 alias、extension 的内部实现）。
- **根因**：三个来源互补——中文手册偏结构（命令分组、用法概览），英文文档偏细节（参数列表、选项说明），源码仓库偏内部（实现逻辑、扩展点）。单一来源无法覆盖全部维度。
- **影响**：最终内容比任何单一来源更全面——覆盖了中文手册中未详细说明的参数细节，英文文档中未提及的实现原理，以及源码中隐含的扩展机制。
- **建议**：对于技术 Wiki 创建任务，始终使用 2+ 个互补来源。来源选择原则：一个结构化参考（手册/教程），一个详细参数参考（官方文档/API 参考），一个实现参考（源码/设计文档）。三个来源的组合关系应满足"结构→细节→内部"的递进互补。

### 洞察 4：Spec 驱动工作流确保质量一致性（P0）

- **现象**：spec.md 定义了 8 个 Requirements（SHALL 句式 + Scenarios），checklist.md 定义了 45 个验证项，实施后全部通过。
- **根因**：Spec 在设计和实施之间充当契约——Requirements 定义了"必须做什么"，Scenarios 定义了"怎么做才算做完"，checklist 定义了"如何验证做完"。三层约束形成闭环。
- **影响**：无范围蔓延，无遗漏内容，质量可验证。45 个检查项提供了客观的质量度量标准，而非主观的"感觉写完了"。
- **建议**：对所有非平凡任务保持 spec→check→implement→verify 四步工作流。spec.md 中的 Requirements 必须使用 SHALL 句式，Scenarios 必须使用 WHEN/THEN 句式。checklist 中的每个检查项必须对应一个具体的 Requirement，且粒度足够细（如"覆盖 gh auth login 的 HTTPS 和 SSH 两种流程"而非"认证部分完整"）。

### 洞察 5：Windows PowerShell heredoc 与 git commit 的兼容性问题（P1）

- **现象**：`git commit -m "$(cat <<'EOF' ...)"` 在 Windows PowerShell 中执行失败，无法生成多行 commit message body。
- **根因**：PowerShell 不支持 bash heredoc 语法（`<<'EOF'`）。这是 bash 特有的 here-document 功能，在 PowerShell 中无等价语法。
- **影响**：多行 commit message（含 subject + body）无法通过 heredoc 方式生成，最终采用单行 commit message 格式，丢失了 body 部分的信息（如详细变更说明、关联 issue 编号）。
- **建议**：在 Windows PowerShell 环境下，使用 `git commit -m "subject" -m "body"` 双参数格式替代 heredoc；或者将 commit message 预写入临时文件，使用 `git commit -F <file>` 方式提交。在跨平台脚本中，建议使用后一种方式以确保兼容性。

---

## E 阶段：模式萃取

> **原则**：每个模式包含触发条件、核心步骤、反模式、迁移验证。按六步标准萃取法展开。

### 模式 1：多源 Wiki 创建工作流

**一句话描述**：基于 2+ 个互补外部文档源，通过 Spec 驱动 + 并行 sub-agent 编写 + 原子化提交，高效创建高质量技术 Wiki 教程的标准化工作流。

- **触发条件**：需要基于外部文档源创建技术 Wiki 教程，且任务涉及多个独立章节、内容量超过 3000 行。
- **核心步骤**（6 步）：
  1. **识别 3+ 互补学习源**：选择结构化参考（手册/教程）+ 详细参数参考（API 文档）+ 实现参考（源码/设计文档），确保三源互补覆盖"结构→细节→内部"三个维度
  2. **设计原子化章节结构**：按单一主题拆分章节，每章独立可读，章节间通过相对路径交叉引用连接。命名采用 kebab-case，编号采用两位数字前缀（如 `03-pr-workflow.md`）
  3. **编写 Spec 三部曲**：spec.md（Requirements + Scenarios）→ tasks.md（原子任务拆分）→ checklist.md（可验证检查项），每个检查项对应一个具体 Requirement
  4. **并行编写各章节**：使用 sub-agent 批量并行编写，每批 3-5 个主题相关文件。在 sub-agent prompt 中提供完整上下文（格式要求、交叉引用格式、写作风格、内容大纲）
  5. **原子化提交**：每个文件完成即独立 commit，commit message 遵循 Conventional Commits 格式，提交前确保 pre-commit hooks 通过
  6. **全量验证**：按 checklist 逐项检查，标记通过/未通过项，记录验证结果
- **反模式**：
  - ❌ **单源学习**：仅依赖一个文档源（如仅用中文手册），导致内容片面——缺少官方文档的详细参数说明或源码中的实现原理
  - ❌ **单文件大文档**：将所有内容写在一个文件中，导致难以维护、难以并行编写、难以原子化提交
  - ❌ **跳过 Spec 直接编写**：导致范围蔓延、内容遗漏、质量不可验证。Spec 是"先想清楚再动手"的保障
  - ❌ **批量提交**：所有文件写完一次性提交，导致历史不可追溯、回退粒度太粗
  - ❌ **章节间强耦合**：章节 A 必须依赖章节 B 的内容才能理解，导致独立可读性丧失
- **迁移验证**：本模式可迁移至任何类似的外部文档→Wiki 教程创建任务，如 Docker CLI Wiki、Kubernetes CLI Wiki、AWS CLI Wiki、Git 命令大全等。核心约束不变：多源互补 + 原子化章节 + Spec 驱动 + 并行编写 + 原子提交。
- **边界条件**：
  - 文档源数量：至少 2 个互补源，超过 5 个源时信息冗余度过高，建议精选 3 个
  - 章节数量：5-15 个章节为最佳范围，少于 5 个时并行收益有限，多于 15 个时 sub-agent 管理成本上升
  - 单章行数：200-1200 行为最佳范围，过短（<100 行）时内容深度不足，过长（>1500 行）时单一文件可读性下降

### 模式 2：原子化文档提交规范

**一句话描述**：当任务涉及多个独立文档文件的创建或修改时，通过"一个文件一次提交"的原子化原则，确保提交历史干净、可追溯、可独立回退。

- **触发条件**：涉及多个独立文档文件（≥3 个）的创建或修改任务，且文件之间无强耦合关系。
- **核心步骤**（5 步）：
  1. **按主题拆分独立文件**：每个文件覆盖单一主题，确保单一职责。文件命名采用 kebab-case + 数字前缀
  2. **每完成一个文件立即独立 commit**：不等待所有文件完成。commit message 格式为 `docs(<scope>): <subject>`
  3. **commit message 遵循 Conventional Commits**：`type(scope): subject` 格式，type 为 `docs`，scope 为项目标识
  4. **提交前确保 pre-commit hooks 通过**：每次提交前运行 hooks 检查，确保格式、链接、拼写等无问题
  5. **所有文件提交后统一验证**：运行 checklist 全量检查，确认所有需求项已覆盖
- **反模式**：
  - ❌ **所有文件写完一次性提交**：一个 commit 包含 8 个文件，`git log` 无法区分各章节的变更历史
  - ❌ **一个 commit 包含多个不相关文件的修改**：如同时提交 `03-pr-workflow.md` 和 `07-cheatsheet.md`，两个文件主题无关
  - ❌ **commit message 缺乏 scope 信息**：如 `docs: add file` 而非 `docs(gh-cli-wiki): add 03-pr-workflow.md`
  - ❌ **提交未通过 hooks 检查的文件**：跳过 pre-commit 强制提交，导致后续 CI 失败
- **迁移验证**：本模式为通用文档管理最佳实践，适用于任何多文件文档项目——技术博客系列、API 文档集、知识库建设、教程体系等。核心约束不变：单一文件单一提交 + Conventional Commits + pre-commit hooks 门禁。
- **边界条件**：
  - 文件数量：3-20 个文件时原子化提交收益最大，超过 30 个文件时可考虑分批提交（每批 5-10 个）
  - 文件耦合度：如果两个文件强耦合（如 A 引用 B 的具体行号），应同时提交或先提交被引用文件
  - 提交频率：不需要每个段落修改都提交，以"可独立审查的完整变更"为提交粒度

### 模式 3：Spec 驱动文档质量保障

**一句话描述**：通过 spec.md（Requirements + Scenarios）→ tasks.md（原子任务）→ checklist.md（可验证检查项）三层 Spec 体系，确保文档类产出物的质量可定义、可度量、可验证。

- **触发条件**：需要创建结构化、可验证的文档类产出物，且任务涉及多个子任务、多个质量维度。
- **核心步骤**（5 步）：
  1. **编写 spec.md**：定义 Requirements（SHALL 句式，如"The tutorial SHALL cover all 13+ gh sub-command groups"）+ Scenarios（WHEN/THEN 句式，如"WHEN user reads installation chapter THEN they can install gh on Windows, macOS, and Linux"）
  2. **编写 tasks.md**：将每个 Requirement 拆分为可执行的原子任务，每个任务映射到一个或多个文件
  3. **编写 checklist.md**：每个 Requirement 对应 1-N 个可验证检查项。检查项粒度足够细——"覆盖 gh auth login 的 HTTPS 和 SSH 两种认证流程"而非"认证部分完整"
  4. **实施后按 checklist 逐项验证**：逐项检查、逐项标记，不跳过、不假设
  5. **记录验证结果**：标记所有通过项，记录失败项及原因，形成可追溯的验证记录
- **反模式**：
  - ❌ **先写文档再补 Spec**：Spec 应在实施前编写，作为设计契约。事后补 Spec 失去质量门作用，只能"描述已做了什么"而非"定义应该做什么"
  - ❌ **checklist 过于笼统**：如检查项为"文档完整"而非"覆盖 gh auth login 的 HTTPS 和 SSH 两种认证流程"。笼统的检查项不可验证，无法提供客观的质量度量
  - ❌ **Spec 和实际产出不一致时强行通过 checklist**：发现了不一致但不修正产出物或 Spec，而是降低检查标准。这破坏了 Spec 作为契约的权威性
  - ❌ **Requirements 缺少 Scenarios**：只有"应覆盖安装"而没有"WHEN 用户在 Windows 上 THEN 可通过 winget 安装"，导致实施者无法判断"覆盖到什么程度算完成"
- **迁移验证**：本模式适用于任何需要质量保证的文档创建任务——技术文档、用户手册、API 参考、培训材料、知识库条目等。核心约束不变：Requirement（SHALL）+ Scenario（WHEN/THEN）+ Checklist（细粒度可验证检查项）。
- **边界条件**：
  - 任务复杂度：简单任务（单文件、<500 行）使用简化版 Spec（仅 checklist）即可
  - 团队规模：单人项目 Spec 可简化，多人协作时必须完整 Spec 以确保共识
  - Spec 变更管理：实施过程中发现 Spec 需要调整时，先更新 Spec 再修改实施，保持 Spec 和实施的同步

---

## Export：归档与交付

### 报告信息

| 属性 | 值 |
|------|-----|
| 报告路径 | `docs/knowledge/learning/github-cli-wiki/RETROSPECTIVE.md` |
| 生成日期 | 2026-07-24 |
| 方法论场景 | 七概念场景4 — 知识沉淀（R→I→E→C） |
| 本次覆盖阶段 | R→I→E→Export |
| 关联 Spec | `.trae/specs/core-foundation/create-github-cli-wiki-tutorial/spec.md` |
| 关联产出物 | `docs/knowledge/learning/github-cli-wiki/` 目录下 8 个 Wiki 文件 |

### 产出物导航

| 文件 | 说明 |
|------|------|
| [00-overview.md](00-overview.md) | GitHub CLI 概述与教程导航 |
| [01-installation.md](01-installation.md) | 安装指南（Windows/macOS/Linux） |
| [02-basic-commands.md](02-basic-commands.md) | 基础命令（auth/repo/issue/gist/api） |
| [03-pr-workflow.md](03-pr-workflow.md) | PR 工作流（create/review/merge/checkout） |
| [04-actions-cicd.md](04-actions-cicd.md) | Actions CI/CD 集成（run/workflow/secret/variable） |
| [05-advanced-usage.md](05-advanced-usage.md) | 高级用法（alias/config/extension/search） |
| [06-faq-troubleshooting.md](06-faq-troubleshooting.md) | 常见问题与排错 |
| [07-cheatsheet.md](07-cheatsheet.md) | 命令速查表 |

### 模式成熟度更新

| 模式 | 当前成熟度 | 本次触发 | 验证方式 |
|------|-----------|---------|---------|
| 多源 Wiki 创建工作流 | L2（已验证） | 本次任务全程应用 | 3 源交叉验证，45/45 checklist 通过 |
| 原子化文档提交规范 | L3（已标准化） | 10 次原子提交全部通过 | Pre-commit hooks 10/10 通过 |
| Spec 驱动文档质量保障 | L2（已验证） | spec.md + tasks.md + checklist.md 完整闭环 | 45/45 checklist 项通过 |

### 后续优化方向

1. **Windows 环境 commit message 工具链优化**：编写 PowerShell 兼容的多行 commit message 脚本，消除 heredoc 语法依赖。建议使用 `git commit -F <tempfile>` 方式，将 commit message 预写入临时文件后提交。

2. **Wiki 章节间导航链接自动生成**：当前章节间交叉引用为手动编写，可开发脚本自动生成"上一章/下一章"导航链接，减少人工维护成本。

3. **Sub-agent prompt 模板化**：将本次任务中用于并行 sub-agent 的 prompt 模板化，提取可复用部分（格式要求、写作风格、交叉引用格式），后续类似任务可直接复用。

4. **Checklist 自动验证脚本**：将 checklist.md 中的 45 个检查项部分自动化（如 frontmatter 格式检查、相对路径有效性检查、kebab-case 命名检查），减少人工验证工作量。

---

> **报告编制说明**：本报告基于 GitHub CLI Wiki 教程创建任务的全生命周期数据编制，遵循七概念方法论 R→I→E→Export 四阶段展开。所有事实陈述均有可验证的客观数据支撑，所有洞察均有"现象→根因→影响→建议"四元组结构，所有模式均可迁移至同类任务。报告采用 Markdown 格式，遵循 SpecWeave 原子化文档规范。
>
> **使用说明**：本报告作为知识沉淀的最终产出物，归档于产出物同级目录。后续类似任务（如其他 CLI 工具 Wiki 创建）应参考本报告中的模式 1（多源 Wiki 创建工作流）和模式 3（Spec 驱动文档质量保障），直接复用已验证的工作流。