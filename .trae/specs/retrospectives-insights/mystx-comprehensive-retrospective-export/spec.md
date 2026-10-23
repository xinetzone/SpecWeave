---
title: "mystx 主题包全面复盘 + 可优化点萃取 + 报告导出"
status: "draft"
id: "mystx-comprehensive-retrospective-export"
methodology: "seven-concepts (R→I→E→V→A→C)"
content-sensitivity: "public"
source: "d:/spaces/SpecWeave/projects/xuanspace/libs/mystx"
---

# mystx 主题包全面复盘 + 可优化点萃取 + 报告导出 Spec

## Why

`mystx`（`d:/spaces/SpecWeave/projects/xuanspace/libs/mystx`）是一个已公开发布到 PyPI、Read the Docs 与 GitHub 的 Sphinx HTML 主题包，自 2026-08-21 首次提交至今累计 32 次提交、发布 13 个 tag（最新 `v0.3.8`），HEAD 停在 `45bd1e4`。它是 `projects/xuanspace` monorepo 下的 git submodule，与 `awesome-okf-xs` 等第一方知识工程资产共用同一套 Sphinx 文档体系。

该子包此前从未被独立复盘过：`.trae/specs` 中与 mystx 相关的 4 个既有 spec 分别属于工具层萃取（`sphinx-config-mystx-extraction`）、Python 3.14 标准库优化（`optimize-mystx-python314-stdlib`）与知识包构建（`laozi-zhudu-mystx-wiki`）；父项目 `xuanspace` 的全面复盘（`retrospective-xuanspace-comprehensive-20261010`）仅以 F-056/F-057/F-059 三条事实间接覆盖了 mystx 的打包门禁、子模块指针与文档配置治理，**未对 mystx 自身的工程质量做系统扫描**。

在初步勘查中已发现多处可验证的口径不一致与工程债信号：README「核心依赖」段声称 `sphinx-book-theme>=1.1.4`、`sphinx>=8.0.0`、`myst-nb`、`myst-parser` 为核心依赖，而 `pyproject.toml` 中 `dependencies = []`（这四项实际位于 `[docs]` 可选组）；CHANGELOG 仅记录 `v0.3.8` 一个版本，缺 `v0.3.1`\~`v0.3.7` 历史条目与 Unreleased 段（git tag 显示 v0.3.1/v0.3.2/v0.3.3/v0.3.4/v0.3.7/v0.3.8 存在）；`pyproject.toml` 无 `[tool.coverage]` 配置段，覆盖率基线无法可复现测量；`[project.optional-dependencies]` 的 docs/test/lint/build/tasks/dev 六组与 `[dependency-groups]` 的同名组内容高度重复；`tasks` 组声明了疑似无效的包名 `invocations>=3.0`；仓库根 `tasks.py` 与 `src/mystx/tasks/` 存在双入口；`src/mystx/tools/__init__.py` 为 0 字节空文件；`doc/_ext/sphinx_docx/writer.py` 单文件 901 行且为内嵌的第三方实现。这些均为待取证线索，须经 R→I→E→V 完整链路验证后方可成为结论。

本 Spec 的目标是以七概念方法论对 mystx 做一次**证据可回溯、结论可迁移、行动项可判定**的全面复盘，并把「可以优化的点」从主观感受转化为带 F 编号溯源的事实清单、带四元组的根因洞察、过 G3 门的可迁移模式与带验收标准的原子行动项，最终归档为可被后续迭代直接消费的报告。

## What Changes

* **不修改 mystx 任何文件**：本 Spec 只产出复盘资产（spec 目录中间产物 + `docs/retrospective/reports/` 报告四件套 + 方法论模式库入库），不向 `projects/xuanspace` 写入或回滚任何内容。mystx 是 xuanspace 的 submodule，xuanspace 又是 SpecWeave 的 submodule——两级只读边界。

