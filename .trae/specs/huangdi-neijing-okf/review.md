# 《黄帝内经》OKF 知识包（neijing-reading）验收审查报告

## 〇、元信息

| 项 | 内容 |
|---|---|
| 审查对象 | `projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/`（bundle 根，32 个 .md）及分组落地页 `huangdi-neijing/index.md`（1 个），合计 33 个 .md |
| 规格依据 | `.trae/specs/huangdi-neijing-okf/spec.md`（AC-1~AC-10）、`tasks.md` |
| 审查员 | 独立验收审查子代理（fresh context，未参与生成，对抗式审查） |
| 审查日期 | 2026-08-31 |
| 审查语言 | 中文 |
| 审查方法 | A 结构/frontmatter 清点 → B 原文逐字核查（bundle 内部互检 + ctext 四部丛刊本在线比对 7 页 + cloudtcm/gushiwen/newdu 备选信源 3 处 + WebSearch 旁证）→ C facts.md 质量扫描 → D 立场与安全通读评分 → E 门检 |
| 在线信源 | ctext.org《重廣補註黃帝內經素問》《黃帝素問靈樞經》（四部丛刊景印本，繁体）；cloudtcm.com 黄元御《素问悬解》卷十二；m.gushiwen.cn 至真要大论；ab.newdu.com 至真要大论简体全文；刘完素《素问玄机原病式》引文（WebSearch） |
| 门检命令 | `python scripts\check-toctrees.py "doc\bundles\think\huangdi-neijing"`（cwd=`projects/awesome-okf-xs`） |

> **审查纪律声明**：审查员未修改 bundle 内任何文件；整改属 C 阶段职责。本报告所有缺陷均给出文件、行号与实证依据；所有经核验为 bundle 正确的疑点同样如实记录（翻案清单），不隐善不溢恶。

---

## 一、AC 验收判定总表

