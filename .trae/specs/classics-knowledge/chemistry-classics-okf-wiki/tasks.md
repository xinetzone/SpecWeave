# 中西化学经典 OKF Wiki 教程 - 实施计划

> 方法论链路：seven-concepts 场景4（知识沉淀）R→I→E→V→C
> 产出根目录：`projects/awesome-okf-xs/doc/bundles/science/`
> 每束统一结构：index.md + log.md + facts.md + insights.md + concepts/（≥4篇 + index）+ examples/（≥2篇 + index）+ references/（≥2篇 + index）
> 委托策略：R/E 阶段 7 束互不写同一文件，可并行委托独立子代理（每代理一束，含信源核验契约）；索引与总表更新串行；V 阶段由全新上下文独立审查员执行。

## Task 1: 域骨架与规范对齐准备

- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建 `doc/bundles/science/index.md`（域索引：自然科学域说明、化学分组导航表、`{toctree}` 引用 chemistry/index）
  - 创建 `doc/bundles/science/chemistry/index.md`（分组索引：双线索说明、7 束导航表占位、`{toctree}` 随束完成逐步补齐）
  - 核对 awesome-okf-xs 子模块工作树状态（git status），确认与既有未提交变更隔离
  - 制定每束 frontmatter 模板（type: OKF/Concept/Example/Reference、sources/generated/verified/status/stale_after/okf_version 字段约定）与信源登记表模板
- **Acceptance Criteria Addressed**: AC-1, AC-3
- **Test Requirements**:
  - `rule` TR-1.1: science/index.md 与 chemistry/index.md 存在且含合法 frontmatter（type 非空）与 toctree 块；证据：文件内容 + gates.toctrees
  - `rule` TR-1.2: 子模块 git status 已核对并记录基线；证据：git status 输出
  - `rule` TR-1.3: 7 个束目录已建空骨架（目录 + 占位），无孤立文件；证据：目录列表

## Task 2: 束1 boyle-sceptical-chymist（波义耳《怀疑的化学家》1661）

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - R：网络调研公版原文（en.wikisource.org / Project Gutenberg / Internet Archive 的 The Sceptical Chymist, 1661）与权威解读（化学史共识）；URL 全部 WebFetch 实测可达后登记
  - facts.md ≥25 条编号事实（作者生卒、出版年、对话体结构、四元素说/三要素说批判、元素定义原文出处、微粒哲学等）
  - concepts/（6 篇）：00-why-read（近代化学宣言）、01-context（17世纪化学语境：亚里士多德四元素说、帕拉塞尔苏斯三要素说、炼金术传统）、02-dialogue-method（对话体与怀疑方法论）、03-element-definition（元素定义与微粒哲学）、04-key-passages（元素定义等核心段落：原文摘录+自撰今译+现代解读）、05-legacy（历史影响与局限）
  - examples/（2 篇）：01-passage-close-reading（经典段落逐句精读实操）、02-reading-route（原文/中译本/化学史参照的阅读路线）
  - references/（2 篇）：original-sources（公版原文信源）、modern-scholarship（权威解读信源）
  - index.md（束入口，含快速导航/快速开始/学习路径）、log.md、insights.md（≥3 条四元组洞察+知识地图）、三个子目录 index.md
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-6, AC-10
- **Test Requirements**:
  - `rule` TR-2.1: facts.md ≥25 条、编号连续、无因果推断词；证据：事实条目统计 + 因果词扫描
  - `rule` TR-2.2: references 登记 URL 100% 实测可达；证据：WebFetch 记录
  - `rule` TR-2.3: concepts 6 篇 + examples 2 篇 + references 2 篇，frontmatter 均含非空 type 与 sources；证据：文件清单 + frontmatter 抽查
  - `rule` TR-2.4: 原文引文均标注出处（著作/部分/页码或章节）且来自公版信源，今译标注自撰；证据：引文-信源对照表
  - `rule` TR-2.5: 全部链接为相对路径，无 file:///、无 d:\ 环境绑定路径；证据：链接扫描
  - `rubric` TR-2.6: 内容质量（事实准确/解读科学/零基础可读）；scale 1-5；anchors 1=事实错误多 3=主线正确但笼统 5=准确深入可自学；threshold >= 4；证据：自评分 + V 阶段复核

