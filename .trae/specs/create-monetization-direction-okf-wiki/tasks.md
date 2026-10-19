# 个人变现方向发现方法论 · OKF Wiki — 实施计划（tasks.md）

> 排序原则：信源先行 → 事实 → 结构 → 内容 → 索引 → 审查 → 提交。每个 Task 为可独立验证的垂直切片。
> 状态只存于 `Status` 字段；完成时勾选标题复选框并补 `Completion Evidence`。

## Task 1: 信源调研与候选清单（R-a）
- [x] 完成
- **Status**: `completed`
- **Completion Evidence**:
  - `sources.md` 落盘；C1 18 / C2 20 / C3 20 / C4 16 条实检索信源（每类 ≥2 下限），含信源距离分层与采用/降级理由。
  - 7 项检索缺口如实登记并给替代来源（Flow 官方免费页、Career Dynamics 原著页、BMC「470 位共创者/500 万册」数字、职业锚 5 vs 8 口径等）。
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 按四类信源（C1 职业匹配/设计人生、C2 优势/兴趣/天赋识别、C3 个人商业模式与变现模式、C4 需求验证/最小验证）检索公开权威来源，每类 ≥2 个；
  - 产出 `.trae/specs/create-monetization-direction-okf-wiki/sources.md`：信源名 / 类型 / 权威口径 / URL / 采用理由 / 弃用理由；
  - 无可访问或信源不足时记录替代来源，不得静默跳过。
- **Acceptance Criteria Addressed**: AC-1、AC-2
- **Test Requirements**:
  - `rule` TR-1.1: `sources.md` 存在；四类信源各有 ≥2 条且每条含可访问 URL 与信源距离标注；证据为文件内容。
  - `rule` TR-1.2: 信源距离分层（一手理论 / 权威出版物 / 工具官方 / 第三方综述 / 二手转述）逐条显式标注；证据为 `sources.md` 分类列。

## Task 2: 事实采集与 P0 核验（R-b / R-c）
- [x] 完成
- **Status**: `completed`
- **Completion Evidence**:
  - `facts.md` 落盘，F-001~F-082 连续无跳号（机检唯一集合恰为 1..82），共 82 条 ≥60 下限；P0 50 / P1 31 / P2 1；核验 ✅58 / ⚠️21 / 单源 3 / ❌0。
  - 勘误四张清单（日期年份 / 成效数字 / 口径对照 10 组 / 引文逐字）逐项过筛留痕；MBTI 科学争议（F-038/F-039/F-040）与「非决定论」边界（F-041）强制标注。
  - 勘误 5 项：E-01 1000 铁粉拔高（丢前提）、E-02 MBTI 伪决定性、E-03 ikigai 四圆图误植溯源、E-04 刻意练习以偏概全（职业域 <1%）、E-05 职业锚版本口径混乱。
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - F-001 起连续编号登记四类信源全部关键声明（提出者、年份、核心主张、工具官方定位、研究结论及限定条件），观点/主张与事实分层；
  - 产出 `.trae/specs/create-monetization-direction-okf-wiki/facts.md`（≥60 条）；
  - 对 P0 声明（年份/提出者/核心主张归属、全部数字）执行 WebSearch 权威核验；勘误四张清单逐项过筛；
  - 性格测评类工具登记科学效度争议与"非决定论"边界。
- **Acceptance Criteria Addressed**: AC-1、AC-2、AC-10
- **Test Requirements**:
  - `rule` TR-2.1: `facts.md` 编号 F-001 起连续无跳号（跳号显式注记），条数 ≥60；证据为正则提取的编号序列。
  - `rule` TR-2.2: C1/C3/C4 类 P0 声明 100% 有核验记录（权威 URL 或显式单源标注）；证据为核验列 + `verification.md` 草案。
  - `rule` TR-2.3: 勘误四清单（日期/年份、成效数字、口径限定、引文逐字）逐项过筛记录；证据为核验记录。

