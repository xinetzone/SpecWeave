---
type: VisualPlan
title: 艺术疗愈六束视觉资产方案（R+I 阶段）
okf_version: "0.2"
generated: { by: "agent:visual-plan-subagent", at: "2026-09-02T17:30:00+08:00" }
status: draft-for-review
scope: projects/awesome-okf-xs/doc/bundles/yishu/liaoyu（6 束 + 组首页）
---

# 艺术疗愈六束视觉资产方案（R+I 阶段）

> 本文件是 seven-concepts 链路 R（事实采集/视觉点盘点）+ I（高价值可视化点洞察）阶段的产出物，供主代理审核后进入 E 阶段（Task 2 配图生成、Task 3 插入与 log 留痕）。
> 事实纪律（G1 事实门）：图中一切人名、年份、组织名、模型名、阶段名均可溯源到对应束正文或 facts 条目（每图附"事实来源"列），**无新造事实、无因果演绎**；单源待核条目照束内口径标注。
> 编码纪律：全部 Mermaid 草案遵循主仓库门禁（`.agents/scripts/check-mermaid.py`，VS Code 预览最小兼容子集）——代码块内无空行、非纯英文标签双引号包裹、无 Markdown 列表触发、**标签一律单行（禁 `<br/>` 与字面 `\n`，多行信息用「；」「，」分隔）**、`subgraph EN_ID ["标题"]`、边标签 `-->|"标签"|`；另禁带圈数字、中文方括号【】、Unicode 箭头、subgraph 内嵌套 direction。单行版本在 VS Code、GitHub 与子模块 Sphinx/MyST 渲染均兼容，Task 3 原样插入即可。
> 增量纪律：视觉资产只做表达层增量，不改动 frontmatter、事实正文、免责声明、toctree 与 facts/references。

## 一、配图方案表（7 张）

- **统一风格前缀**（每张 prompt 开头原样使用）：`warm muted palette, soft paper-textured editorial illustration, gentle healing mood, no text, no words, no letters`
- **统一安全后缀**（每张 prompt 结尾原样使用）：`, landscape composition, no medical scenes, no hospital, no clinical treatment, cozy and calm atmosphere`
- **尺寸**：全部 `landscape_16_9`；GenerateImage 的 path 参数不带扩展名，实际扩展名（.png/.jpg）Task 2 落盘后回写"实际文件名"列。
- **引用语法先例**（meitong 束）：`![中文 alt](/_static/bundles/yishu/vocal/meitong-yanyin-pedagogy/images/anatomy-diaphragm.png)`，本方案一律用 `/_static/bundles/yishu/liaoyu/...` 正斜杠绝对形式。
- **插入通则**：束 index.md 中，引导句 + 图片行紧邻 `## 📚 快速导航` 标题之前插入（即免责声明/特点段之后、导航之前）；组首页紧邻 `## 组内束导航` 之前插入。引导句独立成行，图片行独立成行，均为纯新增行。

