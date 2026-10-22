# 对抗审查报告：知乎专栏「重远投资观」8 篇 → OKF 知识包

## 审查元信息

| 项 | 值 |
|---|---|
| 审查时间 | 2026-10-22 |
| 审查者 | V 阶段审查者（同会话执行，但**机械检查全部独立重跑**，不复述 E 阶段自检结论） |
| 独立性说明 | 本次审查**非** fresh-context 第三方审查。四视角对抗审查在 E 阶段内以"魔鬼代言人 / 新人 / 老板 / 未来"四角色执行并写入 `references/verification.md` 第五节；本报告在此基础上做**独立机械复跑**（重写正则脚本、重跑三个官方门禁、自写链接解析），并逐 AC 给出裁决。局限：结论由同一会话产出，缺少独立第二意见 |
| 审查对象 | `projects/awesome-okf-xs/doc/bundles/sheke/industry/big-tech-pontzi-track-selection/`（10 个 .md）、三级索引增量改动、spec 侧 facts.md / spec.md / tasks.md |
| 对照基准 | spec.md（AC-1~AC-7）、tasks.md、facts.md、同组先例 `ai-solo-company-truth/`、`ai-one-person-micro-product/`、磁盘当前态三级索引 |
| 方法 | ①通读全部 10 个被审文件 + spec/tasks/facts + 先例；②独立重跑机械检查（自写 Python 脚本 + 三个官方门禁 + mermaid 校验器），不复述作者自检；③逐 AC 独立判断并给 rubric 分数与锚点理由；④E 编号与 F 编号双向对账；⑤发现项修复后复检闭环 |

> **结论演进**：**首轮（2026-10-22）：2 项 P1 未闭环**——spec.md 与 log.md 的勘误编号引用错位（P1-1）、log.md 的四视角名称与 verification.md 不一致（P1-2）。
> **终轮（同日）：PASS**——P1-1、P1-2 已修复并复检闭环；AC-1~AC-5 全 PASS、AC-6=4、AC-7=4（均达阈值 4）；残留仅 P2 级观察项。

---

## 逐 AC 裁决

### AC-1：bundle 骨架与定位 —— **PASS**（rule）

独立证据（机械枚举，非引用）：

- 目录枚举恰为 10 个 .md：`index.md`、`log.md`、`concepts/{index,00-pontzi-increment-judgement,01-circle-superstition-and-resource-exchange,02-blue-ocean-cost-structure,03-industry-analysis-playbook}.md`、`references/{index,article-source,verification}.md`，与 FR-1 一一对应；`examples/` 目录 Test-Path=False。
- `okf_version` 出现文件集合 = `['index.md']`（机械扫描全 10 文件），符合 OKF v0.2「仅 bundle 根 index.md 携带」规则，与先例 `ai-solo-company-truth` 同款。
- 根 index.md 隐藏 toctree 三条目（concepts/index、references/index、log）；concepts/index.md toctree 4 条；references/index.md toctree 2 条。官方 `check-toctrees.py` 对本束命中数 **0**。
- 根 index.md 顶部 flagged 状态提示块在位；description 标注"方法论学习包，非操作教程"，两问判定在 log.md 留痕（操作可复现性两问均为"否"）。

### AC-2：F 编号双份一致、事实观点分层 —— **PASS**（rule）

独立证据（正则 `^\|\s*F-(\d{3})\s*\|` 自行提取）：

- `references/article-source.md`：196 条，min=1 / max=196，**连续无跳号、无重复**；spec 侧 `facts.md`：196 条，同样连续。双向差集 = `set()`（完全相等）。
- 全束 F 引用越界扫描：concepts + references + index + log 中出现的所有 `F-NNN` 均在 196 条域内，**越界 0**。
- facts.md 的分类列区分 元信息 / 作者观点 / 作者论证 / 作者建议 / 原文数据主张 / 原文例证 / 原文引述 / 作者框架 / 作者推算；因果推演（如"18 个月触底"）登记为"作者推算"，G1 门（事实栏无推断词）成立。
- locator 分层保留：主文 M + 子页面 S1~S7 共 8 个子表，读者可由 F 编号回溯到具体文章与小节。

### AC-3：P0 核验与勘误完整、flagged 管理 —— **PASS**（rule）

独立证据（verification.md 逐点定位 + E 编号对账）：

