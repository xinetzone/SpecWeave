---
type: spec
title: 手势×声乐教学 OKF wiki 教程束 - 产品需求文档
project: awesome-okf-xs / yishu / vocal
session: sc-20260902-gesture-vocal-wiki
chain: F→R→I→E→V→C（七概念·创新突破场景）
---

# 手势×声乐教学结合教程 OKF 知识包 - 产品需求文档

## Overview

- **Summary**：在 `projects/awesome-okf-xs/doc/bundles/yishu/vocal/` 下新建 OKF 知识包 `gesture-vocal-pedagogy/`（中文标题：《手势辅助声乐教学教程》），系统整合**三大手势体系**——柯尔文/柯达伊手势（Curwen/Kodály hand signs，唱名音高的空间化手型）、声乐课堂教学手势（呼吸/打开/共鸣/线条/咬字五类具象手势）、指挥手势基础（拍点图式与起收拍）——辅以达尔克罗兹体态律动（Dalcroze eurhythmics）与具身认知理论，产出"有信源、有步骤、有示意图、可照做"的中文教学型教程，并配 5 张 seedream 暖灰纸感编辑插画。
- **Purpose**：声乐/视唱教学中"抽象声音参数（音高、呼吸、共鸣、节奏）不可见"是核心教学难题；手势把声音参数转译为可见、可模仿的身体动作，是音乐课堂成本最低的可视化教具。现有公开中文资料零散、术语混乱（"柯尔文手势""柯达伊手势"混用）、手型描述互相矛盾、缺少声乐课堂场景的整合用法。本束把三大体系放到一张知识地图里，给自学者、音乐教师与家长一套可直接照做的手势教学方案。
- **Target Users**：①零基础歌唱/视唱自学者（KTV 爱好者、成人学唱歌）；②中小学/校外音乐教师与合唱指挥；③陪练家长与儿童音乐启蒙场景；④与姊妹束 `meitong-yanyin-pedagogy`（美通唱法与咽音体系）读者群高度重合。

## Goals

- G1：建成符合 OKF v0.2 规范的完整知识包（concepts/examples/references 三层 + facts/insights/log），通过 awesome-okf-xs 全部质量门（gates.all 与定向 Sphinx 构建 0 error）。
- G2：柯尔文七唱名手势（do ré mi fa sol la ti）的手型、空间高度、源流（Sarah Glover → John Curwen → Zoltán Kodály）描述准确、双信源可溯。
- G3：声乐课堂五类教学手势（呼吸/喉位打开/共鸣/音高线条/咬字起收）给出"动作要领→对应发声问题→使用时机→常见错误"的可照做映射。
- G4：指挥手势基础（2/3/4 拍图式、起拍收拍、双手分工）与合唱/集体课应用成篇。
- G5：3 篇实践示例（视唱每日手势练习、声乐练声 20 分钟手势流程、儿童/合唱集体课例）含步骤、剂量与自检标准。
- G6：5 张 seedream 暖灰纸感编辑插画（封面 + 柯尔文手势合集 + 呼吸手势场景 + 指挥拍点 + 集体课堂），落 `doc/_static/bundles/yishu/vocal/gesture-vocal-pedagogy/images/` 并在正文正确引用。
- G7：完成三处注册登记（vocal 组索引、yishu 域索引、bundles 总索引）并通过计数对账门。
- G8：全程七概念链路留痕（log.md 记录 R/I/E/V/C 各阶段），V 阶段对抗审查有实质意见与修正。

## Non-Goals (Out of Scope)

- 不重述发声机能训练细节（呼吸/咽音/混声/纠错/保健以姊妹束 `meitong-yanyin-pedagogy` 为准，本束仅交叉引用，不复制其内容）。
- 不做器乐教学手势、不做舞蹈/戏剧治疗手势（后者见 liaoyu 组 dance-drama-therapy 束）。
- 不生产视频/音频/交互式课件；图片为静态编辑插画（示意图定位，不承担解剖级精度）。
- 不做学术综述或音乐教育心理学 exhaustive 文献综述；科学信源以支撑教学结论为度。
- 不提交推送（push）——按子模块协作惯例，本地原子提交后等待用户统一推送。
- 不修改姊妹束 `meitong-yanyin-pedagogy` 的任何文件（仅在其已存在的锚点上做交叉链接）。

