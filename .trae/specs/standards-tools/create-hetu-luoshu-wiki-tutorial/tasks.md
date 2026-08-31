# Tasks — create-hetu-luoshu-wiki-tutorial

> 七概念链路（场景4 知识沉淀）：**R（T1）→ I（融入 T6）→ 起草（T2–T6）→ V（T9）→ E 定稿（T9）→ C 入库（T7/T8/T10）**
> 实施目录：`projects/awesome-okf-xs/doc/bundles/think/hetu-luoshu/`
> 依赖顺序：T1 → T2 → T3/T4/T5（可并行）→ T6 → T7 → T8 → T9 → T10

## Task 1: R 阶段——联网调研与原典双源核对
- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 执行七概念 R（复盘/事实采集）：用 WebSearch/WebFetch 系统调研河图洛书与宋代图书学，目标产出 ≥50 条编号事实草稿（F-001…），每条带信源 URL
  - 调研板块：① 先秦两汉原典记载（《顾命》《洪范》《子罕》《系辞上》《礼运》《管子·小匡》《大戴礼记·明堂》《易纬·乾凿度》《数术记遗》《汉书》）原文与 ctext.org/维基文库 URL；② 陈抟—刘牧—朱熹/蔡元定—邵雍—周敦颐传承谱系与《进周易表》；③ 《易数钩隐图》《易学启蒙》《周易本义》卷首图、《皇极经世书》《太极图说》关键内容；④ 欧阳修—胡渭《易图明辨》—二黄—毛奇龄—四库提要—朱伯崑《易学哲学史》辨伪谱系；⑤ 凌家滩玉龟玉版（《文物》1989(4) 陈久金/张敬国、2006 正式报告）、阜阳双古堆太乙九宫式盘；⑥ 白晋—莱布尼茨通信、Lo Shu magic square 西传
  - 古籍原文逐段双源核对（ctext.org + 维基文库/识典古籍），异文记 Y-xx、核对失败记 U-xx
  - **G1 质量门**：事实无因果/判断词、可验证、可溯源、数字/URL/年代完整
- **Acceptance Criteria Addressed**: AC-2、AC-3、AC-8
- **Test Requirements**:
  - `rule` TR-1.1: 事实草稿 ≥50 条，每条含编号、客观陈述、≥1 个信源 URL；先秦两汉原典段落均有双源 URL；证据：调研记录
  - `rule` TR-1.2: G1 检查——事实条目无"因为/所以/导致/错误"等因果判断词；异文 Y-xx 与未核对 U-xx 清单存在；证据：清单自查
  - `rubric` TR-1.3: 信源权威性；scale 1-5；anchors 1=通俗自媒体为主 / 3=原典有双源但现代研究信源弱 / 5=原典双源 + 期刊/出版社级现代研究信源齐备；threshold >= 4；证据：信源分级清单

## Task 2: 创建分组入口与 bundle 骨架
- **Status**: `pending`
- **Priority**: high
- **Depends On**: T1
- **Description**:
  - 创建 `think/hetu-luoshu/index.md`（仿 think/yinyangjia/index.md：`type: group`、分组简介、知识包列表表、hidden toctree 含 `hetu-luoshu/index`）
  - 创建 `think/hetu-luoshu/hetu-luoshu/` 目录骨架：`concepts/`、`examples/`、`references/` 子目录
  - 创建 bundle 根 `index.md`（仿 yinyangjia bundle 根：type OKF、title/description/tags/version/source/generated/verified/status/stale_after/okf_version；⚠️ 名实警示段、三层框架速览表、📚 快速导航、🚀 分读者快速开始、📖 学习路径、hidden toctree 引 concepts/examples/references/facts/insights/patterns/log）
  - 注意：T2 写 index.md 时导航链接指向的文件须在 T3–T6 全部创建（占位清单先行，链接不得 404）
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-2.1: 分组 index frontmatter 含 `type: group` 且 toctree 含 `hetu-luoshu/index`；bundle 根 frontmatter 含 type/okf_version/generated/verified/status/stale_after；证据：文件内容
  - `rule` TR-2.2: bundle 根 toctree 列出的 7 个目标（concepts/index、examples/index、references/index、facts、insights、patterns、log）在 T6 完成后全部存在；证据：T8 质量门