- 结论表 22 行齐备，结论分布 ✅3 / ⚠️13 / ⭕3 / ❌3（合计 22，自洽）；替代指标表 4 行；勘误表 23 行，编号 E-01~E-23 连续。
- 机械对账：`E defined = 23`、`E used = 23`、`undefined_used = []`——全包引用的 E 编号全部有定义，无越界引用。
- 三项事实错误有官方依据：E-19（日本家庭部门杠杆率峰值在 1999-2000 约 71%，1991 年是股价房价见顶年）、E-21（2024 年末 61.4% → 2025 年末 59.4%，全年 -2.0pp，与原文 61.1%→57.7% 不吻合）、E-23（统计局 2026-10-19 发布的 9 月数据：一线二手住宅环比 +0.2%、连续 7 个月环比上涨，与原文"新一轮下行周期即将开启"相反）。
- 两项硬错误升级有依据：E-01（985 录取率约 1.9%、211 约 5.2%，原句把两类院校合并为一个分数带）、E-09（AI 短剧结论限于真人实拍生产端，总量层反而暴涨）。
- 口径并列要求落到具体数值：E-16（央行 69.8% vs 国资中心 61.4%，差额 8.4% 为公积金）、E-20（BIS 71.8% vs 国资中心 61.9% vs IMF 61.1%）、E-22（准则口径非无保留意见三种 + 无保留共 4 类，证监会口径另将"带有解释性说明的无保留意见"单列才 5 类）。
- flagged 一致性：含 frontmatter 的 8 个文件（根 index + 4 concepts + article-source + verification）全部 `status: flagged`；`log.md`、`concepts/index.md`、`references/index.md` 无 frontmatter——与先例同款（先例同样是 6 个内容文件带 frontmatter、3 个无）。
- `stale_after: 2026-12-31` 且 verification 第四节给出到期前优先复核项（E-04 杠杆率趋势、E-03 员工规模、E-05 职级制度）。
- 无编造深链：verification 明确"不固化具体页面深链"，只记「发布主体 + 指标名 + 时点 + 结论」三元组，sources 仅列 4 个可核验主体入口（统计局 / 巨潮资讯 / 专栏 API / 主文）。

### AC-4：原创改写与版权安全 —— **PASS**（rule）

独立证据：

- 全束 10 文件无 `.jpg/.jpeg/.png/.gif/.webp/.svg/.html`（机械扫描 media 文件数 = 0），无原图入库，无原文 raw HTML 镜像。
- 敏感串扫描 `file://` / `C:\Users` / `/Users/` / `.temp/` 在 10 文件中命中 **0**。
- 编者补充与编者推断均显式标注：concepts/01 的 6.1 学术理论对照（Bourdieu / Granovetter / Homans）声明"编者补充、未纳入 F 台账"；F-153 标注 ⚠️ 出处缺失；concepts/00 与 03 的跨文章因果链重组标注为编者重组而非原文论证；正文呈现一律为核验后的值，源文错误值只出现在引述与勘误表（verification 第三节铁律）。
- 隐私边界：作者付费知识星球（私域）内容不推断、不入库，仅在 log.md 与 index.md 边界段声明其不可得。

### AC-5：三级索引与机械门禁 —— **PASS**（rule）

独立证据（本轮亲自重跑）：

- 官方 `scripts/check-bundles-index.py` exit 0：`bundles 总索引对账通过: 9 域 / 63 组 / 667 束，frontmatter、计数行、节标题、分组表、toctree 五面一致。`
- 官方 `scripts/check-utf8.py` exit 0：`UTF-8 检查通过: 12161 个文件均为有效 UTF-8。`
- 官方 `scripts/check-toctrees.py` exit 1（19 处），但**本束命中数 = 0**（`Select-String "big-tech-pontzi"` 计数 0）；全部告警来自他人在途束 `jishu/ai/frameworks/vllm/`（断链 8：concepts/index.md 的 09~13 五个条目缺失 + index.md 的 examples/index、references/index、log；未收录 11）。
- mermaid 校验器对全 10 文件逐个调用 `lib.checks.mermaid._process_file`：**files=10，fail=0，全部 [ok]**。首轮曾检出 15 条 error（01/02/03 三块的 `<br/>` HTML 标签 + 带圈数字 ①②③④），已全部改为纯文本标签后复检通过。
- 相对链接：自写解析器扫描全束 `](*.md)` 链接并按各文件所在目录规范化解析，**broken = 0**（含 concepts/00↔01↔02↔03 互链、根 index→concepts/references、主题关联兄弟束链接）。
- 计数自洽：组索引 industry 登记 28 束、域索引 sheke 登记 28 束 industry、总索引 industry 行 28，总索引 total 667 / sheke 74 / jishu 495 / jishu-ai 263，五面一致通过官方脚本。
- **并发污染的如实处置**：目录树地面真值 667 束 vs 索引原登记 664，差额 +1 属本束、+2 属他人在途束（jishu 493→495、jishu/ai 261→263），按"跟随地面真值 + 在 log.md 注记"处置，未误改他人 bundle 内容。

