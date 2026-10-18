---
type: spec
id: "specweave-and-subprojects-comprehensive-retrospective-export"
title: "SpecWeave 与其第一方子项目全面复盘与报告归档"
version: "1.0.0"
source: "seven-concepts-comprehensive-retro 技能 + 用户 2026-10-18 指令（Use Skill: seven-concepts-cmd 全面复盘本项目及其子项目）"
---

# Spec：SpecWeave 与其第一方子项目全面复盘

## 0. 背景

| 项 | 内容 |
|---|---|
| 触发 | 用户指令「全面复盘本项目及其子项目」，并确认范围为「第一方全量」 |
| 编排 | [seven-concepts-cmd](../../../../.agents/skills/seven-concepts-cmd/SKILL.md) 元编排 + seven-concepts-comprehensive-retro 场景技能 |
| 场景判定 | 场景 1「里程碑复盘」链路 R→I→E→V→A→C（含 V 对抗审查，不引入 F 第一性原理） |
| 基线 | 本项目首次全项目复盘为 [retrospective-specweave-full-project-20260719](../../../../docs/retrospective/reports/project-reports/retrospective-specweave-full-project-20260719/README.md)（时点 2026-07-19） |
| 内容敏感度 | 公开（开源仓库自述复盘）→ 标准工作流，产物入根 `docs/`；Spec 落 `.trae/specs/retrospectives-insights/` |

## 1. 范围

**纳入（in）**

1. 主权区：`AGENTS.md`、`.agents/`（roles/rules/protocols/skills/commands/scripts/templates 等）、根 `docs/`
2. 内置应用区：`apps/`（五分组 + 根级，含各应用自治 `.agents/`）
3. 第一方子项目区：`projects/xuanspace`、`projects/awesome-okf-xs`、`projects/daoapps.github.io`（三个 git submodule）+ `projects/monetize`、`projects/tvm-ffi`（主仓直接跟踪的工作目录）
4. 规格区：`.trae/specs/`

**排除（out）**

1. `vendor/` 18 个第三方子模块的内部演进——仅作外部依赖规模登记，不逐模块复盘
2. `.temp/`、`.cache/`、`build/` 等临时/构建目录
3. 任何在途未提交改动的回滚或修复（全程只读）

## 2. 交付物

| # | 交付物 | 落点 |
|---|---|---|
| D1 | 事实清单（F 编号） | 本目录 `facts.md` |
| D2 | 洞察四元组 | 本目录 `insights.md` |
| D3 | E 阶段模式萃取与去重裁决 | 本目录 `e-stage-pattern.md` |
| D4 | V 对抗审查记录 | 本目录 `v-adversarial-review.md` |
| D5 | 复盘报告四文件 | `docs/retrospective/reports/project-reports/retrospective-specweave-and-subprojects-comprehensive-20261018/`（`README.md` + `insight-extraction.md` + `actionable-items.md` + `index.md`） |
| D6 | 模式入库四处登记（新沉淀 1 条 + 并入既有 1 条） | 模式 `.md` + 伴生 `.toml` + 域 toctree + 主索引总表 |
| D7 | 报告索引两处登记 | `project-reports/index.md` toctree + `project-reports/README.md` 清单表 |
| D8 | 独立审查记录 | 本目录 `review.md` |
| D9 | Meoo Fellow 申请草稿（私域） | `playground/meoo/fellow-application-draft-20261018.md` |

## 3. 验收标准

| AC | 类型 | 内容 |
|---|---|---|
| AC-1 | rule | `facts.md` 中每条事实（F 编号）均带来源；全文不含因果推断词（因为/导致/所以/由于/因此） |
| AC-2 | rule | 事实编号 F-001 起连续无缺号；抽查 ≥10 条回溯命令可复现 |
| AC-3 | rule | 洞察 ≥3 条，每条四元组（现象/根因/影响/建议）完整，各引用 ≥2 个 F 编号且无悬空引用 |
| AC-4 | rule | E 阶段每条候选模式均给出「新建 L1 / 并入既有 / 不入库」裁决之一，新建模式四要素齐全 |
| AC-5 | rule | V 对抗审查覆盖四视角、意见 ≥5 条、采纳 ≥2 条，且采纳项在报告中有可定位的修正痕迹 |
| AC-6 | rule | 行动项每条含优先级/Owner/触发条件/可判定验收标准，无「加强沟通」「持续关注」式表述 |
| AC-7 | rule | 报告四文件齐备；三件套 frontmatter 含 `type` 与 `source`，`index.md` 为纯 toctree 且无 frontmatter |
| AC-8 | rubric | 质量门：`check-links.py` 对报告目录与模式库目录 0 新增断链（维度：断链数；阈值：0；锚点：命令退出码与输出） |
| AC-9 | rubric | 质量门：新 YAML/TOML 实际解析通过；报告与模式文档无 `file:///`、无 `.temp/` 引用（维度：禁用项命中数；阈值：0） |
| AC-10 | rule | 模式入库四处登记齐全：模式 md、伴生 toml、域 toctree（字母序）、主索引总表各 1 条 |
| AC-11 | rule | 独立审查由 fresh-context 只读子代理执行，逐条对照本 AC 打开一手文件取证，P0 全部修复并回归 |
| AC-12 | rule | 未获用户明确指令前不创建 git 提交 |

## 4. 约束与红线

1. `projects/`、`vendor/` 为 git submodule，本次全程只读，不修改其内部文件
2. 不修改、不回滚工作区既有在途改动（采集时点已如实登记）
3. 报告与模式文档的交叉引用一律使用相对路径，禁止 `file:///`（本 Spec 文件内的绝对路径链接仅用于指向本仓文件，报告产物中不使用）
4. 派生产物 frontmatter 须携带 `source`
5. 不得向 `.agents/docs/` 写入任何内容（该路径已废止）
