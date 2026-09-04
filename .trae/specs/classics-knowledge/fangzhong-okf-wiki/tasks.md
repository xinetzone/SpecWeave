---
type: tasks
spec: fangzhong-okf-wiki
title: 房中（中国古代性文化）典籍 OKF wiki 教程 — 任务分解与执行计划
method: seven-concepts-cmd（R→F→I→E→V→C）
session: sc-20260830-fangzhong-okf
created: 2026-08-30
status: awaiting-approval
---

# 任务计划（tasks.md）

> 对应 spec.md 的 AC-R1~R13（rule）与 AC-Q1~Q5（rubric）。任务级测试需求（TR）仅引用 rule/rubric。
> 工作目录：`d:\spaces\SpecWeave\projects\awesome-okf-xs`（下称子模块根）；新增文件均在 `doc/bundles/think/fangzhong/` 下。
> 范本：`doc/bundles/think/daoyi/daoyi-reading/`（已暂存未提交的他会话产物，结构/frontmatter/toctree/编号体例照此）与 `doc/bundles/think/laozi/boshu-reading/`。
> ⚠️ 本任务含 R 阶段在线调研（WebSearch/WebFetch 核验 URL 与书目），T2/T8 的事实与链接以执行时实测为准，本文件大纲仅为采集范围。

## 任务依赖图

```
T0 WIP隔离+基线实测（git status/HEAD计数/门禁试跑）
  └─ T1 建束骨架目录
       └─ T2 R阶段在线调研 + facts.md（R→F，G1）
            └─ T3 insights.md（F→I，G2）
                 ├─ T4 分组页 think/fangzhong/index.md
                 ├─ T5 束根 fangzhong-reading/index.md
                 ├─ T6 concepts/ 9篇+index（E）
                 ├─ T7 examples/ 3篇+index（E）
                 └─ T8 references/ 4篇+index（E）
                      └─ T9 log.md
                           ├─ T10 更新 think/index.md
                           └─ T11 更新 bundles/index.md
                                └─ T12 gates.toctrees/utf8 + invoke build（V-机器，隔离态）
                                     └─ T13 对抗审查（V-人工：URL抽查/原文比对/边界核查/争议两说）
                                          └─ T15 子模块原子提交（C）
                                               └─ T14 WIP还原（必做，即使失败也还原）
                                                    └─ T16 fresh-context 独立审查（Review）
```

---

## Phase 0：基线准备

### T0 [high] 实测基线并隔离其他会话 WIP

**2026-08-30 实测工作区状态（执行时重新核对）**：

| 类别 | 路径 | 处置 |
|------|------|------|
| 已暂存(A) | `doc/bundles/think/daoyi/` 下 23 文件（daoyi-reading 束 + daoyi/index.md，他会话产物） | 移出入隔离区 + `git reset HEAD` 取消暂存（记录清单供 T14 重新暂存） |
| 未暂存改(M) | `doc/bundles/index.md`（他会话 WIP：frontmatter 296/39/14、正文 300、含 tcm 标签） | 备份至隔离区后 `git restore` 回 HEAD 版，T11 在 HEAD 基线上加本束计数 |
| 未暂存改(M) | `doc/bundles/think/mozi/mozi-reading/concepts/04-mohist-canons.md`、`05-defensive-warfare.md` | **不动**（已跟踪文件，不影响结构，不在本任务 pathspec 内） |
| 未跟踪(??) | `doc/bundles/tcm/`、`think/buddhism/`、`think/confucian/`、`think/guiguzi/`、`think/huangdi-neijing/` | 整体移入隔离区 |
| 干净(==HEAD) | `doc/bundles/think/index.md`——注意：HEAD 版已含 daoyi/buddhism/guiguzi/huangdi-neijing 的表格行与 toctree 条目（他会话此前已提交索引注册、内容未提交，HEAD 树本身处于中间态） | 验证期用**临时精简版**；提交版=HEAD+fangzhong（保留他组注册） |

