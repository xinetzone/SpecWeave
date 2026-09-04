# daoyi-reading 独立审查报告

- **审查时间**：2026-08-30
- **审查身份**：独立只读审查员（fresh-context review）
- **审查对象根目录**：`projects/awesome-okf-xs/doc/bundles/think/daoyi/`（相对仓库根；24 个 .md 文件）
- **体例基准**：同仓库 `think/laozi/boshu-reading/` 范本（OKF v0.2）
- **审查方式**：全文件通读 + 结构/链接/编号机器枚举核对 + 古典原文在线逐字比对（WebFetch 维基文库 / ctext）+ 外部学术资料对抗抽查
- **写入范围声明**：本报告为本次审查唯一写入物，未修改审查对象中的任何文件。

---

## 总体结论：**pass**

8 项审查清单全部通过，**无阻断项**。发现 **6 条建议级问题**（均为数字/表述口径不一致或排版小疵，不影响知识包可用性与可信度），另附 2 条核验附注。建议作者按建议项修订后发布；如时间紧迫，现状亦可发布（建议项不构成阻断）。

---

## 逐项清单结果

### 清单 1：结构完备性 — **pass**

- 24 个文件齐全（Glob 枚举逐一枚举）：分组页 `index.md`（type: group）；束根 `daoyi-reading/index.md`；`concepts/` 00–08 共 9 篇 + `index.md`；`examples/` 01–03 共 3 篇 + `index.md`；`references/` 01–04 共 4 篇 + `index.md`；`facts.md`、`insights.md`、`log.md`。
- 束根 frontmatter 字段完整：`daoyi-reading/index.md:1-13` 含 `type: OKF`、`okf_version: "0.2"`、`version: "1.0.0"`、`source`、`generated`、`verified`、`status: stable`、`stale_after: 2027-08-30`。
- 9 篇 Concept 页 frontmatter 均含 `type: Concept` + `generated` + `verified` + `status` + `stale_after` + `sources`，逐页核对无缺。
- 4 篇 Reference 页**只有 `generated`、无 `verified`**，符合规范。抽查实证：`references/01-online-sources.md:1-22`，`:6` 有 `generated`，其后直接为 `status`/`stale_after`/`sources`，无 `verified` 字段。
- 三个子目录 `index.md` 与 `facts.md`/`insights.md`/`log.md` 均无 frontmatter；分组页 `index.md` 为 `type: group`。与 boshu-reading 范本体例一致。

### 清单 2：toctree 一致性 — **pass**

全库 toctree 围栏仅 5 处，位置与条目全部合规（grep 枚举）：

| 位置 | 行号 | 收录条目 |
|---|---|---|
| 分组页 `index.md` | `:32` | `daoyi-reading/index` |
| 束根 `daoyi-reading/index.md` | `:94-104` | `concepts/index`、`examples/index`、`references/index`、`facts`、`insights`、`log`（均无 .md 后缀） |
| `concepts/index.md` | `:39` | 00–08 共 9 条 |
| `examples/index.md` | `:19` | 01–03 共 3 条 |
| `references/index.md` | `:20` | 01–04 共 4 条 |

- 所有叶子页（concepts 00–08、examples 01–03、references 01–04）均无 toctree。
- toctree 条目与磁盘文件一一对应，无悬空条目、无遗漏文件。

### 清单 3：链接有效性 — **pass**

- 全库无 `file:///` 绝对链接（grep 零命中）。
- 文件名全部为 kebab-case（如 `01-history-yidao-tongyuan.md`、`04-authenticity-register.md`）。
- 全库 Markdown 相对链接（`](xxx.md)`、`](../xxx)`）经 grep 枚举逐条核对，均指向真实存在的文件，无死链。

### 清单 4：facts.md 编号连续性与措辞 — **pass**

- 七前缀编号连续、总数属实：AX 001–026（26）+ CAN 001–023（23）+ DAO 001–026（26）+ EXC 001–015（15）+ FLW 001–009（9）+ FRG 001–007（7）+ SRC 001–010（10）= **116 条**，与束根 `index.md:50` "116 条"宣称一致；无断号、无重号。
- 事实均带出处（学者姓名、ISBN、URL、道藏编号 DZ/SK、卷次或 ctext res 编号）。
- 未证实说法均显式标注"待考"（10 个文件共 17 处，如 `references/03-modern-scholarship.md:48` 潘毅出生年待考）。
- 抽查未见因果推测式断言或无来源数字。
- 发现 1 处排版小疵（见建议项 6）。

### 清单 5：古典原文在线逐字核验 — **pass**（要求 ≥3 段，实核 4 段逐字一致 + 1 段子串确认）

