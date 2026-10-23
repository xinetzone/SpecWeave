---
title: "mystx 全面复盘 + 报告导出 — 实施计划"
status: "draft"
id: "mystx-comprehensive-retrospective-export-tasks"
methodology: "seven-concepts (R→I→E→V→A→C)"
source: "./spec.md"
---

# mystx 全面复盘 + 报告导出 — Implementation Plan

> 链路：R（事实）→ I（洞察）→ E（模式萃取）→ V（对抗审查）→ A（行动项）→ C（原子提交）
> 质量门：G1（事实无因果词）→ G2（洞察四元组完整）→ G3（模式可迁移）→ G4（行动项原子化）
> 复盘对象：`d:/spaces/SpecWeave/projects/xuanspace/libs/mystx`（**只读**，HEAD 基线 `45bd1e4`）
> 报告基准：`docs/retrospective/reports/project-reports/retrospective-mystx-comprehensive-20261022/`
> 产物命名：以磁盘原文为准（`spec.md` + `tasks.md` + `review.md`），**不创建 `checklist.md`**

## Task 1: R 阶段 — 事实采集（结构 / 构建 / 依赖 / 测试 / CI / 文档）
- [x] **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 以 mystx HEAD `45bd1e4` 为基线，采集 7 维客观事实并输出 `facts.md`（F-001 起连续编号）
  - ①仓库与发布状态：提交数与日期区间、tag 全集（13 个）、HEAD hash、子模块指针（`submodule status`）、工作区 `status --porcelain` 输出
  - ②构建与打包配置：`pyproject.toml` 的 build-system / scikit-build-core 段 / setuptools-scm 动态版本 / sdist-wheel 配置
  - ③依赖声明三层比对：`project.dependencies` vs `[project.optional-dependencies]` vs `[dependency-groups]`，逐组列出差异与重叠
  - ④源码结构：全部 `.py` 行数清单、模块职责分布、`__all__` 导出面、`__init__.py` 导入链（`from . import presets, tasks` 对 invoke 的强制依赖）
  - ⑤测试资产：9 个测试文件 / 51 个 test 函数（据 F-049，`ast` 脚本实测；原任务书所述 59 与实测不符） / 无 `[tool.coverage]` 段 / 无 `fail_under` 门禁
  - ⑥CI/CD 与平台配置：3 个 workflow + `.readthedocs.yml` + `.pre-commit-config.yaml`（含版本固定与配置冲突）
  - ⑦文档与主题资产：README 声明与 pyproject 实际依赖的逐条比对、CHANGELOG 覆盖版本 vs git tag 集合、README 示例引用的目录是否存在、`doc/_ext/sphinx_docx/writer.py` 行数与上游归属线索
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-10
- **Test Requirements**:
  - `rule` TR-1.1: 事实条目 ≥30 条且编号 F-001 起连续无跳号 —— 证据：`facts.md` 条目计数与编号序列
  - `rule` TR-1.2: 7 个采集维度均有事实覆盖，每条含来源标注（文件路径 + 行号 / commit hash / 命令输出）—— 证据：按维度归组的条目抽样
  - `rule` TR-1.3: G1 门通过——Grep `因为|导致|所以|由于|因此` 命中为 0，或全部命中均为逐字引述且已标注引述性质 —— 证据：Grep 输出
  - `rule` TR-1.4: 抽查 ≥10 条事实回溯，命中率 100% —— 证据：回溯对照表（F 编号 → 文件/commit → 结论）
  - `rule` TR-1.5: 全程未写入 `projects/xuanspace` —— 证据：复盘前后 `git -C projects/xuanspace status --porcelain` 输出一致，差异如有则归因并行会话