## Task 3: 束2 lavoisier-treatise（拉瓦锡《化学基础论》1789）

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - R：调研公版原文（Traité élémentaire de chimie, 1789；Robert Kerr 1790 英译本 Elements of Chemistry，Gutenberg/IA/Wikisource）与权威解读
  - facts.md ≥25 条（拉瓦锡生平关键节点、燃素说、氧的命名 1777-1779、燃烧/呼吸/煅烧实验、质量守恒定量方法、1787 命名法、33 种元素表、热质说残留等）
  - concepts/（6 篇）：00-why-read、01-chemical-revolution（燃素说危机与化学革命）、02-oxygen-theory（氧化学说：燃烧/呼吸/煅烧统一解释）、03-conservation-of-mass（质量守恒与定量实验方法）、04-nomenclature-elements（新命名法与第一张现代元素表）、05-key-passages（序言"只从实验得出结论"、元素表等段落原文+今译+解读；含热质说局限辨析）
  - examples/（2 篇）：01-combustion-passage-reading（燃烧实验段落精读）、02-reading-route
  - references/（2 篇）：original-sources、modern-scholarship
  - index.md、log.md、insights.md、子目录 index.md
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-6, AC-10
- **Test Requirements**:
  - `rule` TR-3.1: facts.md ≥25 条、无因果词、可溯源；证据：条目统计 + 抽查
  - `rule` TR-3.2: references URL 100% 实测可达；证据：WebFetch 记录
  - `rule` TR-3.3: concepts 6 + examples 2 + references 2，frontmatter 合规；证据：文件清单
  - `rule` TR-3.4: 公版引文标注出处、今译自撰；证据：引文对照表
  - `rule` TR-3.5: 链接全部相对路径、无环境绑定路径；证据：链接扫描
  - `rubric` TR-3.6: 内容质量 >= 4；scale 1-5；anchors 同 TR-2.6；证据：自评分 + V 复核

## Task 4: 束3 dalton-new-system（道尔顿《化学哲学新体系》1808）

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - R：调研公版原文（A New System of Chemical Philosophy, 1808/1810，IA 扫描本/Wikisource）与权威解读
  - facts.md ≥25 条（道尔顿生平、气体分压定律 1801、原子论公设、1803 原子量表、倍比定律、定比定律背景、原子符号系统、与盖-吕萨克/阿伏伽德罗的争论等）
  - concepts/（5-6 篇）：00-why-read、01-from-gases-to-atoms（气体研究背景：分压/扩散/溶解）、02-atomic-theory（原子论核心公设：同种原子同质同量、化合整数比）、03-atomic-weights（原子量测定方法与倍比定律）、04-key-passages（原子论章节与原子符号表段落原文+今译+解读）、05-legacy（原子论的证实之路：布朗运动/佩兰；局限：武断假设与测量误差）
  - examples/（2 篇）：01-multiple-proportions-reading（倍比定律段落精读）、02-reading-route
  - references/（2 篇）
  - index.md、log.md、insights.md、子目录 index.md
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-6, AC-10
- **Test Requirements**:
  - `rule` TR-4.1: facts.md ≥25 条、无因果词、可溯源；证据：条目统计 + 抽查
  - `rule` TR-4.2: references URL 100% 实测可达；证据：WebFetch 记录
  - `rule` TR-4.3: concepts ≥5 + examples 2 + references 2，frontmatter 合规；证据：文件清单
  - `rule` TR-4.4: 公版引文标注出处、今译自撰；证据：引文对照表
  - `rule` TR-4.5: 链接全部相对路径、无环境绑定路径；证据：链接扫描
  - `rubric` TR-4.6: 内容质量 >= 4；scale 1-5；anchors 同 TR-2.6；证据：自评分 + V 复核

## Task 5: 束4 mendeleev-periodic-law（门捷列夫元素周期律 1869）

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - R：调研公版/权威信源（1869 论文《元素性质与原子量的关系》、《化学原理》Osnovy Khimii、IA/Wikisource；周期律发现史共识资料）与权威解读
  - facts.md ≥25 条（1869 年 2 月 17 日 presentation、63 种已知元素、原子量排序、迈耶尔 1868/1870 独立工作、类铝/类硼/类硅预言与镓 1875/钪 1879/锗 1886 验证、留空位、惰性气体挑战、莫塞莱原子序数修正等）
  - concepts/（6 篇）：00-why-read、01-elements-before-1869（19 世纪元素发现潮与原子量测定：坎尼扎罗 1860 卡尔斯鲁厄会议）、02-discovery（周期律发现过程：纸牌法/表格/论文要点）、03-predictions（三大预言与验证史）、04-key-passages（1869 论文要点与周期表结构原文/译文+解读）、05-legacy（周期律本质：从质量到电子结构；现代周期表演进）
  - examples/（2 篇）：01-prediction-reading（预言与验证段落精读）、02-reading-route
  - references/（2 篇）
  - index.md、log.md、insights.md、子目录 index.md
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-6, AC-10
- **Test Requirements**:
  - `rule` TR-5.1: facts.md ≥25 条、无因果词、可溯源；证据：条目统计 + 抽查
  - `rule` TR-5.2: references URL 100% 实测可达；证据：WebFetch 记录
  - `rule` TR-5.3: concepts 6 + examples 2 + references 2，frontmatter 合规；证据：文件清单
  - `rule` TR-5.4: 公版引文标注出处、今译自撰；证据：引文对照表
  - `rule` TR-5.5: 链接全部相对路径、无环境绑定路径；证据：链接扫描
  - `rubric` TR-5.6: 内容质量 >= 4；scale 1-5；anchors 同 TR-2.6；证据：自评分 + V 复核

