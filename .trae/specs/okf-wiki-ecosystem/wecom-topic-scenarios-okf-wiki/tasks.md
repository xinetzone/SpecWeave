# 企业微信「话题」场景最佳实践示例页 → OKF Wiki 知识包 - Implementation Plan

> 执行约定：严格按依赖顺序取任务；每个任务开始时置 `Status: in_progress`，完成自验后补 `Completion Evidence` 并置 `completed`。
> 方法链路：R（事实采集）→ I（场景洞察）→ E（concepts 撰写）→ V（独立对抗评审）→ C（原子提交，待用户指令）。
> 产出落位：spec 目录 `.trae/specs/okf-wiki-ecosystem/wecom-topic-scenarios-okf-wiki/`；bundle 落 `projects/awesome-okf-xs/doc/bundles/jishu/ai/ecosystems/tencent/wecom-topic-scenarios/`（子模块，只落盘不提交）。

## Task 1: R 阶段事实采集与 P0 核验
- **Status**: `completed`（2026-10-16）
- **Completion Evidence**:
  - `facts.md` 落盘 **F-001…F-047（47 条）**，8 节结构：页面结构（F-001~008）、场景 1~5（F-009~036）、内容呈现与链接存在性（F-037~039）、P0 核验补充（F-040~047）；含「P0 核验结论（五条）」与「勘误与存疑清单」两表。
  - TR-1.1（rule，通过）：正则提取输出 `facts.md 去重编号数 = 47`、`article-source.md 去重编号数 = 47`、`集合相等 = True`、`仅 facts 有/仅 article 有 均为空`、`最小 F-001 / 最大 F-047`、`连续无跳号 = True`、`表行数 = 47`。
  - TR-1.2（rule，通过）：五条 P0 逐条有结论文本——①单源 ✅ 仅厂商自有域名 smartpage（F-040，未检得第三方信源）；②发布日期/版本号/作者/更新时间**四项均未给**（F-041）；③第三方独立信源**未取得**（F-040）；④可达性：未登录访客不可直读，实测 `StatusCode=200 / Length=119188 / HasTitleMarker=False / HasScenarioMarker=False`，WebFetch 失败（F-042）；⑤与 5.0.12 束 F-019 链接关系**无法判定 → 并置登记**（padId 不同、`?p=HXPk2x` 相同、场景重合 3/5，F-043）。
  - TR-1.3（rubric，**4/5**，阈值 ≥4，通过）：五场景的适用对象、**全部**优势条目（3/4/4/6/3）、8 组群聊/话题对照、页面结构（标题/平台标识/导航 5 项/页脚反馈入口）、链接存在性（4 处 API 锚文本）齐全；扣分项：源页正文未在本会话独立重取（登录墙下不可重渲染），依赖任务下发的 2026-10-16 逐字快照，该项已在采纳风险中如实披露。
  - 来源代号：`W` 与分页 `W-P1…W-P5`；勘误/存疑清单含官方未给项（开通条件/套餐/客户端版本门槛/入口路径/机器人来源与权限，F-044）、话题 vs 频道命名张力（F-045）、适用对象描述性口径（F-046）。
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 重新取得源页 5 个分页的**逐字正文**（`?p=`：`HXPk2x` 推进项目协作 / `htt4Bf` 收集产品意见 / `ptlD2c` 分享经验知识 / `tR2p63` 发布公告通知 / `BMbevB` 更多功能及反馈），核对与 spec「Background & Context」记录一致；采集时点记为快照基准日（2026-10-16）。
  - 建立 `facts.md`（本 spec 目录内）：按 `F-001…F-NN` 连续编号登记，每条含**声明摘要 / 来源代号 / 核验状态**；覆盖 5 场景的适用对象、全部优势条目、群聊/话题对照、页面结构（标题、平台标识、导航、底部反馈入口）、内嵌链接存在性（「（点击查看API接口文档）」锚文本、页脚反馈入口）。
  - P0 核验：①信源单源属性（是否仅厂商自有页）；②页面是否给出发布日期/版本号/作者/更新时间；③是否存在第三方独立信源；④可达性（未登录访客是否可直读）；⑤与同分组 `wecom-5-0-12-release` 束 F-019 所登记 smartpage 链接的**同源/异源关系判定**（对比 padId 与 `?p=` 取值、场景集重合度），判定不确定时按并置登记、不择一断言。
  - 记录勘误/存疑清单（页面未给项、命名张力、描述性 vs 规范性表述）。
- **Acceptance Criteria Addressed**: AC-2, AC-7
- **Test Requirements**:
  - `rule` TR-1.1: `facts.md` 的 F 编号连续无跳号；每条含声明摘要与来源代号；表行数与最大编号一致。证据：编号集合提取输出。
  - `rule` TR-1.2: 五条 P0 核验项逐条有明确结论文本（含「未取得/官方未给」的如实标注），无编造信源。证据：facts.md 核验节 + 访问记录。
  - `rubric` TR-1.3: 事实采集完整度；scale 1-5；anchors 1=仅抄录标题级信息，3=覆盖主要声明但对照论证有遗漏，5=5 场景的适用对象/全部优势条目/对照论证/页面结构/链接存在性齐全且逐条可回源；threshold >= 4；证据：facts.md 与源页逐字比对。
