---
id: "create-agent-workspace-starter"
title: "智能体工作区起步套件（Agent Workspace Starter）——最小化 .agents 萃取与对外运营产品化"
source: "用户指令（2026-10-07）+ seven-concepts-cmd 方法论编排"
created_at: "2026-10-07"
status: "draft"
theme: "workspace-governance"
methodology: "seven-concepts（场景：知识沉淀→产品化，链路 R→I→E→V→C；G1-G4 质量门）"
content-sensitivity: "public"
---

# 智能体工作区起步套件（Agent Workspace Starter）- Product Requirements Document

## Overview

- **Summary**: 从 SpecWeave `.agents/`（实测 6850 文件 / 134.5 MB）萃取「全貌导览集」最小化入门套件（≤50 文件），落地为 `apps/dev-tools/agent-workspace-starter/` 对外运营产品。交付物：①最小化 starter 套件（可拷入买家自有项目）；②60 分钟时间盒教程；③「规格驱动小任务」端到端演练剧本；④零依赖自检脚本；⑤装载门面（一句话提示词 + Trae Skill 门面）；⑥运营落地页 README。支撑「9.9 元 · 1 小时快速上手」的低门槛对外运营。
- **Purpose**: 让外部买家以 9.9 元价格、60 分钟为限，从零完成「装载最小化工作区 → 跑通首个规格驱动任务 → 获得可验证产出物」的完整成功体验；同时为 SpecWeave 提供可复制的对外运营交付底座。
- **Target Users**: ①潜在买家（AI 工具个人用户 / 小团队）；②运营者（本项目所有者，需低成本交付与支持）；③智能体（装载 Skill 门面后可辅助买家完成上手）。

## Goals

- **G1**: 萃取全貌导览最小集（≤50 文件）——每个规范类目保留代表文件，剔除 scripts/skills 全家桶（二者占 `.agents/` 总量约 93%）
- **G2**: 交付 60 分钟时间盒教程（总览 + 4 段：概览 10min / 装载 15min / 首个任务 25min / 进阶 10min）
- **G3**: 交付端到端演练剧本——「规格驱动小任务」全流程（写 spec → 实施 → 产出物），照抄可完成
- **G4**: 交付零依赖自检脚本（纯标准库 Python）——程序化验证 starter 装载完整性与可用性
- **G5**: 交付装载门面——可复制的一句话装载提示词 + Trae Skill 门面
- **G6**: 交付运营落地页 README——价值主张 / 内容清单 / 1 小时路径 / 许可与使用边界 / 获取方式
- **G7**: 完成 apps 区域合规登记——apps/AGENTS.md 路由表与 apps/README.md 清单同步

## Non-Goals (Out of Scope)

- 不做支付 / 购买系统（9.9 元交易在站外完成，不属本 spec）
- 不复制完整 SpecWeave 体系（`.agents/` 6850 文件不在交付范围）
- 不引入第三方依赖、不依赖构建步骤（套件为纯 Markdown + 单自检脚本）
- 不修改 `.agents/`（主权区）与 `templates/` 现有资产——只读萃取
- 不做 Hub CLI / A2A / 应用市场（属 agent-app-marketplace spec 范围，且其明确不含商业化计费）
- 不追求教程覆盖全部 17 条核心实践（聚焦「首个成功体验」）

## Background & Context

- `.agents/` 现状（2026-10-07 实测）：6850 文件 / 134.5 MB；`skills`（4378 文件 / 104 MB）+ `scripts`（2010 文件 / 27 MB）为主要体量；入口层其实轻量（ONBOARDING.md 84 行、global-core-rules.md 39 行、context-routing.md 120 行）
- 既有可复用资产：`templates/agent-workspace-hub/`（28 文件空骨架模板，实测 2026-10-07，来自 extract-agent-workspace-template spec）；`.agents/protocols/prompt-bootstrap.md`（322 行装载协议）；`.agents/skills/load-specweave/SKILL.md`（25 行）；`.agents/ONBOARDING.md`（17 条实践速查）
- 先例边界（查重结论）：extract-agent-workspace-template＝内部空骨架模板（无教程、无运营要素）；agent-app-marketplace＝Hub 生态技术平台（Non-Goal 明确不做商业化）；miaowu-ambassador-guide＝阿里云大使入驻文档（无关）
- 用户决策（2026-10-07 AskUserQuestion 两轮）：位置＝apps/dev-tools/；内容物＝教程 + 演练 + 自检脚本 + 装载门面（全选）；萃取档位＝全貌导览集 ~50 文件；演练主题＝规格驱动小任务；命名＝双层（英文技术名 Agent Workspace Starter ＋ 中文运营名「智能体工作区起步套件」）
- 方法论：seven-concepts 知识沉淀→产品化链（R→I→E→V→C），G1-G4 质量门强制