| 编号 | 束 | 文件名（kebab-case） | 落盘目录（子模块内） | 插入位置与引导句 | alt 文本 | Seedream prompt（前缀 + 主题 + 后缀） | 尺寸 | 实际文件名（Task 2 回写） |
|---|---|---|---|---|---|---|---|---|
| I-1 | 组首页 liaoyu | `liaoyu-group-hero` | `doc/_static/bundles/yishu/liaoyu/images/` | `doc/bundles/yishu/liaoyu/index.md`：术语速览段之后、`## 组内束导航` 之前。引导句：`下图以六件艺术器物环绕成环，意象化呈现本组六束的分支结构。` | 暖灰纸感编辑插画：画笔与画架、竖琴、扬起的绸带、戏剧面具、羽毛笔与诗卷、古琴六件艺术器物沿环形路径环绕中央暖光，象征艺术疗愈六个分支 | 前缀 + `: six art objects arranged along a gentle circular path around a soft warm light — a paintbrush with small easel, a small harp, a flowing silk ribbon, two theater masks, a quill pen on a loose scroll, and a Chinese guqin zither — symbolizing six branches of arts and healing; cream and warm beige paper background, ochre and sage green accents` + 后缀 | landscape_16_9 | liaoyu-group-hero.jpg（445.3 KB） |
| I-2 | liaoyu-overview | `overview-arts-circle` | `doc/_static/bundles/yishu/liaoyu/liaoyu-overview/images/` | `doc/bundles/yishu/liaoyu/liaoyu-overview/index.md`：`## 三大特点` 列表之后、`## 📚 快速导航` 之前。引导句：`下图以多种艺术形态的环绕汇聚，呼应本束作为六束枢纽的定位。` | 暖灰纸感编辑插画：画架与空白画布、竖琴、舞鞋、喜剧悲剧双面具、羽毛笔与纸页、水墨卷轴在米白纸面上围成圆环，寓意多艺术形态的汇聚 | 前缀 + `: a flat-lay circle of diverse art forms on warm cream paper — an easel with blank canvas, a small harp, soft dance shoes, comedy and tragedy masks, a quill pen on open pages, and a small ink-wash scroll — surrounding a calm central empty space; muted ochre, sage and terracotta tones` + 后缀 | landscape_16_9 | overview-arts-circle.jpg（363.2 KB） |
| I-3 | art-therapy | `art-therapy-easel-mandala` | `doc/_static/bundles/yishu/liaoyu/art-therapy/images/` | `doc/bundles/yishu/liaoyu/art-therapy/index.md`：`## ⚠️ 免责声明` 块之后、`## 📚 快速导航` 之前。引导句：`下图以画架、画笔与曼陀罗，意象化呈现美术治疗以主动艺术创作为核心的工作方式。` | 暖灰纸感编辑插画：木画架上立着暖色块面的半成品抽象画布，旁置颜料罐与画笔，桌面纸上展开一幅圆形曼陀罗纹样，画室角落有柔和窗光 | 前缀 + `: a wooden easel holding a half-finished abstract canvas with warm color blocks, jars of paint and brushes beside it, a circular mandala pattern unfolding on a sheet of paper on the table, soft studio corner with warm window light, cream paper texture` + 后缀 | landscape_16_9 | art-therapy-easel-mandala.jpg（366.4 KB） |
| I-4 | music-therapy | `music-therapy-harp-listening` | `doc/_static/bundles/yishu/liaoyu/music-therapy/images/` | `doc/bundles/yishu/liaoyu/music-therapy/index.md`：免责声明 blockquote 之后、`## 📚 快速导航` 之前。引导句：`下图以竖琴与安静聆听的场景，意象化呈现音乐治疗以音乐为媒介的专业气质。` | 暖灰纸感编辑插画：窗边立着一架竖琴，椅上放着一副柔软耳机，暖色绸带般的抽象音形在午后柔光中流动，呈现安静聆听的氛围 | 前缀 + `: a harp leaning by a sunlit window, a pair of soft headphones resting on a chair, abstract flowing ribbon shapes suggesting music drifting in warm ochre and sage tones, gentle afternoon light, cream paper texture, calm listening atmosphere` + 后缀 | landscape_16_9 | music-therapy-harp-listening.jpg（482.2 KB） |
| I-5 | dance-drama-therapy | `dance-drama-movement-masks` | `doc/_static/bundles/yishu/liaoyu/dance-drama-therapy/images/` | `doc/bundles/yishu/liaoyu/dance-drama-therapy/index.md`：`## ⚠️ 免责声明` 块之后、`## 📚 快速导航` 之前。引导句：`下图以舒展舞姿与戏剧面具，意象化呈现舞动与戏剧治疗两大分支的身体与行动取向。` | 暖灰纸感编辑插画：一个舒展的抽象舞者扬起长绸带做开放拉伸姿态，旁置支架上的喜剧与悲剧双面具，暖赭与柔玫瑰色调，呈现自由表达感 | 前缀 + `: a graceful abstract dancer with flowing silk ribbons in a wide open stretching pose, paired with comedy and tragedy theater masks resting on a small stand nearby, warm terracotta and muted rose palette, soft paper texture, sense of free movement` + 后缀 | landscape_16_9 | dance-drama-movement-masks.jpg（461.3 KB） |
| I-6 | expressive-arts | `expressive-arts-intermodal-table` | `doc/_static/bundles/yishu/liaoyu/expressive-arts/images/` | `doc/bundles/yishu/liaoyu/expressive-arts/index.md`：`## ⚠️ 免责声明` 块之后、`## 📚 快速导航` 之前。引导句：`下图以一张多媒介工作台，意象化呈现表达性艺术治疗在模态间流动的跨模态工作方式。` | 暖灰纸感编辑插画：暖木工作桌上错落摆放颜料盘与画笔、铃鼓与小手鼓、带抽象墨迹的松散纸页、一双软舞鞋，呈现跨媒介创作工作台 | 前缀 + `: a warm wooden workshop table with mixed creative media arranged together — paint palette and brushes, a small tambourine and hand drum, loose cream pages with abstract ink marks (no readable writing), soft dance shoes — an intermodal creative workspace, muted warm tones, paper texture` + 后缀 | landscape_16_9 | expressive-arts-intermodal-table.jpg（457.0 KB） |
| I-7 | china-art-therapy | `china-guqin-inkwash` | `doc/_static/bundles/yishu/liaoyu/china-art-therapy/images/` | `doc/bundles/yishu/liaoyu/china-art-therapy/index.md`：免责声明 blockquote 之后、`## 📚 快速导航` 之前。引导句：`下图以古琴、水墨与宣纸，意象化呈现本束传统中医情志话语与乐教文献的文雅底色。` | 暖灰纸感水墨插画：案头一张古琴置于长幅宣纸之上，旁有墨碟，纸上淡墨山水留白，暖米与柔灰色调，传统文人书斋氛围 | 前缀 + ` with traditional Chinese ink-wash aesthetic: a Chinese guqin seven-string zither resting on a wooden scholar desk over long rice-paper sheets, an ink stone beside it with soft ink wash, a faint minimalist ink landscape with generous empty space on the paper, warm beige and soft grey palette, literati study mood` + 后缀 | landscape_16_9 | china-guqin-inkwash.jpg（392.6 KB） |

**配图备注**：

