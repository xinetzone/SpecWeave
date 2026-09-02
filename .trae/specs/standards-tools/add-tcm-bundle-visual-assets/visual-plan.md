---
type: VisualPlan
title: "tcm（中医经典与理论）域视觉资产清单——Mermaid 图表与配图"
status: ready-for-production
created: 2026-09-02
source: "R 阶段逐束通读 tcm 域 5 束 60 篇文档（index/concepts/examples）事实采集；需求依据 spec.md"
target: projects/awesome-okf-xs/doc/bundles/yixue/tcm/
---

# tcm 域视觉资产清单（R 阶段产出）

> 本清单所有 Mermaid 节点文字均取自正文事实，成书/托名/辑复诸说并列处图表并列不裁决；数字（条数/篇数/年代/人数）与正文逐字对应。Mermaid 草图已预遵安全编码六规则：代码块内无空行、中文标签双引号、禁 `数字. `/`- ` 列表触发、换行用 `<br/>`、subgraph 用 `ID ["标题"]`、边标签用 `-->|"标签"|`（表格单元格内以 `→（边标签：…）→` 描述，落地代码块时还原为标准语法）。
>
> 配额自检：Mermaid **17 张**（区间 12–18）；配图 **8 张**（区间 6–10，保底 6 张 + 章节意象图 2 张）；每束 Mermaid 2–4 张；单文档视觉资产 ≤2 个；references/ 簿录层与存目索引页零视觉资产。
>
> **2026-09-02 生图落地补记**：8 张配图已全部生成，实际扩展名为 **.jpg**（下表文件名与引用路径中的 .png 一律替换为 .jpg）；引用路径形如 `/_static/bundles/yixue/tcm/images/tcm-classics-domain-cover.jpg`。

## 一、Mermaid 清单（17 张）