## Task 3: 创建 concepts/ 概念文档（12 篇 + index）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: T2
- **Description**:
  - `concepts/index.md`：分节导航表（名实框架/原典层/宋传谱系/图系三宗/数理/辨伪/出土与西传）+ hidden toctree 全 12 篇
  - 12 篇概念文档（文件名与内容见 spec FR-3）：00 名实之辨与阅读地图、01 先秦两汉记载、02 汉易象数基础、03 陈抟传承谱系、04 刘牧《易数钩隐图》、05 朱熹/蔡元定《易学启蒙》、06 邵雍先天学、07 周敦颐《太极图说》、08 数理结构、09 辨伪学史、10 出土与实物、11 影响与西传
  - 每篇 `type: Concept` frontmatter（title/description/tags/sources）；事实陈述引用 F 编号；术数内容严守学术辨析边界（AC-4）；推测性结论显式标注
- **Acceptance Criteria Addressed**: AC-1、AC-3、AC-4、AC-5
- **Test Requirements**:
  - `rule` TR-3.1: 12 篇 + index 共 13 个文件全部存在，每篇含合法 frontmatter（type: Concept），kebab-case 文件名；证据：目录清单
  - `rule` TR-3.2: 五项关键论断（宋代定型/图名互易/三层不混/凌家滩推测标注/莱布尼茨关系）在相关篇目中表述准确且引 F 编号；证据：逐篇抽查
  - `rule` TR-3.3: 无占卜/风水/排盘操作步骤（AC-4）；证据：全文关键词与内容审查
  - `rubric` TR-3.4: 单篇可读性（是什么/为什么/怎么读结构）；scale 1-5；anchors 1=资料堆砌无导读 / 3=内容完整但行文教科书化缺入口 / 5=每篇有定位提示、术语随文注释、与阅读地图呼应；threshold >= 4；证据：V 评审新人视角

## Task 4: 创建 examples/ 实践示例（3 篇 + index）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: T2
- **Description**:
  - `examples/index.md`：导航表 + hidden toctree
  - `01-xici-reading.md`：《系辞上》"天一地二…天地之数五十有五"章 + 《顾命》河图条 + 《洪范》九畴条**原文全录、双源核对**，逐句白话大意与概念注释，异文 Y 标注
  - `02-diagram-reading.md`：通行本河图/洛书/先天八卦图/太极图读图实操——点数统计、方位五行配属、洛书纵横斜各十五幻方亲手验证、先天卦序加一倍法推演、太极图五层生成读法
  - `03-reading-plan.md`：五阶段通读计划（先秦记载→汉易数理→宋代三宗图系→清代辨伪→出土与西传），每阶段书目、检验标准、常见陷阱
- **Acceptance Criteria Addressed**: AC-2、AC-5
- **Test Requirements**:
  - `rule` TR-4.1: 01 篇所录原文与双源逐字一致，异文已登记；证据：TR-1.1 双源记录 + 抽查比对
  - `rule` TR-4.2: 02 篇幻方验证步骤可复算（纵横斜三组各=15）、加一倍法推演链完整（1→2→4→8→64）；证据：文中推演过程自洽
  - `rubric` TR-4.3: 实操可跟做性；scale 1-5；anchors 1=只有结论无步骤 / 3=有步骤但缺"做完怎么知道对"检验 / 5=每步有输入、动作、预期结果与检验标准；threshold >= 4；证据：V 评审新人视角

