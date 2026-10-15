# WorkBuddy OPC 白皮书 OKF Wiki 知识包 - Independent Review

## 审查元信息

| 项 | 内容 |
|---|---|
| 审查时间 | 2026-10-15 |
| 审查者 | 独立对抗审查者（fresh context，只读） |
| 审查对象 | `projects/awesome-okf-xs/doc/bundles/sheke/industry/workbuddy-opc-whitepaper/`（14 个 Markdown）+ 本次三级索引 `sheke/industry/index.md`、`sheke/index.md`、`doc/bundles/index.md` |
| 仓库根 | `d:\spaces\SpecWeave` |
| 只读声明 | 本次审查**未修改任何被审文件**；未执行 `git commit`/`push`；未做任何"顺手修复"；唯一写入文件为本 `review.md` |
| 对照基准 | `spec.md`（AC-1~AC-7）、`tasks.md`（自验证据）、`facts.md`（357 条事实台账）、`.temp/workbuddy-opc/whitepaper.md`（32 页源文提取文本）、`.temp/workbuddy-opc/external-verification.md`（22 项外部核验原始记录）、先例束 `sheke/industry/ai-solo-company-truth`、`workbuddy-content-system`、`ai-one-person-micro-product`、`references/artifact-templates.md`（Review 模板） |
| 方法 | 通读 14 被审文件 + 基准;独立重跑机械检查（正则 F 集合比对、官方三脚本、自编链接解析脚本、敏感路径 Grep、frontmatter 扫描、三级索引计数、git status、定向 Sphinx dummy 构建）;逐 AC 独立裁决;实质性质证抽检（引文忠实性、数字回指、勘误落实、口径标签、verification 转述忠实度、log.md 与磁盘一致性） |

> 说明：先例束 `ai-solo-company-truth` 目录内**无 `review.md`**（仅 index/concepts/references/log），故先例体例比对以其 `index.md` 与 `concepts/00` 为准。

---

## 一、逐 AC 裁决

### AC-1：白皮书章节覆盖完整 — `rule` → **PASS**

独立证据（自跑）：
- 自编解析脚本读取 `references/source-manifest.md`，提取页级登记行 `^\|\s*页(\d+)\s*\|`：**32 行**，min=页1 / max=页32，`页1..32` 缺失集合 = `[]`、重复 = `[]`。双向差集为空。
- 六章归属齐备（第一~六章分别归 concepts/01~06）；封面与目录归 concepts/00；各章小结归 concepts/01–05；§3.5 数据说明 → concepts/03；§5.2 案例数据说明 → concepts/05；结语 → concepts/06（源文页32）。
- W0（SPA 壳页）与 P0/P1（静态制品）在台账「一、两条获取路径」表中显著区分；X1（PDF 母本）在台账**显式登记「未取得」**，未静默跳过。
- `check-toctrees.py` 通过（见机械摘要），页覆盖与源文 `<!-- ===== PAGE n ===== -->` 分页一致。

### AC-2：事实编号连续且可溯源 — `rule` → **PASS**

独立证据（自跑正则 `^\|\s*F-(\d{3})\s*\|`）：
- `facts.md` 与 `article-source.md` 各 **357** 条；`SET_EQUAL: True`；双向差集为空；`min=F-001 / max=F-357`；缺号 `[]`；重复 `0`；编号升序连续。
- 全束 `F-\d{3}` 引用：去重后 **357** 个，范围 1–357，越界 `[]`，且**全部存在于 facts 集合**（无悬空引用）。
- 每条 locator 统一为「页N · §x.y」；类型列取值实测分布 = 元信息 11 / 厂商自述 87 / 第三方研究口径 64 / 官方或协会口径 59 / 白皮书观点 113 / 合作邀约语汇 23，合计 357，全部落在允许集合内（`page_fact` 未单列，已由 facts.md §G1 显式说明）。F 表列数实测 6 列 / 357 行。
- 无 F 编号重排（自 F-001 起）。

### AC-3：口径分层与勘误准确 — `rule` → **PASS**