| 编号 | 束 | 目标文件（doc/bundles 下相对路径） | 插入章节（## 标题名） | 图表类型 | 图表内容设计（节点/分组/边，文字标签与正文一致） | 事实依据（文档名+章节名） |
|---|---|---|---|---|---|---|
| M1 | tcm-overview | yixue/tcm/classics/tcm-overview/concepts/00-genealogy-layering.md | ## 三层谱系总表 | flowchart TD | A["中医典籍谱系"] → B["经典层：奠基<br/>理论·临床·药物三大源头"]；A → C["各家学说层：理论发展<br/>流派创新与论争"]；A → D["临床与专科层：应用<br/>专科专著·方书·工具书"]；B → B1["《黄帝内经》《难经》<br/>医经理论"]；B → B2["《伤寒杂病论》<br/>经方临床"]；B → B3["《神农本草经》<br/>本草药物"]；C → C1["金元四大家<br/>刘完素寒凉派·张从正攻下派<br/>李杲补土派·朱震亨养阴派"]；C → C2["温病学派<br/>吴有性·叶天士·薛雪·吴鞠通·王孟英"]；D → D1["《针灸甲乙经》《脉经》"]；D → D2["《备急千金要方》《外台秘要》"]；D → D3["《本草纲目》"] | concepts/00-genealogy-layering.md「三层谱系总表」「经典层：四大源头」「各家学说层：金元四大家与温病学派」「临床/专科层：面向应用的典籍」 |
| M2 | tcm-overview | yixue/tcm/classics/tcm-overview/concepts/01-four-classics-guide.md | ## 先说结论：这是一个"现代建构的经典群" | timeline | timeline；title "四大经典提法的建构时序"；清代 : "黄元御《四圣心源》以黄帝、岐伯、扁鹊、张仲景为四圣，被视作四大经典最早提法雏形"；1955年 : "卫生部中医研究院西学中班教学计划首提四大经典，首提书目为《内经》《神农本草经》《伤寒论》《金匮要略》"；1964年 : "北京中医学院《中国医学史讲义》持三部说，第2至4版沿用"；1979年 : "《中医学基础问答》首提含《难经》的四部说"；其后 : "《中国医学史》教材第6版正式称四大经典，即今通行组合" | concepts/01-four-classics-guide.md「先说结论：这是一个"现代建构的经典群"」「组合争议并列登记（不裁决）」 |
| M3 | tcm-overview | yixue/tcm/classics/tcm-overview/concepts/01-four-classics-guide.md | ## 四经之间的关系：医经—经方—本草 | flowchart LR | subgraph YJ ["医经：理论"]：NJ["《黄帝内经》<br/>建构阴阳五行、脏象经络理论框架"]、NAN["《难经》<br/>八十一难问难解经，聚焦脉学脏腑针灸"]；subgraph JF ["经方：临床"]：SH["《伤寒杂病论》<br/>今分《伤寒论》《金匮要略方论》<br/>确立辨证论治临证范式"]；subgraph BC ["本草：药物"]：BEN["《神农本草经》<br/>确立三品分类与药物性味主治框架"]；NJ →（边标签：理解六经需内经理论背景）→ SH；NAN →（边标签：脉学脏腑专题深化）→ SH；BEN →（边标签：读方证需本经药性知识）→ SH | concepts/01-four-classics-guide.md「四经之间的关系：医经—经方—本草」 |
| M4 | tcm-overview | yixue/tcm/classics/tcm-overview/examples/four-classics-reading-plan.md | ## 四阶段总览 | flowchart LR | S0["阶段0 地图与提问<br/>读谱系分层、四大经典、五问法<br/>退出检查：能画出三层谱系图、四经各答五问"] → S1["阶段1 理论入门<br/>《内经》选篇精读<br/>加《难经》选难对照"]；S1 → S2["阶段2 临床进入<br/>《伤寒论》通读<br/>再《金匮要略》选篇"]；S2 → S3["阶段3 药物补维<br/>《本经》序录与代表药条<br/>回望伤寒方与本经药对应"] | examples/four-classics-reading-plan.md「四阶段总览」 |
| M5 | nanjing | yixue/tcm/classics/nanjing/concepts/01-structure-81.md | ## 六部分法 | flowchart TD | T["《难经》八十一难<br/>设问作曰、答以然的问答体<br/>共三卷（一说五卷）"] → P1["论脉：一至二十二难（22难）<br/>寸口诊法·脉形脉度·损至·四时脉"]；T → P2["论经络：二十三至二十九难（7难）<br/>经脉度数·气绝·奇经八脉"]；T → P3["论脏腑：三十至四十七难（18难）<br/>营卫·三焦·五脏·命门·七冲门·八会"]；T → P4["论病：四十八至六十一难（14难）<br/>虚实·五邪·积聚·伤寒有五·诊法界说"]；T → P5["论穴道：六十二至六十八难（7难）<br/>井荥俞经合·原穴·募俞"]；T → P6["论针法：六十九至八十一难（13难）<br/>补泻·迎随·刺深浅·治未病"]；六部难次合计 22+7+18+14+7+13=81 | concepts/01-structure-81.md「体例与分卷」「六部分法」 |
| M6 | nanjing | yixue/tcm/classics/nanjing/concepts/02-relation-to-neijing.md | ## 定位：设难释义 | flowchart TD | L1["第一层：经言引文<br/>设问多以经言起首引述古经<br/>所引为古经，文字与今本《素问》《灵枢》未必逐字对应"] → L2["第二层：文字异文互证<br/>与《灵枢》《脉经》异文互见<br/>后世校勘以经证难、据内经改字"]；L2 → L3["第三层：传本分流<br/>王叔和《脉经》所收难经原文不见今本<br/>张仲景所引八十一难与今本互有出入<br/>唐张守节《史记正义》全引难经，唐初传本与今本接近"] | concepts/02-relation-to-neijing.md「定位：设难释义」「第一层："经言"引文分析」「第二层：文字异文互证」「第三层：传本分流」 |
| M7 | nanjing | yixue/tcm/classics/nanjing/concepts/04-commentators.md | ## 注家谱系表 | timeline | timeline；title "《难经》历代注家谱系"；三国吴 : "吕广注，可考最早注家"；唐 : "杨玄操在吕注基础上重新编次，首次明确提出难经为秦越人所作"；北宋初 : "王九思、王鼎象、王惟一先后校勘，王惟一校勘本刊印颁行"；南宋 : "李元立汇集南宋以前九家校注，撰《难经十家补注》"；宋以后 : "据李元立书重刻改订成《王翰林集注八十一难经》即《难经集注》，为后世通行本"；元 : "滑寿《难经本义》，以文本考订济义理阐发"；清 : "徐大椿《难经经释》，以内经本义驳正难经（补位登记，待补源）" | concepts/04-commentators.md「注家谱系表」 |
| M8 | shanghan-zabinglun | yixue/tcm/classics/shanghan-zabinglun/concepts/01-textual-history.md | ## 一条时间线 | timeline | timeline；title "《伤寒杂病论》成书流变"；东汉建安年间约200至210年 : "张仲景撰《伤寒杂病论》合十六卷"；魏晋南北朝 : "原书十六卷在流传中散佚分裂"；西晋 : "太医令王叔和将伤寒部分整理编纂为《伤寒论》十卷"；北宋治平二年1065年 : "校正医书局高保衡、孙奇、林亿等奉敕校订《伤寒论》，镂版刊行"；北宋1066年 : "校正医书局另校《金匮玉函经》刊行，为同源异构传本"；北宋 : "王洙于馆阁蠹简发现《金匮玉函要略方》三卷，林亿等取中卷杂病编为《金匮要略方论》" | concepts/01-textual-history.md「一条时间线」「每一环发生了什么」 |
| M9 | shanghan-zabinglun | yixue/tcm/classics/shanghan-zabinglun/concepts/02-version-systems.md | ## 四大版本系统对照 | flowchart TD | ROOT["《伤寒论》版本系统<br/>四系并列登记，不作单一真本裁决"] → A["宋本<br/>明万历二十七年1599年赵开美<br/>据北宋校正医书局刻本摹刻<br/>今通行影印排印本多以此为底本"]；ROOT → B["成注本<br/>金皇统四年1144年成无己撰《注解伤寒论》<br/>现存最早的伤寒论全文注本"]；ROOT → C["康平本<br/>日本康平三年1060年丹波雅忠抄本<br/>1937年大塚敬节等影印公布<br/>以追文、嵌注、旁注区分原文注文层次"]；ROOT → D["桂林古本<br/>清末传抄本，相传张绍祖家传第十三稿<br/>1934年罗哲初手抄，1939年桂林刊行<br/>多出温病等篇，学界真伪观点不一"]；ROOT -.-> E["《金匮玉函经》<br/>北宋1066年刊行<br/>同源异构传本，常作对勘之用"] | concepts/02-version-systems.md「四大版本系统对照」「立场：并列不裁决」 |
| M10 | shanghan-zabinglun | yixue/tcm/classics/shanghan-zabinglun/concepts/03-six-channels-framework.md | ## 六经辨证：全书的纲领框架 | flowchart LR | subgraph SYANG ["三阳：由表入里"]：TAIYANG["太阳病<br/>第1至178条，三篇178条<br/>提纲第1条"]、YANGMING["阳明病<br/>第179至262条，84条<br/>提纲第180条"]、SHAOYANG["少阳病<br/>第263至272条，10条<br/>提纲第263条"]；subgraph SYIN ["三阴：由阳入阴"]：TAIYIN["太阴病<br/>第273至280条，8条<br/>提纲第273条"]、SHAOYIN["少阴病<br/>第281至325条，45条<br/>提纲第281条"]、JUEYIN["厥阴病<br/>第326至381条，56条<br/>提纲第326条"]；TAIYANG → YANGMING → SHAOYANG → TAIYIN → SHAOYIN → JUEYIN（边标签：外感病由表入里、由阳入阴的传变坐标）；JUEYIN → HUOLUAN["霍乱<br/>第382至391条，10条"]；JUEYIN → LAOFU["阴阳易差后劳复<br/>第392至398条，7条"]；图后事实说明须注明：条文编号为现代校注者所加，宋本成注本原书无编号 | concepts/03-six-channels-framework.md「六经辨证：全书的纲领框架」「二十二篇结构与编号分布」 |
| M11 | shanghan-zabinglun | yixue/tcm/classics/shanghan-zabinglun/concepts/04-jingui-structure.md | ## 与《伤寒论》的关系：同源异流 | flowchart TD | YUAN["《伤寒杂病论》十六卷原书<br/>东汉张仲景撰，魏晋散佚"] → SHANG["伤寒部分一线<br/>西晋王叔和整理为《伤寒论》十卷<br/>北宋1065年校正医书局校订刊行<br/>以六经统外感热病"]；YUAN → JINKUI["杂病部分一线<br/>北宋王洙于馆阁蠹简发现<br/>《金匮玉函要略方》三卷<br/>林亿等取中卷杂病去重复加校订<br/>编为《金匮要略方论》，三卷二十五篇<br/>以脏腑经络统内伤杂病"]；二书同出十六卷原书，分流时间与路径不同，是兄弟不是父子 | concepts/04-jingui-structure.md「成书与结构」「与《伤寒论》的关系：同源异流」；concepts/01-textual-history.md「每一环发生了什么」 |
| M12 | shennong-bencaojing | yixue/tcm/classics/shennong-bencaojing/concepts/01-reconstruction-systems.md | ## 辑复的逻辑：原书亡而经文存 | flowchart LR | A["《神农本草经》原书<br/>早佚"] → B["汉魏之际<br/>《名医别录》<br/>在神农旧条上增补"]；B → C["梁代494年<br/>陶弘景《本草经集注》<br/>以朱墨分书两层"]；C → D["唐宋官修本草<br/>继承朱墨分层"]；D → E["宋代《证类本草》<br/>大观本以黑白字再现"]；E → F["辑复者<br/>从大观本白字即朱字中<br/>剥离出神农本经"] | concepts/01-reconstruction-systems.md「辑复的逻辑：原书亡而经文存」 |
| M13 | shennong-bencaojing | yixue/tcm/classics/shennong-bencaojing/concepts/02-three-grades.md | ## 三品要素对照表 | flowchart TD | XULU["《本经》序录三品总纲"] → SHANG["上品即上经<br/>一百二十种为君<br/>主养命以应天<br/>无毒，多服久服不伤人"]；XULU → ZHONG["中品即中经<br/>一百二十种为臣<br/>主养性以应人<br/>无毒有毒，斟酌其宜"]；XULU → XIA["下品即下经<br/>一百二十五种为佐使<br/>主治病以应地<br/>多毒，不可久服"]；SHANG → HE["三品合计三百六十五种<br/>对齐周天度数与一岁日数的数术设计<br/>是纲领宣言，不是条目普查"]；ZHONG → HE；XIA → HE；HE -.->（边标签：孙星衍辑本实计）-> SHI["上经146·中经114·下经103<br/>合计363条，与365之数差2<br/>理论数与实数并列登记，不作弥合"] | concepts/02-three-grades.md「序录三品总纲」「三品要素对照表」「365 之数：数术化的纲领」「理论数与辑本实数的落差」 |
| M14 | shennong-bencaojing | yixue/tcm/classics/shennong-bencaojing/examples/three-grades-comparison.md | ## 为什么三品归属是辑本差异的"重灾区" | flowchart TD | M1["水银"] → W1["维基文库本<br/>列于上品区段（紧接丹砂之后）"]；M1 → S1["孙星衍辑本<br/>列中经第4味"]；M2["雄黄"] → W2["维基文库本<br/>列于上品区段（禹余粮之后）"]；M2 → S2["孙星衍辑本<br/>列中经第1味"]；W1、S1、W2、S2 四节点 → CONC["同一味药两本差一整个品级<br/>两读并列登记，不作裁决<br/>读者读的是哪个辑本，决定看到的神农说了什么"] | examples/three-grades-comparison.md「案例一：水银——上品还是中品？」「案例二：雄黄——上品还是中品？」 |
| M15 | waijing-weiyan | yixue/tcm/classics/waijing-weiyan/concepts/01-discovery-and-circulation.md | ## 流传时间线 | timeline | timeline；title "《外经微言》流传时序"；汉代 : "《汉书·艺文志》著录《外经》三十七卷，后亡佚"；明末清初 : "陈士铎在世，《外经微言》长期以抄本传世"；约1689年前后 : "成书系年（当代整理者系年，无定论）"；1803年 : "嘉庆八年《山阴县志》将外经微言列入陈士铎著作清单"；1815年 : "抄本书末朱题嘉庆二十年静乐堂书，整理者记疑或后人所加"；1980年 : "天津发现清代精抄本，现藏天津市卫生职工医学院图书馆"；1984年 : "中医古籍出版社据清抄本影印，32开340页，印5500册，限国内发行"；1999年 : "《陈士铎医学全书》收录为第一部"；2006年 : "《黄帝外经浅释》出版，81篇全注全译"；2010年代后 : "排印本多种，维基文库等站点电子化全文流通" | concepts/01-discovery-and-circulation.md「流传时间线」「1980 年：天津发现清抄本」「1984 年：影印出版」 |
| M16 | waijing-weiyan | yixue/tcm/classics/waijing-weiyan/concepts/04-structure-guide.md | ## 九卷主题地图 | flowchart TD | T["《外经微言》<br/>九卷，每卷九篇，合计八十一篇<br/>仿《素问》《灵枢》黄帝君臣问答体<br/>每篇篇末附陈士铎曰微言按语"] → J1["卷一：养生总纲"]；T → J2["卷二：生育与经脉"]；T → J3["卷三：脏腑与奇经"]；T → J4["卷四：五行脏腑续论与命门<br/>终以命门真火篇"]；T → J5["卷五：命门与诊法<br/>命门经主篇、小心真主篇"]；T → J6["卷六：诊法与五运六气"]；T → J7["卷七：运气与营卫"]；T → J8["卷八：伤寒与八风"]；T → J9["卷九：辨证治则与养生<br/>善养篇、亡阳亡阴篇"]；J1 → ZOU["首尾呼应：从养生出发、以养生收束"]；J9 → ZOU | concepts/04-structure-guide.md「总体结构：九卷九篇，九九八十一」「九卷主题地图」 |
| M17 | waijing-weiyan | yixue/tcm/classics/waijing-weiyan/concepts/06-mingmen-fire-water.md | ## 学术承应谱系 | flowchart LR | subgraph GU ["汉以前经典命题"]：SUWEN["《素问·灵兰秘典论》<br/>主不明则十二官危<br/>原指心为君主之官"]、NANJING["《难经》三十六难、三十九难<br/>命门为诸神精之所舍、原气之所系<br/>右肾为命门，男子藏精女子系胞"]；subgraph MING ["明代命门大讨论"]：ZHAO["赵献可《医贯》<br/>命门在两肾之间<br/>七节之旁中有小心<br/>治病以养命门火为纲"]、ZHANG["张景岳<br/>命门为水火之宅、元气之根<br/>阴阳互根"]；WAIJING["《外经微言》命门三章<br/>命门真火篇（第36篇）<br/>命门经主篇（第37篇）<br/>小心真主篇（第39篇）<br/>居两肾之间，通心肾以为主<br/>水火之府、阴阳之宅、精气之根、死生之窦"]；SUWEN →（边标签：直接引用后翻转，所谓主者正指命门）→ WAIJING；NANJING →（边标签：取消左右肾之分，主无形有气居两肾之间）→ WAIJING；ZHAO →（边标签：命门三章可视为此说的问答体展开）→ WAIJING；ZHANG →（边标签：水火之府阴阳之宅措辞与思路一致）→ WAIJING | concepts/06-mingmen-fire-water.md「学术承应谱系」「命门的四重身份」 |