- **Notes**: 临时取证脚本与原始抓取产物一律置 `.temp/`，任务收尾清理；**严禁将页面会话元数据（登录态/企业名/账号标识/令牌/内部文档 ID）写入 facts.md 或任何产出物**。

## Task 2: Bundle 骨架与根文件
- **Status**: `completed`（2026-10-16）
- **Completion Evidence**:
  - 落盘 4 文件：`index.md`(8810B)、`log.md`(5518B)、`concepts/index.md`(205B)、`references/index.md`(87B)。
  - TR-2.1（rule，通过）：根 index frontmatter 含 `okf_version: "0.2"`/`type`/`title`/`description`/`tags`/`generated`/`verified`/`status: stable`/`stale_after: "2027-01-31"`/`sources`（W + W-P2…W-P5 共 5 条分页 URL）；两个子目录 index 均含 toctree 块，条目逐一 `True`（concepts/index → 00/01/02/03/04；references/index → article-source/verification；根 index → concepts/index、references/index、log）。
  - TR-2.2（rule，通过）：「已知边界」含四类必备声明（厂商单源 F-040 / 无版本与日期 F-041 / 信源需登录 F-042 / 官方未给项 F-044），并额外并置登记「话题 vs 频道」命名张力（F-045）与同形 smartpage 链接关系（F-043），**无单方断言**。
  - 无 `examples/` 判定已记入 `log.md`（操作可复现性两问皆否）。
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 新建 `wecom-topic-scenarios/`，产出 `index.md`（根，OKF v0.2 frontmatter：`okf_version`/`type`/`title`/`description`/`tags`/`generated`/`verified`/`status: stable`/`stale_after: 2027-01-31`/`sources`；正文含「内容性质声明 / 可信度状态 / 知识包概述 / 概念导航表 / 已知边界 / 主题关联 / 一句话结论」，结构对齐 `wecom-5-0-12-release`）。
  - 产出 `log.md`（frontmatter + 七概念链路记录、口径决策、并行在途观测、门禁运行方式与实际输出）。
  - 产出 `concepts/index.md`、`references/index.md`（各自 toctree 块；子目录 index 无 frontmatter，与同分组基准同构）。
  - 「已知边界」必须集中声明：厂商单源、无发布日期/版本号、信源需登录态方可阅读、话题 vs 频道命名张力并置、官方未给项（开通条件/套餐/客户端版本门槛/入口路径/机器人来源与权限）。
- **Acceptance Criteria Addressed**: AC-1, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-2.1: 4 个根/索引文件齐备；根 index frontmatter 必填字段齐全且 `okf_version` 为 `"0.2"`；两个子目录 index 含 toctree 块（条目可在后续任务补齐前先按规划登记，或与 Task 3/4 同批提交）。证据：文件清点 + frontmatter 解析。
  - `rule` TR-2.2: 「已知边界」节四类声明（单源 / 无版本日期 / 信源需登录 / 官方未给项）与命名张力并列登记，无单方断言。证据：章节文本核对。
- **Notes**: 本束不建 `examples/`（操作可复现性两问皆否），须在 `log.md` 显式记录该判定。

