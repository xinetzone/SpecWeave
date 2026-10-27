---
status: "draft"
title: "从帛书《老子》视角分析 Xuanspace（玄境）并产出项目蓝图与优化建议书"
change-id: "analyze-xuanspace-through-boshu-laozi"
---

# 从帛书《老子》视角分析 Xuanspace（玄境）并产出项目蓝图与优化建议书

> **方法论编排**：`seven-concepts-cmd`（七概念，场景 4「知识沉淀」链路 R → I → E → F → V → C）+ `dao-san-triads`（三之位诊断）
> **Session**：`sc-20261027-xuanspace-boshu-blueprint`
> **目标落盘目录**：`projects/xuanspace/doc/`
> **规格交付约定**：本文档集以 `spec.md` + `tasks.md` + `review.md` 交付（与 `.trae/specs/README.md` 的「spec.md + tasks.md + review.md」三件套约定一致）。

## Why

Xuanspace（玄境）自述「技术为器、思想为道、器以载道」，并在其 README 中以「道—法—术—器」四层架构图组织自身（见 [README.md](../../../../projects/xuanspace/README.md)）。但项目当前只有面向使用的「指南类」文档（`doc/intro.md`、`doc/build-system.md`、`doc/architecture.md` 等），**缺少一份从思想层反观自身结构与治理的整体蓝图**，也**缺少一份把现状问题收敛为可执行动作的优化建议书**。

本变更以帛书《老子》（马王堆甲本/乙本为主，郭店楚简本等对照）为思想透镜，对 `projects/xuanspace` 做结构化分析与洞察，补齐上述两份文档。

## What Changes

- 新增《项目蓝图》文档：置于 `projects/xuanspace/doc/` 下，承载事实底稿、洞察、第一性原理与「三之位」诊断、目标态蓝图与演进路线。
- 新增《优化建议书》文档：置于同一目录，承载分级（P0/P1/P2）建议，每条含判据、现状证据、期望态、落地动作与验证方式。
- 修改 `projects/xuanspace/doc/index.md`：把两份新文档登记进 toctree，保证 Sphinx 可解析、不产生 orphan。
- **BREAKING**：无。纯新增文档 + 一次 toctree 登记，不改任何代码、配置、CI 或既有结论性内容。

## Impact

- **Affected specs**：新建 change-id `analyze-xuanspace-through-boshu-laozi`，不修改 `.trae/specs/` 下任何既有 spec。
- **Affected code**：仅 `projects/xuanspace/doc/`（Sphinx 文档源）——两份新 Markdown + `index.md` 一处 toctree。**不改** 任何 `.py`、`pyproject.toml`、`.github/workflows/`、`AGENTS.md`。
- **只读引用（零写入）**：`projects/awesome-okf-xs/doc/bundles/guoxue/laozi/**`（帛书老子知识底座，含 `boshu-reading/`、`dao-san-triads/`、`laozi-lineage/`、`laozi-works/`）。
- **授权边界登记**：`projects/AGENTS.md` 默认声明 `projects/` 下 git submodule「❌ 不可直接修改」；本次由用户显式授权写入 `projects/xuanspace/doc`。授权范围为**生成文档**，**不包含 git 提交与推送**。

## Overview

- **Summary**：以帛书《老子》为思想透镜，对 `projects/xuanspace` 做「事实 → 洞察 → 第一性原理 → 三之位诊断 → 蓝图 → 建议」的分析与洞察，产出两份中文文档，落盘 `projects/xuanspace/doc/` 并登记进 Sphinx toctree。
- **Purpose**：让项目的「思想层」不再是口号，而成为可对照、可检验、可演进的自我描述；同时把观察到的结构性问题收敛成带判据的可执行建议。
- **Target Users**：xuanspace 维护者（xinetzone）、项目贡献者、参与该项目的 AI 智能体。

## Goals

- **G1**：交付一份《项目蓝图》，含「道—法—术—器」四层解构、现状能力地图、目标态蓝图与演进路线。
- **G2**：交付一份《优化建议书》，含分级建议条目，每条可判定、可落地、可验证。
- **G3**：方法论合规——按七概念编排（事实 → 洞察 → 第一性原理 → 对抗审查 → 沉淀）执行，并以「三之位」框架做一次项目级诊断。
- **G4**：哲学纪律合规——版本标注、结构类比与影响关系的区分、不附会古人、不做命运断言。
- **G5**：文档可被 Sphinx 正常构建并被 toctree 收录，链接零断链。

