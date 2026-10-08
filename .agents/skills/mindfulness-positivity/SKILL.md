---
name: mindfulness-positivity
version: 1.0.0
description: "正念（Mindfulness）与正面/积极心态（Positive Thinking）的概念辨析与整合方法论门面。当用户提到'正念'、'正面'、'积极心态'、'正能量'、'mindfulness'、'positive thinking'、'乐观'、'习得性乐观'、'有毒正能量'、'toxic positivity'、'先接纳后重构'、'正念和积极有什么区别'、'正念是不是就是往好处想'、'情绪调节'、'自我调节'、'想开点'、'别想太多'，或要求辨析二者、生成二者主题的教程/文章/知识包、或把二者整合为自我调节方案/辅导文案时，必须使用此技能。提供四场景决策树（概念问答/内容产出/自我调节方案/知识包沉淀）、七维度辨析框架、'先接纳后重构'四步整合法与心理健康安全边界（不诊断、不替代治疗、危机转介、证据分级）。本技能承载完整知识底座（docs/knowledge/mindfulness-positivity），避免仅凭印象作答导致概念混同。"
argument-hint: "<场景> [主题] [深度：quick/standard/deep]"
user-invocable: true
paths:
  - ".agents/skills/mindfulness-positivity/**"
  - "../../../docs/knowledge/mindfulness-positivity/**"
title: "Mindfulness-Positivity 正念与正面辨析整合门面"
x-toml-ref: "../../../.meta/toml/.agents/skills/mindfulness-positivity/SKILL.toml"
---

# Mindfulness-Positivity 正念与正面辨析整合门面

> 本 Skill 是**工作流门面（L1）**：四场景决策树 + 七维度辨析框架 +「先接纳后重构」整合法 + 心理健康安全边界。L2 完整知识底座（22 条事实、3 条洞察、模式操作版、信源台账、V 审查记录）位于 [docs/knowledge/mindfulness-positivity](../../../docs/knowledge/mindfulness-positivity/index.md)。

## 1. Skill ID

`mindfulness-positivity`（内部 ID，对外名称：正念与正面辨析整合）

## 2. 功能描述

本技能按四场景自动路由，每场景有明确产物：

| 场景 | 触发特征 | 产物 |
|---|---|---|
| **A 概念问答** | 用户问"正念和正面有什么区别/哪个更好" | 一句话结论 + 七维度对照（必要时配图） |
| **B 内容产出** | 生成教程/文章/文案/知识包 | 引用知识底座事实（F-xxx）产出的 OKF 风格内容 |
| **C 自我调节方案** | 用户希望处理自己的负面情绪 | 「先接纳后重构」四步方案 + 60 秒练习 + 安全边界检查 |
| **D 知识沉淀** | 把该主题沉淀为知识包/模式/Skill | 按七概念 R→I→E→V→C 链路执行 |

> **为什么必须用本技能而非自由发挥？** 正念与正面在中文语境里常被混用（"要正念一点"≈"要正面一点"），自由作答容易把两个立场相反的概念合并成"积极心态"。本技能强制先做概念锚定（F-006 定义、F-013 模型），再从四场景之一输出，保证"看见"与"改写"不被混淆。

## 3. 何时使用本技能

当用户提到以下任何内容时触发：

- "正念"、"mindfulness"、"正念减压"、"MBSR"、"MBCT"、"觉察"、"接纳"
- "正面"、"积极心态"、"积极心理学"、"正能量"、"乐观"、"习得性乐观"、"往好处想"、"想开点"
- "有毒正能量"、"toxic positivity"、"有害积极"
- "正念和积极/正面有什么区别"、"正念是不是就是往好处想"、"哪个对我更有用"
- "情绪调节"、"自我调节"、"怎么处理负面情绪"、"先接纳后重构"
- 任何涉及二者辨析、二者主题写作、二者整合辅导的请求

> **关于触发**：即使没有明说"用 skill"，只要核心对象落在正念/正面这一对概念上，就应使用本技能——底层辨析框架与安全边界是自由作答不具备的。

## 4. 场景决策树

```
用户请求属于哪种？
├─ 只是想知道区别/哪个适合我？ → 场景A 概念问答（第5节框架，quick 即可）
├─ 要写教程/文章/文案/知识包？ → 场景B 内容产出（必须引用知识底座事实编号）
├─ 要处理自己的情绪/自我调节？ → 场景C 自我调节方案（第6节四步法 + 安全边界）
└─ 要沉淀为知识包/模式/Skill？ → 场景D 知识沉淀（R→I→E→V→C，depth=standard）
```

**深度裁剪**：A/C 默认 quick；B/D 默认 standard；D 场景必须走完 V 对抗审查（不可裁剪）。

> **为什么 D 必须 V？** 知识沉淀入库是对外可复用资产，未对抗审查的模式会带着"先接纳后重构有因果证据"之类错误印象入库——见知识底座 V 记录中的 V-2 修正。

## 5. 核心方法 A：七维度辨析框架（场景 A/B 使用）

任何辨析输出必须覆盖以下维度（来源：知识底座 F-006/F-009~F-018）：

| 维度 | 正念（看见） | 正面（改写） |
|---|---|---|
| 本质 | 有目的、在当下、不加评判地注意（F-006） | 有选择地评价与重构认知（F-013） |
| 对负面情绪 | 允许在场、观察它（F-006） | 尽快替换成积极想法（F-015） |
| 评判立场 | 非评判（F-006） | 评价筛选（F-013） |
| 时间方向 | 当下此刻 | 偏向前方（目标/希望） |
| 目标 | 觉察本身，不追求特定情绪 | 达成积极情绪与认知 |
| 过头风险 | 被误用为"放空/逃避" | 有毒正能量：压抑真实感受（F-015~F-018） |
| 一句话 | "此刻发生了什么？"——看见 | "往好处想。"——改写 |