### AC-6：知识转化质量 —— **4 / 5**（rubric，阈值 4，通过）

锚点理由：

- **三分清晰可示范**：concepts/00 把"互联网大厂是一个庞氏结构"这一原始修辞拆成"增量三问判据 + 两条校准链"，并显式加法律定性边界（E-13）与单源作者主张边界——这是把观点转成可用判据而非复述。
- **判据可操作且有失效条件**：concepts/02 的成本打穿三步 + "旧玩家是否已反应"分支，把蓝海定义落到可核验的成本结构对比；concepts/03 给出"读哪三行利润表 + 看哪 4 个市场信号 + 9 条行动清单"，读者可据此执行。
- **迁移边界双层分离**：verification 第四节给出"机制层可迁移 / 数据层不可迁移"的分层时效结论，stale_after + 优先复核清单落到具体 E 编号，读者不会把已被证伪的数据层当作决策依据。
- **不误导**：全束不出现"必赚/稳赚/赶快上车"式语气；原文最刺眼的"30% / 0.3%"晋升概率在 E-02 被降级为定性表述（"晋升空间由公司增量决定，而非入职年份本身"），未复述为概率。
- **扣分项**：①本束的"洞察"主体是编者对三篇互不引用文章的**编辑性重组**，虽已逐处标注，但重组成分高（贴 5 分锚点的"三分"要求但未产出超出原文的新机制发现）；②concepts/01 的编者补充理论对照虽标注"未纳入 F 台账"，但读者无法从 bundle 内部回溯其出处锚点，属弱可溯源；③部分短引号为跨片段压缩（P2-1）。

### AC-7：OKF 规范符合度 —— **4 / 5**（rubric，阈值 4，通过）

锚点理由：

- 与同组先例逐键比对一致：根 index 九字段齐备且 `okf_version` 仅在根；子文件不带 `okf_version`；`status: flagged` + `stale_after` + `sources` 体例与 `ai-solo-company-truth` 同款；log.md 与两个子 index 无 frontmatter，与先例同款。
- toctree + 列表/表格双轨齐备：根 index 用阅读地图 + 核心概念列表 + 隐藏 toctree；组索引用导航表 + toctree；域索引用分组表 + 正文要点；总索引用 frontmatter + 计数行 + mermaid + 分组表 + toctree，五面一致。
- 文档数登记口径有先例依据：同组同形状先例 `ai-one-person-micro-product`（9 文件）登记为「7」，本束 10 文件对应登记「8」。
- 扣分项：①主题关联指向 `ponzi-scheme` 属他人在途束，其入库状态在本束视角不可控（已在 C 阶段提交时以可达性核对处置，列为 P2-3）；②登记口径 28 与磁盘 28 在本束成立，但域索引与总索引的跨层计数说明只存在于 log.md，读者跨层对读时需回查（P2-2）；③`stale_after` 定在 2026-12-31，距数据层时效失效点较近，属保守合理但需按期复核。

---

## 发现清单

### P0（必修，阻断通过）

首轮无 P0。

### P1（必修后复审闭环）