| 段次 | 束内位置 | 在线核验源 | 结果 |
|---|---|---|---|
| 段 3《大医精诚》 | `examples/01-classic-passages.md:47` 区域 | 维基文库 `zh.wikisource.org/wiki/大醫精誠` | **逐字一致**："凡大醫治病，必當安神定志，無欲無求，先發大慈惻隱之心……普同一等，皆如至親之想。" |
| 段 2"治未病" | `examples/01-classic-passages.md:39` 区域 | 维基文库 `黃帝內經/素問第一卷` | **逐字一致**："是故聖人不治已病治未病……譬猶渴而穿井，鬥而鑄錐，不亦晚乎？" |
| 段 10《抱朴子·黄白》 | `examples/01-classic-passages.md:103` 区域 | ctext `baopuzi/huang-bai`（四部丛刊本） | **逐字一致**："龜甲文曰：我命在我不在天，還丹成金億萬年。" |
| 段 5《抱朴子·杂应》 | `examples/01-classic-passages.md:63` 区域 | ctext `baopuzi/za-ying` | **子串一致**：ctext 作"是故古之初为道者，莫不兼修医术，以救近祸焉"，束内引文"古之初为道者，莫不兼修医术，以救近祸焉"为其逐字子串 |
| 段 1《素问·上古天真论》 | `examples/01` 段 1 | 维基文库 `素問第一卷`（同源抓取文本） | "法于阴阳，和于术数……故半百而衰也"在抓取文本中逐字出现，一致 |

- 字符一致性说明：束内录文为简体、在线源为繁体（ctext 杂应篇为简体录文），繁简转换与现代标点差异均在可接受范围；**用字层面无脱漏、无臆改**。
- 段 6《黄庭内景经》未能经维基文库独立核验——该 URL 返回空页面（"此页面目前没有内容"）；束内该段信源为道藏阁（diancang）与识典 DZ0331，且已在矩阵表黄庭经行备注栏（`references/01:52`："网络传本有异文，以道藏本为准"）主动声明异文处理原则，处理透明。详见附注 A。

### 清单 6：信源与辨伪 — **pass**

- **五部争议书两说并陈**（`references/04-authenticity-register.md:21-54`，facts 对应 FRG 组）：
  - 《中藏经》：孙星衍"六朝少数说" vs 北宋成书主流说；
  - 《辅行诀》：马继兴/钱超尘主真 vs 张政烺、李学勤"非近代伪但不可能早到梁代"及田永衍主伪说——`facts.md:140` FRG-003 明确"两说并存"；
  - 《医道还元》：`facts.md:141` FRG-004 明确 1894 年扶乩降著、托名吕祖，性质与价值分述；
  - 《扁鹊心书》：窦材作者身份无争议，王琦 1765 年重刊本掺入后人内容的发现已注明；
  - 《华佗神医秘传》：`facts.md:142` FRG-005 明确定性为 1920 年代上海伪书，不读不引。
- **zysj.com.cn 全站禁用**：全库 8 处出现**全部为禁用警示语境**，无一例作为信源引用——`facts.md:143`（FRG-006）、`log.md:18`、`insights.md:38`、`examples/03:56`、`references/01:75`、`concepts/08:64`、`references/04:79`、`references/index:15`。
- 信源分级链清晰一致：识典古籍＞维基文库＞ctext 主库＞道藏阁（`facts.md:144` FRG-007），并附平台已知缺陷（如 ctext res=161524《本草纲目》OCR 乱码禁用、维基参同契页面 Textquality 50%）。

### 清单 7：非医疗声明 — **pass**（1 处建议补强）

- 束根 `daoyi-reading/index.md:69-75` 有完整非医疗声明，且明确提示外丹服食、符咒疗法的已知健康风险，声明"符、咒、斋、禁仅作学术描述，不提供操作方法"。
- 分组页 `index.md:28-30` 有内容边界提示。
- 涉医页声明覆盖：concepts 00–07 各页均有（00:69、01:71、02:63、03:57、04:66、05:51-53、06:71、07:30 与 07:58）；`examples/index.md:17`、`examples/01:23-25`、`examples/02:65-66`、`examples/03:41-45`（陈撄宁文献三边界）；`references/index.md:18`。
- `concepts/08`（辨伪方法论页）无独立声明——该页为方法论内容、不涉诊疗，可豁免；建议补一句以求整齐（建议项 5）。

### 清单 8：语言客观性 — **pass**

- 正文全部为中文；表述客观克制，无疗效承诺、无玄学化断言；争议问题一律两说并陈或标待考；对扶乩、托名、伪书均直接定性，不含糊。

