---
type: tasks
title: 手势×声乐教学 OKF 教程束 - 实施计划
session: sc-20260902-gesture-vocal-wiki
chain: F→R→I→E→V→C
---

# 手势辅助声乐教学教程束 - 实施计划（任务分解与优先级）

> 执行约定：每个任务委托一个子智能体（general_purpose_task）串行执行；工作目录 `d:\spaces\SpecWeave\projects\awesome-okf-xs`；正文中文、文件名 kebab-case 英文；所有文件 UTF-8 无 BOM、LF；frontmatter 双引号标量内禁止 ASCII 双引号（中文引号用全角“”）；任务完成后更新本文件状态。

## [x] Task 1: F+R 阶段——双源事实调研与 facts/references 产出

- **Priority**: high
- **Depends On**: None
- **Description**:
  - 完成 F 阶段公理界定（写入 insights 素材，不在本任务成文）：手势教学的本质公理——"声音参数（音高/呼吸/共鸣/节奏）不可见，手势是声音→身体动作的转译器"；手势分两套逻辑（视唱符号化手势 vs 声乐机能提示手势）；脚手架终须撤除。
  - Web 公开信源调研（WebSearch/WebFetch，每条事实 ≥2 独立信源，不足者标（单源待核）），产出：
    - `doc/bundles/yishu/vocal/gesture-vocal-pedagogy/facts.md`：GV-01 起编号，≥25 条，纯客观陈述、无因果词；信源 URL 逐条内嵌。
    - `doc/bundles/yishu/vocal/gesture-vocal-pedagogy/references/01-core-books-methods.md`：三大体系著作/机构/教材信源登记。
    - `doc/bundles/yishu/vocal/gesture-vocal-pedagogy/references/02-science-embodied.md`：具身认知与音乐教育实证信源登记。
  - 事实覆盖点（供调研清单，实际以信源为准）：Sarah Glover（1793-1867）Norwich sol-fa 与 sol-fa ladder；John Curwen（1816-1880）《Standard Course of Lessons on the Tonic Sol-fa Method》版本年与手型手势来源；Zoltán Kodály（1882-1967）与柯达伊教学法、International Kodály Society（1975）、Kecskemét Kodály Institute、OAKE；七唱名手型与垂直高度（do 腰位握拳 … ti 额/高位食指 … 高 do 头顶握拳）的标准描述；Émile Jaques-Dalcroze（1865-1950）体态律动、日内瓦学院、《Rhythm, Music and Education》（1921 英译）；指挥图式教材（Hermann Scherchen《Handbook of Conducting》/Max Rudolf《The Grammar of Conducting》版本年）；金铁霖（1940-2022）启发式感觉教学与中国音乐学院；《义务教育艺术课程标准（2022年版）》音乐核心素养与课标中柯尔文手势使用；Lakoff & Johnson《Philosophy in the Flesh》（1999）垂直空间隐喻；手势/动觉辅助视唱音准的实证研究（可检索 Kodály hand signs sight-singing intonation study）。
  - frontmatter：facts.md 用 `type: OKF`（参照 yishu/liaoyu/music-therapy/facts.md 体例，sources 列表 + generated/verified/status/stale_after）；references 两文同样 `type: OKF`。
- **Acceptance Criteria Addressed**: AC-3, AC-11
- **Test Requirements**:
  - `programmatic` TR-1.1: facts.md 存在且 GV 编号条目 ≥25；扫描无"因为/导致/所以/由于"等因果词（引文标题中的除外，需人工复核）。
  - `programmatic` TR-1.2: 每条 GV 事实含至少 1 个 http(s) URL；双源条目占比 ≥80%，其余显式标注（单源待核）。
  - `programmatic` TR-1.3: 三个文件 YAML frontmatter 可被 `yaml.safe_load` 解析（Python 一行扫描），type 字段非空，无 BOM。
  - `human-judgement` TR-1.4: 七唱名手型描述（手型+高度）与至少 2 个权威教学信源（如 OAKE/IKS/音乐学院教材/权威百科）一致；人物生卒年、著作年份无硬错误（评审 rubric：任一人物生卒/著作年错误即 P0）。
- **Notes**: 信源优先级：官方机构站 > 权威出版社/大学 > 百科；网络中文资料对"柯尔文/柯达伊手势"手型描述矛盾多，以英文权威源（Kodály 协会、音乐教育教材）为基线，中文教材作对照。事实登记纯客观，阐释留给后续篇章。

