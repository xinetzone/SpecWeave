# 数字经济与数字资产 OKF 教程束 - Independent Review

> **终态 Result（Review R2，2026-10-17）：`pass`** —— 首轮 5 项发现（F-1~F-5）经本轮全新上下文复审全部修复；终态判定与独立证据见文末「第二轮检查点（Review R2）」与「终态 Result」。

> 评审者：C 门 fresh-context 只读子代理（此前未参与本变更的规划与实施）
> 评审日期：2026-10-17
> 比对基准：本目录 `spec.md`（AC-1 ~ AC-7）与 `tasks.md`（Task 1 ~ Task 10）
> 结论口径：所有结论均来自本轮评审者自跑命令与自行枚举；实施者自验（tasks.md / log.md 中的陈述）**不作为证据采信**
> 命门约束：本项目禁止运行 `sphinx-build`（主会话正在跑全量 dummy 构建，避免争用 `_build`）——该项证据由**主会话提供**，已在下方标明

- [ ] CP-R1: 每条 F 事实的**信源标注**可追到对应 S 编号信源，且 P0 级错引 = 0
  - **Type**: `rule`
  - **Covers**: AC-1, TR-1.1, TR-3.1, TR-8.1, TR-10.2
  - **Result**: `fail`
  - **Independent Evidence**:
    - 自写枚举器解析两束 `facts.md` 表格行并逐条对照 `.trae/specs/digital-economy-okf-wiki/raw/` 四份 R 草案：
      `python -X utf8 - <<枚举器>>`（自写，无第三方依赖）
      → 束 1：F 编号 82 条、连续无跳号、无重复；束 2：F 编号 90 条、连续无跳号、无重复。
    - **内容一致性（数字 / 文号 / 日期 / 机构 / 口径标注）：172/172 条全部与 raw 草案一致，0 处不一致**（如 `F-014 国家统计局令第 33 号 / 2021-05-14 通过 / 2021-05-27 公布`、`F-033 127555 亿元 / 9.9%`、`F-035 140891 亿元 / 10.5%`、`F-082 银发〔2021〕237 号 / 成文 2021-09-15 / 公开 2021-09-24`、`F-055 UST 0.9964→0.7934 / 5-9 最低 0.60 / Terra 171.7 亿 + Luna 207.7 亿美元`、`F-022 财会〔2023〕11 号 / 成文 2023-08-01 / 施行 2024-01-01` 等，均可回溯到 R-A A-20/A-24/A-25、R-D D-17/D-33/D-34、R-C C-28）。
    - **抽样覆盖面**：束 1 核验 82 条（要求 ≥12）、束 2 核验 90 条（要求 ≥13）；按内容文件的 F 引用清单逐文件比对，26 篇内容文档每篇被引 F 号中**至少 2 条**落入核验集合（例如 `digital-asset/concepts/07` 引 F-073/074/075/085/088，全部已核）。
    - **信源标注命中率**：168/172 = **97.67% < 98%**，且存在 **4 条 P0 级错引（要求 = 0）**——见 Finding F-1、F-2。
  - **Findings**: F-1（可行动，P1）、F-2（可行动，P1）

- [x] CP-R2: 四类口径分歧均有独立留痕段且每类 ≥2 个出处
  - **Type**: `rule`
  - **Covers**: AC-2, TR-1.3, TR-2.2
  - **Result**: `pass`
  - **Independent Evidence**:
    - 束 1 `facts.md` L140–192「口径冲突与勘误」7 段：勘误 1（信通院 53.9 万亿/42.8% vs 统计局 140891 亿/10.5%，出处 S23/S24 与 S2/S3）、勘误 2（10.5% vs 10.4% vs「10% 左右」，3 出处）、勘误 3（130816 vs 127878 亿元）、勘误 4（全球口径多范围）、勘误 5（要素表述）、勘误 6（时点差）、勘误 7（二手年份）——**每段均 ≥2 出处并给出「采用口径」**。
    - 束 2 `facts.md` L158–219「口径冲突与勘误」：勘误 1 四方监管定性对照表（中国境内/香港/欧盟/美国 × 7 主题，出处 S28/S53/S57/S56）、勘误 2（稳定币市值 4 出处 S40/S41/S52/S51）、勘误 3（加密市值 3 出处）、勘误 4（可入表≠增值）、勘误 5（境内外不混同）、勘误 6（文号年份倒挂）、勘误 7（已证伪误记表）。
    - 对照 spec AC-2 列明的四类分歧（测度三口径 / 占比年际与口径差 / 加密监管四方分歧 / 稳定币储备与脱锚口径）→ **4/4 覆盖，且每类 ≥2 出处**。
    - 正文侧佐证：束 1 `concepts/02-measurement-framework.md` L37–49 三口径对照表；束 2 `concepts/05-stablecoins.md` L38–70、`concepts/09-risks-and-redlines.md` L53–65、`examples/03-jurisdiction-comparison-table.md` L20–30。
  - **Findings**: 无

- [x] CP-R3: 三门禁 rc=0，且总索引计数五面对账一致
  - **Type**: `rule`
  - **Covers**: AC-3, TR-7.1, TR-7.2, TR-8.1
  - **Result**: `pass`
  - **Independent Evidence**（cwd = `d:\spaces\SpecWeave\projects\awesome-okf-xs`，本轮评审者实跑）:
    - `python scripts/check-toctrees.py` → `toctree 检查通过: 全部 index.md 引用有效，所有内容文档均可达。` **rc=0**
    - `python scripts/check-bundles-index.py` → `bundles 总索引对账通过: 9 域 / 62 组 / 644 束，frontmatter、计数行、节标题、分组表、toctree 五面一致。` **rc=0**
    - `python scripts/check-utf8.py` → `UTF-8 检查通过: 11751 个文件均为有效 UTF-8。` **rc=0**
    - **独立重算计数三角**（自写递归口径枚举器，不引用 gate 结论）：`DOMAINS 9 / GROUPS 62 / BUNDLES 644`；`SHEKE groups 9 / bundles 72 / digital-economy = 2` → 与总索引 frontmatter（`total_bundles: 644`、`groups: 62`、`domains: 9`）、计数行「当前共 **644 个知识包**……**9 个技术域、62 个分组**」、sheke 节标题「### 👥 [社会科学](sheke/index.md) · 72 束 · 9 组」、sheke 分组表「`[💠 数字经济与数字资产（Digital Economy）](sheke/digital-economy/index.md) | 2 |`」**四面对齐**。
    - 变更面一致性：41 个 Markdown 文件（分组 index 1 + 束 2×20），`TOTAL_FILES 41 / MD 41 / NON_MD []`；与 spec FR-1~FR-3 一致。
    - `sphinx-build -b dummy -E doc _build/dummy` **由主会话提供证据**（本评审按约束未执行，避免与主会话争用 `_build` 目录）——该子项未由本评审独立复现。
  - **Findings**: 无（遗留风险 R-1 记录该子项依赖主会话证据）

- [x] CP-U1: 教程教学质量（概念定义清晰度 / 知识地图连贯性 / 跨篇导航有效性 / 非专业读者可跟读至形成判断）
  - **Type**: `rubric`
  - **Covers**: AC-4, TR-4.3, TR-5.4, TR-6.3, TR-9.2
  - **Scale**: 1–5
  - **Anchors**: 1 = 文件摘录堆砌无叙事；3 = 覆盖定义与制度但跨篇跳跃、概念不作辨析；5 = 每篇含「是什么 / 为什么重要 / 制度与数据现状 / 边界与争议」，概念谱系有辨析、示例可独立走读
  - **Pass Threshold**: >= 4
  - **Result**: `pass`
  - **Independent Evidence**（独立阅读 6 篇概念 + 2 篇示例，两束各半）:
    - 束 1：`concepts/01-conceptual-lineage.md`、`concepts/02-measurement-framework.md`、`concepts/09-controversies-and-boundaries.md`、`examples/01-reading-scale-datasets.md`
    - 束 2：`concepts/00-positioning-and-lineage.md`、`concepts/05-stablecoins.md`、`concepts/09-risks-and-redlines.md`、`examples/03-jurisdiction-comparison-table.md`
    - 逐维度评分与理由：
      | 维度 | 分数 | 理由 |
      |---|---|---|
      | 概念定义清晰度 | **5** | G20 / 国家统计局 / OECD-IMF 三套定义并列并指出「关键要素由知识和信息→数据资源」的唯一差别（`concepts/01` L22–24）；「数字资产」三口径对照表给出典型对象、制度依据、会计适用、监管适用四列（`concepts/00` L49–55）；稳定币三类储备与「类货币↔投资工具」连续谱（`concepts/05` L23–25）。定义均带原文措辞与 F 编号括注 |
      | 知识地图连贯性 | **5** | 每束有 00 定位页 + `insights.md` 知识地图 + 束根「推荐学习路径」；束 1 内部「锚定口径 → 看结构 → 定坐标 → 读懂数字 → 看制度 → 守怀疑」链条（`digital-economy/index.md` L78–88）；两束分工（宏观/统计 vs 制度细节/形态边界）显式声明，并以 F-080 跨束导流 |
      | 跨篇导航有效性 | **5** | 每篇结尾「相关文档」段给出上一篇/下一篇/事实出处/信源索引（26/26 篇命中，见 CP-R5）；`concepts/index.md` 与 `examples/index.md` 提供表格式篇目索引与阅读建议；核对演练 `examples/01` 直接回链 `concepts/02`、`concepts/07` |
      | 非专业读者可跟读至形成判断 | **4** | 示例层「三件套规则」「误用情景清单」「怀疑点清单」可让非专业读者独立形成判断（`examples/01` L26–65、`concepts/09` L48–57）；扣分项：数字资产束加密侧（储备赎回、代币化、法域分层）需读者自带一定金融制度常识，且四方法域对照表信息密度高，零基础读者需按「快速开始」路径引导阅读方可达标 |
    - **总分：19 / 20（均分 4.75），≥ 4，判 `pass`**
  - **Findings**: 无