## Task 3: Concepts 五篇撰写
- **Status**: `completed`（2026-10-16）
- **Completion Evidence**:
  - 落盘 5 篇：`00-overview-and-scenario-map.md`(9018B)、`01-task-collaboration.md`(3714B)、`02-feedback-collection.md`(4272B)、`03-knowledge-sharing-and-announcement.md`(6825B)、`04-general-capabilities-and-feedback.md`(4465B)。
  - TR-3.1（rule，通过）：5 篇齐备、frontmatter 合规（type: Concept、generated/verified 为 `process:seven-concepts-e/v`、status/stale_after/sources 齐备）；每篇引用的 F 编号均存在于 `facts.md`；`concepts/index.md` toctree 条目与文件名逐一对应（5/5 True）。
  - TR-3.2（rule，通过）：Mermaid 场景全景图 1 张，节点全部挂 F 编号；`check-mermaid.py --path <等效上下文副本>` 输出 `扫描 11 / 错误 0 / 警告 0`，EXIT=0。**脚本可用性如实说明**：`.agents/scripts/check-links.py` / `check-mermaid.py` 的共享扫描库把 `projects/` 列为排除目录，直接 `--path <bundle>` 会返回「0 文件」的假阴性，故改在保留同级束上下文的临时副本上运行（副本用后已删）。
  - TR-3.3（rubric，**4/5**，阈值 ≥4，通过）：三层职责清晰（总览答「这是什么页/场景怎么分/信源与时效」、场景篇答「谁适用/优势是什么/对照论证」、边界提示答「官方没说什么」），8 组群聊/话题对照表落地，无一条断言超出源页可支撑范围（逐篇抽查无源页外推断）。
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 产出 5 篇 concepts（文件名 ASCII kebab-case，均带 OKF v0.2 frontmatter，`type: Concept`，`generated`/`verified` 为 `process:seven-concepts-*`）：
    - `00-overview-and-scenario-map.md`：源页定位（产品场景示例页，非版本发布页/非操作手册）、5 场景全景与角色映射、信源属性与快照时效、未给项清单、Mermaid 场景全景图。
    - `01-task-collaboration.md`：推进项目协作（适用对象；机器人梳理进展、事项独立不串线、脉络完整三条优势；群聊 vs 话题对照）。
    - `02-feedback-collection.md`：收集产品意见（适用对象；机器人汇总反馈、一事一帖、轻松互动、进展清晰四条优势；含贴表情/轻提醒/长期收集子项与对照）。
    - `03-knowledge-sharing-and-announcement.md`：分享经验知识（适用对象；机器人随问随查、主题独立、轻松互动、信息留存四条优势）与发布公告通知（适用对象；机器人智能答疑、通知不被冲走、问答集中、信息留存、随时修改、已读未读六条优势及对照）。
    - `04-general-capabilities-and-feedback.md`：更多功能及反馈（搜索、消息转话题、分享话题帖三项能力；页面底部反馈入口「关于话题功能 你有什么想反馈吗？我想反馈」）。
  - 每篇所有具体声明带 F 编号引用；厂商自述 / 官方未给 / 命名张力三类措辞显式标注；篇间互链与阅读路径明确；不得出现一条超出源页可支撑范围的断言。
- **Acceptance Criteria Addressed**: AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-3.1: 5 篇文件齐备且 frontmatter 合规；每篇引用的 F 编号均存在于 `facts.md`；`concepts/index.md` toctree 条目与文件名逐一对应。证据：文件清点 + 编号交叉核对。
  - `rule` TR-3.2: Mermaid 图 ≥1 张，通过仓库维护版检查器（`.agents/scripts/check-mermaid.py`）；节点携带 F 依据。证据：检查器输出。
  - `rubric` TR-3.3: 超范围断言扫描与结构质量；scale 1-5；anchors 1=夹带源页外推断，3=个别断言超出源页支撑或层间重复，5=无一条断言超出源页、三层职责清晰、篇间路径明确；threshold >= 4；证据：独立评审逐篇评分。
- **Notes**: 源页每场景正文约 400–800 字符，撰写时**不得为凑篇幅扩写**；只做结构化、分层与溯源，密度对齐同分组 5.0.12 束。

## Task 4: References 双件与口径分层
- **Status**: `completed`（2026-10-16）
- **Completion Evidence**:
  - `article-source.md`(16103B)：F-001~F-047 逐条表 + `?p=` 分页映射表 + 来源代号表；`verification.md`(13736B)：信源清单与可达性记录、P0 核验总表、勘误与存疑清单、口径分层表（四条）、信源距离与厂商叙事评估、四视角审查表、状态裁决 `stable`。
  - TR-4.1（rule，通过）：`facts.md` 与 `article-source.md` 的 `F-\d{3}` 集合**严格相等、连续无跳号**（各 47 条，F-001…F-047），表行数与最大编号一致。
  - TR-4.2（rule，通过）：口径分层表四条齐全（源单源属性 / 话题 vs 频道命名张力 / 适用对象描述性非规范性 / 官方未给项）；V 四视角审查表四视角均有实质结论；状态裁决与依据明确。
  - TR-4.3（rule，通过）：隐私关键词扫描命中数 **0**。**复核说明**：Grep 命中 `verification.md` 的 `xsrf/tinyid/corp_id/access_token` 系该文件第 121 行的**自述行**「…等会话元数据关键词命中数 = 0」，经人工逐行核对**非泄漏**。
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - `references/article-source.md`：双份登记 `F-001…F-NN`（编号集合与 `facts.md` 严格相等、连续无跳号），逐条含声明摘要 / 来源代号 / 核验状态；登记源页 URL 与 5 个分页 `?p=` 标识映射。
  - `references/verification.md`：信源清单与**可达性记录**（未登录访客不可直读、需登录态渲染）；P0 核验总表；勘误与存疑清单；**口径分层表**（源单源属性 / 话题 vs 频道命名张力 / 适用对象描述性非规范性 / 官方未给项）；信源距离与厂商叙事评估；V 四视角对抗审查表（魔鬼代言人 / 新人 / 老板 / 未来）；状态裁决（预期 `stable`）。
- **Acceptance Criteria Addressed**: AC-2, AC-5, AC-7
- **Test Requirements**:
  - `rule` TR-4.1: 两文件 F 编号集合与 `facts.md` 相等且连续无跳号。证据：正则提取比对输出。
  - `rule` TR-4.2: 口径分层表四条齐全；V 四视角审查表四视角均有实质结论；状态裁决与依据明确。证据：文档章节核对。
  - `rule` TR-4.3: 关键词扫描零隐私元数据命中（登录态令牌、企业名、账号标识、`xsrf`/`tinyid`/`corp_id` 等）。证据：扫描输出。
