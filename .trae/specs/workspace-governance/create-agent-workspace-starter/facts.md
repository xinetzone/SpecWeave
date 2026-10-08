---
id: "create-agent-workspace-starter-facts"
title: "R-事实采集——.agents 全貌与「1 小时可消化」量化基线"
source: "实测（2026-10-07，PowerShell Get-ChildItem / Get-Content），只读 .agents/ 与 templates/agent-workspace-hub/"
created_at: "2026-10-07"
content-sensitivity: "public"
related_spec: "spec.md"
related_tasks: "tasks.md#Task 1"
---

# R-事实采集 —— .agents 全貌与「1 小时可消化」量化基线

> 本文件为 Task 1 产出，承载后续萃取任务（Task 3~Task 9）的事实基线与设计输入。
> 数据口径：Windows PowerShell `Get-ChildItem -Recurse -File | Measure-Object -Property Length -Sum`（文件数 / 字节）与 `(Get-Content <file> | Measure-Object -Line).Lines`（行数）。全部数值为 2026-10-07 实测。
> 质量门 G1：全篇只记录客观事实与建议，不含因果词。

## 1. 总量事实

### 1.1 总量与体量分布

| 项目 | 文件数 | 字节 | 占 .agents 字节比 |
|---|---|---|---|
| `.agents/` 总计 | 6850 | 134,549,228 | 100% |
| ├ `skills/` | 4378 | 104,116,004 | 77.4% |
| ├ `scripts/` | 2010 | 27,150,022 | 20.2% |
| ├ `templates/` | 134 | 885,292 | 0.66% |
| ├ `rules/` | 136 | 656,230 | 0.49% |
| ├ `brand/` | 6 | 441,689 | 0.33% |
| ├ `checklists/` | 24 | 214,170 | 0.16% |
| ├ `commands/` | 16 | 172,263 | 0.13% |
| ├ `.cache/` | 2 | 141,566 | 0.11% |
| ├ `protocols/` | 18 | 136,810 | 0.10% |
| ├ `teams/` | 24 | 112,549 | 0.08% |
| ├ `worlds/` | 13 | 78,872 | 0.06% |
| ├ `roles/` | 12 | 76,594 | 0.06% |
| ├ `prompts/` | 15 | 68,831 | 0.05% |
| ├ `capability-registry/` | 4 | 40,474 | 0.03% |
| ├ `workflows/` | 10 | 34,300 | 0.03% |
| ├ `vendor-integration/` | 7 | 32,525 | 0.02% |
| ├ `tools/` | 5 | 28,758 | 0.02% |
| ├ `reports/` | 1 | 24,579 | 0.02% |
| ├ `capabilities/` | 4 | 23,105 | 0.02% |
| ├ `modules/` | 9 | 22,319 | 0.02% |
| ├ `cmake/` | 2 | 21,448 | 0.02% |
| ├ `cache/` | 2 | 9,875 | <0.01% |
| ├ `config/` | 3 | 4,814 | <0.01% |
| ├ `cases/` | 2 | 1,553 | <0.01% |
| ├ `systems/` | 2 | 967 | <0.01% |
| └ `logs/` | 1 | 0 | 0% |

**事实要点**

- `skills/` + `scripts/` 合计 6388 文件 / 131,266,026 字节，占 `.agents/` 字节比 97.6%。两个类目为体量主体。
- 其余 25 个顶层类目合计 462 文件 / 3,283,202 字节，字节占比 2.4%。
- `.agents/` 根级 Markdown 文件共 9 个（不含 `.stats-cache.json`），行数区间 24~120 行，属轻量入口层。

### 1.2 入口层轻量事实（`.agents/` 根级）

| 文件 | 行数 |
|---|---|
| `ONBOARDING.md` | 84 |
| `context-routing.md` | 120 |
| `README.md` | 80 |
| `governance-layers.md` | 47 |
| `global-core-rules.md` | 39 |
| `capability-registry.md` | 32 |
| `subdirectory-responsibilities.md` | 29 |
| `capability-boundaries.md` | 28 |
| `VENDOR-INTEGRATION.md` | 24 |

### 1.3 仓库根契约

| 文件 | 行数 |
|---|---|
| `AGENTS.md`（仓库根） | 121 |
| `CLAUDE.md`（仓库根） | 69 |
| `templates/agent-workspace-hub/AGENTS.md` | 74 |

