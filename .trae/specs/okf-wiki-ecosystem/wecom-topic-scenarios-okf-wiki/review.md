# 企业微信「话题」场景最佳示例页 → OKF Wiki 知识包 - Independent Review

> 评审性质：**fresh-context 独立对抗复核（只读）**。评审者未参与本任务实施，未修改除本文件外的任何文件。
> 取证限定：源页 `page.weixin.qq.com` 对未登录访客为登录墙，**本轮不重新联网抓取**；逐字比对基准为任务下发的「源页真实内容」逐字快照（5 分页正文 + 导航 + 页脚），该快照即为本轮 AC-5/AC-6 的可复核证据路径。凡该快照未含之页面元素，本报告一律记为「不可从下发证据复核」而不臆断其真伪。

- [x] CP-R1: bundle 结构、toctree、frontmatter 必填字段逐项机械核对通过（11 文件、无 `examples/`）
  - **Type**: `rule`
  - **Covers**: AC-1, FR-1, NFR-1
  - **Evidence**: `Get-ChildItem -Recurse` 清点 = 11 个 `.md`（根 `index.md`、`log.md`；`concepts/index.md` + `00/01/02/03/04` 共 5 篇；`references/index.md` + `article-source.md` + `verification.md`），无 `examples/` 目录、无任何非 `.md` 文件。根 index toctree 条目 `concepts/index`/`references/index`/`log` 逐一到文件存在；`concepts/index.md` toctree 5 条与 5 篇文件名逐一对应；`references/index.md` toctree 2 条存在。根 index frontmatter 含 `okf_version: "0.2"`、`type: bundle`、`title`、`description`、`tags`、`generated`、`verified`、`status: stable`、`stale_after: "2027-01-31"`、`sources`（W + W-P2…W-P5 共 5 条 URL）。`sources` 覆盖全部 URL 型来源代号（W-P1 与 W 同 URL，已在 `article-source.md` 来源代号表显式标注为同一 URL、不单列）。

- [x] CP-R2: `facts.md` 与 `references/article-source.md` 的 F 编号集合严格相等、连续无跳号、表行数等于最大编号；四条口径分层在 `verification.md` 与 concepts 正文均有呈现
  - **Type**: `rule`
  - **Covers**: AC-2, TR-1.1, TR-4.1
  - **Evidence**: 自写正则 `F-\d{3}` 独立提取：`facts uniq = 47`、`article uniq = 47`、`集合相等 = True`、`仅 facts 有/仅 article 有 均为空`、`min F-001 / max F-047`、`连续无跳号 = True`；行级 `^\|\s*F-\d{3}\s*\|` 计数 `facts 表行数 = 47`、`article 表行数 = 47`（= 最大编号）。四条口径分层落地：①源单源属性（`verification.md` 口径分层表 + concepts `仅官方单源`/`F-040`）；②话题 vs 频道命名张力（`verification.md` 口径分层表第 2 行 + `00-overview`「功能名的口径」、`01/03/04`「边界提示」）；③适用对象描述性非规范性（口径分层表第 3 行 + `00`「五组适用对象均为厂商描述性口径」及 `01/02/03` 场景页各有 ⚠️ 标注）；④官方未给项（口径分层表第 4 行 + `00`「官方未给项清单」表 + `01/02/03/04` 边界提示）。4/4 在 `verification.md` 与 concepts 正文均有呈现。

- [ ] CP-R3: 三级索引与计数机械同步（门禁退出码、五面一致、三处到位、本束过滤零命中）
  - **Type**: `rule`
  - **Covers**: AC-3, TR-5.1, TR-5.2, TR-5.3
  - **Evidence**: 门禁本身通过（见下），**但独立检视发现 `jishu/ai/index.md` 被本次改动引入了表行缺陷（见 Findings F-1）**，故本检查点判 fail。
    - `python scripts\check-bundles-index.py` → `bundles 总索引对账通过: 9 域 / 61 组 / 641 束，frontmatter、计数行、节标题、分组表、toctree 五面一致。 EXIT=0`。
    - `python scripts\check-toctrees.py` → `toctree 检查通过: 全部 index.md 引用有效，所有内容文档均可达。 EXIT=0`（本束 `wecom-topic-scenarios` 零命中，无污染）。
    - 本束三处到位：`tencent/index.md` 导航表 L31、相关链接 L59、toctree L84；`ecosystems/index.md` 腾讯行 18；`jishu/ai/index.md` 246 束/ecosystems 行 94；`doc/bundles/index.md` `total_bundles: 641`、计数行 641、mermaid jishu 475、节标题「475 束 · 18 组」、jishu 表 ai 行 246。
    - 计数独立复算（复刻 `check-bundles-index.py` 的 `_count_bundles` 口径）自洽：total **641**、jishu **475**、ai **246**、ecosystems **94**、tencent 束 **18**；tencent 概念 **140**、示例 **48**、信源（references 非 index `.md`）**68**、事实 **2879**（逐束取 references/∪spec/facts.md 内最大 F 编号求和）——与 `tencent/index.md`「18 个知识包、140 概念、48 示例、68 信源、2879 条事实」逐项一致。

- [x] CP-R4: 链接 / 编码 / 溯源 / 双向互链机械门禁通过，5.0.12 回补仅 1 行
  - **Type**: `rule`
  - **Covers**: AC-4, TR-6.1, TR-6.2, FR-6
  - **Evidence**: `python .agents\skills\submodule-atomization-finalize-cmd\scripts\check_doc_links.py <bundle>` → `checked_files=11 links=58 broken=0 EXIT=0`；`python scripts\check-utf8.py` → `UTF-8 检查通过: 11688 个文件均为有效 UTF-8。 EXIT=0`。禁用串扫描（bundle）`file://`/`C:\Users`/`.temp` 全部 No matches；会话元数据关键词（xsrf/tinyid/corp_id/access_token/corpid/ticket）大小写不敏感扫描 No matches。派生产物 8 个含 frontmatter 的 Concept/Reference/根文件均带 `sources`（W / W-P2…W-P5）。双向互链：本束根 index「主题关联」L51→5.0.12、L52→5.0.10 各 1 条；`wecom-5-0-12-release/index.md` 回补 1 行（L59）。`git diff --stat` 该文件 = `1 file changed, 1 insertion(+)`，unified diff 仅新增 L59 一条链接行，5.0.10 束未改动。本束目录在子模块中为未跟踪新目录（`?? .../wecom-topic-scenarios/`）。
    - 附注（见 Findings F-6）：`spec.md`/`tasks.md` 作为规则正文含 `file:///`、`.temp/`、`C:\Users`、`xsrf`/`tinyid`/`corp_id` **字面串**（政策描述），若把「新增/修改的 .md」机械扩到 spec 目录会假命中；知识交付物（bundle + `facts.md`）零命中。

- [x] CP-R5: 隐私红线零泄漏、`.temp` 取证产物已清理且零引用
  - **Type**: `rule`
  - **Covers**: AC-7, TR-1.2, TR-4.3, NFR-5
  - **Evidence**: bundle 与 `facts.md` 会话/账号元数据关键词扫描命中数 = 0（无登录态票据、企业名、用户标识、内部文档 ID）。`.temp/smartpage` 不存在；`raw.html`/`probe.txt`/`psd_pages.json`/`all_sections.txt` 全仓检索 = 0 命中；bundle 内 `.temp` 引用 = 0（仓根 `.temp/` 存在的均为**其他并行会话**产物，与本任务无关）。逐字回源抽查 ≥8 条全部在快照命中（见 CP-U2）。附注：`spec.md`/`tasks.md` 因描述本规则含字面串，属政策文本非实际元数据（Findings F-6，advisory）。

- [x] CP-U1: 口径分层与读者决策可用性（AC-5 rubric）
  - **Type**: `rubric`
  - **Covers**: AC-5, TR-3.3
  - **Scale**: 1-5
  - **Anchors**: 1 = 厂商自述、未给项与可核实事实混写，读者无法判断可信度；3 = 主要声明有出处但口径分层不统一、个别场景条目无 F 编号；5 = 每条场景名/适用对象/优势条目可回溯 F 编号，「厂商自述单源 / 官方未给 / 命名张力 / 信源需登录」四类标签全文一致，「已知边界」可直接支持读者「用不用、怎么用、还缺什么」的决策
  - **Pass Threshold**: >= 4
  - **Evidence**: 得分 **4 / 5**。五篇 concepts 的场景名/适用对象/优势条目均带 F 编号（抽查零漏挂）；四类标签全文一致；根 index「已知边界」8 条（单源 / 无版本日期 / 信源需登录 / 话题vs频道 / 同形 smartpage 关系 / 官方未给项 / 描述性口径 / 零量化）可直接支撑「用不用、怎么用、缺什么」决策。扣分：`04` 篇对「分享话题帖」的跨篇指认有误（Findings F-2），削弱了「篇间一致」的满分档。

- [x] CP-U2: 三层结构与来源忠实度（AC-6 rubric）
  - **Type**: `rubric`
  - **Covers**: AC-6, TR-3.3
  - **Scale**: 1-5
  - **Anchors**: 1 = 按源页顺序平铺翻译、无分层与互链、夹带页面外推断；3 = 有分层但层间重复、跨篇跳转不清、个别断言超出源页可支撑范围；5 = 总览答「这是什么页 / 5 场景怎么分 / 信源与时效」，场景篇答「谁适用 / 优势是什么 / 厂商对照论证是什么」，边界篇答「官方没说什么 / 读者还需自行确认什么」，篇间阅读路径明确、Mermaid 节点有 F 依据、无一条断言超出源页可支撑范围
  - **Pass Threshold**: >= 4
  - **Evidence**: 得分 **4 / 5**。三层职责清晰：总览（源页定位 / 5 场景全景 / 8 组对照一览 / 信源时效 / 官方未给项）、场景机制篇（适用对象 + 优势条目 + 群聊vs话题对照）、边界提示（`00` 阅读路径 + 各篇「边界提示」+「阅读路径」互链）。Mermaid 1 张 `flowchart TD`，全部 13 个节点挂 F 编号（F-001/F-004/F-009–F-012/F-013–F-020/F-021–F-025/F-026–F-032/F-033–F-036/F-010/F-014/F-017–F-019/F-022/F-027/F-032/F-034–F-036），均落在 F-001～F-047 内。逐字回源抽查（≥8 条，全部命中下发扬文快照）：①场景名 5 项与导航顺序（F-004）；②`推进项目协作` 适用对象「项目管理、产品经理、销售、商务等」（F-009）；③`收集产品意见` 适用对象「产品经理、运营、客服、行政等」（F-013）；④`分享经验知识` 适用对象「任何乐于分享知识、向往团队学习交流的人」（F-021）；⑤`发布公告通知` 适用对象「行政、人事、秘书、项目/团队负责人」（F-026）；⑥P1 优势1 机器人汇总「进展与结论…不用逐条翻帖、或逐个找同事确认 +（点击查看API接口文档）」（F-010）；⑦P1 优势2 对照「群聊：多项工作的消息互相穿插，容易串线 ／ ✅话题：一项工作一个帖子，一目了然」（F-011）；⑧P2 优势3 三子项「贴表情 / 轻提醒（发帖仅红点提示…回复只通知楼主）/ 长期收集（成员可以随时在话题中发帖）」（F-017–F-019）；⑨P4 优势6「已读未读…阅读回执/阅读状态」（F-032）；⑩页脚「关于话题功能 你有什么想反馈吗？我想反馈」（F-005）。8 组对照计数（P1×1 / P2×3 / P4×4，P3/P5 无）与快照一致（F-037）。扣分：`F-003`「使用场景：」与 `F-006`「更多场景」交叉链接区在下发快照中无对应文字（Findings F-3），`04` 跨篇指认有误（F-2）。

