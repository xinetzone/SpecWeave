# 提高女性魅力与情商 OKF 知识包 - Product Requirements Document

## Overview

- **Summary**: 在 `projects/awesome-okf-xs/doc/bundles/sheke/` 下新建分组 `personal-growth/`（个人成长与自我提升），并新建 OKF bundle `female-charm-eq/`（女性魅力与情商），系统化呈现「魅力（charm）+ 情商（EQ）」的理论与实操知识。
- **Purpose**: 将公开的吸引力心理学、情商科学、沟通/界限/自信等实操知识，按 OKF v0.2 格式沉淀为可检索、可溯源、证据分级的中文知识包，供自学者系统提升人际魅力与情绪能力。
- **Target Users**: 希望提升人际魅力与情绪能力的女性读者；OKF 文档库读者；对证据分级（学界共识/单一研究/通俗主张）敏感的自学者。

## Goals

- 以「能力模型（Salovey/Mayer/MSCEIT）vs 混合模型（Goleman）」为骨架完整呈现情商理论，并如实呈现学术争议。
- 以吸引力科学、魅力三要素、第一印象/自我呈现理论呈现魅力科学。
- 提供可落地的实操：沟通倾听、界限设定、自信训练、职场应用、亲密关系与约会场景。
- 对每个关键主张做证据分级，明确标注被夸大的技巧（power posing、吊桥效应等）与反常识点。
- 全部文档遵循 OKF v0.2 frontmatter 规范，通过 toctree / bundles 索引质量门。

## Non-Goals

- 不提供医美、化妆、整容等外形改造建议。
- 不覆盖心理咨询、临床心理干预。
- 不推荐具体对象、不涉及择偶市场操作。
- 不采集私域内容（全部为公开信源）。

## Background & Context

- R 阶段（事实采集）已完成：三个并行调研子代理返回三份可溯源事实清单——魅力理论 26 条（F-01~F-26）、情商理论 27 条（F1~F27）、实操 28 条（F1~F28），来源含 JPSP、Frontiers、Gross/Goleman/Neff 等文献与公开书页。
- 落盘位置决策：`relationships/` 分组定位为「经典著作解读」；本主题为综合方法论教程，语义上应独立分组。新建 `sheke/personal-growth/`（组=1 束，锚点组模式与 finance/marketing 同构）。
- 知识库治理规则（awesome-okf-xs AGENTS.md）：新增 bundle 后必须同步 `sheke/index.md` 与总索引 `bundles/index.md` 五面计数，并通过 `invoke gates.toctrees`、`invoke gates.bundles`。

## Functional Requirements

- **FR-1**: bundle 采用三层结构 `concepts/` + `examples/` + `references/`，附工作文档 `facts.md`、`insights.md`、`log.md`。
- **FR-2**: 每个非保留 `.md` 文件携带 OKF v0.2 YAML frontmatter，`type` 字段非空；bundle 根 `index.md` 以 `{toctree}` 引用全部内容文档。
- **FR-3**: `facts.md` 汇总全部事实编号（F-xxx），每条可回溯到 `sources` 信源。
- **FR-4**: 分组 `sheke/personal-growth/index.md` 以 `{toctree}` 引用 bundle 根 index。
- **FR-5**: `sheke/index.md` 分组导航表新增 personal-growth 行；总索引 `bundles/index.md` 五面对账（frontmatter / 计数行 / 域节标题 / 分组表束数列 / toctree）同步更新。

## Non-Functional Requirements

- **NFR-1**: 证据分级标注——每个理论主张标注「学界共识/单一研究/通俗主张/自媒体经验」。
- **NFR-2**: 批判视角——被夸大技巧（power posing、吊桥效应）与 Goleman 断言争议必须如实呈现，禁止写成共识。
- **NFR-3**: 反物化、反取悦——实操部分强调真实、自尊、界限，不写「取悦他人」导向。
- **NFR-4**: 文档为 UTF-8 编码；文件名 kebab-case 纯英文；正文中文。

## Constraints