- [x] CP-R4: 合规与风险边界 4/4 满足、0 处推荐性表述
  - **Type**: `rule`
  - **Covers**: AC-5, TR-5.2, TR-5.3
  - **Result**: `pass`
  - **Independent Evidence**（`digital-asset/` 全量扫描 + 束 1 根 index）:
    - ① **两束根 `index.md` 均含声明**：束 1 `index.md` L26「本包为通识教育材料，不构成投资建议……」+ L75「不推荐任何产品或平台」；束 2 `index.md` L26「**不评价任何币种或平台的优劣与投资价值，不推荐任何产品、平台或币种，不预测价格**……不构成投资建议、法律意见或合规意见」。
    - ② **中国境内监管红线逐条登记（文号 + 机构 + 日期）**：`concepts/09-risks-and-redlines.md` L27–35 七行登记表——银发〔2013〕289 号 / 五部门 / 2013-12-03；94 公告（未见公开文号）/ 七部门 / 2017-09-04；三协会公告 / 2021-05-18；金融委第五十一次会议 / 2021-05-21；央行约谈 / 2021-06；发改运行〔2021〕1283 号 / 11 部门 / 落款 2021-09-03、发布 2021-09-24；银发〔2021〕237 号 / 十部门 / 成文 2021-09-15、公开 2021-09-24。
    - ③ **e-CNY 与加密货币 / 稳定币的区别明确辨析**：`concepts/06-ecny-digital-yuan.md` L39（与加密资产：法币 vs 无主权信用担保）、L45（与稳定币）、L49（与第三方支付）三组辨析，且 L23 引白皮书原文；束 2 `facts.md` 勘误 7 表内单列「e-CNY 与比特币、稳定币同为加密资产」误记纠正。
    - ④ **境内外口径并列不混同**：`concepts/05-stablecoins.md` L58–74「三个法域的制度安排并列陈述，不混同、不拼接为『全球监管趋同』」+「中国境内口径（并列陈述）」；`concepts/08-rwa-and-defi.md` L65；`concepts/09` L53–65 四方表 + L97「不得反向推导」；`examples/03` L18 与 L44–51 使用纪律（含「技术可行性 / 境外监管可行性 / 境内合规可行性」三层区分）。
    - **推荐性表述扫描**：`grep 推荐|值得投资|建议购买|首选|值得入手|买入|投资价值高` 命中 15 行，**逐行核验全部为否定式（「不推荐」「不评价」）或导航标题「推荐学习路径」**——0 处推荐产品/平台/币种。
    - 附带核验：`concepts/index.md` 与 `examples/index.md`（两束）均含免责提示。
  - **Findings**: 无

- [x] CP-R5: 工程纪律机械扫描 0 违例
  - **Type**: `rule`
  - **Covers**: AC-6, TR-4.1, TR-5.1, TR-6.1（部分）, TR-7.2
  - **Result**: `pass`
  - **Independent Evidence**（自写枚举器全量扫描 41 个文件）:
    - `TOTAL_FILES 41 / MD 41`；`NON_MD []`（无图片等静态资产，与 Non-Goals「不新增 `_static/` 资产」一致）。
    - **中文文件名**：`CJK_FILENAMES []`（41 个文件名均 kebab-case 纯英文）。
    - **重复 H1**：`H1_NOT_ONE []`——每文件恰 1 个 `# ` 一级标题。
    - `file:///` 命中 0；`.temp/` 命中 0；`.spec/` 命中 0。
    - **结尾导航段**：26 篇内容文件（20 concepts + 6 examples）全部含 `## 相关文档` 结尾段（`MISSING_NAVSECTION []`）。
    - **子目录索引无 frontmatter**：`concepts/index.md`、`examples/index.md`（×2 束，共 4 个文件）首字符检查 `starts_with_---: False`，均为纯 toctree + 表格索引。
    - **链接全量枚举**：`LINK_COUNTS {'root': 242, 'rel': 167}` 共 409 条 → **`BROKEN_COUNT 0`、`OUTSIDE_DOCBUNDLES []`**（`/`-根链接按束根解析、相对链接按文件所在目录解析，全部落到真实文件且**无一条越出 `doc/bundles/`**）。
    - **交叉引用一致性**：束内 `/`-根引用（如 `/concepts/09-risks-and-redlines.md`、`/facts.md`）全部可解析；跨束引用（`../../digital-economy/index.md`）解析到真实文件；无 `../` 越界。
  - **Findings**: F-3（advisory，P2——束内相对路径与 NFR-1/AC-6 字面判据的关系，详见下方）

- [ ] CP-R6: V 门（G1–G5）与 C 门双独立评审收口，`review.md` 终态 Result = pass
  - **Type**: `rule`
  - **Covers**: AC-7, TR-9.1, TR-10.1
  - **Result**: `fail`（因 CP-R1 fail，链条未收口）
  - **Independent Evidence**:
    - V 门回填已核查：`verified: [{ by: "process:okf-v-gate", at: "2026-10-17T19:50:00+08:00" }]` 命中 **30/30** 内容文件（20 concepts + 6 examples + 2 facts.md + 2 insights.md），**4 个子目录 index / 2 束根 index / 2 log / 2 references 共 10 个文件 0 命中**（禁用清单符合规范）。
    - Task 10 修复落点抽验：`digital-asset/references/01-sources-and-authorities.md` 中指向概念的链接采用 `../concepts/...` 形式且解析成功（P0-1 断链确已修复——本评审全量链接枚举 0 断链可独立佐证）。
    - `tasks.md` 队列状态核对：Task 1–6 = `completed`，**Task 7 = `pending`、Task 8 = `pending`、Task 9 = `pending`、Task 10 = `in_progress`**，而 Task 7/8 的产出（41 文件 + 三级索引 + 三门禁 rc=0）已实际存在并被本评审实测通过——状态字段与实际不符。
    - **C 门本轮结论为 `fail`**（存在可行动发现 F-1、F-2），故 AC-7 的「终态 Result = pass」未达成；按模板须将 F-1、F-2 固化为 pending issue → 修复 → 复审至 pass。
  - **Findings**: F-1、F-2（阻塞收口）、F-4（advisory，队列状态未同步）

## Findings

