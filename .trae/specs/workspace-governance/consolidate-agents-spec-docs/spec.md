---
title: ".agents 规范文档复盘洞察与合并去冗余"
status: "draft"
---

# .agents 规范文档复盘洞察与合并去冗余 Spec

## 方法论声明

本规范基于 **R-I-E-C-A-F-V 七概念方法论** 的「场景3：重构优化」链路 **I→F→A→C** 编写（session=`sc-20260901-agents-spec-consolidation`，depth=standard）：

| 概念 | 阶段 | 在本规范中的体现 |
|------|------|-----------------|
| R（Retrospective 复盘） | 事实采集 | §2 现状事实清单（已采集，纯客观描述） |
| I（Insight 洞察） | 根因分析 | §3 洞察四元组（现象+根因+影响+建议） |
| F（First Principles 第一性原理） | 理想设计 | §4 合并策略总纲 |
| A（Atomization 原子化） | 拆分方案 | tasks.md 的 7 个原子任务 |
| C（Atomic Commit 原子提交） | 交付实施 | tasks.md 有序实施；提交须用户另行授权 |
| V（Adversarial Review 对抗审查） | 验证加固 | §5 对抗审查 + Task 7 独立审查 |

> 质量门：G1（事实无因果词，§2 已满足）、G2（洞察四元组，§3 已满足）、G4（行动项原子化，tasks.md）内嵌于本规范。
> 范围声明（用户已确认）：**仅规范文档层**（.md 规范资产），不含脚本代码、缓存与构建产物；复盘与洞察产出**内嵌于本 spec**，不另建报告文件。

---

## 1. Why

`.agents/` 经多轮原子化拆分（"单文件 → 单文件壳 + 子目录分册"模式）后，规范文档层出现三类冗余：壳文件与分册内容重复、壳文件结构不统一（含一处 frontmatter 重复缺陷）、模板目录混入一次性交付物。冗余导致修改需多处同步、索引与实际结构脱节风险上升。本次任务完成全面复盘与洞察，并执行证据充分的合并去冗余动作。

## 2. 现状事实清单（R 阶段产出，G1：无因果推断词）

### 2.1 总量

- `.agents/` 共 1595 个文件：647 `.py`、492 `.md`、310 未追踪 `.pyc`、65 `.ps1`、25 `.sh`。
- 按目录：`scripts/` 1046、`rules/` 135、`templates/` 124、`skills/` 111、`teams/` 24、`protocols/` 18、`checklists/` 18、`prompts/` 15、`worlds/` 13、`roles/` 12、`workflows/` 10、`modules/` 9、`vendor-integration/` 7、`brand/` 6、`tools/` 5、`capabilities/` 4、`capability-registry/` 4、`cases/` 2、`commands/` 16、`config/` 2、`systems/` 2。
- git 追踪文件 1272 个；310 个 `.pyc` 均未追踪（不在本次范围）。

### 2.2 rules/ 的 9 对「单文件壳 + 子目录分册」并存

| 壳文件（行数） | 子目录（文件数） |
|---|---|
| alternatives-guide.md（45） | alternatives-guide/（10） |
| cmd-log-specification.md（20） | cmd-log-specification/（5） |
| detection-and-reporting.md（19） | detection-and-reporting/（7） |
| frontmatter-metadata-standard.md（19） | frontmatter-metadata-standard/（5） |
| identification-standards.md（19） | identification-standards/（7） |
| spec-version-control.md（27） | spec-version-control/（6） |
| spec-writing-guide.md（29） | spec-writing-guide/（9） |
| stage-guardrails.md（22） | stage-guardrails/（5） |
| stage-guardrails-guide.md（28） | stage-guardrails-guide/（6） |

- `data-security/` 无同名壳文件，仅目录内 README.md 承担索引——与上述 9 对模式不一致。
- 壳文件行数均在 19-45 行区间；其中 `alternatives-guide.md`（45 行）除导航表外另含 9 行类型映射表正文。
- `stage-guardrails-guide.md` 第 1-15 行（frontmatter + 标题）与第 9-15 行区域存在**整块重复**（同一 frontmatter 块出现两次）。

### 2.3 templates/ 构成

- 11 个模板子目录 + 41 个根级单文件模板。
- 复盘类模板共 4 处：`comprehensive-retrospective-template/`（9 文件）、`task-retrospective-template/`（4 文件）、`weekly-retrospective-template.md`（72 行）、`engineering-debug-retrospective-template.md`（136 行）。`task-retrospective-template/README.md` 第 26-41 行已含三者适用场景对比表。
- 疑似一次性交付物（非可复用模板）候选：`new-user-first-quota-onboarding.md`（435 行）、`dual-track-weekly-calendar-template.md`（150 行）、`legacy-system-ai-upgrade-kickoff-template.md`（275 行）。
- `templates/README.md`（68 行）为索引，未声明"模板 vs 交付物"准入标准。