* **R 阶段事实采集**：以 `mystx` HEAD `45bd1e4` 为基线，采集仓库结构、构建/依赖/打包配置、CI/CD 配置、测试资产、提交历史、文档资产、主题资产等客观事实，输出 `facts.md`（F-001 起连续编号），通过 G1 门（无因果推断词）。

* **I 阶段洞察萃取**：基于事实清单做 5-Whys 根因分析，产出 ≥3 条四元组洞察（现象/根因/影响/建议），每条引用 ≥2 个 F 编号；对照父项目 `xuanspace` 既有复盘基线做差异分析（强化/反转/新增/无变化），输出 `insights.md`，通过 G2 门。

* **E 阶段模式萃取**：从洞察中提炼 ≥1 个可迁移模式（触发场景/核心步骤/反模式/迁移验证四要素），并与既有方法论模式库做去重裁决（新建 L1 / 并入既有 / 不入库三选一），输出 `e-stage-pattern.md`，通过 G3 门。

* **V 阶段对抗审查**：以魔鬼代言人/新人/老板/未来四视角审查全部中间产物，产出 ≥5 条意见、采纳 ≥2 条并留下可定位修正痕迹，其中至少 1 条须指向「事实证据强度不足」，输出 `v-adversarial-review.md`。

* **A 阶段行动项**：产出 ≥3 条原子行动项，每条含优先级/Owner/触发条件/可判定验收标准，禁止「加强沟通」式空话，通过 G4 门。

* **报告归档**：在 `docs/retrospective/reports/project-reports/retrospective-mystx-comprehensive-20261022/` 产出四文件（`README.md` 主报告 / `insight-extraction.md` / `actionable-items.md` / `index.md`），并在两处索引登记。

* **模式入库**：若 E 阶段裁决为「新建 L1」，则按四处登记落盘（域目录模式文档 + `.meta/toml/` 伴生 TOML + 域 `index.md` toctree + `methodology-patterns/index.md` 模式清单总表）。

* **独立审查**：委派 fresh-context 只读子代理对全部产出物做独立审查，P0 问题必须修复并回归。

## Impact

* **Affected specs**：无既有 spec 被修改或破坏；本 Spec 是对 mystx 的**只读审计 + 新增复盘资产**，不改变 mystx 任何运行时行为。

* **Affected code**（只读对象，不修改）：

  * `projects/xuanspace/libs/mystx/src/mystx/**`（`__init__.py` 67 行 / `config.py` 158 行 / `configs.py` 73 行 / `extensions.py` 69 行 / `themes.py` 96 行 / `myst_compat.py` 104 行 / `utils.py` 38 行 / `version_switcher.py` 71 行 / `presets/` / `tasks/` / `ext/github_readme_stats/` / `theme/mystx/`）

  * `projects/xuanspace/libs/mystx/pyproject.toml`（246 行）、`README.md`（169 行）、`CHANGELOG.md`（18 行）、`tasks.py`（13 行）

  * `projects/xuanspace/libs/mystx/tests/unit/**`（9 文件 51 个 test 函数（据 F-049，`ast` 脚本实测；原任务书所述 59 与实测不符））

  * `projects/xuanspace/libs/mystx/.github/workflows/**`（lint.yml / pages.yml / python-publish.yml）、`.readthedocs.yml`、`.pre-commit-config.yaml`

  * `projects/xuanspace/libs/mystx/doc/**`（`conf.py` 283 行 / `_ext/sphinx_docx/writer.py` 901 行 等）

* **Affected docs**（新增，位于 SpecWeave 主仓）：

  * `.trae/specs/retrospectives-insights/mystx-comprehensive-retrospective-export/`（spec.md + tasks.md + 阶段中间产物）

  * `docs/retrospective/reports/project-reports/retrospective-mystx-comprehensive-20261022/`（报告四件套）

  * `docs/retrospective/patterns/methodology-patterns/**`（条件性：仅当 E 阶段裁决为新建 L1）

* **测试基线**：不修改 mystx 代码，故 mystx 现有测试基线（51 个 test 函数（据 F-049，`ast` 脚本实测；原任务书所述 59 与实测不符））不受影响；本次任务的「测试」体现为报告与事实清单的可核验性（`check-links.py` 链接门禁 + 索引可达性 + 抽样回溯命中率）。