独立证据（自跑 Grep 计数 + 逐项定位）：
- 六类口径在 `verification.md` §二口径分层表**六行齐备**，且 concepts/00 §三给出「六类口径分层速查表」；全束口径标签计数：**厂商自述 124 / 受访者自述 36 / 单一来源 22 / 口号性 11 / 框架性 25 / 非已达成的合作事实 5 / 截至 2026 年 6 月 18**。
- 平台能力数字（235 专家 / 250 Skill / 86 能力）标**厂商自述**：concepts/04:92、index:28/70/78 均落标（F-215/216/218/220/241）。
- §4.4.1「20 个专家团」（F-218）vs §5.1「13 个核心专家团」（F-241）：concepts/04:94 与 concepts/05:30 均**并列表述 + 勘误 9/9a**，verification.md 勘误 9 附 §5.1 表内 13 行自洽清点。
- 三案例数字标**受访者自述（经 WorkBuddy 团队访谈核实）**：concepts/05 §三/§四、F-273~F-293 备注、F-297 声明，三处一致。
- 5%/10%/70%/15%（F-113~F-116）与「80% AI + 20% 品味」（F-064/083/118）标**单一来源/口号性表述**。
- 第六章合作模式表（F-331~F-335/338~340/343~345/348~349）保留「双方各自提供什么」**框架性邀约**，concepts/06 §五表头与页首提示均声明「非已达成的合作事实」。
- 政策与平台数字带**「截至 2026 年 6 月」**时点（18 处命中）。
- 收益/成效承诺扫描：仅命中「**不作**收益承诺/不得当作收益承诺」等**免责声明**，无实际收益承诺或把未证实成效写成确定结论的句子（concepts/06:123 结语复述带厂商自述标注）。
- **勘误落实核查**（重点抽检五项）：
  1. 朝阳「生产工具平台」：concepts/03:37 表内标 500 万 + `⚠️`，紧邻 note（03:47）给官方原文 **1000 万**；index:68/80 亦并列 → 正确值在正文出现，未照抄错值。
  2. 认证费：concepts/06:76 表内 800 元/次 + `⚠️`，note（06:80）给腾讯云现价 **¥330（原 ¥600）**。
  3. 联创存活率：concepts/04:37 正文 45%，勘误 6（04:39）并列「来源原文 **35%**、白皮书作 45%」。
  4. 存量数据时点：concepts/01:32 表头标「白皮书作『截至 2025 年底』」，勘误段（01:40）给出多来源正确时点 **「截至 2025 年 6 月」**。
  5. 专家团口径：concepts/04:94 与 concepts/05:30 并列 20 与 13。

### AC-4：三级索引与计数同步 — `rule` → **PASS**

独立证据（自跑）：
- `python scripts/check-bundles-index.py`（子模块根）：**退出码 0**，末行「9 域 / 61 组 / 639 束，frontmatter、计数行、节标题、分组表、toctree 五面一致」。
- `sheke/industry/index.md`：导航表行 = **26**、toctree 条目 = **26**、磁盘束（含 index.md） = **26**；新束行 `[workbuddy-opc-whitepaper](workbuddy-opc-whitepaper/index.md) | 7+3 | …` 与 toctree 条目 `workbuddy-opc-whitepaper/index` 均存在且可达。
- `sheke/index.md`：正文「**26 束**」、industry 行「（**26 束**）」同步。
- `doc/bundles/index.md` 五面：`total_bundles: 639` / 正文「**639 个知识包**」/ mermaid sheke 节点「**69 束**」/ 域节标题「**69 束**」/ industry 分组行「**26**」，与脚本输出逐项相等（639 / 69 / 26）。
- 基线说明：spec 记的基线为 637/68/25、预期本束增量 638/69/26；实测 `total_bundles=639`（working tree 编辑前已因并行在途变更处于 638），与 tasks.md TR-5.1 及 log.md 的「先读现值再 +1」说明一致；**索引写入值与脚本输出逐项相等**，未回退并行改动。
- `check-toctrees.py` 输出过滤本束名 **零命中**（已独立确认）。

### AC-5：机械门禁与独立审查 — `rule` → **PASS**

