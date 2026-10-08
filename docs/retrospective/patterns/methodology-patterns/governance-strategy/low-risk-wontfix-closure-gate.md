---
type: Pattern
id: "low-risk-wontfix-closure-gate"
title: "审查低危问题「登记不修」闭环门"
source: "../../../reports/concepts/milestone/real-need-day1-wiki-retrospective-20261001.md"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/governance-strategy/low-risk-wontfix-closure-gate.toml"
maturity: "L1"
validation_count: 1
reuse_count: 0
documentation_level: "standard"
domain: "methodology"
layer: "methodology"
category: "governance-strategy"
tags: [review-closure, wontfix, risk-acceptance, governance, audit-trail]
---
# 审查低危问题「登记不修」闭环门

## 来源

本模式萃取自以下实践：

- `docs/retrospective/reports/concepts/milestone/real-need-day1-wiki-retrospective-20261001.md`：real-need-day1 任务独立审查（2026-10-01），P3-3「保留信息组合残余可映射性」以书面登记不修方式闭环，复核后 PASS 结论维持
- 关键洞察：惯性认知是「审查发现问题必须修完才能 PASS」；低危项强行修复可能引入新风险，显式登记反而更可审计

## 核心思想

**低危问题不修复也可以是合规闭环——前提是显式登记、书面论证、复核确认三要素齐备。**

「修复一切发现的问题」在 P0/P1 高危场景是铁律，但对 P2/P3 低危项机械套用会产生两类伤害：强行修复引入新风险、修复成本远超风险敞口。本模式提供第三条路：用书面化决策替代代码变更，让「不修」本身成为可审计的治理行为。

**一句话概括**：不修复不是问题，不记录才是问题。

## 触发场景

- 独立审查/代码评审/安全评估发现的 P2/P3 低优先级问题，经评估不拟修复
- 修复行为本身可能引入新风险的场景（如脱敏产物的过度处理导致内容失真）
- 风险敞口小于修复成本的残余风险处置

## 核心做法（三要素 + 台账）

1. **低危定级**：登记条目含位置、描述、风险等级（P2/P3），定级理由写明影响面与发生概率
2. **书面论证**：不修理由含三维度——影响面分析、触发概率、修复成本（含引入新风险的可能）
3. **复核确认**：复核人显式确认登记内容，并明确维持原审查结论（如 PASS 维持）
4. **台账保留**：登记条目进入可检索台账，供后续同类问题比对与定期回顾

## 反模式

| 反模式 | 后果 |
|--------|------|
| 口头「知道了」无任何记录 | 问题沉没，同类问题反复发现 |
| 为 PASS 强行修复低危项 | 修复引入新风险，返工成本非线性放大 |
| 登记但无论证 | 无法区分「审慎接受」与「偷懒放过」 |
| 无复核确认 | 登记沦为单方声明，审计价值归零 |

## 检验标准

1. 每条「不修」登记含三要素：低危定级 + 书面论证 + 复核确认
2. 复核记录可查（谁确认、何时、结论是否维持）
3. 后续同类问题可与台账比对，避免重复评估
4. P0/P1 问题不适用本门——高危项必须修复，无豁免

## 迁移示例

- **代码评审**：wontfix 决策的规范化记录（issue 附 wontfix 标签 + 评审意见）
- **安全运营**：CVE low-severity 延期处置的风险接受单（risk acceptance）
- **合规审计**：审计观察项（observation）而非不符合项（nonconformity）的处理流程
- **硬件工程**：已知瑕疵的「use-as-is」让步接收流程

## 成熟度说明

当前 L1-draft（单案例验证）。待第二个审查闭环场景复用且四条检验标准全过后升 L2。