* **只读边界**：全程不写入 `projects/xuanspace`，不执行任何回滚；如复盘期间该目录出现并行会话的在途改动，如实标注时点与归因，不计入本次结论。

## Goals

* **G1（事实基线）**：以 F-001 起连续编号采集 ≥30 条客观事实，覆盖仓库结构、构建与依赖配置、测试资产、CI/CD、提交节奏、文档与主题资产，每条可回溯到具体文件路径 / git commit / 命令输出；通过 G1 门（因果推断词 Grep 为空或仅引述）。

* **G2（洞察深度）**：产出 ≥3 条四元组洞察，每条引用 ≥2 个 F 编号，根因表述触及系统性层面而非现象复述；含与父项目 `xuanspace` 复盘基线的差异分析（逐条标注强化/反转/新增/无变化）。

* **G3（模式可迁移）**：产出 ≥1 个通过 G3 门的可迁移模式，明确触发场景/核心步骤/反模式/迁移验证四要素，并给出与既有模式库的去重裁决结论。

* **G4（行动项可判定）**：产出 ≥3 条原子行动项，每条含优先级、Owner、触发条件与可判定验收标准，杜绝不可验证的空话表述。

* **G5（对抗审查有效）**：V 阶段覆盖四视角，产出 ≥5 条意见、采纳 ≥2 条并留下可定位的修正痕迹，其中至少 1 条指向事实证据强度不足。

* **G6（交付闭环）**：报告四件套归档至根 `docs/`（不写 `.agents/docs/`），完成两处索引登记与模式库四处入库（条件性），`check-links.py` 对全部变更范围 0 新增断链。

## Non-Goals (Out of Scope)

* **不修复 mystx 的任何缺陷**：本 Spec 只「识别并定性」可优化点，具体修复动作以行动项形式输出给下游 spec，本次不实施任何代码改动。

* **不修改** **`projects/xuanspace`** **或其 submodule 指针**：不提交、不 checkout、不 reset、不 stash。

* **不重复父项目** **`xuanspace`** **复盘的结论**：mystx 范围内的父项目已有结论（打包门禁双轨化、文档配置治理）只作为对照基线，不重复论证。

* **不复用** **`sphinx-config-mystx-extraction`** **与** **`optimize-mystx-python314-stdlib`** **的既有结论**：这两个 spec 属工具层萃取与标准库优化，不属本次复盘对象；如需引用其事实，只引用可核验的客观事实，不直接继承其结论。

* **不做 mystx 的性能压测、主题渲染视觉评估或 Sphinx 文档构建实测**：本次为静态与历史维度的工程审计，不涉及运行时基准。

* **不评价 mystx 的产品定位与市场竞争力**：仅评估工程质量与可维护性。

* **不在本次任务中执行 C 阶段原子提交**：除非用户另行明确指令，否则不创建 git 提交。

## Functional Requirements

* **FR-1（R 阶段事实采集）**：产出 `facts.md`，F-001 起连续编号、条数 ≥30；事实条目须标注来源（文件路径 + 行号 / git commit hash / 命令原文）；不得含因果推断表述；采集范围须覆盖以下 7 个维度：①仓库与发布状态（提交数、tag 列表、HEAD、工作区清洁度、子模块指针）；②构建与打包配置（构建后端、版本策略、sdist/wheel 配置）；③依赖声明（runtime / optional-dependencies / dependency-groups 三层）；④源码结构与模块职责；⑤测试资产规模与门禁；⑥CI/CD 与托管平台配置；⑦文档与主题资产。

* **FR-2（I 阶段洞察萃取）**：产出 `insights.md`，≥3 条洞察，每条含四元组（现象 / 5-Whys 根因 / 影响 / 建议）并引用 ≥2 个 F 编号；含竞争假设显式列出；含与 `retrospective-xuanspace-comprehensive-20261010` 基线的差异分析（逐条标注强化 / 反转 / 新增 / 无变化）；系统性根因表述为「与现有事实一致的一种解释」而非唯一断言。