## [x] Task 2: F+I 阶段——束骨架、导航索引与架构洞察

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建束骨架文件（内容先搭结构与导航表，正文在 Task 3-5 填充）：
    - `index.md`（束根，含 `okf_version: "0.2"`、type: OKF、完整 tags/description、安全提示 blockquote、快速导航三表、读者路径 mermaid 图、toctree：concepts/index、examples/index、references/index、facts、insights、log）
    - `concepts/index.md`、`examples/index.md`、`references/index.md`（各含分组导航表 + toctree 条目，references/index 收录 01/02 两文）
    - `insights.md`（≥4 条四元组洞察：陈述/证据引 GV 编号/反常识/行动，覆盖 FR-3 四个核心命题）
    - `log.md`（初始化：2026-09-02 编纂日，R/F/I 阶段记录先行落盘）
  - frontmatter 体例对齐姊妹束 meitong-yanyin-pedagogy（generated.by: `agent:seven-concepts-cmd`、verified.by: `process:seven-concepts-v`、status: stable、stale_after: 2027-09-02）。
  - 束根需预留封面图位置（免责声明 blockquote 之后、快速导航之前），但图片引用行在 Task 6 插入。
- **Acceptance Criteria Addressed**: AC-2, AC-10, AC-11
- **Test Requirements**:
  - `programmatic` TR-2.1: 束根 index.md frontmatter 含 okf_version: "0.2"（仅此文件允许）；其余文件无该字段。
  - `programmatic` TR-2.2: 束根 toctree 含 6 条目（concepts/index、examples/index、references/index、facts、insights、log）；references/index toctree 含 01-core-books-methods、02-science-embodied。
  - `programmatic` TR-2.3: insights.md 含 ≥4 条洞察，每条四要素齐备且证据引用 GV- 编号。
  - `human-judgement` TR-2.4: 安全提示 blockquote 与姊妹束口径一致（疼痛/嘶哑即停、就医、不替代面授）；读者路径 mermaid 遵循安全编码（单行标签、中文标签双引号、无 `<br/>`、块内无空行）。
- **Notes**: toctree 条目用无后缀文件名；子目录 index 的 toctree 在 Task 3/4/5 内容就位后由对应任务补齐条目（本任务先建 concepts/index 与 examples/index 的表头骨架，条目随内容追加）。

## [x] Task 3: E 阶段（上）——concepts 00-03 四篇撰写

- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 撰写概念层前 4 篇（每篇 2000-4500 中文字符，面向零基础读者，"要领→问题→时机→错误"四要素文体）：
    - `concepts/00-overview-why-gestures.md`：入门地图（读者画像四分支、术语地图：手势/柯尔文手势/唱名/音高/拍点/律动、与姊妹束 meitong-yanyin-pedagogy 的分工与链接、安全边界、学习顺序）。
    - `concepts/01-why-gestures-work.md`：具身认知与手势有效原理（垂直空间隐喻 pitch=height、视听动觉三通道编码、镜像模仿、脚手架与内化撤除）；事实引 GV 编号。
    - `concepts/02-curwen-hand-signs.md`：柯尔文七唱名手势逐项表解（每唱名：手型描述+身体高度+作用+高频错法，七行总表 + 分节详解）、Glover→Curwen→Kodály 源流、镜面教学（教师面向学生时左右手/方向问题）、中国中小学教材使用现状；预留合集图位置（图注在 Task 6 插入）。
    - `concepts/03-vocal-studio-gestures.md`：声乐课堂五类手势（呼吸类：抱球/闻花/吹纸条；打开类：打哈欠/手掌下压；共鸣类：点眉心/画通道；线条类：手掌上行下行/画圈；咬字起收类：拉唇/起收拍），每类"动作要领→针对的发声问题→使用时机→常见错误"，与姊妹束 concepts/05、06、07 交叉链接（相对路径 `../../meitong-yanyin-pedagogy/concepts/05-eight-steps-silent.md` 形态）。
  - 同步把 4 篇追加进 `concepts/index.md` 导航表与 toctree。
- **Acceptance Criteria Addressed**: AC-4, AC-10
- **Test Requirements**:
  - `programmatic` TR-3.1: 4 个文件存在、frontmatter type: OKF 可解析、无 BOM；concepts/index.md toctree 含 00-03 四条目且无断链。
  - `human-judgement` TR-3.2: 02 篇七唱名表与 facts 登记一致（手型/高度无矛盾）；每个声乐手势四要素齐备；交叉链接路径正确（人工点击核对 3 处）。
  - `human-judgement` TR-3.3: 新手可懂性 rubric——零基础读者能照表做出 do/mi/sol 三个手势并说出高度差异；术语首次出现有解释。
