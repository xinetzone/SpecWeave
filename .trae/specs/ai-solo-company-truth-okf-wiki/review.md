# 独立对抗审查报告：AI 一人公司 110 万自述 → OKF 知识包

## 审查元信息

| 项 | 值 |
|---|---|
| 审查时间 | 2026-10-14 |
| 审查者 | 独立对抗审查者（fresh context，只读） |
| 审查对象 | `projects/awesome-okf-xs/doc/bundles/sheke/industry/ai-solo-company-truth/`（9 个 .md）及三级索引改动、spec 侧 facts.md |
| 只读声明 | 未修改任何被审文件；本次会话唯一写入文件为本报告。子模块 git 工作区经 `git status` 复核，无审查引入的变更 |
| 对照基准 | spec.md（AC-1~AC-7）、tasks.md、facts.md、同组先例 `auto-money-system/`、磁盘当前态三级索引 |
| 方法 | ①通读全部 9 个被审文件 + spec/plan/facts + 先例；②独立重跑机械检查（正则、官方三脚本、Grep、Test-Path、git diff），不复述作者自检；③按质证点 A–G 逐条独立判断；④对全部引号短串逐一抽取并与 F 表原文对账 |

> **结论演进**：**首轮（2026-10-14）：FAIL**——AC-5 规则项失败（concepts/02 两条主题关联相对链接深度错误、Test-Path 不可达，见下文 P0-1），首轮 FAIL 全部裁决与发现完整保留于本报告下文，不删改。
> **第二轮复审（2026-10-14，同日）：PASS**——P0-1、P1-1、P1-2 经独立复核全部闭环，AC-1~AC-5 全 PASS、AC-6/AC-7 均 4/5（≥4）；详见文末"复审记录（第二轮）"。

<details>
<summary>首轮记录（FAIL，已被第二轮 PASS 取代，保留备查）</summary>

**首轮最终结论：FAIL**（AC-5 规则项失败：concepts/02 两条主题关联相对链接深度错误、Test-Path 不可达。详见 P0-1）。

---

## 逐 AC 裁决

### AC-1：bundle 骨架与定位 —— **PASS**（rule）

独立证据：

- 目录枚举恰为 9 个 .md：`index.md`、`log.md`、`concepts/{index,00-revenue-and-health-timeline,01-four-truths,02-actions-and-boundaries}.md`、`references/{index,article-source,verification}.md`，与 FR-1 一一对应；`examples/` Test-Path=False。
- 根 index.md L50-57 隐藏 toctree 三条目（concepts/index、references/index、log）拼写正确；concepts/index.md L3-10 toctree 3 条；references/index.md L3-9 toctree 2 条。官方 check-toctrees 对本束零命中（见机械检查），即三条 toctree 链全部可达。
- 根 index.md L24 明确声明"不是创业操作教程，也没有可复现的 examples/"，description（L5）含"非操作教程"，两问判定在 log.md L8 留痕。

### AC-2：F 编号双份一致、事实观点分层 —— **PASS**（rule，附 1 项 P1 观察）

独立证据（正则 `^\|\s*F-(\d{3})\s*\|` 自行提取，非引用作者输出）：

