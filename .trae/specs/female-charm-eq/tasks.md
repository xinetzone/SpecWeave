# 提高女性魅力与情商 OKF 知识包 - Implementation Plan

> 依据七概念方法论（知识沉淀场景 R→I→E→V→C）编排：R（事实采集，已完成）→ I（洞察，写入 insights.md）→ E（三层结构萃取）→ V（对抗审查，纳入实施中逐条自查）→ C（质量门 + 索引对账闭环）。

## Task 1: 创建分组与 bundle 骨架
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建 `doc/bundles/sheke/personal-growth/index.md`（分组根 index，`type: group`，声明 `total_bundles: 1`，`{toctree}` 引用 `female-charm-eq/index`）。
  - 创建 `doc/bundles/sheke/personal-growth/female-charm-eq/index.md`（bundle 根，`type: OKF`，含完整 frontmatter：okf_version/sources/generated/status/stale_after）。
  - 创建三层目录及各自 `index.md`：`concepts/`、`examples/`、`references/`。
  - 创建工作文档 `facts.md`、`insights.md`、`log.md`（骨架先行，内容在 Task 2-4 填充）。
- **Acceptance Criteria Addressed**: AC-1, AC-5
- **Test Requirements**:
  - `rule` TR-1.1: 目录树存在且分组 index、bundle index、三层 index 均已创建，frontmatter 含非空 `type`。证据：Glob 列目录 + Read 抽查（独立 Review CP-R1 pass）。
  - `rule` TR-1.2: bundle 根与三层 `index.md` 均含 `{toctree}`。证据：Read 检查（独立 Review CP-R1 pass）。
- **Notes**: 分组定位「个人成长与自我提升」，与 relationships（经典著作解读）区分；锚点组模式与 finance/marketing 同构。
- **Completion Evidence**: 分组 index、bundle 根 index、三层 index（concepts/examples/references）、facts/insights/log 全部创建于 `doc/bundles/sheke/personal-growth/`；toctrees 检查通过（独立 Review 复核）。

## Task 2: 撰写 concepts 概念文档（魅力 × 情商理论）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - `concepts/00-overview.md` — 总览：魅力×情商为什么值得学、证据分级说明、知识地图。
  - `concepts/01-attraction-science.md` — 吸引力科学（F-01~F-08）：接近性、曝光效应、相似性、互惠、光环效应、吊桥效应（含批判）。
  - `concepts/02-charisma-models.md` — 魅力模型（F-09~F-12）：韦伯魅力、Cabane 三要素（临在/力量/温暖）、Riggio 六技能、CLT 训练证据。
  - `concepts/03-first-impression.md` — 第一印象与自我呈现（F-13~F-18）：薄片判断、100ms 判断、温暖-能力双维（含 Asch 复制失败）、Goffman 拟剧论。
  - `concepts/04-eq-ability-model.md` — 情商能力模型（F1~F8）：Salovey/Mayer、MSCEIT 四分支。
  - `concepts/05-eq-mixed-model.md` — 情商混合模型与争议（F4/F6/F22~F27）：Goleman 五要素、Locke 批判、人格重叠、增量效度。
  - `concepts/06-emotional-awareness.md` — 情绪觉察与命名（F9~F13）：情绪粒度、情绪标注、REBT ABC。
  - `concepts/07-empathy.md` — 共情（F14~F17）：认知/情感共情、共情-利他、共情疲劳。
  - `concepts/08-emotion-regulation.md` — 情绪调节（F18~F21）：Gross 过程模型、重评 vs 抑制、正念。
  - `concepts/09-boundaries-confidence.md` — 界限与自信（实操 F6~F14）：心理边界、讨好型、冒充者现象、自我慈悲、power posing 争议。
- **Acceptance Criteria Addressed**: AC-1, AC-4
- **Test Requirements**:
  - `rule` TR-2.1: concepts/ 下存在 10 个概念文档（00~09），每个含 frontmatter（type 非空）且事实标注 F-xxx 编号可回溯 facts.md。证据：Glob + Read 抽查（独立 Review CP-R1 确认 10 篇存在、编号可回溯）。
  - `rubric` TR-2.2: 证据分级质量。Scale 1-5；1=无分级；3=部分标注；5=全篇共识/单研/通俗三层明确，Goleman 争议与 power posing 批判如实呈现。Threshold >= 4。
- **Notes**: 事实编号沿用调研清单（魅力 F-01~F-26、情商 F1~F27、实操 F1~F28）；若两清单编号冲突，在 facts.md 统一映射。
- **Completion Evidence**: 10 篇概念文档（00-overview~09-boundaries-confidence）创建完成；独立 Review CP-U1 证据分级 5/5、反常识批判 5/5（Goleman 争议 EQ-22~26、power posing PR-13、Asch CM-16 均如实呈现）。

## Task 3: 撰写 examples 实操文档
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - `examples/00-overview.md` — 实操总览与 30 天训练路线（渐进暴露原理）。
  - `examples/01-communication.md` — 沟通与倾听：积极倾听四级、NVC 四要素、真诚赞美（F1~F5）。
  - `examples/02-boundary-setting.md` — 界限设定：语言模板、三分类、职场/关系场景脚本（F6~F9，含女性反冲实证提示）。
  - `examples/03-confidence-training.md` — 自信训练：冒充者应对、自我慈悲三成分、日常微练习（F10~F14）。
  - `examples/04-workplace.md` — 职场应用：温暖×能力、断言性沟通、双重束缚与缓解策略（F18~F21）。
  - `examples/05-relationships.md` — 亲密关系与约会场景：需求表达、目光接触、第一印象实操（F15~F17）。