- **Notes**: 手型描述用精确日常语言（如"do：四指握拳、拇指轻搭食指外侧，手心向内，置于腰腹高度"），避免依赖图片才能理解；图片是辅助不是唯一载体。

## [ ] Task 4: E 阶段（中）——concepts 04-07 四篇撰写

- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 撰写概念层后 4 篇：
    - `concepts/04-conducting-basics.md`：指挥手势基础——拍点与图式（2 拍下-上、3 拍下-外-上、4 拍下-里-外-上，文字轨迹描述+图示位置预留）、起拍/收拍/保持、右手拍点左手表情的分工、合唱排练组织手势（呼吸提示、进入、强弱）；与 02 柯尔文手势的分工说明（指挥面向群体组织，柯尔文面向音高学习）。
    - `concepts/05-dalcroze-eurhythmics.md`：体态律动定位——Dalcroze 生平与方法、节奏/力度/乐句的全身表达、与手部手势的互补（手=精细符号，身=整体节奏）、课堂简易活动设计（走步/拍手/传导）。
    - `concepts/06-teaching-sequence.md`：手势教学五序列（准备-呈现-练习-内化-撤除）+ 教师手势规范（镜面示范、幅度、时机、左右手约定）+ 一对一与集体课差异 + 与听觉训练的主从关系（手势服务听觉，不替代）。
    - `concepts/07-pitfalls.md`：反模式集（≥10 条，每条：表现→为什么错→正确做法）——七手势高频错法（如 fa 拇指方向、ti 与高音 do 混淆）、手势依赖不撤除、手势高度与音高脱节、只看手不听音、用手势替代模唱、集体课手势幅度过大干扰、镜面方向混乱、对嗓音问题用手势硬纠而不就医等；含安全提示（手势解决不了器质性问题）。
  - 同步把 4 篇追加进 `concepts/index.md` 导航表与 toctree（至此 8 篇齐）。
- **Acceptance Criteria Addressed**: AC-4, AC-10
- **Test Requirements**:
  - `programmatic` TR-4.1: 4 文件存在且 frontmatter 合规；concepts/index.md toctree 含 00-07 全部 8 条目；`invoke gates.toctrees` 对新束无断链无孤立（允许 examples 未完成期间的已知缺口在 Task 5 后归零，任务结束时 concepts 子树自洽）。
  - `human-judgement` TR-4.2: 拍点图式文字描述与经典指挥教材一致（2/3/4 拍方向序列无错）；反模式 ≥10 条且具体可辨认；06 篇五序列与脚手架理论自洽。
  - `human-judgement` TR-4.3: 07 篇安全提示与束根口径一致；反模式不与姊妹束纠错篇矛盾（交叉核对）。
- **Notes**: 指挥图式轨迹图为 Task 6 的第 4 张图，本篇预留图注位；Mermaid 不适合画空间轨迹，用文字+seedream 图。

## [/] Task 5: E 阶段（下）——examples 3 篇实践示例

- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 撰写实践层 3 篇（步骤化、剂量化、自检标准化）：
    - `examples/01-solfege-daily-routine.md`：柯尔文手势视唱每日 10-15 分钟流程——Day0 单手 do-mi-sol 三音 → 七音音阶 → 音程跳进 → 短句模唱 → 《小星星》等简单歌曲带手势；每阶段配剂量（天数/次数）、自检标准（手势高度与音高同步、录音对比）、撤手势节点。
    - `examples/02-vocal-warmup-gestures.md`：20 分钟声乐练声手势流程——抱球呼吸（3 分钟）→ 打哈欠打开（2 分钟）→ 哼鸣点位置（3 分钟）→ 手势带音阶上下行（6 分钟）→ 母音乐句与线条手势（6 分钟）；与姊妹束 `../meitong-yanyin-pedagogy/examples/01-daily-practice-routine.md` 衔接说明（本篇是手势增强版，不替代其机能训练剂量）。
    - `examples/03-group-class-lesson.md`：45 分钟儿童集体视唱/合唱课例——结构表（导入5/新授15/游戏10/合练10/小结5）、手势+指挥+律动的组合时机、教师站位与镜面、课堂游戏（手势接龙、看手猜音）、纪律与安全（动作幅度、嗓音保护）。
  - 同步完善 `examples/index.md` 导航表与 toctree（3 条目）。
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-5.1: 3 文件存在、frontmatter 合规；examples/index.md toctree 含 3 条目；新束全部 .md 被某级 toctree 覆盖（束根→子 index→子文件 链路完整）。
  - `human-judgement` TR-5.2: 每篇含分步流程 + 时间/频次剂量 + 可观察自检标准（评审 rubric：照文可执行无歧义步骤占比 ≥90%）。
  - `human-judgement` TR-5.3: 示例 02 与姊妹束每日练声清单无矛盾（剂量/顺序不冲突，链接有效）。