## Background & Context

- **仓库约定**（已调研确认）：
  - 束根 `index.md` 带 `okf_version: "0.2"`，frontmatter 遵循 `.agents/rules/frontmatter.md`（type 必填；generated/verified actor 约定；status/stale_after）。
  - 束标记：目录含 `concepts/`、`examples/`、`references/` 任一 marker 子目录即计 1 束（check-bundles-index.py 锚点规则）。
  - 束根 toctree 须覆盖全部 .md（含 facts、insights）；子目录 index.md 用 toctree 收录其子文件；条目用文件名（无 .md 后缀）。
  - 图片落 `doc/_static/bundles/<域>/<组>/<束>/images/`，正文以 `![alt](/_static/bundles/.../x.jpg)` 站点根绝对路径引用。
  - 姊妹束 meitong-yanyin-pedagogy 为成熟范本：10 concepts + 2 examples + 3 references + facts(81条) + insights + log，含 3 张解剖图。
  - seedream 配图先例：yishu/liaoyu 六束各 1 张暖灰纸感编辑插画，alt 文本为完整画面描述，插入位置为束根免责声明之后、快速导航之前。
- **门控命令**（py314 conda 环境，cwd=projects/awesome-okf-xs）：
  - `conda run --no-capture-output -n py314 invoke gates.all`（utf8 + toctrees + bundles 三门）
  - 定向构建：`python -m sphinx -b dummy -E doc .temp/dummy <显式文件列表>`（约 3 分钟/30 文件，0 error 即过）
- **共享索引竞态纪律**（项目记忆 verified 2026-09-01/02）：bundles/index.md 有并行会话写入；计数一律以 gates 重算为准，禁止手填；编辑后立即提交；git add 与 commit 分两次调用，中间核验暂存 blob；他会话未暂存改动绝不 add/reset。
- **七概念链路**：本任务为场景5（创新突破）融合知识沉淀——F（第一性原理：手势=声音参数→身体动作的转译器）→ R（双源事实登记）→ I（架构洞察）→ E（可照做教程萃取）→ V（强制对抗：史实准确性 + AI 手部图像审查 + 新手可懂性）→ C（门控 + 原子提交）。
- **内容敏感度**：公开内容（公开发布的教学法、公开信源），标准工作流，产出在子模块 `doc/bundles/`。

## Functional Requirements

