# 腾讯会议 CLI 知识束 v0.4.0 全信源增量复核轮 - 实施计划

> 方法论：seven-concepts-cmd 场景 4（知识沉淀 R→I→E，V 强制，C 收口不提交）。
> 路径裁决：T3 产出 `VERDICT=zero-drift | drift`；T4a/T4b 互斥，仅执行命中的一条，另一条由用户批准取消（零漂移→取消 T4b；漂移→取消 T4a）。

## Task 1: R 阶段·版本面三证采集
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - npm：取 `@tencentcloud/tmeet` latest version 与 time 序列末次发布时间；
  - GitHub Commits API：默认分支 since `2026-09-11T10:00:00Z` 提交列表；
  - tag 锚点：取 refs/tags/v1.0.18 解析的 commit SHA，与基线 `e631b355da2b001d24b82f453b65d96f39c59865` 比对；
  - 全部记录 UTC 采集时间与原始响应摘要。
- **Acceptance Criteria Addressed**: AC-1、AC-2
- **Test Requirements**:
  - `rule` TR-1.1: 三项证据均有命令/URL、UTC 时间戳与实际响应值；证据可独立复跑。
  - `rule` TR-1.2: tag SHA 比对给出 `一致/不一致` 二元结论；不一致时列出新版本面事实候选。
- **Notes**: Specify 预侦察值（1.0.18 / `[]` / e631b355）仅作基线，实施当日必须重跑。

## Task 2: R 阶段·10 信源重采与逐源机械比对
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1（tag 不变则 tag 内文件只做锚点抽检；出现新 tag 则全文重抓比对）
- **Description**:
  - 产品首页、安装指南：全文抓取，与 product-page.md / install-guide.md 登记事实逐段比对；
  - README、docs/command.md、SKILL.md、CHANGELOG.md、package.json：raw tag URL 抓取，比对行数/关键节锚点（44 命令树、9 个二次确认命令、8 EventKey、1594 行、版本历史、Node>=14）；
  - 云文档 133827：抓正文与页面更新时间（基线 2026-07-08）；
  - QQ 用户手册：按 v0.2.0 已验证 dop-api/opendoc JSON 路径复现，取保存时间（基线 2026-06-25）与正文关键锚点；
  - 源码主体：tag SHA 一致即锚定（252/64 Go 文件、38 ApiCmd 等关键计数抽检命令登记但不必全量重数；若 SHA 变化才全量复核 F-113~F-199）；
  - 逐源产出 `零漂移/漂移（原文差异）/不可达（降级依据）` 结论与受影响 F 编号。
- **Acceptance Criteria Addressed**: AC-1、AC-2
- **Test Requirements**:
  - `rule` TR-2.1: 10 个信源每个有独立条目、采集时间与三类结论之一；不可达项必须给出失败原因与降级处置（维持原事实）。
  - `rule` TR-2.2: 所有"漂移"结论引用双方原文/锚点值；无锚点的主观印象不得记为漂移（G1 事实门：零因果推断词）。
  - `rule` TR-2.3: 两个用户面文档（云文档/QQ 手册）的页面时间锚点必须实际取得或明确记为不可达。

## Task 3: R 阶段·漂移矩阵落盘与路径裁决
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1、Task 2
- **Description**:
  - 在 spec 工作目录写 `drift-matrix.md`：版本面 3 行 + 信源 10 行（skill-manifest 一行内含 3 文件锚点），列：ID/URL/UTC 采集时间/方法/基线锚点/本次锚点/结论/受影响 F；
  - 输出机器可读裁决行 `VERDICT=zero-drift` 或 `VERDICT=drift（列触发源与影响面）`；
  - 若漂移仅限"页面元数据时间变化但正文零变化"，裁决为 zero-drift 并在矩阵中说明。