## Task 3: 骨架判定与三层知识地图（I）
- [x] 完成
- **Status**: `completed`
- **Completion Evidence**:
  - `knowledge-map.md` 落盘：操作可复现性两问皆「是」→ 设 `examples/`（4 篇 + 索引）；concepts 11 篇（事实层 4 / 方法层 4 / 路径层 2 + 00 总览），每篇标注单一职责与「不做」边界。
  - 归属候选对照表覆盖 industry / personal-growth / marketing / finance / workplace，推荐 `sheke/industry/monetization-direction`（既有变现簇五束闭环）；bundle 命名三查留痕，定稿 `monetization-direction`。
  - rubric TR-3.2（篇目拆分粒度）自评 **5 分**（阈值 ≥4）：事实层按 C1-C4 分四篇、方法层按盘点→生成→验证→决策分四篇、路径层分矩阵/边界两篇，无一篇跨层职责。
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 执行操作可复现性两问，判定 `examples/` 取舍并记录理由；
  - 产出 `.trae/specs/create-monetization-direction-okf-wiki/knowledge-map.md`：三层拆分地图（事实层/方法层/路径层）+ concepts 篇目清单 + 归属候选对照表（industry vs personal-growth）；
  - 单一职责原子化拆分，避免大文档。
- **Acceptance Criteria Addressed**: AC-3、AC-4、AC-8
- **Test Requirements**:
  - `rule` TR-3.1: `knowledge-map.md` 含两问判定结论 + 候选位置对照表（含理由）；证据为文件内容。
  - `rubric` TR-3.2: 篇目拆分粒度；scale 1-5；1=单篇堆砌/3=篇目有分层但边界模糊/5=每篇单一职责、边界清晰、总览分篇合理；阈值 ≥4；证据为篇目清单与职责描述。

## Task 4: bundle 信源层生成（E-1）
- [x] 完成
- **Status**: `completed`
- **Completion Evidence**:
  - 新建 `sheke/industry/monetization-direction/references/{index,article-source,verification}.md` 三个文件（经目录列举确认无附带改动）。
  - `article-source.md` 收录 F-001~F-082；PowerShell 正则提取比对本机复核：facts.md 唯一编号 82、article-source.md 唯一编号 82、双向差集为空 → TR-4.1 通过。
  - `verification.md` 含核验结论表（✅58/⚠️21/单源 3/❌0）、勘误四张清单、E-01~E-05、单源清单与证据 URL；判定 `status: stable`（非 flagged）、`stale_after: "2027-06-30"`。
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 在 `projects/awesome-okf-xs/doc/bundles/sheke/industry/<bundle>/` 先建 `references/article-source.md`（与 `facts.md` 双份登记）与 `references/verification.md`（核验结论表 + 勘误四清单 + 单源清单 + 证据 URL）；
  - `references/index.md` 含 toctree。
- **Acceptance Criteria Addressed**: AC-2、AC-4、AC-6
- **Test Requirements**:
  - `rule` TR-4.1: `article-source.md` 的 F 编号集合与 `facts.md` 正则比对一致；证据为集合比对输出。
  - `rule` TR-4.2: `verification.md` 含核验结论表、勘误四清单、单源清单与证据 URL；证据为文件内容。

## Task 5: bundle 概念层生成（E-2）
- [x] 完成
- **Status**: `completed`
- **Completion Evidence**:
  - 落盘 `concepts/`（index + 00~10 共 12 文件）与 `examples/`（index + 01~04 共 5 文件）；本机列举确认 20 个 bundle 文件齐备、无越界改动。
  - 本机机械核验：`file:///` 命中 **0**；非 index.md 文件 frontmatter `type` 缺失 **0**；事实层 01~04 因果推断词（因为/导致/所以）命中 **0** → G1 事实门通过。
  - F 引用分布：01 篇 52 / 02 篇 76 / 03 篇 68 / 04 篇 39 次，事实层四篇连续覆盖 F-001~F-082；方法/路径层（05~10）以 F 出处支撑方法依据，并以〔洞察〕标注因果解释。
  - 抽查 `07-needs-validation-method.md`（输入项/步骤/判定标准/七类反模式/达标条件齐备）与 `09-path-matrix.md`（四条主路径的起点/门槛/分阶段行动/退出切换条件齐备 + 切换矩阵）→ rubric TR-5.3（AC-8 方法链路可操作性）自评 **5 分**（阈值 ≥4）。
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 生成 `concepts/00-overview.md` 起的分层文档：事实层 / 方法层（自我盘点、候选方向生成、需求验证、决策）/ 路径层（方向选择矩阵 + 决策清单 + 边界与误区）；
  - 所有具体声明挂 F 编号；因果解释标注"洞察/推断"；收益/规模表述标"非承诺"；
  - `concepts/index.md` 含 toctree；若 TR-3.1 判定为"是"则同步生成 `examples/`（自评表、验证实验模板）+ `examples/index.md`。