- **FR-1（facts 事实层）**：`facts.md` 以 GV-01 起编号登记 ≥25 条客观事实，覆盖：Curwen（1816-1880）、Sarah Glover（1793-1867）、Kodály（1882-1967）、Dalcroze（1865-1950）生平与著作年份；七唱名手型与空间高度；Kodály 机构（IKS、Kecskemét Kodály Institute、OAKE）；Dalcroze 学院与著作；指挥图式经典教材（Scherchen、Max Rudolf）；金铁霖（1940-2022）启发式感觉教学；《义务教育艺术课程标准（2022年版）》音乐核心素养；具身认知/垂直空间隐喻代表文献。每条 ≥2 独立信源或标注（单源待核），信源 URL 逐条内嵌，无因果推断词。
- **FR-2（references 信源层）**：2 篇信源登记——`01-core-books-methods.md`（三大体系著作、机构、教材课标）与 `02-science-embodied.md`（具身认知、音乐教育实证、手势-音高映射研究），含 `references/index.md` 导航。
- **FR-3（insights 洞察层）**：`insights.md` 给出 ≥4 条四元组洞察（陈述/证据引 GV 编号/反常识/行动），核心包括：手势是"声音→身体"转译器而非装饰；视唱手势（柯尔文）与声乐课堂手势是两套逻辑（符号化 vs 机能提示）；脚手架必须随熟练撤除；身体记忆先于符号记忆的教学序列含义。
- **FR-4（concepts 概念层，8 篇）**：
  - `00-overview-why-gestures.md`：入门地图（读者画像、术语地图、与姊妹束关系、安全边界、学习顺序）
  - `01-why-gestures-work.md`：具身认知、垂直空间隐喻（pitch=height）、多通道编码、镜像模仿、脚手架理论
  - `02-curwen-hand-signs.md`：七唱名手型逐项表解（手型+高度+唱名+常见错法）、Glover→Curwen→Kodály 源流、中国教材使用现状、镜面教学方向问题
  - `03-vocal-studio-gestures.md`：五类声乐课堂手势（呼吸/打开喉位/共鸣位置/音高线条/咬字起收）的"要领→针对问题→时机→错误"映射，与咽音/美通练习的交叉引用
  - `04-conducting-basics.md`：2/3/4 拍图式轨迹、起拍/收拍/保持、双手分工、合唱排练中的组织手势
  - `05-dalcroze-eurhythmics.md`：体态律动定位（全身 vs 手部）、节奏/力度/乐句的身体表达、与手势体系的互补边界
  - `06-teaching-sequence.md`：手势教学五序列（准备→呈现→练习→内化→撤除）、教师手势规范（镜面、幅度、时机）、儿童集体课与一对一课差异
  - `07-pitfalls.md`：反模式集——手型错误示范（含七手势高频错法）、手势依赖不撤、手势与音高/发声不一致、用手势替代听觉训练、课堂纪律问题
- **FR-5（examples 实践层，3 篇）**：
  - `01-solfege-daily-routine.md`：柯尔文手势视唱每日练习（音阶→音程→短句→歌曲如《小星星》的分步流程、剂量、自检）
  - `02-vocal-warmup-gestures.md`：20 分钟声乐练声手势流程（呼吸抱球→打哈欠打开→哼鸣找位置→音阶上行下行→母音乐句），与姊妹束每日练声清单衔接
  - `03-group-class-lesson.md`：儿童集体视唱/合唱排练综合课例（45 分钟结构、手势+指挥+律动组合、教师站位与镜面、课堂游戏）
- **FR-6（视觉资产）**：5 张 seedream 生成暖灰纸感编辑插画（暖灰底、米白卡片、深灰褐视觉，与 liaoyu 六束风格统一）：
  1. `hero-gesture-voice.jpg`：束封面（音乐教室中教师抬手做音高手势，抽象暖色温音流从掌心升起）
  2. `curwen-hand-signs-chart.jpg`：七唱名手势沿垂直阶梯分布的合集示意（手部为视觉主体）
  3. `vocal-breath-ball.jpg`：声乐课堂呼吸手势场景（教师双手环抱大球示意腰腹扩张，侧面）
  4. `conducting-patterns.jpg`：指挥拍点轨迹示意（2/3/4 拍手部轨迹线条，纸感图表风）
  5. `child-class-gestures.jpg`：儿童视唱集体课（老师与孩子们一起抬手，手势高低错落）
  - 每张图配完整 alt 文本与图注；**图片定位为示意图**，手型精确性以正文表格为准（图注中诚实声明）。
- **FR-7（注册与导航）**：
  - `vocal/index.md`：知识包表加行、toctree 加 `gesture-vocal-pedagogy/index`、description/tags 更新
  - `yishu/index.md`：声乐组描述更新（两束并列）
  - `bundles/index.md`：frontmatter 计数（以 gates 重算为准）、mermaid yishu 行、域节标题束数、vocal 组行束数（1→2）与说明
- **FR-8（log 留痕）**：`log.md` 按 R/I/E/V/C 五阶段记录编纂过程、信源裁决、V 阶段意见与采纳情况、图片生成记录。
- **FR-9（安全与边界）**：束根与 07 篇含安全提示——练习疼痛/嘶哑即停就医（与姊妹束一致）、手势教学不替代听觉训练与面授、儿童课动作幅度安全。

