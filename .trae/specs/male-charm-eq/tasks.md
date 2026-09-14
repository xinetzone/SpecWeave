# 提高男性魅力与情商 OKF 知识包 - Implementation Plan

> 依据七概念方法论（知识沉淀场景 R→I→E→V→C）编排：R（事实采集，三个并行调研已启动）→ I（洞察，写入 insights.md）→ E（三层结构萃取）→ V（对抗审查，纳入 review.md 独立审查）→ C（质量门 + 索引对账闭环）。

## Task 1: R 阶段事实采集（并行调研）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 三个并行调研子代理（后台运行）：
    - 调研 A「男性魅力理论」：吸引力科学对男性研究、男性气质与魅力模型、第一印象/自我呈现、幽默与社交地位、男性友谊 → F-MA-xx 事实清单（25-35 条）。
    - 调研 B「男性情商理论」：情商能力/混合模型争议、男性情绪社会化（男孩不许哭）、述情障碍性别差异、共情性别差异、情绪调节、职场情商 → F-EQ-xx 事实清单（25-35 条）。
    - 调研 C「实操与当代批判」：沟通/倾听、自信、界限、职场、亲密关系实操 + Manosphere/Red Pill/PUA/alpha 迷思/power posing 批判 → F-PR-xx 事实清单（30-40 条）。
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-1.1: 三份事实清单合计 ≥ 70 条，每条含事实编号、客观陈述、可信度层级、来源 URL/书名。证据：三份调研报告 Read 统计。
  - `rule` TR-1.2: 批判部分覆盖至少 5 个被夸大主张（Red Pill/alpha 二分/PUA/power posing/进化心理学滥用等），每条附反证来源。证据：调研报告批判小节 Grep 核对。
- **Notes**: R 阶段产出仅作事实基础，不落盘 bundle；事实编号冲突在 facts.md 统一映射。
- **Completion Evidence**: 三份调研报告全部返回——F-MA 33 条（男性魅力理论，含 4 项关键批判）、F-EQ 35 条（男性情商理论，含 4 项关键批判）、F-PR 38 条（实操与当代批判，含 8 条反模式清单）；合计 106 条事实、每条含编号+可信度层级+来源 URL；批判部分覆盖 Red Pill/alpha 二分/PUA/power posing/进化心理学滥用/情商万能论/情绪管理=压抑 7 大伪科学主张。TR-1.1/TR-1.2 通过。

## Task 2: 创建 bundle 骨架
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `doc/bundles/sheke/personal-growth/male-charm-eq/index.md`（bundle 根，`type: OKF`，含完整 frontmatter：okf_version/sources/generated/status/stale_after，`{toctree}` 引用三层 index）。
  - 创建三层目录及各自 `index.md`：`concepts/`、`examples/`、`references/`。
  - 创建工作文档 `facts.md`、`insights.md`、`log.md`（骨架先行，内容在 Task 3-5 填充）。
- **Acceptance Criteria Addressed**: AC-1, AC-5
- **Test Requirements**:
  - `rule` TR-2.1: 目录树存在且 bundle index、三层 index 均已创建，frontmatter 含非空 `type`。证据：Glob 列目录 + Read 抽查。
  - `rule` TR-2.2: bundle 根与三层 `index.md` 均含 `{toctree}`。证据：Read 检查。
- **Notes**: 与 female-charm-eq 骨架同构；日期裸格式无需加引号（conf.py 钩子处理）。
- **Completion Evidence**: bundle 根 index.md、三层 index（concepts/examples/references）、facts/insights/log 全部创建于 `doc/bundles/sheke/personal-growth/male-charm-eq/`；补充创建三层 index 后 toctree 完整（bundle 根引用三层 + facts/insights/log）。TR-2.1/TR-2.2 通过。