1. 七图均为器物/场景意象，**无人物临床场景、无医疗器械、无文字**；I-5 的舞者为抽象意象人物（非治疗场景），与束内免责声明口径一致，不含疗效暗示。
2. I-6 prompt 特别声明纸页为 "abstract ink marks (no readable writing)"，防止 AI 在纸页上生成乱码文字。
3. 组首页图 I-1 落组级目录 `liaoyu/images/`（spec Open Questions 默认项），六束封面各落本束 `images/` 目录；Task 2 需先建目录。

## 二、Mermaid 方案（10 张）

**分布**：liaoyu-overview 3 张（M1–M3，枢纽束含决策示例）、art-therapy 2 张（M4–M5）、music-therapy 2 张（M6–M7）、dance-drama-therapy 1 张（M8）、expressive-arts 1 张（M9）、china-art-therapy 1 张（M10）。每束 ≥1 张，总量 10（spec FR-4 候选清单原样落地，8–12 区间内）。

**总览表**：

| 编号 | 目标文件（子模块内绝对路径） | 插入章节锚点 | 图类型 | 事实来源 |
|---|---|---|---|---|
| M1 | `doc/bundles/yishu/liaoyu/liaoyu-overview/concepts/00-overview.md` | `## 六层定义对照表`（标题后、表格前） | flowchart TD（三层 subgraph + 伞式节点） | 本篇六层对照表正文；facts OV-02、OV-03、OV-05、OV-10；AT-13/AT-14；MT-01；DD-03；DD-09 |
| M2 | `doc/bundles/yishu/liaoyu/liaoyu-overview/concepts/01-history.md` | `## 六阶段时间线`（标题后、`### 前史` 前） | flowchart LR（六阶段节点链） | 本篇六阶段正文；facts OV-01、OV-07、OV-08；AT-11；MT-05；DD-03；EA-08 |
| M3 | `doc/bundles/yishu/liaoyu/liaoyu-overview/examples/01-branch-chooser.md` | 开篇导语段后、`## 问题一：你想解决什么？` 前 | flowchart TD（四问决策树） | 本篇四问正文与决策结果对照表；facts OV-05、OV-06、CN-09、CN-10 |
| M4 | `doc/bundles/yishu/liaoyu/art-therapy/concepts/01-founders.md` | 开篇导语段后、`## 一、Adrian Hill` 前 | flowchart LR（四人谱系链 → AATA） | 本篇四节正文；facts AT-01–AT-11、AT-13；OV-07（AATA 1969） |
| M5 | `doc/bundles/yishu/liaoyu/art-therapy/concepts/03-projective-techniques.md` | `## 一、定位：评估传统与治疗传统的分野` 小节末、`## 二、Goodenough` 前 | flowchart TD（双 subgraph 并行脉络） | 本篇正文；facts AT-17、AT-18、AT-10、AT-13/AT-14 |
| M6 | `doc/bundles/yishu/liaoyu/music-therapy/concepts/01-professionalization.md` | 开篇导语段后、`## 战争与医院音乐：职业的起点` 前 | flowchart LR（组织合并谱系 + Gaston 旁注） | 本篇正文；facts MT-02、MT-03、MT-04、MT-05、MT-06 |
| M7 | `doc/bundles/yishu/liaoyu/music-therapy/concepts/03-three-models.md` | 开篇导语段后、`## 分析性音乐治疗（AMT）：Mary Priestley` 前 | flowchart TD（三分支模型结构） | 本篇正文与三模型对照表；facts MT-01、MT-08、MT-09、MT-10、MT-11 |
| M8 | `doc/bundles/yishu/liaoyu/dance-drama-therapy/concepts/03-drama-therapy-models.md` | `## Renee Emunah 与整合五阶段模型` 小节内、五阶段列表与"顺序相位"佐证段后、"文献性简述"段前 | flowchart LR（五阶段顺序流程） | 本篇 Emunah 节正文；facts DD-09、DD-10 |
| M9 | `doc/bundles/yishu/liaoyu/expressive-arts/concepts/01-knill-intermodal.md` | `## 三、跨模态理论核心概念` 小节末（low skill 段后）、`## 四、著作书目` 前 | flowchart LR（跨模态转移循环 + 原则节点） | 本篇第三节正文；facts EA-02、EA-05 |
| M10 | `doc/bundles/yishu/liaoyu/china-art-therapy/concepts/02-qingzhi-xiangsheng.md` | `## 二、《素问·阴阳应象大论》情志相胜五句` 小节内、五句表与异文提醒段后、`## 三、张从正` 前 | flowchart LR（五志相胜环形循环） | 本篇相胜五句表；facts CN-01 |

### M1 术语六层分层图

- **引导句草案**：`下图把六层定义按外延从窄到宽排为三层——四个单模态临床职业、一个跨模态治疗模型与最宽的广义健康促进层，伞式术语 creative arts therapies 覆盖临床职业层。`