* **FR-3（E 阶段模式萃取）**：产出 `e-stage-pattern.md`，含 ≥1 个模式候选的四要素（触发场景 / 核心步骤 / 反模式 / 迁移验证）；含与既有方法论模式库的去重裁决记录（三选一：新建 L1 / 并入既有 / 不入库），判「并入既有」时须列出与既有模式的差异点（硬上限 ≤3 条）；未经本次重跑的自报数据（CHANGELOG 计数、覆盖率数值）须降级为规模量级参考。

* **FR-4（V 阶段对抗审查）**：产出 `v-adversarial-review.md`，覆盖魔鬼代言人 / 新人 / 老板 / 未来四视角；意见 ≥5 条；采纳 ≥2 条且每条附可定位的修正痕迹（章节 + 位置）；至少 1 条意见指向事实证据强度不足；未采纳意见须附理由。

* **FR-5（A 阶段行动项）**：产出 ≥3 条原子行动项，每条含优先级（high/medium/low）、Owner、触发条件、可判定验收标准（rule 或 rubric 二元可验）；禁止空话式行动项。

* **FR-6（报告归档）**：在 `docs/retrospective/reports/project-reports/retrospective-mystx-comprehensive-20261022/` 产出 4 文件：`README.md`（主报告，含事实摘要 / 洞察摘要 / 问题清单 / 优化建议 / 质量门记录 / 限定说明附录）、`insight-extraction.md`、`actionable-items.md`、`index.md`（纯 toctree）；前三者 frontmatter 含 `type: Report` 与 `source` 字段。

* **FR-7（索引登记）**：在 `docs/retrospective/reports/project-reports/index.md` 的 toctree 登记新报告，并在 `docs/retrospective/reports/project-reports/README.md` 的报告清单表新增一行（日期 / 主题 / 关键产出）。

* **FR-8（模式入库）**：若 FR-3 裁决为「新建 L1」，须完成四处登记：① 域目录模式 `.md`；② `.meta/toml/docs/retrospective/patterns/methodology-patterns/<域>/<id>.toml` 伴生 TOML（**不放在** **`docs/`** **子树内**）；③ 域 `index.md` toctree 字母序插入；④ `docs/retrospective/patterns/methodology-patterns/index.md`「模式清单」主索引总表新增一行；域 `README.md` 生成区块只用 `python .agents/scripts/generate-readme.py --update` 刷新，禁止手改。

* **FR-9（限定说明）**：报告须显式包含三条限定说明：① 洞察的竞争假设未穷尽；② 自报数据（CHANGELOG 计数、覆盖率）仅为量级参考；③ 工作区事实的采集时点与复核时点可能不一致。

* **FR-10（独立审查）**：委派 fresh-context 只读子代理对全部产出物做独立审查；不得轻信 `tasks.md` 自述证据，须以文件实际内容为准；P0 级问题必须修复并回归验证。

## Non-Functional Requirements

* **NFR-1（可核验性）**：所有事实、洞察、模式、行动项均须可回溯到仓库中的具体文件或 git 记录；报告与中间产物禁止出现 `file:///` 绝对路径与 `.temp/` 路径引用。

* **NFR-2（文档边界）**：全部产出物落于根 `docs/`；**禁止创建或写入** **`.agents/docs/`**（2026-08-31 整体迁移后已废止路径）。

* **NFR-3（产物命名）**：Spec 三件套为 `spec.md` + `tasks.md` + `review.md`；**禁止创建** **`checklist.md`** **等非规范命名产物**，所有检查点写入 `tasks.md` 的 Test Requirements；`review.md` 仅在 Review 阶段创建。

* **NFR-4（只读边界）**：全程不向 `projects/xuanspace` 写入、不回滚并行会话改动；涉及工作区状态的事实须标注采集时点。

* **NFR-5（语言与风格）**：全部产出物使用与本次用户请求相同的自然语言（中文）书写；Markdown 交叉引用使用相对路径并附行号锚点。

