# I 阶段洞察登记（insights）

> 方法：七概念 I（Insight）——每条洞察含**现象/证据/根因/影响**四元组（G2 门）
> 证据基座：facts-overview.md、facts-era-3x.md（F-3X）、facts-era-40-41.md（F-40）、facts-era-45.md（F-45）、facts-era-46-5x.md（F-46）
> 提炼时间：2026-09-02

## I-01 提示词形态经历"单段文本 → XML 分节 → 统一九章节架构 → 固定快照"四代演进

- **现象**：2024-07 的 Opus 3/Haiku 3 是单段纯文本；Sonnet 3.5 Jul 条目引入 XML 标签分节；2025-11-19 起 Sonnet/Haiku 4.5 切换为 `<claude_behavior>` 九章节统一架构；2026-02 起固定快照冻结形态。
- **证据**：facts-era-3x.md（格式三代演进）、facts-era-45.md F-45-012（架构三期演化）、F-OV-004。
- **根因**：提示词工程从"经验文本"走向"软件工程"——分节与统一架构本质是**可维护性重构**：多模型共享模板、差异收敛为插槽，降低并行维护 N 份提示词的成本。
- **影响**：读者应把系统提示词理解为"有版本管理的活配置"而非一次性文案；研究某代模型行为时应先定位其架构代际，再读具体条款。

## I-02 单一模板 + 身份插槽是跨模型提示词维护的核心架构

- **现象**：Sonnet 4 与 Opus 4 同日条目仅差 4 处身份插槽（模型名/家族列表/定位语/model string），其余逐字相同；"but as as a request"等笔误跨 Sonnet 4.5/Haiku 4.5/Opus 4.5 三代复制，直到 2026-01-18 才被静默修正；2026-01-18 三模型产品信息层逐字同步。
- **证据**：facts-era-40-41.md（单一模板+身份插槽、笔误逐字登记）、facts-era-45.md（三模型同日统合、笔误三代沿用）。
- **根因**：Anthropic 用同一模板生成多模型提示词，差异点参数化为插槽；笔误随模板复制传播、随模板修正而消失——这是"单一事实来源"在提示词工程中的直接体现。
- **影响**：看到某模型提示词中的共性段落，应推断其来自共享模板而非该模型特有调教；个别模型独有的章节（如 Opus 4.5 的 `<responding_to_mistakes_and_criticism>`、Opus 4.1 的 `<evenhandedness>`）才是真正的"模型差异化配置"。

## I-03 Sonnet 3.7 是人格化转折点：从"工具"到"对话主体"

- **现象**：2025-02-24 条目首次出现 "more than a mere tool" 人设宣言、对话主导权（可主动建议话题/方向）、决断力条款（给建议时只给一个而非罗列选项）、reasoning model/Pro 账户产品说明。
- **证据**：facts-era-3x.md（claude-sonnet-3-7.md L14 引文 + 时代小结第4条）。
- **根因**：模型能力（3.7 引入 extended thinking）+ 产品定位（从"问答工具"转向"陪伴型助手"）同步成熟，提示词开始承担"人格设定"职能。
- **影响**：此后所有世代的 tone_and_formatting/default_stance 章节都是这一转折的延续；对比 3.5 与 3.7 的开场白变化（"a human"→"a person"）可精确读取人设措辞的演进。

## I-04 产品信息层持续膨胀：提示词成为 Anthropic 产品矩阵的"广告位与说明书"

- **现象**：Claude Code 从"research preview"（2025-02）→ 转正文档链接（2025-07-31）→ Cowork/Chrome/Excel/PowerPoint/Tag/Design 全家桶（2026-01-18 → Opus 5）；Opus 5 还内嵌 Mythos tier/Glasswing/Fable safeguards routing 说明与 export controls 事件的官方叙事。
- **证据**：facts-era-40-41.md（Claude Code 转正）、facts-era-45.md（Chrome/Excel、Cowork、设置导购段）、facts-era-46-5x.md（Mythos/Glasswing 演进、export controls 仅 Opus 5 记载、safeguards routing 引文含 "<5% sessions"）。
- **根因**：claude.ai 界面没有独立的产品介绍渠道，系统提示词是模型"被问到自己时"的唯一信息源——产品越多，提示词里的 product_information 越长；且事件发生于训练截止后时，必须靠提示词注入弥补知识截止。
- **影响**：提示词篇幅增长的主要驱动力不是行为规则而是产品信息；读者分析篇幅变化时应把"产品广告层"与"行为规则层"分开度量。