| AC | 验收要求（摘要） | 判定 | 依据 |
|---|---|---|---|
| AC-1 | 目录结构符合 OKF v0.2（index/facts/insights/log + concepts/examples/references 三子目录） | ✅ **PASS** | 磁盘恰 33 个 .md：分组 index 1 + bundle 根 4（index/facts/insights/log）+ concepts 13（index+00~11）+ examples 10（index+01~09）+ references 5（index+4）。三目录 index 的表格行、toctree 条目与磁盘文件三者逐一核对一致（12/9/4） |
| AC-2 | toctree 门检通过（断链/可达/清单一致/根 index 四检查） | ✅ **PASS（bundle 范围）** | bundle 范围门检输出"toctree 检查通过: 全部 index.md 引用有效，所有内容文档均可达。"**EXIT=0**。扩展至 think/ 与全 bundles 时 EXIT=1，唯一错误为 `think/confucian/four-books/examples/index.md` 引用不存在的 `01-analects-close-reading`——属**他会话未跟踪 WIP**（confucian/ 整目录 git 未跟踪、four-books 无根 index），与本 bundle 无关，隔离归因 |
| AC-3 | Sphinx 构建无新增警告 | ⚠️ **基本达成（建议复验）** | 门检已覆盖结构层（断链/可达）；本审查会话未重跑完整 Sphinx 构建。建议 C 阶段整改后执行 `invoke build`（或 `sphinx-build -b dummy -E doc _build/dummy`）复验并过滤 huangdi-neijing 相关警告 |
| AC-4 | frontmatter 规范（type/generated/status/stale_after/sources/verified；okf_version 仅 bundle 根） | ✅ **PASS** | bundle 根 index = `type: OKF` + `okf_version: "0.2"`（全库仅一处）；12 Concept、9 Example、4 Reference 均有 type/generated/status/stale_after/sources，Concept/Example 含 verified；4 篇 Reference 无 verified（与 laozi/boshu-reading 先例一致，房屋惯例）；分组 index、目录 index、facts/insights/log 无 frontmatter（惯例） |
| AC-5 | 原文逐字准确（底本用字规则、异文双录、不得张冠李戴篇目） | ❌ **不通过** | ctext 在线比对坐实底本违规 6 处（無/鬥/瀉/五臟×2）、脱文 2 处（冬三月 14 字、"日"字）、同包字形两形未互注 1 组；详见 §二比对表与 §三缺陷 M-3~M-9 |
| AC-6 | facts.md 质量（客观可核验、信源编号一致、无现代因果连词、无史实错误） | ❌ **不通过** | 现代因果连词/推测词扫描 0 命中（3 处"所以"均在文言引号内）✅；但 F-028 史崧年份史实错误（Blocker）、F-110 信源归属错误（M-1）；insights.md 事实计数错误（M-10） |
| AC-7 | 注册登记（bundles/index.md 计数、think/index.md 分组行与 toctree） | ✅ **基本达成** | bundles/index.md frontmatter `total_bundles: 318 / groups: 55 / domains: 14`；think/index.md 有 type: group、分组表 12 行含 huangdi-neijing（L86）、toctree 含 `huangdi-neijing/index`（L103）。注：spec 基线（287 束/33 组/13 域）已陈旧；磁盘实点 351 束/57 组/14 域，与注册数差额可归因于 fangzhong/、confucian/ 等他会话 git 未跟踪 WIP，非本 bundle 责任 |
| AC-8 | 内容立场：白文/古注/现代三层解读、"可以/不可以怎么用"栏 | ⭐ **4/5**（阈值 ≥4，达标） | 见 §五 rubric 评分 |
| AC-9 | 安全：非医疗声明覆盖、阅读边界 | ⭐ **4/5**（阈值 ≥4，达标） | 见 §五 rubric 评分 |
| AC-10 | 原子提交（子模块内 Conventional Commits） | ⬜ **未完成** | huangdi-neijing/ 当前为 git 未跟踪（??）；bundles/index.md、think/index.md 已修改未提交。属 C 阶段，整改后子模块内 `docs(think): ...` 原子提交 |

---

## 二、原文比对明细表（25 段，内部互检 + 在线实证）

> 在线比对底本：ctext.org 四部丛刊景印本（S1 素问繁体、S2 灵枢繁体）。第 8 次 ctext 请求触发限流（"Access to ctext.org is unavailable from your current location……嚴禁使用自動下載軟体"），至真要大论十九条 ctext 正字未能在线核到，已以 cloudtcm《素问悬解》、newdu 简体全文、刘完素《素问玄机原病式》引文旁证，并在表中如实标注。