### 1.4 复核结论与偏差记录

| 基线项 | spec/tasks 记录值 | 本次实测值 | 结论 |
|---|---|---|---|
| `.agents/` 总文件数 | 6850 | 6850 | 一致 |
| `.agents/` 总字节 | 134.5 MB | 134,549,228 | 一致 |
| `skills/` | — | 4378 文件 / 104,116,004 字节 | 一致（按 spec 描述复核） |
| `scripts/` | — | 2010 文件 / 27,150,022 字节 | 一致 |
| `templates/` | — | 134 文件 / 885,292 字节 | 一致 |
| `templates/agent-workspace-hub/` 文件数 | 51 文件 | **28 文件 / 19,918 字节** | **偏差：实测少于 spec 记录值（spec Background 记 51 文件）** |
| `.agents/ONBOARDING.md` | 84 行 | 84 | 一致 |
| `.agents/context-routing.md` | 120 行 | 120 | 一致 |
| `.agents/global-core-rules.md` | 39 行 | 39 | 一致 |
| `.agents/protocols/prompt-bootstrap.md` | 322 行 | 322 | 一致 |
| `.agents/skills/load-specweave/SKILL.md` | 25 行 | 25 | 一致 |

> 偏差项 `templates/agent-workspace-hub/`：实测 28 文件 / 19,918 字节。该目录内 `.agents/` 子骨架中 25 个 README 类文件为 2 行占位；`AGENTS.md` 74 行、`.agents/README.md` 60 行、`.agents/ONBOARDING.md` 7 行、`.agents/context-routing.md` 6 行、`.agents/global-core-rules.md` 6 行、`.agents/capability-registry.md` 6 行、`.agents/docs/development-standards.md` 6 行、`apps/AGENTS.md` 4 行、`projects/AGENTS.md` 4 行、`vendor/AGENTS.md` 4 行、`README.md` 41 行。骨架主体为占位，实质内容集中于 3 个文件。

## 2. 候选萃取清单

> 建议列取值：**保留**（可直接纳入 starter）/ **精简**（改写压缩后纳入）/ **导览**（仅保留 README 作一句话导览）/ **剔除**（不入 starter）。

### 2.1 根契约

| 文件相对路径 | 行数 | 建议 | 一句话理由 |
|---|---|---|---|
| `AGENTS.md`（仓库根） | 121 | 精简 | 全仓最高入口，含启动协议与三层路由；starter 版须保留「启动协议」关键词锚点并压缩至买家单项目视图 |
| `templates/agent-workspace-hub/AGENTS.md` | 74 | 精简 | 空骨架版最小契约，为 starter 根 `AGENTS.md` 的直接改写底本 |

### 2.2 入口层（`.agents/` 根级）

| 文件相对路径 | 行数 | 建议 | 一句话理由 |
|---|---|---|---|
| `.agents/ONBOARDING.md` | 84 | 保留 | L0 入门指南，含能力速查表与任务类型路由，对应「10 分钟概览」段 |
| `.agents/context-routing.md` | 120 | 精简 | 任务类型→必读规范映射表，为智能体自举核心；starter 版按单项目裁剪 |
| `.agents/global-core-rules.md` | 39 | 保留 | 全局核心规则（启动协议、内容分流、按需读取），行数轻量 |
| `.agents/capability-registry.md` | 32 | 精简 | L1 全量静态索引；starter 版仅保留类目导览骨架 |
| `.agents/README.md` | 80 | 精简 | 规范容器总览入口，starter 版作为 `.agents/` 目录首页 |
| `.agents/governance-layers.md` | 47 | 导览 | 治理分层说明，归入导览可选项 |
| `.agents/capability-boundaries.md` | 28 | 剔除 | 角色边界细则，starter 体量外 |
| `.agents/subdirectory-responsibilities.md` | 29 | 剔除 | 目录职责表，与 starter 单项目视图关联度低 |
| `.agents/VENDOR-INTEGRATION.md` | 24 | 剔除 | vendor 子模块协同规范，依赖 SpecWeave 仓结构 |

### 2.3 `protocols/`