## Review History

### Review R1
- **Result**: `fail`
- **Reviewer**: fresh-context 独立对抗评审子代理（未参与 Task 1–6 实施；只读；仅写入本 `review.md`）
- **Evidence**:
  - 门禁重跑（真实路径）：`check-bundles-index.py` EXIT=0（9 域/61 组/641 束五面一致）、`check-toctrees.py` EXIT=0、`check_doc_links.py <bundle>` `checked_files=11 links=58 broken=0` EXIT=0、`check-utf8.py` 通过。
  - 独立复算：F 编号双份集合 47/47 相等且连续、表行 47；tencent 束/概念/示例/信源/事实 = 18/140/48/68/2879，与 `tencent/index.md` 声明逐项一致；上层 641/475/246/94 亦复算一致。
  - `git diff --stat` 与 unified diff 确认 `wecom-5-0-12-release/index.md` 仅 +1 行；`jishu/ai/index.md` diff 除两处计数并改外，**ecosystems 行由 4 格降为 3 格**（丢「成员目录」=16）——P1 缺陷。
  - 隐私/禁用串扫描与 `.temp` 清理核实通过；逐字回源抽查 ≥8 条命中和。
  - 取证限定：源页登录墙不可重新联网抓取，逐字比对以任务下发快照为准；`F-003`/`F-006` 不在该快照内，记为不可复核（F-3）。
- **Blocked By**: 不适用（本轮无受阻检查点；源页不可重取的取证缺口已由下发逐字正文替代，故不判 blocked）

### 分级发现清单（Findings）

- **F-1 · 严重级别 P1 · 可行动**
  - 现象：`projects/awesome-okf-xs/doc/bundles/jishu/ai/index.md` 第 17 行 ecosystems 行丢失「成员目录」列值（原 `| … | 93 | 16 | … |` → 现 `| … | 94 | 以厂商…并存。 |`），该行由 4 格降为 3 格，而表头 L15 为 4 列（分类/束数/成员目录/一句话简介），同行其余 5 行均为 4 格。
  - 复现方式：`git -C projects/awesome-okf-xs diff -- doc/bundles/jishu/ai/index.md`；或读取该文件 L15–L22 观察 L17 仅 3 个单元格。
  - 期望结果：恢复第 3 格为 `16`，即 `| [🏢 厂商与开源社区生态](ecosystems/index.md) | 94 | 16 | 以厂商… |`。
  - 备注：`check-bundles-index.py` 不校验该子表单元格数量，故门禁未拦截（盲区）；该文件属 AC-3 Given 清单内文件，缺陷由本次改动引入。

- **F-2 · 严重级别 P2 · 可行动**
  - 现象：`concepts/04-general-capabilities-and-feedback.md` L32 称「**分享话题帖**（F-036）…与在[收集产品意见](02-feedback-collection.md)中出现的「分享话题帖」能力为同一能力」；但 `02-feedback-collection.md` 全文未出现「分享话题帖」（该能力登记于 P5/F-036）。
  - 复现方式：`rg 分享话题帖 projects/.../wecom-topic-scenarios` —— 仅 `04`、`index.md`、`article-source.md`（F-036）命中，`02` 零命中。
  - 期望结果：删除或改正该跨篇指认（如改为指向同页 F-036 的「链接/二维码传播方式」自述，或删去「在收集产品意见中出现」这一归属）。

- **F-3 · 严重级别 P2 · 可行动**
  - 现象：`F-003`「页面顶部标注『使用场景：』」与 `F-006`「每页底部『更多场景』交叉链接区」在任务下发的逐字快照中无对应文字（快照每页仅见「适用对象：…」前缀；正文与页脚均无「使用场景：」「更多场景」字样）。两事实在 `article-source.md` 均标 `✅ 页面本体`。
  - 复现方式：在下发「源页真实内容」逐字正文中检索「使用场景」「更多场景」= 0 命中；对照 `article-source.md` L52/L55。
  - 期望结果：在本轮证据路径下无法复核 → 或补记其取证出处（渲染态截图/节点路径），或降级为「未取得/不可复核」并同步 `00-overview` L24–L25、`04` L32 中对 F-006 的引用，避免以未复核事实支撑断言。（若实施方确认渲染页确有该 UI 元素，请在 `verification.md` 补一条可复核说明。）

- **F-4 · 严重级别 P2 · advisory**
  - 现象：`tasks.md` TR-6.2 证据称「8 个带 frontmatter 的派生产物均含 `sources:`…`concepts/index.md`、`references/index.md`、`log.md` 与基准束同构无 frontmatter」。实际 `log.md` **有** frontmatter（`type: Changelog` + `title`）但不含 `sources`；带 frontmatter 的派生产物实为 9 个（其中 8 个含 `sources`）。基准束 `wecom-5-0-12-release/log.md` 则**无** frontmatter。
  - 复现方式：对比两束 `log.md` 头部 3 行；`git` 侧读基准束原文。
  - 期望结果：更正证据措辞（「log.md 带最小 frontmatter、不含 sources，与基准束不同构」），或统一两束 log 形态；不影响知识交付物的正确性。

- **F-5 · 严重级别 P2 · advisory（既有漂移，非本次引入）**
  - 现象：`tencent/index.md` 导航表各行声明「信源」数之和 = 67（`tencent-buddy-family` 行未声明），而「关于本分组」信源登记 = 68（机械真值 references 非 index `.md` 计数）；差额来自既有行级漂移——`workbuddy-open-platform-docs` 行声明「4 信源登记文档」但目录实际 3 个。**信源 76→68 的本次改动本身成立**：76 无法用任何口径复现，68 = 新束机械真值（既有束真值 66 + 本束 2）。
  - 复现方式：逐行统计 `tencent/index.md` 导航表声明的信源数；`Get-ChildItem references` 逐束核对实际非 index `.md`。
  - 期望结果：如需行级自洽，修正 `workbuddy-open-platform-docs` 行（4→3）或为 `tencent-buddy-family` 行补计数；本次未引入新不自洽，仅使既有漂移与该口径并存。

- **F-6 · 严重级别 P2 · advisory**
  - 现象：AC-4/AC-7 若把「新增/修改的 `.md`」机械扩到 spec 目录，`spec.md` L50/L53/L97(/L121) 与 `tasks.md` L27/L79/L89/L119–L130 含 `file:///`、`.temp/`、`C:\Users`、`xsrf`/`tinyid`/`corp_id` **字面串**（规则/扫描策略描述文本）。知识交付物（bundle + `facts.md`）为零命中。
  - 复现方式：`rg 'file://|C:\\Users|\.temp|xsrf|tinyid|corp_id' .trae/specs/okf-wiki-ecosystem/wecom-topic-scenarios-okf-wiki` —— 13 行命中（均在 spec/tasks 的规则行）。
  - 期望结果：判定为**政策自述文本、非元数据泄漏/非实际路径引用**（与 `verification.md` 已改写的自述行同类）；建议在 AC-4/AC-7 证据中显式声明扫描口径为「bundle + facts.md」，避免范围歧义。

### 四视角对抗结论

- **魔鬼代言人**：最可能被质疑处有两类。①「厂商自述被当事实」——本束已系统对冲：全篇以「页面原文声称」措辞、`F-040` 单源、`已知边界` 集中声明零量化、`verification.md` 明确「不升级为产品事实」，未发现把厂商话术写成产品事实的语句（8 组对照亦标为「厂商自证定性论证」）。②「计数改动引入不自洽」——**核心暴露点即 F-1**：本次索引改写把 `jishu/ai/index.md` 的一行改成残格，属改索引时引入的新缺陷；信源 76→68 的方向正确但未清理行级漂移（F-5）。
- **新人视角**：仅凭本束可清楚判断「话题能干什么」——5 场景 × 适用对象 × 优势条目 × 群聊对照齐备，且页脚「我想反馈」入口、三通用能力均在册。需自行确认者也已列明：开通条件、套餐、客户端版本门槛、入口路径、机器人来源与权限（`F-044`）、功能名到底是「话题」还是「频道」（`F-045`）、API 文档目标页（`F-038`/`F-005`）。唯一干扰是 `04` 的跨篇指认错误（F-2），可能让新人在 `02` 里找不到「分享话题帖」。
- **老板视角**：信息增量足以支撑一次「要不要评估/试用」的判断，但**不足以支撑采购决策**——页面零量化成效（`F-039`）、零客户案例、无价格与准入（`F-044`）。产出对公开知识库是**合适的**：它把一份广告式场景页忠实登记为「价值主张清单」并标清可信度上限（单源 + 需登录 + 无日期），对读者是净正向；前提是修掉 F-1 的索引残格以保持知识库自身整洁。
- **未来视角**：`stale_after=2027-01-31` 到期时最可能漂移的是：①5 个分页 `?p=` 取值与页面存续（`F-008`/`F-042`）；②「话题 vs 频道」是否并轨（`F-045`）——这最可能使本束与 5.0.12 束的并置口径收敛为单一事实；③5.0.12 束 F-019 登记的 smartpage 与本页关系若有新证据（`F-043`）；④是否出现第三方独立信源/官方帮助中心条目（`F-040`）；⑤开通条件/套餐/客户端门槛是否补齐（`F-044`）。源页无版本号/日期使复核只能以「抓取日 2026-10-16 快照」为锚，到期时须逐字重取渲染页与入册 F 编号对拍——这是本束时效管理的主要困难（已在 `verification.md` 状态裁决中列为复核项）。

### 独立复算结论与自洽性

- F 编号：双份 47/47 相等、连续、表行 47 —— **自洽**。
- tencent 计数：束 18、概念 140、示例 48、信源 68、事实 2879 —— **与 `tencent/index.md` 声明逐项自洽**。
- 上层计数：total 641、jishu 475、ai 246、ecosystems 94 —— **与 `doc/bundles/index.md`、`jishu/ai/index.md`、`ecosystems/index.md` 声明自洽**。
- 「信源」76→68 处置：**成立**（68 为机械真值；76 不可复现）。唯一残留为行级漂移（F-5），非本次引入。
- 索引完整性：`wecom-5-0-12-release/index.md` 恰 +1 行 —— **成立**；`jishu/ai/index.md` 表行残格 —— **不成立（F-1）**。

***

# 企业微信「话题」场景最佳示例页 → OKF Wiki 知识包 - Independent Review（R2）

> 评审性质：**fresh-context 独立对抗复核（只读）**。R2 评审者未参与 R1、未参与实施与修复轮，未修改除本文件外的任何文件，未执行 `git add`/`git commit`。
> 取证限定：源页 `page.weixin.qq.com` 对未登录访客为登录墙，R2 **未重新联网抓取**；逐字比对基准为任务本轮下发的**完整逐字快照**（含页面公共框架行：大标题「了解话题最佳示例」/「使用场景：」/ 5 项导航 / 各页底部「更多场景」交叉链接区 / 页脚反馈入口），据此上一轮被判「不可复核」的 F-003/F-006 在本轮**已可逐字复核**。