### 2.4 主题分散

- 权限主题分布在 `teams/permission-system.md` 与 `worlds/collaboration/permissions.md`；后者第 7-10 行自述"基于 teams/permission-system.md 的 RBAC 模型扩展"。
- `brand/` 含 6 个 logo/HTML 资产（daocollective-logo-legacy.svg、xuantong-logo 系列等），非规范文档。

### 2.5 索引层

- 三层索引：`AGENTS.md`（根）→ `capability-registry.md` + `capability-registry/`（4 分册）→ 各目录 README。
- `rules/README.md`（182 行）列出 rules/ 全部条目；`commands/README.md`（134 行）列出 16 个命令。
- `modules/` 8 个 `self-*.md` 各 47-67 行，结构同构（README.md 66 行承担索引）。

## 3. 洞察（I 阶段产出，G2：四元组完整）

### 洞察 1：壳文件模式已建立但未收敛统一

- **现象**：9 对壳+分册并存，壳文件详略不一（19-45 行），`alternatives-guide.md` 壳内保留映射表正文，`stage-guardrails-guide.md` 存在 frontmatter 整块重复；`data-security/` 无壳。
- **根因**：原子化拆分分批执行，各批次对"壳文件应保留什么"无统一标准，拆分后未做壳文件归一化收尾。
- **影响**：壳与分册内容双写，修改需同步两处；重复 frontmatter 属格式缺陷，可能被元数据工具误解析。
- **建议**：定义壳文件统一模板（frontmatter + 一句话定位 + 导航表，三者之外无正文），9 个壳按模板归一，修复重复块。

### 洞察 2：模板目录缺少准入边界

- **现象**：`templates/` 41 个单文件中混入一次性交付物候选（435 行的配额上手文档、双轨周历等），复盘类模板有 4 处入口。
- **根因**：模板目录历史上兼作"交付物存放点"，无准入标准区分可复用模板与一次性产物。
- **影响**：使用者难以判断哪些是可直接套用的模板；索引膨胀。
- **建议**：建立归档区 `templates/archive/` 收纳一次性交付物，`templates/README.md` 补充准入标准；复盘模板家族保留既有边界（README 已文档化），仅做指针互链。

### 洞察 3：权限主题双写

- **现象**：`worlds/collaboration/permissions.md` 与 `teams/permission-system.md` 在 RBAC 模型描述上存在内容重叠，前者自述为后者的扩展。
- **根因**：worlds/ 体系后建时复制了 teams/ 的模型描述，未以引用替代。
- **影响**：权限模型修改需同步两处，存在口径漂移风险。
- **建议**：`worlds/collaboration/permissions.md` 中与 `teams/permission-system.md` 重复的模型定义段落替换为引用指针，仅保留"扩展差异"部分。

### 洞察 4：非规范资产寄居

- **现象**：`brand/` 6 个视觉资产位于规范容器内。
- **根因**：早期无品牌资产落位规则。
- **影响**：`.agents/` 职责边界（面向智能体的规范与执行资产）被稀释。
- **建议**：本次仅登记不迁移（迁移目的地涉及 docs/ 或 apps/ 的板块决策，超出本次范围），列入开放问题。

## 4. 合并策略总纲（F 阶段第一性原理设计）

**根本原则**：
1. **壳文件唯一职责是导航**——壳内不保留任何与分册重复的正文；导航表必须与分册实际文件一一对应。
2. **重复内容以引用指针替代双写**——保留单一事实源（SSOT），扩展文档只写差异。
3. **一次性产物与可复用模板物理隔离**——归档而非删除，保留历史可追溯。
4. **索引与结构同步**——任何合并动作后，`rules/README.md`、`capability-registry`、`AGENTS.md` 的对应条目必须同步核验。
5. **不重写正文语义**——仅做去重、引用替换、归档迁移与格式修复，不改动规则/模板的实质内容。

### 4.1 动作清单

| 序号 | 动作 | 对象 | 方式 |
|------|------|------|------|
| M1 | 壳文件归一化 | §2.2 的 9 个壳文件 | 按统一模板重写：frontmatter + 一句话定位 + 导航表；移除与分册重复的正文（alternatives-guide.md 的映射表若分册已有则移除，否则保留于壳并注明唯一性） |
| M2 | 格式缺陷修复 | stage-guardrails-guide.md | 删除重复的 frontmatter+标题块 |
| M3 | 权限主题收敛 | worlds/collaboration/permissions.md | 与 teams/permission-system.md 重复段落替换为引用指针 |
| M4 | 模板归档 | §2.3 候选清单（以 Task 1 审计确认者为准） | 迁移至 `templates/archive/`，更新 templates/README.md 索引与准入标准 |
| M5 | 复盘模板互链 | 4 处复盘模板入口 | 在各入口补充指向 task-retrospective-template/README.md 对比表的指针，不合并文件 |
| M6 | 索引同步 | rules/README.md、capability-registry/、AGENTS.md、context-routing.md | 核验并更新受 M1-M5 影响的条目 |