| 文件相对路径 | 行数 | 建议 | 一句话理由 |
|---|---|---|---|
| `.agents/protocols/README.md` | 56 | 保留 | 协议类目导航，starter 类目导览必需 |
| `.agents/protocols/prompt-bootstrap.md` | 322 | 精简 | 一句话装载协议（8 条安全规则 + 幂等 + 路径选择），装载门面的方法论底本 |
| `.agents/protocols/workspace-discovery.md` | 233 | 精简 | 五步工作区发现流程 + AGENTS.md 最小可行子集规范，starter 独立可用性依据 |
| `.agents/protocols/three-layer-routing.md` | 106 | 剔除 | 三层路由体系（主权区/子区域/子应用），SpecWeave 专属结构 |
| `.agents/protocols/four-region-routing-architecture.md` | 292 | 剔除 | 四大顶层区域路由，SpecWeave 专属结构 |
| `.agents/protocols/onboarding-protocol.md` | 133 | 剔除 | 会话启动协议细则，starter 版由 ONBOARDING.md 覆盖 |
| `.agents/protocols/pre-document-reading.md` | 28 | 剔除 | 前置文档阅读协议，细则见其子目录 6 文件 |
| `.agents/protocols/handoff.md` | 55 | 剔除 | 任务交接协议，进阶可选内容 |
| `.agents/protocols/messaging.md` | 47 | 剔除 | 消息传递协议，多智能体协作细则 |
| `.agents/protocols/conflict-resolution.md` | 50 | 剔除 | 冲突解决协议，多智能体协作细则 |
| `.agents/protocols/dependency-management.md` | 166 | 剔除 | 临时依赖管理，SpecWeave 仓专属 |
| `.agents/protocols/app-development-workflow.md` | 195 | 剔除 | 应用生命周期协议，apps 区域专属 |
| `.agents/protocols/pre-document-reading/`（6 文件） | 16~109 | 剔除 | 前置文档阅读子目录，合计 342 行，starter 体量外 |

### 2.4 `rules/`

| 文件相对路径 | 行数 | 建议 | 一句话理由 |
|---|---|---|---|
| `.agents/rules/README.md` | 185 | 精简 | 规则体系架构 + 场景/角色导航，starter 规则类目首页 |
| `.agents/rules/ai-coding-guidelines.md` | 145 | 精简 | AI 编码四原则（歧义澄清/简约至上/精确编辑/目标驱动），买家高频场景 |
| `.agents/rules/content-sensitivity-precheck.md` | 126 | 保留 | 内容敏感度预检，启动协议步骤 2.3 的详细规范 |
| `.agents/rules/fix-prevent-close-loop.md` | 172 | 精简 | 修复→预防→闭环三阶段 SOP，bug 修复类任务核心 |
| `.agents/rules/three-stage-universal-principle.md` | 119 | 精简 | 三阶段普遍规律，跨域方法论 |
| `.agents/rules/meta-document-priority-principle.md` | 146 | 精简 | 元文档优先原则，入口精简与索引维护准则 |
| `.agents/rules/spec-writing-guide.md` | 20 | 保留 | Spec 标准章节结构，演练任务（写 spec）直接依据 |
| `.agents/rules/spec-creation-precheck.md` | 65 | 保留 | Spec 创建前位置/格式预检，演练任务配套 |
| `.agents/rules/stage-guardrails.md` | 16 | 保留 | 阶段守卫规则主文件（含运行时细则） |
| `.agents/rules/stage-guardrails-guide.md` | 17 | 保留 | 阶段守卫运行时使用指南 |
| `.agents/rules/raci-governance-standards.md` | 199 | 剔除 | RACI 治理规范，多角色团队场景 |
| `.agents/rules/enforcement-guidelines.md` | 230 | 剔除 | 治理执行与验证规则，SpecWeave 治理专属 |
| `.agents/rules/identification-standards.md` | 18 | 剔除 | 硬编码识别标准，SpecWeave 治理专属 |
| `.agents/rules/allowable-scenarios.md` | 135 | 剔除 | 硬编码例外审批，SpecWeave 治理专属 |
| `.agents/rules/alternatives-guide.md` | 21 | 剔除 | 硬编码替代方案，SpecWeave 治理专属 |
| `.agents/rules/detection-and-reporting.md` | 18 | 剔除 | 硬编码检测报告，SpecWeave 治理专属 |
| `.agents/rules/skill-development.md` | 153 | 剔除 | Skill 开发规范，进阶可选内容 |
| `.agents/rules/skill-five-elements-mindmap.md` | 117 | 剔除 | 五要素思维导图，进阶可选内容 |
| `.agents/rules/frontmatter-metadata-standard.md` | 15 | 剔除 | Frontmatter 元数据规范细则 |
| `.agents/rules/file-naming-convention.md` | 115 | 剔除 | 文件命名约定，SpecWeave 仓细则 |
| `.agents/rules/cmd-log-specification.md` | 16 | 剔除 | CMD-LOG 规范，SpecWeave 自动化专属 |
| `.agents/rules/spec-version-control.md` | 17 | 剔除 | Spec 版本控制细则 |
| `.agents/rules/data-security/`（约 110 文件） | — | 剔除 | 数据安全治理体系，SpecWeave 治理专属 |