## R2 检查点（复核 R1 发现 + 全量 AC 重验）

- [x] CP2-1: R1 F-1 / Issue I-1 已关闭——`jishu/ai/index.md` 生态行恢复 4 格且第 3 格为 `16`
  - **Type**: `rule`
  - **Covers**: AC-3, TR-I-1.1, TR-I-1.2
  - **Evidence**:
    - `git -C projects/awesome-okf-xs diff -- doc/bundles/jishu/ai/index.md`：生态行两侧均为 4 格，`-| … | 93 | 16 | …` → `+| … | 94 | 16 | …`，**语义变更仅「93→94」一处**，第 3 格 `16` 保留；该文件本轮 diff 共 3 处（description `245→246`、正文 `245→246`、生态行 `93→94`），无其他改动。
    - 机械列数校验：表头 `| 分类 | 束数 | 成员目录 | 一句话简介 |` = **4 格**；L18–L23 共 6 行数据行**全部 = 4 格**，与表头一致。
  - **结论**：**关闭**。

- [x] CP2-2: R1 F-2 / Issue I-2 已关闭——`04-general-capabilities-and-feedback.md` 不再错误指认 `02`，且未引入新问题
  - **Type**: `rule`
  - **Covers**: AC-6, TR-I-2.1
  - **Evidence**:
    - `04-general-capabilities-and-feedback.md` L32 现为：「**分享话题帖**（F-036）：给出两种传播方式『链接、二维码』；**该能力在本束中仅见于源页场景 5（F-036），其余四个场景页未声明该能力，本束不作跨场景外推。**」——已无「在收集产品意见中出现」类指认。
    - 全束 grep「分享话题帖」= 9 处命中（`index.md` L35、`log.md` L53、`article-source.md` F-036、`00` L37/L58、`04` L4/L5/L28/L32）；**无一处**指向 `02-feedback-collection.md`；`02` 全文「分享话题帖」零命中。
    - **新问题判定**：被删句原附带 F-006 引用（「页面底部『更多场景』交叉链接亦属链接传播形态」）；删除后 `04` 不再引 F-006，但 F-003/F-006 仍分别由 `00-overview` L24/L25 与 `article-source.md` L52/L55 支撑，**无 F 依据悬空**；修订句以 F-036 为唯一依据、与快照一致（P5 有「分享话题帖」、P1–P4 均无）。**未引入新问题**。
  - **结论**：**关闭**。

- [x] CP2-3: R1 F-3 / Issue I-3 已关闭——`verification.md` 取证补记准确、无源页外断言
  - **Type**: `rule`
  - **Covers**: AC-2, AC-7, TR-I-3.1
  - **Evidence**: `references/verification.md` L66–L73「### 取证补记（F-003 / F-006：页面框架行）」已落盘。对照本轮完整快照：①`使用场景：`确为大标题下、5 项导航前的独立一行（每页公共框架）→ F-003 成立；②「更多场景」交叉链接区确在各场景页底部、5 页均有 → F-006 成立；③补记给出原文样例「更多场景 / 💬 收集产品意见 → / 📘 分享经验知识 → / 📣 发布公告通知 → / ✨ 更多功能及反馈 →」，与快照 P1 底部顺序**逐字一致**，且「各项顺序在各页不同」（如 P2 起始为「📘 分享经验知识 →」）亦与快照一致；④补记仅登记位置/原文/取证方式（2026-10-16 渲染态 `document.body.innerText`），**未新增 F 编号、未扩写功能、无源页外断言**。
  - **结论**：**关闭**。

- [x] CP2-4: R1 F-4（advisory）与 F-6（advisory）更正核对——F-6 相符；F-4 核心更正相符、残留一处措辞瑕疵（F-R2-A）
  - **Type**: `rule`（advisory 类）
  - **Covers**: TR-6.1, TR-6.2, NFR-1
  - **Evidence**:
    - **F-6 扫描口径声明**：`tasks.md` L118「AC-4/AC-7 的禁用串与会话元数据关键词扫描范围 = 新增 bundle 全目录 + spec 目录 `facts.md`；`spec.md`/`tasks.md` 自身因条款描述需要含政策字面串，不计入扫描范围」——**与实测相符**（对 bundle 全目录与 `facts.md` 扫 `file://`/`C:\Users`/`.temp`/`xsrf`/`tinyid`/`corp_id`/`access_token` 命中 **0**；`spec.md`/`tasks.md` 命中为政策自述）。
    - **F-4 log.md frontmatter 更正**：`tasks.md` TR-6.2 已由原「8 个含 frontmatter…log.md 与基准束同构无 frontmatter」更正为「**9 个文件带 frontmatter，其中 8 个含 `sources:`**；`log.md` 带 frontmatter（`type: Changelog`）不含 sources」——**9/8 数字与事实相符**（实测：根 index、log、5 篇 concepts、article-source、verification 共 9 个带 frontmatter，log 为第 9 个且无 `sources`）。
    - **残留瑕疵**：同句「`log.md` 带 frontmatter（`type: Changelog`）但**按基准束 5.0.12 同构**不含 sources」中的「**同构**」与事实不符——基准束 `wecom-5-0-12-release/log.md` 首行为 `# 变更日志`、**无任何 frontmatter**，两束 log.md 形态**不同构**（F-4 原建议措辞即为「带最小 frontmatter、不含 sources，与基准束不同构」）。定性见 F-R2-A（advisory，不影响知识交付物）。
  - **结论**：F-6 **关闭**；F-4 **核心关闭**，残留措辞见 F-R2-A。

- [x] CP2-5: AC-1 重验——Bundle 结构与规范完整
  - **Type**: `rule`
  - **Covers**: AC-1, FR-1, NFR-1
  - **Evidence**: `Get-ChildItem -Recurse -File` 清点 = **11 个 `.md`**（根 `index.md`/`log.md`；`concepts/index.md` + `00/01/02/03/04`；`references/index.md` + `article-source.md` + `verification.md`），**无 `examples/` 目录**。三个 index.md 均含 `{toctree}` 块，条目逐一解析存在（根 → `concepts/index`/`references/index`/`log`；`concepts/index` → 5 篇；`references/index` → article-source/verification）。根 index frontmatter 含 `okf_version`/`status`/`stale_after`/`sources`（W + W-P2…W-P5 共 5 条 URL，覆盖全部 URL 型来源代号；W-P1 与 W 同 URL 已在 `article-source.md` 显式标注）。
  - **结论**：**pass**。

- [x] CP2-6: AC-2 重验——双份 F 编号一致且核验真实
  - **Type**: `rule`
  - **Covers**: AC-2, TR-1.1, TR-4.1
  - **Evidence**: 自写正则 `F-\d{3}` 独立提取：`facts_uniq = 47`、`article_uniq = 47`、**集合相等 = True**、仅 facts/仅 article 均为空、`min F-001 / max F-047`、**连续无跳号 = True**；行级 `^\|\s*F-\d{3}\s*\|` 计数 `facts 表行 = 47`、`article 表行 = 47`。四条口径分层 **4/4** 在 `verification.md`（口径分层表 4 行）与 concepts 正文均有呈现（单源 F-040；命名张力 F-045 见 `00/01/03/04`；描述性口径 F-046 见 `00/01/02/03`；官方未给项 F-044 见 `00/01/02/03/04`）。
  - **结论**：**pass**。

- [ ] CP2-7: AC-3 重验——三级索引与计数机械同步（门禁通过、计数自洽，但发现 `jishu/index.md` AI 行计数未同步 → F-R2-1）
  - **Type**: `rule`
  - **Covers**: AC-3, TR-5.1, TR-5.2, TR-5.3
  - **Evidence**:
    - 门禁重跑：`python scripts\check-bundles-index.py` → `bundles 总索引对账通过: 9 域 / 61 组 / 641 束，…五面一致。 EXIT=0`；`python scripts\check-toctrees.py` → `toctree 检查通过：全部 index.md 引用有效，所有内容文档均可达。 EXIT=0`（本束 `wecom-topic-scenarios` 零命中）。
    - 本束三处到位：`tencent/index.md` 导航表 L31、相关链接 L59、toctree L84；`ecosystems/index.md` 本类 94 / 腾讯行 18；`jishu/ai/index.md` 246 束 / ecosystems 行 `94`/`16`；`doc/bundles/index.md` `total_bundles: 641`、计数行 641、mermaid jishu 475、节标题「475 束 · 18 组」、jishu 表 ai 行 246。
    - 计数独立复算见下「独立复算结论（R2）」——tencent 18/140/48/68/2879 与上层 641/475/246/94 均自洽。
    - **缺陷（F-R2-1）**：`jishu/index.md` 属 AC-3 Given 清单内文件，其 L20 ai 行简介仍为「**245 束**按读者意图归为六大类…」，而本束使其上游 ai 束数由 245→246（`jishu/ai/index.md` 与 `doc/bundles/index.md` 均已更新为 246，门禁亦以 246 通过），该文件**未同步**。此漂移由本次改动引入（基线 HEAD 三者同为 245），且 `tasks.md` Task 5 证据「`jishu/index.md` 未改：其束数为递归占位、**无本次相关数字**」与事实不符（该行简介确含数字）。
  - **结论**：**fail**（映射发现 F-R2-1）。

- [x] CP2-8: AC-4 重验——链接 / 编码 / 溯源 / 双向互链机械门禁
  - **Type**: `rule`
  - **Covers**: AC-4, TR-6.1, FR-6
  - **Evidence**:
    - `python .agents\skills\submodule-atomization-finalize-cmd\scripts\check_doc_links.py <bundle>` → `checked_files=11 links=57 broken=0 EXIT=0`；`python scripts\check-utf8.py` → `UTF-8 检查通过: 11688 个文件均为有效 UTF-8。 EXIT=0`。
    - **回归关注（唯一变化）**：`links` 由 R1 的 58 变为 57、`broken` 仍为 0。独立复核：bundle 内联链接总数 62（其中 http 链接 5、本地引用 57）；R1 之后对 bundle 正文的**唯一**涉链编辑即 I-2 删除 `04` L32 的一句 Markdown 链接（I-3 补记为纯文本、无链接），故 58→57 由该删除**唯一解释**，无新增断链。
    - 禁用串：5 个被改索引文件命中 **0**；bundle 全目录与 `facts.md` 命中 **0**。派生产物溯源：9 个文件带 frontmatter，其中 8 个含 `sources:`（与 OKF v0.2 及基准束一致；AC-4 字面「`source`」为简写，NFR-1 明列字段为 `sources`）。双向互链：本束根 index「主题关联」L51→5.0.12、L52→5.0.10；`git -C projects/awesome-okf-xs diff -- wecom-5-0-12-release/index.md` = **恰 1 处 `+` 插入、0 删除**（新增 L59 回链行）；5.0.10 束未改动。
  - **结论**：**pass**。