独立证据（自跑）：
- `python scripts/check-utf8.py`：**退出码 0**，末行「UTF-8 检查通过: 11651 个文件均为有效 UTF-8」。
- `check-toctrees.py`：**退出码 0**；输出中 `workbuddy-opc-whitepaper` 命中 **0**。
- 自编链接解析脚本（含 `../` 兄弟束与 concepts 内 `../../` 深度）：**checked=58 / broken=0**；4 条 `../<bundle>/index.md` 互链与 1 条 `../../ai-solo-company-truth/index.md` 均 Test-Path True。
- 敏感路径 Grep（本束 14 文件）：`file:///`、`C:\Users`、`/Users/`、`C:/Users` 实数命中 = **0 处真实路径**（唯一 1 行命中见 P2-2，系 log.md 对模式串的说明性列举）；另对本次 3 个索引独立 Grep = **0**。
- frontmatter 逐文件扫描：根 `index.md` 十键齐备（含 `okf_version`）；10 个内容文件九键齐备且**不含 `okf_version`**；`concepts/index.md`、`references/index.md`、`log.md` **无 frontmatter**；全部符合 NFR-1。
- 定向 Sphinx dummy 构建（子模块根 `python -m sphinx -b dummy -E doc _build/dummy`）：**退出码 0**，末行「build succeeded, 268 warnings」；含本束名的 **28 行全部为「正在读取源文件 / 正在写入输出」进度行**，**与本束相关的 ERROR/WARNING = 0**（全库 ERROR 55 行 / WARNING 184 行为其他束既存/并行问题）。
- 最新独立 Review 结果 = 本报告 `pass`。
- 未声称全库通过：全库告警与并行在途变更按归属隔离并如实记录（见 log.md 及本报告）。

### AC-6：教程可用性与知识分层质量 — `rubric` → **4 / 5（≥4，PASS）**

锚点理由：
- **明确高锚点3以上**：七篇各回答一个明确问题（concepts/index.md 表 + index 阅读路径）；趋势数据与厂商自宣**分层可辩**（口径标签全束一致落地，计数见 AC-3）；§4.4.1/§5.1 冲突**被显式处理**；三案例以「受访者自述」读法呈现；政策与平台数字带时点；含 2 张 Mermaid（concepts/04 OPC 三阶段 × WorkBuddy 三层承接图 + concepts/06 生态四维度链条图，实测 2 块）。
- **未完全达锚点5**：锚点5 要求的「含触发条件+核心步骤+反模式+迁移验证」四要素的**可迁移模式**未成形——concepts 仅出现结构层面的迁移讨论（concepts/05:132「可迁移的是其结构（品牌化+服务力+圈子杠杆、把个人经验沉淀为 Skill）」）与承接映射图，无独立命名的四要素模式小节（详见 P2-5，advisory）。
- 综合：内容齐备、口径分层可辩、冲突显式、案例读法正确、时点齐全，明显优于「洞察停留在复述」的 3 分档，但四要素可迁移模式缺位，取 **4/5**。

### AC-7：OKF 规范符合度 — `rubric` → **4 / 5（≥4，PASS）**

锚点理由：
- **明确高锚点3以上**：根 index 十键齐备（`okf_version` 仅在束根）；子文档九键齐备且不含 `okf_version`；`sources` 体例为「list of maps（id/resource/url）」与先例同款；`concepts/index.md`、`references/index.md` 采用 **toctree + 表格双轨**；`stale_after: 2026-12-31`、`status: flagged`、互链（4 条单向兄弟束互链 + 分工说明）符合先例惯例；读感与同组成熟束一致。
- **未满锚点5的微差**：`verified` 采用 **map 单值**形式（与先例 `workbuddy-content-system` 同款），而非 `ai-solo-company-truth`/`ai-one-person-micro-product` 的 **list** 形式；`at` 为日期（`2026-10-15`）而非 ISO 时间戳。属体例微差，非「明显参差」（详见 P2-6，advisory）。
- 综合取 **4/5**。

---

## 二、发现清单

### P0（阻断通过）— 0 条

无。

### P1（建议本轮闭环）— 0 条

无。

### P2（观察项）— 6 条