| # | 篇目 | bundle 引文（文件:行） | 底本/信源实证 | 判定 |
|---|---|---|---|---|
| 1 | 素问·上古天真论 | concepts/09 L41 blockquote："恬惔虛**無**，真氣從之" | ctext 原文："恬惔虛**无**，真氣從之，精神內守" | ❌ Major（M-3）：底本用"无"不用"無" |
| 2 | 素问·上古天真论 | concepts/09 L52 丈夫 bullet："二八腎氣盛、天癸至、精氣溢**瀉**" | ctext 原文："二八……精氣溢**寫**" | ❌ Major（M-5）：底本用"寫" |
| 3 | 素问·上古天真论 | F-081："太**衝**脈盛／衰少" | ctext 原文："太**衝**脈盛"、"太衝脈衰少" | ✅ 正确（脉名用"衝"规则验证） |
| 4 | 素问·上古天真论 | F-082 段："受五**藏**六府之精而**藏**之……乃能**寫**" | ctext 原文用字一致（藏/寫） | ✅ 正确 |
| 5 | 素问·四气调神大论 | examples/02 L44 冬三月 blockquote："早臥晚起，必待日光，～～去寒就溫，無泄皮膚，使氣亟奪" | ctext 原文："早臥晚起，必待日光，**使志若伏若匿，若有私意，若已有得**，去寒就溫，無泄皮膚使氣亟奪" | ❌ Major（M-7）：中间 14 字无声脱漏且无省略号 |
| 6 | 素问·四气调神大论 | concepts/09 L71 blockquote："譬猶渴而穿井，**鬥**而鑄錐" | ctext 原文："鬭而鑄錐" | ❌ Major（M-4）：底本作"鬭" |
| 7 | 素问·四气调神大论 | F-136 夏三月段 | ctext 同段逐字一致 | ✅ 正确 |
| 8 | 素问·四气调神大论 | F-137 秋三月："冬為**飧**泄" | ctext 原文："冬為**飱**泄" | ⚠️ Minor（m-4）：飧/飱异体未注 |
| 9 | 素问·生气通天论 | F-088 / examples/03 L36："故天運當以光明，是故陽因而上" | ctext 原文："故天運當以**日**光明" | ❌ Major（M-8）：脱"日"字 |
| 10 | 素问·生气通天论 | （旁证）bundle 未引此句 | ctext："因於暑，汗煩則**喘喝**" | ℹ️ 信息：素问"喘喝"用例，佐证灵枢"喘渴"非误字（见 #18） |
| 11 | 素问·阴阳应象大论 | F-097："濕勝則濡**寫**" | ctext 原文："濕勝則濡**寫**" | ✅ 正确（"濡寫"规则验证） |
| 12 | 素问·阴阳应象大论 | concepts/07 L66 治皮毛 blockquote："其次治筋脈，其次治六府，其次治五**臟**。治五**臟**者，半死半生也" | ctext 同篇用字："濁陰走五**藏**……濁陰歸六**府**"（同篇"藏/府"）；底本规则：治皮毛段作"筋脈""六府""五**藏**" | ❌ Major（M-6）："五臟"×2 应为"五藏"；同段"筋脈""六府"正确 |
| 13 | 灵枢·九针十二原 | F-114 等篇名用字："九**鍼**十二原"、"欲以微**鍼**通其經脈" | ctext 篇名即"九**鍼**十二原"；正文"欲以微鍼通其經脈" | ✅ 正确（"鍼"不作"針"规则验证） |
| 14 | 灵枢·九针十二原 | concepts/05 L77-80："**麤**守關，上守機，機之動，不離其空"归属本篇 | ctext 原文该句确在《九针十二原》本经 | ✅ 正确（**翻案 R-3**：前轮疑为《小针解》冒充，经在线核验推翻；"上守機者知守氣也"训释句式才属《小针解》） |
| 15 | 灵枢·九针十二原 | concepts/05 L32："經脈十二，絡脈十五，凡二十七氣"归属本篇 | ctext 原文该句在《九针十二原》五藏五俞段内 | ✅ 正确（**翻案 R-4**） |
| 16 | 灵枢·九针十二原 | F-121：肝经原穴"其原出於太**沖**" | ctext 原文："其原出於太**沖**，太沖二" | ✅ 正确（**翻案 R-2**：穴名底本作"沖"；与 #3 脉名"衝"成双规则） |
| 17 | 灵枢·九针十二原 | concepts/05 blockquote："麤守形，上守神……若風之吹**云**" | ctext 原文："麤"（非"粗"）、"若風之吹**云**" | ✅ 正确（"麤""云"规则验证） |
| 18 | 灵枢·经脉 | F-125 / examples/08 L47："咳上氣，**喘渴**，煩心" | ctext 底本原文确作"喘**渴**" | ✅ 正确（**翻案 R-1**：前轮"喘喝"疑点推翻；素问 #10 之"喘喝"为他篇用例，二字并存于不同书） |
| 19 | 灵枢·经脉 | F-125 / examples/08："**膨膨**而喘咳" | ctext 底本原文："**膨脹**而喘咳" | ⚠️ Minor（m-2）：自称逐字转录 ctext 而字形不同，未注异文 |
| 20 | 灵枢·经脉 | F-125 段："盛則**寫**之"、"消**穀**善飢" | ctext 原文用字一致（寫/穀） | ✅ 正确 |
| 21 | 素问·至真要大论 | F-110（facts.md L173）：反治引文"**熱因熱用，寒因寒用**，塞因塞用，通因通用"，标注信源 S7/S12 | cloudtcm《素问悬解》卷十二（S12）经文明文："**熱因寒用，寒因熱用**，塞因塞用，通因通用"，黄元御注亦申"寒不受熱，則熱因寒用，熱不受寒，則寒因熱用" | ❌ Major（M-1）："熱因熱用"读法仅属 S7 王洪图教材/讲课系统，S12 归属错误 |
| 22 | 素问·至真要大论 | F-111（facts.md L174）：异文双录——gushiwen 与《素问悬解》作"熱因寒用，寒因熱用"；王洪图系统作"熱因熱用，寒因寒用"，源 S3/S12/S7 | cloudtcm 实证与 F-111 一致；concepts/11 L49 述《素问悬解》"保留'热因寒用'读法"亦一致 | ✅ 正确（异文双录体例好；但见 M-1/M-2 编号污染） |
| 23 | 素问·至真要大论 | 十九条字形：F-106（facts.md L169）/examples/06 L35 作"諸氣膹**郁**……諸逆**沖**上"（源 S5/S6）；concepts/08 L30 作"諸氣膹**鬱**……諸逆**衝**上"（自称据《灵素节注类编》即 S5） | newdu 简体通行本作"诸气膹**郁**""诸逆冲上"；刘完素《素问玄机原病式》引"诸气膹郁"；传世文献亦见"諸気膹鬱"；ctext 正字因限流**未核到** | ❌ Major（M-9）：同一信源 S5 同段两种字形并存、全包无校记互注；ctext 正字待 C 阶段冷却后补核定夺 |
| 24 | 素问·至真要大论 | 十九条计数（concepts/08 L32、examples/06）：火 5 + 热 4 + 五脏 5 + 上下 2 + 风寒湿 3 = 19，无属燥条；"諸痛**痒**瘡"（痒非癢）、"諸禁鼓**栗**"（栗非慄） | 与历代通行算法及底本用字规则一致；刘完素补"皆屬於燥"条为后世发挥，bundle 已正确区分（concepts/08 L37） | ✅ 正确（计数 19 坐实；"痒""栗"规则验证） |
| 25 | 史崧献《灵枢》年份 | F-028（facts.md L64）、insights.md L20、concepts/00 L23、concepts/01 L65、editions.md L38：均作"南宋绍兴乙亥年（**1135**）" | 干支核算：绍兴乙亥 = **1155 年**（绍兴二十五年）；1135 年为乙卯年。tasks.md L11 自身写作"史崧献《灵枢》**1155**"；bundle 内"1155"0 命中 | ❌ **Blocker（B-1）**：硬性史实错误，5 处同错 |