## Task 5: 创建 references/ 信源文档（4 篇 + index）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: T2
- **Description**:
  - `references/index.md`：信源总登记表（分级说明）+ hidden toctree
  - `01-core-texts.md`：先秦两汉原典信源——ctext.org/维基文库/识典古籍具体页面 URL、版本说明、稳定性与风险标注
  - `02-song-qing-works.md`：宋清专著版本分级——《易数钩隐图》《易学启蒙》《周易本义》《皇极经世书》《太极图说》《易图明辨》《易学象数论》《图书辨惑》《河图洛书原舛编》的传世版本（道藏/通志堂经解/四库/现代整理本）与获取途径
  - `03-modern-scholarship.md`：现代研究——朱伯崑《易学哲学史》、《文物》1989(4)、凌家滩正式发掘报告（文物出版社 2006）、李学勤/饶宗颐等论著，含证据层级与 URL
  - `04-cross-ref.md`：库内交叉引用（yinyangjia/confucian/confucius/laozi/zhuangzi/huangdi-neijing/daoyi/fangzhong/yangsheng 相关束）+ 外部数字人文资源
- **Acceptance Criteria Addressed**: AC-2、AC-8
- **Test Requirements**:
  - `rule` TR-5.1: 4 篇 + index 全部存在，frontmatter type: Reference；库内交叉引用链接指向真实存在的 bundle 路径；证据：链接抽查
  - `rule` TR-5.2: 关键 URL（ctext 原典页、《文物》/出版社信息）抽测 ≥10 条可达或可查证；不可达者已换源或登记 U-xx；证据：抽测记录

## Task 6: 工作文档定稿（facts / insights / patterns 初稿 / log）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: T3、T4、T5
- **Description**:
  - `facts.md`：R 阶段事实定稿入库（≥50 条 F 编号，按"原典记载/宋传谱系/图系内容/辨伪/出土/西传"分组制表；Y 异文、U 未核对专节；含分层约定说明）
  - `insights.md`：I 阶段 ≥4 条四元组洞察（陈述/证据 F 编号/反常识/行动），候选方向：①名实三层混用是大众误读总根源；②"图出宋代"不是贬低而是经学史常识，清儒辨伪有方法论价值；③河图洛书的真正硬核是数理（幻方/生成数）而非神秘主义；④出土实物（凌家滩/式盘）把符号史推向史前但证据链有层级
  - `patterns.md`：E 阶段模式**初稿**（"层累符号史阅读法"：名物层→图式层→附会层三层剥离 + 双源核对 + 争议并列；含触发场景、3-7 步骤、≥3 反模式、检验标准、跨领域迁移示例如其他层累符号/商标化经典），**V 评审后定稿**
  - `log.md`：创建日志（日期、七概念各阶段过程、结构清单、信源概况、移交事项）
  - **G2 门**（洞察四元组完整、≥3 条、有反常识）；**G3 门初检**（模式要素齐备，V 后复核）
- **Acceptance Criteria Addressed**: AC-1、AC-8
- **Test Requirements**:
  - `rule` TR-6.1: facts.md 条目 ≥50、编号连续、分组清晰，Y/U 专节存在；证据：文件统计
  - `rule` TR-6.2: insights.md ≥4 条且每条含陈述/证据(F 编号)/反常识/行动四要素；证据：逐条核对
  - `rule` TR-6.3: patterns.md 含触发场景（适用/不适用边界）、3-7 步骤、≥3 反模式、检验标准、≥1 跨领域迁移示例；证据：结构核对

## Task 7: 更新两级导航索引（C 入库）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: T6
- **Description**:
  - 更新 `think/index.md`：frontmatter description 补 hetu-luoshu、正文导览段补充分组、分组导航表加行、toctree 加 `hetu-luoshu/index`（更新前先重读最新文件，防并行会话冲突）
  - 更新 `bundles/index.md`：frontmatter `total_bundles` 324→325、`groups` 61→62（domains 14 不变）；正文"当前共 N 个知识包…N 个分组"计数行；think 域节标题"28 束 · 17 组"→"29 束 · 18 组"；think 分组表加 hetu-luoshu 行；两处 mermaid（生态关系概览、推荐入门路径）think 节点标签补 hetu-luoshu
  - **计数最终以 `invoke gates.bundles` 实际对账为准**，若与预估不符以脚本输出修正
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `rule` TR-7.1: think/index.md 表格行、toctree、description 三处一致更新；证据：git diff
  - `rule` TR-7.2: bundles/index.md 五面（frontmatter/计数行/域节标题/分组表/toctree）计数一致；证据：T8 gates.bundles 输出