## Task 6: 束5 cantongqi（《周易参同契》东汉·魏伯阳）

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - R：调研公版原文（zh.wikisource.org《周易參同契》、ctext.org 相关页面）与权威研究信源（炼丹术/化学史学术共识）；URL 实测可达后登记
  - facts.md ≥25 条（作者魏伯阳、东汉成书、"万古丹经王"、三篇结构、纳甲法/卦气说、龙虎/铅汞/还丹术语、炉火火候记载、朱熹《周易参同契考异》注本、外丹内丹诠释史等）
  - concepts/（6 篇）：00-why-read（炼丹理论元典的阅读价值）、01-text-and-author（成书、作者、版本与注本体系）、02-theoretical-framework（易理框架：纳甲/卦气如何模拟炉火周期）、03-alchemy-content（外丹内容：药物、火候、还丹理论）、04-key-passages（"河上姹女"等核心段落：原文+注释+自撰今译+现代解读）、05-modern-chemistry-lens（现代化学视角：炼丹设备与反应观察的经验成就 vs 理论框架局限；与西方炼金术对照）
  - examples/（2 篇）：01-furnace-passage-reading（炉火段落精读实操）、02-reading-route（注本选用与阅读路线）
  - references/（2 篇）：original-sources（维基文库/ctext）、modern-scholarship
  - index.md、log.md、insights.md、子目录 index.md
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-6, AC-10
- **Test Requirements**:
  - `rule` TR-6.1: facts.md ≥25 条、无因果词、可溯源；证据：条目统计 + 抽查
  - `rule` TR-6.2: references URL 100% 实测可达；证据：WebFetch 记录
  - `rule` TR-6.3: concepts 6 + examples 2 + references 2，frontmatter 合规；证据：文件清单
  - `rule` TR-6.4: 古文引文标注篇/章出处、今译自撰；无大段复制现代注本；证据：引文对照表
  - `rule` TR-6.5: 链接全部相对路径、无环境绑定路径；证据：链接扫描
  - `rubric` TR-6.6: 内容质量（含化学成就/局限的平衡辨析，无拔高无贬斥）>= 4；scale 1-5；anchors 1=歪曲/臆说 3=主线正确但辨析浅 5=文献扎实+对照深入；证据：自评分 + V 复核

## Task 7: 束6 baopuzi（《抱朴子·内篇》东晋·葛洪）

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - R：调研公版原文（ctext.org《抱朴子》内篇、zh.wikisource.org）与权威研究信源
  - facts.md ≥25 条（葛洪 283-343/363、内篇 20 卷、金丹篇/黄白篇/仙药篇、丹砂-汞-硫-铅反应记载、"丹砂烧之成水银，积变又还成丹砂"、药金/药银（合金）、雄黄/砒霜制剂、硝石-松脂炼铅丹等）
  - concepts/（6 篇）：00-why-read、01-gehong-context（葛洪生平、内外篇结构与写作目的）、02-jindan-chapter（《金丹》篇：丹法分类、还丹/金液体系）、03-huangbai-chapter（《黄白》篇：人造"金银"——合金与药金记载的化学内涵）、04-key-passages（丹砂-水银循环等核心段落：原文+注释+今译+现代化学解读：HgS ⇌ Hg+S 反应体系）、05-modern-chemistry-lens（经验化学成就：硫化汞合成/铅丹/砷化学/焰色？ vs 服食求仙的理论局限）
  - examples/（2 篇）：01-cinnabar-passage-reading（丹砂段落精读）、02-reading-route
  - references/（2 篇）
  - index.md、log.md、insights.md、子目录 index.md
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-6, AC-10
- **Test Requirements**:
  - `rule` TR-7.1: facts.md ≥25 条、无因果词、可溯源；证据：条目统计 + 抽查
  - `rule` TR-7.2: references URL 100% 实测可达；证据：WebFetch 记录
  - `rule` TR-7.3: concepts 6 + examples 2 + references 2，frontmatter 合规；证据：文件清单
  - `rule` TR-7.4: 古文引文标注篇/卷出处、今译自撰；证据：引文对照表
  - `rule` TR-7.5: 链接全部相对路径、无环境绑定路径；证据：链接扫描
  - `rubric` TR-7.6: 内容质量（化学解读科学、反应方程式准确、成就与局限平衡）>= 4；scale 1-5；anchors 同 TR-6.6；证据：自评分 + V 复核