---

## 三、缺陷清单

### Blocker（1 项，涉及 5 处）

| 编号 | 缺陷 | 位置 | 修复要求 |
|---|---|---|---|
| **B-1** | 史崧献家藏《灵枢》年份错误："南宋绍兴乙亥年（1135）"。绍兴乙亥为 **1155 年**（1135 是乙卯年，非乙亥）。tasks.md 任务书自己写的是 1155，属生成时未贯彻规格。5 处同错 | facts.md:64（F-028）；insights.md:20；concepts/00-why-read-neijing.md:23；concepts/01-authorship-and-editions.md:65；references/editions.md:38 | 5 处统一改为 1155（绍兴二十五年乙亥）；改后全包搜"1135"应 0 命中 |

### Major（10 项）

| 编号 | 缺陷 | 位置 | 实证 |
|---|---|---|---|
| M-1 | F-110 反治引文"熱因熱用，寒因寒用"信源标注 S7/S12，其中 **S12 归属错误**：S12=cloudtcm 黄元御《素问悬解》，其经文与注文均作"熱因寒用，寒因熱用"；"熱因熱用"读法仅属 S7 王洪图《内经选读》/讲课系统 | facts.md:173（F-110） | cloudtcm《素问悬解》卷十二在线实证（比对表 #21） |
| M-2 | examples/06 底本行"黄元御《素问悬解》（**S7**，cloudtcm）"S 编号误标（应为 S12）。根源在 log.md 记录将 S7/S12 整体颠倒：log.md:9"cloudtcm《素问悬解》（S7）"、log.md:37"S7=cloudtcm《素问悬解》；S12=王洪图教材/讲课"——与 facts.md 信源表（S7=王洪图，S12=素问悬解）及 electronic-sources.md 分级表直接矛盾 | examples/06-zhizhen-yao.md:24；log.md:9、log.md:37 | facts.md 信源表 S1~S13 与 electronic-sources.md 分级表互相一致，唯 log 与 example06 底本行颠倒 |
| M-3 | blockquote"恬惔虛**無**"违反底本用字规则（底本作"恬惔虛**无**"） | concepts/09-yangsheng.md:41 | ctext 上古天真论（比对表 #1） |
| M-4 | blockquote"**鬥**而鑄錐"违反底本用字规则（底本作"**鬭**而鑄錐"） | concepts/09-yangsheng.md:71 | ctext 四气调神大论（比对表 #6） |
| M-5 | 丈夫 bullet"精氣溢**瀉**"违反底本用字规则（底本作"精氣溢**寫**"） | concepts/09-yangsheng.md:52 | ctext 上古天真论（比对表 #2） |
| M-6 | 治皮毛段 blockquote"五**臟**"×2 违反底本用字规则（底本作"五**藏**"；同段"筋脈""六府"正确，不需动） | concepts/07-diagnostics.md:66 | ctext 阴阳应象大论同篇"藏/府"用字（比对表 #12） |
| M-7 | 冬三月 blockquote **无声脱漏 14 字**："使志若伏若匿，若有私意，若已有得"，且无省略号标记，构成伪全文 | examples/02-siqi-tiaoshen.md:44 | ctext 四气调神大论（比对表 #5） |
| M-8 | "故天運當以光明"**脱"日"字**（底本作"天運當以**日**光明"） | facts.md F-088；examples/03-shengqi-tongtian.md:36 | ctext 生气通天论（比对表 #9） |
| M-9 | 病机十九条同包两种字形并存且无校记：F-106/examples/06 作"膹**郁**／逆**沖**上"（源 S5/S6），concepts/08 blockquote 作"膹**鬱**／逆**衝**上"（自称据 S5《灵素节注类编》）——同一信源两种录文，全包未互注异文。ctext 正字因限流未核 | facts.md:169；examples/06-zhizhen-yao.md:35；concepts/08-treatment-principles.md:30 | 比对表 #23；C 阶段 ctext 冷却后须补核定夺，统一字形或出异文校记 |
| M-10 | insights.md:3 自称"基于事实清单（facts.md，**128 条**）"——计数错误，facts.md 实为 F-001~F-137 共 **137 条**（facts.md 末行自称 137） | insights.md:3 | facts.md 全文清点 |

