---
status: "draft"
name: create-art-therapy-okf-wiki
version: 1.0.0
created: 2026-09-01
source: "国内外艺术疗愈公开学术与临床知识：创始人经典著作结论性引用（Hill/Naumburg/Kramer/Alvin/Bonny/Nordoff-Robbins/Chace/Whitehouse/Moreno/Knill/McNiff 等）、职业组织公开定义（AATA/AMTA/ADTA/NADTA/IEATA）、循证报告（WHO 2019 scoping review、Cochrane 系统综述）、公共领域中医古籍原文（《黄帝内经》五音疗疾与情志学说）、公开网络学术资源，经双信源核对后整理"
methodology: seven-concepts 场景4（知识沉淀）R→I→E→V→C
content-sensitivity: Public（艺术疗愈历史/理论/循证证据均为公开知识；现代受版权保护著作仅作结论性引用与信源登记，不复制受保护内容；中医古籍属公共领域）
---

# 艺术疗愈 OKF 知识包教程 Spec

## Why

用户希望全面调研国内外艺术疗愈（包含美术、音乐等）相关的原文和解读，以 OKF 知识包形式沉淀到 `projects/awesome-okf-xs/doc/bundles` 的恰当位置，生成内容详实、真实可靠的 wiki 教程。艺术疗愈领域存在三大可信度风险：①网络资料普遍将"艺术治疗"（艺术心理治疗）与"艺术疗愈"（广义健康促进）混为一谈，人物/年代/流派归属错讹频发；②创始人经典著作（Hill 1945、Naumburg 1966、Kramer 1971、Bonny 1973 等）均受版权保护，网络转述常有"名言"实为构拟；③中国语境下中医五音疗疾与西方音乐治疗常被混述。"真实可靠"必须通过**双信源逐条核对历史事实** + **原文引用分层（公共领域全文引用 / 受版权保护著作仅结论性引用并登记）** + **循证证据锚定（WHO/Cochrane）**来保证，而非沿用单一网络流行说法。

## What Changes

- 新增分组 `bundles/yishu/liaoyu/`（艺术疗愈分组，yishu 艺术域第 2 组，与 vocal 平级），含 **6 个知识包**：
  - `liaoyu-overview/`——艺术疗愈总览：定义辨析（艺术治疗 vs 艺术疗愈 vs 表达性艺术治疗）、历史脉络（1940s 战时医院起源→1950-60s 职业化→1990s 循证时代）、分支谱系（美术/音乐/舞动/戏剧/诗歌/表达性艺术六大分支）、流派谱系（精神分析/人本/超个人/神经科学）、循证证据概貌（WHO 2019、Cochrane）、职业体系（AATA/AMTA/ADTA/NADTA/IEATA）、阅读路径；承载 facts.md（跨束汇总）+ insights.md（洞察与模式沉淀）
  - `art-therapy/`——美术治疗（绘画治疗）：Adrian Hill（1942 年提出 art therapy 术语）与战时结核病院实践、Margaret Naumburg 动力取向艺术治疗、Edith Kramer 艺术即治疗与升华说、荣格主动想象与曼陀罗、绘画投射技术脉络、当代神经科学视角
  - `music-therapy/`——音乐治疗：20 世纪早期音乐医学文献、Juliette Alvin 与英国传统、Mary Priestley 分析性音乐治疗、Helen Bonny 引导想象与音乐（GIM）、Nordoff-Robbins 创造性音乐治疗、音乐治疗 vs 音乐医学之辨、Cochrane 循证结论
  - `dance-drama-therapy/`——舞动与戏剧治疗：Marian Chace 与圣伊丽莎白医院、ADTA 定义与真实动作（Mary Whitehouse）、Moreno 心理剧、戏剧治疗五阶段（Renee Emunah）、NADTA 职业体系
  - `expressive-arts/`——表达性艺术治疗：Paolo Knill 跨模态理论、Shaun McNiff 艺术即治疗传统、Levine 夫妇诗意/存在取向、诗歌治疗（NAPT）、整合取向与低技能高敏感度原则
  - `china-art-therapy/`——中国艺术疗愈：中医情志学说与五音疗疾（《黄帝内经》公共领域原文全文引用，交叉引用 `yixue/tcm` 与 `yixue/daoyi` 既有束）、近现代音乐治疗引入（1980s 起高校专业建设）、本土化发展与实践、中西对读
