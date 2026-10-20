---
okf_version: "0.2"
category: tech
title: 'Medium 平台知识包：从"思想之地"到注意力订阅平台'
description: "基于公开资料多源调研的 Medium.com 知识束：平台总览、历史时间线、产品设计、商业模式（会员+Partner Program）、技术架构、生态治理、竞争格局（Substack/Ghost）与 2022-2025 扭亏复盘；全部数量陈述带机构口径，冲突口径并列"
tags: [medium, publishing-platform, business-model, partner-program, substack, creator-economy, turnaround, product-research]
status: stable
stale_after: "2027-06-30"
date: "2026-10-20"
author: "SpecWeave"
summary: "Medium 平台知识束：总览/时间线/产品/商业模式/技术/生态/竞争/转型，冲突口径并列，13 信源可溯源。"
---

# Medium 平台知识包

> Medium 是美国在线出版平台，2012 年由 Evan Williams（Blogger/Twitter 联合创始人）创立，以"深度阅读时间"为核心计量单位，靠会员订阅（$5/月）与 Partner Program 按阅读时长向作者分成，2024-08 起月度盈利。本束基于截至 2026-10-20 的公开资料，按七概念方法论 R→I→E→V→C 生成；Medium 为私有公司、无官方财报，所有事实可溯源至 [信源登记](references/source-inventory.md)，冲突口径并列标注。

---

## 导航

```{toctree}
:maxdepth: 2
:hidden:

concepts/index
examples/index
references/index
log
```

| 类别 | 文档 | 说明 |
|------|------|------|
| **概览** | [Medium 平台总览](concepts/00-overview.md) | 产品身份、创始人基因、一句话商业模式模型 |
| **时间线** | [历史时间线 2012–2026](concepts/01-timeline.md) | 设计时代 / 商业模式时代 / 转型时代三阶段 |
| **产品** | [产品形态与设计理念](concepts/02-product-design.md) | 编辑器、Claps、Tag、Publications、阅读指标 |
| **模式** | [商业模式](concepts/03-business-model.md) | 会员订阅 + Partner Program 分成引擎 |
| **技术** | [技术架构](concepts/04-architecture.md) | Node.js/AWS/Go、Elevators 推荐系统 |
| **生态** | [内容生态与治理](concepts/05-ecosystem-governance.md) | 作者信任危机、治理实验、多国访问限制 |
| **竞争** | [竞争格局](concepts/06-competition.md) | 与 Substack/Ghost 的范式分岔 |
| **复盘** | [2022–2025 转型复盘](concepts/07-turnaround.md) | 资本重组、规模收缩、内容治理的扭亏之战 |
| **示例** | [作者收入模式演算](examples/01-author-earnings-model.md) | Medium vs Substack 分成数学对照 |
| **信源** | [信源登记](references/source-inventory.md) | S01～S13，含级别与转引链 |
| **审查** | [对抗审查记录](references/adversarial-review.md) | V 阶段四视角审查意见与修正 |
| **日志** | [变更日志](log.md) | 生成过程记录 |

## 推荐阅读路径

1. **5 分钟了解**：平台总览 → 商业模式 → 竞争格局。
2. **做内容/写作平台研究**：历史时间线 → 商业模式 → 生态治理 → 转型复盘。
3. **做创作者/自媒体决策**：竞争格局 → 作者收入演算 → 数据口径说明。

## 三条核心结论

1. **Medium 的真正创新是"以注意力质量计费的订阅引擎"**：自始以阅读时间/深度而非 PV 为核心计量单位（2014 年宝马 Re:Form 实验即按阅读分钟数承诺），由此天然与广告模式冲突，最终走向"会员订阅+按阅读时长分成"——2024-08 首次月度盈利验证了该路径 [S02][S06]。
2. **平台与作者的权力结构是 Medium 二十年摇摆的根因**：聚合者必须掌控分发与分成，而"质量民主化"使命要求放权给作者——三次信任危机（2015/2017/2018）与 Substack 的"作者拥有受众"范式反超，都源于这一结构性矛盾 [S02][S08]。
3. **扭亏靠"做减法"而非"做加法"**：2022-2024 年 Stubblebine 通过资本重组（recap）、裁员 250→77 人、内容质量治理三线并进，把月亏 250-260 万美元翻转为月度盈利——内容平台陷入亏损时，先修复供给质量与资本结构，比继续烧钱换增长更有效 [S04][S06]。

## 数据使用须知

- 所有数量陈述均标注**机构 + 时间 + 口径**（如"CEO 公开口径，2024-04"）。
- Medium 无公开财报；转型期月亏损存在 250 万（播客访谈）与 260 万（Simon Willison 摘录）两口径，Substack 付费订阅存在 500 万（The Teardown）与 2000 万（DigitalMarket.World）两口径——**本束全部并列、不合并**，见 [信源登记](references/source-inventory.md)。
- "timeless 媒体品牌"等方向性陈述仅来自播客摘要级证据，显式标注低置信 [S12]。
- 技术架构章节仅含 2012-2017 公开信息，后续细节未公开 [S01]。

---

**调研截止**：2026-10-20｜**规范**：OKF v0.2（Open Knowledge Format）｜**方法**：七概念 R→I→E→V→C（depth=standard，含对抗审查）