| ID | 类型 | 严重级 | 位置 | 复现 | 期望结果 |
|---|---|---|---|---|---|
| **F-1** | `actionable` | **P1** | `digital-asset/facts.md` **L123 / L124 / L125**（F-067 / F-068 / F-069） | `grep -n '^\| F-06[789] \|' digital-asset/facts.md` → 三条均标信源 `S31`；而同文件信源登记表 **L254 定义 S31 = 国务院金融稳定发展委员会第五十一次会议新闻稿（2021-05-21，打击比特币挖矿和交易行为）**、**L255 定义 S32 = 中国人民银行《中国数字人民币的研发进展》白皮书（2021-07-16）**。F-067 正文明确写「中国人民银行 2021-07 发布《中国数字人民币的研发进展》白皮书」，其唯一正确信源是 **S32**。 | 三条的 S 编号改为 **S32**（或 S32 主引 + 必要旁证），并复核同段其他 e-CNY 事实的 S 映射；回归要求：`facts.md` 内每条 F 所标 S 编号与其正文所指文件/机构一致，P0 错引 = 0 |
| **F-2** | `actionable` | **P1** | `digital-asset/facts.md` **L128**（F-072） | F-072 正文为「2022-04-02 人民银行召开数字人民币研发试点工作座谈会……新增……6 个城市为试点地区」，却标信源 `S32`（白皮书，2021-07-16）。白皮书早于该会议 9 个月，无法支撑该事实；束 2 信源登记表内**没有任何 S 编号对应这次座谈会**（R 草案中对应条目为 R-D D-47，信源 S-D08，未进入落库台账）。 | 补登对应信源（征求意见原文或人民银行公告，注明机构与日期）并改正 F-072 的 S 编号；若无法取得，按 Assumptions 的「⚠️ 双源登记 / 单源标注」处理并显式注明。回归要求同上 |
| **F-3** | `advisory` | **P2** | 束内 6 个索引/台账文件（两束 `concepts/index.md`、`examples/index.md`、`references/01-sources-and-authorities.md`） | 自写枚举器：束内相对路径引用 `digital-economy/concepts/index.md` 15 处、`digital-economy/examples/index.md` 11 处、`digital-economy/references/01-sources-and-authorities.md` 4 处；`digital-asset/concepts/index.md` 17 处、`digital-asset/examples/index.md` 10 处、`digital-asset/references/01-sources-and-authorities.md` 4 处（如 `[01 入表](../concepts/01-data-asset-capitalization.md)`、`[facts.md](../facts.md)`、同目录 `00-positioning-and-lineage.md`）。**26 篇内容文件全部使用 `/`-根路径，仅索引/台账文件使用相对路径。** 样板束实测：`sheke/finance/personal-investing` 相对同级 92 处、`../` 36 处、`/`-根仅 3 处。 | NFR-1/AC-6 字面要求「束内引用一律 `/`-根路径」，与样板束事实判据相互矛盾。二选一：①将这 6 个文件的束内引用统一为 `/`-根式；②按 2026-10-17 跨束判据澄清的先例，把 AC-6 判据修正为「允许相对路径，但必须解析到 `doc/bundles/` 内真实文件且不得越界」（本评审实测：409 条链接 0 断链、0 越界，该修正后判据可满足）。**不建议维持字面判据与样板冲突的现状** |
| **F-4** | `advisory` | **P2** | `tasks.md`（Task 7 / 8 / 9 状态字段、Task 10 状态） | Task 7/8 标 `pending`（漏标 `completed`），Task 10 标 `in_progress` 而 9 项修复均已落点（本评审链接枚举可佐证 P0-1 已修）。Task 9 标 `pending`，本轮评审即为 Task 9 执行体。 | 收口时同步 `tasks.md` 状态与 `Completion Evidence`，使队列状态与实际一致 |
| **F-5** | `advisory` | **P2** | `digital-asset/facts.md` **L287 说明段** 与 `digital-asset/concepts/06-ecny-digital-yuan.md` **L54** | 说明段称「F-072 的 mBridge 相关事实（发起方、MVP 阶段与 BIS 移交）见 S62」，但 **F-072 正文完全不含 mBridge 内容**；R 草案 D-48/D-49（mBridge 发起 2021-02、MVP 2024-06-05、BIS 2024-10 移交）**未登记为任何 F 编号**，故 S62 在 `facts.md` 无事实级引用。`concepts/06` L54 按该说明把 mBridge 指向「facts.md 对 F-072 的说明与信源 S62」，形成指向空处的引用链。另：信源登记表 **S5（L228）、S48（L271）** 除登记表本身外无任何引用。 | 二选一：①补登 mBridge 的 F 事实（含 S62）并修正 L287 说明与 `concepts/06` L54 的指称；②若有意不展开 mBridge，则删除 L287 说明、改 `concepts/06` L54 的引用落点，并评估 S5/S48/S62 是否保留在台账（保留则建议标注「背景信源，未直接支撑事实行」） |

## Review History

### Review R1
- **Result**: `fail`
- **Reviewer**: C 门 fresh-context 只读子代理（未参与规划与实施）
- **时间**: 2026-10-17（Asia/Shanghai）
- **材料**: `spec.md`、`tasks.md`、`.agents/skills/TRAE-spec-mode/references/artifact-templates.md`、`raw/R-A~R-D` 四份 R 草案、`projects/awesome-okf-xs/scripts/check-toctrees.py`、`check-bundles-index.py`、`check-utf8.py`、41 个产出文件、样板束 `sheke/finance/personal-investing`
- **Checks Performed**（全部由本轮评审者自跑，未采信实施者自验）:
  1. 自写枚举器：文件清单与总数、中文文件名、每文件 H1 数、禁用引用（`file:///`/`.temp/`/`.spec/`）、结尾导航段、子目录索引 frontmatter
  2. 自写枚举器：F 编号连续性 / 重复 / 跳号；S 登记表条目数与连续性；P0 标记条数；每条 F 的 S 引用与「未被引用的 S」清单
  3. 自写枚举器：409 条 Markdown 链接全量解析（`/`-根按束根、相对按文件目录），断链与外溢检测；束内相对路径逐文件计数
  4. 复跑三门禁（cwd = `projects/awesome-okf-xs`）：`check-toctrees.py` / `check-bundles-index.py` / `check-utf8.py`，均为 **rc=0**
  5. 自写递归口径枚举器重算计数三角：9 域 / 62 组 / 644 束；sheke 72 束 / 9 组；digital-economy 2 束
  6. G2 事实抽核：束 1 全量 82 条、束 2 全量 90 条逐条对照 `raw/` 四份草案（数字 / 文号 / 日期 / 机构 / 口径）
  7. AC-5 合规扫描：数字资产束全量「推荐性表述」扫描与逐行定性；境内监管逐条登记核验；e-CNY 辨析核验；境内外并列不混同核验
  8. AC-4 教学质量：独立阅读 6 篇概念 + 2 篇示例（两束各半）并按四维 rubric 打分
  9. V 门证据核查：`verified` 字段命中分布（30/30 内容文件）；Task 10 修复落点抽验；`tasks.md` 队列状态核对
- **Evidence**: 见各检查点 `Independent Evidence`；
  **未复跑项**：`sphinx-build -b dummy -E doc _build/dummy`（按任务约束避免与主会话争用 `_build`）——**该证据由主会话提供**。
- **Checkpoint Results**:
  - CP-R1 (`rule`): `fail` — 172 条事实内容一致性 100%，但信源标注 168/172 = 97.67% < 98%，且 P0 级错引 4 条（≠0）
  - CP-R2 (`rule`): `pass`
  - CP-R3 (`rule`): `pass`（dummy 构建子项由主会话提供证据）
  - CP-U1 (`rubric`): `pass` — 总分 **19/20**（均分 4.75），四维：5 / 5 / 5 / 4
  - CP-R4 (`rule`): `pass`
  - CP-R5 (`rule`): `pass`（伴随 1 条 advisory）
  - CP-R6 (`rule`): `fail`（受 CP-R1 阻塞 + 队列状态未同步）
- **Recommended Issues**:
  - Issue I-1：e-CNY 段信源错引（F-067/068/069 → S32；F-072 补登对应信源）——priority high，关联 AC-1 / CP-R1 / F-1 / F-2，回归要求：`facts.md` 每条 F 的 S 标注与其正文所指文件一致、P0 错引 = 0
  - Issue I-2：束内引用判据与样板一致性收敛（统一为 `/`-根式 或 澄清 AC-6 判据）——priority medium，关联 AC-6 / CP-R5 / F-3，回归要求：三门禁 rc=0 且全量链接枚举 0 断链、0 越界
  - Issue I-3：mBridge 事实与 S62 引用链、S5/S48 台账归属收敛——priority medium，关联 AC-1 / AC-6 / F-5
  - Issue I-4：`tasks.md` 队列状态与 Completion Evidence 同步——priority low，关联 AC-7 / F-4

## 总体 Result

**`fail`**

判定依据（按 artifact-templates.md 不变量）：CP-R1 与 CP-R6 未通过，存在 ≥1 条可行动发现（F-1、F-2），每条失败检查点均已映射到可行动发现并给出待固化的 pending issue。**注：`fail` 归因于信源标注错误与收口链条未闭合，而非内容质量或门禁问题**——172 条事实的数字 / 文号 / 日期 / 机构全部与 R 阶段原始草案一致，三门禁 rc=0、6 项工程纪律扫描 0 违例、合规边界 4/4、教学质量 rubric 4.75，均为高质量产物。

## 遗留风险

- **R-1**：`sphinx-build -b dummy -E doc _build/dummy` 未由本评审独立复现（避免与主会话争用 `_build`）；本检查点对 Sphinx 侧的完整性结论**依赖主会话证据**。若主会话报告存在来自本分组（`sheke/digital-economy`）的警告，则 AC-3 需重新判定。
- **R-2**：`raw/` 草案中标注为「单源」的条目（如 R-C C-44 贵阳/深圳交易所日期、R-D D-25 央行约谈、R-D D-54 元宇宙风险提示）在落库时虽保留了「单源/媒体转引」标注，但**官方原文仍未补齐**；若后续官方口径更新，相关 F 事实需复核。
- **R-3**：`facts.md` 中带「待核 / 未确证」标记的条目（如 F-044 引用的《公共数据资源授权运营实施规范（试行）》无文号与日期、F-082 对应《数字经济增加值核算方法》全文未公开）属**已声明的已知缺口**，不构成本轮缺陷，但应在 `stale_after`（2027-09-30）前补齐或降级。
- **R-4**：本变更未执行任何 git 提交（`projects/awesome-okf-xs` 为 git submodule），修复后需再次复审并显式获得用户提交指令。