- **Acceptance Criteria Addressed**: AC-1、AC-2
- **Test Requirements**:
  - `rule` TR-3.1: 矩阵行数 ≥13 且每个结论可回溯到 Task 1/2 证据；VERDICT 与矩阵内容一致。
  - `rule` TR-3.2: 裁决规则在文档开头显式声明（何为零漂移/漂移/不可达）。

## Task 4a: E 阶段·零漂移最小留痕（仅 VERDICT=zero-drift 执行）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 束 `log.md` 追加「## 复核轮 2026-10-15（内容版本不变）」节：三证证据值表、逐源结论摘要、复现方法入口、V 审查记录占位；
  - tencent 分组 `index.md`「关于本分组」段补一句：2026-10-15 全信源复核、上游仍 v1.0.18、零漂移；
  - 不改 version、不增 F 编号、不动任何正文文件。
- **Acceptance Criteria Addressed**: AC-3、AC-5、AC-6
- **Test Requirements**:
  - `rule` TR-4a.1: `git diff --name-only` 恰好 2 个文件（log.md、tencent/index.md），spec 目录除外。
  - `rule` TR-4a.2: facts.md/insights.md/concepts/examples/references 零 diff；version 字段保持 0.3.0。
  - `rubric` TR-4a.3: 留痕可审计性；scale 1-5；anchors 1=空泛声称无证据，3=有结论但证据不全，5=值表+时间戳+复现路径齐全；threshold ≥4；证据为 log.md 新增节。

## Task 4b: E 阶段·v0.4.0 条件增补（仅 VERDICT=drift 执行）
- **Status**: `cancelled`
- **Cancellation Evidence**（spec 顶部互斥条款预批准，用户 Approve 阶段已批准）：T3 裁决 `VERDICT=zero-drift`，增补路径未触发；T5 V 审查（V-9）与 R1 均确认零漂移不 bump 语义正确。无 F-200、无 version bump、无正文改动。
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - facts.md 自 F-200 连续续号（三级证据标注 + 来源锚点）；更新受影响 references 文档（页面时间/新版本）；
  - 受影响 concepts/examples 定点修订，旧结论以「⚠️ 口径」并列；新版本 tag 则 source-code.md 增补并复核受影响源码事实；
  - 根 index.md / references/index.md / concepts 索引 / tencent/index.md 计数与描述连锁；log.md 追加 `## 0.4.0 — 2026-10-15`（含 V 审查表）；version bump 0.3.0→0.4.0；
  - 结构性认识确被改变才新增洞察（I 阶段，G2 四元组门），否则明确记录"无新洞察"。
- **Acceptance Criteria Addressed**: AC-3、AC-6
- **Test Requirements**:
  - `rule` TR-4b.1: F 编号自 F-200 连续无重号/断号；每条新事实可在新抓取内容中命中。
  - `rule` TR-4b.2: 旧事实零删除零覆盖；冲突全部以口径并列呈现。
  - `rule` TR-4b.3: 束根/子索引/分组索引的计数与目录树机械对账一致（束数不变，概念/信源/事实数按实际变更）。
  - `rubric` TR-4b.4: 增量文档质量；scale 1-5；anchors 1=新事实无锚点或改写旧结论，3=可消费但有冗余/口径混乱，5=锚点密集、口径表清晰、信息密度对齐 v0.3.0 水准；threshold ≥4；证据为新增/修订文件。

## Task 5: V 阶段·四视角对抗审查（fresh context）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 4a 或 Task 4b
- **Description**:
  - 按既有束 V 记录惯例，由未参与实施的 fresh context 执行四视角审查：
    魔鬼（双向漏判：漂移漏报/无漂移虚报）、新人（结论可读性与术语）、老板（版本语义与计数闭合）、未来（可复现性/stale 策略/链接）；
  - 审查结果记录进束 log.md 对应版本节（零漂移路径同样留 V 表）。