```mermaid
flowchart TD
  UMB ["伞式术语 creative arts therapies：NCCATA 五大专业协会联盟（facts OV-10）"]
  subgraph L1 ["临床职业层：单模态专业，硕士级训练加独立认证"]
    AT ["art therapy 美术治疗：AATA 定义为心理健康职业，资质 ATR 与 ATR-BC"]
    MT ["music therapy 音乐治疗：AMTA 定义为临床与循证地运用音乐干预，资质 MT-BC（CBMT 颁发）"]
    DMT ["dance/movement therapy 舞动治疗：ADTA 职业定义，资质 R-DMT"]
    DT ["drama therapy 戏剧治疗：NADTA 定义为意向性运用戏剧过程，资质 RDT"]
  end
  subgraph L2 ["跨模态治疗模型层"]
    EXA ["expressive arts therapy 表达性艺术治疗：IEATA 定义为以 intermodal 跨模态方式调动多种艺术模态、促成整合经验"]
  end
  subgraph L3 ["广义艺术健康促进层"]
    AIH ["arts in health 艺术与健康：WHO 2019 HEN Report 67，覆盖预防、健康促进与管理治疗全谱系"]
  end
  UMB -.-> L1
  L1 -->|"外延放宽：准入门槛逐层降低、证据强度逐层稀释"| L2
  L2 --> L3
```

- **事实来源**：`liaoyu-overview/concepts/00-overview.md` 六层定义对照表与"伞式术语与跨模态模型的分界"节；facts OV-05（IEATA/intermodal/伞式术语）、OV-10（NCCATA）、OV-02/OV-03（WHO HEN 67）；跨束事实 AT-13/AT-14（AATA、ATR/ATR-BC）、MT-01（AMTA 定义、MT-BC/CBMT）、DD-03（ADTA、R-DMT）、DD-09（NADTA、RDT）。

### M2 六阶段历史时间线

- **引导句草案**：`下图把六个阶段压成一条时间链——每格只登记该阶段最具标志意义的建制节点，完整史实见本节各小节与 facts 编号。`

```mermaid
flowchart LR
  S1 ["前史 1910s 至 1930s：1916 bibliotherapy 一词首用（Crothers）；1921 心理剧诞生（Moreno，维也纳）"]
  S2 ["战时医院 1940s：1942 Hill 首用 art therapy 一词；1942 Chace 进驻 St. Elizabeths 医院；1944 首个大学音乐治疗课程；1947 首位全职舞动治疗师"]
  S3 ["组织潮 1950s 至 1960s：1950 NAMT 成立；1961 首份美术治疗专门期刊（Ulman）；1966 ADTA 成立；1969 AATA 与诗歌治疗协会 APT 成立"]
  S4 ["模型分化 1970s：GIM、Nordoff-Robbins、分析性音乐治疗三大音乐治疗模型成形"]
  S5 ["建制补全与整合 1979 至 1990s：1979 戏剧治疗协会设立（NADTA 前身）；1983 音乐治疗认证委员会 CBMT；1993 美术治疗认证 ATCB；1994 IEATA 成立与 NCCATA 伞式联盟"]
  S6 ["循证时代 2000s 至 2019：Cochrane 系统综述陆续收录；2019 WHO HEN Report 67 发布（Fancourt 与 Finn，赫尔辛基）"]
  S1 --> S2 --> S3 --> S4 --> S5 --> S6
```

- **事实来源**：`liaoyu-overview/concepts/01-history.md` 六阶段时间线正文；facts OV-01（WHO 2019-11-11 赫尔辛基 HEN 67）、OV-07（NAMT 1950、ADTA 1966、AATA 1969、NADTA 前身 1979、CBMT 1983、ATCB 1993、IEATA 1994）、OV-08（Crothers 1916、Moreno 1921、Hill 1942、Chace 1942/1947、1944 课程）；AT-11（Ulman 1961 期刊）；MT-05（1944 密歇根州立学院）；DD-03（ADTA）；EA-08（APT 1969）。

### M3 四问分支选择决策树

- **引导句草案**：`下图把四个问题画成决策树——按序作答，每个出口直接指向一个目标束或一项资质核对动作；本图为阅读导航，不构成治疗建议。`

```mermaid
flowchart TD
  Q1 {"问题一：你想解决什么？"}
  Q1 -->|"确诊或在治的心理健康问题，想寻求治疗"| Q3 {"问题三：是否处于需要临床资质的场景？"}
  Q1 -->|"压力调适、兴趣培养、自我成长"| Q2 {"问题二：你偏好哪种表达形态？"}
  Q1 -->|"文化研究、写作、报道，想弄清概念与史实"| RD ["研究层：阅读路径与方法论，以 facts 层为引用底座"]
  Q2 -->|"绘画、雕塑等视觉艺术"| ATB ["art-therapy 束"]
  Q2 -->|"唱歌、演奏、聆听"| MTB ["music-therapy 束"]
  Q2 -->|"身体动作、舞蹈"| DDB ["dance-drama-therapy 束"]
  Q2 -->|"角色扮演、剧场"| DDB
  Q2 -->|"写作读诗，或不愿限定单一模态"| EXB ["expressive-arts 束"]
  Q3 -->|"是：患者、医疗机构、标准化治疗关系"| CERT ["核对资质缩写与发证机构：ATR-BC、MT-BC、R-DMT、RDT；否决速成班拿证即可治疗的宣称"]
  Q3 -->|"否：社区、文旅、自我使用场景"| AIHB ["arts in health 语域：引用时保留证据限定语"]
  Q4 {"问题四：中文语境有哪些专属判据？"}
  CERT -.->|"涉中文材料时"| Q4
  EXB -.->|"涉中文材料时"| Q4
  Q4 -->|"艺术治疗与艺术疗愈混用"| TERM ["按服务人群、执业场域、从业背书三判据核对"]
  Q4 -->|"五音疗疾式溯源叙事"| CN ["china-art-therapy 束：两套话语体系分层处理"]
```