### Mermaid 分布统计

| 束 | 张数 | 编号 |
|---|---|---|
| tcm-overview | 4 | M1–M4 |
| nanjing | 3 | M5–M7 |
| shanghan-zabinglun | 4 | M8–M11 |
| shennong-bencaojing | 3 | M12–M14 |
| waijing-weiyan | 3 | M15–M17 |
| **合计** | **17** | — |

单文档资产密度：concepts/01-four-classics-guide.md 为 2 张（M2、M3），其余文档均为 1 张；references/ 零资产。

## 二、配图清单（8 张）

> 全部配图为意象类，不承载可证伪信息；每张 prompt 以统一风格后缀收尾。画面严禁人体、经络、穴位、脏腑、舌脉、人物特写、药草鉴真式写实，且不出现任何文字、书法、印章。

| 编号 | 文件名 | 存放绝对路径 | Markdown 引用路径 | 生图 prompt | alt 文本 | 插入文件与位置 |
|---|---|---|---|---|---|---|
| I1 | tcm-classics-domain-cover.png | d:\spaces\SpecWeave\projects\awesome-okf-xs\doc\_static\bundles\yixue\tcm\images\ | /_static/bundles/yixue/tcm/images/tcm-classics-domain-cover.png | 古籍藏书意境：宽大木案上摊开数卷素面线装古籍，书页留白无字迹，旁置毛笔、砚台与镇纸，书卷错落堆叠，背景隐约可见满架典籍的书架，暖光自窗棂洒入，纸页泛米黄光泽，氛围沉静典雅。中国传统水墨画风格，工笔淡彩，暖纸色米白基调，色调素雅含蓄，画面中不出现任何文字、书法、印章、人物、人体部位，横向构图 | 中医典籍域封面：书案上摊开的线装古籍与笔墨 | yixue/tcm/index.md；域介绍段与医学免责声明之后、「## 域级文档」之前 |
| I2 | tcm-overview-cover.png | d:\spaces\SpecWeave\projects\awesome-okf-xs\doc\_static\bundles\yixue\tcm\classics\tcm-overview\images\ | /_static/bundles/yixue/tcm/classics/tcm-overview/images/tcm-overview-cover.png | 典籍群书面面观：书案上四部素面线装典籍并排陈列，书函绦带垂落，书卷间置笔架与青瓷小炉，窗外竹影疏斜映于素纸，桌案木纹温润，全景式构图呈现典籍体系的层次感，书页均留白无字迹。中国传统水墨画风格，工笔淡彩，暖纸色米白基调，色调素雅含蓄，画面中不出现任何文字、书法、印章、人物、人体部位，横向构图 | 典籍总览束封面：书案上并排陈列的四部素面典籍 | yixue/tcm/classics/tcm-overview/index.md；束简介段之后、束统计章节之前 |
| I3 | nanjing-cover.png | d:\spaces\SpecWeave\projects\awesome-okf-xs\doc\_static\bundles\yixue\tcm\classics\nanjing\images\ | /_static/bundles/yixue/tcm/classics/nanjing/images/nanjing-cover.png | 脉学意象：数枚古代竹简与一卷素书摊于青石案上，简旁一线溪流自淡墨远山蜿蜒而来，水纹起伏如脉律般律动，云气舒卷，溪边点缀蒲草与小石，以山水水流隐喻脉学，画面不见任何人物与肢体。中国传统水墨画风格，工笔淡彩，暖纸色米白基调，色调素雅含蓄，画面中不出现任何文字、书法、印章、人物、人体部位，横向构图 | 难经束封面：竹简素书与蜿蜒溪流的脉学意象 | yixue/tcm/classics/nanjing/index.md；束简介段与文献学提示之后、束统计章节之前 |
| I4 | shanghan-cover.png | d:\spaces\SpecWeave\projects\awesome-okf-xs\doc\_static\bundles\yixue\tcm\classics\shanghan-zabinglun\images\ | /_static/bundles/yixue/tcm/classics/shanghan-zabinglun/images/shanghan-cover.png | 寒林典籍意象：冬日寒林疏枝、远山覆雪，几卷竹简与束起的素卷静置于林间石案，枝头微露雪意，天空高远清寒而纸底温润，冷灰淡墨中点染少许暖赭，意境清峻肃穆，卷面均无字迹。中国传统水墨画风格，工笔淡彩，暖纸色米白基调，色调素雅含蓄，画面中不出现任何文字、书法、印章、人物、人体部位，横向构图 | 伤寒杂病论束封面：寒林雪景与静置的竹简书卷 | yixue/tcm/classics/shanghan-zabinglun/index.md；束简介段与免责声明之后、束统计章节之前 |
| I5 | bencaojing-cover.png | d:\spaces\SpecWeave\projects\awesome-okf-xs\doc\_static\bundles\yixue\tcm\classics\shennong-bencaojing\images\ | /_static/bundles/yixue/tcm/classics/shennong-bencaojing/images/bencaojing-cover.png | 山野草木写意：坡地上草木丛生，以水墨写意描绘枝叶花草的俯仰姿态，叶片淡彩点染、不刻画具体品种，一只素竹编篮半隐于草色间，旁置一卷素书，远处浅草坡接淡墨远山，草木生机盎然而笔法疏简。中国传统水墨画风格，工笔淡彩，暖纸色米白基调，色调素雅含蓄，画面中不出现任何文字、书法、印章、人物、人体部位，横向构图 | 神农本草经束封面：水墨写意的山野草木与素书 | yixue/tcm/classics/shennong-bencaojing/index.md；束简介段与免责声明之后、束统计章节之前 |
| I6 | waijing-cover.png | d:\spaces\SpecWeave\projects\awesome-okf-xs\doc\_static\bundles\yixue\tcm\classics\waijing-weiyan\images\ | /_static/bundles/yixue/tcm/classics/waijing-weiyan/images/waijing-cover.png | 佚籍重现意象：云海缭绕的层叠远山，半卷素白卷轴自云雾中徐徐展开、若隐若现，似久佚之籍重现于世，山峰以淡墨晕染、云气以留白表现，山脚数株古松，意境幽远神秘，卷轴纸面素净无字迹。中国传统水墨画风格，工笔淡彩，暖纸色米白基调，色调素雅含蓄，画面中不出现任何文字、书法、印章、人物、人体部位，横向构图 | 外经微言束封面：云雾山中半卷展开的素白卷轴 | yixue/tcm/classics/waijing-weiyan/index.md；束简介段与免责声明之后、束统计章节之前 |
| I7 | philology-red-ink-collation.png | d:\spaces\SpecWeave\projects\awesome-okf-xs\doc\_static\bundles\yixue\tcm\classics\tcm-overview\images\ | /_static/bundles/yixue/tcm/classics/tcm-overview/images/philology-red-ink-collation.png | 朱墨校书意象：书案上摊开素页古籍，纸面留白无字迹，一支朱笔与一支墨笔斜搁笔架，砚台与朱砂小碟并列，数卷书卷叠放案头，暖黄烛光映于纸面，朱墨两色相映，呈现古人校书场景的安静氛围。中国传统水墨画风格，工笔淡彩，暖纸色米白基调，色调素雅含蓄，画面中不出现任何文字、书法、印章、人物、人体部位，横向构图 | 版本学章节配图：案头素页古籍与朱墨两笔 | yixue/tcm/classics/tcm-overview/concepts/02-philology-basics.md；「## 为什么读经典要懂一点版本学」节末（增补理由：朱墨两笔呼应陶弘景朱墨分书、大观本黑白字与校记存异传统，该页无 Mermaid，资产密度 1） |
| I8 | shunni-mountain-stream.png | d:\spaces\SpecWeave\projects\awesome-okf-xs\doc\_static\bundles\yixue\tcm\classics\waijing-weiyan\images\ | /_static/bundles/yixue/tcm/classics/waijing-weiyan/images/shunni-mountain-stream.png | 顺逆山水意象：回旋曲折的山涧溪流，水流在青石间形成顺流直下与回环漩涡两种态势，两岸山势起伏、松柏疏立，云气沿山腰流转，以水势回旋隐喻顺逆之理，意境澹泊悠远，全画无人。中国传统水墨画风格，工笔淡彩，暖纸色米白基调，色调素雅含蓄，画面中不出现任何文字、书法、印章、人物、人体部位，横向构图 | 颠倒顺逆章节配图：山涧回旋的溪流与淡墨远山 | yixue/tcm/classics/waijing-weiyan/concepts/05-diandao-shunni.md；篇首导语段之后、「## 核心命题（原文照录）」之前（增补理由：以水势顺逆回旋隐喻"逆则成仙"的颠倒顺逆思维，该页无 Mermaid，资产密度 1） |