- facts.md：count=38、min=1、max=38、无缺号、无重复；article-source.md：count=38、min=1、max=38、无缺号、无重复。
- 两集合双向差集均为空（only-in-facts 空、only-in-article 空）。
- 三篇 concepts 全部 F 引用（含区间与枚举）：00 篇 10 个、01 篇 22 个、02 篇 18 个，并集 32 个；**越界数 0、引用但 article 表查无者 0**。未被 concepts 引用的 6 个为 F-001/002/003（元信息）、F-004（开场口号）、F-007（"黑工"观点）、F-014（文末口号），属元信息与纯口号，不引用合理。
- 文字层 F-001~014、图卡 F-015~038 的 locator 分层在两份表均保留；自述成效/修辞比例在分类列可辨识（article 表无独立 status 列，但以"页面事实（自述成效/自述经历/自述口径/自述比例）""作者观点（修辞比例）"后缀承载，facts.md 登记的 12 个 flagged 编号在 article 表中均可一一辨识，符合 TR-1.2"列可合并、五信息可辨识"的容许）。
- 所有源文具体数字在 concepts 均挂 F 回指（110/70/180/12 万粉/5 万/12 万投入/7 万/1500/200→8/15 万/9 万/3 万/9.9 万/9.9 块/14 斤/14 小时/四档/2025/2026/Coze 等逐条抽查通过）；派生数"40 万成本/约 36%"有 verification L79 算术行背书并标注 F-006，属可追溯派生而非新声明。

张力披露（不改变本 AC 裁决，记入 P1-1）：02 篇 L74 出现一个 F 表与 verification 均无登记、且无任何计数依据的具体数字"60%"，严格按本 AC Then 子句"concepts 中出现的每个具体数字都能回指某 F 编号"字面读属例外。鉴于它是写作过程自述（非源文经营事实、不作为结论），且 NFR-1 的溯源对象是源声明，按规则意图判 PASS，但要求修复后闭环。

### AC-3：P0 核验与勘误、flagged 管理 —— **PASS**（rule）

独立证据（verification.md 逐点定位）：

- 勘误四张清单齐备：①日期/版本表 L36-42；②成效数字溯源表 L44-55（逐数"无独立出处"）；③口径对照表 L57-64 六点；④引文逐字表 L66-69。
- 五个必登张力全部有落点：110 万 vs 180 万（③-1，L59）、70 万到手成本张力（③-2，L60）、9.9 块 vs 9.9 万（③-3，L61）、2025/2026 时间线（③-4，L62，含"调整 3 个月后"落点推算的附加核对）、"第三档上限"措辞（③-5，L63）；三修辞比例另列③-6（L64）。concepts 侧五张力也均有落点：00 篇 L27-37（双口径+成本+时间线）、L61（9.9 双关）；01 篇 L90（第三档措辞）。
- 算术自洽 5 行记录（L73-79）：80×1500=12 万、12−5=7、15−9=6、100×1=10×10=100 万、110−70=40 万，本人复核结果全部正确（40/110≈36% 亦正确）；且 L76 明确 12 万为"机会成本式投入、非实际现金流出"，防止读者误读。
- 无编造权威 URL：全文外部 URL 仅博文 1 个 + coze.cn 1 个。coze.cn 经本审查独立 WebFetch 实测可访问，确为字节跳动扣子平台官网，且 verification L83 明确"仅证明名词真实，不支撑任何经营结论"。
- flagged 一致性：6 个含 frontmatter 文件（根 index + 3 concepts + article-source + verification）status 均为 flagged；根 index L22 顶部 flagged 提示块明示"不是收益基准、不是行业统计，也不构成成功承诺"。

### AC-4：原创改写与版权安全 —— **PASS**（rule）

独立证据：

- 抽取全束全部中文引号串（134 行清单）逐一与 F 表对账：**最长直引约 29 字**（00 篇 L61），无 >40 字直引；正文为原创改写，无全文/长段镜像。引号 fidelity 问题见 P1-2、P2-1（均为短句裁剪，非长段复制）。
- 新束目录无 .jpg/.jpeg/.png/.gif/.webp/.svg/.bmp/.html/.htm（Glob 实测零文件）；无 raw HTML（正则 `<[a-zA-Z/][^>]*>` 零命中）。
- 无 `file:///`、无 `C:\Users`、无 `/Users/`（Grep 零命中）；临时图片目录 `%TEMP%\okf-article-imgs` Test-Path=False，已清理属实。
- 图卡内容以"图N"locator 转述（article-source L19 及各行 locator 列），原图未入库。

### AC-5：三级索引与机械门禁 —— **FAIL**（rule）