- **事实来源**：`liaoyu-overview/examples/01-branch-chooser.md` 四问正文与"决策结果对照表"；facts OV-05（intermodal/expressive arts）、OV-06（艺术治疗/艺术疗愈三判据、三要素场景）、CN-09（中国建制阶段）、CN-10（速成班乱象与资质核对）。资质缩写 ATR-BC/MT-BC/R-DMT/RDT 亦见 00-overview 六层表与 03-professional-orgs。

### M4 美术治疗先驱谱系

- **引导句草案**：`下图按谱系角色串起四位奠基者与协会节点——四人工作在年代上互有交叠（如 Kramer 1958 年著作与 Ulman 1961 年期刊同期），图中顺序表示"术语—理论—平台—建制"的贡献链而非严格生卒先后。`

```mermaid
flowchart LR
  HILL ["Adrian Hill（1895 至 1977）：术语与出版物奠基，1942 首用 art therapy 一词，1945《Art Versus Illness》"]
  NAUM ["Margaret Naumburg（1890 至 1983）：动力取向艺术治疗，1947 自由艺术表达研究，1966《Dynamically Oriented Art Therapy》"]
  KRAM ["Edith Kramer（1916 至 2014）：艺术即治疗 art as therapy，1958《Art Therapy in a Children's Community》，1971《Art as Therapy with Children》"]
  ULMA ["Elinor Ulman（1910 至 1991）：期刊、定义与评估，1961 创办 Bulletin of Art Therapy，UPAP 标准化评估程序"]
  AATA ["1969 American Art Therapy Association（AATA）成立"]
  HILL -->|"术语进入公共语言"| NAUM
  NAUM -->|"动力取向传统"| KRAM
  KRAM -->|"艺术即治疗取向并行"| ULMA
  ULMA -->|"期刊平台推动领域自我讨论"| AATA
```

- **事实来源**：`art-therapy/concepts/01-founders.md` 四节正文；facts AT-01/AT-02（Hill 生卒、1942/1945 异说、1945 著作）、AT-03/AT-04/AT-05（Naumburg 生卒、动力取向、1947 与 1966 著作）、AT-06/AT-07/AT-08（Kramer 生卒、art as therapy、1958/1971 著作）、AT-09/AT-10/AT-11（Ulman、UPAP、1961 期刊）、AT-13（AATA）；AATA 1969 见 OV-07。注：AT-09 Ulman 生卒细节束内标注为单源待核，图中生卒年照束内登记值。

### M5 绘画投射技术与美术治疗并行脉络

- **引导句草案**：`下图把 1940 年代"图画—心理"学术氛围下的两股脉络并排呈现——投射技术三作属心理评估传统，美术治疗在医疗机构独立生长，二者共享前提但目标、操作者与伦理框架不同。`

```mermaid
flowchart TD
  BASE ["共享前提：图画可以承载心理信息；两股脉络在 1940 年代时间交叠"]
  subgraph EVAL ["心理评估传统：测量与评估，心理学家发展"]
    GOOD ["Goodenough 1926：画人测验 Draw-a-Man，《Measurement of Intelligence by Drawings》，目标为儿童智力测量"]
    BUCK ["Buck 1948/1949（年份异说并列）：房树人技术 H-T-P，目标为人格投射评估"]
    MACH ["Machover 1949：《Personality Projection in the Drawing of the Human Figure》，目标为画人人格投射"]
    GOOD --> BUCK --> MACH
  end
  subgraph THER ["美术治疗传统：治疗关系中促进改变，持 ATR 与 ATR-BC 资质"]
    HUNT ["Huntoon 1946 至 1959：Winter VA 医院艺术治疗工作"]
    ULMN ["Ulman 1955 至 1965：D.C. General Hospital 项目，UPAP 属最早一批标准化艺术治疗评估程序"]
  end
  BASE --> EVAL
  BASE --> THER
```

- **事实来源**：`art-therapy/concepts/03-projective-techniques.md` 正文（含"投射技术不是美术治疗的前身，而是同期背景"澄清）；facts AT-17（Goodenough 1926、Buck 1948/1949 异说、Machover 1949）、AT-18（Huntoon 1946–1959 Winter VA）、AT-10（Ulman 1955–1965、UPAP）、AT-13/AT-14（美术治疗职业与资质）。

### M6 美国音乐治疗组织合并谱系

- **引导句草案**：`下图画出"战地需求到职业统一"的主干——NAMT 与 AAMT 双组织并存二十六年后于 1998 年合并为 AMTA；Gaston 作为同期理论奠基者旁注于侧。`

