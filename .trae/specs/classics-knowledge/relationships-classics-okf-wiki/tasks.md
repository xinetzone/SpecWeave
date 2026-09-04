# 两性关系经典著作 OKF Wiki 教程 — 实施计划

> 方法论链路：seven-concepts 场景 4（知识沉淀）R→I→E，叠加 V 对抗审查。
> 根目录：`d:\AI\projects\awesome-okf-xs`；产出根：`doc/bundles/think/relationships/`。
> 委派策略：Task 2–7 为相互独立的垂直切片，可并行委派 subagent（每束一个 R→I→E 闭环）；主控逐束独立验收后整合。

## Task 1: 分组骨架与目录初始化
- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 新建 `doc/bundles/think/relationships/` 分组目录
  - 编写 `relationships/index.md` 骨架：frontmatter（`type: group`、title/description/tags）、分组导言占位（三层定位说明：学术实证/哲学经典/通俗实用）、6 束导航表占位、`{toctree}` 含 6 个 bundle 的 index
  - 为 6 个 bundle 创建目录：`intimate-relationships/`、`art-of-loving/`、`gottman-seven-principles/`、`five-love-languages/`、`attached/`、`mars-venus/`，各含 `concepts/`、`examples/`、`references/` 子目录
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-1.1: 7 个目录（分组 + 6 束 × 3 子目录）与 relationships/index.md 存在；证据：目录列表
  - `rule` TR-1.2: relationships/index.md 含合法 frontmatter（type: group）与 toctree（6 条 index 引用）；证据：文件内容核对
- **Notes**: 此任务不依赖网络调研，先行落地以固化结构。

## Task 2: 《亲密关系》（Rowland Miller）知识包 — intimate-relationships
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - R：调研公开权威信源（Wikipedia: Intimate Relationships (Miller)、出版社页面、豆瓣读书正版条目、WorldCat），核验作者全名、原版首版年（1993 前后，以核验为准）、最新版次、主流中译本（人民邮电出版社等，以核验为准）、教材结构（吸引力/社会认知/沟通/相互依赖/友谊/爱情/冲突/关系维持与解体等模块）；登记 facts.md（30–50 条，每条带信源脚注）
  - I：提炼概念框架与 3–5 条四元组洞察（如"亲密关系的科学实证转向""相互依赖理论视角"）
  - E：生成 concepts/ 5–6 篇（著作背景与定位、亲密关系科学研究方法、吸引力与社会认知、沟通与冲突、相互依赖与关系维持、爱情与关系发展阶段）、examples/ 2 篇（关系自评与反思清单（原创编排）、阅读与实践路径）、references/ 2 篇（版本与信源、延伸研究）、index.md（含 sources、okf_version、toctree）、log.md、insights.md
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-5, AC-6, AC-8, AC-9
- **Test Requirements**:
  - `rule` TR-2.1: facts.md ≥30 条，每条带信源标识且无因果推断词（G1）；P0 事实（作者/原版年/出版社）双信源；证据：facts.md + 信源 URL
  - `rule` TR-2.2: concepts 5–6 篇、examples 2 篇、references 2 篇，全部含 frontmatter（type/title/sources）；index.md toctree 覆盖全部文档；证据：文件计数与内容核对
  - `rule` TR-2.3: 无 >30 字未标注直引，无盗版链接；证据：引用清单
  - `rubric` TR-2.4: 解读深度；scale 1-5；anchors 1=目录罗列/3=复述层面/5=有结构有洞见；threshold >=4；证据：主控抽样阅读

