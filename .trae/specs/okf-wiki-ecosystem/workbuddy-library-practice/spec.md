---
type: spec
title: "WorkBuddy 资料库协作与工作台实践 OKF Wiki"
description: "将 11 份 WorkBuddy 资料库教程与案例整理为可溯源的实践知识包，并与既有官方文档包明确分工。"
tags: [okf-bundle, workbuddy, library, collaboration, knowledge-workflow, case-study]
methodology: seven-concepts-cmd
content-sensitivity: public
status: draft
sources:
  - id: S01
    resource: "https://www.workbuddy.cn/space/d/guTORrnry3ajlXZ275LEgI?source=3"
    title: "资料库新手教程"
  - id: S02
    resource: "https://www.workbuddy.cn/space/d/af5ArEWGR0c0JRIUYkTyr7?source=3"
    title: "一分钟玩转资料库（含表情标题版本）"
  - id: S03
    resource: "https://www.workbuddy.cn/space/d/eC9igsnYGL62ehjHelJnf2?source=3"
    title: "一分钟玩转资料库"
  - id: S04
    resource: "https://www.workbuddy.cn/space/d/n5QMwOfRMV1JSKKShwErTx"
    title: "和 Agent 一起用资料库"
  - id: S05
    resource: "https://www.workbuddy.cn/space/d/CS0vSIVlr2ufPQb6M4VTVW"
    title: "WorkBuddy资料库：三种载体，一套数据"
  - id: S06
    resource: "https://www.workbuddy.cn/space/d/f6dhUR3e5ZAfXJJVDIOxSG"
    title: "人机协作：和AI一起改文档"
  - id: S07
    resource: "https://www.workbuddy.cn/space/d/6eIVawhHqEthXtVc07P7em"
    title: "使用资料库团队空间多人协作"
  - id: S08
    resource: "https://www.workbuddy.cn/space/d/FJDQeUziLM9BmPGVVKFAj1"
    title: "知识复利：让资料库里的知识流动起来"
  - id: S09
    resource: "https://www.workbuddy.cn/space/d/MFIIY4nQkybtYnVL0W7SIt"
    title: "使用资料库搭建个人和团队工作台"
  - id: S10
    resource: "https://www.workbuddy.cn/space/d/ZljbYQzFpALFLcPwKPlct1?source=3"
    title: "家庭教育专家实战：手把手教你用WorkBuddy搭建专家"
  - id: S11
    resource: "https://www.workbuddy.cn/space/d/DZmnLyzRuyKYvnfHD5WniJ?source=3"
    title: "孙北北面包店同款-如何用资料库打造超级团队（资料库目录）"
generated: { by: "process:TRAE-spec-mode", at: "2026-10-19" }
---

# WorkBuddy 资料库协作与工作台实践 OKF Wiki

## Overview

- **Summary**：把用户提供的 13 个 WorkBuddy 链接（去重后 11 个唯一资料）整理为一个相邻实践包，沉淀资料库协作、人机共编、内容载体分工、知识回存、专家边界与团队工作台案例。
- **Purpose**：在保留来源差异与证据边界的前提下，让读者理解资料库如何从文件存放处变成个人/团队与 Agent 共用的工作空间；避免复述既有官方产品文档包。
- **Target Users**：WorkBuddy 资料库初学者、需要组织个人或团队知识工作流的使用者，以及研究 Agent 人机协作的读者。

## Goals

- 覆盖 11 个唯一来源，并在知识包中保留每条事实、观点和案例的来源映射。
- 将来源中可迁移的实践方法与个案演示分层呈现，明确作者观点、产品事实、演示数据和未验证结论。
- 与现有 `workbuddy-official-docs` 包互补：本包讲实践模式与案例；官方能力、权限细节和可照做产品操作链接回该包，不重复搬运。
- 通过 OKF v0.2 结构、toctree、相对链接、UTF-8 和子项目质量门。

## Non-Goals

- 不重写 WorkBuddy 官方产品手册或复制 `workbuddy-official-docs` 的资料库操作步骤。
- 不把作者体验或案例叙述升级为官方承诺、普遍效果或已独立验证的因果结论。
- 不把面包店演示页中的虚构数据表述为真实经营数据。
- 不修改 SpecWeave 主仓中与本任务无关的文件，不执行 Git commit 或 push。
- 不将知识包中的模式另行登记到主仓方法论模式库。

## Background & Context

### 内容敏感度与采集范围

- 用户已明确确认这些资料按公开内容处理，并指定输出至 `projects/awesome-okf-xs/doc/bundles/`。虽然读取正文使用了已登录的 WorkBuddy 页面，此处按用户的明确确认进入公开流程。
- 输入共 13 个链接，其中 `af5ArEWGR0c0JRIUYkTyr7` 与 `FJDQeUziLM9BmPGVVKFAj1` 各重复一次；唯一来源为 S01–S11。
- S11 是资料库目录而非单篇文章，包含主工作台、商品资料、仓配费用、数仓需求看板等文件。当前已读取四个 HTML 子看板；主工作台页面正文存在加载占位，需在来源台账中保留这一采集缺口。
- S11 的四个 HTML 看板标注其数据为虚构演示数据。