## Functional Requirements

- **FR-1**: 应用主体位于 `apps/dev-tools/agent-workspace-starter/`，目录布局：`starter/`（套件）+ `guide/`（教程）+ `walkthrough/`（演练）+ `scripts/`（自检）+ 装载门面文件（`bootstrap-prompt.md` + `skill/SKILL.md`）+ `README.md`
- **FR-2**: `starter/` 最小化套件——根 `AGENTS.md` 最小契约（含「启动协议」关键词锚点，支持智能体工作区发现）+ `.agents/` 全貌导览（roles/rules/protocols/workflows/templates/commands/checklists/skills/modules 等每个类目保留代表，附一句话导览）
- **FR-3**: `guide/` 60 分钟时间盒教程——总览（学习路径 + 时间盒表）+ 4 段：00 概览(10min) / 01 装载(15min) / 02 首个任务(25min) / 03 进阶(10min)，每段含目标、步骤与完成检查点
- **FR-4**: `walkthrough/` 演练剧本——规格驱动小任务全过程（任务书 → spec 样例 → 实施步骤 → 产出物 → 验收点），关键步骤含「照抄块」与可观察验收点
- **FR-5**: `scripts/verify_starter.py` 零依赖自检——检查 starter 文件齐备性、启动协议关键词锚点、相对链接可达性；通过 exit 0、缺失 exit 非 0 并输出中文缺项报告
- **FR-6**: 装载门面——`bootstrap-prompt.md`（可复制的一句话装载提示词，含安全规则 + 幂等条款）+ Skill 门面（五要素 SKILL.md，供 Trae 环境装载）
- **FR-7**: 运营支撑——README 落地页（价值主张 / 内容清单 / 1 小时路径 / 许可与使用边界 / 获取方式占位）；starter 内含简短许可说明
- **FR-8**: 区域登记——更新 apps/AGENTS.md 路由表与 apps/README.md 清单，运行 docgen 刷新应用清单

## Non-Functional Requirements

- **NFR-1**: 规模约束——starter ≤50 文件；教程 + 演练合计 ≤1500 行（「60 分钟可消化」为硬门）
- **NFR-2**: 零依赖——自检脚本仅用 Python 标准库；套件为纯 Markdown，无构建步骤
- **NFR-3**: 一致性——相对路径引用、禁 `file:///`；派生物 frontmatter 带 `source` 溯源；UTF-8 编码
- **NFR-4**: 可验证——自检脚本支持程序化验收；演练剧本每步有可观察验收点
- **NFR-5**: 可维护——starter 内每份萃取文件可用 `source` 字段追溯到 `.agents/` 源（原创文件注明原创）
- **NFR-6**: 独立可用——starter 拷贝到任意项目后独立工作，不依赖 SpecWeave 仓库其余部分

## Constraints

- **Technical**: 遵循 apps/AGENTS.md 应用自治规范与 apps/README.md 命名约定（kebab-case）；自检脚本以 py314 验证；Windows 环境（pwsh7 可用）
- **Business**: 9.9 元定位决定内容聚焦「首个成功体验」；不内建支付；许可边界须写明（防止 9.9 元入门包被当作完整版转售）
- **Dependencies**: 只读萃取 `.agents/`、`templates/agent-workspace-hub/`；方法论依据 seven-concepts（场景：知识沉淀→产品化）；本 spec 三件套遵循 TRAE-spec-mode 规范（spec.md + tasks.md，review.md 于 Review 阶段创建）
- **边界**: 新增仅限 `apps/dev-tools/agent-workspace-starter/` + apps 登记文件 + 本 spec 目录；不触碰 `.agents/` 主权区

## Assumptions

- 买家环境具备：可装载智能体（Trae 或兼容工具）+ git（或可下载 zip 获取）
- 「1 小时」＝跟随教程完成装载 + 首个演练任务（非通读全部规范）
- 9.9 元交付为内容包，获取 / 收款方式由运营者在站外提供（不属本 spec）
- 教程与套件语言为中文
- 演练的「规格驱动小任务」可在 25 分钟段位内完成（任务体量：单文件级小工具或单文档级产出）

## Acceptance Criteria

### AC-1: 交付物结构齐备

- **Type**: `rule`
- **Given**: 产品目录 `apps/dev-tools/agent-workspace-starter/` 已创建
- **When**: 枚举目录内容
- **Then**: 同时存在 `starter/`、`guide/`（总览 + 4 段）、`walkthrough/`（≥1 完整剧本）、`scripts/verify_starter.py`、装载门面（`bootstrap-prompt.md` + `skill/SKILL.md`）、`README.md`
- **Pass Condition**: 上述 6 类产物全部存在且非空；`starter/` 文件数 ≤50
- **Evidence**: 目录枚举输出清单 + 文件行数统计