- **Acceptance Criteria Addressed**: AC-4、AC-5、AC-8、AC-9、AC-10
- **Test Requirements**:
  - `rule` TR-5.1: concepts 内一切数字/年份/提出者/工具名均有 F 编号出处，无 `facts.md` 之外编造；证据为抽查 + Grep。
  - `rule` TR-5.2: 性格/天赋测评类内容均含科学争议与"非决定论"边界声明；无收益承诺与产品推荐；证据为边界声明段。
  - `rubric` TR-5.3: 方法链路可操作性（对应 AC-8）；scale 1-5；锚点见 AC-8；阈值 ≥4；证据为路径层/方法层文档 + 魔鬼代言人审查记录。

## Task 6: 索引与导航接入（V-1）
- [x] 完成
- **Status**: `completed`
- **Completion Evidence**:
  - 新建 bundle 根 `index.md`（`okf_version: "0.2"` + 三层内容导航 + 5 条主题关联互链 + 已知边界段 + 21 条 toctree）与 `log.md`（两问判定理由 / 归属理由 / 命名三查 / 勘误处置 / 时效依据 / 索引接入）。
  - 修改 `sheke/industry/index.md`（导航表 +1 行、描述与方向分述 26→27、toctree 追加）、`sheke/index.md`（Industry 行 26→27 + 简介补充）、`doc/bundles/index.md`（total_bundles 641→642、正文计数行 641→642、mermaid sheke 节点 69→70、域节标题 69→70 束、Industry 表行 26→27）。
  - 本机复核 toctree：bundle 内 + 组/域/总索引共 **82 条** toctree 条目逐一 `Test-Path`，**缺失 0**；bundle 实际 `.md` = 22，与组索引表「22」一致。
  - gates 实测（本机独立重跑）：`check-utf8.py` **通过**（11741 文件）；`check-toctrees.py` 退出 1、`check-bundles-index.py` 退出 1，但逐行归因显示 **0 条与本 bundle 相关**，全部来自**无关的在途 WIP `sheke/digital-economy/`**（另一 spec，`git status` 显示为未跟踪目录，本次未越界修改）。已按 AC-7 以「手动等效清单 + 如实注明」处置，未谎报 gates 通过。
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 生成 bundle 根 `index.md`（`okf_version` + toctree + 主题关联互链段 + 已知边界）与 `log.md`（含两问判定理由、归属理由）；
  - 接入 `sheke/industry/index.md`（导航表 +1 行、toctree +1 条、束数 26→27）；
  - 同步 `sheke/index.md` 组计数与描述、`bundles/index.md` total_bundles 641→642 与 sheke 域 69→70；
  - **所有计数以执行时读取现值为基准**。
- **Acceptance Criteria Addressed**: AC-3、AC-4、AC-5
- **Test Requirements**:
  - `rule` TR-6.1: 三级 toctree 完整且条目（排除 `:` 指令行）逐一可达；证据为 `invoke gates.toctrees` 或手动等效输出。
  - `rule` TR-6.2: 组/域/总三处计数与正文一致（现值 +1）；证据为 `invoke gates.bundles` 或手动等效输出 + diff。