- 每个束遵循三层结构：`concepts/`（4-6 篇核心概念）、`examples/`（1-2 篇实操）、`references/`（1-2 篇信源登记）+ 根 `index.md`（toctree 导航）+ `facts.md`（本束事实登记）+ `log.md`；总览束额外承载 `insights.md`（跨束洞察与可复用模式）
- 更新导航索引：`bundles/index.md`（`total_bundles` 378→384、`groups` 43→44、yishu 域行 1 束→7 束·2 组、生态 mermaid 图 yishu 节点描述更新、toctree 追加 `yishu/liaoyu/index`）、`yishu/index.md`（域描述更新、分组导航表新增 liaoyu 行、toctree 追加）、新增 `yishu/liaoyu/index.md`（组 index）
- 遵循 seven-concepts 场景4 链路：R（信源采集与事实登记，G1）→ I（洞察，G2）→ E（生成 6 束 + 萃取 ≥2 个可复用模式，G3）→ V（对抗审查：事实抽查 + 原文核对 + 合规审查）→ C（质量门 `invoke gates.all` + 按束原子提交）

**关键决策（落位）**：艺术疗愈是 yishu 艺术域的分支领域（与声乐并列的独立分组），不新开域——art therapy/music therapy 等本质是"艺术手段×疗愈应用"的交叉学科，归 yishu 域最符合学科直觉；中医情志与五音部分通过交叉引用 `yixue/` 既有束衔接而非复制内容（单一可信源原则）。故落位 `yishu/liaoyu/`，domains 计数不变（9），groups 43→44，total_bundles 378→384。

**关键决策（原文分层）**：
- **公共领域**：中医古籍（《黄帝内经》五音疗疾、情志相胜等）全文引用，双源核对（ctext.org、维基文库，辅以既有 `yixue/tcm` 束的核对记录）
- **受版权保护著作**（Hill、Naumburg、Kramer、Alvin、Bonny、McNiff 等 20 世纪著作）：仅经典定义/核心观点**简要结论性引用**（1-2 句以内）+ 完整书目与信源登记，**不整段转录**
- **组织公开定义**：AATA/AMTA/ADTA/NADTA/IEATA 官网职业定义引用并标注 URL
- **循证证据**：WHO 2019 scoping review（Fancourt & Finn）、Cochrane 系统综述作结论性转述并登记 DOI/URL，不虚构效应量数字

**关键决策（可靠性策略）**：历史事实（人物、年份、术语首创、组织成立、专业设立）一律 ≥2 独立信源交叉核对（职业组织官网、学术综述/期刊文献、WHO/Cochrane 报告为主信源；维基百科仅作交叉参考线索不作唯一信源）；无法调和的异说在 facts.md 并列登记不裁决；每个事实带编号与信源 URL 可追溯。

## Impact

- Affected specs: `create-tcm-classics-okf-wiki`（中医经典束，交叉引用衔接不修改其产物）、`create-buddhism-okf-wiki` 等人文类 spec 仅作格式模式参照；`okf-spec`（meta）为格式依据，只读
- Affected code: `projects/awesome-okf-xs`（git submodule，第一方子项目，允许子模块内开发）内 `doc/bundles/` 新增 `yishu/liaoyu/` 组全部文件，以及 `bundles/index.md`、`yishu/index.md` 两个共享索引的更新；提交发生在子模块仓库内（每束一原子提交 + 索引一提交），**遵守并行会话共享索引竞态防护**（add 与 commit 分离、暂存 blob 核验）；主仓 gitlink 变更随推送闸门统一处理（当前用户令暂不推送，仅本地提交）
- 不修改任何既有 bundle 内容（含 `yixue/tcm`、`yixue/daoyi`）；不修改 SpecWeave 主仓其他文件

## ADDED Requirements

### Requirement: 历史与理论事实的双信源核对

知识包 SHALL 覆盖六大分支的历史与理论主干（人物、年代、术语首创、经典著作、职业组织、循证证据），每个关键事实 SHALL 经至少两个独立权威信源交叉核对（职业组织官网、学术文献/综述、WHO/Cochrane 报告为主信源），在 facts.md 登记编号事实与信源 URL；存在学术异说时并列呈现各自依据，不作武断裁决。全部束 facts.md 合计 SHALL ≥60 条编号事实。

#### Scenario: 事实抽查

- **WHEN** 对抗审查随机抽取 10 条 facts.md 事实核对登记信源
- **THEN** 全部与登记信源一致，无虚构引证、无单一网络来源孤证

#### Scenario: 异说并列

- **WHEN** 读者阅读任一存在学术争议的条目（如术语首创年代、"艺术治疗/艺术疗愈"译名边界）
- **THEN** 至少呈现 2 种说法及各自信源，无武断结论

### Requirement: 原文引用分层与版权合规

"原文"引用 SHALL 分层处理：①公共领域中医古籍原文（五音疗疾、情志相胜等）双源逐字核对后可全文引用，并交叉链接 `yixue/` 既有束；②现代受版权保护著作（Hill《Art Versus Illness》、Naumburg、Kramer、Alvin、Bonny、Nordoff-Robbins、McNiff、Knill 等）仅作经典定义/核心观点的简要结论性引用（1-2 句）+ 完整书目登记，不整段转录；③职业组织公开定义（AATA/AMTA/ADTA/NADTA/IEATA）引用原文并标注 URL。每处引用标注出处可溯源。