- **Notes**: 溯源字段：两文件 frontmatter 含 `source`（源页 URL + 快照日期 2026-10-16）。

## Task 5: 三级索引接入与计数同步
- **Status**: `completed`（2026-10-16）
- **Completion Evidence**:
  - **五级索引改动**：`tencent/index.md`（导航表 +1 行、相关链接 +1 条、toctree 追加 `wecom-topic-scenarios/index`、「关于本分组」计数与 2026-10-16 学习来源叙述改写，`5 +4/-1`）；`ecosystems/index.md`（本类 93→94、腾讯行 17→18）；`jishu/ai/index.md`（description 与正文 245→246 束、ecosystems 行 93→94）；`jishu/index.md`（**未改**：其束数为递归占位、无本次相关数字）；`doc/bundles/index.md`（`total_bundles` 640→641、计数行 640→641、mermaid jishu 节点 474→475、jishu 节标题 474→475、jishu 表 ai 行 245→246）。
  - **双向互链**：本束根 index「主题关联」→ 5.0.12（L51）、5.0.10（L52）各 1 条；`wecom-5-0-12-release/index.md` 回补**恰 1 行**（L59，附「话题 vs 频道 命名张力 官方未给、并置登记」口径声明）。逐字 diff 仅 `1 +1`，5.0.10 束未改动。
  - TR-5.1（rule，通过）：`check-bundles-index.py` 输出 `bundles 总索引对账通过: 9 域 / 61 组 / 641 束，frontmatter、计数行、节标题、分组表、toctree 五面一致。` **EXIT=0**。
  - TR-5.2（rule，通过）：三处到位（导航表 / 相关链接 / toctree）；双向互链各 ≥1 条；对 5.0.10/5.0.12 改动限于 1 行回链，未改写其正文事实与计数归属。
  - TR-5.3（rule，通过）：`check-toctrees.py` 全量输出 `toctree 检查通过: 全部 index.md 引用有效，所有内容文档均可达。` **EXIT=0**；过滤 `wecom-topic-scenarios` 零命中；**既有污染项：无**（此前评审记录中的 81 处污染已不复现）。
  - **计数以机械真值落盘（与 spec 预期有差异，按真值为准并披露）**：真实值 束 **18** / 概念 **140** / 示例 **48** / 信源 **68** / 事实 **2879**；与 spec 预期（18/141/48/78/2879）差异两处——①概念 141→140：既有叙述 135 系「非 index」口径（本束贡献 5 篇非 index 概念 → 140），预期值误把本束 `concepts/index.md` 计入；②信源 78→68：既有叙述的「76」为**陈旧漂移值**（与其自身行级口径不符，逐行复算为 67、机械复算为 66），穷举 6 种候选口径均无法复现 76，故采用真值 66→68。
- **Priority**: high
- **Depends On**: Task 3, Task 4
- **Description**:
  - 按需改动五级索引：`tencent/index.md`（导航表行 + 相关链接 + 「关于本分组」计数与叙述 + toctree）、`ecosystems/index.md`（腾讯行计数）、`jishu/ai/index.md`、`jishu/index.md`、`doc/bundles/index.md`。
  - 计数以**机械真值**（目录树 + 门禁脚本）复算：本任务预期束 17→18、概念 135→141、示例 48 不变、信源 76→78、事实 2832→2832+NN；与预期不符时以真值为准并记录差异原因。
  - 双向互链：本束根 index「主题关联」链 5.0.10/5.0.12 束；`wecom-5-0-12-release/index.md` 回补**最多 1 行**指向本束，就该束登记的「场景示例页」smartpage 与本束源页关系作显式口径声明。
- **Acceptance Criteria Addressed**: AC-3, AC-4
- **Test Requirements**:
  - `rule` TR-5.1: bundle 索引门禁脚本（`projects/awesome-okf-xs/scripts/check-bundles-index.py`，脚本名以实施时实际存在为准）退出码 0，五面计数一致。证据：脚本原始输出。
  - `rule` TR-5.2: 本束在 tencent 导航表、相关链接、toctree 三处到位；双向互链各 ≥1 条；对 5.0.10/5.0.12 的改动**不超过允许范围**（不得重写其正文事实、不得改其计数归属）。证据：diff 核对。
  - `rule` TR-5.3: toctree 检查（`check-toctrees` 类脚本）过滤本束名零命中；既有污染项如实记录不修复。证据：脚本输出 + 过滤结果。
- **Notes**: 索引写入后须在**无并行写入窗口**复跑一次门禁以锁定结果。