**动作**：
1. 建立隔离区（主仓侧、子模块树之外——清理-保护域隔离原则）：`d:\spaces\SpecWeave\.temp\active\fangzhong-wip-quarantine\`，下按相对结构 `bundles/` 摆放。
2. 全量记录 `git status --short` 与各未跟踪目录文件数（供 T14 核对还原）。
3. `git show HEAD:doc/bundles/index.md` 记录**已提交基线** frontmatter 计数（total_bundles/groups/domains）、正文计数句、think 节束/组计数、mermaid think 标签原文——T11 在此基线上净增 1 组 1 束。
4. 移动 5 个未跟踪目录与 `think/daoyi/` 至隔离区；`git reset HEAD doc/bundles/think/daoyi`（取消暂存，磁盘文件已移走）；备份 WIP 版 `bundles/index.md` 至隔离区后 `git restore doc/bundles/index.md` 回到 HEAD。
5. 生成**临时验证版** `think/index.md`：HEAD 内容移除 daoyi/buddhism/guiguzi/huangdi-neijing 四组的表格行与 toctree 条目（保留 psi/laozi/zhuangzi/mozi/yinyangjia/legalism/huangdi），加入 fangzhong 行与 `fangzhong/index` 条目（正式内容 T10 写入，此版仅结构占位验证用，T10 重写）。
6. 在隔离态运行 `python scripts/check-toctrees.py` 与 `python scripts/check-utf8.py`，确认退出码 0（验证隔离策略有效：HEAD 树 + 本束占位可达）。
- TR：rule（隔离后 `git status --short` 不含 6 个 WIP 目录；daoyi 暂存已清空；两脚本退出码 0；基线计数已记录）。

### T1 [high] 创建束骨架
- 新建目录 `doc/bundles/think/fangzhong/fangzhong-reading/{concepts,examples,references}`。
- TR：rule AC-R1（目录存在）。

## Phase 1：R→F 事实登记

### T2 [high] R 阶段在线调研 + 编写 facts.md
- 路径：`fangzhong-reading/facts.md`（无 frontmatter，范本同 daoyi）。
- 头注：采集时间 2026-08-30、采集范围（四路公开信源：在线古籍平台/出土整理本与纸本书目/现代学术专著/目录学史料）、"纯客观事实、不含因果推断、未证实标待考"说明。
- **R 阶段调研动作（WebSearch + WebFetch 实测，先核后写）**：
  1. 平台 URL 核验：ctext.org、识典古籍（shidianguji.com）、维基文库、diancang、IDP（idp.bl.uk）/Gallica 上本束核心文献的页面可达性与卷次完整性；
  2. 纸本书目核验：现代学术著作与整理本的出版社/年份/ISBN（高罗佩两书中译本版次、Wile、Needham SCC 5:5、李零、江晓原、刘达临、马继兴、医心方影印本）；
  3. 史料原文核验：《汉志》房中八家著录卷数与小序原文、《隋志》医方类著录、《医心方》卷28结构与引书单、《双梅景闇丛书》子目与刊年、《魏书·释老志》寇谦之清整原文。
- 按前缀分组编号（spec F3.1），素材大纲（★=R 阶段必须在线核验项；未证实者标"待考"或不写）：

  - **CAT 目录著录与源流**：
    - 《汉书·艺文志·方技略》方技四家（医经/经方/房中/神仙）；房中八家★：《容成阴道》26卷、《务成子阴道》36卷、《尧舜阴道》23卷、《汤盘庚阴道》20卷、《天老杂子阴道》25卷、《天一阴道》24卷、《黄帝三王养阳方》20卷、《三家内房有子方》17卷（合计 191 卷；小序"房中者，情性之极，至道之际……乐而有节，则和平寿考"原文★；小序"百八十六卷"与著录合计之差→标待考）；八家全部亡佚；班固（32-92）据刘歆《七略》。
    - 《隋书·经籍志》医方类著录★：《素女秘道经》1卷并《玄女经》、《素女方》1卷、《彭祖养性经》1卷、《郯子说阴阳经》1卷等（原文卷次与小注★核）；《旧唐书·经籍志》《新唐书·艺文志》相关著录★（《玉房秘录》等）。
  - **EXC 出土文献**：
    - 马王堆三号汉墓（长沙，1973 发掘，墓主利豨，下葬汉文帝前元十二年/前168）；房中类竹帛书：《十问》（竹简，黄帝问天师/大成/曹熬/容成等十组问答）、《合阴阳》（竹简）、《天下至道谈》（竹简，"八益七损"）；《养生方》《杂疗方》《胎产书》涉房中求子养胎。
    - 整理本：《马王堆汉墓帛书（肆）》文物出版社1985；马继兴《马王堆古医书考释》湖南科技1992（ISBN★）；裘锡圭主编《长沙马王堆汉墓简帛集成》中华书局2014全7册（ISBN 9787101101683，daoyi 束已验）。
    - 敦煌写本 P.2539《天地阴阳交欢大乐赋》（白行简撰，法国国家图书馆藏，IDP/Gallica 图像页★）。
  - **JIYI 辑佚传世**：
    - 《医心方》30卷，丹波康赖（912-995）撰，日本永观二年（984）成书；卷二十八《房内》引中国房中古书 30 余种★（《素女经》《玄女经》《玉房秘诀》《玉房指要》《洞玄子》《彭祖经》《大清经》《子都经》等，引书清单★核），为房中佚文第一大渊薮；传本系统（半井家本/宫内厅书陵部藏本★）；人民卫生出版社影印/排印本★（版本年与 ISBN 待核）。
    - 叶德辉（1864-1927）《双梅景闇丛书》★（刊年★，光绪间郋园刻本，收入《郋园先生全书》）：辑《素女经》《素女方》《玉房秘诀》《玉房指要》《洞玄子》各1卷并《天地阴阳交欢大乐赋》1卷（子目★核）；佚文辑出以《医心方》卷28为主、敦煌赋为辅。
    - 托名层：素女/玄女（黄帝问对框架）、彭祖（篯铿，传说寿八百）、容成（容成公，《汉志》《容成阴道》）、务成子；《玉房秘诀》题"冲和子"★（撰者与年代争议，见 FRG）；《洞玄子》撰者不详、成书年代★（唐说为主，待核证据）。
  - **YIXUE 医家性医学**：
    - 《素问·上古天真论》天癸生命周期段★（"女子七岁肾气盛……丈夫八岁……八八天癸竭"）与"恬淡虚无"段；《素问·阴阳应象大论》"能知七损八益，则二者可调"★。
    - 孙思邈（581-682）《备急千金要方》卷二十七《养性》含《房中补益》篇★（节欲养生原则："四十以下……"类论述★核原文；只登记原则段，不录操作性条目）；《千金翼方》卷十二养性。
    - 李鹏飞《三元延寿参赞书》5卷（元至元二十八年/1291 自序），"欲不可纵/欲不可早/欲不可强/欲不可绝"四不可★（卷次★核）；收入《道藏》（识典 DZ0851，daoyi 束已验）。
    - 朱震亨《格致余论·色欲箴》★（元）；万全《广嗣纪要》《万氏家传养生四要》★（明，种子/求嗣）；张介宾《景岳全书·妇人规·子嗣》★；岳甫嘉《妙一斋医学正印种子编》★（明，种子专著）；马王堆《胎产书》为求子养胎出土源头。
  - **DAOJIAO 道教房中与内丹**：
    - 葛洪《抱朴子内篇·释滞》★："房中之法十余家，或以补救伤损，或以攻治众病，或以采阴益阳，或以增年延寿，其大要在于还精补脑之一事耳"★原文核；葛洪立场（房中为养生一术、非仙道根本、需真师传授★）。
    - 天师道"黄书合气"（黄赤之道）；寇谦之（365-448）改革，北魏泰常八年（423）"清整道教，除去三张伪法……男女合气之术"★（《魏书·释老志》原文★核）。
    - 《周易参同契》（东汉魏伯阳，"万古丹经王"）与《悟真篇》（张伯端，北宋熙宁乙卯/1075 序）的清修/阴阳双修诠释史★：朱熹《周易参同契考异》（托名邹訢）主清修；《悟真篇》翁葆光注系与薛道光/陆墅注系的分立★（代表注家归属★核）。
    - 东派陆西星（明嘉靖万历间，兴化人）《方壶外史》★；西派李西月（1806-1856，清乐山）《道窍谈》《三车秘旨》★（生卒年★核）；陈撄宁（1880-1969）仙学对阴阳双修的审慎态度★（出处★核）；陶弘景《养性延命录·御女损益篇》辑录房中佚文★。
    - 胡孚琛《道学通论》丹道"三家四派"分类中阴阳丹法（人元）的定位★（表述★核，社科文献2009修订 ISBN 9787509708149 已验）。
  - **WENXUE 文学社会史料**：
    - 白行简（776-826）《天地阴阳交欢大乐赋》敦煌写本 P.2539（叶德辉刻入《双梅景闇丛书》）；本束仅作文献学介绍，不录赋文正文。
    - 明清艳情小说书名级背景（《金瓶梅》《肉蒲团》《株林野史》《昭阳趣史》等仅列名与社会史定位，不录正文）；春宫/秘戏图仅经高罗佩《秘戏图考》作学术史提及，不收录图像。
  - **XUESHU 现代学术**：
    - 高罗佩（R.H. van Gulik, 1910-1967）：《秘戏图考》（*Erotic Colour Prints of the Ming Period*，1951 东京私家版限印 50 册★）；《中国古代房内考》（*Sexual Life in Ancient China*，1961 莱顿 Brill★；中译本版次/译者/出版社/ISBN★核——spec C4 标待考项）。
    - 李零《中国方术正考》《中国方术续考》★（版本/出版社/年份★核）房中相关章节；江晓原《性张力下的中国人》/《云雨》★（版本★核）；刘达临《中国古代性文化》★（版本/ISBN★核）。
    - Douglas Wile, *Art of the Bedchamber: The Chinese Sexual Yoga Classics Including Women's Solo Meditation Texts*, SUNY Press 1992（ISBN★核）；Joseph Needham, *Science and Civilisation in China* Vol. 5 Part 5（1983, Cambridge UP★，内丹/房中章节，ISBN★核）。
  - **FRG 辨伪登记**：
    - 《素女经》等辑本非《汉志》著录原书（汉志八家无素女；《隋志》始著录《素女秘道经》）；托名通则（素女/玄女/彭祖/容成/务成子/冲和子）。
    - 《玉房秘诀》撰者年代、《洞玄子》成书年代之争★（证据两说）；内丹双修清修派（全真主流/朱熹/刘一明）vs 阴阳派（翁葆光/东派/西派）两说并陈★（代表学者★核）。
    - 现代低权威读物警示：署名《素女经》的白话演绎本、地摊"采阴补阳/房中术"读物、无出处网文（"九法/二十四式"等多为演绎或编造）；"还精补脑""采阴补阳"不作功效断言。
    - 高罗佩"中国古代性观念健康开放"说与江晓原"性张力"双向模型的学术修正★（出处★核）。
    - 未证实说法清单（《汉志》小序卷数差、《玉房秘诀》撰者、高罗佩中译本版次、部分 ISBN——一律标"待考"）。
  - **SRC 信源**：
    - 在线矩阵★（R 阶段逐 URL 核验）：《汉书·艺文志》《隋书·经籍志》《素问》《千金要方》《抱朴子内篇》《格致余论》《景岳全书》《云笈七签》《三元延寿参赞书》（识典 DZ0851）在 ctext/识典/维基文库/diancang 的链接；《医心方》卷28、《双梅景闇丛书》辑本、《素女经》辑本、《大乐赋》在维基文库/识典的可用性★；IDP/Gallica P.2539 图像页★。
    - 平台分级：识典＞维基文库＞ctext 主库＞diancang/IDP；zysj.com.cn 污染禁用；平台缺陷（OCR 乱码、未校页面、卷次差异）如实注明。
    - 纸本指南：出土整理本（简帛集成/马继兴考释/帛书肆）、医书校注本（人卫系统）、道藏（中华道藏49册/三家本36册）、《医心方》影印本★、《双梅景闇丛书》影印★（《郋园先生全书》/丛书集成★核）。
- 事实条数目标 ≥100；每条含可溯源信息（学者/书名/出版社/年份/ISBN/URL/卷次）。
- TR：rule AC-R10（无因果推断词、可溯源、未证实标待考/不写）。

## Phase 2：F→I 洞察

### T3 [high] 编写 insights.md
- 路径：`fangzhong-reading/insights.md`。
- 6 条四元组洞察（陈述/证据/反常识/行动），证据引用 facts 编号：
  ① **房中是方技知识体系的一支**：目录学定位（《汉志》方技四家之一，小序"乐而有节则和平寿考"的节欲框架），现代学科三分（性文化史/性医学史/道教养生术）；
  ② **文献层累律："汉志有目→八家全佚→佚文重组"**：今见"古房中经"全是辑佚本，文本三层（马王堆西汉出土→《医心方》984 引文→叶辑1907），读者把辑本当汉代原典是最常见误读；
  ③ **出土本改写房中史**：马王堆《十问》《合阴阳》《天下至道谈》证明西汉房中养生已体系化（八益七损、问答体框架），与《汉志》八家互为表里；
  ④ **辑佚本的使用纪律与双源保存**：《医心方·房内》=佚文第一来源（异国传存）、《双梅景闇》=本土辑刻第二来源（清末），辑本引用必须标注辑出链；
  ⑤ **道教诠释之争的分层**：房中在葛洪处是"养生一术"（《释滞》）、在天师道处是"合气仪式"（黄书）被寇谦之清整、在内丹史中被清修/阴阳两派争夺诠释权——主张、仪式、文本三者不可混为一谈；
  ⑥ **信源分级与现代读物辨伪**：学术读高罗佩/李零/Wile/江晓原，警惕白话演绎与"采补"读物；高罗佩"开放说"已被"性张力"模型修正。
- 末尾附知识地图（六层文献树 + 阅读顺序 ASCII 图）。
- TR：rule（四元组四要素齐备，证据引用 facts 编号）。

## Phase 3：E 束文档生成

### T4 [high] 分组页 `think/fangzhong/index.md`
- type: group；照 think/daoyi/index.md 体例：分组说明（房中=《汉志》方技四家之一、中国古代性文化典籍的学术与文献学入口）、知识包列表表（fangzhong-reading 一行）、学术用途与内容边界一句话提示、toctree 收 `fangzhong-reading/index`。
- TR：rule AC-R2/R3/R8。

### T5 [high] 束根 `fangzhong-reading/index.md`
- frontmatter：type: OKF、title、description、tags（房中,性文化,方技,马王堆,医心方,双梅景闇丛书,道教养生,内丹双修,文献学,阅读教程）、version: "1.0.0"、source（公开信源调研，列 R 阶段四路范围）、generated/verified（agent:seven-concepts-cmd / process:seven-concepts-v，at: 2026-08-30T...+08:00）、status: stable、stale_after: 2027-08-30、okf_version: "0.2"。
- 正文：束定位（房中典籍六层总览教程）、📚快速导航（9概念/3示例/4信源清单）、🚀快速开始（零基础/中医道医基础两入口）、⚠️**学术用途与内容边界声明**（本束为文化史、医学史、宗教史与文献学研究内容，**不构成性教育、医学或两性行为指导；不收录露骨内容**；历史主张不作功效背书）、📖推荐学习路径（三档 ASCII 图）、toctree（concepts/index、examples/index、references/index、facts、insights、log）。
- TR：rule AC-R2/R3/R8/R13。

### T6 [high] concepts/ 9 篇 + index.md
- 每篇 frontmatter：type: Concept、title、description、tags、generated/verified、status、stale_after、sources（引用 /references/ 对应篇）。
- 篇目与要点：
  - `00-what-is-fangzhong.md`：房中概念界定（《汉志》方技四家之一；小序"情性之极，至道之际"）；术语辨析（房中/阴道/养阳/种子/合气/双修/内丹）；现代学术框架（性文化史、性医学史、道教养生术三分）；内容边界与学术用途声明。
  - `01-catalog-origins.md`：《汉志·方技略》房中八家著录表（书名/卷数/托名）、房中小序原文与解读；《隋志》《两唐志》著录；八家全佚与文献层累的起点；方技四家分类中房中的位置。
  - `02-mawangdui-excavated.md`：马王堆三号墓发掘背景；《十问》（问答体、十组问对）、《合阴阳》、《天下至道谈》（八益七损）内容性质；《养生方》《杂疗方》《胎产书》相关条目；三种整理本（帛书肆/马继兴考释/简帛集成）；出土本对房中史的改写（体系化年代提前至西汉）。
  - `03-yixinfang-lost-texts.md`：丹波康赖与《医心方》（984）编纂背景、日本传存系统；卷二十八《房内》结构与引书 30 余种清单；佚文保存的文献学价值（第一大渊薮）；现代影印/排印本指南。
  - `04-shuangmei-jiyi.md`：叶德辉与《双梅景闇丛书》辑佚学（刊年、子目、辑出链：医心方卷28+敦煌赋）；《素女经》《玄女经》《玉房秘诀》《玉房指要》《洞玄子》《彭祖经》各书托名框架与辑本性质；**辑本使用纪律：均为佚文辑本、非《汉志》著录原书**；与《医心方》的双源关系。
  - `05-medical-sexual-medicine.md`：医家性医学谱系双主线（节欲养生 + 求嗣种子）：《素问》天癸说与七损八益；《千金要方·房中补益》节欲论；《三元延寿参赞书》四不可；《格致余论·色欲箴》；种子文献（万全/张介宾/岳甫嘉）与马王堆《胎产书》；医家话语与道教话语的分野。
  - `06-daoist-practices.md`：葛洪《抱朴子·释滞》的房中定位（十余家、还精补脑、一术非仙道）；天师道黄书合气与寇谦之清整（《魏书·释老志》）；《参同契》《悟真篇》清修/阴阳诠释史（朱熹/翁葆光/薛道光注系）；东派陆西星、西派李西月；陈撄宁仙学立场；胡孚琛三家四派分类；**争议两说并陈**。
  - `07-literary-social-sources.md`：文学社会史料层：《天地阴阳交欢大乐赋》敦煌写本（P.2539）的文献学性质；明清艳情小说书名级社会史背景（不录正文）；春宫图与《秘戏图考》的学术史位置（不录图像）；社会史材料的使用边界。
  - `08-modern-scholarship-sources.md`：现代学术地图：高罗佩两书（房内考=通史、秘戏图考=图谱专论）、李零方术研究、江晓原性张力模型、刘达临性文化史、Wile 译本、Needham SCC 5:5、胡孚琛道学通论；信源分级（在线平台优先级 + 纸本两套）；低权威现代读物警示；辨伪方法论（托名规律、著录首见、辑出链、避讳与年代证据）。
- index.md：分组表（入门 00-01 / 出土与辑佚 02-04 / 医家与道教 05-06 / 文学与学术 07-08）+ toctree 9 条。
- TR：rule AC-R1/R2/R9/R13；rubric AC-Q4（六层覆盖+层间交叉引用）。

### T7 [high] examples/ 3 篇 + index.md
- `01-classic-passages.md`：精选原文 8-10 段，**严格限定目录学/养生原则/方法论概述类内容，不录露骨操作性段落**；每段：原文（逐字依 R 阶段已核验权威本）+ 出处（书名/篇卷）+ 3-5 句学术解读 + 全文链接。候选：
  ①《汉志·方技略》房中小序全段；②《素问·上古天真论》天癸生命周期段（女子七/丈夫八）；③《素问·阴阳应象大论》七损八益句；④《千金要方·房中补益》节欲原则段（避开技法条目）；⑤《三元延寿参赞书》"四不可"标题与纲领段；⑥《抱朴子内篇·释滞》"房中之法十余家……还精补脑"段与"不得真师"警示段；⑦马王堆《十问》或《天下至道谈》养生原则短段（八益七损名目层）；⑧《格致余论·色欲箴》短段；⑨《魏书·释老志》寇谦之"除去……男女合气之术"段；⑩《医心方》卷28 卷首题记/目录类短段（呈现佚文辑出结构，不录具体技法条）。篇首附"选段原则与内容边界"说明。
  **每段原文必须与 ctext/识典/维基/IDP 已核验文本逐字一致（T13 抽查比对）**。
- `02-reading-paths.md`：三档路径——零基础（6 周：高罗佩《房内考》→李零方术考房中篇→《汉志》小序→马王堆三书选读→《千金》节欲段→《抱朴子·释滞》，每周具体书目+链接+时长）；中医/道医基础（4 周：《素问》上古天真→《千金》房中补益→《三元延寿参赞书》→《参同契》《悟真篇》诠释史）；研究型（专题书单：Wile/Needham/胡孚琛/江晓原 + 马王堆整理本 + 《医心方》版本 + 道藏目录 + 辑佚丛刊）。
- `03-modern-study-practice.md`：现代学术研究入门：高罗佩两书读法与局限（"开放说"的修正）、李零的方术学框架、江晓原性张力模型、Wile 译本的文献学价值（含女性独自冥想文本）、Needham 的科技史定位；纸本/图书馆获取指南；学术引用规范（辑本必须标辑出链）；边界声明。
- index.md：3 行表 + toctree。
- TR：rubric AC-Q3/Q5；rule AC-R8/R13。

### T8 [high] references/ 4 篇 + index.md
- frontmatter：type: Reference、sources（外部 URL 与书目直接列表；不臆造 resource 路径）。
- `01-online-sources.md`：典籍×平台矩阵大表（《汉志》《隋志》《素问》《千金要方》《抱朴子内篇》《格致余论》《景岳全书》《云笈七签》《三元延寿参赞书》《医心方》卷28、《双梅景闇丛书》辑本、《素女经》辑本、《大乐赋》P.2539 图像、马王堆释文页；列 识典/ctext/维基文库/diancang/IDP 各 URL 与平台备注）；全部 URL 来自 T2 已验证清单；表下注明平台分级与 zysj 禁用。
- `02-print-editions.md`：权威纸本表——出土整理本（《长沙马王堆汉墓简帛集成》中华2014、马继兴《马王堆古医书考释》湖南科技1992、《马王堆汉墓帛书（肆）》文物1985）、医书校注本（人卫《千金要方》校注本、《素问》校注本）、道藏（中华道藏49册/三家本36册，《三元延寿参赞书》《抱朴子》《云笈七签》出处）、《医心方》影印/排印本、《双梅景闇丛书》/《郋园先生全书》影印。
- `03-modern-scholarship.md`：现代学术著作表（高罗佩两书英文原版与中译本、李零两种、江晓原、刘达临、Wile 1992、Needham SCC 5:5、胡孚琛《道学通论》、马继兴），含出版社/年份/ISBN/定位与读法；★项以 T2 核验结果为准。
- `04-authenticity-register.md`：辨伪登记表——①辑本性质（《素女经》等六书=佚文辑本、非汉志原书，标注辑出链）；②托名层（素女/玄女/彭祖/容成/务成子/冲和子）；③年代争议（《玉房秘诀》撰者、《洞玄子》成书，两说证据）；④内丹双修清修/阴阳两派代表学者；⑤高罗佩说与江晓原修正；⑥现代伪托读物警示条（白话演绎本/地摊采补读物/无出处网文）；⑦未证实说法清单（待考项汇总）。
- index.md：4 行表 + 信源使用说明 + toctree。
- TR：rule AC-R6/R7；rubric AC-Q1/Q2。

### T9 [medium] log.md
- `# 更新日志` + `## 2026-08-30`：创建条目（方法 R→F→I→E→V→C、R 阶段四路信源调研、事实条数、9+3+4 结构、辑佚纪律与内容边界原则）。
- TR：rule（日期标题格式 YYYY-MM-DD）。