---

## 第二轮检查点（Review R2 · 复审，2026-10-17）

> 本轮为**全新上下文的独立复审者**（未参与 R1、规划与实施）。以下每条均给出本轮**自跑命令 / 自写枚举器**所得证据；**不采信 R1 结论与 tasks.md 自述**。
> 首轮 5 项发现逐条复核结论（本轮独立验证）：
> - **F-1 已修复**：`digital-asset/facts.md` L123/L124/L125（F-067/F-068/F-069）信源现为 **S32**（人民银行《中国数字人民币的研发进展》白皮书，2021-07-16），与 raw R-D D-41/D-42/D-43（信源 S-D07）一致；S31 仍在正确位置——L152 的 **F-086** 信源为 S31（金融委第五十一次会议，raw D-24/S-D06）。
> - **F-2 已修复**：S 台账存在 **S63** 条目（`digital-asset/facts.md` L286、`references/01-sources-and-authorities.md` L63；raw R-D D-47/S-D08），F-072 信源现为 **S63、S62**（L128）。全束 S 范围表述**逐一核过、无 S1–S62 残留**：`facts.md` L19（说明段"挂 S1–S38、S63"/"S39–S58"/"S59–S62"）、L220（登记表标题「S1–S63」）、`references` L4(description)、L17（"63 个信源"）、L20/L67/L93（三层标题）、`index.md` L14/L51/L55、`log.md` L13、`concepts/00` L70、`concepts/index.md` L25、`tasks.md` L62——均为 S1–S63（`tasks.md` L209 出现的"S1–S62 扩为 S1–S63"系对修复动作的描述，非现存范围）。
> - **F-5 已修复**：F-072 正文（L128）已并入 mBridge 三点（2021-02 联合发起 / 2024-06-05 进入 MVP、沙特加入 / 2024-10 BIS 移交，raw D-48/D-49）；说明段 L288 改为"S62↔F-072 跨境部分、S63↔座谈会"的准确分工，**不再空指**；`concepts/06-ecny-digital-yuan.md` L54 的 `[facts.md 对 F-072 的说明与信源 S62](/facts.md)` 解析成功（`/facts.md` 存在）。
> - **F-3 已修复**：`spec.md` L50（NFR-1「相对路径澄清（2026-10-17 C 门澄清）」，允许同目录清单/台账类文件用同级相对路径、正文导航仍强制 `/`-根路径）与 L123（AC-6「跨束引用澄清」，允许 `../` 但不得越出 `doc/bundles/`）均已写入。与样板束实测一致——自写枚举器计 `sheke/finance/personal-investing`：`root=3 / rel=128 / up(../)=36`，与 spec 引用的"相对同级 92、`../` 36"同向（相对路径为主）。
> - **F-4 已修复**：`tasks.md` L131 Task 7 = `completed`、L156 Task 8 = `completed`、L188 Task 10 = `completed`，均带 Completion Evidence；Task 9 = `pending`（L174，即本轮 C 门执行体，收口后应置 `completed`）；Task 1–6 = `completed`，与实测产出（41 文件、三级索引、三门禁 rc=0）一一对应。

- [x] CP-R1′: 每条 F 事实信源可追 S 编号、P0 级错引 = 0（AC-1、TR-1.1、TR-3.1、TR-8.1、TR-10.2）
  - **Type**: `rule`
  - **Result**: `pass`
  - **Independent Evidence**（自写枚举器 + 逐条对照 `raw/R-A~R-D`）:
    - 束 1：F 编号 **82 条**（F-001~F-082），连续、无跳号、无重复；【P0】标记 **42 条**。束 2：F 编号 **90 条**（F-001~F-090），连续、无跳号、无重复；【P0】标记 **56 条**。
    - S 台账：束 1 = **S1–S43（43 条，无缺号/重复）**；束 2 = **S1–S63（63 条，无缺号/重复）**。
    - 原 4 条 P0 级错引已修正（见上「F-1 / F-2 已修复」）。抽样覆盖两束全部 172 条事实的「内容 ↔ S」对照：束 1 对照 R-A/R-B/R-C（如 F-014 令第33号/S1、F-033 127555亿/9.9%/S2、F-035 140891亿/10.5%/S3、F-064 53.9万亿/42.8%/S23、F-073 10.4%/S43）；束 2 对照 R-C/R-D（F-022 财会11号/S6、F-072 S63+S62、F-080 银发〔2013〕289/S26、F-082 237号/S28、F-084 1283号/S29、F-086 S31、F-090 S53/S56/S57）。
    - **信源标注命中率（本轮独立重算）= 170 / 172 = 98.84% ≥ 98%**；**P0 级错引 = 0**（172 = 82 + 90）。未命中的 2 条为**非 P0** 的未披露替代信源（F-011、F-013），详见 advisory **A-1**。
  - **Findings**: A-1（advisory，P2）

- [x] CP-R2′: 四类口径分歧独立留痕、每类 ≥2 出处（AC-2、TR-1.3、TR-2.2）
  - **Type**: `rule`
  - **Result**: `pass`
  - **Independent Evidence**:
    - 束 1 `facts.md` L144–192「口径冲突与勘误」7 段：勘误 1（信通院 53.9 万亿/42.8% [S23/S24] vs 统计局 140891 亿/10.5% [S2/S3]）、勘误 2（10.5% / 10.4% /「10% 左右」3 出处）、勘误 3（130816 vs 127878 亿元）、勘误 4（全球口径多范围）、勘误 5（要素表述「知识信息」vs「数据资源」）、勘误 6（时点差）、勘误 7（二手年份）——每段 ≥2 出处并给「采用口径」。
    - 束 2 `facts.md` L162–218：勘误 1（中/港/欧/美四方监管定性对照，出处 S28/S53/S57/S56）、勘误 2（稳定币市值 4 出处 S40/S41/S52/S51）、勘误 3（加密市值 4 出处 S43/S44/S45）、勘误 4（可入表≠增值）、勘误 5（境内外不混同）、勘误 6（文号年份倒挂）、勘误 7（已证伪误记表）。
    - 对照 spec AC-2 列明四类分歧（测度三口径 / 占比年际与口径差 / 加密监管四方分歧 / 稳定币储备与脱锚口径）→ **4/4 覆盖，且每类 ≥2 出处**。
  - **Findings**: 无

- [x] CP-R3′: 三门禁 rc=0 + 计数三角对账一致（AC-3、TR-7.1、TR-7.2、TR-8.1）
  - **Type**: `rule`
  - **Result**: `pass`
  - **Independent Evidence**（cwd = `projects/awesome-okf-xs`，本轮实跑）:
    - `python scripts/check-toctrees.py` → `toctree 检查通过: 全部 index.md 引用有效，所有内容文档均可达。`（**rc=0**）
    - `python scripts/check-bundles-index.py` → `bundles 总索引对账通过: 9 域 / 62 组 / 644 束，frontmatter、计数行、节标题、分组表、toctree 五面一致。`（**rc=0**）
    - `python scripts/check-utf8.py` → `UTF-8 检查通过: 11751 个文件均为有效 UTF-8。`（**rc=0**）
    - **独立重算计数三角**（自写枚举器，复现 `check-bundles-index.py` 的锚点/导航/叶子束递归口径，不引用 gate 结论）：`DOMAINS 9 / GROUPS 62 / BUNDLES 644`；`SHEKE groups 9 / bundles 72`；`digital-economy` 分组含 `digital-economy`、`digital-asset` 2 束。与 `doc/bundles/index.md` 的 frontmatter（`total_bundles: 644`/`groups: 62`/`domains: 9`）、计数行、sheke 节标题（72 束 · 9 组）、分组表「束数 2」四面对齐。
    - 变更面：`TOTAL_FILES 41 / MD 41 / NON_MD []`（分组 index 1 + 束 2×20）。
    - **Sphinx：由主会话提供证据**——`_build/build_dummy.log` 存在（约 1.60 MB），含 `build succeeded, 30 warnings.`（L12012）；本轮统计 **WARNING 行恰 30 条**，逐条归属 `jishu`（free-llm-api-roundup 5 条、myst-tutorial 2 条等），`grep 'WARNING.*(sheke|digital-economy|digital-asset)'` → **无匹配**；**来自 `sheke/digital-economy` 的警告数 = 0**。
  - **Findings**: 无

