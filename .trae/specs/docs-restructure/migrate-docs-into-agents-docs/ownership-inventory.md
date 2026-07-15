# docs 与 .agents 归属清单

## 目标

本清单用于完成 Task 1 的“迁移前盘点与第一性分类决策”，明确当前仓库中 `docs/` 与 `.agents/` 的默认归属、边界敏感点，以及根级 `.agents/docs/` 作为未来迁移容器的现状。

## 结论摘要

- 原 `docs/` 子树默认归属为“人类文档”，迁移后只改变物理位置，不改变语义归属。
- 根级 `.agents/docs/` 当前已存在，但此轮盘点未发现已落地的根级内容，可视为待承载迁移内容的空容器。
- 原生 `.agents/` 体系默认归属为“智能体专属文档/资产”，应按现有路由、规则、协议、角色、脚本边界保留，不被迁移内容覆盖。
- 边界模糊内容以“主要读者 + 主要触发方式”判定；若仍模糊，后续必须在 `.agents/docs/README.md` 或 AGENTS 路由中补充显式说明。

## 默认归属规则

| 路径模式 | 默认归属 | 判定依据 | 迁移阶段动作 |
|---|---|---|---|
| `docs/**` | 人类文档 | 来源于原人类文档根目录；主要通过 README、知识索引、人工浏览进入 | 直接迁入 `.agents/docs/`，语义保持不变 |
| `.agents/ONBOARDING.md`、`capability-registry.md`、`capability-boundaries.md`、`global-core-rules.md`、`context-routing.md`、`VENDOR-INTEGRATION.md` | 智能体专属文档 | 属于根级规范入口，服务智能体启动、路由与治理 | 原位保留 |
| `.agents/{capabilities,capability-registry,roles,modules,prompts,tools,protocols,rules,workflows,templates,teams,systems,cases,commands,worlds,checklists,skills,config,scripts}/**` | 智能体专属文档/资产 | 主要通过 `AGENTS.md` 路由、规则入口、脚本逻辑发现 | 原位保留，不与迁移内容混放 |
| `.agents/docs/` | 迁移目标容器 | 物理聚合容器；迁移后同时承载“人类文档”和“智能体专属文档”两类内容 | 后续必须补边界 README，禁止出现 `.agents/docs/docs/` |
| `.agents/scripts/docs/**` | 智能体域内的人类可读辅助文档 | 可被人阅读，但发现方式与维护方式仍从属于 `.agents/scripts/` 工具体系 | 原位保留，并在边界说明中标注为“智能体域内辅助文档” |
| `.agents/README.md` | 智能体域入口说明 | 面向人类可读，但其作用是解释 `.agents/` 容器和 AI 路由结构 | 原位保留，继续作为 `.agents/` 容器入口 |

## `docs/` 当前顶层归属

### 顶层目录

以下目录默认归为“人类文档”，迁移后仍保持该语义：

- `docs/architecture/`
- `docs/code-wiki/`
- `docs/knowledge/`
- `docs/patterns/`
- `docs/quality/`
- `docs/retrospective/`
- `docs/standards/`
- `docs/superpowers/`
- `docs/task-summaries/`
- `docs/templates/`
- `docs/test-plans/`

### 顶层入口文件

以下入口文件默认归为“人类文档”，迁移后仍应作为导航、说明或知识入口继续可读：

- `.agents/docs/README.md`
- `.agents/docs/agent-roles.md`
- `.agents/docs/collaboration.md`
- `.agents/docs/development-standards.md`
- `.agents/docs/knowledge-base.md`
- `.agents/docs/methodology-analysis-report.md`
- `.agents/docs/project-highlights.md`
- `.agents/docs/project-overview.md`
- `.agents/docs/project-structure.md`
- `.agents/docs/raci-governance-standards.md`
- `.agents/docs/related-links.md`
- `.agents/docs/reuse-and-generalization.md`
- `.agents/docs/roadmap.md`
- `.agents/docs/tech-stack.md`
- `.agents/docs/trae-project-adaptation-guide.md`
- `.agents/docs/verification-automation.md`

## `.agents/` 当前顶层归属

以下顶层目录默认归为“智能体专属文档/资产”，迁移阶段不得被人类文档树覆盖：

- `.agents/capabilities/`
- `.agents/capability-registry/`
- `.agents/checklists/`
- `.agents/commands/`
- `.agents/config/`
- `.agents/modules/`
- `.agents/prompts/`
- `.agents/protocols/`
- `.agents/roles/`
- `.agents/rules/`
- `.agents/scripts/`
- `.agents/skills/`
- `.agents/templates/`
- `.agents/teams/`
- `.agents/tools/`
- `.agents/workflows/`
- `.agents/worlds/`
- `.agents/systems/`
- `.agents/cases/`

## 边界敏感项

| 路径 | 默认归属 | 为什么敏感 | 当前处理结论 |
|---|---|---|---|
| `.agents/docs/` | 目标容器 | 后续会同时容纳迁移后的人类文档与原生 agent 侧内容，天然是边界交汇点 | 当前为空容器；后续必须先补边界 README 再落内容 |
| `.agents/README.md` | 智能体专属文档 | 读者有人类维护者，但服务对象是 AI 规范容器 | 继续留在 `.agents/` 根，不并入迁移树 |
| `.agents/scripts/docs/**` | 智能体域内辅助文档 | 内容可人读，但通过脚本目录发现，维护归属仍在 `.agents/scripts/` | 不迁移；后续边界 README 中注明此类例外 |

## Task 1 对应产物

- 目录归属决策：本文件
- 基线与备份：见 [migration-baseline.md](migration-baseline.md)
- 基线明细：见 [artifacts/docs-baseline-summary.json](artifacts/docs-baseline-summary.json)、[artifacts/docs-baseline-manifest.json](artifacts/docs-baseline-manifest.json)
- `docs/` 根路径引用清单：见 [artifacts/docs-root-reference-files-outside-docs-clean.json](artifacts/docs-root-reference-files-outside-docs-clean.json)
