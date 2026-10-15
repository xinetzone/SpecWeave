# 微信公众号「美因」逆龄基因药博文转 OKF Wiki — Implementation Plan

> 执行链路：`R → I → E → V → C`。产出位于子模块 `projects/awesome-okf-xs/doc/bundles/sheke/personal-growth/wechat-anti-aging-er100-nmn/`，spec 位于主仓库 `.trae/specs/okf-wiki-ecosystem/wechat-anti-aging-er100-nmn-okf-wiki/`。

## Task 1: 图文卡片视觉识读与事实补全
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Completion Evidence**:
  - TR-1.1 `rule` ✅：14 张图（imgIndex=0~13）逐张识读，无遗漏，每张给出图片 URL、画面描述、可读文字与确定性标注；证据为 browser_use 子代理第 2 轮完整回传清单。
  - TR-1.2 `rule` ✅：图片仅在线识读，未下载落盘，工作区无新增图片路径；证据为识读方式（browser_take_screenshot 视口截图 + 视觉识读，未保存文件）。
  - TR-1.3 `rubric` 得分 4/5：每张图给出可读文字与「确定/部分确定」标注，正文未覆盖事实显式单列「仅图片单源」清单 9 项；扣分项为图 8/图 10 表格细节因分辨率不足部分标注「[不清晰]」，未升级为独立核验。证据为识读清单 + 与正文交叉比对。
  - **识读关键产出（正文未覆盖的独有事实）**：① Nature 新闻截图原始题录「09 June 2026 / World-first: therapy to make cells young again trialled in a person / By Heidi Ledford」；② Sinclair 抗衰方案清单四条（少吃一点：常跳过早餐、每天 14–16 小时空腹 / 规律运动：每周至少 3 次练到喘不上气 / 补足维生素 D、多吃深色蔬果：蓝莓、无糖抹茶、特级初榨橄榄油、坚果 / 睡够觉、经营稳定关系）；③ NMN 里程碑图称「衰老速度降低到自然状态的 60% 以下」「2013 年论文逆转所有分子层面衰老表现」「2016 年《Nature》子刊评论 Restoring stem cells — all you need is NAD+ 标注为[8]」；④ 检测报告图为「纯度 ≥ 99%」（与正文「99.99% 以上」**口径不一致，须核验勘误**）；⑤ 价格图「公域 999 元 / 读者专属 649 元」。
  - **待 T3 核验的图片侧疑点**：图 4 把 2016 年 Nature 子刊评论编号为 [8]，而正文参考文献 [8] 为《中华老年医学杂志》2026 中华医学会共识——**源文引用编号错位**；图 4 数字口径（60% 以下 / 逆转所有分子层面衰老表现）与正文口径不同源。
- **Description**:
  - 用 browser_use 子代理打开 `https://mp.weixin.qq.com/s/J86wj_jTrBpXBiuzf_82JQ`，定位正文 14 张图片，逐张识读其承载的事实（重点：「Sinclair 抗衰方案清单」条目、文献/共识截图上的可读文字、机构与人物相关图文）。
  - 将识读结论整理为「图片序号 → 可读事实 → 与正文文字是否重复」清单，供 T2 登记。
  - 图片本身不入库；任何临时下载/截图文件在任务结束前删除。
- **Acceptance Criteria Addressed**: AC-2, AC-11
- **Test Requirements**:
  - `rule` TR-1.1: 14 张图片逐张有识读结论记录（或显式标注「无法识读」及原因），清单条目数 = 14；证据为清单文件或任务内记录。
  - `rule` TR-1.2: 工作区内零残留临时图片文件（`git status` 无新增图片路径）；证据为 `git status` 输出。
  - `rubric` TR-1.3: 识读准确度；scale 1-5；锚点 1 = 依赖猜测、把营销图当事实；3 = 主要图片识别但部分条目含糊未标注不确定；5 = 每张图给出可读文字与「确定性/不确定」标注，正文文字未覆盖的条目显式标为「仅图片单源」；threshold >= 4；证据为识读清单 + 与正文交叉比对。

## Task 2: R 阶段事实采集与 F 编号登记
- **Status**: `completed`
- **Priority**: high
- **Depends On**: T1
- **Completion Evidence**:
  - TR-2.1 `rule` ✅：17 个主题全覆盖（事件 6 / 数字 3 / 机制 8 / 反转述 2 / 时间线 1 / 成本 3 / 旁证 2 / NAD+ 3 / 溯源 2 / 共识 4 / 文献 10 / 厂商 4 / 厂商供应 1 / 厂商产品参数 5 / 商业 4 / 源文瑕疵 4 / 图片独有事实 12）；证据为 `facts.md` 主题覆盖统计。
  - TR-2.2 `rule` ✅：F-001 ~ F-074 连续无跳号（脚本校验 74 行、0 跳号、每行恰 5 个半角 `|`）；证据为比对脚本输出。
    - **后续变更注记（R2-7）**：本节为 R 阶段的历史快照；后续经 Issue I-2（追加 F-075~F-089）与 Issue I-8（追加 F-090）扩充为 **F-001 ~ F-090（90 条）**，两侧登记表仍保持集合相等且连续。当前有效值以 `facts.md` 与 `references/article-source.md` 为准。
  - TR-2.3 `rubric` 得分 4/5：每条声明归入「页面事实 / 作者或信源观点 / 厂商自述 / 未核验（待 P0）/ 编辑瑕疵」五类之一并标注 P0/P1/P2；图片独有事实 12 条单列（F-063~074），与正文重复者并入 `W+I` 行未重复编号；扣分项为部分图片细节标注「部分确定」尚待核验升级。
  - 产出：`facts.md`（74 条，`status: draft`）。
- **Depends On**: T1
- **Description**:
  - 依据 `spec.md`「候选事实清单」与 T1 识读结论，从 F-001 起连续编号，登记 spec `facts.md`（表头：编号 / 声明 / 来源 / 状态与限制）。
  - 落实「信源距离预判」：厂商自宣类声明逐条标注「厂商自述」；作者观点与信源转述显式标注，不得混入事实层。
  - 同步登记产出到 bundle 侧占位（正式落盘见 T5）。
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-2.1: `facts.md` 覆盖 `spec.md` 候选清单全部主题（事件/数字/机制/反转述/时间线/成本/旁证/NAD+/溯源/共识/文献/厂商/商业/源文瑕疵），无遗漏主题；证据为主题覆盖比对表。
  - `rule` TR-2.2: F 编号连续无跳号；证据为正则 `^\|\s*F-(\d{3})` 提取结果。
  - `rubric` TR-2.3: 事实粒度与分层质量；scale 1-5；锚点 1 = 把作者观点与厂商话术写成客观事实；3 = 多数条目分层正确但个别观点未标注；5 = 每条声明可归入「页面事实 / 作者或信源观点 / 厂商自述 / 未核验」四类之一且标注完整；threshold >= 4；证据为 `facts.md` 分层标注抽样。

## Task 3: P0 权威核验与勘误四张清单
- **Status**: `completed`
- **Priority**: high
- **Depends On**: T2
- **Completion Evidence**:
  - TR-3.1 `rule` ✅：P0 核验 41 条，覆盖率 100%，零空缺（✅ 15 / ⚠️ 16 / ❌ 2 / single-source 6 / single-source/flagged 2）；P1/P2 抽样核验 6 条已注明抽样范围。
  - TR-3.2 `rule` ✅：勘误四张清单逐类成表——① 日期/版本表 7 项 ② 成效数字溯源表 7 项 ③ 口径对照表 8 项 ④ 引文逐字核对表 5 项；另出正式勘误 13 条（勘-01 ~ 勘-13）。
  - TR-3.3 `rule` ✅：40 条权威信源（全文唯一 URL 41 条含博文）均标注为实际检索所得（含 lifebiosciences.com 四篇公告、nature.com d41586-026-01836-7、PMC10166133 / PMC7442590 / PMC8979162 / PMC7063679 / PMC12294471、stdaily.com、pubmed 28068222 等），报告顶部含「零假核验声明」。
  - TR-3.4 `rubric` 得分 4/5：每项区分「独立权威 / 单源 / 未证实」，成效数字找到原始出处或明确记「无独立出处」，口径限定词逐项对照（物种/组织/读数类型三重限定被识别）；扣分项为部分单源项（如 999 元定价、基因港供应哈佛）只是标 `single-source` 未进一步穷尽渠道。
  - **关键结论**：① 源文硬错——「3 月第一位患者注射」权威实为 **2026-06-09**；② 主推成效数字失实——「剩余寿命近乎翻倍」判 ❌（权威 NMN 小鼠中位寿命 +8.5%／OSK 全身重编程约 +7%）；「恶性肿瘤细胞失去失控增殖特征、部分凋亡」判 ❌（未检索到）；③「8 周/75%」为小鼠表观遗传时钟读数、多组织 50–95%，源文丢失物种/组织/读数三重限定；④ **《NAD+……中国专家共识（2026 版）》真实存在**（科技日报 2026-05-08 等多家独立报道，题录 中华老年医学杂志 2026, 45(4): 497-508），非 flagged 触发项；⑤ `status` 建议 **`flagged`**（两项主推成效数字失实，符合 FR-8 与 SKILL 反模式 #13）。
  - 产出：`verification.md`（169 行，含核验表、勘误、四张清单、权威信源清单、关键缺口）。