### Minor（5 项）

| 编号 | 缺陷 | 位置 | 说明 |
|---|---|---|---|
| m-1 | concepts/06（病因学说）全文无医疗边界/非医疗声明 | concepts/06-disease-causes.md | 同包 05/07/08/09/10 均有边界段，06 缺失，体例不齐且该篇直接谈病因致病 |
| m-2 | "膨膨而喘咳"与 ctext 底本"膨脹而喘咳"字形不同，未注异文 | facts.md F-125；examples/08-jingmai.md:47 | 自称逐字转录 ctext 则应出校或改从底本 |
| m-3 | F-102~F-105、F-127、F-128、F-135 信源为简体页面（gushiwen/huangdineijing.org），却以繁体誊录，繁简转换口径未声明 | facts.md 相关条目 | 建议在 facts.md 信源表或凡例中注明"简体信源经繁体化转录，用字以四部丛刊本为准" |
| m-4 | F-137"飧泄"与 ctext 底本"飱泄"为异体字，未注 | facts.md F-137 | 异体字出校或改从底本 |
| m-5 | log.md:21 用字规则简写"太衝（非沖）"表述过泛 | log.md:21 | 底本穴名即作"太沖"（F-121 正确），规则应限定为"太**衝脈**不作太沖"，避免误导后续整改把穴名改错 |