### 4.2 明确不做（Non-Goals）

- 不合并 `modules/` 8 个 self-*.md（结构同构但证据不足以判定内容重复，列入开放问题）。
- 不迁移 `brand/`（仅登记）。
- 不动 `scripts/`、`skills/` 的 SKILL.md、`.pyc`、缓存文件。
- 不修改 `commands/` 命令文档正文（仅索引核验）。
- 不执行 git commit（用户未授权）。

## 5. 对抗审查记录（V 阶段）

### 视角 1：维护者视角（壳归一化是否破坏既有引用？）

- **攻击点**：壳文件被 AGENTS.md、capability-registry、context-routing 大量引用，重写壳内容是否引入断链？
- **回应**：壳文件路径与文件名不变，仅内部内容归一；导航表链接逐一核验分册实际存在。Task 6 以 check-links 全仓验证。

### 视角 2：新人视角（归档是否造成内容丢失错觉？）

- **攻击点**：模板移入 archive/ 后，使用者可能误以为被删除。
- **回应**：归档而非删除；`templates/README.md` 保留归档清单与准入标准说明，归档文件仍可通过相对路径访问。

### 视角 3：范围蔓延视角（是否应顺带处理 scripts/ 冗余？）

- **攻击点**：scripts/ 占 1046 文件，冗余可能更严重，为何不处理？
- **回应**：用户已明确选择"仅规范文档"范围；脚本清理需独立的测试回归保障，属另一任务。本 spec §2.1 已登记该事实供后续决策。

### 视角 4：未来扩展视角（壳模板是否适应后续拆分？）

- **攻击点**：统一壳模板后，未来新的拆分会不会再次偏离？
- **回应**：壳模板标准写入 `rules/README.md`（或对应元规范位置），后续拆分遵循同一标准；data-security/ 无壳的既有模式以 README 索引为准，两种模式均被承认，不强制改造。

## Impact

- **受影响规范**：`.agents/rules/`（9 壳 + 1 缺陷）、`.agents/worlds/collaboration/permissions.md`、`.agents/teams/permission-system.md`（引用方向不变）、`.agents/templates/`（README + 归档）、`rules/README.md`、`capability-registry.md` 及分册、根 `AGENTS.md`、`context-routing.md`。
- **受影响代码**：无（纯文档治理）。
- **不受影响**：`projects/`、`vendor/` 子模块；`docs/` 文档中心；脚本行为。

## ADDED Requirements

### Requirement: 壳文件统一模板

系统 SHALL 保证 rules/ 下每个「单文件壳 + 子目录分册」对的壳文件仅包含 frontmatter、一句话定位说明与导航表三部分，导航表条目与子目录实际文件一一对应。

#### Scenario: 壳文件内容核验
- **WHEN** 审查任一壳文件（如 stage-guardrails.md）
- **THEN** 文件中不存在与分册重复的正文段落，导航链接全部可达

### Requirement: 模板准入标准

系统 SHALL 在 `templates/README.md` 中声明模板准入标准（可复用性判定），并为一次性交付物提供 `templates/archive/` 归档区。

#### Scenario: 新增模板判定
- **WHEN** 新增一个文档到 templates/
- **THEN** 可依据 README 准入标准判定其应放入根级/子目录还是 archive/

## MODIFIED Requirements

### Requirement: 权限模型单一事实源

`teams/permission-system.md` 为 RBAC 权限模型的唯一定义源；`worlds/collaboration/permissions.md` 仅描述工作区场景的扩展差异，模型定义以引用指针指向前者。

## REMOVED Requirements

### Requirement: 壳文件内的正文双写

**Reason**: 壳文件与分册内容双写违反 SSOT 原则，修改需同步两处。
**Migration**: 壳内重复正文移除，以导航表条目替代；唯一性正文（分册未覆盖者）保留并注明。

### Requirement: 一次性交付物存放于 templates/ 根级

**Reason**: 一次性交付物与可复用模板混放，稀释模板目录职责。
**Migration**: 迁移至 `templates/archive/`，README 登记归档清单。

## 待批准决策

- **D1**：M4 归档候选以 Task 1 审计确认为准（当前候选：new-user-first-quota-onboarding.md、dual-track-weekly-calendar-template.md、legacy-system-ai-upgrade-kickoff-template.md）。**建议批准**。
- **D2**：modules/ 与 brand/ 本次仅登记不处理。**建议批准**。
- **D3**：data-security/ 无壳模式保留现状，不强制补壳。**建议批准**。

## 开放问题

- [ ] modules/ 8 个 self-*.md 是否存在可合并的内容重叠（需专项审计，本次不做）。
- [ ] brand/ 资产的最终落位（docs/ 或 apps/，另行决策）。
- [ ] scripts/ 1046 文件的冗余盘点（独立任务，本次范围外）。