## Phase 4：索引更新

### T10 [high] 更新 `doc/bundles/think/index.md`
- 在 T0 临时验证版基础上**重写为正式版**：HEAD 全部既有行（psi/laozi/zhuangzi/mozi/yinyangjia/buddhism/guiguzi/legalism/huangdi/huangdi-neijing/daoyi——他组注册保留不动）+ 新增 fangzhong 表格行（🏮 房中（Fangzhong）知识包 | 中国古代性文化典籍——《汉志》房中八家、马王堆出土、《医心方》佚文、《双梅景闇》辑本、医家性医学、道教双修论与现代学术的权威文献学阅读教程）与 toctree `fangzhong/index` 条目；description 句补"房中"。
- TR：rule AC-R4（think 部分）。

### T11 [high] 更新 `doc/bundles/index.md`
- 基线为 T0 记录的 **HEAD 版**（`git restore` 后的版本，不含他会话 tcm 等 WIP 改动）：frontmatter 计数在 HEAD 基线上 total_bundles +1、groups +1（domains 不变）；正文计数句同步；think 节束/组计数各 +1、分组表加 fangzhong 行；两处 mermaid think 标签（生态关系概览图、入门路径图）追加 `fangzhong`。
- ⚠️ 不得把他会话 WIP 内容（tcm 域、300 计数等）写入本任务版本——本文件提交版=HEAD+fangzhong 增量。
- TR：rule AC-R4。