## Task 3: 《爱的艺术》（Erich Fromm）知识包 — art-of-loving
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - R：核验 Fromm 生平与著作背景（1956 年出版、人本主义精神分析/法兰克福学派脉络）、全书结构（爱是一种能力/理论：爱不是感觉而是艺术；父母之爱与博爱/自爱/神爱；当代西方社会的爱之瓦解；爱的实践：纪律/专注/耐心/关注）、中译本信息（上海译文/人民文学等，以核验为准）
  - I：洞察（如"爱作为能力而非对象命中注定""资本主义人格市场对爱的侵蚀"）
  - E：concepts/ 5–6 篇（弗洛姆其人与其时代、核心命题：爱是艺术、爱的理论诸形态、爱之瓦解的社会诊断、爱的实践四要素）、examples/ 2 篇（爱的实践日常练习（原创编排）、阅读路径）、references/ 2 篇、index.md、log.md、insights.md、facts.md
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-5, AC-6, AC-8, AC-9
- **Test Requirements**:
  - `rule` TR-3.1: facts.md ≥30 条且可溯源；证据：facts.md + 信源
  - `rule` TR-3.2: 文档数量与 frontmatter 合规；证据：文件核对
  - `rule` TR-3.3: 引用合规（短句标注、无整段复制）；证据：引用清单
  - `rubric` TR-3.4: 哲学概念转述准确（弗洛姆术语中文通行译法）；scale 1-5；threshold >=4；证据：抽样核对

## Task 4: 《幸福的婚姻》（John Gottman）知识包 — gottman-seven-principles
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - R：核验 Gottman "爱情实验室"（Love Lab）背景、本书（1999，与 Nan Silver 合著）七原则结构、"末日四骑士"（批评/蔑视/辩护/冷战，Four Horsemen）、5:1 正负互动比、感情修复尝试（repair attempts）、爱情地图（love maps）等核心概念；中译本信息（浙江人民/中信等，以核验为准）
  - I：洞察（如"蔑视是离婚最强预测因子""婚姻预测的实证方法论"）
  - E：concepts/ 5–6 篇（戈特曼与爱情实验室、末日四骑士、七原则框架（上：完善爱情地图/培养喜爱赞美/彼此靠近/接受影响）（下：解决可解决问题/克服僵局/创造共同意义）、5:1 比率与修复尝试）、examples/ 2 篇（婚姻关系自查（原创编排）、七原则实践计划）、references/ 2 篇、index.md、log.md、insights.md、facts.md
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-5, AC-6, AC-8, AC-9
- **Test Requirements**:
  - `rule` TR-4.1: facts.md ≥30 条、P0 双信源；证据：facts.md + 信源
  - `rule` TR-4.2: 文档数量与 toctree 合规；证据：文件核对
  - `rule` TR-4.3: 引用合规；证据：引用清单
  - `rubric` TR-4.4: 七原则与四骑士内容与原书框架一致、无遗漏无虚构；scale 1-5；threshold >=4；证据：抽样核对

## Task 5: 《爱的五种语言》（Gary Chapman）知识包 — five-love-languages
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - R：核验 Chapman 背景（牧灵辅导）、本书（1992）五种爱语框架（肯定的言词/精心的时刻/接受礼物/服务的行动/身体的接触）、"爱箱"（emotional love tank）隐喻、中译本信息（中国轻工业出版社/江西人民等，以核验为准）；同时调研学界对该框架实证基础的评价（争议呈现，NFR-5）
  - I：洞察（如"爱语差异作为关系错位的解释模型""流行心理学的实证争议"）
  - E：concepts/ 5–6 篇（作者与成书背景、爱箱隐喻与核心命题、五种爱语逐一解读（可分 2 篇）、发现自己与伴侣爱语的方法、学界评价与适用边界）、examples/ 2 篇（爱语自测与应用场景（原创编排）、阅读实践路径）、references/ 2 篇、index.md、log.md、insights.md、facts.md
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-5, AC-6, AC-8, AC-9
- **Test Requirements**:
  - `rule` TR-5.1: facts.md ≥30 条且含"学界评价"类事实信源；证据：facts.md + 信源
  - `rule` TR-5.2: 文档数量与 frontmatter 合规；证据：文件核对
  - `rule` TR-5.3: 引用合规；证据：引用清单
  - `rubric` TR-5.4: 争议呈现公允（不背书也不简单否定）；scale 1-5；anchors 1=无批判全盘接受/3=提及争议但浅/5=公允呈现实证讨论；threshold >=4；证据：抽样核对