通过项（独立证据）：

- 官方 `scripts/check-bundles-index.py` 退出码 0："9 域 / 61 组 / 634 束，frontmatter、计数行、节标题、分组表、toctree 五面一致"。当前态 634（含并行会话 +4 个 jishu 束），本束增量 sheke 66→67、industry 24→25 在 mermaid（bundles/index.md L29）、域节标题（L114）、industry 表行（L124=25）三面同步；frontmatter total_bundles=634（L6）与正文 634（L15）一致。
- industry 组索引：导航表 22 行、toctree 22 条（正则实测），磁盘 25 束；sheke 域索引 L17/L33 同步为登记口径 22。22（登记）/25（磁盘）双轨与 spec Non-Goals 一致，3 个既存漂移束（telecom×2、ling）未被误改，log.md L11 有注记。
- git diff 实测：bundles/index.md 相对 HEAD（629）的改动中本会话仅贡献 sheke/industry 五处增量；jishu 466→470、ai 239→241、iot 8→9、systems 2→3 等并行在途改动完整保留，零回退。
- 官方 `scripts/check-utf8.py` 退出码 0（11556 文件）；本束 9 文件另做 strict UTF-8 roundtrip + BOM 检测全部通过。
- check-toctrees.py 输出 grep `ai-solo-company-truth` **零命中**（告警 81 处逐条核对：sheke 侧仅 ling/telecom×2 三漂移束，余为 jishu 并行在途束 deepseek-harness/agent-self-evolution-evaluation/microsoft-mxc/wifit3/tauri）。
- 根 index.md L40-41 两条主题关联链接 Test-Path=True。

失败项（P0-1）：

- concepts/02-actions-and-boundaries.md L81-82 的两条主题关联链接写作 `../auto-money-system/index.md`、`../ai-one-person-micro-product/index.md`。该文件位于 `concepts/` 子目录，`../` 只回退到束根，规范化解析目标为 `ai-solo-company-truth/auto-money-system/index.md`——**Test-Path=False（两条均 False）**；正确深度应为 `../../auto-money-system/index.md`（实测 True）。同组先例可证惯例：papi-jiang-solo-ip 的 concepts 内引用兄弟束用 `../../ai-monetization/concepts/00-overview.md`。作者 TR-6.1④"两条主题关联 Test-Path 均 True"只测了根 index 的一对，漏测 concepts/02 的一对。违反本 AC"全部相对链接 Test-Path 可达"明文条件。

### AC-6：知识转化质量 —— **4 / 5**（rubric，阈值 4，通过）

锚点理由：

- 事实/作者观点/执行者洞察三分清晰且可示范：00 篇"读这类账本的三个问题"（证据→口径→可复制结构）是超越复述的方法论；01 篇 L56 区分机会成本与现金亏损、L100 主动声明四主题因果链是"编辑性重组、属于待验证假设，原文未做这样的因果论证"——自我设限意识达到 5 分锚点描述。
- 三条建议全部完成"成功公式→可验证假设"降级（02 篇 L25-49），每条带可验证指标、证伪信号、边界三要素；可迁移模式（L60-77）触发条件/核心步骤（6 步）/反模式（5 条）/迁移验证四要素齐备；四类边界表（L53-58）含法律合规空白项声明，非粉饰性罗列。
- 修辞比例防误读处理到位：90%/80%/前 1% 在 01 篇 L21/L38/L59、02 篇 L49/L66、article L78、verification L64、根 index L48 六处显式标注"非统计/后台印象"，全束无一处把经营数字写成确定结论或收益承诺。
- 扣分项：02 篇 L74"60%"恰好在本束自律承诺（"修辞比例不升级为统计"）的同一维度上引入无依据具体数（P1-1）；多处短引号非逐字（P1-2、P2-1）。距 5 分锚点的严谨满格状态差一档。