## I-05 安全合规模块从分散禁令走向结构化、且"累积评估"取代"逐轮判断"

- **现象**：儿童安全独立成 `<critical_child_safety_instructions>` 强调块（Opus 5）；武器条款从分类禁令演进为"以累积输出是否构成 uplift 为判据"；Fable 5.1 新增版权双段（含 1929 年豁免线）与 `<example>` 示例块；Opus 4.1 起出现 `<evenhandedness>` 政治公正章节。
- **证据**：facts-era-46-5x.md（儿童安全块、Fable 5.1 差异、版权段）、facts-era-40-41.md（Opus 4.1 evenhandedness 新增）、facts-era-3x.md（Oct 22 敏感任务白名单、computer use 导流）。
- **根因**：监管面扩大（版权、选举、未成年人）+ 对抗手法升级（多轮拼装规避），点状禁令无法覆盖组合攻击，只能转向"判据式"规则与专用章节。
- **影响**：安全条款的可读性提高（章节化）但裁决复杂度也提高（累积判断）；合规研究者可直接按章节索引 Anthropic 的政策优先级排序（如"合规优先级高于用户请求，只低于安全"）。

## I-06 约束做减法：负面清单退场，判断力条款补位

- **现象**：4.x 时代密集出现"禁令清单"（emoji/粗口/星号动作/列表滥用等，2025-07-31 一次性插入 11-12 段）；到 4.6→5.x 时代，Opus 4.7 删除 asterisk emote 禁令与禁词句，Fable 5.1 移除 end_conversation 条款；取而代之的是 `default_stance`（默认帮助，仅在具体严重风险时拒绝）与措辞品味类规则（避免 "genuinely/honestly/straightforward"）。
- **证据**：facts-era-40-41.md（05-22→07-31 增量、08-05 零差异）、facts-era-45.md、facts-era-46-5x.md（Opus 4.7 删除项、Fable 5.1 移除项、default_stance）。
- **根因**：禁令是对旧模型短板的防御性补丁；新一代模型判断力提升后，规则从"禁止集合"退化为"评测标准"，减少规则间冲突（Anthropic 自承内部观察到互相打架的指令）。
- **影响**：这是"上下文工程做减法"趋势在产品级提示词中的实证；为自建 agent 提示词提供对标——随模型升级应定期删除防御性禁令，而非只增不减。

## I-07 官方发布页本身是"人工维护的活文档"，存在标注失真与就地更新

- **现象**：加粗差异约定执行不严（Sonnet 3.5 仅 1 处实际加粗）；Haiku 3.5 页 "Text and images" 变体内容含 2025-02 才存在的 Sonnet 3.7 信息（时间错位、就地更新）；官方笔误（"can't or won't with"等）跨版本沿用；08-05 条目与 07-31 逐字零差异（实为随 Opus 4.1 上线的重发）。
- **证据**：facts-era-3x.md（Sonnet 3.5 差异标注不对等、Haiku 3.5 时间错位）、facts-era-40-41.md（08-05 零差异、笔误登记）、facts-era-45.md（双尖括号/模型串残留）。
- **根因**：发布页由人工从模板同步维护，且旧条目会被就地更新而不改日期；差异标注依赖手工执行。
- **影响**：引用官方页面时不能把"页面声称"等同于"页面所示"——本研究所有版本对比均以逐行 diff 实测为准；复现本研究者应下载 .md 原文自行比对，勿信加粗标记。