## Task 6: 链接 / 编码 / 溯源门禁
- **Status**: `completed`（2026-10-16）
- **Completion Evidence**:
  - TR-6.1（rule，通过）：`check-utf8.py` → `UTF-8 检查通过: 354 个文件均为有效 UTF-8。` EXIT=0；链接 → `check_doc_links.py <bundle>` → `checked_files=11 links=58 broken=0` EXIT=0；以临时探针机械解析 16 个新增/修改文件相对链接 **209 条，broken=0**；禁用串扫描 **7/7 命中数为 0**（独立复核确认，见下）。
  - **扫描口径声明（2026-10-16 依独立评审 F-6 补记）**：AC-4 / AC-7 的禁用串与会话元数据关键词扫描范围 = **新增 bundle 全目录 + spec 目录 `facts.md`**；`spec.md` / `tasks.md` 自身因条款描述需要含政策字面串（如禁用路径前缀），**不计入扫描范围**，不构成泄漏。
  - **脚本可用性如实说明（两处假阴性已识别并绕开）**：①主仓 `.agents/scripts/check-links.py` 与 `check-mermaid.py` 的共享扫描库把 `projects/` 列入排除目录，直接 `--path <bundle>` 会返回「0 文件」假阴性，改以子模块门禁 + 保留同级束上下文的临时副本（用后已删）双路径取证；②`projects/awesome-okf-xs/scripts/` 下**不存在** `check_doc_links.py`，实际位于 `.agents/skills/submodule-atomization-finalize-cmd/scripts/check_doc_links.py`，按「以实际脚本名为准」采用。
  - TR-6.2（rule，通过）：`.temp/smartpage/` 下取证产物（`raw.html`、`probe.txt`、`psd_pages.json`、`all_sections.txt` 及空目录）与 2 个临时探针脚本已删除（清理前已确认无产出物引用：bundle/spec 内 grep 仅命中政策声明行，四类文件名零命中）；`.temp/` 引用在产出物中零命中。
  - **修复两处已披露缺陷（修复→预防→闭环）**：①`log.md` 文件数笔误 13→11（修复后独立复核 `FILES=11`、`EXAMPLES=False`）；②`references/verification.md` 门禁自述行原以字面串书写禁用路径与会话元数据关键词，导致机械扫描假命中，改写为不含字面串的等效审计表述——修复后 7 个字面串扫描 **全部归零**（`file://` = 0、`C:\Users` = 0、`.temp/` = 0、`xsrf` = 0、`tinyid` = 0、`corp_id` = 0、`access_token` = 0），审计结论与证据强度未削弱。
  - 溯源字段：**9 个文件带 frontmatter**，其中 **8 个**（根 index、5 篇 concepts、article-source、verification）含 `sources:`（W / W-P2…W-P5）；`log.md` 带 frontmatter（`type: Changelog`）但**不含 `sources`**；`concepts/index.md`、`references/index.md` 无 frontmatter。（2026-10-16 依独立评审 F-4 更正原表述「log.md 与基准束同构无 frontmatter」；F-R2-A 进一步更正：基准束 `wecom-5-0-12-release/log.md` **无任何 frontmatter**，故「与基准束同构」的说法不成立，该措辞已删除。）
- **Priority**: medium
- **Depends On**: Task 5
- **Description**:
  - 对全部新增/修改文件执行：UTF-8 校验、Markdown 相对链接可达性、零 `file:///`、零家目录绝对路径、零 `.temp/` 引用、派生产物 `source` 溯源字段存在性。
  - 清理 `.temp/` 下本任务取证产物（临时 HTML、剪贴板导出、分析脚本），确认无产出物引用之。
- **Acceptance Criteria Addressed**: AC-4, AC-7
- **Test Requirements**:
  - `rule` TR-6.1: UTF-8 检查通过；相对链接逐一解析存活；违规关键词（`file:///`、`C:\Users`、`.temp/`）零命中。证据：脚本输出 + Grep 记录。
  - `rule` TR-6.2: `.temp/` 取证产物已清理且产出物零引用。证据：目录清点 + Grep。