### AC-7：OKF 规范符合度 —— **4 / 5**（rubric，阈值 4，通过）

锚点理由：

- 与先例 auto-money-system 逐键比对一致：根 index 九字段（okf_version/type/title/description/tags/generated/verified/status/stale_after/sources）齐备；concepts/reference 子文件不带 okf_version、sources 三条目且 blog 用 `resource:` 键、根 index blog 用 `url:` 键——与先例完全同款；article-source 仅 blog 源 + title、verification 增列背景源 coze-official 并标注用途，体例合理。
- log.md、concepts/index.md、references/index.md 无 frontmatter，与先例同款；stale_after 统一 2026-12-31；toctree+列表/表格双轨齐备；子 index 无 frontmatter 符合先例。
- 扣分项：concepts/02 互链深度违先例且功能失效（P0-1，已计入 AC-5）；22/25 登记与磁盘双口径在域索引与总索引之间未加一句口径说明（P2-2）。

---

## 发现清单

### P0（必修，阻断通过）

| # | 位置 | 问题 | 修复建议 |
|---|---|---|---|
| P0-1 | concepts/02-actions-and-boundaries.md L81、L82 | 两条兄弟束互链深度少一级：`../auto-money-system/index.md`、`../ai-one-person-micro-product/index.md` 自 concepts/ 目录解析 Test-Path=False（规范化后指向本束内不存在的同名目录）；正确为 `../../auto-money-system/index.md`、`../../ai-one-person-micro-product/index.md`（已实测 True）。根 index L40-41 的同型链接深度正确，无需动 | 两处 `../` 改 `../../`；修复后对束内全部 .md 链接重跑 Test-Path 清单 |

### P1（建议在本轮修复后复审）

| # | 位置 | 问题 |
|---|---|---|
| P1-1 | concepts/02-actions-and-boundaries.md L74 | "只转文字层、漏掉图卡层，导致 60% 实质内容缺失"——"60%"在 F 表、verification、同束任何文件均无登记与计数依据，且与根 index L24"约一半实质内容"及 02 篇 L65"本文图卡承载了约一半实质内容"自相矛盾。F 条数 24/38≈63% 是"条数比"，不能直接表述为"内容占比"。这是 concepts 中唯一无 F 回指的具体数字，与全束"无登记数字不入正文"的自律冲突。建议改为"约一半"或明示口径（"F 表 38 条中 24 条（约六成）来自图卡"） |
| P1-2 | concepts/00 L36 与 references/verification.md L60（同句两处）；concepts/00 L58；concepts/00 L61；verification L59 | 非逐字却加引号的 4 类典型：①"工具订阅费、零星外包"——F-006 原文为"工具订阅费**与**零星外包**小成本**"；②"刨掉工具订阅和外包"——F-006 原文为"刨掉工具订阅**费与零星**外包**小成本**"；③L61 约 29 字引语"做一次一对一咨询赚 3 万，不如打包成 9.9 万的标准化落地产品"脱漏 F-013 的"把整套流程"；④"我今年（2026）做到 180 万"把解释性年份插进引号内，F-037 原文为"我今年做到 180 万"，2026 系推断（依据 F-020/F-035 语境），应移到引号外 |

### P2（观察项，不阻断；供后续打磨或台账登记）