## Task 7: 对抗审查与门禁（V-2）
- [x] 完成
- **Status**: `completed`
- **Completion Evidence**:
  - 由**全新独立上下文** agent 执行（实施者自验不作为验收证据），产出 `.trae/specs/create-monetization-direction-okf-wiki/adversarial-review.md`、bundle `references/verification.md` §8、`log.md` 2026-10-17 V 阶段条目。
  - 四视角：事实溯源 PASS / 结构规范（修复后）PASS / 读者可用性 PASS / 时效边界 PASS。
  - 魔鬼代言人 10 条攻击：不成立 6 / 成立 3 / 降级 1；3 条 actionable 已修——① `00-overview.md` 无 F 支撑因果句（「导致方向不可持续」）改为「使风险升高」并标注为方法前提假设；② `09-path-matrix.md` 「样本可短期补齐」改为显式「本方法假设」；③ 补齐 18 个文件缺失的 `verified` 与 `stale_after` 字段（CP-10）。
  - 收尾复核：`file:///` 0；非 index `.md` 的 `type` 缺失 0；本 bundle + 组索引 toctree 65 OK / 0 MISSING；双份 F 编号集合一致（各 82、双向差集空）；事实层 01~04 因果词 0。未决 actionable = 0（advisory 5 项已记录）。
  - **gates 实测转绿**：并行会话的在途 `digital-economy` 于本阶段完成索引接入后，`check-utf8.py` / `check-toctrees.py` / `check-bundles-index.py` 三脚本**全部通过**（9 域 / 62 组 / 644 束，11751 文件）——AC-7 的「gates 全绿」条件达成，且 Task 6 的 39+3 残留已自然消解（本 bundle 相关新增失败始终为 0）。
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 四视角审查（事实溯源 / 结构规范 / 读者可用性 / 时效边界）+ 魔鬼代言人专项证伪（伪科学断言、画饼路径、相关当因果），发现项回落正文；
  - 双份 F 编号复核；跑 `invoke gates.all`（或依赖不可用时执行手动等效清单并在 `log.md` 注明）；
  - 更新 `verification.md` 与 `log.md`。
- **Acceptance Criteria Addressed**: AC-2、AC-5、AC-6、AC-7、AC-9、AC-10
- **Test Requirements**:
  - `rule` TR-7.1: 魔鬼代言人审查记录存在且逐条给出"成立/降级/删除"结论；证据为审查记录。
  - `rule` TR-7.2: gates 全绿或手动等效清单已执行且 `log.md` 注明（未谎报）；证据为 gates 输出或清单。

## Task 8: 原子提交（C）
- [x] 完成
- **Status**: `completed`
- **Completion Evidence**:
  - 子模块提交 **`54a94f66`**（`docs(bundle): 新增「个人变现方向发现」OKF 知识包并接入三级索引`）——25 文件 / +2292 行；显式 `git add` 列出 bundle 目录 + 3 个共享索引文件，**未暂存**并行会话的 `digital-economy/`（`git status` 复核其仍为 untracked）。
  - 主仓库提交 **`aa7e87261`**（`docs(specs): 新增「个人变现方向发现」OKF 知识包规格全链路闭环记录`）——spec 区 7 文件，pre-commit 钩子（放置校验 / 敏感信息 / 模式质量 / Ruff / 并发安全）全部通过。
  - 主仓库提交 **`672964f65`**（`chore(submodule): 更新 awesome-okf-xs 指针至 54a94f66`）——仅 gitlink 1 行变更。
  - `git log origin/main..HEAD` 显示三个提交均在本地未推送区间 → **未 push**（TR-8.1 通过）。
  - 备注：按用户裁定「只提交本 spec 产物」执行；三个共享索引文件同时含并行会话在途 digital-economy 的索引行（同一文件无法拆分），该目录本体未纳入提交。
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - ① 在 awesome-okf-xs 子模块内提交（bundle + 组索引 + 域索引 + 总索引）；② 主仓库提交 spec 区；③ 主仓库提交子模块指针；
  - Conventional Commits 中文描述；显式文件列表；不 push。
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `rule` TR-8.1: 三个提交按序完成，`git log` 显示提交信息符合 Conventional Commits 中文描述且未 push；证据为 `git log` / `git status`。