---

## 四、翻案记录（经在线核验，bundle 正确、前轮疑点推翻）

审查过程中曾对以下 5 项产生怀疑，经 ctext 原文在线比对，**确认 bundle 现状正确**，如实记录以保证公正：

1. **"喘渴"非误字**：ctext 灵枢·经脉底本确作"咳上氣，**喘渴**，煩心"（F-125/examples/08 正确）；素问·生气通天论"喘喝"为另一书用例，二字各有所本。
2. **"太沖"穴名正确**：ctext 九针十二原肝经原穴明文"其原出於太**沖**，太沖二"（F-121 正确）；而上古天真论"太**衝**脈"作"衝"（F-081 正确）——"脉名衝、穴名沖"两条规则双双验证。
3. **"麤守關，上守機"归属正确**：该句确为《灵枢·九针十二原》白文（非《小针解》冒充）；仅"上守機者知守氣也"一类训释句式属《小针解》。concepts/05 归属无误。
4. **"經脈十二，絡脈十五，凡二十七氣"归属正确**：该句在《九针十二原》五藏五俞段内，concepts/05 引用无误。
5. **一批底本用字全部合规**："濡**寫**"（F-097）、"九**鍼**/微**鍼**"、"**麤**守形"、"吹**云**"、"諸痛**痒**瘡"（痒非癢）、"諸禁鼓**栗**"（栗非慄）、"消**穀**善飢"、"五**藏**六**府**"等，经 ctext 比对均与底本一致。病机十九条计数 19（火 5/热 4/五脏 5/上下 2/风寒湿 3，无属燥条）与历代通行算法一致。

---

## 五、Rubric 评分（AC-8 / AC-9，阈值 ≥4）

### AC-8 内容立场与三层解读：**4 / 5**

- **优点**：examples/01~09 普遍落实"白文引录 → 古注（王冰/林亿/张介宾/黄元御等）→ 现代解读"三层结构，且每层标注信源；"可以怎么用／不可以怎么用"栏齐全，措辞克制冷静（如 examples/02 L67 明确"不可以：把'夜卧早起/早卧晚起'当作医嘱照做……据'逆之则伤肝'推断自己的季节病"）；F-111 反治异文双录、concepts/08 刘完素补燥条与十九条原作的区分，体现了良好的文献学纪律；insights.md 四元组结构（陈述/证据/反常识/行动）与跨包链接（laozi、boshu-reading）质量高。
- **扣分点**：F-110 信源归属错误（M-1）直接损害"古注层"的可核验性；insights 事实计数错误（M-10）；故不予 5 分。

### AC-9 安全与非医疗声明：**4 / 5**

- **优点**：bundle 根 index 与分组落地页均有阅读边界声明；concepts/05/07/08/09/10 各有医疗边界段（concepts/10 五运六气篇有专节"运气健康决策边界"）；examples/09 十二周阅读计划设双重非医疗声明（L20"不涉及任何自我诊疗"、L72"任何健康问题请咨询执业医师"）；modern-studies.md 明确版权立场（不复制现代译文）。
- **扣分点**：concepts/06 病因学说篇缺医疗边界提示（m-1），与同包体例不齐；故不予 5 分。