| # | 位置 | 观察 |
|---|---|---|
| P2-1 | concepts/01 L38（"90% 的人把一人公司想简单"，F-015 作"想简单了"且"一人公司"带内层引号）、L49/L56（"净亏 7 万"，F-023 作"净亏损 7 万"）、L75（"技术强三倍"脱"比自己"）、L59 与 verification L64（"80% 来自前 1%（老粉）"脱"的"）、L90（"已经在第三档上限"脱句末"了"）、02 篇 L39（"9.9 万标准化产品"脱"的/落地"）；verification L62 与 00 篇 L37 的压缩组合引号（"2025 年 all in 做 12 个月""2026 前半年做抖音""今年 180 万"） | 均为语气词/连接词级裁剪，语义未变且全部紧邻 F 标注，按本束 AC（仅 >40 字直引须严格逐字）不构成失败；但与"非逐字不加引号"纪律有轻微出入，建议批量回改或去引号转述 |
| P2-2 | sheke/index.md L17、L33（industry 22 束）；bundles/index.md L124（industry 25） | 登记口径 22 与磁盘口径 25 双轨并存，三处各自自洽、log L11 已注记 3 个既存漂移束、门禁脚本只校验总索引故五面一致；读者跨层对读可能困惑，建议后续补登记漂移束或在域索引加一行口径说明。非本次任务范围 |
| P2-3 | facts.md ↔ article-source.md 双份 F 表 | 编号集合完全一致，但个别 claim 文案非逐字相同（F-004："给你们甩几个实打实的数字" vs "实打实的数字"；F-013："不用反复耗时间的真杠杆" vs "真杠杆"）；分类标签 page_fact↔页面事实 为有意英中对照，可接受。若后续要求双份逐字一致可统一 |
| P2-4 | log.md L15 vs 当前脚本输出 | 作者记录 check-toctrees 82 处，本审查实测 81 处（并行会话期间变动所致）；分布全部为并行在途束与 3 个漂移束，本束始终零命中，数字差异无本束责任，仅记录 |

---

## 机械检查原始输出摘要（均为本审查亲自执行，cwd=projects/awesome-okf-xs）

1. **双份 F 集合（PowerShell 正则）**：facts count=38 min=1 max=38；article count=38 min=1 max=38；only-in-facts/only-in-article/missing/dup 四项全空。
2. **concepts F 引用域检查**：00→10 个、01→22 个、02→18 个，并集 32；out-of-range=0；referenced-but-not-in-article=0；未引用集合=F-001/002/003/004/007/014。
3. **check-bundles-index.py**：exit 0，`bundles 总索引对账通过: 9 域 / 61 组 / 634 束，frontmatter、计数行、节标题、分组表、toctree 五面一致。`
4. **check-utf8.py**：exit 0，`UTF-8 检查通过: 11556 个文件均为有效 UTF-8。` 本束 9 文件 strict roundtrip 全 OK、无 BOM。
5. **check-toctrees.py**：exit 1（既有漂移导致），`检测到 81 处 toctree 导航问题`；grep `ai-solo-company-truth` 命中数=0；sheke 侧命中仅 ling-3-1-flash-first-test（9 文件）、telecom-ai-pilot-base（10）、telecom-token-operation（10）+3 条组索引缺失条目。
6. **敏感串/媒体 Grep+Glob**：`file:///|C:\Users|/Users/` 零命中；raw HTML 标签零命中；图片/html 文件零个；examples 目录不存在；`%TEMP%\okf-article-imgs` 不存在。
7. **链接 Test-Path**：根 index 兄弟束链接 2/2 True；concepts/02 兄弟束链接 0/2 True（P0-1）；束内全部相对链接（含 `/references/` 束根惯例链接，先例同款）除上述 2 条外全部可达。
8. **计数实测**：industry 磁盘目录 25；industry/index.md 导航行 22、toctree 条目 22；bundles/index.md total_bundles 634、正文 634、mermaid sheke 67、sheke 节 67、industry 行 25；sheke/index.md industry 两处均 22（登记口径）。
9. **git 范围**：新文件恰为 9 个 .md；本会话修改 3 个索引（bundles/sheke/industry）；jishu 并行 WIP（4 新束 + 4 计数增量）在 diff 中完整保留。
10. **背景源独立复核**：WebFetch https://www.coze.cn/ 成功，站点为字节扣子官网（含 Agent/团队版/企业版内容），verification 的背景一致性声明成立。

---

## 实质性质证覆盖说明（A–G，写明具体查了什么）