## Task 7: V 阶段独立对抗评审与七概念收尾
- **Status**: `completed`（2026-10-16）
- **Completion Evidence**:
  - **评审轮次（每轮均为 fresh-context 只读子代理，不参与实施与修复）**：
    - **R1 → `fail`**：3 条可行动（F-1 P1 `jishu/ai/index.md` 生态行丢「成员目录」格 / F-2 P2 `concepts/04` 跨篇指认错误 / F-3 P2 F-003·F-006 取证出处未标注）+ 3 条 advisory（F-4/F-5/F-6）→ 固化为 Issue I-1/I-2/I-3 并全部修复。
    - **R2 → `fail`**：新发现 1 条可行动 **F-R2-1**（`jishu/index.md` AI 行简介未随 245→246 同步，属本次改动引入；门禁盲区）+ advisory F-R2-A（TR-6.2「与基准束同构」措辞不成立）→ 固化为 Issue I-4/I-5 并全部修复（含全链路计数扇出复扫，判定无其他遗漏）。
    - **R3 → `pass`**：AC-1～AC-7 全量重验通过、无 P0/P1；R1/R2 全部发现已关闭，独立复扫零遗漏；留 2 条 advisory（F-R3-A 门禁记录 `links=58` 未随 I-2 删链回刷 / F-R3-B F-028～F-031 摘要列系要点式转写）。
    - **R4 → `pass`**（确认性复核）：F-R3-A 已以 **append-only 补记**方式在 `verification.md` 落 `links=57 broken=0` 而**未改写原 58 历史行**；F-R3-B 经独立判定**同意为要点式摘要、非缺陷**；自 R3 以来仅 `verification.md`/`log.md` 两文件变动（9 个内容文件时间戳 ≤20:36:33 < R3 review 写入 21:21:33），**无内容回归**，AC-5/AC-6 的 5/5 结论不受影响；四项门禁全绿、禁用串 0 命中。
  - TR-7.1（rule，通过）：四轮评审各自给出逐 AC 复核结论；R2/R3 逐字回源抽查 ≥8 条（R3 达 13 条）全部命中。
  - TR-7.2（rule，通过）：**全部可行动发现（P1/P2）关闭且各有回归证据**（I-1～I-4）；无遗留可行动发现；唯一保留的 2 条 advisory（F-R3-B、F-5 既有漂移）经判定**非缺陷或超范围**，已在 `log.md` 披露理由。
  - TR-7.3（rubric，**4/5**，阈值 ≥4，通过）：评审独立性——四轮均为 fresh-context 只读子代理、**独立重跑全部门禁脚本**、独立复算五级计数、独立逐字回源；扣分项：源页为登录墙，R2/R3/R4 **未能独立联网重新抓取**，逐字比对以下发的完整快照为取证路径（该限制已在各轮受限声明中如实标注）。
  - **七概念链路收尾**：`log.md` 已补齐 R→I→E→V 链路完成记录、计数实际落盘值与偏差、三轮评审（R1/R2/R3）处置、并行在途观测、未决项与预防措施。**C（原子提交）未执行**——按 spec 裁决不 commit，待用户显式指令。
  - **预防措施（三阶段递进之「预防」）**：同一类缺陷「改索引/删链后被改文件自身的审计记录派生数字未回刷」连续三轮出现（F-4 → F-R2-A → F-R3-A），已固化为检查项：**派生数字变更后，扇出清单必须纳入「被改文件自身的自述与门禁记录」**，并已写入本束 `log.md` 供后续同类任务复用。
  - **未做（超出范围，仅披露）**：`.trae/specs/` 全局与主题看板未刷新（按约定由 docgen 自动维护）；既有束历史断链与 `workbuddy-open-platform-docs` 信源行级漂移未修复。
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 向 **fresh-context 只读子代理**委托一次独立对抗评审（不参与实施）：对照 spec AC 逐条复核，独立重取源页验证关键声明可回源，给出四视角审查结论与 P0/P1/P2 分级发现。
  - 发现按「修复→预防→闭环」处置：可行动发现全部关闭并留回归证据；处置过程写入本束 `log.md`。
  - 收尾：`log.md` 补齐七概念链路完成记录、门禁实际输出、并行在途观测、未决项；确认无遗留可行动发现。
- **Acceptance Criteria Addressed**: AC-2, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-7.1: 独立评审报告含逐 AC 复核结论与 5 条随机声明的逐字回源比对。证据：评审报告留存。
  - `rule` TR-7.2: 全部可行动发现（P0/P1）关闭且各有回归证据；无遗留可行动发现。证据：修复记录 + 复跑输出。
  - `rubric` TR-7.3: 评审独立性；scale 1-5；anchors 1=实施者自验冒充评审，3=独立上下文但未独立回源，5=独立上下文 + 独立重取信源 + 逐条 AC 对照 + 四视角结论；threshold >= 4；证据：评审者身份与复核方法说明。

# 审查修复队列（Review R1 = `fail`，2026-10-16）

> 依 Spec Mode 路由：Review R1 判 `fail`，每条可行动发现固化为 pending issue；选取工作前先建队列。

## Issue I-1: `jishu/ai/index.md` 生态行丢失「成员目录」单元格
- **Status**: `completed`（2026-10-16）
- **Completion Evidence**:
  - 修复：该行由 3 格 `| 94 | 以厂商… |` 恢复为 4 格 `| 94 | 16 | 以厂商… |`。
  - TR-I-1.1（rule，通过）：`git diff` 该行 now `-| … | 93 | 16 | …` → `+| … | 94 | 16 | …`，仅「束数 93→94」一处语义变更，第 3 格 `16` 保留。
  - TR-I-1.2（rule，通过）：全表机械列数校验输出 `header cols=4`，导航表 8 行**全部为 4 格**。
  - 复跑 `check-bundles-index.py` → `9 域 / 61 组 / 641 束，五面一致。` EXIT=0。