```mermaid
flowchart LR
  WAR ["二战后退伍军人医院：社区音乐家为伤兵演奏，医护提出雇用音乐家请求"]
  COURSE ["1944 密歇根州立学院：首个大学音乐治疗课程（双源确认）"]
  NAMT ["NAMT：1950-06-02 成立，统一大学水平教育标准，RMT 注册制度（1956），董事会认证项目（1985）"]
  AAMT ["AAMT：1971 成立，双组织并存开始；1980 出版期刊 Music Therapy"]
  AMTA ["AMTA：1998 NAMT 与 AAMT 合并，美国音乐治疗职业自 1971 年以来首次统一"]
  GAST ["E. Thayer Gaston（1901 至 1970）：音乐治疗之父，1968《Music in Therapy》三项价值"]
  WAR --> COURSE --> NAMT
  NAMT -->|"1971 第二组织分立"| AAMT
  NAMT -->|"1998 合并"| AMTA
  AAMT -->|"1998 合并"| AMTA
  GAST -.->|"同期理论奠基"| NAMT
```

- **事实来源**：`music-therapy/concepts/01-professionalization.md` 正文与年份速查表；facts MT-05（医院演奏、1944 课程双源）、MT-02（NAMT 1950-06-02、RMT 1956 单源待核、1985 认证）、MT-03（AAMT 1971、1980 期刊）、MT-04（AMTA 1998 合并）、MT-06（Gaston 生卒、"音乐治疗之父"、1968 著作）。注：RMT 1956 协作细节束内标注单源待核。

### M7 音乐治疗三大模型结构

- **引导句草案**：`下图把三个最具影响力的模型并置——差异不在"是否属于音乐治疗"（三者均满足 AMTA 定义三要件），而在对"音乐如何起作用"的三种回答：关系内分析、聆听诱发意象、即兴共同创造。`

```mermaid
flowchart TD
  ROOT ["1970 年代前后三大模型成形：均满足 AMTA 定义三要件，即持证专业人员、治疗关系、个体化目标"]
  AMTM ["分析性音乐治疗 AMT：Mary Priestley（1925 至 2017），1970 年代初于英国发展，综合 Freud、Jung、Klein 精神分析，核心为治疗关系内的即兴与分析，《Music Therapy in Action》1975"]
  GIM ["引导想象与音乐 GIM：Helen Bonny（1921 至 2010），起源于马里兰精神病学研究中心，致幻剂研究的去药物化转化，核心为音乐聆听诱发意象，《Music and Your Mind》1973，AMI 1986"]
  CMT ["创造性音乐治疗：Paul Nordoff（1909 至 1977）与 Clive Robbins（1927 至 2011），1958 Sunfield 相识、1959 开始合作，核心为即兴音乐的共同创造，《Creative Music Therapy》1977"]
  ROOT --> AMTM
  ROOT --> GIM
  ROOT --> CMT
```

- **事实来源**：`music-therapy/concepts/03-three-models.md` 正文与三模型对照表；facts MT-08（Priestley 生卒 1925-03-04/2017-06-11、1975 著作；AMT 发展时点束内标注单源待核）、MT-09（Bonny 生卒 1921/2010、MPRC 起源、1973 著作、AMI 1986）、MT-10（Nordoff 1909/1977-01-18、Robbins 1927/2011、1958/1959 Sunfield）、MT-11（《Creative Music Therapy》1977）、MT-01（AMTA 三要件）。

### M8 Emunah 整合五阶段流程

- **引导句草案**：`下图把 Emunah 整合五阶段模型画成顺序流程——从低结构的自发扮演推进到高结构的仪式化呈现；五阶段是 Emunah 提出的一个整合模型（facts DD-10），不是 NADTA 官方流程。`

```mermaid
flowchart LR
  ORG ["NADTA 1979 设立：注册戏剧治疗师 RDT 资格与职业标准"]
  BOOK ["Emunah《Acting for Real》：1994 初版（2020 第二版），整合五阶段模型"]
  P1 ["一、戏剧性游戏 Dramatic Play：自发、游戏性的扮演进入"]
  P2 ["二、场景工作 Scenework：即兴场景的搭建与展开"]
  P3 ["三、角色扮演 Role Play：特定角色的代入与探索"]
  P4 ["四、高潮呈现 Culminating Enactment：以完整演出整合前期材料"]
  P5 ["五、戏剧仪式 Dramatic Ritual：仪式化收束，赋予结构与意义"]
  ORG -->|"职业化背景"| BOOK
  BOOK -->|"顺序相位：低结构自发推向高结构仪式化"| P1
  P1 --> P2 --> P3 --> P4 --> P5
```

- **事实来源**：`dance-drama-therapy/concepts/03-drama-therapy-models.md` Emunah 节正文（五阶段名、《Acting for Real》版本、低结构到高结构的文献性概述）；facts DD-09（NADTA 1979、RDT）、DD-10（Emunah、CIIS、五阶段、1994/2020 著作、Taylor & Francis 顺序相位佐证）。

### M9 跨模态转移循环

- **引导句草案**：`下图把跨模态离心化画成一个循环——借助从一个艺术模态向另一个模态的转移离开对问题的固着焦点，再经感官与美学回应达致整合经验；low skill / high sensitivity 原则贯穿全程。`