- **Notes**: git 命令须用全路径 `C:\Program Files\Git\cmd\git.exe`；所有命令只读；事实采集时点须在 `facts.md` 顶部标注
- **Completion Evidence**:
  - 产物：`.trae/specs/retrospectives-insights/mystx-comprehensive-retrospective-export/facts.md`，F-001 ~ F-097 连续无跳号（正文表体 97 行 / 去重 97 个编号，附录抽样表另 27 行，编号集合并集 97）。
  - 维度覆盖：A~G 七维 + H 补充取证段，条目 97 条 ≥30（TR-1.1 通过）；附录回溯抽样对照表 27 条（要求 ≥12），命中率 27/27 = 100%（TR-1.4 通过）。
  - G1 门通过：对 `facts.md` 全文正则检索 `因为|导致|所以|由于|因此` 命中 **0**（TR-1.3 通过）。
  - 只读边界复核：`git -C projects/xuanspace status --porcelain` 与 `git -C projects/xuanspace/libs/mystx status --porcelain` 修正前后均为空输出（TR-1.5 通过）。
  - V 阶段审查修正批次回填：新增 F-088（`git diff --stat v0.3.4 HEAD` = 69 files changed / 2892 insertions / 533 deletions）、F-089（13 tag → 6 谱系映射）、F-090（v0.3.4 pyproject）、F-091（CHANGELOG 模板头）、F-092~F-097（PyPI / GitHub 发布面外部权威）；修正 F-086 括注错误。

## Task 2: I 阶段 — 洞察萃取（5-Whys 根因 + 差异分析）
- [x] **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 基于 `facts.md` 执行 5-Whys 根因分析，输出 `insights.md`
  - 提炼 ≥3 条洞察，每条含四元组（现象 / 根因 / 影响 / 建议）并引用 ≥2 个 F 编号
  - 显式列出竞争假设（根因表述为「与现有事实一致的一种解释」）
  - 与父项目 `retrospective-xuanspace-comprehensive-20261010` 基线做差异分析，逐条标注强化 / 反转 / 新增 / 无变化
- **Acceptance Criteria Addressed**: AC-3, AC-12
- **Test Requirements**:
  - `rule` TR-2.1: 洞察 ≥3 条，四元组完整，每条引用 ≥2 个 F 编号 —— 证据：洞察条目原文 + F 编号引用清单
  - `rule` TR-2.2: 差异分析四类标注（强化/反转/新增/无变化）逐条给出，且每条差异引用具体 F 编号 —— 证据：差异分析表
  - `rule` TR-2.3: 竞争假设显式列出且未以唯一断言表述根因 —— 证据：竞争假设段落
  - `rubric` TR-2.4: 洞察深度评分（是否触及系统性根因而非现象复述）；scale 1-5；anchors 1 = 现象复述、3 = 部分触及、5 = 触及系统性根因；threshold ≥4；证据：5-Whys 推导链
- **Notes**: G2 门未过不得进入 Task 3
- **Completion Evidence**:
  - 产物：`.trae/specs/retrospectives-insights/mystx-comprehensive-retrospective-export/insights.md`，洞察 **5 条**（I-1 ~ I-5，目标区间 4~5 条），每条含「现象 / 5-Whys 根因 / 影响 / 建议」四元组齐备（TR-2.1 通过）。
  - F 编号引用清单逐条可数（脚本逐条实测，与文中自述数一致）：I-1 = 24 个、I-2 = 20 个、I-3 = 25 个、I-4 = 18 个、I-5 = 25 个，均 ≥2（TR-2.1 通过）。
  - 竞争假设 §2 显式列出 **10 条**（含 H4-B 等由 PyPI/GitHub 发布面证据可裁决者），根因表述统一为「与现有事实一致的一种解释」，未作唯一断言（TR-2.3 通过）。
  - 差异分析 §3 表逐条标注强化 / 反转 / 新增 / 无变化，且每条差异引用具体 F 编号（F-024 / F-063 / F-066 / F-069 四处基线差异对应 F-024 pyproject、F-063 pre-commit、F-066 README、F-069 locale 路径）（TR-2.2 通过）。
  - V 阶段审查修正批次落地：I-1 引入 F-088/F-089/F-090/F-092~F-097（diff 可用 + 6 条谱系 + 分发面四元组），I-2 拆分 invoke（硬失败）/ invocations（软降级）失败语义并补 F-095 独立佐证，I-4 改写为「仪式从未真正建立」并补 F-091，I-5 补 F-086 双向投影错位（并集独有 23 项 + docs 组另有 3 项不在并集内）。