## Non-Goals

- 不修改 xuanspace 的任何代码、配置、CI、模板或既有文档结论（除 `doc/index.md` 的 toctree 登记）。
- 不执行《优化建议书》中的任何建议（本变更只产出建议，不落地重构）。
- 不提交、不推送、不创建 tag、不动 `projects/xuanspace` 的 git 历史。
- 不写入 `projects/xuanspace` 之外的任何路径；不修改 `projects/awesome-okf-xs`（只读 submodule）。
- 不做《老子》逐章校勘、不做全书记载梳理（范围限于第四十二章及必要对照章句）。
- 不提供医疗/心理/法律/财税/投资类专业建议；不做个人命运断言。
- 不为 xuanspace 添加 YAML frontmatter 或 `.meta/toml/` 元数据文件（见约束 C-3）。

## Background & Context

- xuanspace 定位为「技术与文化项目共存的空间」，其 README 明确以「技术为器、思想为道、器以载道」为理念，并以「道—法—术—器」四层架构图组织自身；`doc/architecture.md`、`doc/build-system.md`、`doc/cli/`、`doc/okf/` 提供面向使用的说明。
- xuanspace 根 `AGENTS.md`、`CONTRIBUTING.md`、`.agents/`（`frontmatter.md`、`context-routing.md`、`global-core-rules.md`）、`.github/workflows/ci.yml`、`pyproject.toml`、`tools/xs`、`tools/okf`、`tools/templates`、`libs/*`、`vendor/*`（子模块）构成本次分析的事实来源。
- **帛书《老子》知识底座（唯一可信源，只读）**：`projects/awesome-okf-xs/doc/bundles/guoxue/laozi/` 下 `boshu-reading/`（甲乙本异文对照范式）、`dao-san-triads/`（六类「三」谱系 + 第五义关系位 + 七条生存指南 + 「三之位」模式）、`laozi-lineage/`（版本谱系与禁忌字断代）、`laozi-works/`（文本与注疏）。
- **纪律前提（必须显式声明）**：《老子》与 xuanspace 之间**只存在结构类比，不存在历史影响关系**；项目自述的「道—法—术—器」是项目自身的现代重构，**不等于**帛书《老子》原典体系，分析中不得反向声称「老子早就说了」。
- **声明一致性线索（待核验，非预设缺陷）**：`doc/README.md` 首段与目录树示例使用 `docs/`，而同文件第 83/86/89 行与 `doc/conf.py` 使用 `doc/`；`README.md` 称 `xs` 有「15 个子命令」，而 `tools/xs/src/xs/commands/` 现有 12 个命令模块。以上均为**分析线索**，须在事实采集阶段用文件内容核验后再决定是否列为建议，**禁止在核验前断言为缺陷**。

## Functional Requirements