## Task 6: 《依恋》（Amir Levine & Rachel Heller）知识包 — attached
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - R：核验本书（2010，Attached: The New Science of Adult Attachment）背景、成人依恋三类型（焦虑型/回避型/安全型，anxious/avoidant/secure）、依恋系统激活与依恋行为、Bowlby/Ainsworth 依恋理论源流（学术背景）、"抗议行为"（protest behavior）、去激活策略（deactivating strategies）、焦虑-回避陷阱（anxious-avoidant trap）等概念；中译本信息（以核验为准）
  - I：洞察（如"依恋视角重写婚恋冲突解释""安全基地的可获得性"）
  - E：concepts/ 5–6 篇（依恋理论源流：从 Bowlby 到成人依恋、三种依恋类型、依恋系统如何运作、焦虑-回避配对陷阱、走向安全：策略与方法）、examples/ 2 篇（依恋类型自察与关系场景分析（原创编排）、阅读实践路径）、references/ 2 篇、index.md、log.md、insights.md、facts.md
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-5, AC-6, AC-8, AC-9
- **Test Requirements**:
  - `rule` TR-6.1: facts.md ≥30 条、理论源流事实（Bowlby/Ainsworth）双信源；证据：facts.md + 信源
  - `rule` TR-6.2: 文档数量与 toctree 合规；证据：文件核对
  - `rule` TR-6.3: 引用合规；证据：引用清单
  - `rubric` TR-6.4: 依恋类型描述与学界定义一致；scale 1-5；threshold >=4；证据：抽样核对

## Task 7: 《男人来自火星，女人来自金星》（John Gray）知识包 — mars-venus
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - R：核验本书（1992）出版现象（长销纪录）、核心隐喻（火星/金星）、主要论点（男女沟通方式差异、"洞穴期"、计分方式差异、情感需求 12 种等）、中译本信息；**重点**调研学界批评（性别刻板印象、缺乏实证支持、与两性相似性研究 meta-analysis 如 Hyde 2005 "性别相似性假说" 的对照），按 NFR-5 公允呈现争议
  - I：洞察（如"流行话语的解释力与科学边界""时代语境：1990 年代性别角色话语"）
  - E：concepts/ 5–6 篇（成书与出版现象、火星金星隐喻与核心主张、沟通差异论的主要内容、情感需求与"计分"模型、学界批评与性别相似性证据、如何批判性阅读本书）、examples/ 2 篇（沟通场景的批判性应用（原创编排）、阅读路径与阅读警示）、references/ 2 篇、index.md、log.md、insights.md、facts.md
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-5, AC-6, AC-8, AC-9
- **Test Requirements**:
  - `rule` TR-7.1: facts.md ≥30 条且含学界批评信源（如 Hyde 2005 等公开学术资料）；证据：facts.md + 信源
  - `rule` TR-7.2: 文档数量与 frontmatter 合规；证据：文件核对
  - `rule` TR-7.3: 引用合规；证据：引用清单
  - `rubric` TR-7.4: 批判视角充分且对原书主张转述公允（不歪曲稻草人）；scale 1-5；anchors 1=全盘照搬或全盘否定/3=有批评但失衡/5=转述公允+批评有据；threshold >=4；证据：抽样核对

## Task 8: 分组导言、跨书知识地图与交叉引用
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4, Task 5, Task 6, Task 7
- **Description**:
  - 完善 `relationships/index.md`：分组导言（6 书在亲密关系知识谱系中的三层定位：学术实证 [Miller/Gottman/Levine]、哲学经典 [Fromm]、通俗实用 [Chapman/Gray]）、6 束导航表（一句话定位 + 核心概念标签）、Mermaid 知识地图（理论源流与对话关系：依恋理论 ↔ Gottman 实证 ↔ Fromm 哲学 ↔ 爱语/火星金星通俗模型）、阅读路径建议（入门顺序）
  - 在各 bundle 的 insights.md 中补充跨书对比视角与 bundle 间相对链接（如 attached ↔ gottman、five-love-languages ↔ mars-venus 的互补与张力、art-of-loving 对其他五本的哲学审视）
  - 检查 G3 质量门：跨书框架可迁移（触发场景+核心步骤+反模式体现在阅读建议中）