- **Acceptance Criteria Addressed**: AC-3、AC-6、AC-7
- **Test Requirements**:
  - `rule` TR-5.1: 四视角均有意见与处置记录；P0/P1 发现全部回修并复核零残留（Grep 旧错误措辞）。
  - `rule` TR-5.2: 审查者与实施者上下文隔离（独立子代理/独立轮次证据）。

## Task 6: C 阶段·质量门与文档构建
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 子模块目录运行 `invoke gates.all`（utf8/toctrees/bundles）；
  - 运行 `invoke build`（或 `sphinx-build -b dummy` 定向）确认 0 error；
  - 失败则回修至全绿，无关在途欠债按 NFR-6 过滤登记。
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-6.1: gates 三项退出码 0，输出无本束相关告警。
  - `rule` TR-6.2: 构建 0 error；若构建环境不可用记为 blocked 并附环境证据。

## Task 7: C 阶段·变更边界收口与证据回填
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - `git -C` 子模块 status/diff 核对：文件清单命中白名单（束目录内 + tencent/index.md），无 commit/push；
  - 回填本 tasks.md 各项 Completion Evidence（含 rubric 评分与理由）；
  - 输出建议提交文案（`docs(bundles): …`，中文）但不执行。
- **Acceptance Criteria Addressed**: AC-5、AC-6
- **Test Requirements**:
  - `rule` TR-7.1: 无白名单外文件；`git log` 无新增提交；主仓 gitlink 未变动。
  - `rule` TR-7.2: 所有 completed 任务带 Completion Evidence，rubric 有分值/理由/证据。

---

## Completion Evidence（2026-10-15 C 阶段收口回填）

### T1（TR-1.1/1.2 ✅）
- npm（北京 09:47:43）：`npm view @tencentcloud/tmeet version time --json` → latest=1.0.18；1.0.18=2026-09-11T09:17:53.445Z、modified=09:18:10.494Z；19 条版本时间无新版。
- GitHub Commits API `since=2026-09-11T10:00:00Z` → `[]`；tag v1.0.18 commit `e631b355da2b001d24b82f453b65d96f39c59865` 与基线逐字符一致（tag 内日期 2026-09-11T08:48:38Z）。
- V-2 第四证（R1 评审独立复跑确认）：`commits?per_page=1` 默认分支 HEAD sha 恰为 e631b355（main==tag 直证）；tags 列表恰 18 个无新 tag。

### T2（TR-2.1/2.2/2.3 ✅）
- 10 源逐源结论全部「零漂移」，无不可达项（raw.githubusercontent.com 连接重置 → jsDelivr `cdn.jsdelivr.net/gh/TencentCloud/tencentmeeting-cli@v1.0.18/<path>` + GitHub contents API 双替代，见矩阵通道备注）。
- tag 内 5 文件 SHA256（jsDelivr 钉 tag，完整 64 位见束 log.md 复核节哈希表）：README ac526a68…344d2（10523B/265 行）、command.md a82289be…e09d36（59259B/1594 行）、SKILL.md 63d331e9…27a9182（34265B/401 行）、CHANGELOG c7654ed1…4ce47ae（95634B/512 行）、package.json 7d641d46…2c34ca（438B/23 行，blob sha1 609470997aa1444424d082fda436fd3c42828e94 跨通道一致）；R1 评审独立重算 5/5 精确一致。
- 用户面时间锚点（TR-2.3 ✅）：云文档 133827 页面时间 2026-07-08 15:50:30 原样；QQ `lastModifyTime=1782374442912`=2026-06-25T08:00:42.912Z（北京 16:00:42）与基线分钟级登记一致，serverTimestamp=1792029377=2026-10-15T01:56:17Z 证明实时。
- 零推断词：全部锚点均为 grep/API/哈希机械值；V-5/V-6/V-7 口径勘误已入矩阵附记与 log。