- **FR-1**：《项目蓝图》文档须落盘 `projects/xuanspace/doc/` 下，为纯 Markdown（可含 Mermaid），结构不少于：项目定位 → 「道—法—术—器」四层解构 → 现状能力地图 → 「三之位」诊断 → 目标态蓝图 → 演进路线。
- **FR-2**：《项目蓝图》的「道—法—术—器」解构须**逐层给出**：该层在 xuanspace 中的对应实体（文件/目录/机制，带相对路径引用）+ 该层承载的功能 + 该层的薄弱环节。每层须标注「结构类比，非影响关系」。
- **FR-3**：《优化建议书》文档须落盘同目录，为纯 Markdown，结构不少于：分级建议清单（P0/P1/P2）→ 每条建议的完整字段 → 汇总与优先级依据。
- **FR-4**：建议书每条建议须含五要素：**判据**（可判定陈述）+ **现状证据**（相对路径 `#L起-L止` 逐字引用）+ **期望态** + **落地动作**（谁做什么） + **验证方式**（可复跑命令或可观察结果）。
- **FR-5**：洞察须以四元组表达（**陈述 + 证据 + 反常识 + 行动**），维度互不重叠，且 **≥2 条挑战默认假设**。
- **FR-6**：须使用「三之位」框架执行一次项目级诊断，五步齐备（命名二 → 找关系位 → 检验非实体性 → 表述为关系 → 落地动作），并**显式规避 ≥1 个列出的反模式**（不得把第三项当实体、不得跳过「二」直接谈「三」、不得用「第三项」回避选择、不得把结构类比当史实来源、不得停在「二」无限细分）。
- **FR-7**：须通过「三问检验」自查（第三项能否用「如何连接/为何整体」表述；是否识别并规避至少一个反模式；连接方式是否已写成具体动作），并把自查结果写入蓝图。
- **FR-8**：**版本纪律**——每处《老子》引文必须标注版本（马王堆**甲本**／**乙本**／**今本**／**郭店楚简本**之一），**禁止**笼统写「帛书本」；遇甲本损掩处须标注。引文须与知识底座正文一致，不得转述失真。
- **FR-9**：**溯源纪律**——所有关于 xuanspace 现状的事实性陈述必须带相对路径引用（文件为最小单位，关键处到行号）；不得出现无来源的现状断言。
- **FR-10**：两份文档须登记进 `projects/xuanspace/doc/index.md` 的 toctree（新增一个「规划」或等价 caption 分组），且不得破坏现有四个 toctree 的条目与顺序。
- **FR-11**：**xuanspace 当前阶段约束**——两份文档**不添加 YAML frontmatter**、**不创建 `.meta/toml/` 元数据文件**（依 `projects/xuanspace/.agents/rules/frontmatter.md` 中「Task 20 之前」的现行约束）；文档以 H1 开头。
- **FR-12**：建议条目**禁止「正确的废话」**——不得出现「要接纳自己」「要坚持」「需持续优化」这类无判据、无法执行的表述；每条建议必须能被判断为「已做/未做」。

## Non-Functional Requirements

- **NFR-1（语言与术语）**：全部内容为简体中文；同一概念在蓝图与建议书中用词一致；代码、路径、命令、函数签名保留英文原样。
- **NFR-2（可构建）**：在 `projects/xuanspace` 内执行 Sphinx HTML 构建（`pdm run sphinx-build -b html doc/ doc/_build/html` 或等效命令）后，新增文档**不引入新告警/错误**（尤其不得出现 toctree 未收录导致的 orphan 警告）。
- **NFR-3（链接）**：新增与修改文件经 `check-links.py` 校验，**0 断链**；文档内交叉引用一律使用**相对路径**，禁止 `file:///` 绝对路径，禁止引用 `.temp/` 路径。
- **NFR-4（写入边界）**：写入范围严格限定为 `projects/xuanspace/doc/`；不得写入 `projects/xuanspace` 其他目录；不得写入 `projects/awesome-okf-xs`（只读）。
- **NFR-5（无副作用）**：全程不产生 git commit / push / tag；完成后 `projects/xuanspace` 的 git 历史与 HEAD 不变。
- **NFR-6（可读性）**：层级不跳级；表格列数与分隔符一致；Mermaid 图语法正确且经 `check_mermaid.py` 校验；单份文档保持清晰可导航的章节结构。

## Constraints

- **C-1 Technical**：文档源为 `projects/xuanspace/doc/`（git submodule 内）；Sphinx 配置 `path_to_docs = "doc"`，`master_doc = "index"`；构建依赖包括 Sphinx + MyST + `mystx` + `sphinx-book-theme`。
- **C-2 Technical**：Mermaid 语法须符合 `.agents/rules/` 中的 Mermaid 安全编码规则并通过 `check_mermaid.py`。
- **C-3 Technical**：xuanspace 文档当前阶段**禁用** YAML frontmatter 与 `.meta/toml/` 元数据（`projects/xuanspace/.agents/rules/frontmatter.md`）。**须在 Task 1 中复核该约束是否仍然有效**；若已过 Task 20，则该约束失效并须回到本 spec 更新 FR-11。
- **C-4 Business**：写入 `projects/xuanspace/doc` 由用户显式授权，覆盖 `projects/AGENTS.md` 的默认「子模块不可直接修改」边界；授权不含提交/推送。
- **C-5 Dependencies**：只读依赖 `projects/awesome-okf-xs/doc/bundles/guoxue/laozi/**`；该 submodule 若处于 rebase 中间态则禁止任何写操作（本次不写，仅读取）。
- **C-6 交付约定**：本次交付 `spec.md` + `tasks.md` + `review.md` 三件套（`review.md` 承载验收检查点与独立审查记录）。