| ID | 位置 | 问题 | 可复现验证方式 | 建议修复方向 |
|---|---|---|---|---|
| P2-1 | `log.md:7` | 该句「类型仅用：元信息 / **page_fact** / 厂商自述 / …」把 `page_fact` 列为实际使用类型；实测 F 表类型分布无 `page_fact`（`facts.md` §G1 亦声明其「本表未单独使用」）。属 log 与数据/台账的措辞不一致 | 正则 `^\|\s*F-(\d{3})\s*\|` 提取类型列计数（无 `page_fact`）；对照 `facts.md:426` | 将 log 该句改为「实际使用六值（元信息/厂商自述/第三方研究口径/官方或协会口径/白皮书观点/合作邀约语汇），`page_fact` 未单列」 |
| P2-2 | `log.md:19` | 「敏感内容 Grep…四类**命中均为 0**」字面不实：`log.md` 自身第 19 行即含 `file:///`、`C:\Users`、`/Users/`、`C:/Users` 四个模式串，故对「14 文件」做朴素 Grep 会命中 1 行。**实质结论（无真实本机绝对路径引用）成立** | 对 14 文件 Grep 四模式 → 唯一命中行即 log.md:19 | 改为「除本文档对四类模式的说明性列举外，实际路径引用 0 处」 |
| P2-3 | `log.md:12` vs `log.md:23` | 两处「并行在途观测」措辞不一致：12 行（E 阶段）称「**未运行** `git status`…**未触碰任何**其他文件与共享索引」；23 行（V 阶段）称「**实际运行** `git -C … status --short`」并列出 3 索引改动与并行 WIP。最终态与磁盘一致，但同文件并列易误读 | 对照 `git -C projects/awesome-okf-xs status --short` 实测（见机械摘要） | 在 12 行显式标注其视角为「Task 4 E 阶段收尾时点」，或合并为单条累计观测 |
| P2-4 | `concepts/04:28`、`concepts/06:28` | 少量**短引非逐字**（均 < 40 字）：`「个人效率飞升，多人协作几乎没变」`（源文页17 作「…飞升，**但**多人协作几乎没变」）；腾讯研究院喻体引（源文页27 含逗号「组织能自上而下设计的**，**至多是让它生长的土壤」）。属标点/连词级毫厘差异，未超 FR-6「>40 字须严格逐字」阈值 | 对 `whitepaper.md` 归一化（去空白）后做子串比对，列出未逐字短引 | 如需严格逐字，补回「但」与逗号 |
| P2-5 | `concepts/*`（AC-6 相关） | 锚点5 要求的「触发条件+核心步骤+反模式+迁移验证」四要素**可迁移模式**未成形，仅有结构迁移讨论（concepts/05:132）与承接映射图（concepts/04 Mermaid）。属 advisory，AC-6 取 4/5 | Grep `触发条件|反模式|迁移验证|可迁移`（无四要素模式小节） | 可在 concepts/04 或 05 增设一节「OPC 三阶段 × 三层架构判读框架」，补齐四要素（触发条件/步骤/反模式/迁移验证） |
| P2-6 | 全束 frontmatter `verified`/`generated.at` | `verified` 为 map 单值（先例 `workbuddy-content-system` 同款），非 `ai-solo-company-truth` 的 list 形式；`at` 为日期而非 ISO 时间戳。属体例微差，AC-7 取 4/5 | 比对三先例 `index.md` frontmatter（见机械摘要） | 无强制修正；如需完全对齐"多数先例"可用 `verified: [{ by: …, at: … }]` 形式 |

---

## 三、机械检查原始输出摘要（本人亲自执行）

命令与结果数字（均在子模块根 `projects/awesome-okf-xs` 或仓库根执行；未引用任何他人结论）：