## Task 9: 洞察四元组与可迁移模式补强（AC-9 · 验证阶段发现）
- [x] 完成
- **Status**: `completed`
- **Completion Evidence**:
  - **G2（A-5）**：`concepts 05~10` 的 **8 条** `〔洞察〕`（`05 §2.1`、`05 §2.2`、`07 §9`、`08 §9`、`09 §6`、`09 §7`、`10 §3`、`10 §4`）与 `00` 篇三类误区第 3 条的因果表述**全部改写为四要素**（现象 / 根因 / 影响 / 建议），共 **9 条**；保留「非实证结论 / 方法前提假设 / 非承诺」口径；**无根因者 6 条**（`00`、`05 §2.1`、`05 §2.2`、`09 §6`、`09 §7`、`10 §3`）**显式标注**「根因：本包未给出，属待研究方法问题」，未编造；`09 §6` 因位于表格单元格以同行内四要素标签呈现。
  - **G3（A-6）**：`concepts/00-overview.md` 新增 **§六「可迁移模式：变现方向发现四步法」**，触发场景 / 核心步骤（链 `05~08`）/ 反模式（链 `05 §5`、`06 §10`、`07 §6`、`08 §5`、`10 §3`）/ 迁移验证（`09 §4` P1~P4 主干复用且无需改动 + 5 个同簇 bundle 互链，声明非实证检验）**4/4 齐备**。
  - **纪律复核**：事实层 `01~04` **零改动**、因果词命中仍 0；新增文本无 `facts.md` 之外的数字 / 年份 / 提出者（仅引用既有 F-003/006/011/012/031/033/034/035/045/049/052/056/065/066）；内容层因果词命中 **0**；新增相对链接 6 条全部可达、`file:///` 命中 0；未新增任何文件。
  - **AC-9 复评**：G1 ✔ / G2 9/9 ✔ / G3 4/4 ✔ / G4 ✔ → **5 分顶锚，≥4 阈值通过**（补救前未达阈值）。
  - **门禁（exit 0，全绿）**：`scripts/check-utf8.py` **通过**（11751 文件）、`scripts/check-toctrees.py` **通过**、`scripts/check-bundles-index.py` **通过**（9 域 / 62 组 / 644 束五面一致）。记录已同步至 `verification.md` §8.6、`log.md` 2026-10-17 Task 9 条目、`adversarial-review.md` 第六节。**未执行 git 提交**。
- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - **验证阶段发现**：AC-9 的顶锚（5 分）要求 G2「洞察四元组完整（现象+根因+影响+建议）」与 G3「模式含触发场景+核心步骤+反模式+迁移验证」；实测 concepts 05~10 的 `〔洞察〕` 为单句表述、未呈四元组，且无 G3 可迁移模式条目 → AC-9 未达阈值 ≥4，须修复后重验。
  - 在 concepts 05~10 将 `〔洞察〕` 改写为四元组结构（**现象 / 根因 / 影响 / 建议**）；确无根因者**显式说明缺失**，不得编造；
  - 在 `concepts/00-overview.md` 增补紧凑「可迁移模式：四步法」段（触发场景 / 核心步骤 / 反模式 / 迁移验证）；**迁移验证**以「四步法已适配四条起点路径（`09` §4 P1~P4）与 5 个同簇场景互链、主干无需改动」为证据；
  - 同步更新 `references/verification.md` §8 与 `log.md`（新日期条目），并重跑门禁。
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `rule` TR-9.1: 05~10 中每条 `〔洞察〕` 均以「现象 / 根因 / 影响 / 建议」四要素呈现（缺根因须显式说明）；证据为文档内容 + 复核检索输出。
  - `rule` TR-9.2: `00-overview.md` 含「可迁移模式」及其四要素（触发场景 / 核心步骤 / 反模式 / 迁移验证）；证据为文档内容。
  - `rule` TR-9.3: 重跑 `check-utf8.py` / `check-toctrees.py` / `check-bundles-index.py` 三脚本全绿；证据为脚本输出。
- **Notes**: 采用「既有页面增补」而非新增 concepts 篇——新增文件会级联牵动 concepts/index、bundle index、组索引文档数与三级计数，代价高于收益。

# Task Dependencies

- Task 2 depends on Task 1
- Task 3 depends on Task 2
- Task 4 depends on Task 3
- Task 5 depends on Task 4
- Task 6 depends on Task 5
- Task 7 depends on Task 6
- Task 8 depends on Task 7

> 全部为串行依赖（信源先行 → 事实 → 结构 → 内容 → 索引 → 审查 → 提交），无并行分支。