## Assumptions

- 用户授权指「允许在该目录生成文档」，**不包含** git 提交、推送或变更 submodule 指针。
- `projects/awesome-okf-xs/doc/bundles/guoxue/laozi/**` 可作为《老子》相关概念与引文的**唯一可信源**，且可只读引用。
- xuanspace 当前处于 `frontmatter.md` 所述「Task 20 之前」阶段（此假设须在 Task 1 核验，见 C-3）。
- xuanspace 工作树相对干净，基线 HEAD 可作为事实采集的参照点（须在 Task 1 记录实际 HEAD）。
- 用户期望两份文档为**两份独立文件**（而非合并文件）。

## Acceptance Criteria

### AC-1: 两份文档已落盘指定目录
- **Type**: `rule`
- **Given**: 实施完成
- **When**: 列出 `projects/xuanspace/doc/` 目录
- **Then**: 存在《项目蓝图》与《优化建议书》两份 Markdown 文档
- **Pass Condition**: 两个文件均存在且非空，且不新增 `.meta/toml/` 文件
- **Evidence**: 目录列表 + 文件头部内容

### AC-2: toctree 登记且 Sphinx 可解析
- **Type**: `rule`
- **Given**: 两份文档已落盘
- **When**: 查看 `projects/xuanspace/doc/index.md` 并执行 Sphinx HTML 构建
- **Then**: 两份文档出现在 toctree 中，构建成功且**无新增 orphan / 未收录告警**
- **Pass Condition**: 构建命令返回成功；构建日志中无指向新增文档的 warning
- **Evidence**: `index.md` 相关片段 + 构建命令与输出摘要

### AC-3: 《老子》引文版本标注完整
- **Type**: `rule`
- **Given**: 两份文档已完成
- **When**: 检索文档中所有《老子》引文
- **Then**: 每处引文均带版本标注（甲本/乙本/今本/郭店楚简本），无任何笼统的「帛书本」表述
- **Pass Condition**: 面向「帛书本」的检索命中 0 次（作为引文版本的替代表述）；抽查 ≥3 处引文与知识底座正文逐字一致
- **Evidence**: 检索命令与结果 + 抽查对照记录

### AC-4: 现状事实陈述均可溯源
- **Type**: `rule`
- **Given**: 文档中含关于 xuanspace 现状的陈述
- **When**: 抽查 ≥8 条事实性陈述
- **Then**: 每条均带相对路径（关键处含行号）引用，且引用的文件与内容真实存在
- **Pass Condition**: 抽查 8 条全部可解析，0 条无引用
- **Evidence**: 抽查清单（陈述 → 引用 → 核验结果）

### AC-5: 建议条目可判定
- **Type**: `rule`
- **Given**: 《优化建议书》已完成
- **When**: 逐条检查建议条目
- **Then**: 每条均具备「判据 + 现状证据 + 期望态 + 落地动作 + 验证方式」五要素
- **Pass Condition**: 五要素齐备率 100%；无「正确的废话」条目（判据为空或不可判定者计为不通过）
- **Evidence**: 建议条目五要素矩阵

### AC-6: 未越界写入、无 git 副作用
- **Type**: `rule`
- **Given**: 实施完成
- **When**: 在 `projects/xuanspace` 与 SpecWeave 主仓执行 `git status`
- **Then**: 变更仅限于 `doc/` 下三处（两份新文档 + `index.md`）；无新增 commit / 无 push；`awesome-okf-xs` 无任何变更
- **Pass Condition**: `git status` 输出符合上述范围；`git log -1` 与采集时记录的 HEAD 一致
- **Evidence**: 两个仓库的 `git status` 与 `git log -1` 输出

### AC-7: 链接与图表门禁通过
- **Type**: `rule`
- **Given**: 文档已落盘
- **When**: 运行 `check-links.py` 与 `check_mermaid.py`
- **Then**: 新增/修改文件 0 断链；Mermaid 语法校验通过
- **Pass Condition**: 两个脚本退出码为 0（或输出中与本次变更相关的失败项为 0）
- **Evidence**: 两个命令的输出