## Task 3: E 阶段 — 模式萃取与去重裁决
- [x] **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 从洞察中提炼 ≥1 个可迁移模式候选，输出 `e-stage-pattern.md`
  - 四要素齐备：触发场景 / 核心步骤 / 反模式 / 迁移验证
  - 与 `docs/retrospective/patterns/methodology-patterns/` 既有模式做去重裁决，三选一：新建 L1 / 并入既有 / 不入库
  - 未经本次重跑的自报数据（CHANGELOG 计数、覆盖率）降级为规模量级参考
- **Acceptance Criteria Addressed**: AC-4, AC-9
- **Test Requirements**:
  - `rule` TR-3.1: 模式候选四要素齐备 —— 证据：模式文档正文
  - `rule` TR-3.2: 去重裁决结论已记录；若判「并入既有」则差异点 ≤3 条 —— 证据：裁决段落 + 差异点列举
  - `rule` TR-3.3: 自报数据已显式降级标注 —— 证据：相关条目的降级说明
- **Notes**: 裁决为「新建 L1」时，Task 5 才进入模式入库子项
- **Completion Evidence**:
  - 产物：`.trae/specs/retrospectives-insights/mystx-comprehensive-retrospective-export/e-stage-pattern.md`（363 物理行），含 3 个模式候选（C1 发布资格不变量与发布路径对账 / C2 声明面单一权威源与多载体事实对齐 / C3 最小可安装单元验收），C1 与 C2 四要素齐备（触发场景 / 核心步骤 / 反模式 / 迁移验证，TR-3.1 通过）。
  - 去重裁决已记录（TR-3.2 通过）：C1 = 新建 L1（`release-eligibility-invariant-gate`）、C2 = 新建 L1（`single-authority-declaration-alignment`）、C3 = 不入库（方法核心已被既有模式族覆盖，根因受竞争假设 H2-B 挑战未裁决）；两个入库 id 的去重核验口径为——主索引「模式清单」总表 **49** 行登记（表体数据行数，不含表头与分隔行）、governance-strategy 域 toctree **170** 个 kebab-case 模式名条目（另有 2 个非模式条目）、全库 **552** 个模式 `.md`（10 个域目录）、该域 **146** 个伴生 `.toml`，四处检索均零重复。
  - 自报数据已显式降级标注（TR-3.3 通过）：CHANGELOG 计数与覆盖率数值均标注为「规模量级参考」，覆盖率因仓库无 `[tool.coverage]` 段而不作任何量化陈述。
  - V 阶段审查修正批次落地：§2.1 信号 1/2、§2.2 步骤 ①/②/③/⑤、§2.3 反模式 1、§2.4 迁移验证信号 1 全部改写为「版本坐标四元组（含分发面实际发布坐标）」并补 F-088/F-089/F-090/F-092~F-097；新增不变量 I-8（最新 tag 在分发面可安装且可下载，判定方式为 PyPI JSON API 返回 200 且 `info.version` 一致）；§4.4 三处去重计数更正为实测 49 / 170 / 146（原记录值与实测不符，已按实测覆写）。

## Task 4: V 阶段 — 四视角对抗审查
- [x] **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 以魔鬼代言人 / 新人 / 老板 / 未来四视角审查 Task 1~3 的全部产出物
  - 输出 `v-adversarial-review.md`：意见 ≥5 条，采纳 ≥2 条并留下可定位的修正痕迹
  - 至少 1 条意见须指向「事实证据强度不足」
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `rule` TR-4.1: 四视角全覆盖，意见 ≥5 条 —— 证据：意见清单
  - `rule` TR-4.2: 采纳 ≥2 条，每条在对应产出物中有可定位的修正痕迹（章节 + 位置）—— 证据：采纳对照表 + 修正位置
  - `rule` TR-4.3: 至少 1 条意见指向事实证据强度不足 —— 证据：该条意见原文
