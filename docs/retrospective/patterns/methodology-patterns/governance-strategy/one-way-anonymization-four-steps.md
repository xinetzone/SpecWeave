---
type: Pattern
id: "one-way-anonymization-four-steps"
title: "私域内容单向脱敏四步法"
source: "../../../reports/concepts/milestone/real-need-day1-wiki-retrospective-20261001.md"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/governance-strategy/one-way-anonymization-four-steps.toml"
maturity: "L1"
validation_count: 1
reuse_count: 0
documentation_level: "standard"
domain: "methodology"
layer: "methodology"
category: "governance-strategy"
tags: [anonymization, privacy, desensitization, private-domain, governance]
---
# 私域内容单向脱敏四步法

## 来源

本模式萃取自以下实践：

- `docs/retrospective/reports/concepts/milestone/real-need-day1-wiki-retrospective-20261001.md`：real-need-day1 私域 OKF Wiki 教程任务（2026-10-01），285 行私域纪要 → 20 文件知识产物，独立审查首轮 0 P0/0 P1
- 关键洞察：「不落映射表」决策把脱敏从「可回查」变为「单向」——映射表本身才是最大泄露面

## 核心思想

**脱敏在写作生成期单向执行，不留下任何可逆回原文的映射物。**

传统脱敏是「先写原文、后扫描替换、留对照表备查」——对照表一旦泄露，全部脱敏前功尽弃。本模式反其道而行：脱敏词名单前置为写作约束，生成期直接产出代号化文本，映射对照表文件数恒为 0。

**一句话概括**：最安全的映射表，是从未存在过的映射表。

## 触发场景

- 含个人隐私/商业秘密的会议纪要、访谈记录、内部材料转为知识产物（Wiki/教程/复盘）
- 需要对外发布但保留部分事实细节（金额/日期/地名）的脱敏场景
- 私域内容工作流（内容敏感度预检判定为 Private）的产物生成

## 核心做法（四步）

1. **名单前置**：写作前建立脱敏词名单（人名/机构/地点变体/绰号/缩写，40+ 词量级），作为生成期硬约束而非事后检查项
2. **生成期代号化**：角色与实体在写作时直接使用代号，正文从未出现真实姓名——不存在「写后替换」环节
3. **零映射表**：代号↔实名对照关系不写入任何文件（不落盘、不入日志、不入提交）；映射表文件数=0 作为验收硬指标
4. **组合风险登记**：对按方案保留的信息（金额/日期/地名等）做组合可映射性评估；低危组合以「书面登记+论证+复核确认」方式闭环，参照 [低危登记不修闭环门](low-risk-wontfix-closure-gate.md)

## 反模式

| 反模式 | 后果 |
|--------|------|
| 事后扫描补丁式脱敏 | 替换遗漏、上下文残留，审查轮才暴露 |
| 保留映射对照表「备查」 | 对照表本身成为单点泄露面，脱敏成果归零 |
| 逐词脱敏忽略组合推断 | 单个词已脱敏，但「地名+金额+日期」组合仍可映射回实体 |
| 过度脱敏删光金额/日期 | 内容失真，知识产物失去事实价值 |

## 检验标准

1. 脱敏词名单在正文中扫描零命中（机械检查）
2. 映射对照表文件数 = 0（全仓扫描）
3. 保留信息的组合可映射性评估有书面登记记录
4. 残余风险项有显式处置决策（修复或登记不修），独立审查可查

## 迁移示例

- **医疗/法律行业**：病例报道、判例教学的当事人匿名化（生成期化名，不留对照表）
- **咨询行业**：客户案例对外发布前的脱敏改写
- **安全领域**：内部事故复盘对外发布前的攻击面信息处理
- **新闻调查**：线人保护——稿件生成期即使用代号，编辑系统不留实名记录

## 成熟度说明

当前 L1-draft（单案例验证）。待第二个私域脱敏任务复用且四条检验标准全过后升 L2。
