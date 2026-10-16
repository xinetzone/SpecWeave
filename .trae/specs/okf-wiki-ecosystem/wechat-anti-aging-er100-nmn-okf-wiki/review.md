# 微信公众号「美因」逆龄基因药博文转 OKF Wiki — Independent Review

> 覆盖范围：`spec.md` 的 AC-1 ~ AC-12 全部验收标准。
> 审查方式：每轮由**全新上下文**的独立审查者执行（实施者自验不作为最终验收证据）。审查契约含：用户目标、仓库根、`spec.md`/`tasks.md`/`review.md` 绝对路径、环境约束（`invocations` 未安装，改走手动等效验证 + 仓库自带三脚本）、实施产物路径与完成证据。

## Checkpoints

- [x] CP-R1: `facts.md` 与 `references/article-source.md` 的 F 编号集合相等且连续
  - **Type**: `rule`
  - **Covers**: AC-1 / TR-6.1 / TR-I-8.2
  - **Evidence**: R2 实测两侧各 89 条、集合相等、F-001~F-089 连续无跳号；R2-2 修复（补登 F-090）后两侧各 90 条、连续 F-001~F-090，F-075~F-090 逐字一致。

- [x] CP-R2: bundle 正文具体声明 100% 可回溯到 F 编号，观点与事实分层
  - **Type**: `rule`
  - **Covers**: AC-2 / TR-2.1 / TR-2.2 / TR-5.1
  - **Evidence**: R2 抽查 ≥15 项具体数字/日期/机构/文献引用均可回溯 F 编号，正文引用无越界；R2-3（登记表图例缺 `核验` 定义、导语把核验行并入「博文事实」）与 R2-4（正文悬空「勘误⑤」）经 Issue I-9 / I-10 修复。

- [x] CP-R3: 全部 P0 声明有独立权威来源或显式 `single-source/flagged`，零假核验
  - **Type**: `rule`
  - **Covers**: AC-3 / TR-3.1 / TR-3.2 / TR-3.3
  - **Evidence**: R2 实测核验表 41 行，✅15/⚠️16/❌2/single-source 6/single-source-flagged 2，状态字段无空缺；抽查 `lifebiosciences.com/pipeline/`（FDA 2026-01-15、NCT07290244）与 `pubmed/38979132`（NMN 雌鼠中位寿命 +8.5%）实取内容支持声明；`nature.com/d41586-026-01836-7` 遇 cookie 墙记为 inconclusive（不构成反证）。R1 的 F1「45 条权威 URL」虚高经 Issue I-1 修正为「40 条权威信源（全文唯一 URL 41 条含博文）」。

- [x] CP-R4: 核验发现的源文错误（含重复段落等编辑瑕疵）已单列勘误，正文呈现正确值
  - **Type**: `rule`
  - **Covers**: AC-4 / TR-3.2 / TR-I-2.2 / TR-I-8.1
  - **Evidence**: R1 判定「11/13 条勘误已在正文呈现正确值」（勘-07/勘-12 仅登记于 verification）→ I-4 补写勘-07 于正文；R2 判定 CP-R4 `fail`——勘-06 未登记为 F 编号行 → I-8 补登 F-090，修复后勘-01~勘-13 映射 13/13。

- [x] CP-R5: 文末私域带货（999 → 649 元/瓶）已完整披露，bundle 内零购买入口与推荐话术
  - **Type**: `rule`
  - **Covers**: AC-5 / TR-5.4 / TR-I-6.1
  - **Evidence**: R1/R2 两轮 Grep `专属价|领取|点击上方图片|立即购买|专属通道|扫码|加微信` 均 **0 命中**；根 index「内容边界」段与 `concepts/04` 均含带货事实披露与非推荐声明；两侧 F-058 文本已统一为中性转述。

- [x] CP-R6: 厂商自宣声明逐项标注「厂商自述」，index 含提示块
  - **Type**: `rule`
  - **Covers**: AC-6 / TR-5.3
  - **Evidence**: R1/R2 均判定通过——供应哈佛、国际期刊人体临床、纯度、全酶法量产等逐条标注「厂商自述/无独立出处」；根 index 顶部有 flagged + 厂商自述数据提示块。