## Task 8: 束7 tiangong-kaiwu（《天工开物》明·宋应星）

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - R：调研公版原文（zh.wikisource.org《天工開物》、ctext.org）与权威研究信源
  - facts.md ≥25 条（宋应星 1587-?、1637 初刊、18 卷、五金卷（金银铜铁锡/锌/黄铜）、丹青卷（朱砂/墨）、作咸卷（制盐）、燔石卷（煤炭/石灰/矾/硫磺）、彰施（染料）、冶铸/锤锻（金属工艺）、锌（倭铅）冶炼记载世界最早之一、煤的分类等）
  - concepts/（6 篇）：00-why-read、01-song-yingxing-context（宋应星与晚明工艺百科全书）、02-wujin-metallurgy（五金卷：金银铜铁锡冶炼与锌（倭铅）/黄铜工艺）、03-chemical-crafts（丹青/作咸/燔石：朱砂与墨、制盐、煤炭分类/石灰/矾的化学工艺）、04-key-passages（五金/燔石核心段落：原文+注释+今译+现代化学解读）、05-modern-chemistry-lens（工艺化学成就：定量配比/锌冶炼/煤的分类/还原焙烧 vs 理论总结局限；与同时代西方对照）
  - examples/（2 篇）：01-wujin-passage-reading（五金卷段落精读）、02-reading-route
  - references/（2 篇）
  - index.md、log.md、insights.md、子目录 index.md
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-6, AC-10
- **Test Requirements**:
  - `rule` TR-8.1: facts.md ≥25 条、无因果词、可溯源；证据：条目统计 + 抽查
  - `rule` TR-8.2: references URL 100% 实测可达；证据：WebFetch 记录
  - `rule` TR-8.3: concepts 6 + examples 2 + references 2，frontmatter 合规；证据：文件清单
  - `rule` TR-8.4: 古文引文标注卷/篇出处、今译自撰；证据：引文对照表
  - `rule` TR-8.5: 链接全部相对路径、无环境绑定路径；证据：链接扫描
  - `rubric` TR-8.6: 内容质量（工艺化学解读准确、成就与局限平衡）>= 4；scale 1-5；anchors 同 TR-6.6；证据：自评分 + V 复核

## Task 9: 总索引更新与束间交叉引用

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4, Task 5, Task 6, Task 7, Task 8
- **Description**:
  - 更新 `doc/bundles/index.md`：计数（domains 13→14、groups 32→33、total_bundles 280→287，以实际磁盘计数为准）、新增 science 域导航小节（分组表 + 束数 + 说明）、toctree 增加 science/index、生态关系 mermaid 图增加 science 节点与合理边、推荐入门路径补充
  - 补齐 `science/chemistry/index.md` 分组索引（7 束导航表 + toctree 7 条）
  - 束间交叉引用：西方线索 4 束按"元素概念→氧化学说→原子论→周期律"逻辑链互链；中国线索 3 束按"理论（参同契）→实践（抱朴子）→工艺（天工开物）"互链；中西线索在各束 insights/concepts 中设对照链接；炼丹束与 think/laozi 建立道家思想背景交叉引用
- **Acceptance Criteria Addressed**: AC-1, AC-8
- **Test Requirements**:
  - `rule` TR-9.1: 总索引计数与磁盘实际一致（域/组/束三处数字 + frontmatter 字段）；证据：计数核对脚本输出
  - `rule` TR-9.2: 总索引含 science 小节表、toctree 条目、mermaid 节点，四者一致；证据：index.md 片段
  - `rule` TR-9.3: chemistry/index.md toctree 覆盖 7 束；每束 index 至少含 1 条束间交叉链接；证据：链接扫描
  - `rule` TR-9.4: 无断链（gates.toctrees 通过）；证据：gates 输出