#### Scenario: 版权边界

- **WHEN** 读者核查任一现代著作引用
- **THEN** 引用为简要结论性引用且附完整书目，无整段转录受保护内容

#### Scenario: 古籍原文核对

- **WHEN** 读者对照权威信源核查中医古籍引文
- **THEN** 逐字一致（异文处显式标注），且能经链接跳转到 yixue 既有束对读

### Requirement: 循证证据锚定

知识包 SHALL 以 WHO 2019 scoping review（Fancourt & Finn,《What is the evidence on the role of the arts in improving health and well-being?》）与相关 Cochrane 系统综述为循证主锚点，转述其结论范围与局限；SHALL 诚实呈现证据质量分级（如"证据总体有限/中等"），不夸大疗效、不虚构效应量。

#### Scenario: 证据诚实呈现

- **WHEN** 读者阅读任一分支的循证章节
- **THEN** 结论均可追溯至登记的综述报告，证据局限有明示，无"包治"式夸大表述

### Requirement: 免责声明与临床边界

每个束的根 index.md SHALL 在显著位置声明：本教程为艺术疗愈文献学习资料，**非医疗或心理治疗建议**，严重身心困扰请咨询执业医师/心理治疗师/注册艺术治疗师；并标注"艺术治疗（art/psychotherapy 系）与广义艺术疗愈（arts in health）"的边界提示。

#### Scenario: 免责声明可见

- **WHEN** 读者打开任一束首页
- **THEN** 可见免责声明与边界提示

### Requirement: 中国脉络的诚实呈现

`china-art-therapy` 束 SHALL 分层呈现：①中医情志学说与五音疗疾的古籍原文与历代注家解读（公共领域，双源核对）；②近现代西方艺术治疗引入中国的脉络（高校专业建设、职业发展，关键事实双信源核对）；③中西对读的异同辨析（理论根基、实践形态、职业体系差异），不将中医五音与现代音乐治疗混为一谈，同时标注"传统表述与现代证据属于不同话语体系"。

#### Scenario: 中西不混述

- **WHEN** 读者阅读五音疗疾相关章节
- **THEN** 传统语境（中医情志理论）与现代语境（循证音乐治疗）分节呈现、互不冒充，交叉链接可跳转

### Requirement: OKF 格式与导航完整性

所有新增文档 SHALL 遵循 awesome-okf-xs 规范：OKF v0.2 YAML frontmatter（`type` 必填、`sources` 溯源、`generated`/`status`/`stale_after`，规范见 `projects/awesome-okf-xs/.agents/rules/frontmatter.md`；**YAML 双引号标量内禁用 ASCII 双引号**，中文语境一律用全角“”）、束根 index 以 `{toctree}` 引用全部内容文档、Markdown 相对路径交叉引用无断链、束自包含、正文中文/文件名 kebab-case 纯英文，并通过 `invoke gates.all`（UTF-8 + toctree + bundles 计数对账）。索引统计同步更新（bundles 378→384、groups 43→44）。

#### Scenario: 质量门通过

- **WHEN** 在 `projects/awesome-okf-xs` 运行 `invoke gates.all`
- **THEN** utf8、toctrees、bundles 三门全部通过，无孤立文档、无断链，总索引统计与实际文件数一致

### Requirement: 方法论闭环（G1–G3 + V）

教程 SHALL 记录 seven-concepts 场景4 方法论痕迹：各束 facts.md 编号事实无因果推断词且全带信源 URL（G1）、总览束 insights.md ≥3 条带四元组洞察（陈述/证据引用事实编号/反常识/行动）（G2）、≥2 个可复用模式（如"双信源历史事实核对法""艺术疗愈流派谱系判读框架""原文引用分层合规法"）含触发场景/核心步骤/反模式/迁移示例（G3），并在提交前经对抗审查（V）完成事实抽查、原文核对与合规审查。每束 log.md 记录 R-I-E-V-C 各阶段执行摘要。

#### Scenario: 方法论痕迹可查

- **WHEN** 读者打开总览束 insights.md 与任一束 log.md
- **THEN** 可见满足 G2/G3 标准的洞察与模式，以及各阶段执行记录

## MODIFIED Requirements

无（本任务为全新增量；`bundles/index.md` 与 `yishu/index.md` 仅追加计数/导航行，属索引维护而非既有需求变更）。

## REMOVED Requirements

无。

## 开放问题

- 无（落位与范围按七概念场景4 标准链路确定：yishu/liaoyu/ 组 + 总览与五分支共 6 束；若实现阶段发现双信源核对存在无法调和的事实冲突，在 facts.md 并列登记，不作裁决）
- 后续扩展（诗歌治疗独立成束、团体艺术治疗、儿童艺术疗愈专题、神经科学艺术疗愈专题）不在本 spec 范围内，仅在总览束阅读路径中占位