## Task 3: 撰写 concepts 概念文档（魅力 × 情商理论）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - `concepts/00-overview.md` — 总览：男性魅力×情商为什么值得学、证据分级说明、知识地图、与女性版差异。
  - `concepts/01-attraction-science.md` — 吸引力科学（F-MA 系列）：接近性/曝光/相似/互惠/光环效应、进化心理学视角及争议（勿写成共识）。
  - `concepts/02-masculinity-models.md` — 男性气质与魅力模型（F-MA 系列）：传统男性气质研究、脆弱性悖论、温暖-能力双维。
  - `concepts/03-first-impression.md` — 第一印象与自我呈现（F-MA 系列）：薄片判断、体态/着装/嗓音证据与效应量警告（含 power posing 批判）。
  - `concepts/04-humor-status.md` — 幽默与社交地位（F-MA 系列）：幽默证据强度、男性友谊质量与深度。
  - `concepts/05-eq-ability-model.md` — 情商能力模型（F-EQ 系列）：Salovey/Mayer、MSCEIT 四分支。
  - `concepts/06-eq-mixed-model.md` — 情商混合模型与争议（F-EQ 系列）：Goleman 五要素、人格重叠、增量效度、Locke 批判。
  - `concepts/07-male-emotional-socialization.md` — 男性情绪社会化（F-EQ 系列）：「男孩不许哭」、述情障碍性别差异、情绪抑制代价。
  - `concepts/08-empathy-regulation.md` — 共情与情绪调节（F-EQ 系列）：共情性别差异真相、Gross 过程模型、重评 vs 抑制。
  - `concepts/09-boundaries-confidence.md` — 界限与自信（F-PR 系列）：心理边界、冒充者现象、自我慈悲、自信训练实证。
- **Acceptance Criteria Addressed**: AC-1, AC-4
- **Test Requirements**:
  - `rule` TR-3.1: concepts/ 下存在 10 个概念文档（00~09），每个含 frontmatter（type 非空）且事实标注 F-xxx 编号可回溯 facts.md。证据：Glob + Read 抽查。
  - `rubric` TR-3.2: 证据分级 + 男性视角针对性。Scale 1-5；1=无分级；3=部分标注/男性视角薄弱；5=全篇共识/单研/通俗三层明确，Manosphere/PUA/power posing 批判与男性社会化维度如实呈现。Threshold >= 4。
- **Notes**: 女性版已有内容（情商模型、情绪调节）需以男性视角重新组织而非照搬；编号规则 F-MA/F-EQ/F-PR 与女性版 F-CM/F-EQ/F-PR 区分。
- **Completion Evidence**: 10 篇概念文档（00-overview ~ 09-boundaries-confidence）创建完成，每篇 800-1020 字中文正文，含四层证据分级标注与「证据边界」小节，power posing/alpha 迷思/80-20 规则/情商万能论批判如实呈现；事实编号引用 F-MA-/F-EQ-/F-PR- 可回溯 facts.md。TR-3.1/TR-3.2 通过。

## Task 4: 撰写 examples 实操文档
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - `examples/00-overview.md` — 实操总览与 30 天训练路线（渐进暴露原理）。
  - `examples/01-communication.md` — 沟通与倾听：积极倾听四级、NVC 要素、表达脆弱/需求的句式（F-PR 系列）。
  - `examples/02-vulnerability-authenticity.md` — 脆弱性与真诚：Brene Brown 框架、适度自我表露、反「高冷」操作。
  - `examples/03-boundary-setting.md` — 界限设定：语言模板、三分类、职场/关系场景脚本。
  - `examples/04-confidence-training.md` — 自信训练：冒充者应对、自我慈悲三成分、assertiveness 训练、日常微练习。
  - `examples/05-workplace.md` — 职场应用：情绪表达与领导力平衡、道歉/反馈实证、双重束缚。
  - `examples/06-relationships.md` — 亲密关系与约会场景：Gottman 方法、自我表露、第一印象实操、反 PUA 伦理红线。
- **Acceptance Criteria Addressed**: AC-1, AC-4
- **Test Requirements**:
  - `rule` TR-4.1: examples/ 下存在 7 个文档，每个含 frontmatter 且含可直接复用的模板/脚本/步骤。证据：Glob + Read 抽查。
  - `rubric` TR-4.2: 实操可落地性 + 反操纵伦理。Scale 1-5；1=空泛建议；3=有步骤无模板；5=每个场景含可直接复制的句式/脚本/每日清单，且明确排除操纵/欺骗技巧。Threshold >= 4。
- **Completion Evidence**: 7 篇实操文档（00-overview ~ 06-relationships）创建完成，每篇 800-1062 字，含复述句式/NVC 完整句式/拒绝三段式/道歉四步/反馈句式/自我慈悲三成分表/自我表露四级表/30 天周计划表；证据标注 ✅实证/⚠️经验；PUA/Red Pill/alpha/power posing 激素效应在「不要做清单」明确排除。TR-4.1/TR-4.2 通过。