## Phase 5：V 验证与对抗审查

### T12 [high] 机器质量门（WIP 隔离态下）
- 子模块根依次运行：`python scripts/check-toctrees.py`（退出码0）、`python scripts/check-utf8.py`（退出码0）、`invoke build`（构建成功，无 toctree/断链/frontmatter 错误）。
- 补充结构核查：`python scripts/check-toctrees.py doc/bundles/think/fangzhong`（路径模式仅断链检查，验证本束全部 index 引用可解析）。
- 说明：隔离态 think/index.md 为 T0 临时精简版（不含被隔离的 daoyi/buddhism/guiguzi/huangdi-neijing 注册）；T15 提交版为 T10 正式版（HEAD+fangzhong，保留他组注册），二者差异仅为他会话未提交组的注册行——HEAD 树该中间态为既有事实，非本任务引入。
- 任一失败：回 T4-T11 修复后重跑。
- TR：rule AC-R5。

### T13 [high] 对抗审查（fresh 视角只读核查）
- 抽查 ≥6 个信源 URL 实际可达（识典、维基文库、ctext、diancang/IDP 各至少 1）；
- 精选原文段落抽 3 段与权威在线本逐字比对；
- 核查：辑本性质标注（非汉志原书）、托名层、双修两说、低权威读物警示、待考项未写成事实；
- **内容边界核查（AC-R13）**：束内无露骨性行为操作性段落、无色情文学正文、无春宫图像、无功效背书表述；
- 核查全部链接相对路径、无 file:///、文件名 kebab-case、frontmatter type 非空。
- 输出审查结论（pass/fail + 证据），fail 项回 T6-T8 修复。
- TR：rule AC-R6/R7/R9/R13；rubric AC-Q1/Q2/Q5。