- **A 事实纯度/数字语气**：逐数核对 110/70/180/12 万粉/5 万/12 万/7 万/1500/200/8/15 万/9 万/3 万/9.9 万/9.9 块/月入 10 万/14 小时/14 斤/四档边界，全部有 F 锚点且附"自述/无佐证"限定；全束无收益承诺式语气；90%/80%/前 1% 六个落点均被标为修辞/后台印象。唯一例外为 P1-1 的"60%"。
- **B 五大张力**：110vs180、70 万成本张力、9.9 块/9.9 万、第三档上限、2025/2026 时间线，在 concepts 与 verification 两侧均找到落点（见 AC-3 证据）。
- **C 引号与直引**：程序抽取全束引号串 134 行逐条对账，结论：无 >40 字直引；4 处非逐字引号入 P1-2，9 类语气词级裁剪入 P2-1。
- **D frontmatter/体例**：6 个内容文件九字段（子文件无 okf_version）与先例逐键比对一致；blog 源 url/resource 分键惯例一致；log 与两个子 index 无 frontmatter 与先例一致。
- **E 计数自洽**：以磁盘当前态与门禁脚本为准（634/67/25），不因并行会话波动误判；22/25 双轨按 spec Non-Goals 评估为观察项。
- **F 模式与建议**：可迁移模式四要素逐条点名到位；三建议三要素（验证指标/证伪信号/边界）逐条核实存在且非套话（如假设二证伪信号含"成交周期长到现金流断裂"、假设三含"SaaS 研发运维成本超过服务费收入"）。
- **G 链接深度**：根 index 与 concepts/02 共 4 条兄弟束链接分别 Test-Path，发现后者深度错误（P0-1）。

</details>

---

# 复审记录（第二轮，2026-10-14）

## 复审元信息

| 项 | 值 |
|---|---|
| 复审时间 | 2026-10-14（与首轮同日，Implement 方修复后） |
| 复审者 | 首轮独立审查者延续（fresh 重读磁盘修复后文件，只读） |
| 复核范围 | 被修文件 4 个：concepts/00、01、02 与 references/verification；并对全束 9 文件重跑机械门禁 |
| 只读声明 | 未修改任何被审文件；本章节为本次唯一写入（review.md）。`git status` 复核：束内仍恰为 9 个 .md（无新增/删除文件），3 个索引 modified，无修复引入的意外文件 |
| 方法 | 逐行重读 4 个修复文件并与 F 表原文重新对账；自行编写全束 markdown 链接机械解析脚本（23 条，非仅 Test-Path 两条）；重跑官方 UTF-8/index/toctrees 三脚本；frontmatter 字段机械扫描；新数字与敏感串复查 |

## 首轮发现项逐项复核

### P0-1（阻断项）：concepts/02 互链深度 —— **已闭环 ✅**