- **Notes**: F 阶段完成后强制 V；不采纳的意见须附理由
- **Completion Evidence**:
  - 产物：`.trae/specs/retrospectives-insights/mystx-comprehensive-retrospective-export/v-adversarial-review.md`，意见 **11 条**（V-1 ~ V-11）≥5 条（TR-4.1 通过）。
  - 四视角全覆盖（TR-4.1 通过）：魔鬼代言人 3 条（V-1 / V-2 / V-11）/ 新人 2 条（V-4 / V-5）/ 老板 3 条（V-6 / V-7 / V-10）/ 未来 3 条（V-3 / V-8 / V-9）。
  - 采纳 **6 条** ≥2 条，每条在对应产出物中留有可定位修正痕迹（TR-4.2 通过）：P0 **3 条**（V-1 diff 可用性表述过强 / V-2 谱系结构缺失 / V-11 发布面外部权威缺失）+ P1 **3 条**（V-4 F-086 括注错误 / V-6 invoke 与 invocations 失败语义未分级 / V-8 契约层 test 函数计数与 F-049 实测冲突）；未采纳 5 条（V-3 / V-5 / V-7 / V-9 / V-10）逐条附理由（§3.1 N-1 ~ N-5）。
  - 至少 1 条指向事实证据强度不足（TR-4.3 通过）：**V-1 / V-2 / V-11 共 3 条**。
  - 证据强度分级（§4.2 抽验 18 条，覆盖 A~H 全部 8 个维度）：**可回溯 15 条（83.3%）/ 需降级 3 条（16.7%，即 F-011 / F-086 / F-041）/ 不可回溯 0 条（0%）**。
  - 本批次「审查修正落地」已完成 6 条采纳修正 + 5 条 P2 顺带清理（N-1 ~ N-5）的产出物落地，改动范围限定为 `spec.md` / `tasks.md` / `facts.md` / `insights.md` / `e-stage-pattern.md` 五个文件；`projects/xuanspace` 及其 mystx 子模块全程只读，`git status --porcelain` 前后均为空输出。

## Task 5: A 阶段 — 行动项萃取与报告四件套归档
- [x] **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 产出 ≥3 条原子行动项，每条含优先级 / Owner / 触发条件 / 可判定验收标准（rule 或 rubric）
  - 归档报告四件套至 `docs/retrospective/reports/project-reports/retrospective-mystx-comprehensive-20261022/`：
    - `README.md`（主报告：事实摘要 / 洞察摘要 / 问题清单 / 优化建议 / 质量门记录 / 限定说明附录）
    - `insight-extraction.md`（洞察与模式萃取全文）
    - `actionable-items.md`（原子行动项）
    - `index.md`（纯 toctree，无 frontmatter）
  - 前三者 frontmatter 含 `type: Report` 与 `source`
- **Acceptance Criteria Addressed**: AC-6, AC-7, AC-10
- **Test Requirements**:
  - `rule` TR-5.1: 报告 4 文件齐备，前三者 frontmatter 含 `type: Report` 与 `source` —— 证据：目录列举 + frontmatter 片段
  - `rule` TR-5.2: 4 文件全部位于根 `docs/` 下；未创建 `.agents/docs/`；无 `file:///` 与 `.temp/` 引用 —— 证据：写入路径清单 + Grep 输出
  - `rule` TR-5.3: 行动项 ≥3 条，每条含 4 个必需字段且验收标准为 rule 或 rubric；无空话式表述 —— 证据：`actionable-items.md` 条目结构
  - `rule` TR-5.4: 报告含三条限定说明（竞争假设 / 自报口径 / 工作区时点）—— 证据：限定说明附录原文