### 查重与归属

| 候选归属 | 判定 | 理由 |
| --- | --- | --- |
| `jishu/ai/ecosystems/tencent/workbuddy-official-docs/` | 不直接并入 | 该包已覆盖产品资料库、个人/团队空间、权限、MD/CSV/HTML 联动、人机修订、知识库工作流、专家/技能及 9 个官方操作示例；其信源边界是 WorkBuddy 官方站点与官方文档。 |
| `jishu/ai/ecosystems/tencent/workbuddy-library-practice/` | 选定 | 本任务来源是 11 份独立的资料库教程/实践材料与案例目录，主线为实践编排、协作方法和工作台案例；独立来源台账便于保留作者/案例边界，并可链接回官方包作为产品事实参照。 |
| `sheke/industry/workbuddy-content-system/` | 排除 | 该包讨论 AI 驱动的内容业务系统，不以资料库协作与团队工作台为主题。 |
| 新建分组 | 排除 | 腾讯生态分组已存在且收录多个 WorkBuddy 知识包，无需新增分组。 |

**重复控制规则**：如 R 阶段映射发现某条来源没有超出官方包的新增内容，只登记该来源及覆盖映射，不在本包复述该内容；引用产品能力时链接到官方包对应概念/示例页。

### 来源主题初步映射

| 来源 | 已采集主题 | 知识包处理边界 |
| --- | --- | --- |
| S01–S04 | 资料库入门、快速使用、Agent 调用 | 提取资料库作为 Agent 工作空间的使用模式；不重写官方操作步骤。 |
| S05 | MD、CSV、HTML 三种载体与数据联动 | 提炼内容、数据、呈现的职责分工；引用官方包作产品能力核对。 |
| S06 | AI 修订与人工审阅 | 描述提议、审阅、接受的协作边界；区分 MD 与 HTML 案例原文所述行为。 |
| S07 | 团队空间多人协作 | 提炼共享空间中的成员、内容与 Agent 协作模式；权限事实回链官方包。 |
| S08 | 知识成果回存与复用 | 提炼“调用—产出—回存—再调用”的知识循环，不宣称未经证实的效率提升。 |
| S09 | 个人与团队工作台 | 按场景组织资源和工作区的实践。 |
| S10 | 家庭教育专家案例 | 提炼专家判断流程、角色边界、Prompt/Skill/知识库分工和测试要点；不得把案例效果推广为普遍结果。 |
| S11 | 面包店团队工作台目录 | 作为组合工作台案例；标明数据为虚构，主工作台正文未完整取得。 |

## Functional Requirements

- **FR-1**：交付一个位于 `jishu/ai/ecosystems/tencent/workbuddy-library-practice/` 的 OKF v0.2 知识包；至少包含根 `index.md`、`log.md`、`concepts/`、`references/` 及各层级 `index.md`/toctree。
- **FR-2**：建立稳定来源 ID S01–S11 和连续事实编号；至少登记 20 条可逐项回溯的事实。事实、作者观点、推论与案例描述分层，不将解释混入客观事实。
- **FR-3**：知识结构按读者问题组织，覆盖 Agent 共用工作空间、人机共编与审阅、MD/CSV/HTML 分工、团队协作与知识回存、专家构建边界、工作台案例；具体篇目以 Plan 阶段确认的去重结果为准。
- **FR-4**：只有当材料同时提供读者可照做的步骤，以及足以确认步骤顺序/输入输出/适用条件的复现信息时，才创建 `examples/`。不满足时不得为凑结构设立示例目录。
- **FR-5**：父级腾讯生态索引与 `bundles/index.md` 接入新包；计数以实施时读取的磁盘基线为准，不在 Spec 中冻结旧数字。
- **FR-6**：主题关联至少链接 `workbuddy-official-docs`、`workbuddy-one-sentence-mvp`、`tencent-buddy-family`，并用一句话说明各自分工。

## Non-Functional Requirements

- **NFR-1**：所有具体产品能力、数值和限制均有 S 编号或官方知识包引用；不把单一作者陈述写成已核验的客观结论。
- **NFR-2**：全包中文为主，文件名使用 kebab-case；所有 Markdown 内容文件遵循 awesome-okf-xs 的 frontmatter 规则。
- **NFR-3**：所有内部链接可达，无 `file:///` 绝对路径；每个内容文件都能从根 toctree 到达；文件为 UTF-8。
- **NFR-4**：完成内容四视角审查（魔鬼代言人、新人、业务、未来），对可行动问题修订并记录裁定。

## Constraints