### AC-8: 蓝图「道—法—术—器」解构深度
- **Type**: `rubric`
- **Dimension**: 四层解构与 xuanspace 实际结构的贴合度与深度（是否每层都给出具体实体、承载功能与薄弱环节，而非泛泛而谈）
- **Scale**: 1-5
- **Anchors**: 1 = 只有四层名称与空泛描述，无具体文件/目录对应；3 = 四层均有具体实体对应，但薄弱环节笼统或缺「结构类比」声明；5 = 四层各有可核验的实体引用、明确承载功能、具体薄弱环节，且每层显式标注「结构类比，非影响关系」
- **Pass Threshold**: >= 4
- **Evidence**: 蓝图「道—法—术—器」章节内容 + 对照引用

### AC-9: 建议书可执行性与判据强度
- **Type**: `rubric`
- **Dimension**: 建议的可执行性与判据强度（能否被判定为「已做/未做」，动作是否具体到可执行）
- **Scale**: 1-5
- **Anchors**: 1 = 多数建议为口号式表述，无判据；3 = 每条有判据但动作笼统，验证方式依赖人工主观；5 = 每条判据可当场判定、动作具体到文件/命令层面、验证方式可复跑，且优先级依据明确
- **Pass Threshold**: >= 4
- **Evidence**: 建议条目清单 + 判据/验证方式抽查

### AC-10: 洞察质量与反常识性
- **Type**: `rubric`
- **Dimension**: 洞察四元组质量与反常识性（陈述是否非显然、证据是否支撑、反常识点是否有据、行动是否可落地）
- **Scale**: 1-5
- **Anchors**: 1 = 洞察实为常识复述，无证据或反常识点为空；3 = 洞察成立但反常识点牵强或维度有重叠，反常识条目 < 2；5 = ≥3 条洞察维度互不重叠、证据充分、**≥2 条挑战默认假设**且反常识点有明确证据支撑
- **Pass Threshold**: >= 4
- **Evidence**: 洞察清单 + 逐条证据对照

### AC-11: 「三之位」诊断合规
- **Type**: `rule`
- **Given**: 蓝图含「三之位」诊断章节
- **When**: 检查该章节
- **Then**: 五步齐备（命名二 / 找关系位 / 检验非实体性 / 表述为关系 / 落地动作）；显式规避 ≥1 个反模式；「三问检验」自查结果已写入
- **Pass Condition**: 五步与三问检验均可逐项指出；规避的反模式被明确点名
- **Evidence**: 诊断章节原文

## Open Questions

- [ ] 两份文档的最终文件名是否采用 `blueprint.md` + `recommendations.md`？还是使用中文名或其他命名？（默认取前者，Sphinx 文件名保持 ASCII）
- [ ] toctree 新分组的 caption 用「规划」还是「蓝图与规划」？（默认取「规划」）
- [ ] 是否需要在实施后由用户在 `projects/xuanspace` 内自行提交（本次默认不提交、不推送）？
- [ ] 若 Task 1 核验发现 xuanspace 已过 Task 20（frontmatter 约束失效），是否改为按 `.meta/toml/` 二分法补齐元数据？（默认：仍不加，除非用户明确要求）
- [ ] 《优化建议书》中的 P0 建议是否允许随本次一并落地？（默认：不落地，仅产出建议）

## 后续变更（规格完成后的独立授权）

本规格的 **Non-Goals** 与 **Assumptions** 中「不提交、不推送、不落地建议、不变更 submodule 指针」诸条，范围是**本次规格任务自身**（Task 1–7），已如实履行（核验见 [review.md](review.md) 第八节）。

规格完成后，用户**另行授权**落地《优化建议书》**P0-1**（统一根文档目录命名口径为 `doc/`）。该动作超出本规格的授权边界，故不在本文件改写 Non-Goals，而是另记：

- [tasks.md](tasks.md) → 「后续任务：P0-1 落地」Task 8（含提交记录）
- [review.md](review.md) → 「十、P0-1 落地证据」（含门禁核验与过程发现）

涉及提交：`projects/xuanspace` 的 `207256c`、`aed2e5b`、`cc5c5b1`，以及根仓 `b86f2a98e`（子模块指针）。未 push、未 tag。