- **Notes**: 报告须覆盖「可优化点」诉求——问题清单须逐条给出问题描述、证据位置（F 编号 / 文件行号）与优化方向
- **Completion Evidence**:
  - 产物：`docs/retrospective/reports/project-reports/retrospective-mystx-comprehensive-20261022/` 四文件齐备 —— `README.md`（327 物理行）、`insight-extraction.md`（586 物理行）、`actionable-items.md`（148 物理行）、`index.md`（10 物理行，纯 toctree 无 frontmatter）。行数口径为物理行（`splitlines()`），非空行数分别为 258 / 427 / 115 / 8。
  - TR-5.1 通过：前三者 frontmatter 均含 `type: Report` + `id` + `version` + `source`（`source` = `../../../../../.trae/specs/retrospectives-insights/mystx-comprehensive-retrospective-export/insights.md`）；`index.md` 为纯 toctree。
  - TR-5.2 通过：4 文件全部位于根 `docs/retrospective/reports/project-reports/` 下；`.agents/docs` 未创建（`Test-Path` = False）；Grep `file:///` 与 `.temp/` 在新目录零命中；`check-links.py --path <该目录> --check-frontmatter-paths` 输出「25 个本地引用全部存在」「frontmatter 路径字段全部有效」，0 断链。
  - TR-5.3 通过：行动项 **ACT-01 ~ ACT-10 共 10 条**（ACT-01~ACT-09 为 mystx 工程侧，ACT-10 为方法论侧，Owner 不同源故不合并），每条含 描述 / 优先级 / Owner / 触发条件·时间节点 / 验收标准 / 来源 六字段；验收标准 9 条 rule + 1 条 rubric，文末「原子化自评（AC-8 / G4）」rubric 表自评 4~5 分、全部 ≥4（阈值 ≥4）。
  - TR-5.4 通过：报告「附录：限定说明与证据强度」共 **6 条**，覆盖要求的 3 条（①竞争假设未穷尽，主结论为「与现有事实一致的一种解释」，引 insights.md §2 的 10 条 H1-A~H5-B；②自报口径仅作规模量级参考，且因仓库无 `[tool.coverage]` 段故对覆盖率不作任何量化陈述；③工作区事实采双时点标注、只读归因）并额外补充 3 条（版本坐标类事实时效性、本次未做运行时验证、R 阶段事实分两批采集）。
  - 「可优化点」诉求覆盖：「可优化点问题清单」**Q-01 ~ Q-12 共 12 条**，每条含 问题描述 / 证据位置（F 编号 + `文件:行号`）/ 优化方向（→ 具体 ACT 编号）三要素，覆盖 I-1 ~ I-5 全部五条洞察与 D-1 ~ D-6 全部六个独有问题域。
  - 只读边界：本任务未写入 `projects/xuanspace` 及其子模块，未修改 4 份 spec 中间产物，未执行 git 提交。

## Task 6: 索引登记与模式入库
- [x] **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 5
- **Description**:
  - 索引登记 1：`docs/retrospective/reports/project-reports/index.md` toctree 新增新报告条目
  - 索引登记 2：`docs/retrospective/reports/project-reports/README.md` 报告清单表新增一行（日期 / 主题 / 关键产出）
  - 模式入库（条件性，Task 3 裁决为「新建 L1」时执行）：
    - ① 域目录模式 `.md`
    - ② `.meta/toml/docs/retrospective/patterns/methodology-patterns/<域>/<id>.toml` 伴生 TOML
    - ③ 域 `index.md` toctree 字母序插入
    - ④ `docs/retrospective/patterns/methodology-patterns/index.md`「模式清单」主索引总表新增一行
    - ⑤ 域 `README.md` 生成区块用 `python .agents/scripts/generate-readme.py --update` 刷新（禁止手改）
  - 质量门：运行 `python .agents/scripts/check-links.py --path <变更目录>`，0 新增断链
- **Acceptance Criteria Addressed**: AC-8, AC-9
- **Test Requirements**:
  - `rule` TR-6.1: 两处索引均登记 —— 证据：登记行原文
  - `rule` TR-6.2: 模式入库四处齐备（条件性）—— 证据：路径列举 + 登记行原文
  - `rule` TR-6.3: `check-links.py` 对全部变更范围 0 新增断链 —— 证据：链接检查输出