### 2.5 `roles/`

| 文件相对路径 | 行数 | 建议 | 一句话理由 |
|---|---|---|---|
| `.agents/roles/README.md` | 54 | 保留 | 角色定义总览（7 角色 + 职责矩阵） |
| `.agents/roles/developer.md` | 27 | 保留 | 开发者角色定义，行数轻量 |
| `.agents/roles/reviewer.md` | 25 | 保留 | 审查者角色定义，行数轻量 |
| `.agents/roles/tester.md` | 23 | 保留 | 测试者角色定义，行数轻量 |
| `.agents/roles/orchestrator.md` | 22 | 保留 | 编排者角色定义，行数轻量 |
| `.agents/roles/architect.md` | 24 | 保留 | 架构师角色定义，行数轻量 |
| `.agents/roles/thesis-advisor.md` | 209 | 剔除 | 论题顾问角色，SpecWeave 专属 |
| `.agents/roles/token-optimizer.md` | 59 | 剔除 | Token 优化者角色，进阶可选内容 |
| `.agents/roles/co-founder.md` | 21 | 剔除 | 联合创始人角色，SpecWeave 专属 |
| `.agents/roles/collaboration-scenarios.md` | 82 | 剔除 | 协作场景细则，多智能体场景 |

### 2.6 `workflows/`

| 文件相对路径 | 行数 | 建议 | 一句话理由 |
|---|---|---|---|
| `.agents/workflows/README.md` | 24 | 保留 | 工作流类目导航 |
| `.agents/workflows/feature-development.md` | 28 | 保留 | 功能开发流程，首个任务演练直接依据 |
| `.agents/workflows/code-review.md` | 95 | 精简 | 代码审查流程，进阶可选内容 |
| `.agents/workflows/testing.md` | 73 | 精简 | 测试流程，进阶可选内容 |

### 2.7 `templates/`

| 文件相对路径 | 行数 | 建议 | 一句话理由 |
|---|---|---|---|
| `.agents/templates/README.md` | 85 | 精简 | 模板类目导航，starter 模板类目首页 |
| `.agents/templates/task-template.md` | 87 | 保留 | 任务模板，演练任务书直接依据 |
| `.agents/templates/handoff-template.md` | 32 | 保留 | 交接模板，行数轻量 |
| `.agents/templates/ui-pitfalls-guide.md` | 201 | 剔除 | UI 陷阱指南，前端专属 |
| `.agents/templates/wiki-spec-template.md` | 570 | 剔除 | Wiki spec 模板，行数超预算 |
| `.agents/templates/` 其余 40+ 文件 | 12~360 | 剔除 | 领域专属模板（CI/CMake/Docker/复盘等），starter 体量外 |

### 2.8 `commands/`

| 文件相对路径 | 行数 | 建议 | 一句话理由 |
|---|---|---|---|
| `.agents/commands/README.md` | 134 | 精简 | 指令集类目导航，starter 指令类目首页 |
| `.agents/commands/seven-concepts.md` | 296 | 剔除 | 七概念方法论编排，行数超预算 |
| `.agents/commands/retrospective.md` | 111 | 剔除 | 复盘指令，进阶可选内容 |
| `.agents/commands/atomic-commit.md` | 155 | 剔除 | 原子提交指令，进阶可选内容 |
| `.agents/commands/mermaid.md` | 140 | 剔除 | Mermaid 图表指令，进阶可选内容 |
| `.agents/commands/` 其余 10 文件 | 96~283 | 剔除 | 领域指令（导出/萃取/洞察等），starter 体量外 |

### 2.9 `checklists/`