- **Technical**: 遵循 OKF v0.2 frontmatter 规范（.agents/rules/frontmatter.md）；日期裸格式由 doc/conf.py 钩子处理，无需加引号。
- **Business**: 项目为 git submodule（projects/awesome-okf-xs），修改走子项目开发流程（本次为用户明确指定的产出物，直接在子项目内落盘）。
- **Dependencies**: 质量门脚本 `scripts/check-toctrees.py`、`scripts/check-bundles-index.py`（依赖目录树与总索引五面一致）。

## Assumptions

- 用户期望的知识包规模对标既有同类教程（如 marketing-fundamentals：8 概念 + 3 示例 + 1 参考）。
- 三份调研事实清单可直接作为 facts.md 的事实基础，实施阶段可小幅增补信源但不得引入未核验事实。
- `.trae/specs/female-charm-eq/` 为本工作流的规划产物区，bundle 本体落在 `doc/bundles/sheke/personal-growth/female-charm-eq/`。

## Acceptance Criteria

### AC-1: Bundle 目录结构与 OKF 规范合规（rule）
- **Type**: `rule`
- **Given**: bundle 落盘于 `sheke/personal-growth/female-charm-eq/`
- **When**: 检查目录树与全部 `.md` 文件
- **Then**: 存在 `concepts/`、`examples/`、`references/` 三层及各自 `index.md`；bundle 根 `index.md` 与三个子目录 `index.md` 均以 `{toctree}` 引用内容文档；所有非保留 `.md` 文件 frontmatter 含非空 `type`；存在 `facts.md`、`insights.md`、`log.md`
- **Pass Condition**: 目录树与 frontmatter 检查全部通过
- **Evidence**: `Glob`/`Read` 检查结果；`invoke gates.toctrees` 输出

### AC-2: 质量门通过（rule）
- **Type**: `rule`
- **Given**: 实施完成后运行质量门
- **When**: 运行 `invoke gates.toctrees` 与 `invoke gates.bundles`（等价 `python scripts/check-toctrees.py`、`python scripts/check-bundles-index.py`）
- **Then**: 两门均退出码 0；toctrees 零断链、零孤立文档；bundles 五面对账一致
- **Pass Condition**: 两条命令均无报错输出
- **Evidence**: 命令退出码与输出

### AC-3: 索引同步（rule）
- **Type**: `rule`
- **Given**: 新增分组 personal-growth 与束 female-charm-eq
- **When**: 检查 `sheke/index.md` 与 `doc/bundles/index.md`
- **Then**: `sheke/index.md` 分组表含 personal-growth 行并列入 toctree；总索引 frontmatter（total_bundles=535、groups=59）、计数行「535 个知识包 / 9 个学科域、59 个分组」、sheke 域节标题「36 束 · 7 组」、分组表束数列、末尾 toctree 全部同步
- **Pass Condition**: 五面与目录树地面真值一致（由 AC-2 的 gates.bundles 覆盖）
- **Evidence**: gates.bundles 输出 + 索引文件 Read 核对

### AC-4: 内容质量（rubric）
- **Type**: `rubric`
- **Dimension**: 内容质量四维（证据分级 / 反常识批判 / 实操可落地 / 信源可溯源）
- **Scale**: 1-5
- **Anchors**: 1 = 内容堆砌、无证据标注、无实操；3 = 有证据分级但部分缺失、实操有描述但缺模板/步骤、批判视角不全；5 = 全篇证据分级明确、Goleman 争议与 power posing 等批判如实呈现、实操含可直接复用的脚本/模板/训练步骤、facts.md 每条可溯源
- **Pass Threshold**: >= 4
- **Evidence**: 逐篇 Read 抽查 + facts.md 溯源核对

### AC-5: 落盘位置（rule）
- **Type**: `rule`
- **Given**: 产出物应位于用户指定的文档库
- **When**: 检查 bundle 实际路径
- **Then**: bundle 位于 `projects/awesome-okf-xs/doc/bundles/sheke/personal-growth/female-charm-eq/`，且 `sheke/index.md`、`doc/bundles/index.md` 已登记新分组
- **Pass Condition**: 路径与登记一致
- **Evidence**: Glob 路径核对

## Open Questions

- [ ] 是否需要在实施阶段补充中文通俗读物（蔡康永《情商课》）作为独立 references 条目——默认以「通俗主张」层级列入信源清单。