- [x] CP2-9: AC-5 重验——口径分层与读者决策可用性（rubric）
  - **Type**: `rubric`
  - **Covers**: AC-5, TR-3.3
  - **Scale**: 1-5
  - **Anchors**: 1 = 厂商自述、未给项与可核实事实混写，读者无法判断可信度；3 = 主要声明有出处但口径分层不统一、个别场景条目无 F 编号；5 = 每条场景名/适用对象/优势条目可回溯 F 编号，「厂商自述单源 / 官方未给 / 命名张力 / 信源需登录」四类标签全文一致，「已知边界」可直接支持读者「用不用、怎么用、还缺什么」的决策
  - **Pass Threshold**: >= 4
  - **Evidence**: 得分 **5 / 5**（R1 唯一的扣分项 F-2「`04` 跨篇指认有误」已关闭）。五篇 concepts 场景名/适用对象/优势条目均带 F 编号（抽查零漏挂）；四类标签全文一致；根 index「已知边界」8 条（单源 / 无版本日期 / 信源需登录 / 话题vs频道 / 同形 smartpage / 官方未给项 / 描述性口径 / 零量化）可直接支撑「用不用、怎么用、缺什么」。
  - **结论**：**pass**。

- [x] CP2-10: AC-6 重验——知识结构与来源忠实度（rubric）
  - **Type**: `rubric`
  - **Covers**: AC-6, TR-3.3
  - **Scale**: 1-5
  - **Anchors**: 1 = 按源页顺序平铺翻译、无分层与互链、夹带页面外推断；3 = 有分层但层间重复、跨篇跳转不清、个别断言超出源页可支撑范围；5 = 总览答「这是什么页 / 5 场景怎么分 / 信源与时效」，场景篇答「谁适用 / 优势是什么 / 厂商对照论证是什么」，边界篇答「官方没说什么 / 读者还需自行确认什么」，篇间阅读路径明确、Mermaid 节点有 F 依据、无一条断言超出源页可支撑范围
  - **Pass Threshold**: >= 4
  - **Evidence**: 得分 **5 / 5**（R1 两个扣分项 F-2、F-3 均已关闭）。三层职责清晰（总览定位/场景全景/信源时效 → 场景机制篇 → 边界提示 + 篇间阅读路径）；Mermaid 1 张 `flowchart TD`，全部节点（P/N/S1–S5/A1–A7）挂 F 编号，均落在 F-001～F-047 内；逐字回源抽查 ≥8 条全部在下发快照命中（见下「逐字回源抽查」）；无一条断言超出源页可支撑范围。
  - **结论**：**pass**。

- [x] CP2-11: AC-7 重验——隐私红线与零编造
  - **Type**: `rule`
  - **Covers**: AC-7, TR-1.2, TR-4.3, NFR-5
  - **Evidence**: bundle 与 `facts.md` 会话/账号元数据关键词扫描命中 **0**（`xsrf`/`tinyid`/`corp_id`/`access_token`/企业名/用户标识/内部文档 ID 均无）。`.temp/smartpage` 不存在；`raw.html`/`probe.txt`/`psd_pages.json`/`all_sections.txt` 全仓检索 = **0 命中**（`.temp` 其余内容均为其他并行会话产物，与本任务无关）；bundle 内 `.temp` 引用 = 0。逐字回源抽查 ≥8 条全部命中（见 CP2-10/下节）。
  - **结论**：**pass**。

## 逐字回源抽查（对照本轮完整快照，≥8 条）

1. 导航 5 项及顺序（F-004）：🤝 推进项目协作 / 💬 收集产品意见 / 📘 分享经验知识 / 📣 发布公告通知 / ✨ 更多功能及反馈——**命中**。
2. P1 适用对象「项目管理、产品经理、销售、商务等」（F-009）——**命中**。
3. P1 优势1 机器人汇总「进展与结论…不用逐条翻帖、或逐个找同事确认 +（点击查看API接口文档）」（F-010）——**命中**。
4. P1 优势2 对照「群聊：多项工作的消息互相穿插，容易串线 ／ ✅话题：一项工作一个帖子，一目了然」（F-011）——**命中**。
5. P2 优势3 三子项「贴表情 / 轻提醒（发帖仅红点提示…回复只通知楼主）/ 长期收集（成员可以随时在话题中发帖）」（F-017–F-019）——**命中**。
6. P4 优势6「已读未读…阅读回执 / 阅读状态」（F-032）——**命中**。
7. P5 三项能力「搜索 / 消息转话题 / 分享话题帖（通过链接、二维码等方式轻松传播话题）」（F-034–F-036）——**命中**。
8. 页脚「关于话题功能 你有什么想反馈吗？我想反馈」（F-005）——**命中**。
9. 8 组「群聊/话题」对照计数（P1×1 / P2×3 / P4×4，P3/P5 无）（F-037）——**命中**。
10. 「使用场景：」框架行（F-003）与底部「更多场景」交叉链接区（F-006）——本轮完整快照**均命中**（R1 的快照省略所致）。

## 独立复算结论（R2）

- **F 编号**：双份 47/47 相等、连续无跳号、表行 47 —— **自洽**。
- **tencent 计数（自写目录树脚本独立复算）**：束 **18** / 概念 **140** / 示例 **48** / 信源登记 **68** —— 与 `tencent/index.md`「18 个知识包、140 概念、48 示例、68 信源」**逐项一致**；计数口径（各束 `concepts/examples/references` 目录非 index `.md` 求和）可复现。
- **tencent 事实数**：独立复算 = **2879**，与 `tencent/index.md` 声明一致。可复现口径：逐束取该束**内容/登记 `.md`（含根 index、concepts、references、束内 `spec/facts.md`）中的最大 F 编号之和，排除 `log.md`**——18 束求和 = 2879，扣除本束 47 后既有束 = **2832**（与 spec 基线一致）。注：若误将 `log.md` 计入则得 2881（多 2，来自 `tencent-meeting-cli/log.md`「无 F-200」与 `tencentdb-agent-memory/log.md`「无 F-301+」的政策自述串）；若仅取 `references/` 目录则得 2720（漏计 `ai-infra-guard` 存于束内 `spec/facts.md` 的 68 条）。故 2879 为真值，R1 记录的口径描述虽略简（非仅 references/），但数值**可复现且与本束 +47 一致**。
- **上层计数**：total **641**、jishu **475**、ai **246**、ecosystems **94** —— 与 `doc/bundles/index.md`、`jishu/ai/index.md`、`ecosystems/index.md` 声明自洽（`check-bundles-index.py` EXIT=0 佐证）。
- **索引完整性**：`wecom-5-0-12-release/index.md` 恰 +1 行、`jishu/ai/index.md` 表行已恢复 4 格 —— **成立**；`jishu/index.md` AI 行计数未同步 —— **不成立（F-R2-1）**。

## Review History

### Review R2
- **Result**: `fail`
- **Reviewer**: fresh-context 独立对抗评审子代理（未参与 R1/实施/修复；只读；仅写入本 `review.md`）
- **Checks Performed**:
  - `git -C projects/awesome-okf-xs diff`（`jishu/ai/index.md`、`ecosystems/index.md`、`tencent/index.md`、`wecom-5-0-12-release/index.md`、`doc/bundles/index.md`）+ 全表列数机械校验
  - `python scripts\check-bundles-index.py`（EXIT=0）、`python scripts\check-toctrees.py`（EXIT=0）、`python scripts\check-utf8.py`（EXIT=0）
  - `python .agents\skills\submodule-atomization-finalize-cmd\scripts\check_doc_links.py <bundle>`（`checked_files=11 links=57 broken=0` EXIT=0）
  - 自写正则脚本：F 编号双份集合比对、toctree 条目存活、内联链接 62（http 5/本地 57）、禁用串与隐私关键词扫描、目录树计数与事实数复算
  - `grep 分享话题帖` / `使用场景|更多场景` 全束扫描；`.temp` 残留检索
- **Evidence**:
  - R1 三条可行动发现（F-1/I-1、F-2/I-2、F-3/I-3）**全部关闭**，各有回归证据（见 CP2-1/2/3）。F-4 核心更正（9/8 与 sources）**相符**、残留「同构」措辞瑕疵（F-R2-A advisory）；F-6 扫描口径声明**相符**。
  - 全量 AC 重验：AC-1/2/4/5/6/7 **pass**；**AC-3 相关 checkpoint fail** —— `jishu/index.md` L20 ai 行简介仍为「245 束」，未随本束 245→246 同步（新发现 F-R2-1）。
  - 独立复算与 index 声明逐项自洽（tencent 18/140/48/68/2879；上层 641/475/246/94）。
  - 逐字回源抽查 10 条全部命中本轮完整快照。
- **Blocked By**: 不适用（本轮无受阻检查点；源页登录墙不可重取，逐字比对以下发完整快照为可复核证据路径，故不判 `blocked`）

### 分级发现清单（R2 Findings）

- **F-R2-1 · 严重级别 P2 · 可行动（本次改动引入）**
  - 现象：`projects/awesome-okf-xs/doc/bundles/jishu/index.md` L20（AI 行）简介仍写「**245 束**按读者意图归为六大类…」，而本束使其上游 ai 束数由 245→246——`jishu/ai/index.md`（245→246）与 `doc/bundles/index.md`（jishu 表 ai 行 245→246）均已同步，门禁亦以 ai=246 通过，唯 `jishu/index.md` 未同步，形成 245 vs 246 的计数漂移。
  - 复现方式：`git -C projects/awesome-okf-xs log -1 --format="%h %ad" -S "245 束" -- doc/bundles/jishu/index.md` → `1f927d0f`（该文件 AI 行于上一提交由 244→245 主动同步，说明该数字属受维护口径，非「历史一级目录计数」）；对照 `git diff -- doc/bundles/jishu/ai/index.md`（`245→246`）与 `doc/bundles/index.md`（ai 行 `245→246`）。`jishu/index.md` 属 AC-3 Given 清单内文件。
  - 期望结果：将 `jishu/index.md` L20 ai 行简介「245 束」更正为「**246 束**」，与 `jishu/ai/index.md` 及 `doc/bundles/index.md` 一致。
  - 备注：`check-bundles-index.py` 仅审计 `doc/bundles/index.md`，不校验 `jishu/index.md`，故门禁为盲区；`tasks.md` Task 5 证据「`jishu/index.md` 未改：其束数为递归占位、无本次相关数字」的**理由与事实不符**（该行简介确含数字）。
- **F-R2-A · 严重级别 P2 · advisory（措辞残留）**
  - 现象：`tasks.md` TR-6.2 中「`log.md` 带 frontmatter（`type: Changelog`）但**按基准束 5.0.12 同构**不含 sources」用「同构」描述，而基准束 `wecom-5-0-12-release/log.md` 首行为 `# 变更日志`、**无任何 frontmatter**，两束 log.md 形态**不同构**。
  - 复现方式：读取两束 `log.md` 头部 3 行对比。
  - 期望结果：删去「同构」或改为「与基准束**不同构**」，与 F-4 原建议措辞一致；不影响知识交付物正确性。
  - 备注：F-4 的核心数字更正（9 个带 frontmatter / 8 个含 sources）已正确落地，本残留不构成 AC 层缺陷。

### 四视角对抗结论（R2）