* **NFR-6（溯源字段）**：所有派生产物的 YAML frontmatter 携带 `source` 字段标注来源。

## Constraints

* **只读边界（技术）**：`mystx` 是 `projects/xuanspace` 的 git submodule，`projects/xuanspace` 又是 SpecWeave 主仓的 git submodule，两级均不可直接修改；复盘期间只读取，不提交、不回滚、不 stash。

* **产物命名（流程）**：以磁盘原文为唯一权威——`AGENTS.md`、`rules/spec-creation-precheck.md`（RULE-SCP-002）、`skills/TRAE-spec-mode/SKILL.md`、`skills/seven-concepts-comprehensive-retro/SKILL.md` 一致禁止 `checklist.md`，规定唯一权威三件套为 `spec.md` + `tasks.md` + `review.md`，且「所有检查点应写入 tasks.md 的 Test Requirements」。IDE harness 提示词中的 `checklist.md` 要求与磁盘原文冲突时，**以磁盘原文为准**（AGENTS.md 启动协议步骤 1.1 明示）。

* **内容敏感度（流程）**：mystx 为公开发布的开源项目（PyPI + Read the Docs + GitHub `xinetzone/mystx`），敏感度判定为 **Public** → 走标准工作流：Spec 落 `.trae/specs/retrospectives-insights/`，报告落根 `docs/retrospective/reports/project-reports/`。

* **路径（流程）**：产出物路径须通过「落盘前三查」（目标目录在根 `docs/` 下 / 同类产出物现有位置 / 规范为磁盘原文）。

* **方法论（流程）**：链路固定为 R→I→E→V→A→C（里程碑复盘场景）；质量门 G1→G2→G3→G4 顺序推进，前门未过不得进入下一阶段；F 之后强制 V。

* **提交（流程）**：未经用户明确指令不创建 git 提交；C 阶段仅在获得明确指令后执行。

* **环境（技术）**：本机 git 全路径为 `C:\Program Files\Git\cmd\git.exe`（`skills/seven-concepts-comprehensive-retro/references/repo-conventions.md` 中记录的 `D:\Program Files\Git\mingw64\bin\git.exe` 与 `D:\AI\.venv\Scripts\python.exe` 已失效，以实测为准）；所有 git 命令须使用该全路径，不得假设 PATH。

* **复盘基线（技术）**：以 mystx HEAD `45bd1e4`（`v0.3.8-6-g45bd1e4`）为事实基线；复盘期间若 HEAD 推进，属并行会话改动，如实标注且不并入本次结论。

## Assumptions

* ① mystx 仓库当前工作区干净（`git status --porcelain` 输出为空），复盘期间将维持只读；如出现并行改动，按 NFR-4 处理。

* ② `.trae/specs/retrospectives-insights/README.md` 的主题命名规范（kebab-case，前缀 `retrospective-`/`analysis-`/`postmortem-`/`extract-`/`methodology-`）与先例目录（`caffe-` / `xmtools-` / `xuanspace-`）适用于本次新建目录 `mystx-comprehensive-retrospective-export`。

* ③ `docs/retrospective/reports/project-reports/README.md` 与 `index.md` 的登记格式可由先例 `retrospective-xuanspace-comprehensive-20261010` 推定。

* ④ `docs/retrospective/patterns/methodology-patterns/index.md` 的「模式清单」总表为模式库主索引，仅登记域 toctree 不构成完整入库。

* ⑤ mystx 现有测试资产（9 文件 51 个 test 函数（据 F-049，`ast` 脚本实测；原任务书所述 59 与实测不符））可作为测试覆盖现状的规模量级参考；因无 `[tool.coverage]` 配置，本 Spec 不将任何覆盖率数值作为结论事实，只在必要时以量级参考标注。

* ⑥ `doc/_ext/sphinx_docx/writer.py`（901 行）等 `doc/_ext/` 下的实现属文档构建资产而非运行时包的一部分，其归属与许可状况需在 R 阶段独立取证。