- **Notes**: 示例是教程"可照做"承诺的兑现物，禁止"多练习""注意音准"类空话；每个动作必须有可观察达标信号。

## [/] Task 6: seedream 配图生成与嵌入（5 张暖灰纸感插画）

- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 使用 GenerateImage（seedream 插件）生成 5 张图，落 `doc/_static/bundles/yishu/vocal/gesture-vocal-pedagogy/images/`：
    1. `hero-gesture-voice.jpg`（封面，landscape_16_9）：暖灰纸感编辑插画——音乐教室中教师抬手做音高手势，掌心升起暖色绸带状抽象音流，米白与暖灰色调。
    2. `curwen-hand-signs-chart.jpg`（portrait_4_3）：七只手势沿垂直阶梯从低到高排列的合集示意图，纸感图表风，手部为视觉主体（提示词明确：warm gray paper texture editorial illustration, seven hands showing solfège hand signs on vertical steps, soft warm-gray palette, clean educational chart style）。
    3. `vocal-breath-ball.jpg`（landscape_4_3）：教师侧面双手环抱一个大球示意腰腹呼吸扩张，纸感插画。
    4. `conducting-patterns.jpg`（landscape_4_3）：指挥手势拍点轨迹示意——2/3/4 拍三组手部轨迹线条与箭头，纸感图表风。
    5. `child-class-gestures.jpg`（landscape_16_9）：儿童视唱集体课，老师与孩子们一起抬手、手势高低错落，温暖教室氛围。
  - 风格统一：全部 warm gray paper texture、暖灰底+米白+深灰褐、柔和窗光、编辑插画/图表风；不出现文字（AI 文字易错），标签由 Markdown 正文承担。
  - 嵌入位置：封面图→束根 index.md（安全 blockquote 后、快速导航前，引导句+图片行）；合集图→concepts/02 七唱名总表后；呼吸图→concepts/03 呼吸类小节；指挥图→concepts/04 拍点图式小节；课堂图→examples/03 课例结构后。每处配完整 alt（画面描述）+ 图注（"图 N｜…（示意图，手型以正文表格为准）"）。
  - 图片文件若生成到临时目录需移动/复制到目标路径；确认最终落盘 5 张 jpg。
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-6.1: 目标 images/ 目录下存在 5 个 jpg 文件且非 0 字节；正文 `/_static/bundles/yishu/vocal/gesture-vocal-pedagogy/images/` 引用恰好 5 处、与文件名一一对应。
  - `human-judgement` TR-6.2: 逐图审查——手部无六指/融合/明显解剖错误（rubric：手部为画面主体的 3 张图，每张手部错误 ≤1 处轻微；严重错误如六指/多指融合即重生，单图最多重生 2 轮）；五图风格统一为暖灰纸感；图中无乱码文字。
  - `human-judgement` TR-6.3: 图注诚实声明示意性质；alt 文本为完整中文画面描述（与 liaoyu 六束体例一致）。
- **Notes**: AI 手部高风险——若合集图 2 轮后手部仍不可接受，降级为"垂直阶梯+抽象手位色块"示意方案（记录于 log.md）；所有生成结果在 Task 7 V 阶段复审。

## [ ] Task 7: V 阶段——四视角对抗审查与修正

- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 以独立子智能体执行对抗审查（审查者不得是撰写者本人，需重新读全部文件），输出 ≥8 条具体意见（P0-P3 分级），四视角覆盖：
    - 魔鬼代言人：史实硬伤（生卒年/著作年/机构名/手型描述/拍点方向）、信源是否真支持结论、是否有网络讹传照抄、AI 图手部错误。
    - 新人视角：术语未解释、第一步不知道做什么、缺 Hello World 级示例、跨篇引用断裂。
    - 老板视角：自学者/教师拿到手能否真用、剂量是否可执行、安全风险（嗓音/儿童）。
    - 未来视角：手势体系归属是否会被学界更新、图片风格是否过时、与姊妹束边界一年后是否仍清晰。
  - 专项核对：①facts 每条 URL 抽检 ≥10 条可访问且内容相符；②七唱名手型与权威英文源逐项对表；③指挥 2/3/4 拍方向序列；④frontmatter YAML 全束 `yaml.safe_load` 扫描；⑤双引号标量内 ASCII 引号扫描；⑥图片引用路径与文件一一对应。
  - 采纳 ≥3 条意见修正全部 P0/P1 问题；修正记录与未采纳理由写入 `log.md` 的 V 阶段小节。
- **Acceptance Criteria Addressed**: AC-7, AC-3, AC-11
- **Test Requirements**:
  - `programmatic` TR-7.1: log.md 含 V 阶段审查记录（意见清单含 P 级、采纳/不采纳结论）；全束 .md 通过 yaml.safe_load frontmatter 扫描；UTF-8 无 BOM 扫描通过。
  - `human-judgement` TR-7.2: 审查意见 ≥8 条且无"写得很好"类客套；P0/P1 全部修复并有 before/after 说明；史实零硬错误（对照 facts 双源基线）。
  - `human-judgement` TR-7.3: 修正后回归抽查——被修复文件复读确认改动落盘（防并行 Edit 回退），同文件多处修改逐条串行复验。
- **Notes**: 审查发现 facts 层错误时回 Task 1 修 facts 并联动改正文；遵循"事实→洞察→正文"顺序，禁止正文先于事实定稿。

## [x] Task 8: C 阶段——三处注册、门控与原子提交

- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 注册更新（共享索引竞态纪律：编辑前先跑 gates 取树真值→编辑→立即验证→提交，全程紧凑）：
    - `doc/bundles/yishu/vocal/index.md`：知识包表加 gesture-vocal-pedagogy 行（定位+说明）、toctree 加 `gesture-vocal-pedagogy/index`、frontmatter description/tags 与正文导语更新为两束。
    - `doc/bundles/yishu/index.md`：声乐组描述更新（两束并列）、域导语与分组表 vocal 行说明更新。
    - `doc/bundles/index.md`：以 gates 重算为准更新 total_bundles、mermaid yishu 行束数、yishu 域节标题束数、vocal 组行束数（1→2）与说明文字；groups/domains 不变。
  - 门控验证（cwd=projects/awesome-okf-xs，py314 环境）：
    - `conda run --no-capture-output -n py314 invoke gates.all` 三门全绿；
    - 定向构建：`conda run --no-capture-output -n py314 python -m sphinx -b dummy -E doc .temp/dummy <新束全部 .md + vocal/index.md + yishu/index.md + bundles/index.md>` 退出码 0；
    - 清理 `.temp/dummy` 构建产物（若在仓库内）。
  - 原子提交（子模块 awesome-okf-xs 内）：git add **仅**新束目录、_static 新图、3 个注册文件与 log；`git add` 与 `commit` 分两次调用，中间 `git diff --cached --name-only` 核验暂存集无他会话文件；用 UTF-8 提交信息文件 `git commit -F`，信息形如 `docs(yishu): 新增手势辅助声乐教学教程束（柯尔文/课堂/指挥三体系+5图）`；**不 push**；提交后 `git show --stat` 验证。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-8, AC-9, AC-11, AC-12
- **Test Requirements**:
  - `programmatic` TR-8.1: `invoke gates.all` 退出码 0（utf8/toctrees/bundles 三门全过，计数五面对账一致）。
  - `programmatic` TR-8.2: 定向 sphinx dummy 构建退出码 0、无 ERROR；.temp/dummy 已清理。
  - `programmatic` TR-8.3: 暂存集仅含本任务文件（新束 ~18 个 .md + 5 张 jpg + 3 注册文件），无他会话 WIP；提交成功且中文无乱码；未执行 push。
  - `human-judgement` TR-8.4: 三处注册的说明文字与束实际内容一致（束数、篇数、图数描述准确）。
- **Notes**: 若 gates 报共享索引被并行会话改动（计数漂移），以 gates 输出为准重算补丁，不 reset 他人改动；提交后把 commit SHA 与变更摘要回报主会话。主仓库子模块指针是否 bump 留给用户决定（Open Question Q3）。