- **魔鬼代言人**：最可能被质疑处仍是「厂商自述被当事实」与「计数改动引入不自洽」。①厂商自述：全束以「页面原文声称」措辞、F-040 单源、`已知边界` 集中声明零量化（F-039）、8 组对照标为「厂商自证定性论证」，未发现把厂商话术写成产品事实的语句——**仍成立**。②计数自洽：R1 的索引残格（F-1）已修复且门禁通过，但**本次改动仍在 `jishu/index.md` 留下一处 245 vs 246 的计数漂移（F-R2-1）**——即「改索引时漏改一处」这一模式在两轮间复现，说明改索引面缺一张「全链路计数扇出清单」。
- **新人视角**：仅凭本束可清楚判断「话题能干什么」——5 场景 × 适用对象 × 优势条目 × 群聊对照齐备，页脚反馈入口与三项通用能力在册；需自行确认者也已列明（开通条件/套餐/客户端门槛/入口路径/机器人来源与权限 F-044、功能名话题还是频道 F-045、API 文档目标页 F-038）。R1 的唯一干扰（`04` 跨篇指认错误 F-2）**已消除**，新人在 `02` 里不会再被误导去查找「分享话题帖」。
- **老板视角**：信息增量足支撑「要不要评估/试用」、不足以支撑采购决策（零量化 F-039、零案例、无价格与准入 F-044）；产出对公开知识库是净正向，且「单源 + 需登录 + 无日期」可信度上限已明示。前提是保持知识库自身计数整洁——**F-R2-1 是当前唯一待清项**。
- **未来视角**：`stale_after=2027-01-31` 到期时最可能漂移者不变——①5 个分页 `?p=` 与页面存续（F-008/F-042）；②「话题 vs 频道」是否并轨（F-045）；③5.0.12 束 F-019 同形 smartpage 关系新证据（F-043）；④是否出现第三方独立信源（F-040）；⑤开通条件/套餐/客户端门槛补齐（F-044）；⑥`jishu/index.md` 等非门禁覆盖索引的人工同步（本轮新增关注）。

### 受限 / 未覆盖部分（诚实声明）

- 源页对未登录访客为登录墙，R2 **未重新联网抓取**，逐字比对以任务下发的**完整逐字快照**为准；`?p=` 5 分页、页脚与「更多场景」框架行均以该快照为可复核证据路径。若该快照与线上渲染态漂移，本报告未覆盖该差异。
- 未对 `wecom-5-0-10-release` 束做独立全文重读（其 `git` 状态未改动，双向互链仅要求 5.0.12 回补，故未触发）。
- `check-mermaid.py` 对 `projects/` 子模块路径返回「0 文件、0 问题」的**假阴性**已实测复现（EXIT=0 但扫描 0 文件）；Mermaid 结构正确性由 R2 人工核对节点挂 F 编号得出，未再构造临时副本复跑。

***

# 企业微信「话题」场景最佳示例页 → OKF Wiki 知识包 - Independent Review（R3）

> 评审性质：**fresh-context 第三轮独立对抗复核（只读）**。R3 评审者未参与实施、未参与 R1/R2 评审与修复轮；除本 `review.md` 外未修改任何文件，未执行 `git add`/`git commit`。
> 取证限定：源页 `page.weixin.qq.com` 对未登录访客为登录墙，R3 **未重新联网抓取**；逐字比对基准 = 任务本轮下发的**源页完整逐字快照**（大标题「了解话题最佳示例」/「使用场景：」框架行 / 5 项导航及顺序 / 5 分页正文 / 各页「更多场景」交叉链接区 / 页脚反馈入口）。

## R3 检查点（R2 发现关闭复核 + 全量 AC 独立重验）

- [x] CP3-1: R2 F-R2-1 / Issue I-4 已关闭，且独立扇出复扫零遗漏
  - **Type**: `rule`
  - **Covers**: AC-3, TR-I-4.1, TR-I-4.2
  - **Evidence**:
    - `git -C projects/awesome-okf-xs diff -- doc/bundles/jishu/index.md` = **单个 hunk、单行语义变更**：`-…245 束…` → `+…246 束…`（左列 `[递归束数](../index.md)` 占位未动）；六处受改文件 diffstat = 6 files changed, 16 insertions, 12 deletions。
    - **独立扇出复扫（R3 自写，不复用 I-4 结论）**：对 `doc/bundles/` 全树 grep 全部涉改旧值/新值 → `rg -n "245 束" doc/bundles` **零命中**；`246 束` 三处（`doc/bundles/index.md` L139 ai 行、`jishu/index.md` L20 ai 行、`jishu/ai/index.md` L5 description）均为**受维护口径**且互为一致；`640 束`/`474 束`/`\b640\b`/`\b474\b` 在 `doc/bundles/index.md` **零命中**（已为 641/475）。`rg` 其余命中经逐条判定：**唯一非空项**为各束 `log.md` / `references/verification.md` 内**带时点的历史日志/核验记录**（如 `wecom-topic-scenarios/log.md` L37「…245→246…」与 L65 基线句「17 束 / 135 概念 / 48 示例 / 76 信源 / 2832 条」、`tencent/index.md` L45 叙述文本），属 **append-only 回溯证据**，按惯例不回改、不构成漏改。
    - 边界项判定：`wecom-topic-scenarios/log.md:65` 基线句带明确 2026-10-16 时点，且同文件已落实际值 18/140/48/68/2879 并自述 `76` 为**陈旧漂移值** → 历史披露口径，**非遗漏**。
  - **结论**：**关闭**（独立复扫零遗漏；`doc/bundles` 内计数类旧值已无残留）。

- [x] CP3-2: R2 F-R2-A / Issue I-5 已关闭
  - **Type**: `rule`
  - **Covers**: AC-1, TR-6.1, TR-6.2, NFR-1
  - **Evidence**: `tasks.md` L122 末段现文：「…`log.md` 带 frontmatter（`type: Changelog`）但**不含 `sources`**；…（2026-10-16 依独立评审 F-4 更正原表述「log.md 与基准束同构无 frontmatter」；**F-R2-A 进一步更正：基准束 `wecom-5-0-12-release/log.md` 无任何 frontmatter，故「与基准束同构」的说法不成立，该措辞已删除**。）」——**「与基准束同构」措辞已删除**。同句事实陈述独立复核（自写脚本逐文件判定）：bundle 内 **9 个文件带 frontmatter，其中 8 个含 `sources:`**（根 `index.md`、5 篇 concepts、`article-source.md`、`verification.md`）；`log.md` 带 frontmatter（`type: Changelog` + `title`）但**无 `sources`**；`concepts/index.md`、`references/index.md` 无 frontmatter；基准束 `wecom-5-0-12-release/log.md` 首行为 `# 变更日志`、**无任何 frontmatter**（`Get-Content -TotalCount 5`）。**9/8 数字与「两束 log.md 不同构」判定全部与事实相符**。
  - **结论**：**关闭**。

- [x] CP3-3: R1 F-1 / F-2 / F-3（Issue I-1 / I-2 / I-3）未被本轮改动破坏
  - **Type**: `rule`
  - **Covers**: AC-3, AC-6, AC-7
  - **Evidence**:
    - **I-1**：`git diff -- doc/bundles/jishu/ai/index.md` 该文件本轮共 3 处（description `245→246`、正文 `245→246`、生态行 `93→94`）；生态行两侧均 **4 格**，`-| … | 93 | 16 | …` → `+| … | 94 | 16 | …`，第 3 格 `16` 保留。
    - **I-2**：全束 grep「分享话题帖」= 9 处（`00` L37/L58、`04` L4/L5/L28/L32、`article-source.md` L110、`log.md` L53、根 `index.md` L35），**无一处指向 `02-feedback-collection.md`**；`02` 全文「分享话题帖」零命中；`04` L32 现为「该能力在本束中仅见于源页场景 5（F-036），其余四个场景页未声明该能力，本束不作跨场景外推」。
    - **I-3**：`verification.md` L66–L73「### 取证补记（F-003 / F-006：页面框架行）」在册，其「更多场景」样例「💬 收集产品意见 → / 📘 分享经验知识 → / 📣 发布公告通知 → / ✨ 更多功能及反馈 →」与快照 P1 底部**逐字一致**，且「各项顺序在各页不同」与快照（P2 起始为「📘 分享经验知识 →」）一致。
  - **结论**：三条均**未被破坏**。

- [x] CP3-4: AC-1 重验——Bundle 结构与规范完整
  - **Type**: `rule`
  - **Covers**: AC-1, FR-1, NFR-1
  - **Evidence**: `Get-ChildItem -Recurse -File` 清点 = **11 个 `.md`**（根 `index.md`/`log.md`；`concepts/index.md` + `00/01/02/03/04` 5 篇；`references/index.md` + `article-source.md` + `verification.md`），**无 `examples/` 目录、无任何非 `.md` 文件**。三个 index 均含 `{toctree}` 块且条目逐一解析存在（根 → `concepts/index`/`references/index`/`log`；`concepts/index` → 5 篇；`references/index` → article-source/verification）。根 `index.md` frontmatter 含 `okf_version: "0.2"`/`type`/`title`/`description`/`tags`/`generated`/`verified`/`status: stable`/`stale_after: "2027-01-31"`/`sources`（W + W-P2…W-P5 共 5 条 URL，覆盖全部 URL 型来源代号；W-P1 与 W 同 URL 已在 `article-source.md` L25 显式标注「不单列 sources」）。
  - **结论**：**pass**。

- [x] CP3-5: AC-2 重验——双份 F 编号一致且核验真实
  - **Type**: `rule`
  - **Covers**: AC-2, TR-1.1, TR-4.1
  - **Evidence**: R3 自写正则独立提取：`facts_uniq = 47`、`article_uniq = 47`、**集合相等 = True**、`min F-001 / max F-047`、**连续无跳号 = True**；行级 `^\|\s*F-\d{3}\s*\|` 计数 `facts 表行 = 47`、`article 表行 = 47`（= 最大编号）。bundle 内**被引用的 F 编号全部落在 F-001～F-047 内**（自写扫描 `out of range: []`）。四条口径分层 **4/4** 落地：`verification.md`「口径分层表」4 行 + concepts 正文（单源 F-040；话题/频道命名张力 F-045 见 `00`/`01`/`03`/`04`；描述性口径 F-046 见 `00`/`01`/`02`/`03`；官方未给项 F-044 见 `00`/`01`/`02`/`03`/`04`）。
  - **结论**：**pass**。

- [x] CP3-6: AC-3 重验——三级索引与计数机械同步（R2 唯一 fail 项已闭合）
  - **Type**: `rule`
  - **Covers**: AC-3, TR-5.1, TR-5.2, TR-5.3
  - **Evidence**:
    - 门禁重跑：`python scripts\check-bundles-index.py` → `bundles 总索引对账通过: 9 域 / 61 组 / 641 束，frontmatter、计数行、节标题、分组表、toctree 五面一致。 EXIT=0`；`python scripts\check-toctrees.py` → `toctree 检查通过: 全部 index.md 引用有效，所有内容文档均可达。 EXIT=0`（本束 `wecom-topic-scenarios` 零命中）。
    - 本束三处到位：`tencent/index.md` 导航表 **L31**、相关链接 **L59**、toctree **L84**（`git diff` 三处均 `+1`）。
    - 五面计数：`doc/bundles/index.md` `total_bundles: 641`（diff `640→641`）、计数行 641、mermaid jishu 节点 `475 束`、节标题「475 束 · 18 组」、jishu 表 ai 行 `246`；`ecosystems/index.md` 本类 `94`、腾讯行 `18`；`jishu/ai/index.md` `246` + ecosystems 行 `94`/`16`；`jishu/index.md` `246`（I-4 修复）。
    - 上层计数独立复算见「独立复算结论（R3）」——total 641 / jishu 475 / ai 246 / ecosystems 94 / tencent 18 全项自洽。
    - **R2 缺陷（F-R2-1）已闭合**：`rg -n "245 束" doc/bundles` 零命中（见 CP3-1）。
  - **结论**：**pass**（R2 唯一 fail 项已闭合）。