- [x] CP-U1′: 教程教学质量 rubric（AC-4、TR-4.3、TR-5.4、TR-6.3、TR-9.2）
  - **Type**: `rubric`；**Scale**: 1–5；**Pass Threshold**: ≥4
  - **Result**: `pass`；**总分 19 / 20（均分 4.75）**
  - **Independent Evidence**（独立阅读两束 00/02/05/06/09 概念共 8 篇 + 2 篇示例，逐维度自评）:
    | 维度 | 分 | 理由 |
    |---|---|---|
    | 概念定义清晰度 | **5** | `digital-asset/concepts/00` L47–55 三口径对照表给出「典型对象/主要制度依据/会计适用/监管适用/价值判断」五列；`concepts/05` L23–25 稳定币三类储备 + 「类货币↔投资工具」连续谱；`concepts/06` L37–49 三组辨析逐组带 F 编号；`digital-economy/concepts/02` L41–47 三口径对照表（发布机构/口径名/时点/数值/可否混用） |
    | 知识地图连贯性 | **5** | 每束有 00 定位页 + `insights.md` + 束根「推荐学习路径」；束 1 链条「打地基→看结构→定坐标→读懂数字→看制度→守怀疑」（`digital-economy/index.md` L80–88）；两束分工显式（`digital-asset/concepts/00` L74）并以 F-080 跨束导流 |
    | 跨篇导航有效性 | **5** | 26 篇内容文件 **26/26** 均含 `## 相关文档` 结尾段（枚举器 `NAV_MISSING []`）；`concepts/index.md`、`examples/index.md` 提供表格式篇目索引；`examples/01` 回链 `concepts/02`、`concepts/07` |
    | 非专业读者可跟读至形成判断 | **4** | `examples/01`「三件套规则+误用情景清单」、`concepts/09-risks`「非法金融活动识别 7 点」、`examples/03`「使用纪律勾选」可让非专业读者独立走读；扣分项：加密侧（储备赎回、代币化、法域分层）需读者自带一定金融制度常识，四方七主题表信息密度高，零基础读者需按「快速开始」路径引导 |
    - 总分 **19/20 = 4.75 ≥ 4**，判 `pass`（与 R1 同分，但由本轮独立阅读与打分得出）。
  - **Findings**: 无

- [x] CP-R4′: 合规与风险边界 4/4、0 处推荐性表述（AC-5、TR-5.2、TR-5.3）
  - **Type**: `rule`
  - **Result**: `pass`
  - **Independent Evidence**（全束扫描）:
    - ① **两束/分组 index 均含声明**：`digital-asset/index.md` L26、`digital-economy/index.md` L26、分组 `index.md` L18；`concepts/09` L93、`concepts/05` L79、`concepts/07` L79、`concepts/08` L65、`examples/02` L18、`examples/03` L18、两束 `concepts/index.md` 与 `examples/index.md` 免责提示齐备。
    - ② **中国境内监管红线逐条登记（文号+机构+日期）**：`digital-asset/concepts/09-risks-and-redlines.md` L27–35 七行——银发〔2013〕289 号/五部门/2013-12-03；94 公告（未见公开文号）/七部门/2017-09-04；三协会公告/2021-05-18；金融委第五十一次会议/2021-05-21；央行约谈/2021-06；发改运行〔2021〕1283 号/11 部门/落款 2021-09-03、发布 2021-09-24；银发〔2021〕237 号/十部门/成文 2021-09-15、公开 2021-09-24。
    - ③ **e-CNY 与加密资产/稳定币区别明确**：`concepts/06` L39（与加密资产：法币 vs 无主权信用担保）、L45（与稳定币）、L49（与第三方支付）三组辨析；L41 复述勘误 7「e-CNY≠加密资产」。
    - ④ **境内外口径并列不混同**：`concepts/05` L60–74（三个法域制度并列「不混同、不拼接为全球监管趋同」+ 中国境内口径并列）、`concepts/09` L53–65 四方表与 L97「不得反向推导」、`examples/03` L18 与 L22–30、L44–51 使用纪律（含「技术可行性/境外监管可行性/境内合规可行性」三层区分）。
    - **推荐性表述扫描**（自写枚举器，`推荐|值得投资|建议购买|首选|值得入手|买入|投资价值高`）：命中 **20 行**，逐行定性**全部为否定式**（「不推荐」「不评价」）或导航标题「推荐学习路径」——**0 处推荐产品/平台/币种/价格**。
  - **Findings**: 无

- [x] CP-R5′: 工程纪律机械扫描 0 违例（AC-6、TR-4.1、TR-5.1、TR-6.1）
  - **Type**: `rule`
  - **Result**: `pass`
  - **Independent Evidence**（自写枚举器全量扫描 41 文件）:
    - `TOTAL_FILES 41 / MD 41 / NON_MD []`；中文文件名 `CJK_NAMES []`；每文件恰 1 个 `# ` H1（`H1_BAD []`）。
    - `file:///` 命中 **0**；`.temp/` 命中 **0**；`.spec/` 命中 **0**。
    - 26 篇概念/示例内容文件**全部**含 `## 相关文档` 结尾段（`NAV_MISSING []`）；`concepts/index.md`、`examples/index.md`（×2 束，共 4 文件）均**不带 frontmatter**（`SUBDIR_INDEX_HAS_FM []`）。
    - **链接全量枚举**：`root 242 + rel 167 = 409` 条 → **`BROKEN 0`、`OUTSIDE 0`**（`/`-根按束根解析、相对按文件目录解析，全部落真实文件，**无一条越出 `doc/bundles/`**）。
    - 判据一致性：spec.md NFR-1/AC-6 澄清与样板束 `sheke/finance/personal-investing`（root 3 / rel 128 / up 36）方向一致。
  - **Findings**: 无

- [x] CP-R6′: V 门（G1–G5）与 C 门双独立评审收口、`review.md` 终态 Result = pass（AC-7、TR-9.1、TR-10.1）
  - **Type**: `rule`
  - **Result**: `pass`
  - **Independent Evidence**:
    - V 门回填核查：`verified: [{ by: "process:okf-v-gate", at: "2026-10-17T19:50:00+08:00" }]` 命中 30 个内容文件（20 concepts + 6 examples + 2 facts + 2 insights），10 个禁用类文件（子目录 index / 束根 index / log / references）0 命中。
    - Task 10 修复落点抽验：`digital-asset/references/01-sources-and-authorities.md` L102 `[04 加密资产基础](../concepts/04-crypto-assets-basics.md)` 解析成功（原缺 `../` 已修）；本轮全量链接枚举 0 断链可独立佐证。
    - 首轮 CP-R1（fail）与 CP-R6（fail）的成因均已消解：4 条 P0 级错引修正、命中率回升至 98.84%≥98%、`tasks.md` 状态同步、F-5 引用链可解析。
    - **本 `review.md` 终态 Result = `pass`**，满足 AC-7 的 Pass Condition。
  - **Findings**: 无

## 终态 Result

**`pass`**

判定依据（artifact-templates.md 不变量）：第二轮 6 个检查点（CP-R1′–CP-R6′，覆盖 AC-1~AC-7）**全部通过**；每条 AC 均有本轮独立证据；首轮 4 条可行动发现（F-1~F-5，其中 F-1/F-2 为 P1）**经本轮独立复核已全部修复**；无残留可行动发现，仅有 advisory（见下）。

## 遗留风险（R2 更新）

- **R-1**：`sphinx-build -b dummy -E doc _build/dummy` 未由本评审独立复现（按任务约束避免与主会话争用 `_build`）；本轮已**核对主会话证据文件** `_build/build_dummy.log` 存在、含 `build succeeded, 30 warnings.`，且 30 条 WARNING **无一来自 `sheke/digital-economy`**，与 AC-3 结论一致。
- **R-2**：`raw/` 中标注「单源/转引」的条目（如 R-C C-44 贵阳交易所日期、R-D D-25 央行约谈、R-D D-54 元宇宙风险提示）落库时保留了来源性质标注，但**官方原文仍未补齐**；若官方口径更新需复核相应 F 事实。
- **R-3**：`facts.md` 中「待核/未确证」条目（如 F-044 依据的《公共数据资源授权运营实施规范（试行）》无文号日期、F-082 对应《数字经济增加值核算方法》全文未公开）属**已声明的已知缺口**，非本轮缺陷，应在 `stale_after`（2027-09-30）前补齐或降级。
- **R-4**：本变更未执行任何 git 提交（`projects/awesome-okf-xs` 为 git submodule）；收口后提交需用户显式指令。

## 建议性（advisory）发现