| # | 命令 / 脚本 | 结果 |
|---|---|---|
| 1 | 自编 Python：`facts.md` ↔ `article-source.md` 正则 `^\|\s*F-(\d{3})\s*\|` | facts=**357** min1 max357 dup0；article=**357** min1 max357 dup0；**SET_EQUAL=True**；双向差集 `[]`；缺号 `[]`；升序连续 True |
| 2 | 自编 Python：全束 `F-\d{3}` 引用 | 去重 **357**，范围 1–357，越界 `[]`，全部存在于 facts 集合（无悬空）。分文件去重：00=73/01=68/02=48/03=64/04=56/05=62/06=61，index=43，log=24，verification=104 |
| 3 | `python scripts/check-utf8.py` | **exit 0**；「UTF-8 检查通过: 11651 个文件均为有效 UTF-8」 |
| 4 | `python scripts/check-toctrees.py` | **exit 0**；过滤 `workbuddy-opc-whitepaper` → **0 命中** |
| 5 | `python scripts/check-bundles-index.py` | **exit 0**；「9 域 / 61 组 / **639** 束，五面一致」 |
| 6 | 自编链接解析脚本（含 `../`、`../../` 深度） | **checked=58 / broken=0**；跨束链接 16 条全部 True（含 4 条兄弟束 + 1 条 `../../`） |
| 7 | Grep `file:///`、`C:\Users`、`/Users/`、`C:/Users` | 14 文件：真实路径命中 **0**（唯一 1 行为 log.md:19 说明性列举）；3 索引：**0** |
| 8 | frontmatter 扫描（14 文件） | 根 index 十键（含 okf_version）；10 内容文件九键（无 okf_version）；3 个 index/log 无 frontmatter；缺失 `[]` |
| 9 | 非 .md 文件 / `examples/` 目录 | 非 .md = **0**；`examples/` = **False** |
| 10 | industry 索引计数 | 导航表行 **26** / toctree **26** / 磁盘束 **26** |
| 11 | `doc/bundles/index.md` 五面 | total_bundles **639** / 正文 **639** / mermaid sheke **69** / 域节标题 **69** / industry 行 **26**；`sheke/index.md` 正文与 industry 行均 **26** |
| 12 | page 覆盖（source-manifest） | 页级登记 **32** 行，页1–32 缺号 `[]`、重复 `[]` |
| 13 | Mermaid 块计数 | **2**（concepts/04、concepts/06 各 1） |
| 14 | F 表类型分布 | 元信息 11 / 厂商自述 87 / 第三方研究口径 64 / 官方或协会口径 59 / 白皮书观点 113 / 合作邀约语汇 23 = **357**；列数 6/357 |
| 15 | `git -C projects/awesome-okf-xs status --short` | 本次改动：M `doc/bundles/index.md`、M `doc/bundles/sheke/index.md`、M `doc/bundles/sheke/industry/index.md`、?? `…/workbuddy-opc-whitepaper/`；并行 WIP：M jishu 5 个索引 + ?? 2 个新束（与 log.md:23 披露逐项吻合） |
| 16 | Sphinx dummy 构建 `python -m sphinx -b dummy -E doc _build/dummy` | **exit 0**；「build succeeded, 268 warnings」；含本束名 **28 行全为读写进度行**，本束相关 ERROR/WARNING = **0** |
| 17 | 敏感标签 Grep（口径标签） | 厂商自述 124 / 受访者自述 36 / 单一来源 22 / 口号性 11 / 框架性 25 / 非已达成的合作事实 5 / 截至 2026 年 6 月 18 |
| 18 | 收益/承诺措辞扫描 | 仅命中免责声明（不作收益承诺等），**无**实际收益承诺 |

---

## 四、实质性质证覆盖说明（写明查了什么、多少条）

1. **中文引号短串忠实性**：从全束 14 文件抽取 `「…」` 短串，对源文提取文本归一化（去空白）后逐条比对 ——
   - **>40 字直引：0 条**（唯一 >40 字命中为 `log.md` 对 gate 输出 `bundles 总索引对账通过…` 的引用，系命令输出而非白皮书直引，合规）。
   - **未逐字且 ≥8 字的 `「」` 短串：95 条**；逐条判读后，**绝大多数为本知识包自身术语/口径标签**（如「单一来源/口号性表述」「厂商自述，截至 2026 年 6 月」「受访者自述（经 WorkBuddy 团队访谈核实）」）与**勘误描述**（如「最高不超过 **1000 万元**」「¥330（原 ¥600）」），非对白皮书的"直引"主张；仅 **2 条**属短引毫厘差异（P2-4）。