## Non-Functional Requirements

- **NFR-1（事实可信）**：facts 全部条目双信源或显式（单源待核）；人物生卒年、著作年份、机构名与权威信源一致；信源 URL 可访问（V 阶段抽检）。
- **NFR-2（门控全绿）**：`invoke gates.all` 三门（utf8/toctrees/bundles）全过；定向 Sphinx dummy 构建新束全部文件 0 error；YAML frontmatter 无 Malformed（双引号标量内禁 ASCII 双引号，中文引号用全角“”）。
- **NFR-3（风格一致）**：正文中文、文件名 kebab-case 英文；与姊妹束体例一致（导航表、序号、图注格式、toctree 写法）；图片暖灰纸感风格与 liaoyu 六束统一。
- **NFR-4（原子化）**：单文件 500-5000 字符量级，语义完整；任务按 concepts 批次、examples、图片、审查、注册原子推进。
- **NFR-5（竞态安全）**：共享索引编辑遵循"gates 重算→编辑→立即提交"，add 与 commit 分离，暂存 blob 核验；不碰他会话 WIP。
- **NFR-6（可照做性）**：每篇实践/概念含明确步骤、剂量/频次、自检标准与 ≥3 条反模式（E 萃取 G3 门）。

## Constraints

- **Technical**：Markdown + MyST（myst_parser）+ Sphinx；图片为 seedream 生成的静态 jpg；不引入新依赖；所有命令在 Windows + py314 conda 环境执行（WSL 非必需）。
- **Business**：公开知识内容，版权分层——现代著作仅结论性转述+书目登记，不大段照抄；AI 生成图为原创插画，不模仿在世艺术家风格。
- **Dependencies**：seedream 图像生成插件（GenerateImage 工具）；awesome-okf-xs 子模块门控脚本；姊妹束 meitong-yanyin-pedagogy 已存在（交叉链接目标）。

## Assumptions

- A1："手势和声乐教学的结合"解读为：以声乐/视唱教学为应用场景，整合柯尔文手势、声乐课堂手势、指挥手势三大体系（而非仅指其中一种）；若用户只想要其中一种，可在审批时收窄。
- A2：目标读者与姊妹束一致（零基础自学者 + 音乐教师），教程深度对齐 meitong-yanyin-pedagogy。
- A3：AI 生成图像的手部解剖可能存在瑕疵（六指、手型错乱为已知高发问题），对策：图片定位为"氛围/位置示意"、精确手型以正文表格为准、V 阶段逐图审查不合格则重生（上限 2 轮/图）。
- A4：新束计数为 416+1=417（以实施时 gates 重算树真值为准，并行会话可能使基数漂移）。
- A5：本地提交后不推送，由用户决定推送时机（遵循项目记忆中的推送闸门惯例）。

## Acceptance Criteria

### AC-1：束结构完整且被门控识别为 1 束
- **Given**：新束目录 `yishu/vocal/gesture-vocal-pedagogy/` 已创建
- **When**：运行 `invoke gates.bundles`
- **Then**：vocal 组束数由 1 变为 2、yishu 域束数 +1、总束数 +1，五面对账无差异
- **Verification**： `programmatic`

### AC-2：toctree 完整无断链无孤立
- **Given**：束内全部 .md 文件就位
- **When**：运行 `invoke gates.toctrees`
- **Then**：无 broken link、无 orphan 文档；束根 toctree 覆盖 concepts/index、examples/index、references/index、facts、insights、log；子目录 index 覆盖其全部子文件
- **Verification**： `programmatic`

### AC-3：facts 事实层满足 G1 质量门
- **Given**：facts.md 完成
- **When**：审查事实登记
- **Then**：≥25 条 GV 编号事实；无"因为/导致/所以"等因果推断词；每条含信源 URL，双源或（单源待核）标注；七唱名手型描述与权威信源逐条一致
- **Verification**： `programmatic`（计数/因果词扫描）+ `human-judgment`（手型描述准确性）