```mermaid
flowchart LR
  LS ["贯穿原则：low skill / high sensitivity，低技能门槛、高感官敏感度（facts EA-02）"]
  A ["模态一的创作：视觉艺术、音乐、舞动、戏剧、诗歌写作任一"]
  B ["跨模态离心化转移 intermodal decentering：借助模态转换离开对问题的固着焦点"]
  C ["模态二的回应：在新模态中形成感官回响与美学回应"]
  D ["整合经验：模态交织促成整合（IEATA 定义，facts EA-05）"]
  A -->|"创作表达"| B
  B -->|"感官回响"| C
  C -->|"美学回应"| D
  D -->|"再转移、循环深化"| A
  LS -.-> A
  LS -.-> B
  LS -.-> C
```

- **事实来源**：`expressive-arts/concepts/01-knill-intermodal.md` 第三节正文（intermodality、跨模态离心化定义、low skill/high sensitivity）；facts EA-02（IDEC、low skill/high sensitivity 为 EGS 课程核心概念）、EA-05（IEATA 定义：intermodal 调动视觉艺术、音乐、舞动、戏剧、诗歌/写作多模态、促成整合经验）。图中"美学回应"措辞呼应 EA-02 所录 aesthetic responsibility（审美责任）主题词，未作疗效演绎。

### M10 五志相胜循环

- **引导句草案**：`下图依《素问·阴阳应象大论》情志相胜五句（facts CN-01）画出五志克制环——怒胜思、思胜恐、恐胜喜、喜胜忧、悲胜怒，与五行相克序（木克土、土克水、水克火、火克金、金克木）一一对应；末边标签"悲胜怒"为东方段原文，西方段情志名通行本作"忧"、黄元御《素问悬解》作"悲"，两读并列（CN-01 异文四）。本图属中医情志学说文献梳理，不构成现代临床建议。`

```mermaid
flowchart LR
  NU ["怒：肝、角、东方、木；怒伤肝"]
  SI ["思：脾、宫、中央、土；思伤脾"]
  KONG ["恐：肾、羽、北方、水；恐伤肾"]
  XI ["喜：心、徵、南方、火；喜伤心"]
  YOU ["忧（异文：悲）：肺、商、西方、金；忧伤肺"]
  NU -->|"怒胜思（木克土）"| SI
  SI -->|"思胜恐（土克水）"| KONG
  KONG -->|"恐胜喜（水克火）"| XI
  XI -->|"喜胜忧（火克金）"| YOU
  YOU -->|"悲胜怒（金克木）"| NU
```

- **事实来源**：`china-art-therapy/concepts/02-qingzhi-xiangsheng.md` 情志相胜五句表与异文提醒；facts CN-01（五段"在音为某/在志为某/某伤某、某胜某"逐字核对：角-肝-怒、徵-心-喜、宫-脾-思、商-肺-忧、羽-肾-恐；西方段"忧/悲"义理级异文两读并列）。环序严格依五行相克：木（怒）克土（思）、土克水（恐）、水克火（喜）、火克金（忧/悲）、金克木（怒）。

## 三、G1 事实门核对汇总

| 图 | 关键事实锚点（图中出现的人名/年份/组织/模型/阶段名） | 溯源位置 |
|---|---|---|
| M1 | AATA/AMTA/ADTA/NADTA/IEATA 五组织、ATR-BC/MT-BC/R-DMT/RDT 四资质、NCCATA、WHO 2019 HEN 67、intermodal | 00-overview 六层表；OV-02/03/05/10；AT-13/14；MT-01；DD-03/09 |
| M2 | 1916 Crothers、1921 Moreno、1942 Hill/Chace、1944 课程、1947 全职舞动治疗师、1950 NAMT、1961 Ulman 期刊、1966 ADTA、1969 AATA/APT、1979 戏剧治疗协会、1983 CBMT、1993 ATCB、1994 IEATA、2019 WHO HEN 67 | 01-history 六阶段正文；OV-01/07/08；AT-11；MT-05；DD-03；EA-08 |
| M3 | 四问分流、六束出口、四资质缩写、艺术治疗/艺术疗愈三判据、速成班否决、五音疗疾陷阱 | 01-branch-chooser 全文；OV-05/06；CN-09/10 |
| M4 | Hill 1895-1977/1942/1945、Naumburg 1890-1983/1947/1966、Kramer 1916-2014/1958/1971、Ulman 1910-1991/1961/UPAP、AATA 1969 | 01-founders 四节；AT-01–AT-11、AT-13；OV-07 |
| M5 | Goodenough 1926、Buck 1948/1949 异说、Machover 1949、Huntoon 1946–1959、Ulman 1955–1965/UPAP | 03-projective-techniques 正文；AT-17/18/10/13/14 |
| M6 | 1944 密歇根州立、NAMT 1950-06-02/RMT 1956/1985、AAMT 1971/1980 期刊、AMTA 1998 合并、Gaston 1901-1970/1968 | 01-professionalization 正文与速查表；MT-02/03/04/05/06 |
| M7 | Priestley 1925-2017/1975、Bonny 1921-2010/MPRC/1973/AMI 1986、Nordoff 1909-1977 与 Robbins 1927-2011/1958/1959/1977、AMTA 三要件 | 03-three-models 正文与对照表；MT-01/08/09/10/11 |
| M8 | NADTA 1979/RDT、Emunah/CIIS、《Acting for Real》1994/2020、五阶段英文名、低结构到高结构 | 03-drama-therapy-models Emunah 节；DD-09/10 |
| M9 | intermodal decentering（IDEC）、low skill/high sensitivity、五模态清单、IEATA 整合经验定义 | 01-knill-intermodal 第三节；EA-02/05 |
| M10 | 五志-五脏-五音-方位-五行对应、相胜五句、忧/悲异文 | 02-qingzhi-xiangsheng 五句表；CN-01 |