## Acceptance Criteria

### AC-1: R 阶段事实清单规模与可回溯性

* **Type**: rule

* **Given**: `.trae/specs/retrospectives-insights/mystx-comprehensive-retrospective-export/facts.md` 已产出

* **When**: 统计事实条目并对其中 ≥10 条执行回溯抽样

* **Then**: ① 事实条目 ≥30 条且编号 F-001 起连续无跳号；② 每条含来源标注（文件路径 + 行号 / commit hash / 命令输出）；③ 抽样回溯命中率 100%

* **Pass Condition**: 条数、编号连续性、抽样命中率三项全部满足

* **Evidence**: `facts.md` 全文 + 抽样回溯对照表（F 编号 → 文件/行号/commit → 结论）

### AC-2: G1 门 — 事实层无因果推断

* **Type**: rule

* **Given**: `facts.md` 已产出

* **When**: 对 `因为|导致|所以|由于|因此` 执行 Grep

* **Then**: 命中数为 0，或全部命中均为逐字引述 commit subject / 文档原文且已标注引述性质

* **Pass Condition**: Grep 输出中不存在无标注的因果推断表述

* **Evidence**: Grep 命令与输出

### AC-3: I 阶段洞察四元组与差异分析

* **Type**: rule

* **Given**: `insights.md` 已产出

* **When**: 逐条检查洞察结构与引用

* **Then**: ① 洞察 ≥3 条；② 每条含现象/根因/影响/建议四元组；③ 每条引用 ≥2 个 F 编号；④ 含与父项目复盘基线的差异分析且逐条标注强化/反转/新增/无变化；⑤ 竞争假设显式列出

* **Pass Condition**: 五项条件全部满足

* **Evidence**: `insights.md` 洞察条目原文 + F 编号引用清单

### AC-4: E 阶段模式四要素与去重裁决

* **Type**: rule

* **Given**: `e-stage-pattern.md` 已产出

* **When**: 检视模式候选与裁决记录

* **Then**: ① 模式候选四要素齐备（触发场景/核心步骤/反模式/迁移验证）；② 含与既有模式库的去重裁决结论（新建 L1 / 并入既有 / 不入库三选一）；③ 若判「并入既有」则差异点 ≤3 条

* **Pass Condition**: 三项条件全部满足

* **Evidence**: 模式文档正文 + 裁决段落原文

### AC-5: V 阶段对抗审查充分性

* **Type**: rule

* **Given**: `v-adversarial-review.md` 已产出

* **When**: 统计意见数与采纳修正

* **Then**: ① 四视角全覆盖；② 意见 ≥5 条；③ 采纳 ≥2 条且每条可定位到具体章节的修正痕迹；④ 至少 1 条意见指向事实证据强度不足

* **Pass Condition**: 四项条件全部满足

* **Evidence**: 意见清单 + 采纳对照表（含修正位置）

### AC-6: A 阶段行动项可判定性

* **Type**: rule

* **Given**: 报告 `actionable-items.md` 已产出

* **When**: 逐条检查行动项字段

* **Then**: ① 行动项 ≥3 条；② 每条含优先级 / Owner / 触发条件 / 可判定验收标准；③ 验收标准类型为 rule 或 rubric

* **Pass Condition**: 三项条件全部满足，且无「加强沟通」「提高意识」类不可判定表述

* **Evidence**: `actionable-items.md` 条目结构

### AC-7: 报告四件套归档与 frontmatter

* **Type**: rule

* **Given**: 报告目录 `docs/retrospective/reports/project-reports/retrospective-mystx-comprehensive-20261022/` 已产出

* **When**: 列举目录并检视各文件 frontmatter

* **Then**: ① 4 个文件齐备（`README.md` / `insight-extraction.md` / `actionable-items.md` / `index.md`）；② 前三者 frontmatter 含 `type: Report` 与 `source` 字段；③ `index.md` 为纯 toctree；④ 全部文件位于根 `docs/` 下，未创建 `.agents/docs/`