### AC-2: 自检脚本零依赖且行为正确

- **Type**: `rule`
- **Given**: py314 环境，无第三方依赖
- **When**: 对完整 starter 运行 `python scripts/verify_starter.py`；再故意移除一个文件后重跑
- **Then**: 完整时 exit 0 并输出通过报告；缺文件时 exit 非 0 并列出缺失项
- **Pass Condition**: 两次运行的 exit code 与报告均符合预期
- **Evidence**: 两次命令输出（粘贴进 tasks.md Completion Evidence）

### AC-3: starter 独立可装载

- **Type**: `rule`
- **Given**: 将 `starter/` 拷贝到仓库外的一个空目录（模拟买家项目）
- **When**: 检查根 `AGENTS.md` 并执行启动协议关键词锚定（与根 AGENTS.md 步骤 1.2 同源：存在「启动协议」标题块）
- **Then**: 关键词锚点命中；文件间相对引用可达（无死链）
- **Pass Condition**: 「启动协议」关键词存在 + 链接检查 0 断链
- **Evidence**: 关键词搜索结果 + 链接检查输出

### AC-4: 装载门面可用

- **Type**: `rule`
- **Given**: 门面文件已创建
- **When**: 审查提示词与 SKILL.md
- **Then**: 提示词含安全规则（官方来源 / 路径确认 / 只读 / 幂等）且可直接复制使用；SKILL.md 含完整 frontmatter 且描述触发条件
- **Pass Condition**: 提示词 ≥6 条安全规则 + 幂等条款；SKILL.md frontmatter 完整（name/description/version）
- **Evidence**: 文件内容审查记录

### AC-5: 60 分钟可消化（时间盒达标）

- **Type**: `rubric`
- **Dimension**: 教程 + 演练的总学习量与路径清晰度
- **Scale**: 1-5
- **Anchors**: 1 = 总量 >3000 行或路径混乱；3 = 总量 1500-3000 行或部分段超时盒；5 = 总量 ≤1500 行、4 段时间盒明确、每段有完成检查点
- **Pass Threshold**: >= 4
- **Evidence**: 行数统计（wc 口径）+ 模拟新人试走记录（可委托子代理模拟买家走查）

### AC-6: 全貌导览完整度

- **Type**: `rubric`
- **Dimension**: 各规范类目代表覆盖率与可理解性
- **Scale**: 1-5
- **Anchors**: 1 = 覆盖 <5 个类目；3 = 覆盖 5-8 个类目；5 = 覆盖 ≥9 个类目（roles/rules/protocols/workflows/templates/commands/checklists/skills/modules 等）且每类目代表文件含一句话导览
- **Pass Threshold**: >= 4
- **Evidence**: starter/.agents/ 类目清单 + 抽样审查

### AC-7: 区域登记一致

- **Type**: `rule`
- **Given**: 新应用已落地
- **When**: 检查 apps/AGENTS.md 路由表与 apps/README.md 清单
- **Then**: 两处均含 agent-workspace-starter 条目（分组 = dev-tools，说明准确）
- **Pass Condition**: 两个文件均命中；docgen apps 刷新后清单仍正确
- **Evidence**: Grep 结果 + docgen 输出

### AC-8: 萃取溯源完整

- **Type**: `rule`
- **Given**: starter 内文件
- **When**: 检查 frontmatter
- **Then**: 每个从 `.agents/` 萃取的文件带 `source` 字段指向源文件路径；原创文件注明原创
- **Pass Condition**: 有 frontmatter 的萃取文件 100% 带 source
- **Evidence**: Grep `source:` 覆盖统计

### AC-9: 运营可用性

- **Type**: `rubric`
- **Dimension**: README 落地页支撑 9.9 元对外说明的完整度
- **Scale**: 1-5
- **Anchors**: 1 = 无价值主张；3 = 含价值主张与内容清单但缺许可边界；5 = 价值主张 / 内容清单 / 1 小时路径说明 / 许可与使用边界 / 获取方式 五要素齐备且文案可直接复用
- **Pass Threshold**: >= 4
- **Evidence**: README 审查记录

## Open Questions

- [ ] 演练小任务的具体选题（实施阶段定稿；候选：「单文件小工具（如目录树查看器）的规格驱动开发」）
- [ ] Skill 门面落位（默认仅作为产品交付物存在于 `skill/`；是否同时装入本仓 `.agents/skills/` 待批准时确认，若装需评估对主权区的影响）