## Phase 6：C 原子提交

### T15 [high] 子模块内原子提交（WIP 仍处隔离态）
- 提交前确认 think/index.md 已换回 T10 正式版（HEAD+fangzhong）、bundles/index.md 为 T11 版本（HEAD+fangzhong）。
- `git add` 仅以下路径（正斜杠）：`doc/bundles/think/fangzhong`（整个新目录，含分组页与束）、`doc/bundles/think/index.md`、`doc/bundles/index.md`。
- `git status` 确认暂存清单恰为上述路径，不含 daoyi/mozi/tcm 等任何他会话产物。
- message：`docs(bundles): 新增房中典籍阅读 fangzhong-reading 知识束——中国古代性文化典籍六层权威原文与信源`（body 详列：R→F→I→E→V→C、facts 100+条零推测、9概念+3示例+4信源、在线信源矩阵全部访问核验、辑本托名双修争议分层标注、学术边界声明、gates/build 通过、计数净增 1 组 1 束）。
- 主仓不执行任何 git 操作（gitlink 不动）。
- TR：rule AC-R11。

### T14 [high] 还原 WIP（必做收尾，即使失败也必须执行）
1. 将隔离区 6 个目录移回原位：`tcm/`、`think/buddhism/`、`think/confucian/`、`think/guiguzi/`、`think/huangdi-neijing/`、`think/daoyi/`（移回 doc/bundles/ 对应位置）；
2. `git add doc/bundles/think/daoyi`（恢复他会话原暂存状态，按 T0 记录的 23 文件清单核对）；
3. 将隔离区备份的 WIP 版 `bundles/index.md` 覆盖回工作区（恢复他会话未暂存改动状态；注意该版本不含 fangzhong 计数——他会话 rebase 时自行合并，隔离区备份保留至用户确认后再删）；
4. mozi 两个改动文件全程未动，核对仍为 ` M` 状态；
5. 核对 `git status --short` 与 T0 记录一致（daoyi 23 文件 `A`、bundles/index.md ` M`、mozi×2 ` M`、5 目录 `??`），文件数一致。
- TR：rule AC-R12。

## Phase 7：Review

### T16 [medium] fresh-context 独立只读审查
- 以新上下文按 spec.md 全部 AC 逐项核验（含提交后 git log/文件清单、T14 还原后的 WIP 状态），产出 review.md（pass/fail/blocked）；fail 则回 Implement 修复并复审。
- TR：全部 AC。

---

## 任务级验收映射汇总

| 任务 | 覆盖 AC |
|------|---------|
| T0 | AC-R12（基线记录）、AC-R5（隔离策略验证） |
| T1 | AC-R1 |
| T2 | AC-R10、AC-R6（URL 核验） |
| T3 | F3.2（G2） |
| T4/T5 | AC-R1/R2/R3/R8 |
| T6 | AC-R1/R2/R9/R13、AC-Q4 |
| T7 | AC-Q3/Q5、AC-R8/R13 |
| T8 | AC-R6/R7、AC-Q1/Q2 |
| T9 | F3.3 |
| T10/T11 | AC-R4 |
| T12 | AC-R5 |
| T13 | AC-R6/R7/R9/R13、AC-Q1/Q2/Q5 |
| T15 | AC-R11 |
| T14 | AC-R12 |
| T16 | 全部 AC 复核 |