---

## 六、门检与仓库状态

- **门检（E）**：`python scripts\check-toctrees.py "doc\bundles\think\huangdi-neijing"` → "toctree 检查通过: 全部 index.md 引用有效，所有内容文档均可达。" **EXIT=0 [verified]**。
- 全库门检 EXIT=1 的唯一断链位于 `think/confucian/four-books/`（他会话 git 未跟踪 WIP：缺根 index 与 examples/01 文件），**非本 bundle 缺陷**。
- **facts.md 语言扫描**：现代因果连词/推测词（因为/所以/因此/由于/导致/推测/可能等）0 命中；3 处"所以"均在文言引号内，符合"白文照录、解读不用现代因果连词"的要求。
- **信源编号**：facts.md S1~S13 与 references/electronic-sources.md 分级表一致（S7=王洪图《内经选读》及讲课 PDF，三级；S12=cloudtcm《素问悬解》，二级）；唯 log.md 与 examples/06 底本行 S7/S12 颠倒（M-2）。
- **git 状态**：huangdi-neijing/ 为未跟踪（??）；bundles/index.md、think/index.md 已修改未提交；AC-10 原子提交待 C 阶段在子模块 awesome-okf-xs 内完成。

---

## 七、结论

### 总评：❌ **不通过（FAIL）——整改后复审**

**理由**：

1. **1 项 Blocker**（史崧献书年份 1135→1155，5 处同错，且任务书 tasks.md 自身写 1155）属硬性史实错误，不容带病发布；
2. **10 项 Major** 中，6 项为底本逐字违规/脱文（無/鬥/瀉/五臟×2/脱"日"/冬三月脱 14 字），直接击穿 AC-5"原文逐字准确"红线；1 项信源归属错误（M-1）击穿 AC-6 事实可核验性；
3. 但**全部 16 项缺陷均为可定点文本修复**（改字、补句、改编号、补边界段、补校记），**无架构性返工**：结构层（AC-1/4/7）、门检（AC-2）全部通过，安全与立场评分（AC-8/9 均 4/5）达到阈值，三层解读体例、异文双录意识、非医疗声明覆盖整体优良。

### C 阶段整改清单（按优先级）

1. 修 B-1：5 处 1135 → 1155，全包复搜"1135"归零；
2. 修 M-3~M-8：按 ctext 底本改正 6 处用字/脱文（無→无、鬥→鬭、瀉→寫、五臟→五藏×2、"天運當以光明"补"日"、冬三月 blockquote 补回 14 字）；
3. 修 M-1/M-2：F-110 删去 S12 归属（"熱因熱用"仅标 S7）；examples/06 L24"素问悬解（S7）"改为 S12；log.md:9/37 S7↔S12 颠倒更正；
4. 修 M-9：ctext 冷却后（建议隔日）补核至真要大论十九条"郁/鬱""沖/衝"正字，全包统一或出异文校记；
5. 修 M-10：insights.md:3"128 条"→"137 条"；
6. 修 Minor 5 项（补 concepts/06 边界段、膨膨/膨脹出校、繁简口径凡例、飧/飱出校、log 用字规则限定"太衝脈"）；
7. 复验：`python scripts\check-toctrees.py "doc\bundles\think\huangdi-neijing"` + Sphinx `invoke build`（或 dummy 构建过滤 huangdi-neijing 警告）；
8. AC-10：子模块内原子提交（`docs(think): 新增黄帝内经阅读知识包 neijing-reading` 一类 Conventional Commit），勿混入 mozi/confucian 等他会话变更。

**复审触发条件**：以上 1~5 项（Blocker + Major）全部修复并给出 diff，6 项 Minor 建议同批处理；复审将重点复扫底本用字与信源编号，并补核 ctext 十九条正字。