- 修复后 [02-actions-and-boundaries.md L81-82](../../../projects/awesome-okf-xs/doc/bundles/sheke/industry/ai-solo-company-truth/concepts/02-actions-and-boundaries.md#L81-L82) 已改为 `[auto-money-system](../../auto-money-system/index.md)` 与 `[ai-one-person-micro-product](../../ai-one-person-micro-product/index.md)`。
- 独立实测（以 concepts/ 目录为基准做 `[System.IO.Path]::GetFullPath` 规范化解析）：`../../auto-money-system/index.md` → exists=**True**；`../../ai-one-person-micro-product/index.md` → exists=**True**（旧写法 `../` 两条实测仍为 False，反证修复方向正确）。
- 全束链接机械解析（自行编写，覆盖 `](相对.md)` 与束根惯例 `/references/...` 两类，跳过 http 与纯锚点）：**checked=23，broken=0**。根 index 的 2 条兄弟束链接仍为 True。

### P1-1：无据数字"60%" —— **已闭环 ✅**

- 02 篇 L74 反模式改为"只转文字层、漏掉图卡层——本文 38 条登记事实中 24 条（图 1-图 4，F-015~F-038）将整体缺失"，无据的"60%"已删除；24 条与 facts.md 登记说明（图卡层 F-015~F-038 共 24 条）一致。
- L65 同步改为"本文 38 条登记事实中 24 条来自图卡层（F-015~F-038，按条数约六成三）"。独立验算 24/38=0.6316，"六成三"正确且显式限定"按条数"口径，不再是内容占比断言。
- 全束复查：修复未引入任何新的 F 表外具体数字。

### P1-2：四处非逐字引号 —— **3 处闭环、1 处降级为 P2 残留**

- ✅ F-006 成本措辞：00 篇 L36 已改为分引"工具订阅费""零星外包"（两短语均为 F-006 原文逐字）；00 篇 L29/L58 与 verification L60 改为去引号转述（"刨除工具订阅费、零星外包小成本"），不再以引号冒充直引。
- ✅ F-037 年份：verification L59 现为作者称"我今年做到 180 万"（与 F-037 逐字一致），2026 移到引号外并标注"'今年'指 2026 系据 F-020、F-035 语境的推断，原文未直写年份"——推断与直引分离，处理正确。
- ⚠️ F-013 引语：00 篇 L61 现为"一对一咨询赚 3 万不如打包成 9.9 万标准化落地产品"。相较首轮版本补回了"落地"，但仍是 F-013 原文（"做一次一对一咨询赚 3 万，不如把整套流程打包成 9.9 万的标准化落地产品"）的拼接裁剪（脱"做一次""把整套流程""的"，非原文连续片段）。语义零失真、数字与核心措辞全部在原文中、紧邻 F-013 锚点、长度 24 字，按本束硬阈值（>40 字方为直引强约束）不构成违规，**降级为 P2-3 观察**（建议后续直接去引号转述，或逐字截取连续片段）。02 篇 L39"9.9 万标准化落地产品"脱"的"同列 P2-3。

### P2-1：语气词级引号裁剪 —— **01 篇全部回改到位；verification/00 篇残留少量压缩引号（P2，不阻断）**

- ✅ 01 篇逐项核对 F 表：L38"90% 的人把'一人公司'想简单了"与 F-015 逐字一致（内层引号恢复、"了"补回）；L49/L56"净亏损 7 万"与 F-023 逐字；L75"技术比自己强三倍"与 F-034 连续子串一致；L59 80% 句改为去引号转述；L90"已经在第三档上限了"补回"了"，与 F-037 逐字；L27/L28/L55/L73/L86/L50 各金句抽查均与 F-016/F-025/F-033/F-036/F-026 逐字或为连续子串。
- P2 残留（不改变裁决）：verification L62/L64 与 00 篇 L37 仍保留 4 处压缩组合引号（"2025 年 all in 做 12 个月""2026 前半年做抖音""今年 180 万""90% 的人想简单""80% 来自前 1% 老粉"），均为跨片段压缩、语义无损且紧邻 F 标注；同篇 01 已示范正确处理法（逐字或去引号），建议后续统一。省略号截引（verification L41/L42/L69）首末片段逐字，合规。

## 第二轮机械检查原始输出摘要（cwd=projects/awesome-okf-xs，本人亲自执行）

1. **P0 链接规范化 Test-Path**：`../../auto-money-system/index.md`=True、`../../ai-one-person-micro-product/index.md`=True；旧 `../` 两写法=False（对照）。
2. **全束 markdown 链接自写解析脚本**：checked **23** 条，broken **0**。
3. **check-utf8.py**：exit 0，`UTF-8 检查通过: 11556 个文件均为有效 UTF-8。`
4. **check-bundles-index.py**：exit 0，`bundles 总索引对账通过: 9 域 / 61 组 / 634 束，frontmatter、计数行、节标题、分组表、toctree 五面一致。`（计数当前态与首轮一致，修复未触碰索引计数）
5. **check-toctrees.py**：exit 1（仍为并行在途束与 3 个既存漂移束所致），grep `ai-solo-company-truth` 命中数 **0**。
6. **frontmatter 机械扫描**：6 个内容文件（根 index + 3 concepts + article-source + verification）必需键 type/title/description/tags/generated/verified/status: flagged/stale_after/sources 零缺失，根 index 含 okf_version；修复未损伤任何 frontmatter。
7. **concepts F 引用域复查**：三篇并集 32 个 F，越界=空、article 表查无=空（与首轮一致，修复未删坏引用）。
8. **敏感串/媒体/examples**：file 协议与家目录路径命中 0；图片/html 文件 0；examples 目录不存在。
9. **git 范围**：束内 9 文件清单不变（untracked），3 个索引 modified；无修复产生的杂散文件。

## AC 最新裁决（第二轮）

| AC | 类型 | 首轮 | 第二轮 | 变化依据 |
|---|---|---|---|---|
| AC-1 骨架定位 | rule | PASS | **PASS** | 无影响；9 文件、三 toctree、无 examples 复核不变 |
| AC-2 F 双份/分层 | rule | PASS | **PASS** | P1-1 闭环后 concepts 不再有任何 F 表外具体数字（"六成三"为明示口径的算术派生），原附带观察解除 |
| AC-3 P0 核验/flagged | rule | PASS | **PASS** | 四清单/五张力/五算术/flagged 落点不变；年份推断与直引分离后勘误表严谨度提升 |
| AC-4 原创/版权 | rule | PASS | **PASS** | 无长段直引、无图、无敏感路径；残留短引号均 ≤24 字且语义忠实，列 P2 |
| AC-5 索引/门禁 | rule | **FAIL** | **PASS** | P0-1 闭环：23/23 链接可达；官方三脚本本束零问题；计数 634/67/25 与 22 登记双轨维持自洽 |
| AC-6 知识转化质量 | rubric | 4 | **4**（阈值 4，通过） | 主要严谨性瑕疵（60%）已消除；未升 5 系因 00 L61 等 4 处压缩引号残留，距 5 分锚点的满格严谨仍差一档，与首轮评分尺度保持一致 |
| AC-7 OKF 规范符合度 | rubric | 4 | **4**（阈值 4，通过） | 断链这一主要扣分已修复、frontmatter 与先例体例零偏差；22/25 双口径无说明（P2-2，超本次范围）仍在，维持 4 |

## 第二轮残留清单（均 P2，不阻断；不要求本轮处理）

- **P2-3（新编号，承接 P1-2 残留）**：00 篇 L61 F-013 引语拼接裁剪（24 字，语义忠实）；02 篇 L39"9.9 万标准化落地产品"脱"的"。建议去引号转述或截连续原文片段。
- **P2-4**：verification L62/L64、00 篇 L37 共 4 处跨片段压缩引号（承接首轮 P2-1 未处理部分）；01 篇已有正确范例可参照。
- 首轮 P2-2（22 登记/25 磁盘双口径无跨层说明）、P2-3→现 P2-5（facts↔article 双份文案微差）、P2-4→现 P2-6（toctrees 81 vs 日志 82 数字漂移）维持原观察，均非本次修复责任。

## 第二轮最终结论

# ✅ PASS

- 规则项 AC-1~AC-5 全部 PASS（首轮唯一失败项 AC-5 已凭 P0-1 链接修复与 23/23 链接机械解析翻案）；rubric AC-6=4、AC-7=4，均达阈值 4。
- 阻断条件复查：无任一 rule AC 失败、无任一 rubric <4。
- 残留仅为 4+若干处 P2 级短引号压缩与既存索引双轨观察，不影响事实溯源、勘误完整性、版权安全与门禁可达性；已在上方逐条留痕，供后续日常打磨，不作为本知识包交付的阻断项。