**强制结论句**：底层立场相反、顺序上互补——先接纳后重构是健康路径，跳过接纳的硬转积极即有毒正能量（F-018）。

## 6. 核心方法 B：「先接纳后重构」四步整合法（场景 C 使用）

```
① 觉察（20s）：命名此刻感受："我现在感到焦虑/愤怒/难过"，不分析不评价
② 接纳（30-60s）：允许它在场，用呼吸锚点观察身体感受与念头，不与之对抗
③ 现实检验（1-2min）：把事实与解释分开，逐条问"有证据支持吗"
④ 重构（1-2min）：在事实基础上选择更准确的解释或更可行的行动（ABCDE 的 D-E / 认知重评）
   ——完成后检查：重构是否仍否定真实感受？是则退回②
```

**反模式（输出方案时必须对照）**：

1. 跳过接纳直接转念 → 有毒正能量（压抑→反弹）
2. 把觉察误读为认同 → 看见情绪 ≠ 沉浸其中
3. 重构脱离事实 → 不核查证据的"往好处想" = 伪积极
4. 把正念当放空/逃避 → 回避问题而非面对问题
5. 顺序颠倒 → 先重构后接纳 = 用重构否定感受

> **为什么顺序不可反？** 知识底座 I-3：正念管"与想法的关系"，认知技术管"想法的内容"——先接纳让重构有现实基础；顺序反了，重构就变成对感受的否定，机制上与有毒正能量同构（F-015~F-018）。

## 7. 质量门与安全检查清单

产出前逐项确认：

- [ ] **概念锚定**：涉及"正念"的定义引用 F-006 操作定义原文，不写成"想开点"的同义词
- [ ] **证据分级**：研究结论标注口径（机构综述/研究团队/经典文献）；"先接纳后重构"标注为机制性顺序假设（L1），不声称已证因果
- [ ] **事实溯源**：写作用到的事实带 F-xxx 编号（见[信源台账](../../../docs/knowledge/mindfulness-positivity/references/source-inventory.md)）
- [ ] **心理健康安全边界**：内容不得包含诊断、治疗、用药建议措辞；涉及持续情绪困扰/自伤伤人念头时，输出转专业干预提示而非继续自我调节建议
- [ ] **有毒正能量检测**：方案中无"不许难受/别想太多/这没什么"类否定感受话术
- [ ] **交付形态**：B 场景产物为 OKF 风格（frontmatter + 一句话摘要 + 事实编号）；D 场景产物走完整质量门（G1 无因果词/G2 四元组/G3 模式/V 审查）

> **为什么安全边界是硬约束？** 本主题贴近心理健康，AI 内容若把心理技巧包装成"处方"会产生真实伤害（V-6/V-8 修正结论）。凡用户表达临床求助信号（诊断询问、危机描述、治疗选择），本技能只提供科普边界与转介建议，不越界作答。

## 8. Gotchas（陷阱与反直觉行为）

- **"正念"≠"正面"**：最常踩的坑——把"要正念一点"理解成"要正面一点"；任何输出先锚定 F-006 定义。
- **积极本身不毒，否定感受才毒**：判断有毒正能量的关键不是"积不积极"，而是"负面情绪有没有被承认"（F-018）。
- **ABC 的 D 步不是"往好处想"**：驳斥必须基于证据；无证据的驳斥即伪积极。
- **练习"没效果"不是失败**：正念练习觉察到"还是很烦"就是成功——这是看见，不是压抑；方案中必须写明，防止用户因预期错误放弃。
- **AI 心理内容伦理**：本技能产出是自我调节科普，禁止自称"治疗/治愈"；危机场景只做转介。

## 9. 关键参考

| 参考 | 路径 | 何时查阅 |
|---|---|---|
| **知识包入口（L2，运行时首选）** | [../../../docs/knowledge/mindfulness-positivity/index.md](../../../docs/knowledge/mindfulness-positivity/index.md) | 任何场景：事实表 F-001~F-022、洞察、模式定义 |
| 正念教程 | [../../../docs/knowledge/mindfulness-positivity/concepts/01-zheng-nian-mindfulness.md](../../../docs/knowledge/mindfulness-positivity/concepts/01-zheng-nian-mindfulness.md) | 场景 A/B 涉及正念机制、练习、误解 |
| 正面教程 | [../../../docs/knowledge/mindfulness-positivity/concepts/02-zheng-mian-positivity.md](../../../docs/knowledge/mindfulness-positivity/concepts/02-zheng-mian-positivity.md) | 场景 A/B 涉及积极心理学、ABCDE、有毒正能量 |
| 联系与区别（操作版） | [../../../docs/knowledge/mindfulness-positivity/concepts/03-connection-and-differences.md](../../../docs/knowledge/mindfulness-positivity/concepts/03-connection-and-differences.md) | 场景 A/C：七维度对照、四步法操作版、场景速查 |
| 信源台账 | [../../../docs/knowledge/mindfulness-positivity/references/source-inventory.md](../../../docs/knowledge/mindfulness-positivity/references/source-inventory.md) | 事实溯源、口径分级 |
| V 审查记录 | [../../../docs/knowledge/mindfulness-positivity/references/adversarial-review.md](../../../docs/knowledge/mindfulness-positivity/references/adversarial-review.md) | 需要了解本主题已知修正结论时 |

## 10. Changelog

- **v1.0.0** (2026-10-03): 初始版本。随知识包 `docs/knowledge/mindfulness-positivity/`（session sc-20261003-mindfulness-positivity，R→I→E→V→C）同步萃取：四场景决策树、七维度辨析框架、「先接纳后重构」四步整合法、心理健康安全边界、五条 Gotchas。