### T3（TR-3.1/3.2 ✅）
- drift-matrix.md：裁决规则 3 条显式声明；版本面 3 行（V1-V3）+ 信源 10 行（S1-S10）=13；机器裁决行 `VERDICT=zero-drift`；附 V 阶段 7 条补强勘误与时区口径声明（R1 P2-1 修订）。

### T4a（TR-4a.1/4a.2 ✅，TR-4a.3 rubric=4/5）
- 落盘时点 `git diff --name-only` 恰 2 文件：`…/tencent-meeting-cli/log.md`、`…/tencent/index.md`（R1 评审开场快照独立证实）；facts/insights/concepts/examples/references 零 diff；束内 version 字段均为 "0.3.0"（index.md/log.md frontmatter）；facts.md 止于 F-199，F-200 命中 0。
- rubric TR-4a.3 **评分 4/5（≥4 通过，R1 评审打分）**：版本面四证表、5 个完整 64 位 SHA256+字节/行数表、blob sha、jsDelivr URL 模板、双时区标注、QQ 锚点计数表与方法指针（references/user-manual-qqdoc.md 三步法）、14 行四视角 V 表、R1 落盘评审记录；扣 1 分原因为初稿时区误标与毫秒精度两处（P2-1/P2-2），已在同节修订闭合。
- 环境事件（不改变本任务验收）：R1 评审窗口内并行工作流落盘新束 workbuddy-official-docs 并改动 7 个跟踪文件（含 tencent/index.md 计数段由并行方改写为 635 束口径）；我方复核句逐字幸存（Select-String HIT 验证）。提交时须 hunk 级选择性暂存（见 review.md P1-1）。

### T4b：cancelled（spec 互斥条款，用户已预批准；零漂移未触发）

### T5（TR-5.1/5.2 ✅）
- fresh-context 独立子代理（agent ID 56baf44a-…，实施前未接触本任务）四视角审查：V 结论 pass，P0=0、P1=2（V-1 完整物证内联 log、V-10 C 阶段机械验收）、P2=13（V-2~V-9、V-11~V-14）；14 条记录全部有处置并复核（矩阵附记+log V 表）。

### T6（TR-6.1/6.2 ✅）
- `invoke gates.all`（py314 / invoke 3.0.3）最终快照全绿：utf8 通过 11585 文件（含自检探针）；toctrees 通过「全部引用有效、所有内容文档可达」（含 5 项自检）；bundles 对账通过「9 域 / 61 组 / 635 束，五面一致」。说明：评审中途 18→30 处 toctree 告警全部归因于并行工作流未完成接线的外来束，其接线完成后复绿；我方两文件任何时点命中问题清单 0 次（stash 基线 18 处=带改动 18 处，零回归已机械证明）。
- 构建：`python -m sphinx -b dummy -q doc _build_dummy_audit`（Sphinx 9.1.0 + myst_parser，py314）exit 0；我方两路径告警 0、error 0（326 条既有告警全在无关束，Substitution error 等）。我方构建残留 `_build_dummy_audit/` 已删除；评审方 `_build_dummy_review/` 已自清理。

### T7（TR-7.1 ✅ / TR-7.2 本块）
- 子模块 `git log` HEAD 仍为 ee09f074（早于本轮），无 commit/push；主仓 `git diff --submodule=log` 仅 ` m`（modified content），gitlink SHA 未变动。
- 当前工作树跟踪改动 7 个：我方 2 个 + 并行工作流 5 个（doc/bundles 两级 index、ecosystems/index、workbuddy-one-sentence-mvp/index）；未跟踪项 2 个：并行束 workbuddy-official-docs/（非本轮）。我方产物边界仍为 2 文件，diff 内容无 file:///、无绝对路径（唯一 URL 形文本为 jsDelivr https 物证）。
- 建议提交文案（不执行；提交时需仅暂存我方 2 文件/对应 hunk）：
  `docs(bundles): tencent-meeting-cli 束追加 2026-10-15 全信源零漂移复核留痕（tencent，2 文件）`