- **Acceptance Criteria Addressed**: AC-10, AC-2
- **Test Requirements**:
  - `rule` TR-8.1: relationships/index.md 含 Mermaid 地图、对比表、6 条 toctree；证据：文件内容
  - `rule` TR-8.2: 每个 bundle 的 insights.md 至少含 2 条指向其他 bundle 的有效相对链接；证据：链接扫描
  - `rubric` TR-8.3: 知识地图质量；scale 1-5；anchors 1=6 束孤立/3=有对比但浅/5=谱系清晰有洞见；threshold >=4；证据：主控评审

## Task 9: 上层索引更新
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - 更新 `doc/bundles/think/index.md`：分组导航表新增 relationships 行；toctree 增加 `relationships/index`；域描述同步
  - 更新 `doc/bundles/index.md`：frontmatter 统计（total_bundles 280→286、groups 32→33）；think 域标题统计（5 束 2 组 → 11 束 3 组）；think 分组表新增 relationships 行；生态 Mermaid 图 think 节点标签更新（psi · laozi → psi · laozi · relationships）；推荐入门路径 think 节点同步
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `rule` TR-9.1: think/index.md 含 relationships 表行与 toctree 条目；证据：diff 核对
  - `rule` TR-9.2: bundles/index.md 统计数字、表格、Mermaid 三处一致更新；证据：diff 核对

## Task 10: V 阶段 — 质量门、事实抽查与合规扫描
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 9
- **Description**:
  - 运行 `invoke gates.all`（UTF-8 + toctree）与 `invoke clean && invoke build`，修复所有报错/警告
  - 事实抽查：每束抽 5 条事实（共 30 条）回溯信源 URL，记录核验表
  - 版权扫描：逐文件检查直引句（引号/引用块），登记引用清单（位置、字数、出处）；确认无 >30 字未标注直引、无盗版链接
  - 命名扫描：文件名 kebab-case 纯英文（NN- 前缀允许）、无中文文件名
  - 路径扫描：无 `file:///` 绝对路径、无断链
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-5, AC-6, AC-2
- **Test Requirements**:
  - `rule` TR-10.1: `invoke gates.all` 退出码 0；证据：命令日志
  - `rule` TR-10.2: `invoke build` 0 错误 0 警告；证据：构建日志
  - `rule` TR-10.3: 30 条事实抽查全部可溯源、P0 双信源一致；证据：核验表
  - `rule` TR-10.4: 引用清单完整且全部合规；证据：扫描记录
  - `rule` TR-10.5: 文件名与路径扫描 0 违规；证据：扫描输出

## Task 11: 独立评审（Review 阶段，fresh context）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 10
- **Description**:
  - 委派一个全新上下文的只读评审（general_purpose_task），给予评审契约：用户目标、spec.md/tasks.md 绝对路径、产出目录、验收标准 AC-1–AC-10
  - 评审重点：AC-8（事实/观点归属准确性，逐束抽查理论名称与作者归属）、AC-9（解读深度）、AC-10（知识地图）、AC-6（版权合规独立复核）、AC-3/AC-4（独立重跑质量门）
  - 评审结果写入 review.md；pass 则收尾，fail 则将 actionable findings  materialize 为 Task 12+ 修复 issue
- **Acceptance Criteria Addressed**: AC-1–AC-10（全部）
- **Test Requirements**:
  - `rule` TR-11.1: review.md 存在且每个 AC 有独立证据覆盖；证据：review.md
  - `rule` TR-11.2: 评审结果为 pass，或所有 fail 项已转为 pending issue；证据：Review History

## Task 12: 评审问题修复闭环（条件触发）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 11
- **Description**:
  - 若评审 fail：将每个 actionable finding 按 Issue 模板登记到 tasks.md，逐一修复、自验、重跑质量门，然后启动新一轮独立评审（fresh reviewer）
- **Acceptance Criteria Addressed**: 视评审发现
- **Test Requirements**:
  - `rule` TR-12.1: 所有 issue 状态为 completed/cancelled（cancelled 须用户批准）；证据：tasks.md 状态
  - `rule` TR-12.2: 修复后重跑 `invoke gates.all` 与 `invoke build` 通过；证据：命令日志