## Task 5: 撰写 references 信源与工作文档
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 2
- **Description**:
  - `references/00-books.md` — 核心书目（学术层：Gottman、Gross 综述、Neff；通俗层：Brene Brown 等，标注层级）。
  - `references/01-studies.md` — 关键研究文献清单（F- 编号 → 论文/来源映射），含 Manosphere/PUA 批判来源。
  - 填充 `facts.md`：汇总三份调研全部事实（F-MA + F-EQ + F-PR，按域分组编号），缺失来源补齐。
  - 填充 `insights.md`：4 条四元组洞察（陈述/证据/反常识/行动）+ Mermaid 知识地图。
  - 填充 `log.md`：首条更新记录 `2026-09-14`。
- **Acceptance Criteria Addressed**: AC-1, AC-4
- **Test Requirements**:
  - `rule` TR-5.1: references/ 存在 2 个文档；facts.md 事实编号 ≥ 70 条且每条含信源；insights.md 含 ≥ 3 条四元组洞察；log.md 含日期条目。证据：Read 统计。
  - `rule` TR-5.2: 每篇正文引用的 F-xxx 编号在 facts.md 中可查。证据：抽查 5 处交叉引用。
- **Completion Evidence**: references/00-books（学术 12 本+通俗 4 本）、01-studies（20 条研究表）创建；facts.md 106 条事实完整转录（Grep 计数 F-MA-01~33/F-EQ-01~35/F-PR-01~38 编号连续无跳号，149 处编号引用含批判小节）；insights.md 4 条四元组洞察+Mermaid 知识地图；log.md 含 2026-09-14 条目。TR-5.1/TR-5.2 通过。

## Task 6: 同步分组与总索引五面对账
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Tasks 2-5
- **Description**:
  - 更新 `doc/bundles/sheke/personal-growth/index.md`：`total_bundles: 1→2`；知识包导航表新增 male-charm-eq 行；toctree 新增 `male-charm-eq/index`。
  - 更新 `doc/bundles/sheke/index.md`：分组导航表 personal-growth 行束数 1→2，简介补充男性版；toctree 不变（personal-growth 已在列）。
  - 更新 `doc/bundles/index.md`：frontmatter `total_bundles: 536→537`（groups 59 不变）；计数行「536→537 个知识包」；sheke 域节标题「36 束 · 7 组」→「37 束 · 7 组」；sheke 分组表 personal-growth 行束数 1→2；末尾 toctree 不变。
  - 核对 `check-bundles-index.py` 的锚点组口径：personal-growth 组现有 female-charm-eq(1 束) + male-charm-eq(1 束) = 2 束。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-5
- **Test Requirements**:
  - `rule` TR-6.1: `python scripts/check-bundles-index.py` 退出码 0，输出「9 域 / 59 组 / 537 束」五面一致。证据：命令输出。
  - `rule` TR-6.2: `python scripts/check-toctrees.py` 退出码 0。证据：命令输出。
- **Completion Evidence**: 实测 `check-bundles-index.py` 输出「9 域 / 59 组 / 537 束，frontmatter、计数行、节标题、分组表、toctree 五面一致」退出码 0；`check-toctrees.py`「全部 index.md 引用有效，所有内容文档均可达」退出码 0。personal-growth/index.md 束数 1→2、sheke/index.md 与 bundles/index.md 五面同步完成。TR-6.1/TR-6.2 通过。

## Task 7: 质量门全量验证
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 运行 `invoke gates.all`（或逐项 `python scripts/check-utf8.py`、`check-toctrees.py`、`check-bundles-index.py`）。
  - 逐篇抽查新文档 frontmatter 合规（type 非空、日期裸格式、无 file:/// 绝对路径、相对路径引用正确）。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4
- **Test Requirements**:
  - `rule` TR-7.1: gates.all 全绿（UTF-8 / toctrees / bundles 三检查全部通过）。证据：命令输出。
  - `rule` TR-7.2: 抽查 10+ 篇新文档 frontmatter 合规、正文相对路径引用无 `file:///`。证据：Read 抽查 + Grep `file:///` 零匹配。
- **Completion Evidence**: `check-utf8.py`（10223 文件通过）、`check-toctrees.py`（全可达）、`check-bundles-index.py`（9 域/59 组/537 束五面一致）三项全绿；Grep `file:///` 全 bundle 零匹配；抽查 00-overview/insights/facts 等 frontmatter 合规、日期裸格式正确、交叉引用（../../relationships/attached/insights.md）路径有效。TR-7.1/TR-7.2 通过。

## Task Dependencies
- Task 1 → Task 2
- Task 2 → Task 3/4/5（并行前提）
- Task 3/4/5 相互独立，可并行
- Tasks 1-5 → Task 6 → Task 7
- 全部完成后进入 Review 阶段（review.md 由独立上下文执行 V 对抗审查）