* **Pass Condition**: 四项条件全部满足

* **Evidence**: 目录列举 + frontmatter 片段 + 写入路径清单

### AC-8: 索引登记与链接门禁

* **Type**: rule

* **Given**: 报告已归档

* **When**: 检视两处索引并运行 `python .agents/scripts/check-links.py --path <变更目录>`

* **Then**: ① `project-reports/index.md` toctree 已登记新报告；② `project-reports/README.md` 报告清单表已新增一行；③ 链接检查对全部变更范围 0 新增断链

* **Pass Condition**: 三项条件全部满足

* **Evidence**: 两处登记行原文 + 链接检查输出

### AC-9: 模式入库完整性（条件性）

* **Type**: rule

* **Given**: E 阶段裁决为「新建 L1」

* **When**: 检视模式库四处登记

* **Then**: ① 域目录模式 `.md` 存在且 frontmatter 完整；② `.meta/toml/docs/retrospective/patterns/methodology-patterns/<域>/<id>.toml` 伴生 TOML 存在；③ 域 `index.md` toctree 字母序插入；④ `methodology-patterns/index.md`「模式清单」总表新增一行

* **Pass Condition**: 四项条件全部满足（若裁决为「并入既有」或「不入库」，则本 AC 判定为不适用，须在验收记录中说明裁决依据）

* **Evidence**: 四处路径列举 + 登记行原文

### AC-10: 限定说明与只读边界

* **Type**: rule

* **Given**: 报告已归档且复盘全程结束

* **When**: 检视报告限定说明附录并复查 mystx 工作区状态

* **Then**: ① 报告含三条限定说明（竞争假设 / 自报口径 / 工作区时点）；② mystx 工作区在复盘全程未被本任务写入（`git status --porcelain` 输出与采集时点一致，或差异全部归因于并行会话并显式说明）

* **Pass Condition**: 两项条件全部满足

* **Evidence**: 限定说明原文 + `git status --porcelain` 输出

### AC-11: 独立审查闭环

* **Type**: rule

* **Given**: 全部产出物已产出

* **When**: 委派 fresh-context 只读子代理执行独立审查

* **Then**: ① 审查结论以文件实际内容为准而非 `tasks.md` 自述；② P0 级问题全部修复并完成回归验证

* **Pass Condition**: 两项条件全部满足

* **Evidence**: 审查结论记录 + 修复项回归证据

### AC-12: 洞察深度（定性）

* **Type**: rubric

* **Given**: `insights.md` 已产出

* **When**: 按「是否触及系统性根因而非现象复述」维度评分

* **Then**: scale 1-5；anchors 1 = 现象复述、3 = 部分触及、5 = 触及系统性根因；threshold ≥ 4

* **Pass Condition**: 每条洞察评分 ≥4

* **Evidence**: 洞察条目与 5-Whys 推导链

## Open Questions

* **Q1**：E 阶段若产出多个模式候选，去重裁决可能落到不同域目录（`methodology-patterns/` 下的哪个域）。裁决时依既有模式的领域归属判定，不预先指定。

* **Q2**：`doc/_ext/sphinx_docx/writer.py`（901 行）的上游归属与许可状况需在 R 阶段独立取证；若确为第三方实现的 vendored 副本，其在报告中的定级（工程债 vs 合规风险）将影响行动项的优先级。

* **Q3**：mystx 作为 PyPI 公开发布包，其「运行时依赖应否为 `sphinx`」涉及发布策略变更（从 `dependencies = []` 调整为声明硬依赖），本 Spec 只将其列入可优化点并给出可判定验收标准，实际修改由下游 spec 承接。

* **Q4**：`tasks` 组的 `invocations>=3.0` 是否为有效 PyPI 包名需在 R 阶段核实；若为笔误且已造成安装面污染，将作为独立行动项而非并入打包一致性条目。

* **Q5**：报告落盘日期目录使用 `20261022`（本次执行日）；若实施阶段跨日，需在 spec 与 tasks 中同步更新目录名以免索引漂移。