## Task 10: G3 模式沉淀

- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 9
- **Description**:
  - 在 specs 工作区（`.trae/specs/classics-knowledge/chemistry-classics-okf-wiki/patterns.md`）沉淀"公版经典原文 + 现代解读"知识包生产模式：触发条件、R 阶段信源策略（公版文本库优先级、URL 实测、引文长度纪律）、I/E 阶段结构模板、G1/G2 检查清单、反模式（编造引文/环境绑定路径/版权译文照抄/无依据拔高）、跨学科迁移示例（物理/生物经典如何复用）
- **Acceptance Criteria Addressed**: AC-11
- **Test Requirements**:
  - `rubric` TR-10.1: 模式完整度 >= 4；scale 1-5；anchors 1=无沉淀 3=有步骤无反模式 5=触发/步骤/信源/反模式/迁移示例齐全；证据：patterns.md 评审

## Task 11: 本地质量门与构建验证

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 9
- **Description**:
  - 在 awesome-okf-xs 子模块运行 `invoke gates.all`（UTF-8 + toctree）
  - 运行 `invoke clean && invoke build`（Sphinx 全量构建）
  - 全量链接扫描：确认无 file:///、无 d:\ 环境绑定路径、无断链
  - 修复发现的全部 warning/error 后复跑至 0 warning
- **Acceptance Criteria Addressed**: AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-11.1: `invoke gates.all` 退出码 0；证据：命令输出
  - `rule` TR-11.2: `invoke build` 0 warning 0 error；证据：构建日志
  - `rule` TR-11.3: 链接扫描 0 违规（file:///、环境绑定路径、断链）；证据：扫描输出

## Task 12: V 阶段——独立对抗审查

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 11
- **Description**:
  - 由全新上下文独立审查员（fresh subagent）执行：逐束 ≥5 条关键事实回源网络核验（人名/年代/数据/引文出处）；检查版权合规、frontmatter、链接规范、中西对照的平衡性；按 review.md 检查点逐项出具 pass/fail/blocked 结论
- **Acceptance Criteria Addressed**: AC-9, AC-10
- **Test Requirements**:
  - `rule` TR-12.1: 7 束共 ≥35 条事实回源核验记录在案；证据：审查报告
  - `rule` TR-12.2: 输出结构化审查报告（checkpoint 结果 + findings 分级）；证据：review.md
  - `rubric` TR-12.3: 内容质量逐束评分 >= 4；scale 1-5；anchors 见 AC-10；证据：审查员评分

## Task 13: 审查修复闭环

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 12
- **Description**:
  - 将审查 actionable 发现全部转为 pending issue，逐项修复；修复后复跑 gates + build
  - 若首轮 fail，修复后启动新一轮 fresh 审查直至 pass
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `rule` TR-13.1: 每个 actionable finding 有对应修复与证据；证据：issue 闭环记录
  - `rule` TR-13.2: 修复后 gates.all + build 复跑通过；证据：命令输出
  - `rule` TR-13.3: 最终审查结论为 pass；证据：Review History

## Task 14: C 阶段——原子提交（执行前须用户确认）

- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 13
- **Description**:
  - 按线索拆分原子提交（建议：① science 域骨架 + 西方 4 束；② 中国 3 束；③ 总索引与交叉引用更新），在 awesome-okf-xs 子模块内 Conventional Commits 提交
  - 主仓库 gitlink 更新是否提交单独征求用户意见
- **Acceptance Criteria Addressed**: 方法论闭环（G4）
- **Test Requirements**:
  - `rule` TR-14.1: 每次提交单一职责、仅含 science/ 与 bundles/index.md 相关变更；证据：git show --stat
  - `rule` TR-14.2: 提交信息符合 Conventional Commits（docs(science): ...）；证据：git log

# Task Dependencies

- Task 1 是所有束任务的前置（骨架与模板）
- Task 2-8（7 束）在 Task 1 完成后可**并行委托**（各束写各自目录，无共享文件）
- Task 9 依赖 Task 2-8 全部完成（总索引计数需要束落盘）
- Task 10 依赖 Task 9（模式沉淀基于完整实践）
- Task 11 依赖 Task 9（全量验证）
- Task 12 依赖 Task 11（审查对象须通过本地质量门）
- Task 13 依赖 Task 12；fail 时回到修复并重新审查
- Task 14 依赖 Task 13 的 pass 结论，且执行前须用户明确确认