- [x] CP3-7: AC-4 重验——链接 / 编码 / 溯源 / 双向互链机械门禁
  - **Type**: `rule`
  - **Covers**: AC-4, TR-6.1, FR-6
  - **Evidence**:
    - `python .agents\skills\submodule-atomization-finalize-cmd\scripts\check_doc_links.py <bundle>` → `checked_files=11 links=57 broken=0 EXIT=0`；`python scripts\check-utf8.py` → `UTF-8 检查通过: 11688 个文件均为有效 UTF-8。 EXIT=0`。
    - 禁用串扫描（口径 = bundle 全目录 + spec `facts.md`）：`file://` / `C:\Users` / `.temp` / `xsrf` / `tinyid` / `corp_id` / `access_token` / `corpid` / `ticket` **命中数 = 0**（复数命中为 `rg` EXIT=1）。
    - 派生产物溯源：**9 个文件带 frontmatter、其中 8 个含 `sources:`**（实测）；AC-4 字面「`source`」为简写，NFR-1 明列字段为 `sources`。
    - 双向互链：本束根 `index.md`「主题关联」L51→5.0.12、L52→5.0.10；`git diff -- wecom-5-0-12-release/index.md` = **恰 1 处 `+` 插入、0 删除**（新增 L59 回链行）；5.0.10 束未改动（diffstat 未列）。
    - **附注（advisory F-R3-A）**：`verification.md`「门禁运行记录」记录的 `links=58`/`内联链接 63`/`本地引用 58` 与 R3 实测（`links=57`、bundle 内联链接 **62**（http 5 + 本地 57））相差 1，系 I-2 删除 `04` 一处链接后未回刷该记录——属**时点记录未刷新**，非门禁实际失败（`broken=0` 仍成立）。
  - **结论**：**pass**。

- [x] CP3-8: AC-5 重验——口径分层与读者决策可用性（rubric）
  - **Type**: `rubric`
  - **Covers**: AC-5, TR-3.3
  - **Scale**: 1-5
  - **Anchors**: 同 R1/R2（1 = 混写不可判；3 = 分层不统一、个别条目无 F 编号；5 = 每条可回溯 F 编号、四类标签全文一致、「已知边界」直接支撑决策）
  - **Pass Threshold**: >= 4
  - **Evidence**: 得分 **5 / 5**。五篇 concepts 的场景名/适用对象/优势条目均挂 F 编号（R3 复查零漏挂）；四类标签（单源 F-040 / 命名张力 F-045 / 描述性口径 F-046 / 官方未给 F-044）全文一致；根 `index.md`「已知边界」8 条（单源 / 无日期版本 / 信源需登录 / 话题vs频道 / 同形 smartpage / 官方未给项 / 描述性口径 / 零量化）可直接支撑「用不用、怎么用、缺什么」。R1 扣分项 F-2 已闭合。
  - **结论**：**pass**。

- [x] CP3-9: AC-6 重验——知识结构与来源忠实度（rubric）
  - **Type**: `rubric`
  - **Covers**: AC-6, TR-3.3
  - **Scale**: 1-5
  - **Anchors**: 同 R1/R2
  - **Pass Threshold**: >= 4
  - **Evidence**: 得分 **5 / 5**（R1 两扣分项 F-2/F-3 均已闭合）。三层职责清晰（总览定位 / 场景全景 / 信源时效 → 场景机制篇 → 边界提示 + 篇间阅读路径）；Mermaid 1 张 `flowchart TD`，节点（P/N/S1–S5/A1–A7）全挂 F 编号且**全部落在 F-001～F-047**（R3 自写扫描 `out of range: []`）；逐字回源抽查 ≥8 条全部命中本轮快照（见下节）；未发现超出源页可支撑范围的断言。附 minor 观察（advisory F-R3-B）：`F-028`～`F-031` 的「声明摘要」正文短语（如「内容写错或安排有变」）在下发快照中无逐字对应（快照 P4 优势 2–5 仅给标题 + 群聊/话题对照行）——其性质为**要点式摘要而非逐字原文**（`facts.md` 表头即「声明摘要」、`03` 表头为「页面原文要点」），未构成源页外断言，措辞无需强制修改。
  - **结论**：**pass**。

- [x] CP3-10: AC-7 重验——隐私红线与零编造
  - **Type**: `rule`
  - **Covers**: AC-7, TR-1.2, TR-4.3, NFR-5
  - **Evidence**: bundle 全目录 + spec `facts.md` 会话/账号元数据关键词（`xsrf`/`tinyid`/`corp_id`/`access_token`/`corpid`/`ticket`/企业名/用户标识/内部文档 ID）命中 **0**。`.temp/smartpage` **不存在**（`Test-Path` = False）；`raw.html`/`probe.txt`/`psd_pages.json`/`all_sections.txt` 仅命中 `tasks.md`/`review.md`（政策/记录文本），**bundle 与 `facts.md` 零命中**；bundle 内 `.temp` 引用 = 0。逐字回源抽查 ≥8 条全部命中（见下节）。
  - **结论**：**pass**。

- [x] CP3-11: bundle 自 R2 以来是否变动（稳定性取证）
  - **Type**: `rule`
  - **Covers**: AC-1, AC-6
  - **Evidence**: bundle 为子模块内**未跟踪新目录**（`git status` = `?? …/wecom-topic-scenarios/`），无 git 基线；故以文件时间戳取证：11 个 bundle 文件 `LastWriteTime` 最新为 **2026-10-16 20:39:19**（`log.md`），其余为 19:41–20:37；而 R2 的 `review.md` 写入时点为 **20:58:48**。**即 bundle 全部文件最后写入均早于 R2** → R2 之后 bundle 内容**零改动**（R2 之后仅 `jishu/index.md` 21:00、`tasks.md` 21:09、本 `review.md` 变动，均在 bundle 之外）。旁证：`check_doc_links` 当前 `links=57` 与 R2 记录的 57 一致。R2 之后被 R1 修复触及的 bundle 文件（`04` 20:36:33 / `verification.md` 20:36:57 / `log.md` 20:39:19）均由 R2 复核。
  - **结论**：**pass**（bundle 自 R2 起零变动；AC-5/AC-6 无需按新内容重评）。

## 逐字回源抽查（R3，对照本轮完整快照，≥8 条）

1. 大标题「了解话题最佳示例」（F-001）+ 平台标识「使用 智能文档 发布」（F-002）——**命中**。
2. 导航 5 项及顺序（F-004）：🤝 推进项目协作 / 💬 收集产品意见 / 📘 分享经验知识 / 📣 发布公告通知 / ✨ 更多功能及反馈——**命中**。
3. `?p=` 映射（F-008）：HXPk2x=P1 / htt4Bf=P2 / ptlD2c=P3 / tR2p63=P4 / BMbevB=P5——**命中**。
4. P1 适用对象「项目管理、产品经理、销售、商务等」（F-009）——**命中**。
5. P1 优势1「@ 机器人即可让它汇总话题内各项工作的进展与结论，不用逐条翻帖、或逐个找同事确认 +（点击查看API接口文档）」（F-010）——**命中**。
6. P1 优势2 对照「群聊：多项工作的消息互相穿插，容易串线 ／ ✅话题：一项工作一个帖子，一目了然」（F-011）——**命中**。
7. P2 优势3 三子项「贴表情（不想费心措辞…）/ 轻提醒（发帖仅红点提示…回复只通知楼主）/ 长期收集（成员可以随时在话题中发帖）」（F-017–F-019）——**命中**。
8. P3 优势4「信息留存，新人快速跟上：话题支持成员自由邀请他人加入，能让更多志同道合的人加入你的小小『论坛』」（F-025）——**命中**。
9. P4 优势6「已读未读…阅读回执（帮你确认通知是否传达到位，还能提醒未读对象）/ 阅读状态（随时查看有多少人已读通知）」（F-032）——**命中**。
10. P5 三项能力「🔍搜索 / 💬消息转话题 / 🔗分享话题帖（通过链接、二维码等方式轻松传播话题）」（F-034–F-036）——**命中**。
11. 页脚「关于话题功能 你有什么想反馈吗？」+ 按钮「我想反馈」（F-005）——**命中**。
12. 8 组「群聊/✅话题」对照计数（P1×1 / P2×3 / P4×4，P3/P5 无）（F-037）——**命中**（快照逐页计数与 `00` 对照表逐行一致）。
13. 「使用场景：」框架行（F-003）与各页底部「更多场景」交叉链接区（F-006）——**命中**（本轮快照含框架行；`verification.md` 取证补记亦与之一致）。

## 独立复算结论（R3）

- **F 编号**：双份 47/47 相等、连续无跳号、表行 47；bundle 引用 F 编号全部在 F-001～F-047 内 —— **自洽**。
- **tencent 计数（R3 自写目录树脚本独立复算）**：束 **18** / 概念（非 index）**140** / 示例 **48** / 信源登记（references 非 index）**68** / 事实（逐束取内容与登记 `.md` 最大 F 编号求和、排除 `log.md`）**2879** —— **与 `tencent/index.md`「18 个知识包、140 概念、48 示例、68 信源登记、2879 条编号事实」逐项一致**。
- **上层计数**：total **641**、jishu **475**、ai **246**、ecosystems **94** —— 与 `doc/bundles/index.md`、`jishu/ai/index.md`、`jishu/index.md`、`ecosystems/index.md` 声明自洽（门禁 EXIT=0 佐证）。
- **链接自洽**：`check_doc_links` `links=57 broken=0`；R3 内联链接机械计数 = **62**（http 5 / 本地 57）。`verification.md` 门禁记录仍写 `58`/`63` —— **陈旧 1 条**（见 F-R3-A，advisory）。
- **索引完整性**：`wecom-5-0-12-release/index.md` 恰 +1 行 —— **成立**；`jishu/ai/index.md` 生态行 4 格且 `16` 保留 —— **成立**；`jishu/index.md` ai 行 `246` —— **成立**。

## Review History

### Review R3
- **Result**: `pass`
- **Reviewer**: fresh-context 第三轮独立对抗评审子代理（未参与实施、未参与 R1/R2 评审与修复；只读；仅写入本 `review.md`）
- **Checks Performed**:
  - `git -C projects/awesome-okf-xs status/diff/diffstat`（`jishu/index.md`、`jishu/ai/index.md`、`ecosystems/index.md`、`tencent/index.md`、`wecom-5-0-12-release/index.md`、`doc/bundles/index.md`）+ 全表列数机械校验
  - `python scripts\check-bundles-index.py`（EXIT=0）、`python scripts\check-toctrees.py`（EXIT=0）、`python scripts\check-utf8.py`（EXIT=0）
  - `python .agents/skills/submodule-atomization-finalize-cmd/scripts/check_doc_links.py <bundle>`（`checked_files=11 links=57 broken=0` EXIT=0）
  - 自写脚本：F 编号双份集合比对 + 引用范围扫描（out of range）、toctree 条目存活、逐文件内联链接计数（62/57）、bundle 目录树计数与十进事实数复算、frontmatter/sources 计数（9/8）
  - `rg` 全树扇出复扫（旧值 245/640/474/93/17/76/135/2832）+ 禁用串与隐私关键词扫描 + `.temp` 残留检索 + bundle 文件时间戳与 R2 时点比对