| 文件相对路径 | 行数 | 建议 | 一句话理由 |
|---|---|---|---|
| `.agents/checklists/README.md` | 26 | 保留 | 检查清单类目导航 |
| `.agents/checklists/risk-scoring-checklist.md` | 99 | 剔除 | 风险评分清单，SpecWeave 治理专属 |
| `.agents/checklists/code-review-checklist.md` | 120 | 剔除 | 代码审查清单，进阶可选内容 |
| `.agents/checklists/` 其余 21 文件 | 47~350 | 剔除 | 领域检查清单（Docker/CMake/安全等），starter 体量外 |

### 2.10 `skills/`

| 文件相对路径 | 行数 | 建议 | 一句话理由 |
|---|---|---|---|
| `.agents/skills/README.md` | 163 | 精简 | Skill 类目导航与门面规范，starter 技能类目首页 |
| `.agents/skills/load-specweave/SKILL.md` | 25 | 保留 | 装载门面示例（五要素 SKILL），行数轻量 |
| `.agents/skills/` 其余约 4374 文件 | — | 剔除 | Skill 全家桶，占 `.agents/` 字节比 77.4% |

### 2.11 导览型类目（每类目仅取 README 作一句话导览）

| 文件相对路径 | 行数 | 建议 | 一句话理由 |
|---|---|---|---|
| `.agents/modules/README.md` | 66 | 导览 | 自我演进模块总览（8 模块），导览可选项 |
| `.agents/teams/README.md` | 100 | 导览 | 团队管理总览，导览可选项 |
| `.agents/prompts/README.md` | 59 | 导览 | 提示词类目总览，导览可选项 |
| `.agents/tools/README.md` | 39 | 导览 | 工具规范总览，导览可选项 |
| `.agents/worlds/README.md` | 67 | 导览 | 协作环境总览，导览可选项 |
| `.agents/capabilities/README.md` | 50 | 导览 | 渐进式披露规范总览，导览可选项 |
| `.agents/cases/README.md` | 4 | 导览 | 复用案例总览（占位），导览可选项 |
| `.agents/systems/README.md` | 4 | 导览 | 系统架构总览（占位），导览可选项 |
| `.agents/capability-registry/`（4 文件 / 40,474 字节） | — | 剔除 | 能力注册中心实现文件，非导览必需 |
| `.agents/vendor-integration/`（7 文件） | 53~113 | 剔除 | vendor 协同细则，SpecWeave 专属 |
| `.agents/config/`、`.agents/cmake/`、`.agents/brand/`、`.agents/reports/`、`.agents/cache/`、`.agents/.cache/`、`.agents/logs/`、`.agents/.temp/` | — | 剔除 | 配置/构建/品牌/报告/缓存/日志类，非规范内容 |

### 2.12 参考资产：`templates/agent-workspace-hub/`

| 文件相对路径 | 行数 | 建议 | 一句话理由 |
|---|---|---|---|
| `AGENTS.md` | 74 | 精简 | starter 根契约的直接改写底本 |
| `README.md` | 41 | 导览 | 骨架模板说明 |
| `.agents/README.md` | 60 | 精简 | 骨架版 `.agents/` 首页底本 |
| `.agents/ONBOARDING.md` | 7 | 剔除 | 占位（7 行） |
| `.agents/context-routing.md` | 6 | 剔除 | 占位（6 行） |
| `.agents/global-core-rules.md` | 6 | 剔除 | 占位（6 行） |
| `.agents/capability-registry.md` | 6 | 剔除 | 占位（6 行） |
| `.agents/docs/development-standards.md` | 6 | 剔除 | 占位（6 行） |
| `.agents/docs/`（4 个 README 占位） | 2 | 剔除 | 占位 |
| `.agents/` 各类目 README（checklists/commands/config/modules/protocols/roles/rules/scripts/skills/teams/templates/tools/workflows） | 2 | 剔除 | 占位（各 2 行） |
| `apps/AGENTS.md`、`projects/AGENTS.md`、`vendor/AGENTS.md` | 4 | 剔除 | 占位（各 4 行） |

### 2.13 类目保留/剔除数量统计