| # | 位置 | 问题 | 处置 |
|---|---|---|---|
| P1-1 | `.trae/specs/zhihu-big-tech-pontzi-okf-wiki/spec.md` 第 59 行；bundle `log.md` 第 12 行 | **勘误编号引用整体错位一位**。原文把"居民杠杆率三口径"标注为 E-11、"蓝海理论归属"标注为 E-12，但 verification.md 的权威表是：E-11 = 蓝海理论归属、E-12 = 作者原创判据归属、E-13 = 庞氏类比边界、**E-16 = 居民杠杆率单一数字口径二义**、**E-20 = BIS/国资中心/IMF 跨口径推演**、E-22 = 审计意见口径不完整。按原文引用会把三处溯源指向不相干的勘误条目 | 已改为：居民杠杆率三口径（**E-16、E-20**）、蓝海理论归属（**E-11**）、作者原创判据归属（**E-12**）、庞氏法律定性边界（E-13）、审计意见口径（E-22）。复检：spec.md 与 log.md 的 E 引用现已与 verification.md 定义表逐项一致 |
| P1-2 | bundle `log.md` 第 16 行 | 四视角名称与 `references/verification.md` 第五节不一致（log 写"事实核查 / 读者价值 / 魔鬼代言人 / 新人"，verification 与七概念标准为"魔鬼代言人 / 新人 / 老板 / 未来"），读者会误以为存在两套审查视角 | 已统一为「魔鬼代言人 / 新人 / 老板 / 未来」，与 verification.md 第五节表格及七概念 V 阶段标准口径一致 |

### P2（观察项，不阻断）

| # | 位置 | 观察 |
|---|---|---|
| P2-1 | concepts/00、01、02 若干处 | 部分带引号短句为跨片段压缩而非原文连续片段（语义忠实、紧邻 F 锚点、长度短）。按本束 AC-4（仅长段逐字复制算违规）不构成失败，但与"非逐字不加引号"纪律有轻微出入，可后续批量回改为去引号转述 |
| P2-2 | `sheke/index.md` / `doc/bundles/index.md` | 跨层计数口径说明只写在 log.md，域索引与总索引之间无一句口径提示；本束 28/28 自洽，但磁盘继续增长后跨层对读可能困惑 |
| P2-3 | concepts/index.md 主题关联段 | 关联到 `ponzi-scheme`（他人在途束）。本束内可达性成立，但该束若未入库将形成悬空关联；C 阶段提交时以"该关联仅作主题指向、不影响本束可达性"处置并留痕 |
| P2-4 | `check-toctrees.py` 红灯 | 19 处告警全部来自他人在途 `vllm` 束，本束命中 0；本会话不代改他人内容 |
| P2-5 | 总索引 jishu 域计数 | jishu 491→495、jishu/ai 259→263 属他人在途束的地面真值同步，本会话已随目录树同步并在 log.md 注记；他人在途束入库后需由其自身会话完成剩余计数 |
| P2-6 | 审查独立性 | 本次 V 阶段审查与 E 阶段同会话，缺少 fresh-context 第二意见；机械检查已全部独立重跑，但主观判断（rubric 评分）无独立复核 |

---

## 机械检查原始输出摘要（均为本轮亲自执行，cwd=projects/awesome-okf-xs）

1. **束目录枚举**：`bundle_files = 10`，清单与 FR-1 逐一对应；`examples_dir = False`；`media_files = 0`。
2. **双份 F 编号**：`F article= 196 spec= 196 equal= True diff= set()`；连续性 article=True / spec=True；**全束 F 引用越界 = 0**。
3. **相对链接**：自写解析器（正则 `\]\(([^)#]+?\.md)(?:#[^)]*)?\)` + 按文件目录规范化解析，跳过 http）→ **broken_links = 0**。
4. **敏感串**：`file://` / `C:\Users` / `/Users/` / `.temp/` 在 10 文件中 **sensitive_hits = 0**。
5. **frontmatter 九字段**：机械扫描全部含 frontmatter 文件 → **frontmatter_missing = 0**（type/title/description/tags/generated/verified/status/stale_after/sources 全在）。
6. **okf_version 唯一性**：`okf_version_files = ['index.md']`。
7. **flagged 一致性**：`flagged_files = 8`（根 index + 4 concepts + article-source + verification）；log.md 与两个子 index 无 frontmatter，与先例同款。
8. **E 编号对账**：`E defined = 23，E used = 23，undefined_used = []`。
9. **`scripts/check-bundles-index.py`**：exit 0 —— `bundles 总索引对账通过: 9 域 / 63 组 / 667 束，frontmatter、计数行、节标题、分组表、toctree 五面一致。`
10. **`scripts/check-utf8.py`**：exit 0 —— `UTF-8 检查通过: 12161 个文件均为有效 UTF-8。`
11. **`scripts/check-toctrees.py`**：exit 1（19 处），`Select-String "big-tech-pontzi"` **命中数 = 0**；告警全部指向 `doc/bundles/jishu/ai/frameworks/vllm/`。
12. **mermaid 校验器**：全 10 文件逐个 `_process_file` → `files= 10 fail= 0`。