| ID | 类型 | 严重级 | 位置 | 复现 | 期望结果 |
|---|---|---|---|---|---|
| **A-1** | `advisory` | **P2** | `digital-asset/facts.md` **L42（F-011）/ L44（F-013）** | 自写对照器：F-011 正文「国家发展改革委答记者问称……」标信源 **S2**（`references` L25 = 中国政府网转载刘鹤 2019 署名文章《坚持和完善社会主义基本经济制度》）；F-013 正文「淡化所有权、强调使用权」亦标 **S2**。两处对应的 raw R-C 原始信源为 **S-C04（发改委答记者问，2022-12-19）**，该信源**未登记入束 2 台账**（套件内无对应 S 编号）。 | 两条为**非 P0** 一般事实，未披露的替代信源；建议补登 S-C04（发改委答记者问）并将 F-011/F-013 改挂该编号，或将 S2 明确标注为「背景/相关信源」。仅影响理念类陈述的可溯源精度，不涉及数字与文号 |
| **A-2** | `advisory` | **P2** | 两束若干条（束 1 F-025/F-050/F-054 等；束 2 F-032/F-045 等） | 自写对照器：这些事实采用「Sxx（相关：<真实来源名>）」的**披露式替代信源**写法，所标 S 编号与括号内所述来源**并非同一文件**（如束 1 F-050「S18（相关：中国政府网）」、束 2 F-045「S18（相关：国家信息中心研究）」）。因已显式披露，可溯源，未计入命中率失配。 | 属可接受的软性做法；若要更严，可补登括号所指原文件并按其真实 S 编号挂载，或统一改为「背景信源」标注 |
| **A-3** | `advisory` | **P2** | `digital-asset/facts.md` **L271（S48）** | 信源台账登记 S48（FATF《FATF Report to the G20 on So-called Stablecoins》2020-07），但全束无任何 F 事实引用该编号。 | 保留于台账无害；建议在 `references` 中标注为「背景信源，未直接支撑事实行」，避免读者误判为漏引 |
| **A-4** | `advisory` | **P2** | 束 2 的 S 分层归属（`facts.md` L19 vs `references` L4/L20） | `facts.md` 说明段将国际组织/境外官方口径列为「S39–S58」，即把 **S39（新华网）** 归入国际组；而 `references` description 与分层标题将 **S39（新华网）** 归入中国法律与官方组（「S1–S39、S63」）。两处对同一编号的分组归属表述不一致。 | 统一 S39 的三层归属表述（新华网属中国侧官方转载），仅表述一致性，不影响任何事实的信源指向 |
| **A-5** | `advisory` | **P3** | `tasks.md` **L174（Task 9）** | Task 9（C 门独立评审与收口）Status 仍为 `pending`，而本轮即为该 Task 的执行体。 | 收口时置为 `completed` 并补 Completion Evidence |

## Review History 追加

### Review R2
- **Result**: `pass`
- **Reviewer**: C 门 fresh-context 只读子代理（第二轮，未参与 R1、规划与实施）
- **时间**: 2026-10-17（Asia/Shanghai）
- **Checks Performed**（全部由本轮评审者自跑，未采信 R1 与 tasks.md 自述）:
  1. 自写枚举器：文件清单与总数、中文文件名、每文件 H1 数、`file:///`/`.temp/`/`.spec/`、结尾导航段、子目录索引 frontmatter
  2. 自写枚举器：F 编号连续性/重复/跳号、S 台账条目数与连续性、P0 标记条数
  3. 自写枚举器：409 条 Markdown 链接全量解析（`/`-根按束根、相对按文件目录），断链与外溢检测
  4. 复跑三门禁（cwd=`projects/awesome-okf-xs`）：`check-toctrees.py` / `check-bundles-index.py` / `check-utf8.py`，均 **rc=0**
  5. 自写递归束口径枚举器重算计数三角：9 域 / 62 组 / 644 束；sheke 9 组 / 72 束
  6. 对照 `raw/R-A~R-D` 逐条复核两束 172 条事实的「内容 ↔ S 编号」，重算信源标注命中率
  7. AC-5 合规扫描：推荐性表述逐行定性、境内监管逐条登记、e-CNY 辨析、境内外并列不混同
  8. AC-4 教学质量：独立阅读 8 篇概念 + 2 篇示例并按四维 rubric 打分
  9. 核对主会话构建证据 `_build/build_dummy.log` 与 30 条 WARNING 的目录归属；抽样样板束 `sheke/finance/personal-investing` 链接惯例
- **Evidence**: 见各检查点 `Independent Evidence`；**未复跑项**：`sphinx-build`（按约束）——该项由主会话提供，本轮已核对日志文件存在且内容支持结论。
- **Checkpoint Results**:
  - CP-R1′ (`rule`): `pass` — 命中率 170/172 = 98.84% ≥ 98%，P0 级错引 = 0
  - CP-R2′ (`rule`): `pass`
  - CP-R3′ (`rule`): `pass`（dummy 构建子项由主会话提供证据，已核对无本分组警告）
  - CP-U1′ (`rubric`): `pass` — 总分 **19/20**（均分 4.75），四维：5 / 5 / 5 / 4
  - CP-R4′ (`rule`): `pass`
  - CP-R5′ (`rule`): `pass`
  - CP-R6′ (`rule`): `pass`
- **Findings**: A-1 ~ A-5（均为 advisory，无 actionable；P0/P1 级 = 0）
- **Recommended Issues**: 无（无 pending issue 需固化；A-1~A-5 为可选优化项，不阻塞收口）

---

## 第三轮检查点（Review R3 · 用户指令「修复 F-011/F-013 替代信源标注」复审，2026-10-17）

> 本轮为**全新上下文的独立复审者（第三轮）**——未参与 R1、R2、规划与实施。以下每条均给出本轮**自跑命令 / 自写枚举器**所得证据；**不采信 R1/R2 结论与 `tasks.md` 自述**。
> 修复目标（用户 2026-10-17 指令）：新增信源 **S64**（国家发展改革委答记者问，2022-12-19），F-011/F-013 由 S2 改挂 S64；台账由 S1–S63 扩为 **S1–S64** 并同步全部 S 范围表述。

### A. 本次修复是否落地（逐条判定）

1. **S64 双处落点且互相一致 → 已修复**
   - `digital-asset/facts.md` **L287**：`| S64 | 国家发展改革委 | 《构建数据基础制度 更好发挥数据要素作用——国家发展改革委负责同志答记者问》（「数据二十条」的官方解读口径） | 2022-12-19 | https://www.ndrc.gov.cn/xxgk/jd/jd/202212/t20221219_1343696_ext.html |`
   - `digital-asset/references/01-sources-and-authorities.md` **L64**：同上（机构/文件名/日期/链接**逐字段一致**）。
   - 自写枚举器交叉核对：`facts.md` 台账 SI 集合 == `references` 台账 SI 集合（`set_equal True`，64 项）。

2. **S64 与 raw `R-C-data-factor.md` 的 S-C04 一致 → 已修复（非新造来源）**
   - raw `S-C04`（L13）：`国家发展改革委 | 构建数据基础制度 更好发挥数据要素作用——国家发展改革委负责同志答记者问 | 2022-12-19 | https://www.ndrc.gov.cn/xxgk/jd/jd/202212/t20221219_1343696_ext.html`。
   - 比对结论：**机构、文件名、日期、链接四项与 raw 完全一致**，S64 为 raw 既有信源的落库，**非实施方新造**。

3. **F-011 / F-013 改挂 S64，S2 仍在正确位置 → 已修复**
   - `facts.md` **L42**：`| F-011 | 国家发展改革委答记者问称「数据二十条」为全球第一份系统构建数据基础制度的政策文件（官方评价性口径，单源）。| S64 |`（对应 raw `C-06`，信源 S-C04）。
   - `facts.md` **L44**：`| F-013 |「数据二十条」产权思路为「创新数据产权观念，淡化所有权、强调使用权」（该表述出自国家发展改革委答记者问对文件的解读，而非《意见》条文原文）。| S64 |`（对应 raw `C-16`，引文/备注「官方答记者问口径」；正文补注与 raw 一致）。
   - S2 仍在正确位置：`facts.md` **L39** F-008（十九届四中全会《决定》数据增列生产要素）信源 = **S2**（raw `C-01` / S-C02 刘鹤署名文章）。**F-011/F-013 已不再标 S2**。
   - 正文陈述与 S64 实际内容相符：F-011 ↔ raw C-06「发改委答记者问称数据二十条为全球第一份系统构建数据基础制度的政策文件」；F-013 ↔ raw C-16「淡化所有权、强调使用权」——**逐字核对一致**。

4. **S64 编号连续、分类归属自洽 → 已修复**
   - 自写枚举器：`digital-asset/facts.md` S 台账 `count 64, min 1, max 64, contig True, dupes False`（无缺号、无重复）。
   - S64 归入「一、中国法律与官方信源（S1–S39、S63、S64）」层（references L20 标题 / facts.md 说明段①），机构为国家发展改革委 → **中国官方层，自洽**。

5. **`facts.md` 说明段三层区间与 `references` 分层一致 → 已修复（并解决了 R2 遗留 A-4 的一半）**
   - `facts.md` **L19**：①中国法律法规与政策事实（…）挂 **S1–S39、S63、S64**；②国际组织与境外官方口径（…）挂 **S40–S58**；③技术与标准事实（…）挂 **S59–S62**。
   - `references` description（L4）与分层标题（L20/L68/L94）为 **S1–S39、S63、S64 / S40–S58 / S59–S62** → **两处分层逐项一致**（S39 新华网同归中国官方层，R2 A-4 指出的归属不一致已消解）。