### 对抗性外部抽查（清单外加验）

- **老官山髹漆经脉人像数据**：束称"111 个点位、63 条经脉线"（`concepts/06:46`、EXC-007）。外部学术资料（猪飼祥夫论文引島山奈緒子调查）作红点 111 个、红线 22 条 + 刻线 41 条 = 63 条，与束内数字吻合；媒体口径另有 117/119 穴、29/30 白线等异说。束内取发掘报告/学术口径，**可辩护**。
- **《甲乙经》穴数**：束取 348 穴（`facts.md:54` CAN-010、`concepts/02:52`）；外部资料 348（单 49 + 双 299）与 349（单 49 + 双 300）两说并存。束取 348 有据，但未注异说（建议项 4）。

---

## 发现的问题分级

### 阻断项（blocking）

**无。**

### 建议项（suggestions，不阻断发布）

1. **《千金要方》道藏本卷数自相矛盾（93 卷 vs 95 卷）**
   - 93 卷说：`facts.md:63`（CAN-019，识典 DZ1163）、`concepts/03:43`（"《孙真人备急千金要方》93卷本"）、`examples/02:31`（"道藏93卷本"）；
   - 95 卷说：`facts.md:34`（AX-021，引钟肇鹏统计"涵芬楼第799-820册"）、`concepts/01:58`、`concepts/04:21`、`references/02:60`；
   - 且 `concepts/03` 同页 `:43`（93 卷）与 `:47`（"AX-021 记道藏本95卷"）两说并存而未调和。正统道藏通行著录为 93 卷；建议统一核实，并注明钟肇鹏统计口径（95 卷或为含附录/分卷差异）。
2. **典籍数量表述不一致（27 部 vs 17+ 部）**
   - "27 部"：`references/01:4`、`references/01:26`、`references/index:7`、`log.md:13`；
   - "17+ 部"：束根 `index.md:43`、`insights.md:82`；
   - 矩阵表实际行数约 30 行（医经方 14 + 道藏类 16）。建议统一口径（如"矩阵收录 27 行/约 30 种，其中 17+ 部有四平台全文"）。
3. **《周易参同契》维基文库分章数矛盾（36 章 vs 35 章）**
   - 36 章：`facts.md:84`（DAO-012）、`concepts/05:28`；
   - 35 章分章本：`references/01:55`、`examples/01:81`。
   - 建议复核维基文库该页面实际章目后统一（注意勿与《黄庭内景经》36 章混淆，后者无误）。
4. **《甲乙经》穴数宜补异说**：`facts.md:54`（CAN-010）、`concepts/02:52` 作 348 穴；学界另有 349 穴说（单 49 + 双 300）。束内对成书年已有"282 年（一说 256 年）"体例，穴数宜同例补"一说 349 穴"。
5. **`concepts/08` 建议补非医疗声明**：该页为辨伪方法论、不涉诊疗，可豁免；补一行简短声明与全束体例更整齐。
6. **排版小疵**：`facts.md:150`（SRC-001）"CADAL 编号、 HY 为其他馆藏编号"——顿号后多一空格，建议删去。

### 核验附注

- **附注 A（段 6 在线核验缺口）**：维基文库《黃庭內景玉經》页面当前为空页，段 6 未能经维基文库独立逐字核验。束内该段以道藏阁与识典 DZ0331 为信源，且已主动标注"含明/台明"异文、提示以道藏本为准（`references/01:52` 备注栏），处理透明、不构成阻断；建议后续以《中华道藏》第 23 册纸本或识典 DZ0331 精校本做终校。
- **附注 B（老官山数据）**：111 点位 / 63 经脉线与外部学术口径吻合，核查通过；媒体异说（117/119 穴、29/30 白线）无需收录，可在 EXC-007 备注一句"媒体报道数字与发掘报告口径有差异"以防读者交叉检索时困惑。

---

## 审查所用在线核验源

- 维基文库《大醫精誠》：https://zh.wikisource.org/wiki/大醫精誠
- 维基文库《黃帝內經/素問第一卷》：https://zh.wikisource.org/wiki/黃帝內經/素問第一卷
- ctext《抱朴子·黄白》：https://ctext.org/baopuzi/huang-bai/zh
- ctext《抱朴子·杂应》：https://ctext.org/baopuzi/za-ying/zh
- 维基文库《黃庭內景玉經》：https://zh.wikisource.org/wiki/黃庭內景玉經 （抓取时为空页面，见附注 A）
- 外部学术核查：老官山髹漆经脉人像点位/脉线数据、《甲乙经》348/349 穴数争议（WebSearch 学术资料）
