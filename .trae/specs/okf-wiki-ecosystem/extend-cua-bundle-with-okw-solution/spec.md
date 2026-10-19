---
status: "draft"
version: "1.0"
source: "https://mp.weixin.qq.com/s/vEGTwWZ8Mws2fwAQyvm0Yg"
---

# Cua 知识束扩展 × cua+okw 最优解 Spec

## Why

`projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/cua/` 已存在一个 Cua 知识束（源为微信公众号「FinOps实战」文章《开源精选 | Cua》，URL `/s/6FaVJOhGomsSn43RdFMRlg`，2026-10-10 生成，已登记 F-001~F-065）。

现出现同项目的**第二篇独立文章**《别再让 Agent 用你的电脑了「Cua：2.8 万 Star 的开源项目」》（2026-10，URL `/s/vEGTwWZ8Mws2fwAQyvm0Yg`，下称"第二篇"）。它带来既有束未覆盖的新事实快照：六组件命名（含 Cua Spaces）、权限三档、Cua Bench 榜单 v1（KiCad 25 任务）、`cua sb`（gVisor）命令族、FSL/AGPL 许可分层、废弃包与 `cuabot` 安全警告、采用者名单与 Cua Fleets 定价。

同时，用户要求**结合 `apps/dev-tools/openkylin-wsl-devkit`（okw）给出「cua + okw 最优解」**：Cua 的命题是"给 Agent 一台属于它自己的电脑"；okw 提供可管理、可隔离、可复现的 openKylin（WSL）环境。两者组合是本仓独有的增量价值（既有束完全未涉及 okw）。

**去重结论**：同一项目只建一束，本次为**扩展现有束**，不新建重复束（经用户确认）。

## What Changes

- 新增**第二主信源**：把第二篇文章作为束的第二主信源，新增事实清单 `references/second-article-facts.md`（F-066 起连续编号，预计约 35–45 条）
- 新增**核验补充事实**：以 GitHub API 当前时点、官方 README/许可材料、cua.ai 命令、okw 文档核验第二篇的 P0 声明
- 新增概念章节 `concepts/06-cua-okw-solution.md`：**cua × okw 最优解**（标注为「合成设计 / synthesis」，未在本机实测）
- 在 `references/verification.md` 追加**第二轮核验**与**跨信源对账**（Fleets vs Spaces、SDK/CLI 命名、主语言、Stars 快照三版对照）
- 更新束内导航与台账：根 `index.md`、`concepts/index.md`、`references/index.md`、`log.md`；同步**文件计数**（12 → 14）
- **无计数变更**：不新增束、不新增分组 → `ai-agent/index.md`、`ai/index.md`、`jishu/index.md`、`bundles/index.md` 计数**保持不变**
- 仅在既有束内新增/修改文件，**不触碰** other bundles 或父级索引的计数

> 非 BREAKING：束路径、束身份、既有 F-001~F-065 事实与编号**一律不改**（只追加，不改写既有事实）。

## Impact

- **Affected specs（方法论 / 规范）**：OKF v0.2（frontmatter / 保留文件名 / toctree）；`blog-article-to-okf-wiki` 六工序工作流；seven-concepts-cmd 的 R→I→E→V 链路与 G1–G4 质量门
- **Affected code（实际改动面）**：仅 `projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/cua/` 目录内文件（属 git submodule `projects/awesome-okf-xs`，按 `projects/AGENTS.md` 允许子模块内开发；改动随子模块提交）
- **外部依赖（只读引用，不修改）**：`apps/dev-tools/openkylin-wsl-devkit/`（okw CLI 源码与 README）、`docs/tech/guides/openkylin-wsl-devkit/*`（8 篇指南）、`docs/knowledge/tech/openkylin-docs-wiki/`（okw 知识依据）

## 内容敏感度预检

源文为**无访问控制**的微信公众号公开文章（无 `share?code=`/`token=` 等访问控制参数）→ 判定为**公开内容（Public）**→ 标准工作流：规划位于 `.trae/specs/okf-wiki-ecosystem/`，知识包产出物落入 `projects/awesome-okf-xs/doc/bundles/`。

## 方法论编排

- **场景**：知识沉淀（既有知识包扩展）
- **链路**：`R → I → E → V`（结论类扩展，不加 F/A；C 为子模块内原子提交）
- **质量门**：
  - G1（R 产出）：事实无因果词、编号连续、类型（O/V/S）分层
  - G2（I 产出）：归属与骨架判定有依据，跨信源对账四元组完整（现象/差异/影响/处置）
  - G3（E 产出）：`concepts/06` 的"合成设计"边界清晰、可迁移判据齐备
  - G4（V 产出）：机械门禁（toctree/计数/UTF-8/链接）全通过 + 四视角对抗审查
- **已加载 Skill**：`seven-concepts-cmd`（元编排）；实现阶段按需加载 `blog-article-to-okf-wiki`

## 骨架与归属