- **Evidence**:
  - R2 两条发现**全部关闭**：F-R2-1（`jishu/index.md` 245→246，`git diff` 单 hunk 单行语义变更 + R3 独立扇出复扫零遗漏）；F-R2-A（`tasks.md` L122「与基准束同构」措辞已删，9/8 与「不同构」判定与事实相符）。
  - R1 三条可行动发现（I-1/I-2/I-3）**未被破坏**（回归证据见 CP3-3）。
  - 全量 AC 重验：**AC-1 ~ AC-7 全部 pass**（门禁 EXIT=0、计数自洽、双向互链成立、逐字回源全命中、隐私零命中）。
  - bundle 自 R2 起**零变动**（时间戳取证）→ AC-5/AC-6 无需按新内容重评。
  - 无新可行动发现；仅 2 条 advisory（F-R3-A 门禁记录陈旧数、F-R3-B 摘要用词），不影响任何 AC 通过条件。
- **Blocked By**: 不适用（本轮无受阻检查点；源页登录墙不可重取，逐字比对以本轮下发完整快照为可复核证据路径，故不判 `blocked`）

### 分级发现清单（R3 Findings）

- **F-R3-A · 严重级别 P2 · advisory（时点记录未刷新，非门禁失败）**
  - 现象：`references/verification.md`「门禁运行记录」L117 记 `checked_files=11 links=58 broken=0`、L120 记「内联链接 63；本地引用 58」、L134 记「（58 链接、0 断链）」；而 R3 实测 = `links=57`、内联链接 **62**（http 5 + 本地 57），相差恰 1。
  - 复现方式：`python .agents/skills/submodule-atomization-finalize-cmd/scripts/check_doc_links.py <bundle>` → `links=57`；自写正则统计 bundle 11 文件 `[..](..)` 链接 = 62。差值来源明确：修复轮 **I-2** 删除了 `concepts/04` L32 的一处 Markdown 链接（R1 为 58/可能 63）。
  - 期望结果：把该记录注明为「Task 6 时点」或在 I-2 后回刷为 `57`/`62`（如 `links=57 broken=0`、`内联链接 62；本地引用 57`）。**不影响交付物正确性**：实质结论「0 断链」仍成立，AC-4 通过不受影响（类比 R1 F-4 / R2 F-R2-A 的证据措辞类 advisory）。
- **F-R3-B · 严重级别 P2 · advisory（摘要用词，非源页外断言）**
  - 现象：`facts.md` 与 `article-source.md` 的 `F-028`～`F-031`「声明摘要」含正文短语（如「每条通知独立展示，不会被后续消息冲走」「内容写错或安排有变，直接编辑原帖即可」），而本轮下发快照 P4 优势 2–5 仅给出**标题 + 群聊/话题对照行**，无逐字正文。
  - 复现方式：对照本轮快照 P4 段与 `article-source.md` L97–L100 / `facts.md` L72–L75。
  - 期望结果：属**要点式摘要**（`facts.md` 表头即「声明摘要」、`03` 表头为「页面原文要点」），非逐字引用、非源页外断言；如需进一步收敛，可在措辞上统一标注「（摘要）」或补一条取证补记（类比 I-3 的处理方式）。**不构成 AC-6/AC-7 缺陷**，无需强制修复。

### 四视角对抗结论（R3）

- **魔鬼代言人**：①「厂商自述被当事实」——仍不成立：全束以「页面原文/声明摘要」措辞、F-040 单源、F-039 零量化、8 组对照明标「厂商自证定性论证」，`verification.md` 明确「不升级为产品事实」，未见他处把话术写成产品事实。②「改一处、漏一处」——**本轮已基本收敛**：计数类漏改（R1 残格 → R2 旧计数）经 I-4 扇出复扫后，R3 独立复扫 `doc/bundles` **零遗漏**；残余仅 `verification.md` 门禁记录的**链接数陈旧 1 条**（F-R3-A），属时点记录未随 I-2 刷新，攻击面已从「事实/计数错误」降级为「自述记录未刷新」。
- **新人视角**：仅凭本束可清楚判断「话题能干什么」——5 场景 × 适用对象 × 优势条目 × 群聊对照齐备，页脚反馈入口与三项通用能力在册；需自行确认者已列明（开通条件/套餐/客户端门槛/入口路径/机器人来源与权限 F-044、功能名话题还是频道 F-045、API 文档目标页 F-038）。R1 的跨篇指认错误（F-2）已消除，`02` 不会再误导读者查找「分享话题帖」。
- **老板视角**：信息增量足以支撑「要不要评估/试用」、不足以支撑采购决策（零量化 F-039、零案例、无价格与准入 F-044）；产出对公开知识库是净正向，「单源 + 需登录 + 无日期」可信度上限已明示。知识库自身计数现已一致（含 `jishu/index.md`），无待清项。
- **未来视角**：`stale_after=2027-01-31` 到期时最可能漂移者：①5 分页 `?p=` 与页面存续（F-008/F-042）；②「话题 vs 频道」是否并轨（F-045）；③5.0.12 束 F-019 同形 smartpage 关系新证据（F-043）；④第三方独立信源/官方帮助中心条目（F-040）；⑤开通条件/套餐/客户端门槛补齐（F-044）。另建议到期复核时把**非门禁覆盖的自述记录**（`verification.md` 门禁记录、各束 `log.md` 计数基线）一并重取，避免 F-R3-A 类陈旧数累积。
- **追问结论（扇出复扫是否根治）**：「改索引漏一处」的两个具体实例（R1 `jishu/ai` 残格、R2 `jishu/index` 旧计数）**均已关闭**；**计数类旧值**的扇出复扫**已根治**（R3 独立全树复扫零遗漏，历史日志类 append-only 命中已正确豁免）。但 I-4 的扇出清单口径为「`doc/bundles/` 内计数数字」，**未覆盖「被修改文件自身审计记录中的派生数字」**（`verification.md` 门禁记录的链接数即此类），故该「派生数字扇出」子类是**部分未根治**——已以 F-R3-A advisory 登记，建议后续修复轮把「自身核验记录内的派生数字」纳入扇出复扫清单。

### 受限 / 未覆盖部分（R3，诚实声明）

- 源页对未登录访客为登录墙，R3 **未重新联网抓取**，逐字比对以本轮下发的**完整逐字快照**为准；若该快照与线上渲染态漂移，本报告未覆盖该差异。
- 未对 `wecom-5-0-10-release` 束做独立全文重读（`git` 状态未改动，双向互链仅要求 5.0.12 回补，未触发）。
- bundle 为子模块内未跟踪新目录，**无 git 提交基线**；「自 R2 起零变动」以文件秒级时间戳 + `check_doc_links` 链接数一致性作旁证（非内容哈希比对）。
- `check-mermaid.py` 对 `projects/` 子模块路径的「0 文件」假阴性沿用 R2 结论，未再构造临时副本复跑；Mermaid 结构正确性由 R3 人工核对 13 个节点挂 F 编号且全部落在 F-001～F-047 得出。

***

# 企业微信「话题」场景最佳示例页 → OKF Wiki 知识包 - Independent Review（R4）

> 评审性质：**fresh-context 第四轮独立复核（只读）**，本轮为**范围受限的确认性复核**——仅验证 R3 两条 advisory（F-R3-A / F-R3-B）的处置是否恰当、是否引入回归。R4 评审者未参与实施、未参与 R1/R2/R3 评审与修复轮；除本 `review.md` 外未修改任何文件，未执行 `git add` / `git commit`。
> 取证限定：源页 `page.weixin.qq.com` 对未登录访客为登录墙，R4 **未重新联网抓取**；逐字比对基准沿用 R3 下发的源页完整逐字快照。R4 仅对「bundle 磁盘状态 + 门禁复跑 + 机械计数」做可复核取证，不对 R1/R2/R3 已结论的逐字回源做重复审计。

## R4 检查点（范围受限的确认性复核）

- [x] CP4-1: 自 R3 以来 bundle **仅 2 个文件被改动**（`references/verification.md`、`log.md`），其余 9 个未动；仍为 11 文件、无 `examples/`、无增删文件
  - **Type**: `rule`
  - **Covers**: AC-1, AC-6
  - **Evidence**:
    - 文件时间戳（`Get-ChildItem -Recurse -File | Sort LastWriteTime`）：`references/verification.md` 与 `log.md` 均为 **2026-10-16 21:26:25**；其余 9 个文件为 **19:41:40～20:36:33**（最新 `04-general-capabilities-and-feedback.md` 20:36:33）。本 `review.md`（R3 写入时点）`LastWriteTime` = **21:21:33**。**即 9 个文件最后写入均早于 R3 的 review 写入时点**，R3 之后仅 `verification.md` 与 `log.md` 于 21:26:25 变动 → 改动范围**恰为该 2 文件**。
    - 与 R3 记录交叉佐证：R3 记「bundle 最新写入为 20:39:19（`log.md`）」而 R3 时为 `links=57`；当前 `check_doc_links` 仍为 `links=57`（见 CP4-4），链接数未变，与「除 append-only 两文件外内容零改动」一致。
    - `Get-ChildItem -Recurse -File` 清点 = **11 个 `.md`**；`examples` 目录 `Test-Path` = **False**；非 `.md` 文件 = **0**；`git status` 该束目录为 `?? …/wecom-topic-scenarios/`（未跟踪新目录），**无新增/删除文件**。
  - **结论**：**pass**（改动范围 = 2 文件，其余 9 个未动）。

- [x] CP4-2: F-R3-A 处置恰当——append-only 遵守、原 `links=58` 记录未改写、补记数字与实际复跑一致、补记未引入 Markdown 链接
  - **Type**: `rule`
  - **Covers**: AC-4, TR-6.1
  - **Evidence**:
    - **原记录未被改写（append-only 成立）**：`verification.md` **L117** = `checked_files=11 links=58 broken=0   EXIT=0`；**L120** = `找到 11 个 Markdown 文件；内联链接 63；本地引用 58；通过：所有本地引用均存在  EXIT=0`；**L134** 含 `（58 链接、0 断链）`——**行号与原文与 R3 Findings（F-R3-A）逐字一致**，证明原记录既未改字、亦未因上方插入而移位。
    - **新增补记**（L137–L139）：「`# 7) 链接门禁复跑补记（2026-10-16，Issue I-2 修复后）` / `复跑结果：checked_files=11 links=57 broken=0（EXIT=0）。` / `与原记录 links=58 的差 1 条…内联链接由 63 变为 62（http 5 + 本地 57）。核心结论「0 断链」不变。`」——位于「门禁运行记录」节**末尾**，为追加块。
    - **数字与实际复跑一致**：R4 实测 `check_doc_links` = `checked_files=11 links=57 broken=0`（CP4-4）；R4 机械计数 bundle 11 文件内联 `](` = **62**（其中 `](http` = **5**），故本地引用 = **57**。补记的 `57` / 内联 `62`（http 5 + 本地 57）与实际**逐项一致**。
    - **补记未引入 Markdown 链接**：`verification.md` 全文件内联 `](` 计数 = **0**（补记文本以纯文本书名引用，无 `[..](..)` 语法）→ `links` 应保持 **57**，与实跑一致。
  - **结论**：**pass**（append-only + 数字一致 + 无新链接）。