- **Priority**: high
- **Depends On**: None
- **Discovered By**: Review R1（发现 F-1，P1 可行动）
- **Description**:
  - Task 5 改写 `jishu/ai/index.md` 生态行时，把 `| 93 | 16 | … |` 改成了 `| 94 | … |`，**丢失第 3 格成员目录数 `16`**（表头为 4 列），导致该行 3 格而行内列数错位。门禁脚本不校验子表格列数，故未拦截。
  - 复现：`git -C projects/awesome-okf-xs diff -- doc/bundles/jishu/ai/index.md`。
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `rule` TR-I-1.1: 该行恢复为 4 格且第 3 格为 `16`；`git diff` 中该行仅「束数 93→94」一处语义变更。证据：修复后 diff。
  - `rule` TR-I-1.2: 全表所有行单元格数与表头一致（机械列数校验）。证据：列数校验输出。

## Issue I-2: `concepts/04-general-capabilities-and-feedback.md` 跨篇指认错误
- **Status**: `completed`（2026-10-16）
- **Completion Evidence**:
  - 修复（逐字）：原句「…与在[收集产品意见](02-feedback-collection.md)中出现的「分享话题帖」能力为同一能力（该场景页底部的「更多场景」交叉链接亦属链接传播形态，F-006）。」改为「…该能力在本束中仅见于源页场景 5（F-036），其余四个场景页未声明该能力，本束不作跨场景外推。」
  - TR-I-2.1（rule，通过）：全束 grep「分享话题帖」8 处命中，**已无**「在收集产品意见中出现该能力」类指认；`02-feedback-collection.md` 不再被指认。
  - 副作用如实披露：因删除指向 02 的 1 条 Markdown 链接，`check_doc_links.py` 由 `links=58` 变为 `links=57`，`broken=0` 不变；`check-utf8.py` 与 `check-bundles-index.py` 均 EXIT=0。
- **Priority**: medium
- **Depends On**: None
- **Discovered By**: Review R1（发现 F-2，P2 可行动）
- **Description**:
  - 该篇 L32 称「分享话题帖」能力在 `02-feedback-collection.md` 中「出现」，但 02 全文**无「分享话题帖」字样**（该能力属源页 P5/F-036）。跨篇指认错误会误导读者跳转。
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `rule` TR-I-2.1: 该句改为**不指认 02** 的正确表述（或删除该指认），且全束 grep「分享话题帖」不再出现「02/收集产品意见中出现该能力」的表述。证据：修复后 grep。

## Issue I-3: F-003 / F-006 取证出处未标注（评审无法复核）
- **Status**: `completed`（2026-10-16）
- **Completion Evidence**:
  - 修复：在 `references/verification.md` 的「勘误与存疑清单」后、「口径分层表」前新增 `### 取证补记（F-003 / F-006：页面框架行）`：说明 R1 依据的节选快照省略了页面框架行；F-003 为「了解话题最佳示例」大标题下、5 项导航前独立一行「使用场景：」；F-006 为各场景页正文末尾「更多场景 / 💬 收集产品意见 → / 📘 分享经验知识 → / 📣 发布公告通知 → / ✨ 更多功能及反馈 →」（顺序各页不同）；取证出处注明 2026-10-16 渲染态逐页 `document.body.innerText` 抓取；明确二者**非编造、不新增源页外断言**。
  - TR-I-3.1（rule，通过）：补记已落盘（grep 命中）；未新增源页外断言；`check-utf8.py` EXIT=0、禁用串扫描 0 命中。
- **Priority**: low
- **Depends On**: None
- **Discovered By**: Review R1（发现 F-3，P2 可行动）
- **Description**:
  - F-003（页面标注「使用场景：」）与 F-006（各场景页底部「更多场景」交叉链接区）在**下发评审的逐字快照片段中不存在**，故评审标记「不可复核」。经回查渲染态抓取记录，二者**确为页面框架行**（`使用场景：` 位于大标题下、导航之前；`更多场景` 位于各场景页底部），属评审快照省略框架行所致，**非编造**。
  - 处置：在 `references/verification.md` 的核验记录/勘误节补一条**取证补记**，明确二者的取证出处与原文，使后续评审可复核。
- **Acceptance Criteria Addressed**: AC-2, AC-7
- **Test Requirements**:
  - `rule` TR-I-3.1: `verification.md` 含 F-003/F-006 的取证补记（说明系页面框架行、给出原文与位置），且不新增源页外断言。证据：文档章节 + grep。