6. **全局 S 范围表述零残留 → 已修复**
   - 自写枚举器 grep 整个 `doc/bundles/`（不止本分组）：**交付物中无 `S1–S63` / `S1–S62` 等过期范围表述**；出现的范围仅 `S1–S64`（digital-asset）与 `S1–S43`（digital-economy，本束自属范围）、以及其它既有知识包各自的范围。
   - 本分组内 S1–S64 表述落点（两束齐全、逐一核对）：`digital-asset/facts.md` L19（说明段）、L220（登记表标题）、L289（尾注说明）；`digital-asset/references` L4（description）、L17（「64 个信源」）、L20/L68/L94（三层标题）；`digital-asset/index.md` L14/L51/L55；`digital-asset/log.md` L13；`digital-asset/concepts/00` L70；`digital-asset/concepts/index.md` L25。
   - **spec 工作区历史行（只追加不改写，不算残留）**：`.trae/specs/digital-economy-okf-wiki/tasks.md` 中的「S1–S62 扩为 S1–S63」「S1–S62」等**系对历轮修复动作的审计记录**（Task 10 / Task 9 证据段），属历史留痕，**不计入交付物残留**；本轮已按要求**未改动** tasks.md。

7. **未引入新问题 → 未引入新问题**
   - F 段未变：自写枚举器 `digital-economy F 82（F-001~F-082，连续无重复）/ digital-asset F 90（F-001~F-090，连续无重复）`。
   - P0 未变：`digital-economy 42 / digital-asset 56`（合计 98）。
   - 三门禁 rc=0、链接 0 断链 0 越界（见 B 段）。
   - 新观察（非本轮修复引入，见 advisory）：① `digital-asset/facts.md` **F-010**（L41）标 `S1、S2`，其第二信源 S2 与正文不对应——raw `C-05` 的对应第二信源为 **S-C04（即本轮新增的 S64）**；② `digital-economy` 束根 `index.md` **L24**「82 条事实、**41 个信源**」与 facts.md/references 的 **S1–S43（43 个信源）**不一致（疑为 P2-6 新增 S42/S43 后的残留计数）。

### B. 独立重算数据（自跑命令 / 自写枚举器，不引用他人数字）

- **文件清单**：`TOTAL_FILES 41 / MD 41 / NON_MD []`（分组 index 1 + 束 2×20）；`CJK_NAMES []`；`H1_BAD []`（每文件恰 1 个 `# `）；26 篇内容文件 `NAV_MISSING 0`（`## 相关文档` 结尾段齐全）。
- **F 段**：digital-economy **F-001~F-082（82 条，连续、无跳号、无重复）**；digital-asset **F-001~F-090（90 条，连续、无跳号、无重复）**。
- **S 台账**：digital-economy **S1–S43（43 条，连续、无缺号、无重复）**；digital-asset **S1–S64（64 条，连续、无缺号、无重复）**；两束 `facts.md` 与 `references` 台账 SI 集合相等。
- **P0 条数**：digital-economy **42** / digital-asset **56**。
- **计数三角（自写递归枚举器，复现 check-bundles-index 口径）：`DOMAINS 9 / GROUPS 62 / BUNDLES 644`；`SHEKE groups 9 / bundles 72`；`digital-economy 分组 bundles 2`** → 与总索引 frontmatter、计数行、sheke 节标题、分组表束数列四面一致。
- **链接全量枚举**：`root 242 + rel 167 = 409` 条 → **`BROKEN 0`、`OUTSIDE 0`**（`/`-根按束根解析、相对按文件目录解析，全部落真实文件且无一条越出 `doc/bundles/`）；`file:/// = .temp/ = .spec/ = 0`。
- **三门禁（cwd = `d:\spaces\SpecWeave\projects\awesome-okf-xs`，本轮实跑）**：
  - `python scripts/check-toctrees.py` → `toctree 检查通过: 全部 index.md 引用有效，所有内容文档均可达。` **rc=0**
  - `python scripts/check-bundles-index.py` → `bundles 总索引对账通过: 9 域 / 62 组 / 644 束，frontmatter、计数行、节标题、分组表、toctree 五面一致。` **rc=0**
  - `python scripts/check-utf8.py` → `UTF-8 检查通过: 11751 个文件均为有效 UTF-8。` **rc=0**
- **Sphinx 构建证据（主会话提供；本评审按约束未运行 sphinx-build）**：核对 `_build/build_dummy2.log` **存在**（1,635,523 字节，11,886 行）。自统计 `WARNING:` 行 **恰 30 条**，归属目录为 `jishu/ai/learning/free-llm-api-roundup`、`jishu/document/myst/myst-tutorial`、`wenxue/english/english-grammar`——**来自 `sheke/digital-economy` 的 WARNING = 0**；日志尾部含 `build succeeded, 30 warnings.`（成功标志）。
- **信源标注命中率（本轮独立重算）**：对两束 F 行逐条核「事实内容 ↔ 所标 S 编号」（对照 `raw/R-A~R-D` 四份草案的原始信源）：
  - **按「主信源可对应即计命中」（R1/R2 采用口径）= 172 / 172 = 100%**（R2 = 170/172 = 98.84% → **提升**，提升项恰为 F-011、F-013）。
  - **按「每条所标 S 均须与内容对应」的严格口径 = 171 / 172 = 99.42%**，唯一存疑项为 **F-010 的次信源 S2**（详见下方 advisory **A-6**）。两种口径**均 ≥98%**，**P0 级错引 = 0**。
  - 抽样覆盖：digital-asset 全量 90 条逐条对照 `R-C`+`R-D`；digital-economy 全量 82 条对照 `R-A`+`R-B`+`R-C`（覆盖全部 26 篇内容文档，每篇被引 F 号均落入核验集合）。

### C. AC-1 ~ AC-7 逐条终态判定（本轮独立证据）

- **AC-1 事实可溯源 → `pass`**：172 条事实的数字/文号/日期/机构与 raw 一致；命中率 ≥98%（本轮 100%/99.42% 双口径），**P0 级虚构/错引 = 0**；F-011/F-013 错挂已修正。
- **AC-2 口径冲突显式留痕 → `pass`**：束 1 `facts.md` 勘误 1–7、束 2 `facts.md` 勘误 1–7（含四方监管对照表、稳定币 4 出处、加密市值 4 出处、已证伪误记表）；对照 spec 四类分歧 **4/4 覆盖、每类 ≥2 出处**。
- **AC-3 结构与门禁全绿 → `pass`**：三门禁 rc=0；计数三角四面一致；`_build/build_dummy2.log` 含 `build succeeded, 30 warnings.` 且来自本分组的警告 **0** 条。
- **AC-4 教程教学质量（rubric）→ `pass`**：本轮独立评分 **19/20**（见 D 段）。
- **AC-5 合规与风险边界 → `pass`**：4/4 满足、0 处推荐性表述（见 E 段）。
- **AC-6 工程纪律 → `pass`**：0 处 `file:///`、0 处 `.temp/`/`.spec/`、0 中文文件名、无重复 H1；26 篇内容文件结尾导航段齐全；子目录索引不带 frontmatter；409 条链接 0 断链、0 越界（判据按 spec NFR-1/AC-6 的 2026-10-17 澄清执行）。
- **AC-7 双独立评审收口 → `pass`**：V 门（G1–G5）已回填 `verified`（30 内容文件命中）；本 `review.md` 由 C 门全新上下文第三轮评审产出，**终态 Result = `pass`**。

### D. AC-4 独立评分（1–5，四维度）

| 维度 | 分数 | 理由（本轮独立阅读） |
|---|---|---|
| 概念定义清晰度 | **5** | 三套定义并列并点出唯一差别（`digital-economy/concepts/02` 三口径对照表 L41–47「发布机构/口径名称/统计时点/2024 数值/可否混用」）；`digital-asset/concepts/00` 三口径对照表 L49–55；稳定币「类货币↔投资工具」连续谱（`concepts/05` L23–25）。定义均带原文措辞与 F 编号括注。 |
| 知识地图连贯性 | **5** | 每束有 00 定位页 + `insights.md` 知识地图 + 束根「推荐学习路径」；束 1 链条「打地基→看结构→定坐标→读懂数字→看制度→守怀疑」（`digital-economy/index.md` L80–88）；两束分工显式（`digital-asset/concepts/00` L74），并以 F-080 跨束导流。 |
| 跨篇导航有效性 | **5** | 26 篇内容文件 26/26 含 `## 相关文档` 结尾段；`concepts/index.md`、`examples/index.md` 提供表格式篇目索引与阅读建议；`examples/01`（束 1）直接回链 `concepts/02`、`concepts/07`。 |
| 非专业读者可跟读至形成判断 | **4** | `examples/01`「三件套规则 + 误用情景清单 + 核对动作清单」、`concepts/09-risks`「非法金融活动识别 7 点」、`examples/03`「使用纪律」可让非专业读者独立走读；扣分项：加密侧（储备赎回、代币化、法域分层）需读者自带一定金融制度常识，四方七主题表信息密度高，零基础读者需按「快速开始」路径引导方可达标。 |
| **总分** | **19 / 20（均分 4.75）** | ≥4，判 `pass`（与 R1/R2 同分，但由本轮独立阅读与打分得出）。 |