- [x] CP4-3: F-R3-B 独立判定——同意 R3 结论（要点式摘要、正常转写，非源页外断言）
  - **Type**: `rule`（advisory 类）
  - **Covers**: AC-6
  - **Evidence**:
    - **列风格一致性**：`facts.md` 与 `references/article-source.md` 表头均为 `| 编号 | 声明摘要 | 来源 | 核验状态 |`，列名即「**声明摘要**」；P1～P4 场景事实行（`F-010`～`F-032`）列风格统一为「`「优势标题」：要点说明；对照——群聊：… ／ ✅ 话题：…`」，`F-028`～`F-031` 与 `F-011`/`F-015`/`F-016`/`F-020`（R2/R3 已逐字复核命中者）**完全同型**。
    - **短语性质**：`F-028`～`F-031` 的「正文短语」为**优势标题的语义展开**——如 `F-031` 标题「随时修改，无需另发更正」→「内容写错或安排有变，直接编辑原帖即可，不必再发一条更正消息打扰大家」；`F-028` 标题「重要通知，不被聊天冲走」→「每条通知独立展示，不会被后续消息冲走」；`F-029` 标题「问答集中，不用重复解释」→「提问和回复都集中在通知下」；`F-030` 标题「信息留存，新人快速跟上」→「过往通知和问答完整保留」。**未新增标题与对照行未含之能力断言**；核验状态列与全表一致标 `⚠️ 仅官方单源`。
    - **判定**：属该列定义的**要点式摘要**（`article-source.md` 同列同口径；`concepts/03` 表头亦为「页面原文要点」），**非逐字引用、非源页外断言**，不构成 AC-6/AC-7 缺陷。
  - **结论**：**同意 R3 的 advisory 判定**（无需强制修改）。

- [x] CP4-4: 回归门禁四项 + 禁用串扫描（全部 EXIT=0 / 0 命中）
  - **Type**: `rule`
  - **Covers**: AC-4, AC-7, NFR-5
  - **Evidence**（原始输出）：
    - `python .agents\skills\submodule-atomization-finalize-cmd\scripts\check_doc_links.py <bundle>` → `checked_files=11 links=57 broken=0` **EXIT=0**
    - `python projects\awesome-okf-xs\scripts\check-utf8.py <bundle>` → `UTF-8 检查通过: 11 个文件均为有效 UTF-8。` **EXIT=0**
    - `python projects\awesome-okf-xs\scripts\check-bundles-index.py` → `bundles 总索引对账通过: 9 域 / 61 组 / 641 束，frontmatter、计数行、节标题、分组表、toctree 五面一致。` **EXIT=0**
    - `python projects\awesome-okf-xs\scripts\check-toctrees.py` → `toctree 检查通过: 全部 index.md 引用有效，所有内容文档均可达。` **EXIT=0**
    - 禁用串扫描（口径 = bundle 全目录 + spec `facts.md`，大小写不敏感）：`file://` / `C:\Users` / `.temp/` / `xsrf` / `tinyid` / `corp_id` / `access_token` → **No matches（0 命中）**（bundle 全目录与 `facts.md` 均为 0）。
  - **结论**：**pass**（无回归）。

- [x] CP4-5: AC 快速复核（AC-1/AC-2/AC-4/AC-7 机械项）+ AC-5/AC-6 无内容回归判断
  - **Type**: `rule` + `rubric`（无回归）
  - **Covers**: AC-1, AC-2, AC-4, AC-5, AC-6, AC-7
  - **Evidence**:
    - **AC-1** **pass**：11 文件；根 `index.md` toctree（`concepts/index`/`references/index`/`log`）、`concepts/index.md` toctree（`00`～`04` 5 条）、`references/index.md` toctree（`article-source`/`verification`）条目**逐一解析存在**；根 `index.md` frontmatter 含 `okf_version: "0.2"`/`type`/`title`/`description`/`tags`/`generated`/`verified`/`status: stable`/`stale_after: "2027-01-31"`/`sources`（W + W-P2…W-P5 共 5 条）。
    - **AC-2** **pass**（R4 自写正则独立提取）：`facts_uniq=47`、`article_uniq=47`、**集合相等=True**、`only_facts=[]`、`only_article=[]`、`min=F-001 / max=F-047`、**连续无跳号=True**；行级表行数 `facts=47`、`article=47`。
    - **AC-4** **pass**：`check_doc_links` `broken=0`（相对链接可达）；`git -C projects/awesome-okf-xs diff --stat -- …/wecom-5-0-12-release/index.md` = `1 file changed, 1 insertion(+)`，unified diff **仅新增 L59 一条回链行、0 删除**，其目标 `../wecom-topic-scenarios/index.md` 路径存在；5.0.10 束未改动（diffstat 未列）。
    - **AC-7** **pass**：禁用串/元数据关键词 **0 命中**；`.temp/smartpage` `Test-Path`=**False**；`raw.html`/`probe.txt`/`psd_pages.json`/`all_sections.txt` 全仓（排除 `.temp`）检索 = **0 命中**。
    - **AC-5 / AC-6 无内容回归判断**：依据——①承载源页内容的 **9 个文件时间戳全部早于 R3 的 review 写入时点（≤20:36:33 < 21:21:33），内容零改动**；②R3 之后唯一变动的两文件为 `verification.md`（末尾追加门禁复跑补记）与 `log.md`（追加「评审轮次」子节），**均为 append-only 元记录，未新增任何源页事实、未改动口径分层、未新增读者决策断言**；`log.md` 原 R1 修复段落行号未移位（`分享话题帖` 仍位于 **L53**，与 R2/R3 记录一致）佐证追加未穿插改写。故 AC-5（口径分层与读者决策可用性）与 AC-6（三层结构与来源忠实度）的 R3 结论（各 **5/5 pass**）**不受影响，无内容回归**。
  - **结论**：AC-1/2/4/7 **pass**；AC-5/AC-6 **无内容回归**（沿用 R3 pass）。

## Review History

### Review R4
- **Result**: `pass`
- **Reviewer**: fresh-context 第四轮独立复核子代理（未参与实施、未参与 R1/R2/R3 评审与修复；只读；仅写入本 `review.md`；未 `git add`/`git commit`）
- **Checks Performed**:
  - `Get-ChildItem -Recurse -File`（bundle 清点、时间戳排序）+ `Test-Path examples` + 非 `.md` 文件清点 + `git status`
  - `python .agents/skills/submodule-atomization-finalize-cmd/scripts/check_doc_links.py <bundle>`、`python projects/awesome-okf-xs/scripts/check-utf8.py <bundle>`、`python projects/awesome-okf-xs/scripts/check-bundles-index.py`、`python projects/awesome-okf-xs/scripts/check-toctrees.py`（均 EXIT=0）
  - 自写 Python 机械计数：F 编号双份集合比对 + 连续性 + 表行数；bundle 逐文件内联/`](http` 链接计数（62 / 5）；toctree 条目存活；frontmatter/sources 字段核对
  - `git -C projects/awesome-okf-xs diff --stat/–`（`wecom-5-0-12-release/index.md` = 1 insertion）
  - `rg`/`Select-String` 禁用串与隐私关键词扫描（bundle 全目录 + `facts.md`）+ `.temp` 残留与 `raw.html`/`probe.txt`/`psd_pages.json`/`all_sections.txt` 检索
  - 逐字读取 `facts.md`（F-028～F-031 与 P1/P2 同型行）+ `article-source.md`（F-028～F-031）+ `references/verification.md`（门禁记录节）+ `log.md`
- **Evidence**:
  - R3 两条 advisory **处置恰当**：**F-R3-A** —— `verification.md` 以 append-only 追加「门禁复跑补记」（`links=57 broken=0`），**原 `links=58` / 内联 63 / 本地 58 历史记录行号与原文逐字保留未改写**；补记 `57` / 内联 `62`（http 5 + 本地 57）与实际复跑**一致**，补记**未引入 Markdown 链接**（`verification.md` 内联 `](` = 0）。**F-R3-B** —— 抽查 `facts.md`/`article-source.md` 的 `F-028`～`F-031`「声明摘要」列，与同表 P1/P2 行**同型**，短语为优势标题的语义展开、未新增断言；**同意 R3 判定**（要点式摘要、非源页外断言、无强制修改项）。
  - **改动范围**：自 R3 起 bundle **仅 2 文件变动**（`verification.md`、`log.md`，均 21:26:25，晚于 R3 review 写入 21:21:33）；其余 9 个文件 ≤20:36:33 未动；仍 **11 文件、无 `examples/`、无增删文件**。
  - **回归门禁全绿**：四项门禁 `check_doc_links`（`links=57 broken=0`）、`check-utf8`、`check-bundles-index`、`check-toctrees` 全部 **EXIT=0**；禁用串（bundle + `facts.md`）**0 命中**。
  - **AC 复核**：AC-1/AC-2/AC-4/AC-7 **pass**；AC-5/AC-6 **无内容回归**（依据见 CP4-5）。
  - **未引入回归**：R1 三条可行动发现（I-1/I-2/I-3）所涉文件（`04`、`jishu/ai/index.md`）本轮未再变动；R2/R3 已闭合项（F-R2-1、F-R2-A）所涉文件（`jishu/index.md`、`tasks.md`）不在本轮 bundle 改动范围。无新可行动发现。
- **Blocked By**: 不适用（本轮为范围受限确认性复核，无受阻检查点；源页登录墙不可重取，逐字比对沿用 R3 下发快照，故不判 `blocked`）

## 四视角对抗结论（R4，聚焦回归）

- **魔鬼代言人**：本轮最可能的攻击面是「处置本身是否制造了新瑕疵」。核查结论：F-R3-A 的补记**未引入 Markdown 链接**（`links` 仍 57，实跑一致），F-R3-A **未改写**原始 `58` 记录（行号与原文与 R3 记录逐字一致）→ 既未制造新断链、也未篡改审计轨迹；F-R3-B **接受不修改**，同样不产生新断言。**未发现新攻击面**。
- **新人视角**：bundle 内容未变（9 文件时间戳早于 R3），读者可见知识面与 R3 一致；`verification.md` 末尾补记与 `log.md` 评审子节均为面向审阅者的元记录，不增加读者负担。
- **老板视角**：知识库自身整洁度维持——计数与链接数在门禁记录内已如实披露 `57`（并保留历史 `58`），无「以陈旧数冒充当前值」的误导。
- **未来视角**：R3 已登记的预防措施（「派生数字变更后扇出清单纳入被改文件自身的自述与门禁记录」）在本轮已**由 append-only 补记落地**；`verification.md` 门禁记录现已同时保留 58/63 历史值与 57/62 现行值，后续复核不再依赖单值时点。

## 受限 / 未覆盖部分（R4，诚实声明）

- 源页对未登录访客为登录墙，R4 **未重新联网抓取**，逐字比对沿用 R3 下发的完整逐字快照；R4 未对 F-028～F-031 做逐字快照比对（R3 已做并登记 advisory），仅从**列风格一致性 + 标题语义展开**作独立判定。
- bundle 为子模块内**未跟踪新目录，无 git 提交基线**；「自 R3 起仅 2 文件变动」以**秒级文件时间戳 + `check_doc_links` 链接数一致性**作旁证（非内容哈希比对），故未覆盖「两文件内部相对 R3 的逐字节 diff」（R3 未登记其字节数）。
- 未对 `wecom-5-0-10-release` 束做独立全文重读（`git` 状态未改动，未触发）。
- 未重跑 `check-mermaid.py`（沿用 R2/R3 对 `projects/` 路径假阴性结论；本轮 bundle Mermaid 内容未变动）。