- [x] CP-R7: bundle 根、concepts、references 三级 index 均含 `{toctree}` 且条目逐一可达
  - **Type**: `rule`
  - **Covers**: AC-7 / TR-5.2 / TR-7.2
  - **Evidence**: R1/R2 实测 root 4 条 + concepts 5 条 + references 2 条（已排除 `:` 指令行），11/11 `Test-Path` 命中；`check-toctrees.py` 实跑通过。

- [x] CP-R8: 三级计数同步一致
  - **Type**: `rule`
  - **Covers**: AC-8 / TR-7.1 / TR-7.3 / TR-I-7.1
  - **Evidence**: R2 实测 `bundles/index.md` 636/636、mermaid 68 束、域节标题 68 束；`personal-growth/index.md` `total_bundles` 15 = toctree 15 = 实际目录 15；R2-1（`sheke/index.md` 两处仍写「74 条」）经 I-7 修正为「89 条事实双份登记」；R3-A1（I-8 追加 F-090 后 8 处仍写 89 条 / F-001 ~ F-089）经 I-11 全域同步为「90 条 / F-001 ~ F-090 / 16 条核验更正与衍生值」，全域 Grep 断言本包口径残留 = 0。既有漂移项（Industry 行显示 22 vs 实际 25）不在本束范围，见 Review History R3 的 B3。

