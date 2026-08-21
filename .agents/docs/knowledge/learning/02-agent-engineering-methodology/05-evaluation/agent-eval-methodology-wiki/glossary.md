---
id: "agent-eval-methodology-glossary"
title: "Agent评测方法论：核心术语表"
source: "spec:agent-eval-methodology-wiki"
category: "learning"
tags: ["agent-evaluation", "glossary", "methodology"]
date: "2026-08-05"
version: "0.1"
status: "draft"
---

# Agent评测方法论：核心术语表

> 本术语表收录 Agent 评测体系化建设涉及的核心术语，每个术语附一句话通俗解释，帮助不同背景的读者快速对齐概念。

---

## 核心术语

| 术语 | 英文 | 一句话通俗解释 |
|------|------|---------------|
| AI智能体 | AI Agent | 能自主感知环境、规划行动、调用工具来完成任务的大模型程序，好比"会自己动手做事"的AI助手 |
| 评测体系 | Evaluation System | 一套用于系统衡量Agent能力、质量与风险的完整流程和方法，类似"体检套餐"而非单一"测血压" |
| 基准测试 | Benchmark | 一组标准化的测试任务和评分规则，用来横向比较不同Agent的公开可比成绩 |
| 测试用例 | Test Case | 评测中单个具体的任务，包含输入场景、预期行为和评分标准，是评测的最小单元 |
| LLM裁判 | LLM-as-Judge | 用大模型充当评分员，代替人类对Agent输出进行打分的主观评测方法 |
| 奖励黑客 | Reward Hacking | Agent钻评测规则的漏洞来获得高分，但实际并未真正完成任务的现象，类似"作弊式应试" |
| 任务完成率 | Task Success Rate | 评测中Agent成功完成任务的比例，是衡量能力最直观的核心指标 |
| 数据污染 | Data Contamination | 评测数据被模型训练数据意外包含，导致"提前见过答案"而虚报成绩的问题 |
| 可复现性 | Reproducibility | 同一评测在相同条件下能重复得到一致结果的能力，是评测可信度的基石 |
| 奖励模型 | Reward Model | 训练用来估计Agent输出质量好坏的模型，常用于强化学习打分 |
| 工具调用 | Tool Use | Agent调用外部函数、API或软件来完成任务的机制，是Agent区别于聊天机器人的关键能力 |
| 多步规划 | Multi-step Planning | Agent为完成复杂任务而分解步骤、按序执行的过程，考验长程推理能力 |
| 记忆管理 | Memory Management | Agent对历史信息进行存取、更新与遗忘的机制，影响跨轮次任务的连贯性 |
| 对抗样本 | Adversarial Example | 专门设计用来诱导Agent犯错或暴露漏洞的测试输入 |
| 评测漂移 | Evaluation Drift | 因评测数据、模型或环境变化导致评测结果随时间的失真 |
| 人工评估 | Human Evaluation | 由人类评估员对Agent输出进行质量评判的方法，作为LLM裁判的补充或纠偏 |
| 端到端评测 | End-to-end Evaluation | 在真实或接近真实的任务场景中，完整评估Agent从感知到交付全过程的评测方式 |
| 评测闭环 | Evaluation Loop | 评测→分析→迭代→再评测的循环，驱动Agent持续改进的质量回路 |

---

## 术语之间的关系

- **评测体系**（方法）基于 **基准测试**（工具）与 **测试用例**（单元），产出 **任务完成率** 等 **关键指标**（度量）。
- **LLM裁判** 与 **人工评估** 是两种评分方式，前者高效但可能受 **奖励黑客** 影响，后者准确但成本高。
- **可复现性** 是衡量评测体系可信度的核心属性，**数据污染** 与 **评测漂移** 是威胁可信度的两大风险源。
- **工具调用**、**多步规划**、**记忆管理** 是Agent的核心能力，也是评测需要重点覆盖的维度。

---