**讹传规避记录**（R 阶段已按束内修正值制图，未采用网络通说）：Knill 生卒用 1932–2020（EA-01，非 1934–2023）；Whitehouse 卒年 1979（DD-04，M2 未直接出现卒年）；中国音乐治疗锚点 1988 中国音乐学院（M3 仅引 CN-09/10 资质判据，未涉年份）；Buck HTP 年份 1948/1949 异说并列（M5 原样标注）；Ulman 生卒 AT-09 单源待核（M4 照束内登记值并在来源列披露）。

## 四、门禁合规自检（check-mermaid.py 实跑结论）

| 规则（主仓库门禁） | 自检结论 |
|---|---|
| ① 代码块内禁空行 | 10 个块均为连续行，无空行 |
| ② 非纯英文标签双引号包裹 | 全部节点/菱形/边标签均用 `["..."]`、`{"..."}`、`-->|"..."|`；含中文的标签 100% 被引号包裹 |
| ③ 禁 Markdown 列表触发（"1. "、"- " 开头） | 无标签以数字加点或减号加空格开头；M8 阶段序用中文"一、二、三……"（"一"非 ASCII 数字，不触发 `^\d+[.、]` 规则） |
| ④ 标签单行，禁 `<br/>` 与字面 `\n` | 10 块全部单行标签，多行信息以"：""；""，"分隔；无 `<br/>`、无 `\n` |
| ⑤ subgraph 用 `subgraph EN_ID ["标题"]` | M1（L1/L2/L3）、M5（EVAL/THER）均合规，ID 为英文标识符，标题方括号包裹 |
| ⑥ 带标签边用 `-->|"标签"|` | M1/M3/M4/M6/M8/M9/M10 的标签边全部使用该格式；虚线无标签边用 `-.->`，虚线带标签边用 `-.->|"..."|`（M3） |
| ⑦ VS Code 兼容子集 | 无带圈数字（①-⑩）、无中文方括号【】、无 Unicode 箭头（→←↑↓等）、subgraph 内无嵌套 direction |
| ⑧ 安全检查 | 无 click 事件绑定、无危险 HTML 标签、无 on* 事件属性、无 javascript: URL、无以 end 为节点 ID |

**其他静态检查**：标签内未出现 ASCII 双引号嵌套（书名用《》、补充说明用全角（））；未使用 `&`、裸 `<`、`>` 等 mermaid 敏感字符（年份范围用"至"字）；边目标为 subgraph ID（M1/M5）属 mermaid 合法语法；Kramer 书名中 ASCII 撇号（Children's）位于双引号标签内，解析安全。

**验证命令**：`python .agents/scripts/check-mermaid.py --path .trae/specs/liaoyu-visual-assets`（主仓库根目录执行），结果为 0 错误 0 警告。

## 五、风险与备注（交主代理审核）

1. **枢纽束 3 张 Mermaid**：M1–M3 均在 liaoyu-overview（其中 M3 在 examples/）。NFR-4 称"每束 1–2 张"，但 FR-4 候选清单明列这 3 个图位且分属 concepts×2 + examples×1 三个不同文件；总量 10 在 8–12 区间。若审核认为需压缩，建议优先保留 M1、M2，M3 可降为备选。
2. **M4 顺序非严格编年**：Kramer（1958/1971 著作）与 Ulman（1961 期刊）年代交叠，图按"术语—理论—平台—建制"谱系角色排列，引导句已显式声明，避免读者误读为严格时间线。
3. **M9 循环结构**：跨模态转移的"循环"是方法论示意（离心化→回应→整合→再转移），节点措辞严格取自 EA-02/EA-05 已登记表述，未添加束外的阶段名或疗效断言。
4. **M10 末边标签**：节点 YOU 作"忧（异文：悲）"，边标签依东方段原文作"悲胜怒"，引导句已说明两读并列口径；Task 3 插入时引导句须随图一并插入，不得只插图。
5. **配图路径**：组首页图 I-1 落组级目录 `_static/bundles/yishu/liaoyu/images/`（spec Open Questions 默认项）；Task 2 生成前需先建 7 个 images 目录。
6. **单源待核条目**：M6（RMT 1956）、M7（AMT 1970 年代初发展时点）、M4（Ulman 生卒 AT-09）涉及束内标注单源待核的细节，图中照束内登记值呈现，来源列已披露；V 阶段事实抽查时重点复核这三处。
7. **本方案不触碰**：frontmatter、facts.md、references/、免责声明、toctree、共享索引（bundles/index.md 等）均不在 Task 3 变更集内。
8. **单行标签口径**：本方案文件位于主仓库 `.trae/` 侧，受主仓库 Mermaid 门禁约束（禁 `<br/>`），故 10 图均为单行标签；Task 3 插入子模块束文件时**按本版单行文本原样插入**，不得在行内回填 `<br/>`（单行版在 Sphinx/MyST 与 VS Code 均正常渲染，且子模块侧未来若加严门禁也无需返工）。