- **Depends On**: T2
- **Description**:
  - 对全部 P0 声明检索独立权威来源：Life Biosciences 官方公告、FDA / ClinicalTrials.gov、中华医学会与《中华老年医学杂志》官方/DOI、PubMed/DOI、基因港官网、公开人物履历信源。
  - 逐项过**勘误四张清单**：① 日期/版本表（FDA 批准、首次注射、数据公布时点、2013 年溯源年份）② 成效数字溯源表（8 周/75%、寿命翻倍、纯度 99.99%、NAD+ 半衰口径）③ 口径对照表（「细胞生物年龄」「剩余寿命」「连续多年供应」的限定词缺失与拔高）④ 引文逐字核对表（Sinclair 反问、共识表述、王骏履历）。
  - 生成 `references/verification.md`（或先在 spec 侧成型），含 ✅/⚠️/❌ 统计与「勘误」小节；查无实据的项标 `single-source/flagged`，禁止硬编 URL 假核验。
  - 依核验结果定档 `status`（见 spec FR-8）。
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-8
- **Test Requirements**:
  - `rule` TR-3.1: 全部 P0 项有核验状态（✅/⚠️/❌）与来源字段，空缺数 = 0；证据为核验表完整性检查。
  - `rule` TR-3.2: 勘误四张清单逐类有成表结论，零「未过筛」项；证据为四张清单文本。
  - `rule` TR-3.3: 每个权威 URL 均经检索确认可达且内容支持该声明，零凭记忆编造 URL；证据为检索记录与 URL 可达性检查。
  - `rubric` TR-3.4: 核验严谨度；scale 1-5；锚点 1 = 单一信源自证或直接采信源文；3 = 多数项有独立来源但个别口径未对齐限定词；5 = 每项区分「独立权威 / 单源 / 未证实」，成效数字找到原始出处或明确记「无独立出处」，口径限定词逐项对照；threshold >= 4；证据为核验表 + 勘误小节的独立复核。

## Task 4: I 阶段骨架确认与归属落位复核
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: T3
- **Completion Evidence**:
  - TR-4.1 `rule` ✅：目标 bundle 目录不存在 `examples/`（Glob `sheke/personal-growth/*` 扫描无该目录；T5 产出 12 个 md 文件亦无 examples/）。
  - TR-4.2 `rule` ✅：落位 `sheke/personal-growth/wechat-anti-aging-er100-nmn/`，未新建任何分组目录；同分组已含 4 个同类微信博文转化束（`naval-learn-build-link`、`wechat-presence-joy-meditation`、`wechat-public-expression-lift`、`wechat-certainty-fogg-prompt`），形态一致。
  - TR-4.3 `rule` ✅：篇目与 `spec.md` 知识地图一致（`00-er100-first-in-human` / `01-aging-information-theory` / `02-nad-nmn-pathway` / `03-cost-and-access-timeline` / `04-supplement-claims-and-reading-discipline`），依 T3 核验结果无需新增/合并篇目。
- **Depends On**: T3
- **Acceptance Criteria Addressed**: AC-11
- **Test Requirements**:
  - `rule` TR-4.1: 目标 bundle 目录不存在 `examples/`；证据为目录清单。
  - `rule` TR-4.2: bundle 落位于 `sheke/personal-growth/` 且未新增任何分组目录；证据为 `git status --short` 与目录树。
  - `rule` TR-4.3: `concepts/` 篇目与 `spec.md` 知识地图一致（或差异有显式理由记录）；证据为篇目对照表。

## Task 5: E 阶段信源先行生成 bundle
- **Status**: `completed`
- **Priority**: high
- **Depends On**: T4
- **Completion Evidence**:
  - TR-5.1 `rule` ✅：12 个文件全部落盘（`index.md`、`knowledge-map.md`、`log.md`、`concepts/index.md` + 5 篇 concepts、`references/index.md` + `article-source.md` + `verification.md`）；证据为 `Glob **/*.md` 返回 12 条。
  - TR-5.2 `rule` ✅：三级 index 均含 `{toctree}`；3 个 index 共 11 条条目（排除 `:` 指令行）逐一 `Test-Path` 命中；根 index 收录 `concepts/index`、`knowledge-map`、`references/index`、`log`。
  - TR-5.3 `rule` ✅：全部非保留 `.md` 含合法 frontmatter 且 `type` 非空（`Concept`/`Reference`/`bundle`）；根 index `sources` 含博文 URL + 8 条核验权威 URL 双信源。
  - TR-5.4 `rule` ✅：Grep `专属价|领取|点击上方|立即购买|专属通道` 全 bundle命中 **0**；价格仅以客观陈述出现并标注「源文自述价格」；证据为 Grep 输出。
  - TR-5.5 `rubric` 得分 4/5：三类边界（已知 / 厂商自述 / 未知）通篇可辨识；根 index 顶部含 flagged + 厂商自述提示块与「内容边界」五段；`concepts/04` 提供可迁移的带货漏斗识别与保健品内容阅读纪律（三段式可信度衰减、真中掺假手法）；扣分项为部分单源声明仅列入清单、未逐条给出追索路径。
  - **核验结论已在正文落实为正确值**：时间线改 2026-06-09（勘-01）、75% 补物种/组织/读数三重限定（勘-02）、寿命翻倍替换为 +8.5%／+7%（勘-03）、纯度以检测图 ≥99% 呈现（勘-04）、文献 [4][6] 作者序列修正（勘-08/09）、共识题录补全 45(4):497-508（勘-13）。
  - **链接归一化（返工修正）**：初版正文内链使用 `/concepts/…` 前缀式绝对路径，与仓库既有束的相对路径惯例不符且会让链接门禁 `Test-Path` 失败；已改写 5 个文件共 15 处内链为普通相对路径，复测 `]\(/` 命中 0、42 条相对链接全部可达、敏感路径命中 0、文件数仍 12。
  - 产出：`projects/awesome-okf-xs/doc/bundles/sheke/personal-growth/wechat-anti-aging-er100-nmn/`（12 文件，`status: flagged`，`stale_after: 2027-06-30`）。
- **Depends On**: T4
- **Description**:
  - **信源先行**顺序：先写 `references/article-source.md`（F 编号双份登记之一）与 `references/verification.md` → 再写 5 篇 `concepts/`（00 事件层 / 01 衰老信息论 / 02 NAD+-NMN 通路 / 03 成本与可及性 / 04 厂商声明与阅读纪律）与 `knowledge-map.md` → 再写 `references/index.md`、`concepts/index.md` → **最后写** bundle 根 `index.md` 与 `log.md`。
  - 根 `index.md` 含：`okf_version: "0.2"`、厂商自述数据提示块、阅读路径、内容边界（含 999→649 带货披露、非医疗声明、status/stale_after 依据）、隐藏 toctree（`concepts/index`、`knowledge-map`、`references/index`、`log`）。
  - 全部具体声明引用 F 编号；伪代码/推断显著标注「非官方」；`stale_after: 2027-06-30`。
  - 正文遵守「不复制带货话术、不提供购买入口、不发医学建议」。
- **Acceptance Criteria Addressed**: AC-2, AC-5, AC-6, AC-7, AC-10
- **Test Requirements**:
  - `rule` TR-5.1: 产物文件清单完整（index + knowledge-map + concepts/index + 5 concepts + references/index + article-source + verification + log），数量 = 12；证据为 `Test-Path` 逐项输出。
  - `rule` TR-5.2: 三级 index 均含 `{toctree}` 块，条目逐一对应真实文件；证据为 toctree 提取 + `Test-Path`。
  - `rule` TR-5.3: 全部非保留 `.md` 含合法 YAML frontmatter 且 `type` 非空；根 index 含 `sources` 双信源（博文 URL + 核验权威 URL）；证据为 frontmatter 抽样清单。
  - `rule` TR-5.4: 全 bundle 检索「999」「649」「专属价」「领取」「购买」等带货引导词，仅允许出现在**披露性陈述**语境（如实记录价格与披露手柄事实），零引导性文案；证据为 Grep 结果与人工语境判定。
  - `rubric` TR-5.5: 读者可用性；scale 1-5；锚点 1 = 事实与话术混杂；3 = 分层可见但个别未核验数字未标注距离；5 = 三类边界（已知/厂商自述/未知）通篇可辨识，且含可迁移的保健品内容阅读纪律；threshold >= 4；证据为独立审查者通读评估。