### E. AC-5 合规扫描（独立扫描）

- ① **两束根 index 均含声明**：`digital-asset/index.md` L26、`digital-economy/index.md` L26（另有分组 `index.md` L18「不荐不评」）——「不构成投资建议/法律意见/合规意见、不推荐任何产品/平台/币种、不预测价格」齐备。
- ② **中国境内监管红线逐条登记（文号+机构+日期）**：`digital-asset/concepts/09` L27–35 七行——银发〔2013〕289 号/五部门/2013-12-03；94 公告（未见公开文号）/七部门/2017-09-04；三协会公告/2021-05-18；金融委第五十一次会议/2021-05-21；央行约谈/2021-06；发改运行〔2021〕1283 号/11 部门/落款 2021-09-03、发布 2021-09-24；银发〔2021〕237 号/十部门/成文 2021-09-15、公开 2021-09-24。
- ③ **e-CNY 与加密资产/稳定币区别**：`digital-asset/concepts/06` L39（与加密资产：法币 vs 无主权信用担保）、L45（与稳定币）、L49（与第三方支付）三组辨析；L41 复述勘误 7「e-CNY≠加密资产」；四方表 CBDC 行（`concepts/09` L63）。
- ④ **境内外口径并列不混同**：`concepts/05` L60–74（三法域制度并列「不混同、不拼接为全球监管趋同」+ 中国境内口径并列）；`concepts/09` L53–65 四方表 + L97「不得反向推导」；`examples/03` 使用纪律（技术可行性/境外监管可行性/境内合规可行性三层区分）。
- ⑤ **推荐性表述扫描**（自写 grep `推荐|值得投资|建议购买|首选|值得入手|买入|投资价值高`）：命中 **20 行**，逐行定性**全部为否定式**（「不推荐」「不评价」）或导航标题「推荐学习路径」——**0 处推荐产品/平台/币种/价格**。

### Findings（R3 新发现，均为 advisory，非阻塞）

| ID | 类型 | 严重级 | 位置 | 复现 | 期望结果 |
|---|---|---|---|---|---|
| **A-6** | `advisory` | **P2** | `digital-asset/facts.md` **L41（F-010）** | F-010 正文为「数据二十条以数据产权、流通交易、收益分配、安全治理为重点，构成数据基础制度的『四梁八柱』」，标信源 `S1、S2`；**S2 = 中国政府网转载刘鹤 2019 署名文章《坚持和完善社会主义基本经济制度》**，与正文（2022 年「数据二十条」）不对应。raw `R-C-data-factor.md` 对应项 **C-05** 的第二信源为 **S-C04（即本轮新增的 S64 发改委答记者问）**。主信源 S1 正确，故不构成 P0 错引。 | 将 F-010 的次信源由 S2 改为 **S64**（或删去并列的 S2）；回归要求：F 行所标 S 与正文/raw 对应。**非本轮修复引入**（R1/R2 均未捕获）。 |
| **A-7** | `advisory` | **P3** | `digital-economy/index.md` **L24**（束 1 根 index） | 该行称「（82 条事实、**41 个信源**）」，而 `digital-economy/facts.md` 台账与 `references` 均为 **S1–S43（43 个信源）**、`references` L17 亦写「43 个信源」。疑为 P2-6（新增 S42/S43）时漏改的残留计数。 | 将束 1 根 `index.md` L24 的「41 个信源」更正为 **43 个信源**（或改为「S1–S43」）。**非本轮修复引入**（与本轮 S64 修复无关）。 |

> 说明：R2 遗留 advisory 中，**A-4 的一半已随本轮修复消解**（facts.md 说明段三层区间与 references 分层已一致，S39 归属统一）；**A-2（披露式替代信源）、A-3（S48 无事实引用）、A-5（Task 9 状态）** 维持 R2 记录，不重复列为本轮新发现。

### Review History 追加

### Review R3
- **Result**: `pass`
- **Reviewer**: C 门 fresh-context 只读子代理（第三轮，未参与 R1/R2、规划与实施）
- **时间**: 2026-10-17（Asia/Shanghai）
- **Checks Performed**（全部由本轮评审者自跑，未采信 R1/R2 与 tasks.md 自述）:
  1. 自写枚举器：文件清单与总数、中文文件名、每文件 H1 数、`file:///`/`.temp/`/`.spec/`、结尾导航段
  2. 自写枚举器：F 编号连续性/重复/跳号、S 台账条目数与连续性（含两束 facts 与 references 的 SI 集合比对）、P0 标记条数
  3. 自写枚举器：409 条 Markdown 链接全量解析（`/`-根按束根、相对按文件目录），断链与外溢检测
  4. 复跑三门禁（cwd=`projects/awesome-okf-xs`）：`check-toctrees.py` / `check-bundles-index.py` / `check-utf8.py`，均 **rc=0**
  5. 自写递归束口径枚举器重算计数三角：9 域 / 62 组 / 644 束；sheke 9 组 / 72 束；digital-economy 组 2 束
  6. 逐条对照 `raw/R-A~R-D` 复核 C 级事实与 S 映射；核对 **S64 ↔ raw S-C04**（机构/文件名/日期/链接四字段）；重算信源标注命中率
  7. grep 整个 `doc/bundles/` 核查 `S1–S63`/`S1–S62` 残留（区分交付物与 spec 工作区历史行）
  8. AC-5 合规扫描：推荐性表述逐行定性、境内监管逐条登记、e-CNY 辨析、境内外并列不混同
  9. AC-4 教学质量：独立阅读束 1 `concepts/02`、`examples/01` 与束 2 `concepts/00/05/06/09` 并按四维 rubric 打分
  10. 核对主会话构建证据 `_build/build_dummy2.log`（存在、30 条 WARNING、本分组 0 条、含 `build succeeded`）
- **Evidence**: 见上方「第三轮检查点（Review R3）」A/B/C/D/E 各段；**未复跑项**：`sphinx-build`（按约束避免与主会话争用 `_build`）——该项由主会话提供，本轮已核对日志文件存在且内容支持 AC-3 结论。
- **Checkpoint Results**:
  - CP-R1″ (`rule`): `pass` — 命中率 172/172 = 100%（主信源口径；严格口径 171/172 = 99.42%）≥ 98%，P0 级错引 = 0
  - CP-R2″ (`rule`): `pass`
  - CP-R3″ (`rule`): `pass`（dummy 构建子项由主会话提供证据，已核对本分组 0 警告）
  - CP-U1″ (`rubric`): `pass` — 总分 **19/20**（均分 4.75），四维：5 / 5 / 5 / 4
  - CP-R4″ (`rule`): `pass`
  - CP-R5″ (`rule`): `pass`
  - CP-R6″ (`rule`): `pass`
- **Findings**: A-6、A-7（均为 advisory，无 actionable；P0/P1 级 = 0）
- **Recommended Issues**: 无（无 pending issue 需固化；A-6/A-7 为可选的既有优化项，不阻塞收口）

## 终态 Result（Review R3）

**`pass`**

判定依据（artifact-templates.md 不变量）：第三轮 6 个检查点（CP-R1″–CP-R6″，覆盖 AC-1~AC-7）**全部通过**；用户指令的收口修复（F-011/F-013 → S64、S 台账扩为 S1–S64、说明段三层区间对齐）经本轮独立核验**逐条落地且未引入新问题**；每条 AC 均有本轮独立证据；仅余 2 条 advisory（A-6/A-7，均为既有遗留的非阻塞项）。**故本轮 `review.md` 终态 Result = `pass`，满足 AC-7。**

## 遗留风险（R3 更新）

- **R-1**：`sphinx-build -b dummy` 未由本评审独立复现（按约束避免与主会话争用 `_build`）；本轮已核对主会话证据 `_build/build_dummy2.log` 存在、含 `build succeeded, 30 warnings.`，且 30 条 WARNING **无一来自 `sheke/digital-economy`**，与 AC-3 结论一致。
- **R-2 / R-3**：同 R2（raw 单源/转引条目官方原文未补齐；`facts.md` 待核条目应在 `stale_after` 2027-09-30 前补齐或降级）——本轮未变化。
- **R-4**：本变更仍未执行任何 git 提交（`projects/awesome-okf-xs` 为第一方 git submodule）；收口后提交需用户显式指令。
- **R-5（本轮新增）**：A-6（F-010 次信源 S2）、A-7（束 1 根 index「41 个信源」）为既有遗留的表述级瑕疵；不影响 AC-1/门禁与 P0=0 结论，建议在下一次维护窗口一并更正。