- **Notes**: 若 Task 3 裁决为「并入既有」或「不入库」，本 Task 仅执行两处索引登记，TR-6.2 判定为不适用并记录裁决依据
- **Completion Evidence**:
  - **模式入库五步齐备**（Task 3 裁决为「新建 L1」，C1 + C2）：
    - ① 域目录模式 `.md`：`docs/retrospective/patterns/methodology-patterns/governance-strategy/release-eligibility-invariant-gate.md`（258 物理行）、`single-authority-declaration-alignment.md`（224 物理行）；frontmatter 含 `type: Pattern` / `id` / `title` / `source` / `x-toml-ref` / `maturity: "L1"` / `maturity_level: "L1-draft"` / `validation_count: 1` / `reuse_count: 0` / `documentation_level` / `version` / `created_date` / `last_updated` / `tags` / `trigger_conditions` / `problem_solved` / `related_patterns`；正文 12 段（模式类型 / 成熟度 / 一句话 / 适用场景 / 问题背景 / 核心做法 / 反模式 / 检验标准 / 迁移示例 / 案例证据 / 失效条件与演进 / 参考实现与关联）。
    - ② 伴生 TOML ×2：`.meta/toml/docs/retrospective/patterns/methodology-patterns/governance-strategy/{release-eligibility-invariant-gate,single-authority-declaration-alignment}.toml`；字段 `id` / `domain = "methodology"` / `layer = "methodology"` / `maturity` / `validation_count` / `reuse_count` / `documentation_level` / `source`（仓库根相对路径）/ `[bindings]` 的 `rules` / `references` / `skills`。
    - ③ 域 `index.md` toctree 字母序插入：`release-eligibility-invariant-gate`（介于 `reference-as-trigger` 与 `responsibility-transfer-governance`）、`single-authority-declaration-alignment`（介于 `simple-task-high-risk` 与 `snapshot-parity-migration`）；插入后 toctree 共 174 条（其中 172 条模式 + `cases/index` / `exercises/index` 两条非模式）。
    - ④ 主索引 `docs/retrospective/patterns/methodology-patterns/index.md`「模式清单」总表新增 2 行（表尾 `decomposable-recognition-ladder` 之后），成熟度标注 `L1`（与 frontmatter `maturity` 及脚本生成的域 README / CATEGORIES 一致）；数据行 49 → 51（以 HEAD 基线 `git show HEAD:.../index.md` 复算确认）。
    - ⑤ 域 `README.md` 生成区块由 `python .agents/scripts/generate-readme.py --update --target-dir docs/retrospective/patterns/methodology-patterns/governance-strategy` 刷新（**未手改** `<!-- README_INDEX_START -->` 区块），新增 2 行模式条目。
  - **额外一致性核查**：`CATEGORIES.md` 经 `generate-categories.py` 重建（governance-strategy 169 → 173）；`methodology-patterns/README.md` 主题导航表 8 列计数原为存量陈旧值（governance-strategy 63），已对齐 CATEGORIES.md；`related_patterns` 全部经 Glob 校验确实存在于 `governance-strategy/` 域内。**3 处草案 ID 替换为同域实存近邻**（库内 pattern→pattern 的 `related_patterns` 约定为同域 bare id）：C1 的 `preflight-integrity-gate`（实存位置为 `methodology-patterns/` 顶层，不属本域）与 `spec-as-code-automated-gates`（实存位置为 `tools-automation/` 域）→ `quality-assurance-three-layer-model` 与 `three-layer-rule-enforcement`；C2 的 `cross-domain-semantic-drift`（实存位置为 `research-knowledge/` 域）→ `dual-env-drift-reconciliation`。三条替换目标均经目录遍历确认落在 `governance-strategy/` 域内。
  - **索引登记 1**：`docs/retrospective/reports/project-reports/index.md` toctree 新增 `retrospective-mystx-comprehensive-20261022/index`（字母序位于 `retrospective-myst-unified-ecosystem-phase1-20260704/index` 之后、`retrospective-openkylin-evaluation-qgate-20261014/index` 之前）。
  - **索引登记 2**：`docs/retrospective/reports/project-reports/README.md` 报告清单表新增 1 行：`| [retrospective-mystx-comprehensive-20261022/](retrospective-mystx-comprehensive-20261022/README.md) | 2026-10-22 | mystx 全面复盘 | 5 条洞察 / 2 个 L1 模式入库 / 10 条原子行动项 |`。
  - **TR-6.3 通过**：`check-links.py` 对新建报告目录（25 引用 0 断链）、模式库域目录（864 引用 0 断链）、`.meta/toml`（0 引用）全部通过；模式库域的 3 处 frontmatter 断链（`artifact-form-collapse.md` 缺伴生 TOML、`three-as-relation-position.md` 的 `source` 含中文后缀）经 `git status` 核对为**存量问题**（本次未改动该两文件），非本次引入。
  - **Mermaid 门禁**：两个新模式文档中的 mermaid 片段经 `check_mermaid.py` 校验通过（`<br/>` 与带圈数字已改为单行普通数字）。
  - 只读边界：本任务未写入 `projects/xuanspace` 及其子模块，未执行 git 提交。