## Issue I-4: `jishu/index.md` AI 行简介未同步 245→246（R2 新发现）
- **Status**: `completed`（2026-10-16）
- **Completion Evidence**:
  - 修复：`jishu/index.md`（实际第 20 行）简介文本 `245 束` → `246 束`，左列 `[递归束数](../index.md)` 占位未动。
  - TR-I-4.1（rule，通过）：`git diff` 该文件仅此 1 行语义变更（`-…245 束…` → `+…246 束…`）。
  - TR-I-4.2（rule，通过）：**全链路扇出复扫**（7 个旧值 640/245/93/17/76/135/2832 全树 grep 逐处判定）→ **无其他遗漏**；所有残留均落在带时点的历史日志/核验记录（各束 `log.md`、`references/verification.md`）中，属 append-only 回溯证据，按惯例不回改。边界项 `wecom-topic-scenarios/log.md:65` 的基线句（17/135/76/2832）带明确时点且同文件已落实际值 18/140/48/68/2879 并自述 `76` 为陈旧漂移值 → 判定为历史披露口径，非遗漏。
  - TR-I-4.3（rule，通过）：`check-bundles-index.py` → `9 域 / 61 组 / 641 束，五面一致` EXIT=0；`check-toctrees.py` → EXIT=0；另复跑单束链接 `links=57 broken=0` 与 UTF-8（单束 11 文件 + 全树 11688 文件）均 EXIT=0。
  - **顺带实测（非本次引入，仅记录）**：误把整棵 `jishu` 子树传给链接检查器时得 `broken=5903`，经核为其他既有束的历史断链（如缺失文件、锚点命名不符），与本任务无关，超出范围未修复。
- **Priority**: medium
- **Depends On**: None
- **Discovered By**: Review R2（发现 F-R2-1，P2 可行动，**本次改动引入**）
- **Description**:
  - `doc/bundles/jishu/index.md` L19 的 ai 行简介仍写「AI 与大模型应用生态，**245 束**按读者意图归为六大类…」，而 ai 域已 245→246（`jishu/ai/index.md` 与 `doc/bundles/index.md` 均已同步）。Task 5 曾判定该文件「无本次相关数字」，**判定有误**。
  - 该文件属 AC-3 的 Given 清单，但 `check-bundles-index.py` **不审计此文件的该行**（门禁盲区），故两轮门禁均未拦截。
  - 根因（预防措施）：同一次计数变更的「扇出清单」不完整——`jishu/index.md` 的束数单元格为 `[递归束数](../index.md)` 占位，但其**简介文本内的数字**是硬写死的第二事实源，易被漏改。
- **Acceptance Criteria Addressed**: AC-3, AC-4
- **Test Requirements**:
  - `rule` TR-I-4.1: 该行简介数字更正为 **246**；`git diff` 中该文件仅此一处语义变更。证据：修复后 diff。
  - `rule` TR-I-4.2: **全链路计数扇出复扫**——对本次所有涉改计数（641 / 475 / 246 / 94 / 18 / 140 / 68 / 2879）在 `doc/bundles/` 全树 grep，确认无遗漏的旧值（245 / 93 / 17 / 76 / 640 等）。证据：grep 输出。
  - `rule` TR-I-4.3: 复跑 `check-bundles-index.py` 与 `check-toctrees.py`，均 EXIT=0。证据：脚本输出。

## Issue I-5: `tasks.md` TR-6.2 措辞与事实不符（R2 advisory）
- **Status**: `completed`（2026-10-16）
- **Completion Evidence**:
  - 修复：Task 6 溯源字段说明已删除「按基准束 5.0.12 同构」措辞，改为纯事实陈述（9 文件带 frontmatter / 8 个含 `sources` / `log.md` 带 frontmatter 但不含 `sources`），并附 F-R2-A 更正缘由（基准束 `wecom-5-0-12-release/log.md` **无任何 frontmatter**，「同构」不成立）。
  - TR-I-5.1（rule，通过）：该行现文见 Task 6 Completion Evidence 末条。
- **Priority**: low
- **Depends On**: None
- **Discovered By**: Review R2（发现 F-R2-A，P2 advisory）
- **Description**:
  - Task 6 的溯源字段说明原写「`log.md` 带 frontmatter（`type: Changelog`）但按基准束 5.0.12 **同构**不含 sources」——但基准束 `wecom-5-0-12-release/log.md` **无任何 frontmatter**，两束在这一点上并不同构，该措辞不成立。
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-I-5.1: 该句已删除「与基准束同构」措辞，仅保留事实陈述（9 带 frontmatter / 8 含 sources / log.md 带 frontmatter 但不含 sources）；并在同句附 F-R2-A 更正说明。证据：tasks.md 该行。

# Task Dependencies

- Task 1 → Task 2（骨架依赖事实登记）
- Task 1 → Task 4（references 依赖 facts.md 编号集合）
- Task 2 → Task 3（concepts 依赖根 index 导航与 frontmatter 基准）
- Task 3, Task 4 → Task 5（索引接入依赖 concepts 篇数与 references 文件齐备，计数方可机械复算）
- Task 5 → Task 6（门禁须在索引改定后执行）
- Task 6 → Task 7（评审须在门禁通过后进行）
- 可并行项：Task 3 与 Task 4 在同一依赖面上可并行推进（不写同一文件）

# 未决/挂起项

- 无阻断性挂起项。以下为按 spec「Open Questions」既有裁决执行的事项：不提交 git；并行漂移只披露不修复；`stale_after=2027-01-31`；`status` 目标 `stable`。