- [x] CP-R9: UTF-8 严格解码通过；绝对路径与家目录路径零命中
  - **Type**: `rule`
  - **Covers**: AC-9 / TR-6.2
  - **Evidence**: R1/R2 实测 strict-UTF8 失败 0；`file:///`、`C:\Users\`、`/Users/`、`](/ ` 命中均为 0；42 条相对内链 0 断链；`check-utf8.py` 实跑「11597 个文件均为有效 UTF-8」。

- [x] CP-R10: frontmatter 字段齐备且 `sources` 含博文 URL 与核验权威 URL 双信源
  - **Type**: `rule`
  - **Covers**: AC-10 / TR-5.3 / TR-I-5.1
  - **Evidence**: R2 实测 9 个目标文件字段齐备（`type`/`title`/`description`/`tags`/`generated`/`verified`/`status`/`stale_after`/`sources`），`okf_version` 仅出现在 bundle 根 `index.md`；R1 的 R2-5 类问题（子索引仅 `type`+`title`）经 I-5 补齐。

- [x] CP-U1: 读者可在不被误导前提下辨识「已知 / 厂商自述 / 未知」三类边界
  - **Type**: `rubric`
  - **Covers**: AC-11 / TR-1.3 / TR-5.5
  - **Scale**: 1-5
  - **Anchors**: 1 = 事实与话术混杂，读者会把带货文当抗衰指南；3 = 有边界声明但分层不彻底，个别未核验数字未标注来源距离；5 = 三层边界通篇可辨识，且含可迁移的保健品内容阅读纪律
  - **Pass Threshold**: >= 4
  - **Evidence**: R1 得分 **5/5**；R2 得分 **4/5**（扣分因 F 登记表把 15 条核验结论与博文事实混登、图例未定义「核验」，对机器可读边界造成轻微模糊）——该扣分项经 I-9 修复（补图例定义 + 导语显式区分 F-001~F-074 与 F-075+ 性质）。两轮均确认：普通读者读完不会把「8 周逆转 75%」当已证实人体疗效，也不会被引向购买。

- [x] CP-U2: OKF v0.2 结构合规且门禁结论可复现、如实记录
  - **Type**: `rubric`
  - **Covers**: AC-12 / TR-6.3 / TR-6.4
  - **Scale**: 1-5
  - **Anchors**: 1 = 结构缺失且未跑门禁也未做等效验证就声称通过；3 = 结构合规但手动门禁路径未在 `log.md` 注明；5 = 结构完全合规，gates 或手动等效验证均执行且结论如实记入 `log.md`
  - **Pass Threshold**: >= 4
  - **Evidence**: R1 得分 **4/5**（扣分因 `log.md` 手动清单仅 5 项、官方脚本未执行）→ I-3 补齐 8 项并实跑三脚本；R2 得分 **4/5**（三脚本由 R2 独立亲跑，输出与 `log.md` 记录**逐字一致**；扣分因 `review.md` Review History 仍为 Pending）→ 本文件已回填 R1/R2/R3 历史；R3 得分 **4/5**（扣分因 `log.md` 内仍存与事实总数不符的「各 89 条」记录）→ I-11 全域同步后已消除该扣分项。

> 覆盖核对：AC-1 → CP-R1；AC-2 → CP-R2；AC-3 → CP-R3；AC-4 → CP-R4；AC-5 → CP-R5；AC-6 → CP-R6；AC-7 → CP-R7；AC-8 → CP-R8；AC-9 → CP-R9；AC-10 → CP-R10；AC-11 → CP-U1；AC-12 → CP-U2。无遗漏 AC。

## Review History

### Review R1
- **Result**: `fail`
- **Checks Performed**: 双份 F 编号比对；strict UTF-8 解码；`check-utf8.py` / `check-toctrees.py` / `check-bundles-index.py` 实跑；三级 toctree 提取 + `Test-Path`；全 bundle 内链提取 + `Test-Path`；计数五面对账；frontmatter 键解析；带货话术 Grep；四视角内容审查（抽查 ≥15 项事实溯源、6 篇文献元数据、勘-01~勘-13 逐条落实）；`examples/` 残留检查。
- **Evidence**: 两侧 F 各 74 条、集合相等、F-001~F-074 连续；strict-UTF8 失败 0；toctree 11/11 可达；42 条内链 0 断链；`file:///` 等敏感路径 0；计数 636/68/15 一致；话术 0 命中。
- **Checkpoint Results**: CP-R1~CP-R10 全 `pass`；CP-U1 `pass`（5/5）；CP-U2 `pass`（4/5）。
- **Findings**:
  - `F1`: `actionable`；medium；「45 条权威 URL」计数虚高 5 条（实际信源清单 40 条 / 全文唯一 URL 41 条），出现于完成证据与交付正文 → 属数量陈述失真。**已固化为 Issue I-1**。
  - `F2`: `advisory`；medium；AC-4 要求的「新增 F 编号记录正确值」未落实（更正仅以 `勘-xx` 存在）。**→ Issue I-2**。
  - `F3`: `advisory`；medium；`log.md` 手动清单仅 5 项，官方脚本未执行。**→ Issue I-3**。
  - `F4`: `advisory`；low；勘-07 / 勘-12 未进入正文。**→ Issue I-4（勘-07 部分）**。
  - `F5`: `advisory`；low；子索引 frontmatter 仅 `type`+`title`。**→ Issue I-5**。
  - `F6`: `advisory`；low；Oct4/Sox2/Klf4、GS010 €425,000 等核验衍生值未登 F。**→ Issue I-2**。
  - `F7`: `advisory`；low；`sheke/index.md` Industry 行束数既有漂移（非本次引入）。**记录为既有问题、不在范围**。
  - `F8`: `advisory`；low；两侧 F-058 文本不一致。**→ Issue I-6**。
- **Recommended Issues**: I-1 ~ I-6（均已在 tasks.md 固化为 pending 并完成）。

### Review R2
- **Result**: `fail`
- **Checks Performed**: 从头复核全部机械门禁（未采信 R1 结论）；F-075~F-089 逐行两侧比对；I-1 权威 URL 计数复核；勘误↔F 编号映射；抽查 F-075/077/078/079/080/083 权威值 vs 勘误表；连带计数全域 Grep；**三脚本亲跑并与 `log.md` 记录比对**；I-4/I-5/I-6 逐项复核；正文 F 引用有效性；「勘误①~⑤」引用核查；两条权威 URL 实取内容抽查。
- **Evidence**: 两侧 F 各 89、集合相等、连续、F-075~F-089 逐行 0 不一致；`verification.md` `^\| src-` 40 行 / 唯一 id 40 / 全文唯一 URL 41；三脚本实跑输出与 `log.md` **逐字一致**；toctree 11/11；42 条内链 0 断链；`okf_version` 仅根 index；话术 0 命中；`examples/` 不存在。
- **Checkpoint Results**: CP-R1/R3/R5/R6/R7/R9/R10 `pass`；**CP-R2 `fail`**（映射 R2-3/R2-4）、**CP-R4 `fail`**（映射 R2-2）、**CP-R8 `fail`**（映射 R2-1）；CP-U1 `pass`（4/5）；CP-U2 `pass`（4/5）。
- **Findings**:
  - `R2-1`: `actionable`; **high**；`sheke/index.md:18/32` 仍写「74 条事实双份登记」，与 89 条口径冲突。**→ Issue I-7**。
  - `R2-2`: `actionable`; medium；勘-06 未登记为任何新 F 编号行，TR-I-2.2「13/13 映射」不成立。**→ Issue I-8**。
  - `R2-3`: `actionable`; medium；`article-source.md` 来源图例缺 `核验` 定义、标题/导语把 15 条核验结论并入「博文事实」，构成分类污染风险。**→ Issue I-9**。
  - `R2-4`: `actionable`; low；正文出现不存在的「勘误⑤」悬空引用。**→ Issue I-10**。
  - `R2-5` ~ `R2-9`: `advisory`；其中 R2-5/R2-6 已随本轮修复处理，R2-7/R2-8 由主控修文档，R2-9 为**既有问题复述**（Industry 行 22 vs 实际 25，致域内分组行显示之和 65 ≠ 域节标题 68；非本次引入）。
- **Recommended Issues**: I-7 ~ I-10。

### Review R3
- **Result**: `fail`
- **Checks Performed**: 从头复核全部机械门禁（未采信 R1/R2 结论）；F 编号双份提取 + F-075~F-090 逐行比对；勘误↔F 映射；strict UTF-8 解码 + `check-utf8.py`；三级 toctree + `check-toctrees.py`；全 bundle 内链 `Test-Path` + 绝对路径 Grep；计数手工对账 + `check-bundles-index.py`；过时计数全域 Grep（bundle 12 + spec 4 + 两级上级索引）；frontmatter 键解析；带货话术与 `examples/` 检查；勘-01~勘-13 逐条正文落实核对；抽查 ≥18 处事实溯源；悬空勘误编号 Grep；登记表分类污染复核；三脚本亲跑并与 `log.md` 记录逐字比对；P0 行数与核验表集合比对。
- **Evidence**: 两侧 F 各 90、集合相等、连续 F-001~F-090、F-075~F-090 逐字 0 差异；勘误编号两侧各 13 个、13/13 映射；strict-UTF8 失败 0、`check-utf8.py` 通过（11597 文件）；toctree 11/11、`check-toctrees.py` 通过；44 条内链 0 断链；`]\(/`、`file:///`、`C:\Users\`、`/Users/` 均 0；话术 0、`examples/` 不存在；三脚本输出与 `log.md:15-17` **逐字一致**；P0 声明 41 行 = 核验表 41 行。
- **Checkpoint Results**: CP-R1~CP-R7、CP-R9、CP-R10 全 `pass`；**CP-R8 `fail`**（映射 A1）；CP-U1 `pass`（**5/5**）；CP-U2 `pass`（4/5，扣分因 `log.md` 内仍存与当前事实总数不符的「各 89 条」记录）。
- **Findings**:
  - `A1`: `actionable`; **high**；Issue I-8 追加 F-090 后，下游 **8 处**仍写 89 条 / F-001 ~ F-089 / 15 条（bundle `index.md`、`knowledge-map.md`、`references/index.md`、`references/verification.md`、`log.md`、`sheke/index.md` 两处、`personal-growth/index.md`），与两侧登记表已 90 条的事实冲突 → **属 R1-F1 / R2-R2-1 同类「数量陈述失真」的第三次复发**。**→ Issue I-11**。
  - `B1`: `advisory`; low；`concepts/index.md`、`references/index.md` frontmatter 缺 `verified` 键。**→ Issue I-12**。
  - `B2`: `advisory`; low；`sheke/index.md:32` 存在游离 `| 15 |` 单元格，破坏两列结构（既有格式瑕疵）。**记录，不重构**。
  - `B3`: `advisory`; low；`sheke/index.md:33` Industry 行显示 22 束 vs 实际 25 束的既有漂移（致该文件分组行显示之和 65 ≠ 域节标题 68）。**既有问题复述，不在本次范围**。
- **Recommended Issues**: I-11（high）、I-12（low）。
- **修复与根因洞察**：I-11/I-12 已完成；三次同类复发的根因是「上游数字变更后未做全域重扫」，本轮修复以**全域 Grep 断言**收尾（断言本包口径残留 = 0，并识别 `personal-growth/index.md` 中另有 2 处「89 条」属 how-to-live-better 另一束、不属本包口径）。

### Review R4
- **Result**: `fail`
- **Checks Performed**: 从头复核全部机械门禁；计数一致性专项（全域过时计数断言逐条判定归属、正向 8 处断言、束数手工复算 + `check-bundles-index.py`）；F 编号双份提取 + F-075~F-090 逐行比对；勘误↔F 映射；strict UTF-8 + `check-utf8.py`；三级 toctree + `check-toctrees.py`；全 bundle 内链提取 + `Test-Path` + 绝对路径 Grep；frontmatter 键解析与 `okf_version` 范围；话术与 `examples/`；勘-01~勘-13 正文落实逐条核对；抽查 ≥18 处事实溯源；悬空勘误编号 Grep；登记表图例/导语与 F-075+ 权威值抽查；三脚本亲跑并与 `log.md` 逐字比对；读者可用性通读评分；自主发现（F-087 标签、`log.md` 内链计数、衍生值登记、四元组要素、flagged 一致性、跨文数字一致性）。
- **Evidence**: 两侧 F 各 90、集合相等、连续 F-001~F-090、F-075~F-090 逐字 0 差异；勘误映射 13/13；strict-UTF8 失败 0、`check-utf8.py` 通过；toctree 11/11、`check-toctrees.py` 通过；44 条内链 0 断链；`]\(/`、`file:///`、`C:\Users\`、`/Users/` 均 0；frontmatter 11 文件缺失 0、`okf_version` 仅根 index；话术 0、`examples/` 不存在；束数复算 sheke 68 / ALL 636·61·9 与 checker 一致；三脚本输出与 `log.md` **逐字一致**。
- **Checkpoint Results**: CP-R1、CP-R3~CP-R10 全 `pass`；**CP-R2 `fail`**（映射 A1、A3）；CP-U1 `pass`（**5/5**）；CP-U2 `pass`（4/5，扣分因 `log.md` 手动清单内链计数与实测不符）。
- **Findings**:
  - `A1`: `actionable`; **low**；F-087 文本头错标「勘-01」（应为勘误清单② / 关联 F-021），与同行状态列、正文 `concepts/03` 三处自相矛盾。**→ Issue I-13**。
  - `A2`: `actionable`; **low**；`log.md:22` 记内链「共 42 条」，实测 44 条（R2-5 新增 2 条未同步）——**同类「数量陈述失真」第四次出现**，载体为内链计数。**→ Issue I-14**。
  - `A3`: `advisory`; medium；正文多处核验衍生值（2026-01-15、2026-10-08、3 名 OAG/Day 56、共识发布细节、第三方 1500 元）已溯源但未登记 F 编号，与 `concepts/00` 前言「全部具体声明附 F 编号」自相矛盾。**→ Issue I-15**。
  - `B1`~`B5`: `advisory`；B1（子索引 `sources` 缺权威 URL）、B2（组级 description 未收录本束）、B5（`concepts/01:42` 弱引用勘误③）**随本轮修复处理**；B3（游离单元格）、B4（Industry 行既有漂移）**既有问题、不在范围**。
- **Recommended Issues**: I-13、I-14、I-15。
- **收敛趋势（供 Review R5 参考）**：可行动发现数 1 → 4 → 1 → 2，**最高严重度 medium → high → high → low**。发现已从「事实/可信度缺陷」退化为「登记与记录的局部口径不一致」，未见新的内容级缺陷。

### Review R5
- **Result**: `pass`
- **Checks Performed**: 计数一致性专项（全域过时断言逐条判定归属、正向断言、`log.md` 内链计数与实际提取消点比对、束数用同口径脚本独立复算 + `check-bundles-index.py`）；双份 F 编号双侧提取 + **F-001~F-096 全 96 行逐行 diff**；勘误↔F 映射 + F-087 归属复核；strict UTF-8 + `check-utf8.py`；三级 toctree + `check-toctrees.py`；45 条内链逐条 `Test-Path` + 绝对路径 Grep；frontmatter 键解析 / `okf_version` 范围 / 全部文档双信源；话术与 `examples/`；勘-01~勘-13 正文落实逐条核对；抽查 ≥18 处事实溯源（含新增 F-091~F-096 的日期与细节值）；悬空勘误编号 Grep；登记表图例与导语复核；核验表/信源清单计数核对；通读 5 concepts + knowledge-map + 根 index 评分；四元组要素核验；flagged 与 `status` 一致性；三脚本亲跑并与 `log.md` 逐字比对。
- **Evidence**: 双侧 F 各 **96**、`Compare-Object` diff **0**、连续 F-001~F-096 无缺口、**全 96 行逐行 diff = 0**；F-075~F-096 双侧各 22 行 diff 0；勘误集合双侧 01..13、对照 `verification.md` 13 行 **13/13 覆盖**，F-087 行已不含「勘-01」；strict-UTF8 14 文件失败 **0**；toctree 4+5+2 = **11** 条全命中；内链 **45 条 / 0 断链**，`]\(/`、`file:///`、`C:\Users\`、`/Users/` 均 **0**；frontmatter 11 文件缺失 **0**，`okf_version` 仅根 index，全部文档含 blog + 权威 URL 双信源；话术 **0**、`examples/` 不存在；束数独立复算 `sheke=68`、`personal-growth=15`、`domains 9 / groups 61 / total 636` 与 checker 一致；核验表 41 行、`^| src-` 40 行、唯一 URL 41（含博文）自洽；本包口径过时计数残留 **0**；三脚本输出与 `log.md` **逐字一致**。
- **Checkpoint Results**: **CP-R1 ~ CP-R10 全 `pass`**；**CP-U1 `pass`（5/5）**；**CP-U2 `pass`（5/5）**。
- **Findings**:
  - `R5-1`: `advisory`; low；`bundles/index.md` 的 sheke 个人成长行说明文字未提及本束（束数列 15 已正确同步，不影响 AC-8 计数）。
  - `R5-2`: `advisory`; low；`knowledge-map.md` 事实层表中 F-005 同时出现在「已核验」与「需限定」两行，分类标注略有歧义（`verification.md` 记 F-005 为 ⚠️）。
  - `R5-3`: `advisory`; low；`concepts/00` 的「AAV2-OSK」与 `concepts/02` 的「NCT07290244」仅借 F-001 / F-044 承载，未独立登记 F 编号（属 R4-A3 同类别未完全穷尽，影响极低）。
  - 既有问题复述（非可行动）：`sheke/index.md` 的 Industry 行锁数漂移与游离单元格——既有瑕疵、本次未触碰，仅记录。
- **Recommended Issues**: **无**（无 `actionable` 发现；3 条 advisory 不阻塞验收）。

## 完成判定

- 全部任务与修复项 ∈ {completed}：T1~T7 完成，I-1 ~ I-15 全部完成，无 pending / in_progress / blocked。
- 全部必需审查检查点已勾选：CP-R1 ~ CP-R10、CP-U1、CP-U2 共 12 项全部 `[x]`。
- 每条 `rule` 有通过的独立证据；每条 `rubric` 达阈值并有理由与证据（CP-U1 5/5 ≥ 4；CP-U2 5/5 ≥ 4）。
- 最新 Review 结果 == `pass`（Review R5）。
- 无遗留可行动发现（R5 Findings 仅 3 条 `advisory`）。
- 剩余任务：T8（C 阶段双层原子提交）。