## Task 6: V 阶段对抗审查与机械门禁
- **Status**: `completed`
- **Priority**: high
- **Depends On**: T5
- **Completion Evidence**:
  - TR-6.1 `rule` ✅：`facts.md` 与 `references/article-source.md` F 编号集合相等；（R1 时各 74 条，I-2 修复后各 89 条，仍相等且连续）。
  - TR-6.2 `rule` ✅：14 个文件（12 bundle + spec facts/verification）strict UTF-8 解码 0 失败；`file:///`、`C:\Users\`、`/Users/` 命中 0；42 条相对内链 0 断链。
  - TR-6.3 `rule` ✅：`log.md` 已补齐 8 项手动等效验证清单（I-3 修复），并实际运行仓库三个官方脚本：`check-utf8.py`（11597 个文件均有效 UTF-8）、`check-toctrees.py`（全部引用有效、所有内容文档可达）、`check-bundles-index.py`（9 域 / 61 组 / 636 束，五面一致）；`log.md` 明确注明走手动等效路径，**未谎报 gates 通过**。
  - TR-6.4 `rubric` 得分 5/5：由**全新上下文**的独立审查者执行 Review R1，产出可行动发现清单与逐条证据，未把实施者自验当最终结论；证据为 `review.md` 的 Review History。
  - **Review R1 结果 `fail`**：1 条可行动发现（F1：「45 条权威 URL」计数虚高，属数量陈述失真）+ 7 条建议性发现（F2~F8）。检查点判定：CP-R1/R2/R3/R4/R5/R6/R7/R8/R9/R10 全 `pass`；CP-U1 `pass`（5/5）；CP-U2 `pass`（4/5）。
  - **失败已固化为 pending 修复队列**：按规则创建 Issue I-1 ~ I-6 六项（见「审查发现修复队列」章节），并在选取工作前落库；另记录 F7 为**既有问题、不在本次范围**。
- **Depends On**: T5
- **Description**:
  - **四视角审查**内容文档：① 事实溯源（无 F 之外的数字/机构名，勘误在正文落实）② 结构规范（OKF v0.2 符合性）③ 读者可用性（相对链接逐一可达）④ 时效边界（单源/价格时点/观点分层）。
  - **机械门禁**：优先 `invoke gates.utf8` / `invoke gates.toctrees`（需 `pip install -e ".[doc]"`）；依赖不可用时执行**手动等效验证清单**（UTF-8 strict roundtrip / 双份 F 编号比对 / 三级 toctree 可达 / 相对链接全可达 / `file:///` 零出现 / 敏感路径零残留 / frontmatter 齐备 / 勘误落实），并在 `log.md` 注明走的是手动路径。
  - **禁止谎报**：未跑 gates 且未做等效验证时，不得声称「gates 通过」。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-9, AC-12