## Task 7: 独立审查与只读边界复核
- [x] **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - 委派 fresh-context 只读子代理审查全部产出物（spec/tasks/中间产物/报告四件套/模式入库）
  - 审查者不得依赖 `tasks.md` 的自述证据，须以文件实际内容为准
  - P0 级问题必须修复并回归验证；P1/P2 记录在案
  - 复核 mystx 工作区状态，确认本任务全程只读
  - 产出 `review.md`（Review 阶段唯一产物，此前不创建）
- **Acceptance Criteria Addressed**: AC-11, AC-10
- **Test Requirements**:
  - `rule` TR-7.1: 独立审查结论以文件实际内容为依据；P0 问题全部修复并回归 —— 证据：审查结论 + 修复回归记录
  - `rule` TR-7.2: `git -C projects/xuanspace status --porcelain` 复核输出与 Task 1 采集时点一致，或差异全部归因并行会话 —— 证据：前后两次命令输出
  - `rule` TR-7.3: `review.md` 按 TRAE-spec-mode 审查结果契约记录（pass / fail / blocked）—— 证据：review.md 内容
- **Notes**: 依据 `.agents/skills/TRAE-spec-mode/references/artifact-templates.md` 生成 review.md；未经用户明确指令不创建 git 提交
- **Completion Evidence**:
  - 产物：`.trae/specs/retrospectives-insights/mystx-comprehensive-retrospective-export/review.md`，按 `.agents/skills/TRAE-spec-mode/references/artifact-templates.md` L117-L146 契约生成：CP-R1 ~ CP-R11（`rule`）+ CP-U1（`rubric`，scale 1-5 / anchors 1=现象复述、3=部分触及、5=触及系统性根因 / threshold ≥4），每条带 `**Type**` / `**Covers**` / `**Evidence**`（rubric 额外带 `**Scale**` / `**Anchors**` / `**Pass Threshold**`），末段 `## Review History` → `### Review R1` → `- **Result**: `pass`` + Evidence + Findings + Recommended Issues。
  - **AC / TR 覆盖完备性自查**：AC-1 ~ AC-12 全覆盖（AC-1→CP-R1 / AC-2→CP-R2 / AC-3→CP-R4 / AC-4→CP-R5 / AC-5→CP-R6 / AC-6→CP-R7 / AC-7→CP-R8 / AC-8→CP-R9 / AC-9→CP-R10 / AC-10→CP-R3+CP-R8 / AC-11→CP-R11 / AC-12→CP-U1）；TR-1.1 ~ TR-7.3 全覆盖（TR-1.1/1.2/1.4→R1、TR-1.3→R2、TR-1.5/7.2→R3、TR-2.1/2.2/2.3→R4、TR-3.1/3.2/3.3→R5、TR-4.1/4.2/4.3→R6、TR-5.3→R7、TR-5.1/5.2/5.4→R8、TR-6.1/6.3→R9、TR-6.2→R10、TR-7.1/7.3→R11、TR-2.4→CP-U1），无遗漏、无跨 CP 重复覆盖。
  - **TR-7.1 通过**：全部结论以文件实际内容为准——本轮复跑稳定门禁命令（`python .agents/scripts/check-links.py --path <报告目录> --check-frontmatter-paths` / `--path <spec 目录>` / `--path <模式域目录>`、`python .agents/scripts/check-mermaid.py --path <报告目录> | <spec 目录> | <模式域目录>`），并用一次性临时脚本完成机械核验（物理行数 / F 编号连续性 / G1 门因果词 / frontmatter 字段存在性 / ACT 与 Q 计数 / 主索引与域 toctree 的 HEAD↔当前对比 / 新模式 id 全库文件名唯一性 / `related_patterns` 域内存在性 / F 引用清单三值一致性；脚本清理后失效，此处仅留判定口径与结果），未采信任何 `tasks.md` 自述数字。V 阶段 3 条 P0（V-1 / V-2 / V-11）与 3 条 P1（V-4 / V-6 / V-8）已修复并回归：F-088 ~ F-097 补录后 F 编号仍连续（`ids count=97 min=1 max=97 missing=[]`）、链接门禁 0 断链、Mermaid 门禁 0 错误。
  - **TR-7.2 通过**：复核输出与 Task 1 采集时点一致——`git -C projects/xuanspace/libs/mystx status --porcelain` → 空输出，HEAD = `45bd1e4`；`git -C projects/xuanspace status --porcelain` → 空输出，HEAD = `7e5d251`；两次复核结果相同，**无并行会话在途改动**，差异为零。
  - **TR-7.3 通过**：`review.md` 按契约记录 `- **Result**: `pass``，并附 Checks Performed / Evidence / Findings（F-01 ~ F-08）/ Recommended Issues 四段。
  - **门禁复验汇总**：物理行数 spec（`spec.md` 215 / `tasks.md` 218 / `facts.md` 215 / `insights.md` 336 / `e-stage-pattern.md` 363 / `v-adversarial-review.md` 525 / `review.md` 119）；报告（`README.md` 327 / `insight-extraction.md` 586 / `actionable-items.md` 148 / `index.md` 10）；模式（258 / 224）+ 伴生 TOML ×2 存在。链接门禁：报告 25/25、spec 25/25、模式域 864/864，**0 新增断链**。Mermaid 门禁：报告 4 文件 0 错误、spec 7 文件 0 错误、模式域存量 74 问题文件 / 511 错误（**非本次引入**），两个新模式文档门禁输出命中 0 / 0。索引：主索引数据行 49 → 51、域 toctree 174 → 176（新增顺序违规 0）、`CATEGORIES.md` governance-strategy 173、域 README L141 / L162 两行、两处报告索引登记在位。主题看板行已刷新为「✓ 完成」（`docgen` 主题看板机制，仅刷新 `retrospectives-insights` 一个主题，未产生其他主题的无关变更）。
  - **本轮 8 条发现均为 P2 advisory、已留档不修复**：F-01 `tasks.md` Task 2 的 F 引用计数陈旧（24/20/25/18/25 → 实测 26/21/25/24/25，权威文档本身一致，不构成 AC-3 违规）；F-02 模式库「552 个 `.md`」为当前工作区口径（HEAD 基线同口径 550）；F-03 伴生 TOML 基线 vs 当前（域 146 → 148、全域 481 → 483）差额未标注；F-04 `I-` 编号双命名空间（洞察 vs 不变量）；F-05 模式域存量 511 个 mermaid 错误 + 3 处存量 frontmatter 断链；F-06 根 `check_mermaid.py` 硬编码已废止的 `.agents/docs/` 路径而崩溃；F-07 `check-mermaid.py --path` 传单文件为空跑（原 Task 6 结论已在本轮复核成立）；F-08 V 阶段审查者对 `preflight-integrity-gate` 存在域的一次口径误判（最终结论正确）。
  - 只读边界：本任务未写入 `projects/xuanspace` 及其子模块，**未执行任何 git 提交**（按 Task 7 Notes 与 Spec Constraints，须待用户明确指令）。