- **Technical**：目标仓库为 `projects/awesome-okf-xs` 子模块；遵循其 `AGENTS.md`、OKF v0.2、索引与 `invoke gates.*` 规范。实施前后核实子模块自身 Git 状态。
- **Business**：本轮 Spec 批准前不实施知识包或索引变更；未收到明确提交请求时不 commit、不 push。
- **Dependencies**：来源正文采集摘要来自当前会话既有采集；S11 主工作台正文不完整，不能推断其未取得的内容。WorkBuddy 官方能力参照点为 2026-10-15 核验的 `workbuddy-official-docs`，对时效性能力须提示复查。
- **Repository boundary**：仅修改本 Spec 指定的知识包和必要的两个索引；若子项目规则或真实工作树状态显示不能安全写入，则记录阻塞并停止子模块写操作。

## Assumptions

- 用户先前对公开性的明确确认覆盖当前 11 个唯一资料；如后续发现个人信息、商业秘密或未授权客户数据，则暂停并重新判级。
- S11 的明确“虚构演示数据”说明适用于已读取的四个 HTML 看板；不能据此推断未取得的主工作台正文。
- 本包可以作为官方文档包的相邻实践补充，但是否保留独立包须由 R 阶段的逐来源去重结果验证；若无足够新增内容，应在实施前回到 Spec 调整归属。

## Acceptance Criteria

### AC-1: 来源覆盖与敏感度可审计
- **Type**: `rule`
- **Given**：输入链接共 13 个，去重后 11 个唯一 ID。
- **When**：知识包完成来源登记。
- **Then**：S01–S11 每项均对应其 WorkBuddy URL、标题、采集状态和内容类型；两项重复链接被显式记录为去重结果；公开判定注明用户授权及其依据。
- **Pass Condition**：11 个来源 ID 与本 Spec 清单一一对应，无遗漏或重复编号；S11 的正文缺口和虚构数据声明均登记。
- **Evidence**：bundle `references/article-source.md`、`references/verification.md` 与根 `index.md`。

### AC-2: 与现有 WorkBuddy 知识包无实质重复
- **Type**: `rubric`
- **Dimension**：主题边界与重复控制。
- **Scale**：1-5
- **Anchors**：1 = 大段复述官方包且混淆信源；3 = 有分工说明但仍有重复或边界模糊；5 = 每个主要章节均来自 S01–S11 的实践增量，官方产品能力明确回链且不重复搬运。
- **Pass Threshold**：>= 4
- **Evidence**：来源—既有内容覆盖矩阵、逐章来源映射、审查记录。

### AC-3: 事实、观点与案例分层
- **Type**: `rule`
- **Given**：11 份来源含教程、作者解释、专家案例和工作台演示材料。
- **When**：事实与教程内容写入 bundle。
- **Then**：至少 20 条可溯源事实有连续编号；作者观点、未核实效果、产品事实和推论明确区分；所有具体数值/能力声明均能回溯来源。
- **Pass Condition**：抽查任意 10 条事实可定位原始 S 编号；没有把 S10 个案或 S11 虚构数据表述为普遍效果/真实经营事实。
- **Evidence**：`references/article-source.md`、正文事实编号、`references/verification.md`。

### AC-4: 面向读者的知识结构符合骨架判据
- **Type**：`rubric`
- **Dimension**：章节组织、初学者可读性与示例适用性。
- **Scale**：1-5
- **Anchors**：1 = 按来源顺序堆叠摘要或伪造可复现步骤；3 = 主题完整但重组或边界说明一般；5 = 按读者问题组织、从工作空间到协作与案例递进，且 `examples/` 取舍严格通过可复现性两问。
- **Pass Threshold**：>= 4
- **Evidence**：bundle 导航、章节映射表、示例可复现性判定。

### AC-5: OKF 与仓库索引门禁通过
- **Type**: `rule`
- **Given**：目标子模块现有 toctree 与计数基线已读取。
- **When**：bundle 与索引完成。
- **Then**：bundle 各级导航、父级分组索引和总索引同步；相对链接有效；UTF-8 与 Sphinx/Invoke 质量门通过，或在依赖不可用时完成规范要求的逐项手工等效检查并如实记录。
- **Pass Condition**：`invoke gates.all` 和 `invoke build` 通过；若命令因环境依赖无法运行，等效检查全部有证据且不得宣称自动门禁通过。
- **Evidence**：命令输出、索引 diff、bundle `log.md`。

### AC-6: 独立对抗审查完成
- **Type**：`rule`
- **Given**：知识包内容与门禁均完成。
- **When**：进入 Spec Mode Review 阶段。
- **Then**：四视角均给出具体问题与裁定；有行动项的发现已修复并回归验证；审查检查点覆盖本 Spec 所有验收标准。
- **Pass Condition**：`review.md` 记录独立审查结果 `pass`，无未关闭的可行动发现。
- **Evidence**：Spec `review.md`、bundle `references/verification.md` 和修订 diff。

## Open Questions

- [x] 输出位置：用户已确认公开处理并指定 `projects/awesome-okf-xs/doc/bundles/`；选定腾讯生态现有分组。
- [x] Spec 与 bundle 的归属：Spec 放 `.trae/specs/okf-wiki-ecosystem/`；bundle 目标为 `jishu/ai/ecosystems/tencent/workbuddy-library-practice/`，且须经逐来源去重验证。