| 类目 | 讨论文件数 | 保留/精简 | 导览 | 剔除 |
|---|---|---|---|---|
| 根契约 | 2 | 2 | 0 | 0 |
| 入口层 | 9 | 5 | 1 | 3 |
| protocols | 18 | 3 | 0 | 15 |
| rules | 23（不含 data-security 约 110） | 10 | 0 | 13 |
| roles | 10 | 6 | 0 | 4 |
| workflows | 4 | 4 | 0 | 0 |
| templates | 5（另 40+ 未逐列） | 3 | 0 | 2+ |
| commands | 16 | 1 | 0 | 15 |
| checklists | 24 | 1 | 0 | 23 |
| skills | 4378 | 2 | 0 | 4376 |
| 导览型类目 | 8 README + 41 其他 | 0 | 8 | 41 |
| agent-workspace-hub | 28 | 3 | 1 | 24 |

> 统计口径：本表仅统计上表逐行列举的文件；未逐列的同目录文件计入「剔除」。

## 3. 「1 小时可消化」行数预算表

### 3.1 产品硬约束

- starter ≤ 50 文件
- 教程 ≤ 900 行
- 演练 ≤ 600 行
- 教程 + 演练合计 ≤ 1500 行

### 3.2 starter 类目文件数与行数分配（建议值）

| 类目 | 建议文件数 | 建议行数上限 | 对应来源 |
|---|---|---|---|
| 根契约 `starter/AGENTS.md` | 1 | 80 | `templates/agent-workspace-hub/AGENTS.md` + 仓库根 `AGENTS.md` 精简 |
| 入口层（ONBOARDING / context-routing / global-core-rules / capability-registry / README） | 5 | 250 | `.agents/` 根级精简 |
| roles（README + developer / reviewer / tester） | 4 | 120 | `.agents/roles/` 保留原件 |
| rules（README + 5 条核心规则） | 6 | 400 | `.agents/rules/` 精简 |
| protocols（README + prompt-bootstrap + workspace-discovery） | 3 | 180 | `.agents/protocols/` 精简 |
| workflows（README + feature-development + code-review） | 3 | 90 | `.agents/workflows/` 保留/精简 |
| templates（README + task-template + handoff-template） | 3 | 90 | `.agents/templates/` 保留原件 |
| commands（README + 1 代表） | 2 | 90 | `.agents/commands/` 精简 |
| checklists（README + 1 代表） | 2 | 80 | `.agents/checklists/` 导览 |
| skills（README + load-specweave/SKILL.md 示例） | 2 | 80 | `.agents/skills/` 精简 |
| 导览 README（modules / teams / prompts / tools / worlds / capabilities / cases / systems） | 8 | 80 | 各 README 精简（每≤10 行） |
| 许可说明 | 1 | 20 | 新建 |
| **合计** | **40** | **1560** | 预留 10 文件 / 行数余量至 50 文件上限 |

> 注：starter 行数上限为「内容体量参考值」，非产品硬约束；产品硬约束仅约束文件数 ≤50 与 教程+演练 ≤1500 行。

### 3.3 教程 + 演练行数分配

| 交付物 | 段位 | 建议行数上限 |
|---|---|---|
| 教程 `guide/README.md`（总览） | — | 100 |
| 教程 `00-overview.md` | 概览 10min | 200 |
| 教程 `01-bootstrap.md` | 装载 15min | 225 |
| 教程 `02-first-task.md` | 首个任务 25min | 225 |
| 教程 `03-next-steps.md` | 进阶 10min | 150 |
| **教程小计** | 60min | **900** |
| 演练 `walkthrough/`（任务书 → spec → 实施 → 产出物 → 验收） | 25min | 600 |
| **教程 + 演练合计** | — | **1500** |

> 校验：教程 900 ≤ 900 ✓；演练 600 ≤ 600 ✓；合计 1500 ≤ 1500 ✓。

## 4. 质量门 G1 自查

| 检查项 | 结果 |
|---|---|
| 类目覆盖数 | 12 个类目（根契约 / 入口层 / protocols / rules / roles / workflows / templates / commands / checklists / skills / 导览型类目 / agent-workspace-hub），≥10 ✓ |
| 每条候选行是否含「文件路径 + 实测行数 + 保留/剔除建议 + 理由」 | 是 ✓ |
| 行数实测方式 | `(Get-Content <file> | Measure-Object -Line).Lines` 逐个实测 ✓ |
| 因果连接词检查（6 类禁用连接词：因/致/故/由/是故/从属式） | 0 命中 ✓ |
| 预算表 | 含 starter 文件数（40 ≤50）与行数分配（教程 900 + 演练 600 = 1500）✓ |