2. **数字回指 F 编号**：对 7 篇 concepts 逐行扫描「含数字但无 `F-` 引用」的行 → 命中行**全部**为 frontmatter / 元信息导语（页区间、`publishVersion: 4`）/ source-manifest 台账行，**无任何未登记编号的具体数字声明**。另按任务要求聚焦抽核 ≥20 个关键数字（1,600 万家、27.4%、286 万户、+47%、23.8%、570 万家、+42%、34%、7%、7,290 万、23.7%→36.3%、约 -80%、95%、96%、87%、20%-40%、2-10 倍、92%、1:72、8-10 倍、A 轮 3,000 万/2.5 亿/1,060 万/8,700+/周增 9%、5/10/70/15%、20 个 vs 13 个、235/250/86、60 个工作流、3.3 亿、60%、800 元、¥330 原 ¥600、71 套设计系统、3,000 万训力券、50 万㎡、2,500 工位、500 万 vs 1000 万），**逐项均可回指存在的 F 编号且 F 编号在双份表中确实存在**。
3. **勘误落实为正确值**：五项重点勘误（朝阳 500/1000 万、认证 800/¥330·原600、联创 45/35%、存量 2025 年底/2025-06、专家团 20/13）**逐一核查** —— 正确值**均在正文/紧邻 note/index 速查表中出现**，且以 `⚠️` 标记并链接核验报告；**未发现照抄白皮书错值而无更正**的情形（详见 AC-3 证据）。
4. **口径标签全文一致落地**：厂商自述 / 受访者自述（经厂商团队访谈核实）/ 单一来源或口号性 / 政策数字带 2026-06 时点 / 第六章「厂商框架性邀约，非已达成的合作事实」五类标签计数与落点逐类抽验（见 AC-3）；**未发现收益承诺或把未证实成效写成确定结论的句子**。
5. **`verification.md` 转述忠实度**：抽取其 **31** 个 URL 与 `external-verification.md` 的 **79** 个 URL 做集合比对 —— 仅 2 个 URL（W0 分享页 / P0 制品，来自本束自身 frontmatter 的 `sources`）不在外部记录中，**非编造**；其余 29 个全部见于外部原始记录。核验结论计数一致（✅14/⚠️8/❌0/❔0）；「未核到」项（8,700+/周增 9%/True Ventures 领投/《法治日报》/《财经》/杭州 2 万㎡/江苏苏州/80% 独角兽/100+ 领域专家/¥330）在 verification 中均**如实保留为「未核到/口径不符」**，未夸大为「已证实」。**未发现夸大、编造 URL 或把「未核到」写成「已证实」**。
6. **`log.md` 与磁盘一致性**：门禁结论（三脚本 exit 0、UTF-8 11651、639 束、F 357=357、链接 58/0、敏感 0、Sphinx 0 本束告警）与本人实测**逐项吻合**；未提交声明（未 `commit`/`push`）与 `git status` 一致；并行在途观测与 `git status` 实测吻合。**未发现对最终状态的谎报**（3 条措辞精度问题见 P2-1/2/3）。
7. **制品/目录**：束内**无** `examples/`、**无非 .md 制品**、**无原图入库**；bundle `description` 含「**非操作教程**」（index.md:5）。

---

## 五、最终结论

- **Result**: `pass`
- **逐 AC 汇总**: AC-1 `rule` PASS ｜ AC-2 `rule` PASS ｜ AC-3 `rule` PASS ｜ AC-4 `rule` PASS ｜ AC-5 `rule` PASS ｜ AC-6 `rubric` 4/5 PASS ｜ AC-7 `rubric` 4/5 PASS
- **阻断条件复查**：
  - 任一 `rule` AC 失败 → **无**（AC-1~AC-5 全部 PASS，均有本次独立重跑证据）；
  - 任一 `rubric` < 4 → **无**（AC-6=4、AC-7=4，均达阈值）；
  - 「证据不可得」（环境/权限/依赖）→ **无**（Python/Sphinx 8.2.3/官方三脚本/git 均可用并已实跑）；
  - 存在 actionable（P0/P1）发现 → **无**（仅 6 条 advisory P2，均为措辞/体例精度，不阻断）。
- 结论：**`pass`**。6 条 P2 属 advisory，可选择性优化，不构成本轮阻断。

---

## Review History

### Review R1
- **Result**: `pass`
- **Checks Performed**: 通读 14 被审文件 + spec/tasks/facts/先例/源文/外部核验；独立重跑 F 集合比对、官方三脚本、自编链接解析、敏感路径 Grep、frontmatter 扫描、三级索引计数、`git status`、定向 Sphinx dummy 构建；实质性质证（引文忠实性 95+ 短串、数字回指 ≥20 项、五项勘误落实、口径标签、verification 转述忠实度、log.md 一致性）。
- **Evidence**: 见本报告「三、机械检查原始输出摘要」与「四、实质性质证覆盖说明」。
- **Checkpoint Results**: CP-AC-1~CP-AC-5 (`rule`): `pass`；CP-AC-6 (`rubric`): `pass`，score 4；CP-AC-7 (`rubric`): `pass`，score 4。
- **Findings**: P0=0；P1=0；P2=6（P2-1~P2-6，均 advisory，见「二、发现清单」）。
- **Recommended Issues**: 无（pass，无可行动发现）。P2 项如后续维护可择机优化。
