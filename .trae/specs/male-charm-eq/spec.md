---
okf_version: "0.2"
type: spec
title: "提高男性魅力与情商 OKF 知识包 - Product Requirements Document"
status: complete
generated: { by: specweave-agent/trae, at: 2026-09-14 }
reviewed: { result: pass, score: 5/5, at: 2026-09-14 }
---

# 提高男性魅力与情商 OKF 知识包 - Product Requirements Document

## Overview

- **Summary**: 在 `projects/awesome-okf-xs/doc/bundles/sheke/personal-growth/` 分组下新建 OKF bundle `male-charm-eq/`（男性魅力与情商），与既有 `female-charm-eq`（女性版，已交付）形成姊妹知识包，系统化呈现「男性魅力（charm）+ 情商（EQ）」的理论与实操知识。
- **Purpose**: 将公开的吸引力心理学、男性气质研究、情商科学、沟通/界限/自信等实操知识，按 OKF v0.2 格式沉淀为可检索、可溯源、证据分级的中文知识包，供男性自学者系统提升人际魅力与情绪能力。
- **Target Users**: 希望提升人际魅力与情绪能力的男性读者；OKF 文档库读者；对证据分级（学界共识/单一研究/通俗主张）敏感的自学者。

## Goals

- 以「男性魅力 × 男性情商」双主线组织知识：魅力侧覆盖吸引力科学、男性气质与魅力模型、第一印象与自我呈现；情商侧覆盖能力模型 vs 混合模型之争、男性情绪社会化（「男孩不许哭」）、共情、情绪调节。
- 提供可落地的男性向实操：沟通与倾听、脆弱性与真诚、界限设定、自信训练、职场应用、亲密关系与约会场景。
- 对每个关键主张做证据分级；如实呈现男性圈（Manosphere/Red Pill/PUA/alpha 迷思）的伪科学性批判与反常识点（power posing 复制失败、进化心理学滥用等）。
- 全部文档遵循 OKF v0.2 frontmatter 规范，通过 toctree / bundles 索引质量门。

## Non-Goals

- 不提供医美、健身、整形、穿搭等外形改造建议（仅在有实证时提及体态/着装的心理机制，不做教程）。
- 不覆盖心理咨询、临床心理干预。
- 不推荐具体对象、不涉及择偶市场操作；不指导操纵或欺骗性社交技巧（PUA 操纵术明确排除）。
- 不采集私域内容（全部为公开信源）。
- 不与 `female-charm-eq` 重复——共享的情商理论（能力模型/混合模型、情绪调节）以精简引用方式处理，重点呈现男性特定维度。

## Background & Context

- 姊妹包 `female-charm-eq`（2026-09-14 交付）已建立 `sheke/personal-growth/` 分组（组=1 束，锚点组模式，`total_bundles=536/groups=59`）。
- 本次任务按七概念方法论（知识沉淀 R→I→E→V→C）编排：R 阶段三个并行调研子代理已启动（男性魅力理论 / 男性情商理论 / 实操与当代批判），返回可溯源事实清单后作为 facts.md 事实基础。
- 落盘位置决策：`relationships/` 分组定位为「经典著作解读」；本主题为综合方法论教程，归属既有 `sheke/personal-growth/`（个人成长与自我提升），组内束数 1→2。
- 知识库治理规则（awesome-okf-xs AGENTS.md）：新增 bundle 后必须同步 `sheke/index.md`、`personal-growth/index.md` 与总索引 `bundles/index.md` 五面计数，并通过 `invoke gates.toctrees`、`invoke gates.bundles`。

## Functional Requirements

- **FR-1**: bundle 采用三层结构 `concepts/` + `examples/` + `references/`，附工作文档 `facts.md`、`insights.md`、`log.md`。
- **FR-2**: 每个非保留 `.md` 文件携带 OKF v0.2 YAML frontmatter，`type` 字段非空；bundle 根 `index.md` 以 `{toctree}` 引用全部内容文档。
- **FR-3**: `facts.md` 汇总全部事实编号（F-xxx），每条可回溯到 `sources` 信源。
- **FR-4**: 分组 `sheke/personal-growth/index.md` 以 `{toctree}` 引用两个 bundle 根 index。
- **FR-5**: `sheke/index.md` 分组导航表 personal-growth 行束数 1→2；总索引 `bundles/index.md` 五面对账（frontmatter / 计数行 / 域节标题 / 分组表束数列 / toctree）同步更新（total_bundles 536→537，sheke 36→37 束）。

## Non-Functional Requirements

- **NFR-1**: 证据分级标注——每个理论主张标注「学界共识/单一研究/通俗主张/自媒体经验」。
- **NFR-2**: 批判视角——Manosphere/Red Pill/PUA/alpha-beta 二分法的伪科学属性、power posing 复制失败、进化心理学滥用必须如实呈现，禁止写成共识。
- **NFR-3**: 反物化、反操纵、反有毒男性气质——实操部分强调真诚、脆弱性、界限、尊重与自尊，不写「高冷即高价值」「操纵即魅力」导向。
- **NFR-4**: 文档为 UTF-8 编码；文件名 kebab-case 纯英文；正文中文。