- **归属**：既有束 `jishu/ai/frameworks/ai-agent/cua/`（**不新建束、不新建分组**）
- **骨架**：沿用既有 `index + concepts/ + references/ + log`，**无 `examples/`**——“操作可复现性两问”Q2 为否（第二篇的操作命令转述自官方且本机未实测；合成章节亦未实测）
- **新增文件**：`concepts/06-cua-okw-solution.md`、`references/second-article-facts.md`
- **修改文件**：`index.md`、`concepts/index.md`、`references/index.md`、`references/verification.md`、`log.md`（`references/article-source.md` 仅补一行指向第二信源，不改其既有事实体）
- **okw 依赖**：组合章节的事实基础取自 `apps/dev-tools/openkylin-wsl-devkit/README.md` 与 `docs/tech/guides/openkylin-wsl-devkit/{index,02,03,05,08}.md`（交叉引用，不复制正文）

## 事实登记摘要（预计）

- **F-066~F-0NN（第二篇事实）**：文章元信息；六组件（Driver/Spaces/Lume/SDK&CLI/CUA-S1/Bench）；权限三档（standard/bounded/unrestricted）；Cua Bench 榜单 v1 与 KiCad 任务；`cua sb`（gVisor）命令族；许可三档（MIT / FSL-1.1-MIT / cua-perception AGPL-3.0-only）；废弃包与 `cuabot` 安全警告；四类"何时不需要"；采用者（Hermes/Clicky/H Company/Factory Droid）；Cua Fleets 定价
- **核验补充事实**：GitHub API 当前时点（stars/forks/issues/language/contributors）；官方 README 许可分层引语；`cua sb`/`lume`/driver 安装命令
- **跨信源对账**：Fleets（第一篇）↔ Spaces/sandbox（第二篇）命名；"Sandbox SDK"↔"Cua SDK 与 CLI"；主语言 HTML/Rust；Stars 三版快照（24,432 / 29,189 / 2.8 万） → 全部入 `references/verification.md`

## ADDED Requirements

### Requirement: 第二主信源事实登记

知识束 SHALL 以第二篇文章为第二主信源，新增事实清单文件，事实编号从 F-066 起**连续**，逐条标注类型（`O`=客观事实 / `V`=作者观点 / `S`=厂商自述）与来源。

#### Scenario: 事实登记完整且可追溯
- **WHEN** 读者查阅第二篇文章的事实
- **THEN** `references/second-article-facts.md` 存在，含连续 F 编号（F-066 起）、类型列与来源列，且与束内既有 F-001~F-065 **无编号冲突、无重复**

#### Scenario: 既有事实不被改写
- **WHEN** 校验 F-001~F-065 的原文与编号
- **THEN** `references/article-source.md`、`verification.md` 中既有事实体逐字保持（仅允许追加新段落）

### Requirement: cua × okw 最优解章节

知识束 SHALL 提供一章 `concepts/06-cua-okw-solution.md`，结合 Cua 与 okw 给出组合最优解，内容 SHALL 覆盖：分层架构分工、模块选型判据、组合路径、前置条件与风险清单。

#### Scenario: 合成边界清晰（防伪结论）
- **WHEN** 读者阅读该章节
- **THEN** 章节顶部显式标注**「合成设计（synthesis）· 未在本机实测」**，所有非源文/非官方的事实标注为设计推断；不得出现"已实测可用""验证通过"等未经证据支持的表述

#### Scenario: 事实有据（OKF 溯源）
- **WHEN** 章节引用 Cua 或 okw 的具体命令/端口/行为
- **THEN** 相应陈述带 F 编号（Cua 侧）或指向 okw 指南/`okw` 源码（okw 侧）的交叉引用

### Requirement: 跨信源对账

核验报告 SHALL 追加**跨信源对账**段落，对同一实体在两大信源间的命名/数值差异给出"现象—差异—影响—处置"四元组。

#### Scenario: 差异显式呈现
- **WHEN** 第一篇与第二篇对同一模块/数值给出不同口径（如 Fleets vs Spaces、HTML vs Rust、Stars 三版快照）
- **THEN** `references/verification.md` 逐条列出差异并给出处置，正文呈现时携带时点标注

## MODIFIED Requirements

### Requirement: 束内导航与信源台账（既有）

束根 `index.md`、`concepts/index.md`、`references/index.md` 的导航表与 `{toctree}`，以及 `index.md` 的"文件计数"与"已知边界"段落，SHALL 收录新增章节与第二信源，使其可从束根经 toctree 到达。

**变更点**：
- `concepts/index.md`：学习路径与 toctree 追加 `06-cua-okw-solution`
- `references/index.md`：信源清单与事实编号索引追加第二信源（F-066+）
- 根 `index.md`：目录树、分层导航、信源说明、文件计数（"合计 12 个文件" → "合计 14 个文件"）、`sources`/`generated`/`verified` 元数据更新
- `log.md`：追加第二轮的 R→I→E→V 记录与 G1–G4 结论

#### Scenario: toctree 与文件一致
- **WHEN** 运行 `invoke gates.toctrees`
- **THEN** 束内三级 toctree 无断链、无孤立文档，`index.md` 声明的文件计数与实际文件数一致

#### Scenario: 计数不变
- **WHEN** 运行 `invoke gates.bundles`
- **THEN** `bundles/index.md` 与各父级分组索引的束/组/域计数**与改动前一致**（本次不新增束）

## REMOVED Requirements

无。