---

## 实质性质证覆盖说明

- **A 事实纯度与数字语气**：对 196 条 F 台账逐类抽查（官方口径类、作者估算类、修辞类、单源类），确认正文呈现一律为核验后值，且 30%/0.3%、-0.7%、-40%、604.0 亿元、12.15 万人、18.9%、21.13%、128,166 元、242.2 万人等数字在正文中的语气均为"引用并附口径"，无一处升格为结论。全文无收益承诺式语气。
- **B 勘误铁律落地**：核验"正文呈现的必须是正确值"是否真的执行——抽查 E-19/E-21/E-23 三项硬错误：concepts/02 与 03 呈现的是 1999-2000 约 71%、61.4%→59.4%、连续 7 个月环比上涨等核验后值，原值（1991、61.1%→57.7%、"下一轮下行周期开启"）仅存在于 verification 引述列。铁律成立。
- **C 编者边界**：抽查 concepts/01 第 6.1 节、concepts/00 与 03 的跨文章重组段，确认均带"编者补充"/"编者重组"标注，且编者补充内容未被写入 F 台账（196 条无一条为编者观点）。边界清晰。
- **D 引用可回溯**：抽查 12 条随机 F 引用（跨 4 篇 concepts + references），每条均可由 F 编号定位到 article-source 的 locator（M/S1~S7 + 小节名）；无"只见结论不见出处"的悬空引用。
- **E 计数与并发**：以磁盘当前态与官方门禁脚本为准（667 / 74 / 28），不因并行会话波动误判；地面真值差额的归属（+1 本束、+2 他人在途）已逐项定位到具体域与组。
- **F 读者可用性**：按"新人"视角走一遍阅读路径——根 index 阅读地图（判据→成因→行业→行动）→ concepts/00 增量三问 → concepts/01 因果链 → concepts/02 成本结构 → concepts/03 读表与行动清单，每一步都有可执行动作与失效条件，无需回头找原始文章。
- **G 门禁真实性**：四个门禁脚本全部由本轮亲自执行并留存原始输出；对无法运行的官方链接检查（`check-links.py` 不覆盖子模块路径）明确改用自写等效清单并在 log.md 注明，未以"门禁通过"含糊带过。

---

## 最终结论

# ✅ PASS

- 规则项 **AC-1~AC-5 全部 PASS**；rubric **AC-6 = 4**、**AC-7 = 4**，均达阈值 4。
- 阻断条件复查：无任一 rule AC 失败、无任一 rubric < 4。
- 首轮 P1-1（勘误编号错位）、P1-2（四视角名称不一致）已修复并复检闭环；残留仅为 6 项 P2 级观察（短引号压缩、跨层口径说明、主题关联指向他人在途束、并发污染、审查独立性），不影响事实溯源、勘误完整性、版权安全与门禁可达性。
- **交付边界**：本 bundle 为单源转化的方法论学习包，`status: flagged`，机制层可迁移、数据层不可迁移，`stale_after: 2026-12-31`；不得作为投资建议、择业建议或官方统计口径引用。

## C 阶段（原子提交）记录

| # | 提交 | 范围 | 关键处置 |
|---|---|---|---|
| C-1 | 子模块 `projects/awesome-okf-xs` | 本束 10 文件 + 三级索引的本任务增量 | 共享脏文件 `doc/bundles/index.md`、`doc/bundles/sheke/index.md` 含他人在途增量，采用**索引级精确写入**（`git show HEAD:<path>` 取基线 → 临时副本只施加本任务增量 → `git hash-object -w` + `git update-index --cacheinfo`），工作区不被触碰，他人在途改动原样留在工作区 |
| C-2 | 主仓 `SpecWeave` | spec 四件套 + 子模块指针前移 | 提交集仅两类路径；`.trae/specs/retrospectives-insights/` 的他人在途改动不触碰 |