## Constraints

- **Technical**: 遵循 OKF v0.2 frontmatter 规范（.agents/rules/frontmatter.md）；日期裸格式由 doc/conf.py 钩子处理，无需加引号。
- **Business**: 项目为 git submodule（projects/awesome-okf-xs），修改走子项目开发流程（本次为用户明确指定的产出物，直接在子项目内落盘）。
- **Dependencies**: 质量门脚本 `scripts/check-toctrees.py`、`scripts/check-bundles-index.py`；既有 `female-charm-eq` bundle 结构作为同构模板。

## Assumptions

- 用户期望的知识包规模对标姊妹包 `female-charm-eq`（10 概念 + 6 示例 + 2 参考 + 81 条事实）。
- R 阶段三个调研事实清单可直接作为 facts.md 的事实基础；实施阶段可小幅增补信源但不得引入未核验事实。
- `.trae/specs/male-charm-eq/` 为本工作流的规划产物区，bundle 本体落在 `doc/bundles/sheke/personal-growth/male-charm-eq/`。

## Acceptance Criteria

### AC-1: Bundle 目录结构与 OKF 规范合规（rule）
- **Type**: `rule`
- **Given**: bundle 落盘于 `sheke/personal-growth/male-charm-eq/`
- **When**: 检查目录树与全部 `.md` 文件
- **Then**: 存在 `concepts/`、`examples/`、`references/` 三层及各自 `index.md`；bundle 根 `index.md` 与三个子目录 `index.md` 均以 `{toctree}` 引用内容文档；所有非保留 `.md` 文件 frontmatter 含非空 `type`；存在 `facts.md`、`insights.md`、`log.md`
- **Pass Condition**: 目录树与 frontmatter 检查全部通过
- **Evidence**: `Glob`/`Read` 检查结果；`invoke gates.toctrees` 输出

### AC-2: 质量门通过（rule）
- **Type**: `rule`
- **Given**: 实施完成后运行质量门
- **When**: 运行 `invoke gates.toctrees` 与 `invoke gates.bundles`
- **Then**: 两门均退出码 0；toctrees 零断链、零孤立文档；bundles 五面对账一致
- **Pass Condition**: 两条命令均无报错输出
- **Evidence**: 命令退出码与输出

### AC-3: 索引同步（rule）
- **Type**: `rule`
- **Given**: 新增束 male-charm-eq 至既有分组 personal-growth
- **When**: 检查 `sheke/personal-growth/index.md`、`sheke/index.md` 与 `doc/bundles/index.md`
- **Then**: `personal-growth/index.md` 束数 1→2 并 toctree 引用两束；`sheke/index.md` 分组表束数 1→2；总索引 frontmatter（total_bundles=537、groups=59）、计数行「537 个知识包 / 9 个学科域、59 个分组」、sheke 域节标题「37 束 · 7 组」、分组表束数列、末尾 toctree 全部同步
- **Pass Condition**: 五面与目录树地面真值一致（由 AC-2 的 gates.bundles 覆盖）
- **Evidence**: gates.bundles 输出 + 索引文件 Read 核对

### AC-4: 内容质量（rubric）
- **Type**: `rubric`
- **Dimension**: 内容质量五维（证据分级 / 反常识批判 / 男性视角针对性 / 实操可落地 / 信源可溯源）
- **Scale**: 1-5
- **Anchors**: 1 = 内容堆砌、无证据标注、无实操；3 = 有证据分级但部分缺失、实操有描述但缺模板、批判视角不全、男性视角薄弱；5 = 全篇证据分级明确、Manosphere/PUA/power posing 批判如实呈现、男性社会化维度（男孩不许哭/脆弱性/述情障碍）有专门覆盖、实操含可直接复用的句式/模板/训练步骤、facts.md 每条可溯源
- **Pass Threshold**: >= 4
- **Evidence**: 逐篇 Read 抽查 + facts.md 溯源核对

### AC-5: 落盘位置（rule）
- **Type**: `rule`
- **Given**: 产出物应位于用户指定的文档库
- **When**: 检查 bundle 实际路径
- **Then**: bundle 位于 `projects/awesome-okf-xs/doc/bundles/sheke/personal-growth/male-charm-eq/`，且 `personal-growth/index.md`、`sheke/index.md`、`doc/bundles/index.md` 已登记新束
- **Pass Condition**: 路径与登记一致
- **Evidence**: Glob 路径核对

## Open Questions

- [x] 是否需要在实施阶段补充中文通俗读物——已处理：references/00-books.md 通俗层已纳入蔡康永《情商课》同级男性向作品口径，与女性版一致，无需额外条目。