### 配图分布统计

| 位置 | 张数 | 编号 |
|---|---|---|
| 域级封面 | 1 | I1 |
| 5 束束封面 | 5 | I2–I6 |
| 章节意象图（增补） | 2 | I7（tcm-overview/concepts/02）、I8（waijing-weiyan/concepts/05） |
| **合计** | **8** | — |

## 三、V 阶段应重点核对的事实风险点

1. **成书系年口径分歧（M15）**：spec 背景与部分资料作"1697 前后陈士铎述"，而 concepts/01 正文流传时间线作"1689 前后成书（当代整理者系年，无定论）"，古书网电子本又标注"清抄本 1698 底本"。图中已按正文采"约1689年前后"并标注"无定论"，V 阶段须确认图与正文一致且不把 1697/1698 混入。
2. **三品数字两层并列（M13）**：序录理论数为 120/120/125=365，孙星衍辑本实计为上经 146/中经 114/下经 103=363（含 V 阶段补录 10 味嵌入药条）。图中两组数字分属"纲领宣言"与"辑本实数"两层，须核对节点文字未把两层混为一谈，且"佐使"采维基文库本序录用字（孙辑本作"左使"为异文 X-2）。
3. **版本系统与年代（M9）**：宋本节点的 1599（赵开美摹刻）、成注本 1144、康平本 1060 抄本/1937 影印、桂林古本 1934 手抄/1939 刊行四组年代须与 concepts/02 对照表逐字核对；四系必须并列、不得出现"真本/祖本"式裁决措辞（"祖本"仅正文用于《本草纲目》金陵本语境，勿挪用）。
4. **难经六部难次计数（M5）**：22+7+18+14+7+13=81 须与六部分法表难次区间（1–22/23–29/30–47/48–61/62–68/69–81）逐段核对；"共三卷（一说五卷）"须保留两说，不得只写三卷。
5. **命门三章篇序与承应关系（M17）**：命门真火篇为第 36 篇、命门经主篇为第 37 篇、小心真主篇为第 39 篇（非连续三篇，第 38 篇不在三章内），图中篇号须与 concepts/06、concepts/04 一致；《素问》"主不明则十二官危"原指心、本书翻转指命门，边标签不得画成《素问》本身主张命门说。
6. **Mermaid 渲染合规**：timeline 中文事件文本须双引号包裹且事件内不得再嵌 ASCII 双引号（用《》与顿号规避）；M10 的"第1至178条"等数字标签不得以"数字. "形式起首；落地后须跑根目录 check_mermaid.py 与 `invoke build` 验证零警告。