- **Test Requirements**:
  - `rule` TR-6.1: `facts.md` 与 `references/article-source.md` 的 F 编号集合相等（正则双提取比对）；证据为比对输出。
  - `rule` TR-6.2: 全部新增/修改 `.md` 经 strict UTF-8 解码成功；Grep `file:///`、`/Users/`、`C:\Users\` 命中数 = 0；证据为解码脚本输出 + Grep 结果。
  - `rule` TR-6.3: 手动等效验证清单 8 项逐项有结论记录（或 `invoke gates.*` 实际输出），`log.md` 注明实际路径；证据为 `log.md` 门禁小节。
  - `rubric` TR-6.4: 审查独立性；scale 1-5；锚点 1 = 复述实施者自述或只看文件存在性；3 = 有独立通读但抽样不足；5 = 由全新上下文独立复核，给出可行动发现清单与逐条证据，且未把自验当最终结论；threshold >= 4；证据为 review.md 的 Review History。

## Task 7: 三级索引接入与全库计数同步
- **Status**: `completed`
- **Priority**: high
- **Depends On**: T5
- **Completion Evidence**:
  - TR-7.1 `rule` ✅：三处计数一致——`bundles/index.md` frontmatter `total_bundles: 636` = 正文 prose「当前共 **636 个知识包**」= 各域束数之和；`sheke/index.md` 域节标题「68 束」= 该域 8 个分组**实际**束数之和（8+9+3+2+5+15+25+1=68）；`personal-growth/index.md` `total_bundles: 15` = 该组 toctree 15 条。**注（R2-9）**：`sheke/index.md` 的 Industry 分组行**显示**值为「22 束」，与 `bundles/index.md` 该组实际 25 束存在**既有漂移**（`git diff` 证明该行本次未改动），故该文件分组行显示之和为 65 ≠ 域节标题 68；本束自身计数（personal-growth 15 束）不受影响。
  - TR-7.2 `rule` ✅：`personal-growth` 组隐藏 toctree 条目数（排除 `:` 指令行）= 15 = 该目录实际 bundle 子目录数 = 导航表行数；逐条 `Test-Path <bundle>/index.md` 全部成立。
  - TR-7.3 `rule` ✅：`bundles/index.md` 五面对账一致——frontmatter `total_bundles` 636 / 正文 prose 计数 636 / sheke 域节标题 68 束 / 分组表个人成长行 15 / mermaid 节点「（68 束）」；全文已无 `635` / `67 束` / `（14 束）` 残留。
  - **改动清单（4 文件）**：① `personal-growth/index.md`（`total_bundles` 14→15、导航表加行、toctree 加条目、阅读路径加行）② `sheke/index.md`（分组行束数 14→15、行尾「（14 束）」→「（15 束）」、正文分组说明补入本束描述）③ `bundles/index.md`（`total_bundles` 635→636、prose 635→636、mermaid sheke 67→68、域节标题 67 束→68 束、分组表个人成长行 14→15）④ bundle `log.md` 追加索引接入记录。
  - **既有异常（未擅自扩大改动范围，已记录）**：`sheke/index.md` 个人成长行的行内存在一个游离 `| 14 |` 单元格，与该表其余行的两列结构不符，属**索引既有格式瑕疵**；本次仅将该数字同步为 15 以保行内自洽，未重构该行结构。
  - **门禁**：`invocations` 未安装，未调用 `invoke gates.*`；已改用手动等效验证（三处计数对账 + toctree 逐条可达 + 目录计数），**未声称 gates 通过**；证据为上述实测。
- **Depends On**: T5
- **Description**:
  - `sheke/personal-growth/index.md`：导航表加行（束名 + 文档数 + 一句话简介）+ 隐藏 toctree 追加 `wechat-anti-aging-er100-nmn/index` + `total_bundles` 14 → 15 + 阅读路径行。
  - `sheke/index.md`：分组说明补入本束描述 + 束数 67 → 68（含该分组行计数）。
  - `bundles/index.md`：`total_bundles` 635 → 636、`groups: 61` 不变、`domains: 9` 不变，并同步正文 prose 计数（「当前共 635 个知识包…9 个技术域、61 个分组」）。
  - **先读现值再改**，不凭记忆写数字；跑 `invoke gates.bundles` 或 `scripts/check-bundles-index.py` 对账。
- **Acceptance Criteria Addressed**: AC-8, AC-7
- **Test Requirements**:
  - `rule` TR-7.1: 三处计数一致（frontmatter `total_bundles` / 人类导航表束数列 / 机器 toctree 条目数）；证据为计数对账脚本输出。
  - `rule` TR-7.2: `personal-growth` 组 toctree 条目数 = 实际 bundle 目录数 = 15；证据为 `Test-Path` 逐条 + 目录计数。
  - `rule` TR-7.3: 总索引计数行、域节标题数字、分组表束数列、toctree 五面一致；证据为 `check-bundles-index.py` 输出。

## Task 8: C 阶段双层原子提交
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: T6, T7
- **Completion Evidence**:
  - TR-8.1 `rule` ✅：三笔提交，信息均符合 `type(scope): 中文描述`——① 子模块 `ee201d31`「docs(okf-wiki): 新增美因逆龄基因药博文 OKF 知识包并接入三级索引」（15 files changed, 1078 insertions, 9 deletions）② 主仓库 `85da9a9c8`「docs(spec): 新增 wechat-anti-aging-er100-nmn-okf-wiki 规格与事实核验产物」（5 files changed, 1231 insertions）③ 主仓库 `0daa3fb9a`「chore(submodule): 更新 awesome-okf-xs 指针至知识包提交」（1 file changed）。
  - TR-8.2 `rule` ✅：使用 `.agents/scripts/git-commit-utf8.py`（UTF-8 bytes 通道）并**逐个显式列出全部文件**，脚本回显「指定文件: 15 个」「指定文件: 5 个」「指定文件: 1 个」，与暂存区一致，零遗漏/零多余。
  - TR-8.3 `rule` ✅：主仓库子模块指针已更新——提交后 `git status --short -- projects/awesome-okf-xs` 显示 `?`（仅剩**他会话**遗留的未跟踪目录 `doc/bundles/jishu/ai/ecosystems/tencent/workbuddy-open-platform-sharing-and-promotion/`，非本 spec 产物，已按「不回滚无关变更」原则**未触碰**）。
  - TR-8.4 `rule` ✅：**未执行 push**——三笔提交均为本地提交。
  - **提交范围隔离**：主仓库存在大量**并行会话的无关变更**（`.agents/`、`apps/`、其他 `.trae/specs/` 目录等），本次仅提交本 spec 目录（5 文件）与 `projects/awesome-okf-xs` 指针，未使用 `git add -A`；`projects/daoapps.github.io` 的同批未跟踪状态亦未触碰。
- **Depends On**: T6, T7
- **Description**:
  - 提交顺序：① 在子模块 `projects/awesome-okf-xs` 内提交（bundle 全部文件 + `personal-growth/index.md` + `sheke/index.md` + `bundles/index.md`）→ ② 主仓库提交 spec（`.trae/specs/okf-wiki-ecosystem/wechat-anti-aging-er100-nmn-okf-wiki/`）→ ③ 主仓库更新子模块指针。
  - 使用 `python .agents\scripts\git-commit-utf8.py -m "docs(okf-wiki): ..." <显式文件1> <显式文件2> ...`——**必须逐个列出全部 .md 文件，禁止传目录参数**。
  - 遵循 Conventional Commits，主体用中文；用户未要求时不 push。
- **Acceptance Criteria Addressed**: AC-1, AC-8
- **Test Requirements**:
  - `rule` TR-8.1: 子模块与主仓库各有一次提交，提交信息符合 `type(scope): 中文描述`；证据为两处 `git log -1 --stat` 输出。
  - `rule` TR-8.2: 暂存区文件列表与显式指定列表一致，零遗漏/零多余；证据为 `git-commit-utf8.py` 的执行输出。
  - `rule` TR-8.3: 主仓库子模块指针已更新至子模块新 HEAD；证据为 `git diff --submodule` 或 `git status` 输出。
  - `rule` TR-8.4: 未执行 push；证据为 `git status` 显示 ahead 状态。

# 审查发现修复队列（Review R2 → Implement）

> Review R2 结果 `fail`，产生 4 条可行动发现（R2-1 ~ R2-4）与 5 条建议性发现（R2-5 ~ R2-9）。I-1/I-3/I-4/I-5/I-6 经 R2 独立复测确认达标；I-2 为首轮未彻底闭环项（漏登 勘-06、登记表图例与导语口径不一致）。

## Issue I-7: 域索引事实计数未同步（R2-1）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-I-7.1 `rule` ✅：`sheke/index.md` 第 18 行（域说明段）与第 32 行（分组导航表 personal-growth 行）的「74 条事实双份登记」已改为「89 条事实双份登记」；该文件 Grep `74 条` 命中 **0**；仅改计数，toctree / `total_bundles` / Industry 行均未动。
- **Priority**: high
- **Depends On**: None
- **Discovered By**: Review R2（Finding R2-1，可行动）
- **Description**:
  - `doc/bundles/sheke/index.md` 第 18 行（域说明段）与第 32 行（域内分组导航表 personal-growth 行）仍写「**74 条事实双份登记**」，与 `personal-growth/index.md:31`、bundle `index.md`/`knowledge-map.md`/`verification.md` 的「89 条」冲突。
  - 同步为「**89 条事实双份登记**」（只改这两个计数，不动其他文字、不动 toctree、不动 `total_bundles`）。
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `rule` TR-I-7.1: bundle 12 文件 + spec 4 文件 + `personal-growth/index.md` + `sheke/index.md` 中 Grep `74 条` 命中数为 0（合法例外：`article-source.md` 的 F-074 表行、`tasks.md` 的历史证据与 Issue 描述文本）；证据为 Grep 结果。

## Issue I-8: 补登 勘-06 的更正值 F 编号（R2-2）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-I-8.1 `rule` ✅：两侧登记表中出现的勘误编号集合均覆盖 **勘-01 ~ 勘-13 全部 13 个**（R2 时缺 勘-06，已由 F-090 补齐）；映射 13/13。
  - TR-I-8.2 `rule` ✅：spec `facts.md` 与 bundle `references/article-source.md` 各 **90 条**，集合相等、连续 **F-001 ~ F-090** 无跳号；两侧 F-075~F-090 逐字一致（16 行，文本级相同）。
  - F-090 登记内容：勘-06 更正值——图 imgIndex=4 称 2013 年论文「逆转了所有分子层面衰老表现、让老年小鼠线粒体功能恢复到幼年小鼠水平」属拔高；权威口径（Gomes et al., Cell 2013, 155:1624-1638）核心为「NAD+ 下降致假性缺氧状态、损伤核-线粒体通讯」，应降级为「恢复线粒体功能」。
- **Priority**: medium
- **Depends On**: None
- **Discovered By**: Review R2（Finding R2-2，可行动）
- **Description**:
  - `verification.md` 勘误表列 13 条（勘-01~勘-13），但两侧登记表只出现 12 个勘误编号——**勘-06 未被登记为任何新 F 编号行**，导致 TR-I-2.2「勘-01~勘-13 一一对应」不成立。
  - 勘-06：图 04「2013 年论文……逆转了**所有分子层面衰老表现**，让老年小鼠线粒体功能恢复到幼年小鼠水平」→ 权威口径（Gomes 2013）核心为「NAD+ 下降致假性缺氧状态、损伤核-线粒体通讯」，该表述为拔高，应降级为「恢复线粒体功能」。
  - 在两侧登记表**追加 F-090**（保持编号连续、与 F-075~F-089 同格式），登记该更正。
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-I-8.1: 勘-01~勘-13 每条都能在两侧登记表中找到对应新 F 编号行（映射 13/13）；证据为勘误↔F 映射表。
  - `rule` TR-I-8.2: 两侧编号集合相等且连续至 F-090；证据为正则提取比对。

## Issue I-9: 登记表图例与导语口径修正（R2-3）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-I-9.1 `rule` ✅：`article-source.md` 来源图例已补 `核验` 条目（定义为「核验阶段产生的更正值与衍生值，非博文原文事实」），表内实际取值集合 `{核验, I, W, W+I}` 四项与图例**全覆盖**；标题与 H1 改为「事实登记清单（F-001 ~ F-090）：博文原文事实 + 核验更正登记」；导语新增显式声明「F-001 ~ F-074 为博文原文事实；F-075 起为核验阶段追加的更正登记与衍生值，非源文事实」；过宽表述已区分为「F-001 ~ F-074 保留 R 阶段原始标记，F-075 起为核验阶段标记」。
- **Priority**: medium
- **Depends On**: None
- **Discovered By**: Review R2（Finding R2-3，可行动）
- **Description**:
  - bundle `references/article-source.md` 存在分类污染风险：① 「来源」列的取值 `核验` 未在来源图例中定义；② 文档标题「博文事实清单（F-001 ~ F-089）」与导语把 F-075+ 涵盖在「博文事实」内；③ 导语称「状态与限制列保留 R 阶段原始标记」，但新增行状态列为「核验勘误（Review R1）…」，与之矛盾。
  - 修正：① 来源图例补定义 `核验`（＝核验阶段产生的更正值与衍生值，非博文原文事实）；② 导语显式声明「**F-001 ~ F-074 为博文原文事实；F-075 ~ F-090 为核验阶段追加的更正登记与衍生值，非源文事实**」；③ 把「保留 R 阶段原始标记」的过宽表述改为「F-001 ~ F-074 保留 R 阶段原始标记；F-075 起为核验阶段标记」。
- **Acceptance Criteria Adressed**: AC-2
- **Test Requirements**:
  - `rule` TR-I-9.1: 图例覆盖表内全部「来源」取值（W / I / W+I / 核验）；导语明确区分 F-001~F-074 与 F-075+ 的性质；证据为文件摘录。

## Issue I-10: 正文悬空勘误编号引用修正（R2-4）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-I-10.1 `rule` ✅：bundle 内 Grep `勘误⑤` 命中 **0**；正文引用的勘误清单编号集合 ⊆ {②,③,④}。具体修正：`concepts/03-cost-and-access-timeline.md:52`「（勘误⑤③口径对照表）」→「（勘误③口径对照表）」；`concepts/04-supplement-claims-and-reading-discipline.md:39`「（勘误⑤）」→「（勘误④）」（王骏港中大履历修正属④引文逐字核对表）。
- **Priority**: low
- **Depends On**: None
- **Discovered By**: Review R2（Finding R2-4，可行动）
- **Description**:
  - `verification.md` 只有 4 张勘误清单（①日期/版本 ②成效数字溯源 ③口径对照 ④引文逐字核对），但正文出现**不存在的「勘误⑤」**：`concepts/03-cost-and-access-timeline.md:52`（「勘误⑤③口径对照表」）与 `concepts/04-supplement-claims-and-reading-discipline.md:39`（「勘误⑤」）。
  - 修正为实存编号——王骏港中大履历修正属**勘误④引文逐字核对表**；成本项属 ③ 或 ②，按语境就近更正。
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-I-10.1: bundle 内 Grep `勘误⑤` 命中数为 0；正文引用的勘误清单编号集合 ⊆ {①,②,③,④}；证据为 Grep 结果。

## 建议性发现处理（不阻塞验收）
- **R2-5**（concepts 未引用任何 F-075~F-090）：在 `concepts/00` 与 `concepts/04` 各补一处指向「核验更正登记（F-075~F-090）」的指针，打通引用链。
- **R2-6**（`concepts/01` 与 `concepts/00` 以 F-011 标注 OSK 全称 Oct4/Sox2/Klf4，而全称登记值为 F-088）：在这两处引用中一并补上 F-088。
- **R2-7**（`tasks.md` Task 2 完成证据仍写 F-001~F-074 / 74 条）：在 T2 完成证据补注「R1 修复后经 I-2/I-8 扩充至 F-001 ~ F-090（90 条）」，保留历史快照含义。
- **R2-8**（`review.md` 的 Review History 为 Pending）：由主控改写 `review.md`，回填 R1/R2 审查历史与检查点判定。
- **R2-9**（`sheke/index.md` Industry 行「22 束」vs `bundles/index.md` 该组「25 束」的既有漂移；致域内分组行显示之和 65 ≠ 域节标题 68）：**既有问题、不在本次范围**，仅记录；另修正 `tasks.md` TR-7.1 的表述，注明该行显示值与实际束数存在既有漂移。

# 第二轮修复队列依赖

- I-7 / I-9 / I-10 互相独立，可并行
- I-8 与 I-9 都改 `article-source.md` 与 `facts.md`，须**串行**（先 I-9 改导语/图例，再 I-8 追加 F-090；或反之，不得并发）
- 全部修复完成后，以**新的独立审查者**开启 Review R3

# 审查发现修复队列（Review R3 → Implement）

> Review R3 结果 `fail`，产生 1 条可行动发现（A1）与 3 条建议性发现（B1~B3）。CP-R1~CP-R7、CP-R9、CP-R10 全 `pass`；CP-U1 `pass`（5/5）；CP-U2 `pass`（4/5）；**CP-R8 `fail`**（映射 A1）。
> **根因洞察（同类问题第三次复发）**：R1-F1（45→40）、R2-R2-1（74→89）、R3-A1（89→90）三轮都是「**上游数字变更后，下游计数陈述未全库同步**」。这说明修复动作缺少「变更后全域重扫」的收尾步骤——每次只改被点名的位置，未做范围外延扫描。本轮修复必须以**全域断言**收尾，而非只改点名处。

## Issue I-11: 事实计数全域同步至 90 条 / F-001 ~ F-090（A1）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-I-11.1 `rule` ✅：8 处已改——① `bundle/index.md` description「90 条事实（含 16 条核验更正与衍生值）」② `bundle/knowledge-map.md`「90 条 F 编号事实登记在」③ `bundle/references/index.md`「F-001 ~ F-090 逐条事实登记」④ `bundle/references/verification.md` 登记扩充行「扩充至 F-001 ~ F-090（新增 16 条…）」⑤ `bundle/log.md`「F-001 ~ F-090 共 90 条」「（各 90 条）」「追加 F-075 ~ F-090 共 16 条」⑥⑦ `sheke/index.md:18/:32`「90 条事实双份登记」⑧ `personal-growth/index.md:31`「90 条事实双份登记」。
    - **全域断言实测**：bundle 12 文件 Grep `89 条|F-001 ~ F-089|各 89 条|15 条核验更正` = **0**；`sheke/index.md` = **0**；`personal-growth/index.md` 命中 2 处但均为 **how-to-live-better（另一束，真值为 89）**，合法例外不属本包口径 → **本包口径命中 = 0**。
  - TR-I-11.2 `rule` ✅：两侧登记表各 **90 条**，`Compare-Object` 集合差 = 0（相等），F-001~F-090 连续差 = 0，F-075~F-090 两侧逐字一致 16 条。
  - TR-I-11.3 `rule` ✅：三脚本重跑退出码均 0——`check-utf8.py`「11597 个文件均为有效 UTF-8」；`check-toctrees.py`「全部 index.md 引用有效，所有内容文档均可达」；`check-bundles-index.py`「9 域 / 61 组 / 636 束，五面一致」。
  - **收尾复核**：bundle 仍 12 个 md、相对链接断链 0、`]\(/` 0、`file:///` 0。
- **Priority**: high
- **Depends On**: None
- **Discovered By**: Review R3（Finding A1，可行动）
- **Description**:
  - Issue I-8 追加 F-090 后，两侧登记表已为 **90 条（F-001 ~ F-090）**，但下游 **8 处**仍写 89 条 / F-001 ~ F-089 / 15 条：
    1. bundle `index.md` description：「逐条登记 89 条事实（含 15 条核验更正与衍生值）并核验」
    2. bundle `knowledge-map.md`：「89 条 F 编号事实登记在…」
    3. bundle `references/index.md`：「F-001 ~ F-089 逐条事实登记」
    4. bundle `references/verification.md` 的登记扩充说明行：「已从 F-001 ~ F-074 扩充至 F-001 ~ F-089（新增 15 条…）」
    5. bundle `log.md`：「F-001 ~ F-089 共 89 条…（各 89 条）…追加 F-075 ~ F-089 共 15 条」
    6~7. `bundles/sheke/index.md` 两处：「89 条事实双份登记」
    8. `bundles/sheke/personal-growth/index.md`：本束行「89 条事实双份登记」
  - 全部改为 **90 条 / F-001 ~ F-090 / 16 条核验更正与衍生值**。
- **Acceptance Criteria Addressed**: AC-1, AC-8
- **Test Requirements**:
  - `rule` TR-I-11.1: 交付物全域（bundle 12 文件 + `sheke/index.md` + `personal-growth/index.md`）Grep `89 条|F-001 ~ F-089|F-001~F-089|各 89 条|15 条核验` 命中数为 0（合法例外：`article-source.md`/`facts.md` 的 F-089 表行本身）；证据为 Grep 结果。
  - `rule` TR-I-11.2: 两侧登记表仍各 90 条、集合相等、连续 F-001 ~ F-090；证据为正则提取比对。
  - `rule` TR-I-11.3: 重跑 `check-utf8.py` / `check-toctrees.py` / `check-bundles-index.py` 三条均通过；证据为脚本输出。

## Issue I-12: 子索引 frontmatter 补 `verified` 键（B1）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-I-12.1 `rule` ✅：`concepts/index.md` 与 `references/index.md` 已补 `verified: { by: "process:seven-concepts-v", at: "2026-10-15T15:00:00+08:00" }`；键解析实测 11 个文件（除 `log.md`）对字段清单 `{type,title,description,tags,generated,verified,status,stale_after,sources}` 的**缺失数 = 0**；`okf_version` 仍**仅**出现在 bundle 根 `index.md`。
- **Priority**: low
- **Depends On**: None
- **Discovered By**: Review R3（Finding B1，建议性）
- **Description**:
  - `concepts/index.md` 与 `references/index.md` 的 frontmatter 缺 `verified` 键（AC-10 字段清单含之），其余 10 个文件齐备。
  - 补 `verified: { by: "process:seven-concepts-v", at: "2026-10-15T15:00:00+08:00" }`，与 bundle 根 `index.md` 保持一致口径；**不得**加 `okf_version`。
- **Acceptance Criteria Addressed**: AC-10
- **Test Requirements**:
  - `rule` TR-I-12.1: 解析 12 个文件（除 `log.md`）的 frontmatter 键集，对 AC-10 字段清单的缺失数 = 0；`okf_version` 仍仅出现在 bundle 根；证据为键解析输出。

## 建议性发现记录（不阻塞验收）
- **B2**：`sheke/index.md:32` personal-growth 行存在游离 `| 15 |` 单元格，破坏两列结构——属**索引既有格式瑕疵**（I-7 仅同步数字未重构行结构），本次不重构，仅记录。
- **B3**：`sheke/index.md:33` Industry 行显示「22 束」vs `bundles/index.md:123` 实际「25 束」，致该文件分组行显示之和 65 ≠ 域节标题 68——**既有漂移、非本次引入**，仅记录不修复。

# 第三轮修复队列依赖

- I-11 与 I-12 文件集不重叠，可并行
- I-11 完成后必须执行**全域断言**（TR-I-11.1 的 Grep 断言）+ 三脚本重跑；仅改点名处而不做全域扫描视为未完成
- 全部修复完成后，以**新的独立审查者**开启 Review R4

# 审查发现修复队列（Review R4 → Implement）

> Review R4 结果 `fail`，产生 **2 条可行动发现（A1、A2，severity 均为 low）** 与 6 条建议性发现（A3、B1~B5）。
> **收敛趋势**：R1 可行动 1 条（medium）→ R2 4 条（1 high / 2 medium / 1 low）→ R3 1 条（high）→ R4 2 条（**均 low**）。发现严重度持续下降，已接近收敛。
> **根因重复**：A2 是「上游变更后下游计数未同步」的**第四次**出现（R1-F1 → R2-R2-1 → R3-A1 → R4-A2），本次载体为 `log.md` 的内链计数（42 → 实测 44）。
> **关键决策（避免涟漪复发）**：Issue I-15 需要追加 F-091 ~ F-096，会使事实总数由 90 变 **96**——这又会牵动全部计数陈述（正是前四轮翻车的原因）。因此本轮修复**由单一执行者串行完成全部涉及计数的文件**，并以**全域断言**收尾，禁止拆分为多个并发执行者。

## Issue I-13: 修正 F-087 勘误编号错标（A1）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-I-13.1 `rule` ✅：两侧 F-087 文本头由「**勘-01 关联更正值**」改为「**成效数字溯源更正（勘误②）**」，两侧逐字一致；文本头 / 状态列（关联 F-021）/ 正文 `concepts/03`（勘误②）三处口径统一；F-087 行已不含「勘-01」；勘误↔F 映射仍 13/13。
- **Priority**: medium
- **Depends On**: None
- **Discovered By**: Review R4（Finding A1，可行动）
- **Description**:
  - 两侧登记表的 **F-087** 文本头写作「**勘-01 关联更正值**：眼科基因治疗的实际单次费用约 42.5 万–85 万美元…」，但该内容属 `verification.md` 勘误清单 **② 成效数字溯源表**（关联 **F-021**）；同一行的「状态与限制」列已写「关联 F-021」，正文 `concepts/03:35` 也写「勘误②成效数字溯源表」——同一登记行内「勘-01」与「关联 F-021」互斥，三处口径不一致。
  - 修正 F-087 文本头的归属标注，使**文本头 / 状态列 / 正文**三处一致（不再出现「勘-01」）。
- **Acceptance Criteria Addressed**: AC-1, AC-4
- **Test Requirements**:
  - `rule` TR-I-13.1: 两侧 F-087 行**逐字一致**；`勘-01` 不再出现于非日期类登记行；勘误↔F 映射仍 13/13；证据为两侧文本比对 + 编号集合提取。

## Issue I-14: `log.md` 内链计数同步为实测值（A2）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-I-14.1 `rule` ✅：`log.md` 门禁清单第④项由「共 42 条」改为实测值「共 **45** 条」，并注明新增来源（R2-5 修复 `concepts/00`、`concepts/04` 各 +1；R4-B5 修复 `concepts/01` +1）；实测相对内链 45 条、断链 0；记载数与实测数一致。
- **Priority**: medium
- **Depends On**: None
- **Discovered By**: Review R4（Finding A2，可行动）
- **Description**:
  - `log.md` 手动等效验证清单第④项记「本 bundle 12 个文件的相对 Markdown 链接（共 **42** 条…）」，而实测为 **44** 条（差 2 条源于 R2-5 修复在 `concepts/00` 与 `concepts/04` 各新增 1 条内链）。
  - 同步为实测值，并注明新增来源；同时**本轮若因 I-15 新增内链，须一并按最终实测值写**。
- **Acceptance Criteria Addressed**: AC-9, AC-12
- **Test Requirements**:
  - `rule` TR-I-14.1: `log.md` 记载的内链条数 == 逐条提取消点后的实际条数（0 断链）；证据为 Grep 提取计数 + `log.md` 摘录。

## Issue I-15: 正文核验衍生值登记为 F 编号（A3）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-I-15.1 `rule` ✅：两侧登记表各 **96 条**、集合相等（Compare-Object 差 0）、连续 F-001 ~ F-096 无跳号；F-075 ~ F-096 两侧各 22 行、逐字差 0；每行半角 `|` 数均为 5（格式未破坏）。
  - TR-I-15.2 `rule` ✅：**计数全域同步 9 处**——① `bundle/index.md` description「96 条事实（含 22 条核验更正与衍生值）」② `knowledge-map.md`「96 条 F 编号事实登记在」③ `references/index.md`「F-001 ~ F-096」④ `references/verification.md`「扩充至 F-001 ~ F-096（新增 22 条…）」⑤ `log.md` 第 7 行三处（96 条 / 各 96 条 / 追加 F-075 ~ F-096 共 22 条）⑥⑦ `sheke/index.md:18/:32`「96 条事实双份登记」⑧ `personal-growth/index.md:31`「96 条事实双份登记」⑨ `article-source.md` 标题/H1/导语「F-001 ~ F-096 / 共 96 条」。
    - **全域过时断言实测**：范围 14 文件 Grep `90 条|F-001 ~ F-090|各 90 条|16 条核验更正` 命中 2 处，均属 `personal-growth/index.md` 的**游本昌另一束**（其真值 90 条）→ **本包口径残留 = 0**；正向断言命中 11 处，全部为「96 条 / F-001 ~ F-096 / 22 条核验更正」。
  - TR-I-15.3 `rule` ✅：三脚本重跑退出码均 0——`check-utf8.py`（11597 文件有效 UTF-8）、`check-toctrees.py`（全部引用有效、内容文档可达）、`check-bundles-index.py`（9 域 / 61 组 / 636 束，五面一致）。
  - **F-091 ~ F-096 登记内容**：F-091 IND 放行 2026-01-15；F-092 一期数据公布 2026-10-08；F-093 3 名 OAG 受试者 Day 56 耐受良好；F-094 2 名受试者视野测试初步改善信号；F-095 共识 2026-04 发布、老年内分泌代谢疾病学组 2025-02 发起、科技日报 2026-05-08 报道；F-096 第三方渠道同类产品约 1500 元。
  - **建议性项随修**：B1（两子索引 `sources` 各补 `src-lb-pipeline` 权威 URL）✅；B2（`personal-growth/index.md` 组级 description 补入本束一句）✅；B5（`concepts/01:42` 弱引用「勘误③」改为指向核验表 F-009 行）✅。
- **Priority**: medium
- **Depends On**: None
- **Discovered By**: Review R4（Finding A3，advisory medium——直指 AC-2/NFR-1）
- **Description**:
  - 正文出现若干**已溯源但未登记 F 编号**的核验衍生值，与 `concepts/00` 前言「全部具体声明附 F 编号」自相矛盾：
    - `index.md` 与 `concepts/00` 的 `2026-01-15`（IND 放行）、`2026-10-08`（一期数据公布）
    - `concepts/00` 的「3 名 OAG 受试者 Day 56 均耐受良好」「2 名视野测试现初步改善信号」
    - `concepts/02` 的「共识 2026-04 发布 / 老年内分泌代谢疾病学组 2025-02 发起 / 科技日报 2026-05-08 报道」
    - `concepts/04` 的「第三方渠道同类产品约 1500 元」
  - 在两侧登记表**追加 F-091 ~ F-096**（保持编号连续、与 F-075~F-090 同格式），逐条登记上述衍生值；「来源」列用 `核验`，「状态与限制」列写「核验衍生值（Review R4）｜关联 F-xxx｜P0 已核验」。
  - **因事实总数由 90 变为 96**，必须同步全部计数陈述（见 TR-I-15.2）。
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-I-15.1: 两侧登记表各 **96 条**、集合相等、连续 F-001 ~ F-096 无跳号，F-075~F-096 两侧逐字一致；证据为正则提取比对。
  - `rule` TR-I-15.2: **计数全域同步**——8 处计数陈述（bundle `index.md` description、`knowledge-map.md`、`references/index.md`、`references/verification.md` 登记扩充行、`log.md`、`sheke/index.md` 两处、`personal-growth/index.md` 本束行）全部改为 **96 条 / F-001 ~ F-096 / 22 条核验更正与衍生值**；全域 Grep 断言 `90 条|F-001 ~ F-090|各 90 条|16 条核验` 在**本包口径**内命中 0（排除 `article-source.md`/`facts.md` 的 F-090 表行、以及 `personal-growth/index.md` 中 how-to-live-better 另一束的合法「89 条」）；证据为 Grep 结果。
  - `rule` TR-I-15.3: 重跑 `check-utf8.py` / `check-toctrees.py` / `check-bundles-index.py` 三条均通过；证据为脚本输出。

## 建议性发现处理（本轮随修）
- **B1**：`concepts/index.md` 与 `references/index.md` 的 `sources` 仅含 `blog`，缺核验权威 URL → 各补 1 条核验权威 URL（如 `https://www.lifebiosciences.com/pipeline/`），使 AC-10 双信源要求在子文档层面亦满足。
- **B2**：`personal-growth/index.md` 的 frontmatter `description`（组级）未收录本束 → 在组 description 末尾补入本束一句（与本束行简介口径一致，保持简洁）。
- **B5**：`concepts/01:42` 以「勘误③」注解 F-009 肿瘤风险，属弱引用（勘误③为口径对照表，与该议题不严格对应）→ 改为指向「核验报告核验表 F-009 行」。
- **B3 / B4**：`sheke/index.md` 的游离单元格与 Industry 行既有漂移——**既有问题、不在本次范围**，仅记录不修复。

# 第四轮修复队列依赖

- **全部由单一执行者串行完成**（I-13 → I-15 → I-14 → B1/B2/B5），因为 I-15 会把事实总数改写为 96 并牵动所有计数文件；拆分并发会再次制造计数漂移
- 收尾必须执行 TR-I-15.2 的**全域断言** + 三脚本重跑
- 全部完成后，以**新的独立审查者**开启 Review R5

# Task Dependencies

- T2 depends on T1（识读结论是事实登记的输入）
- T3 depends on T2（核验对象来自 F 登记清单）
- T4 depends on T3（骨架与篇目依核验复杂度微调）
- T5 depends on T4（信源先行生成依赖最终篇目）
- T6 depends on T5（审查对象是已生成的 bundle）
- T7 depends on T5（索引接入依赖 bundle 目录已落盘）
- T8 depends on T6 AND T7（提交前须审查通过且索引同步完成）

**可并行项**：T6 与 T7 在 T5 完成后可并行推进；T1（视觉识读）可在 T2 启动前与 spec `facts.md` 初始化并行。

# 审查发现修复队列（Review R1 → Implement）

> Review R1 结果 `fail`，产生 1 条可行动发现（F1）与 7 条建议性发现。以下为按「可行动发现必须固化为 pending issue」规则创建的修复项。

## Issue I-1: 修正「45 条权威 URL」计数虚高
- **Status**: `completed`
- **Completion Evidence**:
  - TR-I-1.1 `rule` ✅：4 处（`knowledge-map.md:91`、`log.md:8`、`references/index.md:13`、spec `tasks.md` TR-3.3 证据行）统一改为「40 条权威信源（全文唯一 URL 41 条含博文）」；bundle 内 Grep `45 条` 命中 **0**，实测 `^\| src-` 行数 = **40**。
- **Priority**: high
- **Depends On**: None
- **Discovered By**: Review R1（Finding F1，可行动）
- **Description**:
  - 实测：bundle `references/verification.md` 的「已核验权威信源清单」实际为 **40 条** `| src-` 行（40 个唯一 id），全文唯一 URL 共 **41** 条（含博文 URL）。但 4 处一致声称「45 条权威 URL」，虚高 5 条，属**数量陈述失真**。
  - 需修正的 4 处：① `bundle/knowledge-map.md:91` ② `bundle/log.md:8` ③ `bundle/references/index.md:13` ④ spec `tasks.md` 的 TR-3.3 完成证据。
  - 统一改为准确表述：「**40 条权威信源**（全文唯一 URL 41 条，含博文本身）」。
- **Acceptance Criteria Addressed**: AC-3, AC-12
- **Test Requirements**:
  - `rule` TR-I-1.1: **交付物与内容声称**中 Grep `45 条` 命中数为 0（范围限定：bundle 全目录 + spec `tasks.md` 中除本 Issue 描述文本以外的完成证据行；本 Issue 的**问题陈述**本身必须保留「45 条」字样以示世缺陷，不计入命中原因为其非内容声称）；且上述 4 处表述与实测值（40 / 41）一致；证据为 Grep 结果 + `Select-String '^| src-'` 行数。

## Issue I-2: 为核验更正与衍生值新增 F 编号（AC-4 要求）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-I-2.1 `rule` ✅：spec `facts.md` 与 bundle `references/article-source.md` 各 **89 条**，集合相等（差异 0），均连续 **F-001 ~ F-089** 无跳号；两侧 F-075~F-089 逐字一致（SHA-256 相同）。
  - TR-I-2.2 `rule` ✅：勘-01~勘-13 与新增 F 编号一一对应（勘-01→F-075、勘-02→F-076、勘-03→F-077、勘-04→F-078、勘-13→F-079、勘-08→F-080、勘-09→F-081、勘-05→F-082、勘-07→F-083、勘-10→F-084、勘-11→F-085、勘-12→F-086，成本项→F-087）；另有 F-088（OSK 三基因全称 Oct4/Sox2/Klf4）、F-089（Luxturna 42.5 万 / GS010 €425,000）两条核验衍生值。
  - TR-I-2.3 `rubric` 得分 4/5：每条更正行含「源文口径→权威值」差异 + 权威来源类别 + 处理方式三要素，「状态与限制」列注明「核验勘误（Review R1）｜对应勘-xx｜P0 已核验」；扣分项为部分行的权威来源以类别（如「核验」）概括，未逐行内嵌完整 URL（URL 完整清单见 `verification.md` 第七节）。
  - **连带计数同步**：因事实总数由 74 扩至 89，已同步 bundle `index.md` description、`log.md`、`references/index.md`、`knowledge-map.md`、`references/verification.md`（新增登记扩充说明行）与父级 `personal-growth/index.md` 的散文计数；并在 `verification.md` 明确区分「R 阶段待核验声明 41 项」与「新增 15 条已核验登记行」。
- **Priority**: high
- **Depends On**: None
- **Discovered By**: Review R1（Finding F2、F6，建议性但直指 AC-4 / NFR-1）
- **Description**:
  - AC-4 要求「**新增 F 编号**记录正确值与差异」；当前更正仅以 `勘-01~勘-13` 平行编号存于 `verification.md`，`facts.md` 停留在 R 阶段 74 条原始值，与 AC-4 字面不符。
  - 从 **F-075** 起新增 F 行，**同时写入 spec `facts.md` 与 bundle `references/article-source.md`**（两侧编号集合必须保持互等且连续）：
    - 勘-01~勘-13 对应的**更正值**各 1 条（如 F-075 = 首例给药权威时点 2026-06-09；F-076 = 75% 的权威口径＝小鼠/表观遗传时钟/多组织 50–95%；F-077 = 小鼠中位寿命 +8.5%（雌）与 OSK 全身重编程约 +7% 取代「近乎翻倍」；F-078 = 检测报告纯度口径 ≥99%；F-079 = 共识题录补全 中华老年医学杂志 2026, 45(4): 497-508；F-080 = 文献 [4] 权威作者序列 Mills KF, Yoshida S, Stein LR…；F-081 = 文献 [6] 权威作者序列 Irie J, Inagaki E, Fujita M…；F-082 = 图 04 引用编号 [4]/[8] 错位；F-083 = 2016 年评论实为 Cell Research（Wu LE & Sinclair DA, 2016, 26: 971-972）；F-084 = 王骏「30 余年」主流口径为四十余年；F-085 = 「全球首个全酶法量产」降级为「率先实现之一」并与 BONTAC 声明冲突；F-086 = 正文重复段落编辑瑕疵；F-087 = 眼科基因治疗实际单价 42.5 万–85 万美元）。
    - 正文中已出现但未登 F 的**核验衍生值**各 1 条（如 **F-088** = OSK 三基因全称 Oct4 / Sox2 / Klf4；**F-089** = Luxturna 每眼约 42.5 万美元、GS010 每针 €425,000）。
  - 每条「状态与限制」列须写明「**核验勘误（Review R1）**」或「**核验衍生值**」+ 对应勘误编号。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4
- **Test Requirements**:
  - `rule` TR-I-2.1: 正则 `^\|\s*F-(\d{3})` 提取两侧编号集合，**相等且连续**（F-001~F-089 或实际终值），无跳号；证据为比对输出。
  - `rule` TR-I-2.2: `verification.md` 的勘-01~勘-13 每条都能在 `facts.md`/`article-source.md` 中找到对应的新 F 编号行；证据为勘误↔F 编号映射表。
  - `rubric` TR-I-2.3: 更正登记的分层清晰度；scale 1-5；锚点 1 = 只写「已勘误」不给数值；3 = 给了正确值但未标来源；5 = 每条更正含「源文口径 / 权威值 / 权威来源 URL / 处理方式」四要素；threshold >= 4；证据为抽样 5 条。

## Issue I-3: 补齐手动等效验证清单并运行官方脚本
- **Status**: `completed`
- **Completion Evidence**:
  - TR-I-3.1 `rule` ✅：`log.md` 门禁小节由 5 项扩为 **8 项**（① UTF-8 strict roundtrip ② 双份 F 编号一致 ③ 三级 toctree 完整可达 ④ 相对链接全可达 ⑤ 敏感/绝对路径零出现 ⑥ frontmatter 齐备 ⑦ 勘误落实 ⑧ 计数三处一致），逐项带结论。
  - TR-I-3.2 `rule` ✅：三个官方脚本**实际执行**且退出码均为 0——`check-utf8.py` → 「UTF-8 检查通过: 11597 个文件均为有效 UTF-8」；`check-toctrees.py` → 「toctree 检查通过: 全部 index.md 引用有效，所有内容文档均可达」；`check-bundles-index.py` → 「bundles 总索引对账通过: 9 域 / 61 组 / 636 束，五面一致」；命令与输出已记入 `log.md`。
- **Priority**: medium
- **Depends On**: None
- **Discovered By**: Review R1（Finding F3，建议性）
- **Description**:
  - `bundle/log.md` 的手动等效验证清单仅记录 5 项，未覆盖 TR-6.3 要求的 8 项（缺 UTF-8 / 相对链接可达 / frontmatter 齐备 / 勘误落实 4 项）。
  - 且本仓 `projects/awesome-okf-xs/scripts/` 下的 `check-utf8.py`、`check-toctrees.py`、`check-bundles-index.py` **可直接独立运行**（Review R1 实测均通过），实施时未执行。
  - 补齐 8 项清单，并**实际运行**上述三个脚本、把命令与关键输出记入 `log.md`。
- **Acceptance Criteria Addressed**: AC-9, AC-12
- **Test Requirements**:
  - `rule` TR-I-3.1: `log.md` 含 8 项清单且每项有结论；证据为 `log.md` 门禁小节。
  - `rule` TR-I-3.2: 三个脚本各有一条实际执行记录（命令 + 输出摘要），或明确记为 `blocked` 并说明原因；**禁止在未执行时声称通过**；证据为 `log.md`。

## Issue I-4: 正文落实勘-07（Cell Research 刊名）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-I-4.1 `rule` ✅：`concepts/02-nad-nmn-pathway.md` 第 50 行（新增 bullet，文件 83→84 行）出现 `Cell Research`，并同句标注「此为**源文口径**」，写明「经核验实为 Cell Research（属 Nature Portfolio 系列刊，doi 10.1038/cr.2016.80），作者 Wu LE & Sinclair DA，2016, 26: 971-972」；`]\(/`、`file:///` 命中 0。
  - 附注：该文件原标题段并无「Nature 子刊」字样（该表述原仅存于 `references/article-source.md` 与 `verification.md`），故以「补写更正条目」方式落实勘-07 于正文。
- **Priority**: low
- **Depends On**: None
- **Discovered By**: Review R1（Finding F4，建议性）
- **Description**:
  - 勘-07（源文称「2016 年发表在《Nature》子刊上的评论」，实为 **Cell Research**（Nature Portfolio 系列刊，doi 10.1038/cr.2016.80），作者 Wu LE & Sinclair DA）仅登记于 `verification.md`，未在正文体现。
  - 在 `concepts/02-nad-nmn-pathway.md` 涉及 NMN 里程碑的段落中，把「Nature 子刊」表述更正为 **Cell Research（Nature Portfolio 系列刊）**并标注源文口径。
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-I-4.1: `concepts/02-nad-nmn-pathway.md` 出现 `Cell Research` 且周边语境标注了源文口径；证据为 Grep + 段落摘录。

## Issue I-5: 补齐子索引 frontmatter 字段
- **Status**: `completed`
- **Completion Evidence**:
  - TR-I-5.1 `rule` ✅：`concepts/index.md` 与 `references/index.md` 的 frontmatter 由 `type`+`title` 补齐为含 `description`/`tags`/`generated`/`status: flagged`/`stale_after: 2027-06-30`/`sources`（id `blog`）；YAML 解析确认两文件**均无** `okf_version` 键，全 bundle `okf_version` 仍仅出现于根 `index.md`；隐藏 toctree 块与正文未动。
- **Priority**: low
- **Depends On**: None
- **Discovered By**: Review R1（Finding F5，建议性）
- **Description**:
  - `concepts/index.md` 与 `references/index.md` 目前仅有 `type` + `title`，而 AC-10 要求「bundle 根 `index.md` 与各子文档 frontmatter」字段齐备。
  - 为两个子索引补齐 `description` / `tags` / `generated` / `status` / `stale_after` / `sources`（**`okf_version` 仍只能出现在 bundle 根**，不得加）。
- **Acceptance Criteria Addressed**: AC-10
- **Test Requirements**:
  - `rule` TR-I-5.1: 两文件的 frontmatter 含 `type`/`title`/`description`/`tags`/`generated`/`status`/`stale_after`/`sources`；全 bundle `okf_version` 仍仅出现在根 `index.md`；证据为键解析输出。

## Issue I-6: 两侧 F-058 表述口径同步
- **Status**: `completed`
- **Completion Evidence**:
  - TR-I-6.1 `rule` ✅：spec `facts.md:69` F-058 已改为与 bundle 侧完全一致的中性文本（「文章以图片引导读者了解产品详情、规格与服用方式，并给出低于公域的私域通道价（源文自述价格）。」），两侧**逐字一致**；`facts.md` 与 bundle 全目录 Grep `领取专属价|点击上方图片` 命中 **0**（残余 3 处均在 `tasks.md` 本 Issue 描述与 `spec.md` 验收标准条文中，属描述缺陷所需的字样，已按 TR-I-6.1 范围限定排除）。
- **Priority**: low
- **Depends On**: None
- **Discovered By**: Review R1（Finding F8，建议性）
- **Description**:
  - spec `facts.md` F-058 保留了源文「点击上方图片」「领取专属价」等引导语，bundle `article-source.md` 已改写为中性表述——同编号两侧文本不一致。
  - 把 spec `facts.md` F-058 也改为与 bundle 侧一致的中性客观转述（保留事实，去掉引导语），使双份登记口径统一。
- **Acceptance Criteria Addressed**: AC-1, AC-5
- **Test Requirements**:
  - `rule` TR-I-6.1: **交付物口径**中两侧 F-058 文本一致，且 spec `facts.md` 与 bundle 全目录 Grep `领取专属价|点击上方图片` 命中数为 0（本 Issue 与 `spec.md` 验收标准条文中的问题陈述字样不计入，属描述缺陷所需）；证据为 Grep 结果 + 两侧文本比对。

## 已知既有问题（不在本次范围，不予修复）
- **Review R1 Finding F7**：`sheke/index.md` 的 Industry 分组行束数（22）与 `bundles/index.md` 该组实际束数（25）存在**既有漂移**，`git diff` 证明该行本次未被改动，非本束引入。按「最小变更、不扩大范围、不回滚无关变更」原则**仅记录不修复**，留待独立治理任务处理。

# 修复队列依赖

- I-1 / I-3 可并行（均独立）
- I-2 与 I-6 须串行（都在改 F 编号登记表，I-6 改 F-058 文本、I-2 追加 F-075+，同文件并发会冲突）
- I-4 / I-5 独立可并行
- 全部修复完成后，以**新的独立审查者**开启 Review R2