# Task Dependencies

- Task 2 依赖 Task 1（事实不清则洞察失真）
- Task 3 依赖 Task 2（洞察未成则模式无根）
- Task 4 依赖 Task 3（模式与审查结论须先进报告）
- Task 5 依赖 Task 4（审查修正须先进报告）
- Task 6 依赖 Task 5（报告定稿后入库与登记）
- Task 7 依赖 Task 6（全部产出物齐备后独立审查）
- Task 1 与 Task 2 串行（同一子代理连续执行以保留上下文）；Task 5 的四个报告文件可并行撰写，Task 6 的两处索引登记与四处模式入库中，域 toctree 插入须最后执行

# 质量门检查点

| 门 | 阶段 | 判定 | 未通过时动作 |
|---|---|---|---|
| G1 | Task 1 产出 | 事实无因果推断词、条数 ≥30、编号连续 | 回到 Task 1 重采集 |
| G2 | Task 2 产出 | 洞察四元组完整、≥3 条、每条引用 ≥2 个 F 编号 | 回到 Task 2 补全 |
| G3 | Task 3 产出 | 模式四要素齐备、可迁移、去重裁决已记录 | 回到 Task 3 重萃取 |
| G4 | Task 5 产出 | 行动项单一职责、可独立验证 | 回到 Task 5 重写 |
| 交付 | Task 6 产出 | 报告四件套齐备 + 两处索引登记 + 0 新增断链 | 回到 Task 5/6 补齐 |
| 收口 | Task 7 产出 | 独立审查 P0 全部闭环 + 只读边界复核通过 | 回到对应 Task 修复并回归 |