- **Acceptance Criteria Addressed**: AC-1, AC-4
- **Test Requirements**:
  - `rule` TR-3.1: examples/ 下存在 6 个文档，每个含 frontmatter 且含可直接复用的模板/脚本/步骤。证据：Glob + Read 抽查（独立 Review CP-U1 实操可落地 5/5）。
  - `rubric` TR-3.2: 实操可落地性。Scale 1-5；1=空泛建议；3=有步骤无模板；5=每个场景含可直接复制的句式/脚本/每日清单。Threshold >= 4。
- **Completion Evidence**: 6 篇实操文档创建完成；独立 Review 确认 examples/01 含复述句式+NVC 模板+对照表、examples/03 含自查 5 问+重构对照表+微练习清单（CP-U1 实操可落地 5/5）。

## Task 4: 撰写 references 信源与工作文档
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - `references/00-books.md` — 核心书目（学术层：Goleman、Gross 综述、Neff；通俗层：Cabane、蔡康永《情商课》，标注层级）。
  - `references/01-studies.md` — 关键研究文献清单（F- 编号 → 论文/来源映射）。
  - 填充 `facts.md`：汇总全部事实（魅力 26 + 情商 27 + 实操 28 ≈ 81 条，按域分组编号）。
  - 填充 `insights.md`：4 条四元组洞察（陈述/证据/反常识/行动）+ Mermaid 知识地图。
  - 填充 `log.md`：首条更新记录 `2026-09-14`。
- **Acceptance Criteria Addressed**: AC-1, AC-4
- **Test Requirements**:
  - `rule` TR-4.1: references/ 存在 2 个文档；facts.md 事实编号 ≥ 40 条且每条含信源；insights.md 含 ≥ 3 条四元组洞察；log.md 含日期条目。证据：Read 统计（独立 Review 确认 81 条事实、4 条洞察）。
  - `rule` TR-4.2: 每篇正文引用的 F-xxx / F-编号在 facts.md 中可查。证据：抽查 5 处交叉引用（独立 Review Grep 验证 5+ 处命中）。
- **Completion Evidence**: references/00-books（学术/通俗双层书目）、01-studies（20 条研究表）创建；facts.md 81 条事实（CM-01~26/EQ-01~27/PR-01~28）补齐 4 条缺失来源后 81/81 全覆盖；insights.md 4 条四元组洞察+Mermaid；log.md 含 2026-09-14 条目。

## Task 5: 同步分组与总索引五面对账
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Tasks 1-4
- **Description**:
  - 更新 `doc/bundles/sheke/index.md`：分组导航表新增 `[🌱 个人成长与自我提升](personal-growth/index.md)` 行，toctree 新增 `personal-growth/index`。
  - 更新 `doc/bundles/index.md`：frontmatter `total_bundles: 534→536`、`groups: 58→59`；计数行「536 个知识包 / 9 个学科域、59 个分组」；sheke 域节标题「35 束 · 6 组」→「36 束 · 7 组」；sheke 分组表新增 personal-growth 行（束数 1）；末尾 toctree 不变（sheke 已在列）。
  - 核对 `check-bundles-index.py` 的锚点组口径：personal-growth 为锚点组（直接含 concepts/examples/references 子目录的 female-charm-eq 视为 1 束），总索引该行束数=1。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-5
- **Test Requirements**:
  - `rule` TR-5.1: `python scripts/check-bundles-index.py` 退出码 0，输出「…域 / …组 / …束，frontmatter、计数行、节标题、分组表、toctree 五面一致」。证据：命令输出（实测「9 域 / 59 组 / 536 束」）。
  - `rule` TR-5.2: `python scripts/check-toctrees.py` 退出码 0。证据：命令输出。
- **Completion Evidence**: sheke/index.md 分组导航+toctree 已更新；bundles/index.md 五面对账完成（total_bundles=536/groups=59/sheke 36 束 7 组/personal-growth 行束数 1）；check-bundles-index.py 输出「9 域 / 59 组 / 536 束」通过。注：基线 HEAD 本身存在 frontmatter 534 vs 树 535 的历史漂移，已随本次对账一并修正。

## Task 6: 质量门全量验证
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 运行 `invoke gates.all`（或逐项 `python scripts/check-utf8.py`、`check-toctrees.py`、`check-bundles-index.py`）。
  - 逐篇抽查新文档 frontmatter 合规（type 非空、日期裸格式、无 file:/// 绝对路径、相对路径引用正确）。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4
- **Test Requirements**:
  - `rule` TR-6.1: gates.all 全绿（UTF-8 / toctrees / bundles 三检查全部通过）。证据：命令输出（三项退出码 0）。
  - `rule` TR-6.2: 抽查 10+ 篇新文档 frontmatter 合规、正文相对路径引用无 `file:///`。证据：Read 抽查记录（独立 Review CP-R1 抽查 6 个文件 + 全目录 Grep `file:///` 零匹配）。
- **Completion Evidence**: `check-utf8.py`（10196 文件通过）、`check-toctrees.py`（全可达）、`check-bundles-index.py`（9 域/59 组/536 束五面一致）三项全绿；独立 Review 全部检查点 pass。

## Task Dependencies
- Task 1 → Task 2/3/4（并行前提）
- Task 2/3/4 相互独立，可并行
- Task 1-4 → Task 5 → Task 6