### AC-4：概念层 8 篇覆盖三大体系且可照做
- **Given**：concepts/ 8 篇完成
- **When**：逐篇审查
- **Then**：FR-4 列出的 8 篇齐备；声乐手势篇每个手势含"要领→问题→时机→错误"四要素；反模式总计 ≥10 条且具体；与姊妹束交叉链接有效
- **Verification**： `human-judgment`

### AC-5：实践示例 3 篇含步骤剂量自检
- **Given**：examples/ 3 篇完成
- **When**：按示例模拟执行
- **Then**：每篇含分步流程、时间/频次剂量、可观察自检标准；示例 02 与姊妹束每日练声清单衔接不矛盾
- **Verification**： `human-judgment`

### AC-6：5 张 seedream 配图生成并正确引用
- **Given**：图片生成任务完成
- **When**：检查 _static 目录与正文引用
- **Then**：5 张 jpg 落于 `doc/_static/bundles/yishu/vocal/gesture-vocal-pedagogy/images/`；正文 5 处 `/_static/...` 引用与文件一一对应；alt 文本为完整画面描述；风格为暖灰纸感编辑插画
- **Verification**： `programmatic`（文件存在+引用计数）+ `human-judgment`（画面与手部质量）

### AC-7：V 对抗审查实质执行并修正
- **Given**：全部初稿与图片完成
- **When**：执行四视角对抗审查（魔鬼代言人/新人/老板/未来）+ 专项史实核对 + 逐图手部审查
- **Then**：审查意见 ≥8 条且具体（P0-P3 分级）；≥3 条被采纳修正；修正记录入 log.md；史实硬错误（人物/年份/手型）清零
- **Verification**： `human-judgment`

### AC-8：定向 Sphinx 构建 0 error
- **Given**：全部文件与注册更新完成
- **When**：运行 `python -m sphinx -b dummy -E doc .temp/dummy <新束全部文件+3个注册文件>`
- **Then**：构建退出码 0，无 ERROR（含无 Malformed YAML）
- **Verification**： `programmatic`

### AC-9：注册三处更新一致
- **Given**：注册编辑完成
- **When**：审查 vocal/index.md、yishu/index.md、bundles/index.md
- **Then**：三处均含新束条目/链接/计数；计数与 gates 输出一致；无手填错误数字
- **Verification**： `programmatic`

### AC-10：安全边界声明就位
- **Given**：束根与相关篇章完成
- **When**：检查安全提示
- **Then**：束根含嗓音安全 blockquote（疼痛即停就医、不替代面授）；07 篇含手势使用安全（不替代听觉训练、儿童动作幅度）
- **Verification**： `human-judgment`

### AC-11：UTF-8/frontmatter 合规
- **Given**：全部文件落盘
- **When**：运行 `invoke gates.utf8` 与 YAML 解析扫描
- **Then**：全部文件 UTF-8 无 BOM；frontmatter 可解析、type 字段齐备；双引号标量内无 ASCII 双引号
- **Verification**： `programmatic`

### AC-12：原子提交完成
- **Given**：全部门控通过
- **When**：执行 git 提交（子模块内）
- **Then**：提交为单一职责（新增手势教程束），暂存集核验无他会话文件混入；commit message 遵循 Conventional Commits 中文描述；不执行 push
- **Verification**： `programmatic`

## Open Questions

- [ ] Q1：教程范围是否认可"三大体系整合"解读（柯尔文 + 声乐课堂手势 + 指挥手势），还是希望收窄为某一种？（默认按整合执行）
- [ ] Q2：5 张配图清单是否合适？柯尔文手势合集图为高风险图（AI 手部精度），若 V 审查两轮不通过则降级为"垂直阶梯+抽象手位"示意图，是否接受？
- [ ] Q3：提交后是否需要同步主仓库子模块指针？（默认不操作，留待用户统一推送时处理）