## Task 8: 质量门与构建验证
- **Status**: `pending`
- **Priority**: high
- **Depends On**: T7
- **Description**:
  - 在 `projects/awesome-okf-xs` 目录依次运行：`invoke gates.toctrees`（零断链零孤立）、`invoke gates.utf8`（UTF-8 无 BOM）、`invoke gates.bundles`（束/组/域三角对账）、`invoke build`（Sphinx 构建零错误）
  - 按记忆约定：OKF 子模块有并行会话风险，若 gates.bundles 报计数不一致，先重读 bundles/index.md 最新状态再修正本束相关行；提交（本任务不 commit）前须显式核对目标文件
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `rule` TR-8.1: 四条命令退出码均为 0，输出无 FAIL/ERROR；证据：完整命令输出记录

## Task 9: V 阶段独立对抗评审与修复
- **Status**: `pending`
- **Priority**: high
- **Depends On**: T8
- **Description**:
  - 委托新鲜上下文的只读评审（general_purpose_task），给评审者：用户目标、仓库根、spec/tasks 绝对路径、bundle 目录、质量门输出；四视角审查：
    1. **魔鬼代言人**：事实/信源攻击——抽查 F 条目与 URL、双源核对真实性、五项关键论断、异文/U 项处置
    2. **新人视角**：零基础能否按阅读地图进入、读图实操可跟做、术语是否随文解释
    3. **老板视角**：定位是否为"权威原文+学术解读阅读教程"而非百科/论文/术数手册；术数边界；篇幅与结构 ROI
    4. **未来视角**：stale_after 合理性、哪些内容会过时（URL/考古新发现）、争议标注是否留了更新接口
  - 评审意见 ≥5 条具体问题、≥2 条采纳修正；结果写入本 spec 目录 `review.md`
  - fail 项 materialize 为本文件 pending Issue（I-1…），修复后 patterns.md 按 V 意见**定稿**（G3 复核）并复跑 T8 质量门；修复后回归检查
- **Acceptance Criteria Addressed**: AC-3、AC-4、AC-5、AC-7、AC-8
- **Test Requirements**:
  - `rule` TR-9.1: review.md 存在且含四视角评审记录、≥5 条具体意见、采纳修正记录；最新 Review Result = pass；证据：review.md
  - `rule` TR-9.2: 所有 actionable finding 有对应修复且复跑 gates 全通过；证据：修复记录 + 质量门输出
  - `rubric` TR-9.3: 评审实质性（无表演式客套）；scale 1-5；anchors 1=无具体问题 / 3=有问题但浅 / 5=问题具体到文件/段落/论断且含反证；threshold >= 4；证据：review.md 意见内容

## Task 10: 收尾与看板登记
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: T9
- **Description**:
  - 在 `.trae/specs/standards-tools/README.md` 登记本 spec（按该看板既有格式）；按需更新 `.trae/specs/README.md` 待办/计数
  - 输出任务完成总结（产出物清单、质量门记录、评审结论、未决 U 项清单）
  - **不执行 git commit**（用户未明确要求；OKF 子模块提交由用户统一处理，总结中给出建议的提交粒度）
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-10.1: standards-tools README 已登记本 spec 且链接可达；证据：文件 diff
  - `rule` TR-10.2: 总结含产出物清单（文件数/字数）、四命令质量门结果、review 结论、U-xx 未决清单；证据：总结文本

# Task Dependencies

- T1（R 调研）→ T2（骨架）→ T3/T4/T5（三类文档，相互可并行）→ T6（工作文档定稿）→ T7（索引）→ T8（质量门）→ T9（V 评审+修复+E 定稿）→ T10（收尾）
- 七概念质量门映射：G1=T1/TR-1.2；G2=T6/TR-6.2；G3=T6 初检 + T9 复核定稿；V 门=T9；C（入库）=T7/T8/T10（不含 git commit）
